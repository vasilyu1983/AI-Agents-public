# Database Monitoring and Alerting Patterns

> Purpose: Operational guide for monitoring PostgreSQL and MySQL databases — pg_stat_statements setup, slow query alerting, Prometheus/Grafana dashboards, capacity planning, and proactive alerting for connections, cache, replication, and vacuum. Freshness anchor: Q1 2026.

---

## Decision Tree: Monitoring Stack Selection

```
START: What is your infrastructure?
│
├─ Managed cloud database (RDS, Cloud SQL, Azure DB)
│   │
│   ├─ Want zero-maintenance monitoring?
│   │   └─ Cloud-native: CloudWatch / Cloud Monitoring / Azure Monitor
│   │       + Performance Insights (RDS) or Query Insights (Cloud SQL)
│   │
│   └─ Want custom dashboards and alerting?
│       └─ Prometheus (via exporters) + Grafana
│           + cloud metrics as supplemental
│
├─ Self-managed database (VM, bare metal, Kubernetes)
│   └─ Prometheus + Grafana (standard)
│       ├─ PostgreSQL: postgres_exporter
│       └─ MySQL: mysqld_exporter
│
└─ Serverless / Neon / PlanetScale
    └─ Platform-native dashboards + webhook alerts
```

---

## Quick Reference: Critical Database Metrics

| Metric | Warning | Critical | Why It Matters |
|--------|---------|----------|---------------|
| Connection usage % | >70% | >90% | Connection exhaustion = outage |
| Cache hit ratio | <95% | <90% | Low cache = slow queries = disk I/O |
| Replication lag (seconds) | >10s | >60s | Read replicas serving stale data |
| Long-running queries | >30s | >300s | Lock contention, resource consumption |
| Dead tuples (table bloat) | >20% dead | >50% dead | VACUUM not keeping up, degraded performance |
| Disk usage % | >70% | >85% | Disk full = database crash |
| Transaction wraparound age | >500M | >1B | Risk of forced shutdown for wraparound prevention |
| Active locks / lock waits | >10 waiting | >50 waiting | Application blocking, potential deadlocks |

---

## pg_stat_statements Setup (PostgreSQL)

### Installation

```sql
-- 1. Add to postgresql.conf (requires restart)
-- shared_preload_libraries = 'pg_stat_statements'

-- Or via ALTER SYSTEM (still requires restart)
ALTER SYSTEM SET shared_preload_libraries = 'pg_stat_statements';

-- 2. Create extension (after restart)
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- 3. Configure parameters
ALTER SYSTEM SET pg_stat_statements.max = 10000;         -- max tracked statements
ALTER SYSTEM SET pg_stat_statements.track = 'all';        -- top, all, or none
ALTER SYSTEM SET pg_stat_statements.track_utility = true;  -- track non-DML
ALTER SYSTEM SET pg_stat_statements.track_planning = true; -- track planning time
SELECT pg_reload_conf();
```

### Essential Queries

```sql
-- Top 10 queries by total execution time
SELECT queryid, LEFT(query, 100) AS query_preview, calls,
  ROUND(total_exec_time::numeric / 1000, 2) AS total_seconds,
  ROUND(mean_exec_time::numeric, 2) AS mean_ms, rows
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;

-- Top 10 by buffer usage (I/O intensive)
SELECT queryid, LEFT(query, 100) AS query_preview, calls,
  shared_blks_hit + shared_blks_read AS total_blocks,
  ROUND(100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0), 1) AS cache_hit_pct
FROM pg_stat_statements ORDER BY shared_blks_read DESC LIMIT 10;

-- Reset statistics (run weekly)
SELECT pg_stat_statements_reset();
```

---

## Slow Query Alerting

### PostgreSQL: log_min_duration_statement

```sql
-- Log queries taking >1 second
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- milliseconds
ALTER SYSTEM SET log_statement = 'none';             -- avoid double-logging
SELECT pg_reload_conf();
```

### MySQL: Slow Query Log

```sql
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;  -- seconds
SET GLOBAL log_queries_not_using_indexes = 'ON';
```

### Alert Rules (Prometheus)

- `SlowQueryRate`: `rate(pg_stat_statements_mean_exec_time_seconds[5m]) > 1` for 5m (warning)
- `LongRunningQuery`: `pg_stat_activity_max_tx_duration{state="active"} > 300` for 1m (critical)

---

## Prometheus Exporters

### PostgreSQL: postgres_exporter

```yaml
# docker-compose.yml
postgres_exporter:
  image: prometheuscommunity/postgres-exporter:latest
  environment:
    DATA_SOURCE_NAME: "postgresql://monitor:${MONITOR_PASSWORD}@db:5432/myapp?sslmode=require"
  ports:
    - "9187:9187"
  command:
    - "--collector.stat_statements"
    - "--collector.stat_activity_autovacuum"

# prometheus.yml
scrape_configs:
  - job_name: postgres
    static_configs:
      - targets: ['postgres_exporter:9187']
    scrape_interval: 15s
```

### MySQL: mysqld_exporter

```yaml
# docker-compose.yml
mysqld_exporter:
  image: prom/mysqld-exporter:latest
  environment:
    DATA_SOURCE_NAME: "monitor:${MONITOR_PASSWORD}@tcp(db:3306)/myapp"
  ports:
    - "9104:9104"
  command:
    - "--collect.auto_increment.columns"
    - "--collect.info_schema.processlist"
    - "--collect.perf_schema.eventsstatements"

# prometheus.yml
scrape_configs:
  - job_name: mysql
    static_configs:
      - targets: ['mysqld_exporter:9104']
    scrape_interval: 15s
```

### Monitor User Setup

```sql
-- PostgreSQL: create monitoring role
CREATE ROLE monitor WITH LOGIN PASSWORD 'strong_password';
GRANT pg_monitor TO monitor;
GRANT SELECT ON pg_stat_statements TO monitor;

-- MySQL: create monitoring user
CREATE USER 'monitor'@'%' IDENTIFIED BY 'strong_password';
GRANT PROCESS, REPLICATION CLIENT, SELECT ON *.* TO 'monitor'@'%';
```

---

## Grafana Dashboard Templates

### PostgreSQL Dashboard Panels

| Panel | Query (PromQL) | Visualization |
|-------|---------------|---------------|
| Connection usage | `pg_stat_activity_count / pg_settings_max_connections` | Gauge (%) |
| Active connections | `pg_stat_activity_count{state="active"}` | Time series |
| Cache hit ratio | `pg_stat_database_blks_hit / (pg_stat_database_blks_hit + pg_stat_database_blks_read)` | Gauge (%) |
| Transactions/sec | `rate(pg_stat_database_xact_commit[5m]) + rate(pg_stat_database_xact_rollback[5m])` | Time series |
| Tuple operations | `rate(pg_stat_database_tup_inserted[5m])`, `tup_updated`, `tup_deleted` | Stacked area |
| Replication lag | `pg_replication_lag_seconds` | Time series |
| Table bloat | `pg_stat_user_tables_n_dead_tup / (pg_stat_user_tables_n_live_tup + pg_stat_user_tables_n_dead_tup)` | Table |
| Disk usage | `pg_database_size_bytes` | Time series |

### MySQL Dashboard Panels

| Panel | Query (PromQL) | Visualization |
|-------|---------------|---------------|
| Connection usage | `mysql_global_status_threads_connected / mysql_global_variables_max_connections` | Gauge (%) |
| Queries/sec | `rate(mysql_global_status_queries[5m])` | Time series |
| InnoDB buffer pool hit ratio | `1 - (rate(mysql_global_status_innodb_buffer_pool_reads[5m]) / rate(mysql_global_status_innodb_buffer_pool_read_requests[5m]))` | Gauge (%) |
| Slow queries | `rate(mysql_global_status_slow_queries[5m])` | Time series |
| Replication lag | `mysql_slave_status_seconds_behind_master` | Time series |
| Table locks waited | `rate(mysql_global_status_table_locks_waited[5m])` | Time series |

### Recommended Grafana Dashboard IDs

| Dashboard | Grafana ID | Description |
|-----------|-----------|-------------|
| PostgreSQL Overview | 9628 | Comprehensive PG monitoring |
| PostgreSQL Query Statistics | 12273 | pg_stat_statements focused |
| MySQL Overview | 7362 | Comprehensive MySQL monitoring |
| MySQL InnoDB Metrics | 7365 | Storage engine focused |
| PgBouncer | 13463 | Connection pool monitoring |

---

## Proactive Alerting Rules

### Connection Alerts

```yaml
groups:
  - name: connections
    rules:
      - alert: HighConnectionUsage
        expr: |
          pg_stat_activity_count{datname!~"template.*"}
          / on(instance) pg_settings_max_connections > 0.7
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Connection usage > 70% on {{ $labels.instance }}"

      - alert: CriticalConnectionUsage
        expr: |
          pg_stat_activity_count{datname!~"template.*"}
          / on(instance) pg_settings_max_connections > 0.9
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Connection usage > 90% on {{ $labels.instance }}"

      - alert: IdleInTransaction
        expr: pg_stat_activity_count{state="idle in transaction"} > 5
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "{{ $value }} idle-in-transaction connections on {{ $labels.instance }}"
```

### Cache Hit Ratio Alerts

```yaml
      - alert: LowCacheHitRatio
        expr: |
          pg_stat_database_blks_hit{datname!~"template.*"}
          / (pg_stat_database_blks_hit + pg_stat_database_blks_read) < 0.95
        for: 15m
        labels:
          severity: warning
        annotations:
          summary: "Cache hit ratio < 95% on {{ $labels.datname }}"
          action: "Check shared_buffers sizing; look for sequential scans on large tables"
```

### Replication Lag Alerts

```yaml
      - alert: ReplicationLagWarning
        expr: pg_replication_lag_seconds > 10
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Replication lag > 10s on {{ $labels.instance }}"

      - alert: ReplicationLagCritical
        expr: pg_replication_lag_seconds > 60
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "Replication lag > 60s on {{ $labels.instance }}"
          action: "Check replica I/O, network, and heavy write load on primary"
```

### VACUUM and Bloat Alerts

- `TableBloat`: `dead_tup / (live_tup + dead_tup) > 0.2` for 30m (warning)
- `TransactionWraparoundRisk`: `wraparound_age > 500M` for 1h (critical) — run VACUUM FREEZE immediately
- `AutovacuumNotRunning`: `last_autovacuum == 0` for 24h (warning)

---

## Capacity Planning Queries

```sql
-- PostgreSQL: table sizes with bloat estimate
SELECT schemaname || '.' || relname AS table_name,
  pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
  pg_size_pretty(pg_indexes_size(relid)) AS index_size,
  n_live_tup AS live_rows, n_dead_tup AS dead_rows,
  ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup + n_dead_tup, 0), 1) AS dead_pct
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC LIMIT 20;

-- PostgreSQL: unused indexes (waste space, slow writes)
SELECT schemaname || '.' || relname AS table_name,
  indexrelname AS index_name,
  pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
  idx_scan AS times_used
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND schemaname NOT IN ('pg_catalog', 'information_schema')
ORDER BY pg_relation_size(indexrelid) DESC LIMIT 20;

-- MySQL: table sizes
SELECT table_schema, table_name,
  ROUND(data_length / 1024 / 1024, 2) AS data_mb,
  ROUND(index_length / 1024 / 1024, 2) AS index_mb, table_rows
FROM information_schema.tables
WHERE table_schema NOT IN ('mysql', 'information_schema', 'performance_schema', 'sys')
ORDER BY data_length + index_length DESC LIMIT 20;
```

---

## Monitoring Checklist

### Initial Setup

- [ ] Install Prometheus exporter (postgres_exporter or mysqld_exporter)
- [ ] Create dedicated monitoring database user with minimal permissions
- [ ] Enable pg_stat_statements (PostgreSQL)
- [ ] Enable slow query log (MySQL) or log_min_duration_statement (PostgreSQL)
- [ ] Import Grafana dashboard templates
- [ ] Configure Alertmanager with notification channels (Slack, PagerDuty)
- [ ] Set up all critical alerts from this guide

### Weekly Review

- [ ] Review top 10 slowest queries (pg_stat_statements)
- [ ] Check for unused indexes (drop or justify)
- [ ] Verify autovacuum is running on all tables
- [ ] Check replication lag trend
- [ ] Review connection usage patterns
- [ ] Check disk growth rate vs available capacity

### Monthly Review

- [ ] Reset pg_stat_statements and collect fresh stats
- [ ] Capacity planning: project disk usage 3 months out
- [ ] Review and tune alert thresholds based on false positive rate
- [ ] Check for new tables missing monitoring coverage
- [ ] Validate backup and recovery procedures

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No pg_stat_statements | Cannot identify slow queries | Enable as shared_preload_library |
| Monitoring only connections | Misses cache, replication, and bloat issues | Monitor all critical metrics from this guide |
| Alert on every metric | Alert fatigue, real issues ignored | Tier: critical (page), warning (Slack), info (log) |
| No baseline for "normal" | Cannot detect anomalies | Establish baseline during first 2 weeks |
| Monitoring only primary | Replica issues go undetected | Monitor all instances including replicas |
| No capacity planning | Disk-full surprises | Monthly growth projection |
| Ignoring unused indexes | Wasted space, slower writes | Audit and drop quarterly |
| Not resetting pg_stat_statements | Stats accumulate, obscure recent patterns | Reset weekly or monthly |
| Monitoring without alerting | Dashboard exists but nobody watches it | Automated alerts with escalation |
| No runbook for alerts | Alert fires, nobody knows what to do | Document response steps for each alert |

---

## Cross-References

- `connection-pooling-patterns.md` — Connection pool metrics and monitoring
- `partition-strategies.md` — Partition-specific monitoring (sizes, VACUUM per partition)
- `data-quality-patterns.md` — Data quality monitoring alongside infrastructure monitoring
- `native-query-patterns.md` — Identifying slow Metabase queries via pg_stat_statements

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
