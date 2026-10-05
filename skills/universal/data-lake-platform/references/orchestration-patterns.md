# Orchestration Patterns

Pick the orchestrator that matches the operating model, then standardize retries, timeouts, concurrency, and alerting across every pipeline. Dagster asset template: [template-dagster-pipeline.md](../assets/orchestration/template-dagster-pipeline.md).

## Choosing

| Situation | Default | Why |
|-----------|---------|-----|
| New lake platform, data-asset thinking (bronze/silver/gold tables) | Dagster | Assets, partitions, and lineage are first-class; backfills per partition |
| Existing Airflow estate | Stay on Airflow | Migration cost rarely pays back; improve DAG hygiene instead |
| Small team, plain Python flows | Prefect | Lowest ceremony for Python-first pipelines |
| Enterprise with a managed-Airflow mandate | Managed Airflow | Operational and compliance fit |

Paradigms differ: Dagster models *data assets*, Airflow models *task DAGs*, Prefect models *Python flows*. Do not run two orchestrators for the same layer.

## Rules That Apply to All Three

- **Idempotent tasks**: every task can rerun for the same logical interval and produce the same result (merge/overwrite-partition, never blind append).
- **Parameterize by logical interval**, not wall-clock `now()`, so backfills and retries process the right slice.
- **Catchup/backfill is explicit**: disable automatic catchup for new pipelines; run backfills as deliberate, bounded jobs with a concurrency limit so they do not starve daily runs or the query engine.
- **Retries with backoff** for transient source/network errors only; data-contract failures should fail fast and alert, not retry.
- **Timeouts** on every task; a hung extract holds locks and slots.
- **Event-driven triggers** (file-arrival sensors) need a dedup run key so the same file does not trigger twice.
- **Transformation step** (dbt/SQLMesh) runs through its CLI or API from the orchestrator, not as a warehouse procedure; see `data-analytics-engineering`.
- **Emit observability per run**: rows in/out, freshness timestamp, and bytes written, recorded as run metadata so anomalies are visible without opening logs.
- **Dead-letter**: rejected records go to a quarantine table with the failure reason, not to logs.

## Version Boundaries Worth Knowing

- Airflow 3 removed `schedule_interval` (use `schedule`) and moved DAG authoring imports to `airflow.sdk`; core operators moved to a separate standard-provider package. DAGs copied from older examples break on these.
- Prefect's older `Deployment.build_from_flow` pattern is deprecated in newer Prefect lines; check the Prefect docs for the current deployment API before copying examples.
