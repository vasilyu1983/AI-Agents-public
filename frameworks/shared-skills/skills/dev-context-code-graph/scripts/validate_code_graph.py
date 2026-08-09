#!/usr/bin/env python3
"""Validate a code-graph.json file against 8 integrity checks."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path


VALID_NODE_TYPES = {"repo", "file", "module", "class", "function", "method", "test", "external_symbol"}
VALID_EDGE_RELATIONS = {"contains", "defines", "imports", "calls", "inherits", "references", "tests"}
VALID_EDGE_GROUPS = {"structural", "dependency", "behavioral", "semantic"}
VALID_PARSE_STATUS = {"parsed", "heuristic", "unsupported", "error", "skipped"}


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
    rendered["graph"] = report_path_value(rendered.get("graph"), output_path)
    return rendered


def check_schema_compliance(nodes: list[dict], edges: list[dict]) -> list[str]:
    issues: list[str] = []
    for node in nodes:
        if node.get("type") not in VALID_NODE_TYPES:
            issues.append(f"Node '{node.get('id', '?')}' has invalid type '{node.get('type')}'")
        confidence = node.get("confidence")
        if confidence is not None and not 0 <= confidence <= 1:
            issues.append(f"Node '{node.get('id', '?')}' has invalid confidence '{confidence}'")
        parse_status = node.get("parse_status")
        if parse_status is not None and parse_status not in VALID_PARSE_STATUS:
            issues.append(f"Node '{node.get('id', '?')}' has invalid parse_status '{parse_status}'")
    for edge in edges:
        if edge.get("relation") not in VALID_EDGE_RELATIONS:
            issues.append(f"Edge {edge.get('source', '?')}->{edge.get('target', '?')} has invalid relation '{edge.get('relation')}'")
        if edge.get("group") not in VALID_EDGE_GROUPS:
            issues.append(f"Edge {edge.get('source', '?')}->{edge.get('target', '?')} has invalid group '{edge.get('group')}'")
        confidence = edge.get("confidence")
        if confidence is not None and not 0 <= confidence <= 1:
            issues.append(f"Edge {edge.get('source', '?')}->{edge.get('target', '?')} has invalid confidence '{confidence}'")
    return issues


def check_dangling_refs(nodes: list[dict], edges: list[dict]) -> list[str]:
    node_ids = {node["id"] for node in nodes if "id" in node}
    issues: list[str] = []
    for edge in edges:
        if edge.get("source") not in node_ids:
            issues.append(f"Unknown source node '{edge.get('source')}'")
        if edge.get("target") not in node_ids:
            issues.append(f"Unknown target node '{edge.get('target')}'")
    return issues


def check_orphans(nodes: list[dict], edges: list[dict]) -> list[str]:
    connected: set[str] = set()
    for edge in edges:
        connected.add(edge.get("source"))
        connected.add(edge.get("target"))
    return [
        f"Node '{node['id']}' (type={node.get('type')}) has zero edges"
        for node in nodes
        if node.get("id") not in connected
    ]


def check_duplicates(nodes: list[dict]) -> list[str]:
    seen: dict[str, int] = {}
    for node in nodes:
        if "id" in node:
            seen[node["id"]] = seen.get(node["id"], 0) + 1
    return [f"Node id '{node_id}' is duplicated {count} times" for node_id, count in seen.items() if count > 1]


def check_parent_edges(nodes: list[dict], edges: list[dict]) -> list[str]:
    edge_keys = {(edge.get("source"), edge.get("target"), edge.get("relation")) for edge in edges}
    issues: list[str] = []
    for node in nodes:
        parent_id = node.get("parent_id")
        if not parent_id:
            continue
        if (parent_id, node["id"], "contains") not in edge_keys and (parent_id, node["id"], "defines") not in edge_keys:
            issues.append(f"Node '{node['id']}' has parent_id '{parent_id}' but no parent edge")
    return issues


def check_circular_imports(edges: list[dict]) -> list[str]:
    graph: dict[str, list[str]] = {}
    for edge in edges:
        if edge.get("relation") == "imports":
            graph.setdefault(edge["source"], []).append(edge["target"])

    visited: set[str] = set()
    stack: set[str] = set()
    issues: list[str] = []

    def dfs(node_id: str, path: list[str]) -> None:
        visited.add(node_id)
        stack.add(node_id)
        for target in graph.get(node_id, []):
            if target not in visited:
                dfs(target, path + [target])
            elif target in stack:
                cycle = path + [target]
                issues.append(f"Circular import: {' -> '.join(cycle)}")
        stack.discard(node_id)

    for node_id in graph:
        if node_id not in visited:
            dfs(node_id, [node_id])
    return issues


def check_staleness(nodes: list[dict], max_age_days: int) -> list[str]:
    threshold = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    issues: list[str] = []
    for node in nodes:
        stamp = node.get("last_verified_at")
        if not stamp:
            continue
        try:
            parsed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        except ValueError:
            issues.append(f"Node '{node.get('id', '?')}' has invalid last_verified_at '{stamp}'")
            continue
        if parsed < threshold:
            issues.append(f"Node '{node.get('id', '?')}' is stale ({stamp})")
    return issues


def check_parse_status_and_confidence(nodes: list[dict]) -> list[str]:
    issues: list[str] = []
    for node in nodes:
        if node.get("type") != "file":
            continue
        parse_status = node.get("parse_status")
        if parse_status not in VALID_PARSE_STATUS:
            issues.append(f"File node '{node.get('id', '?')}' is missing a valid parse_status")
        if parse_status == "unsupported" and node.get("confidence", 1) > 0.5:
            issues.append(f"Unsupported file node '{node.get('id', '?')}' has inflated confidence")
    return issues


def load_graph(graph_path: Path) -> dict:
    return json.loads(graph_path.read_text(encoding="utf-8"))


def apply_fixes(graph: dict) -> dict:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    node_ids = {node["id"] for node in nodes if "id" in node}
    edges = [edge for edge in edges if edge.get("source") in node_ids and edge.get("target") in node_ids]

    edge_keys = {(edge.get("source"), edge.get("target"), edge.get("relation")) for edge in edges}
    for node in nodes:
        parent_id = node.get("parent_id")
        if not parent_id or parent_id not in node_ids:
            continue
        if (parent_id, node["id"], "contains") in edge_keys or (parent_id, node["id"], "defines") in edge_keys:
            continue
        relation = "contains" if node.get("type") == "file" else "defines"
        edges.append(
            {
                "source": parent_id,
                "target": node["id"],
                "relation": relation,
                "group": "structural",
                "weight": 1.0 if relation == "contains" else 0.95,
                "confidence": 0.9,
            }
        )
    graph["edges"] = edges
    graph.setdefault("meta", {})
    graph["meta"]["node_count"] = len(nodes)
    graph["meta"]["edge_count"] = len(edges)
    return graph


def validate_graph(graph: dict, max_age_days: int) -> dict:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    checks = {
        "schema_compliance": check_schema_compliance(nodes, edges),
        "dangling_refs": check_dangling_refs(nodes, edges),
        "orphans": check_orphans(nodes, edges),
        "duplicates": check_duplicates(nodes),
        "parent_edges": check_parent_edges(nodes, edges),
        "circular_imports": check_circular_imports(edges),
        "staleness": check_staleness(nodes, max_age_days),
        "parse_status_and_confidence": check_parse_status_and_confidence(nodes),
    }
    passed = sum(1 for issues in checks.values() if not issues)
    return {
        "checks": checks,
        "checks_passed": passed,
        "checks_total": len(checks),
        "issues_total": sum(len(issues) for issues in checks.values()),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", help="Path to code-graph.json")
    parser.add_argument("--max-age-days", type=int, default=90, help="Staleness threshold in days")
    parser.add_argument("--fix", action="store_true", help="Auto-repair dangling edges and missing parent edges")
    parser.add_argument("--output", help="Optional path to write JSON validation report")
    args = parser.parse_args()

    graph_path = Path(args.graph).expanduser().resolve()
    graph = load_graph(graph_path)
    if args.fix:
        graph = apply_fixes(graph)
        graph_path.write_text(json.dumps(graph, indent=2), encoding="utf-8")

    report = validate_graph(graph, args.max_age_days)
    payload = {
        "graph": str(graph_path),
        "checks_passed": report["checks_passed"],
        "checks_total": report["checks_total"],
        "issues_total": report["issues_total"],
        "checks": report["checks"],
    }
    if args.output:
        output_path = Path(args.output).expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report_for_output(payload, str(output_path)), indent=2), encoding="utf-8")

    status = "PASS" if report["issues_total"] == 0 else "FAIL"
    print(f"Status: {status}")
    print(f"Checks: {report['checks_passed']}/{report['checks_total']}")
    print(f"Issues: {report['issues_total']}")
    return 0 if report["issues_total"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
