---
name: data-lake-platform
description: "Universal data lake and lakehouse patterns covering ingestion (dlt, Airbyte), transformation (SQLMesh, dbt), storage formats (Iceberg, Delta, Hudi, Parquet), query engines (ClickHouse, DuckDB, Doris, StarRocks), streaming (Kafka, Flink), orchestration (Dagster, Airflow, Prefect), and visualization (Metabase, Superset, Grafana). Self-hosted and cloud options."
---

# Data Lake Platform — Quick Reference

Build production data lakes and lakehouses: ingest from any source, transform with SQL, store in open formats, query at scale.

---

## When to Use This Skill

- Design data lake/lakehouse architecture (medallion, data mesh, lambda/kappa)
- Set up data ingestion pipelines (dlt, Airbyte)
- Build SQL transformation layers (SQLMesh, dbt)
- Choose and configure table formats (Iceberg, Delta Lake, Hudi)
- Deploy analytical query engines (ClickHouse, DuckDB, Doris, StarRocks)
- Implement streaming pipelines (Kafka, Flink, Spark Streaming)
- Set up orchestration (Dagster, Airflow, Prefect)
- Implement data quality and governance (Great Expectations, DataHub)
- Optimize storage costs and query performance
- Migrate from legacy warehouse to lakehouse

---

## Quick Reference

| Layer | Tools | Templates | When to Use |
|-------|-------|-----------|-------------|
| **Ingestion** | dlt, Airbyte | `assets/ingestion/` | Extract from APIs, databases, files |
| **Transformation** | SQLMesh, dbt | `assets/transformation/` | SQL-based data modeling |
| **Storage** | Iceberg, Delta, Hudi | `assets/storage/` | Open table formats with ACID |
| **Query Engines** | ClickHouse, DuckDB, Doris | `assets/query-engines/` | Fast analytical queries |
| **Streaming** | Kafka, Flink, Spark | `assets/streaming/` | Real-time data pipelines |
| **Orchestration** | Dagster, Airflow, Prefect | `assets/orchestration/` | Pipeline scheduling |
| **Cloud** | Snowflake, BigQuery, Redshift | `assets/cloud/` | Managed warehouses |
| **Visualization** | Metabase, Superset, Grafana | `assets/visualization/` | Dashboards, BI, monitoring |
| **Observability** | Monte Carlo, Datafold, Great Expectations | `references/operational-playbook.md` | Data quality monitoring, anomaly detection |

---

## Decision Tree: Choosing Your Stack

```text
Data Lake Architecture?
    ├─ Self-hosted priority?
    │   ├─ OLAP queries? → ClickHouse (vector search, lazy materialization in 2025)
    │   ├─ Embedded analytics? → DuckDB (in-process, no server)
    │   ├─ Complex joins + updates? → Apache Doris or StarRocks
    │   └─ Data lakehouse? → Iceberg + Trino/Spark
    │
    ├─ Cloud-native?
    │   ├─ AWS? → Redshift, Athena + Iceberg
    │   ├─ GCP? → BigQuery
    │   ├─ Multi-cloud? → Snowflake
    │   └─ Federated queries? → Lakehouse Federation (query BigQuery, Oracle without copying)
    │
    ├─ Ingestion tool?
    │   ├─ Python-first, simple? → dlt (5,000+ sources, AI-assisted creation)
    │   ├─ GUI, many connectors? → Airbyte
    │   └─ Enterprise, CDC? → Debezium, Fivetran
    │
    ├─ Transformation tool?
    │   ├─ SQL-first, CI/CD? → SQLMesh (9× faster, plan/apply workflow)
    │   ├─ Large community? → dbt (Fusion engine: 30× faster parsing)
    │   └─ Python transformations? → Pandas + Great Expectations
    │
    ├─ Table format?
    │   ├─ Multi-engine reads? → Apache Iceberg (de facto standard)
    │   ├─ Databricks ecosystem? → Delta Lake
    │   ├─ CDC, real-time updates? → Apache Hudi (now supports Iceberg output)
    │   └─ Cross-format interop? → Apache XTable (Iceberg ↔ Delta ↔ Hudi)
    │
    ├─ Streaming? (45%+ of new workloads are real-time)
    │   ├─ Event streaming? → Apache Kafka
    │   ├─ Stream processing? → Apache Flink
    │   └─ Batch + streaming? → Spark Streaming
    │
    └─ Orchestration?
        ├─ Data-aware, modern? → Dagster (recommended)
        ├─ Mature, many integrations? → Airflow
        └─ Python-native, simple? → Prefect
```

---

## Architecture Patterns

### Pattern 1: Medallion Architecture (Bronze/Silver/Gold)

**Use when:** Building enterprise data lake with clear data quality tiers.

```text
Sources → Bronze (raw) → Silver (cleaned) → Gold (business-ready)
            ↓              ↓                  ↓
         Iceberg        Iceberg            Iceberg
         append-only    deduped            aggregated
```

**Tools:** dlt → SQLMesh → ClickHouse/DuckDB → Metabase

See `assets/cross-platform/template-medallion-architecture.md`

### Pattern 2: Data Mesh (Domain-Oriented)

**Use when:** Large organization, multiple domains, decentralized ownership.

```text
Domain A ──→ Domain A Lake ──→ Data Products
Domain B ──→ Domain B Lake ──→ Data Products
Domain C ──→ Domain C Lake ──→ Data Products
                   ↓
            Federated Catalog (DataHub/OpenMetadata)
```

**Tools:** dlt (per domain) → SQLMesh → Iceberg → DataHub

See `references/architecture-patterns.md`

### Pattern 3: Lambda/Kappa (Streaming + Batch)

**Use when:** Real-time + historical analytics required.

```text
Lambda: Kafka → Flink (speed layer) ───→ Serving
                   ↓                        ↑
        Batch (Spark) → Iceberg ───────────┘

Kappa:  Kafka → Flink → Iceberg → Serving (single path)
```

**Tools:** Kafka → Flink → Iceberg → ClickHouse

See `references/streaming-patterns.md`

---

## Core Capabilities

### Quick Selection Guide

| Need | Recommended Tool | Alternative |
|------|------------------|-------------|
| **Ingest from APIs** | dlt | Airbyte |
| **Ingest with CDC** | Debezium | Airbyte CDC |
| **Transform SQL** | SQLMesh | dbt |
| **Store data** | Apache Iceberg | Delta Lake |
| **Query PB-scale** | ClickHouse | Doris/StarRocks |
| **Query local** | DuckDB | Polars |
| **Stream events** | Kafka | Redpanda |
| **Process streams** | Flink | Spark Streaming |
| **Orchestrate** | Dagster | Airflow |
| **Visualize (business)** | Metabase | Superset |
| **Observe data** | Monte Carlo | Elementary |

### 1. Data Ingestion (dlt, Airbyte)

Extract data from any source: REST APIs, databases, files, SaaS platforms.

| Tool | Sources | Setup | Best For |
|------|---------|-------|----------|
| **dlt** | 5,000+ | `pip install dlt` | Python teams, AI-assisted development |
| **Airbyte** | 300+ | Docker/K8s | GUI preference, enterprise CDC |

**dlt (Python-native, recommended):**

- 5,000+ sources (growing via AI-assisted creation)
- Incremental loading, schema evolution, data contracts
- AI-assisted: works with Cursor, Claude, Codex
- Destinations: ClickHouse, DuckDB, Snowflake, BigQuery, Postgres

**Airbyte (GUI, connectors):**

- 300+ pre-built connectors with low-code CDK
- Self-hosted or cloud, CDC replication
- Declarative YAML configuration

See `assets/ingestion/dlt/` and `assets/ingestion/airbyte/`

### 2. SQL Transformation (SQLMesh, dbt)

Build data models with SQL, manage dependencies, test data quality.

| Tool | Speed | Workflow | Best For |
|------|-------|----------|----------|
| **SQLMesh** | 9× faster | Plan/apply (Terraform-like) | New projects, CI/CD-heavy |
| **dbt** | Fusion: 30× faster parsing | Direct run | Existing ecosystems, semantic layer |

**SQLMesh (recommended for new projects):**

- Virtual data environments (no clones needed)
- Automatic change detection, plan/apply workflow
- Built-in unit testing, SQLGlot parsing
- 9× faster execution, 136× faster rollbacks (Databricks benchmark)

**dbt (for existing ecosystems):**

- Large community, extensive packages
- Semantic layer for LLM-based querying
- Fusion engine: 30× faster parsing (Rust rewrite)
- dbt Cloud for managed experience

See `assets/transformation/sqlmesh/` and `assets/transformation/dbt/`

### 3. Open Table Formats (Iceberg, Delta, Hudi)

Store data in open formats with ACID transactions, time travel, schema evolution.

| Format | Best For | Multi-Engine | 2025 Status |
|--------|----------|--------------|-------------|
| **Iceberg** | General use | Excellent | De facto standard |
| **Delta** | Databricks | Good (improving) | Z-ordering, change feed |
| **Hudi** | CDC/upserts | Good | Now outputs Iceberg format |
| **XTable** | Interop | N/A | Cross-format metadata sync |

**Apache Iceberg (de facto standard):**

- Multi-engine: Spark, Trino, Flink, ClickHouse, Snowflake
- Hidden partitioning, snapshot isolation
- Industry momentum (Snowflake, Databricks, AWS adopt)

**Delta Lake:**

- Databricks native, Z-ordering optimization
- Change data feed, improving multi-engine support

**Apache Hudi:**

- Optimized for CDC/updates, record-level indexing
- **2025:** Now supports native Iceberg format output

**Apache XTable (interoperability):**

- Write once, read in any format
- Metadata sync: Iceberg ↔ Delta ↔ Hudi

See `assets/storage/`

### 4. Query Engines (ClickHouse, DuckDB, Doris, StarRocks)

Fast analytical queries on large datasets.

| Engine | Scale | Deployment | 2025 Highlights |
|--------|-------|------------|-----------------|
| **ClickHouse** | PB+ | Server/Cloud | Vector search, lazy materialization, join reordering |
| **DuckDB** | GB-TB | In-process | Iceberg support, Python-native |
| **Doris/StarRocks** | PB+ | Distributed | Complex joins, real-time updates |

**ClickHouse (2025 features):**

- Vector search (25.8), full-text search (25.9+)
- Join reordering: 1,450× faster multi-table queries
- Lazy materialization: deferred column reads
- Native Iceberg/Delta Lake integration

**DuckDB (embedded):**

- In-process, no server required
- Parquet/CSV/Iceberg native reads
- Python/R integration, laptop-scale analytics

**Apache Doris / StarRocks:**

- MPP architecture, MySQL protocol
- Complex joins, real-time updates
- Iceberg/Hudi/Delta catalog integration

See `assets/query-engines/`

### 5. Streaming (Kafka, Flink, Spark)

Real-time data pipelines and stream processing. **45%+ of new data engineering workloads are now real-time.**

| Tool | Processing | Latency | Best For |
|------|------------|---------|----------|
| **Kafka** | Event streaming | ms | Event backbone, CDC |
| **Flink** | True streaming | ms | Complex event processing |
| **Spark Streaming** | Micro-batch | seconds | Batch + stream unified |

**Apache Kafka:**

- Event streaming platform, durable log storage
- Connect ecosystem for CDC and integrations
- Foundation for event-driven architectures

**Apache Flink:**

- True stream processing, exactly-once semantics
- Stateful computations, complex event processing
- Low-latency for fraud detection, real-time analytics

**Spark Streaming:**

- Micro-batch processing (seconds latency)
- Unified batch + stream API
- ML integration, familiar Spark ecosystem

See `assets/streaming/`

### 6. Orchestration (Dagster, Airflow, Prefect)

Schedule and monitor data pipelines.

| Tool | Paradigm | Best For | Learning Curve |
|------|----------|----------|----------------|
| **Dagster** | Software-defined assets | New projects, data-aware | Medium |
| **Airflow** | Task-based DAGs | Enterprise, many integrations | High |
| **Prefect** | Python-native | Simple deployments | Low |

**Dagster (recommended for new projects):**

- Software-defined assets, data-aware scheduling
- Built-in observability and type system
- Modern developer experience

**Airflow:**

- Mature, battle-tested, large community
- Many operators and integrations
- De facto standard in enterprise

**Prefect:**

- Python-native, minimal boilerplate
- Hybrid execution model
- Simple deployment and debugging

See `assets/orchestration/`

### 7. Visualization (Metabase, Superset, Grafana)

Business intelligence dashboards and operational monitoring.

**Metabase (business users):**

- Intuitive question builder
- Self-serve analytics
- Signed embedding
- Caching and permissions

**Apache Superset (analysts):**

- SQL Lab for exploration
- Advanced visualizations
- Row-level security
- Custom chart plugins

**Grafana (infrastructure):**

- Time-series dashboards
- Real-time alerting
- Prometheus/InfluxDB native
- Data pipeline monitoring

See `assets/visualization/` and `references/bi-visualization-patterns.md`

### 8. Data Observability (Monte Carlo, Datafold, Great Expectations)

Monitor data health, detect anomalies, and ensure pipeline reliability.

**Why Observability Matters (2026):**

- 60% of data management tasks will be automated by 2027 (Gartner)
- Traditional monitoring only alerts on known issues
- Modern observability uses AI/ML to detect anomalies and predict failures

**Key Capabilities:**

- **Freshness monitoring** — Detect late-arriving or stale data
- **Volume monitoring** — Track row counts and data growth patterns
- **Schema change detection** — Alert on unexpected column changes
- **Distribution monitoring** — Detect data drift and outliers
- **Lineage-aware alerting** — Understand downstream impact of issues

**Tool Landscape:**

| Tool | Type | Best For |
|------|------|----------|
| Monte Carlo | Commercial | Full-stack observability, enterprise |
| Datafold | Commercial | Data diffing, CI/CD integration |
| Great Expectations | Open source | Data validation, testing |
| Elementary | Open source | dbt-native observability |
| Soda | Open/Commercial | Data quality checks, contracts |

See `references/operational-playbook.md`

---

## Navigation

### Resources (Deep Guides)

| Resource | Description |
|----------|-------------|
| [architecture-patterns.md](references/architecture-patterns.md) | Medallion, data mesh, lakehouse design |
| [ingestion-patterns.md](references/ingestion-patterns.md) | dlt vs Airbyte, CDC, incremental loading |
| [transformation-patterns.md](references/transformation-patterns.md) | SQLMesh vs dbt, testing, CI/CD |
| [storage-formats.md](references/storage-formats.md) | Iceberg vs Delta vs Hudi comparison |
| [query-engine-patterns.md](references/query-engine-patterns.md) | ClickHouse, DuckDB, Doris optimization |
| [streaming-patterns.md](references/streaming-patterns.md) | Kafka, Flink, Spark Streaming |
| [orchestration-patterns.md](references/orchestration-patterns.md) | Dagster, Airflow, Prefect comparison |
| [governance-catalog.md](references/governance-catalog.md) | DataHub, OpenMetadata, lineage |
| [cost-optimization.md](references/cost-optimization.md) | Storage, compute, query optimization |
| [operational-playbook.md](references/operational-playbook.md) | Monitoring, incidents, migrations |
| [bi-visualization-patterns.md](references/bi-visualization-patterns.md) | Metabase, Superset, Grafana operations |

### Templates (Copy-Paste Ready)

| Category | Templates |
|----------|-----------|
| **Cross-platform** | medallion, pipeline, incremental, quality, schema, partitioning, cost, migration |
| **Ingestion/dlt** | pipeline, rest-api, database-source, incremental, warehouse-loading |
| **Ingestion/Airbyte** | connection, custom-connector |
| **Transformation/SQLMesh** | project, model, incremental, dag, testing, production, security |
| **Transformation/dbt** | project, incremental, testing |
| **Storage** | iceberg-table, iceberg-maintenance, delta-table, hudi-table, parquet-optimization |
| **Query Engines** | clickhouse (setup, ingestion, optimization, materialized-views, replication), duckdb, doris, starrocks |
| **Streaming** | kafka-ingestion, flink-processing, spark-streaming |
| **Orchestration** | dagster-pipeline, airflow-dag, prefect-flow |
| **Cloud** | snowflake-setup, bigquery-setup, redshift-setup |
| **Visualization** | metabase (connection-checklist, dashboard-request, incident-playbook) |

---

## Data Quality & Governance

**[assets/cross-platform/template-ingestion-governance-checklist.md](assets/cross-platform/template-ingestion-governance-checklist.md)** — Intake checklist for new datasets (contracts, access control, operability, cost).

**[assets/cross-platform/template-data-quality-backfill-runbook.md](assets/cross-platform/template-data-quality-backfill-runbook.md)** — Runbook for data incidents, backfills, and safe reprocessing.

**[assets/cross-platform/template-data-quality-governance.md](assets/cross-platform/template-data-quality-governance.md)** — Comprehensive checklist for production data platforms.

### Key Sections

- **Data Quality Contracts** — Schema, freshness SLAs, volume bounds, uniqueness
- **Governance & Access Control** — RBAC, row/column security, classification
- **Security** — Encryption at rest/transit, network isolation, audit trails
- **Reliability** — Backfill procedures, idempotency patterns, reprocessing
- **Cost Control** — Storage optimization, compute governance, monitoring

### Do / Avoid

#### GOOD: Do

- Define data contracts before building pipelines
- Implement quality gates at each tier (Bronze → Silver → Gold)
- Use idempotent operations for all transformations
- Enable audit logging from day one
- Plan for backfills in pipeline design
- Document SLAs for every critical table

#### BAD: Avoid

- Skipping data quality validation to "move fast"
- Storing PII without classification and access controls
- Creating pipelines that can't be re-run safely
- Using shared service accounts without audit trails
- Ignoring cost controls until the bill arrives
- Manual schema changes without version control

### Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| **Schema on read only** | Quality issues discovered too late | Add schema validation at Bronze layer |
| **No freshness SLA** | Stale data used in decisions | Define and monitor freshness contracts |
| **Single partition strategy** | Query costs explode | Partition by most common filter column |
| **Unversioned schemas** | Breaking changes surprise consumers | Use schema registry + contracts |
| **No data owner** | Accountability vacuum | Assign owner to every dataset |

---

## Optional: AI/Automation

> **Note**: These are enhancements, not requirements. Implement only after core governance is solid.

- **Automated Quality Monitoring** — Anomaly detection on volumes and distributions
- **AI-Assisted Governance** — Auto-classification of PII columns, metadata enrichment
- **Bounded Claims** — AI detection should supplement, not replace, explicit rules; human review required for PII classification

---

## Related Skills

- **[ai-mlops](../ai-mlops/SKILL.md)** — ML deployment, drift detection, model registry
- **[ai-ml-data-science](../ai-ml-data-science/SKILL.md)** — Feature engineering, ML modeling, EDA
- **[data-sql-optimization](../data-sql-optimization/SKILL.md)** — OLTP database optimization (PostgreSQL, MySQL, Oracle)
- **[ops-devops-platform](../ops-devops-platform/SKILL.md)** — Infrastructure, CI/CD, Kubernetes

---

## Quick Start Examples

### Example 1: dlt + ClickHouse + Metabase

```bash
# Install dlt with ClickHouse
pip install "dlt[clickhouse]"

# Initialize pipeline
dlt init rest_api clickhouse

# Configure and run
python pipeline.py
```

### Example 2: SQLMesh + DuckDB (Local Development)

```bash
# Install SQLMesh
pip install sqlmesh

# Initialize project
sqlmesh init duckdb

# Plan and apply
sqlmesh plan
sqlmesh run
```

### Example 3: Dagster + dlt + SQLMesh

```python
# dagster_pipeline.py
from dagster import asset, Definitions
import dlt
import sqlmesh

@asset
def raw_data():
    pipeline = dlt.pipeline("my_pipeline", destination="duckdb")
    return pipeline.run(source_data())

@asset(deps=[raw_data])
def transformed_data():
    ctx = sqlmesh.Context()
    ctx.run()
```

---

## Sources

See [data/sources.json](data/sources.json) for 100+ curated sources covering:
- Official documentation (dlt, SQLMesh, ClickHouse, Iceberg, etc.)
- Architecture guides (medallion, data mesh)
- Comparison articles (2024-2025 benchmarks)
- Community resources (Discord, Stack Overflow)
- Russian ecosystem (Yandex DataLens, Arenadata, Altinity)

---

## Trend Awareness Protocol

**IMPORTANT**: When users ask recommendation questions about data lakes, lakehouses, or data platforms, you MUST use WebSearch to check current trends before answering.

### Trigger Conditions

- "What's the best tool for [data lake/lakehouse/data platform]?"
- "What should I use for [ingestion/transformation/query engine]?"
- "What's the latest in data engineering?"
- "Current best practices for [Iceberg/dbt/ClickHouse]?"
- "Is [tool/approach] still relevant in 2026?"
- "[Iceberg] vs [Delta Lake] vs [Hudi]?"
- "Best orchestration tool for [data pipelines]?"

### Required Searches

1. Search: `"data lakehouse best practices 2026"`
2. Search: `"[Iceberg/ClickHouse/dbt] vs alternatives 2026"`
3. Search: `"data engineering trends January 2026"`
4. Search: `"[specific tool] new releases 2026"`

### What to Report

After searching, provide:

- **Current landscape**: What data tools/patterns are popular NOW
- **Emerging trends**: New tools, formats, or patterns gaining traction
- **Deprecated/declining**: Tools/approaches losing relevance or support
- **Recommendation**: Based on fresh data, not just static knowledge

### Example Topics (verify with fresh search)

- Table formats (Iceberg, Delta Lake, Hudi, Paimon)
- Query engines (ClickHouse, DuckDB, Doris, StarRocks)
- Transformation tools (dbt, SQLMesh, SQLGlot)
- Ingestion tools (dlt, Airbyte, Fivetran)
- Orchestration (Dagster, Airflow, Prefect)
- Streaming (Kafka, Flink, Spark Streaming)
- Data governance and catalogs (DataHub, OpenMetadata)
