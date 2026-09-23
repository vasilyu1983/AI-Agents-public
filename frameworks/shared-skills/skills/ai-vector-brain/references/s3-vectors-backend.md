# S3 Vectors — Vector Backend Choice

Amazon S3 Vectors is a cost-optimized vector storage service that reached GA in 14 AWS regions in December 2025. AWS documents sub-second query performance for infrequent queries and roughly 100 ms for frequently queried indexes. AWS also advertises up to 90% lower cost than specialized vector databases; treat that as a vendor claim and validate it with the target corpus, query rate, filters, and retention profile.

Treat it as the first cost-oriented candidate for AWS-native retrieval, then compare it with Aurora pgvector or OpenSearch when relational co-location, hybrid search, ranking control, or tighter latency targets matter.

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

The mental model: S3 Vectors brings a managed vector index and query API into S3's storage boundary. Its economic and latency fit still depends on the corpus, query pattern, filters, and alternatives already operated by the team.

---

## Cost shape

S3 Vectors charges for stored vectors and API activity rather than provisioned search capacity. AWS advertises **up to 90%** lower cost than specialized vector databases, but the supplied sources do not support fixed competitor multiples. Build a dated workload estimate with vector count and dimensions, retained metadata, ingest and update volume, query rate, filter pattern, replication, data processing, and any hot tier. Compare the complete cost with the team's actual Aurora, OpenSearch, or external-service configuration.

**Implication for the vector-backend decision in `ai-vector-brain`:** treat S3 Vectors as a cost-oriented candidate. Choose from measured alternatives based on relational co-location, hybrid retrieval, ranking control, query pattern, operational fit, portability, and latency and cost budgets.

---

## Latency profile

| Query class | Latency |
|---|---|
| **Infrequent query** | Sub-second, per AWS documentation |
| **Frequently queried index** | Approximately 100 ms, per AWS documentation |
| **Filtered query** | Benchmark with the target predicate and selectivity |

These are service-level descriptions, not a workload-specific percentile guarantee. Measure the end-to-end retrieval distribution under the intended query rate and filters. If the measured tail misses the retrieval budget, compare a hot index or tiered design.

---

## When S3 Vectors wins

1. **AWS-native RAG.** You are on AWS and want managed vector storage with Bedrock KB or self-managed retrieval.
2. **Cost-sensitive scale.** Large corpora where a workload calculation supports the storage-plus-API cost shape.
3. **Infrequently queried workloads.** Long-tail corpora where usage-priced querying and documented sub-second access meet the product budget.
4. **You're already on S3.** Data lake teams, anyone running Athena or Glue jobs over S3, get co-location and unified billing.
5. **Measured latency fits.** The target query and filter distribution clears the retrieval latency budget.

---

## When to pick something else

| Need | Pick instead |
|---|---|
| Tighter tail-latency target than S3 Vectors meets in testing | Benchmark a hot in-memory or provisioned vector index |
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

- **A-S3V-1 — Choose from familiarity or vendor headline alone.** Compare S3 Vectors with the actual Aurora, OpenSearch, or external-service configuration on the target corpus and query distribution.
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
