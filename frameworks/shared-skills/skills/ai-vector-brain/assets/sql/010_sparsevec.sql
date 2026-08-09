-- 010_sparsevec.sql
-- Learned-sparse / SPLADE leg: sparsevec column + HNSW index on chunks.
--
-- WHY: Dense embeddings blur rare/exact terms (drug names, part numbers,
-- jargon); tsvector is too brittle (no semantic generalisation); BM25 (from
-- 009) adds IDF/saturation but no learned term co-occurrence.  Learned-sparse
-- models (SPLADE, ELSER-style) produce sparse token-weight vectors that
-- capture both exact-term precision and semantic expansion.  The DB stores the
-- sparse vector; SPLADE/ELSER expansion is an app-layer concern — run the model
-- BEFORE insert and pass the resulting {index: weight} map.
--
-- SELECTION CRITERION: adopt ONLY when:
--   (a) labeled evals show dense misses rare/exact-term queries, AND
--   (b) tsvector is too brittle (e.g. typos, morphology, cross-lingual), AND
--   (c) hybrid (lexical+dense) RRF has already been measured and falls short.
--   See references/learned-sparse-splade-leg.md.
--
-- PREREQUISITE: pgvector extension installed (sparsevec type shipped with
-- pgvector; no additional extension required).
--
-- INDEXING CONSTRAINT: pgvector's HNSW index on sparsevec supports at most
-- 1,000 non-zero elements.  SPLADE vectors typically have 50-300 non-zero
-- elements; ELSER vectors typically have 50-150 non-zero elements — both
-- well within the HNSW limit.  Verify at index build time.
--
-- OPERATOR: inner product (<#>) is the correct distance for SPLADE/ELSER
-- sparse vectors (dot-product similarity, not Euclidean distance).
--
-- Load order: after 001_schema.sql.  Independent of 008 and 009.
--
-- SQL not executed (no local Postgres); structural checks only.

-- ---------------------------------------------------------------------------
-- UP  — add sparsevec column and HNSW inner-product index
-- ---------------------------------------------------------------------------

-- Add the sparse-vector column and model-pin column to chunks.
-- NULLable: rows without a SPLADE vector are excluded from the sparse leg by
-- the WHERE clause in the CTE; no sentinel value needed.
-- sparse_model_id: pins each row's sparse vector to a specific model checkpoint,
-- preventing cross-model score incompatibility during SPLADE model upgrades
-- (see Known-traps "stale sparse vectors after model upgrade" in
-- references/learned-sparse-splade-leg.md).
ALTER TABLE chunks
  ADD COLUMN IF NOT EXISTS sparse_vec sparsevec;

ALTER TABLE chunks
  ADD COLUMN IF NOT EXISTS sparse_model_id TEXT;

-- HNSW index for inner-product (dot-product) similarity.
-- m = 16, ef_construction = 64 are safe defaults; tune up if recall drops.
-- Non-NULL predicate ensures rows without a sparse vector are never indexed.
CREATE INDEX IF NOT EXISTS idx_chunks_sparsevec
  ON chunks
  USING hnsw (sparse_vec sparsevec_ip_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE sparse_vec IS NOT NULL;

-- ---------------------------------------------------------------------------
-- How to add a sparse leg to 003_hybrid_search_function.sql
-- (do NOT edit 003 here; this is a pointer-only comment block)
--
-- 003 uses these identifiers verbatim — the sparse CTE must match them:
--   pre-filter CTE : filtered   (selects c.id, c.document_id; enforces ACL/
--                                authority/as_of before any ANN search)
--   rank column    : rank       (ROW_NUMBER alias used in semantic + lexical)
--   id column      : id         (not chunk_id)
--   RRF parameter  : rrf_k      (DOUBLE PRECISION function parameter, not 60)
--   fusion CTE     : fused      (SUM(1.0 / (rrf_k + rank)) AS rrf_score)
--
-- Add a third CTE AFTER the `filtered` CTE in 003, alongside semantic/lexical.
-- Select FROM filtered — do NOT copy the filter predicates inline; that would
-- bypass ACL/authority/as_of guards that filtered already enforces:
--
--   sparse AS (
--     SELECT f.id,
--            ROW_NUMBER() OVER (
--              ORDER BY c.sparse_vec <#> query_sparse_vec ASC
--            ) AS rank
--     FROM   filtered f
--     JOIN   chunks c ON c.id = f.id
--     WHERE  query_sparse_vec IS NOT NULL
--       AND  c.sparse_vec IS NOT NULL
--     LIMIT  candidate_count
--   )
--
-- Then extend the fused CTE's UNION ALL to include the sparse leg:
--
--   fused AS (
--     SELECT id, SUM(1.0 / (rrf_k + rank)) AS rrf_score
--     FROM (
--       SELECT id, rank FROM semantic
--       UNION ALL
--       SELECT id, rank FROM lexical
--       UNION ALL
--       SELECT id, rank FROM sparse    -- <-- new leg
--     ) candidates
--     GROUP BY id
--   )
--
-- Notes:
--   • query_sparse_vec must be produced OUTSIDE the DB — call the SPLADE /
--     ELSER model with the query text before issuing the SQL.  The DB stores
--     and retrieves sparse vectors; it does not run the expansion model.
--   • <#> returns negative inner product; ORDER BY ASC is the pgvector nearest-
--     neighbor direction and lets the sparsevec_ip_ops index participate.
--   • The sparse leg is optional in each query call: pass NULL for
--     query_sparse_vec to make the sparse CTE return no rows and fall back to
--     the lexical+dense RRF path transparently.
--   • HNSW inner-product on sparsevec is an ANN search — for exact recall
--     verification use: SELECT id FROM chunks ORDER BY sparse_vec <#>
--     $1 LIMIT 10  (sequential scan, no index, for eval baseline only).
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- DOWN  — remove the sparse leg (exact inverse of UP; index first, then columns)
-- ---------------------------------------------------------------------------
-- DROP INDEX IF EXISTS idx_chunks_sparsevec;
-- ALTER TABLE chunks DROP COLUMN IF EXISTS sparse_model_id;
-- ALTER TABLE chunks DROP COLUMN IF EXISTS sparse_vec;
-- (After DROP, the lexical+dense RRF in 003 resumes unchanged.)
