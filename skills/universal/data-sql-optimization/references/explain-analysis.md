# EXPLAIN Analysis Patterns

Purpose: read query plans as evidence, not folklore. Use this guide when a user has a slow query, a suspected bad index, or a regression after schema/data changes.

## Table of Contents

- [Start With the Right Capture](#start-with-the-right-capture)
- [Read Plans in This Order](#read-plans-in-this-order)
- [Access Predicates vs Filter Predicates](#access-predicates-vs-filter-predicates)
- [Index-Table Correlation (Clustering Factor)](#index-table-correlation-clustering-factor)
- [What Usually Matters](#what-usually-matters)
- [1. Access Path](#1-access-path)
- [2. Cardinality Estimation](#2-cardinality-estimation)
- [3. Joins](#3-joins)
- [4. Sorts, Materialization, and Spills](#4-sorts-materialization-and-spills)
- [5. Concurrency](#5-concurrency)
- [Symptom -> Likely Next Step](#symptom-likely-next-step)
- [Vendor-Specific Notes](#vendor-specific-notes)
- [PostgreSQL](#postgresql)
- [MySQL](#mysql)
- [SQL Server](#sql-server)
- [SQLite](#sqlite)
- [Common Mistakes](#common-mistakes)
- [Verification Checklist](#verification-checklist)

## Start With the Right Capture

| Engine | Preferred Capture | Use When |
|--------|-------------------|----------|
| PostgreSQL | `EXPLAIN (ANALYZE, BUFFERS, VERBOSE)` | Safe to execute the query in a production-like environment |
| MySQL | `EXPLAIN ANALYZE` or `EXPLAIN FORMAT=JSON` | `EXPLAIN ANALYZE` is safe enough for the workload; otherwise use JSON plus runtime stats |
| SQL Server | Actual execution plan + `SET STATISTICS IO, TIME ON` | You need operator costs plus I/O and CPU evidence |
| Oracle | `DBMS_XPLAN.DISPLAY_CURSOR` or `DBMS_XPLAN.DISPLAY` | You need optimizer plan details from a real cursor |
| SQLite | `EXPLAIN QUERY PLAN` | You need index and scan behavior for a local or embedded database |

If running the query is risky, capture an estimated plan plus live wait, lock, and query-stat evidence instead of guessing.

## Read Plans in This Order

1. Find the operators with the highest elapsed time or repeated loops.
2. Compare rows read vs rows returned.
3. Check whether the issue is:
   - access path
   - cardinality estimation
   - sort/hash spill
   - concurrency or blocking
4. Only then decide whether the fix is query shape, statistics, index design, or configuration.

## Access Predicates vs Filter Predicates

The single most useful distinction when reading an index scan. Every `WHERE` term
lands in one of two roles, and they cost very different amounts:

- **Access predicate** — limits the *scanned index range*. The engine traverses the
  B-tree to the first matching entry and stops at the last one. Work is proportional
  to matching entries.
- **Filter predicate** — evaluated per row *during* the leaf-node traversal (or after
  the heap fetch). It removes rows but does **not** narrow the scan. Work is
  proportional to the rows the access predicate let through.

Winand's framing: an index scan is slow when "the database reads a wide index range
and has to fetch many rows individually" (*SQL Performance Explained*, ch. 2,
p. 21). A filter predicate does nothing to make that range narrower.

### Reading This in PostgreSQL

PostgreSQL exposes the split directly in the plan node:

```text
Index Scan using idx_orders_tenant on orders
  Index Cond: (tenant_id = 42)              <- access predicate: narrows the scan
  Filter: (upper(customer_name) ~~ '%INA%') <- filter predicate: does not narrow it
  Rows Removed by Filter: 4831
```

Signal reading:

| Line | Meaning |
|------|---------|
| `Index Cond:` | Access predicate. This is the term doing the real work. |
| `Filter:` | Filter predicate. Applied per row; the scan was already that wide. |
| `Rows Removed by Filter:` | How much of the scan was wasted. Large value = the access predicate is too loose. |

A large `Rows Removed by Filter` next to a small final row count is the canonical
"wide range, narrow result" signature. It means the access predicate is not
selective enough, not that the query is inherently expensive.

Note that a predicate on an indexed column can still appear under `Filter:` — being
indexed is not the same as being usable as an access predicate.

### Why a Second-Column-Only Match Degenerates to Filter-Only

A multi-column B-tree is ordered by its leading column first. Entries are sorted by
`(a, b)`, so all rows for a given `b` are scattered across the whole index unless `a`
is constrained. Given `CREATE INDEX ON t (a, b)`:

- `WHERE a = ? AND b = ?` — both can be access predicates. Tight range.
- `WHERE a = ?` alone — `a` is an access predicate. Fine.
- `WHERE b = ?` alone — nothing narrows the traversal. If the planner uses the index
  at all, `b` becomes a **filter predicate** over a full index scan, and the scan is
  effectively the whole index with a per-row test. Column order is not cosmetic.

Winand's warning applies directly: the common advice to "index every column in the
where clause" *"ignores the relevance of the column order which determines what
conditions can be used as access predicates and thus has a huge impact on
performance"* (ch. 5, p. 115).

Caveat, since PostgreSQL 18: skip scan can make some leading-column-unconstrained
multicolumn cases usable, most when the leading column has low distinctness. Treat
that as verified-per-plan behavior, not a reason to stop caring about column order.

### When a Filter Predicate Is the Right Answer

Filter predicates are not automatically a bug. Winand's "index filter predicates used
intentionally" case: a predicate that *cannot* serve as an access predicate — a `LIKE`
with a leading wildcard, for instance — can still be worth adding to the index so it
is evaluated during the index scan rather than after the table fetch. That does not
narrow the index range, but it discards rows before the heap access, cutting the
number of table fetches.

Winand's rule for this: *"Don't introduce a new index for the sole purpose of filter
predicates. Extend an existing index instead and keep the maintenance effort low"*
(ch. 5, p. 115). The index also gets bigger, so use it deliberately.

## Index-Table Correlation (Clustering Factor)

An index range scan returns row pointers; the engine must still fetch those rows from
the heap. What that costs depends on whether the matching rows sit in a few adjacent
table blocks or are scattered across thousands. Winand's note:

> The correlation between index order and table order is a performance benchmark —
> the so-called index clustering factor.
>
> — *SQL Performance Explained*, ch. 5, p. 113

He defines it as *"an indirect measure of the probability that two succeeding index
entries refer to the same table block"* (p. 114), and the optimizer folds that
probability into the cost of the table-access step.

### The PostgreSQL-Visible Measure

PostgreSQL exposes this as `pg_stats.correlation` — the statistical correlation
between physical row order and logical column order, ranging -1 to 1:

```sql
SELECT tablename, attname, correlation, n_distinct
FROM pg_stats
WHERE schemaname = 'public' AND tablename = 'orders'
ORDER BY abs(correlation);
```

- `|correlation|` near 1 — index order tracks heap order. A range scan reads few heap
  blocks. Append-only timestamp columns typically look like this.
- `|correlation|` near 0 — index order says nothing about heap placement. Each index
  entry may mean a separate random heap read. Random-UUID keys and heavily updated
  columns land here.

### Why the Planner Flips to Seq Scan

With low correlation, the estimated cost of an index range scan rises roughly with the
number of matching rows, because each one is charged closer to a random page read.
Past a modest fraction of the table, a sequential scan — reading every block, but
sequentially — wins on total cost. That flip is usually the planner being *right*, not
a misestimate. Before overriding it, check whether correlation, not the index, is the
problem.

Design implications and the row-clustering tradeoff live in
[index-patterns.md](index-patterns.md#index-table-correlation-and-clustering).

## What Usually Matters

### 1. Access Path

- A sequential scan or table scan is not automatically wrong. It is often correct for small tables or low-selectivity filters.
- The real problem is usually one of these:
  - many pages read to return few rows
  - a predicate that prevents index use
  - a composite index that does not match the actual filter/order pattern

### 2. Cardinality Estimation

- Large estimated-vs-actual row mismatches usually point to stale or insufficient statistics.
- Preferred fixes by engine:
  - PostgreSQL: `ANALYZE`, then `CREATE STATISTICS` for correlated predicates
  - MySQL: refresh optimizer stats and use histograms where value distribution matters
  - SQL Server: inspect Query Store, parameter sensitivity, and current cardinality behavior before hinting

### 3. Joins

- Nested loop, hash join, and merge join can all be correct.
- Focus on:
  - the size of the build/probe inputs
  - whether the join predicates are sargable
  - whether spills or repeated rescans are happening
- Do not rewrite a query just because a hash join appears.

### 4. Sorts, Materialization, and Spills

- Sorts and hash tables become important when they spill to disk or temp storage.
- Typical levers:
  - reduce rows earlier
  - add an index that satisfies the filter and order
  - adjust memory settings only after confirming query shape is reasonable

### 5. Concurrency

- A query can look expensive when the real bottleneck is waiting.
- Pair plan analysis with:
  - PostgreSQL: `pg_stat_activity`, `pg_locks`, wait events
  - MySQL: Performance Schema waits, metadata locks
  - SQL Server: wait stats, blocked process reports, Query Store runtime stats

## Symptom -> Likely Next Step

| Symptom | Usually Means | Prefer This Next Step |
|---------|---------------|-----------------------|
| Big rows-read / rows-returned gap | Access path or predicate issue | Check predicate shape and relevant index design |
| Actual rows far above estimate | Estimator drift | Refresh stats; add extended stats or histograms if needed |
| Sort or hash spills | Too much data reaches a memory-bound operator | Reduce rows earlier or add an order-aligned index |
| Key lookup / bookmark lookup explosion | Non-covering index for a hot path | Revisit include columns or query projection |
| Plan changes wildly per parameter | Parameter sensitivity | Use Query Store / OPPO / workload-specific evidence before adding hints |
| Query looks cheap but latency is high | Blocking, I/O, or pool contention | Inspect waits, locks, and connection pressure |

## Vendor-Specific Notes

### PostgreSQL

- PostgreSQL 18 skip scan can make some composite indexes useful without a leading equality predicate, but it does not replace normal index design.
- Use `pg_stat_statements`, `pg_stat_io`, and `CREATE STATISTICS` when plan quality is inconsistent.

### MySQL

- OR predicates do not automatically require a UNION rewrite. MySQL can use index merge; verify with EXPLAIN.
- Invisible indexes are the safest way to test index retirement before dropping.

### SQL Server

- Use Query Store to compare plans before and after regressions.
- For optional predicates and parameter-sensitive workloads, check OPPO and related compatibility settings before hand-tuning with hints.

### SQLite

- The query planner is sensitive to ANALYZE data. Prefer `PRAGMA optimize;` over ad hoc tuning rituals.

## Common Mistakes

- Treating any sequential scan as a bug.
- Rewriting subqueries or CTEs before proving they are the bottleneck.
- Adding an index before checking estimation quality.
- Using tiny staging datasets to justify production changes.
- Looking only at estimated cost and ignoring elapsed time, loops, rows, and waits.

## Verification Checklist

- [ ] Plan captured in a representative environment
- [ ] Biggest operators identified by elapsed time or repeated loops
- [ ] Estimation issue separated from access-path issue
- [ ] Concurrency/wait evidence checked if latency exceeds operator time
- [ ] Proposed fix verified with the same capture method
- [ ] Result equivalence confirmed after query rewrites
