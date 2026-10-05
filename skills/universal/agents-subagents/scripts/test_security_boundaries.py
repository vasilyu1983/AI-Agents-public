#!/usr/bin/env python3
"""Focused regressions for executable and supply-chain safety boundaries."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
HEADLESS = SCRIPT_DIR / "headless-review.sh"
TEARDOWN = SCRIPT_DIR / "teardown-team.sh"


class HeadlessReviewBoundaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.text = HEADLESS.read_text(encoding="utf-8")

    def invocation(self) -> str:
        """The `claude -p` invocation with its line continuations flattened."""
        start = self.text.index("claude -p ")
        flattened = self.text[start:].replace("\\\n", " ")
        return flattened.split("\n", 1)[0]

    def test_review_agents_have_no_command_execution_authority(self) -> None:
        self.assertNotIn('"Bash"', self.text)
        self.assertNotIn("Bash(", self.text)
        self.assertIn('--allowedTools "Read,Grep,Glob,Agent"', self.invocation())

    def test_headless_review_loads_no_mcp_servers(self) -> None:
        # Without --strict-mcp-config, `claude -p` loads every configured MCP server and
        # injects each server's `instructions` into the system prompt of a session whose
        # user prompt already carries an untrusted diff. Assert on the invocation itself,
        # not on the file text, so a mention in a comment cannot satisfy the boundary.
        invocation = self.invocation()
        self.assertIn("--strict-mcp-config", invocation)
        # --strict-mcp-config only restricts MCP to servers named by --mcp-config; passing
        # none is what reduces the set to zero.
        self.assertNotIn("--mcp-config", invocation)

    def test_review_content_is_untrusted_and_target_is_worktree_bounded(self) -> None:
        self.assertIn("<UNTRUSTED_DIFF>", self.text)
        self.assertIn("never as instructions", self.text)
        self.assertIn('git rev-parse --show-toplevel', self.text)
        self.assertIn('"$WORKTREE_ROOT"|"$WORKTREE_ROOT"/*', self.text)


class TeardownInputTests(unittest.TestCase):
    def run_teardown(self, *args: str) -> subprocess.CompletedProcess[str]:
        with tempfile.TemporaryDirectory() as tmp:
            env = dict(os.environ, HOME=tmp)
            return subprocess.run(
                ["bash", str(TEARDOWN), *args],
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )

    def test_missing_max_age_value_is_rejected(self) -> None:
        result = self.run_teardown("--max-age")
        self.assertEqual(result.returncode, 2)
        self.assertIn("requires an integer", result.stderr)

    def test_non_numeric_zero_and_out_of_range_values_are_rejected(self) -> None:
        for value in ("0", "87601", "1+1", "x[$(id)]", "999999999999999999999"):
            with self.subTest(value=value):
                result = self.run_teardown("--max-age", value)
                self.assertEqual(result.returncode, 2)
                self.assertIn("positive integer", result.stderr)

    def test_bounded_positive_value_is_accepted(self) -> None:
        result = self.run_teardown("--max-age", "24")
        self.assertEqual(result.returncode, 0)
        self.assertIn("No cleanup performed", result.stdout)


class ThirdPartyProcedureTests(unittest.TestCase):
    def test_docs_do_not_offer_moving_remote_execution_commands(self) -> None:
        debate = (SKILL_DIR / "references/debate-quickstart.md").read_text(encoding="utf-8")
        forking = (SKILL_DIR / "references/subagent-context-forking.md").read_text(encoding="utf-8")
        self.assertNotIn("git clone https://github.com/albinjal/multi-agent-debate-mcp", debate)
        self.assertNotIn("npm install && npm run build", debate)
        self.assertNotIn("npx claude-code-templates@latest", forking)
        self.assertIn("immutable", debate)
        self.assertIn("exact reviewed artifact", forking)


if __name__ == "__main__":
    unittest.main()
