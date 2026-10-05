#!/usr/bin/env python3
"""Generate static Markdown and HTML reports from code-graph.json."""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path


def load_json(path: Path | None) -> dict | None:
    if path is None or not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def top_nodes(nodes: list[dict], edges: list[dict], limit: int = 20) -> list[dict]:
    incoming = defaultdict(float)
    for edge in edges:
        incoming[edge["target"]] += float(edge.get("weight", 1.0))
    ranked = []
    for node in nodes:
        ranked.append(
            {
                "label": node.get("label", node["id"]),
                "type": node.get("type"),
                "path": node.get("path", ""),
                "importance": round(incoming.get(node["id"], 0.0), 3),
            }
        )
    ranked.sort(key=lambda row: (-row["importance"], row["label"]))
    return ranked[:limit]


def render_markdown(graph: dict, validation: dict | None) -> str:
    nodes = graph.get("nodes", [])
    edges = graph.get("edges", [])
    node_counts = Counter(node.get("type") for node in nodes)
    edge_counts = Counter(edge.get("relation") for edge in edges)
    lines = ["# Code Graph Report", ""]
    lines.append(f"- Generated: {graph.get('meta', {}).get('generated_at', 'unknown')}")
    lines.append(f"- Repos: {graph.get('meta', {}).get('repo_count', 0)}")
    lines.append(f"- Nodes: {graph.get('meta', {}).get('node_count', len(nodes))}")
    lines.append(f"- Edges: {graph.get('meta', {}).get('edge_count', len(edges))}")
    if validation:
        lines.append(f"- Validation: {validation.get('checks_passed', 0)}/{validation.get('checks_total', 0)} checks passed")
    lines.append("")
    lines.append("## Node Types")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|------|-------|")
    for node_type, count in sorted(node_counts.items()):
        lines.append(f"| {node_type} | {count} |")
    lines.append("")
    lines.append("## Edge Relations")
    lines.append("")
    lines.append("| Relation | Count |")
    lines.append("|----------|-------|")
    for relation, count in sorted(edge_counts.items()):
        lines.append(f"| {relation} | {count} |")
    lines.append("")
    lines.append("## Most Referenced Nodes")
    lines.append("")
    lines.append("| Label | Type | Path | Importance |")
    lines.append("|-------|------|------|------------|")
    for row in top_nodes(nodes, edges):
        lines.append(f"| {row['label']} | {row['type']} | {row['path']} | {row['importance']} |")
    return "\n".join(lines) + "\n"


def render_html(markdown_report: str) -> str:
    body = markdown_report.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return (
        "<!doctype html><html><head><meta charset='utf-8'>"
        "<title>Code Graph Report</title>"
        "<style>body{font-family:system-ui,sans-serif;max-width:1080px;margin:40px auto;padding:0 24px;line-height:1.5}pre{white-space:pre-wrap}</style>"
        "</head><body><pre>"
        + body
        + "</pre></body></html>"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("graph", help="Path to code-graph.json")
    parser.add_argument("--output-dir", required=True, help="Directory for markdown and html reports")
    parser.add_argument("--validation", help="Optional path to code-graph-validation.json")
    args = parser.parse_args()

    graph = load_json(Path(args.graph).expanduser().resolve())
    if graph is None:
        raise SystemExit("Graph file not found")
    validation = load_json(Path(args.validation).expanduser().resolve()) if args.validation else None
    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown_report = render_markdown(graph, validation)
    html_report = render_html(markdown_report)

    md_path = output_dir / "code-graph-report.md"
    html_path = output_dir / "code-graph-report.html"
    md_path.write_text(markdown_report, encoding="utf-8")
    html_path.write_text(html_report, encoding="utf-8")
    print(f"[ok] Wrote {md_path}")
    print(f"[ok] Wrote {html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
