# LightGBM and Feature-Based Forecasting Patterns

Operational patterns for using LightGBM-style boosted trees for forecasting in March 2026.

## Table of Contents

- [Why This Family Still Matters](#why-this-family-still-matters)
- [Recommended Problem Shape](#recommended-problem-shape)
- [Core Feature Rules](#core-feature-rules)
- [1. Shift Before Rolling](#1-shift-before-rolling)
- [2. Encode Calendar Features Explicitly](#2-encode-calendar-features-explicitly)
- [3. Separate Known-Future From Future-Unknown Covariates](#3-separate-known-future-from-future-unknown-covariates)
- [Library-Level Patterns](#library-level-patterns)
- [MLForecast-Style Global Forecasting](#mlforecast-style-global-forecasting)
- [skforecast-Style Recursive Or Direct Wrappers](#skforecast-style-recursive-or-direct-wrappers)
- [Validation And Tuning](#validation-and-tuning)
- [Do Not Use IID Cross-Validation](#do-not-use-iid-cross-validation)
- [Practical Tuning Order](#practical-tuning-order)
- [Multi-Step Forecasting](#multi-step-forecasting)
- [Common Failure Modes](#common-failure-modes)
- [Evaluation Checklist](#evaluation-checklist)
- [Cross-References](#cross-references)

## Why This Family Still Matters

Feature-based forecasting remains one of the strongest practical defaults when:

- you have many related series
- covariates such as price, promotions, holidays, or weather matter
- you need a good accuracy/latency/maintainability balance
- you want explainability that is still operationally useful

The model does **not** understand time by itself. Temporal structure must be expressed through the schema, features, cutoffs, and validation design.

## Recommended Problem Shape

Use this family when you have:

- `unique_id` or another stable series key
- `ds` timestamp column
- `y` target column
- optional static features per series
- optional known-future covariates such as holidays, planned promotions, or tariff schedules

This pattern scales especially well for **global/panel forecasting**, where one model learns from many related series.

## Core Feature Rules

### 1. Shift Before Rolling

Every aggregate derived from the target must be built from past-only values.

```python
import numpy as np
import pandas as pd

df = df.sort_values(["unique_id", "ds"]).copy()

for lag in [1, 7, 28]:
    df[f"lag_{lag}"] = df.groupby("unique_id")["y"].shift(lag)

for window in [7, 28]:
    shifted = df.groupby("unique_id")["y"].shift(1)
    df[f"rolling_mean_{window}"] = (
        shifted.groupby(df["unique_id"]).rolling(window).mean().reset_index(level=0, drop=True)
    )
    df[f"rolling_std_{window}"] = (
        shifted.groupby(df["unique_id"]).rolling(window).std().reset_index(level=0, drop=True)
    )
```

### 2. Encode Calendar Features Explicitly

```python
iso_week = df["ds"].dt.isocalendar().week.astype("int16")
df["day_of_week"] = df["ds"].dt.dayofweek.astype("int8")
df["day_of_month"] = df["ds"].dt.day.astype("int8")
df["month"] = df["ds"].dt.month.astype("int8")
df["iso_week"] = iso_week

df["dow_sin"] = np.sin(2 * np.pi * df["day_of_week"] / 7)
df["dow_cos"] = np.cos(2 * np.pi * df["day_of_week"] / 7)
```

### 3. Separate Known-Future From Future-Unknown Covariates

Known-future covariates:

- holidays
- planned promotions
- tariff schedules
- published event calendars

Future-unknown covariates:

- realized weather
- realized demand from adjacent systems
- future inventory position unless already scheduled and fixed

Do not feed future-unknown values into the forecast horizon unless you forecast them separately or use scenario inputs.

## Library-Level Patterns

### MLForecast-Style Global Forecasting

Use when:

- many related series share patterns
- you want a global feature-based model
- you want forecasting-specific utilities around lags, windows, and backtesting

```python
from lightgbm import LGBMRegressor
from mlforecast import MLForecast
from mlforecast.lag_transforms import RollingMean

fcst = MLForecast(
    models=[LGBMRegressor(
        objective="regression",
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=63,
        random_state=42,
    )],
    freq="D",
    lags=[1, 7, 28],
    lag_transforms={1: [RollingMean(window_size=7), RollingMean(window_size=28)]},
    date_features=["dayofweek", "month", "quarter"],
)

fcst.fit(
    train_df,
    id_col="unique_id",
    time_col="ds",
    target_col="y",
    static_features=["store_id", "item_family"],
)
```

### skforecast-Style Recursive Or Direct Wrappers

Use when:

- the workflow is mainly single-series or small-portfolio
- you want direct or recursive wrappers around a tabular regressor
- you need a lighter-weight forecasting abstraction

## Validation And Tuning

### Do Not Use IID Cross-Validation

Never use repeated K-fold or standard `GridSearchCV(..., cv=5)` for forecasting rows.

Use:

- rolling-origin backtests
- expanding windows
- panel-aware time splits

### Practical Tuning Order

1. stabilize the schema and cutoff logic
2. verify baseline performance
3. tune lags and windows
4. tune tree complexity and regularization
5. retest with rolling-origin backtests

Useful parameters to tune:

- `num_leaves`
- `learning_rate`
- `n_estimators`
- `min_child_samples`
- `feature_fraction`
- `bagging_fraction`

Tune under a time-aware backtest budget, not with generic row-wise CV.

## Multi-Step Forecasting

Common options:

- **Direct**: one model per horizon or horizon bucket
- **Recursive**: one-step model rolled forward
- **DirRec / hybrid**: mix direct horizon targets with recursive feature updates

Use direct approaches when:

- horizons are short to medium
- horizon-specific behavior matters
- parallel training is acceptable

Use recursive approaches when:

- you need one simpler model
- sequential dependence is strong
- you can tolerate error propagation and validate it explicitly

## Common Failure Modes

| Failure | Why It Hurts | Fix |
|--------|---------------|-----|
| Rolling features built without a prior shift | Leaks current target into features | Shift first, then roll |
| No `unique_id` grouping | Cross-series leakage | Group lags and windows by series |
| Future-known and future-unknown covariates mixed together | Impossible deployment assumptions | Split covariates by availability |
| Generic K-fold CV | Inflated validation scores | Use rolling-origin backtests |
| Only aggregate metrics reported | Long-horizon failures stay hidden | Report horizon and slice metrics |

## Evaluation Checklist

- [ ] Baselines included
- [ ] Features grouped by `unique_id`
- [ ] Rolling stats use shifted targets only
- [ ] Known-future covariates documented
- [ ] Rolling-origin validation performed
- [ ] Horizon-wise metrics reported
- [ ] Slice analysis included
- [ ] Explainability artifacts produced if required

## Cross-References

- [global-panel-forecasting-patterns.md](global-panel-forecasting-patterns.md) - shared-model schemas and grouped validation
- [backtesting-patterns.md](backtesting-patterns.md) - rolling-origin evaluation
- [probabilistic-forecasting.md](probabilistic-forecasting.md) - quantiles and intervals on top of feature-based models
