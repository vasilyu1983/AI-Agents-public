# Building Custom MCP Servers

Build a custom MCP server when no existing registry or vendor server fits your workflow, or when you need to enforce domain-specific auth, approval, or data-shaping rules.

## Table of Contents

- [Build Defaults](#build-defaults)
- [Capability Selection](#capability-selection)
- [Transport Selection](#transport-selection)
- [SDK Lane Lookup](#sdk-lane-lookup)
- [Tool Design Guidance](#tool-design-guidance)
- [Shared Config in Clients](#shared-config-in-clients)
- [Claude Code](#claude-code)
- [Codex](#codex)
- [When to Add Authorization](#when-to-add-authorization)
- [Operational Capabilities to Consider](#operational-capabilities-to-consider)
- [Tool Annotation Hints](#tool-annotation-hints)
- [Testing and Validation](#testing-and-validation)
- [Inspector](#inspector)
- [Minimum Acceptance Checks](#minimum-acceptance-checks)
- [Registry Publishing](#registry-publishing)
- [Production Checklist](#production-checklist)
- [Related](#related)
- [Old patterns: v1-era SDK examples](#old-patterns-v1-era-sdk-examples)

## Build Defaults

- **Protocol revision**: target the newest revision listed at `modelcontextprotocol.io/specification`, and record it. The `2026-07-28` revision is a breaking boundary: stateless (no `initialize` handshake, no `Mcp-Session-Id`), a mandatory `server/discover` RPC, and MRTR instead of server-initiated requests. See [`../SKILL.md`](../SKILL.md) for the summary.
- **SDK lane**: a lookup, see [SDK Lane Lookup](#sdk-lane-lookup). Pin the major version.
- **API level**: the SDK's high-level server API (declarative tool registration with schemas), not low-level request handlers
- **Local development**: `stdio`
- **Shared remote deployment**: Streamable HTTP
- **Authorization**: optional; implement it only if your server needs it

## Capability Selection

Start small. Most servers only need one or two of these:

| Capability | Use it when |
|-----------|-------------|
| Tools | The model should call functions with arguments |
| Resources | The client should read documents, metrics, schemas, or records |
| Prompts | You want reusable prompt templates exposed by the server |
| Human input | The server must ask the human for input, approval, or URL-based auth (MRTR input requests from `2026-07-28`; `elicitation/create` before) |
| Tasks | The server does long-running work (check whether your revision has it in core or as an extension) |
| Roots, Sampling, Logging | Deprecated in `2026-07-28` (SEP-2577). Do not adopt in new servers. Use tool-parameter directories or resource URIs, direct provider API calls, and stderr or OpenTelemetry instead |

Do not implement every capability “because it exists”. Add only what removes real client friction.

## Transport Selection

| Scenario | Transport |
|---------|-----------|
| Local helper launched by the client | `stdio` |
| Shared service accessed by multiple users/clients | Streamable HTTP |
| Older remote server needing backwards compatibility | legacy SSE / HTTP+SSE only as fallback |

## SDK Lane Lookup

Before writing or copying server code, answer three questions from the SDK repo (README, migration guide, release notes) of the language you use:

1. Which major version is the stable line, and which spec revisions does it support?
2. What are the package names, the high-level server class, and its import path in that major version? These have changed between majors.
3. How long does the previous major line keep receiving fixes?

The answers decide which package you install, which import you write, and whether an existing server needs a migration ticket. Pin the major version in the dependency file (`package.json`, `pyproject.toml`) so a fresh install cannot silently move you to a different API. The v1-era examples at the end of this file are labelled legacy; translate them through the migration guide, do not paste them into a new server.

A minimal server, in any SDK, has: a server name and version, one narrowly named tool with a "Use this when..." description, a strict input schema, an output schema when callers parse the result, `isError` results for recoverable failures (see [mcp-patterns.md](mcp-patterns.md)), all four annotation hints, and a transport (`stdio` locally).

## Tool Design Guidance

- Give every tool a concrete “Use this when…” description.
- Prefer structured output via `structuredContent` and `outputSchema`.
- Enforce limits server-side: row counts, page sizes, timeout budgets.
- Keep tool arguments narrow. One focused tool beats one giant “do everything” tool.

## Shared Config in Clients

### Claude Code

Recommended setup:

```bash
claude mcp add my-server --scope project -- node ./dist/index.js
claude mcp list
claude mcp get my-server
```

Shared project config lives in `.mcp.json`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["./dist/index.js"],
      "env": {
        "API_KEY": "${MY_API_KEY}"
      }
    }
  }
}
```

### Codex

The `codex mcp add` CLI handles **both transports directly**: stdio via `--env` + the `--` separator, and Streamable HTTP via `--url` + `--bearer-token-env-var` (check `codex mcp add --help` on your build before scripting them). There is **no `--transport` flag**; transport is inferred from `--url` vs. a trailing stdio command. OAuth-specific flags (`--oauth-client-id`, `--oauth-resource`) exist on `add` too, or run `codex mcp login` after the fact.

```bash
# stdio (local helper) — CLI path
codex mcp add my-server --env API_KEY=secret -- node ./dist/index.js
codex mcp login my-server   # only if the server needs an OAuth handshake

# Streamable HTTP (remote) — CLI path
codex mcp add figma --url https://mcp.figma.com/mcp --bearer-token-env-var FIGMA_OAUTH_TOKEN
codex mcp list
```

Edit `~/.codex/config.toml` directly for fields the CLI doesn't expose: modular tool gating, static headers, and OAuth callback ports.

```toml
# ~/.codex/config.toml — stdio server, full field set
[mcp_servers.my-server]
command = "node"
args = ["./dist/index.js"]
cwd = "/path/to/dir"
startup_timeout_sec = 15
tool_timeout_sec = 120
enabled = true
required = false

[mcp_servers.my-server.env]
API_KEY = "secret"

# ~/.codex/config.toml — remote Streamable HTTP server, full field set
[mcp_servers.figma]
url = "https://mcp.figma.com/mcp"
bearer_token_env_var = "FIGMA_OAUTH_TOKEN"
startup_timeout_sec = 10

[mcp_servers.figma.http_headers]        # static headers
"X-Custom-Header" = "static-value"

[mcp_servers.figma.env_http_headers]    # header value pulled from an env var
"Authorization" = "MY_TOKEN_ENV_VAR"

# Per-server tool gating and approval (Codex's equivalent of deferred loading + permissions)
[mcp_servers.chrome]
enabled_tools = ["open", "screenshot"]
disabled_tools = ["dangerous_tool"]
default_tools_approval_mode = "prompt"  # auto | prompt | writes | approve

[mcp_servers.chrome.tools.open]
approval_mode = "approve"
```

Top-level OAuth callback config (when a remote server drives a browser handshake): `mcp_oauth_callback_port` and `mcp_oauth_callback_url`. Scope: `~/.codex/config.toml` is global; a project-root `.codex/config.toml` is project-scoped and applies only in trusted projects.

> Verify field names and defaults against `codex mcp add --help` and the Codex config reference before relying on them. Codex's MCP config surface has changed before (the CLI gained `--url` after a config-file-only period).

## When to Add Authorization

Authorization is not required for every MCP server.

Add it when:

- the server is remote and shared,
- it exposes sensitive data or write operations,
- the server must act on behalf of a specific user or tenant.

If you add authorization for HTTP, follow the MCP Authorization spec. Also:

- validate token audience/resource,
- keep scopes narrow,
- do not pass MCP bearer tokens through to upstream APIs,
- fail closed on missing or invalid auth.

## Operational Capabilities to Consider

Add these only when the workflow needs them:

- **Structured output (`outputSchema`)**: declare a result schema and return `structuredContent`; the server MUST conform to its own schema. Use it whenever a tool returns data a caller will parse rather than read.
- **Tool annotations** — declare `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` on every tool, not as an optional nicety. See [Tool Annotation Hints](#tool-annotation-hints) below for what each means, when it applies, and why a wrong `destructiveHint` is a safety defect, not a style nit.
- **Resource links** — return `{"type": "resource_link", …}` to point at a resource instead of inlining large content; a key output-bounding tool.
- **Error results**: return recoverable failures as `isError: true` results with actionable text (see [mcp-patterns.md](mcp-patterns.md#tool-result-contract)).
- **Human input** for URL-based auth handoff or explicit approval: MRTR `input_required` results from `2026-07-28`, `elicitation/create` before it. Do not adopt Roots or Sampling in new servers (deprecated, SEP-2577). For auditability, log to stderr or OpenTelemetry instead of protocol Logging.
- **Progress / tasks** for long-running work. The `2026-07-28` revision moved async Tasks out of the core protocol into the official `io.modelcontextprotocol/tasks` extension (poll via `tasks/get`, client input via `tasks/update`, no `tasks/list`). Check your SDK's support before relying on it.

## Tool Annotation Hints

Every tool a custom server implements should declare all four boolean annotation hints in its registration, not just the ones that seem obviously relevant. A client (or a human reviewing an approval prompt) uses these to decide whether a call needs confirmation — get one wrong and the client either under-warns on a dangerous call or over-warns on a safe one until nobody trusts the prompts.

| Hint | Meaning | Set `true` when |
|---|---|---|
| `readOnlyHint` | The tool does not modify its environment | The tool only reads/queries — `get_order`, `list_tables`, `search_docs` |
| `destructiveHint` | The tool may perform destructive updates (only meaningful when `readOnlyHint` is `false`) | The tool can delete, overwrite, or irreversibly change state — `delete_record`, `cancel_order`, `drop_table`. Ignored by clients if `readOnlyHint` is `true`. |
| `idempotentHint` | Calling the tool repeatedly with the same arguments has no additional effect beyond the first call | Re-running the exact call is safe — `set_status(id, "closed")`, `upsert_record`. Leave `false` for anything that appends, increments, or sends (e.g. `send_email`, `create_ticket`) |
| `openWorldHint` | The tool interacts with an open-ended external system rather than a fixed, closed set of resources the server fully controls | The tool calls out to the live internet, a third-party API, or anything the server doesn't have complete inventory of — `web_search`, `call_external_api`. Set `false` for a tool that only touches a bounded, server-owned dataset. |

Why mislabeling `destructiveHint` specifically is a safety problem, not a style nit: annotations are advisory metadata the server asserts about itself — the protocol does not verify them. A client that trusts a false `destructiveHint: false` on a tool that actually deletes data will skip the approval gate it would otherwise show, and the failure looks like a client bug when the defect is actually in the server's own self-description. Treat annotation accuracy as part of the tool's contract, reviewed the same way you'd review the `inputSchema` — not a cosmetic afterthought filled in after the tool works.

Practical defaults when unsure: leave `readOnlyHint: false` unless you've confirmed the tool truly can't write; set `destructiveHint: true` for any write tool unless you've confirmed the write is additive-only; set `idempotentHint: false` unless you've tested the repeat-call case; set `openWorldHint: true` for anything that reaches outside the server's own storage.

## Testing and Validation

### Inspector

The official Inspector is the fastest way to smoke-test your server:

```bash
npx @modelcontextprotocol/inspector node dist/index.js
```

### Minimum Acceptance Checks

- Tool list loads successfully
- One low-cost tool call succeeds
- Recoverable failures (not found, denied, upstream error) return `isError` results with actionable text, not protocol errors
- Pagination / limit controls work
- Large outputs are bounded
- Auth failures stop cleanly after one retry
- Prompt-injection content is treated as data, not instructions

## Registry Publishing

If the server should be discoverable by multiple clients or teams:

1. Add a `server.json` manifest.
2. Publish with `mcp-publisher`.
3. Validate the listing in the official registry.

Do this only after the server surface is stable enough for other clients to depend on.

## Production Checklist

```text
[ ] Tool descriptions say when to use each tool
[ ] Input schemas are strict and minimal
[ ] Output is paginated / bounded
[ ] Writes require explicit approval or are isolated behind narrow tools
[ ] Logs/audit events exist for sensitive operations
[ ] Secrets come from env vars or a secret manager
[ ] Local HTTP binds narrowly and validates Host/Origin
[ ] Remote HTTP uses TLS
[ ] Authorization is implemented only if needed, and correctly
[ ] Inspector smoke test passes
```

## Related

- `references/mcp-security.md`
- `references/mcp-patterns.md`
- `references/mcp-servers.md`
- `references/mcp-evaluation.md` — authoring evaluation questions once a server built here is stable

## Old patterns: v1-era SDK examples

These are v1-era examples. Servers written this way are still common and still run while the v1 line receives fixes. For new code, do the [SDK Lane Lookup](#sdk-lane-lookup) first: the v2 lines renamed packages and classes (according to the Python migration guide, `FastMCP` became `MCPServer`, and TypeScript split into separate server and client packages). The design (narrow tool, strict schemas, `structuredContent`, one transport) carries over unchanged.

### TypeScript (v1 line, single `@modelcontextprotocol/sdk` package)

#### Project Setup

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript tsx @types/node
```

#### Minimal Tool Server

```typescript
import { z } from "zod";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const server = new McpServer({
  name: "my-server",
  version: "1.0.0",
});

server.registerTool(
  "lookup_customer",
  {
    title: "Lookup customer",
    description: "Use this when you need a customer record by ID.",
    inputSchema: {
      customerId: z.string(),
    },
    outputSchema: {
      customerId: z.string(),
      email: z.string().email(),
      status: z.string(),
    },
  },
  async ({ customerId }) => {
    const customer = await getCustomer(customerId);

    return {
      content: [
        {
          type: "text",
          text: `Customer ${customer.id} is ${customer.status}`,
        },
      ],
      structuredContent: {
        customerId: customer.id,
        email: customer.email,
        status: customer.status,
      },
    };
  }
);

const transport = new StdioServerTransport();
await server.connect(transport);
```

#### Resources and Prompts

```typescript
import { z } from "zod";

server.registerResource(
  "schema",
  "schema://orders",
  {
    title: "Orders schema",
    mimeType: "application/json",
  },
  async () => ({
    contents: [
      {
        uri: "schema://orders",
        text: JSON.stringify(await getOrdersSchema(), null, 2),
      },
    ],
  })
);

server.registerPrompt(
  "triage_order",
  {
    title: "Triage order issue",
    description: "Use this when you need a structured support triage prompt.",
    argsSchema: {
      orderId: z.string(),
    },
  },
  async ({ orderId }) => ({
    messages: [
      {
        role: "user",
        content: {
          type: "text",
          text: `Triage order ${orderId} using the current order and payment state.`,
        },
      },
    ],
  })
);
```

### Python (v1 line, in-SDK FastMCP)

#### Project Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]"
```

#### Minimal FastMCP Server

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("my-python-server")

@mcp.tool()
def lookup_invoice(invoice_id: str) -> dict:
    invoice = get_invoice(invoice_id)
    return {
        "invoice_id": invoice["id"],
        "status": invoice["status"],
        "amount": invoice["amount"],
    }

if __name__ == "__main__":
    mcp.run()
```

Avoid unsafe patterns like `eval()` in example code. Even toy snippets become copy-paste production code surprisingly often.
