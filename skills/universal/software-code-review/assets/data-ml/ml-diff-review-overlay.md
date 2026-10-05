# Data / ML Diff Review Overlay

Use this overlay on top of the core review flow when a diff touches data pipelines, training code, experiment tracking, or model serving. It lists the review-specific checks only. For platform choice, MLOps process, and deep domain guidance, route to the owning skills:

- Model training, evaluation, fairness, leakage: [ai-ml-data-science](../../../ai-ml-data-science/SKILL.md)
- Deployment, monitoring, drift, rollback of models and LLMs: [ai-mlops](../../../ai-mlops/SKILL.md)
- dbt/SQLMesh models, metrics, data contracts, data quality: [data-analytics-engineering](../../../data-analytics-engineering/SKILL.md)
- Lakehouse storage, CDC, table formats: [data-lake-platform](../../../data-lake-platform/SKILL.md)

## Data Pipelines

- [ ] Idempotent and re-runnable: a retry or backfill does not duplicate or drop rows (merge keys, partition overwrite, dedup)
- [ ] Schema changes are explicit and backward-compatible for downstream consumers; breaking changes are versioned
- [ ] Validation runs at ingestion and before publish (nulls, ranges, uniqueness, referential integrity, row-count deltas)
- [ ] Failure handling is loud: bad records go to a quarantine/dead-letter path, not silently dropped
- [ ] Time handling is correct: timezones, late-arriving data, event time vs processing time
- [ ] PII is classified, minimised, and masked or encrypted where it lands; access follows least privilege
- [ ] New transforms have unit tests plus at least one data test on realistic fixtures
- [ ] Cost and scan size are proportionate (partition pruning, no accidental full scans or cross joins)

## Training and Evaluation Code

- [ ] No data leakage: splits happen before fitting any preprocessing; no target or future information in features
- [ ] Splits match production reality (time-based for temporal data, grouped for repeated entities)
- [ ] Evaluation reports the metric the product decision depends on, with slice/subgroup breakdowns, not just a global average
- [ ] Baseline comparison exists; a claimed improvement is outside run-to-run noise (seeds, multiple runs)
- [ ] Randomness is seeded and environment, data version, and config are recorded for reproducibility

## Experiment Tracking

- [ ] Every run logs code version, data version, config/hyperparameters, and metrics
- [ ] Artifacts (models, plots, eval outputs) are stored with lineage back to the run
- [ ] No secrets or raw sensitive data are logged as params or artifacts

## Model Deployment and Serving

- [ ] Training/serving skew is prevented: the same feature code or feature store definition is used in both paths
- [ ] Input validation and schema checks guard the inference endpoint
- [ ] Rollout is staged (shadow, canary, or A/B) with a tested rollback to the previous model version
- [ ] Monitoring covers latency, errors, input drift, and prediction/outcome quality, with owners for alerts
- [ ] Model version is visible in logs and responses so incidents can be traced to a specific artifact
