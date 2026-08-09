# Apache Doris Setup Template

## Overview

Setting up Apache Doris for real-time analytics.

## Architecture

```text
┌─────────────────────────────────────────────────────┐
│                    Frontend (FE)                     │
│              (Metadata, Query Planning)              │
│    ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│    │   FE 1   │  │   FE 2   │  │   FE 3   │        │
│    │ (Leader) │  │(Follower)│  │(Follower)│        │
│    └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         ▼               ▼               ▼
┌──────────────┐ ┌──────────────┐ ┌──────────────┐
│   Backend 1  │ │   Backend 2  │ │   Backend 3  │
│     (BE)     │ │     (BE)     │ │     (BE)     │
│  ┌────────┐  │ │  ┌────────┐  │ │  ┌────────┐  │
│  │ Tablet │  │ │  │ Tablet │  │ │  │ Tablet │  │
│  └────────┘  │ │  └────────┘  │ │  └────────┘  │
└──────────────┘ └──────────────┘ └──────────────┘
```

---

## Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  fe:
    image: apache/doris:2.0.3-fe
    hostname: fe
    ports:
      - "8030:8030"   # HTTP
      - "9030:9030"   # MySQL protocol
    volumes:
      - fe_data:/opt/apache-doris/fe/doris-meta
      - ./fe.conf:/opt/apache-doris/fe/conf/fe.conf
    environment:
      FE_SERVERS: "fe:9010"
      FE_ID: 1

  be1:
    image: apache/doris:2.0.3-be
    hostname: be1
    depends_on:
      - fe
    volumes:
      - be1_data:/opt/apache-doris/be/storage
      - ./be.conf:/opt/apache-doris/be/conf/be.conf
    environment:
      FE_SERVERS: "fe:9010"
      BE_ADDR: "be1:9050"

  be2:
    image: apache/doris:2.0.3-be
    hostname: be2
    depends_on:
      - fe
    volumes:
      - be2_data:/opt/apache-doris/be/storage
    environment:
      FE_SERVERS: "fe:9010"
      BE_ADDR: "be2:9050"

volumes:
  fe_data:
  be1_data:
  be2_data:
```

---

## Table Models

### Duplicate Model (Default)

```sql
-- Store all rows (no aggregation)
CREATE TABLE events (
    event_id BIGINT,
    user_id BIGINT,
    event_type VARCHAR(50),
    properties JSON,
    created_at DATETIME
)
DUPLICATE KEY(event_id, user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 16
PROPERTIES (
    "replication_num" = "3",
    "storage_format" = "V2",
    "compression" = "ZSTD"
);
```

### Aggregate Model

```sql
-- Pre-aggregate on insert
CREATE TABLE daily_metrics (
    date DATE,
    user_id BIGINT,
    event_count BIGINT SUM,
    revenue DECIMAL(18,2) SUM,
    first_event DATETIME MIN,
    last_event DATETIME MAX
)
AGGREGATE KEY(date, user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 8
PROPERTIES ("replication_num" = "3");
```

### Unique Model

```sql
-- Latest value per key (upsert)
CREATE TABLE users (
    user_id BIGINT,
    email VARCHAR(255),
    name VARCHAR(100),
    created_at DATETIME,
    updated_at DATETIME
)
UNIQUE KEY(user_id)
DISTRIBUTED BY HASH(user_id) BUCKETS 8
PROPERTIES (
    "replication_num" = "3",
    "enable_unique_key_merge_on_write" = "true"
);
```

---

## Data Loading

### Stream Load (HTTP)

```bash
curl --location-trusted -u admin:password \
    -H "label:events_20240615" \
    -H "column_separator:," \
    -H "columns: event_id, user_id, event_type, properties, created_at" \
    -T events.csv \
    http://fe:8030/api/db/events/_stream_load
```

### Routine Load (Kafka)

```sql
CREATE ROUTINE LOAD db.kafka_events ON events
COLUMNS TERMINATED BY ",",
COLUMNS(event_id, user_id, event_type, properties, created_at)
PROPERTIES (
    "desired_concurrent_number" = "3",
    "max_batch_interval" = "10",
    "max_batch_rows" = "100000"
)
FROM KAFKA (
    "kafka_broker_list" = "kafka:9092",
    "kafka_topic" = "events",
    "property.group.id" = "doris_consumer"
);

-- Check status
SHOW ROUTINE LOAD FOR kafka_events;
```

### INSERT

```sql
INSERT INTO events VALUES
    (1, 1001, 'click', '{"page": "/home"}', '2024-06-15 10:30:00'),
    (2, 1002, 'view', '{"page": "/product"}', '2024-06-15 10:31:00');

-- Insert from query
INSERT INTO daily_metrics
SELECT
    DATE(created_at),
    user_id,
    COUNT(*),
    SUM(CAST(JSON_EXTRACT(properties, '$.amount') AS DECIMAL)),
    MIN(created_at),
    MAX(created_at)
FROM events
GROUP BY DATE(created_at), user_id;
```

---

## Partitioning

### Range Partition

```sql
CREATE TABLE events (
    event_id BIGINT,
    user_id BIGINT,
    event_type VARCHAR(50),
    created_at DATETIME
)
DUPLICATE KEY(event_id)
PARTITION BY RANGE(created_at) (
    PARTITION p202401 VALUES LESS THAN ("2024-02-01"),
    PARTITION p202402 VALUES LESS THAN ("2024-03-01"),
    PARTITION p202403 VALUES LESS THAN ("2024-04-01")
)
DISTRIBUTED BY HASH(user_id) BUCKETS 16;

-- Dynamic partition
ALTER TABLE events SET (
    "dynamic_partition.enable" = "true",
    "dynamic_partition.time_unit" = "MONTH",
    "dynamic_partition.start" = "-3",
    "dynamic_partition.end" = "1",
    "dynamic_partition.prefix" = "p"
);
```

---

## Materialized Views

```sql
-- Create MV for common aggregation
CREATE MATERIALIZED VIEW mv_hourly_events AS
SELECT
    DATE_TRUNC('HOUR', created_at) AS hour,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users
FROM events
GROUP BY hour, event_type;

-- Query auto-routes to MV
SELECT event_type, SUM(event_count)
FROM events
WHERE created_at >= '2024-06-01'
GROUP BY event_type;
-- Uses mv_hourly_events
```

---

## Connection

### MySQL Client

```bash
mysql -h fe -P 9030 -u admin -p
```

### Python

```python
import pymysql

conn = pymysql.connect(
    host='fe',
    port=9030,
    user='admin',
    password='password',
    database='db'
)

cursor = conn.cursor()
cursor.execute("SELECT * FROM events LIMIT 10")
print(cursor.fetchall())
```

---

## Monitoring

```sql
-- Cluster status
SHOW FRONTENDS;
SHOW BACKENDS;

-- Table statistics
SHOW DATA FROM events;

-- Running queries
SHOW PROCESSLIST;

-- Routine load status
SHOW ROUTINE LOAD;
```

---

## Best Practices

1. **Choose right model** - Duplicate for logs, Unique for CDC, Aggregate for metrics
2. **Use partition** - Range by time for time-series
3. **Set bucket count** - ~100MB-1GB per bucket
4. **Enable Merge-on-Write** - For Unique tables with high update rate
5. **Use materialized views** - For common aggregations
6. **Monitor routine loads** - Alert on lag/failures
