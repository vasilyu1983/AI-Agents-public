"""Tests for check_perf_budget.py: lab reports must not silently pass an INP budget."""

import json
import os
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.environ.get("PERF_BUDGET_UNDER_TEST", os.path.join(HERE, "check_perf_budget.py"))
sys.path.insert(0, HERE)
import check_perf_budget as cpb  # noqa: E402


def lighthouse_report(tbt=None, inp=None, lcp=2000):
    audits = {"largest-contentful-paint": {"numericValue": lcp}}
    if tbt is not None:
        audits["total-blocking-time"] = {"numericValue": tbt}
    if inp is not None:
        audits["interaction-to-next-paint"] = {"numericValue": inp}
    return {"audits": audits, "categories": {"performance": {"score": 0.95}}}


def run(budget, report, fmt="lighthouse"):
    with tempfile.TemporaryDirectory() as d:
        bp, rp = os.path.join(d, "b.json"), os.path.join(d, "r.json")
        with open(bp, "w") as f:
            json.dump(budget, f)
        with open(rp, "w") as f:
            json.dump(report, f)
        proc = subprocess.run(
            [sys.executable, SCRIPT, "--budget", bp, "--report", rp, "--format", fmt],
            capture_output=True, text=True,
        )
    return proc.returncode, proc.stdout + proc.stderr


class TestLabInp(unittest.TestCase):
    def test_inp_budget_without_tbt_fails_loud_on_lab_report(self):
        # Navigation-mode Lighthouse reports carry no INP audit; passing here would be silent.
        code, out = run({"lcp_ms": 2500, "inp_ms": 200}, lighthouse_report())
        self.assertEqual(code, 2)
        self.assertIn("field metric", out)

    def test_tbt_budget_gates_lab_run_when_inp_missing(self):
        code, out = run({"lcp_ms": 2500, "inp_ms": 200, "tbt_ms": 200}, lighthouse_report(tbt=150))
        self.assertEqual(code, 0)
        self.assertIn("Not Checked", out)
        self.assertIn("TBT gates this lab run", out)

    def test_tbt_breach_fails(self):
        code, _ = run({"inp_ms": 200, "tbt_ms": 200}, lighthouse_report(tbt=450))
        self.assertEqual(code, 1)

    def test_timespan_report_with_inp_is_checked(self):
        code, out = run({"inp_ms": 200}, lighthouse_report(inp=350))
        self.assertEqual(code, 1)
        self.assertIn("INP", out)

    def test_field_inp_via_custom_report(self):
        code, _ = run({"inp_ms": 200}, {"metrics": {"inp_ms": 180}}, fmt="custom")
        self.assertEqual(code, 0)


class TestMissingMetrics(unittest.TestCase):
    def test_partial_report_cannot_pass(self):
        for fmt, report in [("lighthouse", lighthouse_report()), ("custom", {"lcp_ms": 2000})]:
            with self.subTest(fmt=fmt):
                code, out = run({"lcp_ms": 2500, "js_bytes": 1000}, report, fmt)
                self.assertEqual(code, 2)
                self.assertIn("js_bytes", out)

    def test_missing_keys_listed(self):
        missing = cpb.missing_budget_keys({"lcp_ms": 1, "js_bytes": 1, "unknown": 1}, {"lcp_ms": 5.0, "js_bytes": None})
        self.assertEqual(missing, ["js_bytes"])

    def test_no_matching_metric_exits_2(self):
        code, _ = run({"lcp_ms": 2500}, {"metrics": {}}, fmt="custom")
        self.assertEqual(code, 2)


class TestInputValidation(unittest.TestCase):
    def test_bad_budget_cannot_hide_behind_valid_metric(self):
        for value in [True, "2500", None, -1, float("nan"), float("inf"), {}, []]:
            with self.subTest(value=value):
                code, out = run({"lcp_ms": value, "tbt_ms": 200}, lighthouse_report(tbt=150))
                self.assertEqual(code, 2)
                self.assertNotIn("Status:  PASS", out)

    def test_unknown_budget_key_is_error(self):
        code, out = run({"lcp_ms": 2500, "lcps_ms": 2500}, lighthouse_report())
        self.assertEqual(code, 2)
        self.assertIn("unknown", out)

    def test_invalid_custom_metric_is_error(self):
        for value in [True, "2000", -1, float("nan"), float("inf"), {}, []]:
            with self.subTest(value=value):
                code, _ = run({"lcp_ms": 2500, "tbt_ms": 200}, {"lcp_ms": value, "tbt_ms": 150}, "custom")
                self.assertEqual(code, 2)

    def test_invalid_lighthouse_metric_is_error(self):
        for value in [True, "2000", -1, float("nan"), float("inf")]:
            with self.subTest(value=value):
                code, _ = run({"lcp_ms": 2500}, lighthouse_report(lcp=value))
                self.assertEqual(code, 2)

    def test_score_range_is_checked(self):
        for fmt, budget, report in [
            ("lighthouse", {"lcp_ms": 2500}, {**lighthouse_report(), "categories": {"performance": {"score": 2}}}),
            ("custom", {"lighthouse_performance_score": 90}, {"lighthouse_performance_score": 101}),
            ("custom", {"lighthouse_performance_score": 101}, {"lighthouse_performance_score": 95}),
        ]:
            with self.subTest(fmt=fmt, budget=budget):
                self.assertEqual(run(budget, report, fmt)[0], 2)

    def test_malformed_structures_are_usage_errors(self):
        for fmt, report in [
            ("custom", {"metrics": []}),
            ("lighthouse", {"audits": []}),
            ("lighthouse", {"audits": {"largest-contentful-paint": []}}),
            ("lighthouse", {"categories": []}),
            ("lighthouse", {"audits": {"resource-summary": {"details": {"items": {}}}}}),
            ("lighthouse", {"audits": {"resource-summary": {"details": {"items": [[]]}}}}),
        ]:
            with self.subTest(fmt=fmt, report=report):
                code, out = run({"lcp_ms": 2500}, report, fmt)
                self.assertEqual(code, 2)
                self.assertNotIn("Traceback", out)

    def test_zero_resource_totals_are_valid_measurements(self):
        report = {"audits": {"resource-summary": {"details": {"items": [
            {"resourceType": "total", "transferSize": 0, "requestCount": 0}
        ]}}}}
        self.assertEqual(run({"total_bytes": 10, "requests": 1}, report)[0], 0)

    def test_missing_resource_fields_do_not_become_zero(self):
        for row in [{"resourceType": "total", "requestCount": 1}, {"label": "Script", "requestCount": 1}]:
            with self.subTest(row=row):
                report = lighthouse_report()
                report["audits"]["resource-summary"] = {"details": {"items": [row]}}
                self.assertEqual(run({"lcp_ms": 2500, "total_bytes": 1000}, report)[0], 2)

    def test_resource_totals_do_not_double_count(self):
        rows = [
            {"resourceType": "total", "transferSize": 500, "requestCount": 2},
            {"label": "Script", "transferSize": 500, "requestCount": 2},
            {"resourceType": "third-party", "transferSize": 500, "requestCount": 2},
        ]
        report = {"audits": {"resource-summary": {"details": {"items": rows}}}}
        self.assertEqual(run({"total_bytes": 500, "requests": 2, "js_bytes": 500}, report)[0], 0)

    def test_resource_aggregation_overflow_is_error(self):
        report = {"audits": {"resource-summary": {"details": {"items": [
            {"label": "Script", "transferSize": 1e308, "requestCount": 1},
            {"label": "Image", "transferSize": 1e308, "requestCount": 1},
        ]}}}}
        self.assertEqual(run({"total_bytes": 1000}, report)[0], 2)

    def test_duplicate_json_key_is_error(self):
        with tempfile.TemporaryDirectory() as d:
            bp, rp = os.path.join(d, "budget.json"), os.path.join(d, "report.json")
            with open(bp, "w") as f:
                f.write('{"lcp_ms": 1000, "lcp_ms": 2500}')
            with open(rp, "w") as f:
                json.dump(lighthouse_report(), f)
            proc = subprocess.run([sys.executable, SCRIPT, "--budget", bp, "--report", rp], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("duplicate JSON key", proc.stderr)


if __name__ == "__main__":
    unittest.main()
