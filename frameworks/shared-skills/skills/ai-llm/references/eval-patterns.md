# Evaluation Patterns & Best Practices

*Purpose: Production-ready evaluation, validation, and monitoring patterns for LLM, RAG, agentic, and prompt-based systems. Includes multi-metric test templates, quality gates, anti-patterns, and incident playbooks.*

---

## Core Patterns

---

### Pattern 1: Multi-Metric Evaluation Loop

**Use when:** Validating any LLM system (RAG, agent, or fine-tuned model) before prod or after major update.

**Structure:**

```
1. Select metrics: accuracy, faithfulness, hallucination, latency, cost, toxicity, bias, output format
2. Build eval set: gold Q/A pairs, adversarial/edge cases, regression suite
3. Run automated evals: check pass/fail, collect scores
4. Human-in-the-loop review: sample outputs for subjective criteria (helpfulness, style, etc.)
5. Compare to baseline/last release: regression check
6. Incident plan: rollback/fix on critical metric drop
```

**Checklist:**

- [ ] Metrics chosen for all key risks (see below)
- [ ] Eval/test suite updated with new edge/adversarial cases
- [ ] Automated eval runs after every model/prompt update
- [ ] Human review included for qualitative criteria
- [ ] Regression and incident plan in place

---

### Pattern 2: Faithfulness & Hallucination Testing

**Use when:** RAG or context-grounded LLM systems (where hallucination risk is high).

**Structure:**

```
1. Prepare test set: Q/A with ground-truth context
2. Automated: Compare answer against context—mark “faithful” if all info is supported
3. Score % of outputs with hallucinated/unsupported claims
4. For prod: Set strict thresholds (e.g., <3% hallucination)
5. Human review for ambiguous or borderline cases
```

**Checklist:**

- [ ] Faithfulness eval test set built (with labeled context/support)
- [ ] Score for hallucination and “Not found” cases
- [ ] Alert/rollback if hallucination exceeds threshold

---

### Pattern 3: Latency, Cost, and Abuse Monitoring

**Use when:** System in production or high-traffic environments.

**Structure:**

```
1. Track per-request latency (p50, p95), model/infra cost, error rates
2. Monitor for spikes (alerts if thresholds breached)
3. Log prompt/model changes vs. performance
4. Add abuse/attack detection (prompt injection, tool abuse)
5. Test rollback/failover at regular intervals
```

**Checklist:**

- [ ] All key metrics (latency, cost, usage, errors) logged
- [ ] Alerting for anomalies and threshold breaches
- [ ] Abuse detection (prompt, API, tool) enabled
- [ ] Rollback/failover playbook tested quarterly

---

### Pattern 4: Prompt & Agent Regression Testing

**Use when:** Prompts or agent workflows change frequently; downstream tools depend on format.

**Structure:**

```
1. Maintain prompt/agent test suite with all required outputs (including format, “not found”, error cases)
2. On any prompt change, run regression suite and diff against last passing outputs
3. Block release on any regression
4. Log and version-control all prompt/agent changes
```

**Checklist:**

- [ ] Regression suite always up-to-date
- [ ] All prompt/agent changes logged/versioned
- [ ] No prod deploys without passing regression

---

## Decision Matrices

### Evaluation Metric Table

| Metric       | Applies To         | Target/Threshold    | Tool Example     | Incident Plan           |
|--------------|-------------------|---------------------|------------------|-------------------------|
| Accuracy     | LLM, RAG          | >95%                | Eval harness     | Patch/retrain           |
| Faithfulness | RAG/grounded      | >97%                | Faithful eval    | Tighten RAG/retrieval   |
| Hallucination| All LLM           | <3%                 | Faithful eval    | Rollback, fallback      |
| Latency      | All prod systems  | <2s p95             | LangSmith, W&B   | Autoscale, optimize     |
| Cost         | All prod systems  | Budgeted            | Cost dashboard   | Quantize, batch, trim   |
| Safety/Abuse | All prod systems  | 0 critical          | Abuse logs       | Escalate/block          |
| Format       | Prompt/agent      | 100% compliance     | Output tests     | Patch, block release    |

---

## Traceability Requirements (2026 Standard)

**Critical:** Every evaluation score must be traceable to the exact configuration that produced it.

### Required Traceability Fields

| Field | Description | Example |
|-------|-------------|---------|
| `prompt_version` | Git SHA or version tag of prompt template | `v1.2.3` or `abc123` |
| `model_version` | Exact model identifier with revision | `provider:model@revision` |
| `dataset_version` | Version/hash of eval dataset | `golden-v2.1` |
| `timestamp` | When eval was run | `2026-01-17T10:30:00Z` |
| `config_hash` | Hash of full configuration | `sha256:abc...` |

### Implementation Pattern

```python
# Eval result with full traceability
eval_result = {
    "score": 0.94,
    "metric": "faithfulness",
    "traceability": {
        "prompt_version": "v1.2.3",
        "model_version": "provider:model@revision",
        "dataset_version": "golden-set-v2.1",
        "timestamp": "2026-01-17T10:30:00Z",
        "config_hash": "sha256:abc123...",
        "git_commit": "def456..."
    }
}
```

### LLM-as-Judge Best Practices (2026)

LLM-as-judge is useful, but it is not ground truth. Calibrate against a small human-labeled set and treat judge scores as signals (not absolutes).

**Minimum bar:**
- Keep a human-labeled calibration subset; track judge↔human agreement over time.
- Version the judge prompt + judge model; never change them silently.
- Avoid judging with the same exact model/config you are evaluating when possible.

| Framework | Best For | Notes |
|-----------|----------|-------|
| **DeepEval (G-Eval and variants)** | General criteria-based eval | Strong templating; validate agreement on your domain |
| **RAGAS** | RAG-specific metrics | Use for context precision/recall/faithfulness; verify labeling assumptions |
| **LangSmith / tracing platforms** | Production monitoring + experiments | Great for regression tracking; not a substitute for offline eval design |

### RAGAS Core Metrics

| Metric | What It Measures | Target |
|--------|------------------|--------|
| **Context Precision** | Relevance of retrieved context to query | >0.85 |
| **Context Recall** | Whether all relevant info was retrieved | >0.80 |
| **Faithfulness** | Answer grounded in provided context | >0.95 |
| **Answer Relevancy** | Response relevance to original question | >0.90 |

### Checklist: Evaluation Traceability

- [ ] Every eval result includes prompt/model/dataset versions
- [ ] Configuration hashes computed and stored
- [ ] Eval results stored in versioned database
- [ ] Can reproduce any historical eval from stored config
- [ ] Diff tool available to compare eval runs

---

## Common Mistakes & Anti-Patterns

---

[FAIL] **Single-metric focus:** Only “accuracy” tracked—misses hallucination, latency, or safety failures.  
[OK] **Instead:** Always include multi-metric eval (see table above).

[FAIL] **No regression test suite:** Manual spot checks miss format or edge case errors after prompt/model changes.  
[OK] **Instead:** Automate regression on every change; block release on failures.

[FAIL] **Ignoring user feedback:** Incidents not caught until user complaints (post-prod).  
[OK] **Instead:** Add user feedback and error reporting in all prod deployments.

[FAIL] **No incident plan:** Metrics breach but no tested rollback/failover path.  
[OK] **Instead:** Predefine incident thresholds, auto-rollback, alert on-call team.

---

## Quick Reference

### Evaluation & Rollout Quality Gates

- [ ] Multi-metric eval pass (accuracy, faithfulness, latency, cost, safety)
- [ ] Prompt/agent regression suite pass
- [ ] Hallucination below threshold
- [ ] Edge cases/adversarial inputs tested
- [ ] Rollback/failover plan tested and documented

---

### Emergency Playbook

- If faithfulness drops or hallucination spikes:
  1. Tighten retrieval, lower “top-k”, increase “Not found” fallback
  2. Rollback model/checkpoint
  3. Patch prompt with stricter grounding/citation

- If latency/cost spike:
  1. Quantize model, shorten context, scale infra
  2. Switch to fallback or less expensive model
  3. Alert, throttle, and investigate

- If format/safety failures:
  1. Block output, auto-rollback prompt/model
  2. Patch and add regression test for missed format/safety case

---

## Further Resources

See `data/sources.json` for:

- OpenAI Evals, Anthropic Evals, HELM, LangSmith, W&B, BIG-bench, LLMOps monitoring, evaluation playbooks

---

**Next:**  
Ready to generate any template file (e.g., `assets/rag-pipelines/template-basic-rag.md`) or `data/sources.json` on request.
