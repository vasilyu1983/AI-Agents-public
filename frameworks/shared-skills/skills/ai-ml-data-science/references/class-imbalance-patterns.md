# Class Imbalance Patterns

> Operational guide for handling imbalanced datasets in classification tasks. Covers sampling strategies, loss reweighting, threshold tuning, and evaluation metrics that actually reflect minority-class performance.

**Freshness anchor:** January 2026 — imbalanced-learn 0.12+, scikit-learn 1.5+, LightGBM 4.x

---

## Decision Tree: Choosing an Imbalance Strategy

```
START
│
├─ Imbalance ratio < 5:1?
│   ├─ YES → Class weights usually sufficient
│   │         └─ Try `class_weight='balanced'` first
│   └─ NO → Continue
│
├─ Imbalance ratio 5:1 – 50:1?
│   ├─ Dataset > 50k rows?
│   │   ├─ YES → Undersampling + ensemble (EasyEnsemble, BalancedRF)
│   │   └─ NO  → SMOTE or ADASYN oversampling
│   └─ Tree-based model?
│       ├─ YES → `scale_pos_weight` or `is_unbalance` first
│       └─ NO  → Sampling + class weights combined
│
├─ Imbalance ratio > 50:1?
│   ├─ Anomaly detection framing viable?
│   │   ├─ YES → Switch to One-Class SVM / Isolation Forest
│   │   └─ NO  → Hybrid sampling + cost-sensitive learning
│   └─ Sufficient minority samples (>500)?
│       ├─ YES → SMOTE + Tomek links cleanup
│       └─ NO  → Data collection > algorithmic tricks
│
└─ Always: tune decision threshold via PR curve, not default 0.5
```

---

## Quick Reference: Sampling Methods

| Method | Type | Use When | Pitfall |
|--------|------|----------|---------|
| Random oversampling | Over | Quick baseline, < 10k rows | Overfitting on duplicates |
| SMOTE | Over | Continuous features, ratio 5:1–50:1 | Noisy with high dimensionality |
| ADASYN | Over | Hard minority examples matter | Amplifies noise near boundary |
| BorderlineSMOTE | Over | Decision boundary is key | Slower than vanilla SMOTE |
| Random undersampling | Under | Large dataset (>100k), fast iteration | Loses majority-class information |
| Tomek links | Under | Cleaning noisy boundary | Removes too few samples alone |
| NearMiss-1 | Under | Want majority near minority | Aggressive — validate carefully |
| NearMiss-3 | Under | Moderate cleaning | Better than NearMiss-1 for most cases |
| SMOTE + Tomek | Hybrid | Best general-purpose combo | Two-step tuning required |
| SMOTE + ENN | Hybrid | Cleaner boundaries than SMOTE+Tomek | More aggressive cleaning |

---

## Operational Patterns

### Pattern 1: Class Weights (Simplest First)

- **Use when:** Imbalance ratio < 10:1, tree-based or linear model
- **Implementation:**

```python
# scikit-learn
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(class_weight='balanced', n_estimators=300)

# LightGBM — two options
params_a = {'is_unbalance': True}  # auto-computes weight
params_b = {'scale_pos_weight': neg_count / pos_count}  # manual

# XGBoost
params_xgb = {'scale_pos_weight': neg_count / pos_count}
```

- **Validation:** compare PR-AUC with and without weights
- **Gotcha:** `class_weight='balanced'` uses `n_samples / (n_classes * class_counts)` — verify the math matches your expectations

### Pattern 2: SMOTE Oversampling

- **Use when:** Dataset 1k–50k rows, continuous features, ratio 5:1–100:1
- **Implementation:**

```python
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

pipeline = ImbPipeline([
    ('smote', SMOTE(
        sampling_strategy=0.5,  # target minority:majority ratio
        k_neighbors=5,          # lower for very small minorities
        random_state=42
    )),
    ('clf', RandomForestClassifier(n_estimators=300))
])

# CRITICAL: SMOTE inside CV, never before split
from sklearn.model_selection import cross_val_score
scores = cross_val_score(pipeline, X, y, cv=5, scoring='average_precision')
```

- **Key rule:** NEVER apply SMOTE before train/test split — causes data leakage
- **k_neighbors tuning:** if minority class < 20 samples, set `k_neighbors=3` or lower

### Pattern 3: Undersampling with Ensembles

- **Use when:** Large dataset (>50k rows), need fast training
- **Implementation:**

```python
from imblearn.ensemble import BalancedRandomForestClassifier
from imblearn.ensemble import EasyEnsembleClassifier

# Option A: Balanced Random Forest
brf = BalancedRandomForestClassifier(
    n_estimators=300,
    sampling_strategy='all',
    replacement=False,
    random_state=42
)

# Option B: EasyEnsemble (AdaBoost on balanced subsets)
ee = EasyEnsembleClassifier(
    n_estimators=20,
    random_state=42
)
```

- **Advantage:** retains all minority samples, subsamples majority per tree
- **Gotcha:** BalancedRF can be slower than regular RF due to resampling overhead

### Pattern 4: Threshold Tuning via PR Curve

- **Use when:** Always — default 0.5 threshold is almost never optimal for imbalanced data
- **Implementation:**

```python
from sklearn.metrics import precision_recall_curve
import numpy as np

y_proba = clf.predict_proba(X_test)[:, 1]
precision, recall, thresholds = precision_recall_curve(y_test, y_proba)

# F1-optimal threshold
f1_scores = 2 * (precision * recall) / (precision + recall + 1e-8)
best_idx = np.argmax(f1_scores)
best_threshold = thresholds[best_idx]

# F-beta for recall-heavy use cases (e.g., fraud)
beta = 2
fbeta = (1 + beta**2) * (precision * recall) / (beta**2 * precision + recall + 1e-8)
best_threshold_fbeta = thresholds[np.argmax(fbeta)]
```

- **Business alignment:** choose beta based on cost of FN vs FP
  - `beta=2` — missing positives is 4x worse than false alarms (fraud, medical)
  - `beta=0.5` — false alarms are 4x worse than misses (spam, content moderation)

### Pattern 5: Cost-Sensitive Learning

- **Use when:** Business has explicit cost matrix (cost of FN != cost of FP)
- **Implementation:**

```python
# Custom sample weights reflecting business cost
sample_weights = np.where(y_train == 1, cost_fn, cost_fp)
clf.fit(X_train, y_train, sample_weight=sample_weights)

# For LightGBM: per-instance weighting
train_data = lgb.Dataset(X_train, label=y_train, weight=sample_weights)
```

- **Cost matrix example:**

| | Predicted Positive | Predicted Negative |
|---|---|---|
| Actual Positive | 0 (TP) | $500 (FN — missed fraud) |
| Actual Negative | $10 (FP — investigation cost) | 0 (TN) |

- Weight ratio: `cost_fn / cost_fp = 50` → use as `scale_pos_weight`

### Pattern 6: Hybrid Sampling

- **Use when:** Ratio > 20:1, need clean decision boundaries
- **Implementation:**

```python
from imblearn.combine import SMOTETomek, SMOTEENN

# SMOTE + Tomek (moderate cleanup)
smt = SMOTETomek(
    smote=SMOTE(sampling_strategy=0.5, k_neighbors=5),
    random_state=42
)

# SMOTE + ENN (aggressive cleanup — better boundaries, fewer samples)
smenn = SMOTEENN(
    smote=SMOTE(sampling_strategy=0.5, k_neighbors=5),
    random_state=42
)
```

---

## Evaluation Metrics for Imbalanced Data

### Metrics Decision Table

| Metric | Use When | Do NOT Use When |
|--------|----------|-----------------|
| **PR-AUC** | Primary metric for imbalanced data | Balanced datasets |
| **F1** | Need single threshold, equal FP/FN cost | Costs are asymmetric |
| **F-beta** | Asymmetric FP/FN costs | Costs are equal |
| **MCC** | Want single metric accounting for all quadrants | Need threshold-free metric |
| **ROC-AUC** | Comparing models (not evaluating performance) | Severe imbalance (>100:1) — misleading |
| **Accuracy** | NEVER for imbalanced data | Always — it lies |
| **Cohen's Kappa** | Comparing to random baseline | Need interpretable business metric |

### Metric Implementation

```python
from sklearn.metrics import (
    average_precision_score,  # PR-AUC
    f1_score,
    fbeta_score,
    matthews_corrcoef,        # MCC
    classification_report
)

y_proba = clf.predict_proba(X_test)[:, 1]
y_pred = (y_proba >= best_threshold).astype(int)

metrics = {
    'PR-AUC': average_precision_score(y_test, y_proba),
    'F1': f1_score(y_test, y_pred),
    'F2': fbeta_score(y_test, y_pred, beta=2),
    'MCC': matthews_corrcoef(y_test, y_pred),
}
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Applying SMOTE before train/test split | Data leakage — synthetic samples bleed into test set | Use `imblearn.pipeline.Pipeline` inside CV |
| Using accuracy as primary metric | 99% accuracy with 99:1 ratio means predicting all majority | Switch to PR-AUC or F-beta |
| Using ROC-AUC as sole metric at >50:1 ratio | ROC-AUC inflated by easy TN predictions | Use PR-AUC instead |
| Oversampling to 1:1 ratio | Overfitting + slow training | Target 0.3–0.5 ratio with `sampling_strategy` |
| SMOTE on categorical features | SMOTE interpolates — meaningless for categories | Use SMOTENC or encode first |
| SMOTE on high-dimensional sparse data | Generates noisy synthetic points in sparse space | Reduce dimensions first, then SMOTE |
| Ignoring threshold tuning | Default 0.5 wastes model capability | Always tune via PR curve |
| Resampling test set | Evaluation on resampled test is meaningless | ONLY resample training data |
| Using NearMiss without validation | NearMiss can destroy useful majority patterns | Compare holdout performance with/without |
| Combining multiple strategies blindly | Stacking SMOTE + weights + threshold = unpredictable | Add one technique at a time, measure impact |

---

## Validation Checklist

- [ ] Imbalance ratio measured and documented
- [ ] Baseline established with no correction (to measure improvement)
- [ ] Sampling applied ONLY inside cross-validation folds
- [ ] Test set left untouched (original distribution)
- [ ] PR-AUC or F-beta used as primary metric (NOT accuracy or ROC-AUC)
- [ ] Decision threshold tuned on validation set, evaluated on test set
- [ ] Confusion matrix reviewed at chosen threshold
- [ ] Business cost alignment verified (FN cost vs FP cost)
- [ ] Stratified splits used (`StratifiedKFold`)
- [ ] Results stable across multiple random seeds

---

## Cross-References

- `ai-ml-data-science/references/hyperparameter-optimization.md` — tuning `scale_pos_weight` and sampling params
- `ai-ml-data-science/references/interpretability-explainability.md` — explaining minority-class predictions
- `ai-mlops/references/automated-retraining-patterns.md` — monitoring class distribution drift
- `ai-mlops/references/experiment-tracking-patterns.md` — logging imbalance metrics per run
