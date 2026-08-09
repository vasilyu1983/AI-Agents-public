# SQL Best Practices

Purpose: keep tuning advice grounded in workload behavior and operational safety.

## Core Defaults

- Project only the columns the caller needs.
- Prefer predicates the optimizer can reason about directly.
- Align index design to real access paths, not hypothetical future queries.
- Keep transactions short and explicit.
- Re-test after data-shape, schema, or version changes.

## Query Review Checklist

- [ ] The query shape matches the business question
- [ ] Projection is explicit when row width matters
- [ ] Filters are sargable where possible
- [ ] Join predicates are explicit and typed consistently
- [ ] Pagination strategy matches depth and UX requirements
- [ ] Aggregations happen after unnecessary rows are removed
- [ ] Plan evidence exists for production-critical queries

## Cross-Engine Guidance

### Predicates

- Prefer range predicates over extracting year/month/day from an indexed timestamp.
- Avoid implicit casts on join and filter columns.
- Use expression indexes only when the transformed predicate is truly part of the workload.

### Joins and Subqueries

- Joins are not always better than subqueries.
- CTEs are not always bad for performance.
- The right question is: which shape produces the best verified plan on this engine and version?

### Sorting and Pagination

- Use keyset pagination for deep pages on hot endpoints.
- A LIMIT is only helpful if the engine can stop early or avoid a full expensive sort.

### Statistics

- PostgreSQL: `ANALYZE` and `CREATE STATISTICS` for correlated filters
- MySQL: optimizer statistics and histograms for skewed values
- SQL Server: Query Store plus current compatibility-level behavior for parameter-sensitive queries

## Safe Change Workflow

1. Measure baseline latency, reads, CPU, waits, and result size.
2. Capture plan evidence.
3. State the hypothesis.
4. Make one change.
5. Verify both performance and result correctness.
6. Monitor after deployment long enough to catch low-frequency workloads.

## Strong Recommendations

- Use representative data volume for tuning.
- Audit index usage before adding or dropping indexes.
- Pair performance analysis with lock/wait analysis in production incidents.
- Treat managed-service capabilities as versioned facts that must be checked before advising on them.

## Things To Avoid Teaching As Hard Rules

- "Always rewrite subqueries as joins"
- "Any sequential scan is bad"
- "Most selective column always goes first in a composite index"
- "OR should always become UNION"
- "Add an index whenever a query is slow"

## Final Check

- [ ] The recommendation is tied to a measured bottleneck
- [ ] The advice is correct for the specific engine and version
- [ ] The user has a rollback path for risky changes
- [ ] The query result semantics remain unchanged
