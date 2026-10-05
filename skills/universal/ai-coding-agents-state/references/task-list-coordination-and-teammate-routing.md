# Task List Coordination And Teammate Routing

## Table Of Contents

- [Design Goal](#design-goal)
- [File-Watched Task Lists](#file-watched-task-lists)
- [Claiming And Release](#claiming-and-release)
- [Blocked Tasks](#blocked-tasks)
- [Teammate Routing](#teammate-routing)

## Design Goal

Background task systems for coding agents should support both host-owned runtime tasks and externally-created task lists that workers can pick up automatically.

## File-Watched Task Lists

`useTaskListWatcher.ts` shows a practical model:

- watch a task-list directory
- debounce filesystem events
- check for work only when the agent is idle
- submit one claimed task as the next prompt

This creates a durable “tasks mode” without requiring continuous polling from the main session loop.

## Claiming And Release

The watcher also shows correct claim behavior:

- claim a task before turning it into work
- if submission fails, release the claim
- keep current-task tracking so the worker does not pick up new work until the old one is resolved

That is the right baseline for multi-worker task acquisition. Across processes or hosts, make the claim a lease with a fencing token:

- The claim records the owner, a lease deadline, and a monotonically increasing fencing token.
- The worker renews the lease by heartbeat and presents the token on every progress, complete, or release write.
- The store rejects writes carrying an old token, so a paused worker that wakes after reclaim cannot overwrite the new owner.
- An expired lease is the only path to stale-owner recovery.

Pattern template: [`../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md`](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md).

Completion needs the same care. Write the result (or artifact reference) and the `completed` status in one atomic write, or write the result first and flip the status idempotently. A retry after a claim checks for an existing result before re-executing, so a crash between the two writes produces neither "done with no output" nor a re-run of finished side-effecting work.

## Blocked Tasks

The available-task filter is not just “first pending task.” It also checks:

- no owner assigned
- blockers are completed

This is a good minimum scheduler for coding-agent task queues with dependencies.

## Teammate Routing

The teammate navigation and swarm-permission code show that worker tasks are not just queue items. They also participate in leader-worker coordination:

- teammate tasks have dedicated views
- leader and teammate views are distinct
- permission responses may route back from the leader to a worker task

Treat teammate tasks as runtime actors with UI and approval implications, not just rows in a task list.
