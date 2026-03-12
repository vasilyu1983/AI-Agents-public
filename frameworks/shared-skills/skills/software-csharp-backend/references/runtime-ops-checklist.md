# Runtime Ops Checklist

## Startup and configuration
- Validate critical options at startup and fail fast on invalid config.
- Keep secrets out of source control; load from environment/secret manager.
- Separate functional config from security-sensitive config.
- Keep environment-specific defaults explicit and documented.

## Logging and tracing
- Use structured logs with stable keys for service, operation, and correlation identifiers.
- Propagate trace context across HTTP, messaging, and background execution.
- Redact secrets and regulated fields from logs, traces, and exception payloads.
- Add request/operation scope fields to support incident triage.

## Metrics and health
- Emit request/error/retry counters and latency histograms for critical flows.
- Expose liveness and readiness endpoints with clear dependency semantics.
- Track dependency health and pool saturation for outbound clients/workers.
- Align alerts to user-facing symptoms and actionable thresholds.

## Caching defaults
- Use cache only for read paths with clear invalidation ownership.
- Prefer tag/key-scoped invalidation over broad cache flush.
- Define TTL and staleness behavior explicitly per cache entry category.
- Guard against cache stampede and dependency outage fallback behavior.

## Resilience defaults
- Set explicit timeout on every outbound dependency call.
- Retry only transient failures with bounded backoff and jitter.
- Add circuit breaker and concurrency limits for unstable/slow dependencies.
- Require idempotency guarantees before retrying writes.

## Deployment and runtime hardening
- Use non-root container images and minimal runtime footprint.
- Configure graceful shutdown timeout and verify drain behavior in tests.
- Keep readiness false during migration/startup windows that cannot serve traffic.
- Gate rollout with smoke checks for health, error rate, and latency regression.

## Operational readiness questions
- Can an operator identify failing dependency and impact within minutes?
- Can the service restart safely without manual cleanup?
- Are failure modes documented for degraded dependency behavior?
