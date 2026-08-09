# Apache Hudi Table Template

## Overview

Creating and managing Apache Hudi tables for incremental data processing.

## Table Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Copy on Write (COW)** | Updates rewrite entire file | Read-heavy, batch updates |
| **Merge on Read (MOR)** | Updates written to delta logs | Write-heavy, real-time |

---

## Table Creation

### Copy on Write (COW)

```sql
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    properties STRING,
    created_at TIMESTAMP,
    _hoodie_commit_time STRING,
    _hoodie_commit_seqno STRING,
    _hoodie_record_key STRING,
    _hoodie_partition_path STRING,
    _hoodie_file_name STRING
)
USING hudi
TBLPROPERTIES (
    'type' = 'cow',
    'primaryKey' = 'event_id',
    'preCombineField' = 'created_at'
)
PARTITIONED BY (year, month)
LOCATION 's3://bucket/events';
```

### Merge on Read (MOR)

```sql
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    properties STRING,
    created_at TIMESTAMP
)
USING hudi
TBLPROPERTIES (
    'type' = 'mor',
    'primaryKey' = 'event_id',
    'preCombineField' = 'created_at',
    'hoodie.compaction.strategy' = 'org.apache.hudi.table.action.compact.strategy.LogFileSizeBasedCompactionStrategy',
    'hoodie.compact.inline.max.delta.commits' = '5'
)
PARTITIONED BY (year, month);
```

### PySpark

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .appName("Hudi") \
    .config("spark.serializer", "org.apache.spark.serializer.KryoSerializer") \
    .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.hudi.catalog.HoodieCatalog") \
    .getOrCreate()

# Write options
hudi_options = {
    'hoodie.table.name': 'events',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.precombine.field': 'created_at',
    'hoodie.datasource.write.operation': 'upsert',
    'hoodie.datasource.write.table.type': 'COPY_ON_WRITE',
    'hoodie.upsert.shuffle.parallelism': 200,
    'hoodie.insert.shuffle.parallelism': 200
}

df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save("s3://bucket/events")
```

---

## Write Operations

### Insert

```python
hudi_options = {
    'hoodie.datasource.write.operation': 'insert',
    'hoodie.table.name': 'events',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.precombine.field': 'created_at'
}

df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save("s3://bucket/events")
```

### Upsert

```python
hudi_options = {
    'hoodie.datasource.write.operation': 'upsert',  # Default
    'hoodie.table.name': 'events',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.precombine.field': 'created_at'
}

df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save("s3://bucket/events")
```

### Delete

```python
# Hard delete
hudi_options = {
    'hoodie.datasource.write.operation': 'delete',
    'hoodie.table.name': 'events',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.partitionpath.field': 'year,month',
    'hoodie.datasource.write.precombine.field': 'created_at'
}

# DataFrame with records to delete (only keys needed)
delete_df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("append") \
    .save("s3://bucket/events")
```

### Bulk Insert (Initial Load)

```python
hudi_options = {
    'hoodie.datasource.write.operation': 'bulk_insert',
    'hoodie.bulkinsert.shuffle.parallelism': 200,
    'hoodie.datasource.write.row.writer.enable': 'true'
}

df.write.format("hudi") \
    .options(**hudi_options) \
    .mode("overwrite") \
    .save("s3://bucket/events")
```

---

## Read Operations

### Snapshot Query

```python
# Read latest snapshot
df = spark.read.format("hudi").load("s3://bucket/events")

# SQL
spark.sql("SELECT * FROM events")
```

### Incremental Query

```python
# Read changes since commit
df = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "incremental") \
    .option("hoodie.datasource.read.begin.instanttime", "20240601000000") \
    .load("s3://bucket/events")

# Between two commits
df = spark.read.format("hudi") \
    .option("hoodie.datasource.query.type", "incremental") \
    .option("hoodie.datasource.read.begin.instanttime", "20240601000000") \
    .option("hoodie.datasource.read.end.instanttime", "20240615000000") \
    .load("s3://bucket/events")
```

### Time Travel

```python
# Read as of specific time
df = spark.read.format("hudi") \
    .option("as.of.instant", "20240601000000") \
    .load("s3://bucket/events")
```

---

## MOR Compaction

### Inline Compaction

```python
hudi_options = {
    'hoodie.compact.inline': 'true',
    'hoodie.compact.inline.max.delta.commits': '5'
}
```

### Schedule Compaction

```python
from hudi import HoodieWriteClient

# Schedule compaction
client = HoodieWriteClient(spark, config)
compaction_instant = client.scheduleCompaction(None)

# Execute compaction
client.compact(compaction_instant)
```

### Async Compaction

```python
hudi_options = {
    'hoodie.compact.inline': 'false',
    'hoodie.compaction.async.enabled': 'true'
}
```

---

## Clustering

### Enable Clustering

```python
hudi_options = {
    'hoodie.clustering.inline': 'true',
    'hoodie.clustering.inline.max.commits': '4',
    'hoodie.clustering.plan.strategy.target.file.max.bytes': '1073741824',  # 1GB
    'hoodie.clustering.plan.strategy.sort.columns': 'user_id,created_at'
}
```

### Z-Order Clustering

```python
hudi_options = {
    'hoodie.clustering.plan.strategy.class':
        'org.apache.hudi.client.clustering.plan.strategy.SparkSizeBasedClusteringPlanStrategy',
    'hoodie.layout.optimize.strategy': 'z-order',
    'hoodie.layout.optimize.columns': 'user_id,event_type'
}
```

---

## Maintenance

### Clean Old Files

```python
# Auto-clean (default enabled)
hudi_options = {
    'hoodie.clean.automatic': 'true',
    'hoodie.cleaner.commits.retained': '10',
    'hoodie.cleaner.policy': 'KEEP_LATEST_COMMITS'
}

# Manual clean
from hudi import HoodieWriteClient
client = HoodieWriteClient(spark, config)
client.clean()
```

### Rollback

```python
# Rollback to specific instant
client.rollback("20240601000000")

# Restore to savepoint
client.restoreToSavepoint("savepoint_20240601")
```

---

## Table Properties

| Property | Default | Description |
|----------|---------|-------------|
| `hoodie.table.type` | COPY_ON_WRITE | COW or MOR |
| `hoodie.datasource.write.operation` | upsert | insert, upsert, bulk_insert, delete |
| `hoodie.datasource.write.recordkey.field` | uuid | Primary key column |
| `hoodie.datasource.write.precombine.field` | ts | Deduplication field |
| `hoodie.compact.inline` | false | Enable inline compaction |
| `hoodie.cleaner.commits.retained` | 10 | Commits to retain |
| `hoodie.index.type` | BLOOM | BLOOM, SIMPLE, GLOBAL_BLOOM |

---

## Best Practices

1. **Choose COW for read-heavy** workloads (analytics)
2. **Choose MOR for write-heavy** workloads (streaming)
3. **Set appropriate parallelism** for your cluster
4. **Use BLOOM index** for large tables
5. **Enable clustering** for query performance
6. **Configure compaction** based on write frequency
7. **Monitor timeline** for commit health
