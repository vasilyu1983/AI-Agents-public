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
