# Database Performance Testing

Connection pool pressure testing, read replica lag testing, and performance testing anti-patterns.

## Table of Contents

- [Connection Pool Pressure Testing](#connection-pool-pressure-testing)
- [What to Test](#what-to-test)
- [Pool Metrics to Monitor](#pool-metrics-to-monitor)
- [k6 with Database Monitoring](#k6-with-database-monitoring)
- [Read Replica Lag Testing](#read-replica-lag-testing)
- [What to Test](#what-to-test-1)
- [Monitoring Replica Lag](#monitoring-replica-lag)
- [Performance Testing Anti-Patterns](#performance-testing-anti-patterns)

What this skill owns: connection-pool pressure testing under concurrent load, read-replica lag testing during sustained writes, and testing anti-patterns. Query-level diagnosis (EXPLAIN ANALYZE, pg_stat_statements, index effectiveness, N+1 detection, and migration/DDL lock behavior) is owned by [data-sql-optimization](../../data-sql-optimization/SKILL.md) — read it for the current recipe rather than duplicating it here.

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
-- PostgreSQL: age of last replayed transaction, not complete replication lag
SELECT
  now() - pg_last_xact_replay_timestamp() AS last_replay_age;

-- MySQL 8.0.22+: check replica lag (terminology changed from SHOW SLAVE STATUS)
SHOW REPLICA STATUS\G
-- Look for: Seconds_Behind_Source

-- MySQL < 8.0.22: use the legacy command and column name
SHOW SLAVE STATUS\G
-- Look for: Seconds_Behind_Master
```

Timestamp age grows while a fully caught-up primary is idle. Compare primary/receiver/replay WAL positions and test write-to-read visibility; do not treat a NULL value as zero lag ([PostgreSQL functions](https://www.postgresql.org/docs/current/functions-admin.html)). MySQL `SHOW REPLICA STATUS` dates from 8.0.22, not 8.4; `Seconds_Behind_Source` can read zero with a slow receiver or NULL with stopped threads, so include receiver/applier health ([MySQL reference](https://dev.mysql.com/doc/refman/8.0/en/show-replica-status.html)).

## Performance Testing Anti-Patterns

- **Testing with empty tables** — query plans differ dramatically at scale.
- **Testing without realistic data distribution** — uniform random data does not match real skew.
- **Ignoring connection pool settings** — default pool sizes rarely match production.
- **Not testing concurrent writes** — read-only benchmarks miss lock contention.
- **Testing against a local database** — network latency and connection overhead are absent.
- **Ignoring query plan changes** — the planner may choose different plans at different data volumes; re-check after bulk loads.
