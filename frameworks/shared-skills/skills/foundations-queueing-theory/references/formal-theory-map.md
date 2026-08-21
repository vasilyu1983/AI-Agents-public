---
description: Formal theory map for queueing-theory foundations. Use to separate exact formulas, approximations, and simulation boundaries.
last_verified: 2026-08-14
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
| Learning-augmented scheduling | ML-predicted job sizes combined with provable consistency-robustness guarantees | SPRPT and Trail policy (Mitzenmacher & Shahout 2025); embedding-based prediction for LLM scheduling (Shahout et al., arXiv 2410.01035) | Performance guarantees degrade under adversarial prediction error; consistency-robustness trade-off must be evaluated for target workload |
| Active queue management | Queue delay, buffer sizing, drop/mark policies | Bufferbloat mitigation | Throughput and latency trade off |
| Scalability models | Contention, coherency, load-test fits | USL and retrograde scaling | Fit is empirical and system-specific |
| Memory-coupled service | Joint compute-and-memory stability conditions; eviction dynamics | Systems where admitted work holds a growing, non-releasable resource until completion — KV cache, session state, buffered long-lived connections. Joint stability condition (Nie, Si & Zhou, ICML 2026); eviction limit cycles and the stabilizing effect of service-time heterogeneity (Ao, Dong, Luo & Simchi-Levi 2026). | Single-resource rho is NOT sufficient for stability. Compute rho can sit well below 1 while memory is the binding constraint. Eviction-free operation may be an unstable equilibrium rather than a target. |

## Production Rule

Every queueing estimate needs arrival rate, service distribution, concurrency/server count, buffer policy, stability check, and validation against observed Little's Law. If two of those are unknown, simulate or measure before committing capacity.

Add one question when service consumes a second resource that grows with service progress and is released only at completion: is the stability check single-resource or joint? A compute-only utilization figure is not a stability proof for such systems.
