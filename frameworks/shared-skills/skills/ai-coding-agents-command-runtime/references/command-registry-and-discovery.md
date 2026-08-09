# Command Registry And Discovery

## Table Of Contents

- [Core Pattern](#core-pattern)
- [Useful Runtime Shape](#useful-runtime-shape)
- [Three Command Kinds](#three-command-kinds)
- [Registry Composition Order](#registry-composition-order)
- [Availability vs Enablement](#availability-vs-enablement)
- [Alias And Lookup Rules](#alias-and-lookup-rules)
- [Dynamic Skills](#dynamic-skills)
- [Design Rules To Reuse](#design-rules-to-reuse)

## Core Pattern

Model the slash-command layer as one typed registry that combines all command sources into a single runtime surface.

From the April 2026 `claude_code` snapshot:

- `commands.ts` is the central registry composition point
- commands share a single `Command` contract from `types/command.ts`
- command sources include built-ins, skills, plugins, bundled skills, workflows, MCP skills, and dynamic skills discovered during execution

## Useful Runtime Shape

Use one shared command type with:

- `name`
- optional `aliases`
- `description`
- `type`
  - `prompt`
  - `local`
  - `local-jsx`
- source metadata
  - built-in, skill, plugin, bundled, mcp, workflow, managed
- gating metadata
  - static availability
  - dynamic `isEnabled`
- UI metadata
  - argument hint
  - hidden or user-facing name
- execution metadata
  - immediate
  - sensitive
  - model-invocable or disabled-from-model

This keeps every source on the same dispatch rails while still allowing source-specific UI or policy treatment.

## Three Command Kinds

The repo uses a useful split:

- `prompt`
  - expands into model-visible content
  - often used for skills and workflow prompts
  - can carry allowed-tools, fork context, agent type, and hooks
- `local`
  - lazy-loaded text command
  - returns a compact structured result, not a full terminal UI
- `local-jsx`
  - lazy-loaded interactive TUI command
  - should not be treated as remote-safe by default

This split is better than a generic "command callback" because remote clients, model invocation, and bridge safety behave differently by command kind.

## Registry Composition Order

`commands.ts` composes sources in a deterministic order:

- bundled skills
- built-in plugin skills
- skill-directory commands
- workflow commands
- plugin commands
- plugin skills
- built-in commands

Then `getCommands()` applies:

- availability filtering
- dynamic `isEnabled` filtering
- insertion of dynamic skills before built-ins

Pattern to keep:

- load all sources into one canonical list
- apply auth and availability filters after load
- inject runtime-discovered commands in a deterministic slot
- keep memoized expensive loading separate from fast per-call gating

## Availability vs Enablement

The source separates:

- `availability`
  - auth or provider eligibility
  - who may ever use the command
- `isEnabled()`
  - current feature-flag, environment, or runtime state

Keep those separate in your own runtime.

Why:

- auth state can change mid-session
- feature flags and runtime conditions can vary independently
- mixing them creates brittle caches and inconsistent help or typeahead output

## Alias And Lookup Rules

Use:

- primary `name`
- optional `aliases`
- optional `userFacingName`

And keep one resolver that checks all three consistently.

This prevents drift between:

- help screens
- typeahead
- bridge dispatch
- error messages
- model-side references

## Dynamic Skills

The repo supports dynamic skills discovered after file operations and inserts them into the visible registry before built-ins.

Reusable pattern:

- keep dynamic discovery outside the static command bootstrap
- dedupe against existing names
- insert in a predictable place
- clear only the command memoization layers that depend on discovery

## Design Rules To Reuse

- One command contract, many sources.
- Keep loading memoized; keep auth and enablement fresh.
- Separate command kind from command source.
- Dedupe by stable names and aliases, not just file paths.
- Treat model-invocable commands as a stricter subset of the full registry.
