#!/usr/bin/env python3

from __future__ import annotations

import gc
import socket
import subprocess
import sys
import tempfile
import unittest
import warnings
from datetime import date
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "validate_skill.py"
# Fixtures live outside the skills/ tree so the Claude Code skill loader
# does not try to register the intentionally-malformed SKILL.md files.


def _deny_network(*args: object, **kwargs: object) -> None:
    raise OSError("test suite must not reach the network; mock urlopen instead")


def setUpModule() -> None:
    # Keep the suite hermetic: any in-process attempt to open a socket fails loudly.
    socket.socket.connect = _deny_network  # type: ignore[method-assign]
    socket.create_connection = _deny_network  # type: ignore[assignment]


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

    def test_misspelled_extension_field_warns(self) -> None:
        # `when-to-use` (hyphens) is silently ignored by the runtime; the skill
        # then loses its trigger text with no error. The validator must say so.
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "typo-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: typo-skill
description: Creates a skill with a misspelled field for validator coverage. Use when testing typo warnings.
when-to-use: Use when the field name is misspelled.
disable_model_invocation: true
---

# Typo Skill
""",
                encoding="utf-8",
            )

            result = self.run_validator_on_path(skill_dir)
            self.assertIn("`when-to-use` looks like a misspelling of `when_to_use`", result.stdout)
            self.assertIn(
                "`disable_model_invocation` looks like a misspelling of `disable-model-invocation`",
                result.stdout,
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
            self.assertNotIn("Fact-Checking", result.stdout)

    def test_skill_without_fact_checking_section_validates(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "no-fact-checking-skill"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_text(
                """---
name: no-fact-checking-skill
description: Creates a skill body with no Fact-Checking section. Use when confirming the section is optional.
---

# No Fact-Checking Skill

## Quick Reference

| Task | Action |
|------|--------|
| Do the work | Follow the workflow |

## Workflow

1. Do the work.

## Navigation

- No external references.
""",
                encoding="utf-8",
            )

            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertNotIn("Fact-Checking", result.stdout)

    def test_unknown_clean_code_rule_id_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp)
            catalog_dir = skills_root / "software-clean-code-standard" / "references"
            catalog_dir.mkdir(parents=True)
            (catalog_dir / "clean-code-standard.md").write_text(
                "| Rule | Text |\n|---|---|\n| CC-NAM-01 | Names reveal intent. |\n",
                encoding="utf-8",
            )
            skill_dir = skills_root / "cites-rules"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                """---
name: cites-rules
description: Cites clean-code rules for validator coverage. Use when testing rule ID checks.
---

# Cites Rules

Apply CC-NAM-01 and CC-SEC-001. Licensed CC-BY-4.0.
""",
                encoding="utf-8",
            )

            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("unknown clean-code rule IDs", result.stdout)
            self.assertIn("CC-SEC-001", result.stdout)
            self.assertNotIn("CC-NAM-01,", result.stdout)
            self.assertNotIn("CC-BY-4", result.stdout)

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
    "last_updated": "__TODAY__",
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
}""".replace("__TODAY__", date.today().isoformat()),  # a fixed date goes stale and trips the freshness warning
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

    def write_skill(self, tmp: str, name: str, frontmatter: str) -> Path:
        skill_dir = Path(tmp) / name
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(
            f"---\nname: {name}\n{frontmatter}---\n\n# {name}\n\n## Quick Reference\n\n## Workflow\n\n## Navigation\n",
            encoding="utf-8",
        )
        return skill_dir

    def test_folded_block_description_is_checked(self) -> None:
        # A `description: >-` block used to be skipped by the line parser, so
        # an over-long or first-person description passed with exit 0.
        with tempfile.TemporaryDirectory() as tmp:
            long_text = " ".join(["word"] * 260)  # about 1,300 chars
            skill_dir = self.write_skill(
                tmp,
                "folded-long",
                "description: >-\n  Use when the folded body is too long.\n  " + long_text + "\n",
            )
            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("`description` exceeds 1024 characters", result.stdout)
            self.assertIn("does not look third-person", result.stdout)
            self.assertNotIn("missing `description`", result.stdout)

    def test_literal_block_description_is_rejected_as_multiline(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.write_skill(
                tmp,
                "literal-desc",
                "description: |\n  Validates literal blocks.\n  Use when testing.\n",
            )
            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("`description` must be single-line YAML", result.stdout)

    def test_folded_block_description_within_limits_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.write_skill(
                tmp,
                "folded-ok",
                "description: >-\n  Validates folded descriptions.\n  Use when a description wraps over lines.\n",
            )
            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("Status: PASS", result.stdout)

    def test_background_and_disallowed_tools_are_claude_only_fields(self) -> None:
        # `background` (context: fork blocking) and `disallowed-tools` are
        # Claude Code-only fields; beside a portability claim they must error.
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = self.write_skill(
                tmp,
                "bg-skill",
                "description: Validates background handling. Use when testing field coverage.\n"
                "background: false\n"
                "disallowed-tools: AskUserQuestion\n"
                "compatibility: portable across all runtimes\n",
            )
            result = self.run_validator_on_path(skill_dir)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("alongside a portability claim", result.stdout)

    def test_url_check_retries_head_405_with_get(self) -> None:
        # Some hosts reject HEAD with 405 but serve GET; that is not a broken link.
        import io
        import urllib.error
        from unittest import mock

        sys.path.insert(0, str(SCRIPT_DIR))
        import validate_skill

        calls: list[str] = []
        raised: list[urllib.error.HTTPError] = []

        def fake_urlopen(request, timeout=10):
            calls.append(request.get_method())
            if request.get_method() == "HEAD":
                # HTTPError wraps a temporary file; keep a handle so the test can
                # close it instead of leaking a ResourceWarning at teardown.
                error = urllib.error.HTTPError(request.full_url, 405, "Method Not Allowed", {}, io.BytesIO())
                raised.append(error)
                raise error
            response = mock.MagicMock()
            response.status = 200
            response.__enter__.return_value = response
            return response

        issues: list[validate_skill.Issue] = []
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            with mock.patch.object(validate_skill.urllib.request, "urlopen", fake_urlopen):
                validate_skill.validate_url(Path("sources.json"), "docs", "https://example.com/x", issues)
            for error in raised:
                error.close()
            raised.clear()
            del error
            gc.collect()
        self.assertEqual(calls, ["HEAD", "GET"])
        self.assertEqual(issues, [])
        leaked = [str(w.message) for w in caught if issubclass(w.category, ResourceWarning)]
        self.assertEqual(leaked, [], "mocked HTTPError was not closed")


class LearningsAndSupportFileTests(unittest.TestCase):
    """Checks added in RULES-PHASE 4.4 rows 3-4. Fixtures are built in a temp dir."""

    def setUp(self) -> None:
        global validate_skill
        if str(SCRIPT_DIR) not in sys.path:
            sys.path.insert(0, str(SCRIPT_DIR))
        import validate_skill  # noqa: F811

    def make_skill(self, files: dict[str, str]) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name) / "demo-skill"
        base = {"SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n# Demo\n"}
        for name, text in {**base, **files}.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return root

    def messages(self, check, root: Path) -> list[str]:
        issues: list[validate_skill.Issue] = []
        check(root, issues)
        return [i.message for i in issues]

    def test_learnings_valid_file_passes(self) -> None:
        root = self.make_skill({"learnings.md": "# t\n\n## Patterns That Work\n- [2026-10-01] Keep it short.\n"})
        self.assertEqual(self.messages(validate_skill.validate_learnings, root), [])

    def test_learnings_bad_shape_fails(self) -> None:
        root = self.make_skill({"learnings.md": "- 2026-10-01: no brackets\n"})
        self.assertTrue(any("must start with" in m for m in self.messages(validate_skill.validate_learnings, root)))

    def test_learnings_secret_fails(self) -> None:
        root = self.make_skill({"learnings.md": "- [2026-10-01] Key was " + "sk-ant-" + "abcdefghij1234567890 in the log.\n"})
        self.assertTrue(any("secret or personal data" in m for m in self.messages(validate_skill.validate_learnings, root)))

    def test_learnings_already_redacted_entry_passes(self) -> None:
        root = self.make_skill({"learnings.md": "- [2026-10-01] Path was /Users/[REDACTED-USER]/x.\n"})
        self.assertEqual(self.messages(validate_skill.validate_learnings, root), [])

    def test_learnings_cap_fails_over_150(self) -> None:
        text = "".join(f"- [2026-10-01] Entry {i}.\n" for i in range(151))
        root = self.make_skill({"learnings.md": text})
        self.assertTrue(any("raw cap of 150" in m for m in self.messages(validate_skill.validate_learnings, root)))

    def test_learnings_cap_passes_at_150(self) -> None:
        text = "".join(f"- [2026-10-01] Entry {i}.\n" for i in range(150))
        root = self.make_skill({"learnings.md": text})
        self.assertEqual(self.messages(validate_skill.validate_learnings, root), [])

    def test_support_file_linked_passes(self) -> None:
        root = self.make_skill({
            "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\nSee [a](references/a.md) and [t](assets/t.txt).\n",
            "references/a.md": "# A\n",
            "assets/t.txt": "x\n",
        })
        self.assertEqual(self.messages(validate_skill.validate_support_files, root), [])

    def test_backticked_link_text_counts_as_link(self) -> None:
        # Inline code is stripped before link matching; the link must survive it.
        root = self.make_skill({
            "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\nSee [`references/a.md`](references/a.md).\n",
            "references/a.md": "# A\n",
        })
        self.assertEqual(self.messages(validate_skill.validate_support_files, root), [])

    def test_backticked_broken_link_is_reported(self) -> None:
        root = self.make_skill({
            "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\nSee [`gone.md`](references/gone.md).\n",
        })
        found = self.messages(validate_skill.validate_links, root)
        self.assertTrue(any("broken local link: references/gone.md" in m for m in found), found)

    def test_support_file_unlinked_fails(self) -> None:
        root = self.make_skill({"references/orphan.md": "# O\n", "templates/t.md": "# T\n"})
        found = self.messages(validate_skill.validate_support_files, root)
        self.assertEqual(sum("not linked from SKILL.md" in m for m in found), 2)

    def test_reference_linking_a_hub_linked_reference_passes(self) -> None:
        # b.md is one hop from SKILL.md, so a cross-link from a.md adds no depth.
        root = self.make_skill({
            "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n[a](references/a.md) [b](references/b.md)\n",
            "references/a.md": "See [b](b.md#part).\n",
            "references/b.md": "# B\n",
        })
        self.assertEqual(self.messages(validate_skill.validate_support_files, root), [])

    def test_reference_reachable_only_through_a_reference_fails(self) -> None:
        root = self.make_skill({
            "SKILL.md": "---\nname: demo-skill\ndescription: Demo.\n---\n[a](references/a.md)\n",
            "references/a.md": "See [b](b.md).\n",
            "references/b.md": "# B\n",
        })
        found = self.messages(validate_skill.validate_support_files, root)
        self.assertIn("reference links to a reference that SKILL.md does not link: b.md", found)

    def test_issues_reach_validate_skill_dir(self) -> None:
        root = self.make_skill({"references/orphan.md": "# O\n"})
        issues = validate_skill.validate_skill_dir(root)
        self.assertTrue(any("not linked from SKILL.md" in i.message for i in issues))

    def test_shipped_skill_runs_with_defaults(self) -> None:
        # No overrides: the real feedback-loop skill, real writer import.
        skill = SCRIPT_DIR.parents[1] / "agents-skills-feedback-loop"
        self.assertIsNotNone(validate_skill.load_learning_writer())
        issues = validate_skill.validate_skill_dir(skill)
        new = [i for i in issues if "linked from SKILL.md" in i.message or "learnings" in i.message]
        self.assertEqual([i.message for i in new], [])


if __name__ == "__main__":
    unittest.main()
