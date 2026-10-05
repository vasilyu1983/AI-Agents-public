# Hybrid Search and Reranking Pipeline

Production retrieval combines lexical and dense-vector search, fuses the ranked
lists, and applies a cross-encoder reranker as a final stage. Each stage earns
its cost only when the previous stage's recall ceiling is already reached.

Before selecting an engine, use the capability lookup in section 4; verify model support and licences through the primary sources linked in section 7.

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

Hard filters (tenant, visibility, permissions) go inside each retrieval leg's
query, never after fusion or reranking; see the ACL invariant in
[ai-rag SKILL.md](../../ai-rag/SKILL.md#core-concepts).

---

## 2. Lexical Stage (BM25)

BM25 is a lexical baseline in Elasticsearch and OpenSearch. Do not assume every
engine uses it: [Typesense](https://typesense.org/docs/guide/ranking-and-relevance.html)
combines text-match signals, while [Meilisearch](https://www.meilisearch.com/docs/capabilities/full_text_search/relevancy/ranking_rules)
uses ordered ranking rules. Lexical retrieval suits SKUs, names, and domain terms;
negation still requires explicit query semantics or judged-query validation.

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

**Index type:** compare HNSW and IVF-based ANN on the same corpus, recall target,
query latency, build time, and memory budget. Parameters such as ef_construction,
m, and nprobe change the tradeoff; no index family always wins.

---

## 4. Fusion Stage (Reciprocal Rank Fusion)

RRF merges two or more ranked lists without requiring score normalization:

```
RRF(d) = Σ  1 / (k + rank_i(d))
```

**Fusion method, `k`, weights, and normalization are owned by ai-rag:** see
[hybrid-fusion-patterns.md](../../ai-rag/references/hybrid-fusion-patterns.md)
for the default ladder (unweighted RRF → weighted RRF → normalized linear), the
RRF-until-labels-then-convex-combination rule, and the Cormack `k = 60` caveat.

**Product-search note:** SKU, part-number, and exact-name queries are the usual
query class where the lexical leg should win; confirm it on the judged set
before adding per-leg weights.

**Engine capability lookup (check before coding fusion).** Engines differ in
what they fuse natively, and parameter names, defaults, minimum versions, and
licence gates move between releases, so this file pins none of them. For each
candidate engine, answer these from its current docs:

| Question | Why it matters |
|---|---|
| Native RRF? (single request, or a search-pipeline processor) | Without it you fuse in the application and paginate over a fixed fused window |
| Per-retriever / per-sub-query weights? Must they sum to 1? | Needed for step 2 of the ladder |
| Score-based (linear) fusion, and which normalizers (min-max, L2, z-score, distribution-based)? | Needed for step 3; some engines default to score-based fusion |
| Default fusion method and default keyword/vector balance when the weight is unset? | Defaults differ by engine and sometimes by client library |
| Licence or subscription tier that includes the fusion, rerank, and LTR features on self-managed deployments? | Native fusion can be gated to a paid tier; on a lower tier fuse in the application or choose another engine |
| Is hybrid search GA or experimental in the version you run? | Experimental features change API between minors |

Confirm each answer in the engine's current docs (links in
[`data/sources.json`](../data/sources.json)) before coding.

---

## 5. Cross-Encoder Reranking Stage

A cross-encoder takes the (query, document) pair as a single input and produces
a relevance score. Because it attends to both jointly, it is more accurate than
the bi-encoder that generated the dense vectors — but slower, so it runs only
on a small candidate set.

**Operating parameters:** the reranker candidate budget (top-N in, top-M out)
is owned by [ai-rag ranking-pipeline-guide.md](../../ai-rag/references/ranking-pipeline-guide.md#5-reranking-stage).
Latency cost scales linearly with N; keep N as small as recall allows.

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
version names in a recommendation. Evaluate shortlisted models on your judged
queries; an external leaderboard does not establish performance on your query mix.

---

## 6. In-Postgres Hybrid Option (pgvector + BM25)

For teams already on PostgreSQL who want hybrid search without a dedicated
engine:

- **Dense retrieval:** pgvector extension; store embeddings in a `vector` column,
  build an HNSW index, query with `<=>` (cosine) or `<->` (L2).
- **Lexical retrieval:** tsvector/tsquery with a GIN index — but `ts_rank`
  is not BM25 (no IDF, no term-frequency saturation). When lexical ranking
  quality is the limit, try a BM25 extension before moving engines:
  - **ParadeDB `pg_search`** — BM25 on Tantivy, plus facets/aggregations.
    Community edition is AGPL-3.0 (commercial licence for ParadeDB Enterprise);
    check AGPL obligations before shipping it inside a hosted product.
  - **`pg_textsearch`** (Tiger Data / Timescale) — native `USING bm25` index
    and `<@>` scoring operator; PostgreSQL Licence; needs
    `shared_preload_libraries`. Not available on every managed Postgres —
    check your provider's extension list.
- **Fusion:** compute RRF in SQL, or retrieve both ranked lists and fuse in
  application code.

**When the in-Postgres path is appropriate:**
- Dataset fits comfortably in a single Postgres instance (operationally managed)
- Team wants to avoid a second operational dependency
- Latency requirements are compatible with Postgres ANN performance at your
  data scale

**When to move to a dedicated engine:**
- Measured Postgres ANN recall or latency misses the product target on representative data
- You need typo tolerance, merchandising rules, complex analyzers, or
  distributed sharding that a BM25 extension does not cover
- You need native RRF support without custom SQL

pgvector offers half-precision and binary-quantized storage alongside HNSW and
IVFFlat index types. Look up in the pgvector README at use time: the maximum
indexable dimensions per vector type (a model's output size can exceed the HNSW
cap for full-precision vectors), and whether your installed version supports
iterative index scans for filtered search. Without iterative scans, an HNSW
scan with a selective `WHERE` filter can return fewer rows than `LIMIT` — a
common production recall failure. For index memory sizing, use the single
formula in
[ai-vector-brain production-runbook.md](../../ai-vector-brain/references/production-runbook.md#hnsw-memory-sizing);
the OpenSearch example in `vector-search-api-and-sizing.md` is engine-specific.

---

## 7. Engine Capability Classes

Treat engines as capability classes, not fixed versions. Resolve current feature
status, defaults, and licence terms in each engine's `current` or `latest` docs
before recommending; use the capability lookup in §4 for fusion.

| Engine | Lexical / learned sparse | Dense (ANN) | Hybrid fusion surface to check | Notes |
|---|---|---|---|---|
| Elasticsearch | BM25 and [ELSER learned sparse](https://www.elastic.co/docs/solutions/search/vector/sparse-vector) | Yes | Native RRF and linear retrievers; check per-retriever weights and the subscription tier that includes them on self-managed | Elastic Cloud or self-managed; check current licence terms before redistribution decisions |
| OpenSearch | Yes | Yes | Search-pipeline processors for normalization (linear) and RRF; check weight support in your version | AWS-managed or self-managed; Apache 2.0 |
| Weaviate | Yes, native | Yes | Score-based and rank-based fusion methods; check the default and the effective `alpha` when unset | Effective weighting can depend on the client |
| Qdrant | Yes, native (BM25 sparse vectors) | Yes | Query API prefetch with RRF or distribution-based score fusion (DBSF) | Purpose-built vector engine; DBSF suits well-calibrated retriever scores |
| Vespa | BM25 and [SPLADE learned sparse](https://docs.vespa.ai/en/rag/embedding.html#splade-embedder) | Yes | [Phased ranking](https://docs.vespa.ai/en/ranking/phased-ranking.html) combines retrieval and custom rank profiles | Consider when custom ranking warrants operating an application schema and ranking pipeline |
| pgvector (Postgres) | Via tsvector (`ts_rank`, not BM25) or a BM25 extension (`pg_search` AGPL-3.0, `pg_textsearch` PostgreSQL Licence) | Yes | Via SQL or app-layer fusion (no native RRF) | In-database; no extra service |

**Learned sparse is a separate retrieval choice.** ELSER and SPLADE encode text as
weighted token features; they are not dense embeddings or plain BM25. Evaluate
them when lexical recall misses semantic variants. Keep document/query encoders
compatible, budget inference at ingest and query time, and reindex when changing
the representation. Check model language coverage, licence, and deployment support
in the linked documentation before selection.

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
- [ ] Fusion method selected (unweighted RRF, weighted RRF, or normalized linear), licence tier confirmed, and `k`/weights tuned on the judged set
- [ ] Cross-encoder evaluated: measured gain vs. cost, not assumed
- [ ] Latency budget defined for full search path and for autocomplete separately
- [ ] Structured logs capture retrieval mode, candidate counts per stage, top
  result IDs, and per-stage latency; raw/cleaned query text is gated by the
  product's redaction, access, and retention decision
- [ ] Zero-result rate monitored; hybrid reduces but does not eliminate zero-result
  queries — confirm with live traffic
