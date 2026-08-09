# SQLMesh Model Templates

Use these examples as starting points for a new SQLMesh project. Replace every
schema, column, cadence, and audit with values that belong to the target
repository. The examples use a fictional order-processing dataset.

## Choose the model kind

| Need | Kind | Main constraint |
|---|---|---|
| Rebuild a small result completely | `FULL` | The query must be safe to rerun |
| Process bounded time windows | `INCREMENTAL_BY_TIME_RANGE` | Filter on `@start_date` and `@end_date` |
| Upsert records by a stable key | `INCREMENTAL_BY_UNIQUE_KEY` | The key must identify one logical row |
| Expose a lightweight query | `VIEW` | Avoid expensive repeated computation |

## Full model

```sql
MODEL (
  name core.customers,
  kind FULL,
  grain customer_id,
  cron '@daily',
  audits (
    not_null(columns := [customer_id]),
    unique_values(columns := [customer_id])
  )
);

SELECT
  customer_id,
  NULLIF(TRIM(display_name), '') AS display_name,
  created_at
FROM staging.customers;
```

Use `FULL` when the result is modest and a complete rebuild is easier to reason
about than incremental state.

## Time-range incremental model

```sql
MODEL (
  name marts.daily_order_totals,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column order_date
  ),
  grain (order_date, customer_id),
  cron '@daily',
  audits (
    not_null(columns := [order_date, customer_id]),
    unique_values(columns := [order_date, customer_id])
  )
);

SELECT
  CAST(ordered_at AS DATE) AS order_date,
  customer_id,
  COUNT(*) AS order_count,
  SUM(order_total) AS gross_total
FROM staging.orders
WHERE ordered_at >= @start_date
  AND ordered_at < @end_date
GROUP BY 1, 2;
```

Keep the interval half-open. The same boundary convention must be used by the
source filter, tests, and downstream consumers.

## Unique-key incremental model

```sql
MODEL (
  name core.orders,
  kind INCREMENTAL_BY_UNIQUE_KEY (
    unique_key order_id
  ),
  grain order_id,
  audits (
    not_null(columns := [order_id]),
    unique_values(columns := [order_id])
  )
);

SELECT
  order_id,
  customer_id,
  order_status,
  order_total,
  updated_at
FROM staging.orders_latest;
```

Do not use an unstable timestamp or a mutable display value as the unique key.

## View model

```sql
MODEL (
  name marts.open_orders,
  kind VIEW,
  grain order_id
);

SELECT
  order_id,
  customer_id,
  order_total,
  updated_at
FROM core.orders
WHERE order_status = 'open';
```

## Reusable query patterns

### Deterministic deduplication

```sql
WITH ranked AS (
  SELECT
    source_row_id,
    business_key,
    payload,
    received_at,
    ROW_NUMBER() OVER (
      PARTITION BY business_key
      ORDER BY received_at DESC, source_row_id DESC
    ) AS row_rank
  FROM staging.source_events
)
SELECT
  business_key,
  payload,
  received_at
FROM ranked
WHERE row_rank = 1;
```

Always include a stable tie-breaker in the ordering.

### Aggregation with an explicit grain

```sql
SELECT
  report_date,
  region_code,
  COUNT(DISTINCT order_id) AS orders,
  SUM(order_total) AS gross_total
FROM core.order_facts
GROUP BY report_date, region_code;
```

The `MODEL` grain should match the grouped columns.

### Slowly changing dimension output

```sql
SELECT
  customer_id,
  status,
  valid_from,
  LEAD(valid_from) OVER (
    PARTITION BY customer_id
    ORDER BY valid_from
  ) AS valid_to
FROM staging.customer_status_history;
```

Validate that intervals do not overlap before downstream use.

## Indexes and grants

Database-specific DDL belongs after the model query only when the target engine
and repository conventions support it. Keep object names short and deterministic.

```sql
CREATE INDEX IF NOT EXISTS ix_orders_customer_updated
ON @this_model (customer_id, updated_at);
```

Prefer repository-managed migrations for role and policy definitions. If a
model must own grants, make them explicit and idempotent rather than relying on
undocumented helper macros.

## Documentation block

Document semantics that a column name cannot communicate:

```sql
MODEL (
  name marts.customer_order_summary,
  kind FULL,
  grain customer_id,
  description 'One row per customer with completed-order totals.'
);

SELECT
  customer_id,
  COUNT(*) AS completed_orders,
  SUM(order_total) AS completed_order_total
FROM core.orders
WHERE order_status = 'completed'
GROUP BY customer_id;
```

## Review checklist

- The model name and grain describe the actual result.
- Incremental filters cover every intended row exactly once.
- Deduplication has a deterministic tie-breaker.
- Audits test keys, nullability, and business invariants.
- Sensitive columns are omitted or transformed for the intended audience.
- Engine-specific DDL is supported by the selected gateway.
- `sqlmesh format`, `sqlmesh render`, `sqlmesh test`, and a non-production plan
  succeed before merge.

## Related templates

- `template-sqlmesh-incremental.md`
- `template-sqlmesh-testing.md`
- `template-sqlmesh-security.md`
- `template-sqlmesh-production.md`
