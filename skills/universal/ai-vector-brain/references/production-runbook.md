# Production Runbook

Operational checklist for taking a V1 pgvector brain from pilot to production.
The skill ships the *build*. This file ships the *operate*.

## Table of Contents

- [Pre-Production Gate](#pre-production-gate)
- [Backups](#backups)
- [HNSW Rebuild and Reindex](#hnsw-rebuild-and-reindex)
- [HNSW Memory Sizing](#hnsw-memory-sizing)
- [Embedding Model Migration Playbook](#embedding-model-migration-playbook)
- [Observability and SLOs](#observability-and-slos)
- [Capacity Planning](#capacity-planning)
- [Incident Patterns](#incident-patterns)
- [Tuning Loop](#tuning-loop)

## Pre-Production Gate

Do not promote a brain to production until all of the following hold:

- corpus eval set has ≥50 labeled queries with hand-set `expected_evidence_ids`
- release gates from `eval-by-corpus-type.md` pass on the candidate build
- `006_rls_multitenant.sql` applied if more than one tenant shares the schema
- `007_query_logs.sql` applied and writes are wired into the retrieval path
- backup strategy chosen and tested with one successful restore drill
- HNSW build time, index size, and steady-state memory footprint measured
- p95 latency measured under realistic concurrency, not a single-shot benchmark
- rollback path documented (which corpus_version_id is the last known good)
- ACL deny-by-default check (below) passes with zero rows returned

## ACL Deny-by-Default Check

For a database created before `chunks.is_public` existed, apply
`001_schema.sql` again before loading `003_hybrid_search_function.sql`.
The repeatable `ALTER TABLE` in 001 adds the flag with `FALSE` for existing
rows, so legacy chunks do not become public. Plan this DDL with the database
owner because it takes a table lock; verify the column and default on the
target database before enabling the new retrieval function. The repository's
static contract test checks the SQL asset, but does not execute the migration.

003's `hybrid_retrieve_context` denies access by default: an empty
`acl_scope` (`'{}'`) or a NULL `p_acl_scope` argument must never be treated
as public. Only chunks with `is_public = TRUE`, or chunks whose `acl_scope`
shares a key with a non-NULL `p_acl_scope`, are visible. ACL keys are grant
names and values are ignored, so the fixture's restricted chunk must not carry
the key `group-with-no-access`. Run this before
promoting to production, against a fixture that has at least one
non-public, non-matching chunk:

```sql
-- Fixture: one document/chunk with a restricted ACL scope and is_public = FALSE
-- (the schema default), and no matching key for the scope below.
-- Expect ZERO rows from every call in this block.

-- 1. NULL scope (caller passed no ACL context) must not return restricted content.
SELECT count(*) AS should_be_zero
FROM hybrid_retrieve_context(
  query_text      => 'restricted content',
  query_embedding => (SELECT embedding FROM embeddings LIMIT 1),
  embedding_model => (SELECT model_id FROM embeddings LIMIT 1),
  p_acl_scope     => NULL
) AS r
JOIN chunks c ON c.evidence_id = r.evidence_id
WHERE c.is_public = FALSE;

-- 2. Non-matching, non-empty scope must not return restricted content either.
SELECT count(*) AS should_be_zero
FROM hybrid_retrieve_context(
  query_text      => 'restricted content',
  query_embedding => (SELECT embedding FROM embeddings LIMIT 1),
  embedding_model => (SELECT model_id FROM embeddings LIMIT 1),
  p_acl_scope     => '{"group-with-no-access": true}'::jsonb
) AS r
JOIN chunks c ON c.evidence_id = r.evidence_id
WHERE c.is_public = FALSE;
```

Both counts must be `0`. If either returns rows, the ACL filter is
fail-open — stop and fix `003_hybrid_search_function.sql` before promoting.
Static regression coverage for the same invariant lives in
`scripts/test_sql_asset_contracts.py::test_acl_is_deny_by_default_not_fail_open`
(source-level check; run the SQL above against a live fixture for the
behavioral proof, since the Python test cannot execute SQL).

## Backups

`embeddings` is the largest table. Three backup strategies, ranked by recovery
cost:

| Strategy | RPO | RTO | When to use |
|---|---|---|---|
| Logical: `pg_dump` (custom format) of full DB on a schedule | hours | hours | Single-region, modest corpus (<5M chunks) |
| Logical: `pg_dump` of `documents` + `chunks` only; rebuild embeddings | hours | hours-days | Cost-sensitive; embedding rebuild cost is bounded and known |
| Physical: PITR (pg_basebackup + WAL archive) | minutes | minutes | Multi-region, large corpus, paid SLA |

Restore drills are mandatory. An untested backup is a wish, not a guarantee.

Rebuild-from-source option: if `documents.source_uri` + `content_hash` are
canonical and the source corpus is durable, you can rebuild a brain entirely
from re-ingest. Document the re-ingest time and the upstream rate-limit
budget so the team knows the actual RTO.

## Security: pgvector Version Audit

**Look up the current security floor before every HNSW build.** Check the
pgvector [CHANGELOG](https://github.com/pgvector/pgvector/blob/master/CHANGELOG.md)
and the PostgreSQL security announcements for advisories that affect features
you use, and upgrade to the newest release that fixes all of them. Example of
why: CVE-2026-3172, a buffer overflow in parallel HNSW index builds that could
leak data from other relations or crash the server, was fixed in pgvector 0.8.2
(source: https://www.postgresql.org/about/news/pgvector-082-released-3245/).
Later advisories can raise the floor; the lookup, not this example, sets it.

```sql
-- Check installed version
SELECT extversion FROM pg_extension WHERE extname = 'vector';
```

If upgrading is not immediately possible, disable parallel HNSW builds by setting `max_parallel_maintenance_workers = 0` until the upgrade is applied.

## HNSW Rebuild and Reindex

When to rebuild:

- bulk ingest changed >20% of embeddings (HNSW build is incremental but
  degrades with heavy churn)
- recall@k drops in eval despite no other change
- `ef_construction` was too low at first build and recall ceiling is bounded

How to rebuild without downtime:

```sql
-- Partial per model, like assets/sql/002_indexes_hnsw.sql.
CREATE INDEX CONCURRENTLY idx_embeddings_hnsw_new
  ON embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 128)
  WHERE model_id = '<model_id>';

-- Verify the new index is selected by the planner under a representative query,
-- then drop the old one in the same transaction:
BEGIN;
  DROP INDEX idx_embeddings_hnsw;
  ALTER INDEX idx_embeddings_hnsw_new RENAME TO idx_embeddings_hnsw;
COMMIT;
```

Before building, size the index with [HNSW Memory Sizing](#hnsw-memory-sizing)
and set `maintenance_work_mem` to at least the expected graph size; watch for
the pgvector NOTICE "hnsw graph no longer fits into maintenance_work_mem"
during the build.

## HNSW Memory Sizing

This is the one HNSW memory formula for this skill; other references link
here instead of carrying their own.

Per indexed vector:

```text
bytes_per_vector ≈ k × (vector_bytes + 2·M × id_bytes)

vector_bytes = dim × 4 (vector, fp32) | dim × 2 (halfvec) | dim × 1 (int8)
               | dim / 8 (bit, e.g. a binary_quantize expression index)
2·M          = layer-0 neighbours per node (M is the index's `m`)
id_bytes     = size of one neighbour reference in your engine
k            = engine page/tuple overhead factor, > 1
index_bytes  ≈ N × bytes_per_vector    (N = rows covered by the index)
```

Inputs are symbolic on purpose. Take `id_bytes` from the engine's storage
docs (a PostgreSQL tuple ID is 6 bytes; engines with 4-byte integer ids use 4).
Earlier estimates in this skill implied `k` between about 1.1 (the overhead
factor in OpenSearch's published HNSW estimate) and 1.5. Upper layers hold a
small fraction of nodes and fall inside `k`. Then measure; the measurement
wins over the formula:

```sql
SELECT pg_size_pretty(pg_relation_size('idx_embeddings_hnsw')) AS index_size,
       (SELECT count(*) FROM embeddings WHERE model_id = '<model_id>') AS n_vectors,
       pg_relation_size('idx_embeddings_hnsw')
         / NULLIF((SELECT count(*) FROM embeddings WHERE model_id = '<model_id>'), 0)
         AS bytes_per_vector;
```

Worked example, 1M vectors, 1024-dim fp32, M = 16, `id_bytes` = 6:
`k × (4,096 + 192)` B ≈ 4.7 GB at k = 1.1, 6.4 GB at k = 1.5. The old rule
here, `(m·4·dim) + (2·dim)` bytes per vector, gave about 67 GB, roughly 10–15×
too high: it counted each neighbour link as a full vector.

Quantized indexes: the links do not shrink. With `bit` vectors at 1024-dim,
`vector_bytes` is 128 B while `2·M × id_bytes` is 192 B at M = 16, so the
links are most of the index, and the index is far larger than raw size / 32.
Scaling raw vector size by a quantization ratio understates a binary index
by roughly 3–4× at M = 48 (768–1024-dim). The table heap also keeps the full-precision
vector for the rescore pass (`assets/sql/011_quantize_rescore.sql`); size it
separately under [Capacity Planning](#capacity-planning).

## Embedding Model Migration Playbook

The schema already supports this via `embeddings.model_id`. The runbook:

1. Add new model rows with a distinct `model_id`. Dual-write during the
   migration window.
2. Build a parallel HNSW index filtered to the new model:
   `CREATE INDEX CONCURRENTLY idx_emb_hnsw_v2 ON embeddings USING hnsw
   (embedding vector_cosine_ops) WHERE model_id = '<model_id>';`, where
   `<model_id>` is the new model's id exactly as stored in `embeddings.model_id`.
   Queries use this index only when they filter on the same `model_id`.
3. Route 5% of production queries to the new model. Sample retrieval logs.
4. Run the labeled eval set against the new model. Compare to baseline.
5. If gates hold, ramp 5 → 25 → 50 → 100 with at least one observation
   window per step.
6. Keep the old model for at least one corpus_version cycle so rollback is
   reversible.
7. Delete old model rows only after rollback is no longer needed AND any
   downstream semantic cache has been invalidated.

Never overwrite an embedding row in place. Migration is additive.

## Observability and SLOs

Wire the views from `assets/sql/007_query_logs.sql` to your dashboard. Track:

| Signal | Why | Suggested SLO |
|---|---|---|
| p95 retrieval latency | User experience | <300ms for docs, <500ms for compliance, <800ms with rerank |
| `no_evidence` rate | Corpus coverage / query drift | <15% hourly; investigate spikes |
| Average rerank top score | Retrieval quality drift | <20% drop vs 7-day baseline |
| Cache hit rate | Corpus version churn | Sudden drops suggest invalidation bugs |
| Index size growth | Capacity planning | Trend, alert on rate change |
| HNSW recall@k (offline, eval set) | Index health | Above the gate from `eval-by-corpus-type.md` |

OpenTelemetry: emit a span per retrieve_context call with attributes
`corpus_version_id`, `retrieval_method`, `top_k`, `latency_ms`,
`no_evidence`. The exporter is your choice — Phoenix (Arize), Langfuse, or
generic OTLP all work.

## Capacity Planning

Rough sizing for the V1 schema:

| Resource | Per chunk (approx) | 1M chunks | 10M chunks |
|---|---|---|---|
| `chunks.content` | 2-4 KB | 2-4 GB | 20-40 GB |
| `embeddings.embedding` (1024-dim vector) | ~4.1 KB | ~4 GB | ~40 GB |
| `embeddings.embedding` (1024-dim halfvec) | ~2.1 KB | ~2 GB | ~20 GB |
| HNSW index (m=16, 1024-dim fp32) | ~4.7-6.4 KB ([formula](#hnsw-memory-sizing)) | ~5-6 GB | ~47-64 GB |
| FTS GIN index on `fts_vector` | 30-40% of content | ~1 GB | ~10 GB |

Past ~10M chunks, follow `references/graph-theory-at-scale.md` (DiskANN,
quantization, sharding). pgvector is not infinite; do not pretend it is.

## Incident Patterns

| Symptom | Likely cause | First check |
|---|---|---|
| Sudden recall drop after filter rollout | Missing `hnsw.iterative_scan = 'relaxed_order'` | Session settings on the connection used by the app |
| Latency spike post-ingest | HNSW maintenance / VACUUM contention | `pg_stat_progress_create_index`, autovacuum activity |
| `no_evidence` spike | Corpus version churned without cache invalidation | `corpus_versions` recent rows; cache TTL alignment |
| ACL bleed across tenants | RLS not enabled or `app.tenant_id` unset on a code path | `pg_policies` on the brain tables; grep for missed `set_config` |
| Citation drift after rerank rollout | Rerank rerouting to a different but plausible chunk | Compare pre/post rerank evidence IDs in `query_logs` |
| Slow ingest | Single-row inserts; missing batch path | Connection pool stats; `pg_stat_user_tables.n_tup_ins` rate |

## Tuning Loop

Tune in this order. Stop when the gate is met; do not over-tune.

1. **Confirm gates with eval.** If above the gate, do not tune.
2. **Filter correctness.** Add missing `hnsw.iterative_scan` first.
3. **Hybrid ratio.** Inspect failures — is recall lost in lexical or vector leg?
4. **Chunk size and `unit_type`.** Re-chunk a 10% sample, re-eval.
5. **Embedding model.** Last resort; full migration playbook applies.
6. **Index params.** `ef_construction` 64 → 128, `ef_search` 100 → 200.
7. **Rerank model and `N`.** Size `N` by the rule in [ai-rag ranking-pipeline-guide.md](../../ai-rag/references/ranking-pipeline-guide.md#5-reranking-stage), then confirm on the eval set.

Vibes are not a tuning signal. The eval set is.
