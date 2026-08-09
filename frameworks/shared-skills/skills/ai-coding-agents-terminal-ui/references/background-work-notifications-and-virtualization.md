# Background Work, Notifications, And Virtualization

## Table Of Contents

- [Design Goal](#design-goal)
- [Background Task Navigation](#background-task-navigation)
- [Task Detail Dialogs](#task-detail-dialogs)
- [Deferred And Notification UX](#deferred-and-notification-ux)
- [Virtualized Long Histories](#virtualized-long-histories)

## Design Goal

Terminal coding-agent UIs break down in long sessions unless background work and large histories are treated as first-class UI concerns. The `claude_code` runtime does both.

## Background Task Navigation

`useBackgroundTaskNavigation.ts` shows that background work is navigable, not just counted:

- an arrow-key + Enter pattern moves across teammates or opens the task dialog
- Enter and Escape do different things depending on selection state
- leader and teammate views are separate navigation targets

That is a strong model for coding-agent terminals with concurrent work. **Verified against Claude Code's shipped Agent Teams UX (2026-07-11):** the real bindings are Up/Down arrows to select a teammate in the agent panel, Enter to open its transcript and message it directly, Escape to interrupt its current turn, and `x` to stop a selected teammate — not Shift+Up/Down, and not a single `f` key. If your own design copies this pattern, use plain arrow keys for list selection and reserve Shift-modified arrows for a different action (Claude Code uses Shift+Up/Down elsewhere, for jump-to-top/bottom in message selection) to avoid a collision.

When more than three teammates are idle at once in a real coding-agent runtime, collapse the surplus into a single "N idle agents" row rather than letting the panel grow unbounded — Claude Code does this and expands the collapsed row on Enter. Idle rows should stay addressable (selectable, messageable) even while hidden; hiding a row must not stop the underlying teammate.

## Task Detail Dialogs

`BackgroundTasksDialog.tsx` treats tasks as typed list items with specialized detail views:

- local shell tasks
- local agents
- remote agents
- in-process teammates
- workflows
- monitor tasks

Use the same pattern:

- normalize task list items for selection
- keep per-task-type detail rendering specialized
- exclude foregrounded work from “background” surfaces

## Deferred And Notification UX

The repo also uses deferred hook messages and notification hooks so the REPL can render immediately while slower or less critical status updates arrive later.

That suggests two rules:

- immediate prompt responsiveness wins over eager rendering of all secondary notices
- status and install/update notifications should use a dedicated queue rather than polluting transcript semantics

## Virtualized Long Histories

`useVirtualScroll.ts` is a reminder that terminal UIs still need serious list virtualization:

- estimate heights conservatively
- overscan generously
- quantize scroll-driven re-renders
- keep spacer math stable across resize and rewrap
- cap mounted items to avoid pathological memory growth

For long coding-agent sessions, optimize React and Yoga node count, not just paint speed.
