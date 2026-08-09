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

CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw
  ON embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Per-session tuning recommended in callers (do not set here; this is DDL):
--   SET LOCAL hnsw.ef_search = 100;
--   SET LOCAL hnsw.iterative_scan = 'relaxed_order';   -- pgvector >= 0.8
--   SET LOCAL hnsw.max_scan_tuples = 20000;

