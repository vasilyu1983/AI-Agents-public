# Incremental Loading Template

Use when choosing how a lake table picks up only new or changed data: strategy, watermark handling, late data, deletes, and engine-specific upsert traps. dlt specifics (cursor declaration, `merge_key`, `end_value` backfills) live in [template-dlt-incremental.md](../ingestion/dlt/template-dlt-incremental.md). Incremental transformation models (SQLMesh/dbt) belong to the `data-analytics-engineering` skill ([SKILL.md](../../../data-analytics-engineering/SKILL.md)).

## Choose the Strategy

| Strategy | Use when | Misses / costs |
|---|---|---|
| Log-based CDC | Hard deletes matter, many updates, or no trustworthy change column | Operational weight (slots, retention, connector); see the `data-streaming` skill |
| Change-timestamp cursor | Database sets `updated_at` on every write; deletes are soft or out of scope | Hard deletes; rows committed late with older timestamps |
| Monotonic ID cursor | Insert-only tables | Every update; IDs allocated but committed out of order |
| Snapshot diff (hash compare) | No cursor and no CDC, small or medium tables | Full scan of both sides each run |
| Full refresh | Small tables, or logic too complex to increment safely | Cost grows with table size |

Default: CDC for mutable operational tables where deletes matter; cursor + merge otherwise; full refresh below the size where it simply finishes inside the schedule.

## Watermark Rules

- Take the next watermark from the **data** (max cursor value loaded), never from the wall clock at run time; clock skew and in-flight transactions make `now()` skip rows.
- Persist the watermark only **after** the load commits, ideally in the same transaction or commit as the data. Saving it first loses the window when the load fails.
- Do not derive the watermark from `max(updated_at)` in the target table: a partial or out-of-order load advances it past rows never loaded.
- Use `>=` and de-duplicate by key rather than `>`; many rows can share one timestamp and `>` drops the ones not yet read.
- Check the cursor before trusting it: nulls, values in the future, values that go backwards on update, timezone of storage vs filter.

## Late Data

- Measure lateness (commit or arrival time minus cursor time) and set the lookback window from its high percentile, then alert when observed lateness exceeds the window.
- A lookback re-reads rows, so the target must be keyed (`MERGE`, dedup engine, or partition overwrite). With append-only targets a lookback creates duplicates.
- For event-time aggregates, re-compute the affected partitions within the lookback, not only new partitions.

## Deletes

- Cursor strategies cannot see hard deletes. Choose explicitly: CDC, source soft-delete flag, or a periodic snapshot diff that marks missing keys as deleted.
- Decide the target semantics: physical delete, or tombstone (`is_deleted`, `deleted_at`) kept for audit. Downstream models must filter tombstones consistently.
- Retention and erasure requests (for example GDPR) need physical deletes plus table-format cleanup; a tombstone alone is not erasure.

## Idempotency and Backfill

- Every run must be safe to repeat: key-based `MERGE`, a dedup engine keyed on the business key, or overwrite of exactly the partitions being loaded.
- Backfill with explicit, bounded ranges that do not move the live watermark; run in chunks so a failure repeats one chunk. Operational steps: [template-data-quality-backfill-runbook.md](template-data-quality-backfill-runbook.md).

## Engine Traps

**ClickHouse** (details: [template-clickhouse-ingestion.md](../query-engines/clickhouse/template-clickhouse-ingestion.md), [materialized views](../query-engines/clickhouse/template-clickhouse-materialized-views.md))
- `ReplacingMergeTree(version)` de-duplicates only during background merges, eventually, and only within a partition. Reads must use `FINAL` or `argMax(col, version) ... GROUP BY key` to be correct; never assume a merge has happened.
- The version column must increase for every change of a key (for example `updated_at` or a CDC log position). With equal versions the last inserted row wins, so correctness then depends on insert order.
- Deletes: an `is_deleted` column on the engine (check the release notes for the minimum version) or tombstone rows filtered at read time.
- Materialized views are insert triggers: they see only newly inserted blocks, never existing rows, updates, or deletes. Backfill them explicitly, and do not build them on top of tables that receive corrections.
- Distinct counts in a `SummingMergeTree` MV are wrong (the engine sums the pre-computed counts). Use `AggregatingMergeTree` with `uniqState`/`uniqMerge`.
- `CollapsingMergeTree` needs the cancel row to match the old row exactly and in insert order; use `VersionedCollapsingMergeTree` when order is not guaranteed.

**Iceberg / Delta** (details: [template-iceberg-table.md](../storage/iceberg/template-iceberg-table.md), [template-delta-table.md](../storage/delta/template-delta-table.md))
- De-duplicate the source to one row per key before `MERGE`. Several source rows matching one target row fail the merge (Spark) or apply in undefined order.
- Guard updates against out-of-order arrival: `WHEN MATCHED AND s.updated_at > t.updated_at THEN UPDATE`.
- Add a partition predicate to the `ON` clause when the batch covers known partitions; otherwise `MERGE` scans the whole target.
- Snapshot-range incremental reads return appended data only; snapshots produced by `MERGE`, overwrite, or delete are skipped or rejected. For changes including updates and deletes, use a change feed (Iceberg changelog view, Delta change data feed).
- Time travel takes a snapshot id or timestamp, not relative words like `'yesterday'`; compute the timestamp from the run's reference time.

## Verify

```sql
-- Duplicates on the business key (should return nothing)
SELECT key, count(*) FROM target GROUP BY key HAVING count(*) > 1;

-- Daily volume: gaps or sudden drops point at a skipped window
SELECT CAST(event_time AS DATE) AS d, count(*) FROM target
WHERE event_time >= current_date - INTERVAL '30' DAY GROUP BY d ORDER BY d;
```

- [ ] Source vs target count for the same closed window matches (tolerance only for documented late data).
- [ ] Target `max(cursor)` equals the stored watermark; watermark lag stays under schedule plus lookback.
- [ ] Re-running the last load changes nothing.
- [ ] A test delete in the source is reflected per the chosen delete semantics.
