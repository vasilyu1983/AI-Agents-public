# Connection Pooling Patterns

Purpose: choose the right pooler, size it conservatively, and avoid feature mismatches that turn pooling into a hidden outage source.

## Table of Contents

- [Decision Guide](#decision-guide)
- [PostgreSQL: PgBouncer Modes](#postgresql-pgbouncer-modes)
- [Transaction Pooling Feature Notes](#transaction-pooling-feature-notes)
- [Cloud-Specific Rules](#cloud-specific-rules)
- [Google Cloud SQL](#google-cloud-sql)
- [AWS RDS / Aurora](#aws-rds-aurora)
- [Supabase](#supabase)
- [Sizing Principles](#sizing-principles)
- [Practical Starting Points](#practical-starting-points)
- [Monitoring](#monitoring)
- [PgBouncer](#pgbouncer)
- [PostgreSQL](#postgresql)
- [MySQL / ProxySQL](#mysql-proxysql)
- [Anti-Patterns](#anti-patterns)
- [Verification Checklist](#verification-checklist)

## Decision Guide

| Situation | Preferred Choice | Notes |
|-----------|------------------|-------|
| Self-managed PostgreSQL | PgBouncer | Default answer for most OLTP applications |
| AWS RDS / Aurora PostgreSQL or MySQL | RDS Proxy or PgBouncer | RDS Proxy is strong for bursty or serverless workloads |
| Google Cloud SQL | Application pool plus Managed Connection Pooling when needed | Auth Proxy and language connectors help connectivity, not pooling |
| Supabase PostgreSQL | Supavisor | Use transaction mode for request/response traffic and session mode for migrations or session features |
| MySQL with read/write routing needs | ProxySQL | Adds routing, multiplexing, and query rules |
| Application-only pooling | HikariCP, SQLAlchemy pool, `pg.Pool`, `database/sql`, ADO.NET | Still size from database capacity, not thread count |

## PostgreSQL: PgBouncer Modes

| Mode | Good For | Watch Outs |
|------|----------|------------|
| Session | Migrations, LISTEN/NOTIFY, temp tables, session-level locks | Highest connection cost |
| Transaction | Standard web traffic and API workloads | Session features do not survive checkout/checkin |
| Statement | Very simple autocommit workloads | Rarely the right default |

### Transaction Pooling Feature Notes

According to the PgBouncer feature matrix:

- prepared statements can work in transaction mode when `max_prepared_statements > 0`
- session-scoped behaviors still need session pooling:
  - LISTEN/NOTIFY
  - session-level advisory locks
  - temp tables that must survive across transactions
  - long-lived `SET` state

Do not describe transaction pooling as "no prepared statements" without checking the PgBouncer version and configuration.

## Cloud-Specific Rules

### Google Cloud SQL

- Cloud SQL Auth Proxy and language connectors are connection helpers, not poolers.
- Use an application pool first.
- Add **Managed Connection Pooling** when connection churn or serverless fan-out makes direct pooling insufficient.

### AWS RDS / Aurora

- RDS Proxy is a good default for Lambda, Fargate, or workloads with bursty connection creation.
- PgBouncer still gives more explicit control over PostgreSQL feature compatibility.

### Supabase

- Supavisor transaction endpoints fit request/response traffic.
- Use session mode for migrations, long transactions, and session-bound features.

## Sizing Principles

- Leave headroom on the database for admin sessions, maintenance, and replication.
- Keep application pools smaller than people first guess; scale after measuring waiting clients and queue time.
- Size from **concurrent in-flight queries**, not from web worker count or request rate alone.
- For serverless, assume connection churn is the primary risk.

### Practical Starting Points

| Workload | App Pool | Server Pooler | Database `max_connections` |
|----------|----------|---------------|-----------------------------|
| Single API service | 10-20 | 20-40 | 100-150 |
| Multiple app instances | 10-30 per instance | 50-120 | 150-300 |
| Bursty/serverless | keep app-side pooling minimal | 50-150 | 100-250 |

These are starting points, not formulas. Tune from waiting clients, saturation, and tail latency.

## Monitoring

### PgBouncer

```sql
SHOW POOLS;
SHOW STATS;
SHOW SERVERS;
SHOW CLIENTS;
```

Watch:

- `cl_waiting` sustained above zero
- `sv_active` near pool limits
- spikes in login/auth failures
- long-lived `idle in transaction` sessions on the database side

### PostgreSQL

```sql
SELECT state, count(*)
FROM pg_stat_activity
GROUP BY state
ORDER BY count(*) DESC;

SELECT pid, application_name, now() - xact_start AS tx_age, state, query
FROM pg_stat_activity
WHERE state = 'idle in transaction'
ORDER BY tx_age DESC;
```

### MySQL / ProxySQL

- check active frontend/backend connection counts
- track waits on free connections
- correlate pool exhaustion with slow query or metadata-lock spikes

## Anti-Patterns

- treating connectivity tooling as if it were pooling
- using session pooling for ordinary stateless web traffic
- maxing both the app pool and the server pooler, causing double-pooling waste
- ignoring session-bound features before switching to transaction pooling
- sizing solely from CPU cores or thread counts
- no alerting on waiting clients or idle-in-transaction sessions

## Verification Checklist

- [ ] Pooler choice matches the engine and managed-service environment
- [ ] Feature compatibility checked for prepared statements, temp tables, LISTEN/NOTIFY, and advisory locks
- [ ] Database headroom reserved for admin and maintenance
- [ ] Waiting-client and saturation metrics available
- [ ] Rollback path exists for pool-mode changes
