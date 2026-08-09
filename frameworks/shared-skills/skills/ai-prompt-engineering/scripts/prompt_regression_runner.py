#!/usr/bin/env python3
"""
prompt_regression_runner.py — Prompt regression suite runner (stdlib-only).

Reads a JSONL regression suite where each record specifies a prompt variant,
expected golden substrings, and an optional JSON schema. Validates pre-collected
actual outputs — does NOT call any LLM API.

Usage:
    python prompt_regression_runner.py --input suite.jsonl
    python prompt_regression_runner.py --input suite.jsonl --output report.json --verbose
    python prompt_regression_runner.py --input suite.jsonl --filter-variant v2
    python prompt_regression_runner.py --help

Input JSONL format (one JSON object per line):
    {
      "variant_id": "cot-v2",
      "prompt": "Think step by step. What is 17 * 13?",
      "actual": "Let me work through this: 17 * 13 = 221.",
      "golden_substrings": ["221"],
      "schema": {"type": "object", "properties": {"answer": {"type": "number"}}}
    }

Fields:
    variant_id        — prompt variant identifier (used in grouping/filtering)
    prompt            — the full prompt text (stored for traceability)
    actual            — the model's actual output string
    golden_substrings — list of strings that must all appear case-insensitively in actual
    schema            — optional JSON Schema dict; actual is parsed as JSON and validated

Exit code: 0 if all pass, 1 if any fail, 2 on input error.
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Minimal JSON Schema validator (stdlib-only)
# ---------------------------------------------------------------------------

def _validate_schema(value, schema: dict, path: str = "$") -> list[str]:
    errors: list[str] = []
    if not isinstance(schema, dict):
        return errors

    type_map = {
        "string": str,
        "number": (int, float),
        "integer": int,
        "boolean": bool,
        "array": list,
        "object": dict,
        "null": type(None),
    }
    expected_type = schema.get("type")
    if expected_type:
        expected_py = type_map.get(expected_type)
        if expected_py and not isinstance(value, expected_py):
            errors.append(f"{path}: expected {expected_type}, got {type(value).__name__}")
            return errors

    if isinstance(value, dict):
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property '{key}'")
        for key, sub in schema.get("properties", {}).items():
            if key in value:
                errors.extend(_validate_schema(value[key], sub, f"{path}.{key}"))

    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(value):
                errors.extend(_validate_schema(item, item_schema, f"{path}[{i}]"))

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        errors.append(f"{path}: {repr(value)} not in enum {enum}")

    return errors


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate(record: dict) -> tuple[bool, list[str]]:
    actual = record.get("actual", "")
    failures: list[str] = []

    for sub in record.get("golden_substrings", []):
        if sub.lower() not in actual.lower():
            failures.append(f"missing golden substring: {repr(sub)}")

    schema = record.get("schema")
    if schema:
        try:
            parsed = json.loads(actual)
            errs = _validate_schema(parsed, schema)
            failures.extend(errs)
        except json.JSONDecodeError as e:
            failures.append(f"actual is not valid JSON: {e}")

    return len(failures) == 0, failures


def run(
    input_path: Path,
    output_path: Path | None,
    variant_filter: str | None,
    verbose: bool,
) -> int:
    records: list[tuple[int, dict]] = []
    try:
        with input_path.open() as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append((lineno, json.loads(line)))
                except json.JSONDecodeError as e:
                    print(f"[WARN] line {lineno}: skipped — {e}", file=sys.stderr)
    except FileNotFoundError:
        print(f"[ERROR] File not found: {input_path}", file=sys.stderr)
        return 2

    if not records:
        print("[ERROR] No valid records in input.", file=sys.stderr)
        return 2

    if variant_filter:
        records = [(ln, r) for ln, r in records if r.get("variant_id", "") == variant_filter]
        if not records:
            print(f"[ERROR] No records match variant_id={variant_filter!r}", file=sys.stderr)
            return 2

    results: list[dict] = []
    variant_stats: dict[str, dict] = {}
    passed_total = 0

    for lineno, record in records:
        passed, failures = evaluate(record)
        if passed:
            passed_total += 1
        vid = record.get("variant_id", f"line-{lineno}")
        if vid not in variant_stats:
            variant_stats[vid] = {"passed": 0, "total": 0}
        variant_stats[vid]["total"] += 1
        if passed:
            variant_stats[vid]["passed"] += 1

        entry = {
            "lineno": lineno,
            "variant_id": vid,
            "passed": passed,
            "failures": failures,
        }
        results.append(entry)

        if verbose:
            status = "PASS" if passed else "FAIL"
            detail = "" if passed else f" — {'; '.join(failures)}"
            print(f"[{status}] {vid}{detail}")

    total = len(results)
    pass_rate = passed_total / total if total > 0 else 0.0
    print(f"\nResults: {passed_total}/{total} passed  ({pass_rate:.1%})")

    if len(variant_stats) > 1:
        print("\nBy variant:")
        for vid, s in sorted(variant_stats.items()):
            vr = s["passed"] / s["total"] if s["total"] > 0 else 0.0
            print(f"  {vid:<30} {s['passed']}/{s['total']} ({vr:.1%})")

    report = {
        "total": total,
        "passed": passed_total,
        "failed": total - passed_total,
        "pass_rate": round(pass_rate, 4),
        "by_variant": {
            k: {**v, "pass_rate": round(v["passed"] / v["total"], 4) if v["total"] else 0}
            for k, v in variant_stats.items()
        },
        "results": results,
    }

    if output_path:
        with output_path.open("w") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to: {output_path}")

    return 0 if pass_rate == 1.0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Prompt regression runner — validates pre-collected outputs against golden sets.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, type=Path, help="JSONL regression suite")
    parser.add_argument("--output", type=Path, default=None, help="Output JSON report")
    parser.add_argument("--filter-variant", metavar="VARIANT_ID", help="Only run records with this variant_id")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-record results")
    args = parser.parse_args()
    sys.exit(run(args.input, args.output, args.filter_variant, args.verbose))


if __name__ == "__main__":
    main()
