# Data Quality Patterns for Lake Platforms

> Purpose: Operational reference for implementing data quality across data lake architectures — testing strategies, anomaly detection, SLO definition, automated remediation, and observability dashboards. Freshness anchor: Q1 2026.

---

## Decision Tree: Choosing a Data Quality Approach

```
START: What level of data quality automation do you need?
│
├─ Basic: Schema validation + freshness checks
│   └─ dbt tests + source freshness (free, dbt-native)
│
├─ Intermediate: Anomaly detection + quality dashboards
│   │
│   ├─ Using dbt? → Elementary (open core, dbt-native)
│   │
│   └─ Not using dbt? → Great Expectations or Soda Core
│
├─ Advanced: ML-powered anomaly detection + automated remediation
│   │
│   ├─ Budget for SaaS? → Monte Carlo or Bigeye
│   │
│   └─ Open-source preferred? → Elementary + custom alerting
│
└─ Enterprise: End-to-end observability + compliance
    └─ Monte Carlo + catalog integration (Atlan/DataHub)
```

---

## Quick Reference: Data Quality Dimensions

| Dimension | What It Measures | Test Type | Example Check |
|-----------|-----------------|-----------|---------------|
| Completeness | Missing values | not_null, row_count | `order_id IS NOT NULL` |
| Uniqueness | Duplicate records | unique, distinct_count | `COUNT(order_id) = COUNT(DISTINCT order_id)` |
| Freshness | Data recency | timestamp comparison | `MAX(created_at) > NOW() - INTERVAL '4 hours'` |
| Volume | Expected row counts | row_count_range | `1000 < COUNT(*) < 1000000` |
| Validity | Values in expected range | accepted_values, range | `status IN ('active', 'inactive')` |
| Consistency | Cross-table agreement | referential_integrity | `customer_id EXISTS IN dim_customers` |
| Accuracy | Matches source of truth | reconciliation | `SUM(amount) matches finance system` |
| Distribution | Statistical properties | mean, stddev, percentile | `AVG(amount) BETWEEN 20 AND 200` |

---

## Great Expectations Integration

### Setup for Data Lake

```python
# great_expectations/datasources/lake_config.py
import great_expectations as gx

context = gx.get_context()

# S3/Delta Lake datasource
datasource = context.sources.add_spark(
    name="delta_lake",
    spark_config={
        "spark.sql.extensions": "io.delta.sql.DeltaSparkSessionExtension",
        "spark.sql.catalog.spark_catalog": "org.apache.spark.sql.delta.catalog.DeltaCatalog"
    }
)

# Add data asset
data_asset = datasource.add_dataframe_asset(name="fct_orders")
```

### Expectation Suite for Lake Tables

```python
# great_expectations/expectations/lake_orders_suite.py
suite = context.add_expectation_suite("lake_orders_suite")

# Completeness
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="order_id", mostly=1.0
    )
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(
        column="customer_id", mostly=0.99
    )
)

# Uniqueness
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeUnique(column="order_id")
)

# Volume
suite.add_expectation(
    gx.expectations.ExpectTableRowCountToBeBetween(
        min_value=1000, max_value=10000000
    )
)

# Validity
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="status",
        value_set=["pending", "completed", "cancelled", "refunded"]
    )
)

# Distribution
suite.add_expectation(
    gx.expectations.ExpectColumnMeanToBeBetween(
        column="amount", min_value=10, max_value=500
    )
)

# Freshness (custom)
suite.add_expectation(
    gx.expectations.ExpectColumnMaxToBeBetween(
        column="created_at",
        min_value={"$PARAMETER": "now() - interval 4 hours"}
    )
)
```

---

## dbt Test Strategies for Lakes

### Layer-Specific Testing

| Layer | Tests | Purpose |
|-------|-------|---------|
| Source | freshness, row_count, schema | Detect ingestion issues early |
| Staging | not_null, unique, accepted_values | Validate cleansing logic |
| Intermediate | referential_integrity, row_count | Validate join logic |
| Mart | all above + business rules + anomaly | Full quality assurance |

### Source Quality Gate

```yaml
# models/staging/sources.yml
sources:
  - name: raw_lake
    database: raw
    schema: delta_tables
    freshness:
      warn_after: {count: 4, period: hour}
      error_after: {count: 8, period: hour}
    loaded_at_field: _ingested_at
    tables:
      - name: orders
        columns:
          - name: order_id
            tests:
              - not_null
              - unique
          - name: amount
            tests:
              - not_null
      - name: customers
        freshness:
          warn_after: {count: 24, period: hour}
          error_after: {count: 48, period: hour}
```

---

## Anomaly Detection for Pipelines

### Volume Anomaly Detection

```sql
-- monitors/volume_anomaly.sql
WITH daily_volumes AS (
  SELECT
    DATE_TRUNC('day', created_at) AS load_date,
    COUNT(*) AS row_count
  FROM analytics.fct_orders
  WHERE created_at >= CURRENT_DATE - INTERVAL '60 days'
  GROUP BY 1
),
stats AS (
  SELECT
    AVG(row_count) AS mean_count,
    STDDEV(row_count) AS stddev_count
  FROM daily_volumes
  WHERE load_date < CURRENT_DATE  -- training window
),
today AS (
  SELECT row_count
  FROM daily_volumes
  WHERE load_date = CURRENT_DATE
)
SELECT
  today.row_count,
  stats.mean_count,
  stats.stddev_count,
  ABS(today.row_count - stats.mean_count) / NULLIF(stats.stddev_count, 0) AS z_score
FROM today, stats
WHERE ABS(today.row_count - stats.mean_count) / NULLIF(stats.stddev_count, 0) > 3
```

### Schema Change Detection

```python
# monitors/schema_drift.py
def detect_schema_drift(table_name: str, expected_schema: dict) -> list:
    """Compare current table schema against expected contract."""
    current = get_current_schema(table_name)
    issues = []

    # Removed columns
    for col in expected_schema:
        if col not in current:
            issues.append({
                "type": "column_removed",
                "column": col,
                "severity": "error"
            })

    # Added columns (informational)
    for col in current:
        if col not in expected_schema:
            issues.append({
                "type": "column_added",
                "column": col,
                "severity": "info"
            })

    # Type changes
    for col in expected_schema:
        if col in current and current[col]["type"] != expected_schema[col]["type"]:
            issues.append({
                "type": "type_changed",
                "column": col,
                "expected": expected_schema[col]["type"],
                "actual": current[col]["type"],
                "severity": "error"
            })

    return issues
```

### Distribution Shift Detection

- Compare 7-day rolling window against 30-day baseline
- Alert when mean Z-score > 2 or median percent change > 20%
- Use `PERCENTILE_CONT`, `AVG`, `STDDEV` for statistical comparison

---

## SLO Definition for Data Quality

### SLO Template

| Metric | Target | Measurement | Alert Threshold |
|--------|--------|-------------|-----------------|
| Freshness | <4 hours from source | `MAX(created_at)` vs `NOW()` | >2h warn, >4h error |
| Completeness | >99.5% non-null on required fields | `COUNT(non_null) / COUNT(*)` | <99.5% error |
| Uniqueness | 0 duplicates on primary keys | `COUNT(*) - COUNT(DISTINCT pk)` | >0 error |
| Volume | Within 3 sigma of 30-day average | Z-score of daily count | >3 sigma warn |
| Schema | 0 unexpected changes | Contract comparison | Any drift = error |
| Accuracy | <1% deviation from source of truth | Monthly reconciliation | >1% error |

### SLO Configuration

```yaml
# quality/slos/fct_orders_slo.yml
table: analytics.fct_orders
slos:
  freshness:
    column: created_at
    warn_threshold: 2h
    error_threshold: 4h
    check_frequency: 15m

  completeness:
    columns:
      - name: order_id
        target: 1.0
      - name: customer_id
        target: 0.995
      - name: amount
        target: 0.999
    check_frequency: 1h

  volume:
    method: z_score
    training_window: 30d
    sensitivity: 3
    check_frequency: 1h

  uniqueness:
    columns: [order_id]
    target: 1.0
    check_frequency: 1h
```

---

## Automated Remediation Workflows

### Remediation Decision Matrix

| Issue | Severity | Auto-Remediate? | Action |
|-------|----------|-----------------|--------|
| Late-arriving data | warn | No | Alert; wait for source |
| Duplicate records | error | Yes | Deduplicate using ROW_NUMBER |
| NULL in required field | error | Conditional | Default value if safe; else block pipeline |
| Volume drop >50% | error | No | Alert; manual investigation required |
| Schema column removed | error | No | Alert; block downstream |
| Schema column added | info | Yes | Add to schema contract |
| Distribution shift | warn | No | Alert; investigate root cause |

### Auto-Deduplication Pattern

```sql
-- Deduplicate using ROW_NUMBER, keeping most recently ingested row
CREATE OR REPLACE TABLE analytics.fct_orders AS
WITH deduped AS (
  SELECT *, ROW_NUMBER() OVER (PARTITION BY order_id ORDER BY _ingested_at DESC) AS rn
  FROM analytics.fct_orders_raw
)
SELECT * EXCEPT(rn) FROM deduped WHERE rn = 1
```

### Circuit Breaker Pattern

- Run quality checks before downstream processing
- On error: send alert, mark table unhealthy, block downstream
- On warn: send alert, allow downstream
- On pass: mark table healthy, allow downstream

---

## Data Observability Tools (2026)

| Tool | Approach | Best For | Pricing |
|------|----------|----------|---------|
| Elementary | dbt-native, open core | dbt shops, cost-conscious | Free / paid UI |
| Monte Carlo | ML-powered, SaaS | Enterprise, multi-warehouse | Enterprise |
| Bigeye | Metric-focused monitoring | Precision monitoring | SaaS |
| Soda Core | SQL-based checks | Multi-platform | Open core |
| Datafold | Diff-based testing | CI/CD regression | SaaS |
| Great Expectations | Python expectation suites | Spark/Python pipelines | Free |

---

## Quality Dashboard Components

### Essential Metrics

| Metric | Visualization | Update Frequency |
|--------|--------------|------------------|
| Tables passing all tests | Scorecard (%) | Real-time |
| Freshness status per table | Heatmap (green/yellow/red) | Every 15 min |
| Test failure trend | Time series | Daily |
| Volume anomalies | Sparkline per table | Hourly |
| SLO compliance | Gauge chart | Daily |
| Time to remediation | Bar chart | Weekly |
| Coverage (% tables with tests) | Progress bar | Weekly |

### Dashboard Data Sources

- Quality scorecard: `COUNT(pass) / COUNT(*) FROM quality.test_results`
- Freshness heatmap: compute `hours_stale` from `NOW() - max_timestamp`, bucket into green/yellow/red
- Volume sparklines: daily row counts per table from `quality.volume_monitor`

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Quality checks only at ingestion | Transformation bugs pass silently | Test every layer (source, staging, mart) |
| No SLOs defined | No objective measure of "good enough" | Define SLOs before building monitors |
| Alert on everything | Alert fatigue, real issues ignored | Tier alerts: error (page), warn (Slack), info (log) |
| Manual remediation only | Slow recovery, human bottleneck | Automate safe remediations (dedup, defaults) |
| Testing in dev, not in prod | Production anomalies go undetected | Run monitors on production data continuously |
| Single quality check frequency | Either too noisy or too slow | Adjust frequency per table criticality |
| No circuit breaker | Bad data propagates to dashboards | Quality gates block downstream on failure |
| Quality team owns all tests | Bottleneck, domain context lost | Domain teams own their quality tests |

---

## Cross-References

- `data-quality-testing.md` — dbt-specific testing patterns and coverage metrics
- `security-access-patterns.md` — PII detection as a quality dimension
- `monitoring-alerting-patterns.md` — Infrastructure monitoring alongside data quality
- `data-mesh-patterns.md` — Quality standards within data product specifications

---

*Last updated: 2026-02-10 | Next review: 2026-05-10*
