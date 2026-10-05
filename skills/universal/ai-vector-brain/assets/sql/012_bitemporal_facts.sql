-- 012_bitemporal_facts.sql
-- Bitemporal state facts: "who owns X now", "who owned X at t", and
-- "what did we believe at k about time t", next to the chunk store.
--
-- Vocabulary (canonical across the library; map other engines with the table
-- in references/postgres-pgvector-default.md#bitemporal-state-facts):
--   valid time        [valid_from, valid_to)        when the fact held; NULL valid_to = still holds
--   transaction time  [recorded_at, superseded_at)  when we believed it; NULL superseded_at = current belief
--   provenance        source_id, source_span        the episode/event/document and the locator inside it
--   identity          entity_id                     stable ID, never a display name
--
-- Rules the DDL enforces:
--   * no two current beliefs for one (entity_id, attribute) overlap in valid time;
--   * a row is never updated except to set superseded_at; corrections insert new rows;
--   * an explicitly cleared field is a row whose value is JSON null; no row means unknown;
--   * a lower-authority source never supersedes a higher-authority current belief:
--     the assertion is held in fact_candidates for review instead.
--
-- Load order: independent of 001-011 (no FK into documents/chunks; join on
-- source_id when the source is an ingested document).
--
-- Executed 2026-10-02 on PGlite 0.3.16 (Postgres compiled to WASM) with
-- btree_gist: the whole file twice (idempotent), every ACCEPTANCE line below,
-- the known-at replay, a split inside a closed row, the overlap rejection, the
-- erasure recipe exactly as written, and value_references on nested and
-- near-miss IDs. Not tested on server Postgres or managed providers; the
-- advisory lock is reasoned, not load-tested.

-- ---------------------------------------------------------------------------
-- UP
-- ---------------------------------------------------------------------------

CREATE EXTENSION IF NOT EXISTS btree_gist;  -- scalar "=" inside the GiST EXCLUDE

CREATE TABLE IF NOT EXISTS entities (
  entity_id   TEXT PRIMARY KEY,              -- 'incident:42', 'person:u_812'
  entity_type TEXT NOT NULL
  -- Names are facts (attribute 'name') so a rename keeps the old name
  -- resolvable as of its period and never creates a second entity.
);

-- Idempotency ledger: a redelivered upstream event is a no-op.
-- entity_id is the subject the event asserted about, so erasure can find the
-- ledger rows (no FK: the erasure recipe deletes these rows itself).
CREATE TABLE IF NOT EXISTS fact_events (
  event_id   TEXT PRIMARY KEY,
  entity_id  TEXT,
  applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE fact_events ADD COLUMN IF NOT EXISTS entity_id TEXT;  -- upgrade path
CREATE INDEX IF NOT EXISTS idx_fact_events_entity ON fact_events (entity_id);

CREATE TABLE IF NOT EXISTS state_facts (
  fact_id       BIGSERIAL PRIMARY KEY,
  entity_id     TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
  attribute     TEXT NOT NULL,               -- role-specific: 'incident_owner', not 'owner'
  value         JSONB NOT NULL,              -- 'null'::jsonb = explicitly cleared
  valid_from    TIMESTAMPTZ NOT NULL,
  valid_to      TIMESTAMPTZ,
  recorded_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
  superseded_at TIMESTAMPTZ,
  source_id     TEXT NOT NULL,
  source_span   TEXT,                        -- offsets, section anchor, or JSON pointer
  authority     SMALLINT NOT NULL DEFAULT 0, -- source rank; higher = more authoritative
  event_id      TEXT REFERENCES fact_events(event_id),
  CHECK (valid_to IS NULL OR valid_to > valid_from),
  CHECK (superseded_at IS NULL OR superseded_at >= recorded_at),
  CONSTRAINT state_facts_no_overlap EXCLUDE USING gist (
    entity_id WITH =,
    attribute WITH =,
    tstzrange(valid_from, valid_to, '[)') WITH &&
  ) WHERE (superseded_at IS NULL)
);

ALTER TABLE state_facts                      -- upgrade path
  ADD COLUMN IF NOT EXISTS authority SMALLINT NOT NULL DEFAULT 0;

-- Held assertions: a lower-authority source contradicted a higher-authority
-- current belief (P22, source authority reconciliation). Never read by the
-- as-of queries; a reviewer promotes one by re-asserting it with a higher
-- authority, or deletes it.
CREATE TABLE IF NOT EXISTS fact_candidates (
  candidate_id     BIGSERIAL PRIMARY KEY,
  entity_id        TEXT NOT NULL REFERENCES entities(entity_id) ON DELETE CASCADE,
  attribute        TEXT NOT NULL,
  value            JSONB NOT NULL,
  valid_from       TIMESTAMPTZ NOT NULL,
  authority        SMALLINT NOT NULL,
  source_id        TEXT NOT NULL,
  source_span      TEXT,
  event_id         TEXT NOT NULL REFERENCES fact_events(event_id),
  blocked_by       BIGINT NOT NULL,            -- fact_id of the higher-authority row
  held_at          TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_state_facts_current
  ON state_facts (entity_id, attribute, valid_from)
  WHERE superseded_at IS NULL;
CREATE INDEX IF NOT EXISTS idx_state_facts_source ON state_facts (source_id);

-- value_references: true when entity ID p_id appears as an exact JSON string
-- anywhere in p_value (scalar, array element, or nested object field). The
-- erasure recipe uses it to find other entities' facts that point at p_id.
CREATE OR REPLACE FUNCTION value_references(p_value JSONB, p_id TEXT)
RETURNS BOOLEAN LANGUAGE sql IMMUTABLE AS $$
  SELECT jsonb_path_exists(p_value, '$.** ? (@ == $id)', jsonb_build_object('id', p_id))
$$;

-- assert_fact: the only write path. Handles a normal update, a correction at
-- the same valid_from, and an out-of-order backfill with one rule: split the
-- current belief that covers p_valid_from, and end the new fact where the
-- covered belief ended (or where the next known belief starts). If the
-- covering belief has a strictly higher authority, nothing is split: the
-- assertion goes to fact_candidates and the call returns 'held_lower_authority'.
-- Equal or higher authority supersedes as before. p_authority is INTEGER so a
-- bare literal (5) resolves without a cast; it is stored as SMALLINT.
-- Returns: 'duplicate' | 'unchanged' | 'held_lower_authority' | 'current' | 'history'.
-- The earlier 7-argument signature is dropped first so calls stay unambiguous.
DROP FUNCTION IF EXISTS assert_fact(TEXT, TEXT, TEXT, JSONB, TIMESTAMPTZ, TEXT, TEXT);
CREATE OR REPLACE FUNCTION assert_fact(
  p_event_id    TEXT,
  p_entity_id   TEXT,
  p_attribute   TEXT,
  p_value       JSONB,
  p_valid_from  TIMESTAMPTZ,
  p_source_id   TEXT,
  p_source_span TEXT DEFAULT NULL,
  p_authority   INTEGER DEFAULT 0
) RETURNS TEXT
LANGUAGE plpgsql AS $$
DECLARE
  cov     state_facts%ROWTYPE;
  next_vf TIMESTAMPTZ;
BEGIN
  INSERT INTO fact_events (event_id, entity_id) VALUES (p_event_id, p_entity_id)
  ON CONFLICT (event_id) DO NOTHING;
  IF NOT FOUND THEN
    RETURN 'duplicate';
  END IF;

  -- Serialise writers per (entity, attribute); the EXCLUDE is the backstop.
  PERFORM pg_advisory_xact_lock(hashtext(p_entity_id || '|' || p_attribute));

  SELECT * INTO cov FROM state_facts
  WHERE entity_id = p_entity_id AND attribute = p_attribute
    AND superseded_at IS NULL
    AND valid_from <= p_valid_from
    AND (p_valid_from < valid_to OR valid_to IS NULL)
  FOR UPDATE;

  IF FOUND THEN
    IF cov.value = p_value THEN
      RETURN 'unchanged';                    -- same value already holds at t
    END IF;
    IF cov.authority > p_authority THEN      -- stale or secondary source: hold, do not split
      INSERT INTO fact_candidates (entity_id, attribute, value, valid_from, authority,
                                   source_id, source_span, event_id, blocked_by)
      VALUES (p_entity_id, p_attribute, p_value, p_valid_from, p_authority,
              p_source_id, p_source_span, p_event_id, cov.fact_id);
      RETURN 'held_lower_authority';
    END IF;
    UPDATE state_facts SET superseded_at = now() WHERE fact_id = cov.fact_id;
    IF cov.valid_from < p_valid_from THEN    -- keep the earlier part of the old belief
      INSERT INTO state_facts (entity_id, attribute, value, valid_from, valid_to,
                               source_id, source_span, authority, event_id)
      VALUES (cov.entity_id, cov.attribute, cov.value, cov.valid_from, p_valid_from,
              cov.source_id, cov.source_span, cov.authority, cov.event_id);
    END IF;
    next_vf := cov.valid_to;                 -- NULL when cov was the open (current) row
  ELSE                                       -- t precedes everything known, or falls in a gap
    SELECT min(valid_from) INTO next_vf FROM state_facts
    WHERE entity_id = p_entity_id AND attribute = p_attribute
      AND superseded_at IS NULL AND valid_from > p_valid_from;
  END IF;

  INSERT INTO state_facts (entity_id, attribute, value, valid_from, valid_to,
                           source_id, source_span, authority, event_id)
  VALUES (p_entity_id, p_attribute, p_value, p_valid_from, next_vf,
          p_source_id, p_source_span, p_authority, p_event_id);
  RETURN CASE WHEN next_vf IS NULL THEN 'current' ELSE 'history' END;
END;
$$;

-- ---------------------------------------------------------------------------
-- QUERIES (paste-ready; $1 entity_id, $2 attribute, $3 valid time t, $4 known-at k)
-- ---------------------------------------------------------------------------
--
-- As of t (current belief):
--   SELECT value, source_id, source_span FROM state_facts
--   WHERE entity_id = $1 AND attribute = $2 AND superseded_at IS NULL
--     AND valid_from <= $3 AND ($3 < valid_to OR valid_to IS NULL);
--   No row = unknown (abstain). A row with value 'null' = known to be cleared.
--
-- As of t, as known at k (audit replay: what the agent could have answered then):
--   SELECT value, source_id FROM state_facts
--   WHERE entity_id = $1 AND attribute = $2
--     AND recorded_at <= $4 AND (superseded_at IS NULL OR $4 < superseded_at)
--     AND valid_from <= $3 AND ($3 < valid_to OR valid_to IS NULL);
--
-- Erasure ($1 = the erased entity_id) is a hard DELETE of every version
-- (superseded rows still hold the value) of two sets of facts: the entity's own
-- facts, and other entities' facts whose value references it (incident_owner =
-- "person:alice"), matched by value_references(value, $1). Values must hold
-- IDs, not display names (names are facts on the entity and go with it); free
-- text that mentions the ID is not matched. A deleted reference leaves that
-- period unknown (abstain), not reassigned. Run in one transaction, in this
-- order (state_facts and fact_candidates reference fact_events):
--   BEGIN;
--   CREATE TEMP TABLE erase_events ON COMMIT DROP AS
--     SELECT event_id FROM fact_events WHERE entity_id = $1
--     UNION SELECT event_id FROM state_facts
--       WHERE event_id IS NOT NULL AND (entity_id = $1 OR value_references(value, $1))
--     UNION SELECT event_id FROM fact_candidates
--       WHERE entity_id = $1 OR value_references(value, $1);
--   DELETE FROM fact_candidates WHERE entity_id = $1 OR value_references(value, $1);
--   DELETE FROM state_facts     WHERE entity_id = $1 OR value_references(value, $1);
--                               -- all versions: a split copies the value it splits
--   DELETE FROM fact_events WHERE event_id IN (SELECT event_id FROM erase_events);
--   DELETE FROM entities WHERE entity_id = $1;   -- ON DELETE CASCADE is the backstop
--   COMMIT;
-- Not covered here, each needs its own purge: derived copies outside these
-- tables (chunk text, search indexes, caches, embeddings, exports, backups),
-- and the upstream event source (a redelivered event re-creates the fact once
-- its ledger row is gone). DELETE does not physically erase: the tuples stay
-- on disk, and plain VACUUM only makes their space reusable, not overwritten;
-- copies also persist in WAL, replicas and backups until they age out. Byte-level
-- erasure is a storage and retention policy, not a SQL step.
--
-- Source retraction (not erasure) supersedes instead, keeping the audit trail:
--   UPDATE state_facts SET superseded_at = now()
--   WHERE source_id = $1 AND superseded_at IS NULL;
--   then re-assert the surviving sources' facts for the affected intervals.

-- ---------------------------------------------------------------------------
-- ACCEPTANCE (run on a scratch database; each line states the expected result)
-- ---------------------------------------------------------------------------
--   Running example shared with ai-context-layer evals-and-operations.md: owner
--   Alice -> Bob at 09:10; a 09:00 snapshot arrives late; a 09:11 index refresh
--   still says Alice. The event stream and its snapshots rank 10, the index 0.
--   INSERT INTO entities VALUES ('incident:42', 'incident'), ('person:alice', 'person');
--   SELECT assert_fact('e1', 'incident:42', 'incident_owner', '"person:alice"', '2026-03-01 08:50+00', 'evt:open',     NULL, 10); -- current
--   SELECT assert_fact('e2', 'incident:42', 'incident_owner', '"person:bob"',   '2026-03-01 09:10+00', 'evt:reassign', NULL, 10); -- current (equal authority supersedes; alice split to [08:50, 09:10))
--   SELECT assert_fact('e2', 'incident:42', 'incident_owner', '"person:bob"',   '2026-03-01 09:10+00', 'evt:reassign', NULL, 10); -- duplicate
--   SELECT assert_fact('e3', 'incident:42', 'incident_owner', '"person:alice"', '2026-03-01 09:00+00', 'snap:0900',    NULL, 10); -- unchanged (late snapshot agrees with history)
--   SELECT assert_fact('e4', 'incident:42', 'incident_owner', '"person:alice"', '2026-03-01 09:11+00', 'idx:refresh',  NULL, 0);  -- held_lower_authority
--   SELECT assert_fact('e5', 'incident:42', 'incident_owner', '"team:oncall"',  '2026-03-01 08:40+00', 'snap:0840',    NULL, 10); -- history ([08:40, 08:50), arrives last; current stays bob)
--   As of 09:05 -> alice; as of now -> bob; fact_candidates holds the e4 alice row, blocked_by = bob's fact_id.
--   As of 09:20 known at a time before e2 was applied -> alice; known now -> bob.
--   A direct INSERT of a second open row for the same key fails on state_facts_no_overlap.
--   Erasure of 'person:alice' with the recipe above: removes both e1 rows (the
--   superseded open original and its [08:50, 09:10) split copy), the e4 candidate,
--   the e1 and e4 ledger rows, and the entity. Afterwards as of 09:05 -> no row
--   (unknown); as of now -> bob, whose row is untouched.

-- ---------------------------------------------------------------------------
-- DOWN
-- ---------------------------------------------------------------------------
-- DROP FUNCTION IF EXISTS assert_fact(TEXT, TEXT, TEXT, JSONB, TIMESTAMPTZ, TEXT, TEXT, INTEGER);
-- DROP FUNCTION IF EXISTS value_references(JSONB, TEXT);
-- DROP TABLE IF EXISTS fact_candidates;
-- DROP TABLE IF EXISTS state_facts;
-- DROP TABLE IF EXISTS fact_events;
-- DROP TABLE IF EXISTS entities;
