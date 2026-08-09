# Model Evaluation Report

Use this report when deciding whether a model candidate should deploy, iterate, or be rejected.

---

## 1. Executive Summary

- Recommendation: <Deploy / Iterate / Reject>
- Primary reason: <short explanation>
- Baseline beaten: <yes/no>
- Main open risk: <short explanation>

---

## 2. Objective And Decision Context

- Business context
- Intended action triggered by the model
- Task type
- Prediction timestamp / decision point
- Success criteria

---

## 3. Data Description

| Dataset | Version / Snapshot | Size | Time Range | Notes |
|--------|---------------------|------|------------|-------|

**Known Data Risks**

- <risk 1>
- <risk 2>

**Validation / Contract Checks**

- Schema validation: <details>
- Freshness expectation: <details>
- Leakage checks completed: <details>

---

## 4. Feature Engineering Summary

- Key numeric features
- Categorical encodings
- Text / embedding features
- Datetime / event features
- Train / serve parity notes
- Prediction-time availability notes

---

## 5. Model Experiments

| Model | Split Strategy | Primary Metric | Notes |
|-------|----------------|----------------|-------|

**Final Candidate Chosen Because**

- <reason 1>
- <reason 2>

---

## 6. Metrics, Threshold, And Calibration

- Primary metric: <value>
- Guardrails: <list>
- Threshold / ranking policy: <details>
- Calibration status: <checked / adjusted / not applicable>
- Calibration metric(s): <Brier / ECE / note>

---

## 7. Slice Analysis

| Slice | N | Metric | Gap vs Overall | Action |
|-------|---|--------|----------------|--------|

---

## 8. Error Analysis

- Systematic error patterns
- Representative failure cases
- Hypothesized causes
- Candidate fixes

---

## 9. Uncertainty

- Metric confidence interval: <value>
- Method: <bootstrap / repeated CV / other>
- Prediction interval or conformal method: <details / n/a>
- Interpretation for stakeholders: <short explanation>

---

## 10. Risks And Mitigations

| Risk | Mitigation |
|------|------------|
|      |            |

---

## 11. Deployment Readiness

- [ ] Beats baseline meaningfully
- [ ] Threshold or ranking rule defined
- [ ] Calibration reviewed
- [ ] Uncertainty treatment reviewed
- [ ] Weak slices documented
- [ ] Owner and monitoring expectations defined

---

## 12. Appendix

- Hyperparameters
- Seeds
- Environment info
- Reproduction command(s)
