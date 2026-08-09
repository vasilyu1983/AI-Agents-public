# Metabase Modern Surface Area

> Purpose: Keep automation guidance aligned with current Metabase in 2026 (v62 as of July 2026), not just what it was when "cards and dashboards" were the whole story. Verify release-number-specific claims against current Metabase docs before citing them — the release cadence is monthly, so any of these rows can be superseded by the time you read this.

## Release Anchors (2026)

| Release | Date | Key additions |
|---------|------|---------------|
| v59 | March 2026 | Data Studio, AI SQL generation in Open Source, semantic layer tooling |
| v60 | April 2026 | AI open-sourced, official MCP server, Metabot in Slack, split panel charts, Metrics Explorer |
| v61 | May 2026 | AI governance (per-group controls, token limits, Metabot customization, usage analytics), dashboards-as-code via MCP, metrics math |
| v62 | June 2026 | Official Metabase CLI (`@metabase/cli`) for questions/dashboards/documents/transforms; MCP server can run SQL, create collections, and render interactive charts in the AI client; Interactive Schema Viewer (Data Studio ER diagrams); custom-visualization plugin SDK (Gantt, org chart, radar, calendar, heatmap — Pro/Enterprise, not usable in embeds/subscriptions/alerts); Alert Management hub; Library sub-collections; programmatic embedded-filter updates without page reload |
| v63 | reported in beta as of July 2026 | Not yet on the stable release line at the time of writing; check `metabase.com/releases` and `/docs/latest` before relying on it |

## Why This Matters

Metabase is no longer only:

- cards
- dashboards
- collections

Current automation and architecture choices also intersect with:

- Data Studio workflows (v59+)
- Documents
- transforms and pipeline-style data shaping
- dependency graph and model-aware navigation
- AI surfaces: Agent API, Metabot (Slack, v60+), MCP server (v60+, SQL/collection-write + interactive charts as of v62)
- AI governance: per-group access controls, token limits, usage analytics (v61+, Pro/Enterprise)
- Dashboards-as-code via MCP terminal (v61+) and the official Metabase CLI (v62+)
- richer embedding and tenancy controls, including programmatic embedded-filter updates (v62+)
- Modular embedding SDK (renamed from "Interactive embedding"; Pro/Enterprise)
- Custom-visualization plugin SDK and Interactive Schema Viewer (v62+, Pro/Enterprise)

## Operational Implication

When a user asks for "Metabase automation", first identify which layer they mean:

| Layer | Typical tasks |
|------|---------------|
| Classic content layer | cards, dashboards, collections, layout |
| Promotion layer | Remote Sync, serialization, Git-backed review |
| Embedded app layer | tenants, embedding permissions, JWT, routing, modular SDK |
| AI analytics layer | Agent API, semantic discovery, app-side agents |
| AI assistant layer | Metabot (UI + Slack), MCP server (terminal/agent, SQL + collection writes v62+), dashboards-as-code, official Metabase CLI (v62+) |
| AI governance layer | Per-group controls, token limits, usage analytics (v61+, Pro/Enterprise) |
| Modern UI surface | Data Studio, Documents, Metrics Explorer, split panel charts, Interactive Schema Viewer, custom visualizations, Alert Management hub (v62+) |

## Guardrail

Do not default every Metabase request to `/api/card` and `/api/dashboard`. Confirm whether the user really wants saved content CRUD, or whether they actually need promotion, embedding, tenancy, or AI query execution.

Do not treat a frozen release note, such as Metabase 59, as the current product baseline after a newer docs version is available. Use release notes for dated change context and `/docs/latest` for current behavior. Current release line is v62 (June 2026); verify against `/docs/latest` since the cadence is monthly and v63 may already be stable by the time you read this.
