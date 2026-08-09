# Postgres + pgvector Default

This is the V1 implementation recipe for a durable vector brain. It is intentionally plain SQL-first.

> **Version gate** — SQL examples and GUC knobs in this file require:
> - pgvector ≥ 0.8.0 for `hnsw.iterative_scan` (iterative index scan)
> - pgvector ≥ 0.8.1 for optimised `binary_quantize` performance and Postgres 18 support
> - pgvector ≥ 0.7.0 for `halfvec`, `sparsevec`, and `binary_quantize` itself
>
> Latest stable release as of this validation: **0.8.3** (2026-06-18); **0.8.2** (2026-02-25) carries the mandatory parallel-HNSW buffer-overflow (CVE-2026-3172) fix — treat 0.8.2 as the hard floor, and check the [CHANGELOG](https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md) for what 0.8.3+ adds before upgrading.
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
- [Tenant And Project Isolation](#tenant-and-project-isolation)
- [Operational Checks](#operational-checks)

## Schema Shape

Use separate tables for source documents, chunks, embeddings, ingest runs, and query/eval records.

Load the SQL assets in order:

1. `assets/sql/001_schema.sql`
2. `assets/sql/002_indexes_hnsw.sql`
3. `assets/sql/003_hybrid_search_function.sql`
3b. `assets/sql/008_fts_hardening.sql` *(recommended — weighted, unaccent-aware lexical vector; reversible)*
4. `assets/sql/004_ingest_ledger.sql`
5. `assets/sql/005_eval_tables.sql`
6. `assets/sql/006_rls_multitenant.sql` *(optional — only when more than one tenant shares the schema)*
7. `assets/sql/007_query_logs.sql` *(observability; required for production SLOs)*

## ASCII Flow

```text
001_schema.sql
  creates: documents, chunks, embeddings
       |
       v
002_indexes_hnsw.sql
  adds: source/doc indexes, FTS GIN, ACL GIN, HNSW on embeddings
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

Start with HNSW:

```sql
CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw
  ON embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);
```

Tune with evals, not intuition. Per-session knobs the caller (not the DDL) should set:

```sql
SET LOCAL hnsw.ef_search = 100;                  -- raise for recall, lower for latency
SET LOCAL hnsw.iterative_scan = 'relaxed_order'; -- pgvector >= 0.8; preserves recall under WHERE filters
SET LOCAL hnsw.max_scan_tuples = 20000;          -- safety ceiling for iterative scan
```

**`iterative_scan` values (pgvector ≥ 0.8.0):**

| Value | Behaviour | Use when |
|---|---|---|
| `'relaxed_order'` | Returns results in approximate similarity order; keeps scanning past the first LIMIT until enough candidates pass the filter | Filter-heavy corpora — the standard choice for all queries with a `WHERE` clause |
| `'strict_order'` | Returns results in strict similarity order; stops as soon as LIMIT is satisfied | Filter-light or unfiltered queries where exact ranking matters |
| off (default pre-0.8.0) | No iterative scan; HNSW graph traversal stops at its natural boundary regardless of filter | Do not use with selective predicates — silently destroys recall |

Without `iterative_scan = 'relaxed_order'`, a selective `WHERE` clause silently destroys recall — every filtered query is a recall trap. Verify these knobs against your installed pgvector version (≥ 0.8.0 required).

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
