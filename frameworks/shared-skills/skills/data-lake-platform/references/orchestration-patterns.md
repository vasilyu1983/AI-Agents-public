# Orchestration Patterns

## Tool Comparison

| Feature | Dagster | Airflow | Prefect |
|---------|---------|---------|---------|
| **Paradigm** | Software-defined assets | Task DAGs | Flow-based |
| **Data awareness** | Native (assets) | Primarily task-centric (XCom) | Flow/task results |
| **Testing** | Strong (unit tests) | Varies by operator/codebase | Strong (Python-first) |
| **UI** | Modern | Mature | Modern |
| **Deployment** | K8s, Docker | K8s, Docker | Hybrid, Cloud |
| **Community** | Growing | Large | Growing |

**Recommendation:** Pick the orchestrator that matches your operating model (asset-based vs task-based vs Python flow-based) and standardize retries, timeouts, concurrency, and alerting across all pipelines.

---

## Dagster

### Software-Defined Assets

```python
from dagster import asset, Definitions, AssetExecutionContext
import dlt

@asset(
    description="Raw events from API",
    group_name="bronze"
)
def raw_events(context: AssetExecutionContext):
    """Ingest events using dlt"""
    pipeline = dlt.pipeline(
        pipeline_name="events",
        destination="duckdb",
        dataset_name="raw"
    )
    info = pipeline.run(events_source())
    context.log.info(f"Loaded {info.loads_package}")
    return info

@asset(
    deps=[raw_events],
    description="Cleaned events",
    group_name="silver"
)
def cleaned_events(context: AssetExecutionContext):
    """Transform with SQLMesh"""
    import sqlmesh
    ctx = sqlmesh.Context()
    ctx.run(select_models=["staging.stg_events"])
    return "staging.stg_events"

@asset(
    deps=[cleaned_events],
    description="Daily event metrics",
    group_name="gold"
)
def daily_metrics(context: AssetExecutionContext):
    """Aggregate metrics"""
    import sqlmesh
    ctx = sqlmesh.Context()
    ctx.run(select_models=["marts.fct_daily_events"])
    return "marts.fct_daily_events"

defs = Definitions(
    assets=[raw_events, cleaned_events, daily_metrics]
)
```

### Schedules and Sensors

```python
from dagster import (
    ScheduleDefinition,
    sensor,
    RunRequest,
    SensorEvaluationContext
)

# Time-based schedule
daily_schedule = ScheduleDefinition(
    job=define_asset_job("daily_pipeline", selection="*"),
    cron_schedule="0 6 * * *",  # 6 AM daily
    execution_timezone="UTC"
)

# Event-based sensor
@sensor(job=define_asset_job("incremental_pipeline"))
def new_files_sensor(context: SensorEvaluationContext):
    new_files = check_for_new_files("s3://bucket/incoming/")
    if new_files:
        yield RunRequest(
            run_key=f"files_{hash(tuple(new_files))}",
            run_config={"files": new_files}
        )
```

### Resources and IO Managers

```python
from dagster import ConfigurableResource, IOManager, io_manager
from dagster_duckdb import DuckDBResource

class ClickHouseResource(ConfigurableResource):
    host: str
    port: int = 9000
    database: str
    user: str
    password: str

    def query(self, sql: str):
        import clickhouse_connect
        client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            database=self.database,
            username=self.user,
            password=self.password
        )
        return client.query(sql)

defs = Definitions(
    assets=[...],
    resources={
        "duckdb": DuckDBResource(database="analytics.duckdb"),
        "clickhouse": ClickHouseResource(
            host="clickhouse.example.com",
            database="analytics",
            user="dagster",
            password={"env": "CLICKHOUSE_PASSWORD"}
        )
    }
)
```

---

## Apache Airflow

### DAG Definition

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=5)
}

with DAG(
    'data_pipeline',
    default_args=default_args,
    description='Daily data pipeline',
    schedule_interval='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['data-lake']
) as dag:

    def ingest_data(**context):
        import dlt
        pipeline = dlt.pipeline(
            pipeline_name="events",
            destination="clickhouse"
        )
        pipeline.run(events_source())

    ingest = PythonOperator(
        task_id='ingest_events',
        python_callable=ingest_data
    )

    transform = SQLExecuteQueryOperator(
        task_id='transform_events',
        conn_id='clickhouse_default',
        sql='CALL sqlmesh_run()'
    )

    ingest >> transform
```

### TaskFlow API

```python
from airflow.decorators import dag, task
from datetime import datetime

@dag(
    schedule_interval='0 6 * * *',
    start_date=datetime(2024, 1, 1),
    catchup=False
)
def data_pipeline():

    @task
    def extract():
        import dlt
        pipeline = dlt.pipeline("events", destination="duckdb")
        return pipeline.run(events_source())

    @task
    def transform(extract_result):
        import sqlmesh
        ctx = sqlmesh.Context()
        ctx.run()
        return "completed"

    @task
    def load(transform_result):
        # Export to ClickHouse
        pass

    data = extract()
    transformed = transform(data)
    load(transformed)

pipeline = data_pipeline()
```

---

## Prefect

### Flow Definition

```python
from prefect import flow, task
from prefect.tasks import task_input_hash
from datetime import timedelta

@task(
    retries=3,
    retry_delay_seconds=60,
    cache_key_fn=task_input_hash,
    cache_expiration=timedelta(hours=1)
)
def ingest_events():
    import dlt
    pipeline = dlt.pipeline("events", destination="duckdb")
    return pipeline.run(events_source())

@task
def transform_data(ingest_result):
    import sqlmesh
    ctx = sqlmesh.Context()
    ctx.run()
    return "marts.fct_events"

@task
def export_to_clickhouse(table_name: str):
    # Export logic
    pass

@flow(name="daily-pipeline")
def data_pipeline():
    result = ingest_events()
    table = transform_data(result)
    export_to_clickhouse(table)

if __name__ == "__main__":
    data_pipeline()
```

### Deployment

```python
from prefect.deployments import Deployment
from prefect.server.schemas.schedules import CronSchedule

deployment = Deployment.build_from_flow(
    flow=data_pipeline,
    name="daily-production",
    schedule=CronSchedule(cron="0 6 * * *"),
    work_queue_name="default",
    infrastructure=KubernetesJob(
        image="my-registry/data-pipeline:latest",
        namespace="data"
    )
)

deployment.apply()
```

---

## Best Practices

### Data Pipeline Patterns

```text
1. Idempotency
   - Use merge/upsert instead of append
   - Include processing timestamps
   - Support re-runs without duplicates

2. Incremental Processing
   - Track high watermarks
   - Process only new/changed data
   - Use partitioning for efficient scans

3. Error Handling
   - Implement dead letter queues
   - Alert on failures
   - Enable manual retries

4. Monitoring
   - Track data freshness
   - Monitor row counts
   - Alert on anomalies
```

### Observability

```python
# Dagster: Built-in asset observations
@asset
def monitored_asset(context):
    result = process_data()
    context.log_event(
        AssetObservation(
            asset_key="monitored_asset",
            metadata={
                "row_count": result.count(),
                "freshness": datetime.now().isoformat()
            }
        )
    )
    return result
```

---

## Choosing an Orchestrator

| Use Case | Recommendation |
|----------|----------------|
| New data platform | **Dagster** |
| Existing Airflow | Stay with **Airflow** |
| Simple Python pipelines | **Prefect** |
| ML pipelines | Dagster or Prefect |
| Enterprise, compliance | Airflow (managed) |
