# Learned-Sparse / SPLADE — The Fourth Leg

Learned-sparse models (SPLADE, ELSER, and their derivatives) encode queries and
documents as sparse token-weight vectors — high-dimensional but with very few
non-zero elements — that capture both exact-term precision and semantic
expansion through learned term co-occurrence. They close a specific gap: when
dense embeddings blur rare or exact terms (product codes, drug names, obscure
jargon), tsvector is too brittle to handle morphological variation, and BM25 adds
IDF/saturation but no learned generalisation — a SPLADE-style fourth leg bridges
all three failure modes simultaneously. The DB stores the sparse vector; the
expansion model runs in the app layer before insert and before query. This
toolkit is **not** a guide to training or fine-tuning sparse models — use the
Hugging Face `naver/splade-v3` family or Elasticsearch's ELSER for English, and
treat the model choice as out-of-scope here. It is also **not** a backend
selection guide — use [backend-selection.md](backend-selection.md) for that.

> Verified against primary sources fetched 2026-05-19 (see Verified-against
> table). Backend feature claims are volatile — re-verify before production
> adoption. Scope: when the retrieval pipeline needs a learned-sparse leg, what
> is the recipe on each backend?

## Table of Contents

- [When you need this](#when-you-need-this)
- [Decision](#decision)
- [Worked recipe — pgvector](#worked-recipe--pgvector)
- [Per-backend coverage](#per-backend-coverage)
- [Anti-patterns](#anti-patterns)
- [Known traps](#known-traps)
- [Verified against](#verified-against)

## When you need this

**Trigger signals (adopt the learned-sparse leg when you see these in evals):**

- Dense retrieval misses queries containing rare or exact terms (drug names,
  industrial part numbers, regulatory identifiers, proprietary jargon) that do
  not cluster near semantically similar documents in embedding space.
- tsvector covers the exact-match case but is too brittle: no morphological
  generalisation, fails on typos, brittle across languages, collapses when the
  user term and the document term are both present but differently inflected.
- Hybrid (lexical + dense + RRF) already runs but labeled evals still show MRR
  or recall@5 failing on the rare-exact-term query class — the failure persists
  after BM25 upgrade of the lexical leg.

**When you do NOT need this (YAGNI gate):**

- Hybrid (lexical + dense) RRF already passes your labeled retrieval eval for
  the query distribution in production — do not add a fourth leg without
  measurement; you cannot know whether the upgrade helped.
- No labeled eval set exists — you cannot determine whether rare-term recall is
  a real gap or whether the model improves it; build the eval before adding
  infrastructure.
- The corpus is short-form and code-heavy — tsvector with `simple`+`unaccent`
  weight-A already captures exact identifiers; SPLADE generalisation adds noise,
  not signal, for code symbols.
- The operational cost of running a sparse embedding model (latency, memory, API
  cost per insert and per query) exceeds the retrieval gain — profile first.

## Decision

This toolkit addresses a **fourth leg** of the retrieval pipeline, alongside
the existing three:

```
query → [tsvector / BM25 lexical leg] ─┐
query → [dense vector leg]             ─┤
query → [learned-sparse leg]           ─┼─ RRF fusion → top-K results
                                        │
        (plain SQL for count/aggregate)─┘
```

The decision to add the learned-sparse leg is **independent** of the RRF fusion
step. The fusion function in `003_hybrid_search_function.sql` consumes rank
position; adding a third input CTE requires only extending the UNION ALL block —
see `assets/sql/010_sparsevec.sql`.

Cross-link: [lexical-vs-vector-vs-hybrid.md](lexical-vs-vector-vs-hybrid.md)
covers the upstream choice of whether any retrieval leg is needed, and the
decision matrix for which leg(s) a given query shape requires.

## Worked recipe — pgvector

**Prerequisite:** pgvector installed (ships the `sparsevec` type; no additional
extension required). App must call a SPLADE or ELSER-style model before insert
and before query to produce sparse token-weight maps. The DB stores and retrieves
sparse vectors; it does not run the expansion model.

**SQL asset:** [`../assets/sql/010_sparsevec.sql`](../assets/sql/010_sparsevec.sql)

```sql
-- UP: add sparsevec column and HNSW inner-product index (from 010_sparsevec.sql)
ALTER TABLE chunks
  ADD COLUMN IF NOT EXISTS sparse_vec sparsevec;

CREATE INDEX IF NOT EXISTS idx_chunks_sparsevec
  ON chunks
  USING hnsw (sparse_vec sparsevec_ip_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE sparse_vec IS NOT NULL;
```

**App-layer expansion (before INSERT and before query):**

```python
# Pseudocode — any SPLADE-compatible model works here.
# naver/splade-v3 is the recommended open-weight English model.
sparse_model = SpladeEncoder("naver/splade-v3")

# At index time (before INSERT):
doc_sparse = sparse_model.encode_document(chunk.content)
# → {"2134": 0.41, "8910": 0.27, ...}  (token_id: weight)
chunk.sparse_vec = to_sparsevec(doc_sparse)  # app converts to pgvector format

# At query time (before SQL):
query_sparse = sparse_model.encode_query(user_query)
query_sparse_pg = to_sparsevec(query_sparse)
```

**Sparse leg CTE in `003_hybrid_search_function.sql`** (add alongside the
existing lexical and dense CTEs — see the comment block in 010 for the full
UNION ALL patch):

```sql
-- Sparse leg: inner-product (dot-product) ANN search on learned-sparse vectors.
-- Insert AFTER the `filtered` CTE (003's ACL/authority/as_of pre-filter) and
-- select FROM it — do NOT copy the filter predicates inline; that bypasses ACL.
sparse AS (
  SELECT f.id,
         ROW_NUMBER() OVER (
           ORDER BY c.sparse_vec <#> query_sparse_vec ASC
         ) AS rank
  FROM   filtered f
  JOIN   chunks c ON c.id = f.id
  WHERE  query_sparse_vec IS NOT NULL
    AND  c.sparse_vec IS NOT NULL
  LIMIT  candidate_count
)
```

`<#>` returns negative inner product; `ORDER BY ASC` is the pgvector
nearest-neighbor direction and lets the `sparsevec_ip_ops` index participate.
RRF downstream consumes rank position only — no score calibration needed after
adding the sparse CTE. The sparse CTE must reuse 003's `filtered` pre-filter CTE
so that ACL, authority, and as_of constraints are enforced before the ANN search.

**Down:** `DROP INDEX IF EXISTS idx_chunks_sparsevec; ALTER TABLE chunks DROP COLUMN IF EXISTS sparse_model_id; ALTER TABLE chunks DROP COLUMN IF EXISTS sparse_vec;` — the lexical+dense RRF in 003 resumes unchanged.

## Per-backend coverage

| Backend | Verdict | Pointer / caveat |
|---|---|---|
| pgvector | native | `sparsevec` type; HNSW `sparsevec_ip_ops`; <=1,000 non-zero for HNSW index; <=16,000 stored |
| pgvectorscale | not-supported | StreamingDiskANN/SBQ indexes dense `vector` only; no `sparsevec` index; use pgvector for sparse leg |
| ParadeDB | unverified | Inherits pgvector's `sparsevec`; sparse HNSW not primary-source-confirmed in ParadeDB docs at build |
| Qdrant | native | Named sparse vectors; separate inverted-index storage; SPLADE integration via FastEmbed |
| Weaviate | unverified | Hybrid search uses BM25F + dense; separate learned-sparse vector storage not confirmed in primary docs at build |
| Milvus/Zilliz | unverified | Sparse vector support documented in milvus.io; `SPARSE_FLOAT_VECTOR` / `SPARSE_INVERTED_INDEX` not primary-source-confirmed at build (milvus.io returned 403) |
| Vespa | unverified | `tensor<float>(x{})` mapped tensor supports sparse structures; SPLADE via pyvespa not primary-source-confirmed at build (pyvespa URL 404) |
| LanceDB | unverified | FTS + dense vector supported; dedicated sparse vector column / SPLADE leg not primary-source-confirmed at build |
| Chroma | not-supported | Dense `embedding` column only; no sparse vector storage; use dense+rerank or add a lexical engine |
| AWS S3 Vectors | not-supported | Dense vector storage only; no sparse vector type; pair with OpenSearch for sparse/neural-sparse leg |
| Turbopuffer | unverified | BM25 FTS + dense hybrid supported; separate SPLADE sparse vector leg not primary-source-confirmed at build |
| Pinecone Serverless | unverified | Sparse-vector index exists (dot-product); SPLADE-style workflow documented; BM25 is separate; verify current API |
| Cloudflare Vectorize | not-supported | Dense vector only; no sparse vector type; pair with a lexical engine for rare-term precision |
| Upstash Vector | unverified | Sparse/keyword index mentioned in overview; SPLADE-specific workflow not primary-source-confirmed at build |
| AWS Bedrock KB | not-supported | Managed dense vector RAG only; no sparse vector leg; pair with OpenSearch neural-sparse for this need |
| Azure AI Search | unverified | Semantic ranker + BM25 hybrid confirmed; dedicated SPLADE sparse vector field not primary-source-confirmed at build |
| Vertex AI Vector Search | not-supported | Dense vector index (ScaNN) only; no sparse vector support; pair with a separate sparse leg |
| OpenAI File Search | unverified | Opaque managed service; docs 403 at build; sparse-leg support not primary-source-confirmed |
| Elasticsearch/OpenSearch | native | ES: ELSER `sparse_vector` field + `text_expansion` / `sparse_vector` query; OS: neural-sparse processor + `sparse_vector` field |
| Redis Stack | not-supported | HNSW index on dense vectors only; no sparse vector type; BM25STD is lexical, not learned-sparse |
| MongoDB Atlas | unverified | Atlas Vector Search indexes dense vectors; sparse vector / SPLADE leg not primary-source-confirmed at build |

Legend: native (recipe/operator pointer) · emulate (how + "anti-pattern unless X") · not-supported (use leg/toolkit Y) · unverified (not primary-source-confirmed at build)

## Anti-patterns

**Pattern → Anti-pattern → Recipe**

**Pattern: run the sparse expansion model in the app layer, store vectors in the DB.**

- Anti-pattern: calling a SPLADE model at query time inside a database function
  or stored procedure, or storing raw text and expecting the DB to run the model
  at search time. The DB stores and retrieves sparse vectors; it does not run
  transformer inference.
- Recipe: encode the document at ingest time (`sparse_model.encode_document`)
  before INSERT; encode the query at query time before the SQL call; pass the
  resulting sparse vector as a query parameter (`$1 :: sparsevec`).

**Pattern: add the sparse leg only after evals confirm the gap.**

- Anti-pattern: adding the learned-sparse leg "just in case" before measuring
  whether rare-term recall is actually a failure mode. SPLADE vectors require
  running a model on every chunk at index time and on every query at runtime —
  the cost is real. If hybrid RRF already passes eval, the leg adds latency and
  infrastructure with no measurable gain.
- Recipe: run `scripts/build_eval_seed.py`, label expected evidence for rare-term
  queries, measure recall@5 and MRR on dense-only vs lexical+dense vs
  lexical+dense+sparse before committing to 010.

**Pattern: use inner product (`<#>`) for SPLADE/ELSER vectors, not cosine distance.**

- Anti-pattern: indexing `sparsevec` with `sparsevec_cosine_ops` for
  SPLADE/ELSER vectors, or sorting `ORDER BY sparse_vec <=> query` (cosine).
  SPLADE and ELSER scores are dot-product-based by design; L2-normalising and
  then cosine-scoring is an approximation that loses the weight-magnitude
  information the model was trained to express.
- Recipe: use `sparsevec_ip_ops` and `ORDER BY sparse_vec <#> query_sparse_vec
  ASC`; pgvector indexes nearest-neighbor distance operators in ascending order.

**Pattern: use asymmetric encoding — document encoder at index time, query encoder at query time.**

- Anti-pattern: using the same SPLADE checkpoint for both document and query
  encoding when the model has separate `doc_encoder` / `query_encoder` heads
  (SPLADE-v3 and most production checkpoints are asymmetric). Using the wrong
  head degrades recall significantly.
- Recipe: always call `encode_document` for chunks at index time and
  `encode_query` for user queries at runtime. Check the model card for
  asymmetry.

## Known traps

- **HNSW `sparsevec` index limit is 1,000 non-zero elements** — pgvector's HNSW
  index on `sparsevec` supports at most 1,000 non-zero elements. SPLADE-v3
  typically produces 50–300 non-zero elements per document, well within the
  limit. If using a denser SPLADE variant or ELSER with an expanded vocabulary,
  verify non-zero element counts before building the index; rows over 1,000
  non-zero elements will be excluded from the HNSW index (they still reside in
  the table and can be found via sequential scan, but not via ANN search).
- **`sparsevec` HNSW returns approximate results** — like all HNSW indexes, the
  sparse index is ANN, not exact. For ground-truth eval baselines, use a
  sequential scan: `ORDER BY sparse_vec <#> $1 LIMIT k` without the index. Use
  `SET enable_indexscan = off` to force sequential scan in a session.
- **Milvus sparse vectors do not automatically run SPLADE** — `SPARSE_FLOAT_VECTOR`
  stores pre-computed sparse vectors; the Milvus built-in BM25 FTS is a
  separate feature. To use SPLADE with Milvus, run the model externally and
  insert the sparse float vector directly.
- **OpenSearch neural-sparse has two operating modes** — doc-only mode (cheaper:
  only query is expanded at search time, documents are indexed as raw tokens)
  and bi-encoder mode (documents and queries both expanded by the model, higher
  quality). The neural sparse two-phase processor pipeline applies doc-only mode
  first, then rescores with bi-encoder — confirm the mode in your pipeline
  config before benchmarking.
- **ELSER requires an Elasticsearch subscription or trial** — ELSER v2 is
  generally available but is not Apache-licensed; it requires an Elastic
  subscription at the appropriate tier. Verify licensing before production
  adoption.
- **Stale sparse vectors after model upgrade** — sparse token IDs are
  model-vocabulary-specific. Upgrading the SPLADE checkpoint requires
  re-encoding the entire corpus; partial re-encoding creates vocabulary
  mismatches between old and new rows. Add a `sparse_model_id` column (parallel
  to the `model_id` column in 001_schema.sql) and filter by it in the sparse CTE
  to avoid cross-model score incompatibility during migration. The `-- UP`
  migration in `010_sparsevec.sql` provisions this column
  (`sparse_model_id TEXT`).

## Verified against

| Claim | Source id |
|---|---|
| pgvector: `sparsevec` type exists; `8 * non-zero elements + 16` bytes; ≤16,000 non-zero stored | `pgvector-readme` |
| pgvector: HNSW `sparsevec` index limit: ≤1,000 non-zero elements | `pgvector-readme` |
| pgvector: `sparsevec` operators `<->`, `<#>`, `<=>`, `<+>` | `pgvector-readme` |
| pgvectorscale: StreamingDiskANN + SBQ only; no sparse vector index | `pgvectorscale-readme` |
| Qdrant: sparse vectors kept in special storage, indexed in a separate index | `qdrant-docs` |
| Qdrant: named sparse vectors (e.g. `text-sparse`) supported | `qdrant-docs` |
| Qdrant: SPLADE via FastEmbed documented (tutorial listed in docs) | `qdrant-docs` |
| Elasticsearch: ELSER — "Elastic Learned Sparse EncodeR" — retrieval model; `sparse_vector` field type used | `elasticsearch-elser` |
| Elasticsearch: ELSER expands passages into collections of terms; terms are learned associations | `elasticsearch-elser` |
| OpenSearch: neural-sparse search documented; sparse_encoding ingest processor; neural sparse query; two-phase processor | `opensearch-neural-sparse` |
| Chroma: no sparse vector type; `$contains` / `$not_contains` filter only | `chroma-docs` |
| AWS S3 Vectors: dense vector storage only | `aws-s3-vectors` |
| AWS Bedrock KB: managed dense vector RAG only | `aws-bedrock-knowledge-bases` |
| Cloudflare Vectorize: vector-only, cosine/euclidean/dot-product distance metrics only | `cloudflare-vectorize` |
| Redis Stack: HNSW on dense vectors; BM25STD scorer (lexical, not sparse) | `redis-stack-vector` |
| Vertex AI Vector Search: dense vector index (ScaNN); no sparse vector support in primary docs | `vertex-vector-search` |
