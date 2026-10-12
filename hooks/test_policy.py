#!/usr/bin/env python3
"""Tests for policy.py (shared policy loader).

Run: python3 hooks/test_policy.py
"""

import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import policy  # noqa: E402

GOOD = json.loads((HERE.parent / "config" / "policy.json").read_text())


class PolicyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.home = self.tmp / "home"
        (self.home / ".agents").mkdir(parents=True)
        patcher = mock.patch.dict(os.environ, {"HOME": str(self.home)})
        patcher.start()
        self.addCleanup(patcher.stop)
        os.environ.pop("AGENTS_POLICY", None)

    def write(self, name, data):
        p = self.tmp / name
        p.write_text(data if isinstance(data, str) else json.dumps(data))
        return p

    def with_branches(self, branches):
        d = copy.deepcopy(GOOD)
        d["vcs"]["protected_branches"] = branches
        return d

    def test_repo_file_loads(self):
        self.assertEqual(policy.load()["vcs"]["protected_branches"], ["main", "dev"])

    def test_explicit_path_beats_env(self):
        explicit = self.write("a.json", self.with_branches(["a"]))
        env = self.write("b.json", self.with_branches(["b"]))
        with mock.patch.dict(os.environ, {"AGENTS_POLICY": str(env)}):
            self.assertEqual(policy.load(explicit)["vcs"]["protected_branches"], ["a"])

    def test_env_beats_home_file(self):
        (self.home / ".agents" / "policy.json").write_text(json.dumps(self.with_branches(["home"])))
        env = self.write("b.json", self.with_branches(["env"]))
        with mock.patch.dict(os.environ, {"AGENTS_POLICY": str(env)}):
            self.assertEqual(policy.load()["vcs"]["protected_branches"], ["env"])
        self.assertEqual(policy.load()["vcs"]["protected_branches"], ["home"])

    def test_missing_file_raises(self):
        with self.assertRaises(policy.PolicyError):
            policy.load(self.tmp / "nope.json")

    def test_malformed_json_raises(self):
        with self.assertRaises(policy.PolicyError):
            policy.load(self.write("bad.json", "{not json"))

    def test_missing_required_key_raises(self):
        for key in policy.REQUIRED:
            d = copy.deepcopy(GOOD)
            del d[key]
            with self.assertRaises(policy.PolicyError, msg=key):
                policy.load(self.write("k.json", d))

    def test_bad_vcs_values_raise(self):
        for branches in ([], "main", [1]):
            with self.assertRaises(policy.PolicyError):
                policy.load(self.write("v.json", self.with_branches(branches)))
        d = copy.deepcopy(GOOD)
        d["vcs"]["default_base"] = None
        with self.assertRaises(policy.PolicyError):
            policy.load(self.write("v.json", d))


if __name__ == "__main__":
    unittest.main()
