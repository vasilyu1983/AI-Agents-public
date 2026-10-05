---
name: ai-coding-agents-runtime-core
description: "Designs tool and slash-command runtimes for coding-agent CLIs: registries, deferred loading, tool search, dispatch, forks. Use when modeling tool pools. Not approvals or plugins."
compatibility: Portable core. Works on Claude Code and Codex.
version: "2.0"
last_validated: 2026-09-29
---

# AI Coding Agents Runtime Core

Use this skill to design or review the two registries every coding-agent CLI ships: the **tool runtime** (tool contracts, pool assembly, deferred loading, ToolSearch, execution pipeline, remote rendering, subagent dispatch) and the **slash-command runtime** (typed command kinds, source-aware discovery, lazy loading, forked commands, remote-safe dispatch).

Both are registries with sources, precedence, filtering before exposure, refresh after topology change, and a single execution path. Design them with one contract vocabulary so permission, telemetry, and rendering semantics do not diverge.

This skill owns tool and command architecture. It does not own approval policy or sandboxing ([`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md)), plugin packaging ([`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md)), session persistence ([`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md)), MCP server design ([`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md)), or broader architecture ([`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md)).

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should tools be modeled and assembled? | [references/tool-registry-and-pool-assembly.md](references/tool-registry-and-pool-assembly.md) | Tool contract, built-in vs MCP pool, deny filtering, prompt-cache-stable ordering |
| How do deferred tools, execution, and remote results work? | [references/deferred-loading-execution-and-remote-results.md](references/deferred-loading-execution-and-remote-results.md) | ToolSearch, defer rules, execution pipeline, remote tool-result rendering |
| Should this tool be deferred or always-loaded? | [references/deferral-eligibility-decision-tree.md](references/deferral-eligibility-decision-tree.md) | Decision tree, `alwaysLoad` vs `shouldDefer`, per-server and per-tool overrides |
| How does OpenAI Codex model unified exec and composable CLI tools? | [references/openai-codex-unified-exec-and-tool-contracts.md](references/openai-codex-unified-exec-and-tool-contracts.md) | PTY sessions, stdin writes, output budgets, permission-aware params |
| Plugin-activated built-ins, spawn rules, subagent dispatch modes, Goose tool origin, toolshim | [references/tool-runtime-extensions-and-goose-patterns.md](references/tool-runtime-extensions-and-goose-patterns.md) | Reference-runtime extensions and cross-platform patterns |
| How should commands be represented and discovered? | [references/command-registry-and-discovery.md](references/command-registry-and-discovery.md) | Registry model, command kinds, load order, source precedence |
| How do commands run inline, forked, and remote? | [references/command-dispatch-forking-and-remote-safety.md](references/command-dispatch-forking-and-remote-safety.md) | Dispatch rules, forked execution, remote-safe filtering, bridge gating |
| Which events must invalidate cached command discovery? | [references/memoization-invalidation-contract.md](references/memoization-invalidation-contract.md) | Event table, invalidation invariants, integration checklist |
| How does OpenAI Codex model slash-command availability? | [references/openai-codex-command-state-machine.md](references/openai-codex-command-state-machine.md) | Command metadata, inline-arg support, active-task and side-conversation availability |
| Declarative (recipe-style) commands, precedence, fork inheritance, when a full registry is overkill | [references/command-declarative-artifacts-and-judgment-calls.md](references/command-declarative-artifacts-and-judgment-calls.md) | Artifact commands, declared extensions, trust-boundary judgment calls |

## When To Use

- Design a tool registry or slash-command registry for a coding-agent runtime or REPL
- Add built-in, MCP, plugin, skill, or workflow-provided tools and commands
- Model tool result rendering, progress events, interrupt behavior, or the execution pipeline
- Decide which tools to defer behind tool search
- Separate bridge-safe, remote-safe, and terminal-only commands in hybrid runtimes
- Review aliasing, immediacy, availability gates, forked commands, or subagent dispatch

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Approval modes, permission routing, sandbox policy | [`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md) |
| Plugin package and extension architecture | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| Session lifecycle, resume, context forking | [`../ai-coding-agents-state/SKILL.md`](../ai-coding-agents-state/SKILL.md) |
| Terminal REPL design, remote and bridge transport | [`../ai-coding-agents-surfaces/SKILL.md`](../ai-coding-agents-surfaces/SKILL.md) |
| MCP server design | [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md) |
| Generic CLI design outside agent runtimes | [`../software-devtools/SKILL.md`](../software-devtools/SKILL.md) |

## Shared Contract

- One interface per registry for every source (built-ins, MCP, plugins, skills, workflows), so dispatch, telemetry, and rendering share one lifecycle.
- Make kind and origin explicit fields. Never infer them from file layout or naming.
- Filter before exposure: blanket-denied, mode-hidden, or unavailable entries must not reach the model or the menu. Enforce revocation at execution time as well.
- Separate static availability (auth, provider, platform) from dynamic enablement (feature flag, environment). Recheck at dispatch and fail closed with a typed reason if the menu-time snapshot is stale.
- Rebuild the visible set through one refresh path after any topology change (MCP reconnect, plugin or skill reload, policy change, mode transition).
- Resolve name conflicts by an explicit per-source-pair policy, not "last loaded wins" and not "higher trust always wins". Record every shadowing event and show it in help and load telemetry. A namespaced entry (`plugin:name`) never shadows an un-namespaced name, and a namespace separator is not a path.
- Unknown remote entries degrade into renderable stubs, never invisible failures.

## Tool Runtime Workflow

1. **Define the tool contract.** Execution, validation, permissions, rendering, and interruption live on the tool type, ideally via a shared base or factory.
2. **Assemble the pool through one function** from built-ins plus MCP or other external tools. Keep built-ins a stable contiguous prefix when prompt-cache reuse depends on order; append newly discovered schemas after the reusable prefix.
3. **Mark deferral explicitly.** Use a first-class deferred flag plus a never-defer override for tools that must appear on turn one. Do not use heuristics the runtime cannot inspect or explain.
4. **Keep ToolSearch separate from execution.** Discovery is one tool; calling the loaded tool is another phase.
5. **Attest callability after discovery.** A deferred schema load proves only that metadata was found. Re-evaluate connection health, auth identity, policy, runtime mode, and schema version before exposing the tool as callable; return a typed unavailable reason if any changed.
6. **Rebuild at turn boundaries** after topology or policy change. A removed or denied tool leaves the next turn's visible set even if that loses cache reuse.
7. **Make the execution pipeline explicit.** Validation, permission check, telemetry, hooks, execution, result shaping, persistence, and rendering are separate stages behind one host entrypoint.
8. **Normalize remote results** into the local message model, with fallback rendering for tools the local client cannot execute. Treat transparent wrapper tools differently from direct tools.
9. **Model subagent dispatch as a handle plus a completion event.** Background, foreground, and fork are separate dispatch modes with explicit context and visibility; background permission prompts route to a visible session. A message delivered to a running subagent is task direction, not consent to a permission-gated action. See the extensions reference.

## Command Runtime Workflow

1. **Classify command surfaces.** Prompt-expansion, local text, and local JSX or TUI commands are different kinds. A full-screen cross-session manager is its own surface kind.
2. **Define one typed registry contract** with stable fields for names, aliases, source, availability, and enablement. Start from [assets/templates/minimal-command-registry.ts](assets/templates/minimal-command-registry.ts), which shows source precedence, shadow recording, and the lazy shim.
3. **Model load order explicitly:** bundled and built-in entries, then skills, plugins, workflows, and dynamic discoveries. De-duplicate dynamic entries by canonical file identity, not display name.
4. **Load lazily.** Heavy implementations load on invocation; lightweight shims keep menus responsive. A loader failure degrades one command, not the registry.
5. **Decide model-invocability.** Prompt-style commands need descriptions, argument hints, fork behavior, and tool allowances.
6. **Gate remote and bridge execution with explicit allowlists.** Bridge-safe filtering is a trust-boundary control, not a UX nicety; a command's safety must not depend on the client "just not sending it".
7. **Treat forked commands as subagent orchestration** with explicit allowed tools, agent selection, and a runtime-scoped context-start mode. In Claude Code a documented conversation fork inherits parent history and shares its prompt-cache prefix; a command named "fork" elsewhere proves neither.
8. **Make invalidation explicit.** Memoized discovery needs a host-owned invalidation path for skill, plugin, auth, feature-gate, and policy change. An in-session reload is its own command kind. A safe-start mode that disables extension layers is an availability class. See [references/memoization-invalidation-contract.md](references/memoization-invalidation-contract.md).
9. **Validate with conflict cases:** aliases, duplicate names, missing loaders, auth-gated commands, stale caches, mode-specific filtering.

Use the full command contract only when at least two hold: multiple independently loading sources, a remote or bridge client, or model-invocable commands. A CLI with a handful of static commands is better served by a flat match statement.

## Build Order

1. One typed contract per registry (tool and command) and explicit kinds.
2. Deterministic composition and precedence; built-in registration apart from external ingestion.
3. Assembly-time filtering for deny rules and mode visibility.
4. Deferred loading with ToolSearch as explicit phases; lazy command loading.
5. One execution pipeline from validation through rendering.
6. Invalidation and refresh hooks; mode filtering for local, remote, and bridge contexts.
7. Remote normalization, forked commands, and subagent dispatch with explicit inheritance rules.

## Core Invariants

- The model only sees tools that are callable in the current mode; every command has one typed dispatch path.
- Built-ins and external entries share one lifecycle contract.
- Discovery is separate from execution; availability is separate from enablement.
- Names, aliases, and ordering resolve deterministically.
- Remote-safe and bridge-safe command sets are explicit allowlists.
- Memoized discovery has explicit invalidation triggers.
- Remote tool uses render locally even when the local client cannot execute them.

## Failure Modes

- Duplicate tool or command names or aliases with unstable winner selection; alias expansion treated as string replacement that loses permission, telemetry, or fork metadata.
- Blanket-denied tools still advertised; filtering applied only at call time after the model planned around them.
- Registry bound once at startup: stale after MCP reconnect, plugin reload, feature-gate change, auth change, or policy change; deferred tools vanish after discovery.
- Loader failure collapsing the whole registry instead of one command; eager-loading every command.
- Terminal-only commands leaking into remote, mobile, or bridge paths; remote tool uses invisible because the local client lacks the implementation or cannot replay transport-specific results.
- Forked commands or subagents inheriting broader context or tools than intended; assuming subagent dispatch is synchronous by default.
- Built-ins, wrappers, and MCP tools modeled as separate systems with different permission, telemetry, and rendering semantics.
- Building slash-command UX around discovery only and forgetting dispatch guarantees, argument parsing, and degraded-mode behavior.
- Over-engineering: the full registry contract for a single-source, terminal-only tool.

## Minimal Viable Version

- One interface per registry, one assembly path for built-ins and one for external entries, one deny filter before exposure.
- One ToolSearch-style mechanism for deferred discovery; one lazy command loader; one central execution pipeline with permission and telemetry hooks.
- One precedence order, one invalidation path, one remote-safe allowlist, one error shape for unavailable or failed-to-load entries.

## What Strong Implementations Add

- Base-tool factories, feature-gated built-in enumeration, coordinator-mode filtering, and refreshable registries.
- Wrapper-versus-direct rendering, storage-aware result shaping, and normalized remote replay.
- Source provenance in menus, separate remote-safe and bridge-safe allowlists, and command-load telemetry with degraded-mode rendering.
- Declarative command artifacts with declared extension dependencies, verified at load time rather than mid-execution (see the judgment-calls reference).

## Navigation

### References

All files under [`references/`](references/) are listed in the Quick Reference table above.

### Templates

- [assets/templates/minimal-command-registry.ts](assets/templates/minimal-command-registry.ts) — Source precedence, shadow recording, lazy shim, cache invalidation; test in [minimal-command-registry.test.mjs](assets/templates/minimal-command-registry.test.mjs)

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and implementation references

### Related Skills

- [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) — Broader coding-agent architecture
- [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) — Plugin-provided commands and reload semantics
- [`../ai-coding-agents-safety-envelope/SKILL.md`](../ai-coding-agents-safety-envelope/SKILL.md) — Approval and permission routing
- [`../agents-mcp/SKILL.md`](../agents-mcp/SKILL.md) — MCP server connectivity and capability design

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
