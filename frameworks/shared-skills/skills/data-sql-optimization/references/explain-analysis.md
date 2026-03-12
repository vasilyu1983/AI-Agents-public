```markdown
# EXPLAIN Analysis Patterns

*Purpose: Step-by-step, copy-paste ready guides and checklists for using EXPLAIN (and EXPLAIN ANALYZE) to diagnose and remediate SQL query performance issues.*

---

## Core Patterns

### Pattern 1: Basic EXPLAIN Usage (PostgreSQL, MySQL, SQL Server)

**Use when:** Diagnosing why a query is slow, verifying index usage, or preparing for optimization.

**Examples:**
```sql
-- PostgreSQL
EXPLAIN (ANALYZE, BUFFERS) SELECT ...;

-- MySQL
EXPLAIN FORMAT=JSON SELECT ...;

-- SQL Server
SET SHOWPLAN_ALL ON; SELECT ...;
```

**Checklist:**

- [ ] Query runs in production-like environment
- [ ] EXPLAIN captures actual execution plan (not just estimated, if possible)
- [ ] Output saved or copied for review

---

### Pattern 2: Identifying Table/Seq Scans

**Indicators:**

- PostgreSQL: `Seq Scan on ...`
- MySQL: `type: ALL` in plan output
- SQL Server: `Table Scan` operator

**Operational Remediation:**

- Add index for columns used in WHERE/JOIN
- Rewrite predicates to be sargable (no functions/wrappers)
- Use LIMIT if possible for user queries

---

### Pattern 3: Detecting Unused Indexes

**Indicators:**

- Plan shows `Seq Scan` or `Table Scan` even when index exists
- No `Index Scan`, `Index Seek`, or `key` in plan output

**Operational Fixes:**

- Verify query WHERE/JOIN matches index structure
- Reorder index columns if composite
- Use functional index for computed predicates

---

### Pattern 4: Interpreting JOIN Performance

**Indicators:**

- PostgreSQL: `Hash Join`, `Nested Loop`, `Merge Join`
- MySQL: `type: ref` or `type: ALL` (bad for large tables)
- SQL Server: `Nested Loops`, `Merge Join`, `Hash Match`

**Checklist:**

- [ ] Join columns are indexed on both sides
- [ ] Smaller (filtered) table appears first in join order if possible
- [ ] Prefer Hash/Merge joins only when faster (large tables, analytics)

---

### Pattern 5: Detecting Sorting/Filesort

**Indicators:**

- MySQL: `Using filesort` in Extra column
- PostgreSQL: `Sort` node with high cost
- SQL Server: `Sort` operator in plan

**Operational Fixes:**

- Add index to support ORDER BY column(s)
- Minimize result set size (add WHERE, LIMIT)
- Consider pre-aggregating or storing data sorted if pattern is frequent

---

### Pattern 6: Estimated vs. Actual Rows

**Indicators:**

- PostgreSQL: EXPLAIN ANALYZE shows `rows=actual/estimated`
- Large mismatch = outdated stats or bad query structure

**Operational Fixes:**

- Run `ANALYZE` or `UPDATE STATISTICS` to refresh
- Simplify query or add better filter/index

---

## Decision Tree

**If query is slow:**

- Run EXPLAIN in target DB
- Table/Seq Scan present? -> Add/fix index
- Unindexed JOIN? -> Add index to join column(s)
- Filesort/sort node? -> Index for ORDER BY/GROUP BY
- Estimated/actual row mismatch? -> Refresh stats, check predicate
- Still slow? -> Rewrite as CTE or break into steps

---

## Common Mistakes

[FAIL] **Interpreting EXPLAIN output without understanding the DB's operators:**  
Use official docs for plan operator meanings.

[FAIL] **Assuming index always used if exists:**  
Check for functions or type mismatches in predicates.

[FAIL] **Ignoring estimated vs. actual row differences:**  
Update statistics/analyze and re-test.

---

## Quick Reference Table

| Symptom/Node        | What it Means                | What to Do                           |
|---------------------|-----------------------------|--------------------------------------|
| Seq/Table Scan      | No usable index              | Add/fix index, check WHERE           |
| Index Scan/Seek     | Good: index is used          | Confirm for correct filter/join col   |
| Hash Join           | May be ok for large joins    | Index join keys if high cardinality   |
| Sort/Filesort       | Slow sort in memory/disk     | Add index for sort/group cols         |
| Actual >> Estimate  | Outdated stats/bad plan      | Run ANALYZE, check predicate sargability|

---

## Quality Checklist

- [ ] EXPLAIN/ANALYZE output reviewed for every slow or major query
- [ ] Table scans always justified or avoided
- [ ] JOIN and WHERE columns match index structure
- [ ] Estimated and actual rows match within 10x
- [ ] Sorting/aggregation uses index when possible
- [ ] Plan output copied to ticket/docs for review

---

*Use this guide as an operational checklist for query tuning and code review. All patterns are actionable and align with best practices from major RDBMS.*

```
