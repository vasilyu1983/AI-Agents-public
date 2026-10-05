---
name: ai-coding-agents-surfaces
description: "Designs user-facing surfaces of coding-agent runtimes: remote and bridge sessions, transports, reconnect, terminal REPL, input history. Use when building agent UIs."
compatibility: Portable core. Works on Claude Code and Codex.
version: "2.0"
last_validated: 2026-09-29
---

# AI Coding Agents Surfaces

Use this skill to design or review where a coding-agent runtime meets the user: a local CLI or terminal UI in front of execution that may run remotely, plus the bridges, transports and approval routing between them. The terminal UI and the remote runtime are one design problem: the UI renders and controls runtime state it does not own, and the wire between the two must carry typed control traffic.

It covers remote sessions, bridge transports, viewer-only clients, SSH-style local-UI remote-tool flows, REPL structure, prompt input, message rendering, command queues, virtualized history, interrupts, notifications and background-task navigation. It is not generic desktop app UX.

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| What should the remote runtime model look like? | [references/local-ui-remote-execution-model.md](references/local-ui-remote-execution-model.md) | Local UI, remote agent loop, viewer modes, mode boundaries, version skew |
| How should bridge transport and approval work? | [references/bridge-transport-and-permission-bridging.md](references/bridge-transport-and-permission-bridging.md) | WebSocket control flow, permission bridging, reconnect, message adaptation |
| Which transport (WebSocket vs SSE vs HTTP POST vs ACP stdio)? | [references/transport-selection.md](references/transport-selection.md) | Decision tree, criteria, hybrid patterns, anti-patterns |
| How do I build reconnect with sequence-number resume? | [references/recipe-reconnect-with-sequence.md](references/recipe-reconnect-with-sequence.md) | Resumable stream recipe with ring buffer and client reconnect loop |
| How do editors talk to agents (ACP), and how does codegen keep methods in sync? | [references/acp-editor-transports-and-agent-delegation.md](references/acp-editor-transports-and-agent-delegation.md) | ACP stdio transport, protocol codegen, the agent-delegating mode |
| How does Codex structure app-server and remote-control lifecycle? | [references/openai-codex-app-server-remote-control.md](references/openai-codex-app-server-remote-control.md) | Daemon lifecycle, JSON control output, remote host bootstrap, long-running work |
| How does Codex keep app-server protocol clients in sync? | [references/openai-codex-app-server-protocol-codegen.md](references/openai-codex-app-server-protocol-codegen.md) | Schema-driven artifacts, experimental filtering, fixture tests, update workflow |
| What did Codex's MCP-server mode look like (historical)? | [references/openai-codex-as-mcp-server.md](references/openai-codex-as-mcp-server.md) | Historical: the removed subcommand; lesson on approval bridging when a runtime is exposed over MCP |
| How should the REPL, prompt and history work? | [references/repl-message-input-and-history.md](references/repl-message-input-and-history.md) | Message model, prompt queue, input behavior, interrupt handling |
| How should background work and large histories render? | [references/background-work-notifications-and-virtualization.md](references/background-work-notifications-and-virtualization.md) | Background-task UX, notifications, virtual scroll, teammate navigation |
| Input states and keybindings for background navigation? | [references/input-state-machine.md](references/input-state-machine.md) | State machine, transition table, mode keybindings, vendor-example bindings, reserved keys |
| How do ToolSearch deferred-tool results render? | [references/recipe-toolsearch-render.md](references/recipe-toolsearch-render.md) | Discovery annotation, collapse behavior, permission-prompt sequencing, scroll rules |
| Which Codex TUI patterns should be snapshot-tested? | [references/openai-codex-tui-status-and-snapshot-patterns.md](references/openai-codex-tui-status-and-snapshot-patterns.md) | Status line/title, approval modals, warnings, narrow-terminal states |
| TUI framework choice, fixed-grid rendering, dual-surface CLI+desktop, status-line and keybinding parity traps | [references/tui-rendering-patterns-and-shipped-cli-parity.md](references/tui-rendering-patterns-and-shipped-cli-parity.md) | One framework per surface, pre-truncation, shared protocol, parity checks |

## When To Use

- Design remote coding-agent sessions with a local CLI frontend, or SSH-like "local REPL, remote tools" behavior
- Build bridge or direct-connect transport, viewer-only clients, or editor (ACP) integrations
- Route permission requests from remote execution back to the local UI
- Design a terminal-first REPL, prompt input, history, search, interrupt and notification behavior
- Add background-task surfaces, teammate navigation, or task detail dialogs
- Improve large-session rendering with virtualization or deferred updates
- Separate interactive UI behavior from headless, remote or SDK behavior

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Session persistence, resume, background-task runtime design | [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) |
| Tool approval system design | [`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md) |
| Plugin architecture | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| Cloud sandbox isolation substrate (container vs VM) | `ai-coding-agents-cloud-sandboxes` |
| Provider-level agent-as-provider delegation (turn-scoped) | [`../ai-coding-agents-provider-runtime/SKILL.md`](../ai-coding-agents-provider-runtime/SKILL.md) |
| Generic UI/UX design | [`../software-ui-ux-design/SKILL.md`](../software-ui-ux-design/SKILL.md) |

## Remote and Bridge Workflow

1. **Separate UI from execution.** Decide what runs locally, what runs remotely, and what state must be mirrored.
2. **Treat remote control as a first-class mode.** Viewer-only, full control, SSH proxy, agent-delegating and remote-creation flows are explicit runtime modes.
3. **Split transcript traffic from control traffic.** Keep SDK or transcript messages separate from typed control requests (permission prompts, cancellations, reconnect notifications, unsupported-control errors).
4. **Choose transport shape deliberately.** Reads and writes need not share a transport; WebSocket or SSE for reads plus HTTP POST for writes is often easier to recover than one bidirectional pipe.
5. **Bridge unknown tools safely.** Normalize tools that do not exist in the local client into synthetic local renderables instead of failing the UI.
6. **Track pending control requests.** Permission prompts and cancellations need stable request IDs, local bookkeeping and explicit cleanup so reconnects and late cancellations do not leak stale UI state.
7. **Plan reconnect behavior.** Distinguish transient reconnecting, permanent disconnect and viewer-only no-interrupt modes; decide whether the client resumes from sequence numbers, replays from checkpoints, or only reconnects live.
8. **Keep approval local where possible.** Remote execution can ask; the local controller decides and answers with a structured result.
9. **Make replay idempotent.** Give transcript and control events monotonic sequence numbers plus stable operation IDs; on reconnect, deduplicate by operation ID, acknowledge the highest contiguous sequence, and never replay a side effect merely because its acknowledgement was lost.
10. **Test degraded modes.** Network drops, reconnect backoff, remote interrupt, stale control requests, unsupported control subtypes, local versus remote command filtering.

### Remote Host Rules

- Local UI and remote execution share one semantic session contract; control messages use a typed schema separate from transcript messages.
- Pending permission requests are keyed, cancellable, and removed from local state when the server cancels or the session dies.
- Remote mode exposes only the commands that make sense remotely. Viewer-only clients must be unable to send interrupts, approve, or mutate remote state; model viewer mode as a runtime capability boundary, not a UI flag.
- Unsupported control-request subtypes return a structured error instead of hanging the remote side.
- Client and daemon versions skew: negotiate protocol version and capabilities at connect, refuse with a typed incompatibility error when ranges do not overlap, and upgrade the daemon before clients. See [Client and Daemon Version Skew](references/local-ui-remote-execution-model.md#client-and-daemon-version-skew).
- SSH-like proxy modes render locally and execute remotely without pretending to be fully local sessions.
- Transport reconnect is not session resume; do not replay the wrong in-flight state.

### Naming and Hosting Traps

- A shared command name does not mean a shared role: one product's "remote control" may be a user-facing steering entry point and another's low-level daemon plumbing. Check the role before assuming parity.
- A locally-executing session mirrored to another device (execution stays local, only steering moves) and a cloud-hosted session (execution never touches the user's machine) are different runtime modes with different data-residency, credential and failure-domain properties.
- Remote-control features can be switched off by managed or organization policy or be unavailable under zero-data-retention arrangements; check the vendor's current remote-control and admin-settings docs before depending on one.
- A cloud-hosted run started by a trigger (schedule, API call, repository event) or an interactive request is a remote-task lifecycle object: trigger, workspace start, execute, persist artifacts, deliver by webhook or session URL. Treat it as distinct from local-agent and devbox tasks for ownership and cancellation. Ownership is split: [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) owns the trigger and background-run lifecycle (schedules, routines, webhook and queue triggers); `ai-coding-agents-cloud-sandboxes` owns where the code runs after the laptop closes; [`../software-paas-hosting/SKILL.md`](../software-paas-hosting/SKILL.md) owns hosting your own trigger service; this skill keeps only the UI and transport for these runs.

## Terminal UI Workflow

1. **Keep the REPL a host-owned state machine.** Prompt input, message history, background tasks and overlays share one session model; the UI must not own semantic state the runtime cannot restore.
2. **Separate transcript data from render strategy.** Large histories need virtualization and deferred rendering, not truncated state ownership. Optimize mounting and scroll math, not just terminal paint.
3. **Use dedicated stores for high-frequency signals.** Command queues, scroll state and background-task counts must not force full-tree re-renders.
4. **Treat interrupt behavior as first-class UX.** Idle escape, active interrupt, teammate-view escape and remote interrupt are different actions with different keys and runtime effects.
5. **Make background work navigable.** Inspect, foreground or kill tasks without losing the main session; a badge count alone is not a surface.
6. **Model interactive-only features explicitly** so they do not leak into headless, remote or viewer-only paths.
7. **Cover every task transition in the UI.** For queued, running, needs-input, cancelling, failed, completed and disconnected states, define the visible label, available action, keyboard path, screen-reader text, and the runtime event that clears it.
8. **Test long sessions.** Search, rewind, virtualization, notification timing and prompt-input persistence after hundreds of turns.

### Terminal Host Rules

- Prompt input survives round-trips through overlays, interrupts and search.
- Interactive UI degrades cleanly when the runtime is headless, remote or viewer-only.
- Use one TUI framework per surface, native to the runtime's language; a desktop client uses the same typed daemon or ACP protocol as the CLI, so message blocks, keybindings and interrupt semantics live at the protocol level.
- Before claiming parity with a shipped CLI, read its current keybinding, status-line and agent-teams docs; presenting a plausible key or field as fact is the dominant failure. Status-line, keybinding and split-pane traps are in [references/tui-rendering-patterns-and-shipped-cli-parity.md](references/tui-rendering-patterns-and-shipped-cli-parity.md).
- Internal-runtime patterns (REPL ownership, virtual scroll) are illustrative design guidance, not documented product behavior; label them so.

## Build Order

1. Define the shared session contract, runtime modes, and the host-owned REPL state machine.
2. Implement typed control messages separately from transcript messages; separate transcript data from render state and scroll math.
3. Stand up read and write transports, even if they start as one simple channel.
4. Add permission request routing with stable IDs and cancellation; add prompt input persistence through overlays and interrupts.
5. Add reconnect and resume behavior; add background-task navigation and notifications.
6. Add virtualization for long histories.
7. Add synthetic local rendering for remote-only tools, and remote, headless and viewer-only degradation rules.

## Core Invariants

- The local UI is a controller and renderer, not the source of truth for remote execution or session state.
- Transcript traffic and control traffic are never ambiguous on the wire.
- Every remote control request is attributable, cancellable and terminal.
- Viewer-only sessions cannot mutate remote state; unknown remote capabilities degrade into renderable local objects, not disappear.
- Prompt input survives mode changes; interrupt semantics map to explicit runtime actions.
- Long-session performance comes from virtualization, never silent truncation of semantic history.

## Failure Modes

- Reconnect loops that duplicate transcript or control events; permission prompts that survive cancellation or session death.
- Local UI trying to execute a remote-only tool directly; viewer clients leaking interrupts or approvals.
- Remote servers sending unsupported control subtypes with no structured fallback; all remote traffic merged into one chat stream.
- Losing prompt input when entering search, overlays or teammate views; idle escape, active interrupt and exit collapsed into one key path.
- Background dialogs drifting out of sync with runtime task state; scroll jumps and mount churn on resize or replay.
- Interactive-only affordances leaking into headless or viewer-only modes; history performance "solved" by discarding structure that replay, accessibility or auditing needs.

## Minimal Viable Version

- One remote session mode with explicit local-controller ownership, one typed message family each for transcript and control events, stable request IDs for prompts and cancellations, basic reconnect with visible disconnected versus reconnecting state, remote tool uses rendered locally.
- One host-owned REPL state machine, one persistent prompt input, one explicit interrupt path for active turns, one navigable background-task surface, one virtualization strategy for long histories.

## What Strong Implementations Add

- Hybrid transports, sequence-aware resume or checkpoint replay, viewer-only and SSH-like proxy modes with different capabilities, server-driven cancellation and pending-request cleanup, and telemetry for control latency, reconnects and approval round-trips.
- ACP stdio transport for editor integrations with session-ID re-attach, a local typed-HTTP daemon decoupling GUI clients from the CLI, schema-driven protocol codegen, and an `agent-delegating` mode (orchestrator, neither UI nor executor); see [references/acp-editor-transports-and-agent-delegation.md](references/acp-editor-transports-and-agent-delegation.md).
- Teammate navigation and task-detail overlays with state preservation, resize-stable virtual scroll, notification queues that do not steal focus, and UI restrictions that match runtime capability.

## Navigation

- References: the Quick Reference table lists every file in `references/`.
- Data: [`data/sources.json`](data/sources.json) holds primary documentation and source references.
- Related: [`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md), [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md), [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md), [`../software-ui-ux-design/SKILL.md`](../software-ui-ux-design/SKILL.md).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
