# MCP Server Development

Use this file when the request is about exposing a developer tool, SDK, or data source to AI agents via the Model Context Protocol.

Verify SDK names, versions, and tooling availability at [modelcontextprotocol.io](https://modelcontextprotocol.io/) before final recommendations — the ecosystem moves fast.

## Table of Contents

- [When to Expose via MCP vs Conventional SDK/CLI](#when-to-expose-via-mcp-vs-conventional-sdkcli)
- [MCP Architecture: Server vs Client Responsibilities](#mcp-architecture-server-vs-client-responsibilities)
- [Designing Tools, Resources, and Prompts for Agent Consumption](#designing-tools-resources-and-prompts-for-agent-consumption)
- [Decision Table: Tool vs Resource vs Prompt](#decision-table-tool-vs-resource-vs-prompt)
- [Testing an MCP Server Before Publishing](#testing-an-mcp-server-before-publishing)
- [Publishing and Distribution Considerations](#publishing-and-distribution-considerations)
- [Do / Avoid](#do--avoid)
- [Known Traps](#known-traps)

## When to Expose via MCP vs Conventional SDK/CLI

| Situation | MCP server | Conventional SDK/CLI |
|---|---|---|
| Primary consumer is an AI agent or AI-powered IDE | Yes | No |
| Primary consumer is a human developer typing commands | No | Yes |
| Tool surface needs to be discoverable at runtime by an LLM | Yes | No |
| You control the host application (e.g. your own app embeds the agent) | Build an MCP client instead | Yes |
| Output is always structured data consumed programmatically | Both (MCP + `--json` CLI) | Yes |
| Low-volume internal tooling, no agent integration planned | No | Yes |

Build both when: your tool already has a CLI and you want agent-native access without breaking existing workflows. The MCP server wraps the same business logic; the CLI stays for humans.

## MCP Architecture: Server vs Client Responsibilities

**Server** (what you build when exposing your tool):
- Declares **tools**, **resources**, and **prompts** the host can discover.
- Executes tool calls when invoked by the host.
- Manages its own authentication and rate limiting — never assume the host does this.
- Communicates over stdio (local process) or HTTP/SSE (remote) [verify current transport options at modelcontextprotocol.io].

**Client** (the host application — Claude Desktop, VS Code, Cursor, your own agent):
- Discovers available servers and negotiates capabilities.
- Sends tool call requests; receives structured results.
- Owns the conversation context and decides when to invoke which server.

You rarely build a client unless you are building an AI IDE, agent framework, or custom host. Building a server is the 90% case for developer tooling.

## Designing Tools, Resources, and Prompts for Agent Consumption

### Tools (callable actions)

- **One responsibility per tool.** `search_files` and `read_file` are two tools, not one.
- **All inputs as typed parameters.** Agents cannot fill in missing info interactively.
- **Return structured output.** JSON objects with predictable fields; avoid free-form prose blobs agents must parse.
- **Idempotent where possible.** Agents retry on timeout — running the same tool call twice must be safe or return a "already done" signal.
- **Descriptive names and descriptions.** The LLM reads the tool description to decide whether to call it. Write descriptions like short docstrings: what it does, when to use it, what it returns.
- **Actionable errors.** On failure, return a structured error with a code and a message that tells the agent how to recover — not a raw exception stack.

### Resources (readable data)

- Expose read-only data (files, database records, API responses) as resources, not as tools.
- Use stable, predictable URIs so agents can construct resource paths from known patterns.
- Paginate large result sets; do not return multi-megabyte blobs in a single resource response.

### Prompts (reusable templates)

- Use prompts for complex, multi-turn workflows where the server knows the right sequence of tool calls (e.g. a "deploy and verify" workflow).
- Keep prompts optional — agents that do not use them must still reach the same outcome through individual tool calls.

## Decision Table: Tool vs Resource vs Prompt

| Content type | Use |
|---|---|
| Action with side effects (write, deploy, transform) | Tool |
| Read-only data the agent needs as context | Resource |
| Guided multi-step workflow with known structure | Prompt |
| Real-time event stream | Resource with streaming [verify support at modelcontextprotocol.io] |

## Testing an MCP Server Before Publishing

1. **Smoke-test locally** using the official MCP developer tooling (Inspector) [verify current name and install at modelcontextprotocol.io]. The Inspector connects to your server, lists capabilities, and lets you invoke tools manually without an LLM in the loop.
2. **Unit-test tool handlers** in isolation — call the handler function directly with typed inputs, assert the output shape. No MCP protocol overhead needed for this layer.
3. **Protocol-level integration test** — start your server in a subprocess, connect a test MCP client, call each tool, and assert the MCP-formatted response. Catches serialization and capability-negotiation bugs.
4. **Agent smoke test** — run your server with a real agent host (Claude Desktop, VS Code + extension, or a lightweight test harness). Give the agent a task that requires your tool; verify it discovers and uses the tool correctly.
5. **Error path testing** — invoke tools with missing params, bad auth, and unavailable dependencies. Confirm every error returns a structured MCP error, not an unhandled exception that silently breaks the agent.
6. **Idempotency check** — call every write/deploy tool twice with the same arguments. The second call must not duplicate state or crash.

## Publishing and Distribution Considerations

Follow the same hygiene as any developer-facing package (see [publishing-and-support.md](publishing-and-support.md)), plus:

- **Declare transport and auth requirements** in your README up front: stdio vs HTTP, env vars required, OAuth flows if any. Agents and developers need this to configure the host correctly.
- **Version your tool surface.** Renaming or removing a tool is a breaking change — bump the major version. Adding a new tool is additive — minor bump.
- **Publish to a discoverable registry.** The official MCP Registry (registry.modelcontextprotocol.io) launched in preview in late 2025 and had grown to roughly 10,000 server records by mid-2026; it indexes metadata and points to the actual package on npm/PyPI/etc. — it is not itself a package host. It remains in preview (breaking changes possible before GA), so also publish the underlying package to npm/PyPI/crates.io with an `mcp-server` tag for direct discovery. Re-verify registry maturity at modelcontextprotocol.io before treating it as the sole distribution channel.
- **Keep the server stateless where possible.** Stateless servers are easier to scale, test, and restart. Store per-session state in the host or an external store, not inside the server process.
- **Document resource URI patterns.** If your server exposes `files://{path}`, document the scheme and the valid path shapes. Agents construct URIs from documentation, not from exploration.
- **Ship a minimal working configuration example** — a single `claude_desktop_config.json` or equivalent snippet that wires the server to a known-working host. This is the MCP equivalent of a quickstart code sample.

## Do / Avoid

**Do**
- Write tool descriptions as if a mid-level LLM will read them to decide whether to call the tool — be explicit about what the tool does and what it returns.
- Return structured, typed results from every tool — not raw strings.
- Test the error path with the official MCP developer tooling before shipping.
- Version the tool surface using semver; treat tool removal as a breaking change.
- Support stdio transport for local tools; prefer HTTP/SSE for remote or multi-tenant servers [verify at modelcontextprotocol.io].

**Avoid**
- Combining multiple responsibilities in one tool (the LLM will misuse it).
- Returning free-form prose as tool output — agents must be able to parse results programmatically.
- Requiring interactive confirmation mid-tool-call — the agent cannot respond.
- Stateful servers that break when restarted or when a second instance starts alongside the first.
- Shipping without testing through the official MCP developer tooling — surprises in the protocol layer surface late and are hard to debug in production agent sessions.

## Known Traps

- **Description drift**: tool descriptions become stale as implementation changes. Treat them like API docs — update them in the same commit as the implementation.
- **Silent truncation**: returning large payloads that the host truncates quietly leads to agents acting on incomplete data. Paginate proactively.
- **Transport mismatch**: a server designed for stdio fails silently when deployed as HTTP. Test both transports if you intend to support both.
- **Auth assumptions**: never assume the host handles authentication on your behalf. Your server must validate credentials on every tool call.
