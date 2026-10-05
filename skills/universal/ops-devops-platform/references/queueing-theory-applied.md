# Queueing Theory Applied to DevOps and Platform Engineering

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. This file is a link adapter: it maps platform decisions to the foundation and keeps only DevOps-specific inputs, pitfalls, and worked numbers. Formulas and derivations live in the foundation.

CI runner pools, Kubernetes replicas, Kafka consumer groups, gateway thread pools, and service chains are queues. Size them from a latency SLO and measured variability, not from a fixed CPU or utilization target.

---

## Table of Contents

- [Theory Pointers](#theory-pointers)
- [Patterns](#patterns)
  - [P3 Capacity Sizing via M/M/c and Erlang-C](#p3-capacity-sizing-via-mmc-and-erlang-c)
  - [P5 Priority-Queue Policy for Multi-Tier Traffic](#p5-priority-queue-policy-for-multi-tier-traffic)
  - [P6 Jackson-Network Thinking for Microservice Topology](#p6-jackson-network-thinking-for-microservice-topology)
  - [P7 Kingman Heavy-Traffic Approximation for Mean Queue Wait](#p7-kingman-heavy-traffic-approximation-for-mean-queue-wait)
  - [P8 Bufferbloat Avoidance in Queue and Buffer Sizing](#p8-bufferbloat-avoidance-in-queue-and-buffer-sizing)
  - [P9 USL Retrograde Detection for Scaling Limits](#p9-usl-retrograde-detection-for-scaling-limits)
  - [P11 Fork-Join Sizing for Parallel-Only-at-Scale Stages](#p11-fork-join-sizing-for-parallel-only-at-scale-stages)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
- [Composition Guide](#composition-guide)
- [Sources](#sources)

---

## Theory Pointers

| Need | Owner |
|---|---|
| Little's Law, stationarity | [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) |
| M/M/c, Erlang-C | [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md) |
| M/G/1, Pollaczek-Khinchine | [04-mg1-pollaczek-khinchine.md](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) |
| Priority queues | [05-priority-queues.md](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md) |
| Jackson networks, flow balance | [06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) |
| Kingman (single server) | [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) |
| Bufferbloat, AQM | [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md) |
| USL | [09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md) |
| Erlang-B (loss systems) | [10-loss-systems-erlang-b.md](../../foundations-queueing-theory/assets/templates/queueing-theory/10-loss-systems-erlang-b.md) |
| Fork-join | [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md) |
| Allen-Cunneen G/G/c, square-root staffing, pooling, overload, retries, CoDel, tail-at-scale | [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md) |
| Trace-driven simulation | [trace-driven-simulation.md](../../foundations-queueing-theory/references/trace-driven-simulation.md) |

---

## Patterns

### P3 Capacity Sizing via M/M/c and Erlang-C

**Decision**: replica count, runner count, or connection-pool size for a latency SLO.

**DevOps inputs**:

- λ from `rate(http_requests_total[5m])` over a stable window; E[S] as the arithmetic mean of per-request service time from APM (not p50).
- Offered load a = λ·E[S]. Stability needs c > a.
- Increase c until mean Wq meets the declared mean budget. Validate percentile SLOs separately with replay or load tests.
- **No portable ρ target.** Derive c from the SLO and measured variability (square-root staffing c ≈ a + β√a; Allen-Cunneen when CV² ≠ 1). The right ρ rises with a: large pools run hot safely, small pools cannot. See [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md).
- Kubernetes HPA: the per-replica RPS or CPU target is derived from the chosen c at peak (target = λ_peak / c), not set first.
- Connection pools (PgBouncer, HikariCP): λ = connection checkouts/s, E[S] = mean hold time, c = pool size. Pick the wait-probability and Wq limits from the caller's budget (illustrative: C(c,a) ≤ 0.05, Wq ≤ 2 ms).

**Erlang-C at a = 10 Erlangs** (M/M/c baseline; re-derived):

| c | ρ | C(c,10) | Wq / E[S] |
|---|---|---|---|
| 11 | 0.91 | 0.6821 | 0.682 |
| 13 | 0.77 | 0.2853 | 0.0951 |
| 15 | 0.67 | 0.1020 | 0.0204 |
| 20 | 0.50 | 0.0037 | 0.00037 |

Going from c = 11 to 13 cuts mean Wq about 7.2×. Erlang-C is a Poisson/exponential baseline, not a bound; for bursty arrivals or heavy-tailed service use Allen-Cunneen or simulate.

---

### P5 Priority-Queue Policy for Multi-Tier Traffic

**Decision**: separate interactive and batch traffic that share workers. Mean-wait formulas (single-server, non-preemptive): [05-priority-queues.md](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md). They are not c-worker or p99 results.

**DevOps mapping**:

- Priority must apply at the worker that serves the request. Priority at the load balancer with a shared FIFO thread pool behind it does nothing.
- Kubernetes `PriorityClass` and preemption act on pod **scheduling**, not request queues. Use them to keep interactive capacity schedulable; they do not reorder requests.
- Gateway/Nginx: separate upstream groups and rate-limit batch at ingress (`limit_req_zone`). The batch load cap is a policy choice (illustrative: ρ_batch ≤ 0.30).
- Kafka: separate topics or consumer groups per priority class so batch lag cannot delay interactive events.
- Starvation guard: reserve a capacity floor for low priority (illustrative: 10% via a token bucket). Low-priority wait grows without bound as total load approaches 1.

---

### P6 Jackson-Network Thinking for Microservice Topology

**Decision**: which service in a chain to scale. Flow-balance equations: [06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md).

**DevOps mapping**:

- Read per-service rates and routing fractions from the mesh (`istio_requests_total`) and service time from `istio_request_duration_milliseconds` or traces.
- Retries are routing. A 10% retry rate on each of 3 stages inflates load at the last stage by 1.1³ = 1.33×. Retry loops put feedback terms in the routing matrix; this is the mechanism behind retry storms. Retry budgets: see [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md).
- The bottleneck is the station with the highest ρᵢ; the chain ceiling is min(cᵢ·μᵢ). After scaling it, re-solve; the next station becomes the bottleneck. "Scaling didn't help" usually means the bottleneck moved to an unmonitored service.
- Alert on the bottleneck station's queue wait or queue depth against its SLO-derived budget, not on a fixed ρ.

---

### P7 Kingman Heavy-Traffic Approximation for Mean Queue Wait

**Decision**: how much burstiness and service-time spread add to mean wait. Formula and limits: [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md). Kingman is single-server. For c servers use Allen-Cunneen (Wq_GGc ≈ Wq_MMc × (CV²a + CV²s)/2), not Kingman with E[S]/c.

**Measuring inputs on a platform**:

- CV²_a: variance/mean² of event-level inter-arrival gaps. Binned RPS series do not identify it.
- CV²_s: variance/mean² of the raw service-time sample from APM traces. Do not infer it from p99/p50; percentile ratios do not identify the second moment.
- Mixed fast/slow paths (cache hit vs miss) are the usual source of high CV²_s.

**Levers**: smooth arrivals with an ingress token bucket (lower CV²_a); split heterogeneous work into size-class lanes (lower CV²_s). Both cut mean wait without adding capacity.

---

### P8 Bufferbloat Avoidance in Queue and Buffer Sizing

**Decision**: how deep to let a work queue grow before shedding. Mechanism: [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md).

**Wait vs drain** (keep these separate):

- A FCFS arrival behind backlog Q waits **Q/μ**. That is its latency.
- The backlog clears in **Q/(μ − λ)**. That is the drain time, not the latency.

**Size the queue limit from the delay budget**:

```
limit ≈ μ × (latency_budget − E[S])
```

Example: capacity μ = 100 req/s, budget 250 ms, E[S] = 50 ms → limit ≈ 20 queued requests. An unbounded backlog of 10,000 at the same μ makes the last caller wait 100 s instead of getting a fast 503/429.

**DevOps mapping**:

- controller-runtime: `MaxConcurrentReconciles` defaults to 1; one slow reconcile blocks the rest. Watch the `workqueue_depth` and queue-duration metrics.
- Kafka consumer lag is an application-layer buffer. At 500 msg/s consumed vs 600 msg/s produced, lag grows 100 msg/s. Alert on lag growth rate and on consumer delay (lag ÷ consume rate), not on absolute lag.
- Bounded in-process queues: `LinkedBlockingQueue(capacity)` in Java, `asyncio.Queue(maxsize=N)` in Python, with N from the formula above. Return 429 when full so latency debt becomes visible error-budget spend. For sojourn-time AQM (CoDel, adaptive LIFO) see [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md).

---

### P9 USL Retrograde Detection for Scaling Limits

**Decision**: whether adding replicas still adds throughput. Model and fitting: [09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md).

**DevOps mapping**:

- Load-test at several replica counts (for example N = 1, 2, 4, 8, 16) and fit σ and κ with `scipy.optimize.curve_fit`. Use enough points to see the curve bend.
- Example: σ ≈ 0, κ = 0.003 → N_max = √((1−σ)/κ) ≈ 18. Past that, throughput falls.
- κ sources on a platform: consensus rounds, distributed cache invalidation, leader election, cross-shard joins. Fix by sharding state or relaxing consistency where the SLO allows.
- σ sources: global mutexes, single-writer tables, single-partition topics. Fix by partitioning the serial resource.
- M/M/c assumes linear scaling. Check USL before any horizontal plan for a service with shared distributed state.

---

### P11 Fork-Join Sizing for Parallel-Only-at-Scale Stages

**Decision**: wall-clock time of sharded CI or scatter-gather calls. Theory: [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md).

E[max] = E[S]·H_K is exact only for iid exponential branch times with no waiting. For other distributions, correlated branches, or shared queues, simulate or model the joint maximum from aligned branch traces. There is no general correction factor.

| K | H_K |
|---|---|
| 2 | 1.50 |
| 5 | 2.28 |
| 10 | 2.93 |
| 20 | 3.60 |

**DevOps mapping** (numbers assume iid exponential; check against traces):

- CI sharding: 20 shards at mean 3 min → E[max] ≈ 10.8 min. Balance shard sizes and fix the slowest shard; that beats adding shards.
- Scatter-gather: 5 downstreams at mean 80 ms → E[max] ≈ 183 ms, so a 200 ms SLO is tight. Use per-call timeouts with partial-result fallback.
- Hedged requests: send a backup after the first request exceeds a high percentile (Dean & Barroso use the p95), only for idempotent calls. Hedging at p50 roughly doubles load.
- Tail at scale: if each branch is slow 1% of the time, 1−0.99^10 = 9.6% of 10-way and 63% of 100-way requests hit a slow branch.

---

## Anti-Patterns

### A1 M/M/1 Used at ρ Approaching 1 Without USL Check

Adding replicas when wait explodes near saturation helps only while scaling is near linear. If κ > 0, replicas past N_max lower throughput. Fit USL (P9) before large horizontal steps; a curve that bends down is κ, a curve that flattens is σ.

### A2 Little's Law Applied on Non-Stationary Windows

L = λW holds for long-run averages over a window where the system starts and ends in similar states. During spikes, rollouts, or recovery, in-flight counts, rates, and latencies over a short window will not agree (for example L = 500 measured vs λW = 200 × 0.1 = 20). Check it on stable, representative windows much longer than the service time; a persistent mismatch means a measurement mismatch (different populations) or an unstable system. See [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md).

### A3 Erlang-C and Erlang-B Confusion

Erlang-C is for systems where blocked arrivals wait; Erlang-B for systems where they are refused. Check the pool config: does a busy pool block the caller or error at once? Example at a = 20, c = 25: Erlang-C wait probability ≈ 0.209; Erlang-B blocking probability ≈ 0.050. They describe different systems; neither substitutes for the other. See [10-loss-systems-erlang-b.md](../../foundations-queueing-theory/assets/templates/queueing-theory/10-loss-systems-erlang-b.md).

- Erlang-B: WebRTC slots, pools that fail fast, license servers.
- Erlang-C: HTTP request queues, job schedulers, DB pools with a wait timeout > 0.

### A4 Fork-Join Sized by Mean Response Time

Completion time is the max of branch times. For iid exponential branches with mean 100 ms and K = 8, E[max] ≈ 272 ms (H₈ ≈ 2.718). For a percentile with iid branches of CDF F, solve F(t)^K = p. A fixed margin above the mean does not certify p99; replay aligned branch traces.

### A5 CV² of Service Time Ignored

High CV²_s (mixed cache-hit and DB paths) inflates mean wait above the M/M/c prediction. Measure CV²_s from raw service times. Worked single-server example: CV²_s = 4, CV²_a = 2 → VF = 3; to keep mean Wq ≤ 20 ms with E[S] = 10 ms needs ρ/(1−ρ) × 3 × 10 ms ≤ 20 ms, so ρ ≤ 0.40. Kingman gives the mean only; it does not explain a p99 gap. Fix structurally with fast/slow lanes.

---

## Recipes

### R1 Capacity Plan for a New Service

1. **Inputs**: λ_peak from projection or analog service; E[S] and CV²_s from staging traces; CV²_a from event-level arrivals. Sanity-check L = λ·E[S] against staging concurrency.
2. **Baseline c**: a = λ_peak·E[S]. Start at the square-root-staffing value c ≈ a + β√a and step c until Erlang-C mean Wq meets the queue share of the mean budget.
3. **Variability**: apply Allen-Cunneen (multiply the M/M/c Wq by (CV²_a + CV²_s)/2) and step c again, or reduce CV² via ingress smoothing or lanes. Validate means and tails by replay; see [trace-driven-simulation.md](../../foundations-queueing-theory/references/trace-driven-simulation.md).
4. **USL check**: for shared-state services, fit USL from load tests. If c > N_max, reduce σ/κ before scaling.
5. **HPA and alerts**: per-replica target = λ_peak / c. Alert on queue wait or depth crossing the budget-derived limit, plus direct p99/error-budget alerts. Choose the lead margin from measured scale-out delay.

**Output**: c with its assumptions, a Wq estimate with measured CV², a USL ceiling, and a derived HPA target.

### R2 Saturation SLO Threshold — Set the Alert Before the Cliff

1. Measure inter-arrival gaps and service durations for the same queue.
2. Set a mean latency budget B. Solve Wq(ρ) + E[S] = B with Kingman (one worker) or Allen-Cunneen (c workers). Derive p99 boundaries separately from load tests or replay.
3. Pick the alert margin from observed scale-out delay and response time, then validate lead time and false alarms against incident timelines.
4. Prefer a direct queue-depth or queue-wait gauge. Kafka lag (records) and delay (seconds) are different metrics.

**Synthetic single-server example**: E[S] = 20 ms, CV²_a = 2.5, CV²_s = 2.0, VF = 2.25, B = 200 ms. W(ρ) ≈ ρ/(1−ρ) × 45 ms + 20 ms: 155 ms at ρ = 0.75, 275 ms at ρ = 0.85, exactly 200 ms at ρ = 0.80. The mean boundary is 0.80 for this workload only; it says nothing about p99.

### R3 Multi-Stage Pipeline Bottleneck Hunt

1. **Collect** per-service γᵢ, routing Pᵢⱼ (retries included as extra routing), μᵢ = 1/E[Sᵢ], and cᵢ from the mesh or traces.
2. **Solve flow balance** (P6) for λᵢ; compute ρᵢ = λᵢ/(cᵢμᵢ); bottleneck = argmax ρᵢ; ceiling = min(cᵢμᵢ).
3. **Size the bottleneck** with R1 steps 2–3 against that station's share of the end-to-end budget.
4. **USL check** on the bottleneck if it shares distributed state.
5. **Re-solve** with the new cᵢ and find the next bottleneck; repeat while any station misses its budget.
6. **Mixed SLO classes** at the bottleneck: keep total load < 1 and apply P5; validate multi-worker behaviour by load test.

**Output**: per-service ρᵢ before and after, Δc per stage, a USL ceiling for the bottleneck, and where the bottleneck moves next.

---

## Composition Guide

| Concern | Pattern / Recipe | Foundation primitive |
|---|---|---|
| New service sizing | R1 | Little, M/M/c, Allen-Cunneen, USL |
| Existing pipeline bottleneck | R3 | Jackson, M/M/c, USL, priority |
| Alert threshold | R2 | Kingman / Allen-Cunneen, Little |
| Queue and buffer limits | P8 | Bufferbloat |
| Horizontal scaling sanity | P9 | USL |
| Multi-tier traffic | P5 | Priority queues |
| Fan-out / scatter-gather | P11 | Fork-join |

Brownfield order: R2 (pressure alerts) → P8 (bound queues, return 429) → R3 (bottleneck hunt) → R1 (apply at every new-service design review).

---

## Sources

- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- Whitt, W. (1993). "Approximations for the GI/G/m queue." *Production and Operations Management*, 2(2), 114–161.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer.
- Nichols, K. & Jacobson, V. (2012). "Controlling Queue Delay." *ACM Queue*, 10(5).
- Dean, J. & Barroso, L. A. (2013). "The Tail at Scale." *Communications of the ACM*, 56(2), 74–80.
- Google SRE Book (2016). Ch. 21, "Handling Overload." <https://sre.google/sre-book/handling-overload/>
- Kubernetes documentation: Horizontal Pod Autoscaler. <https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/>
