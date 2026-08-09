# MCP Servers — Discovery and Evaluation

Use this reference to choose an existing MCP server before you build your own.

## Table of Contents

- [Default Rule](#default-rule)
- [Discovery Workflow](#discovery-workflow)
- [Common Server Types](#common-server-types)
- [Good Reasons to Reuse an Existing Server](#good-reasons-to-reuse-an-existing-server)
- [Good Reasons to Build a Custom Server](#good-reasons-to-build-a-custom-server)
- [Claude Code Examples](#claude-code-examples)
- [Local stdio server](#local-stdio-server)
- [Remote Streamable HTTP server](#remote-streamable-http-server)
- [Codex / OpenAI Examples](#codex--openai-examples)
- [Local helper (stdio — CLI path)](#local-helper-stdio--cli-path)
- [Remote server (Streamable HTTP)](#remote-server-streamable-http)
- [Evaluation Checklist](#evaluation-checklist)
- [Backwards Compatibility Notes](#backwards-compatibility-notes)
- [Publishing a Custom Server](#publishing-a-custom-server)
- [Related](#related)

## Default Rule

**Search the official registry first**: https://registry.modelcontextprotocol.io

Do not treat a static markdown list of packages as the source of truth. Package names, transports, and hosted endpoints change faster than this repo should pretend to track.

## Discovery Workflow

1. Search the registry by domain or system.
2. Prefer provider-hosted or officially maintained servers.
3. Verify:
   - transport,
   - auth model,
   - read/write scope,
   - maintenance source,
   - documentation quality,
   - whether the server output is bounded.
4. Run a three-step smoke test:
   - add/configure the server,
   - list/get the server in the client,
   - call one low-cost read tool.

## Common Server Types

| Category | Typical fit | Notes |
|---------|--------------|-------|
| Database | PostgreSQL, MySQL, SQLite, analytics replicas | Prefer read-only roles and strict row limits |
| Filesystem | docs, logs, repos outside current workspace | Scope roots tightly |
| Git / GitHub / issue trackers | PR review, issue triage, repository metadata | Treat issue/body text as hostile input |
| Browser automation | end-to-end workflows, page inspection | Isolate from sensitive credentials |
| SaaS business systems | Notion, Stripe, PostHog, Slack, Linear | Prefer vendor-hosted remote servers where available |
| Internal APIs | proprietary workflows, approval systems, domain data | Strong candidate for a custom server |

## Curated Server Catalog

Servers grouped by domain. Each entry notes transport, tool weight (light/medium/heavy), and install pattern.

### Currently Active

These are configured in the local setup script (`docs/scripts/code-agents-mcps.sh`) or via Claude/Codex plugins.

| Server | Transport | Platform | Purpose |
|--------|-----------|----------|---------|
| PostHog | Streamable HTTP | Codex, Claude (plugin) | Product analytics, error tracking, feature flags |
| Stripe | Streamable HTTP | Codex (project-scoped), Claude (plugin) | Payment processing, billing |
| Supabase | Streamable HTTP | Codex (project-scoped), Claude (plugin) | Database, auth, storage |
| Lenny's Data | Streamable HTTP | Codex, Claude | Startup/product/growth newsletter archive |
| XcodeBuildMCP | stdio (`npx`) | Claude | Xcode project building for iOS/macOS |
| Context7 | stdio (`npx`) | Claude (plugin) | Up-to-date library/framework documentation |
| Playwright | stdio (`npx`) | Claude (plugin) | Browser automation and E2E testing |
| Firebase | stdio (`npx`) | Claude (plugin) | Backend, auth, hosting |
| Chrome DevTools | stdio (`npx`) | Claude | Browser debugging, performance, a11y |
| Mermaid Chart | Streamable HTTP | Claude (plugin) | Diagram rendering and validation |
| Hugging Face | Streamable HTTP | Claude (plugin) | ML model/dataset/Spaces access |
| Vercel | Streamable HTTP | Claude (plugin) | Deployment, logs, project management |
| Linear | Streamable HTTP | Claude (plugin) | Issue tracking and project management |
| GitLab | Streamable HTTP | Claude (plugin) | Repository and CI/CD management |
| Google Calendar | Streamable HTTP | Claude (plugin) | Calendar access |
| Gmail | Streamable HTTP | Claude (plugin) | Email access |

### Recommended — High Value, Lightweight

Vetted servers that fill real gaps without bloating tool surface.

| Server | Tools | Transport | Install | Use case |
|--------|-------|-----------|---------|----------|
| **DBHub** | ~3 | stdio (`npx`) | `npx dbhub` | Zero-dep database access (Postgres, MySQL, SQLite); ultra-lightweight |
| **Sentry** | medium | Streamable HTTP | `--url https://mcp.sentry.dev/sse` | Error tracking, AI-powered issue search, performance |
| **Exa Search** | ~3 | stdio (`npx`) | `npx exa-mcp-server` | AI-native semantic web search; structured results |
| **Firecrawl** | ~5 | stdio (`npx`) | `npx firecrawl-mcp` | Web scraping to clean LLM-ready data; autonomous research |
| **Stack Overflow** (community) | 3 | stdio (`npx`) | `npx -y @gscalzo/stackoverflow-mcp` | Search the validated Q&A corpus before debugging from scratch; tools: `search_by_error`, `search_by_tags`, `analyze_stack_trace`. Community server over the public Stack Exchange API — not an official Stack Overflow product. Pairs with `qa-debugging` |

**Auth note (Stack Overflow):** runs unauthenticated (rate-limited). An optional Stack Apps
key via `STACKOVERFLOW_API_KEY` raises the request quota only — it authorizes throughput,
not private data, so it is not a secret (still keep it out of commits as a matter of hygiene).

**Emerging — Stack Overflow for Agents (verify before adding):** `agents.stackoverflow.com`
is an API-first validated-answer exchange built for agents — "search before burning tokens,"
plus an optional write-back path (TILs/Blueprints) tied to the operator's identity via SSO
with dashboard-issued API keys. As of June 2026 this is beta and its primary endpoint docs
(`agents.stackoverflow.com/llms.txt`) were not verifiable at authoring time; confirm the tool
or endpoint surface against primary docs before wiring it, and treat its write path as an
explicit, human-approved action rather than an automatic side effect.

### Recommended — Workflow and Documents

| Server | Tools | Transport | Install | Use case |
|--------|-------|-----------|---------|----------|
| **Task Master AI** | medium | stdio (`npx`) | `npx task-master-ai` | PRD → structured tasks with dependencies; pairs with `docs-ai-prd` and `dev-workflow-planning` |
| **Markdownify** | ~4 | stdio (`npx`) | `npx markdownify-mcp` | Convert PDF/image/audio/HTML to markdown; pairs with `document-pdf` and `docs-notes-retrieval` |
| **Excel MCP** | medium | stdio (`npx`) | `npx excel-mcp-server` | Read/write/format `.xlsx` without Microsoft Excel installed; pairs with `document-xlsx` |

### Recommended — Infrastructure and DevOps

Heavier but modular. Disable unused toolsets to keep token cost down.

| Server | Tools | Transport | Install | Use case |
|--------|-------|-----------|---------|----------|
| **Docker** | ~6 | stdio (`npx`) | `npx mcp-server-docker` | Container and image management |
| **Kubernetes** | modular | stdio (binary) | [containers/kubernetes-mcp-server](https://github.com/containers/kubernetes-mcp-server) | K8s/OpenShift; enable only needed toolsets |
| **Cloudflare** | medium | Streamable HTTP | Official Cloudflare MCP | Workers, KV, R2, D1 |
| **Grafana** | medium | stdio | [grafana/mcp-grafana](https://github.com/grafana/mcp-grafana) | Dashboards, metrics, alerting |

### Situational — Evaluate Before Adding

| Server | Tools | Transport | When to add |
|--------|-------|-----------|-------------|
| **Notion** | medium | Streamable HTTP | Only if Notion is your primary knowledge base |
| **Qdrant** | medium | stdio | Building local RAG pipelines or agent memory |
| **Memory MCP** (official) | ~5 | stdio (`npx`) | Persistent knowledge graph; may overlap with file-based memory |
| **Codebase Memory MCP** | medium | stdio | Persistent code-graph memory across sessions; overlaps with `dev-context-code-graph` and `agents-memory` — pick one source of truth |
| **Twilio** | medium | Streamable HTTP | Only when building SMS/voice flows for `ai-voice-bots`; otherwise out of scope |
| **Composio** | heavy | varies | Need 250+ platform connectors; token-expensive |

### Skip or Defer

| Server | Why |
|--------|-----|
| Brave Search | Redundant with Exa + built-in WebSearch |
| Tavily | Redundant with Exa Search + built-in WebSearch; revisit only if structured-result quality differs materially in side-by-side test |
| GitHub MCP | `gh` CLI + GitLab plugin already cover this |
| Slack MCP | Heavy tool surface; high token cost for limited return |
| Google Workspace MCP | Gmail plugin covers email; Docs/Sheets rarely needed in agent loops |
| Discord / Telegram / Teams MCP | Heavy tool surface; chat archive access rarely justifies token cost |
| Jira / Confluence MCP | Defer until a project lands in Atlassian; current portfolio uses Linear/GitLab |
| HubSpot / Salesforce MCP | Defer until a project needs CRM in agent loop |
| AWS / BigQuery / Snowflake / MongoDB MCP | Generic interpreters with broad tool surface; prefer DBHub or narrow custom servers |
| MCPHub | Only useful at 10+ active servers; current setup is well below |
| Stealth Browser MCP | Bypasses bot detection; out of scope for this catalog |
| Postman | Direct `curl`/`fetch` is simpler |
| LangSmith | Only if using LangChain ecosystem |

For building your own server when no listed option fits, see `references/mcp-custom.md` (FastMCP and equivalent SDKs).

### Token Budget Awareness

Each MCP server adds ~1,500–2,000 tokens of tool definitions per message. A four-server setup can burn 7k tokens before the first prompt.

Mitigations:
- prefer servers with fewer than 10 tools
- disable unused toolsets in modular servers (e.g., Kubernetes)
- consider [MCP Optimizer](https://github.com/stacklok/mcp-optimizer) for semantic tool filtering (~96% token reduction)
- audit with `claude mcp list` and remove servers you no longer use

## Good Reasons to Reuse an Existing Server

- You only need standard read access.
- The provider already maintains auth and API drift.
- The server has a narrow, comprehensible tool surface.
- The workflow is common enough that inventing your own server adds no value.

## Good Reasons to Build a Custom Server

- You need opinionated approval rules.
- You need stable, domain-specific tool names and schemas.
- The upstream API is noisy or dangerous and needs reshaping.
- You need to combine multiple backend systems behind one controlled surface.

## Claude Code Examples

### Local stdio server

```bash
claude mcp add postgres \
  --scope project \
  --env POSTGRES_URL=postgresql://user:pass@localhost:5432/app \
  -- npx -y @modelcontextprotocol/server-postgres

claude mcp list
claude mcp get postgres
```

### Remote Streamable HTTP server

```bash
claude mcp add --transport http stripe --scope local https://mcp.stripe.com
```

For shared team configuration, commit `.mcp.json` at the repo root.

## Codex / OpenAI Examples

### Local helper (stdio — CLI path)

```bash
codex mcp add repo-tools --env API_KEY=secret -- node ./dist/index.js
codex mcp list
```

### Remote server (Streamable HTTP)

```bash
codex mcp add openaiDeveloperDocs --url https://developers.openai.com/mcp
```

Or declare it directly in `~/.codex/config.toml` when you need fields the CLI doesn't expose (static headers, tool gating):

```toml
[mcp_servers.openaiDeveloperDocs]
url = "https://developers.openai.com/mcp"
startup_timeout_sec = 10
```

See [`mcp-custom.md`](mcp-custom.md#codex) for the full `config.toml` schema (env, headers, tool gating, OAuth).

## Evaluation Checklist

Before adopting any server, answer these:

```text
[ ] Who maintains it?
[ ] Is transport documented and current?
[ ] Is auth model clear?
[ ] Are writes separated from reads?
[ ] Are outputs paginated / bounded?
[ ] Does the tool surface expose generic interpreters or narrow domain tools?
[ ] Is the server listed in the official registry or vendor docs?
[ ] Can you smoke-test it with one read call before trusting it?
```

## Backwards Compatibility Notes

- Prefer Streamable HTTP for new remote deployments.
- Use legacy SSE only when the server or client still requires it.
- Keep one-off fallback bridges out of the default path unless the user explicitly needs that exact provider workaround.

## Publishing a Custom Server

If you build a server that other teams or clients should discover:

1. add a `server.json` manifest,
2. validate it locally,
3. publish with `mcp-publisher`,
4. confirm the registry listing.

## Related

- `references/mcp-custom.md`
- `references/mcp-security.md`
- `data/sources.json`
