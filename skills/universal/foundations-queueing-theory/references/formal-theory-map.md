---
description: Formal theory map for queueing-theory foundations. Use to separate exact formulas, approximations, and simulation boundaries.
status: stable
---

# Queueing Theory Formal Theory Map

## Purpose

Use this map when a capacity or latency recommendation needs the formula assumptions, stationarity boundary, or a decision on whether closed-form queueing is enough.

## Theory Areas

| Area | Formal Objects | What It Supports | Boundary |
|---|---|---|---|
| Conservation laws | L, lambda, W, steady-state averages | Little's Law sanity checks | Requires stable long-run averages |
| Birth-death processes | Poisson arrivals, exponential service, Markov chains | M/M/1, M/M/c, Erlang-B/C | Bursty traffic breaks assumptions |
| General service queues | Service-time moments, residual life | M/G/1 and P-K formula | Exact mainly for Poisson arrivals |
| Heavy traffic | Utilization rho near 1, variability factors | Kingman's approximation | Approximation degrades away from heavy traffic |
| Queueing networks | Traffic equations, product-form solutions | Jackson networks | Product form needs specific routing/service assumptions |
| Scheduling disciplines | Priority, preemption, head-of-line behavior | Priority queues and SLO classes. SOAP framework (Scully, Harchol-Balter & Scheller-Wolf 2018) unifies all M/G/1 age-based policies; use to compare SRPT vs. Gittins vs. FB for a given job-size distribution. | Starvation and fairness need explicit checks; SOAP applies to M/G/1 only (multiserver extensions are active research) |
| Learning-augmented scheduling | ML-predicted job sizes with consistency-robustness guarantees | Graceful degradation under bounded multiplicative prediction error is proven for SPRPT-with-bounce (C = 3.5) and PSPJF (C = 1.5) (Scully, Grosof & Mitzenmacher, ITCS 2022); plain SPRPT has no such constant-factor bound. Trail: limited preemption with threshold c × predicted_size (Shahout et al., arXiv 2410.01035). Survey: Mitzenmacher & Shahout, *Stochastic Systems* 2025 (arXiv 2503.07545) | Guarantees need bounded multiplicative error; evaluate the consistency-robustness trade-off on the target workload |
| Multi-server approximations | Allen-Cunneen G/G/c, square-root staffing (Halfin-Whitt regime), pooling | Pool sizing without fixed ρ targets; see [`multiserver-overload-and-disciplines.md`](multiserver-overload-and-disciplines.md) | Approximations; heavy tails, autocorrelation and abandonment need simulation or Erlang-A |
| Discipline sensitivity | FCFS vs processor sharing vs loss | Whether CV²_s enters the mean at all | PS and Erlang-B insensitivity hold for the mean/blocking, not for per-job tails |
| Overload dynamics | Retry amplification, goodput, metastability | Shedding, adaptive LIFO, retry budgets | No steady state at ρ ≥ 1; the sustaining loop is owned by foundations-distributed-systems |
| Active queue management | Queue delay, buffer sizing, drop/mark policies | Bufferbloat mitigation | Throughput and latency trade off |
| Scalability models | Contention, coherency, load-test fits | USL and retrograde scaling | Fit is empirical and system-specific |
| Memory-coupled service | Joint compute-and-memory stability conditions; eviction dynamics | Systems where admitted work holds a growing, non-releasable resource until completion — KV cache, session state, buffered long-lived connections. Joint stability condition (Nie, Si & Zhou, ICML 2026); eviction limit cycles and the stabilizing effect of service-time heterogeneity (Ao, Dong, Luo & Simchi-Levi 2026). | Single-resource rho is NOT sufficient for stability. Compute rho can sit well below 1 while memory is the binding constraint. Eviction-free operation may be an unstable equilibrium rather than a target. |

## Production Rule

Every queueing estimate needs arrival rate, service distribution, concurrency/server count, buffer policy, stability check, and validation against observed Little's Law. If two of those are unknown, simulate or measure before committing capacity.

Add one question when service consumes a second resource that grows with service progress and is released only at completion: is the stability check single-resource or joint? A compute-only utilization figure is not a stability proof for such systems.

## Scheduling Research Notes (moved from SKILL.md)

- **Age-based M/G/1 policies.** SOAP (Scully, Harchol-Balter & Scheller-Wolf 2018) gives one response-time formula for SRPT, FCFS, FB and Gittins. Gittins with a negative discount rate achieves strong tail optimality in the light-tailed M/G/1 without known sizes (Harlev, Yu & Scully 2025). Standard Gittins is brittle under distributional misspecification; Robust Gittins bounds the damage (Moseley et al. 2025).
- **M/G/k mean.** SRPT-k is no longer optimal for the mean: SEK-SMOD beats it at all loads and job-size distributions (Grosof & Hurtado-Lange, arXiv 2510.25963, SIGMETRICS 2026).
- **M/G/k tail.** Yu, Harlev, Adakroy & Scully (SIGMETRICS 2026) report that γ-Boost is heavy-traffic tail-optimal for light-tailed M/G/k but can be worse than FCFS at lighter loads, and give a variant that favours larger jobs (only the title and venue were checked; read the paper before quoting these claims).
- **Practical rule.** Benchmark any scheduling policy across the whole load range, not only at the design point.
- **LLM engines.** Work-conservation is sufficient for maximum throughput on a single engine (Dai, Deng, Li & Peng, arXiv 2504.07347); RAD/SLAI (Bari, Hegde & de Veciana, arXiv 2508.01002) addresses prefill/decode tiling. Serving-specific sizing lives in `ai-llm-inference`.
