# Gateway And Mesh Resilience

Use this reference when resilience policy may belong in a gateway, service mesh, or shared client layer rather than in application code.

## Put Policies In The Mesh Or Gateway When

- the rule should apply consistently across many services
- the backend pool has many interchangeable instances
- you need endpoint ejection or passive health based on observed traffic
- you need shared rate limiting, concurrency limits, or traffic shaping

## Keep Policies In Application Code When

- fallback behavior depends on business semantics
- idempotency decisions are per operation
- degraded responses require domain-specific payload changes
- callers need per-request policy overrides based on business context

## Core Controls

### Outlier Detection

Use when a backend pool is mostly healthy but one or more endpoints are bad.

Expected behavior:

- observe local error or latency signals
- eject unhealthy hosts conservatively
- reintroduce hosts after a cooldown and successful probes
- emit ejection events for debugging

Good fit:

- bad pod or instance
- one AZ with partial degradation
- noisy neighbor effects on a subset of hosts

Poor fit:

- dependency-wide outage
- business-logic errors that every host returns consistently

### Adaptive Concurrency

Use when latency rises under load and the system needs to bound in-flight work.

Expected behavior:

- adjust allowed concurrency from measured latency
- reject or queue less work before collapse
- protect the dependency and upstream callers from saturation feedback loops

Guardrails:

- bound queues even if concurrency is adaptive
- instrument shed volume and rejected work
- pair with deadlines and fallback behavior

### Shared Retry / Timeout Policy

Use a shared layer only if one team clearly owns it and callers know it exists.

Rules:

- do not let gateway retries multiply with app retries
- keep per-route policy visible and documented
- do not retry unsafe methods by default
- propagate remaining deadlines, not fresh timeouts

## Testing Matrix

Validate separately:

- one-host bad in a pool
- 10-20% intermittent failures
- dependency-wide 5xx incident
- latency inflation without errors
- overload where rejections are preferable to latency collapse

## Telemetry Checklist

- [ ] endpoint ejection count and duration
- [ ] concurrency limit value over time
- [ ] shed / reject count and rate
- [ ] retry volume by enforcement layer
- [ ] route-level timeout count
- [ ] degraded-mode activation when shared policy trips

## Related Resources

- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) - App-level breaker logic
- [load-shedding-backpressure.md](load-shedding-backpressure.md) - Overload patterns
- [deadlines-hedging.md](deadlines-hedging.md) - Deadline and hedging choices
- [resilience-telemetry.md](resilience-telemetry.md) - Shared metrics and tracing fields
