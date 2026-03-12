# Open Table Formats

## Format Comparison

| Feature | Apache Iceberg | Delta Lake | Apache Hudi |
|---------|---------------|------------|-------------|
| ACID + time travel | Yes | Yes | Yes |
| Schema + partition evolution | Strong (hidden partitions) | Strong (best in Databricks) | Strong (best for CDC-heavy writes) |
| Multi-engine reads | Strong | Improving | Improving |
| Upserts/deletes (CDC) | Good | Good | Excellent |
| Ecosystem fit | Open lakehouse | Databricks-first | Ingest/CDC-first |

Default choice: Iceberg for multi-engine lakehouses. Choose Delta when you are Databricks-centered. Choose Hudi when you need high-volume upserts/deletes and CDC-driven ingestion semantics.

Interoperability is improving (for example, Hudi can emit Iceberg-compatible tables; Apache XTable can sync metadata between formats), but validate feature parity for your engines before committing.

---

## Apache XTable (Cross-Format Interoperability)

Apache XTable (incubating) enables seamless interoperability between Iceberg, Delta Lake, and Hudi. Co-launched by Microsoft, Google, and Onehouse, donated to ASF.

### Why XTable Matters

- **No format lock-in** — Write in one format, read in any other
- **Gradual migration** — Move between formats without rewrites
- **Best-of-breed** — Use Hudi for writes, Iceberg for reads

### How It Works

```bash
# XTable syncs metadata between formats (no data copy)
java -jar xtable-utilities.jar \
  --sourceFormat HUDI \
  --targetFormats ICEBERG,DELTA \
  --dataset s3://bucket/hudi/events
```

### Use Cases

| Scenario | Solution |
|----------|----------|
| Spark writes, Trino reads | Write Delta -> XTable -> Read Iceberg |
| CDC with Hudi, analytics with Iceberg | Write Hudi -> XTable -> Query Iceberg |
| Multi-engine lakehouse | Single source -> XTable -> All formats |

### Limitations

- Metadata sync only (no data transformation)
- Some features don't translate (e.g., Hudi's record-level indexing)
- Requires periodic sync runs

See [Apache XTable Documentation](https://xtable.apache.org/)

---

## Apache Iceberg

### Creating Tables

```sql
-- Spark SQL
CREATE TABLE catalog.db.events (
    event_id STRING,
    user_id BIGINT,
    event_type STRING,
    created_at TIMESTAMP
)
USING iceberg
PARTITIONED BY (days(created_at))
TBLPROPERTIES (
    'write.format.default' = 'parquet',
    'write.parquet.compression-codec' = 'zstd'
);

-- PyIceberg
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import StringType, LongType, TimestampType

catalog = load_catalog("rest", uri="http://localhost:8181")

schema = Schema(
    NestedField(1, "event_id", StringType(), required=True),
    NestedField(2, "user_id", LongType(), required=True),
    NestedField(3, "event_type", StringType()),
    NestedField(4, "created_at", TimestampType())
)

catalog.create_table("db.events", schema=schema)
```

### Hidden Partitioning

```sql
-- Iceberg derives partition from column (no partition column in queries)
CREATE TABLE events (
    event_id STRING,
    created_at TIMESTAMP
)
PARTITIONED BY (
    days(created_at),     -- Daily partition
    bucket(16, event_id)  -- Hash bucket
);

-- Query without knowing partition structure
SELECT * FROM events WHERE created_at > '2024-01-01';
-- Iceberg automatically prunes partitions
```

### Schema Evolution

```sql
-- Add column
ALTER TABLE events ADD COLUMN user_agent STRING;

-- Rename column
ALTER TABLE events RENAME COLUMN user_agent TO browser;

-- Widen type
ALTER TABLE events ALTER COLUMN user_id TYPE BIGINT;

-- Reorder columns
ALTER TABLE events ALTER COLUMN browser AFTER event_type;
```

### Time Travel

```sql
-- Query specific snapshot
SELECT * FROM events VERSION AS OF 123456789;

-- Query by timestamp
SELECT * FROM events TIMESTAMP AS OF '2024-01-01 00:00:00';

-- Rollback to snapshot
CALL catalog.system.rollback_to_snapshot('db.events', 123456789);
```

### Maintenance

```sql
-- Expire old snapshots (keep 7 days)
CALL catalog.system.expire_snapshots('db.events', TIMESTAMP '2024-01-01');

-- Remove orphan files
CALL catalog.system.remove_orphan_files('db.events');

-- Rewrite data files (compaction)
CALL catalog.system.rewrite_data_files('db.events');

-- Rewrite manifests
CALL catalog.system.rewrite_manifests('db.events');
```

---

## Delta Lake

### Creating Tables

```python
from delta import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .getOrCreate()

# Create table
df.write.format("delta") \
    .partitionBy("date") \
    .save("s3://bucket/delta/events")

# Create with SQL
spark.sql("""
CREATE TABLE events (
    event_id STRING,
    user_id BIGINT,
    created_at TIMESTAMP
)
USING delta
PARTITIONED BY (date(created_at))
LOCATION 's3://bucket/delta/events'
""")
```

### delta-rs (Python without Spark)

```python
from deltalake import DeltaTable, write_deltalake
import polars as pl

# Write Polars DataFrame
df = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
write_deltalake("./delta_table", df, mode="append")

# Read
dt = DeltaTable("./delta_table")
df = pl.read_delta("./delta_table")

# Merge/Upsert
dt.merge(
    source=updates_df,
    predicate="target.id = source.id",
    source_alias="source",
    target_alias="target"
).when_matched_update_all().when_not_matched_insert_all().execute()
```

### Z-Ordering (Optimize for Queries)

```sql
-- Optimize with Z-order
OPTIMIZE events ZORDER BY (user_id, event_type);

-- Vacuum old files
VACUUM events RETAIN 168 HOURS;
```

---

## Apache Hudi

Hudi can emit Iceberg-compatible tables in some configurations. Validate supported features for your engine mix (Spark/Flink/Trino, catalog type, maintenance operations).

### Table Types

```python
# Copy-on-Write (CoW): Best for read-heavy
hudi_options = {
    'hoodie.table.type': 'COPY_ON_WRITE',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.partitionpath.field': 'date',
    'hoodie.datasource.write.precombine.field': 'updated_at'
}

# Merge-on-Read (MoR): Best for write-heavy/CDC
hudi_options = {
    'hoodie.table.type': 'MERGE_ON_READ',
    ...
}
```

### Native Iceberg Output

```python
# Create Iceberg-compatible tables using Hudi
hudi_options = {
    'hoodie.table.type': 'COPY_ON_WRITE',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.table.format': 'ICEBERG',  # Output Iceberg format
    ...
}
```

### Upsert Operations

```python
df.write.format("hudi") \
    .options(**hudi_options) \
    .option("hoodie.datasource.write.operation", "upsert") \
    .mode("append") \
    .save("s3://bucket/hudi/events")
```

---

## Parquet Optimization

### Compression

```python
# Best compression: ZSTD
df.write.parquet(
    "output.parquet",
    compression="zstd",
    compression_level=3
)

# Row group size (default 128MB, tune for query patterns)
spark.conf.set("parquet.block.size", 134217728)  # 128MB
```

### Column Pruning

```python
# Only read needed columns
df = spark.read.parquet("data.parquet").select("id", "name")

# With PyArrow
import pyarrow.parquet as pq
table = pq.read_table("data.parquet", columns=["id", "name"])
```

### Predicate Pushdown

```python
# Filters pushed to Parquet reader
df = spark.read.parquet("data.parquet") \
    .filter("date >= '2024-01-01'")

# With DuckDB
duckdb.query("""
    SELECT * FROM read_parquet('data.parquet')
    WHERE date >= '2024-01-01'
""")
```

---

## Best Practices

1. **Use Iceberg** for multi-engine access and ClickHouse integration
2. **Use Hudi** for heavy CDC/upsert workloads
3. **Use Delta** in Databricks ecosystem
4. **Partition by time** (daily/hourly) for time-series
5. **Compact regularly** to optimize read performance
6. **Set retention policies** to manage storage costs
7. **Use ZSTD compression** for best size/speed tradeoff
