# MCP Servers — Discovery and Evaluation

Use this reference to choose an existing MCP server before you build your own.

## Table of Contents

- [Default Rule](#default-rule)
- [Discovery Workflow](#discovery-workflow)
- [Common Server Types](#common-server-types)
- [Server Categories: Adoption Judgments](#server-categories-adoption-judgments)
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

## Server Categories: Adoption Judgments

These judgments are durable. Which products fill each category changes, so look that up in the registry.

- **Docs servers** package library and platform documentation as tools. Prefer them over ad hoc scraping for code generation, migrations, SDK usage, and version-sensitive questions.
- **Search and research servers** should stay read-only and source-oriented. Pair them with narrow extraction tools instead of one giant "research" tool.
- **Memory and repo servers** are retrieval infrastructure, not a substitute for repo structure, docs, or AGENTS files. Scope memory by repo, tenant, or workspace, and pick one source of truth when a memory server overlaps file-based memory.
- **Database servers**: prefer narrow, few-tool servers over ORM wrappers or generic interpreters. Scope them to a read-only role with row limits (see [mcp-for-dwh.md](mcp-for-dwh.md)). Check maintenance status: reference servers get archived. For example, `@modelcontextprotocol/server-postgres` moved to the servers repo's archive.
- **Error-tracking and observability servers** earn their token cost when debugging needs production context without switching to a dashboard. Add alerting or paging tools only when incident automation justifies them.
- **DevOps and infrastructure servers** are often modular. Enable only the toolsets the workflow needs.
- **Multi-server hubs and gateways** pay off for inventory, auth, and lifecycle management across many servers, users, or mixed transports. Do not add one to front one or two stdio servers.
- **Redundant servers**: skip a server that duplicates a built-in tool (web search, file access) or a CLI the agent already uses well (for example `gh`), unless it adds scoping or auth the built-in lacks. Heavy chat-archive and suite-wide workspace servers rarely repay their tool-definition cost in agent loops.
- **Broad connector aggregators and generic cloud or database interpreters** have large tool surfaces. Prefer a narrow vendor or custom server unless the breadth is the point.

### Token Budget Awareness

Every connected server adds tool definitions to context, and the cost varies widely by server. Measure it (`/context` in Claude Code) instead of estimating from a per-server rule of thumb.

Mitigations:
- prefer servers with few, narrow tools
- disable unused toolsets in modular servers
- use deferred tool loading where the client supports it (see `../SKILL.md`, Deferred Tool Loading)
- at large fleets, consider a gateway with semantic tool filtering
- remove servers you no longer use

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
  -- npx -y <maintained-postgres-mcp-server>   # pick from the registry

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
[ ] Who maintains it, and is it archived or deprecated?
[ ] Is the transport documented, and is it an Active (not Deprecated) spec transport?
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
