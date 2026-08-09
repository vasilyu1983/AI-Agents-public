# Evaluation Patterns

Operational guidance for deciding whether an ML candidate is ready to deploy, iterate, or reject. Focus on metrics, thresholds, calibration, uncertainty, slice analysis, and explicit recommendation criteria.

---
## Table of Contents

- [1. Start With The Decision](#1-start-with-the-decision)
- [2. Metric, Threshold, And Calibration Selection](#2-metric-threshold-and-calibration-selection)
- [2.1 Primary Metrics](#21-primary-metrics)
- [2.2 Guardrail Metrics](#22-guardrail-metrics)
- [2.3 Threshold Selection](#23-threshold-selection)
- [3. Slice, Error, And Temporal Analysis](#3-slice-error-and-temporal-analysis)
- [3.1 Slice Analysis](#31-slice-analysis)
- [3.2 Error Analysis](#32-error-analysis)
- [3.3 Temporal Robustness](#33-temporal-robustness)
- [4. Uncertainty And Confidence](#4-uncertainty-and-confidence)
- [4.1 Classification](#41-classification)
- [4.2 Regression](#42-regression)
- [4.3 What To Report](#43-what-to-report)
- [5. Recommendation Logic](#5-recommendation-logic)
- [5.1 Deployment Readiness Gate](#51-deployment-readiness-gate)
- [6. Evaluation Report Structure](#6-evaluation-report-structure)
- [7. Model Card Structure](#7-model-card-structure)
- [8. Common Failure Modes](#8-common-failure-modes)
- [9. Practical Defaults](#9-practical-defaults)


## 1. Start With The Decision

Before choosing metrics, write down:

- the action the model output will trigger
- whether the output is a score, thresholded label, top-k ranking, or interval
- the baseline to beat
- the cost of false positives, false negatives, or over/under-estimation

**Rule:** evaluation is incomplete if it reports only an aggregate offline score and ignores the downstream decision rule.

**Checklist: Decision Context**

- [ ] Decision or workflow triggered by the model is documented
- [ ] Baseline and minimum acceptable performance are documented
- [ ] Output type is explicit: score, label, rank, or interval
- [ ] Business or operational costs are listed

---

## 2. Metric, Threshold, And Calibration Selection

### 2.1 Primary Metrics

**Classification**

- **ROC-AUC**: useful ranking metric, but insufficient when the decision uses a threshold
- **PR-AUC**: preferred for imbalanced positive classes
- **Log loss**: useful when probability quality matters
- **F1 / F-beta**: acceptable when the business truly values a specific precision/recall tradeoff

**Regression**

- **MAE**: robust default when median-like error matters
- **RMSE**: use when large misses are materially worse
- **Pinball loss / interval coverage**: use when quantiles or decision bands matter

**Ranking**

- **NDCG**
- **MAP**
- **Recall@K**

### 2.2 Guardrail Metrics

Track these alongside the primary metric:

- **Calibration**: Brier score, calibration curve, expected calibration error
- **Fairness / segment parity**: performance gaps across sensitive or operationally important slices
- **Latency / size / cost**: inference constraints still matter in offline evaluation
- **Stability**: variance across folds, time splits, or seeds

### 2.3 Threshold Selection

Document threshold choice explicitly. Common patterns:

1. **Cost-sensitive thresholding**: convert FP/FN costs to an operating point
2. **Capacity-based thresholding**: score top N or top X%
3. **Utility-maximizing thresholding**: optimize profit, save rate, or review yield
4. **Calibrated policy thresholding**: choose cutoff only after probabilities are calibrated

**Checklist: Metrics And Thresholds**

- [ ] Primary metric chosen and justified
- [ ] Guardrails chosen and justified
- [ ] Threshold rule documented
- [ ] Threshold compared against baseline policy
- [ ] Metric definitions are reproducible

---

## 3. Slice, Error, And Temporal Analysis

### 3.1 Slice Analysis

Minimum slices usually include:

- geography or market
- user/account/product segment
- time period or recency cohort
- confidence bucket
- common vs rare cases
- sensitive features where allowed and appropriate

For each slice, record:

- sample size
- primary metric
- thresholded outcome metric if relevant
- calibration or interval behavior where relevant
- action required if the slice is weak

### 3.2 Error Analysis

Review concrete examples, not just tables:

- false positives and false negatives separately
- highest-loss regression examples
- low-confidence correct predictions
- drifted or recently failing cases

Cluster failure modes into a short taxonomy such as:

- label quality issue
- missing feature
- stale data
- threshold problem
- calibration problem
- coverage gap

### 3.3 Temporal Robustness

If data changes over time, inspect:

- metric drift by month or quarter
- calibration drift by period
- threshold stability over recent windows

**Checklist: Slice And Error Review**

- [ ] Core operational slices reviewed
- [ ] Weak slices explained with hypotheses
- [ ] Example-level failures reviewed
- [ ] Temporal robustness checked when relevant
- [ ] Remediation ideas recorded

---

## 4. Uncertainty And Confidence

Use uncertainty-aware reporting when decisions are risk-sensitive.

### 4.1 Classification

- confidence intervals on metrics via bootstrap or repeated CV
- calibrated probabilities when a score is treated as a likelihood
- optional conformal or abstention policies when low-confidence cases are routed to review

### 4.2 Regression

- prediction intervals or quantile estimates
- coverage checks on held-out data
- interval width analysis by slice

### 4.3 What To Report

At minimum, include:

- point estimate
- interval or variance estimate
- method used
- practical interpretation for decision-makers

**Checklist: Uncertainty**

- [ ] Metric uncertainty reported for key claims
- [ ] Probability calibration checked when probabilities are used
- [ ] Prediction intervals or quantiles checked when outputs need ranges
- [ ] Uncertainty communication is understandable to non-DS readers

---

## 5. Recommendation Logic

End every serious evaluation with one of:

- **Deploy**: beats baseline, threshold/calibration are acceptable, key slices are understood, and risks are manageable
- **Iterate**: promising, but blocked by specific weaknesses such as calibration, slice gaps, or instability
- **Reject / Hold**: does not beat baseline meaningfully, fails critical constraints, or risks are not acceptable

### 5.1 Deployment Readiness Gate

A candidate is not deployment-ready unless all of these are answered:

- What baseline did it beat?
- What threshold or ranking policy will production use?
- Is probability calibration acceptable?
- Are uncertainty bounds acceptable?
- Which slices are weakest, and what is the mitigation?
- What inputs/outputs/versioning assumptions must MLOps preserve?

**Checklist: Final Recommendation**

- [ ] Recommendation is explicit: deploy, iterate, or reject
- [ ] Recommendation references evidence, not intuition
- [ ] Open risks and mitigations are listed
- [ ] Handoff notes are complete enough for operations or reviewers

---

## 6. Evaluation Report Structure

Use this order:

1. Objective and decision context
2. Dataset versions, time windows, and limitations
3. Feature and prediction-time assumptions
4. Baselines and candidate models
5. Metrics, threshold policy, and calibration
6. Slice and error analysis
7. Uncertainty and confidence
8. Risks, mitigations, and recommendation

The report should support a reviewer answering: "Should we act on this model now?"

---

## 7. Model Card Structure

Keep model cards shorter than full reports, but include:

- intended use and out-of-scope use
- dataset and version summary
- prediction-time assumptions
- core performance metrics
- threshold or decision policy
- calibration / uncertainty summary
- sensitive-slice or fairness notes
- owner, maintenance plan, and contact path

---

## 8. Common Failure Modes

- High ROC-AUC but poor threshold performance at the actual operating point
- Good aggregate metrics with unacceptable weak slices
- Strong ranking metrics with poor calibration
- Narrow intervals with poor actual coverage
- Repeated CV improvement that disappears on the true holdout
- "Deploy" recommendation without threshold, owner, or rollback expectations

---

## 9. Practical Defaults

- If the model triggers an action, always report thresholded performance alongside ranking metrics.
- If the model emits probabilities, always inspect calibration.
- If the output is used for planning or budgeting, report intervals, not just point estimates.
- If the data is time-sensitive, always review recent-window performance separately.
- If the result is close to baseline, default to `iterate`, not `deploy`.

---

## 10. Benchmark Contamination

**Scope:** apply this section when evaluating LLM-based models, or any model trained on large crawled corpora where test data may have appeared in pretraining or fine-tuning data. For classical ML with small curated datasets, standard train/test split hygiene (§2 of `modelling-patterns.md`) is sufficient.

### 10.1 Detection

**MinHash near-duplicate matching:**
- Compute MinHash signatures for benchmark examples and training documents
- Use LSH at Jaccard similarity threshold 0.5–0.7 to catch near-matches
- Flag training documents that overlap with any benchmark split; remove before final training run or report results with and without contaminated examples

**Exact n-gram matching:**
- 13-gram overlap is a common threshold (used in LLaMA evaluations and similar work)
- Fast and interpretable; use as a first pass before MinHash

**Min-K% Prob (post-training detection):**
- Extract the k% of tokens with lowest log-probability under the model for a given input
- Contaminated examples tend to have higher min-k% probability than held-out examples
- Applicable when training corpus access is limited; does not require corpus re-scanning
- Reference: arXiv 2310.16789 (verify before citing specific figures)

### 10.2 Contamination-Resistant Benchmark Choice

When contamination risk is non-trivial:

- Prefer recently released benchmarks not present in the training data window
- Prefer benchmarks with procedural or dynamic generation (new instances per run)
- Consider private held-out test sets for high-stakes comparisons
- Report contamination analysis results alongside benchmark scores — do not omit when detected

**Checklist: Contamination**

- [ ] Contamination scope assessed: is training data large/crawled enough to warrant checking?
- [ ] MinHash or n-gram check run between training corpus and evaluation benchmarks
- [ ] Contaminated examples quarantined and results reported with/without them
- [ ] Benchmark choice accounts for contamination risk; newer or procedural benchmarks preferred when risk is high
