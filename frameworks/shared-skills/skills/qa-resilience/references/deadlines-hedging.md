# Deadlines And Hedging

Use this reference when the main problem is tail latency, retry amplification, or unclear deadline ownership.

## Core Rules

- Every request path needs an overall deadline.
- Each hop consumes part of that budget and propagates the remainder downstream.
- Retry and hedging decisions must respect the remaining deadline, not a fresh timeout.
- Hedging is for idempotent or safely cancellable operations only.
- Prefer ordinary retries for transient failures; prefer hedging only when p99 is dominated by stragglers, not widespread failure.

## Deadline Budgeting

Starting point:

- User-facing request: 1 end-to-end deadline
- Per-hop budgets derived from that deadline
- DB and pool wait timeouts bounded inside the same budget
- On timeout, fail fast and cancel downstream work

Checklist:

- [ ] End-to-end deadline defined per journey
- [ ] Remaining deadline propagated to downstream calls
- [ ] Per-try timeouts do not exceed remaining budget
- [ ] Queue wait time and DB statement timeout are bounded
- [ ] Timeout errors are visible in metrics, logs, and traces

## Retry Vs Hedging

Use retry when:

- failure is transient
- a later attempt is likely to succeed
- extra load is acceptable
- the operation is safe to repeat

Use hedging when:

- a dependency is usually healthy
- p99 is driven by a small fraction of slow requests
- you can send a parallel attempt without duplicate side effects
- you can cancel losing attempts promptly

Do not hedge when:

- the operation mutates state
- the downstream cannot cancel promptly
- the system is already overloaded
- one user request could fan out into many expensive subrequests

## Hedging Guardrails

- Hedge only safe reads or explicitly idempotent operations.
- Start with one additional attempt, not broad fanout.
- Delay the hedge slightly; do not duplicate immediately unless the transport policy requires it.
- Cancel or ignore losing attempts as soon as a winner is chosen.
- Instrument hedge count, winner/loser ratio, added load, and p99 improvement.
- Disable hedging automatically during brownouts or overload incidents.

## Example Decision Table

| Situation | Preferred Control |
|-----------|-------------------|
| 429 / 503 with Retry-After | Retry with jitter, honor server guidance |
| One-off connection reset | Retry if deadline and idempotency allow |
| High p99 with low error rate | Small hedging trial on reads |
| Dependency-wide incident | Breaker or outlier controls, not hedging |
| Overloaded dependency | Concurrency limit and load shedding, not hedging |

## Telemetry

Capture:

- total deadline
- remaining deadline
- timeout cause and layer
- retry count
- hedge attempt count
- hedge winner/loser count
- added request volume from hedging

## Related Resources

- [retry-patterns.md](retry-patterns.md) - Retry budgets and backoff
- [timeout-policies.md](timeout-policies.md) - Per-hop timeout structure
- [gateway-mesh-resilience.md](gateway-mesh-resilience.md) - Shared policy controls
- [resilience-telemetry.md](resilience-telemetry.md) - What to emit during tests
