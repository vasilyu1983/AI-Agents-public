# Cost Calculation

## Table of Contents

- [TCO Components](#tco-components)
- [Sizing Inputs You Need First](#sizing-inputs-you-need-first)
- [Formula 1 Hot Index RAM Footprint pgvector Qdrant Weaviate Milvus OpenSearch k-NN Redis](#formula-1--hot-index-ram-footprint-pgvector-qdrant-weaviate-milvus-opensearch-k-nn-redis)
- [Formula 2 Object-Storage-Backed S3 Vectors Turbopuffer Pinecone Serverless](#formula-2--object-storage-backed-s3-vectors-turbopuffer-pinecone-serverless)

Concrete formulas, worked examples, and a sizing checklist for vector-brain cost estimation. Use this before locking a backend choice from [backend-selection.md](backend-selection.md).

**Health warning**: every unit price below is illustrative and drifts. Verify against current vendor pricing pages (see [data/sources.json](../data/sources.json)) before quoting numbers to a stakeholder. Pricing in this file uses 2026 ballpark figures.

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
- **rerank N**: candidates sent to cross-encoder (5–10× K typical)
- **avg tokens per chunk**: drives embedding cost
- **churn**: chunks added/changed per day → re-embeddings
- **LLM grounding tokens per answer**: drives generation cost (separate from retrieval)

## Formula 1 — Hot Index RAM Footprint (pgvector, Qdrant, Weaviate, Milvus, OpenSearch k-NN, Redis)

The dominant cost driver for in-memory ANN.

```text
raw_vectors_bytes  = N × d × bytes_per_element
hnsw_overhead      = raw_vectors_bytes × 1.5     # graph links, ~50% on top
quantization_save  = 0.25–1.0                    # 0.25 for int8, 0.5 for halfvec, 1.0 for none
index_ram_bytes    = (raw_vectors_bytes × 1.5) × quantization_save
total_ram_bytes    = index_ram_bytes × replicas
```

**Worked example — 10M vectors, d=1536, halfvec, HA replicas=2:**

```text
raw          = 10_000_000 × 1536 × 4    = 61.4 GB (float32)
halfvec      = 61.4 GB × 0.5            = 30.7 GB
hnsw_index   = 30.7 GB × 1.5            = 46.1 GB
ha           = 46.1 GB × 2              = 92.2 GB RAM
```

Map to instance class: ~`r6i.4xlarge` (128 GB) × 2 nodes ≈ $1.5–2k/month on AWS on-demand. Reserved cuts ~40%.

**Worked example — 100M vectors, d=1024, int8 quantized:**

```text
raw          = 100_000_000 × 1024 × 4   = 410 GB
int8         = 410 GB × 0.25            = 102 GB
hnsw_index   = 102 GB × 1.5             = 154 GB
ha=2         = 308 GB RAM
```

This is where pgvector on a single node stops being cheap. Time to consider pgvectorscale (DiskANN), Milvus, or object-backed alternatives.

## Formula 2 — Object-Storage-Backed (S3 Vectors, Turbopuffer, Pinecone Serverless)

Storage cheap, queries metered.

```text
storage_bytes   = N × d × bytes_per_element × 1.2     # ~20% metadata overhead
storage_cost    = storage_bytes × $/GB-month
query_cost      = QPS × seconds_per_month × $/query
write_cost      = churn_per_day × 30 × $/write
egress          = bytes_returned × $/GB-egress         # often the surprise
total_monthly   = storage + query + write + egress
```

**Worked example — 100M vectors, d=1024, S3 Vectors at illustrative $0.06/GB-month storage, $0.0004/1k queries, 5 QPS sustained:**

```text
storage      = 100M × 1024 × 4 × 1.2 = 492 GB
storage_$    = 492 × $0.06          = $29.5/month
queries/mo   = 5 × 86400 × 30        = ~13M queries
query_$      = 13M × $0.0004/1k     = $5.2/month
total        ≈ $35/month  (excluding embedding generation)
```

Compare to ~$1.5–2k/month for the equivalent hot index above. **At low–medium QPS over a large corpus, this is the 10–100× cost gap.** Crossover happens around sustained 100+ QPS where per-query costs catch up to fixed RAM cost.

**Compare crossover (rule of thumb):**

```text
fixed_ram_cost_per_month       (hot index instances)
─────────────────────────────  =  break-even QPS for object-backed
query_$ × seconds_per_month
```

If you're below break-even QPS, object-backed wins. Above, hot index wins.

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

Prompt caching (Anthropic, OpenAI) cuts repeated system-prompt input cost by ~90%. Always enable it for grounded RAG. See [contextual-retrieval.md](contextual-retrieval.md).

## Worked End-to-End: Three Scenarios at 10M Vectors, 5 QPS

Illustrative monthly run rate, AWS-equivalent on-demand. **Numbers will drift; treat as ratios, not commitments.**

| Bucket | pgvector (hot, HA) | S3 Vectors (cold) | Bedrock KB on S3 Vectors |
|---|---|---|---|
| Storage / RAM | ~$1,500 (r6i.4xlarge × 2) | ~$30 | ~$30 (passthrough) |
| Query serving | included in instance | ~$5 | ~$5 + KB query fee |
| Embedding (3-small, initial) | ~$100 one-time | same | bundled per chunk |
| Embedding (churn 1%/day) | ~$30/mo | same | bundled |
| Reranker (Cohere, optional) | ~$200/mo | same | not exposed |
| LLM grounding (Claude/GPT) | ~$300/mo | same | bundled per query |
| **Vector-infra subtotal** | **~$1,500** | **~$35** | **~$50–80** |
| **All-in subtotal** | **~$2,130** | **~$565** | **varies by KB pricing** |

The headline gap (~$1,500 vs $35 on vector infra) shrinks once embeddings + reranker + LLM are added, but pgvector hot still costs ~4× more all-in at this scale and access pattern.

**Crossover signal**: if QPS triples (15 QPS sustained), pgvector cost stays flat (~$1,500) while S3 Vectors query line triples (~$15). Hot index wins by absolute amount only above ~200 QPS sustained at this corpus size.

## Sizing Checklist Before You Quote a Number

- [ ] Vector count today + 12-month projection
- [ ] Embedding model + dimension + bytes per element (with/without quantization)
- [ ] Replicas for HA
- [ ] QPS sustained, QPS peak
- [ ] Rerank N per query and rerank model
- [ ] Churn per day (re-embedding cost)
- [ ] LLM grounding budget (separate but always asked together)
- [ ] Egress/bandwidth assumptions
- [ ] Reserved vs on-demand for hot indexes (~30–50% savings reserved)
- [ ] Region multiplier (Frankfurt/London/Tokyo can be ~20% higher than us-east-1)
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
