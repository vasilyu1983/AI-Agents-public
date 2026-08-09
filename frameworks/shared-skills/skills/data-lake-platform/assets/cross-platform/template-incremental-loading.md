# Incremental Loading Template

## Overview

Patterns for efficient incremental data loading across the data lake stack.

## Incremental Strategies

| Strategy | Use When | Example |
|----------|----------|---------|
| **Time-based** | Source has reliable timestamp | `WHERE updated_at > @last_run` |
| **Cursor-based** | Sequential ID or monotonic key | `WHERE id > @last_id` |
| **CDC** | Need real-time, source supports | Debezium, dlt CDC |
| **Hash-based** | No reliable incremental key | Compare row hashes |
| **Full refresh** | Small tables, complex logic | `TRUNCATE + INSERT` |

---

## dlt Incremental Loading

### Time-Based Incremental

```python
import dlt
from dlt.sources.rest_api import rest_api_source

@dlt.source
def api_source():
    @dlt.resource(
        name="orders",
        write_disposition="merge",
        primary_key="order_id"
    )
    def orders(
        updated_at=dlt.sources.incremental(
            "updated_at",
            initial_value="2024-01-01T00:00:00Z"
        )
    ):
        """Incrementally load orders by updated_at."""
        response = requests.get(
            "https://api.example.com/orders",
            params={
                "updated_after": updated_at.last_value,
                "per_page": 100
            }
        )
        for order in response.json()["orders"]:
            yield order

    return orders

# Pipeline automatically tracks state
pipeline = dlt.pipeline(
    pipeline_name="orders_incremental",
    destination="clickhouse"
)
pipeline.run(api_source())
```

### Cursor-Based Incremental

```python
@dlt.resource(
    write_disposition="append",
    primary_key="event_id"
)
def events(
    event_id=dlt.sources.incremental(
        "event_id",
        initial_value=0,
        primary_key=True  # Use as cursor
    )
):
    """Load events incrementally by ID."""
    while True:
        response = requests.get(
            "https://api.example.com/events",
            params={
                "after_id": event_id.last_value,
                "limit": 1000
            }
        )
        batch = response.json()["events"]
        if not batch:
            break
        yield batch
```

### Database CDC with dlt

```python
from dlt.sources.sql_database import sql_database

source = sql_database(
    credentials="postgresql://user:pass@host:5432/db",
    table_names=["users", "orders"],
    incremental=dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2024-01-01"
    ),
    # Backend queries: WHERE updated_at > @last_value
    backend_kwargs={"chunk_size": 50000}
)
```

---

## SQLMesh Incremental Models

### INCREMENTAL_BY_TIME_RANGE

```sql
-- Best for time-series data
MODEL (
  name silver.stg_events,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column created_at,
    batch_size 1,          -- Days per batch
    batch_concurrency 4,   -- Parallel batches
    lookback 2             -- Re-process last 2 periods
  ),
  cron '@hourly',
  grain event_id
);

SELECT
    event_id,
    user_id,
    event_type,
    properties,
    created_at
FROM bronze.raw_events
WHERE created_at BETWEEN @start_dt AND @end_dt
  AND event_id IS NOT NULL;
```

### INCREMENTAL_BY_UNIQUE_KEY

```sql
-- Best for SCD Type 1 (upsert)
MODEL (
  name silver.stg_users,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key [user_id],
    when_matched WHEN MATCHED THEN UPDATE SET
      email = source.email,
      name = source.name,
      updated_at = source.updated_at
  ),
  cron '@daily',
  grain user_id
);

SELECT
    user_id,
    email,
    name,
    created_at,
    updated_at
FROM bronze.raw_users
WHERE updated_at >= @execution_date - INTERVAL 1 DAY;
```

### SCD Type 2 (History Tracking)

```sql
MODEL (
  name silver.dim_users_history,
  kind SCD_TYPE_2 (
    unique_key [user_id],
    valid_from_name valid_from,
    valid_to_name valid_to,
    invalidate_hard_deletes true
  ),
  cron '@daily',
  grain [user_id, valid_from]
);

SELECT
    user_id,
    email,
    subscription_tier,
    updated_at AS effective_date
FROM bronze.raw_users;
```

---

## ClickHouse Incremental Patterns

### ReplacingMergeTree (Deduplication)

```sql
-- Automatically keeps latest version
CREATE TABLE silver.users (
    user_id UInt64,
    email String,
    name String,
    updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;

-- Insert new/updated records
INSERT INTO silver.users
SELECT * FROM bronze.raw_users
WHERE updated_at > (
    SELECT max(updated_at) FROM silver.users
);

-- Query with deduplication
SELECT * FROM silver.users FINAL;

-- Or use argMax for latest value
SELECT
    user_id,
    argMax(email, updated_at) AS email,
    argMax(name, updated_at) AS name,
    max(updated_at) AS updated_at
FROM silver.users
GROUP BY user_id;
```

### CollapsingMergeTree (State Changes)

```sql
-- Track state changes with sign column
CREATE TABLE silver.balances (
    user_id UInt64,
    balance Decimal(18, 2),
    updated_at DateTime,
    sign Int8  -- 1 = insert, -1 = delete
)
ENGINE = CollapsingMergeTree(sign)
ORDER BY (user_id, updated_at);

-- Insert new state (cancel old + add new)
INSERT INTO silver.balances
SELECT user_id, balance, now(), -1 FROM silver.balances WHERE user_id = 123
UNION ALL
SELECT 123, 1500.00, now(), 1;
```

### Materialized View (Real-time Aggregation)

```sql
-- Source table
CREATE TABLE bronze.events (
    event_id UUID,
    user_id UInt64,
    event_type String,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY (created_at, event_id);

-- Auto-updating aggregate
CREATE MATERIALIZED VIEW silver.hourly_events
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type)
AS SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users
FROM bronze.events
GROUP BY hour, event_type;
```

---

## Iceberg Incremental Patterns

### Merge Into (Upsert)

```sql
-- Apache Spark / Trino
MERGE INTO silver.customers t
USING bronze.raw_customers s
ON t.customer_id = s.customer_id
WHEN MATCHED AND s.updated_at > t.updated_at THEN
    UPDATE SET *
WHEN NOT MATCHED THEN
    INSERT *;
```

### Incremental Read

```python
# PyIceberg incremental read
from pyiceberg.catalog import load_catalog

catalog = load_catalog("rest")
table = catalog.load_table("silver.events")

# Read only new snapshots
scan = table.scan(
    snapshot_id=last_processed_snapshot
).to_arrow()
```

### Time Travel for Comparison

```sql
-- Compare current vs previous state
SELECT
    'new' AS status,
    current.*
FROM silver.customers current
LEFT JOIN silver.customers VERSION AS OF 'yesterday' AS prev
    ON current.customer_id = prev.customer_id
WHERE prev.customer_id IS NULL

UNION ALL

SELECT
    'changed' AS status,
    current.*
FROM silver.customers current
JOIN silver.customers VERSION AS OF 'yesterday' AS prev
    ON current.customer_id = prev.customer_id
WHERE current.updated_at > prev.updated_at;
```

---

## State Management

### dlt State Tracking

```python
# dlt automatically manages state in .dlt/
# State location: .dlt/pipelines/{pipeline_name}/state/

# Manual state access
pipeline = dlt.pipeline(pipeline_name="my_pipeline")
state = pipeline.state

# Check last incremental value
last_value = state["sources"]["api"]["resources"]["orders"]["incremental"]["updated_at"]["last_value"]

# Reset state (force full refresh)
pipeline.drop()
```

### SQLMesh State

```bash
# View model state
sqlmesh info

# Force full refresh of model
sqlmesh run --model silver.stg_orders --restate-model

# Backfill specific date range
sqlmesh plan --start 2024-01-01 --end 2024-01-31
```

### Custom State Table

```sql
-- Track pipeline state in ClickHouse
CREATE TABLE meta.pipeline_state (
    pipeline_name String,
    resource_name String,
    last_value String,
    last_run DateTime,
    rows_processed UInt64
)
ENGINE = ReplacingMergeTree(last_run)
ORDER BY (pipeline_name, resource_name);

-- Update after each run
INSERT INTO meta.pipeline_state VALUES
    ('orders_pipeline', 'orders', '2024-06-15T10:30:00Z', now(), 15000);
```

---

## Best Practices

### DO

1. **Use time-based incremental** when source has reliable timestamps
2. **Add lookback period** to catch late-arriving data
3. **Track state externally** for complex pipelines
4. **Validate row counts** after incremental loads
5. **Monitor data freshness** with alerts

### DON'T

1. **Don't assume timestamps are reliable** - validate first
2. **Don't skip deduplication** - duplicates happen
3. **Don't use full refresh** for large tables without reason
4. **Don't ignore late data** - design for it
5. **Don't forget to test** incremental logic with edge cases

---

## Validation Queries

```sql
-- Check for gaps in incremental data
SELECT
    toDate(created_at) AS date,
    count() AS records,
    min(created_at) AS min_time,
    max(created_at) AS max_time
FROM silver.stg_events
GROUP BY date
ORDER BY date;

-- Detect duplicate records
SELECT
    event_id,
    count() AS duplicates
FROM silver.stg_events
GROUP BY event_id
HAVING count() > 1;

-- Compare source vs target counts
SELECT
    'bronze' AS layer, count() AS records FROM bronze.raw_events
UNION ALL
SELECT
    'silver' AS layer, count() AS records FROM silver.stg_events;
```
