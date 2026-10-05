"""Regression checks for source-validator input and scan boundaries."""

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).with_name("validate_sources.py")
spec = importlib.util.spec_from_file_location("validate_sources", SCRIPT)
validator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validator)


def run_cli(root, *args):
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(root), "--scan-only", *args],
        text=True, capture_output=True, check=False,
    )


def test_missing_root_fails_closed(tmp_path):
    root = tmp_path / "missing"
    result = run_cli(root, "--json")
    assert result.returncode == 2
    assert str(root) in result.stderr
    assert result.stdout == ""


def test_file_root_fails_closed(tmp_path):
    root = tmp_path / "input.md"
    root.write_text("https://example.com")
    result = run_cli(root)
    assert result.returncode == 2
    assert str(root) in result.stderr


def test_archive_tree_is_pruned_before_reading(tmp_path):
    archive = tmp_path / ".archive"
    archive.mkdir()
    (archive / "invalid.md").write_bytes(b"\xff")
    (tmp_path / "active.md").write_text("https://example.com")
    assert validator.inventory(tmp_path) == [
        {"path": "active.md", "url": "https://example.com"}
    ]


def test_symlink_does_not_expand_scan_outside_root(tmp_path):
    external = tmp_path / "outside.md"
    external.write_text("https://outside.example.com")
    root = tmp_path / "skill"
    root.mkdir()
    (root / "linked.md").symlink_to(external)
    (root / "active.md").write_text("https://example.com")
    assert validator.inventory(root) == [
        {"path": "active.md", "url": "https://example.com"}
    ]


@pytest.mark.parametrize("timeout", ["0", "-1", "nan", "inf"])
def test_invalid_timeout_fails_before_scan(tmp_path, timeout):
    (tmp_path / "active.md").write_text("https://example.com")
    result = run_cli(tmp_path, "--timeout", timeout)
    assert result.returncode == 2
    assert "timeout" in result.stderr.lower()


def test_scan_only_keeps_valid_json_inventory(tmp_path):
    (tmp_path / "active.md").write_text("https://example.com")
    result = run_cli(tmp_path, "--json")
    assert result.returncode == 0
    assert json.loads(result.stdout) == [
        {"path": "active.md", "url": "https://example.com"}
    ]


def test_empty_root_fails_closed(tmp_path):
    result = run_cli(tmp_path)
    assert result.returncode == 2
    assert str(tmp_path) in result.stderr


def test_unreadable_text_reports_input_path(tmp_path):
    path = tmp_path / "invalid.md"
    path.write_bytes(b"\xff")
    result = run_cli(tmp_path)
    assert result.returncode == 2
    assert str(path) in result.stderr
    assert "Traceback" not in result.stderr
