#!/usr/bin/env python3
"""The coverage audit must fail loud on bad arguments and a missing or malformed alias file."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent / "audit_team_coverage.py"


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False
    )


class AuditTeamCoverageCliTests(unittest.TestCase):
    def test_unknown_argument_exits_2_without_auditing(self) -> None:
        result = run("--bogus")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("team_count", result.stdout)

    def test_help_exits_0_without_auditing(self) -> None:
        result = run("--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("usage:", result.stdout)
        self.assertNotIn("team_count", result.stdout)

    def test_missing_alias_file_is_an_error_naming_the_path(self) -> None:
        missing = "/nonexistent/naming-aliases.json"
        result = run("--aliases", missing)
        self.assertEqual(result.returncode, 2)
        self.assertIn(missing, result.stderr)
        self.assertNotIn("team_count", result.stdout)

    def test_alias_file_without_members_or_teams_mapping_fails(self) -> None:
        # A typo such as "member" used to skip the collision checks and exit 0,
        # hiding the very alias collisions this audit exists to catch.
        payloads = {
            "typo": {"member": {"ai-agent-architect": "no-such-member"}, "teams": {}},
            "empty": {},
            "teams_missing": {"members": {}},
            "members_not_mapping": {"members": [], "teams": {}},
            "not_object": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            for label, payload in payloads.items():
                with self.subTest(label):
                    path = Path(tmp) / f"{label}.json"
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    result = run("--aliases", str(path))
                    self.assertEqual(result.returncode, 2)
                    self.assertIn("lacks 'members'/'teams' mapping", result.stderr)
                    self.assertNotIn("team_count", result.stdout)

    def test_alias_entries_must_be_non_empty_strings(self) -> None:
        # A list id raised a traceback and an empty name matched nothing; a bad
        # file must be named as one, not crash or pass as a missing id.
        payloads = {
            "list_id": {"members": {"old-name": ["a"]}, "teams": {}},
            "null_id": {"members": {}, "teams": {"old-team": None}},
            "empty_id": {"members": {"old-name": " "}, "teams": {}},
            "empty_alias": {"members": {"": "ai-agent-architect"}, "teams": {}},
            "padded_alias": {"members": {" agent-architect": "ai-agent-architect"}, "teams": {}},
            "trailing_space_alias": {"members": {"ai-agent-architect ": "ai-agent-architect"}, "teams": {}},
            "zero_width_alias": {"members": {"agent\u200barchitect": "ai-agent-architect"}, "teams": {}},
            "padded_id": {"members": {"agent-architect": " ai-agent-architect"}, "teams": {}},
        }
        with tempfile.TemporaryDirectory() as tmp:
            for label, payload in payloads.items():
                with self.subTest(label):
                    path = Path(tmp) / f"{label}.json"
                    path.write_text(json.dumps(payload), encoding="utf-8")
                    result = run("--aliases", str(path))
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("must be non-empty strings", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)

    def test_unreadable_or_ambiguous_alias_json_is_an_error(self) -> None:
        # Invalid JSON raised a traceback, and a duplicate key let the later value
        # win silently, hiding the entry a reviewer actually read.
        payloads = {
            "invalid": '{"members": {',
            "duplicate": '{"members": {"old": "ai-agent-architect", "old": "ai-agent-architect"}, "teams": {}}',
        }
        with tempfile.TemporaryDirectory() as tmp:
            for label, text in payloads.items():
                with self.subTest(label):
                    path = Path(tmp) / f"{label}.json"
                    path.write_text(text, encoding="utf-8")
                    result = run("--aliases", str(path))
                    self.assertEqual(result.returncode, 2, result.stderr)
                    self.assertIn("cannot read alias file", result.stderr)
                    self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
