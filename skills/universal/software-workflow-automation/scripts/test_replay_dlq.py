#!/usr/bin/env python3
"""Offline input/configuration regressions; never call a replay service."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).with_name("replay_dlq.py")


class ReplayTests(unittest.TestCase):
    def run_replay(self, messages, *args):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "messages.json"
            path.write_text(json.dumps(messages))
            return subprocess.run([sys.executable, str(SCRIPT), str(path), *args],
                                  capture_output=True, text=True)

    def test_unconfigured_execute_fails(self):
        result = self.run_replay([{"id": "one", "payload": {"order": "synthetic"}}], "--execute")
        self.assertEqual(result.returncode, 2)
        self.assertIn("Configure TARGET_COMMAND_TEMPLATE", result.stderr)
        self.assertNotIn("[OK]", result.stdout)

    def test_bad_messages_filters_and_limits_fail(self):
        for messages, args in (([None], ()), ([{"id": "one"}], ()),
                               ([{"payload": {}}], ("--filter", "[]")),
                               ([{"payload": {}}], ("--limit", "-1"))):
            with self.subTest(messages=messages, args=args):
                result = self.run_replay(messages, *args)
                self.assertEqual(result.returncode, 2)
                self.assertIn("ERROR:", result.stderr)
                self.assertNotIn("Summary:", result.stdout)

    def test_dry_run_valid_payload(self):
        result = self.run_replay([{"id": "one", "payload": {"order": "synthetic"}}])
        self.assertEqual(result.returncode, 0)
        self.assertIn("[DRY-RUN]", result.stdout)


if __name__ == "__main__":
    unittest.main()
