# Data Contracts, Lineage & Feature Store Operations

Operational patterns for managing data contracts, lineage tracking, and feature store hygiene in production ML systems.

---

## Overview

Data contracts and lineage tracking are critical for production ML systems. They ensure data quality, enable debugging, and maintain train-serve consistency. This guide covers modern best practices for feature store operations and data governance.

---

## 1. Data Contracts

### 1.1 Contract Components

A robust data contract defines:

- **Schema**: Column names, types, nullability constraints
- **Ranges & Constraints**: Min/max values, allowed categorical values, regex patterns
- **Freshness SLAs**: Maximum acceptable data lag
- **Versioning**: Contract version number and compatibility rules

### 1.2 Contract Enforcement

**When to check contracts:**
- At data ingestion (source -> feature store)
- Before training (feature store -> training pipeline)
- At serving time (feature store -> production model)

**Enforcement strategy:**
- **Fail fast**: Block pipeline on critical contract violations
- **Warn**: Log non-critical violations but continue
- **Degrade gracefully**: Use fallback values for optional fields

### 1.3 Schema Evolution

**Backward-compatible changes (safe):**
- Adding optional fields
- Relaxing constraints (e.g., widening ranges)
- Adding new enum values

**Breaking changes (require coordination):**
- Removing fields
- Changing data types
- Renaming columns
- Tightening constraints

**Migration strategy:**
1. Version the contract (v1 -> v2)
2. Run shadow mode (dual write to v1 and v2)
3. Validate v2 data quality matches v1
4. Gradual cutover with rollback plan
5. Deprecate v1 after validation period

**Checklist: Schema Evolution**

- [ ] Contract version incremented
- [ ] Backward/forward compatibility assessed
- [ ] Shadow run completed successfully
- [ ] Rollback artifacts preserved
- [ ] Deprecation timeline communicated

---

## 2. Data Lineage Tracking

### 2.1 What to Track

**Essential lineage metadata:**
- Source system and extraction timestamp
- Feature store write timestamp and version
- Training run ID and model version
- Feature transformation code version (git commit)
- Data quality metrics at each stage

**Why it matters:**
- Debug data quality issues
- Audit compliance (GDPR, SOC2)
- Root cause analysis for model degradation
- Reproduce experiments

### 2.2 Lineage Implementation Patterns

**Storage:**
- Structured logs (JSON lines)
- Metadata stores (MLflow, DVC, Feast)
- Graph databases (Neo4j for complex lineage)

**Tagging convention:**
```python
lineage_metadata = {
    "source": "postgres://db/table",
    "extraction_ts": "2024-11-22T10:00:00Z",
    "feature_store_version": "v2.1",
    "git_commit": "a1b2c3d4",
    "run_id": "train-20241122-001",
    "model_version": "v1.5.2",
    "feature_set_hash": "sha256:abcd1234..."
}
```

**Checklist: Lineage Implemented**

- [ ] Source -> feature store -> train -> serve path tracked
- [ ] Run IDs and model versions logged
- [ ] Git commits captured for reproducibility
- [ ] Lineage queryable (e.g., "which training runs used this data version?")
- [ ] Retention policy defined (how long to keep lineage)

---

## 3. Feature Store Hygiene

### 3.1 Materialization Cadence

**Document and enforce:**
- Batch update frequency (hourly, daily, weekly)
- Streaming update latency targets
- Backfill procedures for historical data

**Monitoring:**
- Freshness lag (source timestamp -> feature store timestamp)
- Materialization job success rate
- Data volume anomalies

### 3.2 Backfill & Replay

**Requirements for safe backfill:**
- Idempotent writes (duplicate runs produce same result)
- Timestamp-based partitioning
- Preserved input data snapshots
- Validation against production data

**Replay scenarios:**
- Bug fix in feature transformation logic
- Schema migration
- Historical model training
- Audit requirements

**Checklist: Backfill Ready**

- [ ] Backfill procedure documented and tested
- [ ] Idempotency verified (run twice -> same output)
- [ ] Validation metrics defined (replay vs original)
- [ ] Impact assessment for downstream consumers

### 3.3 Encoder & Mapping Versioning

**What to version:**
- Categorical encoders (target, frequency, hash)
- Normalization parameters (mean, std, min, max)
- Embedding models and weights
- Lookup tables and dictionaries

**Storage strategy:**
- Store alongside model artifacts
- Use feature store's versioning system
- Tag with training run ID
- Keep rollback versions

**Checklist: Encoders Versioned**

- [ ] All transformations serialized
- [ ] Encoder versions match training config
- [ ] Unseen category handling defined
- [ ] Serving uses same encoder version as training

---

## 4. Train-Serve Parity

### 4.1 Common Parity Issues

**Sources of divergence:**
- Different feature computation logic (Python vs SQL)
- Timezone mismatches
- Rounding/precision differences
- Async updates (training uses stale data)

**Detection:**
- Shadow mode: run both pipelines, compare features
- Synthetic tests with known inputs
- Production monitoring: track distribution drift

### 4.2 Ensuring Parity

**Best practices:**
- Single source of truth: shared feature transformation code
- Use feature store for both training and serving
- Integration tests: compare training vs serving features
- Monitor drift between training and production feature distributions

**Checklist: Parity Validated**

- [ ] Shared transformation code between train/serve
- [ ] Feature store used for both pipelines
- [ ] Integration tests pass (feature equality within tolerance)
- [ ] Drift monitoring active (KL divergence, PSI)
- [ ] Serving feature distributions match training

---

## 5. Monitoring & Alerts

### 5.1 Key Metrics

**Data quality:**
- Null rate per feature
- Out-of-range values
- Distribution shift (KL divergence, KS test, PSI)

**Freshness:**
- Data lag (source -> feature store)
- Staleness alerts (SLA violations)

**Operational:**
- Materialization job failures
- Query latency (p50, p99)
- Storage costs

### 5.2 Alert Strategy

**Critical (page on-call):**
- Contract violation blocking production
- Freshness SLA breach > 2x threshold
- Materialization job failures

**Warning (Slack/email):**
- Non-critical contract violations
- Minor distribution drift
- Performance degradation

**Checklist: Monitoring Active**

- [ ] Freshness SLAs defined and monitored
- [ ] Distribution drift alerts configured
- [ ] Contract violation alerts active
- [ ] Runbooks documented for common alerts
- [ ] False positive rate < 5%

---

## 6. Governance & Compliance

### 6.1 PII Handling

**Requirements:**
- PII identified and tagged in metadata
- Access controls enforced (RBAC)
- Audit logs for PII access
- Hard delete capability (GDPR right to erasure)

### 6.2 Data Residency

**Multi-region strategy:**
- Segment feature stores by region
- Enforce data sovereignty rules
- Replicate non-sensitive features
- Document cross-border data flows

**Checklist: Governance Ready**

- [ ] PII fields identified and tagged
- [ ] Access controls implemented
- [ ] Hard delete procedure tested
- [ ] Data residency requirements documented
- [ ] Audit trail enabled

---

## Related Resources

- [Feature Engineering Patterns](feature-engineering-patterns.md) - Feature transformation techniques
- [Reproducibility Checklist](reproducibility-checklist.md) - Experiment tracking and versioning
- [Feature Freshness & Streaming](feature-freshness-streaming.md) - Real-time feature updates
- [Production Feedback Loops](production-feedback-loops.md) - Online learning and model updates
