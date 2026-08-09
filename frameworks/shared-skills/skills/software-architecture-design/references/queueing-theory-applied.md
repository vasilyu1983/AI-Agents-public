# Queueing Theory Applied to Architecture

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Applied patterns, anti-patterns, and recipes that translate queueing-theory primitives into architecture decisions. Use this reference when sizing services, designing backpressure, allocating latency budgets, or detecting scaling limits.

Primitives live in [`foundations-queueing-theory`](../../foundations-queueing-theory/SKILL.md). This reference assumes familiarity with M/M/c, Kingman, USL, Jackson networks, and fork-join; it does not re-derive formulas — it shows how to apply them to real systems.

---

## Table of Contents

- [Patterns](#patterns)
  - [P1 — Service Sizing via M/M/c and Erlang-C](#p1--service-sizing-via-mmc-and-erlang-c)
  - [P2 — Backpressure Design from Jackson-Network Analysis](#p2--backpressure-design-from-jackson-network-analysis)
  - [P3 — Priority-Queue Routing for Multi-Tier Latency SLOs](#p3--priority-queue-routing-for-multi-tier-latency-slos)
  - [P4 — Bufferbloat Avoidance in Buffer Sizing](#p4--bufferbloat-avoidance-in-buffer-sizing)
  - [P5 — USL Detection of Architecture-Level Coherency Limits](#p5--usl-detection-of-architecture-level-coherency-limits)
  - [P6 — Kingman for Synchronous RPC Tail Latency](#p6--kingman-for-synchronous-rpc-tail-latency)
  - [P7 — Fork-Join for Parallel Scatter-Gather APIs](#p7--fork-join-for-parallel-scatter-gather-apis)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Queue Sizes Set "for Safety" Without Little's Law](#a1--queue-sizes-set-for-safety-without-littles-law)
  - [A2 — M/M/1 Modeling on Bursty Traffic (CV² Ignored)](#a2--mm1-modeling-on-bursty-traffic-cv-ignored)
  - [A3 — Priority Queues with Starvation Risk](#a3--priority-queues-with-starvation-risk)
  - [A4 — Coherency-Bound Architecture Scaled Past USL Inflection](#a4--coherency-bound-architecture-scaled-past-usl-inflection)
  - [A5 — Fork-Join Sized by Mean Worker Time](#a5--fork-join-sized-by-mean-worker-time)
- [Recipes](#recipes)
  - [R1 — Service-Sizing Playbook](#r1--service-sizing-playbook)
  - [R2 — Backpressure Topology Design](#r2--backpressure-topology-design)
  - [R3 — Tail-Latency Budget Allocation](#r3--tail-latency-budget-allocation)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 — Service Sizing via M/M/c and Erlang-C

**Problem**: how many replicas, threads, or connection-pool slots are needed to satisfy a wait-time SLO?

**Mechanism**: the M/M/c queue (Erlang-C formula) gives the probability C(c, a) that an arriving request must wait, and the mean wait Wq = C(c, a) / (c × μ − λ). Size c until Wq ≤ SLO_target.

**Architecture example — Kubernetes HTTP service**:

A checkout service receives λ = 600 req/s at peak. Each request spends E[S] = 50 ms on the server (μ = 20 req/s per pod). Offered load a = λ/μ = 30 Erlangs.

Minimum stable pods c_min = 31 (so ρ = 600/(31 × 20) = 0.968 — too close to 1). At c = 40: ρ = 0.75, Erlang-C gives C(40, 30) ≈ 0.055, Wq ≈ 0.055 / (40×20 − 600) = 0.055 / 200 ≈ 0.28 ms. Well inside a 5 ms wait SLO.

**Design rules**:
- Size for ρ ≤ 0.75 as steady-state ceiling. Erlang-C wait probability drops non-linearly below that.
- Always add one spare server beyond the computed minimum (the last server buys the most SLO margin at low ρ).
- After computing c from Erlang-C, apply a Kingman correction (see P6) if CV²_a > 1 or CV²_s > 1 — real traffic inflates Wq beyond what Erlang-C predicts.
- For connection pools (Postgres `pgBouncer`, HikariCP), use this pattern: pool_size = ceil(a) + headroom_servers, not a round number chosen intuitively.

**When to use**: new service capacity planning, autoscaler target configuration (set HPA min replicas = c from Erlang-C at median load, max replicas = c at 2× peak load), thread pool and connection pool sizing.

---

### P2 — Backpressure Design from Jackson-Network Analysis

**Problem**: a multi-stage pipeline (API → queue → worker → DB) degrades unpredictably under load. Scaling the wrong stage does not help.

**Mechanism**: Jackson's theorem treats each pipeline stage as an independent M/M/c queue, but the effective arrival rate at each stage is determined by flow-balance equations: λᵢ = γᵢ + Σⱼ λⱼ × Pⱼᵢ. The bottleneck is the stage with the highest ρᵢ. Backpressure applied at the bottleneck — or upstream of it — prevents queue accumulation throughout the network.

**Architecture example — async order pipeline**:

```
API ingress (γ = 200 req/s)
  → Validation worker pool (μ = 300 req/s, c = 1)   ρ = 0.67
  → Enrichment worker pool (μ = 150 req/s, c = 2)   ρ = 200/(2×150) = 0.67
  → Payment processor  (μ = 80 req/s, c = 3)        ρ = 200/(3×80) = 0.83 ← bottleneck
  → DB write (μ = 400 req/s, c = 1)                 ρ = 0.50
```

Payment processor is the bottleneck. Backpressure strategy:
1. Payment worker pool raises a `queue_depth` metric when its local queue exceeds BDP-equivalent depth.
2. Enrichment workers observe the downstream signal and shed incoming jobs with HTTP 429 / Kafka consumer pause.
3. API ingress rate-limits at the same signal, returning 503 to upstream callers.

**Design rules**:
- Identify the bottleneck before placing backpressure. Backpressure upstream of the bottleneck is correct; upstream of a fast stage is noise.
- After scaling the bottleneck stage (e.g. add a fourth payment worker: ρ = 200/(4×80) = 0.625), re-solve flow balance. The new bottleneck may be Enrichment or DB.
- Use finite queue sizes at each stage, sized to BDP-equivalent depth (see P4). Unbounded queues hide the bottleneck signal.
- Retry loops in microservices create feedback arcs that are not in the original flow-balance graph. Model retry rates explicitly: a 10% retry rate on failure at the Payment stage increases λ_payment by 10% above the external arrival rate.

**When to use**: any async pipeline where stages have independent scaling (Kafka-based microservices, SQS-backed Lambda chains, gRPC streaming pipelines). Not needed when the pipeline is a single-process in-memory call chain.

---

### P3 — Priority-Queue Routing for Multi-Tier Latency SLOs

**Problem**: interactive and batch workloads share the same worker pool. Interactive requests occasionally wait behind long-running batch jobs, breaking the interactive SLO without exceeding the aggregate utilization limit.

**Mechanism**: non-preemptive priority queues separate work into classes. A high-priority class 1 arrival waits at most one service period of the current low-priority job; once that completes, class 1 jumps the queue. The mean wait for class 1 is Wq_1 = W0 / (1 − ρ₁), where W0 is the residual service time of the in-progress job.

**Architecture example — LLM inference service**:

An inference API serves:
- **Class 1 (interactive)**: λ₁ = 10 req/s, E[S₁] = 0.5 s (chat responses)
- **Class 2 (async)**: λ₂ = 3 req/s, E[S₂] = 5.0 s (document summarization)

Without priority, at ρ = 0.75, both classes share a single wait distribution. A class 1 request arriving just after a 5-second batch job starts faces a 5-second wait — violating a 1-second interactive SLO.

With non-preemptive priority:
- Class 1 waits at most one E[S₂] period of in-progress work, then all queued class 1 jobs drain before any class 2 job is scheduled.
- GPU inference is not safely preemptible mid-token (stateful), so non-preemptive is the correct regime.

**Implementation**: separate job queues in Celery/Bull/Redis, with workers polling class 1 queue first (strict priority). Alternatively, maintain a single sorted-priority queue with class discrimination at the consumer.

**Design rules**:
- Apply priority end-to-end: ingress admission, queue insertion, and worker scheduler. Priority at the load balancer only, without priority at the worker, provides no protection.
- Monitor class 2 wait time separately. If class 2 p99 grows unboundedly, high-priority traffic is near capacity and starving the lower class (see A3).
- Reserve a minimum throughput floor for lower-priority classes: configure rate limiters on class 1 to prevent ρ₁ approaching 1.0, which causes class 2 starvation.
- For three or more SLO tiers (e.g. premium / standard / background), the starvation risk compounds. Validate that sum of ρ across all classes stays below 0.85.

**When to use**: whenever the same worker pool serves workloads with qualitatively different latency SLOs — inference services, video-encoding pipelines, database query schedulers, Kafka consumer partitions with mixed event types.

---

### P4 — Bufferbloat Avoidance in Buffer Sizing

**Problem**: an application queue is large by default or unbounded. Under spike traffic, requests queue up silently. Throughput looks healthy but p99 latency spikes to seconds or minutes.

**Mechanism**: buffer depth in time units D = buffer_size / service_rate. When D >> E[S] at steady-state utilization, the queue absorbs spikes without emitting backpressure signals. Callers never back off, the queue grows, and latency accumulates. The correct buffer is proportional to the Bandwidth-Delay Product (BDP): buffer ≈ RTprop × bottleneck_rate, or equivalently, the steady-state M/M/1 queue depth Lq = ρ² / (1 − ρ) with a small safety factor.

**Architecture example — Kafka consumer pipeline**:

A Kafka topic receives 5,000 msg/s. Consumer processes at 6,000 msg/s (ρ = 0.83). Topic retention is 24 hours — effectively unbounded buffer. During a marketing campaign spike at 9,000 msg/s for 10 minutes, 10 min × 60 s × (9,000 − 6,000) = 1,800,000 messages queue up. After the spike, the consumer takes 1,800,000 / (6,000 − 5,000) = 1,800 seconds = 30 minutes to drain. End-to-end message latency is 30 minutes, despite "normal" throughput after the spike.

Correct design:
1. Compute steady-state Lq ≈ 0.83² / (1 − 0.83) / 6000 ≈ 0.7 seconds of backlog at normal load.
2. Set a consumer lag alert at 2–3× Lq (a few seconds). Alert triggers producer flow control or horizontal consumer scale-out.
3. Apply a finite processing window deadline per message (e.g. 30 s). Messages exceeding the deadline are dead-lettered, not silently processed with stale data.

**Design rules**:
- Never use "unbounded" as a queue size without a documented reason and a compensating flow-control mechanism.
- For in-process queues (Java BlockingQueue, Python asyncio.Queue), default sizes of 0 (synchronous handoff) or small values (2–4× batch size) are safer than the default unbounded.
- A queue depth alert is a leading latency indicator. Queue depth × (1 / service_rate) = latency. Alert on depth before latency breaches — this is the difference between proactive and reactive SLO management.
- HTTP server backlogs (nginx `backlog`, Node.js server listen backlog) are also buffers. Size them to no more than a few seconds of arrival at the configured rate.

**When to use**: any system with explicit queues — async job systems (BullMQ, Sidekiq, Celery), message brokers (Kafka, SQS, RabbitMQ), thread pool queues, and HTTP server accept backlogs.

---

### P5 — USL Detection of Architecture-Level Coherency Limits

**Problem**: the team adds more Kubernetes pods, database replicas, or cache nodes, but throughput plateaus or drops. CPU and memory are not saturated.

**Mechanism**: the Universal Scalability Law models throughput as X(N) = λN / (1 + σ(N−1) + κN(N−1)). When κ > 0, there is a coherency cost — cross-node coordination, cache invalidation, distributed consensus, or global lock contention. Past N_max = sqrt((1 − σ) / κ), adding nodes actively reduces throughput.

**Architecture example — distributed session cache**:

A session service runs Redis Cluster. Load tests at increasing shard counts:

| Shards N | Throughput (req/s) |
|----------|--------------------|
| 1 | 50,000 |
| 2 | 96,000 |
| 4 | 176,000 |
| 8 | 290,000 |
| 16 | 370,000 |
| 32 | 340,000 ← retrograde |

Fitting USL: σ ≈ 0.02, κ ≈ 0.0008. N_max = sqrt(0.98 / 0.0008) ≈ 35 shards.

At N = 32, cluster gossip and key-routing overhead is the coherency cost κ. The architecture-level fix is not "add more shards" — it is to reduce cross-shard coordination: route requests to a preferred shard using consistent hashing (reduces gossip amplification), or partition session data by user cohort to reduce cross-shard invalidation.

**Design rules**:
- Run USL load tests before committing to a scale-out target. Fit σ and κ from at least 5 data points (N = 1, 2, 4, 8, 16 at minimum). Two data points are insufficient.
- A κ > 0.005 is a red flag: N_max is typically below 15, and the architecture has a structural coherency problem.
- Common coherency sources: distributed locking (ZooKeeper, etcd), strong-consistency replication (Raft, Paxos), cross-service session state, and shared writable caches.
- The fix is architectural: shard or partition the serialized resource, eliminate global state, or switch to eventual consistency at the boundary. Adding more nodes without fixing κ makes the problem worse past N_max.

**When to use**: pre-commit capacity planning for any shared-state architecture — database clusters, distributed caches, consensus services, and Kubernetes clusters under high API-server load.

---

### P6 — Kingman for Synchronous RPC Tail Latency

**Problem**: p99 latency on a synchronous RPC service is 3–5× higher than the mean, even at moderate utilization (ρ ≈ 0.70). M/M/1 analysis says latency should be fine.

**Mechanism**: Kingman's formula Wq ≈ (ρ / (1 − ρ)) × ((CV²_a + CV²_s) / 2) × E[S] shows that bursty arrivals (CV²_a > 1) and variable service times (CV²_s > 1) multiply the M/M/1 wait by the variability factor VF = (CV²_a + CV²_s) / 2. Real microservices commonly have CV²_a ≈ 2–4 (HTTP traffic is bursty) and CV²_s ≈ 2–8 (database-backed endpoints with variable query plans). At ρ = 0.70 and VF = 3, Wq is 3× the M/M/1 prediction.

**Architecture example — user-profile API**:

A user-profile service: λ = 140 req/s, E[S] = 5 ms, ρ = 0.70. Measured CV²_a = 2.5 (retries and load-balancer bursts), CV²_s = 3.5 (mix of cache hits at 1 ms and DB misses at 15 ms).

```
VF  = (2.5 + 3.5) / 2 = 3.0
Wq ≈ (0.70 / 0.30) × 3.0 × 5 ms = 35 ms
```

M/M/1 would predict Wq = (0.70/0.30) × 5 = 11.7 ms. Actual observed p99 ≈ 40 ms — consistent with Kingman (not M/M/1).

Architectural interventions ranked by impact:
1. **Reduce CV²_s**: split the service into a fast path (cache hit, < 2 ms) and a slow path (DB miss, 15 ms). Route independently. Reduces CV²_s from 3.5 to near 0 on each path.
2. **Reduce CV²_a**: enforce rate-limiting with token bucket at the ingress to smooth bursts. Reduces CV²_a from 2.5 toward 1.0.
3. **Reduce ρ**: scale out to c = 2 pods (ρ → 0.35). At ρ = 0.35, Wq = (0.35/0.65) × 3.0 × 5 = 8 ms — a 4× improvement from the same VF.

**Design rules**:
- Measure CV²_a and CV²_s from production histograms before sizing. Use the p99/p50 ratio as a quick proxy: if p99/p50 > 4, CV²_s is likely > 2.
- When designing SLO budgets, apply a VF of 2–3 for typical microservices. Allocate latency budget = Kingman Wq + E[S], not M/M/1 Wq + E[S].
- Splitting heterogeneous workloads into homogeneous fast/slow lanes is the highest-leverage architectural intervention for tail latency.

**When to use**: SLO design and capacity planning for any synchronous RPC service (REST, gRPC). Especially important when service time is bimodal (cache hit vs. miss, warm vs. cold path).

---

### P7 — Fork-Join for Parallel Scatter-Gather APIs

**Problem**: an API aggregates responses from K downstream services in parallel (scatter-gather / fan-out pattern). Latency is higher than expected, and adding more parallel calls makes it worse.

**Mechanism**: fork-join completion time is bounded by the slowest worker. For K independent workers with exponential service time E[S], the expected completion time is E[max] = E[S] × H_K, where H_K is the K-th harmonic number. H_5 ≈ 2.28, H_10 ≈ 2.93. Latency grows logarithmically with K — diminishing returns on parallelism — but the p99 of the maximum grows faster than the mean.

**Architecture example — product-detail API**:

An e-commerce product page aggregates:
- Inventory service: E[S] = 30 ms
- Pricing service: E[S] = 40 ms
- Reviews service: E[S] = 60 ms
- Recommendations service: E[S] = 80 ms
- Media CDN check: E[S] = 20 ms

K = 5 calls, E[S_max] ≈ 80 ms (slowest service dominates). Using the H_K bound on the slowest service: E[max] ≈ 80 × H_5 = 80 × 2.28 = 182 ms. With worker utilization ρ = 0.5 at each service, queueing adds further delay.

For a 200 ms p50 SLO, this is tight. For 300 ms p99, it is probably violated.

Architectural interventions:
1. **Mandatory vs. optional calls**: classify each downstream call. Only mandatory calls block the response. Optional calls (recommendations) run in parallel but are returned as best-effort if they exceed a deadline.
2. **Timeout + hedge**: set a per-call timeout at 1.5× E[S] of that service. Issue a hedge request (duplicate call to a second instance) for the slowest service after 1× E[S], cancel the slower one when the first responds.
3. **Reduce K**: cache recommendations and media status client-side; eliminate those calls from the hot path. Reduce K from 5 to 3; H_3 ≈ 1.83, expected max drops proportionally.
4. **Bound CV²_s at slow workers**: Reviews service has high variance. Cache reviews with short TTL; serve stale on miss (reduces E[S] and CV²_s).

**Design rules**:
- Size fork-join by E[max] = E[S_slowest] × H_K, not by the mean of any individual service.
- For p99 SLOs, the tail of the maximum is heavier than the mean. Use simulation or extreme-value bounds (Gumbel distribution) for p99 sizing.
- Never add more parallel calls to reduce latency past K ≈ 8–10. H_K grows slowly (H_20 ≈ 3.60); additional calls add stragglers without proportional benefit.
- Speculative execution (issue duplicate request to second instance after a hedge timeout) is the most effective p99 fix for fork-join — it trades a small throughput cost for a large tail reduction.

**When to use**: any scatter-gather or fan-out API design — BFF (Backend for Frontend) aggregation, GraphQL resolver parallelism, ML ensemble inference, CI test sharding.

---

## Anti-Patterns

### A1 — Queue Sizes Set "for Safety" Without Little's Law

**Symptom**: a developer sets an application queue size to a large round number (e.g. `queue_size=10000`) to "avoid dropping requests." Under sustained load, the queue fills silently, p99 latency grows to minutes, and callers time out while the system reports healthy throughput.

**Root cause**: queue size is set without asking "what latency does this depth imply?" Little's Law answers directly: L = λ × W. A queue of 10,000 items at λ = 200 req/s implies W = 50 seconds of latency before a newly arriving request is processed. This violates virtually any user-facing SLO.

**Diagnosis**: compute the implied wait time for the maximum queue depth: W_max = queue_size / λ. If W_max exceeds the SLO by more than a factor of 3, the queue size is wrong.

**Fix**: compute the correct queue depth from steady-state Lq = ρ² / (1 − ρ) and add a 2–3× safety buffer. Set an alert when queue depth exceeds 1× Lq — this is a leading indicator of latency SLO breach. When the queue is full, emit a backpressure signal (429, NACK, consumer pause) rather than silently accepting.

---

### A2 — M/M/1 Modeling on Bursty Traffic (CV² Ignored)

**Symptom**: capacity planning uses M/M/1 to set the number of servers. The model says the service handles the load at ρ = 0.70 with acceptable latency. In production, p99 is 3–5× higher than the model predicts.

**Root cause**: M/M/1 assumes Poisson arrivals (CV²_a = 1) and exponential service times (CV²_s = 1). Real HTTP traffic is bursty (CV²_a often 2–5, from load balancer bursts, retry storms, and frontend batching). Real service times are bimodal (CV²_s often 2–8, from cache hit/miss mix). Kingman's formula shows that Wq scales linearly with VF = (CV²_a + CV²_s) / 2. Ignoring VF = 3 means the capacity model is 3× optimistic.

**Diagnosis**: measure CV²_a and CV²_s from production latency histograms. Compute VF. If VF > 1.5, M/M/1 is an unreliable model for this system.

**Fix**: use Kingman's formula for initial sizing. If CV²_a > 1 and arrivals are Poisson-ish, apply the M/G/1 Pollaczek-Khinchine formula for higher accuracy. For sizing at ρ > 0.8, always validate with load test rather than relying on any analytic model.

---

### A3 — Priority Queues with Starvation Risk

**Symptom**: after introducing priority queues to protect interactive workloads, background jobs take hours or never complete. SLA with downstream consumers is violated. Under load, all workers are serving high-priority traffic.

**Root cause**: non-preemptive priority queuing guarantees class 1 (high priority) service ahead of class 2 (low priority) as long as class 1 arrivals exist. When ρ₁ approaches 1.0 — or when the combined utilization ρ₁ + ρ₂ > 1 — the server is always busy with high-priority work and class 2 never drains. This is queueing-theoretic starvation.

**Diagnosis**: compute ρ₁ = λ₁ × E[S₁]. If ρ₁ > 0.85, class 2 starvation risk is high. Monitor class 2 queue depth and age-of-oldest-job separately from class 1.

**Fix**:
- Rate-limit class 1 to cap ρ₁ ≤ 0.70, leaving guaranteed capacity for class 2.
- Implement aging: a class 2 job waiting longer than a threshold is promoted to class 1 priority.
- Alternatively, use weighted fair queuing (WFQ) instead of strict priority: assign class 1 a weight of 4 and class 2 a weight of 1. Class 1 gets 80% of throughput; class 2 always gets 20%.

---

### A4 — Coherency-Bound Architecture Scaled Past USL Inflection

**Symptom**: the team doubles the number of database replicas or cache nodes to handle read load. Throughput is lower after the scale-out event than before. Infrastructure cost doubles, performance regresses.

**Root cause**: the system has non-trivial coherency cost κ > 0 in USL terms. N_max = sqrt((1 − σ) / κ) has already been exceeded. Common sources: strong-consistency replication (each write must be acknowledged by all replicas), distributed locking, cache coherency (each write invalidates all replicas), and consensus (Raft with N followers). Past N_max, the coordination overhead grows as O(N²) via the κN(N−1) term.

**Diagnosis**: run load tests at N = 1, 2, 4, 8 nodes. If throughput growth is sub-linear and decelerating rapidly, fit USL. Compute N_max. If current deployment count is above N_max, the architecture is in retrograde.

**Fix**: the fix is architectural, not operational.
- Reduce κ: switch from synchronous strong-consistency replication to asynchronous replication for read-heavy paths. Accept eventual consistency on reads.
- Shard the serialized resource: if a global lock is the coherency source, partition it so each shard has independent locking.
- Reduce σ: identify the serialized critical section (Amdahl bottleneck) and parallelize or remove it.
- Scaling out past N_max without reducing κ makes the problem worse. Stop scaling; fix the architecture first.

---

### A5 — Fork-Join Sized by Mean Worker Time

**Symptom**: the team designs a scatter-gather API with K = 8 downstream calls, each with E[S] = 100 ms. The SLO is 300 ms p99. Load testing shows p99 consistently at 450–600 ms.

**Root cause**: the design assumed completion time ≈ E[S] = 100 ms (parallel = fast). The actual completion time is E[max] = E[S] × H_K = 100 × H_8 = 100 × 2.72 = 272 ms for the mean. The p99 of the maximum is significantly higher, especially when one worker has high CV²_s (variable service time) or high ρ (own queue congestion).

**Diagnosis**: compute E[max] = E[S_slowest] × H_K. If E[max] > 0.5 × SLO, the p99 will likely violate the SLO under load. Identify which worker has the highest CV²_s.

**Fix**:
- Apply the harmonic-number correction in capacity planning. Design for E[max], not E[S].
- Implement hedge requests for the worker with the highest CV²_s: issue a duplicate call after 1.5 × E[S], cancel the loser.
- Mark non-critical calls as optional: return a response when mandatory calls complete; fill optional data asynchronously or from cache.
- If K is large (> 8), question whether all calls are necessary on every request. Prefetch, cache, or paginate optional data.

---

## Recipes

### R1 — Service-Sizing Playbook

**Goal**: given a traffic forecast, determine the number of replicas (pods, threads, workers) that satisfies the wait-time SLO at peak load.

**Steps**:

1. **Measure inputs**: collect λ (arrivals/s at peak), E[S] (mean service time), CV²_s (service-time variance), CV²_a (inter-arrival variance). Source from APM histograms (p50 and p99 give a rough CV² estimate: CV²_s ≈ (p99/p50 − 1)^2 / 4 as a heuristic).

2. **Compute offered load and minimum stable pool**:
   ```
   a = λ / μ  where μ = 1 / E[S]
   c_min = ceil(a) + 1   (stability requires ρ < 1)
   ```

3. **Run Erlang-C at candidate pool sizes**: for c = c_min to c_min + 20:
   ```
   ρ = λ / (c × μ)
   C(c, a) = [ (a^c / c!) × 1/(1−ρ) ] / [ Σ(a^k/k!, k=0..c-1) + (a^c/c!) × 1/(1−ρ) ]
   Wq = C(c, a) / (c × μ − λ)
   ```
   Find the smallest c such that Wq ≤ SLO_wait.

4. **Apply Kingman correction** for real traffic variability:
   ```
   VF = (CV²_a + CV²_s) / 2
   Wq_real ≈ Wq_erlang × VF
   ```
   If Wq_real > SLO_wait, increase c until Wq_real / VF fits the SLO window. This is the corrected minimum pool size.

5. **Apply safety margin**: add one server beyond the VF-corrected minimum. Set this as the autoscaler minimum replica count. Configure HPA scale-up trigger at ρ = 0.70 (not CPU 80%).

6. **SLO check**: verify that E[S] + Wq_real ≤ end-to-end latency budget for this service (accounting for network overhead and downstream latency).

**Example** — order validation service:
- λ = 200 req/s, E[S] = 20 ms, μ = 50 req/s per pod, a = 4.0 Erlangs
- c_min = 5 pods (ρ = 0.80 at 5 pods)
- Erlang-C at c = 6: ρ = 0.67, C(6, 4) ≈ 0.09, Wq ≈ 0.09/(6×50 − 200) = 0.09/100 = 0.9 ms
- CV²_a = 2.0, CV²_s = 2.0, VF = 2.0
- Wq_real ≈ 0.9 × 2 = 1.8 ms
- Total W = 1.8 + 20 = 21.8 ms, well inside a 50 ms SLO
- Safety: set minimum pods = 7 (c_corrected + 1)

**Strongest outcome**: the VF correction (step 4) prevents the most common failure mode — a service that passes pre-production load tests (low CV²) but violates SLO in production (high CV²).

---

### R2 — Backpressure Topology Design

**Goal**: design the flow-control topology for a multi-stage async pipeline so that overload at any bottleneck stage is absorbed by the correct upstream stage, not silently queued.

**Steps**:

1. **Map the pipeline as a Jackson network**: draw each stage as a node. Record γᵢ (external arrivals), μᵢ (service rate per worker), cᵢ (worker count), and routing probabilities Pᵢⱼ including retry arcs.

2. **Solve flow-balance equations**:
   ```
   λᵢ = γᵢ + Σⱼ λⱼ × Pⱼᵢ
   ρᵢ = λᵢ / (cᵢ × μᵢ)
   ```
   Rank stages by ρᵢ. The highest ρᵢ is the bottleneck. Note any retry-amplification arcs that increase effective λ.

3. **Place finite queues at the bottleneck and one stage upstream**:
   - Bottleneck stage: queue_depth = Lq_bottleneck × 2 (steady-state M/M/c queue depth with a 2× buffer).
   - One upstream stage: queue_depth = same rule applied to that stage.
   - All other stages: also bounded, but a more generous bound is acceptable since they are not the bottleneck.

4. **Define the backpressure signal**: when the bottleneck queue depth exceeds 1× Lq_bottleneck (the steady-state expected depth), the bottleneck emits a signal:
   - Synchronous: HTTP 429 / gRPC RESOURCE_EXHAUSTED
   - Async (Kafka): pause consumer assignment on the upstream topic
   - Internal: upstream worker sleeps (credit-based or semaphore-based flow control)

5. **Propagate the signal upstream**: each stage observes the downstream backpressure signal and propagates it to its own upstream. Ingress (API gateway or producer) sees the signal and either sheds load (503 to clients) or applies rate limiting.

6. **Re-solve after scaling the bottleneck**: if adding cᵢ workers at the bottleneck reduces ρᵢ below 0.70, re-run step 2. Verify the new bottleneck is not a previously underprovisioned stage.

**Example** — image processing pipeline:
- Ingress (γ = 50 img/s) → Resize (μ = 80/s, c=1, ρ=0.63) → ML inference (μ = 40/s, c=2, ρ=0.63) → Storage write (μ = 200/s, c=1, ρ=0.25)
- Both Resize and ML inference have similar ρ. But ML inference has CV²_s ≈ 4 (model inference is variable).
- Kingman Wq at ML inference ≈ (0.63/0.37) × (1+4)/2 × 25ms ≈ 106 ms — ML inference is the effective bottleneck under variability.
- Backpressure: ML inference worker emits pause signal to Resize when its local queue exceeds 5 jobs (Lq ≈ 2.7 at ρ=0.63, 2× = 5). Resize worker pauses and emits 429 to ingress. Ingress rate-limits at the source.

---

### R3 — Tail-Latency Budget Allocation

**Goal**: given a top-level end-to-end latency SLO (e.g. 500 ms p99), allocate a per-component latency budget and define an escalation policy when a component breaches its budget.

**Steps**:

1. **Establish the end-to-end budget**: SLO_e2e = total allowed latency at the chosen percentile (e.g. 500 ms p99). Subtract fixed network overhead (RTprop): budget_available = SLO_e2e − Σ(network_hops × RTprop).

2. **Map synchronous call graph**: identify all serial components in the critical path (each adds to latency). Parallel branches (fork-join) contribute max(branches), not sum.
   - For serial stages: budget_total = Σ(budget_i)
   - For parallel stages: budget_total = max(budget_i over parallel branches) + join_overhead

3. **Apply Kingman sizing per component**: for each serial component with known λᵢ, E[Sᵢ], CV²_aᵢ, CV²_sᵢ:
   ```
   VF_i = (CV²_ai + CV²_si) / 2
   Wq_i = (ρ_i / (1 − ρ_i)) × VF_i × E[S_i]
   W_i  = Wq_i + E[S_i]
   ```
   The component-level budget allocation is budget_i = W_i (with headroom factor 1.2–1.5× for tail).

4. **Check budget feasibility**: if Σ(budget_i for serial path) > budget_available, the allocation is infeasible. Options:
   - Increase server count at the highest-Wq component to reduce ρ.
   - Move a serial component to an async path (decouple it from the critical path).
   - Challenge whether the SLO_e2e is achievable given the workload characteristics.

5. **Define the escalation policy**: for each component, define three operating zones:
   - **Green** (ρ < 0.65): W_i within budget. No action.
   - **Yellow** (ρ 0.65–0.80): Kingman Wq approaching budget. Alert; prepare scale-out.
   - **Red** (ρ > 0.80 or Wq > budget_i): budget breached. Trigger autoscaler or manual incident.

6. **For fork-join branches**: apply the harmonic-number correction:
   - budget_parallel = E[S_slowest] × H_K × VF_slowest
   - If budget_parallel > allocated parallel branch budget, apply hedge timeout on the slowest worker.

**Example** — payment checkout flow:

SLO: 800 ms p99. Network overhead: 3 hops × 1 ms = 3 ms. Budget: 797 ms.

| Component | E[S] | ρ | VF | Wq (Kingman) | W | Budget |
|-----------|------|---|----|-------------|---|--------|
| API gateway | 2 ms | 0.40 | 1.5 | 2 ms | 4 ms | 10 ms |
| Auth service | 5 ms | 0.55 | 2.0 | 12 ms | 17 ms | 25 ms |
| Cart service | 10 ms | 0.60 | 2.5 | 37 ms | 47 ms | 60 ms |
| Payment gateway (external) | 200 ms | — | — | — | 200 ms | 250 ms |
| DB write | 8 ms | 0.50 | 2.0 | 16 ms | 24 ms | 20 ms |
| **Total serial** | | | | | **292 ms** | **365 ms** |

Budget consumed: 292 ms (mean) vs. 797 ms available. Headroom is sufficient for p99 tail at the whole-flow level. Note, however, that the DB write row's own Kingman-corrected W (24 ms) exceeds its allocated 20 ms budget — this is exactly the case the escalation policy in step 5 should catch even when the aggregate SLO still has headroom; either raise the DB write's budget allocation, reduce its VF (e.g. by fixing connection-pool contention), or add a server. External payment gateway is the dominant component; hedge it with a 400 ms timeout and a fallback to async confirmation.

**Strongest outcome**: step 3 (Kingman per component) reveals that the Cart service — not the external gateway — has the highest queue-induced latency relative to its E[S]. Reducing CV²_s at Cart (split cache-hit vs. DB-miss paths) drops Wq from 37 ms to ~12 ms, cutting p99 more than doubling Cart's server count would.

---

## Composition

The patterns in this reference compose as follows:

| Starting point | Natural next step |
|---------------|-------------------|
| P1 (M/M/c sizing) | Apply P6 (Kingman VF correction) before finalizing c; check P5 (USL) before scaling past 8 pods |
| P2 (backpressure topology) | Apply P4 (bufferbloat / finite queue depth) at each stage; P3 (priority) if multiple SLO classes share the bottleneck |
| P3 (priority queues) | Monitor starvation risk (A3); validate combined ρ stays below 0.85 |
| P5 (USL coherency) | Fix architecture before returning to P1 for re-sizing; re-run USL after reducing κ |
| P7 (fork-join) | Size each worker branch with P1 + P6; apply timeout and hedge for p99 SLO |
| R1 (sizing playbook) | Feeds into R3 (tail-latency budget) as the per-component W_i values |
| R2 (backpressure topology) | Depends on R1 for correct queue depth targets at each stage |
| R3 (tail-latency budget) | Depends on P6 Kingman values per component; uses P7 for parallel branches |

**Anti-patterns as guards**: run A1 (Little's Law check on queue depth) and A2 (CV² check) before publishing any capacity plan. Run A4 (USL retrograde check) before any scale-out decision for shared-state services. Run A5 (harmonic-number check) before approving any fan-out design.

---

## Sources

- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer.
- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11).
- Nelson, R. & Tantawi, A. N. (1988). "The Approximate Analysis of Fork/Join Synchronization in Parallel Queues." *IEEE Transactions on Computers*, 37(6), 739–743.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Kleinrock, L. (1976). *Queueing Systems, Vol. 2: Computer Applications*. Wiley-Interscience.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- Dean, J. & Ghemawat, S. (2008). "MapReduce: Simplified Data Processing on Large Clusters." *CACM*, 51(1), 107–113.
- [`foundations-queueing-theory`](../../foundations-queueing-theory/SKILL.md) — canonical primitive definitions, formulas, and worked examples for all models referenced here.
