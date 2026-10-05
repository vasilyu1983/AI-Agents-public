# Input State Machine: Background Navigation Modes

Documents the input-state machine for the terminal REPL, with emphasis on background-navigation modes where keybindings, escape behavior, and prompt-input ownership change.

## Table of Contents

- [State Overview](#state-overview)
- [State Transition Table](#state-transition-table)
- [Invariants](#invariants)
- [Mode-specific keybinding rules](#mode-specific-keybinding-rules)
- [Vendor example: one CLI's bindings](#vendor-example-one-clis-bindings)
- [Input ownership rules](#input-ownership-rules)
- [Failure modes](#failure-modes)
- [Related](#related)

## State Overview

```
States:
  IDLE          — No active agent turn; prompt is ready for user input
  ACTIVE        — Agent turn in progress; interrupt available
  SEARCH        — History search overlay is open
  TEAMMATE      — Teammate-task navigation overlay is open
  BACKGROUND    — Background-task list or detail dialog is open
  REWIND        — Checkpoint/rewind menu is open
  VIEWER        — Read-only remote session; no input path
  HEADLESS      — No terminal attached; interactive affordances disabled
```

## State Transition Table

| Current state | Input / event | Next state | Side effect |
|--------------|---------------|------------|-------------|
| IDLE | User types | IDLE | Prompt buffer accumulates |
| IDLE | Enter | ACTIVE | Submit the prompt; the input stays editable for queuing (see ACTIVE) |
| IDLE | `Ctrl+R` or `/search` | SEARCH | Open history search overlay; preserve prompt buffer |
| IDLE | `Ctrl+B` or `/background` | BACKGROUND | Open background-task surface; preserve prompt buffer |
| IDLE | `Escape` | IDLE | Clear the draft prompt buffer |
| IDLE | `/rewind` or `Esc Esc` | REWIND | Open rewind menu |
| IDLE | Remote viewer attach | VIEWER | Disable input path; show viewer badge |
| ACTIVE | `Escape` (single) or `Ctrl+C` | ACTIVE | Send interrupt signal to agent; show "interrupting..." |
| ACTIVE | `Enter` | ACTIVE | Queue the draft as the next message; does not interrupt the running turn |
| ACTIVE | Agent completes | IDLE or ACTIVE | Deliver the next queued message if any; otherwise keep the draft in the prompt |
| ACTIVE | `Ctrl+B` | BACKGROUND | Open background panel without interrupting agent |
| ACTIVE | Agent spawns teammate | BACKGROUND | Increment background badge; no mode change |
| SEARCH | Type query | SEARCH | Update search results in overlay |
| SEARCH | Execute key | ACTIVE or IDLE | Run the selected history item immediately |
| SEARCH | Fill key | IDLE | Place the selection in the prompt buffer without executing |
| SEARCH | `Escape` | IDLE | Dismiss and restore the prior buffer (if `Escape` is not the fill key) |
| TEAMMATE | Arrow keys | TEAMMATE | Navigate teammate list |
| TEAMMATE | `Enter` | TEAMMATE | Expand selected teammate detail |
| TEAMMATE | `Escape` | prev state | Return to previous state (IDLE or ACTIVE) |
| BACKGROUND | Arrow keys | BACKGROUND | Navigate task list |
| BACKGROUND | `Enter` | BACKGROUND | Expand task detail or foreground task |
| BACKGROUND | `K` (kill) | BACKGROUND | Confirm then send kill signal to selected task |
| BACKGROUND | `F` (foreground) | IDLE or ACTIVE | Move selected background task to foreground; attach stdin |
| BACKGROUND | `Escape` | prev state | Return to previous state; preserve background count badge |
| REWIND | Arrow keys | REWIND | Navigate checkpoint list |
| REWIND | `Enter` | IDLE | Apply selected checkpoint and restore |
| REWIND | `Escape` | prev state | Dismiss rewind menu |
| VIEWER | Any keyboard input | VIEWER | Silently drop; no interrupt, no mutation |
| HEADLESS | Any event | HEADLESS | Process events; no UI callbacks |

## Invariants

- **Prompt buffer is preserved** across all overlay transitions (SEARCH, BACKGROUND, TEAMMATE, REWIND). The buffer must not be cleared when entering or exiting an overlay.
- **A single `Escape` in IDLE** is not an exit; it clears the draft prompt buffer. A single `Escape` in ACTIVE is an interrupt request, not a state transition.
- **Double `Esc Esc`** in IDLE or ACTIVE opens the rewind menu. This must not collide with single-escape behavior.
- **VIEWER state disables all mutating keybindings** unconditionally. The VIEWER → any mutation path must not exist in the state machine.
- **HEADLESS suppresses all terminal paint and interactive callbacks** but processes messages normally. Overlays must not leak into headless paths.
- **Interrupt in ACTIVE does not close overlays.** If the user opened BACKGROUND while the agent was running, an interrupt does not dismiss the background panel.
- **Background badge is additive** — it reflects the count of running/pending backgrounded tasks, not the BACKGROUND overlay state. The badge is visible in all non-VIEWER states.

## Mode-specific keybinding rules

### IDLE mode
- `Escape` — clear the draft prompt buffer
- `Esc Esc` — open REWIND
- `Ctrl+C` — clear the draft; it copies instead only when a text selection is active (renderers that support in-app selection)
- `Tab` — command/path completion

### ACTIVE mode
- `Escape` — send interrupt to agent; show "interrupting..." UI feedback
- `Ctrl+C` — same as Escape in ACTIVE
- `Ctrl+B` — open BACKGROUND without leaving ACTIVE
- Typing keeps editing the draft; `Enter` queues it as the next message and does not interrupt the running turn

### BACKGROUND mode
- `K` (kill), `F` (foreground), `D` (detail) below are **illustrative design keys for this pattern, not documented Claude Code shortcuts** — verify against your own runtime before presenting them as an existing product's bindings. Claude Code itself has no default per-item kill or foreground key on an individual background task; its real primitives are a global "background the current turn" action and a global "kill all background subagents" action (see [Vendor example](#vendor-example-one-clis-bindings)).
- `K` — kill selected task (requires confirmation dialog)
- `F` — foreground selected task
- `D` — show task detail pane
- `Escape` — close panel, return to previous state
- Arrow keys — navigate task list (do not also bind `K` or another action key to navigation; `K` is kill here)

### SEARCH mode
- All printable characters — update query
- Execute key vs fill key — whether `Enter` runs the recalled command or only places it in the prompt differs between products, and within one product can differ by renderer (inline vs fullscreen). Whichever key executes a recalled command must differ from the fill key, and the UI must show which key does which. A user who expects "fill" and gets "run" re-executes a command by accident.
- `Escape` — cancel and restore the prior buffer (unless it is the fill key in your design)
- `Arrow up/down` — navigate results
- A cycle-scope key (session → project → everywhere) is worth adding once history spans multiple projects — otherwise search silently misses relevant history from other repos.

### VIEWER mode (remote read-only)
- All keys are swallowed at the input layer
- Scroll events are forwarded to the virtual scroll component
- No keybinding to "take control" — that requires a protocol-level capability grant

## Vendor example: one CLI's bindings

The mode/keybinding pattern above is generic design guidance. What follows is one shipped CLI (Claude Code) as a worked example. Exact keys, contexts, and defaults change between releases: before claiming parity with any shipped CLI, read its current keybinding, status-line, and agent-teams docs.

- **Config file**: `~/.claude/keybindings.json`, an object with a `bindings` array; each block has a `context` (e.g. `Chat`, `Task`, `HistorySearch`, `Footer`, `MessageSelector`, `Transcript`, `Confirmation`) and a keystroke-to-action map. Actions are `namespace:action` (e.g. `chat:submit`, `task:background`). Set an action to `null` to unbind it; changes apply live, no restart.
- **Reserved, cannot be rebound**: `Ctrl+C` (interrupt), `Ctrl+D` (exit), `Ctrl+M` (identical to Enter in terminals), Caps Lock (never delivered to terminal apps).
- **Terminal-multiplexer conflicts to design around**: `Ctrl+B` is the tmux prefix (press twice to send through), `Ctrl+A` is the GNU screen prefix, `Ctrl+Z` suspends the process (SIGTSTP). Claude Code's own `task:background` default is `Ctrl+B`, which collides with tmux — that's why it ships a second chord, `Ctrl+X Ctrl+B`, specifically so tmux users have a conflict-free path. Any coding-agent TUI that binds a primary action to `Ctrl+B`, `Ctrl+A`, or `Ctrl+Z` needs a documented alternate chord, not just a footnote.
- **No granular per-task kill/foreground key exists in the shipped product.** The real primitives are global: `task:background` (send the current turn to background) and `chat:killAgents` (`Ctrl+X Ctrl+K`, stops *all* running background subagents at once). A design that needs per-item kill or foreground must build and name it explicitly — don't imply it already exists.
- **History search separates execute from fill**: distinct `historySearch:execute` and `historySearch:accept` actions exist, and which physical key maps to each depends on the renderer; `historySearch:cycleScope` cycles session → project → everywhere. Check the current docs for the key mapping in the renderer you target.
- **Agent Teams navigation** (in-process mode): Up/Down arrows select a teammate in the agent panel, Enter opens its transcript and lets you message it directly, Escape clears the selection in the panel and interrupts the teammate's current turn only while you are viewing its transcript, `x` stops a selected teammate, Ctrl+T toggles the task list. There is no Shift+Up/Down teammate-navigation binding — Shift+Up/Down is `messageSelector:top`/`messageSelector:bottom` (jump to top/bottom of a message list), a different context entirely. When more than three teammates are idle, the surplus collapses into one "N idle agents" row; Enter expands it.
- **Display mode is a capability to detect, not assume.** Split-pane mode requires a supported multiplexer or terminal (tmux, or iTerm2 with its CLI) and is unavailable in several common terminals (for example VS Code's integrated terminal). Detect split-pane capability and default to the in-process display, which works everywhere.

## Input ownership rules

The REPL owns the terminal's raw input mode. Overlays receive synthetic key events forwarded by the REPL; they must not call `raw_mode()` or `cooked_mode()` independently.

```
Terminal (raw mode) → REPL input loop → dispatch by current state
                                       ├── IDLE     → prompt buffer / submit
                                       ├── ACTIVE   → interrupt or buffer
                                       ├── SEARCH   → search overlay handler
                                       ├── BACKGROUND → task panel handler
                                       ├── TEAMMATE → teammate panel handler
                                       ├── REWIND   → checkpoint menu handler
                                       ├── VIEWER   → drop
                                       └── HEADLESS → drop
```

## Failure modes

- **Escape ambiguity**: registering `Esc` and `Esc Esc` as separate bindings requires a debounce timer. Without it, a double-escape always fires the single-escape handler first and the double-escape never triggers. Use a 100–150ms debounce window.
- **Overlay entered while ACTIVE**: if the user opens BACKGROUND during an active turn and the turn completes while BACKGROUND is open, the state machine must transition to `BACKGROUND` (not to `IDLE`) and the prompt buffer must be restored when BACKGROUND closes.
- **Viewer mode leaking interrupt path**: a remote attach that changes state to VIEWER must also replace the keybinding dispatch table. Switching state but not keybindings creates a path where `Escape` still sends an interrupt.
- **Headless affordances in interactive code paths**: any component that renders an overlay, registers a timer, or calls `crossterm::enable_raw_mode` must be gated on `is_interactive()`. Otherwise headless sessions throw terminal errors on startup.

## Related

- [`repl-message-input-and-history.md`](repl-message-input-and-history.md) — REPL ownership, prompt queue, and interrupt semantics
- [`background-work-notifications-and-virtualization.md`](background-work-notifications-and-virtualization.md) — Background-task navigation and notifications
- [`recipe-toolsearch-render.md`](recipe-toolsearch-render.md) — How ToolSearch deferred-tool results render in the REPL
