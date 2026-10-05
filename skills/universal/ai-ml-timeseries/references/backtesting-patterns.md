# Backtesting Patterns for Forecasting

Reliable, repeatable validation frameworks for forecasting systems.

## Table of Contents

- [Non-Negotiable Rules](#non-negotiable-rules)
- [Valid Backtest Structures](#valid-backtest-structures)
- [Pattern 1: Final Holdout](#pattern-1-final-holdout)
- [Pattern 2: Rolling-Origin Backtest](#pattern-2-rolling-origin-backtest)
- [Pattern 3: Rolling Window](#pattern-3-rolling-window)
- [Pattern 4: Panel-Aware Backtest](#pattern-4-panel-aware-backtest)
- [Horizon-Wise Evaluation](#horizon-wise-evaluation)
- [Paired Promotion Test](#paired-promotion-test)
- [Metric Defaults](#metric-defaults)
- [Point Forecast Metrics](#point-forecast-metrics)
- [Probabilistic Metrics](#probabilistic-metrics)
- [Business Metrics](#business-metrics)
- [Execution Workflow](#execution-workflow)
- [Common Failure Modes](#common-failure-modes)
- [Backtesting Checklist](#backtesting-checklist)

## Non-Negotiable Rules

- Never use random IID splits for forecasting.
- Freeze the prediction cutoff, horizon, and covariate availability rules before backtesting.
- Compare every candidate against simple baselines under the same windows.
- Report performance by horizon and key slices, not only one global number.

## Valid Backtest Structures

### Pattern 1: Final Holdout

Use when:

- the dataset is small
- you need one simple go/no-go check after feature and model choices are mostly fixed

Structure:

- train on early history
- hold out the final contiguous forecast window
- use only for a final sanity check, not as the only model-selection procedure

### Pattern 2: Rolling-Origin Backtest

Use when:

- model selection or tuning depends on realistic repeated forecasts
- the deployment pattern scores on a repeated cadence

Example:

- train: `t0 -> t100`
- validate: `t101 -> t114`
- train: `t0 -> t114`
- validate: `t115 -> t128`

This is the default pattern for most forecasting work.

### Pattern 3: Rolling Window

Use when:

- regime drift makes very old history less relevant
- you want a fixed training window size

Example:

- train: `t0 -> t100`, validate `t101 -> t114`
- train: `t14 -> t114`, validate `t115 -> t128`

### Pattern 4: Panel-Aware Backtest

Use when:

- many related series are trained together
- global/panel models share parameters across `series_id`

Rules:

- split by time first, not by rows
- keep all series aligned to the same cutoff schedule where possible
- report both global metrics and per-segment/per-series-band metrics

## Horizon-Wise Evaluation

For forecast horizon `H`:

- compute metrics separately for each horizon step
- inspect degradation as horizon grows
- summarize worst horizons, not only average accuracy

Minimum outputs:

- horizon-by-horizon table
- aggregate summary across all windows
- slice analysis for important cohorts

## Paired Promotion Test

Load this when deciding whether a candidate replaces the forecast in use, or before stating that it "beats" a baseline. A lower mean error over a handful of correlated windows is not evidence on its own.

- **Bar.** Compare against the forecast currently driving decisions, including planner overrides, on the same origins. Naive and seasonal naive are only the floor. If overrides are not logged as their own forecast, start logging them; their value cannot be measured otherwise.
- **Differential.** At each decision horizon h, compute the per-origin loss differential d_t = L(incumbent) - L(candidate) under the business loss.
- **Test.** Test whether mean d is 0. The default is the Diebold-Mariano test (Diebold & Mariano, 1995) with the Harvey-Leybourne-Newbold small-sample correction (Harvey, Leybourne & Newbold, 1997). Multiply the DM statistic by sqrt((n + 1 - 2h + h(h - 1)/n) / n) and compare the result with Student t on n - 1 degrees of freedom.
  - h-step errors from overlapping windows are autocorrelated up to lag h - 1, so the variance of mean d must include those autocovariances.
  - Deviation: when losses are heavy-tailed or n is small, use a moving-block bootstrap that resamples origins in blocks at least h long.
- **Decision.** Promote at a horizon only when the interval for mean d excludes 0 and the gain clears the materiality bar (the bundled evaluator uses skill >= 0.10). Test each decision horizon separately; a win at h=1 does not license h=30.
- **Few origins.** The test has little power with few origins. The bundled evaluator gives no verdict below 6 origins, but passing that floor is not passing the test. Add origins rather than relax the test.

## Metric Defaults

### Point Forecast Metrics

Default to:

- MAE
- WAPE
- MASE

Use optionally:

- RMSE when large misses deserve extra penalty
- sMAPE only if stakeholders already understand it

Avoid making MAPE a default, especially when actuals can be zero or near zero.

### Probabilistic Metrics

- Pinball loss for quantiles
- CRPS or interval score for distributions/intervals
- Coverage and mean interval width for calibration quality

### Business Metrics

- stockout cost
- overforecast cost
- service-level miss rate
- waste or holding-cost proxies

## Execution Workflow

1. Freeze cutoff timestamp policy and forecast horizon.
2. Choose expanding, rolling-origin, or rolling window scheme.
3. Define covariates available at each cutoff.
4. Train and predict for each window.
5. Record predictions, actuals, window metadata, and model version.
6. Aggregate metrics by horizon, slice, and business objective.
7. Compare against naive and seasonal-naive baselines.
8. Document failure cases, not only mean performance.

## Backtest Design Traps That Look Correct But Aren't

These are the traps that pass a superficial "is this rolling-origin?" check but still produce misleading numbers:

- **Retraining cadence mismatch.** A backtest that retrains the model every window looks rigorous but is often unaffordable in production, where retraining might realistically happen weekly or monthly. If the deployed system will not retrain as often as the backtest does, the backtest overstates achievable accuracy. Match the backtest's retrain cadence to the deployment's actual retrain cadence, or report both.
- **Calendar leakage through repeated structure, not timestamps.** Rolling-origin windows preserve time order, but if every window happens to land on the same day-of-week or the same point in a promotional cycle, the backtest can look artificially stable — it never tests the model against the specific calendar edge cases (leap day, a holiday that moves, a fiscal-year boundary) that will eventually occur in production. Deliberately include at least one window that spans an unusual calendar event.
- **Covariate availability drift between backtest and production.** A backtest that pulls "known-future" covariates from a table with today's (fully updated, corrected) values is not testing what will actually be available at each historical cutoff — e.g. promo calendars are sometimes finalized late, or weather/economic indicators get revised after the fact. If the covariate source is revised historically, the backtest is leaking a cleaner version of the future than production will ever have. Snapshot covariates as-of each cutoff, or explicitly document the leakage risk if that isn't feasible.
- **Global/panel backtests that hide per-series collapse.** A shared model's aggregate MASE can look flat across windows while a meaningful subset of series (new SKUs, discontinued items, low-volume tail) silently degrades every window. Track a per-series or per-band trend across backtest windows, not just the aggregate trend.
- **Treating one strong backtest run as proof of stability.** Rolling-origin windows are correlated with each other (they share most of their training data), so their apparent variance understates true model risk. Look for windows with sharply worse performance rather than only the mean; a few bad windows out of many is often the more decision-relevant signal than the average.
- **Reconciliation and calibration checks scoped only to the final window.** For hierarchical or probabilistic models, running the coherence or calibration check once at the end (rather than per backtest window) can miss that reconciliation quality or interval coverage degrades in specific regimes (e.g., post-promotion weeks, low-volume periods). Re-run these checks per window, not just once.

## Common Failure Modes

| Failure | Why It Breaks Backtests | Fix |
|--------|--------------------------|-----|
| Random CV or K-fold | Leaks future information into training | Use rolling-origin or expanding windows |
| Backtest rows not tied to cutoff timestamps | Feature leakage becomes invisible | Store cutoff timestamp per prediction |
| Evaluating only one final holdout | High variance, weak model selection | Use repeated windows |
| Reporting one aggregate metric | Hides horizon or segment failures | Report horizon and slice breakdowns |
| Scoring rich model without baselines | False confidence | Keep naive and seasonal-naive in every run |

## Backtesting Checklist

- [ ] Temporal ordering preserved
- [ ] Cutoff timestamp defined explicitly
- [ ] Enough windows to measure stability
- [ ] Baselines included in every comparison
- [ ] Horizon-wise metrics reported
- [ ] Slice-level analysis included
- [ ] Business metrics aligned to the decision
- [ ] Covariate availability rules documented
