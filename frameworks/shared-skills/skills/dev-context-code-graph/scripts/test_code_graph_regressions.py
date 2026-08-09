#!/usr/bin/env python3
"""Regression tests for the dev-context-code-graph scripts."""

from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


scan_code_repo = load_module("scan_code_repo.py", "dev_context_code_graph_scan")
build_code_graph = load_module("build_code_graph.py", "dev_context_code_graph_build")
validate_code_graph = load_module("validate_code_graph.py", "dev_context_code_graph_validate")
query_code_graph = load_module("query_code_graph.py", "dev_context_code_graph_query")
export_code_graph_report = load_module("export_code_graph_report.py", "dev_context_code_graph_report")


class CodeGraphRegressionTests(unittest.TestCase):
    def test_python_repo_scan_build_validate_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "py-repo"
            repo.mkdir()
            (repo / "app.py").write_text(
                "def helper():\n    return 1\n\n"
                "class Service:\n    def run(self):\n        return helper()\n",
                encoding="utf-8",
            )
            (repo / "test_app.py").write_text(
                "from app import helper\n\n"
                "def test_helper():\n    assert helper() == 1\n",
                encoding="utf-8",
            )

            profile = scan_code_repo.scan_repo(repo)
            self.assertEqual(profile["repo_id"], "py-repo")
            self.assertGreaterEqual(len(profile["files"]), 2)
            self.assertTrue(any(symbol["type"] == "function" and symbol["label"] == "helper" for symbol in profile["symbols"]))
            self.assertTrue(any(relation["relation"] == "tests" for relation in profile["relations"]))

            profiles_dir = Path(tmpdir) / "code-profiles"
            profiles_dir.mkdir()
            (profiles_dir / "py-repo.json").write_text(json.dumps(profile, indent=2), encoding="utf-8")

            graph = build_code_graph.GraphBuilder()
            build_code_graph.build_from_profiles(profiles_dir, graph)
            graph_payload = graph.to_dict()
            self.assertEqual(graph_payload["meta"]["repo_count"], 1)
            self.assertTrue(any(node["type"] == "file" for node in graph_payload["nodes"]))
            self.assertTrue(any(edge["relation"] == "calls" for edge in graph_payload["edges"]))

            report = validate_code_graph.validate_graph(graph_payload, 90)
            self.assertEqual(report["issues_total"], 0)

            graph_path = Path(tmpdir) / "graphs" / "code-graph.json"
            graph_path.parent.mkdir()
            graph_path.write_text(json.dumps(graph_payload, indent=2), encoding="utf-8")
            markdown = export_code_graph_report.render_markdown(graph_payload, None)
            self.assertIn("Code Graph Report", markdown)

    def test_typescript_repo_links_relative_imports(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            repo = Path(tmpdir) / "ts-repo"
            (repo / "src").mkdir(parents=True)
            (repo / "src" / "math.ts").write_text("export function sum(a: number, b: number) { return a + b; }\n", encoding="utf-8")
            (repo / "src" / "app.ts").write_text(
                "import { sum } from './math'\n"
                "export function runApp() { return sum(1, 2) }\n",
                encoding="utf-8",
            )
            (repo / "src" / "app.test.ts").write_text(
                "import { runApp } from './app'\n"
                "test('runs', () => { runApp() })\n",
                encoding="utf-8",
            )

            profile = scan_code_repo.scan_repo(repo)
            imports = [relation for relation in profile["relations"] if relation["relation"] == "imports"]
            self.assertTrue(imports)
            self.assertTrue(any(relation["relation"] == "tests" for relation in profile["relations"]))
            self.assertTrue(any("math.ts" in file_entry["path"] for file_entry in profile["files"]))
            self.assertTrue(any(symbol["label"] == "runApp" for symbol in profile["symbols"]))

    def test_query_search_rank_and_path(self) -> None:
        nodes = [
            {"id": "repo#file#a", "type": "file", "label": "a.py"},
            {"id": "repo#file#a#function#helper", "type": "function", "label": "helper", "parent_id": "repo#file#a"},
            {"id": "repo#file#test#test-helper", "type": "test", "label": "test_helper", "parent_id": "repo#file#test"},
        ]
        edges = [
            {"source": "repo#file#a", "target": "repo#file#a#function#helper", "relation": "defines", "group": "structural", "weight": 0.95},
            {"source": "repo#file#test#test-helper", "target": "repo#file#a#function#helper", "relation": "tests", "group": "behavioral", "weight": 0.7},
        ]
        results = query_code_graph.query_search(nodes, "helper", None, 10)
        self.assertEqual(results[0]["label"], "helper")
        ranked = query_code_graph.rank_nodes(nodes, edges, None, 10)
        self.assertEqual(ranked[0]["label"], "helper")
        forward, _backward = query_code_graph.build_adjacency(edges)
        paths = query_code_graph.bfs_paths("repo#file#test#test-helper", "repo#file#a#function#helper", forward, 2)
        self.assertEqual(paths[0][-1], "repo#file#a#function#helper")

    def test_apply_fixes_adds_missing_parent_edge(self) -> None:
        graph = {
            "meta": {"generated_at": "2026-03-22T00:00:00+00:00", "version": "1.0", "graph_contract_version": "1.0", "build_source": "code_profiles", "node_count": 2, "edge_count": 0, "repo_count": 1},
            "nodes": [
                {"id": "repo", "type": "repo", "label": "repo"},
                {"id": "repo#file#a", "type": "file", "label": "a.py", "parent_id": "repo", "parse_status": "parsed"},
            ],
            "edges": [],
        }
        fixed = validate_code_graph.apply_fixes(graph)
        self.assertTrue(any(edge["relation"] == "contains" for edge in fixed["edges"]))


if __name__ == "__main__":
    unittest.main()
