# Queueing Theory Applied to Observability

The queueing math (Little's Law, M/M/c, P-K, Kingman, priority queues, Jackson networks, bufferbloat, USL) lives in [`foundations-queueing-theory`](../../foundations-queueing-theory/SKILL.md). Check its [When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) section first. Multi-server variability (Allen-Cunneen), square-root staffing, overload, retries, and fan-out tails are in [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md). Capacity sizing and diagnosis belong to [`software-performance`](../../software-performance/SKILL.md); load tests belong to [`qa-testing-performance`](../../qa-testing-performance/SKILL.md). This file keeps only the telemetry rules.

## Rules that are specific to telemetry

| Question | Rule | Primitive |
|---|---|---|
| What is the leading saturation signal? | In-flight concurrency (queue depth), not CPU. Little's Law, L = λW, links it to throughput and **mean** time in system. Use OTel `http.server.active_requests` (UpDownCounter) or an equivalent gauge for L. | [01-littles-law](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) |
| Are our metrics consistent? | Check measured L against λ × W_mean over the same window. A large gap means mismatched windows, mixed populations, or a hidden queue (thread pool, connection pool, upstream buffer) that the telemetry does not cover. | same |
| Why did p99 explode while CPU looked fine? | Waiting time grows roughly as ρ/(1−ρ) times arrival and service-time variability (Kingman, one server; Allen-Cunneen for c servers). Alerts on raw latency need utilisation (ρ) and measured variability next to them to be interpretable. | [07-kingman-formula](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md), [04-mg1-pollaczek-khinchine](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) |
| Is there a standing queue? | A p99/p50 ratio that grows with load while p50 stays flat points to a buffer, not slower work. Find the layer from its queue metric (table below). The ratio is a diagnostic, not a universal threshold, and it does not measure CV²_s; baseline it per service. | [08-bufferbloat](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md) |
| Do tiered SLOs share one pool? | Predict per-class wait with the priority-queue formulas before promising a tier. Segment telemetry by a priority span attribute. | [05-priority-queues](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md) |
| Did a release change scalability? | Fit USL (σ contention, κ coherency) to throughput vs concurrency before and after the release. Confirm with a load test, not production noise. | [09-usl-universal-scalability](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md) |
| How do we split an end-to-end latency budget? | Allocate per-hop budgets from measured visit counts and service times along the trace. Tail latencies do not add linearly, so validate the allocation against end-to-end traces. | [06-jackson-networks](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) |

## Building a saturation alert

1. Measure λ (`rate(http_requests_total[5m])`), mean service time E[S], and CV²_s from raw span durations or native-histogram variance. Bucket-based estimates of variance are coarse.
2. Pick a **mean** latency target W_target that is consistent with the p99 SLO for this service's measured tail shape. Little's Law gives means only; do not plug a p99 budget into it.
3. Queue-depth alert: in-flight L above λ × W_target, sustained over the alert window.
4. Utilisation warning: derive ρ* from the SLO and measured variability (P-K or Kingman for one server, Allen-Cunneen for c servers). There is no portable ρ threshold such as 70% or 80%.
5. Page on queue depth (cause); use p99 as the lagging confirmation (effect).

Why variability matters (P-K, ρ = 0.8): Wq = 10·E[S] at CV²_s = 4 vs 4·E[S] at CV²_s = 1, so 2.5× more waiting at the same utilisation. An SLO derived from M/M/1 math without measuring CV²_s is optimistic.

## Where the buffer hides

| Layer | Queue metric to check |
|---|---|
| Application executor / thread pool | executor queue size or remaining capacity (JMX, runtime metrics) |
| HTTP server / socket backlog | listen-queue length (`ss -lnt`, eBPF tooling) |
| Kafka consumer | `records-lag-max`, consumer-group lag |
| Database connection pool | `db.client.connection.pending_requests`, `db.client.connection.wait_time` (OTel) |

Bound the buffer from the delay budget, not from a multiple of Lq: limit ≈ μ × (latency budget − E[S]). Reject with backpressure (HTTP 429, gRPC `RESOURCE_EXHAUSTED`) when full. Example (illustrative): μ = 1000/s, budget 200 ms, E[S] = 5 ms → limit ≈ 195.

A FCFS arrival behind backlog Q waits Q/μ. The time to drain Q is Q/(μ − λ). Chart the wait, not the drain time, as the user-facing latency.

## Tiered SLOs on a shared pool

1. Collect per-class λ and service-time moments from traces, split by a span attribute such as `request.priority` or `user.tier`.
2. Compute per-class Wq with the non-preemptive priority formulas in [05-priority-queues](../../foundations-queueing-theory/assets/templates/queueing-theory/05-priority-queues.md).
3. Check Wq_k + E[S_k] against each tier's SLO. If the top tier fails, throttle the lower tier or add capacity.
4. Low-priority wait grows without bound as total load approaches capacity. Reserve capacity or a minimum share for the lower tier to prevent starvation.
5. Dashboard: p99 per `priority` label, with the predicted wait as an overlay.

## Pitfalls

| Pitfall | Why it misleads | Fix |
|---|---|---|
| Alert on raw p99 with no ρ context | At low load, p99 reflects service-time spread, not queueing. Pages fire with nothing to fix. | Gate the p99 alert on ρ > ρ* (derived as above) or page on queue depth instead. |
| Page on CPU > 80% alone | ρ does not show whether a queue has formed. At ρ = 0.8 with Poisson arrivals, M/M/1 gives Lq = 3.2, while CV²_s = 3 gives Lq ≈ 6.4 (P-K). Same ρ, twice the queue. | Alert on queue depth; treat ρ as a warning. |
| Alert only on the slow service | A slow downstream raises upstream time in system (Little's Law), so upstream SLOs breach next. | Add end-to-end critical-path latency alerts from traces alongside per-service alerts. |
| Read p99/p50 as CV²_s | Quantile ratios do not identify the second moment. | Compute CV² from the service-time sample. |

## Related

- [methods-red-use-golden.md](methods-red-use-golden.md): which saturation metrics to collect
- [slo-design-guide.md](slo-design-guide.md): latency SLIs as ratios, not quantiles
- [alerting-strategies.md](alerting-strategies.md): multi-window burn-rate alerts
- [performance-profiling-guide.md](performance-profiling-guide.md): measuring service time
- [reliability-theory-applied.md](reliability-theory-applied.md), [control-theory-applied.md](control-theory-applied.md), [information-theory-applied.md](information-theory-applied.md)

## Sources

- Little, J. D. C. (1961). "A Proof for the Queuing Formula: L = λW." *Operations Research* 9(3), 383–387.
- Kingman, J. F. C. (1961). "The Single Server Queue in Heavy Traffic." *Proc. Cambridge Philosophical Society* 57(4), 902–904.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research* 5(4), 518–521.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
