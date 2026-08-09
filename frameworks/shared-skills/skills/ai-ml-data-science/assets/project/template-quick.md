# Quick DS Workflow Template

Use this for short experiments, feasibility checks, or fast iteration cycles.

---

## Objective

<Define the problem in 2-3 sentences.>

**Decision Triggered:** <what will the model output change?>

**Prediction Timestamp:** <what information is available at scoring time?>

---

## Data

- Dataset(s): <names>
- Version / snapshot: <id>
- Rows / columns: <shape>
- Main quality issues: <list>

---

## EDA Notes

- Top findings
- Missingness summary
- Leakage risks
- Key slices to watch

---

## Features

- Key engineered features
- Encoders / transforms used
- Point-in-time safeguards

---

## Models Tried

- Baseline: <model + metric>
- Candidate(s): <models>
- Split strategy: <temporal / group / random>

---

## Evaluation

- Primary metric: <value>
- Threshold / ranking rule: <value>
- Calibration checked: <yes/no + note>
- Uncertainty checked: <yes/no + note>

---

## Best Current Candidate

- Model: <name>
- Why it wins: <short reason>
- Main limitation: <short reason>

---

## Recommendation

- <Deploy / Iterate / Reject>
- Next step: <single next action>
