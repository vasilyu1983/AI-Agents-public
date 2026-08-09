# SQL Performance Tuning Worksheet (Explain -> Hypothesis -> Change -> Verify)

Systematic workflow: Explain -> Hypothesis -> Change -> Verify (with baseline measurement)

---

## Core

## Step 1: Explain (Baseline + Context)

### Query Identification

**Query under investigation:**
```sql
-- Paste the slow query here
```

**Current metrics:**
| Metric | Value | Target |
|--------|-------|--------|
| Execution time | ___ ms | < ___ ms |
| Rows scanned | ___ | < ___ |
| Rows returned | ___ | ___ |
| Buffer hits | ___ | > 95% |
| Temp disk usage | ___ MB | 0 MB |

**Measurement commands:**

```sql
-- PostgreSQL: Enable timing
\timing on

-- PostgreSQL: Get execution stats
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) <your_query>;

-- MySQL: Enable profiling
SET profiling = 1;
<your_query>;
SHOW PROFILE FOR QUERY 1;

-- SQL Server: Enable statistics
SET STATISTICS IO ON;
SET STATISTICS TIME ON;
<your_query>;
```

### Context Gathering

- [ ] Table row counts documented
- [ ] Index list captured
- [ ] Current statistics age checked
- [ ] Concurrent workload noted
- [ ] Hardware/resource constraints known

---

## Step 2: Hypothesis (Plan-Based)

### Execution Plan Review

**Plan summary:**
```text
-- Paste EXPLAIN output here
```

### Cost Breakdown

| Operation | Est. Rows | Est. Cost | Actual Rows | Actual Time |
|-----------|-----------|-----------|-------------|-------------|
| Seq Scan on X | | | | |
| Index Scan on Y | | | | |
| Hash Join | | | | |
| Sort | | | | |
| Aggregate | | | | |

### Red Flags Checklist

- [ ] **Sequential scan** on large table (>10k rows)
- [ ] **Nested loop** with high outer row count
- [ ] **Sort** operation spilling to disk
- [ ] **Hash join** with large build table
- [ ] **Filter** removing >50% of rows late in plan
- [ ] **Estimate vs actual** mismatch (>10x difference)
- [ ] **Missing index** hint in plan warnings

### Root Cause Hypothesis

| Hypothesis | Evidence | Likelihood |
|------------|----------|------------|
| Missing index on filter column | Seq scan on WHERE clause | High/Med/Low |
| Stale statistics | Estimate vs actual mismatch | High/Med/Low |
| Suboptimal join order | Small table scanned first | High/Med/Low |
| N+1 query pattern | Query executed in loop | High/Med/Low |
| Inefficient predicate | Function on indexed column | High/Med/Low |

**Primary hypothesis:**
```text
[State the most likely cause based on evidence]
```

---

## Step 3: Change (Intervention)

### Proposed Changes

| Change | Rationale | Risk | Reversibility |
|--------|-----------|------|---------------|
| Add index on X(col) | Enable index scan | Low | DROP INDEX |
| Rewrite subquery as JOIN | Avoid correlated scan | Medium | Revert SQL |
| Update statistics | Fix estimate mismatch | Low | Auto-recovers |
| Add LIMIT/pagination | Reduce result set | Low | Remove LIMIT |
| Denormalize lookup | Eliminate join | High | Schema rollback |

### Index Creation (if applicable)

```sql
-- PostgreSQL: B-tree index
CREATE INDEX CONCURRENTLY idx_table_column
ON table_name (column_name)
WHERE condition;  -- Partial index if applicable

-- MySQL: Index with prefix
CREATE INDEX idx_table_column
ON table_name (column_name(255));

-- Composite index (leftmost prefix rule)
CREATE INDEX idx_table_multi
ON table_name (col1, col2, col3);
```

### Query Rewrite (if applicable)

**Before:**
```sql
-- Original slow query
```

**After:**
```sql
-- Optimized query
```

**Changes made:**
- [ ] Removed SELECT *
- [ ] Added explicit column list
- [ ] Converted subquery to JOIN
- [ ] Added predicate pushdown
- [ ] Used EXISTS instead of IN
- [ ] Added LIMIT for pagination
- [ ] Removed function on indexed column

### Statistics Update (if applicable)

```sql
-- PostgreSQL: Update statistics
ANALYZE table_name;
ANALYZE table_name (specific_column);

-- PostgreSQL: More detailed stats
ALTER TABLE table_name ALTER COLUMN col SET STATISTICS 1000;
ANALYZE table_name;

-- MySQL: Update statistics
ANALYZE TABLE table_name;
```

---

## Step 4: Verify (Validation)

### Post-Change Metrics

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| Execution time | ___ ms | ___ ms | ___% |
| Rows scanned | ___ | ___ | ___% |
| Buffer hits | ___% | ___% | +___% |
| Temp disk usage | ___ MB | ___ MB | ___% |

### New Execution Plan

```text
-- Paste new EXPLAIN output here
```

### Validation Checklist

- [ ] Query returns same results
- [ ] Execution time meets target
- [ ] No regression on related queries
- [ ] Index used as expected in plan
- [ ] No new warnings in plan

### Regression Testing

```sql
-- Compare result sets (should be empty if equal)
SELECT * FROM (
    -- Original query results
) original
EXCEPT
SELECT * FROM (
    -- Optimized query results
) optimized;
```

### Load Testing (if critical query)

- [ ] Tested under concurrent load
- [ ] Tested with production-like data volume
- [ ] Tested with cold cache

---

## Decision Log

| Date | Change | Result | Keep/Revert |
|------|--------|--------|-------------|
| YYYY-MM-DD | Added index on X | 80% improvement | Keep |
| YYYY-MM-DD | Rewrote subquery | No change | Revert |

---

## Do / Avoid

### GOOD: Do

- Measure baseline before any change
- Change one variable at a time
- Verify results match after optimization
- Document all changes and rationale
- Test with representative data volumes
- Check for query plan regressions after index changes
- Update statistics before concluding "needs index"

### BAD: Avoid

- Adding indexes without checking if they'll be used
- Optimizing queries without understanding the plan
- Assuming more indexes = better performance
- Ignoring write performance impact of indexes
- Skipping verification step
- Optimizing for test data volumes (not production)
- Making multiple changes simultaneously

---

## Anti-Patterns Detected

| Anti-Pattern | Found? | Fix Applied |
|--------------|--------|-------------|
| SELECT * | [ ] | [ ] |
| N+1 queries | [ ] | [ ] |
| Missing WHERE clause | [ ] | [ ] |
| Function on indexed column | [ ] | [ ] |
| Implicit type conversion | [ ] | [ ] |
| Unbounded result set | [ ] | [ ] |
| OR conditions preventing index use | [ ] | [ ] |
| LIKE '%prefix' pattern | [ ] | [ ] |

---

## Optional: AI/Automation

> **Note**: AI tools should supplement, not replace, systematic analysis.

### AI-Assisted Analysis

- EXPLAIN plan summarization (identify bottlenecks)
- Query rewrite suggestions (must be validated)
- Index recommendation review (check selectivity first)

### Bounded Claims

- AI suggestions require human verification of correctness
- Automated index recommendations may miss workload context
- Query rewrites must be tested for result equivalence

---

## Related Templates

- [template-explain-analysis.md](template-explain-analysis.md) — Deep EXPLAIN plan interpretation
- [template-index.md](template-index.md) — Index design patterns
- [template-slow-query.md](template-slow-query.md) — Slow query triage

---

**Last Updated**: December 2025
