#!/usr/bin/env python3
"""
Scan a repo for context artifacts (AGENTS.md, CLAUDE.md, rules, specs, hooks, etc.)
and build a context-graph.json.

Usage:
  python3 scan_context_artifacts.py /path/to/repo [--output /path/to/context-graph.json]
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Artifact pattern catalogue
# ---------------------------------------------------------------------------

# Each entry: (glob_pattern, node_type, loading_tier)
ARTIFACT_PATTERNS = [
    ("AGENTS.md",                          "agents_md",          "L1_always"),
    ("CLAUDE.md",                          "claude_md",          "L1_always"),
    (".claude/rules/*.md",                 "rule",               "L1_always"),
    (".claude/agents/*.md",                "subagent",           "L2_on_demand"),
    (".claude/hooks/*",                    "hook",               "L1_always"),
    ("docs/specs/*.md",                    "spec",               "L2_on_demand"),
    ("specs/*.md",                         "spec",               "L2_on_demand"),
    ("SPEC.md",                            "spec",               "L2_on_demand"),
    ("docs/plans/*.md",                    "plan",               "L2_on_demand"),
    ("plans/*.md",                         "plan",               "L2_on_demand"),
    ("docs/references/*.md",               "reference",          "L3_referenced"),
    ("assets/**/*",                        "asset",              "L3_referenced"),
    ("skills/*/SKILL.md",                  "skill",              "L3_referenced"),
    (".github/copilot-instructions.md",    "copilot_instructions","L1_always"),
    (".github/instructions/*.md",          "copilot_instructions","L2_on_demand"),
    (".github/instructions/*.instructions.md", "copilot_instructions", "L2_on_demand"),
    (".github/agents/*.md",                "github_agent",       "L2_on_demand"),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_mtime_iso(path: Path) -> str:
    mtime = path.stat().st_mtime
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()


def path_to_id(relative_path: str) -> str:
    """Convert a relative path to a node ID: replace / and . and spaces with -."""
    # strip extension, replace path separators and special chars
    no_ext = re.sub(r"\.[^/]+$", "", relative_path)
    return re.sub(r"[/\\ ]+", "-", no_ext).strip("-")


def rel_path_str(abs_path: Path, repo_root: Path) -> str:
    try:
        return str(abs_path.relative_to(repo_root))
    except ValueError:
        return str(abs_path)


def token_cost(path: Path) -> int:
    try:
        return int(path.stat().st_size / 4)
    except OSError:
        return 0


# ---------------------------------------------------------------------------
# Scanner
# ---------------------------------------------------------------------------

def scan_artifacts(repo_root: Path) -> list[dict]:
    """Return a list of node dicts for all discovered context artifacts."""
    nodes: list[dict] = []
    seen_paths: set[str] = set()

    for glob_pattern, node_type, tier in ARTIFACT_PATTERNS:
        for abs_path in sorted(repo_root.glob(glob_pattern)):
            if not abs_path.is_file():
                continue
            rel = rel_path_str(abs_path, repo_root)
            if rel in seen_paths:
                continue
            seen_paths.add(rel)

            node_id = path_to_id(rel)
            label   = abs_path.stem

            node = {
                "id":               node_id,
                "type":             node_type,
                "label":            label,
                "path":             rel,
                "last_modified_at": file_mtime_iso(abs_path),
                "token_cost":       token_cost(abs_path),
                "loading_tier":     tier,
                "stale":            False,
            }
            nodes.append(node)

    return nodes


# ---------------------------------------------------------------------------
# Edge detection
# ---------------------------------------------------------------------------

# Patterns to search within file content
# imports: CLAUDE.md !include or # @import or @path directives
RE_IMPORT        = re.compile(r"(?:!include|#\s*@import|@path)\s+([^\s\"']+)", re.MULTILINE)
# references: markdown links to relative paths
RE_MD_LINK       = re.compile(r"\[([^\]]+)\]\((\./|\.\./)([^)]+)\)")
# delegates_to: skill delegation patterns like [skill-name] or (skill:...) in text
RE_SKILL_BRACKET = re.compile(r"\[([a-z][a-z0-9-]{2,})\](?!\()")          # [skill-name] not followed by (
RE_SKILL_PAREN   = re.compile(r"\(skill:([a-z][a-z0-9-]+)\)")              # (skill:name)
# enforces: hook file references a rule file by filename stem
RE_RULE_REF      = re.compile(r"\b([a-z][a-z0-9-]+(?:-rule|-policy|-coding))\b")


def detect_edges(nodes: list[dict], repo_root: Path) -> list[dict]:
    """
    Parse each node's file to detect edges.
    Returns list of edge dicts with source, target, relation.
    """
    edges: list[dict] = []
    edge_keys_seen: set[tuple] = set()

    # Build lookup: path → node_id and id → node for fast reverse lookups
    path_to_node: dict[str, dict] = {n["path"]: n for n in nodes}
    id_to_node: dict[str, dict]   = {n["id"]: n for n in nodes}

    # All node IDs for target resolution
    all_ids = set(id_to_node)
    all_paths = set(path_to_node)

    def add_edge(src_id: str, tgt_id: str, relation: str):
        if src_id == tgt_id:
            return
        key = (src_id, tgt_id, relation)
        if key in edge_keys_seen:
            return
        edge_keys_seen.add(key)
        edges.append({"source": src_id, "target": tgt_id, "relation": relation})

    def resolve_path_ref(ref: str, source_path: str) -> str:
        """Given a relative ref in a file, return the matching node_id or ''."""
        # Normalise: strip leading ./ or ../
        clean = re.sub(r"^\.{1,2}/", "", ref)
        # Try direct path match
        for p in all_paths:
            if p.endswith(clean) or Path(p).name == Path(clean).name:
                return path_to_node[p]["id"]
        # Try id match
        stem = Path(clean).stem
        candidate_id = path_to_id(clean)
        if candidate_id in all_ids:
            return candidate_id
        # Partial stem match
        for nid in all_ids:
            if nid.endswith(stem) or nid == stem:
                return nid
        return ""

    for node in nodes:
        src_id    = node["id"]
        node_type = node["type"]
        file_path = repo_root / node["path"]

        if not file_path.exists() or not file_path.is_file():
            continue

        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue

        # ── imports (CLAUDE.md and similar) ──────────────────────────────────
        if node_type in ("claude_md", "agents_md", "copilot_instructions"):
            for m in RE_IMPORT.finditer(content):
                tgt = resolve_path_ref(m.group(1), node["path"])
                if tgt:
                    add_edge(src_id, tgt, "imports")

        # Binary-ish assets are modeled as nodes, but we do not try to parse them.
        if node_type == "asset":
            continue

        # ── references (markdown links in any artifact) ───────────────────────
        for m in RE_MD_LINK.finditer(content):
            ref = m.group(3)          # path after ./ or ../
            tgt = resolve_path_ref(ref, node["path"])
            if tgt:
                add_edge(src_id, tgt, "references")

        # ── delegates_to (Quick Reference tables or inline skill mentions) ────
        if node_type in ("claude_md", "agents_md", "rule", "spec"):
            for m in RE_SKILL_BRACKET.finditer(content):
                skill_name = m.group(1)
                # Only add if another node with matching id/stem exists
                for nid, nd in id_to_node.items():
                    if nd.get("type") == "skill" or skill_name in nid:
                        add_edge(src_id, nid, "delegates_to")
                        break
            for m in RE_SKILL_PAREN.finditer(content):
                skill_name = m.group(1)
                for nid, nd in id_to_node.items():
                    if skill_name in nid:
                        add_edge(src_id, nid, "delegates_to")
                        break

        # ── enforces (hook → rule) ────────────────────────────────────────────
        if node_type == "hook":
            for m in RE_RULE_REF.finditer(content):
                rule_name = m.group(1)
                for nid, nd in id_to_node.items():
                    if nd.get("type") == "rule" and (
                        rule_name in nid or nid.endswith(rule_name)
                    ):
                        add_edge(src_id, nid, "enforces")

    return edges


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build_context_graph(repo_root: Path) -> dict:
    nodes = scan_artifacts(repo_root)
    edges = detect_edges(nodes, repo_root)

    return {
        "meta": {
            "scope": repo_root.name,
            "generated_at": now_iso(),
            "maturity_level": None,
        },
        "nodes": nodes,
        "edges": edges,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Scan a repo for context artifacts and build a context-graph.json."
    )
    parser.add_argument("repo", help="Path to the repository root")
    parser.add_argument(
        "--output", metavar="FILE",
        help="Output JSON path (default: <repo>/context-graph.json)"
    )
    args = parser.parse_args()

    repo_root = Path(args.repo).resolve()
    if not repo_root.is_dir():
        print(f"Error: repo path not found: {repo_root}", file=sys.stderr)
        sys.exit(1)

    print(f"[scan] Scanning {repo_root}")
    graph = build_context_graph(repo_root)

    output_path = Path(args.output).resolve() if args.output else repo_root / "context-graph.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(graph, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )

    n = len(graph["nodes"])
    e = len(graph["edges"])
    print(
        f"[done] Context graph written to {output_path}\n"
        f"       nodes={n}  edges={e}"
    )

    if n == 0:
        print(
            "[info] No context artifacts found. "
            "Expected files like AGENTS.md, CLAUDE.md, .claude/rules/*.md, etc.",
            file=sys.stderr
        )


if __name__ == "__main__":
    main()
