# Metabase Native Query Patterns

> Purpose: Operational reference for writing effective SQL in Metabase — variables, field filters, template tags, SQL snippets, caching, performance tuning, and common gotchas. Freshness anchor: Q1 2026.

---

## Quick Reference: Template Tag Types

| Tag Type | Syntax | Generates | Use When |
|----------|--------|-----------|----------|
| Text | `{{text_var}}` | String literal (quoted) | Free-text filter input |
| Number | `{{number_var}}` | Numeric literal | ID or amount filters |
| Date | `{{date_var}}` | Date literal | Date range filtering |
| Field Filter | `{{field_filter_var}}` | Full WHERE clause | Dynamic dashboard filters |
| Snippet | `{{snippet: name}}` | Reusable SQL fragment | Shared CTEs or conditions |
| Card (Sub-query) | `{{#card_id}}` | Saved question as subquery | Composing questions |

---

## Variables (Text, Number, Date)

### Basic Variable Syntax

```sql
-- Text variable: user types a string
SELECT *
FROM orders
WHERE status = {{status}}

-- Number variable: user types a number
SELECT *
FROM orders
WHERE customer_id = {{customer_id}}

-- Date variable: user selects a date
SELECT *
FROM orders
WHERE created_at >= {{start_date}}
  AND created_at < {{end_date}}
```

### Variable Configuration

```
Click variable tag in editor sidebar:
├── Variable type: Text | Number | Date
├── Filter widget type: dropdown, search, date picker
├── Required: yes/no
├── Default value: optional
└── Label: human-readable name
```

### Optional Variables (Handle NULL)

```sql
-- Optional filter: include WHERE only when value provided
SELECT *
FROM orders
WHERE 1=1
  [[AND status = {{status}}]]
  [[AND region = {{region}}]]
  [[AND created_at >= {{start_date}}]]

-- The [[ ]] brackets make the clause optional
-- If user leaves filter empty, clause is excluded entirely
```

### Variable Gotchas

| Issue | Cause | Fix |
|-------|-------|-----|
| Text variable adds unwanted quotes | Metabase auto-quotes text vars | Use for string comparisons only |
| Number in text variable causes type error | Variable type mismatch | Set variable type to Number |
| Date comparison returns no results | Timezone mismatch | Use `::date` cast or `DATE_TRUNC` |
| Optional clause breaks SQL | Syntax error inside `[[ ]]` | Ensure `[[ ]]` wraps complete AND clause |
| Variable in LIKE clause fails | Auto-quoting interferes | Use `LIKE CONCAT('%', {{search}}, '%')` |

---

## Field Filters

### What Makes Field Filters Special

- Generates an entire WHERE clause (not just a value)
- Connects to Metabase's filter widget (date pickers, dropdown lists)
- Supports "between", "is", "is not", relative dates
- Maps to a specific database column

### Field Filter Syntax

```sql
-- Field filter replaces entire WHERE condition
SELECT
  DATE_TRUNC('day', created_at) AS order_date,
  COUNT(*) AS order_count,
  SUM(amount) AS total_revenue
FROM orders
WHERE {{created_at_filter}}
GROUP BY 1
ORDER BY 1
```

### Field Filter Configuration

```
Click the variable tag → Set type to "Field Filter"
├── Database: your_database
├── Table: orders
├── Column: created_at
└── Widget type: Date (auto-selected for date columns)
```

### Field Filter on Non-Date Columns

```sql
-- Field filter on a category column
SELECT *
FROM orders
WHERE {{status_filter}}

-- Configure: Field Filter → orders → status
-- Widget: dropdown with auto-populated values
```

### Field Filter Limitations

| Limitation | Workaround |
|-----------|------------|
| Only works with a single table column | Use regular variables for cross-table filters |
| Cannot use inside CTEs directly | Filter in final SELECT, or use subquery |
| Cannot combine with other conditions on same column | Use regular variables instead |
| Must map to exact column in database | Create view if column name differs |

### Field Filter in CTE Workaround

```sql
-- WRONG: field filter in CTE (will fail)
-- WITH filtered AS (
--   SELECT * FROM orders WHERE {{date_filter}}
-- )

-- CORRECT: filter in final query or use subquery
SELECT
  o.order_id,
  o.amount,
  c.name
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE {{date_filter}}  -- field filter on orders.created_at
```

---

## SQL Snippets

### Creating Snippets

```
Native query editor → Snippet icon (or type {{snippet:)
→ Create new snippet
→ Name: "active_orders_cte"
→ Content: (SQL below)
```

### Snippet Examples

```sql
-- Snippet: "active_orders_cte"
active_orders AS (
  SELECT *
  FROM orders
  WHERE status IN ('completed', 'processing')
    AND is_test = false
    AND created_at >= '2025-01-01'
)

-- Usage in any question:
WITH {{snippet: active_orders_cte}}
SELECT
  DATE_TRUNC('month', created_at) AS month,
  COUNT(*) AS order_count
FROM active_orders
GROUP BY 1
```

```sql
-- Snippet: "standard_exclusions"
AND is_test = false AND is_internal = false AND status != 'cancelled'
-- Usage: SELECT * FROM orders WHERE created_at >= {{start_date}} {{snippet: standard_exclusions}}

-- Snippet: "revenue_calculation"
SUM(CASE WHEN status = 'completed' THEN amount - COALESCE(refund_amount, 0) ELSE 0 END)
-- Usage: SELECT region, {{snippet: revenue_calculation}} AS net_revenue FROM orders GROUP BY 1
```

### Snippet Best Practices

| Practice | Reason |
|----------|--------|
| Name with clear prefix: `cte_`, `calc_`, `filter_` | Discoverability |
| Document what the snippet does in a comment | Maintainability |
| Keep snippets small and focused | Reusability |
| Use snippets for shared business logic | Consistency across questions |
| Review snippets quarterly | Prevent drift from business rules |

---

## Saved Question Reuse (Card References)

### Syntax

```sql
-- Reference a saved question by ID
SELECT
  region,
  COUNT(*) AS customer_count
FROM {{#42}}  -- saved question #42 as subquery
GROUP BY 1

-- Metabase wraps saved question as:
-- (SELECT ... FROM ... WHERE ...) AS question_42
```

### Use Cases

- **Use when**: Reusing a complex filtered dataset across multiple analyses
- **Use when**: Non-SQL users built a question in the GUI that SQL users want to extend
- **Avoid when**: Performance-critical queries (adds subquery overhead)

### Gotchas with Card References

| Issue | Cause | Fix |
|-------|-------|-----|
| Slow performance | Subquery not optimized | Rewrite as CTE or materialized view |
| Column names change | Someone edited the saved question | Pin column aliases in the saved question |
| Circular reference | Question A references B which references A | Restructure to avoid cycles |
| Cannot use in CTE | Metabase limitation | Use as subquery in FROM clause |

---

## Result Caching Configuration

### Cache Settings

```
Admin → Settings → Caching
├── Saved question cache duration: 300 seconds (default)
├── Cache strategy: TTL | Schedule | Adaptive
├── Minimum query duration to cache: 1000ms
└── Max cache entry size: 100MB (default)
```

### Per-Question Cache Override

```
Question → Info → Caching
├── Use default: inherits global setting
├── Custom TTL: set specific duration
├── Schedule: cache refreshes at specific times
└── Don't cache: always run fresh
```

### Cache Strategy Decision

| Strategy | Use When | Setting |
|----------|----------|---------|
| TTL (time-to-live) | Data updates on known schedule | Duration = pipeline interval |
| Schedule | Dashboard must be fresh by 9 AM | Schedule = daily at 8:30 AM |
| Adaptive | Variable update frequency | Metabase auto-adjusts |
| No cache | Real-time data required | Disable per question |

### Cache Monitoring

```sql
-- Check cache hit rate (Metabase application database)
SELECT
  DATE_TRUNC('day', started_at) AS day,
  COUNT(*) AS total_queries,
  COUNT(CASE WHEN cache_hit THEN 1 END) AS cache_hits,
  ROUND(100.0 * COUNT(CASE WHEN cache_hit THEN 1 END) / COUNT(*), 1) AS hit_rate_pct
FROM query_execution
WHERE started_at > NOW() - INTERVAL '7 days'
GROUP BY 1
ORDER BY 1;
```

---

## Query Performance in Metabase

### Performance Checklist

- [ ] Check `query_execution` table for slow queries (>10s)
- [ ] Add database indexes for columns used in field filters
- [ ] Use materialized views for complex aggregations
- [ ] Enable caching for dashboards viewed frequently
- [ ] Limit result rows (Metabase caps at 2000 for display, 1M for download)
- [ ] Avoid SELECT * — select only needed columns
- [ ] Use date range filters to limit scanned data

### Identifying Slow Queries

```sql
-- Top 10 slowest queries in last 7 days (Metabase application DB)
SELECT card_id, card_name,
  ROUND(AVG(running_time) / 1000.0, 2) AS avg_seconds,
  COUNT(*) AS execution_count
FROM query_execution
WHERE started_at > NOW() - INTERVAL '7 days' AND card_id IS NOT NULL
GROUP BY card_id, card_name ORDER BY avg_seconds DESC LIMIT 10;
```

---

## Common Metabase SQL Patterns

### Pattern: Date Spine with Metrics

- Generate date spine with `generate_series` (PG) or recursive CTE (MySQL)
- LEFT JOIN daily aggregations onto spine
- COALESCE nulls to 0 for days with no data

### Pattern: Running Total

- Use window function: `SUM(SUM(amount)) OVER (ORDER BY month)` for cumulative
- Combine with `DATE_TRUNC` for monthly/weekly granularity

### Pattern: Top N with "Other"

```sql
WITH ranked AS (
  SELECT category, SUM(amount) AS revenue,
    ROW_NUMBER() OVER (ORDER BY SUM(amount) DESC) AS rn
  FROM orders WHERE {{created_at_filter}} GROUP BY 1
)
SELECT CASE WHEN rn <= 10 THEN category ELSE 'Other' END AS category,
  SUM(revenue) AS revenue
FROM ranked GROUP BY 1 ORDER BY SUM(revenue) DESC
```

---

## Common Gotchas

| Gotcha | Symptom | Fix |
|--------|---------|-----|
| Timezone mismatch | Counts differ from other tools | Use `AT TIME ZONE` or `::date` casts |
| Field filter in CTE | Error: "invalid syntax" | Move field filter to final WHERE clause |
| Variable in ORDER BY | Error or unexpected behavior | Use column position: `ORDER BY 1` |
| Text variable with apostrophe | SQL injection / syntax error | Metabase parameterizes; use prepared statements |
| Empty optional variable | Query returns nothing | Wrap in `[[ ]]` for optional clause |
| Snippet in wrong position | Syntax error | Ensure snippet content matches context (CTE vs WHERE) |
| `LIMIT` in saved question reference | Subquery truncates data | Remove LIMIT from referenced question |
| JSON columns | Cannot use field filters on JSON | Extract to typed column or use regular variable |
| `generate_series` not available | MySQL or non-PostgreSQL database | Use recursive CTE or calendar table |

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Hardcoded dates in SQL | Dashboards go stale | Use date variables or field filters |
| Business logic duplicated across questions | Inconsistency, maintenance burden | Use snippets or saved question references |
| SELECT * in native queries | Slow performance, unnecessary data | Select only needed columns |
| No caching on frequently viewed dashboards | Unnecessary load on database | Enable caching aligned with data freshness |
| Complex SQL instead of query builder | Non-SQL users cannot modify | Use GUI builder when possible; native SQL for complex only |
| Snippet used once | Unnecessary indirection | Inline the SQL; use snippets only for reuse |
| No comments in complex queries | Hard to maintain | Add SQL comments for business logic |
| Ignoring Metabase query execution log | Performance issues go unnoticed | Review slow queries weekly |

---

## Cross-References

- `permissions-collections.md` — Who can run native queries
- `embedding-integration.md` — Parameter passing in embedded queries
- `partition-strategies.md` — Table partitioning for query performance
- `monitoring-alerting-patterns.md` — Database monitoring for query performance

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
