#!/usr/bin/env python3
"""Convert an .xcresult bundle to JUnit XML for CI publishing.

Reads `xcrun xcresulttool get test-results tests` (Xcode 16+; test fixtures
captured from Xcode 27.0) and emits <testsuites><testsuite><testcase> with <failure>,
<error> and <skipped> elements.

Tree shape (Xcode 27): Test Plan > Unit test bundle / UI test bundle >
Test Suite > Test Case. A failed Test Case carries child nodes such as
"Failure Message", "Runtime Warning", "Expected Failure" and, for
parameterized tests, "Arguments". The Test Case node is the test unit; its
children are details, never separate tests.

The converter fails closed:
  - It cross-checks its failure count against
    `xcresulttool get test-results summary` and exits 4 on a mismatch.
  - An unknown Test Case result is reported as <error>, not as a pass.
  - Zero Test Case nodes is exit 3 (unexpected structure).

Usage:
    python3 xcresult_to_junit.py <bundle.xcresult> [--output junit.xml]
    python3 xcresult_to_junit.py --tests-json tests.json \
        [--summary-json summary.json] [--output junit.xml]

Exit codes:
    0  Success (the JUnit file may still contain failures; the xcodebuild
       exit code remains the pass/fail gate)
    1  Usage error / xcresulttool not found / input not found
    2  xcresulttool returned a non-zero exit code
    3  Unexpected output format (no Test Case nodes, bad JSON)
    4  Parsed failure count disagrees with the xcresult summary
"""

import argparse
import json
import os
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any, Dict, Iterator, List, Optional, Tuple

PASSED = {"passed"}
FAILED = {"failed", "failure", "unexpected failure"}
SKIPPED = {"skipped"}
EXPECTED_FAILURE = {"expected failure"}
DETAIL_TYPES = {"Failure Message", "Expected Failure", "Runtime Warning"}


# ---------------------------------------------------------------------------
# xcresulttool helpers
# ---------------------------------------------------------------------------

def _run_xcresulttool(args: List[str]) -> Dict[str, Any]:
    cmd = ["xcrun", "xcresulttool"] + args + ["--format", "json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    except FileNotFoundError:
        print(
            "error: xcrun not found. Install Xcode 16+ and select it with\n"
            "  `sudo xcode-select -s /Applications/Xcode.app`.",
            file=sys.stderr,
        )
        sys.exit(1)
    if result.returncode != 0:
        print(
            f"error: {' '.join(cmd)} exited with code {result.returncode}.\n"
            f"  stderr: {result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)
    return _parse_json(result.stdout, " ".join(cmd))


def _parse_json(text: str, origin: str) -> Dict[str, Any]:
    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"error: {origin} is not valid JSON: {exc}", file=sys.stderr)
        sys.exit(3)
    if not isinstance(data, dict):
        print(f"error: {origin}: expected a JSON object", file=sys.stderr)
        sys.exit(3)
    return data


def _load_json_file(path: str) -> Dict[str, Any]:
    if not os.path.isfile(path):
        print(f"error: file not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path, encoding="utf-8") as fh:
        return _parse_json(fh.read(), path)


# ---------------------------------------------------------------------------
# Tree walk
# ---------------------------------------------------------------------------

def iter_test_cases(
    nodes: List[Dict[str, Any]], suite: Optional[str] = None, bundle: Optional[str] = None
) -> Iterator[Tuple[str, Dict[str, Any]]]:
    """Yield (suite_name, test_case_node) for every "Test Case" node.

    Does not descend into a Test Case: its children are details.
    """
    for node in nodes:
        ntype = node.get("nodeType", "")
        name = node.get("name", "")
        if ntype == "Test Case":
            yield (suite or bundle or "UnknownSuite", node)
            continue
        child_suite = suite
        child_bundle = bundle
        if ntype == "Test Suite":
            child_suite = f"{suite}.{name}" if suite else name
        elif ntype.endswith("test bundle"):
            child_bundle = name
        yield from iter_test_cases(node.get("children", []), child_suite, child_bundle)


def _duration_seconds(node: Dict[str, Any]) -> float:
    value = node.get("durationInSeconds")
    if isinstance(value, (int, float)):
        return float(value)
    text = node.get("duration")
    if isinstance(text, str):
        match = re.match(r"^\s*([0-9.]+)\s*s\s*$", text)
        if match:
            return float(match.group(1))
    return 0.0


def _detail_messages(node: Dict[str, Any], kinds: set) -> List[str]:
    """Collect detail-node text of the given kinds, recursing into Arguments."""
    out: List[str] = []
    for child in node.get("children", []):
        ctype = child.get("nodeType", "")
        if ctype in kinds:
            text = child.get("name", "")
            loc = child.get("sourceLocation") or {}
            if loc.get("filePath"):
                text = f"{os.path.basename(loc['filePath'])}:{loc.get('lineNumber', '?')}: {text}"
            out.append(text)
        elif ctype == "Arguments":
            prefix = f"[{child.get('name', '')}] "
            out.extend(prefix + m for m in _detail_messages(child, kinds))
    return out


# ---------------------------------------------------------------------------
# JUnit XML assembly
# ---------------------------------------------------------------------------

def build_junit(data: Dict[str, Any], name: str = "xcresult") -> ET.ElementTree:
    top_nodes = data.get("testNodes")
    if not isinstance(top_nodes, list):
        print("error: expected a 'testNodes' list at top level.", file=sys.stderr)
        sys.exit(3)

    suites: Dict[str, List[Dict[str, Any]]] = {}
    for suite_name, node in iter_test_cases(top_nodes):
        suites.setdefault(suite_name, []).append(node)
    if not suites:
        print("error: no 'Test Case' nodes found; refusing to emit an empty report.", file=sys.stderr)
        sys.exit(3)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    root = ET.Element("testsuites", name=name)
    totals = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}

    for suite_name, cases in suites.items():
        counts = {"tests": 0, "failures": 0, "errors": 0, "skipped": 0}
        suite_time = 0.0
        suite_el = ET.SubElement(root, "testsuite", name=suite_name, timestamp=timestamp)
        for node in cases:
            duration = _duration_seconds(node)
            suite_time += duration
            counts["tests"] += 1
            case_el = ET.SubElement(
                suite_el, "testcase", classname=suite_name,
                name=node.get("name", "unknown"), time=f"{duration:.3f}",
            )
            status = str(node.get("result", "")).strip().lower()
            warnings = _detail_messages(node, {"Runtime Warning"})
            if status in FAILED:
                counts["failures"] += 1
                msgs = _detail_messages(node, {"Failure Message"}) or ["Test failed (no failure message in xcresult)"]
                fail_el = ET.SubElement(case_el, "failure", message=msgs[0].splitlines()[0])
                fail_el.text = "\n".join(msgs)
            elif status in SKIPPED:
                counts["skipped"] += 1
                ET.SubElement(case_el, "skipped")
            elif status in EXPECTED_FAILURE:
                # withKnownIssue / XCTExpectFailure: counted as passing, but keep the evidence.
                known = _detail_messages(node, {"Expected Failure"})
                out = ET.SubElement(case_el, "system-out")
                out.text = "Expected failure (known issue):\n" + "\n".join(known)
            elif status not in PASSED:
                counts["errors"] += 1
                err = ET.SubElement(case_el, "error", message=f"Unrecognised xcresult result: {node.get('result')!r}")
                err.text = "\n".join(_detail_messages(node, DETAIL_TYPES))
            if warnings:
                err_el = ET.SubElement(case_el, "system-err")
                err_el.text = "Runtime warnings:\n" + "\n".join(warnings)
        for key, value in counts.items():
            suite_el.set(key, str(value))
            totals[key] += value
        suite_el.set("time", f"{suite_time:.3f}")

    for key, value in totals.items():
        root.set(key, str(value))
    return ET.ElementTree(root)


def check_against_summary(tree: ET.ElementTree, summary: Dict[str, Any]) -> Optional[str]:
    """Return an error string if the JUnit counts disagree with the summary."""
    root = tree.getroot()
    parsed_failed = int(root.get("failures", "0")) + int(root.get("errors", "0"))
    parsed_total = int(root.get("tests", "0"))
    want_failed = summary.get("failedTests")
    want_total = summary.get("totalTestCount")
    for key, value in (("failedTests", want_failed), ("totalTestCount", want_total)):
        if type(value) is not int or value < 0:
            return f"summary {key} must be a non-negative integer"
    if want_failed > want_total:
        return "summary failedTests exceeds totalTestCount"
    problems = []
    if isinstance(want_failed, int) and want_failed != parsed_failed:
        problems.append(f"failures+errors={parsed_failed} but summary failedTests={want_failed}")
    if isinstance(want_total, int) and want_total != parsed_total:
        problems.append(f"tests={parsed_total} but summary totalTestCount={want_total}")
    if summary.get("result") == "Failed" and parsed_failed == 0:
        problems.append("summary result is Failed but no failing test case was parsed")
    return "; ".join(problems) or None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="xcresult_to_junit.py",
        description="Convert an .xcresult bundle (or saved xcresulttool JSON) to JUnit XML.",
    )
    parser.add_argument("bundle", nargs="?", metavar="<bundle.xcresult>",
                        help="Path to the .xcresult bundle produced by xcodebuild.")
    parser.add_argument("--tests-json", help="Saved output of `xcresulttool get test-results tests`.")
    parser.add_argument("--summary-json", help="Saved output of `xcresulttool get test-results summary`.")
    parser.add_argument("--output", default="junit.xml", help="Output file path (default: junit.xml).")
    args = parser.parse_args(argv)
    if bool(args.bundle) == bool(args.tests_json):
        parser.error("pass exactly one of <bundle.xcresult> or --tests-json")
    return args


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    summary: Optional[Dict[str, Any]] = None
    if args.bundle:
        bundle = os.path.abspath(args.bundle)
        if not os.path.exists(bundle):
            print(f"error: bundle not found: {bundle}", file=sys.stderr)
            return 1
        data = _run_xcresulttool(["get", "test-results", "tests", "--path", bundle])
        summary = _run_xcresulttool(["get", "test-results", "summary", "--path", bundle])
        name = os.path.basename(bundle).replace(".xcresult", "")
    else:
        data = _load_json_file(args.tests_json)
        if args.summary_json:
            summary = _load_json_file(args.summary_json)
        name = os.path.basename(args.tests_json).replace(".json", "")

    tree = build_junit(data, name)
    if hasattr(ET, "indent"):
        ET.indent(tree)
    tree.write(args.output, encoding="unicode", xml_declaration=True)
    root = tree.getroot()
    print(f"JUnit XML written to: {args.output} (tests={root.get('tests')} "
          f"failures={root.get('failures')} errors={root.get('errors')} skipped={root.get('skipped')})")

    if summary is not None:
        problem = check_against_summary(tree, summary)
        if problem:
            print(f"error: JUnit report disagrees with xcresult summary: {problem}", file=sys.stderr)
            return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
