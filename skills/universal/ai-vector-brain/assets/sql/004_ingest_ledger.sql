-- Ingest ledger and corpus-version tracking.

CREATE TABLE IF NOT EXISTS corpus_versions (
  id TEXT PRIMARY KEY,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  source_summary JSONB NOT NULL DEFAULT '{}'::jsonb,
  notes TEXT
);

CREATE TABLE IF NOT EXISTS ingest_runs (
  id BIGSERIAL PRIMARY KEY,
  corpus_version_id TEXT REFERENCES corpus_versions(id),
  source_id TEXT NOT NULL,
  ingest_mode TEXT NOT NULL,
  from_version TEXT,
  to_version TEXT,
  status TEXT NOT NULL CHECK (status IN ('running', 'ok', 'failed', 'rolled_back')),
  stats JSONB NOT NULL DEFAULT '{}'::jsonb,
  error TEXT,
  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  finished_at TIMESTAMPTZ
);

ALTER TABLE documents
  ADD COLUMN IF NOT EXISTS invalidated_at TIMESTAMPTZ,
  ADD COLUMN IF NOT EXISTS valid_from_corpus_version TEXT,
  ADD COLUMN IF NOT EXISTS valid_to_corpus_version TEXT;

CREATE INDEX IF NOT EXISTS idx_ingest_runs_source_status
  ON ingest_runs (source_id, status, started_at DESC);

CREATE INDEX IF NOT EXISTS idx_documents_live
  ON documents (source_id, source_path)
  WHERE invalidated_at IS NULL;

