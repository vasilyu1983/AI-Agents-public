#!/usr/bin/env python3
"""
prompt_eval_runner.py — LLM prompt regression runner (offline / stdlib-only).

Reads a JSONL regression suite and checks each record against substring
and/or JSON-schema assertions. Does NOT call any LLM API — it validates
pre-collected actual outputs. Pair with cost_estimator.py to track cost.

Usage:
    python prompt_eval_runner.py --input suite.jsonl
    python prompt_eval_runner.py --input suite.jsonl --output report.json --verbose
    python prompt_eval_runner.py --help

Input JSONL format:
    {
      "id": "summarise-01",
      "input": "Summarise quantum computing in one sentence.",
      "actual": "Quantum computers use superposition and entanglement...",
      "expected_substrings": ["quantum", "superposition"],
      "expected_schema": {"type": "object", "properties": {"answer": {"type": "string"}}}
    }

Fields:
    id                  — unique test case identifier
    input               — the prompt text (not evaluated here, stored for traceability)
    actual              — the model's actual output string
    expected_substrings — list of strings that must all appear (case-insensitive) in actual
    expected_schema     — optional JSON Schema dict; actual is parsed as JSON and validated

Exit code: 0 if all pass, 1 if any fail, 2 on input error.
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Minimal JSON Schema validator (stdlib-only, supports type/properties/required/items)
# ---------------------------------------------------------------------------

def _validate_schema(value, schema: dict, path: str = "$") -> list[str]:
    """Return list of validation error messages (empty = valid)."""
    errors: list[str] = []
    if not isinstance(schema, dict):
        return errors

    expected_type = schema.get("type")
    if expected_type:
        type_map = {
            "string": str,
            "number": (int, float),
            "integer": int,
            "boolean": bool,
            "array": list,
            "object": dict,
            "null": type(None),
        }
        expected_py = type_map.get(expected_type)
        if expected_py and not isinstance(value, expected_py):
            errors.append(f"{path}: expected type {expected_type}, got {type(value).__name__}")
            return errors  # further checks are meaningless

    if isinstance(value, dict):
        required = schema.get("required", [])
        for key in required:
            if key not in value:
                errors.append(f"{path}: missing required property '{key}'")
        for key, sub_schema in schema.get("properties", {}).items():
            if key in value:
                errors.extend(_validate_schema(value[key], sub_schema, f"{path}.{key}"))

    if isinstance(value, list):
        item_schema = schema.get("items")
        if item_schema:
            for i, item in enumerate(value):
                errors.extend(_validate_schema(item, item_schema, f"{path}[{i}]"))

    enum = schema.get("enum")
    if enum is not None and value not in enum:
        errors.append(f"{path}: value {repr(value)} not in enum {enum}")

    return errors


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------

def evaluate_record(record: dict) -> tuple[bool, list[str]]:
    """Return (passed, failure_reasons)."""
    actual = record.get("actual", "")
    failures: list[str] = []

    # Substring checks
    for sub in record.get("expected_substrings", []):
        if sub.lower() not in actual.lower():
            failures.append(f"missing substring: {repr(sub)}")

    # JSON schema check
    schema = record.get("expected_schema")
    if schema:
        try:
            parsed = json.loads(actual)
        except json.JSONDecodeError as e:
            failures.append(f"actual is not valid JSON: {e}")
            parsed = None

        if parsed is not None:
            schema_errors = _validate_schema(parsed, schema)
            failures.extend(schema_errors)

    return len(failures) == 0, failures


def run(input_path: Path, output_path: Path | None, verbose: bool) -> int:
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
        print("[ERROR] No valid records found.", file=sys.stderr)
        return 2

    results = []
    passed_count = 0

    for lineno, record in records:
        passed, failures = evaluate_record(record)
        if passed:
            passed_count += 1
        entry = {
            "lineno": lineno,
            "id": record.get("id", f"line-{lineno}"),
            "passed": passed,
            "failures": failures,
        }
        results.append(entry)
        if verbose:
            status = "PASS" if passed else "FAIL"
            detail = ""  if passed else f" — {'; '.join(failures)}"
            print(f"[{status}] {entry['id']}{detail}")

    total = len(results)
    pass_rate = passed_count / total if total > 0 else 0.0
    summary = {
        "total": total,
        "passed": passed_count,
        "failed": total - passed_count,
        "pass_rate": round(pass_rate, 4),
        "results": results,
    }

    print(f"\nResults: {passed_count}/{total} passed  ({pass_rate:.1%})")

    if output_path:
        with output_path.open("w") as f:
            json.dump(summary, f, indent=2)
        print(f"Report written to: {output_path}")

    return 0 if pass_rate == 1.0 else 1


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Offline prompt regression runner — validates pre-collected LLM outputs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--input", required=True, type=Path, help="Input JSONL regression suite")
    parser.add_argument("--output", type=Path, default=None, help="Optional output JSON report")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print per-record results")
    args = parser.parse_args()
    sys.exit(run(args.input, args.output, args.verbose))


if __name__ == "__main__":
    main()
