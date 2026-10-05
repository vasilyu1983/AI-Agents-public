#!/usr/bin/env python3
"""Offline CLI regressions; DEBUGGING_SCRIPTS_UNDER_TEST selects old helpers."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPTS = Path(os.environ.get("DEBUGGING_SCRIPTS_UNDER_TEST", Path(__file__).parent))


class HelperTests(unittest.TestCase):
    def config_result(self, a, b):
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("a.json", "b.json")]
            for path, value in zip(paths, (a, b)):
                path.write_text(json.dumps(value), encoding="utf-8")
            return subprocess.run([sys.executable, str(SCRIPTS / "config_diff.py"),
                                   *map(str, paths)], capture_output=True, text=True)

    def log_result(self, content):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.log"
            path.write_bytes(content)
            return subprocess.run([sys.executable, str(SCRIPTS / "log_error_summary.py"),
                                   str(path)], capture_output=True, text=True)

    def test_scalar_types_remain_distinct(self):
        for scalar in (True, False, None, 1, 1.5):
            with self.subTest(scalar=scalar):
                result = self.config_result({"value": scalar}, {"value": json.dumps(scalar)})
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_literal_path_keys_remain_distinct(self):
        for a, b in (({"a.b": 1}, {"a": {"b": 1}}),
                     ({"a[0]": 1}, {"a": [1]}),
                     ({"": {"a": 1}}, {"a": 1})):
            with self.subTest(a=a):
                result = self.config_result(a, b)
                self.assertEqual(result.returncode, 1, result.stdout + result.stderr)

    def test_empty_container_is_not_a_string(self):
        for value in ({}, []):
            with self.subTest(value=value):
                self.assertEqual(self.config_result({"v": value}, {"v": json.dumps(value)}).returncode, 1)

    def test_reordered_keys_stay_equal(self):
        self.assertEqual(self.config_result({"a.b": 1, "c": [True]},
                                            {"c": [True], "a.b": 1}).returncode, 0)

    def test_secret_changes_are_detected_and_redacted(self):
        result = self.config_result({"token": "synthetic-before"}, {"token": "synthetic-after"})
        self.assertEqual(result.returncode, 1)
        self.assertIn("<redacted>", result.stdout)
        self.assertNotIn("synthetic-before", result.stdout)
        self.assertNotIn("synthetic-after", result.stdout)

    def test_nul_after_probe_window_fails(self):
        result = self.log_result(b"info healthy\n" * 60 + b"binary\x00tail\n")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertNotIn("No error", result.stdout)

    def test_invalid_utf8_fails(self):
        result = self.log_result(b"info healthy\ninvalid \xff\n")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_invalid_utf8_stdin_fails(self):
        result = subprocess.run([sys.executable, str(SCRIPTS / "log_error_summary.py"), "-"],
                                input=b"info invalid \xff\n", capture_output=True)
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)

    def test_clean_nonempty_log_succeeds(self):
        result = self.log_result(b"info healthy\n")
        self.assertEqual(result.returncode, 0)
        self.assertIn("1 scanned lines", result.stdout)


if __name__ == "__main__":
    unittest.main()
