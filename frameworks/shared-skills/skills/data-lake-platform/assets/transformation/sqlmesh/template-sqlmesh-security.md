# SQLMesh Security and Privacy Patterns

This guide shows portable security patterns for a fictional multi-tenant order
system. Treat it as a design checklist, not as a ready-made policy set. Database
roles, identity propagation, retention periods, and legal requirements must be
defined by the repository that adopts the template.

## Security boundaries

Use separate controls for separate risks:

| Risk | Primary control |
|---|---|
| A user reads another tenant's rows | Database row-level security |
| A permitted user sees unnecessary fields | Projection, masking, or a restricted view |
| A pipeline account can mutate production | Least-privilege database role |
| Historical data is retained too long | Scheduled deletion with an auditable rule |
| Sensitive access cannot be reconstructed | Database and application audit logs |

Row filtering does not mask columns. A role that may read a row can still read
every projected column unless a separate control removes or transforms it.

## Publish only the required columns

The safest public model does not contain data its audience does not need.

```sql
MODEL (
  name marts.customer_directory,
  kind VIEW,
  grain customer_id,
  description 'Customer directory without contact or authentication data.'
);

SELECT
  customer_id,
  display_name,
  account_state,
  created_at
FROM core.customers;
```

Keep email addresses, phone numbers, authentication identifiers, and free-text
notes in a separately governed model if they must exist at all.

## Deterministic pseudonyms

Use a keyed, centrally managed transformation for stable pseudonyms. Do not put
the key in SQL, model files, seed data, or CI variables printed to logs.

```sql
MODEL (
  name restricted.customer_research_ids,
  kind VIEW,
  grain customer_id
);

SELECT
  customer_id,
  encode(
    hmac(customer_id::text, current_setting('app.pseudonym_key'), 'sha256'),
    'hex'
  ) AS research_id
FROM core.customers;
```

The example uses PostgreSQL `pgcrypto`; choose an equivalent supported by the
target engine. Rotation and access to the key belong in the platform runbook.

## Tenant row-level security

Create policies through a migration or infrastructure workflow so ownership is
clear and policy changes are reviewed separately from analytical query changes.

```sql
ALTER TABLE serving.orders ENABLE ROW LEVEL SECURITY;
ALTER TABLE serving.orders FORCE ROW LEVEL SECURITY;

CREATE POLICY orders_read_by_tenant
ON serving.orders
FOR SELECT
TO app_reader
USING (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
);
```

The application must set `app.tenant_id` on every checked-out connection and
clear it before the connection returns to the pool. Reject a request when the
context is missing rather than falling back to unrestricted access.

For writes, specify both visibility and the allowed new state:

```sql
CREATE POLICY orders_write_by_tenant
ON serving.orders
FOR UPDATE
TO app_writer
USING (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
)
WITH CHECK (
  tenant_id = NULLIF(current_setting('app.tenant_id', true), '')::uuid
);
```

## Role design

Keep roles composable and avoid granting ownership to runtime identities.

```text
NOLOGIN capability roles
  warehouse_read
  restricted_read
  pipeline_write

LOGIN identities
  analytics_service -> warehouse_read
  privacy_service   -> restricted_read
  transform_runner  -> warehouse_read + pipeline_write
```

Example grants:

```sql
GRANT USAGE ON SCHEMA marts TO warehouse_read;
GRANT SELECT ON ALL TABLES IN SCHEMA marts TO warehouse_read;

GRANT USAGE ON SCHEMA restricted TO restricted_read;
GRANT SELECT ON ALL TABLES IN SCHEMA restricted TO restricted_read;
```

Set default privileges for future objects in the migration that owns the
schema. Do not assume grants on today's tables will cover tomorrow's models.

## Data retention

Retention should be a named rule with an owner, clock, and evidence trail.

```sql
DELETE FROM restricted.expired_exports
WHERE expires_at < CURRENT_TIMESTAMP;
```

Before automating deletion, define:

- the authoritative timestamp;
- applicable holds or exceptions;
- batch size and retry behavior;
- evidence recorded after each run;
- how downstream snapshots and backups are handled.

## Audit-friendly model metadata

Descriptions should state audience and sensitivity without embedding internal
role inventories or real organization names.

```sql
MODEL (
  name marts.order_status_counts,
  kind FULL,
  grain (report_date, order_status),
  description 'Daily order counts; contains no direct customer identifiers.'
);
```

## Verification

Test security with distinct database sessions and explicit assertions.

```sql
SET ROLE app_reader;
SET app.tenant_id = '11111111-1111-1111-1111-111111111111';

SELECT COUNT(*)
FROM serving.orders
WHERE tenant_id <> '11111111-1111-1111-1111-111111111111';
-- Expected: 0

RESET app.tenant_id;
SELECT COUNT(*) FROM serving.orders;
-- Expected: 0 rows or an error, according to the fail-closed design.
```

Also verify:

- a tenant cannot insert or update a row for another tenant;
- a pooled connection does not retain the previous request's context;
- model owners and superusers are not used for application tests;
- restricted columns are absent from general-purpose models;
- policy and grant changes are visible in migration history;
- backups, exports, and temporary tables follow the same classification rules.

## Common mistakes

- Treating RLS as column masking.
- Using a permissive policy without understanding that permissive policies are
  combined with `OR`.
- Testing only as the table owner, which can bypass policies.
- Storing secrets in model definitions or sample environment files.
- Granting schema access without object access, or object access without schema
  usage.
- Publishing real identifiers, role names, hostnames, or regulatory mappings in
  reusable examples.

## Release checklist

1. Classify the model's inputs and outputs.
2. Confirm the minimum audience and columns.
3. Review migrations for grants, policies, and default privileges.
4. Run SQLMesh render, unit tests, audits, and a non-production plan.
5. Execute positive and negative authorization tests using non-owner roles.
6. Record the policy owner, retention rule, and rollback procedure.
