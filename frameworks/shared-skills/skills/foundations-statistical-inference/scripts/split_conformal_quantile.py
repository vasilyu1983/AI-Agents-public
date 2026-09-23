#!/usr/bin/env python3
"""Strict stdin JSON split-conformal order statistic; no coverage certification."""
import json
import sys
from decimal import Decimal
from fractions import Fraction


def reject_constant(value):
    raise ValueError("nonfinite JSON number: " + value)


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate key: " + key)
        result[key] = value
    return result


def numeric(value, name):
    if isinstance(value, bool) or not isinstance(value, (int, Decimal)):
        raise ValueError(name + " must be a finite JSON number")
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError(name + " must be finite")
    return Fraction(value)


def calculate(payload):
    if not isinstance(payload, dict) or set(payload) != {"scores", "alpha"}:
        raise ValueError("input must contain exactly scores and alpha")
    scores = payload["scores"]
    if not isinstance(scores, list) or not scores:
        raise ValueError("scores must be a nonempty array")
    ordered = sorted((numeric(value, "score"), value) for value in scores)
    alpha = numeric(payload["alpha"], "alpha")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be strictly between zero and one")
    adjusted = (len(scores) + 1) * (1 - alpha)
    rank = -(-adjusted.numerator // adjusted.denominator)
    unbounded = rank > len(scores)
    threshold = None if unbounded else str(ordered[rank - 1][1])
    return {"n": len(scores), "rank": rank, "unbounded": unbounded,
            "threshold": threshold, "comparison": "score <= threshold"}


def main():
    try:
        if len(sys.argv) != 1:
            raise ValueError("no arguments accepted; provide JSON on stdin")
        payload = json.load(sys.stdin, parse_float=Decimal,
                            parse_constant=reject_constant,
                            object_pairs_hook=unique_object)
        print(json.dumps(calculate(payload), allow_nan=False, sort_keys=True))
        return 0
    except (ValueError, TypeError, OverflowError, RecursionError) as error:
        print(json.dumps({"error": str(error)}, allow_nan=False), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
