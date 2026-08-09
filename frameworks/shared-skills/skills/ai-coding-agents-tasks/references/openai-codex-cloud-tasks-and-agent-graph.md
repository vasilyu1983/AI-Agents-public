# OpenAI Codex Cloud Tasks and Agent Graph

Sources:
- OpenAI Codex repo, commit `9f42c89c0112771dc29100a6f3fc904049b2655f`
- `codex-rs/cloud-tasks/src/cli.rs`
- `codex-rs/cloud-tasks/src/app.rs`
- `codex-rs/agent-graph-store/src/store.rs`

Use this reference when designing hosted task queues, "best of N" task runs, apply/diff flows, or parent-child task topology for coding-agent runtimes.

## Table of Contents

- [What To Steal](#what-to-steal)
- [Agent Graph Store Pattern](#agent-graph-store-pattern)
- [Portable Runtime Contract](#portable-runtime-contract)
- [Tests To Require](#tests-to-require)
- [Source Links](#source-links)

## What To Steal

### Task CLI as lifecycle boundary

Codex models cloud tasks as explicit CLI operations, not only as chat commands:

- `exec` creates a task with prompt, branch, env, and attempt count.
- `status` inspects a known task.
- `list` is bounded by environment and limit.
- `apply` materializes a chosen task result into the local worktree.
- `diff` inspects a task result before applying.

This is a cleaner boundary than "background chat did something." A hosted coding-agent runtime should treat each task result as an artifact that can be inspected, diffed, and applied by a separate command path.

### Best-of-N attempts as a first-class field

Codex bounds task attempts in the CLI with a small range. The useful pattern is not the exact numeric limit; it is that "run several independent attempts" is part of the task request, not an external loop.

Design rule:
- Store `attempt_count` on the task.
- Attribute each attempt separately.
- Pick/apply one result explicitly.
- Keep abandoned attempts inspectable until retention expires.

Known trap:
- Do not merge all attempts into one transcript. That destroys comparison and blame when one attempt was useful and another was unsafe.

### Apply is not success/failure only

The Codex task app has explicit apply-result levels:

- success
- partial
- error

It also models skipped and conflicting paths. Import this state shape. "Apply failed" is too coarse for agent tasks because partial application can leave useful local files and unresolved conflicts.

Minimum apply result fields:

- `task_id`
- `attempt_id`
- `applied_paths`
- `skipped_paths`
- `conflict_paths`
- `result_level`
- `message`

Known trap:
- If partial apply is possible, the UI and task store must both represent it. A green terminal line with conflicted files is a misleading state.

### Environment-scoped listing

Codex task listing is environment-filtered. That pattern matters for multi-tenant or multi-repo hosts.

Task list queries should include:

- account or org
- repo or workspace
- branch
- environment
- limit
- sort key

Known trap:
- A global "recent tasks" list is useful for humans but dangerous as a runtime API. It can accidentally apply or cancel work from the wrong repo or environment.

## Agent Graph Store Pattern

Codex has a small persistent agent graph store for parent-child thread topology. The reusable shape:

- Store parent thread id, child thread id, task id, status, and timestamps.
- Upsert edges idempotently.
- Return children in stable ordering.
- Traverse descendants breadth-first.
- Let status updates target an existing edge.

This is the missing link between "spawn a subagent" and "understand the task tree later."

Design rule:
- Treat task topology as runtime state, not transcript decoration.
- Parent-child links must survive process restart.
- Store status on the edge or relationship when the child thread's own status is not enough.

Known trap:
- Reconstructing topology from message text works until resumes, compaction, or remote tasks split the transcript.

## Portable Runtime Contract

For a coding-agent task system, import these fields:

```text
TaskRequest
  prompt
  repo/workspace
  branch
  environment
  attempt_count
  parent_thread_id?
  requested_by

TaskAttempt
  attempt_id
  task_id
  status
  transcript_ref
  diff_ref?
  result_ref?

TaskApplyResult
  task_id
  attempt_id
  result_level: success | partial | error
  applied_paths[]
  skipped_paths[]
  conflict_paths[]
```

## Tests To Require

- Creating a task with invalid attempt count is rejected before dispatch.
- Listing tasks cannot cross the requested environment.
- Diff does not mutate local files.
- Apply reports partial success when one path applies and one conflicts.
- Applying the same attempt twice is idempotent or explicitly refused.
- Parent-child graph returns stable child ordering.
- Descendant traversal does not loop if bad data creates a cycle.

## Source Links

- [cloud-tasks CLI](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/cloud-tasks/src/cli.rs)
- [cloud-tasks app](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/cloud-tasks/src/app.rs)
- [agent graph store](https://github.com/openai/codex/blob/9f42c89c0112771dc29100a6f3fc904049b2655f/codex-rs/agent-graph-store/src/store.rs)
