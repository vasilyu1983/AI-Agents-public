---
description: Applied patterns, scenarios, anti-patterns, and known traps for queueing-theory foundations.
status: stable
---

# Queueing Theory Patterns, Scenarios, and Traps

## Use Patterns

| Pattern | Use When | Stack |
|---|---|---|
| Capacity sizing | Need enough workers for latency SLO | Little's Law -> M/M/c -> Allen-Cunneen adjustment -> square-root staffing check |
| Overload / retry storm | Throughput high, goodput low, clients retrying | Retry-inclusive λ -> Q/μ vs client timeout -> delay-bounded queue, adaptive LIFO, retry budget |
| Saturation alerting | Need leading indicator before p99 breaks | Little's Law -> queue depth threshold -> utilization guard |
| Pipeline bottleneck hunt | Multi-stage system slows down | Jackson network -> highest rho -> re-solve after change |
| Drop-on-busy system | Calls/connections are blocked, not queued | Erlang-B -> blocking target |
| Fan-out latency audit | Scatter-gather p95/p99 is high | Fork-join -> tail distribution -> speculative execution |
| Scale-out limit | Adding replicas stops helping | USL fit -> contention/coherency diagnosis |
| Prediction-augmented scheduling | ML output-length predictions available; need to reduce mean response time while bounding degradation under prediction error | Embed job-size predictor -> scheduling variant with a proven degradation bound (SPRPT-with-bounce or PSPJF) -> for LLM serving, Trail's limited preemption -> measure consistency/robustness ratio -> escalate to Robust Gittins if distributional uncertainty is high |
| Memory-coupled capacity sizing | Admitted work holds a resource that grows with service progress and frees only at completion (KV cache, session state) | Joint compute-and-memory stability condition -> derive stable service rate -> size cluster from forecast arrival rate -> admission-control on projected peak occupancy -> check for eviction limit cycles |

## Known Traps

- Rho below 1 does not mean latency is acceptable.
- Mean service time hides variance; CV often dominates wait.
- Large buffers preserve throughput while destroying latency.
- Erlang formulas assume Poisson arrivals; bursty or dependent arrivals usually wait longer.
- Variance inflation (P-K, Kingman) is an FCFS result; processor sharing and loss systems are insensitive to CV²_s in the mean.
- At ρ ≥ 1 with client timeouts, FCFS can reach zero goodput at full utilization.
- Fork-join mean math understates tail latency.
- Scaling one stage can move the bottleneck downstream.
- A compute-only rho is not a stability proof when memory is a second binding constraint.
- Homogeneous workloads can be less stable than heterogeneous ones under memory coupling: synchronized completions align memory peaks and trigger evict-restart cycles.
- Shortest-first is not a universal default. Recent M/G/k results beat SRPT-k on the mean and beat gamma-Boost on the tail by giving larger jobs more priority in some regimes; a policy tuned at peak load can be worse than FCFS off-peak.

## Exit Checklist

- [ ] Arrival rate and service rate are measured over a stable window.
- [ ] Server count or utilization is derived from the SLO, not from a fixed ρ target.
- [ ] Arrival and service variability are included.
- [ ] Blocking vs waiting behavior is explicit.
- [ ] Queue depth alert follows Little's Law.
- [ ] Formula result is validated by load test or simulation when assumptions are weak.
- [ ] If a second resource grows during service and frees only at completion, the stability check is joint, not compute-only.
