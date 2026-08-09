#!/usr/bin/env python3
"""
Observability maturity scoring and SLO error budget tool for qa-observability.

Deterministic scoring across 6 signal dimensions. No API or LLM calls —
all logic is derived from the input JSON profile.

Subcommands:
  maturity — score observability maturity across 6 signal dimensions
  slo      — calculate error budget status for each SLO
  report   — full observability readiness report (maturity + SLO)

Usage:
  python scripts/observability_scorer.py maturity --input data/sample-observability-profile.json
  python scripts/observability_scorer.py slo      --input data/sample-slo-data.json
  python scripts/observability_scorer.py report   \\
    --input data/sample-observability-profile.json \\
    --slos  data/sample-slo-data.json \\
    --output report.md
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Constants — signal dimensions
# ---------------------------------------------------------------------------

DIMENSIONS = [
    "structured_logs",
    "metrics",
    "distributed_tracing",
    "slo_sli",
    "alerting",
    "correlation_ids",
]

DIMENSION_MAX: Dict[str, int] = {
    "structured_logs":    20,
    "metrics":            20,
    "distributed_tracing": 20,
    "slo_sli":            15,
    "alerting":           15,
    "correlation_ids":    10,
}

DIMENSION_DESCRIPTIONS: Dict[str, str] = {
    "structured_logs":     "JSON logs, correlation IDs in logs, PII redaction",
    "metrics":             "Golden signals, histograms, exemplars",
    "distributed_tracing": "Auto-instrumentation, manual spans, propagation",
    "slo_sli":             "SLI/SLO definitions and error budget policy",
    "alerting":            "Burn-rate alerts, alert fatigue management",
    "correlation_ids":     "Request ID propagation within and across services",
}

TOTAL_MAX = sum(DIMENSION_MAX.values())  # 100

# Maturity level thresholds
MATURITY_ADVANCED    = 85
MATURITY_PROFICIENT  = 65
MATURITY_DEVELOPING  = 40

# Per-dimension rating thresholds (as % of max for that dimension)
DIM_COMPLETE_PCT = 0.90
DIM_PARTIAL_PCT  = 0.50


# ---------------------------------------------------------------------------
# SLO constants
# ---------------------------------------------------------------------------

SLO_STATUS_EXHAUSTED = "BUDGET_EXHAUSTED"  # burn rate > 100%
SLO_STATUS_CRITICAL  = "CRITICAL"          # >50% burn in <20% of window
SLO_STATUS_AT_RISK   = "AT_RISK"           # >20% burn
SLO_STATUS_HEALTHY   = "HEALTHY"


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ObservabilityProfile:
    service_name: str
    stack: str
    environment: str
    signals: Dict[str, dict]
    notes: str
    raw: dict = field(repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "ObservabilityProfile":
        return cls(
            service_name=d.get("service_name", "unknown-service"),
            stack=d.get("stack", "unknown"),
            environment=d.get("environment", "production"),
            signals=d.get("signals", {}),
            notes=d.get("notes", ""),
            raw=d,
        )


@dataclass
class DimensionResult:
    dimension: str
    raw_score: int
    max_score: int
    rating: str      # COMPLETE | PARTIAL | MISSING
    description: str
    pct: float       # 0.0–1.0


@dataclass
class MaturityResult:
    profile: ObservabilityProfile
    total_score: int
    total_max: int
    maturity_level: str
    dimension_results: List[DimensionResult]


@dataclass
class SLOEntry:
    name: str
    service: str
    metric_type: str
    target_pct: float
    window_days: int
    current_availability_pct: float
    good_events: int
    total_events: int
    raw: dict = field(repr=False)

    @classmethod
    def from_dict(cls, d: dict) -> "SLOEntry":
        return cls(
            name=d.get("name", "unnamed-slo"),
            service=d.get("service", "unknown"),
            metric_type=d.get("metric_type", "availability"),
            target_pct=float(d.get("target_pct", 99.9)),
            window_days=int(d.get("window_days", 30)),
            current_availability_pct=float(d.get("current_availability_pct", 100.0)),
            good_events=int(d.get("good_events", 0)),
            total_events=int(d.get("total_events", 0)),
            raw=d,
        )


@dataclass
class SLOResult:
    slo: SLOEntry
    error_budget_pct: float      # allowed failure rate = 1 - target_pct/100
    consumed_pct: float          # how much of the error budget is consumed (0–∞)
    burn_rate: float             # current_burn_rate: (1 - actual) / (1 - target)
    status: str
    remaining_budget_events: int


# ---------------------------------------------------------------------------
# Scoring logic — maturity
# ---------------------------------------------------------------------------

def dimension_rating(raw: int, max_score: int) -> str:
    pct = raw / max_score if max_score else 0.0
    if pct >= DIM_COMPLETE_PCT:
        return "COMPLETE"
    if pct >= DIM_PARTIAL_PCT:
        return "PARTIAL"
    return "MISSING"


def maturity_level(total: int) -> str:
    if total >= MATURITY_ADVANCED:
        return "ADVANCED"
    if total >= MATURITY_PROFICIENT:
        return "PROFICIENT"
    if total >= MATURITY_DEVELOPING:
        return "DEVELOPING"
    return "FOUNDATIONAL"


def compute_maturity(profile: ObservabilityProfile) -> MaturityResult:
    dimension_results: List[DimensionResult] = []
    total = 0

    for dim in DIMENSIONS:
        max_score = DIMENSION_MAX[dim]
        sig = profile.signals.get(dim, {})
        raw_score = sig.get("score", 0)
        raw_score = max(0, min(max_score, int(raw_score)))
        total += raw_score
        pct = raw_score / max_score if max_score else 0.0
        dimension_results.append(
            DimensionResult(
                dimension=dim,
                raw_score=raw_score,
                max_score=max_score,
                rating=dimension_rating(raw_score, max_score),
                description=DIMENSION_DESCRIPTIONS[dim],
                pct=pct,
            )
        )

    return MaturityResult(
        profile=profile,
        total_score=total,
        total_max=TOTAL_MAX,
        maturity_level=maturity_level(total),
        dimension_results=dimension_results,
    )


# ---------------------------------------------------------------------------
# Scoring logic — SLOs
# ---------------------------------------------------------------------------

def compute_slo_status(slo: SLOEntry) -> SLOResult:
    target_fraction = slo.target_pct / 100.0
    actual_fraction = slo.current_availability_pct / 100.0

    error_budget_pct = 1.0 - target_fraction          # e.g. 0.001 for 99.9%
    actual_error_rate = 1.0 - actual_fraction          # how bad things are now

    if error_budget_pct <= 0:
        burn_rate = float("inf") if actual_error_rate > 0 else 0.0
    else:
        burn_rate = actual_error_rate / error_budget_pct

    # consumed_pct: what fraction of the error budget is consumed
    consumed_pct = burn_rate * 100.0  # 100% consumed == budget exactly spent

    # Remaining budget in events
    if slo.total_events > 0:
        allowed_failures = slo.total_events * error_budget_pct
        actual_failures = slo.total_events - slo.good_events
        remaining_budget_events = max(0, int(allowed_failures - actual_failures))
    else:
        remaining_budget_events = 0

    # Status classification
    if burn_rate > 1.0:
        status = SLO_STATUS_EXHAUSTED
    elif burn_rate > 0.5 and slo.window_days > 0:
        # CRITICAL: >50% burn rate and we are in the first 20% of the window
        # Proxy: if burn_rate is high enough that budget would be gone in <20% of window
        time_to_exhaustion_fraction = 1.0 / burn_rate if burn_rate > 0 else float("inf")
        if time_to_exhaustion_fraction < 0.20:
            status = SLO_STATUS_CRITICAL
        else:
            status = SLO_STATUS_AT_RISK
    elif burn_rate > 0.20:
        status = SLO_STATUS_AT_RISK
    else:
        status = SLO_STATUS_HEALTHY

    return SLOResult(
        slo=slo,
        error_budget_pct=error_budget_pct * 100.0,
        consumed_pct=consumed_pct,
        burn_rate=burn_rate,
        status=status,
        remaining_budget_events=remaining_budget_events,
    )


# ---------------------------------------------------------------------------
# I/O helpers
# ---------------------------------------------------------------------------

def load_json_file(path: Path, label: str = "file") -> object:
    if not path.exists():
        print(f"ERROR: {label} not found: {path}", file=sys.stderr)
        sys.exit(1)
    with open(path) as f:
        return json.load(f)


def load_profile(path: Path) -> ObservabilityProfile:
    data = load_json_file(path, "observability profile")
    if not isinstance(data, dict):
        print(f"ERROR: {path} must be a JSON object.", file=sys.stderr)
        sys.exit(1)
    return ObservabilityProfile.from_dict(data)


def load_slos(path: Path) -> List[SLOEntry]:
    data = load_json_file(path, "SLO data")
    if not isinstance(data, list):
        print(f"ERROR: {path} must be a JSON array of SLO objects.", file=sys.stderr)
        sys.exit(1)
    return [SLOEntry.from_dict(item) for item in data]


def ts() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def truncate(text: str, width: int) -> str:
    return text if len(text) <= width else text[: width - 1] + "…"


RATING_ICONS = {
    "COMPLETE": "✓",
    "PARTIAL":  "~",
    "MISSING":  "✗",
}

STATUS_ICONS = {
    SLO_STATUS_HEALTHY:   "✓",
    SLO_STATUS_AT_RISK:   "~",
    SLO_STATUS_CRITICAL:  "!",
    SLO_STATUS_EXHAUSTED: "✗",
}


# ---------------------------------------------------------------------------
# Subcommand: maturity
# ---------------------------------------------------------------------------

def cmd_maturity(args: argparse.Namespace) -> int:
    profile = load_profile(Path(args.input))
    result = compute_maturity(profile)

    print(f"\nObservability Maturity Score — {ts()}")
    print(f"Service     : {profile.service_name}")
    print(f"Stack       : {profile.stack}")
    print(f"Environment : {profile.environment}")
    print()
    print(f"Total Score    : {result.total_score} / {result.total_max}")
    print(f"Maturity Level : {result.maturity_level}")
    print()

    c_dim  = 22
    c_sc   = 10
    c_rt   = 10
    c_desc = 48

    header = (
        f"  {'Dimension':<{c_dim}} {'Score':>{c_sc}}  {'Rating':<{c_rt}}  {'Description':<{c_desc}}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))

    for dr in result.dimension_results:
        icon = RATING_ICONS[dr.rating]
        bar_filled = round(dr.pct * 10)
        bar = "█" * bar_filled + "░" * (10 - bar_filled)
        score_str = f"{dr.raw_score}/{dr.max_score}"
        print(
            f"  {icon} {truncate(dr.dimension, c_dim - 2):<{c_dim - 2}} "
            f"{score_str:>{c_sc}}  "
            f"{dr.rating:<{c_rt}}  "
            f"{truncate(dr.description, c_desc)}"
        )
        print(f"    [{bar}]")

    print()
    print(
        "Maturity levels: "
        "ADVANCED (≥85)  PROFICIENT (65–84)  DEVELOPING (40–64)  FOUNDATIONAL (<40)"
    )
    print(
        "Dimension rating: "
        "COMPLETE (≥90% of max)  PARTIAL (50–89%)  MISSING (<50%)"
    )

    missing = [dr for dr in result.dimension_results if dr.rating == "MISSING"]
    partial = [dr for dr in result.dimension_results if dr.rating == "PARTIAL"]
    if missing:
        print()
        print(f"Missing dimensions ({len(missing)}): " + ", ".join(dr.dimension for dr in missing))
    if partial:
        print(f"Partial dimensions ({len(partial)}): " + ", ".join(dr.dimension for dr in partial))

    return 0


# ---------------------------------------------------------------------------
# Subcommand: slo
# ---------------------------------------------------------------------------

def cmd_slo(args: argparse.Namespace) -> int:
    slos = load_slos(Path(args.input))
    results = [compute_slo_status(s) for s in slos]

    print(f"\nSLO Error Budget Status — {ts()}")
    print(f"Source : {args.input}")
    print(f"SLOs   : {len(results)}")
    print()

    c_name    = 28
    c_svc     = 18
    c_target  = 8
    c_avail   = 10
    c_burn    = 10
    c_consumed = 12
    c_status  = 18

    header = (
        f"  {'SLO Name':<{c_name}} {'Service':<{c_svc}} "
        f"{'Target':>{c_target}} {'Actual':>{c_avail}} "
        f"{'BurnRate':>{c_burn}} {'Consumed%':>{c_consumed}} "
        f"{'Status':<{c_status}}"
    )
    print(header)
    print("  " + "-" * (len(header) - 2))

    for r in results:
        icon = STATUS_ICONS[r.status]
        burn_str = f"{r.burn_rate:.2f}x" if r.burn_rate != float("inf") else "∞"
        consumed_str = f"{r.consumed_pct:.1f}%"
        print(
            f"  {icon} {truncate(r.slo.name, c_name - 2):<{c_name - 2}} "
            f"{truncate(r.slo.service, c_svc):<{c_svc}} "
            f"{r.slo.target_pct:>{c_target}.2f}% "
            f"{r.slo.current_availability_pct:>{c_avail}.3f}% "
            f"{burn_str:>{c_burn}} "
            f"{consumed_str:>{c_consumed}} "
            f"{r.status:<{c_status}}"
        )

    print()
    print(
        "Status key:\n"
        "  HEALTHY         — burn rate ≤ 20% of budget\n"
        "  AT_RISK         — burn rate > 20% of budget\n"
        "  CRITICAL        — burn rate > 50%, budget exhausted in < 20% of window\n"
        "  BUDGET_EXHAUSTED — burn rate > 100% (error budget already spent)"
    )

    # Detail for non-healthy SLOs
    non_healthy = [r for r in results if r.status != SLO_STATUS_HEALTHY]
    if non_healthy:
        print()
        print("Detail for non-healthy SLOs:")
        for r in non_healthy:
            print()
            print(f"  [{r.status}] {r.slo.name} ({r.slo.service})")
            print(f"    Metric type        : {r.slo.metric_type}")
            print(f"    Target             : {r.slo.target_pct:.3f}%")
            print(f"    Current            : {r.slo.current_availability_pct:.3f}%")
            print(f"    Error budget       : {r.error_budget_pct:.4f}% of requests")
            print(f"    Burn rate          : {r.burn_rate:.2f}x")
            print(f"    Budget consumed    : {r.consumed_pct:.1f}%")
            if r.slo.total_events > 0:
                print(f"    Remaining budget   : {r.remaining_budget_events} events")
            print(f"    Window             : {r.slo.window_days} days")

    return 0


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> int:
    profile = load_profile(Path(args.input))
    maturity = compute_maturity(profile)

    slo_results: Optional[List[SLOResult]] = None
    if args.slos:
        slos = load_slos(Path(args.slos))
        slo_results = [compute_slo_status(s) for s in slos]

    lines = [
        f"# Observability Readiness Report — {profile.service_name}",
        "",
        f"**Generated**: {ts()}  ",
        f"**Stack**: {profile.stack}  ",
        f"**Environment**: {profile.environment}  ",
        f"**Source**: {args.input}  ",
        "",
        "---",
        "",
        "## 1. Executive Summary",
        "",
        "| Metric | Value |",
        "|---|---|",
        f"| Service | {profile.service_name} |",
        f"| Stack | {profile.stack} |",
        f"| Maturity Score | **{maturity.total_score} / {maturity.total_max}** |",
        f"| Maturity Level | **{maturity.maturity_level}** |",
    ]

    if slo_results:
        exhausted = sum(1 for r in slo_results if r.status == SLO_STATUS_EXHAUSTED)
        critical  = sum(1 for r in slo_results if r.status == SLO_STATUS_CRITICAL)
        at_risk   = sum(1 for r in slo_results if r.status == SLO_STATUS_AT_RISK)
        healthy   = sum(1 for r in slo_results if r.status == SLO_STATUS_HEALTHY)
        lines += [
            f"| SLOs Tracked | {len(slo_results)} |",
            f"| Budget Exhausted | {exhausted} |",
            f"| Critical | {critical} |",
            f"| At Risk | {at_risk} |",
            f"| Healthy | {healthy} |",
        ]

    lines += [""]

    # Maturity interpretation
    level = maturity.maturity_level
    if level == "ADVANCED":
        interp = (
            "The service demonstrates advanced observability practice. "
            "All core signals are present and well-configured. "
            "Focus on maintaining quality and reducing MTTR for edge cases."
        )
    elif level == "PROFICIENT":
        interp = (
            "The service has solid observability coverage with minor gaps. "
            "Address PARTIAL and MISSING dimensions to reach ADVANCED. "
            "Prioritise SLO/SLI definitions and burn-rate alerting if not yet complete."
        )
    elif level == "DEVELOPING":
        interp = (
            "Core signals are present but coverage is incomplete. "
            "Structured logs, distributed tracing, and correlation IDs are the highest-leverage improvements. "
            "Define SLIs/SLOs before adding more instrumentation."
        )
    else:
        interp = (
            "Foundational observability signals are missing. "
            "Start with correlation IDs, structured JSON logs, and golden signal metrics. "
            "Without these, failures are not diagnosable in production."
        )

    lines += [
        f"_{interp}_",
        "",
        "---",
        "",
        "## 2. Maturity Scorecard",
        "",
        "| Dimension | Score | Max | Rating | Description |",
        "|---|---|---|---|---|",
    ]

    for dr in maturity.dimension_results:
        lines.append(
            f"| {dr.dimension} | {dr.raw_score} | {dr.max_score} | **{dr.rating}** | {dr.description} |"
        )

    lines += [
        "",
        "_Rating thresholds: COMPLETE (≥90% of max) · PARTIAL (50–89%) · MISSING (<50%)_",
        "_Maturity levels: ADVANCED (≥85) · PROFICIENT (65–84) · DEVELOPING (40–64) · FOUNDATIONAL (<40)_",
        "",
        "---",
        "",
    ]

    # SLO section
    if slo_results:
        lines += [
            "## 3. SLO Error Budget Status",
            "",
            "| SLO | Service | Type | Target | Actual | Burn Rate | Consumed | Status |",
            "|---|---|---|---|---|---|---|---|",
        ]
        for r in slo_results:
            burn_str = f"{r.burn_rate:.2f}x" if r.burn_rate != float("inf") else "∞"
            lines.append(
                f"| {r.slo.name} | {r.slo.service} | {r.slo.metric_type} "
                f"| {r.slo.target_pct:.3f}% | {r.slo.current_availability_pct:.3f}% "
                f"| {burn_str} | {r.consumed_pct:.1f}% | **{r.status}** |"
            )

        lines += [
            "",
            "_burn_rate = (1 − actual_availability) / (1 − target_availability)_",
            "",
            "---",
            "",
        ]

    # Remediation plan
    lines += [
        "## 4. Prioritised Improvement Plan",
        "",
        "Dimensions ordered by impact. Address MISSING dimensions first, then PARTIAL.",
        "",
    ]

    missing_dims = [dr for dr in maturity.dimension_results if dr.rating == "MISSING"]
    partial_dims = [dr for dr in maturity.dimension_results if dr.rating == "PARTIAL"]
    complete_dims = [dr for dr in maturity.dimension_results if dr.rating == "COMPLETE"]

    remediation_guidance: Dict[str, List[str]] = {
        "structured_logs": [
            "Emit logs as structured JSON to stdout/stderr",
            "Include `request_id` / `trace_id` in every log record",
            "Redact or mask PII fields (email, tokens, SSNs) before emission",
            "Use a log pipeline (OpenTelemetry Collector filelog receiver or equivalent)",
        ],
        "metrics": [
            "Instrument the four golden signals: latency, traffic, errors, saturation",
            "Use histograms (not averages) for latency; prefer native histograms in Prometheus",
            "Attach exemplars to histogram observations to link traces to metrics",
            "Expose a /metrics endpoint or push via OTLP to your metrics backend",
        ],
        "distributed_tracing": [
            "Add OpenTelemetry auto-instrumentation for your runtime (Node.js, Python, Go, Java)",
            "Add manual spans around business workflow boundaries, not just route-level calls",
            "Verify `traceparent` propagation across HTTP, message queues, and RPC boundaries",
            "Export traces via OTLP to Jaeger, Tempo, or your APM backend",
        ],
        "slo_sli": [
            "Define SLIs for each critical user journey (availability, latency, error rate)",
            "Set SLO targets with explicit error budgets (e.g., 99.9% over 30 days)",
            "Document an error budget policy: what triggers a freeze vs. a postmortem",
            "Use `assets/monitoring/slo/slo-definition.yaml` as your SLO definition template",
        ],
        "alerting": [
            "Replace raw infrastructure alerts with multi-window burn-rate alerts",
            "Use 1-hour and 6-hour burn-rate windows for fast and slow burn detection",
            "Tune alert thresholds to reduce alert fatigue; target < 5 pages/on-call week",
            "Use `assets/monitoring/slo/prometheus-alert-rules.yaml` as your alert template",
        ],
        "correlation_ids": [
            "Generate a `request_id` (UUID v4) at the outermost entry point (API gateway or load balancer)",
            "Propagate `request_id` via HTTP headers (`X-Request-ID`) across all service calls",
            "Include `request_id` in every log line, span, and error response",
            "Validate propagation with an end-to-end integration test that checks for the ID in downstream logs",
        ],
    }

    def emit_dimension_remediation(
        buf: List[str], dims: List[DimensionResult], label: str
    ) -> None:
        if not dims:
            return
        buf.append(f"### {label}")
        buf.append("")
        for dr in dims:
            buf += [
                f"#### {dr.dimension}",
                "",
                f"- **Score**: {dr.raw_score} / {dr.max_score} ({dr.rating})",
                f"- **Description**: {dr.description}",
                "",
                "**Steps to improve:**",
                "",
            ]
            for step in remediation_guidance.get(dr.dimension, ["See skill references."]):
                buf.append(f"- {step}")
            buf.append("")

    emit_dimension_remediation(lines, missing_dims, "MISSING Dimensions (highest priority)")
    emit_dimension_remediation(lines, partial_dims, "PARTIAL Dimensions")

    if complete_dims:
        lines += [
            "### COMPLETE Dimensions",
            "",
            ", ".join(dr.dimension for dr in complete_dims),
            "",
        ]

    # SLO remediation
    if slo_results:
        non_healthy = [r for r in slo_results if r.status != SLO_STATUS_HEALTHY]
        if non_healthy:
            lines += [
                "---",
                "",
                "## 5. SLO Remediation",
                "",
            ]
            for r in non_healthy:
                lines += [
                    f"### {r.slo.name} — {r.status}",
                    "",
                    f"- **Service**: {r.slo.service}",
                    f"- **Burn rate**: {r.burn_rate:.2f}x ({r.consumed_pct:.1f}% of budget consumed)",
                    f"- **Remaining budget**: {r.remaining_budget_events} events",
                    "",
                    "**Actions:**",
                    "",
                ]
                if r.status == SLO_STATUS_EXHAUSTED:
                    lines += [
                        "- Declare an incident if not already open",
                        "- Freeze non-critical feature work until budget is restored",
                        "- Run a postmortem within 48 hours",
                        "- Review burn-rate alert rules — why was this not caught earlier?",
                    ]
                elif r.status == SLO_STATUS_CRITICAL:
                    lines += [
                        "- Escalate to on-call lead immediately",
                        "- Stop non-critical deployments until burn rate drops below 1.0x",
                        "- Investigate the error source using correlated traces and logs",
                    ]
                else:  # AT_RISK
                    lines += [
                        "- Investigate increased error or latency source",
                        "- Consider a deployment freeze if burn rate continues rising",
                        "- Review recent deploys and configuration changes",
                    ]
                lines.append("")

    if profile.notes:
        lines += [
            "---",
            "",
            "## Profile Notes",
            "",
            f"_{profile.notes}_",
        ]

    lines += [
        "",
        "---",
        "",
        "_Report generated by observability_scorer.py — qa-observability skill_",
    ]

    output = "\n".join(lines)

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(output)
        print(f"Report written to {args.output}")
    else:
        print(output)

    return 0


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Observability maturity scoring and SLO error budget tool (qa-observability).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # --- maturity ---
    p_maturity = sub.add_parser(
        "maturity",
        help="Score observability maturity across 6 signal dimensions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Score observability maturity (0–100) across 6 signal dimensions.\n\n"
            "Dimensions and weights:\n"
            "  structured_logs    (0–20)\n"
            "  metrics            (0–20)\n"
            "  distributed_tracing(0–20)\n"
            "  slo_sli            (0–15)\n"
            "  alerting           (0–15)\n"
            "  correlation_ids    (0–10)\n\n"
            "Maturity levels:\n"
            "  ADVANCED     — total ≥ 85\n"
            "  PROFICIENT   — total 65–84\n"
            "  DEVELOPING   — total 40–64\n"
            "  FOUNDATIONAL — total < 40\n\n"
            "Per-dimension rating:\n"
            "  COMPLETE — ≥ 90% of max score\n"
            "  PARTIAL  — 50–89% of max score\n"
            "  MISSING  — < 50% of max score\n\n"
            "Example:\n"
            "  python scripts/observability_scorer.py maturity \\\n"
            "    --input data/sample-observability-profile.json"
        ),
    )
    p_maturity.add_argument("--input", required=True, help="Path to observability profile JSON")

    # --- slo ---
    p_slo = sub.add_parser(
        "slo",
        help="Calculate error budget status for each SLO",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Calculate error budget burn rate and status for each SLO.\n\n"
            "Formula:\n"
            "  burn_rate = (1 − actual_availability) / (1 − target_availability)\n\n"
            "Status flags:\n"
            "  HEALTHY         — burn rate ≤ 20% of budget\n"
            "  AT_RISK         — burn rate > 20% of budget\n"
            "  CRITICAL        — burn rate > 50%, budget exhausted in < 20% of window\n"
            "  BUDGET_EXHAUSTED — burn rate > 100% (budget already spent)\n\n"
            "Example:\n"
            "  python scripts/observability_scorer.py slo \\\n"
            "    --input data/sample-slo-data.json"
        ),
    )
    p_slo.add_argument("--input", required=True, help="Path to SLO data JSON array")

    # --- report ---
    p_report = sub.add_parser(
        "report",
        help="Full observability readiness report (maturity + SLO)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "Produces a Markdown report covering:\n"
            "  1. Executive summary\n"
            "  2. Maturity scorecard per dimension\n"
            "  3. SLO error budget status table (if --slos provided)\n"
            "  4. Prioritised improvement plan\n"
            "  5. SLO remediation actions (if applicable)\n\n"
            "Examples:\n"
            "  python scripts/observability_scorer.py report \\\n"
            "    --input data/sample-observability-profile.json \\\n"
            "    --slos  data/sample-slo-data.json\n\n"
            "  python scripts/observability_scorer.py report \\\n"
            "    --input data/sample-observability-profile.json \\\n"
            "    --slos  data/sample-slo-data.json \\\n"
            "    --output report.md"
        ),
    )
    p_report.add_argument("--input", required=True, help="Path to observability profile JSON")
    p_report.add_argument("--slos", metavar="FILE", help="Path to SLO data JSON (optional)")
    p_report.add_argument("--output", metavar="FILE", help="Write report to file (default: stdout)")

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    dispatch = {
        "maturity": cmd_maturity,
        "slo": cmd_slo,
        "report": cmd_report,
    }
    return dispatch[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
