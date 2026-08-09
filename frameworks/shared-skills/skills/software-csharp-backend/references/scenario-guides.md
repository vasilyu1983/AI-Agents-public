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

## Multi-tenant services
- Resolve tenant context at boundary and propagate through all layers.
- Enforce tenant isolation in query filters and cache keys.
- Keep per-tenant limits and quotas configurable.
- Ensure telemetry includes tenant identifiers only when policy allows.
- Validate data migration and backfill plans for tenant-scoped schema changes.

## Distributed/cloud-native services
- Use Aspire service defaults only when the repository already embraces Aspire or needs opinionated distributed-service wiring.
- Keep service-specific auth, retry, timeout, and health behavior explicit even when a shared service-defaults package is present.
- Ensure telemetry names, resource attributes, and health probe semantics remain stable outside the Aspire local-dev environment.
- Treat local orchestration helpers as composition aids, not substitutes for runtime-hardening decisions.

## Selection checklist
- If latency and p99 are dominant constraints, use the high-throughput profile.
- If replay/retry/ordering dominate, use the event-driven profile.
- If isolation and tenant policy dominate, use the multi-tenant profile.
- If distributed composition and shared local-dev/runtime wiring dominate, use the distributed/cloud-native profile.
