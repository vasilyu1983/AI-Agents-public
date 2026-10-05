---
description: Data Science — expert-board data-science mode for modelling, forecasting, and quantum-fit decisions.
last_verified: 2026-09-30
status: stable
---

## Data Science

**Typical scenario**

A team has a candidate model or forecast and needs to know whether the evaluation supports shipping it, or a stakeholder asks whether a quantum or foundation-model approach beats the current baseline.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "data-science"`.

Scenario: Decide whether the new gradient-boosted churn model should replace the logistic baseline.

Required context:
- decision_and_metric: retention offers go to the top 5% by churn risk; precision at 5% drives offer cost
- data_description: 18 months of account events, label = cancellation within 60 days
- operating_constraints: weekly batch scoring, no GPU, model must be explainable to CRM owners

Instructions:
- ai-data-scientist audits leakage, split design, baselines, and threshold choice
- ai-forecasting-scientist checks temporal validity: refit cadence and features unknown at scoring time
- ai-mlops-engineer checks training-serving skew, reproducibility, and rollback
- The expansion gate admits ai-quantum-data-scientist only when a quantum approach is on the table
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn ai_data_scientist, ai_forecasting_scientist, and ai_mlops_engineer in parallel; add ai_quantum_data_scientist only for a quantum question.

Task: decide whether the new churn model should replace the logistic baseline.

Return:
- whether the evaluation supports the claimed gain at the decision threshold
- leakage, temporal-validity, and skew risks found or ruled out
- adopt, hold for evidence, or reject, with the single gap that would change it
```
