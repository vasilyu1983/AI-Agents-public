#!/usr/bin/env python3
"""
Validate a knowledge-graph.json file against 8 integrity checks.

Usage:
  python3 validate_graph.py graphs/knowledge-graph.json
  python3 validate_graph.py graphs/knowledge-graph.json --max-age-days 60
  python3 validate_graph.py graphs/knowledge-graph.json --fix
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# Valid enum values (must match knowledge-graph.schema.json)
# ---------------------------------------------------------------------------

VALID_NODE_TYPES = {
    "repo", "service", "domain", "provider", "process", "artifact",
    "library", "package", "api_endpoint", "queue_topic",
    "database", "table", "entity", "event", "config", "context_artifact",
    "skill", "agent",
}

VALID_EDGE_RELATIONS = {
    "contains", "imports", "exposes", "calls", "subscribes_to", "publishes_to",
    "reads_from", "writes_to", "owns_data_in", "depends_on", "shares_library_with",
    "deploys_with", "replaces", "extends", "related_to", "similar_to",
    "contradicts", "co_occurs", "uses_provider", "implements_process",
    "documents", "governed_by",
}

VALID_EDGE_GROUPS = {"structural", "behavioral", "data_flow", "dependency", "semantic"}


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


def report_for_output(report: dict, output_path: str | None) -> dict:
    rendered = dict(report)
    if "graph" in rendered:
        rendered["graph"] = report_path_value(rendered.get("graph"), output_path)
    return rendered

# ---------------------------------------------------------------------------
# Individual check functions
# ---------------------------------------------------------------------------

def check_schema_compliance(nodes: list, edges: list) -> list[str]:
    """Verify that node types, edge relations, and edge groups are from allowed enums."""
    issues = []
    for n in nodes:
        ntype = n.get("type")
        if ntype not in VALID_NODE_TYPES:
            issues.append(
                f"Node '{n.get('id', '?')}' has invalid type '{ntype}'"
            )

    for e in edges:
        rel = e.get("relation")
        grp = e.get("group")
        src = e.get("source", "?")
        tgt = e.get("target", "?")
        if rel not in VALID_EDGE_RELATIONS:
            issues.append(
                f"Edge {src}→{tgt} has invalid relation '{rel}'"
            )
        if grp is not None and grp not in VALID_EDGE_GROUPS:
            issues.append(
                f"Edge {src}→{tgt} has invalid group '{grp}'"
            )

    return issues


def check_dangling_refs(nodes: list, edges: list) -> list[str]:
    """Edges must not reference node IDs that are absent from the nodes list."""
    node_ids = {n["id"] for n in nodes if "id" in n}
    issues = []
    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if src and src not in node_ids:
            issues.append(
                f"Edge source '{src}' → '{e.get('target', '?')}' references unknown node '{src}'"
            )
        if tgt and tgt not in node_ids:
            issues.append(
                f"Edge '{e.get('source', '?')}' → target '{tgt}' references unknown node '{tgt}'"
            )
    return issues


def check_orphans(nodes: list, edges: list) -> list[str]:
    """
    A node is an orphan if it appears in neither source nor target of any edge.
    Exempt leaf-style nodes where isolation is expected:
    - api_endpoint: may intentionally terminate a branch
    - artifact: documentation sources may exist before deterministic linkers cover them

    Artifact coverage is still reported separately by check_graph_consistency.py.
    """
    connected_ids: set[str] = set()
    for e in edges:
        if e.get("source"):
            connected_ids.add(e["source"])
        if e.get("target"):
            connected_ids.add(e["target"])

    EXEMPT_TYPES = {"api_endpoint", "artifact"}
    issues = []
    for n in nodes:
        nid = n.get("id")
        if not nid:
            continue
        if n.get("type") in EXEMPT_TYPES:
            continue
        if nid not in connected_ids:
            issues.append(
                f"Node '{nid}' (type={n.get('type', '?')}) has zero edges (orphan)"
            )
    return issues


def check_confidence_floor(nodes: list, edges: list, floor: float = 0.05) -> list[str]:
    """
    Report nodes and edges whose confidence is below the floor.
    Skips entries where the confidence field is absent.
    """
    issues = []
    for n in nodes:
        conf = n.get("confidence")
        if conf is None:
            continue
        if conf < floor:
            issues.append(
                f"Node '{n.get('id', '?')}' has confidence {conf:.3f} < floor {floor}"
            )
    for e in edges:
        conf = e.get("confidence")
        if conf is None:
            continue
        if conf < floor:
            issues.append(
                f"Edge '{e.get('source', '?')}' → '{e.get('target', '?')}' "
                f"has confidence {conf:.3f} < floor {floor}"
            )
    return issues


def check_duplicates(nodes: list, edges: list = None) -> list[str]:
    """Report node IDs that appear more than once in the nodes list."""
    seen: dict[str, int] = {}
    for n in nodes:
        nid = n.get("id")
        if not nid:
            continue
        seen[nid] = seen.get(nid, 0) + 1

    issues = []
    for nid, count in seen.items():
        if count > 1:
            issues.append(f"Node id '{nid}' is duplicated {count} times")
    return issues


def check_containment_consistency(nodes: list, edges: list) -> list[str]:
    """
    If a node has a parent_id field, there must be an edge with
      source=parent_id, target=node_id, relation in ('contains', 'exposes').
    'exposes' is semantically valid for repo→api_endpoint parent relationships.
    """
    # Build set of (source, target, relation) for fast lookup
    edge_tuples = {
        (e.get("source"), e.get("target"), e.get("relation"))
        for e in edges
    }
    issues = []
    for n in nodes:
        parent = n.get("parent_id")
        if not parent:
            continue
        nid = n.get("id")
        valid_parent_relations = {"contains", "exposes", "owns_data_in"}
        if not any((parent, nid, rel) in edge_tuples for rel in valid_parent_relations):
            issues.append(
                f"Node '{nid}' has parent_id='{parent}' but no 'contains' edge from parent"
            )
    return issues


def check_circular_deps(nodes: list, edges: list) -> list[str]:
    """
    Detect cycles in the 'depends_on' subgraph using iterative DFS.
    Cycles indicate circular dependencies which could cause build or startup failures.
    """
    dep_graph: dict[str, list[str]] = {}
    for e in edges:
        if e.get("relation") == "depends_on":
            src = e.get("source")
            tgt = e.get("target")
            if src and tgt:
                dep_graph.setdefault(src, []).append(tgt)

    node_ids = {n["id"] for n in nodes if "id" in n}
    issues = []
    visited: set[str] = set()
    in_stack: set[str] = set()

    def dfs(start: str):
        stack = [(start, iter(dep_graph.get(start, [])))]
        path = [start]
        in_stack.add(start)
        visited.add(start)
        while stack:
            node, children = stack[-1]
            try:
                child = next(children)
                if child not in node_ids:
                    continue
                if child in in_stack:
                    # Found a cycle — find where it starts in the path
                    cycle_start = path.index(child)
                    cycle = path[cycle_start:] + [child]
                    issues.append(
                        f"Circular dependency: {' → '.join(cycle)}"
                    )
                elif child not in visited:
                    visited.add(child)
                    in_stack.add(child)
                    path.append(child)
                    stack.append((child, iter(dep_graph.get(child, []))))
            except StopIteration:
                stack.pop()
                in_stack.discard(node)
                if path and path[-1] == node:
                    path.pop()

    for nid in node_ids:
        if nid not in visited:
            dfs(nid)

    return issues


def check_staleness(nodes: list, edges: list, max_age_days: int = 90) -> list[str]:
    """
    Report nodes where last_verified_at is older than max_age_days.
    Skips nodes that have no last_verified_at field.
    """
    now = datetime.now(timezone.utc)
    threshold = now - timedelta(days=max_age_days)
    issues = []
    for n in nodes:
        verified_raw = n.get("last_verified_at")
        if not verified_raw:
            continue
        try:
            # Handle both offset-aware and naive (assume UTC)
            verified = datetime.fromisoformat(verified_raw.rstrip("Z"))
            if verified.tzinfo is None:
                verified = verified.replace(tzinfo=timezone.utc)
            if verified < threshold:
                age_days = (now - verified).days
                issues.append(
                    f"Node '{n.get('id', '?')}' last_verified_at is {age_days} days ago "
                    f"(threshold={max_age_days}d)"
                )
        except ValueError:
            issues.append(
                f"Node '{n.get('id', '?')}' has unparseable last_verified_at: '{verified_raw}'"
            )
    return issues


def check_supersession_integrity(nodes: list, edges: list) -> list[str]:
    """Validate bitemporal supersession edges and time-axis consistency.

    For graphs that adopt the v2 bitemporal schema:
    - superseded_by must point to an edge that exists.
    - supersedes must point to an edge that exists.
    - valid_until must not precede valid_at.
    - ingested_until must not precede ingested_at.
    """
    edge_index = {edge.get("edge_id"): edge for edge in edges if edge.get("edge_id")}
    issues = []
    for edge in edges:
        edge_label = f"{edge.get('source', '?')}→{edge.get('target', '?')}"
        succ = edge.get("superseded_by")
        if succ and succ not in edge_index:
            issues.append(f"Edge {edge_label} superseded_by unknown edge_id '{succ}'")
        prev = edge.get("supersedes")
        if prev and prev not in edge_index:
            issues.append(f"Edge {edge_label} supersedes unknown edge_id '{prev}'")

        valid_at = _parse_iso_safe(edge.get("valid_at"))
        valid_until = _parse_iso_safe(edge.get("valid_until"))
        if valid_at and valid_until and valid_until < valid_at:
            issues.append(f"Edge {edge_label} valid_until precedes valid_at")

        ingested_at = _parse_iso_safe(edge.get("ingested_at"))
        ingested_until = _parse_iso_safe(edge.get("ingested_until"))
        if ingested_at and ingested_until and ingested_until < ingested_at:
            issues.append(f"Edge {edge_label} ingested_until precedes ingested_at")
    return issues


def check_community_consistency(nodes: list, edges: list) -> list[str]:
    """Validate community labels when present.

    Skips silently when no node carries community_id (community detection has
    not been run on this graph). When community_id is present:
    - every community must be a connected subgraph (Louvain occasionally
      produces disconnected communities; surface them so the user can switch
      to Leiden via igraph)
    - singleton communities are flagged as low-information
    """
    has_community = any(node.get("community_id") for node in nodes)
    if not has_community:
        return []

    community_members: dict[str, list[str]] = {}
    node_community: dict[str, str] = {}
    for node in nodes:
        community = node.get("community_id")
        nid = node.get("id")
        if not community or not nid:
            continue
        community_members.setdefault(community, []).append(nid)
        node_community[nid] = community

    # Build undirected adjacency restricted to in-community edges
    intra_adjacency: dict[str, set[str]] = {nid: set() for nid in node_community}
    for edge in edges:
        source = edge.get("source")
        target = edge.get("target")
        if source not in node_community or target not in node_community:
            continue
        if node_community[source] == node_community[target]:
            intra_adjacency[source].add(target)
            intra_adjacency[target].add(source)

    issues = []
    for community, members in community_members.items():
        if len(members) == 1:
            # Singletons are common but worth reporting at scale
            continue
        # BFS to find connected components within the community
        visited: set[str] = set()
        components = 0
        for member in members:
            if member in visited:
                continue
            components += 1
            queue = [member]
            visited.add(member)
            while queue:
                current = queue.pop()
                for neighbour in intra_adjacency.get(current, set()):
                    if neighbour not in visited and neighbour in members:
                        visited.add(neighbour)
                        queue.append(neighbour)
        if components > 1:
            issues.append(
                f"Community '{community}' is split into {components} disconnected components "
                f"(size {len(members)}). Consider re-running with Leiden or higher --resolution."
            )
    return issues


def _parse_iso_safe(value) -> datetime | None:
    if not value or not isinstance(value, str):
        return None
    raw = value.strip()
    if not raw:
        return None
    if raw.endswith("Z"):
        raw = raw[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


# ---------------------------------------------------------------------------
# Validation orchestrator
# ---------------------------------------------------------------------------

CHECKS = [
    check_schema_compliance,
    check_dangling_refs,
    check_orphans,
    check_confidence_floor,
    check_duplicates,
    check_containment_consistency,
    check_staleness,
    check_circular_deps,
    check_supersession_integrity,
    check_community_consistency,
]


# ---------------------------------------------------------------------------
# Auto-repair (--fix)
# ---------------------------------------------------------------------------

def auto_fix(data: dict) -> tuple[dict, list[str]]:
    """
    Apply safe, deterministic repairs to a graph dict.
    Returns (fixed_data, list_of_repairs_applied).

    Repairs:
      1. Remove edges whose source or target references a missing node ID.
      2. For nodes with parent_id but no valid parent edge, insert a 'contains' edge.
      3. Remove duplicate nodes (keep first occurrence by list position).
    """
    repairs: list[str] = []
    nodes: list[dict] = data.get("nodes", [])
    edges: list[dict] = data.get("edges", [])

    # 3. Deduplicate nodes (keep first occurrence)
    seen_ids: set[str] = set()
    deduped_nodes = []
    for n in nodes:
        nid = n.get("id")
        if nid and nid in seen_ids:
            repairs.append(f"Removed duplicate node '{nid}'")
        else:
            deduped_nodes.append(n)
            if nid:
                seen_ids.add(nid)
    nodes = deduped_nodes
    node_ids = seen_ids

    # 1. Remove dangling edges
    clean_edges = []
    for e in edges:
        src = e.get("source")
        tgt = e.get("target")
        if src and src not in node_ids:
            repairs.append(f"Removed dangling edge: '{src}' → '{tgt}' (source missing)")
            continue
        if tgt and tgt not in node_ids:
            repairs.append(f"Removed dangling edge: '{src}' → '{tgt}' (target missing)")
            continue
        clean_edges.append(e)
    edges = clean_edges

    # 2. Add missing parent→child edges
    edge_tuples = {
        (e.get("source"), e.get("target"), e.get("relation"))
        for e in edges
    }
    valid_parent_relations = {"contains", "exposes", "owns_data_in"}
    for n in nodes:
        parent = n.get("parent_id")
        if not parent:
            continue
        nid = n.get("id")
        if not any((parent, nid, rel) in edge_tuples for rel in valid_parent_relations):
            new_edge = {
                "source": parent,
                "target": nid,
                "relation": "contains",
                "group": "structural",
                "weight": 1.0,
                "confidence": 0.5,
                "notes": "auto-added by validate_graph --fix",
            }
            edges.append(new_edge)
            edge_tuples.add((parent, nid, "contains"))
            repairs.append(f"Added missing 'contains' edge: '{parent}' → '{nid}'")

    data = dict(data)
    data["nodes"] = nodes
    data["edges"] = edges
    # Update meta counts
    if "meta" in data:
        data["meta"] = dict(data["meta"])
        data["meta"]["node_count"] = len(nodes)
        data["meta"]["edge_count"] = len(edges)
    return data, repairs


def validate(graph_path: str, max_age_days: int = 90, fix: bool = False) -> dict:
    path = Path(graph_path)
    if not path.exists():
        return {"error": f"File not found: {graph_path}"}

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return {"error": f"JSON parse error: {exc}"}

    repairs_applied: list[str] = []
    if fix:
        data, repairs_applied = auto_fix(data)
        if repairs_applied:
            path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    nodes = data.get("nodes", [])
    edges = data.get("edges", [])

    results = []
    for fn in CHECKS:
        name = fn.__name__.replace("check_", "")
        if fn is check_staleness:
            issues = fn(nodes, edges, max_age_days)
        else:
            issues = fn(nodes, edges)

        passed = len(issues) == 0
        results.append({
            "check": name,
            "passed": passed,
            "issue_count": len(issues),
            "issues": issues[:10],
        })

    passed_count = sum(1 for r in results if r["passed"])
    total = len(results)

    report = {
        "graph": str(path),
        "checks_passed": passed_count,
        "checks_total": total,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "repairs_applied": repairs_applied,
        "results": results,
    }
    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Validate a knowledge-graph.json file against 8 integrity checks."
    )
    parser.add_argument("graph", help="Path to knowledge-graph.json")
    parser.add_argument(
        "--max-age-days", type=int, default=90, metavar="N",
        help="Staleness threshold in days for last_verified_at (default: 90)"
    )
    parser.add_argument(
        "--fix", action="store_true",
        help=(
            "Auto-repair the graph in place before validation: remove dangling edges, "
            "add missing parent→child edges, deduplicate nodes"
        ),
    )
    parser.add_argument(
        "--output", metavar="FILE",
        help="Optional path to write the JSON validation report.",
    )
    args = parser.parse_args()

    report = validate(args.graph, max_age_days=args.max_age_days, fix=args.fix)
    output_report = report_for_output(report, args.output)
    rendered = json.dumps(output_report, indent=2)
    print(rendered)

    if args.output:
        out_path = Path(args.output).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(rendered, encoding="utf-8")

    if "error" in report:
        sys.exit(1)
    sys.exit(0 if report["checks_passed"] == report["checks_total"] else 1)


if __name__ == "__main__":
    main()
