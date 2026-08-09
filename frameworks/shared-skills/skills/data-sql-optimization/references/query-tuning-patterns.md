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

## Decision Guide

| Symptom | Likely Lever |
|---------|--------------|
| Function/cast on filter column | Make predicate sargable or add expression index |
| OR predicates with bad plan | Test native plan first, then rewrite only if verified |
| Deep-page slowness | Keyset pagination |
| Parameter-dependent regressions | Separate query shapes or use engine-native parameter features |
| Large row explosion before aggregation | Pre-aggregate or filter earlier |
| Wildly wrong row estimates | Statistics, histograms, or extended statistics |

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
