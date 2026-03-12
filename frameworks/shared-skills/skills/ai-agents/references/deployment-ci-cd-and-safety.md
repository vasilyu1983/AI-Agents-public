# Deployment, CI/CD & Safety — Best Practices 

*Purpose: Provide operational procedures for deploying, evaluating, gating, monitoring, and securing AI agents in production environments with multi-layer guardrails.*

**Modern Update**: NIST AI RMF compliance, OWASP GenAI Top 10 defenses, OpenTelemetry observability, and human-in-the-loop for high-risk operations are now production standards.

---

## Multi-Layer Guardrails (Critical)

### Defense-in-Depth Architecture

**Five mandatory layers for production agents**:

```yaml
Layer 1: Input Validation
  - PII redaction (real-time)
  - Content filtering (harmful content, jailbreaks)
  - Prompt injection detection
  - Input sanitization

Layer 2: RBAC/ABAC Authorization
  - Fine-grained permissions per tool/action
  - Externalized policy (OPA/Rego or managed engines)
  - Zero standing privileges
  - Short-lived secrets with rotation

Layer 3: Tool Gating
  - Signature verification (Sigstore/Cosign)
  - Human approval for high-risk operations
  - Tool invocation logging
  - Scope validation (tool matches authorized role)

Layer 4: Output Filtering
  - PII detection (before delivery)
  - Content moderation (policy violations)
  - Compliance validation
  - Format verification

Layer 5: Observability & Monitoring
  - OpenTelemetry GenAI spans
  - SIEM integration with alerting
  - Real-time anomaly detection
  - Audit trail for all operations
```

### Human-in-the-Loop (HITL) Requirements

**Mandatory HITL approval for**:
- Financial transactions (payments, transfers, account modifications)
- Database write operations (UPDATE, DELETE, DROP)
- Legal or compliance actions (contract signing, regulatory filings)
- Irreversible operations (account deletion, data purging)
- Production system modifications (deployments, configuration changes)

**Implementation pattern**:
```yaml
agent_prepares_action()
if requires_human_approval(action):
  request = create_approval_request(action)
  approval = wait_for_human_approval(request)
  if approval.granted:
    execute_with_audit(action, approval.id)
  else:
    log_rejection(action, approval.reason)
else:
  execute_with_validation(action)
```

**HITL metrics to track**:
- Approval queue length
- Average approval time
- Approval/rejection ratio
- False positive rate (unnecessary approvals)

### OWASP GenAI Top 10  Defenses

**1. Prompt Injection**:
- Treat all user input as untrusted
- Use delimiter tags to separate instructions from data
- Validate prompt structure before execution
- Never concatenate user input directly into system prompts

**2. Insecure Output Handling**:
- Validate all LLM outputs against schema
- Never execute LLM-generated code without sandboxing
- Filter outputs before rendering (XSS prevention)

**3. Training Data Poisoning**:
- Validate RAG data sources
- Use curated, verified knowledge bases
- Monitor for drift in retrieval quality

**4. Model Denial of Service**:
- Token limits per request
- Rate limiting per user/API key
- Circuit breakers for cascading failures
- Cost budgets with automatic kill switches

**5. Supply Chain Vulnerabilities**:
- Pin all dependency versions
- Verify tool signatures (Sigstore/Cosign)
- Use SBOMs and SLSA attestations
- Audit third-party plugins before integration

**6. Sensitive Information Disclosure**:
- PII redaction at ingestion and output
- Memory TTLs to limit data retention
- DLP (Data Loss Prevention) on all channels
- Secrets in Vault/KMS, never in prompts

**7. Insecure Plugin Design**:
- Least privilege for tool permissions
- Require explicit confirmation for high-risk tools
- Validate tool outputs before use
- Never trust tool results without verification

**8. Excessive Agency**:
- Limit tool capabilities per agent role
- Require HITL for destructive operations
- Implement fail-safe defaults (deny by default)
- Audit logs for all agent actions

**9. Overreliance**:
- Always require citations for factual claims
- Confidence scoring for agent outputs
- Human review for critical decisions
- Fallback to human expert when confidence low

**10. Model Theft**:
- API key rotation
- Usage monitoring for anomalies
- Rate limiting per endpoint
- Authentication for all model access

---

## 1. Deployment Pipeline (Enhanced)

### Pattern: Standard Deployment Flow

```
dev → CI tests → evaluation suite → staging → canary → production
```

**Checklist**

- [ ] Commit triggers automated CI.  
- [ ] Evaluation suite blocks unsafe/inaccurate revisions.  
- [ ] Version pinned before staging.  
- [ ] Canary monitors key metrics for regression.  
- [ ] Rollback plan defined.  

**Anti-Patterns**

- AVOID: Deploying without evaluation.  
- AVOID: Manual steps without reproducibility.  

---

# 2. CI/CD Configuration

### Pattern: Automated CI Stage

```
lint → unit tests → integration tests → tool-call tests → eval tests
```

**Checklist**

- [ ] All tools validated with type + schema tests.  
- [ ] RAG pipeline tested end-to-end.  
- [ ] Multi-agent routes tested for correctness.  
- [ ] Memory write/read rules validated.  
- [ ] No unversioned dependencies.  

### Failure Rules

- Test fail → block merge  
- Eval fail → block deploy  
- Safety fail → immediate halt  

---

# 3. Evaluation Gate

### Pattern: Quality & Safety Thresholds

```
correctness >= 4.0
grounding >= 4.0
tool_success_rate >= 95%
safety = "pass"
latency_p95 <= target
```

**Checklist**

- [ ] Thresholds defined per environment (staging vs prod).  
- [ ] Results attached to build artifacts.  
- [ ] Historical scores maintained for regression detection.  

### Decision Tree

```
Did evaluation meet thresholds?
→ Yes → Promote to staging
→ No → Reject build
```

---

# 4. Staging Environment Procedures

### Pattern: Staging Validation

```
deploy → run synthetic tests → run real-task replay → compare to baseline
```

**Checklist**

- [ ] Synthetic queries cover all agent modes.  
- [ ] Replay tests cover real workflows.  
- [ ] Validate logs + traces function correctly.  
- [ ] Validate latency + throughput under load.  

**Anti-Patterns**

- AVOID: Using production data directly.  
- AVOID: Skipping tool verification in staging.  

---

# 5. Canary Deployment

### Pattern: Limited & Monitored Rollout

```
deploy_to_subset(1–5%)
monitor(metrics)
if stable → expand
else → rollback
```

**Checklist**

- [ ] Monitor correctness, safety, latency, cost.  
- [ ] Compare against previous version.  
- [ ] Define rollback triggers.  

### Canary Rollback Triggers

- Error spike  
- Safety violation  
- Tool-call failure increase  
- Latency p99 jump  
- Observability failures  

---

# 6. Versioning & Model Pinning

### Pattern: Deterministic Version Control

```
agent_version = x.y.z
embedding_model_version = pinned
retriever_version = pinned
tool_schema_version = pinned
```

**Checklist**

- [ ] Pin all model versions.  
- [ ] Store all prompts with version tag.  
- [ ] Keep compatibility log for all components.  

---

# 7. Production Monitoring

### Pattern: Continuous Observability

```
collect:
  - logs
  - traces
  - metrics
monitor_for:
  - tool errors
  - grounding failures
  - safety violations
```

**Operational Metrics**

- Tool success rate  
- RAG retrieval relevance  
- Latency p50/p95/p99  
- Cost per request  
- Safety pass rate  

**Alert Conditions**

- Error > threshold  
- Tool-call retry spike  
- Stale or missing logs  
- Trace span failures  

---

# 8. Safety Enforcement Layer

### Pattern: Safety Gate Before Action

```
check_action_risk()
check_domain_support()
scan_for_policy_violations()
require_confirmation_if_needed()
perform_action()
```

**High-Risk Categories**

- OS-level automation  
- File modification/deletion  
- Financial or transactional actions  
- System configuration changes  

**Checklist**

- [ ] Require user confirmation for high-risk tasks.  
- [ ] Block hallucinated actions/tools.  
- [ ] Reject incomplete or ambiguous user requests.  
- [ ] Validate parameters explicitly.  

---

# 9. Prompt Hardening

### Pattern: Preprocessing Filter

```
sanitize_input()
block_injections()
reject_adversarial_phrases()
normalize_request()
```

**Checklist**

- [ ] Reject attempts to bypass instructions.  
- [ ] Block system override language.  
- [ ] Block payloads intended to break tools.  
- [ ] Remove suspicious executable content.  

**Anti-Patterns**

- AVOID: Accepting raw user text into agent plan.  

---

# 10. Tool Safety Hardening

### Pattern: Safe Tool Wrapper

```
validate_input()
check_scope()
enforce_rate_limit()
execute()
verify()
```

**Checklist**

- [ ] Parameter type + range checks.  
- [ ] Confirmation for destructive actions.  
- [ ] Reject calls outside declared scope.  
- [ ] Log every invocation.  

---

# 11. Memory Safety Hardening

### Pattern: Controlled Memory Interface

```
memory_agent.validate_write(entry)
memory_agent.validate_read(query)
```

**Rules**

- Never store sensitive PII.  
- Never store internal reasoning.  
- Require explicit confirmation from user.  
- Check consistency before writing.  

---

# 12. Failure Handling

### Pattern: Fail-Fast With Recovery

```
detect_failure()
type_error()
if transient → retry
if soft_error → request clarification
if fatal → surface + halt
```

**Checklist**

- [ ] Documented retry policy.  
- [ ] Recorded failure metadata.  
- [ ] Alert on repeated transient failures.  

---

# 13. Deployment Anti-Patterns (Master List)

- AVOID: Deploying without evaluation suite.  
- AVOID: No version pinning.  
- AVOID: Ignoring safety failures.  
- AVOID: Overwriting production without canary.  
- AVOID: Missing rollback mechanism.  
- AVOID: No logging/observability.  
- AVOID: Using dev/staging tools in production.  
- AVOID: Allowing tool schema drift.  

---

# 14. Quick Reference Tables

### CI/CD Stage Table

| Stage | Required Actions |
|--------|------------------|
| CI | tests, linting, static analysis |
| Evaluation | scoring, safety checks |
| Staging | replay tests, observability check |
| Canary | partial rollout |
| Production | monitoring, alerts |

### Safety Layer Table

| Layer | Enforcement |
|--------|-------------|
| Prompt | sanitization, anti-injection |
| Tool | validation, confirmation |
| Memory | safe-write rules |
| Agent | unsafe-action blocking |

### Rollback Conditions Table

| Condition | Action |
|-----------|--------|
| Safety violation | immediate rollback |
| Latency spike | rollback |
| Tool-call failure | rollback |
| Evaluation score drop | rollback |

---

# End of File
