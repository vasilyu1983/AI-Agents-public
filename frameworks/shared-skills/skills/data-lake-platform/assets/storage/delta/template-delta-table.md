# Delta Lake Table Template

## Overview

Creating and managing Delta Lake tables for ACID transactions on data lakes.

## Table Creation

### Spark SQL

```sql
-- Create Delta table
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    properties STRING,
    created_at TIMESTAMP
)
USING DELTA
PARTITIONED BY (year INT, month INT)
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- With generated columns
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    created_at TIMESTAMP,
    year INT GENERATED ALWAYS AS (YEAR(created_at)),
    month INT GENERATED ALWAYS AS (MONTH(created_at))
)
USING DELTA
PARTITIONED BY (year, month);
```

### PySpark

```python
from delta import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("DeltaLake") \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
    .getOrCreate()

# Create table from DataFrame
df = spark.createDataFrame([
    ("evt_001", 1001, "click", "2024-06-15 10:30:00"),
    ("evt_002", 1002, "view", "2024-06-15 10:31:00")
], ["event_id", "user_id", "event_type", "created_at"])

df.write.format("delta") \
    .partitionBy("year", "month") \
    .option("delta.autoOptimize.optimizeWrite", "true") \
    .save("s3://bucket/events")
```

---

## Data Operations

### Insert

```sql
-- Append data
INSERT INTO events VALUES
    ('evt_003', 1003, 'purchase', '{"amount": 99.99}', TIMESTAMP '2024-06-15 10:32:00');

-- Insert overwrite (replace partition)
INSERT OVERWRITE events
PARTITION (year = 2024, month = 6)
SELECT * FROM staging.events WHERE year = 2024 AND month = 6;
```

### Merge (Upsert)

```sql
MERGE INTO events t
USING updates s
ON t.event_id = s.event_id
WHEN MATCHED THEN
    UPDATE SET *
WHEN NOT MATCHED THEN
    INSERT *;

-- With conditions
MERGE INTO events t
USING updates s
ON t.event_id = s.event_id
WHEN MATCHED AND s.event_type = 'delete' THEN
    DELETE
WHEN MATCHED THEN
    UPDATE SET
        event_type = s.event_type,
        properties = s.properties
WHEN NOT MATCHED THEN
    INSERT (event_id, user_id, event_type, properties, created_at)
    VALUES (s.event_id, s.user_id, s.event_type, s.properties, s.created_at);
```

### Update

```sql
UPDATE events
SET event_type = 'conversion'
WHERE event_id = 'evt_001';
```

### Delete

```sql
DELETE FROM events
WHERE created_at < '2023-01-01';

-- Delete by partition (faster)
DELETE FROM events
WHERE year = 2023 AND month = 1;
```

---

## Time Travel

### Query Historical Data

```sql
-- By version
SELECT * FROM events VERSION AS OF 5;

-- By timestamp
SELECT * FROM events TIMESTAMP AS OF '2024-06-01 00:00:00';

-- Using @ syntax
SELECT * FROM events@v5;
SELECT * FROM events@20240601000000;
```

### View History

```sql
DESCRIBE HISTORY events;

-- With limit
DESCRIBE HISTORY events LIMIT 10;
```

### Restore

```sql
-- Restore to version
RESTORE TABLE events TO VERSION AS OF 5;

-- Restore to timestamp
RESTORE TABLE events TO TIMESTAMP AS OF '2024-06-01 00:00:00';
```

---

## Schema Evolution

### Enable Column Mapping (Required for rename/drop)

```sql
ALTER TABLE events SET TBLPROPERTIES (
    'delta.columnMapping.mode' = 'name',
    'delta.minReaderVersion' = '2',
    'delta.minWriterVersion' = '5'
);
```

### Add Column

```sql
ALTER TABLE events ADD COLUMN browser_info STRING AFTER user_id;
```

### Rename Column

```sql
-- Requires column mapping enabled
ALTER TABLE events RENAME COLUMN browser_info TO browser;
```

### Drop Column

```sql
-- Requires column mapping enabled
ALTER TABLE events DROP COLUMN deprecated_field;
```

### Change Type

```sql
-- Only widening allowed
ALTER TABLE events ALTER COLUMN user_id TYPE BIGINT;
```

---

## Optimization

### OPTIMIZE (Compaction)

```sql
-- Compact all files
OPTIMIZE events;

-- Compact specific partition
OPTIMIZE events WHERE year = 2024 AND month = 6;

-- With Z-ORDER clustering
OPTIMIZE events ZORDER BY (user_id, event_type);
```

### Liquid Clustering (Delta 3.0+)

```sql
-- Create with clustering
CREATE TABLE events (...)
USING DELTA
CLUSTER BY (user_id, event_type);

-- Enable on existing table
ALTER TABLE events CLUSTER BY (user_id, event_type);

-- Trigger clustering
OPTIMIZE events;
```

### Auto-Optimization

```sql
-- Enable auto-optimize
ALTER TABLE events SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

---

## Maintenance

### Vacuum (Remove Old Files)

```sql
-- Dry run (see what would be deleted)
VACUUM events DRY RUN;

-- Delete files older than 7 days (default)
VACUUM events;

-- Delete files older than custom retention
VACUUM events RETAIN 168 HOURS;  -- 7 days

-- Override safety check (dangerous!)
SET spark.databricks.delta.retentionDurationCheck.enabled = false;
VACUUM events RETAIN 0 HOURS;
```

### Table Properties

```sql
-- Set retention
ALTER TABLE events SET TBLPROPERTIES (
    'delta.logRetentionDuration' = 'interval 30 days',
    'delta.deletedFileRetentionDuration' = 'interval 7 days'
);

-- View properties
SHOW TBLPROPERTIES events;
```

---

## Table Properties Reference

| Property | Default | Description |
|----------|---------|-------------|
| `delta.autoOptimize.optimizeWrite` | false | Auto-optimize writes |
| `delta.autoOptimize.autoCompact` | false | Auto-compaction |
| `delta.logRetentionDuration` | 30 days | Transaction log retention |
| `delta.deletedFileRetentionDuration` | 7 days | Vacuum threshold |
| `delta.columnMapping.mode` | none | Enable `name` for schema evolution |
| `delta.minReaderVersion` | 1 | Minimum reader version |
| `delta.minWriterVersion` | 2 | Minimum writer version |

---

## Query Integration

### DuckDB

```sql
-- Query Delta table
SELECT * FROM delta_scan('s3://bucket/events');

-- With options
SELECT * FROM delta_scan('s3://bucket/events', version=5);
```

### Spark

```python
# Read Delta table
df = spark.read.format("delta").load("s3://bucket/events")

# With version
df = spark.read.format("delta").option("versionAsOf", 5).load("s3://bucket/events")

# With timestamp
df = spark.read.format("delta").option("timestampAsOf", "2024-06-01").load("s3://bucket/events")
```

### delta-rs (Python)

```python
from deltalake import DeltaTable

# Load table
dt = DeltaTable("s3://bucket/events")

# Query as PyArrow
table = dt.to_pyarrow_table()

# Query specific version
dt = DeltaTable("s3://bucket/events", version=5)
```

---

## Best Practices

1. **Use auto-optimize** for most workloads
2. **Enable column mapping** for schema flexibility
3. **OPTIMIZE with Z-ORDER** for query performance
4. **Set appropriate retention** based on compliance needs
5. **VACUUM regularly** to reclaim storage
6. **Use partitioning wisely** - avoid over-partitioning
