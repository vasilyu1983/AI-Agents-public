# EXPLAIN Analysis Patterns

Purpose: read query plans as evidence, not folklore. Use this guide when a user has a slow query, a suspected bad index, or a regression after schema/data changes.

## Table of Contents

- [Start With the Right Capture](#start-with-the-right-capture)
- [Read Plans in This Order](#read-plans-in-this-order)
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
