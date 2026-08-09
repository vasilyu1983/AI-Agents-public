# Queueing Theory Applied to DevOps and Platform Engineering

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Last verified: 2026-05-02._

Every DevOps platform is a network of queues. CI runner pools, Kubernetes worker nodes, Kafka consumer groups, API gateway thread pools, and microservice chains are all queueing systems with measurable utilization, service time, and wait time. Without intentional capacity modeling, they fail in predictable but avoidable ways: latency spikes at 70% CPU, scaling events that make things worse, and alert storms that appear after the cliff is already crossed.

This reference maps the 11 primitives from [foundations-queueing-theory](../../foundations-queueing-theory/SKILL.md) onto the concrete problems that platform and DevOps engineers face daily.

---

## Table of Contents

- [Patterns](#patterns)
  - [P3 Capacity Sizing via M/M/c and Erlang-C](#p3-capacity-sizing-via-mmc-and-erlang-c)
  - [P5 Priority-Queue Policy for Multi-Tier Traffic](#p5-priority-queue-policy-for-multi-tier-traffic)
  - [P6 Jackson-Network Thinking for Microservice Topology](#p6-jackson-network-thinking-for-microservice-topology)
  - [P7 Kingman Heavy-Traffic Approximation for Tail Latency Under Load](#p7-kingman-heavy-traffic-approximation-for-tail-latency-under-load)
  - [P8 Bufferbloat Avoidance in Queue and Buffer Sizing](#p8-bufferbloat-avoidance-in-queue-and-buffer-sizing)
  - [P9 USL Retrograde Detection for Scaling Limits](#p9-usl-retrograde-detection-for-scaling-limits)
  - [P11 Fork-Join Sizing for Parallel-Only-at-Scale Stages](#p11-fork-join-sizing-for-parallel-only-at-scale-stages)
- [Anti-Patterns](#anti-patterns)
  - [A1 M/M/1 Used at ρ Approaching 1 Without USL Check](#a1-mm1-used-at-ρ-approaching-1-without-usl-check)
  - [A2 Little's Law Applied on Non-Stationary Windows](#a2-littles-law-applied-on-non-stationary-windows)
  - [A3 Erlang-C and Erlang-B Confusion](#a3-erlang-c-and-erlang-b-confusion)
  - [A4 Fork-Join Sized by Mean Response Time](#a4-fork-join-sized-by-mean-response-time)
  - [A5 CV² of Service Time Ignored on G/G/1 Workloads](#a5-cv-of-service-time-ignored-on-gg1-workloads)
- [Recipes](#recipes)
  - [R1 Capacity Plan for a New Service](#r1-capacity-plan-for-a-new-service)
  - [R2 Saturation SLO Threshold — Set the Alert Before the Cliff](#r2-saturation-slo-threshold--set-the-alert-before-the-cliff)
  - [R3 Multi-Stage Pipeline Bottleneck Hunt](#r3-multi-stage-pipeline-bottleneck-hunt)
- [Composition Guide](#composition-guide)
- [Sources](#sources)

---

## Patterns

### P3 Capacity Sizing via M/M/c and Erlang-C

**Primitive**: [M/M/c (Erlang-C)](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)

**Problem**: How many Kubernetes pod replicas, RDS connection pool slots, or GitHub Actions runners are needed to meet a latency SLO at the expected request rate? The instinct is to size for peak CPU utilization. The correct approach is to size for queue wait time.

**Structure**:

```
a   = λ / μ          (offered load in Erlangs)
ρ   = λ / (c × μ)   (per-server utilization; must be < 1)

Erlang-C: C(c, a) = probability that an arrival must wait

Wq  = C(c, a) / (c × μ − λ)   (mean queue wait time)
W   = Wq + 1/μ                 (total response time)
```

**Implementation in practice**:

- Collect λ (requests/s from Prometheus `rate(http_requests_total[5m])`) and E[S] (mean service time from APM p50).
- Compute offered load a = λ / μ. This is the minimum number of servers for stability — you need c > a.
- Iterate c upward until Wq satisfies the latency budget (W ≤ SLO). Use an Erlang-C calculator or the formula above. A target of ρ ≤ 0.70–0.75 provides stable headroom.
- For Kubernetes HPA, set the target CPU or RPS such that at target load the replica count c produces ρ = 0.70. The HPA metric threshold is a derived quantity, not a primary one.
- For database connection pools (PgBouncer, HikariCP): model connection arrivals as λ, mean transaction time as 1/μ, pool size as c. Erlang-C gives the probability that a connection request waits. Set pool size so C(c, a) ≤ 0.05 (5% of requests queue) and Wq ≤ 2 ms.

**Erlang-C quick reference** (a = 10 Erlangs):

| c | ρ per server | C(c, 10) | Wq / E[S] |
|---|-------------|---------|-----------|
| 11 | 0.91 | 0.763 | 7.6× |
| 13 | 0.77 | 0.356 | 1.5× |
| 15 | 0.67 | 0.152 | 0.46× |
| 20 | 0.50 | 0.016 | 0.03× |

Moving from ρ = 0.91 to ρ = 0.77 (adding 2 servers at a = 10) cuts Wq by 5×. The last few servers buy the most SLO improvement.

**DevOps sizing heuristic**: always provision for ρ_target ≤ 0.70 at sustained peak, then add one spare server above that. The Erlang-C curve is convex — the penalty for operating at ρ = 0.80 vs. 0.70 is far larger than the cost of one extra replica.

---

### P5 Priority-Queue Policy for Multi-Tier Traffic

**Primitive**: [Priority Queues](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md)

**Problem**: A Kubernetes cluster or API gateway handles both interactive user traffic and background batch jobs. Under load, batch jobs saturate the worker pool and interactive requests see elevated p99. Adding more nodes raises cost but does not fix the structural mix. Priority scheduling separates SLO classes without requiring over-provisioning.

**Structure (non-preemptive, two classes)**:

```
Class 1: interactive  λ₁, E[S₁], ρ₁ = λ₁ / (c × μ₁)
Class 2: batch        λ₂, E[S₂], ρ₂ = λ₂ / (c × μ₂)

W0  = (λ₁ × E[S₁²] + λ₂ × E[S₂²]) / 2   (residual service time)

Wq_1 = W0 / (1 − ρ₁)
Wq_2 = W0 / ((1 − ρ₁)(1 − ρ₁ − ρ₂))
```

Class 1 latency depends only on its own load and the residual service time of whichever job is currently in service — at most one batch job's service time. Class 2 latency can be arbitrarily high when ρ₁ + ρ₂ approaches 1.

**Implementation in practice**:

- **Kubernetes**: assign interactive workloads to pods with `PriorityClass: high-priority` (value 100000) and batch to `PriorityClass: low-priority` (value 1000). The scheduler preempts low-priority pods when high-priority pods cannot be scheduled. Set `preemptionPolicy: PreemptLowerPriority` on high-priority class.
- **API gateway / Nginx**: use separate upstream groups for interactive and batch paths. Rate-limit batch at ingress (`limit_req_zone`) so batch ρ₂ stays below 0.30, leaving ρ_interactive head-room.
- **Kafka**: maintain separate topics or partitions for high-value and low-value events. Assign dedicated consumer group with higher replica count to the high-value topic. Do not share a single consumer group across priority classes — partition rebalancing destroys the ordering guarantee.
- **Starvation guard**: when ρ₁ is sustained above 0.85, low-priority class may starve. Reserve a floor — e.g., 10% of worker capacity — for batch via a token bucket bypass even under high priority load.

**Anti-pattern to avoid**: applying priority at the load balancer but not at the worker. If the Nginx upstream sends batch and interactive to the same thread pool without priority scheduling, the benefit is lost at the final service point.

---

### P6 Jackson-Network Thinking for Microservice Topology

**Primitive**: [Jackson Networks](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md)

**Problem**: A microservice chain passes through API gateway → auth service → business logic → database → cache. When latency rises, engineers guess the bottleneck, scale the wrong service, and find that latency is unchanged or worse. Jackson network analysis makes bottleneck identification deterministic.

**Structure**:

Solve traffic equations (flow balance) to find effective arrival rate at each station:

```
λᵢ = γᵢ + Σⱼ λⱼ × Pⱼᵢ
```

Then compute per-station utilization:

```
ρᵢ = λᵢ / (cᵢ × μᵢ)
```

The **bottleneck** is the station with the highest ρᵢ. The throughput ceiling of the entire pipeline is:

```
X_max = min over stations of (cᵢ × μᵢ)
```

**Implementation in practice**:

- **Read from service mesh**: Istio, Linkerd, or AWS App Mesh emit per-service request rates and latency. Use `istio_requests_total` (γᵢ, routing probabilities Pᵢⱼ) and `istio_request_duration_milliseconds` (to derive μᵢ).
- **Flow-balance calculation**: for a linear chain with retry amplification, effective λᵢ at stage i = λ_external × Πⱼ≤ᵢ (1 + retry_rate_j). A 10% retry rate on each of 3 stages inflates effective load to 1.1³ = 1.33× the external arrival rate at the final stage — a 33% hidden load.
- **After scaling**: after scaling the bottleneck station, re-solve flow balance. The next-highest ρᵢ becomes the new bottleneck. Failing to re-solve is the most common mistake: engineers report "scaling didn't help" when in fact it shifted the bottleneck to an unmonitored service.
- **Cycles (retry loops)**: retries create feedback cycles in the routing matrix. Model them explicitly: if 20% of requests to stage 2 retry stage 1, the routing matrix has P₂₁ = 0.20. The resulting λ₁ is higher than external arrivals suggest. This is the mathematical explanation for retry storms.

**DevOps action**: build a simple Jackson spreadsheet from your service mesh data. Update it after every major scaling action. Assign the bottleneck station an alert: `ρ_bottleneck > 0.70 for 5 minutes`.

---

### P7 Kingman Heavy-Traffic Approximation for Tail Latency Under Load

**Primitive**: [Kingman's Formula](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md)

**Problem**: M/M/1-based capacity models predict acceptable latency at 80% CPU. Real production latency is 3–5× higher. The gap is caused by arrival burstiness (CV²_a > 1) and service-time variability (CV²_s > 1) — both of which M/M/1 ignores by assuming Poisson arrivals and exponential service. Kingman's formula makes this gap visible before it causes an incident.

**Formula**:

```
Wq ≈ (ρ / (1 − ρ)) × ((CV²_a + CV²_s) / 2) × E[S]

Variability Factor (VF) = (CV²_a + CV²_s) / 2
```

| VF | Wq vs. M/M/1 |
|----|-------------|
| 0.5 | 50% of M/M/1 |
| 1.0 | Equal to M/M/1 |
| 2.0 | 2× M/M/1 |
| 5.0 | 5× M/M/1 — common in task queues, LLM inference |

**Measuring CV²_a and CV²_s in practice**:

- **CV²_a** from Prometheus: compute the inter-arrival time series from `rate(http_requests_total[1m])` sampled every 5 seconds. Calculate variance / mean² over a representative window. HTTP traffic from mobile apps or microservices is typically CV²_a = 2–4 (bursty).
- **CV²_s** from APM: export the full service-time histogram from Datadog or Jaeger. CV²_s = σ²_service / μ²_service. For services with fast and slow code paths (cache hit vs. miss, DB query vs. cache hit), CV²_s can exceed 5.

**Application to SLO budgets**: run Kingman at the expected peak ρ before launch. If VF = 3 and ρ = 0.80, Wq is 3× the M/M/1 prediction. If M/M/1 says "40 ms queue wait at ρ = 0.80," Kingman says "120 ms." That 80 ms gap — invisible to M/M/1-based sizing — is where SLO budget goes.

**Levers**: reduce CV²_a with a rate-limiting / token bucket layer at ingress (smooths bursty arrivals). Reduce CV²_s by splitting heterogeneous jobs into separate queues by size class (fast-lane / slow-lane). Either action reduces VF and the resulting Wq, even without adding capacity.

---

### P8 Bufferbloat Avoidance in Queue and Buffer Sizing

**Primitive**: [Bufferbloat](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md)

**Problem**: Prometheus shows CPU at 75%, throughput is stable, but p99 latency is 10–30× p50 under load. The system is "working" — no errors, no dropped requests — yet SLOs are breached. The culprit is oversized application-layer buffers: they absorb load silently while accumulating latency debt.

**Core mechanism**:

```
Latency penalty = queue_depth / processing_rate

For a thread pool with unbounded queue:
  Spike arrival rate = 2× normal rate for 10 seconds
  Excess accumulation = (2λ − λ) × 10s = 10λ jobs
  Drain time = 10λ / excess_capacity
  Every job arriving during drain waits: latency spikes for minutes
```

**Implementation in practice**:

- **Kubernetes workqueue**: set `maxConcurrentReconciles` in controller-runtime to match actual worker throughput. Default is often 1 — a single slow reconcile blocks all others. Expose the controller workqueue depth via `workqueue_depth` metric; alert if depth exceeds 2× expected.
- **Kafka consumer lag**: unbounded consumer lag is application-layer bufferbloat. A consumer processing 500 msg/s falling behind a 600 msg/s producer creates a standing queue that grows by 100 msg/s. The correct response is to add consumer replicas before lag exceeds `max.poll.interval.ms × processing_rate`. Alert on lag **growth rate**, not lag absolute value.
- **HTTP server backlog**: set `backlog` in your HTTP server to a bounded value. For a service at 100 RPS with E[S] = 50 ms, L = λ × W = 100 × 0.05 = 5 in-flight. An unbounded backlog of 10,000 means callers queue for 100 seconds during a spike rather than receiving a 503 and backing off.
- **BDP rule**: size buffers at most 2–3× the expected steady-state queue depth from M/M/1: Lq = ρ² / (1 − ρ). At ρ = 0.70, Lq ≈ 1.6 items. A buffer of 5–10 items is sufficient — not 1,000.
- **Active Queue Management**: where possible, apply AQM (CoDel or PIE in application-level queue schedulers). For Java services: use `LinkedBlockingQueue` with a bounded capacity; for Python asyncio: `asyncio.Queue(maxsize=N)`. Explicit backpressure — returning 429 when the queue is full — converts silent latency debt into observable error budget consumption.

---

### P9 USL Retrograde Detection for Scaling Limits

**Primitive**: [Universal Scalability Law](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md)

**Problem**: A service under sustained load is scaled from 4 replicas to 8 replicas. Throughput improves less than expected. It is scaled to 16 replicas. Throughput drops. The team adds a 17th replica. Throughput drops further. This is retrograde scaling — caused by coordination overhead (κ > 0) in distributed systems — and it is predictable from load test data collected before the production incident.

**USL model**:

```
X(N) = λ × N / (1 + σ(N − 1) + κN(N − 1))

N_max = sqrt((1 − σ) / κ)

σ = contention coefficient (serialized resources: locks, global state)
κ = coherency coefficient (cross-node coordination: consensus, cache invalidation)
```

**Implementation in practice**:

- **Fit USL from load tests**: run load tests at N = 1, 2, 4, 8, 16 replicas; record throughput X(N). Use non-linear least-squares (Python `scipy.optimize.curve_fit`) to fit σ and κ. A minimum of 5–6 data points is required for a reliable fit.
- **Identify N_max before production**: if the fit yields κ = 0.003 (non-zero), N_max ≈ 18 nodes. Scaling beyond 18 reduces throughput. This is a hard architectural limit until κ is reduced.
- **Reduce κ in practice**: κ is driven by distributed coordination — Raft consensus rounds, distributed cache invalidation (Redis CLUSTER, Memcached replication), global leader election, cross-shard join queries. Reducing κ means: sharding global state, switching from strong to eventual consistency where the SLO allows, or partitioning workloads that share coordinated resources.
- **Reduce σ in practice**: σ is driven by serialized critical sections — global mutexes, single-writer database tables, single-partition Kafka topics. Shard the serial resource (e.g., partition Kafka by tenant key to distribute load, split the global mutex into per-shard locks).
- **When to stop scaling horizontally**: if load tests show X(N) flattening at N = 8 with σ = 0.10, the system has exhausted horizontal scaling efficiency via Amdahl's Law. Adding more nodes buys little throughput. The fix is architectural (reduce σ), not operational.
- **Compose with M/M/c**: M/M/c assumes linear scaling — that adding a server linearly reduces ρ per server. USL invalidates this assumption when κ > 0. Always run a USL check alongside M/M/c sizing for any distributed system.

---

### P11 Fork-Join Sizing for Parallel-Only-at-Scale Stages

**Primitive**: [Fork-Join (Parallel Work, Slowest-Worker Bound)](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md)

**Problem**: A CI pipeline fans out to K parallel test shards and completes when all shards finish. An API aggregator fans out to K downstream services and returns when all respond. In both cases, the completion time is determined by the **slowest** worker — and engineers who size these stages by average worker latency underestimate the actual completion time by 2–3×.

**Structure**:

```
E[max(S₁,...,Sₖ)] = E[S] × H_K        (exponential service times)

H_K = Σ_{k=1}^{K} 1/k                 (K-th harmonic number)
```

| K | H_K | E[max] / E[S] |
|---|-----|--------------|
| 1 | 1.00 | 1.00× |
| 2 | 1.50 | 1.50× |
| 5 | 2.28 | 2.28× |
| 10 | 2.93 | 2.93× |
| 20 | 3.60 | 3.60× |

For non-exponential workers (high CV²_s), the expected maximum is higher than H_K × E[S]. Measure the empirical 95th percentile per worker and use that as the effective E[S] in the formula for SLO analysis.

**Implementation in practice**:

- **CI test sharding**: a test suite with K = 20 shards and mean shard time E[S] = 3 min has E[max] ≈ 3 × 3.6 = 10.8 min — even if each shard averages 3 minutes. To cut wall-clock time, reduce the slowest shard (identify outliers, not average), not the average. A shard distribution with low CV²_s (uniform shard size) is more valuable than adding more shards.
- **Scatter-gather API**: an aggregation endpoint that fans out to K = 5 downstream APIs: if each averages 80 ms, E[max] ≈ 80 × 2.28 = 182 ms. A 200 ms SLO for the aggregated response is tight, not comfortable. Set a 150 ms timeout per downstream call with a partial-results fallback to bound the fan-out tail.
- **Multi-AZ health check probes**: Kubernetes readiness probes across K = 3 AZs must all pass before traffic is routed. E[max] = E[probe] × H₃ ≈ E[probe] × 1.83. Size the `timeoutSeconds` on readiness probes accordingly — not as E[probe] alone.
- **Speculative execution**: for K > 5 with high CV²_s, launch a hedge request to the slowest worker after a timeout equal to the median completion time (P50). If the hedge finishes first, use its result. This trades compute cost for latency tail reduction. Effective in scatter-gather APIs and parallel data retrieval where idempotency is guaranteed.
- **Diminishing returns**: doubling workers from K = 10 to K = 20 adds only H₂₀ − H₁₀ ≈ 0.67 × E[S] to completion time. The incremental latency penalty of adding more parallel branches is sub-linear — use this to justify wider fan-out without SLO anxiety, but set a per-branch timeout to prevent a single slow branch from dominating.

---

## Anti-Patterns

### A1 M/M/1 Used at ρ Approaching 1 Without USL Check

**Queueing theory diagnosis**: M/M/1 predicts Wq = ρ/(μ(1−ρ)), which diverges as ρ → 1. Engineers observe this and respond by adding servers. If the system has any coherency overhead (κ > 0), adding servers past N_max reduces throughput — making the utilization problem worse, not better.

**Symptom**: A service is scaled from 8 to 16 pods when ρ ≈ 0.85. Throughput improves by less than expected. Engineers conclude "the service needs more CPUs" and request larger instance types, not recognizing that the throughput ceiling is architectural.

**Fix**: Before any horizontal scaling action past N = 8, run a USL fit from load tests. If κ > 0, N_max is finite. Optimize for lower σ/κ before scaling further. Then apply M/M/c to size within the USL-validated range.

**How to detect in production**: plot X(N) from load tests at several replica counts. A throughput curve that bends over and declines is the signature of κ > 0 retrograde. A curve that flattens is σ > 0 Amdahl saturation.

---

### A2 Little's Law Applied on Non-Stationary Windows

**Queueing theory diagnosis**: Little's Law (L = λW) holds only at steady state. During traffic spikes, deployment rollouts, and incident recovery, the system is transient. Applying L = λW to a 1-minute window during a spike produces consistency errors: the measured L, λ, and W will not satisfy the equation, leading to incorrect diagnoses.

**Symptom**: An engineer observes L = 500 in-flight requests, λ = 200 req/s, and W = 100 ms. Little's Law gives L = λW = 200 × 0.1 = 20 — wildly inconsistent with the measured 500. The engineer concludes the metrics are broken. They are not; the system is not at steady state (it is recovering from a queue accumulation spike).

**Fix**: validate the measurement window before applying Little's Law. Use a window of at least 10× the mean service time. For a service with E[S] = 50 ms, use a minimum 500 ms window. For capacity planning purposes, use a window of at least 5 minutes during a period of stable, representative traffic — not during a peak or incident.

**Correct application**: use Little's Law as a sanity check on steady-state dashboards — verify that `inflight_gauge ≈ request_rate × mean_latency` over a 5-minute rolling window. A persistent violation of this identity signals either a measurement misalignment (different populations counted) or an unstable system.

---

### A3 Erlang-C and Erlang-B Confusion

**Queueing theory diagnosis**: Erlang-C models a **queuing** system — arrivals wait for service when all servers are busy. Erlang-B models a **loss** system — arrivals are dropped (blocked) when all servers are busy. Applying Erlang-C to a system that actually drops connections produces an over-optimistic wait-time estimate (you think requests wait; they actually fail).

**Symptom**: A WebSocket connection pool is sized using Erlang-C ("at a = 20 Erlangs and c = 25 connections, only 8% of requests wait"). In production, clients see connection refused errors under load. The system was actually dropping connections (Erlang-B behavior), not queuing them. The correct Erlang-B blocking probability at a = 20, c = 25 is non-trivial and larger than the Erlang-C wait probability would suggest.

**Fix**:
- Use **Erlang-B** when arrivals that find all servers busy are dropped and lost (WebRTC connections, thread pool exhaustion that returns an immediate error, license server slots).
- Use **Erlang-C / M/M/c** when arrivals that find all servers busy wait in a queue (HTTP request queuing, job scheduler queues, database connection pools with a wait timeout > 0).
- Check your server configuration: does a busy connection pool return an error immediately or block the caller? That answer determines the correct model.

---

### A4 Fork-Join Sized by Mean Response Time

**Queueing theory diagnosis**: In a K-way fork-join, the completion time equals the maximum of K independent service times, not their mean. E[max] = E[S] × H_K, where H_K ≥ 1 and grows with K. Sizing by mean service time underestimates the actual completion time by a factor of H_K — which is 2.3× for K = 5 and 2.9× for K = 10.

**Symptom**: A scatter-gather endpoint fans out to K = 8 downstream services, each with E[S] = 100 ms mean. Engineers add 10% margin and set a 110 ms SLO. In production, p50 latency is 215 ms (H₈ ≈ 2.15×). The SLO is missed from day one. Post-incident review finds the sizing assumed sequential rather than maximum-order statistics.

**Fix**: apply the H_K correction during design. For K = 8, budget E[max] = 100 × 2.15 = 215 ms. Set a per-branch timeout at P90 of the individual service time distribution and return partial results when the timeout is hit. For p99 SLOs, the tail of the maximum is heavier than the harmonic correction alone — add 30–50% on top of E[max] as an empirical p99 buffer, or simulate.

---

### A5 CV² of Service Time Ignored on G/G/1 Workloads

**Queueing theory diagnosis**: Kingman's formula shows that queue wait is inflated by the variability factor VF = (CV²_a + CV²_s) / 2. When CV²_s is large — mixed fast (cache hit) and slow (DB query) service times — the actual Wq can be 3–5× higher than M/M/1 predicts. Ignoring CV²_s produces capacity plans that are under-provisioned for the actual workload mix.

**Symptom**: Load testing at ρ = 0.75 shows acceptable p50 latency. Production p99 latency at the same ρ is 5× higher. Tracing reveals that some requests hit a slow code path (cache miss + synchronous DB call) with service time 10× the mean. The CV²_s for this service is approximately 4.0. Kingman predicts VF = (1 + 4.0) / 2 = 2.5, so Wq is 2.5× the M/M/1 prediction — accounting for most of the p99 gap.

**Fix**:
- Measure CV²_s from your APM service-time histogram: CV²_s = variance / mean². If CV²_s > 2, apply Kingman rather than M/M/1 for capacity sizing.
- Reduce CV²_s structurally: separate fast and slow code paths into separate queues or worker pools (fast-lane / slow-lane). Route cache-hit requests to a shallow pool and DB-backed requests to a deeper pool with longer timeouts.
- Set ρ_max lower when CV²_s is high. At CV²_s = 4 and CV²_a = 2, VF = 3. To keep Wq ≤ 20 ms with E[S] = 10 ms, you need ρ/(1−ρ) × 3 × 0.010 ≤ 0.020, so ρ ≤ 0.40. That is a far lower utilization ceiling than you would expect from M/M/1 alone.

---

## Recipes

### R1 Capacity Plan for a New Service

**Goal**: Determine the replica count (or thread pool size) for a new service before launch, with an SLO-backed justification.

**Primitives used**: Little's Law (#1) → M/M/c with Erlang-C (#3) → Kingman (#7) for variability adjustment → USL (#9) for scaling safety check.

**Tooling**: Prometheus or Datadog (traffic metrics), APM service-time histograms, Python `scipy` for USL fit from load tests.

```
Step 1 — Establish baseline traffic parameters
  λ_p50 = expected average arrival rate (req/s) from traffic projection
  λ_peak = peak arrival rate (e.g., 2× p50 for diurnal patterns)
  E[S]   = mean service time from staging or analogous service APM data
  μ      = 1 / E[S]

  Sanity-check with Little's Law:
    L_expected = λ_p50 × E[S]   (expected in-flight request count)
    Verify this matches staging concurrency metrics.

Step 2 — M/M/c minimum sizing (Erlang-C)
  a = λ_peak / μ               (offered load in Erlangs at peak)
  Target ρ ≤ 0.70:
    c_target = ceil(a / 0.70)  (first-pass replica count)

  Compute Wq from Erlang-C at (c_target, a):
    C(c, a) = Erlang-C formula or calculator
    Wq = C(c, a) / (c × μ − λ_peak)

  If Wq > latency_budget × 0.20:   (queue wait ≤ 20% of total SLO)
    increment c and recompute until Wq is within budget.

Step 3 — Kingman variability adjustment
  Measure (or estimate from similar services):
    CV²_a = 2.0  (HTTP traffic, moderately bursty; measure in staging)
    CV²_s = 1.5  (typical mixed API with some DB calls)
    VF    = (CV²_a + CV²_s) / 2 = 1.75

  Wq_kingman = Wq_mmc × VF
    (Erlang-C gives the Poisson/exponential baseline; multiply by VF for realism)

  If Wq_kingman exceeds budget, either:
    (a) add one more replica (repeat Step 2)
    (b) reduce CV²_a via rate limiting at ingress
    (c) split into fast/slow lanes to reduce CV²_s

Step 4 — USL retrograde check
  If this service communicates with shared state (distributed cache, DB cluster, Kafka):
    Run load tests at N = 1, 2, 4, 8 replicas
    Fit σ and κ via scipy.optimize.curve_fit
    Compute N_max = sqrt((1 − σ) / κ)

  If c_target (from Step 2) > N_max:
    c_target cannot be reached via horizontal scaling alone.
    Reduce σ/κ (shard state, reduce coordination) before proceeding.

Step 5 — Safety margin and alert threshold
  c_final = c_target + 1 spare replica

  HPA target metric = λ_peak / c_target
    (set HPA to scale in when average RPS per replica exceeds this value)

  SLO alert: trigger if ρ_observed > 0.75 for > 5 minutes
    (Erlang-C: at ρ = 0.75 with a = 10 Erlangs, C(c,a) is still manageable;
     at ρ = 0.85, Wq doubles)
```

**Expected output**: a justified replica count with a documented ρ_target, a Wq estimate that accounts for real-world variability, a USL-verified scaling ceiling, and an HPA threshold derived from first principles rather than "we set it to 70% CPU."

---

### R2 Saturation SLO Threshold — Set the Alert Before the Cliff

**Goal**: Determine the utilization or queue-depth threshold at which an alert fires before the SLO is breached, not after. Set this threshold on `Lq` (queue depth) rather than `p99` to get a leading indicator.

**Primitives used**: Kingman (#7) for tail latency under load → Little's Law (#1) to convert latency to queue depth → set alert on `Lq`, not `p99`.

```
Step 1 — Model tail latency vs. utilization using Kingman
  Measure CV²_a, CV²_s from production histograms.
  VF = (CV²_a + CV²_s) / 2

  For each ρ from 0.50 to 0.95 (step 0.05):
    Wq(ρ) = (ρ / (1 − ρ)) × VF × E[S]
    W(ρ)  = Wq(ρ) + E[S]

  Find ρ_slo: smallest ρ where W(ρ) > latency_SLO
    This is the cliff. You want to alert well before reaching ρ_slo.

Step 2 — Set alert threshold at ρ_alert = ρ_slo − 0.10
  Example: if ρ_slo = 0.82, set ρ_alert = 0.72.
  This gives ~10 percentage points of headroom to investigate before breach.

Step 3 — Convert ρ_alert to a queue-depth threshold (leading indicator)
  At ρ_alert, compute Lq from Little's Law:
    Wq_alert = Kingman(ρ_alert)
    Lq_alert = λ × Wq_alert

  Alert condition (Prometheus):
    sum(rate(http_requests_total[1m])) × (histogram_quantile(0.50, latency_bucket))
      > Lq_alert

  Or equivalently:
    workqueue_depth > Lq_alert   (Kubernetes controller workqueue)
    kafka_consumer_lag > Lq_alert × E[S]  (Kafka consumer lag in seconds)

Step 4 — Why Lq beats p99 as a threshold
  p99 latency is a lagging indicator:
    - By the time p99 exceeds the SLO, the queue is already saturated.
    - p99 includes both queue wait and service time; it rises sharply near ρ_slo.
  Lq is a leading indicator:
    - Queue depth starts rising before latency spikes (Lq = λ × Wq).
    - An alert on Lq fires when Wq is still within SLO budget, giving response time.
    - Lq is less noisy than p99 at moderate ρ (no tail sampling artifacts).

Step 5 — Compose with USL bound
  If USL fit shows N_max < c_final:
    Reduce ρ_alert further to ρ_alert = ρ_slo − 0.15.
    Add a separate alert: "replica count approaching N_max" (triggered when
    c_actual > N_max × 0.80).
```

**Concrete example**: a backend service with E[S] = 20 ms, CV²_a = 2.5, CV²_s = 2.0, VF = 2.25, SLO = 200 ms.

- Kingman: W(ρ) = (ρ/(1−ρ)) × 2.25 × 0.020 + 0.020.
- At ρ = 0.85: W = (0.85/0.15) × 0.045 + 0.020 = 5.67 × 0.045 + 0.020 = 0.275 s — SLO breached.
- At ρ = 0.75: W = 3.0 × 0.045 + 0.020 = 0.155 s — within SLO.
- ρ_slo ≈ 0.82, ρ_alert = 0.72. Alert fires when utilization crosses 72%, not when p99 crosses 200 ms.

---

### R3 Multi-Stage Pipeline Bottleneck Hunt

**Goal**: Identify the throughput bottleneck in a microservice chain or data pipeline and quantify the scaling action needed to relieve it without shifting the bottleneck to an unmonitored stage.

**Primitives used**: Jackson networks (#6) to identify ρ_max → M/M/c (#3) to size the bottleneck station → USL (#9) to verify scaling the bottleneck does not trigger retrograde → priority queues (#5) if mixed SLO classes converge at the bottleneck.

**This is the strongest recipe because it converts a vague "we need to scale" conversation into a numerical answer before any infrastructure is changed.**

```
Step 1 — Collect per-service traffic data (Jackson input)
  From service mesh (Istio/Linkerd metrics) or tracing:
    γᵢ  = external request rate into station i (req/s)
    Pᵢⱼ = routing probability from station i to station j
          (fraction of requests that call service j after service i)
    μᵢ  = 1 / E[Sᵢ]   (from per-service mean latency metric)
    cᵢ  = current replica count for service i

  Include retry amplification:
    If service i retries downstream service j at rate r_retry:
      Pᵢⱼ_effective = Pᵢⱼ + r_retry   (e.g., 0.70 routing + 0.10 retry = 0.80)

Step 2 — Solve flow balance equations
  λᵢ = γᵢ + Σⱼ λⱼ × Pⱼᵢ   (solve this linear system for each station i)

  For a linear chain (common case): λᵢ = λ_external × Πⱼ<ᵢ (1 + retryⱼ)

  Compute per-station utilization:
    ρᵢ = λᵢ / (cᵢ × μᵢ)

  Identify bottleneck: i* = argmax(ρᵢ)
  Identify throughput ceiling: X_max = min over i of (cᵢ × μᵢ)

Step 3 — Size bottleneck station with M/M/c
  At bottleneck i*:
    a*  = λᵢ* / μᵢ*          (offered load)
    c*_target: smallest c such that ρᵢ* ≤ 0.70 and Wq ≤ SLO_budget × 0.20

    Erlang-C at (c*_target, a*): verify Wq is within budget.

  Compute Δc = c*_target − cᵢ*   (number of additional replicas needed)

Step 4 — USL check on bottleneck station
  If bottleneck station shares distributed state (DB, cache, Kafka partition):
    Run load tests at current cᵢ* and 2× cᵢ*
    Fit USL: compute σ, κ, N_max
    If c*_target > N_max:
      Horizontal scaling is insufficient. Required action: reduce κ (shard state).

Step 5 — Re-solve flow balance after scaling
  After scaling station i* to c*_target:
    Recompute all ρᵢ with updated X_max = min(cᵢ × μᵢ) using new cᵢ*
    Identify new bottleneck i**
    If ρᵢ** > 0.80: repeat Steps 3–4 for the new bottleneck.

  Document the cascade: "Scaling auth from 2→4 replicas moves bottleneck to
  business-logic at ρ = 0.78. Business-logic needs to scale from 3→5."

Step 6 — Priority separation at bottleneck (if mixed SLO classes)
  If interactive (SLO = 100 ms) and batch (SLO = 5 s) traffic converge at i*:
    Compute ρ₁ = λ₁_interactive / (c*_target × μᵢ*)
    Verify ρ₁ + ρ₂_batch < 0.90 (system stability requirement)

    If without priority: both classes share wait proportional to ρ/(1−ρ)
    With non-preemptive priority:
      Wq_1 = W0 / (1 − ρ₁)      (interactive protected from batch)
      Wq_2 = W0 / ((1−ρ₁)(1−ρ₁−ρ₂))  (batch latency increases; acceptable)

    Implement as separate Kubernetes Deployments with PriorityClass,
    or separate thread pools with a priority queue at the worker.
```

**Expected output**: a table of per-service ρᵢ before and after, a Δc recommendation for each stage, a USL-validated scaling ceiling for the bottleneck, and a projection of where the bottleneck moves after the fix. This replaces "let's add 10 pods and see" with a testable prediction.

---

## Composition Guide

Queueing primitives at different scopes compose without coupling. The patterns above address separate concerns and should be applied in this order for a new platform:

| Concern | Pattern / Recipe | Primitive(s) |
|---------|-----------------|--------------|
| New service sizing | R1 | Little's Law (#1), M/M/c (#3), Kingman (#7), USL (#9) |
| Existing pipeline bottleneck | R3 | Jackson (#6), M/M/c (#3), USL (#9), Priority (#5) |
| Alert threshold calibration | R2 | Kingman (#7), Little's Law (#1) |
| Buffer and queue depth sizing | P8 | Bufferbloat (#8) |
| Horizontal scaling sanity | P9 | USL (#9) |
| Multi-tier traffic mixing | P5 | Priority Queues (#5) |
| Fan-out / scatter-gather | P11 | Fork-Join (#11) |

**Composition rules**:

- Always run Little's Law as a sanity check after computing Wq and Lq from any other formula. If L ≠ λ × W, re-examine measurement alignment.
- Apply Kingman on top of M/M/c whenever CV²_s > 1.5 or CV²_a > 1.5. M/M/c alone will underestimate Wq in real traffic.
- Run USL before committing to a horizontal scaling plan that targets N > 8 replicas for any service with shared distributed state.
- If the Jackson network analysis reveals a bottleneck, check USL for that bottleneck before scaling it. Scaling past N_max makes things worse.
- For fork-join stages, confirm that each worker in the fan-out is independently provisioned (not sharing a bottleneck resource) — otherwise the fork-join is effectively serial despite apparent parallelism.

**Starting point for a brownfield platform**: implement in this order:
1. R2 (alert thresholds from Kingman) — immediately improves alert lead time without any infrastructure change.
2. P8 (bufferbloat audit) — find and bound oversized queues; return 429 instead of silent latency accumulation.
3. R3 (pipeline bottleneck hunt) — replace guesswork scaling with flow-balance analysis.
4. R1 (new service sizing) — apply to every new service at design review, before launch.

---

## Sources

- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Kleinrock, L. (1976). *Queueing Systems, Vol. 2: Computer Applications*. Wiley-Interscience.
- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Pollaczek, F. (1930). "Über eine Aufgabe der Wahrscheinlichkeitstheorie." *Mathematische Zeitschrift*, 32(1), 64–100.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer. (USL and retrograde scaling.)
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. (Definitive computer systems queueing reference.)
- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11).
- Nichols, K. & Jacobson, V. (2012). "Controlling Queue Delay." *ACM Queue*, 10(5). (CoDel algorithm.)
- Nelson, R. & Tantawi, A. N. (1988). "The Approximate Analysis of Fork/Join Synchronization in Parallel Queues." *IEEE Transactions on Computers*, 37(6), 739–743.
- Little, J. D. C. (1961). "A Proof for the Queuing Formula: L = λW." *Operations Research*, 9(3), 383–387.
- Whitt, W. (1993). "Approximations for the GI/G/m queue." *Production and Operations Management*, 2(2), 114–161.
- Google SRE Book (2016). Ch. 21: "Handling Overload." [https://sre.google/sre-book](https://sre.google/sre-book)
- Kubernetes documentation. HPA — Horizontal Pod Autoscaler. [https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- DORA State of DevOps Report 2023. [https://dora.dev](https://dora.dev)
