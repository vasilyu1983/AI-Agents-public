---
name: ai-coding-agents-remote-runtime
description: "Designs remote execution and bridge runtimes for coding agents. Use when implementing remote sessions, local-UI remote-execution, reconnect logic, or permission bridging."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Remote Runtime

Use this skill to design or review coding-agent runtimes where execution happens remotely but the user still interacts through a local CLI or terminal UI.

This skill covers remote sessions, bridge transports, viewer-only clients, SSH-style local-UI remote-tool flows, and remote approval routing.

## ASCII Flow

```text
local client / terminal UI
  |
  v
bridge transport
  WebSocket | SSE | HTTP POST | ACP stdio | SSH-like tunnel
  |
  v
remote runtime
  agent loop + tools + sandbox + session store
  |
  +--> permission request -> bridge -> local owner decision -> remote execution
  +--> stream events       -> bridge -> local rendering
  +--> reconnect           -> sequence resume or replay from checkpoint
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| What should the remote runtime model look like? | [`references/local-ui-remote-execution-model.md`](references/local-ui-remote-execution-model.md) | Local UI, remote agent loop, viewer modes, and mode boundaries |
| How should bridge transport and approval work? | [`references/bridge-transport-and-permission-bridging.md`](references/bridge-transport-and-permission-bridging.md) | WebSocket control flow, permission bridging, reconnect, and message adaptation |
| Which transport should I use (WebSocket vs SSE vs HTTP POST vs ACP stdio)? | [`references/transport-selection.md`](references/transport-selection.md) | Decision tree, criteria, hybrid patterns, and anti-patterns |
| How do I build reconnect with sequence-number resume? | [`references/recipe-reconnect-with-sequence.md`](references/recipe-reconnect-with-sequence.md) | Step-by-step resumable stream recipe with ring buffer and client reconnect loop |
| How does OpenAI Codex structure app-server and remote-control daemon lifecycle? | [`references/openai-codex-app-server-remote-control.md`](references/openai-codex-app-server-remote-control.md) | Daemon lifecycle, JSON control output, remote host bootstrap, long-running work |
| How does OpenAI Codex keep app-server protocol clients in sync? | [`references/openai-codex-app-server-protocol-codegen.md`](references/openai-codex-app-server-protocol-codegen.md) | Schema-driven TypeScript/JSON artifacts, experimental filtering, fixture tests, and explicit update workflow |
| How does `codex mcp-server` work and how does it differ from the app-server-daemon? | [`references/openai-codex-as-mcp-server.md`](references/openai-codex-as-mcp-server.md) | `McpServer` subcommand, `codex-rs/mcp-server` crate, approval bridging over MCP, contrast with HTTP daemon |

## When To Use

- Design remote coding-agent sessions with a local CLI frontend
- Build bridge or direct-connect transport for a coding-agent runtime
- Add viewer-only remote session clients or assistant-style observers
- Route permission requests from remote execution back to local UI
- Model SSH-like “local REPL, remote tools” behavior

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Session persistence and resume lifecycle | [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md) |
| Tool approval system design | [`../ai-coding-agents-permissions/SKILL.md`](../ai-coding-agents-permissions/SKILL.md) |
| Plugin architecture | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |

## Default Workflow

1. **Separate UI from execution.** Decide what runs locally, what runs remotely, and what state must be mirrored between them.
2. **Treat remote control as a first-class mode.** Viewer-only, full control, SSH proxy, and remote-creation flows should be explicit runtime modes.
3. **Split transcript traffic from control traffic.** Keep SDK or transcript messages separate from typed control requests such as permission prompts, cancellations, reconnect notifications, and unsupported-control errors.
4. **Choose transport shape deliberately.** Reads and writes do not need the same transport. Hybrid patterns such as WebSocket or SSE for reads plus HTTP POST for writes are often easier to recover and reason about than pretending the whole session is one bidirectional pipe.
5. **Bridge unknown tools safely.** Remote execution may reference tools that do not exist in the local client; normalize them into synthetic local renderables instead of failing the UI.
6. **Track pending control requests.** Permission prompts and cancellations need stable request IDs, local bookkeeping, and explicit cleanup so reconnects and late cancellations do not leak stale UI state.
7. **Plan reconnect behavior.** Distinguish transient reconnecting, permanent disconnect, and viewer-only no-interrupt modes. Decide whether the client resumes from sequence numbers, replays from checkpoints, or only reconnects live.
8. **Keep approval local where possible.** Remote execution can ask; the local controller should decide and respond with a structured result.
9. **Test degraded modes.** Verify network drops, reconnect backoff, remote interrupt, stale control requests, unsupported control subtypes, and local or remote command filtering.

## Host Rules

- Local UI and remote execution should share one semantic session contract.
- Control messages should use a typed schema separate from normal transcript messages.
- Reads and writes may use different transports if that improves ordering, retry semantics, or observability.
- Pending permission requests must be keyed, cancellable, and removable from local state when the server cancels or the session dies.
- Remote mode should expose only the commands that make sense in a remote session.
- Unknown remote tools should still render through synthetic local message or tool-stub paths rather than crashing the local UI.
- Viewer-only clients must not accidentally send interrupts or mutate remote state.
- Unsupported control-request subtypes should return a structured error response instead of hanging the remote side.
- SSH-like proxy modes should render locally and execute remotely without pretending they are fully local sessions.

## Build Order

1. Define the shared session contract and runtime modes.
2. Implement typed control messages separately from transcript messages.
3. Stand up the read and write transports, even if they start as one simple channel.
4. Add permission request routing with stable IDs and cancellation.
5. Add reconnect and resume behavior.
6. Add synthetic local rendering for remote-only tools and control events.

## Core Invariants

- The local UI is a controller and renderer, not the source of truth for remote execution.
- Transcript traffic and control traffic must never be ambiguous on the wire.
- Every remote control request must be attributable, cancellable, and terminal.
- Viewer-only sessions must be unable to mutate remote state.
- Unknown remote capabilities must degrade into renderable local objects, not disappear.

## Failure Modes

- Network reconnect loops that duplicate transcript or control events.
- Permission prompts that survive cancellation or session death.
- Local UI trying to execute a remote-only tool directly.
- Viewer clients leaking interrupts or approve actions.
- Remote servers sending unsupported control subtypes with no structured fallback.
- Conflating a cloud-hosted session (execution never touches the user's machine) with a locally-executing session mirrored to another device (execution stays local, only steering moves). They have different data-residency, credential, and failure-domain properties; see the Shipped Reference Implementations table above.

## Minimal Viable Version

- One remote session mode with explicit local-controller ownership.
- One typed message family for transcript events and one for control events.
- Stable request IDs for permission prompts and cancellations.
- Basic reconnect with clear user-visible disconnected versus reconnecting state.
- Remote tool uses rendered locally, even if the local client cannot execute them.

## What Strong Implementations Add

- Hybrid transports with different read and write semantics.
- Sequence-aware resume or replay from checkpoints.
- Viewer-only and SSH-like proxy modes with different capabilities.
- Server-driven cancellation, reconnect backoff, and pending-request cleanup.
- Full telemetry for control latency, reconnect attempts, and approval round-trips.
- **ACP stdio transport** for editor integrations (Zed, JetBrains, etc.) with session-ID re-attach.
- **Local typed-HTTP daemon** (OpenAPI-generated) decoupling GUI clients from the CLI entry point.
- **Schema-driven protocol-method codegen** so the wire contract is source-of-truth for dispatch.

## Known Traps

- Treating transport reconnect as if it were session resume and replaying the wrong in-flight state.
- Assuming the local client and remote runtime share the same tool registry, approval model, or capability envelope.
- Modeling viewer mode as presentation-only and accidentally exposing execution or approval paths that should remain server-owned.
- Leaving permission prompts and pending requests as local UI state instead of durable remote-runtime objects.
- Merging all remote traffic into one chat stream and losing the distinction between control messages, tool results, and durable session state.

## Common Anti-Patterns

- Treating the whole remote session as one undifferentiated chat stream.
- Assuming the local client and remote runtime always share the same tool registry.
- Using transport reconnect as if it were session resume.
- Modeling viewer mode as a UI flag instead of a runtime capability boundary.
- Leaving permission prompts as UI state instead of durable runtime objects.

## Shipped Reference Implementations (July 2026)

The patterns in this skill are not hypothetical — they map onto products you can inspect directly today. Ground any design decision in the real thing before inventing a new taxonomy; verified 2026-07-11:

| Runtime mode this skill describes | Shipped as | Where execution lives | Key primitives |
|---|---|---|---|
| Outbound-poll mirroring / viewer + controller | Claude Code **Remote Control** (`code.claude.com/docs/en/remote-control`) | Stays on the local machine that started it | `claude remote-control` (server mode, `--spawn same-dir\|worktree\|session`, `--capacity N`), `claude --remote-control`/`--rc` (interactive), `/remote-control`/`/rc` (attach existing session), session URL + QR from `claude.ai/code` or the mobile app; outbound HTTPS only, no inbound ports |
| Remote-execution devbox (SSH-stdio) | Claude Code Desktop app's SSH-host connection | Moves to the remote SSH host; agent auto-installs there on first connect | Point-and-connect `ssh user@host`; session history is siloed per surface |
| Cloud-hosted container (no local session) | **Claude Code on the web** (`claude.ai/code`, `--cloud` flag) and **Routines** (`code.claude.com/docs/en/web-scheduled-tasks`) | Anthropic-managed VM/container, fresh per session or per trigger | Repo clone into isolated VM; Routines add schedule/API/GitHub triggers on top of the same cloud-session substrate |
| App-server daemon + typed control | OpenAI Codex `codex app-server` / `codex app-server-daemon` | Local daemon process, `CODEX_HOME`-scoped | `start`/`stop`/`restart`/`enable-remote-control`/`disable-remote-control`/`bootstrap`, one JSON object per command |
| Remote-control infra for SSH/custom clients (distinct from the daemon above) | OpenAI Codex `codex remote-control` (v0.130+) | Local machine, foreground unless a `start` subcommand is used | Foreground `codex remote-control` enables remote control for one invocation; `codex remote-control start/stop/restart` manages the daemon; **this is infrastructure for SSH workflows and custom integrations, not a ready-made browser/QR flow** — Codex's user-facing QR/mobile pairing is mediated by the desktop app, not this CLI command |
| Editor-spawned stdio agent | ACP (Agent Client Protocol, Zed-originated, Apache-licensed) — adopted by Zed, JetBrains, Google, GitHub, and 25+ agents; Goose 2.0 made it the default server mode | Spawned subprocess on the editor's machine | Line-delimited JSON-RPC 2.0 over stdin/stdout; session-ID re-attach on reconnect |

Two naming traps this table exists to prevent:

- Claude Code's and Codex's commands are both called "remote control" but are not peers: Claude's is the primary user-facing entry point (prints its own session URL/QR); Codex's is low-level plumbing that other surfaces (the desktop app) build the user-facing flow on top of. Do not assume feature parity from name similarity alone.
- "Remote Control" (session stays local, mirrored) and "Claude Code on the web" / Routines (session runs in the cloud, nothing local) are Anthropic's own explicit contrast pair, not two names for the same thing. Pick the one that matches your actual failure and data-residency model before designing around either.

## Cloud-Hosted Remote Execution

Modern coding-agent platforms offer a third remote-runtime mode beyond local-to-remote bridge and developer devbox: **cloud-hosted containers** that run without a local session.

**Routines / cloud containers:** a trigger (schedule, API call, GitHub event) starts a fresh cloud container, the agent loop executes, artifacts are persisted, and results are delivered via webhook or session URL. No local machine involvement after trigger. The container lifecycle is: trigger → container start → execute (agent loop + tools + sandbox) → persist artifacts → webhook/session result. Treat as a remote-task lifecycle distinct from local-agent and devbox tasks. **Claude Code on the web** (`claude.ai/code`, or `claude --cloud`) is the on-demand sibling of Routines: same cloud-VM substrate, triggered interactively instead of by schedule/API/webhook, with sessions that persist across browser closes and can run in parallel across repos.

**Codex devboxes:** microVM/Firecracker-style isolated environments for Codex cloud tasks. Lifecycle mirrors Routines but with branched workspaces, multiple terminals, and app/browser tools. The isolation substrate is microVM-class, not container-class — security boundary differs.

**`claude -p` non-interactive execution:** `claude -p "prompt"` runs Claude Code in non-interactive (piped) mode — no terminal UI, output to stdout. This is a first-class primitive for CI/webhook-triggered runs: a CI step or webhook handler calls `claude -p` with the task description and captures the output. It combines with the Responses-API remote session model: the piped execution runs on the local machine but behaves like a remote job from the CI perspective. Authentication, approval mode, and sandbox settings all apply normally.

Design implications:
- Treat Routines-spawned tasks and `claude -p` CI runs as remote-task lifecycle objects, not as local-agent tasks, for ownership and cancellation purposes.
- Both modes are fresh-session each invocation: `AGENTS.md` / `CLAUDE.md` provides context; there is no transcript memory across runs.
- Design prompts to be self-contained per invocation.

## Cross-Platform Patterns (Goose)

Goose 2.0 (AAIF, April 2026) makes ACP the **default server mode** — the daemon starts in ACP mode automatically. HTTP daemon and WebSocket bridge are opt-in overlays, not the primary transport. This is a correction from earlier Goose descriptions where `goose acp` was a subcommand.

Goose ships two remote-runtime shapes worth importing: **ACP stdio as editor transport**, and a **local daemon with typed API** (goosed + OpenAPI). Both shift the skill's default assumption that "remote" means "across the internet."

### ACP (Agent Client Protocol) as local stdio transport

ACP is Zed's line-delimited JSON stdio protocol for editor ↔ agent. In Goose 2.0, ACP is the default server mode; editors (Zed, JetBrains, IntelliJ, PyCharm, WebStorm, VS Code forks) spawn the process and drive it. Reconnect is session-ID re-attach, not replay.

- **Pattern:** treat ACP as a first-class remote transport class alongside WebSocket. The `local UI ↔ remote agent` split still holds — the editor is the UI, the agent process is the executor — but the wire is a spawned subprocess, not a socket.
- **Anti-pattern:** building "IDE integration" as an in-process SDK embed. That couples editor lifecycle to agent lifecycle and makes crashes, upgrades, and custom distros impossible to isolate.
- **Recipe:** separate ACP server plumbing from the agent core. The `goose-acp-macros` pattern (proc-macros that generate method-routing code from the ACP schema) is the right level of indirection — your protocol-method set should be code-generated from the schema, not hand-written and drifting.

### Codegen for protocol methods

When the wire is typed (ACP, MCP, your own bridge protocol), hand-written method dispatch drifts from the schema as protocols evolve. Goose uses `goose-acp-macros` to generate handler scaffolding at compile time from the ACP meta/schema JSON.

- **Pattern:** treat the protocol schema as source-of-truth; generate server method dispatch, client stubs, and message validators from it.
- **Anti-pattern:** copy-pasting message type definitions into handwritten `match` arms. Every protocol bump becomes a multi-file change with nothing to verify against.
- **Recipe:** commit `acp-schema.json` (or equivalent) to the repo. CI regenerates dispatch code and fails the build if handwritten code diverges.

### Local daemon with typed HTTP API (goosed + OpenAPI)

Goose's desktop UI does not spawn the CLI for each action. A background daemon (`goosed`) runs, and the UI calls it through an OpenAPI-typed HTTP surface. The UI and daemon regenerate client/server code from the OpenAPI spec on each build.

- **Pattern:** model local multi-process coding agents as UI → typed-RPC → daemon, with session state owned by the daemon and the UI treated as one of many possible clients.
- **Anti-pattern:** the UI calling `goose` or `claude` as a shell subprocess and parsing stdout. That is fine for a CLI-native experience but produces fragile GUIs and makes multi-window or multi-agent coordination impossible.
- **Recipe:** version the daemon API separately from the binary (see `ai-coding-agents-release-distribution` — API version is its own compatibility contract). Provide an auto-generated OpenAPI client as the install-time artifact for third-party UIs.

### Agent-as-ACP-client delegation

ACP is bidirectional in practice: Goose can *also* act as an ACP client and delegate work to Claude Code or Codex running as ACP servers. This is the mirror image of the transport discussed above, and the skill's existing Viewer-only / SSH-proxy / Full-control mode taxonomy needs a fourth mode: **agent-delegating**, where the local runtime is neither UI nor executor — it is orchestrator.

- **Pattern:** add `agent-delegating` as a named mode; its control messages and approval routing follow the same typed-message discipline as the others.
- **Anti-pattern:** implementing delegation inside the provider layer (see `ai-coding-agents-provider-runtime` — agent-as-provider belongs there) *and* as a remote-runtime mode. Pick one; they interact but are not duplicates. Provider-level delegation is turn-scoped; remote-runtime delegation is session-scoped.

## Navigation

### References

- [`references/local-ui-remote-execution-model.md`](references/local-ui-remote-execution-model.md) — Local UI, remote agent loop, viewer-only mode, and SSH-style execution
- [`references/bridge-transport-and-permission-bridging.md`](references/bridge-transport-and-permission-bridging.md) — WebSocket control messages, permission routing, reconnect, and SDK-to-REPL adaptation
- [`references/transport-selection.md`](references/transport-selection.md) — Decision tree for WebSocket vs SSE vs HTTP POST vs ACP stdio
- [`references/recipe-reconnect-with-sequence.md`](references/recipe-reconnect-with-sequence.md) — Resumable stream recipe with sequence numbers and client reconnect loop
- [`references/openai-codex-app-server-remote-control.md`](references/openai-codex-app-server-remote-control.md) — OpenAI Codex app-server daemon lifecycle, machine-readable remote control, bootstrap, and long-running work
- [`references/openai-codex-app-server-protocol-codegen.md`](references/openai-codex-app-server-protocol-codegen.md) — OpenAI Codex app-server protocol codegen, experimental method filtering, and schema fixture validation
- [`references/openai-codex-as-mcp-server.md`](references/openai-codex-as-mcp-server.md) — `codex mcp-server` subcommand, `codex-rs/mcp-server` crate, approval bridging over MCP, contrast with app-server-daemon

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and source references for remote runtime guidance

### Related Skills

- [`../ai-coding-agents-permissions/SKILL.md`](../ai-coding-agents-permissions/SKILL.md)
- [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md)
- [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- The core patterns (typed control messages, permission bridging, reconnect states) were originally grounded in an internal April 2026 `claude_code` source snapshot; the Shipped Reference Implementations section above replaces that internal grounding with the live, citable product docs (`code.claude.com/docs/en/remote-control`, `code.claude.com/docs/en/claude-code-on-the-web`, `code.claude.com/docs/en/web-scheduled-tasks`), verified 2026-07-11.
- Exact flags, defaults, and version gates (e.g. `--spawn`, `--capacity`, minimum CLI versions noted in the Claude Code docs, Codex's `codex remote-control` subcommand set) move monthly. Re-check the live docs before quoting an exact flag name or version number in user-facing guidance.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
