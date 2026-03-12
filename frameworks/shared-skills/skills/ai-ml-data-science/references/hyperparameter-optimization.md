# Hyperparameter Optimization

> Operational guide for systematic hyperparameter tuning using Optuna, Ray Tune, and Bayesian optimization. Covers search space design, pruning, multi-objective optimization, and reproducible tuning recipes for common model families.

**Freshness anchor:** January 2026 — Optuna 3.6+, Ray Tune 2.9+, scikit-learn 1.5+, LightGBM 4.x

---

## Decision Tree: Choosing an Optimization Strategy

```
START
│
├─ < 10 hyperparameters?
│   ├─ YES → Optuna with TPE sampler (default)
│   └─ NO  → Continue
│
├─ 10–30 hyperparameters?
│   ├─ Training time < 5 min per trial?
│   │   ├─ YES → Optuna TPE, 100–300 trials
│   │   └─ NO  → Optuna with pruning (MedianPruner)
│   └─ Distributed cluster available?
│       ├─ YES → Ray Tune + Optuna integration
│       └─ NO  → Optuna with SQLite storage for resumability
│
├─ Multi-objective (e.g., accuracy + latency)?
│   └─ Optuna with NSGAIISampler → Pareto front
│
├─ Need warmstarting from prior runs?
│   └─ Optuna with enqueue_trial for known-good configs
│
└─ Very expensive trials (>1 hour each)?
    └─ Bayesian optimization (GP) with <50 trials
        OR early stopping with aggressive pruning
```

---

## Quick Reference: Sampler Selection

| Sampler | Trials Needed | Best For | Avoid When |
|---------|--------------|----------|------------|
| TPE (default) | 50–300 | General purpose, mixed types | Very few trials (<20) |
| GP (Gaussian Process) | 10–50 | Expensive evaluations | High-dimensional (>15 params) |
| CMA-ES | 50–200 | Continuous params, neural nets | Categorical-heavy spaces |
| NSGA-II | 100–500 | Multi-objective | Single objective |
| Random | 20–100 | Baseline comparison, parallel | Always outperformed by TPE |
| Grid | all combos | Exhaustive, < 4 params | > 4 params (combinatorial explosion) |

---

## Operational Patterns

### Pattern 1: Optuna Basic Setup

- **Use when:** Starting any tuning task
- **Implementation:**

```python
import optuna

def objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000, step=100),
        'max_depth': trial.suggest_int('max_depth', 3, 12),
        'learning_rate': trial.suggest_float('learning_rate', 1e-3, 0.3, log=True),
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
    }

    # Cross-validation inside objective
    scores = cross_val_score(model_cls(**params), X, y, cv=5, scoring='average_precision')
    return scores.mean()

study = optuna.create_study(
    direction='maximize',
    sampler=optuna.samplers.TPESampler(seed=42),
    study_name='lgbm_tuning_v1',
    storage='sqlite:///optuna_studies.db',  # resumable
)
study.optimize(objective, n_trials=200, timeout=3600)
```

- **Key rules:**
  - Always use `log=True` for learning rates, regularization
  - Always set `seed` in sampler for reproducibility
  - Use SQLite storage for runs > 30 minutes (crash recovery)

### Pattern 2: Pruning for Expensive Models

- **Use when:** Single trial takes > 2 minutes
- **Implementation:**

```python
from optuna.pruners import MedianPruner, HyperbandPruner

study = optuna.create_study(
    direction='maximize',
    pruner=MedianPruner(
        n_startup_trials=10,   # don't prune first 10
        n_warmup_steps=20,     # don't prune before 20 epochs
        interval_steps=5,      # check every 5 epochs
    ),
)

def objective(trial):
    params = {... }  # suggest params

    for epoch in range(100):
        train_one_epoch(model, params)
        val_score = evaluate(model)

        trial.report(val_score, epoch)
        if trial.should_prune():
            raise optuna.TrialPruned()

    return val_score
```

- **Pruner selection:**

| Pruner | Aggression | Use When |
|--------|-----------|----------|
| MedianPruner | Moderate | Default choice |
| HyperbandPruner | Aggressive | Deep learning, many epochs |
| PercentilePruner | Configurable | Fine-tune aggression |
| ThresholdPruner | Fixed | Known minimum acceptable score |

### Pattern 3: LightGBM Tuning Recipe

- **Use when:** Tuning LightGBM for tabular data
- **Search space (battle-tested ranges):**

```python
def lgbm_objective(trial):
    params = {
        'objective': 'binary',
        'metric': 'average_precision',
        'verbosity': -1,
        'boosting_type': 'gbdt',

        # Tier 1: Highest impact
        'learning_rate': trial.suggest_float('learning_rate', 0.005, 0.2, log=True),
        'n_estimators': trial.suggest_int('n_estimators', 100, 2000, step=100),
        'num_leaves': trial.suggest_int('num_leaves', 15, 255),
        'max_depth': trial.suggest_int('max_depth', 3, 12),

        # Tier 2: Regularization
        'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
        'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
        'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),

        # Tier 3: Stochastic
        'subsample': trial.suggest_float('subsample', 0.5, 1.0),
        'colsample_bytree': trial.suggest_float('colsample_bytree', 0.4, 1.0),
        'subsample_freq': trial.suggest_int('subsample_freq', 1, 7),

        # Tier 4: Fine-tuning
        'min_split_gain': trial.suggest_float('min_split_gain', 0.0, 1.0),
        'max_bin': trial.suggest_int('max_bin', 63, 511),
    }

    cv_result = lgb.cv(params, train_set, nfold=5, stratified=True,
                       return_cvbooster=True)
    return cv_result['valid average_precision-mean'][-1]
```

- **Tuning order:** Tune Tier 1 first (50 trials), freeze best, then add Tier 2–4

### Pattern 4: scikit-learn Tuning Recipe

- **Use when:** Tuning RandomForest, GradientBoosting, SVM, or other sklearn models

```python
def sklearn_rf_objective(trial):
    params = {
        'n_estimators': trial.suggest_int('n_estimators', 100, 1000, step=50),
        'max_depth': trial.suggest_int('max_depth', 3, 30),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 20),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 15),
        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.3, 0.5, 0.7]),
        'class_weight': trial.suggest_categorical('class_weight', ['balanced', 'balanced_subsample', None]),
    }
    clf = RandomForestClassifier(**params, random_state=42, n_jobs=-1)
    scores = cross_val_score(clf, X, y, cv=5, scoring='average_precision')
    return scores.mean()
```

### Pattern 5: Multi-Objective Optimization

- **Use when:** Trading off accuracy vs latency, accuracy vs model size, etc.
- **Implementation:**

```python
study = optuna.create_study(
    directions=['maximize', 'minimize'],  # accuracy UP, latency DOWN
    sampler=optuna.samplers.NSGAIISampler(seed=42),
)

def multi_objective(trial):
    params = {... }
    score = cross_val_score(model(**params), X, y, cv=3).mean()
    latency = measure_inference_latency(model(**params), X[:100])
    return score, latency

study.optimize(multi_objective, n_trials=200)

# Get Pareto front
pareto_trials = study.best_trials
for t in pareto_trials:
    print(f"Score: {t.values[0]:.4f}, Latency: {t.values[1]:.2f}ms")
```

### Pattern 6: Warmstarting with Known-Good Configs

- **Use when:** You have prior knowledge or production configs to start from

```python
study = optuna.create_study(direction='maximize')

# Seed with known-good config
study.enqueue_trial({
    'learning_rate': 0.05,
    'n_estimators': 500,
    'max_depth': 7,
    'num_leaves': 63,
})

study.optimize(objective, n_trials=150)
```

### Pattern 7: Ray Tune for Distributed Tuning

- **Use when:** Cluster available, need to parallelize across GPUs/nodes

```python
from ray import tune
from ray.tune.search.optuna import OptunaSearch

search_space = {
    'learning_rate': tune.loguniform(1e-4, 1e-1),
    'batch_size': tune.choice([32, 64, 128, 256]),
    'hidden_size': tune.choice([128, 256, 512]),
}

analysis = tune.run(
    train_fn,
    config=search_space,
    search_alg=OptunaSearch(metric='val_loss', mode='min'),
    num_samples=200,
    resources_per_trial={'cpu': 4, 'gpu': 1},
    scheduler=tune.schedulers.ASHAScheduler(
        metric='val_loss', mode='min',
        max_t=100, grace_period=10,
    ),
)
```

---

## Reproducibility Checklist

```python
# 1. Fix all random seeds
import numpy as np, random, torch
random.seed(42)
np.random.seed(42)
torch.manual_seed(42)

# 2. Use seeded sampler
sampler = optuna.samplers.TPESampler(seed=42)

# 3. Log environment
import optuna, sklearn, lightgbm
env_info = {
    'optuna': optuna.__version__,
    'sklearn': sklearn.__version__,
    'lgbm': lightgbm.__version__,
    'python': sys.version,
}

# 4. Store study to DB
study = optuna.create_study(storage='sqlite:///studies.db', study_name='exp_v1')

# 5. Export best trial
best = study.best_trial
print(f"Best value: {best.value}")
print(f"Best params: {best.params}")
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Grid search with > 5 params | Combinatorial explosion (3^10 = 59k combos) | Use TPE or Bayesian optimization |
| Not using `log=True` for learning rate | Wastes trials in high range, under-explores low range | Always `log=True` for rates, regularization |
| Tuning all params simultaneously from start | High-dimensional space, slow convergence | Tune in tiers: most impactful first |
| No pruning for expensive trials | Wasting compute on clearly bad configs | Add MedianPruner or ASHA scheduler |
| Tuning on test set | Overfitting to test data | Tune on validation, evaluate once on test |
| Fixed number of CV folds regardless of dataset size | 5-fold on 500 rows = noisy; 10-fold on 1M rows = slow | Scale folds: 10 for small, 3–5 for large |
| Ignoring study persistence | Lose progress on crash | Use `storage='sqlite:///...'` |
| Not comparing to random baseline | Can't tell if TPE is actually helping | Run 50 random trials first as reference |
| Copy-pasting search spaces across projects | Different data needs different ranges | Start from recipes, adjust based on data |
| Running 1000 trials without analysis | Diminishing returns after ~100–200 for TPE | Check convergence plots, stop early |

---

## Convergence Analysis

```python
# Check if study has converged
import optuna.visualization as vis

# Plot optimization history
vis.plot_optimization_history(study)

# Parameter importance (which params matter most)
vis.plot_param_importances(study)

# Slice plot (effect of each param)
vis.plot_slice(study)

# Rule of thumb: if best value hasn't improved in last 30% of trials, stop
```

---

## Cross-References

- `ai-ml-data-science/references/class-imbalance-patterns.md` — tuning `scale_pos_weight` and sampling ratio
- `ai-ml-data-science/references/interpretability-explainability.md` — interpreting tuned models
- `ai-mlops/references/experiment-tracking-patterns.md` — logging Optuna studies to MLflow/W&B
- `ai-mlops/references/automated-retraining-patterns.md` — scheduling tuning runs in pipelines
