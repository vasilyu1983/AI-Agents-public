```markdown
# PostgreSQL EXPLAIN/ANALYZE Template

*Purpose: Standardize the operational process for capturing, analyzing, and optimizing PostgreSQL query plans using EXPLAIN (ANALYZE, BUFFERS).*

---

## When to Use

Use this template for:
- Diagnosing slow queries in PostgreSQL
- Reviewing query plans before/after schema/index changes
- Routine performance tuning or periodic health checks

---

## Structure

This template includes:
1. **Query & Context**
2. **EXPLAIN Output**
3. **Plan Analysis Checklist**
4. **Action Items & Validation**

---

# TEMPLATE STARTS HERE

## 1. Query & Context

- **Query:**  
  [Paste SQL statement being reviewed]

- **Database/Schema:**  
  [Name, version, environment]

- **Table(s) Involved:**  
  [e.g., orders, users, etc.]

- **Expected Result Size:**  
  [Rows, typical use-case]

---

## 2. EXPLAIN Output

- **Command Used:**  
  ```sql
  EXPLAIN (ANALYZE, BUFFERS, VERBOSE) [SQL...]
  ```

- **Plan Output:**  
  [Paste raw plan or use gist/plan visualizer link]

---

## 3. Plan Analysis Checklist

- [ ] Is there a `Seq Scan` on a large table?  
  - [ ] If yes, should an index be used?
- [ ] Is `Index Scan` or `Index Only Scan` used for key filters?
- [ ] Any join type concerns? (`Nested Loop`, `Hash Join`, `Merge Join`)
- [ ] Are actual rows close to estimated? (`rows=` numbers)
- [ ] Any `Sort` or `HashAggregate` on large sets?
- [ ] Is any node showing high I/O (`Buffers: shared hit/read/dirtied/written`)?
- [ ] Is `Filter:` used where it could be index-based?
- [ ] Is the most selective filter applied earliest?
- [ ] Any sign of missing/up-to-date statistics?

---

## 4. Action Items & Validation

- **Optimization Steps Proposed:**  
  [e.g., add index, rewrite WHERE, change join order, ANALYZE]

- **Plan After Optimization:**  
  [Paste updated plan, highlight changes]

- **Performance Before/After:**  
  - Before: [timing, rows, I/O]
  - After:  [timing, rows, I/O]

- **Rollback Plan:**  
  [DROP INDEX, revert query, etc.]

---

# COMPLETE EXAMPLE

## 1. Query & Context

- **Query:**  
  SELECT * FROM orders WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 10;
- **Database/Schema:**  
  prod, PostgreSQL 15
- **Table(s) Involved:**  
  orders
- **Expected Result Size:**  
  10 rows

---

## 2. EXPLAIN Output

- **Command Used:**  
  EXPLAIN (ANALYZE, BUFFERS, VERBOSE) SELECT * FROM orders WHERE customer_id = 42 ORDER BY created_at DESC LIMIT 10;
- **Plan Output:**  
  Seq Scan on orders ... Filter: (customer_id = 42) ... 14,200 rows removed by filter

---

## 3. Plan Analysis Checklist

- [x] Seq Scan present on large table
- [ ] Index on (customer_id, created_at) missing
- [ ] Index Only Scan not possible
- [ ] No problematic joins
- [x] Actual rows (10) << estimated (15,000)
- [ ] Sort operation not optimized
- [ ] Statistics up to date

---

## 4. Action Items & Validation

- **Optimization Steps Proposed:**  
  CREATE INDEX idx_orders_customer_id_created_at ON orders(customer_id, created_at DESC);

- **Plan After Optimization:**  
  Index Scan on orders using idx_orders_customer_id_created_at

- **Performance Before/After:**  
  - Before: 920 ms, 14,210 rows scanned
  - After: 8 ms, 10 rows scanned

- **Rollback Plan:**  
  DROP INDEX idx_orders_customer_id_created_at;

---

## Quality Checklist

Before finalizing:

- [ ] EXPLAIN plan pasted in docs/ticket
- [ ] Index or rewrite tested in staging
- [ ] Rollback steps documented

```
