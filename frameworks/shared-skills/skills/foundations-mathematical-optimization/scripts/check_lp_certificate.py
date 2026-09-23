#!/usr/bin/env python3
"""Verify exact witnesses for max c.x, Ax<=b,x>=0 and its min-form dual."""
import argparse
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import json
from pathlib import Path
import re
import sys

LIMITS = {"scalar_characters": 1000, "decimal_exponent_magnitude": 1000}
DECIMAL = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?\Z")


def scalar(value):
    """Parse decimal text without floating-point rounding or expression evaluation."""
    if isinstance(value, bool) or not isinstance(value, (int, Decimal, str)):
        raise ValueError("scalars must be finite numbers or decimal strings")
    raw = str(value)
    if len(raw) > LIMITS["scalar_characters"] or not DECIMAL.fullmatch(raw):
        raise ValueError("invalid decimal scalar (maximum 1000 characters)")
    try:
        number = Decimal(raw)
    except InvalidOperation as exc:
        raise ValueError("invalid decimal scalar") from exc
    if not number.is_finite() or abs(number.as_tuple().exponent) > LIMITS["decimal_exponent_magnitude"]:
        raise ValueError("scalar must be finite with exponent magnitude <=1000")
    return Fraction(number)


def vector(value, length, label):
    if not isinstance(value, list) or len(value) != length:
        raise ValueError(f"{label} must be an array of length {length}")
    return [scalar(item) for item in value]


def check_certificate(payload):
    if not isinstance(payload, dict) or set(payload) != {"A", "b", "c", "x", "y"}:
        raise ValueError("input must have exactly A, b, c, x, y")
    matrix = payload["A"]
    if not isinstance(matrix, list) or not matrix or not isinstance(matrix[0], list) or not matrix[0]:
        raise ValueError("A must be a nonempty matrix with nonempty rows")
    m, n = len(matrix), len(matrix[0])
    A = [vector(row, n, "A row") for row in matrix]
    b, y = vector(payload["b"], m, "b"), vector(payload["y"], m, "y")
    c, x = vector(payload["c"], n, "c"), vector(payload["x"], n, "x")
    dot = lambda first, second: sum((a * z for a, z in zip(first, second)), Fraction(0))
    primal_slacks = [b[i] - dot(A[i], x) for i in range(m)]
    dual_slacks = [dot([A[i][j] for i in range(m)], y) - c[j] for j in range(n)]
    primal_violations = [f"x[{j}]>=0" for j in range(n) if x[j] < 0]
    primal_violations += [f"Ax[{i}]<=b[{i}]" for i in range(m) if primal_slacks[i] < 0]
    dual_violations = [f"y[{i}]>=0" for i in range(m) if y[i] < 0]
    dual_violations += [f"A^Ty[{j}]>=c[{j}]" for j in range(n) if dual_slacks[j] < 0]
    primal, dual = dot(c, x), dot(b, y)
    return {
        "primal_feasible": not primal_violations,
        "dual_feasible": not dual_violations,
        "optimal": not primal_violations and not dual_violations and dual == primal,
        "primal_objective": str(primal), "dual_objective": str(dual), "gap": str(dual - primal),
        "primal_slacks": list(map(str, primal_slacks)), "dual_slacks": list(map(str, dual_slacks)),
        "primal_violations": primal_violations, "dual_violations": dual_violations,
    }


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"nonfinite JSON constant: {value}")


def loads(text):
    return json.loads(text, parse_float=Decimal, parse_constant=reject_constant, object_pairs_hook=unique_object)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON file or - for standard input")
    args = parser.parse_args()
    try:
        raw = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
        result = check_certificate(loads(raw))
    except (ValueError, OSError, UnicodeError, RecursionError) as exc:
        print(json.dumps({"error": str(exc)}))
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    sys.exit(main())
