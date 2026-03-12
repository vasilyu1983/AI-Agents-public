```markdown
# Query Tuning Patterns

*Purpose: Copy-paste ready query rewrite strategies, anti-pattern remediation, and operational step-by-step patterns for fast and reliable SQL queries.*

---

## Core Patterns

### Pattern 1: Use Covering Indexes for Frequent Queries

**Use when:** You have a hot query filtering on column(s) and always retrieving the same set of columns.

**Example:**
```sql
-- Before: Index only on user_id
SELECT user_id, created_at FROM orders WHERE user_id = 123;

-- Better: Covering index for filter and select
CREATE INDEX idx_orders_user_id_created_at ON orders(user_id) INCLUDE (created_at);
```

**Checklist:**

- [ ] Index includes all columns in SELECT and WHERE
- [ ] EXPLAIN shows Index Scan/Seek, not Seq/Table Scan

---

### Pattern 2: Sargable WHERE Clauses

**Use when:** Queries are slow and EXPLAIN shows sequential scan or full table scan.

**Examples:**

- Avoid:

  ```sql
  WHERE LOWER(email) = 'alice@example.com'
  WHERE YEAR(order_date) = 2024
  ```

- Do:

  ```sql
  WHERE email = LOWER('alice@example.com')
  -- Or add expression/functional index if supported
  CREATE INDEX idx_orders_order_date_year ON orders (EXTRACT(YEAR FROM order_date));
  ```

**Checklist:**

- [ ] No functions/wrappers on indexed columns in WHERE
- [ ] Query uses column = value, not computation = value

---

### Pattern 3: Rewriting N+1 to JOINs or CTEs

**Anti-pattern:** Application issues one parent query, then multiple queries per child record.

**Remediation:**

```sql
-- Before (N+1):
SELECT id FROM customers;
-- For each id: SELECT * FROM orders WHERE customer_id = ?

-- After (JOIN):
SELECT c.id, o.* FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id;
```

**Checklist:**

- [ ] Use JOIN/CTE for 1-to-many or related queries
- [ ] No repeated queries for related data

---

### Pattern 4: Limiting Results and Pagination

**Use when:** Large tables, user-facing queries.

**Examples:**

```sql
-- Basic pagination (offset/limit)
SELECT * FROM events ORDER BY created_at DESC LIMIT 50 OFFSET 100;

-- Seek method (faster for deep pages)
SELECT * FROM events
WHERE (created_at, id) < ('2024-04-30 12:00:00', 12345)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

**Checklist:**

- [ ] LIMIT always present on large tables
- [ ] Use seek/“keyset” pagination for deep paging

---

### Pattern 5: Optimizing JOIN Order

**Guideline:** Place most selective/filtering table first in JOIN order, and ensure join keys are indexed.

**Example:**

```sql
-- Filtering first
SELECT * FROM users u
JOIN logins l ON l.user_id = u.id
WHERE u.status = 'active' AND l.created_at > now() - INTERVAL '7 days';
```

**Checklist:**

- [ ] WHERE clause applies before join, not after
- [ ] Join keys are indexed on both tables

---

## Decision Trees

**If query is slow:**

- Is there a table/seq scan? -> Add/fix index, check sargability
- Is there an unindexed JOIN? -> Index join keys
- Is there a filesort/temp file? -> Index for sort/group columns
- Is LIMIT missing? -> Add or paginate

---

## Common Mistakes

[FAIL] **Multiple overlapping indexes for similar queries:**  
Creates write overhead, rarely used.  
[OK] **Instead:** Regularly review usage with statistics views.

[FAIL] **Relying on ORM-generated queries blindly:**  
Often inefficient for complex access.  
[OK] **Instead:** Profile and hand-optimize as needed; use EXPLAIN.

[FAIL] **Ignoring cardinality or data distribution:**  
Bad plans due to poor stats.  
[OK] **Instead:** ANALYZE/VACUUM (Postgres), UPDATE STATISTICS (SQL Server/MySQL).

---

## Quick Reference Table

| Query Symptom    | Pattern or Fix               |
|------------------|-----------------------------|
| Table Scan       | Add/fix index, sargable WHERE|
| Slow Pagination  | Use seek/keyset pagination   |
| N+1 Problem      | Rewrite as JOIN or CTE       |
| Sorting slow     | Index for ORDER BY columns   |
| Full scan JOIN   | Index join columns           |

---

## Quality Checklist

- [ ] Query plan reviewed in target environment
- [ ] All joins/filter columns indexed
- [ ] No full table scans unless intentional
- [ ] No N+1 or repeated queries per parent row
- [ ] Results paginated for user-facing queries
- [ ] Performance tested with realistic data volume

---

*All patterns above are operational, copy-paste ready, and designed for safe, auditable query optimization. Use as step-by-step checklists and templates for code review or live tuning.*

```
