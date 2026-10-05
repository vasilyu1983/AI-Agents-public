-- Query logging and retrieval observability.
--
-- Capture every retrieval call to support drift detection, no-evidence rate
-- monitoring, latency tracking, and offline eval replay. Keep separate from
-- ingest_runs (operational ingest) and eval_runs (labeled eval).
--
-- High-volume deployments: shard by month with declarative partitioning, or
-- ship to a log warehouse and prune the OLTP table on a 30-day window.

CREATE TABLE IF NOT EXISTS query_logs (
  id BIGSERIAL PRIMARY KEY,
  corpus_version_id TEXT REFERENCES corpus_versions(id),
  tenant_id TEXT,
  query_text TEXT NOT NULL,
  query_text_hash TEXT GENERATED ALWAYS AS (md5(query_text)) STORED,
  embedding_model TEXT NOT NULL,
  retrieval_method TEXT NOT NULL,           -- 'hybrid_rrf' | 'hybrid_rrf+rerank' | 'vector_only'
  filters JSONB NOT NULL DEFAULT '{}'::jsonb,
  top_k INTEGER NOT NULL,
  candidates INTEGER,
  result_count INTEGER NOT NULL,
  no_evidence BOOLEAN NOT NULL,
  top_score DOUBLE PRECISION,
  rerank_top_score DOUBLE PRECISION,
  evidence_ids TEXT[] NOT NULL DEFAULT '{}',
  latency_ms INTEGER NOT NULL,
  cache_hit BOOLEAN NOT NULL DEFAULT FALSE,
  agent_id TEXT,
  session_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_query_logs_created
  ON query_logs (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_query_logs_no_evidence
  ON query_logs (created_at DESC) WHERE no_evidence;

CREATE INDEX IF NOT EXISTS idx_query_logs_corpus_version
  ON query_logs (corpus_version_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_query_logs_hash
  ON query_logs (query_text_hash);

-- Suggested observability views. Wire to Grafana / Metabase / Looker.

CREATE OR REPLACE VIEW retrieval_health_hourly AS
SELECT
  date_trunc('hour', created_at)           AS bucket,
  corpus_version_id,
  count(*)                                 AS n_queries,
  avg(latency_ms)::INTEGER                 AS avg_latency_ms,
  percentile_disc(0.95) WITHIN GROUP (ORDER BY latency_ms) AS p95_latency_ms,
  avg(CASE WHEN no_evidence THEN 1 ELSE 0 END)::NUMERIC(5,3) AS no_evidence_rate,
  avg(CASE WHEN cache_hit   THEN 1 ELSE 0 END)::NUMERIC(5,3) AS cache_hit_rate,
  avg(result_count)::NUMERIC(5,2)          AS avg_results
FROM query_logs
GROUP BY 1, 2
ORDER BY 1 DESC;

CREATE OR REPLACE VIEW top_zero_evidence_queries AS
SELECT
  query_text,
  count(*)                                 AS occurrences,
  max(created_at)                          AS last_seen
FROM query_logs
WHERE no_evidence
  AND created_at > now() - INTERVAL '7 days'
GROUP BY query_text
ORDER BY occurrences DESC
LIMIT 100;

-- Suggested SLO alerts (implement in your alerting stack, not in SQL):
--   no_evidence_rate (hourly)         > 0.15 for 2 consecutive buckets
--   p95_latency_ms (hourly)           > corpus-specific budget for 2 buckets
--   avg(rerank_top_score) drop        > 20% versus 7-day baseline
--   cache_hit_rate                    sudden drop -> corpus version churn or invalidation bug
