# Cost Optimization Template

Use when running a cost review of a lake or ClickHouse deployment: storage, compute, and ingestion. The principles are in [references/cost-optimization.md](../../references/cost-optimization.md); this template is the working checklist and its traps.

## Order of work

1. **Measure first.** Rank queries by bytes read, and tables by size and file count, before changing anything. A few query shapes usually dominate cost.
2. **Fix the layout** (partitioning, sort order, file size): see [template-partitioning-strategy.md](template-partitioning-strategy.md) and [template-parquet-optimization.md](../storage/parquet/template-parquet-optimization.md). Bytes scanned drop for every query at once.
3. **Fix retention:** snapshot expiry, VACUUM or cleaning, data TTL. Retained snapshots keep deleted and replaced files billable.
4. **Only then** pre-aggregate hot queries, or add compute.

## Storage

- **Codec:** use Parquet + zstd for lake data. For ClickHouse, choose codecs per column type as described in [template-clickhouse-optimization.md](../query-engines/clickhouse/template-clickhouse-optimization.md). Ratios depend on data, so measure the compressed vs uncompressed bytes of one representative partition before and after. Do not budget from a published ratio table.
- **Small files:** compaction pays for itself through fewer object requests and faster planning. The schedule and order are in [template-iceberg-maintenance.md](../storage/iceberg/template-iceberg-maintenance.md). For Delta and Hudi, see their table templates.
- **Retention:** the snapshot and file retention window comes from the time-travel need, consumer lag, and the erasure SLA; see the maintenance template. Longer retention than that is pure storage cost.

### Tiering: the trap

- **Never apply object-store lifecycle transitions or expirations to prefixes a live table still references.**
  - An expiration rule deletes files that snapshots point to, which corrupts the table.
  - A transition to a storage class that needs a restore before reading makes queries fail.
  - Infrequent-access classes stay readable but add per-GB retrieval fees and minimum-duration charges. They lose money on data that is still scanned.
- Tier with the table format instead: expire or delete old data through the table (snapshot expiry, `DELETE` plus VACUUM, partition drops), or move old partitions into a separate archive table that has its own location and lifecycle.
- Safe targets for raw lifecycle rules are temp and staging prefixes, bronze landing files past the replay window, and exported archives outside any table location.
- ClickHouse: tier with a storage policy and `TTL ... TO VOLUME 'cold'`, and drop with `TTL ... DELETE` aligned to partitions. The engine moves whole parts, so queries stay correct.

## Compute

- Read only the needed columns, and filter on partition and sort columns without wrapping them in functions. `SELECT *` and `CAST(col) = ...` defeat pruning.
- Pre-aggregate hot dashboard queries with materialized views or rollup tables, or with projections in ClickHouse, instead of scaling the cluster. Each one adds insert and merge cost, so build one only for a query shape that is actually hot.
- Use approximate distinct counts (HLL-style) where exactness is not required.
- Guard shared clusters with per-role limits, such as ClickHouse settings profiles (`max_bytes_to_read`, `max_execution_time`, `max_memory_usage`) or warehouse resource groups. Size the limits from the observed 99th-percentile legitimate query, not from round numbers, so they stop runaway queries without blocking normal work.

## Ingestion

- Fewer, larger batches lower both compute and storage cost: fewer commits, files, and parts. ClickHouse batching, async inserts, and buffer tables are covered in [template-clickhouse-ingestion.md](../query-engines/clickhouse/template-clickhouse-ingestion.md).
- Load columnar files (Parquet) rather than JSON where the loader supports it; that saves parsing CPU and typing work.
- Streaming into lake tables creates small files and many snapshots by design. Budget compaction as part of the pipeline's cost.

## Monitoring

Scan-based cost: take the per-TB-scanned price from your own billing or contract, never from a constant in code.

```sql
-- ClickHouse: bytes read per user and query kind over the last 7 days
SELECT user, query_kind, count() AS queries,
       formatReadableSize(sum(read_bytes)) AS read,
       round(sum(query_duration_ms) / 1000) AS seconds
FROM system.query_log
WHERE event_date >= today() - 7 AND type = 'QueryFinish'
GROUP BY user, query_kind
ORDER BY sum(read_bytes) DESC;
```

- Alert on **trends against the table's own baseline** rather than fixed dollar or GB thresholds: bytes read per day, storage growth per week, and average file size falling (compaction missing).
- Track storage per table, including snapshot overhead. For Iceberg, compare bytes of distinct `file_path` in `all_files` against `files`: the difference is roughly what expiry would reclaim.

## Verify

- [ ] Every production lake table has scheduled compaction and snapshot expiry (or VACUUM or cleaning).
- [ ] Lifecycle rules touch only non-table prefixes or prefixes the table format has already released.
- [ ] Top-cost queries were reviewed with their scan bytes before compute was added.
- [ ] Each layout or codec change was measured before and after on the same partition and query.
