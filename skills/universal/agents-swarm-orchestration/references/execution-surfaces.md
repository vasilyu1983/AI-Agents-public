# Execution Surfaces

Use this reference when the lead already has a valid plan and now needs to choose the orchestration surface: single thread, isolated workers, Claude Code agent team, manager, or handoff.

## Table of Contents

- [Single Thread](#single-thread)
- [Subagents Or Codex Workers](#subagents-or-codex-workers)
- [Claude Code Agent Teams](#claude-code-agent-teams)
- [Agent Team Communication Patterns](#agent-team-communication-patterns)
- [Cross-Session Messaging](#cross-session-messaging)
- [Manager vs Handoff](#manager-vs-handoff)

## Single Thread

Stay in the main conversation when there are fewer than 3 bounded tasks, when multiple changes hit the same module, or when the lead still needs to make core product or architecture decisions.

Use single-thread execution when:

- ownership is still fluid
- interfaces are not frozen
- the work is small enough that coordination overhead outweighs any gain

## Subagents Or Codex Workers

Use isolated workers when the lead only needs the result back:

- targeted exploration
- log or test triage
- bounded implementation on exclusive files
- code review or verifier passes

Platform notes:

- Claude Code subagents may auto-delegate based on the registered description.
- Claude Code background behavior depends on the active mode. Standard mode may use foreground when the result is needed; agent-view fork mode runs Claude-spawned subagents in the background. `background: true` forces background, but `false` is not a documented foreground pin. Current background permission requests surface in the main conversation.
- Codex subagents require explicit spawning.
- Codex concurrency and recursion controls vary by active runtime surface. Do not hardcode undocumented `max_threads` or `max_depth` keys; discover the callable tool/config schema and keep ordinary workers leaf-only by policy.
- Claude Code recursive spawn has a configurable depth cap; look up the current default and setting before relying on it. Keep nesting at depth 1 (2 for hierarchical migrations) by policy because recursive fan-out multiplies tokens and latency quickly and errors compound uncaught across levels.

## Claude Code Agent Teams

Use agent teams when workers need direct discussion, self-coordination, or a shared task list. Reserve this for work where teammate-to-teammate communication is part of the solution rather than a convenience.

Check the current docs for this surface's status and enabling flag before choosing it; while it is experimental, behavior changes between CLI releases. Constraints before choosing this surface:

- **Team config is runtime state, not an authored artifact.** Setup and cleanup are automatic; do not pre-author or version `~/.claude/teams/`. Reusable roles belong in subagent definitions, which are referenced at spawn time.
- **Team and current forked-subagent work reports through notifications and task state.** Design dependencies around completion state rather than assuming a synchronous return value.
- **A subagent definition's `skills:` and `mcpServers` frontmatter is ignored when it runs as a teammate.** Teammates load skills and MCP servers from project/user settings instead. A worker that depends on a preloaded skill will silently run without it.
- **Teammates share the lead checkout.** `isolation: worktree` on a reused definition does not isolate a teammate; assign disjoint files or use ordinary isolated subagents.

Good fits:

- complex implementation where workers need to negotiate an interface live
- shared triage boards where teammates self-claim unblocked work
- debate or review boards where findings move laterally before they reach the lead

## Agent Team Communication Patterns

Agent teams coordinate through three mechanisms.

### SendMessage

- Direct: send to one teammate by name for task-specific coordination, findings handoff, or shutdown requests.
- Broadcast: send to all teammates simultaneously. Use sparingly because token cost scales with team size.

### Shared task list

- All teammates see task status and can self-claim unblocked work.
- Tasks have statuses such as `pending`, `in_progress`, and `completed`, plus dependency relationships.
- Task claiming typically relies on file locking to avoid race conditions.
- Claude task files are stored under `~/.claude/tasks/{team-name}/`.

### Context sharing principles

- No shared memory: teammates do not inherit the lead’s conversation history or each other’s context windows.
- Coordinate through state, not ambient context: pass findings via `SendMessage` and task-file updates.
- Distill before sharing: send synthesis, not raw logs, stack traces, or long transcripts.

### Teammate lifecycle tools

| Tool | Who Uses It | Purpose |
|------|-------------|---------|
| `SendMessage` | Any teammate | Direct or broadcast messaging |
| `TaskList` | Any teammate | View all tasks and statuses |
| `TaskUpdate` | Any teammate | Claim, complete, or update tasks |

Team creation and cleanup are lifecycle behavior, not tools to call or config files to pre-author.

### Quality-gate hooks

Optional hooks can keep team work disciplined:

- `TeammateIdle`: give feedback and keep the teammate active if the result is not good enough yet
- `TaskCreated`: validate a task before it enters the list
- `TaskCompleted`: enforce quality checks before a task is marked complete

## Cross-Session Messaging

Independent Claude Code sessions can message each other directly without forming a team or enabling the teams flag. Look up the minimum CLI version, supported platforms, and whether remote or cloud sessions can send as well as receive before designing a flow around it.

Use it when the only thing that has to cross a session boundary is a finding:

- a long-running session in another terminal or worktree needs to hand back a result
- two humans-in-the-loop sessions are working adjacent areas and one discovers something the other needs
- you want peer messaging without accepting the agent-teams caveats above

Prefer a full agent team only when you also need the shared task list, self-claiming, or the `TeammateIdle` / `TaskCreated` / `TaskCompleted` quality gates. If the requirement is just "pass this finding over there", cross-session messaging is the lighter surface and is not experimental.

Same distillation discipline applies: send synthesis, not raw logs. Windows sessions have no equivalent — fall back to file-backed state.

## Manager vs Handoff

For OpenAI-style multi-agent systems:

- Use manager or agents-as-tools when one orchestrator should keep control of the user conversation.
- Use handoffs when the next specialist should own the conversation and receive the history.

The distinction is ownership. In a manager pattern, the lead still owns requirements, approvals, and synthesis. In a handoff pattern, ownership moves with the conversation itself.
