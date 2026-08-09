#!/usr/bin/env python3
"""Convert an .xcresult bundle to JUnit XML for CI publishing.

Uses xcresulttool (Xcode 16+) to read test results and emits a standard
JUnit XML document: <testsuites><testsuite><testcase> with <failure> elements
for failed tests.

Usage:
    python3 xcresult_to_junit.py <bundle.xcresult> [--output junit.xml]

Requirements:
    - Xcode 16+ (xcresulttool with 'get test-results tests' subcommand)
    - Python 3.9+ (stdlib only — no third-party dependencies)

Exit codes:
    0  Success
    1  Usage error / xcresulttool not found / bundle not found
    2  xcresulttool returned a non-zero exit code
    3  Unexpected output format
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# xcresulttool helpers
# ---------------------------------------------------------------------------

def _find_xcresulttool() -> str:
    """Return the absolute path to xcresulttool or raise SystemExit."""
    tool = shutil.which("xcresulttool")
    if tool:
        return tool
    # Try the Xcode-bundled path as a fallback
    xcode_path = "/Applications/Xcode.app/Contents/Developer/usr/bin/xcresulttool"
    if os.path.isfile(xcode_path):
        return xcode_path
    print(
        "error: xcresulttool not found.\n"
        "  Ensure Xcode 16+ is installed and the Xcode Command Line Tools are\n"
        "  active (`xcode-select --install` or `sudo xcode-select -s /Applications/Xcode.app`).",
        file=sys.stderr,
    )
    sys.exit(1)


def _load_xcresult_json(xcresulttool: str, bundle_path: str) -> dict[str, Any]:
    """Run xcresulttool and return parsed JSON.

    Xcode 16+ subcommand:
        xcresulttool get test-results tests --path <bundle> --format json
    """
    cmd = [
        xcresulttool,
        "get",
        "test-results",
        "tests",
        "--path",
        bundle_path,
        "--format",
        "json",
    ]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError:
        print(f"error: failed to launch {xcresulttool}", file=sys.stderr)
        sys.exit(1)

    if result.returncode != 0:
        print(
            f"error: xcresulttool exited with code {result.returncode}.\n"
            f"  stderr: {result.stderr.strip()}",
            file=sys.stderr,
        )
        sys.exit(2)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        print(
            f"error: xcresulttool output is not valid JSON: {exc}",
            file=sys.stderr,
        )
        sys.exit(3)


# ---------------------------------------------------------------------------
# Data extraction
# ---------------------------------------------------------------------------

def _iter_test_nodes(nodes: list[dict[str, Any]]):
    """Recursively yield leaf test-node dicts (individual test cases)."""
    for node in nodes:
        children = node.get("children", [])
        if children:
            yield from _iter_test_nodes(children)
        else:
            yield node


def _duration_str(node: dict[str, Any]) -> str:
    """Return duration in seconds as a string, defaulting to '0'."""
    dur = node.get("duration")
    if dur is None:
        return "0"
    try:
        return str(float(dur))
    except (TypeError, ValueError):
        return "0"


def _build_suites(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Group leaf test nodes by their suite name.

    Returns {suite_name: [test_node, ...]}
    """
    suites: dict[str, list[dict[str, Any]]] = {}
    top_nodes = data.get("testNodes", data.get("tests", []))
    if not isinstance(top_nodes, list):
        print(
            "error: unexpected xcresulttool JSON structure — "
            "expected 'testNodes' or 'tests' list at top level.",
            file=sys.stderr,
        )
        sys.exit(3)

    for node in _iter_test_nodes(top_nodes):
        # The node name typically looks like "ClassName/testMethodName()" or
        # a plain method name.  The parent suite is stored in 'suiteName' or
        # derived from the node name prefix.
        suite = node.get("suiteName") or node.get("nodeType", "UnknownSuite")
        name = node.get("name", "unknown")
        suites.setdefault(suite, []).append({"name": name, "node": node})
    return suites


# ---------------------------------------------------------------------------
# JUnit XML assembly
# ---------------------------------------------------------------------------

def _make_junit_xml(data: dict[str, Any], bundle_path: str) -> ET.ElementTree:
    """Return an ElementTree representing the JUnit XML document."""
    suites_map = _build_suites(data)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    bundle_name = os.path.basename(bundle_path).replace(".xcresult", "")

    testsuites_el = ET.Element("testsuites", name=bundle_name)

    total_tests = 0
    total_failures = 0
    total_errors = 0

    for suite_name, cases in suites_map.items():
        suite_tests = len(cases)
        suite_failures = 0
        suite_errors = 0
        suite_time = 0.0

        testsuite_el = ET.SubElement(
            testsuites_el,
            "testsuite",
            name=suite_name,
            timestamp=timestamp,
        )

        for case in cases:
            node = case["node"]
            test_name = case["name"]
            duration = _duration_str(node)
            try:
                suite_time += float(duration)
            except ValueError:
                pass

            status = (node.get("result") or node.get("nodeResult") or "").lower()
            is_failed = status in {"failure", "failed", "unexpected failure"}
            is_errored = status in {"error"}

            testcase_el = ET.SubElement(
                testsuite_el,
                "testcase",
                classname=suite_name,
                name=test_name,
                time=duration,
            )

            if is_failed:
                suite_failures += 1
                failure_message = _collect_failure_message(node)
                failure_el = ET.SubElement(
                    testcase_el,
                    "failure",
                    message=failure_message or "Test failed",
                )
                failure_el.text = failure_message or ""
            elif is_errored:
                suite_errors += 1
                error_el = ET.SubElement(
                    testcase_el,
                    "error",
                    message="Test error",
                )
                error_el.text = _collect_failure_message(node) or ""
            elif status in {"skipped", "expected failure"}:
                ET.SubElement(testcase_el, "skipped")

        testsuite_el.set("tests", str(suite_tests))
        testsuite_el.set("failures", str(suite_failures))
        testsuite_el.set("errors", str(suite_errors))
        testsuite_el.set("time", f"{suite_time:.3f}")

        total_tests += suite_tests
        total_failures += suite_failures
        total_errors += suite_errors

    testsuites_el.set("tests", str(total_tests))
    testsuites_el.set("failures", str(total_failures))
    testsuites_el.set("errors", str(total_errors))

    return ET.ElementTree(testsuites_el)


def _collect_failure_message(node: dict[str, Any]) -> str:
    """Extract a human-readable failure message from a test node."""
    # Try common fields emitted by xcresulttool
    for key in ("failureSummaries", "failureMessages", "failures"):
        items = node.get(key)
        if isinstance(items, list) and items:
            parts = []
            for item in items:
                if isinstance(item, dict):
                    msg = item.get("message") or item.get("description") or str(item)
                    loc = item.get("fileName", "")
                    line = item.get("lineNumber", "")
                    if loc:
                        parts.append(f"{loc}:{line}: {msg}" if line else f"{loc}: {msg}")
                    else:
                        parts.append(msg)
                elif isinstance(item, str):
                    parts.append(item)
            return "\n".join(parts)
    return node.get("message") or node.get("description") or ""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="xcresult_to_junit.py",
        description=(
            "Convert an .xcresult bundle to JUnit XML for CI publishing.\n"
            "Requires Xcode 16+ (xcresulttool with 'get test-results tests' support)."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "bundle",
        metavar="<bundle.xcresult>",
        help="Path to the .xcresult bundle produced by xcodebuild.",
    )
    parser.add_argument(
        "--output",
        metavar="<path>",
        default="junit.xml",
        help="Output file path (default: junit.xml).",
    )
    return parser.parse_args()


def _indent_xml(element: ET.Element, level: int = 0) -> None:
    """Add pretty-print indentation in-place (Python < 3.9 compat shim)."""
    indent = "\n" + "  " * level
    if len(element):
        element.text = indent + "  "
        element.tail = indent
        for child in element:
            _indent_xml(child, level + 1)
        # Last child tail closes the parent
        child.tail = indent  # type: ignore[possibly-undefined]
    else:
        element.tail = indent


def main() -> None:
    args = _parse_args()

    bundle_path = os.path.abspath(args.bundle)
    if not os.path.exists(bundle_path):
        print(f"error: bundle not found: {bundle_path}", file=sys.stderr)
        sys.exit(1)

    xcresulttool = _find_xcresulttool()
    data = _load_xcresult_json(xcresulttool, bundle_path)
    tree = _make_junit_xml(data, bundle_path)

    _indent_xml(tree.getroot())
    tree.write(args.output, encoding="unicode", xml_declaration=True)
    print(f"JUnit XML written to: {args.output}")


if __name__ == "__main__":
    main()
