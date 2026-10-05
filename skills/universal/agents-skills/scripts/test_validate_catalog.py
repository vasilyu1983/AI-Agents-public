#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
VALIDATOR = SCRIPT_DIR / "validate_catalog.py"


class ValidateCatalogTests(unittest.TestCase):
    def run_validator(self, path: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), str(path)],
            check=False,
            capture_output=True,
            text=True,
        )

    def test_empty_catalog_root_fails_closed(self) -> None:
        # A root with no skill directories is a wrong path, not a clean catalog;
        # it must not print "Skills: 0 ... Fail: 0" and exit 0.
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_validator(Path(tmp))
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("no skill directories found", result.stderr)
            self.assertNotIn("Skills: 0", result.stdout)

    def test_missing_catalog_root_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_validator(Path(tmp) / "does-not-exist")
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_grouped_catalog_walks_group_folders_not_groups(self) -> None:
        # The repository keeps skills in group folders; a group folder itself
        # must never be validated as a skill.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "skills"
            for rel in ("universal/alpha-skill", "client/acme/beta-skill"):
                (root / rel).mkdir(parents=True)
            result = self.run_validator(root)
            self.assertIn("- Skills: 2", result.stdout, result.stdout + result.stderr)
            self.assertIn("alpha-skill", result.stdout)
            self.assertIn("beta-skill", result.stdout)
            self.assertNotIn("`universal`", result.stdout)
            self.assertNotIn("`client`", result.stdout)



if __name__ == "__main__":
    unittest.main()
