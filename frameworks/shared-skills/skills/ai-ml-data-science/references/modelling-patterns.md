# Modelling Patterns

Operational modelling techniques, baseline-first methodologies, model selection, train/test splits, and model comparison rules.

---

## 1. Model Selection & Baselines (Modern Best Performers)

### 1.1 Decision Guide

Based on current benchmarks and best practices:

| Data type / size | Start with | Modern Best Practices |
|-----------------------------------|------------------------------------|------------|
| Tabular, small-medium | **LightGBM**, XGBoost | Tree-based methods deliver best performance + efficiency |
| Tabular, large & complex | LightGBM, CatBoost, then NN | LightGBM offers significant computational advantage |
| High-dim sparse (text, counts) | Linear models, NB, shallow NN | Fast, interpretable baselines |
| Time series forecasting | LightGBM, then RNNs/Transformers | Tree-based methods excel vs traditional ARIMA |
| Mixed modalities | Gradient boosting, then NN/Transformers | Transformers for long-term dependencies |

**Key Finding:** Tree-based methods (LightGBM) deliver best performance with significant computational efficiency advantage.

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

**Checklist: Baselines**

- [ ] Simple baseline implemented (majority class, mean, naive forecast)
- [ ] LightGBM/XGBoost tried as primary candidate
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

**First choice:**
- LightGBM (fast, accurate, handles categorical features)
- XGBoost (mature, well-tested)
- CatBoost (handles high-cardinality categoricals)

**Linear models:**
- Logistic regression (interpretable baseline)
- Ridge/Lasso (regularized linear)
- Use when: Need interpretability, compliance, or very fast inference

**Neural networks:**
- Only when: Large datasets (>1M rows), complex interactions
- TabNet, FT-Transformer for tabular data

### 3.2 Text Data

**Start with:**
- TF-IDF + linear models (fast baseline)
- Pretrained embeddings (Sentence-BERT) + LightGBM

**Advanced:**
- Fine-tuned transformers (BERT, RoBERTa)
- Only when: Large labeled dataset, need state-of-art

### 3.3 When to Avoid Deep Models

**Don't use neural networks when:**
- Small datasets (<10k samples)
- Highly structured relational data (use tree models)
- Need interpretability for compliance
- Limited compute budget

**Checklist: Model Family**

- [ ] Model complexity matches data size
- [ ] Baseline -> interpretable model -> complex model progression
- [ ] Compute and latency constraints considered
- [ ] Interpretability requirements documented

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

**Benchmark reference** (H100 GPUs):

- 1.2B rows, 120 features: ~7 minutes with 6x H100 GPUs
- 100M rows: ~30-60 seconds

### 7.2 GPU Training with LightGBM

```python
import lightgbm as lgb

params = {
    'device': 'gpu',
    'gpu_platform_id': 0,
    'gpu_device_id': 0,
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
from ray.train.lightgbm import LightGBMTrainer
from ray.train import ScalingConfig

trainer = LightGBMTrainer(
    label_column="target",
    params={
        "objective": "binary",
        "metric": "auc",
        "num_leaves": 63
    },
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
- Paired t-test (cross-validation folds)
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
