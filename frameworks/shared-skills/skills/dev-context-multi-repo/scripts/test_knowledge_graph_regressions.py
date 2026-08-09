#!/usr/bin/env python3
"""Regression tests for multi-repo knowledge graph tooling."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent


def load_module(filename: str, module_name: str):
    spec = importlib.util.spec_from_file_location(module_name, SCRIPT_DIR / filename)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


build_knowledge_graph = load_module(
    "build_knowledge_graph.py",
    "dev_context_multi_repo_build_knowledge_graph",
)
incremental_update = load_module(
    "incremental_update.py",
    "dev_context_multi_repo_incremental_update",
)
check_graph_consistency = load_module(
    "check_graph_consistency.py",
    "dev_context_multi_repo_check_graph_consistency",
)
validate_graph = load_module(
    "validate_graph.py",
    "dev_context_multi_repo_validate_graph",
)
query_graph = load_module(
    "query_graph.py",
    "dev_context_multi_repo_query_graph",
)
export_graph_report = load_module(
    "export_graph_report.py",
    "dev_context_multi_repo_export_graph_report",
)
scan_portfolio = load_module(
    "scan_portfolio.py",
    "dev_context_multi_repo_scan_portfolio",
)


def write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def run_git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip()


def init_git_repo(repo: Path) -> str:
    repo.mkdir(parents=True, exist_ok=True)
    run_git(repo, "init")
    run_git(repo, "config", "user.name", "Codex")
    run_git(repo, "config", "user.email", "codex@example.com")
    (repo / "README.md").write_text("hello\n", encoding="utf-8")
    run_git(repo, "add", "README.md")
    run_git(repo, "commit", "-m", "initial")
    return run_git(repo, "rev-parse", "HEAD")


class BuildKnowledgeGraphRegressionTests(unittest.TestCase):
    def test_parse_api_catalog_collapses_duplicate_routes_and_preserves_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            hub_dir = Path(tmp_dir)
            api_catalog_path = hub_dir / "overview" / "api-catalog.json"
            write_json(
                api_catalog_path,
                {
                    "domains": [
                        {
                            "name": "Payments",
                            "key": "payments",
                            "services": [
                                {
                                    "repo": "payments-api",
                                    "title": "Payments API",
                                    "endpoints": [
                                        {
                                            "method": "post",
                                            "path": "/payments",
                                            "type": "public",
                                            "purpose": "Create payment",
                                            "auth": "customer",
                                        },
                                        {
                                            "method": "POST",
                                            "path": "/payments",
                                            "type": "private",
                                            "purpose": "Back-office replay",
                                            "timeout_ms": 30,
                                        },
                                    ],
                                }
                            ],
                        }
                    ]
                },
            )

            graph_builder = build_knowledge_graph.GraphBuilder()
            build_knowledge_graph.parse_api_catalog(hub_dir, graph_builder)
            graph = graph_builder.to_dict("test-portfolio", "hub")

            endpoint_nodes = [node for node in graph["nodes"] if node.get("type") == "api_endpoint"]
            self.assertEqual(len(endpoint_nodes), 1)

            endpoint_props = endpoint_nodes[0].get("properties", {})
            self.assertEqual(endpoint_props.get("endpoint_interfaces"), ["public", "private"])
            self.assertEqual(endpoint_props.get("purposes"), ["Create payment", "Back-office replay"])
            self.assertEqual(endpoint_props.get("purpose"), "Create payment / Back-office replay")
            self.assertEqual(endpoint_props.get("auth"), "customer")
            self.assertEqual(endpoint_props.get("timeout_ms"), 30)

            exposes_edges = [edge for edge in graph["edges"] if edge.get("relation") == "exposes"]
            self.assertEqual(len(exposes_edges), 1)

            counts = check_graph_consistency.count_api_catalog_json(api_catalog_path)
            self.assertEqual(counts["domains"], 1)
            self.assertEqual(counts["services"], 1)
            self.assertEqual(counts["endpoint_rows"], 2)
            self.assertEqual(counts["unique_endpoints"], 1)
            self.assertEqual(counts["duplicate_endpoint_rows"], 1)

    def test_overview_documents_do_not_require_outgoing_document_edges(self) -> None:
        overview_artifact_id = check_graph_consistency.artifact_node_id("overview/README.md")
        api_artifact_id = check_graph_consistency.artifact_node_id("overview/api-catalog.json")

        node_index = {
            overview_artifact_id: {
                "id": overview_artifact_id,
                "type": "artifact",
                "label": "README.md",
                "properties": {
                    "artifact_kind": "overview-document",
                    "path": "overview/README.md",
                },
            },
            api_artifact_id: {
                "id": api_artifact_id,
                "type": "artifact",
                "label": "api-catalog.json",
                "properties": {
                    "artifact_kind": "api-catalog",
                    "path": "overview/api-catalog.json",
                },
            },
        }

        missing = check_graph_consistency.artifact_paths_without_documents(
            node_index=node_index,
            documented_targets={},
            edges=[],
        )

        self.assertEqual(missing, ["overview/api-catalog.json"])


class ArtifactLayoutRegressionTests(unittest.TestCase):
    def test_scan_portfolio_resolves_profiles_beneath_artifact_root(self) -> None:
        out_dir = scan_portfolio.resolve_profiles_out(None, "/tmp/portfolio/docs/context")
        self.assertEqual(out_dir, Path("/tmp/portfolio/docs/context/profiles"))

    def test_build_hub_views_defaults_to_sibling_catalog_directory(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            profiles_dir = root / "docs" / "context" / "profiles"
            write_json(
                profiles_dir / "sample-repo.json",
                {
                    "repo_name": "sample-repo",
                    "status": "active",
                    "repo_kind": "library",
                    "languages": ["TypeScript"],
                    "frameworks": ["React"],
                    "architecture_style": "unknown",
                    "confidence_score": 0.55,
                    "summary": "Sample repo summary.",
                    "interfaces_exposed": ["REST"],
                    "integrates_with": ["Stripe"],
                    "risk_flags": ["missing-ci-signals"],
                    "evidence": [{"path": "package.json", "reason": "high-signal manifest"}],
                },
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "build_hub_views.py"),
                    str(profiles_dir),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

            catalog_path = root / "docs" / "context" / "catalog" / "sample-repo.md"
            self.assertTrue(catalog_path.exists())
            self.assertIn("Sample repo summary.", catalog_path.read_text(encoding="utf-8"))

    def test_build_artifact_set_writes_standard_subfolders_beneath_artifact_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repo_root = root / "estate"
            repo = repo_root / "sample-app"
            init_git_repo(repo)
            write_json(
                repo / "package.json",
                {
                    "name": "sample-app",
                    "dependencies": {"react": "^19.0.0", "next": "^16.0.0"},
                },
            )

            artifact_root = root / "docs" / "context"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "build_artifact_set.py"),
                    "--artifact-root",
                    str(artifact_root),
                    str(repo_root),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            summary = json.loads(result.stdout)

            self.assertEqual(summary["artifact_root"], str(artifact_root.resolve()))
            self.assertTrue((artifact_root / "profiles" / "sample-app.json").exists())
            self.assertTrue((artifact_root / "catalog" / "sample-app.md").exists())
            self.assertTrue((artifact_root / "graphs" / "knowledge-graph.json").exists())
            self.assertTrue((artifact_root / "reports" / "graph-validation.json").exists())
            self.assertTrue((artifact_root / "reports" / "graph-report.md").exists())
            self.assertTrue((artifact_root / "reports" / "drift.json").exists())


class IncrementalUpdateRegressionTests(unittest.TestCase):
    def test_bootstrap_seeds_base_commit_shas_without_staling_existing_nodes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            repo_dir = root / "repo"
            head_sha = init_git_repo(repo_dir)

            graph_path = root / "knowledge-graph.json"
            output_path = root / "knowledge-graph.updated.json"
            write_json(
                graph_path,
                {
                    "meta": {
                        "generated_at": "2026-03-21T00:00:00+00:00",
                        "node_count": 2,
                        "edge_count": 1,
                    },
                    "nodes": [
                        {"id": "sample-repo", "type": "repo", "label": "Sample Repo"},
                        {
                            "id": "sample-repo#GET#/health",
                            "type": "api_endpoint",
                            "label": "GET /health",
                            "parent_id": "sample-repo",
                        },
                    ],
                    "edges": [
                        {
                            "source": "sample-repo",
                            "target": "sample-repo#GET#/health",
                            "relation": "exposes",
                            "group": "structural",
                        }
                    ],
                },
            )

            summary = incremental_update.incremental_update(
                graph_path=str(graph_path),
                repo_map={"sample-repo": str(repo_dir)},
                output_path=str(output_path),
            )

            self.assertEqual(summary["repos_checked"], 1)
            self.assertEqual(summary["repos_bootstrapped"], ["sample-repo"])
            self.assertEqual(summary["repos_changed"], [])
            self.assertEqual(summary["repos_unchanged"], [])
            self.assertEqual(summary["nodes_marked_stale"], 0)
            self.assertEqual(summary["nodes_removed"], 0)

            updated_graph = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_graph["meta"]["base_commit_shas"], {"sample-repo": head_sha})
            self.assertEqual(len(updated_graph["nodes"]), 2)
            self.assertFalse(any(node.get("stale") for node in updated_graph["nodes"]))

    def test_invalid_git_paths_are_reported_separately(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            invalid_repo_dir = root / "not-a-git-repo"
            invalid_repo_dir.mkdir(parents=True, exist_ok=True)

            graph_path = root / "knowledge-graph.json"
            output_path = root / "knowledge-graph.updated.json"
            write_json(
                graph_path,
                {
                    "meta": {
                        "generated_at": "2026-03-21T00:00:00+00:00",
                        "node_count": 1,
                        "edge_count": 0,
                    },
                    "nodes": [
                        {"id": "sample-repo", "type": "repo", "label": "Sample Repo"},
                    ],
                    "edges": [],
                },
            )

            summary = incremental_update.incremental_update(
                graph_path=str(graph_path),
                repo_map={"sample-repo": str(invalid_repo_dir)},
                output_path=str(output_path),
            )

            self.assertEqual(summary["repos_checked"], 1)
            self.assertEqual(summary["repos_invalid_git"], ["sample-repo"])
            self.assertEqual(summary["repos_not_found"], [])
            self.assertEqual(summary["repos_bootstrapped"], [])
            self.assertEqual(summary["repos_changed"], [])
            self.assertEqual(summary["nodes_marked_stale"], 0)
            self.assertEqual(summary["nodes_removed"], 0)

            updated_graph = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(updated_graph["meta"]["base_commit_shas"], {})
            self.assertFalse(any(node.get("stale") for node in updated_graph["nodes"]))

    def test_portable_repo_map_resolves_named_roots_relative_to_repo_map(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            graph_dir = root / "estate" / "requirements-hub" / "graphs"
            graph_dir.mkdir(parents=True, exist_ok=True)
            main_repo = root / "estate" / "sample-main"
            qa_repo = root / "estate-qa" / "sample-qa"
            legacy_repo = root / "legacy-estate" / "backend"
            init_git_repo(main_repo)
            init_git_repo(qa_repo)
            init_git_repo(legacy_repo)

            repo_map_path = graph_dir / "repos.json"
            write_json(
                repo_map_path,
                {
                    "roots": {
                        "main": ["../.."],
                        "qa": ["../../../estate-qa"],
                        "legacy": ["../../../legacy-estate"],
                    },
                    "repos": {
                        "main-repo": {"root": "main", "path": "sample-main"},
                        "qa-repo": {"root": "qa", "path": "sample-qa"},
                        "legacy-repo": {"root": "legacy", "path": "backend"},
                    },
                },
            )

            resolved = incremental_update.load_repo_map(repo_map_path)

            self.assertEqual(resolved["main-repo"], str(main_repo.resolve()))
            self.assertEqual(resolved["qa-repo"], str(qa_repo.resolve()))
            self.assertEqual(resolved["legacy-repo"], str(legacy_repo.resolve()))

    def test_report_paths_are_relativized_for_output_files(self) -> None:
        summary = {
            "output_path": "/tmp/hub/graphs/knowledge-graph.json",
        }
        self.assertEqual(
            incremental_update.report_path_value(summary["output_path"], "/tmp/hub/reports/incremental-update.json"),
            "../graphs/knowledge-graph.json",
        )
        self.assertEqual(
            validate_graph.report_for_output(
                {"graph": "/tmp/hub/graphs/knowledge-graph.json"},
                "/tmp/hub/reports/graph-validation.json",
            )["graph"],
            "../graphs/knowledge-graph.json",
        )
        consistency_report = check_graph_consistency.report_for_output(
            {
                "hub": "/tmp/hub",
                "graph": "/tmp/hub/graphs/knowledge-graph.json",
                "facts": {"source_files_newer_than_graph": ["/tmp/hub/overview/README.md"]},
                "missing_last_verified": ["/tmp/hub/overview/platform-summary.md"],
            },
            "/tmp/hub/reports/consistency-report.json",
        )
        self.assertEqual(consistency_report["hub"], "..")
        self.assertEqual(consistency_report["graph"], "../graphs/knowledge-graph.json")
        self.assertEqual(consistency_report["facts"]["source_files_newer_than_graph"], ["../overview/README.md"])
        self.assertEqual(consistency_report["missing_last_verified"], ["../overview/platform-summary.md"])


class QueryGraphRegressionTests(unittest.TestCase):
    def test_render_output_supports_mermaid_grouping(self) -> None:
        result = {
            "nodes": [
                {"id": "payments-api", "type": "repo", "label": "Payments API", "domain": "payments"},
                {"id": "sumsub", "type": "provider", "label": "Sumsub"},
            ],
            "edges": [
                {
                    "source": "payments-api",
                    "target": "sumsub",
                    "relation": "uses_provider",
                    "group": "integration",
                }
            ],
        }

        rendered = query_graph.render_output(
            result,
            "mermaid",
            query_label="Provider map",
            mermaid_direction="TD",
            mermaid_group_by="type",
        )

        self.assertIn("flowchart TD", rendered)
        self.assertIn('subgraph group_repo["Type: repo"]', rendered)
        self.assertIn('subgraph group_provider["Type: provider"]', rendered)
        self.assertIn("payments_api -->|uses_provider| sumsub", rendered)
        self.assertIn("classDef type_repo", rendered)
        self.assertIn("classDef type_provider", rendered)

    def test_diagram_output_writes_mermaid_file_with_filters(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            graph_path = root / "knowledge-graph.json"
            output_path = root / "diagram.mmd"

            write_json(
                graph_path,
                {
                    "meta": {"generated_at": "2026-03-21T00:00:00+00:00"},
                    "nodes": [
                        {"id": "payments", "type": "domain", "label": "Payments"},
                        {"id": "payments-api", "type": "repo", "label": "Payments API", "domain": "payments"},
                        {"id": "sumsub", "type": "provider", "label": "Sumsub"},
                        {"id": "artifact-overview", "type": "artifact", "label": "Overview"},
                    ],
                    "edges": [
                        {"source": "payments", "target": "payments-api", "relation": "contains", "group": "structural"},
                        {"source": "payments-api", "target": "sumsub", "relation": "uses_provider", "group": "integration"},
                        {"source": "artifact-overview", "target": "payments-api", "relation": "documents", "group": "semantic"},
                    ],
                },
            )

            query_graph.cmd_diagram(
                graph_path=str(graph_path),
                include_types="domain,repo,provider",
                exclude_types="",
                include_relations="contains,uses_provider",
                exclude_relations="documents",
                diagram_limit=50,
                fmt="mermaid",
                output_path=str(output_path),
                mermaid_direction="LR",
                mermaid_group_by="domain",
            )

            rendered = output_path.read_text(encoding="utf-8")
            self.assertIn("flowchart LR", rendered)
            self.assertIn('subgraph group_payments["Domain: payments"]', rendered)
            self.assertIn("payments -->|contains| payments_api", rendered)
            self.assertIn("payments_api -->|uses_provider| sumsub", rendered)
            self.assertNotIn("documents", rendered)


class ExportGraphReportRegressionTests(unittest.TestCase):
    def test_export_graph_report_writes_html_and_markdown_with_discovered_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            graph_path = root / "graphs" / "knowledge-graph.json"
            reports_dir = root / "reports"

            write_json(
                graph_path,
                {
                    "meta": {
                        "generated_at": "2026-03-22T00:00:00+00:00",
                        "graph_contract_version": "1.1",
                        "build_source": "hub",
                        "base_commit_shas": {"payments-api": "abc123"},
                    },
                    "nodes": [
                        {"id": "payments", "type": "domain", "label": "Payments"},
                        {"id": "payments-api", "type": "repo", "label": "Payments API", "domain": "payments"},
                        {"id": "sumsub", "type": "provider", "label": "Sumsub"},
                        {"id": "kyc", "type": "process", "label": "KYC", "domain": "payments"},
                    ],
                    "edges": [
                        {"source": "payments", "target": "payments-api", "relation": "contains", "group": "structural", "weight": 1.0},
                        {"source": "payments-api", "target": "sumsub", "relation": "uses_provider", "group": "integration", "weight": 0.8},
                        {"source": "payments-api", "target": "kyc", "relation": "implements_process", "group": "business", "weight": 0.9},
                    ],
                },
            )
            write_json(
                reports_dir / "graph-validation.json",
                {
                    "graph": "../graphs/knowledge-graph.json",
                    "checks_passed": 8,
                    "checks_total": 8,
                    "results": [{"check": "schema_compliance", "passed": True}],
                },
            )
            write_json(
                reports_dir / "consistency-report.json",
                {
                    "hub": "..",
                    "graph": "../graphs/knowledge-graph.json",
                    "status": "ok",
                    "mismatches": [],
                },
            )
            write_json(
                reports_dir / "incremental-update.json",
                {
                    "repos_checked": 1,
                    "repos_changed": [],
                    "repos_unchanged": ["payments-api"],
                    "repos_bootstrapped": [],
                    "repos_not_found": [],
                    "repos_invalid_git": [],
                },
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "export_graph_report.py"),
                    str(graph_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)
            html_path = Path(output["html"])
            markdown_path = Path(output["markdown"])

            self.assertTrue(html_path.exists())
            self.assertTrue(markdown_path.exists())

            html_text = html_path.read_text(encoding="utf-8")
            markdown_text = markdown_path.read_text(encoding="utf-8")

            self.assertIn("Static report", html_text)
            self.assertIn("Payments API", html_text)
            self.assertIn("8/8 checks passed", html_text)
            self.assertIn("Platform Overview", html_text)
            self.assertIn("# Hub Graph Report", markdown_text)
            self.assertIn("## Diagram Exports", markdown_text)
            self.assertIn("```mermaid", markdown_text)
            self.assertIn("Repositories To Providers", markdown_text)

    def test_export_graph_report_handles_missing_optional_reports(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir)
            graph_path = root / "graphs" / "knowledge-graph.json"
            output_dir = root / "custom-reports"

            write_json(
                graph_path,
                {
                    "meta": {
                        "generated_at": "2026-03-22T00:00:00+00:00",
                    },
                    "nodes": [
                        {"id": "payments-api", "type": "repo", "label": "Payments API"},
                    ],
                    "edges": [],
                },
            )

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT_DIR / "export_graph_report.py"),
                    str(graph_path),
                    "--output-dir",
                    str(output_dir),
                    "--skip-diagrams",
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            output = json.loads(result.stdout)
            markdown_text = Path(output["markdown"]).read_text(encoding="utf-8")

            self.assertIn("Graph Validation", markdown_text)
            self.assertIn("missing", markdown_text)
            self.assertNotIn("## Diagram Exports", markdown_text)


if __name__ == "__main__":
    unittest.main()
