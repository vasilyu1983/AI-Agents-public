```markdown
# PostgreSQL Index Creation Template

*Purpose: Standardize the process for proposing, creating, validating, and rolling back indexes in PostgreSQL for query and schema optimization.*

---

## When to Use

Use this template when:
- Adding a new index in PostgreSQL to support slow queries, joins, or reporting
- Auditing or refactoring existing indexes
- Preparing for schema migrations that impact query performance

---

## Structure

This template includes:
1. **Index Proposal & Rationale**
2. **DDL (Create Index)**
3. **Validation (EXPLAIN, Usage, Monitoring)**
4. **Rollback & Maintenance**

---

# TEMPLATE STARTS HERE

## 1. Index Proposal & Rationale

- **Target Query:**  
  [Paste or describe the SQL statement(s) that will use this index]

- **Observed Problem:**  
  [e.g., Seq Scan in EXPLAIN, slow WHERE or JOIN, missing index]

- **Proposed Index:**  
  [e.g., Single-column, composite, partial, or functional]

- **Index Columns & Order:**  
  [e.g., (customer_id, created_at DESC)]

- **Is this a covering index?**  
  [Yes/No. If yes, list INCLUDE columns.]

- **Partial/Filtered Condition:**  
  [e.g., WHERE status = 'active'] (leave blank if not applicable)

---

## 2. DDL (Create Index)

**PostgreSQL Example:**  
```sql
CREATE INDEX CONCURRENTLY idx_table_columns
  ON tablename(column1 [DESC], column2 [ASC])
  [INCLUDE (col3, col4)]              -- optional
  [WHERE condition];                  -- optional
```

*Fill out or adjust options as needed.*

---

## 3. Validation (EXPLAIN, Usage, Monitoring)

- **Before:**  
  - Query plan: [Paste EXPLAIN (ANALYZE) before index]
  - Timing: [e.g., 350 ms, 8000 rows scanned]

- **After:**  
  - Query plan: [Paste EXPLAIN (ANALYZE) after index]
  - Timing: [e.g., 14 ms, 12 rows scanned]
  - Confirmed index usage: [Yes/No, e.g., "Index Scan on idx_table_columns"]

- **Other queries possibly affected:**  
  [List or N/A]

- **Stats refresh:**  
  - Run `ANALYZE tablename;` after creation

- **Index usage monitoring:**  
  - Use `pg_stat_user_indexes` to verify hits
  - Add to quarterly/annual index review

---

## 4. Rollback & Maintenance

- **Rollback Command:**  

  ```sql
  DROP INDEX CONCURRENTLY IF EXISTS idx_table_columns;
  ```

- **Post-Deployment Actions:**  
  - Monitor query performance and index usage for 1–2 weeks
  - Schedule periodic REINDEX/maintenance as appropriate
  - Document all changes and update schema diagrams/docs

---

# COMPLETE EXAMPLE

## 1. Index Proposal & Rationale

- **Target Query:**  
  SELECT * FROM orders WHERE customer_id = 88 AND created_at >= '2024-01-01';

- **Observed Problem:**  
  Seq Scan, slow dashboard load

- **Proposed Index:**  
  Composite

- **Index Columns & Order:**  
  (customer_id, created_at DESC)

- **Is this a covering index?**  
  No

- **Partial/Filtered Condition:**  
  (blank)

---

## 2. DDL (Create Index)

```sql
CREATE INDEX CONCURRENTLY idx_orders_customer_id_created_at
  ON orders(customer_id, created_at DESC);
```

---

## 3. Validation (EXPLAIN, Usage, Monitoring)

- **Before:**  
  Plan: Seq Scan  
  Timing: 550 ms

- **After:**  
  Plan: Index Scan on idx_orders_customer_id_created_at  
  Timing: 10 ms  
  Confirmed index usage: Yes

- **Stats refresh:**  
  ANALYZE orders;

- **Index usage monitoring:**  
  Check `pg_stat_user_indexes` after 1 week

---

## 4. Rollback & Maintenance

- **Rollback Command:**  
  DROP INDEX CONCURRENTLY IF EXISTS idx_orders_customer_id_created_at;

- **Post-Deployment Actions:**  
  - Monitor for negative performance or index bloat
  - Include index in periodic review

---

## Quality Checklist

Before finalizing:

- [ ] Index DDL peer reviewed
- [ ] EXPLAIN plans captured before and after
- [ ] Rollback command documented
- [ ] Monitoring steps in place

```
