# Git-Anchored Ingestion

## Table of Contents

- [The five rules](#the-five-rules)
- [Schema additions to LearnedMemory knowledge_chunk](#schema-additions-to-learnedmemory--knowledge_chunk)
- [Run ledger](#run-ledger)
- [Bi-temporal recall](#bi-temporal-recall)

Ingest pattern for KBs whose source is a portfolio of git repositories.
Required reading for RA10. Composes with P4 (temporal facts), P10
(filesystem-as-memory), and P13 (managed-memory boundary) when an external
embedding service is used.

## The five rules

1. **Commit is time.** Every chunk row carries `valid_from_commit` and an
   optional `valid_to_commit`. Wall-clock timestamps are derived, not
   canonical. Bi-temporal queries map to commit ancestry, not to dates.
2. **Diff, do not rescan.** On every ingest run, compute the file-level diff
   between `last_indexed_commit_sha` and `current_sha`. Process only changed
   paths.
3. **Idempotency by content hash.** For each emitted chunk, compute
   `content_hash = blake3(normalized_text)`. If the row with this hash already
   exists for `(repo, path)`, skip the embedding call.
4. **Tombstone, never delete.** A removed file or removed chunk gets
   `valid_to_commit=current_sha`. The row stays. `recall(as_of=<past>)` still
   sees it. This is the only way A11 (forget path) and audit reconstruction
   compose.
5. **Force-push is detected, not trusted.** Before processing
   `(last_sha → current_sha)`, verify `last_sha` is an ancestor of `current_sha`.
   If not, the branch was rewritten — fall back to a full repo re-scan and
   write an `ingest_anomaly` row.

## Schema additions to `LearnedMemory` / `knowledge_chunk`

```sql
-- Postgres / pgvector
ALTER TABLE knowledge_chunk
  ADD COLUMN source_repo         text NOT NULL,
  ADD COLUMN source_path         text NOT NULL,
  ADD COLUMN source_commit_sha   text NOT NULL,
  ADD COLUMN content_hash        bytea NOT NULL,
  ADD COLUMN valid_from_commit   text NOT NULL,
  ADD COLUMN valid_to_commit     text,                 -- NULL = current
  ADD COLUMN chunk_anchor        text;                 -- heading path or "L120-L155"

CREATE UNIQUE INDEX uq_chunk_idem
  ON knowledge_chunk (source_repo, source_path, content_hash)
  WHERE valid_to_commit IS NULL;   -- partial: a revert may re-add tombstoned content

CREATE INDEX ix_chunk_valid
  ON knowledge_chunk (source_repo, source_path)
  WHERE valid_to_commit IS NULL;
```

`MongoDB`: same fields as a sub-document, with a partial unique index on
`{ source_repo, source_path, content_hash }` and a partial index on
`{ source_repo, source_path, valid_to_commit: null }`.

## Run ledger

One row per ingest attempt — separate from the chunk table.

```sql
CREATE TABLE ingest_run (
  id              uuid PRIMARY KEY,
  source_repo     text NOT NULL,
  branch          text NOT NULL,
  from_sha        text,
  to_sha          text NOT NULL,
  started_at      timestamptz NOT NULL,
  finished_at     timestamptz,
  stats           jsonb,            -- {added, updated, tombstoned, skipped, anomalies}
  status          text NOT NULL     -- running | ok | failed | rolled_back
);
```

Freshness SLOs read from this table. A repo with no `ok` row in N hours is
stale.

## Bi-temporal recall

```sql
-- "What did we believe on commit X?" — point-in-time recall.
SELECT * FROM knowledge_chunk
WHERE source_repo = $1
  AND (valid_from_commit IN (ancestors_of($X)))
  AND (valid_to_commit  IS NULL
       OR valid_to_commit NOT IN (ancestors_of($X)));
```

For most stacks, materialize an `ancestors_of` helper as a recursive CTE seeded
from a `commit_graph` table populated by the ingest run. This is the single
hardest-to-cheat part of RA10; it is also the part that pays for itself the
day a regulator asks "what did your AML doc say on date Y."

## Webhook plumbing

```text
GitHub push event
  → /webhooks/git_push  (HMAC-verified)
  → enqueue ingest_job(repo, branch, before_sha, after_sha)
  → worker:
      lock = advisory_lock(repo)
      try:
        run_ingest(repo, before_sha, after_sha)
      finally:
        release(lock)
```

Advisory lock per repo prevents two ingest runs colliding when a busy repo
gets back-to-back pushes. Webhooks are best-effort — keep a nightly catch-up
poll that compares `last_indexed_sha` against `git ls-remote`.

## Failure handling

- **Embedding endpoint down.** Mark `ingest_run.status='failed'`, do not
  partially commit chunks. Retry with backoff. Memory and operational truth
  must remain intact (P13).
- **Branch rewritten.** Full repo re-scan; write an `ingest_anomaly`. The
  previous chunks are tombstoned with `valid_to_commit=current_sha`.
- **Repo deleted from portfolio.** Tombstone all live chunks with
  `valid_to_commit=current_sha`. Keep the catalog row in a `removed` state for
  audit; do not hard-delete.

## Anti-patterns specifically blocked

- **A7 violation by hard delete.** `DELETE FROM knowledge_chunk` is forbidden
  in the normal path. DSAR uses a separate, audited code path that tombstones
  *and* redacts text.
- **A13 violation by orphan chunks.** A chunk row without
  `(source_repo, source_path, source_commit_sha)` is rejected at write time.
- **A15 violation by re-running expensive pipelines.** Recurring agent
  queries that hit the same chunks repeatedly are a signal to compile a
  synthesis page in the hub repo (P7).

## See also

- `reference-architectures.md` → RA10 — the recipe this reference supports.
- `markdown-chunking-patterns.md` — chunk-emission rules for markdown.
- `builds/cookbooks/git_repo_ingest.md` — runnable Python example.
- Partner skill `dev-context-multi-repo` — catalog and freshness tooling that
  RA10 ingestion consumes.
