# Open Table Formats

Choose format, catalog, and interoperability path together; the format alone is not the control plane. For any release, spec-version, or per-engine support question, use [SKILL.md: Version and support lookup](../SKILL.md#version-and-support-lookup).

## Contents

- [Format Selection](#format-selection)
- [Interoperability Levers](#interoperability-levers)
- [Apache Iceberg](#apache-iceberg)
- [Delta Lake](#delta-lake)
- [Apache Hudi](#apache-hudi)
- [Apache Paimon](#apache-paimon)
- [DuckLake](#ducklake)
- [Parquet Files](#parquet-files)
- [Iceberg v3 Readiness](#iceberg-v3-readiness)

## Format Selection

| Need | Default | Why |
|------|---------|-----|
| Open multi-engine reads, long-term portability | Iceberg | Widest engine and REST-catalog support; hidden partitioning; branches/tags |
| Databricks-native governance and operations | Delta | Unity Catalog, managed maintenance, deletion vectors in the Databricks stack |
| Heavy upserts/deletes, incremental pull, Spark-heavy | Hudi | Record-level index, CoW/MoR choice per table, incremental queries |
| Changelog-native, streaming-first, Flink-heavy | Paimon | LSM primary-key tables built around Flink semantics |
| Already locked into mixed formats | XTable bridge or a migration plan | Reduce format sprawl; metadata sync is not feature parity |

Rules:

- Keep Iceberg as the open default unless a platform-specific reason is stronger.
- Upserts: Hudi and Paimon are built for them; Iceberg and Delta handle them well but need regular compaction of delete files.
- Test real interoperability (SKILL.md proof matrix) before advertising multi-engine support.

## Interoperability Levers

**Iceberg REST catalog** — one catalog contract across engines and clients. Polaris for open self-hosted, Glue Iceberg REST for AWS, Snowflake Open Catalog when Snowflake is in the operating model, Nessie when branch/tag workflows are primary.

**Apache XTable** — translates metadata between formats without copying data. Use for migration without immediate rewrites, mixed-engine estates, and staged experiments. Metadata sync does not erase format-specific behavior (delete semantics, clustering, maintenance).

**Delta UniForm** — Delta stays the source of truth; outside readers see Iceberg-compatible metadata. Before promising portability, validate per reader: supported engines, writer symmetry (external engines usually read only), maintenance semantics, and ACL behavior outside Databricks.

## Apache Iceberg

- **Hidden partitioning**: partition by transforms (`days(ts)`, `bucket(16, id)`, `truncate(10, name)`); queries filter on the source column and still prune. Users never reference partition columns, so the layout can change without query rewrites.
- **Partition evolution** is metadata-only: old files keep the old spec, new writes use the new spec. Use it instead of rewriting a table when volume changes; plan-time pruning works across both specs.
- **Transforms by volume**: `hours()` only when a single day holds far more than the target file size; otherwise `days()`/`months()`. Use `bucket(N, col)` for high-cardinality join/filter keys instead of identity partitions.
- **Branches and tags**: branches for isolated backfills, QA, and write-audit-publish; tags for audit points and release markers. DDL differs by engine; validate syntax on the active engine.
- **Maintenance order**: expire snapshots -> remove orphan files -> rewrite data files -> rewrite manifests. Expiry cutoff = now minus the time-travel window, computed by the scheduler. Orphan cleanup cutoff must be older than the longest-running write, or live job files are deleted.

```sql
-- Spark SQL procedures
CALL catalog.system.expire_snapshots(table => 'db.events', older_than => TIMESTAMP '<retention cutoff>', retain_last => 10);
CALL catalog.system.remove_orphan_files(table => 'db.events', older_than => TIMESTAMP '<older than longest write>');
CALL catalog.system.rewrite_data_files('db.events');
CALL catalog.system.rewrite_manifests('db.events');

-- Trino equivalents (no CALL system.rewrite_* procedures)
ALTER TABLE db.events EXECUTE expire_snapshots(retention_threshold => '7d');
ALTER TABLE db.events EXECUTE remove_orphan_files(retention_threshold => '7d');
ALTER TABLE db.events EXECUTE optimize;
```

Full maintenance template: [template-iceberg-maintenance.md](../assets/storage/iceberg/template-iceberg-maintenance.md).

## Delta Lake

- Use when Databricks is the control plane or Delta-native operations matter more than engine neutrality.
- Outside Databricks, delta-rs (Python/Rust, Polars) reads and writes Delta without Spark; check which table features (deletion vectors, column mapping, clustering) the client supports before enabling them on shared tables — enabling a reader/writer feature locks out clients that lack it.
- Add UniForm only when a named external reader exists; test each reader.

## Apache Hudi

- **Copy-on-Write** for read-heavy tables: updates rewrite files, reads are plain Parquet.
- **Merge-on-Read** for write-heavy/CDC tables: updates land in log files, reads merge until compaction; schedule compaction or read latency grows.
- Required keys: `recordkey.field` (identity), `partitionpath.field`, and the precombine/ordering field (e.g. `updated_at`) that decides which duplicate wins. A wrong or missing ordering field silently keeps the wrong version under out-of-order CDC.
- Validate index type and compaction behavior per engine before claiming interoperability.

## Apache Paimon

Good fit: changelog-rich pipelines, primary-key tables with continuous updates, Flink-centric compute and table services. Validate engine support outside Flink explicitly; do not assume Iceberg or Hudi semantics.

## DuckLake

Stores all table metadata in a SQL database (SQLite single-process, PostgreSQL multi-instance, or DuckDB) instead of file-based metadata; ships as a DuckDB extension. Check its release notes for client support and minimum DuckDB version.

- **Choose** when DuckDB is the primary engine, the team is small, and no Spark/Flink concurrent writes are required.
- **Do not choose** when multiple engines need concurrent read/write by design, an Iceberg REST contract is required, or engine portability is a hard requirement. Then Iceberg format v2 + REST catalog is the default.
- Name the upgrade trigger (second engine, concurrent writers) at design time.

## Parquet Files

Every table format writes Parquet underneath: ZSTD compression by default, target file and row-group sizes per [template-parquet-optimization.md](../assets/storage/parquet/template-parquet-optimization.md), and select only needed columns so pruning and pushdown work.

## Iceberg v3 Readiness

Iceberg format v3 is a spec version. Its main additions: deletion vectors (a bitmap per data file stored in Puffin files, replacing position deletes), row lineage, and type-system extensions (e.g. Variant, nanosecond timestamps). Whether an engine supports each of these for read, write, row-level operations, and maintenance is a lookup, not a fact to quote: [SKILL.md: Version and support lookup](../SKILL.md#version-and-support-lookup).

Before upgrading a table:

- [ ] Every writer and every reader of the table passes the proof matrix on v3, including row-level update/delete and maintenance.
- [ ] Existing schema is valid under v3 type and nullability rules.
- [ ] Treat the upgrade as one-way: Iceberg does not support downgrading `format-version`, so a reader that lacks v3 is locked out until it upgrades.
- [ ] New tables stay on `format-version=2` until the above passes.
- [ ] Canonical details: the [Iceberg spec](https://iceberg.apache.org/spec/). Vendor delete-performance benchmarks: read the dataset shape before quoting a figure.
