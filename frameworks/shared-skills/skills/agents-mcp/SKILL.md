---
name: agents-mcp
description: Configure and build Model Context Protocol (MCP) servers for AI coding agent integration (Claude Code, Codex CLI). Set up database, filesystem, git, and API connections. Build custom MCP servers with TypeScript/Python SDK, implement tools and resources, configure transports (stdio, HTTP), and deploy for production. Advises when to use MCP vs direct tool calls.
---

# MCP (Model Context Protocol) — Advisor & Reference

Specification: https://modelcontextprotocol.io/specification/2025-11-25 (November 2025)

## When to Use MCP (Decision Tree)

| Scenario | Use MCP? | Why |
|----------|----------|-----|
| Query PostgreSQL/MySQL/SQLite | **Yes** | Official servers exist, read-only by default |
| Access filesystem outside workspace | **Yes** | Scoped allowlists, audit trail |
| GitHub/Linear/Slack/Notion integration | **Yes** | Vendor MCP servers available |
| One-off HTTP API call | **No** | Use WebFetch or Bash curl |
| Internal API with auth | **Maybe** | Build custom MCP server if repeated, otherwise direct call |
| Need write access to production DB | **Caution** | Prefer read-only; if writes needed, scope tightly |

**Rule of thumb**: Use MCP when (1) an official/community server exists, (2) you need audit/permission control, or (3) you'll reuse the integration across sessions.

## Quick Start (Local stdio via npx)

1) Create or edit `.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "POSTGRES_URL": "${DATABASE_URL}" }
    }
  }
}
```

2) Validate the connection:

```bash
export DATABASE_URL="postgresql://user:pass@localhost:5432/db"
claude mcp list
claude mcp get postgres
```

## Common Tasks

### Add a database connection

```bash
# PostgreSQL
claude mcp add postgres --env POSTGRES_URL=postgresql://user:pass@host:5432/db -- npx -y @modelcontextprotocol/server-postgres

# SQLite (local file)
claude mcp add sqlite -- npx -y @modelcontextprotocol/server-sqlite ./data/app.db
```

### Add GitHub integration

```bash
claude mcp add github --env GITHUB_TOKEN=ghp_xxx -- npx -y @modelcontextprotocol/server-github
```

### Add filesystem access (scoped)

```bash
# Read-only access to ./docs
claude mcp add docs-readonly --deny "mcp__filesystem__write_file" -- npx -y @modelcontextprotocol/server-filesystem ./docs
```

### Add remote server (HTTP transport)

```bash
claude mcp add --transport http notion https://mcp.notion.com/mcp
```

### Add PostHog MCP (EU/US + Codex fallback)

Use the region-matching PostHog MCP host:

- EU workspaces: `https://mcp-eu.posthog.com/mcp`
- US workspaces: `https://mcp.posthog.com/mcp`

```bash
# Codex streamable HTTP (default)
codex mcp add posthog --url https://mcp-eu.posthog.com/mcp
codex mcp login posthog

# If Codex fails at initialize with HTTP 500, use SSE bridge fallback
codex mcp remove posthog
codex mcp add posthog -- npx -y mcp-remote@latest https://mcp-eu.posthog.com/sse
```

The SSE bridge keeps PostHog available in Codex when `streamable_http` handshakes fail.

## Permission Management

```bash
# Allow all tools from a server (wildcard)
claude mcp add --allow "mcp__postgres__*" postgres -- npx -y @modelcontextprotocol/server-postgres

# Allow specific tools only
claude mcp add --allow "mcp__postgres__query,mcp__postgres__list_tables" postgres -- npx -y @modelcontextprotocol/server-postgres

# Deny a specific tool
claude mcp add --deny "mcp__filesystem__write_file" filesystem -- npx -y @modelcontextprotocol/server-filesystem ./data
```

## Build vs Use Decision

| Need | Recommendation |
|------|----------------|
| Database query (PG/MySQL/SQLite) | Use official server |
| GitHub/Linear/Slack/Notion | Use vendor server |
| Custom internal API | Build custom server (TypeScript recommended) |
| One-time data fetch | Don't use MCP; use WebFetch |
| Browser automation | Use Puppeteer MCP server |

## Build Custom MCP Server (Quick Start)

When no existing server fits your needs, build a custom one:

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk
```

Minimal TypeScript server (`src/index.ts`):

```typescript
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { CallToolRequestSchema, ListToolsRequestSchema } from "@modelcontextprotocol/sdk/types.js";

const server = new Server(
  { name: "my-server", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: "my_tool",
    description: "What this tool does",
    inputSchema: {
      type: "object",
      properties: { query: { type: "string" } },
      required: ["query"]
    }
  }]
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (request.params.name === "my_tool") {
    const result = await doWork(request.params.arguments);
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  }
  throw new Error(`Unknown tool: ${request.params.name}`);
});

const transport = new StdioServerTransport();
await server.connect(transport);
```

Register in `.claude/.mcp.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "npx",
      "args": ["tsx", "./my-mcp-server/src/index.ts"],
      "env": { "API_KEY": "${MY_API_KEY}" }
    }
  }
}
```

**Full guide**: `references/mcp-custom.md` (TypeScript + Python, resources, prompts, testing, deployment)

## Production Guardrails (Required)

- Assume tool outputs are untrusted (prompt injection). Sanitize/structure before reuse.
- Default to least privilege: read-only DB, scoped filesystem allowlists, minimal tool allowlists.
- Keep secrets out of `.mcp.json`; inject via env vars or a secret manager at runtime.
- Add timeouts, retries, and rate limits; log all tool invocations for audit.

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Server not found" | Check `claude mcp list`; verify package installed |
| "Permission denied" | Add `--allow` for specific tools |
| "Connection refused" | Verify env vars, check network access |
| "500 Internal Server Error" on initialize (streamable HTTP) | For PostHog in Codex, switch to SSE bridge: `npx -y mcp-remote@latest https://mcp-eu.posthog.com/sse` |
| Slow responses | Check server logs, add timeout config |
| "Tool output too large" | Use pagination or limit queries |

## What To Read Next

| Task | Resource |
|------|----------|
| Choose an existing server | `references/mcp-servers.md` |
| Build a custom server | `references/mcp-custom.md` |
| Implementation patterns (DB/API/filesystem) | `references/mcp-patterns.md` |
| Security hardening (OAuth, scopes, injection defense) | `references/mcp-security.md` |
| Templates | `assets/database/`, `assets/filesystem/`, `assets/api/`, `assets/deployment/` |
| Curated links | `data/sources.json` |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [agents-subagents](../agents-subagents/SKILL.md) | Creating agents that use MCP tools |
| [agents-hooks](../agents-hooks/SKILL.md) | Automating MCP server startup/validation |
| [ops-devops-platform](../ops-devops-platform/SKILL.md) | Deploying MCP servers in CI/CD |

---

## Operational Reliability Addendum (Feb 2026)

### MCP Health Gate (Run Before Data Work)

For each MCP server used in a task, run:

1. Presence: `codex mcp list`
2. Auth state: `codex mcp get <server>` or equivalent
3. Minimal smoke test: one low-cost read/list call

Only proceed to analysis/query work after all 3 pass.

### Transport/Auth Fallback Playbook

If login/initialize fails:
1. verify endpoint region (EU vs US),
2. verify transport support (streamable HTTP vs SSE bridge),
3. retry with documented fallback transport,
4. re-run health gate.

### MCP Incident Note Template

When MCP setup fails, report in one block:
- server name,
- endpoint/transport used,
- exact failure message,
- next fallback attempted,
- final status.

### Auth Error Escalation (1-Retry Max)

When an MCP tool call fails with an auth/token error:

1. Retry **once** after re-authenticating (`codex mcp login <server>` or equivalent).
2. If the retry also fails, **stop immediately** and notify the user with:
   - server name,
   - exact error message,
   - what was attempted.
3. Do **not** loop retries — auth failures that survive one re-auth are environment/config issues that require human intervention.

Unbounded auth retry loops waste context window and block productive work.

### Reuse Rule

Cache working MCP connection settings per session and avoid repeated re-login/reconfigure unless health gate fails.
