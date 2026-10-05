# Global and Panel Forecasting Patterns

Operational patterns for forecasting many related series with a shared model.

Use this when the problem is not just "one series over time" but "many series with shared signal".

## When To Prefer A Global/Panel Model

Use a shared model when:

- you have many related series
- some individual series are short or noisy
- shared covariates such as promotions, holidays, price, or channel matter
- you want one training workflow instead of many local models

Prefer local-only models when:

- there are very few important series
- each series behaves very differently and has enough history on its own
- interpretability and per-series simplicity matter more than pooled learning

## Minimum Schema

Use a long-format table with:

- `unique_id` or equivalent series key
- `ds` timestamp
- `y` target value
- optional static features per series
- optional dynamic covariates per timestamp

Recommended categories:

- static features: region, store format, product family
- known-future covariates: holidays, planned promotions, tariffs
- future-unknown covariates: realized weather, realized competitor actions

Keep the distinction explicit.

## Panel Feature Rules

- Build lag and rolling features within each `unique_id`, never across pooled rows.
- Keep feature windows aligned to the series frequency.
- Use series metadata as static features only if it is available at inference time.
- If the panel is sparse or intermittent, add zero-aware features such as recent zero counts and days since last demand.

## Backtesting Rules

- Split by cutoff time first, not by random rows.
- Keep all series aligned to the same cutoff schedule when possible.
- Report both overall metrics and metrics by volume band, geography, or series family.
- Inspect tails: a good mean can hide many broken low-volume or high-volume series.

## Practical Model Choices

| Situation | Good Default |
|----------|---------------|
| Covariate-rich tabular panel | MLForecast or skforecast with LightGBM/XGBoost |
| Mixed panel with fast baseline search | AutoGluon TimeSeries |
| Deep shared temporal structure | Neural/deep forecasting stack |
| Must roll up coherently | base panel forecast + hierarchical reconciliation |

## Failure Modes

| Failure | Why It Breaks | Fix |
|--------|----------------|-----|
| Treating pooled rows as IID | Cross-series leakage and fake validation | Group features by series and split by time |
| Missing `unique_id` semantics | Features silently mix series | Enforce schema contract |
| Using future-unknown covariates at inference | Unrealistic forecasts | Separate known-future from unknown-future drivers |
| Reporting only one global score | High-risk cohorts disappear | Report slices and tails |

## Checklist

- [ ] Long-format schema defined
- [ ] `unique_id`, `ds`, and `y` present
- [ ] Static vs dynamic covariates separated
- [ ] Known-future vs future-unknown covariates separated
- [ ] Grouped lag/rolling features implemented
- [ ] Time-based panel backtesting used
- [ ] Slice metrics reported
- [ ] Hierarchical coherence requirement checked
