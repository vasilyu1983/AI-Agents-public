# Index Patterns

Purpose: choose, validate, and retire indexes based on workload evidence.

## Table of Contents

- [Start With the Workload](#start-with-the-workload)
- [Common Index Shapes](#common-index-shapes)
- [Composite Index Ordering](#composite-index-ordering)
- [Index-Table Correlation and Clustering](#index-table-correlation-and-clustering)
- [Index-Only Scans Are Fragile](#index-only-scans-are-fragile)
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

## Index-Table Correlation and Clustering

An index tells you *which* rows match. Fetching them is a separate cost, and it
depends on how the matching rows are physically laid out. Winand calls the
index-vs-table ordering relationship the **index clustering factor**, *"an indirect
measure of the probability that two succeeding index entries refer to the same table
block"* (*SQL Performance Explained*, ch. 5, p. 114). The optimizer charges the
table-access step according to that probability.

The practical consequence:

- **Well-correlated index** — matching rows sit in a few adjacent blocks, so the heap
  fetch is a handful of reads. Winand: *"When using an index with a good clustering
  factor, the selected tables rows are stored closely together so that the database
  only needs to read a few table blocks to get all the rows"* (p. 119).
- **Poorly correlated index** — each matching row may be a separate random read. Wide
  range scans get expensive fast, and past some selectivity the planner correctly
  prefers a sequential scan.

In PostgreSQL, read this from `pg_stats.correlation` (see
[explain-analysis.md](explain-analysis.md#index-table-correlation-clustering-factor)
for the query and how it drives the seq-scan flip).

### Design Implications

- **Append-ordered keys correlate for free.** A table that only grows chronologically
  has heap order matching timestamp order. Winand's example: an index on the sale date
  had the better clustering factor *"because the SALES table only grows chronologically.
  New rows are always appended to the end of the table as long as there are no rows
  deleted"* (p. 119). This is the concrete argument for time-ordered surrogate keys
  (`uuidv7()` in PostgreSQL 18, or a bigint sequence) over random UUIDv4 in
  append-heavy OLTP.
- **You can optimize the heap for one index only.** Reordering rows to match an index
  is possible (PostgreSQL `CLUSTER`, SQL Server clustered index choice) but you have
  one physical order to spend. Winand: *"you can only store the table rows in one
  sequence. That means you can optimize the table for one index only"* (p. 113), and
  he calls row sequencing *"a rather impractical approach"* for most cases. In
  PostgreSQL specifically, `CLUSTER` takes an ACCESS EXCLUSIVE lock and does not
  maintain the order afterward — new updates re-scatter rows.
- **Good correlation can make a covering index unnecessary.** If the rows are already
  clustered, the heap fetch is cheap and the index-only scan buys little. Winand:
  *"Some indexes have a good clustering factor automatically so that the performance
  advantage of an index-only scan is minimal"* (p. 119).
- **BRIN depends entirely on this.** BRIN stores per-block-range summaries, so it is
  useful precisely when physical locality is strong and useless when it is not.

## Index-Only Scans Are Fragile

An index-only scan avoids the table entirely when the index carries every column the
statement touches — `WHERE`, `SELECT`, `ORDER BY`, all of them. It is a large win when
it applies, and it silently stops applying.

**Any non-covered column reverts you to heap fetches.** Adding one column to the
`WHERE` clause is enough, even when it makes the result set *smaller*. Winand shows a
query that got slower by becoming more selective, because the new predicate column was
not in the index and forced a table access; his framing is that *"The relevant factor
is not how many rows the query delivers but how many rows the database must inspect to
find them"* (ch. 5, p. 118). His warning: *"Extending the where clause can cause
'illogical' performance behavior. Check the execution plan before extending queries"*
(p. 118).

Two more ways to lose it quietly:

- **Adding a column to the `SELECT` list.** Worse than a `WHERE` change, because a new
  predicate can at least open a different access path, while a projection change cannot.
- **Expression indexes.** An index on `LOWER(email)` cannot serve an index-only scan
  that selects `email` — the original value is not stored. Winand: *"Always aim to
  index the original data as that is often the most useful information you can put
  into an index."*

**PostgreSQL adds a visibility-map dependence.** The index does not record row
visibility, so PostgreSQL must confirm each row is visible to the transaction. It skips
that check only for heap pages marked all-visible in the visibility map, which
`VACUUM` maintains. On a table with vacuum lag or heavy churn, a plan that says
`Index Only Scan` can still do large numbers of heap fetches — visible in the plan as
`Heap Fetches:`. A non-trivial `Heap Fetches` count means the scan is index-only in
name only; the fix is vacuum health, not index design.

Practical stance: index the `WHERE` clause first and extend for covering only when
measurement justifies it. Winand: *"Do not design an index for an index-only scan on
suspicion only because it unnecessarily uses memory and increases the maintenance
effort needed for update statements."* Where the engine supports `INCLUDE`, prefer it
for the projection-only columns — they widen the leaf without widening the search key.
And leave a comment on the index saying an index-only scan depends on it, so the next
person adding a column knows what they are about to break.

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
