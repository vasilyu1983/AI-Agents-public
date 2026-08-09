#!/usr/bin/env python3
"""
check_perf_budget.py

Reads a performance budget file (perf-budget.json) and validates a Lighthouse
or custom report JSON against it. Exits 0 if all thresholds pass, 1 if any
threshold is breached.

Budget file keys are upper bounds (fail if report value > threshold) except
'lighthouse_performance_score' which is a lower bound (fail if score < threshold).

Supported budget keys:
  lcp_ms                    Largest Contentful Paint in milliseconds
  inp_ms                    Interaction to Next Paint in milliseconds
  cls                       Cumulative Layout Shift score
  fcp_ms                    First Contentful Paint in milliseconds
  tbt_ms                    Total Blocking Time in milliseconds
  ttfb_ms                   Time to First Byte in milliseconds
  js_bytes                  Total JavaScript transfer size in bytes
  css_bytes                 Total CSS transfer size in bytes
  image_bytes               Total image transfer size in bytes
  total_bytes               Total page transfer size in bytes
  requests                  Total number of requests
  lighthouse_performance_score  Lighthouse performance score (0-100, lower bound)

Usage:
  python3 check_perf_budget.py --help
  python3 check_perf_budget.py --budget perf-budget.json --report lighthouse-report.json
  python3 check_perf_budget.py --budget perf-budget.json --report report.json --format custom
  python3 check_perf_budget.py --generate-budget > perf-budget.json
  python3 check_perf_budget.py --generate-report > sample-report.json

Exit codes:
  0  All thresholds pass
  1  One or more thresholds breached
  2  Usage error or invalid input
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Budget and metric definitions
# ---------------------------------------------------------------------------

@dataclass
class MetricSpec:
    key: str
    label: str
    unit: str
    lower_bound: bool = False  # if True, fail when value < threshold


METRICS: list[MetricSpec] = [
    MetricSpec("lcp_ms", "LCP", "ms"),
    MetricSpec("inp_ms", "INP", "ms"),
    MetricSpec("cls", "CLS", "score"),
    MetricSpec("fcp_ms", "FCP", "ms"),
    MetricSpec("tbt_ms", "TBT", "ms"),
    MetricSpec("ttfb_ms", "TTFB", "ms"),
    MetricSpec("js_bytes", "JS bytes", "bytes"),
    MetricSpec("css_bytes", "CSS bytes", "bytes"),
    MetricSpec("image_bytes", "Image bytes", "bytes"),
    MetricSpec("total_bytes", "Total bytes", "bytes"),
    MetricSpec("requests", "Requests", "count"),
    MetricSpec("lighthouse_performance_score", "Lighthouse score", "score (0-100)", lower_bound=True),
]

METRIC_BY_KEY: dict[str, MetricSpec] = {m.key: m for m in METRICS}

# ---------------------------------------------------------------------------
# Lighthouse JSON extraction
# ---------------------------------------------------------------------------

LH_AUDIT_MAP: dict[str, str] = {
    "lcp_ms": "largest-contentful-paint",
    "inp_ms": "experimental-interaction-to-next-paint",
    "cls": "cumulative-layout-shift",
    "fcp_ms": "first-contentful-paint",
    "tbt_ms": "total-blocking-time",
    "ttfb_ms": "server-response-time",
}

LH_RESOURCE_SUMMARY_MAP: dict[str, str] = {
    "js_bytes": "Script",
    "css_bytes": "Stylesheet",
    "image_bytes": "Image",
}


def extract_lighthouse_metrics(report: dict) -> dict[str, float | None]:
    """Extract budget-relevant metrics from a Lighthouse JSON report."""
    metrics: dict[str, float | None] = {m.key: None for m in METRICS}

    audits = report.get("audits", {})

    # Timing audits
    for budget_key, audit_key in LH_AUDIT_MAP.items():
        audit = audits.get(audit_key, {})
        value = audit.get("numericValue")
        if value is not None:
            metrics[budget_key] = float(value)

    # Lighthouse performance score
    categories = report.get("categories", {})
    perf = categories.get("performance", {})
    score = perf.get("score")
    if score is not None:
        metrics["lighthouse_performance_score"] = float(score) * 100  # 0-1 -> 0-100

    # Resource summary (resource-summary audit)
    rs_audit = audits.get("resource-summary", {})
    items = rs_audit.get("details", {}).get("items", [])
    total_size = 0
    total_requests = 0
    for item in items:
        label = item.get("label", "")
        size = item.get("transferSize", 0)
        count = item.get("requestCount", 0)
        total_size += size
        total_requests += count
        for budget_key, rs_label in LH_RESOURCE_SUMMARY_MAP.items():
            if label == rs_label:
                metrics[budget_key] = float(size)
    if total_size > 0:
        metrics["total_bytes"] = float(total_size)
    if total_requests > 0:
        metrics["requests"] = float(total_requests)

    return metrics


def extract_custom_metrics(report: dict) -> dict[str, float | None]:
    """
    Extract metrics from a flat or nested custom report.
    Supports top-level keys matching budget keys, or a 'metrics' sub-object.
    """
    raw: dict[str, Any] = report.get("metrics", report)
    result: dict[str, float | None] = {}
    for m in METRICS:
        val = raw.get(m.key)
        if val is not None:
            try:
                result[m.key] = float(val)
            except (TypeError, ValueError):
                result[m.key] = None
        else:
            result[m.key] = None
    return result


# ---------------------------------------------------------------------------
# Budget validation
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    key: str
    label: str
    unit: str
    threshold: float
    actual: float | None
    passed: bool
    lower_bound: bool


def validate_budget(
    budget: dict,
    report_metrics: dict[str, float | None],
) -> list[CheckResult]:
    results: list[CheckResult] = []

    for key, threshold_raw in budget.items():
        if key not in METRIC_BY_KEY:
            continue
        try:
            threshold = float(threshold_raw)
        except (TypeError, ValueError):
            continue

        spec = METRIC_BY_KEY[key]
        actual = report_metrics.get(key)

        if actual is None:
            # Metric not present in report — skip, do not fail
            continue

        if spec.lower_bound:
            passed = actual >= threshold
        else:
            passed = actual <= threshold

        results.append(CheckResult(
            key=key,
            label=spec.label,
            unit=spec.unit,
            threshold=threshold,
            actual=actual,
            passed=passed,
            lower_bound=spec.lower_bound,
        ))

    return results


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(results: list[CheckResult], budget_path: str, report_path: str) -> int:
    failures = [r for r in results if not r.passed]
    passes = [r for r in results if r.passed]
    skipped_count = len(METRICS) - len(results)

    status = "PASS" if not failures else "FAIL"
    print(f"## Performance Budget Check")
    print()
    print(f"- Status:  {status}")
    print(f"- Budget:  {budget_path}")
    print(f"- Report:  {report_path}")
    print(f"- Checks:  {len(results)} ({len(passes)} pass, {len(failures)} fail, {skipped_count} not in report)")
    print()

    if failures:
        print("## Failures")
        for r in failures:
            direction = "below" if r.lower_bound else "above"
            print(
                f"  FAIL  {r.label:<35} actual={_fmt(r.actual, r.unit)}  "
                f"threshold={_fmt(r.threshold, r.unit)}  "
                f"({direction} budget)"
            )
        print()

    if passes:
        print("## Passing Checks")
        for r in passes:
            print(
                f"  pass  {r.label:<35} actual={_fmt(r.actual, r.unit)}  "
                f"threshold={_fmt(r.threshold, r.unit)}"
            )
        print()

    return 0 if not failures else 1


def _fmt(value: float | None, unit: str) -> str:
    if value is None:
        return "n/a"
    if unit == "bytes":
        return f"{value / 1024:.1f}kB"
    if unit in ("ms",):
        return f"{value:.0f}ms"
    if unit == "score (0-100)":
        return f"{value:.0f}"
    return f"{value:.3f}"


# ---------------------------------------------------------------------------
# Template generators
# ---------------------------------------------------------------------------

SAMPLE_BUDGET = {
    "lcp_ms": 2500,
    "inp_ms": 200,
    "cls": 0.1,
    "fcp_ms": 1800,
    "tbt_ms": 200,
    "ttfb_ms": 800,
    "js_bytes": 350000,
    "css_bytes": 75000,
    "image_bytes": 600000,
    "total_bytes": 1200000,
    "requests": 50,
    "lighthouse_performance_score": 90,
}

SAMPLE_REPORT = {
    "metrics": {
        "lcp_ms": 2100,
        "inp_ms": 180,
        "cls": 0.05,
        "fcp_ms": 1400,
        "tbt_ms": 150,
        "ttfb_ms": 620,
        "js_bytes": 310000,
        "css_bytes": 62000,
        "image_bytes": 450000,
        "total_bytes": 980000,
        "requests": 42,
        "lighthouse_performance_score": 93,
    }
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a performance report against a budget file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--budget", type=Path, help="Path to perf-budget.json")
    parser.add_argument("--report", type=Path, help="Path to the report JSON to validate")
    parser.add_argument(
        "--format",
        choices=["lighthouse", "custom"],
        default="lighthouse",
        help="Report format: 'lighthouse' (default) or 'custom' (flat/nested metrics object)",
    )
    parser.add_argument(
        "--generate-budget",
        action="store_true",
        help="Print a sample perf-budget.json to stdout and exit",
    )
    parser.add_argument(
        "--generate-report",
        action="store_true",
        help="Print a sample custom report JSON to stdout and exit",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.generate_budget:
        print(json.dumps(SAMPLE_BUDGET, indent=2))
        return 0

    if args.generate_report:
        print(json.dumps(SAMPLE_REPORT, indent=2))
        return 0

    if not args.budget or not args.report:
        print("Error: --budget and --report are required", file=sys.stderr)
        print("Run with --help for usage.", file=sys.stderr)
        return 2

    budget_path = args.budget.resolve()
    report_path = args.report.resolve()

    for p, label in [(budget_path, "budget"), (report_path, "report")]:
        if not p.exists():
            print(f"Error: {label} file not found: {p}", file=sys.stderr)
            return 2

    try:
        budget = json.loads(budget_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in budget file: {exc}", file=sys.stderr)
        return 2

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"Error: invalid JSON in report file: {exc}", file=sys.stderr)
        return 2

    if not isinstance(budget, dict):
        print("Error: budget file must be a JSON object", file=sys.stderr)
        return 2

    if not isinstance(report, dict):
        print("Error: report file must be a JSON object", file=sys.stderr)
        return 2

    if args.format == "lighthouse":
        report_metrics = extract_lighthouse_metrics(report)
    else:
        report_metrics = extract_custom_metrics(report)

    results = validate_budget(budget, report_metrics)

    return print_report(results, str(budget_path), str(report_path))


if __name__ == "__main__":
    sys.exit(main())
