---
source_snapshot: openai/codex main branch (verified 2026-05-25)
anchors:
  - codex-rs/cli/src/main.rs — McpServer subcommand variant
  - codex-rs/mcp-server/ — codex-mcp crate (src/main.rs, src/lib.rs, src/codex_tool_runner.rs, src/message_processor.rs)
  - codex-rs/app-server-daemon/ — distinct HTTP daemon crate (different transport, different audience)
---

# OpenAI Codex As MCP Server

## When To Use

Use this reference when designing or reviewing the surface that lets external editors or AI runtimes drive Codex over the Model Context Protocol (MCP). It covers the `codex mcp-server` subcommand, the `codex-rs/mcp-server` crate, and the contrast with the existing app-server-daemon.

## What It Covers

- `codex mcp-server` subcommand — stdio MCP server mode
- `codex-rs/mcp-server` crate structure and responsibilities
- How external clients drive Codex as a tool
- Contrast with `codex-rs/app-server-daemon` (HTTP daemon, different transport and audience)
- Approval bridging inside the MCP server path

## The `codex mcp-server` Subcommand

`codex-rs/cli/src/main.rs` exposes a top-level `McpServer` subcommand:

> "Start Codex as an MCP server (stdio)"

When launched, Codex runs as a long-lived stdio process. MCP clients (editors, Claude Code, other agents) connect over standard input/output using the MCP wire protocol. The client sends requests; Codex processes them through its agent loop and returns results.

This is the primary integration path for editors and orchestrators that want to drive Codex as a **tool**, rather than as a UI-bearing terminal application.

## The `codex-rs/mcp-server` Crate

Source: `codex-rs/mcp-server/src/`

Key modules:

| Module | Role |
|--------|------|
| `main.rs` | Entrypoint — bootstraps the MCP stdio server |
| `lib.rs` | Library exports |
| `codex_tool_config.rs` | Tool configuration: which Codex tools are exposed via MCP and with what schema |
| `codex_tool_runner.rs` | Execution engine — routes MCP tool-call requests into Codex's internal agent loop |
| `message_processor.rs` | Parses incoming MCP messages and dispatches to the appropriate handler |
| `outgoing_message.rs` | Formats MCP-compliant responses |
| `exec_approval.rs` | Approval workflow for command execution requests received over MCP |
| `patch_approval.rs` | Approval workflow for code-patch requests received over MCP |

The approval modules (`exec_approval.rs`, `patch_approval.rs`) are notable: because the MCP client may be another AI agent rather than a human, Codex still enforces its approval model. Approvals can be either auto-resolved by policy or forwarded back to the calling client as MCP-formatted elicitation requests.

## How External Clients Drive Codex

```text
editor / Claude Code / orchestrator
  |
  | (MCP wire protocol, stdin/stdout)
  v
codex mcp-server process
  message_processor -> codex_tool_runner
  |
  +--> Codex agent loop (same core as interactive TUI)
  +--> exec_approval / patch_approval (honor AskForApproval policy)
  +--> outgoing_message -> MCP response back to client
```

From the client side, Codex appears as a set of MCP tools (file editing, code execution, search, apply-patch, etc.). The calling runtime never needs to know how Codex implements those tools internally.

## Contrast: MCP Server vs App-Server-Daemon

These are two unrelated remote-integration surfaces with different transports and different audiences:

| Dimension | `codex mcp-server` | `codex-rs/app-server-daemon` |
|-----------|-------------------|------------------------------|
| Transport | stdio (MCP wire) | HTTP (typed REST / OpenAPI) |
| Protocol | Model Context Protocol | JSON/HTTP control protocol |
| Primary audience | Editors, AI orchestrators, MCP clients | Desktop GUI clients, remote-control tooling |
| Crate | `codex-rs/mcp-server` | `codex-rs/app-server-daemon` |
| Companion | `codex mcp-server` CLI subcommand | `codex app-server` / `codex remote-control` |
| Session model | One Codex session per MCP connection | Multiple sessions managed by daemon |
| Approval routing | MCP elicitation back to calling client | Local or remote human UI |

When an editor wants Codex as a background tool, it uses `mcp-server`. When a desktop GUI wants to manage multiple Codex sessions with HTTP round-trips, it uses `app-server-daemon`.

## Design Rules

- Treat the MCP server path as a first-class integration target, not a debugging interface.
- Approval policy (`AskForApproval`) applies equally when the caller is another AI agent; do not auto-approve everything from a "trusted" client.
- The MCP server should not re-implement core business logic; it routes requests through the same `codex_tool_runner` that the interactive session uses.
- Distinguish MCP stdio transport from the HTTP daemon transport in documentation, examples, and error messages — conflating them produces wrong integration guides.
- Editors using the MCP path should receive structured elicitation requests when approval is needed, not silent failures.

## Anti-Patterns

- Treating `codex mcp-server` and `app-server-daemon` as interchangeable because both allow external control. The wire protocol, session model, and audience differ.
- Bypassing `exec_approval` / `patch_approval` on the assumption that the MCP caller is an AI and "already trusted." Policy still applies.
- Building editor integrations as in-process SDK embeds when the `mcp-server` stdio mode already provides a clean, isolated integration boundary.
