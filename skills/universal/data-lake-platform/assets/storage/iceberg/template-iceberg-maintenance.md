# Apache Iceberg Maintenance Template

Use when scheduling or debugging Iceberg maintenance: snapshot expiry, orphan-file cleanup, compaction, and manifest rewrites.

Procedure names below are Spark's (`CALL <catalog>.system.*`). Other engines expose different commands; for example, Trino uses `ALTER TABLE ... EXECUTE optimize | expire_snapshots | remove_orphan_files`. For which engine supports which procedure or option, use [Version and support lookup](../../../SKILL.md#version-and-support-lookup). Table layout choices are in [template-iceberg-table.md](template-iceberg-table.md).

## Order of a maintenance run

1. **Expire snapshots.** This drops snapshots older than the retention window and deletes the data and metadata files that only those snapshots referenced.
2. **Remove orphan files.** Use a safety margin longer than the longest write. This deletes files that no snapshot ever referenced, such as those left by failed or aborted writes and crashed compactions.
3. **Rewrite data files (compaction).**
4. **Rewrite manifests.**

Why this order:

- Expiry first shrinks the snapshot set, so the orphan scan and the compaction planner reason over less metadata. Expiry already deletes the files it knows about. Orphan cleanup only needs to catch files that were never committed.
- Compaction commits a new snapshot. The small files it replaces stay referenced by earlier snapshots, so they are reclaimed by the **next** expiry run. Expect storage to drop one cycle later, not immediately.
- Manifests go last so they are regrouped over the post-compaction file set. Rewriting them before compaction is wasted work, because compaction writes new manifests.
- Run one maintenance job per table at a time. Concurrent maintenance commits on the same table conflict and retry.

## Snapshot expiry: compute the cutoff from the retention window

Derive the retention window; never copy a constant:

- **Lower bound:** the maximum of (a) the time-travel or rollback horizon the business needs, (b) the longest query or job that pins a snapshot, and (c) the lag of the slowest incremental or streaming consumer that reads snapshots.
- **Upper bound:** the data-erasure SLA. Deleted rows stay physically in files referenced by older snapshots until those snapshots expire.
- If the lower bound exceeds the upper bound, surface the conflict: shorten consumer lag or change the erasure process. Do not silently pick one. Tagged snapshots are also retained, so a long-lived tag also holds deleted data.

`older_than` is always `now - retention window`, computed at run time and never a literal date:

```python
from datetime import datetime, timedelta, timezone

RETENTION = timedelta(days=RETENTION_DAYS)   # from the window above
cutoff = (datetime.now(timezone.utc) - RETENTION).strftime("%Y-%m-%d %H:%M:%S")
# The TIMESTAMP literal is read in the Spark session time zone: run with spark.sql.session.timeZone=UTC.
spark.sql(f"""
  CALL catalog.system.expire_snapshots(
    table       => 'db.events',
    older_than  => TIMESTAMP '{cutoff}',
    retain_last => 10   -- floor: keeps rollback points on tables that commit rarely
  )
""")
```

Also set `history.expire.max-snapshot-age-ms` and `history.expire.min-snapshots-to-keep` on the table. Then every engine or job that expires without explicit arguments uses the same retention.

## Orphan-file cleanup

- Compute `older_than = now - safety margin` the same way. The margin must exceed the longest possible write or commit, including retries and long compactions. Files from an in-flight write stay unreferenced until commit, and deleting them corrupts that commit. The Spark procedure's default margin is a few days; never go below your longest job runtime.
- Run with `dry_run => true` first on any new table or location, and read the list.
- Never point it at a location shared with another table or with non-Iceberg data. Everything this table does not reference looks orphaned.
- Watch for URI mismatches. If files were written with different schemes or authorities (for example `s3://` vs `s3a://`), live files can look orphaned. Configure the scheme and authority equivalence options from your engine's docs, and dry-run.
- There is no separate "delete orphan metadata" step. Old `metadata.json` files are bounded by `write.metadata.delete-after-commit.enabled` plus `write.metadata.previous-versions-max`.

```sql
CALL catalog.system.remove_orphan_files(
  table      => 'db.events',
  older_than => TIMESTAMP '<now - safety margin, computed like the expiry cutoff>',
  dry_run    => true
);
```

## Compaction (rewrite data files)

- **Scope.** Use `where` to limit a run to partitions that are no longer receiving writes, such as closed days. Compacting the partition a streaming writer is appending to causes commit conflicts. On large tables, set `partial-progress.enabled` so the rewrite commits in groups instead of failing all-or-nothing.
- **Strategy.** Use `binpack` for routine runs; it is the cheapest option and fixes only file sizes. Use `sort` on the leading filter column, or `zorder` on a few columns that are filtered together, for hot read-heavy tables. Either one costs a full shuffle, so run it less often. Z-order dilutes as columns are added.
- **Trigger.** A file group qualifies when it has at least `min-input-files` files outside the min/max size band around the target. Tune the band rather than rewriting everything on each run.
- **Merge-on-read tables.** Also fold delete files, using the `delete-file-threshold` option to rewrite data files that carry many deletes and `rewrite_position_delete_files` for position deletes. Tie the compaction frequency to the commit rate when writers produce equality deletes.

```sql
CALL catalog.system.rewrite_data_files(
  table      => 'db.events',
  strategy   => 'sort',
  sort_order => 'user_id ASC NULLS LAST',
  where      => 'created_at >= TIMESTAMP ''<closed window start>'' AND created_at < TIMESTAMP ''<closed window end>''',
  options    => map('target-file-size-bytes', '268435456', 'partial-progress.enabled', 'true')
);
```

## Manifest rewrite

Streaming and frequent small appends add manifests with each commit, so query planning slows as commits accumulate. Run `rewrite_manifests` when planning time grows with commit count, not on a fixed calendar.

## Health signals (metadata tables)

```sql
-- Small files per partition: average size well under target in a closed partition means compaction is missing
SELECT partition, count(*) AS files, avg(file_size_in_bytes)/1e6 AS avg_mb
FROM catalog.db.events.files GROUP BY partition ORDER BY files DESC;

-- Outstanding delete files (merge-on-read): rising counts mean compaction is not keeping up
SELECT content, count(*) AS delete_files FROM catalog.db.events.delete_files GROUP BY content;

-- Snapshot and manifest growth: unbounded growth means expiry or manifest rewrite is not running
SELECT count(*) FROM catalog.db.events.snapshots;
SELECT count(*) FROM catalog.db.events.manifests;
```

Alert on trends relative to the table's own target and history, not on absolute file counts. The signals are average file size falling in closed partitions, delete files per data file rising, snapshot count growing without bound, and planning time rising.

## Verify and roll back

- [ ] After expiry, only snapshots newer than the cutoff remain, plus the `retain_last` snapshots and tagged ones.
- [ ] The orphan dry-run list was reviewed and contains no file referenced by the `files` or `all_files` metadata tables.
- [ ] Each compaction snapshot has `operation = 'replace'`, and its summary shows added records equal to deleted records, so row counts are unchanged.
- [ ] A typical query plans fewer files after compaction than before.
- [ ] Rollback: a compaction is an ordinary snapshot. If a sort rewrite regresses reads, use `rollback_to_snapshot` to the prior snapshot while it is still unexpired.
