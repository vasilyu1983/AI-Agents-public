---
name: ai-coding-agents-command-runtime
description: "Designs slash-command runtimes for coding-agent CLIs. Use when modeling command registries, lazy loading, aliases, forked commands, or remote-safe dispatch."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Command Runtime

Use this skill to design or review the slash-command layer of a coding-agent CLI: command registry shape, typed command kinds, lazy loading, source-aware discovery, and safe dispatch across local, remote, and bridge modes.

This skill owns command-runtime architecture for coding agents. For broader agent creation, start with [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md).

## ASCII Flow

```text
command sources
  built-ins + skills + plugins + workflows + dynamic discoveries
       |
       v
registry composition
  typed command contract + source tags + deterministic precedence
  plugin-namespaced skills: plugin-name:skill-name
       |
       v
availability + enablement
  feature gates + auth + mode filters + aliases
  /agents as first-class tabbed command surface (background agent management)
       |
       v
dispatch
  prompt command | local text | local UI | forked subagent | remote-safe
  /reload-skills (in-session reload) | SessionStart reloadSkills hook
  --safe-mode (disables CLAUDE.md, plugins, skills, hooks, MCP)
       |
       v
execution result or unavailable-command error
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should commands be represented and discovered? | [`references/command-registry-and-discovery.md`](references/command-registry-and-discovery.md) | Registry model, command kinds, load order, source precedence |
| How should commands execute across inline, forked, and remote flows? | [`references/command-dispatch-forking-and-remote-safety.md`](references/command-dispatch-forking-and-remote-safety.md) | Dispatch rules, forked execution, remote-safe filtering, bridge gating |
| How does OpenAI Codex model slash-command availability? | [`references/openai-codex-command-state-machine.md`](references/openai-codex-command-state-machine.md) | Command metadata, inline-arg support, active-task availability, side-conversation availability |

## When To Use

- Design slash-command architecture for a coding-agent CLI or REPL
- Add commands from built-ins, skills, plugins, workflows, or MCP-backed sources
- Define command kinds such as prompt, local text, and local JSX or TUI commands
- Review aliasing, immediacy, availability gates, or source-aware command formatting
- Separate bridge-safe, remote-safe, and terminal-only commands in hybrid runtimes

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Broader coding-agent architecture | [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) |
| Plugin package and extension architecture | [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) |
| Tool registry and tool execution semantics | [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md) |
| Session lifecycle and resume | [`../ai-coding-agents-sessions/SKILL.md`](../ai-coding-agents-sessions/SKILL.md) |
| Terminal REPL interaction design | [`../ai-coding-agents-terminal-ui/SKILL.md`](../ai-coding-agents-terminal-ui/SKILL.md) |
| Generic CLI design outside agent runtimes | [`../software-devtools/SKILL.md`](../software-devtools/SKILL.md) |

## Default Workflow

1. **Classify command surfaces.** Separate prompt-expansion commands from local text commands and local JSX or TUI commands.
2. **Define the registry contract.** Keep one typed command interface with stable fields for names, aliases, source, availability, and enablement.
3. **Model load order explicitly.** Load bundled and built-in entries, then skills, plugins, workflows, and any dynamic discoveries, with deterministic precedence.
4. **Keep loading lazy.** Heavy implementations should load on invocation, not during registry bootstrap.
5. **Decide which commands are model-invocable.** Prompt-style commands and skills need extra fields for descriptions, argument hints, fork behavior, and tool allowances.
6. **Separate UI-safe from bridge-safe.** Remote and bridge clients should see only commands that are valid without local terminal interaction.
7. **Treat forked commands as subagent orchestration.** Give them explicit allowed tools, agent selection, and prompt-cache-safe context inheritance.
8. **Make cache invalidation explicit.** Memoized command discovery must have a host-owned invalidation path when skills, plugins, or policy layers change.
9. **Validate with conflict cases.** Test aliases, duplicate names, missing loaders, auth-gated commands, stale caches, and mode-specific filtering.

## Host Rules

- Keep one registry type for every command source so built-ins, skills, plugins, and workflows share the same dispatch contract.
- Make command kind explicit. Do not infer "text versus TUI versus prompt" from file layout or naming.
- Separate static availability from dynamic enablement. Auth or provider eligibility and feature-flag or environment checks are different concerns.
- Default to lazy loading for anything with heavy UI, IO, or optional dependencies.
- Allow heavyweight commands to expose lightweight shims so menus and help text stay responsive before the real implementation loads.
- Keep prompt commands declarative and source-tagged so they can be formatted differently in UI and model contexts.
- Gate remote and bridge command execution with explicit allowlists. Do not let terminal-only commands leak into mobile or web control paths.
- De-duplicate dynamically discovered commands by canonical file identity, not only by display name or path string.

## Build Order

1. Define the typed command contract and command kinds.
2. Implement deterministic registry composition and precedence.
3. Add aliases, source tags, and availability versus enablement fields.
4. Add lazy loading, shim commands, and loader-failure handling.
5. Add invalidation hooks for skill, plugin, and policy refresh.
6. Add mode-specific filtering for local, remote, and bridge contexts.
7. Add forked-command execution with explicit inheritance rules.

## Core Invariants

- Every command must have one typed dispatch path.
- Availability and enablement are not the same field.
- Command names and aliases must resolve deterministically.
- Remote-safe and bridge-safe command sets must be explicit.
- Heavy command implementations should load on invocation, not registry bootstrap.
- Memoized command discovery must have explicit invalidation triggers.

## Failure Modes

- Duplicate names or aliases with unstable winner selection.
- Mode filtering leaking terminal-only commands into remote clients.
- Stale dynamic-skill caches keeping removed commands visible.
- Loader failures collapsing the whole registry instead of one command.
- Dynamic command caches surviving plugin disable, skill reload, or policy change.
- Forked commands inheriting broader context or tools than intended.

## Minimal Viable Version

- One registry type for all command sources.
- One precedence order across built-ins, skills, plugins, and workflows.
- One lazy loader path for nontrivial commands.
- One explicit invalidation path for memoized command lists.
- One allowlist for remote-safe or bridge-safe execution.
- One clear error shape for unavailable or failed-to-load commands.

## What Strong Implementations Add

- Memoized discovery with explicit invalidation boundaries.
- Feature-gated built-in command enumeration and lightweight command shims.
- User-facing source formatting and provenance in command menus.
- Declarative prompt commands with fork behavior and tool allowances.
- Separate remote-safe and bridge-safe allowlists.
- Command-load telemetry and degraded-mode rendering for partial registry failure.

## Known Traps

- Merging built-ins, plugin commands, and repo-local commands without a deterministic precedence model and then getting unstable resolution by load order.
- Exposing commands in one client surface that cannot execute safely in remote, mobile, or bridge-controlled paths.
- Treating alias expansion as pure string replacement and losing metadata needed for permissions, telemetry, and fork semantics.
- Memoizing discovery results without an explicit invalidation path for plugin reloads, auth-state changes, or feature gates.
- Building slash-command UX around discovery only and forgetting dispatch guarantees, argument parsing, and degraded-mode behavior.

## Common Anti-Patterns

- Inferring command kind from file location or naming conventions alone.
- Treating auth or feature-flag state as part of static registry shape.
- Resolving aliases with first-hit-wins behavior that changes by load timing.
- Eager-loading every command at startup.
- Memoizing command discovery with no host-owned invalidation path.
- Assuming commands visible in a local REPL are valid in remote or mobile control paths.

## Claude Code Command Surface Extensions (2026)

### /reload-skills and SessionStart reloadSkills

`/reload-skills` (shipped Claude Code v2.1.152, May 2026) is a first-class in-session reload command that re-discovers and re-registers all skills from their source directories without restarting the runtime, preserving transcript, loaded files, and task list — a reload, not a restart. The equivalent programmatic path is a `SessionStart` hook whose return value sets `reloadSkills: true`; this exists specifically so a hook that fetches, generates, or installs skills before the first turn can make them available in the same session instead of only on the next launch. Both paths belong in the same "invalidation and reload" command kind alongside `/reload-plugins`.

### --safe-mode flag

`--safe-mode` (and the equivalent `CLAUDE_CODE_SAFE_MODE` env var, shipped v2.1.169) is a degraded-mode startup flag that disables CLAUDE.md loading, plugins, skills, hooks, and MCP servers — the same five customization layers, together, every time. It is the canonical remote-safe / hardened-bootstrap entry point for CI, sandboxed pipelines, or diagnostic "is it my config or the product" triage where third-party extension code must not run. It does not disable auth, the configured model or base URL, conversation history, or the project trust dialog — those are separate availability axes, not folded into this flag. Commands that depend on skills or plugins should be filtered out of the model-visible command set when `--safe-mode` is active; this is an availability class (feature-gated by mode flag) distinct from auth-gated or environment-gated.

### Plugin-namespaced skills

Skills shipped inside plugins are namespaced by plugin name for slash-command purposes: `plugin-name:skill-name` (mirroring the existing `commands/` namespacing), while legacy un-namespaced invocation is kept for backward compatibility. This is a distinct naming tier in the precedence model, and the namespace separator is `:`, not `/` — do not parse it as a path. Treat the exact cross-tier resolution order (built-in vs. project-local vs. plugin-namespaced) as implementation-specific: verify it against the current source or docs for your target runtime before hard-coding a precedence assumption, since this is the kind of internal ordering detail that changes without a changelog entry.

### Agent View (`claude agents`) as a full-screen dashboard surface

`claude agents` opens Agent View, a full-screen dashboard for every background session on the machine — it is a CLI subcommand, not a `/agents` in-session slash command; do not register `/agents` in a slash-command table. Sessions are grouped by urgency, not by a flat state enum: **Pinned**, **Ready for review** (open PR), **Needs input**, **Working**, and **Completed** (finished, failed, and stopped sessions collapsed together). `/bg` backgrounds an active session into this view; `claude --bg` launches directly into the background from the shell.

Design lesson for your own registry even though `/agents` is not a literal command: a background-agent manager is a distinct command-surface *kind* — full-screen, non-modal, state-grouped by actionability rather than by lifecycle stage — and it composes with, but is architecturally separate from, the `/plugin`, `/model`, `/permissions` style single-purpose tabbed commands. If you enumerate command-surface kinds in a registry, add "dashboard surface" as its own kind rather than forcing it into the `local-jsx` command contract used for simple TUI commands; a dashboard has its own refresh, selection, and cross-session dispatch semantics that a modal command does not.

## Cross-Platform Patterns (Goose)

Goose introduces a different kind of command: **recipes**, YAML-serialized parameterized workflows with their own extension manifest. This is a distinct point in the design space from Claude Code's frontmatter-plus-prompt slash commands.

### Recipes as typed, portable commands

A Goose recipe carries `version / title / description / instructions / author / extensions / activities / prompt / parameters` where each parameter declares `{key, input_type, requirement, description, default}`. The "command" is a versioned artifact that travels between machines with its dependencies stated.

- **Pattern:** for commands that encode reusable workflows, prefer a declarative artifact over a live registry entry. Parameters are typed, extension dependencies are pinned, and the artifact can be statically validated before being added to the registry.
- **Anti-pattern:** encoding complex workflow commands as free-form prompt text with implicit argument conventions. That blocks validation, sharing, and portability across agents and machines.
- **Recipe:** extend the typed command contract with an optional `artifact_ref` variant — the command is a reference to a recipe-style artifact. Discovery reads the artifact; validation happens at registration, not execution.

### Declared-extension commands

A Goose recipe lists its required extensions. The command cannot run if they are absent — this is an install/activation check, not a runtime tool-call failure.

- **Pattern:** commands that depend on particular tools, MCP servers, or skills should declare those dependencies in the command definition. The registry verifies dependencies at load time and surfaces unavailable commands with an actionable error (install X), not a silent "no-op."
- **Anti-pattern:** commands that hard-code `require_tool("github.pr_create")` inside their body and discover unavailability only mid-execution.
- **Recipe:** add `requires_extensions: Vec<ExtensionRef>` to the command type. Unavailable-dependency state is a first-class command availability class (beside auth-gated and feature-gated).

## Judgment Calls

These are the calls a non-expert gets wrong even after reading the patterns above, because the patterns describe *what* to build, not *when the trade-off actually bites*.

- **Bridge-safe filtering is a trust-boundary control, not a UX nicety.** A remote or mobile client that can invoke a `local-jsx` command is, in effect, being handed a slice of local code execution surface — Ink rendering, filesystem side effects, terminal-only state mutation — from a network hop away. Model the remote-safe/bridge-safe allowlist as a security boundary with the same rigor as a permission gate, not as "which commands happen to render okay on a small screen." If a command's safety depends on "the bridge client will just not send that," you have not actually gated it.
- **Precedence order is a security decision before it is a UX decision.** When user-scope, project-scope, and plugin-scope commands can collide on the same name, decide up front whether a *lower*-trust source (a freshly installed plugin) is allowed to silently shadow a *higher*-trust one (a built-in or a project safety command). Prefer "higher trust always wins, and a same-name lower-trust registration is surfaced as a warning" over "last loaded wins" — silent shadowing of a safety-relevant command by an untrusted plugin is a worse failure than a slightly less convenient override model.
- **Forked-command tool inheritance should default to strictly narrower than the parent's, never wider, and the delta should be visible.** It is tempting to let a fork "inherit everything" for simplicity, since it already inherits the full conversation. Inheriting conversation content and inheriting tool permissions are different axes: widen neither by default, and log the effective allowed-tools set for a fork the same way you would for a fresh subagent, or debugging a runaway fork becomes a transcript-diffing exercise.
- **Know when the full typed registry is overkill.** A CLI with under ~10 static commands and no plugin, skill, or remote-client story does not need source tags, availability-vs-enablement separation, or a memoization-invalidation contract — a flat match statement is more honest about the system's actual complexity and easier to audit. Reach for the full contract in this skill when you have at least two of: multiple command sources that load independently, a remote or bridge client, or model-invocable (prompt-type) commands. Building the full registry contract for a single-source, terminal-only tool is the over-engineering failure mode of this skill, and it is at least as common as the under-engineering failure modes listed above.
- **`isEnabled()` staleness is worse than a missing command.** A command that silently disappears because a feature flag flipped is confusing but recoverable — the user tries again later. A command that appears available, is dispatched, and then fails mid-execution because `isEnabled()` was stale at menu-render time but re-checked at dispatch time is a worse experience. If you cannot guarantee the enablement check is consistent between "shown in the menu" and "actually dispatched," fail closed at dispatch and surface why, rather than trusting the menu-time snapshot.

## Navigation

### References

- [`references/command-registry-and-discovery.md`](references/command-registry-and-discovery.md) — Typed command contracts, source composition, and discovery order
- [`references/command-dispatch-forking-and-remote-safety.md`](references/command-dispatch-forking-and-remote-safety.md) — Dispatch rules, forked command execution, and remote or bridge safety
- [`references/openai-codex-command-state-machine.md`](references/openai-codex-command-state-machine.md) — OpenAI Codex slash-command metadata, ordering, aliases, and state-dependent availability

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and implementation references for command-runtime guidance

### Related Skills

- [`../ai-coding-agents/SKILL.md`](../ai-coding-agents/SKILL.md) — Broader coding-agent architecture
- [`../ai-coding-agents-plugins/SKILL.md`](../ai-coding-agents-plugins/SKILL.md) — Plugin-provided commands and reload semantics
- [`../ai-coding-agents-tools/SKILL.md`](../ai-coding-agents-tools/SKILL.md) — Tool registry and execution path design

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- The registry-composition and dispatch patterns in the references are grounded in a local April 2026 `claude_code` source snapshot; that architecture (typed command contract, source composition order, availability vs. enablement) is stable in intent but re-check upstream code or docs before relying on exact internal ordering.
- The `/reload-skills`, `--safe-mode`, `/fork`, and Agent View (`claude agents`) claims in this file were re-verified against current Claude Code product docs and changelog entries as of 2026-07-11 (see `data/sources.json` → `verified_2026_07_11`). Re-verify version gates before citing them, since Claude Code ships weekly and these flags/commands are young enough to still be moving.
- Command availability, auth gates, and bridge behavior are product-specific. Preserve the architecture, but verify the exact command surfaces in the target runtime before shipping.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
