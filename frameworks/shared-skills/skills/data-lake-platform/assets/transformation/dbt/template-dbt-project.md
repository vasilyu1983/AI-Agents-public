# dbt Project Template

## Overview

Setting up a dbt project for SQL transformations.

## Project Structure

```text
my_project/
├── dbt_project.yml           # Project config
├── profiles.yml              # Connection profiles
├── packages.yml              # Dependencies
├── models/
│   ├── staging/              # Bronze → Silver
│   │   ├── _staging__models.yml
│   │   ├── _staging__sources.yml
│   │   └── stg_*.sql
│   ├── intermediate/         # Silver transformations
│   │   └── int_*.sql
│   └── marts/                # Gold layer
│       ├── _marts__models.yml
│       └── fct_*.sql, dim_*.sql
├── macros/
│   └── utils.sql
├── tests/
│   └── generic/
├── seeds/
│   └── static_data.csv
└── snapshots/
    └── scd_type_2.sql
```

---

## Configuration

### dbt_project.yml

```yaml
name: 'analytics'
version: '1.0.0'

profile: 'analytics'

model-paths: ["models"]
seed-paths: ["seeds"]
test-paths: ["tests"]
macro-paths: ["macros"]
snapshot-paths: ["snapshots"]

target-path: "target"
clean-targets:
  - "target"
  - "dbt_packages"

models:
  analytics:
    staging:
      +materialized: view
      +schema: staging
    intermediate:
      +materialized: ephemeral
    marts:
      +materialized: table
      +schema: marts

vars:
  start_date: '2024-01-01'
```

### profiles.yml

```yaml
# ~/.dbt/profiles.yml
analytics:
  target: dev
  outputs:
    dev:
      type: clickhouse
      host: localhost
      port: 8123
      user: "{{ env_var('DBT_USER') }}"
      password: "{{ env_var('DBT_PASSWORD') }}"
      schema: analytics_dev
      secure: false

    prod:
      type: clickhouse
      host: clickhouse.example.com
      port: 8443
      user: "{{ env_var('DBT_USER') }}"
      password: "{{ env_var('DBT_PASSWORD') }}"
      schema: analytics
      secure: true
```

### packages.yml

```yaml
packages:
  - package: dbt-labs/dbt_utils
    version: 1.1.1

  - package: dbt-labs/codegen
    version: 0.12.1

  - package: calogica/dbt_expectations
    version: 0.10.1
```

---

## Models

### Sources Definition

```yaml
# models/staging/_staging__sources.yml
version: 2

sources:
  - name: raw
    database: bronze
    schema: raw
    tables:
      - name: users
        identifier: raw_users
        loaded_at_field: _loaded_at
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}

      - name: events
        identifier: raw_events
        loaded_at_field: _loaded_at
        freshness:
          warn_after: {count: 1, period: hour}
          error_after: {count: 6, period: hour}

      - name: orders
        identifier: raw_orders
```

### Staging Model

```sql
-- models/staging/stg_users.sql
{{
    config(
        materialized='incremental',
        unique_key='user_id',
        incremental_strategy='merge'
    )
}}

with source as (
    select * from {{ source('raw', 'users') }}
    {% if is_incremental() %}
    where _loaded_at > (select max(_loaded_at) from {{ this }})
    {% endif %}
),

renamed as (
    select
        id as user_id,
        lower(trim(email)) as email,
        coalesce(name, 'Unknown') as name,
        created_at,
        updated_at,
        _loaded_at
    from source
)

select * from renamed
```

### Intermediate Model

```sql
-- models/intermediate/int_user_orders.sql
with users as (
    select * from {{ ref('stg_users') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

user_orders as (
    select
        u.user_id,
        u.email,
        count(o.order_id) as total_orders,
        sum(o.amount) as total_spent,
        min(o.created_at) as first_order_at,
        max(o.created_at) as last_order_at
    from users u
    left join orders o on u.user_id = o.user_id
    group by u.user_id, u.email
)

select * from user_orders
```

### Mart Model

```sql
-- models/marts/fct_daily_orders.sql
{{
    config(
        materialized='table',
        partition_by={'field': 'order_date', 'data_type': 'date'}
    )
}}

with orders as (
    select * from {{ ref('stg_orders') }}
),

daily_orders as (
    select
        date(created_at) as order_date,
        count(*) as order_count,
        count(distinct user_id) as unique_customers,
        sum(amount) as total_revenue,
        avg(amount) as avg_order_value
    from orders
    where status = 'completed'
    group by order_date
)

select * from daily_orders
```

---

## Testing

### Schema Tests

```yaml
# models/marts/_marts__models.yml
version: 2

models:
  - name: fct_daily_orders
    description: "Daily order metrics"
    columns:
      - name: order_date
        description: "Order date"
        tests:
          - not_null
          - unique

      - name: order_count
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0

      - name: total_revenue
        tests:
          - not_null
          - dbt_expectations.expect_column_values_to_be_between:
              min_value: 0
```

### Custom Tests

```sql
-- tests/generic/test_positive_values.sql
{% test positive_values(model, column_name) %}

select *
from {{ model }}
where {{ column_name }} < 0

{% endtest %}
```

---

## Macros

### Utility Macros

```sql
-- macros/utils.sql
{% macro generate_schema_name(custom_schema_name, node) %}
    {%- set default_schema = target.schema -%}
    {%- if custom_schema_name is none -%}
        {{ default_schema }}
    {%- else -%}
        {{ default_schema }}_{{ custom_schema_name }}
    {%- endif -%}
{% endmacro %}

{% macro safe_divide(numerator, denominator) %}
    case
        when {{ denominator }} = 0 then null
        else {{ numerator }} / {{ denominator }}
    end
{% endmacro %}
```

---

## Commands

```bash
# Install dependencies
dbt deps

# Run all models
dbt run

# Run specific models
dbt run --select staging
dbt run --select fct_daily_orders+  # With downstream
dbt run --select +fct_daily_orders  # With upstream

# Test
dbt test
dbt test --select stg_users

# Generate docs
dbt docs generate
dbt docs serve

# Full refresh (ignore incremental)
dbt run --full-refresh

# Compile (dry run)
dbt compile

# Debug
dbt debug
```

---

## CI/CD

### GitHub Actions

```yaml
name: dbt CI

on:
  pull_request:
    paths: ['models/**', 'dbt_project.yml']

jobs:
  dbt-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - run: pip install dbt-clickhouse

      - run: dbt deps

      - run: dbt build --select state:modified+
        env:
          DBT_USER: ${{ secrets.DBT_USER }}
          DBT_PASSWORD: ${{ secrets.DBT_PASSWORD }}
```

---

## Best Practices

1. **Use refs** - Always `{{ ref('model') }}` not table names
2. **Layer models** - staging → intermediate → marts
3. **Test everything** - Especially primary keys and nulls
4. **Document models** - Use YAML descriptions
5. **Use incremental** - For large tables
6. **Version control** - All models in git
