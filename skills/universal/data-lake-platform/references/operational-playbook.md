# Operational Playbook

Monitoring, incident flows, migrations, and recovery for a running lakehouse. Serving-engine details: ClickHouse templates under `../assets/query-engines/clickhouse/`. Backfill runbook: [template-data-quality-backfill-runbook.md](../assets/cross-platform/template-data-quality-backfill-runbook.md).

## Monitor

| Signal | Source | Alert when |
|--------|--------|-----------|
| Freshness | Last committed snapshot / load timestamp per table | Older than the table's SLA |
| Pipeline failures | Orchestrator | Any failure on a production asset |
| Small-file drift | File count and average file size per table/partition | Average size falling well below target; files per partition climbing |
| Snapshot/metadata growth | Snapshot count, manifest count | Growing without bound (expiry job not running) |
| CDC / consumer lag | Kafka consumer lag, replication-slot lag | Beyond the freshness budget; slot lag growing on the source |
| Serving latency | Engine query log (p95/p99) | Above the dashboard SLO |
| ClickHouse parts | Active parts per table/partition | Climbing toward the insert-throttling limit (batch inserts; see the ClickHouse templates) |

## Incident Flows

**Pipeline failure** — read the failing task's error; check source availability, credentials, upstream schema changes, and resource limits; fix the cause; rerun the *same logical interval* (idempotent); verify downstream counts and quality checks; update the runbook if new.

**Bad data landed** — scope it (tables, partitions, time range); stop the writer; quarantine or roll back (below); notify consumers with the affected range; correct and backfill; rerun quality checks before re-opening. Quality tooling: `data-analytics-engineering`.

**Serving engine degradation** — find the expensive running queries and kill runaways; check memory and merge backlog (parts count). `OPTIMIZE ... FINAL` rewrites whole partitions and is heavy: use it only on a targeted partition as a one-off, never as a routine fix.

## Recovery with Table Formats

- Rollback to a prior snapshot (Iceberg `rollback_to_snapshot`, Delta `RESTORE`) changes the table for **every** reader immediately; announce it and pause writers first, or later commits race the rollback.
- A snapshot is recoverable only until it expires: the snapshot-retention window **is** the recovery window. Set it from the recovery objective, then balance storage cost.
- For risky rewrites or backfills, write to a branch (Iceberg/Nessie) or a staging table and publish after validation (write-audit-publish) instead of relying on rollback.
- Serving engines are not backed up by the lake: keep engine-native backups, or prove you can rebuild serving tables from the lake within the recovery objective.

## Migrations

**New source** — document schema, volume, SLA, and delete semantics; build in dev; test on a sample including deletes and late rows; deploy; watch the first runs; register in the catalog.

**Schema change** — check reader compatibility first ([template-schema-evolution.md](../assets/cross-platform/template-schema-evolution.md)); notify consumers; apply the change (Iceberg `ADD`/`RENAME COLUMN` is metadata-only); backfill only if historical rows need the new column; verify old and new queries.

**Format migration (e.g. Parquet/Hive -> Iceberg)**:

1. Prefer in-place metadata migration where supported (Iceberg `snapshot` to trial without touching the source, then `migrate`), or rewrite in bounded batches by partition.
2. Validate per partition: row counts **and** a column checksum/aggregate, not totals only.
3. Switch writers, then readers; keep the old table read-only as a fallback for a defined period; drop it only after the validation period passes.
4. Full checklist: [template-migration-checklist.md](../assets/cross-platform/template-migration-checklist.md).

## Runbook Skeleton

Symptoms -> impact (systems, consumers) -> known causes -> resolution steps -> verification (the query that proves it is fixed) -> prevention -> on-call and escalation contacts.
