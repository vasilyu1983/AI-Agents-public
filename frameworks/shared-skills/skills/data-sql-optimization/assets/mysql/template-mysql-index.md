```markdown
# MySQL Index Creation Template

*Purpose: Safely design, document, implement, and validate new indexes in MySQL for reliable query acceleration.*

---

## When to Use

Use this template when:
- Adding a new index for a slow or high-traffic MySQL query
- Reviewing indexes during schema optimization or code review
- Planning index changes for migrations

---

## Structure

This template includes:
1. **Index Rationale & Design**
2. **DDL (Create Index)**
3. **Validation (EXPLAIN, Usage, Monitoring)**
4. **Rollback & Maintenance**

---

# TEMPLATE STARTS HERE

## 1. Index Rationale & Design

- **Query/Use-case:**  
  [Paste the SQL or describe the query pattern that needs optimization]

- **Observed Issue:**  
  [e.g., EXPLAIN shows type: ALL, no index, slow response]

- **Proposed Index:**  
  [Single-column, composite, covering, etc.]

- **Index Columns & Order:**  
  [e.g., (customer_id, status, created_at DESC)]

- **Additional Notes:**  
  [e.g., Consider index size, expected selectivity, possible overlaps]

---

## 2. DDL (Create Index)

**MySQL Example:**  
```sql
CREATE INDEX idx_tablename_columns
  ON tablename(column1, column2 [DESC], ...);
```

*Edit for your specific table and columns.*

---

## 3. Validation (EXPLAIN, Usage, Monitoring)

- **Before:**  
  - Query plan: [Paste EXPLAIN before index]
  - type: [e.g., ALL, range, ref, etc.]
  - key: [NULL or existing index]
  - Timing/Rows: [e.g., 700 ms, 8,000 rows scanned]

- **After:**  
  - Query plan: [Paste EXPLAIN after index]
  - type: [e.g., ref, range, index, etc.]
  - key: [Index used]
  - Timing/Rows: [e.g., 8 ms, 5 rows scanned]
  - Confirmed index usage: [Yes/No]

- **Other queries potentially affected:**  
  [List or mark N/A]

- **Index usage monitoring:**  
  - Use `SHOW INDEX FROM tablename;`
  - Monitor slow query log for regressions
  - Check with `SHOW STATUS LIKE 'Handler_read%';` as needed

---

## 4. Rollback & Maintenance

- **Rollback Command:**  

  ```sql
  DROP INDEX idx_tablename_columns ON tablename;
  ```

- **Post-Deployment Monitoring:**  
  - Monitor query latency for key paths
  - Review DML (insert/update/delete) performance
  - Include index in periodic schema/index audits

---

# COMPLETE EXAMPLE

## 1. Index Rationale & Design

- **Query/Use-case:**  
  SELECT * FROM orders WHERE customer_id = 211 AND status = 'paid' ORDER BY created_at DESC LIMIT 10;
- **Observed Issue:**  
  Full table scan (type: ALL), slow, no index used
- **Proposed Index:**  
  Composite
- **Index Columns & Order:**  
  (customer_id, status, created_at DESC)

---

## 2. DDL (Create Index)

```sql
CREATE INDEX idx_orders_customer_status_created
  ON orders(customer_id, status, created_at DESC);
```

---

## 3. Validation (EXPLAIN, Usage, Monitoring)

- **Before:**  
  type: ALL  
  key: NULL  
  Timing: 630 ms, 9,000 rows scanned

- **After:**  
  type: ref  
  key: idx_orders_customer_status_created  
  Timing: 6 ms, 10 rows scanned  
  Confirmed index usage: Yes

- **Index usage monitoring:**  
  SHOW INDEX FROM orders;

---

## 4. Rollback & Maintenance

- **Rollback Command:**  
  DROP INDEX idx_orders_customer_status_created ON orders;

- **Post-Deployment Monitoring:**  
  - Monitor dashboard, slow query log
  - Check for any impact on writes
  - Review in next schema/index audit

---

## Quality Checklist

Before finalizing:

- [ ] Index DDL reviewed and peer approved
- [ ] EXPLAIN plans and query timings saved before/after
- [ ] Rollback command ready
- [ ] Monitoring steps documented

```
