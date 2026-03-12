# Hierarchical Forecasting

> Operational guide for forecasting hierarchically organized time series. Covers reconciliation methods, implementation with Python libraries, and patterns for product, geographic, and temporal hierarchies. Focus on coherent forecasts that add up correctly across levels.

**Freshness anchor:** January 2026 — hierarchicalforecast 0.6+, scikit-hts 0.7+, statsforecast 1.7+

---

## Decision Tree: Choosing a Reconciliation Approach

```
START
│
├─ Hierarchy depth?
│   ├─ 2 levels (e.g., total / products)
│   │   └─ Bottom-up usually sufficient
│   ├─ 3+ levels
│   │   └─ Continue to method selection
│   └─ Grouped (cross-product, e.g., product x region)
│       └─ Use MinT or ERM — simpler methods break on groups
│
├─ Forecast quality varies by level?
│   ├─ Bottom level is best → Bottom-up
│   ├─ Top level is best → Top-down (proportions)
│   ├─ Middle level is best → Middle-out
│   └─ Mixed / unknown → MinT (optimal reconciliation)
│
├─ Need probabilistic forecasts?
│   ├─ YES → MinT with bootstrap or normality assumption
│   └─ NO  → Any reconciliation method
│
├─ Series count?
│   ├─ < 100 series → MinT (full covariance feasible)
│   ├─ 100–10,000 → MinT with shrinkage or diagonal covariance
│   └─ > 10,000 → Bottom-up or top-down (covariance too large)
│
└─ Temporal aggregation needed (daily → weekly → monthly)?
    └─ Temporal reconciliation (FoReco / thief)
```

---

## Quick Reference: Reconciliation Methods

| Method | Approach | Pros | Cons | Use When |
|--------|----------|------|------|----------|
| Bottom-up | Sum base-level forecasts | No information loss, simple | Noisy at bottom | Bottom series are reliable |
| Top-down (AHP) | Disaggregate top by avg proportions | Smooth, uses top-level signal | Loses bottom patterns | Top-level is most reliable |
| Top-down (PHA) | Proportions of historical averages | Better than AHP | Still top-dependent | Simple hierarchy, few levels |
| Middle-out | Forecast at middle, aggregate up, disaggregate down | Balances noise vs signal | Choosing middle level is subjective | Clear "natural" middle level |
| OLS (MinT) | Optimal least squares | Unbiased, uses all levels | Assumes equal variance | Quick optimal baseline |
| WLS (MinT) | Weighted least squares | Accounts for different variances | Needs variance estimates | Variance differs by level |
| MinT (shrunk) | Shrinkage estimator for covariance | Handles many series | Approximation | 100–10k series |
| ERM | Empirical risk minimization | Robust, data-driven | Needs more data | Grouped hierarchies |

---

## Operational Patterns

### Pattern 1: Hierarchy Definition

- **Use when:** Setting up any hierarchical forecast
- **Implementation:**

```python
# Example: Product hierarchy
# Total → Category → Subcategory → SKU
#
# Summing matrix S maps bottom level to all levels:
# [Total]         = [1 1 1 1 1 1] @ [SKU1..SKU6]
# [Category A]    = [1 1 1 0 0 0]
# [Category B]    = [0 0 0 1 1 1]
# [SubCat A1]     = [1 1 0 0 0 0]
# [SubCat A2]     = [0 0 1 0 0 0]
# [SubCat B1]     = [0 0 0 1 1 0]
# [SubCat B2]     = [0 0 0 0 0 1]
# [SKU 1..6]      = I (identity)

import numpy as np
import pandas as pd

# Define hierarchy tags
hierarchy_df = pd.DataFrame({
    'sku': ['SKU1', 'SKU2', 'SKU3', 'SKU4', 'SKU5', 'SKU6'],
    'subcategory': ['A1', 'A1', 'A2', 'B1', 'B1', 'B2'],
    'category': ['A', 'A', 'A', 'B', 'B', 'B'],
})
```

### Pattern 2: Bottom-Up with statsforecast + hierarchicalforecast

- **Use when:** Reliable bottom-level data, simple hierarchy

```python
from statsforecast import StatsForecast
from statsforecast.models import AutoETS, AutoARIMA
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.methods import BottomUp, MinTrace

# Prepare data in long format with hierarchy columns
# Required columns: unique_id, ds (date), y (value)

# Step 1: Generate base forecasts at all levels
sf = StatsForecast(
    models=[AutoETS(season_length=12)],
    freq='M',
    n_jobs=-1,
)
base_forecasts = sf.forecast(h=12)

# Step 2: Reconcile
reconciler = HierarchicalReconciliation(
    reconcilers=[
        BottomUp(),
        MinTrace(method='mint_shrink'),
    ]
)
reconciled = reconciler.reconcile(
    Y_hat_df=base_forecasts,
    Y_df=train_df,
    S=summing_matrix,
    tags=hierarchy_tags,
)
```

### Pattern 3: MinT Optimal Reconciliation

- **Use when:** Want statistically optimal coherent forecasts
- **Implementation:**

```python
from hierarchicalforecast.methods import MinTrace

# Method options for covariance estimation:
# 'ols'          — identity covariance (equal weights)
# 'wls_struct'   — structural scaling (by level)
# 'wls_var'      — variance scaling (from residuals)
# 'mint_shrink'  — shrinkage estimator (recommended default)
# 'mint_cov'     — full sample covariance (small hierarchies only)

reconciler = HierarchicalReconciliation(
    reconcilers=[
        MinTrace(method='mint_shrink'),  # best general choice
    ]
)

# For grouped time series (product x region):
# Use the same approach but define grouped summing matrix
```

- **Covariance method selection:**

| Method | Series Count | Accuracy | Computation |
|--------|-------------|----------|-------------|
| `mint_cov` | < 50 | Highest | Fast |
| `mint_shrink` | 50–5,000 | High | Moderate |
| `wls_var` | 5,000–50,000 | Good | Fast |
| `wls_struct` | Any | Decent | Fastest |
| `ols` | Any | Baseline | Fastest |

### Pattern 4: Grouped Hierarchies (Product x Region)

- **Use when:** Multiple hierarchy dimensions that cross (not just nested)

```python
# Grouped hierarchy example:
# Total → {Product A, Product B} × {Region East, Region West}
#
# This is NOT a tree — it's a cross-product.
# Each combination must be forecasted.

# Define tags for grouped hierarchy
tags = {
    'total': train_df['unique_id'].unique().tolist(),
    'product': ['Product_A', 'Product_B'],
    'region': ['East', 'West'],
    'product_region': ['A_East', 'A_West', 'B_East', 'B_West'],
}

# hierarchicalforecast handles grouped structures natively
# MinTrace with shrinkage is recommended for grouped hierarchies
```

### Pattern 5: Temporal Aggregation

- **Use when:** Need coherent forecasts across time granularities (daily, weekly, monthly)
- **Concept:** Forecasts at different temporal granularities should be consistent

```python
# Temporal hierarchy: daily → weekly → monthly → quarterly
# Use temporal reconciliation to ensure:
#   sum(daily forecasts in week) = weekly forecast
#   sum(weekly in month) = monthly forecast

# Implementation with FoReco (R) or custom:
def temporal_bottom_up(daily_forecasts, freq_map):
    """Aggregate daily forecasts to higher frequencies."""
    weekly = daily_forecasts.resample('W').sum()
    monthly = daily_forecasts.resample('M').sum()
    quarterly = daily_forecasts.resample('Q').sum()
    return {'D': daily_forecasts, 'W': weekly, 'M': monthly, 'Q': quarterly}

# For optimal temporal reconciliation:
# Forecast at each temporal level independently
# Then reconcile using MinT across temporal aggregation matrix
```

### Pattern 6: Evaluation Across Hierarchy Levels

- **Use when:** Always — evaluate at each level, not just aggregate

```python
from hierarchicalforecast.evaluation import HierarchicalEvaluation

def evaluate_hierarchy(actual, forecasted, hierarchy_tags):
    """Evaluate forecast accuracy at each hierarchy level."""
    results = {}
    for level, series_ids in hierarchy_tags.items():
        level_actual = actual[actual['unique_id'].isin(series_ids)]
        level_forecast = forecasted[forecasted['unique_id'].isin(series_ids)]

        # MASE (scale-independent, preferred for hierarchical)
        mase = compute_mase(level_actual, level_forecast)
        # RMSSE
        rmsse = compute_rmsse(level_actual, level_forecast)

        results[level] = {'MASE': mase, 'RMSSE': rmsse}

    return pd.DataFrame(results).T

# Key metrics for hierarchical evaluation:
# - MASE: scale-free, comparable across levels
# - RMSSE: used in M5 competition
# - Coherence error: sum(bottom) - top (should be ~0 after reconciliation)
```

---

## Coherence Verification

```python
def check_coherence(forecasts, summing_matrix, tolerance=1e-6):
    """Verify that reconciled forecasts are coherent."""
    bottom_level = forecasts.iloc[-summing_matrix.shape[1]:]
    reconstructed = summing_matrix @ bottom_level.values

    all_levels = forecasts.values
    max_error = np.abs(all_levels - reconstructed).max()

    is_coherent = max_error < tolerance
    return is_coherent, max_error

# Run after every reconciliation
coherent, error = check_coherence(reconciled, S)
assert coherent, f"Incoherent forecasts: max error = {error}"
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Forecasting only at top level and disaggregating | Loses bottom-level patterns and dynamics | Forecast all levels, then reconcile |
| Bottom-up without checking bottom data quality | Noisy bottom series compound upward | Audit bottom-level data; consider middle-out |
| MinT with full covariance on >200 series | Covariance matrix is singular or poorly estimated | Use `mint_shrink` or `wls_var` |
| Ignoring grouped structure | Treating product x region as simple nesting | Use grouped reconciliation (not tree) |
| Evaluating only at top level | Reconciliation can improve top while degrading bottom | Evaluate at every level |
| Not checking coherence post-reconciliation | Implementation bugs cause incoherent forecasts | Always run coherence check |
| Using proportions from stale history | Proportions shift over time | Use recent proportions or MinT |
| Same model for all series | Different levels may need different models | Fit appropriate model per level |
| Temporal aggregation without reconciliation | Daily, weekly, monthly forecasts contradict each other | Apply temporal reconciliation |
| Reconciling without base forecast residuals | MinT needs residuals for covariance estimation | Store residuals from base forecast step |

---

## Validation Checklist

- [ ] Hierarchy structure defined and summing matrix verified
- [ ] Base forecasts generated at all levels independently
- [ ] Reconciliation method chosen based on hierarchy size and quality
- [ ] Coherence verified post-reconciliation (sum check)
- [ ] Accuracy evaluated at every hierarchy level (not just top)
- [ ] Proportions or covariances updated with recent data
- [ ] Grouped hierarchies handled with cross-product structure
- [ ] New series / discontinued series handled in hierarchy updates
- [ ] Temporal coherence checked if multiple frequencies used
- [ ] Reconciliation improves (or at least doesn't degrade) vs base forecasts

---

## Cross-References

- `ai-ml-timeseries/references/probabilistic-forecasting.md` — coherent prediction intervals across hierarchy
- `ai-ml-timeseries/references/anomaly-detection-patterns.md` — detecting anomalies at different hierarchy levels
- `ai-mlops/references/automated-retraining-patterns.md` — scheduling hierarchy reconciliation in pipelines
- `ai-mlops/references/experiment-tracking-patterns.md` — logging per-level accuracy metrics
