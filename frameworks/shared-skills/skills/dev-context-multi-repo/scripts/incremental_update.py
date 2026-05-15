#!/usr/bin/env python3
"""
Incrementally update a knowledge-graph.json using git diff to detect changed repos.

Protocol:
  1. Read meta.base_commit_shas from the existing graph (repo_id → last-scan SHA).
  2. For each repo_id in the map, compare its current HEAD SHA to the stored SHA.
  3. If a repo has no stored SHA yet, seed its baseline SHA without staling existing nodes.
  4. Mark all nodes belonging to changed repos as stale=True.
  5. (Optional) Re-scan changed repos if --profiles dir is provided.
  6. Merge updated profiles into the graph.
  7. Remove nodes that remain stale after the merge.
  8. Update meta.base_commit_shas with the new HEADs.
  9. Write updated graph back to disk.

Usage:
  python3 incremental_update.py graphs/knowledge-graph.json \\
      --repo-map repos.json          # JSON: {repo_id: "/abs/path/to/repo"}
  python3 incremental_update.py graphs/knowledge-graph.json \\
      --repo-map repos.json \\
      --profiles profiles/           # Re-scan and merge updated profiles
  python3 incremental_update.py graphs/knowledge-graph.json \\
      --repo-map repos.json --dry-run
  python3 incremental_update.py graphs/knowledge-graph.json \\
      --repo-map repos.json --output graphs/knowledge-graph.next.json --report reports/incremental-update.json

repos.json format:
  {
    "payments-ledger": "/abs/path/to/payments-ledger",
    "sc-booking": "/abs/path/to/sc.booking"
  }

Portable repo-map format:
  {
    "roots": {
      "main": ["../.."],
      "qa": ["../../../platform-qa"]
    },
    "repos": {
      "payments-ledger": {"root": "main", "path": "payments-ledger"},
      "qa-tests": {"root": "qa", "path": "qa-tests"}
    }
  }
"""
import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def normalize_profile_entity_type(raw: str) -> str:
    if not raw:
        return "entity"
    lowered = raw.strip().lower()
    if lowered == "nuget_package":
        return "package"
    return lowered


def normalize_root_key(raw: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", raw.strip().lower()).strip("_")


def report_path_value(path_value: str | None, report_path: str | None) -> str | None:
    if not path_value:
        return path_value
    if not report_path:
        return str(Path(path_value))
    anchor = Path(report_path).resolve().parent
    try:
        return os.path.relpath(Path(path_value).resolve(), start=anchor)
    except ValueError:
        return str(Path(path_value).resolve())


def root_overrides_from_env() -> dict[str, str]:
    overrides: dict[str, str] = {}
    prefix = "DEV_CONTEXT_REPO_ROOT_"
    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue
        root_name = normalize_root_key(key[len(prefix):])
        if root_name and value:
            overrides[root_name] = value
    return overrides


def parse_root_overrides(values: list[str]) -> dict[str, str]:
    overrides = root_overrides_from_env()
    for raw in values:
        if "=" not in raw:
            raise ValueError(f"Invalid --repo-root value '{raw}'. Expected NAME=PATH.")
        name, path = raw.split("=", 1)
        root_name = normalize_root_key(name)
        if not root_name or not path:
            raise ValueError(f"Invalid --repo-root value '{raw}'. Expected NAME=PATH.")
        overrides[root_name] = path
    return overrides


def _candidate_paths_from_value(path_value: str, repo_map_dir: Path) -> list[Path]:
    candidate = Path(path_value).expanduser()
    if candidate.is_absolute():
        return [candidate.resolve()]
    return [(repo_map_dir / candidate).resolve()]


def _candidate_paths_from_root(
    root_name: str,
    roots: dict[str, object],
    repo_map_dir: Path,
    root_overrides: dict[str, str],
) -> list[Path]:
    normalized_root = normalize_root_key(root_name)
    if normalized_root in root_overrides:
        return [Path(root_overrides[normalized_root]).expanduser().resolve()]

    root_spec = roots.get(root_name)
    if root_spec is None:
        root_spec = roots.get(normalized_root)
    if root_spec is None:
        return []

    values: list[str]
    if isinstance(root_spec, str):
        values = [root_spec]
    elif isinstance(root_spec, list):
        values = [value for value in root_spec if isinstance(value, str)]
    elif isinstance(root_spec, dict):
        if isinstance(root_spec.get("path"), str):
            values = [root_spec["path"]]
        else:
            values = [value for value in root_spec.get("paths", []) if isinstance(value, str)]
    else:
        values = []

    roots_out: list[Path] = []
    for value in values:
        roots_out.extend(_candidate_paths_from_value(value, repo_map_dir))
    return roots_out


def resolve_repo_map_entry(
    repo_id: str,
    entry: str | dict,
    *,
    roots: dict[str, object],
    repo_map_dir: Path,
    root_overrides: dict[str, str],
) -> str:
    candidates: list[Path] = []

    def add_candidates(values: list[str], *, relative_only: bool = False):
        for value in values:
            if not isinstance(value, str) or not value:
                continue
            if relative_only:
                candidates.append((repo_map_dir / value).expanduser().resolve())
            else:
                candidates.extend(_candidate_paths_from_value(value, repo_map_dir))

    if isinstance(entry, str):
        add_candidates([entry])
    elif isinstance(entry, dict):
        root_name = entry.get("root")
        root_path = entry.get("path")
        if isinstance(root_name, str) and isinstance(root_path, str):
            for root_base in _candidate_paths_from_root(root_name, roots, repo_map_dir, root_overrides):
                candidates.append((root_base / root_path).resolve())

        add_candidates([entry["path"]] if isinstance(entry.get("path"), str) and not root_name else [])
        add_candidates(entry.get("paths", []) if isinstance(entry.get("paths"), list) else [])
        add_candidates([entry["relative_path"]] if isinstance(entry.get("relative_path"), str) else [], relative_only=True)
        add_candidates(entry.get("relative_paths", []) if isinstance(entry.get("relative_paths"), list) else [], relative_only=True)
    else:
        raise ValueError(f"Unsupported repo-map entry for '{repo_id}': {type(entry).__name__}")

    unique_candidates: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        rendered = str(candidate)
        if rendered in seen:
            continue
        seen.add(rendered)
        unique_candidates.append(candidate)

    for candidate in unique_candidates:
        if candidate.exists():
            return str(candidate)

    return str(unique_candidates[0]) if unique_candidates else ""


def load_repo_map(repo_map_path: Path, root_overrides: dict[str, str] | None = None) -> dict[str, str]:
    raw = json.loads(repo_map_path.read_text(encoding="utf-8"))
    root_overrides = root_overrides or {}
    repo_map_dir = repo_map_path.resolve().parent

    if isinstance(raw, dict) and "repos" in raw and isinstance(raw["repos"], dict):
        roots = raw.get("roots", {}) if isinstance(raw.get("roots"), dict) else {}
        repos = raw["repos"]
    elif isinstance(raw, dict):
        roots = {}
        repos = {key: value for key, value in raw.items() if not str(key).startswith("_")}
    else:
        raise ValueError("Repo map must be a JSON object.")

    resolved: dict[str, str] = {}
    for repo_id, entry in repos.items():
        resolved[repo_id] = resolve_repo_map_entry(
            repo_id,
            entry,
            roots=roots,
            repo_map_dir=repo_map_dir,
            root_overrides=root_overrides,
        )
    return resolved


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def git_head_sha(repo_path: str) -> str:
    """Return the current HEAD commit SHA for a git repository, or '' on failure."""
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "HEAD"],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def git_changed_files(repo_path: str, from_sha: str, to_sha: str = "HEAD") -> list[str]:
    """
    Return list of changed file paths (relative to repo root) between two SHAs.
    Returns empty list if git is unavailable or the repo is untracked.
    """
    try:
        result = subprocess.run(
            ["git", "-C", repo_path, "diff", "--name-only", f"{from_sha}..{to_sha}"],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            return [f for f in result.stdout.splitlines() if f]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


# ---------------------------------------------------------------------------
# Profile merge helpers
# ---------------------------------------------------------------------------

def load_profile(profile_path: Path) -> dict:
    """Load a single repo profile JSON, returning empty dict on error."""
    try:
        return json.loads(profile_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def profile_to_nodes_edges(profile: dict, repo_id: str) -> tuple[list[dict], list[dict]]:
    """
    Convert a repo profile to minimal graph nodes + edges.
    Mirrors the logic in build_knowledge_graph.py Mode A (simplified).
    """
    now = datetime.now(timezone.utc).isoformat()
    nodes: list[dict] = []
    edges: list[dict] = []

    # Repo node
    repo_node = {
        "id": repo_id,
        "type": "repo",
        "label": profile.get("repo_name", repo_id),
        "last_verified_at": now,
        "stale": False,
    }
    if profile.get("summary"):
        repo_node["summary"] = profile["summary"]
    if profile.get("tags"):
        repo_node["tags"] = profile["tags"]
    nodes.append(repo_node)

    # Sub-entities
    for sub in profile.get("sub_entities", []):
        sub_id = sub.get("id")
        if not sub_id:
            continue
        sub_node = {
            "id": sub_id,
            "type": normalize_profile_entity_type(sub.get("type", "entity")),
            "label": sub.get("label", sub_id),
            "parent_id": repo_id,
            "last_verified_at": now,
            "stale": False,
        }
        nodes.append(sub_node)
        edges.append({
            "source": repo_id,
            "target": sub_id,
            "relation": "contains",
            "group": "structural",
            "weight": 1.0,
        })

    # Dependencies
    for dep in profile.get("dependencies_direct", []):
        if not dep:
            continue
        dep_id = dep.lower().replace(" ", "-")
        nodes.append({
            "id": dep_id,
            "type": "library",
            "label": dep,
            "last_verified_at": now,
            "stale": False,
        })
        edges.append({
            "source": repo_id,
            "target": dep_id,
            "relation": "depends_on",
            "group": "dependency",
            "weight": 0.6,
        })

    return nodes, edges


# ---------------------------------------------------------------------------
# Graph merge
# ---------------------------------------------------------------------------

def merge_nodes(existing: list[dict], updated: list[dict]) -> list[dict]:
    """
    Merge updated nodes into existing list.
    - Updated nodes replace existing ones with the same ID.
    - New nodes (IDs not in existing) are appended.
    - First-writer-wins for scalar fields NOT present in updated node.
    """
    existing_map = {n["id"]: i for i, n in enumerate(existing) if "id" in n}
    result = list(existing)

    for new_node in updated:
        nid = new_node.get("id")
        if not nid:
            continue
        if nid in existing_map:
            idx = existing_map[nid]
            merged = dict(result[idx])
            merged.update(new_node)  # new values win for updated fields
            result[idx] = merged
        else:
            result.append(new_node)
            existing_map[nid] = len(result) - 1

    return result


def merge_edges(existing: list[dict], updated: list[dict]) -> list[dict]:
    """
    Merge updated edges using (source, target, relation) as the dedup key.
    Updated edges replace existing ones with the same key.
    """
    EdgeKey = tuple  # (source, target, relation)

    def key(e: dict) -> EdgeKey:
        return (e.get("source"), e.get("target"), e.get("relation"))

    existing_map: dict[EdgeKey, int] = {}
    result = list(existing)
    for i, e in enumerate(result):
        existing_map[key(e)] = i

    for new_edge in updated:
        k = key(new_edge)
        if k in existing_map:
            result[existing_map[k]] = new_edge
        else:
            result.append(new_edge)
            existing_map[k] = len(result) - 1

    return result


# ---------------------------------------------------------------------------
# Core update logic
# ---------------------------------------------------------------------------

def incremental_update(
    graph_path: str,
    repo_map: dict[str, str],
    profiles_dir: str | None = None,
    dry_run: bool = False,
    output_path: str | None = None,
) -> dict:
    """
    Main update function. Returns a summary dict.

    repo_map: {repo_id: abs_path_to_repo}
    """
    path = Path(graph_path)
    if not path.exists():
        print(f"Error: graph not found: {graph_path}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(path.read_text(encoding="utf-8"))
    nodes: list[dict] = data.get("nodes", [])
    edges: list[dict] = data.get("edges", [])
    meta: dict = data.get("meta", {})
    base_shas: dict[str, str] = meta.get("base_commit_shas", {})

    repo_node_ids = {n.get("id") for n in nodes if n.get("type") == "repo" and n.get("id")}

    summary = {
        "repos_checked": 0,
        "repos_changed": [],
        "repos_unchanged": [],
        "repos_bootstrapped": [],
        "repos_not_found": [],
        "repos_invalid_git": [],
        "nodes_marked_stale": 0,
        "nodes_removed": 0,
        "profiles_merged": 0,
        "dry_run": dry_run,
    }

    # 1. Detect changed repos
    changed_repo_ids: set[str] = set()
    new_shas: dict[str, str] = {}

    for repo_id, repo_path in repo_map.items():
        summary["repos_checked"] += 1
        if not repo_path:
            summary["repos_not_found"].append(repo_id)
            continue

        rp = Path(repo_path)
        if not rp.exists():
            summary["repos_not_found"].append(repo_id)
            continue

        current_sha = git_head_sha(repo_path)
        if not current_sha:
            summary["repos_invalid_git"].append(repo_id)
            continue
        new_shas[repo_id] = current_sha
        stored_sha = base_shas.get(repo_id, "")

        if not stored_sha:
            # First observation: seed the baseline SHA without staling existing graph nodes.
            summary["repos_bootstrapped"].append(repo_id)
            if profiles_dir and repo_id not in repo_node_ids:
                changed_repo_ids.add(repo_id)
                summary["repos_changed"].append(repo_id)
                print(
                    f"  [{repo_id}] no stored SHA yet; queued profile merge for new repo",
                    file=sys.stderr,
                )
        elif current_sha == stored_sha:
            summary["repos_unchanged"].append(repo_id)
        else:
            changed_files = git_changed_files(repo_path, stored_sha, current_sha)
            if changed_files:
                changed_repo_ids.add(repo_id)
                summary["repos_changed"].append(repo_id)
                print(
                    f"  [{repo_id}] {len(changed_files)} changed file(s) since {stored_sha[:7]}",
                    file=sys.stderr,
                )
            else:
                summary["repos_unchanged"].append(repo_id)

    # 2. Mark nodes for changed repos as stale
    stale_ids: set[str] = set()
    for n in nodes:
        nid = n.get("id", "")
        parent = n.get("parent_id", "")
        if nid in changed_repo_ids or parent in changed_repo_ids:
            n["stale"] = True
            stale_ids.add(nid)
            summary["nodes_marked_stale"] += 1

    # 3. Merge updated profiles (if provided)
    updated_node_ids: set[str] = set()
    if profiles_dir and changed_repo_ids:
        pd = Path(profiles_dir)
        for repo_id in changed_repo_ids:
            # Try {repo_id}.json or any file whose stem normalizes to repo_id
            candidates = list(pd.glob(f"{repo_id}.json")) + list(pd.glob(f"{repo_id.replace('-', '_')}.json"))
            for profile_path in candidates:
                profile = load_profile(profile_path)
                if not profile:
                    continue
                new_nodes, new_edges = profile_to_nodes_edges(profile, repo_id)
                if not dry_run:
                    nodes = merge_nodes(nodes, new_nodes)
                    edges = merge_edges(edges, new_edges)
                updated_node_ids.update(n["id"] for n in new_nodes if "id" in n)
                summary["profiles_merged"] += 1
                print(f"  [{repo_id}] merged profile from {profile_path.name}", file=sys.stderr)
                break

    # 4. Remove nodes that are still stale (not refreshed by profile merge)
    if not dry_run:
        remaining_stale = [n for n in nodes if n.get("stale") and n.get("id") not in updated_node_ids]
        remaining_ids = {n.get("id") for n in remaining_stale}
        summary["nodes_removed"] = len(remaining_stale)

        nodes = [n for n in nodes if n.get("id") not in remaining_ids]
        edges = [e for e in edges if e.get("source") not in remaining_ids and e.get("target") not in remaining_ids]

    # 5. Update meta
    now_iso = datetime.now(timezone.utc).isoformat()
    updated_shas = dict(base_shas)
    updated_shas.update(new_shas)

    updated_meta = dict(meta)
    updated_meta["base_commit_shas"] = updated_shas
    updated_meta["generated_at"] = now_iso
    updated_meta["node_count"] = len(nodes)
    updated_meta["edge_count"] = len(edges)

    # 6. Write
    if not dry_run:
        out = dict(data)
        out["meta"] = updated_meta
        out["nodes"] = nodes
        out["edges"] = edges
        write_path = Path(output_path).resolve() if output_path else path.resolve()
        write_path.parent.mkdir(parents=True, exist_ok=True)
        write_path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
        summary["output_path"] = str(write_path)

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Incrementally update a knowledge-graph.json based on git diff. "
            "Reads meta.base_commit_shas to determine which repos changed, "
            "seeds missing baselines safely, marks changed nodes stale, "
            "optionally merges fresh profiles, and removes unreachable stale nodes."
        )
    )
    parser.add_argument("graph", help="Path to knowledge-graph.json")
    parser.add_argument(
        "--repo-map", required=True, metavar="FILE",
        help=(
            "JSON repo map. Supports the legacy flat format (repo_id -> path) and a "
            "portable format with named roots and repo-relative paths."
        ),
    )
    parser.add_argument(
        "--repo-root", action="append", default=[], metavar="NAME=PATH",
        help=(
            "Override a named portable repo-map root at runtime. Repeatable. "
            "Example: --repo-root main=/work/platform --repo-root qa=/work/platform-qa"
        ),
    )
    parser.add_argument(
        "--profiles", metavar="DIR",
        help="Directory containing updated *.json profile files to merge for changed repos",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Detect and report changes without modifying the graph file",
    )
    parser.add_argument(
        "--output", metavar="FILE",
        help="Optional path for the updated graph. Defaults to overwriting the input graph.",
    )
    parser.add_argument(
        "--report", metavar="FILE",
        help="Optional path to write the JSON summary report.",
    )

    args = parser.parse_args()

    repo_map_path = Path(args.repo_map)
    if not repo_map_path.exists():
        print(f"Error: repo-map file not found: {args.repo_map}", file=sys.stderr)
        sys.exit(1)

    try:
        root_overrides = parse_root_overrides(args.repo_root)
        repo_map = load_repo_map(repo_map_path, root_overrides=root_overrides)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    summary = incremental_update(
        graph_path=args.graph,
        repo_map=repo_map,
        profiles_dir=args.profiles,
        dry_run=args.dry_run,
        output_path=args.output,
    )

    report_summary = dict(summary)
    report_summary["output_path"] = report_path_value(summary.get("output_path"), args.report)

    rendered = json.dumps(report_summary, indent=2)
    print(rendered)

    if args.report:
        report_path = Path(args.report).resolve()
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(rendered, encoding="utf-8")

    if summary["repos_changed"]:
        sys.exit(0)  # Changes detected — caller can inspect summary
    else:
        sys.exit(0)  # No changes needed


if __name__ == "__main__":
    main()
