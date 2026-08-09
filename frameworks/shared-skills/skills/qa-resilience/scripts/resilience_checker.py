#!/usr/bin/env python3
"""Resilience pattern coverage checker and scorer.

Subcommands:
  assess  -- Score resilience pattern coverage across 9 failure-mode categories.
             Weighted score 0-100. Tiers: HARDENED (>=80), ADEQUATE (60-79),
             AT_RISK (40-59), VULNERABLE (<40).
  gaps    -- For each missing or misconfigured pattern, report the gap, the
             failure mode it leaves unprotected, and the recommended fix.
  report  -- Full Markdown resilience assessment report.

Pattern weights (derived from SKILL.md priority):
  timeouts:            20%
  retries:             15%
  circuit_breaker:     15%
  bulkheads:           15%
  graceful_degradation:15%
  health_checks:       10%
  retry_budget:         5%
  hedging:              3%
  chaos_testing:        2%
"""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

WEIGHTS: dict[str, float] = {
    "timeouts":             20.0,
    "retries":              15.0,
    "circuit_breaker":      15.0,
    "bulkheads":            15.0,
    "graceful_degradation": 15.0,
    "health_checks":        10.0,
    "retry_budget":          5.0,
    "hedging":               3.0,
    "chaos_testing":         2.0,
}

RESILIENCE_TIERS: list[tuple[int, str]] = [
    (80, "HARDENED"),
    (60, "ADEQUATE"),
    (40, "AT_RISK"),
    (0,  "VULNERABLE"),
]

# Gap catalogue: pattern -> (failure_mode_unprotected, recommended_fix)
GAP_GUIDANCE: dict[str, tuple[str, str]] = {
    "timeouts": (
        "Unbounded remote calls and DB queries exhaust connection pools and thread "
        "resources. Cascading slowdowns cannot be bounded at any layer.",
        "Budget a timeout per hop: set connection, request, and DB statement timeouts "
        "independently. Propagate the remaining deadline across gRPC/HTTP calls. "
        "Bound pool-wait time so callers fail fast rather than queue indefinitely. "
        "See references/timeout-policies.md.",
    ),
    "retries": (
        "Transient failures and rate-limit responses are not recovered automatically. "
        "Non-idempotent retries risk duplicate side effects when misconfigured.",
        "Add bounded retries (2-3 max for user-facing paths) with full jitter and a "
        "per-try timeout. Verify idempotency before retrying any mutating call. Honor "
        "Retry-After headers. Assign retry ownership to one layer only. "
        "See references/retry-patterns.md.",
    ),
    "retry_budget": (
        "During partial outages, unbounded retries create retry storms that amplify "
        "traffic 5-10x, prolonging and worsening the incident for all callers.",
        "Introduce a retry budget (token bucket or success-ratio cap) per dependency. "
        "Tighten or disable retries when budget exhaustion is detected. Alert when "
        "budget exhaustion spikes. See references/retry-patterns.md.",
    ),
    "hedging": (
        "Tail-latency outliers on safe reads degrade p99 for all users. Without "
        "hedging, the slowest backend replica determines user-visible latency.",
        "Evaluate hedging for idempotent, cancellation-safe reads with high p99. "
        "Issue a second request after a short delay; cancel the loser. Measure the "
        "extra load before enabling in production. "
        "See references/deadlines-hedging.md.",
    ),
    "circuit_breaker": (
        "Sustained downstream failures propagate to all callers. Without a breaker, "
        "the service continues hammering a failing dependency until resources are "
        "exhausted, creating cascading failures.",
        "Add a circuit breaker per high- and medium-criticality dependency. Tune the "
        "failure window to observed traffic (avoid false trips on transient spikes). "
        "Use half-open probes for recovery. Emit state-change events to your telemetry "
        "pipeline. See references/circuit-breaker-patterns.md.",
    ),
    "bulkheads": (
        "A shared connection pool means saturation against one dependency starves all "
        "others. A fraud-detection spike can block payment-gateway calls with zero "
        "isolation.",
        "Isolate outbound connections into per-dependency pools with explicit size "
        "limits. Reject new requests early when a pool is at capacity rather than "
        "queuing indefinitely. Consider adaptive concurrency for variable traffic. "
        "See references/bulkhead-isolation.md.",
    ),
    "graceful_degradation": (
        "Non-critical feature failures surface as full checkout failures. Users lose "
        "the ability to complete purchases because of low-priority dependency outages.",
        "Wrap non-critical calls (notifications, catalog enrichment) in fire-and-forget "
        "with tight timeouts. Define the degraded UX and freshness contract explicitly. "
        "Instrument degraded-mode duration and fallback rate as metrics. "
        "See references/graceful-degradation.md.",
    ),
    "health_checks": (
        "Deep health probes that call downstream dependencies fail when those "
        "dependencies are slow, causing unnecessary pod restarts and traffic loss. "
        "Missing startup probes cause readiness failures on every deploy.",
        "Make liveness shallow (process alive, not DB-connected). Bound readiness "
        "checks tightly; do not call slow dependencies. Add a startup probe for slow "
        "init paths. Implement graceful shutdown to drain in-flight requests. "
        "See references/health-check-patterns.md.",
    ),
    "chaos_testing": (
        "Failure behavior is untested under realistic conditions. DR runbooks and "
        "failover procedures may be incorrect or out of date, discovered only during "
        "a real incident.",
        "Define steady state and hypothesis before any experiment. Start with "
        "deterministic fault injection in non-prod (mock, fault proxy, or mesh faults). "
        "Run scoped production experiments with blast-radius limits, abort criteria, "
        "and on-call awareness. Schedule game days with DR failover drills. "
        "See references/chaos-engineering-guide.md.",
    ),
}

# Hedging is optional (N/A is acceptable) — only penalised when explicitly absent
# and no note indicates it was evaluated and deemed unnecessary.
HEDGING_NA_KEYWORDS = ("n/a", "not applicable", "not needed", "evaluated", "safe reads not present")


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


def _resilience_tier(score: float) -> str:
    for threshold, label in RESILIENCE_TIERS:
        if score >= threshold:
            return label
    return "VULNERABLE"


def _pattern_score(pattern_name: str, pattern_data: dict) -> float:
    """Return 0.0, 0.5, or 1.0 for a pattern.

    - has_it=False                    -> 0.0
    - has_it=True, configured=False   -> 0.5
    - has_it=True, configured=True    -> 1.0
    - hedging with N/A notes          -> 1.0 (not applicable = full credit)
    """
    has_it: bool = pattern_data.get("has_it", False)
    configured: bool = pattern_data.get("configured_correctly", False)
    notes: str = (pattern_data.get("notes") or "").lower()

    # Hedging N/A: if the service has no safe idempotent reads, hedging is not
    # applicable and should not be penalised.
    if pattern_name == "hedging" and not has_it:
        if any(kw in notes for kw in HEDGING_NA_KEYWORDS):
            return 1.0

    if not has_it:
        return 0.0
    if not configured:
        return 0.5
    return 1.0


def _compute_score(patterns: dict) -> tuple[float, dict[str, float]]:
    """Return (weighted_score_0_to_100, per_pattern_scores_dict)."""
    per_pattern: dict[str, float] = {}
    weighted_total = 0.0

    for name, weight in WEIGHTS.items():
        pattern_data = patterns.get(name, {})
        raw = _pattern_score(name, pattern_data)
        per_pattern[name] = raw
        weighted_total += raw * weight

    return round(weighted_total, 1), per_pattern


def _score_label(raw: float) -> str:
    if raw == 1.0:
        return "OK"
    if raw == 0.5:
        return "PARTIAL"
    return "MISSING"


def _is_gap(pattern_name: str, pattern_data: dict, raw: float) -> bool:
    """Return True if this pattern needs attention (missing or partial)."""
    if pattern_name == "hedging":
        notes = (pattern_data.get("notes") or "").lower()
        if not pattern_data.get("has_it", False) and any(kw in notes for kw in HEDGING_NA_KEYWORDS):
            return False
    return raw < 1.0


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_assess(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    service_name = data.get("service_name", "Unknown")
    patterns = data.get("patterns", {})

    score, per_pattern = _compute_score(patterns)
    tier = _resilience_tier(score)

    print(f"Resilience Assessment — {service_name}  (assessed: {data.get('assessed_date', '?')})")
    print()
    print(f"{'PATTERN':<24} {'WEIGHT':>7}  {'STATUS':<8}  {'CONTRIB':>8}  NOTES")
    print("-" * 90)

    for name, weight in WEIGHTS.items():
        raw = per_pattern.get(name, 0.0)
        status = _score_label(raw)
        contrib = round(raw * weight, 1)
        pattern_data = patterns.get(name, {})
        notes_preview = (pattern_data.get("notes") or "")[:60].replace("\n", " ")
        if len(pattern_data.get("notes") or "") > 60:
            notes_preview += "..."
        print(f"  {name:<22} {weight:>6.0f}%  {status:<8}  {contrib:>7.1f}  {notes_preview}")

    print("-" * 90)
    print(f"  {'TOTAL':<22} {'100':>6}%  {'':8}  {score:>7.1f}")
    print()
    print(f"Resilience score : {score:.1f} / 100  [{tier}]")
    print()
    print("Tiers: HARDENED >=80 | ADEQUATE 60-79 | AT_RISK 40-59 | VULNERABLE <40")

    gap_count = sum(
        1 for name, raw in per_pattern.items()
        if _is_gap(name, patterns.get(name, {}), raw)
    )
    if gap_count:
        print()
        print(f"Gaps found: {gap_count}. Run 'gaps' subcommand for remediation details.")

    return 0


def cmd_gaps(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    service_name = data.get("service_name", "Unknown")
    patterns = data.get("patterns", {})

    _, per_pattern = _compute_score(patterns)

    gaps = [
        (name, per_pattern[name])
        for name in WEIGHTS
        if _is_gap(name, patterns.get(name, {}), per_pattern[name])
    ]

    if not gaps:
        print(f"No gaps found for {service_name}. All resilience patterns are in place.")
        return 0

    print(f"Resilience Gaps — {service_name}")
    print(f"Found {len(gaps)} pattern(s) that are missing or misconfigured.")
    print()

    for i, (name, raw) in enumerate(gaps, 1):
        status = _score_label(raw)
        weight = WEIGHTS[name]
        pattern_data = patterns.get(name, {})
        failure_mode, fix = GAP_GUIDANCE.get(name, ("(no guidance)", "(no guidance)"))
        notes = (pattern_data.get("notes") or "").strip()

        print(f"{'=' * 72}")
        print(f"[{i}] {name.upper()}  ({status}, weight={weight:.0f}%)")
        print()
        print("  Current state:")
        for line in _wrap(notes, width=68, indent="    "):
            print(line)
        print()
        print("  Failure mode left unprotected:")
        for line in _wrap(failure_mode, width=68, indent="    "):
            print(line)
        print()
        print("  Recommended fix:")
        for line in _wrap(fix, width=68, indent="    "):
            print(line)
        print()

    print(f"{'=' * 72}")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    data = _load_json(args.input)
    service_name = data.get("service_name", "Unknown")
    patterns = data.get("patterns", {})
    observability = data.get("observability", {})
    dependencies = data.get("dependencies", [])
    today = date.today()

    score, per_pattern = _compute_score(patterns)
    tier = _resilience_tier(score)

    gaps = [
        (name, per_pattern[name])
        for name in WEIGHTS
        if _is_gap(name, patterns.get(name, {}), per_pattern[name])
    ]
    ok_count = len(WEIGHTS) - len(gaps)

    lines: list[str] = []
    a = lines.append

    # Header
    a(f"# Resilience Assessment Report — {service_name}")
    a("")
    a(f"**Report date:** {today}  ")
    a(f"**Assessed date:** {data.get('assessed_date', '?')}  ")
    a(f"**Team:** {data.get('team', '?')}  ")
    a(f"**Language / platform:** {data.get('language', '?')} / {data.get('deployment', '?')}")
    a("")
    a("---")
    a("")

    # Summary
    a("## Resilience Score")
    a("")
    a(f"| Metric | Value |")
    a(f"|--------|-------|")
    a(f"| Score | **{score:.1f} / 100** |")
    a(f"| Tier | **{tier}** |")
    a(f"| Patterns OK | {ok_count} / {len(WEIGHTS)} |")
    a(f"| Gaps (missing or misconfigured) | {len(gaps)} |")
    a("")
    a("> Tiers: **HARDENED** ≥80 | **ADEQUATE** 60–79 | **AT_RISK** 40–59 | **VULNERABLE** <40")
    a("")
    a("---")
    a("")

    # Pattern detail table
    a("## Pattern Coverage")
    a("")
    a("| Pattern | Weight | Status | Weighted Score | Notes |")
    a("|---------|--------|--------|---------------|-------|")
    for name, weight in WEIGHTS.items():
        raw = per_pattern.get(name, 0.0)
        status = _score_label(raw)
        contrib = round(raw * weight, 1)
        pattern_data = patterns.get(name, {})
        note_cell = (pattern_data.get("notes") or "").replace("|", "\\|")[:120]
        if len(pattern_data.get("notes") or "") > 120:
            note_cell += "…"
        a(f"| {name} | {weight:.0f}% | {status} | {contrib:.1f} | {note_cell} |")
    a(f"| **Total** | **100%** | | **{score:.1f}** | |")
    a("")
    a("---")
    a("")

    # Dependency inventory
    if dependencies:
        a("## Dependency Inventory")
        a("")
        a("| Dependency | Type | Criticality | Notes |")
        a("|------------|------|-------------|-------|")
        for dep in dependencies:
            note_cell = (dep.get("notes") or "").replace("|", "\\|")
            a(f"| {dep['name']} | {dep.get('type', '?')} | {dep.get('criticality', '?')} | {note_cell} |")
        a("")
        a("---")
        a("")

    # Gaps and remediation
    if gaps:
        a("## Gaps and Remediation")
        a("")
        a(f"{len(gaps)} pattern(s) are missing or misconfigured. Address in priority order (highest weight first).")
        a("")
        for name, raw in gaps:
            status = _score_label(raw)
            weight = WEIGHTS[name]
            pattern_data = patterns.get(name, {})
            failure_mode, fix = GAP_GUIDANCE.get(name, ("", ""))
            notes = (pattern_data.get("notes") or "").strip()

            a(f"### {name.replace('_', ' ').title()}  ({status}, {weight:.0f}% weight)")
            a("")
            a(f"**Current state:** {notes}")
            a("")
            a(f"**Failure mode left unprotected:** {failure_mode}")
            a("")
            a(f"**Recommended fix:** {fix}")
            a("")
        a("---")
        a("")
    else:
        a("## Gaps and Remediation")
        a("")
        a("No gaps found. All resilience patterns are present and correctly configured.")
        a("")
        a("---")
        a("")

    # Observability
    a("## Observability")
    a("")
    a("| Signal | Present |")
    a("|--------|---------|")
    a(f"| Distributed tracing | {'Yes' if observability.get('has_tracing') else 'No'} |")
    a(f"| Alerts configured | {'Yes' if observability.get('has_alerts') else 'No'} |")
    a(f"| SLO defined | {'Yes' if observability.get('slo_defined') else 'No'} |")
    if observability.get("slo_target"):
        a(f"| SLO target | {observability['slo_target']} |")
    if observability.get("notes"):
        a("")
        a(f"**Notes:** {observability['notes']}")
    a("")
    a("---")
    a("")

    # Recommendations summary
    a("## Recommended Next Steps")
    a("")
    if gaps:
        a("Address gaps in descending weight order:")
        a("")
        for i, (name, raw) in enumerate(gaps, 1):
            _, fix_summary = GAP_GUIDANCE.get(name, ("", ""))
            # First sentence only for the summary list
            first_sentence = fix_summary.split(".")[0] + "."
            a(f"{i}. **{name.replace('_', ' ').title()}** ({_score_label(raw)}) — {first_sentence}")
        a("")
    else:
        a("- Schedule a chaos/fault-injection experiment to validate current controls under realistic failure conditions.")
        a("- Review SLO burn rate and degraded-mode telemetry monthly.")
        a("")

    a("---")
    a("")
    a(f"*Generated by resilience_checker.py on {today}*  ")
    a(f"*Based on: [qa-resilience skill](../SKILL.md)*")

    report_text = "\n".join(lines)

    if args.output:
        out = Path(args.output)
        out.write_text(report_text, encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report_text)

    return 0


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def _wrap(text: str, width: int = 72, indent: str = "") -> list[str]:
    """Simple word wrapper that respects existing newlines."""
    result: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = indent
        for word in words:
            if len(line) + len(word) + 1 > width and line.strip():
                result.append(line.rstrip())
                line = indent + word + " "
            else:
                line += word + " "
        if line.strip():
            result.append(line.rstrip())
    return result or [indent]


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="resilience_checker.py",
        description="Resilience pattern coverage checker and scorer (stdlib-only).",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # assess
    p_assess = sub.add_parser(
        "assess",
        help="Score resilience pattern coverage; show weighted score and tier.",
    )
    p_assess.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to sample-service-profile.json",
    )

    # gaps
    p_gaps = sub.add_parser(
        "gaps",
        help="List gaps with failure mode and recommended fix for each missing pattern.",
    )
    p_gaps.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to sample-service-profile.json",
    )

    # report
    p_report = sub.add_parser(
        "report",
        help="Full Markdown resilience assessment report.",
    )
    p_report.add_argument(
        "--input", required=True, metavar="FILE",
        help="Path to sample-service-profile.json",
    )
    p_report.add_argument(
        "--output", default=None, metavar="FILE",
        help="Write report to this file instead of stdout",
    )

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "assess": cmd_assess,
        "gaps":   cmd_gaps,
        "report": cmd_report,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
