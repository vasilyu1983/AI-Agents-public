```markdown
# MySQL EXPLAIN Analysis Template

*Purpose: Systematically document, review, and optimize MySQL query execution plans for performance tuning.*

---

## When to Use

Use this template when:
- Investigating slow MySQL queries
- Reviewing SQL before/after index or schema changes
- Performing regular database performance audits

---

## Structure

This template includes:
1. **Query & Context**
2. **EXPLAIN Output**
3. **Plan Review Checklist**
4. **Optimization & Verification**

---

# TEMPLATE STARTS HERE

## 1. Query & Context

- **SQL Query:**  
  [Paste the query being analyzed]

- **Schema/DB/Version:**  
  [e.g., mydb, MySQL 8.0.33, prod/staging]

- **Tables Involved:**  
  [List relevant tables]

- **Expected Result Size:**  
  [e.g., 1 row, top 100, full table, etc.]

---

## 2. EXPLAIN Output

- **Command Used:**  
  ```sql
  EXPLAIN [FORMAT=JSON] [SQL...]
  ```

- **Plan Output:**  
  [Paste EXPLAIN table or JSON output]

---

## 3. Plan Review Checklist

- [ ] Are there any rows with `type: ALL`? (full table scan)
- [ ] Are appropriate indexes being used? (look at `key` column)
- [ ] Are all JOIN columns indexed?
- [ ] Any filesort/temp table in `Extra`? (slows ORDER BY, GROUP BY)
- [ ] Does `rows` estimate seem reasonable? (compare to table size)
- [ ] Any range/index_merge/index_subquery that can be improved?
- [ ] Is `Using where` present? (good—filtering at index)
- [ ] Are queries limited (`LIMIT`, appropriate WHERE)?
- [ ] Any sign of missing/outdated stats?

---

## 4. Optimization & Verification

- **Proposed Index or Query Rewrite:**  
  [Add new index, rewrite WHERE/JOIN, change join order, etc.]

- **Plan After Change:**  
  [Paste updated EXPLAIN, note differences]

- **Performance Before/After:**  
  - Before: [e.g., 900 ms, 8000 rows]
  - After:  [e.g., 13 ms, 50 rows]

- **Rollback Plan:**  
  [DROP INDEX, revert query, etc.]

---

# COMPLETE EXAMPLE

## 1. Query & Context

- **SQL Query:**  
  SELECT * FROM orders WHERE customer_id = 102 AND status = 'paid' ORDER BY created_at DESC LIMIT 5;
- **Schema/DB/Version:**  
  ordersdb, MySQL 8.0.33, production
- **Tables Involved:**  
  orders
- **Expected Result Size:**  
  5 rows

---

## 2. EXPLAIN Output

- **Command Used:**  
  EXPLAIN SELECT * FROM orders WHERE customer_id = 102 AND status = 'paid' ORDER BY created_at DESC LIMIT 5;
- **Plan Output:**  

  | id | select_type | table  | type | key  | key_len | ref   | rows | Extra                        |
  |----|-------------|--------|------|------|---------|-------|------|------------------------------|
  | 1  | SIMPLE      | orders | ALL  | NULL | NULL    | NULL  | 8000 | Using where; Using filesort  |

---

## 3. Plan Review Checklist

- [x] type: ALL (full table scan)
- [ ] No index used (key: NULL)
- [x] Using where present
- [x] Using filesort present
- [ ] Join not relevant (single table)
- [x] Query limited with LIMIT
- [ ] Stats up to date

---

## 4. Optimization & Verification

- **Proposed Index or Query Rewrite:**  
  CREATE INDEX idx_orders_customer_status_created ON orders(customer_id, status, created_at DESC);

- **Plan After Change:**  
  type: ref  
  key: idx_orders_customer_status_created  
  Extra: Using where

- **Performance Before/After:**  
  - Before: 880 ms, 8000 rows
  - After: 7 ms, 5 rows

- **Rollback Plan:**  
  DROP INDEX idx_orders_customer_status_created ON orders;

---

## Quality Checklist

Before finalizing:

- [ ] EXPLAIN plans captured and reviewed before/after
- [ ] Index/query changes tested with production-like data
- [ ] Rollback steps documented

```
