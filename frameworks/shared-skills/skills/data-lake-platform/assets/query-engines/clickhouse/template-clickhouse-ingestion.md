# ClickHouse Ingestion Template

## Overview

Data ingestion patterns for loading data into ClickHouse.

## Ingestion Methods

| Method | Throughput | Latency | Best For |
|--------|------------|---------|----------|
| **Native INSERT** | High | Low | Batch loads |
| **Async INSERT** | Very High | Higher | High-frequency small batches |
| **Buffer Table** | Very High | Buffered | Real-time streams |
| **Kafka Engine** | High | Low | Kafka integration |
| **HTTP Interface** | Medium | Low | Simple integrations |

---

## Native Batch Insert

### Python Batch Insert

```python
import clickhouse_connect
from datetime import datetime

client = clickhouse_connect.get_client(
    host='localhost',
    port=8123,
    username='admin',
    password='password'
)

# Batch insert (recommended: 10k-100k rows per batch)
data = [
    [str(uuid.uuid4()), 1001, 'click', '{"page": "/home"}', datetime.now()],
    [str(uuid.uuid4()), 1002, 'view', '{"page": "/product"}', datetime.now()],
    # ... more rows
]

client.insert(
    'bronze.raw_events',
    data=data,
    column_names=['event_id', 'user_id', 'event_type', 'properties', 'created_at']
)
```

### INSERT FROM SELECT

```sql
-- Copy data between tables
INSERT INTO silver.stg_events
SELECT
    generateUUIDv4() AS event_id,
    JSONExtractUInt(raw_data, 'user_id') AS user_id,
    JSONExtractString(raw_data, 'event_type') AS event_type,
    JSONExtractString(raw_data, 'properties') AS properties,
    parseDateTimeBestEffort(JSONExtractString(raw_data, 'created_at')) AS created_at
FROM bronze.raw_events
WHERE _ingested_at >= today() - 1;
```

### INSERT FROM File

```sql
-- From local file (CSV)
INSERT INTO bronze.raw_events
FROM INFILE '/data/events.csv'
FORMAT CSV;

-- From S3
INSERT INTO bronze.raw_events
SELECT *
FROM s3(
    'https://s3.amazonaws.com/bucket/events/*.parquet',
    'AWS_ACCESS_KEY',
    'AWS_SECRET_KEY',
    'Parquet'
);

-- From URL
INSERT INTO bronze.raw_events
SELECT *
FROM url('https://api.example.com/data.json', 'JSONEachRow');
```

---

## Async Insert (High Throughput)

### Enable Async Insert

```sql
-- Session level
SET async_insert = 1;
SET wait_for_async_insert = 0;  -- Don't wait for flush
SET async_insert_max_data_size = 10000000;  -- 10 MB buffer
SET async_insert_busy_timeout_ms = 200;  -- Flush every 200ms

-- Insert (auto-batched)
INSERT INTO events VALUES (...);
```

### User-Level Configuration

```xml
<!-- users.xml -->
<clickhouse>
    <profiles>
        <streaming>
            <async_insert>1</async_insert>
            <wait_for_async_insert>0</wait_for_async_insert>
            <async_insert_max_data_size>10485760</async_insert_max_data_size>
            <async_insert_busy_timeout_ms>200</async_insert_busy_timeout_ms>
        </streaming>
    </profiles>
</clickhouse>
```

### Monitor Async Inserts

```sql
-- Check async insert queue
SELECT
    query_id,
    format,
    bytes,
    rows,
    flush_time_microseconds / 1000 AS flush_ms
FROM system.asynchronous_inserts
ORDER BY first_update DESC
LIMIT 20;
```

---

## Buffer Tables

### Buffer Table Setup

```sql
-- Target table
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type String,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at);

-- Buffer table (auto-flushes to events)
CREATE TABLE events_buffer AS events
ENGINE = Buffer(
    default,           -- Database
    events,            -- Target table
    16,                -- Num buffers
    10, 100,           -- Min/max flush seconds
    10000, 1000000,    -- Min/max flush rows
    10000000, 100000000 -- Min/max flush bytes
);
```

### Buffer Usage

```python
# Insert to buffer (high frequency OK)
for event in stream:
    client.insert('events_buffer', [event])
    # Auto-batched and flushed to events table
```

### Monitor Buffer

```sql
SELECT
    database, table,
    formatReadableSize(total_bytes) AS buffer_size,
    total_rows AS buffered_rows
FROM system.parts
WHERE table LIKE '%_buffer';
```

---

## Kafka Integration

### Kafka Engine Table

```sql
-- Kafka consumer table
CREATE TABLE events_kafka (
    event_id String,
    user_id UInt64,
    event_type String,
    properties String,
    created_at DateTime
)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse_consumer',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 4,
    kafka_max_block_size = 65536;

-- Target table
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type LowCardinality(String),
    properties String,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at);

-- Materialized view (auto-inserts from Kafka)
CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT
    toUUID(event_id) AS event_id,
    user_id,
    event_type,
    properties,
    created_at
FROM events_kafka;
```

### Kafka with Avro/Protobuf

```sql
CREATE TABLE events_kafka_avro (...)
ENGINE = Kafka
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse_avro',
    kafka_format = 'AvroConfluent',
    format_avro_schema_registry_url = 'http://schema-registry:8081';
```

---

## dlt Integration

### dlt to ClickHouse

```python
import dlt

@dlt.source
def api_source():
    @dlt.resource(
        name="events",
        write_disposition="append",
        primary_key="event_id"
    )
    def events():
        for batch in fetch_events():
            yield batch
    return events

pipeline = dlt.pipeline(
    pipeline_name="events_to_clickhouse",
    destination="clickhouse",
    dataset_name="bronze"
)

# Run pipeline
load_info = pipeline.run(api_source())
print(load_info)
```

### dlt Configuration

```toml
# .dlt/secrets.toml
[destination.clickhouse.credentials]
host = "localhost"
port = 8123
username = "admin"
password = "secret"
database = "analytics"
secure = false
```

---

## Incremental Loading

### Timestamp-Based

```sql
-- Track last loaded timestamp
CREATE TABLE meta.load_state (
    table_name String,
    last_loaded_at DateTime
)
ENGINE = ReplacingMergeTree(last_loaded_at)
ORDER BY table_name;

-- Load incremental data
INSERT INTO silver.stg_events
SELECT *
FROM bronze.raw_events
WHERE _ingested_at > (
    SELECT coalesce(max(last_loaded_at), '1970-01-01')
    FROM meta.load_state
    WHERE table_name = 'silver.stg_events'
);

-- Update state
INSERT INTO meta.load_state VALUES ('silver.stg_events', now());
```

### Using ReplacingMergeTree

```sql
-- Upsert pattern with ReplacingMergeTree
CREATE TABLE silver.users (
    user_id UInt64,
    email String,
    name String,
    updated_at DateTime
)
ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;

-- Insert new/updated records (auto-deduplicates)
INSERT INTO silver.users
SELECT * FROM bronze.raw_users
WHERE updated_at > @last_run;
```

---

## Best Practices

### DO

1. **Batch inserts** - 10k-100k rows per INSERT
2. **Use native format** - Faster than JSON/CSV
3. **Partition by time** - For efficient pruning
4. **Compress JSON columns** - ZSTD(3) or higher
5. **Monitor insert rates** - Via system.query_log

### DON'T

1. **Don't insert row by row** - Use batching
2. **Don't use INSERT SYNC for streams** - Use async/buffer
3. **Don't ignore backpressure** - Monitor queue sizes
4. **Don't skip deduplication** - Use ReplacingMergeTree

---

## Monitoring

```sql
-- Insert performance
SELECT
    event_date,
    count() AS inserts,
    sum(written_rows) AS total_rows,
    formatReadableSize(sum(written_bytes)) AS total_bytes,
    round(sum(written_rows) / sum(query_duration_ms) * 1000) AS rows_per_sec
FROM system.query_log
WHERE query_kind = 'Insert'
  AND event_date >= today() - 7
GROUP BY event_date
ORDER BY event_date DESC;

-- Failed inserts
SELECT
    event_time,
    query,
    exception
FROM system.query_log
WHERE query_kind = 'Insert'
  AND exception != ''
  AND event_date >= today()
ORDER BY event_time DESC
LIMIT 20;
```
