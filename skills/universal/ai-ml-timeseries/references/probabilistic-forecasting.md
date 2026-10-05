# Probabilistic Forecasting

Operational guide for prediction intervals, quantile forecasts, and full predictive distributions.

The goal is **decision-useful uncertainty**, not just a confidence band on a chart.

## Table of Contents

- [Decision Tree](#decision-tree)
- [Methods Comparison](#methods-comparison)
- [Pattern 1: Split Conformal With MAPIE v1](#pattern-1-split-conformal-with-mapie-v1)
- [Fit the base model first or let SplitConformalRegressor fit it when prefit=False.](#fit-the-base-model-first-or-let-splitconformalregressor-fit-it-when-prefit=false)
- [Pattern 2: Time-Series Conformal With MAPIE v1](#pattern-2-time-series-conformal-with-mapie-v1)
- [Pattern 3: Quantile Regression](#pattern-3-quantile-regression)
- [Pattern 4: Distributional Forecasting](#pattern-4-distributional-forecasting)
- [Calibration Assessment](#calibration-assessment)
- [Coverage Against Sampling Noise](#coverage-against-sampling-noise)
- [Scoring Rules](#scoring-rules)
- [Decision Quantile From Costs](#decision-quantile-from-costs)
- [Anti-Patterns](#anti-patterns)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)

## Decision Tree

```text
Need uncertainty for a forecast:
    ├─ Need distribution-free coverage guarantees?
    │   ├─ IID/exchangeable setting -> split or cross conformal
    │   └─ Time-dependent residuals -> time-series conformal (EnbPI / adaptive variants)
    │
    ├─ Need asymmetric intervals or service-level planning?
    │   └─ Quantile regression or conformalized quantile regression
    │
    ├─ Know the observation family?
    │   └─ Use distributional forecasting (Poisson, NegBin, Gamma, etc.) and still check calibration
    │
    └─ Need fast practical default?
        └─ Quantile model + calibration review, or conformal wrapper on top of a strong point model
```

## Methods Comparison

| Method | Main Benefit | Main Limitation | Good Fit |
|--------|--------------|-----------------|----------|
| Split conformal | Coverage guarantee with simple workflow | Symmetric intervals unless combined with quantiles | Strong point model + calibration set |
| Time-series conformal | Adapts to temporal dependence | More stateful and implementation-heavy | Sequential forecasting with residual drift |
| Quantile regression | Native asymmetric intervals | No automatic guarantee | Inventory, staffing, risk-sensitive planning |
| Conformalized quantile regression | Asymmetric intervals plus conformal calibration | More moving parts | Strong quantile models with calibration set |
| Distributional forecasting | Full probabilistic model | Assumption-sensitive | Count data, positive skew, demand distributions |

## Pattern 1: Split Conformal With MAPIE v1

MAPIE v1 replaced the older generic regression classes with more specific names such as:

- `SplitConformalRegressor`
- `CrossConformalRegressor`
- `ConformalizedQuantileRegressor`
- `TimeSeriesRegressor`

It also moved time-series usage to `mapie.regression` and uses `confidence_level` for the time-series interface.

Use split conformal when:

- you have a strong point model already
- you can reserve a clean conformalization/calibration window
- you want a simple, auditable interval workflow

```python
from lightgbm import LGBMRegressor
from mapie.regression import SplitConformalRegressor

base_model = LGBMRegressor(
    n_estimators=500,
    learning_rate=0.05,
    num_leaves=63,
    random_state=42,
)

# Fit the base model first or let SplitConformalRegressor fit it when prefit=False.
base_model.fit(X_train, y_train)

scr = SplitConformalRegressor(
    estimator=base_model,
    confidence_level=[0.8, 0.95],
    prefit=True,
)
scr.conformalize(X_calib, y_calib)
pred_df = scr.predict_interval(X_test)
```

Key rule:

- the calibration window must be later in time than the training window
- do not random-shuffle rows into calibration

## Pattern 2: Time-Series Conformal With MAPIE v1

Use `TimeSeriesRegressor` when:

- residual behavior changes over time
- you need one-step or sequential updates
- temporal dependence makes exchangeability assumptions too weak

```python
from lightgbm import LGBMRegressor
from mapie.regression import TimeSeriesRegressor
from mapie.subsample import BlockBootstrap

base_model = LGBMRegressor(n_estimators=300, random_state=42)

ts_reg = TimeSeriesRegressor(
    estimator=base_model,
    method="enbpi",
    cv=BlockBootstrap(n_resamplings=20, length=24, overlapping=True),
)

ts_reg.fit(X_train, y_train)
# predict returns (point, intervals); TimeSeriesRegressor has no predict_interval
y_pred, y_pis = ts_reg.predict(X_test[:step], confidence_level=0.9, ensemble=True)

# EnbPI's value comes from sequential updates as actuals arrive
ts_reg.update(X_test[:step], y_test[:step], ensemble=True, confidence_level=0.9)
```

Use this when the prediction process is sequential and you expect interval width to evolve with recent residuals.

## Pattern 3: Quantile Regression

Use when:

- the decision needs asymmetric risk control
- you need P10/P50/P90 or similar service-level outputs
- the base model is feature-based and tabular

```python
import lightgbm as lgb

def train_quantile_model(X_train, y_train, q):
    model = lgb.LGBMRegressor(
        objective="quantile",
        alpha=q,
        n_estimators=500,
        learning_rate=0.05,
        num_leaves=63,
        random_state=42,
        verbosity=-1,
    )
    model.fit(X_train, y_train)
    return model

quantiles = [0.1, 0.5, 0.9]
models = {q: train_quantile_model(X_train, y_train, q) for q in quantiles}
predictions = {q: model.predict(X_test) for q, model in models.items()}
```

Watch for quantile crossing. Fix it explicitly or use model-side monotonic post-processing if available.

## Pattern 4: Distributional Forecasting

Use when the outcome family is well understood:

| Outcome Type | Usual Family | Example |
|-------------|--------------|---------|
| Counts | Poisson or Negative Binomial | Daily orders, arrivals |
| Positive skew | Gamma or LogNormal | Claim amount, duration |
| Zero-heavy counts | Zero-inflated count family | Intermittent demand |

Even with a distributional model, still evaluate empirical coverage and calibration.

## Calibration Assessment

Every probabilistic model must be checked on holdout windows.

Minimum reporting:

- empirical coverage at each target level, including the decision quantile q* (see [Decision Quantile From Costs](#decision-quantile-from-costs))
- mean interval width
- pinball loss or CRPS
- horizon-wise calibration
- slice-wise calibration for important cohorts

```python
import pandas as pd

def assess_interval_calibration(y_true, lower, upper, nominal):
    actual_coverage = ((y_true >= lower) & (y_true <= upper)).mean()
    mean_width = (upper - lower).mean()
    return {
        "nominal_coverage": nominal,
        "actual_coverage": actual_coverage,
        "coverage_error": abs(actual_coverage - nominal),
        "mean_interval_width": mean_width,
    }

def quantile_reliability(y_true, quantile_preds):
    rows = []
    for q, preds in quantile_preds.items():
        observed = (y_true <= preds).mean()
        rows.append({"quantile": q, "observed_fraction": observed})
    return pd.DataFrame(rows)
```

## Coverage Against Sampling Noise

Load this before calling an interval over- or under-confident from backtest coverage.

- Under independent coverage hits with a common probability p, coverage from n origins is a binomial estimate with standard error sqrt(p(1 - p) / n). Worked check: for p = 0.8 this is about 0.09 at n = 20 and 0.04 at n = 100. The [NIST Wilson interval](https://www.itl.nist.gov/div898/handbook/prc/section2/prc241.htm) is a screen under those assumptions; a fixed "within 5 pp" rule ignores sample size.
- If p lies outside a horizon's Wilson interval, flag that horizon for investigation. "Consistent with nominal" means the screen did not reject, not proof of calibration. Screening many levels and horizons also increases false-positive risk; confirm decision-critical findings before changing intervals.
- Set n to distinct origins within each horizon, not repeated rows across horizons. The bundled evaluator rejects an interval level supplied for only some rows, because silent exclusions can hide difficult origins or horizons. Pooled coverage is descriptive only; duplicating the same hits across horizons cannot add independent evidence.
- Distinct origins can still have serially dependent hits. Overlapping h-step windows are one cause; spacing origins at least h apart removes overlap but does not remove regime or seasonal dependence. Before promotion, use a block bootstrap of the hit sequence, preserving its dependence, or series-aware resampling for panels. Inspect the hit sequence itself; [residual diagnostics](https://otexts.com/fpp3/diagnostics.html) do not establish independent hits on their own.
- Check conditional coverage. An on-target average can hide misses that cluster in one regime or season (promotion weeks, one quarter, a volume band). Tabulate misses by season, regime and slice, and look for runs of consecutive misses. If misses cluster, recalibrate per group, for example with conformal calibration per group, rather than widening every interval.

## Scoring Rules

Use proper probabilistic scores:

- pinball loss for specific quantiles
- CRPS for full predictive distributions
- interval score / Winkler score for interval quality

Do not evaluate uncertainty quality with MAE alone.

## Decision Quantile From Costs

The quantile to forecast is set by the cost of being short versus the cost of being long, not picked from 80/90/95%:

- decision quantile q* = c_u / (c_u + c_o), where c_u is the cost per unit short (lost margin, penalty, expedite) and c_o the cost per unit left over (holding, spoilage, markdown)
- worked check: c_u = 4, c_o = 1 gives q* = 0.8; c_u = 1, c_o = 3 gives q* = 0.25 (under-stock on purpose)
- score the candidate models with pinball loss at q*, not at a default level, and report empirical coverage of q* per horizon (it should be close to q*)
- when costs differ by segment or horizon, q* differs too; do not reuse one service level across them
- a symmetric central interval answers "how uncertain", not "how much to stock"; use it for communication, and q* for the action

```python
import numpy as np

def pinball_loss(y_true, q_pred, q):
    diff = y_true - q_pred
    return np.maximum(q * diff, (q - 1) * diff).mean()
```

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Point forecast plus/minus constant | Ignores heteroscedasticity and context | Use quantile, conformal, or distributional method |
| Random calibration split | Breaks temporal realism | Use a later-in-time calibration window |
| Reporting only nominal coverage | Wide useless intervals can still "look good" | Report width and sharpness too |
| Ignoring horizon-wise calibration | Near-term and long-term uncertainty behave differently | Calibrate and report by horizon |
| Keeping old MAPIE v0 class names in examples | Users copy broken code | Use v1 class names and interfaces |

## Validation Checklist

- [ ] Probabilistic objective chosen explicitly
- [ ] Calibration window is temporally valid
- [ ] Coverage reported at multiple levels
- [ ] Mean interval width reported
- [ ] Horizon-wise calibration included
- [ ] Slice-wise calibration included
- [ ] Pinball loss or CRPS used for comparison
- [ ] Quantile crossing checked
- [ ] Decision-to-quantile mapping documented
- [ ] Recalibration scheduled after retrains

## Cross-References

- [hierarchical-forecasting.md](hierarchical-forecasting.md) - coherent probabilistic forecasts across levels
- [anomaly-detection-patterns.md](anomaly-detection-patterns.md) - intervals as anomaly bounds
- [backtesting-patterns.md](backtesting-patterns.md) - horizon-aware validation design
