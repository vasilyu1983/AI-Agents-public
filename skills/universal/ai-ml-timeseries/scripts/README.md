# ts_evaluator.py

Stdlib-only Python CLI for time series forecast evaluation. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives data scientists and ML engineers fast, reproducible answers to three core evaluation questions:

1. **Backtest** — How accurate is the model at each horizon, and does it beat the naive (or seasonal-naive) baseline at that same horizon?
2. **Calibration** — Do horizon-wise coverage screens flag the prediction intervals (50%, 80%, 90%), under an independence assumption?
3. **Report** — A full Markdown evaluation report combining both analyses with recommendations.

## Quick Start

Run from the `ai-ml-timeseries/` directory:

```bash
# Horizon-wise accuracy: MAE, RMSE, MAPE, MASE, skill vs the baseline at the same horizon
python scripts/ts_evaluator.py backtest --input data/sample-forecast-results.json

# Per-horizon calibration check for 50%, 80%, 90% intervals
python scripts/ts_evaluator.py calibration --input data/sample-forecast-results.json

# Full Markdown evaluation report written to file
python scripts/ts_evaluator.py report --input data/sample-forecast-results.json --output /tmp/ts-eval-report.md
```

## JSON Input Format

The script reads from a rolling-origin backtest results file:

```json
{
  "model_name": "LightGBM-DirectMultiStep",
  "target_variable": "daily_revenue_usd",
  "forecast_horizons": [1, 7, 14, 30],
  "season_length": 7,
  "history_values": [42920, 42630, 43460, 44550, 48010, 49100, 45830, 42370],
  "backtest_windows": [
    {
      "origin_date": "2025-09-01",
      "origin_value": 47830,
      "horizon_h": 1,
      "actual_value": 48320,
      "point_forecast": 47100,
      "lower_50": 44200,
      "upper_50": 50100,
      "lower_80": 41500,
      "upper_80": 53200,
      "lower_90": 39800,
      "upper_90": 55400
    }
  ]
}
```

| Field | Required | Notes |
|---|---|---|
| `model_name` | No | Label for output headers; `unknown` when omitted |
| `target_variable` | No | Label for output headers; `unknown` when omitted |
| `forecast_horizons` | No | Not read; every output lists the horizons found in `backtest_windows` |
| `backtest_windows[].origin_date` | Yes | Non-empty string naming the forecast origin (an ISO date by convention; not parsed). Use the same string for one origin at every horizon: distinct values are counted as distinct origins |
| `season_length` | No | Season length m for the MASE scale (default 1) |
| `history_values` | No | In-sample values before the first origin; enables MASE (scale = mean abs m-step naive error) |
| `backtest_windows[].horizon_h` | Yes | Integer horizon >= 1 (e.g. 1, 7, 14, 30 for days) |
| `backtest_windows[].origin_value` | Yes | Last value observed at the origin; it is the naive forecast for every horizon |
| `backtest_windows[].actual_value` | Yes | Observed outcome at this horizon |
| `backtest_windows[].point_forecast` | Yes | Model's point prediction |
| `backtest_windows[].seasonal_naive_forecast` | No | Seasonal-naive forecast for this target; used as the baseline when it beats naive. Supply it for every row at every horizon or for none; partial coverage exits 2 in `backtest` and `report` (`calibration` does not read it, so it only checks a present value is a finite number) |
| `backtest_windows[].lower_50` … `upper_90` | For `calibration` | Interval bounds; both ends per level, lower <= upper, wider levels contain narrower ones. Each supplied level must cover every row; partial levels exit 2 |

Every input number must be finite with magnitude <= 1e150; rescale larger series (for example to thousands). A metric can still overflow through a near-zero denominator (history_values that barely vary, or a near-exact baseline); every computed metric is checked, and one that is not finite exits 2 naming the metric, so no printed metric is `inf`. `N/A` marks a metric that does not apply. Invalid input (missing, non-numeric or out-of-range field, duplicate origin/horizon row, inverted or crossing interval, no interval fields for `calibration`) exits 2 and names the offending row; a missing, unreadable, non-UTF-8 or non-JSON input file also exits 2 and names the file. No metric is printed from partial input. `report --output` exits 2 when the path is a directory or cannot be written.

## Metrics Reference

### Point Accuracy (backtest subcommand)

| Metric | Formula | Notes |
|---|---|---|
| MAE | mean(|actual - forecast|) | Scale-dependent; comparable across horizons |
| RMSE | sqrt(mean((actual - forecast)²)) | Penalizes large errors more than MAE |
| MAPE % | mean(|actual - forecast| / |actual|) × 100 | Rows whose actual is 0, or so close to 0 that the ratio overflows, are left out and counted in a `MAPE: … excludes k of n row(s)` note; N/A when every row is left out. Avoid MAPE when actuals can be near zero |
| MASE | MAE / in-sample MAE of the m-step naive | Scale-free; needs `history_values` |
| Baseline MAE | MAE of the naive forecast (`origin_value`), or of the seasonal naive when lower | Computed at the same horizon |
| Skill Score | 1 - MAE(model) / MAE(baseline) | >= 0.10 beats baseline; 0 to 0.10 marginal; < 0 worse; N/A when the baseline MAE is 0 |

### Calibration (calibration subcommand)

Coverage is scored separately at each horizon, where each row is one origin. The stated level is compared with a 95% Wilson score interval (z = 1.96), assuming independent coverage hits with a common probability. Distinct origins do not establish independence; serial dependence requires block- or series-aware confirmation before promotion. Pooled coverage is descriptive only and has no confidence interval or inferential verdict. Multiple horizon/level screens can produce chance flags, so confirm decision-critical findings before adjusting intervals.

| Diagnosis | Meaning | Action |
|---|---|---|
| consistent with nominal (n=…) | Stated level lies inside the Wilson interval | Screen did not reject under its assumptions; not proof of calibration |
| over-confident | Stated level above the interval (intervals too narrow) | Confirm with dependence-aware evidence before recalibrating |
| under-confident | Stated level below the interval (intervals too wide) | Confirm with dependence-aware evidence before tightening |

### Horizon Verdicts

Each horizon is judged by its skill against the baseline at the same horizon. Error that grows with horizon is expected (a random walk's naive error grows roughly with the square root of h), so the ratio MAE(h) / MAE(h=1) is not a defect signal on its own.

| Verdict | Rule |
|---|---|
| insufficient origins | Fewer than 6 distinct `origin_date` values at this horizon. Below 6, a model that wins at every origin still fails a two-sided 5% sign test, so no verdict is given |
| beats baseline | Skill >= 0.10. This is a screen, not a promotion decision: confirm it with a paired test across origins (see the skill's Forecast Decision Gate) |
| marginal | 0 <= skill < 0.10 |
| worse than baseline | Skill < 0, or the baseline has zero error while the model does not |
| undefined | Both the baseline and the model have zero error |

A baseline with zero error raises a warning that names the baseline and its field (`origin_value` or `seasonal_naive_forecast`), because an exact baseline usually means the field was copied from `actual_value`.

## Subcommand Reference

```bash
python scripts/ts_evaluator.py backtest     --help
python scripts/ts_evaluator.py calibration  --help
python scripts/ts_evaluator.py report       --help
```
