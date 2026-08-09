-- Hybrid lexical + vector search with reciprocal-rank fusion.
--
-- All filter parameters are optional (NULL means "no filter on this dimension").
-- Filters are applied inside both CTEs so they constrain the candidate pool
-- BEFORE fusion -- required for correct ACL/authority/effective-time semantics.
--
-- ACL semantics: a chunk is visible when its `acl_scope` is the empty object
-- (public) OR shares at least one key with `p_acl_scope`. Adapt to your tenancy
-- model if you store ACL differently.
--
-- Effective-time semantics: a chunk is in scope when its document's
-- [effective_from, effective_to] window contains `p_as_of`, OR the document has
-- no effective dates set (treated as always-effective).

-- Adding p_fts_config changes this function's argument-type identity. A bare
-- CREATE OR REPLACE would NOT replace the prior 13-argument version -- it would
-- leave that old overload alive, so 13-positional-arg callers would silently
-- keep the hardcoded 'english' path and never benefit from this migration.
-- Drop the prior signature explicitly first (no-op on a fresh install). No
-- CASCADE: if an unexpected dependency exists, fail loud instead of silently
-- dropping it.
DROP FUNCTION IF EXISTS hybrid_retrieve_context(
  TEXT, vector, TEXT, INTEGER, INTEGER, DOUBLE PRECISION,
  TEXT[], TEXT[], TEXT, TEXT[], JSONB, TIMESTAMPTZ, TEXT[]
);

CREATE OR REPLACE FUNCTION hybrid_retrieve_context(
  query_text         TEXT,
  -- Must match embeddings.embedding in 001_schema.sql.
  query_embedding    vector(1024),
  embedding_model    TEXT,
  match_count        INTEGER DEFAULT 20,
  candidate_count    INTEGER DEFAULT 50,
  rrf_k              DOUBLE PRECISION DEFAULT 60.0,
  -- Optional filters. NULL on any of these means unfiltered on that dimension.
  p_doc_type             TEXT[]      DEFAULT NULL,
  p_authority            TEXT[]      DEFAULT NULL,
  p_language             TEXT        DEFAULT NULL,
  p_source_path_prefix   TEXT[]      DEFAULT NULL,
  p_acl_scope            JSONB       DEFAULT NULL,
  p_as_of                TIMESTAMPTZ DEFAULT NULL,
  p_unit_type            TEXT[]      DEFAULT NULL,
  -- FTS text-search config. Default 'english' keeps existing callers working.
  -- Pass 'vb_unaccent_english' (see 008_fts_hardening.sql) or a per-language
  -- regconfig to match the column's config. RRF already normalizes rank
  -- position -- do not over-tune ts_rank normalization flags pre-fusion.
  p_fts_config           REGCONFIG   DEFAULT 'english'
)
RETURNS TABLE (
  chunk_id           BIGINT,
  evidence_id        TEXT,
  content            TEXT,
  contextual_summary TEXT,
  source_uri         TEXT,
  source_path        TEXT,
  section_path       TEXT,
  citation_anchor    TEXT,
  authority          TEXT,
  effective_from     TIMESTAMPTZ,
  effective_to       TIMESTAMPTZ,
  rrf_score          DOUBLE PRECISION
)
LANGUAGE SQL
STABLE
AS $$
WITH
filtered AS (
  SELECT c.id, c.document_id
  FROM chunks c
  JOIN documents d ON d.id = c.document_id
  WHERE (p_doc_type           IS NULL OR c.doc_type = ANY(p_doc_type))
    AND (p_authority          IS NULL OR c.authority = ANY(p_authority))
    AND (p_language           IS NULL OR c.language = p_language)
    AND (p_unit_type          IS NULL OR c.unit_type = ANY(p_unit_type))
    AND (p_source_path_prefix IS NULL
         OR EXISTS (
           SELECT 1 FROM unnest(p_source_path_prefix) prefix
           WHERE d.source_path LIKE prefix || '%'
         ))
    AND (p_acl_scope IS NULL
         OR c.acl_scope = '{}'::jsonb
         OR c.acl_scope ?| (SELECT array_agg(k) FROM jsonb_object_keys(p_acl_scope) k))
    AND (p_as_of IS NULL
         OR (
           (d.effective_from IS NULL OR d.effective_from <= p_as_of)
           AND (d.effective_to IS NULL OR d.effective_to >= p_as_of)
         ))
),
semantic AS (
  SELECT f.id,
         row_number() OVER (ORDER BY e.embedding <=> query_embedding) AS rank
  FROM   filtered f
  JOIN   embeddings e ON e.chunk_id = f.id
  WHERE  e.model_id = embedding_model
  ORDER  BY e.embedding <=> query_embedding
  LIMIT  candidate_count
),
lexical AS (
  SELECT f.id,
         row_number() OVER (
           ORDER BY ts_rank_cd(c.fts_vector, websearch_to_tsquery(p_fts_config, query_text)) DESC
         ) AS rank
  FROM   filtered f
  JOIN   chunks c ON c.id = f.id
  WHERE  c.fts_vector @@ websearch_to_tsquery(p_fts_config, query_text)
  ORDER  BY ts_rank_cd(c.fts_vector, websearch_to_tsquery(p_fts_config, query_text)) DESC
  LIMIT  candidate_count
),
fused AS (
  SELECT id, sum(1.0 / (rrf_k + rank)) AS rrf_score
  FROM (
    SELECT id, rank FROM semantic
    UNION ALL
    SELECT id, rank FROM lexical
  ) candidates
  GROUP BY id
)
SELECT c.id,
       c.evidence_id,
       c.content,
       c.contextual_summary,
       d.source_uri,
       d.source_path,
       c.section_path,
       c.citation_anchor,
       c.authority,
       d.effective_from,
       d.effective_to,
       f.rrf_score
FROM   fused f
JOIN   chunks c   ON c.id = f.id
JOIN   documents d ON d.id = c.document_id
ORDER  BY f.rrf_score DESC
LIMIT  match_count;
$$;
