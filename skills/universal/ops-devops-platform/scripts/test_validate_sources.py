"""Offline CLI regressions; SOURCES_VALIDATOR_SCRIPT selects the old/new script."""

import copy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(os.environ.get("SOURCES_VALIDATOR_SCRIPT", Path(__file__).with_name("validate_sources.py")))
INVENTORY = Path(__file__).resolve().parents[1] / "data" / "sources.json"


def run_validator(tmp_path, data):
    path = tmp_path / "sources.json"
    path.write_text(json.dumps(data))
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--skip-network", "--path", str(path)],
        text=True, capture_output=True, check=False,
    )


def inventory():
    return json.loads(INVENTORY.read_text())


def test_inventory_including_nested_sources_passes(tmp_path):
    result = run_validator(tmp_path, inventory())
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("field,value", [
    ("name", ""), ("url", "file:///tmp/example"),
    ("description", None), ("kind", []), ("optional", "false"),
])
def test_invalid_source_is_rejected(tmp_path, field, value):
    data = inventory()
    data["kubernetes"][0][field] = value
    result = run_validator(tmp_path, data)
    assert result.returncode == 1
    assert "ERR\t" in result.stdout
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("value", [None, [], {"sources": "not-an-array"}, {"sources": [None]}])
def test_nested_container_is_checked(tmp_path, value):
    data = inventory()
    data["sota_2026"] = value
    result = run_validator(tmp_path, data)
    assert result.returncode == 1
    assert "ERR\t" in result.stdout
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("field,value", [("url", "not-a-url"), ("type", []), ("notes", "")])
def test_nested_entry_is_checked(tmp_path, field, value):
    data = inventory()
    data["sota_2026"]["sources"][0][field] = value
    result = run_validator(tmp_path, data)
    assert result.returncode == 1
    assert "ERR\t" in result.stdout


@pytest.mark.parametrize("data", [[], None, {}, {"metadata": {}}, {"docs": [None]}])
def test_invalid_inventory_fails_cleanly(tmp_path, data):
    result = run_validator(tmp_path, copy.deepcopy(data))
    assert result.returncode == 1
    assert "ERR\t" in result.stdout
    assert "Traceback" not in result.stderr


@pytest.mark.parametrize("missing", [False, True])
def test_missing_or_invalid_json_names_path(tmp_path, missing):
    path = tmp_path / "missing-or-invalid.json"
    if not missing:
        path.write_text("{")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--skip-network", "--path", str(path)],
        text=True, capture_output=True, check=False,
    )
    assert result.returncode == 1
    assert str(path) in result.stdout
    assert "ERR\t" in result.stdout
    assert "Traceback" not in result.stderr
