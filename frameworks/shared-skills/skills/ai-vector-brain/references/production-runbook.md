# Production Runbook

Operational checklist for taking a V1 pgvector brain from pilot to production.
The skill ships the *build*. This file ships the *operate*.

## Table of Contents

- [Pre-Production Gate](#pre-production-gate)
- [Backups](#backups)
- [HNSW Rebuild and Reindex](#hnsw-rebuild-and-reindex)
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

**CVE-2026-3172 — buffer overflow in parallel HNSW index builds.** pgvector 0.8.2 (released 2026-02-26) patches a buffer overflow that can leak sensitive data from other relations or crash the database server. The vulnerability is triggered specifically by parallel HNSW index builds. Audit your installed pgvector version and upgrade to >=0.8.2 before enabling or running parallel HNSW builds. Source: https://www.postgresql.org/about/news/pgvector-082-released-3245/

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
CREATE INDEX CONCURRENTLY idx_embeddings_hnsw_new
  ON embeddings USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 128);

-- Verify the new index is selected by the planner under a representative query,
-- then drop the old one in the same transaction:
BEGIN;
  DROP INDEX idx_embeddings_hnsw;
  ALTER INDEX idx_embeddings_hnsw_new RENAME TO idx_embeddings_hnsw;
COMMIT;
```

Memory footprint: rule of thumb is `~(m * 4 * dim) + (2 * dim)` bytes per
vector, plus overhead. A 1M-vector / 1024-dim / m=16 index is roughly
65–80 GB of resident memory. Verify against your installed pgvector version
and `pg_relation_size('idx_embeddings_hnsw')`.

## Embedding Model Migration Playbook

The schema already supports this via `embeddings.model_id`. The runbook:

1. Add new model rows with a distinct `model_id`. Dual-write during the
   migration window.
2. Build a parallel HNSW index filtered to the new model:
   `CREATE INDEX CONCURRENTLY idx_emb_hnsw_v2 ON embeddings USING hnsw
   (embedding vector_cosine_ops) WHERE model_id = 'voyage:voyage-4-large';`
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
| HNSW index (m=16, 1024-dim) | ~70 KB | ~70 GB | ~700 GB |
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
7. **Rerank model and `N`.** Oversample to 5-10× `K` before rerank.

Vibes are not a tuning signal. The eval set is.
