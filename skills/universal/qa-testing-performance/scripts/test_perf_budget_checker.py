#!/usr/bin/env python3

"""Tests for perf_budget_checker.py.

Run: python3 -m unittest scripts.test_perf_budget_checker -v
"""

from __future__ import annotations

import sys
import os
import json
import subprocess
import tempfile
import importlib.util
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

SCRIPT = Path(os.environ.get("QA_PERF_BUDGET_UNDER_TEST", SCRIPT_DIR / "perf_budget_checker.py"))
spec = importlib.util.spec_from_file_location("perf_budget_under_test", SCRIPT)
pb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pb)


def run_cli(data, command="check"):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "results.json"
        path.write_text(json.dumps(data))
        return subprocess.run([sys.executable, str(SCRIPT), command, "--input", str(path)],
                              capture_output=True, text=True)



class StatusConstantsTests(unittest.TestCase):
    def test_status_constants_exist(self):
        self.assertTrue(pb.PASS)
        self.assertTrue(pb.WARN)
        self.assertTrue(pb.FAIL)


class ApiP95Tests(unittest.TestCase):
    def test_within_budget_passes(self):
        status, _ = pb._check_api_p95(80, 100)
        self.assertEqual(status, pb.PASS)

    def test_warn_zone_25pct(self):
        status, _ = pb._check_api_p95(120, 100)
        self.assertEqual(status, pb.WARN)

    def test_fail_above_25pct(self):
        status, _ = pb._check_api_p95(150, 100)
        self.assertEqual(status, pb.FAIL)


class ApiP99Tests(unittest.TestCase):
    def test_within_budget_passes(self):
        status, _ = pb._check_api_p99(90, 100, "p99")
        self.assertEqual(status, pb.PASS)

    def test_tighter_warn_zone_15pct(self):
        # p99 has tighter warn (15%) vs p95 (25%)
        status, _ = pb._check_api_p99(110, 100, "p99")
        self.assertEqual(status, pb.WARN)
        status, _ = pb._check_api_p99(120, 100, "p99")
        self.assertEqual(status, pb.FAIL)

    def test_label_appears_in_note(self):
        _, note = pb._check_api_p99(90, 100, "p99.9")
        self.assertIn("p99.9", note)


class ThroughputTests(unittest.TestCase):
    def test_meets_minimum(self):
        status, _ = pb._check_throughput(500, 500)
        self.assertEqual(status, pb.PASS)

    def test_warn_within_10pct(self):
        status, _ = pb._check_throughput(460, 500)
        self.assertEqual(status, pb.WARN)

    def test_fail_below_90pct(self):
        status, _ = pb._check_throughput(400, 500)
        self.assertEqual(status, pb.FAIL)


class ErrorRateTests(unittest.TestCase):
    def test_well_under_passes(self):
        status, _ = pb._check_error_rate(0.1, 1.0)
        self.assertEqual(status, pb.PASS)

    def test_at_budget_passes(self):
        status, _ = pb._check_error_rate(1.0, 1.0)
        self.assertEqual(status, pb.PASS)

    def test_above_budget_warns(self):
        status, _ = pb._check_error_rate(1.3, 1.0)
        self.assertEqual(status, pb.WARN)


class CoreWebVitalsBudgetTests(unittest.TestCase):
    """User budget is authoritative and must FAIL even inside Google's own band."""

    def test_lcp_over_user_budget_fails_even_within_google_good_band(self):
        # 2400ms is still Google "good" (<=2500ms) but exceeds a 2000ms budget.
        status, note = pb._check_lcp(2400, 2000)
        self.assertEqual(status, pb.FAIL)
        self.assertIn("2000", note)

    def test_lcp_within_user_budget_passes(self):
        status, _ = pb._check_lcp(1900, 2000)
        self.assertEqual(status, pb.PASS)

    def test_inp_over_user_budget_fails_even_within_google_good_band(self):
        # 190ms is still Google "good" (<200ms) but exceeds a 100ms budget.
        status, note = pb._check_inp(190, 100)
        self.assertEqual(status, pb.FAIL)
        self.assertIn("100", note)

    def test_cls_over_user_budget_fails(self):
        status, _ = pb._check_cls(0.09, 0.05)
        self.assertEqual(status, pb.FAIL)


class EvaluateBudgetsIntegrationTests(unittest.TestCase):
    """Verify the new p99/p99.9 keys get picked up by _evaluate_budgets."""

    def test_p99_metrics_recognized(self):
        data = {
            "budgets": {"api_p95_ms": 100, "api_p99_ms": 200, "api_p999_ms": 500},
            "results": {"api_p95_ms": 80, "api_p99_ms": 180, "api_p999_ms": 480},
        }
        checks = pb._evaluate_budgets(data)
        metrics = {c["metric"] for c in checks}
        self.assertIn("API p95", metrics)
        self.assertIn("API p99", metrics)
        self.assertIn("API p99.9", metrics)
        # All within budget → all pass.
        self.assertTrue(all(c["status"] == pb.PASS for c in checks))

    def test_p99_fail_status_propagates(self):
        data = {
            "budgets": {"api_p99_ms": 100},
            "results": {"api_p99_ms": 200},  # 2× budget — well past 15% warn zone
        }
        checks = pb._evaluate_budgets(data)
        self.assertEqual(checks[0]["status"], pb.FAIL)


class FailClosedCliTests(unittest.TestCase):
    def test_empty_unknown_and_missing_budgets(self):
        for data in [{}, {"budgets": {}, "results": {}},
                     {"budgets": {"api_p95_ms": 100, "typo": 100}, "results": {"api_p95_ms": 80}},
                     {"budgets": {"api_p95_ms": 100, "inp_ms": 200}, "results": {"api_p95_ms": 80}}]:
            with self.subTest(data=data):
                proc = run_cli(data)
                self.assertEqual(proc.returncode, 2)
                self.assertNotIn("CI gate PASSED", proc.stdout)

    def test_invalid_budget_numbers(self):
        for value in [True, "100", None, -1, 0, float("nan"), float("inf"), [], {}]:
            with self.subTest(value=value):
                proc = run_cli({"budgets": {"api_p95_ms": value}, "results": {"api_p95_ms": 80}})
                self.assertEqual(proc.returncode, 2)
                self.assertNotIn("Traceback", proc.stderr)

    def test_invalid_result_numbers(self):
        for value in [True, "80", None, -1, float("nan"), float("inf"), [], {}]:
            with self.subTest(value=value):
                proc = run_cli({"budgets": {"api_p95_ms": 100}, "results": {"api_p95_ms": value}})
                self.assertEqual(proc.returncode, 2)
                self.assertNotIn("Traceback", proc.stderr)

    def test_invalid_percentages(self):
        for budget, actual in [(101, 1), (1, 101)]:
            self.assertEqual(run_cli({"budgets": {"error_rate_pct": budget},
                                      "results": {"error_rate_pct": actual}}).returncode, 2)

    def test_bad_input_containers(self):
        for data in [[], {"budgets": [], "results": {}}, {"budgets": {"cls": 0.1}, "results": []}]:
            with self.subTest(data=data):
                proc = run_cli(data)
                self.assertEqual(proc.returncode, 2)
                self.assertNotIn("Traceback", proc.stderr)

    def test_report_failure_propagates(self):
        proc = run_cli({"budgets": {"lcp_ms": 1000}, "results": {"lcp_ms": 2000}}, "report")
        self.assertEqual(proc.returncode, 1)
        self.assertIn("Overall result: FAIL", proc.stdout)
        self.assertIn("LCP | <= user budget | none | > user budget", proc.stdout)

    def test_warn_policy_preserved(self):
        proc = run_cli({"budgets": {"api_p95_ms": 100}, "results": {"api_p95_ms": 120}})
        self.assertEqual(proc.returncode, 0)
        self.assertIn("PASSED WITH WARNINGS", proc.stdout)

    def test_zero_error_budget_and_measurement_pass(self):
        self.assertEqual(run_cli({"budgets": {"error_rate_pct": 0},
                                  "results": {"error_rate_pct": 0}}).returncode, 0)

    def test_plan_missing_and_invalid_scenarios(self):
        valid = {"name": "load", "type": "load", "duration_minutes": 1, "virtual_users": 1}
        cases = [{}, {"test_scenarios": []}, {"test_scenarios": {}}, {"test_scenarios": [[]]}]
        for key, value in [("type", "unknown"), ("type", []), ("type", {}), ("duration_minutes", -1), ("virtual_users", True),
                           ("virtual_users", 1.5), ("name", "")]:
            cases.append({"test_scenarios": [{**valid, key: value}]})
        for data in cases:
            with self.subTest(data=data):
                proc = run_cli(data, "plan")
                self.assertEqual(proc.returncode, 2)
                self.assertNotIn("Traceback", proc.stderr)

    def test_fractional_duration_is_not_truncated(self):
        proc = run_cli({"test_scenarios": [{"name": "load", "type": "load",
                         "duration_minutes": 2.5, "virtual_users": 5}]}, "plan")
        self.assertEqual(proc.returncode, 0)
        self.assertIn("[nightly]", proc.stdout)
        self.assertNotIn("[PR_gate]", proc.stdout)

    def test_duplicate_json_key_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "results.json"
            path.write_text('{"budgets":{"cls":0.01,"cls":0.1},"results":{"cls":0.05}}')
            proc = subprocess.run([sys.executable, str(SCRIPT), "check", "--input", str(path)],
                                  capture_output=True, text=True)
        self.assertEqual(proc.returncode, 2)
        self.assertIn("duplicate JSON key", proc.stderr)


class K6TemplateRegressions(unittest.TestCase):
    def run_flow(self, flow, status):
        template = os.environ.get("QA_K6_TEMPLATE_UNDER_TEST", str(SCRIPT_DIR.parent / "assets/template-k6-load-test.js"))
        harness = r"""
const fs = require('fs');
const vm = require('vm');
let source = fs.readFileSync(process.argv[1], 'utf8')
  .replace(/^import .*;$/gm, '')
  .replace(/export default function/g, 'function defaultFlow')
  .replace(/export function/g, 'function')
  .replace(/export const/g, 'const');
const samples = [];
const status = Number(process.argv[3]);
const response = {status, json: () => ({length: 1}), timings: {duration: 10}};
const context = {
  __ENV: {},
  http: {get: () => response, post: () => response},
  check: (r, checks) => Object.values(checks).every(check => check(r)),
  sleep: () => {},
  randomIntBetween: () => 1,
  Rate: class {add(value) {samples.push(value);}},
  Trend: class {add() {}},
};
vm.createContext(context);
vm.runInContext(source, context);
context[process.argv[2]]({});
process.stdout.write(JSON.stringify(samples));
"""
        proc = subprocess.run(["node", "-e", harness, template, flow, str(status)], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        return json.loads(proc.stdout)

    def test_browse_records_success_and_failure_denominator(self):
        self.assertEqual(self.run_flow("browseFlow", 200), [False, False])
        self.assertEqual(self.run_flow("browseFlow", 500), [True, True])

    def test_checkout_records_success_and_failure_denominator(self):
        self.assertEqual(self.run_flow("checkoutFlow", 201), [False])
        self.assertEqual(self.run_flow("checkoutFlow", 500), [True])


if __name__ == "__main__":
    unittest.main()
