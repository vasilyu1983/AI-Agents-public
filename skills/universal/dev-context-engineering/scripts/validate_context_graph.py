#!/usr/bin/env python3
"""
Validate a context-graph.json file produced by scan_context_artifacts.py.

Usage:
  python3 validate_context_graph.py /path/to/context-graph.json
  python3 validate_context_graph.py /path/to/context-graph.json --repo /path/to/repo
  python3 validate_context_graph.py /path/to/context-graph.json --output report.json
"""
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


VALID_NODE_TYPES = {
    "agents_md",
    "claude_md",
    "rule",
    "spec",
    "plan",
    "subagent",
    "hook",
    "copilot_instructions",
    "github_agent",
    "reference",
    "asset",
    "skill",
}

VALID_RELATIONS = {
    "imports",
    "delegates_to",
    "enforces",
    "documents",
    "triggers",
    "validates",
    "overrides",
    "extends",
    "references",
    "supersedes",
}

STALE_TIER_DAYS = 90
STALE_TIERS = {"L1_always"}


def check_schema_compliance(nodes: list[dict], edges: list[dict]) -> list[str]:
    issues = []
    for node in nodes:
        if node.get("type") not in VALID_NODE_TYPES:
            issues.append(
                f"Node '{node.get('id', '?')}' has invalid type '{node.get('type')}'"
            )
        for field in ("id", "type", "label", "path"):
            if field not in node:
                issues.append(f"Node '{node.get('id', '?')}' missing required field '{field}'")
    for edge in edges:
        if edge.get("relation") not in VALID_RELATIONS:
            issues.append(
                f"Edge {edge.get('source', '?')}→{edge.get('target', '?')} has invalid relation '{edge.get('relation')}'"
            )
        for field in ("source", "target", "relation"):
            if field not in edge:
                issues.append(f"Edge missing required field '{field}'")
    return issues


def check_dangling_refs(nodes: list[dict], edges: list[dict]) -> list[str]:
    node_ids = {n["id"] for n in nodes if "id" in n}
    issues = []
    for edge in edges:
        src = edge.get("source")
        tgt = edge.get("target")
        if src not in node_ids:
            issues.append(f"Edge references unknown source '{src}'")
        if tgt not in node_ids:
            issues.append(f"Edge references unknown target '{tgt}'")
    return issues


def check_duplicate_ids(nodes: list[dict], edges: list[dict]) -> list[str]:
    seen = {}
    for node in nodes:
        nid = node.get("id")
        if not nid:
            continue
        seen[nid] = seen.get(nid, 0) + 1
    return [f"Node id '{nid}' is duplicated {count} times" for nid, count in seen.items() if count > 1]


def check_paths_exist(nodes: list[dict], edges: list[dict], repo_root: Path) -> list[str]:
    issues = []
    for node in nodes:
        node_path = node.get("path")
        if not node_path:
            continue
        abs_path = repo_root / node_path
        if not abs_path.exists():
            issues.append(f"Node '{node.get('id', '?')}' path does not exist: {node_path}")
    return issues


def _parse_iso(value: str) -> datetime | None:
    if not value:
        return None
    try:
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except (TypeError, ValueError):
        return None


def check_stale_tiers(nodes: list[dict], edges: list[dict]) -> list[str]:
    """Flag hot-tier nodes that haven't been touched recently.

    Hot instructions (L1_always) drift fastest because they are read every
    session. Anything older than STALE_TIER_DAYS deserves a re-verification pass.
    """
    issues = []
    now = datetime.now(timezone.utc)
    for node in nodes:
        tier = node.get("loading_tier")
        if tier not in STALE_TIERS:
            continue
        last_modified = _parse_iso(node.get("last_modified_at", ""))
        last_verified = _parse_iso(node.get("last_verified_at", ""))
        anchor = last_verified or last_modified
        if not anchor:
            issues.append(
                f"Hot-tier node '{node.get('id', '?')}' has no last_modified_at or last_verified_at"
            )
            continue
        age_days = (now - anchor).days
        if age_days > STALE_TIER_DAYS:
            issues.append(
                f"Hot-tier node '{node.get('id', '?')}' is {age_days}d old (>{STALE_TIER_DAYS}d threshold)"
            )
    return issues


def check_supersession_integrity(nodes: list[dict], edges: list[dict]) -> list[str]:
    """Validate bitemporal supersession edges form a consistent chain."""
    edge_index = {edge.get("edge_id"): edge for edge in edges if edge.get("edge_id")}
    issues = []
    for edge in edges:
        succ = edge.get("superseded_by")
        if succ and succ not in edge_index:
            issues.append(
                f"Edge {edge.get('source')}→{edge.get('target')} superseded_by unknown edge_id '{succ}'"
            )
        valid_at = _parse_iso(edge.get("valid_at", ""))
        valid_until = _parse_iso(edge.get("valid_until", ""))
        if valid_at and valid_until and valid_until < valid_at:
            issues.append(
                f"Edge {edge.get('source')}→{edge.get('target')} valid_until precedes valid_at"
            )
    return issues


def check_orphans(nodes: list[dict], edges: list[dict]) -> list[str]:
    connected = set()
    for edge in edges:
        if edge.get("source"):
            connected.add(edge["source"])
        if edge.get("target"):
            connected.add(edge["target"])

    exempt = {"asset"}
    issues = []
    for node in nodes:
        nid = node.get("id")
        if not nid or node.get("type") in exempt:
            continue
        if nid not in connected:
            issues.append(f"Node '{nid}' has zero edges (orphan)")
    return issues


CHECKS = [
    check_schema_compliance,
    check_dangling_refs,
    check_duplicate_ids,
    check_paths_exist,
    check_orphans,
    check_stale_tiers,
    check_supersession_integrity,
]


def validate(graph_path: Path, repo_root: Path) -> dict:
    data = json.loads(graph_path.read_text(encoding="utf-8"))
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    results = []
    for check in CHECKS:
        if check is check_paths_exist:
            issues = check(nodes, edges, repo_root)
        else:
            issues = check(nodes, edges)
        results.append(
            {
                "check": check.__name__.replace("check_", ""),
                "passed": not issues,
                "issue_count": len(issues),
                "issues": issues[:10],
            }
        )

    report = {
        "graph": str(graph_path),
        "repo_root": str(repo_root),
        "checks_passed": sum(1 for result in results if result["passed"]),
        "checks_total": len(results),
        "node_count": len(nodes),
        "edge_count": len(edges),
        "results": results,
    }
    return report


def main():
    parser = argparse.ArgumentParser(description="Validate a context-graph.json file.")
    parser.add_argument("graph", help="Path to context-graph.json")
    parser.add_argument(
        "--repo",
        help="Repository root for validating node paths. Defaults to the graph file's parent directory.",
    )
    parser.add_argument("--output", help="Optional path to write the JSON report.")
    args = parser.parse_args()

    graph_path = Path(args.graph).resolve()
    if not graph_path.exists():
        print(f"Error: graph not found: {graph_path}", file=sys.stderr)
        sys.exit(1)

    repo_root = Path(args.repo).resolve() if args.repo else graph_path.parent
    report = validate(graph_path, repo_root)
    output = json.dumps(report, indent=2, ensure_ascii=False)
    print(output)

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(output, encoding="utf-8")

    sys.exit(0 if report["checks_passed"] == report["checks_total"] else 1)


if __name__ == "__main__":
    main()
