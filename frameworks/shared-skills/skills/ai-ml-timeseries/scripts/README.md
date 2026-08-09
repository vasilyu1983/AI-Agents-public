# ts_evaluator.py

Stdlib-only Python CLI for time series forecast evaluation. No external dependencies — runs with any Python 3.9+ installation.

## Purpose

Gives data scientists and ML engineers fast, reproducible answers to three core evaluation questions:

1. **Backtest** — How accurate is the model at each horizon? Does it beat naive? Does error degrade faster than expected?
2. **Calibration** — Are the prediction intervals actually achieving stated coverage (50%, 80%, 90%)?
3. **Report** — A full Markdown evaluation report combining both analyses with recommendations.

## Quick Start

Run from the `ai-ml-timeseries/` directory:

```bash
# Horizon-wise accuracy: MAE, RMSE, MAPE, skill score vs naive
python scripts/ts_evaluator.py backtest --input data/sample-forecast-results.json

# Probabilistic calibration check for 50%, 80%, 90% intervals
python scripts/ts_evaluator.py calibration --input data/sample-forecast-results.json

# Full Markdown evaluation report written to file
python scripts/ts_evaluator.py report --input data/sample-forecast-results.json --output /tmp/ts-eval-report.md
```

## JSON Input Format

The script reads from a rolling-origin backtest results file. Required fields:

```json
{
  "model_name": "LightGBM-DirectMultiStep",
  "target_variable": "daily_revenue_usd",
  "forecast_horizons": [1, 7, 14, 30],
  "backtest_windows": [
    {
      "origin_date": "2025-09-01",
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
| `model_name` | Yes | Label for output headers |
| `target_variable` | Yes | Label for output headers |
| `forecast_horizons` | No | Informational; derived from windows if omitted |
| `backtest_windows[].origin_date` | Yes | ISO date string for the backtest origin |
| `backtest_windows[].horizon_h` | Yes | Integer horizon (e.g. 1, 7, 14, 30 for days) |
| `backtest_windows[].actual_value` | Yes | Observed outcome at this horizon |
| `backtest_windows[].point_forecast` | Yes | Model's point prediction |
| `backtest_windows[].lower_50`, `upper_50` | Yes | 50% prediction interval bounds |
| `backtest_windows[].lower_80`, `upper_80` | Yes | 80% prediction interval bounds |
| `backtest_windows[].lower_90`, `upper_90` | Yes | 90% prediction interval bounds |

## Metrics Reference

### Point Accuracy (backtest subcommand)

| Metric | Formula | Notes |
|---|---|---|
| MAE | mean(|actual - forecast|) | Scale-dependent; comparable across horizons |
| RMSE | sqrt(mean((actual - forecast)²)) | Penalizes large errors more than MAE |
| MAPE % | mean(|actual - forecast| / |actual|) × 100 | Avoid when actuals can be near zero |
| Naive MAE | MAE of "predict last known value" baseline | Benchmark for skill score |
| Skill Score | 1 - MAE(model) / MAE(naive) | > 0 = beats naive; > 0.10 = meaningful |

### Calibration (calibration subcommand)

| Diagnosis | Meaning | Action |
|---|---|---|
| good | Actual coverage within 5 pp of stated level | No action needed |
| over-confident | Actual coverage < stated level (intervals too narrow) | Widen intervals via conformal recalibration |
| under-confident | Actual coverage > stated level (intervals too wide) | Tighten intervals to improve sharpness |

### Horizon Degradation Flag

A horizon is flagged if MAE(h) / MAE(h=1) exceeds 1.5. This catches models where error grows unreasonably fast with horizon distance — a sign of missing horizon-specific features or an inappropriate multi-step strategy.

## Subcommand Reference

```bash
python scripts/ts_evaluator.py backtest     --help
python scripts/ts_evaluator.py calibration  --help
python scripts/ts_evaluator.py report       --help
```
