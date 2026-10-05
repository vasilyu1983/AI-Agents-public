#!/usr/bin/env python3

"""Tests for resilience_checker.py.

Run: python3 -m unittest scripts.test_resilience_checker -v
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

CHECKER_PATH = Path(os.environ.get("RESILIENCE_CHECKER_UNDER_TEST", SCRIPT_DIR / "resilience_checker.py"))
spec = importlib.util.spec_from_file_location("resilience_checker", CHECKER_PATH)
rc = importlib.util.module_from_spec(spec)
spec.loader.exec_module(rc)


class TierAndLabelTests(unittest.TestCase):
    def test_tier_for_high_score(self):
        # Smoke: function exists and returns a non-empty string
        label = rc._resilience_tier(95.0)
        self.assertIsInstance(label, str)
        self.assertTrue(label)

    def test_tier_for_low_score(self):
        label = rc._resilience_tier(10.0)
        self.assertIsInstance(label, str)

    def test_score_label_returns_string(self):
        self.assertIsInstance(rc._score_label(0.9), str)
        self.assertIsInstance(rc._score_label(0.1), str)


class PatternScoreTests(unittest.TestCase):
    def test_empty_pattern_data_does_not_crash(self):
        # Should produce a numeric score without raising on minimal input.
        score = rc._pattern_score("retries", {})
        self.assertIsInstance(score, float)

    def test_score_is_bounded(self):
        score = rc._pattern_score("circuit_breakers", {"implemented": True})
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)


class ComputeScoreTests(unittest.TestCase):
    def test_empty_patterns_yields_zero(self):
        # Returns a per-pattern breakdown filled with zeros; total is 0.
        total, breakdown = rc._compute_score({})
        self.assertEqual(total, 0.0)
        self.assertIsInstance(breakdown, dict)
        # All values should be zero when no patterns are implemented.
        self.assertTrue(all(v == 0.0 for v in breakdown.values()))

    def test_returns_per_pattern_breakdown(self):
        _total, breakdown = rc._compute_score({"retries": {"implemented": True}})
        self.assertIsInstance(breakdown, dict)
        self.assertIn("retries", breakdown)


class ParserTests(unittest.TestCase):
    def test_parser_has_subcommands(self):
        parser = rc.build_parser()
        # Argparse subparsers are stored as actions; verify --help string lists them.
        help_text = parser.format_help()
        for cmd in ("assess", "gaps", "report"):
            self.assertIn(cmd, help_text)


class FailClosedTests(unittest.TestCase):
    def run_cli(self, profile, command="assess", output=None):
        with tempfile.TemporaryDirectory() as temp:
            profile_path = Path(temp) / "profile.json"
            profile_path.write_text(json.dumps(profile))
            args = [sys.executable, str(CHECKER_PATH), command, "--input", str(profile_path)]
            if output:
                args += ["--output", str(output)]
            return subprocess.run(args, capture_output=True, text=True)

    def test_string_booleans_rejected_before_claiming_coverage(self):
        profile = {"patterns": {name: {"has_it": "false", "configured_correctly": "false"}
                               for name in rc.WEIGHTS}}
        for command in ("assess", "gaps", "report"):
            with self.subTest(command=command):
                result = self.run_cli(profile, command)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("must be a JSON boolean", result.stderr)
                self.assertEqual(result.stdout, "")

    def test_invalid_report_leaves_existing_artifact_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "report.md"
            output.write_text("previous evidence")
            result = self.run_cli({"patterns": {"retries": {"has_it": "yes", "configured_correctly": "yes"}}},
                                  "report", output)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(output.read_text(), "previous evidence")

    def test_unknown_fields_and_observability_booleans_are_rejected(self):
        profiles = [
            {"patterns": {"circuit_breakers": {"has_it": True, "configured_correctly": True}}},
            {"patterns": {"retries": {"implemented": True}}},
            {"patterns": {}, "observability": {"has_alerts": "false"}},
            {"patterns": {"retries": {"has_it": False, "configured_correctly": True}}},
        ]
        for profile in profiles:
            with self.subTest(profile=profile):
                result = self.run_cli(profile)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Error: invalid profile", result.stderr)

    def test_evaluated_hedging_is_not_automatically_na(self):
        pattern = {"has_it": False, "configured_correctly": False,
                   "notes": "Evaluated: safe reads exist and hedging is needed, not implemented."}
        self.assertEqual(rc._pattern_score("hedging", pattern), 0.0)
        self.assertTrue(rc._is_gap("hedging", pattern, 0.0))

    def test_explicit_na_and_real_booleans_remain_supported(self):
        pattern = {"has_it": False, "configured_correctly": False,
                   "notes": "N/A: safe reads not present"}
        self.assertEqual(rc._pattern_score("hedging", pattern), 1.0)
        result = self.run_cli({"patterns": {"hedging": pattern}})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Self-reported coverage only", result.stdout)


if __name__ == "__main__":
    unittest.main()
