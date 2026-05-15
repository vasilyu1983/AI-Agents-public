#!/usr/bin/env python3
"""Calibrate knowledge-graph edge weights from evidence and provenance signals."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


DIRECT_EVIDENCE_TERMS = (
    "manifest",
    "schema",
    "workflow",
    "migration",
    "contract",
    "api-catalog",
    "database-schemas",
    "package",
    "lockfile",
    "project",
    "solution",
)
INDIRECT_EVIDENCE_TERMS = (
    "mermaid",
    "overview",
    "readme",
    "prose",
    "summary",
    "matrix",
    "catalog",
)


def load_graph(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_graph(path: Path, graph: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def edge_key(edge: dict) -> tuple[str, str, str]:
    return (
        str(edge.get("source", "")),
        str(edge.get("target", "")),
        str(edge.get("relation", "")),
    )


def clamp(value: float, low: float = 0.05, high: float = 1.0) -> float:
    return max(low, min(high, value))


def base_weight(edge: dict) -> float:
    value = edge.get("weight_static", edge.get("weight", 0.5))
    try:
        return clamp(float(value))
    except (TypeError, ValueError):
        return 0.5


def evidence_items(edge: dict) -> list[dict]:
    evidence = edge.get("evidence")
    return evidence if isinstance(evidence, list) else []


def evidence_factor(edge: dict) -> float:
    return min(1.2, 0.5 + 0.1 * len(evidence_items(edge)))


def provenance_factor(edge: dict) -> float:
    evidence = evidence_items(edge)
    if not evidence:
        return 0.7 if edge.get("relation") in {"documents", "related_to", "co_occurs"} else 0.8

    text = " ".join(
        str(item.get("path", "")) + " " + str(item.get("reason", "")) + " " + str(item.get("source", ""))
        for item in evidence
        if isinstance(item, dict)
    ).lower()
    if any(term in text for term in DIRECT_EVIDENCE_TERMS):
        return 1.1
    if any(term in text for term in INDIRECT_EVIDENCE_TERMS):
        return 0.7
    return 0.9


def agreement_factor(edge: dict, grouped_edges: dict[tuple[str, str, str], list[dict]]) -> float:
    if edge.get("relation") == "contradicts" or edge.get("properties", {}).get("contradicted"):
        return 0.6

    evidence = evidence_items(edge)
    distinct_sources = {
        str(item.get("path") or item.get("source") or item.get("reason"))
        for item in evidence
        if isinstance(item, dict) and (item.get("path") or item.get("source") or item.get("reason"))
    }
    if len(distinct_sources) >= 3:
        return 1.2
    if len(grouped_edges.get(edge_key(edge), [])) >= 3:
        return 1.2
    return 1.0


def calibrate_graph(graph: dict, *, activate: bool = True) -> tuple[dict, dict]:
    edges = graph.get("edges", [])
    grouped: dict[tuple[str, str, str], list[dict]] = {}
    for edge in edges:
        grouped.setdefault(edge_key(edge), []).append(edge)

    changed = 0
    decreases = 0
    increases = 0
    for edge in edges:
        static = base_weight(edge)
        factors = {
            "evidence": round(evidence_factor(edge), 3),
            "provenance": round(provenance_factor(edge), 3),
            "agreement": round(agreement_factor(edge, grouped), 3),
        }
        calibrated = clamp(static * factors["evidence"] * factors["provenance"] * factors["agreement"])
        calibrated = round(calibrated, 4)

        edge["weight_static"] = round(static, 4)
        edge["weight_calibrated"] = calibrated
        edge["weight_factors"] = factors
        if activate:
            edge["weight"] = calibrated

        if calibrated != round(static, 4):
            changed += 1
            if calibrated > static:
                increases += 1
            else:
                decreases += 1

    graph.setdefault("meta", {})["weight_calibration"] = {
        "mode": "calibrated" if activate else "computed",
        "edge_count": len(edges),
        "changed_edges": changed,
        "increased_edges": increases,
        "decreased_edges": decreases,
    }
    return graph, graph["meta"]["weight_calibration"]


def diff_rows(original: dict, calibrated: dict, top: int) -> list[dict]:
    before = {edge_key(edge): edge for edge in original.get("edges", [])}
    rows = []
    for edge in calibrated.get("edges", []):
        key = edge_key(edge)
        old_weight = base_weight(before.get(key, {}))
        new_weight = float(edge.get("weight_calibrated", edge.get("weight", old_weight)))
        delta = round(new_weight - old_weight, 4)
        if delta == 0:
            continue
        rows.append(
            {
                "source": key[0],
                "target": key[1],
                "relation": key[2],
                "weight_static": round(old_weight, 4),
                "weight_calibrated": round(new_weight, 4),
                "delta": delta,
                "weight_factors": edge.get("weight_factors", {}),
            }
        )
    rows.sort(key=lambda row: (-abs(row["delta"]), row["source"], row["relation"], row["target"]))
    return rows if top == 0 else rows[:top]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", help="Path to knowledge-graph.json")
    parser.add_argument("--output", help="Output path. Defaults to overwriting the input graph.")
    parser.add_argument("--no-activate", action="store_true", help="Compute calibrated fields but leave active weight unchanged")
    parser.add_argument("--diff", action="store_true", help="Print top weight changes as JSON")
    parser.add_argument("--top", type=int, default=20, help="Rows to print with --diff (default: 20; 0 = all)")
    args = parser.parse_args()

    graph_path = Path(args.graph)
    original = load_graph(graph_path)
    graph = json.loads(json.dumps(original))
    graph, summary = calibrate_graph(graph, activate=not args.no_activate)

    output_path = Path(args.output) if args.output else graph_path
    write_graph(output_path, graph)

    payload = {
        "graph": str(graph_path),
        "output": str(output_path),
        "summary": summary,
    }
    if args.diff:
        payload["diff"] = diff_rows(original, graph, args.top)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
