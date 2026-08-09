# Metabase Agent API

> Purpose: Operational guide for using Metabase's versioned Agent API for semantic, AI-driven analytics workflows. Freshness anchor: June 2026.

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

- Agent API returns a maximum of 200 rows per request.
- To page through larger result sets, use `POST /api/agent/v1/query`; when more rows are available the response includes a `continuation_token` — pass it in the next request.
- Queries run against the authenticated user's scoped permissions.

## MCP Server (v60+, expanded v62)

For agent-driven content generation (generating questions, editing dashboards via conversation), prefer the official Metabase MCP server over raw Agent API calls. The MCP server:

- connects Metabase to Claude, Cursor, VS Code, and other MCP-compatible AI clients
- applies the same Metabase permissions as the authenticated user
- supports dashboards-as-code via AI terminal (v61+)
- as of v62, can execute SQL, create collections, and render interactive charts directly in the AI client (toggle time range/granularity, change chart type, drill through) — not just read/describe content
- is documented at `metabase.com/docs/latest/ai/mcp`

Use the Agent API when you need direct programmatic control over semantic discovery and query execution from your own app code. Use the MCP server when a human is driving through a conversational AI client (Claude, Cursor, VS Code) and wants content created or charts rendered in that session. Use the official Metabase CLI (`references/metabase-cli.md`, v62+) when you want scripted, non-conversational content ops without an MCP session.

## Guardrails

- Prefer Agent API for AI analytics apps over direct SQL templating when semantic safety matters.
- Keep classic REST and Agent API concerns separate in code and docs.
- Do not assume Agent API and classic API share auth headers.
- Do not assume API key auth is user-scoped; use session or JWT when per-user permission boundaries matter.
- If the output needs to become a saved Metabase artifact, explicitly hand off to classic REST API after query generation.
- Handle `continuation_token` pagination when queries may return more than 200 rows.
