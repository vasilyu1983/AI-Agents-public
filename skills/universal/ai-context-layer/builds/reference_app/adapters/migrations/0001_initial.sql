-- ai-context-layer reference app — initial schema (Phase 2)
--
-- Bi-temporal LearnedMemory, append-only EpisodeLog, pgvector-backed
-- KnowledgeSource + KnowledgeChunk. Every row carries owner_scope so A10
-- (no ACL/tenant scope on memory) is impossible to construct accidentally.
--
-- Vector dim default is 1536 (OpenAI text-embedding-3-small). If you use a
-- different model, change the column type before applying. Phase 5 cookbook
-- (`embedding-model migration`) covers re-embedding.

CREATE EXTENSION IF NOT EXISTS vector;

-- -----------------------------------------------------------------------------
-- Episode log: append-only spine. Every LearnedMemory.source_episode_id
-- points here. NEVER truncate. The audit trail dies if you do.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS episode_log (
    id           text PRIMARY KEY,
    episode      jsonb NOT NULL,
    owner_scope  jsonb NOT NULL,
    appended_at  timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS episode_log_owner_idx
    ON episode_log USING gin (owner_scope);


-- -----------------------------------------------------------------------------
-- LearnedMemory: bi-temporal, non-destructive.
--   * fact time:   valid_from / valid_to  (when the claim was true in the world)
--   * system time: created_at / invalidated_at  (when we learned or corrected)
--   * supersedes_id chains corrections so you can ask "when did we first
--     believe X" without losing history. Hard delete is forbidden.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS learned_memory (
    id                 text PRIMARY KEY,
    entity_id          text NOT NULL,
    entity_type        text NOT NULL,
    memory_type        text NOT NULL,
    value              jsonb NOT NULL,
    source             text NOT NULL,
    source_episode_id  text NOT NULL REFERENCES episode_log(id),
    confidence         double precision NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    created_at         timestamptz NOT NULL DEFAULT now(),
    updated_at         timestamptz NOT NULL DEFAULT now(),
    valid_from         timestamptz,
    valid_to           timestamptz,
    invalidated_at     timestamptz,    -- system-time supersession (A3 blocker)
    expires_at         timestamptz,    -- TTL, distinct from supersession
    supersedes_id      text REFERENCES learned_memory(id),
    owner_scope        jsonb NOT NULL,
    inferred           boolean NOT NULL,
    tags               text[] NOT NULL DEFAULT '{}'
);
CREATE INDEX IF NOT EXISTS learned_memory_entity_idx
    ON learned_memory (entity_id, memory_type);
CREATE INDEX IF NOT EXISTS learned_memory_owner_idx
    ON learned_memory USING gin (owner_scope);
-- Hot-path partial index: most reads ask for active rows only.
CREATE INDEX IF NOT EXISTS learned_memory_active_idx
    ON learned_memory (entity_id, memory_type)
    WHERE invalidated_at IS NULL;


-- -----------------------------------------------------------------------------
-- KnowledgeSource: registered documents/pages/etc. content_hash drives change
-- detection — re-embed only when hash changes, not on every nightly job.
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_source (
    id            text PRIMARY KEY,
    uri           text NOT NULL,
    title         text NOT NULL,
    content_hash  text NOT NULL,
    owner_scope   jsonb NOT NULL,
    indexed_at    timestamptz NOT NULL DEFAULT now(),
    last_seen_at  timestamptz NOT NULL DEFAULT now(),
    metadata      jsonb NOT NULL DEFAULT '{}'::jsonb
);
CREATE INDEX IF NOT EXISTS knowledge_source_owner_idx
    ON knowledge_source USING gin (owner_scope);


-- -----------------------------------------------------------------------------
-- KnowledgeChunk: embedded slices for retrieval. ON DELETE CASCADE so source
-- removal cleans up chunks. owner_scope is duplicated here so retrieval
-- can filter without joining (hot path).
-- -----------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS knowledge_chunk (
    id           text PRIMARY KEY,
    source_id    text NOT NULL REFERENCES knowledge_source(id) ON DELETE CASCADE,
    chunk_index  integer NOT NULL,
    snippet      text NOT NULL,
    embedding    vector,
    metadata     jsonb NOT NULL DEFAULT '{}'::jsonb,
    owner_scope  jsonb NOT NULL,
    indexed_at   timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS knowledge_chunk_source_idx
    ON knowledge_chunk (source_id);
CREATE INDEX IF NOT EXISTS knowledge_chunk_owner_idx
    ON knowledge_chunk USING gin (owner_scope);
-- Vector index for retrieval.
-- Operational tuning (HNSW vs IVFFlat vs pgvectorscale, m/ef_construction/ef_search,
-- iterative_scan for filtered queries, halfvec for >2000 dims, model migration via
-- model_id) lives in `skills/universal/ai-vector-brain/`. This
-- reference app uses HNSW with conservative defaults; for production brains, use
-- the canonical schema and DDL at:
--   ai-vector-brain/assets/sql/001_schema.sql
--   ai-vector-brain/assets/sql/002_indexes_hnsw.sql
CREATE INDEX IF NOT EXISTS knowledge_chunk_embedding_idx
    ON knowledge_chunk USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
