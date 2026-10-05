# Schema Design Scenarios

Worked scenarios for common schema decisions. The MongoDB Atlas AI-context scenario lives in [mongodb-atlas-ai-context.md](mongodb-atlas-ai-context.md).

## Contents

- [S1 — Multi-tenant schema: shared vs schema-per-tenant](#s1--multi-tenant-schema-shared-vs-schema-per-tenant)
- [S2 — Postgres expand-contract migration with online backfill](#s2--postgres-expand-contract-migration-with-online-backfill)
- [S3 — Index design for high-cardinality lookup](#s3--index-design-for-high-cardinality-lookup)
- [S4 — Soft-delete vs row archival](#s4--soft-delete-vs-row-archival)
- [S5 — JSONB column versioning](#s5--jsonb-column-versioning)

## S1 — Multi-tenant schema: shared vs schema-per-tenant

1. Enumerate isolation requirements: compliance, data residency, noisy-neighbor risk, and restore granularity.
2. Use **shared schema with `tenant_id`** as a starting point when isolation requirements allow it; one schema simplifies migrations, while RLS can enforce per-row visibility if configured and tested correctly.
3. Use **schema-per-tenant** when independently managed restore or contractual isolation requires it. Migrations then run for every schema and pooler/catalog overhead must be measured on the expected tenant count (see [Connection Pooling & Schema Design](partitioning-and-pooling.md#connection-pooling--schema-design)).
4. For shared schema: add `tenant_id` to every data table, enable RLS, and add a composite index `(tenant_id, id)` on high-traffic tables.
5. Verify a new tenant row produces correct RLS visibility in a CI integration test.

**RLS failure and performance gates.** Query as the actual application role: superusers and roles with `BYPASSRLS` always bypass policies, while table owners normally bypass them unless `FORCE ROW LEVEL SECURITY` is set. If a policy reads `current_setting('app.tenant_id', true)`, a missing setting yields `NULL`, so design the predicate to deny that case; set tenant context from trusted authentication in the transaction, clear it before connection reuse, and do not treat a client-settable GUC alone as proof of identity. Index tenant predicates and inspect `EXPLAIN` under the application role: RLS applies policy expressions per row, and only `LEAKPROOF` functions may be moved before that check, which can change plan choices. Test absent and wrong tenant contexts and a bypass-capable role. [PostgreSQL row security](https://www.postgresql.org/docs/current/ddl-rowsecurity.html), [current_setting](https://www.postgresql.org/docs/current/functions-admin.html#FUNCTIONS-ADMIN-SET).

## S2 — Postgres expand-contract migration with online backfill

1. **Expand**: add the new column as `nullable` with no constraints; deploy app code that writes to both old and new columns.
2. Run the backfill as a separate, rate-limited background job — not inside the migration transaction; verify row counts before and after.
3. **Migrate**: deploy app code that reads from the new column; run `CREATE INDEX CONCURRENTLY` on the new column.
4. Add `NOT NULL` + constraints only after backfill is complete. **PostgreSQL 18+:** add the constraint directly with `ALTER TABLE ... ADD CONSTRAINT ... NOT NULL NOT VALID` (instant, no scan), then `VALIDATE CONSTRAINT` in a separate statement (`SHARE UPDATE EXCLUSIVE` lock only, concurrent writes proceed) — validate with `VALIDATE CONSTRAINT`, not `SET NOT NULL`: running `SET NOT NULL` while the not-null constraint is still invalid validates it with a full scan under `ACCESS EXCLUSIVE`. **PostgreSQL 12-17:** first add `CHECK (col IS NOT NULL) NOT VALID` (instant, no scan), then `VALIDATE CONSTRAINT` (`SHARE UPDATE EXCLUSIVE`), then `SET NOT NULL` (Postgres uses the validated CHECK and skips its own scan).
5. **Contract**: deploy app code that drops the old column path; remove the old column in a follow-up migration after one release cycle.

## S3 — Index design for high-cardinality lookup

1. Identify the exact `WHERE`, `JOIN ON`, and `ORDER BY` clauses from the query plan (`EXPLAIN ANALYZE`).
2. Lead the composite index with the column every query filters on by equality; add range-filter columns after (Equality → Sort → Range).
3. Use a partial index to exclude soft-deleted or inactive rows: `WHERE deleted_at IS NULL`.
4. Use a covering index (`INCLUDE (col)`) to avoid a heap fetch on hot queries.
5. Run `CREATE INDEX CONCURRENTLY` on production; monitor `pg_stat_user_indexes` for unused indexes and drop them.

## S4 — Soft-delete vs row archival

1. Use soft delete (`deleted_at TIMESTAMP`) only when you need a recovery window or audit trail.
2. Add a partial index `WHERE deleted_at IS NULL`; exclude deleted rows from all ORM default scopes.
3. For large tables, archive rows older than N days to an archive table on a schedule.
4. When audit trail is the primary need, prefer an append-only audit log table — hard-delete the operational row, keep the event.
5. Verify that all `COUNT`, aggregate, and join queries explicitly filter `deleted_at IS NULL`; add a lint rule or ORM default scope to enforce it.

## S5 — JSONB column versioning

1. Add a `schema_version INT DEFAULT 1` column alongside the JSONB column.
2. On read, branch on `schema_version` and normalize older shapes in the application layer.
3. Run a one-time backfill migration upgrading all `schema_version = 1` rows; rate-limit to avoid lock contention.
4. After backfill, add a `CHECK (schema_version = 2)` constraint and drop the normalization branch.
5. Match the index to the query operator: a GIN index on the JSONB column can support containment (`@>`), while a frequent `payload->>'status' = 'ready'` text comparison needs an expression B-tree index such as `CREATE INDEX ON events ((payload->>'status'));` for a table `events(payload jsonb)`. Verify the actual predicate with `EXPLAIN`; a plain JSONB GIN index does not cover arbitrary `->>` equality. See [PostgreSQL JSONB indexing](https://www.postgresql.org/docs/current/datatype-json.html#JSON-INDEXING).
