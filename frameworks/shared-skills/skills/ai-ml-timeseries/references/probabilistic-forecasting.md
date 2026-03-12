# Probabilistic Forecasting

> Operational guide for generating prediction intervals, quantile forecasts, and distributional predictions. Covers quantile regression, conformal prediction, calibration assessment, and decision support using uncertainty. Focus on producing reliable uncertainty estimates, not just point forecasts.

**Freshness anchor:** January 2026 — MAPIE 0.9+, LightGBM 4.x, statsforecast 1.7+, scikit-learn 1.5+

---

## Decision Tree: Choosing a Probabilistic Method

```
START
│
├─ Need distribution-free guarantees?
│   ├─ YES → Conformal Prediction (MAPIE)
│   └─ NO  → Continue
│
├─ Model type?
│   ├─ LightGBM / XGBoost / tree-based
│   │   ├─ Need specific quantiles → Quantile regression (native)
│   │   └─ Need full distribution → Conformal on top of point model
│   │
│   ├─ Linear / GLM
│   │   ├─ Known distribution → Distributional (Normal, Poisson, NegBin)
│   │   └─ Unknown → Quantile regression (QuantReg)
│   │
│   ├─ Neural network (temporal fusion transformer, etc.)
│   │   └─ Distributional output head or quantile loss
│   │
│   └─ Statistical (ARIMA, ETS, Prophet)
│       └─ Built-in prediction intervals (use them, then calibrate)
│
├─ What uncertainty do you need?
│   ├─ Symmetric intervals (80%, 95%) → Conformal or normal approx
│   ├─ Asymmetric intervals → Quantile regression
│   └─ Full predictive distribution → Distributional model or ensemble
│
└─ How many training samples?
    ├─ < 500 → Conformal (works with small calibration sets)
    ├─ 500–50k → Quantile regression
    └─ > 50k → Any method
```

---

## Quick Reference: Methods Comparison

| Method | Guarantees | Calibration | Asymmetric | Implementation Effort |
|--------|-----------|-------------|------------|----------------------|
| Conformal prediction | Coverage guarantee | Auto-calibrated | No (symmetric) | Low (wraps any model) |
| Quantile regression | None (must calibrate) | Manual check | Yes | Medium |
| Bootstrap residuals | Approximate | Manual check | Depends | Low |
| Distributional forecast | Parametric assumption | Must verify | Depends on distribution | Medium-High |
| Bayesian inference | Posterior coverage | Auto (if model correct) | Yes | High |
| Ensemble spread | Heuristic | Must calibrate | Yes | Medium |

---

## Operational Patterns

### Pattern 1: Conformal Prediction with MAPIE

- **Use when:** Need guaranteed coverage with any base model
- **Implementation:**

```python
from mapie.regression import MapieRegressor
from mapie.time_series import MapieTimeSeriesRegressor
from sklearn.ensemble import GradientBoostingRegressor

# Standard conformal (exchangeable data)
base_model = GradientBoostingRegressor(n_estimators=300)
mapie = MapieRegressor(
    estimator=base_model,
    method='plus',         # jackknife+ (recommended)
    cv=5,                  # cross-conformal
)
mapie.fit(X_train, y_train)

y_pred, y_intervals = mapie.predict(X_test, alpha=[0.05, 0.20])
# y_intervals shape: (n_samples, 2, n_alphas)
# alpha=0.05 → 95% interval; alpha=0.20 → 80% interval

# Time series conformal (accounts for temporal dependence)
mapie_ts = MapieTimeSeriesRegressor(
    estimator=base_model,
    method='enbpi',        # ensemble batch prediction intervals
    cv='prefit',
)
mapie_ts.fit(X_train, y_train)
y_pred_ts, y_intervals_ts = mapie_ts.predict(
    X_test, alpha=0.05, ensemble=True, optimize_beta=True
)
```

- **Key property:** Conformal guarantees `P(y in interval) >= 1 - alpha` regardless of model quality
- **Gotcha:** Guarantee is marginal (average coverage), not conditional (per-instance)

### Pattern 2: LightGBM Quantile Regression

- **Use when:** Need specific quantiles, tabular data, fast training
- **Implementation:**

```python
import lightgbm as lgb

def train_quantile_model(X_train, y_train, quantile, params=None):
    """Train a single quantile model."""
    default_params = {
        'objective': 'quantile',
        'alpha': quantile,
        'metric': 'quantile',
        'n_estimators': 500,
        'learning_rate': 0.05,
        'num_leaves': 63,
        'verbosity': -1,
    }
    if params:
        default_params.update(params)

    model = lgb.LGBMRegressor(**default_params)
    model.fit(X_train, y_train)
    return model

# Train multiple quantiles
quantiles = [0.025, 0.10, 0.25, 0.50, 0.75, 0.90, 0.975]
models = {q: train_quantile_model(X_train, y_train, q) for q in quantiles}

# Predict
predictions = {q: m.predict(X_test) for q, m in models.items()}

# 95% interval: [0.025, 0.975]
# 80% interval: [0.10, 0.90]
# Point forecast: 0.50 (median)
```

- **Quantile crossing fix:** Sort predicted quantiles per instance

```python
import numpy as np

def fix_crossing(pred_dict, quantiles):
    """Ensure quantile predictions don't cross."""
    matrix = np.column_stack([pred_dict[q] for q in sorted(quantiles)])
    matrix_sorted = np.sort(matrix, axis=1)  # enforce monotonicity
    return {q: matrix_sorted[:, i] for i, q in enumerate(sorted(quantiles))}
```

### Pattern 3: Distributional Forecasting

- **Use when:** Know the data-generating distribution, need full predictive distribution
- **Distribution selection:**

| Data Type | Distribution | Parameters | Use Case |
|-----------|-------------|------------|----------|
| Continuous, symmetric | Normal | mu, sigma | Revenue, temperature |
| Continuous, positive | LogNormal | mu, sigma | Prices, durations |
| Count data (low) | Poisson | lambda | Daily events, arrivals |
| Count data (overdispersed) | Negative Binomial | mu, alpha | Sales counts with variance |
| Continuous, positive, skewed | Gamma | shape, rate | Wait times, claim amounts |
| Zero-inflated counts | ZINB | mu, alpha, pi | Intermittent demand |

```python
# Example: Negative Binomial for sales count data
import statsmodels.api as sm

# GLM approach
model = sm.GLM(
    y_train,
    sm.add_constant(X_train),
    family=sm.families.NegativeBinomial(alpha=1.0),
)
result = model.fit()

# Generate prediction intervals from fitted distribution
from scipy.stats import nbinom
mu_pred = result.predict(sm.add_constant(X_test))
alpha = result.scale
# Convert to scipy parameterization and compute intervals
```

### Pattern 4: Calibration Assessment

- **Use when:** Always — every probabilistic forecast must be calibrated

```python
def assess_calibration(y_true, lower, upper, nominal_coverage=0.95):
    """Check if prediction intervals achieve stated coverage."""
    covered = ((y_true >= lower) & (y_true <= upper)).mean()

    width = (upper - lower).mean()

    return {
        'nominal_coverage': nominal_coverage,
        'actual_coverage': covered,
        'miscalibration': abs(covered - nominal_coverage),
        'mean_interval_width': width,
    }

# Multi-level calibration (reliability diagram)
def calibration_curve(y_true, quantile_preds, quantiles):
    """PIT histogram / reliability diagram."""
    results = []
    for q in quantiles:
        below = (y_true <= quantile_preds[q]).mean()
        results.append({'quantile': q, 'observed_fraction': below})
    return pd.DataFrame(results)

# Perfect calibration: observed_fraction ≈ quantile at all levels
```

- **Calibration targets:**

| Metric | Good | Acceptable | Poor |
|--------|------|-----------|------|
| Coverage error (95%) | < 2% | 2–5% | > 5% |
| Coverage error (80%) | < 3% | 3–7% | > 7% |
| PIT uniformity (KS test p-value) | > 0.10 | 0.01–0.10 | < 0.01 |

### Pattern 5: Scoring Rules

- **Use when:** Comparing probabilistic forecasts (not just point accuracy)

```python
def pinball_loss(y_true, y_pred, quantile):
    """Quantile loss (pinball loss) — lower is better."""
    errors = y_true - y_pred
    return np.where(errors >= 0, quantile * errors, (quantile - 1) * errors).mean()

def winkler_score(y_true, lower, upper, alpha=0.05):
    """Winkler interval score — penalizes width + miscoverage."""
    width = upper - lower
    penalty_lower = (2 / alpha) * np.maximum(lower - y_true, 0)
    penalty_upper = (2 / alpha) * np.maximum(y_true - upper, 0)
    return (width + penalty_lower + penalty_upper).mean()

def crps_empirical(y_true, ensemble_preds):
    """CRPS from ensemble predictions — measures full distribution quality."""
    n_ensemble = ensemble_preds.shape[1]
    n_samples = len(y_true)

    crps_values = []
    for i in range(n_samples):
        fc = np.sort(ensemble_preds[i])
        obs = y_true[i]
        term1 = np.mean(np.abs(fc - obs))
        term2 = np.mean(np.abs(fc[:, None] - fc[None, :])) / 2
        crps_values.append(term1 - term2)
    return np.mean(crps_values)

# Metric selection:
# - Pinball loss → evaluating specific quantiles
# - Winkler score → evaluating prediction intervals
# - CRPS → evaluating full predictive distribution
```

### Pattern 6: Decision Support with Prediction Intervals

- **Use when:** Translating uncertainty into actionable decisions

```python
# Inventory planning with quantile forecasts
def compute_safety_stock(demand_forecast, upper_quantile, lead_time_days):
    """Safety stock from prediction intervals."""
    # Upper quantile represents service level
    # e.g., 0.95 quantile → 95% service level
    expected_demand = demand_forecast['q50'] * lead_time_days
    safety_stock = (upper_quantile - demand_forecast['q50']) * np.sqrt(lead_time_days)
    reorder_point = expected_demand + safety_stock
    return {
        'expected_demand': expected_demand,
        'safety_stock': safety_stock,
        'reorder_point': reorder_point,
    }

# Risk-aware decision thresholds
# - Conservative (risk-averse): use 95th percentile
# - Balanced: use 80th percentile
# - Aggressive (cost-minimizing): use median (50th percentile)
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Using point forecast +/- constant as interval | Ignores heteroscedasticity, wrong coverage | Use proper probabilistic method |
| Not checking calibration | Intervals may have 70% coverage when labeled 95% | Always compute coverage on holdout |
| Quantile crossing (q10 > q50 for some instances) | Invalid probabilistic forecast | Sort quantiles per instance |
| Training single model for multiple quantiles | Each quantile needs separate loss optimization | Train one model per quantile (or multi-output) |
| Normal assumption on skewed data | Intervals are symmetric when data is asymmetric | Use quantile regression or appropriate distribution |
| Evaluating probabilistic forecast with MAE only | Ignores uncertainty quality | Use CRPS, Winkler, or pinball loss |
| Conformal on non-exchangeable data | Coverage guarantee doesn't hold | Use time-series conformal (EnbPI) |
| Ignoring interval width | Trivially wide intervals have perfect coverage | Report sharpness alongside coverage |
| Same alpha for all use cases | Different decisions need different confidence levels | Match alpha to decision cost structure |
| Not recalibrating after model update | New model may have different calibration | Recalibrate on fresh holdout after every retrain |

---

## Validation Checklist

- [ ] Probabilistic method chosen based on model type and data properties
- [ ] Coverage assessed at multiple levels (80%, 90%, 95%)
- [ ] Calibration error < 5% at each level
- [ ] Interval sharpness (width) reported alongside coverage
- [ ] Scoring rule used for model comparison (CRPS or Winkler)
- [ ] Quantile crossing handled (sorting or monotonic constraint)
- [ ] Decision framework maps uncertainty to business actions
- [ ] Conformal guarantee assumptions verified (exchangeability or time-series variant)
- [ ] Recalibration scheduled after each model retrain
- [ ] PIT histogram checked for uniformity

---

## Cross-References

- `ai-ml-timeseries/references/hierarchical-forecasting.md` — coherent probabilistic forecasts across levels
- `ai-ml-timeseries/references/anomaly-detection-patterns.md` — prediction intervals as anomaly bounds
- `ai-ml-data-science/references/hyperparameter-optimization.md` — tuning quantile models
- `ai-mlops/references/experiment-tracking-patterns.md` — logging interval metrics and calibration
