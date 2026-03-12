# StarRocks Setup Template

## Overview

Setting up StarRocks for high-performance analytics with external catalog support.

## Docker Compose

```yaml
version: '3.8'

services:
  fe:
    image: starrocks/fe-ubuntu:3.2-latest
    hostname: fe
    ports:
      - "8030:8030"   # HTTP
      - "9030:9030"   # MySQL
    volumes:
      - fe_meta:/opt/starrocks/fe/meta

  be:
    image: starrocks/be-ubuntu:3.2-latest
    hostname: be
    depends_on:
      - fe
    volumes:
      - be_storage:/opt/starrocks/be/storage
    environment:
      FE_HOST: fe

volumes:
  fe_meta:
  be_storage:
```

---

## Table Creation

### Primary Key Table (Recommended)

```sql
CREATE TABLE events (
    event_id BIGINT,
    user_id BIGINT,
    event_type VARCHAR(50),
    properties JSON,
    created_at DATETIME
)
PRIMARY KEY (event_id)
DISTRIBUTED BY HASH(event_id) BUCKETS 16
PROPERTIES (
    "replication_num" = "3",
    "enable_persistent_index" = "true"
);
```

### Duplicate Key Table

```sql
CREATE TABLE event_logs (
    event_id BIGINT,
    user_id BIGINT,
    event_type VARCHAR(50),
    created_at DATETIME
)
DUPLICATE KEY(event_id, user_id)
PARTITION BY RANGE(created_at) (
    PARTITION p202406 VALUES LESS THAN ("2024-07-01")
)
DISTRIBUTED BY HASH(user_id) BUCKETS 16;
```

---

## External Catalogs

### Iceberg Catalog

```sql
CREATE EXTERNAL CATALOG iceberg_catalog
PROPERTIES (
    "type" = "iceberg",
    "iceberg.catalog.type" = "rest",
    "iceberg.catalog.uri" = "http://iceberg-rest:8181",
    "aws.s3.access_key" = "${AWS_ACCESS_KEY}",
    "aws.s3.secret_key" = "${AWS_SECRET_KEY}",
    "aws.s3.region" = "us-east-1"
);

-- Query Iceberg table
SELECT * FROM iceberg_catalog.db.events
WHERE created_at >= '2024-01-01';
```

### Hive Catalog

```sql
CREATE EXTERNAL CATALOG hive_catalog
PROPERTIES (
    "type" = "hive",
    "hive.metastore.uris" = "thrift://hive-metastore:9083"
);
```

### Delta Lake Catalog

```sql
CREATE EXTERNAL CATALOG delta_catalog
PROPERTIES (
    "type" = "deltalake",
    "hive.metastore.uris" = "thrift://hive-metastore:9083"
);
```

---

## Materialized Views

### Async Refresh MV

```sql
-- Create MV on external data
CREATE MATERIALIZED VIEW mv_daily_events
DISTRIBUTED BY HASH(date) BUCKETS 8
REFRESH ASYNC START('2024-01-01 00:00:00') EVERY (INTERVAL 1 HOUR)
AS SELECT
    DATE(created_at) AS date,
    event_type,
    COUNT(*) AS events,
    COUNT(DISTINCT user_id) AS users
FROM iceberg_catalog.db.events
GROUP BY DATE(created_at), event_type;

-- Manual refresh
REFRESH MATERIALIZED VIEW mv_daily_events;
```

---

## Data Loading

### Stream Load

```bash
curl --location-trusted -u admin: \
    -H "label:events_load" \
    -H "column_separator:," \
    -T events.csv \
    http://fe:8030/api/db/events/_stream_load
```

### Routine Load (Kafka)

```sql
CREATE ROUTINE LOAD db.events_load ON events
COLUMNS(event_id, user_id, event_type, properties, created_at)
PROPERTIES (
    "desired_concurrent_number" = "3",
    "format" = "json",
    "jsonpaths" = "[\"$.event_id\",\"$.user_id\",\"$.event_type\",\"$.properties\",\"$.created_at\"]"
)
FROM KAFKA (
    "kafka_broker_list" = "kafka:9092",
    "kafka_topic" = "events"
);
```

---

## Query Optimization

### Query Cache

```sql
-- Enable query cache
SET enable_query_cache = true;
SET query_cache_entry_max_bytes = 1048576;
SET query_cache_entry_max_rows = 10000;
```

### Query Profile

```sql
-- Enable profiling
SET enable_profile = true;

-- View profile
SHOW PROFILELIST;
ANALYZE PROFILE FROM 'profile_id';
```

---

## Best Practices

1. **Use Primary Key** - For real-time upserts
2. **External catalogs** - Query Iceberg/Delta directly
3. **Async MVs** - Pre-aggregate external data
4. **Enable query cache** - For repeated queries
5. **Use persistent index** - For Primary Key tables
