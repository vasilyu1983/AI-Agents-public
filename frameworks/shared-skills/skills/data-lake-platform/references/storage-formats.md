# Open Table Formats

Choose format, catalog, and interoperability path together.

## Table of Contents

- [Format Comparison](#format-comparison)
- [Interoperability Levers](#interoperability-levers)
- [Iceberg REST catalogs](#iceberg-rest-catalogs)
- [Apache XTable](#apache-xtable)
- [Delta UniForm](#delta-uniform)
- [Format Selection Guide](#format-selection-guide)
- [Apache Iceberg](#apache-iceberg)
- [Why It Matters](#why-it-matters)
- [Creating Tables](#creating-tables)
- [Hidden Partitioning](#hidden-partitioning)
- [Maintenance](#maintenance)
- [Branches and Tags](#branches-and-tags)
- [Delta Lake](#delta-lake)
- [Creating Tables](#creating-tables)
- [delta-rs and Polars](#delta-rs-and-polars)
- [When to Add UniForm](#when-to-add-uniform)
- [Apache Hudi](#apache-hudi)
- [Table Types](#table-types)
- [Copy-on-Write: read-heavy](#copy-on-write-read-heavy)
- [Merge-on-Read: write-heavy](#merge-on-read-write-heavy)
- [Upserts](#upserts)
- [Notes](#notes)
- [Apache Paimon](#apache-paimon)
- [Parquet Optimization](#parquet-optimization)
- [Compression](#compression)
- [Column Pruning and Pushdown](#column-pruning-and-pushdown)
- [Best Practices](#best-practices)

## Format Comparison (July 2026)

| Feature | Apache Iceberg | Delta Lake 4.3 | Apache Hudi | Apache Paimon |
|---------|----------------|----------------|-------------|---------------|
| Spec version | v2 (default); v3 GA on Snowflake/AWS, Public Preview on Databricks | Protocol v3; Liquid Clustering GA | 1.0 stable (1.1 dev, not production-ready) | 1.3.x |
| Best fit | Open multi-engine lakehouse | Databricks-centered lakehouse | CDC-heavy mutable tables | Streaming-first mutable lakehouse |
| Catalog posture | REST-first; Polaris TLP (Feb 2026); Glue, Nessie, Open Catalog | Catalog-managed tables mature since 4.1; Unity Catalog Delta APIs route all ops since 4.3 | Mixed by engine | Flink-first; expanding interop |
| Time travel | Strong | Strong | Strong | Strong |
| Branches and tags | First-class | Limited | Workflow-specific | Workflow-specific |
| Deletion vectors | GA in v3 spec (bitmap/Puffin encoding) | GA (conflict-free enablement since 4.1) | N/A (MoR log) | N/A (MoR log) |
| Upserts and deletes | Good | Good | Excellent | Excellent |
| Read interoperability | Strong; Trino v3 support experimental (no row-update/delete/OPTIMIZE on v3) | Improving via UniForm and native Flink connector (4.2+) | Improving | Growing; validate engine support |
| Default recommendation | Open analytics default | Databricks default | Mutable CDC default (Spark-heavy) | Mutable streaming default (Flink-heavy) |

Default posture:

- **Iceberg** for open, multi-engine analytics.
- **Delta** when Databricks is the center of gravity.
- **Hudi** for high-volume upserts and incremental pull patterns.
- **Paimon** for streaming-first lakehouse designs built around Flink semantics.

## Interoperability Levers

### Iceberg REST catalogs

Iceberg REST is now a practical interoperability boundary, not just a spec detail. Use it when you need one catalog contract across engines and clients.

Typical choices:

- Polaris for open self-hosted or controlled deployment
- Glue Iceberg REST for AWS-managed stacks
- Snowflake Open Catalog when Snowflake is in the operating model
- Nessie when branch/tag workflows are primary

### Apache XTable

XTable is useful when you must bridge open table formats without copying data.

Use it for:

- format migration without immediate rewrites
- mixed engine estates where format lock-in already exists
- staged interoperability experiments

Do not assume full feature parity after sync. Metadata sync does not erase format-specific behavior.

### Delta UniForm

UniForm improves external read interoperability for Delta tables. Use it when Delta remains the source of truth but outside readers must consume Iceberg-compatible metadata.

Validate carefully:

- supported engines and readers
- writer symmetry
- maintenance semantics
- governance and ACL behavior outside Databricks

## Format Selection Guide

```text
Need open multi-engine reads and long-term portability?
    -> Iceberg first

Need Databricks-native governance and operations?
    -> Delta first

Need heavy upserts, deletes, or incremental pull patterns in Spark-heavy stack?
    -> Hudi first

Need changelog-native, streaming-first table semantics in Flink-heavy stack?
    -> Paimon first

Already locked into mixed formats?
    -> Add XTable or explicit migration plan, then reduce format sprawl
```

## Apache Iceberg

Use Iceberg when portability, open catalogs, and multi-engine analytics are the primary goals.

### Why It Matters

- Branches and tags make isolated backfills, promotion, and audit snapshots easier.
- REST catalogs are broadly practical across cloud and open deployments.
- The v3 spec extends capabilities with row lineage, binary deletion vectors, and more advanced type and metadata support.

### Creating Tables

```sql
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
```

### Hidden Partitioning

```sql
CREATE TABLE events (
    event_id STRING,
    created_at TIMESTAMP
)
PARTITIONED BY (
    days(created_at),
    bucket(16, event_id)
);

SELECT *
FROM events
WHERE created_at > '2024-01-01';
```

### Maintenance

```sql
CALL catalog.system.expire_snapshots('db.events', TIMESTAMP '2024-01-01');
CALL catalog.system.remove_orphan_files('db.events');
CALL catalog.system.rewrite_data_files('db.events');
CALL catalog.system.rewrite_manifests('db.events');
```

### Branches and Tags

Use branches for isolated backfills, QA, and promotion. Use tags for durable audit points and release markers. Validate exact syntax in the active engine because DDL differs by implementation.

## Delta Lake

Use Delta when Databricks is the control plane or when Delta-native operations and governance matter more than open-engine neutrality.

### Creating Tables

```python
from delta import DeltaTable
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
    .getOrCreate()

df.write.format("delta") \
    .partitionBy("date") \
    .save("s3://bucket/delta/events")
```

### delta-rs and Polars

```python
from deltalake import DeltaTable, write_deltalake
import polars as pl

df = pl.DataFrame({"id": [1, 2], "value": ["a", "b"]})
write_deltalake("./delta_table", df, mode="append")

dt = DeltaTable("./delta_table")
df = pl.read_delta("./delta_table")
```

### When to Add UniForm

Add UniForm when external readers need Iceberg-compatible metadata over Delta-managed data. Keep Delta as the source of truth and test each reader explicitly before promising portability.

## Apache Hudi

Use Hudi when high write rates, CDC, and mutable-table semantics dominate the design.

### Table Types

```python
# Copy-on-Write: read-heavy
hudi_options = {
    'hoodie.table.type': 'COPY_ON_WRITE',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.partitionpath.field': 'date',
    'hoodie.datasource.write.precombine.field': 'updated_at'
}

# Merge-on-Read: write-heavy
hudi_options = {
    'hoodie.table.type': 'MERGE_ON_READ',
    'hoodie.datasource.write.recordkey.field': 'event_id',
    'hoodie.datasource.write.partitionpath.field': 'date',
    'hoodie.datasource.write.precombine.field': 'updated_at'
}
```

### Upserts

```python
df.write.format("hudi") \
    .options(**hudi_options) \
    .option("hoodie.datasource.write.operation", "upsert") \
    .mode("append") \
    .save("s3://bucket/hudi/events")
```

### Notes

- Hudi remains strong for high-throughput upsert and delete paths.
- Validate index and compaction behavior per engine before claiming broad interoperability.
- Use explicit maintenance windows and retention rules; MoR tradeoffs do not disappear on their own.

## Apache Paimon

Use Paimon when the lakehouse is streaming-first, Flink-native, and mutation-heavy.

Good fit:

- changelog-rich pipelines
- primary-key tables with continuous updates
- Flink-centric compute and table services

Watch-outs:

- validate engine support outside the Flink-centered stack
- do not assume identical semantics to Iceberg or Hudi
- keep interoperability tests explicit if Trino, Spark, or external readers are required

## Parquet Optimization

Parquet still matters because every table format eventually writes files.

### Compression

```python
df.write.parquet(
    "output.parquet",
    compression="zstd",
    compression_level=3
)
```

### Column Pruning and Pushdown

```python
df = spark.read.parquet("data.parquet").select("id", "name")
```

```sql
SELECT *
FROM read_parquet('data.parquet')
WHERE date >= '2024-01-01';
```

## DuckLake v1.0 (GA April 13 2026)

DuckLake is a production-ready lakehouse format from DuckDB Labs that stores all metadata in a SQL database (catalog) rather than file-based catalogs. Available as a DuckDB core extension (v1.5.2+); top-10 DuckDB extension by download count as of April 2026.

**Supported catalogs**: SQLite (single-process), PostgreSQL (multi-instance multiplayer), DuckDB.

**Clients available**: DuckDB (reference), Apache Spark, Trino, Apache DataFusion, Pandas.

**Key features**: Iceberg-compatible deletion vectors, sorted tables, bucket partitioning, data inlining, geometry support.

```sql
-- Install and attach a PostgreSQL-backed DuckLake:
INSTALL ducklake; LOAD ducklake;
ATTACH 'ducklake:postgres:dbname=catalog host=localhost' AS lake;
CREATE TABLE lake.events (id BIGINT, ts TIMESTAMP, event_type VARCHAR);
```

**Choose DuckLake when**:
- DuckDB is the primary or only query engine
- Small team, operational simplicity matters more than multi-engine support
- Multi-instance coordination via PostgreSQL catalog is acceptable
- No Spark/Flink concurrent write access required

**Do not choose DuckLake when**:
- Multiple engines (Spark, Flink, Trino) need concurrent read/write access by design
- Standardized open catalog contract (Iceberg REST) is required
- Future engine portability is a non-negotiable hard requirement

In those cases, Iceberg v2 + REST catalog (Polaris or Glue) is the correct default.

## Iceberg v3 spec (July 2026 status)

Iceberg v3 is GA on Snowflake (May 7 2026) and on AWS (S3 Tables, Glue Data Catalog, EMR, rolled out from Nov 2025). On **Databricks it is Public Preview** (announced Apr 9 2026, Databricks Runtime 18.0+ with Unity Catalog) — do not call it GA on Databricks. On Trino, v3 support is experimental in the connector's own docs: base reads/writes work but row-level updates, deletes, and `OPTIMIZE` on v3 tables are not supported; Starburst's Trino-based product has broader v3 coverage than open-source Trino.

Key v3 additions:
- **Deletion vectors**: bitmap stored in Puffin files, one bit per row. Replaces positional and equality delete files. AWS reports ~55% faster delete operations and ~74% smaller delete file sizes vs v2 in its own benchmark (verify against current AWS docs before quoting for another cloud or dataset shape).
- **Row lineage**: track row provenance across operations.
- **Type system extensions**: stricter nullability, new type support.

Production upgrade checklist:
- [ ] Confirm the exact status per engine — GA, public preview, and "experimental" are not interchangeable; check each vendor's current release notes, not a blog summary
- [ ] Confirm all engines that write to the table support v3 (Trino: experimental, no row-level update/delete/OPTIMIZE on v3 as of July 2026)
- [ ] Confirm all engines that read the table support v3 delete file formats
- [ ] Validate existing schema against v3 nullability and type rules before enabling
- [ ] Use `format-version=2` default in new tables until full engine support is confirmed
- [ ] Read the [official Iceberg v3 spec](https://iceberg.apache.org/spec/) for canonical details

## Best Practices

1. Choose format and catalog together; the format alone is not the control plane.
2. Keep Iceberg as the open default unless there is a stronger platform-specific reason.
3. Use Delta when Databricks-native governance and operations are decisive.
4. Use Hudi or Paimon when mutation and streaming semantics dominate.
5. Test real interoperability before advertising multi-engine support.
6. Compact, expire snapshots, and enforce retention on a schedule.
7. Use ZSTD-compressed Parquet unless a specific workload proves otherwise.
