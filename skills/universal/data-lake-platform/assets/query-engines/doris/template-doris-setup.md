# Apache Doris Table Design and Loading

Use when Doris is the chosen serving layer and you are designing tables and loads. Whether to add a serving engine at all, and Doris vs ClickHouse vs StarRocks, is decided in [query-engine-patterns.md](../../../references/query-engine-patterns.md). Doris is MySQL-protocol MPP: frontends (FE) hold metadata and plan queries, backends (BE) store tablets and execute.

## Choose the Data Model (Cannot Be Changed Later)

| Data | Model | Why / trap |
|------|-------|-----------|
| Append-only events, logs | `DUPLICATE KEY` | Keeps every row. The key columns are only the sort prefix, not a uniqueness constraint |
| CDC / mutable entities (upserts, deletes) | `UNIQUE KEY` with merge-on-write (`"enable_unique_key_merge_on_write" = "true"`) | Merge-on-write resolves the newest row at load time, so reads stay fast. Merge-on-read loads cheaper but merges on every query, which is the wrong trade for a serving layer. Check your version's default |
| Pre-aggregated metrics only | `AGGREGATE KEY` with `SUM`/`MAX`/`MIN`/`REPLACE` | Raw rows are gone: you can never re-slice by a column you did not keep. `count(*)` on it is expensive and differs from row counts |

Changing the model means a new table and a full reload, so decide from the access pattern and the source's update semantics, not from the first query.

## Key Order and Prefix Index

- Key columns must be the first columns of the schema, in key order.
- Doris builds a sparse prefix index from the leading bytes of the sort key. A `VARCHAR` key column truncates the index at that column. Put the most-filtered, fixed-width columns (ids, dates) first and long strings last. Check the exact prefix length rules in the Doris docs for your version.

## Partitioning and Bucketing

- `PARTITION BY RANGE(<date>)` for time-series data. Use partitions for retention and for pruning time filters.
- **Dynamic partition retention deletes data.** With `dynamic_partition.enable = true`, a negative `dynamic_partition.start` (e.g. `-3` with `time_unit = MONTH`) **drops partitions older than that window**. Set it from the agreed retention, never copy it from an example. Leave it unset when history must be kept.
- `DISTRIBUTED BY HASH(<col>)`: hash on a high-cardinality column that queries join or group on, to avoid skew. A low-cardinality bucket column (status, country) creates hot tablets.
- Bucket count: size tablets to the per-tablet range the Doris docs recommend. Too many small tablets bloat FE metadata and compaction work; too few limit parallelism. Buckets per partition are fixed at creation, so size for expected growth (or use automatic bucketing if your version provides it).
- `replication_num = 3` needs at least three live BEs, or table creation and loads fail. Dev clusters need `1`.

## Loading and Idempotency

- **Stream Load (HTTP push):** every load carries a `label`. Doris rejects a second load with the same label in the same database, which gives **exactly-once retries** when the label is deterministic, e.g. `<table>_<source_file>_<offset_range>`. A random or timestamp label turns every retry into a duplicate load.
- **Routine Load (Kafka pull):** a job pauses when errors exceed `max_error_number` in a window. Monitor `SHOW ROUTINE LOAD` for `State = PAUSED` and read `ReasonOfStateChanged` and `ErrorLogUrls`. A paused job builds lag silently until someone looks.
- **Deletes into UNIQUE tables:** send them through the load (the hidden delete-sign column / `merge_type = DELETE` in Stream Load). Otherwise a deleted source row stays visible forever.
- Batch small writes. Many tiny `INSERT INTO ... VALUES` statements each create a version, and compaction falls behind ("too many versions" errors). Push small writes through Stream Load or a buffered loader.

## Materialized Views

- **Synchronous MVs (rollups)** live inside one table, are updated with every load, and are picked automatically by the optimizer. Use them for a few hot aggregations on a `DUPLICATE` table. Restrictions apply on `UNIQUE`/`AGGREGATE` models.
- **Asynchronous MVs** can span tables and external catalogs and refresh on a schedule or on base-table change. They are stale between refreshes, so state the staleness tolerance and check how query rewrite treats stale MVs.
- Every MV adds load-time and storage cost. Confirm with `EXPLAIN` that queries hit it before keeping it.

## Verify

- `SHOW BACKENDS`: all BEs alive; disk usage balanced (skew means a bad bucket column).
- `SHOW ROUTINE LOAD`: every job `RUNNING`; lag checked on the Kafka side.
- Re-sending one Stream Load with the same label is rejected as a duplicate, and the table count is unchanged.
- For `UNIQUE` tables: `count(*)` equals the source's live key count after deletes.
- `EXPLAIN` of the top dashboard queries shows partition pruning and, where intended, the MV/rollup.
