# SQL Anti-Patterns

*Purpose: Operational detection and remediation of common SQL anti-patterns, with step-by-step patterns and quick references for safe query and schema optimization.*

---
## Table of Contents

- [Core Patterns](#core-patterns)
- [Anti-Pattern 1: SELECT *](#anti-pattern-1-select)
- [Anti-Pattern 2: No Index on Foreign Keys/Join Columns](#anti-pattern-2-no-index-on-foreign-keysjoin-columns)
- [Anti-Pattern 3: Non-Sargable Predicates](#anti-pattern-3-non-sargable-predicates)
- [Anti-Pattern 4: Over-Indexing](#anti-pattern-4-over-indexing)
- [Anti-Pattern 5: N+1 Query Pattern](#anti-pattern-5-n1-query-pattern)
- [Anti-Pattern 6: EAV (Entity-Attribute-Value) Model for Flexible Schema](#anti-pattern-6-eav-entity-attribute-value-model-for-flexible-schema)
- [Anti-Pattern 7: No WHERE on DELETE/UPDATE](#anti-pattern-7-no-where-on-deleteupdate)
- [Anti-Pattern 8: Nullable Booleans/Unknown State](#anti-pattern-8-nullable-booleansunknown-state)
- [Anti-Pattern 9: Polymorphic Associations](#anti-pattern-9-polymorphic-associations)
- [Anti-Pattern 10: Adjacency Lists Without Traversal Aid](#anti-pattern-10-adjacency-lists-without-traversal-aid)
- [Anti-Pattern 11: Overloaded Status/ENUM Columns](#anti-pattern-11-overloaded-statusenum-columns)
- [Anti-Pattern 12: Three-Valued Logic and NULL](#anti-pattern-12-three-valued-logic-and-null)
- [Quick Detection Checklist](#quick-detection-checklist)
- [Operational Anti-Pattern Table](#operational-anti-pattern-table)
- [Edge Cases & Fallbacks](#edge-cases-&-fallbacks)


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

**Problem:** Using functions or computations on indexed columns (e.g., `WHERE LOWER(name) = ...` or `WHERE YEAR(date) = <YEAR>`).

**Detection:**

- WHERE uses function or computation on indexed column
- Plan shows table/seq scan

**Operational Fix:**

- Refactor to compare directly, or use a functional index if supported

```sql
-- Bad:
WHERE YEAR(order_date) = <YEAR>
-- Good:
WHERE order_date >= '<YEAR>-01-01' AND order_date < '<YEAR+1>-01-01'
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

Rule: `rules/sql/safety.md` loads this invariant when Claude edits a matching file.

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

### Anti-Pattern 12: Three-Valued Logic and NULL

**Problem:** SQL is not two-valued. `NULL` means "unknown", and comparisons against it
return `NULL` rather than `TRUE` or `FALSE`. Code written with a Python or Java mental
model produces silently wrong results — most destructively, queries that return zero
rows and look like "no matches" rather than a bug.

Karwin's framing (*SQL Antipatterns, Vol. 1*, ch. 14, "Fear of the Unknown") is that
using `NULL` is not itself the antipattern: *"the antipattern is using null like an
ordinary value or using an ordinary value like null."*

**Detection:**

- Any `NOT IN (SELECT ...)` where the subquery column is nullable
- Equality or inequality comparisons against a nullable column without an `IS NULL` arm
- A query that returns zero rows when the data clearly contains matches
- Sentinel values (`-1`, `'N/A'`, `9999-12-31`) standing in for "unknown"

#### Scalar and Boolean Truth Tables

These are the cases where the result differs from what most programmers expect
(Karwin, ch. 14):

| Expression | Expected | Actual | Because |
|------------|----------|--------|---------|
| `NULL = 0` | TRUE | NULL | Null is not zero. |
| `NULL = 12345` | FALSE | NULL | Unknown if the unspecified value is equal to a given value. |
| `NULL <> 12345` | TRUE | NULL | Also unknown if it's unequal. |
| `NULL + 12345` | 12345 | NULL | Null is not zero. |
| `NULL \|\| 'string'` | 'string' | NULL | Null is not an empty string. |
| `NULL = NULL` | TRUE | NULL | Unknown if one unspecified value is the same as another. |
| `NULL <> NULL` | FALSE | NULL | Also unknown if they're different. |

| Expression | Expected | Actual | Because |
|------------|----------|--------|---------|
| `NULL AND TRUE` | FALSE | NULL | Null is not false. |
| `NULL AND FALSE` | FALSE | FALSE | Any truth value AND FALSE is false. |
| `NULL OR FALSE` | FALSE | NULL | Null is not false. |
| `NULL OR TRUE` | TRUE | TRUE | Any truth value OR TRUE is true. |
| `NOT (NULL)` | TRUE | NULL | Null is not false. |

The two rows that do behave predictably — `AND FALSE` and `OR TRUE` — are the reason
`NOT IN` fails and `NOT EXISTS` does not.

#### The `NOT IN (NULL)` Trap

This is the highest-impact instance, documented independently by both Karwin (ch. 14,
"Mini-Antipattern: NOT IN (NULL)") and Angelakos (*PostgreSQL Mistakes and How to Avoid
Them*, §2.1). A single `NULL` anywhere in the `NOT IN` list makes the predicate return
zero rows — always, regardless of the data.

```sql
-- Returns rows as expected
SELECT * FROM bugs WHERE status IN (NULL, 'NEW');

-- Returns NOTHING. Not "everything except NEW" — nothing at all.
SELECT * FROM bugs WHERE status NOT IN (NULL, 'NEW');
```

Why, per Karwin: `NOT IN` expands to negated equality comparisons combined with `AND`
(by De Morgan's law), so `NOT (status = NULL) AND NOT (status = 'NEW')`. The first term
is `NOT (NULL)`, which is `NULL`. `NULL AND anything` is never `TRUE`, so no row ever
matches.

The production-realistic version is a subquery, where nobody notices the `NULL`.
Angelakos's worked case: a query for customers in states with no supplier returned zero
rows because one supplier — a non-US company — had `NULL` in its `state` column.

```sql
-- Broken: one NULL state in suppliers makes this return zero rows
SELECT email FROM erp.customer_contact_details
WHERE state NOT IN (SELECT state FROM erp.suppliers);
```

Angelakos: *"the predicate state NOT IN (SELECT state FROM erp.suppliers) can never
return TRUE if even one NULL is present."*

**Operational Fix — prefer `NOT EXISTS`:**

```sql
SELECT ccd.email
FROM erp.customer_contact_details ccd
WHERE NOT EXISTS (SELECT FROM erp.suppliers s
                  WHERE ccd.state = s.state)
  AND ccd.state IS NOT NULL;
```

This is correct *and* faster. `NOT IN (SELECT ...)` cannot be converted into an
anti-join by the PostgreSQL planner, which falls back to a hashed or plain subplan;
Angelakos notes the hashed form is only chosen for small result sets and the plain
subplan is very slow, so such a query *"may offer decent performance on a small scale
but can slow down by whole orders of magnitude if you cross a size threshold."* The
`NOT EXISTS` form plans as a `Hash Anti Join`. A `LEFT JOIN ... WHERE s.state IS NULL`
is an equivalent anti-join formulation.

`NOT IN` remains safe against a literal list you control, or a subquery on a `NOT NULL`
column. The risk is that the column's nullability can change later, so `NOT EXISTS` is
the better default.

#### Null-Safe Comparison: `IS DISTINCT FROM`

`IS DISTINCT FROM` behaves like `<>` but always returns `TRUE` or `FALSE`, never
`NULL`. It removes the need for hand-written `IS NULL OR ...` arms. These are
equivalent:

```sql
SELECT * FROM bugs WHERE assigned_to IS NULL OR assigned_to <> 1;
SELECT * FROM bugs WHERE assigned_to IS DISTINCT FROM 1;
```

It is especially useful with a bind parameter that may itself be `NULL` — one predicate
handles both cases:

```sql
SELECT * FROM bugs WHERE assigned_to IS DISTINCT FROM ?;
```

**Portability — verify per engine and version.** Karwin's 2022 survey listed
PostgreSQL, IBM DB2, and Firebird as supporting it, with Oracle and Microsoft SQL
Server not yet doing so, and MySQL offering the proprietary `<=>` operator equivalent
to `IS NOT DISTINCT FROM`. That snapshot has since moved: SQL Server added
`IS [NOT] DISTINCT FROM` in SQL Server 2022. Check your target engine's current
documentation rather than assuming either the old or new state, and be aware that
`IS DISTINCT FROM` may not be usable as an index access predicate even where it is
supported — verify with `EXPLAIN` on hot paths.

#### Other Fixes

- **Declare `NOT NULL` wherever a null would be nonsensical.** Karwin: *"It's better to
  allow the database to enforce constraints uniformly rather than rely on application
  code."* Note that a column can legitimately need `NOT NULL` while having no sensible
  `DEFAULT` — do not add a sentinel default just to satisfy a blanket rule.
- **Use `COALESCE` for presentation, not storage.** It supplies a non-null value in a
  result set without writing a fake value into the table. String concatenation is the
  classic case: one null middle initial nulls the entire concatenated name.
- **Never use a sentinel value to mean "unknown".** Karwin's warning is that any flag
  value inside the column's legitimate domain will eventually be needed for its literal
  meaning. `-1`, `0`, and `9999-12-31` all silently corrupt aggregates — `AVG` counts
  them, `NULL` is correctly ignored.
- **Watch aggregate semantics.** `count(col)` ignores nulls while `count(*)` does not;
  this is correct behavior and a frequent source of "wrong" totals.

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
