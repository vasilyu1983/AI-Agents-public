# Backend Selection

## Table of Contents

- [Default](#default)
- [Selection Axes](#selection-axes)
- [Backend Matrix Condensed](#backend-matrix-condensed)

Choose the storage and retrieval backend after identifying corpus shape, scale, filter needs, residency, access pattern, and ops appetite.

For per-backend deep dives (S3 Vectors, Turbopuffer, Pinecone Serverless, Bedrock KB, OpenSearch, Vertex, Azure AI Search, edge/serverless tier), see [backend-selection-extended.md](backend-selection-extended.md).

## Upstream Decision (Run This First)

Backend selection is a *substrate-level* decision. Before picking a vector backend, validate the broader stack against the org-tier matrix in [`../../ai-context-layer/references/architectures-by-organization.md`](../../ai-context-layer/references/architectures-by-organization.md) (T1–T5 × S1–S5) and the combination rules in [`../../ai-context-layer/references/substrate-combinations.md`](../../ai-context-layer/references/substrate-combinations.md) (C1–C5 = real value; X1–X5 = clever but costly). Routed via `router-engineering/engineering-scenarios.md` §L1/L2.

The default below assumes those checks point at a vector substrate. If they point at "files only" (T1) or "Postgres only, no separate vector" (T2 RA9 converged), this doc is the wrong starting point — go back to the substrate decision first.

## Default

Use **Postgres + pgvector** for v1 unless a concrete constraint says otherwise.

Good fit:

- repo and docs brains
- compliance and policy corpora with strong metadata requirements
- small to medium corpora (≤10M vectors, sustained hot working set)
- teams that need plain SQL, backups, migrations, and inspectability
- systems where source truth, ingest ledger, query logs, and eval tables belong together

Avoid as the only backend when:

- sustained vector QPS and vector count exceed Postgres operating comfort
- filter-heavy ANN queries cannot meet recall or latency targets after tuning
- cost-per-stored-vector dominates the budget (cold/archival corpora)
- advanced multi-stage ranking is the primary product
- the team needs a managed vector service more than SQL control

## Selection Axes

Pick a backend against these axes, in this priority order:

1. **Access pattern** — hot (sustained QPS, low p95) vs cold (bursty, archival, p95 in hundreds of ms acceptable)
2. **Scale** — vectors, sustained QPS, peak QPS, churn (writes/day)
3. **Cost shape** — pay-for-RAM (hot index) vs pay-for-storage+per-query (object-backed) vs pay-per-node (managed cluster)
4. **Filter complexity** — simple tag filters vs deep metadata predicates vs full SQL joins
5. **Tenant model** — row-level (RLS) vs namespace-per-tenant vs index/collection-per-tenant
6. **Cloud gravity** — AWS / GCP / Azure / Cloudflare / multi-cloud / self-host
7. **Residency & compliance** — UK/EU data residency, audit, deletion guarantees, customer-managed keys
8. **Ops appetite** — SQL-native vs managed service vs cluster ownership
9. **Update freshness** — live editorial (seconds) vs batch (minutes/hours) vs archival (rare writes)
10. **Ecosystem fit** — already on Bedrock / Vertex / Copilot? assistant-bundled wins on time-to-first-answer

## Backend Matrix (Condensed)

Detailed cards live in [backend-selection-extended.md](backend-selection-extended.md).

### SQL-native

| Backend | Use When | Watch For |
|---|---|---|
| **Postgres + pgvector** | Durable default, SQL-first brain, repo/docs/policy corpora, ≤10M vectors hot | HNSW memory, filtered recall, operational tuning |
| **Postgres + pgvectorscale** | 10M–100M Postgres-native, filter-heavy, StreamingDiskANN | Extension maturity, managed-host availability |
| **Postgres + ParadeDB / pg_textsearch** | Built-in FTS insufficient, true BM25 + vectors in one engine | Extension availability, portability |

> **Capability recipes (pointers — not duplicated here):** [BM25 vs ts_rank](bm25-when-ts_rank-isnt-enough.md) · [learned-sparse / SPLADE leg](learned-sparse-splade-leg.md) · [quantization + two-pass rescore](quantization-and-rescore.md) · [embedded / local brain](embedded-local-brain.md) · [self-hosted embedding runtime](embedding-runtime.md)

### Dedicated vector services (self-host or managed)

| Backend | Use When | Watch For |
|---|---|---|
| **Qdrant** | Dedicated service, strong filtering, simple ops, payload indexing | Extra service, data duplication, joins move to app |
| **Weaviate** | Productized hybrid search, modules, managed workflows | Schema/vendor model choices, portability |
| **Milvus / Zilliz** | Large-scale (100M+), sparse+dense, GPU options, high corpus volume | Cluster complexity, ops cost |
| **Vespa** | Search/ranking-heavy serving with custom ranking pipelines | Steep learning curve; overkill for simple brains |
| **LanceDB** | Local/embedded, columnar, multimodal, high-churn data-science | Production serving and governance boundaries |
| **Chroma** | Local prototype, lightweight app brain | Governance, scale, production durability |

### Serverless / object-storage-backed (cost-driven tier)

| Backend | Use When | Watch For |
|---|---|---|
| **AWS S3 Vectors** | Cold/archival corpora on AWS, Bedrock KB integration, ~90% cheaper than hot indexes | Higher latency (hundreds of ms p95), AWS-only, write-batch model |
| **Turbopuffer** | Cheap large-scale, namespace-per-tenant, object-storage-backed | Newer ecosystem, latency profile vs hot indexes |
| **Pinecone Serverless** | No-ops, scale-to-zero, dynamic scale, mixed hot/cold | Lock-in, ACL coarse, cost spikes with QPS |
| **Cloudflare Vectorize / Upstash Vector** | Edge functions, serverless apps, small–medium footprint | Modest scale ceiling, query-cost variance |

### Hyperscaler managed (assistant-bundled or platform-native)

| Backend | Use When | Watch For |
|---|---|---|
| **AWS Bedrock Knowledge Bases** | "RAG on AWS, now" — bundles ingest + retrieval + grounding (can sit on S3 Vectors / OpenSearch / Aurora); 2026 adds native reranking, GraphRAG (Neptune Analytics), and multimodal retrieval | Region constraints; ranking control improved but still less than self-hosted |
| **AWS Kendra GenAI Index** | Managed retriever (hybrid + semantic + built-in reranker); index once, reuse across Bedrock KB and Amazon Q Business | Cost; AWS-only; less control than owning the index |
| **Azure AI Search (vector)** | Microsoft stack, Copilot integration, hybrid out of the box | Azure-only, per-tier pricing model |
| **Vertex AI Vector Search** | GCP stack, Gemini grounding, large-scale managed ANN | GCP-only, costly idle, separate from BigQuery vectors |
| **OpenAI / Anthropic File Search** | Fastest hosted assistant path, low infra ownership | ACL, deletion, residency, ranking opacity, vendor lock-in |

### Search-engine k-NN (lift-and-shift)

| Backend | Use When | Watch For |
|---|---|---|
| **Elasticsearch / OpenSearch k-NN** | Already on ELK, need lexical+vector in one cluster | Vector recall tuning, RAM cost, version skew |
| **Redis Stack (RediSearch)** | Already on Redis, hot small corpus, sub-10ms p95 | Memory cost, persistence model, recall tuning |
| **MongoDB Atlas Vector Search** | Already on MongoDB, JSON-doc model fits | Atlas-only, recall vs filtered query tradeoffs |

### Non-vector escape hatches

| Backend | Use When | Watch For |
|---|---|---|
| **Compiled wiki / lexical-only** | Small, stable corpus where direct reads or BM25 solve the problem | Poor semantic recall for broad paraphrase queries |

## Escalation Triggers

Escalate away from default pgvector only when measured evidence justifies it. Pick the destination by which axis breaks:

- **Recall** drops under the corpus eval target despite hybrid + reranking → Qdrant/Weaviate/Milvus (better filtered ANN), or rerank harder
- **Filtered vector search** misses relevant chunks under realistic filters → pgvectorscale, Qdrant payload indexes
- **Index memory** or build time blocks operations → DiskANN (pgvectorscale), Milvus, S3 Vectors for cold tier
- **p95 latency** exceeds product budget under expected concurrency → dedicated service (Qdrant/Pinecone) or sharding
- **Ingestion churn** overwhelms the query-serving instance → split read/write, move to managed
- **Cost-per-vector** dominates (large cold corpus) → S3 Vectors, Turbopuffer, Pinecone Serverless
- **A required feature** is backend-native elsewhere and expensive to rebuild → choose by feature
- **Ecosystem** already on Bedrock / Vertex / Copilot and time-to-first-answer matters → assistant-bundled tier

## Decision Flow

```text
Can direct files, compiled wiki, or lexical search answer the task?
  -> yes: do not add vector infra yet

Need semantic recall over a changing corpus?
  -> yes, continue

Is access pattern HOT (sustained QPS, low p95 < ~150 ms)?
  -> yes:
       small/medium + SQL preferred   -> Postgres + pgvector (default)
       large + Postgres-native        -> pgvectorscale
       large + dedicated service      -> Qdrant / Weaviate / Milvus
       already on ELK / Redis / Mongo -> use their k-NN
  -> no (cold/archival or bursty):
       on AWS + Bedrock workflow      -> S3 Vectors (+ Bedrock KB)
       cheap large-scale multi-tenant -> Turbopuffer
       scale-to-zero managed          -> Pinecone Serverless
       edge / serverless app          -> Cloudflare Vectorize / Upstash

Need graph traversal to bound evidence?
  -> add graph/edge tables or graph store before retrieval

Need fastest hosted assistant path?
  -> Bedrock KB (AWS) / Vertex (GCP) / Azure AI Search / OpenAI File Search
     with explicit deletion / ACL / residency caveats
```

## Cost-Shape Cheatsheet

Three pricing archetypes drive most decisions at scale:

- **Pay-for-RAM (hot index)** — pgvector, Qdrant, Weaviate, Milvus, Vespa, OpenSearch k-NN, Redis. Cost grows with vectors × dimension × replicas. Best for hot working sets.
- **Pay-for-storage + per-query (object-backed)** — S3 Vectors, Turbopuffer, Pinecone Serverless. Storage is cheap; cost grows with QPS. Best for cold/archival or bursty.
- **Pay-per-node (managed cluster)** — Vertex Vector Search, Azure AI Search tiers, Milvus/Zilliz Cloud. Predictable, but expensive at low utilization.

At 100M vectors, archetype 1 is typically 10–100× more expensive at rest than archetype 2.

For concrete formulas (HNSW RAM footprint, object-storage break-even QPS, embedding/rerank/LLM line items) and worked examples at 1M / 10M / 100M scale, see [cost-calculation.md](cost-calculation.md).

## Tenant Model Cheatsheet

- **Row-level (RLS)** — pgvector with `assets/sql/006_rls_multitenant.sql`. Best when tenants share schema and queries are SQL-native.
- **Namespace-per-tenant** — Turbopuffer, Pinecone, Qdrant collections. Best when tenant counts are high and isolation matters.
- **Index/collection-per-tenant** — Qdrant, Weaviate, Milvus. Best for hard isolation, low tenant count.
- **Bring-your-own-key / region** — Bedrock KB, Vertex, Azure. Best for regulated data residency.

## Current-Source Rule

Backend capabilities, extension support, pricing, benchmark claims, and model rankings drift. Verify against primary vendor docs (see [data/sources.json](../data/sources.json)) before turning this matrix into a purchase or migration decision. S3 Vectors, Turbopuffer, and Pinecone Serverless in particular have moved fast in 2025–2026.
