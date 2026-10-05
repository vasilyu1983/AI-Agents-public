"""CLI regressions for policy-manifest input validation; no network required."""

import json
from pathlib import Path
import subprocess
import sys

import pytest


SCRIPT = Path(__file__).with_name("dep_auditor.py")


def run_cli(tmp_path, command, ecosystem):
    manifest = tmp_path / "policy.json"
    manifest.write_text(json.dumps({"ecosystems": [ecosystem]}), encoding="utf-8")
    arguments = [sys.executable, str(SCRIPT), command, "--input", str(manifest)]
    if command == "report":
        arguments += ["--output", str(tmp_path / "report.md")]
    return subprocess.run(
        arguments,
        capture_output=True, text=True, check=False,
    )


@pytest.mark.parametrize("command", ["health", "audit", "report"])
@pytest.mark.parametrize("ecosystem", [
    {"name": "nodejs"},
    {"name": 7, "dependencies": []},
    {"name": "nodejs", "dependencies": [], "lockfile_present": "false"},
    {"name": "nodejs", "dependencies": [], "security_scanning": []},
    {"name": "nodejs", "dependencies": [], "security_scanning": {"active": "false"}},
    {"name": "nodejs", "dependencies": [], "security_scanning": {"last_run_date": "9999-01-01"}},
    {"name": "nodejs", "dependencies": [], "security_scanning": {"last_run_date": 123}},
    {"name": "nodejs", "dependencies": [{"name": "pkg", "version": "1.0", "known_vulnerability": False, "days_since_update": True}]},
    {"name": "nodejs", "dependencies": [{"name": "pkg", "version": "1.0", "known_vulnerability": False, "days_since_update": -1}]},
    {"name": "nodejs", "dependencies": [{"known_vulnerability": False}]},
])
def test_malformed_declarations_fail_closed(tmp_path, command, ecosystem):
    result = run_cli(tmp_path, command, ecosystem)
    assert result.returncode == 2, result.stdout + result.stderr
    assert "Error:" in result.stderr
    assert "Traceback" not in result.stderr
    assert result.stdout == ""
    assert not (tmp_path / "report.md").exists()


@pytest.mark.parametrize("command", ["health", "audit", "report"])
def test_explicit_dependency_free_policy_is_valid(tmp_path, command):
    assert run_cli(tmp_path, command, {"name": "nodejs", "dependencies": []}).returncode == 0


@pytest.mark.parametrize("command", ["audit", "report"])
@pytest.mark.parametrize("severity, expected", [("high", 1), ("medium", 0), ("invalid", 2)])
def test_declared_flag_status_remains_distinct(tmp_path, command, severity, expected):
    ecosystem = {"name": "nodejs", "dependencies": [
        {"name": "pkg", "version": "1.0", "known_vulnerability": True, "severity": severity}
    ]}
    assert run_cli(tmp_path, command, ecosystem).returncode == expected
