---
description: Applied patterns, scenarios, anti-patterns, and known traps for queueing-theory foundations.
last_verified: 2026-08-14
status: stable
---

# Queueing Theory Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Capacity sizing | Need enough workers for latency SLO | Little's Law -> M/M/c -> Kingman adjustment |
| Saturation alerting | Need leading indicator before p99 breaks | Little's Law -> queue depth threshold -> utilization guard |
| Pipeline bottleneck hunt | Multi-stage system slows down | Jackson network -> highest rho -> re-solve after change |
| Drop-on-busy system | Calls/connections are blocked, not queued | Erlang-B -> blocking target |
| Fan-out latency audit | Scatter-gather p95/p99 is high | Fork-join -> tail distribution -> speculative execution |
| Scale-out limit | Adding replicas stops helping | USL fit -> contention/coherency diagnosis |
| Prediction-augmented scheduling | ML output-length predictions available; need to reduce mean response time while bounding degradation under prediction error | Embed job-size predictor -> SPRPT with Trail policy -> measure consistency/robustness ratio -> escalate to Robust Gittins if distributional uncertainty is high |
| Memory-coupled capacity sizing | Admitted work holds a resource that grows with service progress and frees only at completion (KV cache, session state) | Joint compute-and-memory stability condition -> derive stable service rate -> size cluster from forecast arrival rate -> admission-control on projected peak occupancy -> check for eviction limit cycles |

## Known Traps

- Rho below 1 does not mean latency is acceptable.
- Mean service time hides variance; CV often dominates wait.
- Large buffers preserve throughput while destroying latency.
- Erlang formulas are optimistic under bursty arrivals.
- Fork-join mean math understates tail latency.
- Scaling one stage can move the bottleneck downstream.
- A compute-only rho is not a stability proof when memory is a second binding constraint.
- Homogeneous workloads can be less stable than heterogeneous ones under memory coupling: synchronized completions align memory peaks and trigger evict-restart cycles.
- Shortest-first is not a universal default. Recent M/G/k results beat SRPT-k on the mean and beat gamma-Boost on the tail by giving larger jobs more priority in some regimes; a policy tuned at peak load can be worse than FCFS off-peak.

## Exit Checklist

- [ ] Arrival rate and service rate are measured over a stable window.
- [ ] Utilization rho is below the target operating point.
- [ ] Arrival and service variability are included.
- [ ] Blocking vs waiting behavior is explicit.
- [ ] Queue depth alert follows Little's Law.
- [ ] Formula result is validated by load test or simulation when assumptions are weak.
- [ ] If a second resource grows during service and frees only at completion, the stability check is joint, not compute-only.
