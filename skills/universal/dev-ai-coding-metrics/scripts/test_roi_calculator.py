#!/usr/bin/env python3
"""Regression tests for roi_calculator.py.

Requirements pinned here (SKILL.md Anti-Gaming Checklist and Measurement Checklist):
missing inputs fail closed instead of becoming a grade or reset advice; there is no
single blended score; ROI without review burden is labelled not decision-grade.

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "roi_calculator.py"
SAMPLE = HERE.parent / "data" / "sample-ai-metrics.json"

spec = importlib.util.spec_from_file_location("roi_calculator", SCRIPT)
roi = importlib.util.module_from_spec(spec)
sys.modules["roi_calculator"] = roi  # dataclasses resolve their module here
spec.loader.exec_module(roi)


def run(command: str, data: dict | None = None, path: Path | None = None):
    with tempfile.TemporaryDirectory() as tmp:
        if path is None:
            path = Path(tmp) / "in.json"
            path.write_text(json.dumps(data))
        return subprocess.run([sys.executable, str(SCRIPT), command, "--input", str(path)],
                              capture_output=True, text=True)


class FailClosed(unittest.TestCase):
    def test_empty_input_exits_2_for_every_subcommand(self):
        # Before the fix: `report --input {}` exited 0 with "Health grade: F" and
        # "Consider a structured reset" computed from no data.
        for command in ("roi", "score", "report"):
            proc = run(command, {})
            self.assertEqual(proc.returncode, 2, command)
            self.assertIn("insufficient data", proc.stderr)
            self.assertNotIn("reset", proc.stdout.lower())
            self.assertNotIn("grade", proc.stdout.lower())

    def test_missing_family_is_named(self):
        data = json.loads(SAMPLE.read_text())
        del data["metric_families"]["quality"]
        proc = run("score", data)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("metric_families.quality.score", proc.stderr)

    def test_missing_roi_input_is_named(self):
        data = json.loads(SAMPLE.read_text())
        del data["avg_dev_hourly_rate"]
        proc = run("roi", data)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("avg_dev_hourly_rate", proc.stderr)


class NoBlendedScore(unittest.TestCase):
    def test_sample_report_has_per_family_ratings_and_no_composite(self):
        proc = run("report", path=SAMPLE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertNotIn("Composite score", proc.stdout)
        self.assertNotIn("Health grade", proc.stdout)
        self.assertIn("| Quality |", proc.stdout)
        self.assertFalse(hasattr(roi.calc_score(json.loads(SAMPLE.read_text())), "composite"))


class ReviewBurden(unittest.TestCase):
    def test_roi_without_burden_is_labelled_not_decision_grade(self):
        proc = run("roi", path=SAMPLE)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("not decision-grade", proc.stdout)

    def test_burden_hours_reduce_net_savings(self):
        data = json.loads(SAMPLE.read_text())
        base = roi.calc_roi(data)
        data["review_hours_per_dev_per_week"] = 1.0
        data["rework_hours_per_dev_per_week"] = 0.5
        burdened = roi.calc_roi(data)
        self.assertTrue(burdened.burden_included)
        self.assertLess(burdened.annual_net_savings, base.annual_net_savings)
        self.assertAlmostEqual(burdened.weekly_hours_saved, data["team_size"] * (3.5 - 1.5))


if __name__ == "__main__":
    unittest.main()
