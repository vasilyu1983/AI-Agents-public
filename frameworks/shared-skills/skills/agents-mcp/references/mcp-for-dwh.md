# MCP for Data Warehouses

> Vendor-neutral patterns for connecting an LLM/agent to a structured data store via MCP without giving the model production write access, raw PII, or unbounded query budgets. The store can be a warehouse (Postgres, Snowflake, BigQuery, DuckDB, Redshift), a BI semantic layer (Metabase, Looker, Cube, dbt Semantic Layer), or an OLAP system (ClickHouse, Druid).

---

## Table of Contents

- [When MCP-for-DWH is the right answer](#when-mcp-for-dwh-is-the-right-answer)
- [Pattern catalog: three MCP shapes for a DWH](#pattern-catalog-three-mcp-shapes-for-a-dwh)
- [Selection matrix](#selection-matrix)
- [The 7 enforcement layers](#the-7-enforcement-layers)
- [Worked tool schema: Shape A — managed BI MCP](#worked-tool-schema-shape-a--managed-bi-mcp)
- [Worked tool schema: Shape B — DB-driver MCP](#worked-tool-schema-shape-b--db-driver-mcp)
- [Worked tool schema: Shape C — custom thin MCP](#worked-tool-schema-shape-c--custom-thin-mcp)
- [Audit log table](#audit-log-table)
- [Anti-pattern catalog](#anti-pattern-catalog)
- [Recipes](#recipes)
- [Vendor mapping](#vendor-mapping)
- [Composition](#composition)
- [Check](#check)

---

## When MCP-for-DWH is the right answer

Use when:

- An agent needs to answer questions grounded in a structured store, not just documents.
- The store has stable schemas and is the source of truth for the org's metrics, events, or entities.
- The org needs an auditable record of every model-to-data query for compliance or incident review.
- Multiple agents or agent purposes need data access and per-purpose isolation matters.

Do NOT use when:

- The agent only needs documents or unstructured text — use a retrieval MCP (RAG pattern) instead.
- The store is the system of record for live transactions and the agent might mutate it — write paths must not go through MCP without explicit review tooling and human approval gates.
- The store is per-tenant and per-tenant isolation is not enforced at the DB layer; app-layer isolation is not sufficient once the LLM can compose queries.
- The question can be answered by a pre-computed export or a scheduled report — do not build MCP infrastructure for a cron job.

---

## Pattern catalog: three MCP shapes for a DWH

### Shape A — Managed BI MCP (semantic layer in front)

The MCP server fronts a BI or semantic layer. The LLM calls governed metric and dimension tools; the semantic layer translates those calls into SQL and applies its own row/column policies.

Example fits: Metabase MCP, Cube MCP, a custom MCP wrapping a dbt Semantic Layer API.

**Pros:** Semantic layer already enforces metric definitions, join paths, and (often) row/column policies. LLM sees governed metrics, not raw tables. Smallest blast radius — if the semantic layer is right, the LLM cannot construct a query the semantic layer would reject.

**Cons:** LLM is constrained to pre-defined metrics. Ad-hoc exploration is limited. Adding a new metric is a separate semantic layer workflow, not an agent task.

**Right when:** The org already has a mature semantic layer and the agent's job is metric retrieval or dashboard narration, not exploration.

---

### Shape B — DB-driver MCP (direct connection, scoped role)

The MCP server holds a DB credential for a dedicated read-only role and exposes tools that let the LLM describe the schema and execute SELECT statements.

Example fits: Postgres MCP server, Snowflake MCP server, BigQuery MCP server.

**Pros:** Full SQL expressiveness. The vendor's own RBAC, RLS, and CLS mechanisms enforce guardrails at the DB layer. Good fit for analytical exploration where the query space is not fully enumerable in advance.

**Cons:** LLM writes arbitrary SQL. Must be locked to a read-only role, capped by statement timeout, capped by result-row count, and capped by cost budget on metered warehouse engines. Schema discovery tools can leak org structure if not scoped to an allow-list.

**Right when:** Agent must explore a stable warehouse and the team can properly lock down the role with the vendor's native access controls.

---

### Shape C — Custom thin MCP (purpose-built tools)

The MCP server exposes 5–15 named tools, each wrapping one parameterised query. The LLM never sees SQL; it calls tools with typed arguments.

Example fits: A fraud analytics MCP with tools like `risk_score_for_entity`, `top_n_signals`, `case_count_by_disposition`.

**Pros:** Smallest LLM surface area. Each tool is a reviewed, versioned contract. No SQL injection surface. Strongest auditability — every tool call maps to a known query that was reviewed before deployment.

**Cons:** Every new question requires a new tool and a new deployment. Slow to evolve. Bad fit for ad-hoc exploration or any domain where the question space is not known in advance.

**Right when:** High-stakes domain (finance, compliance, fraud, clinical) where every possible query must be reviewed and approved before the model can run it.

---

## Selection matrix

| Need | A) Managed BI MCP | B) DB-driver MCP | C) Custom thin MCP |
|---|---|---|---|
| Pre-governed metrics and joins | Yes | Partial | Yes (if encoded) |
| Ad-hoc SQL exploration | No | Yes | No |
| Smallest LLM surface | Partial | No | Yes |
| Auditability per query | Yes | Partial | Yes |
| Speed to add new questions | Partial | Yes | No |
| Cost capping (metered warehouse) | Yes | Manual | Yes |
| PII boundary enforced at MCP layer | Depends on BI config | Yes (DB role) | Yes |
| Right for high-stakes regulated domain | Partial | No | Yes |
| Works without an existing semantic layer | No | Yes | Yes |

---

## The 7 enforcement layers

Every shape requires all 7. "The MCP server is read-only" is not sufficient — each layer defends a different failure mode.

### Layer 1 — Read-only at the DB layer

The MCP role must be read-only in the database itself, not by trusting the LLM to send only SELECTs.

```sql
-- Postgres: create a dedicated permission role, then a login user that assumes it
create role llm_agent nologin;
create role llm_agent_user login password '<from-secret-vault>';
grant llm_agent to llm_agent_user;
revoke create on schema analytics from llm_agent;
revoke insert, update, delete, truncate, alter table on all tables in schema analytics from llm_agent;
-- Grant only what is needed
grant usage on schema analytics to llm_agent;
grant select on table analytics.orders_summary, analytics.user_cohorts to llm_agent;
```

Shape A enforcement: the BI layer's own role. Verify its effective grants before relying on the semantic layer.

Shape B enforcement: the scoped DB role above. Validate with `\dp` (Postgres) or `SHOW GRANTS` (Snowflake).

Shape C enforcement: the parameterised query runner in the MCP server never accepts raw SQL from the LLM.

### Layer 2 — Schema and collection scoping

The role sees only the allow-listed schemas, collections, or semantic models. Default deny on everything else.

```sql
-- Postgres: grant USAGE on specific schemas only
grant usage on schema analytics to llm_agent;
-- Not: grant usage on schema public, raw, pii_vault to llm_agent;
```

For Shape B, the `list_tables` tool must filter by an allow-listed schema set, not expose `information_schema` or system schemas.

### Layer 3 — Row and column policies (RLS / CLS)

Per-row policy filters by tenant, department, or sensitivity tag. Direct identifiers are blocked at the column policy level.

```sql
-- Postgres row-level security example
alter table analytics.orders_summary enable row level security;
create policy tenant_isolation on analytics.orders_summary
  using (tenant_id = current_setting('app.current_tenant')::uuid);
```

The MCP server sets the session variable before executing any query. It does not expose the variable-setting mechanism as a tool.

### Layer 4 — Pseudonym boundary

Direct identifiers (name, email, national ID, account number) must never be returned to the MCP client. The boundary is enforced in the DB role's column grants and in the semantic layer's column policies — not in a prompt instruction to the LLM.

See: [`../../data-analytics-engineering/references/pii-vault-and-pseudonymisation.md`](../../data-analytics-engineering/references/pii-vault-and-pseudonymisation.md)

The pseudonym lookup tool, if it exists, lives on a separate MCP server with its own role, its own audit log, and human-in-the-loop approval before any lookup executes.

### Layer 5 — Query budgets

| Budget type | Postgres example | Snowflake example | BigQuery example |
|---|---|---|---|
| Statement timeout | `SET statement_timeout = '30s'` | `ALTER SESSION SET STATEMENT_TIMEOUT_IN_SECONDS = 30` | per-job timeout in job config |
| Max rows returned | Server-side `LIMIT` injection | Server-side `LIMIT` injection | `maxResults` in query config |
| Max bytes scanned | Not native; use result row limit | `BYTES_SCANNED_LIMIT` in warehouse config | `maximumBytesBilled` in query config |
| Max concurrent queries | PgBouncer pool size | warehouse multi-cluster config | BigQuery slot reservations |

The MCP server injects `LIMIT` if the LLM omits it. It does not trust the LLM to self-limit.

### Layer 6 — Audit log contract

Every MCP tool call produces one row in an append-only audit table (schema in the [Audit log table](#audit-log-table) section). The audit table must not be readable by the MCP role — log writes go through a separate append-only writer credential or a log forwarder.

Minimum fields: `call_id`, `ts`, `mcp_tool`, `params_redacted`, `sql_hash`, `rows_returned`, `duration_ms`, `agent_id`, `session_id`, `prompt_hash`, `error_code`.

Raw SQL is never logged. Log the hash; investigators with elevated access reconstruct from session and prompt.

### Layer 7 — Connection-string secrecy

The MCP server holds the DB credential. The LLM never sees the connection string, the role name, or the schema list outside what the MCP exposes via a `discover` or `list_tables` tool (which is itself scoped to the allow-list).

```bash
# Correct: credential in environment, not in prompt or tool description
DATABASE_URL=postgresql://llm_agent_user:secret@host:5432/warehouse
```

The credential must not appear in tool descriptions, error messages, or log output. If the MCP server logs connection errors, redact the DSN before writing the log line.

---

## Worked tool schema: Shape A — managed BI MCP

```json
{
  "name": "list_collections",
  "description": "List available metric collections (governed models) the agent may query.",
  "input_schema": {
    "type": "object",
    "properties": {}
  }
}
```

```json
{
  "name": "describe_metric",
  "description": "Return the definition, dimensions, and allowed filters for a single metric.",
  "input_schema": {
    "type": "object",
    "required": ["metric_id"],
    "properties": {
      "metric_id": {
        "type": "string",
        "description": "Metric identifier as returned by list_collections."
      }
    }
  }
}
```

```json
{
  "name": "run_governed_metric",
  "description": "Execute a governed metric query. The semantic layer enforces joins, row policies, and column policies.",
  "input_schema": {
    "type": "object",
    "required": ["metric_id", "dimensions", "filters", "time_range"],
    "properties": {
      "metric_id": { "type": "string" },
      "dimensions": {
        "type": "array",
        "items": { "type": "string" },
        "description": "Dimension names to group by. Must be members of the metric's allowed dimension set."
      },
      "filters": {
        "type": "array",
        "items": {
          "type": "object",
          "required": ["field", "operator", "value"],
          "properties": {
            "field": { "type": "string" },
            "operator": { "type": "string", "enum": ["eq", "neq", "gt", "lt", "in", "between"] },
            "value": {}
          }
        }
      },
      "time_range": {
        "type": "object",
        "required": ["start", "end"],
        "properties": {
          "start": { "type": "string", "format": "date" },
          "end": { "type": "string", "format": "date" }
        }
      }
    }
  }
}
```

---

## Worked tool schema: Shape B — DB-driver MCP

```json
{
  "name": "list_tables",
  "description": "List tables available to the agent in the allow-listed schemas.",
  "input_schema": {
    "type": "object",
    "properties": {
      "schema": {
        "type": "string",
        "description": "Filter to a specific schema. If omitted, returns tables from all allowed schemas."
      }
    }
  }
}
```

```json
{
  "name": "describe_table",
  "description": "Return column names, types, and descriptions for a table. Never returns PII-tagged columns.",
  "input_schema": {
    "type": "object",
    "required": ["schema", "table"],
    "properties": {
      "schema": { "type": "string" },
      "table": { "type": "string" }
    }
  }
}
```

```json
{
  "name": "execute_select",
  "description": "Execute a read-only SELECT query. The server rejects non-SELECT statements, injects LIMIT if absent, and enforces a statement timeout.",
  "input_schema": {
    "type": "object",
    "required": ["sql"],
    "properties": {
      "sql": {
        "type": "string",
        "description": "A pure SELECT statement. DML, DDL, and CTEs that call write functions are rejected server-side."
      },
      "max_rows": {
        "type": "integer",
        "default": 1000,
        "maximum": 10000,
        "description": "Row cap applied server-side. The server enforces this even if the SQL omits LIMIT."
      }
    }
  }
}
```

Server-side validation for `execute_select`:

1. Parse the SQL into an AST. Reject if the statement type is not `SELECT`.
2. Reject any statement containing `INSERT`, `UPDATE`, `DELETE`, `DROP`, `CREATE`, `COPY`, or `pg_read_file` equivalents even inside CTEs.
3. If no `LIMIT` clause is present, inject `LIMIT {max_rows}`.
4. Set `statement_timeout` for the session before executing.
5. Record the query hash, row count, and duration in the audit log.

---

## Worked tool schema: Shape C — custom thin MCP

Each tool wraps one parameterised query reviewed and approved before deployment.

```json
{
  "name": "risk_score_for_entity",
  "description": "Return the current composite risk score and contributing signal counts for one entity over a time window.",
  "input_schema": {
    "type": "object",
    "required": ["entity_id", "window_days"],
    "properties": {
      "entity_id": { "type": "string" },
      "window_days": { "type": "integer", "minimum": 1, "maximum": 90 }
    }
  }
}
```

```json
{
  "name": "top_n_signals",
  "description": "Return the top N signals by severity for a pack and time window.",
  "input_schema": {
    "type": "object",
    "required": ["pack", "n", "window_days"],
    "properties": {
      "pack": { "type": "string" },
      "n": { "type": "integer", "minimum": 1, "maximum": 50 },
      "window_days": { "type": "integer", "minimum": 1, "maximum": 90 }
    }
  }
}
```

```json
{
  "name": "case_count_by_disposition",
  "description": "Return case counts grouped by disposition category for a time window.",
  "input_schema": {
    "type": "object",
    "required": ["window_days"],
    "properties": {
      "window_days": { "type": "integer", "minimum": 1, "maximum": 365 },
      "group_by": {
        "type": "string",
        "enum": ["disposition", "team", "product_line"],
        "default": "disposition"
      }
    }
  }
}
```

```json
{
  "name": "metric_trend",
  "description": "Return a time-series of a single metric aggregated by day.",
  "input_schema": {
    "type": "object",
    "required": ["metric_id", "start_date", "end_date"],
    "properties": {
      "metric_id": { "type": "string" },
      "start_date": { "type": "string", "format": "date" },
      "end_date": { "type": "string", "format": "date" }
    }
  }
}
```

```json
{
  "name": "entity_event_count",
  "description": "Return event counts for an entity by event type over a window. No raw event rows returned.",
  "input_schema": {
    "type": "object",
    "required": ["entity_id", "window_days"],
    "properties": {
      "entity_id": { "type": "string" },
      "window_days": { "type": "integer", "minimum": 1, "maximum": 90 },
      "event_types": {
        "type": "array",
        "items": { "type": "string" },
        "description": "If omitted, returns counts for all permitted event types."
      }
    }
  }
}
```

---

## Audit log table

```sql
create table mcp_audit (
  call_id      uuid        primary key default gen_random_uuid(),
  ts           timestamptz not null default now(),
  mcp_tool     text        not null,
  params_redacted jsonb    not null,
  sql_hash     text,                          -- sha256 of the executed SQL; null for Shape C tools
  rows_returned int,
  duration_ms  int,
  agent_id     text        not null,
  session_id   text        not null,
  prompt_hash  text,                          -- hash of the triggering prompt turn; set by the agent harness
  error_code   text
);

create index mcp_audit_ts       on mcp_audit (ts);
create index mcp_audit_agent_ts on mcp_audit (agent_id, ts);
create index mcp_audit_session  on mcp_audit (session_id, ts);
```

`params_redacted`: before writing, redact any user-provided string fields that might carry direct identifiers. Apply the same pseudonym substitution used in the data layer — do not log raw IDs if those IDs are direct identifiers.

`sql_hash`: log `encode(sha256(sql::bytea), 'hex')` (Postgres). Never log raw SQL in the audit table. Elevated-access investigators reconstruct the query from session context and prompt hash.

The MCP role has no `SELECT` grant on `mcp_audit`. Writes go through a separate append-only writer role or a log forwarder. The audit table itself must live in a schema the MCP role cannot see.

---

## Anti-pattern catalog

| Anti-pattern | Consequence | Corrective recipe |
|---|---|---|
| Trust the LLM to send only SELECTs | Data loss or corruption on the first prompt-injection that includes a DELETE | DB-side read-only role; server-side AST rejection of non-SELECT |
| Connection string in the system prompt or tool description | Credential leak via prompt injection or log exfiltration | Credential in MCP server environment only; redact from all log output |
| MCP role with `SELECT *` on entire schema | Direct-identifier PII leak; audit log reveals org structure | Column-level grants; deny direct-identifier columns explicitly |
| No statement timeout | Runaway query holds a warehouse slot or triggers a full table scan cost spike | DB-level timeout + MCP-level query budget per session |
| Audit log readable by the MCP role | LLM can inspect its own audit trail and adapt around controls; sensitive prompts or redacted params may leak | Separate append-only writer role; MCP role has zero access to audit schema |
| One shared MCP role across multiple agent purposes | Cross-purpose data leak; audit log cannot distinguish agent intent | One role per purpose; per-agent `session_id` tag in every audit row |
| Prompt-side pseudonym unmask | LLM acts as a reversal channel — pseudonym + context in one window reconstructs PII | Pseudonym lookup is its own tool on its own server with its own role and approval gate |
| Schema discovery via wildcard `information_schema` | Leaks full org table inventory including tables the agent has no business knowing exist | Allow-list schemas and tables in the `list_tables` tool; never expose `information_schema` |
| Bypassing the BI semantic layer when Shape A is available | Re-implements metric governance badly; joins and filters diverge from the semantic layer's definitions | If the BI semantic layer exists, prefer Shape A; extend it rather than going around it |
| No per-query cost cap on metered warehouse engines | A single agent loop triggers a multi-thousand-dollar scan | `maximumBytesBilled` (BigQuery) or warehouse-level cost controls; fail the query, not the budget |

---

## Recipes

### R1 — Stand up Shape B (DB-driver MCP) for read-only exploration

1. Create a dedicated permission role plus login user: `create role llm_agent nologin; create role llm_agent_user login; grant llm_agent to llm_agent_user;`
2. Grant `USAGE` on the allow-listed schemas only; do not grant `USAGE` on raw, PII, or system schemas.
3. Grant `SELECT` on specific tables (pseudonymised columns only); use column-level grants to deny direct-identifier columns.
4. Revoke all write capabilities explicitly: `REVOKE INSERT, UPDATE, DELETE, TRUNCATE, ALTER TABLE ON ALL TABLES IN SCHEMA analytics FROM llm_agent;`
5. Set role-level timeouts: `ALTER ROLE llm_agent SET statement_timeout = '30s'; ALTER ROLE llm_agent SET idle_in_transaction_session_timeout = '10s';`
6. Create the audit table in a schema the role cannot access; create the append-only writer role.
7. Configure the MCP server with the role's credential via environment variable; verify with `list_tables` that only allow-listed tables appear.
8. Smoke test: attempt a `DROP TABLE` via `execute_select`; confirm rejection; attempt a query without `LIMIT`; confirm the server injects one.

### R2 — Add Shape A (managed BI MCP) on top of an existing semantic layer

1. Enumerate the metric and dimension allow-list: only expose metrics that have a documented owner and a verified row/column policy in the semantic layer.
2. Verify that the semantic layer's underlying role satisfies Layers 1–4 (read-only, scoped, RLS, pseudonym boundary).
3. Build or configure the MCP server to expose `list_collections`, `describe_metric`, and `run_governed_metric` only.
4. Add the audit log call on every `run_governed_metric` invocation; the semantic layer's own query log is not a substitute.
5. Smoke test: attempt to retrieve a metric that references a PII-tagged column; confirm the semantic layer's column policy blocks it at the DB layer, not just in the prompt.
6. Run a load test with `max_rows` and a per-session query budget; confirm the budget cap fires before the warehouse cost cap.

### R3 — Migrate from Shape B to Shape C as risk increases

1. Export the top-N actual queries from the Shape B audit log for the past 30 days.
2. Convert each into a parameterised tool with typed input schema and an inline reviewed SQL template.
3. Deploy Shape C alongside Shape B (do not cut over yet); run both for one week with the same agent traffic.
4. Compare audit logs: confirm Shape C covers all high-frequency queries; identify gaps and add tools for them.
5. Freeze Shape B: revoke the `execute_select` tool from the agent's tool list in the MCP config.
6. Keep the Shape B audit log for forensic use; do not drop it.
7. After 30 days with no Shape B queries, decommission the Shape B role from the DB.

### R4 — Per-purpose role isolation

1. Identify distinct agent purposes that currently share one role: e.g. `agent_fincrime`, `agent_comms_triage`, `agent_kpi_reporting`.
2. Create one DB role per purpose; grant only the schemas and tables each purpose legitimately needs.
3. Deploy one MCP server instance per purpose; each holds only its own role's credential.
4. Tag every audit row with `agent_id` and verify in the audit log that the tags are populated before promoting to production.
5. Validate that `agent_fincrime` cannot call any tool that would return data scoped to `agent_kpi_reporting`'s tables.
6. Document the role-to-purpose mapping in the server's `data/sources.json`; include the grant review date.

---

## Vendor mapping

| Capability | Postgres | Snowflake | BigQuery | DuckDB |
|---|---|---|---|---|
| Read-only role | `REVOKE INSERT, UPDATE, DELETE` on role | `OWNERSHIP` / `USAGE` / `SELECT` grant separation; no write privileges | IAM `roles/bigquery.dataViewer` on dataset | Grant via macro; no native role system |
| Statement timeout | `statement_timeout` session variable | `STATEMENT_TIMEOUT_IN_SECONDS` in session parameters | Per-query `timeoutMs` in job config | `PRAGMA threads`; no native timeout |
| Row-level security | Native RLS policies (`CREATE POLICY`) | Row access policies | Row access policies on table | Application-layer `WHERE` clause; no native RLS |
| Column-level security | Column-level `GRANT SELECT (col)` | Dynamic data masking policies | Column-level security policies | Application-layer column filter; no native CLS |
| Audit log | `pgaudit` extension or `log_statement = 'all'` | `QUERY_HISTORY` / `ACCESS_HISTORY` views | Cloud Audit Logs (Data Access log type) | Application-layer logging only |
| Query cost cap | Not native; use row limit + timeout | `BYTES_SCANNED_LIMIT` at warehouse level | `maximumBytesBilled` per query | Not applicable (local engine) |

---

## Composition

- [`mcp-security.md`](mcp-security.md) — baseline security every MCP server needs; this file extends the Safe Database Checklist section
- [`mcp-custom.md`](mcp-custom.md) — building a custom MCP server (Shape C starts here)
- [`../../data-metabase/SKILL.md`](../../data-metabase/SKILL.md) — Shape A concrete patterns when the managed BI layer is Metabase
- [`../../data-analytics-engineering/references/pii-vault-and-pseudonymisation.md`](../../data-analytics-engineering/references/pii-vault-and-pseudonymisation.md) — PII boundary the MCP enforces at Layer 4
- [`../../ai-rag/references/wiki-grounded-retrieval.md`](../../ai-rag/references/wiki-grounded-retrieval.md) — when the MCP also fronts an unstructured wiki surface alongside the warehouse

---

## Check

Your DWH MCP is configured correctly if:

- The DB role cannot execute `INSERT`, `UPDATE`, `DELETE`, or `ALTER` — verified by attempting each after deployment, not by reading the grant list.
- Each agent purpose has its own DB role; no two agent purposes share a credential.
- Direct-identifier columns (name, email, national ID, account number) are absent from every column grant on the MCP role; confirm by running `DESCRIBE TABLE` through the MCP and verifying the columns returned.
- The audit log has one row for every MCP tool call and the audit table is not visible to the MCP role (`SELECT` on the audit table from the MCP role returns a permission error).
- Query budgets are enforced at the DB layer (timeout, row limit) and at the MCP server layer (LIMIT injection, max_rows cap) — two independent enforcement points, not one.
- No PII flows through the prompt or the tool response; pseudonym substitution happens at the DB layer, not in a prompt instruction.
- The vendor's native RLS and CLS mechanisms are used for row and column isolation; application-layer filters in the MCP server are defense-in-depth, not the primary boundary.
- A migration path from Shape B to Shape C is documented and tested; the audit log from Shape B is retained as a forensic asset after migration.
