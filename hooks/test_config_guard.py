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
os.environ["GUARD_BLOCK_LOG"] = os.path.join(tempfile.mkdtemp(), "blocks.jsonl")  # keep the suite off the real telemetry file
ENTRY = next(e for e in json.loads((HERE / "hooks.json").read_text())["scopes"]["claude-user"]["hooks"]
             if e["script"] == "config-guard.py")


def run(stdin, cmd=None, env=None):
    cmd = cmd or [sys.executable, str(HOOK)]
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True, timeout=10, env=env)


def payload(tool, path):
    return json.dumps({"tool_name": tool, "tool_input": {"file_path": path}})


class BlockLog(unittest.TestCase):
    MARKER = "MARKER-NOT-LOGGED-7f3a"

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp(dir=os.environ.get("TMPDIR")))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        self.log = self.tmp / "blocks.jsonl"
        self.env = dict(os.environ, GUARD_BLOCK_LOG=str(self.log))
        self.cfg = self.tmp / f".eslintrc-{self.MARKER}.json"
        self.cfg.write_text("{}")

    def test_block_logs_one_line_without_path(self):
        self.assertEqual(run(payload("Edit", str(self.tmp / ".eslintrc.json")), env=self.env).returncode, 0)
        (self.tmp / ".eslintrc.json").write_text("{}")
        r = run(payload("Edit", str(self.tmp / ".eslintrc.json")), env=self.env)
        self.assertEqual(r.returncode, 2)
        (entry,) = [json.loads(x) for x in self.log.read_text().splitlines()]
        self.assertEqual((entry["hook"], entry["rule"]), ("config-guard", "config:protected-file"))
        self.assertNotIn(str(self.tmp), self.log.read_text())

    def test_allowed_edit_writes_nothing(self):
        (self.tmp / "app.py").write_text("")
        self.assertEqual(run(payload("Edit", str(self.tmp / "app.py")), env=self.env).returncode, 0)
        self.assertFalse(self.log.exists())

    def test_unwritable_log_still_blocks(self):
        (self.tmp / ".eslintrc.json").write_text("{}")
        (self.tmp / "afile").write_text("")
        env = dict(os.environ, GUARD_BLOCK_LOG=str(self.tmp / "afile" / "x.jsonl"))
        r = run(payload("Edit", str(self.tmp / ".eslintrc.json")), env=env)
        self.assertEqual(r.returncode, 2)
        self.assertIn("block log failed", r.stderr)


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
        self.assertEqual(run(payload("Edit", str(self.tmp / "app.py")), ["sh", "-c", ENTRY["command"]], env).returncode, 0,
                         "not installed: the wrapper must not block every edit")
        self.assertEqual(run(target, ["sh", "-c", ENTRY["command"]], env).returncode, 2,
                         "not installed: a protected config edit is blocked")
        (home / ".agents/hooks").mkdir(parents=True)
        (home / ".agents/hooks/config-guard.py").symlink_to(HOOK)
        self.assertEqual(run(target, ["sh", "-c", ENTRY["command"]], env).returncode, 2)

    def _wrapper(self, payload_text):
        home = self.tmp / "nohome"
        return run(payload_text, ["sh", "-c", ENTRY["command"]], dict(os.environ, HOME=str(home)))

    def test_missing_script_protected_name_blocks(self):
        r = self._wrapper(payload("Edit", "/x/y/.eslintrc.json"))
        self.assertEqual(r.returncode, 2)
        self.assertIn("config-guard missing", r.stderr)

    def test_missing_script_other_file_allowed(self):
        self.assertEqual(self._wrapper(payload("Edit", "/x/y/app.py")).returncode, 0)

    def _policy(self, protected):
        pol = json.loads((HERE.parent / "config" / "policy.json").read_text())
        pol["protected_paths"] = protected
        f = self.tmp / "policy.json"
        f.write_text(json.dumps(pol))
        return dict(os.environ, AGENTS_POLICY=str(f))

    def test_policy_protected_path_blocks(self):
        env = self._policy([".github/workflows/*.yml"])
        repo = HERE.parent
        r = run(payload("Edit", str(repo / ".github/workflows/ci.yml")), env=env)
        self.assertEqual(r.returncode, 2)
        self.assertEqual(run(payload("Edit", str(repo / ".github/other.txt")), env=env).returncode, 0)

    def test_policy_unreadable_keeps_builtin(self):
        env = dict(os.environ, AGENTS_POLICY=str(self.tmp / "missing.json"))
        r = run(payload("Edit", str(self.tmp / ".eslintrc.json")), env=env)
        self.assertEqual(r.returncode, 2)
        r = run(payload("Edit", str(self.tmp / "app.py")), env=env)
        self.assertEqual(r.returncode, 0)
        self.assertIn("policy unreadable, protected_paths not applied", r.stderr)


if __name__ == "__main__":
    unittest.main()
