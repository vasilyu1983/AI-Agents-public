# SQL Transformation Patterns

## Tool Selection (SQLMesh vs dbt)

Prefer a single transformation framework per platform and standardize conventions (project layout, naming, environments, test policy).

| Criterion | SQLMesh | dbt | Notes |
|----------|---------|-----|------|
| Environments/promotions | Strong | Strong | Both support dev/stage/prod patterns (implementation differs) |
| Change planning | Plan/apply workflow | Run-first by default | If you need explicit review gates, plan/apply is a good fit |
| Testing and quality gates | Audits/tests | Tests/exposures | Either can enforce contracts; pick one and make it mandatory |
| Macros/templating | SQL-first with compiler | Jinja macros widely used | Prefer minimal templating; keep logic in SQL where possible |
| Ecosystem/packages | Smaller | Larger | dbt has broader community packages; SQLMesh is more framework-complete out of the box |
| Semantic layer/metrics | Emerging/depends | First-class option | If metrics governance is a requirement, validate tooling up front |

---

## Semantic Layers (2026 Baseline)

Semantic layers are becoming first-class citizens in transformation tools, enabling:

- **LLM-based querying** — Natural language to SQL
- **Consistent metrics** — Single source of truth for business definitions
- **Governance** — Controlled access to curated data products

### dbt Semantic Layer

```yaml
# models/semantic/metrics.yml
semantic_models:
  - name: orders
    defaults:
      agg_time_dimension: order_date
    entities:
      - name: order_id
        type: primary
      - name: customer_id
        type: foreign
    measures:
      - name: order_total
        agg: sum
        expr: amount
      - name: order_count
        agg: count
        expr: order_id
    dimensions:
      - name: order_date
        type: time
      - name: status
        type: categorical

metrics:
  - name: revenue
    type: simple
    type_params:
      measure: order_total
  - name: average_order_value
    type: derived
    type_params:
      expr: revenue / order_count
```

### Cube.js (Alternative)

```javascript
// cube.js semantic layer
cube(`Orders`, {
  sql: `SELECT * FROM orders`,

  measures: {
    count: { type: `count` },
    totalRevenue: { sql: `amount`, type: `sum` },
    averageOrderValue: {
      sql: `${totalRevenue} / ${count}`,
      type: `number`
    }
  },

  dimensions: {
    status: { sql: `status`, type: `string` },
    createdAt: { sql: `created_at`, type: `time` }
  }
});
```

---

## SQLMesh Patterns

### Project Structure

```text
my_project/
├── sqlmesh.yaml           # Configuration
├── models/
│   ├── staging/           # Bronze → Silver
│   │   ├── stg_users.sql
│   │   └── stg_orders.sql
│   ├── intermediate/      # Silver transformations
│   │   └── int_order_items.sql
│   └── marts/             # Gold layer
│       ├── fct_orders.sql
│       └── dim_users.sql
├── macros/
│   └── utils.sql
├── audits/                # Data quality tests
│   └── assert_positive_amounts.sql
└── tests/                 # Unit tests
    └── test_order_total.yaml
```

### Model Types

```sql
-- models/staging/stg_orders.sql
MODEL (
  name staging.stg_orders,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column created_at,
    batch_size 1,
    batch_concurrency 2
  ),
  cron '@daily',
  grain order_id
);

SELECT
    order_id,
    customer_id,
    total_amount,
    status,
    created_at,
    updated_at
FROM raw.orders
WHERE created_at BETWEEN @start_dt AND @end_dt;
```

```sql
-- models/marts/fct_orders.sql
MODEL (
  name marts.fct_orders,
  kind FULL,
  cron '@daily',
  grain order_id,
  audits (
    assert_positive_amounts,
    not_null(columns=[order_id, customer_id])
  )
);

SELECT
    o.order_id,
    o.customer_id,
    u.user_segment,
    o.total_amount,
    o.status,
    o.created_at
FROM staging.stg_orders o
JOIN marts.dim_users u ON o.customer_id = u.user_id;
```

### Incremental Strategies

```sql
-- INCREMENTAL_BY_TIME_RANGE: Best for time-series
MODEL (
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column created_at
  )
);

-- INCREMENTAL_BY_UNIQUE_KEY: Best for SCD Type 1
MODEL (
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key [user_id]
  )
);

-- SCD_TYPE_2: Best for historical tracking
MODEL (
  kind SCD_TYPE_2 (
    unique_key [user_id],
    valid_from_name valid_from,
    valid_to_name valid_to
  )
);
```

### Plan and Apply Workflow

```bash
# Preview changes (dry run)
sqlmesh plan

# Apply to development environment
sqlmesh plan dev

# Apply to production
sqlmesh plan prod --no-prompts

# Run specific model
sqlmesh run --model marts.fct_orders
```

---

## dbt Patterns

### Project Structure

```text
my_project/
├── dbt_project.yml
├── models/
│   ├── staging/
│   │   ├── _staging__models.yml
│   │   └── stg_orders.sql
│   ├── intermediate/
│   │   └── int_order_items.sql
│   └── marts/
│       ├── _marts__models.yml
│       └── fct_orders.sql
├── macros/
│   └── utils.sql
├── tests/
│   └── assert_positive_amounts.sql
└── seeds/
    └── country_codes.csv
```

### Model Configuration

```sql
-- models/staging/stg_orders.sql
{{
    config(
        materialized='incremental',
        unique_key='order_id',
        incremental_strategy='merge',
        partition_by={
            'field': 'created_at',
            'data_type': 'timestamp',
            'granularity': 'day'
        }
    )
}}

SELECT
    order_id,
    customer_id,
    total_amount,
    status,
    created_at,
    updated_at
FROM {{ source('raw', 'orders') }}

{% if is_incremental() %}
WHERE updated_at > (SELECT max(updated_at) FROM {{ this }})
{% endif %}
```

### Schema Tests

```yaml
# models/marts/_marts__models.yml
version: 2

models:
  - name: fct_orders
    description: "Fact table for orders"
    columns:
      - name: order_id
        description: "Primary key"
        tests:
          - unique
          - not_null
      - name: total_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
      - name: status
        tests:
          - accepted_values:
              values: ['pending', 'confirmed', 'shipped', 'delivered', 'cancelled']
```

---

## Medallion Layer Patterns

### Bronze (Raw Staging)

```sql
-- Keep raw data with minimal transformation
MODEL (name staging.stg_raw_events, kind FULL);

SELECT
    _dlt_load_id,
    _dlt_id,
    event_id,
    raw_payload,  -- Keep original JSON
    CAST(created_at AS TIMESTAMP) AS created_at,
    current_timestamp() AS _loaded_at
FROM raw.events;
```

### Silver (Cleaned)

```sql
-- Parse, validate, deduplicate
MODEL (
  name intermediate.int_events,
  kind INCREMENTAL_BY_UNIQUE_KEY (unique_key [event_id])
);

SELECT
    event_id,
    user_id,
    event_type,
    JSON_EXTRACT_STRING(raw_payload, '$.properties') AS properties,
    created_at,
    _loaded_at
FROM staging.stg_raw_events
WHERE event_id IS NOT NULL
  AND created_at IS NOT NULL
QUALIFY ROW_NUMBER() OVER (PARTITION BY event_id ORDER BY _loaded_at DESC) = 1;
```

### Gold (Business-Ready)

```sql
-- Aggregate for business use
MODEL (name marts.fct_daily_events, kind FULL, grain [date, event_type]);

SELECT
    DATE(created_at) AS date,
    event_type,
    COUNT(*) AS event_count,
    COUNT(DISTINCT user_id) AS unique_users,
    AVG(CAST(JSON_EXTRACT_STRING(properties, '$.duration') AS FLOAT)) AS avg_duration
FROM intermediate.int_events
GROUP BY 1, 2;
```

---

## Testing Patterns

### SQLMesh Unit Tests

```yaml
# tests/test_order_total.yaml
test_order_total_calculation:
  model: marts.fct_orders
  inputs:
    staging.stg_orders:
      - order_id: 1
        customer_id: 100
        total_amount: 99.99
        status: confirmed
        created_at: 2024-01-01
    marts.dim_users:
      - user_id: 100
        user_segment: premium
  expected:
    - order_id: 1
      customer_id: 100
      user_segment: premium
      total_amount: 99.99
      status: confirmed
```

### Data Quality Audits

```sql
-- audits/assert_positive_amounts.sql
AUDIT (
  name assert_positive_amounts,
  dialect clickhouse
);

SELECT * FROM @this_model
WHERE total_amount < 0;
-- Audit fails if any rows returned
```

---

## CI/CD Integration

### GitHub Actions (SQLMesh)

```yaml
name: SQLMesh CI

on:
  pull_request:
    paths: ['models/**', 'sqlmesh.yaml']

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install sqlmesh
      - run: sqlmesh plan --no-prompts --skip-tests
      - run: sqlmesh test
```

### GitHub Actions (dbt)

```yaml
name: dbt CI

on:
  pull_request:
    paths: ['models/**', 'dbt_project.yml']

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
      - run: pip install dbt-core dbt-clickhouse
      - run: dbt deps
      - run: dbt build --select state:modified+
```
