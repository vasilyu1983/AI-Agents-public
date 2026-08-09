# Backend Selection — Extended

## Table of Contents

- [SQL-native](#sql-native)
- [Dedicated vector services](#dedicated-vector-services)
- [Serverless object-storage-backed cost-driven tier](#serverless--object-storage-backed-cost-driven-tier)
- [Hyperscaler managed assistant-bundled or platform-native](#hyperscaler-managed-assistant-bundled-or-platform-native)

Per-backend cards beyond the condensed matrix in [backend-selection.md](backend-selection.md). Use this when an escalation trigger has fired and you need to choose a concrete non-default backend.

Verify against primary vendor docs before committing. Pricing, regions, quotas, and feature sets drift quarterly — especially for the serverless / object-backed tier.

---

## SQL-native

### Postgres + pgvector

- **Shape**: Postgres extension. HNSW or IVFFlat indexes, halfvec, iterative scan, hybrid via FTS.
- **Best for**: V1 default. Repo/docs/policy brains where SQL, joins, RLS, and inspectability matter.
- **Scale ceiling (practical)**: ~10M vectors hot per instance before HNSW memory becomes the constraint.
- **Cost shape**: Pay-for-RAM (hot). Sized by Postgres host.
- **Filters**: Full SQL. Use `assets/sql/002_indexes_hnsw.sql` and the iterative_scan knob.
- **Multitenant**: RLS. See `assets/sql/006_rls_multitenant.sql`.
- **Watch for**: HNSW build memory, filtered-recall under selective predicates, pg_dump backup time at scale.

### Postgres + pgvectorscale (Timescale)

- **Shape**: StreamingDiskANN + statbm25 in Postgres.
- **Best for**: 10M–100M vectors when you want to stay in Postgres and need DiskANN-class recall under filters.
- **Cost shape**: Pay-for-RAM + SSD; cheaper than pure HNSW at the same recall.
- **Watch for**: Managed-host support (Timescale Cloud supports it natively; others vary), extension version skew.

### Postgres + ParadeDB / pg_textsearch

- **Shape**: True BM25 in Postgres (Tantivy-backed in ParadeDB) alongside pgvector.
- **Best for**: Compliance/policy or code corpora where BM25 quality matters and you want one engine.
- **Watch for**: Extension availability on managed hosts, portability if you later migrate.

> **Capability recipes (pointers — not duplicated here):** [BM25 vs ts_rank](bm25-when-ts_rank-isnt-enough.md) · [learned-sparse / SPLADE leg](learned-sparse-splade-leg.md) · [quantization + two-pass rescore](quantization-and-rescore.md) · [embedded / local brain](embedded-local-brain.md) · [self-hosted embedding runtime](embedding-runtime.md)

---

## Dedicated vector services

### Qdrant

- **Shape**: Rust-native vector DB, HNSW, payload indexes, scalar/binary quantization.
- **Best for**: Filter-heavy retrieval where payload index + ANN combine cleanly. Strong self-host story; managed cloud available.
- **Cost shape**: Pay-per-node (managed) or self-host.
- **Watch for**: Data duplication with system-of-record; joins move to app layer.

### Weaviate

- **Shape**: Vector DB with modules (rerankers, generative, multi-tenant tenants).
- **Best for**: Productized hybrid search where you want batteries-included modules.
- **Watch for**: Vendor schema choices, model-module lock-in.

### Milvus / Zilliz Cloud

- **Shape**: Distributed vector DB. Multiple index types (HNSW, IVF, DiskANN, GPU), sparse+dense.
- **Best for**: 100M+ vectors, high QPS, GPU-accelerated workloads.
- **Watch for**: Cluster complexity, cost at low utilization, operational learning curve.

### Vespa

- **Shape**: Search and ranking platform. Tensor + lexical + structured retrieval in one ranking pipeline.
- **Best for**: When ranking itself is the product (e-commerce search, custom multi-stage ranking).
- **Watch for**: Steep learning curve; overkill for simple brains.

### LanceDB

- **Shape**: Embedded columnar (Lance format) vector DB. Local-first, S3-backed in newer versions.
- **Best for**: Data-science/notebook workflows, high-churn experimental corpora, multimodal.
- **Watch for**: Production serving, multi-writer semantics, governance.

### Chroma

- **Shape**: Lightweight embedded vector DB, server mode available.
- **Best for**: Prototypes, demos, small in-process brains.
- **Watch for**: Governance, scale, durability beyond prototypes.

---

## Serverless / object-storage-backed (cost-driven tier)

This tier shifts the cost shape from pay-for-RAM to pay-for-storage + per-query. At ~100M vectors and bursty access, it can be 10–100× cheaper than hot indexes.

### AWS S3 Vectors

- **Shape**: Vector-native S3 buckets. Sub-second similarity search on object-storage-backed indexes. Native Bedrock Knowledge Bases integration.
- **Best for**:
  - Cold/archival corpora on AWS (compliance history, log embeddings, contract archives)
  - Bedrock RAG workflows where keeping vectors next to S3 source documents simplifies governance
  - Cost-sensitive large corpora where p95 latency in the hundreds of ms is acceptable
- **Cost shape**: Pay-for-storage + per-query. ~90% cheaper than OpenSearch/Pinecone for large cold corpora (per AWS positioning).
- **Filters**: Metadata filters supported; full SQL joins do not apply.
- **Latency**: Sub-second per AWS, typically higher than in-memory HNSW. Not for chat-fast loops at sustained high QPS without a hot tier in front.
- **Tenant model**: Per-bucket / per-index isolation. Good for tenant-per-bucket designs.
- **Residency**: Standard S3 region selection. Good for UK/EU residency requirements.
- **Watch for**: AWS-only, write-batch behavior, evolving feature surface (verify quotas and regions), no native graph traversal, limited ranking control compared to Vespa/OpenSearch.
- **Pair with**: Bedrock Knowledge Bases for the assistant-bundled path; or use directly via `s3vectors` API for custom pipelines.

### Turbopuffer

- **Shape**: Object-storage-backed vector + lexical DB. Namespace-per-tenant model.
- **Best for**: Multi-tenant SaaS with many tenants, cheap large-scale, hybrid out of the box.
- **Cost shape**: Pay-for-storage + per-query. Competitive with S3 Vectors on storage; designed for multitenant SaaS.
- **Watch for**: Newer ecosystem, smaller community, latency profile vs hot indexes.

### Pinecone Serverless

- **Shape**: Managed vector DB with scale-to-zero serverless tier (distinct from pod-based Pinecone).
- **Best for**: No-ops production RAG with dynamic load, mixed hot/cold corpora, fast time-to-first-answer.
- **Cost shape**: Per-read + per-write + storage. Predictable for steady QPS; cost spikes possible under high read load.
- **Watch for**: Lock-in, ACL granularity (namespace-level), region availability, opaque ranking internals.

### Cloudflare Vectorize / Upstash Vector

- **Shape**: Serverless vector DBs sitting next to edge runtimes (Workers / serverless functions).
- **Best for**: Edge apps, low-footprint serverless RAG, dev-friendly free tiers.
- **Cost shape**: Per-query + storage, with generous free tiers.
- **Watch for**: Scale ceilings (suited to small–medium corpora), query-cost variance, regional coverage.

---

## Hyperscaler managed (assistant-bundled or platform-native)

Pick these when ecosystem gravity and time-to-first-answer dominate over ranking control.

### AWS Bedrock Knowledge Bases

- **Shape**: Managed ingest → chunk → embed → store → retrieve → ground pipeline. Sits on top of S3 Vectors, OpenSearch Serverless, Aurora pgvector, or other vector stores.
- **Best for**: AWS-first orgs wanting "RAG on AWS, now" without owning the pipeline.
- **Watch for**: Limited ranking control, region constraints, chunking-strategy lock-in, eval visibility weaker than a custom pipeline.

### Azure AI Search (vector)

- **Shape**: Managed search service with native vector + hybrid + semantic ranker.
- **Best for**: Microsoft stack, Copilot integration, customers who already buy Azure search.
- **Cost shape**: Per-tier (replicas × partitions).
- **Watch for**: Azure-only, tier ladder pricing, vector quota by tier.

### Vertex AI Vector Search

- **Shape**: Managed ANN on GCP. Streaming updates, large-scale serving.
- **Best for**: GCP-first, Gemini grounding, large-scale managed ANN with predictable SLOs.
- **Cost shape**: Pay-per-node-hour. Costly at low utilization.
- **Watch for**: Separate product from BigQuery's `VECTOR_SEARCH` — pick based on access pattern.

### OpenAI File Search / Anthropic Files / Bedrock Agents

- **Shape**: Assistant-bundled retrieval. Upload files, get retrieval, no infra.
- **Best for**: Prototypes, single-tenant tools, internal copilots where ranking opacity is acceptable.
- **Watch for**: ACL granularity, deletion semantics, residency, vendor lock-in, ranking-internals opacity, eval reproducibility.

---

## Search-engine k-NN (lift-and-shift)

### Elasticsearch / OpenSearch k-NN

- **Shape**: Existing search engines extended with k-NN (HNSW). OpenSearch also has a serverless tier.
- **Best for**: Teams already on ELK/OpenSearch wanting BM25 + vector in one cluster. OpenSearch Serverless is a common Bedrock KB store.
- **Watch for**: Vector recall tuning, RAM cost relative to dedicated vector DBs, version skew between Elastic and OpenSearch forks.

### Redis Stack (RediSearch)

- **Shape**: Redis modules adding vector search.
- **Best for**: Hot small corpora (<1M vectors) where sub-10ms p95 matters and Redis is already in stack.
- **Watch for**: RAM cost grows fast with dimension, persistence model assumptions, recall tuning.

### MongoDB Atlas Vector Search

- **Shape**: Vector indexes on Atlas collections; works alongside Atlas Search (Lucene) for hybrid.
- **Best for**: Teams already on MongoDB where JSON-doc model fits the corpus.
- **Watch for**: Atlas-only, recall vs filtered query tradeoffs, index build cost.

---

## Choosing Between Look-Alikes

### "Cheap large-scale" — S3 Vectors vs Turbopuffer vs Pinecone Serverless

| Axis | S3 Vectors | Turbopuffer | Pinecone Serverless |
|---|---|---|---|
| Cloud | AWS-only | Cloud-agnostic (runs on object storage) | Cloud-agnostic managed |
| Tenant model | Per-bucket / per-index | Namespace-per-tenant (designed for it) | Namespace-per-tenant |
| Hybrid (BM25 + vector) | Limited; pair with OpenSearch | Native hybrid | Sparse-dense supported |
| Bedrock integration | Native | None | None |
| Latency archetype | Cold (hundreds of ms) | Cold–warm | Warm (with cache) |
| Best fit | Bedrock RAG, archival on AWS | Multi-tenant SaaS with many tenants | No-ops production RAG |

### "Assistant-bundled fastest path" — Bedrock KB vs Vertex vs Azure vs OpenAI File Search

| Axis | Bedrock KB | Vertex | Azure AI Search | OpenAI File Search |
|---|---|---|---|---|
| Cloud | AWS | GCP | Azure | Vendor-cloud |
| Ranking control | Medium | Medium | High (semantic ranker) | Low |
| Eval visibility | Medium | Medium | High | Low |
| Residency | AWS regions | GCP regions | Azure regions | Limited |
| Best fit | AWS estate | GCP estate, Gemini | Microsoft estate, Copilot | Prototype, single-vendor |

### "Already in our stack" — search-engine k-NN

| Axis | OpenSearch / Elastic | Redis Stack | Mongo Atlas |
|---|---|---|---|
| Strength | Hybrid + ops familiarity | Sub-10ms latency | JSON-doc fit |
| Scale ceiling | High | Memory-bound | Medium |
| Best fit | Already on ELK | Hot small corpus | Already on Mongo |

---

## Migration Notes

Moving between archetypes is non-trivial. Plan for:

- **Re-embedding only if model changes** — never overwrite embeddings in place during a live cutover. Use `model_id` columns from day one (see [postgres-pgvector-default.md](postgres-pgvector-default.md)).
- **Backfill order** — load source-of-truth → chunks → embeddings → indexes → eval re-baseline.
- **Hybrid period** — run both backends with dual-write, route a percentage of queries to the new one, compare via the eval harness (see [eval-by-corpus-type.md](eval-by-corpus-type.md)).
- **Citation stability** — keep stable evidence IDs and source anchors across backends so citations don't break.

See [production-runbook.md](production-runbook.md) for the embedding-migration drill.

---

## When NOT to Move Off pgvector

Most teams escalate too early. Stay on pgvector when:

- You haven't run a labeled eval yet — moving backends without an eval baseline trades one black box for another.
- You haven't tuned HNSW (`m`, `ef_construction`, `ef_search`, `hnsw.iterative_scan`) or added hybrid + rerank.
- The cost concern is theoretical, not measured against actual usage.
- Compliance or audit requirements make SQL inspectability a hard requirement.
- The team doesn't have ops capacity for an additional dedicated service.

The default exists because it's right most of the time. Escalate against evidence, not hype.
