#!/usr/bin/env python3
"""
prompt_eval_runner.py — LLM prompt regression runner (offline / stdlib-only).

Reads a JSONL regression suite and checks each record against substring
and/or JSON-schema assertions. Does NOT call any LLM API — it validates
pre-collected actual outputs. For per-call cost, see ops-cost-optimization's
cost_estimator.py.

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
    id                  — optional unique non-empty string (defaults to line-N)
    input               — the prompt text (not evaluated here, stored for traceability)
    actual              — the model's actual output string
    expected_substrings — list of strings that must all appear (case-insensitive) in actual
    expected_schema     — optional JSON Schema dict; actual is parsed as JSON and validated

Every record needs at least one assertion (expected_substrings and/or an
expected_schema that can reject some value); a record with none FAILS, because it
could never fail.

The schema check supports only: type (a name or a list such as ["string","null"]),
properties, required, additionalProperties (true/false), enum, const, items,
minLength, maxLength, minimum, maximum, anyOf, plus the annotations description,
title, $schema, default and examples. Any other keyword or type name is an input
error (exit 2), never silently ignored. true/false never count as numbers.
An empty or whitespace-only expected substring matches everything, so it is an
input error too.

Exit code: 0 if all pass, 1 if any fail, 2 on input error (missing file,
malformed JSONL line or assertion field, empty suite, unsupported schema,
empty substring, invalid/duplicate ID, or non-JSON numeric constant).
"""

import argparse
import json
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Minimal JSON Schema validator (stdlib-only, fails closed)
#
# Supported: type (a name or a list of names), properties, required,
# additionalProperties (true/false), enum, const, items, minLength, maxLength,
# minimum, maximum, anyOf. Annotations: description, title, $schema, default,
# examples. Any other keyword or type name is an input error (exit 2), because
# an ignored constraint would let invalid output pass.
# Keep this block identical in ai-prompt-engineering/scripts/prompt_regression_runner.py
# and ai-evals/scripts/prompt_eval_runner.py.
# ---------------------------------------------------------------------------

_SCHEMA_TYPES = ("string", "number", "integer", "boolean", "array", "object", "null")
_SCHEMA_ANNOTATIONS = {"description", "title", "$schema", "default", "examples"}
_SCHEMA_KEYWORDS = {
    "type", "properties", "required", "additionalProperties", "enum", "const",
    "items", "minLength", "maxLength", "minimum", "maximum", "anyOf",
} | _SCHEMA_ANNOTATIONS


def _is_number(value) -> bool:
    # bool is a subclass of int in Python, but true/false are not JSON numbers.
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _json_type(value) -> str:
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    return {str: "string", list: "array", dict: "object"}.get(type(value), "null")


def _matches_type(value, name: str) -> bool:
    if name == "integer":
        return _is_number(value) and (isinstance(value, int) or value.is_integer())
    if name == "number":
        return _is_number(value)
    if name == "boolean":
        return isinstance(value, bool)
    if name == "null":
        return value is None
    return isinstance(value, {"string": str, "array": list, "object": dict}[name])


def _json_equal(a, b) -> bool:
    """JSON equality: 1 == 1.0, but true != 1 (Python's == says True == 1)."""
    if isinstance(a, bool) or isinstance(b, bool):
        return isinstance(a, bool) and isinstance(b, bool) and a == b
    if _is_number(a) and _is_number(b):
        return a == b
    if isinstance(a, list) and isinstance(b, list):
        return len(a) == len(b) and all(_json_equal(x, y) for x, y in zip(a, b))
    if isinstance(a, dict) and isinstance(b, dict):
        return a.keys() == b.keys() and all(_json_equal(a[k], b[k]) for k in a)
    return type(a) is type(b) and a == b


def schema_asserts(schema) -> bool:
    """True if the schema can reject some value, not only annotate it.

    Vacuous forms do not count: a type list naming every type, minLength 0, empty
    required/properties, additionalProperties true, and an anyOf with any branch
    that accepts everything. This is a heuristic: keywords apply only to their own
    type, so an untyped branch such as {"minLength": 5} still admits numbers.
    """
    if not isinstance(schema, dict):
        return False
    types = schema.get("type")
    if types is not None and not (isinstance(types, list) and set(types) >= set(_SCHEMA_TYPES)):
        return True
    if schema.get("minLength", 0) > 0:
        return True
    if any(k in schema for k in ("enum", "const", "maxLength", "minimum", "maximum")):
        return True
    if schema.get("required") or schema.get("additionalProperties") is False:
        return True
    props = schema.get("properties")
    if isinstance(props, dict) and any(schema_asserts(s) for s in props.values()):
        return True
    if schema_asserts(schema.get("items")):
        return True
    branches = schema.get("anyOf")
    return isinstance(branches, list) and bool(branches) and all(schema_asserts(b) for b in branches)


def check_schema(schema, path: str = "schema") -> list[str]:
    """Return every part of the schema this validator cannot enforce (empty = usable)."""
    if not isinstance(schema, dict):
        return [f"{path}: a schema must be a JSON object, got {_json_type(schema)}"]
    errors = [
        f"{path}: unsupported keyword {k!r}; supported: {', '.join(sorted(_SCHEMA_KEYWORDS))}"
        for k in schema if k not in _SCHEMA_KEYWORDS
    ]
    if "type" in schema:
        t = schema["type"]
        names = t if isinstance(t, list) else [t]
        if not names or not all(isinstance(n, str) and n in _SCHEMA_TYPES for n in names):
            errors.append(f"{path}.type: unsupported type {t!r}; use one of {', '.join(_SCHEMA_TYPES)} or a list of them")
    if "properties" in schema:
        if not isinstance(schema["properties"], dict):
            errors.append(f"{path}.properties: must be an object mapping names to schemas")
        else:
            for key, sub in schema["properties"].items():
                errors.extend(check_schema(sub, f"{path}.properties.{key}"))
    required = schema.get("required", [])
    if not isinstance(required, list) or not all(isinstance(k, str) for k in required):
        errors.append(f"{path}.required: must be a list of strings")
    if not isinstance(schema.get("additionalProperties", True), bool):
        errors.append(f"{path}.additionalProperties: only true or false is supported")
    if "enum" in schema and not (isinstance(schema["enum"], list) and schema["enum"]):
        errors.append(f"{path}.enum: must be a non-empty list")
    if "items" in schema:
        errors.extend(check_schema(schema["items"], f"{path}.items"))
    for kw in ("minLength", "maxLength"):
        if kw in schema and not (
            isinstance(schema[kw], int) and not isinstance(schema[kw], bool) and schema[kw] >= 0
        ):
            errors.append(f"{path}.{kw}: must be a non-negative integer")
    for kw in ("minimum", "maximum"):
        if kw in schema and not _is_number(schema[kw]):
            errors.append(f"{path}.{kw}: must be a number")
    if "anyOf" in schema:
        if not (isinstance(schema["anyOf"], list) and schema["anyOf"]):
            errors.append(f"{path}.anyOf: must be a non-empty list of schemas")
        else:
            for i, sub in enumerate(schema["anyOf"]):
                errors.extend(check_schema(sub, f"{path}.anyOf[{i}]"))
    return errors


def _validate_schema(value, schema: dict, path: str = "$") -> list[str]:
    """Return validation errors (empty = valid). The schema must pass check_schema first."""
    if "type" in schema:
        names = schema["type"] if isinstance(schema["type"], list) else [schema["type"]]
        if not any(_matches_type(value, n) for n in names):
            return [f"{path}: expected {' or '.join(names)}, got {_json_type(value)}"]

    errors: list[str] = []
    if "enum" in schema and not any(_json_equal(value, e) for e in schema["enum"]):
        errors.append(f"{path}: {value!r} not in enum {schema['enum']}")
    if "const" in schema and not _json_equal(value, schema["const"]):
        errors.append(f"{path}: {value!r} does not equal const {schema['const']!r}")

    if isinstance(value, dict):
        props = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in value:
                errors.append(f"{path}: missing required property '{key}'")
        for key, sub in props.items():
            if key in value:
                errors.extend(_validate_schema(value[key], sub, f"{path}.{key}"))
        if schema.get("additionalProperties") is False:
            extra = sorted(k for k in value if k not in props)
            if extra:
                errors.append(f"{path}: unexpected properties {extra} (additionalProperties is false)")

    if isinstance(value, list) and "items" in schema:
        for i, item in enumerate(value):
            errors.extend(_validate_schema(item, schema["items"], f"{path}[{i}]"))

    if isinstance(value, str):
        if "minLength" in schema and len(value) < schema["minLength"]:
            errors.append(f"{path}: length {len(value)} is below minLength {schema['minLength']}")
        if "maxLength" in schema and len(value) > schema["maxLength"]:
            errors.append(f"{path}: length {len(value)} is above maxLength {schema['maxLength']}")

    if _is_number(value):
        if "minimum" in schema and value < schema["minimum"]:
            errors.append(f"{path}: {value} is below minimum {schema['minimum']}")
        if "maximum" in schema and value > schema["maximum"]:
            errors.append(f"{path}: {value} is above maximum {schema['maximum']}")

    if "anyOf" in schema:
        branch_errors = [_validate_schema(value, sub, path) for sub in schema["anyOf"]]
        if all(branch_errors):
            reasons = "; ".join(errs[0] for errs in branch_errors)
            errors.append(f"{path}: matches no anyOf branch ({reasons})")

    return errors


def parse_json_strict(text: str):
    """json.loads that rejects NaN and Infinity, which are not valid JSON."""
    def _reject(token):
        raise ValueError(f"{token} is not valid JSON")
    return json.loads(text, parse_constant=_reject)


# ---------------------------------------------------------------------------
# Evaluation logic
# ---------------------------------------------------------------------------

def input_error(record: dict) -> str | None:
    """Return why a record cannot be evaluated honestly (exit 2), else None."""
    if "id" in record and not (isinstance(record["id"], str) and record["id"].strip()):
        return "'id' must be a non-empty string when provided"
    substrings = record.get("expected_substrings")
    if "expected_substrings" in record and not isinstance(substrings, list):
        return "'expected_substrings' must be a list when provided"
    if isinstance(substrings, list) and not all(isinstance(s, str) and s.strip() for s in substrings):
        # "" is a substring of every output, so it would pass vacuously.
        return "'expected_substrings' must hold non-empty, non-whitespace strings"
    if "expected_schema" in record:
        schema_errors = check_schema(record["expected_schema"], "expected_schema")
        if schema_errors:
            return "; ".join(schema_errors)
    return None


def evaluate_record(record: dict) -> tuple[bool, list[str]]:
    """Return (passed, failure_reasons)."""
    failures: list[str] = []
    actual = record.get("actual")
    if not isinstance(actual, str):
        return False, ["missing or non-string 'actual' output"]

    substrings = record.get("expected_substrings") or []
    schema = record.get("expected_schema")
    if not isinstance(substrings, list):
        return False, ["'expected_substrings' must be a list"]
    # A record with no assertion cannot fail, so it must not count as a pass.
    if not substrings and not schema_asserts(schema):
        return False, ["no assertions: add expected_substrings and/or an expected_schema that can reject some value"]

    # Substring checks
    for sub in substrings:
        if sub.lower() not in actual.lower():
            failures.append(f"missing substring: {repr(sub)}")

    # JSON schema check
    if schema:
        try:
            parsed = parse_json_strict(actual)
        except ValueError as e:
            failures.append(f"actual is not valid JSON: {e}")
        else:
            failures.extend(_validate_schema(parsed, schema))

    return len(failures) == 0, failures


def run(input_path: Path, output_path: Path | None, verbose: bool) -> int:
    records: list[tuple[int, dict]] = []
    seen_ids: set[str] = set()
    try:
        with input_path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    obj = parse_json_strict(line)
                    if not isinstance(obj, dict):
                        print(f"[ERROR] line {lineno}: record must be a JSON object", file=sys.stderr)
                        return 2
                    err = input_error(obj)
                    if err:
                        print(f"[ERROR] line {lineno}: {err}", file=sys.stderr)
                        return 2
                    case_id = obj.get("id", f"line-{lineno}").strip()
                    if case_id in seen_ids:
                        print(f"[ERROR] line {lineno}: duplicate case id {case_id!r}", file=sys.stderr)
                        return 2
                    seen_ids.add(case_id)
                    obj["id"] = case_id
                    records.append((lineno, obj))
                except ValueError as e:
                    # A malformed line is a broken test case, not a skippable one.
                    print(f"[ERROR] line {lineno}: invalid JSON — {e}", file=sys.stderr)
                    return 2
    except FileNotFoundError:
        print(f"[ERROR] File not found: {input_path}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as e:
        print(f"[ERROR] Cannot read {input_path} as UTF-8 JSONL: {e}", file=sys.stderr)
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
