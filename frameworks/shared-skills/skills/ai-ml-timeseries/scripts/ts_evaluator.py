#!/usr/bin/env python3
"""
Time series forecast evaluator — stdlib-only CLI tool.

Subcommands:
  backtest     — Analyze rolling-origin backtest results: MAE/RMSE/MAPE per horizon,
                 horizon degradation flag, comparison against naive baseline.
  calibration  — Check probabilistic calibration for 50%, 80%, and 90% intervals.
  report       — Full time series model evaluation report (Markdown).

Usage:
  python scripts/ts_evaluator.py backtest --input data/sample-forecast-results.json
  python scripts/ts_evaluator.py calibration --input data/sample-forecast-results.json
  python scripts/ts_evaluator.py report --input data/sample-forecast-results.json --output report.md
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CONFIDENCE_LEVELS = [
    ("50", "lower_50", "upper_50"),
    ("80", "lower_80", "upper_80"),
    ("90", "lower_90", "upper_90"),
]

CALIBRATION_GOOD_THRESHOLD = 0.05   # < 5 pp calibration error is good
SKILL_SCORE_GOOD = 0.10             # > 10% improvement over naive = meaningful
DEGRADATION_THRESHOLD = 1.5         # MAE(h) / MAE(h=1) expected growth rate cap


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class HorizonMetrics:
    horizon_h: int
    n: int
    mae: float
    rmse: float
    mape: float
    naive_mae: float
    skill_score: float


@dataclass
class CalibrationResult:
    level: str
    stated_coverage: float
    actual_coverage: float
    calibration_error: float
    diagnosis: str   # "good", "under-confident", "over-confident"
    n: int


@dataclass
class DegradationFlag:
    horizon_h: int
    mae: float
    mae_h1: float
    ratio: float
    expected_ratio: float
    flagged: bool


@dataclass
class BacktestReport:
    model_name: str
    target_variable: str
    horizon_metrics: list[HorizonMetrics]
    degradation_flags: list[DegradationFlag]


@dataclass
class CalibrationReport:
    model_name: str
    target_variable: str
    results: list[CalibrationResult]


# ---------------------------------------------------------------------------
# Core metric functions
# ---------------------------------------------------------------------------

def _compute_horizon_metrics(windows: list[dict]) -> list[HorizonMetrics]:
    """Group windows by horizon and compute MAE, RMSE, MAPE, naive MAE, skill score."""
    by_horizon: dict[int, list[dict]] = defaultdict(list)
    for w in windows:
        by_horizon[w["horizon_h"]].append(w)

    results: list[HorizonMetrics] = []
    for h in sorted(by_horizon.keys()):
        rows = by_horizon[h]
        n = len(rows)

        errors = [abs(r["actual_value"] - r["point_forecast"]) for r in rows]
        sq_errors = [(r["actual_value"] - r["point_forecast"]) ** 2 for r in rows]
        pct_errors = [
            abs(r["actual_value"] - r["point_forecast"]) / abs(r["actual_value"])
            for r in rows
            if r["actual_value"] != 0
        ]

        mae = sum(errors) / n
        rmse = math.sqrt(sum(sq_errors) / n)
        mape = (sum(pct_errors) / len(pct_errors)) * 100 if pct_errors else float("nan")

        # Naive baseline: predict last known value = the actual at horizon 1 for this origin
        # Because we only have one series, naive = predict the value from origin_date
        # We approximate: for horizon h, naive forecast = actual at h=1 for same origin.
        # If h=1 rows are available, use them; else fall back to mean actuals as naive proxy.
        naive_errors = _compute_naive_errors(rows, by_horizon.get(1, []))
        naive_mae = sum(naive_errors) / len(naive_errors) if naive_errors else mae

        skill_score = 1.0 - (mae / naive_mae) if naive_mae > 0 else float("nan")

        results.append(HorizonMetrics(
            horizon_h=h,
            n=n,
            mae=mae,
            rmse=rmse,
            mape=mape,
            naive_mae=naive_mae,
            skill_score=skill_score,
        ))

    return results


def _compute_naive_errors(
    rows: list[dict],
    h1_rows: list[dict],
) -> list[float]:
    """
    Naive baseline: predict the value known at the origin (i.e. the actual at h=1).
    Match by origin_date. If no h=1 row for an origin, fall back to the row's own actual
    as the naive prediction (zero skill).
    """
    h1_by_origin = {r["origin_date"]: r["actual_value"] for r in h1_rows}
    errors: list[float] = []
    for r in rows:
        naive_pred = h1_by_origin.get(r["origin_date"], r["actual_value"])
        errors.append(abs(r["actual_value"] - naive_pred))
    return errors


def _compute_degradation_flags(
    horizon_metrics: list[HorizonMetrics],
) -> list[DegradationFlag]:
    """
    Flag horizons where MAE grows faster than a linear-proportional expectation.
    Expected: MAE(h) <= MAE(h=1) * (h / 1) * DEGRADATION_THRESHOLD
    In practice we flag if ratio > DEGRADATION_THRESHOLD compared to ratio-vs-h1.
    """
    if not horizon_metrics:
        return []

    mae_h1 = horizon_metrics[0].mae  # baseline (h=1)
    flags: list[DegradationFlag] = []

    for hm in horizon_metrics:
        ratio = hm.mae / mae_h1 if mae_h1 > 0 else 1.0
        expected_ratio = DEGRADATION_THRESHOLD
        flagged = (hm.horizon_h > 1) and (ratio > expected_ratio)
        flags.append(DegradationFlag(
            horizon_h=hm.horizon_h,
            mae=hm.mae,
            mae_h1=mae_h1,
            ratio=ratio,
            expected_ratio=expected_ratio,
            flagged=flagged,
        ))

    return flags


def _compute_calibration(
    windows: list[dict],
) -> list[CalibrationResult]:
    """Compute coverage and calibration error for each confidence level."""
    results: list[CalibrationResult] = []
    n = len(windows)

    for level_str, lower_key, upper_key in CONFIDENCE_LEVELS:
        stated = float(level_str) / 100.0
        hits = sum(
            1 for w in windows
            if w.get(lower_key) is not None
            and w.get(upper_key) is not None
            and w[lower_key] <= w["actual_value"] <= w[upper_key]
        )
        valid_n = sum(
            1 for w in windows
            if w.get(lower_key) is not None and w.get(upper_key) is not None
        )
        actual_coverage = hits / valid_n if valid_n > 0 else float("nan")
        cal_error = abs(actual_coverage - stated)

        if math.isnan(actual_coverage):
            diagnosis = "no data"
        elif cal_error < CALIBRATION_GOOD_THRESHOLD:
            diagnosis = "good"
        elif actual_coverage > stated:
            diagnosis = "under-confident"  # intervals are wider than needed
        else:
            diagnosis = "over-confident"   # intervals are too narrow

        results.append(CalibrationResult(
            level=level_str,
            stated_coverage=stated,
            actual_coverage=actual_coverage,
            calibration_error=cal_error,
            diagnosis=diagnosis,
            n=valid_n,
        ))

    return results


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _fmt_float(v: float, decimals: int = 1) -> str:
    if math.isnan(v):
        return "N/A"
    return f"{v:.{decimals}f}"


def _fmt_pct(v: float) -> str:
    if math.isnan(v):
        return "N/A"
    return f"{v * 100:.1f}%"


def _fmt_number(v: float) -> str:
    if math.isnan(v):
        return "N/A"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if v >= 1_000:
        return f"{v / 1_000:.1f}K"
    return f"{v:.0f}"


def print_separator(width: int = 64, char: str = "-") -> None:
    print(char * width)


def print_kv(label: str, value: str, width: int = 32) -> None:
    print(f"  {label:<{width}} {value}")


def print_table_row(cols: list[str], widths: list[int]) -> None:
    row = "  ".join(f"{str(c):<{w}}" for c, w in zip(cols, widths))
    print(row)


# ---------------------------------------------------------------------------
# Subcommand: backtest
# ---------------------------------------------------------------------------

def cmd_backtest(args: argparse.Namespace) -> None:
    data = _load_json(args.input)
    windows = data.get("backtest_windows", [])
    model_name = data.get("model_name", "unknown")
    target = data.get("target_variable", "unknown")

    if not windows:
        print("Error: No backtest_windows found in input file.", file=sys.stderr)
        sys.exit(1)

    horizon_metrics = _compute_horizon_metrics(windows)
    degradation_flags = _compute_degradation_flags(horizon_metrics)

    col_widths = [8, 6, 10, 10, 8, 12, 10]
    headers = ["Horizon", "  N", "MAE", "RMSE", "MAPE%", "Naive MAE", "Skill"]

    print()
    print(f"=== BACKTEST ANALYSIS: {model_name} ===")
    print(f"  Target: {target}")
    print(f"  Windows: {len(windows)}  |  Horizons: {sorted(set(w['horizon_h'] for w in windows))}")
    print()
    print_separator(68)
    print_table_row(headers, col_widths)
    print_separator(68)

    for hm in horizon_metrics:
        skill_str = _fmt_float(hm.skill_score, 3)
        row = [
            f"h={hm.horizon_h}",
            str(hm.n),
            _fmt_number(hm.mae),
            _fmt_number(hm.rmse),
            _fmt_float(hm.mape, 1),
            _fmt_number(hm.naive_mae),
            skill_str,
        ]
        print_table_row(row, col_widths)

    print_separator(68)

    # Degradation summary
    flagged = [f for f in degradation_flags if f.flagged]
    print()
    print("  Horizon Degradation Check")
    print(f"  Threshold: MAE(h) / MAE(h=1) > {DEGRADATION_THRESHOLD:.1f}")
    print()
    for f in degradation_flags[1:]:   # skip h=1 (baseline)
        flag_str = "  *** FLAGGED ***" if f.flagged else ""
        print(f"    h={f.horizon_h:>2}  ratio={f.ratio:.2f}  (threshold {f.expected_ratio:.1f}){flag_str}")

    if flagged:
        print()
        print(f"  WARNING: {len(flagged)} horizon(s) exceed degradation threshold.")
        print("  Consider direct multi-step forecasting or additional horizon-specific features.")
    else:
        print()
        print("  No horizons exceed degradation threshold.")

    print()
    for hm in horizon_metrics:
        if hm.skill_score < 0:
            print(f"  WARNING: h={hm.horizon_h} skill score {hm.skill_score:.3f} is negative — model is worse than naive baseline.")
    print()


# ---------------------------------------------------------------------------
# Subcommand: calibration
# ---------------------------------------------------------------------------

def cmd_calibration(args: argparse.Namespace) -> None:
    data = _load_json(args.input)
    windows = data.get("backtest_windows", [])
    model_name = data.get("model_name", "unknown")
    target = data.get("target_variable", "unknown")

    if not windows:
        print("Error: No backtest_windows found in input file.", file=sys.stderr)
        sys.exit(1)

    results = _compute_calibration(windows)

    col_widths = [8, 14, 16, 16, 14]
    headers = ["Level", "Stated", "Actual", "Cal. Error", "Diagnosis"]

    print()
    print(f"=== CALIBRATION ANALYSIS: {model_name} ===")
    print(f"  Target: {target}  |  Total windows: {len(windows)}")
    print()
    print_separator(72)
    print_table_row(headers, col_widths)
    print_separator(72)

    for r in results:
        row = [
            f"{r.level}%",
            _fmt_pct(r.stated_coverage),
            _fmt_pct(r.actual_coverage),
            _fmt_pct(r.calibration_error),
            r.diagnosis,
        ]
        print_table_row(row, col_widths)

    print_separator(72)

    # Summary
    print()
    print(f"  Calibration threshold: < {CALIBRATION_GOOD_THRESHOLD * 100:.0f} pp error = good")
    print()

    n_good = sum(1 for r in results if r.diagnosis == "good")
    n_over = sum(1 for r in results if r.diagnosis == "over-confident")
    n_under = sum(1 for r in results if r.diagnosis == "under-confident")

    print(f"  Good:            {n_good}/{len(results)} interval(s)")
    if n_over:
        print(f"  Over-confident:  {n_over} interval(s)  — actual coverage < stated level.")
        print("                   Intervals are too narrow; predictions are more certain than warranted.")
        print("                   Consider widening intervals via recalibration or conformal methods.")
    if n_under:
        print(f"  Under-confident: {n_under} interval(s)  — actual coverage > stated level.")
        print("                   Intervals are wider than necessary; sharpness can be improved.")

    print()
    overall_score = 1.0 - (sum(r.calibration_error for r in results) / len(results))
    print(f"  Overall calibration score: {overall_score:.3f}  (1.0 = perfect; lower = worse)")
    print()


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    input_path = getattr(args, "input", None)
    output_path = getattr(args, "output", None)

    if not input_path:
        print("Error: --input <json_file> is required for the report subcommand.", file=sys.stderr)
        sys.exit(1)

    data = _load_json(input_path)
    windows = data.get("backtest_windows", [])
    model_name = data.get("model_name", "unknown")
    target = data.get("target_variable", "unknown")
    horizons = data.get("forecast_horizons", sorted(set(w["horizon_h"] for w in windows)))
    description = data.get("description", "")

    horizon_metrics = _compute_horizon_metrics(windows)
    degradation_flags = _compute_degradation_flags(horizon_metrics)
    calibration_results = _compute_calibration(windows)

    lines: list[str] = []
    a = lines.append

    a("# Time Series Forecast Evaluation Report")
    a("")
    a(f"**Model:** {model_name}  ")
    a(f"**Target variable:** {target}  ")
    a(f"**Forecast horizons:** {horizons}  ")
    a(f"**Backtest windows:** {len(windows)}  ")
    if description:
        a(f"**Description:** {description}  ")
    a("")

    # --- Backtest metrics ---
    a("---")
    a("")
    a("## Backtest Metrics by Horizon")
    a("")
    a("| Horizon | N | MAE | RMSE | MAPE % | Naive MAE | Skill Score |")
    a("|---------|---|-----|------|--------|-----------|-------------|")
    for hm in horizon_metrics:
        skill_str = _fmt_float(hm.skill_score, 3)
        a(f"| h={hm.horizon_h} | {hm.n} | {_fmt_number(hm.mae)} | {_fmt_number(hm.rmse)} | {_fmt_float(hm.mape, 1)}% | {_fmt_number(hm.naive_mae)} | {skill_str} |")
    a("")
    a("> **Skill Score** = 1 - MAE(model) / MAE(naive). Positive = better than naive. > 0.10 = meaningful improvement.")
    a("")

    # --- Horizon degradation ---
    a("---")
    a("")
    a("## Horizon Degradation Analysis")
    a("")
    a(f"Threshold: MAE(h) / MAE(h=1) > {DEGRADATION_THRESHOLD:.1f} triggers a flag.")
    a("")
    a("| Horizon | MAE | Ratio vs h=1 | Flagged |")
    a("|---------|-----|--------------|---------|")
    for f in degradation_flags:
        flag_str = "YES — review" if f.flagged else "No"
        a(f"| h={f.horizon_h} | {_fmt_number(f.mae)} | {f.ratio:.2f}x | {flag_str} |")
    a("")
    flagged = [f for f in degradation_flags if f.flagged]
    if flagged:
        a(f"> **WARNING:** {len(flagged)} horizon(s) show unexpected error degradation. "
          "Consider direct multi-step strategies, horizon-specific features, or additional training data.")
    else:
        a("> All horizons within expected degradation bounds.")
    a("")

    # --- Negative skill warnings ---
    negative_skill = [hm for hm in horizon_metrics if not math.isnan(hm.skill_score) and hm.skill_score < 0]
    if negative_skill:
        a("### Negative Skill Score Warnings")
        a("")
        for hm in negative_skill:
            a(f"- **h={hm.horizon_h}:** skill score {hm.skill_score:.3f} — model is worse than naive baseline at this horizon.")
        a("")

    # --- Calibration ---
    a("---")
    a("")
    a("## Probabilistic Calibration")
    a("")
    a(f"Good calibration: coverage error < {CALIBRATION_GOOD_THRESHOLD * 100:.0f} pp.")
    a("")
    a("| CI Level | Stated Coverage | Actual Coverage | Error | Diagnosis |")
    a("|----------|-----------------|-----------------|-------|-----------|")
    for r in calibration_results:
        a(f"| {r.level}% | {_fmt_pct(r.stated_coverage)} | {_fmt_pct(r.actual_coverage)} | {_fmt_pct(r.calibration_error)} | {r.diagnosis} |")
    a("")
    overall_score = 1.0 - (sum(r.calibration_error for r in calibration_results) / len(calibration_results))
    a(f"**Overall calibration score:** {overall_score:.3f} (1.0 = perfect)")
    a("")

    n_over = sum(1 for r in calibration_results if r.diagnosis == "over-confident")
    n_under = sum(1 for r in calibration_results if r.diagnosis == "under-confident")
    n_good_cal = sum(1 for r in calibration_results if r.diagnosis == "good")

    if n_good_cal == len(calibration_results):
        a("> All confidence intervals are well-calibrated.")
    else:
        if n_over:
            a(f"> **Over-confident intervals ({n_over}):** Actual coverage falls below stated level — intervals are too narrow. "
              "Recalibrate using conformal prediction or isotonic regression on held-out data.")
        if n_under:
            a(f"> **Under-confident intervals ({n_under}):** Actual coverage exceeds stated level — intervals are wider than needed. "
              "Tighten intervals to improve sharpness without sacrificing coverage.")
    a("")

    # --- Recommendations ---
    a("---")
    a("")
    a("## Summary and Recommendations")
    a("")
    best_skill = max(
        (hm for hm in horizon_metrics if not math.isnan(hm.skill_score)),
        key=lambda x: x.skill_score,
        default=None,
    )
    worst_skill = min(
        (hm for hm in horizon_metrics if not math.isnan(hm.skill_score)),
        key=lambda x: x.skill_score,
        default=None,
    )
    if best_skill:
        a(f"- Best skill at **h={best_skill.horizon_h}** (skill score {best_skill.skill_score:.3f}).")
    if worst_skill:
        a(f"- Weakest skill at **h={worst_skill.horizon_h}** (skill score {worst_skill.skill_score:.3f}).")
    if flagged:
        a(f"- Horizon degradation flagged at: {[f.horizon_h for f in flagged]}. Investigate direct multi-step or richer lag features.")
    if n_over:
        a(f"- {n_over} over-confident CI(s). Apply conformal recalibration before production.")
    if n_under:
        a(f"- {n_under} under-confident CI(s). Intervals can be tightened for better sharpness.")
    if not flagged and not n_over and not n_under:
        a("- No critical issues detected. Model is better than naive across all horizons with well-calibrated intervals.")
    a("")

    report_text = "\n".join(lines)

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
        prog="ts_evaluator",
        description="Time series forecast evaluator — stdlib only. No pip install required.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="SUBCOMMAND")
    subparsers.required = True

    # --- backtest ---
    p_backtest = subparsers.add_parser(
        "backtest",
        help="Analyze rolling-origin backtest results: MAE/RMSE/MAPE per horizon, degradation, naive comparison.",
        description=(
            "Compute MAE, RMSE, MAPE per horizon from rolling-origin backtest results. "
            "Compare against a naive baseline and flag horizons where error grows "
            "faster than expected (degradation check)."
        ),
    )
    p_backtest.add_argument(
        "--input",
        metavar="JSON_FILE",
        required=True,
        help="Path to backtest results JSON (e.g. data/sample-forecast-results.json).",
    )
    p_backtest.set_defaults(func=cmd_backtest)

    # --- calibration ---
    p_calibration = subparsers.add_parser(
        "calibration",
        help="Check probabilistic calibration for 50%%, 80%%, and 90%% confidence intervals.",
        description=(
            "For each confidence interval (50%%, 80%%, 90%%), compute the actual coverage "
            "and compare to the stated level. Output calibration error and diagnosis: "
            "'good', 'over-confident' (intervals too narrow), or 'under-confident' (too wide)."
        ),
    )
    p_calibration.add_argument(
        "--input",
        metavar="JSON_FILE",
        required=True,
        help="Path to backtest results JSON (e.g. data/sample-forecast-results.json).",
    )
    p_calibration.set_defaults(func=cmd_calibration)

    # --- report ---
    p_report = subparsers.add_parser(
        "report",
        help="Generate a full Markdown time series evaluation report.",
        description=(
            "Reads a backtest results JSON and produces a Markdown report combining "
            "horizon-wise metrics, degradation analysis, probabilistic calibration, "
            "and actionable recommendations."
        ),
    )
    p_report.add_argument(
        "--input",
        metavar="JSON_FILE",
        required=True,
        help="Path to backtest results JSON (e.g. data/sample-forecast-results.json).",
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
