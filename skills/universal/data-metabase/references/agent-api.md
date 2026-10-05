# Metabase Agent API

> Purpose: Operational guide for using Metabase's versioned Agent API for semantic, AI-driven analytics workflows.

## Table of Contents

- [When to Use Agent API](#when-to-use-agent-api)
- [Decision Rule](#decision-rule)
- [Auth Model](#auth-model)
- [Practical Workflow](#practical-workflow)
- [Response Limits](#response-limits)
- [MCP Server](#mcp-server-v60-expanded-v62) — [connecting a CLI client](#connecting-a-cli-client-to-the-mcp-server), [diagnosing the connection](#diagnosing-the-connection), [tool behaviour](#tool-behaviour), [SQL kill switch](#admin-kill-switch-for-sql)
- [Guardrails](#guardrails)

## When to Use Agent API

Use Agent API when you need:

- an application-side AI assistant to discover tables, fields, and metrics
- semantic query construction without creating saved cards first
- a versioned API surface for headless BI workflows
- AI features outside Metabase's own UI

Do not use Agent API when you need:

- card or dashboard CRUD
- collection management
- permission administration
- schema refresh operations

Those remain classic Metabase REST API tasks.

## Decision Rule

| Need | Use |
|------|-----|
| Save a question in Metabase | Classic REST API |
| Edit `visualization_settings` | Classic REST API |
| Let an app-side AI agent ask BI questions safely | Agent API |
| Promote content between environments | Remote Sync or serialization |

## Auth Model

- Agent API supports API key, session token, and JWT authentication in current Metabase docs.
- API key auth uses `X-API-Key`; permissions come from the group assigned to the key, not an individual user.
- Session auth uses `X-Metabase-Session` after login and is scoped to the authenticated user.
- JWT auth is available on Pro and Enterprise plans; it is useful for app-side user scoping and signed embedded-agent flows.
- Choose auth based on the product boundary, then verify the exact headers and plan constraints against the running Metabase version.

## Practical Workflow

1. Confirm the Metabase instance exposes the Agent API for your plan/edition.
2. Choose API key, session token, or JWT auth based on whether the client acts as a service account, a logged-in user, or an embedded app user.
3. Use the Agent API to discover semantic context first.
4. Build and execute queries through the Agent API.
5. Use classic REST API only if you also need to save results as cards or attach them to dashboards.

## Response Limits

- Agent API caps the rows returned per request; read the current cap from the Agent API docs rather than hardcoding it.
- To page through larger result sets, use `POST /api/agent/v1/query`; when more rows are available the response includes a `continuation_token` — pass it in the next request.
- Queries run against the authenticated user's scoped permissions.

## MCP Server (v60+, expanded v62)

For agent-driven content generation (generating questions, editing dashboards via conversation), prefer the official Metabase MCP server over raw Agent API calls. The MCP server:

- connects Metabase to Claude, Cursor, VS Code, and other MCP-compatible AI clients
- applies the same Metabase permissions as the authenticated user
- in recent versions, can go beyond reading content: dashboards-as-code, SQL execution, collection creation and interactive charts in the AI client. Tool coverage changes by release, so check the MCP docs (`metabase.com/docs/latest/ai/mcp`) for what your Metabase version supports before relying on a capability

Use the Agent API when you need direct programmatic control over semantic discovery and query execution from your own app code. Use the MCP server when a human is driving through a conversational AI client (Claude, Cursor, VS Code) and wants content created or charts rendered in that session. Use the official Metabase CLI (`references/metabase-cli.md`; check that your Metabase version ships it) when you want scripted, non-conversational content ops without an MCP session.

### Connecting a CLI client to the MCP server

The endpoint is `https://<metabase-host>/api/metabase-mcp`. Auth is OAuth 2.0 with dynamic client registration: no API key or static bearer token, and the token carries the logged-in user's permissions. An admin must enable MCP once in **Admin → AI → MCP**. The per-client toggles there (Claude, Cursor, ChatGPT) control browser inline-chart origins; they do not gate CLI connections.

Claude Code:

```bash
claude mcp add --transport http --scope user metabase https://<metabase-host>/api/metabase-mcp
# then /mcp -> metabase -> Authenticate (browser consent page)
```

- Use `--scope project` only when the team wants the declaration checked into that project.
- `MCP server metabase already exists` means it is registered; do not add a second copy. `claude mcp get metabase` shows the effective scope. Resolution is `local` before `project` before `user`, so a stray local entry shadows the intended user-wide one: run `claude mcp remove metabase --scope local` from the directory that owns it.
- Persistent `{"error":"invalid_request"...}` after re-authenticating means a stale client registration. Reset it and pin a stable callback port: `claude mcp remove metabase --scope local`, `claude mcp logout metabase`, `claude mcp remove metabase --scope user`, then `claude mcp add --transport http --scope user --callback-port <port> metabase https://<metabase-host>/api/metabase-mcp` and `claude mcp login metabase`.

Codex:

- Check first with `codex mcp list` and `codex mcp get metabase`. Register with `codex mcp add metabase --url https://<metabase-host>/api/metabase-mcp`, then `codex mcp login metabase`. Refresh bad credentials with `codex mcp logout metabase` then `login`, without removing the server.
- The declaration lives in `~/.codex/config.toml` as `[mcp_servers.metabase]` with `url = ...`. For a headless or remote machine, set `mcp_oauth_callback_port` (or `mcp_oauth_callback_url`) at the top level before logging in.
- If a Codex build cannot reach remote HTTP MCP servers, upgrade it. Use an `mcp-remote` stdio bridge only as a temporary fallback: it adds a Node dependency and a second OAuth layer.

After connecting or refreshing, restart the client and open a new session: a configured server does not prove the current session loaded its tools.

### Diagnosing the connection

- `! Needs authentication` = endpoint reachable, OAuth pending. `Failed to connect` = wrong URL or MCP disabled on the server.
- `invalid_request: "The token request is invalid."` = the cached OAuth token expired or was revoked; the server is healthy. Re-authenticate interactively; a non-interactive session cannot recover from this state.
- An OAuth redirect loop means the instance **Site URL** does not exactly equal `https://<metabase-host>`.
- Unauthenticated probes settle "is it me or the server":

```bash
curl -s -o /dev/null -w "%{http_code}\n" https://<metabase-host>/api/health          # 200 = up
curl -s -o /dev/null -w "%{http_code}\n" https://<metabase-host>/api/metabase-mcp    # 401 = MCP on, needs OAuth
curl -s https://<metabase-host>/api/session/properties | jq '{v:.version.tag, tz:."report-timezone-short", sql:."mcp-execute-sql-enabled", tier:(."token-features"|to_entries|map(select(.value))|map(.key))}'
```

### Tool behaviour

Read the inventory before planning: list the tools the client actually loaded and compare them with Admin → AI → MCP and the MCP docs for the running version. CLI clients can see tools the docs omit and miss browser-only visualization tools; the set changes between releases. Read caps (hits per `search`, items per page, rows per query) from the response fields and the docs; do not hardcode them. The behaviours below were observed on one live server; re-check them on yours.

| Tool | Behaviour worth knowing |
|------|-------------------------|
| `search` | `term_queries` and `semantic_queries` are both required keys (`null` the unused one); results are capped per call, so a short list is not proof of absence |
| `read_resource` | several `metabase://` URIs per call; lists are paged (`total`/`pages`, append `?page=N`, no continuation token). Saved questions are `metabase://question/{id}`, not `card`, and return portable MBQL |
| `construct_query` | MBQL 5 → `query_handle`; field refs are 4-segment portable names `[<database-name>, <schema>, <table>, <column>]`, every clause carries a `{}` options map, the first stage has `source-table`; numeric ids are rejected |
| `construct_native_query` | wraps SQL into a handle without running it; feeds `create_question` for saved SQL cards |
| `execute_question` | runs a saved card; fails on parameterised / template-tag cards |
| `query` | paged via `continuation_token`; all keys required (`null` the unused) |
| `execute_sql` | needs native-query permission and `mcp-execute-sql-enabled`; classed as a **write** tool because DML runs if the DB user allows it; failures return `status: failed` with the database error and SQLSTATE (e.g. `42501` = permission denied) |
| `create_question` | omitting `collection_id` saves to the caller's **personal** collection; explicit `null` = root. Always pass a curated collection id |
| `create_metric` | exactly one aggregation and at most one date grouping |
| `update_dashboard` | `dashcards` actions `add` / `remove` / `move`; `dashcard_id` comes from `metabase://dashboard/{id}/items` |

Paging makes full catalog walks expensive: prefer a precise `search` term, or a REST export, when a complete list is required.

### Admin kill switch for SQL

An admin can disable `execute_sql` instance-wide with the `mcp-execute-sql-enabled` setting (Admin → AI → MCP), independent of any user's native-query permission. If SQL execution stops for everyone, read that setting (the `session/properties` probe above) before assuming a permissions regression, and fall back to `construct_query` / `execute_query`, which the switch does not gate. Row/column security does not filter native SQL either (see `references/permissions-collections.md`), so an `execute_sql` path bypasses it for any user with native-query permission.

## Guardrails

- Prefer Agent API for AI analytics apps over direct SQL templating when semantic safety matters.
- Keep classic REST and Agent API concerns separate in code and docs.
- Do not assume Agent API and classic API share auth headers.
- Do not assume API key auth is user-scoped; use session or JWT when per-user permission boundaries matter.
- If the output needs to become a saved Metabase artifact, explicitly hand off to classic REST API after query generation.
- Always handle `continuation_token` pagination; do not assume one response holds the full result.
