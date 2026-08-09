# Collaboration Patterns

Use this file when the request is about presence, sync, or collaborative editing.

## Presence

- Separate ephemeral presence from durable document state.
- Throttle high-frequency updates like cursor movement.
- Define offline and reconnect semantics explicitly.

## Shared State

- Prefer CRDTs for new collaborative editors unless a centralized OT system is already established.
- Persist periodic snapshots or compacted state for recovery.
- Keep user intent and system events distinguishable in the protocol.

## Recovery

- Replays must be idempotent.
- Detect duplicate messages by ID.
- Treat reconnect and deploy events as first-class flows, not edge cases.
