#!/usr/bin/env python3
"""Fail-closed contract validation regressions."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contract_validator import validate_contract  # noqa: E402


class FailClosedContractTests(unittest.TestCase):
    SCRIPT = Path(__file__).resolve().parent / "contract_validator.py"

    def test_empty_contract_list_is_an_error(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            source = Path(temp_dir) / "contracts.json"
            source.write_text("[]", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(self.SCRIPT), "--input", str(source)],
                capture_output=True, text=True,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("empty", result.stdout + result.stderr)

    def test_boolean_risk_tier_is_not_an_integer_tier(self):
        errors = validate_contract(
            {"caller": "example", "task_type": "summary", "risk_tier": True, "input": "text"},
            "ModelRequest",
        )
        self.assertTrue(errors)
        self.assertIn("risk_tier", " ".join(errors))

    def test_nonfinite_eval_score_is_rejected(self):
        errors = validate_contract(
            {"suite_version": "example", "judged_dimensions": ["accuracy"],
             "score": float("nan"), "status": "pass"},
            "EvalRun",
        )
        self.assertTrue(errors)
        self.assertIn("score", " ".join(errors))

    def test_boolean_eval_score_is_rejected(self):
        errors = validate_contract(
            {"suite_version": "example", "judged_dimensions": ["accuracy"],
             "score": True, "status": "pass"},
            "EvalRun",
        )
        self.assertIn("score", " ".join(errors))


if __name__ == "__main__":
    unittest.main()
