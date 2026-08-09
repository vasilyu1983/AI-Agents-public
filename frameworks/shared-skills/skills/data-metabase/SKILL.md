---
name: data-metabase
description: "Automates Metabase cards, dashboards, Remote Sync, embedding, tenants, and the Agent API/MCP server for AI workflows. Use when scripting, promoting, or embedding Metabase content."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Metabase Automation

Automate Metabase content, promotion, embedding, and admin refresh workflows.

Classic Metabase REST API still owns cards, dashboards, collections, permissions, and schema refresh operations. The newer Agent API is the right surface for headless semantic BI assistants and app-side AI workflows. Metabase v60 (April 2026) added an official MCP server and open-sourced AI; v61 (May 2026) added AI governance, dashboards-as-code via MCP, and per-group Metabot controls. v62 (June 2026, current line) added the official `@metabase/cli`, an Interactive Schema Viewer, a custom-visualization plugin SDK, an Alert Management hub, Library sub-collections, and expanded MCP capabilities — run SQL, create collections, and render interactive charts directly in the AI client. Verify `/docs/latest` and `metabase.com/releases` before citing version-specific behavior, since the release cadence is monthly.

## Quick Reference

| Task | Path | Use When |
|------|------|----------|
| Create/update questions and dashboards | Classic REST API + `scripts/metabase_api.py` | Standard content automation and incremental upserts |
| Promote content between environments | Remote Sync or serialization | Git-backed promotion, reviewable diffs, cross-environment moves |
| Build embedded customer analytics | Embedding + tenants + embedding permissions | Multi-tenant apps, customer portals, row-level isolation |
| Build an AI analytics app | Agent API | Versioned, semantic, app-side AI querying |
| Integrate Metabase with an AI coding agent | MCP server (v60+) | Claude, Cursor, VS Code — generate questions and dashboards via conversation |
| Govern AI access by group | Metabot AI governance (v61+, Pro/Enterprise) | Per-group controls, token limits, usage analytics |
| Refresh schema metadata | Database sync/rescan endpoints | New tables, changed columns, stale field values |
| Tune native SQL questions | Export-first + native query patterns | Stable automation without guessing request shapes |

## Decision Tree

```text
Need to create or edit saved Metabase content?
  -> Use classic REST API (`card`, `dashboard`, `collection`).

Need repeatable dev -> prod promotion with reviewable diffs?
  -> Prefer Remote Sync or serialization before raw REST upserts.

Need embedded analytics for many customers or workspaces?
  -> Use embedding + tenants + embedding permissions.

Need an AI assistant to discover metrics/tables and construct queries?
  -> Use the versioned Agent API, not raw card CRUD.

Need to generate or edit questions/dashboards from an AI coding agent or terminal?
  -> Use the official Metabase MCP server (v60+, connects Claude/Cursor/VS Code).
```

## ASCII Flow

```text
Metabase automation request
  -> health check and authentication
  -> discover IDs: database, collection, table, fields, entities
  -> choose surface
     +-- cards, dashboards, collections -> classic REST API
     +-- dev-to-prod promotion -> Remote Sync or serialization
     +-- customer analytics -> embedding + tenants + permissions
     +-- semantic assistant -> Agent API
     +-- AI terminal / agent build -> MCP server (v60+)
  -> export existing JSON when structure is complex
  -> upsert or promote content
  -> refresh metadata if schema changed
  -> validate by running/exporting results
```

## Quick Start

### Inputs (env vars)

- `METABASE_URL` (e.g., `https://metabase.example.com`)
- Preferred: `METABASE_API_KEY`
- Optional: `METABASE_SESSION`
- Fallback: `METABASE_USERNAME` + `METABASE_PASSWORD`

### Sanity checks

```bash
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py health
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py whoami
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py list-databases
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py list-collections --tree
```

### Live API documentation

Your Metabase instance serves OpenAPI docs at `/api/docs` (for example `https://metabase.example.com/api/docs`). Use this to confirm request shapes for your exact build before scripting bulk edits.

## Workflow

1. Confirm API availability (`GET /api/util/health`).
2. Authenticate with an API key first, then fall back to session auth only if needed.
3. Discover IDs instead of hardcoding them across environments:
   - `collection_id` for save location
   - `database` id for `dataset_query`
   - table and field IDs if using MBQL
4. Choose the right surface:
   - classic REST API for cards/dashboards/admin
   - Agent API for semantic, AI-driven querying
   - Remote Sync or serialization for promotion workflows
5. Create/update a card:
   - prefer native SQL for stable automation
   - set `display` and `visualization_settings` explicitly
6. Create/update a dashboard, then place cards with explicit layout.
7. Refresh metadata if schema changed.
8. Validate by running/exporting results and re-opening exported JSON.

## Key Concepts

- UI "Question" == API `card`
- Chart configuration lives on the card as `display` + `visualization_settings`
- Most visualization keys are easiest to manage by exporting an existing card JSON, then editing that payload
- Remote Sync is for Git-backed promotion, not per-request runtime automation
- Agent API is a separate, versioned surface for semantic query construction and execution; returns max 200 rows per request; paginate via `continuation_token`
- MCP server (v60+) connects Metabase to Claude, Cursor, VS Code, and other MCP clients with the same permissions as the authenticated user; enables dashboards-as-code from AI terminals; v62 adds SQL execution, collection creation, and interactive charts rendered in the AI client itself
- Official Metabase CLI (v62+, `npm install -g @metabase/cli`, distinct from the classic REST/JAR admin surfaces) builds questions, dashboards, documents, and transforms from the terminal — see `references/metabase-cli.md`
- Metabot (v60+, open source) integrates with Slack; v61 adds per-group access controls, token limits, and usage analytics (Pro/Enterprise only for governance features)
- Interactive/modular embedding SDK requires Pro/Enterprise, React 18/19, Node 20+, Metabase v1.52+
- Custom visualizations (v62+, Pro/Enterprise) let you build React-based chart types (Gantt, org chart, radar, calendar, heatmap) via a plugin SDK — not supported in embeds, subscriptions, or alerts

## Pricing Reference (July 2026)

| Plan | Price | Key limits |
|------|-------|------------|
| Open Source | Free (self-host, unlimited users) | No modular embedding SDK, no sandboxing, no AI governance |
| Starter | $90/mo base + $6/user (5 included) | No SSO, no row-level security, no interactive embedding |
| Pro | $517.50/mo base + $12/user (10 included) | SSO, sandboxing, modular embedding SDK, custom visualizations, schema viewer, Metabot governance |
| Enterprise | Custom (~$20k/yr+) | Same features as Pro + 1-day SLA, dedicated success engineer |

AI add-on: Metabase's hosted AI service bills at $3.75 per 1M tokens (1M included); most deployments instead bring their own model provider key, in which case you pay that provider directly and Metabase charges nothing extra for AI usage. Transforms include 1,000 runs/mo on Starter/Pro, then $0.01–$0.02/run.

Prices change often — verify current numbers at `metabase.com/pricing` before quoting costs in any proposal; do not reuse the figures above past one quarter without re-checking.

## Guardrails

- Prefer Remote Sync or Metabase serialization for bulk, cross-environment promotion; use direct API for incremental upserts.
- Do not hardcode numeric IDs across environments when you can discover them or use entity IDs / synced content.
- Never commit `METABASE_API_KEY`, passwords, or session tokens.
- Prefer a dedicated, least-privileged automation account and collection.
- Treat internal admin notify endpoints separately from normal automation. They use server-side `MB_API_KEY`, not the user-facing `METABASE_API_KEY`.
- If a dashboard uses tabs, filters, or complex dashcard state, export first and preserve that structure instead of rebuilding from memory.

## Navigation

| Topic | File | Load when |
|-------|------|-----------|
| Authentication (API key + fallback) | [references/api-auth.md](references/api-auth.md) | Any API automation task |
| Reports (cards): create/edit patterns | [references/reports-cards.md](references/reports-cards.md) | Creating or updating saved questions |
| Dashboards and card placement | [references/dashboards.md](references/dashboards.md) | Building or replicating dashboards |
| Charts and `visualization_settings` | [references/charts-settings.md](references/charts-settings.md) | Configuring chart display or axis settings |
| Agent API for semantic BI | [references/agent-api.md](references/agent-api.md) | Building AI analytics apps or headless BI workflows |
| Embedding and integration | [references/embedding-integration.md](references/embedding-integration.md) | Public links, signed JWT, or SDK embedding |
| Tenants, embedding permissions, routing | [references/tenants-routing.md](references/tenants-routing.md) | Multi-tenant apps or customer portal isolation |
| Permissions and collections | [references/permissions-collections.md](references/permissions-collections.md) | Group setup, sandboxing, or collection hierarchy |
| Native SQL query patterns | [references/native-query-patterns.md](references/native-query-patterns.md) | Template tags, field filters, caching in SQL cards |
| Remote Sync and promotion workflows | [references/remote-sync.md](references/remote-sync.md) | Git-backed content promotion or cross-env moves |
| Modern surface area (v59+, updated v61) | [references/metabase-59-surface.md](references/metabase-59-surface.md) | Confirming which API layer a request belongs to |
| CLI: `mb` API client and JAR admin commands | [references/metabase-cli.md](references/metabase-cli.md) | Scripting content via `mb`, or server admin (migrate, dump-to-h2, serialization) |

## Assets

| Template | File |
|----------|------|
| Card spec skeleton | [assets/card-spec.template.json](assets/card-spec.template.json) |
| Dashboard spec skeleton | [assets/dashboard-spec.template.json](assets/dashboard-spec.template.json) |
| Dashcard layout skeleton | [assets/dashcards-layout.template.json](assets/dashcards-layout.template.json) |
| Embed JWT examples | [assets/embed-jwt-example.md](assets/embed-jwt-example.md) |

## Scripts

`scripts/metabase_api.py` is a dependency-free helper for auth, discovery, content CRUD, dashboard layout work, query execution, and schema refresh.

Examples:

```bash
# Print authenticated user (tries API key, then session)
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py whoami

# Discover IDs before scripting
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py list-collections --tree
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py list-databases
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py database-metadata --id 2
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py list-fields --database-id 2

# Export an existing card JSON (use as a template for visualization_settings)
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py export-card --id 123 --out card.json

# Export an existing dashboard JSON (use as a template for layout)
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py export-dashboard --id 5 --out dashboard.json

# Create/update a card from a JSON spec (see references/reports-cards.md)
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py upsert-card --spec card-spec.json

# Create/update a dashboard from a JSON spec
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py upsert-dashboard --spec dashboard-spec.json

# Add or update dashboard layout
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py add-dashcard --dashboard-id 5 --spec dashcard.json
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py update-dashcards --dashboard-id 5 --spec dashcards-layout.json

# Execute a query spec or export a saved card result
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py run-query --spec dataset-query.json
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py export-card-query --id 123 --format csv --out report.csv

# Refresh metadata after schema changes
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py sync-schema --id 2
python3 frameworks/shared-skills/skills/data-metabase/scripts/metabase_api.py rescan-values --id 2
```

## Known Traps

- Treating Metabase as the semantic layer of record while metrics, joins, and business definitions still drift in dbt, SQLMesh, or raw SQL cards.
- Copying cards manually between environments and silently breaking references, permissions, or dashboard filter wiring because serialization or sync strategy was never defined.
- Reusing one question across dashboards with slightly different filter semantics and creating hidden KPI disagreements that look like product changes.
- Embedding tenant dashboards without a strict parameter contract, collection isolation model, and signed-embed verification path.
- Letting native SQL cards become the default authoring path for everything, then losing discoverability, lineage, and reuse across teams.
- Designing dashboard filters around visual convenience rather than stable field mappings, leading to broken linked filters after schema or model changes.

## Common Anti-Patterns

- Treating dashboard screenshots or PDF exports as the decision artifact instead of versioned questions, documented metrics, and reproducible model definitions.
- Building one large "executive dashboard" that mixes raw exploratory cards, production KPIs, and operational monitoring in the same surface.
- Using personal collections as production distribution channels instead of curated shared collections with ownership and promotion rules.
- Hardcoding environment-specific table names, URLs, or card IDs into migration and automation workflows.
- Solving multi-tenancy with card duplication alone when embedding parameters, row-level source models, or separate collections would provide cleaner isolation.
- Using Metabase to compensate for unresolved source-model problems that should be fixed upstream in warehouse modeling or metric governance.

## Related Skills

- [../data-analytics-engineering/SKILL.md](../data-analytics-engineering/SKILL.md) for semantic modeling, metrics, and BI-ready warehouse design
- [../data-sql-optimization/SKILL.md](../data-sql-optimization/SKILL.md) for query tuning and database performance work
- [../software-backend/SKILL.md](../software-backend/SKILL.md) for application integration and service-layer implementation
- [../agents-mcp/SKILL.md](../agents-mcp/SKILL.md) when Metabase access should be wrapped as tools rather than ad hoc scripts
- [../agents-mcp/references/mcp-for-dwh.md](../agents-mcp/references/mcp-for-dwh.md) for the LLM-via-MCP pattern catalog (Shape A managed-BI MCP applies directly to Metabase); enforcement layers (read-only role, query budgets, pseudonym boundary, audit log) apply regardless of shape

## Trend Awareness Protocol

When the user asks for the current or best Metabase approach in 2026, verify the latest official docs and release notes before answering.

Trigger examples:

- "What is the best way to promote Metabase content now?"
- "Is serialization still the right choice in 2026?"
- "Should I use Agent API or classic API?"
- "What changed in Metabase 59/60/61 for embedding or dashboards?"
- "What is the current best practice for multi-tenant Metabase?"
- "How do I use the Metabase MCP server?"
- "What Metabot or AI governance features are available now?"

## Fact-Checking

- Use web search/web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
