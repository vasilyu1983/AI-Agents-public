# Primitive 10 — Loss Systems and the Erlang-B Formula

**Source**: Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.

## Definition

A **loss system** (Erlang-B model) is one in which arriving customers who find all servers busy are **blocked and cleared** — they leave immediately without waiting. There is no queue.

Also called the **M/M/c/c queue** (c servers, capacity = c, no waiting room).

### Erlang-B Formula

Probability that an arriving customer is blocked (all c servers busy):

```
B(c, a) = (aᶜ / c!) / Σ_{k=0}^{c} (aᵏ / k!)
```

where **a = λ / μ** is the offered traffic load in **Erlangs** (dimensionless).

**Recursive computation** (numerically stable):

```
B(0, a) = 1
B(c, a) = (a × B(c−1, a)) / (c + a × B(c−1, a))
```

### Grade of Service (GoS)

In telephony and loss systems, **Grade of Service (GoS) = B(c, a)** is the fraction of calls lost. Typical targets: 1% (B=0.01) for voice, 0.01% (B=0.0001) for critical data.

## When to Use

- **Voice/video call capacity**: PSTN, WebRTC, conferencing — calls are dropped if no circuit is free.
- **Rate limiting / circuit breaker sizing**: requests exceeding capacity are rejected (not queued).
- **License pool management**: software licenses — process blocked if no license available (no wait).
- **Stateful connection pool (no backlog)**: if connection pool has no queue and rejects overflow, Erlang-B applies.
- **Satellite/radio channel allocation**: fixed channel capacity; excess traffic is lost.

Do NOT use Erlang-B when arriving customers will wait (use Erlang-C / M/M/c, primitive 03). Key question: **does the system queue or block?**

## Inputs

| Input | Symbol | Source |
|-------|--------|--------|
| Offered load | a = λ/μ | Traffic analysis (in Erlangs) |
| Number of servers / channels | c | Infrastructure sizing |
| Target blocking probability | B_target | SLA / GoS requirement |

## Outputs

- **B(c, a)**: probability of blocking (call loss rate).
- **Minimum c** to achieve target GoS at given load a.
- **Carried load**: a × (1 − B(c, a)) — actual throughput delivered.

## Erlang-B Reference Table (GoS ≤ 1%)

_Corrected 2026-07-11: recomputed via the Erlang-B recursion B(c,a) = a·B(c−1,a) / (c + a·B(c−1,a)); most rows in a prior version of this table understated the required c by one or more servers._

| Offered load a (Erlangs) | Required c (for ≤1% blocking) | B(c, a) achieved |
|--------------------------|------------------------------|-------------------|
| 1 | 5 | 0.0031 |
| 5 | 11 | 0.0083 |
| 10 | 18 | 0.0071 |
| 20 | 30 | 0.0085 |
| 50 | 64 | 0.0084 |
| 100 | 117 | 0.0098 |

Erlang-B has economies of scale: larger trunks are more efficient (fewer spare circuits per Erlang). Always recompute from the recursion above for a capacity commitment — do not read required-c off a static table.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Erlang-B used when system queues | System has a backlog/retry; blocking is not permanent | Use Erlang-C (primitive 03) for queuing systems |
| Erlang-C used when system drops | Thinking customers wait when they actually abandon | Use Erlang-B for drop/reject; Erlang-C with abandonment correction for partial patience |
| Peak traffic used without peaking factor | Busy-hour traffic ≠ average traffic | Determine busy-hour Erlang load; size for peak, not average |
| a computed from wrong time unit | Mix of call/min and service rate in calls/hr | Normalize units: a = λ (calls/s) / μ (service rate calls/s) |

## Worked Example

A WebRTC conferencing service supports up to c simultaneous calls. Each call lasts on average **20 min** (μ = 1/1200 calls/s). During peak hour, **60 calls/hr arrive** (λ = 60/3600 = 1/60 calls/s).

```
a = λ / μ = (1/60) / (1/1200) = 1200/60 = 20 Erlangs
```

Target: GoS = 1% (B ≤ 0.01). From Erlang-B table: **c = 30 channels** required.

With only c = 25 channels:
```
B(25, 20) ≈ 0.050 = 5.0% blocking
```

5.0% of calls are dropped — unacceptable for a conferencing service. Add 5 channels (total 30) to reach 1%.

**Carried load** at c=30: 20 × (1 − 0.01) = 19.8 Erlangs (98% of offered load delivered).

## Composition

- **M/M/c / Erlang-C** (primitive 03): complementary model — use Erlang-C when calls queue, Erlang-B when calls are blocked.
- **Little's Law** (primitive 01): carried load = mean occupancy Lc = a × (1 − B(c,a)); W = 1/μ (no queue in loss system).
- **Jackson networks** (primitive 06): loss systems can appear at one stage of a multi-stage network; model that stage separately with Erlang-B.

## Sources

- Erlang, A. K. (1917). "Solution of some Problems in the Theory of Probabilities of Significance in Automatic Telephone Exchanges." *Post Office Electrical Engineers' Journal*, 10, 189–197.
- Cooper, R. B. (1981). *Introduction to Queueing Theory* (2nd ed.). North-Holland. Chapter 3.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
