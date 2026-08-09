---
name: data-sql-optimization
description: "Diagnoses and tunes SQL for OLTP workloads on PostgreSQL, MySQL, and SQL Server. Use when tuning queries, reading plans, indexing, or fixing lock contention."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# SQL Optimization

Operational guidance for **transactional SQL systems**. This skill is strongest on **PostgreSQL, MySQL, and SQL Server** for query tuning, plan analysis, index strategy, connection pressure, lock contention, and safe production changes.

**Primary coverage:** PostgreSQL, MySQL, SQL Server
**Lighter coverage:** Oracle, SQLite
**Out of scope:** OLAP engines and lakehouse tuning. Use [data-lake-platform](../data-lake-platform/SKILL.md) for ClickHouse, DuckDB, Doris, StarRocks, Iceberg, Delta Lake, or Hudi.

## Quick Reference

### Scripts

| Script | What it does | Usage |
|--------|-------------|-------|
| [scripts/pg_slow_query_triage.sql](scripts/pg_slow_query_triage.sql) | Five-section triage report from `pg_stat_statements`: top by total time, mean time, I/O, variance, and cache-hit ratio | Copy-paste into `psql` or any SQL client; requires `pg_stat_statements` extension |
| [scripts/explain_collector.py](scripts/explain_collector.py) | Runs `EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)` on a list of queries via `psql`, outputs JSONL | `DATABASE_URL=postgresql://... python explain_collector.py --queries slow.txt` |

```bash
# Triage: paste directly into psql
psql $DATABASE_URL -f frameworks/shared-skills/skills/data-sql-optimization/scripts/pg_slow_query_triage.sql

# Collect EXPLAIN plans for top queries (production-safe mode):
python scripts/explain_collector.py --queries queries.txt --no-analyze --output plans.jsonl

# Collect with ANALYZE (executes queries — use on a replica):
DATABASE_URL=postgresql://user:pass@replica:5432/db \
  python scripts/explain_collector.py --queries queries.txt --output plans.jsonl
```

| Need | Start Here | Use When |
|------|------------|----------|
| Slow query triage | [template-slow-query.md](assets/cross-platform/template-slow-query.md) | You need a safe intake before changing anything |
| Plan review | [references/explain-analysis.md](references/explain-analysis.md) | You already have `EXPLAIN`, `EXPLAIN ANALYZE`, Query Store, or Performance Schema evidence |
| Index design or index removal | [references/index-patterns.md](references/index-patterns.md) | You are deciding whether to add, reshape, make invisible, or drop an index |
| Query rewrite | [references/query-tuning-patterns.md](references/query-tuning-patterns.md) | A query shape or estimation problem is the likely bottleneck |
| Connection saturation | [references/connection-pooling-patterns.md](references/connection-pooling-patterns.md) | App pools, PgBouncer, RDS Proxy, Supavisor, or Cloud SQL pooling are involved |
| Monitoring and alerting | [references/monitoring-alerting-patterns.md](references/monitoring-alerting-patterns.md) | You need dashboards, baselines, or alerts for database performance |
| Locking / deadlocks | [template-lock-analysis.md](assets/cross-platform/template-lock-analysis.md) | The issue is blocking, deadlocks, or long transactions rather than raw query cost |
| Partitioning | [references/partition-strategies.md](references/partition-strategies.md) | Retention, pruning, or table growth is driving the change |
| Security or RLS review | [template-security-audit.md](assets/cross-platform/template-security-audit.md) | You are reviewing least privilege, SQL injection controls, or tenant isolation |

## Coverage Model

| Engine | Status | Notes |
|--------|--------|-------|
| PostgreSQL 18 (GA 2025-09-25) | Primary | AIO, skip scan, uuidv7(), statistics retention across pg_upgrade; deepest coverage |
| MySQL 9.7 LTS (GA 2026-04-21) | Primary | Current LTS; HyperGraph optimizer available but not default; 8.4 LTS still supported |
| SQL Server 2025 (GA 2025-11-18) | Primary | IQP 3.0, DOP feedback, OPPO; Query Store on readable secondaries |
| Oracle | Secondary | Use templates and official docs for optimizer-specific edge cases |
| SQLite | Secondary | Focus on indexes, planner behavior, WAL, and `PRAGMA optimize` |

## Use This Skill When

Invoke this skill for requests about:

- Slow SQL queries, plan interpretation, or index usage
- PostgreSQL `pg_stat_statements`, MySQL Performance Schema, or SQL Server Query Store
- Missing indexes, over-indexing, invisible-index trials, or composite-index ordering
- Correlated predicate misestimation, histograms, or extended statistics
- Lock contention, idle-in-transaction sessions, or deadlock triage
- Connection storms, pool sizing, PgBouncer modes, RDS Proxy, Supavisor, or Cloud SQL Managed Connection Pooling
- Partition pruning, retention via detach/drop, or online schema change safety
- Backup, restore, migration, and replication runbooks
- Database security reviews, least privilege, or PostgreSQL RLS checks

## First Response Checklist

Before recommending changes, collect:

1. Database engine and exact version
2. Query text or workload shape
3. Relevant schema, indexes, and estimated row counts
4. Actual evidence: plan output, wait stats, query stats, or error text
5. Recent changes: schema, config, deploy, traffic spike, or data skew
6. Concurrency context: app pool, server pooler, replica topology
7. Success metric: p95 latency, CPU, reads, lock time, error rate, or connection count

If any of these are missing, request them or use the intake templates before suggesting a production change.

## EXPLAIN-Driven Diagnosis Checklist

Run this sequence before recommending any change:

```sql
-- PostgreSQL: capture full plan evidence
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT) <query>;

-- MySQL: get JSON plan for detailed cost breakdown
EXPLAIN FORMAT=JSON <query>;

-- SQL Server: turn on I/O and CPU evidence
SET STATISTICS IO, TIME ON;
<query>;
```

| Step | What to Check | Red Flag |
|------|---------------|----------|
| 1 | Highest-cost or longest-elapsed operator | Any node consuming >60% of total time |
| 2 | Rows estimated vs rows actual | Ratio >10x in either direction |
| 3 | Loops * rows per loop = total rows processed | High total even if one loop looks cheap |
| 4 | Shared hit vs read buffers (PostgreSQL) | `reads` >> `hits` on a hot query |
| 5 | Sort or hash spill | `Sort Method: external merge`, `Hash Batches > 1` |
| 6 | Key/bookmark lookup on hot path | Many per parent row; add INCLUDE columns |
| 7 | Nested loop on large build side | Switch to hash join via statistics fix, not a hint |
| 8 | Waiting time >> execution time | Investigate locks or pool saturation, not the plan |

**Bottleneck decision table:**

| Plan shows | Likely cause | First lever |
|-----------|-------------|-------------|
| Seq scan, high rows-read/rows-returned | Missing or unusable index | Check predicate sargability; add index |
| Index scan but high loops | N+1 or bad join order | Batch or fix estimation |
| Actual >> estimated rows | Stale/insufficient stats | `ANALYZE`; `CREATE STATISTICS` (PG); histogram (MySQL) |
| Plan varies by parameter | Parameter sensitivity | Query Store / OPPO (SQL Server); separate query shapes |
| Sort spill | Projection too wide; no order-aligned index | Narrow projection; add covering index |
| Cheap plan but slow wall time | Waits: locks, I/O, pool | Check `pg_stat_activity`, wait events, pool stats |

## Workflow

1. Confirm the engine, workload, symptom, and evidence available before suggesting a change.
2. Route search, lakehouse, backend-architecture, or observability-heavy work to the adjacent skill when SQL tuning is not the primary problem.
3. Gather plans, stats, and workload context before proposing indexes, rewrites, or configuration changes.
4. Change one lever at a time and verify correctness plus performance impact after each step.
5. Re-check version-sensitive behavior with the navigation references before final recommendations.

## ASCII Flow

```text
SQL performance request
  -> confirm engine, version, workload, and success metric
  -> collect evidence: query, schema, indexes, plan, waits, stats
  -> classify bottleneck
     +-- query shape or estimates -> rewrite/statistics path
     +-- missing or excess index -> index trial path
     +-- locks or deadlocks -> transaction-shape path
     +-- connections -> pool/topology path
     +-- table growth -> partition/retention path
  -> change one lever at a time
  -> verify correctness, latency, reads, locks, and rollback path
```

## Routing Guide

**If the problem is a slow query**

- Start with [template-slow-query.md](assets/cross-platform/template-slow-query.md)
- Then use:
  - PostgreSQL: [template-pg-explain.md](assets/postgres/template-pg-explain.md)
  - MySQL: [template-mysql-explain.md](assets/mysql/template-mysql-explain.md)
  - SQL Server: [template-mssql-explain.md](assets/mssql/template-mssql-explain.md)
  - Oracle: [template-oracle-explain.md](assets/oracle/template-oracle-explain.md)

**If the likely problem is cardinality or estimator drift**

- PostgreSQL: check [references/operational-patterns.md](references/operational-patterns.md) for `CREATE STATISTICS`, `pg_upgrade` statistics retention, and PG18 planner changes
- MySQL: use histograms and optimizer statistics in [references/operational-patterns.md](references/operational-patterns.md)
- SQL Server: inspect Query Store, parameter sensitivity, and OPPO in [template-mssql-explain.md](assets/mssql/template-mssql-explain.md)

**If the issue is index design**

- Start with [references/index-patterns.md](references/index-patterns.md)
- Use vendor templates:
  - PostgreSQL: [template-pg-index.md](assets/postgres/template-pg-index.md)
  - MySQL: [template-mysql-index.md](assets/mysql/template-mysql-index.md)
  - SQL Server: [template-mssql-index.md](assets/mssql/template-mssql-index.md)

**If the issue is blocking or lock waits**

- Use [template-lock-analysis.md](assets/cross-platform/template-lock-analysis.md)
- Favor transaction-shape fixes before configuration changes

**If the issue is connection pressure**

- Use [references/connection-pooling-patterns.md](references/connection-pooling-patterns.md)
- Distinguish connection helpers from actual poolers. Cloud SQL Auth Proxy and language connectors are not poolers by themselves.

**If the request is PostgreSQL tenant isolation or privilege review**

- Use [template-pg-rls.md](assets/postgres/template-pg-rls.md)
- Pair with [template-security-audit.md](assets/cross-platform/template-security-audit.md)

## Navigation and Templates

Templates live under `assets/`. Reference guides — load on demand:

- [references/explain-analysis.md](references/explain-analysis.md) — Load when reading EXPLAIN/EXPLAIN ANALYZE output: row estimates, join order, memory spills, per-engine capture commands.
- [references/index-patterns.md](references/index-patterns.md) — Load when deciding whether to add, reshape, or retire an index; covers composite, partial, covering, BRIN, invisible, and PG18 skip scan.
- [references/query-tuning-patterns.md](references/query-tuning-patterns.md) — Load when the likely fix is in the SQL itself: sargability, OR rewrites, keyset pagination, N+1 collapse, estimation fixes.
- [references/sql-best-practices.md](references/sql-best-practices.md) — Load for workload-grounded tuning defaults and safe-change workflow; useful before making production changes.
- [references/sql-antipatterns.md](references/sql-antipatterns.md) — Load during schema or query code review to detect and remediate common anti-patterns (SELECT *, N+1, EAV, non-sargable predicates).
- [references/query-optimization-research-runtime.md](references/query-optimization-research-runtime.md) — Load when a recommendation depends on version-specific engine behavior (PG18 AIO, MySQL 9.7 HyperGraph, SQL Server 2025 IQP 3.0, LITHE rewrite research).
- [references/partition-strategies.md](references/partition-strategies.md) — Load when table growth, retention, or vacuum pressure motivates partitioning; includes migration patterns and pg_partman guidance.
- [references/connection-pooling-patterns.md](references/connection-pooling-patterns.md) — Load when the symptom is connection saturation, pooler misconfiguration, or cloud-managed pool selection (PgBouncer, RDS Proxy, Supavisor, Cloud SQL).
- [references/monitoring-alerting-patterns.md](references/monitoring-alerting-patterns.md) — Load when setting up query stats, wait-event monitoring, or alert thresholds for PostgreSQL, MySQL, or SQL Server.
- [references/operational-patterns.md](references/operational-patterns.md) — Load for the production tuning workflow, safe migration checklist, or engine-specific operational cautions.

## Operating Rules

- Measure before change. A fast guess is still a guess.
- Correctness beats speed. Verify result equivalence after rewrites.
- Change one variable at a time when triaging production behavior.
- Sequential scans, hash joins, and materialization can be correct plans.
- Subqueries and CTEs are not anti-patterns by default; prove they are the bottleneck before rewriting.
- Do not add indexes just because a column appears in `WHERE`. Check workload value, write cost, and plan change.
- Treat version-sensitive behavior as volatile. For PostgreSQL 18, MySQL 9.7 LTS (or 8.4 LTS), and SQL Server 2025 features, prefer vendor docs over memory.

## Known Traps

- Tuning SQL in isolation without confirming whether the real bottleneck is missing indexes, bad cardinality estimates, lock contention, pool saturation, or ORM query shape.
- Adding indexes reactively for every slow query and degrading write throughput, autovacuum health, and cache residency.
- Testing with development-sized datasets and drawing conclusions that collapse under production row counts, skew, or tenant hot spots.
- Rewriting queries aggressively before examining actual plans with row estimates, memory usage, spill behavior, and join order.
- Treating pagination, search, or reporting queries as harmless OLTP traffic when they dominate I/O and block core transactional paths.
- Assuming one engine's plan behavior or hint strategy transfers cleanly between PostgreSQL, MySQL, and SQL Server.

## Common Anti-Patterns

- Solving all latency problems with more indexes instead of fixing query shape, access patterns, or workload isolation.
- Running large ad hoc analytics directly on the primary OLTP path when summary tables, replicas, or warehouse sync should absorb the load.
- Using `SELECT *` and ORM default eager loading in latency-sensitive request paths.
- Benchmarking single queries without concurrent load, cache-warm versus cold-path comparison, or p95 and p99 visibility.
- Keeping ineffective or duplicate indexes indefinitely because no index review or usage audit is part of routine operations.
- Treating planner hints or session-level knobs as the first-line fix instead of a last resort after query, schema, and statistics improvements.

## Related Skills

- [software-backend](../software-backend/SKILL.md) - Application query generation, ORM behavior, and API/database interaction
- [software-security-appsec](../software-security-appsec/SKILL.md) - SQL injection prevention, auth, secrets, and hardening
- [ops-devops-platform](../ops-devops-platform/SKILL.md) - Infrastructure, failover automation, and operational runbooks
- [qa-observability](../qa-observability/SKILL.md) - Telemetry, alerting, and SLO design
- [qa-debugging](../qa-debugging/SKILL.md) - Production incident debugging workflow
- [data-lake-platform](../data-lake-platform/SKILL.md) - OLAP engines, Parquet, and warehouse/lakehouse tuning

## Fact-Checking

- Verify current external facts, version behavior, and managed-service capabilities against official vendor docs before final answers.
- Prefer primary sources in [data/sources.json](data/sources.json).
- If a current fact cannot be verified, mark it as unverified and avoid prescribing a risky production change.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

