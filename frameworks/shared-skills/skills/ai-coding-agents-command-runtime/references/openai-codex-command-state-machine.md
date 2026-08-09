# OpenAI Codex Command State Machine

Source snapshot: OpenAI Codex commit `7d47056ea42636271ac020b86347fbbef49490aa` (2026-05-22), especially `codex-rs/tui/src/slash_command.rs`.

## Table Of Contents

- [Design Goal](#design-goal)
- [Command Metadata](#command-metadata)
- [Availability Predicates](#availability-predicates)
- [Presentation Order](#presentation-order)
- [Runtime Tests](#runtime-tests)

## Design Goal

Slash commands are not just strings mapped to handlers. Codex treats them as a typed command set with user-visible descriptions and state-dependent availability. Copy the state machine, not just the command names.

## Command Metadata

A useful command contract includes:

- canonical command string
- aliases or alternate serialized names
- user-visible description
- whether inline arguments are supported
- whether the command is visible on this platform or build

Keep these fields close to the enum or registry entry so completion menus, help text, and dispatch cannot drift.

## Availability Predicates

Codex separates at least two availability questions:

- **available during active task**: commands such as status, diff, copy, background process listing, and feedback can run while the agent is working; commands that reconfigure session state usually cannot.
- **available in side conversation**: only a smaller subset of read/render/context commands remains available inside an ephemeral side thread.

Use explicit predicates for these states. Do not encode them as ad hoc UI checks in the command handler.

## Presentation Order

The built-in command enum is intentionally not alphabetized because enum order controls popup order. High-frequency commands appear earlier.

For runtime builders:

- make command order a deliberate UX contract
- document whether order is usage-ranked, fixed, or grouped by category
- test order if users rely on keyboard navigation

## Runtime Tests

Codex's implementation suggests a compact command test matrix:

- parsing canonical names and aliases
- all visible commands have descriptions
- inline-arg support matches dispatcher behavior
- commands blocked during task do not run through alternate UI paths
- side conversations cannot run commands that mutate parent session state

## Traps

- Letting individual handlers decide whether they are safe during active execution.
- Alphabetizing command enums when enum order feeds the picker.
- Supporting inline args in parsing but not in handler tests.
- Forgetting platform-specific visibility rules.
