# Modelling Patterns

Operational modelling techniques, baseline-first workflows, split design, and model-family comparison rules for practical DS work.

---
## Table of Contents

- [1. Model Selection & Baselines (Practical Starting Points)](#1-model-selection-&-baselines-practical-starting-points)
- [1.1 Decision Guide](#11-decision-guide)
- [1.2 Baseline First Pattern](#12-baseline-first-pattern)
- [2. Train/Validation/Test Split Design](#2-trainvalidationtest-split-design)
- [2.1 Split Strategies](#21-split-strategies)
- [2.2 Common Pitfalls](#22-common-pitfalls)
- [2.3 Recommended Ratios](#23-recommended-ratios)
- [3. Model Family Selection](#3-model-family-selection)
- [3.1 Tabular Data](#31-tabular-data)
- [3.2 Text Data](#32-text-data)
- [3.3 When to Avoid Deep Models](#33-when-to-avoid-deep-models)
- [4. Hyperparameter Tuning](#4-hyperparameter-tuning)
- [4.1 Tuning Strategy](#41-tuning-strategy)
- [4.2 Key Parameters by Model](#42-key-parameters-by-model)
- [4.3 Stability and Reproducibility](#43-stability-and-reproducibility)
- [5. Overfitting Control](#5-overfitting-control)
- [5.1 Detection](#51-detection)
- [5.2 Mitigation Techniques](#52-mitigation-techniques)
- [6. CatBoost for Categorical-Heavy Data](#6-catboost-for-categorical-heavy-data)
- [6.1 When to Choose CatBoost](#61-when-to-choose-catboost)
- [6.2 CatBoost vs LightGBM vs XGBoost](#62-catboost-vs-lightgbm-vs-xgboost)
- [6.3 CatBoost Key Parameters](#63-catboost-key-parameters)
- [7. GPU Scaling for Large Datasets](#7-gpu-scaling-for-large-datasets)
- [7.1 When to Use GPU Training](#71-when-to-use-gpu-training)
- [7.2 GPU Training with LightGBM](#72-gpu-training-with-lightgbm)
- [7.3 Distributed Training with Ray](#73-distributed-training-with-ray)
- [7.4 XGBoost GPU Training](#74-xgboost-gpu-training)
- [8. Model Comparison](#8-model-comparison)
- [8.1 Fair Comparison Rules](#81-fair-comparison-rules)
- [8.2 Statistical Significance](#82-statistical-significance)
- [9. Thresholding for Classification](#9-thresholding-for-classification)
- [9.1 Threshold Selection](#91-threshold-selection)
- [9.2 Per-Segment Validation](#92-per-segment-validation)


## 1. Model Selection & Baselines (Practical Starting Points)

### 1.1 Decision Guide

Use current tooling and benchmarks as inputs, but keep the recommendation conditional on data shape, latency, interpretability, and team constraints.

| Data shape | Start with | Compare against | Notes |
|------------|------------|-----------------|-------|
| Tabular, small-medium (within a tabular foundation model's current limits) | Linear/logistic baseline, then LightGBM or CatBoost | A tabular foundation model as zero-shot candidate (no tuning required; check its licence) | Boosted trees are usually strong, but not automatic winners; add a tabular FM to the comparison set before tuning — see Section 3.1 |
| Tabular, categorical-heavy | CatBoost and LightGBM | regularized linear model | CatBoost often earns its keep when categorical handling is central |
| Tabular, very large structured data | LightGBM or CatBoost | simpler baseline, sampled baseline, occasionally compact NN | Escalate to neural/tabular-transformer approaches only with evidence |
| High-dimensional sparse text/counts | Regularized linear, NB | shallow tree model, shallow NN | Sparse linear baselines remain hard to beat on speed and interpretability |
| Time-aware tabular events | Leakage-safe baseline, then boosting | calibrated linear model | Use time-safe splits; move to `ai-ml-timeseries` if forecasting is the main problem |
| Mixed modalities | task-specific baseline per modality | late-fusion or specialized encoder | Avoid collapsing everything into one complex model too early |

**Rule:** describe a model family as a **strong baseline** or **good candidate**, not as universally best.

### 1.2 Baseline First Pattern

Always implement simple baselines first:

**Classification:**
- Majority-class classifier
- Stratified random
- Simple rule-based (if domain knowledge available)

**Regression:**
- Mean/median predictor
- Linear regression
- Moving average (for time series)

**Time series:**
- Seasonal naive forecast
- Last-value carry-forward

**Why baselines matter:**
- Establish minimum performance bar
- Reality check for model complexity
- Fast iteration and debugging
- Interpretability reference
- Provide a fallback candidate if the complex model fails calibration, latency, or governance checks

**Expert judgment: when the baseline should win**

A non-expert stops at "the fancier model scored higher." An expert asks what the lift actually costs and whether it survives scrutiny:

- If the complex candidate beats the baseline by less than the run-to-run variance across 3–5 seeds, there is no real winner yet — report it as noise, not progress.
- A 1–2 point metric gain that costs 10x inference latency, loses interpretability required for a regulated decision, or adds a new training dependency is usually not worth shipping — say so explicitly rather than defaulting to "higher number wins."
- Prefer the simpler model whenever the stronger candidate's gain is concentrated in one slice (e.g., one geography or one time window) rather than distributed — concentrated gains are often overfitting to that slice, not genuine generalization.
- When a linear/logistic baseline is within a few points of a boosted-tree candidate on tabular data, that is a signal the feature set is already doing most of the work — investigate the features before reaching for a bigger model.
- Treat "we added a neural net and it helped a little" as a red flag on small-to-medium tabular data (<50k rows): the more likely explanation is variance or leakage, not a genuine capacity advantage. Re-check the split and feature pipeline before concluding the neural net is the reason.

**Checklist: Baselines**

- [ ] Simple baseline implemented (majority class, mean, naive forecast)
- [ ] At least one simple baseline compared against one strong structured-data candidate
- [ ] Complexity added only after baselines understood
- [ ] Compute, latency, and explainability constraints considered early
- [ ] Model performance logged in experiment tracker (MLflow/W&B)

---

## 2. Train/Validation/Test Split Design

### 2.1 Split Strategies

**Random split (IID):**
- Use when: Data is independent and identically distributed
- Pros: Simple, maximizes training data
- Cons: Doesn't test temporal generalization

**Time-based split:**
- Use when: Forecasting or temporal leakage risk
- Pattern: Train on [T0, T1], validate on [T1, T2], test on [T2, T3]
- Pros: Tests realistic deployment scenario
- Cons: Less training data, seasonality may affect splits

**Group-based split:**
- Use when: User/item/entity leakage risk
- Pattern: Split by user_id, never mix same user across sets
- Examples: Recommendation systems, fraud detection
- Pros: Tests generalization to new entities
- Cons: Reduces effective sample size

**Cross-validation:**
- Use when: Small datasets, need robust estimates
- K-fold: 5 or 10 folds typical
- Stratified: Preserve class balance in each fold
- Time-series CV: Rolling/expanding window
- Pros: Better variance estimates, more data usage
- Cons: K times slower, risk of data leakage if not careful

### 2.2 Common Pitfalls

**Leakage:**
- Same entity in train and test (user, transaction)
- Feature computed using test data
- Future information in training

**Imbalance:**
- Rare classes missing from validation/test
- Non-representative splits

**Size:**
- Test set too small for reliable metrics
- Validation set too small for hyperparameter tuning

### 2.3 Recommended Ratios

**Large datasets (>100k samples):**
- Train: 80%, Validation: 10%, Test: 10%

**Medium datasets (10k-100k):**
- Train: 70%, Validation: 15%, Test: 15%

**Small datasets (<10k):**
- Use cross-validation instead of single split
- Hold out 20% for final test

**Checklist: Split Design**

- [ ] Split respects time order when needed
- [ ] No record from same entity in both train and test where leakage matters
- [ ] Test/validation sets held out from all model decisions
- [ ] Evaluation method documented and reproducible
- [ ] Class balance validated in all splits
- [ ] Test set size sufficient for statistical significance

---

## 3. Model Family Selection

### 3.1 Tabular Data

**Usual candidates:**
- LightGBM for fast, strong tabular baselines
- CatBoost when categorical handling is central or encodings are awkward
- XGBoost when the surrounding stack already standardizes on it

**Tabular foundation models (TabPFN family, TabICL):**
- In-context, prior-fitted transformers: one forward pass, no per-dataset hyperparameter tuning. "Trees always win on tabular" (Grinsztajn 2022) no longer holds inside their limits.
- **Size regime is a lookup, not a remembered number.** Row, feature and CPU-sample limits change with each release, trade rows against features (not a flat ceiling), and differ between the recommended range and the hard ceiling. Read the current model card / README before deciding, and note the release you checked in the experiment log.
  - Within the current limits and raw accuracy is the bar: add the FM to the comparison set.
  - Beyond the limits, very wide tables, or a natively inspectable, CPU-cheap model is required: keep LightGBM/CatBoost as defaults.
  - Near the edge of the limits: "worth trying, measure latency and memory," not a safe default.
- **Compare against a tuned boosted-tree model.** Published win rates are usually against *default* (untuned) competitors; do not cite them as "beats tuned XGBoost" without checking the paper's exact setup.
- **Licence gate (check before the bake-off, not after):** read the LICENSE or model card of the exact checkpoint before any evaluation that feeds a commercial decision. Vendor sources disagree across releases: the repository README calls recent TabPFN weights non-commercial, while the TabPFN-3 report calls its licence permissive for research and internal evaluation. Do not assume either way; record the checkpoint and licence version with the result. Production commercial use needs a commercial licence or the vendor API. Using TabPFN or its outputs to train, fine-tune or distill another model for commercial use is not permitted under the default licence. An open FM such as TabICL may avoid this; verify its weight availability and licence too.
- **Distilled export:** a distillation engine can compress a fitted TabPFN into a compact MLP or tree ensemble for low-latency serving. Use it only for non-commercial work or when a commercial licence explicitly covers it; otherwise serve the FM through the licensed API or pick a GBDT/open-weight FM. Verify current tooling support before committing.
- Frame as: add to the comparison set. Do not replace boosted-tree baselines — verify on each problem.

**Linear models:**
- Logistic regression (interpretable baseline)
- Ridge/Lasso (regularized linear)
- Use when: Need interpretability, compliance, or very fast inference

**Neural networks:**
- Consider only when: very large datasets, complex interactions, or strong prior evidence
- Validate against boosted-tree baselines before committing
- TabNet, FT-Transformer, or compact MLPs are experiments, not default answers

### 3.2 Text Data

**Start with:**
- TF-IDF + linear models (fast baseline)
- Pretrained embeddings (Sentence-BERT) + LightGBM

**Advanced:**
- Fine-tuned transformers (BERT, RoBERTa)
- Only when: large labeled dataset, domain mismatch justifies fine-tuning, and inference cost is acceptable

### 3.3 When to Avoid Deep Models

**Don't use neural networks when:**
- Small datasets (<10k samples)
- Highly structured relational data (use tree models)
- Need interpretability for compliance
- Limited compute budget
- The boosted-tree or linear baseline already meets the acceptance threshold

**Checklist: Model Family**

- [ ] Model complexity matches data size
- [ ] Baseline -> interpretable model -> complex model progression
- [ ] Compute and latency constraints considered
- [ ] Interpretability requirements documented
- [ ] Thresholding, calibration, and uncertainty implications considered for the final candidate

---

## 4. Hyperparameter Tuning

### 4.1 Tuning Strategy

**Level 1: Manual scan (fast)**
- Test 3-5 values per key parameter
- Use domain knowledge and defaults
- Time: Minutes to hours

**Level 2: Grid search (thorough)**
- Small grid on important parameters
- Use when: Need reproducibility
- Time: Hours to day

**Level 3: Random search (efficient)**
- Sample random combinations
- Better than grid for high-dimensional spaces
- Time: Hours to day

**Level 4: Bayesian optimization (smart)**
- Use Optuna, Ray Tune, Hyperopt
- Learns from previous trials
- Time: Hours to days

### 4.2 Key Parameters by Model

**LightGBM:**
- `num_leaves` (31-255)
- `learning_rate` (0.01-0.3)
- `min_data_in_leaf` (20-100)
- `feature_fraction` (0.7-1.0)

**XGBoost:**
- `max_depth` (3-10)
- `learning_rate` (0.01-0.3)
- `min_child_weight` (1-10)
- `subsample` (0.7-1.0)

**Neural networks:**
- Learning rate (1e-5 to 1e-2, log scale)
- Batch size (16, 32, 64, 128)
- Dropout rate (0.1-0.5)
- Number of layers (2-6)

### 4.3 Stability and Reproducibility

**Best practices:**
- Set random seeds (model, data split, sampling)
- Run multiple seeds for final model (e.g., 5 seeds)
- Report mean +/- std across seeds
- Log all hyperparameters to experiment tracker

**Checklist: Hyperparameter Tuning**

- [ ] Parameters logged in experiment tracker
- [ ] Seeds logged and controlled
- [ ] Overfitting checked (train vs validation)
- [ ] Multiple runs for stability (3-5 seeds minimum)
- [ ] Best parameters documented with justification

---

## 5. Overfitting Control

### 5.1 Detection

**Indicators of overfitting:**
- Train error decreases while validation error increases
- Large gap between train and validation metrics
- Model performs well on training data but poorly on new data

**Monitoring:**
- Plot train vs validation loss/metric over epochs/iterations
- Check learning curves
- Validate on held-out test set

### 5.2 Mitigation Techniques

**For tree models:**
- Limit `max_depth` (3-10)
- Increase `min_data_in_leaf` / `min_child_weight`
- Reduce `num_leaves`
- Use feature subsampling (`feature_fraction`, `colsample_bytree`)

**For neural networks:**
- Dropout (0.2-0.5)
- L2 regularization (weight decay)
- Early stopping (patience = 5-10 epochs)
- Data augmentation

**For linear models:**
- L1 (Lasso) or L2 (Ridge) regularization
- Reduce number of features (feature selection)

**Universal:**
- Get more training data
- Simplify model architecture
- Cross-validation for robust estimates

**Checklist: Overfitting Control**

- [ ] Train vs validation gap monitored
- [ ] Regularization applied (appropriate to model type)
- [ ] Early stopping configured (if applicable)
- [ ] Learning curves analyzed
- [ ] Test set performance validates generalization

---

## 6. CatBoost for Categorical-Heavy Data

### 6.1 When to Choose CatBoost

CatBoost often outperforms LightGBM/XGBoost when:

- Dataset contains **many categorical features** (>30% of features)
- High-cardinality categoricals (cities, product IDs, user IDs)
- Limited time for feature engineering (native handling reduces preprocessing)
- Need robust defaults with minimal hyperparameter tuning

**Key advantages:**

- **Ordered target encoding**: Prevents target leakage automatically
- **Built-in overfitting detection**: Automatic early stopping
- **GPU support**: Native CUDA implementation for training
- **Symmetric trees**: Better generalization on some datasets

### 6.2 CatBoost vs LightGBM vs XGBoost

| Criterion | LightGBM | XGBoost | CatBoost |
|-----------|----------|---------|----------|
| Categorical handling | Manual (one-hot, target encoding) | Manual | Native (ordered target encoding) |
| Training speed | Fastest | Fast | Moderate |
| Accuracy (general) | Excellent | Excellent | Excellent |
| Accuracy (high-cardinality cats) | Good | Good | Best |
| Hyperparameter sensitivity | Moderate | High | Low |
| GPU support | Yes | Yes | Yes (native CUDA) |

### 6.3 CatBoost Key Parameters

```python
from catboost import CatBoostClassifier

model = CatBoostClassifier(
    iterations=1000,
    learning_rate=0.1,
    depth=6,  # 4-10 typical
    l2_leaf_reg=3,  # L2 regularization
    cat_features=['city', 'product_id', 'category'],  # Specify categorical columns
    early_stopping_rounds=50,
    verbose=100
)
```

**Checklist: CatBoost**

- [ ] Categorical features identified and passed to `cat_features`
- [ ] Compared against LightGBM/XGBoost baseline
- [ ] Early stopping configured
- [ ] GPU enabled for large datasets (`task_type='GPU'`)

---

## 7. GPU Scaling for Large Datasets

### 7.1 When to Use GPU Training

**Indicators:**

- Dataset exceeds 10M+ rows
- Training time >1 hour on CPU
- Need rapid experimentation cycles
- Production requires frequent retraining

Benchmark CPU and GPU training on a representative subset of your own data, with matched boosting rounds and tree depth. Record hardware, feature count, memory and scaling behavior before budgeting a full run; an unattributed billion-row timing is not capacity evidence.

### 7.2 GPU Training with LightGBM

```python
import lightgbm as lgb

# 'cuda' needs a CUDA/ROCm build and is faster than 'gpu' (OpenCL);
# use 'gpu' only when CUDA is unavailable, then set gpu_platform_id from clinfo.
params = {
    'device_type': 'cuda',
    'objective': 'binary',
    'metric': 'auc',
    'num_leaves': 63,
    'learning_rate': 0.05,
    'feature_fraction': 0.8
}

train_data = lgb.Dataset(X_train, label=y_train)
model = lgb.train(params, train_data, num_boost_round=500)
```

### 7.3 Distributed Training with Ray

For datasets that don't fit in memory or require horizontal scaling:

```python
# label_column/params/num_boost_round are the deprecated legacy API; read the
# installed Ray Train LightGBMTrainer page before copying.
import lightgbm as lgb
import ray.train
from ray.train import ScalingConfig
from ray.train.lightgbm import LightGBMTrainer, RayTrainReportCallback, get_network_params

def train_fn(config):
    train = ray.train.get_dataset_shard("train").materialize().to_pandas()
    valid = ray.train.get_dataset_shard("valid").materialize().to_pandas()
    dtrain = lgb.Dataset(train.drop(columns="target"), label=train["target"])
    dvalid = lgb.Dataset(valid.drop(columns="target"), label=valid["target"])
    params = {"objective": "binary", "metric": "auc", "num_leaves": 63, **get_network_params()}
    lgb.train(params, dtrain, valid_sets=[dvalid], valid_names=["valid"],
              callbacks=[RayTrainReportCallback()])

trainer = LightGBMTrainer(
    train_loop_per_worker=train_fn,
    scaling_config=ScalingConfig(
        num_workers=4,
        use_gpu=True,
        resources_per_worker={"GPU": 1}
    ),
    datasets={"train": train_ds, "valid": valid_ds}
)

result = trainer.fit()
```

### 7.4 XGBoost GPU Training

```python
import xgboost as xgb

params = {
    'tree_method': 'hist',
    'device': 'cuda',
    'objective': 'binary:logistic',
    'eval_metric': 'auc',
    'max_depth': 6,
    'learning_rate': 0.1
}

dtrain = xgb.DMatrix(X_train, label=y_train)
model = xgb.train(params, dtrain, num_boost_round=500)
```

**Checklist: GPU Scaling**

- [ ] GPU availability verified (`nvidia-smi`)
- [ ] CUDA drivers and libraries installed
- [ ] Memory requirements estimated (GPU VRAM)
- [ ] Fallback to CPU configured for debugging
- [ ] Ray cluster configured for distributed training (if needed)
- [ ] Training time benchmarked: CPU vs GPU

---

## 8. Model Comparison

### 8.1 Fair Comparison Rules

**Requirements:**
- Same train/validation/test split (same random seed)
- Same evaluation metric
- Same feature set (or document differences)
- Same hardware (for latency comparisons)

**What to compare:**
- Primary metric (accuracy, RMSE, etc.)
- Compute cost (training time, memory)
- Inference latency (p50, p95, p99)
- Model size (disk, memory)
- Interpretability (if relevant)

### 8.2 Statistical Significance

**When to test:**
- Comparing two models
- Small performance differences
- Need confidence in improvement

**Methods:**
- Corrected resampled t-test on CV folds (Nadeau-Bengio); the uncorrected paired t-test treats overlapping folds as independent, underestimates variance and inflates false positives
- Bootstrap confidence intervals
- Permutation test

**Checklist: Model Comparison**

- [ ] Apples-to-apples comparison (same data, metric, hardware)
- [ ] Primary metric differences documented
- [ ] Secondary metrics considered (latency, cost, interpretability)
- [ ] Statistical significance tested (if differences small)
- [ ] Documented reasons for final choice

---

## 9. Thresholding for Classification

### 9.1 Threshold Selection

**Methods:**
- **ROC curve**: Maximize TPR, minimize FPR
- **PR curve**: Precision-recall trade-off (better for imbalanced)
- **F1 score**: Harmonic mean of precision and recall
- **Cost-sensitive**: Assign costs to FP and FN, minimize total cost

**Context-specific:**
- Fraud detection: High recall (catch fraudsters), tolerate FP
- Spam filtering: High precision (don't block legitimate emails)
- Medical diagnosis: Balance based on cost of FN vs FP

### 9.2 Per-Segment Validation

**Why it matters:**
- Optimal threshold may vary by segment
- Fairness: ensure performance across demographics
- Business logic: different risk tolerances

**Checklist: Thresholding**

- [ ] Threshold selection method documented (ROC, PR, cost)
- [ ] ROC and PR curves generated
- [ ] Threshold chosen with business justification
- [ ] Per-segment thresholds validated (if applicable)
- [ ] Trade-offs documented (precision vs recall)  
