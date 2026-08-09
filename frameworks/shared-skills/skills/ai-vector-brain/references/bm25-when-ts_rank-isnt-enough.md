# BM25 — When ts_rank Isn't Enough

PostgreSQL's `ts_rank` and `ts_rank_cd` score lexical matches by term
frequency and field weight — but they have **no IDF** (inverse document
frequency) and **no document-length saturation**. On large tables this means
relevance `ORDER BY` degrades: documents that repeat a query term many times
rank above genuinely relevant ones, and rare terms receive the same weight as
common ones. When labeled evals reveal this failure mode, the fix is real Okapi
BM25 scoring — available natively in ParadeDB `pg_search` on Postgres, and
natively in OpenSearch, Elasticsearch, Weaviate, Vespa, LanceDB,
Turbopuffer, Azure AI Search, and Redis Stack on other backends.

This toolkit is **not** a guide to tuning `ts_rank` — normalization flags do
not add IDF. It is also **not** a backend-selection guide — use
[backend-selection.md](backend-selection.md) for that. The scope is: when the
lexical leg needs upgrading from tsvector to true BM25, what is the recipe on
each backend?

> Verified against primary sources fetched 2026-05-19 (see Verified-against
> table). Backend feature claims are volatile — re-verify before production
> adoption.

## Table of Contents

- [When you need this](#when-you-need-this)
- [Decision](#decision)
- [Worked recipe — ParadeDB pg\_search](#worked-recipe--paradedb-pg_search)
- [Per-backend coverage](#per-backend-coverage)
- [Anti-patterns](#anti-patterns)
- [Known traps](#known-traps)
- [Verified against](#verified-against)

## When you need this

**Trigger signals (adopt BM25 when you see these in evals):**

- `ts_rank` / `ts_rank_cd` `ORDER BY` places documents with many keyword
  repetitions above genuinely relevant ones on large tables (keyword stuffing
  winning).
- Rare query terms (low-frequency domain jargon, product codes) fail to surface
  relevant documents even when the match is exact — because `ts_rank` weights
  every matched term identically, regardless of corpus-wide frequency.
- Retrieval MRR or recall@5 on labeled eval set falls below threshold and
  lexical tuning (setweight, normalization flags, `ts_rank_cd` proximity) does
  not recover it.

**When you do NOT need this (YAGNI gate):**

- The corpus is small (< ~50k chunks) — ts_rank ranking differences are
  imperceptible at this scale.
- The hybrid fusion leg (RRF in `003_hybrid_search_function.sql`) already
  passes eval — RRF consumes rank position, not raw score; BM25's score
  precision benefit is downstream of position and may be absorbed by the
  fusion.
- The corpus is identifier/code-heavy — exact-token recall (the `008` tsvector
  with `vb_unaccent_simple`) matters more than IDF-weighted ranking; see
  [postgres-fts-tuning.md](postgres-fts-tuning.md).
- No labeled eval set exists — do not upgrade the lexical leg without
  measurement; you cannot know whether the upgrade helped.

## Decision

This toolkit addresses the **lexical leg** of the hybrid retrieval pipeline:

```
query → [BM25 lexical leg] ─┐
                              ├─ RRF fusion → top-K results
query → [dense vector leg]  ─┘
```

The decision to upgrade the lexical leg to BM25 is **independent** of the
RRF fusion step. The fusion function (`003_hybrid_search_function.sql`) consumes
rank position, so replacing the tsvector CTE with a BM25 CTE requires no
changes to the fusion logic.

Cross-link: [lexical-vs-vector-vs-hybrid.md](lexical-vs-vector-vs-hybrid.md)
covers the upstream decision of whether to enable a lexical leg at all, and
when to run the BM25 upgrade evaluation.

## Worked recipe — ParadeDB pg\_search

**Prerequisite:** ParadeDB `pg_search` installed on the Postgres instance.
See https://github.com/paradedb/paradedb for installation (packages available
for major Postgres versions).

**SQL asset:** [`../assets/sql/009_bm25_pg_search.sql`](../assets/sql/009_bm25_pg_search.sql)

```sql
-- UP: create the BM25 index (from 009_bm25_pg_search.sql)
DROP INDEX IF EXISTS idx_chunks_bm25;

CREATE INDEX idx_chunks_bm25
  ON chunks
  USING bm25 (
    id,
    content,
    contextual_summary,
    section_path,
    doc_type,
    symbol_name
  )
  WITH (key_field = 'id');
```

**Lexical CTE swap in `003_hybrid_search_function.sql`** (do not edit 003
directly; see the commented patch block in 009 for the full replacement):

```sql
-- Replace the ts_rank CTE with this BM25 CTE:
lexical AS (
  SELECT id AS chunk_id,
         ROW_NUMBER() OVER (ORDER BY pdb.score(id) DESC) AS rank_pos
  FROM   chunks
  WHERE  content ||| query_text
    AND  <existing filter predicates unchanged>
  LIMIT  candidate_count
)
```

`pdb.score(id)` returns the true Okapi BM25 score. RRF downstream consumes rank
position only — no score calibration needed after the swap. The `|||` match
operator tokenizes the bound `query_text` with the content field's tokenizer;
avoid string-concatenating raw user text into `pdb.parse()`.

**Down:** `DROP INDEX IF EXISTS idx_chunks_bm25;` — the tsvector leg in 008
resumes automatically.

## Per-backend coverage

| Backend | Verdict | Pointer / caveat |
|---|---|---|
| pgvector | not-supported | No BM25 engine; use tsvector leg ([postgres-fts-tuning.md](postgres-fts-tuning.md)) |
| pgvectorscale | not-supported | StreamingDiskANN + SBQ only; no lexical/BM25 index; use tsvector leg |
| ParadeDB | native | `CREATE INDEX ... USING bm25`; `pdb.score(id)`; Tantivy-backed |
| Qdrant | emulate | Sparse-vector dot-product via sparse index -- not true BM25 IDF/saturation; anti-pattern unless sparse-vector recall already passes eval |
| Weaviate | native | `.bm25()` query method; BM25F scoring with property weighting |
| Milvus/Zilliz | unverified | BM25 FTS not primary-source-confirmed at build (milvus.io redirect-looped) |
| Vespa | native | `bm25(fieldName)` rank feature; configurable b/k1 via rank-profile |
| LanceDB | native | FTS via Lance with BM25 scoring; keyword-based retrieval |
| Chroma | not-supported | `$contains` substring filter only; no BM25 scoring; use dense leg + rerank |
| AWS S3 Vectors | not-supported | Vector similarity only; pair with OpenSearch for BM25 (see S3 Vectors docs on OpenSearch integration) |
| Turbopuffer | native | Dedicated BM25 full-text search guide; hybrid BM25 + vector supported |
| Pinecone Serverless | native | BM25 via document-schema API; public-preview, two-path caveat in Known traps |
| Cloudflare Vectorize | not-supported | Vector-only; no FTS/BM25; pair with a lexical engine |
| Upstash Vector | unverified | Sparse/keyword index documented; BM25 not confirmed by name in primary docs at build time |
| AWS Bedrock KB | not-supported | Vector RAG only; no native BM25; pair with OpenSearch for lexical leg |
| Azure AI Search | native | BM25Similarity default on all services created after July 2020; configurable b/k1 |
| Vertex AI Vector Search | unverified | Sparse embeddings for keyword-style search supported; BM25 not confirmed by name in primary docs at build time |
| OpenAI File Search | unverified | Opaque managed service; scoring algorithm not publicly documented; docs returned 403 at build time |
| Elasticsearch/OpenSearch | native | BM25 default similarity (Elasticsearch: `BM25Similarity (default)`); `match` query |
| Redis Stack | native | `BM25STD` is the default scorer in Redis Open Source >= 8.4 (`FT.SEARCH ... SCORER BM25STD`); `BM25` is deprecated |
| MongoDB Atlas | not-supported | Atlas Search uses Lucene 3.5.0 scoring (not BM25); no integrated BM25 |

Legend: native (recipe/operator pointer) · emulate (how + "anti-pattern unless X") · not-supported (use leg/toolkit Y) · unverified (not primary-source-confirmed at build)

## Anti-patterns

**Pattern → Anti-pattern → Recipe**

**Pattern: upgrade the lexical leg for true BM25 IDF/saturation.**

- Anti-pattern: tuning `ts_rank` normalization flags (e.g., flag 32 for
  document-length normalization) expecting BM25-equivalent behaviour.
  `ts_rank` normalization is a linear divisor, not the BM25 saturation
  function; it cannot replicate IDF. All normalization tuning is wasted if
  IDF is the missing signal.
- Recipe: run evals first. If `ts_rank` ORDER BY fails (MRR drops on rare-term
  queries), install pg_search and swap the lexical CTE per 009.

**Pattern: keep a single lexical leg active at a time.**

- Anti-pattern: running both `idx_chunks_fts` (GIN tsvector from 008) and
  `idx_chunks_bm25` (pg_search from 009) simultaneously in production.
  Both indexes write on every INSERT/UPDATE, doubling lexical write overhead
  with no recall benefit — only one leg is used in the CTE at query time.
- Recipe: drop `idx_chunks_fts` when deploying 009 in production; restore it
  via 008's DOWN section if rolling back to tsvector.

**Pattern: validate BM25 upgrade with labeled evals before deploying.**

- Anti-pattern: shipping the BM25 leg without a before/after eval comparison.
  BM25 can regress on short-document corpora (document-length saturation
  hurts when all docs are similar length and short — IDF is the only win, and
  on small corpora IDF variance is low).
- Recipe: run `scripts/build_eval_seed.py`, label expected evidence, measure
  recall@5 and MRR on tsvector vs BM25 before committing to 009.

## Known traps

- **ParadeDB pg_search is not available for new Neon projects (as of March 19, 2026).** Neon previously offered pg_search to all users; that availability ended for new projects on that date. Existing projects that loaded pg_search continue to have access, but new Neon projects cannot install it. Teams on Neon building against a new project must use the `ts_rank` / FTS path (assets/sql/008_fts_hardening.sql) or add an external lexical leg (OpenSearch, Typesense, Meilisearch) for BM25-quality scoring. If pg_search is required, run on a self-hosted Postgres, ParadeDB's managed offering, or a Neon project that predates the deprecation.

- **Only one BM25 index per table** — pg_search enforces this constraint. If a
  prior BM25 index exists on `chunks`, `CREATE INDEX … USING bm25` will error.
  The UP block in 009 drops the prior index first.
- **Pinecone has two distinct BM25 paths; pick the right one** — the legacy vector API's `pinecone-sparse-english-v0` model produces sparse vectors scored by dot product (not true Okapi BM25). The document-schema API (`type: "text"` field, public preview as of 2026-01.alpha) delivers real BM25 with IDF and length normalisation handled server-side. Use the document-schema path for true BM25; the sparse-vector path only if sparse recall passes eval without IDF.
- **Azure AI Search BM25 is per-shard by default** — scoring statistics are
  computed per shard; add `scoringStatistics=global` to queries for consistent
  cross-shard BM25 scores (costs a latency penalty).
- **RRF absorbs rank-position changes, not score precision** — the BM25 upgrade
  pays off when rank order changes (better candidates move up); if the same
  documents surface at the same positions, RRF produces identical results
  regardless of BM25 vs ts_rank raw scores.

## Verified against

| Claim | Source id |
|---|---|
| pgvector: no BM25 engine; vector-similarity index only | `pgvector-readme` |
| ParadeDB: `USING bm25` index type, Tantivy-backed | `paradedb-pg-search` |
| ParadeDB: BM25 scoring feature listed | `paradedb-docs` |
| pgvectorscale: no BM25 / statbm25 support | `pgvectorscale-readme` |
| Weaviate: native `.bm25()` query; BM25F scoring | `weaviate-docs` |
| Milvus: BM25 FTS not confirmed at build (milvus.io redirect-looped) | `milvus-docs` (unverified) |
| Vespa: `bm25(fieldName)` rank feature | `vespa-docs` |
| LanceDB: BM25 keyword-based search via Lance FTS (confirmed at docs.lancedb.com) | `lancedb-docs` |
| Turbopuffer: native BM25 full-text search | `turbopuffer-docs` |
| Azure AI Search: `BM25Similarity` fixed algorithm on all services created after July 2020 (primary source: learn.microsoft.com/azure/search/index-similarity-and-scoring) | `azure-ai-search-vector` |
| Elasticsearch: `BM25Similarity (default)` | `elasticsearch-vector` |
| Redis Stack: `BM25STD` default scorer (renamed from `BM25` in Redis Open Source 8.4) | `redis-stack-vector` |
| Cloudflare Vectorize: vector-only, no BM25 | `cloudflare-vectorize` |
| AWS S3 Vectors: vector similarity only | `aws-s3-vectors` |
| AWS Bedrock KB: vector RAG only | `aws-bedrock-knowledge-bases` |
| OpenSearch: `match` query supported (full-text) | `opensearch-bm25` |
| Pinecone: native BM25 via document-schema API; IDF + length normalisation at index time; public preview 2026-01.alpha | `pinecone-fts` |
| Qdrant: sparse-vector index with IDF modifier; dot-product scoring; no Okapi BM25 length saturation | `qdrant-docs` |
| MongoDB Atlas: Atlas Search scoring references Lucene 3.5.0 (classic VSM, not BM25) | `mongodb-atlas-vector` |
| Chroma: `$contains` / `$not_contains` substring filter only; no BM25 scoring | `chroma-docs` |
