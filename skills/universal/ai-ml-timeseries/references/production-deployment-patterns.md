# Production Forecast Operations

Forecast-specific production rules. Generic pipeline, registry, retraining-scheduler, feature-drift, ingestion and governance patterns live in [ai-mlops](../../ai-mlops/SKILL.md); this file keeps only what changes because the model is a forecast.

## Table of Contents

- [What Lives Where](#what-lives-where)
- [Monitor Error Against The Backtest, By Horizon](#monitor-error-against-the-backtest-by-horizon)
- [Actuals Latency](#actuals-latency)
- [Forecast Of Record Per Vintage](#forecast-of-record-per-vintage)
- [Fallback Ladder](#fallback-ladder)
- [Checklist](#checklist)

## What Lives Where

| Need | Owner |
|------|-------|
| Same code for training and serving, idempotent feature jobs, replay | [ai-mlops feature-store-patterns](../../ai-mlops/references/feature-store-patterns.md) |
| Scheduled or triggered retraining, champion/challenger gate | [ai-mlops automated-retraining-patterns](../../ai-mlops/references/automated-retraining-patterns.md) |
| Feature distribution drift (PSI, KS) | [ai-mlops drift-detection-guide](../../ai-mlops/references/drift-detection-guide.md) |
| Streaming ingestion, late and out-of-order events, backfill jobs | [ai-mlops data-ingestion-patterns](../../ai-mlops/references/data-ingestion-patterns.md) |
| Tenant isolation, PII, residency | [ai-mlops governance-checklists](../../ai-mlops/references/governance-checklists.md) |
| Forecast contract, cutoff record, lineage | [forecast-governance-patterns.md](forecast-governance-patterns.md) |

## Monitor Error Against The Backtest, By Horizon

- The reference for live error at horizon h is the **distribution of backtest error at the same h**, from the rolling-origin backtest that justified deployment. Never compare against training (in-sample) error: it is optimistic by construction and makes every healthy model look degraded.
- Alert when the rolling live error at h leaves the upper backtest quantile you chose in advance (for example the 90th percentile of fold errors at h) for the number of consecutive windows that the backtest says is unlikely under no change. Set the quantile and run length from the backtest, not from a flat percentage.
- Error rising with horizon is expected; a single "MAE grew 15%" threshold across horizons alerts on long horizons and misses short ones.
- Also track live skill against the seasonal-naive forecast at each h. A model whose skill falls to about 0 is no longer earning its cost even if absolute error looks stable (for example after a level shift that also hurts the baseline).
- Report by the same slices the backtest used (volume band, segment); an aggregate hides a failing slice.

## Actuals Latency

- A forecast for horizon h can be scored only after its actual lands **and stops being revised**. Record, per target, the delay until actuals are final (settlements, returns, restatements).
- Score only matured forecasts; mark the rest pending. Scoring provisional actuals makes error jump when late revisions arrive.
- Long horizons plus slow actuals mean weeks before a degradation is visible. Pair error monitoring with leading signals: covariate availability, input volume, and the share of series on fallback.
- Late or out-of-order source data must re-run the affected cutoff, not overwrite the stored forecast (see the next section).

## Forecast Of Record Per Vintage

- Store every issued forecast immutably, keyed by (series, cutoff timestamp, horizon, model version). This forecast of record is what gets scored, audited and explained.
- Never regenerate a past vintage with today's data or model to "fill a gap"; that leaks the future into the evaluation and hides what decision-makers actually saw.
- Keep the fallback flag and the covariate values used with each record, so a bad period can be traced to model, data or fallback.

## Fallback Ladder

Define the order before launch and test each step:

1. Primary model, if its inputs are complete and the forecast passes sanity checks.
2. Last known-good model version, if the new version fails checks.
3. Seasonal-naive: the value one season earlier for each target period (for daily data with weekly seasonality, the same weekday last week), not the whole last season as a single vector.
4. Naive (last value) or a short moving average, when history is shorter than one season.
5. Explicit "insufficient data" response; never an unlabelled zero.

Sanity checks that trigger the next step: missing or non-finite values, wrong sign for the target, values far outside the historical range at that horizon, a flat forecast for a series that is not flat, and missing known-future covariates. Record which step served each forecast and alert on the fallback share.

## Checklist

- [ ] Live error monitored per horizon against the backtest error distribution, not training error
- [ ] Live skill vs seasonal-naive tracked per horizon and slice
- [ ] Actuals finality delay recorded; only matured forecasts scored
- [ ] Forecast of record stored immutably per vintage with fallback flag
- [ ] Fallback ladder defined, tested, and its usage alerted
- [ ] Generic pipeline, retraining, drift and governance controls delegated to ai-mlops
