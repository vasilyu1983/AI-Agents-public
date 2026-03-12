# Query Engine Patterns

## Lake Query vs Serving Store

- Lake query engines (Trino, Spark): best for open table formats + large joins + federated queries.
- Serving engines (ClickHouse, StarRocks/Doris): best for low-latency dashboards and high concurrency.
- Embedded engines (DuckDB): best for local dev, notebooks, and small/medium data exploration.

## Engine Comparison (Pragmatic)

| Engine | Best for | Typical deployment |
|--------|----------|--------------------|
| Trino | Lakehouse SQL on Iceberg/Delta/Hudi; federated queries | Cluster |
| Spark | Heavy transforms, ML feature builds, batch and structured streaming | Cluster |
| ClickHouse | Low-latency analytics serving; high QPS dashboards | Cluster/Cloud |
| StarRocks/Doris | MPP serving with complex joins and real-time ingestion | Cluster |
| DuckDB | Local/embedded analytics, dev/test, edge workloads | In-process |

### Trino Pattern (Iceberg)

```sql
-- Typical workflow: define a catalog (Hive/Glue/REST) and query Iceberg tables
SELECT *
FROM iceberg.analytics.events
WHERE event_date >= DATE '2024-01-01';
```

---

## ClickHouse Patterns

### Table Engine Selection

```sql
-- MergeTree: Default, best for most cases
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type LowCardinality(String),
    event_data String,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at)
SETTINGS index_granularity = 8192;

-- ReplacingMergeTree: Deduplication by version
CREATE TABLE users (
    user_id UInt64,
    email String,
    name String,
    updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;

-- AggregatingMergeTree: Pre-aggregated metrics
CREATE TABLE hourly_metrics (
    hour DateTime,
    user_id UInt64,
    event_count AggregateFunction(count, UInt64),
    unique_events AggregateFunction(uniq, String)
)
ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, user_id);

-- CollapsingMergeTree: State changes (sign column)
CREATE TABLE balances (
    user_id UInt64,
    balance Decimal(18, 2),
    updated_at DateTime,
    sign Int8  -- 1 for insert, -1 for delete
)
ENGINE = CollapsingMergeTree(sign)
ORDER BY (user_id, updated_at);
```

### Materialized Views for Real-Time Aggregation

```sql
-- Source table
CREATE TABLE raw_events (
    event_id UUID,
    user_id UInt64,
    event_type String,
    created_at DateTime
)
ENGINE = MergeTree()
ORDER BY (created_at, event_id);

-- Aggregated view (updates automatically)
CREATE MATERIALIZED VIEW hourly_stats
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type)
AS SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users
FROM raw_events
GROUP BY hour, event_type;
```

### Query Optimization

```sql
-- Use PREWHERE for early filtering (before reading columns)
SELECT user_id, event_type, count()
FROM events
PREWHERE created_at >= '2024-01-01'
WHERE event_type = 'purchase'
GROUP BY user_id, event_type;

-- Use FINAL sparingly (forces deduplication)
SELECT * FROM users FINAL WHERE user_id = 123;

-- Better: Use argMax for latest value
SELECT
    user_id,
    argMax(email, updated_at) AS email,
    argMax(name, updated_at) AS name
FROM users
GROUP BY user_id;

-- Sample for exploration
SELECT event_type, count()
FROM events
SAMPLE 0.1  -- 10% sample
GROUP BY event_type;
```

### Replication Setup

```sql
-- ReplicatedMergeTree (requires ZooKeeper/ClickHouse Keeper)
CREATE TABLE events ON CLUSTER my_cluster (
    event_id UUID,
    user_id UInt64,
    created_at DateTime
)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at);

-- Distributed table for queries across shards
CREATE TABLE events_distributed ON CLUSTER my_cluster
AS events
ENGINE = Distributed(my_cluster, default, events, user_id);
```

---

## DuckDB Patterns

### In-Process Analytics

```python
import duckdb

# Create persistent database
con = duckdb.connect("analytics.duckdb")

# Query Parquet files directly
df = con.execute("""
    SELECT
        date_trunc('day', created_at) AS date,
        event_type,
        count(*) AS events
    FROM read_parquet('s3://bucket/events/*.parquet')
    WHERE created_at >= '2024-01-01'
    GROUP BY 1, 2
""").df()

# Query Iceberg tables
con.execute("INSTALL iceberg; LOAD iceberg;")
df = con.execute("""
    SELECT * FROM iceberg_scan('s3://bucket/iceberg/events')
    WHERE created_at >= '2024-01-01'
""").df()
```

### Integration with Pandas/Polars

```python
import duckdb
import pandas as pd

# Query pandas DataFrame
df = pd.read_csv("data.csv")
result = duckdb.query("""
    SELECT category, sum(amount) AS total
    FROM df
    GROUP BY category
""").df()

# Export to Parquet
duckdb.query("""
    COPY (SELECT * FROM df WHERE amount > 100)
    TO 'filtered.parquet' (FORMAT PARQUET)
""")
```

### Window Functions

```sql
-- Running totals and rankings
SELECT
    date,
    product,
    sales,
    sum(sales) OVER (
        PARTITION BY product
        ORDER BY date
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_sales,
    rank() OVER (
        PARTITION BY date
        ORDER BY sales DESC
    ) AS daily_rank
FROM sales_data;
```

---

## Apache Doris Patterns

### Table Types

```sql
-- Duplicate Model: Store all data (default)
CREATE TABLE events (
    event_id BIGINT,
    user_id BIGINT,
    event_type VARCHAR(50),
    created_at DATETIME
)
DUPLICATE KEY(event_id, user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 16
PROPERTIES ("replication_num" = "3");

-- Aggregate Model: Pre-aggregation
CREATE TABLE metrics (
    date DATE,
    user_id BIGINT,
    visit_count BIGINT SUM,
    revenue DECIMAL(18,2) SUM,
    last_visit DATETIME REPLACE
)
AGGREGATE KEY(date, user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 16;

-- Unique Model: Upsert semantics
CREATE TABLE users (
    user_id BIGINT,
    email VARCHAR(255),
    name VARCHAR(100),
    updated_at DATETIME
)
UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 8;
```

### Real-Time Ingestion

```sql
-- Stream Load (HTTP API)
curl --location-trusted -u user:password \
    -H "label:load_20240101_001" \
    -H "column_separator:," \
    -T data.csv \
    http://doris-fe:8030/api/db/table/_stream_load

-- Routine Load from Kafka
CREATE ROUTINE LOAD db.kafka_load ON events
COLUMNS TERMINATED BY ",",
COLUMNS(event_id, user_id, event_type, created_at)
FROM KAFKA (
    "kafka_broker_list" = "kafka:9092",
    "kafka_topic" = "events",
    "property.group.id" = "doris_consumer"
);
```

---

## StarRocks Patterns

### Catalog Integration (Iceberg, Hudi, Delta)

```sql
-- Create Iceberg catalog
CREATE EXTERNAL CATALOG iceberg_catalog
PROPERTIES (
    "type" = "iceberg",
    "iceberg.catalog.type" = "rest",
    "iceberg.catalog.uri" = "http://rest-catalog:8181"
);

-- Query Iceberg table
SELECT * FROM iceberg_catalog.db.events
WHERE created_at >= '2024-01-01';

-- Create materialized view on external data
CREATE MATERIALIZED VIEW mv_daily_stats
DISTRIBUTED BY HASH(date) BUCKETS 8
REFRESH ASYNC START('2024-01-01 00:00:00') EVERY (INTERVAL 1 HOUR)
AS SELECT
    date(created_at) AS date,
    count(*) AS events
FROM iceberg_catalog.db.events
GROUP BY date(created_at);
```

---

## Performance Tuning

### ClickHouse

```sql
-- Check query execution
EXPLAIN PIPELINE SELECT ... FROM events WHERE ...;

-- Optimize table (merge parts)
OPTIMIZE TABLE events FINAL;

-- Monitor slow queries
SELECT
    query,
    query_duration_ms,
    read_rows,
    read_bytes
FROM system.query_log
WHERE type = 'QueryFinish'
ORDER BY query_duration_ms DESC
LIMIT 10;
```

### DuckDB

```sql
-- Explain query plan
EXPLAIN ANALYZE SELECT ... FROM events;

-- Set memory limit
SET memory_limit = '4GB';

-- Parallel processing
SET threads = 8;
```

### General Tips

1. **Partition by time** for time-series data
2. **Order by query patterns** (most filtered columns first)
3. **Use appropriate data types** (LowCardinality, Decimal)
4. **Pre-aggregate** with materialized views
5. **Monitor query patterns** and optimize accordingly
