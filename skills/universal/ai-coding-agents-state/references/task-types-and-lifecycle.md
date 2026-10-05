# Task Types And Lifecycle

## Table Of Contents

- [Design Goal](#design-goal)
- [Typed Task Families](#typed-task-families)
- [Background Visibility](#background-visibility)
- [Cancellation Semantics](#cancellation-semantics)

## Design Goal

Coding-agent runtimes need a typed task model. The `claude_code` runtime distinguishes task families instead of treating all work as one generic async job.

## Typed Task Families

`tasks/types.ts` and the task modules show a union of concrete task families such as:

- local shell tasks
- local agent tasks
- remote agent tasks
- in-process teammate tasks
- workflow tasks
- monitor tasks
- dream or speculative tasks

This is the right pattern:

- type task families explicitly
- give each one its own lifecycle and detail renderer
- use a shared union only where the UI or host truly needs “any task”

## Background Visibility

`isBackgroundTask(...)` in `tasks/types.ts` encodes an important rule:

- only running or pending work counts
- foregrounded work should not be shown as background work

That is worth copying because coding-agent UIs often over-count tasks and confuse the user about what is actually “in the background.”

## Cancellation Semantics

The surrounding task and teammate code distinguishes:

- abort current work
- keep the worker alive
- kill the task or worker entirely

Preserve that distinction. “Interrupt” and “kill” are not the same lifecycle action in coding-agent runtimes.

Make kill two-phase:

1. A cancel request moves the task to `cancelling`.
2. The worker acknowledges, or a hard-kill deadline expires.
3. The runtime kills the whole process group and cascades cancellation to child tasks.
4. The task becomes terminal only after the children are reaped.

A terminal state set before the children are reaped leaves orphan shells still mutating the workspace.
