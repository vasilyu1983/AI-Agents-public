# Mechanism: Circuit Breaker and Backpressure

**Sources**: Nygard, M. (2018), *Release It! Design and Deploy Production-Ready Software*, 2nd ed., Ch. 5. Brewer, E. (2000), "Towards Robust Distributed Systems" (Brewer's CAP theorem context). Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 7.

## Definition

Two complementary mechanisms for cascading-failure isolation in distributed systems:

**Circuit Breaker**: A stateful switch that monitors failure rate and interrupts the connection to a failing downstream service before it can overload the upstream caller.

```
States:
  CLOSED   → normal operation; requests flow through
  OPEN     → upstream is isolated; requests fail fast (no downstream call)
  HALF-OPEN → test probe: allow limited requests to check recovery

Transitions:
  CLOSED → OPEN:      failures exceed threshold (e.g., >50% in 60s window)
  OPEN → HALF-OPEN:   timeout elapsed (e.g., 30s); allow 1 probe request
  HALF-OPEN → CLOSED: probe succeeds → service recovered
  HALF-OPEN → OPEN:   probe fails → reset timeout
```

**Backpressure**: A feedback signal propagated upstream to slow down producers when downstream capacity is exhausted. Prevents queue buildup and cascading overload.

```
Producer → [Queue] → Consumer

Without backpressure:
  Queue grows unboundedly → memory exhaustion → system crash

With backpressure:
  Consumer signals "slow down" when queue length > threshold
  Producer reduces send rate (or blocks) until queue drains
  Feedback loop: queue length → send rate reduction
```

The two mechanisms compose: the circuit breaker isolates fully-failed components; backpressure throttles partially-loaded ones.

## When to Use

**Circuit Breaker**:
- Service dependency that fails intermittently under load.
- Prevent retry storm amplifying a partial failure into full outage.
- Any synchronous RPC call to an external service.
- Agent tool calls to external APIs — wrap each tool with a circuit breaker.

**Backpressure**:
- Producer-consumer pipelines (message queues, streaming systems, agent-to-tool pipelines).
- Anywhere a queue can grow unboundedly.
- Rate-limiting at ingress when downstream capacity is finite.

## Inputs

| Input | Circuit Breaker | Backpressure |
|-------|----------------|--------------|
| Failure rate | Required | — |
| Timeout/probe interval | Required | — |
| Queue depth | — | Required |
| Consumer processing rate | — | Required |
| Threshold parameters | Failure %, window size | Max queue depth, desired depth |

## Outputs

| Output | Description |
|--------|-------------|
| Circuit state | CLOSED / OPEN / HALF-OPEN |
| Fail-fast response | Returned immediately when OPEN (no downstream call made) |
| Backpressure signal | Rate reduction instruction sent to producer |
| Admission decision | Accept or reject incoming request |

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Circuit opens on transient blip | Threshold too sensitive | Widen window; require minimum request count before tripping |
| Circuit never opens | Threshold too conservative | Tighten failure rate threshold |
| Retry storm after circuit closes | All callers retry simultaneously | Add jitter to re-try timing; use exponential backoff ([11-rate-limiting-token-bucket.md](11-rate-limiting-token-bucket.md)) |
| Backpressure signal not honored | Producer ignores signal | Enforce at queue ingress; drop or block if signal not respected |
| Queue absorbs brief spikes fine but fails on sustained load | Backpressure threshold too high | Lower threshold; apply backpressure earlier |
| Half-open probe brings system back down | Too many probes at once | Allow exactly one probe; wait for full success before CLOSED |

## Worked Example: Agent Tool Call Isolation

**Problem**: An agent calls a vector database API. The API starts timing out at >80% utilization. Without a circuit breaker, every step waits the full timeout before failing.

```
Circuit Breaker configuration:
  window = 60 seconds
  threshold = 40% failure rate (need only 40% fail rate in 60s window)
  timeout = 20 seconds
  probe_interval = 15 seconds

Sequence:
  t=0:   API healthy, CLOSED
  t=30:  API latency spikes; 45% of calls fail in 60s window
  t=30+: OPEN → fail fast (no calls to API); agent falls back to cached context
  t=45:  probe sent → fails → remain OPEN, reset timer
  t=60:  probe sent → succeeds → HALF-OPEN
  t=61:  next request succeeds → CLOSED; normal operation resumes

Without circuit breaker: every call at t=30 to t=60 waits 30s timeout → agent loop stalls.
With circuit breaker: calls at t=30 to t=60 fail in <1ms → agent continues with fallback.
```

## Sources

- Nygard (2018), *Release It!*, 2nd ed., Ch. 5. Pragmatic Bookshelf.
- Brewer (2000), PODC keynote.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 7.
- Fowler, M. "CircuitBreaker" pattern. [https://martinfowler.com/bliki/CircuitBreaker.html](https://martinfowler.com/bliki/CircuitBreaker.html)
