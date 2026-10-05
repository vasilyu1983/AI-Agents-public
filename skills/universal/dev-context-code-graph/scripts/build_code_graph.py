#!/usr/bin/env python3
"""Build a code graph JSON from code-profile artifacts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


GRAPH_CONTRACT_VERSION = "1.0"
EDGE_WEIGHTS = {
    "contains": 1.0,
    "defines": 0.95,
    "imports": 0.72,
    "calls": 0.8,
    "inherits": 0.78,
    "references": 0.55,
    "tests": 0.7,
}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_id(text: str) -> str:
    return re.sub(r"[^a-z0-9._-]", "-", text.lower().strip()).strip("-")


class GraphBuilder:
    def __init__(self) -> None:
        self.nodes: dict[str, dict] = {}
        self.edge_keys: set[tuple[str, str, str]] = set()
        self.edges: list[dict] = []
        self.repo_ids: set[str] = set()

    def add_node(self, node_id: str, node_type: str, label: str, **kwargs) -> None:
        if node_id not in self.nodes:
            node = {"id": node_id, "type": node_type, "label": label}
            for key, value in kwargs.items():
                if value is not None:
                    node[key] = value
            self.nodes[node_id] = node
            return

        existing = self.nodes[node_id]
        for key, value in kwargs.items():
            if value is None:
                continue
            if key == "tags":
                existing.setdefault("tags", [])
                existing["tags"] = sorted(set(existing["tags"]) | set(value))
            elif key == "properties":
                existing.setdefault("properties", {})
                for prop_key, prop_value in value.items():
                    existing["properties"].setdefault(prop_key, prop_value)
            elif key == "evidence":
                existing.setdefault("evidence", [])
                existing["evidence"].extend(value)
            elif key not in existing:
                existing[key] = value

    def add_edge(self, source: str, target: str, relation: str, group: str, confidence: float | None = None, notes: str | None = None) -> None:
        key = (source, target, relation)
        if key in self.edge_keys:
            return
        self.edge_keys.add(key)
        payload = {
            "source": source,
            "target": target,
            "relation": relation,
            "group": group,
            "weight": EDGE_WEIGHTS.get(relation, 0.5),
        }
        if confidence is not None:
            payload["confidence"] = round(confidence, 3)
        if notes:
            payload["notes"] = notes
        self.edges.append(payload)

    def ensure_external_node(self, node_id: str) -> None:
        if node_id in self.nodes:
            return
        label = node_id.split("#", 2)[-1].replace("-", " ")
        self.add_node(node_id, "external_symbol", label, confidence=0.45)

    def to_dict(self) -> dict:
        return {
            "meta": {
                "generated_at": now_iso(),
                "version": "1.0",
                "graph_contract_version": GRAPH_CONTRACT_VERSION,
                "build_source": "code_profiles",
                "node_count": len(self.nodes),
                "edge_count": len(self.edges),
                "repo_count": len(self.repo_ids),
            },
            "nodes": list(self.nodes.values()),
            "edges": self.edges,
        }


def build_from_profiles(profiles_dir: Path, graph: GraphBuilder) -> None:
    json_files = sorted(profiles_dir.glob("*.json"))
    if not json_files:
        raise SystemExit(f"No profile JSON files found in {profiles_dir}")

    for path in json_files:
        profile = json.loads(path.read_text(encoding="utf-8"))
        repo_id = profile["repo_id"]
        graph.repo_ids.add(repo_id)
        graph.add_node(
            repo_id,
            "repo",
            profile["repo_name"],
            path=profile.get("repo_path"),
            summary=profile.get("summary"),
            confidence=profile.get("confidence_score"),
            first_seen_at=profile.get("last_scanned_at"),
            last_verified_at=profile.get("last_scanned_at"),
        )

        file_ids = {entry["id"] for entry in profile.get("files", [])}
        symbol_ids = {entry["id"] for entry in profile.get("symbols", [])}

        for entry in profile.get("files", []):
            graph.add_node(
                entry["id"],
                "file",
                entry["path"],
                parent_id=repo_id,
                path=entry["path"],
                language=entry["language"],
                kind=entry.get("kind"),
                parse_status=entry.get("parse_status"),
                confidence=entry.get("confidence"),
                first_seen_at=profile.get("last_scanned_at"),
                last_verified_at=profile.get("last_scanned_at"),
            )
            graph.add_edge(repo_id, entry["id"], "contains", "structural", 1.0)

        for entry in profile.get("symbols", []):
            graph.add_node(
                entry["id"],
                entry["type"],
                entry["label"],
                parent_id=entry["parent_id"],
                path=entry.get("path"),
                language=entry.get("language"),
                line_start=entry.get("line_start"),
                line_end=entry.get("line_end"),
                properties={"signature": entry.get("signature")} if entry.get("signature") else {},
                confidence=entry.get("confidence"),
                first_seen_at=profile.get("last_scanned_at"),
                last_verified_at=profile.get("last_scanned_at"),
            )
            graph.add_edge(entry["parent_id"], entry["id"], "defines", "structural", entry.get("confidence", 0.8))

        known_nodes = file_ids | symbol_ids | {repo_id}
        for relation in profile.get("relations", []):
            source = relation["source"]
            target = relation["target"]
            if source not in known_nodes and source not in graph.nodes:
                graph.ensure_external_node(source)
            if target not in known_nodes and target not in graph.nodes:
                graph.ensure_external_node(target)
            graph.add_edge(
                source,
                target,
                relation["relation"],
                relation["group"],
                relation.get("confidence"),
                relation.get("notes"),
            )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", required=True, help="Directory containing code-profile JSON files")
    parser.add_argument("--output", help="Output path for code-graph.json")
    args = parser.parse_args()

    profiles_dir = Path(args.profiles).expanduser().resolve()
    output = Path(args.output).expanduser().resolve() if args.output else (profiles_dir.parent / "graphs" / "code-graph.json")
    output.parent.mkdir(parents=True, exist_ok=True)

    graph = GraphBuilder()
    build_from_profiles(profiles_dir, graph)
    payload = graph.to_dict()
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"[ok] Wrote code graph to {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
