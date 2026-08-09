# Command Dispatch, Forking, And Remote Safety

## Table Of Contents

- [Lazy Dispatch](#lazy-dispatch)
- [Prompt Commands As Agent Orchestration](#prompt-commands-as-agent-orchestration)
- [Forked Command Execution](#forked-command-execution)
- [Immediate vs Queued Commands](#immediate-vs-queued-commands)
- [Remote-Safe vs Bridge-Safe](#remote-safe-vs-bridge-safe)
- [Help And Typeahead Formatting](#help-and-typeahead-formatting)
- [Failure Handling](#failure-handling)
- [Design Rules To Reuse](#design-rules-to-reuse)

## Lazy Dispatch

The `claude_code` runtime lazy-loads many command implementations:

- `local` commands load a module that returns a text result
- `local-jsx` commands load a module that renders interactive UI
- prompt commands stay declarative and usually do not need a heavy loader

Keep this pattern:

- registry metadata is cheap and always available
- heavy UI or optional dependencies load only on invocation
- command lists remain fast to assemble

## Prompt Commands As Agent Orchestration

`types/command.ts` gives prompt commands extra fields:

- `allowedTools`
- `hooks`
- `skillRoot`
- `context`
  - `inline`
  - `fork`
- `agent`
- `effort`
- `paths`

This is a strong pattern for coding-agent CLIs:

- prompt commands are not just text macros
- they can define a bounded subagent execution contract
- they can pick an agent type and constrain tools

## Forked Command Execution

`utils/forkedAgent.ts` shows the reusable fork model:

- preserve cache-critical parameters from the parent
- clone mutable state that should not leak back into the main loop
- inject allowed tools into a modified permission context
- choose an agent type explicitly
- record sidechain transcripts unless the work is intentionally ephemeral

The key pattern:

- forked commands should inherit cache-safe context
- they should not inherit the full mutable parent state
- they should get an explicit allowed-tools envelope

### Activation surfaces (Claude Code)

Confirmed against current Claude Code product docs (`/en/sub-agents`, "Fork the current conversation"; re-check before relying on exact version gates, since these move fast):

- `/fork <directive>` — the on-demand slash command. Enabled by default from v2.1.161; on earlier versions (from v2.1.117) it requires `CLAUDE_CODE_FORK_SUBAGENT=1`. Claude Code names the fork from the first words of the directive, and the fork runs in a panel below the prompt while you keep working in the main session.
- `CLAUDE_CODE_FORK_SUBAGENT` — env var honored in interactive mode, headless mode, and the Agent SDK. Set to `1` to force-enable fork mode (including letting the model itself request the `fork` subagent type), set to `0` to force-disable it everywhere, including any staged server-side rollout. Letting the model spawn forks on its own (rather than the user typing `/fork`) is still experimental.

Two behaviors worth designing for explicitly, not folding into generic subagent handling:

- **Forks cannot spawn forks.** A fork can spawn other (named) subagent types, and those count toward the normal depth limit, but forking is depth-limited to one level. Model this as a property of the `fork` command kind, not a generic recursion guard.
- **Enabling fork mode changes background-execution semantics globally.** Once fork mode is on, *every* subagent spawn — fork or named — runs in the background by default (the per-command `background` frontmatter field stops applying), unless `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS=1` overrides it back to synchronous. Treat this as a mode-level toggle, not a per-command flag, when you replicate the design.

Because a fork's system prompt and tool definitions are identical to the parent's at spawn time, its first request reuses the parent's prompt cache — official docs confirm this makes forking cheaper than a fresh subagent spawn but do not commit to a specific multiplier; treat any "Nx cheaper" figure you see in blog posts as anecdotal until you've measured it on your own token accounting. Tool calls remain isolated; only the final result returns to the parent's conversation, though the fork can also be given `isolation: "worktree"` so its file edits land in a separate git worktree instead of the parent's checkout. See [`../../ai-coding-agents-sessions/references/context-forking.md`](../../ai-coding-agents-sessions/references/context-forking.md) for session-lifecycle implications and `agents-subagents` §"Forking Parent Context Into Subagents" for design-side rules.

## Immediate vs Queued Commands

The command model supports `immediate`.

Use it sparingly for commands that must bypass the normal queue:

- mode toggles
- runtime controls
- plugin or settings reload
- short management flows

Most commands should remain queued so command ordering and user expectations stay stable.

## Remote-Safe vs Bridge-Safe

The repo distinguishes:

- `REMOTE_SAFE_COMMANDS`
  - commands safe in remote REPL mode
- `BRIDGE_SAFE_COMMANDS`
  - commands safe when invoked over a remote-control bridge

And it keeps one helper:

- `isBridgeSafeCommand()`

Important pattern:

- remote-safe is not the same as bridge-safe
- local JSX or TUI commands should be blocked by default in remote bridge contexts
- prompt commands are safer because they expand to model text instead of local UI

Typical implementation split:

- remote-safe
  - local commands that still make sense when the whole REPL is already in remote mode
  - often session-management or lightweight informational commands
- bridge-safe
  - commands safe to invoke from a thin mobile or web controller over a bridge
  - must not require local Ink rendering or terminal-only side effects

If you collapse these into one allowlist, you usually either over-expose terminal-only commands to bridge clients or under-expose harmless remote-session commands.

## Help And Typeahead Formatting

`formatDescriptionWithSource()` adds source-aware labels:

- plugin name when command came from a plugin
- bundled marker for bundled skills
- source labels for user or project settings

Keep this pattern when commands come from many sources:

- users need to know origin in interactive help
- models usually need the plain description
- use one formatter for user-facing listings, not ad hoc formatting across views

## Failure Handling

Good defaults from this runtime:

- skill and plugin command loading failures should degrade to empty lists, not crash the whole registry
- command resolution errors should enumerate the available names and aliases
- cache-clearing utilities should separate memoization invalidation from heavier source cache resets

Critical edge cases for a scratch rebuild:

- dynamic skill discovery adds commands after bootstrap
  - clear only command-index memoization first
  - clear heavier source caches only when the underlying source really changed
- plugin command load fails
  - keep the registry alive and mark the source degraded
  - do not make `/help` or typeahead disappear because one optional source broke
- alias collision between built-in and plugin command
  - document precedence and enforce deterministic resolution
- remote bridge invokes a `local-jsx` command
  - reject explicitly instead of trying to render partial terminal UI remotely
- prompt command without explicit description
  - decide whether it is hidden from model invocation, hidden from user help, or both

Useful workaround from the source shape:

- keep one cheap registry record that is always loadable
- move heavy behavior into lazy loaders
- keep a small set of explicit cache-clearing utilities rather than one global "reset everything" button

## Design Rules To Reuse

- Keep the registry cheap and loaders lazy.
- Treat forked prompt commands as constrained subagent launches.
- Separate remote-safe, bridge-safe, and terminal-only command paths.
- Make command origin visible in user-facing help.
- Fail soft on optional command sources; fail loud on bad dispatch.
