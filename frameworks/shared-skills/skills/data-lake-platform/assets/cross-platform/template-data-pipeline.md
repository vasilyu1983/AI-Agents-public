# Data Pipeline Template

## Overview

End-to-end data pipeline from source to analytics-ready tables.

## Pipeline Architecture

```text
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Sources   │───→│   Ingest    │───→│  Transform  │───→│    Serve    │
│ API/DB/File │    │  (dlt)      │    │  (SQLMesh)  │    │ (ClickHouse)│
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
                          │                  │                  │
                          ▼                  ▼                  ▼
                   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
                   │   Bronze    │    │   Silver    │    │    Gold     │
                   │ (Raw/Lake)  │    │  (Cleaned)  │    │  (Marts)    │
                   └─────────────┘    └─────────────┘    └─────────────┘
```

## Step 1: Source Configuration

### dlt Source Definition

```python
# pipelines/sources/api_source.py
import dlt
from dlt.sources.rest_api import rest_api_source

@dlt.source(name="crm")
def crm_source(api_key: str = dlt.secrets.value):
    """CRM API data source."""

    config = {
        "client": {
            "base_url": "https://api.crm.example.com/v1/",
            "auth": {"type": "api_key", "api_key": api_key}
        },
        "resources": [
            {
                "name": "customers",
                "endpoint": {"path": "customers", "params": {"per_page": 100}},
                "primary_key": "id"
            },
            {
                "name": "orders",
                "endpoint": {"path": "orders"},
                "primary_key": "order_id"
            },
            {
                "name": "products",
                "endpoint": {"path": "products"},
                "primary_key": "sku"
            }
        ]
    }

    yield from rest_api_source(config)
```

### Database Source

```python
# pipelines/sources/db_source.py
import dlt
from dlt.sources.sql_database import sql_database

@dlt.source(name="postgres_source")
def postgres_source():
    """PostgreSQL CDC source."""
    return sql_database(
        credentials="postgresql://user:pass@host:5432/db",
        schema="public",
        table_names=["users", "transactions", "events"],
        incremental=dlt.sources.incremental("updated_at"),
        chunk_size=10000
    )
```

## Step 2: Ingestion Pipeline

### dlt Pipeline Configuration

```python
# pipelines/bronze_pipeline.py
import dlt
from sources.api_source import crm_source
from sources.db_source import postgres_source

def run_bronze_pipeline():
    """Ingest raw data to bronze layer."""

    pipeline = dlt.pipeline(
        pipeline_name="bronze_ingestion",
        destination="filesystem",  # or "clickhouse", "duckdb"
        dataset_name="bronze",
        progress="log"
    )

    # Load API data
    api_info = pipeline.run(
        crm_source(),
        write_disposition="merge",
        primary_key="id"
    )
    print(f"API load: {api_info}")

    # Load database data
    db_info = pipeline.run(
        postgres_source(),
        write_disposition="merge"
    )
    print(f"DB load: {db_info}")

    return pipeline

if __name__ == "__main__":
    run_bronze_pipeline()
```

### Filesystem Destination (Iceberg)

```python
# pipelines/config.py
import dlt

# Configure Iceberg destination
destination_config = {
    "filesystem": {
        "bucket_url": "s3://data-lake/bronze/",
        "credentials": {
            "aws_access_key_id": dlt.secrets["aws_access_key_id"],
            "aws_secret_access_key": dlt.secrets["aws_secret_access_key"]
        }
    },
    "table_format": "iceberg",
    "iceberg": {
        "catalog_type": "rest",
        "catalog_uri": "http://iceberg-rest:8181"
    }
}
```

## Step 3: Transformation Layer

### SQLMesh Project Structure

```text
transform/
├── sqlmesh.yaml
├── models/
│   ├── staging/
│   │   ├── stg_customers.sql
│   │   ├── stg_orders.sql
│   │   └── stg_products.sql
│   ├── intermediate/
│   │   └── int_order_items.sql
│   └── marts/
│       ├── fct_daily_sales.sql
│       └── dim_customers.sql
├── audits/
│   └── data_quality.sql
└── tests/
    └── test_sales.yaml
```

### SQLMesh Configuration

```yaml
# transform/sqlmesh.yaml
gateways:
  local:
    connection:
      type: clickhouse
      host: localhost
      port: 8123
      database: analytics

model_defaults:
  dialect: clickhouse
  start: 2024-01-01

default_gateway: local
```

### Staging Model (Bronze → Silver)

```sql
-- models/staging/stg_customers.sql
MODEL (
  name silver.stg_customers,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key [customer_id]
  ),
  cron '@daily',
  grain customer_id,
  audits (
    not_null(columns=[customer_id, email]),
    unique(columns=[customer_id])
  )
);

SELECT
    id AS customer_id,
    lower(trim(email)) AS email,
    coalesce(name, 'Unknown') AS name,
    created_at,
    updated_at,
    -- Data quality flags
    CASE
        WHEN email LIKE '%@%' THEN true
        ELSE false
    END AS is_valid_email
FROM bronze.customers
WHERE id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY id
    ORDER BY updated_at DESC
) = 1;
```

### Mart Model (Silver → Gold)

```sql
-- models/marts/fct_daily_sales.sql
MODEL (
  name gold.fct_daily_sales,
  kind FULL,
  cron '@daily',
  grain [date, product_id]
);

SELECT
    toDate(o.created_at) AS date,
    oi.product_id,
    p.category,
    count(DISTINCT o.order_id) AS order_count,
    sum(oi.quantity) AS units_sold,
    sum(oi.quantity * oi.unit_price) AS revenue,
    avg(oi.unit_price) AS avg_price
FROM silver.stg_orders o
JOIN silver.int_order_items oi ON o.order_id = oi.order_id
JOIN silver.stg_products p ON oi.product_id = p.product_id
WHERE o.status = 'completed'
GROUP BY date, oi.product_id, p.category;
```

## Step 4: Serving Layer

### ClickHouse Optimized Tables

```sql
-- Create optimized serving table
CREATE TABLE gold.sales_dashboard
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, category, product_id)
AS SELECT * FROM gold.fct_daily_sales;

-- Materialized view for real-time updates
CREATE MATERIALIZED VIEW gold.mv_hourly_sales
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, category)
AS SELECT
    toStartOfHour(created_at) AS hour,
    category,
    count() AS orders,
    sum(total) AS revenue
FROM silver.stg_orders
GROUP BY hour, category;
```

## Step 5: Orchestration

### Dagster Pipeline

```python
# orchestration/pipeline.py
from dagster import asset, Definitions, ScheduleDefinition
import subprocess

@asset(group_name="bronze")
def bronze_crm():
    """Ingest CRM data to bronze."""
    subprocess.run(["python", "pipelines/bronze_pipeline.py"], check=True)
    return "CRM data ingested"

@asset(deps=[bronze_crm], group_name="silver")
def silver_transform():
    """Transform bronze to silver."""
    subprocess.run(["sqlmesh", "run", "--select-model", "silver.*"], check=True)
    return "Silver models updated"

@asset(deps=[silver_transform], group_name="gold")
def gold_marts():
    """Build gold marts."""
    subprocess.run(["sqlmesh", "run", "--select-model", "gold.*"], check=True)
    return "Gold marts updated"

daily_schedule = ScheduleDefinition(
    job=define_asset_job("daily_pipeline", selection="*"),
    cron_schedule="0 6 * * *"  # 6 AM daily
)

defs = Definitions(
    assets=[bronze_crm, silver_transform, gold_marts],
    schedules=[daily_schedule]
)
```

## Monitoring

### Pipeline Health Checks

```python
# monitoring/health.py
def check_pipeline_health():
    checks = {
        "bronze_freshness": check_table_freshness("bronze.*", max_hours=24),
        "silver_freshness": check_table_freshness("silver.*", max_hours=25),
        "gold_freshness": check_table_freshness("gold.*", max_hours=26),
        "row_counts": check_row_counts_growing(),
        "quality_audits": check_sqlmesh_audits_passing()
    }
    return all(checks.values()), checks

def check_table_freshness(pattern, max_hours):
    """Check if tables were updated within threshold."""
    query = f"""
    SELECT table, max(_loaded_at) AS last_update
    FROM system.parts
    WHERE table LIKE '{pattern}'
    GROUP BY table
    HAVING dateDiff('hour', last_update, now()) > {max_hours}
    """
    # Return True if no stale tables
    return execute_query(query).empty
```

## Best Practices

1. **Idempotency**: All pipelines should be re-runnable
2. **Incremental**: Process only new/changed data when possible
3. **Schema evolution**: Handle schema changes gracefully
4. **Data quality**: Validate at each layer boundary
5. **Monitoring**: Alert on freshness, row counts, quality issues
6. **Documentation**: Document lineage and business logic
