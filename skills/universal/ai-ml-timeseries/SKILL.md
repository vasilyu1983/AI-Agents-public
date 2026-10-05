---
name: ai-ml-timeseries
description: "Builds and backtests demand and revenue forecasts: rolling-origin backtests, prediction intervals, reconciliation, zero-shot foundation models. Use when forecasting time series."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-26
---

# Time Series Forecasting - Production Patterns

Define the prediction cutoff before modelling: only information available then can enter features or baselines. Compare models on the decision horizon against the forecast currently driving decisions.

## Scope Boundaries

- **General EDA, tabular modelling, experiment design, or reusable DS workflow** -> [ai-ml-data-science](../ai-ml-data-science/SKILL.md)
- **Deployment architecture, monitoring stack, release gates, incident playbooks** -> [ai-mlops](../ai-mlops/SKILL.md)
- **Generic LLM lifecycle, prompting, or provider selection** -> [ai-llm](../ai-llm/SKILL.md)
- **RAG and search systems** -> [ai-rag](../ai-rag/SKILL.md)

## Workflow

1. Define the forecast target, horizon, cutoff timestamp, granularity, and business-loss shape first.
2. Route generic DS workflow or full production-ops work to the adjacent skill when forecasting depth is not the main need.
3. Choose the baseline, feature pattern, and model family from the decision tree.
4. Run leakage-safe backtests, compare horizon-aware metrics, and add interval or calibration checks when decisions need uncertainty.
5. Before selecting a package or checkpoint, open its official docs from [data/sources.json](data/sources.json) and check the installed API, supported covariates, context/horizon limits and weight licence. For TSFM comparisons, load [model roles and lookup steps](references/ts-llm-patterns.md#practical-model-roles); record the benchmark snapshot next to any quoted rank. For MAPIE code, load [probabilistic patterns](references/probabilistic-forecasting.md) and compare the example to the installed release's docs.

## Quick Reference

### Choose The Forecasting Pattern

```text
Need to build or review a forecast:
    ├─ One series or a small local portfolio?
    │   ├─ Few covariates, interpretability first -> naive/seasonal naive + ETS/SARIMAX baseline
    │   └─ Nonlinear effects or richer covariates -> feature-based boosting
    │
    ├─ Many related series?
    │   ├─ Need one shared model with covariates -> global/panel forecasting
    │   └─ Need rollups to add up across levels -> hierarchical forecasting + reconciliation
    │
    ├─ Intermittent or zero-heavy demand?
    │   ├─ Very sparse and operationally simple -> Croston/SBA/ADIDA baseline
    │   └─ Need richer covariates or scale -> global boosting with zero-aware features
    │
    ├─ Need uncertainty, service levels, or inventory decisions?
    │   └─ Add quantiles, conformal intervals, or distributional forecasts
    │
    ├─ Long horizon or low-feature setup?
    │   ├─ Need strong zero-shot baseline -> TS foundation models
    │   └─ Need supervised optimization on many series -> global/deep forecasting
    │
    └─ Need production handoff?
        └─ Record cutoff timestamp, feature contract, fallback, lineage, and retraining trigger
```

## Core Principles

### 1. Cutoff Timestamp Before Features

- Define the exact prediction timestamp before building labels or features.
- Every lag, rolling aggregate, calendar flag, and external signal must be justified relative to what is known at that cutoff.
- Known-future covariates and future-unknown covariates must be treated differently.

### 2. Baselines First

- Always compare against naive and seasonal-naive baselines, scored at the same horizon from the value known at each origin; a baseline built from any later actual leaks the future.
- Add ETS/SARIMAX or other local classical baselines when interpretability matters.
- Candidate models do not earn deployment if they barely beat a simple baseline.
- Naive and seasonal naive are the floor. The promotion bar is the forecast currently driving decisions, planner overrides included, scored on the same origins. Log overrides as a separate forecast so their value can be measured too.
- A point-skill win is a screen, not a promotion. Promote only when a paired test on per-origin loss differentials at the decision horizon excludes zero ([paired promotion test](references/backtesting-patterns.md#paired-promotion-test)).

### 3. Horizon And Slice Evaluation

- Report accuracy by horizon, not only a single global score.
- Slice by segment, geography, SKU family, volume band, or any business-relevant cohort.
- Prefer MASE/WAPE/MAE over MAPE when zeros or near-zeros exist, except on intermittent series.
- When more than half the periods are zero, MAE, WAPE and MASE reward an all-zero forecast (they are minimised by the median). Select mean forecasts on RMSSE and stocking decisions on pinball loss; never on MAE or WAPE alone ([intermittent metrics](references/intermittent-demand-patterns.md#standard-metrics-often-mislead)).
- Judge each horizon by skill against the baseline at that horizon. Error that grows with horizon is expected and is not a defect on its own.

### 4. Global/Panel Before Per-Series Complexity

- When many related series exist, default to a shared global/panel approach before building separate bespoke models.
- Use hierarchical reconciliation when forecasts must remain coherent across levels.
- Promote complexity only when it earns accuracy, calibration, or operational simplicity.

### 5. Probabilistic When The Decision Is Risk-Sensitive

- Use quantiles, conformal intervals, or full predictive distributions when downstream actions depend on uncertainty.
- Evaluate both coverage and sharpness; wide intervals with nominal coverage are not automatically useful.
- Screen coverage at each horizon with a Wilson interval only under independent coverage hits with a common probability; distinct origins alone do not establish independence. Dependent residuals need block- or series-aware evidence before promotion. Keep pooled coverage descriptive and inspect clustered misses ([coverage against noise](references/probabilistic-forecasting.md#coverage-against-sampling-noise)).
- Set the decision quantile from costs, q* = c_u / (c_u + c_o), and score it with pinball loss and per-horizon coverage ([decision quantile](references/probabilistic-forecasting.md#decision-quantile-from-costs)).
- Reassess calibration after every retrain or major model change.

### 6. Forecasting-Specific Handoff

- A forecast package is incomplete without cutoff timestamps, horizon definition, feature contract, metric definitions, fallback rules, and lineage metadata.
- Keep forecasting-specific handoff guidance here; route full deployment architecture to [ai-mlops](../ai-mlops/SKILL.md).

## Forecast Decision Gate

Create a cutoff ledger for every backtest fold: training end, forecast origin, horizon, feature availability, retrain policy, and any revision or publication lag. Report error and interval quality by horizon and decision-critical slice before aggregating. Promote a forecast only when it beats the forecast currently in use (planner overrides included) on the business-weighted loss, and a paired test across origins confirms the gain, without hiding a blocking slice. The fallback for missing or late covariates must also be tested. Beating the naive or seasonal-naive floor is necessary but never sufficient.

## Known Traps

- Mixing future-known covariates and future-unknown covariates in the same feature path without documenting which values are actually available at forecast time.
- Using one global backtest score to justify deployment when horizon-specific error behavior differs materially.
- Using MAPE on zero-heavy, intermittent, or near-zero series and then comparing models on unstable percentages.
- Building bespoke per-series models before testing a strong global or panel baseline on related series.
- Ignoring hierarchy and coherence when downstream consumers expect rollups to add up.

## Common Anti-Patterns

- Reusing IID validation habits from generic tabular ML instead of rolling-origin or expanding-window evaluation.
- Treating decomposition visuals as evidence of production signal without backtesting the actual decision horizon.
- Using feature-rich models whose future covariates are unavailable or operationally too expensive to maintain.
- Comparing TS foundation models to weak baselines and calling the result strategic proof.
- Trusting a TSFM zero-shot win before reading the checkpoint's weight licence and re-testing on private or post-cutoff data ([TSFM trust gate](references/ts-llm-patterns.md#tsfm-trust-gate)).

## Navigation: Core References

### Data Integrity And Features

- **[TS EDA Best Practices](references/ts-eda-best-practices.md)** - Timestamp integrity, missingness, decomposition, and stability checks
- **[Lag & Rolling Patterns](references/lag-rolling-patterns.md)** - Leakage-safe lags, rolling windows, and calendar patterns
- **[Global & Panel Forecasting Patterns](references/global-panel-forecasting-patterns.md)** - Shared models, panel schemas, known-future covariates, grouped evaluation

### Model And Strategy Selection

- **[Model Selection Guide](references/model-selection-guide.md)** - Model-family decision matrix
- **[LightGBM TS Patterns](references/lightgbm-ts-patterns.md)** - Feature-based/global boosting patterns, MLForecast/skforecast workflows
- **[Multi-Step Forecasting Patterns](references/multistep-forecasting-patterns.md)** - Direct, recursive, and seq2seq tradeoffs
- **[Intermittent Demand Patterns](references/intermittent-demand-patterns.md)** - Sparse-demand baselines and zero-aware modelling

### Validation, Uncertainty, And Advanced Forecasting

- **[Backtesting Patterns](references/backtesting-patterns.md)** - Rolling-origin evaluation, panel-aware backtests, and metric design
- **[Probabilistic Forecasting](references/probabilistic-forecasting.md)** - Quantiles, conformal methods, calibration, and scoring rules
- **[Hierarchical Forecasting](references/hierarchical-forecasting.md)** - Coherent forecasts and reconciliation methods
- **[Time-Series Foundation Model Patterns](references/ts-llm-patterns.md)** - TSFM roles, trust gate (licence, contamination), zero-shot benchmarking
- **[Anomaly Detection Patterns](references/anomaly-detection-patterns.md)** - Residual and interval-based anomaly workflows

### Handoff And Forecast Operations

- **[Forecast Governance Patterns](references/forecast-governance-patterns.md)** - Cutoff timestamps, lineage, fallback rules, and forecast contracts
- **[Production Forecast Operations](references/production-deployment-patterns.md)** - Horizon-matched live monitoring against the backtest, actuals latency, forecast of record, fallback ladder

## Templates

### Data Preparation

- **[TS EDA Template](assets/timeseries/template-ts-eda.md)** - Reproducible structure for timestamp and seasonality review
- **[Resample & Fill Template](assets/timeseries/template-resample-fill.md)** - Resampling, gap rules, and fill policies

### Feature And Model Design

- **[Lag & Rolling Features](assets/timeseries/template-lag-rolling.md)** - Leakage-safe feature specification
- **[Calendar Features](assets/timeseries/template-calendar-features.md)** - Known-future business calendar and event feature spec
- **[Forecast Model Template](assets/timeseries/template-forecast-model.md)** - Forecast package contract for local, global, or hierarchical models
- **[Multi-Step Strategy](assets/timeseries/template-multistep-strategy.md)** - Direct, recursive, and seq2seq strategy contract

### Evaluation And Uncertainty

- **[Backtest Template](assets/timeseries/template-backtest.md)** - Rolling-origin or expanding-window evaluation spec
- **[TS Metrics Template](assets/timeseries/template-ts-metrics.md)** - Horizon, slice, business-loss, and probabilistic metric contract

### Foundation Models

- **[TS Foundation Model Template](assets/timeseries/template-ts-llm.md)** - Zero-shot TSFM benchmark and evaluation scaffold

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/ts_evaluator.py](scripts/ts_evaluator.py) | Stdlib-only CLI: horizon-wise metrics and skill vs naive/seasonal-naive from `origin_value` (no verdict below 6 origins), independence-assuming per-horizon Wilson screens, descriptive pooled coverage, Markdown report. Exits 2 on invalid input, partially supplied interval levels or an unwritable `--output`. Its "beats baseline" is a screen; run the paired test before promoting |

```bash
# Horizon-wise accuracy: MAE, RMSE, MAPE, MASE, skill vs the baseline at the same horizon (invalid input exits 2)
python scripts/ts_evaluator.py backtest --input data/sample-forecast-results.json

# Per-horizon calibration screen for 50%, 80%, 90% prediction intervals; pooled coverage is descriptive
python scripts/ts_evaluator.py calibration --input data/sample-forecast-results.json

# Full Markdown evaluation report written to file
python scripts/ts_evaluator.py report --input data/sample-forecast-results.json --output /tmp/ts-eval-report.md
```

## Data Files

| File | Description |
|------|-------------|
| [data/sources.json](data/sources.json) | Curated primary sources for classical forecasting, MLForecast, skforecast, AutoGluon, TSFM repositories, fev-bench, and MAPIE |
| [data/sample-forecast-results.json](data/sample-forecast-results.json) | Synthetic rolling-origin backtest for a daily revenue forecast: horizons 1, 7, 14, 30 days, 48 rows, 12 origins, with `origin_value` and in-sample history for MASE |

## External Sources

See **[data/sources.json](data/sources.json)** for current primary sources across:

- classical forecasting references
- official docs for MLForecast, HierarchicalForecast, skforecast, AutoGluon TimeSeries, LightGBM, and MAPIE
- official TSFM repositories and model cards
- fev-bench benchmark and governance references used for high-impact deployments

## Related Skills

- **[ai-ml-data-science](../ai-ml-data-science/SKILL.md)** - General DS workflows, experiment design, and broader modelling patterns
- **[ai-mlops](../ai-mlops/SKILL.md)** - Deployment architecture, monitoring, and release operations
- **[ai-llm](../ai-llm/SKILL.md)** - Provider/model lifecycle questions outside time-series forecasting
- **[data-sql-optimization](../data-sql-optimization/SKILL.md)** - Storage and query design for time-series marts

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
