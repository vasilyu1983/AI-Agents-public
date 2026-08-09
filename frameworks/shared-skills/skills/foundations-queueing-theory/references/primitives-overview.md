---
description: Domain-agnostic overview of 11 queueing-theory primitives — failure modes, decision checklist, and anti-pattern taxonomy.
last_verified: 2026-05-02
status: stable
---

# Queueing-Theory Primitives Overview

## Table of Contents

- [Why Queueing Theory Matters](#why-queueing-theory-matters)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why Queueing Theory Matters

Every system that serves requests has a queue — visible or hidden. Without intentional capacity modeling, systems fail in predictable but avoidable ways:

| Failure Mode | Queueing Theory Diagnosis | What Goes Wrong |
|-------------|--------------------------|-----------------|
| Latency spikes at 70% CPU | ρ approaching 1; M/M/1 hyperbolic blowup | SLO breach before saturation; no headroom |
| "We have 16 servers — latency should be fine" | Retrograde scaling (USL κ > 0) | Adding servers reduces throughput past N_max |
| p99 is 20× p50 under load | High service-time variance (CV² >> 1) inflates M/G/1 queue wait | P-K / Kingman predicts the gap |
| System is "fast" but callers see slowness | Bufferbloat: large buffers absorb load, hide congestion | Latency accumulates in silent queues |
| Fan-out query is slow even though each call is fast | Completion waits for slowest worker (fork-join max) | Completion time > any individual call time |
| Scaling microservices doesn't help | Bottleneck shifted to another stage | Jackson network flow balance not re-solved |

Each primitive addresses a specific failure mode. They compose: real systems need 2–4 primitives applied in sequence.

---

## Primitive Index

11 primitives, each in its own playbook under [`../assets/templates/queueing-theory/`](../assets/templates/queueing-theory/).

| # | Primitive | Failure Mode It Addresses | Primary Domains |
|---|-----------|--------------------------|-----------------|
| 1 | [Little's Law (L = λW)](../assets/templates/queueing-theory/01-littles-law.md) | Misaligned latency/throughput/concurrency metrics | All domains: any stable system |
| 2 | [M/M/1](../assets/templates/queueing-theory/02-mm1.md) | Underestimated latency at moderate utilization | Single-server services, databases, APIs |
| 3 | [M/M/c (Erlang-C)](../assets/templates/queueing-theory/03-mmc.md) | Over/under-provisioned worker pools | Thread pools, agent pools, DB connections |
| 4 | [M/G/1 / Pollaczek-Khinchine](../assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) | Variance-driven latency inflation ignored | LLM inference, DB queries, batch jobs |
| 5 | [Priority Queues](../assets/templates/queueing-theory/05-priority-queues.md) | High-latency workloads blocked by low-priority batch | Mixed-SLO services, inference tiering |
| 6 | [Jackson Networks](../assets/templates/queueing-theory/06-jackson-networks.md) | Hidden bottleneck in multi-stage pipeline | Microservice chains, data pipelines |
| 7 | [Kingman's Formula (G/G/1)](../assets/templates/queueing-theory/07-kingman-formula.md) | M/M/1 underestimates real latency from bursty/variable traffic | Cloud services, task queues, APIs |
| 8 | [Bufferbloat](../assets/templates/queueing-theory/08-bufferbloat.md) | Good throughput + terrible latency; buffers hiding congestion | Application queues, Kafka lag, networks |
| 9 | [USL (Universal Scalability Law)](../assets/templates/queueing-theory/09-usl-universal-scalability.md) | Retrograde scaling when adding servers hurts throughput | Distributed DBs, clusters, ML training |
| 10 | [Erlang-B (Loss Systems)](../assets/templates/queueing-theory/10-loss-systems-erlang-b.md) | Call/connection blocking above target GoS | WebRTC, telephony, license pools |
| 11 | [Fork-Join / Slowest-Worker](../assets/templates/queueing-theory/11-fork-join-parallel.md) | Fan-out latency dominated by slowest worker | Scatter-gather, MapReduce, LLM fan-out |

---

## Anti-Patterns by Domain

### Capacity Planning

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Sizing for average load without headroom | M/M/1: latency is hyperbolic near ρ=1 | Size for ρ ≤ 0.70; keep 30% headroom |
| Using M/M/1 when service time is variable | CV² > 1 inflates wait beyond M/M/1 prediction | Measure CV²_s; apply P-K or Kingman |
| Scaling horizontally without checking USL | Retrograde at high N reduces throughput | Fit USL from load-test series; find N_max |

### Latency Debugging

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Blaming network for p99 spikes under load | Bufferbloat in application-layer queue | Set finite queue depth; monitor queue depth as leading indicator |
| Treating p50 as representative | M/G/1: high CV² → p99 >> p50 | Model tail; monitor percentiles; bound service times |
| No Little's Law sanity check | L ≠ λ × W signals measurement misalignment | Verify consistency of depth/rate/latency metrics |

### Multi-Stage Systems

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Scaling one service without re-solving flow balance | Bottleneck shifts downstream undetected | Jackson networks: re-solve after each scaling action |
| Fan-out sized by mean worker time | Fork-join completion = E[max] >> E[S] | Apply H_K correction; model tail of maximum |
| Priority not applied end-to-end | Priority at load balancer, FIFO at worker | Apply priority consistently: ingress, queue, and worker scheduler |

---

## Decision Checklist

- [ ] **Is the system stable?** → compute ρ = λ/(c×μ). If ρ ≥ 1, no steady state exists; scale first.
- [ ] **Single server?** → M/M/1 (02) for baseline; check whether latency is acceptable at current ρ.
- [ ] **Multiple parallel servers?** → M/M/c (03); compute Erlang-C wait probability.
- [ ] **Service time variable (CV² ≠ 1)?** → P-K (04) if arrivals are Poisson; Kingman (07) if arrivals are also non-Poisson.
- [ ] **Multi-stage pipeline?** → Jackson networks (06); solve flow balance; find bottleneck.
- [ ] **Scaling horizontally?** → USL (09); fit σ and κ from load tests; verify N_max.
- [ ] **Mixed SLO classes?** → Priority queues (05); model each class separately.
- [ ] **High latency despite good throughput?** → Bufferbloat (08); check queue depths and AQM.
- [ ] **Fan-out / scatter-gather?** → Fork-join (11); compute E[max] = E[S] × H_K.
- [ ] **Drop-on-busy (no queue)?** → Erlang-B (10); compute blocking probability.
- [ ] **Sanity-checking any result?** → Little's Law (01); verify L = λ × W.

---

## Sources

- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Kleinrock, L. (1976). *Queueing Systems, Vol. 2: Computer Applications*. Wiley-Interscience.
- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Mathematical Proceedings of the Cambridge Philosophical Society*, 57(4), 902–904.
- Pollaczek, F. (1930). "Über eine Aufgabe der Wahrscheinlichkeitstheorie." *Mathematische Zeitschrift*, 32(1), 64–100.
- Khinchine, A. Y. (1932). "Mathematical theory of a stationary queue." *Matematicheskii Sbornik*, 39(4), 73–84.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer.
- Cooper, R. B. (1981). *Introduction to Queueing Theory* (2nd ed.). North-Holland.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- Little, J. D. C. (1961). "A Proof for the Queuing Formula: L = λW." *Operations Research*, 9(3), 383–387.
- Nelson, R. & Tantawi, A. N. (1988). "Fork/Join Synchronization in Parallel Queues." *IEEE Transactions on Computers*, 37(6), 739–743.
