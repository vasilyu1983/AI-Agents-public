import csv
import math
import os
import subprocess
import sys
import tempfile
import unittest

import analyze_paired_results as analyzer


class PairedAnalyzerTests(unittest.TestCase):
    def write_rows(self, rows):
        handle = tempfile.NamedTemporaryFile("w", newline="", delete=False)
        writer = csv.DictWriter(handle, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def write_text(self, text):
        handle = tempfile.NamedTemporaryFile("w", delete=False)
        handle.write(text)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def run_cli(self, path):
        return subprocess.run(
            [sys.executable, analyzer.__file__, path, "--bootstrap-reps", "100"],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_known_improvement_and_stable_seed(self):
        path = self.write_rows([
            {"unit_id": str(i), "cluster_id": str(i), "stratum": "core", "baseline": 0, "candidate": 1,
             "critical_baseline": False, "critical_candidate": False} for i in range(6)
        ])
        first = analyzer.analyze(analyzer.load_rows(path), reps=200, seed=7)
        second = analyzer.analyze(analyzer.load_rows(path), reps=200, seed=7)
        self.assertEqual(first, second)
        self.assertEqual(first["results"]["overall"]["effect_candidate_minus_baseline"], 1)
        self.assertEqual(first["results"]["overall"]["bootstrap_percentile_interval"]["lower"], 1)

    def test_repeated_cluster_is_one_block_and_estimands_are_explicit(self):
        path = self.write_rows([
            {"unit_id": "a1", "cluster_id": "a", "stratum": "core", "baseline": 0, "candidate": 1, "critical_baseline": 0, "critical_candidate": 0},
            {"unit_id": "a2", "cluster_id": "a", "stratum": "core", "baseline": 0, "candidate": 1, "critical_baseline": 0, "critical_candidate": 1},
            {"unit_id": "a3", "cluster_id": "a", "stratum": "core", "baseline": 0, "candidate": 1, "critical_baseline": 0, "critical_candidate": 0},
            {"unit_id": "b1", "cluster_id": "b", "stratum": "edge", "baseline": 1, "candidate": 0, "critical_baseline": 1, "critical_candidate": 0},
        ])
        rows = analyzer.load_rows(path)
        unit = analyzer.analyze(rows, "unit_mean", reps=200)
        cluster = analyzer.analyze(rows, "cluster_mean", reps=200)
        self.assertAlmostEqual(unit["results"]["overall"]["effect_candidate_minus_baseline"], 0.5)
        self.assertAlmostEqual(cluster["results"]["overall"]["effect_candidate_minus_baseline"], 0.0)
        self.assertEqual(unit["results"]["overall"]["clusters"], 2)
        self.assertIn("edge", unit["results"]["by_stratum"])
        self.assertEqual(unit["critical_failures"]["by_stratum"]["core"]["new_candidate_failures"], 1)
        self.assertAlmostEqual(cluster["results"]["overall"]["baseline_mean_for_estimand"], 0.5)

    def test_overall_named_stratum_cannot_replace_overall_and_one_cluster_has_no_interval(self):
        path = self.write_rows([
            {"unit_id": "a", "cluster_id": "one", "stratum": "overall", "baseline": 0, "candidate": 1},
            {"unit_id": "b", "cluster_id": "two", "stratum": "other", "baseline": 0, "candidate": 0},
        ])
        result = analyzer.analyze(analyzer.load_rows(path), reps=200)
        self.assertEqual(result["results"]["overall"]["units"], 2)
        self.assertEqual(result["results"]["by_stratum"]["overall"]["units"], 1)
        self.assertIsNone(result["results"]["by_stratum"]["overall"]["bootstrap_percentile_interval"])

    def test_duplicate_unit_and_nonfinite_score_rejected(self):
        duplicate = self.write_rows([
            {"unit_id": "x", "baseline": 0, "candidate": 0},
            {"unit_id": "x", "baseline": 0, "candidate": 1},
        ])
        with self.assertRaisesRegex(ValueError, "unique"):
            analyzer.load_rows(duplicate)
        nonfinite = self.write_rows([{"unit_id": "x", "baseline": 0, "candidate": math.inf}])
        with self.assertRaisesRegex(ValueError, "finite"):
            analyzer.load_rows(nonfinite)

    def test_absent_critical_columns_are_not_reported_as_zero_failures(self):
        path = self.write_rows([
            {"unit_id": "a", "baseline": 0, "candidate": 1},
            {"unit_id": "b", "baseline": 1, "candidate": 1},
        ])
        result = analyzer.analyze(analyzer.load_rows(path), reps=100)
        self.assertFalse(result["critical_failures"]["overall"]["available"])

    def test_partial_critical_metadata_fails_cleanly_at_cli(self):
        path = self.write_text("unit_id,baseline,candidate,critical_baseline,critical_candidate\na,0,1,true,\n")
        result = self.run_cli(path)
        self.assertEqual(result.returncode, 2)
        self.assertIn("populated for every row or omitted", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_duplicate_headers_and_overflowing_difference_fail_cleanly(self):
        duplicate = self.write_text("unit_id,baseline,candidate,candidate\na,0,1,0\n")
        result = self.run_cli(duplicate)
        self.assertEqual(result.returncode, 2)
        self.assertIn("header names must be unique", result.stderr)
        overflow = self.write_text("unit_id,baseline,candidate\na,-1e308,1e308\n")
        result = self.run_cli(overflow)
        self.assertEqual(result.returncode, 2)
        self.assertIn("difference must be finite", result.stderr)
        self.assertNotIn("Infinity", result.stdout)

    def test_large_finite_scores_with_representable_mean_do_not_overflow(self):
        path = self.write_text("unit_id,baseline,candidate\na,0,1e308\nb,0,1e308\n")
        result = self.run_cli(path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Infinity", result.stdout)


if __name__ == "__main__":
    unittest.main()
