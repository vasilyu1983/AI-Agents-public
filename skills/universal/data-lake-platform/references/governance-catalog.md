# Data Governance and Catalog

Choose the control plane for open tables, discovery, lineage, and policy enforcement. Catalog comparison table: [SKILL.md: Catalog Landscape](../SKILL.md#catalog-landscape). Release, Iceberg-spec, and IAM-model status per catalog: [SKILL.md: Version and support lookup](../SKILL.md#version-and-support-lookup).

## Decision Tree

```text
What are you choosing?
    ├─ Runtime catalog for Iceberg tables?
    │   ├─ Open, self-hosted, multi-engine -> Polaris (or Nessie if branching is primary)
    │   ├─ AWS-managed -> Glue Iceberg REST + S3 Tables
    │   ├─ Snowflake in the operating model -> Open Catalog
    │   ├─ Databricks-centric -> Unity Catalog
    │   └─ Single engine / small team -> DuckLake (PostgreSQL catalog for multi-instance)
    ├─ Heterogeneous multi-catalog federation (Hive + RDBMS + Kafka + Iceberg)?
    │   └─ Apache Gravitino — federates metadata; does NOT replace a runtime Iceberg catalog
    ├─ Discovery, ownership, and lineage portal?
    │   ├─ Open source -> DataHub (search, API, automation) or OpenMetadata (integrated profiling)
    │   └─ Databricks-only estate -> Unity may be enough at first
    └─ Need both? -> runtime table catalog + metadata platform; they solve different problems
```

## Four Planes — Do Not Collapse Them

| Plane | Job | Typical choice |
|-------|-----|----------------|
| Runtime table catalog | Resolve tables, snapshots, branches, and vended credentials for readers and writers | Polaris, Glue REST, Nessie, Unity, Open Catalog |
| Metadata platform | Discovery, ownership, glossary, stewardship | DataHub, OpenMetadata |
| Lineage | Job and dataset lineage events | OpenLineage or platform-native |
| Access control | Table, row, column, and tag policies | Platform IAM, Lake Formation, Unity, Ranger-style |

Default stacks:

- **Open multi-engine**: Polaris or Glue REST + DataHub/OpenMetadata + OpenLineage + IAM or Ranger-style enforcement.
- **AWS-managed**: Glue REST + S3 Tables + Lake Formation; add DataHub/OpenMetadata when discovery spans non-AWS assets.
- **Databricks-centered**: Unity Catalog first; add a metadata platform only if non-Databricks assets matter.
- **Branch-heavy dev/test**: Nessie plus explicit promotion rules and retention for data branches (unmerged branches pin snapshots and storage).

## Choose-When Rules

- **Polaris**: Trino, Spark, Flink, and Python clients need one vendor-neutral REST contract; self-hosting is acceptable.
- **Glue Iceberg REST + S3 Tables**: S3, IAM/SigV4, and Lake Formation are already the security model. S3 Tables runs its own compaction — disable your own compaction jobs on those tables or they fight.
- **Snowflake Open Catalog**: Snowflake is a core platform but external engines need Iceberg access; validate external write paths and the service-principal model.
- **Nessie**: data branches for promotion, testing, and isolated backfills matter more than centralized policy UX.
- **Unity Catalog**: most critical readers and writers are Databricks-managed; verify external interoperability case by case.
- **Gravitino**: several incompatible catalog systems cannot be migrated to one standard and need a unified API or RBAC. Validate production readiness per deployment.

## Lineage and Contracts — Production Minimum

- Emit job and dataset lineage via OpenLineage or a platform-native equivalent.
- Record owners, domains, sensitivity tags, and lifecycle state in the metadata plane before broad consumer adoption.
- Enforce schema and freshness contracts in CI or orchestration, not only in dashboards. Quality checks (GX, Soda, dbt/SQLMesh tests): `data-analytics-engineering` skill.
- Keep access rules in the access-control plane, not in ad hoc SQL view sprawl.

## Rules

1. Pick the runtime table catalog explicitly; never leave it as an implied engine default.
2. Treat metadata platforms as complements to table catalogs, not replacements.
3. Version-control branch/tag promotion, replay, and retention policies.
4. Validate access-control semantics per engine; table visibility is not enough (see [security-access-patterns.md](security-access-patterns.md)).
5. Apache Top-Level Project status is a governance milestone, not a production-readiness signal.
