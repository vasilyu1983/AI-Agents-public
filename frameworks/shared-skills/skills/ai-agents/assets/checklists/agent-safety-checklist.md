# Agent Design & Safety Checklist

**Purpose**: Ensure production-ready agent development with multi-layer safety controls and observability baseline.

---

## Template Contract

### Goals
- Ensure the agent is bounded, auditable, and rollbackable.
- Prevent unsafe tool actions, data leakage, and uncontrolled spend.
- Make quality and safety measurable before production rollout.

### Inputs
- Agent spec (purpose, users, permissions).
- Tool inventory (APIs, data stores, side effects).
- Data classification (PII, confidential, public).
- SLOs/budgets (latency, cost per request, failure rate).

### Decisions
- Autonomy level and step/time/cost caps.
- Tool allowlist + authorization model per tool.
- HITL triggers and escalation paths.
- Evaluation gates and rollout strategy (canary, shadow, rollback).

### Risks
- Prompt injection and tool abuse via untrusted inputs.
- Data exfiltration via tools, logs, or citations.
- Runaway loops (cost/latency explosions) and cascading retries.
- Non-reproducible behavior due to hidden state or missing traces.

### Metrics
- Task success rate, tool success rate, refusal correctness.
- Guardrail violation rate, PII leakage rate.
- Latency (TTFT/total) p50/p95/p99 and cost per request.

## Pre-Development

### Scope Definition
- [ ] Agent purpose documented (single responsibility)
- [ ] Tool allowlist defined (no "all tools" access)
- [ ] Maximum autonomy level specified (L1-L5)
- [ ] HITL triggers identified (financial, destructive, legal actions)

### Risk Assessment
- [ ] Blast radius documented (what can go wrong)
- [ ] Data access classified (PII, confidential, public)
- [ ] Destructive actions identified (delete, modify, send)
- [ ] Regulatory constraints checked (GDPR, HIPAA, SOX, EU AI Act)

---

## Implementation

### Guardrails (Multi-Layer Defense Required)

**Layer 1: Input Validation**
- [ ] PII redaction configured
- [ ] Content filtering enabled
- [ ] Prompt injection detection active

**Layer 2: Authorization**
- [ ] RBAC/ABAC configured per tool
- [ ] Fine-grained permissions defined
- [ ] Principle of least privilege applied

**Layer 3: Tool Gating**
- [ ] Tool signatures verified (artifact signing)
- [ ] Human approval required for high-risk operations
- [ ] Rate limits per tool configured

**Layer 4: Output Filtering**
- [ ] PII detection in responses
- [ ] Policy compliance validation
- [ ] Content moderation active

**Layer 5: Observability**
- [ ] OpenTelemetry spans configured
- [ ] SIEM integration active
- [ ] Real-time alerts defined

### OpenTelemetry Spans (Required)

```yaml
spans:
  - llm_call: {prompt, response, tokens, latency, model}
  - tool_call: {name, params, result, duration, success}
  - retrieval: {query, chunks, scores, method}
  - memory_op: {operation, type, key, size}
  - agent_handoff: {source, target, schema_version, trace_id}
```

### Failure Handling
- [ ] Retry policy defined (max retries, exponential backoff)
- [ ] Fallback behavior specified
- [ ] Timeout limits set (per-step and total)
- [ ] Error classification (retriable vs fatal)
- [ ] Graceful degradation path documented

---

## Pre-Production

### Evaluation Suite
- [ ] Golden dataset created (minimum 50 test cases)
- [ ] Final answer evaluation (correctness, grounding, clarity)
- [ ] Trajectory evaluation (step quality, tool use)
- [ ] Safety evaluation (policy violations, harmful content)
- [ ] Adversarial testing completed

### Security Testing
- [ ] OWASP GenAI Top 10 checked
- [ ] Prompt injection testing passed
- [ ] Tool abuse scenarios tested
- [ ] PII leakage testing passed

### Deployment Readiness
- [ ] Canary deployment configured
- [ ] Rollback procedure documented and tested
- [ ] Incident runbook created
- [ ] On-call rotation assigned

---

## Production Metrics

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Tool success rate | >=95% | <90% |
| Latency P95 | <5s | >10s |
| Hallucination rate | <5% | >10% |
| HITL approval rate | Monitor | Sudden change |
| Cost per request | <$0.10 | >$0.50 |
| Error rate | <1% | >5% |
| Guardrail violations | 0 | >0 |

---

## Post-Launch Monitoring

### Daily Checks
- [ ] Error rate within threshold
- [ ] Cost within budget
- [ ] No guardrail violations
- [ ] Latency stable

### Weekly Reviews
- [ ] Evaluation score trends
- [ ] User feedback analysis
- [ ] Cost optimization opportunities
- [ ] Security incident review

### Monthly Reviews
- [ ] Model performance degradation check
- [ ] Tool usage patterns analysis
- [ ] Capacity planning update
- [ ] Compliance audit

---

## Anti-Patterns to Avoid

| Anti-Pattern | Risk | Detection |
|--------------|------|-----------|
| Runaway autonomy | Resource exhaustion, unintended actions | Monitor step count, cost per request |
| Hidden state | Non-reproducible behavior | Checkpoint logging, state serialization |
| Unbounded tools | Security vulnerabilities | Tool allowlist enforcement |
| Missing handoff validation | Context corruption | Schema validation errors |
| Single guardrail layer | Bypass via injection | Red team testing |
| Trusting tool outputs | Injection attacks | Output sanitization checks |

---

## Sign-Off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| ML Engineer | | | |
| Security | | | |
| Product Owner | | | |
| Platform | | | |
