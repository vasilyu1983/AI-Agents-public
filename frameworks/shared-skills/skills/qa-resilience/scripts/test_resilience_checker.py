#!/usr/bin/env python3

"""Tests for resilience_checker.py.

Run: python3 -m unittest scripts.test_resilience_checker -v
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

import resilience_checker as rc  # noqa: E402


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


if __name__ == "__main__":
    unittest.main()
