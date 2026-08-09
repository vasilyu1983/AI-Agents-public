# MongoDB Atlas as Context Layer for AI Agents

Use when the agent needs durable memory, RAG over private data, and tool-grade retrieval — and you want to avoid running a separate vector store.

## Collection Topology

| Collection | Purpose | Key fields |
|---|---|---|
| `documents` | Source-of-truth content (chunks of docs, tickets, transcripts) | `text`, `embedding`, `source_id`, `tenant_id`, `content_hash`, `created_at`, `metadata` |
| `agent_memory` | Long-term agent memory (facts, preferences, derived summaries) | `agent_id`, `user_id`, `memory_type`, `text`, `embedding`, `importance`, `last_used_at`, `ttl_at` |
| `agent_traces` | Append-only conversation/tool-call history | TTL-indexed for short-term, archived to time-series for analytics |

Co-locate the `embedding` field on the source document. Do **not** put embeddings in a sidecar collection — it forces `$lookup` on every retrieval.

## Chunk and Embed

- Chunk by semantic boundary (heading, paragraph, ~500–1000 tokens) with 10–15% overlap.
- Store `{ text, embedding, source_id, tenant_id, content_hash, created_at, metadata }` per chunk.
- Use `content_hash` to dedupe re-ingested chunks idempotently.
- Pin the embedding model name and dimension in a config document; mixing dims in one index breaks `$vectorSearch`.

## Atlas Vector Search Index Definition

```json
{
  "fields": [
    { "type": "vector", "path": "embedding", "numDimensions": 1024, "similarity": "cosine" },
    { "type": "filter", "path": "tenant_id" },
    { "type": "filter", "path": "source_type" }
  ]
}
```

- `similarity`: `cosine` for normalized text embeddings, `dotProduct` if you control normalization, `euclidean` rarely.
- Always declare filter fields you'll use — pre-filtering at ANN time keeps tenant isolation correct and recall high.

## Retrieval Pattern

- Use `$vectorSearch` with a `filter` clause for tenant and source scoping (mandatory for multi-tenant agents).
- For hybrid retrieval, run `$vectorSearch` and `$search` (BM25) and combine with `$rankFusion` (8.1+) or RRF in app code.
- `numCandidates ≈ 10–20× limit`; tune by measuring recall on a labeled eval set, not by guessing.

## Agent Memory Pattern

- **Write path**: extract candidate facts → embed → upsert with `content_hash` to dedupe → score `importance`.
- **Read path**: `$vectorSearch` filtered by `agent_id`/`user_id`, then re-rank by `importance × recency_decay(last_used_at)`.
- TTL index on `ttl_at` for forgetting; bump `last_used_at` on retrieval — batch updates in hot loops, do not update on every read.

## Operational Checklist

- [ ] Every retrieval query includes the tenant filter — add a query helper that enforces this, not a convention. Test with a deliberately mis-scoped fixture in CI.
- [ ] Sensitive fields use Queryable Encryption (GA in 8.x); embeddings are reversible, treat them as PII.
- [ ] Vector index RAM budget estimated: `numDimensions × 4 bytes × doc_count × 1.5` (float32 vectors, ~1.5x multiplier for HNSW graph overhead — a rough planning number, not a guarantee; measure against an actual index build before sizing production hardware). Quantize (`scalar` or `binary`) when corpus > 10M chunks.
- [ ] Re-embedding plan exists: changing the embedding model requires re-embedding everything. Version the `embedding_model` field per doc; run a dual-write window during migration (expand-contract).
- [ ] Labeled eval set of 50–200 queries built; recall@k and MRR measured before tuning index params or adding hybrid search.

## When to Leave Atlas for a Dedicated Vector DB

Only when you exceed ~100M vectors with strict p99 < 50 ms requirements, or you need GPU-accelerated indexes. Below that, the operational simplicity of one engine wins.
