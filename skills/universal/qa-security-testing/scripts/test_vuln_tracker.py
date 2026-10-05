#!/usr/bin/env python3
"""Unit tests for vuln_tracker.py."""

from __future__ import annotations

import importlib.util
import io
import json
import os
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace


SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR.parent / "data"


def load_module():
    path = Path(os.environ.get("VULN_TRACKER_SCRIPT", str(SCRIPT_DIR / "vuln_tracker.py")))
    spec = importlib.util.spec_from_file_location("vuln_tracker", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


vuln_tracker = load_module()


class VulnTrackerTests(unittest.TestCase):
    def test_malformed_findings_cannot_report_clean(self) -> None:
        valid = {"id": "X", "title": "Finding", "severity": "critical",
                 "status": "open", "due_date": "2026-01-01"}
        variants = [
            {**valid, "status": "opened"}, {**valid, "severity": "CRITICAL"},
            {**valid, "status": None}, {**valid, "due_date": None},
            {**valid, "epss": "0.99"}, {**valid, "epss": 1.1},
            {**valid, "cvss": float("nan")}, {**valid, "cvss": True},
            {**valid, "reachable": "false"}, {**valid, "kev": "true"},
            {**valid, "id": ""}, {},
        ]
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "findings.json"
            for finding in variants:
                path.write_text(json.dumps({"vulnerabilities": [finding]}))
                for command in (vuln_tracker.cmd_status, vuln_tracker.cmd_sla,
                                vuln_tracker.cmd_triage, vuln_tracker.cmd_report):
                    with self.subTest(finding=finding, command=command.__name__):
                        output = io.StringIO()
                        with self.assertRaises(SystemExit), redirect_stdout(output):
                            command(SimpleNamespace(input=str(path), coverage=None, output=None))
                        self.assertEqual(output.getvalue(), "")

    def test_malformed_coverage_cannot_report_full_coverage(self) -> None:
        scanner = {"name": "SAST", "type": "SAST"}
        valid = {"scanners": [scanner], "attack_surfaces": [
            {"name": "API", "scanners": {"SAST": True}}]}
        variants = [{}, {"scanners": [], "attack_surfaces": []},
                    {**valid, "attack_surfaces": [{"name": "API", "scanners": {"SAST": "false"}}]},
                    {**valid, "attack_surfaces": [{"name": "API", "scanners": {"Ghost": True}}]},
                    {**valid, "scanners": [scanner, scanner]},
                    {**valid, "attack_surfaces": [{"name": "API"}]}]
        for data in variants:
            with self.subTest(data=data), self.assertRaises(SystemExit):
                vuln_tracker._coverage_breadth(data)

    def test_coverage_with_no_scanners_is_zero_not_clean(self) -> None:
        self.assertEqual(vuln_tracker._coverage_breadth({"scanners": [],
                         "attack_surfaces": [{"name": "API", "scanners": {}}]}), 0.0)

    def test_missing_coverage_has_no_invented_score(self) -> None:
        args = SimpleNamespace(input=str(DATA_DIR / "sample-vulnerabilities.json"),
                               coverage=None, output=None)
        for command in (vuln_tracker.cmd_status, vuln_tracker.cmd_report):
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(command(args), 0)
            self.assertIn("unavailable", output.getvalue())
            self.assertNotIn("50%", output.getvalue())
            self.assertNotIn("(estimated)", output.getvalue())

    def test_invalid_coverage_leaves_report_output_untouched(self) -> None:
        with TemporaryDirectory() as tmp:
            coverage_path = Path(tmp) / "coverage.json"
            coverage_path.write_text('{}')
            output_path = Path(tmp) / "report.md"
            output_path.write_text('existing report')
            args = SimpleNamespace(input=str(DATA_DIR / "sample-vulnerabilities.json"),
                                   coverage=str(coverage_path), output=str(output_path))
            with self.assertRaises(SystemExit), redirect_stdout(io.StringIO()):
                vuln_tracker.cmd_report(args)
            self.assertEqual(output_path.read_text(), 'existing report')

    def test_explicit_empty_findings_are_valid(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "findings.json"
            path.write_text('{"vulnerabilities": []}')
            args = SimpleNamespace(input=str(path), coverage=None, output=None)
            for command in (vuln_tracker.cmd_status, vuln_tracker.cmd_sla,
                            vuln_tracker.cmd_triage, vuln_tracker.cmd_report):
                with redirect_stdout(io.StringIO()):
                    self.assertEqual(command(args), 0)

    def test_coverage_breadth_detects_partial_coverage(self) -> None:
        data = vuln_tracker._load_json(str(DATA_DIR / "sample-scan-coverage.json"))
        breadth = vuln_tracker._coverage_breadth(data)

        self.assertGreater(breadth, 0.0)
        self.assertLess(breadth, 1.0)

    def test_posture_score_returns_weighted_percentage(self) -> None:
        self.assertEqual(vuln_tracker._posture_score(1.0, 1.0, 1.0), 100.0)
        self.assertLess(vuln_tracker._posture_score(0.5, 0.5, 0.5), 100.0)

    def test_report_recommendations_use_recorded_deadlines(self) -> None:
        findings = [
            {"id": "C", "title": "Critical finding", "severity": "critical",
             "status": "open", "due_date": "2099-01-15"},
            {"id": "H", "title": "High finding", "severity": "high",
             "status": "in_progress", "due_date": "2099-02-10"},
            {"id": "R", "title": "Resolved finding", "severity": "critical",
             "status": "resolved", "due_date": "2099-03-20"},
        ]
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "findings.json"
            path.write_text(json.dumps({"vulnerabilities": findings}))
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertEqual(vuln_tracker.cmd_report(SimpleNamespace(
                    input=str(path), coverage=None, output=None)), 0)
        recommendations = output.getvalue().split("## Recommendations", 1)[1]
        self.assertIn("**C** (critical) by recorded due date **2099-01-15**", recommendations)
        self.assertIn("**H** (high) by recorded due date **2099-02-10**", recommendations)
        self.assertNotIn("**R**", recommendations)
        self.assertNotIn("within 24 hours", recommendations)
        self.assertNotIn("within 7 days", recommendations)

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

    def test_kev_low_cvss_outranks_non_kev_high_cvss_low_epss(self) -> None:
        # A severity-only sort would put the 9.8 first. KEV is confirmed
        # exploitation, so the 5.3 must be fixed first.
        kev_low = {"id": "KEV-LOW", "severity": "medium", "cvss": 5.3,
                   "epss": 0.05, "kev": True, "reachable": None}
        high_quiet = {"id": "HIGH-QUIET", "severity": "critical", "cvss": 9.8,
                      "epss": 0.01, "kev": False, "reachable": True}
        ranked = vuln_tracker.rank_vulns([high_quiet, kev_low])
        self.assertEqual([v["id"] for v in ranked], ["KEV-LOW", "HIGH-QUIET"])
        self.assertEqual(vuln_tracker.triage_priority(kev_low)[0], 0)

    def test_high_epss_reachable_outranks_high_cvss_low_epss(self) -> None:
        hot = {"id": "HOT", "severity": "medium", "cvss": 6.5, "epss": 0.94, "reachable": True}
        cold = {"id": "COLD", "severity": "critical", "cvss": 9.1, "epss": 0.02, "reachable": True}
        self.assertEqual([v["id"] for v in vuln_tracker.rank_vulns([cold, hot])], ["HOT", "COLD"])

    def test_unreachable_is_tracked_not_dropped(self) -> None:
        unreachable = {"id": "U", "severity": "critical", "cvss": 9.1, "epss": 0.02, "reachable": False}
        pri, reason = vuln_tracker.triage_priority(unreachable)
        self.assertEqual(pri, 3)
        self.assertIn("do not auto-close", reason)
        self.assertEqual(len(vuln_tracker.rank_vulns([unreachable])), 1)

    def test_sla_output_labels_bundled_defaults_not_due_dates(self) -> None:
        # cmd sla's "SLA rules:" header must not present the bundled SLA_DAYS
        # constants as if they drove the overdue computation below (they don't --
        # that uses each finding's own due_date). Fails on the old unlabelled header.
        vuln = {"id": "X", "title": "Finding", "severity": "critical",
                "status": "open", "due_date": "2026-01-01"}
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "findings.json"
            path.write_text(json.dumps({"vulnerabilities": [vuln]}))
            output = io.StringIO()
            with redirect_stdout(output):
                vuln_tracker.cmd_sla(SimpleNamespace(input=str(path), coverage=None, output=None))
            text = output.getvalue()
            self.assertNotIn("SLA rules: CRITICAL=", text)
            self.assertIn("illustrative", text.lower())
            self.assertIn("due_date", text)

    def test_report_sla_table_labelled_illustrative(self) -> None:
        # The "## SLA Compliance" table must be labelled as bundled illustrative
        # defaults, not presented as the live rule driving the overdue list.
        vuln = {"id": "X", "title": "Finding", "severity": "critical",
                "status": "open", "due_date": "2026-01-01"}
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "findings.json"
            path.write_text(json.dumps({"vulnerabilities": [vuln]}))
            output = io.StringIO()
            with redirect_stdout(output):
                vuln_tracker.cmd_report(SimpleNamespace(input=str(path), coverage=None, output=None))
            text = output.getvalue()
            self.assertIn("## SLA Compliance", text)
            self.assertIn("illustrative", text.lower())
            self.assertNotIn("| Rule | Threshold |", text)

    def test_missing_vulnerabilities_key_fails_instead_of_reporting_clean(self) -> None:
        # A malformed scanner export must not read as "no open vulnerabilities".
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "export.json"
            path.write_text('{"findings": [{"id": "X", "severity": "critical"}]}')
            for cmd in (vuln_tracker.cmd_status, vuln_tracker.cmd_sla, vuln_tracker.cmd_triage):
                with self.assertRaises(SystemExit) as ctx, redirect_stdout(io.StringIO()):
                    cmd(SimpleNamespace(input=str(path)))
                self.assertNotEqual(ctx.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
