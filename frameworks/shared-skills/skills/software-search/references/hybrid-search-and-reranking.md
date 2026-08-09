# Hybrid Search and Reranking Pipeline

Production retrieval combines lexical and dense-vector search, fuses the ranked
lists, and applies a cross-encoder reranker as a final stage. Each stage earns
its cost only when the previous stage's recall ceiling is already reached.

**Freshness:** Do not assume current engine versions or benchmark figures from
this file. Resolve version-specific features and quantitative claims via the
canonical docs listed in `data/sources.json` at use-time.

## Table of Contents

- [1. Stage Map](#1-stage-map)
- [2. Lexical Stage (BM25)](#2-lexical-stage-bm25)
- [3. Dense Vector Stage (ANN)](#3-dense-vector-stage-ann)
- [4. Fusion Stage (Reciprocal Rank Fusion)](#4-fusion-stage-reciprocal-rank-fusion)
- [5. Cross-Encoder Reranking Stage](#5-cross-encoder-reranking-stage)
- [6. In-Postgres Hybrid Option (pgvector + BM25)](#6-in-postgres-hybrid-option-pgvector--bm25)
- [7. Engine Capability Classes](#7-engine-capability-classes)
- [8. When Each Stage Earns Its Cost](#8-when-each-stage-earns-its-cost)
- [9. Checklist Before Shipping a Hybrid Pipeline](#9-checklist-before-shipping-a-hybrid-pipeline)
- [10. Freshness](#10-freshness)

---

## 1. Stage Map

```
Query
  → [Lexical retrieval — BM25]        top-K lexical candidates
  → [Dense vector retrieval — ANN]    top-K semantic candidates
  → [Fusion — RRF or weighted sum]    merged ranked list
  → [Cross-encoder reranking]         re-scored top-N
  → Final results
```

Apply stages left to right. Stop adding stages when quality goals are met and
latency budget is not exceeded.

---

## 2. Lexical Stage (BM25)

BM25 is the production-default relevance function in Elasticsearch, OpenSearch,
Typesense, and Meilisearch. It handles exact and near-exact keyword matches,
domain terms, SKUs, proper nouns, and negation well.

**When lexical alone is sufficient:**
- Corpus is fully enumerable with known vocabulary (catalog, part numbers)
- Users reliably use exact product or entity names
- Query logs show low query-reformulation rate

**BM25 weaknesses BM25 cannot self-heal:**
- Synonym / paraphrase queries (user writes "cheap" when documents say "affordable")
- Semantic intent queries ("something to help me sleep")
- Cross-lingual or code-mixed queries

Use full-text GIN indexes (tsvector in PostgreSQL, inverted index in dedicated
engines) to keep lexical retrieval fast. Analyzer chain — tokenizer, token
filters, stemmer — determines which token surface forms are stored; configure
once at index time and lock it before production traffic starts.

---

## 3. Dense Vector Stage (ANN)

Dense retrieval embeds the query into the same vector space as indexed documents,
then finds approximate nearest neighbors (ANN).

**When dense retrieval earns its cost:**
- Paraphrase or synonym queries where BM25 consistently misses relevant docs
- Semantic intent queries with no keyword overlap with relevant documents
- Multi-lingual corpora where the embedding model covers all languages

**When dense retrieval does NOT earn its cost:**
- BM25 alone already meets recall@K targets on your judged-query set
- The embedding model was not trained on your domain (verify on a sample)
- Latency budget leaves no headroom for an ANN call plus embedding generation

**Index type:** choose an HNSW or IVF-based ANN index. HNSW offers better
recall at query time; IVF-Flat is cheaper to build for large corpora. Verify
current engine defaults at use-time — parameter tuning (ef_construction, m,
nprobe) directly affects recall vs. latency tradeoff. [verify against current
vendor benchmark]

---

## 4. Fusion Stage (Reciprocal Rank Fusion)

RRF merges two or more ranked lists without requiring score normalization.

**Formula:**

```
RRF(d) = Σ  1 / (k + rank_i(d))
```

where `rank_i(d)` is the position of document `d` in list `i`, and `k` is a
smoothing constant. `k = 60` was the empirically-best value in the original RRF
paper's benchmarks (Cormack, Clarke & Büttcher, "Reciprocal Rank Fusion
Outperforms Condorcet and Individual Rank Learning Methods," SIGIR 2009) and
most engines (Elasticsearch's `rank_constant`, for example) ship it as the
default. Treat it as a safe starting point, not a proven-optimal constant for
every corpus — tune on your judged-query set.

**Why RRF over weighted-sum fusion:**

| Property | RRF | Weighted sum |
|---|---|---|
| Requires score normalization | No | Yes |
| Stable across query types | Yes | Fragile |
| Parameter surface | One (`k`) | One weight per retriever |
| Sensitive to BM25 score scale changes | No | Yes |

Use weighted-sum fusion only after normalizing scores on a held-out judged-query
set. When score calibration is unclear, prefer RRF.

Elasticsearch exposes RRF as a native `rrf` retriever (minimum two child
retrievers, `rank_constant` and `rank_window_size` parameters). OpenSearch
supports RRF via a search-pipeline `score-ranker-processor` layered on its
`normalization-processor` hybrid query. Qdrant's Query API supports RRF and
DBSF (distribution-based score fusion) as prefetch-fusion methods. Verify the
current API surface, parameter names, and minimum supported version in each
engine's `current` docs before coding — these APIs have moved between minor
releases in the past two years.

---

## 5. Cross-Encoder Reranking Stage

A cross-encoder takes the (query, document) pair as a single input and produces
a relevance score. Because it attends to both jointly, it is more accurate than
the bi-encoder that generated the dense vectors — but slower, so it runs only
on a small candidate set.

**Typical operating parameters:**
- Feed the top-N from the fusion stage (commonly 20–100 candidates)
- Return the top-M to the caller (commonly 5–20)
- Latency cost scales linearly with N; keep N as small as recall allows

**When cross-encoder reranking earns its cost:**
- Final precision on your judged-query set is below acceptable threshold after
  lexical + dense + RRF
- Latency budget after fusion still has headroom for an additional model call
- The reranker was trained on a distribution similar to your queries

**When cross-encoder reranking does NOT earn its cost:**
- RRF alone meets precision targets
- P99 latency after fusion is already at or above budget
- You do not have a judged-query set to verify the gain is real

Open-weight cross-encoders are available on Hugging Face (BGE-reranker family,
ms-marco variants, domain fine-tunes). Hosted reranking APIs are available
from providers including Cohere, Jina, Voyage, and others — treat this as a
capability class, not a fixed vendor list, and do not hardcode specific model
version names in a recommendation. [verify against current vendor benchmark]
— check current BEIR or MIRACL leaderboard standings, and confirm the reranker
was evaluated on a distribution similar to your query mix, at use-time.

---

## 6. In-Postgres Hybrid Option (pgvector + BM25)

For teams already on PostgreSQL who want hybrid search without a dedicated
engine:

- **Dense retrieval:** pgvector extension; store embeddings in a `vector` column,
  build an HNSW index, query with `<=>` (cosine) or `<->` (L2).
- **Lexical retrieval:** tsvector/tsquery with a GIN index.
- **Fusion:** compute RRF in SQL, or retrieve both ranked lists and fuse in
  application code.

**When the in-Postgres path is appropriate:**
- Dataset fits comfortably in a single Postgres instance (operationally managed)
- Team wants to avoid a second operational dependency
- Latency requirements are compatible with Postgres ANN performance at your
  data scale

**When to move to a dedicated engine:**
- Dataset scale makes Postgres ANN recall or latency unacceptable [verify
  against current pgvector benchmarks at use-time]
- You need faceted aggregations, complex analyzers, or distributed sharding
- You need native RRF support without custom SQL

pgvector supports `halfvec` (16-bit float, half the storage of `float32`) and
binary quantization (`binary_quantize`, ~1 bit per dimension) for storage
reduction, alongside HNSW and IVFFlat index types. See the worked memory-sizing
example in `SKILL.md` for how to re-derive the storage math for your own
corpus size and dimension count. Verify the current pgvector version,
quantization options, and index type support in the pgvector GitHub README at
use-time — this extension has added capabilities across recent minor releases.

---

## 7. Engine Capability Classes

Treat engines as capability classes, not fixed versions. Resolve current feature
status in each engine's `current` or `latest` docs before recommending.

| Engine | Lexical (BM25) | Dense (ANN) | Native hybrid / RRF | Notes |
|---|---|---|---|---|
| Elasticsearch | Yes | Yes | Yes — native `rrf` retriever | Elastic Cloud or self-managed; license is SSPL/Elastic License v2/AGPLv3 (choose one) — verify current terms before redistribution decisions |
| OpenSearch | Yes | Yes | Yes — `normalization-processor` + `score-ranker-processor` (RRF) | AWS-managed or self-managed; Apache 2.0 |
| Weaviate | Yes, native (no longer module-gated) | Yes | Yes — native BM25 + vector fusion | Verify current fusion algorithm options in docs |
| Qdrant | Yes, native (BM25 sparse vectors) | Yes | Yes — Query API prefetch + RRF or DBSF fusion | Purpose-built vector engine; DBSF suits well-calibrated retriever scores |
| pgvector (Postgres) | Via tsvector | Yes | Via SQL or app-layer fusion (no native RRF) | In-database; no extra service |

Engine capability classes shift release to release — Weaviate and Qdrant both
moved from module/client-side lexical support to native BM25 within the past
two years. Do NOT pin engine versions in design decisions. Always anchor
recommendations to the engine's canonical `current` documentation.

---

## 8. When Each Stage Earns Its Cost

Use this table as a decision gate before adding a stage.

| Stage | Add when | Skip when |
|---|---|---|
| Dense vector retrieval | BM25 recall misses paraphrase/semantic queries on judged set | BM25 alone meets recall targets |
| RRF fusion | Both lexical and dense retrievers are live and lists need merging | Only one retriever is running |
| Cross-encoder reranking | Precision below target after fusion, latency budget has headroom | Precision is acceptable after RRF, or latency is already at budget |

---

## 9. Checklist Before Shipping a Hybrid Pipeline

- [ ] Judged-query set exists with coverage across navigational, informational,
  and tail queries
- [ ] Recall@K from each retriever measured against the judged set separately
- [ ] Fusion method selected (RRF vs. weighted sum) and `k` tuned on the judged set
- [ ] Cross-encoder evaluated: measured gain vs. cost, not assumed
- [ ] Latency budget defined for full search path and for autocomplete separately
- [ ] Structured logs capture: raw query, cleaned query, retrieval mode, candidate
  counts per stage, top result IDs, per-stage latency
- [ ] Zero-result rate monitored; hybrid reduces but does not eliminate zero-result
  queries — confirm with live traffic

---

## 10. Freshness

Resolve current engine versions, feature availability, and quantitative
benchmark figures via the canonical sources in `data/sources.json` at
use-time:

- Elasticsearch: https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html
- OpenSearch: https://docs.opensearch.org/latest/
- pgvector: https://github.com/pgvector/pgvector
- Qdrant: https://qdrant.tech/documentation/
- Weaviate: https://weaviate.io/developers/weaviate

Do not state version numbers or quantitative benchmark figures from memory.
Write "[verify against current vendor benchmark]" wherever a figure is needed
and resolve it from primary sources at use-time.
