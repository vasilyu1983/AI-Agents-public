# Cost Optimization

Lake cost is driven by bytes scanned, file count, and retained storage. Fix layout first, then compute. Templates: [template-cost-optimization.md](../assets/cross-platform/template-cost-optimization.md), [template-partitioning-strategy.md](../assets/cross-platform/template-partitioning-strategy.md).

## Storage

- **Compression**: Parquet + ZSTD (moderate level) is the default. Snappy/LZ4 only when decode CPU is the proven bottleneck. Ratios depend on cardinality, types, and sort order, so no fixed percentage holds: write one representative partition with each candidate codec and compare size and scan time.
- **Partitioning**: size time granularity from volume — the finest grain at which one partition still holds several target-size files (daily is the common result; small tables go monthly). Add `bucket(N, key)` for high-cardinality filter/join keys. Hourly creates 24x the partitions of daily — use it only when each hourly partition still yields files near the target size and queries routinely filter by hour. Full rules: [template-partitioning-strategy.md](../assets/cross-platform/template-partitioning-strategy.md).
- **File size**: small files multiply metadata, planning time, and request costs. Keep files near the target size with compaction; see [storage-formats.md](storage-formats.md) and the Parquet template.
- **Retention**: expire snapshots and old data on a schedule; retained snapshots keep deleted files billable. Tier cold prefixes (e.g. bronze after the replay window) with object-store lifecycle rules, and expire temp/staging prefixes. Never tier or expire files an active snapshot references — use table-format expiry, not raw lifecycle rules, on table data.

## Compute

- Read only needed columns and filter on partition/sort columns so pruning works; `SELECT *` defeats columnar formats.
- Pre-aggregate hot dashboard queries (materialized views or rollup tables) instead of scaling the engine.
- Use approximate distinct counts (HLL-style) where exactness is not required.
- Serving engines (ClickHouse etc.): match the table sort key to the dominant filter; see the ClickHouse templates under `assets/query-engines/`.

## Monitoring

- Track bytes read and query time per user/query kind from the engine's query log, weekly; the top few query shapes usually dominate cost.
- Track table size, file count, and average file size per table; a falling average file size is the early signal of a missing compaction job.

## Verify

- [ ] Every production table has a compaction and snapshot-expiry schedule.
- [ ] Object-store lifecycle rules touch only non-table or explicitly expired prefixes.
- [ ] Top-cost queries reviewed with their scan bytes before adding compute.
