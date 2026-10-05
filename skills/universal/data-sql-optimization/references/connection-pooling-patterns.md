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
- [Idle Connections Are Not Free](#idle-connections-are-not-free)
- [Evidence: Throughput and Latency vs Client Count](#evidence-throughput-and-latency-vs-client-count)
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

### Idle Connections Are Not Free

The common assumption is that an idle session costs nothing because it is not running
a query. In PostgreSQL that is wrong, for two independent reasons.

**Snapshot cost scales with total connections, not active ones.** MVCC requires every
transaction to obtain a snapshot before it starts work, and building that snapshot
means examining all open connections — the system cannot know a session is idle without
checking it. Angelakos cites Tom Lane on this: it makes *"the (computational) cost of
taking a snapshot proportional to the total number of connections"* (*PostgreSQL
Mistakes and How to Avoid Them*, §6.4.2, p. 109). An idle session therefore slows down
every *other* session's transaction start. Angelakos calls the result **snapshot
contention**.

PostgreSQL 14 improved this substantially but did not remove it: obtaining snapshots
for many incoming connections remains computationally significant, so size the pool
from measured snapshot and lock overhead rather than assuming a newer major fixed it.

**Process and lock-table overhead is unavoidable.** PostgreSQL uses a process-per-
connection model, so every connection is an OS process with its own memory,
scheduling, and IPC overhead, plus shared-memory and lock-table entries. Thousands of
mostly-idle backends risk process thrashing, where the system spends more time context
switching than executing.

There is also a latent-load hazard worth stating plainly: connections made available to
an application may all be used at once. A traffic spike against thousands of idle
connections can convert a quiet server into an overload instantly.

**The sizing heuristic.** Angelakos states it as a rule of thumb with the caveat
attached: *"As an empirical rule of thumb, you shouldn't have more PostgreSQL
connections than four times the number of your cores. But again, don't use my guidance
as canon because your optimal ratio is bound to be workload specific."* Treat `4 ×
cores` as a ceiling to start from and tune down from measurement.

Real concurrency is usually far below connection count. Angelakos notes that in the
wild, *"applications with 5,000 connections have been seen only running about 15 to 30
active tasks concurrently in the database."*

**Fix by pooling, not by timeouts.** A transaction-mode pooler (PgBouncer, Supavisor)
lets the application hold many client connections while only a small number reach
PostgreSQL. Angelakos prefers this to `idle_session_timeout`, which closes sessions out
from under clients that may not expect it. Note the distinction from
`idle_in_transaction_session_timeout`, which targets a genuinely dangerous state and is
worth setting regardless.

Watch for `wait_event_type: LWLock` in `pg_stat_activity` — Angelakos flags a lot of it
as a good indication of excessive concurrency, since lightweight locks have no fair
queuing and contended lockers slow each other down.

### Evidence: Throughput and Latency vs Client Count

Angelakos ran `pgbench` at varying client counts against a fixed server to show what
over-provisioning connections actually does. Quoted verbatim from table 6.1 (§6.3,
p. 105), **with its test conditions**, which matter because the shape of the curve is
the transferable finding, not the absolute numbers:

Conditions: PostgreSQL 17.0 (Ubuntu 17.0-1.pgdg24.04+1); a cloud compute instance with
16 GB RAM described as "modestly sized"; `shared_buffers = 1GB`, `work_mem = 4MB`,
`max_connections = 2000`; pgbench built-in TPC-B-like workload at scaling factor 1000
(a 100-million-row `pgbench_accounts`); 24 threads; 300-second runs driven from a
separate host.

| Number of clients | TPS | Latency average |
|-------------------|-------|-----------------|
| 2,000 | 352.1 | 5,535.267 ms |
| 1,500 | 506.8 | 2,869.986 ms |
| 1,000 | 586.1 | 1,694.616 ms |
| 500 | 628.4 | 794.688 ms |
| 250 | 635.7 | 392.554 ms |
| 125 | 556.9 | 224.411 ms |
| 63 | 613.0 | 102.758 ms |
| 32 | 572.3 | 55.907 ms |
| 16 | 301.8 | 53.009 ms |

How to read it:

- **Throughput plateaus; latency does not.** TPS is roughly flat from 1,500 down to 32
  clients, so a throughput-only dashboard would suggest the server handled 1,500 clients
  fine. It did not. Latency at 1,500 clients is 2.87 s versus 55.9 ms at 32 — the server
  bought that flat TPS by queueing. Angelakos: *"It was only able to sustain this TPS
  plateau by trading latency for higher concurrency."*
- **The low end is measurement, not a limit.** The 301.8 TPS at 16 clients means the
  benchmark stopped supplying enough work, not that the server got worse.
- **Do not port these numbers.** They describe one instance size, one config, and one
  synthetic workload. The transferable claim is the shape: past the server's real
  capacity, added connections buy latency, not throughput. Reproduce on your own
  hardware before quoting a client count.

This is the empirical case for the sizing principles above: pick the pool size from
where latency is still acceptable, and let the pooler queue the rest.

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
