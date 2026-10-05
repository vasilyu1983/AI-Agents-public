---
name: data-lake-platform
description: "Designs lakehouse platforms across Iceberg, Delta, Hudi, and Paimon. Use when choosing catalogs, CDC paths, query engines, governance, or cost controls."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-09-25
---

# Data Lake Platform

Build and operate production data lakes and lakehouses: ingest, store in open table formats, catalog, maintain, and serve analytics reliably. Transformation (dbt/SQLMesh) and data-quality testing live in `data-analytics-engineering`; Kafka/Flink streaming lives in `data-streaming`.

## Quick Reference

| Task | Resource |
|------|----------|
| Pick a table format and spec version | [references/storage-formats.md](references/storage-formats.md) |
| Pick a catalog / control plane | [references/governance-catalog.md](references/governance-catalog.md) |
| Design a batch or CDC ingest path | [references/ingestion-patterns.md](references/ingestion-patterns.md) |
| Scaffold or inspect an Iceberg table | `scripts/scaffold_iceberg_table.py`, `scripts/inspect_iceberg_metadata.sh` |
| Check any version, spec-support, or vendor feature-status claim | [Version and support lookup](#version-and-support-lookup) |

### Quick-Start Decision Table

| Situation | Default choice |
|-----------|----------------|
| Open multi-engine analytics | Iceberg + REST catalog (Polaris/Glue/Nessie) + Trino/Spark |
| Databricks primary compute | Delta + Unity Catalog; add UniForm only if external readers exist |
| CDC-heavy mutable, Spark-centered | Hudi (CoW for read-heavy, MoR for write-heavy) + Kafka/Debezium |
| Streaming-first mutable, Flink-centered | Paimon + Flink CDC |
| Single-engine embedded / analyst workstation | DuckLake, or DuckDB + Parquet/Iceberg |
| Low-latency BI, high-concurrency dashboards | ClickHouse or StarRocks serving layer, fed from the lake |
| Heterogeneous estate (Hive + Kafka + RDBMS) | Apache Gravitino as a federated "catalog of catalogs" |

## Format Comparison

| Property | Apache Iceberg | Delta Lake | Apache Hudi | Apache Paimon |
|----------|----------------|------------|-------------|---------------|
| Spec / protocol | Format v2 is the broad-compatibility baseline; v3 support is per engine ([look up](#version-and-support-lookup)) | Protocol features gated per table (reader/writer features) | Table version per release line | Flink-first LSM table format |
| Row-level deletes | Position/equality delete files (v2); deletion vectors (v3 spec) | Deletion vectors | MoR log files | LSM merge |
| Catalog posture | REST-catalog-first | Catalog-managed tables (Unity Catalog) | Mixed | Flink catalog first |
| Branches and tags | First-class | Limited | Workflow-specific | Workflow-specific |
| Multi-engine reads | Strongest (Trino, Spark, DuckDB, Flink) | Via UniForm and native connectors | Narrower; validate | Narrower; validate |

- DuckLake keeps its catalog in a SQL database (SQLite, PostgreSQL, or DuckDB). It suits single-engine or small-team lakehouses, not concurrent Spark/Flink writers.
- Default to Iceberg format v2 when any required engine cannot yet write v3 with row-level updates, deletes, and maintenance. Choose v3 only when the proof matrix below passes for every engine.

## Decision Tree

```text
Choosing a lakehouse path:
    ├─ Databricks is the primary platform?
    │   └─ Delta + Unity Catalog; add UniForm only if external readers matter
    ├─ Need open multi-engine access across Trino/Spark/DuckDB?
    │   └─ Iceberg + Polaris / Glue REST / Nessie / Open Catalog
    │       format v2 unless every writer passes v3 row-level ops and maintenance
    ├─ Heavy CDC, mutable tables, or streaming-first semantics?
    │   ├─ Flink-native stack -> Paimon first, compare with Hudi
    │   └─ Spark-heavy stack  -> Hudi first (CoW read-heavy, MoR write-heavy)
    ├─ Single-engine embedded or analyst workstation?
    │   └─ DuckLake (PostgreSQL catalog for multi-instance) or DuckDB + Parquet
    │       name the upgrade trigger to Iceberg (2nd engine or concurrent writers)
    ├─ Low-latency dashboards or embedded analytics?
    │   ├─ High-concurrency BI, proven by load test -> add ClickHouse / StarRocks / Doris
    │   └─ Local, notebook, CI -> DuckDB + Parquet/Iceberg
    └─ Heterogeneous multi-format estate?
        └─ Gravitino federation over existing catalogs
```

## Catalog Landscape

| Catalog | Best for | Watch-outs |
|---------|----------|------------|
| Apache Polaris | Open self-hosted Iceberg control plane | Still need separate metadata/lineage tooling |
| Glue Iceberg REST + S3 Tables | AWS-native managed Iceberg | AWS-centric; managed tables run their own compaction, so do not double-schedule it |
| Snowflake Open Catalog | Snowflake-adjacent open Iceberg interop | Validate write paths and service principals |
| Project Nessie | Branch/tag promotion, isolated backfills | Narrower governance scope |
| Unity Catalog | Databricks-centered governance + compute | Cross-engine behavior must be proven |
| Apache Gravitino | Federated multi-format metadata | Validate production readiness per deployment |
| DuckLake | Single-engine or small-team SQL-native lakehouse | Not designed for concurrent Spark/Flink writes |

Feature status and IAM model for every row: [look up](#version-and-support-lookup) before recommending.

## Interoperability Proof Matrix

A platform choice is provisional until every required path has a named result for the exact workload:

| Path | Prove with |
|---|---|
| Each writer -> catalog -> table | create, append, schema evolution, concurrent commit |
| Each reader -> catalog -> table | predicate pushdown, deletes, time travel, required types |
| Operations | compaction, snapshot expiry, orphan cleanup, failed-job recovery |
| Failure and rollback | partial commit, credential outage, replay, restore to prior snapshot |

Mark each cell `pass`, `unsupported`, or `unverified`, with engine and connector versions. A spec feature or vendor GA label does not close a cell. If a required cell is unsupported, use the lowest common format version or change the architecture before production commitment.

## Version and Support Lookup

This skill carries no release numbers, GA dates, or per-engine support status on purpose; they change release to release. This is the one place that says how to look them up — other files point here.

1. **Name the claim precisely**: format and spec version (e.g. Iceberg format v3), feature (row-level update/delete, deletion vectors, row lineage, `OPTIMIZE`/compaction, Variant type), and operation (read, write, maintenance).
2. **Check each engine separately** in its own docs or release notes — for Trino, the Iceberg connector page; for a managed platform, the vendor's release notes, not a partner blog. A vendor distribution of an engine (e.g. a commercial Trino distribution) is a different product from the open-source engine; never conflate them when someone says "Trino".
3. **Separate the layers**: "the spec supports X" ≠ "this engine build supports X" ≠ "this catalog and client library support X". A feature is usable only when engine, catalog, and client all agree.
4. **Separate the labels**: GA, public preview, experimental, and read-only are different answers. Platform GA does not mean every feature or external client is GA.
5. **Source tier**: use a `trust_tier: primary` source from `data/sources.json` (project release notes, spec, vendor release notes). Blogs and aggregators blur preview and GA.
6. **Re-check close to launch**; record the checked version and date in the proof matrix.
7. **If browsing is unavailable**, say so and mark version- or status-dependent recommendations as unverified.

Delta catalog-managed tables and coordinated commits, catalog feature status (S3 Tables, Open Catalog, Unity Catalog, Gravitino, DuckLake), and current releases of every format and engine follow the same procedure.

## Workflow Checklist

Before stating a version, feature status, price, or benchmark figure, run the [Version and Support Lookup](#version-and-support-lookup). Quote a benchmark only after reading its dataset shape and source; otherwise state the direction and hedge.

### 1. Architecture and Ingestion

- [ ] Choose the architecture pattern: [references/architecture-patterns.md](references/architecture-patterns.md)
- [ ] Define the CDC or batch ingest path: [references/ingestion-patterns.md](references/ingestion-patterns.md)
- [ ] Streaming semantics, if needed: `data-streaming` skill
- [ ] Domain ownership, if the org is distributed: [references/data-mesh-patterns.md](references/data-mesh-patterns.md)

### 2. Storage and Catalog

- [ ] Select format and spec version: [references/storage-formats.md](references/storage-formats.md); fill the proof matrix
- [ ] Select the catalog: [references/governance-catalog.md](references/governance-catalog.md)
- [ ] Schedule compaction, snapshot retention, and orphan-file cleanup before the first production write

### 3. Transformation and Orchestration

- [ ] Transformation tool and incremental models: `data-analytics-engineering` skill; verify it supports the target catalog and format
- [ ] Orchestrator: [references/orchestration-patterns.md](references/orchestration-patterns.md)

### 4. Query and Serving

- [ ] Lake query engine: [references/query-engine-patterns.md](references/query-engine-patterns.md)
- [ ] Add a serving layer only when concurrency/latency requirements are proven
- [ ] BI layer: [references/bi-visualization-patterns.md](references/bi-visualization-patterns.md)

### 5. Quality, Security, and Ops

- [ ] Quality contracts and checks: `data-analytics-engineering` (data-quality-testing, lake-data-quality-patterns)
- [ ] Access control per engine: [references/security-access-patterns.md](references/security-access-patterns.md)
- [ ] Runbooks: [references/operational-playbook.md](references/operational-playbook.md)
- [ ] File-size targets, retention, and cost guardrails: [references/cost-optimization.md](references/cost-optimization.md)

## Quick Commands

```bash
# Generate Spark SQL DDL for a partitioned Iceberg table (exits non-zero on unknown/invalid partition columns):
python scripts/scaffold_iceberg_table.py --catalog rest --name analytics.events \
  --columns "event_id BIGINT, user_id BIGINT, event_type STRING, ts TIMESTAMP" \
  --partition ts_month,event_type --format-version 2 --target-file-size-mb 256

# Inspect S3-backed Iceberg table layout:
./scripts/inspect_iceberg_metadata.sh --location s3://my-bucket/warehouse/analytics/events --backend s3

# Iceberg maintenance order (Spark procedures; Trino: ALTER TABLE ... EXECUTE expire_snapshots/remove_orphan_files/optimize).
# older_than = now minus the time-travel window, computed by the scheduler; never hard-code a date.
CALL catalog.system.expire_snapshots(table => 'db.events', older_than => TIMESTAMP '<retention cutoff>', retain_last => <retained-snapshot-count-from-policy>);
# Preview orphan candidates; review the result before a separate cleanup call.
CALL catalog.system.remove_orphan_files(table => 'db.events', older_than => TIMESTAMP '<older than longest write>', dry_run => true);
CALL catalog.system.rewrite_data_files('db.events');
CALL catalog.system.rewrite_manifests('db.events');
```

## Do / Avoid

**Do**

- Define data contracts, owners, and retention rules before the first write.
- Make every pipeline idempotent, replayable, and safe to backfill.
- Keep catalog, lineage, and access-control choices explicit.
- Prove interoperability on real engines (the proof matrix) before promising multi-engine support.
- Run any spec-version or vendor-status claim through [Version and support lookup](#version-and-support-lookup).

**Avoid**

- Treating Delta, Iceberg, Hudi, and Paimon as interchangeable.
- Enabling a format version or feature in production because a vendor headline says "supported" — it may mean preview or read-only, for some clients only.
- Hiding governance inside a single vendor-specific default.
- Shipping CDC without delete handling, retention policy, and replay drills.

## Known Traps

- Choosing a table format for vendor fit before validating engine support, catalog behavior, delete semantics, and maintenance tooling across the actual estate.
- Treating object storage plus an open table format as a complete platform while compaction, snapshot retention, metadata cleanup, and orphan-file controls stay unmanaged.
- Mixing CDC upserts, streaming ingestion, and batch rewrites in the same tables without explicit idempotency, late-arrival, and rollback rules.
- Assuming all engines interpret schema evolution, partition pruning, delete files, and time travel consistently.
- Copying warehouse-style small-table habits into the lake, creating small-file, manifest, and metadata amplification at scale.
- Assuming DuckLake is interchangeable with Iceberg REST for multi-engine workloads.
- Treating a coordinated-commits or catalog-managed-tables migration (Delta, Iceberg REST) as a config flag. It changes who owns the commit path and can require client/connector upgrades across every reader and writer — run it as a migration with a rollback plan.
- Picking the format with the best headline feature (row lineage, deletion vectors, Variant) without checking that the client's own catalog, engine, and client library can exercise it.
- Treating Apache Top-Level Project status as production readiness. Graduation is a governance milestone; check adoption, release cadence, and operator experience separately.
- Upgrading an Iceberg table's `format-version` before every reader passes the proof matrix. The upgrade is one-way (no downgrade), so a lagging reader is locked out; new tables stay on v2 until then ([storage-formats.md](references/storage-formats.md#iceberg-v3-readiness)).
- Treating `DELETE` as erasure. Rows stay readable in older snapshots until snapshot expiry and physical file removal (Delta: `VACUUM`); keep the time-travel window shorter than the erasure deadline and purge raw/bronze and CDC copies too ([security-access-patterns.md](references/security-access-patterns.md#right-to-erasure-in-a-lakehouse)).
- Timestamp-cursor incremental loads (`updated_at > last_max`) silently miss hard deletes and rows committed late with an older timestamp. Use log-based CDC or a soft-delete column, re-read a lookback window, compare `>=` at the boundary, and merge on the key ([ingestion-patterns.md](references/ingestion-patterns.md)).
- Letting a proof-of-concept's single-engine choice (DuckLake, embedded DuckDB) silently become production once a second team needs concurrent writes or another engine.

## Navigation

**References** (load on demand)

| File | Load when |
|------|-----------|
| [references/architecture-patterns.md](references/architecture-patterns.md) | Choosing medallion, lambda, kappa, or lakehouse layering |
| [references/data-mesh-patterns.md](references/data-mesh-patterns.md) | Domain ownership, data products, federated governance |
| [references/ingestion-patterns.md](references/ingestion-patterns.md) | Batch or CDC ingest paths (dlt, Airbyte, Debezium) |
| [references/orchestration-patterns.md](references/orchestration-patterns.md) | Choosing or configuring an orchestrator |
| [references/storage-formats.md](references/storage-formats.md) | Format choice, file sizing, compaction, Iceberg v3 readiness |
| [references/governance-catalog.md](references/governance-catalog.md) | Catalog, lineage, and metadata choices |
| [references/query-engine-patterns.md](references/query-engine-patterns.md) | Choosing Trino, Spark, DuckDB, ClickHouse, or StarRocks |
| [references/bi-visualization-patterns.md](references/bi-visualization-patterns.md) | BI layer on the lake |
| [references/security-access-patterns.md](references/security-access-patterns.md) | Table/row/column policies and engine-level ACLs |
| [references/operational-playbook.md](references/operational-playbook.md) | Runbooks for compaction, recovery, and on-call |
| [references/cost-optimization.md](references/cost-optimization.md) | File-size targets, retention windows, cost guardrails |

**Templates** (`assets/`)

- Blueprints: [medallion](assets/cross-platform/template-medallion-architecture.md), [pipeline](assets/cross-platform/template-data-pipeline.md), [migration](assets/cross-platform/template-migration-checklist.md), [partitioning](assets/cross-platform/template-partitioning-strategy.md), [schema evolution](assets/cross-platform/template-schema-evolution.md), [cost](assets/cross-platform/template-cost-optimization.md)
- Ingestion: [governance checklist](assets/cross-platform/template-ingestion-governance-checklist.md), [incremental loading](assets/cross-platform/template-incremental-loading.md), [dlt](assets/ingestion/dlt/template-dlt-pipeline.md) ([REST API source](assets/ingestion/dlt/template-dlt-rest-api.md), [database source](assets/ingestion/dlt/template-dlt-database-source.md), [incremental and merge](assets/ingestion/dlt/template-dlt-incremental.md), [warehouse loading](assets/ingestion/dlt/template-dlt-warehouse-loading.md)), [Airbyte](assets/ingestion/airbyte/template-airbyte-connection.md), [Dagster](assets/orchestration/template-dagster-pipeline.md)
- Quality: [data quality](assets/cross-platform/template-data-quality.md), [quality governance](assets/cross-platform/template-data-quality-governance.md), [backfill runbook](assets/cross-platform/template-data-quality-backfill-runbook.md)
- Formats: [Iceberg table](assets/storage/iceberg/template-iceberg-table.md), [Iceberg maintenance](assets/storage/iceberg/template-iceberg-maintenance.md), [Delta](assets/storage/delta/template-delta-table.md), [Hudi](assets/storage/hudi/template-hudi-table.md), [Parquet](assets/storage/parquet/template-parquet-optimization.md)
- Engines and BI: [DuckDB](assets/query-engines/duckdb/template-duckdb-analytics.md), [DuckDB import/export](assets/query-engines/duckdb/template-duckdb-data-import.md), [ClickHouse](assets/query-engines/clickhouse/template-clickhouse-optimization.md), [ClickHouse setup](assets/query-engines/clickhouse/template-clickhouse-setup.md), [ClickHouse ingestion](assets/query-engines/clickhouse/template-clickhouse-ingestion.md), [ClickHouse replication and sharding](assets/query-engines/clickhouse/template-clickhouse-replication.md), [ClickHouse MVs](assets/query-engines/clickhouse/template-clickhouse-materialized-views.md), [StarRocks](assets/query-engines/starrocks/template-starrocks-setup.md), [Doris](assets/query-engines/doris/template-doris-setup.md), [Metabase request](assets/visualization/metabase/dashboard-request.md), [Metabase connection checklist](assets/visualization/metabase/connection-checklist.md), [Metabase incident playbook](assets/visualization/metabase/incident-playbook.md)

## Related Skills

- [data-streaming](../data-streaming/SKILL.md) - Kafka, Flink, CDC, and streaming ingestion into the lake
- [data-analytics-engineering](../data-analytics-engineering/SKILL.md) - dbt/SQLMesh transformation, semantic layer, data-quality testing
- [ai-mlops](../ai-mlops/SKILL.md) - MLOps, deployment, platform operations
- [ai-ml-data-science](../ai-ml-data-science/SKILL.md) - Analytics and feature engineering workflows
- [data-sql-optimization](../data-sql-optimization/SKILL.md) - OLTP tuning and relational operations
- [ops-devops-platform](../ops-devops-platform/SKILL.md) - Infra, Kubernetes, observability, and runbooks

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
