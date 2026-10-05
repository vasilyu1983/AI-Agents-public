#!/usr/bin/env python3
"""
Time series forecast evaluator — stdlib-only CLI tool.

Subcommands:
  backtest     — Rolling-origin backtest metrics per horizon: MAE/RMSE/MAPE, MASE,
                 and skill against the naive (and optional seasonal-naive) baseline
                 at the same horizon.
  calibration  — Coverage of the 50%, 80% and 90% intervals per horizon, judged
                 screened against a Wilson score interval assuming independent hits;
                 pooled coverage is descriptive only.
  report       — Full time series model evaluation report (Markdown).

Input contract (fail closed): every backtest row needs origin_date, horizon_h,
actual_value, point_forecast and origin_value (the last value observed at the
forecast origin, which defines the naive forecast). Numbers must be finite with
magnitude <= MAX_ABS_VALUE. Invalid input exits 2 and names the offending row
(or the file, when it is missing, unreadable or not JSON); no metric is printed
from partial input. A supplied interval level must cover every row, so missing
intervals cannot silently select a favorable subset. An unwritable report
--output path also exits 2.

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
from dataclasses import dataclass
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

REQUIRED_ROW_NUMBERS = ("actual_value", "point_forecast", "origin_value")

SKILL_SCORE_GOOD = 0.10             # > 10% improvement over the baseline = meaningful
# Two-sided 95% normal quantile; each screen assumes independent hits with common coverage.
WILSON_Z = 1.96
# With independent origins, even five wins fail a two-sided 5% sign test (2 * 0.5**5 = 0.0625).
MIN_ORIGINS_FOR_VERDICT = 6
# Keeps squared errors (at most (2e150)**2 = 4e300) and their sums below the float maximum (~1.8e308).
MAX_ABS_VALUE = 1e150
NUMBER_RULE = f"a finite number with magnitude <= {MAX_ABS_VALUE:g} (rescale larger series, e.g. to thousands)"

EXIT_INPUT_ERROR = 2


class InputError(ValueError):
    """Raised when the input file breaks the contract; the CLI exits 2."""


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class HorizonMetrics:
    horizon_h: int
    n: int
    mae: float
    rmse: float
    mape: float                 # nan when every row's actual is ~0 (see mape_excluded)
    mape_excluded: int          # rows left out of MAPE: actual is 0 or its percentage error overflows
    mase: float                 # nan when no history_values were supplied
    naive_mae: float
    snaive_mae: float           # nan when seasonal_naive_forecast is absent
    baseline_name: str          # the stronger (lower-MAE) baseline at this horizon
    baseline_mae: float
    skill_score: float          # 1 - MAE / baseline MAE at the same horizon; nan when baseline MAE is 0
    n_origins: int              # distinct origin_date values at this horizon
    verdict: str                # "beats baseline", "marginal", "worse than baseline", "undefined",
                                # or "insufficient origins" below MIN_ORIGINS_FOR_VERDICT


@dataclass
class CalibrationResult:
    level: str
    horizon: Optional[int]   # None = descriptive pooled row; no inferential interval
    stated_coverage: float
    actual_coverage: float
    calibration_error: float
    ci_low: float            # Wilson score interval for the observed coverage
    ci_high: float
    diagnosis: str   # "consistent with nominal (n=...)", "under-confident", "over-confident", "no data"
    n: int           # rows; distinct origins do not establish independent coverage hits
    n_origins: int


# ---------------------------------------------------------------------------
# Input validation (runs before any metric)
# ---------------------------------------------------------------------------

def _is_number(v: object) -> bool:
    # The bound also rejects nan and inf, and compares huge JSON integers without float overflow.
    return isinstance(v, (int, float)) and not isinstance(v, bool) and abs(v) <= MAX_ABS_VALUE


def validate(data: object, need_intervals: bool = False,
             need_seasonal_complete: bool = True) -> tuple[list[dict], Optional[float]]:
    """Check the input contract. Returns (windows, mase_scale). Raises InputError.

    need_seasonal_complete=False skips the seasonal-baseline completeness rules for
    commands that never read seasonal_naive_forecast (calibration); a present value
    must still be a finite number.
    """
    if not isinstance(data, dict):
        raise InputError("top level must be a JSON object")
    windows = data.get("backtest_windows")
    if not isinstance(windows, list) or not windows:
        raise InputError("backtest_windows must be a non-empty list")

    seen: set[tuple[str, int]] = set()
    for i, w in enumerate(windows):
        where = f"backtest_windows[{i}]"
        if not isinstance(w, dict):
            raise InputError(f"{where}: must be an object")
        origin = w.get("origin_date")
        if not isinstance(origin, str) or not origin:
            raise InputError(f"{where}: origin_date must be a non-empty string")
        h = w.get("horizon_h")
        if not isinstance(h, int) or isinstance(h, bool) or h < 1:
            raise InputError(f"{where}: horizon_h must be an integer >= 1, got {h!r}")
        for key in REQUIRED_ROW_NUMBERS:
            if key not in w:
                hint = (" (the last observed value at the origin; without it no naive "
                        "baseline can be computed)") if key == "origin_value" else ""
                raise InputError(f"{where}: missing {key}{hint}")
            if not _is_number(w[key]):
                raise InputError(f"{where}: {key} must be {NUMBER_RULE}, got {w[key]!r}")
        if "seasonal_naive_forecast" in w and not _is_number(w["seasonal_naive_forecast"]):
            raise InputError(f"{where}: seasonal_naive_forecast must be {NUMBER_RULE}")
        if (origin, h) in seen:
            raise InputError(f"{where}: duplicate row for origin {origin!r}, horizon {h}")
        seen.add((origin, h))

        present = []
        for level, lo_key, hi_key in CONFIDENCE_LEVELS:
            has_lo, has_hi = lo_key in w, hi_key in w
            if has_lo != has_hi:
                raise InputError(f"{where}: {level}% interval needs both {lo_key} and {hi_key}")
            if not has_lo:
                continue
            lo, hi = w[lo_key], w[hi_key]
            if not (_is_number(lo) and _is_number(hi)):
                raise InputError(f"{where}: {level}% interval bounds must each be {NUMBER_RULE}")
            if lo > hi:
                raise InputError(f"{where}: inverted {level}% interval ({lo_key}={lo} > {hi_key}={hi})")
            present.append((lo, hi))
        # Wider levels must contain narrower ones (no quantile crossing).
        for (lo_a, hi_a), (lo_b, hi_b) in zip(present, present[1:]):
            if lo_b > lo_a or hi_b < hi_a:
                raise InputError(f"{where}: crossing intervals (a wider level is inside a narrower one)")

    seasonal_by_horizon: dict[int, list[bool]] = defaultdict(list)
    for w in windows if need_seasonal_complete else []:
        seasonal_by_horizon[w["horizon_h"]].append("seasonal_naive_forecast" in w)
    for horizon, present in seasonal_by_horizon.items():
        if any(present) and not all(present):
            raise InputError(
                f"horizon {horizon}: seasonal_naive_forecast must be supplied "
                "for every row or none"
            )
    # A horizon without the seasonal baseline would be judged against naive alone
    # while the others use the stronger of the two, so require all horizons or none.
    with_seasonal = sorted(h for h, present in seasonal_by_horizon.items() if all(present))
    without_seasonal = sorted(h for h, present in seasonal_by_horizon.items() if not any(present))
    if with_seasonal and without_seasonal:
        raise InputError(
            f"horizons {without_seasonal}: seasonal_naive_forecast must be supplied "
            f"for every horizon or none (present for horizons {with_seasonal})"
        )

    for level, lower_key, _ in CONFIDENCE_LEVELS:
        present = [lower_key in w for w in windows]
        if any(present) and not all(present):
            missing = next(i for i, supplied in enumerate(present) if not supplied)
            raise InputError(
                f"backtest_windows[{missing}]: {level}% interval must be supplied "
                "for every row or none; partial coverage would select a subset"
            )

    if need_intervals and not any(lo in w for w in windows for _, lo, _ in CONFIDENCE_LEVELS):
        raise InputError("no prediction-interval fields (lower_50/upper_50, ...) in any row")

    mase_scale: Optional[float] = None
    history = data.get("history_values")
    if history is not None:
        m = data.get("season_length", 1)
        if not isinstance(m, int) or isinstance(m, bool) or m < 1:
            raise InputError(f"season_length must be an integer >= 1, got {m!r}")
        if not isinstance(history, list) or len(history) <= m or not all(_is_number(v) for v in history):
            raise InputError(f"history_values must be a list of more than season_length ({m}) values, "
                             f"each {NUMBER_RULE}")
        diffs = [abs(history[t] - history[t - m]) for t in range(m, len(history))]
        mase_scale = sum(diffs) / len(diffs)
        if mase_scale == 0:
            raise InputError("history_values give a zero in-sample naive error; MASE is undefined")
    return windows, mase_scale


# ---------------------------------------------------------------------------
# Core metric functions
# ---------------------------------------------------------------------------

def _mae(pairs: list[tuple[float, float]]) -> float:
    return sum(abs(a - f) for a, f in pairs) / len(pairs)


def _compute_horizon_metrics(windows: list[dict], mase_scale: Optional[float]) -> list[HorizonMetrics]:
    """Per horizon: model error, naive / seasonal-naive error at the SAME horizon, skill."""
    by_horizon: dict[int, list[dict]] = defaultdict(list)
    for w in windows:
        by_horizon[w["horizon_h"]].append(w)

    results: list[HorizonMetrics] = []
    for h in sorted(by_horizon):
        rows = by_horizon[h]
        n = len(rows)
        model = [(r["actual_value"], r["point_forecast"]) for r in rows]
        mae = _mae(model)
        rmse = math.sqrt(sum((a - f) ** 2 for a, f in model) / n)
        # A row's percentage error is undefined when its actual is 0 or so close to 0 that the
        # ratio overflows; such rows are left out of MAPE and counted.
        pct = [abs(a - f) / abs(a) for a, f in model if a != 0]
        pct = [x for x in pct if math.isfinite(x)]
        mape_excluded = n - len(pct)
        mape = (sum(pct) / len(pct)) * 100 if pct else float("nan")
        mase = mae / mase_scale if mase_scale else float("nan")

        # Naive forecast for every horizon = the value observed at the origin.
        naive_mae = _mae([(r["actual_value"], r["origin_value"]) for r in rows])
        snaive_mae = float("nan")
        if all("seasonal_naive_forecast" in r for r in rows):
            snaive_mae = _mae([(r["actual_value"], r["seasonal_naive_forecast"]) for r in rows])

        baseline_name, baseline_mae = "naive", naive_mae
        if not math.isnan(snaive_mae) and snaive_mae < naive_mae:
            baseline_name, baseline_mae = "seasonal naive", snaive_mae

        skill = 1.0 - mae / baseline_mae if baseline_mae > 0 else float("nan")
        n_origins = len({r["origin_date"] for r in rows})
        if n_origins < MIN_ORIGINS_FOR_VERDICT:
            verdict = "insufficient origins"
        elif baseline_mae == 0:
            # A perfect baseline is beaten by nothing; only an equally perfect model ties it.
            verdict = "undefined" if mae == 0 else "worse than baseline"
        elif skill >= SKILL_SCORE_GOOD:
            verdict = "beats baseline"
        elif skill >= 0:
            verdict = "marginal"
        else:
            verdict = "worse than baseline"

        hm = HorizonMetrics(h, n, mae, rmse, mape, mape_excluded, mase, naive_mae, snaive_mae,
                            baseline_name, baseline_mae, skill, n_origins, verdict)
        # nan is a documented "not applicable" value; inf only comes from a near-zero denominator.
        for name in ("mae", "rmse", "mape", "mase", "naive_mae", "snaive_mae", "baseline_mae", "skill_score"):
            if math.isinf(getattr(hm, name)):
                raise InputError(
                    f"h={h}: computed {name} is not a finite number (a near-zero denominator: "
                    "history_values that barely vary give a near-zero MASE scale, a near-exact baseline "
                    "gives a near-zero skill denominator); check those values or drop the near-constant rows"
                )
        results.append(hm)
    return results


def _metrics_or_exit(path: str, windows: list[dict], mase_scale: Optional[float]) -> list[HorizonMetrics]:
    try:
        return _compute_horizon_metrics(windows, mase_scale)
    except InputError as exc:
        print(f"Error: invalid input in {path}: {exc}", file=sys.stderr)
        sys.exit(EXIT_INPUT_ERROR)


def _wilson(hits: int, n: int, z: float = WILSON_Z) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""
    p = hits / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


def _coverage(level: str, horizon: Optional[int], rows: list[dict],
              lower_key: str, upper_key: str) -> CalibrationResult:
    stated = float(level) / 100.0
    n = len(rows)
    n_origins = len({w["origin_date"] for w in rows})
    hits = sum(1 for w in rows if w[lower_key] <= w["actual_value"] <= w[upper_key])
    actual = hits / n
    # Horizons from one origin share data state. Repeating those hits cannot add independent
    # trials, so the pooled rate is descriptive and must never decide a level's verdict.
    if horizon is None:
        nan = float("nan")
        return CalibrationResult(level, horizon, stated, actual, abs(actual - stated), nan, nan,
                                 "descriptive only (shared origins)", n, n_origins)
    lo, hi = _wilson(hits, n)
    if lo <= stated <= hi:
        diagnosis = f"consistent with nominal (n={n})"
    elif actual > stated:
        diagnosis = "under-confident"  # intervals wider than needed
    else:
        diagnosis = "over-confident"   # intervals too narrow
    return CalibrationResult(level, horizon, stated, actual, abs(actual - stated), lo, hi,
                             diagnosis, n, n_origins)


def _compute_calibration(windows: list[dict]) -> list[CalibrationResult]:
    """Per level: horizon-wise independence-assuming screens, then descriptive pooled coverage."""
    results: list[CalibrationResult] = []
    nan = float("nan")
    for level, lower_key, upper_key in CONFIDENCE_LEVELS:
        rows = [w for w in windows if lower_key in w]
        if not rows:
            results.append(CalibrationResult(level, None, float(level) / 100.0, nan, nan, nan, nan,
                                             "no data", 0, 0))
            continue
        by_horizon: dict[int, list[dict]] = defaultdict(list)
        for w in rows:
            by_horizon[w["horizon_h"]].append(w)
        for h in sorted(by_horizon):
            results.append(_coverage(level, h, by_horizon[h], lower_key, upper_key))
        results.append(_coverage(level, None, rows, lower_key, upper_key))
    return results


def _flagged(results: list[CalibrationResult], diagnosis: str) -> list[CalibrationResult]:
    return [r for r in results if r.diagnosis == diagnosis]


def _level_verdicts(results: list[CalibrationResult]) -> list[str]:
    """One line per level: only horizon screens decide; pooled rows are descriptive."""
    lines = []
    for level, _, _ in CONFIDENCE_LEVELS:
        cells = [r for r in results if r.level == level and r.n > 0 and r.horizon is not None]
        if not cells:
            lines.append(f"{level}%: no data")
            continue
        bad = [r for r in cells if r.diagnosis in ("over-confident", "under-confident")]
        if bad:
            lines.append(f"{level}%: " + "; ".join(
                f"{r.diagnosis} {'at h=' + str(r.horizon) if r.horizon is not None else 'pooled'} "
                f"({_fmt_pct(r.actual_coverage)}, n={r.n})" for r in bad))
        else:
            lines.append(f"{level}%: consistent with nominal at every horizon "
                         f"(independence assumed; smallest n={min(r.n for r in cells)})")
    return lines


def _overall_calibration(results: list[CalibrationResult]) -> float:
    scored = [r for r in results if r.horizon is not None]
    return 1.0 - sum(r.calibration_error for r in scored) / len(scored)


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _fmt_float(v: float, decimals: int = 1) -> str:
    if math.isnan(v):
        return "N/A"
    if abs(v) >= 1e9:
        return f"{v:.3g}"
    return f"{v:.{decimals}f}"


def _fmt_pct(v: float) -> str:
    if math.isnan(v):
        return "N/A"
    return f"{v * 100:.1f}%"


def _fmt_number(v: float) -> str:
    if math.isnan(v):
        return "N/A"
    if abs(v) >= 1e12:
        return f"{v:.3g}"
    if abs(v) >= 1_000_000:
        return f"{v / 1_000_000:.2f}M"
    if abs(v) >= 1_000:
        return f"{v / 1_000:.1f}K"
    if abs(v) >= 10:
        return f"{v:.0f}"
    return f"{v:.3g}"


def _calibration_cells(r: CalibrationResult) -> tuple[str, str, str]:
    """Horizon, CI and diagnosis cells for one calibration row."""
    if not r.n:
        return "-", "N/A", r.diagnosis
    horizon = f"h={r.horizon}" if r.horizon is not None else f"pooled ({r.n_origins} origins)"
    ci = "N/A" if r.horizon is None else f"{_fmt_pct(r.ci_low)}-{_fmt_pct(r.ci_high)}"
    return horizon, ci, r.diagnosis


def print_separator(width: int = 64, char: str = "-") -> None:
    print(char * width)


def print_table_row(cols: list[str], widths: list[int]) -> None:
    print("  ".join(f"{str(c):<{w}}" for c, w in zip(cols, widths)))


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def _load_json(path: str) -> object:
    p = Path(path)
    if not p.is_file():
        print(f"Error: File not found: {path}", file=sys.stderr)
        sys.exit(EXIT_INPUT_ERROR)
    try:
        with p.open(encoding="utf-8") as f:
            return json.load(f)
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Error: cannot read {path}: {exc}", file=sys.stderr)
        sys.exit(EXIT_INPUT_ERROR)
    except ValueError as exc:  # JSONDecodeError, or an integer past the int-string digit limit
        print(f"Error: Invalid JSON in {path}: {exc}", file=sys.stderr)
        sys.exit(EXIT_INPUT_ERROR)


def _load_valid(path: str, need_intervals: bool = False,
                need_seasonal_complete: bool = True) -> tuple[dict, list[dict], Optional[float]]:
    data = _load_json(path)
    try:
        windows, mase_scale = validate(data, need_intervals=need_intervals,
                                       need_seasonal_complete=need_seasonal_complete)
    except InputError as exc:
        print(f"Error: invalid input in {path}: {exc}", file=sys.stderr)
        sys.exit(EXIT_INPUT_ERROR)
    return data, windows, mase_scale  # type: ignore[return-value]


# ---------------------------------------------------------------------------
# Subcommand: backtest
# ---------------------------------------------------------------------------

def _baseline_warning(hm: HorizonMetrics) -> Optional[str]:
    if hm.baseline_mae == 0:
        field = "origin_value" if hm.baseline_name == "naive" else "seasonal_naive_forecast"
        outcome = ("the model also has zero error; skill is undefined" if hm.mae == 0
                   else f"the model (MAE {_fmt_number(hm.mae)}) is worse")
        return (f"h={hm.horizon_h} the {hm.baseline_name} baseline has zero error, so {outcome}; "
                f"check that {field} is not copied from actual_value.")
    if hm.verdict == "worse than baseline":
        return (f"h={hm.horizon_h} skill {_fmt_float(hm.skill_score, 3)}: the model is worse than "
                f"the {hm.baseline_name} baseline.")
    if hm.verdict == "insufficient origins":
        return (f"h={hm.horizon_h} has {hm.n_origins} origin(s); add backtest origins until there are "
                f">= {MIN_ORIGINS_FOR_VERDICT} before judging this horizon.")
    return None


def _mape_notes(horizon_metrics: list[HorizonMetrics]) -> list[str]:
    return [f"h={hm.horizon_h} excludes {hm.mape_excluded} of {hm.n} row(s) whose actual is ~0 "
            "(percentage error undefined)" for hm in horizon_metrics if hm.mape_excluded]


def cmd_backtest(args: argparse.Namespace) -> None:
    data, windows, mase_scale = _load_valid(args.input)
    horizon_metrics = _metrics_or_exit(args.input, windows, mase_scale)

    col_widths = [7, 4, 8, 8, 7, 6, 9, 15, 7]
    headers = ["Horizon", "N", "MAE", "RMSE", "MAPE%", "MASE", "Base MAE", "Baseline", "Skill"]

    print()
    print(f"=== BACKTEST ANALYSIS: {data.get('model_name', 'unknown')} ===")
    print(f"  Target: {data.get('target_variable', 'unknown')}")
    print(f"  Windows: {len(windows)}  |  Horizons: {sorted(set(w['horizon_h'] for w in windows))}")
    print()
    print_separator(90)
    print_table_row(headers, col_widths)
    print_separator(90)
    for hm in horizon_metrics:
        print_table_row([
            f"h={hm.horizon_h}", str(hm.n), _fmt_number(hm.mae), _fmt_number(hm.rmse),
            _fmt_float(hm.mape, 1), _fmt_float(hm.mase, 2), _fmt_number(hm.baseline_mae),
            hm.baseline_name, _fmt_float(hm.skill_score, 3),
        ], col_widths)
    print_separator(90)

    print()
    print("  Horizon verdicts (skill vs the stronger baseline at the same horizon;")
    print(f"  error growth with horizon is expected and is not itself a defect; meaningful skill >= {SKILL_SCORE_GOOD:.2f};")
    print(f"  a verdict needs >= {MIN_ORIGINS_FOR_VERDICT} distinct origins; confirm with a paired test before promoting)")
    for hm in horizon_metrics:
        print(f"    h={hm.horizon_h:>3}  {hm.verdict}  ({hm.n_origins} origins)")
    if mase_scale is None:
        print()
        print("  MASE: N/A (add history_values and season_length to the input to scale errors).")
    for note in _mape_notes(horizon_metrics):
        print(f"  MAPE: {note}")
    for hm in horizon_metrics:
        warning = _baseline_warning(hm)
        if warning:
            print(f"  WARNING: {warning}")
    print()



# ---------------------------------------------------------------------------
# Subcommand: calibration
# ---------------------------------------------------------------------------

def cmd_calibration(args: argparse.Namespace) -> None:
    # Calibration never reads seasonal_naive_forecast, so its completeness is not required.
    data, windows, _ = _load_valid(args.input, need_intervals=True, need_seasonal_complete=False)
    results = _compute_calibration(windows)

    col_widths = [6, 20, 8, 8, 15, 6, 30]
    headers = ["Level", "Horizon", "Stated", "Actual", "95% Wilson CI", "N", "Diagnosis"]

    print()
    print(f"=== CALIBRATION ANALYSIS: {data.get('model_name', 'unknown')} ===")
    print(f"  Target: {data.get('target_variable', 'unknown')}  |  Total windows: {len(windows)}")
    print()
    print_separator(108)
    print_table_row(headers, col_widths)
    print_separator(108)
    for r in results:
        horizon, ci, diagnosis = _calibration_cells(r)
        print_table_row([f"{r.level}%", horizon, _fmt_pct(r.stated_coverage), _fmt_pct(r.actual_coverage),
                         ci, str(r.n), diagnosis], col_widths)
    print_separator(108)

    print()
    print("  Horizon-wise Wilson screens assume independent coverage hits with a common probability.")
    print("  Distinct origins do not ensure independence; overlapping outcomes or serial dependence need")
    print("  dependence-aware confirmation. Pooled coverage is descriptive only. Level verdicts:")
    for line in _level_verdicts(results):
        print(f"    {line}")
    n_over = len(_flagged(results, "over-confident"))
    n_under = len(_flagged(results, "under-confident"))
    if n_over:
        print(f"  Over-confident screen: {n_over} cell(s) — actual coverage < stated; confirm dependence before recalibrating.")
    if n_under:
        print(f"  Under-confident screen: {n_under} cell(s) — actual coverage > stated; confirm before tightening intervals.")
    print()
    print(f"  Overall calibration score: {_overall_calibration(results):.3f}  "
          "(1.0 = perfect; mean over level-horizon cells with data)")
    print()


# ---------------------------------------------------------------------------
# Subcommand: report
# ---------------------------------------------------------------------------

def cmd_report(args: argparse.Namespace) -> None:
    data, windows, mase_scale = _load_valid(args.input)
    horizons = sorted(set(w["horizon_h"] for w in windows))  # from the data, never the forecast_horizons label
    horizon_metrics = _metrics_or_exit(args.input, windows, mase_scale)
    calibration_results = _compute_calibration(windows)
    has_intervals = any(r.n > 0 for r in calibration_results)

    lines: list[str] = []
    a = lines.append
    a("# Time Series Forecast Evaluation Report")
    a("")
    a(f"**Model:** {data.get('model_name', 'unknown')}  ")
    a(f"**Target variable:** {data.get('target_variable', 'unknown')}  ")
    a(f"**Forecast horizons:** {horizons}  ")
    a(f"**Backtest windows:** {len(windows)}  ")
    if data.get("description"):
        a(f"**Description:** {data['description']}  ")
    a("")
    a("---")
    a("")
    a("## Backtest Metrics by Horizon")
    a("")
    a("| Horizon | N | Origins | MAE | RMSE | MAPE % | MASE | Baseline | Baseline MAE | Skill | Verdict |")
    a("|---------|---|---------|-----|------|--------|------|----------|--------------|-------|---------|")
    for hm in horizon_metrics:
        a(f"| h={hm.horizon_h} | {hm.n} | {hm.n_origins} | {_fmt_number(hm.mae)} | {_fmt_number(hm.rmse)} | "
          f"{_fmt_float(hm.mape, 1)} | {_fmt_float(hm.mase, 2)} | {hm.baseline_name} | "
          f"{_fmt_number(hm.baseline_mae)} | {_fmt_float(hm.skill_score, 3)} | {hm.verdict} |")
    a("")
    a("> **Skill** = 1 - MAE(model) / MAE(baseline) at the same horizon; the baseline is the naive "
      "forecast (value at origin) or the seasonal naive, whichever is stronger. "
      f">= {SKILL_SCORE_GOOD:.2f} = meaningful. A verdict needs >= {MIN_ORIGINS_FOR_VERDICT} distinct "
      "origins, and \"beats baseline\" is a screen: confirm it with a paired test across origins before "
      "promoting. Error that grows with horizon is expected; judge each horizon by its skill, not by its "
      "ratio to h=1.")
    if mase_scale is None:
        a("> MASE is N/A: the input has no `history_values`.")
    for note in _mape_notes(horizon_metrics):
        a(f"> MAPE at {note}.")
    a("")
    warnings = [w for w in (_baseline_warning(hm) for hm in horizon_metrics) if w]
    if warnings:
        a("### Baseline Warnings")
        a("")
        for warning in warnings:
            a(f"- {warning}")
        a("")

    a("---")
    a("")
    a("## Probabilistic Calibration")
    a("")
    if not has_intervals:
        a("No prediction-interval fields in the input; calibration not assessed.")
    else:
        a("Horizon-wise Wilson screens assume independent coverage hits with a common probability. "
          "Distinct origins do not ensure independence: overlapping outcomes or serial dependence need "
          "dependence-aware confirmation. Pooled coverage is descriptive only and has no Wilson interval.")
        a("")
        a("| CI Level | Horizon | Stated Coverage | Actual Coverage | 95% Wilson CI | N | Diagnosis |")
        a("|----------|---------|-----------------|-----------------|---------------|---|-----------|")
        for r in calibration_results:
            horizon, ci, diagnosis = _calibration_cells(r)
            a(f"| {r.level}% | {horizon} | {_fmt_pct(r.stated_coverage)} | {_fmt_pct(r.actual_coverage)} | "
              f"{ci} | {r.n} | {diagnosis} |")
        a("")
        for line in _level_verdicts(calibration_results):
            a(f"- {line}")
        a("")
        a(f"**Overall calibration score:** {_overall_calibration(calibration_results):.3f} "
          "(1.0 = perfect; mean over level-horizon cells)")
    a("")

    n_over = len(_flagged(calibration_results, "over-confident"))
    n_under = len(_flagged(calibration_results, "under-confident"))
    a("---")
    a("")
    a("## Summary and Recommendations")
    a("")
    for hm in horizon_metrics:
        if hm.verdict == "insufficient origins":
            a(f"- h={hm.horizon_h}: insufficient origins ({hm.n_origins}). Add backtest origins until there "
              f"are >= {MIN_ORIGINS_FOR_VERDICT} before judging this horizon.")
        elif hm.verdict != "beats baseline":
            a(f"- h={hm.horizon_h}: {hm.verdict}. Do not ship this horizon on the model; fall back to the "
              f"{hm.baseline_name} forecast or fix features for this horizon.")
    if n_over:
        a(f"- {n_over} over-confident horizon screen(s). Confirm with dependence-aware inference before recalibrating.")
    if n_under:
        a(f"- {n_under} under-confident horizon screen(s). Confirm before tightening intervals.")
    if all(hm.verdict == "beats baseline" for hm in horizon_metrics) and not n_over and not n_under:
        a("- Model beats the baseline at every horizon on point skill and no assessed interval level is "
          "flagged by the independence-assuming screen at any horizon. Confirm with a paired test across origins, against the forecast "
          "currently in use, before promoting.")
    a("")

    report_text = "\n".join(lines)
    if args.output:
        try:
            Path(args.output).write_text(report_text, encoding="utf-8")
        except OSError as exc:
            print(f"Error: cannot write report to {args.output}: {exc.strerror or exc}. "
                  "--output needs a file path (not a directory) in an existing, writable directory.",
                  file=sys.stderr)
            sys.exit(EXIT_INPUT_ERROR)
        print(f"Report written to: {args.output}")
    else:
        print(report_text)


# ---------------------------------------------------------------------------
# CLI wiring
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ts_evaluator",
        description="Time series forecast evaluator — stdlib only. Invalid input exits 2.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="SUBCOMMAND")
    subparsers.required = True

    p_backtest = subparsers.add_parser(
        "backtest",
        help="Per-horizon MAE/RMSE/MAPE/MASE and skill against the naive or seasonal-naive baseline "
             "at the same horizon.",
    )
    p_backtest.add_argument("--input", metavar="JSON_FILE", required=True,
                            help="Backtest results JSON (e.g. data/sample-forecast-results.json).")
    p_backtest.set_defaults(func=cmd_backtest)

    p_cal = subparsers.add_parser(
        "calibration",
        help="Per-horizon coverage of the 50%%, 80%% and 90%% prediction intervals against their "
             "stated levels (95%% Wilson interval).",
    )
    p_cal.add_argument("--input", metavar="JSON_FILE", required=True,
                       help="Backtest results JSON with lower_/upper_ interval fields.")
    p_cal.set_defaults(func=cmd_calibration)

    p_report = subparsers.add_parser("report", help="Full Markdown evaluation report.")
    p_report.add_argument("--input", metavar="JSON_FILE", required=True,
                          help="Backtest results JSON (e.g. data/sample-forecast-results.json).")
    p_report.add_argument("--output", metavar="OUTPUT_FILE",
                          help="Write the Markdown report to this file instead of stdout.")
    p_report.set_defaults(func=cmd_report)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
