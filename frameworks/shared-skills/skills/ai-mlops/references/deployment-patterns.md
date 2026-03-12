# Deployment Patterns for ML & LLM Systems

These deployment patterns define reliable, repeatable ways to ship ML/RAG/LLM models into
production environments.

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

---

## 4. Production Readiness Checklist (Final)

- [ ] Serving environment built & tested
- [ ] Canary/shadow test passed
- [ ] Monitoring & alerting enabled
- [ ] SLOs/SLA documented
- [ ] Resilience patterns tested (timeouts, retries)