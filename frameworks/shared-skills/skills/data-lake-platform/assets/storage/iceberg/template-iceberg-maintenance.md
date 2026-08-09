# Apache Iceberg Maintenance Template

## Overview

Maintenance operations for optimizing Iceberg table performance and storage.

## Maintenance Operations

| Operation | Purpose | Frequency |
|-----------|---------|-----------|
| **Compaction** | Merge small files | Daily/Weekly |
| **Expire Snapshots** | Remove old metadata | Weekly |
| **Remove Orphan Files** | Delete unused files | Weekly |
| **Rewrite Manifests** | Optimize manifest files | Monthly |
| **Delete Orphan Metadata** | Clean metadata files | Monthly |

---

## File Compaction

### Rewrite Data Files

```sql
-- Spark SQL procedure
CALL catalog.system.rewrite_data_files(
    table => 'db.events',
    options => map(
        'target-file-size-bytes', '134217728',  -- 128 MB
        'min-input-files', '5',
        'max-concurrent-file-group-rewrites', '4'
    )
);

-- With partition filter (faster)
CALL catalog.system.rewrite_data_files(
    table => 'db.events',
    where => 'created_at_month = "2024-06"'
);

-- Using bin-packing strategy
CALL catalog.system.rewrite_data_files(
    table => 'db.events',
    strategy => 'binpack',
    options => map(
        'target-file-size-bytes', '134217728',
        'min-file-size-bytes', '104857600',
        'max-file-size-bytes', '178257920'
    )
);

-- Using sort strategy (better for query performance)
CALL catalog.system.rewrite_data_files(
    table => 'db.events',
    strategy => 'sort',
    sort_order => 'user_id ASC, created_at DESC',
    options => map('target-file-size-bytes', '134217728')
);
```

### PyIceberg Compaction

```python
from pyiceberg.catalog import load_catalog

catalog = load_catalog("rest")
table = catalog.load_table("db.events")

# Get current file stats
scan = table.scan()
files = list(scan.plan_files())
print(f"Current files: {len(files)}")
print(f"Total size: {sum(f.file.file_size_in_bytes for f in files) / 1e9:.2f} GB")

# Compact (via Spark)
# PyIceberg doesn't have built-in compaction yet
# Use Spark or Trino procedures
```

---

## Snapshot Management

### Expire Old Snapshots

```sql
-- Expire snapshots older than timestamp
CALL catalog.system.expire_snapshots(
    table => 'db.events',
    older_than => TIMESTAMP '2024-06-01 00:00:00',
    retain_last => 10,  -- Keep at least 10 snapshots
    max_concurrent_deletes => 4
);

-- Expire by age (milliseconds)
CALL catalog.system.expire_snapshots(
    table => 'db.events',
    max_snapshot_age_ms => 604800000  -- 7 days
);
```

### View Snapshot History

```sql
-- List all snapshots
SELECT
    committed_at,
    snapshot_id,
    parent_id,
    operation,
    summary['added-data-files'] AS added_files,
    summary['deleted-data-files'] AS deleted_files
FROM catalog.db.events.snapshots
ORDER BY committed_at DESC;

-- Current snapshot
SELECT * FROM catalog.db.events.refs
WHERE type = 'BRANCH' AND name = 'main';
```

---

## Orphan File Cleanup

### Remove Orphan Files

```sql
-- Remove files not referenced by any snapshot
CALL catalog.system.remove_orphan_files(
    table => 'db.events',
    older_than => TIMESTAMP '2024-06-01 00:00:00',
    dry_run => true  -- Preview first
);

-- Execute removal
CALL catalog.system.remove_orphan_files(
    table => 'db.events',
    older_than => TIMESTAMP '2024-06-01 00:00:00',
    dry_run => false
);

-- With location override
CALL catalog.system.remove_orphan_files(
    table => 'db.events',
    location => 's3://bucket/db/events/data',
    older_than => TIMESTAMP '2024-06-01 00:00:00'
);
```

### Delete Orphan Metadata

```sql
-- Clean up metadata files
CALL catalog.system.delete_orphan_files(
    table => 'db.events',
    location => 's3://bucket/db/events/metadata',
    older_than => TIMESTAMP '2024-06-01 00:00:00'
);
```

---

## Manifest Optimization

### Rewrite Manifests

```sql
-- Optimize manifest files for better read performance
CALL catalog.system.rewrite_manifests(
    table => 'db.events',
    use_caching => true
);

-- Rewrite with specific settings
CALL catalog.system.rewrite_manifests(
    table => 'db.events',
    spec_id => 0  -- Current partition spec
);
```

### Check Manifest Stats

```sql
-- Manifest file statistics
SELECT
    length AS manifest_length,
    partition_spec_id,
    added_snapshot_id,
    added_data_files_count,
    existing_data_files_count,
    deleted_data_files_count
FROM catalog.db.events.manifests;

-- Data files per manifest
SELECT
    path,
    partition,
    file_size_in_bytes,
    record_count
FROM catalog.db.events.files;
```

---

## Automated Maintenance

### Dagster Pipeline

```python
from dagster import asset, schedule, ScheduleDefinition
from pyspark.sql import SparkSession

@asset(group_name="maintenance")
def compact_events():
    """Compact small files in events table."""
    spark = SparkSession.builder.getOrCreate()

    spark.sql("""
        CALL catalog.system.rewrite_data_files(
            table => 'db.events',
            where => 'created_at_month = date_format(current_date() - INTERVAL 1 DAY, "yyyy-MM")',
            options => map('target-file-size-bytes', '134217728')
        )
    """)

@asset(group_name="maintenance")
def expire_snapshots():
    """Expire old snapshots."""
    spark = SparkSession.builder.getOrCreate()

    spark.sql("""
        CALL catalog.system.expire_snapshots(
            table => 'db.events',
            older_than => current_timestamp() - INTERVAL 7 DAYS,
            retain_last => 10
        )
    """)

@asset(group_name="maintenance")
def remove_orphans():
    """Remove orphan files."""
    spark = SparkSession.builder.getOrCreate()

    spark.sql("""
        CALL catalog.system.remove_orphan_files(
            table => 'db.events',
            older_than => current_timestamp() - INTERVAL 3 DAYS
        )
    """)

# Weekly schedule
maintenance_schedule = ScheduleDefinition(
    job=define_asset_job("maintenance_job", selection="*"),
    cron_schedule="0 2 * * 0"  # Sunday 2 AM
)
```

### Shell Script

```bash
#!/bin/bash
# iceberg_maintenance.sh

SPARK_SUBMIT="spark-submit --master yarn"
CATALOG="catalog"
DATABASE="db"
TABLE="events"

# Compact files
echo "Compacting files..."
$SPARK_SUBMIT --class org.apache.iceberg.spark.actions.RewriteDataFilesAction \
    --conf spark.sql.catalog.$CATALOG=org.apache.iceberg.spark.SparkCatalog \
    iceberg-spark-runtime.jar \
    --table $CATALOG.$DATABASE.$TABLE \
    --target-file-size-bytes 134217728

# Expire snapshots
echo "Expiring snapshots..."
$SPARK_SUBMIT -e "
    CALL $CATALOG.system.expire_snapshots(
        table => '$DATABASE.$TABLE',
        older_than => current_timestamp() - INTERVAL 7 DAYS,
        retain_last => 10
    )
"

# Remove orphan files
echo "Removing orphan files..."
$SPARK_SUBMIT -e "
    CALL $CATALOG.system.remove_orphan_files(
        table => '$DATABASE.$TABLE',
        older_than => current_timestamp() - INTERVAL 3 DAYS
    )
"

echo "Maintenance complete"
```

---

## Monitoring

### Table Health Metrics

```sql
-- File statistics
SELECT
    'data_files' AS metric,
    count(*) AS count,
    sum(file_size_in_bytes) / 1e9 AS total_gb,
    avg(file_size_in_bytes) / 1e6 AS avg_mb,
    min(file_size_in_bytes) / 1e6 AS min_mb,
    max(file_size_in_bytes) / 1e6 AS max_mb
FROM catalog.db.events.files;

-- Small files (need compaction)
SELECT count(*) AS small_files
FROM catalog.db.events.files
WHERE file_size_in_bytes < 104857600;  -- < 100 MB

-- Snapshot count
SELECT count(*) AS snapshot_count
FROM catalog.db.events.snapshots;

-- Partition statistics
SELECT
    partition,
    count(*) AS files,
    sum(record_count) AS records,
    sum(file_size_in_bytes) / 1e9 AS size_gb
FROM catalog.db.events.files
GROUP BY partition
ORDER BY size_gb DESC;
```

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| Small files (< 100MB) | > 100 | > 500 | Compact |
| Snapshot count | > 50 | > 100 | Expire |
| Avg file size | < 50MB | < 10MB | Compact |
| Total files | > 10k | > 50k | Compact |

---

## Best Practices

1. **Compact after bulk loads** - Run compaction after large INSERT operations
2. **Expire snapshots weekly** - Keep 7-14 days of snapshots
3. **Remove orphans with delay** - Wait 3+ days before removing
4. **Monitor file counts** - Alert on too many small files
5. **Schedule maintenance** - Off-peak hours, weekly minimum
6. **Test before automation** - Run with dry_run first
