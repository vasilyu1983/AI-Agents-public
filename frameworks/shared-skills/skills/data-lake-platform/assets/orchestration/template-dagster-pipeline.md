# Dagster Pipeline Template

## Overview

Orchestrating data pipelines with Dagster for data lake workloads.

## Project Structure

```text
my_project/
├── pyproject.toml
├── setup.py
├── my_project/
│   ├── __init__.py
│   ├── assets/
│   │   ├── __init__.py
│   │   ├── bronze.py
│   │   ├── silver.py
│   │   └── gold.py
│   ├── references/
│   │   ├── __init__.py
│   │   └── clickhouse.py
│   ├── jobs/
│   │   └── __init__.py
│   └── definitions.py
└── workspace.yaml
```

---

## Asset Definitions

### Bronze Layer (Ingestion)

```python
# assets/bronze.py
from dagster import asset, AssetExecutionContext
import dlt

@asset(
    group_name="bronze",
    compute_kind="dlt",
    description="Raw events from API"
)
def bronze_events(context: AssetExecutionContext) -> None:
    """Ingest events from API to bronze layer."""
    pipeline = dlt.pipeline(
        pipeline_name="bronze_events",
        destination="clickhouse",
        dataset_name="bronze"
    )

    load_info = pipeline.run(api_source())
    context.log.info(f"Loaded {load_info}")
    return None


@asset(
    group_name="bronze",
    compute_kind="dlt",
    description="Raw users from database"
)
def bronze_users(context: AssetExecutionContext) -> None:
    """Sync users from PostgreSQL to bronze layer."""
    pipeline = dlt.pipeline(
        pipeline_name="bronze_users",
        destination="clickhouse",
        dataset_name="bronze"
    )

    load_info = pipeline.run(postgres_source())
    context.log.info(f"Loaded {load_info}")
```

### Silver Layer (Transform)

```python
# assets/silver.py
from dagster import asset, AssetExecutionContext
import subprocess

@asset(
    group_name="silver",
    deps=[bronze_events, bronze_users],
    compute_kind="sqlmesh",
    description="Cleaned and validated events"
)
def silver_events(context: AssetExecutionContext) -> None:
    """Transform bronze events to silver."""
    result = subprocess.run(
        ["sqlmesh", "run", "--select-model", "silver.stg_events"],
        capture_output=True,
        text=True,
        check=True
    )
    context.log.info(result.stdout)


@asset(
    group_name="silver",
    deps=[bronze_users],
    compute_kind="sqlmesh"
)
def silver_users(context: AssetExecutionContext) -> None:
    """Transform bronze users to silver."""
    result = subprocess.run(
        ["sqlmesh", "run", "--select-model", "silver.stg_users"],
        capture_output=True,
        text=True,
        check=True
    )
    context.log.info(result.stdout)
```

### Gold Layer (Marts)

```python
# assets/gold.py
from dagster import asset, AssetExecutionContext
import subprocess

@asset(
    group_name="gold",
    deps=[silver_events, silver_users],
    compute_kind="sqlmesh",
    description="Daily event metrics"
)
def gold_daily_events(context: AssetExecutionContext) -> None:
    """Build daily event aggregations."""
    subprocess.run(
        ["sqlmesh", "run", "--select-model", "gold.fct_daily_events"],
        check=True
    )


@asset(
    group_name="gold",
    deps=[silver_users],
    compute_kind="sqlmesh"
)
def gold_dim_users(context: AssetExecutionContext) -> None:
    """Build user dimension table."""
    subprocess.run(
        ["sqlmesh", "run", "--select-model", "gold.dim_users"],
        check=True
    )
```

---

## Resources

### ClickHouse Resource

```python
# references/clickhouse.py
from dagster import ConfigurableResource
import clickhouse_connect

class ClickHouseResource(ConfigurableResource):
    host: str
    port: int = 8123
    username: str
    password: str
    database: str = "default"

    def get_client(self):
        return clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            database=self.database
        )

    def execute(self, query: str):
        client = self.get_client()
        return client.query(query)
```

---

## Schedules and Sensors

### Schedules

```python
# jobs/__init__.py
from dagster import (
    ScheduleDefinition,
    define_asset_job,
    AssetSelection
)

# Daily full pipeline
daily_pipeline_job = define_asset_job(
    name="daily_pipeline",
    selection=AssetSelection.all()
)

daily_schedule = ScheduleDefinition(
    job=daily_pipeline_job,
    cron_schedule="0 6 * * *",  # 6 AM daily
    execution_timezone="UTC"
)

# Hourly bronze refresh
hourly_bronze_job = define_asset_job(
    name="hourly_bronze",
    selection=AssetSelection.groups("bronze")
)

hourly_schedule = ScheduleDefinition(
    job=hourly_bronze_job,
    cron_schedule="0 * * * *"  # Every hour
)
```

### Sensors

```python
from dagster import sensor, RunRequest, SensorEvaluationContext
import os

@sensor(job=daily_pipeline_job)
def new_file_sensor(context: SensorEvaluationContext):
    """Trigger pipeline when new file arrives."""
    watch_path = "/data/incoming/"

    for filename in os.listdir(watch_path):
        filepath = os.path.join(watch_path, filename)

        if os.path.isfile(filepath):
            yield RunRequest(
                run_key=filename,
                run_config={
                    "ops": {
                        "bronze_events": {
                            "config": {"filepath": filepath}
                        }
                    }
                }
            )
```

---

## Definitions

```python
# definitions.py
from dagster import Definitions, load_assets_from_modules

from . import assets
from .resources.clickhouse import ClickHouseResource
from .jobs import daily_schedule, hourly_schedule, new_file_sensor

all_assets = load_assets_from_modules([assets.bronze, assets.silver, assets.gold])

defs = Definitions(
    assets=all_assets,
    resources={
        "clickhouse": ClickHouseResource(
            host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
            username=os.environ.get("CLICKHOUSE_USER", "default"),
            password=os.environ.get("CLICKHOUSE_PASSWORD", ""),
            database="analytics"
        )
    },
    schedules=[daily_schedule, hourly_schedule],
    sensors=[new_file_sensor]
)
```

---

## Partitioned Assets

```python
from dagster import (
    asset,
    DailyPartitionsDefinition,
    AssetExecutionContext
)

daily_partitions = DailyPartitionsDefinition(start_date="2024-01-01")

@asset(
    partitions_def=daily_partitions,
    group_name="gold"
)
def partitioned_daily_events(context: AssetExecutionContext) -> None:
    """Daily events partitioned by date."""
    partition_date = context.partition_key

    subprocess.run([
        "sqlmesh", "run",
        "--select-model", "gold.fct_daily_events",
        "--start", partition_date,
        "--end", partition_date
    ], check=True)
```

---

## Commands

```bash
# Start Dagster UI
dagster dev

# Run specific job
dagster job execute -j daily_pipeline

# Materialize assets
dagster asset materialize --select bronze_events

# Backfill partitioned assets
dagster asset backfill --asset partitioned_daily_events \
    --start-date 2024-01-01 --end-date 2024-06-01
```

---

## Best Practices

1. **Use asset groups** - Organize by medallion layer
2. **Define dependencies** - Clear lineage with `deps`
3. **Add compute_kind** - Visual distinction in UI
4. **Use resources** - Shared connections
5. **Implement sensors** - Event-driven triggers
6. **Partition large datasets** - Efficient backfills
