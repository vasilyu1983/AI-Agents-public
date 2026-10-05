# Server PostgreSQL memory verification

Use `scripts/verify_postgres_memory.py` when the shipped bitemporal facts and RLS examples need behavioral evidence on server PostgreSQL. The SQL text contract tests do not establish backend correctness. This runner loads the actual `012_bitemporal_facts.sql` twice and applies `006_rls_multitenant.sql` to minimal document/chunk/embedding tables; it requires no pgvector or Python driver.

Have the database administrator provision a **dedicated disposable test database**, install `btree_gist`, and create an existing reader role distinct from the connection role:

```sql
-- Run only in the dedicated test database, as its administrator.
CREATE EXTENSION IF NOT EXISTS btree_gist;
CREATE ROLE memory_test_reader NOLOGIN NOSUPERUSER NOBYPASSRLS;
GRANT memory_test_reader TO memory_test_owner;
```

`memory_test_owner` denotes your existing test connection role. It must have database `CREATE` permission and permission to `SET ROLE memory_test_reader`. Names above are examples; the runner takes the reader name explicitly. Do not grant the reader ownership or `BYPASSRLS`. There must be no default `app.tenant_id` setting on the connection. Provisioning is outside the runner; it never creates roles, databases, or installs dependencies. Use your approved secret loader to set `MEMORY_TEST_DSN`; do not place credentials in shell history or a checked-in file.

```bash
export MEMORY_TEST_ALLOW=dedicated-test-database
export MEMORY_TEST_RLS_ROLE=memory_test_reader
# MEMORY_TEST_DSN: a libpq URI, key=value connection string, or bare database name, from your secret loader.
# The runner splits it into PGHOST, PGUSER, PGPASSWORD, ... (libpq ignores a URI in PGDATABASE);
# unknown parameters stop the run rather than being dropped.
python3 skills/universal/ai-vector-brain/scripts/verify_postgres_memory.py
python3 skills/universal/ai-vector-brain/scripts/test_verify_postgres_memory.py
```

The DSN parser supports the explicitly mapped libpq environment parameters, UTF-8 URI values, and keyword values with libpq quoting/backslash escapes. URI `+` stays literal; encode spaces as `%20`. Malformed percent escapes, NUL, empty bracketed addresses, bracket suffix garbage, and unknown parameters fail before starting `psql`. This is a conservative subset, not a replacement for every libpq connection option or URI compatibility alias. Parser semantics follow the [official connection-string documentation](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING) and the [libpq parser source](https://github.com/postgres/postgres/blob/master/src/interfaces/libpq/fe-connect.c) (`conninfo_parse`, `conninfo_uri_parse_options`, `conninfo_uri_decode`).

The runner uses an unpredictable fresh schema inside one transaction and rolls back at completion. A connection failure, SQL error, assertion failure, or timeout closes the session and rolls back. It qualifies the asset's upgrade `DROP FUNCTION` with the scratch schema so an existing function in `public` cannot be touched. No backend errors or DSN are printed; the result is a small JSON record. Exit `0` requires server assertions and the completion marker; exit `1` means a backend/preflight/assertion failure; exit `2` means not run or inconclusive. Missing configuration or `psql` never produces a simulated success.

Coverage: insertion, reassignment, duplicate replay, agreeing late snapshot, historical backfill, lower-authority candidate holding, half-open as-of boundaries, JSON-null clearance versus unknown attributes, overlap rejection, exact nested reference matching, and the ordered erasure recipe with unrelated records preserved. RLS is exercised with a non-owner `NOSUPERUSER NOBYPASSRLS` role: separate tenant reads, rejected cross-tenant writes on all three tables, and missing/empty scope denial across all three fixture tables. Both tenants are seeded before enabling RLS and before setting the tenant variable: missing-scope reads therefore run against populated tables, and missing-scope writes must raise an authorization error. An allowed tenant write is a positive control. The empty-string read check runs after these populated checks.

The known-at check uses an explicitly seeded older `recorded_at`: PostgreSQL `now()` is constant throughout the rollback transaction. This tests the replay predicate and supersession behavior, **not** a replay across independently committed transactions. Concurrency, advisory-lock contention, query plans, ANN quality, physical erasure, and managed-provider permissions remain unmeasured. `012` has no tenant column or RLS policy: the `006` checks verify the retrieval-table template and do not prove isolation of a shared fact store. Use a schema/database per fact-store tenant or separately implement and verify a tenant-aware fact adapter before sharing it.
