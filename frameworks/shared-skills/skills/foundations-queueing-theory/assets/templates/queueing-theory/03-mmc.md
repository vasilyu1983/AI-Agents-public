# Primitive 03 — M/M/c Queue (Multi-Server, Erlang-C)

**Source**: Kleinrock (1975); Erlang, A. K. (1917); Cooper (1981).

## Definition

The **M/M/c queue** extends M/M/1 to **c identical parallel servers**, each serving at rate μ. A single queue feeds all servers.

- Poisson arrivals at rate λ.
- Exponential service times, rate μ per server.
- c servers; shared infinite buffer.

**System utilization** (per server):

```
ρ = λ / (c × μ)
```

Stability requires **ρ < 1**.

### Erlang-C Formula (probability of waiting)

The probability that an arriving customer must wait (all servers busy):

```
C(c, a) = [ (a^c / c!) × (1 / (1 − ρ)) ] / [ Σ_{k=0}^{c-1} (a^k / k!) + (a^c / c!) × (1 / (1 − ρ)) ]
```

where **a = λ / μ** (offered traffic load in Erlangs).

### Key Metrics

| Metric | Formula |
|--------|---------|
| Probability of waiting | C(c, a) — Erlang-C |
| Mean wait in queue | Wq = C(c, a) / (c × μ − λ) |
| Mean time in system | W = Wq + 1/μ |
| Mean queue length | Lq = λ × Wq |
| Mean items in system | L = λ × W |

## When to Use

- **Sizing a thread pool or worker pool**: how many workers satisfy a target wait-time SLO?
- **Call center / support queue staffing**: determine agent count to keep 80% of callers waiting < 20 s.
- **Database connection pool sizing**: Erlang-C gives probability that all connections are busy.
- **API gateway concurrency**: model gateway workers against a Poisson traffic model.

Do NOT apply M/M/c when service times are non-exponential without verifying the approximation holds (use M/G/c or Kingman). Do NOT use Erlang-C when calls/requests may be blocked-and-cleared rather than queued (use Erlang-B, primitive 10).

## Inputs

| Input | Symbol | Source |
|-------|--------|--------|
| Arrival rate | λ | Requests/s or calls/s |
| Service rate per server | μ | 1 / mean_service_time |
| Number of servers | c | Current or candidate pool size |

## Outputs

- **C(c, a)**: probability of queuing (dimensioning KPI).
- **Wq**: mean wait time (SLO compliance).
- **Minimum c** to achieve target wait SLO.

## Erlang-C Table (exact, a = 10 Erlangs)

_Corrected 2026-07-11: prior values in this table were computed incorrectly (verified by recomputing the Erlang-B recursion and the Erlang-C conversion C(c,a) = c·B(c,a) / (c − a·(1−B(c,a))) in code). Recompute from the formula above rather than trusting any static table when a exact figure matters._

| c (servers) | ρ per server | C(c, 10) | Wq / (1/μ) |
|-------------|-------------|---------|------------|
| 11 | 0.909 | 0.682 | 0.682 service-times |
| 13 | 0.769 | 0.285 | 0.095 |
| 15 | 0.667 | 0.102 | 0.020 |
| 20 | 0.500 | 0.004 | 0.0004 |

Adding servers has diminishing returns. The relationship between c and Wq is convex: the last few servers buy the most SLO improvement at low utilization.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Erlang-C used for a loss system | Arrivals are dropped, not queued | Use Erlang-B (primitive 10) |
| Single utilization metric hides per-server overload | Routing is uneven (hot spots) | Model per-shard separately or use power-of-two-choices routing |
| Optimal c computed at ρ = 0.95 | Any measurement error triggers instability | Size for ρ ≤ 0.70–0.80 plus one spare server |
| Non-Poisson bursts ignored | Traffic is bursty (CV² > 1) | Apply Kingman correction (primitive 07) |

## Worked Example

A contact-center service receives **30 calls/min** (λ = 0.5 calls/s). Each call takes on average **2 s** of agent handling time (μ = 0.5 calls/s per agent). Offered load a = λ/μ = 1 Erlang.

Minimum stable c = 2 (otherwise a/c ≥ 1). With c = 2 agents:
- ρ = 0.5 / (2 × 0.5) = 0.50
- Erlang-C C(2, 1) ≈ 0.333
- Wq = 0.333 / (2 × 0.5 − 0.5) = 0.333 / 0.5 = 0.667 s

_Corrected 2026-07-11: the mean wait above is 0.667 seconds, not "40 seconds" as an earlier version of this file stated — that annotation was arithmetically wrong (0.667 s and 40 s differ by ~60×, suggesting a stray minutes↔seconds slip). At c = 2, the queue already clears a 30-second SLO comfortably; there is no capacity problem to fix at this traffic level._

With a third agent (c = 3): ρ = 0.33, C(3,1) ≈ 0.091 (recomputed; an earlier version of this file stated ≈0.053), Wq ≈ 0.091 s (recomputed; an earlier version stated ≈6.4 s). Adding the third agent still helps — it cuts mean wait by roughly 7× (0.667 s → 0.091 s) — but the business question is whether that improvement is worth the extra agent's cost, not whether a 30 s SLO is met, since 2 agents already meet it. This is the standard Erlang-C trap: **the marginal server buys a large relative latency improvement even when the absolute SLO was never at risk** — verify against the actual SLO before over-provisioning on relative-improvement intuition alone.

## Transient / Finite-Time Caveat

Classical Erlang-C results are steady-state only. Real systems are never permanently at steady state — autoscaling events, traffic bursts, and cold starts all create transient windows.

For systems that do not reach stationarity, apply finite-time mixing bounds from Nguyen, Varma, Maguluri (SIGMETRICS 2025). Key results:

- The M/M/c queue has a mixing time that scales with c and ρ; approaching the **Halfin-Whitt regime** (ρ near but below 1) maximizes the gap between transient and steady-state behavior.
- During scaling transitions (c changing), steady-state Erlang-C formulas are lower bounds on required capacity — actual wait times during the transition window will exceed steady-state predictions.
- Use finite-time bounds when: burst windows shorter than mixing time, autoscaling-in-progress, or SLO applies during cold-start.

**Rule of thumb**: if your measurement window is less than ~10 service times × c, the queue may not have reached stationarity; treat Erlang-C as optimistic.

## Autoscaling-as-Queue-Control

In cloud environments, c (the server or replica count) is dynamically adjustable. Treat c as a control variable in a multi-timescale policy:

1. **Short-horizon routing** (seconds): balance load across existing capacity using Erlang-C sizing to meet the wait-time SLO.
2. **Long-horizon scaling** (minutes–hours): adjust c based on traffic forecasts (SageServe pattern: Jaiswal et al., SIGMETRICS 2026). SageServe co-optimizes routing and VM/GPU scaling via traffic forecasting and Integer Linear Programming; validated at Microsoft Office 365 (10M+ requests/day, 3 regions, 25% GPU-hour savings).

**Caution**: Classic Erlang-C assumes c is fixed. For dynamic c, note that SLO violations spike during c-adjustment transitions — apply finite-time Erlang-C bounds (Nguyen et al. 2025, above) during scaling events to set conservative capacity floors.

**Kill criterion for SageServe pattern**: if traffic is memoryless (no forecastable structure), reactive Erlang-C sizing without forecasting may be adequate.

## Composition

- **Little's Law** (primitive 01): verify L = λ × W after computing W.
- **M/M/1** (primitive 02): degenerate case c=1; compare to confirm multi-server benefit.
- **Erlang-B** (primitive 10): use instead when system blocks rather than queues.
- **USL** (primitive 09): check whether adding servers encounters coherency overhead.

## Sources

- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. Chapter 4.
- Cooper, R. B. (1981). *Introduction to Queueing Theory* (2nd ed.). North-Holland.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. Chapter 14 ("Server Farms: M/M/k and M/M/k/k"). _(Corrected 2026-07-11: prior text cited Chapter 17, which is "Networks of Queues and Jackson Product Form" — see primitive 06.)_
