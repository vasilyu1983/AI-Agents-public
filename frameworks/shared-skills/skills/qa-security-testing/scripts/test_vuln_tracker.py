#!/usr/bin/env python3
"""Unit tests for vuln_tracker.py."""

from __future__ import annotations

import importlib.util
import io
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"


def load_module():
    spec = importlib.util.spec_from_file_location("vuln_tracker", SCRIPT_DIR / "vuln_tracker.py")
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


vuln_tracker = load_module()


class VulnTrackerTests(unittest.TestCase):
    def test_coverage_breadth_detects_partial_coverage(self) -> None:
        data = vuln_tracker._load_json(str(DATA_DIR / "sample-scan-coverage.json"))
        breadth = vuln_tracker._coverage_breadth(data)

        self.assertGreater(breadth, 0.0)
        self.assertLess(breadth, 1.0)

    def test_posture_score_returns_weighted_percentage(self) -> None:
        self.assertEqual(vuln_tracker._posture_score(1.0, 1.0, 1.0), 100.0)
        self.assertLess(vuln_tracker._posture_score(0.5, 0.5, 0.5), 100.0)

    def test_report_writes_markdown(self) -> None:
        output_buffer = io.StringIO()
        with TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "security-report.md"
            args = SimpleNamespace(
                input=str(DATA_DIR / "sample-vulnerabilities.json"),
                coverage=str(DATA_DIR / "sample-scan-coverage.json"),
                output=str(output_path),
            )
            with redirect_stdout(output_buffer):
                exit_code = vuln_tracker.cmd_report(args)

            report_text = output_path.read_text(encoding="utf-8")

        self.assertEqual(exit_code, 0)
        self.assertIn("# Security Testing Report", report_text)
        self.assertIn("## Scanner Coverage", report_text)
        self.assertIn("Report written to", output_buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
