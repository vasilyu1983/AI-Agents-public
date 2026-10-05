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

For relational app state with server-owned permissions and offline reads, evaluate a sync engine instead of encoding tables as a document CRDT:

| Engine | Sync unit | Authorization and write check |
|---|---|---|
| [Zero](https://zero.rocicorp.dev/docs/queries) | Query results replicated from Postgres | Server resolves named queries and filters by authenticated context; check mutators separately. |
| [Electric](https://electric.ax/docs/sync/guides/shapes) | Postgres shapes (selected rows/columns) | Serve shape requests through an authorization layer; inspect its write path separately. |
| [PowerSync](https://docs.powersync.com/sync/streams/overview) | Sync Streams into client SQLite | Authenticate subscriptions and define the upload/conflict path. Older Sync Rules are legacy. |

Check each engine's current feature and deployment docs before choosing. Document CRDTs still fit free-form concurrent editing; a sync engine does not replace an editor's merge algorithm.

## Recovery

- Replays must be idempotent.
- Detect duplicate messages by ID.
- Treat reconnect and deploy events as first-class flows, not edge cases.
