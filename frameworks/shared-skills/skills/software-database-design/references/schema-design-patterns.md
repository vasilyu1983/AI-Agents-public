# Schema Design Patterns

Use this file when the request is about table shape, entity boundaries, or long-lived schema evolution.

## Core Relational Patterns

- Normalize by default for transactional data.
- Denormalize only when the read path proves it is necessary.
- Prefer explicit join tables for many-to-many relations when metadata or history matters.
- Use foreign keys unless there is a concrete, measured reason not to.

## Common Shapes

| Pattern | Use When | Notes |
|---|---|---|
| Tenant column | Most SaaS multi-tenancy | Simpler than per-tenant schema, needs strong indexing and RLS if used |
| Join table | Many-to-many relation | Keep business metadata on the join when needed |
| Append-only audit table | Compliance or history matters | Separate from primary hot-path table when possible |
| Soft delete | Recovery or legal retention matters | Add explicit cleanup/reporting plan; do not use by reflex |
| Event table | Immutable business facts | Pair with snapshots/materialized read models for performance |
| Temporal / system-versioned table | Need to answer "what did this row look like at time T" | See Temporal/Audit Patterns below — no mainstream relational engine except SQL Server and MariaDB has this natively; Postgres and MySQL need an explicit pattern |

## Temporal / Audit Table Patterns

Pick based on what question the system must answer later — these are not interchangeable:

- **Append-only audit log** (event sourcing lite): a separate `*_events` or `*_audit` table, one row per change, storing `(entity_id, changed_at, changed_by, field, old_value, new_value)` or a full before/after snapshot as JSON. Answers "what happened and when" and "who did it." Cheapest to build; does not let you efficiently query "what was the full row state at time T" without replaying events.
- **System-versioned (temporal) table**: every row carries `valid_from`/`valid_to` (or `sys_period` as a range type), and updates insert a new row + close out the old one instead of overwriting. Answers "what did the full entity look like at time T" directly with a `WHERE valid_from <= T AND valid_to > T` predicate. SQL Server and MariaDB support this as a native `SYSTEM VERSIONING` feature; PostgreSQL and MySQL require building it with triggers, a range type (`tstzrange` in Postgres), or an extension — budget for that build cost, it is not a checkbox.
- **Soft delete is a narrower tool, not a temporal pattern**: a `deleted_at TIMESTAMP` only answers "is this row currently considered deleted," not "what did it look like before." Don't reach for soft delete when the actual requirement is audit history — that needs one of the two patterns above. Soft delete earns its complexity (every query must remember to filter it, every unique constraint must account for it) only when there's a real recovery window or legal retention requirement; default to hard delete otherwise and let the audit log (if one exists) carry the history.

## Identifier Guidance

- Prefer integer or time-ordered identifiers for clustered indexes and write-heavy tables.
- Use UUIDs when cross-system generation or client-side generation matters.
- Be consistent: mix fewer identifier strategies, not more.
- See the primary-key trade-off note in `SKILL.md` (Anti-Patterns section) for the concrete bigint-vs-UUIDv7 decision — it is a real trade-off between insert locality/index size and distributed-generation needs, not a default to apply by reflex.
