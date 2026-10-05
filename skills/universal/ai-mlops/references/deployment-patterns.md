# Deployment Patterns for ML & LLM Systems

These deployment patterns define reliable, repeatable ways to ship ML/RAG/LLM models into
production environments.

Use this when the main question is which deployment mode or rollout pattern to choose.

## Table of Contents

- [Quick Navigation](#quick-navigation)
- [1. Pre-Deployment Readiness Checklist](#1-pre-deployment-readiness-checklist)
- [2. Deployment Architecture Patterns](#2-deployment-architecture-patterns)
- [Pattern 1: Batch Deployment](#pattern-1-batch-deployment)
- [Pattern 2: Online API Deployment](#pattern-2-online-api-deployment)
- [Pattern 3: Hybrid Deployment](#pattern-3-hybrid-deployment)
- [Pattern 4: Streaming Inference](#pattern-4-streaming-inference)
- [3. Rollout Strategies](#3-rollout-strategies)
- [Strategy 1: Shadow Deployment](#strategy-1-shadow-deployment)
- [Strategy 2: Canary Release](#strategy-2-canary-release)
- [Strategy 3: Blue-Green Deployment](#strategy-3-blue-green-deployment)
- [Choosing a Rollout Strategy](#choosing-a-rollout-strategy)
- [4. Production Readiness Checklist (Final)](#4-production-readiness-checklist-final)

## Quick Navigation

- [Pre-Deployment Readiness Checklist](#1-pre-deployment-readiness-checklist)
- [Deployment Architecture Patterns](#2-deployment-architecture-patterns)
- [Rollout Strategies](#3-rollout-strategies)
- [Production Readiness Checklist (Final)](#4-production-readiness-checklist-final)

---

## 1. Pre-Deployment Readiness Checklist

Complete **before** deploying any model:

- [ ] Model registry entry created (version, owners, metadata)
- [ ] Evaluation report attached
- [ ] Model card completed
- [ ] Training artifacts frozen
- [ ] Environment specification pinned (requirements.txt, Dockerfile, conda env)
- [ ] Rollback target identified (previous version or baseline)
- [ ] Infra prerequisites validated (GPU/CPU/memory)

---

## 2. Deployment Architecture Patterns

Whatever the mode, split the system into three pipelines — **feature** (raw data → versioned
features), **training** (features → registered model with eval report), and **inference**
(registered model + versioned prompts/config → served output) — that meet only at the feature
store and the model registry. Each pipeline is versioned, tested, and deployed on its own
schedule, so a change in one does not force a redeploy of the others.

### Pattern 1: Batch Deployment
Use when latency is not a constraint.

**Workflow**:
- Scheduled batch job (Airflow, Dagster, Prefect)
- Feature build → Score → Store predictions
- Store results in database/file store
- Downstream consumers read from prediction table

**Pros**:
- Cheap
- Scales with compute clusters
- Easy backfills

**Cons**:
- Not real-time
- Stale predictions possible

---

### Pattern 2: Online API Deployment
Use for latency-sensitive use cases.

**Workflow**:
- Real-time request → transform → model inference → return JSON
- Use FastAPI/gRPC as serving layer
- Horizontal scaling behind load balancer

**Pros**:
- Real-time insights
- Good user experience

**Cons**:
- Requires careful infra & monitoring

---

### Pattern 3: Hybrid Deployment  
Use when some features require batch processing and others depend on fresh signals.

**Workflow**:
- Batch compute heavy slow features (embeddings, aggregates)
- Fetch real-time signals on request
- Join → inference → response

**Pros**:
- Best of both worlds
- Reduced latency with rich features

**Cons**:
- More complex system design

---

### Pattern 4: Streaming Inference
For event-driven systems (fraud, security alerts, clickstream).

**Workflow**:
- Kafka/Kinesis → feature enrich → inference → publish output

**Checklist**:
- [ ] Consumer group configured
- [ ] Dead-letter queue setup
- [ ] Exactly-once or at-least-once semantics defined

---

## 3. Rollout Strategies

### Strategy 1: Shadow Deployment
- Live traffic duplicated to new model
- Responses ignored
- Compare predictions offline

### Strategy 2: Canary Release
- Serve small % of traffic to new model
- Increase gradually

### Strategy 3: Blue-Green Deployment
- Blue (current), Green (new)
- Flip traffic when ready

**Checklist**:
- [ ] Rollout plan approved
- [ ] Rollback automated
- [ ] Logs & dashboards ready

### Choosing a Rollout Strategy

| Strategy | Use when | Risk to users | Rollback speed |
|---|---|---|---|
| Direct deployment | Internal or low-traffic tools | High | Slow (manual redeploy) |
| Blue-green | Zero downtime and instant switch-back needed | Low | Instant (flip traffic) |
| Canary (small slice) | Most production changes | Medium, bounded by slice | Fast (automated) |
| Shadow | High-risk changes you must see on real traffic first | None (responses not served) | Not needed |
| A/B test | You need to measure impact, not only safety | Low | Medium (needs analysis) |
| Feature flag | Gradual or per-segment exposure | Low | Fast (config change) |

Default by system maturity — raise the bar as traffic and blast radius grow:

| Stage | Default | Why |
|---|---|---|
| MVP / development | Direct deployment | Fast iteration, little traffic |
| Beta | Canary | Real users, limited exposure |
| Production | Shadow, then canary | Validate on real traffic before any user sees it |
| Mature production | Canary plus A/B test | Measure impact while limiting exposure |

For batch jobs, pair the scheduler with retries and a failover path; for multi-site serving,
use blue-green or geo-routed rollout and keep every site on the same model and prompt version
(see [multi-region-patterns.md](multi-region-patterns.md)).

---

## 4. Production Readiness Checklist (Final)

- [ ] Serving environment built & tested
- [ ] Canary/shadow test passed
- [ ] Monitoring & alerting enabled
- [ ] SLOs/SLA documented
- [ ] Resilience patterns tested (timeouts, retries)
