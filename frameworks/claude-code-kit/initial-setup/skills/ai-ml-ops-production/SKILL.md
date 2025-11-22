---
name: ai-ml-ops-production
description: >
  Operational patterns for ML/LLM production (Modern automation-first): event-driven pipelines,
  automated drift detection (18-second response), real-time retraining triggers, data ingestion (dlt),
  deployment (APIs, batch jobs), monitoring, lifecycle management. Emphasizes modular, auditable,
  scalable automation with sub-50ms latency and F1 >0.99 post-incident recovery.
---

# Production ML Engineering – Quick Reference

This skill covers the **production ML lifecycle** with **Modern automation advances**:

1. **Data ingestion** (dlt): Load data from APIs, databases to warehouses
2. **Model deployment**: Batch jobs, real-time APIs, hybrid systems, event-driven automation
3. **Operations**: Real-time monitoring, **18-second drift detection**, automated retraining, incident response

**Key Advances:**

- **Event-driven, modular, auditable pipelines** automating every key phase
- **18-second drift detection** with F1 >0.99 post-attack recovery
- **Automated retraining triggers** (drift, schema change, volume threshold, manual override)
- **Scalable architecture:** >2,300 req/sec with sub-50ms latency

It is execution-focused:

- Data ingestion patterns (REST APIs, database replication, incremental loading)
- Deployment patterns (batch, online, hybrid, streaming, event-driven)
- **Automated monitoring** with real-time drift detection
- **Automated retraining** pipelines (monitor → detect → trigger → validate → deploy)
- Incident handling with rapid recovery (F1 >0.99 restoration)
- Links to copy-paste templates in `templates/`

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Data Ingestion | dlt (data load tool) | `dlt pipeline run`, `dlt init` | Loading from APIs, databases to warehouses |
| Batch Deployment | Airflow, Dagster, Prefect | `airflow dags trigger`, `dagster job launch` | Scheduled predictions on large datasets |
| API Deployment | FastAPI, Flask, TorchServe | `uvicorn app:app`, `torchserve --start` | Real-time inference (<500ms latency) |
| Model Registry | MLflow, W&B | `mlflow.register_model()`, `wandb.log_model()` | Versioning and promoting models |
| Drift Detection | Evidently, WhyLabs | `evidently.dashboard()`, monitor metrics | Automated drift monitoring (18s response) |
| Monitoring | Prometheus, Grafana | `prometheus.yml`, Grafana dashboards | Metrics, alerts, SLO tracking |
| Incident Response | Runbooks, PagerDuty | Documented playbooks, alert routing | Handling failures and degradation |

---

## When to Use This Skill

Claude should invoke this skill when the user asks for **deployment, operations, or data ingestion** help, e.g.:

- "How do I deploy this model to prod?"
- "Design a batch + online scoring architecture."
- "Add monitoring and drift detection to our model."
- "Write an incident runbook for this ML service."
- "Package this LLM/RAG pipeline as an API."
- "Plan our retraining and promotion workflow."
- "Load data from Stripe API to Snowflake."
- "Set up incremental database replication with dlt."
- "Build an ELT pipeline for warehouse loading."

If the user is asking only about **EDA, modelling, or theory**, prefer:

- `ai-ml-data-science` (EDA, features, modelling, SQL transformation with SQLMesh)
- `ai-llm-development` (prompting, fine-tuning, eval)
- `ai-llm-rag-engineering` (retrieval pipeline design)
- `ai-llm-ops-inference` (compression, spec decode, serving internals)

If the user is asking about **SQL transformation (after data is loaded)**, prefer:

- `ai-ml-data-science` (SQLMesh templates for staging, intermediate, marts layers)

---

## Decision Tree: Choosing Deployment Strategy

```text
User needs to deploy: [ML System]
    ├─ Data Ingestion?
    │   ├─ From REST APIs? → dlt REST API templates
    │   ├─ From databases? → dlt database sources (PostgreSQL, MySQL, MongoDB)
    │   └─ Incremental loading? → dlt incremental patterns (timestamp, ID-based)
    │
    ├─ Model Serving?
    │   ├─ Latency <500ms? → FastAPI real-time API
    │   ├─ Batch predictions? → Airflow/Dagster batch pipeline
    │   └─ Mix of both? → Hybrid (batch features + online scoring)
    │
    ├─ Monitoring & Ops?
    │   ├─ Drift detection? → Evidently + automated retraining triggers
    │   ├─ Performance tracking? → Prometheus + Grafana dashboards
    │   └─ Incident response? → Runbooks + PagerDuty alerts
    │
    └─ LLM/RAG Production?
        ├─ Cost optimization? → Caching, prompt templates, token budgets
        └─ Safety? → See ai-ml-ops-security skill
```

---

## Core Patterns Overview

This skill provides 13 production-ready patterns organized into comprehensive guides:

### Data & Infrastructure Patterns

**Pattern 0: Data Contracts, Ingestion & Lineage**
→ See [Data Ingestion Patterns](resources/data-ingestion-patterns.md)

- Data contracts with SLAs and versioning
- Ingestion modes (CDC, batch, streaming)
- Lineage tracking and schema evolution
- Replay and backfill procedures

**Pattern 1: Choose Deployment Mode**
→ See [Deployment Patterns](resources/deployment-patterns.md)

- Decision table (batch, online, hybrid, streaming)
- When to use each mode
- Deployment mode selection checklist

**Pattern 2: Standard Deployment Lifecycle**
→ See [Deployment Lifecycle](resources/deployment-lifecycle.md)

- Pre-deploy, deploy, observe, operate, evolve phases
- Environment promotion (dev → staging → prod)
- Gradual rollout strategies (canary, blue-green)

**Pattern 3: Packaging & Model Registry**
→ See [Model Registry Patterns](resources/model-registry-patterns.md)

- Model registry structure and metadata
- Packaging strategies (Docker, ONNX, MLflow)
- Promotion flows (experimental → production)
- Versioning and governance

### Serving Patterns

**Pattern 4: Batch Scoring Pipeline**
→ See [Deployment Patterns](resources/deployment-patterns.md)

- Orchestration with Airflow/Dagster
- Idempotent scoring jobs
- Validation and backfill procedures

**Pattern 5: Real-Time API Scoring**
→ See [API Design Patterns](resources/api-design-patterns.md)

- Service design (HTTP/JSON, gRPC)
- Input/output schemas
- Rate limiting, timeouts, circuit breakers

**Pattern 6: Hybrid & Feature Store Integration**
→ See [Feature Store Patterns](resources/feature-store-patterns.md)

- Batch vs online features
- Feature store architecture
- Training-serving consistency
- Point-in-time correctness

### Operations Patterns

**Pattern 7: Monitoring & Alerting**
→ See [Monitoring Best Practices](resources/monitoring-best-practices.md)

- Data, performance, and technical metrics
- SLO definition and tracking
- Dashboard design and alerting strategies

**Pattern 8: Drift Detection & Automated Retraining**
→ See [Drift Detection Guide](resources/drift-detection-guide.md)

- Real-time drift detection (18-second response)
- Automated retraining triggers
- Event-driven retraining pipelines
- Performance targets (F1 >0.99 recovery)

**Pattern 9: Incidents & Runbooks**
→ See [Incident Response Playbooks](resources/incident-response-playbooks.md)

- Common failure modes
- Detection, diagnosis, resolution
- Post-mortem procedures

**Pattern 10: LLM / RAG in Production**
→ See [LLM & RAG Production Patterns](resources/llm-rag-production-patterns.md)

- Prompt and configuration management
- Safety and compliance (PII, jailbreaks)
- Cost optimization (token budgets, caching)
- Monitoring and fallbacks

**Pattern 11: Cross-Region, Residency & Rollback**
→ See [Multi-Region Patterns](resources/multi-region-patterns.md)

- Multi-region deployment architectures
- Data residency and tenant isolation
- Disaster recovery and failover
- Regional rollback procedures

**Pattern 12: Online Evaluation & Feedback Loops**
→ See [Online Evaluation Patterns](resources/online-evaluation-patterns.md)

- Feedback signal collection (implicit, explicit)
- Shadow and canary deployments
- A/B testing with statistical significance
- Human-in-the-loop labeling
- Automated retraining cadence

---

## Resources (Detailed Guides)

For comprehensive operational guides, see:

**Core Infrastructure:**

- **[Data Ingestion Patterns](resources/data-ingestion-patterns.md)** - Data contracts, CDC, batch/streaming ingestion, lineage, schema evolution
- **[Deployment Lifecycle](resources/deployment-lifecycle.md)** - Pre-deploy validation, environment promotion, gradual rollout, rollback
- **[Model Registry Patterns](resources/model-registry-patterns.md)** - Versioning, packaging, promotion workflows, governance
- **[Feature Store Patterns](resources/feature-store-patterns.md)** - Batch/online features, hybrid architectures, consistency, latency optimization

**Serving & APIs:**

- **[Deployment Patterns](resources/deployment-patterns.md)** - Batch, online, hybrid, streaming deployment strategies and architectures
- **[API Design Patterns](resources/api-design-patterns.md)** - ML/LLM/RAG API patterns, input/output schemas, reliability patterns, versioning

**Operations & Reliability:**

- **[Monitoring Best Practices](resources/monitoring-best-practices.md)** - Metrics collection, alerting strategies, SLO definition, dashboard design
- **[Drift Detection Guide](resources/drift-detection-guide.md)** - Statistical tests, automated detection, retraining triggers, recovery strategies
- **[Incident Response Playbooks](resources/incident-response-playbooks.md)** - Runbooks for common failure modes, diagnostics, resolution steps

**Advanced Patterns:**

- **[LLM & RAG Production Patterns](resources/llm-rag-production-patterns.md)** - Prompt management, safety, cost optimization, caching, monitoring
- **[Multi-Region Patterns](resources/multi-region-patterns.md)** - Multi-region deployment, data residency, disaster recovery, rollback
- **[Online Evaluation Patterns](resources/online-evaluation-patterns.md)** - A/B testing, shadow deployments, feedback loops, automated retraining

---

## Templates

Use these as copy-paste starting points for production artifacts:

### Data Ingestion (dlt)

For loading data into warehouses and pipelines:

- **[dlt basic pipeline setup](templates/ingestion/template-dlt-pipeline.md)** - Install, configure, run basic extraction and loading
- **[dlt REST API sources](templates/ingestion/template-dlt-rest-api.md)** - Extract from REST APIs with pagination, authentication, rate limiting
- **[dlt database sources](templates/ingestion/template-dlt-database-source.md)** - Replicate from PostgreSQL, MySQL, MongoDB, SQL Server
- **[dlt incremental loading](templates/ingestion/template-dlt-incremental.md)** - Timestamp-based, ID-based, merge/upsert patterns, lookback windows
- **[dlt warehouse loading](templates/ingestion/template-dlt-warehouse-loading.md)** - Load to Snowflake, BigQuery, Redshift, Postgres, DuckDB

**Use dlt when:**

- Loading data from APIs (Stripe, HubSpot, Shopify, custom APIs)
- Replicating databases to warehouses
- Building ELT pipelines with incremental loading
- Managing data ingestion with Python

**For SQL transformation (after ingestion), use:**

→ `ai-ml-data-science` skill (SQLMesh templates for staging/intermediate/marts layers)

### Deployment & Packaging

- **[Deployment & MLOps template](templates/deployment/template-deployment-mlops.md)** - Complete MLOps lifecycle, model registry, promotion workflows
- **[API service template](templates/deployment/template-api-service.md)** - Real-time REST/gRPC API with FastAPI, input validation, rate limiting
- **[Batch scoring pipeline template](templates/deployment/template-batch-pipeline.md)** - Orchestrated batch inference with Airflow/Dagster, validation, backfill

### Monitoring & Operations

- **[Monitoring & alerting template](templates/monitoring/template-monitoring-plan.md)** - Data/performance/technical metrics, dashboards, SLO definition
- **[Drift detection & retraining template](templates/monitoring/template-drift-retraining.md)** - Automated drift detection, retraining triggers, promotion pipelines
- **[Incident runbook template](templates/ops/template-incident-runbook.md)** - Failure mode playbooks, diagnosis steps, resolution procedures

## Navigation

**Resources**
- [resources/drift-detection-guide.md](resources/drift-detection-guide.md)
- [resources/model-registry-patterns.md](resources/model-registry-patterns.md)
- [resources/online-evaluation-patterns.md](resources/online-evaluation-patterns.md)
- [resources/monitoring-best-practices.md](resources/monitoring-best-practices.md)
- [resources/llm-rag-production-patterns.md](resources/llm-rag-production-patterns.md)
- [resources/api-design-patterns.md](resources/api-design-patterns.md)
- [resources/incident-response-playbooks.md](resources/incident-response-playbooks.md)
- [resources/deployment-patterns.md](resources/deployment-patterns.md)
- [resources/data-ingestion-patterns.md](resources/data-ingestion-patterns.md)
- [resources/deployment-lifecycle.md](resources/deployment-lifecycle.md)
- [resources/feature-store-patterns.md](resources/feature-store-patterns.md)
- [resources/multi-region-patterns.md](resources/multi-region-patterns.md)

**Templates**
- [templates/ingestion/template-dlt-pipeline.md](templates/ingestion/template-dlt-pipeline.md)
- [templates/ingestion/template-dlt-rest-api.md](templates/ingestion/template-dlt-rest-api.md)
- [templates/ingestion/template-dlt-database-source.md](templates/ingestion/template-dlt-database-source.md)
- [templates/ingestion/template-dlt-incremental.md](templates/ingestion/template-dlt-incremental.md)
- [templates/ingestion/template-dlt-warehouse-loading.md](templates/ingestion/template-dlt-warehouse-loading.md)
- [templates/deployment/template-deployment-mlops.md](templates/deployment/template-deployment-mlops.md)
- [templates/deployment/template-api-service.md](templates/deployment/template-api-service.md)
- [templates/deployment/template-batch-pipeline.md](templates/deployment/template-batch-pipeline.md)
- [templates/ops/template-incident-runbook.md](templates/ops/template-incident-runbook.md)
- [templates/monitoring/template-drift-retraining.md](templates/monitoring/template-drift-retraining.md)
- [templates/monitoring/template-monitoring-plan.md](templates/monitoring/template-monitoring-plan.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---

## External Resources

See `data/sources.json` for curated references on:

- Serving frameworks (FastAPI, Flask, gRPC, TorchServe, KServe, Ray Serve)
- Orchestration (Airflow, Dagster, Prefect)
- Model registries and MLOps (MLflow, W&B, Vertex AI, Sagemaker)
- Monitoring and observability (Prometheus, Grafana, OpenTelemetry, Evidently)
- Feature stores (Feast, Tecton, Vertex, Databricks)
- Streaming & messaging (Kafka, Pulsar, Kinesis)
- LLMOps & RAG infra (vector DBs, LLM gateways, safety tools)

---

## Related Skills

For adjacent topics, reference these skills:

- **[ai-ml-data-science](../ai-ml-data-science/SKILL.md)** - EDA, feature engineering, modelling, evaluation, SQLMesh transformations
- **[ai-llm-development](../ai-llm-development/SKILL.md)** - Prompting, fine-tuning, evaluation for LLMs
- **[ai-llm-engineering](../ai-llm-engineering/SKILL.md)** - Agentic workflows, multi-agent systems, LLMOps
- **[ai-llm-rag-engineering](../ai-llm-rag-engineering/SKILL.md)** - RAG pipeline design, chunking, retrieval, evaluation
- **[ai-llm-ops-inference](../ai-llm-ops-inference/SKILL.md)** - Model serving optimization, quantization, batching
- **[ai-ml-ops-security](../ai-ml-ops-security/SKILL.md)** - Security, privacy, governance, compliance
- **[ai-prompt-engineering](../ai-prompt-engineering/SKILL.md)** - Prompt design patterns and best practices

---

Use this skill to **turn trained models into reliable services**, not to derive the model itself.
