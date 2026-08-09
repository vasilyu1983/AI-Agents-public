---
name: data-lake-platform
description: "Designs lakehouse platforms across Iceberg, Delta, Hudi, and Paimon. Use when choosing catalogs, CDC paths, query engines, governance, or cost controls."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Data Lake Platform

Build and operate production data lakes and lakehouses: ingest, transform, store in open formats, and serve analytics reliably.

## Quick Reference

| Task | Resource | When to Use |
|------|----------|-------------|
| Pick a table format and spec version | [references/storage-formats.md](references/storage-formats.md) | Choosing Iceberg v2/v3, Delta 4.x, Hudi, Paimon, or DuckLake |
| Pick a catalog / control plane | [references/governance-catalog.md](references/governance-catalog.md) | Choosing Polaris, Glue, Nessie, Unity, Gravitino, or Open Catalog |
| Design ingestion or CDC path | [references/ingestion-patterns.md](references/ingestion-patterns.md) | dlt, Airbyte, Debezium, Flink CDC |
| Scaffold or inspect an Iceberg table | `scripts/scaffold_iceberg_table.py`, `scripts/inspect_iceberg_metadata.sh` | New table DDL or auditing an existing table's file/metadata layout |
| Sanity-check an interoperability or version claim | `data/sources.json` + [Fact-Checking](#fact-checking) below | Any claim about spec-version GA status, engine support, or vendor feature |

### Quick-Start Decision Table

| Situation | Default choice |
|-----------|----------------|
| Open multi-engine analytics | Iceberg + REST catalog (Polaris/Glue/Nessie) + Trino |
| Databricks primary compute | Delta 4.x + Unity Catalog; add UniForm only if external readers exist |
| CDC-heavy mutable, Spark-centered | Hudi (CoW or MoR) + Kafka/Debezium |
| Streaming-first mutable, Flink-centered | Paimon + Flink CDC |
| Single-engine embedded / analyst workstation | DuckLake (v1.0 GA Apr 2026) or DuckDB + Parquet/Iceberg |
| Low-latency BI, high concurrency dashboards | ClickHouse or StarRocks serving layer |
| Local/CI prototyping with open-table portability | DuckDB + Iceberg extension |

## Format State as of July 2026

| Feature | Apache Iceberg (1.11.x) | Delta Lake 4.3 | Apache Hudi (1.0 stable / 1.1 dev) | Apache Paimon (1.3.x) |
|---------|----------------|----------------|-------------|---------------|
| Spec version | v3 GA on managed platforms; Trino writes still experimental | Protocol v3; Liquid Clustering GA | 1.x table version | 1.x |
| Deletion vectors | GA (v3 spec; bitmap on Puffin) | GA | N/A (MoR log) | N/A (MoR log) |
| Catalog posture | REST-first; Polaris TLP Feb 2026 | Catalog-managed tables mature (4.1-4.3); Unity Catalog Delta APIs route all ops | Mixed | Flink-first, expanding |
| Coordinated commits | Via catalog (Polaris/Glue/Nessie) | GA since 4.1; streaming + CDC on catalog-managed tables since 4.3 | N/A | N/A |
| Branches and tags | First-class | Limited | Workflow-specific | Workflow-specific |
| Multi-engine reads | Strong (Trino, Spark, DuckDB, Flink) | Improving via UniForm + native Flink connector (4.2+); Trino v3 writes still experimental | Improving | Growing; validate |
| Trino v3 support | Experimental: read/write of base data works; row-level updates, deletes, and OPTIMIZE on v3 tables are not supported | Readers via UniForm | N/A | N/A |

**Key July 2026 facts (verify before quoting further out):**
- Iceberg v3 is GA on Snowflake (May 7 2026) and AWS (S3 Tables, Glue, EMR — Nov 2025). On **Databricks it is Public Preview** (announced Apr 9 2026, Databricks Runtime 18.0+ with Unity Catalog), not GA — do not tell a Databricks-only user v3 is production-ready there without checking current Databricks release notes.
- Trino's Iceberg connector treats format-version-3 support as experimental in its own docs: base read/write works, but row-level updates, deletes, and `OPTIMIZE` on v3 tables are unsupported. Starburst's Trino-based product has broader v3 support (deletion vectors, variant type) than open-source Trino — don't conflate the two when a client asks about "Trino."
- Delta Lake shipped 4.1 (Mar 2026, catalog-managed tables GA), 4.2 (Apr 2026, native Flink connector, geospatial + Variant GA in Kernel), and 4.3 (Jun 2026, Unity Catalog Delta APIs route every table operation, streaming/CDF on catalog-managed tables). Treat "4.1" as a floor, not the current version.
- Apache Polaris graduated to Apache Top-Level Project on Feb 19 2026 (~100 contributors, 6 releases, 2800+ PRs at graduation) and is now on a monthly release train with federation and credential vending in production.
- DuckLake v1.0 GA Apr 13 2026: SQL-based catalog (SQLite/PostgreSQL/DuckDB), Iceberg-compatible deletion vectors, clients for Spark/Trino/DataFusion/Pandas. DuckLake 1.1 is expected ~Sept 2026 — re-check compatibility notes before committing to a long-lived DuckLake deployment.
- Amazon S3 Tables: Iceberg v3 deletion vectors and row lineage supported (GA, rolled out from Nov 2025); simplified IAM permissions (Mar 2026); GovCloud GA (Feb 2026); two new regions (May 2026).
- Apache Gravitino: TLP graduated Jun 2025; 1.2.0 (Mar 13 2026) added Table Maintenance Service, ClickHouse catalog, end-to-end UDF management; 1.2.1 (May 11 2026) is a stability/correctness patch — prefer it over 1.2.0 for new deployments.
- Apache Hudi 1.1 is an active development branch (pluggable table-format framework, indexing rework) — **not recommended for production** as of July 2026; production Hudi deployments should stay on the 1.0.x line.

Any number here (release dates, contributor counts, benchmark percentages) can drift within weeks in this space — re-verify against the primary source in `data/sources.json` before repeating it in a client-facing recommendation, especially GA-vs-preview status, which vendors routinely blur in marketing copy.

## Decision Tree

```text
Choosing a lakehouse path:
    ├─ Databricks is the primary platform?
    │   └─ Delta 4.x + Unity Catalog; add UniForm only if external readers matter
    │
    ├─ Need open multi-engine access across Trino/Spark/DuckDB?
    │   └─ Iceberg v2/v3 + Polaris / Glue REST / Nessie / Open Catalog
    │       Note: default to v2 if Trino must write; v2 avoids row-update/delete/OPTIMIZE
    │       gaps that v3 still has on open-source Trino as of July 2026
    │
    ├─ Need heavy CDC, mutable tables, or streaming-first semantics?
    │   ├─ Flink-native stack -> Paimon first, compare with Hudi
    │   └─ Spark-heavy stack -> Hudi first (CoW for read-heavy, MoR for write-heavy)
    │
    ├─ Single-engine embedded or analyst workstation?
    │   └─ DuckLake v1.0 (PostgreSQL catalog for multi-instance) or DuckDB + Parquet
    │
    ├─ Need low-latency dashboards or embedded analytics?
    │   ├─ High concurrency BI -> Add ClickHouse / StarRocks / Doris
    │   └─ Local, notebook, CI -> DuckDB + Parquet/Iceberg
    │
    └─ Heterogeneous multi-format estate (Hive + Kafka + RDBMS)?
        └─ Apache Gravitino as federated "catalog of catalogs"
```

## Catalog Landscape (July 2026)

| Catalog | Status | Best for | Watch-outs |
|---------|--------|----------|------------|
| Apache Polaris | TLP since Feb 2026; monthly release train; production-ready | Open self-hosted Iceberg control plane | You still need separate metadata/lineage |
| Glue Iceberg REST + S3 Tables | GA; v3 deletion vectors/row lineage; simplified IAM Mar 2026 | AWS-native managed Iceberg | AWS-centric; S3 Tables auto-compaction |
| Snowflake Open Catalog | GA; v3 GA May 7 2026 | Snowflake-adjacent open Iceberg interop | Validate write paths and service principals |
| Project Nessie | Stable | Branch/tag promotion, isolated backfills | Narrower governance scope |
| Unity Catalog | GA; Delta Lake 4.3 routes all catalog-managed ops through it | Databricks-centered governance + compute | Cross-engine behavior must be verified |
| Apache Gravitino | TLP Jun 2025; 1.2.1 (May 2026) is current stable | Federated multi-format metadata unification | Newer; validate production readiness per deployment |
| DuckLake | v1.0 GA Apr 2026; 1.1 expected ~Sept 2026 | Single-engine or small-team SQL-native lakehouse | Not designed for Spark/Flink concurrent writes |

## Workflow Checklist

### 1. Architecture and Ingestion

- [ ] Choose architecture pattern: [references/architecture-patterns.md](references/architecture-patterns.md) — medallion, mesh, lambda, kappa, lakehouse
- [ ] Define CDC or batch ingestion path: [references/ingestion-patterns.md](references/ingestion-patterns.md) — dlt, Airbyte, Debezium, Flink CDC
- [ ] Configure streaming semantics if needed: [references/streaming-patterns.md](references/streaming-patterns.md) — Kafka, Flink, Spark Structured Streaming
- [ ] Define data mesh domain ownership if org is distributed: [references/data-mesh-patterns.md](references/data-mesh-patterns.md)

### 2. Storage and Catalog

- [ ] Select table format and version: [references/storage-formats.md](references/storage-formats.md)
  - [ ] Iceberg: confirm v2 or v3 — check all engine support before enabling v3
  - [ ] Delta: use 4.x catalog-managed tables for new workloads
  - [ ] Hudi/Paimon: validate engine stack before committing
- [ ] Select catalog: [references/governance-catalog.md](references/governance-catalog.md)
  - [ ] Polaris for open Iceberg; Glue REST for AWS; Nessie for branching; Unity for Databricks
  - [ ] Consider Gravitino for heterogeneous multi-catalog federation
- [ ] Set compaction, snapshot retention, and orphan-file cleanup schedule
- [ ] Test interoperability with all intended engines before declaring multi-engine support

### 3. Transformation

- [ ] Choose transformation tool: [references/transformation-patterns.md](references/transformation-patterns.md) — dbt, SQLMesh, Spark
- [ ] Verify dbt or SQLMesh supports target catalog and table format
- [ ] Set up incremental models with idempotency guarantees
- [ ] Add orchestration layer: [references/orchestration-patterns.md](references/orchestration-patterns.md)

### 4. Query and Serving

- [ ] Choose lake query engine: [references/query-engine-patterns.md](references/query-engine-patterns.md)
- [ ] Add serving layer only when concurrency/latency requirements are proven
- [ ] Configure BI and visualization layer: [references/bi-visualization-patterns.md](references/bi-visualization-patterns.md)

### 5. Quality, Security, and Ops

- [ ] Define data quality contracts and checks: [references/data-quality-patterns.md](references/data-quality-patterns.md)
- [ ] Enforce access control per engine: [references/security-access-patterns.md](references/security-access-patterns.md)
- [ ] Build operational runbooks: [references/operational-playbook.md](references/operational-playbook.md)
- [ ] Enforce file size targets, compaction policy, and cost guardrails: [references/cost-optimization.md](references/cost-optimization.md)

## Quick Commands

```bash
# Generate DDL for partitioned Iceberg table (REST catalog, format v2):
python scripts/scaffold_iceberg_table.py \
  --catalog rest \
  --name analytics.events \
  --columns "event_id BIGINT, user_id BIGINT, event_type STRING, ts TIMESTAMP" \
  --partition ts_month,event_type \
  --format-version 2 \
  --target-file-size-mb 256

# Inspect S3-backed Iceberg table layout:
./scripts/inspect_iceberg_metadata.sh \
  --location s3://my-bucket/warehouse/analytics/events \
  --backend s3

# Iceberg maintenance (run in Spark or Trino):
CALL catalog.system.expire_snapshots('db.events', TIMESTAMP '2026-01-01');
CALL catalog.system.remove_orphan_files('db.events');
CALL catalog.system.rewrite_data_files('db.events');
CALL catalog.system.rewrite_manifests('db.events');

# DuckLake: create catalog and attach (DuckDB v1.5.2+):
INSTALL ducklake; LOAD ducklake;
ATTACH 'ducklake:postgres:dbname=catalog host=localhost' AS lake;

# Delta: check table version and history:
DESCRIBE HISTORY delta.`s3://bucket/path/to/table`
```

## Reference Architectures

- **Open multi-engine**: object storage + Iceberg v2/v3 + Polaris or Glue REST + Trino/Spark + DataHub/OpenMetadata + OpenLineage
- **Databricks-centered**: Delta 4.x + Unity Catalog; add external interoperability only where there is a real consumer requirement
- **Streaming-first mutable**: Kafka/Flink CDC + Hudi or Paimon + Trino/Spark readers + strict replay and retention rules
- **Serving-heavy analytics**: Iceberg/Hudi/Delta upstream + ClickHouse/StarRocks/Doris downstream for fast dashboards
- **Small-team embedded**: DuckLake v1.0 + PostgreSQL catalog + DuckDB compute; upgrade path to Iceberg when multi-engine needed

## Do / Avoid

**Do**

- Define data contracts, owners, and retention rules before first write.
- Make every pipeline idempotent, replayable, and safe to backfill.
- Keep catalog, lineage, and access-control choices explicit.
- Test interoperability on real engines before committing to multi-engine promises.
- Confirm the exact Iceberg v3 feature and engine support matrix (GA vs preview vs experimental — they are not the same) before enabling v3 in production, and re-check it close to launch since GA dates and preview scopes move monthly.
- Use a serving layer only when workloads prove the need.
- Distinguish "the spec supports X" from "our vendor's build of the engine supports X" — Trino open source and Starburst's Trino-based product diverge on Iceberg v3 coverage, and Databricks' own docs may say "Public Preview" even when a partner blog calls it "available."

**Avoid**

- Treating Delta, Iceberg, Hudi, and Paimon as interchangeable.
- Enabling Iceberg v3 writes on Trino in production — as of July 2026 Trino's own docs mark v3 as experimental with row-level updates, deletes, and `OPTIMIZE` unsupported on v3 tables.
- Repeating a vendor's "v3 support" headline without checking whether it means GA, public preview, or read-only — Databricks Iceberg v3 is Public Preview, not GA, even though it is easy to find blog copy that reads as if it shipped.
- Hiding governance inside a single vendor-specific default.
- Shipping CDC without delete handling, retention policy, and replay drills.
- Recommending managed services or format/spec-version claims without current-source verification — this space re-ships GA announcements monthly, and a fact that was accurate in the last training pass is a coin flip a month later.

## Known Traps

- Choosing a table format for vendor fit before validating engine support, catalog behavior, delete semantics, and maintenance tooling across the actual estate.
- Treating object storage plus an open table format as a complete platform while leaving compaction, snapshot retention, metadata cleanup, and orphan-file controls unmanaged.
- Mixing CDC upserts, streaming ingestion, and batch rewrites into the same tables without explicit idempotency, late-arrival, and rollback rules.
- Assuming all engines interpret schema evolution, partition pruning, delete files, and time travel consistently across formats.
- Copying warehouse-style small-table habits into the lake and creating severe small-file, manifest, and metadata amplification at scale.
- Assuming DuckLake is interchangeable with Iceberg REST for multi-engine workloads — DuckLake is SQL-catalog-native and not designed for concurrent Spark/Flink write access.
- Recommending a coordinated-commits or catalog-managed-tables migration (Delta 4.x, Iceberg REST) as a drop-in change. It changes who owns the commit path and can require a client/connector version bump across every reader and writer — sequence it as a migration with a rollback plan, not a config flag.
- Picking the format with the best headline feature (row lineage, deletion vectors, Variant type) without asking whether the *catalog and compute stack the client already has* can actually exercise that feature today. A GA spec feature is not GA for that client until their engine, catalog, and client library all agree on it.
- Treating "Apache project" or "Top-Level Project" status as a maturity signal by itself. TLP graduation (Polaris, Gravitino) is a governance and community milestone, not a production-readiness certification — check adoption, release cadence, and operator experience separately.
- Letting a proof-of-concept's convenient single-engine choice (e.g., DuckLake, embedded DuckDB) silently become the production architecture once a second team needs concurrent writes or a different query engine. Name the upgrade trigger and the target format up front.

## Navigation

**References** (load on demand)

| File | Load when |
|------|-----------|
| [references/architecture-patterns.md](references/architecture-patterns.md) | Choosing medallion, mesh, lambda, kappa, or lakehouse pattern |
| [references/data-mesh-patterns.md](references/data-mesh-patterns.md) | Designing domain ownership, data products, or federated governance |
| [references/ingestion-patterns.md](references/ingestion-patterns.md) | Designing batch or CDC ingest paths (dlt, Airbyte, Debezium) |
| [references/streaming-patterns.md](references/streaming-patterns.md) | Designing Kafka, Flink, or Spark Structured Streaming pipelines |
| [references/orchestration-patterns.md](references/orchestration-patterns.md) | Choosing or configuring an orchestrator (Airflow, Prefect, etc.) |
| [references/storage-formats.md](references/storage-formats.md) | Choosing Iceberg v2/v3, Delta 4.x, Hudi, Paimon, or DuckLake |
| [references/governance-catalog.md](references/governance-catalog.md) | Choosing Polaris, Glue, Nessie, Unity, Gravitino, or Open Catalog |
| [references/transformation-patterns.md](references/transformation-patterns.md) | Designing dbt or SQLMesh transformation layer |
| [references/query-engine-patterns.md](references/query-engine-patterns.md) | Choosing Trino, Spark, DuckDB, ClickHouse, or StarRocks |
| [references/bi-visualization-patterns.md](references/bi-visualization-patterns.md) | Designing BI layer (Metabase, Superset, Looker, etc.) |
| [references/data-quality-patterns.md](references/data-quality-patterns.md) | Adding GX, Soda, or custom quality contracts |
| [references/security-access-patterns.md](references/security-access-patterns.md) | Configuring table/row/column policies and engine-level ACLs |
| [references/operational-playbook.md](references/operational-playbook.md) | Building runbooks for compaction, recovery, and oncall |
| [references/cost-optimization.md](references/cost-optimization.md) | Enforcing file-size targets, retention windows, and cost guardrails |

**Templates**

- Core blueprints: [assets/cross-platform/template-medallion-architecture.md](assets/cross-platform/template-medallion-architecture.md), [assets/cross-platform/template-data-pipeline.md](assets/cross-platform/template-data-pipeline.md), [assets/cross-platform/template-migration-checklist.md](assets/cross-platform/template-migration-checklist.md), [assets/cross-platform/template-partitioning-strategy.md](assets/cross-platform/template-partitioning-strategy.md)
- Ingestion: [assets/cross-platform/template-ingestion-governance-checklist.md](assets/cross-platform/template-ingestion-governance-checklist.md), [assets/cross-platform/template-incremental-loading.md](assets/cross-platform/template-incremental-loading.md), [assets/ingestion/dlt/template-dlt-rest-api.md](assets/ingestion/dlt/template-dlt-rest-api.md), [assets/ingestion/airbyte/template-airbyte-connection.md](assets/ingestion/airbyte/template-airbyte-connection.md)
- Storage and quality: [assets/cross-platform/template-schema-evolution.md](assets/cross-platform/template-schema-evolution.md), [assets/cross-platform/template-data-quality.md](assets/cross-platform/template-data-quality.md), [assets/cross-platform/template-data-quality-governance.md](assets/cross-platform/template-data-quality-governance.md), [assets/cross-platform/template-data-quality-backfill-runbook.md](assets/cross-platform/template-data-quality-backfill-runbook.md)
- Open formats: [assets/storage/iceberg/template-iceberg-table.md](assets/storage/iceberg/template-iceberg-table.md), [assets/storage/iceberg/template-iceberg-maintenance.md](assets/storage/iceberg/template-iceberg-maintenance.md), [assets/storage/delta/template-delta-table.md](assets/storage/delta/template-delta-table.md), [assets/storage/hudi/template-hudi-table.md](assets/storage/hudi/template-hudi-table.md)
- Transforms: [assets/transformation/dbt/template-dbt-project.md](assets/transformation/dbt/template-dbt-project.md), [assets/transformation/sqlmesh/template-sqlmesh-project.md](assets/transformation/sqlmesh/template-sqlmesh-project.md), [assets/transformation/sqlmesh/template-sqlmesh-incremental.md](assets/transformation/sqlmesh/template-sqlmesh-incremental.md), [assets/transformation/sqlmesh/template-sqlmesh-testing.md](assets/transformation/sqlmesh/template-sqlmesh-testing.md), [assets/transformation/sqlmesh/template-sqlmesh-layering-and-access.md](assets/transformation/sqlmesh/template-sqlmesh-layering-and-access.md)
- Engines and BI: [assets/query-engines/duckdb/template-duckdb-analytics.md](assets/query-engines/duckdb/template-duckdb-analytics.md), [assets/query-engines/clickhouse/template-clickhouse-optimization.md](assets/query-engines/clickhouse/template-clickhouse-optimization.md), [assets/query-engines/clickhouse/template-clickhouse-materialized-views.md](assets/query-engines/clickhouse/template-clickhouse-materialized-views.md), [assets/visualization/metabase/dashboard-request.md](assets/visualization/metabase/dashboard-request.md)

## Related Skills

- [ai-mlops](../ai-mlops/SKILL.md) - MLOps, deployment, platform operations
- [ai-ml-data-science](../ai-ml-data-science/SKILL.md) - Analytics and feature engineering workflows
- [data-sql-optimization](../data-sql-optimization/SKILL.md) - OLTP tuning and relational operations
- [ops-devops-platform](../ops-devops-platform/SKILL.md) - Infra, Kubernetes, observability, and runbooks

## Tool/Platform Recommendation Protocol

1. Read `data/sources.json` and start from primary docs.
2. Verify current platform behavior for catalogs, connectors, security, and interoperability.
3. Distinguish open-standard behavior from vendor-specific behavior.
4. Report defaults, tradeoffs, and what is still vendor-bound.
5. If browsing is unavailable, state the limitation and mark recommendations as unverified.

## Fact-Checking

- This skill's dated facts (spec-version GA status, release numbers, contributor/PR counts, benchmark percentages) reflect a snapshot and go stale within weeks — the lakehouse catalog and format space ships GA and preview announcements monthly.
- Before repeating a GA/preview/experimental status claim, verify it against a `trust_tier: primary` source in `data/sources.json` (project release notes, vendor release notes) rather than a blog or aggregator, which often blur preview and GA language.
- Explicitly separate "the format spec supports X" from "this specific engine/vendor build supports X" — these routinely diverge (see Trino vs. Starburst on Iceberg v3; Databricks Public Preview vs. Snowflake/AWS GA on Iceberg v3).
- If web access is unavailable, say so explicitly and mark version- or GA-status-dependent recommendations as unverified rather than presenting a frozen snapshot as current.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
