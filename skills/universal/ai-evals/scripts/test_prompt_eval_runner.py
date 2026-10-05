"""Pin the fail-closed behaviour of prompt_eval_runner.py.

This runner carries the same schema validator as ai-prompt-engineering's
prompt_regression_runner.py. A check that silently ignores a schema keyword, or
lets a vacuous assertion pass, reports green on output that production would
reject, so each test feeds the input that used to slip through.

Run: python3 -m pytest -q -p no:cacheprovider scripts/test_prompt_eval_runner.py
Set PROMPT_EVAL_RUNNER to test another copy of the script.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

RUNNER = Path(os.environ.get(
    "PROMPT_EVAL_RUNNER", Path(__file__).resolve().parent / "prompt_eval_runner.py"
))


def run(tmp_path, records):
    suite = tmp_path / "suite.jsonl"
    suite.write_text("\n".join(json.dumps(r) for r in records) + "\n")
    report = tmp_path / "report.json"
    proc = subprocess.run(
        [sys.executable, "-B", str(RUNNER), "--input", str(suite), "--output", str(report)],
        capture_output=True, text=True,
    )
    data = json.loads(report.read_text()) if report.exists() else None
    return proc, data


def schema_record(actual, schema):
    return {"id": "case-1", "actual": json.dumps(actual), "expected_schema": schema}


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


def test_additional_properties_false_rejects_an_extra_key(tmp_path):
    schema = {"type": "object", "properties": {"a": {"type": "string"}}, "additionalProperties": False}
    proc, data = run(tmp_path, [schema_record({"a": "x", "leak": 1}, schema)])
    assert proc.returncode == 1
    assert "leak" in " ".join(data["results"][0]["failures"])


def test_nullable_type_list_accepts_null_and_rejects_other_types(tmp_path):
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


def test_any_of_rejects_a_value_matching_no_branch(tmp_path):
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
    # Each of these accepts every value, so the case used to pass vacuously.
    proc, data = run(tmp_path, [schema_record({"a": 1}, schema)])
    assert proc.returncode == 1
    assert "no assertions" in " ".join(data["results"][0]["failures"])


def test_empty_expected_substring_is_an_input_error(tmp_path):
    # "" is in every string, so this assertion could never fail.
    proc, _ = run(tmp_path, [{"id": "a", "actual": "anything", "expected_substrings": [""]}])
    assert proc.returncode == 2
    assert "expected_substrings" in proc.stderr


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


@pytest.mark.parametrize("invalid", [None, False, 0, "", {}, "ok"])
def test_malformed_substrings_cannot_be_ignored_by_valid_schema(tmp_path, invalid):
    record = schema_record("ok", {"type": "string"})
    record["expected_substrings"] = invalid
    proc, data = run(tmp_path, [record])
    assert proc.returncode == 2
    assert "expected_substrings" in proc.stderr
    assert data is None


def test_null_schema_is_an_input_error_even_with_valid_substrings(tmp_path):
    proc, data = run(tmp_path, [{"actual": "ok", "expected_substrings": ["ok"], "expected_schema": None}])
    assert proc.returncode == 2
    assert "expected_schema" in proc.stderr
    assert data is None


@pytest.mark.parametrize("case_id", [None, False, 3, "", "   ", []])
def test_invalid_case_id_is_an_input_error(tmp_path, case_id):
    proc, data = run(tmp_path, [{"id": case_id, "actual": "ok", "expected_substrings": ["ok"]}])
    assert proc.returncode == 2
    assert "'id'" in proc.stderr
    assert data is None


@pytest.mark.parametrize("ids", [("same", "same"), (" same ", "same"), (None, "line-1")])
def test_duplicate_case_ids_cannot_inflate_the_denominator(tmp_path, ids):
    records = [{"actual": "ok", "expected_substrings": ["ok"]} for _ in ids]
    for record, case_id in zip(records, ids):
        if case_id is not None:
            record["id"] = case_id
    proc, data = run(tmp_path, records)
    assert proc.returncode == 2
    assert "duplicate case id" in proc.stderr
    assert data is None


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), float("-inf")])
def test_non_json_numeric_constant_in_suite_is_an_input_error(tmp_path, invalid):
    record = {"actual": "ok", "expected_substrings": ["ok"], "trace_metadata": invalid}
    proc, data = run(tmp_path, [record])
    assert proc.returncode == 2
    assert "not valid JSON" in proc.stderr
    assert data is None


def test_omitted_assertion_fields_and_generated_ids_remain_supported(tmp_path):
    proc, data = run(tmp_path, [
        {"actual": "ok", "expected_substrings": ["ok"]},
        {"actual": '"ok"', "expected_schema": {"type": "string"}},
    ])
    assert proc.returncode == 0, proc.stderr
    assert [item["id"] for item in data["results"]] == ["line-1", "line-2"]
