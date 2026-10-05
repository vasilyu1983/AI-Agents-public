# dlt Destination and Warehouse Loading Template

Use when choosing or tuning where a dlt pipeline loads: warehouse, database, or lake filesystem. Pipeline identity and dispositions: [template-dlt-pipeline.md](template-dlt-pipeline.md). Merge and incremental semantics: [template-dlt-incremental.md](template-dlt-incremental.md).

## Choose the Destination Path

| Situation | Load path | Reason |
|---|---|---|
| Warehouse (Snowflake, BigQuery, Redshift, Databricks), non-trivial volume | Stage files in object storage (`staging="filesystem"`), then bulk `COPY` | Bulk copy from staged files is faster and cheaper than inserts; staged files double as a raw archive |
| Postgres or another OLTP-style database | Direct load (insert) | No bulk-copy path worth the extra moving part |
| Lakehouse bronze layer | `filesystem` destination with a table format (Delta or Iceberg; check the dlt docs for current support) | Open files readable by any engine; table format adds atomic commits and schema history |
| Local development, tests | DuckDB | Same pipeline code; swap the destination in config |

```python
pipeline = dlt.pipeline(
    pipeline_name="crm_to_snowflake",
    destination="snowflake",
    staging="filesystem",          # bucket_url and credentials in config/secrets
    dataset_name="source_crm",
)
pipeline.run(source, loader_file_format="parquet")
```

## File Format

- Prefer `parquet` for warehouse loads: typed and compressed, avoids JSON type guessing on load.
- Use `jsonl` when the payload has deeply nested or highly variable structures the Parquet writer cannot type cleanly.
- Keep the same format for the life of a table where possible; switching can change inferred types.

## Physical Layout Hints

- Declare partitioning, clustering, sort, and distribution through dlt column hints or the destination's adapter (for example the BigQuery adapter for partition and cluster). Check the destination page in the dlt docs for which hint maps to which physical property; hint names are not uniform across destinations.
- Partition by the column queries filter on (usually an event or business date), not by `_dlt_load_id`. Partitioning by load id helps only load auditing.
- Set layout on the **first** load. Partitioning usually cannot be changed on an existing table (clustering often can); changing it later means a rebuild (`refresh="drop_resources"` or a manual copy), and dlt does not alter layout of a table it already created.
- Merge loads scan the target by key: cluster or sort by `primary_key` (or partition by `merge_key`) on large merge tables, or every merge becomes a full-table scan.

## Loading Mechanics and Traps

- `merge` loads go to a staging dataset (`<dataset>_staging`) and are merged in the destination. The loading role needs create rights on that dataset.
- A run can finish with failed jobs. Call `load_info.raise_on_failed_jobs()` (or confirm the raise-on-failure setting) so an orchestrator sees the failure.
- Load parallelism is the `[load] workers` config, not a `run()` argument. Raise it only when the destination accepts concurrent copies without queueing.
- Identifier casing: dlt normalizes names (snake_case by default). Snowflake upper-cases unquoted identifiers; downstream SQL must use the normalized names.
- Loading the same source into several destinations: one pipeline per destination, each with its own `pipeline_name`. Sharing a name shares state and cursor.

## Cost

- Use a dedicated, small warehouse/compute for loading with auto-suspend; size up only if load time breaks the freshness target.
- Incremental extraction (see [template-dlt-incremental.md](template-dlt-incremental.md)) is the largest cost lever: repeated `replace` of large tables pays for the full scan and full write every run.
- Set lifecycle rules on the staging bucket; staged files accumulate indefinitely otherwise.
- Keep only the load packages you need locally; completed packages can be deleted once loaded (see the dlt config for retention).

## Access

- Loader credentials: a service account with write access to the target datasets and staging only, not an admin user.
- Credentials in `.dlt/secrets.toml` or environment variables, never committed.

## Verify

- [ ] `_dlt_loads` has the new `load_id` with status 0 and no failed jobs.
- [ ] Row counts per table match the extracted counts in the trace.
- [ ] Partition and cluster settings present on the created table (warehouse information schema).
- [ ] Critical columns (keys, amounts, timestamps) are non-null and correctly typed; no `__v_` variant columns.
