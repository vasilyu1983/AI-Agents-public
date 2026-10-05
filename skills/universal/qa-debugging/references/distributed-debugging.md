# Distributed Debugging

How to find which service actually caused a cross-service failure, and the ways traces, logs,
and clocks mislead. Instrumentation setup (OpenTelemetry SDKs, collectors, sampling policy,
backends) is owned by `../../qa-observability/SKILL.md`; see
`../../qa-observability/references/distributed-tracing-patterns.md` and `../../qa-observability/references/sampling-strategies.md`.

## Contents

- [Default Sequence](#default-sequence)
- [Find the Originating Service](#find-the-originating-service)
- [When the Trace Is Missing or Broken](#when-the-trace-is-missing-or-broken)
- [Time and Ordering](#time-and-ordering)
- [Retries, Timeouts, and Queues](#retries-timeouts-and-queues)
- [Consistency and Network Symptoms](#consistency-and-network-symptoms)

---

## Default Sequence

1. Get one concrete failing request: trace ID, correlation ID, or the tuple (user/tenant,
   endpoint, timestamp) to find it.
2. Open the full trace before reading any single service's logs.
3. Find the originating span (next section), then read that service's logs **filtered by the
   trace ID**, not by time window.
4. Check that span's dependencies (DB, cache, queue, external API) for the same window.
5. Only then widen to aggregate metrics to see whether this request is typical of the failure.

## Find the Originating Service

- The service returning the user-visible 5xx is usually the **messenger, not the cause.** Walk
  down the causal chain to the deepest span that errored or was slow *first*; everything above
  it is propagation.
- Latency: find where **self time** grew, subtracting the union of overlapping synchronous
  child intervals rather than summing their durations. Async work may outlive its parent; use
  the request's critical path instead of assuming the root span encloses every child.
- Fan-out: with N parallel calls, total latency follows the slowest one. A dependency with a
  rare slow tail becomes a common slow tail at high fan-out.
- Errors that appear in many services at once point to a shared dependency (DNS, auth, config
  service, a common database, a sidecar), not N independent bugs. Check what they share before
  debugging any one of them.

## When the Trace Is Missing or Broken

- **The failing request was probably not sampled.** Head-based sampling at a low rate drops most
  error traces. If you cannot find traces for failures, the fix is tail-based sampling that keeps
  errors and slow requests (owned by qa-observability), not more searching.
- **Gaps and orphan root spans mean broken context propagation**, usually at an async boundary
  (queue message, thread pool, background job, a proxy that strips headers) or at a hop that
  uses a hand-rolled header.
- **Hand-rolled `traceparent` headers are a common cause.** The W3C format is
  `00-<32 lowercase hex trace-id>-<16 hex parent-id>-<2 hex flags>`. A value built from a dashed
  UUID string, a reused correlation ID of the wrong length, or an all-zero ID is invalid, and a
  receiver that gets an invalid `traceparent` ignores it and starts a new trace. The symptom
  looks like missing instrumentation downstream. Use the tracing SDK's propagator rather than
  building the header; if you must build one, use `uuid4().hex` (32 chars, no dashes) for the
  trace ID and a fresh 16-hex span ID per hop, and keep the trace ID unchanged across hops.
- Keep a separate business correlation ID (order ID, request ID) in logs and message metadata
  anyway: it survives hops where trace context is lost and joins traces to support tickets.

## Time and Ordering

- **Do not order cross-host events by wall-clock timestamp.** Clock skew between hosts can
  reorder events that are milliseconds apart, and a child span can appear to start before its
  parent. Use causal order (parent-child span links, message offsets, sequence numbers).
- When a timeline "shows" an effect before its cause, suspect skew before suspecting a bug.
  Check the NTP/chrony offset on the involved hosts (`chronyc tracking`, `timedatectl`).
- Anything that compares timestamps from different hosts for correctness (lock expiry, TTLs,
  last-write-wins) is a latent bug; the fix is logical ordering (versions, fencing tokens,
  hybrid logical clocks), not tighter clock sync.

## Retries, Timeouts, and Queues

- **Retry amplification.** Attempts at several layers multiply: 3 attempts at each of 3 layers
  can produce 27 bottom-level attempts; 3 retries plus the initial attempt can produce 64.
  A dependency that is slow becomes a dependency that
  is overloaded. Look for retry counts on spans before concluding the dependency is just slow.
- **Timeout inversion.** If a caller's timeout is shorter than its callee's, the callee keeps
  working on requests nobody is waiting for. Timeouts should shrink going down the call chain,
  ideally via a propagated deadline.
- **Queue diagnosis order:** consumer lag per partition, then DLQ contents grouped by error type
  and producer, then consumer rebalance events around the incident time.
  - Lag on one partition only points to a hot key or a poison message blocking that partition.
  - Duplicates or reordering after a rebalance mean consumers are not idempotent or commit
    offsets before processing finishes.
  - Out-of-order processing for one entity means the partition key is not the entity ID, or a
    retry path re-enqueues behind later messages.

## Consistency and Network Symptoms

| Symptom | Likely cause | First check |
|---------|--------------|-------------|
| Write succeeds, immediate read is stale | Read-after-write against a replica | Replica lag for that window; whether the read path pins to primary after writes |
| Timeouts between one pair of services only | Network policy, DNS, connection pool exhaustion on the caller | Caller pool metrics and DNS resolution from the caller's pod |
| 503 from a Kubernetes Service | No ready endpoints | `kubectl get endpoints <svc>`: empty means readiness is failing, not networking |
| Latency spike with low CPU usage | CPU throttling under a cgroup limit, or waiting on a dependency | Container throttling metrics; off-CPU time |
| Intermittent 5xx across many services | Shared dependency or a mesh/sidecar issue | What the failing services have in common |
| Two nodes both acting as leader | Split brain during a partition | Election logs; whether the resource checks fencing tokens |

For in-cluster connectivity tests, run a throwaway debug pod in the caller's namespace and test
from there. Testing from your laptop or a different namespace bypasses the network policies and
DNS search paths that are the likely cause.
