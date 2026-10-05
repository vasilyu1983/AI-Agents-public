# ClickHouse Table and Query Optimization

Use when designing a ClickHouse table or diagnosing a slow query. Schema decisions (sort key, engine, partition) dominate; server knobs come last.

## Sort Key (ORDER BY) and Primary Key

The sparse primary index stores one mark per granule (`index_granularity` rows, 8192 by default). A query skips granules only when its filter constrains a **prefix** of the sort key. Choose `ORDER BY` by these rules, in order:

1. **Lead with the columns almost every query filters on with equality**, e.g. `tenant_id` in a multi-tenant table. Filters on later key columns only prune well when earlier columns have few distinct values.
2. **Order the leading columns from low to high cardinality.** This helps pruning on later columns and compresses better, because sorted runs of repeated values compress well.
3. **Put the timestamp after the equality columns** unless most queries filter only by time range. `ORDER BY (tenant_id, event_type, created_at)` serves "tenant X, last 7 days"; `ORDER BY (created_at, ...)` makes every other column useless for pruning.
4. **Never lead with a unique id** (`event_id`, UUID). Doing so disables pruning on every other column. Point lookups by id belong in a skip index or a lookup table.
5. **`PRIMARY KEY` may be a shorter prefix of `ORDER BY`.** Use this when the engine needs a long sort key (the dedup/summing key) but the index only needs its first columns; it keeps the in-memory index small.
6. **The sort key is effectively permanent.** `ALTER ... MODIFY ORDER BY` can only append columns added in the same `ALTER`. Any other change means a new table plus `INSERT ... SELECT`, so validate the key against real query logs before loading production data.

## Partition Key

- Partitions are for data management (TTL, `DROP PARTITION`, `REPLACE PARTITION` for backfills), not for query speed. The sort key does the pruning.
- Keep partition cardinality low: monthly (`toYYYYMM`) by default, daily only for high-volume tables with short retention. Each insert creates at least one part **per partition it touches**, so a fine-grained key multiplies part counts.
- Never partition by a column that changes over a row's life (status, `updated_at`). With `ReplacingMergeTree`, versions of one key that land in different partitions are **never** merged, so they never deduplicate.

## Table Engine Choice

| Need | Engine | Caveat that bites |
|------|--------|-------------------|
| Append-only facts, logs | `MergeTree` | Default. Choose it unless you need merge-time semantics |
| Newest version per key (CDC, upserts) | `ReplacingMergeTree(version)` | Dedup happens **only during background merges**, only within one partition and one shard, and merges are not guaranteed to ever run. Duplicates are visible until then |
| Pre-summed counters | `SummingMergeTree` | Only additive columns. `uniq`, averages and quantiles cannot be summed; queries must still `sum() ... GROUP BY` because unmerged rows coexist |
| Distinct counts, quantiles, averages | `AggregatingMergeTree` with `-State` / `-Merge` | Insert with `uniqState(...)`, read with `uniqMerge(...)`; use `SimpleAggregateFunction` for `sum`/`max`/`min`/`any` (cheaper) |

**Reading a `ReplacingMergeTree` correctly:** pick one and apply it everywhere:

- `SELECT ... FROM t FINAL`: correct but merges at read time. Cost grows with unmerged parts. It is cheaper when the partition key guarantees all versions of a key share a partition (then partitions can be finalized independently; check the `FINAL`-related settings for your version).
- `argMax(col, version) ... GROUP BY key`: explicit and portable; the default for views and BI.
- Deletes: write a tombstone version with `is_deleted = 1` and filter it out. Some releases accept `ReplacingMergeTree(version, is_deleted)` to drop tombstones at merge; check your version's release notes before relying on it.

Do not schedule `OPTIMIZE TABLE ... FINAL` as a dedup mechanism. It rewrites whole partitions, competes with inserts for merge threads, and still leaves duplicates from rows inserted afterwards.

## Column Types and Codecs

- Use the smallest type that fits; unsigned when values cannot be negative; `Decimal` for money.
- `LowCardinality(String)` pays off below roughly 10k distinct values per part. Above that the dictionary overhead outweighs the gain.
- Avoid `Nullable`: it adds a null-mask stream per column and blocks some optimizations. Use a default value (`''`, `0`) unless NULL has business meaning.
- Codecs: `Delta`/`DoubleDelta` + `ZSTD` for monotonic integers and timestamps, `Gorilla` for float gauges, higher `ZSTD` levels for large JSON/text blobs. Measure with `system.columns` (`data_compressed_bytes` vs `data_uncompressed_bytes`) before and after; do not apply codecs by folklore.

## Query-Side Levers

- **PREWHERE:** ClickHouse moves selective `WHERE` conditions to `PREWHERE` automatically. Write it explicitly only when `EXPLAIN` shows the optimizer chose badly, e.g. the cheap selective filter sits on a small column.
- **Projections:** give a second sort order or pre-aggregation inside the same table. They cost extra storage and insert/merge work. Check engine support before using them on non-plain `MergeTree` engines, because behavior with Replacing/Collapsing engines is version-dependent.
- **Skip indexes** (`minmax`, `set`, `bloom_filter`, `tokenbf_v1`) only skip granules when matching values are clustered. A bloom filter on a random id spread across all granules skips nothing and still costs insert time. Prove the effect with `EXPLAIN indexes = 1`.
- **Joins:** by default the right-hand table is built into an in-memory hash table. Put the smaller side on the right, or turn small dimensions into dictionaries (`dictGet`). For large-large joins, pre-join in the pipeline or co-locate on a shard key.
- **Sampling:** `SAMPLE BY` must be part of the sort key and use a hashed column (`intHash32(user_id)`). It cannot be added cheaply later, so decide at table creation.

## Part Count and Merges

Too many active parts per partition is the most common ClickHouse production failure. Inserts are first slowed, then rejected with "Too many parts". The limits are the MergeTree settings `parts_to_delay_insert` and `parts_to_throw_insert`; read the actual values from `system.merge_tree_settings` instead of assuming them. Causes and fixes are in [template-clickhouse-ingestion.md](template-clickhouse-ingestion.md#part-count-and-insert-batching).

```sql
SELECT database, table, partition, count() AS active_parts
FROM system.parts WHERE active
GROUP BY database, table, partition
ORDER BY active_parts DESC LIMIT 20;
```

## Verify

- `EXPLAIN indexes = 1 <query>` shows selected granules far below total granules for the main dashboard queries.
- `system.query_log`: `read_rows` for the top queries is close to the rows they logically need, not the table size.
- A `ReplacingMergeTree` table returns the same count with `FINAL` and with the `argMax` query, and both match the source key count.
- Active parts per partition stay flat under normal load; merges keep up (`system.merges` is not permanently saturated).
