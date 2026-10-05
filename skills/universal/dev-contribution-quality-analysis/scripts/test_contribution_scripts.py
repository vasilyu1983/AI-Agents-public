#!/usr/bin/env python3
"""Regression tests for the contribution-quality scripts.

Each test pins a requirement from references/scoring-model.md and SKILL.md:
unknowns are not zeroes, volume is never quality, no tier on insufficient data,
and a missing config key fails with a named error instead of a traceback.

Run: python3 -m unittest discover -s scripts -p 'test_*.py'
"""
from __future__ import annotations

import csv
import importlib.util
import subprocess
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

HERE = Path(__file__).resolve().parent


def _load(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


extract = _load("extract_profile", "extract-contribution-profile.py")
rating = _load("code_rating", "compute-code-rating.py")
exporter = _load("git_numstat", "export-git-numstat.py")
report = _load("quality_report", "generate-quality-report.py")

THRESHOLDS = extract.DEFAULT_CONFIG["thresholds"]


def _commits(n: int, ins: int = 100, dels: int = 50, start: date = date(2026, 1, 5), step: int = 1):
    return [
        {
            "repo": "r",
            "datetime": (start + timedelta(days=i * step)).isoformat() + "T10:00:00",
            "insertions": ins,
            "deletions": dels,
            "code_ins": ins,
            "code_del": dels,
            "files_changed": 2,
            "subject": "feat: add parser support for x",
        }
        for i in range(n)
    ]


class ChurnIsUnknownNotInverted(unittest.TestCase):
    def test_small_commits_do_not_produce_churn_over_100_pct(self):
        # Before the fix, 10 commits of +100/-50 gave 225% churn (0/8 pts) while the
        # same work as one commit gave 0% (8/8): small-commit discipline was punished.
        many = extract.compute_d2_signals(_commits(10))
        one = extract.compute_d2_signals(_commits(1, ins=1000, dels=500))
        self.assertIsNone(many["churn_14d_pct"])
        self.assertIsNone(one["churn_14d_pct"])
        d2_many = extract.score_d2(many, THRESHOLDS, {})
        d2_one = extract.score_d2(one, THRESHOLDS, {})
        self.assertIsNone(d2_many["breakdown"]["churn_rate"])
        self.assertEqual(d2_many["score"], d2_one["score"])


class UnknownsEarnNoCredit(unittest.TestCase):
    def test_unmeasured_duplication_is_not_imputed(self):
        d2 = extract.score_d2(extract.compute_d2_signals(_commits(40)), THRESHOLDS, {})
        self.assertIsNone(d2["breakdown"]["duplication_ratio"])  # was a neutral 3 pts
        self.assertEqual(d2["status"], "insufficient_evidence")
        self.assertEqual(d2["max_achievable"], 0)

    def test_measured_duplication_is_scored(self):
        signals = extract.compute_d2_signals(_commits(40))
        signals["duplication_ratio_pct"] = 4.0
        d2 = extract.score_d2(signals, THRESHOLDS, {})
        self.assertEqual(d2["breakdown"]["duplication_ratio"], 5)
        self.assertEqual(d2["max_achievable"], 5)


class TierRules(unittest.TestCase):
    def _profile(self, commits):
        return extract.build_person_profile(
            "p", commits, [], [], {}, extract.DEFAULT_CONFIG,
            date(2026, 1, 1), date(2026, 3, 31), set(),
        )

    def test_insufficient_data_gets_no_tier(self):
        profile = self._profile(_commits(3))
        self.assertTrue(profile["data_summary"]["insufficient_data"])
        self.assertIsNone(profile["tier"]["tier"])  # was "D"

    def test_tier_cannot_be_a_without_code_quality_evidence(self):
        profile = self._profile(_commits(45, step=2))
        self.assertIn("d2", profile["tier"]["unmeasured_dimensions"])
        self.assertNotEqual(profile["tier"]["tier"], "A")


class VolumeIsContextNotQuality(unittest.TestCase):
    def test_commit_calendar_does_not_change_quality_tier(self):
        start, end = date(2026, 1, 1), date(2026, 3, 31)
        spread = extract.build_person_profile(
            "p", _commits(40, step=2), [], [], {}, extract.DEFAULT_CONFIG,
            start, end, set(),
        )
        burst = extract.build_person_profile(
            "p", _commits(40, step=0), [], [], {}, extract.DEFAULT_CONFIG,
            start, end, set(),
        )
        self.assertIsNone(spread["scores"]["d1"]["score"])
        self.assertIsNone(burst["scores"]["d1"]["score"])
        self.assertEqual(spread["tier"], burst["tier"])

    def test_nominal_quality_max_excludes_d1(self):
        scored = {
            "d1": {"score": None, "status": "context_only", "max_achievable": 0},
            "d2": {"score": 21, "max_achievable": 21, "status": "measured"},
            "d3": {"score": 15, "max_achievable": 15, "status": "measured"},
            "d4": {"score": 20, "max_achievable": 20, "status": "measured"},
            "d5": {"score": 10, "max_achievable": 10, "status": "measured"},
        }
        tier = extract.assign_tier(scored, False)
        self.assertEqual(tier["max"], 66)
        self.assertNotIn("d1", tier["unmeasured_dimensions"])

    def test_person_report_labels_d1_as_context(self):
        profile = extract.build_person_profile(
            "p", _commits(40, step=0), [], [], {}, extract.DEFAULT_CONFIG,
            date(2026, 1, 1), date(2026, 3, 31), set(),
        )
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "report.md"
            report.generate_person_report([profile], None, path)
            rendered = path.read_text()
        self.assertIn("D1 Delivery cadence | context only", rendered)
        self.assertIn("D1: Delivery cadence (context only; not in tier)", rendered)

    def test_mr_throughput_and_active_days_do_not_change_d1(self):
        start, end = date(2026, 1, 1), date(2026, 3, 31)
        commits = _commits(40, step=2)
        few = extract.compute_d1_signals(commits, [], start, end, set(), {})
        many = extract.compute_d1_signals(commits, [{}] * 50, start, end, set(), {})
        self.assertNotEqual(few["mr_per_week"], many["mr_per_week"])
        self.assertEqual(
            extract.score_d1(few, THRESHOLDS, {})["score"],
            extract.score_d1(many, THRESHOLDS, {})["score"],
        )
        self.assertNotIn("mr_throughput", extract.score_d1(few, THRESHOLDS, {})["breakdown"])

    def test_merges_are_not_review_participation(self):
        signals = {"review_events_per_week": None, "distinct_repos_meaningful": 1,
                   "merges_of_others_per_week": 9.0}
        d4 = extract.score_d4(signals, THRESHOLDS, {})
        self.assertIsNone(d4["breakdown"]["review_participation"])

    def test_code_rating_uses_volume_bands_in_alphabetical_order(self):
        self.assertEqual(rating.band(300, 100), "V1")
        self.assertEqual(rating.band(10, 100), "V4")
        self.assertEqual(rating.band(10, 0), "V?")
        header = ("author_email,is_merge,files_changed,code_ins,code_del,test_ins,test_del,"
                  "config_ins,config_del,docs_ins,docs_del,other_ins,other_del").split(",")
        with tempfile.TemporaryDirectory() as tmp:
            src, out = Path(tmp) / "c.csv", Path(tmp) / "o.csv"
            with src.open("w", newline="") as f:
                w = csv.DictWriter(f, fieldnames=header)
                w.writeheader()
                for who, ins in (("zed@x.io", 400), ("amy@x.io", 20)):
                    for _ in range(6):
                        row = dict.fromkeys(header, "0")
                        row.update(author_email=who, files_changed="2", code_ins=str(ins))
                        w.writerow(row)
            subprocess.run([sys.executable, str(HERE / "compute-code-rating.py"),
                            "--input", str(src), "--out-csv", str(out)],
                           check=True, capture_output=True)
            with out.open(newline="") as f:
                rows = list(csv.DictReader(f))
        self.assertEqual([r["person"] for r in rows], ["amy@x.io", "zed@x.io"])
        self.assertEqual({r["volume_band"] for r in rows}, {"V1", "V4"})
        self.assertNotIn("band", rows[0])


class ConfigValidation(unittest.TestCase):
    def test_missing_input_keys_exit_2_with_named_keys(self):
        # Before the fix: raw KeyError: 'input_commits' traceback, exit 1.
        proc = subprocess.run([sys.executable, str(HERE / "extract-contribution-profile.py")],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("input_commits", proc.stderr)
        self.assertIn("input_mr", proc.stderr)
        self.assertNotIn("Traceback", proc.stderr)


class StandaloneGitExport(unittest.TestCase):
    def test_numstat_classification_and_bad_input(self):
        sha = "a" * 40
        raw = (f"{sha}\x1fExample\x1fexample@example.invalid\x1f2026-01-05T10:00:00+00:00"
               "\x1ffeat: add tests\x1f\n\n3\t1\tsrc/app.py\n2\t0\ttests/test_app.py\n")
        with patch.object(exporter, "git", return_value=raw):
            row = exporter.commit_row(Path("/tmp/repo"), sha)
        self.assertEqual((row["code_ins"], row["test_ins"], row["insertions"]), (3, 2, 5))
        with patch.object(exporter, "git", return_value=raw + "bad numstat row\n"):
            with self.assertRaisesRegex(ValueError, "malformed numstat"):
                exporter.commit_row(Path("/tmp/repo"), sha)


class Uncertainty(unittest.TestCase):
    def test_wilson_interval_is_wide_on_small_samples(self):
        small = extract.wilson_interval(1, 5)
        large = extract.wilson_interval(20, 100)
        self.assertGreater(small[1] - small[0], large[1] - large[0])
        self.assertIsNone(extract.wilson_interval(0, 0))


if __name__ == "__main__":
    unittest.main()
