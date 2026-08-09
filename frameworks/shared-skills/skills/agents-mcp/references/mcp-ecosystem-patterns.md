# MCP Ecosystem Patterns

Use this file when the question is not "how do I implement the protocol?" but "which kind of MCP server should I adopt?"

## Docs Servers

- Use docs-oriented servers when the user needs current library or platform documentation more than raw API access.
- Context7 is the clearest example from the source set: it packages current docs into a tool surface instead of forcing ad hoc web scraping.
- Prefer docs servers for code generation, migration work, SDK usage, and version-sensitive framework questions.

## Search And Research Servers

- Use search-oriented servers (such as Exa Search) when the workflow starts with web search, source discovery, or current-event lookup.
- Keep them read-only and source-oriented. The goal is evidence gathering, not arbitrary browsing side effects.
- Pair search servers with narrow downstream tools for extraction or summarization rather than one giant "research" tool.

## Memory And Repo Servers

- Use Codebase Memory MCP or similar memory servers when a repo or workspace must become reusable context across sessions.
- Treat memory servers as retrieval infrastructure, not as an excuse to skip repository structure, docs, or AGENTS files.
- Keep memory scoped by repo, tenant, or workspace so agents do not blend unrelated context.

## Multi-Server Hubs

- Use MCPHub or an internal gateway when you need inventory, auth, and lifecycle management across many servers.
- Hubs help when you have multiple internal services, many users, or mixed transports.
- They are not mandatory for small local setups; do not add a hub just to front one or two simple stdio servers.

## Database Servers

- Use lightweight database MCP servers (DBHub, official Postgres server) when agents need direct SQL access for reconciliation, reporting, or schema inspection.
- Prefer zero-dependency, narrow-tool servers over full ORM wrappers.
- Always scope to read-only roles with strict row limits unless the workflow explicitly requires writes.

## Error Tracking and Observability Servers

- Use Sentry MCP or Grafana MCP when debugging workflows need production context without dashboard context-switching.
- Sentry provides AI-powered issue search; Grafana provides metrics and dashboards.
- Pair with alerting tools (PagerDuty) only when incident response automation justifies the token overhead.

## DevOps and Infrastructure Servers

- Use Docker and Kubernetes MCPs for container management and cluster operations.
- Kubernetes MCP supports modular toolsets — disable unneeded ones to keep token cost low.
- Cloudflare MCP wraps Workers, KV, R2, and D1 behind a single surface.

## Token Budget Management

- Each MCP server adds ~1,500–2,000 tokens of tool definitions per message.
- Use MCP Optimizer (Stacklok) for semantic tool filtering when running many servers (~96% token reduction).
- Audit regularly: remove servers that are no longer used.

## Rapid Authoring

- For Python, FastMCP is the highest-value pattern from the source list because it compresses the path from idea to working server.
- Use FastMCP for internal workflow wrappers, thin policy layers, and quick prototypes that may later harden into fuller services.
- Move to lower-level SDK surfaces only when you need protocol features FastMCP does not expose cleanly.
