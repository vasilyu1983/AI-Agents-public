#!/usr/bin/env python3
"""Independent hand-answer and invalid-input regressions for the LP checker."""
import copy
from pathlib import Path
import subprocess
import sys
import unittest

from check_lp_certificate import check_certificate, loads


class CertificateTests(unittest.TestCase):
    def setUp(self):
        self.case = {"A": [[1, 1], [1, 0], [0, 1]], "b": [4, 2, 3],
                     "c": [3, 2], "x": [2, 2], "y": [2, 1, 0]}

    def test_optimal_hand_answer(self):
        result = check_certificate(self.case)
        self.assertTrue(result["optimal"])
        self.assertEqual((result["primal_objective"], result["dual_objective"], result["gap"]), ("10", "10", "0"))
        self.assertEqual(result["primal_slacks"], ["0", "0", "1"])
        self.assertEqual(result["dual_slacks"], ["0", "0"])

    def test_suboptimal_feasible(self):
        self.case["x"] = [1, 3]
        result = check_certificate(self.case)
        self.assertTrue(result["primal_feasible"])
        self.assertTrue(result["dual_feasible"])
        self.assertFalse(result["optimal"])
        self.assertEqual(result["gap"], "1")

    def test_zero_gap_invalid_witness(self):
        self.case["x"] = [0, 5]  # objective10, but violates two constraints
        result = check_certificate(self.case)
        self.assertEqual(result["gap"], "0")
        self.assertFalse(result["optimal"])
        self.assertEqual(result["primal_violations"], ["Ax[0]<=b[0]", "Ax[2]<=b[2]"])

    def test_dual_constraint_violation(self):
        self.case["y"] = [0, 0, 0]
        result = check_certificate(self.case)
        self.assertFalse(result["dual_feasible"])
        self.assertEqual(result["dual_slacks"], ["-3", "-2"])
        self.assertEqual(result["gap"], "-10")

    def test_negative_primal(self):
        self.case["x"] = [-1, 2]
        self.assertIn("x[0]>=0", check_certificate(self.case)["primal_violations"])

    def test_negative_dual(self):
        self.case["y"] = [3, -1, 0]
        self.assertIn("y[1]>=0", check_certificate(self.case)["dual_violations"])

    def test_decimal_exactness(self):
        result = check_certificate(loads('{"A":[[0.1]],"b":[0.03],"c":[0.2],"x":[0.3],"y":[2]}'))
        self.assertTrue(result["optimal"])
        self.assertEqual(result["primal_objective"], "3/50")

    def test_exponent_and_decimal_strings(self):
        result = check_certificate({"A": [["1e-1"]], "b": [".03"], "c": ["+0.20"], "x": ["3e-1"], "y": ["2."]})
        self.assertTrue(result["optimal"])

    def test_large_integer_not_rounded(self):
        k = 9007199254740993
        result = check_certificate({"A": [[1]], "b": [k], "c": [1], "x": [k], "y": [1]})
        self.assertEqual(result["primal_objective"], str(k))

    def test_zero_objectives(self):
        result = check_certificate({"A": [[0]], "b": [0], "c": [0], "x": [0], "y": [0]})
        self.assertTrue(result["optimal"])

    def test_negative_coefficients(self):
        result = check_certificate({"A": [[-1], [1]], "b": [-1, 2], "c": [1], "x": [2], "y": [0, 1]})
        self.assertTrue(result["optimal"])
        self.assertEqual(result["primal_slacks"], ["1", "0"])

    def test_invalid_shapes(self):
        for key, value in [("A", []), ("A", [[]]), ("A", [[1], [1, 2]]), ("A", [1]),
                           ("b", [4]), ("y", [2]), ("c", [3]), ("x", [2]), ("b", "bad")]:
            with self.subTest(key=key, value=value):
                payload = copy.deepcopy(self.case)
                payload[key] = value
                with self.assertRaises(ValueError):
                    check_certificate(payload)

    def test_invalid_scalars(self):
        for value in [True, False, None, "NaN", "Infinity", "1/3", "1+1", " 1 ", "0x10", float("nan"), {}, []]:
            with self.subTest(value=value):
                payload = copy.deepcopy(self.case)
                payload["x"][0] = value
                with self.assertRaises(ValueError):
                    check_certificate(payload)

    def test_resource_limits(self):
        for value in ["1e1001", "1e-1001", "1" * 1001]:
            self.case["x"][0] = value
            with self.assertRaises(ValueError):
                check_certificate(self.case)

    def test_strict_object(self):
        for value in [[], None, {}, {**self.case, "domain": "integer"}]:
            with self.assertRaises(ValueError):
                check_certificate(value)
        del self.case["y"]
        with self.assertRaises(ValueError):
            check_certificate(self.case)

    def test_duplicate_keys(self):
        with self.assertRaises(ValueError):
            loads('{"A":[],"A":[]}')

    def test_nonfinite_json(self):
        for value in ["NaN", "Infinity", "-Infinity"]:
            with self.assertRaises(ValueError):
                loads(value)

    def test_invalid_json(self):
        for value in ["", "{} {}", "{'A': []}"]:
            with self.assertRaises(ValueError):
                loads(value)

    def test_cli_valid(self):
        script = Path(__file__).with_name("check_lp_certificate.py")
        run = subprocess.run([sys.executable, str(script), "-"], input='{"A":[[1]],"b":[3],"c":[2],"x":[3],"y":[2]}', text=True, capture_output=True)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(loads(run.stdout)["optimal"])

    def test_cli_invalid(self):
        script = Path(__file__).with_name("check_lp_certificate.py")
        run = subprocess.run([sys.executable, str(script)], input='{"bad":true}', text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("error", loads(run.stdout))

    def test_cli_missing_file(self):
        script = Path(__file__).with_name("check_lp_certificate.py")
        run = subprocess.run([sys.executable, str(script), "/definitely-missing-lp-certificate.json"], text=True, capture_output=True)
        self.assertEqual(run.returncode, 2)
        self.assertIn("error", loads(run.stdout))


if __name__ == "__main__":
    unittest.main()
