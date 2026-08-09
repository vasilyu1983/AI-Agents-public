# Interpretability and Explainability

> Operational guide for explaining ML model predictions. Covers SHAP, LIME, permutation importance, partial dependence, and audience-appropriate communication of model behavior. Focus on actionable interpretation, not theory.

**Freshness anchor:** verified 2026-07-11 — SHAP 0.52+ (requires Python >=3.12), LIME 0.2+, scikit-learn 1.9+, LightGBM 4.6+. SHAP 0.45.0 changed multi-output `shap_values()` return type from a Python list to a single `np.ndarray` — see the Pattern 1 gotcha below before indexing with `shap_values[1]`.

---
## Table of Contents

- [Decision Tree: Choosing an Explanation Method](#decision-tree-choosing-an-explanation-method)
- [Quick Reference: Methods Comparison](#quick-reference-methods-comparison)
- [Operational Patterns](#operational-patterns)
- [Pattern 1: TreeSHAP for Tree-Based Models](#pattern-1-treeshap-for-tree-based-models)
- [Train model](#train-model)
- [Create explainer (auto-detects tree type)](#create-explainer-auto-detects-tree-type)
- [For binary classification: shap_values is [neg_class, pos_class]](#for-binary-classification-shapvalues-is-negclass-posclass)
- [Use shap_values[1] for positive class explanations](#use-shapvalues1-for-positive-class-explanations)
- [Global: Summary plot (feature importance + distribution)](#global-summary-plot-feature-importance-distribution)
- [Global: Bar plot (mean absolute SHAP per feature)](#global-bar-plot-mean-absolute-shap-per-feature)
- [Local: Single prediction waterfall](#local-single-prediction-waterfall)
- [Pattern 2: KernelSHAP for Black-Box Models](#pattern-2-kernelshap-for-black-box-models)
- [Background data: use k-means summary for speed](#background-data-use-k-means-summary-for-speed)
- [Compute on subset (KernelSHAP is slow)](#compute-on-subset-kernelshap-is-slow)
- [Pattern 3: LIME for Quick Local Explanations](#pattern-3-lime-for-quick-local-explanations)
- [Explain single prediction](#explain-single-prediction)
- [Or export: exp.as_html(), exp.as_list()](#or-export-expashtml-expaslist)
- [Pattern 4: Permutation Importance](#pattern-4-permutation-importance)
- [Sort by importance](#sort-by-importance)
- [Pattern 5: Partial Dependence and ICE Plots](#pattern-5-partial-dependence-and-ice-plots)
- [PDP for top features](#pdp-for-top-features)
- [Pattern 6: Feature Importance Stability Analysis](#pattern-6-feature-importance-stability-analysis)
- [Bootstrap SHAP importance stability](#bootstrap-shap-importance-stability)
- [Compute rank stability per feature](#compute-rank-stability-per-feature)
- [> 0.9 = stable rankings; < 0.7 = unstable, report with caveats](#09-=-stable-rankings-07-=-unstable-report-with-caveats)
- [Audience-Appropriate Explanations](#audience-appropriate-explanations)
- [Technical Audience (Data Scientists)](#technical-audience-data-scientists)
- [Business Stakeholders](#business-stakeholders)
- [Regulatory / Audit](#regulatory-audit)
- [Model Explanation Report](#model-explanation-report)
- [Anti-Patterns](#anti-patterns)
- [Model Card Template (Interpretability Section)](#model-card-template-interpretability-section)
- [Interpretability](#interpretability)
- [Explanation Method](#explanation-method)
- [Top Features (Stable)](#top-features-stable)
- [Stability](#stability)
- [Limitations](#limitations)
- [Validation Checklist](#validation-checklist)
- [Cross-References](#cross-references)


## Decision Tree: Choosing an Explanation Method

```
START
│
├─ Model type?
│   ├─ Tree-based (LightGBM, XGBoost, RF, CatBoost)
│   │   └─ Use TreeSHAP (exact, fast, O(TLD))
│   │
│   ├─ Linear (LogisticRegression, Lasso, Ridge)
│   │   └─ Use LinearSHAP or direct coefficient interpretation
│   │
│   ├─ Neural network
│   │   ├─ Tabular → KernelSHAP (slow) or DeepSHAP
│   │   └─ Image/text → GradientSHAP, Integrated Gradients
│   │
│   └─ Black-box / API-only
│       └─ KernelSHAP or LIME (model-agnostic)
│
├─ Explanation scope?
│   ├─ Global (overall model behavior)
│   │   ├─ Feature importance ranking → SHAP summary plot
│   │   ├─ Feature effect curves → PDP or SHAP dependence
│   │   └─ Feature interactions → SHAP interaction values
│   │
│   └─ Local (single prediction)
│       ├─ Detailed breakdown → SHAP waterfall
│       ├─ Quick approximation → LIME
│       └─ Contrastive ("why not X?") → SHAP force plot
│
└─ Audience?
    ├─ Data scientist → Full SHAP values, interaction plots
    ├─ Business stakeholder → Top 3 drivers, bar charts
    └─ Regulatory / audit → Model cards, stability analysis
```

---

## Quick Reference: Methods Comparison

| Method | Scope | Speed (10k rows) | Consistency | Model Types |
|--------|-------|-------------------|-------------|-------------|
| TreeSHAP | Global + Local | < 1 min | Exact | Tree ensembles only |
| KernelSHAP | Global + Local | 10–60 min | Approximate | Any model |
| DeepSHAP | Global + Local | 2–10 min | Approximate | Neural networks |
| LIME | Local only | ~1 sec/instance | Unstable across runs | Any model |
| Permutation Importance | Global only | 1–5 min | Stable with enough reps | Any model |
| PDP | Global only | 1–5 min | Exact (for model) | Any model |
| ICE Plots | Local curves | 1–5 min | Exact (for model) | Any model |

---

## Operational Patterns

### Pattern 1: TreeSHAP for Tree-Based Models

- **Use when:** Using LightGBM, XGBoost, CatBoost, RandomForest
- **Implementation:**

```python
import shap

# Train model
model = lgb.LGBMClassifier(**params).fit(X_train, y_train)

# Create explainer (auto-detects tree type)
explainer = shap.TreeExplainer(model)
explanation = explainer(X_test)  # returns a shap.Explanation, not a raw array/list

# Global: Summary plot (feature importance + distribution)
shap.summary_plot(explanation)

# Global: Bar plot (mean absolute SHAP per feature)
shap.plots.bar(explanation)

# Local: Single prediction waterfall
shap.plots.waterfall(explanation[0])
```

- **Version gotcha (verify against your installed SHAP version before trusting older tutorials):** the old pattern `shap_values = explainer.shap_values(X_test); shap_values[1]` assumed multi-output classification always returned a Python list indexed by class. As of SHAP 0.45.0, `shap_values()` for multi-output/scikit-learn-style classifiers returns a single `np.ndarray` of shape `(n_samples, n_features, n_classes)` instead — `shap_values[1]` on that array now selects **sample 1**, not the positive class, and silently produces a wrong explanation with no error. For binary classification, index the last axis (`shap_values[..., 1]`) or, better, use the modern `explainer(X)` call shown above, which always returns a `shap.Explanation` object with `.values`/`.base_values` regardless of model type. LightGBM/XGBoost with the default raw-margin output instead return a plain `(n_samples, n_features)` array with no class axis at all — check `.shape` before indexing rather than assuming a fixed convention.
- **Performance tip:** For large datasets, compute SHAP on a representative sample (5k–10k rows)
- **Gotcha:** TreeSHAP with `feature_perturbation='interventional'` gives causal-style attribution but requires background data

### Pattern 2: KernelSHAP for Black-Box Models

- **Use when:** Model is an API, neural network, or ensemble of mixed types
- **Implementation:**

```python
# Background data: use k-means summary for speed
background = shap.kmeans(X_train, 100)

explainer = shap.KernelExplainer(model.predict_proba, background)

# Compute on subset (KernelSHAP is slow)
shap_values = explainer.shap_values(X_test[:500], nsamples=500)
```

- **Speed tradeoff:** `nsamples` controls accuracy vs speed
  - `nsamples=100` — fast, rough approximation
  - `nsamples=500` — good balance
  - `nsamples=2048` — high accuracy, slow

### Pattern 3: LIME for Quick Local Explanations

- **Use when:** Need fast, single-prediction explanation for stakeholders
- **Implementation:**

```python
from lime.lime_tabular import LimeTabularExplainer

lime_exp = LimeTabularExplainer(
    training_data=X_train.values,
    feature_names=X_train.columns.tolist(),
    class_names=['Negative', 'Positive'],
    mode='classification',
    discretize_continuous=True,
)

# Explain single prediction
exp = lime_exp.explain_instance(
    X_test.iloc[0].values,
    model.predict_proba,
    num_features=10,
    num_samples=5000,
)

exp.show_in_notebook()
# Or export: exp.as_html(), exp.as_list()
```

- **Stability check:** Run LIME 5 times on same instance — if top features change, results are unreliable
- **Gotcha:** LIME fits a local linear model — fails for highly non-linear local behavior

### Pattern 4: Permutation Importance

- **Use when:** Need global feature ranking, model-agnostic, simple to explain
- **Implementation:**

```python
from sklearn.inspection import permutation_importance

result = permutation_importance(
    model, X_test, y_test,
    n_repeats=30,
    random_state=42,
    scoring='average_precision',
    n_jobs=-1,
)

# Sort by importance
sorted_idx = result.importances_mean.argsort()[::-1]
for idx in sorted_idx[:15]:
    print(f"{X_test.columns[idx]:30s}: "
          f"{result.importances_mean[idx]:.4f} +/- {result.importances_std[idx]:.4f}")
```

- **Key advantage:** Measures importance on unseen data (test set) — avoids overfitting bias
- **Gotcha:** Correlated features split importance — consider grouping correlated features

### Pattern 5: Partial Dependence and ICE Plots

- **Use when:** Need to show how a feature affects predictions across its range
- **Implementation:**

```python
from sklearn.inspection import PartialDependenceDisplay

# PDP for top features
features = ['age', 'income', ('age', 'income')]  # single + interaction
PartialDependenceDisplay.from_estimator(
    model, X_train, features,
    kind='both',      # PDP (average) + ICE (individual)
    subsample=500,    # ICE lines to plot
    grid_resolution=50,
    n_jobs=-1,
)
```

- **PDP vs ICE:**
  - PDP = average effect (can hide heterogeneity)
  - ICE = individual curves (reveals subgroups with different effects)
- **Always plot both** — if ICE lines are parallel, PDP is reliable; if they cross, PDP is misleading

### Pattern 6: Feature Importance Stability Analysis

- **Use when:** Regulatory or audit context, need confidence in feature rankings
- **Implementation:**

```python
import numpy as np

# Bootstrap SHAP importance stability
n_bootstrap = 20
importance_ranks = []

for i in range(n_bootstrap):
    sample_idx = np.random.choice(len(X_test), size=len(X_test), replace=True)
    X_sample = X_test.iloc[sample_idx]
    exp_sample = explainer(X_sample)  # shap.Explanation; check exp_sample.values.shape once, don't assume

    # exp_sample.values.shape is (n_samples, n_features, n_classes) for scikit-learn-style
    # binary classifiers, or (n_samples, n_features) for raw-margin LightGBM/XGBoost — branch on it
    vals = exp_sample.values[..., 1] if exp_sample.values.ndim == 3 else exp_sample.values
    mean_abs = np.abs(vals).mean(axis=0)
    ranks = np.argsort(-mean_abs)  # descending
    importance_ranks.append(ranks)

# Compute rank stability per feature
from scipy.stats import kendalltau
stability_scores = []
for i in range(n_bootstrap):
    for j in range(i+1, n_bootstrap):
        tau, _ = kendalltau(importance_ranks[i], importance_ranks[j])
        stability_scores.append(tau)

print(f"Mean rank correlation: {np.mean(stability_scores):.3f}")
# > 0.9 = stable rankings; < 0.7 = unstable, report with caveats
```

---

## Audience-Appropriate Explanations

### Technical Audience (Data Scientists)

- Full SHAP summary plots with distributions
- Interaction values and dependence plots
- Permutation importance with confidence intervals
- Raw SHAP values for downstream analysis

### Business Stakeholders

- Top 3–5 drivers as horizontal bar chart
- Natural language: "This customer was flagged primarily because their account age (2 months) is unusually short, and their transaction frequency (47/day) is 5x the average"
- Avoid: SHAP values, log-odds, probability scores
- Use: directional language ("increases risk", "decreases likelihood")

### Regulatory / Audit

- Model card documenting: features used, protected attributes, fairness metrics
- Stability analysis across bootstrap samples
- Monotonicity checks for regulated features
- Feature importance consistency across time periods
- Documentation template:

```markdown
## Model Explanation Report
- Model type: [type]
- Training date: [date]
- Explanation method: [TreeSHAP/KernelSHAP]
- Top 10 features (stable across 20 bootstrap runs): [list]
- Protected attribute impact: [analysis]
- Monotonicity compliance: [pass/fail per feature]
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Using `model.feature_importances_` as primary explanation | Biased toward high-cardinality features (Gini/split-based) | Use SHAP or permutation importance |
| LIME without stability check | LIME explanations change across runs | Run 5x, report only stable features |
| SHAP on entire dataset (500k+ rows) | Slow and unnecessary | Sample 5k–10k representative rows |
| Showing raw SHAP values to business users | Not interpretable without context | Translate to "increases/decreases" language |
| PDP without ICE overlay | Hides heterogeneous effects | Always use `kind='both'` |
| Permutation importance on training data | Overfitting inflates importance | Always compute on test/holdout set |
| Confusing feature importance with causation | Correlation != causation | Explicitly state "predictive importance, not causal" |
| Single explanation method | Each has blind spots | Use 2+ methods, check agreement |
| Ignoring correlated features | SHAP splits importance among correlated features | Group correlated features or note caveat |
| KernelSHAP with too few nsamples | Noisy, unreliable attributions | Minimum nsamples=500 for production use |

---

## Model Card Template (Interpretability Section)

```markdown
## Interpretability

### Explanation Method
- Primary: TreeSHAP (exact for tree ensemble)
- Secondary: Permutation importance (validation)

### Top Features (Stable)
| Rank | Feature | Mean |SHAP| | Direction |
|------|---------|-------------|-----------|
| 1    | [name]  | [value]     | [+/-]     |

### Stability
- Bootstrap rank correlation (Kendall tau): [value]
- Feature ranking consistent across [N] time periods: [yes/no]

### Limitations
- [Correlated feature groups]
- [Non-monotonic relationships]
- [Protected attribute interactions]
```

---

## Validation Checklist

- [ ] Explanation method matches model type (TreeSHAP for trees, etc.)
- [ ] SHAP values computed on representative sample (not full dataset unless small)
- [ ] Feature importance stable across bootstrap samples (tau > 0.8)
- [ ] Permutation importance confirms SHAP rankings (top 5 agree)
- [ ] PDP/ICE plots reviewed for non-linear effects and interactions
- [ ] Business-appropriate summary prepared (top drivers, directional language)
- [ ] Model card updated with interpretability section
- [ ] No causal claims made from correlational analysis
- [ ] Protected attributes checked for disproportionate importance

---

## Cross-References

- `ai-ml-data-science/references/class-imbalance-patterns.md` — interpreting minority-class predictions
- `ai-ml-data-science/references/hyperparameter-optimization.md` — feature importance after tuning
- `ai-mlops/references/experiment-tracking-patterns.md` — logging SHAP artifacts
- `ai-rag/references/embedding-model-guide.md` — explaining embedding-based features
