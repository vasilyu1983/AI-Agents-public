```markdown
# SQL Anti-Patterns

*Purpose: Operational detection and remediation of common SQL anti-patterns, with step-by-step patterns and quick references for safe query and schema optimization.*

---

## Core Patterns

### Anti-Pattern 1: SELECT *

**Problem:** Fetching all columns increases network, memory, and disk usage, and prevents index-only scans.

**Detection:**  
- Query contains `SELECT *`  
- EXPLAIN plan does not show index-only scan

**Operational Fix:**
- Enumerate only the columns needed for the use-case
```sql
-- Instead of:
SELECT * FROM users WHERE id = 1;

-- Use:
SELECT id, name, email FROM users WHERE id = 1;
```

---

### Anti-Pattern 2: No Index on Foreign Keys/Join Columns

**Problem:** Slow joins or filters, table/seq scan in EXPLAIN.

**Detection:**  

- JOINs on columns without an index  
- Table scan on child/lookup table in query plan

**Operational Fix:**

```sql
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
```

---

### Anti-Pattern 3: Non-Sargable Predicates

**Problem:** Using functions or computations on indexed columns (e.g., `WHERE LOWER(name) = ...` or `WHERE YEAR(date) = 2023`).

**Detection:**  

- WHERE uses function or computation on indexed column  
- Plan shows table/seq scan

**Operational Fix:**

- Refactor to compare directly, or use a functional index if supported

```sql
-- Bad:
WHERE YEAR(order_date) = 2023
-- Good:
WHERE order_date >= '2023-01-01' AND order_date < '2024-01-01'
```

---

### Anti-Pattern 4: Over-Indexing

**Problem:** Every column or many redundant indexes; slows down writes and maintenance.

**Detection:**  

- Multiple indexes with same prefix columns  
- Insert/update performance degraded

**Operational Fix:**

- Review index usage statistics
- Drop unused or redundant indexes

---

### Anti-Pattern 5: N+1 Query Pattern

**Problem:** Issuing one query per parent record (inefficient).

**Detection:**  

- Application logs show repeated queries for child entities per parent row

**Operational Fix:**

- Rewrite using JOINs or CTEs to retrieve all needed data at once

---

### Anti-Pattern 6: EAV (Entity-Attribute-Value) Model for Flexible Schema

**Problem:** Poor performance, difficult indexing, complex queries.

**Detection:**  

- Table with columns like `entity_id`, `attribute`, `value`  
- Frequent pivoting/aggregation issues

**Operational Fix:**

- Use proper columns or separate tables for common attributes
- Only use EAV for truly unstructured/rarely queried data

---

### Anti-Pattern 7: No WHERE on DELETE/UPDATE

**Problem:** Unintentional full-table modifications.

**Detection:**  

- Queries: `UPDATE table SET ...` or `DELETE FROM table` with no WHERE

**Operational Fix:**

- Always require WHERE clause (enforce code review/linter)
- Use transactions and test with SELECT before destructive ops

---

### Anti-Pattern 8: Nullable Booleans/Unknown State

**Problem:** `NULL` vs `FALSE` meaning is ambiguous; predicates become non-sargable.

**Detection:**  

- Boolean columns allow NULL and appear in filters or joins
- Business logic treats NULL differently from false

**Operational Fix:**

- Set `NOT NULL` with default (e.g., `DEFAULT false`)
- Backfill existing NULLs and simplify predicates

---

### Anti-Pattern 9: Polymorphic Associations

**Problem:** Single FK column points to multiple tables (e.g., `parent_type/parent_id`), blocking FK enforcement and efficient indexing.

**Detection:**  

- Table has columns `parent_type`, `parent_id`
- No real foreign key constraints; queries branch on type

**Operational Fix:**

- Use separate linking tables per parent entity with real FKs
- If required, add database constraints via CHECK + FK per table

---

### Anti-Pattern 10: Adjacency Lists Without Traversal Aid

**Problem:** Hierarchical queries are slow/deep recursion heavy.

**Detection:**  

- Self-referencing FK only; repeated recursive CTEs for reads

**Operational Fix:**

- Add closure table or materialized path for reads; maintain via triggers/jobs
- Index path/ancestor columns to accelerate traversal

---

### Anti-Pattern 11: Overloaded Status/ENUM Columns

**Problem:** Single status column encodes multiple concerns (state + visibility + billing), making predicates brittle and non-indexable.

**Detection:**  

- Status column has >8 overloaded values or dual meaning
- Queries include many `status IN (...)` clauses with business rules embedded

**Operational Fix:**

- Split into focused columns (e.g., lifecycle_state, visibility_state)
- Use CHECK constraints and targeted indexes per concern

---

### Quick Detection Checklist

- [ ] Are there any SELECT * in production queries?
- [ ] Do all JOIN and WHERE columns have supporting indexes?
- [ ] Any WHERE using functions or casts on indexed columns?
- [ ] Are similar/overlapping indexes present?
- [ ] Any evidence of N+1 queries in logs/profiling?
- [ ] Is EAV used for highly structured or frequently queried data?
- [ ] Are all DML statements (UPDATE/DELETE) properly scoped with WHERE?

---

### Operational Anti-Pattern Table

| Symptom                   | Anti-Pattern                 | Operational Fix                       |
|---------------------------|------------------------------|---------------------------------------|
| Slow JOIN/table scan      | Unindexed join/filter column | Add index, verify predicate           |
| High query count per page | N+1 Query                    | JOIN/CTE, retrieve in batch           |
| Write slowness            | Too many/redundant indexes   | Drop unused/review index stats        |
| Hard to query schema      | EAV on structured data       | Redesign schema, add columns          |
| Large DELETE/UPDATE       | No WHERE clause              | Always require WHERE, review/test     |

---

### Edge Cases & Fallbacks

- If anti-pattern is detected in legacy code: Document risk, schedule refactor in technical debt backlog.
- If EAV is required: Restrict use to sparse, rarely queried attributes, and supplement with materialized views or summary tables for analytics.

---

*Use this guide to detect and immediately fix the most common SQL anti-patterns found in schema and query code reviews. All fixes are copy-paste ready and operationally safe for major RDBMS.*

```
