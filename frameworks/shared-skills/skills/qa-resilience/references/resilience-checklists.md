# Resilience and Reliability Checklists (2026 Best Practices)

Use these checklists when hardening distributed systems against failures.

## Dependency Resilience
- Circuit breakers on all external dependencies with alerting on open/half-open states
- Timeouts per dependency (short, explicit, never infinite)
- Retries with exponential backoff + jitter; cap attempts to avoid storms; use per-try timeouts and a total deadline budget
- Bulkhead isolation for noisy neighbors (connection pools, worker pools, queuing)
- Idempotent handlers for retried operations; use request IDs for dedupe
- Fallbacks: cached data, stale reads, default responses, partial renders
- Backpressure and load shedding when latency or queue depth breach SLOs
- DR readiness: failover drills, backup/restore tests, and clear RPO/RTO targets (when applicable)

## Health and Readiness
- Liveness probes for process health; readiness probes for dependency health
- Startup probes for slow boot sequences
- Dependency contracts documented (SLO, timeout budget, error budget owner)
- Synthetic checks for critical user journeys, not only host-level checks
- Graceful shutdown hooks with in-flight request drains

## Observability for Resilience
- Golden signals tracked (latency, error rate, traffic, saturation)
- High-cardinality logs avoided; structured logging with correlation IDs
- Distributed tracing across service boundaries with clear service names
- Error budget burn alerts (multi-window, multi-burn-rate)
- Automated rollback triggers tied to SLO breaches

## Failure Testing
- Chaos experiments planned with blast radius limits and auto-revert
- Load tests cover peak + failover scenarios (zonal outage, dependency slowness)
- Game days scheduled with documented scenarios and owners
- Post-incident reviews with action items tracked to completion
