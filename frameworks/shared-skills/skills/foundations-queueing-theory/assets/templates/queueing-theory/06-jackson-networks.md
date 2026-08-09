# Primitive 06 — Jackson Networks (Network of Queues, Product-Form Solution)

**Source**: Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.

## Definition

A **Jackson network** is an open network of M/M/c queues where customers route probabilistically between stations. The key result is the **product-form solution**: the joint steady-state distribution factorizes over stations as if each station were an independent M/M/c queue with its effective arrival rate.

### Conditions (Jackson's Theorem)

1. External Poisson arrivals at each station.
2. Exponential service times at each station.
3. Routing is probabilistic (Markovian routing matrix P).
4. Network is open (customers eventually leave).

### Effective Arrival Rates

Solve the traffic equations (flow balance):

```
λᵢ = γᵢ + Σⱼ λⱼ × Pⱼᵢ
```

where γᵢ = external arrival rate at station i, Pⱼᵢ = routing probability from j to i.

### Product-Form Result

```
π(n₁, n₂, ..., nₖ) = Π πᵢ(nᵢ)
```

Each station's marginal distribution is that of an isolated M/M/cᵢ queue with arrival rate λᵢ. Analyze each station independently using M/M/1 or M/M/c formulas.

**Closed Jackson networks** (fixed population N) use BCMP or Mean Value Analysis (MVA); open networks use the above.

## When to Use

- **Microservice pipeline analysis**: requests flow through auth → business logic → database; model each hop.
- **CI/CD pipeline bottleneck identification**: build → test → deploy stages with probabilistic reruns.
- **Data pipeline latency**: Kafka consumer → transformer → sink; solve for throughput bottleneck.
- **Multi-tier web architecture**: load balancer → app servers → cache → DB; find which tier limits throughput.
- **Call routing systems**: calls may transfer between agent pools; model as Jackson network.

Do NOT apply when service times are non-exponential across stages — use BCMP extensions (which allow general service distributions with FCFS, LCFS-PR, or PS disciplines) or simulation.

## Inputs

| Input | Symbol | Source |
|-------|--------|--------|
| External arrival rates | γᵢ | Traffic telemetry per entry point |
| Service rates | μᵢ (per station) | Profiling each service |
| Routing probabilities | Pᵢⱼ | Tracing / service mesh data |
| Server counts per station | cᵢ | Infrastructure inventory |

## Outputs

- **Effective λᵢ per station**: reveals which stations carry more load than external arrivals suggest.
- **ρᵢ per station**: identifies the bottleneck station (highest ρ).
- **W per station + end-to-end W**: sum of per-station W weighted by routing.
- **Throughput ceiling**: min over stations of (cᵢ × μᵢ).

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Non-Poisson arrivals at intermediate stations | Batch releases from upstream create bursts | Use G/G/1 Kingman approximation (primitive 07) per station; verify burstiness |
| Routing cycles amplify load | Retry logic creates feedback loops: λᵢ spikes when downstream is slow | Model retry amplification explicitly; add loop-breaking circuit breakers |
| Ignoring correlation between stations | Downstream bursty arrivals from upstream queued batch releases | Check inter-departure variability; Jackson product form breaks under non-Poisson inter-departures |
| Single-tier scaling without flow balance | Adding servers at bottleneck shifts bottleneck to next station | Solve flow-balance equations after scaling; re-identify new bottleneck |

## Worked Example

A 3-stage microservice chain:

| Station | External arrivals γᵢ (req/s) | Service rate μᵢ (req/s) | Servers cᵢ | Routing |
|---------|------------------------------|--------------------------|------------|---------|
| Auth (1) | 100 | 200 | 1 | 100% to Logic (2) |
| Logic (2) | 0 | 80 | 2 | 70% to DB, 30% exit |
| DB (3) | 0 | 60 | 3 | 100% exit |

**Traffic equations:**
- λ₁ = 100 (no feedback)
- λ₂ = λ₁ = 100
- λ₃ = 0.70 × λ₂ = 70

**Utilizations:**
- ρ₁ = 100/200 = 0.50
- ρ₂ = 100/(2×80) = 0.625
- ρ₃ = 70/(3×60) = 0.389

**Bottleneck**: Logic (station 2) at ρ = 0.625. Adding a third Logic server reduces ρ₂ to 0.417.

No re-examination of Auth or DB needed unless scaling Logic reveals them as new bottlenecks (re-solve flow equations).

## LLM Agent Networks as Stochastic Processing Networks

A network of LLM inference engines is **not** a classical Jackson network. The product-form assumption is violated because:
- **KV-cache memory coupling**: token generation holds GPU memory that constrains other requests across the same engine — stages are not independent.
- **Batch-dependent service rates**: throughput varies with batch composition, not just queue depth.

However, the throughput-optimality criterion maps to classical stability theory:

- **Single-engine serving**: any work-conserving scheduling policy achieves maximum stable throughput (Dai, Deng, Li & Peng, arXiv:2504.07347; accepted POMACS / SIGMETRICS 2026 as "Optimal Scheduling Algorithms for LLM Inference: Theory and Practice"). Empirically, Orca and Sarathi-serve are throughput-optimal under this criterion; vanilla vLLM (without continuous batching) is not maximally stable. _(Flag: verify against current vLLM version — scheduler may have been updated.)_
- **Multi-agent LLM routing**: work-conservation alone is insufficient for multi-engine networks. Apply MaxWeight-style scheduling on the inter-engine routing layer, analogous to the stability condition for open stochastic processing networks.

**Key analogy**: the throughput-optimality condition for single LLM engines plays the same role as the stability condition for open Jackson networks (ρᵢ < 1 at each station) — necessary but not sufficient for tail-latency SLOs.

## Tandem Queue Sojourn Bounds Beyond Classical Jackson

Classical Jackson product-form gives mean end-to-end latency via `W = Σ Wᵢ`. For **tail-latency SLOs** on multi-stage pipelines, mean analysis is insufficient — and the product-form independence assumption understates tail risk when arrivals are non-Poisson.

**SIGMETRICS 2025 result (Ciucu & Mehri 2025):** Closed-form polynomial-exponential bounds on end-to-end sojourn time distributions in tandem queues with general arrivals and light-tailed service times:

```
P[T_end > t] ≤ f(t) × exp(−θ × t)
```

where f(t) is a polynomial whose degree equals the number of **bottleneck stages** (stages operating near their capacity limit). For two-stage exponential service, the bounds are numerically sharp and improve large-deviations bounds by orders of magnitude.

Use these bounds when:
- Tail latency SLO must be verified (not just mean latency).
- Arrivals are non-Poisson (CV²_a ≠ 1) — e.g., bursty microservice traffic.
- The pipeline has 2+ bottleneck stages.

**Kill criterion:** Drop if arrivals are well-approximated as Poisson (CV²_a ≈ 1) — in that case, classical Jackson mean analysis plus Kingman's CV correction suffices.

See also: Fork-join (primitive 11) for multi-path latency analysis where paths reconverge.

## Composition

- **M/M/c** (primitive 03): each station in a Jackson network is an independent M/M/c queue.
- **Little's Law** (primitive 01): end-to-end L = sum of per-station Lᵢ; W = L/λ.
- **Kingman** (primitive 07): when non-exponential service times appear at one or more stations.
- **USL** (primitive 09): check whether adding servers at bottleneck hits coherency limits.

## Sources

- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. Chapter 4.
- Kleinrock, L. (1976). *Queueing Systems, Vol. 2: Computer Applications*. Wiley-Interscience.
- Cooper, R. B. (1981). *Introduction to Queueing Theory* (2nd ed.). North-Holland. Chapter 6.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. Ch. 17 ("Networks of Queues and Jackson Product Form"). _(Corrected 2026-07-11: prior text cited Ch. 30, which covers preemptive non-size-based scheduling — see primitive 05.)_
