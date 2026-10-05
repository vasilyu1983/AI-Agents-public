---
name: data-sql-optimization
description: "Diagnoses and tunes SQL for OLTP workloads on PostgreSQL, MySQL, and SQL Server. Use when tuning queries, reading plans, indexing, or fixing lock contention."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# SQL Optimization

**Out of scope:** OLAP engines and lakehouse tuning. Use [data-lake-platform](../data-lake-platform/SKILL.md) for ClickHouse, DuckDB, Doris, StarRocks, Iceberg, Delta Lake, or Hudi.

## Quick Reference

### Scripts

| Script | What it does | Usage |
|--------|-------------|-------|
| [scripts/pg_slow_query_triage.sql](scripts/pg_slow_query_triage.sql) | Six-section triage report from `pg_stat_statements`: total time, mean time, I/O, variance, cache-hit ratio, and spills/planning/WAL | Copy-paste into `psql` or any SQL client; requires `pg_stat_statements` extension |
| [scripts/explain_collector.py](scripts/explain_collector.py) | Collects estimated JSON plans via `psql`; `--analyze` opts into query execution | `DATABASE_URL=postgresql://... python explain_collector.py --queries slow.txt` |
| [scripts/test_explain_collector.py](scripts/test_explain_collector.py) | Offline input, execution-mode and JSON-envelope regressions | `python scripts/test_explain_collector.py` |

```bash
# Triage: paste directly into psql
psql "$DATABASE_URL" -f skills/universal/data-sql-optimization/scripts/pg_slow_query_triage.sql

# Collect estimated plans for reviewed queries (default):
python scripts/explain_collector.py --queries queries.txt --no-analyze --output plans.jsonl

# Collect actual plans (executes queries — review side effects first):
DATABASE_URL=postgresql://user:pass@test-db:5432/db \
  python scripts/explain_collector.py --queries queries.txt --analyze --output plans.jsonl
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
| Backup and recovery design | [references/recovery-strategy-design.md](references/recovery-strategy-design.md) | You need a recovery capability mapped to failure scenarios, not just a backup job |
| Security or RLS review | [template-security-audit.md](assets/cross-platform/template-security-audit.md) | You are reviewing least privilege, SQL injection controls, or tenant isolation |

## Coverage Model

| Engine | Status | Notes |
|--------|--------|-------|
| PostgreSQL | Primary | Deepest coverage. Version-gated features used here (skip scan, AIO, `uuidv7()`, statistics kept across `pg_upgrade`) arrived in PostgreSQL 18 |
| MySQL | Primary | Recommend an LTS line, not an Innovation release, for production. Check whether the HyperGraph optimizer is on by default in the user's version before relying on its plans |
| SQL Server | Primary | Use Query Store for plan regressions; IQP features have different release and compatibility prerequisites. Check the [Microsoft feature matrix](https://learn.microsoft.com/en-us/sql/relational-databases/performance/intelligent-query-processing?view=sql-server-ver17) for the exact feature before recommending it |
| Oracle | Secondary | Use templates and official docs for optimizer-specific edge cases |
| SQLite | Secondary | Focus on indexes, planner behavior, WAL, and `PRAGMA optimize` |

Version lookups: take the user's exact version from `SELECT version()` (or `@@version`) first; current minor releases are in [data/versions.json](data/versions.json) (`postgresql`, `mysql`), refreshed by script. For which majors or LTS lines are supported and when each reaches end of life, read the vendor's versioning or support-policy page; plan an upgrade before the line in use reaches EOL. Before recommending a feature from a newer major, confirm in the release notes that the major is GA; do not recommend beta-only features for production.

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

Start with an estimated plan. Use actual-plan capture only after reviewing the statement, functions and triggers: `ANALYZE` executes it, and rollback does not undo sequence changes or external effects. The collector accepts one line per statement and rejects internal semicolons, including inside literals/comments.

```sql
-- PostgreSQL: estimated plan first; opt into ANALYZE for reviewed execution
EXPLAIN (VERBOSE, FORMAT TEXT) <query>;

-- MySQL: get JSON plan for detailed cost breakdown
EXPLAIN FORMAT=JSON <query>;

-- SQL Server: turn on I/O and CPU evidence
SET STATISTICS IO, TIME ON;
<query>;
```

| Step | What to Check | Red Flag |
|------|---------------|----------|
| 1 | Operator time and loops | Parent times include child work; do not sum them or treat cost units as milliseconds |
| 2 | Rows estimated vs rows actual | Ratio >10x in either direction |
| 3 | Loops * rows per loop = total rows processed | High total even if one loop looks cheap |
| 4 | Shared hit vs read buffers (PostgreSQL) | `reads` >> `hits` on a hot query |
| 5 | Sort or hash spill | `Sort Method: external merge`, `Hash Batches > 1` |
| 6 | Key/bookmark lookup on hot path | Many per parent row; add INCLUDE columns |
| 7 | Nested loop outer rows × inner work | Check estimates and repeated inner scans before choosing a join strategy |
| 8 | Waiting time >> execution time | Investigate locks or pool saturation, not the plan |

**Bottleneck decision table:**

| Plan shows | Likely cause | First lever |
|-----------|-------------|-------------|
| Seq scan, high rows-read/rows-returned | Missing/unusable index or valid scan choice | Check selectivity and sargability; compare an index trial |
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

### Production Change Gate

Choose proof and rollback by the change being made:

| Change | Trial | Rollback trigger | Rollback |
|---|---|---|---|
| Query rewrite | Replay representative parameters and concurrency; compare result sets | Wrong rows or worse p95/reads/locks | Revert query or feature flag |
| New index | Build with the engine's online/concurrent path where available; confirm chosen plans | Write latency, lock time, or storage exceeds budget | Drop with the safe online path after dependents are checked |
| Statistics change | Capture plans before/after across skewed values | Regression for another parameter class | Restore target/statistics setting and analyze |
| Pool/config change | Canary one service or pool; watch waits and saturation | Queueing, timeouts, or connection churn rises | Restore prior value and recycle only affected pools |
| Partition/schema change | Rehearse on production-shaped data and verify dual reads/writes | Row-count mismatch, blocked writers, or replication lag | Stop cutover and return traffic to old path |

Do not declare a tuning win from one warm-cache execution. Record correctness, p50/p95/p99, logical/physical reads, CPU, locks, and write impact over the same workload window; name any metric that could not be measured.

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

Load cross-engine worksheets only when documenting the corresponding decision:

| Decision | Template |
|---|---|
| Multi-symptom incident diagnosis | [diagnostics](assets/cross-platform/template-diagnostics.md) |
| Rewrite and result-equivalence review | [query tuning](assets/cross-platform/template-query-tuning.md) |
| New schema or integrity review | [schema design](assets/cross-platform/template-schema-design.md) |
| Record baseline, experiment and verification | [tuning worksheet](assets/cross-platform/template-performance-tuning-worksheet.md) |
| Record a plan review across engines | [EXPLAIN analysis](assets/cross-platform/template-explain-analysis.md) |
| Record index trial and write impact | [index design](assets/cross-platform/template-index.md) |
| Rehearse schema rollout and rollback | [migration](assets/cross-platform/template-migration.md) |
| Rehearse recovery and verify recovered data | [backup/restore](assets/cross-platform/template-backup-restore.md) |
| Plan replication topology, lag, and failover | [MySQL replication/HA](assets/mysql/template-replication-ha.md), [PostgreSQL replication/HA](assets/postgres/template-replication-ha.md) |
| Tune an embedded SQLite workload | [SQLite optimization](assets/sqlite/template-sqlite-optimization.md) |

Reference guides — load on demand:

- [references/explain-analysis.md](references/explain-analysis.md) — Load when reading EXPLAIN/EXPLAIN ANALYZE output: row estimates, join order, memory spills, per-engine capture commands.
- [references/index-patterns.md](references/index-patterns.md) — Load when deciding whether to add, reshape, or retire an index; covers composite, partial, covering, BRIN, invisible, and PG18 skip scan.
- [references/query-tuning-patterns.md](references/query-tuning-patterns.md) — Load when the likely fix is in the SQL itself: sargability, OR rewrites, keyset pagination, N+1 collapse, estimation fixes.
- [references/sql-best-practices.md](references/sql-best-practices.md) — Load for workload-grounded tuning defaults and safe-change workflow; useful before making production changes.
- [references/sql-antipatterns.md](references/sql-antipatterns.md) — Load during schema or query code review to detect and remediate common anti-patterns (SELECT *, N+1, EAV, non-sargable predicates).
- [references/query-optimization-research-runtime.md](references/query-optimization-research-runtime.md) — Load when a recommendation depends on version-specific engine behavior (PG18 AIO, MySQL HyperGraph, SQL Server 2025 IQP, LITHE rewrite research).
- [references/partition-strategies.md](references/partition-strategies.md) — Load when table growth, retention, or vacuum pressure motivates partitioning; includes migration patterns and pg_partman guidance.
- [references/connection-pooling-patterns.md](references/connection-pooling-patterns.md) — Load when the symptom is connection saturation, pooler misconfiguration, or cloud-managed pool selection (PgBouncer, RDS Proxy, Supavisor, Cloud SQL).
- [references/monitoring-alerting-patterns.md](references/monitoring-alerting-patterns.md) — Load when setting up query stats, wait-event monitoring, or alert thresholds for PostgreSQL, MySQL, or SQL Server.
- [references/operational-patterns.md](references/operational-patterns.md) — Load for the production tuning workflow, safe migration checklist, engine-specific operational cautions, `work_mem` sizing, idle-in-transaction lock cascades, and online schema change tooling (gh-ost vs pt-osc).
- [references/recovery-strategy-design.md](references/recovery-strategy-design.md) — Load when designing or reviewing backup and recovery: failure-scenario taxonomy, detection per failure class, storage tiering, recovery testing as a deliverable.

Primary sources live in [data/sources.json](data/sources.json).

## Known Traps

- Sequential scans, hash joins, materialization, subqueries and CTEs can be correct choices. Require plan evidence before rewriting.
- Each added index increases write and maintenance work. Check overlapping indexes and measure write impact alongside read gains.
- Development data hides production skew and tenant hot spots; compare representative parameters under concurrency.
- Planner hints and session knobs are diagnostic experiments after query, schema and statistics checks; do not transfer hints across engines.

## Related Skills

- [software-backend](../software-backend/SKILL.md) - Application query generation, ORM behavior, and API/database interaction
- [software-security-appsec](../software-security-appsec/SKILL.md) - SQL injection prevention, auth, secrets, and hardening
- [ops-devops-platform](../ops-devops-platform/SKILL.md) - Infrastructure, failover automation, and operational runbooks
- [qa-observability](../qa-observability/SKILL.md) - Telemetry, alerting, and SLO design
- [qa-debugging](../qa-debugging/SKILL.md) - Production incident debugging workflow
- [data-lake-platform](../data-lake-platform/SKILL.md) - OLAP engines, Parquet, and warehouse/lakehouse tuning

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
