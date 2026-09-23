#!/usr/bin/env python3
"""Compute E-values for risk ratios and confidence intervals."""

import argparse
import json
import math


def _validate_rr(value, name):
    value = float(value)
    if not math.isfinite(value) or value <= 0:
        raise ValueError(f"{name} must be a positive finite risk ratio")
    return value


def evalue_for_rr(rr):
    rr = _validate_rr(rr, "rr")
    try:
        scale = rr if rr >= 1 else 1 / rr
    except OverflowError as exc:
        raise ValueError("E-value exceeds the finite output range") from exc
    if not math.isfinite(scale):
        raise ValueError("E-value exceeds the finite output range")
    result = scale * (1 + math.sqrt(1 - 1 / scale))
    if not math.isfinite(result):
        raise ValueError("E-value exceeds the finite output range")
    return result


def calculate(rr, ci_low=None, ci_high=None):
    rr = _validate_rr(rr, "rr")
    result = {"risk_ratio": rr, "point_evalue": evalue_for_rr(rr)}
    if (ci_low is None) != (ci_high is None):
        raise ValueError("provide both ci_low and ci_high, or neither")
    if ci_low is None:
        return result
    low = _validate_rr(ci_low, "ci_low")
    high = _validate_rr(ci_high, "ci_high")
    if low > high or not low <= rr <= high:
        raise ValueError("require ci_low <= rr <= ci_high")
    if low <= 1 <= high:
        bound, interval_evalue = 1.0, 1.0
    elif high < 1:
        bound, interval_evalue = high, evalue_for_rr(high)
    else:
        bound, interval_evalue = low, evalue_for_rr(low)
    result["confidence_interval"] = {
        "low": low,
        "high": high,
        "bound_closest_to_null": bound,
        "evalue": interval_evalue,
    }
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rr", type=float, required=True)
    parser.add_argument("--ci-low", type=float)
    parser.add_argument("--ci-high", type=float)
    parser.add_argument("--output")
    args = parser.parse_args()
    try:
        result = calculate(args.rr, args.ci_low, args.ci_high)
    except ValueError as exc:
        parser.error(str(exc))
    rendered = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as handle:
            handle.write(rendered)
    else:
        print(rendered, end="")


if __name__ == "__main__":
    main()
