# PostgreSQL Row-Level Security Template

Row-level security (RLS) adds database-enforced predicates to table access. Use
it when rows in one table have different audiences and the database can obtain
trusted request context. RLS complements application authorization; it does not
replace identity verification, column controls, encryption, or audit logging.

The examples below use a fictional multi-tenant task application.

## Core behavior

```sql
CREATE TABLE app.tasks (
  task_id uuid PRIMARY KEY,
  tenant_id uuid NOT NULL,
  title text NOT NULL,
  task_state text NOT NULL,
  created_by uuid NOT NULL,
  created_at timestamptz NOT NULL DEFAULT now()
);

ALTER TABLE app.tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE app.tasks FORCE ROW LEVEL SECURITY;
```

`ENABLE` applies policies to ordinary roles. `FORCE` also subjects the table
owner to RLS in normal operation. Superusers and roles with `BYPASSRLS` still
bypass policies, so application connections must not use them.

With RLS enabled and no applicable policy, access is denied by default.

## Tenant context

One common pattern passes a validated tenant identifier through a transaction-
local PostgreSQL setting:

```sql
SELECT set_config('app.current_tenant', $1, true);
```

The third argument makes the setting transaction-local. Build a small helper
that fails closed when context is absent or malformed:

```sql
CREATE FUNCTION app.current_tenant_id()
RETURNS uuid
LANGUAGE sql
STABLE
AS $$
  SELECT NULLIF(current_setting('app.current_tenant', true), '')::uuid
$$;
```

Only the trusted request boundary may set the value. Do not accept a tenant
identifier from a client without checking that the authenticated principal is
authorized for it.

## Read policy

```sql
CREATE POLICY tasks_select_tenant
ON app.tasks
FOR SELECT
TO task_reader
USING (tenant_id = app.current_tenant_id());
```

`USING` controls which existing rows are visible.

## Insert policy

```sql
CREATE POLICY tasks_insert_tenant
ON app.tasks
FOR INSERT
TO task_writer
WITH CHECK (
  tenant_id = app.current_tenant_id()
  AND created_by = NULLIF(current_setting('app.current_user', true), '')::uuid
);
```

`WITH CHECK` controls the state of a new row.

## Update policy

```sql
CREATE POLICY tasks_update_tenant
ON app.tasks
FOR UPDATE
TO task_writer
USING (tenant_id = app.current_tenant_id())
WITH CHECK (tenant_id = app.current_tenant_id());
```

Use both clauses: the role must be allowed to see the old row and to create the
new row state.

## Delete policy

```sql
CREATE POLICY tasks_delete_tenant
ON app.tasks
FOR DELETE
TO task_writer
USING (tenant_id = app.current_tenant_id());
```

If deletion is not a supported operation, omit the policy and let default deny
apply.

## User ownership within a tenant

```sql
CREATE POLICY task_notes_by_author
ON app.task_notes
FOR ALL
TO task_editor
USING (
  tenant_id = app.current_tenant_id()
  AND author_id = NULLIF(current_setting('app.current_user', true), '')::uuid
)
WITH CHECK (
  tenant_id = app.current_tenant_id()
  AND author_id = NULLIF(current_setting('app.current_user', true), '')::uuid
);
```

Be deliberate with `FOR ALL`. Separate policies are easier to review when read
and write permissions differ.

## Restrictive and permissive policies

Permissive policies for the same command are combined with `OR`. Restrictive
policies are combined with `AND` against the permissive result.

```sql
CREATE POLICY tasks_not_archived
ON app.tasks
AS RESTRICTIVE
FOR SELECT
TO task_reader
USING (task_state <> 'archived');
```

Document the intended Boolean expression whenever more than one policy applies.

## Roles and grants

RLS is evaluated only after ordinary privileges allow the command.

```sql
CREATE ROLE task_reader NOLOGIN;
CREATE ROLE task_writer NOLOGIN;

GRANT USAGE ON SCHEMA app TO task_reader, task_writer;
GRANT SELECT ON app.tasks TO task_reader;
GRANT SELECT, INSERT, UPDATE, DELETE ON app.tasks TO task_writer;
```

Grant these capability roles to login identities. Do not make the application
role the table owner.

## Performance

Index the columns used by policy predicates and common query filters:

```sql
CREATE INDEX ix_tasks_tenant_created
ON app.tasks (tenant_id, created_at DESC);

CREATE INDEX ix_tasks_tenant_state
ON app.tasks (tenant_id, task_state);
```

Then compare plans using a realistic non-owner role:

```sql
BEGIN;
SET LOCAL ROLE task_reader;
SELECT set_config(
  'app.current_tenant',
  '11111111-1111-1111-1111-111111111111',
  true
);
EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM app.tasks ORDER BY created_at DESC LIMIT 20;
ROLLBACK;
```

Avoid volatile functions, network calls, and large subqueries in policies.
Mark helper functions with the narrowest correct volatility and secure their
`search_path` if they use `SECURITY DEFINER`.

## Connection pooling

Session state can leak across pooled requests. Prefer transaction-local context:

```sql
BEGIN;
SELECT set_config('app.current_tenant', $1, true);
SELECT set_config('app.current_user', $2, true);
-- application queries
COMMIT;
```

Integration tests must reuse a connection across two different tenants and
prove that the second request cannot inherit the first request's context.

## Migration sequence

1. Add the scope column as nullable if backfill is required.
2. Populate and validate the scope for every existing row.
3. Add `NOT NULL`, foreign keys, and supporting indexes.
4. Create non-owner capability roles and grants.
5. Add command-specific policies.
6. Enable and force RLS.
7. Run negative authorization tests before serving traffic.
8. Monitor errors and query plans during rollout.

Do not enable RLS before existing rows have valid scope values unless the
planned default-deny outage is intentional.

## Test matrix

| Scenario | Expected result |
|---|---|
| Context missing | No rows or a controlled error |
| Tenant A reads Tenant A | Allowed |
| Tenant A reads Tenant B | No rows |
| Tenant A inserts Tenant B row | Rejected |
| Writer changes `tenant_id` | Rejected |
| Owner-like runtime role | Prohibited by configuration |
| Pooled connection changes tenant | No state leakage |

Example negative assertion:

```sql
BEGIN;
SET LOCAL ROLE task_writer;
SELECT set_config(
  'app.current_tenant',
  '11111111-1111-1111-1111-111111111111',
  true
);

INSERT INTO app.tasks (
  task_id,
  tenant_id,
  title,
  task_state,
  created_by
) VALUES (
  'aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa',
  '22222222-2222-2222-2222-222222222222',
  'Forbidden cross-tenant row',
  'open',
  '33333333-3333-3333-3333-333333333333'
);
-- Expected: row-level security policy violation.
ROLLBACK;
```

## Inspection queries

```sql
SELECT
  schemaname,
  tablename,
  rowsecurity,
  forcerowsecurity
FROM pg_tables
WHERE schemaname = 'app';

SELECT
  schemaname,
  tablename,
  policyname,
  permissive,
  roles,
  cmd,
  qual,
  with_check
FROM pg_policies
WHERE schemaname = 'app'
ORDER BY tablename, policyname;
```

Review drift between these results and migration definitions.

## Review checklist

- Every protected table has a non-null scope column.
- Each supported command has an explicit policy.
- Update policies contain appropriate `USING` and `WITH CHECK` clauses.
- Application roles are neither owners, superusers, nor `BYPASSRLS` roles.
- Policy columns are indexed and plans are tested as runtime roles.
- Pooling tests prove context isolation.
- Column sensitivity is controlled separately from RLS.
- Migrations include rollback and staged-rollout instructions.
- Examples contain only fictional identifiers and reserved domains.
