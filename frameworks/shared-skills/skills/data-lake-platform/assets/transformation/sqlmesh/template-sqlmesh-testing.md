# SQLMesh Testing and Data Quality Templates

Use complementary checks at three levels:

1. Unit tests prove query behavior with small synthetic inputs.
2. Audits enforce invariants on evaluated model data.
3. A plan validates lineage and change categorization before application.

The examples use fictional order records and contain no production data.

## Model audits

```sql
MODEL (
  name core.orders,
  kind FULL,
  grain order_id,
  audits (
    not_null(columns := [order_id, customer_id, ordered_at]),
    unique_values(columns := [order_id]),
    accepted_values(column := order_status, is_in := ['open', 'completed', 'cancelled'])
  )
);

SELECT
  order_id,
  customer_id,
  order_status,
  order_total,
  ordered_at
FROM staging.orders;
```

Choose audits that express a genuine contract. A noisy threshold that is always
ignored is worse than no threshold.

## Custom audit

An audit query returns failing rows.

```sql
AUDIT (
  name positive_order_total
);

SELECT *
FROM @this_model
WHERE order_total < 0;
```

Parameterized version:

```sql
AUDIT (
  name values_within_bounds
);

SELECT *
FROM @this_model
WHERE @column < @minimum
   OR @column > @maximum;
```

Use it from a model:

```sql
audits (
  values_within_bounds(
    column := order_total,
    minimum := 0,
    maximum := 100000
  )
)
```

## Unit test

```yaml
# tests/test_daily_order_totals.yaml
test_daily_order_totals_groups_completed_orders:
  model: marts.daily_order_totals
  inputs:
    core.orders:
      rows:
        - order_id: 1001
          customer_id: 501
          order_status: completed
          order_total: 25.00
          ordered_at: '2025-01-10 09:00:00'
        - order_id: 1002
          customer_id: 501
          order_status: cancelled
          order_total: 10.00
          ordered_at: '2025-01-10 10:00:00'
  outputs:
    query:
      rows:
        - order_date: '2025-01-10'
          customer_id: 501
          order_count: 1
          gross_total: 25.00
```

Include boundary cases: duplicate source records, nulls, interval edges,
time-zone changes, and values that should be rejected.

## Commands

```bash
# Run all unit tests.
sqlmesh test

# Run one test by name.
sqlmesh test test_daily_order_totals_groups_completed_orders

# Render a bounded interval.
sqlmesh render marts.daily_order_totals --start 2025-01-10 --end 2025-01-11

# Preview an isolated environment without applying it.
sqlmesh plan review_123 --gateway ci --no-prompts

# Run model audits after evaluation.
sqlmesh audit --gateway ci
```

Use a disposable database or schema for CI. Never aim test commands at a
production gateway.

## Minimal verification script

```bash
#!/usr/bin/env bash
set -euo pipefail

gateway="${SQLMESH_GATEWAY:-local}"
environment="${SQLMESH_ENVIRONMENT:-verification}"

sqlmesh format --check
sqlmesh test --gateway "$gateway"
sqlmesh plan "$environment" --gateway "$gateway" --no-prompts
```

The script intentionally does not auto-apply.

## CI example

```yaml
validate-models:
  image: python:3.12-slim
  stage: test
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
  script:
    - pip install -r requirements.lock
    - sqlmesh format --check
    - sqlmesh test --gateway ci
    - sqlmesh plan "mr_${CI_MERGE_REQUEST_IID}" --gateway ci --no-prompts
```

Provide database variables through protected CI settings and ensure the CI
identity cannot alter production.

## What to test

| Contract | Appropriate check |
|---|---|
| Primary key is present and unique | `not_null` and `unique_values` audits |
| Enumeration contains known values | Accepted-values audit |
| Query implements business branching | Unit test with one row per branch |
| Incremental boundaries do not overlap | Unit tests at start/end timestamps |
| Join does not multiply the grain | Row-count or uniqueness audit |
| Freshness stays within an objective | Time-based custom audit |
| Sensitive fields are not published | Schema assertion and authorization test |

## Failure handling

- Preserve the failing test name, model, SQLMesh version, and gateway class.
- Reproduce with the smallest synthetic input possible.
- Distinguish query defects from stale fixtures and environment failures.
- Do not weaken an audit merely to make a deployment green.
- If an invariant legitimately changed, update the model, test, and consumer
  contract in the same review.

## Review checklist

- Fixtures are synthetic and easy to understand.
- Each unit test asserts one behavior.
- Incremental models test interval boundaries.
- Audits match the declared grain and business invariants.
- CI uses a disposable, least-privilege environment.
- The plan is reviewed before any apply step.
- Test output contains no credentials or copied production rows.
