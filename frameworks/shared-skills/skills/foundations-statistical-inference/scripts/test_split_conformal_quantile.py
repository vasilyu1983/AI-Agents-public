#!/usr/bin/env python3
"""Known answers and strict CLI behavior, independent of implementation formulas."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

SCRIPT = Path(__file__).resolve().with_name("split_conformal_quantile.py")


class QuantileTests(unittest.TestCase):
    def run_cli(self, raw, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], input=raw,
                              capture_output=True, text=True)

    def answer(self, raw):
        result = self.run_cli(raw)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, "")
        return json.loads(result.stdout)

    def test_known_nine_scores(self):
        result = self.answer('{"scores":[1,2,3,4,5,6,7,8,9],"alpha":0.2}')
        self.assertEqual((result["rank"], result["threshold"]), (8, "8"))

    def test_small_sample_unbounded(self):
        result = self.answer('{"scores":[2,4],"alpha":0.1}')
        self.assertEqual(result["rank"], 3)
        self.assertTrue(result["unbounded"])
        self.assertIsNone(result["threshold"])

    def test_exact_decimal_boundary(self):
        result = self.answer('{"scores":[1,2,3,4,5,6,7,8,9],"alpha":0.7}')
        self.assertEqual(result["rank"], 3)
        self.assertEqual(result["threshold"], "3")

    def test_decimal_scores_preserved(self):
        result = self.answer('{"scores":[0.123456789012345678901,0.2],"alpha":0.5}')
        self.assertEqual(result["threshold"], "0.2")

    def test_ties_shuffle_and_negative_scores(self):
        first = self.answer('{"scores":[-1,2,2,4],"alpha":0.5}')
        second = self.answer('{"scores":[4,2,-1,2],"alpha":0.5}')
        self.assertEqual(first, second)
        self.assertEqual(first["threshold"], "2")

    def test_single_observation_finite(self):
        self.assertEqual(self.answer('{"scores":[7],"alpha":0.5}')["threshold"], "7")

    def test_scientific_notation(self):
        self.assertEqual(self.answer('{"scores":[1e-300,2e-300],"alpha":5e-1}')["rank"], 2)

    def test_invalid_inputs(self):
        invalid = ["", "[]", "null", "{}", '{"scores":[],"alpha":0.1}',
                   '{"scores":[true],"alpha":0.1}', '{"scores":[1],"alpha":true}',
                   '{"scores":["1"],"alpha":0.1}', '{"scores":[1],"alpha":0}',
                   '{"scores":[1],"alpha":1}', '{"scores":[NaN],"alpha":0.1}',
                   '{"scores":[Infinity],"alpha":0.1}', '{"scores":[1],"alpha":0.1,"x":0}',
                   '{"scores":[1],"alpha":0.1,"alpha":0.2}',
                   '{"scores":[1],"alpha":0.1} {}']
        for raw in invalid:
            with self.subTest(raw=raw):
                result = self.run_cli(raw)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")
                self.assertIn("error", json.loads(result.stderr))

    def test_unknown_cli_argument(self):
        result = self.run_cli('{"scores":[1],"alpha":0.5}', "--unknown")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main()
