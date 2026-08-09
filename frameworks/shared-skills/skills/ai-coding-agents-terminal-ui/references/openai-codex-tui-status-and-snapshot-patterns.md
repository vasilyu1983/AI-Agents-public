# OpenAI Codex TUI Status And Snapshot Patterns

Source snapshot: OpenAI Codex commit `9f42c89c0112771dc29100a6f3fc904049b2655f` (2026-05-24), especially `codex-rs/tui/src/chatwidget`, `codex-rs/tui/src/chatwidget/snapshots`, and `codex-rs/cli/src/doctor/output`.

Web sources checked 2026-05-25:

- OpenAI, "Codex for (almost) everything", Apr 16, 2026: https://openai.com/index/codex-for-almost-everything/
- Codex use cases: https://developers.openai.com/codex/use-cases

## Table Of Contents

- [Design Goal](#design-goal)
- [Status Surfaces](#status-surfaces)
- [Approval Rendering](#approval-rendering)
- [Snapshot Coverage](#snapshot-coverage)
- [Multi-Surface Consistency](#multi-surface-consistency)
- [Known Traps](#known-traps)

## Design Goal

Terminal UI is a runtime surface, not a logging afterthought. Codex snapshot tests cover chat layout, approvals, status line, terminal title, hooks, plugin popups, app-server events, background terminals, and small terminal sizes.

## Status Surfaces

Codex treats status as multiple coordinated surfaces:

- in-chat status output
- status line
- terminal title
- setup popups
- rate-limit refresh outputs
- thread names and resume hints

For new TUIs, define which fields appear on each surface and test them separately. Status line and terminal title need compact versions of the same truth.

## Approval Rendering

Codex snapshots cover:

- exec approval modals
- patch approval modals
- auto-review approvals and denials
- guardian review timeout and denial states
- approval choices that let users deny and steer the agent

Best practice:

- render the requested command or patch clearly
- preserve the reason and risk context
- make denial plus steering a first-class path
- test multiline and no-reason cases

## Snapshot Coverage

Snapshot-test the awkward states, not only the happy path:

- narrow terminal dimensions
- running vs idle chat
- hook output before or during assistant messages
- interrupted turns
- background terminal list and stop flow
- plugin detail popups
- app-server warnings
- goal active, blocked, complete, and budget-limited states

## Multi-Surface Consistency

OpenAI's product direction increasingly spans CLI, app, browser, remote devboxes, and computer use. The terminal UI should therefore avoid owning facts that belong to the session core. It should render state supplied by the core and expose user choices back as typed events.

## Known Traps

- Treating terminal output as untestable prose.
- Letting status line, title, and chat output drift.
- Making approval modals unreadable in narrow terminals.
- Hiding hook or app-server warnings until after the next assistant message.
- Designing CLI-only state that cannot be mirrored in desktop or remote clients.
