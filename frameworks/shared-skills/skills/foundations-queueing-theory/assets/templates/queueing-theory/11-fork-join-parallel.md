# Primitive 11 — Fork-Join Queues (Parallel Work, Slowest-Worker Bound)

**Source**: Nelson, R. & Tantawi, A. N. (1988). "The Approximate Analysis of Fork/Join Synchronization in Parallel Queues." *IEEE Transactions on Computers*, 37(6), 739–743. Harchol-Balter (2013), scheduling chapters. _(Corrected 2026-07-11: a prior version cited "Ch. 33," which is the book's SRPT/fairness chapter, not fork-join; Nelson & Tantawi (1988) above is the primary source for the fork-join formulas used here.)_

## Definition

A **fork-join queue** models parallel work that must synchronize:

1. **Fork**: a job splits into K sub-tasks, each sent to a parallel worker.
2. **Join**: the job completes only when **all K sub-tasks finish**.

The response time is therefore bounded by the **slowest (maximum-order) sub-task**:

```
T_fork-join ≥ E[max(S₁, S₂, ..., Sₖ)]
```

### The Slowest-Worker Bound (Lower Bound)

For K parallel workers each with exponential service time E[S]:

```
E[max(S₁,...,Sₖ)] = E[S] × Σ_{k=1}^{K} 1/k  = E[S] × H_K
```

where H_K is the K-th harmonic number (H₁=1, H₂=1.5, H₃≈1.83, H₁₀≈2.93).

This grows logarithmically with K: doubling workers adds ln(2) ≈ 0.7× average service time to the completion time.

### Upper Bound (Stochastic)

For M/M/1 workers with load ρ per worker, a tight upper bound on fork-join response time W_FJ:

```
W_FJ ≤ W_MM1(1 worker) + (K−1) × E[S] / (1 − ρ) × correction_factor
```

The exact analysis is intractable; use simulation or the Nelson-Tantawi approximation for operational sizing.

## When to Use

- **Fan-out parallel queries**: API aggregating responses from K downstream services (scatter-gather).
- **MapReduce / Spark stages**: reducers wait for all mapper outputs.
- **Distributed checkpoints**: all-reduce in ML training (all workers must sync before next step).
- **Multi-AZ health checks**: request passes only when all N zones respond.
- **Parallel test suites**: CI job completes when all K test shards finish.
- **LLM ensemble**: generate K candidate responses in parallel; completion = slowest model reply.

## Inputs

| Input | Symbol | Source |
|-------|--------|--------|
| Number of parallel workers | K | Architecture design |
| Mean service time per worker | E[S] | Profiling |
| Service time variance | CV² per worker | Profiling |
| Worker utilization | ρ per worker | Traffic analysis |

## Outputs

- **E[max]**: expected completion time lower bound.
- **Variance of completion time**: increases with K (more workers → higher maximum).
- **SLO feasibility**: whether p99 target is achievable given slowest-worker distribution.
- **Optimal K**: point of diminishing returns where adding workers no longer meaningfully reduces E[max].

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Sizing fork-join by mean rather than max | E[S] underestimates completion time; E[max] >> E[S] | Use H_K correction; model tail explicitly |
| High-CV worker in the fork-join | One slow worker type dominates all completions | Bound or cap slow workers; use timeout + fallback |
| Stragglers in MapReduce / all-reduce | Long tail from disk I/O, GC, or preemption | Speculative execution (duplicate task to faster node) |
| Ignoring synchronization point contention | Join point itself is a queue; saturated join delays all | Model join point as a separate M/M/c queue |
| All K workers share one bottleneck resource | Effectively serial despite parallelism | Separate the bottleneck resource or use resource partitioning |

## Worked Example

An API aggregates weather data from K = 5 upstream providers in parallel (fan-out). Each provider has mean latency E[S] = 200 ms.

**Lower bound on completion time** (exponential service times):

```
E[max] = E[S] × H_K = 200 × (1 + 1/2 + 1/3 + 1/4 + 1/5)
       = 200 × 2.283 = 456.7 ms
```

Even though each provider averages 200 ms, the fan-out completion time averages ~457 ms — 2.28× the individual service time. With 10 providers (K=10):

```
E[max] = 200 × H_{10} = 200 × 2.929 = 585.8 ms
```

Doubling providers only adds 128 ms (from 457 ms to 586 ms) due to logarithmic growth. Adding more providers for data completeness has diminishing latency cost.

**SLO check**: a 600 ms p50 SLO is achievable with K ≤ 10. For p99, the tail of the maximum is much heavier — use simulation or extreme-value bounds.

**Fix for SLO violation**: impose a 450 ms timeout; return best-effort with K' responses received. A hedge request (speculative execution) on slowest provider further reduces tail.

## Composition

- **M/M/1** (primitive 02): each worker in the fork-join is an independent M/M/1 queue at load ρ.
- **Little's Law** (primitive 01): total items in the fork-join system = K × (items per worker); verify.
- **Priority queues** (primitive 05): high-priority fork-join jobs can preempt low-priority workers to reduce stragglers.
- **USL** (primitive 09): adding more fork branches can hit coherency overhead at the join synchronization point.

## Sources

- Nelson, R. & Tantawi, A. N. (1988). "The Approximate Analysis of Fork/Join Synchronization in Parallel Queues." *IEEE Transactions on Computers*, 37(6), 739–743.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. (Ch. 33 covers SRPT/fairness, not fork-join; cited here for general scheduling-theory background only.)
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Dean, J. & Ghemawat, S. (2008). "MapReduce: Simplified Data Processing on Large Clusters." *CACM*, 51(1), 107–113. (Speculative execution rationale.)
