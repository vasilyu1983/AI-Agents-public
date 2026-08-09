# Building Custom MCP Servers

Build a custom MCP server when no existing registry or vendor server fits your workflow, or when you need to enforce domain-specific auth, approval, or data-shaping rules.

## Table of Contents

- [Build Defaults](#build-defaults)
- [Capability Selection](#capability-selection)
- [Transport Selection](#transport-selection)
- [TypeScript (Recommended)](#typescript-recommended)
- [Project Setup](#project-setup)
- [Minimal Tool Server](#minimal-tool-server)
- [Resources and Prompts](#resources-and-prompts)
- [Tool Design Guidance](#tool-design-guidance)
- [Python (Recommended)](#python-recommended)
- [Project Setup](#project-setup)
- [Minimal FastMCP Server](#minimal-fastmcp-server)
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

## Build Defaults

- **Protocol baseline**: MCP specification `2025-11-25`
- **Production SDK lane**: stable **v1** docs
- **TypeScript**: prefer `McpServer`
- **Python**: prefer `FastMCP`
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
| Roots | The client should declare approved working directories or resources |
| Sampling | The server needs controlled access to model inference |
| Elicitation | The server must ask the human for input, approval, or URL-based auth |
| Logging / tasks | The server does long-running or operationally sensitive work |

Do not implement every capability “because it exists”. Add only what removes real client friction.

## Transport Selection

| Scenario | Transport |
|---------|-----------|
| Local helper launched by the client | `stdio` |
| Shared service accessed by multiple users/clients | Streamable HTTP |
| Older remote server needing backwards compatibility | legacy SSE / HTTP+SSE only as fallback |

## TypeScript (Recommended)

### Project Setup

```bash
mkdir my-mcp-server && cd my-mcp-server
npm init -y
npm install @modelcontextprotocol/sdk zod
npm install -D typescript tsx @types/node
```

### Minimal Tool Server

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

### Resources and Prompts

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

### Tool Design Guidance

- Give every tool a concrete “Use this when…” description.
- Prefer structured output via `structuredContent` and `outputSchema`.
- Enforce limits server-side: row counts, page sizes, timeout budgets.
- Keep tool arguments narrow. One focused tool beats one giant “do everything” tool.

## Python (Recommended)

### Project Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install "mcp[cli]"
```

### Minimal FastMCP Server

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

The `codex mcp add` CLI handles **both transports directly**: stdio via `--env` + the `--` separator, and Streamable HTTP via `--url` + `--bearer-token-env-var` (added in `openai/codex` PR #4904, merged 2025-10-08 — confirmed current against `codex mcp add --help` on codex-cli 0.144.1). There is still **no `--transport` flag**; transport is inferred from `--url` vs. a trailing stdio command. OAuth-specific flags (`--oauth-client-id`, `--oauth-resource`) exist on `add` too, or run `codex mcp login` after the fact.

```bash
# stdio (local helper) — CLI path
codex mcp add my-server --env API_KEY=secret -- node ./dist/index.js
codex mcp login my-server   # only if the server needs an OAuth handshake

# Streamable HTTP (remote) — CLI path
codex mcp add figma --url https://mcp.figma.com/mcp --bearer-token-env-var FIGMA_OAUTH_TOKEN
codex mcp list
```

Editing `~/.codex/config.toml` directly is still required for fields the CLI doesn't expose: modular tool gating, static headers, and OAuth callback ports.

```toml
# ~/.codex/config.toml — stdio server, full field set
[mcp_servers.my-server]
command = "node"
args = ["./dist/index.js"]
cwd = "/path/to/dir"
startup_timeout_sec = 15        # default 10; startup_timeout_ms is an accepted alias
tool_timeout_sec = 120          # default 60
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

> Verify field names against the current Codex CLI (`codex mcp add --help`) or `learn.chatgpt.com/docs/config-file/config-reference` before relying on them — Codex's MCP config surface has changed at least once (CLI gained `--url` after the config-file-only period) and may change again.

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

- **Structured output (`outputSchema`)** — declare a result schema and return `structuredContent`; the server MUST conform to its own schema. Use it whenever a tool returns data a caller will parse rather than read. (Stable since `2025-06-18`.)
- **Tool annotations** — declare `readOnlyHint`, `destructiveHint`, `idempotentHint`, `openWorldHint` on every tool, not as an optional nicety. See [Tool Annotation Hints](#tool-annotation-hints) below for what each means, when it applies, and why a wrong `destructiveHint` is a safety defect, not a style nit.
- **Resource links** — return `{"type": "resource_link", …}` to point at a resource instead of inlining large content; a key output-bounding tool.
- **Roots** for filesystem-aware agents
- **Elicitation** for URL-based auth handoff or explicit human input (flat JSON Schema only). Note: the `2026-07-28-RC` folds elicitation, sampling, and roots into Multi Round-Trip Requests — do not hard-couple to today's elicitation shape if you expect to track the RC.
- **Sampling** only if the server genuinely needs model access
- **Logging** for auditability and incident response
- **Progress / tasks** for long-running work. Async **Tasks** (poll via `tasks/get`, mid-flight input via `tasks/update`) are experimental in `2025-11-25` (and in python-sdk ≥ 1.28.0); they move to the `io.modelcontextprotocol/tasks` extension in the RC. Treat as experimental.

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
- Invalid arguments return clean errors
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
