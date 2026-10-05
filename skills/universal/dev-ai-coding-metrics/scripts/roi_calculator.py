#!/usr/bin/env python3
"""
AI coding metrics ROI calculator — stdlib-only CLI tool.

Subcommands:
  roi    — Calculate ROI: time saved, cost saved, payback period, annualized ROI %
  score  — Rate each of the 6 metric families (Strong/Developing/Weak); no composite
  report — Full metrics dashboard report in Markdown

Fails closed: a missing metric family or ROI input exits 2 and names the missing
keys. There is no composite score or letter grade — a blended AI productivity score
is rejected by the skill's anti-gaming checklist.

Usage:
  python scripts/roi_calculator.py roi --input data/sample-ai-metrics.json
  python scripts/roi_calculator.py score --input data/sample-ai-metrics.json
  python scripts/roi_calculator.py report --input data/sample-ai-metrics.json
  python scripts/roi_calculator.py report --input data/sample-ai-metrics.json --output report.md
"""

from __future__ import annotations

import argparse
import datetime
import json
import math
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# 6 metric families and their display labels
FAMILY_KEYS = [
    "adoption",
    "delivery",
    "quality",
    "economics",
    "experience",
    "agent_execution",
]

FAMILY_LABELS = {
    "adoption": "Adoption",
    "delivery": "Delivery",
    "quality": "Quality",
    "economics": "Economics",
    "experience": "Experience",
    "agent_execution": "Agent Execution",
}

# Score thresholds for rating bands
RATING_BANDS = [
    (80, "Strong"),
    (60, "Developing"),
    (0,  "Weak"),
]

ROI_REQUIRED_KEYS = [
    "team_size",
    "hours_saved_per_dev_per_week",
    "avg_dev_hourly_rate",
    "ai_tooling_monthly_cost",
    "measurement_period_weeks",
]

# Optional burden terms. Unless both are supplied, the ROI output is labelled
# "excludes review burden, not decision-grade".
ROI_BURDEN_KEYS = [
    "review_hours_per_dev_per_week",
    "rework_hours_per_dev_per_week",
]

EXIT_INSUFFICIENT_DATA = 2

BURDEN_CAVEAT = (
    "ROI has incomplete review burden or rework cost: supply both "
    "review_hours_per_dev_per_week and rework_hours_per_dev_per_week "
    "(explicit zero if measured absent); not decision-grade."
)

WEEKS_PER_YEAR = 52
MONTHS_PER_YEAR = 12


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class FamilyScore:
    key: str
    label: str
    score: int
    rating: str
    signals: list[str]


@dataclass
class ScoreResult:
    families: list[FamilyScore]
    summary: str


@dataclass
class RoiResult:
    team_size: int
    hours_saved_per_dev_per_week: float
    burden_hours_per_dev_per_week: float
    burden_included: bool
    weekly_hours_saved: float
    monthly_hours_saved: float
    annual_hours_saved: float
    avg_dev_hourly_rate: float
    monthly_value_saved: float
    annual_value_saved: float
    ai_tooling_monthly_cost: float
    ai_tooling_annual_cost: float
    monthly_net_savings: float
    annual_net_savings: float
    payback_weeks: float
    annualized_roi_pct: float | None
    measurement_period_weeks: int


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------

def classify_rating(score: int) -> str:
    for threshold, rating in RATING_BANDS:
        if score >= threshold:
            return rating
    return "Weak"


class InsufficientData(ValueError):
    """Raised when required inputs are missing; never scored as zero."""


def numeric(data: dict, key: str, *, integer=False, minimum=0, maximum=None):
    value = data.get(key)
    if (isinstance(value, bool) or not isinstance(value, (int, float))
            or not math.isfinite(value) or value < minimum
            or (maximum is not None and value > maximum)
            or (integer and not isinstance(value, int))):
        raise InsufficientData(f"invalid {key}: expected a finite {'integer' if integer else 'number'}"
                               f" >= {minimum}" + (f" and <= {maximum}" if maximum is not None else ""))
    return value


def missing_family_keys(data: dict) -> list[str]:
    families_raw = data.get("metric_families")
    if not isinstance(families_raw, dict):
        return [f"metric_families.{k}.score" for k in FAMILY_KEYS]
    missing = []
    for key in FAMILY_KEYS:
        family = families_raw.get(key)
        if not isinstance(family, dict) or family.get("score") is None:
            missing.append(f"metric_families.{key}.score")
    return missing


def missing_roi_keys(data: dict) -> list[str]:
    return [k for k in ROI_REQUIRED_KEYS if data.get(k) is None]


def calc_family_scores(data: dict) -> list[FamilyScore]:
    missing = missing_family_keys(data)
    if missing:
        raise InsufficientData(", ".join(missing))
    families_raw = data["metric_families"]
    results: list[FamilyScore] = []

    for key in FAMILY_KEYS:
        family_data = families_raw[key]
        score = numeric(family_data, "score", integer=True, maximum=100)
        signals = family_data.get("signals", [])
        if not isinstance(signals, list) or any(not isinstance(signal, str) for signal in signals):
            raise InsufficientData(f"invalid metric_families.{key}.signals: expected a string array")
        rating = classify_rating(score)
        results.append(FamilyScore(
            key=key,
            label=FAMILY_LABELS[key],
            score=score,
            rating=rating,
            signals=signals,
        ))

    return results


def calc_score(data: dict) -> ScoreResult:
    """Per-family ratings only. No composite, no letter grade, no program verdict."""
    families = calc_family_scores(data)
    weak = [f.label for f in families if f.rating == "Weak"]
    if weak:
        summary = (f"Weak families: {', '.join(weak)}. Read each family on its own; "
                   "do not average families into one program score.")
    else:
        summary = "No family rated Weak. Read each family on its own; do not average them."
    return ScoreResult(families=families, summary=summary)


def calc_roi(data: dict) -> RoiResult:
    missing = missing_roi_keys(data)
    if missing:
        raise InsufficientData(", ".join(missing))
    team_size = numeric(data, "team_size", integer=True, minimum=1)
    hours_saved = numeric(data, "hours_saved_per_dev_per_week")
    hourly_rate = numeric(data, "avg_dev_hourly_rate")
    monthly_cost = numeric(data, "ai_tooling_monthly_cost")
    period_weeks = numeric(data, "measurement_period_weeks", integer=True, minimum=1)

    # Review and rework time spent on AI output is a cost, not a saving.
    burden_included = all(k in data for k in ROI_BURDEN_KEYS)
    burden_hours = sum(numeric(data, k) for k in ROI_BURDEN_KEYS if k in data)

    weekly_hours_saved = team_size * (hours_saved - burden_hours)
    # monthly = weekly * (52/12)
    monthly_hours_saved = weekly_hours_saved * WEEKS_PER_YEAR / MONTHS_PER_YEAR
    annual_hours_saved = weekly_hours_saved * WEEKS_PER_YEAR

    monthly_value = monthly_hours_saved * hourly_rate
    annual_value = annual_hours_saved * hourly_rate

    annual_cost = monthly_cost * MONTHS_PER_YEAR
    monthly_net = monthly_value - monthly_cost
    annual_net = annual_value - annual_cost

    # Payback period in weeks: time until cumulative savings cover first month of cost
    # (i.e. how many weeks of savings equal one month of tool cost)
    if weekly_hours_saved > 0 and hourly_rate > 0:
        weekly_value = weekly_hours_saved * hourly_rate
        payback_weeks = monthly_cost / weekly_value if weekly_value > 0 else float("inf")
    else:
        payback_weeks = float("inf")

    # Annualized ROI % = (annual net savings / annual cost) * 100
    annualized_roi_pct = (annual_net / annual_cost * 100) if annual_cost > 0 else None

    return RoiResult(
        team_size=team_size,
        hours_saved_per_dev_per_week=hours_saved,
        burden_hours_per_dev_per_week=burden_hours,
        burden_included=burden_included,
        weekly_hours_saved=weekly_hours_saved,
        monthly_hours_saved=round(monthly_hours_saved, 1),
        annual_hours_saved=round(annual_hours_saved, 1),
        avg_dev_hourly_rate=hourly_rate,
        monthly_value_saved=round(monthly_value, 2),
        annual_value_saved=round(annual_value, 2),
        ai_tooling_monthly_cost=monthly_cost,
        ai_tooling_annual_cost=annual_cost,
        monthly_net_savings=round(monthly_net, 2),
        annual_net_savings=round(annual_net, 2),
        payback_weeks=round(payback_weeks, 1),
        annualized_roi_pct=round(annualized_roi_pct, 1) if annualized_roi_pct is not None else None,
        measurement_period_weeks=period_weeks,
    )


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_money(value: float, prefix: str = "$") -> str:
    if value >= 1_000_000:
        return f"{prefix}{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{prefix}{value / 1_000:.1f}K"
    return f"{prefix}{value:.0f}"


def fmt_hours(value: float) -> str:
    return f"{value:,.1f} hrs"


def fmt_pct(value: float | None) -> str:
    return "N/A (zero tooling cost)" if value is None else f"{value:.1f}%"


def fmt_weeks(value: float) -> str:
    if value == float("inf"):
        return "N/A"
    return f"{value:.1f} weeks"


def print_separator(width: int = 62, char: str = "-") -> None:
    print(char * width)


def print_kv(label: str, value: str, width: int = 36) -> None:
    print(f"  {label:<{width}} {value}")


def score_bar(score: int, width: int = 20) -> str:
    filled = round(score / 100 * width)
    return "[" + "#" * filled + "." * (width - filled) + "]"


# ---------------------------------------------------------------------------
# Subcommand: roi
# ---------------------------------------------------------------------------

def cmd_roi(args: argparse.Namespace) -> None:
    data = _load_json(args.input)
    r = calc_roi(data)

    team_name = data.get("team_name", "Engineering Team")

    print()
    print(f"=== ROI ANALYSIS: {team_name} ===")
    print_separator()
    print_kv("Team size", f"{r.team_size} developers")
    print_kv("Measurement period", f"{r.measurement_period_weeks} weeks")
    print_kv("Hours saved / dev / week", fmt_hours(r.hours_saved_per_dev_per_week))
    print_kv("Review + rework / dev / week", fmt_hours(r.burden_hours_per_dev_per_week))
    print_kv("Avg dev rate (fully loaded)", fmt_money(r.avg_dev_hourly_rate) + "/hr")
    print_kv("AI tooling cost (monthly)", fmt_money(r.ai_tooling_monthly_cost))
    print_separator()
    print("  TIME SAVED")
    print_kv("  Weekly hours saved (team)", fmt_hours(r.weekly_hours_saved))
    print_kv("  Monthly hours saved (team)", fmt_hours(r.monthly_hours_saved))
    print_kv("  Annual hours saved (team)", fmt_hours(r.annual_hours_saved))
    print_separator()
    print("  FINANCIAL IMPACT")
    print_kv("  Monthly value of time saved", fmt_money(r.monthly_value_saved))
    print_kv("  Annual value of time saved", fmt_money(r.annual_value_saved))
    print_kv("  Annual tool cost", fmt_money(r.ai_tooling_annual_cost))
    print_kv("  Annual net savings", fmt_money(r.annual_net_savings))
    print_separator()
    print("  ROI SUMMARY")
    print_kv("  Tool-cost-equivalent weeks", fmt_weeks(r.payback_weeks))
    print_kv("  Annualized ROI", fmt_pct(r.annualized_roi_pct))
    print()
    print("  Note: Time-saved inputs are self-reported estimates. Validate")
    print("  against delivery metrics before presenting to leadership.")
    if not r.burden_included:
        print(f"  {BURDEN_CAVEAT}")
    print()


# ---------------------------------------------------------------------------
# Subcommand: score
# ---------------------------------------------------------------------------

def cmd_score(args: argparse.Namespace) -> None:
    data = _load_json(args.input)
    result = calc_score(data)

    team_name = data.get("team_name", "Engineering Team")
    period = data.get("measurement_period_weeks", "?")

    print()
    print(f"=== ADOPTION SCORECARD: {team_name} ===")
    print(f"  Measurement period: {period} weeks")
    print_separator()

    col_w = [18, 7, 14, 22]
    headers = ["Family", "Score", "Rating", "Health bar"]
    header_row = "  " + "  ".join(f"{h:<{w}}" for h, w in zip(headers, col_w))
    print(header_row)
    print_separator()

    for f in result.families:
        bar = score_bar(f.score)
        row = "  " + "  ".join([
            f"{f.label:<{col_w[0]}}",
            f"{f.score:<{col_w[1]}}",
            f"{f.rating:<{col_w[2]}}",
            f"{bar:<{col_w[3]}}",
        ])
        print(row)

    print_separator()
    print(f"  {result.summary}")
    print()

    if args.signals:
        print("  --- Key Signals by Family ---")
        for f in result.families:
            if f.signals:
                print(f"\n  [{f.label}]")
                for sig in f.signals:
                    print(f"    • {sig}")
        print()


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    data = _load_json(args.input)

    team_name = data.get("team_name", "Engineering Team")
    team_size = data.get("team_size", 0)
    period = data.get("measurement_period_weeks", 0)
    notes = data.get("notes", "")
    missing = missing_roi_keys(data) + missing_family_keys(data)
    if missing:
        raise InsufficientData(", ".join(missing))

    roi = calc_roi(data)
    score_result = calc_score(data)

    lines: list[str] = []
    a = lines.append

    a("# AI Coding Metrics Dashboard")
    a("")
    a(f"**Team:** {team_name}  ")
    a(f"**Team size:** {team_size} developers  ")
    a(f"**Measurement period:** {period} weeks  ")
    a(f"**Report date:** {datetime.date.today().isoformat()}  ")
    if notes:
        a(f"**Notes:** {notes}  ")
    a("")

    # --- Scorecard ---
    a("---")
    a("")
    a("## Scorecard")
    a("")
    a("Per-family ratings only; families are not averaged into a composite score or grade.")
    a("")
    a("| Family | Score | Rating | Signals (sample) |")
    a("|--------|-------|--------|-----------------|")

    for f in score_result.families:
        first_signal = f.signals[0] if f.signals else "—"
        # Truncate long signals for table readability
        if len(first_signal) > 70:
            first_signal = first_signal[:67] + "..."
        a(f"| {f.label} | {f.score} | {f.rating} | {first_signal} |")

    a("")
    a(f"> {score_result.summary}")
    a("")

    # --- ROI Analysis ---
    a("---")
    a("")
    a("## ROI Analysis")
    a("")
    a("| Metric | Value |")
    a("|--------|-------|")
    a(f"| Hours saved / dev / week | {roi.hours_saved_per_dev_per_week} hrs |")
    a(f"| Review + rework / dev / week | {roi.burden_hours_per_dev_per_week} hrs |")
    a(f"| Weekly hours saved (team) | {fmt_hours(roi.weekly_hours_saved)} |")
    a(f"| Annual hours saved (team) | {fmt_hours(roi.annual_hours_saved)} |")
    a(f"| Annual value of time saved | {fmt_money(roi.annual_value_saved)} |")
    a(f"| Annual tool cost | {fmt_money(roi.ai_tooling_annual_cost)} |")
    a(f"| Annual net savings | {fmt_money(roi.annual_net_savings)} |")
    a(f"| Tool-cost-equivalent weeks | {fmt_weeks(roi.payback_weeks)} |")
    a(f"| Annualized ROI | {fmt_pct(roi.annualized_roi_pct)} |")
    a("")
    a("> **Assumption note:** Hours-saved inputs are self-reported estimates.")
    a("> Triangulate with delivery metrics before citing to leadership.")
    a("> Value of capacity is a scenario estimate, not realized cash savings; calibrate assumptions against observed outcomes.")
    if not roi.burden_included:
        a(f"> **{BURDEN_CAVEAT}**")
    a("")

    # --- Per-family signals ---
    a("---")
    a("")
    a("## Metric Family Details")
    a("")

    for f in score_result.families:
        a(f"### {f.label} — {f.score}/100 ({f.rating})")
        a("")
        if f.signals:
            for sig in f.signals:
                a(f"- {sig}")
        else:
            a("- No signals recorded.")
        a("")

    # --- Measurement rules reminder ---
    a("---")
    a("")
    a("## Measurement Rules to Confirm Before Sharing")
    a("")
    a("1. Baseline of at least 8 weeks established before rollout.")
    a("2. Assistant and agent metrics tracked separately.")
    a("3. Every speed metric paired with at least one quality metric.")
    a("4. Results aggregated at team level — no individual surveillance.")
    a("5. Self-reported inputs labeled as estimates, not evidence.")
    a("")

    report_text = "\n".join(lines)

    output_path = getattr(args, "output", None)
    if output_path:
        Path(output_path).write_text(report_text, encoding="utf-8")
        print(f"Report written to: {output_path}")
    else:
        print(report_text)


# ---------------------------------------------------------------------------
# JSON loader
# ---------------------------------------------------------------------------

def _load_json(path: str) -> dict:
    p = Path(path)
    if not p.exists():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(1)
    try:
        with p.open(encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                raise InsufficientData("input: expected a JSON object")
            return data
    except json.JSONDecodeError as exc:
        print(f"Error: Invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(1)


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="roi_calculator",
        description="AI coding metrics ROI calculator — stdlib only. No pip install required.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="SUBCOMMAND")
    subparsers.required = True

    # --- roi ---
    p_roi = subparsers.add_parser(
        "roi",
        help="Calculate ROI: time saved, cost saved, payback period, annualized ROI pct.",
        description=(
            "Reads team size, hours saved per dev per week, tooling cost, and hourly rate "
            "from the input JSON and outputs weekly/monthly/annual savings, net benefit, "
            "payback period in weeks, and annualized ROI percentage."
        ),
    )
    p_roi.add_argument(
        "--input",
        metavar="JSON_FILE",
        required=True,
        help="Path to metrics JSON file (e.g. data/sample-ai-metrics.json).",
    )
    p_roi.set_defaults(func=cmd_roi)

    # --- score ---
    p_score = subparsers.add_parser(
        "score",
        help="Rate each of the 6 metric families (Strong/Developing/Weak); no composite grade.",
        description=(
            "Reads per-family scores from the input JSON and outputs a scorecard table "
            "with Strong/Developing/Weak ratings per family. Exits 2 if any family is missing."
        ),
    )
    p_score.add_argument(
        "--input",
        metavar="JSON_FILE",
        required=True,
        help="Path to metrics JSON file (e.g. data/sample-ai-metrics.json).",
    )
    p_score.add_argument(
        "--signals",
        action="store_true",
        default=False,
        help="Print all key signals for each family after the scorecard table.",
    )
    p_score.set_defaults(func=cmd_score)

    # --- report ---
    p_report = subparsers.add_parser(
        "report",
        help="Generate a full Markdown metrics dashboard report from a JSON input file.",
        description=(
            "Combines scorecard, ROI analysis, and per-family signal details into a single "
            "Markdown report. Prints to stdout by default; use --output to write to a file."
        ),
    )
    p_report.add_argument(
        "--input",
        metavar="JSON_FILE",
        required=True,
        help="Path to metrics JSON file (e.g. data/sample-ai-metrics.json).",
    )
    p_report.add_argument(
        "--output",
        metavar="OUTPUT_FILE",
        help="Write Markdown report to this file instead of stdout.",
    )
    p_report.set_defaults(func=cmd_report)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.func(args)
    except InsufficientData as exc:
        print(f"Error: insufficient data or invalid input: {exc}. Nothing was scored.", file=sys.stderr)
        return EXIT_INSUFFICIENT_DATA
    return 0


if __name__ == "__main__":
    sys.exit(main())
