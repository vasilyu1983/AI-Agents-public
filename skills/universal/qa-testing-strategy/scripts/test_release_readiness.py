#!/usr/bin/env python3
"""Known-bad inputs must never return SHIP. Run: python3 scripts/test_release_readiness.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from release_readiness import release_readiness  # noqa: E402

GREEN = {
    "security_clean": True,
    "critical_e2e_pass": True,
    "no_open_p0": True,
    "test_pass_rate": 100,
    "e2e_pass_rate": 100,
    "flake_rate": 0,
    "performance_pass": True,
    "staging_soak_hours": 4,
}


class ReleaseReadinessTest(unittest.TestCase):
    def test_all_green_ships(self):
        self.assertEqual(release_readiness(GREEN)["recommendation"], "SHIP")

    def test_security_failure_blocks_even_when_everything_else_is_perfect(self):
        # The old compensatory score returned 85.0 -> SHIP for this input.
        result = release_readiness({**GREEN, "security_clean": False})
        self.assertEqual(result["recommendation"], "BLOCK")
        self.assertIn("security_clean", result["hard_gate_failures"])

    def test_critical_e2e_failure_blocks(self):
        self.assertEqual(release_readiness({**GREEN, "critical_e2e_pass": False})["recommendation"], "BLOCK")

    def test_open_p0_blocks(self):
        self.assertEqual(release_readiness({**GREEN, "no_open_p0": False})["recommendation"], "BLOCK")

    def test_missing_hard_gate_fails_closed(self):
        metrics = dict(GREEN)
        del metrics["security_clean"]
        self.assertEqual(release_readiness(metrics)["recommendation"], "BLOCK")

    def test_truthy_non_boolean_does_not_pass_hard_gate(self):
        self.assertEqual(release_readiness({**GREEN, "security_clean": "false"})["recommendation"], "BLOCK")

    def test_performance_failure_does_not_ship(self):
        # The old score returned 90.0 -> SHIP for a failed performance check.
        self.assertNotEqual(release_readiness({**GREEN, "performance_pass": False})["recommendation"], "SHIP")


if __name__ == "__main__":
    unittest.main()
