---
description: Applied patterns, scenarios, anti-patterns, and known traps for queueing-theory foundations.
last_verified: 2026-05-02
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

## Known Traps

- Rho below 1 does not mean latency is acceptable.
- Mean service time hides variance; CV often dominates wait.
- Large buffers preserve throughput while destroying latency.
- Erlang formulas are optimistic under bursty arrivals.
- Fork-join mean math understates tail latency.
- Scaling one stage can move the bottleneck downstream.

## Exit Checklist

- [ ] Arrival rate and service rate are measured over a stable window.
- [ ] Utilization rho is below the target operating point.
- [ ] Arrival and service variability are included.
- [ ] Blocking vs waiting behavior is explicit.
- [ ] Queue depth alert follows Little's Law.
- [ ] Formula result is validated by load test or simulation when assumptions are weak.
