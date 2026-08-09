# Index Patterns

Purpose: choose, validate, and retire indexes based on workload evidence.

## Table of Contents

- [Start With the Workload](#start-with-the-workload)
- [Common Index Shapes](#common-index-shapes)
- [Composite Index Ordering](#composite-index-ordering)
- [PostgreSQL 18 Skip Scan](#postgresql-18-skip-scan)
- [Safe Index Retirement](#safe-index-retirement)
- [PostgreSQL](#postgresql)
- [MySQL](#mysql)
- [SQL Server](#sql-server)
- [Patterns](#patterns)
- [Pattern 1: Composite Filter + Sort](#pattern-1-composite-filter-sort)
- [Pattern 2: Covering Read Path](#pattern-2-covering-read-path)
- [Pattern 3: Partial / Filtered Index](#pattern-3-partial-filtered-index)
- [Pattern 4: Expression Index](#pattern-4-expression-index)
- [Anti-Patterns](#anti-patterns)
- [Verification Checklist](#verification-checklist)

## Start With the Workload

An index earns its keep when it materially improves an important read path without creating unacceptable write or storage cost.

Capture first:

- query text or normalized workload
- filter, join, and order-by columns
- row counts and selectivity
- read frequency vs write frequency
- before/after plan evidence

## Common Index Shapes

| Pattern | Best For | Notes |
|---------|----------|-------|
| Single-column B-tree | Equality and simple range filters | Default starting point for hot lookup predicates |
| Composite index | Equality + range + order combinations | Match the real access pattern, not a generic "most selective first" rule |
| Covering / INCLUDE | Hot reads that still need extra columns | Prefer INCLUDE columns over widening the search key when the engine supports it |
| Partial / filtered index | A stable hot subset of rows | Strong fit for active-state or tenant-scope filters |
| Functional / expression index | Filters on transformed values | Use only when the transformed predicate is part of the real workload |
| BRIN (PostgreSQL) | Very large append-heavy tables | Useful when physical locality is strong and B-tree is too expensive |
| Invisible index (MySQL) | Safe index-retirement trials | Hide first, monitor, then drop if the workload stays healthy |

## Composite Index Ordering

Good ordering usually follows this logic:

1. equality predicates that appear on almost every call
2. range predicate that narrows the scan
3. order-by columns if the sort is part of the hot path
4. extra projected columns as INCLUDE/covering columns where supported

Do not teach "most selective first" as a universal rule. Selectivity matters, but operator shape and ordering requirements matter more.

## PostgreSQL 18 Skip Scan

PostgreSQL 18 can use skip scan for some multicolumn B-tree cases where the leading column is not constrained by equality.

Use this as a bonus, not as a default design strategy:

- it helps most when the leading column has relatively low distinctness
- it does not mean every `(a, b)` index replaces an index on `b`
- verify with `EXPLAIN (ANALYZE, BUFFERS)`

## Safe Index Retirement

### PostgreSQL

- check usage with `pg_stat_user_indexes`
- compare write overhead and index size
- only drop after a representative observation window

### MySQL

- make the index invisible first
- monitor plans and latency
- drop only if the workload remains healthy

### SQL Server

- review usage DMVs and Query Store evidence
- be careful with indexes that exist mainly to avoid key lookups on a hot path

## Patterns

### Pattern 1: Composite Filter + Sort

```sql
-- Hot path: WHERE tenant_id = ? AND created_at >= ? ORDER BY created_at DESC
CREATE INDEX idx_orders_tenant_created_at
ON orders (tenant_id, created_at DESC);
```

### Pattern 2: Covering Read Path

```sql
-- PostgreSQL / SQL Server style
CREATE INDEX idx_orders_tenant_created_at
ON orders (tenant_id, created_at DESC)
INCLUDE (status, total_amount);
```

### Pattern 3: Partial / Filtered Index

```sql
CREATE INDEX idx_orders_open_created_at
ON orders (created_at DESC)
WHERE status IN ('pending', 'processing');
```

### Pattern 4: Expression Index

```sql
CREATE INDEX idx_users_lower_email
ON users (LOWER(email));
```

## Anti-Patterns

- indexing every foreign key, status field, or sort column without workload evidence
- duplicate indexes with the same leading key pattern
- putting low-value projected columns into the search key instead of INCLUDE
- assuming a composite index is automatically useful for every subset of its columns
- dropping an index because usage stats are low without checking batch jobs, reports, or failover paths

## Verification Checklist

- [ ] Important read path identified before index creation
- [ ] Query plan improved in a representative environment
- [ ] Write amplification and storage cost considered
- [ ] Composite key order matches the real filter/order pattern
- [ ] Retirement path uses usage stats or invisible-index testing
- [ ] PostgreSQL 18 skip scan treated as verified behavior, not assumption
