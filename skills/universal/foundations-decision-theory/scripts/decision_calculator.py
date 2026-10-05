#!/usr/bin/env python3
"""Exact finite-state decision analysis using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import math
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


EXPECTED_KEYS = {
    "states",
    "actions",
    "utilities",
    "prior",
    "signal_likelihoods",
    "study_cost",
}


class DecisionInputError(ValueError):
    """Raised when a decision model violates the input contract."""


def _number(value: Any, path: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, float, Decimal, Fraction)):
        raise DecisionInputError(f"{path} must be a finite number (booleans are invalid)")
    if isinstance(value, float) and not math.isfinite(value):
        raise DecisionInputError(f"{path} must be finite")
    if isinstance(value, Decimal) and not value.is_finite():
        raise DecisionInputError(f"{path} must be finite")
    return Fraction(value)


def _probability(value: Any, path: str) -> Fraction:
    result = _number(value, path)
    if result < 0.0 or result > 1.0:
        raise DecisionInputError(f"{path} must be between 0 and 1")
    return result


def _names(value: Any, path: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise DecisionInputError(f"{path} must be a non-empty list of names")
    names: list[str] = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item or item != item.strip():
            raise DecisionInputError(f"{path}[{index}] must be a non-empty, trimmed string")
        if item in names:
            raise DecisionInputError(f"{path} contains duplicate name {item!r}")
        names.append(item)
    return names


def _mapping(value: Any, path: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise DecisionInputError(f"{path} must be an object")
    return value


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DecisionInputError(f"duplicate JSON object key {key!r}")
        result[key] = value
    return result


def _exact_keys(mapping: Mapping[str, Any], expected: Sequence[str], path: str) -> None:
    actual = set(mapping)
    wanted = set(expected)
    missing = sorted(wanted - actual)
    extra = sorted(actual - wanted)
    if missing or extra:
        details = []
        if missing:
            details.append(f"missing {missing}")
        if extra:
            details.append(f"unexpected {extra}")
        raise DecisionInputError(f"{path} has invalid keys: {', '.join(details)}")


def _probabilities(value: Any, names: Sequence[str], path: str) -> dict[str, Fraction]:
    mapping = _mapping(value, path)
    _exact_keys(mapping, names, path)
    probabilities = {name: _probability(mapping[name], f"{path}.{name}") for name in names}
    total = sum(probabilities.values(), Fraction())
    if total != 1:
        raise DecisionInputError(f"{path} probabilities must sum to 1 (received {total!r})")
    return probabilities


def _sum(values: Sequence[Fraction], path: str) -> Fraction:
    del path
    return sum(values, Fraction())


def _product(left: Fraction, right: Fraction, path: str) -> Fraction:
    del path
    return left * right


def _difference(left: Fraction, right: Fraction, path: str) -> Fraction:
    del path
    return left - right


def _best(
    values: Mapping[str, Fraction], order: Sequence[str]
) -> tuple[Fraction, list[str]]:
    best = max(values.values())
    return best, [name for name in order if values[name] == best]


def _nonnegative_difference(left: Fraction, right: Fraction, path: str) -> Fraction:
    result = _difference(left, right, path)
    if result < 0.0:
        raise DecisionInputError(f"{path} produced an invalid negative value")
    return result


def _json_number(value: Fraction, path: str) -> float:
    try:
        result = float(value)
    except OverflowError as error:
        raise DecisionInputError(f"{path} cannot be represented as a finite JSON number") from error
    if not math.isfinite(result):
        raise DecisionInputError(f"{path} cannot be represented as a finite JSON number")
    if result == 0.0 and value != 0:
        raise DecisionInputError(f"{path} underflows to zero as a JSON number")
    return result


def _json_ready(value: Any, path: str = "result") -> Any:
    if isinstance(value, Fraction):
        return _json_number(value, path)
    if isinstance(value, dict):
        return {key: _json_ready(item, f"{path}.{key}") for key, item in value.items()}
    if isinstance(value, list):
        return [_json_ready(item, f"{path}[{index}]") for index, item in enumerate(value)]
    return value


def analyze(model: Mapping[str, Any]) -> dict[str, Any]:
    """Validate and analyze a finite action-by-state utility model."""
    root = _mapping(model, "input")
    unknown = sorted(set(root) - EXPECTED_KEYS)
    if unknown:
        raise DecisionInputError(f"input has unexpected keys: {unknown}")

    states = _names(root.get("states"), "states")
    actions = _names(root.get("actions"), "actions")
    utility_input = _mapping(root.get("utilities"), "utilities")
    _exact_keys(utility_input, actions, "utilities")
    utilities: dict[str, dict[str, Fraction]] = {}
    for action in actions:
        row = _mapping(utility_input[action], f"utilities.{action}")
        _exact_keys(row, states, f"utilities.{action}")
        utilities[action] = {
            state: _number(row[state], f"utilities.{action}.{state}") for state in states
        }

    state_best = {state: max(utilities[action][state] for action in actions) for state in states}
    regrets: dict[str, dict[str, Fraction]] = {}
    maximum_regret: dict[str, Fraction] = {}
    for action in actions:
        regrets[action] = {
            state: _difference(state_best[state], utilities[action][state], f"regret.{action}.{state}")
            for state in states
        }
        maximum_regret[action] = max(regrets[action].values())
    minimax_value = min(maximum_regret.values())
    minimax_actions = [
        action for action in actions if maximum_regret[action] == minimax_value
    ]

    output: dict[str, Any] = {
        "states": states,
        "actions": actions,
        "minimax_regret": {
            "regret_matrix": regrets,
            "maximum_regret": maximum_regret,
            "value": minimax_value,
            "optimal_actions": minimax_actions,
        },
        "expected_utility": None,
        "evpi": None,
        "sample_information": None,
    }

    has_prior = "prior" in root
    has_signals = "signal_likelihoods" in root
    has_cost = "study_cost" in root
    if not has_prior:
        if has_signals or has_cost:
            raise DecisionInputError("prior is required when signal_likelihoods or study_cost is supplied")
        return _json_ready(output)

    prior = _probabilities(root["prior"], states, "prior")
    expected: dict[str, Fraction] = {}
    for action in actions:
        terms = [
            _product(prior[state], utilities[action][state], f"expected_utility.{action}.{state}")
            for state in states
        ]
        expected[action] = _sum(terms, f"expected_utility.{action}")
    current_value, current_actions = _best(expected, actions)
    perfect_terms = [
        _product(prior[state], state_best[state], f"perfect_information.{state}")
        for state in states
    ]
    perfect_value = _sum(perfect_terms, "perfect_information.value")
    evpi = _nonnegative_difference(perfect_value, current_value, "evpi")
    output["prior"] = prior
    output["expected_utility"] = {
        "by_action": expected,
        "value": current_value,
        "optimal_actions": current_actions,
    }
    output["evpi"] = {
        "value_with_perfect_information": perfect_value,
        "value": evpi,
    }

    if not has_signals:
        if has_cost:
            raise DecisionInputError("signal_likelihoods is required when study_cost is supplied")
        return _json_ready(output)

    likelihood_input = _mapping(root["signal_likelihoods"], "signal_likelihoods")
    signals = list(likelihood_input)
    if not signals:
        raise DecisionInputError("signal_likelihoods must contain at least one named signal")
    _names(signals, "signal_likelihoods keys")
    likelihoods: dict[str, dict[str, Fraction]] = {}
    for signal in signals:
        row = _mapping(likelihood_input[signal], f"signal_likelihoods.{signal}")
        _exact_keys(row, states, f"signal_likelihoods.{signal}")
        likelihoods[signal] = {
            state: _probability(row[state], f"signal_likelihoods.{signal}.{state}")
            for state in states
        }
    for state in states:
        total = sum((likelihoods[signal][state] for signal in signals), Fraction())
        if total != 1:
            raise DecisionInputError(
                f"signal likelihoods conditional on state {state!r} must sum to 1 "
                f"(received {total!r})"
            )

    signal_results: dict[str, Any] = {}
    sampled_terms: list[Fraction] = []
    for signal in signals:
        joint = {
            state: _product(
                prior[state], likelihoods[signal][state], f"joint.{signal}.{state}"
            )
            for state in states
        }
        signal_probability = _sum(list(joint.values()), f"signal_probability.{signal}")
        if signal_probability == 0.0:
            signal_results[signal] = {
                "probability": 0.0,
                "impossible": True,
                "posterior": None,
                "expected_utility_by_action": None,
                "value": None,
                "optimal_actions": [],
            }
            continue
        posterior = {
            state: joint[state] / signal_probability
            for state in states
        }
        posterior_expected: dict[str, Fraction] = {}
        for action in actions:
            terms = [
                _product(
                    posterior[state],
                    utilities[action][state],
                    f"posterior_expected.{signal}.{action}.{state}",
                )
                for state in states
            ]
            posterior_expected[action] = _sum(
                terms, f"posterior_expected.{signal}.{action}"
            )
        posterior_value, posterior_actions = _best(posterior_expected, actions)
        sampled_terms.append(
            _product(signal_probability, posterior_value, f"sampled_value.{signal}")
        )
        signal_results[signal] = {
            "probability": signal_probability,
            "impossible": False,
            "posterior": posterior,
            "expected_utility_by_action": posterior_expected,
            "value": posterior_value,
            "optimal_actions": posterior_actions,
        }

    value_with_sample = _sum(sampled_terms, "sample_information.value")
    evsi = _nonnegative_difference(value_with_sample, current_value, "evsi")
    if evsi > evpi:
        raise DecisionInputError("evsi exceeds evpi for the supplied finite signal model")
    cost = _number(root.get("study_cost", 0.0), "study_cost")
    if cost < 0.0:
        raise DecisionInputError("study_cost must be non-negative")
    net_evsi = _difference(evsi, cost, "sample_information.net_evsi")
    if evsi == cost:
        recommendation = "indifferent"
    elif evsi > cost:
        recommendation = "run"
    else:
        recommendation = "skip"
    output["sample_information"] = {
        "likelihoods": likelihoods,
        "signals": signal_results,
        "value_with_sample_information": value_with_sample,
        "evsi": evsi,
        "study_cost": cost,
        "net_evsi": net_evsi,
        "recommendation": recommendation,
    }
    return _json_ready(output)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON model path, or - for stdin")
    parser.add_argument("--compact", action="store_true", help="emit compact JSON")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.input == "-":
            model = json.load(
                sys.stdin,
                object_pairs_hook=_strict_object,
                parse_float=Decimal,
            )
        else:
            with Path(args.input).open(encoding="utf-8") as handle:
                model = json.load(
                    handle,
                    object_pairs_hook=_strict_object,
                    parse_float=Decimal,
                )
        result = analyze(model)
    except (DecisionInputError, json.JSONDecodeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 2
    json.dump(
        result,
        sys.stdout,
        indent=None if args.compact else 2,
        separators=(",", ":") if args.compact else None,
        sort_keys=False,
        allow_nan=False,
    )
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
