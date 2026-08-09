---
name: ai-coding-agents-terminal-ui
description: "Designs terminal-first coding-agent UX: REPL, prompt input, status lines, keybindings, display modes. Use when shaping TUI rendering, history, or background-task navigation."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# AI Coding Agents Terminal UI

Use this skill to design or review the terminal-first user experience of a coding-agent runtime: REPL structure, prompt input, message rendering, command queues, virtualized history, interrupt behavior, notifications, and background-task navigation.

This skill is for terminal interaction patterns, not generic desktop app UX.

## ASCII Flow

```text
runtime events
  |
  v
host-owned REPL state
  transcript + prompt input + command queue + background tasks + overlays
  |
  v
render pipeline
  message model + virtualized history + notifications + task surfaces
  |
  v
input state machine
  idle | editing | running | search | overlay | teammate view | remote/viewer
  |
  v
runtime action
  submit, interrupt, foreground task, kill task, search, rewind, resume
```

## Quick Reference

| Question | Read | Outcome |
|----------|------|---------|
| How should the REPL, prompt, and history work? | [`references/repl-message-input-and-history.md`](references/repl-message-input-and-history.md) | Message model, prompt queue, input behavior, interrupt handling |
| How should background work and large histories render? | [`references/background-work-notifications-and-virtualization.md`](references/background-work-notifications-and-virtualization.md) | Background-task UX, notifications, virtual scroll, and teammate navigation |
| What are the input states and keybindings for background navigation? | [`references/input-state-machine.md`](references/input-state-machine.md) | State machine, transition table, mode-specific keybindings, invariants, failure modes |
| How do ToolSearch deferred-tool results render in the REPL? | [`references/recipe-toolsearch-render.md`](references/recipe-toolsearch-render.md) | Discovery annotation, collapse behavior, permission-prompt sequencing, scroll rules |
| What OpenAI Codex TUI patterns should be snapshot-tested? | [`references/openai-codex-tui-status-and-snapshot-patterns.md`](references/openai-codex-tui-status-and-snapshot-patterns.md) | Status line/title, approval modals, hook/app-server warnings, narrow terminal states |
| What are Claude Code's real status-line fields, keybinding contexts, and Agent Teams display modes? | [`references/input-state-machine.md`](references/input-state-machine.md) | Verified `statusLine` JSON fields, `keybindings.json` contexts/reserved keys, in-process vs split-pane display modes |

## When To Use

- Design a terminal-first coding-agent REPL or prompt UI
- Decide how message history, search, rewind, and interrupt should behave
- Add background-task surfaces, teammate navigation, or task detail dialogs
- Improve large-session rendering with virtualization or deferred updates
- Separate interactive UI behavior from headless or SDK behavior

## Use Other Skills

| Need | Use Instead |
|------|-------------|
| Background task runtime design | [`../ai-coding-agents-tasks/SKILL.md`](../ai-coding-agents-tasks/SKILL.md) |
| Remote or bridge runtime | [`../ai-coding-agents-remote-runtime/SKILL.md`](../ai-coding-agents-remote-runtime/SKILL.md) |
| Tool approval architecture | [`../ai-coding-agents-permissions/SKILL.md`](../ai-coding-agents-permissions/SKILL.md) |

## Default Workflow

1. **Keep the REPL as a host-owned state machine.** Prompt input, message history, background tasks, and overlays should share one session model.
2. **Separate transcript data from render strategy.** Large histories need virtualization and deferred rendering, not truncated state ownership.
3. **Use dedicated stores for high-frequency signals.** Command queues, scroll state, and background-task counts should not force full-tree re-renders.
4. **Treat interrupt behavior as first-class UX.** Idle escape, active interrupt, teammate-view escape, and remote interrupt are different actions.
5. **Make background work navigable.** Users should be able to inspect, foreground, or kill tasks without losing the main session.
6. **Model interactive-only features explicitly.** Some callbacks and overlays exist only in REPL mode and should not leak into headless paths.
7. **Test long sessions.** Verify search, rewind, virtualization, notification timing, and prompt-input persistence after hundreds of turns.

## Host Rules

- The UI should not own semantic session state that the runtime cannot restore.
- Large histories should optimize mounting and scroll math, not just terminal paint.
- Background work deserves a first-class dialog or tree, not a single badge count.
- Prompt input should survive round-trips through overlays, interrupts, and search.
- Interactive UI behavior should degrade cleanly when the runtime is headless, remote, or viewer-only.

## Build Order

1. Define the host-owned REPL state machine.
2. Separate transcript data from render state and scroll math.
3. Add prompt input persistence through overlays and interrupts.
4. Add background-task navigation and notifications.
5. Add virtualization for long histories.
6. Add remote, headless, and viewer-only degradation rules.

## Core Invariants

- The UI renders runtime state; it does not become the only owner of it.
- Prompt input must survive mode changes and overlays.
- Interrupt semantics must map to explicit runtime actions.
- Background work must be inspectable without destroying main-session context.
- Long-session performance must come from virtualization, not silent truncation of semantic history.

## Failure Modes

- Losing prompt input when entering search, overlays, or teammate views.
- Treating idle escape, active interrupt, and exit as one key path.
- Background-task dialogs drifting out of sync with runtime task state.
- Scroll jumps and mount churn during resize or long-session replay.
- Interactive-only affordances leaking into headless or viewer-only modes.

## Minimal Viable Version

- One host-owned REPL state machine.
- One persistent prompt input model.
- One explicit interrupt path for active turns.
- One navigable background-task surface.
- One virtualization strategy for long histories.

## What Strong Implementations Add

- Dedicated stores for high-frequency UI signals.
- Teammate navigation and task-detail overlays with state preservation.
- Deferred range growth, overscan tuning, and resize-stable virtual scroll.
- Notification queues that do not steal focus or input state.
- Viewer-only and remote-specific UI restrictions that match runtime capability.

## Known Traps

- Letting the UI become the system of record for session or task state that the runtime cannot restore after reconnect or resume.
- Re-rendering long histories or background panels on every scroll, queue, or notification update until the terminal becomes unusable under real sessions.
- Treating background work as counters instead of navigable surfaces with recoverable detail, status transitions, and cancellation context.
- Using the same keybindings and escape behavior for every UI mode and creating accidental destructive actions.
- Solving history performance by discarding semantic structure that replay, accessibility, or auditing still needs.

## Common Anti-Patterns

- Letting the UI own session semantics that resume cannot restore.
- Re-rendering the full history tree on every queue or scroll update.
- Using one “escape” behavior for every UI state.
- Treating background work as a badge count instead of a navigable surface.
- Solving long-session rendering by dropping semantic history on the floor.

## TUI Framework Selection

As of mid-2026, the main choices for coding-agent terminal UIs are:

| Framework | Language | Used by | Notes |
|-----------|----------|---------|-------|
| Ink 6 + React 19 | TypeScript | Claude Code, Gemini CLI | Mature; component model familiar to web developers; commonly cited ~30 FPS render cap and ~50 MB+ baseline (verify against target environment before treating as hard limits); large ecosystem |
| Ratatui | Rust | Codex (codex-rs/tui) | Low overhead; strong for high-frequency event loops; explicit layout model |
| Bubble Tea v2 | Go | Various OSS tools | Declarative View/Update/Init pattern; v2 adds concurrent commands |
| OpenTUI | TypeScript/emerging | — | Emerging; watch but do not depend on for production |

**Selection heuristics:**
- Rust runtime: Ratatui avoids a separate language runtime.
- TypeScript/Node runtime (Claude Code, Gemini CLI pattern): Ink 6 is the established choice.
- Go with message-driven architecture preference: Bubble Tea v2.
- Avoid mixing two TUI frameworks in the same surface.

**Dual-surface invariant:** both a CLI surface and a desktop (GUI) surface should consume a shared typed daemon or ACP server. Rendering stacks may differ — Ink for CLI, Tauri/web for desktop — but the **protocol contract must be identical**. Goose 2.0 (AAIF, April 2026) is the canonical example: TypeScript TUI and Tauri desktop are both clients of the same ACP daemon; message model, tool results, and interrupt semantics flow through the same protocol.

## Cross-Platform Patterns (Goose)

Goose (AAIF, formerly Block) 2.0 ships a **TypeScript TUI** (beta: `npx @aaif/goose`) and is migrating the **desktop from Electron to Tauri** — both clients of a shared ACP daemon, not separate runtimes. This updates the earlier Ink-style REPL + Electron desktop description.

### Fixed-grid, no-overflow rendering

Goose's terminal renderer has **no overflow clipping**. Content wider than its container *visually corrupts the frame* — there is no scroll-to-reveal. All content must be pre-truncated to its container's character dimensions before being emitted.

- **Pattern:** treat container dimensions as a hard input to rendering. Message blocks compute their truncation *before* the renderer sees them. Resize events are first-class and trigger re-layout at the content level, not just the terminal repaint level.
- **Anti-pattern:** relying on terminal scroll or native overflow to handle long lines. This works by accident in some terminals and corrupts output in others. Long provider responses, wide diffs, and tool output are the main offenders.
- **Recipe:** every message component accepts `(max_cols, max_rows)` and returns pre-truncated content plus an "expand" affordance that opens a separate dialog/pager. The REPL state machine tracks which messages are collapsed-due-to-space vs. collapsed-by-user.

### Dual-surface invariant (CLI + desktop, shared ACP daemon)

Goose's desktop UI is not a different product — it is a client of the same ACP daemon as the CLI (see `ai-coding-agents-remote-runtime` for the daemon pattern). Message blocks, keybindings, and interrupt semantics must work in both surfaces because they are defined at the protocol level, not the rendering layer.

- **Pattern:** design components against the smaller surface (CLI) first. Desktop adds window management, copy/paste affordances, and native GUI controls, but the message model is identical.
- **Anti-pattern:** maintaining parallel message components for "CLI" and "desktop." This produces visual drift, divergent keybindings, and features that exist in one surface but not the other.
- **Recipe:** one component library renders both surfaces. The desktop shell provides hooks for native affordances (file drag-and-drop, OS notifications) but never replaces the core render pipeline.

## Claude Code Reference: Status Lines, Keybindings, Agent Teams

Verified 2026-07-11 against `code.claude.com/docs/en/statusline`, `.../keybindings`, and `.../agent-teams`. Use this as ground truth before inventing status-line fields or keybindings for a design that claims Claude Code parity — the dominant failure mode in this space is presenting a plausible-sounding key or field as fact when it does not exist in the shipped product.

**Status line.** The status line is a user-supplied shell command (`statusLine.type = "command"`) that receives one JSON blob on stdin per update and prints text to stdout — it does not own state, it renders a snapshot. Expert traps:
- The command's stdout is captured, not connected to the real terminal, so `tput cols` and other terminal-size probes return nothing inside the script. Read the `COLUMNS`/`LINES` environment variables Claude Code injects instead (v2.1.153+). Any status-line design that assumes direct TTY access from a subprocess will silently misrender width.
- Updates are event-driven (new assistant message, `/compact`, permission-mode change, vim-mode toggle) and debounced 300ms; a script still running when a new trigger fires gets cancelled mid-run. Use the optional `refreshInterval` (minimum 1s) only for genuinely time-based segments (a clock, idle-session cost drift) — polling for no reason burns a process tick every interval even when nothing changed.
- The status line hides during autocomplete, help, and permission prompts, and renders in its own row above the footer badges rather than replacing them — do not design it as the only place transient status can live.

**Keybindings.** Real customization lives in `~/.claude/keybindings.json` (`$schema`, `$docs`, `bindings[]`, each block scoped to a `context` such as `Chat`, `Task`, `HistorySearch`, `Footer`, `MessageSelector`). Load-bearing facts that contradict looser generic TUI assumptions:
- `Ctrl+C`, `Ctrl+D`, `Ctrl+M`, and Caps Lock are hard-reserved and cannot be rebound.
- `Ctrl+B` is the default for `task:background`, but it collides with the tmux prefix key — that's why a second chord, `Ctrl+X Ctrl+B`, exists as of v2.1.169 specifically to avoid that conflict. Any coding-agent TUI that binds a primary action to `Ctrl+B` needs a tmux-safe alternate chord, not just a note in the docs.
- There is no default per-item "kill" or "foreground" key on an individual background task in the footer/task surfaces; the real primitives are `task:background` (send current turn to background) and `chat:killAgents` (`Ctrl+X Ctrl+K`, stops *all* running background subagents at once). Do not assume a granular per-task kill shortcut exists — build one if your design needs it and document it as new, not "standard."
- History recall is asymmetric: `historySearch:execute` (Enter) *runs* the selected past command immediately, while `historySearch:accept` (Escape or Tab) only *fills* the input without executing. A design that treats Enter-in-search as "just paste" will surprise users by re-running commands.

**Agent Teams display modes.** As of v2.1.178+, the default `teammateMode` is `"in-process"` (before v2.1.179 the default was `"auto"`, so upgraded configs that relied on the old default now stay in-process unless set explicitly). Split-pane mode (`"tmux"` or, from v2.1.186, `"iterm2"`) requires tmux or iTerm2 with the `it2` CLI and is **not supported** in VS Code's integrated terminal, Windows Terminal, or Ghostty. Teammate navigation in in-process mode is Up/Down arrows to select a teammate in the agent panel, Enter to open its transcript and message it directly, Escape to interrupt its current turn, and `x` to stop a selected teammate — there is no Shift+Up/Down teammate-navigation binding in the shipped product; that pattern in the References below is illustrative design guidance, not a documented Claude Code shortcut. Treat split-pane availability as a runtime capability to detect, not a default to assume.

## Navigation

### References

- [`references/repl-message-input-and-history.md`](references/repl-message-input-and-history.md) — REPL ownership, prompt queue, interrupt semantics, and message history
- [`references/background-work-notifications-and-virtualization.md`](references/background-work-notifications-and-virtualization.md) — Background-task navigation, notifications, and virtualized long-session rendering
- [`references/input-state-machine.md`](references/input-state-machine.md) — Input state machine for background navigation modes with transition table and keybinding rules
- [`references/recipe-toolsearch-render.md`](references/recipe-toolsearch-render.md) — How ToolSearch deferred-tool results render in the REPL
- [`references/openai-codex-tui-status-and-snapshot-patterns.md`](references/openai-codex-tui-status-and-snapshot-patterns.md) — OpenAI Codex TUI status surfaces, approval rendering, app-server/hook warnings, and snapshot coverage

### Data

- [`data/sources.json`](data/sources.json) — Primary documentation and source references for terminal-agent UI patterns

### Related Skills

- [`../ai-coding-agents-tasks/SKILL.md`](../ai-coding-agents-tasks/SKILL.md)
- [`../ai-coding-agents-remote-runtime/SKILL.md`](../ai-coding-agents-remote-runtime/SKILL.md)
- [`../software-ui-ux-design/SKILL.md`](../software-ui-ux-design/SKILL.md)

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- The internal-runtime patterns (REPL ownership, background-task navigation model, virtual-scroll approach) are grounded in a local April 2026 `claude_code` snapshot plus current TUI framework docs and are illustrative design guidance, not documented product behavior — label them as such when presenting to a reader who might mistake them for a shipped feature.
- The status-line fields, `keybindings.json` contexts/actions, and Agent Teams display-mode facts in "Claude Code Reference" above were web-verified on 2026-07-11 against `code.claude.com/docs/en/{statusline,keybindings,agent-teams}` and are current product documentation, not inference from a snapshot. Re-verify before depending on exact field names or key defaults, since these pages carry inline `min-version`/`max-version` notes that shift with releases.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
