# Topic Contract Template

Use this template when defining a new streaming topic or formalizing an existing one.

## Topic Identity

- Topic name:
- Owning team:
- Business purpose:
- Producer systems:
- Consumer systems:

## Delivery Contract

- Event type or topic family:
- Key field:
- Ordering guarantee:
- Retention policy:
- Compaction enabled:
- Replay expectation:

## Schema Contract

- Serialization format:
- Registry or schema store:
- Compatibility mode:
- Required fields:
- Delete semantics:
- Deprecation window:

## Operational Contract

- Target throughput:
- Target end-to-end latency:
- Critical alerts:
- Lag threshold:
- Backfill or replay owner:
- Incident escalation path:

## Notes

- Lock down names, keys, retention, and delete handling before launch.
- If the topic is shared across teams, require an owner and schema review path.
