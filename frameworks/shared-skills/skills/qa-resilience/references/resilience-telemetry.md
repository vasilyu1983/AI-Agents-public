# Resilience Telemetry

Use this reference to define the minimum telemetry contract for retries, timeouts, breakers, degraded mode, overload, and resilience tests.

## Required Outcomes

An operator should be able to answer:

- what failed
- where it failed
- whether the failure was retried, hedged, shed, degraded, or short-circuited
- whether the system recovered automatically
- how much user impact occurred

## Minimum Signals

### Metrics

- request rate, error rate, latency, saturation
- retry count and retry budget exhaustion
- hedging attempt count and hedge win rate
- circuit breaker open / half-open / closed transitions
- endpoint ejection count and duration
- concurrency limit value and shed / reject volume
- degraded-mode activation rate and degraded duration
- recovery time after dependency restoration

### Traces

Capture per span or request when possible:

- dependency name
- timeout or deadline info
- retry count
- hedge count
- final outcome
- error type
- degraded marker if fallback was used

### Logs

Include structured fields:

- correlation ID or trace ID
- dependency / route name
- policy layer that acted (app, client, mesh, gateway)
- breaker state
- retry or hedge count
- shed / reject reason
- fallback reason

## Naming Guidance

Prefer vendor-neutral naming that maps cleanly to OpenTelemetry semantics when available.

Useful attributes and concepts:

- `error.type`
- `server.address`
- `server.port`
- request method / route
- resend or retry count when the transport or client exposes it
- explicit degraded-state marker

Do not rely only on free-text log messages for resilience assertions.

## Test Assertions

A resilience test should assert both behavior and telemetry:

- timeout occurred within budget
- retry count stayed within budget
- no duplicate side effects happened
- breaker or ejection happened when expected
- overload resulted in bounded rejection rather than runaway latency
- degraded mode was visible in telemetry and ended after recovery

## Dashboards And Alerts

Track:

- multi-window burn-rate alerts
- p95 / p99 by dependency and route
- fallback and degraded-mode duration
- retries per request and total retry volume
- shed rate and queue depth
- breaker state changes and host ejections

## Related Resources

- [../../qa-observability/SKILL.md](../../qa-observability/SKILL.md) - Broader observability patterns
- [retry-patterns.md](retry-patterns.md) - Retry signals
- [graceful-degradation.md](graceful-degradation.md) - Degraded-state behavior
- [gateway-mesh-resilience.md](gateway-mesh-resilience.md) - Shared enforcement layers
