#!/usr/bin/env python3
"""Performance budget checker for web, API, and load test results.

Subcommands:
  check   -- Validate measured results against performance budgets. PASS/WARN/FAIL
             per metric and an overall CI gate verdict.
  plan    -- Recommend CI test tier assignment (PR_gate / nightly / pre_release)
             for each test scenario based on type, duration, and resource cost.
  report  -- Full Markdown performance test report combining budget check and
             test execution matrix.
"""

import argparse
import json
import math
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Core Web Vitals thresholds (ms / unitless)
LCP_WARN = 2500   # ms  — "needs improvement" boundary
LCP_FAIL = 4000   # ms  — "poor" boundary

INP_WARN = 200    # ms
INP_FAIL = 500    # ms

CLS_WARN = 0.1    # unitless
CLS_FAIL = 0.25   # unitless

# CI tier assignment rules
# Each scenario is classified by (type, duration_minutes, virtual_users).
# Types: load, stress, soak, spike
# Tiers: PR_gate, nightly, pre_release

CI_TIER_LABELS = {
    "PR_gate": "PR_gate",
    "nightly": "nightly",
    "pre_release": "pre_release",
}

# Status labels and emoji-free symbols
PASS = "PASS"
WARN = "WARN"
FAIL = "FAIL"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _load_json(path: str) -> dict:
    try:
        with Path(path).open(encoding="utf-8") as fh:
            data = json.load(fh, object_pairs_hook=_unique_object)
    except (OSError, ValueError, UnicodeError) as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    return _object(data, "input")


def _object(value, label):
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be an object")
    return value


def _number(value, label, positive=False, maximum=None):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a number")
    try:
        n = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be finite") from exc
    if not math.isfinite(n) or n < 0 or (positive and n == 0):
        raise ValueError(f"{label} must be finite and {'positive' if positive else 'non-negative'}")
    if maximum is not None and n > maximum:
        raise ValueError(f"{label} must be at most {maximum}")
    return n


def _today() -> str:
    return str(date.today())


# ---------------------------------------------------------------------------
# Budget evaluation logic
# ---------------------------------------------------------------------------


def _check_lcp(actual: float, budget: float) -> tuple[str, str]:
    """Return (status, note) for LCP metric.

    The user's `budget` is the authoritative gate: any value over budget is a
    FAIL. Google's CWV bands (LCP_WARN/LCP_FAIL) are attached only as
    informational context in the note, not as an alternate pass condition —
    a budget tighter than Google's "good" threshold must still fail past it.
    """
    band = "good" if actual <= LCP_WARN else ("needs improvement" if actual <= LCP_FAIL else "poor")
    if actual <= budget:
        return PASS, f"{actual}ms — within budget ({budget}ms); Google CWV: {band}"
    return FAIL, f"{actual}ms — exceeds budget ({budget}ms); Google CWV: {band}"


def _check_inp(actual: float, budget: float) -> tuple[str, str]:
    """Return (status, note) for INP metric. Budget is authoritative; see _check_lcp."""
    band = "good" if actual <= INP_WARN else ("needs improvement" if actual <= INP_FAIL else "poor")
    if actual <= budget:
        return PASS, f"{actual}ms — within budget ({budget}ms); Google CWV: {band}"
    return FAIL, f"{actual}ms — exceeds budget ({budget}ms); Google CWV: {band}"


def _check_cls(actual: float, budget: float) -> tuple[str, str]:
    """Return (status, note) for CLS metric. Budget is authoritative; see _check_lcp."""
    band = "good" if actual <= CLS_WARN else ("needs improvement" if actual <= CLS_FAIL else "poor")
    if actual <= budget:
        return PASS, f"{actual:.3f} — within budget ({budget}); Google CWV: {band}"
    return FAIL, f"{actual:.3f} — exceeds budget ({budget}); Google CWV: {band}"


def _check_api_p95(actual: float, budget: float) -> tuple[str, str]:
    ratio = actual / budget
    if ratio <= 1.0:
        return PASS, f"{actual}ms — within budget ({budget}ms)"
    if ratio <= 1.25:
        return WARN, f"{actual}ms — {ratio:.0%} of budget ({budget}ms); within 25% headroom"
    return FAIL, f"{actual}ms — exceeds budget ({budget}ms) by more than 25%"


def _check_api_p99(actual: float, budget: float, label: str = "p99") -> tuple[str, str]:
    """Tail-latency budgets (p99, p99.9). Tighter WARN zone — tail regressions matter."""
    ratio = actual / budget
    if ratio <= 1.0:
        return PASS, f"{actual}ms — within {label} budget ({budget}ms)"
    if ratio <= 1.15:
        return WARN, f"{actual}ms — {ratio:.0%} of {label} budget ({budget}ms); under 15% headroom"
    return FAIL, f"{actual}ms — exceeds {label} budget ({budget}ms) by more than 15%"


def _check_throughput(actual: float, minimum: float) -> tuple[str, str]:
    ratio = actual / minimum
    if ratio >= 1.0:
        return PASS, f"{actual} rps — meets minimum ({minimum} rps)"
    if ratio >= 0.9:
        return WARN, f"{actual} rps — {(1 - ratio):.0%} below minimum ({minimum} rps)"
    return FAIL, f"{actual} rps — more than 10% below minimum ({minimum} rps)"


def _check_error_rate(actual: float, budget: float) -> tuple[str, str]:
    if actual <= budget * 0.5:
        return PASS, f"{actual}% — well within budget ({budget}%)"
    if actual <= budget:
        return PASS, f"{actual}% — within budget ({budget}%)"
    if actual <= budget * 1.5:
        return WARN, f"{actual}% — exceeds budget ({budget}%), under 1.5x"
    return FAIL, f"{actual}% — significantly exceeds budget ({budget}%)"


def _check_bundle_size(actual: float, budget: float) -> tuple[str, str]:
    ratio = actual / budget
    if ratio <= 1.0:
        return PASS, f"{actual}KB — within budget ({budget}KB)"
    if ratio <= 1.15:
        return WARN, f"{actual}KB — {ratio:.0%} of budget ({budget}KB); within 15% headroom"
    return FAIL, f"{actual}KB — exceeds budget ({budget}KB) by more than 15%"


def _evaluate_budgets(data: dict) -> list[dict]:
    """Return a list of {metric, status, note} dicts for all budget metrics."""
    data = _object(data, "input")
    budgets = _object(data.get("budgets"), "budgets")
    results = _object(data.get("results"), "results")
    supported = {"lcp_ms", "inp_ms", "cls", "api_p95_ms", "api_p99_ms", "api_p999_ms",
                 "api_throughput_rps", "error_rate_pct", "bundle_size_kb"}
    if not budgets:
        raise ValueError("budgets must contain at least one supported metric")
    for key, value in budgets.items():
        if key not in supported:
            raise ValueError(f"unknown budget metric: {key}")
        _number(value, f"budget {key}", positive=key in {
            "api_p95_ms", "api_p99_ms", "api_p999_ms", "api_throughput_rps", "bundle_size_kb"
        }, maximum=100 if key == "error_rate_pct" else None)
        if key not in results:
            raise ValueError(f"result missing for budget metric: {key}")
        _number(results[key], f"result {key}", maximum=100 if key == "error_rate_pct" else None)
    checks = []

    # LCP
    if "lcp_ms" in budgets and "lcp_ms" in results:
        status, note = _check_lcp(float(results["lcp_ms"]), float(budgets["lcp_ms"]))
        checks.append({"metric": "LCP", "actual": results["lcp_ms"], "budget": budgets["lcp_ms"], "status": status, "note": note})

    # INP
    if "inp_ms" in budgets and "inp_ms" in results:
        status, note = _check_inp(float(results["inp_ms"]), float(budgets["inp_ms"]))
        checks.append({"metric": "INP", "actual": results["inp_ms"], "budget": budgets["inp_ms"], "status": status, "note": note})

    # CLS
    if "cls" in budgets and "cls" in results:
        status, note = _check_cls(float(results["cls"]), float(budgets["cls"]))
        checks.append({"metric": "CLS", "actual": results["cls"], "budget": budgets["cls"], "status": status, "note": note})

    # API p95 latency
    if "api_p95_ms" in budgets and "api_p95_ms" in results:
        status, note = _check_api_p95(float(results["api_p95_ms"]), float(budgets["api_p95_ms"]))
        checks.append({"metric": "API p95", "actual": results["api_p95_ms"], "budget": budgets["api_p95_ms"], "status": status, "note": note})

    # API p99 latency (tail; tighter WARN zone)
    if "api_p99_ms" in budgets and "api_p99_ms" in results:
        status, note = _check_api_p99(float(results["api_p99_ms"]), float(budgets["api_p99_ms"]), "p99")
        checks.append({"metric": "API p99", "actual": results["api_p99_ms"], "budget": budgets["api_p99_ms"], "status": status, "note": note})

    # API p99.9 latency (deep tail; surfaces coordinated-omission and queue-buildup)
    if "api_p999_ms" in budgets and "api_p999_ms" in results:
        status, note = _check_api_p99(float(results["api_p999_ms"]), float(budgets["api_p999_ms"]), "p99.9")
        checks.append({"metric": "API p99.9", "actual": results["api_p999_ms"], "budget": budgets["api_p999_ms"], "status": status, "note": note})

    # API throughput
    if "api_throughput_rps" in budgets and "api_throughput_rps" in results:
        status, note = _check_throughput(float(results["api_throughput_rps"]), float(budgets["api_throughput_rps"]))
        checks.append({"metric": "Throughput", "actual": results["api_throughput_rps"], "budget": budgets["api_throughput_rps"], "status": status, "note": note})

    # Error rate
    if "error_rate_pct" in budgets and "error_rate_pct" in results:
        status, note = _check_error_rate(float(results["error_rate_pct"]), float(budgets["error_rate_pct"]))
        checks.append({"metric": "Error rate", "actual": results["error_rate_pct"], "budget": budgets["error_rate_pct"], "status": status, "note": note})

    # Bundle size
    if "bundle_size_kb" in budgets and "bundle_size_kb" in results:
        status, note = _check_bundle_size(float(results["bundle_size_kb"]), float(budgets["bundle_size_kb"]))
        checks.append({"metric": "Bundle size", "actual": results["bundle_size_kb"], "budget": budgets["bundle_size_kb"], "status": status, "note": note})

    return checks


def _gate_verdict(checks: list[dict]) -> tuple[str, str]:
    """Return (verdict, reason) for CI gate decision."""
    if not checks:
        raise ValueError("cannot produce a gate verdict without metric checks")
    fail_metrics = [c["metric"] for c in checks if c["status"] == FAIL]
    warn_metrics = [c["metric"] for c in checks if c["status"] == WARN]

    if fail_metrics:
        return FAIL, f"CI gate BLOCKED — {len(fail_metrics)} metric(s) failed: {', '.join(fail_metrics)}"
    if warn_metrics:
        return WARN, f"CI gate PASSED WITH WARNINGS — {len(warn_metrics)} metric(s) in warning zone: {', '.join(warn_metrics)}"
    return PASS, "CI gate PASSED — all metrics within budget"


# ---------------------------------------------------------------------------
# CI tier assignment logic
# ---------------------------------------------------------------------------


def _assign_ci_tier(scenario: dict) -> tuple[str, str]:
    """Return (tier, rationale) for a test scenario."""
    scenario = _object(scenario, "scenario")
    stype = scenario.get("type")
    if not isinstance(stype, str) or stype not in {"load", "stress", "soak", "spike", "capacity"}:
        raise ValueError("scenario type must be load, stress, soak, spike or capacity")
    name = scenario.get("name")
    if not isinstance(name, str) or not name.strip():
        raise ValueError("scenario name must be a non-empty string")
    duration = _number(scenario.get("duration_minutes"), "duration_minutes", positive=True)
    vus_raw = scenario.get("virtual_users")
    vus = _number(vus_raw, "virtual_users", positive=True)
    if not isinstance(vus_raw, int):
        raise ValueError("virtual_users must be an integer")

    # Smoke/very short load tests → PR gate
    if stype == "load" and duration <= 2 and vus <= 10:
        return "PR_gate", "Short smoke load test (<=2 min, <=10 VUs) — candidate for PR gate; confirm environment cost"

    # Spike tests with moderate VUs → nightly (not every PR)
    if stype == "spike" and vus <= 300:
        return "nightly", "Spike test — infra disruption risk, run nightly not per-PR"

    # Soak tests always go to nightly or pre_release based on duration
    if stype == "soak":
        if duration >= 60:
            return "nightly", f"Long soak test ({duration} min) — too costly for PR gate"
        return "nightly", "Soak test — detects slow leaks, suitable for nightly cadence"

    # Stress tests → pre_release (find ceiling, not needed per nightly)
    if stype in {"stress", "capacity"}:
        return "pre_release", "Stress / capacity test — find breaking point, run pre-release only"

    # Large spike tests → pre_release
    if stype == "spike" and vus > 300:
        return "pre_release", f"High-VU spike test ({vus} VUs) — infra impact, reserve for pre-release"

    # Load tests with significant VUs / long duration → nightly
    if stype == "load" and (duration > 10 or vus > 50):
        return "nightly", f"Full load test ({duration} min, {vus} VUs) — too heavy for per-PR gate"

    # Default moderate load → nightly
    return "nightly", f"Load test ({duration} min, {vus} VUs) — scheduled nightly run"


def _build_tier_matrix(data: dict) -> list[dict]:
    """Return list of {name, type, duration, vus, tier, rationale}."""
    scenarios = data.get("test_scenarios", [])
    if not isinstance(scenarios, list):
        raise ValueError("test_scenarios must be an array")
    matrix = []
    for s in scenarios:
        tier, rationale = _assign_ci_tier(s)
        matrix.append({
            "name": s.get("name", "?"),
            "type": s.get("type", "?"),
            "duration_minutes": s.get("duration_minutes", 0),
            "virtual_users": s.get("virtual_users", 0),
            "tier": tier,
            "rationale": rationale,
        })
    return matrix


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------


def cmd_check(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    checks = _evaluate_budgets(data)
    verdict, verdict_msg = _gate_verdict(checks)

    service = data.get("service_name", "Unknown")
    test_date = data.get("test_date", "?")
    env = data.get("environment", "?")

    print(f"Performance Budget Check — {service}")
    print(f"Test date: {test_date}  |  Environment: {env}")
    print()

    # Column widths
    col_metric = 12
    col_actual = 12
    col_budget = 12
    col_status = 7

    header = (
        f"  {'METRIC':<{col_metric}} {'ACTUAL':>{col_actual}} {'BUDGET':>{col_budget}} "
        f"{'STATUS':^{col_status}}  NOTE"
    )
    print(header)
    print("  " + "-" * 90)

    for c in checks:
        status_display = f"[{c['status']}]"
        actual_str = str(c["actual"])
        budget_str = str(c["budget"])
        print(
            f"  {c['metric']:<{col_metric}} {actual_str:>{col_actual}} {budget_str:>{col_budget}} "
            f"{status_display:^{col_status}}  {c['note']}"
        )

    print()
    print(f"  {verdict_msg}")
    print()

    # Summary counts
    pass_count = sum(1 for c in checks if c["status"] == PASS)
    warn_count = sum(1 for c in checks if c["status"] == WARN)
    fail_count = sum(1 for c in checks if c["status"] == FAIL)
    print(f"  Summary: {pass_count} PASS  {warn_count} WARN  {fail_count} FAIL  (of {len(checks)} metrics)")

    # Exit code: 0 = pass/warn, 1 = fail (CI-friendly)
    return 1 if verdict == FAIL else 0


def cmd_plan(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    matrix = _build_tier_matrix(data)
    if not matrix:
        raise ValueError("plan requires at least one test scenario")

    service = data.get("service_name", "Unknown")
    test_date = data.get("test_date", "?")

    print(f"CI Test Execution Matrix — {service}")
    print(f"Test date: {test_date}")
    print()

    # Group by tier
    tiers_order = ["PR_gate", "nightly", "pre_release"]
    grouped: dict[str, list[dict]] = {t: [] for t in tiers_order}
    for row in matrix:
        grouped[row["tier"]].append(row)

    for tier in tiers_order:
        rows = grouped[tier]
        if not rows:
            continue
        print(f"  [{tier}]  ({len(rows)} scenario{'s' if len(rows) != 1 else ''})")
        print(f"  {'SCENARIO':<40} {'TYPE':<12} {'DURATION':>9} {'VUS':>6}  RATIONALE")
        print("  " + "-" * 95)
        for r in rows:
            print(
                f"  {r['name']:<40} {r['type']:<12} {r['duration_minutes']:>8}m "
                f"{r['virtual_users']:>6}  {r['rationale']}"
            )
        print()

    # Tier summary
    print("  Tier definitions:")
    print("    PR_gate     — runs on every pull request; must complete in <5 min")
    print("    nightly     — scheduled overnight; full suite, baseline comparison")
    print("    pre_release — manual trigger before release; capacity, stress, spike")

    return 0


def cmd_report(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    checks = _evaluate_budgets(data)
    verdict, verdict_msg = _gate_verdict(checks)
    matrix = _build_tier_matrix(data)

    service = data.get("service_name", "Unknown")
    test_date = data.get("test_date", "?")
    env = data.get("environment", "?")
    today = _today()

    lines: list[str] = []
    a = lines.append

    a(f"# Performance Test Report — {service}")
    a("")
    a(f"**Report date:** {today}  ")
    a(f"**Test date:** {test_date}  ")
    a(f"**Environment:** {env}")
    a("")
    a("---")
    a("")

    # --- CI Gate verdict ---
    a("## CI Gate Verdict")
    a("")
    gate_badge = {"PASS": "PASS", "WARN": "PASS (with warnings)", "FAIL": "FAIL"}[verdict]
    a(f"**Overall result: {gate_badge}**")
    a("")
    a(f"> {verdict_msg}")
    a("")

    pass_count = sum(1 for c in checks if c["status"] == PASS)
    warn_count = sum(1 for c in checks if c["status"] == WARN)
    fail_count = sum(1 for c in checks if c["status"] == FAIL)
    a(f"| Result | Count |")
    a(f"|--------|-------|")
    a(f"| PASS | {pass_count} |")
    a(f"| WARN | {warn_count} |")
    a(f"| FAIL | {fail_count} |")
    a(f"| **Total metrics** | **{len(checks)}** |")
    a("")
    a("---")
    a("")

    # --- Budget breakdown ---
    a("## Performance Budget Results")
    a("")
    a("| Metric | Actual | Budget | Status | Note |")
    a("|--------|--------|--------|--------|------|")
    for c in checks:
        a(f"| {c['metric']} | {c['actual']} | {c['budget']} | **{c['status']}** | {c['note']} |")
    a("")
    a("### Threshold Reference (WARN zones are advisory heuristics)")
    a("")
    a("| Metric | PASS | WARN | FAIL |")
    a("|--------|------|------|------|")
    a("| LCP | <= user budget | none | > user budget |")
    a("| INP | <= user budget | none | > user budget |")
    a("| CLS | <= user budget | none | > user budget |")
    a("| API p95 | <= budget | up to +25% | > +25% budget |")
    a("| API p99 / p99.9 | <= budget | up to +15% | > +15% budget |")
    a("| Throughput | >= minimum | within 10% below | > 10% below minimum |")
    a("| Error rate | <= budget | up to 1.5x budget | > 1.5x budget |")
    a("| Bundle size | <= budget | up to +15% | > +15% budget |")
    a("")
    a("---")
    a("")

    # --- Test execution matrix ---
    a("## Test Execution Matrix")
    a("")
    tiers_order = ["PR_gate", "nightly", "pre_release"]
    grouped: dict[str, list[dict]] = {t: [] for t in tiers_order}
    for row in matrix:
        grouped[row["tier"]].append(row)

    for tier in tiers_order:
        rows = grouped[tier]
        if not rows:
            continue
        a(f"### {tier} ({len(rows)} scenario{'s' if len(rows) != 1 else ''})")
        a("")
        a("| Scenario | Type | Duration | VUs | Rationale |")
        a("|----------|------|----------|-----|-----------|")
        for r in rows:
            a(f"| {r['name']} | {r['type']} | {r['duration_minutes']}m | {r['virtual_users']} | {r['rationale']} |")
        a("")

    a("**Tier definitions:**")
    a("")
    a("- **PR_gate** — runs on every pull request; must complete in under 5 minutes")
    a("- **nightly** — scheduled overnight; full suite with baseline comparison")
    a("- **pre_release** — manual trigger before release; capacity, stress, spike testing")
    a("")
    a("---")
    a("")

    # --- Recommendations ---
    a("## Recommendations")
    a("")
    fail_items = [c for c in checks if c["status"] == FAIL]
    warn_items = [c for c in checks if c["status"] == WARN]

    if fail_items:
        a("### Failing Metrics (action required before merge)")
        a("")
        for c in fail_items:
            a(f"- **{c['metric']}**: {c['note']}")
        a("")

    if warn_items:
        a("### Warning Metrics (monitor and address)")
        a("")
        for c in warn_items:
            a(f"- **{c['metric']}**: {c['note']}")
        a("")

    # Metric-specific advice
    advice_map = {
        "LCP": "Investigate largest content element — server response time, render-blocking resources, or image optimization.",
        "INP": "Audit main-thread JavaScript tasks. Break up long tasks, defer non-critical work.",
        "CLS": "Fix unexpected layout shifts: set explicit dimensions on images/iframes, avoid inserting DOM above existing content.",
        "API p95": "Profile slow endpoints with distributed tracing. Check DB query p95, connection pool wait, and GC pause times.",
        "Throughput": "Scale horizontally or investigate thread pool / event loop saturation under load.",
        "Error rate": "Review error logs from the load test run. Classify errors (timeouts, 5xx, validation) and address root causes.",
        "Bundle size": "Run bundle analysis (webpack-bundle-analyzer or similar). Identify large dependencies for code splitting or tree-shaking.",
    }
    flagged = {c["metric"] for c in fail_items + warn_items}
    if flagged:
        a("### Remediation Guidance")
        a("")
        for metric, advice in advice_map.items():
            if metric in flagged:
                a(f"**{metric}:** {advice}")
        a("")

    if not fail_items and not warn_items:
        a("All metrics are within budget. No immediate action required.")
        a("")

    a("---")
    a("")
    a(f"*Generated by perf_budget_checker.py on {today}*")

    report_text = "\n".join(lines)

    if args.output:
        out = Path(args.output)
        out.write_text(report_text, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report_text)

    return 1 if verdict == FAIL else 0


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="perf_budget_checker.py",
        description="Performance budget checker and CI gate validator (stdlib-only).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # check
    p_check = sub.add_parser(
        "check",
        help=(
            "Validate measured results against performance budgets.\n"
            "Outputs PASS/WARN/FAIL per metric and overall CI gate verdict.\n"
            "Exit code: 0 = pass/warn, 1 = fail."
        ),
    )
    p_check.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to performance results JSON (e.g. data/sample-perf-results.json)",
    )

    # plan
    p_plan = sub.add_parser(
        "plan",
        help=(
            "Recommend CI tier assignment for each test scenario.\n"
            "Tiers: PR_gate / nightly / pre_release based on type, duration, VUs."
        ),
    )
    p_plan.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to performance results JSON (e.g. data/sample-perf-results.json)",
    )

    # report
    p_report = sub.add_parser(
        "report",
        help="Full Markdown performance test report (budget check + execution matrix).",
    )
    p_report.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to performance results JSON (e.g. data/sample-perf-results.json)",
    )
    p_report.add_argument(
        "--output", default=None, metavar="FILE",
        help="Write report to this file instead of stdout (e.g. report.md)",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "check":  cmd_check,
        "plan":   cmd_plan,
        "report": cmd_report,
    }
    try:
        return dispatch[args.command](args)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
