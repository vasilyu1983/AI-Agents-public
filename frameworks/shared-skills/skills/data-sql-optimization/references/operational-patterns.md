# Operational Patterns and Standards

Operational guidance for production tuning and safe database changes. This file focuses on PostgreSQL, MySQL, and SQL Server. Oracle and SQLite remain lighter-support paths.

## Table of Contents

- [Production Tuning Workflow](#production-tuning-workflow)
- [PostgreSQL 18 Operational Notes](#postgresql-18-operational-notes)
- [New Features Worth Knowing](#new-features-worth-knowing)
- [Planner and Estimation](#planner-and-estimation)
- [Operational Cautions](#operational-cautions)
- [MySQL 9.7 LTS Operational Notes](#mysql-97-lts-operational-notes-ga-2026-04-21)
- [Optimizer and Statistics](#optimizer-and-statistics)
- [Reliability and Change Safety](#reliability-and-change-safety)
- [SQL Server 2025 Operational Notes](#sql-server-2025-operational-notes-ga-2025-11-18)
- [Parameter-Sensitive Workloads](#parameter-sensitive-workloads)
- [Concurrency](#concurrency)
- [Shared Operational Defaults](#shared-operational-defaults)
- [Statistics Before Indexes](#statistics-before-indexes)
- [Safe Migrations](#safe-migrations)
- [Reliability Drills](#reliability-drills)
- [Template Selection](#template-selection)
- [Anti-Patterns](#anti-patterns)
- [Final Check](#final-check)

## Production Tuning Workflow

1. Measure baseline latency, reads, CPU, waits, and result size.
2. Capture plan evidence with the engine-appropriate tool.
3. Write the bottleneck hypothesis.
4. Change one variable.
5. Verify performance and result correctness.
6. Monitor long enough to catch low-frequency workloads.

Use [template-performance-tuning-worksheet.md](../assets/cross-platform/template-performance-tuning-worksheet.md) to keep the loop explicit.

## PostgreSQL 18 Operational Notes

### New Features Worth Knowing

- async I/O is a PostgreSQL 18 capability; verify whether it is enabled and relevant before attributing gains to it
- `pg_aios` exists for async-I/O observability
- `uuidv7()` gives time-ordered UUIDs with better index locality than UUIDv4 in append-heavy OLTP patterns
- `pg_upgrade` retains optimizer statistics, which reduces post-upgrade plan churn

### Planner and Estimation

- PostgreSQL 18 skip scan improves some multicolumn B-tree cases; verify with plan output instead of assuming the composite index is now enough
- `CREATE STATISTICS` is still the preferred fix for correlated-predicate misestimation
- use `pg_stat_statements` plus `pg_stat_io` when latency and I/O stories disagree

### Operational Cautions

- avoid unbounded replication-slot retention
- monitor autovacuum lag, freeze age, and table bloat
- do not replace query-shape fixes with blanket `work_mem` increases

## MySQL 9.7 LTS Operational Notes (GA 2026-04-21)

MySQL 9.7.0 is the current LTS; MySQL 8.4 LTS remains supported. Both are production-grade.

### Optimizer and Statistics

- histograms help when skewed distributions confuse the optimizer
- invisible indexes are the safest way to test index removal
- OR predicates may be handled by index merge; verify before rewriting to UNION or UNION ALL
- HyperGraph optimizer is available in 9.7 but not enabled by default; test at session scope before any global change

```sql
-- Enable HyperGraph optimizer for a session (MySQL 9.7+)
SET optimizer_switch='hypergraph_optimizer=on';
-- Verify with EXPLAIN (will show "hypergraph" in output)
```

### Reliability and Change Safety

- keep slow query log or Performance Schema visibility enabled
- use `gh-ost` or `pt-online-schema-change` for large-table DDL where blocking risk matters
- monitor binlog retention and replica lag as part of change planning

## SQL Server 2025 Operational Notes (GA 2025-11-18)

### Parameter-Sensitive Workloads

- IQP 3.0 includes DOP Feedback and CE Feedback for expressions — active by default at compatibility level 170
- OPPO (Optional Parameter Plan Optimization) replaces manual hint-based workarounds for optional-parameter queries; check database compatibility level and `OPTIONAL_PARAMETER_OPTIMIZATION` database-scoped config before assuming it is active

### Concurrency

- Optimized locking reduces lock memory and blocking risk; verify prerequisites and isolation settings before recommending it
- Query Store should be part of the default incident workflow for plan regressions
- Readable-secondary Query Store can preserve plan history outside the primary

## Shared Operational Defaults

### Statistics Before Indexes

Prefer this order:

1. refresh or validate statistics
2. inspect parameter sensitivity
3. add or reshape indexes only if the access path still looks wrong

### Safe Migrations

- capture rollback path before DDL
- stage large-table changes
- validate row counts and critical query plans after the change
- pair schema changes with connection-pool and lock-risk checks

### Reliability Drills

- [ ] restore backups on a schedule
- [ ] test replica promotion or failover with a written runbook
- [ ] track storage growth, WAL/binlog growth, and replication lag
- [ ] set alerts for latency, error rate, connection pressure, and blocking

## Template Selection

| Problem | Template |
|---------|----------|
| Slow query intake | [template-slow-query.md](../assets/cross-platform/template-slow-query.md) |
| Plan review | [template-explain-analysis.md](../assets/cross-platform/template-explain-analysis.md) or engine-specific explain template |
| Index review | [template-index.md](../assets/cross-platform/template-index.md) or engine-specific index template |
| Locking / deadlocks | [template-lock-analysis.md](../assets/cross-platform/template-lock-analysis.md) |
| Migration planning | [template-migration.md](../assets/cross-platform/template-migration.md) |
| Backup / restore drill | [template-backup-restore.md](../assets/cross-platform/template-backup-restore.md) |
| Security / privilege review | [template-security-audit.md](../assets/cross-platform/template-security-audit.md) |

## Anti-Patterns

- using engine-version features without checking version and compatibility level
- dropping indexes based only on one day's usage
- treating planner improvements as a substitute for real workload validation
- changing query shape, index design, and memory knobs all at once
- tuning from synthetic tiny datasets

## Final Check

- [ ] Recommendation is tied to observed evidence
- [ ] Version-sensitive features checked against vendor docs
- [ ] Rollback path documented for risky changes
- [ ] Monitoring exists for the thing being changed
