#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock


HERE = Path(__file__).resolve().parent
VALIDATOR_PATH = HERE / "validate_catalog_integrity.py"

spec = importlib.util.spec_from_file_location("catalog_integrity", VALIDATOR_PATH)
assert spec and spec.loader
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def claude_member(*, leaf: bool) -> str:
    boundary = "disallowedTools:\n  - Agent\n" if leaf else ""
    return f"---\nname: fixture\n{boundary}skills:\n  - fixture-skill\n---\nBody\n"


def codex_member(body: str) -> str:
    return f'name = "fixture"\ndeveloper_instructions = """\n{body}\n"""\n'


CURRENT_FOOTER = (
    "Linked skills: fixture-skill. Declared for Codex; deploy-preset.sh materializes "
    "native `[[skills.config]]` entries at any scope and explicit model fields only "
    "when policy requires; standard-tier agents inherit configured Codex defaults."
)


class CodexCatalogContractTests(unittest.TestCase):
    def run_contract_check(
        self, *, claude_text: str, codex_instructions: str
    ) -> tuple[dict[str, object], list[str]]:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            claude = root / "claude"
            codex = root / "codex"
            claude.mkdir()
            codex.mkdir()
            (claude / "fixture.md").write_text(claude_text, encoding="utf-8")
            (codex / "fixture.toml").write_text(
                codex_member(codex_instructions), encoding="utf-8"
            )
            summary: dict[str, object] = {}
            errors: list[str] = []
            with (
                mock.patch.object(validator, "CLAUDE_MEMBERS", claude),
                mock.patch.object(validator, "CODEX_MEMBERS", codex),
            ):
                validator.check_codex_runtime_contracts(summary, errors)
        return summary, errors

    def test_accepts_current_footer_and_leaf_boundary(self) -> None:
        summary, errors = self.run_contract_check(
            claude_text=claude_member(leaf=True),
            codex_instructions=(
                "You are a leaf worker: do not delegate or spawn subagents; return findings.\n\n"
                + CURRENT_FOOTER
            ),
        )
        self.assertEqual(errors, [])
        self.assertEqual(summary["codex_leaf_member_count"], 1)

    def test_rejects_legacy_footer_and_missing_current_footer(self) -> None:
        summary, errors = self.run_contract_check(
            claude_text=claude_member(leaf=False),
            codex_instructions=(
                "Teammate note: Linked shared skills (fixture-skill) are declared for Codex."
            ),
        )
        self.assertEqual(summary["codex_members_with_legacy_footer"], ["fixture"])
        self.assertEqual(summary["codex_members_missing_current_footer"], ["fixture"])
        self.assertTrue(any("legacy footer" in error for error in errors))

    def test_rejects_claude_only_tools_and_missing_leaf_boundary(self) -> None:
        summary, errors = self.run_contract_check(
            claude_text=claude_member(leaf=True),
            codex_instructions=f"Use WebSearch and WebFetch.\n\n{CURRENT_FOOTER}",
        )
        self.assertEqual(
            summary["codex_forbidden_claude_tool_identifiers"],
            ["fixture: WebFetch", "fixture: WebSearch"],
        )
        self.assertEqual(
            summary["codex_leaf_members_missing_no_delegation_boundary"],
            ["fixture"],
        )
        self.assertTrue(any("Claude-only tool" in error for error in errors))
        self.assertTrue(any("no-delegation boundary" in error for error in errors))

    def test_non_leaf_is_exempt_from_boundary(self) -> None:
        summary, errors = self.run_contract_check(
            claude_text=claude_member(leaf=False),
            codex_instructions=CURRENT_FOOTER,
        )
        self.assertEqual(errors, [])
        self.assertEqual(
            summary["codex_leaf_members_missing_no_delegation_boundary"], []
        )


class CatalogCountTextTests(unittest.TestCase):
    def test_accepts_current_semantic_catalog_counts(self) -> None:
        text = (
            "141 Claude members; 141 Codex members; 24 installable team recipes; "
            "20 debate-enabled teams; 12 of 141 members have steering examples."
        )
        self.assertEqual(
            validator.find_catalog_count_mismatches(
                text, members=141, teams=24, debate_teams=20
            ),
            [],
        )

    def test_rejects_any_stale_catalog_count_not_only_historical_values(self) -> None:
        text = "33 Team Recipes (27 debate-enabled); all 140 canonical members"
        mismatches = validator.find_catalog_count_mismatches(
            text, members=141, teams=24, debate_teams=20
        )
        self.assertEqual(
            mismatches,
            [
                "canonical_members: found 140, expected 141",
                "team_recipes: found 33, expected 24",
                "debate_enabled_teams: found 27, expected 20",
            ],
        )


class ReferenceStampFreshnessTests(unittest.TestCase):
    """The freshness gate compares last_verified against the file's last commit."""

    def _run(self, files: dict[str, str], commit_dates: dict[str, str], strict: bool):
        summary: dict[str, object] = {}
        errors: list[str] = []
        warnings: list[str] = []
        with tempfile.TemporaryDirectory() as tmp:
            refs = Path(tmp) / "references"
            refs.mkdir()
            for name, text in files.items():
                target = refs / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(text, encoding="utf-8")
            with mock.patch.object(validator, "ROOT", Path(tmp)), mock.patch.object(
                validator, "REFERENCES_DIR", refs
            ), mock.patch.object(
                validator,
                "_git_last_commit_date",
                lambda path: commit_dates.get(path.name),
            ):
                validator.check_reference_stamp_freshness(
                    summary, errors, warnings, strict=strict
                )
        return summary, errors, warnings

    @staticmethod
    def _doc(stamp: str | None) -> str:
        if stamp is None:
            return "# No frontmatter\n"
        return f"---\ndescription: fixture\nlast_verified: {stamp}\nstatus: stable\n---\n\n# Fixture\n"

    def test_stamp_older_than_last_commit_is_advisory_by_default(self) -> None:
        summary, errors, warnings = self._run(
            {"stale.md": self._doc("2026-04-23")},
            {"stale.md": "2026-08-29"},
            strict=False,
        )
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)
        self.assertIn("STALE STAMP references/stale.md", warnings[0])
        self.assertEqual(
            summary["reference_stamp_stale"],
            [
                {
                    "file": "references/stale.md",
                    "last_verified": "2026-04-23",
                    "last_commit": "2026-08-29",
                }
            ],
        )

    def test_stamp_older_than_last_commit_blocks_under_strict_freshness(self) -> None:
        _, errors, warnings = self._run(
            {"stale.md": self._doc("2026-04-23")},
            {"stale.md": "2026-08-29"},
            strict=True,
        )
        self.assertEqual(warnings, [])
        self.assertEqual(len(errors), 1)
        self.assertIn("predates last commit 2026-08-29", errors[0])

    def test_stamp_on_or_after_last_commit_is_clean(self) -> None:
        summary, errors, warnings = self._run(
            {
                "same.md": self._doc("2026-09-02"),
                "newer.md": self._doc("2026-09-02"),
            },
            {"same.md": "2026-09-02", "newer.md": "2026-08-01"},
            strict=True,
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(summary["reference_stamp_stale"], [])

    def test_uncommitted_file_is_not_stale(self) -> None:
        # No git history -> _git_last_commit_date returns None -> nothing to compare.
        summary, errors, warnings = self._run(
            {"brand-new.md": self._doc("2026-01-01")}, {}, strict=True
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(summary["reference_stamp_stale"], [])

    def test_missing_stamp_is_reported_separately_and_never_fails(self) -> None:
        summary, errors, warnings = self._run(
            {"nofm.md": self._doc(None)}, {"nofm.md": "2026-08-29"}, strict=True
        )
        self.assertEqual(errors, [])
        self.assertEqual(warnings, [])
        self.assertEqual(summary["reference_stamp_unstamped"], ["references/nofm.md"])

    def test_nested_references_are_walked(self) -> None:
        summary, _, warnings = self._run(
            {"sub/nested.md": self._doc("2026-04-23")},
            {"nested.md": "2026-08-29"},
            strict=False,
        )
        self.assertEqual(len(warnings), 1)
        self.assertEqual(
            summary["reference_stamp_stale"][0]["file"], "references/sub/nested.md"
        )

    def test_git_last_commit_date_returns_none_outside_a_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "orphan.md"
            target.write_text("x", encoding="utf-8")
            self.assertIsNone(validator._git_last_commit_date(target))

    def test_git_last_commit_date_reads_a_real_commit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            env = {
                "GIT_AUTHOR_NAME": "t",
                "GIT_AUTHOR_EMAIL": "t@example.com",
                "GIT_COMMITTER_NAME": "t",
                "GIT_COMMITTER_EMAIL": "t@example.com",
                "GIT_COMMITTER_DATE": "2026-08-29T00:00:00 +0000",
                "GIT_AUTHOR_DATE": "2026-08-29T00:00:00 +0000",
                "PATH": "/usr/bin:/bin:/usr/local/bin",
                "HOME": tmp,
            }
            target = root / "committed.md"
            target.write_text("x", encoding="utf-8")
            subprocess.run(["git", "init", "-q"], cwd=root, env=env, check=True)
            subprocess.run(["git", "add", "committed.md"], cwd=root, env=env, check=True)
            subprocess.run(["git", "commit", "-qm", "x"], cwd=root, env=env, check=True)
            self.assertEqual(validator._git_last_commit_date(target), "2026-08-29")


class GeneratedWorkflowAssetTests(unittest.TestCase):
    """check_generated_workflow_assets iterates every manifest, not a fixed list."""

    def check(self, mutate) -> list[str]:
        with tempfile.TemporaryDirectory() as tmp:
            workflows = Path(tmp)
            for suffix in (".manifest.json", ".js", ".codex-plan.json"):
                source = validator.WORKFLOWS_DIR / f"adversarial-review{suffix}"
                (workflows / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
            mutate(workflows)
            summary: dict[str, object] = {}
            errors: list[str] = []
            with mock.patch.object(validator, "WORKFLOWS_DIR", workflows):
                validator.check_generated_workflow_assets(summary, errors)
        return errors

    def test_current_copy_is_clean(self) -> None:
        self.assertEqual(self.check(lambda _: None), [])

    def test_stale_output_fails(self) -> None:
        def stale(workflows: Path) -> None:
            with (workflows / "adversarial-review.js").open("a", encoding="utf-8") as handle:
                handle.write("// hand edit\n")
        self.assertEqual(len(self.check(stale)), 1)
        self.assertIn("stale generated workflow asset", self.check(stale)[0])

    def test_unknown_engine_fails(self) -> None:
        def bad_engine(workflows: Path) -> None:
            manifest = workflows / "adversarial-review.manifest.json"
            manifest.write_text(manifest.read_text(encoding="utf-8").replace('"engine": "review"', '"engine": "nope"', 1), encoding="utf-8")
        errors = self.check(bad_engine)
        self.assertEqual(len(errors), 1)
        self.assertIn("unknown workflow.engine 'nope'", errors[0])

    def test_staged_workflow_needs_the_loop_it_extends(self) -> None:
        """feature-delivery imports review-fix-loop at generation time; without that base it fails loud."""
        chain = ("adversarial-review", "review-fix-loop", "feature-delivery")

        def copy_chain(workflows: Path) -> None:
            for wid in chain:
                for suffix in (".manifest.json", ".js", ".codex-plan.json"):
                    source = validator.WORKFLOWS_DIR / f"{wid}{suffix}"
                    (workflows / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")

        self.assertEqual(self.check(copy_chain), [])

        def drop_base(workflows: Path) -> None:
            copy_chain(workflows)
            (workflows / "review-fix-loop.manifest.json").unlink()

        errors = self.check(drop_base)
        self.assertEqual(len(errors), 1)
        self.assertIn("cannot generate workflow from feature-delivery.manifest.json", errors[0])


if __name__ == "__main__":
    unittest.main()
