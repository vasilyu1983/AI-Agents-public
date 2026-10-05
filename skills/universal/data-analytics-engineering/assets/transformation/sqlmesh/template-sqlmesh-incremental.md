# SQLMesh Incremental Strategies Template

*Purpose: Implement efficient incremental model patterns for large-scale data processing.*

## Incremental by Time Range

### Basic Pattern
```sql
MODEL (
  name staging.stg_events,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column event_timestamp
  ),
  start '2024-01-01',
  cron '@hourly'
);

SELECT *
FROM raw.events
WHERE event_timestamp BETWEEN @start_date AND @end_date;
```

### With Lookback Window
```sql
MODEL (
  name intermediate.int_sessions,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column session_start,
    lookback 7  -- Reprocess last 7 days
  ),
  start '2024-01-01',
  cron '@daily'
);
```

## Incremental by Unique Key

### Upsert Pattern
```sql
MODEL (
  name staging.stg_users,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key user_id
  ),
  cron '@hourly'
);

SELECT
  user_id,
  email,
  updated_at
FROM raw.users;
```

### Composite Unique Key
```sql
MODEL (
  name staging.stg_order_items,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key [order_id, line_item_id]
  )
);
```

## Best Practices

- BEST: Use time range for append-only data (logs, events)
- BEST: Use unique key for slowly changing dimensions
- BEST: Add lookback window for late-arriving data
- BEST: Partition by date for large tables
- BEST: Test backfills before production

## Backfill Strategy

```bash
# Backfill specific date range
sqlmesh run --start 2024-01-01 --end 2024-01-31

# Backfill with parallelism
sqlmesh run --start 2024-01-01 --execution-time 2024-12-01 --parallel 4
```
