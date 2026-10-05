"""Pin the fail-closed behaviour of prompt_regression_runner.py.

The runner is the skill's only enforcement of the structured-output contract in
references/core-patterns.md. A check that silently ignores a schema keyword, or
lets a vacuous assertion pass, reports green on output that production would
reject, so each test feeds the input that used to slip through.

Run: python3 -m pytest -q -p no:cacheprovider scripts/test_prompt_regression_runner.py
Set PROMPT_REGRESSION_RUNNER to test another copy of the script.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RUNNER = Path(os.environ.get(
    "PROMPT_REGRESSION_RUNNER", Path(__file__).resolve().parent / "prompt_regression_runner.py"
))


def run(tmp_path, records, *args):
    suite = tmp_path / "suite.jsonl"
    suite.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    report = tmp_path / "report.json"
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--input", str(suite), "--output", str(report), *args],
        capture_output=True, text=True,
    )
    data = json.loads(report.read_text()) if report.exists() else None
    return proc, data


def schema_record(actual, schema, **extra):
    return {"variant_id": "v1", "actual": json.dumps(actual), "schema": schema, **extra}


# --- R1: the schema check fails closed -------------------------------------

def test_unsupported_keyword_is_an_input_error(tmp_path):
    # oneOf is not implemented; ignoring it would pass any value, so refuse the suite.
    schema = {"type": "object", "properties": {"s": {"oneOf": [{"const": "ok"}]}}}
    proc, _ = run(tmp_path, [schema_record({"s": "banana"}, schema)])
    assert proc.returncode == 2
    assert "oneOf" in proc.stderr


def test_unknown_type_name_is_an_input_error(tmp_path):
    # A typo such as "objekt" used to disable the type check entirely.
    proc, _ = run(tmp_path, [schema_record({"a": 1}, {"type": "objekt"})])
    assert proc.returncode == 2
    assert "objekt" in proc.stderr


def test_additional_properties_false_rejects_an_extra_key(tmp_path):
    # A closed object is how the skill keeps unexpected fields out of consumers.
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "additionalProperties": False}
    proc, data = run(tmp_path, [schema_record({"a": "x", "leak": 1}, schema)])
    assert proc.returncode == 1
    assert "leak" in " ".join(data["results"][0]["failures"])


def test_nullable_type_list_accepts_null_and_rejects_other_types(tmp_path):
    # core-patterns.md recommends nullable fields instead of forcing a guess.
    # Annotation keywords ride along: they must be allowed, not treated as unsupported.
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "title": "t",
              "description": "d", "type": "object",
              "properties": {"a": {"type": ["string", "null"], "default": None, "examples": ["x"]}}}
    proc, _ = run(tmp_path, [schema_record({"a": None}, schema)])
    assert proc.returncode == 0, proc.stderr
    proc, _ = run(tmp_path, [schema_record({"a": 3}, schema)])
    assert proc.returncode == 1


def test_true_is_not_an_integer(tmp_path):
    # bool subclasses int in Python; a JSON true in a count field is a real defect.
    schema = {"type": "object", "properties": {"n": {"type": "integer"}}}
    proc, _ = run(tmp_path, [schema_record({"n": True}, schema)])
    assert proc.returncode == 1


def test_true_does_not_match_a_numeric_enum(tmp_path):
    # Python's True == 1 must not leak into enum/const comparison.
    proc, _ = run(tmp_path, [schema_record({"n": True}, {"properties": {"n": {"enum": [1, 2]}}})])
    assert proc.returncode == 1


def test_any_of_rejects_a_value_matching_no_branch(tmp_path):
    # Discriminated unions are the skill's pattern for answer/clarify/refuse output.
    schema = {"properties": {"status": {"anyOf": [{"const": "ok"}, {"const": "error"}]}}}
    proc, _ = run(tmp_path, [schema_record({"status": "banana"}, schema)])
    assert proc.returncode == 1
    proc, _ = run(tmp_path, [schema_record({"status": "error"}, schema)])
    assert proc.returncode == 0, proc.stderr


def test_length_and_range_bounds_are_enforced(tmp_path):
    schema = {"properties": {"s": {"minLength": 5}, "n": {"maximum": 10}}}
    proc, data = run(tmp_path, [schema_record({"s": "x", "n": 11}, schema)])
    assert proc.returncode == 1
    assert len(data["results"][0]["failures"]) == 2


# --- R2: an empty golden substring is vacuous ------------------------------

def test_empty_golden_substring_is_an_input_error(tmp_path):
    # "" is in every string, so this assertion could never fail.
    proc, _ = run(tmp_path, [{"variant_id": "v1", "actual": "anything", "golden_substrings": [""]}])
    assert proc.returncode == 2
    assert "golden_substrings" in proc.stderr


# --- R3: per-case pass rate over repeated runs -----------------------------

def repeats():
    rows = []
    for case, outcomes in (("refund-01", [True, True, True]), ("refund-02", [True, False, True])):
        for ok in outcomes:
            rows.append({"variant_id": "v2", "case_id": case,
                         "actual": "refund approved" if ok else "no",
                         "golden_substrings": ["refund"]})
    return rows


def test_repeated_runs_report_a_per_case_pass_rate(tmp_path):
    # SKILL.md promises per-case pass rates; a pooled rate hides which case is flaky.
    proc, data = run(tmp_path, repeats())
    cases = data["by_case"]["v2"]
    assert cases["refund-01"]["pass_rate"] == 1.0
    assert cases["refund-02"]["pass_rate"] == round(2 / 3, 4)
    assert cases["refund-02"]["total"] == 3
    assert proc.returncode == 1  # default --min-pass-rate 1.0 keeps any failed run blocking


def test_min_pass_rate_treats_a_flake_inside_the_threshold_as_noise(tmp_path):
    # The variance-aware gate: a case above the agreed rate does not block the build.
    proc, data = run(tmp_path, repeats(), "--min-pass-rate", "0.6")
    assert proc.returncode == 0, proc.stdout
    assert data["gate"]["failed_cases"] == []
    proc, data = run(tmp_path, repeats(), "--min-pass-rate", "0.7")
    assert proc.returncode == 1
    assert data["gate"]["failed_cases"] == ["v2/refund-02"]


def test_a_failed_must_pass_run_blocks_whatever_the_rate(tmp_path):
    rows = repeats()
    rows[4]["must_pass"] = True  # the failing refund-02 run
    proc, data = run(tmp_path, rows, "--min-pass-rate", "0.5")
    assert proc.returncode == 1
    assert data["gate"]["failed_cases"] == ["v2/refund-02"]


def test_repeats_without_a_variant_id_still_group_by_case(tmp_path):
    # Each line used to become its own variant, so a flaky case read as 1/1 and 0/1.
    rows = [{k: v for k, v in r.items() if k != "variant_id"} for r in repeats()]
    proc, data = run(tmp_path, rows, "--min-pass-rate", "0.6")
    assert proc.returncode == 0, proc.stdout
    assert data["by_case"][""]["refund-02"]["total"] == 3
    # A real variant cannot share the variant-less group, and the filter can select it.
    proc, data = run(tmp_path, rows + [dict(repeats()[0], variant_id="(no variant)")])
    assert data["by_case"][""]["refund-01"]["total"] == 3
    proc, data = run(tmp_path, rows, "--filter-variant", "", "--min-pass-rate", "0.6")
    assert proc.returncode == 0, proc.stderr


@pytest.mark.parametrize("vid", [None, "", 3])
def test_variant_id_must_be_a_non_empty_string(tmp_path, vid):
    # A null variant_id next to a missing one crashed the report sort with a traceback.
    rows = [dict(repeats()[0], variant_id=vid), repeats()[1]]
    proc, _ = run(tmp_path, rows)
    assert proc.returncode == 2
    assert "variant_id" in proc.stderr and "Traceback" not in proc.stderr


@pytest.mark.parametrize("schema", [
    {"required": []},
    {"properties": {}},
    {"additionalProperties": True},
    {"properties": {"a": {"description": "only an annotation"}}},
    {"anyOf": [{"type": "string"}, {"title": "matches anything"}]},
    {"type": ["string", "number", "integer", "boolean", "array", "object", "null"]},
    {"minLength": 0},
])
def test_a_schema_that_cannot_reject_anything_is_not_an_assertion(tmp_path, schema):
    # Each of these accepts every value, so a record relying on it alone passes vacuously.
    proc, _ = run(tmp_path, [{"variant_id": "v1", "actual": "{}", "schema": schema}])
    assert proc.returncode == 2
    assert "no assertions" in proc.stderr


def test_unreadable_input_is_an_input_error(tmp_path):
    # A directory or a non-UTF-8 export used to crash with a traceback (exit 1),
    # which a CI gate cannot tell apart from a failing prompt.
    bad_bytes = tmp_path / "latin1.jsonl"
    bad_bytes.write_bytes(b'{"actual": "caf\xe9"}\n')
    for target in (tmp_path, bad_bytes):
        proc = subprocess.run([sys.executable, "-B", str(RUNNER), "--input", str(target)],
                              capture_output=True, text=True)
        assert proc.returncode == 2, (target, proc.stderr)
        assert "Traceback" not in proc.stderr
