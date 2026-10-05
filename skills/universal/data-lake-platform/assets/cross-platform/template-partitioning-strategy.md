# Partitioning Strategy Template

Use when choosing the partition key and granularity for a lake table (Iceberg, Delta, Hudi, Hive-style Parquet) or a ClickHouse table, or when diagnosing partition-related slowness.

## Rules

1. **Partition only on what nearly every query filters on, or on the unit of data management** (retention drops, partition-replace backfills). Everything else belongs in sorting, clustering, or Z-order within partitions.
2. **Low cardinality only.** Never partition on user, session, order, or device ids. Use `bucket(N, key)` (Iceberg), clustering (Delta), or the sort key (ClickHouse) instead.
3. **Size from the data.** Pick the finest time granularity at which one partition still holds at least about 1 GB, which is several target-size files after compaction. Worked examples:
   - At 5 GB/day, daily partitions are about 5 GB and number 365 a year: fine.
   - At 200 MB/day, daily partitions hold only one or two files, so go monthly (about 6 GB).
   - Go hourly only at tens of GB per day **and** when queries filter by hour.
   - These are starting points; tune by measuring files per partition and planning time.
4. **Bound the partition count.** Keep total partitions over the retention period in the low thousands per table. Each partition adds listing, planning, and metastore cost. In ClickHouse, it multiplies parts.
5. **Composite keys multiply.** Region × category × day is the product of their cardinalities. Compute it before creating the table.
6. **Partitioning is not sorting.** Partitions prune coarsely; the sort key, clustering, or Z-order prunes within them. Decide both.
7. **Partition by immutable attributes.** A partition value that changes over a row's life (status, `updated_at`) causes duplicates or missed dedup in upsert engines: Hudi non-global indexes and ClickHouse `ReplacingMergeTree`.

## Engine specifics

### Iceberg

- Hidden partitioning: transforms (`days(ts)`, `bucket(N, id)`, `truncate(W, s)`) derive partition values, and queries filter on the source column.
- Partition evolution is metadata-only; old files keep the old spec.
- Details, including how to choose the bucket count, are in [template-iceberg-table.md](../storage/iceberg/template-iceberg-table.md#partition-spec).

### Delta

- Prefer liquid clustering when every reader supports it. Otherwise, derive the partition column from the timestamp with a generated column so timestamp filters prune.
- Commonly cited vendor guidance is to not partition tables below roughly 1 TB. See [template-delta-table.md](../storage/delta/template-delta-table.md#layout-decision).

### Hive-style Parquet (raw files read by DuckDB, Spark, Trino)

- Partition values live only in directory names (`event_date=<date>/`). A filter must target the partition column itself. A filter on `created_at` alone does **not** prune `year=/month=` directories, so write a date partition column and filter on it.
- Path values are strings. Engines infer their types differently (`month=01` vs `1`), so zero-pad consistently or declare the partition types explicitly.
- Overwrite writes must be partition-scoped. A dataset-level "overwrite" mode can delete partitions the job never meant to touch.

### ClickHouse

- `PARTITION BY` is for data management: TTL, `DROP PARTITION` for retention, and `REPLACE PARTITION ... FROM staging` for atomic backfills. It does not speed up queries; the `ORDER BY` key does the pruning.
- Default to monthly (`toYYYYMM(ts)`), and use daily only for high-volume tables with day-level retention operations. Merges never cross partitions, and each insert creates at least one part per partition it touches. Fine partitions therefore lead to "too many parts".
- For retention, prefer whole-partition drops or `TTL ... DELETE` with `ttl_only_drop_parts = 1` on partition-aligned TTLs. Row-level TTL deletes rewrite parts.
- Sort-key rules and skip indexes: [template-clickhouse-optimization.md](../query-engines/clickhouse/template-clickhouse-optimization.md).

## Anti-patterns

| Pattern | Problem | Fix |
|---------|---------|-----|
| `PARTITION BY user_id` | Millions of tiny partitions | Bucket, cluster, or sort by `user_id` |
| Daily partitions on a table with a few hundred MB per day | One or two small files per partition, and a slow planner | Monthly partitions plus a sort on the time column |
| `(region, category, day)` | Cartesian explosion of partitions | Keep time only; cluster by region and category |
| Filtering on a derived column in some queries and the source column in others | Pruning works only for some queries | Standardize on the source column (Iceberg) or on the partition column (Hive-style) |

## Verify

- [ ] Partition size distribution: files and bytes per partition, and skew (largest vs median). Engine views: the Iceberg `files`/`partitions` metadata tables, Delta `DESCRIBE DETAIL` per partition, ClickHouse `system.parts WHERE active`.
- [ ] Pruning: `EXPLAIN` of the top queries reads far fewer partitions or files than the total. In ClickHouse, `EXPLAIN indexes = 1` shows the parts and granules selected.
- [ ] The projected partition count over the full retention period stays within the bound in rule 4.
