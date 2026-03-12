# Connection Pooling Patterns

> Purpose: Operational guide for configuring and managing database connection pools — PgBouncer, ProxySQL, application-level poolers, sizing formulas, monitoring, troubleshooting, and cloud-specific patterns. Freshness anchor: Q1 2026.

---

## Decision Tree: Choosing a Connection Pooler

```
START: What database are you using?
│
├─ PostgreSQL
│   │
│   ├─ Need lightweight, dedicated pooler?
│   │   └─ PgBouncer (most common, battle-tested)
│   │
│   ├─ Need connection pooling + load balancing + query routing?
│   │   └─ Pgpool-II (heavier, more features)
│   │
│   ├─ Using AWS RDS/Aurora?
│   │   └─ RDS Proxy (managed, IAM auth support)
│   │
│   ├─ Using GCP Cloud SQL?
│   │   └─ Cloud SQL Auth Proxy (managed, IAM)
│   │
│   └─ Using Supabase?
│       └─ Built-in PgBouncer (Supavisor in 2026)
│
├─ MySQL
│   │
│   ├─ Need query routing + read/write splitting?
│   │   └─ ProxySQL
│   │
│   ├─ Using AWS RDS/Aurora?
│   │   └─ RDS Proxy
│   │
│   └─ Application-only?
│       └─ Application-level pool (HikariCP, SQLAlchemy)
│
└─ Application-level only (any database)
    ├─ Java/Kotlin → HikariCP
    ├─ Python → SQLAlchemy pool / asyncpg pool
    ├─ Node.js → pg-pool / knex pool
    ├─ Go → database/sql (built-in pool)
    └─ .NET → ADO.NET (built-in pool)
```

---

## Quick Reference: Pooler Comparison (2026)

| Pooler | Database | Mode | Overhead | Features | License |
|--------|----------|------|----------|----------|---------|
| PgBouncer | PostgreSQL | Transaction/Session/Statement | Very low (~2KB/conn) | Pool, auth passthrough | ISC |
| Pgpool-II | PostgreSQL | All | Medium | Pool, LB, replication, query cache | BSD |
| ProxySQL | MySQL | Connection multiplexing | Low | Pool, routing, query rules | GPL |
| RDS Proxy | PG/MySQL | Managed | N/A (managed) | Pool, IAM auth, failover | AWS |
| Cloud SQL Proxy | PG/MySQL | Managed | Low | IAM auth, encryption | Google |
| HikariCP | Any (JDBC) | Application-level | Low | Fast, leak detection | Apache 2.0 |
| SQLAlchemy Pool | Any (Python) | Application-level | Low | Configurable, events | MIT |

---

## PgBouncer

### Pooling Modes

| Mode | Session Lifetime | Prepared Statements | Use When |
|------|-----------------|-------------------|----------|
| **Transaction** | Per-transaction | Not supported (use `DEALLOCATE ALL`) | Most applications (recommended) |
| **Session** | Per-client session | Supported | Apps using prepared statements, SET commands |
| **Statement** | Per-statement | Not supported | Simple autocommit queries only |

### Configuration

```ini
# /etc/pgbouncer/pgbouncer.ini

[databases]
# database = host=... port=... dbname=...
myapp = host=db-primary.internal port=5432 dbname=myapp
myapp_ro = host=db-replica.internal port=5432 dbname=myapp

[pgbouncer]
# Listening
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

# Pool sizing
pool_mode = transaction
default_pool_size = 20          # connections per user/db pair
min_pool_size = 5               # pre-warmed connections
reserve_pool_size = 5           # overflow connections
reserve_pool_timeout = 3        # seconds before using reserve pool

# Limits
max_client_conn = 1000          # max client connections to PgBouncer
max_db_connections = 100        # max connections TO the database (total)
max_user_connections = 50       # max connections per user

# Timeouts
server_idle_timeout = 600       # close idle server connections after 10min
client_idle_timeout = 0         # 0 = no timeout for idle clients
server_connect_timeout = 15     # timeout for new server connections
query_timeout = 300             # kill queries running >5min
client_login_timeout = 60       # timeout for client auth

# Logging
log_connections = 1
log_disconnections = 1
log_pooler_errors = 1
stats_period = 60               # stats logging interval
```

### Auth File

```
# /etc/pgbouncer/userlist.txt
# "username" "password_or_md5"
"myapp_user" "md5abc123..."
"readonly_user" "md5def456..."
```

### PgBouncer with Transaction Mode Gotchas

| Feature | Works in Transaction Mode? | Workaround |
|---------|--------------------------|------------|
| Prepared statements | No | Use `DEALLOCATE ALL` on checkout; or use session mode |
| SET commands (e.g., `SET search_path`) | No (resets per-tx) | Use per-query `SET LOCAL` or fully qualify schemas |
| LISTEN/NOTIFY | No | Use session mode for LISTEN connections |
| Advisory locks | No (session-level) | Use session mode or table-level locks |
| Temp tables | No (session-level) | Use CTEs or regular tables with cleanup |
| COPY | Yes | Works in transaction mode |

---

## Pgpool-II

- **Use when**: Need read/write splitting, load balancing across replicas, or watchdog HA
- **Key settings**: `num_init_children` (pool size), `max_pool` (conns per child), `load_balance_mode = on`
- **Read/write splitting**: `statement_level_load_balance = on` routes SELECT to replicas, writes to primary
- **Backend weights**: Assign higher `backend_weight` to replicas for read-heavy workloads

---

## ProxySQL (MySQL)

### Configuration

```sql
-- ProxySQL admin interface (port 6032)

-- Add backend servers
INSERT INTO mysql_servers (hostgroup_id, hostname, port, weight)
VALUES
  (10, 'mysql-primary.internal', 3306, 1000),    -- writer
  (20, 'mysql-replica1.internal', 3306, 1000),    -- reader
  (20, 'mysql-replica2.internal', 3306, 1000);    -- reader

-- Query routing rules
INSERT INTO mysql_query_rules (rule_id, match_pattern, destination_hostgroup, apply)
VALUES
  (1, '^SELECT .* FOR UPDATE', 10, 1),            -- FOR UPDATE → primary
  (2, '^SELECT', 20, 1),                          -- reads → replicas
  (3, '.*', 10, 1);                               -- everything else → primary

-- Connection pool settings
UPDATE global_variables SET variable_value='2000'
  WHERE variable_name='mysql-max_connections';
UPDATE global_variables SET variable_value='true'
  WHERE variable_name='mysql-multiplexing';

-- Apply changes
LOAD MYSQL SERVERS TO RUNTIME;
LOAD MYSQL QUERY RULES TO RUNTIME;
SAVE MYSQL SERVERS TO DISK;
SAVE MYSQL QUERY RULES TO DISK;
```

---

## Application-Level Pooling

### HikariCP (Java/Kotlin)

```yaml
# application.yml (Spring Boot)
spring:
  datasource:
    hikari:
      minimum-idle: 5
      maximum-pool-size: 20
      idle-timeout: 300000        # 5 min
      max-lifetime: 1800000       # 30 min
      connection-timeout: 30000   # 30 sec
      leak-detection-threshold: 60000  # warn if connection held >60s
      pool-name: "myapp-pool"
      connection-test-query: "SELECT 1"
```

### SQLAlchemy Pool (Python)

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@pgbouncer:6432/myapp",
    pool_size=10,               # steady-state connections
    max_overflow=20,            # burst connections
    pool_timeout=30,            # wait for connection timeout (seconds)
    pool_recycle=1800,          # recycle connections after 30 min
    pool_pre_ping=True,         # validate connection before use
    echo_pool="debug",         # log pool events (dev only)
)
```

### Node.js pg-pool

```javascript
const { Pool } = require("pg");

const pool = new Pool({
  host: "pgbouncer.internal",
  port: 6432,
  database: "myapp",
  user: "myapp_user",
  password: process.env.DB_PASSWORD,
  max: 20,                     // max connections in pool
  idleTimeoutMillis: 30000,    // close idle after 30s
  connectionTimeoutMillis: 5000, // timeout waiting for connection
  maxUses: 7500,               // close after N uses (prevent leaks)
});

// Health check
pool.on("error", (err) => {
  console.error("Unexpected pool error:", err);
});
```

---

## Pool Sizing Formulas

```
# PostgreSQL max_connections
max_connections = (available_RAM_MB - shared_buffers_MB - OS_reserved_MB) / per_connection_MB
# per_connection_MB ≈ 5-10 MB; practical limit: 200-500

# PgBouncer pool size
default_pool_size = max_db_connections / number_of_user_db_pairs
# Leave headroom: max_db_connections = postgres max_connections - 10

# Application pool size
app_pool_size = expected_concurrent_queries + (avg_query_time_ms / 1000) * requests_per_second
# Minimum: 2 * CPU_cores (CPU-bound) | Maximum: 10 * CPU_cores (IO-bound)
```

### Sizing Quick Reference

| Workload | App Pool | PgBouncer Pool | DB max_connections |
|----------|----------|---------------|-------------------|
| Small (1 app, <100 RPS) | 10-20 | 20-30 | 100 |
| Medium (3 apps, <500 RPS) | 15-30 each | 50-100 | 200 |
| Large (10+ apps, >1000 RPS) | 20-50 each | 100-200 | 300-500 |
| Serverless (Lambda/Cloud Functions) | N/A | 50-100 | 100-200 |

---

## Monitoring

### Key Metrics

| Metric | Alert Threshold | Query (PgBouncer) |
|--------|----------------|-------------------|
| Active connections | >80% of pool | `SHOW POOLS` → `sv_active` |
| Waiting clients | >0 sustained | `SHOW POOLS` → `cl_waiting` |
| Idle connections | <min_pool_size | `SHOW POOLS` → `sv_idle` |
| Average query time | >p99 baseline | `SHOW STATS` → `avg_query_time` |
| Total queries/sec | Sudden drop or spike | `SHOW STATS` → `avg_req` |
| Connection errors | >0 | `SHOW STATS` → `total_login_time` |

### PgBouncer Monitoring Queries

```sql
-- Connect to PgBouncer admin database
-- psql -h pgbouncer -p 6432 -U admin pgbouncer

-- Pool status
SHOW POOLS;
-- Columns: database, user, cl_active, cl_waiting, sv_active, sv_idle, sv_used, pool_mode

-- Connection statistics
SHOW STATS;
-- Columns: database, total_xact_count, total_query_count, total_received, total_sent, avg_xact_time, avg_query_time

-- Active server connections
SHOW SERVERS;

-- Active client connections
SHOW CLIENTS;

-- Memory usage
SHOW MEM;
```

### PostgreSQL Connection Monitoring

```sql
-- Current connections by state
SELECT state, COUNT(*) AS connections,
  ROUND(100.0 * COUNT(*) / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections'), 1) AS pct_of_max
FROM pg_stat_activity GROUP BY state ORDER BY connections DESC;

-- Long-running idle-in-transaction connections (potential leaks)
SELECT pid, application_name, state, NOW() - state_change AS duration, query
FROM pg_stat_activity
WHERE state = 'idle in transaction' AND NOW() - state_change > INTERVAL '5 minutes'
ORDER BY duration DESC;
```

---

## Troubleshooting Connection Exhaustion

### Symptoms and Causes

| Symptom | Likely Cause | Investigation |
|---------|-------------|---------------|
| "too many connections" from database | Pool size exceeds max_connections | Check `SHOW POOLS` sv_active vs max_db_connections |
| "connection pool exhausted" from app | App pool too small or connections not returned | Check for connection leaks (idle in transaction) |
| Clients waiting in PgBouncer | Database connections saturated | Check `SHOW POOLS` cl_waiting; increase pool or optimize queries |
| Intermittent connection timeouts | Burst traffic exceeds pool | Add reserve_pool; increase max_client_conn |
| Connections stuck "idle in transaction" | Application not committing/rolling back | Set `idle_in_transaction_session_timeout` in PostgreSQL |
| All connections active, none idle | Pool too small for workload | Increase pool size or optimize query concurrency |

### Emergency Response Checklist

- [ ] Check `SHOW POOLS` for waiting clients and active server connections
- [ ] Check PostgreSQL `pg_stat_activity` for idle-in-transaction sessions
- [ ] Kill long-running idle-in-transaction: `SELECT pg_terminate_backend(pid)`
- [ ] Check application logs for connection leak stack traces
- [ ] Temporarily increase `reserve_pool_size` in PgBouncer
- [ ] If needed, reload PgBouncer: `RELOAD;` (does not drop connections)
- [ ] Long-term: set `idle_in_transaction_session_timeout = '5min'` in PostgreSQL

---

## Cloud-Specific Patterns

| Service | Key Config | Notes |
|---------|-----------|-------|
| **AWS RDS Proxy** | `max_connections_percent`: 50-90% | Use for Lambda/serverless; supports IAM auth |
| **GCP Cloud SQL Proxy** | `--max-connections 100` | Sidecar pattern; handles IAM auth + encryption |
| **Supabase (Supavisor)** | Port 6543 (transaction), 5432 (session) | Transaction mode for serverless; session for migrations |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No connection pooler with serverless | Connection storm on cold start | Use PgBouncer or RDS Proxy |
| App pool + PgBouncer both maxed | Double-pooling wastes connections | Size app pool small, let PgBouncer manage |
| Session mode for web apps | Connections held during idle time | Use transaction mode |
| No connection timeout | Leaked connections never reclaimed | Set `idle_in_transaction_session_timeout` |
| max_connections = 10000 | PostgreSQL OOM, context switching overhead | Use pooler; keep max_connections reasonable |
| No monitoring on pool metrics | Exhaustion surprises during traffic spikes | Alert on waiting clients and active connection % |
| Same pool size for all environments | Dev pool wastes resources; prod pool too small | Size per environment based on load |
| Not recycling connections | Stale connections accumulate memory | Set `pool_recycle` / `max_lifetime` |

---

## Cross-References

- `partition-strategies.md` — Query optimization reduces connection hold time
- `monitoring-alerting-patterns.md` — Dashboard templates for connection metrics
- `native-query-patterns.md` — Metabase query performance and connection usage

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
