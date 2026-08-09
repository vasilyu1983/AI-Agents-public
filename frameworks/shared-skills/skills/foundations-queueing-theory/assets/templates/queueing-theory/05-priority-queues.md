# Primitive 05 — Priority Queues (Preemptive vs. Non-Preemptive)

**Source**: Kleinrock (1976), Vol. 2; Harchol-Balter (2013), Ch. 29–30.

## Definition

A **priority queue** assigns a priority class to each customer. Higher-priority customers are served before lower-priority ones. Two regimes:

### Preemptive Priority
When a high-priority job arrives and a lower-priority job is in service, the server **interrupts** the low-priority job (which resumes later — preemptive-resume, or restarts — preemptive-repeat).

### Non-Preemptive Priority
A high-priority arrival waits until the current service (of any class) **completes**, then jumps ahead of all waiting lower-priority jobs.

### Key Metrics (two-class: class 1 = high, class 2 = low)

**Non-preemptive, M/G/1 base:**

```
Wq_1 = W0 / (1 − ρ₁)
Wq_2 = W0 / ((1 − ρ₁)(1 − ρ₁ − ρ₂))
```

where W0 = (λ₁ × E[S₁²] + λ₂ × E[S₂²]) / 2 (residual service time).

**Preemptive-resume:**

```
Wq_1 = W0 / (1 − ρ₁)          (same as non-preemptive)
W_2  = W_2(non-preemptive) + (additional preemption overhead)
```

High-priority class is unaffected by low-priority in the preemptive case (except through residual service time).

## When to Use

- **Protect SLOs for critical workloads**: interactive requests should not wait behind batch jobs.
- **LLM inference tiering**: chat (interactive) vs. offline summarization (batch) share the same GPU pool.
- **Database query scheduling**: OLTP reads get priority over analytics scans.
- **Kafka consumer priority**: high-value events processed before low-value audit logs.
- **Network QoS**: VoIP and real-time traffic over bulk data transfers.

Use **non-preemptive** when:
- Service interruption is expensive or impossible (database transactions, GPU inference mid-token).
- Acceptable delay for high-priority class is bounded — the current low-priority job will finish "soon."

Use **preemptive-resume** when:
- High-priority latency SLO is strict (milliseconds).
- Service work is stateful and safely pausable.

## Inputs

| Input | Symbol | Source |
|-------|--------|--------|
| Arrival rates per class | λ₁, λ₂, ... | Traffic segmentation |
| Mean service time per class | E[S₁], E[S₂] | Profiling |
| Second moment per class | E[S₁²], E[S₂²] | From service-time histogram |

## Outputs

- **Wq per priority class**: wait time SLO validation per tier.
- **Cross-class impact**: how much low-priority class suffers when high-priority load increases.
- **Priority inversion risk**: whether low-priority class starves under sustained high-priority load.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Priority inversion / starvation | High-priority traffic fills all capacity; low-priority never served | Rate-limit high-priority class; reserve minimum bandwidth for low-priority |
| Head-of-line blocking in non-preemptive | One large low-priority job delays high-priority arrivals | Switch to preemptive for strict SLOs, or bound low-priority job size |
| Correct priorities on wrong queue level | Priority applied at load balancer but not at worker | Apply priority end-to-end: ingress, queue, and worker scheduler |
| Mixed workloads in same priority class | High-CV class hides behind low-CV class | Split into separate classes; model each with P-K (primitive 04) |

## Worked Example

An inference service receives two request classes:
- **Class 1 (interactive)**: λ₁ = 5 req/s, E[S₁] = 0.5 s, E[S₁²] = 0.5 s² (CV² = 1)
- **Class 2 (batch)**: λ₂ = 2 req/s, E[S₂] = 3.0 s, E[S₂²] = 12.0 s² (CV² = 0.33)

```
ρ₁ = 5 × 0.5 = 2.5  ← exceeds 1 — need multiple servers
```

Assume 5 servers (M/G/c approximation, ρ system = (5×0.5 + 2×3)/(5) = (2.5+6)/5 = 1.7 ← still > 1).

Needs 10 servers for ρ = 0.85. With non-preemptive priority:
- Class 1 mean wait is dramatically lower than without priority (batch jobs cannot block interactive ones for more than one service period).
- Class 2 wait increases but batch jobs are latency-tolerant.

**Without priority**: both classes share equal wait; interactive requests occasionally wait behind 3-second batch jobs.
**With non-preemptive priority**: interactive class waits at most one 3-second batch job service, then gets immediate service.

## Tail-Optimal Scheduling Under Unknown Job Sizes

Classical SRPT (Shortest Remaining Processing Time) minimizes mean response time but requires knowing job sizes. When job sizes are unknown, prior work accepted a trade-off: optimize for mean or accept tail degradation.

**SIGMETRICS 2025 result (Harlev, Yu, Scully 2025):** The first scheduling policy achieving strong tail optimality in the light-tailed M/G/1 without known job sizes, using a Gittins index policy with a **negative discount rate**. Prior Gittins with standard discount rates optimized mean completion time; the negative-discount-rate variant shifts the objective toward tail percentiles.

Use this policy when:
- Tail latency (p99, p99.9) matters more than mean latency.
- Job sizes are not known at arrival (or estimates are unreliable).
- The service-time distribution is light-tailed (e.g., bounded or sub-exponential).

**Kill criterion:** Drop if mean latency degradation from the negative-discount Gittins policy exceeds the acceptable margin for the specific job-size distribution in use — simulation or analysis is needed per-distribution.

See also: Robustness Warning below (Gittins fragility under distributional uncertainty).

## Trail Policy for LLM Serving (Hybrid Preemptive / Non-Preemptive)

The Trail policy (Mitzenmacher & Shahout, Stochastic Systems 2025) is a scheduling discipline for LLM inference that combines SPRPT with a non-preemptive phase:

- **Phase 1 (young requests):** Preemptive SPRPT scheduling on predicted remaining token count — short predicted jobs get priority.
- **Phase 2 (aged requests):** Once a request has been in service for `c × predicted_size` time, preemption is disabled. The request runs to completion without KV-cache re-compute.

This policy is analyzable via the SOAP framework. It avoids the main cost of standard SRPT preemption in LLM systems (KV-cache re-compute) while preserving most of the tail-latency benefit.

## Robustness Warning

The Gittins index policy is **not robust to distributional misspecification**. Moseley, Newman, Pruhs, Zhou (SIGMETRICS 2025) prove that even arbitrarily small perturbations to the true job-size distribution can cause unbounded mean completion time degradation under standard Gittins.

**When to apply Robust Gittins:**
- Job-size distributions are estimated from monitoring data or ML predictions (not known analytically).
- The system deploys any Gittins-adjacent scheduling policy (SRPT with estimated sizes, SPRPT, size-based priority lanes).

The Robust Gittins policy (Moseley et al. 2025) bounds degradation by a new distributional-error measure — use it as the safe default when distributions are learned rather than prescribed. Pair with prediction-augmented SPRPT (Mitzenmacher & Shahout 2025) for systems where predictions are available.

**Kill criterion:** Drop Robust Gittins concern entirely if the system uses FCFS or FIFO scheduling — Gittins fragility is only relevant when explicitly deploying Gittins or Gittins-adjacent policies.

## Composition

- **M/G/1 / P-K** (primitive 04): non-preemptive priority analysis builds directly on P-K residual service time.
- **M/M/c** (primitive 03): extend priority model to c servers for multi-server pools.
- **Fork-join** (primitive 11): in parallel systems, slow workers in low-priority class still gate high-priority fork completion.

## Sources

- Kleinrock, L. (1976). *Queueing Systems, Vol. 2: Computer Applications*. Wiley-Interscience.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. Priority scheduling analysis. _(Corrected 2026-07-11: these two Kleinrock citations previously had their publication years transposed — Vol. 1: Theory was published in 1975, Vol. 2: Computer Applications in 1976.)_
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. Ch. 30 ("Preemptive, Non-Size-Based Policies"), Ch. 29 ("Non-Preemptive, Non-Size-Based Policies"). _(Corrected 2026-07-11: prior text cited Ch. 18–19, which cover classed and closed networks of queues, not priority scheduling.)_
- Cooper, R. B. (1981). *Introduction to Queueing Theory* (2nd ed.). North-Holland. Chapter 5.
