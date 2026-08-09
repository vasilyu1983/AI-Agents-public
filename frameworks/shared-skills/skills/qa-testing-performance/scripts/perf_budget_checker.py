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


def _load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        sys.exit(f"Error: file not found: {path}")
    try:
        with p.open(encoding="utf-8") as fh:
            return json.load(fh)
    except json.JSONDecodeError as exc:
        sys.exit(f"Error: invalid JSON in {path}: {exc}")


def _today() -> str:
    return str(date.today())


# ---------------------------------------------------------------------------
# Budget evaluation logic
# ---------------------------------------------------------------------------


def _check_lcp(actual: float, budget: float) -> tuple[str, str]:
    """Return (status, note) for LCP metric."""
    if actual <= budget and actual < LCP_WARN:
        return PASS, f"{actual}ms — within budget ({budget}ms)"
    if actual <= LCP_WARN:
        return PASS, f"{actual}ms — within budget ({budget}ms)"
    if actual < LCP_FAIL:
        return WARN, f"{actual}ms — exceeds budget ({budget}ms), in 'needs improvement' zone"
    return FAIL, f"{actual}ms — exceeds FAIL threshold ({LCP_FAIL}ms)"


def _check_inp(actual: float, budget: float) -> tuple[str, str]:
    if actual <= budget and actual < INP_WARN:
        return PASS, f"{actual}ms — within budget ({budget}ms)"
    if actual <= INP_WARN:
        return PASS, f"{actual}ms — within budget ({budget}ms)"
    if actual < INP_FAIL:
        return WARN, f"{actual}ms — exceeds budget ({budget}ms), in warning zone"
    return FAIL, f"{actual}ms — exceeds FAIL threshold ({INP_FAIL}ms)"


def _check_cls(actual: float, budget: float) -> tuple[str, str]:
    if actual <= budget and actual < CLS_WARN:
        return PASS, f"{actual:.3f} — within budget ({budget})"
    if actual <= CLS_WARN:
        return PASS, f"{actual:.3f} — within budget ({budget})"
    if actual < CLS_FAIL:
        return WARN, f"{actual:.3f} — exceeds budget ({budget}), in warning zone"
    return FAIL, f"{actual:.3f} — exceeds FAIL threshold ({CLS_FAIL})"


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
    budgets = data.get("budgets", {})
    results = data.get("results", {})

    checks = []

    def _safe(key: float | None, default: float = 0.0) -> float:
        return float(results.get(key, default))

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
    stype = scenario.get("type", "load").lower()
    duration = int(scenario.get("duration_minutes", 0))
    vus = int(scenario.get("virtual_users", 0))

    # Smoke/very short load tests → PR gate
    if stype == "load" and duration <= 2 and vus <= 10:
        return "PR_gate", "Short smoke load test (<=2 min, <=10 VUs) — safe for every PR"

    # Spike tests with moderate VUs → nightly (not every PR)
    if stype == "spike" and vus <= 300:
        return "nightly", "Spike test — infra disruption risk, run nightly not per-PR"

    # Soak tests always go to nightly or pre_release based on duration
    if stype == "soak":
        if duration >= 60:
            return "nightly", f"Long soak test ({duration} min) — too costly for PR gate"
        return "nightly", "Soak test — detects slow leaks, suitable for nightly cadence"

    # Stress tests → pre_release (find ceiling, not needed per nightly)
    if stype == "stress":
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
    a("### Threshold Reference")
    a("")
    a("| Metric | PASS | WARN | FAIL |")
    a("|--------|------|------|------|")
    a("| LCP | < 2500ms (budget) | 2500–4000ms | > 4000ms |")
    a("| INP | < 200ms (budget) | 200–500ms | > 500ms |")
    a("| CLS | < 0.1 (budget) | 0.1–0.25 | > 0.25 |")
    a("| API p95 | <= budget | up to +25% | > +25% budget |")
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

    return 0


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
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
