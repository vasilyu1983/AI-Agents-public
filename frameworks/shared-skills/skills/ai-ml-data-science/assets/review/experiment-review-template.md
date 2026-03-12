# ML Experiment Review Template

**Purpose**: Ensure reproducibility, validate methodology, document decisions for future reference.

---

## Template Contract

### Goals
- Validate methodology, prevent leakage, and document decisions.
- Make results reproducible and interpretable for stakeholders.

### Inputs
- Problem statement + success criteria.
- Dataset version(s), split strategy, and feature definitions.
- Experiment config (code commit, environment, seeds).

### Decisions
- Baseline and final model selection, metric thresholds, and deployment recommendation.
- Follow-up actions for failure modes and slices.

### Risks
- Leakage, metric gaming, overfitting narratives, and non-reproducible runs.
- Miscommunication of uncertainty and limitations.

### Metrics
- Primary/secondary metrics with confidence intervals.
- Slice performance and calibration (where applicable).

## 1. Experiment Metadata

```yaml
experiment_id: ""
created: "YYYY-MM-DD"
author: ""
hypothesis: ""
status: "planning | running | completed | abandoned"
repository: ""
commit_hash: ""
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
- **Prediction horizon**: _______________
- **Baseline to beat**: _______________

---

## 3. Data Review

### Dataset Summary

| Attribute | Value |
|-----------|-------|
| Source | |
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

### Data Contract
- [ ] Schema documented
- [ ] Expected distributions documented
- [ ] Freshness requirements defined
- [ ] Data source reliability assessed

---

## 4. Feature Engineering

### Feature Summary

| Feature | Type | Source | Rationale | Importance |
|---------|------|--------|-----------|------------|
| | | | | |

### Feature Validation

| Check | Status | Notes |
|-------|--------|-------|
| No target leakage | [ ] Pass | |
| Temporal validity | [ ] Pass | All features available at prediction time |
| Missing handled | [ ] Pass | Imputation strategy: ___ |
| Encoding appropriate | [ ] Pass | |

### Feature Importance (Top 10)

| Rank | Feature | Importance Score | Method |
|------|---------|-----------------|--------|
| 1 | | | |
| 2 | | | |
| ... | | | |

---

## 5. Modeling

### Baseline
- **Model**: _______________
- **Metric**: _______________
- **Score**: _______________

### Models Evaluated

| Model | Hyperparameters | CV Score | Test Score | Training Time |
|-------|----------------|----------|------------|---------------|
| | | | | |

### Final Model
- **Selected model**: _______________
- **Key hyperparameters**: _______________
- **Selection rationale**: _______________

### Hyperparameter Tuning
- **Method**: [ ] Grid [ ] Random [ ] Bayesian [ ] Manual
- **Search space**: _______________
- **Best parameters**: _______________
- **Tuning logged in**: _______________

---

## 6. Evaluation

### Cross-Validation

| Fold | Score | Notes |
|------|-------|-------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |
| **Mean +/- Std** | | |

### Test Set Results

| Metric | Train | Validation | Test | Baseline |
|--------|-------|------------|------|----------|
| Primary | | | | |
| Secondary 1 | | | | |
| Secondary 2 | | | | |

### Statistical Significance
- **Test vs Baseline**: p-value = ___
- **Confidence level**: ___%
- **Effect size**: ___

### Sliced Analysis

| Slice | N | Metric | vs Overall | Action |
|-------|---|--------|------------|--------|
| | | | | |

### Calibration (if probabilities)
- [ ] Calibration plot reviewed
- [ ] Brier score: ___
- [ ] Calibration method applied: _______________

---

## 7. Uncertainty Communication

### Point Estimate
- **Metric**: _______________
- **Value**: _______________

### Confidence Interval
- **95% CI**: [___, ___]
- **Method**: [ ] Bootstrap [ ] Analytical [ ] Other

### Known Limitations
1. _______________
2. _______________
3. _______________

### Failure Modes
1. _______________
2. _______________

---

## 8. Reproducibility

### Environment
- **Python version**: ___
- **Key packages**: _______________
- **Requirements file**: _______________
- **Random seed**: ___

### Artifacts
- [ ] Code committed: [commit hash]
- [ ] Data version: _______________
- [ ] Model artifact saved: _______________
- [ ] Metrics logged: _______________

### Re-run Instructions
```bash
# Commands to reproduce
```

---

## 9. Decision

### Recommendation
- [ ] **Deploy**: Results meet threshold, proceed to production
- [ ] **Iterate**: Promising but needs improvement on _______________
- [ ] **Abandon**: Does not beat baseline meaningfully
- [ ] **Pivot**: Reframe problem as _______________

### Justification
_______________

### Next Steps
1. _______________
2. _______________
3. _______________

---

## 10. Anti-Patterns Check

| Anti-Pattern | Status | Notes |
|--------------|--------|-------|
| Metric gaming | [ ] Clear | |
| Overfitting narrative | [ ] Clear | Results match hypothesis confirmation? |
| Leakage overlooked | [ ] Clear | |
| Statistical significance ignored | [ ] Clear | |
| Business impact unclear | [ ] Clear | |
| Reproducibility broken | [ ] Clear | |

---

## 11. Sign-Off

| Role | Name | Date | Decision |
|------|------|------|----------|
| Data Scientist | | | |
| ML Engineer | | | |
| Domain Expert | | | |
| Product Owner | | | |
