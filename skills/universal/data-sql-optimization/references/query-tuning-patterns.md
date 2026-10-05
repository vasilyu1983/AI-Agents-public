# Query Tuning Patterns

Purpose: tune query shape safely. Use these patterns when the likely fix is in the SQL itself rather than pure configuration.

## Table of Contents

- [Pattern 1: Make Predicates Sargable](#pattern-1-make-predicates-sargable)
- [Pattern 2: Treat OR Rewrites as a Measured Hypothesis](#pattern-2-treat-or-rewrites-as-a-measured-hypothesis)
- [Pattern 3: Replace Offset Pagination on Deep Pages](#pattern-3-replace-offset-pagination-on-deep-pages)
- [Pattern 4: Collapse N+1 Workloads](#pattern-4-collapse-n1-workloads)
- [Pattern 5: Fix Estimation Before Adding Indexes](#pattern-5-fix-estimation-before-adding-indexes)
- [Pattern 6: Reduce Rows Earlier](#pattern-6-reduce-rows-earlier)
- [Pattern 7: Remove Query Shape Ambiguity](#pattern-7-remove-query-shape-ambiguity)
- [Pattern 8: Pipeline the ORDER BY for Top-N](#pattern-8-pipeline-the-order-by-for-top-n)
- [Pattern 9: Greatest-N-Per-Group](#pattern-9-greatest-n-per-group)
- [Pattern 10: Bind Parameters and Skewed Distributions](#pattern-10-bind-parameters-and-skewed-distributions)
- [Decision Guide](#decision-guide)
- [Common Mistakes](#common-mistakes)
- [Verification Checklist](#verification-checklist)

## Pattern 1: Make Predicates Sargable

Use when the plan reads many rows and the filter applies a function or cast to the indexed column.

```sql
-- Avoid
WHERE DATE(order_created_at) = '2026-03-01'

-- Prefer
WHERE order_created_at >= '2026-03-01'
  AND order_created_at < '2026-03-02'
```

Notes:

- Move transformation to the constant side when semantics allow.
- If the business rule truly depends on the transformed value, use an expression or functional index where supported.

## Pattern 2: Treat OR Rewrites as a Measured Hypothesis

Use when a query has OR predicates and the plan shows poor selectivity handling.

```sql
-- Original
SELECT user_id
FROM users
WHERE email = 'a@example.com'
   OR phone = '+15551234567';

-- Rewrite only if verified faster and equivalent
SELECT user_id FROM users WHERE email = 'a@example.com'
UNION
SELECT user_id FROM users WHERE phone = '+15551234567';
```

Do not rewrite by reflex:

- MySQL can use index merge for OR predicates.
- PostgreSQL 18 can plan some OR cases more effectively than older versions.
- SQLite has explicit OR-term planner behavior that may already be acceptable.

## Pattern 3: Replace Offset Pagination on Deep Pages

Use when `OFFSET` grows large and latency scales with page depth.

```sql
-- Keyset pagination
SELECT id, created_at, status
FROM orders
WHERE (created_at, id) < ('2026-03-13 10:15:00+00', 9384201)
ORDER BY created_at DESC, id DESC
LIMIT 50;
```

Requirements:

- Stable sort key
- Matching index on the sort/filter columns
- Client can pass the last seen key

### Why It Beats OFFSET

`OFFSET` still makes the engine walk every row from the beginning of the ordered set
and throw away the ones before the requested page, so latency grows with page depth.
Winand names a second, less obvious problem: with `OFFSET`, *"the pages drift when
inserting new sales because the numbering is always done from scratch"* (*SQL
Performance Explained*, ch. 7, p. 149). Keyset pagination (Winand's "seek method")
uses the last row of the previous page as a delimiter, so the predicate becomes an
index **access** predicate and newly inserted rows do not shift page boundaries.

### The Deterministic-Sort Requirement

Keyset pagination is only correct if the `ORDER BY` yields a total order. Sorting by a
non-unique column alone silently loses or repeats rows: if several rows share the
boundary value, a simple `<` skips all of them, not just the ones already shown.

> Paging requires a deterministic sort order.
>
> — *SQL Performance Explained*, ch. 7, p. 150

Winand is explicit that this is the developer's job even when the spec does not ask
for it: *"Even if the functional specifications only require sorting 'by date, latest
first', we as the developers must make sure the order by clause yields a deterministic
row sequence."* Do not rely on observed stability — parallel query execution can return
a different order for the same plan on the same data.

The fix is a tie-breaker column, ideally one already in the index so the pipelined
`ORDER BY` survives; otherwise any unique column, with the index extended to match.

### Row-Value Syntax

The clean expression applies the "comes after" comparison to the whole key tuple at
once:

```sql
CREATE INDEX sl_dtid ON sales (sale_date, sale_id);

SELECT *
FROM sales
WHERE (sale_date, sale_id) < (?, ?)
ORDER BY sale_date DESC, sale_id DESC
FETCH FIRST 10 ROWS ONLY;
```

This is the SQL standard's row value constructor. Per SQL:92 §8.2.7.2, `RX < RY` holds
when `RXi = RYi` for all `i < n` and `RXn < RYn` for some `n` — exactly "RX sorts
before RY", which is the logic paging needs. Reverse the comparison for ascending
order.

Engine support for row values *as index access predicates* varies and has broadened
considerably since Winand's 2017 survey — verify against your engine's current version
rather than assuming. PostgreSQL has long supported both evaluating row values and
using them for index access. Confirm with `EXPLAIN` that the row-value comparison
appears as an index condition and not as a filter.

### The "Equivalent Logic" Trap

Where row values are not usable as access predicates, the logic must be spelled out —
and the obvious spelling is the slow one. This form is the readable one:

```sql
-- Logically correct, but the whole thing becomes a FILTER predicate
WHERE (sale_date < ?)
   OR (sale_date = ? AND sale_id < ?)
```

Optimizers generally do not factor the common bound out of the OR branches, so nothing
narrows the index range. Winand tested this and found *"none of the databases provides
this service"* (ch. 7, p. 155). Add the redundant bound manually so there is something
to seek on:

```sql
-- The redundant first term is what enables index access
WHERE sale_date <= ?
  AND ( (sale_date < ?)
     OR (sale_date = ? AND sale_id < ?) )
```

Now `sale_date <= ?` is the access predicate and the rest is a filter that discards a
few already-seen rows from the boundary page. Do not "clean up" that first line — it
looks redundant and is load-bearing.

### Known Limits

Keyset pagination cannot jump to an arbitrary page number, and browsing backwards means
reversing every comparison and sort direction. Both restrictions are irrelevant for
infinite-scroll UIs and fatal for a numbered-page UI that must offer "jump to page 47".
Choose the pagination model and the UI together.

## Pattern 4: Collapse N+1 Workloads

Use when application logs or tracing show repeated child queries per parent row.

```sql
SELECT c.id, c.name, o.id AS order_id, o.total_amount
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE c.id = ANY($1);
```

Do not over-join blindly. Batch loading, prefetch, or a summary table can be better depending on row explosion risk.

## Pattern 5: Fix Estimation Before Adding Indexes

Use when the plan is unstable or actual rows differ sharply from estimates.

Typical fixes:

- PostgreSQL: `ANALYZE`, then `CREATE STATISTICS` for correlated columns
- MySQL: histograms for skewed columns
- SQL Server: Query Store review, parameter-sensitive plan analysis, OPPO eligibility

## Pattern 6: Reduce Rows Earlier

Use when expensive joins, sorts, or aggregations happen on far more rows than the final result needs.

Preferred tactics:

- push selective predicates before broad joins when semantics allow
- pre-aggregate one side of a one-to-many join before joining
- narrow projection so the plan can use covering/index-only behavior

Avoid cargo-cult rules like "always replace subqueries with joins." Some subqueries are already optimal.

## Pattern 7: Remove Query Shape Ambiguity

Use when a single query tries to handle many optional filters and produces unstable plans.

Typical approaches:

- split into separate query shapes in the application
- generate SQL only for active predicates
- on SQL Server, check whether OPPO already handles the optional-parameter case

## Pattern 8: Pipeline the ORDER BY for Top-N

Use when a query sorts a large set only to return the first few rows.

An `ORDER BY` that matches an existing index lets the engine read rows already in
order, skip the sort operator entirely, and stop as soon as the row limit is met. When
no such index exists, the engine must read and sort the whole result set before it can
return the first row.

```sql
-- Pipelined: the index supplies the order, execution aborts after 10 rows
CREATE INDEX idx_sales_date ON sales (sale_date DESC);

SELECT * FROM sales ORDER BY sale_date DESC FETCH FIRST 10 ROWS ONLY;
```

What to look for in the plan:

- **PostgreSQL** — no `Sort` node above the index scan. A `Limit` directly over an
  `Index Scan` is pipelined; `Limit` over `Sort` over `Seq Scan` is not.
- **Oracle** — `COUNT STOPKEY` without `SORT ORDER BY`; `SORT ORDER BY STOPKEY`
  means it is materializing.
- **SQL Server / MySQL** — check for an explicit sort operator between the scan and
  the row-limiting step.

Two conditions must both hold, and the second is easy to miss:

1. An index covers the `ORDER BY` in a compatible direction.
2. The engine **knows** the query is row-limited when it plans. Fetching a few rows
   and closing the cursor does not qualify — the optimizer has already committed to a
   plan. Use `LIMIT` / `FETCH FIRST` / `TOP` so the limit is part of the statement.
   Winand: *"Inform the database whenever you don't need all rows."*

The scalability argument, direction only — Winand reports no magnitudes worth quoting
here: without pipelining, response time grows with table size; with it, response time
grows with the number of rows *selected* and is largely independent of table size
(*SQL Performance Explained*, ch. 7, pp. 146–147). This is also why deep `OFFSET`
paging degrades even on a pipelined plan: the row count being read still grows page by
page. See [Pattern 3](#pattern-3-replace-offset-pagination-on-deep-pages).

Note that `ORDER BY` direction interacts with composite indexes: mixed
`ORDER BY a ASC, b DESC` needs an index declared in matching directions, or the engine
falls back to a sort.

## Pattern 9: Greatest-N-Per-Group

Use when you need the whole row that holds the max (or min) per group — not just the
aggregate value.

The naive form is wrong, not merely slow:

```sql
-- Broken: bug_id is not functionally dependent on the grouping key
SELECT product_id, MAX(date_reported) AS latest, bug_id
FROM bugs JOIN bugs_products USING (bug_id)
GROUP BY product_id;
```

Karwin calls this the Single-Value Rule violation (*SQL Antipatterns, Vol. 1*, ch. 15,
"Ambiguous Groups"). Every select-list column must have one value per group; `bug_id`
does not, and nothing connects it to the row where `MAX` was found. Most engines reject
this. MySQL rejects it too since 5.7 under the default `ONLY_FULL_GROUP_BY`. MySQL
without that mode and SQLite accept it and return an arbitrary row's value — MySQL
takes the first row in the group by physical storage, SQLite the last, and neither
behavior is documented or guaranteed to persist across versions.

### Solution Ladder

Ordered roughly worst-to-best for large data. Measure rather than assume.

**1. Correlated subquery / `NOT EXISTS`** — readable, poor scaling.

```sql
SELECT bp1.product_id, b1.date_reported AS latest, b1.bug_id
FROM bugs b1 JOIN bugs_products bp1 USING (bug_id)
WHERE NOT EXISTS (
  SELECT * FROM bugs b2 JOIN bugs_products bp2 USING (bug_id)
  WHERE bp1.product_id = bp2.product_id
    AND b1.date_reported < b2.date_reported);
```

Karwin: *"this solution isn't likely to be the best for performance, because correlated
subqueries are executed once for each row of the outer query."*

**2. Derived table** — noncorrelated, so the subquery runs once, but the interim result
must be materialized. Note it can return **multiple rows per group** when the max value
ties; add a tie-breaker if you need exactly one.

**3. Window function `ROW_NUMBER()`** — the default modern answer. One pass, explicit
tie-breaking, exactly one row per group.

```sql
SELECT product_id, date_reported, bug_id
FROM (
  SELECT bp.product_id, b.date_reported, b.bug_id,
         ROW_NUMBER() OVER (PARTITION BY bp.product_id
                            ORDER BY b.date_reported DESC, b.bug_id DESC) AS rn
  FROM bugs b JOIN bugs_products bp USING (bug_id)
) t
WHERE t.rn = 1;
```

The `ORDER BY` inside `OVER` needs its own tie-breaker for a deterministic result —
same requirement as keyset pagination. Use `RANK()` instead if you want all tied rows.

**4. `LATERAL` / top-1-per-group join** — usually the fastest when the group keys live
in a small driving table and an index supports the per-group ordering, because each
group does one indexed lookup instead of scanning all rows.

```sql
SELECT p.id, b.date_reported, b.bug_id
FROM products p
CROSS JOIN LATERAL (
  SELECT b.date_reported, b.bug_id
  FROM bugs b JOIN bugs_products bp USING (bug_id)
  WHERE bp.product_id = p.id
  ORDER BY b.date_reported DESC, b.bug_id DESC
  LIMIT 1
) b;
```

`LATERAL` is PostgreSQL/Oracle syntax; SQL Server spells it `CROSS APPLY` / `OUTER
APPLY`. It shines with few groups and many rows per group, and loses to the window
function when the group count approaches the row count.

Two non-solutions worth naming: applying a second aggregate (`MAX(bug_id)`) is only
correct if that column's max always coincides with the ordering column's max, and
`GROUP_CONCAT` / `string_agg` answers a different question — it returns all values in
the group, not the one belonging to the max.

## Pattern 10: Bind Parameters and Skewed Distributions

Use when a parameterized query performs unpredictably on a column whose values are
unevenly distributed.

Bind parameters should be the default: they prevent SQL injection and let the engine
reuse a cached plan. The exception is narrow but sharp. With a literal value, the
optimizer consults the column histogram, estimates how many rows that specific value
matches, and prices the plan accordingly. With a placeholder it cannot: Winand's
description is that the optimizer *"has no concrete values available to determine their
frequency. It then just assumes an equal distribution and always gets the same row
count estimates and cost values. In the end, it will always select the same execution
plan"* (*SQL Performance Explained*, ch. 2, p. 34).

On a skewed column that single plan is wrong for one end of the distribution. The
classic shape is a status column where `'done'` outnumbers `'todo'` by orders of
magnitude: an index scan is right for `'todo'` and a sequential scan is right for
`'done'`, and a generic plan picks one and loses on the other. Partitioned tables have
the same problem, since the literal value can determine which partitions are scanned.

Winand's rule: *"you should always use bind parameters except for values that shall
influence the execution plan"*, with the balancing caution that *"there are only a few
cases in which the actual values affect the execution plan. You should therefore use
bind parameters if in doubt — just to prevent SQL injections."*

### PostgreSQL's Generic vs Custom Plan Machinery

Since PostgreSQL 9.2, this is not purely a choose-one decision. For
prepared statements, PostgreSQL builds a **custom plan** (re-planned with the actual
parameter values) for the first several executions, then compares the average custom
plan cost against a **generic plan** cost; if the generic plan is not more expensive,
it switches to it and stops re-planning. The heuristic is documented as taking effect
after roughly the first five executions — verify against the `PREPARE` documentation
for your major version, as the details have changed over time.

Override it with `plan_cache_mode`:

```sql
-- Force re-planning per execution: skewed column, plan matters more than planning cost
SET plan_cache_mode = 'force_custom_plan';

-- Force plan reuse: uniform distribution, high execution rate, planning is the cost
SET plan_cache_mode = 'force_generic_plan';

-- Default: let the cost comparison decide
SET plan_cache_mode = 'auto';
```

Set this at session or transaction scope for the specific workload rather than
globally. Note that this machinery applies to server-side prepared statements — whether
your driver or pooler uses them is a separate question, and transaction-mode poolers
may prevent statements from surviving long enough to reach the generic-plan threshold
at all.

Other engines expose different levers for the same problem: SQL Server has parameter
sniffing plus OPPO and Query Store for diagnosis, MySQL relies on histograms. In all
cases, diagnose before overriding — confirm the regression really is
parameter-sensitivity and not stale statistics.

## Decision Guide

| Symptom | Likely Lever |
|---------|--------------|
| Function/cast on filter column | Make predicate sargable or add expression index |
| OR predicates with bad plan | Test native plan first, then rewrite only if verified |
| Deep-page slowness | Keyset pagination |
| Parameter-dependent regressions | Separate query shapes or use engine-native parameter features |
| Large row explosion before aggregation | Pre-aggregate or filter earlier |
| Wildly wrong row estimates | Statistics, histograms, or extended statistics |
| Sort before a small LIMIT | Add an index matching the ORDER BY so the sort is pipelined |
| Row-per-group query returns wrong or arbitrary rows | Window function `ROW_NUMBER()`, or `LATERAL` when groups are few |
| Prepared statement fast for some values, slow for others | Skewed column with a generic plan; check `plan_cache_mode` |

## Common Mistakes

- Rewriting into CTEs or joins without verifying semantics and runtime.
- Treating UNION ALL as a universal replacement for OR.
- Assuming LIMIT alone makes a query cheap if the engine still must sort or scan a large set.
- Fixing query shape while ignoring pool contention or lock waits.

## Verification Checklist

- [ ] Baseline captured before rewrite
- [ ] Rewritten query returns equivalent results
- [ ] Matching index exists for the new filter/order pattern
- [ ] Statistics-related fixes tested before index proliferation
- [ ] Deep-page and worst-case parameters tested, not only happy-path inputs
