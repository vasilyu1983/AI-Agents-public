import unittest
import json
import subprocess
import sys

import evalue


class EValueTests(unittest.TestCase):
    def test_protective_example_uses_bound_closest_to_null(self):
        result = evalue.calculate(0.75, 0.62, 0.91)
        self.assertAlmostEqual(result["point_evalue"], 2.0, places=2)
        self.assertEqual(result["confidence_interval"]["bound_closest_to_null"], 0.91)
        self.assertAlmostEqual(result["confidence_interval"]["evalue"], 1.43, places=2)

    def test_harmful_and_null_crossing(self):
        harmful = evalue.calculate(2.0, 1.2, 3.0)
        self.assertAlmostEqual(harmful["point_evalue"], 2 + 2 ** 0.5)
        self.assertEqual(harmful["confidence_interval"]["bound_closest_to_null"], 1.2)
        crossing = evalue.calculate(1.1, 0.9, 1.4)
        self.assertEqual(crossing["confidence_interval"]["evalue"], 1.0)

    def test_invalid_inputs(self):
        for args in ((0,), (float("inf"),), (2, 0.5, 1.5), (0.8, 0.9, 0.7)):
            with self.assertRaises(ValueError):
                evalue.calculate(*args)

    def test_large_representable_evalues_avoid_intermediate_overflow(self):
        self.assertAlmostEqual(evalue.evalue_for_rr(1e200) / 1e200, 2.0)
        self.assertAlmostEqual(evalue.evalue_for_rr(1e-200) / 1e200, 2.0)

    def test_unrepresentable_evalue_fails_cleanly_at_cli(self):
        result = subprocess.run(
            [sys.executable, evalue.__file__, "--rr", "5e-324"], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("finite output range", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(result.stdout, "")

    def test_large_cli_json_remains_strict_and_finite(self):
        result = subprocess.run(
            [sys.executable, evalue.__file__, "--rr", "1e200"], capture_output=True, text=True, check=False
        )
        self.assertEqual(result.returncode, 0)
        payload = json.loads(result.stdout, parse_constant=lambda value: self.fail(value))
        self.assertAlmostEqual(payload["point_evalue"] / 1e200, 2.0)


if __name__ == "__main__":
    unittest.main()
