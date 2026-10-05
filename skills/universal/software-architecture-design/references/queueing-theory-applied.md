# Queueing Theory Applied to Architecture

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. If the foundation's skip-conditions fire, use the foundation it routes to.

This file maps queueing results to architecture decisions: replica and pool sizing, backpressure, buffer bounds, scale-out limits, fan-out, and latency budgets. It does not restate the theory. Formulas, assumptions, and derivations live in the foundation:

| Primitive | Owner |
|-----------|-------|
| Little's Law | [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) |
| M/M/c, Erlang-C | [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md) |
| M/G/1 (Pollaczek-Khinchine) | [04-mg1-pollaczek-khinchine.md](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) |
| Priority queues | [05-priority-queues.md](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md) |
| Jackson networks | [06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) |
| Kingman (single server) | [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) |
| Bufferbloat | [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md) |
| USL | [09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md) |
| Fork-join | [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md) |
| Allen-Cunneen G/G/c, square-root staffing, pooling, overload, retries, fan-out tails | [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md) |

Two rules apply everywhere below:

- **No portable utilization target.** Derive c (and so ρ) from the SLO and measured variability, using Erlang-C/Allen-Cunneen or square-root staffing (c ≈ a + β√a). Any ρ figure below is illustrative.
- **Measure CV² directly.** Compute CV²_s = Var(S)/E[S]² from a service-time sample. The p99/p50 ratio does not identify the second moment.

---

## Table of Contents

- [Patterns](#patterns): P1 sizing · P2 backpressure · P3 priority · P4 buffer bounds · P5 USL · P6 variability · P7 fork-join
- [Anti-Patterns](#anti-patterns): A1–A5
- [Recipes](#recipes): R1 sizing · R2 backpressure topology · R3 latency budget
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 — Service Sizing via M/M/c and Erlang-C

**Decision**: how many replicas, threads, or pool slots meet a wait-time SLO.

**Example (Kubernetes HTTP service)**: λ = 600 req/s, E[S] = 50 ms (μ = 20/s per pod), a = 30 Erlangs. Erlang-C Wq by pod count:

| c | ρ | Wq |
|---|---|----|
| 31 | 0.97 | 40 ms |
| 34 | 0.88 | 4.7 ms |
| 35 | 0.86 | 2.8 ms |
| 40 | 0.75 | 0.28 ms (C(40,30) ≈ 0.055) |

For a 5 ms mean-wait SLO under Poisson/exponential assumptions, c = 34 is the minimum. Erlang-C is a baseline, not a bound: if measured CV²_a or CV²_s ≠ 1, scale with Allen-Cunneen (Wq ≈ Wq_M/M/c × (CV²_a + CV²_s)/2) or simulate.

**Design rules**:
- Connection and thread pools: size from the same calculation, not a round number.
- Autoscaler minimum = c at the forecast floor load; maximum = c at forecast peak plus the SLO's variability allowance. Scale on queue wait or in-flight count, not CPU alone.
- At high ρ, validate any analytic c with a load test.

---

### P2 — Backpressure Design from Jackson-Network Analysis

**Decision**: which stage of a multi-stage pipeline to scale or throttle. Solve flow balance (λᵢ = γᵢ + Σⱼ λⱼPⱼᵢ), rank stages by ρᵢ, and treat the highest as the bottleneck ([06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md)).

**Example (async order pipeline, γ = 200 req/s)**:

```
Validation  (μ = 300/s, c = 1)  ρ = 0.67
Enrichment  (μ = 150/s, c = 2)  ρ = 0.67
Payment     (μ = 80/s,  c = 3)  ρ = 0.83  ← bottleneck
DB write    (μ = 400/s, c = 1)  ρ = 0.50
```

Backpressure: Payment signals when its queue wait exceeds its delay budget; Enrichment sheds (429 / consumer pause); ingress rate-limits (503).

**Design rules**:
- Place backpressure at or upstream of the bottleneck. After scaling it (a fourth Payment worker gives ρ = 0.625), re-solve flow balance; the bottleneck may move.
- Bound every stage queue from its delay budget (see P4). Unbounded queues hide the bottleneck.
- Model retries as extra arcs: a 10% retry rate at Payment raises λ_payment by 10%. Retry amplification and retry budgets: [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md).

**When to use**: independently scaled async stages (Kafka microservices, SQS-backed Lambda chains, gRPC streaming). Not needed for an in-process call chain.

---

### P3 — Priority-Queue Routing for Multi-Tier Latency SLOs

**Decision**: protect an interactive class that shares workers with long batch jobs.

**Example (LLM inference service)**: class 1 interactive, λ₁ = 10 req/s, E[S₁] = 0.5 s; class 2 async, λ₂ = 3 req/s, E[S₂] = 5 s. Offered load is 5 + 15 = 20 Erlangs, so this is a pool. Without priority, a chat request can queue behind 5-second summarization jobs. With non-preemptive priority, a class 1 arrival waits for the residual of jobs in service plus queued class 1 work only; class 2 queued work is skipped. Mean waits by class: [05-priority-queues.md](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md).

GPU inference is costly to preempt mid-generation, so non-preemptive is the usual regime.

**Design rules**:
- Apply priority end to end: admission, queue insertion, and worker scheduling. Priority at the load balancer alone does nothing.
- Monitor class 2 wait and age-of-oldest-job separately. Unbounded growth means class 1 load is starving class 2 (A3).
- Cap class 1 with a rate limiter so the remaining capacity meets the class 2 SLO. Derive the cap from class 2's throughput and delay requirements, not a fixed ρ.
- Implementation: separate queues polled class 1 first (Celery/BullMQ/Redis), or one priority-sorted queue.

---

### P4 — Buffer Bounds and Bufferbloat

**Decision**: how deep an application queue or broker backlog may grow before it signals.

**Mechanism**: a FCFS arrival behind backlog Q waits Q/μ. The backlog drains in Q/(μ − λ). These are different numbers. Size a queue from its delay budget: **limit ≈ μ × (latency budget − E[S])**, with μ the stage's total service rate. Theory: [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md).

**Example (Kafka consumer)**: λ = 5,000 msg/s, μ = 6,000 msg/s (ρ = 5/6), 24 h retention (effectively unbounded). A 10-minute spike at 9,000 msg/s builds 600 s × 3,000 = 1.8M messages of lag.
- Peak wait at spike end: 1.8M / 6,000 = **300 s** (5 minutes).
- Drain time: 1.8M / (6,000 − 5,000) = 1,800 s (30 minutes). Waits fall from 300 s toward zero over that period.
- Steady-state M/M/1 Lq = ρ²/(1 − ρ) ≈ 4.2 messages ≈ **0.69 ms** of work (Lq/μ); the mean queue wait is Wq = Lq/λ ≈ 0.83 ms. Normal lag is near zero, so steady-state Lq is no basis for an alert.

Correct design:
1. Pick a freshness budget, e.g. 30 s. Alert when lag / consumption rate exceeds it: here lag > 6,000 × 30 = 180,000 messages. The alert triggers consumer scale-out or producer flow control.
2. Give messages a processing deadline (e.g. 30 s). Dead-letter expired messages instead of processing stale data.

**Design rules**:
- Do not leave a queue unbounded without a documented reason and a flow-control mechanism.
- In-process queues (BlockingQueue, asyncio.Queue): bound them from the delay budget; a synchronous handoff (size 0) is often fine.
- Alert on queue depth ÷ service rate (the implied wait). It leads latency.
- HTTP accept backlogs (nginx `backlog`, listen backlog) are buffers too. Bound them the same way.

---

### P5 — USL Detection of Architecture-Level Coherency Limits

**Decision**: whether adding nodes will raise throughput. Model and fitting: [09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md).

**Example (Redis Cluster session service)**:

| Shards N | 1 | 2 | 4 | 8 | 16 | 32 |
|----------|---|---|---|---|----|----|
| Throughput (req/s) | 50,000 | 96,000 | 176,000 | 290,000 | 370,000 | 340,000 |

A least-squares USL fit gives σ ≈ 0.034, κ ≈ 0.0027, N_max = √((1 − σ)/κ) ≈ 19. Throughput at 32 is past the peak. The fix is architectural: cut cross-shard coordination (consistent-hash routing, partition sessions by cohort), not more shards.

**Design rules**:
- Fit σ and κ from at least 5 load levels before committing to a scale-out target.
- Coherency sources: distributed locks (ZooKeeper, etcd), synchronous replication and consensus (Raft, Paxos), shared writable caches, cross-service session state.
- Fix κ by partitioning the serialized resource, removing global state, or relaxing consistency at the boundary. Scaling past N_max without that makes throughput worse.

---

### P6 — Variability and Synchronous RPC Wait

**Decision**: why a moderately loaded RPC service misses its latency SLO, and which lever to pull. Single-server Kingman: [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md). Multi-server: Allen-Cunneen in [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md).

**Example (user-profile API, one server)**: λ = 140 req/s, E[S] = 5 ms, ρ = 0.70. Measured CV²_a = 2.5 (retries, LB bursts) and CV²_s = 3.5 (computed from the service-time sample).

```
VF = (2.5 + 3.5) / 2 = 3.0
Kingman Wq ≈ (0.70/0.30) × 3.0 × 5 ms = 35 ms   (M/M/1: 11.7 ms)
```

These are mean waits. Do not compare them with an observed p99.

Levers:
1. **Split workloads**: separate cache-hit and DB-miss lanes. Each lane has lower CV²_s than the mix.
2. **Smooth arrivals**: token-bucket ingress lowers CV²_a toward 1.
3. **Add a server**: at c = 2 (ρ = 0.35 per server), Allen-Cunneen gives Wq ≈ 0.18 / (400 − 140)/s × 3.0 ≈ 2.1 ms. Do not reuse the single-server formula with ρ halved.

**Design rules**:
- Measure CV²_a and CV²_s before sizing. Budget latency as Wq(with VF) + E[S].
- Bimodal service times (hit/miss, warm/cold) are the main case for lane splitting.

---

### P7 — Fork-Join for Parallel Scatter-Gather APIs

**Decision**: how fan-out width and the slowest dependency set response time. Response time is the maximum of the branch times. E[max] = E[S] × H_K holds exactly only for K iid exponential branches with no queueing. Otherwise compute or simulate the maximum: [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md).

**Example (product-detail API)**: five parallel calls with means 30, 40, 60, 80, 20 ms. If each were independent exponential, E[max] ≈ 117 ms by inclusion-exclusion (illustrative; real latency distributions differ). Dropping recommendations and media from the hot path leaves 30/40/60 ms and E[max] ≈ 82 ms. Queueing at each dependency adds more.

Interventions:
1. **Mandatory vs optional calls**: only mandatory calls block the response; optional ones return best-effort by a deadline.
2. **Hedged requests**: send a second request after the first has been outstanding longer than the dependency's p95 latency, and cancel the loser (Dean & Barroso 2013).
3. **Reduce K**: cache or prefetch data that does not need a live call.
4. **Cut variance at the slow branch**: short-TTL caching, serve stale on miss.

**Design rules**:
- Size by the distribution of the maximum, not by any branch mean. For p99, simulate from measured branch distributions.
- Each extra branch adds a chance of a straggler: with a 1% slow-call rate per branch, 1 − 0.99¹⁰ = 9.6% of 10-way requests hit one, and 1 − 0.99¹⁰⁰ = 63% of 100-way requests. Tail-at-scale detail: [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md).

**When to use**: BFF aggregation, GraphQL resolver fan-out, ML ensembles, sharded search, CI test sharding.

---

## Anti-Patterns

### A1 — Queue Sizes Set "for Safety" Without Little's Law

**Symptom**: `queue_size=10000` to "avoid drops". Under sustained load the queue fills, callers time out, throughput looks healthy.

**Diagnosis**: implied wait = queue depth / service rate. At 200 req/s, 10,000 queued items is a 50 s wait for the last arrival.

**Fix**: set the bound from the delay budget: limit ≈ μ × (latency budget − E[S]). For example, 250 req/s capacity, 1 s budget, E[S] = 50 ms gives about 237 slots. When full, signal backpressure (429, NACK, consumer pause) instead of accepting silently.

---

### A2 — M/M/1 Modeling on Bursty Traffic (CV² Ignored)

**Symptom**: the capacity model says latency is fine; production waits are several times higher.

**Root cause**: M/M/1 and Erlang-C assume CV²_a = CV²_s = 1. Wait scales roughly with (CV²_a + CV²_s)/2, so measured variability above 1 makes the model optimistic by that factor.

**Fix**: measure CV²_a and CV²_s from samples. Use Kingman (one server), Allen-Cunneen (c servers), or P-K for Poisson arrivals with general service. At high ρ, validate with a load test.

---

### A3 — Priority Queues with Starvation Risk

**Symptom**: after adding priority, background jobs never finish.

**Root cause**: under strict priority, class 2 gets only the capacity class 1 leaves. When class 1 load approaches capacity, or total load exceeds it, class 2 starves.

**Diagnosis**: compare class 1 offered load with capacity; track class 2 queue depth and oldest-job age separately.

**Fix**:
- Rate-limit class 1 so the leftover capacity meets class 2's throughput and delay needs.
- Age class 2 jobs: promote a job after it waits past a threshold.
- Use weighted fair queuing instead of strict priority. With weights 4:1, a saturated server gives class 2 at least 20% of capacity.

---

### A4 — Coherency-Bound Architecture Scaled Past USL Inflection

**Symptom**: doubling replicas or cache nodes lowers throughput and doubles cost.

**Root cause**: κ > 0 and the deployment is past N_max. Sources: synchronous replication, distributed locks, cache invalidation fan-out, consensus.

**Diagnosis**: load-test at several N, fit USL (P5), compare deployed N with N_max.

**Fix** (architectural): async replication on read-heavy paths, shard the locked resource, shrink the serialized critical section (σ). Stop scaling until κ drops.

---

### A5 — Fork-Join Sized by Mean Worker Time

**Symptom**: 8 parallel calls of E[S] = 100 ms each; the design assumed ~100 ms; p99 is several hundred ms.

**Root cause**: response time is the maximum of 8 branches. Even in the iid-exponential, no-queueing case, E[max] = 100 × H_8 ≈ 272 ms. Queueing and heavy-tailed branches make the tail worse.

**Fix**: size from the distribution of the maximum (P7); hedge the high-variance branch after its p95; make non-critical calls optional; question every call when K is large.

---

## Recipes

### R1 — Service-Sizing Playbook

**Goal**: replica count that meets the wait SLO at peak.

1. **Measure**: λ at peak, E[S], and CV²_s and CV²_a computed from samples (variance / mean²).
2. **Offered load**: a = λ × E[S]. Stability needs c > a.
3. **Erlang-C baseline**: find the smallest c with Wq_M/M/c ≤ SLO wait ([03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)).
4. **Variability**: Allen-Cunneen, Wq ≈ Wq_M/M/c × (CV²_a + CV²_s)/2. Raise c until this meets the SLO. Square-root staffing (c ≈ a + β√a) gives the same answer in closed form for large a.
5. **SLO check**: E[S] + Wq ≤ this service's share of the end-to-end budget (R3).
6. **Autoscaling**: set min/max replicas from steps 3–4 at floor and peak forecasts. Trigger on measured queue wait or in-flight count.

**Example (order validation)**: λ = 200 req/s, E[S] = 20 ms (μ = 50/s per pod), a = 4.
- c = 5 (ρ = 0.80): Erlang-C Wq ≈ 11.1 ms; with CV²_a = CV²_s = 2 (VF = 2), ≈ 22 ms.
- c = 6 (ρ = 0.67): C(6,4) ≈ 0.28, Wq ≈ 2.8 ms; with VF = 2, ≈ 5.7 ms.
- Total W at c = 6 ≈ 25.7 ms, inside a 50 ms budget. c = 5 gives ≈ 42 ms, which is tight but also inside.

---

### R2 — Backpressure Topology Design

**Goal**: overload at the bottleneck is pushed upstream, not silently queued.

1. **Map the pipeline** as a Jackson network: γᵢ, μᵢ, cᵢ, routing Pᵢⱼ including retry arcs.
2. **Solve flow balance** and rank stages by ρᵢ. Then compute each stage's Wq with its measured variability (Allen-Cunneen for c > 1). The effective bottleneck is the stage that eats most of its delay budget, which may not be the highest ρ.
3. **Bound queues** at the bottleneck and one stage upstream: limit ≈ μᵢ × (stage budget − E[Sᵢ]). Bound the others too.
4. **Signal**: when implied wait (depth / service rate) crosses the stage budget, emit 429 / RESOURCE_EXHAUSTED, pause the upstream consumer, or withhold credits.
5. **Propagate** stage by stage to ingress, which sheds (503) or rate-limits.
6. **Re-solve** after scaling the bottleneck.

**Example (image pipeline, γ = 50 img/s)**: Resize (μ = 80/s, c = 1, ρ = 0.63) → ML inference (μ = 40/s, c = 2, ρ = 0.63) → Storage (μ = 200/s, c = 1, ρ = 0.25). Both first stages have similar ρ, but ML inference has CV²_s ≈ 4. Allen-Cunneen at ML inference: Wq ≈ 16 ms (M/M/2) × 2.5 ≈ 40 ms, Lq ≈ 2. Resize with CV²_s = 1 waits ≈ 21 ms. With a 200 ms ML-stage budget, bound its queue at about 80 × (0.200 − 0.025) ≈ 14 jobs; past that it pauses Resize, which returns 429 to ingress.

---

### R3 — Tail-Latency Budget Allocation

**Goal**: split an end-to-end SLO into component budgets and an escalation policy.

1. **Available budget** = SLO_e2e − network overhead.
2. **Critical path**: serial stages add; parallel branches contribute their maximum (P7) plus join overhead.
3. **Per-component wait** with measured variability: Kingman for one server, Allen-Cunneen for c servers. W_i = Wq_i + E[S_i]. Mean W_i is not a percentile; for percentile budgets, use measured distributions or simulation.
4. **Feasibility**: if serial budgets exceed the available budget, add capacity at the largest Wq, move work off the critical path, or renegotiate the SLO.
5. **Escalation by budget, not ρ band**:
   - Green: measured wait well inside budget_i.
   - Yellow: wait trending toward budget_i. Alert and prepare scale-out.
   - Red: wait above budget_i. Scale out or open an incident.
6. **Parallel branches**: budget from the simulated or measured maximum; hedge the slowest branch.

**Example (checkout, 800 ms SLO, 3 ms network, 797 ms available)**. Single-server Kingman per component:

| Component | E[S] | ρ | VF | Wq | W | Budget |
|-----------|------|---|----|----|---|--------|
| API gateway | 2 ms | 0.40 | 1.5 | 2 ms | 4 ms | 10 ms |
| Auth | 5 ms | 0.55 | 2.0 | 12 ms | 17 ms | 25 ms |
| Cart | 10 ms | 0.60 | 2.5 | 37.5 ms | 47.5 ms | 60 ms |
| Payment gateway (external) | 200 ms | — | — | — | 200 ms | 250 ms |
| DB write | 8 ms | 0.50 | 2.0 | 16 ms | 24 ms | 20 ms |
| **Serial total** | | | | | **292 ms** | **365 ms** |

The flow has headroom overall, but DB write's W (24 ms) exceeds its 20 ms budget. Step 5 should catch this: raise its budget, cut its variability (e.g. pool contention), or add a server. Cart has the largest queue wait relative to E[S]. A second Cart server (ρ = 0.30 each) brings Allen-Cunneen Wq to ≈ 2.5 ms; lowering VF alone to 0.8 would bring it to ≈ 12 ms. Hedge the external gateway with a timeout and an async-confirmation fallback.

---

## Composition

| Starting point | Next step |
|----------------|-----------|
| P1 sizing | Add measured variability (P6, Allen-Cunneen); check P5 before large scale-out of shared-state services |
| P2 backpressure | Bound each queue from its delay budget (P4); add P3 if SLO classes share the bottleneck |
| P3 priority | Watch starvation (A3) |
| P5 USL | Fix κ, then re-size with P1 and re-fit USL |
| P7 fork-join | Size each branch with P1 + P6; hedge for p99 |
| R1 sizing | Feeds per-component W_i into R3 |
| R2 topology | Uses R1 service rates and R3 stage budgets for queue bounds |
| R3 budget | Uses P6 per component and P7 for parallel branches |

Before publishing a capacity plan, run A1 (implied wait of every queue bound) and A2 (measured CV²). Before a shared-state scale-out, run A4. Before approving a fan-out design, run A5.

---

## Sources

- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer.
- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *Communications of the ACM*, 55(1).
- Nelson, R. & Tantawi, A. N. (1988). "Approximate Analysis of Fork/Join Synchronization in Parallel Queues." *IEEE Transactions on Computers*, 37(6), 739–743.
- Dean, J. & Barroso, L. A. (2013). "The Tail at Scale." *Communications of the ACM*, 56(2), 74–80.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- [`foundations-queueing-theory`](../../foundations-queueing-theory/SKILL.md) — canonical definitions, formulas, and worked examples.
