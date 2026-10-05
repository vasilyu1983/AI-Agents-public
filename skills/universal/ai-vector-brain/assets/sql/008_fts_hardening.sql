-- 008_fts_hardening.sql
-- Supersedes the v1 chunks.fts_vector (defined in 001_schema.sql) and its GIN
-- index (002_indexes_hnsw.sql) with a weighted, unaccent-aware lexical vector.
--
-- WHY: the v1 column used a single 'english' config with no setweight, so
-- (a) section/title and body rank equally, (b) accented and exact-identifier
-- tokens are lost to stemming. See references/postgres-fts-tuning.md.
--
-- !! OPERATIONAL WARNING !!
-- Dropping and re-adding a STORED generated column REWRITES the chunks table
-- and takes an ACCESS EXCLUSIVE lock for the duration. On large tables run in a
-- maintenance window, OR use the online parallel-column variant documented in
-- references/postgres-fts-tuning.md ("fts_vector lifecycle" recipe).
--
-- CONCURRENTLY note: CREATE INDEX CONCURRENTLY cannot run inside a transaction
-- block. This file is written to run OUTSIDE an explicit transaction (psql -f
-- without BEGIN/COMMIT). Do not wrap it in BEGIN/COMMIT.
--
-- !! QUERY-SIDE CONFIG MUST MATCH !!
-- After this migration the column is built with vb_unaccent_english /
-- vb_unaccent_simple. A query still using websearch_to_tsquery('english', ...)
-- does NOT unaccent query terms, so accented queries (e.g. 'Muller' vs
-- 'Mueller'/'Müller') silently under-match -- the OPPOSITE of this migration's
-- goal. Pass p_fts_config => 'vb_unaccent_english' to hybrid_retrieve_context
-- (see 003_hybrid_search_function.sql) and references/postgres-fts-tuning.md.
-- The 'english' DEFAULT in 003 is retained only for backward compatibility and
-- does NOT realize this migration's benefit.
--
-- Load order: after 002_indexes_hnsw.sql, before/with 003. Idempotent where
-- Postgres allows; the column drop/add is not idempotent (guarded by IF EXISTS).

-- ---------------------------------------------------------------------------
-- UP
-- ---------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS unaccent;

-- Immutable, constant-named config -> legal inside a generated column.
-- 'english' stem keeps recall; 'unaccent' folds diacritics before stemming.
DROP TEXT SEARCH CONFIGURATION IF EXISTS vb_unaccent_english;
CREATE TEXT SEARCH CONFIGURATION vb_unaccent_english (COPY = english);
ALTER TEXT SEARCH CONFIGURATION vb_unaccent_english
  ALTER MAPPING FOR hword, hword_part, word
  WITH unaccent, english_stem;

-- 'simple' + unaccent: no stemming. Applied below to the full
-- section_path+content body (not only identifier columns) so exact
-- identifiers, codes, SKUs, and proper nouns embedded in prose survive --
-- english_stem would destroy them. Tradeoff: this roughly doubles weight-A
-- body lexeme volume; that is the accepted cost of full-text exact-token
-- recall (see failure mode 1 in references/postgres-fts-tuning.md).
DROP TEXT SEARCH CONFIGURATION IF EXISTS vb_unaccent_simple;
CREATE TEXT SEARCH CONFIGURATION vb_unaccent_simple (COPY = simple);
ALTER TEXT SEARCH CONFIGURATION vb_unaccent_simple
  ALTER MAPPING FOR hword, hword_part, word
  WITH unaccent, simple;

DROP INDEX IF EXISTS idx_chunks_fts;
ALTER TABLE chunks DROP COLUMN IF EXISTS fts_vector;

-- Weights: A = section_path (navigational title signal) + exact-token layer,
-- B = contextual_summary, C = content body.
ALTER TABLE chunks ADD COLUMN fts_vector TSVECTOR GENERATED ALWAYS AS (
  setweight(to_tsvector('vb_unaccent_english', coalesce(section_path, '')), 'A')
  || setweight(to_tsvector('vb_unaccent_simple', coalesce(section_path, '') || ' ' || coalesce(content, '')), 'A')
  || setweight(to_tsvector('vb_unaccent_english', coalesce(contextual_summary, '')), 'B')
  || setweight(to_tsvector('vb_unaccent_english', coalesce(content, '')), 'C')
) STORED;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunks_fts
  ON chunks USING GIN (fts_vector);

-- Optional: typo-tolerant fallback for exact identifiers/codes. Apply trgm GIN
-- to the identifier-bearing column only (NOT full body -- trgm GIN bloats on
-- long text). symbol_name is the repo-brain identifier column from 001.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_chunks_symbol_trgm
  ON chunks USING GIN (symbol_name gin_trgm_ops)
  WHERE symbol_name IS NOT NULL;

-- ---------------------------------------------------------------------------
-- Per-row language variant (commented; use instead of the generated column
-- above when chunks.language varies per row and you need per-row configs).
-- A generated column cannot pick its regconfig from another column, so the
-- per-row path requires a trigger:
--
-- ALTER TABLE chunks DROP COLUMN IF EXISTS fts_vector;
-- ALTER TABLE chunks ADD COLUMN fts_vector TSVECTOR;
-- CREATE OR REPLACE FUNCTION chunks_fts_refresh() RETURNS trigger AS $$
-- BEGIN
--   NEW.fts_vector :=
--     setweight(to_tsvector(NEW.language::regconfig, coalesce(NEW.section_path,'')), 'A')
--     || setweight(to_tsvector('vb_unaccent_simple', coalesce(NEW.content,'')), 'A')
--     || setweight(to_tsvector(NEW.language::regconfig, coalesce(NEW.contextual_summary,'')), 'B')
--     || setweight(to_tsvector(NEW.language::regconfig, coalesce(NEW.content,'')), 'C');
--   RETURN NEW;
-- END $$ LANGUAGE plpgsql;
-- CREATE TRIGGER trg_chunks_fts BEFORE INSERT OR UPDATE ON chunks
--   FOR EACH ROW EXECUTE FUNCTION chunks_fts_refresh();
-- (chunks.language stores e.g. 'english'/'simple'; map app codes to regconfig.)
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- Advanced index lever (commented): RUM stores positions/rank IN the index.
-- Use when read-heavy + phrase-heavy + rank-critical, or ORDER BY ts+timestamp.
-- Tradeoff: slower build/insert than GIN. Third-party
-- (github.com/postgrespro/rum) -- the extension build MUST match your PG major.
-- Verify the release supports your PG version before relying on it.
--
-- CREATE EXTENSION IF NOT EXISTS rum;
-- DROP INDEX IF EXISTS idx_chunks_fts;
-- CREATE INDEX idx_chunks_fts ON chunks USING rum (fts_vector rum_tsvector_ops);
-- ---------------------------------------------------------------------------

-- ---------------------------------------------------------------------------
-- DOWN  (restores the exact 001_schema.sql + 002_indexes_hnsw.sql state)
-- ---------------------------------------------------------------------------
-- DROP INDEX IF EXISTS idx_chunks_symbol_trgm;
-- DROP INDEX IF EXISTS idx_chunks_fts;
-- ALTER TABLE chunks DROP COLUMN IF EXISTS fts_vector;
-- ALTER TABLE chunks ADD COLUMN fts_vector TSVECTOR GENERATED ALWAYS AS (
--   to_tsvector('english', coalesce(contextual_summary, '') || ' ' || content)
-- ) STORED;
-- CREATE INDEX IF NOT EXISTS idx_chunks_fts ON chunks USING GIN (fts_vector);
-- DROP TEXT SEARCH CONFIGURATION IF EXISTS vb_unaccent_english;
-- DROP TEXT SEARCH CONFIGURATION IF EXISTS vb_unaccent_simple;
-- (unaccent/pg_trgm extensions left installed; harmless. DROP EXTENSION only
--  if nothing else uses them.)
