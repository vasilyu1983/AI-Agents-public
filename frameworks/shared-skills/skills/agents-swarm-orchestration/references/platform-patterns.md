# Platform Patterns


## Table of Contents

- [Claude Code](#claude-code)
- [Subagents](#subagents)
- [Subagent configuration](#subagent-configuration)
- [Subagent invocation and lifecycle](#subagent-invocation-and-lifecycle)
- [Agent teams](#agent-teams)
- [Codex multi-agents](#codex-multi-agents)
- [Codex subagents](#codex-subagents)
- [OpenAI Agents SDK](#openai-agents-sdk)
- [Manager / agents-as-tools](#manager-agents-as-tools)
- [Handoffs](#handoffs)
- [Cross-platform takeaway](#cross-platform-takeaway)
- [Prompt structure for reusable worker prompts](#prompt-structure-for-reusable-worker-prompts)

## Claude Code

### Subagents

Source: https://code.claude.com/docs/en/sub-agents

- Subagents run in their own context window with their own system prompt, tool access, and permissions.
- They work well when the lead only needs the result back.
- They are the right default for focused workers that explore, triage, review, or modify exclusive files.
- Subagents stay inside one session. If workers need to communicate with each other directly, use agent teams or cross-session messaging (Aug 2026, macOS/Linux) instead.
- Since June 2026 subagents can spawn their own subagents; chains are capped at 5 levels. Keep assignments bounded anyway — the cap is a runaway backstop, not a design target.

Practical default:

- Use read-only subagents for exploration, search, and plan support.
- Use edit-capable subagents only when file ownership is exclusive and the lead already froze the interface.

Built-in subagents:

| Subagent | Model | Tools | Purpose |
|----------|-------|-------|---------|
| Explore | Haiku | Read-only | File discovery, code search, codebase exploration |
| Plan | Inherits | Read-only | Codebase research during plan mode |
| General-purpose | Inherits | All | Complex research, multi-step operations, code modifications |
| statusline-setup | Sonnet | Read, Edit | Auto-invoked to configure the Claude Code status line — do not call directly |
| Claude Code Guide | Haiku | Docs lookup | Auto-invoked for "how do I…" questions about Claude Code, the Agent SDK, and the Claude API — do not call directly |

### Subagent configuration

Source: https://code.claude.com/docs/en/sub-agents

Subagents are defined as Markdown files with YAML frontmatter. Store them at different scopes with this precedence (highest first):

1. Managed settings (organization-wide)
2. `--agents` CLI flag (current session, JSON)
3. `.claude/agents/` (current project, version-controllable)
4. `~/.claude/agents/` (all user projects)
5. Plugin `agents/` directory (where plugin is enabled)

Key frontmatter fields:

| Field | Purpose |
|-------|---------|
| `name` | Required. Lowercase-hyphen identifier |
| `description` | Required. When Claude should delegate |
| `tools` | Tool allowlist; inherits all if omitted |
| `disallowedTools` | Tool denylist; removed from inherited pool |
| `model` | `sonnet`, `opus`, `haiku`, full model ID, or `inherit` (default) |
| `permissionMode` | `default`, `acceptEdits`, `auto`, `dontAsk`, `bypassPermissions`, `plan` |
| `maxTurns` | Cap on agentic turns |
| `skills` | Skills injected at startup (full content, not just availability) |
| `mcpServers` | MCP servers scoped to this subagent (inline or reference) |
| `hooks` | Lifecycle hooks: PreToolUse, PostToolUse, Stop |
| `memory` | Persistent memory scope: `user`, `project`, or `local` |
| `background` | Pins foreground vs background. Background is the default since ~2026-07 (v2.1.195+); set `false` for edit-capable workers |
| `effort` | `low`, `medium`, `high`, `xhigh`, `max` (Opus only; `xhigh` is the new 4.7-era default — see [`../../agents-subagents/references/cost-control.md`](../../agents-subagents/references/cost-control.md) §"Opus 4.7 Cost Levers") |
| `isolation` | `worktree` for git-worktree isolation |
| `color` | UI color: red, blue, green, yellow, purple, orange, pink, cyan |
| `initialPrompt` | Auto-submitted first turn when used as `--agent` |

Model resolution order: `CLAUDE_CODE_SUBAGENT_MODEL` env var > per-invocation parameter > frontmatter `model` > parent conversation model.

Restrict which subagents a coordinator can spawn using `Agent(type1, type2)` in the `tools` field. Omitting `Agent` entirely prevents spawning. Plugin subagents cannot use `hooks`, `mcpServers`, or `permissionMode`.

### Subagent invocation and lifecycle

Source: https://code.claude.com/docs/en/sub-agents

Invocation modes:

- **Natural language**: name the subagent in the prompt; Claude decides whether to delegate.
- **@-mention**: type `@` and pick from typeahead; guarantees that subagent runs.
- **`--agent` / `agent` setting**: whole session uses the subagent's system prompt, tools, and model.

Foreground vs background:

Background is the **default** since ~July 2026 (v2.1.195+); set `background: false` in frontmatter to pin a worker to the foreground.

- **Foreground**: blocks main conversation; permission prompts pass through. Pin edit-capable workers here.
- **Background** (default): runs concurrently; permissions pre-approved at launch, unapproved actions auto-denied. Ctrl+B backgrounds a running foreground task.

Resume: use `SendMessage` with the agent ID to continue a completed subagent with full prior context. Subagent transcripts persist independently of main conversation compaction.

Auto-compaction: subagents compact at ~95% capacity (configurable via `CLAUDE_AUTOCOMPACT_PCT_OVERRIDE`).

### Agent teams

Source: https://code.claude.com/docs/en/agent-teams

- Agent teams are separate Claude Code sessions coordinated by a lead.
- Teams use a shared task list and direct inter-agent messaging.
- They are best for work that benefits from disagreement, discussion, and self-coordination between workers.
- The feature is experimental and disabled by default; enable via `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` in settings.json or environment. Minimum version at launch was Claude Code `v2.1.32`. As of Aug 2026 the behavior still churns week to week — re-verify against the docs on every CLI bump.
- **Enabling the flag changes subagent semantics session-wide:** subagent results come back as idle notifications rather than synchronous returns. Any flow that waits on a subagent's return value can stall. Do not enable teams in sessions built around blocking subagent calls.
- **`~/.claude/teams/{team-name}/` is runtime state, not a config artifact.** The runtime writes it when the lead creates the team. Do not pre-author, template, or version it. Reusable roles live in subagent definitions and are referenced at spawn time.
- At initial research-preview launch this required **Opus 4.6 or newer** as the lead model. Current docs describe a per-team "default teammate model" setting instead of a hard lead-model floor — verify the live requirement against [code.claude.com/docs/en/agent-teams](https://code.claude.com/docs/en/agent-teams) before assuming a model gate still applies.
- Known limitations (verify against current SDK docs): split-pane display mode does not work reliably in the VS Code extension — use the terminal CLI or in-process display mode. Earlier practitioner reports of background teammates stalling on unseen permission prompts are not currently confirmed in official docs; treat as a risk to re-verify and keep edit-capable teammates foreground until you have.

Architecture:

| Component | Role |
|-----------|------|
| Team lead | Main session that creates the team, spawns teammates, coordinates |
| Teammates | Separate Claude Code instances with own context windows |
| Task list | Shared file-based work items at `~/.claude/tasks/{team-name}/` |
| Mailbox | SendMessage-based peer-to-peer messaging system |

Communication tools:

- `SendMessage` — direct (to one teammate by name) or broadcast (to all). Broadcast costs scale with team size.
- `TaskList` / `TaskUpdate` — shared task coordination with file-locking for safe concurrent claiming.
- Automatic idle notifications when a teammate finishes.

Context sharing:

- Each teammate loads project context (CLAUDE.md, MCP servers, skills) plus the spawn prompt. The lead's conversation history does not carry over.
- Coordinate through task state and messages, not shared context windows.
- Team config at `~/.claude/teams/{team-name}/config.json` contains the `members` array; teammates can read this to discover each other.

Subagent definitions as teammates:

- Any subagent definition (project, user, plugin, CLI) can be referenced when spawning a teammate.
- The teammate uses the definition's `tools` and `model`, with the body appended as additional instructions.
- `skills` and `mcpServers` from the subagent definition are **not** applied to teammates. Teammates load these from project/user settings.
- Team coordination tools (SendMessage, task tools) are always available even when the definition restricts `tools`.

Quality gate hooks:

- `TeammateIdle` — runs when a teammate is about to go idle. Exit code 2 sends feedback and keeps the teammate working.
- `TaskCreated` — runs when a task is being created. Exit code 2 prevents creation.
- `TaskCompleted` — runs when a task is being marked complete. Exit code 2 prevents completion.

Display modes:

- **In-process** (default): all teammates in one terminal. Shift+Down cycles between them.
- **Split panes**: requires tmux or iTerm2. Each teammate gets its own pane.

Use agent teams when:

- teammates need to challenge each other or share findings directly
- the lead would otherwise become a communication bottleneck
- the task graph benefits from self-claiming and dynamic reassignment

Do not use agent teams when:

- only the result matters
- the work is small enough for subagents
- the coordination overhead outweighs the collaboration benefit

## Codex multi-agents

Source: https://developers.openai.com/codex/concepts/multi-agents

Official guidance emphasizes protecting the main thread:

- Keep the main agent focused on requirements, decisions, and final outputs.
- Use parallel workers for exploration, tests, or log analysis.
- Return summaries from workers instead of raw intermediate output.
- Start with tasks that mostly read. Write-heavy parallelism is higher risk because conflicts and coordination costs rise quickly.

Suggested usage pattern:

- Main thread owns scope, approvals, and final synthesis.
- Parallel workers handle read-heavy scans, review, testing, summarization, and narrowly scoped changes.
- Merge one result at a time after validation.

Current model examples rotate on [developers.openai.com/codex/concepts/multi-agents](https://developers.openai.com/codex/concepts/multi-agents) — pair a stronger reasoning model (multi-step implementation, code review, security-sensitive work) with a faster, cheaper variant (exploration, read-heavy scans, summaries). Check the page for the current model names before committing to specific IDs; prior editions pinned `gpt-5.3-codex` / `gpt-5.3-codex-spark`, but OpenAI refreshes these every few months.

Do not hardcode specific model IDs into the main skill or worker prompts. Re-verify before use.

## Codex subagents

Source: https://developers.openai.com/codex/subagents

Codex supports spawning specialized subagents in parallel, then collecting results in one consolidated response. Unlike Claude Code subagents (auto-delegated), Codex subagents require explicit user activation.

### Activation and management

- Users must explicitly request subagent workflows (e.g., "Spawn one agent per point, wait for all of them, and summarize the result for each point").
- Use `/agent` in CLI to switch between active agent threads.
- Approval overlays show source thread labels; press `o` to open threads before approving.

### Concurrency configuration

Settings under `[agents]` in configuration:

| Parameter | Default | Purpose |
|-----------|---------|---------|
| `max_threads` | 6 | Concurrent open agent thread cap |
| `max_depth` | 1 | Spawned agent nesting depth (prevents recursive fan-out) |
| `job_max_runtime_seconds` | 1800 | Per-worker timeout for CSV batch jobs |

Increasing `max_depth` beyond 1 risks repeated fan-out, which increases token usage, latency, and local resource consumption.

### Custom agent definition

TOML files in `~/.codex/agents/` (personal) or `.codex/agents/` (project-scoped).

Required fields: `name`, `description`, `developer_instructions`.

Optional fields: `nickname_candidates`, `model`, `model_reasoning_effort`, `sandbox_mode`, `mcp_servers`, `skills.config`.

Example:

```toml
name = "pr_explorer"
description = "Read-only codebase explorer for gathering evidence"
model = "gpt-5.3-codex-spark"
sandbox_mode = "read-only"
developer_instructions = """
Trace real execution paths, cite files and symbols, avoid proposing fixes.
"""
```

### Isolation and sandbox

- Subagents inherit the parent session's sandbox policy (read-only, workspace-write, etc.).
- Runtime overrides (sandbox choices, approval settings, `--yolo`) apply to children.
- Non-interactive flows: actions requiring new approval fail, surfacing errors to parent.

### Built-in agents

Codex ships with defaults (overridable by custom agents with matching names):

- `default` — general-purpose fallback
- `worker` — execution-focused implementation
- `explorer` — read-heavy codebase exploration

### CSV batch processing (experimental)

The `spawn_agents_on_csv` tool processes tabular work items — one worker per row. Each worker must call `report_agent_job_result` exactly once. Exported CSV includes original data plus `job_id`, `item_id`, `status`, `last_error`, `result_json`.

## OpenAI Agents SDK

Sources:

- https://openai.github.io/openai-agents-python/agents/
- https://openai.github.io/openai-agents-python/multi_agent/

OpenAI exposes two broad orchestration patterns:

### Manager / agents-as-tools

- One orchestrator keeps control of the conversation.
- Specialist agents are exposed as tools.
- Best when the lead should retain responsibility for user interaction, gating, and synthesis.

Use this when:

- the user should experience one coherent owner
- the lead must apply consistent policy before and after each specialist call
- specialists do bounded work and return outputs rather than take over

### Handoffs

- A specialist agent receives the conversation history and takes over the interaction.
- Best when ownership should move to the specialist, not back to the original lead after every step.

Use this when:

- the specialist needs to own the next turn
- the conversation is naturally routed by domain, queue, or workflow stage
- decentralized control is acceptable

### Capability additions

Per @OpenAIDevs ([source](https://x.com/OpenAIDevs/status/2044466699785920937)):

- **Controlled sandboxes** for long-running agents — use as the default isolation surface for edit-capable OpenAI workers, parallel to worktree isolation on Claude Code.
- **Open-source harness is inspectable and customizable** — you can replace the default run loop while keeping the SDK's primitives. Relevant when manager/handoff is too rigid for a workflow.
- **Explicit control over memory creation and storage** — decide when writes happen and where they land; aligns with the opt-in memory guidance in [../../agents-subagents/references/agent-tools.md](../../agents-subagents/references/agent-tools.md).

Verify exact API surface against the SDK docs before committing to the capability — the tweet is an announcement, not a spec.

### Cross-platform takeaway

- If control should stay centralized, use a lead manager and workers as tools or bounded subagents.
- If ownership should move, use handoffs.
- If workers must collaborate with each other, use a team-style surface rather than forcing all coordination through the lead.

## Prompt structure for reusable worker prompts

Source: https://developers.openai.com/api/docs/guides/prompt-caching

To improve reuse and caching:

- Put static instructions, examples, and reusable policy text first.
- Put task-specific or user-specific payloads last.
- Keep tool lists and prompt prefixes stable across similar worker launches.

This matters most when a lead launches many workers with the same operating instructions and only a small task payload changes.
