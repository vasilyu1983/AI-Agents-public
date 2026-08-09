# Intermittent Demand Forecasting Patterns

Operational patterns for forecasting sparse, intermittent, or erratic demand with many zeros.

---
## Table of Contents

- [Overview](#overview)
- [Pattern 1: Classical Intermittent Methods](#pattern-1-classical-intermittent-methods)
- [Croston's Method](#crostons-method)
- [Syntetos-Boylan Approximation (SBA)](#syntetos-boylan-approximation-sba)
- [ADIDA (Aggregate-Disaggregate Intermittent Demand Approach)](#adida-aggregate-disaggregate-intermittent-demand-approach)
- [Pattern 2: Modern ML Approaches](#pattern-2-modern-ml-approaches)
- [LightGBM with Zero-Inflation Features](#lightgbm-with-zero-inflation-features)
- [Train LightGBM](#train-lightgbm)
- [Pattern 3: Two-Stage Modeling](#pattern-3-two-stage-modeling)
- [Hurdle Model (Probability + Magnitude)](#hurdle-model-probability-magnitude)
- [Stage 1: Binary classifier (will there be demand?)](#stage-1-binary-classifier-will-there-be-demand)
- [Stage 2: Regressor for non-zero demand](#stage-2-regressor-for-non-zero-demand)
- [Prediction](#prediction)
- [Pattern 4: Hierarchical Bayesian Models](#pattern-4-hierarchical-bayesian-models)
- [Pattern 5: Evaluation Metrics for Intermittent Demand](#pattern-5-evaluation-metrics-for-intermittent-demand)
- [Standard Metrics Often Mislead](#standard-metrics-often-mislead)
- [Pattern 6: Forecasting Very Sparse Data (<10% non-zero)](#pattern-6-forecasting-very-sparse-data-10%-non-zero)
- [Challenges](#challenges)
- [Approach](#approach)
- [Baseline: Average non-zero demand * historical frequency](#baseline-average-non-zero-demand-historical-frequency)
- [Aggregate to weekly/monthly if daily is too sparse](#aggregate-to-weeklymonthly-if-daily-is-too-sparse)
- [Decision Tree: Choosing Intermittent Demand Method](#decision-tree-choosing-intermittent-demand-method)
- [Checklist: Intermittent Demand Forecasting](#checklist-intermittent-demand-forecasting)
- [Data Analysis](#data-analysis)
- [Method Selection](#method-selection)
- [Feature Engineering (for ML)](#feature-engineering-for-ml)
- [Evaluation](#evaluation)
- [Production](#production)
- [References](#references)


## Overview

Intermittent demand occurs when:
- Data has many zeros (>50% zero values)
- Demand is sporadic or lumpy
- Traditional forecasting methods fail due to sparsity

Common in: retail, spare parts, slow-moving inventory, industrial equipment.

---

## Pattern 1: Classical Intermittent Methods

### Croston's Method

**When to Use:**
- Regular intervals between non-zero demands
- Approximately constant demand size

**How It Works:**
1. Forecast demand size separately from demand intervals
2. Combine forecasts: forecast = size / interval

```python
import numpy as np

def croston_forecast(demand, alpha=0.1):
    """
    Croston's intermittent demand forecasting

    Args:
        demand: Array of demand values (with zeros)
        alpha: Smoothing parameter (0-1)
    """
    non_zero_idx = np.where(demand > 0)[0]

    # Initialize
    size_forecast = demand[non_zero_idx[0]]
    interval_forecast = non_zero_idx[1] - non_zero_idx[0]

    forecasts = []

    for i in range(1, len(non_zero_idx)):
        # Update size forecast
        size_forecast = alpha * demand[non_zero_idx[i]] + (1 - alpha) * size_forecast

        # Update interval forecast
        interval = non_zero_idx[i] - non_zero_idx[i-1]
        interval_forecast = alpha * interval + (1 - alpha) * interval_forecast

        # Forecast = size / interval
        forecast = size_forecast / interval_forecast
        forecasts.append(forecast)

    return forecasts
```

### Syntetos-Boylan Approximation (SBA)

**Improvement over Croston:**
- Addresses Croston's bias
- Better for highly intermittent demand

```python
def sba_forecast(demand, alpha=0.1):
    """SBA reduces Croston's bias"""
    croston_fc = croston_forecast(demand, alpha)

    # Bias correction factor
    correction = 1 - (alpha / 2)

    return [fc * correction for fc in croston_fc]
```

### ADIDA (Aggregate-Disaggregate Intermittent Demand Approach)

**When to Use:**
- Need balance between Croston and naive forecasts
- Want simpler approach

```python
def adida_forecast(demand, window=4):
    """
    Aggregate demand over window, then disaggregate
    """
    # Aggregate
    aggregated = [sum(demand[i:i+window]) for i in range(0, len(demand), window)]

    # Forecast aggregated demand
    agg_forecast = aggregated[-1]  # Naive or SES

    # Disaggregate
    return agg_forecast / window
```

---

## Pattern 2: Modern ML Approaches

### LightGBM with Zero-Inflation Features

**Practical March 2026 default when sparse demand also has useful covariates**

```python
import lightgbm as lgb
import pandas as pd

def create_intermittent_features(df, target_col='demand'):
    """
    Feature engineering for intermittent demand
    """
    # Standard lag features
    for lag in [1, 7, 28]:
        df[f'lag_{lag}'] = df[target_col].shift(lag)

    shifted = df[target_col].shift(1)

    # Zero-inflation specific features
    df['zero_count_7d'] = (shifted == 0).rolling(7).sum()
    df['zero_count_28d'] = (shifted == 0).rolling(28).sum()
    df['nonzero_count_7d'] = (shifted > 0).rolling(7).sum()
    df['nonzero_count_28d'] = (shifted > 0).rolling(28).sum()

    # Recency of last non-zero demand
    nonzero_idx = df[df[target_col] > 0].index
    df['days_since_last_demand'] = 0
    for i in df.index:
        recent_nonzero = nonzero_idx[nonzero_idx < i]
        if len(recent_nonzero) > 0:
            df.loc[i, 'days_since_last_demand'] = i - recent_nonzero[-1]

    # Average non-zero demand
    df['avg_nonzero_7d'] = shifted.replace(0, np.nan).rolling(7).mean()
    df['avg_nonzero_28d'] = shifted.replace(0, np.nan).rolling(28).mean()

    # Intermittency coefficient (Croston-inspired)
    df['intermittency_ratio'] = df['zero_count_28d'] / 28

    return df

# Train LightGBM
params = {
    'objective': 'regression',
    'metric': 'mae',
    'boosting_type': 'gbdt',
    'num_leaves': 31,
    'learning_rate': 0.05,
}

train_data = lgb.Dataset(X_train, y_train)
model = lgb.train(params, train_data, num_boost_round=100)
```

**Why LightGBM Works:**
- Handles sparse data naturally
- Captures non-linear patterns in zero occurrence
- Fast training and inference
- Explainable with SHAP values

---

## Pattern 3: Two-Stage Modeling

### Hurdle Model (Probability + Magnitude)

**Stage 1:** Predict probability of non-zero demand
**Stage 2:** Predict magnitude if non-zero

```python
from sklearn.linear_model import LogisticRegression
from lightgbm import LGBMRegressor

# Stage 1: Binary classifier (will there be demand?)
binary_target = (y_train > 0).astype(int)
classifier = LogisticRegression()
classifier.fit(X_train, binary_target)

# Stage 2: Regressor for non-zero demand
non_zero_mask = y_train > 0
regressor = LGBMRegressor()
regressor.fit(X_train[non_zero_mask], y_train[non_zero_mask])

# Prediction
prob_nonzero = classifier.predict_proba(X_test)[:, 1]
magnitude = regressor.predict(X_test)
final_forecast = prob_nonzero * magnitude
```

**Benefits:**
- Models different processes separately
- Improves accuracy for highly intermittent data
- Interpretable (why forecast is zero)

---

## Pattern 4: Hierarchical Bayesian Models

**When to Use:**
- Multiple related intermittent series
- Want probabilistic forecasts
- Have domain knowledge for priors

```python
import pymc as pm

with pm.Model() as hierarchical_model:
    # Global hyperparameters
    mu_global = pm.Normal('mu_global', mu=10, sigma=10)
    sigma_global = pm.HalfNormal('sigma_global', sigma=5)

    # Series-specific parameters
    mu_series = pm.Normal('mu_series', mu=mu_global, sigma=sigma_global, shape=n_series)

    # Zero-inflation parameter
    p_zero = pm.Beta('p_zero', alpha=2, beta=2, shape=n_series)

    # Likelihood
    for i in range(n_series):
        # Zero-inflated Poisson
        pm.ZeroInflatedPoisson(
            f'demand_{i}',
            psi=p_zero[i],
            mu=mu_series[i],
            observed=demand_data[i]
        )

    # Sample posterior
    trace = pm.sample(1000, tune=1000)
```

---

## Pattern 5: Evaluation Metrics for Intermittent Demand

### Standard Metrics Often Mislead

**Problem:** MAPE undefined when actual = 0

**Better Metrics:**

1. **WAPE (Weighted Absolute Percentage Error)**
```python
def wape(y_true, y_pred):
    return np.abs(y_true - y_pred).sum() / y_true.sum()
```

2. **MAE-over-Volume**
```python
def mae_over_volume(y_true, y_pred):
    return np.abs(y_true - y_pred).mean() / y_true.mean()
```

3. **MASE (Mean Absolute Scaled Error)**
```python
def mase(y_true, y_pred, y_train):
    mae = np.abs(y_true - y_pred).mean()
    naive_mae = np.abs(np.diff(y_train)).mean()
    return mae / naive_mae
```

4. **Zero-forecast Accuracy**
```python
def zero_forecast_accuracy(y_true, y_pred, threshold=0.5):
    """How well do we predict zeros?"""
    true_zeros = (y_true == 0)
    pred_zeros = (y_pred < threshold)
    return (true_zeros == pred_zeros).mean()
```

---

## Pattern 6: Forecasting Very Sparse Data (<10% non-zero)

### Challenges
- Not enough non-zero samples
- Classical methods fail
- Need robust baselines

### Approach

1. **Start with simple baseline:**
```python
# Baseline: Average non-zero demand * historical frequency
non_zero_avg = demand[demand > 0].mean()
non_zero_freq = (demand > 0).sum() / len(demand)
baseline_forecast = non_zero_avg * non_zero_freq
```

2. **Try Croston/SBA first:**
```python
croston_fc = croston_forecast(demand, alpha=0.1)
sba_fc = sba_forecast(demand, alpha=0.1)
```

3. **If data allows, use LightGBM with engineered features:**
```python
df = create_intermittent_features(df)
model = lgb.train(params, lgb.Dataset(X_train, y_train))
```

4. **Fall back to aggregation:**
```python
# Aggregate to weekly/monthly if daily is too sparse
weekly_demand = demand.resample('W').sum()
weekly_forecast = forecast_weekly(weekly_demand)
daily_forecast = weekly_forecast / 7  # Disaggregate
```

---

## Judgment Call: Reading Intermittency Correctly Before Choosing A Method

The zero-frequency percentage alone is a weak signal — two series with the same zero rate can need completely different treatment:

- **Distinguish "intermittent" from "lumpy" from "erratic."** Regular small gaps with stable non-zero size (classic Croston territory) behave very differently from irregular gaps with highly variable non-zero size (lumpy demand, where Croston's assumption of roughly constant size breaks down and SBA or a two-stage hurdle model does better). Check the coefficient of variation of non-zero demand sizes, not just the zero rate, before picking a method.
- **Watch for structural zeros vs. stockout zeros.** A zero can mean "no demand" or "we were out of stock and lost the sale." These require opposite handling: true no-demand zeros are legitimate targets; stockout zeros are censored observations that will bias a model toward under-forecasting if treated as real zeros. If stockout flags exist, either exclude those periods or model demand as censored rather than feeding raw stockout zeros as ground truth.
- **Aggregation trades signal for smoothness, but not for free.** Aggregating daily to weekly reduces sparsity and often improves apparent accuracy, but it also delays the operational decision (reorder timing, staffing) by the aggregation window — check that the business can actually act on the coarser cadence before defaulting to it as a fix for sparsity.
- **A hurdle/two-stage model is usually worth the complexity once volume justifies it**, but the two stages should be evaluated separately as well as jointly: a classifier with poor recall on rare-demand events will suppress real orders regardless of how good the magnitude regressor is. Report classifier precision/recall alongside the final WAPE/MASE, not just the blended metric.

## Decision Tree: Choosing Intermittent Demand Method

```
Intermittent Demand Forecasting:
    ├─ Zero frequency > 70% (very sparse)?
    │   ├─ Yes → Croston/SBA or aggregate to higher level
    │   └─ No → LightGBM with zero-inflation features
    │
    ├─ Multiple related series?
    │   ├─ Yes → Hierarchical Bayesian model
    │   └─ No → Single-series approach
    │
    ├─ Need probabilistic forecasts?
    │   ├─ Yes → Hurdle model or Bayesian
    │   └─ No → LightGBM or Croston
    │
    └─ Computational constraints?
        ├─ High → Croston/SBA (fast, simple)
        └─ Low → LightGBM (best performance)
```

---

## Checklist: Intermittent Demand Forecasting

### Data Analysis
- [ ] Computed zero frequency (% zeros)
- [ ] Identified demand pattern (lumpy, erratic, intermittent)
- [ ] Checked for sufficient non-zero samples
- [ ] Analyzed intervals between non-zero demands

### Method Selection
- [ ] Tried simple baseline (avg non-zero × frequency)
- [ ] Tested Croston/SBA for regular patterns
- [ ] Tested LightGBM with zero-inflation features
- [ ] Considered two-stage hurdle model
- [ ] Evaluated hierarchical model if multiple series

### Feature Engineering (for ML)
- [ ] Created zero-count features
- [ ] Added days-since-last-demand
- [ ] Computed average non-zero demand
- [ ] Added intermittency ratio
- [ ] Included seasonal/calendar features

### Evaluation
- [ ] Used appropriate metrics (WAPE, MAE-over-volume, MASE)
- [ ] Avoided MAPE (undefined for zeros)
- [ ] Tracked zero-forecast accuracy
- [ ] Compared against baselines
- [ ] Evaluated by demand category (very sparse vs moderately sparse)

### Production
- [ ] Implemented fallback for very sparse items
- [ ] Set threshold for zero forecasts
- [ ] Monitored forecast accuracy by sparsity level
- [ ] Documented aggregation strategy if needed

---

## References

See also:
- [Model Selection Guide](model-selection-guide.md) - Choosing forecasting models
- [LightGBM TS Patterns](lightgbm-ts-patterns.md) - Tree-based forecasting best practices
- [Lag & Rolling Patterns](lag-rolling-patterns.md) - Feature engineering for ML
