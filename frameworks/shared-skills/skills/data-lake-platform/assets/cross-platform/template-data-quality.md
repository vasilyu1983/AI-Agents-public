# Data Quality Template

## Overview

Data quality framework for validation at each layer of the data lake.

## Quality Dimensions

| Dimension | Definition | Example Check |
|-----------|------------|---------------|
| **Completeness** | No missing required values | `NOT NULL` constraints |
| **Uniqueness** | No duplicate records | Primary key uniqueness |
| **Validity** | Values within expected ranges | Email regex, date ranges |
| **Consistency** | Data matches across sources | Referential integrity |
| **Timeliness** | Data is fresh enough | Max age < SLA |
| **Accuracy** | Data reflects reality | Business rule validation |

---

## SQLMesh Audits

### Built-in Audits

```sql
-- models/staging/stg_orders.sql
MODEL (
  name silver.stg_orders,
  kind INCREMENTAL_BY_TIME_RANGE (time_column created_at),
  grain order_id,
  audits (
    -- Completeness
    not_null(columns=[order_id, customer_id, total_amount, created_at]),

    -- Uniqueness
    unique(columns=[order_id]),

    -- Validity
    accepted_values(column=status, values=['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']),

    -- Custom audit reference
    assert_positive_amounts
  )
);

SELECT
    order_id,
    customer_id,
    total_amount,
    status,
    created_at
FROM bronze.raw_orders
WHERE created_at BETWEEN @start_dt AND @end_dt;
```

### Custom Audits

```sql
-- audits/assert_positive_amounts.sql
AUDIT (
  name assert_positive_amounts,
  dialect clickhouse
);

-- Fails if any rows returned
SELECT *
FROM @this_model
WHERE total_amount < 0
   OR quantity < 0;
```

```sql
-- audits/assert_referential_integrity.sql
AUDIT (
  name assert_orders_have_customers,
  dialect clickhouse
);

SELECT o.*
FROM @this_model o
LEFT JOIN silver.stg_customers c ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL;
```

```sql
-- audits/assert_no_future_dates.sql
AUDIT (
  name assert_no_future_dates,
  dialect clickhouse
);

SELECT *
FROM @this_model
WHERE created_at > now() + INTERVAL 1 HOUR;
```

---

## Great Expectations

### Installation

```bash
pip install great-expectations
great_expectations init
```

### Expectation Suite

```python
# expectations/bronze_events_suite.py
import great_expectations as gx

context = gx.get_context()

# Create expectation suite
suite = context.add_expectation_suite("bronze_events")

# Add expectations
validator = context.get_validator(
    batch_request=batch_request,
    expectation_suite_name="bronze_events"
)

# Completeness
validator.expect_column_values_to_not_be_null("event_id")
validator.expect_column_values_to_not_be_null("user_id")
validator.expect_column_values_to_not_be_null("created_at")

# Uniqueness
validator.expect_column_values_to_be_unique("event_id")

# Validity
validator.expect_column_values_to_match_regex(
    "email",
    r"^[\w.-]+@[\w.-]+\.\w+$"
)
validator.expect_column_values_to_be_between(
    "amount",
    min_value=0,
    max_value=1000000
)
validator.expect_column_values_to_be_in_set(
    "status",
    ["pending", "active", "completed", "cancelled"]
)

# Consistency
validator.expect_column_pair_values_to_be_equal(
    "calculated_total",
    "sum_of_line_items"
)

# Save suite
validator.save_expectation_suite()
```

### Run Validation

```python
# validation/run_checks.py
import great_expectations as gx

context = gx.get_context()

# Run checkpoint
result = context.run_checkpoint(
    checkpoint_name="bronze_validation",
    batch_request={
        "datasource_name": "clickhouse",
        "data_asset_name": "bronze.raw_events"
    }
)

if not result.success:
    # Alert on failures
    failed_expectations = [
        r for r in result.run_results.values()
        if not r.success
    ]
    send_alert(failed_expectations)
```

---

## Soda Core

### Installation

```bash
pip install soda-core-duckdb  # or soda-core-clickhouse
```

### Configuration

```yaml
# soda/configuration.yml
data_source clickhouse:
  type: clickhouse
  host: localhost
  port: 8123
  database: analytics
  username: ${CLICKHOUSE_USER}
  password: ${CLICKHOUSE_PASSWORD}
```

### Check Definition

```yaml
# soda/checks/silver_orders.yml
checks for silver.stg_orders:
  # Freshness
  - freshness(created_at) < 24h

  # Row count
  - row_count > 0
  - row_count_change < 50%

  # Completeness
  - missing_count(order_id) = 0
  - missing_count(customer_id) = 0
  - missing_count(total_amount) = 0

  # Uniqueness
  - duplicate_count(order_id) = 0

  # Validity
  - invalid_count(email) = 0:
      valid regex: '^[\w.-]+@[\w.-]+\.\w+$'

  - invalid_count(status) = 0:
      valid values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']

  - min(total_amount) >= 0
  - max(total_amount) < 1000000

  # Consistency
  - values in (customer_id) must exist in silver.stg_customers (customer_id)

  # Schema
  - schema:
      fail:
        when required column missing: [order_id, customer_id, total_amount, status, created_at]
```

### Run Checks

```bash
soda scan -d clickhouse -c soda/configuration.yml soda/checks/silver_orders.yml
```

---

## ClickHouse Quality Checks

### Inline Quality Metrics

```sql
-- Create quality metrics table
CREATE TABLE meta.data_quality_results (
    check_time DateTime DEFAULT now(),
    table_name String,
    check_name String,
    check_type String,
    passed UInt8,
    failed_count UInt64,
    details String
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(check_time)
ORDER BY (check_time, table_name, check_name);

-- Run quality checks
INSERT INTO meta.data_quality_results
SELECT
    now() AS check_time,
    'silver.stg_orders' AS table_name,
    'null_order_id' AS check_name,
    'completeness' AS check_type,
    countIf(order_id IS NULL) = 0 AS passed,
    countIf(order_id IS NULL) AS failed_count,
    '' AS details
FROM silver.stg_orders
WHERE created_at >= today() - 1;
```

### Quality Dashboard Query

```sql
-- Quality summary by table
SELECT
    table_name,
    check_type,
    countIf(passed = 1) AS checks_passed,
    countIf(passed = 0) AS checks_failed,
    round(countIf(passed = 1) * 100.0 / count(), 2) AS pass_rate
FROM meta.data_quality_results
WHERE check_time >= today() - 7
GROUP BY table_name, check_type
ORDER BY table_name, check_type;

-- Recent failures
SELECT
    check_time,
    table_name,
    check_name,
    failed_count,
    details
FROM meta.data_quality_results
WHERE passed = 0
  AND check_time >= today() - 1
ORDER BY check_time DESC;
```

---

## Data Contracts

### Contract Definition

```yaml
# contracts/orders_contract.yaml
contract:
  name: orders_v1
  version: "1.0.0"
  owner: data-team@company.com

schema:
  - name: order_id
    type: String
    required: true
    unique: true

  - name: customer_id
    type: UInt64
    required: true
    foreign_key: customers.customer_id

  - name: total_amount
    type: Decimal(18,2)
    required: true
    constraints:
      - min: 0
      - max: 1000000

  - name: status
    type: String
    required: true
    allowed_values:
      - pending
      - confirmed
      - shipped
      - delivered
      - cancelled

  - name: created_at
    type: DateTime
    required: true
    constraints:
      - max: now() + 1h

sla:
  freshness: 24h
  completeness: 99.9%
  availability: 99.5%

alerts:
  - type: slack
    channel: "#data-quality"
    on: [schema_change, sla_breach, quality_failure]
```

### Contract Validation

```python
# contracts/validate.py
import yaml
from dataclasses import dataclass

@dataclass
class ContractViolation:
    contract: str
    field: str
    violation_type: str
    details: str

def validate_contract(table_name: str, contract_path: str) -> list[ContractViolation]:
    with open(contract_path) as f:
        contract = yaml.safe_load(f)

    violations = []

    for field in contract["schema"]:
        # Check required fields
        if field["required"]:
            null_count = query(f"SELECT count() FROM {table_name} WHERE {field['name']} IS NULL")
            if null_count > 0:
                violations.append(ContractViolation(
                    contract=contract["contract"]["name"],
                    field=field["name"],
                    violation_type="completeness",
                    details=f"{null_count} null values"
                ))

        # Check constraints
        if "constraints" in field:
            for constraint in field["constraints"]:
                # Validate each constraint type
                pass

    return violations
```

---

## Alerting Integration

### Slack Alerts

```python
# monitoring/alerts.py
import requests

def send_quality_alert(check_results: list, webhook_url: str):
    failures = [r for r in check_results if not r["passed"]]

    if not failures:
        return

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "🚨 Data Quality Alert"}
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{len(failures)} checks failed*"
            }
        }
    ]

    for failure in failures[:5]:  # Limit to 5
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"• *{failure['table']}*: {failure['check']} - {failure['count']} failures"
            }
        })

    requests.post(webhook_url, json={"blocks": blocks})
```

---

## Best Practices

1. **Validate at boundaries**: Check data when entering each layer
2. **Fail fast**: Stop pipelines on critical quality issues
3. **Track trends**: Monitor quality metrics over time
4. **Document expectations**: Use data contracts for critical tables
5. **Alert appropriately**: Critical issues → PagerDuty; warnings → Slack
6. **Root cause analysis**: Track why quality issues occur
