---
name: ops-database-sql
description: Production-grade SQL optimization with AI-assisted query analysis, EXPLAIN ANALYZE automation, balanced indexing strategies, performance tuning, schema design, and operations across PostgreSQL, MySQL, SQL Server, Oracle, SQLite, and DuckDB.
---

# SQL Optimization — Comprehensive Reference

This skill equips Claude with actionable checklists, patterns, and templates for SQL optimization using modern best practices: AI-powered query analysis, automated EXPLAIN interpretation, intelligent indexing (avoiding over-indexing), performance monitoring with pg_stat_statements, schema evolution, migrations, backup/recovery, high availability, security, and analytical workloads.

**Supported Platforms:** PostgreSQL, MySQL, SQL Server, Oracle, SQLite, DuckDB

---

## Quick Reference

| Task | Tool/Framework | Command | When to Use |
|------|----------------|---------|-------------|
| Query Performance Analysis | EXPLAIN ANALYZE | `EXPLAIN (ANALYZE, BUFFERS) SELECT ...` (PG) / `EXPLAIN ANALYZE SELECT ...` (MySQL) | Diagnose slow queries, identify missing indexes |
| Find Slow Queries | pg_stat_statements / slow query log | `SELECT * FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 10;` | Identify performance bottlenecks in production |
| Index Analysis | pg_stat_user_indexes / SHOW INDEX | `SELECT * FROM pg_stat_user_indexes WHERE idx_scan = 0;` | Find unused indexes, validate index coverage |
| Schema Migration | Flyway / Liquibase | `flyway migrate` / `liquibase update` | Version-controlled database changes |
| Backup & Recovery | pg_dump / mysqldump | `pg_dump -Fc dbname > backup.dump` | Point-in-time recovery, disaster recovery |
| Replication Setup | Streaming / GTID | Configure postgresql.conf / my.cnf | High availability, read scaling |
| Analytical Queries | DuckDB | `SELECT * FROM read_parquet('data.parquet')` | Fast analytics on large datasets (10M+ rows) |
| Query Optimization | AI-assisted tools | pgai (PostgreSQL) / Performance Schema (MySQL) | ML-based query plan analysis, predictive caching |

---

## Decision Tree: Choosing the Right Approach

```text
Query performance issue?
    ├─ Identify slow queries first?
    │   ├─ PostgreSQL → pg_stat_statements (top queries by total_exec_time)
    │   └─ MySQL → Performance Schema / slow query log
    │
    ├─ Analyze execution plan?
    │   ├─ PostgreSQL → EXPLAIN (ANALYZE, BUFFERS, VERBOSE)
    │   ├─ MySQL → EXPLAIN FORMAT=JSON or EXPLAIN ANALYZE
    │   ├─ DuckDB → EXPLAIN ANALYZE (columnar optimization)
    │   └─ SQL Server → SET STATISTICS IO ON; SET STATISTICS TIME ON;
    │
    ├─ Need indexing strategy?
    │   ├─ PostgreSQL → B-tree (default), GIN (JSONB), GiST (spatial), partial indexes
    │   ├─ MySQL → BTREE (default), FULLTEXT (text search), SPATIAL
    │   └─ Check: Table >10k rows AND selectivity <10% AND 10x+ speedup verified
    │
    ├─ Schema changes needed?
    │   ├─ New database → template-schema-design.md
    │   ├─ Modify schema → template-migration.md (Flyway/Liquibase)
    │   └─ Large tables (MySQL) → gh-ost / pt-online-schema-change (avoid locks)
    │
    ├─ High availability setup?
    │   ├─ PostgreSQL → Streaming replication (template-replication-ha.md)
    │   └─ MySQL → GTID-based replication (template-replication-ha.md)
    │
    ├─ Backup/disaster recovery?
    │   └─ template-backup-restore.md (pg_dump, mysqldump, PITR)
    │
    └─ Analytics on large datasets?
        └─ DuckDB → Parquet/columnar format, vectorized execution
```

---

## When to Use This Skill

Claude should invoke this skill when users ask for:

### Query Optimization (Modern Approaches)
- AI-assisted SQL query performance review and tuning
- Automated EXPLAIN ANALYZE plan interpretation with optimization suggestions
- Index creation strategies with balanced approach (avoiding over-indexing)
- Troubleshooting slow queries using pg_stat_statements or Performance Schema
- Identifying and remediating SQL anti-patterns with operational fixes
- Query rewrite suggestions or migration from slow to fast patterns
- Statistics maintenance and auto-analyze configuration

### Database Operations
- Schema design with normalization and performance trade-offs
- Database migrations with version control (Liquibase, Flyway)
- Backup and recovery strategies (point-in-time recovery, automated testing)
- High availability and replication setup (streaming, GTID-based)
- Database security auditing (access controls, encryption, SQL injection prevention)
- Lock analysis and deadlock troubleshooting
- Connection pooling (pgBouncer, Pgpool-II, ProxySQL)

### Performance Tuning (Modern Standards)
- Memory configuration (work_mem, shared_buffers, effective_cache_size)
- Automated monitoring with pg_stat_statements and query pattern analysis
- Index health monitoring (unused index detection, index bloat analysis)
- Vacuum strategy and autovacuum tuning (PostgreSQL)
- InnoDB buffer pool optimization (MySQL)
- Partition pruning improvements (PostgreSQL 17+)

### Analytical Workloads (DuckDB)
- Analytical query optimization with columnar storage
- Data import/export workflows with Parquet compression (ZSTD)
- Format conversion (CSV, Parquet, JSON) with optimal performance
- Projection and filter pushdown optimization

---

## Resources (Best Practices Guides)

Find detailed operational patterns and quick references in:

- **SQL Best Practices**: [resources/sql-best-practices.md](resources/sql-best-practices.md)
- **Query Tuning Patterns**: [resources/query-tuning-patterns.md](resources/query-tuning-patterns.md)
- **Indexing Strategies**: [resources/index-patterns.md](resources/index-patterns.md)
- **EXPLAIN/Analysis**: [resources/explain-analysis.md](resources/explain-analysis.md)
- **SQL Anti-Patterns**: [resources/sql-antipatterns.md](resources/sql-antipatterns.md)
- **External Sources**: [data/sources.json](data/sources.json) — vendor docs and reference links
- **Operational Standards**: [resources/operational-patterns.md](resources/operational-patterns.md) — Deep operational checklists, database-specific guidance, and template selection trees

Each file includes:
- Copy-paste ready checklists (e.g., "query review", "index design", "explain review")
- Anti-patterns with operational fixes and alternatives
- Query rewrite and indexing strategies with examples
- Troubleshooting guides (step-by-step)

---

## Templates (Copy-Paste Ready)

Templates are organized by database technology for precision and clarity:

### Cross-Platform Templates (All Databases)
- [templates/cross-platform/template-query-tuning.md](templates/cross-platform/template-query-tuning.md) - Universal query optimization
- [templates/cross-platform/template-explain-analysis.md](templates/cross-platform/template-explain-analysis.md) - Execution plan analysis
- [templates/cross-platform/template-index.md](templates/cross-platform/template-index.md) - Index design patterns
- [templates/cross-platform/template-slow-query.md](templates/cross-platform/template-slow-query.md) - Slow query triage
- [templates/cross-platform/template-schema-design.md](templates/cross-platform/template-schema-design.md) - Schema modeling
- [templates/cross-platform/template-migration.md](templates/cross-platform/template-migration.md) - Database migrations
- [templates/cross-platform/template-backup-restore.md](templates/cross-platform/template-backup-restore.md) - Backup/DR planning
- [templates/cross-platform/template-security-audit.md](templates/cross-platform/template-security-audit.md) - Security review
- [templates/cross-platform/template-diagnostics.md](templates/cross-platform/template-diagnostics.md) - Performance diagnostics
- [templates/cross-platform/template-lock-analysis.md](templates/cross-platform/template-lock-analysis.md) - Lock troubleshooting

### PostgreSQL Templates
- [templates/postgres/template-pg-explain.md](templates/postgres/template-pg-explain.md) - PostgreSQL EXPLAIN analysis
- [templates/postgres/template-pg-index.md](templates/postgres/template-pg-index.md) - PostgreSQL indexing (B-tree, GIN, GiST)
- [templates/postgres/template-replication-ha.md](templates/postgres/template-replication-ha.md) - Streaming replication & HA

### MySQL Templates
- [templates/mysql/template-mysql-explain.md](templates/mysql/template-mysql-explain.md) - MySQL EXPLAIN analysis
- [templates/mysql/template-mysql-index.md](templates/mysql/template-mysql-index.md) - MySQL/InnoDB indexing
- [templates/mysql/template-replication-ha.md](templates/mysql/template-replication-ha.md) - MySQL replication & HA

### DuckDB Templates (Analytical Queries)
- [templates/duckdb/template-duckdb-analytics.md](templates/duckdb/template-duckdb-analytics.md) - Analytical query optimization
- [templates/duckdb/template-duckdb-data-import.md](templates/duckdb/template-duckdb-data-import.md) - Data import/export workflows

### Microsoft SQL Server Templates
- [templates/mssql/template-mssql-explain.md](templates/mssql/template-mssql-explain.md) - SQL Server EXPLAIN/SHOWPLAN analysis
- [templates/mssql/template-mssql-index.md](templates/mssql/template-mssql-index.md) - SQL Server indexing and tuning

### Oracle Templates
- [templates/oracle/template-oracle-explain.md](templates/oracle/template-oracle-explain.md) - Oracle EXPLAIN plan review and tuning

### SQLite Templates
- [templates/sqlite/template-sqlite-optimization.md](templates/sqlite/template-sqlite-optimization.md) - SQLite optimization and pragma guidance

---

## Related Skills

**Infrastructure & Operations:**
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — Infrastructure, backups, monitoring, and incident response
- [../quality-observability-performance/SKILL.md](../quality-observability-performance/SKILL.md) — Performance monitoring, profiling, and metrics
- [../quality-debugging-troubleshooting/SKILL.md](../quality-debugging-troubleshooting/SKILL.md) — Production debugging patterns

**Application Integration:**
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API/database integration and application patterns
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design and data architecture
- [../foundation-api-design/SKILL.md](../foundation-api-design/SKILL.md) — REST API and database interaction patterns

**Quality & Security:**
- [../quality-resilience-patterns/SKILL.md](../quality-resilience-patterns/SKILL.md) — Resilience, circuit breakers, and failure handling
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) — Database security, auth, SQL injection prevention
- [../software-testing-automation/SKILL.md](../software-testing-automation/SKILL.md) — Database testing strategies

**Data Engineering & AI:**
- [../ai-ml-data-science/SKILL.md](../ai-ml-data-science/SKILL.md) — SQLMesh, dbt, data transformations
- [../ai-ml-ops-production/SKILL.md](../ai-ml-ops-production/SKILL.md) — Data pipelines, ETL, and warehouse loading (dlt)
- [../ai-ml-timeseries/SKILL.md](../ai-ml-timeseries/SKILL.md) — Time-series databases and forecasting

---

## Navigation

**Resources**
- [resources/explain-analysis.md](resources/explain-analysis.md)
- [resources/query-tuning-patterns.md](resources/query-tuning-patterns.md)
- [resources/operational-patterns.md](resources/operational-patterns.md)
- [resources/sql-antipatterns.md](resources/sql-antipatterns.md)
- [resources/index-patterns.md](resources/index-patterns.md)
- [resources/sql-best-practices.md](resources/sql-best-practices.md)

**Templates**
- [templates/cross-platform/template-slow-query.md](templates/cross-platform/template-slow-query.md)
- [templates/cross-platform/template-backup-restore.md](templates/cross-platform/template-backup-restore.md)
- [templates/cross-platform/template-schema-design.md](templates/cross-platform/template-schema-design.md)
- [templates/cross-platform/template-explain-analysis.md](templates/cross-platform/template-explain-analysis.md)
- [templates/cross-platform/template-security-audit.md](templates/cross-platform/template-security-audit.md)
- [templates/cross-platform/template-diagnostics.md](templates/cross-platform/template-diagnostics.md)
- [templates/cross-platform/template-index.md](templates/cross-platform/template-index.md)
- [templates/cross-platform/template-migration.md](templates/cross-platform/template-migration.md)
- [templates/cross-platform/template-lock-analysis.md](templates/cross-platform/template-lock-analysis.md)
- [templates/cross-platform/template-query-tuning.md](templates/cross-platform/template-query-tuning.md)
- [templates/oracle/template-oracle-explain.md](templates/oracle/template-oracle-explain.md)
- [templates/sqlite/template-sqlite-optimization.md](templates/sqlite/template-sqlite-optimization.md)
- [templates/postgres/template-pg-index.md](templates/postgres/template-pg-index.md)
- [templates/postgres/template-replication-ha.md](templates/postgres/template-replication-ha.md)
- [templates/postgres/template-pg-explain.md](templates/postgres/template-pg-explain.md)
- [templates/mysql/template-mysql-explain.md](templates/mysql/template-mysql-explain.md)
- [templates/mysql/template-mysql-index.md](templates/mysql/template-mysql-index.md)
- [templates/mysql/template-replication-ha.md](templates/mysql/template-replication-ha.md)
- [templates/duckdb/template-duckdb-data-import.md](templates/duckdb/template-duckdb-data-import.md)
- [templates/duckdb/template-duckdb-analytics.md](templates/duckdb/template-duckdb-analytics.md)
- [templates/mssql/template-mssql-index.md](templates/mssql/template-mssql-index.md)
- [templates/mssql/template-mssql-explain.md](templates/mssql/template-mssql-explain.md)

**Data**
- [data/sources.json](data/sources.json) — Curated external references

---

## Operational Deep Dives

See [resources/operational-patterns.md](resources/operational-patterns.md) for:
- End-to-end optimization checklists and anti-pattern fixes
- Database-specific quick references (PostgreSQL, MySQL, DuckDB, SQL Server, Oracle, SQLite)
- Slow query troubleshooting workflow and reliability drills
- Template selection decision tree and platform migration notes

---
## Related Skills

This skill focuses on **query optimization** within a single database. For related workflows:

**SQL Transformation & Analytics Engineering:**
→ `ds-engineering-suite` skill
- SQLMesh templates for building staging/intermediate/marts layers
- Incremental models (FULL, INCREMENTAL_BY_TIME_RANGE, INCREMENTAL_BY_UNIQUE_KEY)
- DAG management and model dependencies
- Unit tests and audits for SQL transformations

**Data Ingestion (Loading into Warehouses):**
→ `ml-ops-production-engineering` skill
- dlt templates for extracting from REST APIs, databases
- Loading to Snowflake, BigQuery, Redshift, Postgres, DuckDB
- Incremental loading patterns (timestamp, ID-based, merge/upsert)
- Database replication (Postgres, MySQL, MongoDB → warehouse)

**Use Case Decision:**
- **Query is slow in production** → Use this skill (sql-optimization)
- **Building feature pipelines in SQL** → Use ds-engineering-suite (SQLMesh)
- **Loading data from APIs/DBs to warehouse** → Use ml-ops-production-engineering (dlt)

---

## External Resources

See [data/sources.json](data/sources.json) for 62+ curated resources including:

**Core Documentation:**
- **RDBMS Documentation**: PostgreSQL, MySQL, SQL Server, Oracle, SQLite, DuckDB official docs
- **Query Optimization**: Use The Index, Luke, SQL Performance Explained, vendor optimization guides
- **Schema Design**: Database Refactoring (Fowler), normalization guides, data type selection

**Modern Optimization (2024-2025):**
- **PostgreSQL 17**: B-tree optimizations, CTE improvements, skip scan, partition pruning, incremental sorting
- **MySQL 8.4/8.5**: Thread pool management, parallel processing, AI integration, workload analysis
- **DuckDB**: Columnar optimization, zone maps, vectorized execution, query optimizer insights (100x improvements)

**Operations & Infrastructure:**
- **HA & Replication**: Streaming replication, GTID-based replication, failover automation
- **Migrations**: Liquibase, Flyway version control and deployment patterns
- **Backup/Recovery**: pgBackRest, Percona XtraBackup, point-in-time recovery
- **Monitoring**: pg_stat_statements, Performance Schema, EXPLAIN visualizers (Dalibo, depesz)
- **Security**: OWASP SQL Injection Prevention, Postgres hardening, encryption standards
- **Analytical Databases**: DuckDB extensions, Parquet specification, columnar storage patterns

---

Use [resources/operational-patterns.md](resources/operational-patterns.md) and the templates directory for detailed workflows, migration notes, and ready-to-run commands.
