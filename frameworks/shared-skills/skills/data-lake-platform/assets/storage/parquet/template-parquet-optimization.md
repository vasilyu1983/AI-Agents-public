# Parquet Optimization Template

## Overview

Optimizing Parquet files for query performance and storage efficiency.

## File Structure

```text
Parquet File
├── Row Group 1 (default: 128 MB)
│   ├── Column Chunk: event_id
│   │   ├── Page 1 (default: 1 MB)
│   │   ├── Page 2
│   │   └── Statistics (min, max, null_count)
│   ├── Column Chunk: user_id
│   └── Column Chunk: created_at
├── Row Group 2
└── Footer (schema, row group metadata)
```

---

## Write Optimization

### PyArrow

```python
import pyarrow as pa
import pyarrow.parquet as pq

# Optimized write settings
table = pa.table({
    "event_id": ["evt_001", "evt_002"],
    "user_id": [1001, 1002],
    "event_type": ["click", "view"],
    "created_at": pa.array([
        "2024-06-15 10:30:00",
        "2024-06-15 10:31:00"
    ]).cast(pa.timestamp("us"))
})

pq.write_table(
    table,
    "events.parquet",
    compression="zstd",
    compression_level=3,
    row_group_size=128 * 1024 * 1024,  # 128 MB
    data_page_size=1024 * 1024,  # 1 MB
    write_statistics=True,
    use_dictionary=True,
    dictionary_pagesize_limit=1024 * 1024
)
```

### Partitioned Write

```python
# Write with partitioning
pq.write_to_dataset(
    table,
    root_path="s3://bucket/events",
    partition_cols=["year", "month"],
    compression="zstd",
    existing_data_behavior="overwrite_or_ignore"
)
```

### PySpark

```python
df.write.parquet(
    "s3://bucket/events",
    mode="overwrite",
    compression="zstd",
    partitionBy=["year", "month"]
)

# With options
df.write.option("parquet.block.size", 134217728) \  # 128 MB
    .option("parquet.page.size", 1048576) \  # 1 MB
    .option("parquet.enable.dictionary", True) \
    .option("compression", "zstd") \
    .parquet("s3://bucket/events")
```

---

## Compression Comparison

| Codec | Ratio | Speed | CPU | Best For |
|-------|-------|-------|-----|----------|
| **Snappy** | ~2x | Fast | Low | Default, balanced |
| **ZSTD** | ~3-4x | Medium | Medium | Storage efficiency |
| **GZIP** | ~3x | Slow | High | Max compression |
| **LZ4** | ~2x | Very Fast | Very Low | Speed priority |
| **Uncompressed** | 1x | Fastest | None | Already compressed data |

### Recommendation

```python
# For most analytics workloads
compression = "zstd"
compression_level = 3  # Balance speed/ratio

# For real-time/streaming
compression = "snappy"

# For archival
compression = "zstd"
compression_level = 9
```

---

## Row Group Sizing

### Guidelines

| Data Volume | Row Group Size | Rationale |
|-------------|----------------|-----------|
| < 1 GB | 64-128 MB | Single file OK |
| 1-10 GB | 128 MB | Standard |
| > 10 GB | 256-512 MB | Reduce metadata |

### Configure

```python
# PyArrow
pq.write_table(table, "data.parquet", row_group_size=128 * 1024 * 1024)

# PySpark
spark.conf.set("parquet.block.size", "134217728")  # 128 MB

# DuckDB
COPY table TO 'data.parquet' (ROW_GROUP_SIZE 100000);
```

---

## Dictionary Encoding

### When to Use

- **Use**: Low cardinality columns (< 10k unique values)
- **Skip**: High cardinality columns (UUIDs, timestamps)

### Configure

```python
# PyArrow - per column control
pq.write_table(
    table,
    "data.parquet",
    use_dictionary=True,  # Enable globally
    column_encoding={
        "event_id": "PLAIN",  # Disable for high cardinality
        "event_type": "RLE_DICTIONARY",  # Enable for low cardinality
        "user_id": "DELTA_BINARY_PACKED"  # Good for sorted integers
    }
)
```

---

## Column Sorting

### Benefits

- Better compression
- Faster predicate pushdown
- More effective statistics

### Implementation

```python
# Sort before writing
df_sorted = df.sort("user_id", "created_at")
df_sorted.write.parquet("s3://bucket/events")

# Or with DuckDB
COPY (SELECT * FROM events ORDER BY user_id, created_at)
TO 'events.parquet' (FORMAT PARQUET);
```

---

## Statistics and Predicate Pushdown

### Check Statistics

```python
import pyarrow.parquet as pq

# Read metadata
parquet_file = pq.ParquetFile("data.parquet")

# File metadata
print(parquet_file.metadata)

# Row group statistics
for i in range(parquet_file.metadata.num_row_groups):
    rg = parquet_file.metadata.row_group(i)
    for j in range(rg.num_columns):
        col = rg.column(j)
        print(f"Column {col.path_in_schema}:")
        print(f"  Min: {col.statistics.min}")
        print(f"  Max: {col.statistics.max}")
        print(f"  Nulls: {col.statistics.null_count}")
```

### Optimize for Pushdown

```sql
-- DuckDB predicate pushdown
SELECT * FROM read_parquet('data.parquet')
WHERE user_id = 1001;  -- Uses row group statistics

-- Check if pushdown is working
EXPLAIN ANALYZE SELECT * FROM read_parquet('data.parquet')
WHERE user_id = 1001;
```

---

## File Compaction

### Merge Small Files

```python
import pyarrow.parquet as pq
import pyarrow.dataset as ds

# Read multiple small files
dataset = ds.dataset("s3://bucket/events/", format="parquet")

# Write as single optimized file
ds.write_dataset(
    dataset.to_batches(),
    "s3://bucket/events_compacted/",
    format="parquet",
    max_partitions=1024,
    max_open_files=100,
    max_rows_per_file=10_000_000,
    min_rows_per_group=100_000,
    max_rows_per_group=1_000_000
)
```

### DuckDB Compaction

```sql
-- Compact small files
COPY (SELECT * FROM read_parquet('input/*.parquet'))
TO 'output/compacted.parquet'
(FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000);
```

---

## Schema Design

### Nested Types

```python
# Efficient nested structure
schema = pa.schema([
    ("event_id", pa.string()),
    ("user", pa.struct([
        ("id", pa.int64()),
        ("email", pa.string()),
        ("name", pa.string())
    ])),
    ("properties", pa.map_(pa.string(), pa.string())),
    ("tags", pa.list_(pa.string()))
])
```

### Avoid

```python
# BAD: Avoid: JSON strings (can't filter/pushdown)
schema = pa.schema([
    ("properties", pa.string())  # JSON as string
])

# GOOD: Better: Structured columns
schema = pa.schema([
    ("property_key", pa.string()),
    ("property_value", pa.string())
])
```

---

## Read Optimization

### Column Projection

```python
# Only read needed columns
df = pq.read_table(
    "data.parquet",
    columns=["event_id", "user_id", "created_at"]
)

# DuckDB
SELECT event_id, user_id, created_at
FROM read_parquet('data.parquet');
```

### Row Group Filtering

```python
# Read specific row groups
pq.read_table(
    "data.parquet",
    filters=[
        ("user_id", ">=", 1000),
        ("user_id", "<", 2000)
    ]
)
```

### Parallel Read

```python
# PyArrow parallel read
pq.read_table(
    "data.parquet",
    use_threads=True,
    memory_map=True
)

# DuckDB
SET threads TO 8;
SELECT * FROM read_parquet('data.parquet');
```

---

## Best Practices

| Aspect | Recommendation |
|--------|----------------|
| **Compression** | ZSTD level 3 for most cases |
| **Row Group Size** | 128 MB |
| **Page Size** | 1 MB |
| **Dictionary** | Enable for low cardinality columns |
| **Sorting** | Sort by query filter columns |
| **Statistics** | Always enable |
| **File Size** | Target 128 MB - 1 GB per file |

---

## Monitoring

```python
# File analysis
def analyze_parquet(path):
    pf = pq.ParquetFile(path)
    meta = pf.metadata

    print(f"Rows: {meta.num_rows:,}")
    print(f"Row Groups: {meta.num_row_groups}")
    print(f"Columns: {meta.num_columns}")
    print(f"Size: {pf.metadata.serialized_size / 1e6:.2f} MB")

    # Compression ratio
    total_compressed = sum(
        meta.row_group(i).column(j).total_compressed_size
        for i in range(meta.num_row_groups)
        for j in range(meta.num_columns)
    )
    total_uncompressed = sum(
        meta.row_group(i).column(j).total_uncompressed_size
        for i in range(meta.num_row_groups)
        for j in range(meta.num_columns)
    )
    print(f"Compression ratio: {total_uncompressed / total_compressed:.2f}x")
```
