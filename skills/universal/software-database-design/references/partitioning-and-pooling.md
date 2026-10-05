# Partitioning and Connection Pooling

Use this file when a schema decision depends on table partitioning or on how a connection pooler sits between the application and PostgreSQL. For splitting data across clusters, see [sharding-decision-framework.md](sharding-decision-framework.md).

## Contents

- [Partitioning Decision Gates](#partitioning-decision-gates)
- [Connection Pooling & Schema Design](#connection-pooling--schema-design)

## Partitioning Decision Gates

Partitioning is an operational tool (faster maintenance, cheap bulk-drop of old data, partition pruning on scans) — it is not a performance feature you reach for because a table "feels big." Gate it on real, measured signals:

| Signal | Partition? | Rationale |
|--------|-----------|-----------|
| Table exceeds a few hundred GB, or `VACUUM`/`REINDEX`/backup on it now takes hours | Yes | Maintenance ops scale per-partition, not per-table |
| Retention policy drops data older than N (days/months) on a schedule | Yes | `DROP PARTITION` is instant; `DELETE FROM ... WHERE created_at < ?` on a monolith is a slow, bloat-generating scan |
| Nearly every query filters on the same column you'd partition by (e.g. `tenant_id`, `created_at`) | Yes | Partition pruning turns a full scan into a scan of 1-2 partitions |
| Table is a few tens of GB and queries don't consistently filter on a single candidate key | No | Partitioning adds DDL complexity (per-partition indexes/constraints, cross-partition unique constraints need the partition key in the key) for no query win — a good composite index solves it cheaper |
| The real problem is a missing index or stale statistics | No | Check `EXPLAIN ANALYZE` before reaching for partitioning; it's a common (and expensive) way to avoid diagnosing the actual query plan |

Default to PostgreSQL declarative range or list partitioning on the field the retention/access pattern demands; hash-partition only to spread write load evenly with no natural range/list key. Re-verify current limits (partition count, unique-constraint requirements) against the target major version's docs before committing to a scheme — these have loosened across recent PostgreSQL releases.

## Connection Pooling & Schema Design

Schema and migration choices interact with the connection pooler, not just the database engine — this is easy to miss because it only bites under load:

- **Transaction-mode pooling (for example PgBouncer) does not preserve session-scoped state across transactions.** The server connection remains assigned for the whole transaction and is released afterward; statement pooling, not transaction pooling, can reassign it after each statement. Session-level `SET search_path`, advisory locks, `LISTEN/NOTIFY`, and temp tables therefore cannot be assumed to persist across separate transactions. Use `SET LOCAL search_path` inside an explicit transaction when the pooler supports it, or schema-qualify tenant references; never rely on a per-request session setting across pooled transactions. Verify the chosen pooler's mode and feature support before migration or ORM configuration.

Pool release boundaries: [PgBouncer `pool_mode`](https://www.pgbouncer.org/config#pool_mode).
- **Prepared statements and transaction pooling used to be mutually exclusive**; PgBouncer 1.21+ supports prepared statements in transaction mode via `max_prepared_statements`, but confirm the pooler version and setting before assuming an ORM's prepared-statement cache is safe under pooling — older poolers or misconfigured settings silently fall back to unprepared (slower) execution or error.
- **Schema-per-tenant multiplies pooled connection overhead.** Every additional schema is additional catalog metadata pooled connections must resolve; at a few thousand schemas, `search_path`-per-request switching plus catalog bloat becomes a measurable tax. This is one more reason shared-schema-with-RLS scales further than schema-per-tenant for most SaaS (see [Scenario S1](schema-design-scenarios.md#s1--multi-tenant-schema-shared-vs-schema-per-tenant)).
- **Migrations that use session-level `SET` (e.g. `SET statement_timeout`, `SET lock_timeout`) need it re-applied per pooled connection**, not assumed to persist — run migrations through a direct (non-pooled) connection, not through the application's pooled path.
