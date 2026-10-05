# Database Monitoring and Alerting Patterns

Purpose: monitor PostgreSQL, MySQL, and SQL Server so tuning decisions come from evidence and regressions are detected quickly.

## Table of Contents

- [What to Measure First](#what-to-measure-first)
- [PostgreSQL](#postgresql)
- [Baseline Setup](#baseline-setup)
- [Core Queries](#core-queries)
- [MySQL](#mysql)
- [Baseline Setup](#baseline-setup)
- [What to Watch](#what-to-watch)
- [SQL Server](#sql-server)
- [Baseline Setup](#baseline-setup)
- [What to Watch](#what-to-watch)
- [Alerting Guidelines](#alerting-guidelines)
- [Anti-Patterns](#anti-patterns)
- [Final Check](#final-check)

## What to Measure First

| Signal | Why It Matters |
|--------|----------------|
| Query latency and throughput | Tells you where the user-facing pain is |
| Rows read vs rows returned | Separates access-path issues from raw query count |
| Waits / blocking | Prevents query-plan analysis from hiding concurrency problems |
| Connection usage and waiting clients | Detects saturation before outages |
| Replication lag | Protects reads and failover readiness |
| Bloat / dead rows / temp spills | Shows maintenance and memory pressure |

## PostgreSQL

### Baseline Setup

- enable `pg_stat_statements`
- collect from `pg_stat_activity`, `pg_locks`, `pg_stat_replication`, and `pg_stat_io`
- log slow queries with a threshold that fits the service SLO

### Core Queries

```sql
SELECT queryid, calls, total_exec_time, mean_exec_time, rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

SELECT pid, wait_event_type, wait_event, state, query
FROM pg_stat_activity
WHERE state <> 'idle';

SELECT backend_type, object, reads, writes, writebacks
FROM pg_stat_io
ORDER BY reads + writes DESC
LIMIT 20;
```

Watch for:

- query classes with high total time, not only high average time
- `idle in transaction`
- replication lag growth during write bursts
- autovacuum falling behind on hot tables

## MySQL

### Baseline Setup

- keep Performance Schema enabled
- expose sys schema views where available
- keep slow query logging or equivalent query insight enabled

### What to Watch

- top statements by total latency
- temporary tables and filesorts
- replica lag
- metadata-lock waits during DDL
- connection creation spikes during deploys or cold starts

## SQL Server

### Baseline Setup

- use Query Store for top queries, regressed plans, and plan comparison
- inspect waits and blocked sessions alongside execution plans
- monitor tempdb, memory grants, and spill-heavy queries

### What to Watch

- regressed plans in Query Store
- parameter-sensitive query variants
- lock waits and deadlocks
- tempdb pressure

## Alerting Guidelines

Use three severities:

- critical: page someone now
- warning: investigation during business hours
- info: dashboard or daily report only

Typical candidates:

- connection usage near exhaustion
- waiting clients in the pooler
- replication lag beyond read freshness tolerance
- a new slow-query class dominating total runtime
- long-running blocking transactions

## Anti-Patterns

- monitoring only CPU and connection count
- alerting on every metric without a baseline
- resetting statement stats so often that trend analysis becomes useless
- keeping dashboards without response runbooks

## Final Check

- [ ] Query stats, waits, and connection pressure are all visible
- [ ] Alerts align to service impact, not vanity thresholds
- [ ] Managed-service native metrics are used where exporters are unavailable
- [ ] Monitoring covers replicas and poolers, not only primaries
