#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
AUDITOR = SCRIPT_DIR / "audit_skill_metadata.py"


def write_skill(root: Path, name: str, description: str, short_description: str, default_prompt: str) -> None:
    skill_dir = root / name
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        f"""---
name: {name}
description: "{description}"
---

# {name}

## Quick Reference

| Task | Action |
|------|--------|
| Audit metadata | Run the metadata auditor |

## Workflow

1. Audit the skill.

## Navigation

- `agents/openai.yaml`

## Fact-Checking

- Reconfirm local metadata before trust.
""",
        encoding="utf-8",
    )
    (skill_dir / "agents").mkdir(parents=True)
    (skill_dir / "agents" / "openai.yaml").write_text(
        f"""interface:
  display_name: "{name}"
  short_description: "{short_description}"
  default_prompt: "{default_prompt}"
""",
        encoding="utf-8",
    )


def write_compact_discovery(root: Path, text: str | None = None) -> None:
    graph_dir = root.parent / "graph"
    graph_dir.mkdir(parents=True, exist_ok=True)
    (graph_dir / "codex-discovery.md").write_text(
        text or "# Codex Skill Discovery\n\nGenerated compact discovery map for Codex.\n",
        encoding="utf-8",
    )


def write_large_valid_catalog(root: Path, count: int = 100) -> None:
    for index in range(count):
        name = f"fixture-{index:03d}"
        prefix = (
            f"Audits repository metadata fixture {index}. Use when testing local inventory "
            "thresholds and runtime evidence. "
        )
        description = prefix + ("z" * (170 - len(prefix)))
        write_skill(
            root,
            name,
            description,
            "Repository metadata audit",
            f"Use ${name} when testing repository metadata inventory thresholds and runtime evidence.",
        )


class AuditSkillMetadataTests(unittest.TestCase):
    def run_auditor(self, root: Path, *extra_args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(AUDITOR), str(root), *extra_args],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_json_output_reports_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "sample-skill",
                "Creates a deliberately long metadata description for testing. Use for metadata audit coverage only.",
                "Unrelated UI label",
                "Load the tool with no skill token.",
            )

            result = self.run_auditor(root, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["summary"]["skills"], 1)
            warnings = payload["results"][0]["warnings"]
            self.assertIn("description missing `Use when` trigger clause", warnings)
            self.assertIn("default_prompt missing `$skill-name` invocation token", warnings)

    def test_json_output_flags_template_splice_default_prompt(self) -> None:
        splice_warning = (
            'default_prompt reads as a template splice ("for <Verb>s ..."); '
            'rewrite as "Use $name to <verb> ..." or "... when ..."'
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "spliced-skill",
                "Builds spliced fixtures for metadata output. Use when testing template splice detection.",
                "Spliced fixture",
                "Use $spliced-skill for Builds spliced fixtures for metadata output. Use when testing template splice detection.",
            )
            write_skill(
                root,
                "clean-skill",
                "Builds clean fixtures for metadata output. Use when testing template splice detection.",
                "Clean fixture",
                "Use $clean-skill to build clean fixtures for metadata output. Use when testing template splice detection.",
            )

            result = self.run_auditor(root, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            by_skill = {entry["skill"]: entry["warnings"] for entry in payload["results"]}
            self.assertIn(splice_warning, by_skill["spliced-skill"])
            self.assertNotIn(splice_warning, by_skill["clean-skill"])

    def test_json_output_flags_truncated_short_description(self) -> None:
        truncation_warning = (
            "short_description is a hard prefix of the SKILL.md description cut "
            "mid-sentence; write a complete <=80-char sentence"
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "truncated-skill",
                "Builds truncated fixtures for metadata output. Use when testing truncation detection.",
                "Builds truncated fixtures for metadata",
                "Use $truncated-skill when testing truncation detection of metadata fixtures.",
            )
            write_skill(
                root,
                "sentence-skill",
                "Builds sentence fixtures for metadata output. Use when testing truncation detection.",
                "Builds sentence fixtures for metadata output.",
                "Use $sentence-skill when testing truncation detection of metadata fixtures.",
            )
            write_skill(
                root,
                "distinct-skill",
                "Builds distinct fixtures for metadata output. Use when testing truncation detection.",
                "Distinct metadata fixture builder",
                "Use $distinct-skill when testing truncation detection of metadata fixtures.",
            )

            result = self.run_auditor(root, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            by_skill = {entry["skill"]: entry["warnings"] for entry in payload["results"]}
            self.assertIn(truncation_warning, by_skill["truncated-skill"])
            self.assertNotIn(truncation_warning, by_skill["sentence-skill"])
            self.assertNotIn(truncation_warning, by_skill["distinct-skill"])

    def test_strict_mode_fails_on_warnings(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            write_compact_discovery(root)
            write_skill(
                root,
                "good-skill",
                "Builds durable APIs for audit coverage. Use when testing metadata thresholds.",
                "Durable API audit",
                "Use $good-skill when auditing durable APIs and metadata coverage.",
            )

            result = self.run_auditor(root, "--strict")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Status: PASS", result.stdout)

            write_skill(
                root,
                "bad-skill",
                "Builds a metadata fixture that intentionally misses the required trigger clause for strict mode.",
                "Bad metadata fixture",
                "Audit this fixture without the invocation token.",
            )

            strict = self.run_auditor(root, "--strict")
            self.assertEqual(strict.returncode, 1, strict.stdout + strict.stderr)
            self.assertIn("bad-skill", strict.stdout)

    def test_strict_mode_rejects_oversized_or_non_generated_discovery(self) -> None:
        for discovery in (
            "Generated compact discovery map for Codex\n" + ("x" * 8001),
            "# Hand-written discovery\n",
        ):
            with self.subTest(size=len(discovery)):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "skills"
                    root.mkdir()
                    write_compact_discovery(root, discovery)
                    write_skill(
                        root,
                        "good-skill",
                        "Builds durable APIs for audit coverage. Use when testing metadata thresholds.",
                        "Durable API audit",
                        "Use $good-skill when auditing durable APIs and metadata coverage.",
                    )
                    result = self.run_auditor(root, "--strict")
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_compact_index_does_not_imply_runtime_mitigation(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            write_compact_discovery(root)
            write_large_valid_catalog(root)

            result = self.run_auditor(root, "--json", "--strict")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            inventory = payload["description_budget"]
            discovery = payload["compact_discovery"]

            self.assertEqual(inventory["inventory_level"], "critical")
            self.assertEqual(inventory["runtime_load_status"], "unknown")
            self.assertIsNone(inventory["runtime_load_evidence"])
            self.assertIn("repository-local", inventory["threshold_basis"])
            self.assertIsNone(inventory["codex_budget"])
            self.assertIsNone(inventory["claude_code_budget"])
            self.assertIsNone(inventory["legacy_anthropic_budget"])
            self.assertIsNone(inventory["fits_codex_default"])
            self.assertIn("intentionally null", inventory["legacy_field_semantics"])
            self.assertTrue(discovery["structurally_valid"])
            self.assertEqual(discovery["runtime_load_status"], "unknown")
            self.assertFalse(payload["strict_gate"]["runtime_loading_evaluated"])
            self.assertEqual(
                payload["strict_gate"]["scope"],
                "repository_metadata_and_compact_index_structure",
            )
            self.assertNotIn("mitigated", result.stdout.lower())

            markdown = self.run_auditor(root)
            self.assertEqual(markdown.returncode, 0, markdown.stdout + markdown.stderr)
            self.assertIn("Runtime loading evidence: UNKNOWN", markdown.stdout)
            self.assertIn("Runtime use: UNKNOWN", markdown.stdout)
            self.assertIn("runtime prompt loading not evaluated", markdown.stdout)
            self.assertNotIn("MITIGATED", markdown.stdout)

    def test_json_reports_unreadable_compact_discovery_without_crashing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            write_skill(
                root,
                "good-skill",
                "Builds durable APIs for audit coverage. Use when testing metadata thresholds.",
                "Durable API audit",
                "Use $good-skill when auditing durable APIs and metadata coverage.",
            )
            write_compact_discovery(root)
            discovery_path = root.parent / "graph" / "codex-discovery.md"
            discovery_path.write_bytes(b"\xff\xfe")

            result = self.run_auditor(root, "--json", "--strict")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            discovery = payload["compact_discovery"]
            self.assertEqual(discovery["structural_status"], "unreadable")
            self.assertFalse(discovery["structurally_valid"])
            self.assertEqual(discovery["runtime_load_status"], "unknown")
            self.assertIn("UnicodeDecodeError", discovery["read_error"])

    def test_runtime_discovery_report_does_not_claim_prompt_or_compact_index_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            write_compact_discovery(root)
            write_skill(
                root,
                "good-skill",
                "Builds durable APIs for audit coverage. Use when testing metadata thresholds.",
                "Durable API audit",
                "Use $good-skill when auditing durable APIs and metadata coverage.",
            )
            report = Path(tmp) / "runtime.json"
            report.write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "observed_at_utc": "2026-09-05T00:00:00+00:00",
                        "observation": "installed Codex app-server skills/list",
                        "codex_version": "codex-cli 0.153.4",
                        "model_visible_prompt_observed": False,
                        "caveat": "Discovery does not prove model prompt inclusion.",
                        "entries": [
                            {
                                "repository_skill_count": 1,
                                "repository_enabled_count": 1,
                                "missing_repository_skills": [],
                                "shadowed_repository_skills": [],
                                "errors": [],
                            }
                        ],
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_auditor(root, "--json", "--runtime-discovery-report", str(report))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            evidence = json.loads(result.stdout)["runtime_discovery"]
            self.assertEqual(evidence["status"], "observed")
            self.assertTrue(evidence["discovery_observed"])
            self.assertEqual(evidence["repository_enabled_count"], 1)
            self.assertEqual(evidence["model_prompt_inclusion_status"], "unknown")
            self.assertEqual(evidence["compact_index_use_status"], "unknown")

    def test_strict_mode_rejects_malformed_optional_runtime_report(self) -> None:
        reports = (
            "{not-json",
            json.dumps({"schema_version": 1, "entries": [{"errors": None}]}),
        )
        for report_text in reports:
            with self.subTest(report_text=report_text):
                with tempfile.TemporaryDirectory() as tmp:
                    root = Path(tmp) / "skills"
                    root.mkdir()
                    write_compact_discovery(root)
                    write_skill(
                        root,
                        "good-skill",
                        "Builds durable APIs for audit coverage. Use when testing metadata thresholds.",
                        "Durable API audit",
                        "Use $good-skill when auditing durable APIs and metadata coverage.",
                    )
                    report = Path(tmp) / "runtime.json"
                    report.write_text(report_text, encoding="utf-8")

                    result = self.run_auditor(
                        root,
                        "--json",
                        "--strict",
                        "--runtime-discovery-report",
                        str(report),
                    )
                    self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
                    payload = json.loads(result.stdout)
                    self.assertEqual(payload["runtime_discovery"]["status"], "invalid")
                    self.assertFalse(payload["strict_gate"]["passes"])

    def test_exact_compact_discovery_budget_boundary_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            prefix = "Generated compact discovery map for Codex\n"
            write_compact_discovery(root, prefix + ("x" * (8000 - len(prefix))))
            write_skill(
                root,
                "good-skill",
                "Builds durable APIs for audit coverage. Use when testing metadata thresholds.",
                "Durable API audit",
                "Use $good-skill when auditing durable APIs and metadata coverage.",
            )
            result = self.run_auditor(root, "--strict")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_strict_mode_fails_without_compact_discovery(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            root.mkdir()
            write_skill(
                root,
                "good-skill",
                "Builds durable APIs for audit coverage. Use when testing metadata thresholds.",
                "Durable API audit",
                "Use $good-skill when auditing durable APIs and metadata coverage.",
            )

            result = self.run_auditor(root, "--strict")
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("Exists: no", result.stdout)

    def test_json_output_lists_top_long_skills(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_skill(
                root,
                "long-skill",
                "Builds long fixtures for metadata output. Use when testing top long skill reporting.",
                "Long fixture",
                "Use $long-skill when testing top long skill reporting.",
            )
            write_skill(
                root,
                "short-skill",
                "Builds short fixtures for metadata output. Use when testing top long skill reporting.",
                "Short fixture",
                "Use $short-skill when testing top long skill reporting.",
            )
            skill_md = root / "long-skill" / "SKILL.md"
            skill_md.write_text(skill_md.read_text(encoding="utf-8") + ("\nextra detail\n" * 80), encoding="utf-8")

            result = self.run_auditor(root, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["top_long_skills"][0]["skill"], "long-skill")

    def test_json_output_reports_benchmark_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = tmp_path / "skills"
            root.mkdir()
            write_skill(
                root,
                "benchmarked-long-skill",
                "Builds benchmarked long fixtures for metadata output. Use when testing benchmark coverage.",
                "Benchmarked long fixture",
                "Use $benchmarked-long-skill when testing benchmark coverage.",
            )
            skill_md = root / "benchmarked-long-skill" / "SKILL.md"
            skill_md.write_text(skill_md.read_text(encoding="utf-8") + ("\nextra detail\n" * 260), encoding="utf-8")

            manifest_dir = tmp_path / "evals" / "tasks"
            manifest_dir.mkdir(parents=True)
            (manifest_dir / "pilot-router-and-long-skills.json").write_text(
                json.dumps(
                    {
                        "tasks": [
                            {
                                "id": "bench",
                                "curated_paths": ["skills/benchmarked-long-skill/SKILL.md"],
                                "expected_skills": ["benchmarked-long-skill"],
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )

            result = self.run_auditor(root, "--json")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["benchmark_coverage"]["long_skills_with_benchmark"], 1)
            self.assertTrue(payload["top_long_skills"][0]["has_benchmark_task"])


if __name__ == "__main__":
    unittest.main()
