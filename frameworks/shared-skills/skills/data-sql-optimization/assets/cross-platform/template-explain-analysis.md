```markdown
# SQL EXPLAIN Analysis Template

*Purpose: Use this template to document, analyze, and act on SQL execution plans during query tuning or review.*

---

## When to Use

Use this template when:
- Reviewing slow or critical queries
- Making schema/index changes
- Preparing for production migrations
- Performing periodic performance audits

---

## Structure

This template has 3 sections:
1. **Plan Collection** — capture how/where EXPLAIN was run
2. **Plan Review Checklist** — quick operational checks
3. **Action Items & Verification** — optimizations, retesting, rollback

---

# TEMPLATE STARTS HERE

## 1. Plan Collection

- **Database:** [e.g., PostgreSQL 15, MySQL 8.0]
- **Command Used:** [e.g., EXPLAIN (ANALYZE, BUFFERS) SELECT ...]
- **Schema Version/Date:** [Timestamp or migration hash]
- **Relevant Query:** [Paste the SQL being analyzed]
- **EXPLAIN Output:**  
  [Paste plan text or attach screenshot/JSON if large]

---

## 2. Plan Review Checklist

- [ ] Are there any Seq/Table Scans?  
  - [ ] If yes, are they justified (small table, no filter)?
- [ ] Are join columns indexed on both tables?
- [ ] Does WHERE use sargable predicates (no function/wrapper on indexed col)?
- [ ] Are filesort/temp or sort nodes present?
- [ ] Are estimated and actual row counts close (within 10x)?
- [ ] Is there a major difference in cost between steps?
- [ ] Does the plan show index scans/seeks for main filter/join columns?
- [ ] Any indication of missing/outdated stats?

---

## 3. Action Items & Verification

- **Proposed Index or Query Rewrite:**  
  [e.g., add composite index, rewrite predicate, adjust join order]

- **Plan After Change:**  
  [Paste updated plan or describe expected result]

- **Performance Before/After:**  
  - Before: [e.g., 2,500 ms, 100k rows scanned]
  - After:  [e.g., 42 ms, 800 rows scanned]

- **Rollback Plan:**  
  [How to revert index or query if results degrade]

---

# COMPLETE EXAMPLE

## 1. Plan Collection

- **Database:** PostgreSQL 15
- **Command Used:** EXPLAIN (ANALYZE, BUFFERS) SELECT * FROM orders WHERE customer_id = 123;
- **Schema Version/Date:** 2024-05-01 (prod schema v19)
- **Relevant Query:**  
  SELECT * FROM orders WHERE customer_id = 123;
- **EXPLAIN Output:**  
  Seq Scan on orders  (cost=0.00..1220.00 rows=2 width=...)  
    Filter: (customer_id = 123)  
    Rows Removed by Filter: 12500

---

## 2. Plan Review Checklist

- [x] Seq Scan present (not justified, large table)
- [ ] Index on customer_id missing
- [x] WHERE is sargable
- [ ] No sort, temp, or filesort
- [x] Estimated/actual rows match (plan estimates 2, actual 1)
- [ ] Stats may be slightly outdated

---

## 3. Action Items & Verification

- **Proposed Index or Query Rewrite:**  
  CREATE INDEX idx_orders_customer_id ON orders(customer_id);

- **Plan After Change:**  
  Index Scan on orders (cost much lower, no filter step)

- **Performance Before/After:**  
  - Before: 1,250 ms, 12,500 rows scanned
  - After: 4 ms, 1 row scanned

- **Rollback Plan:**  
  DROP INDEX idx_orders_customer_id;

---

## Quality Checklist

Before finalizing:
- [ ] Plan reviewed and pasted in ticket/docs
- [ ] Index or query change tested in staging/prod-like data
- [ ] Rollback plan documented and ready
```
