# Operational Patterns and Standards

Actionable patterns, checklists, and database-specific guidance for SQL optimization, indexing, and reliability.

---

## Production Tuning Workflow (Measure -> Explain -> Change -> Verify)

Use this workflow to avoid guesswork and prevent performance regressions:

1. **Measure**: capture baseline latency/cost (p95/p99, rows scanned, CPU/IO, lock time).
2. **Explain**: run `EXPLAIN` / `EXPLAIN ANALYZE` (plus buffers/IO where available).
3. **Hypothesis**: write the expected bottleneck and expected outcome.
4. **Change**: make one change at a time (query rewrite, index, stats, config).
5. **Verify**: re-measure with representative data and validate result equivalence.

Template: [assets/cross-platform/template-performance-tuning-worksheet.md](../assets/cross-platform/template-performance-tuning-worksheet.md)

---

## Foundational SQL Patterns
- **Projection/Filtering:** Explicit column lists; filter early with selective predicates; `HAVING` only for aggregates.
- **Joins:** Prefer explicit `JOIN ... ON` over implicit joins; check join cardinality and needed indexes per key.
- **Grouping/Set Ops:** Use `GROUP BY` only on needed dimensions; choose `UNION ALL` unless dedup is required.
- **Window Functions:** Use windowed aggregates (ROW_NUMBER, SUM OVER PARTITION/ORDER) instead of procedural loops.
- **NULL/Logic:** Remember three-valued logic; use `IS NULL`/`COALESCE`; avoid nullable boolean flags.
- **Defaults & Constraints:** Define sensible defaults, NOT NULL where possible, and check constraints for data quality.

---

## Query Optimization Checklist
- [ ] Query uses smallest result set possible (`WHERE`, `LIMIT`, early filtering)
- [ ] JOINs properly indexed on join keys (INNER JOIN preferred over subqueries)
- [ ] Functions/casts avoided on indexed columns in WHERE clause
- [ ] SELECT uses only needed columns (no `SELECT *`)
- [ ] UNION ALL instead of UNION (avoid duplicate removal overhead)
- [ ] Subqueries converted to JOINs when possible (optimizer-friendly)
- [ ] Query plan shows Index Scan, not Sequential/Table Scan
- [ ] Statistics are up-to-date (auto-analyze enabled)

---

## EXPLAIN ANALYZE Interpretation
- **PostgreSQL:** `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)`
- **MySQL:** `EXPLAIN FORMAT=JSON` or `EXPLAIN ANALYZE`
- **Checklist:**
 - [ ] Index Scan for filtered queries (not Seq Scan on large tables)
 - [ ] JOINs have matching indexes on both sides
 - [ ] No "Using filesort" or "Using temporary" for large datasets
 - [ ] Estimated rows vs. actual rows match within 10x (no cardinality misestimation)
 - [ ] Shared buffers hit ratio >99% for hot data
 - [ ] No nested loops with large outer tables

---

## Balanced Index Strategy
- **Critical Principle:** Avoid over-indexing (slows writes, wastes storage)
- **Index only when:**
 - Column appears frequently in WHERE, JOIN, ORDER BY
 - Table has >10,000 rows and query selectivity <10%
 - Index provides 10x+ speedup (verify with EXPLAIN)
- **Index Types:**
 - B-tree (default): Equality and range queries
 - Partial index: `CREATE INDEX idx ON table(col) WHERE active = true;`
 - Covering index (Postgres): `CREATE INDEX idx ON table(col1, col2) INCLUDE (col3);`
 - Expression index: `CREATE INDEX idx ON table(LOWER(email));`
- **Monitor unused indexes:**
```sql
-- PostgreSQL: Find unused indexes
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexname NOT LIKE 'pg_toast%';
```

---

## PostgreSQL Memory Tuning
- **OLTP Systems (many small transactions):**
 - work_mem: 4-16MB (prevent excessive memory per connection)
 - shared_buffers: 25% of RAM
 - effective_cache_size: 50-75% of total RAM
- **OLAP Systems (analytical queries):**
 - work_mem: 64-256MB (allow in-memory operations)
 - shared_buffers: 25% of RAM
 - effective_cache_size: 75% of total RAM
- **Connection Pooling (Required for production):**
  - Use pgBouncer or Pgpool-II to limit active connections
  - Target: <100 active connections (reduce RAM, improve response time)

---

## Connection Pooling

### PgBouncer Pooling Modes

| Mode | Use Case | Supports Prepared Stmts | Notes |
|------|----------|------------------------|-------|
| **Session** | Legacy apps, full PostgreSQL features | Yes | Connection held for entire session |
| **Transaction** | Web apps, microservices (default Azure) | Limited | Released after each transaction |
| **Statement** | High-frequency OLTP, simple queries | No | Released after each statement |

### Pool Sizing Formula

```text
default_pool_size = (RAM / 20MB) / databases
Max: 100-200 per server
```

### Connection Pooler Comparison

| Feature | PgBouncer | Pgcat | Odyssey |
|---------|-----------|-------|---------|
| **Best for** | VPS, standard deployments | Cloud-native, Kubernetes | Enterprise, high-scale |
| **Language** | C | Rust | C |
| **Multi-tenant** | Basic | Excellent | Good |
| **Read/Write splitting** | No | Yes | Yes |
| **Query caching** | No | No | Yes |
| **Memory footprint** | Very low | Low | Medium |
| **Recommendation** | Default choice (90% of cases) | Modern K8s environments | Large-scale operations |

### PgBouncer Configuration Example

```ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = *
auth_type = scram-sha-256
pool_mode = transaction
default_pool_size = 20
max_client_conn = 1000
```

### Deployment Patterns

- **Same VM as app**: Lowest latency, simplest setup
- **Sidecar (Kubernetes)**: Deploy PgBouncer container alongside app pod
- **Dedicated pool layer**: HAProxy + multiple PgBouncer instances for HA

### Security Note (CVE-2025-12819)

PgBouncer before 1.25.1 is vulnerable to arbitrary SQL execution during authentication via a malicious `search_path` parameter in the StartupMessage in certain non-default configurations (notably `track_extra_parameters` including `search_path` plus `auth_user` set). Recommended actions:

- Upgrade PgBouncer to 1.25.1+
- Remove `search_path` (and other security-sensitive parameters) from `track_extra_parameters`
- Fully-qualify objects/operators in `auth_query` (for example, `pg_catalog.current_user` instead of `current_user`)

---

## PostgreSQL 17+ Optimizations
- **Skip Scan:** B-tree indexes efficiently traverse multi-column indexes
- **Partition Pruning:** Improved query time for partitioned tables
- **Parallel Query:** Better cost estimation for parallel scans
- **Incremental Sorting:** Reduces memory for ORDER BY operations
- **Incremental VACUUM:** Only processes changed portions of large tables (not full 500GB scan)

---

## PostgreSQL 18 Features

### Async I/O Subsystem (2-3x Faster I/O)

PostgreSQL 18 introduces asynchronous I/O using Linux io_uring or background workers:

- **2-3x faster** sequential scans, bitmap heap scans, and VACUUMs
- Parallel disk reads hide I/O latency
- Enable with: `io_method = io_uring` (requires Linux 5.10+)

```sql
-- Check current I/O method
SHOW io_method;

-- Verify async I/O is active in EXPLAIN
EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM large_table WHERE created_at > '2025-01-01';
-- Look for "Async IO" in output
```

### Skip Scan for B-tree Indexes

Multicolumn B-tree indexes now support "skip scan" lookups:

- Improves queries that omit `=` condition on prefix columns
- Can be faster even without leading column equality; still prefer leading conditions when possible

```sql
-- Index on (tenant_id, created_at)
CREATE INDEX idx_orders_tenant_created ON orders(tenant_id, created_at);

-- Previously slow (no tenant_id filter):
SELECT * FROM orders WHERE created_at > '2025-01-01';

-- PostgreSQL 18: Uses skip scan, much faster
```

### OR Condition Index Optimization

Queries with `OR` in WHERE can now use indexes more effectively:

- Reduces need for UNION ALL rewrites
- Planner can use OR-expansion/index union; still verify with EXPLAIN and keep UNION ALL rewrites as an option

```sql
-- Previously required UNION rewrite:
SELECT * FROM users WHERE status = 'active' OR role = 'admin';

-- PostgreSQL 18: Optimizer uses index efficiently
```

### Parallel GIN Index Builds

GIN indexes (for JSONB, arrays, full-text) now support parallel builds:

```sql
-- Parallel GIN build (uses multiple workers)
CREATE INDEX CONCURRENTLY idx_docs_content ON documents USING GIN(content);
```

### UUIDv7 Support

Native UUIDv7 generation (sortable, time-ordered):

```sql
-- Better index locality than UUIDv4
SELECT gen_random_uuid();  -- Still v4
SELECT uuidv7();           -- New: v7 (time-ordered)
```

### Data Checksums Default ON

New clusters have data checksums enabled by default:

- Detects storage corruption
- Disable with: `initdb --no-data-checksums`

### Hash Join and Merge Join Improvements

- Boosted hash join performance for large tables
- Merge joins can now use incremental sorts

---

## PostgreSQL Mistakes to Avoid
- **Identity vs. Serial:** Use `GENERATED BY DEFAULT AS IDENTITY`; avoid `serial`.
- **Autovacuum/WAL:** Monitor freeze age and slot retention; avoid unbounded replication slots filling disk.
- **CTE Materialization:** Avoid forced materialization on large datasets unless isolation is needed.
- **Time Zones:** Store in `timestamptz`, convert at the edge; avoid mixing timestamptz/timestamp.
- **Data Types:** Prefer `numeric` for money, `jsonb` with indexes for semi-structured data, and correct varchar length for constraints.

---

## Anti-Pattern Remediation
- **Anti-pattern:** `SELECT *` (returns unnecessary data, prevents covering indexes)  
 - **Fix:** `SELECT col1, col2 FROM table;`
- **Anti-pattern:** Functions on indexed columns (`WHERE LOWER(email) = 'test@example.com'`)  
 - **Fix:** Create expression index: `CREATE INDEX idx ON users(LOWER(email));`
- **Anti-pattern:** UNION (removes duplicates with expensive sort)  
 - **Fix:** `UNION ALL` (faster, skip duplicate removal if not needed)
- **Anti-pattern:** Correlated subqueries in SELECT  
 - **Fix:** Convert to LEFT JOIN with aggregation
- **Anti-pattern:** Missing WHERE clause on large tables  
 - **Fix:** Always filter by indexed column (timestamp, status, etc.)

---

## MySQL Operational Hotspots (High Performance MySQL)
- **Redo/Undo & Flush:** Size redo/undo logs for workload; use appropriate flush method (O_DIRECT vs fsync) and monitor IO stalls.

---

## Optional: AI/Automation

> **Note**: Automation can accelerate triage, but correctness and production safety still require human verification.

### Candidate automations (use with guardrails)

- **Plan summarization**: summarize large plans into the top 3 bottlenecks.
- **Query linting**: detect anti-patterns (missing predicates, `SELECT *`, implicit casts).
- **Index candidates**: suggest indexes, but require a written workload justification and rollback plan.

### Bounded claims

- Automated suggestions cannot prove result equivalence.
- Automated index suggestions can increase write latency and storage costs.
- Any auto-fix must be gated behind tests and explicit approval.
- **Buffer Pool & Change Buffer:** Ensure buffer pool fits hot set; watch change buffer for write amplification.
- **Replication:** Prefer semi-sync or delayed replicas for safety; monitor lag and use read-only/read_only+super_read_only on replicas.
- **Online Schema Changes:** Use `gh-ost` or `pt-online-schema-change` for large tables; avoid blocking DDL.
- **Binary Logs:** Retain `binlog_expire_logs_seconds` for PITR; avoid unbounded growth.

---

## Slow Query Troubleshooting Workflow
1. **Identify slow queries:** Use pg_stat_statements (Postgres) or slow query log (MySQL)
```sql
-- PostgreSQL: Top 10 slowest queries by total time
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC LIMIT 10;
```
2. **Analyze execution plan:** Run `EXPLAIN ANALYZE` and check for Seq Scans
3. **Review index coverage:** Use `\\di` (Postgres) or `SHOW INDEX FROM table` (MySQL)
4. **Apply optimization:**
 - Add missing indexes (verify selectivity first)
 - Rewrite query (convert subquery to JOIN)
 - Update statistics: `ANALYZE table;`
5. **Validate improvement:** Re-run EXPLAIN ANALYZE, compare timings
6. **Monitor production:** Track query performance metrics for 24-48 hours

---

## Optimization Philosophy

Principles for production tuning:

1. **Measure first**: capture baseline latency, rows scanned, and resource usage before changes.
2. **Fix query shape before hardware**: reduce scanned rows and improve join/selectivity before scaling.
3. **Balance reads and writes**: indexes and materialization have write and storage costs.
4. **Keep feedback loops short**: small changes, verified with EXPLAIN and representative datasets.
5. **Treat stats as part of correctness**: stale stats cause bad plans and misleading conclusions.

---

## Database-Specific Quick Reference

### PostgreSQL
- **EXPLAIN**: `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)`
- **Index types**: B-tree, GIN (JSONB, arrays), GiST (spatial), BRIN (large sequential tables)
- **Monitoring**: `pg_stat_statements`, `pg_stat_user_tables`, `pg_locks`
- **Vacuum**: Monitor bloat with pg_stat_user_tables
- **Connection pooling**: pgBouncer or Pgpool-II
- **Memory tuning**: work_mem (4-16MB OLTP, 64-256MB OLAP), shared_buffers (25% RAM)
- **New in PG17+**: Skip scan, improved partition pruning, incremental sorting

### MySQL
- **EXPLAIN**: `EXPLAIN FORMAT=JSON` or `EXPLAIN ANALYZE`
- **Index types**: BTREE, FULLTEXT, SPATIAL
- **Monitoring**: Performance Schema, slow query log, `pt-query-digest`
- **InnoDB**: Buffer pool 70-80% of RAM, binlog retention 7+ days, doublewrite buffer enabled
- **Replication**: GTID-based replication, monitor lag with `Seconds_Behind_Master`
- **Connection pooling**: ProxySQL for routing and multiplexing

### DuckDB (Analytical Workloads)
- **EXPLAIN**: `EXPLAIN ANALYZE`
- **Optimization**: Columnar Parquet format, projection/filter pushdown, vectorized execution
- **Data loading**: `read_parquet()`, `read_csv()`, extensions (postgres_scanner, mysql_scanner)
- **Export**: `COPY table TO 'file.parquet' (FORMAT PARQUET, COMPRESSION ZSTD);`
- **Performance**: Multi-threaded by default, processes data in parallel across CPU cores
- **Use case**: Analytics on large datasets (10M+ rows), ETL transformations, format conversion

### SQL Server
- **EXPLAIN**: `SET STATISTICS IO ON; SET STATISTICS TIME ON;`
- **Index types**: Clustered, non-clustered, columnstore
- **Monitoring**: DMVs, Query Store
- **Memory**: Buffer pool extension, in-memory OLTP for hot tables
- **Query hints**: Use sparingly; let optimizer choose plan
- **SQL Server 2025**: Optional parameter plan optimization (OPPO), optimized locking, tempdb space resource governance, expression cardinality estimation feedback

### Oracle
- **EXPLAIN**: `EXPLAIN PLAN FOR ...` then `SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);`
- **Index types**: B-tree, bitmap (low-cardinality), function-based indexes
- **Monitoring**: AWR, ASH, V$ views
- **Optimizer**: Gather statistics regularly; avoid hints unless necessary

### SQLite
- **EXPLAIN**: `EXPLAIN QUERY PLAN ...`
- **Optimization**: Covering indexes, avoid triggers for hot paths, keep transactions short
- **Pragmas**: WAL mode for concurrency, `PRAGMA optimize;` periodically

---

## Symptom -> Action Reference

| Symptom | Likely Cause | Action |
|-----------------------------|-----------------------------|--------------------------------------------|
| Seq Scan on large table | Missing/wrong index | Create covering index for filter/join key |
| "Using temporary; filesort" | No sort/group index | Add index for ORDER BY / GROUP BY column |
| "Function on column" | Indexed column wrapped func | Use functional index or rewrite query |
| High replication lag | Large transactions, I/O | Batch updates, tune sync commit mode |
| Deadlocks | Lock ordering mismatch | Standardize lock acquisition order |

---

## Reliability Drills (Database Reliability Engineering)
- [ ] Backups validated with periodic restore tests (including PITR)
- [ ] Replica/failover tested under load with clear promotion runbook
- [ ] Capacity models for storage/WAL/binlog growth and buffer memory
- [ ] SLO/SLI for latency, error rate, and replication lag tracked with alerts
- [ ] Runbooks include load-shed/backpressure and retry budgets

---

## Template Selection Guide

Use this decision tree to select the right template:

```
Query is slow?
├─ Yes -> Use ../assets/cross-platform/template-slow-query.md
│ ├─ Need EXPLAIN analysis?
│ │ ├─ PostgreSQL -> ../assets/postgres/template-pg-explain.md
│ │ ├─ MySQL -> ../assets/mysql/template-mysql-explain.md
│ │ ├─ SQL Server -> ../assets/mssql/template-mssql-explain.md
│ │ └─ Oracle -> ../assets/oracle/template-oracle-explain.md
│ └─ Need index optimization?
│ ├─ PostgreSQL -> ../assets/postgres/template-pg-index.md
│ ├─ MySQL -> ../assets/mysql/template-mysql-index.md
│ └─ SQL Server -> ../assets/mssql/template-mssql-index.md
├─ Schema change needed?
│ ├─ New schema -> ../assets/cross-platform/template-schema-design.md
│ └─ Modify schema -> ../assets/cross-platform/template-migration.md
├─ Backup/DR planning?
│ └─ Use ../assets/cross-platform/template-backup-restore.md
├─ Replication setup?
│ ├─ PostgreSQL -> ../assets/postgres/template-replication-ha.md
│ └─ MySQL -> ../assets/mysql/template-replication-ha.md
├─ Lock contention/deadlocks?
│ └─ Use ../assets/cross-platform/template-lock-analysis.md
├─ General diagnostics?
│ └─ Use ../assets/cross-platform/template-diagnostics.md
└─ Security audit?
 └─ Use ../assets/cross-platform/template-security-audit.md
```

---

## Platform Migration Notes

When migrating between databases:
- **Postgres <-> MySQL**: Index syntax differs (INCLUDE vs covering index workarounds)
- **RDBMS -> DuckDB**: Use DuckDB scanners (postgres_scanner, mysql_scanner) for direct import (see `../data-lake-platform/SKILL.md`)
- **CSV -> Parquet**: Use DuckDB for fast conversion with compression (see `../data-lake-platform/SKILL.md`)

---

This resource centralizes operational content referenced by the lightweight `SKILL.md`.
