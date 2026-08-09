# Database Performance Testing

Query benchmarking, connection pool pressure testing, index validation, N+1 detection, and migration performance.

## Table of Contents

- [Query Benchmarking](#query-benchmarking)
- [Establish Query Baselines](#establish-query-baselines)
- [PostgreSQL](#postgresql)
- [MySQL](#mysql)
- [Connection Pool Pressure Testing](#connection-pool-pressure-testing)
- [What to Test](#what-to-test)
- [Pool Metrics to Monitor](#pool-metrics-to-monitor)
- [k6 with Database Monitoring](#k6-with-database-monitoring)
- [Index Effectiveness Validation](#index-effectiveness-validation)
- [Verify Indexes Are Used](#verify-indexes-are-used)
- [Test Index Performance at Scale](#test-index-performance-at-scale)
- [N+1 Query Detection](#n1-query-detection)
- [Detection Strategies](#detection-strategies)
- [ORM-Specific Detection](#orm-specific-detection)
- [Django — django-debug-toolbar or django-query-inspector](#django-—-django-debug-toolbar-or-django-query-inspector)
- [nplusone library — automatic N+1 detection](#nplusone-library-—-automatic-n1-detection)
- [pip install nplusone](#pip-install-nplusone)
- [Prevention](#prevention)
- [Migration Performance Testing](#migration-performance-testing)
- [Pre-Migration Checklist](#pre-migration-checklist)
- [Time a migration against a test database with production-scale data](#time-a-migration-against-a-test-database-with-production-scale-data)
- [For PostgreSQL — check if migration requires ACCESS EXCLUSIVE lock](#for-postgresql-—-check-if-migration-requires-access-exclusive-lock)
- [Use pg_locks monitoring during migration](#use-pglocks-monitoring-during-migration)
- [Read Replica Lag Testing](#read-replica-lag-testing)
- [What to Test](#what-to-test)
- [Monitoring Replica Lag](#monitoring-replica-lag)
- [Performance Testing Anti-Patterns](#performance-testing-anti-patterns)

## Query Benchmarking

### Establish Query Baselines

For each critical query, record:
- Execution time p50, p95, p99
- Rows examined vs rows returned (selectivity)
- Index usage (via EXPLAIN)
- Execution plan stability across data volumes

### PostgreSQL

```sql
-- Enable timing
\timing on

-- EXPLAIN ANALYZE with buffers for real execution stats
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT o.id, o.total, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.created_at > NOW() - INTERVAL '7 days'
ORDER BY o.created_at DESC
LIMIT 100;

-- Key indicators in output:
-- Seq Scan → missing index
-- Nested Loop with high row count → potential N+1 or bad join
-- Sort with external merge → insufficient work_mem
-- Buffers: shared hit vs read → cache effectiveness
```

```sql
-- pg_stat_statements — top queries by total time
SELECT
  queryid,
  calls,
  mean_exec_time::numeric(10,2) AS avg_ms,
  stddev_exec_time::numeric(10,2) AS stddev_ms,
  total_exec_time::numeric(10,2) AS total_ms,
  rows / NULLIF(calls, 0) AS avg_rows,
  query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

### MySQL

```sql
-- EXPLAIN ANALYZE (MySQL 8.0.18+)
EXPLAIN ANALYZE
SELECT o.id, o.total, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.created_at > DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY o.created_at DESC
LIMIT 100;

-- Performance Schema — top queries
SELECT
  DIGEST_TEXT,
  COUNT_STAR AS calls,
  AVG_TIMER_WAIT / 1e9 AS avg_ms,
  SUM_TIMER_WAIT / 1e9 AS total_ms,
  SUM_ROWS_EXAMINED / COUNT_STAR AS avg_rows_examined
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 20;
```

## Connection Pool Pressure Testing

Connection pool exhaustion is a common production failure under load. Test it explicitly.

### What to Test

| Scenario | How | Expected Behavior |
|----------|-----|-------------------|
| Normal load | Ramp to expected concurrency | Pool stays below max, no wait time |
| Saturation | Exceed pool max connections | Bounded wait time, then timeout error |
| Slow queries | Inject artificial query delay | Pool fills, new requests queue, timeout fires |
| Connection leak | Open connections without returning | Pool exhausts, alerts fire |
| Failover | Kill primary, observe pool behavior | Pool drains, reconnects to replica/new primary |

### Pool Metrics to Monitor

- Active connections (should stay below max)
- Idle connections
- Pending/waiting requests
- Connection wait time (p95, p99)
- Connection timeout rate
- Connection creation rate (high rate = pool churn)

### k6 with Database Monitoring

```javascript
// k6 — while running load test, monitor pool metrics via your APM
// The load test itself hits the API; database pool metrics come from
// your application's metrics endpoint or APM dashboard.

import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 50 },
    { duration: '5m', target: 50 },   // hold — pool should stabilize
    { duration: '2m', target: 200 },  // exceed expected pool capacity
    { duration: '5m', target: 200 },  // hold — expect pool saturation signals
    { duration: '2m', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};
```

## Index Effectiveness Validation

### Verify Indexes Are Used

After adding an index, verify it is actually selected by the query planner under realistic conditions.

```sql
-- PostgreSQL: check index usage stats
SELECT
  schemaname, relname, indexrelname,
  idx_scan, idx_tup_read, idx_tup_fetch
FROM pg_stat_user_indexes
WHERE schemaname = 'public'
ORDER BY idx_scan DESC;

-- Unused indexes (candidates for removal)
SELECT indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND schemaname = 'public';
```

### Test Index Performance at Scale

Indexes that work at 10K rows may not work at 10M rows. Test with production-scale data volumes.

```sql
-- Generate test data at scale
INSERT INTO orders (customer_id, total, created_at)
SELECT
  (random() * 100000)::int,
  (random() * 1000)::numeric(10,2),
  NOW() - (random() * 365)::int * INTERVAL '1 day'
FROM generate_series(1, 10000000);

-- Re-run EXPLAIN ANALYZE with realistic data volume
ANALYZE orders;
```

## N+1 Query Detection

N+1 queries cause linear scaling of database calls with result set size.

### Detection Strategies

1. **Application-level logging** — count queries per request; flag when count exceeds threshold.
2. **APM/tracing** — trace spans per request reveal repeated identical query patterns.
3. **Database slow log** — look for repeated queries with different parameters in rapid succession.
4. **Load test correlation** — if query count scales linearly with response data size, suspect N+1.

### ORM-Specific Detection

```python
# Django — django-debug-toolbar or django-query-inspector
# nplusone library — automatic N+1 detection
# pip install nplusone
INSTALLED_APPS = ['nplusone.ext.django']
MIDDLEWARE = ['nplusone.ext.django.NPlusOneMiddleware']
NPLUSONE_RAISE = True  # raise exception on N+1 in tests
```

```javascript
// Prisma — query logging
const prisma = new PrismaClient({ log: ['query'] });
// Count queries per request in tests
```

### Prevention

- **Eager loading** — `include` / `prefetch_related` / `JOIN FETCH`
- **DataLoader pattern** — batch and cache within a request lifecycle
- **Query count assertions in tests** — fail if query count exceeds expected maximum

## Migration Performance Testing

Schema migrations on large tables can lock tables for minutes or hours. Test migration duration before applying to production.

### Pre-Migration Checklist

1. Test the migration against a copy of production data (or representative volume).
2. Measure execution time and lock duration.
3. Identify blocking DDL operations (ALTER TABLE with full table rewrite).
4. Use online schema change tools for large tables:
   - PostgreSQL: `CREATE INDEX CONCURRENTLY`, `pg_repack`, or `pgroll`
   - MySQL: `pt-online-schema-change`, `gh-ost`
5. Plan rollback procedure before execution.

```bash
# Time a migration against a test database with production-scale data
time psql -d test_db -f migrations/0042_add_index.sql

# For PostgreSQL — check if migration requires ACCESS EXCLUSIVE lock
# Use pg_locks monitoring during migration
```

## Read Replica Lag Testing

For read-replica architectures, test that read-after-write consistency is handled correctly.

### What to Test

| Scenario | Expected Behavior |
|----------|-------------------|
| Write then immediate read | Read from primary or wait for replication |
| High write volume | Replica lag stays within SLO (e.g., < 1s) |
| Replica failover | Application reconnects, reads continue |
| Lag exceeds threshold | Application falls back to primary for reads |

### Monitoring Replica Lag

```sql
-- PostgreSQL: check replication lag on replica
SELECT
  now() - pg_last_xact_replay_timestamp() AS replication_lag;

-- MySQL: check seconds_behind_master
SHOW SLAVE STATUS\G
-- Look for: Seconds_Behind_Master
```

## Performance Testing Anti-Patterns

- **Testing with empty tables** — query plans differ dramatically at scale.
- **Testing without realistic data distribution** — uniform random data does not match real skew.
- **Ignoring connection pool settings** — default pool sizes rarely match production.
- **Not testing concurrent writes** — read-only benchmarks miss lock contention.
- **Testing against a local database** — network latency and connection overhead are absent.
- **Ignoring query plan changes** — the planner may choose different plans at different data volumes; re-check after bulk loads.
