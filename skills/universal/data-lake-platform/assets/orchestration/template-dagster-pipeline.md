# Dagster Pipeline Template

Use when orchestrating lake ingestion and downstream builds with Dagster: asset boundaries, partitions and backfills, triggers, and checks. Orchestrator choice and Airflow/Prefect patterns: [references/orchestration-patterns.md](../../references/orchestration-patterns.md).

## Asset Boundaries

- One asset per table that someone reads, not one asset per script. Table-level assets give lineage, selective re-runs, and per-table checks.
- For dlt, use Dagster's dlt integration (`@dlt_assets`), which creates one asset per dlt resource from the source definition. Wrapping `pipeline.run()` in a single asset hides which table failed.
- For dbt or SQLMesh, use their Dagster integrations so each model is an asset. Do not `subprocess.run(["sqlmesh", ...])` or `dbt run` inside one asset: lineage, per-model failures, and partial retries are lost. Model design itself belongs to the `data-analytics-engineering` skill.
- Group assets by layer (`bronze`, `silver`, `gold`) or by source; keep one grouping scheme.

## Resources and Config

- Connections are `ConfigurableResource`s injected into assets; credentials via `EnvVar("NAME")`, which resolves at run time and keeps the value out of the UI. Reading `os.environ` at import time bakes the value into the code location.
- One `Definitions` object per code location listing assets, resources, schedules, sensors, and checks.

## Partitions and Backfills

Partition when data arrives or is corrected in time slices; the partition is the unit of re-run.

```python
daily = DailyPartitionsDefinition(start_date="<history_start>")

@asset(partitions_def=daily)
def orders_bronze(context):
    window = context.partition_time_window
    # Bounded window: dlt incremental with end_value does not advance stored state,
    # so re-running any partition is idempotent and safe beside the live schedule.
    source = orders_source(start=window.start, end=window.end)  # merge by key inside
    ...
```

- Each partition run must be idempotent: overwrite that partition, or `merge` by key. Appending per partition double-counts on every retry or backfill.
- Pass the partition window into the loader as an explicit range (dlt: `initial_value` + `end_value`, see [backfill rules](../ingestion/dlt/template-dlt-incremental.md#backfill-and-replay)). Do not let a partitioned run advance a shared incremental cursor.
- Choose granularity from how data is corrected and queried. Too fine (hourly over years) creates thousands of runs and slow UI/backfill planning; too coarse makes each retry expensive.
- For engines that process a range efficiently in one query, use a single-run backfill policy instead of one run per partition.
- Backfill in bounded ranges, newest first when consumers need recent data soonest; cap concurrency (below).

## Triggers

- **Schedules**: set `execution_timezone` explicitly; for partitioned jobs build the schedule from the partitions definition so each tick targets the right partition.
- **Sensors**: store progress in the sensor cursor (`context.update_cursor`) and set a stable `run_key` per unit of work so the same file or event never launches twice. Do not re-list a whole bucket or directory on every tick.
- **Upstream completion**: prefer asset-based triggering (downstream runs when upstream materializes) over fixed-time schedules that assume upstream finished. Check the Dagster docs for the current declarative automation API before using it.

## Reliability

- `RetryPolicy` with backoff for transient failures (network, rate limits). Do not retry data errors; they fail the same way and multiply load.
- Limit concurrent runs that hit the same source or warehouse (tag-based run concurrency limits or pools; see the Dagster docs for the current mechanism). Parallel backfills can take down a production source database.
- Put timeouts on external calls; a hung extraction holds a run slot indefinitely.

## Asset Checks

- Attach checks to the assets they guard: row count within an expected range, key uniqueness, non-null keys, freshness (max event time vs current time).
- Make checks that protect consumers blocking where supported, so a failed check stops downstream materialization instead of publishing bad data.
- Alert on freshness from the data (max event time), not only on run success; a successful run can load zero rows.

## Verify

- [ ] Asset graph shows one asset per loaded table and per model, with correct upstream edges.
- [ ] Re-running one partition twice leaves identical data (idempotency).
- [ ] A backfill of a past range does not move the live incremental cursor.
- [ ] A sensor tick with no new input launches no run; the same input never launches twice.
- [ ] A failed blocking check prevents downstream assets from materializing.
