# Experiment Tracking Patterns

> Operational guide for organizing, logging, and managing ML experiments using MLflow, Weights & Biases, and Neptune. Covers naming conventions, artifact management, team collaboration, model registry integration, and CI/CD handoff. Focus on reproducibility and production readiness.

**Freshness anchor:** January 2026 — MLflow 2.16+, W&B 0.17+, Neptune 1.10+

---

## Decision Tree: Choosing a Tracking Platform

```
START
│
├─ Team size?
│   ├─ Solo / small team (1-5)
│   │   ├─ Budget constrained? → MLflow (open source, self-hosted)
│   │   └─ Want managed service? → W&B (free tier) or Neptune (free tier)
│   │
│   └─ Large team (5+) / enterprise
│       ├─ On-premise required? → MLflow (self-host) or Neptune (on-prem option)
│       ├─ Deep collaboration features? → W&B (reports, sweeps)
│       └─ Need model registry + deployment? → MLflow (best registry integration)
│
├─ Primary use case?
│   ├─ Research / exploration → W&B (best visualization, sweeps)
│   ├─ Production ML pipeline → MLflow (model registry, serving)
│   ├─ Deep learning / training runs → W&B (GPU monitoring, media logging)
│   └─ Tabular ML / AutoML → MLflow or Neptune
│
└─ Integration requirements?
    ├─ Databricks → MLflow (native)
    ├─ AWS SageMaker → MLflow (managed) or W&B
    ├─ Kubernetes → MLflow (deployed) or W&B
    └─ Airflow / Dagster → MLflow (API-first)
```

---

## Quick Reference: Platform Comparison

| Feature | MLflow | W&B | Neptune |
|---------|--------|-----|---------|
| Open source | Yes | No (client is) | No (client is) |
| Self-hosted | Yes | Yes (Enterprise) | Yes (Enterprise) |
| Model registry | Excellent | Good | Good |
| Visualization | Basic | Excellent | Good |
| Collaboration | Basic | Excellent (Reports) | Good |
| Hyperparameter sweeps | Via Optuna | Built-in (Sweeps) | Via Optuna |
| Artifact storage | Built-in | Built-in | Built-in |
| Cost (small team) | Free | Free tier | Free tier |
| Cost (enterprise) | Self-host cost | $50+/user/mo | $49+/user/mo |
| CI/CD integration | Excellent (API) | Good | Good |

---

## Operational Patterns

### Pattern 1: Naming Conventions

- **Use when:** Always — consistent naming is the foundation of experiment organization

```
# Experiment naming: {project}/{model_family}/{objective}
Examples:
  fraud-detection/lightgbm/pr-auc-optimization
  recommender/two-tower/recall-at-10
  demand-forecast/temporal-fusion/mape-reduction

# Run naming: {date}_{description}_{variant}
Examples:
  2026-01-15_baseline_v1
  2026-01-15_smote-oversampling_v2
  2026-01-16_tuned-hyperparams_v3

# Model naming (registry): {project}-{model_type}-{version_strategy}
Examples:
  fraud-lgbm-v3
  recommender-two-tower-v1
  demand-tft-v2
```

- **Naming rules:**
  - Lowercase, hyphens for spaces
  - Date prefix on runs for chronological sorting
  - Version suffix for lineage tracking
  - Never use special characters or spaces

### Pattern 2: MLflow Experiment Setup

- **Use when:** Using MLflow as tracking backend
- **Implementation:**

```python
import mlflow
from mlflow.tracking import MlflowClient

# Configuration
mlflow.set_tracking_uri("http://mlflow-server:5000")
mlflow.set_experiment("fraud-detection/lightgbm/pr-auc-optimization")

# Structured run
with mlflow.start_run(run_name="2026-01-15_baseline_v1") as run:
    # 1. Log parameters (ALL of them)
    mlflow.log_params({
        'model_type': 'lightgbm',
        'n_estimators': 500,
        'learning_rate': 0.05,
        'max_depth': 7,
        'num_leaves': 63,
        'class_weight': 'balanced',
        'train_rows': len(X_train),
        'feature_count': X_train.shape[1],
        'train_date_range': f"{train_start} to {train_end}",
        'cv_folds': 5,
    })

    # 2. Log metrics (train + validation + test)
    mlflow.log_metrics({
        'train_pr_auc': train_score,
        'val_pr_auc': val_score,
        'test_pr_auc': test_score,
        'val_f1': f1_score,
        'val_mcc': mcc_score,
        'training_time_seconds': elapsed,
    })

    # 3. Log artifacts
    mlflow.log_artifact("confusion_matrix.png")
    mlflow.log_artifact("shap_summary.png")
    mlflow.log_artifact("feature_importance.csv")

    # 4. Log model with signature
    from mlflow.models import infer_signature
    signature = infer_signature(X_test, model.predict(X_test))
    mlflow.sklearn.log_model(model, "model", signature=signature)

    # 5. Log dataset info
    mlflow.log_input(
        mlflow.data.from_pandas(X_train, name="training_data"),
        context="training"
    )

    # 6. Tags for filtering
    mlflow.set_tags({
        'team': 'ml-platform',
        'stage': 'experimentation',
        'data_version': 'v2.3',
        'git_commit': git_sha,
    })
```

### Pattern 3: W&B Experiment Setup

- **Use when:** Using Weights & Biases, especially for deep learning
- **Implementation:**

```python
import wandb

# Initialize
run = wandb.init(
    project="fraud-detection",
    name="2026-01-15_baseline_v1",
    config={
        'model_type': 'lightgbm',
        'n_estimators': 500,
        'learning_rate': 0.05,
        'max_depth': 7,
        'dataset_version': 'v2.3',
    },
    tags=['baseline', 'lightgbm', 'balanced-weights'],
    notes="Initial baseline with class_weight=balanced",
)

# Log metrics over training
for epoch in range(n_epochs):
    train_loss, val_loss = train_epoch()
    wandb.log({
        'train/loss': train_loss,
        'val/loss': val_loss,
        'val/pr_auc': val_pr_auc,
        'epoch': epoch,
    })

# Log artifacts
wandb.log({
    'confusion_matrix': wandb.plot.confusion_matrix(
        y_true=y_test, preds=y_pred, class_names=['Normal', 'Fraud']
    ),
    'roc_curve': wandb.plot.roc_curve(y_test, y_proba),
    'shap_summary': wandb.Image("shap_summary.png"),
})

# Log model artifact
artifact = wandb.Artifact("fraud-lgbm-v1", type="model")
artifact.add_file("model.pkl")
run.log_artifact(artifact)

run.finish()
```

### Pattern 4: Metric Logging Best Practices

- **Use when:** Deciding what to log and how

| Category | Metrics to Log | Frequency |
|----------|---------------|-----------|
| Performance | PR-AUC, F1, MCC, accuracy (if balanced) | Per epoch + final |
| Loss | Train loss, val loss | Per step or epoch |
| Calibration | Coverage at 95%, 80% (if probabilistic) | Final |
| Efficiency | Training time, inference latency, GPU utilization | Per run |
| Data | Row count, feature count, class distribution, date range | Per run |
| Cost | GPU hours, spot instance cost, API tokens used | Per run |
| Fairness | Metric parity across protected groups | Per run |

- **Logging rules:**
  - Log BOTH train and validation metrics (to detect overfitting)
  - Log wall clock time (not just epochs)
  - Log data statistics (detects silent data issues)
  - Log git commit hash (reproducibility)
  - Log random seed (reproducibility)

### Pattern 5: Artifact Management

- **Use when:** Storing models, plots, data snapshots, and configs

```python
# Artifact organization structure
"""
artifacts/
├── model/                  # Serialized model
│   ├── model.pkl
│   ├── model_signature.json
│   └── requirements.txt
├── evaluation/             # Evaluation outputs
│   ├── confusion_matrix.png
│   ├── shap_summary.png
│   ├── pr_curve.png
│   └── metrics.json
├── data/                   # Data snapshot (metadata, not full data)
│   ├── data_profile.json   # schema, stats, distributions
│   └── sample.parquet      # small representative sample
└── config/                 # Full configuration
    ├── params.yaml
    └── environment.yaml
"""

# Artifact lifecycle policy
ARTIFACT_RETENTION = {
    'production_models': 'forever',          # never delete
    'staging_candidates': '180_days',        # 6 months
    'experiment_models': '30_days',          # 1 month
    'evaluation_plots': '90_days',           # 3 months
    'failed_runs': '7_days',                 # 1 week
}
```

### Pattern 6: Model Registry Integration

- **Use when:** Promoting models from experimentation to production
- **Implementation (MLflow):**

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()

# Register model from experiment run
model_uri = f"runs:/{run_id}/model"
mv = client.create_model_version(
    name="fraud-detection-lgbm",
    source=model_uri,
    run_id=run_id,
    description="LightGBM with balanced weights, PR-AUC=0.87"
)

# Stage transitions
# None → Staging → Production → Archived
client.transition_model_version_stage(
    name="fraud-detection-lgbm",
    version=mv.version,
    stage="Staging",
    archive_existing_versions=False,
)

# Promote to production after validation
client.transition_model_version_stage(
    name="fraud-detection-lgbm",
    version=mv.version,
    stage="Production",
    archive_existing_versions=True,  # archive previous production version
)
```

### Pattern 7: CI/CD Integration

- **Use when:** Automating experiment-to-production handoff
- **Pipeline steps:**
  1. Trigger on `workflow_dispatch` with `run_id` input
  2. Download model artifact: `mlflow artifacts download -r $RUN_ID`
  3. Run validation: `python scripts/validate_model.py --run-id $RUN_ID --min-pr-auc 0.85 --max-latency-ms 50`
  4. On success: `python scripts/register_model.py --run-id $RUN_ID --stage staging`
- **Key rule:** Never skip validation step, even for "minor" changes

### Pattern 8: Run Comparison Workflow

- **Use when:** Deciding which run to promote

```python
# MLflow: compare runs programmatically
from mlflow.tracking import MlflowClient

client = MlflowClient()
experiment = client.get_experiment_by_name("fraud-detection/lightgbm/pr-auc-optimization")

# Get all runs, sorted by metric
runs = client.search_runs(
    experiment_ids=[experiment.experiment_id],
    filter_string="metrics.test_pr_auc > 0.80",
    order_by=["metrics.test_pr_auc DESC"],
    max_results=10,
)

# Compare top runs
comparison = []
for run in runs:
    comparison.append({
        'run_name': run.info.run_name,
        'pr_auc': run.data.metrics.get('test_pr_auc'),
        'f1': run.data.metrics.get('test_f1'),
        'latency_ms': run.data.metrics.get('inference_latency_ms'),
        'training_time': run.data.metrics.get('training_time_seconds'),
    })

comparison_df = pd.DataFrame(comparison)
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| No naming convention | Experiments named "test1", "final", "final_v2" | Enforce `{date}_{description}_{variant}` |
| Logging only final metrics | Can't diagnose overfitting or training issues | Log per-epoch train + val metrics |
| Not logging data statistics | Silent data issues go undetected | Log row count, feature count, distributions |
| Storing huge datasets as artifacts | Fills storage, slow uploads | Store data metadata + small sample, not full dataset |
| No git commit tracking | Cannot reproduce results | Auto-log `git rev-parse HEAD` |
| Manual model promotion | Error-prone, no audit trail | CI/CD pipeline with validation gates |
| Everyone uses different tags | Cannot filter or compare across team | Standardize tag vocabulary in team docs |
| Not cleaning up failed runs | Storage waste, cluttered UI | Auto-delete failed runs after 7 days |
| Logging metrics without context | "accuracy: 0.95" means nothing without data version, split info | Always log data version, split strategy, date range |
| Separate tracking for dev vs production | Cannot trace production model back to experiment | Single tracking server, different experiment prefixes |

---

## Validation Checklist

- [ ] Tracking server configured and accessible to team
- [ ] Naming convention documented and enforced
- [ ] All parameters logged (not just "important" ones)
- [ ] Train + validation + test metrics logged separately
- [ ] Git commit hash auto-logged per run
- [ ] Artifacts organized in standard directory structure
- [ ] Artifact retention policy configured
- [ ] Model registry stages defined (None → Staging → Production)
- [ ] CI/CD pipeline validates before promotion
- [ ] Run comparison workflow documented for team

---

## Cross-References

- `ai-mlops/references/automated-retraining-patterns.md` — triggering experiments from drift detection
- `ai-mlops/references/cost-management-finops.md` — cost tracking per experiment
- `ai-ml-data-science/references/hyperparameter-optimization.md` — Optuna + MLflow/W&B integration
- `ai-ml-data-science/references/interpretability-explainability.md` — logging SHAP artifacts
