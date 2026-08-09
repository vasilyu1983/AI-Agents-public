---
name: ai-ml-timeseries
description: "Time-series forecasting with temporal validation, panel models, probabilistic forecasts, and TS foundation models. Use when modeling ordered observations."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Time Series Forecasting - Production Patterns

**Scope note:** This skill covers forecasting system construction and evaluation. It is not part of the LLM-build or LLM-training stack — route LLM lifecycle, prompting, or provider questions to [ai-llm](../ai-llm/SKILL.md).

**July 2026 posture:** define a cutoff timestamp before modelling, start with strong baselines, prefer horizon-aware validation over IID thinking, treat known-future covariates explicitly, and verify fast-moving tooling against current official docs before recommending it.

This skill is the implementation guide for **forecasting systems**:

- timestamp integrity, frequency checks, and point-in-time feature design
- local, global/panel, and hierarchical forecasting workflows
- leakage-safe backtesting, horizon-wise evaluation, and business-loss alignment
- probabilistic forecasting, calibration, and interval quality
- time-series foundation models (TSFMs) and zero-shot benchmark patterns
- forecasting-specific handoff, fallback, and lineage requirements

Use this skill for **forecasting depth**. Use sibling skills for general data science, generic LLM strategy, or full production operations.

## When To Use This Skill

Activate this skill when the user asks for:

- building or reviewing a forecast model
- choosing between local, global/panel, hierarchical, or foundation-model approaches
- creating lag, rolling, calendar, or known-future covariate features
- designing a rolling-origin backtest or fixing temporal leakage
- selecting forecasting metrics by horizon, segment, or business cost
- adding prediction intervals, quantiles, or conformal calibration
- comparing Chronos-2, Chronos-Bolt, Toto, TimesFM, AutoGluon TimeSeries, MLForecast, skforecast, or classical baselines
- defining forecast-specific fallback, lineage, and handoff requirements

## Scope Boundaries

- **General EDA, tabular modelling, experiment design, or reusable DS workflow** -> [ai-ml-data-science](../ai-ml-data-science/SKILL.md)
- **Deployment architecture, monitoring stack, release gates, incident playbooks** -> [ai-mlops](../ai-mlops/SKILL.md)
- **Generic LLM lifecycle, prompting, or provider selection** -> [ai-llm](../ai-llm/SKILL.md)
- **RAG and search systems** -> [ai-rag](../ai-rag/SKILL.md)

Keep this skill focused on **forecast creation, validation, and forecasting-specific operational patterns**.

## ASCII Flow

```text
forecast need
  |
  v
forecast contract
  target + horizon + cutoff + granularity + business loss + update cadence
  |
  v
time-series validation
  timestamp integrity + leakage checks + rolling-origin backtest
  |
  v
model pattern
  naive baseline -> local/classical -> feature ML -> global/panel -> TS foundation
  |
  v
forecast handoff
  point/interval forecasts + lineage + fallback + monitoring trigger
```

## Quick Reference

| Task | Default Tooling / Pattern | When To Use |
|------|---------------------------|-------------|
| Timestamp integrity | pandas, Polars, statsmodels | Frequency checks, missing timestamps, DST/timezone cleanup |
| Feature-based forecasting | LightGBM/XGBoost + MLForecast or skforecast | Covariate-rich, interpretable, scalable forecasts |
| Classical local baseline | naive, seasonal naive, ETS/SARIMAX | Small data, interpretable baseline, low-covariate settings |
| Global/panel forecasting | MLForecast, AutoGluon TimeSeries, NeuralForecast | Many related series, shared signal, unified training |
| Hierarchical coherence | HierarchicalForecast | Need forecasts that add up across levels |
| Probabilistic forecasts | quantile regression, conformal, distributional models | Risk-sensitive decisions, service-level planning |
| TS foundation models | Chronos-2 / Chronos-Bolt (Amazon), Toto (Datadog), TimesFM, AutoGluon TSFM support | Zero-shot baselines, long horizons, sparse feature engineering; verify current releases |
| Backtesting | rolling-origin / expanding windows | Forecast validation without leakage |
| Forecast handoff | cutoff timestamp + lineage + fallback | Production-ready forecast packages |

## Workflow

1. Define the forecast target, horizon, cutoff timestamp, granularity, and business-loss shape first.
2. Route generic DS workflow or full production-ops work to the adjacent skill when forecasting depth is not the main need.
3. Choose the baseline, feature pattern, and model family from the decision tree.
4. Run leakage-safe backtests, compare horizon-aware metrics, and add interval or calibration checks when decisions need uncertainty.
5. Verify fast-moving tooling and TSFM claims with the navigation and fact-checking sources before final recommendations.

## Current-Facts Protocol For Current-Best-Tooling Recommendations

Use this protocol whenever the user asks for the **best**, **latest**, **current**, or **still relevant** forecasting tooling — TSFM releases, benchmark leaderboards, and package APIs move on a roughly quarterly cadence, so treat any specific version number or benchmark figure below as provisional pending a live check:

1. Start from [data/sources.json](data/sources.json).
2. Verify fast-moving facts with official docs or official repositories.
3. Separate **stable guidance** from **volatile facts** such as current model capabilities, package APIs, or hosted deployment options.
4. Recommend a default plus 1-2 alternatives, with tradeoffs by horizon, covariates, scale, and operational cost.

Use this protocol for questions such as:

- "Should I use MLForecast, skforecast, or AutoGluon TimeSeries?"
- "Should I use Chronos-2, Chronos-Bolt, or Toto as my zero-shot baseline?"
- "What is the current MAPIE API for time-series conformal intervals?"
- "Should I still be using Prophet or TBATS here?"

## Decision Tree: Choose The Forecasting Pattern

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

- Always compare against naive and seasonal-naive baselines.
- Add ETS/SARIMAX or other local classical baselines when interpretability matters.
- Candidate models do not earn deployment if they barely beat a simple baseline.

### 3. Horizon And Slice Evaluation

- Report accuracy by horizon, not only a single global score.
- Slice by segment, geography, SKU family, volume band, or any business-relevant cohort.
- Prefer MASE/WAPE/MAE over MAPE when zeros or near-zeros exist.

### 4. Global/Panel Before Per-Series Complexity

- When many related series exist, default to a shared global/panel approach before building separate bespoke models.
- Use hierarchical reconciliation when forecasts must remain coherent across levels.
- Promote complexity only when it earns accuracy, calibration, or operational simplicity.

### 5. Probabilistic When The Decision Is Risk-Sensitive

- Use quantiles, conformal intervals, or full predictive distributions when downstream actions depend on uncertainty.
- Evaluate both coverage and sharpness; wide intervals with nominal coverage are not automatically useful.
- Reassess calibration after every retrain or major model change.

### 6. Forecasting-Specific Handoff

- A forecast package is incomplete without cutoff timestamps, horizon definition, feature contract, metric definitions, fallback rules, and lineage metadata.
- Keep forecasting-specific handoff guidance here; route full deployment architecture to [ai-mlops](../ai-mlops/SKILL.md).

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

## Navigation: Core References

### Data Integrity And Features

- **[TS EDA Best Practices](references/ts-eda-best-practices.md)** - Timestamp integrity, missingness, decomposition, and stability checks
- **[Lag & Rolling Patterns](references/lag-rolling-patterns.md)** - Leakage-safe lags, rolling windows, and calendar patterns
- **[Global & Panel Forecasting Patterns](references/global-panel-forecasting-patterns.md)** - Shared models, panel schemas, known-future covariates, grouped evaluation

### Model And Strategy Selection

- **[Model Selection Guide](references/model-selection-guide.md)** - May 2026 model-family decision matrix
- **[LightGBM TS Patterns](references/lightgbm-ts-patterns.md)** - Feature-based/global boosting patterns, MLForecast/skforecast workflows
- **[Multi-Step Forecasting Patterns](references/multistep-forecasting-patterns.md)** - Direct, recursive, and seq2seq tradeoffs
- **[Intermittent Demand Patterns](references/intermittent-demand-patterns.md)** - Sparse-demand baselines and zero-aware modelling

### Validation, Uncertainty, And Advanced Forecasting

- **[Backtesting Patterns](references/backtesting-patterns.md)** - Rolling-origin evaluation, panel-aware backtests, and metric design
- **[Probabilistic Forecasting](references/probabilistic-forecasting.md)** - Quantiles, conformal methods, calibration, and scoring rules
- **[Hierarchical Forecasting](references/hierarchical-forecasting.md)** - Coherent forecasts and reconciliation methods
- **[Time-Series Foundation Model Patterns](references/ts-llm-patterns.md)** - Chronos, TimesFM, zero-shot baselines, and TSFM usage
- **[Anomaly Detection Patterns](references/anomaly-detection-patterns.md)** - Residual and interval-based anomaly workflows

### Handoff And Forecast Operations

- **[Forecast Governance Patterns](references/forecast-governance-patterns.md)** - Cutoff timestamps, lineage, fallback rules, and forecast contracts
- **[Production Deployment Patterns](references/production-deployment-patterns.md)** - Broader production controls; use when forecasting-specific guidance must connect to deployment

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
| [scripts/ts_evaluator.py](scripts/ts_evaluator.py) | Stdlib-only CLI: horizon-wise backtest metrics, probabilistic calibration check, and full Markdown evaluation report |

```bash
# Horizon-wise accuracy: MAE, RMSE, MAPE, skill score vs naive baseline
python scripts/ts_evaluator.py backtest --input data/sample-forecast-results.json

# Probabilistic calibration check for 50%, 80%, 90% prediction intervals
python scripts/ts_evaluator.py calibration --input data/sample-forecast-results.json

# Full Markdown evaluation report written to file
python scripts/ts_evaluator.py report --input data/sample-forecast-results.json --output /tmp/ts-eval-report.md
```

## Data Files

| File | Description |
|------|-------------|
| [data/sources.json](data/sources.json) | Curated primary sources for classical forecasting, MLForecast, skforecast, AutoGluon, Chronos-2/Chronos-Bolt, TimesFM, Toto, fev-bench, and MAPIE |
| [data/sample-forecast-results.json](data/sample-forecast-results.json) | Realistic rolling-origin backtest results for a daily revenue forecast model across horizons 1, 7, 14, 30 days (48 rows, 12 backtest origins) |

## External Sources

See **[data/sources.json](data/sources.json)** for current primary sources across:

- classical forecasting references
- official docs for MLForecast, HierarchicalForecast, skforecast, AutoGluon TimeSeries, LightGBM, and MAPIE
- official Chronos-2/Chronos-Bolt, TimesFM, and Toto repositories
- fev-bench benchmark and governance references used for high-impact deployments

## Related Skills

- **[ai-ml-data-science](../ai-ml-data-science/SKILL.md)** - General DS workflows, experiment design, and broader modelling patterns
- **[ai-mlops](../ai-mlops/SKILL.md)** - Deployment architecture, monitoring, and release operations
- **[ai-llm](../ai-llm/SKILL.md)** - Provider/model lifecycle questions outside time-series forecasting
- **[data-sql-optimization](../data-sql-optimization/SKILL.md)** - Storage and query design for time-series marts

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify volatile external facts, package APIs, hosted options, and model capabilities before final answers.
- Prefer official docs, official repositories, standards, or release notes.
- If web access is unavailable, state that clearly and mark time-sensitive guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
