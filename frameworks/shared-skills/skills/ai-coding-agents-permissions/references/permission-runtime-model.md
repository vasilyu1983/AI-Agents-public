# Permission Runtime Model

## Table Of Contents

- [Design Goal](#design-goal)
- [Central Permission Context](#central-permission-context)
- [Mode Handling](#mode-handling)
- [Tool vs Host Responsibility](#tool-vs-host-responsibility)
- [Promptability Rules](#promptability-rules)

## Design Goal

Coding-agent runtimes need one host-owned permission model that stays consistent across tools, sessions, and execution topologies. Do not let each tool invent its own approval semantics.

The `claude_code` source makes this explicit through `ToolPermissionContext` in `Tool.ts`.

## Central Permission Context

`ToolPermissionContext` holds the approval state for a running session:

- `mode`
- allow, deny, and ask rules by source
- additional working directories
- bypass and auto-mode availability
- stripped dangerous rules
- background-agent promptability flags
- a `prePlanMode` field so plan-mode transitions can restore the prior mode

That is the correct model to copy:

- keep one canonical permission object
- let multiple runtime layers read it
- update it in place through host-owned transitions

## Mode Handling

The source shows that plan mode is not just a UI state. It is part of permission control:

- the runtime stores the pre-plan permission mode
- model-initiated plan-mode entry can temporarily change behavior
- exit restores the previous mode instead of guessing

Use the same rule:

- permission mode transitions should be explicit and reversible
- plan mode should not permanently corrupt ordinary approval state

## Tool vs Host Responsibility

The host owns:

- rule precedence
- allow/deny/ask semantics
- when prompts are shown
- whether a request can be delegated or auto-denied

Tools can still contribute:

- human-readable request text
- tool-specific input rendering
- tool-specific validation of whether approval is needed

Do not let tools store the final approval policy themselves.

## Promptability Rules

`Tool.ts` also captures a critical distinction:

- some contexts should avoid prompts entirely
- some contexts should await automated checks before showing a dialog

Those two flags matter for production coding agents:

- background workers cannot safely block forever on a UI they do not control
- coordinator workers may need classifier or hook output before a final dialog is shown

Treat “can prompt the user” as a first-class runtime capability, not an assumption.

## Edge Cases And Workarounds

Production permission systems need a few more rules than the high-level model suggests:

- over-broad shell or Bash allow rules
  - sanitize or strip them after loading from disk
  - do not trust user-edited permission rules to be safe just because they parsed
- bypass mode availability
  - represent "bypass exists" separately from "bypass is currently allowed"
  - policy or runtime state may disable bypass without removing the field from the model
- background workers
  - if they cannot render approval UI, auto-deny or route the request to a controller
  - do not leave them waiting forever on a prompt no one can see
- plan-mode entry and exit
  - store the pre-plan mode explicitly
  - exiting plan mode should restore, not recompute, the old mode
- automated checks before dialog
  - if approval depends on hooks or classifiers, record that the dialog is intentionally delayed

Practical rule:

- keep the permission object small enough to reason about
- put every weird approval branch behind explicit booleans or enums
- avoid hidden behavior inferred from UI state alone
