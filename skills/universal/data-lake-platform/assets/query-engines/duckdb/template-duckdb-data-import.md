# DuckDB Data Import and Export

Use when loading files or external databases into DuckDB, or writing Parquet out of it, and the result must be correct and reproducible. Basic `read_csv` / `read_parquet` / `COPY` syntax is assumed.

## CSV and JSON: Inference Traps

- **Type inference samples rows.** A column that looks numeric in the sample but holds `'N/A'` or a long id further down fails the load, or is mistyped. For production loads, declare types (`columns = {...}` / `types = {...}`), or widen the sample (`sample_size = -1` scans the whole file at extra cost).
- **`ignore_errors = true` drops bad rows silently.** If you need tolerance, capture the rejects instead (the `store_rejects` option, where available; check your version's `read_csv` docs) and assert the reject count is zero or within an agreed budget.
- **Globs with drifting schemas.** By default files are matched by position, which can misalign or fail when a column is added. Use `union_by_name = true` whenever files come from a producer whose schema evolves.
- **Keep lineage.** Add `filename = true` so every row records its source file. This is needed for reprocessing and for proving which file carried a bad row.
- Dates and timestamps: set `dateformat` / `timestampformat` explicitly for non-ISO inputs. Auto-detection can read `03/04` as either day-first or month-first depending on the sample.

## Parquet and Hive Layouts

- `hive_partitioning = true` exposes `key=value` directories as columns. Partition values may be read as strings or auto-cast, so check with `DESCRIBE` and filter with matching types, or pruning fails silently.
- Many small files (thousands of KB-sized files) cost more in per-file overhead than the data, especially on S3. Compact upstream, or compact once into DuckDB or larger files.

## External Databases (Postgres, MySQL, SQLite)

- Attach with `ATTACH '<connection>' AS src (TYPE postgres, READ_ONLY)`. Keep credentials in DuckDB secrets (`CREATE SECRET`) or environment variables, not in connection strings saved in scripts.
- Point large extracts at a **read replica**. A full-table scan through the scanner is a long-running query on the source and competes with production traffic.
- Scans are not guaranteed to be one consistent snapshot across several tables. Extract related tables inside one source transaction or from a replica snapshot if referential consistency matters.
- For repeated work, copy into local DuckDB tables once (`CREATE TABLE ... AS SELECT`) rather than querying the remote table in every step.

## Incremental Loads and Upserts

- `WHERE ts > (SELECT max(ts) FROM target)` loses late-arriving rows and rows sharing the max timestamp. Reprocess an overlap window and upsert by key instead:

```sql
CREATE TABLE IF NOT EXISTS orders (order_id BIGINT PRIMARY KEY, status VARCHAR, updated_at TIMESTAMP);

INSERT INTO orders
SELECT order_id, status, updated_at
FROM read_parquet('landing/orders/*.parquet', filename = true)
WHERE updated_at >= (SELECT coalesce(max(updated_at), TIMESTAMP '1970-01-01') FROM orders) - INTERVAL 2 DAY
QUALIFY row_number() OVER (PARTITION BY order_id ORDER BY updated_at DESC) = 1  -- one row per key per batch
ON CONFLICT (order_id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at
WHERE excluded.updated_at > orders.updated_at;                                   -- never regress a newer row
```

- Deduplicate within the batch before `ON CONFLICT`. Two rows for the same key in one statement raise a conflict error.
- The overlap window (2 days here) is a placeholder: set it from the source's observed maximum lateness.
- Deletes in the source are invisible to this pattern. Use a CDC feed or periodic full-key reconciliation (anti-join on keys).

## Writing Parquet for Later Reads

- Sort before writing by the column most queries filter on (`COPY (SELECT ... ORDER BY customer_id, event_date) TO ...`). Row-group min/max statistics can only prune when the data is clustered.
- Compression: the Parquet default (Snappy) favors read speed and compatibility; `ZSTD` gives smaller files at extra write cost and is the usual choice for lake storage. Pick one per dataset and keep it consistent.
- `PARTITION_BY (col)` writes Hive-style directories. Partition only on low-cardinality columns queried by equality or range (date, region). Partitioning by a high-cardinality column produces a flood of tiny files. See [template-partitioning-strategy.md](../../cross-platform/template-partitioning-strategy.md).
- Re-running a partitioned `COPY` into an existing directory fails or mixes old and new files, depending on the `OVERWRITE`/`OVERWRITE_OR_IGNORE` options. Write to a fresh path and swap, so a failed run never leaves half-written partitions visible to readers.
- If the output is meant to be a lake table (multiple writers, time travel, schema evolution), write through a table format (Iceberg/Delta/DuckLake) instead of loose Parquet files.

## Verify

- Row count in equals row count out plus rejects, per source file (`GROUP BY filename`).
- `DESCRIBE` of the loaded table matches the declared types; no column silently became `VARCHAR`.
- Primary-key uniqueness holds after upserts (`count(*) = count(DISTINCT key)`).
- Re-running the same load produces an identical table (idempotency), and a re-read of the written Parquet returns the same aggregates as the source query.
