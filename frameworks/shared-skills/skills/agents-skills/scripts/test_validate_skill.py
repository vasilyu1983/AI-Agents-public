#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "validate_skill.py"
# Malformed-SKILL.md fixture tests are not published: the fixtures they
# need are private-repo only. The tests below build their own temp skills.


class ValidateSkillTests(unittest.TestCase):
    def run_validator_on_path(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            check=False,
            capture_output=True,
            text=True,
        )

    def run_validator_on_path_with_urls(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(path), "--check-urls"],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_missing_canonical_sections_warns(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "minimal-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: minimal-skill
description: Creates a minimal skill body for validator coverage. Use when testing section warnings.
---

# Minimal Skill

## Workflow

1. Do the work.
""",
                encoding="utf-8",
            )

            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("missing canonical `Quick Reference` section", result.stdout)
            self.assertIn("missing canonical `Navigation` section", result.stdout)
            self.assertIn("missing canonical `Fact-Checking` section", result.stdout)

    def test_missing_sources_metadata_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "metadata-gap"
            (skill_dir / "data").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: metadata-gap
description: Creates a test skill for sources metadata validation. Use when validating sources metadata handling.
---

# Metadata Gap

## Quick Reference

| Task | Action |
|------|--------|
| Validate metadata | Check the sources file |

## Workflow

1. Open the sources file.

## Navigation

- `data/sources.json`

## Fact-Checking

- Reconfirm source metadata before trust.
""",
                encoding="utf-8",
            )
            (skill_dir / "data" / "sources.json").write_text(
                """{
  "metadata": {
    "last_updated": "2026-03-24"
  }
}""",
                encoding="utf-8",
            )

            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("missing `metadata.title`", result.stdout)
            self.assertIn("missing `metadata.description`", result.stdout)
            self.assertIn("missing `metadata.skill`", result.stdout)

    def test_manual_url_check_sources_are_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "manual-url-skill"
            (skill_dir / "data").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: manual-url-skill
description: Creates a test skill for manual URL validation. Use when checking bot-protected sources.
---

# Manual URL Skill

## Quick Reference

| Task | Action |
|------|--------|
| Validate URLs | Check manual skip handling |

## Workflow

1. Open the sources file.

## Navigation

- `data/sources.json`

## Fact-Checking

- Reconfirm manual sources in a browser or product UI.
""",
                encoding="utf-8",
            )
            (skill_dir / "data" / "sources.json").write_text(
                """{
  "metadata": {
    "title": "manual-url-skill sources",
    "description": "Fixture sources for manual URL validation.",
    "last_updated": "2026-03-24",
    "skill": "manual-url-skill"
  },
  "sources": [
    {
      "name": "Bot Protected Manual Source",
      "url": "https://example.invalid/manual",
      "type": "workflow",
      "url_check": "manual"
    }
  ]
}""",
                encoding="utf-8",
            )

            result = self.run_validator_on_path_with_urls(skill_dir)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Status: PASS", result.stdout)

    def test_invalid_url_check_value_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "bad-url-check"
            (skill_dir / "data").mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: bad-url-check
description: Creates a test skill for invalid URL validation metadata. Use when checking source schema.
---

# Bad URL Check

## Quick Reference

| Task | Action |
|------|--------|
| Validate URLs | Check schema |

## Workflow

1. Open the sources file.

## Navigation

- `data/sources.json`

## Fact-Checking

- Reconfirm source metadata.
""",
                encoding="utf-8",
            )
            (skill_dir / "data" / "sources.json").write_text(
                """{
  "metadata": {
    "title": "bad-url-check sources",
    "description": "Fixture sources for invalid URL validation metadata.",
    "last_updated": "2026-03-24",
    "skill": "bad-url-check"
  },
  "sources": [
    {
      "name": "Bad URL Check Source",
      "url": "https://example.com/",
      "type": "reference",
      "url_check": "sometimes"
    }
  ]
}""",
                encoding="utf-8",
            )

            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("invalid `url_check` value", result.stdout)


if __name__ == "__main__":
    unittest.main()
