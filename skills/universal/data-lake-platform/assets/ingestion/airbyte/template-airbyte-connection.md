# Airbyte Connection Template

Use when configuring an Airbyte connection: sync mode per stream, CDC setup, schedule, schema-change policy, and monitoring. Engine-agnostic incremental strategy: [template-incremental-loading.md](../../cross-platform/template-incremental-loading.md). For code-first pipelines see the [dlt templates](../dlt/template-dlt-pipeline.md).

## Sync Mode per Stream

| Source mode | Destination mode | Use when | Trap |
|---|---|---|---|
| Full refresh | Overwrite | Small tables, no cursor | Table is briefly empty or partial during the sync on some destinations |
| Full refresh | Append | Periodic snapshots for history | Storage grows by the full table every sync; set retention |
| Incremental | Append | Immutable events | Cursor `>=` re-reads boundary rows: duplicates. Deduplicate downstream |
| Incremental | Append + Deduped | Mutable rows with a primary key | Needs a real primary key; without one, rows collapse or duplicate |

Default for mutable tables: **Incremental + Append + Deduped** with CDC as the source method where the database supports it.

## Cursor vs CDC (Database Sources)

- A user-defined cursor (`updated_at`) misses hard deletes and rows committed late with an older timestamp. Use it only when deletes are out of scope and the column is set by the database on every write.
- CDC reads the transaction log: captures deletes and every change, and puts less load on the source than repeated cursor queries.
- Postgres CDC needs logical replication, a publication, and a replication slot. **The slot retains WAL until Airbyte reads it**: if syncs stop (paused connection, failing sync, deleted connection), disk fills on the primary. Alert on slot lag, and drop the slot when retiring the connection.
- Sync frequency must beat WAL/binlog retention. If the log is purged before the next sync, the connection must re-snapshot the whole table.
- Tables without a primary key cannot use dedup and may not be supported for CDC; add a key or use full refresh.
- Deletes arrive as rows with `_ab_cdc_deleted_at` set. Check how your destination mode applies them (removed vs kept as tombstones) and filter them in transformations if kept.

## Destination Typing

Older Airbyte versions produced raw JSON tables plus a separate "normalization" step. Current destinations type and deduplicate in the destination (Destinations V2) and normalization was removed; check the destination connector's docs for its raw-table and typing behaviour before building models on it. Transformations belong in the `data-analytics-engineering` skill, not in Airbyte custom operations.

## Schedule

- Derive the interval from the freshness target, not habit. A sync that takes longer than its interval queues back-to-back syncs and never catches up; alert on sync duration approaching the interval.
- Respect source API limits: the connector's page size and request rate apply per sync; shorter intervals do not increase allowed throughput.
- Use cron in UTC for syncs other jobs depend on; trigger downstream jobs from sync completion (orchestrator or webhook), not a fixed later time.

## Schema Changes

- Set the non-breaking change policy per connection: propagate columns (default for raw bronze), ignore, or pause. Pause when downstream contracts are strict.
- Breaking changes (primary key or cursor change, stream removed) require a manual reset of the affected streams; a reset re-syncs history, so plan it like a backfill.
- Clearing or resetting a stream removes its destination data until the re-sync completes, so downstream readers see missing data. Prefer a refresh mode that keeps existing data if your platform offers one (check the docs).

## Configuration as Code

- Manage sources, destinations, and connections through the Airbyte API or Terraform provider, not only the UI, so config is reviewed and reproducible. Look up connector definition IDs and provider versions from the current Airbyte docs; do not copy IDs from examples.
- Credentials from a secrets manager or variables; never inline.
- Set job resource limits for large streams; out-of-memory kills show up as retried attempts, not clear errors.

## Monitoring

- Alert on: failed sync, time since last successful sync above the freshness target, sync duration trend, records synced dropping to zero for a stream that normally has volume, CDC slot or binlog lag.
- Compare record counts per stream with the source periodically; a successful sync can still skip a stream deselected after a schema change.

## Verify

- [ ] Each stream has the intended sync mode, cursor, and primary key (review the catalog, not the UI summary).
- [ ] After the first sync: row count equals the source; no duplicate primary keys in deduped tables.
- [ ] A test update and delete in the source appear correctly after the next sync (CDC).
- [ ] Replication slot lag returns near zero after each sync.
