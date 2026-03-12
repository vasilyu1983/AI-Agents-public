```markdown
# SQL Index Creation Template

*Purpose: Standardize the process of adding, documenting, and validating indexes for query optimization. Ensures all index changes are operationally safe and performance-tested.*

---

## When to Use

Use this template when:
- Proposing a new index for slow queries or schema review
- Refactoring existing indexes
- Preparing for deployment/migration that impacts query performance

---

## Structure

This template has 4 sections:
1. **Index Design & Rationale** — why and how the index is needed
2. **DDL & Implementation** — ready-to-run SQL
3. **Validation & EXPLAIN Review** — before/after impact
4. **Rollback & Maintenance** — revert and monitor plan

---

# TEMPLATE STARTS HERE

## 1. Index Design & Rationale

- **Query or Access Pattern:**  
  [Paste representative SQL using the target columns]

- **Current Plan/Problem:**  
  [EXPLAIN shows table scan, slow join, etc.]

- **Reason for Index:**  
  [e.g., WHERE on user_id is slow, frequent lookup by email, etc.]

- **Index Type:**  
  [Single, composite, covering/INCLUDE, partial/filtered, functional/expr]

- **Columns to Index (in order):**  
  [List columns, e.g., (user_id, created_at)]

---

## 2. DDL & Implementation

**Create Index Statement:**  
```sql
-- Edit as needed for your RDBMS
CREATE INDEX idx_tablename_columns
  ON tablename(column1, column2)
  [INCLUDE (column3, ...)] -- Optional, Postgres/SQL Server
  [WHERE condition];       -- Optional, partial/filtered index
```

**Example:**  

```sql
CREATE INDEX idx_orders_customer_id_created_at
  ON orders(customer_id, created_at)
  INCLUDE (amount, status);
```

- **Expected Impact:**  
  [e.g., Should support queries filtering by customer_id and date, covering status/amount in result]

---

## 3. Validation & EXPLAIN Review

- **Before:**  
  - Query plan: [Paste pre-index plan]
  - Timing: [e.g., 1,300 ms]
  - Rows scanned: [e.g., 18,000]

- **After:**  
  - Query plan: [Paste post-index plan]
  - Timing: [e.g., 12 ms]
  - Rows scanned: [e.g., 18]

- **Other queries potentially affected:**  
  [Review for index bloat, overlaps, negative impact]

---

## 4. Rollback & Maintenance

- **Rollback Command:**  

  ```sql
  DROP INDEX idx_tablename_columns;
  ```

- **Post-Deployment Monitoring:**  
  - Check index usage with pg_stat_user_indexes, INFORMATION_SCHEMA, or RDBMS-specific tools.
  - Monitor DML (insert/update/delete) latency for regression.
  - Schedule routine index maintenance (REINDEX, ANALYZE, OPTIMIZE TABLE).

---

# COMPLETE EXAMPLE

## 1. Index Design & Rationale

- **Query or Access Pattern:**  
  SELECT * FROM orders WHERE customer_id = 77 AND created_at >= '2024-01-01';

- **Current Plan/Problem:**  
  Table scan in EXPLAIN, query takes 800 ms

- **Reason for Index:**  
  Accelerate customer order lookups for analytics dashboard

- **Index Type:**  
  Composite

- **Columns to Index (in order):**  
  (customer_id, created_at)

---

## 2. DDL & Implementation

**Create Index Statement:**  

```sql
CREATE INDEX idx_orders_customer_id_created_at
  ON orders(customer_id, created_at);
```

- **Expected Impact:**  
  Filter + range scan, supports rapid dashboard queries

---

## 3. Validation & EXPLAIN Review

- **Before:**  
  Plan: Seq Scan on orders  
  Timing: 800 ms  
  Rows scanned: 12,000

- **After:**  
  Plan: Index Scan on orders  
  Timing: 15 ms  
  Rows scanned: 24

---

## 4. Rollback & Maintenance

- **Rollback Command:**  
  DROP INDEX idx_orders_customer_id_created_at;

- **Post-Deployment Monitoring:**  
  - Check pg_stat_user_indexes for hits
  - Monitor dashboard for improved response
  - Revisit in quarterly index review

---

## Quality Checklist

Before finalizing:

- [ ] Index reviewed with query and plan
- [ ] No overlapping/redundant indexes created
- [ ] EXPLAIN plans saved in ticket/docs
- [ ] Rollback and monitoring steps documented

```
