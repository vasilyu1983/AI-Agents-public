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
    python prompt_regression_runner.py --input repeats.jsonl --min-pass-rate 0.8
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
    schema            — JSON Schema dict; actual is parsed as JSON and validated
    case_id           — optional; records sharing a case_id within a variant are
                        repeated runs of one case and get a per-case pass rate
    must_pass         — optional bool; if this run fails, its case fails the gate
                        whatever its pass rate

Every record must have a string `actual` and at least one assertion: a
`golden_substrings` list of non-blank strings, or a `schema` that can reject some
value. A record with no assertion, or with an empty substring (which
matches everything), would pass vacuously, so it is rejected as an input error,
as is any line that is not a JSON object.

The schema check supports only: type (a name or a list such as ["string","null"]),
properties, required, additionalProperties (true/false), enum, const, items,
minLength, maxLength, minimum, maximum, anyOf, plus the annotations description,
title, $schema, default and examples. Any other keyword or type name is an input
error, never silently ignored. true/false never count as numbers.

Gate: each case (variant_id + case_id) passes when its pass rate across repeats
is at least --min-pass-rate (default 1.0) and no must_pass run failed. Set the
rate from the baseline's run-to-run variance, measured with the same k and settings.

Exit code: 0 if every case passes the gate, 1 if any case fails it, 2 on input
error (the message names the line).
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
# Evaluation
# ---------------------------------------------------------------------------

def validate_record(record) -> str | None:
    """Return an error message if the record cannot be evaluated, else None."""
    if not isinstance(record, dict):
        return f"record must be a JSON object, got {type(record).__name__}"
    if "actual" not in record:
        return "missing required field 'actual'"
    if not isinstance(record["actual"], str):
        return "field 'actual' must be a string"
    golden = record.get("golden_substrings")
    schema = record.get("schema")
    if golden is not None and (
        not isinstance(golden, list) or not all(isinstance(g, str) for g in golden)
    ):
        return "field 'golden_substrings' must be a list of strings"
    if golden and not all(g.strip() for g in golden):
        # "" is a substring of every output, so it would pass vacuously.
        return "field 'golden_substrings' must not contain empty or whitespace-only strings"
    if schema is not None and not isinstance(schema, dict):
        return "field 'schema' must be a JSON object"
    if schema is not None:
        schema_errors = check_schema(schema)
        if schema_errors:
            return "; ".join(schema_errors)
    if not golden and not schema_asserts(schema):
        return (
            "record has no assertions: add a non-empty 'golden_substrings' list "
            "or a 'schema' that can reject some value (it would otherwise pass vacuously)"
        )
    if "variant_id" in record and not (isinstance(record["variant_id"], str) and record["variant_id"]):
        return "field 'variant_id' must be a non-empty string"
    if "case_id" in record and not (isinstance(record["case_id"], str) and record["case_id"]):
        return "field 'case_id' must be a non-empty string"
    if "must_pass" in record and not isinstance(record["must_pass"], bool):
        return "field 'must_pass' must be true or false"
    return None


def evaluate(record: dict) -> tuple[bool, list[str]]:
    actual = record.get("actual", "")
    failures: list[str] = []

    for sub in record.get("golden_substrings", []):
        if sub.lower() not in actual.lower():
            failures.append(f"missing golden substring: {repr(sub)}")

    schema = record.get("schema")
    if schema:
        try:
            parsed = parse_json_strict(actual)
        except ValueError as e:
            failures.append(f"actual is not valid JSON: {e}")
        else:
            failures.extend(_validate_schema(parsed, schema))

    return len(failures) == 0, failures


def run(
    input_path: Path,
    output_path: Path | None,
    variant_filter: str | None,
    verbose: bool,
    min_pass_rate: float = 1.0,
) -> int:
    records: list[tuple[int, dict]] = []
    input_errors: list[str] = []
    try:
        with input_path.open(encoding="utf-8") as f:
            for lineno, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    records.append((lineno, json.loads(line)))
                except json.JSONDecodeError as e:
                    input_errors.append(f"line {lineno}: invalid JSON — {e}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {input_path}", file=sys.stderr)
        return 2
    except (OSError, UnicodeDecodeError) as e:
        print(f"[ERROR] Cannot read {input_path} as UTF-8 JSONL: {e}", file=sys.stderr)
        return 2

    for lineno, record in records:
        err = validate_record(record)
        if err:
            input_errors.append(f"line {lineno}: {err}")
    if input_errors:
        for msg in input_errors:
            print(f"[ERROR] {msg}", file=sys.stderr)
        print(f"[ERROR] {len(input_errors)} invalid record(s); no results reported.", file=sys.stderr)
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
    # Repeated runs of one case share a case_id; a record without one is its own case.
    case_stats: dict[str, dict[str, dict]] = {}
    passed_total = 0

    for lineno, record in records:
        passed, failures = evaluate(record)
        if passed:
            passed_total += 1
        # Repeats of a case that names no variant still belong together; "" cannot
        # collide with a real variant_id (validated non-empty) and --filter-variant ""
        # selects it.
        vid = record.get("variant_id", "" if "case_id" in record else f"line-{lineno}")
        if vid not in variant_stats:
            variant_stats[vid] = {"passed": 0, "total": 0}
        variant_stats[vid]["total"] += 1
        if passed:
            variant_stats[vid]["passed"] += 1
        cid = record.get("case_id", f"line-{lineno}")
        cs = case_stats.setdefault(vid, {}).setdefault(
            cid, {"passed": 0, "total": 0, "must_pass_failed": False}
        )
        cs["total"] += 1
        if passed:
            cs["passed"] += 1
        elif record.get("must_pass"):
            cs["must_pass_failed"] = True

        entry = {
            "lineno": lineno,
            "variant_id": vid,
            "case_id": cid,
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

    # Gate per case, not per run: a case passes the gate when its pass rate across
    # repeats reaches --min-pass-rate and no run flagged must_pass failed.
    gate_failures: list[str] = []
    for vid, cases in case_stats.items():
        for cid, cs in cases.items():
            cs["pass_rate"] = round(cs["passed"] / cs["total"], 4)
            if cs["passed"] / cs["total"] < min_pass_rate or cs["must_pass_failed"]:
                gate_failures.append(f"{vid}/{cid}")

    if any(cs["total"] > 1 for cases in case_stats.values() for cs in cases.values()):
        print("\nBy case (repeated runs):")
        for vid, cases in sorted(case_stats.items()):
            for cid, cs in sorted(cases.items()):
                flag = "  must_pass failed" if cs["must_pass_failed"] else ""
                print(f"  {vid}/{cid:<28} {cs['passed']}/{cs['total']} ({cs['pass_rate']:.1%}){flag}")

    if gate_failures:
        print(f"\nGate: FAIL — {len(gate_failures)} case(s) below min pass rate {min_pass_rate:.0%} "
              f"or with a failed must_pass run: {', '.join(sorted(gate_failures))}")

    report = {
        "total": total,
        "passed": passed_total,
        "failed": total - passed_total,
        "pass_rate": round(pass_rate, 4),
        "by_variant": {
            k: {**v, "pass_rate": round(v["passed"] / v["total"], 4) if v["total"] else 0}
            for k, v in variant_stats.items()
        },
        "by_case": case_stats,
        "gate": {"min_pass_rate": min_pass_rate, "failed_cases": sorted(gate_failures)},
        "results": results,
    }

    if output_path:
        with output_path.open("w") as f:
            json.dump(report, f, indent=2)
        print(f"Report written to: {output_path}")

    return 1 if gate_failures else 0


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
    parser.add_argument(
        "--min-pass-rate", type=float, default=1.0, metavar="RATE",
        help="Per-case pass rate (0-1) a case needs across its repeated runs (default 1.0: every run must pass)",
    )
    args = parser.parse_args()
    if not 0.0 <= args.min_pass_rate <= 1.0:
        parser.error("--min-pass-rate must be between 0 and 1")
    sys.exit(run(args.input, args.output, args.filter_variant, args.verbose, args.min_pass_rate))


if __name__ == "__main__":
    main()
