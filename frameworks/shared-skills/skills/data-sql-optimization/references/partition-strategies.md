# Table Partition Strategies

> Purpose: Operational guide for implementing table partitioning — PostgreSQL declarative partitioning, MySQL partitioning, partition key selection, maintenance operations, query optimization with partition pruning, and migration patterns. Freshness anchor: Q1 2026.

---

## Decision Tree: Should You Partition?

```
START: Is your table large and causing performance issues?
│
├─ Table < 10GB and queries are fast
│   └─ NO partitioning needed — use indexes instead
│
├─ Table > 10GB OR queries scan full table despite indexes
│   │
│   ├─ Do most queries filter on a date/time column?
│   │   └─ YES → Range partitioning by date (most common)
│   │
│   ├─ Do most queries filter on a categorical column (region, status)?
│   │   └─ YES → List partitioning by category
│   │
│   ├─ Do you need even data distribution with no natural partition key?
│   │   └─ YES → Hash partitioning
│   │
│   └─ Do you need to DROP old data efficiently?
│       └─ YES → Range partitioning (DETACH + DROP partition)
│
└─ Table causes VACUUM issues (bloat, long autovacuum)
    └─ Range partitioning (VACUUM runs per partition)
```

---

## Quick Reference: Partition Types

| Type | PostgreSQL | MySQL | Best For |
|------|-----------|-------|----------|
| Range | `PARTITION BY RANGE (column)` | `PARTITION BY RANGE (column)` | Time-series, dates, sequential IDs |
| List | `PARTITION BY LIST (column)` | `PARTITION BY LIST (column)` | Categories, regions, status values |
| Hash | `PARTITION BY HASH (column)` | `PARTITION BY HASH (column)` | Even distribution, no natural key |
| Sub-partition | Range + List/Hash | Supported | Time + region combinations |

---

## PostgreSQL Declarative Partitioning

### Range Partitioning (By Date)

```sql
-- Create partitioned table
CREATE TABLE events (
    event_id    BIGSERIAL,
    event_type  TEXT NOT NULL,
    payload     JSONB,
    created_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (event_id, created_at)  -- partition key must be in PK
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE events_2026_01 PARTITION OF events
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');

CREATE TABLE events_2026_02 PARTITION OF events
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE TABLE events_2026_03 PARTITION OF events
    FOR VALUES FROM ('2026-03-01') TO ('2026-04-01');

-- Create default partition (catches rows that don't match any partition)
CREATE TABLE events_default PARTITION OF events DEFAULT;

-- Create indexes (automatically applies to all partitions)
CREATE INDEX idx_events_type ON events (event_type);
CREATE INDEX idx_events_created ON events (created_at);
```

### List Partitioning (By Category)

```sql
-- Create partitioned table
CREATE TABLE orders (
    order_id    BIGSERIAL,
    region      TEXT NOT NULL,
    amount      DECIMAL(10,2),
    created_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (order_id, region)
) PARTITION BY LIST (region);

-- Create partitions per region
CREATE TABLE orders_us PARTITION OF orders
    FOR VALUES IN ('US', 'CA');

CREATE TABLE orders_eu PARTITION OF orders
    FOR VALUES IN ('GB', 'DE', 'FR', 'ES', 'IT');

CREATE TABLE orders_apac PARTITION OF orders
    FOR VALUES IN ('JP', 'AU', 'SG', 'IN');

CREATE TABLE orders_default PARTITION OF orders DEFAULT;
```

### Hash Partitioning (Even Distribution)

```sql
-- Create partitioned table with 8 hash partitions
CREATE TABLE sessions (
    session_id  UUID NOT NULL,
    user_id     BIGINT,
    data        JSONB,
    created_at  TIMESTAMPTZ NOT NULL,
    PRIMARY KEY (session_id)
) PARTITION BY HASH (session_id);

-- Create hash partitions (modulus must be power of 2 or consistent)
CREATE TABLE sessions_p0 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 0);
CREATE TABLE sessions_p1 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 1);
CREATE TABLE sessions_p2 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 2);
CREATE TABLE sessions_p3 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 3);
CREATE TABLE sessions_p4 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 4);
CREATE TABLE sessions_p5 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 5);
CREATE TABLE sessions_p6 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 6);
CREATE TABLE sessions_p7 PARTITION OF sessions FOR VALUES WITH (MODULUS 8, REMAINDER 7);
```

### Sub-Partitioning

- Partition parent by RANGE (date), then sub-partition each by LIST (region) or HASH
- Use when queries commonly filter on both dimensions
- Keep sub-partition count manageable (partitions * sub-partitions total)

---

## MySQL Partitioning

### Range Partitioning

```sql
-- MySQL range partitioning (by date using TO_DAYS)
CREATE TABLE events (
    event_id    BIGINT AUTO_INCREMENT,
    event_type  VARCHAR(50) NOT NULL,
    payload     JSON,
    created_at  DATETIME NOT NULL,
    PRIMARY KEY (event_id, created_at)
) PARTITION BY RANGE (TO_DAYS(created_at)) (
    PARTITION p2026_01 VALUES LESS THAN (TO_DAYS('2026-02-01')),
    PARTITION p2026_02 VALUES LESS THAN (TO_DAYS('2026-03-01')),
    PARTITION p2026_03 VALUES LESS THAN (TO_DAYS('2026-04-01')),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);
```

### MySQL-Specific Constraints

| Constraint | Impact | Workaround |
|-----------|--------|------------|
| Partition key must be in every unique index | Limits PK and unique index design | Include partition column in composite PKs |
| No foreign keys on partitioned tables | Cannot reference or be referenced | Enforce at application level |
| Max 8192 partitions per table | Limits daily partitions to ~22 years | Use monthly/weekly granularity |
| Partition expression must be integer or function | Cannot partition on VARCHAR directly | Use HASH or convert to integer |

---

## Partition Key Selection

### Decision Criteria

| Criterion | Weight | Question |
|-----------|--------|----------|
| Query alignment | High | Do most WHERE clauses filter on this column? |
| Cardinality | Medium | Does the column produce reasonable partition counts? |
| Data distribution | Medium | Are values evenly distributed across partitions? |
| Retention alignment | High | Can old partitions be dropped for data lifecycle? |
| Insert pattern | Medium | Do new rows go to a single partition (append-only)? |

### Common Partition Keys

| Use Case | Partition Key | Type | Granularity |
|----------|--------------|------|-------------|
| Event logs | `created_at` | Range | Monthly or weekly |
| Time-series metrics | `timestamp` | Range | Daily or hourly |
| Multi-tenant SaaS | `tenant_id` | List or Hash | Per-tenant or hashed |
| Regional data | `region` | List | Per-region |
| IoT sensor data | `device_id` + `timestamp` | Hash + Range | Sub-partitioned |

### Partition Count Guidelines

| Granularity | Partitions/Year | Best For | Maintenance |
|-------------|----------------|----------|-------------|
| Hourly | 8,760 | Very high volume, short retention | High (automate) |
| Daily | 365 | High volume, weeks of retention | Medium |
| Weekly | 52 | Medium volume, months of retention | Low |
| Monthly | 12 | Standard analytics, years of retention | Low |
| Quarterly | 4 | Low volume, long retention | Very low |

---

## Maintenance Operations

### Creating Future Partitions

```sql
-- Automated partition creation (run monthly via cron/scheduler)
-- PostgreSQL

DO $$
DECLARE
    start_date DATE := DATE_TRUNC('month', CURRENT_DATE + INTERVAL '1 month');
    end_date DATE := start_date + INTERVAL '1 month';
    partition_name TEXT := 'events_' || TO_CHAR(start_date, 'YYYY_MM');
BEGIN
    EXECUTE format(
        'CREATE TABLE IF NOT EXISTS %I PARTITION OF events FOR VALUES FROM (%L) TO (%L)',
        partition_name, start_date, end_date
    );
    RAISE NOTICE 'Created partition: %', partition_name;
END $$;
```

### Detaching and Dropping Old Partitions

```sql
-- Step 1: Detach partition (fast, non-blocking in PG 14+)
ALTER TABLE events DETACH PARTITION events_2024_01 CONCURRENTLY;

-- Step 2: Optionally archive
-- pg_dump -t events_2024_01 dbname > /archive/events_2024_01.sql

-- Step 3: Drop
DROP TABLE events_2024_01;
```

### Retention Policy Automation

- Script: query `pg_tables` for partitions older than retention window
- For each: `ALTER TABLE parent DETACH PARTITION child`, then `DROP TABLE child`
- Schedule via cron or orchestrator (monthly for monthly partitions)

### Attaching Existing Tables as Partitions

```sql
-- Add constraint matching partition bounds FIRST (avoids full table scan)
ALTER TABLE legacy_events_2025_12
  ADD CONSTRAINT chk_partition CHECK (
    created_at >= '2025-12-01' AND created_at < '2026-01-01'
  );

-- Then attach (PostgreSQL validates constraint, skips scan if constraint matches)
ALTER TABLE events
  ATTACH PARTITION legacy_events_2025_12
  FOR VALUES FROM ('2025-12-01') TO ('2026-01-01');
```

---

## Query Optimization with Partition Pruning

### How Pruning Works

```
Query: SELECT * FROM events WHERE created_at >= '2026-01-15' AND created_at < '2026-02-15'

Without partitioning: Full table scan (all rows)
With partitioning:    Scans only events_2026_01 + events_2026_02 (2 partitions)
```

### Verifying Partition Pruning

```sql
-- EXPLAIN shows which partitions are scanned
EXPLAIN (COSTS OFF)
SELECT COUNT(*)
FROM events
WHERE created_at >= '2026-01-01'
  AND created_at < '2026-02-01';

-- Expected output shows only one partition:
-- Aggregate
--   ->  Seq Scan on events_2026_01 events
--         Filter: (created_at >= ... AND created_at < ...)
```

### Pruning Checklist

- [ ] Partition key appears in WHERE clause (required for pruning)
- [ ] Filter uses constants or parameters (not subqueries for static pruning)
- [ ] `enable_partition_pruning = on` in postgresql.conf (default: on)
- [ ] EXPLAIN shows only relevant partitions
- [ ] JOIN conditions on partition key enable pruning on both sides
- [ ] Avoid functions on partition key column: `WHERE DATE_TRUNC('month', created_at)` prevents pruning

### Queries That Defeat Pruning

| Query Pattern | Pruning? | Fix |
|--------------|----------|-----|
| `WHERE created_at > NOW() - INTERVAL '30 days'` | Yes (runtime pruning) | Good as-is |
| `WHERE DATE_TRUNC('month', created_at) = '2026-01-01'` | No (function on column) | `WHERE created_at >= '2026-01-01' AND created_at < '2026-02-01'` |
| `WHERE EXTRACT(YEAR FROM created_at) = 2026` | No (function on column) | Use range comparison |
| `WHERE created_at IN (SELECT ...)` | Limited | Use explicit range if possible |
| `WHERE created_at::date = '2026-01-15'` | No (cast on column) | `WHERE created_at >= '2026-01-15' AND created_at < '2026-01-16'` |

---

## Migration: Unpartitioned to Partitioned

### Strategy 1: Create New + Backfill (Recommended)

```sql
-- 1. Create new partitioned table
CREATE TABLE events_partitioned (
    LIKE events INCLUDING ALL
) PARTITION BY RANGE (created_at);

-- 2. Create partitions for all existing data
-- (generate these dynamically based on data range)
CREATE TABLE events_partitioned_2025_01 PARTITION OF events_partitioned
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');
-- ... repeat for each month ...

-- 3. Backfill data (in batches to avoid lock contention)
INSERT INTO events_partitioned
SELECT * FROM events
WHERE created_at >= '2025-01-01' AND created_at < '2025-02-01';
-- ... repeat per partition ...

-- 4. Verify row counts match
SELECT COUNT(*) FROM events;
SELECT COUNT(*) FROM events_partitioned;

-- 5. Swap tables (requires brief lock)
BEGIN;
ALTER TABLE events RENAME TO events_old;
ALTER TABLE events_partitioned RENAME TO events;
COMMIT;

-- 6. Verify application works, then drop old table
-- DROP TABLE events_old;  -- after validation period
```

### Strategy 2: pg_partman Extension

- `CREATE EXTENSION pg_partman` then `partman.create_parent()` with interval and premake count
- Set `infinite_time_partitions = true` and `retention` in `partman.part_config`
- pg_partman handles automatic creation and cleanup

### Migration Checklist

- [ ] Audit all queries against the table for partition key usage
- [ ] Verify partition key is included in primary key and unique indexes
- [ ] Test with representative data volume in staging
- [ ] Benchmark query performance before and after
- [ ] Plan maintenance window for table swap
- [ ] Update application connection strings if needed
- [ ] Set up automated partition creation for future periods
- [ ] Set up automated partition cleanup for retention
- [ ] Verify VACUUM operates per-partition
- [ ] Update monitoring dashboards

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Partitioning small tables (<1GB) | Overhead exceeds benefit | Use indexes instead |
| Too many partitions (>10,000) | Planning time increases, memory overhead | Use coarser granularity |
| Partition key not in queries | No pruning benefit, just complexity | Choose key based on query patterns |
| No default partition | Inserts fail for unexpected values | Always create DEFAULT partition |
| Manual partition creation | Missed partitions cause insert failures | Automate with pg_partman or cron |
| Forgetting indexes on partitions | Scans within partition are slow | CREATE INDEX on parent (auto-inherits) |
| Functions on partition key in WHERE | Defeats partition pruning | Use range comparisons directly |
| Never dropping old partitions | Table grows unbounded | Implement retention policy with DETACH + DROP |
| Migrating without testing queries | Performance regression for non-pruned queries | Benchmark all critical queries before migration |

---

## Cross-References

- `connection-pooling-patterns.md` — Connection management for partitioned table queries
- `monitoring-alerting-patterns.md` — Monitoring partition sizes and VACUUM progress
- `native-query-patterns.md` — Metabase query patterns that benefit from partitioning

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
