# Delta Lake Table Template

Use when creating or maintaining a Delta table: layout (partitioning vs clustering), idempotent writes, schema changes, and VACUUM and retention.

Table features and protocol versions differ by engine and runtime; open-source Delta and vendor runtimes do not expose the same features. Before enabling a feature, check [Version and support lookup](../../../SKILL.md#version-and-support-lookup) against **every** reader of the table. Schema-change compatibility rules are in [template-schema-evolution.md](../../cross-platform/template-schema-evolution.md).

## Layout decision

1. **Default when every reader supports it: liquid clustering (`CLUSTER BY`).** Clustering keys can change without rewriting the table, and `OPTIMIZE` clusters incrementally. It cannot be combined with `PARTITIONED BY` or `ZORDER` on the same table.
2. **Otherwise: partition by a low-cardinality date column, and Z-order within partitions.**
   - Commonly cited vendor guidance is to not partition tables below roughly 1 TB and to keep each partition at 1 GB or more. Below that, partitioning only creates small files.
   - `OPTIMIZE ... ZORDER BY` on 1–4 columns used together in filters. It is not incremental: a run rewrites all files in the targeted partitions, so always scope it with `WHERE` on partition columns.
3. **Derive the partition column with a generated column.** Delta can then turn filters on the timestamp into partition filters for supported expressions, so users do not have to filter on `event_date` by hand.

```sql
CREATE TABLE events (
  event_id   STRING,
  user_id    BIGINT,
  created_at TIMESTAMP,
  event_date DATE GENERATED ALWAYS AS (CAST(created_at AS DATE))
)
USING DELTA
PARTITIONED BY (event_date)
TBLPROPERTIES (
  'delta.columnMapping.mode'           = 'name',             -- enables rename/drop; upgrades the protocol (one-way)
  'delta.deletedFileRetentionDuration' = 'interval 7 days',  -- VACUUM horizon, see Retention
  'delta.logRetentionDuration'         = 'interval 30 days'  -- log/time-travel horizon
);
```

## Writes

- **MERGE:** deduplicate the source on the key first, because multiple source rows matching one target row fail the MERGE. Put the partition predicate in the `ON` clause (`t.event_date >= '<start>' AND ...`). Without it, the MERGE scans the whole target, and concurrent MERGEs on disjoint partitions still conflict (concurrent-modification errors), because Delta cannot prove they touched different files.
- **Idempotent backfill:** use `replaceWhere` so the replace is atomic and safe to re-run. Rows in the new data that fall outside the predicate fail the write instead of leaking.

  ```python
  (df.write.format("delta").mode("overwrite")
     .option("replaceWhere", "event_date >= '<start_date>' AND event_date < '<end_date>'")
     .saveAsTable("events"))
  ```

  A plain `INSERT OVERWRITE` without a partition clause replaces the **whole table** unless dynamic partition overwrite is both enabled and supported.
- **Optimized writes and auto-compaction** (`delta.autoOptimize.optimizeWrite`, `delta.autoOptimize.autoCompact`) are runtime-dependent. They suit streaming and small-batch writers. Each costs a shuffle or an extra rewrite per write, so skip them for large batch writers that already produce target-size files.

## Schema changes (Delta specifics)

- Rename and drop require column mapping (`name` mode). Enabling it upgrades the reader and writer protocol, so readers without column-mapping support can no longer read the table. Treat the change as one-way.
- Streaming reads from a table that has had a rename, drop, or type change fail on the non-additive change unless the stream is configured with a schema tracking location. Configure that tracking before the change, not after.
- Type changes: widening works only with the type-widening table feature. Anything else needs a full rewrite with `overwriteSchema`, or the expand/contract pattern.
- `mergeSchema` on write silently adds new columns. Enable it for bronze ingestion only. In governed layers, keep enforcement on and apply explicit `ALTER TABLE` migrations.

## Retention, VACUUM, and time travel

- To time travel to version V you need its log entry (kept for `delta.logRetentionDuration`, subject to checkpoint cleanup) **and** its data files, which VACUUM removes after `delta.deletedFileRetentionDuration`. The usable window is the smaller of the two.
- VACUUM retention must exceed the longest-running reader or writer and the lag of any streaming consumer. A shorter retention deletes files that in-flight queries or a lagging stream still need, which fails queries and breaks stream restarts. Never disable the retention-duration safety check to VACUUM to 0 hours on a table with any concurrent activity.
- Run `VACUUM events DRY RUN` before the real run. VACUUM only deletes unreferenced files; it does not compact.
- Erasure: `DELETE` removes rows logically, but the bytes stay in old files until VACUUM runs after retention. The erasure SLA must be at least the VACUUM interval plus the retention. With deletion vectors, rows are only masked until files are rewritten; use `REORG TABLE ... APPLY (PURGE)` (check support), then VACUUM.

## Restore

- `RESTORE TABLE events TO VERSION AS OF <v>` is itself a new commit, so it is reversible. It fails if the files for version v were already vacuumed.
- Before a risky backfill, record the current version from `DESCRIBE HISTORY events LIMIT 1`.

## Verify

- [ ] `DESCRIBE HISTORY`: the `operation` and `operationMetrics` (output rows, updated rows, deleted rows) match expectations after each MERGE or backfill.
- [ ] `DESCRIBE DETAIL`: `sizeInBytes / numFiles` is near the target file size, and the partition or clustering columns are as intended.
- [ ] The `VACUUM ... DRY RUN` output was reviewed before the first real VACUUM.
- [ ] After enabling a table feature, every reader engine runs a smoke query successfully.
