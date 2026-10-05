-- Indexes for the default pgvector implementation.
--
-- Tuning notes (verify against your installed pgvector version before relying):
--   * pgvector >= 0.8 supports `hnsw.iterative_scan = 'relaxed_order'` to
--     preserve recall under selective WHERE filters. Set per-session, not here.
--   * For embeddings > 2000 dims, store as `halfvec(N)` (pgvector >= 0.7) and
--     change the HNSW operator class to `halfvec_cosine_ops`.
--   * Raise `ef_construction` to 128 only when recall@10 < 0.85 in eval and
--     the longer build time is acceptable.

CREATE INDEX IF NOT EXISTS idx_documents_source
  ON documents (source_id, doc_type);

CREATE INDEX IF NOT EXISTS idx_documents_effective
  ON documents (effective_from, effective_to)
  WHERE effective_from IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_chunks_document
  ON chunks (document_id, chunk_index);

CREATE INDEX IF NOT EXISTS idx_chunks_doc_type
  ON chunks (doc_type);

CREATE INDEX IF NOT EXISTS idx_chunks_authority
  ON chunks (authority)
  WHERE authority IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_chunks_unit_type
  ON chunks (unit_type);

CREATE INDEX IF NOT EXISTS idx_chunks_fts
  ON chunks USING GIN (fts_vector);

CREATE INDEX IF NOT EXISTS idx_chunks_acl_scope
  ON chunks USING GIN (acl_scope);

CREATE INDEX IF NOT EXISTS idx_embeddings_model
  ON embeddings (model_id);

-- One partial HNSW index per active model_id. Vectors from different models
-- live in different spaces; one index across all model_ids makes the graph
-- walk return neighbours from the wrong model, and 003's
-- `e.model_id = embedding_model` filter then discards them after the scan, so
-- recall drops while two models coexist (the migration window).
-- Apply with the active model id (the `<provider>:<model>` string that
-- scripts/embed_and_load.py writes to embeddings.model_id):
--   psql -v model_id='<provider>:<model>' -f 002_indexes_hnsw.sql
-- An unset variable is a syntax error, so the file fails loud instead of
-- building an index that matches no rows.
-- Upgrading an install that already has the older non-partial
-- idx_embeddings_hnsw: IF NOT EXISTS skips this statement and keeps the old
-- index. Build the partial one CONCURRENTLY under a new name, then drop the
-- old one CONCURRENTLY.
-- A second model gets its own partial index during a migration: see
-- references/production-runbook.md, Embedding Model Migration Playbook, step 2.
-- 003 is a single-SELECT SQL function, so Postgres inlines it and sees the
-- model id as a constant when the caller passes a literal or the plan is a
-- custom plan; that is what lets the planner match this partial index. Under
-- a generic plan (plan_cache_mode = force_generic_plan, or a prepared
-- statement that switched to one) it cannot, and falls back to an exact scan
-- of that model's rows: correct, but slower. Confirm with EXPLAIN.
CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw
  ON embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE model_id = :'model_id';

-- Per-session tuning recommended in callers (do not set here; this is DDL):
--   SET LOCAL hnsw.ef_search = 100;
--   SET LOCAL hnsw.iterative_scan = 'relaxed_order';   -- pgvector >= 0.8
--   SET LOCAL hnsw.max_scan_tuples = 20000;

