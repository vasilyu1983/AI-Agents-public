# Database Patterns

Comprehensive guide for PostgreSQL patterns, connection pooling, migration strategies, query optimization, ORM comparison, and index design. Use when designing data layers, choosing ORMs, optimizing queries, or planning schema migrations.

## Contents

- [PostgreSQL-Specific Patterns](#postgresql-specific-patterns)
- [Connection Pooling](#connection-pooling)
- [Migration Strategies](#migration-strategies)
- [ORM Comparison](#orm-comparison)
- [Index Design Patterns](#index-design-patterns)
- [Query Optimization](#query-optimization)
- [N+1 Detection and Prevention](#n1-detection-and-prevention)
- [Database Monitoring and Alerting](#database-monitoring-and-alerting)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)

---

## PostgreSQL-Specific Patterns

### JSONB for Semi-Structured Data

```sql
-- Store flexible metadata alongside relational data
CREATE TABLE products (
  id         UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name       TEXT NOT NULL,
  price      NUMERIC(10,2) NOT NULL,
  metadata   JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Index JSONB for fast queries
CREATE INDEX idx_products_metadata ON products USING GIN (metadata);

-- Query nested JSONB fields
SELECT name, price, metadata->>'color' AS color
FROM products
WHERE metadata @> '{"category": "electronics"}';

-- Partial JSONB index (only index specific keys)
CREATE INDEX idx_products_category ON products
  USING GIN ((metadata->'tags'));
```

**When to use JSONB vs separate tables:**

| JSONB | Separate Table |
|-------|----------------|
| Schema varies per row | Schema is uniform |
| Query patterns are simple (key lookup) | Complex joins and aggregations |
| Data is read-mostly | Data is frequently updated at field level |
| Fewer than 10-20 keys | Dozens of structured columns |

### Common Table Expressions (CTEs)

```sql
-- Recursive CTE: org hierarchy
WITH RECURSIVE org_tree AS (
  -- Base case: top-level managers
  SELECT id, name, manager_id, 1 AS depth
  FROM employees
  WHERE manager_id IS NULL

  UNION ALL

  -- Recursive case: subordinates
  SELECT e.id, e.name, e.manager_id, ot.depth + 1
  FROM employees e
  INNER JOIN org_tree ot ON e.manager_id = ot.id
  WHERE ot.depth < 10  -- safety limit to prevent infinite recursion
)
SELECT * FROM org_tree ORDER BY depth, name;

-- Non-recursive CTE: complex multi-step query
WITH monthly_revenue AS (
  SELECT
    date_trunc('month', created_at) AS month,
    SUM(total) AS revenue
  FROM orders
  WHERE status = 'completed'
  GROUP BY 1
),
monthly_growth AS (
  SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) AS prev_revenue,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month))
      / NULLIF(LAG(revenue) OVER (ORDER BY month), 0) * 100, 1) AS growth_pct
  FROM monthly_revenue
)
SELECT * FROM monthly_growth ORDER BY month DESC;
```

### Window Functions

```sql
-- Running totals and rankings
SELECT
  id,
  customer_id,
  total,
  -- Running total per customer
  SUM(total) OVER (
    PARTITION BY customer_id
    ORDER BY created_at
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  ) AS running_total,
  -- Rank within customer orders
  ROW_NUMBER() OVER (
    PARTITION BY customer_id
    ORDER BY total DESC
  ) AS rank_by_amount,
  -- Percentile
  PERCENT_RANK() OVER (ORDER BY total) AS percentile
FROM orders;
```

### Table Partitioning

```sql
-- Range partitioning by date (ideal for time-series data)
CREATE TABLE events (
  id         UUID NOT NULL DEFAULT gen_random_uuid(),
  event_type TEXT NOT NULL,
  payload    JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE events_2026_01 PARTITION OF events
  FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE events_2026_02 PARTITION OF events
  FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Automate partition creation with pg_partman
-- or create partitions via migration scripts

-- Benefits:
-- 1. Fast partition pruning (only scan relevant months)
-- 2. Easy data archival (DROP old partitions)
-- 3. Parallel query across partitions
-- 4. Smaller indexes per partition
```

### Advisory Locks

```sql
-- Distributed locking without external tools
-- Use for: migrations, batch jobs, singleton processes

-- Try to acquire lock (non-blocking)
SELECT pg_try_advisory_lock(hashtext('batch-job-daily-report'));
-- Returns true if acquired, false if already held

-- Acquire lock (blocking)
SELECT pg_advisory_lock(hashtext('batch-job-daily-report'));

-- Release lock
SELECT pg_advisory_unlock(hashtext('batch-job-daily-report'));

-- Session-level locks auto-release on disconnect
-- Transaction-level: pg_advisory_xact_lock (auto-release on commit/rollback)
```

---

## Connection Pooling

### Why Connection Pooling Matters

```text
Each PostgreSQL connection costs:
  - ~5-10MB of RAM on the server
  - A new backend process (fork)
  - Kernel resources (file descriptors, context switches)

Typical limits:
  - PostgreSQL default max_connections: 100
  - Managed Postgres (AWS RDS, Supabase): 20-500 depending on instance size
  - Serverless/Edge: Connections are especially scarce (many functions, few connections)
```

### Pooling Strategies

| Strategy | Description | Best For |
|----------|-------------|----------|
| PgBouncer (external) | Standalone connection pool proxy | Multiple services, serverless |
| Prisma connection pool | Built into Prisma client | Prisma-based apps |
| Drizzle + `postgres` driver pool | Driver-level pooling | Drizzle-based apps |
| Neon pooler / Supabase pooler | Managed pooling service | Serverless, edge functions |

### PgBouncer Configuration

```ini
; pgbouncer.ini
[databases]
myapp = host=postgres port=5432 dbname=myapp

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt

; Pool mode:
;   session   = connection held for entire session (default, safest)
;   transaction = connection returned after each transaction (most efficient)
;   statement = connection returned after each statement (most restrictive)
pool_mode = transaction

; Pool sizing
default_pool_size = 20       ; connections per user/database pair
max_client_conn = 200        ; max clients connected to PgBouncer
reserve_pool_size = 5        ; extra connections for burst
reserve_pool_timeout = 3     ; seconds before using reserve pool

; Timeouts
server_idle_timeout = 600    ; close idle server connections after 10 min
client_idle_timeout = 0      ; no client idle timeout
query_timeout = 30           ; kill queries running longer than 30s
```

### Prisma Connection Pool Tuning

```typescript
import { PrismaClient } from '@prisma/client';

const prisma = new PrismaClient({
  datasources: {
    db: {
      url: process.env.DATABASE_URL,
    },
  },
  // Connection pool settings via URL parameters:
  // postgresql://user:pass@host:5432/db?connection_limit=10&pool_timeout=10
});

// Or use Prisma Accelerate for serverless pooling:
// DATABASE_URL="prisma://accelerate.prisma-data.net/?api_key=..."
```

### Connection Pool Sizing Formula

```text
Optimal pool size per service instance:
  pool_size = (number_of_cpu_cores * 2) + number_of_disks

For a 4-core machine with SSD:
  pool_size = (4 * 2) + 1 = 9 connections

Total across all instances:
  total_connections = pool_size * num_instances

MUST be less than PostgreSQL max_connections
(leave headroom for admin connections and monitoring)
```

---

## Migration Strategies

### Strategy Comparison

| Strategy | Description | Downtime | Risk |
|----------|-------------|----------|------|
| Expand-Contract | Add new → migrate data → remove old | Zero | Low |
| Backward-Compatible | New schema works with old AND new code | Zero | Low |
| Shadow Table | Write to both during transition | Zero | Medium |
| Blue-Green DB | Two databases, switch at cutover | Brief | Medium |
| Big Bang | Apply all changes at once, deploy new code | Required | High |

### Expand-Contract Pattern (Recommended)

```text
Phase 1: EXPAND — Add new column/table (backward-compatible)
  ├─ Migration: ALTER TABLE users ADD COLUMN email_verified BOOLEAN DEFAULT false;
  ├─ Deploy: Old code ignores new column, new code can use it
  └─ Duration: Deploy new code progressively

Phase 2: MIGRATE — Backfill data
  ├─ Script: UPDATE users SET email_verified = true WHERE verified_at IS NOT NULL;
  ├─ Run in batches to avoid locking
  └─ Duration: Depends on table size

Phase 3: CONTRACT — Remove old column/table
  ├─ Migration: ALTER TABLE users DROP COLUMN verified_at;
  ├─ Deploy: All code now uses new column
  └─ Duration: After all code uses new schema
```

### Batch Migration for Large Tables

```sql
-- Never run unbounded UPDATEs on large tables
-- Bad: UPDATE users SET status = 'active' WHERE old_status = 1;  -- locks entire table

-- Good: Batch update with progress tracking
DO $$
DECLARE
  batch_size INT := 1000;
  updated INT;
BEGIN
  LOOP
    UPDATE users
    SET status = 'active'
    WHERE id IN (
      SELECT id FROM users
      WHERE old_status = 1 AND status IS NULL
      LIMIT batch_size
      FOR UPDATE SKIP LOCKED
    );

    GET DIAGNOSTICS updated = ROW_COUNT;
    RAISE NOTICE 'Updated % rows', updated;

    IF updated = 0 THEN EXIT; END IF;

    -- Brief pause to reduce lock contention
    PERFORM pg_sleep(0.1);
  END LOOP;
END $$;
```

### Zero-Downtime Column Rename

```text
Step 1: Add new column
  ALTER TABLE users ADD COLUMN full_name TEXT;

Step 2: Backfill (batched)
  UPDATE users SET full_name = name WHERE full_name IS NULL; -- batched

Step 3: Deploy code that writes to BOTH columns
  -- Application writes to both 'name' and 'full_name'

Step 4: Deploy code that reads from new column
  -- Application reads from 'full_name', still writes to both

Step 5: Drop old column
  ALTER TABLE users DROP COLUMN name;

NEVER use ALTER TABLE ... RENAME COLUMN in production with live traffic.
```

---

## ORM Comparison

### Prisma vs Drizzle vs Raw SQL

| Feature | Prisma | Drizzle | Raw SQL (Kysely/sqlc) |
|---------|--------|---------|----------------------|
| Type safety | Generated types from schema | Schema-as-code types | Generated from SQL / builder |
| Learning curve | Low (schema DSL) | Low (SQL-like TS API) | Medium (SQL knowledge) |
| Migration approach | Prisma Migrate (declarative) | Drizzle Kit (SQL-based) | Manual SQL files |
| Query complexity | Great for CRUD, limited for complex SQL | Handles complex SQL well | Full SQL power |
| Performance | Good (query engine overhead) | Excellent (thin layer) | Best (direct driver) |
| Edge/Serverless | Prisma Accelerate, or driver adapters | Native, lightweight | Native |
| Introspection | Schema pull from existing DB | Schema pull | N/A (you write SQL) |
| Relations | Declarative, auto joins | Explicit joins (SQL-like) | Manual joins |
| Best for | Rapid development, CRUD-heavy | Performance-sensitive, SQL-experienced teams | Complex queries, DBA teams |

### Decision Criteria

```text
Choosing ORM/query layer:
  ├─ Fast prototyping, CRUD-heavy → Prisma (best DX, generated types)
  ├─ Performance-sensitive, complex queries → Drizzle (SQL-like, thin layer)
  ├─ Legacy DB, need full SQL control → Raw SQL + Kysely (type-safe builder)
  ├─ Edge/Serverless deployment → Drizzle or Prisma w/ driver adapters
  └─ Go/Rust backend → GORM/SeaORM (see language-specific guides)
```

### Prisma Example

```typescript
// schema.prisma
// model User {
//   id        String   @id @default(uuid())
//   email     String   @unique
//   orders    Order[]
//   createdAt DateTime @default(now())
// }

// Type-safe queries
const user = await prisma.user.findUnique({
  where: { email: 'user@example.com' },
  include: { orders: { take: 5, orderBy: { createdAt: 'desc' } } },
});

// Transaction
const [order, inventory] = await prisma.$transaction([
  prisma.order.create({ data: { userId: user.id, total: 99.99 } }),
  prisma.inventory.update({
    where: { productId: 'abc' },
    data: { quantity: { decrement: 1 } },
  }),
]);
```

### Drizzle Example

```typescript
import { pgTable, uuid, text, numeric, timestamp } from 'drizzle-orm/pg-core';
import { eq, desc } from 'drizzle-orm';

// Schema as TypeScript code
export const users = pgTable('users', {
  id: uuid('id').primaryKey().defaultRandom(),
  email: text('email').notNull().unique(),
  createdAt: timestamp('created_at').defaultNow().notNull(),
});

export const orders = pgTable('orders', {
  id: uuid('id').primaryKey().defaultRandom(),
  userId: uuid('user_id').references(() => users.id).notNull(),
  total: numeric('total', { precision: 10, scale: 2 }).notNull(),
});

// SQL-like queries
const userOrders = await db
  .select()
  .from(users)
  .leftJoin(orders, eq(users.id, orders.userId))
  .where(eq(users.email, 'user@example.com'))
  .orderBy(desc(orders.total))
  .limit(5);
```

---

## Index Design Patterns

### Index Types

| Index Type | Use When | Example |
|------------|----------|---------|
| B-tree (default) | Equality, range, sorting, prefix LIKE | `CREATE INDEX idx_email ON users (email)` |
| GIN | JSONB containment, array overlap, full-text | `CREATE INDEX idx_meta ON products USING GIN (metadata)` |
| GiST | Geometric, range types, full-text (ranking) | `CREATE INDEX idx_geo ON locations USING GIST (coordinates)` |
| BRIN | Large sequential/append-only tables (time-series) | `CREATE INDEX idx_time ON events USING BRIN (created_at)` |
| Hash | Equality-only (rare, B-tree is usually better) | `CREATE INDEX idx_hash ON sessions USING HASH (token)` |

### Partial Indexes

```sql
-- Index only active users (much smaller index)
CREATE INDEX idx_active_users ON users (email)
  WHERE deleted_at IS NULL;

-- Index only recent orders
CREATE INDEX idx_recent_orders ON orders (created_at DESC)
  WHERE status IN ('pending', 'processing');

-- Index only non-null values
CREATE INDEX idx_tracking ON shipments (tracking_number)
  WHERE tracking_number IS NOT NULL;
```

### Composite Index Design

```sql
-- Column order matters: put equality columns first, range columns last
-- For query: WHERE status = 'active' AND created_at > '2026-01-01'
CREATE INDEX idx_status_created ON orders (status, created_at);

-- Covering index: includes all columns needed by query (index-only scan)
CREATE INDEX idx_orders_covering ON orders (status, created_at)
  INCLUDE (total, customer_id);

-- This query can be answered entirely from the index:
SELECT total, customer_id FROM orders
WHERE status = 'active' AND created_at > '2026-01-01';
```

### Index Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Index every column | Write performance degrades, storage bloat | Index only queried columns |
| Missing composite index | Sequential scans on filtered + sorted queries | Analyze query patterns, add composites |
| Unused indexes | Storage and write overhead for no read benefit | Check `pg_stat_user_indexes` for unused indexes |
| Over-indexing JSONB | GIN indexes on large JSONB are expensive | Use partial GIN or expression indexes |

```sql
-- Find unused indexes
SELECT
  schemaname, relname AS table, indexrelname AS index,
  idx_scan AS times_used, pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Query Optimization

### EXPLAIN ANALYZE Checklist

```sql
-- Always use EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) for optimization
EXPLAIN (ANALYZE, BUFFERS)
SELECT u.email, COUNT(o.id) AS order_count
FROM users u
LEFT JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2025-01-01'
GROUP BY u.email
ORDER BY order_count DESC
LIMIT 10;
```

**What to look for:**

| Red Flag | Meaning | Fix |
|----------|---------|-----|
| `Seq Scan` on large table | No useful index | Add appropriate index |
| `Sort` with high cost | In-memory or disk sort | Add index matching ORDER BY |
| `Nested Loop` with high rows | N+1 at database level | Consider Hash Join (rewrite query) |
| `Rows Removed by Filter` >> actual rows | Index not selective enough | More selective index or partial index |
| `Buffers: shared read` >> `shared hit` | Data not cached | Increase `shared_buffers` or optimize query |

### Query Optimization Checklist

- [ ] Use `EXPLAIN ANALYZE` to verify the query plan
- [ ] Ensure indexes exist for WHERE, JOIN, and ORDER BY columns
- [ ] Avoid `SELECT *` — select only needed columns
- [ ] Use `LIMIT` for paginated queries
- [ ] Replace correlated subqueries with JOINs or CTEs
- [ ] Use `EXISTS` instead of `IN` for large subqueries
- [ ] Batch INSERTs (use `unnest` or multi-row INSERT)
- [ ] Set `statement_timeout` on application queries
- [ ] Monitor slow queries via `pg_stat_statements`

---

## N+1 Detection and Prevention

### The N+1 Problem

```typescript
// N+1: 1 query for users + N queries for orders
const users = await db.query('SELECT * FROM users LIMIT 100');
for (const user of users) {
  // This runs 100 separate queries!
  user.orders = await db.query('SELECT * FROM orders WHERE user_id = $1', [user.id]);
}

// Fix 1: JOIN (single query)
const usersWithOrders = await db.query(`
  SELECT u.*, o.id AS order_id, o.total
  FROM users u
  LEFT JOIN orders o ON o.user_id = u.id
  LIMIT 100
`);

// Fix 2: Batch load (2 queries)
const users = await db.query('SELECT * FROM users LIMIT 100');
const userIds = users.map(u => u.id);
const orders = await db.query('SELECT * FROM orders WHERE user_id = ANY($1)', [userIds]);
// Group orders by user in application code
```

### ORM-Level Prevention

```typescript
// Prisma: use include/select (eager loading)
const users = await prisma.user.findMany({
  include: { orders: true },  // Single query with JOIN
  take: 100,
});

// Drizzle: explicit join
const result = await db
  .select()
  .from(users)
  .leftJoin(orders, eq(users.id, orders.userId))
  .limit(100);
```

### Detection Tools

| Tool | How It Detects | Language |
|------|---------------|---------|
| Prisma query log | Shows all SQL queries | TypeScript |
| pg_stat_statements | Tracks query frequency and duration | PostgreSQL |
| DataLoader pattern | Batches multiple lookups into single query | Any (GraphQL) |
| OpenTelemetry DB spans | Trace shows repeated similar queries | Any |

---

## Database Monitoring and Alerting

### Key Metrics

| Metric | Source | Alert Threshold |
|--------|--------|-----------------|
| Active connections | `pg_stat_activity` | > 80% of `max_connections` |
| Long-running queries | `pg_stat_activity` | > 30s duration |
| Dead tuples (bloat) | `pg_stat_user_tables` | > 10% of live tuples |
| Replication lag | `pg_stat_replication` | > 10s |
| Cache hit ratio | `pg_stat_database` | < 99% |
| Transaction rate | `pg_stat_database` | Sudden drop or spike |
| Disk usage | OS / cloud metrics | > 80% capacity |
| Lock waits | `pg_stat_activity` | > 5s wait time |

### Essential Monitoring Queries

```sql
-- Active connections by state
SELECT state, COUNT(*) FROM pg_stat_activity
WHERE datname = current_database()
GROUP BY state;

-- Long-running queries
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '10 seconds'
ORDER BY duration DESC;

-- Cache hit ratio (should be > 99%)
SELECT
  sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0) AS ratio
FROM pg_statio_user_tables;

-- Table bloat estimate
SELECT
  relname AS table,
  n_dead_tup AS dead_rows,
  n_live_tup AS live_rows,
  ROUND(n_dead_tup::numeric / NULLIF(n_live_tup, 0) * 100, 1) AS dead_pct,
  last_autovacuum
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY dead_pct DESC;

-- Top queries by total time (requires pg_stat_statements extension)
SELECT
  queryid,
  calls,
  ROUND(total_exec_time::numeric, 2) AS total_time_ms,
  ROUND(mean_exec_time::numeric, 2) AS mean_time_ms,
  ROUND((stddev_exec_time)::numeric, 2) AS stddev_ms,
  LEFT(query, 100) AS query_preview
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;
```

---

## Anti-Patterns

| Anti-Pattern | Impact | Fix |
|-------------|--------|-----|
| No connection pooling | Connection exhaustion | PgBouncer or ORM pool |
| Missing indexes on foreign keys | Slow JOINs and CASCADE deletes | Index all FK columns |
| `SELECT *` everywhere | Wasted bandwidth, prevents index-only scans | Select only needed columns |
| Large transactions | Lock contention, replication lag | Keep transactions short and focused |
| No query timeout | Runaway queries consume connections | `statement_timeout = '30s'` |
| Storing files in database | Bloated tables, slow backups | Use object storage (S3) + URL reference |
| UUID v4 as primary key without care | B-tree index fragmentation | Use UUIDv7 (time-ordered) or BIGSERIAL |
| No `VACUUM` monitoring | Table bloat, slow scans | Monitor `autovacuum`, tune settings |

---

## Cross-References

- [nodejs-best-practices.md](nodejs-best-practices.md) — Node.js-specific database connection patterns
- [go-best-practices.md](go-best-practices.md) — GORM and Go database patterns
- [python-best-practices.md](python-best-practices.md) — SQLAlchemy patterns
- [rust-best-practices.md](rust-best-practices.md) — SeaORM and SQLx patterns
- [message-queues-background-jobs.md](message-queues-background-jobs.md) — Background jobs that interact with databases
- [infrastructure-economics.md](infrastructure-economics.md) — Database cost optimization
- [../../data-sql-optimization/SKILL.md](../../data-sql-optimization/SKILL.md) — Deep SQL optimization and indexing strategies
- [../../software-architecture-design/references/data-architecture-patterns.md](../../software-architecture-design/references/data-architecture-patterns.md) — CQRS, event sourcing, polyglot persistence
