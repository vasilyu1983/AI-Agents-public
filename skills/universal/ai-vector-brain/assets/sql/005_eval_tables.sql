-- Query logs and retrieval eval tables.

CREATE TABLE IF NOT EXISTS query_logs (
  id BIGSERIAL PRIMARY KEY,
  corpus_version_id TEXT REFERENCES corpus_versions(id),
  query_text TEXT NOT NULL,
  query_embedding vector(1024),
  filters JSONB NOT NULL DEFAULT '{}'::jsonb,
  retrieved_chunk_ids BIGINT[] NOT NULL DEFAULT '{}',
  user_feedback SMALLINT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS eval_queries (
  id TEXT PRIMARY KEY,
  corpus_type TEXT NOT NULL,
  query_text TEXT NOT NULL,
  metric_focus TEXT NOT NULL,
  expected_chunk_ids BIGINT[] NOT NULL DEFAULT '{}',
  expected_paths TEXT[] NOT NULL DEFAULT '{}',
  as_of TIMESTAMPTZ,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS eval_runs (
  id BIGSERIAL PRIMARY KEY,
  corpus_version_id TEXT REFERENCES corpus_versions(id),
  eval_set TEXT NOT NULL,
  backend TEXT NOT NULL,
  embedding_model TEXT,
  metrics JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

