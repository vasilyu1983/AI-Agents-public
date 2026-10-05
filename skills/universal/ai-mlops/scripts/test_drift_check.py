"""Regression checks for invalid drift-check thresholds."""

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("drift_check.py")


class DriftCheckInputTests(unittest.TestCase):
    def test_infinite_thresholds_cannot_make_a_drift_check_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            baseline = root / "baseline.json"
            current = root / "current.json"
            baseline.write_text(json.dumps({"feature": [100, 100]}))
            current.write_text(json.dumps({"feature": [1, 199]}))

            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--baseline", str(baseline),
                 "--current", str(current), "--warn", "inf", "--alert", "inf"],
                capture_output=True, text=True, check=False,
            )

        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertIn("finite", result.stderr)


if __name__ == "__main__":
    unittest.main()
