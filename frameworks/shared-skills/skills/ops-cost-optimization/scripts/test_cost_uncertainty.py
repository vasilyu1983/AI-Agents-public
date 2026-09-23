#!/usr/bin/env python3
"""Known-answer and validation tests for cost_uncertainty.py."""

from __future__ import annotations

import importlib.util
import io
import json
import math
import sys
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from tempfile import TemporaryDirectory


SCRIPT = Path(__file__).with_name("cost_uncertainty.py")
SPEC = importlib.util.spec_from_file_location("cost_uncertainty", SCRIPT)
assert SPEC and SPEC.loader
cost_uncertainty = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = cost_uncertainty
SPEC.loader.exec_module(cost_uncertainty)


def input_spec(name: str, distribution: dict, bounds: list[float] | None = None) -> dict:
    return {
        "name": name,
        "unit": "unit",
        "bounds": bounds or [0, 100],
        "distribution": distribution,
        "provenance": {"kind": "scenario", "source": "test fixture", "as_of": "2026-09-08"},
        "distribution_assumption": "Known-answer test assumption.",
    }


def model_raw(inputs: list[dict], components: list[dict], *, draws: int = 20000) -> dict:
    return {
        "schema_version": 1,
        "model_name": "known answer",
        "currency": "USD",
        "budget": 5,
        "quantiles": [0.1, 0.5, 0.9],
        "simulation": {"draws": draws, "seed": 1234, "batches": 10, "probability_se_target": 0.01},
        "independent_inputs": inputs,
        "joint_empirical_groups": [],
        "components": components,
    }


class SimulationTests(unittest.TestCase):
    def test_deterministic_known_answer_has_zero_model_and_mean_sampling_spread(self) -> None:
        raw = model_raw(
            [input_spec("quantity", {"type": "constant", "value": 4})],
            [{"name": "usage", "coefficient": 3, "factors": ["quantity"], "divisor": 2}],
            draws=1000,
        )
        raw["budget"] = 5.99
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        self.assertEqual(result["modeled_cost"]["mean"], 6)
        self.assertEqual(result["modeled_cost"]["standard_deviation"], 0)
        self.assertEqual(set(result["modeled_cost"]["quantiles"].values()), {6})
        self.assertEqual(result["budget"]["exceedance_probability"], 1)
        self.assertEqual(result["simulation_error"]["mean_standard_error"], 0)
        self.assertEqual(
            result["assumptions"]["inputs"][0]["provenance"],
            {"kind": "scenario", "source": "test fixture", "as_of": "2026-09-08"},
        )

    def test_distinct_close_quantiles_keep_distinct_keys(self) -> None:
        raw = model_raw(
            [input_spec("x", {"type": "uniform", "low": 0, "high": 10}, [0, 10])],
            [{"name": "cost", "coefficient": 1, "factors": ["x"], "divisor": 1}],
            draws=1000,
        )
        raw["quantiles"] = [0.1, 0.1000004]
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        quantiles = result["modeled_cost"]["quantiles"]
        self.assertEqual(set(quantiles), {"q_0.1", "q_0.1000004"})
        self.assertEqual(set(result["simulation_error"]["batch_quantile_standard_error_approximate"]), set(quantiles))

    def test_empirical_weights_recover_known_mean(self) -> None:
        raw = model_raw(
            [input_spec("x", {"type": "empirical", "values": [0, 10], "weights": [1, 3]}, [0, 10])],
            [{"name": "cost", "coefficient": 1, "factors": ["x"], "divisor": 1}],
            draws=50000,
        )
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        self.assertAlmostEqual(result["modeled_cost"]["mean"], 7.5, delta=0.06)

    def test_budget_equality_is_not_exceedance_and_wilson_keeps_uncertainty(self) -> None:
        raw = model_raw(
            [input_spec("x", {"type": "constant", "value": 5})],
            [{"name": "cost", "coefficient": 1, "factors": ["x"], "divisor": 1}],
            draws=1000,
        )
        raw["budget"] = 5
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        self.assertEqual(result["budget"]["exceedance_count"], 0)
        self.assertEqual(result["budget"]["exceedance_probability"], 0)
        self.assertEqual(result["simulation_error"]["exceedance_probability_wilson_95"][0], 0)
        self.assertGreater(result["simulation_error"]["exceedance_probability_wilson_95"][1], 0)

    def test_uniform_known_distribution(self) -> None:
        raw = model_raw(
            [input_spec("x", {"type": "uniform", "low": 0, "high": 10}, [0, 10])],
            [{"name": "cost", "coefficient": 1, "factors": ["x"], "divisor": 1}],
            draws=50000,
        )
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        self.assertAlmostEqual(result["modeled_cost"]["mean"], 5, delta=0.04)
        self.assertAlmostEqual(result["modeled_cost"]["quantiles"]["q_0.1"], 1, delta=0.06)
        self.assertAlmostEqual(result["modeled_cost"]["quantiles"]["q_0.9"], 9, delta=0.06)
        self.assertAlmostEqual(result["budget"]["exceedance_probability"], 0.5, delta=0.01)
        self.assertLess(result["simulation_error"]["exceedance_probability_standard_error"], 0.003)

    def test_seed_is_reproducible(self) -> None:
        raw = model_raw(
            [input_spec("x", {"type": "triangular", "low": 0, "mode": 2, "high": 10}, [0, 10])],
            [{"name": "cost", "coefficient": 1, "factors": ["x"], "divisor": 1}],
            draws=1000,
        )
        model = cost_uncertainty.load_model(raw)
        self.assertEqual(cost_uncertainty.simulate(model), cost_uncertainty.simulate(model))

    def test_signed_component_represents_credit(self) -> None:
        raw = model_raw(
            [
                input_spec("outflow", {"type": "constant", "value": 10}),
                input_spec("credit", {"type": "constant", "value": 3}),
            ],
            [
                {"name": "outflow", "coefficient": 1, "factors": ["outflow"], "divisor": 1},
                {"name": "credit", "coefficient": -1, "factors": ["credit"], "divisor": 1},
            ],
            draws=1000,
        )
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        self.assertEqual(result["modeled_cost"]["mean"], 7)

    def test_joint_empirical_rows_preserve_dependence(self) -> None:
        raw = model_raw([], [{"name": "usage", "coefficient": 1, "factors": ["quantity", "rate"], "divisor": 1}], draws=1000)
        raw["budget"] = 999
        raw["joint_empirical_groups"] = [{
            "name": "paired",
            "inputs": [
                {"name": "quantity", "unit": "units", "bounds": [0, 1000]},
                {"name": "rate", "unit": "USD/unit", "bounds": [0, 10]},
            ],
            "rows": [
                {"values": [100, 10], "weight": 1},
                {"values": [1000, 1], "weight": 1},
            ],
            "provenance": {"kind": "observed", "source": "paired test rows", "as_of": "2026-09-08"},
            "distribution_assumption": "Whole-row resampling.",
        }]
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        self.assertEqual(result["modeled_cost"]["minimum_draw"], 1000)
        self.assertEqual(result["modeled_cost"]["maximum_draw"], 1000)
        self.assertEqual(result["budget"]["exceedance_probability"], 1)
        self.assertEqual(result["assumptions"]["dependence"]["joint_empirical_groups_preserved_by_row_resampling"], ["paired"])
        self.assertEqual(result["assumptions"]["inputs"][0]["provenance"]["source"], "paired test rows")


class MorrisTests(unittest.TestCase):
    def test_linear_additive_known_effects(self) -> None:
        raw = model_raw(
            [
                input_spec("x", {"type": "uniform", "low": 0, "high": 1}, [0, 1]),
                input_spec("z", {"type": "uniform", "low": 0, "high": 1}, [0, 1]),
            ],
            [
                {"name": "x_cost", "coefficient": 2, "factors": ["x"], "divisor": 1},
                {"name": "z_cost", "coefficient": 4, "factors": ["z"], "divisor": 1},
            ],
            draws=1000,
        )
        result = cost_uncertainty.morris(cost_uncertainty.load_model(raw), 20, 6, 77)
        factors = {item["input"]: item for item in result["factors"]}
        self.assertAlmostEqual(factors["x"]["mu_star"], 2)
        self.assertAlmostEqual(factors["z"]["mu_star"], 4)
        self.assertAlmostEqual(factors["x"]["sigma"], 0, places=12)
        self.assertAlmostEqual(factors["z"]["sigma"], 0, places=12)
        self.assertEqual(result["factors"][0]["input"], "z")

    def test_refuses_dependent_inputs(self) -> None:
        raw = model_raw([], [{"name": "usage", "coefficient": 1, "factors": ["q", "r"], "divisor": 1}], draws=1000)
        raw["joint_empirical_groups"] = [{
            "name": "paired",
            "inputs": [
                {"name": "q", "unit": "units", "bounds": [0, 2]},
                {"name": "r", "unit": "rate", "bounds": [0, 2]},
            ],
            "rows": [{"values": [1, 2], "weight": 1}, {"values": [2, 1], "weight": 1}],
            "provenance": {"kind": "observed", "source": "test", "as_of": "2026-09-08"},
            "distribution_assumption": "paired",
        }]
        with self.assertRaisesRegex(cost_uncertainty.InputError, "requires independent inputs"):
            cost_uncertainty.morris(cost_uncertainty.load_model(raw), 10, 6, 1)

    def test_interaction_produces_varying_elementary_effects(self) -> None:
        raw = model_raw(
            [
                input_spec("x", {"type": "uniform", "low": 0, "high": 10}, [0, 10]),
                input_spec("y", {"type": "uniform", "low": 0, "high": 10}, [0, 10]),
            ],
            [{"name": "interaction", "coefficient": 1, "factors": ["x", "y"], "divisor": 1}],
            draws=1000,
        )
        result = cost_uncertainty.morris(cost_uncertainty.load_model(raw), 40, 6, 8)
        self.assertTrue(all(factor["sigma"] > 20 for factor in result["factors"]))

    def test_refuses_independent_empirical_input(self) -> None:
        raw = model_raw(
            [input_spec("x", {"type": "empirical", "values": [1, 2]})],
            [{"name": "cost", "coefficient": 1, "factors": ["x"], "divisor": 1}],
            draws=1000,
        )
        with self.assertRaisesRegex(cost_uncertainty.InputError, "unsupported: x"):
            cost_uncertainty.morris(cost_uncertainty.load_model(raw), 10, 6, 1)


class ValidationTests(unittest.TestCase):
    def valid(self) -> dict:
        return model_raw(
            [input_spec("x", {"type": "uniform", "low": 0, "high": 10}, [0, 10])],
            [{"name": "cost", "coefficient": 1, "factors": ["x"], "divisor": 1}],
            draws=1000,
        )

    def test_rejects_non_finite_input(self) -> None:
        raw = self.valid()
        raw["independent_inputs"][0]["distribution"]["high"] = math.nan
        with self.assertRaisesRegex(cost_uncertainty.InputError, "finite"):
            cost_uncertainty.load_model(raw)

    def test_rejects_boolean_schema_version(self) -> None:
        raw = self.valid()
        raw["schema_version"] = True
        with self.assertRaisesRegex(cost_uncertainty.InputError, "schema_version must be 1"):
            cost_uncertainty.load_model(raw)

    def test_rejects_duplicate_json_keys(self) -> None:
        with TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
            with self.assertRaisesRegex(cost_uncertainty.InputError, "duplicate JSON key"):
                cost_uncertainty.parse_json(path)

    def test_rejects_integer_too_large_for_float(self) -> None:
        raw = self.valid()
        raw["budget"] = 10 ** 10000
        with self.assertRaisesRegex(cost_uncertainty.InputError, "supported numeric range"):
            cost_uncertainty.load_model(raw)

    def test_tiny_probability_target_does_not_underflow(self) -> None:
        raw = self.valid()
        raw["simulation"]["probability_se_target"] = 1e-300
        result = cost_uncertainty.simulate(cost_uncertainty.load_model(raw))
        minimum = result["simulation_error"]["probability_precision_target"]["worst_case_minimum_draws"]
        self.assertGreater(minimum, 10 ** 500)

    def test_rejects_weight_total_overflow(self) -> None:
        raw = self.valid()
        raw["independent_inputs"][0]["distribution"] = {
            "type": "empirical",
            "values": [1, 2],
            "weights": [1e308, 1e308],
        }
        with self.assertRaisesRegex(cost_uncertainty.InputError, "weights total"):
            cost_uncertainty.load_model(raw)

    def test_rejects_non_finite_derived_component(self) -> None:
        raw = self.valid()
        raw["independent_inputs"][0]["distribution"] = {"type": "constant", "value": 2}
        raw["components"][0]["coefficient"] = 1e308
        model = cost_uncertainty.load_model(raw)
        with self.assertRaisesRegex(cost_uncertainty.InputError, "non-finite cost"):
            cost_uncertainty.simulate(model)

    def test_cli_returns_two_for_duplicate_json_and_numeric_overflow(self) -> None:
        with TemporaryDirectory() as directory:
            duplicate = Path(directory) / "duplicate.json"
            duplicate.write_text('{"schema_version": 1, "schema_version": 1}', encoding="utf-8")
            with redirect_stderr(io.StringIO()):
                self.assertEqual(cost_uncertainty.main(["--input", str(duplicate)]), 2)

            raw = self.valid()
            raw["independent_inputs"][0]["distribution"] = {"type": "constant", "value": 2}
            raw["components"][0]["coefficient"] = 1e308
            overflow = Path(directory) / "overflow.json"
            overflow.write_text(json.dumps(raw), encoding="utf-8")
            with redirect_stderr(io.StringIO()):
                self.assertEqual(cost_uncertainty.main(["--input", str(overflow)]), 2)

    def test_rejects_support_outside_bounds(self) -> None:
        raw = self.valid()
        raw["independent_inputs"][0]["bounds"] = [0, 5]
        with self.assertRaisesRegex(cost_uncertainty.InputError, "within declared bounds"):
            cost_uncertainty.load_model(raw)

    def test_requires_provenance(self) -> None:
        raw = self.valid()
        del raw["independent_inputs"][0]["provenance"]
        with self.assertRaisesRegex(cost_uncertainty.InputError, "missing keys: provenance"):
            cost_uncertainty.load_model(raw)

    def test_rejects_unknown_factor_and_duplicate_names(self) -> None:
        raw = self.valid()
        raw["components"][0]["factors"] = ["missing"]
        with self.assertRaisesRegex(cost_uncertainty.InputError, "unknown inputs"):
            cost_uncertainty.load_model(raw)
        raw = self.valid()
        raw["independent_inputs"].append(raw["independent_inputs"][0].copy())
        with self.assertRaisesRegex(cost_uncertainty.InputError, "duplicate input name"):
            cost_uncertainty.load_model(raw)


if __name__ == "__main__":
    unittest.main()
