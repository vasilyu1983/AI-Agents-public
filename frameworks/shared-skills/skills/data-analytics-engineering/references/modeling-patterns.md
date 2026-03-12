# Analytics Modeling Patterns

## Core Principles

- Define grain before writing transformations
- Prefer star schema for BI and reporting
- Separate staging, intermediate, and marts
- Keep metric definitions stable and versioned
- Validate joins with row count checks

## Layer Architecture

### Three-Layer Pattern

| Layer | Purpose | Naming | Tests |
|-------|---------|--------|-------|
| **Staging** | Clean raw data, rename columns, cast types | `stg_[source]__[entity]` | not_null, unique on PK |
| **Intermediate** | Business logic, joins, deduplication | `int_[entity]_[verb]` | relationships, row counts |
| **Marts** | Final tables for consumption | `fct_[event]`, `dim_[entity]` | accepted_values, freshness |

### Staging Layer Rules

- One model per source table
- Column renaming only (no joins)
- Type casting and null handling
- No business logic

### Intermediate Layer Rules

- Complex joins and window functions
- Deduplication logic
- Business calculations
- Can reference other intermediate models

### Marts Layer Rules

- Star schema design (facts + dimensions)
- Wide tables for specific use cases
- Aggregations and final metrics
- Optimized for BI tool consumption

## Dimensional Modeling

### Fact Tables

```sql
-- fct_orders: grain = one row per order line item
SELECT
    order_line_id,           -- degenerate dimension
    order_id,                -- degenerate dimension
    customer_key,            -- FK to dim_customers
    product_key,             -- FK to dim_products
    order_date_key,          -- FK to dim_dates
    quantity,                -- measure
    unit_price,              -- measure
    discount_amount,         -- measure
    net_revenue              -- calculated measure
FROM {{ ref('int_orders_enriched') }}
```

### Dimension Tables

```sql
-- dim_customers: SCD Type 2 for tracking changes
SELECT
    customer_key,            -- surrogate key
    customer_id,             -- natural key
    customer_name,
    segment,
    region,
    valid_from,
    valid_to,
    is_current
FROM {{ ref('int_customers_history') }}
```

### Slowly Changing Dimensions

| Type | Behavior | Use Case |
|------|----------|----------|
| **SCD 0** | Never update | Reference data, codes |
| **SCD 1** | Overwrite | Corrections, non-audited fields |
| **SCD 2** | Version with history | Audited attributes, segment changes |
| **SCD 3** | Previous value column | Single prior value needed |

## Metric Definition Patterns

### MetricFlow Syntax (dbt Semantic Layer)

```yaml
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
        type_params:
          time_granularity: day
      - name: order_status
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

### Metric Governance Rules

- One canonical definition per metric
- Version metrics with semantic versioning
- Document calculation logic inline
- Include grain and time spine requirements
- Specify valid dimensions for each metric

## Data Quality Testing

### Test Coverage Matrix

| Model Type | Required Tests | Optional Tests |
|------------|----------------|----------------|
| Staging | not_null (PK), unique (PK) | accepted_values |
| Intermediate | relationships, row_count | dbt_expectations |
| Facts | freshness, not_null (FKs) | range checks |
| Dimensions | unique (SK), not_null (NK) | SCD validity |

### dbt-expectations Examples

```yaml
# Updated: dbt-expectations now maintained by Metaplane
# Install: pip install dbt-expectations (Metaplane fork)

models:
  - name: fct_orders
    tests:
      - dbt_expectations.expect_table_row_count_to_be_between:
          min_value: 1000
          max_value: 10000000
      - dbt_expectations.expect_column_values_to_be_between:
          column_name: order_total
          min_value: 0
          max_value: 1000000
      - dbt_expectations.expect_column_values_to_match_regex:
          column_name: order_id
          regex: "^ORD-[0-9]{8}$"
```

### Elementary Anomaly Detection

```yaml
# Elementary provides ML-based anomaly detection
models:
  - name: fct_orders
    meta:
      elementary:
        timestamp_column: created_at
    tests:
      - elementary.volume_anomalies:
          timestamp_column: created_at
          where: "order_status = 'completed'"
      - elementary.freshness_anomalies:
          timestamp_column: updated_at
```

## State Management Patterns

### dbt (Stateless)

- Relies on incremental flags and manifests
- Add-ons like dbt_artifacts for change tracking
- Full refresh on schema changes
- CI validation with state comparison

### SQLMesh (Stateful)

- Built-in state tracking
- Virtual dev environments
- Only changed tables rebuilt
- Terraform-like state management
- Can reduce rebuild work by tracking change impact (validate in your environment)

### When to Choose Each

| Scenario | Recommendation |
|----------|----------------|
| Existing dbt investment | Stay with dbt |
| New greenfield project | Evaluate SQLMesh |
| Large-scale transformations | Evaluate SQLMesh (stateful rebuilds, compile-time parsing) |
| dbt Cloud features needed | dbt |
| Vendor-specific ecosystem (e.g., ingestion tooling) | Validate integration options before choosing |

## Anti-Patterns to Avoid

### Mixed Grains

```sql
-- BAD: mixing order-level and line-item-level
SELECT
    order_id,
    line_item_id,        -- line-item grain
    order_total,         -- order grain (will duplicate)
    line_item_amount
FROM orders
JOIN line_items USING (order_id)
```

### Metric Drift

- Multiple definitions of "revenue" across teams
- Undocumented filters in metric calculations
- No versioning on metric changes
- **Solution**: Implement semantic layer with single source of truth

### Missing Lineage

- No documentation of upstream dependencies
- Unclear data freshness expectations
- No ownership assignment
- **Solution**: Use OpenLineage + DataHub for metadata

## Related Resources

- [Tool Comparison 2026](tool-comparison-2026.md) - dbt vs SQLMesh vs Coalesce
- [Data Quality Test Plan](../assets/data-quality-test-plan.md) - Test coverage template
- [Metric Dictionary](../assets/metric-dictionary.md) - Metric definition template
