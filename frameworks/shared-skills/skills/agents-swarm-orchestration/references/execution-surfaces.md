# Execution Surfaces

Use this reference when the lead already has a valid plan and now needs to choose the orchestration surface: single thread, isolated workers, Claude Code agent team, manager, or handoff.

## Table of Contents

- [Single Thread](#single-thread)
- [Subagents Or Codex Workers](#subagents-or-codex-workers)
- [Claude Code Agent Teams](#claude-code-agent-teams)
- [Agent Team Communication Patterns](#agent-team-communication-patterns)
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
- Codex subagents require explicit spawning.
- Codex defaults to `max_threads: 6` and `max_depth: 1`.
- Keep nesting at depth 1 on both platforms; recursive fan-out multiplies tokens and latency quickly.

## Claude Code Agent Teams

Use agent teams when workers need direct discussion, self-coordination, or a shared task list. Reserve this for work where teammate-to-teammate communication is part of the solution rather than a convenience.

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
| `TeamCreate` | Lead only | Create a new team with a task list |
| `SendMessage` | Any teammate | Direct or broadcast messaging |
| `TaskList` | Any teammate | View all tasks and statuses |
| `TaskUpdate` | Any teammate | Claim, complete, or update tasks |
| `TeamDelete` | Lead only | Clean up team resources |

### Quality-gate hooks

Optional hooks can keep team work disciplined:

- `TeammateIdle`: give feedback and keep the teammate active if the result is not good enough yet
- `TaskCreated`: validate a task before it enters the list
- `TaskCompleted`: enforce quality checks before a task is marked complete

## Manager vs Handoff

For OpenAI-style multi-agent systems:

- Use manager or agents-as-tools when one orchestrator should keep control of the user conversation.
- Use handoffs when the next specialist should own the conversation and receive the history.

The distinction is ownership. In a manager pattern, the lead still owns requirements, approvals, and synthesis. In a handoff pattern, ownership moves with the conversation itself.
