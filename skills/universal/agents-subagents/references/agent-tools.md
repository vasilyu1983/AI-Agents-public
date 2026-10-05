---
description: Tool, permission, MCP, memory, and isolation guidance for agent frontmatter.
last_verified: 2026-09-16
status: stable
---

# Claude Code Subagent Tool Guide

Use this reference when choosing built-in tools, permission boundaries, MCP scope, and isolation settings for custom Claude Code subagents.

## Table of Contents

- [Key Rule](#key-rule)
- [Canonical Delegation Tool](#canonical-delegation-tool)
- [Tool Selection Matrix](#tool-selection-matrix)
- [Safe Defaults By Role](#safe-defaults-by-role)
- [Reviewer](#reviewer)
- [Implementer](#implementer)
- [Researcher](#researcher)
- [`tools` Vs `disallowedTools`](#tools-vs-disallowedtools)
- [Permission And Safety Fields](#permission-and-safety-fields)
- [`permissionMode`](#permissionmode)
- [`maxTurns`](#maxturns)
- [MCP Scope](#mcp-scope)
- [`mcpServers`](#mcpservers)
- [Memory](#memory)
- [`memory`](#memory)
- [Background And Isolation](#background-and-isolation)
- [`background`](#background)
- [`isolation`](#isolation)
- [Recommended Combinations](#recommended-combinations)
- [Read-Only Reviewer](#read-only-reviewer)
- [Bounded Implementer](#bounded-implementer)
- [Browser Verifier](#browser-verifier)
- [Anti-Patterns](#anti-patterns)
- [Tool Overload](#tool-overload)
- [Permission Creep](#permission-creep)
- [Unbounded Worker](#unbounded-worker)
- [Quick Checklist](#quick-checklist)
- [Related](#related)

## Key Rule

Start with the smallest useful capability set. Expand only when the task clearly requires it.

## Canonical Delegation Tool

- `Agent` is the current canonical delegation tool name in Claude Code.
- `Task` still appears as an alias in some examples and older material.
- Custom subagents under `.claude/agents/` should not themselves be designed as mini-orchestrators by default.
- If you need multi-worker dispatch, hand that concern off to [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md).

## Frontmatter Fields Beyond Tools

This file covers tool allow-lists, permission surfaces, MCP scope, memory, background, and isolation — the fields most worth thinking through per agent. The current field matrix (including `skills`, `hooks`, `effort`, `color`, `initialPrompt`, plugin-agent restrictions, and the `CLAUDE_CODE_SUBAGENT_MODEL` resolution order) is maintained as a single source of truth in [`../../agents-swarm-orchestration/references/platform-patterns.md`](../../agents-swarm-orchestration/references/platform-patterns.md). Do not duplicate that table here — read both when shaping an agent file.

Summary of the extra fields:

- **`skills`** — list of skill ids to inject as full content at subagent startup. Not inherited by Agent Team teammates. See [skill-subagent-patterns.md](skill-subagent-patterns.md).
- **`hooks`** — lifecycle hooks (`PreToolUse`, `PostToolUse`, `Stop`) for per-agent guardrails or observability. Plugin-provided agents cannot use `hooks`.
- **`effort`** — `low` / `medium` / `high` / `xhigh` / `max` reasoning budget. The default differs by model: read it in the model-configuration docs before relying on an inherited value. Drop to `low` or `medium` for readers and verifiers to avoid paying for reasoning tokens they do not need, then check on your own evals that quality holds (see [cost-control.md](cost-control.md)). Frontmatter effort overrides the session level but not an effort environment variable.
- **`color`** — UI tag color (red, blue, green, yellow, purple, orange, pink, cyan). Cosmetic; useful for disambiguating several active workers.
- **`experimental.cacheTtl`** — prompt-cache lifetime for this subagent's requests. Check the sub-agents docs for the accepted values and the minimum version before setting it.
- **`initialPrompt`** — auto-submitted first turn when the agent is started via `--agent`. Useful for whole-session specialists.
- **Plugin-agent restrictions** — plugin-provided agents cannot use `hooks`, `mcpServers`, or `permissionMode`. Reuse plugin agents only when those fields are not needed.

## Tool Selection Matrix

| Need | Add |
|------|-----|
| Read file contents | `Read` |
| Search code/text | `Grep` |
| Discover files by pattern | `Glob` |
| Make targeted edits | `Edit` |
| Create new files | `Write` |
| Run tests, builds, git, scripts | `Bash` |
| Fetch current docs from a known URL | `WebFetch` |
| Search the web for current facts | `WebSearch` |

## Safe Defaults By Role

### Reviewer

```yaml
tools: Read, Grep, Glob
maxTurns: 8
```

Use for code review, migration review, regression checks, and policy audits.

### Implementer

```yaml
tools: Read, Grep, Glob, Edit, Write, Bash
permissionMode: acceptEdits
maxTurns: 12
```

Use only when the task has bounded file ownership and explicit verification.

### Researcher

```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
maxTurns: 10
```

Use for up-to-date framework behavior, docs comparison, or source-backed recommendations.

## `tools` Vs `disallowedTools`

Prefer `tools` when:

- the job is narrow
- you know exactly what the subagent needs
- you want predictable behavior

Prefer `disallowedTools` when:

- you want a mostly inherited environment
- you only need to block a few risky tools
- the subagent mainly exists to add scoped MCP servers or hooks

Avoid mixing both unless you have a specific runtime reason and have tested the result.

`disallowedTools` also accepts MCP server-level wildcards: `mcp__<server>` or `mcp__<server>__*` removes every tool from one server (these two patterns are documented for `tools` and behave the same in `disallowedTools`), and, in `disallowedTools` only, `mcp__*` removes every MCP tool from any server (sub-agents docs, "Both fields accept MCP server-level patterns..." / "In `disallowedTools`, `mcp__*` also removes every MCP tool from any server"; checked 2026-09-27). Prefer these over enumerating individual MCP tool names when the intent is "no MCP access for this worker" or "no access to this one integration."

## Permission And Safety Fields

### `permissionMode`

Use the default unless the subagent has a clear, repeated need for a different approval posture.

Good fits:

- reviewer or researcher: keep default approvals
- bounded implementer: `acceptEdits` can be reasonable
- fully trusted automation: stricter review before considering broader permissions

Bad fit:

- setting permissive modes just to avoid thinking through file ownership and verification

### `maxTurns`

Set it when the worker should stop after a bounded amount of exploration or edits.

Good fits:

- review agents
- browser verifiers
- researchers that should return findings quickly

## MCP Scope

### `mcpServers`

Scope MCP servers to the subagent that needs them instead of loading everything into the parent thread.

Good fits:

- `playwright` for browser verification
- `github` for issue or PR review
- project-specific API/database servers for one specialized worker

Rules:

- keep the server list minimal
- do not give a general reviewer a write-capable MCP server unless it truly needs it
- if MCP scope is the main reason for the subagent, say that in the description

### Inline MCP servers vs references

Anthropic's current subagent docs explicitly recommend defining MCP servers **inline inside the subagent's frontmatter** (rather than referencing a server configured at project scope) when the goal is to keep that server's tool descriptions out of the parent conversation entirely:

> _"To keep an MCP server out of the main conversation entirely and avoid its tool descriptions consuming context there, define it inline here rather than in `.mcp.json`. The subagent gets the tools; the parent conversation doesn't."_ — [Claude Code subagents docs](https://code.claude.com/docs/en/sub-agents)

Decision rule:

- **Inline in subagent frontmatter** — when only one worker needs the server, and the tool descriptions (often 10–20k tokens) should never appear in the parent context. Use for workers that own the integration — e.g., a browser-verifier that is the only caller of Playwright, a security reviewer that is the only caller of a sensitive repo-access MCP.
- **Reference a project/user-scoped server** — when multiple workers share the server, or the main thread itself needs occasional access. You pay the parent-context tax but avoid re-declaring the server in every agent file.

Current Claude Code mitigates but does not eliminate the cost: MCP tool definitions are deferred by default, so only tool **names** (not full descriptions) enter the initial context until a specific tool is used; confirm the running version still defers them. Inline MCP is still the right lever when a server is single-owner and the parent thread never needs it.

## Memory

### `memory`

Use only when the subagent benefits from durable, project-specific learning across runs.

Good fits:

- repeated release-review patterns
- stable repo conventions that are narrower than project memory
- recurring reviewer heuristics for the same codebase

Important behavior:

- subagent memory automatically enables `Read`, `Write`, and `Edit` so the worker can maintain its memory files
- choose the scope deliberately: `user` for cross-project learning, `project` for versioned team knowledge, `local` for project-specific but untracked memory

Where memory lands, per scope:

| Scope | Location | Use when |
|---|---|---|
| `user` | `~/.claude/agent-memory/<name-of-agent>/` | "the subagent should remember learnings across all projects" |
| `project` | `.claude/agent-memory/<name-of-agent>/` | "the subagent's knowledge is project-specific and shareable via version control" |
| `local` | `.claude/agent-memory-local/<name-of-agent>/` | "the subagent's knowledge is project-specific but shouldn't be checked into version control" |

What actually gets loaded — **this is the budget a memory file must be written to fit**: the subagent's system prompt includes the first "200 lines or 25KB of `MEMORY.md` in the memory directory (whichever comes first), with instructions to curate `MEMORY.md` if it exceeds that limit", plus instructions for reading and writing the memory directory. Anything past that cap is on disk but not in context, so keep `MEMORY.md` an index and put detail in sibling files the worker opens on demand.

The field is **part of auto memory**, so it is silently inert when auto memory is off: it is "controlled by" the `autoMemoryEnabled` setting and the `CLAUDE_CODE_DISABLE_AUTO_MEMORY` environment variable, and "when auto memory is off, the `memory` field has no effect." Check both before diagnosing a worker that never remembers anything. Source: [code.claude.com/docs/en/sub-agents](https://code.claude.com/docs/en/sub-agents).

Avoid when:

- the information is already in `CLAUDE.md` or project memory
- the task is one-off
- the subagent can just read the source of truth each run

## Background And Isolation

### `background`

Whether a subagent runs in the foreground or background depends on the session mode (interactive, fork mode, `-p`, Agent SDK) and on the release; the defaults differ between these modes and have changed between releases. Do not pin a default in a prompt or agent file.

Before a step that consumes a subagent's result, determine whether this session runs subagents in the background: read the sub-agents docs for the running version and confirm with the [runtime smoke test](runtime-smoke-tests.md). If it does, force the foreground where the runtime exposes a lever (the tool call's background flag, or the environment variable that disables background tasks) or wait explicitly for the completion notification. The documented agent-file field is `background: true`, which forces that agent to run in the background. Do not use `background: false` on an agent file as a foreground pin unless the docs for the running version say it blocks. Check where permission requests from background subagents surface on the running version before relying on them.

Good fits for forced background:

- browser verification
- longer-running research
- large but bounded read-only audits

Avoid when:

- the worker needs rapid clarifications
- the parent thread must inspect each step interactively
- the calling step depends immediately on the result — force the foreground or wait explicitly for the completion notification, as above

### `isolation`

Use `worktree` when parallel **subagents** may edit files, run git commands, or otherwise contend on the same checkout. Agent Team teammates are separate sessions but share the lead's working directory; a teammate does not gain worktree isolation from a reused definition's `isolation` field. With agent teams enabled, a named spawn from the main conversation becomes a teammate unless the call is a fork or passes `isolation` on the call itself; passing it there launches a worktree-isolated subagent instead (sub-agents docs §agent teams, checked 2026-09-27).

Check the worktree base before fan-out. An isolated worktree may be created from the default branch or remote ref rather than the parent's `HEAD`, so a worker can silently miss unpushed or uncommitted parent work. Before spawning, check which base the runtime uses (docs or settings for the running version); then either commit and push the parent state, or configure the base to `HEAD`. After spawn, confirm each worker's base SHA (`git -C <worktree> rev-parse HEAD` or `git merge-base`) equals the parent `HEAD` before trusting its diff.

Good fits:

- parallel implementers on separate file sets
- risky changes that deserve an isolated branch-like workspace

Avoid when:

- the subagent is read-only
- the task is tiny and entirely sequential
- the subagent's output is an artifact a later worker in the same run must read from the lead checkout (context packets, code graphs, portfolio profiles, PRDs, curated docs). Isolating it would strand the artifact on a worktree branch. The `dev-context-*`, `dev-portfolio-mapper`, and `docs-*` members therefore run `permissionMode: acceptEdits` with no `isolation` on purpose; they compensate with narrow `owned_files` in their team recipes and a bounded `maxTurns`.

## Recommended Combinations

### Read-Only Reviewer

```yaml
tools: Read, Grep, Glob
maxTurns: 8
```

### Bounded Implementer

```yaml
tools: Read, Grep, Glob, Edit, Write, Bash
permissionMode: acceptEdits
maxTurns: 12
isolation: worktree
```

### Browser Verifier

```yaml
tools: Read, Grep, Glob
mcpServers:
  - playwright
background: true
maxTurns: 10
```

## Anti-Patterns

### Tool Overload

```yaml
tools: Read, Grep, Glob, Edit, Write, Bash, WebFetch, WebSearch
```

Problem: too much freedom for a worker that probably needs one role, not all roles.

### Permission Creep

```yaml
permissionMode: bypassPermissions
```

Problem: this hides weak task boundaries instead of fixing them.

### Unbounded Worker

```yaml
tools: Read, Grep, Glob, WebFetch, WebSearch
```

Problem: without `maxTurns` or an explicit deliverable, the subagent can over-explore.

## Codex Tool Model

Codex does not use `tools`/`disallowedTools`. Tool access is governed by `sandbox_mode`:

- `sandbox_mode = "read-only"` — no file writes, no shell writes
- `sandbox_mode = "workspace-write"` — full write access within workspace
- Omitting `sandbox_mode` inherits the parent sandbox policy

MCP servers are configured via `[mcp_servers.<name>]` TOML tables:

```toml
[mcp_servers.chrome_devtools]
url = "http://localhost:3000/mcp"
startup_timeout_sec = 20
```

**Sandbox inheritance**: subagents inherit the parent's sandbox policy. Parent turn-level overrides (like `--yolo`) reapply to spawned children.

**Approval surfacing**: approval requests from inactive threads surface in the main thread. Press `o` to switch to the requesting thread.

## Repeated Structured Fan-Out (Codex)

For tabular or repeated work, keep the row schema and result schema in the parent-owned execution plan, spawn bounded clean-context workers, wait for all results, and validate completeness before synthesis. Do not depend on a batch helper unless the active Codex surface documents and exposes it; the portable contract is spawn, wait, follow-up, and parent-side aggregation.

## Quick Checklist

```text
SUBAGENT CAPABILITY CHECKLIST

[ ] Does the subagent need to modify files, or is review enough?
[ ] Is `tools` narrower than inheriting the full parent capability set?
[ ] Are risky tools removed or never granted?
[ ] Is MCP scope limited to the one server the task needs?
[ ] Is `memory` omitted unless it creates real repeat-use value?
[ ] Is `background` reserved for non-interactive work?
[ ] Is `isolation: worktree` used for parallel or risky edits?
```

## Related

- [agent-patterns.md](agent-patterns.md) - Prompt and role patterns
- [../SKILL.md](../SKILL.md) - Main subagent guide
- [../../agents-mcp/SKILL.md](../../agents-mcp/SKILL.md) - MCP server design and security
- [../../agents-swarm-orchestration/SKILL.md](../../agents-swarm-orchestration/SKILL.md) - Multi-worker orchestration
