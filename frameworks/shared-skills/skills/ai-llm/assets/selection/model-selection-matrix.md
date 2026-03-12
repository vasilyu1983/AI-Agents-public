# LLM Model Selection Matrix

**Purpose**: Systematic model comparison with documented rationale for enterprise decisions.

---

## Template Contract

### Goals
- Select a model that meets quality, latency, cost, and governance requirements.
- Document rationale to enable repeatability, auditability, and future re-evaluation.

### Inputs
- Task definition and acceptance criteria.
- Representative traffic samples and a golden eval set.
- Non-functional requirements: latency, throughput, availability, and budget.
- Governance requirements: privacy, residency, licensing, retention, compliance.

### Decisions
- Primary model, fallback model(s), and routing criteria.
- Deployment mode (managed API, self-hosted, hybrid) and data handling posture.
- Change management gates (eval pass, canary, rollback).

### Risks
- Vendor lock-in, deprecations, and pricing changes.
- Data leakage/retention and compliance violations.
- Silent regressions on upgrades (quality, safety, latency).

### Metrics
- Task success rate, refusal correctness, and safety violation rate.
- Latency p95/p99, cost per request, and error rate.
- Stability metrics: variance across runs, drift sensitivity.

## 1. Task Requirements

### Primary Task
- [ ] Task type: [ ] Generation [ ] Classification [ ] Extraction [ ] Reasoning [ ] Code [ ] Multimodal
- [ ] Quality requirement: [ ] High (critical path) [ ] Medium (user-facing) [ ] Acceptable (internal)
- [ ] Latency budget: ___ms P95
- [ ] Cost budget: $___/1K requests
- [ ] Context length needed: ___tokens
- [ ] Output length typical: ___tokens

### Constraints
- [ ] Data residency: [ ] Any [ ] US-only [ ] EU-only [ ] Specific: ___
- [ ] Deployment: [ ] API-only [ ] On-premise [ ] Hybrid
- [ ] Fine-tuning needed: [ ] Yes [ ] No [ ] Maybe future
- [ ] Compliance: [ ] SOC2 [ ] HIPAA [ ] GDPR [ ] FedRAMP [ ] None

---

## 2. Model Comparison Matrix

### Scoring Guide (1-10)
- **Quality**: Task-specific benchmark performance
- **Latency**: Time to first token + generation speed
- **Cost**: Per 1K token (input + output weighted)
- **Context**: Maximum context window size
- **Reliability**: Uptime, rate limits, consistency

| Model | Quality | Latency | Cost | Context | License | Weighted Score |
|-------|---------|---------|------|---------|---------|----------------|
| Candidate 1 | /10 | /10 | /10 | ___ | ___ | |
| Candidate 2 | /10 | /10 | /10 | ___ | ___ | |
| Candidate 3 | /10 | /10 | /10 | ___ | ___ | |

### Weights (must sum to 1.0)
- Quality: ___
- Latency: ___
- Cost: ___
- Context: ___
- License fit: ___

---

## 3. Licensing Matrix

| Candidate | License Type | Commercial Use | Fine-tuning | Data Retention | Notes |
|----------|--------------|----------------|-------------|----------------|-------|
| Candidate 1 | Proprietary API | ___ | ___ | ___ | |
| Candidate 2 | Open-weight (permissive) | ___ | ___ | N/A | |
| Candidate 3 | Open-weight (restricted) | ___ | ___ | N/A | |

---

## 4. Cost Projection

### Per Request Estimate
- Average input tokens: ___
- Average output tokens: ___
- Requests per day: ___
- Requests per month: ___

| Model | Input $/1K | Output $/1K | Est. Daily | Est. Monthly |
|-------|-----------|-------------|------------|--------------|
| | | | | |
| | | | | |
| | | | | |

---

## 5. Risk Assessment

| Risk | Likelihood (1-5) | Impact (1-5) | Mitigation |
|------|-----------------|--------------|------------|
| API rate limits | | | Fallback provider, request batching |
| Model deprecation | | | Abstraction layer, provider agnostic |
| Cost increases | | | Budget alerts, model tiering |
| Quality regression | | | Evaluation suite, A/B testing |
| Vendor lock-in | | | Multi-provider strategy |
| Data leakage | | | Zero retention, private endpoints |

---

## 6. Evaluation Results

### Benchmark Scores (Task-Specific)

| Model | Benchmark 1 | Benchmark 2 | Benchmark 3 | Overall |
|-------|-------------|-------------|-------------|---------|
| | | | | |

### Latency Testing (P50/P95/P99)

| Model | TTFT P50 | TTFT P95 | Total P50 | Total P95 |
|-------|----------|----------|-----------|-----------|
| | | | | |

---

## 7. Decision

**Primary Model**: _______________

**Rationale**:
1. _______________
2. _______________
3. _______________

**Fallback Model**: _______________

**Fallback Trigger**:
- [ ] Primary unavailable >30s
- [ ] Rate limit exceeded
- [ ] Cost threshold exceeded
- [ ] Other: _______________

**Re-evaluation Date**: _______________

---

## 8. Governance

### Approval Chain
- [ ] Technical Lead: _______________ Date: ___
- [ ] Security Review: _______________ Date: ___
- [ ] Legal/Compliance: _______________ Date: ___
- [ ] Budget Approval: _______________ Date: ___

### Change Management
- Model changes require: [ ] A/B test [ ] Evaluation suite pass [ ] Stakeholder approval
- Minimum notice for deprecation: ___ days
- Rollback procedure documented: [ ] Yes [ ] No
