# Cost Calculation

## Table of Contents

- [TCO Components](#tco-components)
- [Sizing Inputs You Need First](#sizing-inputs-you-need-first)
- [Formula 1 Hot Index RAM Footprint pgvector Qdrant Weaviate Milvus OpenSearch k-NN Redis](#formula-1--hot-index-ram-footprint-pgvector-qdrant-weaviate-milvus-opensearch-k-nn-redis)
- [Formula 2 Object-Storage-Backed S3 Vectors Turbopuffer Pinecone Serverless](#formula-2--object-storage-backed-s3-vectors-turbopuffer-pinecone-serverless)

Concrete formulas, worked examples, and a sizing checklist for vector-brain cost estimation. Use this before locking a backend choice from [backend-selection.md](backend-selection.md).

**Health warning**: every unit price below is illustrative and drifts. Verify against current vendor pricing pages (see [data/sources.json](../data/sources.json)) before quoting numbers to a stakeholder. Treat every price here as a placeholder input to the formula, not a current rate.

## TCO Components

Vector-brain cost is more than "vector storage". A complete estimate has five buckets:

1. **Embedding generation (one-time + churn)** — provider API calls or self-hosted GPU time
2. **Vector storage** — RAM (hot index) or object storage (cold index)
3. **Query serving** — per-query reads, per-node-hour, or RAM-amortized
4. **Auxiliary services** — reranker API calls, LLM grounding tokens, observability
5. **Ops overhead** — engineer hours, backups, monitoring, cluster management

A 100M-vector brain often has embeddings as the **second-largest line item** behind serving infra. Don't forget the embeddings.

## Sizing Inputs You Need First

Before any formula gives a meaningful number, collect:

- **N**: vector count (today, 12 months, 36 months)
- **d**: embedding dimension (e.g. 1536 for `text-embedding-3-small`, 1024 for `voyage-4`, 3072 for `text-embedding-3-large`; Amazon Nova 2 Multimodal Embeddings is Matryoshka-tunable to 3072/1024/384/256)
- **bytes per element**: 4 (float32), 2 (float16/halfvec), 1 (int8 quantized), 0.125 (binary)
- **replicas**: 1 for single-node, 2–3 for HA
- **QPS sustained / peak**: queries per second across the cluster
- **top-K**: results per query (affects rerank cost)
- **rerank N**: candidates sent to the cross-encoder; size it by the rule in [ai-rag ranking-pipeline-guide.md](../../ai-rag/references/ranking-pipeline-guide.md#5-reranking-stage)
- **avg tokens per chunk**: drives embedding cost
- **churn**: chunks added/changed per day → re-embeddings
- **LLM grounding tokens per answer**: drives generation cost (separate from retrieval)

## Formula 1 — Hot Index RAM Footprint (pgvector, Qdrant, Weaviate, Milvus, OpenSearch k-NN, Redis)

The dominant cost driver for in-memory ANN.

Size the index with the single HNSW formula in
[production-runbook.md](production-runbook.md#hnsw-memory-sizing); this file
does not keep its own copy. For RAM budgeting:

```text
index_ram_bytes = N × bytes_per_vector      # from production-runbook.md#hnsw-memory-sizing
total_ram_bytes = (index_ram_bytes + hot heap/working set) × replicas
```

Do not scale raw vector size by a quantization ratio: the graph links do not
shrink when the vectors do, so that shortcut understates quantized indexes
(badly for binary).

**Worked example — 10M vectors, d=1536, halfvec, M=16, 6-byte ids, HA replicas=2:**

```text
bytes_per_vector = k × (1536 × 2 + 2 × 16 × 6) = k × 3,264 B
index            = 10M × k × 3,264 B        = k × 32.6 GB per replica
ha=2             = k × 65.3 GB RAM           (k ≈ 1.1–1.5 → ~72–98 GB)
```

Map to an instance class: pick the smallest memory-optimized class whose RAM covers the per-replica index plus OS, `shared_buffers` and working-set headroom (here a 128 GB class per node, 2 nodes). Price it from the provider's rate card for your region, on-demand and reserved or committed, because the discount varies by term and provider.

**Worked example — 100M vectors, d=1024, int8 quantized, M=16, 6-byte ids:**

```text
bytes_per_vector = k × (1024 × 1 + 192)     = k × 1,216 B
index            = 100M × k × 1,216 B       = k × 122 GB per replica
ha=2             = k × 243 GB RAM            (k ≈ 1.1–1.5 → ~270–365 GB)
```

Then measure `pg_relation_size` on a sample build, as the runbook shows.

This is where pgvector on a single node stops being cheap. Time to consider pgvectorscale (DiskANN), Milvus, or object-backed alternatives.

## Formula 2 — Object-Storage-Backed (S3 Vectors, Turbopuffer, Pinecone Serverless)

Storage cheap, queries metered.

```text
storage_bytes   = N × d × bytes_per_element × 1.2     # ~20% metadata overhead
storage_cost    = storage_bytes × $/GB-month
request_cost    = queries_per_month × $/million-queries
processed_cost  = queries_per_month × avg_vector_bytes × $/TB-processed     # tiered by index size
write_cost      = churn_per_day × 30 × $/write
egress          = bytes_returned × $/GB-egress         # often the surprise
total_monthly   = storage + request_cost + processed_cost + write + egress
```

S3 Vectors query cost has **two components**, not one flat per-query rate: a
per-query request fee and a data-processed fee based on "sum of vectors per
index × average vector size," tiered by index size. Look up both on the AWS
S3 Vectors pricing page for your region before computing; the tiers and rates
change. Both components matter: the data-processed fee dominates at large
index sizes.

**Worked example — 100M vectors, d=1024 (4 KB/vector), S3 Vectors, 5 QPS sustained.** The unit prices below are illustrative inputs from an earlier pricing snapshot, kept to show the shape of the result; substitute the rates you looked up:

```text
storage      = 100M × 1024 × 4 × 1.2  = 492 GB
storage_$    = 492 × $0.06            = $29.5/month
queries/mo   = 5 × 2,592,000 s         = ~12.96M queries
request_$    = 12.96M × $2.50/1M      = $32.40/month
processed_$  ≈ tiered data-processed fee over 12.96M queries × 4KB avg vector,
               100M-vector index      ≈ $2,700–2,950/month  (dominant term)
query_total  ≈ $2,730–2,980/month
total        ≈ $2,760–3,010/month  (excluding embedding generation)
```

This is **not** a flat $0.0004/1k-queries rate and **not** ~$35/month total —
the data-processed component, driven by index size, is the dominant cost and
was previously omitted. The figures are re-derived from the request fee plus
the tiered data-processed fee; re-check the tiers on the AWS pricing page
before reusing them. Compare to ~$1.5–2k/month for the equivalent hot pgvector index
above — at this scale and QPS, S3 Vectors is **not** the 10–100× cheaper
option the earlier version of this table implied; it can be comparable to or
more expensive than a hot index once the corpus is large, even at modest QPS.
Recompute the crossover for your own N, d, and QPS rather than reusing a rule
of thumb — the crossover point depends heavily on index size, not just QPS.

**Compare crossover (rule of thumb):**

```text
fixed_ram_cost_per_month       (hot index instances)
─────────────────────────────  =  break-even QPS for object-backed
query_$ × seconds_per_month
```

If you're below break-even QPS, object-backed wins. Above, hot index wins.
Because `query_$` for S3 Vectors is now known to include a data-processed
component that scales with index size (see above), this formula's
`query_$` term must use the full two-part query cost at your own N and d —
plugging in only the request fee (as the earlier version of this doc did)
understates the per-query cost by roughly 30× at 10M vectors and 90× at 100M
vectors (d=1024), so it overstates the break-even QPS by the same factor.

## Formula 3 — Managed Cluster (Vertex, Azure AI Search, Pinecone Pod, Milvus Cloud)

```text
nodes_required   = ceil(N / vectors_per_node) × replicas
node_hours       = nodes_required × 730            # hours per month
cost_per_node    = $/hour × tier_multiplier
total_monthly    = node_hours × cost_per_node + storage + egress
```

Cost is **predictable** but **expensive at low utilization** — you pay full node-hours even at 0 QPS. Best for steady production load.

## Formula 4 — Embedding Generation Cost

Often forgotten until the bill arrives.

```text
total_tokens     = N × avg_tokens_per_chunk
initial_cost     = total_tokens × $/1M-tokens
churn_cost_mo    = (churn_per_day × 30) × avg_tokens × $/1M-tokens
total            = initial + churn (× lifetime)
```

**Worked example — 10M chunks × 500 tokens avg, `text-embedding-3-small` at $0.02/1M tokens:**

```text
tokens       = 10M × 500             = 5 billion
initial_$    = 5_000 × $0.02         = $100  (one-time)
churn 1%/day = 0.01 × 10M × 500 × 30 = 1.5B tokens/mo
churn_$/mo   = 1500 × $0.02          = $30/month
```

With `text-embedding-3-large` (~$0.13/1M), the same load is ~$650 initial + ~$195/month. Choose the embedder against eval lift, not vibes — 3-large is rarely 6× better than 3-small on real corpora.

## Formula 5 — Reranker Cost (Cohere Rerank, Voyage Rerank-2.5, cross-encoder API)

Often the **hidden line item** in production RAG.

```text
rerank_calls_per_query  = 1  (one batch of N candidates)
rerank_units_per_call   = N × tokens_per_candidate / 1000   # vendor-specific
rerank_$_per_query      = rerank_units × $/unit
monthly_rerank_$        = QPS × 86400 × 30 × rerank_$_per_query
```

**Worked example — 50 QPS, N=50 candidates, ~400 tokens each, Cohere Rerank illustrative $2/1k searches:**

```text
queries/mo   = 50 × 86400 × 30       = ~130M queries
rerank_$     = 130M × $2/1k          = $260k/month
```

At the lower 5 QPS example used in the end-to-end table below: `queries/mo ≈
12.96M`, `rerank_$ ≈ 12.96M × $2/1k ≈ $25,900/month` — not the ~$200/mo
figure an earlier version of the table below used, which was off by roughly
two orders of magnitude. Always
re-derive the rerank cost from this formula at your own QPS rather than
copying a table row.

That number is real. **Reranker cost can dwarf storage cost at scale.** Mitigations:

- rerank only top-50 from hybrid retrieval, not top-500
- skip rerank for high-confidence single-hit queries
- self-host a cross-encoder (bge-reranker-v2-m3, ~$0.5–1k/month GPU) above ~5–10 QPS sustained
- cache rerank scores against `(query_hash, candidate_id, model_id)` keyed by `corpus_version`

## Formula 6 — LLM Grounding Cost (the actual chat answer)

Not a vector-brain cost strictly, but always bundled into the same budget conversation.

```text
input_tokens_per_answer  = top_K × avg_chunk_tokens + system_prompt + question
output_tokens_per_answer = expected_answer_length
cost_per_answer          = input × $/1M-input + output × $/1M-output
monthly_$                = answers_per_month × cost_per_answer
```

Prompt caching cuts the cost of a repeated system-prompt prefix to the
cache-read rate. The cache-read multiplier is model- and vendor-dependent:
look it up per model rather than assuming one discount for every model. Always enable it for grounded RAG.
See [contextual-retrieval.md](contextual-retrieval.md).

**Worked example — 5 QPS, top-K=2k input tokens + 200 output tokens per
answer, a representative small/fast model at roughly $1/$5 per million
input/output tokens:**

```text
answers/mo   = 5 × 2,592,000          = ~12.96M answers
input_$      = 12.96M × 2,000 × $1/1M = $25,920/month
output_$     = 12.96M × 200 × $5/1M   = $12,960/month
total        ≈ $38,900/month
```

This is orders of magnitude above a flat "~$300/mo" estimate that an earlier
version of the table below used for the same 5 QPS workload — LLM grounding
cost scales with answer volume × tokens, not a fixed monthly figure. Always
re-derive per-answer cost from your chosen model's current per-token price
(see [ai-api-cost-guide.md#pricing-overview](../../ops-cost-optimization/references/ai-api-cost-guide.md#pricing-overview) for where the dated rates live) rather than reusing a table row.

## Worked End-to-End: Three Scenarios at 10M Vectors, 5 QPS

Illustrative monthly run rate, AWS-equivalent on-demand, d=1024.
**Numbers will drift; treat as ratios, not commitments; re-derive from the
formulas above rather than copying this table.**

| Bucket | pgvector (hot, HA) | S3 Vectors (cold) | Bedrock KB on S3 Vectors |
|---|---|---|---|
| Storage / RAM | ~$1,500 (r6i.4xlarge × 2) | ~$3 (10M-vector storage; do not reuse the 100M figure) | ~$3 (passthrough) |
| Query serving (request + data-processed) | included in instance | ~$1,040–1,110 (tiered data-processed fee dominates; see Formula 2) | ~$1,040–1,110 + KB query fee |
| Embedding (3-small, initial) | ~$100 one-time | same | bundled per chunk |
| Embedding (churn 1%/day) | ~$30/mo | same | bundled |
| Reranker (Cohere, optional, 5 QPS) | ~$25,900/mo | same | not exposed |
| LLM grounding (per Formula 6, 5 QPS) | ~$38,900/mo | same | bundled per query |
| **Vector-infra subtotal** | **~$1,500** | **~$1,045–1,115** | **~$1,045–1,115 + KB fee** |
| **All-in monthly (excl. one-time embedding)** | **~$66,300** | **~$65,900** | **varies by KB pricing** |

At this scale (10M vectors, 5 QPS), the vector-infra-only gap between
pgvector hot and S3 Vectors is roughly 1.3–1.4×, not the 10–100× an earlier
version of this table claimed — the gap narrows sharply as index size grows
because S3 Vectors' data-processed fee scales with index size. Once reranker
and LLM grounding costs are added, both paths land in the same order of
magnitude because those two buckets dominate the all-in total at 5 QPS
regardless of vector backend. Always recompute reranker and LLM grounding
cost from Formulas 5 and 6 at your own QPS before quoting a total — those
two buckets, not the vector backend choice, usually decide the bill.

**Crossover signal**: because the S3 Vectors data-processed fee scales with
both QPS and index size, there is no single "QPS threshold" that holds across
corpus sizes. Recompute the crossover ratio (Formula 2's break-even
comparison) for your own N, d, and QPS rather than reusing a fixed number —
an earlier version of this section claimed a ~100–200 QPS or ~1,450 QPS
crossover; both used the incomplete (request-fee-only) query cost and should
not be reused.

## Sizing Checklist Before You Quote a Number

- [ ] Vector count today + 12-month projection
- [ ] Embedding model + dimension + bytes per element (with/without quantization)
- [ ] Replicas for HA
- [ ] QPS sustained, QPS peak
- [ ] Rerank N per query and rerank model
- [ ] Churn per day (re-embedding cost)
- [ ] LLM grounding budget (separate but always asked together)
- [ ] Egress/bandwidth assumptions
- [ ] Reserved or committed vs on-demand for hot indexes (price both from the rate card)
- [ ] Region multiplier (price the target region; rates differ by region)
- [ ] Observability and backup costs (often ~5–15% on top)

## Common Cost Mistakes

- Quoting "vector DB cost" without embedding generation — embeddings can be 30–50% of TCO for high-churn corpora
- Ignoring reranker calls — at 50+ QPS, reranker often beats storage cost
- Sizing for peak QPS on a hot index when sustained is 1/10th — over-provision waste
- Forgetting halfvec / quantization — halves or quarters RAM with near-zero recall loss after tuning
- Ignoring embedder-native quantization support in FinOps sizing — quantization-aware embedders (e.g. voyage-3.5 int8 2048-dim) cut vector-DB storage ~83% vs OpenAI-v3-large float32 3072-dim at higher retrieval quality (vendor benchmark); factor the embedder's quantization support and output dimension into storage and RAM estimates before comparing backends
- Comparing managed cluster cost at 1 QPS — pay-per-node is predictable but punishing at low utilization
- Treating egress as zero — multi-region or cross-cloud egress is a real line item
- Ignoring backup + WAL storage on pgvector — can be ~20% on top of instance cost
- Mixing on-demand pricing with reserved pricing across backends in the same comparison

## Migration Cost (One-Time)

Re-embedding for a model change scales linearly:

```text
migration_$ = N × avg_tokens × $/1M-tokens × (1 + qa_overhead)
```

Where `qa_overhead` is ~10–20% for parallel A/B running before cutover. Plan dual-storage for ~2–4 weeks during migration.

## Current-Source Rule

Pricing pages change. Before turning this file's ratios into a budget, re-verify:

- AWS S3 Vectors pricing page
- Bedrock Knowledge Bases pricing page
- Pinecone Serverless pricing page
- Vertex AI Vector Search pricing
- Azure AI Search tier pricing
- Embedding provider pricing (OpenAI, Voyage, Cohere, AWS Bedrock embedding models)
- Reranker provider pricing (Cohere, Voyage, Jina)
- LLM grounding provider pricing

See [backend-selection.md](backend-selection.md) for which backends fit which workload before optimizing for cost.
