# REPL Message, Input, And History Model

## Table Of Contents

- [Design Goal](#design-goal)
- [REPL Ownership](#repl-ownership)
- [Prompt Input And Command Queue](#prompt-input-and-command-queue)
- [Interrupt Semantics](#interrupt-semantics)
- [Interactive-Only Boundaries](#interactive-only-boundaries)

## Design Goal

A coding-agent terminal UI should behave like a coherent session shell, not a loose collection of chat widgets. A reference coding-agent REPL shows that message history, input state, interrupts, and overlays need one host-owned interaction model.

## REPL Ownership

In the reference implementation, the top-level REPL screen owns:

- initial messages
- deferred hook messages
- interrupt handling
- rewind and search interactions
- remote interrupt bridging
- prompt visibility and disablement

That is the correct pattern: keep the conversation shell centralized instead of distributing session UX rules across many message-row components.

## Prompt Input And Command Queue

The reference command-queue store and prompt-input component show a useful split:

- a unified command queue lives outside the prompt component
- the prompt subscribes to queue state
- queue mutation changes references only when needed

Copy this:

- use a dedicated store for queued commands
- let prompt input preserve typed text through UI transitions
- keep queue semantics independent from transcript rendering

## Interrupt Semantics

The REPL and prompt-input code distinguish several interrupt-like actions:

- interrupt active work
- clear selection or exit teammate view
- remote interrupt forwarding
- idle escape behavior

Do not collapse them into one “Escape cancels” rule. Coding-agent terminals need explicit semantics per view and task state.

## Interactive-Only Boundaries

The reference tool contract and REPL screen make it clear that some behavior exists only in interactive mode:

- UI-only system messages
- interruptibility toggles
- overlays and dialogs
- OS notifications

Keep those boundaries explicit so the runtime does not assume a REPL exists in SDK or headless execution.
