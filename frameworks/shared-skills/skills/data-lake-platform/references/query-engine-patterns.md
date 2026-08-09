# Query Engine Patterns

Choose query engines based on access pattern, concurrency, and interoperability with the table catalog.

## Table of Contents

- [Lake Query vs Serving Store](#lake-query-vs-serving-store)
- [Engine Comparison](#engine-comparison)
- [Decision Guide](#decision-guide)
- [Trino Patterns](#trino-patterns)
- [Iceberg and Lakehouse Querying](#iceberg-and-lakehouse-querying)
- [Catalog Guidance](#catalog-guidance)
- [Spark Patterns](#spark-patterns)
- [DuckDB Patterns](#duckdb-patterns)
- [Parquet and Iceberg Reads](#parquet-and-iceberg-reads)
- [Where DuckDB Fits](#where-duckdb-fits)
- [ClickHouse Patterns](#clickhouse-patterns)
- [Table Engine Selection](#table-engine-selection)
- [Materialized Views](#materialized-views)
- [Operational Guidance](#operational-guidance)
- [StarRocks and Doris](#starrocks-and-doris)
- [StarRocks External Catalog](#starrocks-external-catalog)
- [Doris Real-Time Ingestion](#doris-real-time-ingestion)
- [Best Practices](#best-practices)

## Lake Query vs Serving Store

- **Lake query engines** such as Trino and Spark are best for open table formats, large joins, and federated access.
- **Serving engines** such as ClickHouse, StarRocks, and Doris are best for high-concurrency dashboards and sub-second analytics.
- **Embedded engines** such as DuckDB are best for local analysis, CI, notebooks, workstation analytics, and some edge workloads.

## Engine Comparison

| Engine | Best for | Typical deployment | Watch-outs |
|--------|----------|--------------------|-----------|
| Trino | Open lakehouse SQL, federated queries, catalog-driven analytics | Cluster or managed service | Needs explicit catalog and connector discipline |
| Spark | Heavy transforms, ML, batch and streaming compute | Cluster | Operationally heavier for interactive analytics |
| DuckDB | Local, embedded, workstation, CI, edge, and lightweight app analytics | In-process | Not a cluster serving layer |
| ClickHouse | Low-latency serving and high-QPS dashboards | Cluster or cloud | Model tables for access patterns, not generic OLTP habits |
| StarRocks | External lake queries plus serving acceleration | Cluster or cloud | Tune refresh, materialization, and external catalog behavior |
| Doris | Real-time ingestion and MPP serving | Cluster | Strong serving story, weaker open-engine neutrality than lake query engines |

## Decision Guide

```text
Need open lakehouse SQL across Iceberg, Hudi, Delta, or federated sources?
    -> Trino first

Need large batch compute, feature builds, or streaming transforms?
    -> Spark first

Need analyst-local or embedded app analytics over Parquet or Iceberg?
    -> DuckDB first

Need sub-second dashboards or embedded customer-facing analytics?
    -> ClickHouse or StarRocks

Need to keep lake as source of truth but accelerate hot queries?
    -> Serving layer downstream from the lake, not instead of it
```

## Trino Patterns

Use Trino as the default open lake query layer when you want SQL over Iceberg and other systems without locking into one vendor compute plane.

### Iceberg and Lakehouse Querying

```sql
SELECT *
FROM iceberg.analytics.events
WHERE event_date >= DATE '2024-01-01';
```

### Catalog Guidance

Prefer explicit catalog design:

- Iceberg + REST, Glue, Polaris, Nessie, or Open Catalog for open tables
- Lakehouse connector when you need one connector to access Iceberg, Delta Lake, and Hudi through a shared metastore model
- Separate catalogs by environment and trust boundary

## Spark Patterns

Use Spark when transforms and compute intensity dominate.

Good fit:

- feature engineering and ML-heavy joins
- large batch transforms
- structured streaming tied closely to the write path

Do not default to Spark for every BI query if Trino or a serving layer fits better.

## DuckDB Patterns

DuckDB is no longer just a notebook toy. Treat it as the default embedded analytics engine for local analysis, test harnesses, analyst workstations, and some application-side OLAP.

### Parquet and Iceberg Reads

```python
import duckdb

con = duckdb.connect("analytics.duckdb")

df = con.execute("""
    SELECT
        date_trunc('day', created_at) AS date,
        event_type,
        count(*) AS events
    FROM read_parquet('s3://bucket/events/*.parquet')
    WHERE created_at >= '2024-01-01'
    GROUP BY 1, 2
""").df()

con.execute("INSTALL iceberg; LOAD iceberg;")
df = con.execute("""
    SELECT *
    FROM iceberg_scan('s3://bucket/iceberg/events')
    WHERE created_at >= '2024-01-01'
""").df()
```

### Where DuckDB Fits

- local validation of lakehouse tables
- reproducible analyst workflows
- CI checks against Parquet or Iceberg snapshots
- embedded app analytics where cluster overhead is unjustified

Validate current catalog and cloud integrations from the active docs before recommending specific REST or managed-catalog flows.

## ClickHouse Patterns

Use ClickHouse when serving performance matters more than open-engine neutrality.

### Table Engine Selection

```sql
CREATE TABLE events (
    event_id UUID,
    user_id UInt64,
    event_type LowCardinality(String),
    event_data String,
    created_at DateTime
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(created_at)
ORDER BY (user_id, created_at)
SETTINGS index_granularity = 8192;
```

### Materialized Views

```sql
CREATE MATERIALIZED VIEW hourly_stats
ENGINE = SummingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (hour, event_type)
AS SELECT
    toStartOfHour(created_at) AS hour,
    event_type,
    count() AS event_count,
    uniq(user_id) AS unique_users
FROM raw_events
GROUP BY hour, event_type;
```

### Operational Guidance

- model `ORDER BY` around real filters and joins
- use `FINAL` sparingly
- pre-aggregate where dashboard SLAs demand it
- keep the lake or raw ingest log as source of truth for reprocessing

## StarRocks and Doris

Use these when you want serving acceleration over lake data with stronger native MPP behavior than a general lake query layer.

### StarRocks External Catalog

```sql
CREATE EXTERNAL CATALOG iceberg_catalog
PROPERTIES (
    "type" = "iceberg",
    "iceberg.catalog.type" = "rest",
    "iceberg.catalog.uri" = "http://rest-catalog:8181"
);
```

### Doris Real-Time Ingestion

```sql
CREATE ROUTINE LOAD db.kafka_load ON events
COLUMNS TERMINATED BY ",",
COLUMNS(event_id, user_id, event_type, created_at)
FROM KAFKA (
    "kafka_broker_list" = "kafka:9092",
    "kafka_topic" = "events",
    "property.group.id" = "doris_consumer"
);
```

## Best Practices

1. Keep the lakehouse source of truth separate from the serving-optimized read model when workloads diverge.
2. Choose query engines by concurrency, latency, and governance boundary, not by habit.
3. Treat catalog compatibility as part of engine selection.
4. Use DuckDB aggressively for local and CI validation, but not as a generic cluster replacement.
5. Add serving engines only when the lake query layer cannot meet the workload economically.
