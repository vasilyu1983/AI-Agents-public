# PII Vault And Pseudonymisation

> Purpose: Vendor-neutral pattern catalog for separating direct identifiers from analytical facts so warehouses, BI tools, and LLM-fronted query surfaces can safely consume the data. Pairs with `contracts-catalogs-lineage.md` (column-level metadata) and the `../../agents-mcp/references/mcp-for-dwh.md` boundary (the LLM should hit pseudonymised columns by default). Freshness anchor: May 2026.

---
## Table of Contents

- [When To Use This](#when-to-use-this)
- [Column Classification Model](#column-classification-model)
- [The Vault Pattern](#the-vault-pattern)
- [Tokenisation Choice Tree](#tokenisation-choice-tree)
- [Role-Based Unmask Views](#role-based-unmask-views)
- [dbt Contract Integration](#dbt-contract-integration)
- [LLM-Context PII Boundary](#llm-context-pii-boundary)
- [Retention And Erasure Mechanics](#retention-and-erasure-mechanics)
- [Anti-Pattern Catalog](#anti-pattern-catalog)
- [Recipes](#recipes)
- [AI / Agent Readiness Checklist](#ai-agent-readiness-checklist)
- [Cross-References](#cross-references)

---

## When To Use This

Use this pattern when ANY of the following hold:

- Analytical tables carry personal data (employees, customers, counterparties)
- An LLM, agent, or non-employee role will query the warehouse
- Multiple purposes share the same underlying facts (purpose limitation requires separation by role)
- The organisation owes data-subject rights (access, erasure, portability) on warehouse data

Do NOT use when:

- The warehouse contains only synthetic or fully public data
- Direct identifiers ARE the analytical object (e.g. an identity-resolution table — that IS the vault, but never the primary BI surface)

---

## Column Classification Model

Every column lands in exactly one class.

| Class | What It Is | Vault Treatment |
|---|---|---|
| Direct identifier | Identifies a person on its own: email, phone, full name, government ID, employee ID from HR system, raw IP address | Vault-only; never in fact tables |
| Quasi-identifier | Does not identify alone but combines to identify: postcode, birth-date, job-title at team level, login-region plus device, age bracket plus postcode | Generalised or k-anonymised in marts; raw only in vault |
| Sensitive non-identifying | Not identifying but special-category content: salary band, health status, sentiment score, free-text content | Subject to its own access policy; separate from identifier vault |
| Non-sensitive analytical | Metrics, timestamps, product IDs, event types with no personal dimension | No vault treatment required |

Anti-pattern flag: treating quasi-identifiers as safe analytical columns is the most common privacy-enforcement trigger in recent regulatory guidance. A postcode plus a birth-date is routinely sufficient to re-identify.

---

## The Vault Pattern

```text
[ Raw source ] ──> [ Vault (direct identifiers) ] ──> [ Pseudonymisation function ]
                                                                │
                                                                v
                                                    [ Marts (pseudonymised facts) ]
                                                                │
                                              ┌─────────────────┴─────────────────┐
                                              v                                   v
                                    [ BI / LLM / Agents ]              [ Authorised role ]
                                    (pseud columns only,         (vault unmask join, audited,
                                     default access)              time-limited, purpose-tagged)
```

### Vault Schema (Canonical Shape)

`vault_person`:

| Column | Type | Purpose |
|---|---|---|
| `canonical_id` | UUID, primary key | Stable internal identity anchor |
| `pseud` | TEXT (HMAC or deterministic token) | What marts, BI, and LLM see |
| `source_system_ids` | JSON / VARIANT | Identity bridging: `{crm: ..., hr: ..., chat: ..., ticket: ...}` |
| `direct_identifiers` | Encrypted column or separate physical table | Email, name, phone — never in marts |
| `created_at` | TIMESTAMP | Vault row creation |
| `superseded_by` | UUID, nullable | Identity merge chain |
| `erasure_requested_at` | TIMESTAMP, nullable | Right-to-erasure trigger |

Marts NEVER join to the vault by `email` or `name`. The only permitted join keys are `canonical_id` (internal pipelines, with explicit role) and `pseud` (BI, LLM, agent access).

---

## Tokenisation Choice Tree

```text
Need to JOIN across marts on the same person?
  yes -> need a deterministic value
    Keys rotate? -> no  -> HMAC-SHA256(canonical_id, vault_key)
                -> yes -> deterministic AEAD with versioned key
  no -> random UUID per fact row (highest privacy, no cross-time joins)

Need to PRESERVE field format (e.g. card BIN + last 4 visible)?
  yes -> Format-Preserving Encryption (e.g. FF1)
  no  -> HMAC or random

Need to BE REVERSIBLE outside the vault?
  yes -> STOP. Reversibility outside the vault defeats the pattern.
  no  -> HMAC / FPE without key export
```

| Function | Joinable | Reversible | Format-Preserving | Use When |
|---|---|---|---|---|
| HMAC-SHA256 | Yes (with key) | No | No | Default for analytics joins; key stays in vault service |
| FPE (e.g. FF1) | Yes | Yes (with key) | Yes | Legacy BI requiring original field shape |
| Deterministic AEAD (versioned) | Yes (within key version) | Yes (with key) | No | Keys rotate periodically; versioned decryption |
| Random UUID per row | No | No | No | Per-event aggregates; no person-join required |

Prefer HMAC-SHA256 by default. Introduce FPE only when a downstream system cannot accept a changed field shape. Introduce reversibility only when the vault itself is the unmask surface — never in marts.

---

## Role-Based Unmask Views

```sql
-- Default mart view: pseudonymised only (BI, LLM, agent role)
CREATE VIEW mart.fact_session AS
  SELECT
    pseud          AS person_pseud,
    ts,
    duration_s,
    channel_pseud
  FROM raw.session;

-- Authorised unmask view: vault join with audit logging
CREATE VIEW sensitive.fact_session_unmasked AS
  SELECT
    v.email        AS person_email,
    s.ts,
    s.duration_s,
    s.channel_pseud
  FROM raw.session s
  JOIN vault.person v ON v.pseud = s.pseud
  WHERE current_role() IN ('hr_investigator', 'compliance_reviewer')
    AND audit.log_unmask_access(
          'fact_session',
          current_user(),
          current_query_id()
        );
```

Cross-vendor mapping:

| Platform | Role Enforcement | Masking Policy |
|---|---|---|
| Postgres | Row-level security policies + `current_role()` | Column masking via functions |
| Snowflake | Row access policies + dynamic data masking | Native masking policy objects |
| BigQuery | Column-level security + data masking + authorized views | IAM-bound masking rules |
| DuckDB | Macro-based masking layer + manual role check | No native policy engine; enforce at view level |

Rule: never rely on application-layer masking when the database supports policy enforcement. Application-layer masking is bypassable via direct connection.

---

## dbt Contract Integration

Mark every column with a `pii` classification in the model YAML:

```yaml
models:
  - name: fct_session
    config:
      contract:
        enforced: true
    columns:
      - name: person_pseud
        data_type: varchar
        meta:
          pii: direct_token   # pseudonymised direct identifier
      - name: ts
        data_type: timestamp
        meta:
          pii: none
      - name: duration_s
        data_type: integer
        meta:
          pii: none
```

Allowed `pii` values: `direct`, `direct_token`, `quasi`, `sensitive`, `none`.

CI enforcement rules:

- Any model NOT in `models/sensitive/` MUST have zero columns with `pii: direct`.
- Column-level lineage tools surface downstream PII propagation; treat propagation to a non-vault model as a test failure.
- Cross-reference `contracts-catalogs-lineage.md` for the full column-metadata contract pattern.

---

## LLM-Context PII Boundary

Non-negotiable rules when an LLM or agent reads the warehouse:

- LLM-facing roles (`role llm_agent` or equivalent) receive grants ONLY to pseudonymised views. No direct-identifier columns are accessible at all.
- The MCP or agent boundary (`../../agents-mcp/references/mcp-for-dwh.md`) enforces the role at the connection level — not in the prompt and not in the system instruction.
- Unmask requires a separate role, a separate query path, and an audit log entry. It cannot be triggered by the LLM itself.
- Prompt-side unmask requests ("expand pseud `p_a1b2` to the person's email") must be rejected by the agent layer, not just discouraged. The agent must not issue a vault-join query on behalf of an LLM turn.

Anti-pattern (most common LLM-warehouse PII leak): the LLM receives a pseudonymised value in query results, the user asks "who is `p_a1b2`?", and the agent issues a vault lookup to answer. This is a reversal channel through the LLM. Treat it identically to direct identifier exposure.

For multi-source ingestion where LLM context is assembled from warehouse data, see `../../ai-context-layer/references/multi-source-wiki-ingestion.md`.

---

## Retention And Erasure Mechanics

### Right-To-Erasure Pattern

1. Set `vault_person.erasure_requested_at = now()` for the `canonical_id`.
2. Null or crypto-shred the direct-identifier columns (delete the key version for AEAD-encrypted fields).
3. Retain the `pseud` value — marts remain functionally intact; no path back to the person exists.
4. Write an audit record: `{pseud, erasure_at, requested_by, purpose}`.
5. Document the re-erasure procedure for backup restores; a restored backup that contains unencrypted vault rows is a breach.

### Retention Class Table

Org sets actual retention windows. This table uses placeholder variables.

| Class | Vault Treatment | Mart Treatment |
|---|---|---|
| `transaction_records` | Encrypted retain; key rotated per schedule | Pseudonymised retain |
| `incident_records` | Encrypted retain | Pseudonymised retain |
| `investigation_records` | Encrypted retain | Pseudonymised retain |
| `routine_telemetry` | Short-window retain, then crypto-shred | Aggregate-only after window |

---

## Anti-Pattern Catalog

| Anti-Pattern | Consequence | Corrective Recipe |
|---|---|---|
| Email as join key in marts | Erasure breaks downstream joins; PII spreads across marts | Replace join key with `pseud`; backfill via Recipe R2 |
| Quasi-identifiers treated as safe | Re-identification trivial with two or three columns in combination | Classify quasi columns; generalise or k-anonymise in marts |
| Vault and mart in same schema; role separation by view only | Role bypass via direct table access on vault rows | Vault in a separate schema with no SELECT grant to mart roles |
| Prompt-side unmask | LLM becomes a PII reversal channel | Enforce at agent layer: reject vault-join queries initiated by LLM turns |
| Pseudonyms generated per ingest run (non-deterministic) | Cross-time joins silently break; identity stitching fails | Use deterministic HMAC or AEAD keyed on `canonical_id` |
| FPE used where HMAC suffices | Reversibility unnecessarily preserved; key compromise = full re-identification | Default to HMAC; introduce FPE only for legacy field-shape requirements |
| App-layer masking instead of DB-layer policy | Bypassable via direct connection | Enforce at DB policy layer; treat app masking as defence-in-depth only |
| Vault unmask view has no audit log | No trail for DSAR response or breach investigation | Audit log is a mandatory gate in the unmask view definition |
| Backup contains unencrypted vault rows | Restore = breach | Encrypt at-rest before backup; document re-erasure on restore |
| Reusing analytics pseudonyms as auth identifiers | Cross-domain identity leakage; pseud values leak into auth logs | Keep analytics and auth identity spaces strictly separate |

---

## Recipes

### R1 — Stand Up Vault And Pseudonymisation For A New Mart

1. Classify every column in the target mart: `direct`, `quasi`, `sensitive`, or `none`.
2. Choose tokenisation per direct-identifier column using the choice tree: default HMAC-SHA256.
3. Create `vault.person` schema and table; encrypt direct-identifier columns at rest.
4. Define the `canonical_id` -> `pseud` mapping function as a vault-internal service or SQL function with key access restricted to the vault schema role.
5. Build the mart with `pseud` as the only person reference; run the column-level CI test confirming zero `pii: direct` columns outside `models/sensitive/`.
6. Create the role matrix: `llm_agent` and `bi_analyst` get mart grants; `hr_investigator` and `compliance_reviewer` get the audited unmask view grant.
7. Create the audit log table: `{unmask_view, queried_by, query_id, ts, purpose}`.
8. Add dbt column metadata (`meta: {pii: ...}`) and enforce in CI.

### R2 — Migrate An Existing Mart To Pseudonymised

1. Snapshot the current mart to a versioned backup table.
2. Stand up `vault.person` and populate it from the current email / name columns: generate `canonical_id` and `pseud` for every distinct person.
3. Backfill: add `pseud` column to the mart alongside the existing direct-identifier columns (dual-write window).
4. Update all downstream consumers to use `pseud` as the join key; validate query results against the snapshot for a designated overlap window.
5. Cut over reads: point BI, LLM, and agent roles to the pseudonymised mart view.
6. Cut over writes: pipelines write `pseud` only; direct-identifier columns become write-blocked.
7. Drop direct-identifier columns from the mart after the cutover window closes.
8. Run the CI test confirming no `pii: direct` columns remain; close the migration record.

### R3 — Add LLM Or Agent Access To An Existing Warehouse

1. Create a dedicated `llm_agent` database role with SELECT grants on pseudonymised mart views only.
2. Configure the MCP or agent connection to enforce `llm_agent` role at connection time (`../../agents-mcp/references/mcp-for-dwh.md`).
3. Enforce query budget and timeout at the database level (statement timeout, row-count cap) — not only in the agent prompt.
4. Enable the audit log table; route query logs for the `llm_agent` role to it.
5. Run an adversarial eval: attempt to retrieve a direct identifier through the LLM interface; confirm the warehouse returns no rows.
6. Add the eval as a CI test that runs on every warehouse permission change.

### R4 — Handle A Right-To-Erasure Request

1. Receive the request; look up the `canonical_id` in `vault.person` via the internal identity bridge (not via the mart).
2. Set `erasure_requested_at` and begin the crypto-shred: null direct-identifier columns and delete the associated key version.
3. Write the erasure audit record: `{pseud, erasure_at, requested_by, canonical_id_hash}`.
4. Verify downstream mart queries for the `pseud` return no personal data (should return only aggregated facts).
5. Document backup re-erasure: log that the backup taken before `erasure_at` contains personal data and must be re-erased on restore.

---

## AI / Agent Readiness Checklist

- [ ] Every column in shared marts is classified (`direct`, `direct_token`, `quasi`, `sensitive`, `none`) in the dbt model YAML
- [ ] No `pii: direct` column exists outside `vault.*` and `models/sensitive/` — CI test enforces this
- [ ] LLM and agent roles hold grants only to pseudonymised views; no vault-schema grants
- [ ] MCP or agent connection enforces the restricted role at connection level, not prompt level
- [ ] Unmask views include an audit log gate that fires on every query
- [ ] A right-to-erasure procedure is documented and tested; crypto-shred is the default mechanism
- [ ] Backup restore triggers a re-erasure check before the backup goes live
- [ ] Quasi-identifier combinations have been reviewed for re-identification risk
- [ ] Prompt-side unmask is blocked at the agent layer and covered by an adversarial CI eval
- [ ] Column-level lineage is available to trace PII propagation to downstream models

---

## Cross-References

- `contracts-catalogs-lineage.md` — Column-level metadata, ownership, and lineage for governed assets
- `metric-governance.md` — Certification and versioning discipline for metrics that join to pseudonymised facts
- `../../agents-mcp/references/mcp-for-dwh.md` — MCP boundary enforcement for LLM warehouse access
- `../../ai-context-layer/references/multi-source-wiki-ingestion.md` — Context assembly from warehouse data for LLM surfaces
