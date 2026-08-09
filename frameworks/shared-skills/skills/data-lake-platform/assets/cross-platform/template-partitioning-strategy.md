# Partitioning Strategy Template

## Overview

Data partitioning strategies for optimal query performance and storage efficiency.

## Partitioning Types

| Type | Best For | Example |
|------|----------|---------|
| **Time-based** | Time-series, event data | `PARTITION BY toYYYYMM(date)` |
| **Hash** | Even distribution | `PARTITION BY hash(user_id, 16)` |
| **Range** | Ordered data | `PARTITION BY range(amount)` |
| **List** | Categorical data | `PARTITION BY region` |
| **Composite** | Complex queries | `PARTITION BY (region, month)` |

---

## ClickHouse Partitioning

### Time-Based Partitioning

```sql
-- Monthly partitions (most common)
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type String,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at)
SETTINGS index_granularity = 8192;

-- Daily partitions (high volume)
CREATE TABLE events_daily (
    event_id UUID,
    user_id UInt64,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMMDD(created_at)
ORDER BY (user_id, created_at);

-- Weekly partitions
CREATE TABLE events_weekly (
    event_id UUID,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toMonday(created_at)
ORDER BY created_at;
```

### Composite Partitioning

```sql
-- Region + Month
CREATE TABLE sales (
    sale_id UUID,
    region String,
    amount Decimal(18, 2),
    sale_date Date
)
ENGINE = MergeTree()
PARTITION BY (region, toYYYYMM(sale_date))
ORDER BY (sale_date, sale_id);
```

### Ordering Key Strategy

```sql
-- Order by query patterns
-- Most selective column first
CREATE TABLE user_events (
    user_id UInt64,
    session_id UUID,
    event_type LowCardinality(String),
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, session_id, created_at)
-- Queries filtering by user_id will be fastest
```

### Skip Indices

```sql
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type String,
    properties String,
    created_at DateTime,
    -- Skip indices for additional columns
    INDEX idx_event_type event_type TYPE set(100) GRANULARITY 4,
    INDEX idx_properties properties TYPE tokenbf_v1(10240, 3, 0) GRANULARITY 4
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at);
```

---

## Apache Iceberg Partitioning

### Hidden Partitioning

```sql
-- Iceberg transforms (no partition columns in data)
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (
    months(created_at),      -- Monthly partitions
    bucket(16, user_id)      -- Hash buckets for user_id
);
```

### Partition Transforms

```sql
-- Time transforms
PARTITIONED BY (
    years(created_at),       -- Year
    months(created_at),      -- Month
    days(created_at),        -- Day
    hours(created_at)        -- Hour
)

-- Identity (exact value)
PARTITIONED BY (
    region,                  -- Each region = partition
    identity(status)         -- Each status = partition
)

-- Bucket (hash)
PARTITIONED BY (
    bucket(16, user_id),     -- 16 buckets by user_id hash
    bucket(8, order_id)
)

-- Truncate (for strings/numbers)
PARTITIONED BY (
    truncate(2, zip_code)    -- First 2 chars of zip
)
```

### Partition Evolution

```sql
-- Add partition field (no rewrite needed)
ALTER TABLE events ADD PARTITION FIELD bucket(16, user_id);

-- Remove partition field
ALTER TABLE events DROP PARTITION FIELD months(created_at);

-- Change partition granularity
ALTER TABLE events REPLACE PARTITION FIELD
    months(created_at) WITH days(created_at);
```

### Query Optimization

```python
# PyIceberg - partition pruning
from pyiceberg.catalog import load_catalog

catalog = load_catalog("rest")
table = catalog.load_table("db.events")

# Efficient query (uses partition pruning)
scan = table.scan(
    filter="created_at >= '2024-01-01' AND created_at < '2024-02-01'"
)
# Only reads January partition files

# Check partition metrics
for file in table.scan().to_arrow().column("file_path"):
    print(file)
```

---

## Delta Lake Partitioning

### Basic Partitioning

```python
# Create partitioned table
df.write.format("delta") \
    .partitionBy("year", "month") \
    .save("/delta/events")

# SQL
spark.sql("""
    CREATE TABLE events (
        event_id STRING,
        user_id BIGINT,
        created_at TIMESTAMP,
        year INT GENERATED ALWAYS AS (YEAR(created_at)),
        month INT GENERATED ALWAYS AS (MONTH(created_at))
    )
    USING DELTA
    PARTITIONED BY (year, month)
""")
```

### Z-Order Clustering

```sql
-- Optimize for multi-dimensional queries
OPTIMIZE events ZORDER BY (user_id, event_type);

-- Combine with partitioning
-- Partition by time, Z-order by query columns
OPTIMIZE events
WHERE created_at >= '2024-01-01'
ZORDER BY (user_id, product_id);
```

### Liquid Clustering (Delta 3.0+)

```sql
-- Auto-clustering without explicit partitioning
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    created_at TIMESTAMP
)
USING DELTA
CLUSTER BY (user_id, event_type);

-- Trigger clustering
OPTIMIZE events;
```

---

## DuckDB Partitioning

### Hive-Style Partitioning

```sql
-- Write partitioned Parquet
COPY events TO 's3://bucket/events'
(FORMAT PARQUET, PARTITION_BY (year, month));

-- Creates structure:
-- s3://bucket/events/year=2024/month=01/data.parquet
-- s3://bucket/events/year=2024/month=02/data.parquet
```

### Query Partitioned Data

```sql
-- DuckDB auto-detects partition columns
SELECT * FROM read_parquet('s3://bucket/events/*/*.parquet',
    hive_partitioning=true)
WHERE year = 2024 AND month = 1;
-- Only reads matching partitions
```

---

## Partition Sizing Guidelines

### Target Partition Size

| Data Volume | Partition Granularity | Target Size |
|-------------|----------------------|-------------|
| < 1 GB/day | Monthly | 1-10 GB |
| 1-10 GB/day | Weekly | 5-20 GB |
| 10-100 GB/day | Daily | 10-50 GB |
| > 100 GB/day | Hourly | 5-20 GB |

### Anti-Patterns

```sql
-- [FAIL] Too many partitions (>10k)
PARTITION BY toYYYYMMDD(created_at)  -- Daily for 10 years = 3650 partitions

-- [FAIL] Too few records per partition
PARTITION BY (region, category, toYYYYMMDD(date))  -- Explosive combination

-- [FAIL] High-cardinality partition key
PARTITION BY user_id  -- Millions of partitions

-- [OK] Balanced approach
PARTITION BY toYYYYMM(created_at)  -- ~120 partitions over 10 years
```

---

## ClickHouse Partition Management

### View Partitions

```sql
-- List partitions
SELECT
    partition,
    name,
    rows,
    formatReadableSize(bytes_on_disk) AS size,
    modification_time
FROM system.parts
WHERE table = 'events' AND active
ORDER BY partition DESC;

-- Partition statistics
SELECT
    partition,
    count() AS parts,
    sum(rows) AS total_rows,
    formatReadableSize(sum(bytes_on_disk)) AS total_size
FROM system.parts
WHERE table = 'events' AND active
GROUP BY partition
ORDER BY partition DESC;
```

### Partition Operations

```sql
-- Detach partition (keeps data, removes from table)
ALTER TABLE events DETACH PARTITION 202301;

-- Attach partition back
ALTER TABLE events ATTACH PARTITION 202301;

-- Drop partition (deletes data)
ALTER TABLE events DROP PARTITION 202301;

-- Move partition to another table
ALTER TABLE events MOVE PARTITION 202301 TO TABLE events_archive;

-- Freeze partition (backup)
ALTER TABLE events FREEZE PARTITION 202301;
```

### TTL with Partitions

```sql
CREATE TABLE events (
    event_id UUID,
    created_at DateTime,
    data String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY created_at
TTL created_at + INTERVAL 2 YEAR DELETE;
-- Drops old partitions automatically
```

---

## Best Practices

### DO

1. **Partition by query patterns** - most filtered column
2. **Keep partitions 1-50 GB** - too small = overhead, too large = slow queries
3. **Use time-based for time-series** - natural data locality
4. **Add secondary clustering** - Z-order or ordering key
5. **Monitor partition sizes** - rebalance if skewed

### DON'T

1. **Don't partition by high-cardinality columns** - user_id, session_id
2. **Don't create >10k partitions** - metadata overhead
3. **Don't skip partitioning for large tables** - full scans are slow
4. **Don't ignore partition pruning** - always filter by partition key
5. **Don't mix partition and sort key** - they serve different purposes

---

## Partition Pruning Validation

```sql
-- ClickHouse: Check if partition pruning works
EXPLAIN indexes = 1
SELECT * FROM events
WHERE created_at >= '2024-01-01' AND created_at < '2024-02-01';

-- Look for "Parts: X/Y" where X << Y indicates pruning worked

-- Query system.query_log for actual parts read
SELECT
    query,
    read_rows,
    read_bytes,
    result_rows
FROM system.query_log
WHERE query LIKE '%events%'
ORDER BY event_time DESC
LIMIT 10;
```
