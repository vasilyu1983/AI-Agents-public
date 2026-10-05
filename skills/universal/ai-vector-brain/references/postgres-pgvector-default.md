# Postgres + pgvector Default

This is the V1 implementation recipe for a durable vector brain. It is intentionally plain SQL-first.

> **Version gate** — SQL examples and GUC knobs in this file require:
> - pgvector ≥ 0.8.0 for `hnsw.iterative_scan` (iterative index scan)
> - pgvector ≥ 0.8.1 for optimised `binary_quantize` performance and Postgres 18 support
> - pgvector ≥ 0.7.0 for `halfvec`, `sparsevec`, and `binary_quantize` itself
>
> **Security floor: look it up.** Before any HNSW build, check the [CHANGELOG](https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md) and security advisories and run the newest release that fixes every advisory for features you use (for example, the parallel-HNSW buffer overflow CVE-2026-3172 was fixed in 0.8.2). See [production-runbook.md](production-runbook.md#security-pgvector-version-audit).
> Verify your installed version before relying on any knob:
> ```sql
> SELECT extversion FROM pg_extension WHERE extname = 'vector';
> ```

## Table of Contents

- [Schema Shape](#schema-shape)
- [ASCII Flow](#ascii-flow)
- [Why Separate Tables](#why-separate-tables)
- [Hybrid Retrieval](#hybrid-retrieval)
- [Index Defaults](#index-defaults)
- [Embedding Migration](#embedding-migration)
- [Corpus Versioning](#corpus-versioning)
- [Bitemporal State Facts](#bitemporal-state-facts)
- [Tenant And Project Isolation](#tenant-and-project-isolation)
- [Operational Checks](#operational-checks)

## Schema Shape

Use separate tables for source documents, chunks, embeddings, ingest runs, and query/eval records.

Load the SQL assets in order:

1. `assets/sql/001_schema.sql`
2. `assets/sql/002_indexes_hnsw.sql` *(run with `psql -v model_id='<provider>:<model>'`, the same string `embed_and_load.py` writes; also for 011 if you adopt it)*
3. `assets/sql/003_hybrid_search_function.sql`
3b. `assets/sql/008_fts_hardening.sql` *(recommended — weighted, unaccent-aware lexical vector; reversible)*
4. `assets/sql/004_ingest_ledger.sql`
5. `assets/sql/005_eval_tables.sql`
6. `assets/sql/006_rls_multitenant.sql` *(optional — only when more than one tenant shares the schema)*
7. `assets/sql/007_query_logs.sql` *(observability; required for production SLOs)*
8. `assets/sql/012_bitemporal_facts.sql` *(optional — only when agents ask state or as-of questions; see [Bitemporal State Facts](#bitemporal-state-facts))*

## ASCII Flow

```text
001_schema.sql
  creates: documents, chunks, embeddings
       |
       v
002_indexes_hnsw.sql
  adds: source/doc indexes, FTS GIN, ACL GIN, partial HNSW per model_id
       |
       v
003_hybrid_search_function.sql
  filters first, then builds lexical + vector candidate sets
       |
       v
RRF fusion
  combines ranks, returns evidence_id + source/citation fields
       |
       v
004_ingest_ledger.sql + 005_eval_tables.sql
  tracks freshness, corpus versions, query logs, eval runs
```

## Why Separate Tables

- `documents` stores source truth and idempotency hashes.
- `chunks` stores retrieval units and lexical search vectors.
- `embeddings` stores model-specific vectors, so migration is additive.
- `ingest_runs` makes freshness and failure visible.
- `query_logs` and eval tables make tuning measurable.

## Hybrid Retrieval

V1 default retrieval is:

```text
query_text --------------------+
                               v
                         lexical CTE
                         chunks.fts_vector
                               |
filters: doc_type, authority,  +--> RRF fusion --> optional rerank --> context pack
language, source_path_prefix,  |
ACL, as_of, unit_type          |
                               |
query_embedding ---------------+
                               v
                         semantic CTE
                         embeddings <=> query_embedding
```

Filters run inside both CTEs before fusion. That is mandatory for ACL,
authority, effective-time, and `unit_type` correctness.

### Lexical layer

The v1 `chunks.fts_vector` (defined in `001_schema.sql`) is a single-config
`english` vector with no weighting. For any production corpus, apply
`assets/sql/008_fts_hardening.sql` (reversible) and tune per
[postgres-fts-tuning.md](postgres-fts-tuning.md). Pass the matching
`p_fts_config` to `hybrid_retrieve_context` so query and column configs agree.

Do not ship pure vector search for code, policies, guides, or proper-noun-heavy documentation unless evals prove it is better.

## Index Defaults

Start with HNSW, one partial index per active `model_id` (as in
`assets/sql/002_indexes_hnsw.sql`); vectors from different models are not
comparable, and a query uses the index only when it filters on the same
`model_id`:

```sql
CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw
  ON embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64)
  WHERE model_id = '<model_id>';
```

Size it first with [production-runbook.md](production-runbook.md#hnsw-memory-sizing).

Tune with evals, not intuition. Per-session knobs the caller (not the DDL) should set:

```sql
SET LOCAL hnsw.ef_search = 100;                  -- raise for recall, lower for latency
SET LOCAL hnsw.iterative_scan = 'relaxed_order'; -- pgvector >= 0.8; evaluate recall and re-sort before assigning ranks
SET LOCAL hnsw.max_scan_tuples = 20000;          -- safety ceiling for iterative scan
```

**`iterative_scan` values (pgvector ≥ 0.8.0):**

| Value | Behaviour | Use when |
|---|---|---|
| `'relaxed_order'` | Allows slight distance disorder for better recall; scans until enough matches or a scan budget is reached | Filtered ANN when eval favors recall; re-sort the materialized candidate set by distance before assigning fusion ranks |
| `'strict_order'` | Preserves distance order among returned candidates; scans until enough matches or a scan budget is reached | Filtered ANN when strict ordering is preferred; this is still approximate retrieval |
| off (default) | No iterative scan; the initial ANN scan can yield too few matches after filtering | Queries whose filtered recall passes eval with the initial scan |

For filtered ANN with insufficient recall, evaluate strict or relaxed iterative scans, partial indexes, or partitioning. A selective subset may be better served by exact search using an index on its filter columns. Iterative scans still stop at configured scan/memory budgets; neither ordering mode guarantees exhaustive recall. With relaxed ordering, re-sort candidates in an outer query over a materialized CTE (`ORDER BY distance + 0` on Postgres 17+) before assigning rank positions. See the [pgvector filtering and iterative-scan recipes](https://github.com/pgvector/pgvector#filtering); verify support in the installed version (≥ 0.8.0 for iterative scans).

For embeddings >2000 dimensions (e.g. `text-embedding-3-large` at 3072) use `halfvec(N)` instead of `vector(N)` (pgvector >= 0.7) and `halfvec_cosine_ops` as the operator class. Half-precision halves storage and raises the dimension ceiling to 4000 with negligible recall impact.

For `>1M` chunks under heavy filter selectivity or sustained concurrent load, escalate to `pgvectorscale` StreamingDiskANN — see `references/backend-selection.md`.

## Embedding Migration

Never overwrite a live embedding column in place.

Use `model_id`:

1. backfill new embeddings as new rows with a new `model_id`
2. dual-write during migration
3. route a small query percentage to the new model
4. run retrieval evals and production sampling
5. cut over and delete old model rows only after rollback is no longer needed

## Corpus Versioning

Every ingest run should produce or update a corpus version. Use it to invalidate:

- semantic caches
- generated context packs
- eval baselines
- compiled summaries that depend on old chunks

## Bitemporal State Facts

Chunks answer "which evidence is relevant"; they cannot answer "who owns INC-42 now" or "who owned it at 09:05" without the model guessing from whichever paragraph ranked first. When agents ask state questions, keep typed facts beside the chunks: [`assets/sql/012_bitemporal_facts.sql`](../assets/sql/012_bitemporal_facts.sql) (independent of 001-011; join on `source_id`).

Canonical columns (use these names; map other engines with the table below):

| Column | Meaning |
|---|---|
| `valid_from`, `valid_to` | valid time, half-open `[valid_from, valid_to)`; `NULL` `valid_to` = still holds |
| `recorded_at`, `superseded_at` | transaction time, half-open; `NULL` `superseded_at` = current belief |
| `source_id`, `source_span` | provenance: the episode, event, or document, and the locator inside it |
| `entity_id` | stable ID, never a display name; names are facts, so a rename keeps history |

As of `t`, and as of `t` known at `k` (audit replay of what the agent could have answered then):

```sql
-- current belief
WHERE superseded_at IS NULL
  AND valid_from <= $t AND ($t < valid_to OR valid_to IS NULL)
-- known at k
WHERE recorded_at <= $k AND (superseded_at IS NULL OR $k < superseded_at)
  AND valid_from <= $t AND ($t < valid_to OR valid_to IS NULL)
```

Rules the asset encodes, each from a failure it prevents:

- **One write path, `assert_fact`; no `UPDATE` of a value.** It splits the current belief covering the new `valid_from` and ends the new fact where the covered belief ended, or where the next known belief starts. An out-of-order backfill (an old snapshot arriving after the newer change) therefore fills history and leaves the current row alone. Each fact carries a source `authority` (higher wins): a write that would supersede a current belief of strictly higher authority is held in `fact_candidates` for review and returns `held_lower_authority`, so a stale index refresh cannot replace the system of record; equal or higher authority supersedes as normal. Invalidating by arrival order lets a late import overwrite current state. Graphiti documents that it prioritises new information (arXiv 2501.13956); whether a backfill trips this is inferred, so plant an out-of-order backfill on the installed version before relying on it.
- **No overlapping current beliefs** per `(entity_id, attribute)`: a GiST `EXCLUDE` over `tstzrange(valid_from, valid_to, '[)')`, partial on `superseded_at IS NULL`. Scalar `=` inside GiST needs `btree_gist`; on managed Postgres, check the provider's extension allowlist before relying on it.
- **Duplicate events are no-ops** through an `event_id` ledger, not a unique index on facts (a split re-inserts rows that carry the same event).
- **Cleared is not unknown.** A row whose value is JSON `null` means "known to have no deadline"; no row means "never recorded", and the agent must abstain.
- **Role-specific attributes** (`incident_owner`, `task_owner`), never a bare `owner`, so one question cannot return the other role.
- **Supersession is not erasure.** Superseded rows still hold the value. Erasure deletes every version of the entity's own facts and of other facts whose value references it (`incident_owner = "person:alice"`, matched by `value_references`), its held candidates, and their `fact_events` ledger rows, then the entity; `ON DELETE CASCADE` alone misses the references. The asset's recipe is ordered and transactional. Derived copies (indexes, caches, embeddings, backups) and the upstream event source need their own purge, and `DELETE` only makes rows invisible to queries: plain `VACUUM` makes their space reusable without overwriting it, and copies persist in WAL, replicas, and backups until they age out. Treat query invisibility, derived-store deletion, and byte-level erasure (a storage and retention policy) as separate checks.
- **Do not reuse 003's document window predicate.** `hybrid_retrieve_context` treats `documents.effective_to` as inclusive (`effective_to >= p_as_of`); `valid_to` is exclusive. Convert at the boundary.

Vocabulary mapping (field names come from each project's docs; confirm them against the installed version before writing an adapter):

| Source | Valid time → canonical | Transaction time → canonical |
|---|---|---|
| Graphiti / Zep edges | `valid_at` → `valid_from`, `invalid_at` → `valid_to` | `created_at` → `recorded_at`, `expired_at` → `superseded_at` |
| Context-hub graph edges ([dev-context-multi-repo](../../dev-context-multi-repo/SKILL.md)) | `valid_at` → `valid_from`, `valid_until` → `valid_to` | `ingested_at` → `recorded_at`, `ingested_until` → `superseded_at` |
| `documents` in 001 | `effective_from` → `valid_from`, `effective_to` → `valid_to` (inclusive in 003) | `ingested_at` → `recorded_at`; none for supersession |

The engine-neutral acceptance tests (update, backfill, duplicate, clearance, point-in-time, role confusion) live in [ai-evals retrieval-and-memory-eval](../../ai-evals/references/retrieval-and-memory-eval.md#4-state-maintenance-scoring). For actual server assertions against the shipped SQL assets, use [PostgreSQL memory verification](postgres-memory-verification.md); it requires an explicit dedicated test DSN and reports missing backend access as not run.

## Tenant And Project Isolation

Default isolation choices:

- single project or local brain: one database/schema
- multiple project brains: one schema per brain or per project
- strict multi-tenant app: typed `tenant_id` plus Row Level Security and mandatory app filters

Do not bolt tenant filtering onto a mixed corpus after indexing. Isolation is a schema decision.

## Operational Checks

- row counts by source and document type
- duplicate content hash checks
- chunks without source URI or anchor
- embeddings missing for active chunks
- stale ingest runs
- eval regression since last corpus version
- failed or partial ingest runs
