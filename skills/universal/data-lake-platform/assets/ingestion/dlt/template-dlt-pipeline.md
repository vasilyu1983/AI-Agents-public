# dlt Pipeline Template

Use when building or debugging any dlt pipeline: identity, write disposition, resets, and the rules that make runs safe to repeat. Specialised files: [REST API](template-dlt-rest-api.md), [database sources](template-dlt-database-source.md), [incremental and merge semantics](template-dlt-incremental.md) (owns cursors, merge keys, deletes, backfill), [destinations](template-dlt-warehouse-loading.md).

## Identity Is State

- A pipeline is code plus persistent state (schema, incremental cursors, pending load packages) keyed by `pipeline_name`. State is stored locally and synced to the destination (`_dlt_pipeline_state`), so a fresh machine with the same name resumes where the last run stopped.
- Treat `pipeline_name` and `dataset_name` as primary keys. Renaming either silently starts from `initial_value` again (full re-extract) or writes a second copy of the data. Plan a rename like a migration.
- One pipeline per source system and destination dataset. Two pipelines writing the same dataset race on schema updates.

```python
pipeline = dlt.pipeline(
    pipeline_name="github_issues",   # durable identity; do not rename casually
    destination="postgres",
    dataset_name="source_github",    # convention: source_<system>
)
load_info = pipeline.run(source)
load_info.raise_on_failed_jobs()      # a run can finish with failed load jobs
```

## Write Disposition: Choose Before Writing the Resource

| Disposition | Use when | Avoid when |
|---|---|---|
| `append` | Immutable, insert-only events | Source updates or deletes rows (duplicates accumulate) |
| `merge` | Mutable rows with a stable `primary_key`, loaded incrementally | No stable key: merge cannot match rows |
| `replace` | Small dimensions, explicit rebuilds, one-off backfills | Large tables on a schedule (full re-extract every run) |

Default for large or mutable tables: `merge` + `dlt.sources.incremental`. Merge strategies (`delete-insert`, `upsert`, `scd2`), `merge_key`, and hard deletes are covered in [template-dlt-incremental.md](template-dlt-incremental.md).

Set hints on the resource (`@dlt.resource(...)` or `resource.apply_hints(...)`), not in hand-rolled state. Custom state (`dlt.current.resource_state()`) is only for logic `incremental` cannot express.

## Pattern Selection

- **Full-load script**: small dimension-like tables, `replace`.
- **Incremental**: large or mutable tables, `merge` or `append` + incremental. The default for big sources.
- **Reusable source package**: several pipelines share extraction logic. Extend the package; do not fork it into a standalone script.
- **Custom API source**: pagination or state the declarative REST source cannot express.

## Schema Evolution Traps

- Default contract is `evolve`: new columns are added silently. A type change creates a variant column (`<col>__v_<type>`) instead of failing, so downstream models keep reading the old column and miss values.
- For tables with consumers, set `schema_contract` (for example freeze `data_type`, evolve `columns`) so type drift fails the run instead of forking the column.
- Nested lists become child tables (`<parent>__<field>`, joined on `_dlt_parent_id`). Cap depth with `max_table_nesting` when payloads are deep or unbounded.

## Refresh and Reset: Do Not Hand-Clean Tables

Manual `DROP`/`TRUNCATE` leaves cursor state pointing past data that no longer exists, so the next run loads nothing. Use built-in refresh modes, which reset state and tables together:

| Mode | Effect |
|---|---|
| `refresh="drop_sources"` | Reset all source state and drop all its tables |
| `refresh="drop_resources"` | Reset selected resources and drop their tables |
| `refresh="drop_data"` | Truncate selected tables and reset resource state; keep schema |

```python
pipeline.run(source.with_resources("issues"), refresh="drop_data")
```

## Configuration

- Credentials only in `.dlt/secrets.toml` (gitignored) or environment variables (`SOURCES__GITHUB__ACCESS_TOKEN`); non-secret settings in `.dlt/config.toml`.
- Parallelism and file sizing are config sections (`[extract]`, `[normalize]`, `[load]` workers and buffer sizes), not `run()` arguments.
- dlt moves quickly: when upstream docs and a working local example disagree, follow the working example and check the release notes for the change.

## Debugging: Suspect State First

When behaviour changes between runs without a code change, inspect state before editing code:

```bash
dlt pipeline <pipeline_name> info            # state, cursors, schema
dlt pipeline <pipeline_name> trace           # last run's steps and timings
dlt pipeline <pipeline_name> failed-jobs     # load jobs that did not land
```

Common causes: a cursor already past the data (renamed pipeline, manual truncate), pending packages from a crashed run being loaded first, schema contract blocking a column.

## Scope

Keep ingestion (dlt) separate from transformation. dbt and SQLMesh models belong to the `data-analytics-engineering` skill ([SKILL.md](../../../../data-analytics-engineering/SKILL.md)); do not run SQL transforms inside the pipeline file.

## Verify

- [ ] `load_info` has no failed jobs; `_dlt_loads` shows the new `load_id` with status 0.
- [ ] Row counts per table match the source for the loaded window.
- [ ] A second run with no source changes loads zero new rows (incremental) or identical data (replace).
- [ ] No unexpected `__v_` variant columns or new child tables in the schema diff.
