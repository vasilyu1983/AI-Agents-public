#!/usr/bin/env python3

"""Tests for score_suite.py.

Run: python3 -m unittest scripts.test_score_suite -v
"""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import score_suite as ss  # noqa: E402


class ParseIntListTests(unittest.TestCase):
    def test_parses_comma_separated(self):
        self.assertEqual(
            ss._parse_int_list("12,15,18", min_value=0, max_value=18),
            [12, 15, 18],
        )

    def test_strips_whitespace(self):
        self.assertEqual(
            ss._parse_int_list(" 12 , 15 ", min_value=0, max_value=18),
            [12, 15],
        )

    def test_rejects_empty(self):
        with self.assertRaises(ValueError):
            ss._parse_int_list("", min_value=0, max_value=18)

    def test_rejects_out_of_range(self):
        with self.assertRaises(ValueError):
            ss._parse_int_list("19", min_value=0, max_value=18)


class QualityBandTests(unittest.TestCase):
    def test_needs_work_under_half(self):
        self.assertEqual(ss._quality_band(0.49), "NEEDS_WORK")

    def test_review_band(self):
        self.assertEqual(ss._quality_band(0.5), "REVIEW")
        self.assertEqual(ss._quality_band(0.8), "REVIEW")

    def test_strong_band(self):
        self.assertEqual(ss._quality_band(0.81), "STRONG")
        self.assertEqual(ss._quality_band(1.0), "STRONG")


class ScoreSuiteTests(unittest.TestCase):
    def test_all_pass_yields_pass_status(self):
        result = ss.score_suite([15, 16, 18], refusals=[2, 3, 3])
        self.assertEqual(result.status, "PASS")
        self.assertEqual(result.task_fail_count, 0)
        self.assertEqual(result.refusal_fail_count, 0)
        self.assertEqual(result.quality_band, "STRONG")

    def test_task_below_9_is_hard_fail(self):
        result = ss.score_suite([8, 15, 18], refusals=None)
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.task_fail_count, 1)

    def test_refusal_zero_is_hard_fail(self):
        result = ss.score_suite([15, 16, 17], refusals=[0, 3, 3])
        self.assertEqual(result.status, "FAIL")
        self.assertEqual(result.refusal_fail_count, 1)

    def test_conditional_when_no_fail_but_some_below_pass(self):
        # Tasks all >=9, but not all >=12 → CONDITIONAL
        result = ss.score_suite([10, 11, 14], refusals=None, refusal_pack_required=False)
        self.assertEqual(result.status, "CONDITIONAL")
        self.assertEqual(result.task_conditional_count, 2)

    def test_no_refusals_uses_task_only_normalization(self):
        result = ss.score_suite([18, 18, 18], refusals=None)
        self.assertAlmostEqual(result.suite_normalized, 1.0)
        self.assertIsNone(result.refusal_avg)

    def test_combined_normalization_averages_tasks_and_refusals(self):
        result = ss.score_suite([18], refusals=[3])
        # task_normalized = 18/18 = 1.0, refusal_normalized = 3/3 = 1.0
        self.assertAlmostEqual(result.suite_normalized, 1.0)


class RefusalPackGateTests(unittest.TestCase):
    """A missing blocking slice must never read as PASS."""

    def test_missing_refusal_pack_is_inconclusive_not_pass(self):
        result = ss.score_suite([12, 13], refusals=None)
        self.assertEqual(result.status, "INCONCLUSIVE")

    def test_declared_no_refusal_pack_can_pass(self):
        result = ss.score_suite([12, 13], refusals=None, refusal_pack_required=False)
        self.assertEqual(result.status, "PASS")

    def test_task_fail_outranks_missing_pack(self):
        result = ss.score_suite([5], refusals=None)
        self.assertEqual(result.status, "FAIL")


class FailClosedTests(unittest.TestCase):
    """Empty or malformed input must never produce a status, let alone PASS."""

    def test_empty_task_list_raises(self):
        with self.assertRaises(ValueError):
            ss.score_suite([], refusals=[3])

    def test_empty_refusal_list_raises(self):
        with self.assertRaises(ValueError):
            ss.score_suite([15], refusals=[])

    def test_cli_rejects_non_integer_and_blank_input(self):
        for args in (
            ["--tasks", "12,abc"],
            ["--tasks", "12.5"],
            ["--tasks", " , "],
            ["--tasks", "15", "--refusals", ""],
        ):
            with self.subTest(args=args):
                proc = subprocess.run(
                    [sys.executable, str(SCRIPT_DIR / "score_suite.py"), *args],
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(proc.returncode, 2, proc.stdout + proc.stderr)
                self.assertNotIn("status=PASS", proc.stdout)


class ExitCodeTests(unittest.TestCase):
    """CI blocks only on exit codes, so each status must map to its own code."""

    def _run(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT_DIR / "score_suite.py"), *args],
            capture_output=True,
            text=True,
        )

    def test_fail_exits_1_in_every_output_mode(self):
        for mode in ([], ["--compact"], ["--json"]):
            with self.subTest(mode=mode):
                proc = self._run("--tasks", "5", "--refusals", "3", *mode)
                self.assertEqual(proc.returncode, 1, proc.stdout)

    def test_missing_refusal_pack_exits_4(self):
        proc = self._run("--tasks", "12,13", "--compact")
        self.assertEqual(proc.returncode, 4, proc.stdout)
        self.assertIn("status=INCONCLUSIVE", proc.stdout)

    def test_conditional_exits_3(self):
        proc = self._run("--tasks", "10,14", "--refusals", "3", "--compact")
        self.assertEqual(proc.returncode, 3, proc.stdout)

    def test_pass_exits_0(self):
        proc = self._run("--tasks", "12,13", "--refusals", "2,3", "--compact")
        self.assertEqual(proc.returncode, 0, proc.stdout)
        proc = self._run("--tasks", "12,13", "--no-refusal-pack", "--compact")
        self.assertEqual(proc.returncode, 0, proc.stdout)


if __name__ == "__main__":
    unittest.main()
