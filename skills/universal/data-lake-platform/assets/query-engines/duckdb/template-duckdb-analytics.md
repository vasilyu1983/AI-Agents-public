# DuckDB Analytics Query Review

Use when a DuckDB query over Parquet, CSV or a `.duckdb` file is slow or runs out of memory. Where DuckDB fits and where it does not is covered in [query-engine-patterns.md](../../../references/query-engine-patterns.md).

## Fit Check First

- DuckDB is in-process and single-node: one read-write process per database file, with any number of read-only readers. If the requirement is many concurrent writers or a shared dashboard backend with high QPS, the fix is a different engine, not tuning.
- Querying the same Parquet repeatedly (dashboards, notebooks)? Load it once into a `.duckdb` table. Native storage keeps zone maps and compression tuned for DuckDB and avoids re-reading file footers, which is especially costly on object storage.

## Read the Plan

Run `EXPLAIN ANALYZE <query>` and check, in this order:

1. **Scan volume.** Does the `READ_PARQUET` / `TABLE_SCAN` node list only the needed columns, and do its filters appear *inside* the scan? Projection and filter pushdown are automatic. When they are missing, the query shape blocks them (next section).
2. **Row-group pruning.** Filters skip Parquet row groups only by their min/max statistics, so pruning works only when the data is **sorted or clustered by the filter column**. A `WHERE customer_id = ...` on randomly ordered files reads everything. The fix is on the write side: sort by the common filter column before writing (see [template-duckdb-data-import.md](template-duckdb-data-import.md#writing-parquet-for-later-reads)).
3. **Partition pruning.** With `hive_partitioning = true`, a filter on the partition column should cut the file list. If the partition values were read as strings and the filter compares numbers, pruning can silently fail; cast consistently.
4. **Operator memory.** Large hash joins, `GROUP BY` on high-cardinality keys, sorts, and window functions are where memory goes. Check which operator dominates.

## Query Shapes That Block Pushdown

- Functions on the filtered column (`WHERE lower(region) = 'us'`, `WHERE CAST(ts AS DATE) = ...`) disable statistics-based skipping. Compare the raw column to a constant or range (`ts >= '<start>' AND ts < '<end>'`), or normalize the data at write time.
- `SELECT *` on wide Parquet reads every column chunk. Name columns, especially in views that other queries build on.
- Filters applied only after a join or in an outer query can block pushdown in complex plans. Check the plan; do not assume.

## Memory and Parallelism

- `memory_limit` defaults to a large share of system RAM. In containers, set it explicitly below the container limit, or the OS kills the process before DuckDB spills.
- Set `temp_directory` to a fast disk with room. Joins, aggregations and sorts can spill larger-than-memory work there instead of failing.
- For large `COPY`/`CREATE TABLE AS` jobs where output order does not matter, `SET preserve_insertion_order = false` cuts memory use substantially.
- `threads` defaults to the core count, and raising it past that does not help CPU-bound queries. Queries over remote files (S3/HTTP) are I/O-latency-bound and can benefit from more threads than cores; measure.
- DuckDB parallelizes Parquet scans by row group. A single file with one huge row group, or thousands of tiny files, both limit parallelism. Aim for files of tens to hundreds of MB with multiple row groups.

## Joins and Aggregations

- The optimizer reorders joins and picks the hash-build side from cardinality estimates. Hand-ordering tables rarely helps; stale or missing statistics on raw files are the usual cause of a bad plan. Materializing a filtered side into a temp table often fixes it.
- For exploration on huge data, `approx_count_distinct` and `approx_quantile` are far cheaper than exact versions. Label the results as approximate.
- Window functions over a huge single partition (no `PARTITION BY`) sort everything in one pass. Partition when the logic allows.

## Verify

- Record wall time and bytes scanned before and after each change on the same data and warm/cold cache state; change one thing at a time.
- The `EXPLAIN ANALYZE` scan node reads only the needed columns and a fraction of row groups for selective filters.
- Results match the pre-optimization query exactly, or within stated error for approximate functions.
- Peak memory stays under `memory_limit` without spill errors at production data size, not just on a sample.
