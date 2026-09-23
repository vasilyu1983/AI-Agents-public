<!-- Focused reference for vector search api and sizing. -->

# Vector Search API and Sizing

## Contents

- [Vector Search API Pattern](#vector-search-api-pattern)
- [Ranking Signal Mix](#ranking-signal-mix)
- [Index-Time vs Query-Time Signals Boosting](#index-time-vs-query-time-signals-boosting)
- [Vector Memory Sizing](#vector-memory-sizing-worked-example)

## Vector Search API Pattern

Use this pattern when semantic search is a product feature, not just an LLM
context retriever.

**Request contract**:

- `query`: required non-empty string, with length and character-class limits
- `limit`: bounded integer, default 10, hard max 50
- `offset` or cursor: optional pagination, only if the engine supports stable
  ordering
- `filters`: allowlisted fields only; never pass arbitrary filter JSON through
  to the search engine

**Response contract**:

- stable result ID and display fields
- relevance score or rank, clearly marked as diagnostic when the score is not
  user-meaningful
- matched source metadata needed for display
- applied query preprocessing version

**Operational rules**:

- Keep the endpoint stateless and idempotent even if implemented as `POST`.
- Validate and sanitize input before embedding or query construction.
- Rate-limit by authenticated actor or API key; IP-only limits are weak for
  logged-in products.
- Add structured errors for invalid input, unavailable embedder, search timeout,
  and backend failure.
- Log raw query, cleaned query, retrieval mode, top result IDs, latency, and
  result count.
- Start with exact or small-corpus search to debug embeddings, then move to an
  index once quality is proven.

### Ranking Signal Mix

For product search, semantic similarity is usually one leg of ranking, not the
whole ranker. Typical final scoring candidates:

- vector or hybrid relevance
- recency decay
- popularity or engagement
- editorial boost or business rule
- personalization, only when user consent and isolation rules are clear

Do not hand-pick weights from intuition. Calibrate weights against judged
queries and analytics slices. If scores come from different systems and cannot
be normalized safely, prefer rank-based fusion such as RRF before applying
business boosts.

### Index-Time vs Query-Time Signals Boosting

Once popularity or engagement signals are part of the ranker, there is a second
decision: where the boost is applied. Grainger et al. frame it as scale versus
flexibility.

**Query-time boosting** keeps signals in a separate sidecar collection. Each incoming
query first looks up its boosts there, then the boosts are injected into the main
query. Because the collections stay separate, signals for one query can be updated by
touching one document, boosting can be switched off by simply skipping the lookup, and
a different boosting algorithm can be swapped in at any time. That flexibility — and
the ease of incorporating real-time signals and running ranking experiments — is the
reason it is the more common implementation.

Its costs are structural, not incidental:

- Every search becomes two searches back-to-back; the main query waits on the lookup.
- Only a top-N slice of boosted documents can be injected before query cost becomes
  unreasonable, so relevance is traded against scalability. A query with hundreds of
  documents carrying signals will boost only the handful that fit.
- Paging degrades. Covering page 2 means loading more boosts than page 1 did, page 10
  more still, so deep paging gets progressively slower and can time out. Worse, boost
  is only one scoring factor: as the boost set grows between pages, documents can jump
  onto a page the user already passed or reappear on a later one, producing skipped
  and duplicated results.

**Index-time boosting** inverts the problem — instead of boosting popular documents
for a query at query time, it writes the popular queries and their boost values into a
field on each document at indexing time, and the query simply searches that field. The
same signals aggregation feeds both; only the final application step differs. This
removes the second query, keeps query cost flat as the number of boosted documents
grows, and fixes paging outright, because every matching document carries its boost
rather than just the top-N that fit in a query string.

Its costs land on the indexing side:

- Adding or removing a keyword from the model requires reindexing every document
  associated with that keyword. Incremental per-keyword updates can therefore mean
  continuous reindexing; batch regeneration can mean reindexing the whole corpus.
- Changing the boosting function needs a migration, not an edit. Reweighting click
  versus purchase signals means writing a second boost field, reindexing into it, then
  cutting the query over — otherwise scores fluctuate while the corpus is half-updated.
- Under sustained indexing pressure, separate the servers that index from the servers
  that serve queries, or indexing CPU and memory will degrade query latency. Several
  engines expose a mechanism for this (replica types, follower indexes); confirm the
  specific mechanism and its current behaviour in your engine's own docs.

**Choosing**: take query-time boosting when the ranking function is still moving —
active experimentation, real-time signals, boosts that need to be toggled per request.
Take index-time boosting when the model has stabilised and scale is the constraint:
deep paging matters, per-query boost sets are large, or query latency is the budget
under pressure. The book's own summary of the tradeoff is that query-time is more
flexible while index-time is more scalable and gives more consistent relevance ranking.

For the full learning-to-rank pipeline that sits above these signal decisions — feature
logging, judgment lists, model training, and reranking — see
[ai-rag](../../ai-rag/SKILL.md), whose `references/learning-to-rank-pipeline.md`
covers it end to end.

### Vector Memory Sizing (Worked Example)

Estimate before choosing a vector index type — memory, not disk, is usually the
binding constraint for in-memory ANN indexes (HNSW).

**Formula**: `raw_bytes = num_vectors × dims × bytes_per_value`. Add HNSW graph
overhead on top (graph edges + metadata); treat 20-50% of raw size as a
starting planning range and verify the actual multiplier against the specific
engine's current documentation before sizing hardware.

**Worked derivation** — 1,000,000 documents, 768-dimension embeddings (a common
mid-size embedding model output), three storage precisions:

| Precision | Bytes/dim | Raw size = 1,000,000 × 768 × bytes/dim | Raw size (GiB) |
|---|---|---|---|
| float32 (full precision) | 4 | 3,072,000,000 bytes | ≈ 2.86 GiB |
| halfvec / float16 | 2 | 1,536,000,000 bytes | ≈ 1.43 GiB |
| binary quantized (1 bit) | 0.125 | 96,000,000 bytes | ≈ 0.09 GiB |

Adding a 30% HNSW graph overhead to the float32 case: `2.86 GiB × 1.3 ≈ 3.72 GiB`
of working memory for one million 768-dim vectors — before the rest of the
document payload (text, metadata) is counted.

**How to use this**: re-run the same formula with your own `num_vectors` and
`dims` — never scale a neighboring number instead of recomputing from your
corpus size and embedding dimension. Binary and scalar quantization trade
recall for memory; validate the recall drop against your judged-query set
before committing to a lower precision in production. Confirm current
quantization support (halfvec, binary, product quantization) in the specific
engine's docs — pgvector, Elasticsearch, OpenSearch, and Qdrant each expose
different quantization options and defaults that change across releases.

---

Back to [software-search/SKILL.md](../SKILL.md).
