# ClickHouse Optimization Template

## Overview

Performance optimization techniques for ClickHouse queries and tables.

## Optimization Hierarchy

| Level | Impact | Effort | Examples |
|-------|--------|--------|----------|
| **Schema Design** | Very High | High | Table engines, partitioning, ordering |
| **Query Optimization** | High | Medium | PREWHERE, sampling, projections |
| **Server Tuning** | Medium | Low | Memory, threads, caches |
| **Hardware** | High | High | SSD, RAM, CPU cores |

---

## Schema Optimization

### Table Engine Selection

```sql
-- MergeTree: General purpose (default choice)
CREATE TABLE events (...)
ENGINE = MergeTree()
ORDER BY (user_id, created_at);

-- ReplacingMergeTree: Deduplicate by version
CREATE TABLE users (...)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;

-- SummingMergeTree: Auto-sum numeric columns
CREATE TABLE daily_metrics (...)
ENGINE = SummingMergeTree()
ORDER BY (date, metric_name);

-- AggregatingMergeTree: Pre-aggregated state
CREATE TABLE hourly_stats (
    hour DateTime,
    user_count AggregateFunction(uniq, UInt64),
    event_count AggregateFunction(count, UInt64)
)
ENGINE = AggregatingMergeTree()
ORDER BY hour;
```

### Optimal Ordering Key

```sql
-- Order by cardinality (low → high) and query patterns
-- Most selective columns first

-- GOOD: Low cardinality first, matches query patterns
CREATE TABLE events (...)
ENGINE = MergeTree()
ORDER BY (tenant_id, user_id, created_at);
-- tenant_id: ~100 values
-- user_id: ~1M values
-- created_at: continuous

-- [FAIL] Bad: High cardinality first
ORDER BY (event_id, created_at, user_id);
```

### Column Types

```sql
CREATE TABLE events (
    -- Use smallest type that fits
    event_id UUID,                              -- 16 bytes
    user_id UInt64,                             -- 8 bytes (not Int64 if always positive)
    amount Decimal(18, 2),                      -- Exact decimals

    -- Use LowCardinality for <10k unique values
    event_type LowCardinality(String),          -- Dictionary encoded
    country LowCardinality(String),
    status LowCardinality(String),

    -- Nullable only when necessary (adds overhead)
    optional_field Nullable(String),

    -- DateTime vs Date
    created_at DateTime,                        -- 4 bytes
    event_date Date MATERIALIZED toDate(created_at)  -- 2 bytes
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (event_type, user_id, created_at);
```

### Compression Codecs

```sql
CREATE TABLE events (
    -- Sequential data: Delta + ZSTD
    id UInt64 CODEC(Delta, ZSTD(1)),
    created_at DateTime CODEC(DoubleDelta, ZSTD(1)),

    -- Low cardinality: LowCardinality (implicit dict encoding)
    event_type LowCardinality(String),

    -- JSON/text: High ZSTD level
    properties String CODEC(ZSTD(5)),

    -- Floats: Gorilla for time series
    metric_value Float64 CODEC(Gorilla, ZSTD(1)),

    -- Default: ZSTD(1) is good general choice
    description String CODEC(ZSTD(1))
)
ENGINE = MergeTree();
```

---

## Query Optimization

### PREWHERE (Early Filtering)

```sql
-- PREWHERE filters before reading all columns
-- Use for highly selective conditions

-- GOOD: PREWHERE on indexed/partition column
SELECT user_id, event_type, properties
FROM events
PREWHERE created_at >= '2024-01-01'  -- Filter first
WHERE event_type = 'purchase';        -- Then filter

-- Auto-optimization (ClickHouse moves WHERE to PREWHERE automatically)
-- But explicit PREWHERE can help with complex queries
```

### Avoid SELECT *

```sql
-- [FAIL] Bad: Reads all columns
SELECT * FROM events WHERE user_id = 123;

-- GOOD: Only needed columns
SELECT event_id, event_type, created_at
FROM events
WHERE user_id = 123;
```

### Use Projections

```sql
-- Create projection for different access pattern
ALTER TABLE events ADD PROJECTION events_by_type (
    SELECT *
    ORDER BY (event_type, created_at)
);

-- Materialize projection
ALTER TABLE events MATERIALIZE PROJECTION events_by_type;

-- ClickHouse auto-selects optimal projection
SELECT * FROM events WHERE event_type = 'purchase';
-- Uses events_by_type projection automatically
```

### Skip Indices

```sql
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type String,
    properties String,
    created_at DateTime,

    -- Skip index for text search
    INDEX idx_props properties TYPE tokenbf_v1(10240, 3, 0) GRANULARITY 4,

    -- Skip index for set membership
    INDEX idx_type event_type TYPE set(100) GRANULARITY 4,

    -- Skip index for bloom filter
    INDEX idx_user user_id TYPE bloom_filter(0.01) GRANULARITY 4
)
ENGINE = MergeTree()
ORDER BY created_at;
```

### Sampling

```sql
-- Add SAMPLE BY clause to table
CREATE TABLE events (...)
ENGINE = MergeTree()
ORDER BY (user_id, created_at)
SAMPLE BY user_id;

-- Query with sampling (for exploration)
SELECT event_type, count()
FROM events
SAMPLE 0.1  -- 10% sample
GROUP BY event_type;

-- Sample by rows
SELECT * FROM events SAMPLE 10000;  -- ~10000 rows
```

---

## Aggregation Optimization

### Pre-Aggregation with Materialized Views

```sql
-- Source table
CREATE TABLE raw_events (...)
ENGINE = MergeTree()
ORDER BY created_at;

-- Pre-aggregated hourly stats
CREATE MATERIALIZED VIEW hourly_stats
ENGINE = SummingMergeTree()
ORDER BY (hour, event_type)
AS SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS events,
    uniq(user_id) AS users
FROM raw_events
GROUP BY hour, event_type;

-- Query aggregated data (100x faster than raw)
SELECT * FROM hourly_stats
WHERE hour >= '2024-01-01';
```

### AggregatingMergeTree for Complex Aggregates

```sql
-- Store aggregate state
CREATE TABLE user_stats (
    date Date,
    user_id UInt64,
    event_count AggregateFunction(count, UInt64),
    unique_events AggregateFunction(uniq, String),
    total_amount AggregateFunction(sum, Decimal(18,2))
)
ENGINE = AggregatingMergeTree()
ORDER BY (date, user_id);

-- Insert with -State functions
INSERT INTO user_stats
SELECT
    toDate(created_at) AS date,
    user_id,
    countState() AS event_count,
    uniqState(event_type) AS unique_events,
    sumState(amount) AS total_amount
FROM raw_events
GROUP BY date, user_id;

-- Query with -Merge functions
SELECT
    user_id,
    countMerge(event_count) AS total_events,
    uniqMerge(unique_events) AS unique_types,
    sumMerge(total_amount) AS total
FROM user_stats
WHERE date >= '2024-01-01'
GROUP BY user_id;
```

---

## Server Configuration

### Memory Settings

```xml
<!-- config.xml -->
<clickhouse>
    <!-- Per-query memory limit -->
    <max_memory_usage>10000000000</max_memory_usage>  <!-- 10 GB -->

    <!-- Per-server memory limit -->
    <max_server_memory_usage_ratio>0.9</max_server_memory_usage_ratio>

    <!-- Mark cache (index) -->
    <mark_cache_size>5368709120</mark_cache_size>  <!-- 5 GB -->

    <!-- Uncompressed cache (data) -->
    <uncompressed_cache_size>8589934592</uncompressed_cache_size>  <!-- 8 GB -->

    <!-- Compiled expression cache -->
    <compiled_expression_cache_size>134217728</compiled_expression_cache_size>
</clickhouse>
```

### Thread Settings

```xml
<clickhouse>
    <!-- Background merge threads -->
    <background_pool_size>16</background_pool_size>

    <!-- Background move threads -->
    <background_move_pool_size>8</background_move_pool_size>

    <!-- Max threads per query -->
    <max_threads>8</max_threads>
</clickhouse>
```

### Query Settings

```sql
-- Session-level optimizations
SET max_threads = 8;
SET max_memory_usage = 10000000000;
SET max_bytes_before_external_group_by = 5000000000;
SET max_bytes_before_external_sort = 5000000000;
SET optimize_aggregation_in_order = 1;
SET compile_expressions = 1;
SET min_count_to_compile_expression = 3;
```

---

## Monitoring Performance

### Slow Query Analysis

```sql
-- Slow queries
SELECT
    query,
    query_duration_ms,
    read_rows,
    formatReadableSize(read_bytes) AS read_size,
    formatReadableSize(memory_usage) AS memory
FROM system.query_log
WHERE event_date >= today()
  AND type = 'QueryFinish'
  AND query_duration_ms > 1000
ORDER BY query_duration_ms DESC
LIMIT 20;
```

### Query Explanation

```sql
-- Explain query plan
EXPLAIN PLAN
SELECT user_id, count()
FROM events
WHERE created_at >= '2024-01-01'
GROUP BY user_id;

-- Explain with pipeline
EXPLAIN PIPELINE
SELECT ...;

-- Explain with indexes
EXPLAIN indexes = 1
SELECT ...;
```

### Part Statistics

```sql
-- Parts per table
SELECT
    table,
    count() AS parts,
    sum(rows) AS total_rows,
    formatReadableSize(sum(bytes_on_disk)) AS size
FROM system.parts
WHERE active
GROUP BY table
ORDER BY sum(bytes_on_disk) DESC;

-- Tables needing optimization (too many parts)
SELECT database, table, count() AS parts
FROM system.parts
WHERE active
GROUP BY database, table
HAVING count() > 100
ORDER BY parts DESC;
```

### Optimize Tables

```sql
-- Merge small parts
OPTIMIZE TABLE events;

-- Force final merge (slower, use sparingly)
OPTIMIZE TABLE events FINAL;

-- Optimize single partition
OPTIMIZE TABLE events PARTITION 202401;
```

---

## Best Practices Summary

| Area | Recommendation |
|------|----------------|
| **Order Key** | Low cardinality first, match query patterns |
| **Types** | Smallest type, LowCardinality for <10k values |
| **Compression** | Delta+ZSTD for timestamps, ZSTD(3-5) for text |
| **Queries** | PREWHERE, avoid SELECT *, use projections |
| **Aggregation** | Materialized views, AggregatingMergeTree |
| **Memory** | 10GB per query, 90% server limit |
| **Monitoring** | Track slow queries, part counts |
