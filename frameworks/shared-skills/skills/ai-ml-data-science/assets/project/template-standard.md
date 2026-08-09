# Standard Data Science Project Template

Use this template for a full DS project plan, experiment package, or model-candidate handoff.

---

## 1. Project Overview

**Objective:**  
<Describe the business problem, target outcome, and decision impact.>

**Decision Triggered By Model:**  
<What action will a prediction or score cause?>

**Task Type:**  
<classification / regression / ranking / forecasting-like event modelling / other>

**Prediction Timestamp / Decision Point:**  
<Exactly what information is available when the prediction is made?>

---

## 2. Success Criteria

- Primary metric: <metric>
- Baseline to beat: <baseline>
- Minimum acceptable threshold for success: <value>

**Guardrails**

- Calibration: <required / not required>
- Uncertainty or interval requirement: <required / not required>
- Fairness or sensitive-slice constraints: <list>
- Latency / cost / size constraints: <list>

---

## 3. Reproducible Environment

- Runtime manager: <uv / other>
- Python version: <version>
- Entry points: <scripts / marimo notebook / package module>
- Key dependencies: <list>
- Experiment tracking: <MLflow / W&B / other>

---

## 4. Data Summary

| Dataset | Source | Version / Snapshot | Time Range | Rows | Notes |
|--------|--------|--------------------|------------|------|-------|
|        |        |                    |            |      |       |

**Data Risks**

- <coverage gap>
- <label quality issue>
- <freshness issue>

**Contracts / Validation**

- Schema validation: <Pandera / GX Core / other>
- Freshness expectation: <details>
- Duplicate / entity checks: <details>

---

## 5. EDA Summary

- Top findings
- Missingness overview
- Outlier patterns
- Leakage risks
- Slice risks
- Target distribution notes

---

## 6. Feature Engineering Plan

**Feature Set Version:**  
<vX.Y>

**Numeric Features:**  
- Scaling: <method>
- Outlier handling: <method>

**Categorical Features:**  
- Encoding method: <one-hot / target / frequency / CatBoost-native / other>

**Text / Embeddings:**  
- Representation: <tfidf / embeddings / other>

**Datetime / Event Features:**  
- Extracted: <list>
- Timezone handling: <details>
- Point-in-time safeguards: <details>

**Train / Serve Parity**

- Offline transform path: <details>
- Serving-time or shared transform path: <details>

---

## 7. Modelling Plan

**Baselines**

- Simple baseline: <name>
- Interpretable baseline: <name>

**Candidate Models**

- Candidate 1: <model>
- Candidate 2: <model>

**Validation Strategy**

- Split type: <temporal / group / random>
- Validation design: <holdout / CV / rolling window>
- Final test set: <size and rationale>
- Seed policy: <single / repeated seeds>

**Tuning Budget**

- Search method: <manual / random / Bayesian>
- Trial budget: <count or compute budget>

---

## 8. Evaluation Plan

**Primary Metric:** <metric>

**Threshold / Decision Policy:**  
<operating threshold, top-k rule, or interval policy>

**Calibration Plan:**  
<how calibration will be checked or improved>

**Uncertainty Plan:**  
<bootstrap CI / prediction intervals / conformal / none>

**Slice Evaluation**

- geography / market: <yes/no>
- user or product segment: <yes/no>
- recency / time period: <yes/no>
- sensitive features: <yes/no and conditions>

---

## 9. Deliverables

- Reproducible analysis entrypoint
- Data validation checks
- Feature engineering specification
- Training pipeline or script
- Evaluation report
- Model card
- Production handoff package

---

## 10. Deployment Readiness Gate

- [ ] Beats baseline meaningfully
- [ ] Threshold or ranking policy defined
- [ ] Calibration reviewed
- [ ] Uncertainty treatment reviewed
- [ ] Weak slices documented with actions
- [ ] Risks and rollback notes documented
- [ ] Owner assigned

---

## 11. Risks & Mitigations

| Risk | Mitigation | Owner |
|------|------------|-------|
|      |            |       |

---

## 12. Final Recommendation

- Recommendation: <Deploy / Iterate / Reject>
- Reason: <short explanation>
- Next owner: <team / person>
