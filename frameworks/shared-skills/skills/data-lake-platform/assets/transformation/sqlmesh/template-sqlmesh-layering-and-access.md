# SQLMesh Layers and Access Boundaries

Use this template to define clear dependencies between transformation layers.
The names below are generic; a repository may use different names, but it
should keep equivalent contracts explicit.

## Layer contracts

### `staging`

- Reads from source or landing schemas only.
- Casts types, normalizes names, and performs source-local cleanup.
- Keeps source keys needed for traceability.
- Avoids cross-source joins.
- Is not a stable interface for dashboards or external consumers.

### `core`

- Reads from `staging` and other `core` models.
- Resolves shared entities and reusable business rules.
- Declares a stable grain for every model.
- Adds deterministic deduplication and relationship checks.
- Does not contain presentation-only formatting.

### `marts`

- Reads primarily from `core`.
- Publishes consumer-oriented datasets at documented grains.
- Includes descriptions, ownership, freshness expectations, and audits.
- Exposes only the columns required by its intended audience.
- Avoids reaching back to raw sources around the core contract.

### `restricted`

- Contains datasets requiring a narrower audience than general marts.
- Uses separate roles and schemas from broadly readable analytics.
- Omits or transforms sensitive columns where possible.
- Has explicit retention and access-review ownership.

## Dependency rule

```text
sources -> staging -> core -> marts
                         \-> restricted
```

Dependencies should move to the right. A staging model must not depend on a
mart, and a general mart must not use a restricted model as a shortcut.

## Materialization guide

| Situation | Starting choice |
|---|---|
| Small, cheap, deterministic result | `FULL` |
| Large event table with a reliable time column | `INCREMENTAL_BY_TIME_RANGE` |
| Mutable records with a stable key | `INCREMENTAL_BY_UNIQUE_KEY` |
| Thin projection with acceptable query cost | `VIEW` |

Choose based on correctness and operating cost, then measure. Do not copy a
materialization choice solely because a nearby model uses it.

## Access design

Keep authorization definitions in migrations or infrastructure code unless the
repository explicitly assigns them to model lifecycle hooks.

Suggested capability roles:

```text
analytics_reader  -> SELECT on marts
restricted_reader -> SELECT on restricted
transform_writer  -> create/update transformation-owned schemas
```

Runtime identities should receive capability roles without owning schemas or
tables. Set default privileges for newly created objects and test authorization
with non-owner sessions.

## Model example

```sql
MODEL (
  name marts.daily_order_counts,
  kind INCREMENTAL_BY_TIME_RANGE (
    time_column report_date
  ),
  grain (report_date, order_status),
  description 'Daily order counts by status; no customer identifiers.',
  audits (
    not_null(columns := [report_date, order_status]),
    unique_values(columns := [report_date, order_status])
  )
);

SELECT
  CAST(ordered_at AS DATE) AS report_date,
  order_status,
  COUNT(*) AS order_count
FROM core.orders
WHERE ordered_at >= @start_date
  AND ordered_at < @end_date
GROUP BY 1, 2;
```

## PostgreSQL operating notes

- PostgreSQL identifiers are limited to 63 bytes; keep generated index and
  constraint names concise.
- Index the columns used by common joins, filters, and row-security predicates.
- Refresh planner statistics after large rebuilds through the repository's
  deployment process.
- Avoid session-dependent logic in shared models unless connection context is
  established and cleared reliably.
- Keep engine-specific DDL isolated so other gateways can render models.

## Validation sequence

1. `sqlmesh format --check`
2. `sqlmesh render <model> --start <date> --end <date>`
3. `sqlmesh test`
4. Create a plan for an isolated, non-production environment.
5. Review lineage, model categorization, audits, and expected backfills.
6. Apply only through the repository's approved deployment path.

## Review questions

- Does every model read only from allowed upstream layers?
- Is the declared grain true for every output row?
- Are incremental boundaries complete and non-overlapping?
- Is sensitive data absent from broadly readable models?
- Are roles, grants, and retention owned outside ad hoc analyst sessions?
- Are schema names and examples generic enough for public reuse?
