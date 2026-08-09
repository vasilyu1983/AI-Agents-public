# Apache Iceberg Table Template

## Overview

Creating and managing Apache Iceberg tables for data lake storage.

## Table Creation

### Spark SQL

```sql
-- Create Iceberg table
CREATE TABLE catalog.db.events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    properties STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (months(created_at), bucket(16, user_id))
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd',
    'write.target-file-size-bytes' = '134217728',
    'format-version' = '2'
);
```

### PyIceberg

```python
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField, StringType, LongType, TimestampType
)
from pyiceberg.partitioning import PartitionSpec, PartitionField
from pyiceberg.transforms import MonthTransform, BucketTransform

# Connect to catalog
catalog = load_catalog("rest", uri="http://iceberg-rest:8181")

# Define schema
schema = Schema(
    NestedField(1, "event_id", StringType(), required=True),
    NestedField(2, "user_id", LongType(), required=True),
    NestedField(3, "event_type", StringType(), required=True),
    NestedField(4, "properties", StringType(), required=False),
    NestedField(5, "created_at", TimestampType(), required=True)
)

# Define partitioning
partition_spec = PartitionSpec(
    PartitionField(
        source_id=5,
        field_id=1000,
        transform=MonthTransform(),
        name="created_at_month"
    ),
    PartitionField(
        source_id=2,
        field_id=1001,
        transform=BucketTransform(num_buckets=16),
        name="user_id_bucket"
    )
)

# Create table
table = catalog.create_table(
    identifier="db.events",
    schema=schema,
    partition_spec=partition_spec,
    properties={
        "write.format.default": "parquet",
        "write.parquet.compression-codec": "zstd"
    }
)
```

---

## Partition Transforms

### Available Transforms

| Transform | Example | Use Case |
|-----------|---------|----------|
| `identity` | `region` | Exact value partitions |
| `years(ts)` | Year extraction | Yearly archives |
| `months(ts)` | Month extraction | Monthly partitions |
| `days(ts)` | Day extraction | Daily partitions |
| `hours(ts)` | Hour extraction | High-volume hourly |
| `bucket(n, col)` | Hash into n buckets | Even distribution |
| `truncate(n, col)` | First n chars/digits | Prefix grouping |

### Partition Examples

```sql
-- Time-based partitioning
PARTITIONED BY (days(created_at))

-- Time + hash for large tables
PARTITIONED BY (months(created_at), bucket(16, user_id))

-- Multiple dimensions
PARTITIONED BY (region, months(order_date))

-- String prefix (e.g., first 2 chars of country code)
PARTITIONED BY (truncate(2, country_code))
```

---

## Data Operations

### Insert Data

```python
# PyIceberg with PyArrow
import pyarrow as pa
from pyiceberg.catalog import load_catalog

catalog = load_catalog("rest")
table = catalog.load_table("db.events")

# Create Arrow table
arrow_table = pa.table({
    "event_id": ["evt_001", "evt_002"],
    "user_id": [1001, 1002],
    "event_type": ["click", "view"],
    "properties": ['{"page": "/home"}', '{"page": "/product"}'],
    "created_at": [
        pa.scalar("2024-06-15 10:30:00").cast(pa.timestamp("us")),
        pa.scalar("2024-06-15 10:31:00").cast(pa.timestamp("us"))
    ]
})

# Append data
table.append(arrow_table)
```

```sql
-- Spark SQL insert
INSERT INTO catalog.db.events VALUES
    ('evt_001', 1001, 'click', '{"page": "/home"}', TIMESTAMP '2024-06-15 10:30:00'),
    ('evt_002', 1002, 'view', '{"page": "/product"}', TIMESTAMP '2024-06-15 10:31:00');

-- Insert from query
INSERT INTO catalog.db.events
SELECT * FROM staging.raw_events
WHERE created_at >= '2024-06-01';
```

### Merge (Upsert)

```sql
-- MERGE INTO for upserts
MERGE INTO catalog.db.events t
USING staging.new_events s
ON t.event_id = s.event_id
WHEN MATCHED THEN
    UPDATE SET *
WHEN NOT MATCHED THEN
    INSERT *;
```

### Delete

```sql
-- Delete specific rows
DELETE FROM catalog.db.events
WHERE created_at < '2023-01-01';

-- Delete by partition (faster)
DELETE FROM catalog.db.events
WHERE created_at_month = '2023-01';
```

### Update

```sql
-- Update specific rows
UPDATE catalog.db.events
SET event_type = 'purchase'
WHERE event_id = 'evt_001';
```

---

## Time Travel

### Query Historical Data

```sql
-- By snapshot ID
SELECT * FROM catalog.db.events VERSION AS OF 123456789;

-- By timestamp
SELECT * FROM catalog.db.events TIMESTAMP AS OF '2024-06-01 00:00:00';

-- Compare versions
SELECT * FROM catalog.db.events VERSION AS OF 123456789
EXCEPT
SELECT * FROM catalog.db.events VERSION AS OF 123456788;
```

### View Snapshots

```sql
-- List all snapshots
SELECT * FROM catalog.db.events.snapshots;

-- Snapshot details
SELECT
    snapshot_id,
    committed_at,
    operation,
    summary
FROM catalog.db.events.history;
```

### Rollback

```sql
-- Rollback to snapshot
CALL catalog.system.rollback_to_snapshot('db.events', 123456789);

-- Rollback to timestamp
CALL catalog.system.rollback_to_timestamp('db.events', TIMESTAMP '2024-06-01 00:00:00');
```

---

## Schema Evolution

### Add Column

```sql
ALTER TABLE catalog.db.events ADD COLUMN browser_info STRING;

-- With position
ALTER TABLE catalog.db.events ADD COLUMN session_id STRING AFTER user_id;
```

### Rename Column

```sql
ALTER TABLE catalog.db.events RENAME COLUMN browser_info TO browser;
```

### Change Type

```sql
-- Widen type (int → long, float → double)
ALTER TABLE catalog.db.events ALTER COLUMN user_id TYPE BIGINT;
```

### Drop Column

```sql
ALTER TABLE catalog.db.events DROP COLUMN deprecated_field;
```

### Required to Optional

```sql
ALTER TABLE catalog.db.events ALTER COLUMN properties DROP NOT NULL;
```

---

## Partition Evolution

### Add Partition Field

```sql
-- Add new partition field (no rewrite)
ALTER TABLE catalog.db.events ADD PARTITION FIELD bucket(8, event_type);
```

### Drop Partition Field

```sql
ALTER TABLE catalog.db.events DROP PARTITION FIELD months(created_at);
```

### Replace Partition

```sql
-- Change granularity
ALTER TABLE catalog.db.events REPLACE PARTITION FIELD
    months(created_at) WITH days(created_at);
```

---

## Table Properties

### Common Properties

```sql
-- Set properties
ALTER TABLE catalog.db.events SET TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd',
    'write.target-file-size-bytes' = '134217728',
    'read.split.target-size' = '134217728',
    'write.metadata.delete-after-commit.enabled' = 'true',
    'history.expire.max-snapshot-age-ms' = '604800000'
);
```

### Property Reference

| Property | Default | Description |
|----------|---------|-------------|
| `write.format.default` | parquet | File format |
| `write.parquet.compression-codec` | gzip | Compression |
| `write.target-file-size-bytes` | 512MB | Target file size |
| `read.split.target-size` | 128MB | Read split size |
| `write.metadata.delete-after-commit.enabled` | false | Auto-cleanup |

---

## Query Integration

### DuckDB

```sql
-- Install and load extension
INSTALL iceberg;
LOAD iceberg;

-- Query Iceberg table
SELECT * FROM iceberg_scan('s3://bucket/db/events');

-- With catalog
ATTACH 's3://bucket/' AS lake (TYPE iceberg);
SELECT * FROM lake.db.events;
```

### Trino

```sql
-- Catalog configuration in Trino
-- /etc/trino/catalog/iceberg.properties
-- connector.name=iceberg
-- iceberg.catalog.type=rest
-- iceberg.rest-catalog.uri=http://iceberg-rest:8181

SELECT * FROM iceberg.db.events
WHERE created_at >= TIMESTAMP '2024-01-01';
```

### ClickHouse

```sql
-- ClickHouse 23.8+ with Iceberg support
SELECT *
FROM iceberg('http://iceberg-rest:8181', 'db', 'events')
WHERE created_at >= '2024-01-01';
```

---

## Best Practices

1. **Use format version 2** - Better delete support
2. **Partition by time + hash** - Time for pruning, hash for parallelism
3. **Target 128-512 MB files** - Balance between parallelism and overhead
4. **Use ZSTD compression** - Best compression ratio for analytics
5. **Enable metadata cleanup** - Prevent metadata bloat
6. **Expire old snapshots** - After retention period
