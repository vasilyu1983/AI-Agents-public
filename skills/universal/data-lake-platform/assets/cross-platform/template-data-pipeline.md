# Data Pipeline Template

Use when laying out an end-to-end lake pipeline (sources → bronze → silver → gold → serving) and deciding which component owns each step. Layer contracts: [template-medallion-architecture.md](template-medallion-architecture.md).

## Stages and Owners

```text
Sources ──► Ingest (dlt / Airbyte / CDC) ──► Bronze ──► Transform ──► Silver ──► Gold ──► Serve
            raw, append or merge by key               (dbt / SQLMesh)                 (engine / BI)
```

| Stage | Owner | Rule |
|---|---|---|
| Ingest | [dlt](../ingestion/dlt/template-dlt-pipeline.md), [Airbyte](../ingestion/airbyte/template-airbyte-connection.md), or CDC (`data-streaming` skill) | Land source data as-is plus load metadata; no business logic |
| Bronze | Object storage with a table format, or a raw warehouse schema | Immutable history or keyed merge; replayable |
| Silver / Gold | Transformation layer: `data-analytics-engineering` skill ([SKILL.md](../../../data-analytics-engineering/SKILL.md)) | All SQL modelling, tests, and incremental models live there |
| Serve | Query engine or serving tables ([ClickHouse](../query-engines/clickhouse/template-clickhouse-optimization.md), [DuckDB](../query-engines/duckdb/template-duckdb-analytics.md)) | Built from gold; never written to directly by ingestion |
| Orchestrate | [Dagster](../orchestration/template-dagster-pipeline.md) or another orchestrator | Triggers downstream on upstream completion, not on clock offsets |

## Decisions to Make Up Front

1. **Load strategy per source table**: full, cursor, or CDC ([template-incremental-loading.md](template-incremental-loading.md)). Record it with the reason.
2. **Bronze format**: open table format on object storage when several engines read it or history must be replayable; raw warehouse schema when one warehouse is the only consumer.
3. **Keys and deletes**: business key per table and delete semantics (physical vs tombstone) before the first load; both are costly to change later.
4. **Freshness target per gold table**: drives schedules and alerts. Stagger upstream targets so each layer's target includes its upstream's.
5. **Naming**: one dataset/schema per source in bronze (`source_<system>`), stable pipeline names (renames reset state; see [dlt identity](../ingestion/dlt/template-dlt-pipeline.md#identity-is-state)).

## Pipeline Rules

- **Idempotent at every stage**: re-running any step for the same window yields the same data (keyed merge or partition overwrite, never blind append).
- **Replayable from bronze**: silver and gold can be rebuilt from bronze without re-extracting sources. Keep bronze retention at least as long as the longest rebuild you must support.
- **One writer per table**: two pipelines writing the same table race on schema and data.
- **Schema drift is caught at ingest**: set contracts on bronze tables that feed strict models ([template-schema-evolution.md](template-schema-evolution.md)).
- **Quality gates at layer boundaries**: row counts, key uniqueness, null keys, freshness ([template-data-quality.md](template-data-quality.md)); a failed gate stops downstream builds.
- **Secrets** in a secrets manager or the tool's secrets file, never in pipeline code or config dicts.

## Monitoring

- Freshness from the data (max event or cursor time per table), not from run success; a successful run can load zero rows.
- For dlt, per-load status and timing are in the `_dlt_loads` table of each dataset; alert when the newest successful load is older than the freshness target.
- Track row counts per load and alert on drops to zero or large deviations from the recent norm.
- Alert on cost signals too: bytes scanned or compute time per run trending up usually means an incremental broke into a full scan.

## Verify

- [ ] Each source table has a documented load strategy, key, delete semantics, and freshness target.
- [ ] Re-running the whole pipeline for yesterday's window changes nothing.
- [ ] Dropping and rebuilding one silver table from bronze reproduces it.
- [ ] Freshness and quality alerts fire in a test (stale table, duplicate key).
