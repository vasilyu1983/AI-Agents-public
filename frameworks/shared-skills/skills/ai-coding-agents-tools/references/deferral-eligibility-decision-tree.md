# Deferral Eligibility Decision Tree

Use this reference when deciding whether a tool should be deferred behind ToolSearch (withheld from turn-one tool list) or always loaded. Decide at tool-registration time, before session startup.

## Table of Contents

- [Decision Tree](#decision-tree)
- [Summary Table](#summary-table)
- [Criteria explained](#criteria-explained)
- [Override: alwaysLoad_overrides](#override-alwaysload_overrides)
- [Anti-patterns](#anti-patterns)
- [Related](#related)

## Decision Tree

```
Start: Should this tool be deferred?
│
├── Is the tool required for the agent to function on turn one?
│   (e.g., Read, Bash, ToolSearch itself)
│   └── YES → alwaysLoad = true. Never defer.
│
├── Is the tool used in > 50% of sessions?
│   (analytics-based; default to NO if unknown)
│   └── YES → alwaysLoad = true. Deferral cost (extra round-trip) outweighs
│             prompt-cache savings for tools the model almost always needs.
│
├── Does the tool schema contribute significantly to token count?
│   (rough threshold: > 800 tokens for the schema + description)
│   └── NO  → alwaysLoad = true. Small schemas add negligible cache-miss cost.
│   └── YES → continue ↓
│
├── Is the tool from an MCP server that may not be connected every session?
│   └── YES → shouldDefer = true. MCP tools are per-session; loading all of them
│             on turn one forces cache invalidation when any server connects/disconnects.
│
├── Is the tool a large or complex MCP extension (e.g., full Stripe API surface)?
│   └── YES → shouldDefer = true. Large extension manifests are the primary
│             motivation for deferral; load only when the model queries for them.
│
├── Is the tool a rarely-used built-in (used in < 10% of sessions)?
│   └── YES → shouldDefer = true. Reduces the stable cache prefix size
│             for the majority of sessions that never use it.
│
├── Is the tool a plugin-provided capability gated by settings/policy?
│   └── YES → shouldDefer = true AND require policy trust class to load
│             (see deferred-tool-policy-layer.md). Loading before policy
│             is confirmed leaks capability into the model's planning.
│
└── None of the above
    └── Default: alwaysLoad = true. When in doubt, load on turn one.
        Deferral adds a round-trip; only defer when the cache benefit
        clearly outweighs the latency cost.
```

## Summary Table

| Criterion | Defer? | Reasoning |
|-----------|--------|-----------|
| Required for turn-one agent function | No — alwaysLoad | Agent cannot operate without it |
| Used in > 50% of sessions | No — alwaysLoad | Round-trip cost outweighs cache benefit |
| Schema < 800 tokens | No — alwaysLoad | Negligible cache impact |
| MCP tool (connection is per-session) | Yes — shouldDefer | Cache stability across session topologies |
| Large/complex MCP extension | Yes — shouldDefer | Primary motivation for deferral |
| Built-in used in < 10% of sessions | Yes — shouldDefer | Stable cache prefix for majority |
| Policy-gated capability | Yes — shouldDefer + trust gate | Prevent premature capability planning |
| Unknown / unclear | No — alwaysLoad | Safe default; defer only when justified |

## Criteria explained

### Turn-one necessity

Tools the agent must call to start any task — file reading, shell execution, ToolSearch itself — must be always-loaded. Deferring them creates a circular dependency: the agent needs the tool to discover the tool.

### Session frequency

If telemetry shows a tool is called in most sessions, deferring it saves no cache hits in practice but adds a round-trip on every session. Use session-frequency data; if it is unavailable, default to alwaysLoad.

### Schema token size

The prompt-cache benefit of deferral comes from keeping the stable prefix smaller. A 200-token schema has minimal impact on cache prefix size. A 3000-token schema for a complex MCP extension is the canonical use case for deferral.

### MCP topology instability

MCP servers connect and disconnect per session. If any MCP tool is in the always-loaded list and its server is not connected, the tool list changes between sessions — cache miss on every topology difference. Deferring all MCP tools except explicit overrides is the standard mitigation.

### Policy gating

A tool that requires a trust class above the current session's settings layer must be deferred. Loading it on turn one makes it visible in the model's planning context before policy is confirmed. The policy layer and deferral eligibility interact: `deferred-tool-policy-layer.md` documents the settings that govern this.

## Override: alwaysLoad_overrides

The settings layer supports an `always_load_overrides` list that promotes specific tools to always-loaded regardless of their `shouldDefer` flag:

```json
{ "always_load_overrides": ["mcp__github__create_pull_request"] }
```

Use this for teams that use a specific MCP tool in nearly every session and want to pay the slightly larger cache prefix for the latency savings.

## Real-World Calibration (Claude Code, July 2026)

Since Claude Code v2.1.69, tool search covers built-in tools too, not only MCP tools — refine the "MCP tools defer, built-ins mostly don't" heuristic above with this observed split rather than guessing from first principles:

- **Always-loaded in practice:** `Read`, `Edit`, `Write`, `Bash`, `Grep`, `Glob`, `Agent`, `Skill`, and `ToolSearch` itself — the tools nearly every coding session needs on turn one.
- **Deferred by default in practice:** `WebFetch`, `WebSearch`, `Monitor`, `NotebookEdit`, `SendMessage`, `TaskStop`, worktree-management tools (`EnterWorktree`, `ExitWorktree`), and most MCP-provided tools.

This lines up with the criteria above: the always-loaded set is turn-one-necessary plus high session frequency; the deferred set is useful sometimes but expensive if loaded unconditionally in every session. Recalibrate a new tool's `alwaysLoad`/`shouldDefer` flag against this reference split before inventing new heuristics.

Caveat: this is a snapshot of one runtime at one point in time and will drift as the always-load set is retuned. Re-verify against the current tools reference or a live session's tool list before treating it as ground truth for a specific deployment or version.

## Anti-patterns

- Deferring all MCP tools unconditionally including the ones used in every session. The round-trip cost accumulates.
- Deferring tools with tiny schemas. The cache savings are below measurement noise.
- Marking a policy-gated tool as `alwaysLoad`. The model will see and plan around a capability that policy may disallow.
- Never reviewing deferral decisions after session-frequency data is available. Decisions made without analytics should be revisited.

## Related

- [`deferred-loading-execution-and-remote-results.md`](deferred-loading-execution-and-remote-results.md) — ToolSearch execution pipeline and remote result normalization
- [`tool-registry-and-pool-assembly.md`](tool-registry-and-pool-assembly.md) — Tool contract and pool assembly
- [`../../ai-coding-agents-settings-policy/references/deferred-tool-policy-layer.md`](../../ai-coding-agents-settings-policy/references/deferred-tool-policy-layer.md) — Settings layer governance of ToolSearch
- [`../../ai-coding-agents-terminal-ui/references/recipe-toolsearch-render.md`](../../ai-coding-agents-terminal-ui/references/recipe-toolsearch-render.md) — How ToolSearch results render in the REPL
