# Data Lake Architecture Patterns

## Medallion Architecture (Bronze/Silver/Gold)

The medallion architecture organizes data into three layers based on quality and refinement level.

### Bronze Layer (Raw)

- **Purpose:** Land raw data exactly as received
- **Format:** Original format or Parquet with minimal transformation
- **Schema:** Schema-on-read, append-only
- **Retention:** Long-term (years)

```sql
-- Bronze: Raw events with metadata
CREATE TABLE bronze.raw_events (
    _ingested_at TIMESTAMP DEFAULT now(),
    _source_file STRING,
    _batch_id STRING,
    raw_data STRING  -- JSON or original format
)
PARTITIONED BY (date(_ingested_at));
```

### Silver Layer (Cleaned)

- **Purpose:** Deduplicated, validated, typed data
- **Format:** Iceberg/Delta with schema enforcement
- **Schema:** Schema-on-write, strict types
- **Retention:** Medium-term (months to years)

```sql
-- Silver: Cleaned and typed
CREATE TABLE silver.events (
    event_id STRING NOT NULL,
    user_id STRING NOT NULL,
    event_type STRING,
    event_data MAP<STRING, STRING>,
    created_at TIMESTAMP,
    _processed_at TIMESTAMP
)
PARTITIONED BY (date(created_at));
```

### Gold Layer (Business-Ready)

- **Purpose:** Aggregated, business-aligned datasets
- **Format:** Optimized for query patterns
- **Schema:** Dimensional models, wide tables
- **Retention:** Based on business needs

```sql
-- Gold: Business metrics
CREATE TABLE gold.daily_user_metrics (
    date DATE,
    user_id STRING,
    total_events INT,
    unique_event_types INT,
    first_event_at TIMESTAMP,
    last_event_at TIMESTAMP
)
PARTITIONED BY (date);
```

### When to Use Medallion

- Clear data quality progression needed
- Multiple consumers with different needs
- Data lineage and audit requirements
- Gradual refinement workflow

---

## Data Mesh Architecture

Decentralized, domain-oriented data ownership with federated governance.

### Core Principles

1. **Domain Ownership:** Each domain owns its data products
2. **Data as Product:** Treat data with product thinking
3. **Self-Serve Platform:** Common infrastructure for all domains
4. **Federated Governance:** Shared standards, local implementation

### Domain Structure

```text
Domain A (Orders)
├── Source Systems
├── Domain Data Lake
│   ├── bronze/
│   ├── silver/
│   └── gold/
├── Data Products
│   ├── orders_fact
│   └── order_metrics
└── Domain Catalog Entry

Domain B (Customers)
├── Source Systems
├── Domain Data Lake
└── Data Products
    ├── customer_360
    └── customer_segments
```

### Data Product Contract

```yaml
# data_product.yaml
name: orders_fact
domain: orders
owner: orders-team@company.com
version: 2.1.0
sla:
  freshness: 1h
  availability: 99.9%
schema:
  format: iceberg
  location: s3://orders-lake/gold/orders_fact
  columns:
    - name: order_id
      type: string
      description: Unique order identifier
      pii: false
quality:
  tests:
    - unique: order_id
    - not_null: [order_id, customer_id, created_at]
    - accepted_values:
        column: status
        values: [pending, confirmed, shipped, delivered, cancelled]
```

### When to Use Data Mesh

- Large organization (100+ data practitioners)
- Multiple business domains
- Bottleneck with central data team
- Domain expertise distributed

---

## Lambda Architecture

Combines batch and real-time processing for comprehensive analytics.

### Components

```text
                    ┌─────────────────┐
                    │   Data Source   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │   Speed Layer   │           │   Batch Layer   │
    │  (Real-time)    │           │  (Historical)   │
    │                 │           │                 │
    │  Kafka → Flink  │           │  Spark → Lake   │
    └────────┬────────┘           └────────┬────────┘
             │                             │
             └──────────────┬──────────────┘
                            │
                            ▼
                  ┌─────────────────┐
                  │  Serving Layer  │
                  │  (ClickHouse)   │
                  └─────────────────┘
```

### Speed Layer (Real-time)

- Processes recent data with low latency
- Approximate results acceptable
- Overwrites when batch catches up

### Batch Layer (Accurate)

- Recomputes all data periodically
- Ground truth for historical data
- Corrects speed layer approximations

### When to Use Lambda

- Need both real-time and historical views
- Can afford complexity of two paths
- Accuracy eventually required

---

## Kappa Architecture

Simplified streaming-only architecture.

```text
                    ┌─────────────────┐
                    │   Data Source   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Kafka       │
                    │  (Event Log)    │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │     Flink       │
                    │  (Processing)   │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │    Iceberg      │
                    │  (Storage)      │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │   ClickHouse    │
                    │   (Serving)     │
                    └─────────────────┘
```

### When to Use Kappa

- Event-driven architecture
- Can reprocess from log
- Simpler operations preferred
- Streaming-first mindset

---

## Lakehouse Architecture

Combines data lake flexibility with warehouse reliability.

### Key Features

- Open table formats (Iceberg, Delta, Hudi)
- ACID transactions on data lake
- Schema enforcement and evolution
- Time travel and versioning
- Multi-engine access

### Stack Example

```text
┌─────────────────────────────────────────────┐
│            Query Engines                     │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ClickHouse│ │  Trino  │ │  Spark  │        │
│  └────┬────┘ └────┬────┘ └────┬────┘        │
│       └──────────┬┴──────────┘              │
└──────────────────┼──────────────────────────┘
                   │
┌──────────────────┼──────────────────────────┐
│       Apache Iceberg (Table Format)          │
│  ┌─────────────────────────────────────┐    │
│  │ Metadata │ Snapshots │ Manifests    │    │
│  └─────────────────────────────────────┘    │
└──────────────────┼──────────────────────────┘
                   │
┌──────────────────┼──────────────────────────┐
│         Object Storage (S3/GCS/MinIO)        │
│  ┌─────────────────────────────────────┐    │
│  │      Parquet Data Files             │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### When to Use Lakehouse

- Need warehouse features on data lake
- Multiple query engines required
- Open format lock-in prevention
- Cost optimization priority

---

## Choosing an Architecture

| Factor | Medallion | Data Mesh | Lambda | Kappa | Lakehouse |
|--------|-----------|-----------|--------|-------|-----------|
| Team size | Any | Large (100+) | Medium | Small-Medium | Any |
| Real-time needs | Low | Varies | High | High | Medium |
| Complexity | Low | High | High | Medium | Medium |
| Governance | Centralized | Federated | Centralized | Centralized | Centralized |
| Best for | Most cases | Large orgs | Mixed workloads | Event-driven | Modern default |

**Recommendation:** Start with **Medallion + Lakehouse** (Iceberg). Add Data Mesh principles as organization scales. Consider Lambda/Kappa only if real-time is critical.
