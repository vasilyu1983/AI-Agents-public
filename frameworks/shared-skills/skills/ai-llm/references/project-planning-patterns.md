# Project Planning & Stack Selection Patterns

Operational patterns for planning LLM projects, selecting technology stacks, and architecting production pipelines.

---

## Project Planning & Stack Selection (AI Engineering Stack)

### Planning Checklist

- **Use case + expectations:** Success metric, latency/cost targets, safety boundaries, maintenance owner/cadence.
- **Stack fit:** Decide prompt-only vs RAG vs fine-tune vs hybrid; record why options were rejected.
- **Milestones:** Prototype → eval → gated rollout; exit criteria and artifacts per milestone.
- **Artifacts upfront:** System prompt, data contract/schema, evaluation set, monitoring plan, rollback path drafted before build starts.

### Decision Framework

**When to choose each approach:**

| Approach | Use When | Avoid When | Typical Timeline |
|----------|----------|------------|------------------|
| **Prompt-only** | Well-defined task, no domain knowledge needed | Need current data, domain expertise | Days |
| **RAG** | Current knowledge required, factual accuracy critical | Latency <100ms, highly dynamic reasoning | Weeks |
| **Fine-tuning** | Custom behavior, consistent style, private data | Limited data (<1k examples), rapidly changing requirements | Weeks-Months |
| **Hybrid (RAG + Fine-tune)** | Best accuracy, domain expertise + current knowledge | Budget/complexity constraints | Months |

### Stack Selection Matrix

**Core Components:**

| Component | Options | Selection Criteria |
|-----------|---------|-------------------|
| **LLM Provider** | OpenAI, Anthropic, Google, Azure, AWS Bedrock, Self-hosted | Latency, cost, privacy, compliance |
| **Framework** | LangChain, LlamaIndex, LangGraph, Haystack | Complexity, observability, team expertise |
| **Vector DB** | Pinecone, Qdrant, Chroma, Weaviate, Milvus | Scale, latency, budget, deployment model |
| **Orchestration** | Airflow, Dagster, ZenML, Prefect | Existing infra, complexity, team skills |
| **Monitoring** | LangSmith, W&B, Arize, LangFuse | Observability depth, cost, integrations |

---

## Feature/Training/Inference (FTI) Pipeline Blueprint

Complete end-to-end pipeline architecture for production LLM systems.

### Feature Pipeline

**Purpose:** Transform raw data into model-ready features

**Components:**
- **Data collection:** Ingestion from sources (APIs, databases, files)
- **Cleaning:** Deduplication, filtering, normalization, PII detection/redaction
- **Feature store:** Materialization cadence (hourly, daily, event-driven)
- **Versioning:** Track encoders, mappings, transformations

**Checklist:**
- [ ] Data sources identified and access validated
- [ ] Cleaning pipeline with quality metrics
- [ ] Feature store configured with TTL/retention
- [ ] Version control for feature definitions
- [ ] Monitoring for data drift and schema changes

### Training Pipeline

**Purpose:** Reproducible model training with full lineage tracking

**Components:**
- **Repro configs:** Data snapshot + commit SHA for exact reproduction
- **Orchestrator:** Airflow/Dagster/ZenML for pipeline execution
- **Metadata store:** MLflow, W&B for experiment tracking
- **Registry entry:** Model versioning with eval report and signatures

**Checklist:**
- [ ] Training config versioned (data, hyperparameters, code)
- [ ] Orchestration with retry/failure handling
- [ ] Experiment tracking with metrics/artifacts
- [ ] Model registry with promotion workflow
- [ ] Evaluation report attached to each run

### Inference Pipeline

**Purpose:** Serve predictions with safety, observability, and rollback capability

**Components:**
- **Serving config:** Model/adapters, quantization, batching
- **Prompt versioning:** Track prompt templates and versions
- **Logging + guardrails:** Input/output filtering, safety checks
- **Rollout gates:** Shadow mode → canary → full production

**Checklist:**
- [ ] Serving infrastructure with auto-scaling
- [ ] Prompt templates versioned and tested
- [ ] Multi-layer guardrails enabled (input/output filtering)
- [ ] Logging with trace IDs for debugging
- [ ] Canary deployment with automated rollback

### Traceability

**End-to-end lineage tracking:**

```
Run ID: abc-123-def
├─ Feature Build: 2024-01-15T10:00:00Z (data snapshot v1.2)
├─ Training: commit SHA a1b2c3d (config.yaml)
├─ Evaluation: accuracy=0.92, hallucination=2.1%
└─ Deployment: production (canary 10% → 100%)
```

**Storage:**
- Artifacts in model registry (models, adapters, configs)
- Metadata in experiment tracker (metrics, logs, hyperparameters)
- Lineage in metadata store (parent/child relationships)

**Required fields:**
- `run_id`: Unique identifier linking all stages
- `data_snapshot_id`: Exact data version used
- `code_commit`: Git SHA for reproducibility
- `config_hash`: Deterministic config fingerprint
- `eval_report_uri`: Link to evaluation results

---

## AI Engineering Stack Patterns

### Monolithic vs Modular Architecture

**Monolithic (Good for MVP):**
```
Single application
├─ Prompt templates
├─ RAG retrieval
├─ Tool calling
└─ Response generation
```

**Pros:** Simple deployment, fast iteration, low latency
**Cons:** Hard to scale, difficult to test components, tight coupling

**Modular (Production Standard):**
```
Service architecture
├─ Prompt Service (versioned templates)
├─ Retrieval Service (vector DB + reranking)
├─ Tool Service (MCP servers)
├─ LLM Gateway (routing, caching, rate limiting)
└─ Observability Service (logging, tracing, metrics)
```

**Pros:** Independent scaling, easier testing, clear boundaries
**Cons:** Higher latency, more complexity, distributed debugging

### Selection Criteria

| Pattern | Use When | Team Size | Complexity |
|---------|----------|-----------|------------|
| Monolithic | MVP, <10k requests/day | 1-3 engineers | Low |
| Modular | Production, >10k requests/day | 4+ engineers | Medium-High |
| Hybrid | Gradual migration | Any | Medium |

---

## Performance Budgeting

### Setting Budgets Up Front

Define clear performance targets before implementation:

**Token Cost Budget:**
- Target cost per request: $0.01-$0.10 (depending on use case)
- Monthly budget ceiling: $X,000
- Cost allocation: 70% LLM calls, 20% embeddings, 10% infrastructure

**Latency Targets:**
- p50: <500ms (typical)
- p95: <2s (acceptable)
- p99: <5s (maximum tolerance)

**Throughput Requirements:**
- Requests per second: 10-1000 (depends on scale)
- Tokens per second: 50-500 (depends on model/hardware)
- Concurrent users: 100-10,000

**Quality Gates:**
- Hallucination rate: <3%
- Accuracy/F1: >90% (task-dependent)
- Groundedness: >95% (for RAG systems)
- User satisfaction: >4/5 stars

### Profiling Harness

**Testing infrastructure:**

```python
# Load generation with mixed prompt lengths
test_prompts = [
    short_prompts,   # 10-50 tokens
    medium_prompts,  # 50-200 tokens
    long_prompts     # 200-1000 tokens
]

metrics = {
    "goodput": useful_tokens_per_second,
    "gpu_utilization": percent_used,
    "memory_headroom": available_vram,
    "tail_latencies": [p50, p95, p99]
}
```

**Capture:**
- Goodput (useful tokens/s, not just throughput)
- GPU utilization (target: 70-90%)
- Memory headroom (avoid OOM)
- Tail latencies (p95, p99 critical)

### Rollout Gates

**Automated gates before promotion:**

- [ ] Token cost < budget ceiling
- [ ] p95 latency < target
- [ ] GPU utilization 70-90%
- [ ] Quality metrics meet thresholds
- [ ] No critical errors in canary

**Dashboard attachment:**
- Attach performance metrics to deployment PRs
- Automated checks fail if budgets breached
- Manual override requires approval

### Regression Loop

**Continuous performance testing:**

```yaml
triggers:
  - prompt_change: Run perf tests
  - model_change: Run perf tests
  - index_change: Run perf tests
  - scheduled: Daily perf regression suite

gates:
  - regression_threshold: 10% degradation blocks deploy
  - manual_review: Required for 5-10% degradation
```

---

## Related Resources

- **[Production Checklists](production-checklists.md)** - Pre-deployment validation and operational checklists
- **[LLMOps Best Practices](llmops-best-practices.md)** - Operational lifecycle and deployment patterns
- **[Evaluation Patterns](eval-patterns.md)** - Testing, metrics, and quality validation
- **[Decision Matrices](decision-matrices.md)** - Quick reference tables for technology selection

---
