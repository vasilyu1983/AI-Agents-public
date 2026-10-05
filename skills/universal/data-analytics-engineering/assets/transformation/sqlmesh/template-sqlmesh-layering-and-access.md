# SQLMesh Layering, Access Control & Postgres Operational Rules

*Purpose: Layer contracts, access-control macros, and Postgres-specific operational patterns that don't appear in upstream SQLMesh docs but show up in every production project. Pair with the per-model templates in this directory.*

## Layered Architecture Contracts

Pick the layer first, then a template. Each layer has a **read-from contract** that should not be violated.

### `stage` (and `stage_fincrime` / domain-scoped stage variants)

- **Reads only**: raw / source schemas. **Never** `intermediate` or any public-family layer.
- Avoid joins unless truly unavoidable.
- Do most non-join work here: casting, renaming, cleanup, normalization, source-local derivations.
- Prefer **table** materialization to decouple downstream models from source schema drift.
- Large tables → default to incremental kinds.

### `intermediate`

- **Reads only**: `stage`, other `stage_*` variants, and other `intermediate` models.
- Main integration layer — joins freely.
- Prefer wide, reusable business logic outputs over one-off reporting shapes.
- Add indexes for downstream join keys, common filters, identifiers.
- Add stable-output audits (see "Audit triad" below).
- Large tables → default to incremental.

### Public family: `public`, `public_limited`, `public_fincrime`, `sandbox`

- **Reads from**: `stage*`, `intermediate`, and other public-family models.
- Treat as **consumption layers** — wide, denormalized, BI- or controlled-exposure-ready.
- Prefer `VIEW` for thin pass-through / light derivation.
- Prefer **table** when the model is reused, expensive, audited, indexed, or a stable consumption surface.
- Prefer **incremental table** for large or frequently queried datasets.
- Require a `description "..."` in `MODEL (...)` and field-level comments on projected user-facing columns (including intentional masking, e.g. `"see users_personal table"`).
- Apply access-control macros (next section).

## Access Control — Use the Macros

Prefer repo macros over handwritten `GRANT` / `CREATE POLICY` SQL. Place all access blocks **at the end of the model file**.

```sql
-- end-of-file pattern
@grant_select_on_this_model_by_tags(['analytics', 'finance']);

@rls_policies(
    role='analyst',
    entity=true   -- filter rows by legal entity / protected scope
);
```

| Macro | When |
|---|---|
| `@grant_select_on_this_model_by_tags(...)` | All public-family models. Tag-driven grants are auditable; bare `GRANT` statements are not. |
| `@rls_policies(..., entity=true)` | Row filtering by legal entity or protected-personal scope is required. |
| `@rls_policies(..., entity=false)` | Need RLS-aware mechanics without legal-entity filtering. |

Default `public_fincrime` to fincrime-only grants unless the project's `access_rights.md` (or equivalent) explicitly requires broader access.

## Postgres Operational Rules

### 63-character identifier limit

PostgreSQL truncates identifiers at 63 chars. SQLMesh-generated index, constraint, and helper-model names can blow past this silently.

- Keep `CREATE INDEX` and constraint names short; abbreviate long model names.
- Watch helper-model names auto-generated for incremental kinds — those count too.

```sql
-- bad: silently truncated, may collide
CREATE INDEX idx_public_customer_lifetime_value_aggregate_by_legal_entity_v2 ON @this_model (legal_entity_id);

-- good
CREATE INDEX ix_pub_clv_agg_entity ON @this_model (legal_entity_id);
```

### Refresh stats after rebuild — guarded `ANALYZE`

For table models that benefit from fresh planner statistics after rebuild (heavy downstream joins or filters), use the guarded post-statement pattern. Place it **immediately before** any trailing `CREATE INDEX` block.

```sql
-- ... model query ...

@IF(@runtime_stage = 'evaluating', ANALYZE @this_model);

CREATE INDEX ix_pub_tx_account ON @this_model (account_id);
CREATE INDEX ix_pub_tx_ts ON @this_model (event_ts);
```

The `@runtime_stage = 'evaluating'` guard ensures `ANALYZE` only runs during the evaluation phase, not during planning/rendering.

### Block ordering at end of file

```
1. Model query
2. Guarded ANALYZE (if used)
3. CREATE INDEX statements
4. ON_VIRTUAL_UPDATE_BEGIN / ON_VIRTUAL_UPDATE_END block
5. Access-control macros (@grant_select_on_this_model_by_tags, @rls_policies)
```

## Stable-Output Audit Triad

For `intermediate` and public-family models, add audits when the output is stable enough to defend. Aim for at least one from each category that fits.

| Category | Audit | When |
|---|---|---|
| Uniqueness | `unique_values(columns := [...])` | Business keys expected to be unique |
| Freshness | `assert_positive_order_by` / freshness check on `updated_at` or `event_ts` | Model exposes a recency column |
| Volume | `row_count_for_date_range(...)` | Daily/monthly counts are stable enough to alarm on |

Don't add boilerplate audits to satisfy a template — they erode trust when they fire on noise.

## Validation Flow

Use the safest available validation, in order:

1. `sqlmesh render <model>` — inspect generated SQL without touching the DB.
2. `sqlmesh test` — model unit tests under `tests/`.
3. `sqlmesh plan <branch_env> --dry-run --verbose --no-prompts --auto-apply` — full lineage + categorization without applying.
4. Repo-standard helper script if one exists (e.g. `./test_sqlmesh.sh`) — wraps the above with project conventions.

## Branch / Environment Conventions

- Use a **dedicated test gateway** (e.g. `dwh_local_test`) for dry-run validation; do not validate against `prod` gateway from a dev machine.
- Branch-scoped SQLMesh environments default to the current git branch name.
- In CI, distinguish `sqlmesh plan <branch_env> --auto-apply` (updates a non-prod environment on the prod gateway — *not* a promotion) from `sqlmesh plan --auto-apply` (no env arg → targets `prod`).

## When to Override These Rules

A repo-specific rule may intentionally override these defaults — read the project's `access_rights.md`, `config.yaml`, and the nearest local example before editing. When the project's nearest working example disagrees with this template, follow the local example unless it's clearly broken.
