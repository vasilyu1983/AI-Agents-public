# Production Checklists

Comprehensive pre-deployment checklists and operational validation patterns for production LLM systems (Modern Production Standards).

---

## LLM Lifecycle Checklist

Before starting a production LLM/RAG project, validate all items below.

### Data & Training

- [ ] Data source reliability and access confirmed
- [ ] Data curation pipeline ready with deduplication, filtering, PII detection
- [ ] **PEFT/LoRA fine-tuning** strategy selected (**Modern standard for efficiency**)
- [ ] Pretrain/fine-tune hardware budgeted (with backup plan)
- [ ] Regular validation checks for overfitting/underfitting
- [ ] Training data versioned and stored
- [ ] Data quality metrics tracked (completeness, accuracy, freshness)
- [ ] License compliance verified for training data
- [ ] Bias and fairness assessment completed

### Prompt Engineering (Modern CI/CD)

- [ ] Prompt templates versioned and stored (with test suite)
- [ ] **CI/CD integration:** automated tests, version control, rapid deployment
- [ ] Iteration strategy defined (start simple → refine)
- [ ] Reasoning steps incorporated where appropriate
- [ ] Few-shot examples validated for quality
- [ ] Prompt injection defenses tested
- [ ] Fallback prompts defined for edge cases
- [ ] A/B testing framework in place

### RAG Pipeline (Recent Advances)

- [ ] Chunking strategy evaluated with a retrieval test set (baseline + alternatives)
- [ ] Index built, embedding model validated
- [ ] **Hybrid retrieval** enabled (BM25 + vector + reranking)
- [ ] Reranking configured (if precision is critical) and validated on test set
- [ ] Retrieval metrics baseline established (recall@k, nDCG/MRR, empty-result rate)
- [ ] Groundedness and hallucination metrics tracked
- [ ] Chunk size/overlap tuned per corpus (documented rationale)
- [ ] Metadata filtering strategy defined
- [ ] Citation/source tracking implemented
- [ ] Index refresh strategy documented

### Deployment & Serving (Modern Performance)

- [ ] High-throughput serving engine evaluated (batching/scheduling, streaming, isolation)
- [ ] Quantization/compression strategy selected and validated on eval set
- [ ] Attention/prefill optimizations evaluated where supported
- [ ] Cost-per-token targets documented
- [ ] Auto-scaling configured based on traffic
- [ ] Load balancing strategy defined
- [ ] Caching strategy implemented (prompt/response caching)
- [ ] Rate limiting configured per user/API key
- [ ] Timeout and retry policies set

### Operations (Modern Automation)

- [ ] Drift monitoring enabled with clear triggers and runbooks
- [ ] **Automated retraining triggers** configured (drift, schema, volume, manual)
- [ ] Model registry with promotion workflow
- [ ] SLOs defined (latency p95/p99, error rate, cost) and tracked
- [ ] Incident response playbook documented
- [ ] Rollback procedure tested
- [ ] On-call rotation established
- [ ] Disaster recovery plan validated

### Agentic System

- [ ] Tool use, error handling, and fallback paths mapped
- [ ] Multi-agent orchestration patterns defined (if applicable)
- [ ] Tool success rate baseline established (target: >95%)
- [ ] Human-in-the-loop gates configured for high-risk actions
- [ ] Agent step limits and timeout configured
- [ ] Tool permission model defined (RBAC/ABAC)

### Evaluation (Automated Testing)

- [ ] Multi-metric evaluation (hallucination, bias, latency, cost)
- [ ] **Automated regression test suite** with CI/CD integration
- [ ] Recall@K, Precision@K, nDCG tracked for RAG
- [ ] Groundedness, verbosity, instruction following measured
- [ ] Golden test set created and maintained
- [ ] LLM-as-judge evaluation configured
- [ ] Human evaluation baseline established
- [ ] A/B testing framework operational

### Safety/Guardrails (Modern Multi-Layered Defense)

- [ ] Multi-layer defense-in-depth strategy defined (prompt + tool gating + runtime checks)
- [ ] Guardrails selected and validated against realistic abuse cases
- [ ] Input/output filtering with anomaly detection
- [ ] Continuous monitoring enabled
- [ ] Abuse monitoring and escalation path defined
- [ ] Multimodal injection risks addressed
- [ ] PII detection and redaction enabled
- [ ] Content moderation policies enforced
- [ ] Rate limiting and abuse detection active

---

## Performance Budget & Goodput Gates

### Budgets Up Front

Define and document performance targets before implementation:

**Token Cost:**
- [ ] Token cost ceiling per request defined
- [ ] Monthly budget allocated
- [ ] Cost tracking dashboard configured
- [ ] Alerts set for budget overruns

**Latency:**
- [ ] p95 latency target documented
- [ ] p99 latency maximum tolerance set
- [ ] Latency monitoring enabled
- [ ] SLO/SLA defined for response times

**Throughput:**
- [ ] Tokens per second target set
- [ ] Requests per second capacity planned
- [ ] Concurrent user limits defined
- [ ] Load testing completed

**Quality Gates:**
- [ ] Hallucination rate threshold (<3% recommended)
- [ ] Accuracy/F1 target defined (>90% typical)
- [ ] Groundedness threshold for RAG (>95%)
- [ ] User satisfaction metric tracked

### Profiling Harness

**Load Testing:**
- [ ] Load generator configured with mixed prompt lengths
- [ ] Goodput (useful tokens/s) measured
- [ ] GPU utilization tracked (target: 70-90%)
- [ ] Memory headroom monitored
- [ ] Tail latencies captured (p95, p99)

**Metrics Collection:**
- [ ] Request/response logging enabled
- [ ] Distributed tracing configured
- [ ] Cost per request tracked
- [ ] Error rate monitoring active

### Rollout Gates

**Pre-Deployment Checks:**
- [ ] Performance budgets not breached
- [ ] Quality metrics meet thresholds
- [ ] Security scan passed
- [ ] Load testing successful
- [ ] Canary deployment plan ready

**Dashboard Attachment:**
- [ ] Metrics attached to deployment PRs
- [ ] Automated checks configured
- [ ] Manual override process documented
- [ ] Rollback criteria defined

### Regression Loop

**Continuous Testing:**
- [ ] Performance tests run on prompt changes
- [ ] Performance tests run on model updates
- [ ] Performance tests run on index changes
- [ ] Daily regression suite scheduled
- [ ] Regression detection threshold configured (10% recommended)

---

## Reliability & Data Infrastructure (DDIA-Grade)

### Replication & Sharding

**Planning:**
- [ ] Replication strategy selected (leader/follower vs multi-leader)
- [ ] Shard plan documented for vector store
- [ ] Traffic-aligned sharding configured
- [ ] Rebalancing procedure defined
- [ ] Hot-shard mitigation in place

**Checklist:**
- [ ] Replication factor configured (3+ for production)
- [ ] Shard distribution balanced
- [ ] Cross-region replication enabled (if needed)
- [ ] Failover tested and documented
- [ ] Backup and restore procedures validated

### Backpressure & Load Shedding

**Graceful Degradation:**
- [ ] Queue configured with size limits
- [ ] Rate limiting at ingress
- [ ] Load shedding strategy defined
- [ ] Cached answers for degraded mode
- [ ] Circuit breakers configured

**Checklist:**
- [ ] Backpressure mechanisms tested
- [ ] Queue depth monitoring enabled
- [ ] Graceful degradation triggers defined
- [ ] User-facing error messages prepared
- [ ] Recovery procedures documented

### Consistency & Rollback

**Versioning:**
- [ ] Prompts versioned with git
- [ ] Models versioned in registry
- [ ] Indexes versioned and tagged
- [ ] Rollback artifacts retained (last 3 versions minimum)
- [ ] Atomic swap capability for upgrades

**Checklist:**
- [ ] Rollback procedure tested
- [ ] Version compatibility matrix documented
- [ ] Config changes require approval
- [ ] Deployment history tracked
- [ ] Audit trail maintained

### Freshness & Ingestion

**Data Pipelines:**
- [ ] Batch ingestion pipeline operational
- [ ] Streaming ingestion configured (if needed)
- [ ] Idempotent upserts implemented
- [ ] GDPR hard-delete capability
- [ ] Restore/reindex procedure rehearsed

**Checklist:**
- [ ] Dual-path ingestion (batch + stream) with idempotency
- [ ] Data freshness SLAs defined
- [ ] Reindex strategy documented
- [ ] Data retention policies configured
- [ ] PII deletion workflow validated

---

## User Feedback & Online Evaluation

### Feedback Signals

**Collection:**
- [ ] Thumbs up/down captured with request IDs
- [ ] Edit tracking enabled
- [ ] Abandonment rate monitored
- [ ] PII scrubbing applied to feedback
- [ ] Feedback storage with retention policy

**Checklist:**
- [ ] Feedback logging with privacy filters enabled
- [ ] User consent obtained for data collection
- [ ] Feedback aggregation dashboard
- [ ] Feedback loop to training pipeline
- [ ] Regular review of user feedback

### Shadowing & Canary Deployments

**Traffic Routing:**
- [ ] Shadow mode configured (0% user-facing)
- [ ] Canary percentage defined (5-10% recommended)
- [ ] Solve rate comparison enabled
- [ ] Cost/latency tracking per variant
- [ ] Auto-abort on regressions

**Checklist:**
- [ ] Shadow/canary with guardrails and abort gates
- [ ] Metrics comparison dashboard
- [ ] Statistical significance testing
- [ ] Rollback trigger conditions defined
- [ ] Gradual rollout plan (10% → 50% → 100%)

### Label Loops

**Training Data Generation:**
- [ ] Critiques converted to supervised pairs
- [ ] Pairwise preferences for DPO/ORPO
- [ ] Eval set protection from contamination
- [ ] Label quality validation
- [ ] Active learning pipeline configured

**Checklist:**
- [ ] Label pipelines for SFT + DPO with eval protection
- [ ] Human labeling guidelines documented
- [ ] Inter-annotator agreement tracked
- [ ] Label versioning enabled
- [ ] Bias monitoring in labeled data

### Dashboards & Alerts

**Monitoring:**
- [ ] Solve rate dashboard
- [ ] Groundedness tracking
- [ ] Hallucination rate monitoring
- [ ] Format error detection
- [ ] Per-dataset slice views
- [ ] Live alerts configured

**Checklist:**
- [ ] Online dashboards/alerts tied to business KPIs
- [ ] Alert escalation path defined
- [ ] On-call runbooks prepared
- [ ] Regular dashboard reviews scheduled
- [ ] Metric definitions documented

---

## Agentic Trust & Safety (Biswas/Iusztin Patterns)

### Controls

**Agent Limits:**
- [ ] Step caps configured per agent type
- [ ] Plan iteration limits set
- [ ] Tool allowlist defined per agent
- [ ] High-risk tool approvals required
- [ ] Audit trails for every call

**Checklist:**
- [ ] Step/tool caps and approvals for sensitive actions
- [ ] Agent identity and permissions configured
- [ ] Tool usage logging enabled
- [ ] Approval workflow tested
- [ ] Timeout and failure handling defined

### Coordination

**Multi-Agent Orchestration:**
- [ ] Coordinator/worker/delegator pattern implemented
- [ ] Explicit hand-off rules defined
- [ ] Conflict arbitration mechanism
- [ ] Task routing logic documented
- [ ] Agent communication protocol versioned

**Checklist:**
- [ ] Hand-off/coordination rules tested
- [ ] Agent discovery mechanism
- [ ] Load balancing across agents
- [ ] Failure recovery for agent crashes
- [ ] Inter-agent authentication

### Abuse & Safety

**Input/Output Filtering:**
- [ ] Jailbreak detection on inputs
- [ ] Prompt injection filters on context
- [ ] Output scanning for policy violations
- [ ] Escalation to human for unsafe outcomes
- [ ] Abuse pattern detection

**Checklist:**
- [ ] Input/output safety filters and escalation path
- [ ] Full audit log for agent plans/actions
- [ ] Abuse monitoring dashboard
- [ ] Incident response playbook
- [ ] Regular security audits

---

## Weekly Production Tasks

Ongoing operational responsibilities for production LLM systems:

### Evaluation & Quality

- [ ] Run evaluation suite with new production data
- [ ] Review quality metrics trends (hallucination, accuracy, groundedness)
- [ ] Check for model/tool drift
- [ ] Analyze failed requests and error patterns
- [ ] Update golden test set with new edge cases

### Safety & Security

- [ ] Review SIEM alerts and incident taxonomy
- [ ] Check abuse monitoring dashboard
- [ ] Audit HITL approval queue metrics
- [ ] Review PII detection logs
- [ ] Update content moderation rules if needed

### Performance & Cost

- [ ] Review cost/latency budgets
- [ ] Check GPU utilization and resource usage
- [ ] Analyze tail latencies (p95, p99)
- [ ] Review cache hit rates
- [ ] Optimize underperforming queries

### Operations & Reliability

- [ ] Check model registry for pending updates
- [ ] Review deployment pipeline health
- [ ] Validate backup and restore procedures
- [ ] Test rollback capability
- [ ] Update runbooks based on incidents

### User Feedback & Improvement

- [ ] Analyze user feedback trends
- [ ] Review solve rate and user satisfaction
- [ ] Identify common failure modes
- [ ] Plan prompt/model improvements
- [ ] Update training data with new examples

---

## Related Resources

- **[Project Planning Patterns](project-planning-patterns.md)** - Stack selection and pipeline architecture
- **[LLMOps Best Practices](llmops-best-practices.md)** - Operational lifecycle and deployment
- **[Evaluation Patterns](eval-patterns.md)** - Testing, metrics, and quality validation
- **[Anti-Patterns](anti-patterns.md)** - Common mistakes and prevention strategies

---

## Shared Utilities (Implementation Patterns)

For cross-cutting implementation concerns in LLM systems, reference these centralized utilities:

- [llm-utilities.md](../../software-clean-code-standard/utilities/llm-utilities.md) — Token counting (tiktoken), streaming, cost estimation, rate limit handling
- [error-handling.md](../../software-clean-code-standard/utilities/error-handling.md) — Effect Result types, correlation IDs for LLM error handling
- [resilience-utilities.md](../../software-clean-code-standard/utilities/resilience-utilities.md) — p-retry v6, circuit breaker for LLM API calls
- [logging-utilities.md](../../software-clean-code-standard/utilities/logging-utilities.md) — pino v9 + OpenTelemetry for LLM logging
- [observability-utilities.md](../../software-clean-code-standard/utilities/observability-utilities.md) — OpenTelemetry SDK, tracing for LLM latency/cost tracking
- [config-validation.md](../../software-clean-code-standard/utilities/config-validation.md) — Zod 3.24+ for API key validation, secrets management
- [testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) — Vitest, MSW v2 for mocking LLM APIs

---
