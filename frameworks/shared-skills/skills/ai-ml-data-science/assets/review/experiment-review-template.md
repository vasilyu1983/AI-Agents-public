# ML Experiment Review Template

**Purpose**: validate methodology, prevent leakage, and document whether the experiment is ready for production handoff.

---

## Template Contract

### Goals
- Validate methodology, prevent leakage, and document decisions.
- Make results reproducible and interpretable for reviewers and stakeholders.

### Inputs
- Problem statement and success criteria.
- Dataset version(s), split strategy, and feature definitions.
- Experiment config (code commit, environment, seeds).

### Decisions
- Baseline and final model selection, threshold policy, calibration status, and deployment recommendation.

### Risks
- Leakage, metric gaming, overfitting narratives, unstable calibration, and non-reproducible runs.

### Metrics
- Primary and secondary metrics with confidence intervals or intervals where applicable.
- Slice performance, calibration, and threshold tradeoffs.

## 1. Experiment Metadata

```yaml
experiment_id: ""
created: "YYYY-MM-DD"
author: ""
hypothesis: ""
status: "planning | running | completed | abandoned"
repository: ""
commit_hash: ""
environment: ""
dataset_version: ""
feature_set_version: ""
prediction_timestamp_rule: ""
```

---

## 2. Problem Definition

### Business Context
- **Problem statement**: _______________
- **Success criteria**: _______________
- **Stakeholder**: _______________
- **Timeline**: _______________

### ML Framing
- **Task type**: [ ] Classification [ ] Regression [ ] Ranking [ ] Clustering [ ] Other
- **Target variable**: _______________
- **Prediction horizon / timestamp**: _______________
- **Baseline to beat**: _______________

---

## 3. Data Review

### Dataset Summary

| Attribute | Value |
|-----------|-------|
| Source | |
| Version | |
| Rows | |
| Columns | |
| Time range | |
| Target distribution | |
| Missing rate (overall) | |

### Leakage Check (CRITICAL)

| Check | Status | Notes |
|-------|--------|-------|
| No features derived from target | [ ] Pass [ ] Fail | |
| No future data in features | [ ] Pass [ ] Fail | |
| Train/test split is appropriate | [ ] Pass [ ] Fail | Temporal if time-based |
| Global statistics on train only | [ ] Pass [ ] Fail | Scalers, encoders |
| No test data in validation | [ ] Pass [ ] Fail | |

### Data Quality

| Check | Result | Action Taken |
|-------|--------|--------------|
| Missing values | ___% | |
| Duplicates | ___% | |
| Outliers | ___ detected | |
| Class balance | Ratio: ___ | |
| Feature types correct | [ ] Yes [ ] No | |

### Sensitive Features And Slices
- [ ] Sensitive attributes identified
- [ ] High-risk slices identified
- [ ] Exclusions documented

---

## 4. Feature Engineering

### Feature Summary

| Feature | Type | Source | Available At Prediction Time? | Rationale |
|---------|------|--------|-------------------------------|-----------|
| | | | | |

### Feature Validation

| Check | Status | Notes |
|-------|--------|-------|
| No target leakage | [ ] Pass | |
| Temporal validity | [ ] Pass | All features available at prediction time |
| Missing handled | [ ] Pass | Imputation strategy: ___ |
| Encoding appropriate | [ ] Pass | |
| Train/serve parity | [ ] Pass | |

---

## 5. Model Review

### Candidate Models

| Model | Purpose | Primary Metric | Notes |
|-------|---------|----------------|-------|
| | | | |

### Decision Policy
- **Selected threshold or policy**: _______________
- **Calibration status**: _______________
- **Uncertainty treatment**: _______________

### Stability
- [ ] Seeds logged
- [ ] Multiple runs compared where needed
- [ ] Environment captured

---

## 6. Evaluation Review

| Check | Status | Notes |
|-------|--------|-------|
| Primary metric justified | [ ] Pass | |
| Guardrails defined | [ ] Pass | |
| Threshold tradeoff documented | [ ] Pass | |
| Calibration reviewed | [ ] Pass | |
| Uncertainty documented | [ ] Pass | |
| Slice analysis completed | [ ] Pass | |
| Error review completed | [ ] Pass | |

### Final Recommendation
- [ ] Deploy
- [ ] Iterate
- [ ] Reject

**Conditions before deploy:** __________________________________

**Fallback or rollback candidate:** _____________________________
