# OpenAI Codex Session Task Turn Protocol

Source snapshot: OpenAI Codex commit `7d47056ea42636271ac020b86347fbbef49490aa` (2026-05-22), especially `codex-rs/docs/protocol_v1.md` and `codex-rs/protocol/src/protocol.rs`.

## Table Of Contents

- [Design Goal](#design-goal)
- [Vocabulary To Reuse](#vocabulary-to-reuse)
- [Queue Contract](#queue-contract)
- [Resume And Fork Bookmarks](#resume-and-fork-bookmarks)
- [Interruption Rules](#interruption-rules)

## Design Goal

Use Codex's protocol vocabulary when designing a coding-agent runtime that must be driven by more than one UI. The important idea is the boundary: UI clients submit operations, the core owns session and task state, and events stream back over a stable protocol.

## Vocabulary To Reuse

Codex separates:

- **Session**: current configuration plus persistent runtime state.
- **Task**: the agent doing work in response to user input.
- **Turn**: one model request plus any tool execution and follow-up output.

Copy this split when writing runtime docs. It avoids overloaded terms like "conversation" for both the saved thread and the currently running work.

## Queue Contract

Codex models the core protocol as submission and event queues:

- UI -> core: `Submission` with a UI-provided correlation ID and an `Op`.
- core -> UI: `Event` with matching correlation information and an `EventMsg`.
- Transport can be channels, IPC, stdio, TCP, HTTP/2, or gRPC.
- Non-framed transports should use newline-delimited JSON.

For new runtimes, this gives a clean test seam: record submitted ops, assert emitted events, and keep UI rendering out of core behavior tests.

## Resume And Fork Bookmarks

Each completed turn can return a model `response_id`. The UI can store that bookmark and pass it into later input to continue or fork from a previous point.

Design implication:

- transcript replay and provider-native response continuation are different restore paths
- store both the human-readable rollout and the provider bookmark when available
- make fork explicit so users can tell whether they continued the current task or branched from a prior turn

## Interruption Rules

Codex's protocol makes interruption host-owned:

- a session has at most one active task
- a new user turn or explicit interrupt aborts the current task
- reconfiguration aborts running execution
- a task can also pause on approval or fatal provider/runtime errors

Copy this as an invariant. Parallel work should be separate sessions or separate agent instances, not hidden concurrent tasks inside one session.

## Traps

- Treating `Session` as the same thing as a task queue.
- Letting a UI mutate core state without an operation/event audit trail.
- Resuming only from transcript text when a provider-native response bookmark exists.
- Allowing multiple active tasks in one session without explicit cancellation semantics.
