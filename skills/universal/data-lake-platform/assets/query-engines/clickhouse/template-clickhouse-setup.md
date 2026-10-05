# ClickHouse Setup

Use when deciding whether to add ClickHouse as a serving layer and how to size its first deployment. Table design lives in [template-clickhouse-optimization.md](template-clickhouse-optimization.md); clusters in [template-clickhouse-replication.md](template-clickhouse-replication.md).

## Add a Serving Engine at All?

Engine choice across Trino, Spark, DuckDB and serving stores is in [query-engine-patterns.md](../../../references/query-engine-patterns.md). Add ClickHouse only when all of these hold:

- A measured workload misses its latency or concurrency target on the lake query layer (Trino/Spark/DuckDB) after partition pruning, file compaction and a pre-aggregated table were tried. "Dashboards feel slow" is not a measurement.
- The access patterns are known and stable enough to design an `ORDER BY` for. ClickHouse rewards tables modelled per query shape and punishes ad-hoc joins across many large tables.
- Someone owns a second copy of the data: its freshness SLA, backfills, schema changes and deletes (GDPR erasure must reach it too).

Keep the lake (or the raw ingest log) as the source of truth. Anything in ClickHouse must be rebuildable from it; if it is not, you have created a second system of record.

## Deployment Shape

| Situation | Default | Why |
|-----------|---------|-----|
| Dev, CI, a single dashboard on modest data | Single node | No Keeper, no distributed DDL; one node goes a long way on columnar scans |
| Production, data fits on one node | 1 shard x 2 replicas + 3 Keeper nodes | Replication gives availability; sharding adds distributed-query cost you do not need yet |
| Working set or insert rate exceeds one node | N shards x 2 replicas | Shard only when one node's disk, CPU or insert throughput is proven insufficient; adding shards later does not rebalance existing data |
| No team to run Keeper, upgrades and backups | Managed service | Ops capacity is the real constraint; compare cost against the engineer time, not the VM price |

Replicate before you shard. Most "we need a cluster" requests are availability requests.

## Server Settings That Are the Lesson

- **Memory:** set a per-query `max_memory_usage` and a server-wide `max_server_memory_usage_ratio` below 1 so one query cannot OOM-kill the server. Set `max_bytes_before_external_group_by` and `max_bytes_before_external_sort` to roughly half of `max_memory_usage` so large aggregations spill to disk instead of failing.
- **File descriptors:** raise `nofile` well above the OS default; each part is several files and merges open many at once.
- **Timezone:** set the server `timezone` to UTC and store `DateTime` in UTC; convert at query time. Mixed server timezones break `toDate()` partitioning across replicas.
- **Storage:** local SSD/NVMe for hot data; object storage disks or tiered `TTL ... TO VOLUME` only after measuring cold-query latency.

## Access Control

- Never ship the `default` user with an empty password or `::/0` networks.
- Give BI tools a separate read-only user (`readonly = 1`, or `2` if the tool must set session settings) with its own profile: `max_execution_time`, `max_memory_usage`, `max_result_rows`, and a quota. One runaway dashboard query should hit its own limit, not the server's.
- Give each ingestion job its own user so `system.query_log` attributes load and failures.

## Layer Tables and Engine per Layer

| Layer | Engine | Key choices |
|-------|--------|-------------|
| Bronze (raw landing) | `MergeTree` | `ORDER BY` on ingest time + load id; `TTL` = raw retention window; keep payload as a compressed `String` |
| Silver (current state) | `ReplacingMergeTree(version)` | `ORDER BY` = the business key (it is the dedup key); partition by an immutable date, never by the version column |
| Gold (serving aggregates) | `AggregatingMergeTree` / `SummingMergeTree`, fed by MVs | See [template-clickhouse-materialized-views.md](template-clickhouse-materialized-views.md) |

```sql
-- Silver: the version column and ORDER BY are the lesson
CREATE TABLE silver.users (
    user_id     UInt64,
    email       String,
    signup_date Date,
    updated_at  DateTime64(3),
    is_deleted  UInt8
)
ENGINE = ReplacingMergeTree(updated_at)  -- highest updated_at wins at merge time
PARTITION BY toYYYYMM(signup_date)       -- immutable per key, so all versions share a partition
ORDER BY user_id;                        -- dedup key; cannot be changed in place
```

Dedup-at-merge caveats for `ReplacingMergeTree` are in [template-clickhouse-optimization.md](template-clickhouse-optimization.md#table-engine-choice).

## Verify

- `SELECT * FROM system.clusters` lists every expected replica; `errors_count` is 0.
- `SELECT database, table, is_readonly, absolute_delay FROM system.replicas` shows no read-only replica and near-zero delay.
- `system.disks` free space stays above what the largest merge needs (a merge can temporarily need space close to the size of the parts it rewrites).
- The BI user cannot run `INSERT`, `ALTER` or `DROP`, and hits its own memory/time limit on a deliberately heavy query.
- A rebuild of one gold table from the lake or bronze layer has been rehearsed and timed.
