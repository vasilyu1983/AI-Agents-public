# Primitive 01 — Little's Law (L = λW)

**Source**: John D. C. Little, "A Proof for the Queuing Formula: L = λW," Operations Research, 9(3), 1961.

## Definition

**Little's Law** states that for any stable system in steady state:

```
L = λ × W
```

| Symbol | Meaning | Unit |
|--------|---------|------|
| L | Average number of items in the system (queue + service) | items / jobs / requests |
| λ | Average arrival rate | items per time unit |
| W | Average time an item spends in the system | time units |

The law is distribution-free: it holds regardless of arrival distribution, service distribution, or number of servers, provided the system is ergodic (time-averaged = ensemble-averaged) and in steady state.

## When to Use

- **Initial capacity sizing**: derive one unknown (L, λ, W) from the other two.
- **SLO validation**: if you know target latency W and throughput λ, you can bound queue depth L.
- **Bottleneck detection**: unexpected L/λ ratio reveals hidden latency.
- **Dashboard sanity-checking**: confirm that observed request depth, rate, and latency are mutually consistent.

Do NOT apply Little's Law across non-stationary windows (burst periods, startup transients) or across different queue populations (request queue vs. thread pool are separate systems).

## Inputs

| Input | Symbol | How to measure |
|-------|--------|----------------|
| Arrival rate | λ | Requests/sec from access logs or metrics |
| Mean latency | W | p50 or mean response time (not p99 — that requires tail analysis) |
| Mean queue depth | L | Concurrency gauge, inflight counter |

## Outputs

- The third quantity given the other two.
- Consistency check: if measured L ≠ λ × W, either the system is not in steady state, or measurement windows are misaligned.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| L/λ ≠ W despite stable system | Mixed populations (HTTP and batch in same counter) | Separate queue populations; apply Little's Law to each independently |
| Non-stationary window | Burst traffic measured over short window | Use a window ≥ 10× mean service time for stationarity |
| p99 used for W | Heavy tail biases the mean | Use arithmetic mean latency, not percentiles |
| Ignoring think time in users | External think time counted as part of W | Model closed-loop systems with closed-form corrections |

## Worked Example

A payment API handles **500 req/s** (λ = 500) with mean response time **80 ms** (W = 0.08 s).

```
L = λ × W = 500 × 0.08 = 40 requests in-flight at any moment
```

If the infrastructure team observes 200 in-flight requests but still 500 req/s, then either:
- Mean latency is actually 0.4 s (400 ms) — a hidden slowdown, or
- The counter includes queued-but-not-yet-dispatched requests.

This discrepancy surfaces a measurement or architecture problem before it becomes an incident.

## Composition

- Combine with **M/M/1** (primitive 02) or **M/M/c** (primitive 03) to split L into queue component Lq and service component Ls.
- Use as a sanity check after applying **Kingman's formula** (primitive 07) — Little's Law validates that predicted W is consistent with observed L and λ.

## Sources

- Little, J. D. C. (1961). "A Proof for the Queuing Formula: L = λW." *Operations Research*, 9(3), 383–387.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. Chapter 6 ("Little's Law and Other Operational Laws"). _(Corrected 2026-07-11: prior text cited Chapter 9, which is "Ergodicity Theory" — verified against the publisher's chapter list.)_
