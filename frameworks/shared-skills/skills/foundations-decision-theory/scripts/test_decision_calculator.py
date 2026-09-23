#!/usr/bin/env python3
"""Known-answer and contract tests for decision_calculator.py."""

from __future__ import annotations

import copy
import importlib.util
import json
import math
import subprocess
import sys
import tempfile
import unittest
from decimal import Decimal
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
FIXTURE_PATH = SKILL_DIR / "data" / "finite-state-decision-fixtures.json"
SPEC = importlib.util.spec_from_file_location("decision_calculator", SCRIPT_DIR / "decision_calculator.py")
assert SPEC and SPEC.loader
decision_calculator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(decision_calculator)


class DecisionCalculatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixtures = json.loads(
            FIXTURE_PATH.read_text(encoding="utf-8"), parse_float=Decimal
        )["cases"]

    def model(self, name: str = "symmetric_75_percent_signal") -> dict:
        return copy.deepcopy(self.fixtures[name]["input"])

    def test_symmetric_signal_known_answer(self) -> None:
        result = decision_calculator.analyze(self.model())
        self.assertEqual(result["expected_utility"]["optimal_actions"], ["act", "outside"])
        self.assertAlmostEqual(result["expected_utility"]["value"], 0.0)
        self.assertAlmostEqual(result["evpi"]["value"], 0.5)
        self.assertAlmostEqual(result["sample_information"]["evsi"], 0.25)
        self.assertAlmostEqual(result["sample_information"]["net_evsi"], 0.05)
        self.assertEqual(result["sample_information"]["recommendation"], "run")
        self.assertEqual(
            result["sample_information"]["signals"]["positive"]["optimal_actions"],
            ["act"],
        )
        self.assertEqual(
            result["sample_information"]["signals"]["negative"]["optimal_actions"],
            ["outside"],
        )

    def test_uninformative_signal_has_zero_evsi_even_when_evpi_exceeds_cost(self) -> None:
        model = self.model("uninformative_signal")
        model["study_cost"] = 0.1
        result = decision_calculator.analyze(model)
        self.assertAlmostEqual(result["evpi"]["value"], 0.5)
        self.assertAlmostEqual(result["sample_information"]["evsi"], 0.0)
        self.assertEqual(result["sample_information"]["recommendation"], "skip")

    def test_perfect_signal_evsi_equals_evpi(self) -> None:
        result = decision_calculator.analyze(self.model("perfect_signal"))
        self.assertAlmostEqual(result["sample_information"]["evsi"], result["evpi"]["value"])
        self.assertEqual(result["sample_information"]["recommendation"], "indifferent")

    def test_regret_ties_do_not_require_probabilities(self) -> None:
        result = decision_calculator.analyze(self.model("regret_tie_without_prior"))
        self.assertIsNone(result["expected_utility"])
        self.assertIsNone(result["evpi"])
        self.assertEqual(result["minimax_regret"]["value"], 2.0)
        self.assertEqual(result["minimax_regret"]["optimal_actions"], ["left", "right"])

    def test_one_action_noisy_study_has_exactly_zero_evpi_and_evsi(self) -> None:
        model = {
            "states": ["x", "y"],
            "actions": ["only"],
            "utilities": {"only": {"x": 1, "y": 2}},
            "prior": {"x": Decimal("0.1"), "y": Decimal("0.9")},
            "signal_likelihoods": {
                "yes": {"x": Decimal("0.2"), "y": Decimal("0.8")},
                "no": {"x": Decimal("0.8"), "y": Decimal("0.2")},
            },
        }
        result = decision_calculator.analyze(model)
        self.assertEqual(result["evpi"]["value"], 0.0)
        self.assertEqual(result["sample_information"]["evsi"], 0.0)
        self.assertEqual(result["sample_information"]["recommendation"], "indifferent")

    def test_large_common_offset_does_not_create_a_false_tie(self) -> None:
        small = {
            "states": ["s"],
            "actions": ["lower", "higher"],
            "utilities": {"lower": {"s": 0.0}, "higher": {"s": 0.0005}},
            "prior": {"s": 1.0},
        }
        large = copy.deepcopy(small)
        large["utilities"] = {
            "lower": {"s": 1e12},
            "higher": {"s": 1e12 + 0.0005},
        }
        self.assertNotEqual(
            large["utilities"]["lower"]["s"], large["utilities"]["higher"]["s"]
        )
        small_result = decision_calculator.analyze(small)
        large_result = decision_calculator.analyze(large)
        self.assertEqual(small_result["expected_utility"]["optimal_actions"], ["higher"])
        self.assertEqual(large_result["expected_utility"]["optimal_actions"], ["higher"])
        self.assertEqual(large_result["minimax_regret"]["optimal_actions"], ["higher"])

    def test_smallest_positive_float_remains_distinct_from_zero(self) -> None:
        tiny = math.nextafter(0.0, 1.0)
        model = {
            "states": ["s"],
            "actions": ["zero", "tiny"],
            "utilities": {"zero": {"s": 0.0}, "tiny": {"s": tiny}},
            "prior": {"s": 1.0},
        }
        result = decision_calculator.analyze(model)
        self.assertEqual(result["expected_utility"]["optimal_actions"], ["tiny"])
        self.assertEqual(result["minimax_regret"]["optimal_actions"], ["tiny"])
        self.assertEqual(result["minimax_regret"]["regret_matrix"]["zero"]["s"], tiny)

    def test_impossible_signal_is_retained_without_posterior(self) -> None:
        model = self.model()
        model["signal_likelihoods"]["impossible"] = {"gain": 0, "loss": 0}
        result = decision_calculator.analyze(model)
        impossible = result["sample_information"]["signals"]["impossible"]
        self.assertTrue(impossible["impossible"])
        self.assertIsNone(impossible["posterior"])
        self.assertEqual(impossible["optimal_actions"], [])
        self.assertAlmostEqual(result["sample_information"]["evsi"], 0.25)

    def test_action_independent_state_offsets_preserve_choices_and_information_values(self) -> None:
        base = decision_calculator.analyze(self.model())
        shifted_model = self.model()
        offsets = {"gain": 10.0, "loss": -3.0}
        for action in shifted_model["actions"]:
            for state in shifted_model["states"]:
                shifted_model["utilities"][action][state] += offsets[state]
        shifted = decision_calculator.analyze(shifted_model)
        self.assertEqual(
            shifted["expected_utility"]["optimal_actions"],
            base["expected_utility"]["optimal_actions"],
        )
        self.assertEqual(
            shifted["minimax_regret"]["optimal_actions"],
            base["minimax_regret"]["optimal_actions"],
        )
        self.assertAlmostEqual(shifted["evpi"]["value"], base["evpi"]["value"])
        self.assertAlmostEqual(
            shifted["sample_information"]["evsi"], base["sample_information"]["evsi"]
        )

    def test_positive_utility_scale_scales_values_and_preserves_choices(self) -> None:
        base = decision_calculator.analyze(self.model())
        scaled_model = self.model()
        factor = 7
        scaled_model["study_cost"] *= factor
        for action in scaled_model["actions"]:
            for state in scaled_model["states"]:
                scaled_model["utilities"][action][state] *= factor
        scaled = decision_calculator.analyze(scaled_model)
        self.assertEqual(
            scaled["expected_utility"]["optimal_actions"],
            base["expected_utility"]["optimal_actions"],
        )
        self.assertAlmostEqual(scaled["evpi"]["value"], factor * base["evpi"]["value"])
        self.assertAlmostEqual(
            scaled["sample_information"]["evsi"],
            factor * base["sample_information"]["evsi"],
        )
        self.assertAlmostEqual(
            scaled["minimax_regret"]["value"],
            factor * base["minimax_regret"]["value"],
        )
        self.assertEqual(
            scaled["sample_information"]["recommendation"],
            base["sample_information"]["recommendation"],
        )

    def test_rejects_probability_sum_instead_of_normalizing(self) -> None:
        model = self.model()
        model["prior"] = {"gain": 0.6, "loss": 0.6}
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "sum to 1"):
            decision_calculator.analyze(model)

    def test_rejects_near_unit_prior_instead_of_tolerating_or_normalizing(self) -> None:
        model = self.model()
        model["prior"] = {"gain": Decimal("0.5"), "loss": Decimal("0.5000000000005")}
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "sum to 1"):
            decision_calculator.analyze(model)

    def test_rejects_signal_likelihood_sum_error(self) -> None:
        model = self.model()
        model["signal_likelihoods"]["positive"]["gain"] = 0.8
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "conditional on state"):
            decision_calculator.analyze(model)

    def test_rejects_bool_and_nonfinite_numbers(self) -> None:
        for bad in (True, math.nan, math.inf, -math.inf, 10**400):
            with self.subTest(bad=bad):
                model = self.model()
                model["utilities"]["act"]["gain"] = bad
                with self.assertRaises(decision_calculator.DecisionInputError):
                    decision_calculator.analyze(model)

    def test_rejects_malformed_matrix_and_names(self) -> None:
        missing_cell = self.model()
        del missing_cell["utilities"]["act"]["loss"]
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "invalid keys"):
            decision_calculator.analyze(missing_cell)
        duplicate_name = self.model()
        duplicate_name["states"] = ["gain", "gain"]
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "duplicate"):
            decision_calculator.analyze(duplicate_name)
        blank_name = self.model()
        blank_name["actions"] = ["act", " "]
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "trimmed string"):
            decision_calculator.analyze(blank_name)

    def test_rejects_signals_or_cost_without_required_context(self) -> None:
        signal_without_prior = self.model()
        del signal_without_prior["prior"]
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "prior is required"):
            decision_calculator.analyze(signal_without_prior)
        cost_without_signal = self.model()
        del cost_without_signal["signal_likelihoods"]
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "signal_likelihoods"):
            decision_calculator.analyze(cost_without_signal)

    def test_rejects_negative_cost_unknown_keys_and_overflow(self) -> None:
        negative_cost = self.model()
        negative_cost["study_cost"] = -1
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "non-negative"):
            decision_calculator.analyze(negative_cost)
        unknown = self.model()
        unknown["notes"] = "silently ignored fields hide contract errors"
        with self.assertRaisesRegex(decision_calculator.DecisionInputError, "unexpected keys"):
            decision_calculator.analyze(unknown)
        overflow = self.model()
        overflow["utilities"]["act"] = {"gain": 1e308, "loss": -1e308}
        overflow["utilities"]["outside"]["gain"] = -1e308
        with self.assertRaisesRegex(
            decision_calculator.DecisionInputError, "cannot be represented as a finite JSON number"
        ):
            decision_calculator.analyze(overflow)

    def test_cli_reads_file_and_reports_invalid_input_with_exit_two(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            input_path = Path(temporary_directory) / "model.json"
            input_path.write_text(json.dumps(self.model(), default=float), encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "decision_calculator.py"), str(input_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            result = json.loads(completed.stdout)
            self.assertAlmostEqual(result["sample_information"]["evsi"], 0.25)

            input_path.write_text('{"states": ["only"]}', encoding="utf-8")
            failed = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "decision_calculator.py"), str(input_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(failed.returncode, 2)
            self.assertTrue(failed.stderr.startswith("error:"))

            input_path.write_text(
                '{"states":["s"],"actions":["a"],'
                '"utilities":{"a":{"s":1,"s":2}}}',
                encoding="utf-8",
            )
            duplicate = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "decision_calculator.py"), str(input_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(duplicate.returncode, 2)
            self.assertIn("duplicate JSON object key", duplicate.stderr)

            huge_integer = "1" + ("0" * 400)
            input_path.write_text(
                '{"states":["s"],"actions":["a"],'
                '"utilities":{"a":{"s":' + huge_integer + '}},"prior":{"s":1}}',
                encoding="utf-8",
            )
            too_large = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "decision_calculator.py"), str(input_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(too_large.returncode, 2)
            self.assertIn("cannot be represented as a finite JSON number", too_large.stderr)
            self.assertNotIn("Traceback", too_large.stderr)

            input_path.write_text(
                '{"states":["s"],"actions":["zero","tiny"],'
                '"utilities":{"zero":{"s":0},"tiny":{"s":1e-400}},'
                '"prior":{"s":1}}',
                encoding="utf-8",
            )
            underflow = subprocess.run(
                [sys.executable, str(SCRIPT_DIR / "decision_calculator.py"), str(input_path)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(underflow.returncode, 2)
            self.assertIn("underflows to zero as a JSON number", underflow.stderr)
            self.assertNotIn("Traceback", underflow.stderr)


if __name__ == "__main__":
    unittest.main()
