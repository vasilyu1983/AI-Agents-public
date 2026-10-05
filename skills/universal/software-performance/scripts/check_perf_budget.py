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
  2  Usage error, invalid input, or no budget metric found in the report

Note: INP is a field metric. It needs real user interactions, so a Lighthouse
navigation (lab) report has no INP value; TBT is the lab proxy. With
--format lighthouse, an inp_ms budget that the report cannot satisfy is only
accepted when tbt_ms is also budgeted and present (TBT then gates the lab run);
otherwise the script exits 2 instead of passing silently. Take INP itself from
field/RUM data (for example a custom report built from CrUX or your RUM tool).
Every other budgeted metric must be present, or the script exits 2. Unknown
budget keys and invalid numbers also exit 2; partial reports cannot pass.
"""

from __future__ import annotations

import argparse
import json
import math
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


def number(value: Any, label: str, maximum: float | None = None) -> float:
    """Accept JSON numbers only, without coercing booleans or strings."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    try:
        result = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be finite") from exc
    if not math.isfinite(result) or result < 0:
        raise ValueError(f"{label} must be finite and non-negative")
    if maximum is not None and result > maximum:
        raise ValueError(f"{label} must be at most {maximum:g}")
    return result


def object_value(value: Any, label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result

# ---------------------------------------------------------------------------
# Lighthouse JSON extraction
# ---------------------------------------------------------------------------

# Audit ids tried in order. Accept INP when an imported report actually contains
# it; navigation reports normally omit it. Keep the legacy experimental id.
LH_AUDIT_MAP: dict[str, tuple[str, ...]] = {
    "lcp_ms": ("largest-contentful-paint",),
    "inp_ms": ("interaction-to-next-paint", "experimental-interaction-to-next-paint"),
    "cls": ("cumulative-layout-shift",),
    "fcp_ms": ("first-contentful-paint",),
    "tbt_ms": ("total-blocking-time",),
    "ttfb_ms": ("server-response-time",),
}

LH_RESOURCE_SUMMARY_MAP: dict[str, str] = {
    "js_bytes": "Script",
    "css_bytes": "Stylesheet",
    "image_bytes": "Image",
}


def extract_lighthouse_metrics(report: dict) -> dict[str, float | None]:
    """Extract budget-relevant metrics from a Lighthouse JSON report."""
    metrics: dict[str, float | None] = {m.key: None for m in METRICS}

    audits = object_value(report.get("audits", {}), "audits")

    # Timing audits
    for budget_key, audit_keys in LH_AUDIT_MAP.items():
        for audit_key in audit_keys:
            audit = object_value(audits.get(audit_key, {}), audit_key)
            value = audit.get("numericValue")
            if value is not None:
                metrics[budget_key] = number(value, audit_key)
                break

    # Lighthouse performance score
    categories = object_value(report.get("categories", {}), "categories")
    perf = object_value(categories.get("performance", {}), "performance")
    score = perf.get("score")
    if score is not None:
        metrics["lighthouse_performance_score"] = number(score, "performance score", 1) * 100

    # Resource summary (resource-summary audit)
    rs_audit = object_value(audits.get("resource-summary", {}), "resource-summary")
    details = object_value(rs_audit.get("details", {}), "resource-summary details")
    items = details.get("items", [])
    if not isinstance(items, list):
        raise ValueError("resource-summary items must be an array")
    total_size = 0
    total_requests = 0
    sizes_complete = counts_complete = True
    resource_rows = 0
    # Lighthouse emits a "total" row plus per-type rows and an overlapping
    # "third-party" row; summing every row would double-count bytes.
    total_row = None
    for item in items:
        item = object_value(item, "resource-summary item")
        label = item.get("label", "")
        rtype = str(item.get("resourceType", "")).lower()
        size = item.get("transferSize")
        count = item.get("requestCount")
        if size is not None:
            size = number(size, "transferSize")
        if count is not None:
            count = number(count, "requestCount")
        if rtype == "total" or label == "Total":
            if total_row is not None:
                raise ValueError("resource-summary has duplicate total rows")
            total_row = (size, count)
            continue
        if rtype == "third-party" or label == "Third-party":
            continue
        resource_rows += 1
        if size is None:
            sizes_complete = False
        else:
            total_size += size
        if count is None:
            counts_complete = False
        else:
            total_requests += count
        for budget_key, rs_label in LH_RESOURCE_SUMMARY_MAP.items():
            if label == rs_label or rtype == rs_label.lower():
                metrics[budget_key] = size
    if total_row is not None:
        total_size, total_requests = total_row
        sizes_complete = total_size is not None
        counts_complete = total_requests is not None
    if sizes_complete and (total_row is not None or resource_rows):
        metrics["total_bytes"] = number(total_size, "total transferSize")
    if counts_complete and (total_row is not None or resource_rows):
        metrics["requests"] = number(total_requests, "total requestCount")

    return metrics


def extract_custom_metrics(report: dict) -> dict[str, float | None]:
    """
    Extract metrics from a flat or nested custom report.
    Supports top-level keys matching budget keys, or a 'metrics' sub-object.
    """
    raw = object_value(report.get("metrics", report), "metrics")
    result: dict[str, float | None] = {}
    for m in METRICS:
        val = raw.get(m.key)
        if val is not None:
            maximum = 100 if m.lower_bound else None
            result[m.key] = number(val, m.key, maximum)
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

    if not budget:
        raise ValueError("budget must contain at least one metric")
    for key, threshold_raw in budget.items():
        if key not in METRIC_BY_KEY:
            raise ValueError(f"unknown budget metric: {key}")
        threshold = number(threshold_raw, f"budget {key}", 100 if METRIC_BY_KEY[key].lower_bound else None)

        spec = METRIC_BY_KEY[key]
        actual = report_metrics.get(key)

        if actual is None:
            # CLI rejects missing metrics, except its explicit Lighthouse INP proxy.
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

def missing_budget_keys(budget: dict, report_metrics: dict[str, float | None]) -> list[str]:
    """Budgeted metrics the report has no value for (these were not checked)."""
    return [k for k in budget if k in METRIC_BY_KEY and report_metrics.get(k) is None]


def lab_inp_problem(budget: dict, report_metrics: dict[str, float | None]) -> str | None:
    """Return an error when a lab report cannot gate an INP budget at all.

    Navigation reports normally omit INP; absent INP can only be explicitly
    skipped here if TBT is budgeted and measured. TBT does not prove field INP.
    """
    if "inp_ms" not in budget or report_metrics.get("inp_ms") is not None:
        return None
    if "tbt_ms" in budget and report_metrics.get("tbt_ms") is not None:
        return None
    return (
        "inp_ms is budgeted but the Lighthouse report has no INP value (INP is a field "
        "metric; navigation runs normally omit it) and no tbt_ms budget/value is available as "
        "the lab proxy. Add tbt_ms to the budget, or check INP against field/RUM data "
        "with --format custom."
    )


def print_report(
    results: list[CheckResult],
    budget_path: str,
    report_path: str,
    missing: list[str] | None = None,
) -> int:
    failures = [r for r in results if not r.passed]
    passes = [r for r in results if r.passed]
    missing = missing or []
    skipped_count = len(missing)

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

    if missing:
        print("## Not Checked (budgeted but missing from report)")
        for key in missing:
            note = ""
            if key == "inp_ms":
                note = "  (INP is a field metric; TBT gates this lab run)"
            print(f"  SKIP  {METRIC_BY_KEY[key].label:<35}{note}")
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
        budget = json.loads(budget_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"Error: cannot read budget file {budget_path}: {exc}", file=sys.stderr)
        return 2

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"), object_pairs_hook=unique_object)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"Error: cannot read report file {report_path}: {exc}", file=sys.stderr)
        return 2

    if not isinstance(budget, dict):
        print("Error: budget file must be a JSON object", file=sys.stderr)
        return 2

    if not isinstance(report, dict):
        print("Error: report file must be a JSON object", file=sys.stderr)
        return 2

    try:
        if args.format == "lighthouse":
            report_metrics = extract_lighthouse_metrics(report)
        else:
            report_metrics = extract_custom_metrics(report)
        results = validate_budget(budget, report_metrics)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    if args.format == "lighthouse":
        problem = lab_inp_problem(budget, report_metrics)
        if problem:
            print(f"Error: {problem}", file=sys.stderr)
            return 2

    missing = missing_budget_keys(budget, report_metrics)
    required_missing = [key for key in missing if not (args.format == "lighthouse" and key == "inp_ms")]
    if required_missing:
        print(f"Error: budgeted metrics missing from report: {', '.join(required_missing)}", file=sys.stderr)
        return 2

    if not results:
        # Nothing matched: a wrong --format or an empty report must not pass silently.
        print(
            "Error: no budget metric was found in the report "
            f"(format={args.format}); check --format and the report contents.",
            file=sys.stderr,
        )
        return 2

    return print_report(
        results, str(budget_path), str(report_path), missing
    )


if __name__ == "__main__":
    sys.exit(main())
