# S3 Vectors — Vector Backend Choice

Amazon S3 Vectors is a cost-optimized vector storage tier that reached GA (generally available, 14 regions) in December 2025 and is mainstream by Q1 2026. It stores vectors as S3 objects with a built-in approximate-nearest-neighbor index, supporting large-scale vector workloads at sub-second cold and ~100ms warm latency for as little as ~10% of traditional vector-DB cost.

It is the default vector backend choice on AWS for new builds in 2026, replacing "Aurora pgvector by default" and "OpenSearch by default" for most workloads.

---

## Table of Contents

- [What S3 Vectors is](#what-s3-vectors-is)
- [Cost shape](#cost-shape)
- [Latency profile](#latency-profile)
- [When S3 Vectors wins](#when-s3-vectors-wins)
- [When to pick something else](#when-to-pick-something-else)
- [Integration with Bedrock Knowledge Bases](#integration-with-bedrock-knowledge-bases)
- [Direct API access](#direct-api-access)
- [Limits and lock-in](#limits-and-lock-in)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

---

## What S3 Vectors is

A storage tier inside Amazon S3 specifically for vectors:

- Vectors stored as S3 objects in a managed format
- Built-in ANN index (the index is managed by AWS, not by you)
- Query API for nearest-neighbor search with metadata filtering
- Integrates natively with **Bedrock Knowledge Bases** as a vector store option
- Up to 2 billion vectors per index (GA limit); trillions per bucket across many indexes — verify current AWS docs
- Auto-scales across multiple indexes

The mental model: S3 Vectors is to vector storage what S3 is to object storage — cheap, durable, scales to large size, sub-second access. Not the fastest, but the cheapest that's still fast enough for most production RAG.

---

## Cost shape

The 2026 economic shift. Order-of-magnitude comparison (model only — verify current pricing):

| Backend | Relative cost at 100M vectors | Notes |
|---|---|---|
| **S3 Vectors** | **~1x** (baseline, cheapest) | Storage + per-query charges; no provisioned capacity |
| pgvector on Aurora Serverless | ~5–8x | Includes Aurora ACU charges |
| OpenSearch Serverless | ~6–10x | Per-OCU billing, minimum OCU floor |
| Pinecone Standard | ~8–12x | Per-pod or serverless tier |
| OpenSearch Managed Cluster | ~10–15x | Instance-hour billing, multi-AZ |

This is the headline ~90% cost reduction figure AWS quotes. It is real for cold or rarely-queried corpora; the gap narrows on hot workloads where the alternatives' provisioned cost amortizes.

**Implication for the vector-backend decision in `ai-vector-brain`:** S3 Vectors becomes the AWS default. Choose another only when latency or co-location demands it.

---

## Latency profile

| Query class | Latency |
|---|---|
| **Cold query** (first hit after idle) | Sub-second (typically 200–800ms) |
| **Warm query** (recent hit) | ~100ms |
| **Filtered query** (with metadata predicate) | Similar to warm, depending on filter selectivity |

This is **not** the fastest tier — Redis Enterprise and well-tuned Pinecone serve sub-50ms p99. For most RAG workloads, the 100ms warm path is fine — model inference and reranker add ≥ 300ms regardless.

If you need < 50ms vector retrieval, S3 Vectors is not the right tier.

---

## When S3 Vectors wins

1. **AWS-native RAG.** You are on AWS and want managed vector storage with Bedrock KB or self-managed retrieval.
2. **Cost-sensitive scale.** Million-to-trillion vector range where 90% cost reduction is meaningful.
3. **Cold or warm-but-not-hot workloads.** Most enterprise knowledge bases hit a long tail of vectors that rarely get queried. S3 Vectors handles long-tail at near-zero cost.
4. **You're already on S3.** Data lake teams, anyone running Athena or Glue jobs over S3, get co-location and unified billing.
5. **No need for sub-50ms p99.** Most RAG isn't latency-bound at the vector tier; reranker + model dominate.

---

## When to pick something else

| Need | Pick instead |
|---|---|
| Sub-50ms p99 vector retrieval | **Redis Enterprise Cloud** |
| Co-locate vectors with relational data (joins, ACID) | **Aurora pgvector** |
| Hybrid BM25 + vector retrieval in one engine | **OpenSearch Serverless** (or self-managed) |
| GraphRAG — graph + vector co-resident | **Neptune Analytics** |
| Cross-cloud portability | **Pinecone** or self-hosted **Qdrant** |
| Need to leave AWS in < 12 months | Anything not S3 Vectors |
| Document model + vectors | **MongoDB Atlas Vector Search** |

The defining trade is **portability**. S3 Vectors is AWS-only and the storage format is proprietary. Migration off means re-embedding into another backend.

---

## Integration with Bedrock Knowledge Bases

S3 Vectors is a first-class vector store option for [Bedrock Knowledge Bases](../../ai-rag/references/aws-bedrock-knowledge-bases.md):

```text
[S3 documents] → KB ingest → chunk + embed → [S3 Vectors] → Retrieve API → cite
```

Configuration is a dropdown choice in the KB setup. No separate provisioning step (unlike Aurora or OpenSearch cluster setup).

For most "company-wiki RAG on AWS" (H2 scenario) builds, this is the lowest-friction path: documents in S3, vectors in S3, retrieval via KB. One bucket family, one billing line.

---

## Direct API access

S3 Vectors is also accessible directly via AWS SDK — you don't have to go through Bedrock KB. Use direct access when:

- You want custom chunking outside the KB-supported modes
- You're using a non-Bedrock embedding model
- You're integrating with a non-AWS agent framework that needs raw vector queries
- You're building a custom retrieval pipeline (hybrid fusion, custom rerank) where KB's flow doesn't fit

Trade-off: you give up the KB-managed citations and source attribution. Build those yourself ([`grounding-checklists.md`](../../ai-rag/references/grounding-checklists.md), [`confidence-scoring.md`](../../ai-rag/references/confidence-scoring.md)).

---

## Limits and lock-in

| Property | Note |
|---|---|
| Maximum vectors per index | 2 billion vectors per index (GA limit); trillions per bucket across many indexes — verify current AWS docs |
| Maximum dimensions | Check current AWS docs; typical embedding models (768–3072 dim) supported |
| Region availability | GA in 14 regions as of December 2025; verify your region in current AWS docs |
| Cross-region replication | Use S3 replication patterns |
| Backup | S3 versioning + lifecycle policies |
| Storage format | Proprietary AWS format; migration off = re-embed |
| Pricing changes | New product (2025); model risk for long-term commitments |

The biggest lock-in risk is the **storage format**. There is no "export vectors to Parquet and re-ingest into Pinecone" path — you must re-embed your corpus to migrate. Plan accordingly: keep source documents in S3 (you can re-embed); do not treat the vectors themselves as your source of truth.

---

## Anti-patterns

- **A-S3V-1 — Default to Aurora pgvector "because that's what we know."** S3 Vectors is ~5–10x cheaper for most workloads at comparable latency. The decision now needs justification, not the other way around.
- **A-S3V-2 — Pick S3 Vectors for sub-50ms latency workloads.** It's a warm-path tier. For tier-1 latency, use Redis or Pinecone.
- **A-S3V-3 — Treat vectors as source of truth.** Storage format is proprietary. Always keep source documents and embedding model versions tracked so you can re-embed.
- **A-S3V-4 — Skip KB and build everything direct because "we want control."** For first-pass RAG, KB + S3 Vectors is the lowest-friction stack. Drop to direct API access only when KB hits a customization wall.
- **A-S3V-5 — Use S3 Vectors for cross-cloud builds.** It's AWS-only. If portability matters in 12 months, pick a portable backend (Pinecone, Qdrant, pgvector).
- **A-S3V-6 — Plan capacity by provisioning.** It's serverless. The trap is assuming a fixed cost — usage-based billing means surprise bills if a misconfigured agent loops queries. Set query-cost alarms.

---

## Related

- [`../../ai-rag/references/aws-bedrock-knowledge-bases.md`](../../ai-rag/references/aws-bedrock-knowledge-bases.md) — Primary consumer of S3 Vectors
- [../../ai-rag/references/backend-comparison-fixtures.md](../../ai-rag/references/backend-comparison-fixtures.md) — Cross-backend test fixtures (verify S3 Vectors row is current)
- [`../../ai-rag/references/index-selection-guide.md`](../../ai-rag/references/index-selection-guide.md) — Broader index selection
- [`../../software-paas-hosting/references/aws-bedrock-agentcore.md`](../../software-paas-hosting/references/aws-bedrock-agentcore.md) — AWS agent platform (often used together)
- AWS docs: [Using S3 Vectors with Bedrock Knowledge Bases](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-vectors-bedrock-kb.html), [S3 Vectors product page (verify current)](https://aws.amazon.com/s3/features/vectors/)
