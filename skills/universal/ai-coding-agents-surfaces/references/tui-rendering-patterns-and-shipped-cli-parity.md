# TUI Framework Selection, Rendering Patterns, and Shipped-CLI Parity

Moved from the former terminal-ui skill. The internal-runtime patterns (REPL ownership, background-task navigation model, virtual-scroll approach) are illustrative design guidance, not documented product behavior; label them as such when presenting to a reader who might mistake them for a shipped feature.

## TUI Framework Selection

Use the TUI framework native to your runtime's language, and one framework per surface. Mixing two TUI frameworks in one surface doubles the layout and input models you must keep consistent. Framework versions, performance ceilings, and which products use which framework change quickly; check current framework docs and benchmark in your target terminal before treating any limit as hard.

## Cross-Platform Patterns

### Fixed-grid, no-overflow rendering

Some terminal renderers have **no overflow clipping**: content wider than its container visually corrupts the frame, with no scroll-to-reveal. Design as if yours is one of them and pre-truncate all content to its container's character dimensions before emitting it.

- **Pattern:** treat container dimensions as a hard input to rendering. Message blocks compute their truncation *before* the renderer sees them. Resize events are first-class and trigger re-layout at the content level, not just the terminal repaint level.
- **Anti-pattern:** relying on terminal scroll or native overflow to handle long lines. This works by accident in some terminals and corrupts output in others. Long provider responses, wide diffs, and tool output are the main offenders.
- **Recipe:** every message component accepts `(max_cols, max_rows)` and returns pre-truncated content plus an "expand" affordance that opens a separate dialog/pager. The REPL state machine tracks which messages are collapsed-due-to-space vs. collapsed-by-user.

### Dual-surface invariant (CLI + desktop, shared protocol)

CLI and GUI clients share one protocol contract; rendering may differ. A desktop UI should be a client of the same typed daemon or ACP server as the CLI (see `ai-coding-agents-surfaces` for the daemon pattern), so message blocks, keybindings, tool results, and interrupt semantics are defined at the protocol level, not the rendering layer.

- **Pattern:** design components against the smaller surface (CLI) first. Desktop adds window management, copy/paste affordances, and native GUI controls, but the message model is identical.
- **Anti-pattern:** maintaining parallel message components for "CLI" and "desktop." This produces visual drift, divergent keybindings, and features that exist in one surface but not the other.
- **Recipe:** one component library renders both surfaces. The desktop shell provides hooks for native affordances (file drag-and-drop, OS notifications) but never replaces the core render pipeline.

## Shipped-CLI Parity: Status Lines, Keybindings, Agent Teams

Before claiming parity with a shipped CLI, read its current keybinding, status-line, and agent-teams docs. The dominant failure mode in this space is presenting a plausible-sounding key or field as fact when it does not exist in the shipped product. [`references/input-state-machine.md`](input-state-machine.md#vendor-example-one-clis-bindings) has one CLI's bindings as a worked example. Traps that generalize:

**Status line.** A status line driven by a user-supplied command renders a snapshot passed in on stdin and prints text; it does not own state.
- The command's stdout is captured, not connected to the real terminal, so `tput cols` and other terminal-size probes return nothing inside the script. Read the terminal-size values the host passes in (environment variables or the input payload; check its docs). Any status-line design that assumes direct TTY access from a subprocess will silently misrender width.
- Updates are event-driven and debounced; a script still running when a new trigger fires gets cancelled. Use a periodic refresh only for genuinely time-based segments (a clock, cost drift) — polling for no reason burns a process every interval even when nothing changed.
- The status line can be hidden during autocomplete, help, and permission prompts — do not design it as the only place transient status can live.

**Keybindings.**
- Some keys are reserved by the host or the terminal and cannot be rebound (interrupt, exit, and keys a terminal cannot distinguish from Enter). Check the host's reserved-key list.
- Any `Ctrl+B`, `Ctrl+A`, or `Ctrl+Z` binding ships a multiplexer-safe alternate chord: those are the tmux prefix, the GNU screen prefix, and suspend.
- Do not assume a granular per-task kill or foreground shortcut exists in a shipped CLI; its real primitives may be global (background the current turn, stop all background agents). If your design needs per-item actions, build them and document them as new, not "standard."
- History recall separates execute from fill: whichever key executes a recalled command must differ from the fill key, and the UI must show which is which. Which physical key does which varies by product and renderer, so never assume `Enter` only pastes.

**Agent Teams display modes.** Detect split-pane capability (it needs a supported multiplexer or terminal) and default to in-process teammate display, which works everywhere. Treat split-pane availability as a runtime capability to detect, not a default to assume. Teammate-navigation keys in the references are illustrative design guidance unless a shipped CLI's docs say otherwise.
