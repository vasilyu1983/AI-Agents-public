#!/usr/bin/env python3
"""Reproducible Monte Carlo cost uncertainty and Morris screening (stdlib only)."""

from __future__ import annotations

import argparse
import json
import math
import random
import statistics
import sys
from dataclasses import dataclass
from decimal import Decimal, ROUND_CEILING
from pathlib import Path
from typing import Any, Iterable


class InputError(ValueError):
    """Raised when the uncertainty model is invalid."""


def _object(value: Any, where: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{where} must be an object")
    return value


def _keys(value: dict[str, Any], allowed: set[str], required: set[str], where: str) -> None:
    missing = required - value.keys()
    unknown = value.keys() - allowed
    if missing:
        raise InputError(f"{where} missing keys: {', '.join(sorted(missing))}")
    if unknown:
        raise InputError(f"{where} has unknown keys: {', '.join(sorted(unknown))}")


def _text(value: Any, where: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{where} must be a non-empty string")
    return value.strip()


def _number(value: Any, where: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise InputError(f"{where} must be a number")
    try:
        result = float(value)
    except (OverflowError, ValueError) as exc:
        raise InputError(f"{where} is outside the supported numeric range") from exc
    if not math.isfinite(result):
        raise InputError(f"{where} must be finite")
    _assert_finite_output(result)
    return result


def _validated_weights(weights: list[float], where: str) -> list[float]:
    if not weights or any(weight <= 0 for weight in weights):
        raise InputError(f"{where} must contain positive weights")
    try:
        total = math.fsum(weights)
    except OverflowError as exc:
        raise InputError(f"{where} total is outside the supported numeric range") from exc
    if not math.isfinite(total) or total <= 0:
        raise InputError(f"{where} total must be finite and positive")
    return weights


def _integer(value: Any, where: str, minimum: int) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise InputError(f"{where} must be an integer >= {minimum}")
    return value


def _list(value: Any, where: str) -> list[Any]:
    if not isinstance(value, list):
        raise InputError(f"{where} must be an array")
    return value


def _bounds(value: Any, where: str) -> tuple[float, float]:
    items = _list(value, where)
    if len(items) != 2:
        raise InputError(f"{where} must contain [minimum, maximum]")
    low, high = (_number(items[0], f"{where}[0]"), _number(items[1], f"{where}[1]"))
    if low > high:
        raise InputError(f"{where} minimum must not exceed maximum")
    return low, high


def _provenance(value: Any, where: str) -> dict[str, str]:
    obj = _object(value, where)
    _keys(obj, {"kind", "source", "as_of"}, {"kind", "source", "as_of"}, where)
    kind = _text(obj["kind"], f"{where}.kind")
    if kind not in {"observed", "contract", "expert", "scenario", "derived"}:
        raise InputError(f"{where}.kind must be observed, contract, expert, scenario, or derived")
    return {
        "kind": kind,
        "source": _text(obj["source"], f"{where}.source"),
        "as_of": _text(obj["as_of"], f"{where}.as_of"),
    }


@dataclass(frozen=True)
class Distribution:
    kind: str
    parameters: dict[str, Any]

    def sample(self, rng: random.Random) -> float:
        if self.kind == "constant":
            return self.parameters["value"]
        if self.kind == "uniform":
            return rng.uniform(self.parameters["low"], self.parameters["high"])
        if self.kind == "triangular":
            return rng.triangular(
                self.parameters["low"], self.parameters["high"], self.parameters["mode"]
            )
        values = self.parameters["values"]
        weights = self.parameters.get("weights")
        return rng.choices(values, weights=weights, k=1)[0]

    def from_unit_interval(self, u: float) -> float:
        if self.kind == "uniform":
            return self.parameters["low"] + u * (self.parameters["high"] - self.parameters["low"])
        if self.kind == "triangular":
            low, mode, high = self.parameters["low"], self.parameters["mode"], self.parameters["high"]
            split = (mode - low) / (high - low)
            if u <= split:
                return low + math.sqrt(u * (high - low) * (mode - low))
            return high - math.sqrt((1 - u) * (high - low) * (high - mode))
        raise InputError(f"Morris screening does not support {self.kind} distributions")


@dataclass(frozen=True)
class InputSpec:
    name: str
    unit: str
    bounds: tuple[float, float]
    distribution: Distribution
    provenance: dict[str, str]
    distribution_assumption: str


@dataclass(frozen=True)
class JointGroup:
    name: str
    inputs: tuple[tuple[str, str, tuple[float, float]], ...]
    rows: tuple[tuple[tuple[float, ...], float], ...]
    provenance: dict[str, str]
    distribution_assumption: str


@dataclass(frozen=True)
class Component:
    name: str
    coefficient: float
    factors: tuple[str, ...]
    divisor: float


@dataclass(frozen=True)
class Model:
    name: str
    currency: str
    budget: float
    quantiles: tuple[float, ...]
    draws: int
    seed: int
    batches: int
    probability_se_target: float | None
    inputs: tuple[InputSpec, ...]
    joint_groups: tuple[JointGroup, ...]
    components: tuple[Component, ...]


def _distribution(value: Any, bounds: tuple[float, float], where: str) -> Distribution:
    obj = _object(value, where)
    kind = _text(obj.get("type"), f"{where}.type")
    allowed: dict[str, tuple[set[str], set[str]]] = {
        "constant": ({"type", "value"}, {"type", "value"}),
        "uniform": ({"type", "low", "high"}, {"type", "low", "high"}),
        "triangular": ({"type", "low", "mode", "high"}, {"type", "low", "mode", "high"}),
        "empirical": ({"type", "values", "weights"}, {"type", "values"}),
    }
    if kind not in allowed:
        raise InputError(f"{where}.type must be constant, uniform, triangular, or empirical")
    _keys(obj, *allowed[kind], where)
    params: dict[str, Any] = {}
    if kind == "constant":
        params["value"] = _number(obj["value"], f"{where}.value")
        support = [params["value"]]
    elif kind == "uniform":
        params["low"] = _number(obj["low"], f"{where}.low")
        params["high"] = _number(obj["high"], f"{where}.high")
        if params["low"] >= params["high"]:
            raise InputError(f"{where}.low must be less than high")
        support = [params["low"], params["high"]]
    elif kind == "triangular":
        for key in ("low", "mode", "high"):
            params[key] = _number(obj[key], f"{where}.{key}")
        if not params["low"] <= params["mode"] <= params["high"] or params["low"] == params["high"]:
            raise InputError(f"{where} requires low <= mode <= high and low < high")
        support = [params["low"], params["high"]]
    else:
        values = [_number(item, f"{where}.values[{index}]") for index, item in enumerate(_list(obj["values"], f"{where}.values"))]
        if not values:
            raise InputError(f"{where}.values must not be empty")
        params["values"] = values
        if "weights" in obj:
            weights = [_number(item, f"{where}.weights[{index}]") for index, item in enumerate(_list(obj["weights"], f"{where}.weights"))]
            if len(weights) != len(values):
                raise InputError(f"{where}.weights must be positive and match values")
            params["weights"] = _validated_weights(weights, f"{where}.weights")
        support = values
    if min(support) < bounds[0] or max(support) > bounds[1]:
        raise InputError(f"{where} support must stay within declared bounds {list(bounds)}")
    return Distribution(kind, params)


def load_model(raw: Any) -> Model:
    root = _object(raw, "root")
    allowed = {"schema_version", "model_name", "currency", "budget", "quantiles", "simulation", "independent_inputs", "joint_empirical_groups", "components"}
    required = allowed - {"joint_empirical_groups"}
    _keys(root, allowed, required, "root")
    if isinstance(root["schema_version"], bool) or root["schema_version"] != 1:
        raise InputError("schema_version must be 1")

    simulation = _object(root["simulation"], "simulation")
    _keys(simulation, {"draws", "seed", "batches", "probability_se_target"}, {"draws", "seed", "batches"}, "simulation")
    draws = _integer(simulation["draws"], "simulation.draws", 100)
    seed = _integer(simulation["seed"], "simulation.seed", 0)
    batches = _integer(simulation["batches"], "simulation.batches", 2)
    if draws < batches * 20:
        raise InputError("simulation.draws must provide at least 20 draws per batch")
    target = None
    if "probability_se_target" in simulation:
        target = _number(simulation["probability_se_target"], "simulation.probability_se_target")
        if not 0 < target < 0.5:
            raise InputError("simulation.probability_se_target must be between 0 and 0.5")

    quantiles = tuple(_number(q, f"quantiles[{i}]") for i, q in enumerate(_list(root["quantiles"], "quantiles")))
    if not quantiles or any(not 0 < q < 1 for q in quantiles) or list(quantiles) != sorted(set(quantiles)):
        raise InputError("quantiles must be unique, increasing values strictly between 0 and 1")

    inputs: list[InputSpec] = []
    names: set[str] = set()
    for index, item in enumerate(_list(root["independent_inputs"], "independent_inputs")):
        where = f"independent_inputs[{index}]"
        obj = _object(item, where)
        _keys(obj, {"name", "unit", "bounds", "distribution", "provenance", "distribution_assumption"}, {"name", "unit", "bounds", "distribution", "provenance", "distribution_assumption"}, where)
        name = _text(obj["name"], f"{where}.name")
        if name in names:
            raise InputError(f"duplicate input name: {name}")
        names.add(name)
        bounds = _bounds(obj["bounds"], f"{where}.bounds")
        inputs.append(InputSpec(name, _text(obj["unit"], f"{where}.unit"), bounds, _distribution(obj["distribution"], bounds, f"{where}.distribution"), _provenance(obj["provenance"], f"{where}.provenance"), _text(obj["distribution_assumption"], f"{where}.distribution_assumption")))

    groups: list[JointGroup] = []
    group_names: set[str] = set()
    for group_index, item in enumerate(_list(root.get("joint_empirical_groups", []), "joint_empirical_groups")):
        where = f"joint_empirical_groups[{group_index}]"
        obj = _object(item, where)
        _keys(obj, {"name", "inputs", "rows", "provenance", "distribution_assumption"}, {"name", "inputs", "rows", "provenance", "distribution_assumption"}, where)
        group_name = _text(obj["name"], f"{where}.name")
        if group_name in group_names:
            raise InputError(f"duplicate joint group name: {group_name}")
        group_names.add(group_name)
        defs: list[tuple[str, str, tuple[float, float]]] = []
        for input_index, definition in enumerate(_list(obj["inputs"], f"{where}.inputs")):
            input_where = f"{where}.inputs[{input_index}]"
            input_obj = _object(definition, input_where)
            _keys(input_obj, {"name", "unit", "bounds"}, {"name", "unit", "bounds"}, input_where)
            name = _text(input_obj["name"], f"{input_where}.name")
            if name in names:
                raise InputError(f"duplicate input name: {name}")
            names.add(name)
            defs.append((name, _text(input_obj["unit"], f"{input_where}.unit"), _bounds(input_obj["bounds"], f"{input_where}.bounds")))
        if len(defs) < 2:
            raise InputError(f"{where}.inputs must contain at least two jointly sampled inputs")
        rows: list[tuple[tuple[float, ...], float]] = []
        for row_index, row in enumerate(_list(obj["rows"], f"{where}.rows")):
            row_where = f"{where}.rows[{row_index}]"
            row_obj = _object(row, row_where)
            _keys(row_obj, {"values", "weight"}, {"values", "weight"}, row_where)
            values = tuple(_number(value, f"{row_where}.values[{i}]") for i, value in enumerate(_list(row_obj["values"], f"{row_where}.values")))
            if len(values) != len(defs):
                raise InputError(f"{row_where}.values must match the group's input count")
            for value, definition in zip(values, defs):
                if not definition[2][0] <= value <= definition[2][1]:
                    raise InputError(f"{row_where} value for {definition[0]} is outside declared bounds")
            weight = _number(row_obj["weight"], f"{row_where}.weight")
            if weight <= 0:
                raise InputError(f"{row_where}.weight must be positive")
            rows.append((values, weight))
        if len(rows) < 2:
            raise InputError(f"{where}.rows must contain at least two scenarios")
        _validated_weights([row[1] for row in rows], f"{where}.rows weights")
        groups.append(JointGroup(group_name, tuple(defs), tuple(rows), _provenance(obj["provenance"], f"{where}.provenance"), _text(obj["distribution_assumption"], f"{where}.distribution_assumption")))

    components: list[Component] = []
    component_names: set[str] = set()
    for index, item in enumerate(_list(root["components"], "components")):
        where = f"components[{index}]"
        obj = _object(item, where)
        _keys(obj, {"name", "coefficient", "factors", "divisor"}, {"name", "coefficient", "factors", "divisor"}, where)
        name = _text(obj["name"], f"{where}.name")
        if name in component_names:
            raise InputError(f"duplicate component name: {name}")
        component_names.add(name)
        coefficient = _number(obj["coefficient"], f"{where}.coefficient")
        factors = tuple(_text(factor, f"{where}.factors") for factor in _list(obj["factors"], f"{where}.factors"))
        if len(factors) != len(set(factors)):
            raise InputError(f"{where}.factors must not contain duplicates")
        unknown = set(factors) - names
        if unknown:
            raise InputError(f"{where}.factors reference unknown inputs: {', '.join(sorted(unknown))}")
        divisor = _number(obj["divisor"], f"{where}.divisor")
        if divisor <= 0:
            raise InputError(f"{where}.divisor must be positive")
        components.append(Component(name, coefficient, factors, divisor))
    if not components:
        raise InputError("components must not be empty")
    if not names and all(not component.factors for component in components):
        pass

    budget = _number(root["budget"], "budget")
    if budget < 0:
        raise InputError("budget must be non-negative")
    return Model(_text(root["model_name"], "model_name"), _text(root["currency"], "currency"), budget, quantiles, draws, seed, batches, target, tuple(inputs), tuple(groups), tuple(components))


def _evaluate(model: Model, values: dict[str, float]) -> tuple[float, dict[str, float]]:
    total = 0.0
    breakdown: dict[str, float] = {}
    for component in model.components:
        amount = component.coefficient
        for factor in component.factors:
            amount *= values[factor]
        amount /= component.divisor
        if not math.isfinite(amount):
            raise InputError(f"component {component.name} produced a non-finite cost")
        breakdown[component.name] = amount
        total += amount
    if not math.isfinite(total):
        raise InputError("total cost is non-finite")
    return total, breakdown


def _draw_values(model: Model, rng: random.Random) -> dict[str, float]:
    values = {spec.name: spec.distribution.sample(rng) for spec in model.inputs}
    for group in model.joint_groups:
        row = rng.choices(group.rows, weights=[entry[1] for entry in group.rows], k=1)[0][0]
        values.update({definition[0]: value for definition, value in zip(group.inputs, row)})
    return values


def _quantile(sorted_values: list[float], probability: float) -> float:
    position = probability * (len(sorted_values) - 1)
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return sorted_values[lower]
    fraction = position - lower
    return sorted_values[lower] * (1 - fraction) + sorted_values[upper] * fraction


def _qkey(probability: float) -> str:
    # repr is the shortest round-trippable spelling, so distinct accepted
    # binary floats cannot overwrite each other in the output object.
    return f"q_{probability!r}"


def _sample_se(values: Iterable[float]) -> float:
    items = list(values)
    return statistics.stdev(items) / math.sqrt(len(items)) if len(items) > 1 else 0.0


def _wilson(successes: int, total: int) -> list[float]:
    z = 1.959963984540054
    p = successes / total
    denominator = 1 + z * z / total
    centre = (p + z * z / (2 * total)) / denominator
    radius = z * math.sqrt(p * (1 - p) / total + z * z / (4 * total * total)) / denominator
    lower = 0.0 if successes == 0 else max(0.0, centre - radius)
    upper = 1.0 if successes == total else min(1.0, centre + radius)
    return [lower, upper]


def simulate(model: Model) -> dict[str, Any]:
    rng = random.Random(model.seed)
    totals: list[float] = []
    component_totals = {component.name: 0.0 for component in model.components}
    for _ in range(model.draws):
        total, breakdown = _evaluate(model, _draw_values(model, rng))
        totals.append(total)
        for name, amount in breakdown.items():
            component_totals[name] += amount
    ordered = sorted(totals)
    mean = statistics.fmean(totals)
    sd = statistics.stdev(totals) if len(totals) > 1 else 0.0
    exceedances = sum(value > model.budget for value in totals)
    probability = exceedances / model.draws
    qvalues = {_qkey(q): _quantile(ordered, q) for q in model.quantiles}

    batch_values: list[list[float]] = [[] for _ in range(model.batches)]
    for index, value in enumerate(totals):
        batch_values[index % model.batches].append(value)
    batch_q_se = {
        _qkey(q): _sample_se(_quantile(sorted(batch), q) for batch in batch_values)
        for q in model.quantiles
    }
    probability_se = math.sqrt(probability * (1 - probability) / model.draws)
    target_info = None
    if model.probability_se_target is not None:
        target_decimal = Decimal(str(model.probability_se_target))
        worst_case_draws = int(
            (Decimal("0.25") / (target_decimal * target_decimal)).to_integral_value(
                rounding=ROUND_CEILING
            )
        )
        target_info = {
            "target": model.probability_se_target,
            "achieved_at_estimated_probability": probability_se <= model.probability_se_target,
            "worst_case_minimum_draws": worst_case_draws,
            "worst_case_draw_requirement_met": model.draws >= worst_case_draws,
        }

    provenance = [
        {
            "input": item.name,
            "unit": item.unit,
            "distribution": item.distribution.kind,
            "distribution_assumption": item.distribution_assumption,
            "provenance": item.provenance,
        }
        for item in model.inputs
    ]
    provenance.extend(
        {
            "joint_group": group.name,
            "inputs": [definition[0] for definition in group.inputs],
            "distribution": "weighted joint empirical rows",
            "distribution_assumption": group.distribution_assumption,
            "provenance": group.provenance,
        }
        for group in model.joint_groups
    )
    result = {
        "schema_version": 1,
        "model_name": model.name,
        "currency": model.currency,
        "modeled_cost": {
            "mean": mean,
            "standard_deviation": sd,
            "minimum_draw": min(totals),
            "maximum_draw": max(totals),
            "quantiles": qvalues,
            "mean_by_component": {name: total / model.draws for name, total in component_totals.items()},
        },
        "budget": {
            "threshold": model.budget,
            "comparison": "modeled_cost > budget",
            "exceedance_probability": probability,
            "exceedance_count": exceedances,
        },
        "simulation_error": {
            "draws": model.draws,
            "seed": model.seed,
            "batches": model.batches,
            "mean_standard_error": sd / math.sqrt(model.draws),
            "exceedance_probability_standard_error": probability_se,
            "exceedance_probability_wilson_95": _wilson(exceedances, model.draws),
            "batch_quantile_standard_error_approximate": batch_q_se,
            "probability_precision_target": target_info,
            "interpretation": "These diagnostics describe Monte Carlo sampling error only; they do not validate distributions, sources, dependence, or the cost formula. Batch quantile SE is approximate and can be unstable for sparse tail quantiles or small batches.",
        },
        "assumptions": {
            "inputs": provenance,
            "dependence": {
                "independent_inputs_assumed_mutually_independent": [item.name for item in model.inputs],
                "joint_empirical_groups_preserved_by_row_resampling": [group.name for group in model.joint_groups],
                "cross_group_independence_assumed": len(model.joint_groups) + bool(model.inputs) > 1,
            },
            "model_scope": "Results are conditional on the supplied cost formula, distributions, provenance, bounds, and dependence structure.",
        },
    }
    _assert_finite_output(result)
    return result


def morris(model: Model, trajectories: int, levels: int, seed: int) -> dict[str, Any]:
    if model.joint_groups:
        raise InputError("Morris screening requires independent inputs; joint empirical groups need a dependence-aware method")
    varying = [item for item in model.inputs if item.distribution.kind != "constant"]
    unsupported = [item.name for item in varying if item.distribution.kind not in {"uniform", "triangular"}]
    if unsupported:
        raise InputError("Morris screening supports only independent uniform or triangular inputs; unsupported: " + ", ".join(unsupported))
    if not varying:
        raise InputError("Morris screening requires at least one varying input")
    if trajectories < 4:
        raise InputError("Morris trajectories must be >= 4")
    if levels < 4 or levels % 2:
        raise InputError("Morris levels must be an even integer >= 4")
    rng = random.Random(seed)
    step_count = levels // 2
    delta = step_count / (levels - 1)
    grid = [index / (levels - 1) for index in range(levels)]
    effects = {item.name: [] for item in varying}
    constants = {item.name: item.distribution.parameters["value"] for item in model.inputs if item.distribution.kind == "constant"}
    for _ in range(trajectories):
        directions = {item.name: rng.choice((-1, 1)) for item in varying}
        point: dict[str, float] = {}
        for item in varying:
            direction = directions[item.name]
            candidates = grid[step_count:] if direction < 0 else grid[:-step_count]
            point[item.name] = rng.choice(candidates)
        order = list(varying)
        rng.shuffle(order)
        values = constants | {item.name: item.distribution.from_unit_interval(point[item.name]) for item in varying}
        before, _ = _evaluate(model, values)
        for item in order:
            point[item.name] += directions[item.name] * delta
            values[item.name] = item.distribution.from_unit_interval(point[item.name])
            after, _ = _evaluate(model, values)
            effects[item.name].append((after - before) / (directions[item.name] * delta))
            before = after
    factors = []
    for item in varying:
        values = effects[item.name]
        factors.append({
            "input": item.name,
            "input_unit": item.unit,
            "effect_unit": f"{model.currency} per normalized-quantile unit",
            "mu": statistics.fmean(values),
            "mu_star": statistics.fmean(abs(value) for value in values),
            "sigma": statistics.stdev(values) if len(values) > 1 else 0.0,
            "elementary_effects": len(values),
        })
    factors.sort(key=lambda item: item["mu_star"], reverse=True)
    result = {
        "method": "Morris elementary-effects screening",
        "trajectories": trajectories,
        "levels": levels,
        "delta": delta,
        "seed": seed,
        "model_evaluations": trajectories * (len(varying) + 1),
        "factors": factors,
        "interpretation": "mu_star ranks overall effect across sampled input quantiles; sigma indicates changing elementary effects from nonlinearity or interactions and does not identify which cause.",
        "limits": "Screening varies independent continuous input quantiles. It is not Sobol variance attribution, a causal effect, or valid for the refused dependent/empirical inputs.",
    }
    _assert_finite_output(result)
    return result


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise InputError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_unique_object)
    except FileNotFoundError as exc:
        raise InputError(f"input not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from exc


def _assert_finite_output(value: Any, where: str = "output") -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise InputError(f"{where} is non-finite; reduce unsupported numeric magnitudes")
    if isinstance(value, dict):
        for key, item in value.items():
            _assert_finite_output(item, f"{where}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _assert_finite_output(item, f"{where}[{index}]")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Cost uncertainty model JSON")
    parser.add_argument("--output", type=Path, help="Write JSON here instead of stdout")
    parser.add_argument("--sensitivity", action="store_true", help="Also run Morris screening")
    parser.add_argument("--morris-trajectories", type=int, default=20)
    parser.add_argument("--morris-levels", type=int, default=6)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        model = load_model(parse_json(args.input))
        result = simulate(model)
        if args.sensitivity:
            result["sensitivity"] = morris(model, args.morris_trajectories, args.morris_levels, model.seed + 1)
        _assert_finite_output(result)
        payload = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
        if args.output:
            args.output.write_text(payload, encoding="utf-8")
        else:
            sys.stdout.write(payload)
        return 0
    except (InputError, OSError, OverflowError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
