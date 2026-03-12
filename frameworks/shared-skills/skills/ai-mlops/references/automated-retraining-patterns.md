# Automated Retraining Patterns

> Operational guide for end-to-end automated model retraining pipelines. Covers trigger detection, data preparation, training orchestration, validation gates, promotion workflows, deployment, and rollback. Focus on production-grade automation with Airflow and Dagster patterns.

**Freshness anchor:** January 2026 — Airflow 2.9+, Dagster 1.7+, MLflow 2.16+, Great Expectations 0.18+

---

## Decision Tree: Retraining Trigger Selection

```
START
│
├─ How fast does data distribution change?
│   ├─ Rapidly (hours–days): e-commerce, ad click, fraud
│   │   └─ Drift-triggered retraining (continuous monitoring)
│   │
│   ├─ Moderately (weeks–months): churn, demand forecasting
│   │   └─ Scheduled retraining (weekly/monthly) + drift guard
│   │
│   └─ Slowly (months–years): medical, credit scoring
│       └─ Scheduled retraining (quarterly) + performance trigger
│
├─ Can you measure real-time ground truth?
│   ├─ YES (immediate labels) → Performance-triggered
│   │   └─ Retrain when metric drops below threshold
│   │
│   ├─ DELAYED (labels arrive days–weeks later) → Drift-triggered
│   │   └─ Monitor input drift as proxy, validate on delayed labels
│   │
│   └─ NO (no labels in production) → Drift-triggered only
│       └─ Monitor input distribution, retrain on significant shift
│
└─ Regulatory constraints?
    ├─ YES → Scheduled retraining with mandatory review gates
    └─ NO  → Drift or performance triggered
```

---

## Quick Reference: Retraining Strategies

| Strategy | Trigger | Frequency | Best For | Risk |
|----------|---------|-----------|----------|------|
| Scheduled | Cron/calendar | Fixed (weekly/monthly) | Stable domains, regulated | May retrain unnecessarily |
| Performance-triggered | Metric drop | On threshold breach | Labeled data available | Delayed detection if labels lag |
| Drift-triggered | Distribution shift | On drift detection | Fast-changing data | False positives from benign shifts |
| Hybrid (scheduled + drift) | Both | Fixed + on-demand | Most production systems | Higher complexity |
| Continuous (online) | Every batch | Per data batch | Streaming, real-time | Hard to validate, rollback |

---

## Operational Patterns

### Pattern 1: Drift Detection Triggers

- **Use when:** Data distribution changes are primary concern
- **Implementation:**

```python
from scipy.stats import ks_2samp, chi2_contingency
import numpy as np

class DriftDetector:
    """Detect feature and prediction drift."""

    def __init__(self, reference_data, p_value_threshold=0.01):
        self.reference = reference_data
        self.threshold = p_value_threshold

    def check_feature_drift(self, current_data):
        """Per-feature KS test for continuous, chi-squared for categorical."""
        drift_results = {}
        for col in self.reference.columns:
            if self.reference[col].dtype in ['float64', 'int64']:
                stat, p_value = ks_2samp(
                    self.reference[col].dropna(),
                    current_data[col].dropna()
                )
                drift_results[col] = {
                    'test': 'ks',
                    'statistic': stat,
                    'p_value': p_value,
                    'drifted': p_value < self.threshold,
                }
            else:
                # Chi-squared for categorical (align categories, compare counts)
                ref_counts = self.reference[col].value_counts()
                cur_counts = current_data[col].value_counts()
                all_cats = set(ref_counts.index) | set(cur_counts.index)
                observed = np.array([cur_counts.get(c, 0) for c in all_cats])
                expected = np.array([ref_counts.get(c, 0) for c in all_cats])
                expected = expected * (observed.sum() / expected.sum())
                stat, p_value = chi2_contingency(np.array([observed, expected]))[:2]
                drift_results[col] = {'test': 'chi2', 'p_value': p_value,
                                       'drifted': p_value < self.threshold}

        n_drifted = sum(1 for r in drift_results.values() if r['drifted'])
        should_retrain = n_drifted >= max(1, len(drift_results) * 0.2)

        return drift_results, should_retrain

    def check_prediction_drift(self, reference_preds, current_preds):
        """Check if model output distribution has shifted."""
        stat, p_value = ks_2samp(reference_preds, current_preds)
        return {'statistic': stat, 'p_value': p_value, 'drifted': p_value < self.threshold}
```

- **Drift thresholds:**

| Signal | Metric | Warning | Retrain |
|--------|--------|---------|---------|
| Feature drift | KS p-value | < 0.05 on 10% features | < 0.01 on 20% features |
| Prediction drift | KS p-value | < 0.05 | < 0.01 |
| Performance drop | PR-AUC delta | -0.02 from baseline | -0.05 from baseline |
| Label drift | Class ratio change | > 10% relative | > 25% relative |

### Pattern 2: Data Preparation Pipeline

- **Use when:** Automating data extraction and validation before training
- **Implementation (Dagster):**

```python
from dagster import asset, FreshnessPolicy
import great_expectations as gx

@asset(freshness_policy=FreshnessPolicy(maximum_lag_minutes=1440))
def training_data():
    """Extract from warehouse, validate with Great Expectations, log profile."""
    df = run_query("SELECT * FROM ml_features.fraud_features WHERE ...")

    # Validate with Great Expectations
    validator = gx.get_context().sources.pandas_default.read_dataframe(df)
    validator.expect_table_row_count_to_be_between(min_value=10000)
    validator.expect_column_values_to_not_be_null("user_id")
    results = validator.validate()
    if not results.success:
        raise ValueError(f"Data validation failed: {results.statistics}")

    return df, {'row_count': len(df), 'class_dist': df['is_fraud'].value_counts().to_dict()}
```

### Pattern 3: Training Orchestration (Airflow)

- **Use when:** Airflow is the orchestrator for ML pipelines
- **Implementation:**

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'ml-platform',
    'retries': 2,
    'retry_delay': timedelta(minutes=10),
    'email_on_failure': True,
    'email': ['ml-oncall@company.com'],
}

with DAG(
    dag_id='fraud_model_retraining',
    default_args=default_args,
    schedule_interval='0 6 * * 1',  # Weekly Monday 6am
    catchup=False,
    tags=['ml', 'retraining', 'fraud'],
) as dag:

    check_drift = PythonOperator(
        task_id='check_drift',
        python_callable=run_drift_detection,
    )

    should_retrain = BranchPythonOperator(
        task_id='should_retrain',
        python_callable=evaluate_drift_results,
        # Returns 'prepare_data' or 'skip_retraining'
    )

    prepare_data = PythonOperator(
        task_id='prepare_data',
        python_callable=extract_and_validate_data,
    )

    train_model = PythonOperator(
        task_id='train_model',
        python_callable=train_and_log_model,
    )

    validate_model = PythonOperator(
        task_id='validate_model',
        python_callable=run_validation_gates,
    )

    promote_or_reject = BranchPythonOperator(
        task_id='promote_or_reject',
        python_callable=champion_challenger_decision,
        # Returns 'promote_model' or 'reject_model'
    )

    promote_model = PythonOperator(
        task_id='promote_model',
        python_callable=promote_to_production,
    )

    reject_model = PythonOperator(
        task_id='reject_model',
        python_callable=log_rejection_and_alert,
    )

    skip_retraining = PythonOperator(
        task_id='skip_retraining',
        python_callable=lambda: print("No drift detected, skipping"),
    )

    monitor_post_deploy = PythonOperator(
        task_id='monitor_post_deploy',
        python_callable=run_post_deployment_checks,
        trigger_rule='none_failed_min_one_success',
    )

    (check_drift >> should_retrain >>
     [prepare_data, skip_retraining])
    (prepare_data >> train_model >> validate_model >>
     promote_or_reject >> [promote_model, reject_model])
    promote_model >> monitor_post_deploy
```

### Pattern 4: Champion/Challenger Validation Gates

- **Use when:** Deciding whether new model replaces current production model
- **Implementation:**

```python
def champion_challenger_decision(ti):
    """Compare new model against production model."""
    challenger_metrics = ti.xcom_pull(task_ids='validate_model')
    champion_metrics = get_production_model_metrics()

    gates = {
        'pr_auc_improvement': {
            'check': challenger_metrics['pr_auc'] >= champion_metrics['pr_auc'] - 0.005,
            'description': 'PR-AUC must not degrade by more than 0.5%',
        },
        'latency_acceptable': {
            'check': challenger_metrics['p99_latency_ms'] <= 100,
            'description': 'P99 latency must be under 100ms',
        },
        'calibration_ok': {
            'check': abs(challenger_metrics['coverage_95'] - 0.95) < 0.05,
            'description': '95% interval coverage within 5% of nominal',
        },
        'no_regression_subgroups': {
            'check': all(
                challenger_metrics[f'pr_auc_{group}'] >= champion_metrics[f'pr_auc_{group}'] - 0.01
                for group in ['high_value', 'new_users', 'mobile']
            ),
            'description': 'No subgroup regresses by more than 1%',
        },
        'data_quality_passed': {
            'check': challenger_metrics['data_validation_passed'],
            'description': 'Training data passed all quality checks',
        },
    }

    all_passed = all(g['check'] for g in gates.values())
    failed_gates = [name for name, g in gates.items() if not g['check']]

    if all_passed:
        return 'promote_model'
    else:
        log_gate_failures(failed_gates, gates)
        return 'reject_model'
```

- **Gate categories:**

| Gate Type | Metric | Threshold | Mandatory |
|-----------|--------|-----------|-----------|
| Primary metric | PR-AUC | >= champion - 0.005 | Yes |
| Latency | P99 inference | <= 100ms | Yes |
| Subgroup fairness | PR-AUC per group | >= champion - 0.01 | Yes |
| Calibration | Coverage error | < 5% | Recommended |
| Model size | Disk / memory | <= 2x champion | Recommended |
| Data quality | GE validation | All passed | Yes |

### Pattern 5: Deployment and Rollback

- **Use when:** Automating model promotion and safe rollback

```python
def promote_to_production(ti):
    """Blue-green deployment with automatic rollback."""
    new_model_uri = ti.xcom_pull(task_ids='train_model', key='model_uri')

    # Step 1: Register in model registry
    client = MlflowClient()
    mv = client.create_model_version("fraud-model", new_model_uri)

    # Step 2: Deploy to canary (10% traffic)
    deploy_canary(model_version=mv.version, traffic_pct=10)

    # Step 3: Monitor canary for 1 hour
    canary_metrics = monitor_canary(duration_minutes=60)

    if canary_metrics['error_rate'] > 0.01 or canary_metrics['latency_p99'] > 150:
        # Rollback canary
        rollback_canary()
        raise ValueError(f"Canary failed: {canary_metrics}")

    # Step 4: Ramp to 100%
    deploy_full(model_version=mv.version)

    # Step 5: Archive previous production version
    client.transition_model_version_stage("fraud-model", mv.version, "Production")

def rollback_to_previous():
    """Emergency rollback procedure."""
    client = MlflowClient()
    # Get previous production version
    versions = client.get_latest_versions("fraud-model", stages=["Archived"])
    previous = max(versions, key=lambda v: v.version)

    # Redeploy previous version
    deploy_full(model_version=previous.version)
    client.transition_model_version_stage("fraud-model", previous.version, "Production")

    # Alert team
    send_alert("Model rollback executed", severity="high")
```

### Pattern 6: Post-Deployment Monitoring

- **Use when:** Always — every deployment needs monitoring

```python
def run_post_deployment_checks(ti):
    """Monitor model health after deployment."""

    checks = {
        'prediction_distribution': {'metric': 'ks_test_pvalue', 'threshold': 0.01, 'window': '1_hour'},
        'error_rate': {'metric': 'http_5xx_rate', 'threshold': 0.005, 'window': '15_minutes'},
        'latency': {'metric': 'p99_latency_ms', 'threshold': 100, 'window': '15_minutes'},
        'throughput': {'metric': 'requests_per_second', 'threshold_lower': 10, 'window': '15_minutes'},
    }

    # Run checks at 15min, 1hr, 24hr post-deploy
    for check_time in [15, 60, 1440]:
        results = run_checks(checks, minutes_after_deploy=check_time)
        if not results['all_passed']:
            send_alert(f"Post-deploy check failed at {check_time}min: {results}")
            if check_time <= 60:
                rollback_to_previous()
                break
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Fix |
|---|---|---|
| Retraining without validation gates | Bad model goes to production | Mandatory champion/challenger check |
| No rollback procedure | Stuck with bad model | Pre-build rollback, test it regularly |
| Retraining on every minor drift signal | Wasted compute, model instability | Set meaningful drift thresholds, add cooldown |
| No data validation before training | Garbage in, garbage out | Great Expectations or equivalent before training |
| Manual promotion to production | Slow, error-prone, no audit trail | Automated pipeline with approval gates |
| Not monitoring after deployment | Issues detected by users, not system | Automated post-deploy checks at 15min/1hr/24hr |
| Retraining without fresh labels | Training on stale ground truth | Verify label freshness before training |
| Same hyperparameters every retrain | Optimal params change with data | Re-tune periodically (monthly) or use AutoML |
| No training data versioning | Cannot reproduce or debug models | Version training data snapshots |
| Alerting on all drift without filtering | Alert fatigue from benign shifts | Filter: only alert when drift + performance drop coincide |

---

## Validation Checklist

- [ ] Retraining trigger defined (schedule, drift, performance, or hybrid)
- [ ] Data validation runs before every training job
- [ ] Champion/challenger comparison automated with clear gates
- [ ] Canary deployment configured (10% traffic minimum)
- [ ] Rollback procedure documented and tested
- [ ] Post-deployment monitoring checks at 15min, 1hr, 24hr
- [ ] Training data versioned and lineage tracked
- [ ] Drift detection calibrated (not too sensitive, not too slack)
- [ ] Alerts routed to on-call with appropriate severity
- [ ] Full pipeline tested end-to-end in staging before production

---

## Cross-References

- `ai-mlops/references/experiment-tracking-patterns.md` — logging retraining runs
- `ai-mlops/references/cost-management-finops.md` — cost budgets for retraining
- `ai-ml-data-science/references/hyperparameter-optimization.md` — re-tuning during retraining
- `ai-ml-data-science/references/class-imbalance-patterns.md` — monitoring class distribution drift
