#!/usr/bin/env python3
"""CLI regressions: invalid evidence cannot produce scored output files."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).with_name("product_scorer.py")
FEATURE = {"id": "F1", "name": "Feature", "reach": 100,
           "impact": 2, "confidence": 0.8, "effort_weeks": 2}
DIMENSIONS = ("problem_severity", "solution_quality", "market_timing",
              "team_market_fit", "economic_viability")


class ScorerTests(unittest.TestCase):
    def invoke(self, command, raw, assessment=None, extra=()):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "input.json"
            source.write_text(raw)
            output = base / "output"
            args = [sys.executable, str(SCRIPT), command, "--input", str(source)]
            if command in ("rice", "report"):
                args += ["--output", str(output)]
            if command == "report":
                pmf = base / "assessment.json"
                pmf.write_text(json.dumps(assessment))
                args += ["--pmf", str(pmf)]
            result = subprocess.run(args + list(extra), capture_output=True, text=True)
            return result, output.read_text() if output.exists() else None

    def assessment(self, score=3):
        return {"dimensions": {key: {"score": score} for key in DIMENSIONS}}

    def rejected(self, command, raw, **kwargs):
        result, output = self.invoke(command, raw, **kwargs)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        self.assertIsNone(output)

    def test_known_rice(self):
        result, output = self.invoke("rice", json.dumps([FEATURE]))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(output)[0]["rice_score"], 80.0)

    def test_known_opportunity_and_report(self):
        result, _ = self.invoke("pmf", json.dumps(self.assessment()))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SIGNALS", result.stdout)
        self.assertIn("not a PMF measurement", result.stdout)
        result, report = self.invoke("report", json.dumps([FEATURE]),
                                     assessment=self.assessment())
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("80.0", report)

    def test_reject_invalid_feature_numbers(self):
        for field, value in (("reach", -1), ("reach", 10001), ("reach", True),
                             ("reach", float("nan")), ("impact", True),
                             ("confidence", True), ("effort_weeks", None),
                             ("effort_weeks", "2")):
            with self.subTest(field=field, value=value):
                self.rejected("rice", json.dumps([{**FEATURE, field: value}]))

    def test_reject_invalid_feature_shapes(self):
        for payload in ([], [None], [{**FEATURE, "name": None}],
                        [{**FEATURE, "theme": []}]):
            with self.subTest(payload=payload):
                self.rejected("rice", json.dumps(payload))

    def test_reject_duplicate_keys(self):
        raw = json.dumps([FEATURE]).replace('"reach": 100', '"reach": 1, "reach": 100')
        self.rejected("rice", raw)

    def test_reject_overflow_in_preserved_extra_field(self):
        raw = json.dumps([FEATURE]).replace('"reach": 100', '"extra": 1e999, "reach": 100')
        self.rejected("rice", raw)

    def test_reject_invalid_assessments(self):
        for payload in ([], {"dimensions": []}, self.assessment(True),
                        {"dimensions": {key: None for key in DIMENSIONS}},
                        {**self.assessment(), "product_name": []}):
            with self.subTest(payload=payload):
                self.rejected("pmf", json.dumps(payload))

    def test_report_rejects_boolean_scores(self):
        self.rejected("report", json.dumps([FEATURE]), assessment=self.assessment(True))

    def test_reject_nonpositive_top(self):
        self.rejected("rice", json.dumps([FEATURE]), extra=("--top", "-1"))


if __name__ == "__main__":
    unittest.main()
