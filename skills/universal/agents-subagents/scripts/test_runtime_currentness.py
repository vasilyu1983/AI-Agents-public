#!/usr/bin/env python3
"""Regression checks for runtime claims that previously drifted silently."""

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL = Path(__file__).resolve().parents[1]
SWARM = SKILL.parent / "agents-swarm-orchestration"
# The agent catalog lives outside this skill, at <repo>/agents.
AGENTS_DIR = Path(__file__).resolve().parents[4] / "agents"


def read(relative: str) -> str:
    return (SKILL / relative).read_text(encoding="utf-8")


class RuntimeCurrentnessTests(unittest.TestCase):
    def test_universal_ladder_starts_small(self) -> None:
        text = read("SKILL.md")
        text = text.split("## Scenario Selection Rule", 1)[1].split("## Runtime Surfaces", 1)[0]
        positions = [
            text.index("**main thread**"),
            text.index("**built-in subagent**"),
            text.index("saved **Workflow**"),
            text.index("**shared team**"),
            text.index("**debate-enabled team**"),
        ]
        self.assertEqual(positions, sorted(positions))

    def test_removed_claude_foreground_pin_is_not_recommended(self) -> None:
        documents = "\n".join(
            [
                read("SKILL.md"),
                read("references/agent-tools.md"),
                read("references/runtime-surfaces.md"),
                read("references/skill-subagent-patterns.md"),
                (SWARM / "SKILL.md").read_text(encoding="utf-8"),
                (SWARM / "references/platform-patterns.md").read_text(encoding="utf-8"),
            ]
        )
        stale_assertions = [
            r"run_in_background:\s*false.{0,100}(?:block|foreground)",
            r"(?:pin|force).{0,80}foreground.{0,80}background:\s*false",
            r"chain(?:s| cap)?\s+(?:are\s+)?capped at 5",
        ]
        for pattern in stale_assertions:
            self.assertIsNone(re.search(pattern, documents, re.IGNORECASE | re.DOTALL))

    def test_codex_docs_do_not_depend_on_undocumented_surfaces(self) -> None:
        core_documents = "\n".join(
            [
                read("references/runtime-surfaces.md"),
                read("references/agent-tools.md"),
                read("references/runtime-smoke-tests.md"),
            ]
        )
        for stale in ("V1-path feature", "multi_agent_v2", "spawn_agents_on_csv"):
            self.assertNotIn(stale, core_documents)

        swarm_documents = "\n".join(
            [
                (SWARM / "SKILL.md").read_text(encoding="utf-8"),
                (SWARM / "references/platform-patterns.md").read_text(encoding="utf-8"),
            ]
        )
        self.assertNotIn("V1-path feature", swarm_documents)
        self.assertNotIn("multi_agent_v2", swarm_documents)
        if "spawn_agents_on_csv" in swarm_documents:
            self.assertIn("not guaranteed", swarm_documents)
            self.assertIn("capability-check", swarm_documents)

    def test_codex_clean_context_is_a_launch_choice(self) -> None:
        stale = "You inherit no conversation history"
        paths = sorted((AGENTS_DIR / "codex").glob("*.toml"))
        paths.append(AGENTS_DIR / "templates/member-codex.toml.template")
        offenders = [str(path.relative_to(AGENTS_DIR)) for path in paths if stale in path.read_text(encoding="utf-8")]
        self.assertEqual(offenders, [])

    def test_removed_claude_agents_editor_is_not_operational_guidance(self) -> None:
        lifecycle = read("references/team-lifecycle.md")
        self.assertNotRegex(lifecycle, r"run `/agents` to see")
        self.assertNotRegex(lifecycle, r"use `/agents` to refresh")


if __name__ == "__main__":
    unittest.main()
