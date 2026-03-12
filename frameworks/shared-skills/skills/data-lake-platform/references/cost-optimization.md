# Cost Optimization

## Storage Optimization

### Compression

| Format | Compression | Size Reduction | Best For |
|--------|-------------|----------------|----------|
| Parquet + ZSTD | Level 3 | 70-80% | General use |
| Parquet + Snappy | Fast | 60-70% | Real-time |
| Parquet + LZ4 | Very fast | 50-60% | Low latency |

```python
# dlt with compression
pipeline.run(
    data,
    loader_file_format="parquet",
    parquet_compression="zstd"
)

# ClickHouse compression
CREATE TABLE events (...)
ENGINE = MergeTree()
SETTINGS min_compress_block_size = 65536,
         max_compress_block_size = 1048576;
```

### Partitioning Strategy

```sql
-- Good: Partition by date for time-series
PARTITIONED BY (date(created_at))

-- Better: Add bucketing for large cardinality
PARTITIONED BY (
    date(created_at),
    bucket(16, user_id)
)

-- Avoid: Too many small partitions
-- Bad: PARTITIONED BY (hour(created_at))  -- 24x more partitions
```

### Lifecycle Policies

```python
# S3 lifecycle for data tiers
{
    "Rules": [
        {
            "ID": "bronze-to-glacier",
            "Prefix": "bronze/",
            "Status": "Enabled",
            "Transitions": [
                {"Days": 90, "StorageClass": "GLACIER"}
            ]
        },
        {
            "ID": "delete-temp",
            "Prefix": "temp/",
            "Status": "Enabled",
            "Expiration": {"Days": 7}
        }
    ]
}
```

---

## Compute Optimization

### ClickHouse

```sql
-- Use PREWHERE for early filtering
SELECT * FROM events
PREWHERE date >= '2024-01-01'  -- Filters before reading columns
WHERE status = 'completed';

-- Use sampling for exploration
SELECT count() FROM events SAMPLE 0.01;  -- 1% sample

-- Optimize ORDER BY for common queries
ORDER BY (user_id, created_at)  -- Match query patterns
```

### Query Optimization

```sql
-- Avoid SELECT *
SELECT event_id, user_id, created_at  -- Only needed columns
FROM events
WHERE date >= '2024-01-01';

-- Use approximate functions
SELECT uniqHLL12(user_id) AS approx_users  -- Faster than exact count
FROM events;

-- Limit result sets
SELECT * FROM events
WHERE user_id = 123
ORDER BY created_at DESC
LIMIT 100;
```

---

## Cost Monitoring

### Tracking Query Costs

```sql
-- ClickHouse query log analysis
SELECT
    user,
    query_kind,
    count() AS queries,
    sum(read_bytes) / 1e9 AS gb_read,
    sum(query_duration_ms) / 1000 AS total_seconds
FROM system.query_log
WHERE event_date >= today() - 7
GROUP BY user, query_kind
ORDER BY gb_read DESC;
```

### Storage Analysis

```sql
-- ClickHouse table sizes
SELECT
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) AS size,
    sum(rows) AS rows,
    count() AS parts
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;
```

---

## Best Practices

1. **Compress everything** - ZSTD level 3 default
2. **Partition wisely** - Daily for most, hourly only if needed
3. **Expire old data** - Set retention policies
4. **Monitor costs** - Track query and storage costs
5. **Use tiered storage** - Hot/warm/cold data tiers
6. **Optimize queries** - Avoid SELECT *, use LIMIT
7. **Pre-aggregate** - Materialized views for common queries
