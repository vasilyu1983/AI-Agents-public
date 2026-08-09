#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


GRAPH_KEYS = ("routes_from", "composes", "feeds", "depends_on")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build and validate the shared-skill graph from frontmatter metadata.")
    parser.add_argument("catalog_root", help="Path to the skills catalog root")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--check", action="store_true", help="Validate graph edges and print a status summary")
    parser.add_argument("--mermaid", action="store_true", help="Print a Mermaid graph")
    return parser.parse_args()


def skill_dirs(catalog_root: Path) -> list[Path]:
    return sorted(path for path in catalog_root.iterdir() if path.is_dir() and not path.name.startswith("."))


def frontmatter_lines(skill_md: Path) -> list[str]:
    lines = skill_md.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{skill_md} is missing opening frontmatter delimiter")

    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            return lines[1:index]

    raise ValueError(f"{skill_md} is missing closing frontmatter delimiter")


def strip_quotes(raw: str) -> str:
    if (raw.startswith('"') and raw.endswith('"')) or (raw.startswith("'") and raw.endswith("'")):
        return raw[1:-1]
    return raw


def parse_inline_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []
    if raw == "[]":
        return []
    if not (raw.startswith("[") and raw.endswith("]")):
        return [strip_quotes(raw)]

    inner = raw[1:-1].strip()
    if not inner:
        return []

    return [strip_quotes(item.strip()) for item in inner.split(",") if item.strip()]


def parse_graph_metadata(skill_md: Path) -> dict[str, list[str]]:
    lines = frontmatter_lines(skill_md)
    graph: dict[str, list[str]] = {}
    in_metadata = False
    metadata_indent = 0
    in_graph = False
    graph_indent = 0
    current_key: str | None = None

    index = 0
    while index < len(lines):
        raw = lines[index]
        stripped = raw.strip()
        indent = len(raw) - len(raw.lstrip(" "))

        if not stripped:
            index += 1
            continue

        if not in_metadata:
            if stripped == "metadata:":
                in_metadata = True
                metadata_indent = indent
            index += 1
            continue

        if indent <= metadata_indent:
            in_metadata = False
            in_graph = False
            current_key = None
            continue

        if not in_graph:
            if stripped == "graph:":
                in_graph = True
                graph_indent = indent
            index += 1
            continue

        if indent <= graph_indent:
            in_graph = False
            current_key = None
            continue

        if indent == graph_indent + 2 and ":" in stripped:
            key, value = stripped.split(":", 1)
            key = key.strip()
            if key not in GRAPH_KEYS:
                index += 1
                current_key = None
                continue
            value = value.strip()
            if value:
                graph[key] = parse_inline_list(value)
                current_key = None
            else:
                graph[key] = []
                current_key = key
            index += 1
            continue

        if current_key and indent >= graph_indent + 4 and stripped.startswith("- "):
            graph.setdefault(current_key, []).append(strip_quotes(stripped[2:].strip()))

        index += 1

    return {key: value for key, value in graph.items() if value}


def collect_graph(catalog_root: Path) -> tuple[dict[str, dict[str, list[str]]], list[str]]:
    graph: dict[str, dict[str, list[str]]] = {}
    errors: list[str] = []
    skill_names = {path.name for path in skill_dirs(catalog_root)}

    for skill_dir in skill_dirs(catalog_root):
        try:
            metadata = parse_graph_metadata(skill_dir / "SKILL.md")
        except ValueError as exc:
            errors.append(str(exc))
            continue
        if metadata:
            graph[skill_dir.name] = metadata

    for source, relations in graph.items():
        for relation, targets in relations.items():
            for target in targets:
                if target == source:
                    errors.append(f"`{source}` has a self-referential `{relation}` edge")
                elif target not in skill_names:
                    errors.append(f"`{source}` references unknown skill `{target}` via `{relation}`")

    return graph, errors


def edges_from_graph(graph: dict[str, dict[str, list[str]]]) -> list[dict[str, str]]:
    edges: list[dict[str, str]] = []
    for source, relations in sorted(graph.items()):
        for relation, targets in sorted(relations.items()):
            for target in targets:
                edge_source = target if relation == "routes_from" else source
                edge_target = source if relation == "routes_from" else target
                edges.append({"from": edge_source, "to": edge_target, "type": relation})
    return edges


def mermaid(graph: dict[str, dict[str, list[str]]]) -> str:
    lines = ["graph TD"]
    for edge in edges_from_graph(graph):
        lines.append(f"  {edge['from']} -->|{edge['type']}| {edge['to']}")
    return "\n".join(lines)


def main() -> int:
    args = parse_args()
    catalog_root = Path(args.catalog_root).resolve()
    graph, errors = collect_graph(catalog_root)
    edges = edges_from_graph(graph)

    if args.json:
        payload = {
            "catalog_root": str(catalog_root),
            "skills_with_graph_metadata": len(graph),
            "edge_count": len(edges),
            "errors": errors,
            "graph": graph,
            "edges": edges,
        }
        print(json.dumps(payload, indent=2))
    elif args.mermaid:
        print(mermaid(graph))
    else:
        print("## Skill Graph Summary")
        print()
        print(f"- Catalog: `{catalog_root}`")
        print(f"- Skills with graph metadata: {len(graph)}")
        print(f"- Edge count: {len(edges)}")
        print(f"- Errors: {len(errors)}")
        print()
        print("Status: PASS" if not errors else "Status: FAIL")
        if errors:
            print()
            print("## Graph Errors")
            for error in errors:
                print(f"- {error}")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
