# Medallion Architecture Template

## Overview

Bronze → Silver → Gold data quality progression for data lakes.

## Directory Structure

```text
data-lake/
├── bronze/                    # Raw data (append-only)
│   ├── events/
│   ├── users/
│   └── orders/
├── silver/                    # Cleaned, validated
│   ├── stg_events/
│   ├── stg_users/
│   └── stg_orders/
└── gold/                      # Business-ready
    ├── fct_daily_events/
    ├── dim_users/
    └── mart_sales/
```

## Bronze Layer (Raw)

### dlt Ingestion

```python
import dlt

@dlt.source
def api_source():
    @dlt.resource(
        name="events",
        write_disposition="append",
        table_format="iceberg"
    )
    def events():
        for batch in fetch_events():
            yield batch

    return events

pipeline = dlt.pipeline(
    pipeline_name="bronze_ingestion",
    destination="filesystem",  # or clickhouse, duckdb
    dataset_name="bronze"
)

pipeline.run(api_source())
```

### Bronze Table (ClickHouse)

```sql
CREATE TABLE bronze.raw_events (
    _dlt_load_id String,
    _dlt_id String,
    _ingested_at DateTime DEFAULT now(),
    raw_data String  -- Original JSON
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(_ingested_at)
ORDER BY (_ingested_at, _dlt_id)
TTL _ingested_at + INTERVAL 2 YEAR;
```

## Silver Layer (Cleaned)

### SQLMesh Model

```sql
-- models/staging/stg_events.sql
MODEL (
  name silver.stg_events,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column created_at
  ),
  cron '@hourly',
  grain event_id,
  audits (
    not_null(columns=[event_id, user_id, created_at])
  )
);

SELECT
    JSONExtractString(raw_data, 'event_id') AS event_id,
    JSONExtractUInt(raw_data, 'user_id') AS user_id,
    JSONExtractString(raw_data, 'event_type') AS event_type,
    parseDateTimeBestEffort(
        JSONExtractString(raw_data, 'created_at')
    ) AS created_at,
    raw_data AS properties,
    _ingested_at AS _loaded_at
FROM bronze.raw_events
WHERE _ingested_at BETWEEN @start_dt AND @end_dt
  AND JSONExtractString(raw_data, 'event_id') IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY JSONExtractString(raw_data, 'event_id')
    ORDER BY _ingested_at DESC
) = 1;
```

## Gold Layer (Business-Ready)

### Fact Table

```sql
-- models/marts/fct_daily_events.sql
MODEL (
  name gold.fct_daily_events,
  kind FULL,
  cron '@daily',
  grain [date, event_type]
);

SELECT
    toDate(created_at) AS date,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users,
    min(created_at) AS first_event,
    max(created_at) AS last_event
FROM silver.stg_events
GROUP BY date, event_type;
```

### Dimension Table

```sql
-- models/marts/dim_users.sql
MODEL (
  name gold.dim_users,
  kind SCD_TYPE_2 (
    unique_key [user_id],
    valid_from_name valid_from,
    valid_to_name valid_to
  ),
  cron '@daily',
  grain user_id
);

SELECT
    user_id,
    email,
    name,
    created_at,
    CASE
        WHEN total_orders >= 10 THEN 'vip'
        WHEN total_orders >= 3 THEN 'regular'
        ELSE 'new'
    END AS segment
FROM silver.stg_users u
LEFT JOIN (
    SELECT user_id, count() AS total_orders
    FROM silver.stg_orders
    GROUP BY user_id
) o USING (user_id);
```

## Data Quality

### Great Expectations Suite

```python
# bronze_quality.py
validator.expect_column_values_to_not_be_null("_dlt_id")
validator.expect_column_to_exist("raw_data")

# silver_quality.py
validator.expect_column_values_to_not_be_null("event_id")
validator.expect_column_values_to_be_unique("event_id")
validator.expect_column_values_to_match_regex(
    "email", r"^[\w.-]+@[\w.-]+\.\w+$"
)

# gold_quality.py
validator.expect_column_values_to_be_between(
    "event_count", min_value=0
)
validator.expect_table_row_count_to_be_between(
    min_value=1
)
```

## Orchestration (Dagster)

```python
from dagster import asset, Definitions

@asset(group_name="bronze")
def bronze_events():
    """Ingest raw events"""
    pipeline = dlt.pipeline(...)
    return pipeline.run(...)

@asset(deps=[bronze_events], group_name="silver")
def silver_events():
    """Clean and validate events"""
    ctx = sqlmesh.Context()
    ctx.run(select_models=["silver.stg_events"])

@asset(deps=[silver_events], group_name="gold")
def gold_daily_events():
    """Aggregate daily metrics"""
    ctx = sqlmesh.Context()
    ctx.run(select_models=["gold.fct_daily_events"])
```

## Best Practices

1. **Bronze:** Never modify raw data, append-only
2. **Silver:** Deduplicate, validate, type columns
3. **Gold:** Aggregate for specific use cases
4. **Lineage:** Track transformations in catalog
5. **Quality:** Validate at each layer transition
