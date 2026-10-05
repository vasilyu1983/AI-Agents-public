# Deadlines And Hedging

Use this reference when the main problem is tail latency, retry amplification, or unclear deadline ownership.

## Contents

- [Core Rules](#core-rules)
- [Deadline Budgeting](#deadline-budgeting)
- [Server-Side Deadline Enforcement](#server-side-deadline-enforcement)
- [Deadline And Cancellation Propagation](#deadline-and-cancellation-propagation)
- [Bimodal Latency Is Worse Than Uniform Slowness](#bimodal-latency-is-worse-than-uniform-slowness)
- [Retry Vs Hedging](#retry-vs-hedging)
- [Hedging Guardrails](#hedging-guardrails)
- [Example Decision Table](#example-decision-table)
- [Telemetry](#telemetry)
- [Related Resources](#related-resources)

---

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

## Server-Side Deadline Enforcement

A deadline is not only a client-side give-up timer. The server must enforce it too, or it burns capacity on work nobody is waiting for. *Site Reliability Engineering*, Ch. 22 §"Missing deadlines" states the failure mode plainly: "A common theme in many cascading outages is that servers spend resources handling requests that will exceed their deadlines on the client. As a result, resources are spent while no progress is made: you don't get credit for late assignments with RPCs."

Rules:

- Check the **remaining** deadline at each processing stage, not just on arrival. The book's guidance: if a request splits into parsing, backend request, and processing stages, "check that there is enough time left to handle the request before each stage."
- Abandon work whose remaining budget cannot cover the next stage. Return a deadline-exceeded error rather than starting work that will be discarded.
- Exception worth keeping: a long, checkpointed catch-up operation should check the deadline *after* writing the checkpoint, not after the expensive step — otherwise the work is thrown away rather than banked.

## Deadline And Cancellation Propagation

Propagate the caller's remaining budget rather than inventing a fresh deadline per hop. With propagation, the whole RPC subtree shares one absolute deadline: a 30s deadline at server A, minus 7s of processing, becomes a 23s deadline on the call to B; B spends 4s and calls C with 19s.

Without it, a hardcoded downstream deadline lets a subtree keep working on a request its root already abandoned — SRE Ch. 22 §"Deadline propagation" walks the case where B ignores propagation and uses a hardcoded 20s deadline, so "server C processes the request thinking it has 15 seconds to spare, but is not doing useful work, since the request from server A to server B has already exceeded its deadline."

Practical notes from the same section:

- Trim the outgoing deadline slightly (a few hundred ms) for network transit and client-side post-processing.
- Consider an upper bound on outgoing deadlines to noncritical or normally-fast backends — but understand the traffic mix first, or large-payload and compute-heavy requests will fail every time.
- Deadline propagation alone leaks resources when a deep call fails fast but the root keeps waiting. **Cancellation propagation** fixes this: push fatal errors and timeouts up the stack and cancel the other in-flight RPCs in the call tree. Ch. 22 §"Cancellation propagation" also notes this is what makes hedging safe — once any server answers, the client cancels the now-superfluous requests, and those cancellations must propagate transitively through the whole fan-out.

## Bimodal Latency Is Worse Than Uniform Slowness

A mix of fast responses and deadline-length hangs is more dangerous than everything being uniformly slow, because the hung fraction parks threads and connections until the deadline expires. A small failing minority can therefore consume the pool and take down the healthy majority.

*Illustration, not a measurement* — the arithmetic below is SRE Ch. 22 §"Bimodal latency" worked as an example, not a figure observed in any system here. Given a frontend of 10 servers × 100 worker threads (1,000 threads), normally serving 1,000 QPS at 100 ms (≈100 threads busy): if an event makes 5% of requests never complete under a 100-second deadline, those 50 QPS demand 50 × 100 = 5,000 threads. The book concludes the frontend "will only be able to handle 19.6% of the requests (1,000 threads available / (5,000 + 95) threads' worth of work), resulting in an 80.4% error rate." The point is the shape, not the digits: a 5% fault became a near-total outage purely through pool occupancy.

Mitigations:

- Look at the latency **distribution**, not the mean — the book warns "it may not be clear that bimodal latency is the cause of an outage when you are looking at mean latency."
- Return errors early instead of waiting out the deadline. If a backend is known-unavailable, fail fast rather than holding the slot; use the RPC layer's fail-fast option where one exists.
- Do not set deadlines orders of magnitude above mean latency. In the example the deadline was three orders of magnitude above the normal mean, which is what converted a few slow requests into thread exhaustion.
- Cap in-flight requests per keyspace, tenant, or caller so one misbehaving client cannot occupy the whole pool (see [load-shedding-backpressure.md](load-shedding-backpressure.md)).

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
