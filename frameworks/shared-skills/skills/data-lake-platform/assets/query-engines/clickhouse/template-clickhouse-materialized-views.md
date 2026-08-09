# ClickHouse Materialized Views Template

## Overview

Materialized views for real-time aggregation and data transformation.

## Types of Materialized Views

| Type | Trigger | Use Case |
|------|---------|----------|
| **Standard MV** | On INSERT to source | Real-time aggregation |
| **Refreshable MV** | Scheduled | Complex transformations |
| **Chained MV** | Cascading | Multi-stage processing |

---

## Standard Materialized Views

### Basic Aggregation

```sql
-- Source table
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type LowCardinality(String),
    amount Decimal(18, 2),
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at);

-- Target table (store aggregated data)
CREATE TABLE hourly_events (
    hour DateTime,
    event_type LowCardinality(String),
    event_count UInt64,
    unique_users UInt64,
    total_amount Decimal(18, 2)
)
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type);

-- Materialized view (auto-inserts on source insert)
CREATE MATERIALIZED VIEW hourly_events_mv
TO hourly_events
AS SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users,
    sum(amount) AS total_amount
FROM events
GROUP BY hour, event_type;
```

### Query Materialized View

```sql
-- Query target table directly (recommended)
SELECT * FROM hourly_events
WHERE hour >= '2024-01-01'
ORDER BY hour DESC;

-- SummingMergeTree may have duplicates until merge
-- Use GROUP BY for exact results
SELECT
    hour,
    event_type,
    sum(event_count) AS event_count,
    max(unique_users) AS unique_users,  -- uniq is not summable
    sum(total_amount) AS total_amount
FROM hourly_events
WHERE hour >= '2024-01-01'
GROUP BY hour, event_type;
```

---

## AggregatingMergeTree Pattern

### Complex Aggregates

```sql
-- Target table with aggregate functions
CREATE TABLE user_metrics (
    date Date,
    user_id UInt64,
    event_count AggregateFunction(count, UInt64),
    unique_events AggregateFunction(uniq, String),
    avg_amount AggregateFunction(avg, Decimal(18, 2)),
    max_amount AggregateFunction(max, Decimal(18, 2)),
    percentile_amount AggregateFunction(quantile(0.95), Decimal(18, 2))
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(date)
ORDER BY (date, user_id);

-- Materialized view with -State functions
CREATE MATERIALIZED VIEW user_metrics_mv
TO user_metrics
AS SELECT
    toDate(created_at) AS date,
    user_id,
    countState() AS event_count,
    uniqState(event_type) AS unique_events,
    avgState(amount) AS avg_amount,
    maxState(amount) AS max_amount,
    quantileState(0.95)(amount) AS percentile_amount
FROM events
GROUP BY date, user_id;

-- Query with -Merge functions
SELECT
    user_id,
    countMerge(event_count) AS total_events,
    uniqMerge(unique_events) AS unique_types,
    avgMerge(avg_amount) AS avg_amount,
    maxMerge(max_amount) AS max_amount,
    quantileMerge(0.95)(percentile_amount) AS p95_amount
FROM user_metrics
WHERE date >= '2024-01-01'
GROUP BY user_id
ORDER BY total_events DESC
LIMIT 100;
```

---

## Refreshable Materialized Views

### Scheduled Refresh (ClickHouse 23.3+)

```sql
-- Refreshable MV (runs on schedule)
CREATE MATERIALIZED VIEW daily_summary
REFRESH EVERY 1 HOUR
TO daily_summary_target
AS SELECT
    toDate(created_at) AS date,
    event_type,
    count() AS events,
    uniq(user_id) AS users,
    sum(amount) AS revenue
FROM events
WHERE created_at >= today() - 7
GROUP BY date, event_type;

-- Check refresh status
SELECT
    name,
    refresh_state,
    last_refresh_time,
    next_refresh_time
FROM system.view_refreshes;

-- Manual refresh
SYSTEM REFRESH VIEW daily_summary;
```

---

## Chained Materialized Views

### Multi-Stage Processing

```sql
-- Stage 1: Raw events → Cleaned events
CREATE MATERIALIZED VIEW stage1_clean
TO silver.clean_events
AS SELECT
    event_id,
    user_id,
    lower(event_type) AS event_type,
    JSONExtractFloat(properties, 'amount') AS amount,
    created_at
FROM bronze.raw_events
WHERE event_id IS NOT NULL
  AND user_id IS NOT NULL;

-- Stage 2: Cleaned events → Hourly aggregates
CREATE MATERIALIZED VIEW stage2_hourly
TO gold.hourly_events
AS SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS events,
    uniq(user_id) AS users,
    sum(amount) AS total
FROM silver.clean_events
GROUP BY hour, event_type;

-- Stage 3: Hourly → Daily rollup
CREATE MATERIALIZED VIEW stage3_daily
TO gold.daily_events
AS SELECT
    toDate(hour) AS date,
    event_type,
    sum(events) AS events,
    max(users) AS users,  -- Approximate
    sum(total) AS total
FROM gold.hourly_events
GROUP BY date, event_type;
```

---

## Filtering and Routing

### Filtered Views

```sql
-- Only aggregate specific event types
CREATE MATERIALIZED VIEW purchase_metrics_mv
TO gold.purchase_metrics
AS SELECT
    toDate(created_at) AS date,
    user_id,
    count() AS purchase_count,
    sum(amount) AS total_spent
FROM events
WHERE event_type = 'purchase'  -- Filter
GROUP BY date, user_id;
```

### Multiple Views on Same Source

```sql
-- Different aggregations from same source
CREATE MATERIALIZED VIEW by_hour_mv TO hourly_events AS ...;
CREATE MATERIALIZED VIEW by_user_mv TO user_events AS ...;
CREATE MATERIALIZED VIEW by_type_mv TO type_events AS ...;

-- Each view receives all inserts to source
-- Useful for multiple access patterns
```

---

## Real-Time Dashboards

### Dashboard Query Pattern

```sql
-- Fast dashboard queries using MVs

-- 1. Real-time metrics (last 24h)
SELECT
    toStartOfHour(now() - INTERVAL number HOUR) AS hour,
    coalesce(events, 0) AS events,
    coalesce(users, 0) AS users
FROM numbers(24) AS n
LEFT JOIN hourly_events h ON h.hour = toStartOfHour(now() - INTERVAL n.number HOUR)
ORDER BY hour;

-- 2. Comparison metrics
SELECT
    'today' AS period,
    sum(events) AS events
FROM hourly_events
WHERE hour >= today()
UNION ALL
SELECT
    'yesterday' AS period,
    sum(events) AS events
FROM hourly_events
WHERE hour >= today() - 1 AND hour < today();

-- 3. Top users (pre-aggregated)
SELECT
    user_id,
    countMerge(event_count) AS events
FROM user_metrics
WHERE date >= today() - 7
GROUP BY user_id
ORDER BY events DESC
LIMIT 10;
```

---

## Management

### View Operations

```sql
-- List all materialized views
SELECT
    name,
    engine,
    as_select
FROM system.tables
WHERE engine LIKE '%View%';

-- Drop materialized view
DROP VIEW IF EXISTS hourly_events_mv;

-- Detach/attach (keeps data)
DETACH VIEW hourly_events_mv;
ATTACH VIEW hourly_events_mv;
```

### Backfill Existing Data

```sql
-- MV only processes new inserts
-- Backfill historical data manually

INSERT INTO hourly_events
SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users,
    sum(amount) AS total_amount
FROM events
WHERE created_at < '2024-01-01'  -- Historical data
GROUP BY hour, event_type;
```

### Monitor Performance

```sql
-- Check MV processing lag
SELECT
    database,
    table,
    is_currently_executing,
    latest_fail_reason
FROM system.mutations
WHERE table LIKE '%_mv';

-- Check target table size growth
SELECT
    partition,
    formatReadableSize(sum(bytes_on_disk)) AS size,
    sum(rows) AS rows
FROM system.parts
WHERE table = 'hourly_events' AND active
GROUP BY partition
ORDER BY partition DESC;
```

---

## Best Practices

### DO

1. **Use target tables** - `TO target_table` for better control
2. **Use appropriate engine** - SummingMergeTree for counts/sums
3. **Include filters early** - Filter in MV definition if possible
4. **Plan for backfill** - MVs don't process existing data
5. **Test with small data** - Verify aggregation logic first

### DON'T

1. **Don't chain too many MVs** - Performance overhead
2. **Don't use uniq without understanding** - Approximate, can't sum
3. **Don't forget GROUP BY** - Required for aggregation MVs
4. **Don't modify target schema** - Breaks MV insert
5. **Don't use FINAL in MVs** - Performance issue

---

## Common Patterns

### Time-Series Rollup

```text
raw_events (1 row/event)
    ↓ MV
minute_events (1 row/minute/user)
    ↓ MV
hourly_events (1 row/hour/user)
    ↓ Refreshable MV
daily_summary (1 row/day)
```

### Multi-Tenant Aggregation

```sql
CREATE MATERIALIZED VIEW tenant_metrics_mv
TO tenant_metrics
AS SELECT
    tenant_id,
    toDate(created_at) AS date,
    event_type,
    count() AS events,
    uniq(user_id) AS users
FROM events
GROUP BY tenant_id, date, event_type;
```
