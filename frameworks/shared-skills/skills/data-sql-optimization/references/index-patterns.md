```markdown
# Index Patterns

*Purpose: Copy-paste ready index design templates, anti-pattern avoidance, and decision trees for reliable query acceleration.*

---

## Core Patterns

### Pattern 1: Basic Single-Column Index

**Use when:** Query frequently filters on one column (e.g., WHERE user_id = ?)

**Example:**
```sql
CREATE INDEX idx_table_user_id ON my_table(user_id);
```

**Checklist:**

- [ ] Index name follows convention (`idx_tablename_column`)
- [ ] Column is high-cardinality (not boolean/low-selectivity)
- [ ] Index supports WHERE/join/filter in common queries

---

### Pattern 2: Multi-Column (Composite) Index

**Use when:** Query filters on two or more columns together or filters and sorts.

**Example:**

```sql
-- Supports WHERE a=? AND b=?
CREATE INDEX idx_table_a_b ON my_table(a, b);

-- Supports WHERE a=? AND b=? ORDER BY c
CREATE INDEX idx_table_a_b_c ON my_table(a, b, c);
```

**Checklist:**

- [ ] Columns ordered by most selective/useful filter first
- [ ] Matches left-to-right prefix usage in queries

---

### Pattern 3: Covering/INCLUDE Index (PostgreSQL, SQL Server)

**Use when:** Query reads columns not in filter but always together (covering index). Eliminates Key Lookups/table access entirely.

**Example (Postgres):**

```sql
CREATE INDEX idx_orders_user_id_include ON orders(user_id) INCLUDE (status, created_at);
```

**Example (SQL Server):**

```sql
CREATE INDEX idx_orders_user_id ON orders(user_id) INCLUDE (status, created_at);
```

**Why covering indexes matter:**

- Query can be satisfied entirely from the index (Index-Only Scan)
- Eliminates expensive Key Lookup / RID Lookup operations
- Reduces I/O by 10-100x for high-traffic queries

**Checklist:**

- [ ] INCLUDE only frequently-read columns (SELECT list)
- [ ] Use for high-traffic analytical/reporting queries
- [ ] Verify with EXPLAIN that "Index Only Scan" appears (Postgres) or no Key Lookup (SQL Server)

---

### Pattern 4: Partial/Filtered Index

**Use when:** Only a subset of rows are frequently filtered (e.g., WHERE status = 'active').

**Example:**

```sql
CREATE INDEX idx_table_active_only ON my_table(user_id) WHERE status = 'active';
```

**Checklist:**

- [ ] WHERE condition matches query predicate
- [ ] Reduces index size, write cost

---

### Pattern 5: Expression/Functional Index

**Use when:** Filtering on computed value or function (e.g., WHERE lower(email) = ...)

**Example (Postgres):**

```sql
CREATE INDEX idx_users_lower_email ON users(LOWER(email));
```

**Checklist:**

- [ ] Query uses function matching index expression exactly
- [ ] Supported only in databases with functional index support

---

### Pattern 6: Skip Scan (PostgreSQL 18+)

**Use when:** Query filters on non-leading columns of a composite index.

**Background:** Before PostgreSQL 18, composite indexes required filters on leading columns. Skip scan allows the optimizer to "skip" over distinct values of the leading column.

**Example:**

```sql
-- Composite index on (tenant_id, created_at)
CREATE INDEX idx_orders_tenant_created ON orders(tenant_id, created_at);

-- Query that ONLY filters on created_at (no tenant_id)
SELECT * FROM orders WHERE created_at > '2025-01-01';

-- PostgreSQL 18: Uses skip scan instead of sequential scan
-- PostgreSQL 17 and earlier: Sequential scan (index not usable)
```

**When skip scan helps:**

- Low cardinality on leading column (few distinct values)
- Frequently query non-leading columns
- Don't want to create separate single-column indexes

**Checklist:**

- [ ] PostgreSQL 18+ required
- [ ] Leading column has low-to-medium cardinality
- [ ] Verify skip scan in EXPLAIN output

---

## Decision Tree

**If query is slow:**

- Does WHERE or JOIN use an indexed column? -> If not, add index for column(s)
- Are multiple columns filtered? -> Use composite index in the same order as query
- Are only a subset of rows needed? -> Use partial/filtered index
- Is query filtering on function? -> Add functional index if supported

---

## Common Anti-Patterns

[FAIL] **Over-indexing every column:**  
Slows down writes and bloats storage.  
[OK] **Instead:** Index only for high-value queries—review usage with statistics.

[FAIL] **Wrong index column order in composite index:**  
Only leading columns used for seeking.  
[OK] **Instead:** Order columns in index to match WHERE/JOIN patterns.

[FAIL] **Unused or redundant indexes:**  
Wasted space, overhead on insert/update.  
[OK] **Instead:** Regularly audit with index usage stats; drop unused.

[FAIL] **Index on low-cardinality column (e.g., is_active):**  
Not selective, not helpful.  
[OK] **Instead:** Index higher-cardinality columns or use as part of composite.

---

## Quick Reference Table

| Query Type                                | Recommended Index Example                               |
|-------------------------------------------|--------------------------------------------------------|
| WHERE col = ?                             | CREATE INDEX idx_table_col ON table(col);              |
| WHERE a = ? AND b = ?                     | CREATE INDEX idx_table_a_b ON table(a, b);             |
| WHERE status = 'active'                   | CREATE INDEX idx_table_active ON table(col) WHERE status='active'; |
| WHERE lower(email) = ?                    | CREATE INDEX idx_lower_email ON table(LOWER(email));   |
| ORDER BY created_at DESC                  | CREATE INDEX idx_created_at ON table(created_at DESC);  |
| JOIN ... ON a.id = b.a_id                 | CREATE INDEX idx_b_a_id ON b(a_id);                    |
| SELECT a, b, c WHERE a = ? (covering)     | CREATE INDEX idx ON table(a) INCLUDE (b, c);           |
| WHERE b = ? (skip scan, PG18+)            | CREATE INDEX idx ON table(a, b); -- skip scan on b     |

---

## Quality Checklist

- [ ] Indexes match real query patterns (profiled in production)
- [ ] No redundant/duplicate indexes
- [ ] Write overhead considered for all new indexes
- [ ] Indexes periodically reviewed/dropped as needed
- [ ] Naming conventions followed

---

*All index patterns above are copy-paste ready for operational tuning. Always validate with EXPLAIN before/after creation, and monitor impact on writes and reads.*

```
