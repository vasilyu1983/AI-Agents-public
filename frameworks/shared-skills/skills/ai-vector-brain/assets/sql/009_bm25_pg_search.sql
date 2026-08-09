-- 009_bm25_pg_search.sql
-- Alternative lexical leg: ParadeDB pg_search BM25 index on chunks.
--
-- WHY: ts_rank / ts_rank_cd have no IDF and no document-length saturation,
-- so relevance ORDER BY degrades on large tables and rewards keyword stuffing.
-- When evals reveal that failure mode, swap the lexical CTE in
-- 003_hybrid_search_function.sql to this BM25 path.  See the commented patch
-- block at the bottom of this file.
--
-- SELECTION CRITERION: adopt ONLY when ts_rank ORDER BY fails evals
-- (recall/MRR on the labeled eval set).  The tsvector leg in 008 is simpler,
-- has zero extra dependency, and is sufficient for most repo/docs/compliance
-- brains.  See references/bm25-when-ts_rank-isnt-enough.md.
--
-- PREREQUISITE: ParadeDB pg_search extension installed.
--   Debian/Ubuntu: apt install postgresql-{PG_MAJOR}-pg-search
--   Or install from https://github.com/paradedb/paradedb
--
-- CONCURRENCY: CREATE INDEX USING bm25 does not support CONCURRENTLY.
-- Run in a maintenance window or use a migration slot.
--
-- INVARIANT: only ONE BM25 index per table is allowed by pg_search.
-- Drop any existing BM25 index before running UP.
--
-- Load order: after 001_schema.sql.  Independent of 008_fts_hardening.sql
-- (the two lexical legs are alternatives, not complements).
--
-- SQL not executed (no local Postgres); structural checks only.

-- ---------------------------------------------------------------------------
-- UP  — create pg_search BM25 index on chunks
-- ---------------------------------------------------------------------------

-- Only one BM25 index per table is permitted.  Drop any prior one first.
DROP INDEX IF EXISTS idx_chunks_bm25;

-- USING bm25: pg_search index type, Tantivy-backed, real Okapi BM25 scoring.
-- key_field must be the UNIQUE primary key column (un-tokenised).
-- Include every column that the lexical leg needs to score and retrieve.
CREATE INDEX idx_chunks_bm25
  ON chunks
  USING bm25 (
    id,            -- key_field: must be unique, listed first
    content,
    contextual_summary,
    section_path,
    doc_type,
    symbol_name
  )
  WITH (key_field = 'id');

-- ---------------------------------------------------------------------------
-- How to swap the lexical CTE in 003_hybrid_search_function.sql
-- (do NOT edit 003 here; this is a pointer-only comment block)
--
-- Current 003 lexical CTE (tsvector path):
--
--   lexical AS (
--     SELECT id AS chunk_id,
--            ROW_NUMBER() OVER (ORDER BY ts_rank_cd(fts_vector,
--              websearch_to_tsquery(p_fts_config, query_text)) DESC) AS rank_pos
--     FROM   chunks
--     WHERE  fts_vector @@ websearch_to_tsquery(p_fts_config, query_text)
--     ...
--     LIMIT  candidate_count
--   )
--
-- BM25 replacement CTE (pg_search path):
--
--   lexical AS (
--     SELECT id AS chunk_id,
--            ROW_NUMBER() OVER (ORDER BY pdb.score(id) DESC) AS rank_pos
--     FROM   chunks
--     WHERE  content ||| query_text
--     AND  <copy the p_doc_type / p_authority / p_as_of / p_acl_scope filter block from 003 unchanged>
--     LIMIT  candidate_count
--   )
--
-- Notes:
--   • pdb.score(id) returns the true BM25 score; RRF downstream ignores
--     the raw value and consumes rank position only, so no score calibration
--     is needed when fusing with the vector CTE.
--   • The ||| match-disjunction operator tokenizes query_text with the field's
--     tokenizer and avoids Tantivy query-string parsing from user input. For
--     exact phrases, use the ### phrase operator with a bound text value or
--     token array; avoid string-concatenating raw user text into pdb.parse().
--   • The p_fts_config parameter is unused in the BM25 path; leave the
--     function signature unchanged for call-site compatibility.
--   • If 008_fts_hardening.sql is installed, DROP the GIN index
--     (idx_chunks_fts) before benchmarking; both indexes scan on the same
--     column and having both adds write overhead without benefit on one leg.
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- DOWN  (restores to the tsvector-only lexical leg; 008 handles that index)
-- ---------------------------------------------------------------------------
-- DROP INDEX IF EXISTS idx_chunks_bm25;
-- (After DROP, 003's tsvector CTE resumes using idx_chunks_fts from 008.
--  No schema changes needed; the BM25 index is purely additive.)
