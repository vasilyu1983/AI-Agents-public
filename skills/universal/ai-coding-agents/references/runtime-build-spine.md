# Runtime Build Spine

Moved from the hub SKILL.md. For building a coding-agent runtime (Track B), not for defining an agent on an existing platform. Each item names the skill that owns it.

## Recommended Build Order

For a new CLI coding-agent runtime, treat these subsystems as a fixed spine — not one prompt plus a tool runner — and implement them in this order:

1. settings and policy layering — defines what the runtime is allowed to do (owner: [`ai-coding-agents-settings-policy`](../../ai-coding-agents-settings-policy/SKILL.md))
2. command registry and lazy command loading — how users and the host invoke higher-level actions (owner: [`ai-coding-agents-runtime-core`](../../ai-coding-agents-runtime-core/SKILL.md))
3. provider abstraction, streaming normalization, and context-window policy (owner: [`ai-coding-agents-provider-runtime`](../../ai-coding-agents-provider-runtime/SKILL.md))
4. execution sandbox, workspace mounts, network policy, and destructive-command guards — the real security envelope (owner: [`ai-coding-agents-safety-envelope`](../../ai-coding-agents-safety-envelope/SKILL.md))
5. tool contract, built-in enumeration, and tool-pool assembly (owner: [`ai-coding-agents-runtime-core`](../../ai-coding-agents-runtime-core/SKILL.md))
6. permission context and approval routing — decides when risky actions are allowed (owner: [`ai-coding-agents-safety-envelope`](../../ai-coding-agents-safety-envelope/SKILL.md))
7. central tool-execution pipeline (owner: [`ai-coding-agents-runtime-core`](../../ai-coding-agents-runtime-core/SKILL.md))
8. session persistence, history, and resume — decides what state survives (owner: [`ai-coding-agents-state`](../../ai-coding-agents-state/SKILL.md))
9. remote transport and permission bridging (owner: [`ai-coding-agents-surfaces`](../../ai-coding-agents-surfaces/SKILL.md))
10. task runtime and teammate orchestration — long-running and delegated work (owner: [`ai-coding-agents-state`](../../ai-coding-agents-state/SKILL.md))
11. terminal UI, background-task surfaces, and virtualization — renders and controls runtime state without owning it (owner: [`ai-coding-agents-surfaces`](../../ai-coding-agents-surfaces/SKILL.md))
12. plugin loading, versioned cache, and managed extension policy (owner: [`ai-coding-agents-plugins`](../../ai-coding-agents-plugins/SKILL.md))
13. observability, replay, regression evals, and release gates — closes the feedback loop (owner: [`ai-coding-agents-observability-evals`](../../ai-coding-agents-observability-evals/SKILL.md))
14. update channels, migrations, and distribution — keeps upgrades, caches, and compatibility survivable (owners: [`ai-coding-agents-settings-policy`](../../ai-coding-agents-settings-policy/SKILL.md) for update channels and version pins; [`ai-coding-agents-plugins`](../../ai-coding-agents-plugins/SKILL.md) for cache and upgrade compatibility; [`software-devtools`](../../software-devtools/SKILL.md) for packaging and signing)

Why this order:

- earlier layers define the contracts later layers consume
- permission and session flows are hard to retrofit once tools and UI exist
- remote runtime, tasks, and terminal UI depend on stable command, tool, and settings semantics
- plugins should land after the host runtime has clear ownership of precedence and trust boundaries

If one of these is missing, the usual outcome is not "slightly worse UX." The usual outcome is hidden fragility that appears under reconnects, long sessions, remote control, worker delegation, or upgrades.

## Cross-platform validation

The spine above is derived from the Claude Code lineage and cross-checked against Goose (Rust, MCP+ACP, OSS). Patterns that appeared in the Claude Code lineage but were missing in Goose have been imported into the subsystem skills into the subsystem skills as Goose patterns in their references. When designing a new runtime, read the Claude-Code-derived core *and* the Goose additions in each subsystem skill before committing to an architecture.

## Core Invariants

- one host-owned state model per subsystem
- typed contracts between subsystems instead of implicit shared assumptions
- cache invalidation is explicit and event-driven, not "restart and hope"
- recovery behavior classified by failure family, not generic retry loops
- approvals and sandboxing treated as runtime architecture, not prompt wording
- resume, remote control, and background work designed before polish layers
- telemetry keeps causal order and low-cardinality dimensions
- observability able to explain why the runtime did what it did

## Common False Shortcuts

- building the agent as “LLM + tools + prompt” with no subsystem boundaries
- adding permissions before sandboxing or vice versa and pretending they are interchangeable
- bolting on session resume after tools, UI, and remote flows already exist
- treating remote execution as “the same session over the network”
- memoizing discovery and registry state with no invalidation plan
- shipping plugins before the host owns precedence, trust, and cache policy
- letting cache identity ignore install context, path, or versioned state
- adding evals only after incidents instead of using them as a design constraint
- assuming a good local prototype will survive upgrades, worktrees, and delegation unchanged
