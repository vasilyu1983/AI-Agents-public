```markdown
# SQL Query Tuning Template

*Purpose: Use this template for systematic, repeatable review and optimization of SQL queries before deployment or when troubleshooting slowness.*

---

## When to Use

Use this template when:
- Reviewing new or changed SQL queries
- Investigating slow report, dashboard, or transactional queries
- Preparing for migration or major database changes

---

## Structure

This template has 4 sections:
1. **Query & Table Details** — context, schema, purpose
2. **Performance Review Checklist** — operational checks
3. **EXPLAIN Analysis** — plan output & findings
4. **Optimization & Verification** — fixes and validation

---

# TEMPLATE STARTS HERE

## 1. Query & Table Details

- **Query Purpose:**  
  [Describe what business logic, report, or endpoint uses this query]

- **Primary Table(s):**  
  [e.g., orders, users, events]

- **Expected Result Set Size:**  
  [Row count or "single row", "top 100", etc.]

- **Is this user-facing or internal?**  
  [Yes/No]

---

## 2. Performance Review Checklist

- [ ] Only needed columns in SELECT (no `SELECT *`)
- [ ] WHERE clause is selective and matches index
- [ ] Joins are on indexed columns
- [ ] No functions/wrappers on indexed columns in WHERE/JOIN
- [ ] Results are paginated (`LIMIT` or similar)
- [ ] No unnecessary subqueries or CTEs

---

## 3. EXPLAIN Analysis

- **Plan Used:**  
  [Paste or summarize EXPLAIN (ANALYZE) output]

- **Table/Seq Scan present?**  
  [Yes/No. If yes, on which table(s)?]

- **Join Type(s) and Order:**  
  [e.g., Nested Loop, Hash Join]

- **Rows Examined vs. Returned:**  
  [Summarize, e.g. "100k scanned, 150 returned"]

- **Sorting/Aggregation Method:**  
  [Filesort, index, in-memory, etc.]

---

## 4. Optimization & Verification

- **Proposed Rewrite or Index Change:**  
  [e.g., add composite index, rewrite predicate]

- **Updated EXPLAIN Plan:**  
  [Paste new plan summary]

- **Performance Test Results:**  
  [Before: X ms/rows. After: Y ms/rows.]

- **Rollback Plan:**  
  [How to revert if performance regresses]

---

# COMPLETE EXAMPLE

## 1. Query & Table Details

- **Query Purpose:**  
  Used in dashboard to display top 10 customers by revenue last year

- **Primary Table(s):**  
  orders, customers

- **Expected Result Set Size:**  
  10 rows

- **Is this user-facing or internal?**  
  User-facing

---

## 2. Performance Review Checklist

- [x] Only needed columns selected
- [x] WHERE filters by year and customer_id
- [x] JOIN on indexed customer_id
- [x] No functions on WHERE columns
- [x] Results limited (LIMIT 10)
- [x] No unneeded subqueries

---

## 3. EXPLAIN Analysis

- **Plan Used:**  
  Index Scan on orders, Nested Loop join to customers

- **Table/Seq Scan present?**  
  No

- **Join Type(s) and Order:**  
  Nested Loop: orders -> customers

- **Rows Examined vs. Returned:**  
  1,200 scanned, 10 returned

- **Sorting/Aggregation Method:**  
  In-memory sort (on revenue desc)

---

## 4. Optimization & Verification

- **Proposed Rewrite or Index Change:**  
  Add composite index: `(customer_id, order_date) INCLUDE (amount)`

- **Updated EXPLAIN Plan:**  
  Index Scan + Sort (smaller temp file)

- **Performance Test Results:**  
  Before: 120 ms. After: 8 ms.

- **Rollback Plan:**  
  Drop index if query slows or write overhead spikes.

---

## Quality Checklist

Before finalizing:
- [ ] Query and plan reviewed with realistic data
- [ ] All changes tested in staging/prod-like environment
- [ ] Rollback steps documented
```
