# Apache Iceberg Table Template

Use when creating an Iceberg table or choosing its format version, partition spec, row-level write mode, and table properties.

For which spec version or feature a given engine can read and write, use [Version and support lookup](../../../SKILL.md#version-and-support-lookup). "Format v2" below is a spec identifier, not a support claim. Maintenance (expiry, orphans, compaction) lives in [template-iceberg-maintenance.md](template-iceberg-maintenance.md); schema-change rules live in [template-schema-evolution.md](../../cross-platform/template-schema-evolution.md).

## Defaults

| Decision | Default | Why, and when to deviate |
|----------|---------|--------------------------|
| Format version | v2 or later | Row-level deletes (merge-on-read, delete files) need v2. Pick the highest version that **every** reader of the table supports; one lagging engine sets the ceiling. Upgrades are one-way. |
| File format and codec | Parquet + zstd | See [template-parquet-optimization.md](../parquet/template-parquet-optimization.md). |
| Target file size | 128–512 MB | Lower end when copy-on-write updates are frequent, because each update rewrites whole files. Higher end for large append-only tables, because fewer files mean less planning and fewer object opens. |
| Partitioning | Time transform on the event timestamp | Add `bucket` or `identity` fields only with a reason from [Partition spec](#partition-spec). |
| Row-level write mode | Set explicitly per table | See [Copy-on-write vs merge-on-read](#copy-on-write-vs-merge-on-read). |
| Catalog | One catalog of record per table | Two catalogs registering the same table location commit independently and overwrite each other's metadata pointer. |

## Skeleton (the properties are the lesson)

```sql
CREATE TABLE catalog.db.events (
    event_id   STRING,
    user_id    BIGINT,
    event_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(created_at))
TBLPROPERTIES (
    'format-version'                  = '2',
    'write.parquet.compression-codec' = 'zstd',
    'write.target-file-size-bytes'    = '268435456',     -- 256 MB, see Defaults
    'write.distribution-mode'         = 'hash',          -- cluster rows by partition before write; set explicitly, defaults differ by engine
    'write.delete.mode'               = 'merge-on-read', -- only for update/CDC-heavy tables
    'write.update.mode'               = 'merge-on-read',
    'write.merge.mode'                = 'merge-on-read',
    'write.metadata.delete-after-commit.enabled' = 'true',  -- otherwise every commit leaves a metadata.json forever
    'write.metadata.previous-versions-max'       = '100'
);
```

## Partition spec

- **Hidden partitioning.** Partition values are derived from a source column by a transform (`years`, `months`, `days`, `hours`, `bucket(N, col)`, `truncate(W, col)`, identity). Queries filter on the source column (`created_at`), and pruning follows automatically. Writers cannot put a row in the wrong partition. Always filter on the source column, never on a derived partition-field name.
- **Time granularity.** Choose the finest time transform at which one partition still holds several target-size files after compaction. Sizing rules are in [template-partitioning-strategy.md](../../cross-platform/template-partitioning-strategy.md).
- **`bucket(N, key)`.** Add it only for point lookups or joins on a high-cardinality key, or when one time partition is too large to scan. Pick N so each bucket in each time partition still reaches the target file size: `N <= partition bytes / target file size`. Too many buckets produce N small files per time partition per write.
- **`identity(col)`.** Use it only for low-cardinality columns that appear in nearly every predicate, such as region or a large tenant. Never use it on user, session, or order ids.

### Partition evolution

```sql
ALTER TABLE catalog.db.events REPLACE PARTITION FIELD days(created_at) WITH hours(created_at);
```

- Evolution is metadata-only. Existing files keep the old spec, new writes use the new spec, and planning prunes each spec separately. Rewrite old data with `rewrite_data_files` only if queries over the old layout are slow.
- Queries that filter on a derived partition column name, or tools that read the `partitions` metadata table assuming one spec, break or mis-report after evolution. Filter on source columns.
- Bucket-aligned joins apply only to files written with the same bucket spec. Changing N leaves old files in the old bucketing until they are rewritten.

## Copy-on-write vs merge-on-read

| Update pattern | Mode | Why |
|----------------|------|-----|
| Rare bulk updates or deletes, read-heavy | copy-on-write | Readers never merge deletes; each write rewrites every touched data file. |
| Frequent small updates, CDC upserts, erasure deletes scattered across partitions | merge-on-read | Writes add small delete files. Reads merge them until compaction folds them in. |
| Streaming upserts that write equality deletes | merge-on-read plus frequent compaction | Each equality delete must be applied to older data files at read time, so reads slow with every uncompacted commit. |

- Merge-on-read without scheduled compaction becomes a slow read regression. Track delete files per data file (see the maintenance template).
- The mode is set per operation (`write.delete.mode`, `write.update.mode`, `write.merge.mode`), so set all three.
- Before enabling merge-on-read, confirm every reader applies delete files. A reader that does not either fails or returns deleted rows (use the version lookup).

## Row-level operations

- **MERGE:** deduplicate the source on the join key first. Two source rows matching one target row make the MERGE fail. Put a partition predicate in the `ON` clause when the batch is time-bounded, so only affected partitions are scanned and rewritten.
- **DELETE:** a predicate aligned to whole partitions is a metadata-only commit. A predicate that cuts through files rewrites them (copy-on-write) or writes delete files (merge-on-read).
- **Idempotent backfill:** replace a partition range atomically (`INSERT OVERWRITE` with dynamic overwrite, or `overwritePartitions()`), and never use append-then-delete, which briefly exposes duplicates. In Spark's static overwrite mode, an `INSERT OVERWRITE` without a partition clause replaces the whole table.

## Time travel and rollback

- Rollback works only to snapshots that have not been expired: `CALL catalog.system.rollback_to_snapshot('db.events', <snapshot_id>)`.
- Before a risky backfill, record the current snapshot id, or tag it so expiry keeps it: `ALTER TABLE catalog.db.events CREATE TAG pre_backfill RETAIN 14 DAYS`. Tag and branch syntax is engine-specific (use the version lookup).
- Write-audit-publish: write to a branch, validate, then fast-forward `main`. Readers never see unvalidated data.

## Reading from other engines

- Read through the catalog, not a raw table path. A path-based scan can resolve an older `metadata.json` and silently return stale data.
- Before production use, run a smoke query from each engine, because readers differ in format-version and delete-file support.

## Verify

- [ ] Files per partition and average file size are near target: `SELECT partition, count(*), avg(file_size_in_bytes)/1e6 FROM catalog.db.events.files GROUP BY partition`.
- [ ] `EXPLAIN` of a typical query filtering on the source column plans far fewer files than the table holds.
- [ ] `catalog.db.events.snapshots` shows the expected `operation` per commit (append vs overwrite vs delete).
- [ ] Every reader engine returns the same row count for one partition.
