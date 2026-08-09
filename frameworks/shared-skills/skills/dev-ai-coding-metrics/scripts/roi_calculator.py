#!/usr/bin/env python3
"""
AI coding metrics ROI calculator — stdlib-only CLI tool.

Subcommands:
  roi    — Calculate ROI: time saved, cost saved, payback period, annualized ROI %
  score  — Score adoption across 6 metric families with a health grade (A/B/C/D/F)
  report — Full metrics dashboard report in Markdown

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

# Grade thresholds (applied to composite score 0-100)
GRADE_BANDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
    (60, "D"),
    (0,  "F"),
]

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
    composite: float
    grade: str
    summary: str


@dataclass
class RoiResult:
    team_size: int
    hours_saved_per_dev_per_week: float
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
    annualized_roi_pct: float
    measurement_period_weeks: int


# ---------------------------------------------------------------------------
# Core calculation functions
# ---------------------------------------------------------------------------

def classify_rating(score: int) -> str:
    for threshold, rating in RATING_BANDS:
        if score >= threshold:
            return rating
    return "Weak"


def classify_grade(composite: float) -> str:
    for threshold, grade in GRADE_BANDS:
        if composite >= threshold:
            return grade
    return "F"


def calc_family_scores(data: dict) -> list[FamilyScore]:
    families_raw = data.get("metric_families", {})
    results: list[FamilyScore] = []

    for key in FAMILY_KEYS:
        family_data = families_raw.get(key, {})
        score = int(family_data.get("score", 0))
        signals = family_data.get("signals", [])
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
    families = calc_family_scores(data)
    composite = sum(f.score for f in families) / len(families) if families else 0.0
    grade = classify_grade(composite)

    strong_count = sum(1 for f in families if f.rating == "Strong")
    weak_count = sum(1 for f in families if f.rating == "Weak")

    if grade in ("A", "B"):
        summary = f"Program is performing well across most families ({strong_count} Strong). Sustain and expand."
    elif grade == "C":
        summary = f"Mixed results. Focus investment on Weak families ({weak_count} flagged). Address quality and agent risks."
    elif grade == "D":
        summary = f"Below threshold. Significant gaps in {weak_count} families. Reassess program design before expanding."
    else:
        summary = "Program is underperforming across the board. Consider a structured reset with a focused pilot scope."

    return ScoreResult(
        families=families,
        composite=round(composite, 1),
        grade=grade,
        summary=summary,
    )


def calc_roi(data: dict) -> RoiResult:
    team_size = int(data.get("team_size", 0))
    hours_saved = float(data.get("hours_saved_per_dev_per_week", 0.0))
    hourly_rate = float(data.get("avg_dev_hourly_rate", 0.0))
    monthly_cost = float(data.get("ai_tooling_monthly_cost", 0.0))
    period_weeks = int(data.get("measurement_period_weeks", 12))

    weekly_hours_saved = team_size * hours_saved
    monthly_hours_saved = weekly_hours_saved * (MONTHS_PER_YEAR / WEEKS_PER_YEAR) * WEEKS_PER_YEAR / MONTHS_PER_YEAR
    # Simpler: monthly = weekly * (52/12)
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
    annualized_roi_pct = (annual_net / annual_cost * 100) if annual_cost > 0 else 0.0

    return RoiResult(
        team_size=team_size,
        hours_saved_per_dev_per_week=hours_saved,
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
        annualized_roi_pct=round(annualized_roi_pct, 1),
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


def fmt_pct(value: float) -> str:
    return f"{value:.1f}%"


def fmt_weeks(value: float) -> str:
    if value == float("inf"):
        return "N/A"
    return f"{value:.1f} weeks"


def print_separator(width: int = 62, char: str = "-") -> None:
    print(char * width)


def print_kv(label: str, value: str, width: int = 36) -> None:
    print(f"  {label:<{width}} {value}")


def grade_bar(score: int, width: int = 20) -> str:
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
    print_kv("  Payback period", fmt_weeks(r.payback_weeks))
    print_kv("  Annualized ROI", fmt_pct(r.annualized_roi_pct))
    print()
    print("  Note: Time-saved inputs are self-reported estimates. Validate")
    print("  against delivery metrics before presenting to leadership.")
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
        bar = grade_bar(f.score)
        row = "  " + "  ".join([
            f"{f.label:<{col_w[0]}}",
            f"{f.score:<{col_w[1]}}",
            f"{f.rating:<{col_w[2]}}",
            f"{bar:<{col_w[3]}}",
        ])
        print(row)

    print_separator()
    print(f"  Composite score: {result.composite:.1f} / 100")
    print(f"  Health grade:    {result.grade}")
    print()
    print(f"  Assessment: {result.summary}")
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
    adoption_pct = data.get("adoption_pct", None)

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
    a(f"**Composite score:** {score_result.composite:.1f} / 100  ")
    a(f"**Health grade:** {score_result.grade}  ")
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
    a(f"| Weekly hours saved (team) | {fmt_hours(roi.weekly_hours_saved)} |")
    a(f"| Annual hours saved (team) | {fmt_hours(roi.annual_hours_saved)} |")
    a(f"| Annual value of time saved | {fmt_money(roi.annual_value_saved)} |")
    a(f"| Annual tool cost | {fmt_money(roi.ai_tooling_annual_cost)} |")
    a(f"| Annual net savings | {fmt_money(roi.annual_net_savings)} |")
    a(f"| Payback period | {fmt_weeks(roi.payback_weeks)} |")
    a(f"| Annualized ROI | {fmt_pct(roi.annualized_roi_pct)} |")
    a("")
    a("> **Assumption note:** Hours-saved inputs are self-reported estimates.")
    a("> Triangulate with delivery metrics before citing to leadership.")
    a("> A conservative 50% discount on self-reported hours is a reasonable starting adjustment.")
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
    a("## Measurement Rules Applied")
    a("")
    a("1. Baseline established before rollout (12-week reference period).")
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
            return json.load(f)
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
        help="Score adoption across 6 metric families with a health grade (A/B/C/D/F).",
        description=(
            "Reads per-family scores from the input JSON and outputs a scorecard table "
            "with Strong/Developing/Weak ratings, a composite 0-100 score, and a health grade."
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


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
