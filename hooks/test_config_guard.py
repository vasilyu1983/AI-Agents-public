#!/usr/bin/env python3
"""Regression tests for config-guard.py (lint and format config guard).

Run: python3 hooks/test_config_guard.py

The guard exists so an agent fixes code instead of loosening an existing rule, while
still being able to create a config for the first time. The last case runs the exact
command that hooks/hooks.json registers, through `sh -c`, with HOME set to a temp folder.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOK = HERE / "config-guard.py"
ENTRY = next(e for e in json.loads((HERE / "hooks.json").read_text())["scopes"]["claude-user"]["hooks"]
             if e["script"] == "config-guard.py")


def run(stdin, cmd=None, env=None):
    cmd = cmd or [sys.executable, str(HOOK)]
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=10, env=env)


def payload(tool, path):
    return json.dumps({"tool_name": tool, "tool_input": {"file_path": path}})


class ConfigGuard(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / ".eslintrc.json").write_text("{}")

    def test_edit_existing_config_denied_with_reason(self):
        for tool in ("Write", "Edit"):
            with self.subTest(tool=tool):
                r = run(payload(tool, str(self.tmp / ".eslintrc.json")))
                self.assertEqual(r.returncode, 2)
                self.assertIn("do not disable this hook", r.stderr)

    def test_symlink_to_config_denied(self):
        (self.tmp / "lint-settings").symlink_to(self.tmp / ".eslintrc.json")
        self.assertEqual(run(payload("Edit", str(self.tmp / "lint-settings"))).returncode, 2)

    def test_case_variant_name_denied(self):
        (self.tmp / ".Prettierrc").write_text("{}")  # exists under this case on any file system
        self.assertEqual(run(payload("Edit", str(self.tmp / ".Prettierrc"))).returncode, 2)

    def test_first_creation_allowed(self):
        self.assertEqual(run(payload("Write", str(self.tmp / "ruff.toml"))).returncode, 0)

    def test_ordinary_file_allowed(self):
        (self.tmp / "app.py").write_text("")
        self.assertEqual(run(payload("Edit", str(self.tmp / "app.py"))).returncode, 0)

    def test_other_tool_ignored(self):
        self.assertEqual(run(json.dumps({"tool_name": "Read", "tool_input": {}})).returncode, 0)

    def test_fails_closed(self):
        for raw in ("{", json.dumps({"tool_name": "Write", "tool_input": {}}), "[]"):
            with self.subTest(raw=raw):
                self.assertEqual(run(raw).returncode, 2)

    def test_registered_command(self):
        home = self.tmp / "home"
        env = dict(os.environ, HOME=str(home))
        target = payload("Edit", str(self.tmp / ".eslintrc.json"))
        self.assertEqual(run(target, ["sh", "-c", ENTRY["command"]], env).returncode, 0,
                         "not installed: the wrapper must not block every edit")
        (home / ".agents/hooks").mkdir(parents=True)
        (home / ".agents/hooks/config-guard.py").symlink_to(HOOK)
        self.assertEqual(run(target, ["sh", "-c", ENTRY["command"]], env).returncode, 2)


if __name__ == "__main__":
    unittest.main()
