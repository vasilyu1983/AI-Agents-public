# Migration Strategies

Use this file when the request is about changing schema in production.

## Default Safe Pattern

1. Expand: add nullable column, new table, or compatible index.
2. Backfill: migrate data in batches.
3. Dual-write or dual-read if needed.
4. Contract: remove old path only after cutover is verified.

## Rules

- Separate schema migration from long-running backfill.
- Make migrations idempotent where possible.
- Avoid destructive changes in the same deploy as application cutover.
- For large tables, prefer online/index-concurrent strategies the engine supports.
- Run migration DDL through a direct (non-pooled) connection where the tool supports it — session-level settings like `statement_timeout` and `lock_timeout` are not guaranteed to survive a transaction-mode pooler reassigning the backend connection mid-migration.

## PostgreSQL Lock Levels (verify against the target version before relying on this)

Every plain `ALTER TABLE` sub-command takes at least some table-level lock; the risk is duration, not the lock's existence:

| Operation | Lock | Duration |
|---|---|---|
| `ADD COLUMN` (nullable, no default, or constant default) | `ACCESS EXCLUSIVE` | Milliseconds — metadata-only since Postgres 11, no table rewrite |
| `ADD COLUMN ... DEFAULT <volatile/expression>` | `ACCESS EXCLUSIVE` | Full table rewrite — scales with table size, treat as high-risk |
| `ALTER COLUMN TYPE` (incompatible type) | `ACCESS EXCLUSIVE` | Full table rewrite |
| `SET NOT NULL` (no pre-existing validated constraint) | `ACCESS EXCLUSIVE` | Full table scan to verify no NULLs — scales with table size |
| `ADD CONSTRAINT ... CHECK (...) NOT VALID` | `ACCESS EXCLUSIVE` | Milliseconds — skips the verification scan |
| `VALIDATE CONSTRAINT` (the deferred scan for the above) | `SHARE UPDATE EXCLUSIVE` | Scan runs, but concurrent reads/writes proceed |
| `CREATE INDEX` | `SHARE` | Blocks writes for the build duration |
| `CREATE INDEX CONCURRENTLY` | `SHARE UPDATE EXCLUSIVE` | Slower build, but reads/writes proceed |
| `DROP TABLE`, `TRUNCATE`, `VACUUM FULL`, `CLUSTER` | `ACCESS EXCLUSIVE` | Full duration of the operation |

**The `SET NOT NULL` skip-scan pattern (Postgres 12+):** add the constraint as `NOT VALID` first (instant), `VALIDATE CONSTRAINT` separately (lighter lock, concurrent-safe), then `SET NOT NULL` — Postgres reuses the validated constraint and skips its own redundant scan. This is the standard way to add `NOT NULL` to a populated column on a large table without a blocking full-table-scan window.

## High-Risk Changes

- Column type changes on hot tables (triggers a full rewrite and `ACCESS EXCLUSIVE` for the duration)
- `ADD COLUMN` with a volatile or expression default (also a full rewrite — a constant default is metadata-only and safe)
- Renames without compatibility layer
- Dropping columns still referenced by old code paths
- Backfills that lock large tables or saturate replicas
- `SET NOT NULL` without the `NOT VALID` → `VALIDATE CONSTRAINT` → `SET NOT NULL` sequence on a large, populated table

## Hyrum's Law and the Adds-vs-Drops Rule

Hyrum's Law: with enough consumers of a schema, every observable property — a column's existence, its name, its nullability, even its NULL-vs-empty-string convention — becomes something someone depends on, whether or not it was ever a documented contract. This is why expand/contract is a *deploy-sequencing* discipline, not just a naming convention for the three phases:

- **Adds are safe in any deploy.** A new nullable column or new table changes nothing an existing consumer already observes — nothing to violate.
- **Drops and renames are never safe in the same deploy as the add they pair with.** A rename is a drop wearing an add's clothes: `name` → `full_name` is not one step, it's expand (add `full_name`, dual-write both), migrate (backfill, cut reads over, verify), then contract (stop writing `name`, drop `name` in a *separate, later* deploy) — five numbered steps across at least two deploys, never collapsed into one.
- **The gate for contract is "no code references the old shape," not "the new shape looks done."** Verify via a grep/query audit of read paths (application code, reporting queries, downstream consumers) before dropping — the old column looking unused in your own codebase doesn't mean an out-of-band consumer isn't depending on it.
- Treat a migration with no tested `down` path the same as a deploy that can't be rolled back — don't ship expand or migrate steps you haven't verified you can reverse.

Source: adapted from addyosmani/agent-skills, `skills/deprecation-and-migration.md` (MIT), commit `7676817`, 2026-08-09.
