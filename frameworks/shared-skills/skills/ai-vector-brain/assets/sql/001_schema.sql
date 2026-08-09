-- Core schema for a Postgres + pgvector vector brain.
-- Load after enabling the vector extension in the target database.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS documents (
  id BIGSERIAL PRIMARY KEY,
  source_id TEXT NOT NULL,
  source_uri TEXT NOT NULL,
  source_path TEXT,
  title TEXT,
  doc_type TEXT NOT NULL,
  language TEXT NOT NULL DEFAULT 'en',
  version_or_commit TEXT,
  content_hash TEXT NOT NULL,
  authority TEXT,
  effective_from TIMESTAMPTZ,
  effective_to TIMESTAMPTZ,
  acl_scope JSONB NOT NULL DEFAULT '{}'::jsonb,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  ingested_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (source_uri, content_hash)
);

CREATE TABLE IF NOT EXISTS chunks (
  id BIGSERIAL PRIMARY KEY,
  document_id BIGINT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
  chunk_index INTEGER NOT NULL,
  content TEXT NOT NULL,
  contextual_summary TEXT,
  token_count INTEGER NOT NULL,
  section_path TEXT,
  -- anchor: stable heading slug or symbol/line anchor, produced by the chunker.
  -- citation_anchor: the human-presentable compound anchor used in citations
  -- (e.g. 'docs/ops/runbook.md#restart-procedure').
  anchor TEXT,
  citation_anchor TEXT,
  -- symbol_name: function/class/method name when known (repo brain).
  symbol_name TEXT,
  -- unit_type: discriminates retrieval-unit kinds defined in framework.md.
  unit_type TEXT NOT NULL DEFAULT 'chunk'
    CHECK (unit_type IN ('chunk', 'parent', 'knowledge_packet', 'compiled_page')),
  parent_chunk_id BIGINT REFERENCES chunks(id),
  doc_type TEXT NOT NULL,
  language TEXT NOT NULL DEFAULT 'en',
  authority TEXT,
  acl_scope JSONB NOT NULL DEFAULT '{}'::jsonb,
  content_hash TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  -- v1 baseline lexical vector. 008_fts_hardening.sql supersedes this with a
  -- weighted, unaccent-aware definition (reversible). See
  -- references/postgres-fts-tuning.md.
  fts_vector TSVECTOR GENERATED ALWAYS AS (
    to_tsvector('english', coalesce(contextual_summary, '') || ' ' || content)
  ) STORED,
  -- evidence_id is the stable string identifier returned by the agent tool
  -- contract. Convention: 'chunk_' || id::text. Generated, immutable.
  evidence_id TEXT GENERATED ALWAYS AS ('chunk_' || id::text) STORED,
  UNIQUE (document_id, chunk_index)
);

CREATE TABLE IF NOT EXISTS embeddings (
  id BIGSERIAL PRIMARY KEY,
  chunk_id BIGINT NOT NULL REFERENCES chunks(id) ON DELETE CASCADE,
  model_id TEXT NOT NULL,
  -- V1 assets default to 1024 dimensions. If you choose another embedding
  -- dimension, update every vector(N)/bit(N) occurrence in 003, 005, and 011
  -- before loading data.
  embedding vector(1024) NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (chunk_id, model_id)
);
