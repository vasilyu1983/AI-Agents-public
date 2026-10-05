# StarRocks Table Design and Lake Acceleration

Use when StarRocks is the chosen serving layer, either on native tables or accelerating an Iceberg/Hive/Delta lake through external catalogs. Whether to add it at all is decided in [query-engine-patterns.md](../../../references/query-engine-patterns.md). Table-model, bucketing, label and Routine Load rules largely mirror Doris ([template-doris-setup.md](../doris/template-doris-setup.md)); this file covers what differs.

## Query the Lake in Place or Copy?

Default to **external catalog + async materialized views** and keep the lake as the only copy. Copy data into native tables only when you need:

- sub-second latency at high concurrency that MVs over external data do not reach in a measured test, or
- real-time upserts/deletes at a freshness the lake's commit cadence cannot give.

Every native copy is a second system of record that needs its own backfill, deletes and schema changes.

## Native Table Models

| Data | Model | Trap |
|------|-------|------|
| Mutable entities, CDC | `PRIMARY KEY` | The primary-key index is held in memory unless the persistent index is enabled. Size BE memory against key count x key width, or enable `enable_persistent_index` to trade memory for disk. Keep the key narrow (integers, not long strings) |
| Append-only events | `DUPLICATE KEY` | Keys only define sort order, not uniqueness |
| Pre-aggregated counters | `AGGREGATE KEY` | Raw rows are lost; prefer an MV over a `DUPLICATE` table if raw data may be needed later |

- Deletes into `PRIMARY KEY` tables arrive through the load: the `__op` column in Stream Load or Routine Load. Without it, deleted source rows stay.
- Partial-column updates are supported on `PRIMARY KEY` tables, but they rewrite more than they appear to. Test load throughput before using them on wide tables.
- Partition by time for retention; hash-distribute on a high-cardinality join/group column. The same skew and tablet-size rules as Doris apply.

## External Catalogs

- Create one catalog per metastore (Iceberg REST/Glue/Hive). Authenticate with instance roles or catalog-level credentials managed by the platform, never access keys in DDL, which is stored in metadata and visible to admins.
- **Metadata caching means staleness.** New snapshots or files written by Spark/Flink may not be visible until the cached metadata refreshes. Know the refresh interval and how to force a refresh before debugging "missing rows".
- Pruning depends on the lake layout: partition columns and file statistics. A badly partitioned Iceberg table stays slow through StarRocks too; fix the layout ([template-partitioning-strategy.md](../../cross-platform/template-partitioning-strategy.md)).

## Async Materialized Views over the Lake

```sql
CREATE MATERIALIZED VIEW mv_daily_events
PARTITION BY event_date                     -- align with the base table's partitions -> incremental refresh
DISTRIBUTED BY HASH(event_type)
REFRESH ASYNC EVERY (INTERVAL 1 HOUR)       -- no hard-coded START date
AS SELECT event_date, event_type, count(*) AS events, count(DISTINCT user_id) AS users
FROM lake.analytics.events
GROUP BY event_date, event_type;
```

- **Partition-align the MV with the base table.** Only changed partitions refresh; an unpartitioned MV recomputes everything on every refresh.
- **Transparent rewrite skips stale MVs** unless you allow bounded staleness (an MV property; check the name in your version's docs). If dashboards "stop using" the MV after a lake write, this is why.
- `count(DISTINCT)` in an MV only rewrites queries at the MV's grain or finer. Rolling distinct counts up to a coarser grain needs bitmap/HLL columns, not re-summing.
- Check refresh health in the MV task history (`information_schema.task_runs`) and alert on failed or overdue refreshes.

## Verify

- `EXPLAIN` / query profile of the top dashboard queries shows the MV rewrite and partition pruning on external scans.
- After a lake write, the MV and the direct external query agree once the refresh interval plus cache refresh has passed.
- `PRIMARY KEY` tables: `count(*)` equals the source's live key count after deletes; BE memory headroom is monitored.
- Re-sending a Stream Load with the same label is rejected, not double-loaded.
