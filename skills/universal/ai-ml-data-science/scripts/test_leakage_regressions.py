"""Synthetic CLI regressions. ML_SCRIPT_DIR can point at saved pre-fix scripts."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

SCRIPTS = Path(os.environ.get("ML_SCRIPT_DIR", Path(__file__).resolve().parent))


def invoke(tmp_path, script, payload, suffix=".json", command=None, output=False):
    path = tmp_path / ("spec" + suffix)
    path.write_text(payload if isinstance(payload, str) else json.dumps(payload))
    args = [sys.executable, str(SCRIPTS / script)]
    if command:
        args += [command, "--input", str(path)]
    else:
        args += ["--spec", str(path)]
    if output:
        args += ["--output", str(tmp_path / "report.md")]
    return subprocess.run(args, capture_output=True, text=True)


def column_spec(**times):
    return {"target": "outcome", "columns": [{"name": "score", **times}]}


@pytest.mark.parametrize("tail", ["broken", "null", "42"])
def test_jsonl_does_not_ignore_bad_record(tmp_path, tail):
    result = invoke(tmp_path, "leakage_scan.py", json.dumps(column_spec()) + "\n" + tail, ".jsonl")
    assert result.returncode == 2
    assert "ERROR" in result.stderr and "Traceback" not in result.stderr


@pytest.mark.parametrize("spec", [{}, {"target": "outcome", "columns": []}, {"target": "outcome", "columns": [{"name": "x", "role": "featre"}]}])
def test_scanner_rejects_incomplete_schema(tmp_path, spec):
    result = invoke(tmp_path, "leakage_scan.py", spec)
    assert result.returncode == 2
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("obs,cutoff", [("2026-01-02", "2026-01-01"), ("T+31d", "T+30d"), ("T+2h", "T+60m")])
def test_later_observation_is_flagged(tmp_path, obs, cutoff):
    result = invoke(tmp_path, "leakage_scan.py", column_spec(observation_time=obs, label_time=cutoff))
    assert result.returncode == 1 and "TIME_LEAKAGE" in result.stdout


def test_prediction_cutoff_precedes_future_label(tmp_path):
    spec = column_spec(observation_time="T+1d", label_time="T+30d")
    spec["prediction_time"] = "T"
    assert invoke(tmp_path, "leakage_scan.py", spec).returncode == 1


def test_incomparable_times_are_input_error(tmp_path):
    result = invoke(tmp_path, "leakage_scan.py", column_spec(observation_time="unknown", label_time="T"))
    assert result.returncode == 2 and "Traceback" not in result.stderr


@pytest.mark.parametrize("obs,cutoff", [("T-1d", "T"), ("2026-01-01T03:00:00+03:00", "2026-01-01T01:00:00+00:00"), ("T", "T")])
def test_safe_times_pass(tmp_path, obs, cutoff):
    assert invoke(tmp_path, "leakage_scan.py", column_spec(observation_time=obs, label_time=cutoff)).returncode == 0


def model_spec():
    return {"features": [{"name": "usage"}], "prediction_timestamp_defined": True,
            "prediction_timestamp_field": "scored", "label_timestamp_field": "observed",
            "training_data": {"data_collection_date": "2026-02-01"},
            "train_val_test_split_method": "temporal",
            "split_config": {"train_end": "2026-01-01", "val_end": "2026-01-02", "test_end": "2026-01-03"}}


@pytest.mark.parametrize("command", ["leakage", "report"])
@pytest.mark.parametrize("output", [False, True])
def test_toolkit_failure_is_nonzero_in_both_output_modes(tmp_path, command, output):
    spec = model_spec()
    spec["prediction_timestamp_defined"] = False
    assert invoke(tmp_path, "ml_toolkit.py", spec, command=command, output=output).returncode == 1


@pytest.mark.parametrize("cutoffs", [{}, {"train_end": "2026-99-01", "val_end": "2027-01-01", "test_end": "2028-01-01"}, {"train_end": "2026-01-01", "val_end": "2026-01-01", "test_end": "2026-01-03"}])
def test_missing_invalid_or_equal_cutoffs_do_not_pass(tmp_path, cutoffs):
    spec = model_spec()
    spec["split_config"] = cutoffs
    assert invoke(tmp_path, "ml_toolkit.py", spec, command="leakage").returncode == 1


@pytest.mark.parametrize("spec", [{}, [], {"features": []}, {"features": [{"name": "usage"}], "prediction_timestamp_defined": "false"}])
def test_toolkit_schema_error_is_distinct(tmp_path, spec):
    result = invoke(tmp_path, "ml_toolkit.py", spec, command="leakage")
    assert result.returncode == 2 and "Traceback" not in result.stderr


def test_toolkit_complete_synthetic_spec_passes(tmp_path):
    assert invoke(tmp_path, "ml_toolkit.py", model_spec(), command="leakage").returncode == 0
