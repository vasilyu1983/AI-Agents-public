# LLMOps Best Practices

*Purpose: Practical guidance for executing and maintaining production-grade LLM systems, from project validation through deployment, monitoring, and continuous improvement.*

---

## Core Patterns

---

### Pattern 1: LLM Project Preflight & Lifecycle

**Use when:** Starting any LLM, RAG, or agentic AI project—especially for production or critical deployments.

**Structure:**

```
1. Define business/user goal (clear success criteria)
2. Identify target data sources (access, licensing, update schedule)
3. Data curation pipeline: deduplication, filtering, PII scan, split
4. Model path: choose (API, OSS, custom fine-tune)
5. Plan for eval: select metrics, test suites, human-in-the-loop
6. Deployment target: resource plan, scaling, rollback/upgrade
7. Observability: logs, alerts, usage/latency dashboards
8. Safety & guardrails: input/output filtering, abuse/escalation
```

**Checklist:**

- [ ] Clear user/business goal defined
- [ ] Data curation pipeline (dedup, filter, PII) in place
- [ ] Pretraining/fine-tune plan with rollback/checkpoints
- [ ] Evaluation plan (metrics, regression, human review)
- [ ] Deployment resource + rollback
- [ ] Observability: logs, dashboards, alerting
- [ ] Safety: guardrails, escalation, abuse handling

---

### Pattern 2: LLMOps Lifecycle—End-to-End Steps

| Step         | What to Do                                        | Validation           |
|--------------|---------------------------------------------------|----------------------|
| **Data**     | Raw → Cleaned → Chunked (for RAG)                 | Dedup/PII scan       |
| **Training** | Pretrain or fine-tune, log all settings            | Repro logs, backup   |
| **Eval**     | Multi-metric (accuracy, faithfulness, latency)     | Test suite, spot QA  |
| **Prompting**| Version templates, test with edge cases            | Prompt eval suite    |
| **RAG/Agent**| Validate chunking, retrieval, tool flow            | Retrieval recall     |
| **Deploy**   | Stage → Prod with monitoring                       | Canary, rollback     |
| **LLMOps**   | Monitor, alert, update, auto-abort on failure      | Live metrics, failover|

---

### Pattern 3: Production Readiness—Quality Gates

**Before launch, pass all:**

- [ ] **Data**: Source checked, up-to-date, deduped, filtered
- [ ] **Model**: Eval pass on regression, hallucination <3%
- [ ] **Prompts**: All core prompts versioned & regression-tested
- [ ] **RAG**: Retrieval recall >85%, context window fits key data
- [ ] **Agents**: Tool use/plan reproducible, no infinite loops
- [ ] **Safety**: Abuse cases filtered, critical output escalation

---

## Decision Matrices

### Model Path Selection Table

| Scenario                | Use           | Decision         | Validation          |
|-------------------------|---------------|------------------|---------------------|
| Low risk, fast launch   | Closed API    | Use as-is        | API limits, eval    |
| Custom data, moderate   | Finetune OSS  | LoRA/PEFT tune   | LoRA, QLoRA metrics |
| Confidential data       | Private train | Local/secure infra| Data audit, secure  |

---

### Deployment Pattern Matrix

| Scale     | Pattern                  | Checklist                        |
|-----------|--------------------------|-----------------------------------|
| Single    | Direct deploy            | API/DB creds secured              |
| Batch     | Job scheduler            | Retry/failover scripts            |
| Realtime  | Canary/staged rollout    | Auto-metrics, quick rollback      |
| Multi-site| Blue/green, geo-routing  | Consistent model, version control |

---

## Common Mistakes & Anti-Patterns

---

[FAIL] **Data Drift Ignored**: No schedule for re-curating data, leading to outdated/irrelevant model behavior.  
[OK] **Instead**: Automate data refresh, log drift, set up re-ingestion triggers.

[FAIL] **No Prompt Versioning**: Ad-hoc edits break workflows, regressions sneak in.  
[OK] **Instead**: Store all prompt templates in version control, run regression suites after edit.

[FAIL] **No Rollback Plan**: Deployments go live without a way to revert on failure.  
[OK] **Instead**: Canary deployments, automatic rollback, fast “last known good” fallback.

[FAIL] **Observability Gaps**: No logging/alerts for latency, OOM, or safety.  
[OK] **Instead**: Add logs, health pings, resource use monitors, safety/abuse event logs.

[FAIL] **Ignoring Edge Cases in Eval**: Models tested only on “happy path.”  
[OK] **Instead**: Test all common and edge cases—short, long, adversarial, weird user input.

---

## Quick Reference

### LLMOps Production Checklist

- [ ] Data freshness + deduplication validated
- [ ] Model eval: hallucination, faithfulness, latency pass
- [ ] Prompt templates: versioned, tested, edge cases
- [ ] RAG: top-k retrieval recall and source tracking
- [ ] Agent workflows: tool flow, fallback, step limit
- [ ] Monitoring: latency, cost, abuse, drift
- [ ] Rollback path and escalation ready

---

### Emergency Playbook

- If hallucinations spike:  
  1. Route queries to RAG/grounded mode  
  2. Tighten retrieval, compress context  
  3. Trigger rollback to previous checkpoint/model

- If cost/latency spikes:  
  1. Switch to quantized model, reduce context window  
  2. Batch/stream processing, enable autoscaling  
  3. Alert/auto-disable non-critical features

- If user abuse detected:  
  1. Auto-block, log event, alert on-call  
  2. Escalate critical cases, triage, patch prompts/filters

---

## Further Resources

See `data/sources.json` for:

- OpenAI, Anthropic, Gemini, HuggingFace, vLLM, LlamaIndex, LangChain, PEFT, DeepSpeed, LangSmith, W&B, and more.

---

**Next**:  
See [references/rag-best-practices.md](rag-best-practices.md) for copy-paste RAG/Retrieval patterns and validation guides.
