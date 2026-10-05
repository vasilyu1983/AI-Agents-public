# Query Engine Patterns

Choose engines by access pattern, concurrency, latency, and catalog compatibility — not by habit. Engine templates live under `../assets/query-engines/` (ClickHouse, DuckDB, StarRocks, Doris).

## Three Roles

- **Lake query engines** (Trino, Spark): SQL over open table formats, large joins, federation. The default.
- **Serving engines** (ClickHouse, StarRocks, Doris): high-concurrency dashboards and sub-second analytics, downstream of the lake.
- **Embedded engine** (DuckDB): local analysis, CI checks, notebooks, application-side OLAP.

## Decision Guide

| Need | Default | Watch-outs |
|------|---------|-----------|
| Open lakehouse SQL across Iceberg/Delta/Hudi or federated sources | Trino | Explicit catalog and connector discipline; separate catalogs per environment and trust boundary |
| Heavy batch transforms, feature builds, streaming tied to the write path | Spark | Heavy for interactive BI; do not default every query to it |
| Analyst-local, CI, or embedded analytics over Parquet/Iceberg | DuckDB | Single process; not a cluster serving layer |
| Sub-second dashboards, customer-facing analytics, high QPS | ClickHouse | Model tables for access patterns; merges are asynchronous |
| Accelerate lake queries in place (external catalog + materialized views) | StarRocks | Tune refresh and external-catalog caching |
| Real-time ingestion plus MPP serving | Doris | Less engine-neutral than lake engines |

## Rules

1. **Serving layer only when proven**: add ClickHouse/StarRocks/Doris when a load test shows the lake engine cannot meet the concurrency or latency SLO economically — not before.
2. **The lake stays the source of truth**: serving tables are rebuildable read models. Keep the lake or raw ingest log for reprocessing.
3. **Catalog compatibility is part of engine choice**: an engine that cannot use your catalog for writes (or for a format version's delete files) fails the proof matrix. Per-engine support: [SKILL.md: Version and support lookup](../SKILL.md#version-and-support-lookup).
4. **Trino catalogs**: the Iceberg connector for Iceberg tables; a multi-format lakehouse-style connector only when one catalog must expose Iceberg, Delta, and Hudi through a shared metastore.
5. **DuckDB for validation**: use it in CI to assert row counts, schema, and invariants against Parquet or Iceberg snapshots before promotion; verify catalog/cloud integrations against its extension docs before recommending a REST or managed-catalog flow.
6. **ClickHouse modeling**: `ORDER BY` follows the dominant filters (low-cardinality columns first, then time); partition coarsely (monthly or daily by volume), never by a high-cardinality key; use `FINAL` sparingly because it forces merge-on-read at query time; pre-aggregate with materialized views where dashboard SLOs demand it. Details: [ClickHouse optimization template](../assets/query-engines/clickhouse/template-clickhouse-optimization.md).
7. **Streaming into serving engines** (Doris routine load, ClickHouse Kafka engine): the consumer offset is state; plan replay and dedup (ReplacingMergeTree or unique-key tables) because at-least-once delivery duplicates rows on restart.
