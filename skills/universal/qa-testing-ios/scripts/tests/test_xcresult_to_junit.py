#!/usr/bin/env python3
"""Regression tests for xcresult_to_junit.py.

Fixtures are real `xcrun xcresulttool get test-results {tests,summary}`
output from Xcode 27.0 (xcresulttool 25115) for a probe package with
11 tests: 7 passed, 3 failed, 1 expected failure (withKnownIssue), one
parameterized test and two runtime warnings. File paths and device IDs
are scrubbed.

The CLI test runs the converter against a fake `xcrun` on PATH, so it
needs no Xcode. Point XCRESULT_TO_JUNIT at another converter to check it:
a leaf-walking converter reports failures="0" here and must fail.

Run: python3 -m unittest discover -s scripts/tests -v
"""

import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

HERE = os.path.dirname(os.path.abspath(__file__))
FIXTURES = os.path.join(HERE, "fixtures")
SCRIPT = os.environ.get("XCRESULT_TO_JUNIT", os.path.join(os.path.dirname(HERE), "xcresult_to_junit.py"))
TESTS_JSON = os.path.join(FIXTURES, "xcode27_tests.json")
SUMMARY_JSON = os.path.join(FIXTURES, "xcode27_summary.json")

sys.path.insert(0, os.path.dirname(HERE))
import xcresult_to_junit as conv  # noqa: E402


def _load(path):
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def _run_cli_with_fake_xcrun(tests_path, summary_path):
    """Run SCRIPT on a dummy bundle with a fake xcrun/xcresulttool on PATH."""
    tmp = tempfile.mkdtemp()
    bundle = os.path.join(tmp, "R.xcresult")
    os.mkdir(bundle)
    shim = (
        "#!/bin/sh\n"
        'case "$*" in\n'
        f'  *summary*) cat "{summary_path}" ;;\n'
        f'  *) cat "{tests_path}" ;;\n'
        "esac\n"
    )
    for tool in ("xcrun", "xcresulttool"):
        path = os.path.join(tmp, tool)
        with open(path, "w") as fh:
            fh.write(shim)
        os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC)
    out = os.path.join(tmp, "junit.xml")
    env = dict(os.environ, PATH=tmp + os.pathsep + os.environ.get("PATH", ""))
    proc = subprocess.run(
        [sys.executable, SCRIPT, bundle, "--output", out],
        capture_output=True, text=True, env=env, check=False,
    )
    root = ET.parse(out).getroot() if os.path.exists(out) else None
    return proc, root


class FixtureCounts(unittest.TestCase):
    def setUp(self):
        self.root = conv.build_junit(_load(TESTS_JSON)).getroot()

    def test_reports_all_three_failures(self):
        # Summary for this bundle: 11 total, 3 failed. Under-reporting is the defect.
        self.assertEqual(self.root.get("failures"), "3")
        self.assertEqual(self.root.get("tests"), "11")
        self.assertEqual(self.root.get("errors"), "0")
        self.assertEqual(self.root.get("skipped"), "0")

    def test_detail_nodes_are_not_test_cases(self):
        names = {s.get("name") for s in self.root.iter("testsuite")}
        self.assertEqual(names, {"Basics", "SerialSuite"})
        case_names = {c.get("name") for c in self.root.iter("testcase")}
        for bogus in ("1", "2", "Issue recorded: warn only"):
            self.assertNotIn(bogus, case_names)

    def test_failure_text_comes_from_children(self):
        failed = {c.get("name"): c.find("failure") for c in self.root.iter("testcase") if c.find("failure") is not None}
        self.assertEqual(set(failed), {"noConfirmHangs()", "mixXCT()", "fails()"})
        self.assertIn("Confirmation was confirmed 0 times", failed["noConfirmHangs()"].text)
        self.assertIn("XCTAssertEqual failed", failed["mixXCT()"].text)

    def test_durations_are_read(self):
        self.assertGreater(sum(float(c.get("time")) for c in self.root.iter("testcase")), 0.0)

    def test_summary_cross_check_passes_on_consistent_input(self):
        self.assertIsNone(conv.check_against_summary(conv.build_junit(_load(TESTS_JSON)), _load(SUMMARY_JSON)))


class FailsClosed(unittest.TestCase):
    def test_invalid_summary_counts_are_rejected(self):
        tree = conv.build_junit(_load(TESTS_JSON))
        for summary in ({}, {"failedTests": "3", "totalTestCount": 11},
                        {"failedTests": False, "totalTestCount": 11},
                        {"failedTests": -1, "totalTestCount": 11},
                        {"failedTests": 12, "totalTestCount": 11}):
            with self.subTest(summary=summary):
                self.assertIsNotNone(conv.check_against_summary(tree, summary))

    def test_summary_mismatch_is_detected(self):
        data = _load(TESTS_JSON)

        def mark_passed(nodes):
            for n in nodes:
                if n.get("nodeType") == "Test Case" and n.get("result") == "Failed":
                    n["result"] = "Passed"
                mark_passed(n.get("children", []))

        mark_passed(data["testNodes"])
        problem = conv.check_against_summary(conv.build_junit(data), _load(SUMMARY_JSON))
        self.assertIsNotNone(problem)
        self.assertIn("summary failedTests=3", problem)

    def test_unknown_result_is_an_error_not_a_pass(self):
        data = {"testNodes": [{"nodeType": "Test Suite", "name": "S", "children": [
            {"nodeType": "Test Case", "name": "t()", "result": "Mixed"}]}]}
        root = conv.build_junit(data).getroot()
        self.assertEqual(root.get("errors"), "1")

    def test_empty_tree_exits_nonzero(self):
        with self.assertRaises(SystemExit) as ctx:
            conv.build_junit({"testNodes": []})
        self.assertEqual(ctx.exception.code, 3)


class Cli(unittest.TestCase):
    def test_cli_rejects_missing_summary_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            summary = os.path.join(tmp, "summary.json")
            with open(summary, "w") as fh:
                json.dump({}, fh)
            proc, _ = _run_cli_with_fake_xcrun(TESTS_JSON, summary)
            self.assertEqual(proc.returncode, 4, proc.stderr)
            self.assertIn("summary failedTests", proc.stderr)

    def test_cli_reports_three_failures_and_exits_zero(self):
        proc, root = _run_cli_with_fake_xcrun(TESTS_JSON, SUMMARY_JSON)
        self.assertIsNotNone(root, proc.stderr)
        self.assertEqual(root.get("failures"), "3", "converter under-reports failures")
        self.assertEqual(proc.returncode, 0, proc.stderr)


if __name__ == "__main__":
    unittest.main()
