#!/usr/bin/env python3

"""Tests for perf_budget_checker.py.

Run: python3 -m unittest scripts.test_perf_budget_checker -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import perf_budget_checker as pb  # noqa: E402


class StatusConstantsTests(unittest.TestCase):
    def test_status_constants_exist(self):
        self.assertTrue(pb.PASS)
        self.assertTrue(pb.WARN)
        self.assertTrue(pb.FAIL)


class ApiP95Tests(unittest.TestCase):
    def test_within_budget_passes(self):
        status, _ = pb._check_api_p95(80, 100)
        self.assertEqual(status, pb.PASS)

    def test_warn_zone_25pct(self):
        status, _ = pb._check_api_p95(120, 100)
        self.assertEqual(status, pb.WARN)

    def test_fail_above_25pct(self):
        status, _ = pb._check_api_p95(150, 100)
        self.assertEqual(status, pb.FAIL)


class ApiP99Tests(unittest.TestCase):
    def test_within_budget_passes(self):
        status, _ = pb._check_api_p99(90, 100, "p99")
        self.assertEqual(status, pb.PASS)

    def test_tighter_warn_zone_15pct(self):
        # p99 has tighter warn (15%) vs p95 (25%)
        status, _ = pb._check_api_p99(110, 100, "p99")
        self.assertEqual(status, pb.WARN)
        status, _ = pb._check_api_p99(120, 100, "p99")
        self.assertEqual(status, pb.FAIL)

    def test_label_appears_in_note(self):
        _, note = pb._check_api_p99(90, 100, "p99.9")
        self.assertIn("p99.9", note)


class ThroughputTests(unittest.TestCase):
    def test_meets_minimum(self):
        status, _ = pb._check_throughput(500, 500)
        self.assertEqual(status, pb.PASS)

    def test_warn_within_10pct(self):
        status, _ = pb._check_throughput(460, 500)
        self.assertEqual(status, pb.WARN)

    def test_fail_below_90pct(self):
        status, _ = pb._check_throughput(400, 500)
        self.assertEqual(status, pb.FAIL)


class ErrorRateTests(unittest.TestCase):
    def test_well_under_passes(self):
        status, _ = pb._check_error_rate(0.1, 1.0)
        self.assertEqual(status, pb.PASS)

    def test_at_budget_passes(self):
        status, _ = pb._check_error_rate(1.0, 1.0)
        self.assertEqual(status, pb.PASS)

    def test_above_budget_warns(self):
        status, _ = pb._check_error_rate(1.3, 1.0)
        self.assertEqual(status, pb.WARN)


class EvaluateBudgetsIntegrationTests(unittest.TestCase):
    """Verify the new p99/p99.9 keys get picked up by _evaluate_budgets."""

    def test_p99_metrics_recognized(self):
        data = {
            "budgets": {"api_p95_ms": 100, "api_p99_ms": 200, "api_p999_ms": 500},
            "results": {"api_p95_ms": 80, "api_p99_ms": 180, "api_p999_ms": 480},
        }
        checks = pb._evaluate_budgets(data)
        metrics = {c["metric"] for c in checks}
        self.assertIn("API p95", metrics)
        self.assertIn("API p99", metrics)
        self.assertIn("API p99.9", metrics)
        # All within budget → all pass.
        self.assertTrue(all(c["status"] == pb.PASS for c in checks))

    def test_p99_fail_status_propagates(self):
        data = {
            "budgets": {"api_p99_ms": 100},
            "results": {"api_p99_ms": 200},  # 2× budget — well past 15% warn zone
        }
        checks = pb._evaluate_budgets(data)
        self.assertEqual(checks[0]["status"], pb.FAIL)


if __name__ == "__main__":
    unittest.main()
