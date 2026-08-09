# Cost Optimization Template

## Overview

Strategies for reducing storage, compute, and operational costs in data lake environments.

## Cost Categories

| Category | Typical Share | Optimization Potential |
|----------|---------------|----------------------|
| **Storage** | 30-50% | High (compression, tiering) |
| **Compute** | 40-60% | High (query optimization) |
| **Egress** | 5-15% | Medium (data locality) |
| **Operations** | 5-10% | Medium (automation) |

---

## Storage Optimization

### Compression Strategies

```sql
-- ClickHouse: Column-level compression
CREATE TABLE events (
    event_id UUID CODEC(ZSTD(3)),
    user_id UInt64 CODEC(Delta, ZSTD(1)),
    event_type LowCardinality(String),  -- Dictionary encoding
    properties String CODEC(ZSTD(5)),   -- High compression for JSON
    created_at DateTime CODEC(DoubleDelta, ZSTD(1))
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at);
```

### Codec Selection Guide

| Data Type | Recommended Codec | Compression Ratio |
|-----------|------------------|-------------------|
| Timestamps | DoubleDelta, ZSTD | 10-50x |
| Sequential IDs | Delta, ZSTD | 20-100x |
| Low cardinality | LowCardinality | 5-20x |
| JSON/text | ZSTD(3-5) | 3-10x |
| Floats | Gorilla, ZSTD | 5-15x |
| UUIDs | ZSTD(1) | 2-3x |

### Iceberg File Optimization

```sql
-- Compact small files
CALL catalog.system.rewrite_data_files(
    table => 'db.events',
    options => map('target-file-size-bytes', '134217728')  -- 128 MB
);

-- Remove orphan files
CALL catalog.system.remove_orphan_files(
    table => 'db.events',
    older_than => TIMESTAMP '2024-01-01 00:00:00'
);

-- Expire old snapshots
CALL catalog.system.expire_snapshots(
    table => 'db.events',
    older_than => TIMESTAMP '2024-06-01 00:00:00',
    retain_last => 10
);
```

### Data Tiering

```yaml
# Iceberg storage tiering
storage_tiers:
  hot:
    path: s3://data-lake-hot/
    retention: 30d
    storage_class: STANDARD

  warm:
    path: s3://data-lake-warm/
    retention: 365d
    storage_class: STANDARD_IA

  cold:
    path: s3://data-lake-archive/
    retention: 7y
    storage_class: GLACIER
```

```python
# Automated tiering script
from datetime import datetime, timedelta

def tier_partitions(table, catalog):
    """Move old partitions to cheaper storage."""
    hot_cutoff = datetime.now() - timedelta(days=30)
    warm_cutoff = datetime.now() - timedelta(days=365)

    # Move to warm tier
    catalog.execute(f"""
        ALTER TABLE {table}
        SET PARTITION FIELD location = 's3://data-lake-warm/'
        WHERE created_at < '{hot_cutoff.isoformat()}'
          AND created_at >= '{warm_cutoff.isoformat()}'
    """)
```

### ClickHouse Storage Policies

```xml
<!-- config.xml -->
<storage_configuration>
    <disks>
        <hot>
            <type>local</type>
            <path>/data/hot/</path>
        </hot>
        <cold>
            <type>s3</type>
            <endpoint>https://s3.amazonaws.com/bucket/cold/</endpoint>
        </cold>
    </disks>
    <policies>
        <tiered>
            <volumes>
                <hot>
                    <disk>hot</disk>
                </hot>
                <cold>
                    <disk>cold</disk>
                </cold>
            </volumes>
            <move_factor>0.1</move_factor>
        </tiered>
    </policies>
</storage_configuration>
```

```sql
-- Use tiered storage
CREATE TABLE events (...)
ENGINE = MergeTree()
SETTINGS storage_policy = 'tiered';

-- TTL-based tiering
CREATE TABLE events (
    created_at DateTime,
    data String
)
ENGINE = MergeTree()
ORDER BY created_at
TTL created_at + INTERVAL 30 DAY TO VOLUME 'cold',
    created_at + INTERVAL 365 DAY DELETE
SETTINGS storage_policy = 'tiered';
```

---

## Compute Optimization

### Query Optimization

```sql
-- ClickHouse: Use PREWHERE for early filtering
SELECT user_id, count()
FROM events
PREWHERE created_at >= '2024-01-01'  -- Filter before reading columns
WHERE event_type = 'purchase'
GROUP BY user_id;

-- Use sampling for exploration
SELECT event_type, count()
FROM events
SAMPLE 0.01  -- 1% sample
GROUP BY event_type;

-- Limit columns read
SELECT user_id, created_at  -- Don't SELECT *
FROM events
WHERE user_id = 123;
```

### Materialized Views for Common Queries

```sql
-- Pre-aggregate expensive queries
CREATE MATERIALIZED VIEW hourly_events_mv
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type)
AS SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users
FROM events
GROUP BY hour, event_type;

-- Query the view instead of raw table
SELECT * FROM hourly_events_mv
WHERE hour >= '2024-01-01'
  AND hour < '2024-02-01';
```

### Projection Optimization (ClickHouse)

```sql
-- Create projection for different access patterns
ALTER TABLE events ADD PROJECTION events_by_type (
    SELECT * ORDER BY (event_type, created_at)
);

-- Materialize projection
ALTER TABLE events MATERIALIZE PROJECTION events_by_type;

-- ClickHouse auto-selects best projection
SELECT * FROM events WHERE event_type = 'purchase';
```

### Resource Quotas

```sql
-- ClickHouse: Limit resource usage
CREATE SETTINGS PROFILE analyst_profile
SETTINGS
    max_memory_usage = 10000000000,          -- 10 GB
    max_execution_time = 300,                -- 5 minutes
    max_rows_to_read = 1000000000,           -- 1 billion rows
    max_bytes_to_read = 100000000000;        -- 100 GB

-- Apply to user
ALTER USER analyst SETTINGS PROFILE 'analyst_profile';
```

---

## Ingestion Optimization

### Batch Size Tuning

```python
# dlt: Optimal batch sizes
pipeline = dlt.pipeline(
    pipeline_name="events",
    destination="clickhouse"
)

# For ClickHouse: larger batches = better compression
pipeline.run(
    source(),
    loader_file_format="parquet",  # Better than JSON
    write_disposition="append"
)
```

### Buffer Tables (ClickHouse)

```sql
-- Buffer for high-frequency inserts
CREATE TABLE events_buffer AS events
ENGINE = Buffer(
    default, events,       -- Target table
    16,                    -- Num buffers
    10, 100,               -- Min/max seconds
    10000, 1000000,        -- Min/max rows
    10000000, 100000000    -- Min/max bytes
);

-- Insert to buffer (auto-flushes to events)
INSERT INTO events_buffer VALUES (...);
```

### Async Inserts (ClickHouse 21.8+)

```sql
-- Enable async inserts for small batches
SET async_insert = 1;
SET wait_for_async_insert = 0;
SET async_insert_max_data_size = 10000000;  -- 10 MB
SET async_insert_busy_timeout_ms = 200;

-- ClickHouse batches small inserts automatically
INSERT INTO events VALUES (...);  -- Batched with other inserts
```

---

## Cost Monitoring

### Storage Metrics

```sql
-- ClickHouse: Storage usage by table
SELECT
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) AS size,
    formatReadableSize(sum(data_compressed_bytes)) AS compressed,
    formatReadableSize(sum(data_uncompressed_bytes)) AS uncompressed,
    round(sum(data_uncompressed_bytes) / sum(data_compressed_bytes), 2) AS ratio
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;

-- Storage by partition
SELECT
    partition,
    formatReadableSize(sum(bytes_on_disk)) AS size,
    sum(rows) AS rows
FROM system.parts
WHERE table = 'events' AND active
GROUP BY partition
ORDER BY partition DESC;
```

### Query Cost Tracking

```sql
-- ClickHouse: Query resource usage
SELECT
    user,
    query_kind,
    count() AS queries,
    formatReadableSize(sum(read_bytes)) AS total_read,
    formatReadableSize(sum(memory_usage)) AS total_memory,
    round(sum(query_duration_ms) / 1000, 2) AS total_seconds
FROM system.query_log
WHERE event_date >= today() - 7
  AND type = 'QueryFinish'
GROUP BY user, query_kind
ORDER BY sum(read_bytes) DESC;

-- Expensive queries
SELECT
    query,
    formatReadableSize(read_bytes) AS read_size,
    formatReadableSize(memory_usage) AS memory,
    query_duration_ms / 1000 AS seconds
FROM system.query_log
WHERE event_date >= today()
  AND type = 'QueryFinish'
ORDER BY read_bytes DESC
LIMIT 20;
```

### Cost Dashboard Queries

```sql
-- Daily cost estimate
SELECT
    event_date,
    formatReadableSize(sum(read_bytes)) AS bytes_read,
    round(sum(read_bytes) / 1e12 * 0.005, 2) AS estimated_cost_usd,  -- $5/TB
    count() AS query_count
FROM system.query_log
WHERE event_date >= today() - 30
  AND type = 'QueryFinish'
GROUP BY event_date
ORDER BY event_date DESC;
```

---

## Automation Scripts

### Automated Compaction

```python
# scheduled_maintenance.py
from datetime import datetime, timedelta

def run_maintenance():
    """Daily maintenance tasks."""

    # 1. Compact small files
    execute("OPTIMIZE TABLE events FINAL")

    # 2. Expire old snapshots (Iceberg)
    cutoff = (datetime.now() - timedelta(days=7)).isoformat()
    execute(f"""
        CALL catalog.system.expire_snapshots(
            table => 'db.events',
            older_than => TIMESTAMP '{cutoff}'
        )
    """)

    # 3. Remove orphan files
    execute("""
        CALL catalog.system.remove_orphan_files(table => 'db.events')
    """)

    # 4. Analyze tables
    execute("ANALYZE TABLE events")

if __name__ == "__main__":
    run_maintenance()
```

### Cost Alerting

```python
# cost_monitor.py
def check_costs():
    """Alert if costs exceed threshold."""

    daily_cost = query("""
        SELECT sum(read_bytes) / 1e12 * 5 AS cost_usd
        FROM system.query_log
        WHERE event_date = today() AND type = 'QueryFinish'
    """)[0]["cost_usd"]

    if daily_cost > 100:  # $100/day threshold
        send_alert(f"Daily cost ${daily_cost:.2f} exceeds threshold")

    # Check storage growth
    storage_gb = query("""
        SELECT sum(bytes_on_disk) / 1e9 AS gb
        FROM system.parts WHERE active
    """)[0]["gb"]

    weekly_growth = query("""
        SELECT sum(bytes_on_disk) / 1e9 AS gb
        FROM system.parts
        WHERE modification_time >= today() - 7
    """)[0]["gb"]

    if weekly_growth > storage_gb * 0.1:  # >10% weekly growth
        send_alert(f"Storage growth {weekly_growth:.0f} GB this week")
```

---

## Best Practices Checklist

### Storage

- [ ] Enable compression (ZSTD level 3+ for text)
- [ ] Use LowCardinality for low-cardinality strings
- [ ] Implement data tiering (hot/warm/cold)
- [ ] Set TTL for data retention
- [ ] Compact small files regularly
- [ ] Expire old snapshots (Iceberg/Delta)

### Compute

- [ ] Use materialized views for common aggregations
- [ ] Create projections for different access patterns
- [ ] Implement query resource limits
- [ ] Use PREWHERE for early filtering
- [ ] Avoid SELECT * in production queries
- [ ] Use sampling for exploration

### Operations

- [ ] Automate maintenance tasks
- [ ] Monitor costs daily
- [ ] Set up cost alerts
- [ ] Review expensive queries weekly
- [ ] Track storage growth trends
