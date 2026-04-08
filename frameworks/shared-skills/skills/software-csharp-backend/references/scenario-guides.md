# Scenario Guides

## High-throughput HTTP APIs
- Use request-thin handlers and keep per-request allocations low.
- Use keyset pagination for hot list endpoints.
- Batch dependent reads and avoid per-item downstream calls.
- Set strict timeout budgets and bounded retries for every outbound dependency.
- Prefer asynchronous pipelines and avoid blocking sync-over-async.

## Event-driven workers
- Make consumers idempotent by business key or explicit idempotency key.
- Keep handlers resumable with checkpointing for long workflows.
- Separate poison/dead-letter handling from transient retry paths.
- Include operation IDs and message metadata in logs/traces.
- Verify duplicate and out-of-order delivery behavior in tests.
- Classify non-retryable exceptions before entering generic retry logic, not inside it. A `KafkaNonRetryableException` that flows through the retry loop repeats side effects and violates operator expectations.
- Treat cancellation as control flow, not failure handling. `OperationCanceledException` must exit the consumer loop before failure routing kicks in. Treating shutdown as a processing failure can incorrectly commit messages, route them to retry/DLQ, or pause partitions during normal host stop.
- Isolate failure-routing failures to the affected partition. A retry/DLQ publish failure should pause only that partition, not kill the whole consumer task or sleep the entire loop. Produce visible host-level faulting instead of leaving a dead background task behind.
- Treat retry/DLQ adoption as a contract change: switching from "commit in finally" to "commit only after success or retry/DLQ publish" changes runtime semantics even if public APIs stay the same. New behavior must be explicitly opt-in.
- Add regression coverage for legacy consumer behaviors (shared fan-out, custom `IMessageSubscription`) whenever core consumer internals change. New failure-handling modes are not safe if they break older extension points.

## Multi-tenant services
- Resolve tenant context at boundary and propagate through all layers.
- Enforce tenant isolation in query filters and cache keys.
- Keep per-tenant limits and quotas configurable.
- Ensure telemetry includes tenant identifiers only when policy allows.
- Validate data migration and backfill plans for tenant-scoped schema changes.

## Selection checklist
- If latency and p99 are dominant constraints, use the high-throughput profile.
- If replay/retry/ordering dominate, use the event-driven profile.
- If isolation and tenant policy dominate, use the multi-tenant profile.
