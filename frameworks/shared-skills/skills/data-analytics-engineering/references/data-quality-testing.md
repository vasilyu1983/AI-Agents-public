# Data Quality Testing for Analytics Pipelines

> Purpose: Operational reference for implementing automated data quality testing across analytics pipelines — dbt tests, Great Expectations, anomaly detection, and coverage metrics. Freshness anchor: Q1 2026.

---

## Decision Tree: Choosing a Testing Approach

```
START: What is your transformation layer?
│
├─ dbt
│   │
│   ├─ Need basic schema validation?
│   │   └─ YES → dbt built-in tests (not_null, unique, accepted_values, relationships)
│   │
│   ├─ Need statistical or complex tests?
│   │   └─ YES → dbt-expectations package
│   │
│   ├─ Need anomaly detection over time?
│   │   └─ YES → Elementary anomaly monitors
│   │
│   └─ Need cross-database or source validation?
│       └─ YES → dbt + Great Expectations via external tests
│
├─ Spark / Python pipelines
│   └─ Great Expectations or Soda Core
│
└─ Warehouse-native (no orchestrator)
    └─ Scheduled SQL checks + alerting (Monte Carlo, Datafold)
```

---

## Quick Reference: Testing Tool Comparison (2026)

| Tool | Integration | Test Types | Anomaly Detection | Cost |
|------|-------------|-----------|-------------------|------|
| dbt tests (built-in) | Native dbt | Schema, custom SQL | No | Free |
| dbt-expectations | dbt package | Statistical, regex, distribution | Limited | Free |
| Elementary | dbt package + UI | Anomaly, schema, freshness | Yes (built-in) | Open core |
| Great Expectations | Python, Spark, SQL | 300+ expectation types | Via profiling | Free |
| Soda Core | Python, dbt, Spark | SQL-based checks | Basic | Open core |
| Monte Carlo | SaaS, warehouse-native | ML anomaly detection | Yes (automated) | Enterprise |
| Datafold | CI/CD, dbt | Diff testing, regression | Column-level | SaaS |

---

## dbt Built-In Tests

### Schema Tests (YAML-configured)

```yaml
# models/staging/stg_orders.yml
models:
  - name: stg_orders
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'completed', 'cancelled', 'refunded']
      - name: customer_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_customers')
              field: customer_id
      - name: amount
        tests:
          - not_null
      - name: created_at
        tests:
          - not_null
```

### Custom Data Tests (SQL)

```sql
-- tests/assert_revenue_not_negative.sql
-- Fails if any completed order has negative revenue
SELECT
  order_id,
  amount
FROM {{ ref('fct_orders') }}
WHERE status = 'completed'
  AND amount < 0
```

```sql
-- tests/assert_daily_order_volume.sql
-- Fails if any day has zero orders (data gap detection)
WITH date_spine AS (
  SELECT date_day
  FROM {{ ref('dim_dates') }}
  WHERE date_day >= '2025-01-01'
    AND date_day < CURRENT_DATE
),
daily_orders AS (
  SELECT
    DATE_TRUNC('day', created_at) AS order_date,
    COUNT(*) AS order_count
  FROM {{ ref('fct_orders') }}
  GROUP BY 1
)
SELECT d.date_day
FROM date_spine d
LEFT JOIN daily_orders o ON d.date_day = o.order_date
WHERE o.order_count IS NULL
  AND EXTRACT(DOW FROM d.date_day) NOT IN (0, 6) -- exclude weekends if applicable
```

### Test Severity Configuration

```yaml
models:
  - name: fct_orders
    columns:
      - name: order_id
        tests:
          - unique:
              severity: error  # blocks pipeline
          - not_null:
              severity: error
      - name: discount_code
        tests:
          - not_null:
              severity: warn  # logs warning, pipeline continues
```

---

## dbt-expectations Package

### Installation

```yaml
# packages.yml
packages:
  - package: calogica/dbt_expectations
    version: [">=0.10.0", "<0.12.0"]
```

### Common Expectations

```yaml
models:
  - name: fct_orders
    tests:
      # Row count within expected range
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 1000
          max_value: 1000000

      # No duplicate compound keys
      - dbt_expectations.expect_compound_columns_to_be_unique:
          column_list: ["order_id", "line_item_id"]

    columns:
      - name: email
        tests:
          # Regex pattern match
          - dbt_expectations.expect_column_values_to_match_regex:
              regex: "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"

      - name: amount
        tests:
          # Value range check
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
              max_value: 100000
              mostly: 0.99  # 99% of values must pass

          # Distribution check
          - dbt_expectations.expect_column_mean_to_be_between:
              min_value: 20
              max_value: 200

      - name: created_at
        tests:
          # Freshness check
          - dbt_expectations.expect_row_values_to_have_recent_data:
              datepart: day
              interval: 1
```

---

## Elementary Anomaly Detection

### Installation and Setup

```yaml
# packages.yml
packages:
  - package: elementary-data/elementary
    version: [">=0.14.0", "<0.16.0"]
```

### Anomaly Monitor Configuration

```yaml
models:
  - name: fct_orders
    tests:
      # Volume anomaly — detect unusual row count changes
      - elementary.volume_anomaly:
          timestamp_column: created_at
          time_bucket:
            period: day
            count: 1
          training_period:
            period: day
            count: 30
          sensitivity: 3  # standard deviations

      # Freshness anomaly — detect late-arriving data
      - elementary.freshness_anomaly:
          timestamp_column: created_at
          sensitivity: 3

    columns:
      - name: amount
        tests:
          # Column-level anomaly
          - elementary.column_anomalies:
              timestamp_column: created_at
              column_anomalies:
                - zero_count
                - null_count
                - average
                - standard_deviation

      - name: status
        tests:
          # Distribution shift detection
          - elementary.all_columns_anomalies:
              timestamp_column: created_at
```

---

## Great Expectations Integration

### Use When

- Python/Spark pipelines (non-dbt)
- Need profiling-driven test generation
- Cross-database validation required
- Complex statistical tests beyond dbt capabilities

### Checkpoint Configuration

```yaml
# great_expectations/checkpoints/orders_checkpoint.yml
name: orders_checkpoint
config_version: 1.0
class_name: Checkpoint
run_name_template: "orders_validation_%Y%m%d"
validations:
  - batch_request:
      datasource_name: warehouse
      data_asset_name: fct_orders
    expectation_suite_name: orders_suite
    action_list:
      - name: store_validation_result
        action:
          class_name: StoreValidationResultAction
      - name: send_slack_notification
        action:
          class_name: SlackNotificationAction
          slack_webhook: ${SLACK_WEBHOOK}
          notify_on: failure
```

### Common Expectations

```python
suite = context.add_expectation_suite("orders_suite")
suite.add_expectation(gx.expectations.ExpectTableRowCountToBeBetween(min_value=1000))
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="order_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="order_id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(
    column="amount", min_value=0, max_value=100000, mostly=0.99))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeInSet(
    column="status", value_set=["pending", "completed", "cancelled", "refunded"]))
```

---

## Freshness Monitoring

### dbt Source Freshness

```yaml
# models/staging/sources.yml
sources:
  - name: raw_orders
    database: raw
    schema: ecommerce
    freshness:
      warn_after: {count: 6, period: hour}
      error_after: {count: 12, period: hour}
    loaded_at_field: _loaded_at
    tables:
      - name: orders
        freshness:
          warn_after: {count: 2, period: hour}
          error_after: {count: 4, period: hour}
      - name: order_items
      - name: customers
        freshness:
          warn_after: {count: 24, period: hour}
          error_after: {count: 48, period: hour}
```

```bash
# Run freshness check
dbt source freshness --select source:raw_orders
```

---

## Test Coverage Metrics

### Coverage Targets

| Layer | Minimum Coverage | Recommended | Critical Tests |
|-------|-----------------|-------------|----------------|
| Staging (stg_) | 80% of columns | 100% of columns | not_null, unique on PKs |
| Intermediate (int_) | 50% of models | 80% of models | Row count, join integrity |
| Mart (fct_, dim_) | 100% of models | 100% of columns | All schema + custom business rules |
| Metrics | 100% | 100% | Output validation vs known values |

### CI/CD Integration Checklist

- [ ] Run `dbt test` on every PR that modifies models
- [ ] Fail CI if test coverage drops below threshold
- [ ] Run `dbt source freshness` in scheduled pipeline
- [ ] Post test results to Slack/Teams on failure
- [ ] Store test history for trend analysis
- [ ] Run anomaly monitors on schedule (not just on PR)
- [ ] Include data diff (Datafold) for mart-layer changes

---

## Test-Driven Analytics Development

### Workflow

1. Write failing test (expected behavior of new model)
2. Build model to pass the test
3. Add edge case tests
4. Validate against stakeholder expectations
5. Deploy with full test suite

### Example: TDD for Revenue Metric

- Step 1: Write tests FIRST — `not_null`, `row_count > 0`, `values_between min:0`, `recent_data`
- Step 2: Build model to pass the tests
- Step 3: Add edge case tests (zero revenue days, refunds exceeding orders)
- Step 4: Validate against stakeholder expectations
- Step 5: Deploy with full test suite

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Tests only on staging models | Business logic errors in marts go undetected | Test every layer, especially marts |
| All tests set to `severity: error` | Minor issues block entire pipeline | Use `warn` for non-critical, `error` for data integrity |
| No freshness monitoring | Stale data served without anyone knowing | Add source freshness checks + alerting |
| Hard-coded thresholds for anomalies | Thresholds break as data grows | Use statistical anomaly detection (Elementary) |
| Tests only in CI, never scheduled | Anomalies between deployments are missed | Run scheduled test suites on production |
| No test for row count changes | Silent data loss goes unnoticed | Add volume anomaly tests on every mart table |
| Testing only happy path | Edge cases cause production failures | Add tests for NULLs, zeros, duplicates, future dates |
| Ignoring test failures as noise | Real issues get buried | Fix or remove flaky tests immediately |

---

## Cross-References

- `semantic-layer-patterns.md` — Semantic models depend on tested upstream models
- `metric-governance.md` — Metric validation tests and certification process
- `data-quality-patterns.md` — Broader data quality framework for lake platforms
- `monitoring-alerting-patterns.md` — Alerting infrastructure for test failures

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
