# Data Governance and Catalog

Purpose: choose the right control plane for open tables, discovery, lineage, and policy enforcement.

## Table of Contents

- [Decision Tree](#decision-tree)
- [Catalog Pattern Comparison](#catalog-pattern-comparison)
- [Recommended Layering](#recommended-layering)
- [Runtime Catalog Patterns](#runtime-catalog-patterns)
- [Apache Polaris](#apache-polaris)
- [AWS Glue Iceberg REST and S3 Tables](#aws-glue-iceberg-rest-and-s3-tables)
- [Snowflake Open Catalog](#snowflake-open-catalog)
- [Project Nessie](#project-nessie)
- [Unity Catalog](#unity-catalog)
- [Metadata Platforms](#metadata-platforms)
- [DataHub](#datahub)
- [datahub/recipes/clickhouse.yaml](#datahubrecipesclickhouseyaml)
- [OpenMetadata](#openmetadata)
- [openmetadata/clickhouse-ingestion.yaml](#openmetadataclickhouse-ingestionyaml)
- [Lineage and Contracts](#lineage-and-contracts)
- [Data Quality](#data-quality)
- [Great Expectations](#great-expectations)
- [Soda](#soda)
- [soda/checks.yaml](#sodachecksyaml)
- [Best Practices](#best-practices)

## Decision Tree

```text
What are you choosing?
    ├─ Runtime catalog for Iceberg tables?
    │   ├─ Open, self-hosted, multi-engine -> Polaris (TLP Feb 2026) or Nessie
    │   ├─ AWS-managed -> Glue Iceberg REST + S3 Tables (v3 + simplified IAM Mar 2026)
    │   ├─ Snowflake-managed -> Open Catalog (v3 GA May 7 2026)
    │   ├─ Databricks-centric -> Unity Catalog
    │   └─ Single-engine / small team -> DuckLake v1.0 (PostgreSQL catalog for multi-instance)
    │
    ├─ Heterogeneous multi-catalog federation (Hive + RDBMS + Kafka + Iceberg)?
    │   └─ Apache Gravitino (TLP Jun 2025; 1.2.1 May 2026 current stable)
    │
    ├─ Metadata discovery and lineage portal?
    │   ├─ Open-source metadata platform -> DataHub or OpenMetadata
    │   └─ Databricks-only governance -> Unity may be enough for v1
    │
    └─ Need both?
        └─ Use a runtime table catalog plus a metadata platform; they solve different problems
```

## Catalog Pattern Comparison (July 2026)

| Pattern | Status | Best for | Strengths | Watch-outs |
|---------|--------|----------|-----------|------------|
| Apache Polaris | TLP since Feb 19 2026; production-ready | Open Iceberg control plane | REST-first, multi-engine friendly, vendor-neutral TLP | Still need separate metadata/lineage/access planes |
| AWS Glue Iceberg REST + S3 Tables | GA; v3 + deletion vectors; simplified IAM Mar 2026 | AWS-native open-table catalog | Managed REST; IAM/SigV4; auto-compaction on S3 Tables | AWS-centric operational model |
| Snowflake Open Catalog | GA; Iceberg v3 GA May 7 2026 | Snowflake-adjacent Iceberg interop | Managed; v3 GA earliest | Validate write paths and service-principal model |
| Project Nessie | Stable | Branching and promotion workflows | Git-like branches/tags | Narrower governance scope |
| Unity Catalog | GA; open-source effort ongoing | Databricks-centered governance | Native row/column controls, audits, platform integration | Vendor-centered; cross-engine behavior must be checked |
| Apache Gravitino | TLP Jun 2025; 1.2.1 (May 2026) current stable | Federated multi-catalog (Hive + Kafka + RDBMS + Iceberg) | Unified metadata API across heterogeneous sources | Newer; validate production readiness per deployment |
| DuckLake | GA v1.0 Apr 2026 | Single/small-team SQL-native lakehouse | Simplest operational model; PostgreSQL for multi-instance | Not for concurrent Spark/Flink write access |
| DataHub | Stable | Metadata and governance portal | Discovery, lineage, ownership, policy workflows | Not a runtime table catalog |
| OpenMetadata | Stable | Metadata and governance portal | Catalog, lineage, profiling, open-source | Not a runtime table catalog |

## Recommended Layering

Do not collapse these concerns into one product category:

- **Runtime table catalog**: resolves tables, snapshots, branches, and credentials for readers and writers.
- **Metadata platform**: manages discovery, ownership, glossary, documentation, and stewardship workflows.
- **Lineage plane**: records job and dataset lineage, usually via OpenLineage or platform-native events.
- **Access-control plane**: enforces table, row, column, and tag policies.

Recommended default stacks:

- **Open multi-engine stack**: Polaris or Glue REST + DataHub/OpenMetadata + OpenLineage + platform IAM or Ranger-style enforcement.
- **AWS-managed stack**: Glue REST + S3 Tables + Lake Formation + DataHub/OpenMetadata where broader discovery is needed.
- **Databricks-centered stack**: Unity Catalog first; add DataHub/OpenMetadata only if cross-platform discovery or non-Databricks assets matter.
- **Branch-heavy dev/test workflow**: Nessie plus explicit promotion rules and retention for data branches.

## Runtime Catalog Patterns

### Apache Polaris

Apache Polaris graduated from the Apache Incubator to Top-Level Project on February 19 2026 (unanimous vote; ~100 contributors, 6 releases, 2800+ PRs). Use Polaris when you want an open, Iceberg-native control plane with REST semantics and vendor neutrality.

Good fit:

- Trino, Spark, Flink, and Python clients need one catalog contract
- You want self-hosting or controlled deployment with neutral governance
- You need open governance posture without forcing one compute engine

### AWS Glue Iceberg REST and S3 Tables

Use this path when AWS is your control plane and you want managed Iceberg semantics without operating your own REST catalog.

Good fit:

- S3 is already your storage standard
- IAM, SigV4, and Lake Formation are part of the security model
- You want AWS-managed operational posture for open tables

### Snowflake Open Catalog

Use Open Catalog when Snowflake is part of the operating model but you still need open Iceberg interoperability outside Snowflake.

Good fit:

- Snowflake is already a core platform and team skill center
- You need managed Iceberg catalog behavior for external engines
- You can tolerate vendor-specific boundaries and validate writer support

### Project Nessie

Use Nessie when branch and tag workflows are the main requirement, especially for data promotion, testing, and isolated backfills.

Good fit:

- Feature-style data branches are operationally important
- Promotion and rollback workflows matter more than centralized policy UX
- You are comfortable composing governance from multiple tools

### Unity Catalog

Use Unity Catalog when Databricks is the primary governance and compute plane.

Good fit:

- Unity-native access control, masking, audit, and asset management are central
- Most critical readers and writers are Databricks-managed
- External interoperability is secondary and verified case by case

### Apache Gravitino

Apache Gravitino graduated to TLP in June 2025. Use it as a federated "catalog of catalogs" when the estate includes heterogeneous metadata sources (Hive, RDBMS, Kafka, Iceberg, ClickHouse) that need a unified API.

Good fit:

- Platform has multiple incompatible catalog systems that cannot be migrated to a single standard
- Need unified RBAC across catalog systems
- AI model catalog integration is on the roadmap (Gravitino 2026 roadmap item)

Version 1.2.0 (March 13 2026) added: Table Maintenance Service, ClickHouse catalog, end-to-end UDF management, scan planning offload for DuckDB and Spark, multi-version Trino connector. 1.2.1 (May 11 2026) is a stability/correctness patch — prefer it for new deployments.

Do not use Gravitino as a replacement for a runtime Iceberg catalog. It federates metadata; it does not replace Polaris, Glue, or Nessie for table-level coordination.

## Metadata Platforms

### DataHub

Choose DataHub when search, ownership workflows, catalog API access, and broader metadata automation matter.

```yaml
# datahub/recipes/clickhouse.yaml
source:
  type: clickhouse
  config:
    host_port: clickhouse:9000
    database: analytics
    username: datahub
    password: ${CLICKHOUSE_PASSWORD}
    include_tables: true
    include_views: true
    profiling:
      enabled: true

sink:
  type: datahub-rest
  config:
    server: http://datahub-gms:8080
```

### OpenMetadata

Choose OpenMetadata when you want a strongly integrated open-source metadata platform with profiling and governance workflows.

```yaml
# openmetadata/clickhouse-ingestion.yaml
source:
  type: clickhouse
  serviceName: clickhouse-analytics
  serviceConnection:
    config:
      type: Clickhouse
      hostPort: clickhouse:9000
      username: openmetadata
      password: ${CLICKHOUSE_PASSWORD}
      databaseSchema: analytics

processor:
  type: orm-profiler
  config:
    profiler:
      includeViews: true

sink:
  type: metadata-rest
  config: {}

workflowConfig:
  openMetadataServerConfig:
    hostPort: http://openmetadata:8585/api
    authProvider: openmetadata
    securityConfig:
      jwtToken: ${JWT_TOKEN}
```

## Lineage and Contracts

Minimum expectation for production stacks:

- Emit job and dataset lineage via OpenLineage or platform-native equivalent.
- Record owners, domains, sensitivity tags, and lifecycle state in the metadata plane.
- Enforce schema and freshness contracts in CI or orchestration, not only in dashboards.
- Keep access-control rules outside ad hoc SQL view sprawl when possible.

## Data Quality

### Great Expectations

```python
import great_expectations as gx

context = gx.get_context()
suite = context.add_expectation_suite("events_quality")

validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="events_quality"
)

validator.expect_column_values_to_not_be_null("event_id")
validator.expect_column_values_to_be_unique("event_id")
validator.expect_column_values_to_be_in_set(
    "status", ["pending", "completed", "failed"]
)
validator.expect_column_values_to_be_between(
    "amount", min_value=0, max_value=1000000
)

validator.save_expectation_suite()
```

### Soda

```yaml
# soda/checks.yaml
checks for events:
  - row_count > 0
  - missing_count(event_id) = 0
  - duplicate_count(event_id) = 0
  - invalid_count(status) = 0:
      valid values: [pending, completed, failed]
  - freshness(created_at) < 1h
```

## Best Practices

1. Pick the runtime table catalog explicitly; do not leave it as an implied engine default.
2. Treat metadata platforms as complements to table catalogs, not replacements.
3. Keep branch/tag promotion, replay, and retention policies version-controlled.
4. Enforce ownership, data class, and contract metadata before broad consumer adoption.
5. Validate access-control semantics per engine; table visibility is not enough.
6. Verify current platform claims from primary docs before recommending managed catalogs.
