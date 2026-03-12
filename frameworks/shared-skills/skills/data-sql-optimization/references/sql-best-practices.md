```markdown
# SQL Best Practices

*Purpose: Actionable patterns, checklists, and templates for optimizing SQL queries, index design, and database performance across major RDBMS.*

---

## Core Patterns

### Pattern 1: Query Review & Tuning

**Use when:** Reviewing any query for performance before deployment or when troubleshooting slowness.

**Structure:**
```

1. Check SELECT clause: avoid SELECT *; fetch only necessary columns.
2. Confirm WHERE clause restricts result set appropriately.
3. Review JOINs: ensure proper ON conditions and that join columns are indexed.
4. Use LIMIT/OFFSET for paginated or large-result queries.
5. Check for functions or expressions on indexed columns in WHERE.
6. Ensure GROUP BY, ORDER BY, and aggregates use indexed columns when possible.

```

**Checklist:**
- [ ] No SELECT *
- [ ] WHERE clause uses sargable (index-usable) predicates
- [ ] Joins on indexed columns
- [ ] LIMIT/OFFSET or pagination for user-facing queries
- [ ] No unnecessary subqueries/CTEs if simple join suffices

---

## Core SQL Fundamentals (Learning SQL)

- **Projection & Filtering:** Explicit column lists; `WHERE` before aggregation; `HAVING` only for aggregates.
- **Join Matrix:** Prefer explicit `JOIN ... ON`; ensure join keys are indexed and check join cardinality.
- **Set Operations:** Default to `UNION ALL` unless dedup is required; align column types and order.
- **NULL & Logic:** Use `IS NULL`/`COALESCE`; remember three-valued logic; avoid nullable booleans where possible.
- **Defaults & Constraints:** Set sensible defaults, `NOT NULL` by default, and use check constraints for data quality.

### Window Functions Quick Reference

```sql
SELECT order_id,
       ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY created_at DESC) AS rn,
       SUM(amount) OVER (PARTITION BY customer_id) AS customer_total
FROM orders;
```

- Use window functions for rankings/rollups without extra joins.
- Combine PARTITION (group) + ORDER (sequence); add FILTER where supported for conditional aggregates.

### GROUP BY & HAVING

- Group only on required dimensions; pre-filter before grouping.
- Use HAVING strictly for aggregate filters; keep non-aggregate predicates in WHERE.

---

### Pattern 2: Explain Plan Analysis

**Use when:** Diagnosing slow queries or validating query/index changes.

**Structure:**
```

1. Run EXPLAIN (ANALYZE, BUFFERS) on the query (Postgres) or EXPLAIN FORMAT=JSON (MySQL).
2. Identify full table/seq scans, hash joins, or filesort operations.
3. Check estimated vs. actual rows (Postgres) for misestimation.
4. Confirm index usage matches expectations for filter/join columns.
5. Look for high-cost steps or frequent node re-checks.

```

**Checklist:**
- [ ] Index Scan/Seek for main table filters
- [ ] No Seq Scan (unless table is tiny)
- [ ] JOINs use hash/merge only if faster than nested loop
- [ ] No filesort/temp tables for large result sets
- [ ] Estimated/actual row counts match within 10x

---

### Pattern 3: Index Design

**Use when:** Supporting frequent filters, sorts, or joins.

**Structure:**
```

1. Identify query filter/join columns.
2. Create single or multi-column indexes that match query filter patterns.
3. Use INCLUDE/covering index for columns returned but not filtered.
4. Drop unused or redundant indexes (analyze with pg_stat_user_indexes or INFORMATION_SCHEMA.STATISTICS).
5. Regularly run index maintenance (REINDEX, OPTIMIZE TABLE, etc.).

```

**Checklist:**
- [ ] Index present for every major WHERE/JOIN key
- [ ] No duplicate/redundant indexes
- [ ] Covering index if possible for high-traffic queries
- [ ] Regular index usage stats reviewed

---

### Pattern 4: Anti-Pattern Remediation

| Anti-Pattern                                 | Detection                | Operational Fix                   |
|----------------------------------------------|--------------------------|-----------------------------------|
| SELECT * everywhere                         | Scan query text          | Enumerate columns needed          |
| WHERE on computed value (e.g., YEAR(date))  | EXPLAIN shows seq scan   | Index on computed value or add col|
| OR conditions on non-indexed columns         | Slow queries, table scan | Composite index, rewrite as UNION |
| No WHERE on large tables (accidental full)   | Table scan in EXPLAIN    | Always filter queries             |
| Multiple N+1 queries                        | Excessive queries/logs   | Use JOINs/CTEs                   |

---

## Decision Matrices

| Symptom                 | Likely Root Cause        | Action                                  |
|-------------------------|-------------------------|-----------------------------------------|
| Seq/Table scan          | No/misplaced index      | Add correct index for filter/join cols  |
| Slow JOIN               | Unindexed join columns  | Index both sides, consider join order   |
| Slow sort/aggregate     | No index on sort/group  | Add index, rewrite query if possible    |
| Query fine in test, slow prod | Data size difference  | Check stats, analyze, reindex           |

---

## Quick Reference

### Query Optimization Checklist

- [ ] WHERE clause is selective and sargable
- [ ] Joins use indexed columns
- [ ] No functions on filter columns (unless indexed functional/expr index)
- [ ] Results limited to user need (pagination)
- [ ] Aggregates use indexes or pre-aggregated data where possible
- [ ] Query plan reviewed before deploy

### Index Review

- [ ] No unused indexes (check index scan stats)
- [ ] No redundant/overlapping indexes
- [ ] Write queries balanced with index count (avoid over-indexing)
- [ ] Maintenance (REINDEX, ANALYZE, VACUUM) scheduled

---

## Common Mistakes

[FAIL] **Adding too many indexes:**  
Increases write cost, can slow down DML.  
[OK] **Instead:** Index only high-value queries; monitor index usage.

[FAIL] **Assuming default indexes are enough:**  
Primary key often not queried directly.  
[OK] **Instead:** Profile and add indexes for real-world access patterns.

[FAIL] **Forgetting to ANALYZE/VACUUM (Postgres):**  
Outdated stats cause bad plans.  
[OK] **Instead:** Automate ANALYZE after large data changes.

---

## Edge Cases & Fallbacks

- If performance tanks after schema change: Roll back, drop added index, review plan.
- If EXPLAIN shows table scan for a filtered query: Add or fix index, or rewrite predicate.

---

*Use this guide for hands-on SQL review and optimization. All steps are operational and copy-paste ready.*
```
