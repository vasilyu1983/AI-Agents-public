# Prompt Evaluation & Regression Test Template

**Purpose**: Establish baseline performance, detect regressions, enable data-driven iteration.

---

## Template Contract

### Goals
- Quantify prompt quality and safety with repeatable tests.
- Catch regressions before deploy and monitor after deploy.
- Enable controlled iteration (A/B, canary, rollback).

### Inputs
- Prompt text + variables + tool/RAG configuration.
- Golden dataset and acceptance criteria per category.
- Target models (or model tiers) and runtime settings.
- SLOs/budgets: latency, cost, error rate, safety thresholds.

### Decisions
- Metrics/thresholds, weights, and gating rules.
- Release strategy (shadow, canary, A/B) and rollback criteria.
- Model compatibility constraints and fallbacks.

### Risks
- Overfitting to the test set (prompt “metric gaming”).
- Silent regressions due to model/provider changes.
- Safety failures (leakage, injection susceptibility, policy violations).

### Metrics
- Accuracy/task success, format compliance, refusal correctness.
- Safety pass rate, citation coverage (if RAG), hallucination rate (sampled).
- Latency p95 and cost per request under representative load.

## 1. Prompt Metadata

```yaml
prompt_id: ""
version: ""  # Semantic: major.minor.patch
created: "YYYY-MM-DD"
last_modified: "YYYY-MM-DD"
author: ""
model_compatibility:
  - ""
description: ""
changelog: ""
```

### Version History

| Version | Date | Change Summary | Impact |
|---------|------|----------------|--------|
| | | | |

---

## 2. Test Suite Definition

### Test Categories

| Category | Count | Description |
|----------|-------|-------------|
| Happy path | ___ | Standard expected inputs |
| Edge cases | ___ | Boundary conditions |
| Adversarial | ___ | Malicious/tricky inputs |
| Format validation | ___ | Output structure tests |
| Safety | ___ | Refusal/policy tests |
| **Total** | ___ | Minimum 50 recommended |

### Golden Dataset

| ID | Input | Expected Output | Category | Difficulty | Pass Criteria |
|----|-------|-----------------|----------|------------|---------------|
| 1 | | | | | |
| 2 | | | | | |
| 3 | | | | | |
| ... | | | | | |

---

## 3. Evaluation Criteria

### Quantitative Metrics

| Criterion | Weight | Scoring Method | Threshold |
|-----------|--------|----------------|-----------|
| Accuracy | 0.30 | Exact match / Semantic similarity | >=0.90 |
| Relevance | 0.25 | LLM-as-judge (1-5 scale) | >=4.0 |
| Format compliance | 0.15 | Schema validation pass rate | >=0.95 |
| Latency | 0.15 | P95 < target | <2000ms |
| Cost | 0.15 | Tokens within budget | <___ tokens |

### Qualitative Assessment

| Dimension | Scoring Rubric |
|-----------|---------------|
| Tone | 1=Wrong, 2=Inconsistent, 3=Acceptable, 4=Good, 5=Perfect |
| Completeness | 1=Missing key info, 3=Adequate, 5=Comprehensive |
| Clarity | 1=Confusing, 3=Clear, 5=Exemplary |
| Safety | Pass/Fail (any violation = fail) |

---

## 4. Baseline Results

### Performance Baseline

| Metric | Baseline Value | Target | Status |
|--------|---------------|--------|--------|
| Accuracy | | >=0.90 | [ ] Pass [ ] Fail |
| Relevance (avg) | | >=4.0 | [ ] Pass [ ] Fail |
| Format compliance | | >=0.95 | [ ] Pass [ ] Fail |
| Latency P50 | | <___ms | [ ] Pass [ ] Fail |
| Latency P95 | | <___ms | [ ] Pass [ ] Fail |
| Cost per call | | <$___ | [ ] Pass [ ] Fail |
| Safety pass rate | | 100% | [ ] Pass [ ] Fail |

### Per-Category Results

| Category | Pass Rate | Notes |
|----------|-----------|-------|
| Happy path | ___% | |
| Edge cases | ___% | |
| Adversarial | ___% | |
| Format validation | ___% | |
| Safety | ___% | |

---

## 5. Regression Test Protocol

### Pre-Commit Gate
- [ ] Run against golden dataset (automated)
- [ ] Compare all metrics to baseline
- [ ] Flag if any metric drops >5%
- [ ] Block merge if safety tests fail

### Pre-Deploy Gate
- [ ] Run full test suite (all categories)
- [ ] A/B test on 5% shadow traffic
- [ ] Human review of 10 random outputs
- [ ] Compare cost projection to budget

### Post-Deploy Monitoring (24h)
- [ ] Monitor live accuracy metrics
- [ ] Sample 1% of responses for quality review
- [ ] Track user feedback/complaints
- [ ] Compare to baseline latency

### Rollback Criteria
Automatic rollback if:
- [ ] Accuracy drops >10% from baseline
- [ ] Any safety test fails in production
- [ ] Latency P95 exceeds SLA by >50%
- [ ] Cost exceeds budget by >25%

---

## 6. A/B Test Framework

### Experiment Setup

```yaml
experiment_id: ""
hypothesis: ""
control_prompt_version: ""
treatment_prompt_version: ""
traffic_split: 50/50
duration: "7 days"
primary_metric: ""
secondary_metrics: []
```

### Results Template

| Metric | Control | Treatment | Delta | Significant? |
|--------|---------|-----------|-------|--------------|
| | | | | |

### Decision Criteria
- [ ] Primary metric improved by >___% with p<0.05
- [ ] No secondary metric degraded by >___%
- [ ] Qualitative review passed

---

## 7. Model Compatibility Testing

### Cross-Model Results

| Model | Accuracy | Format | Latency | Cost | Notes |
|-------|----------|--------|---------|------|-------|
| Model A | | | | | |
| Model B | | | | | |
| Model C | | | | | |

### Model-Specific Adjustments
- GPT-4o: _______________
- Claude: _______________
- Gemini: _______________

---

## 8. Failure Analysis

### Common Failure Patterns

| Pattern | Frequency | Root Cause | Fix |
|---------|-----------|------------|-----|
| | | | |

### Edge Cases Requiring Attention

| Case | Current Behavior | Desired Behavior | Priority |
|------|-----------------|------------------|----------|
| | | | |

---

## 9. Versioning Best Practices

### Version Numbering
- **Major** (x.0.0): Breaking changes, fundamental restructure
- **Minor** (0.x.0): New capabilities, significant improvements
- **Patch** (0.0.x): Bug fixes, minor tweaks

### Required Documentation per Change
- [ ] What changed (diff or description)
- [ ] Why it changed (rationale)
- [ ] Expected impact (metrics)
- [ ] Rollback plan

### Prompt Registry
- [ ] All versions stored in version control
- [ ] Changelogs maintained
- [ ] Deprecated versions marked
- [ ] Migration guides for major versions

---

## 10. Sign-Off

### Pre-Production Checklist
- [ ] All regression tests pass
- [ ] Human review completed
- [ ] Cost projection approved
- [ ] Rollback procedure documented

### Approvals

| Role | Name | Date |
|------|------|------|
| Prompt Engineer | | |
| ML Engineer | | |
| Product Owner | | |
