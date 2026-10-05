---
description: Decision rules for multi-server sizing (Allen-Cunneen, square-root staffing), scheduling-discipline sensitivity (FCFS vs processor sharing), and overload behaviour (retries, goodput, shedding).
status: stable
---

# Multi-Server Sizing, Disciplines, and Overload

Read this when you size a pool of more than one server, when you are unsure whether service-time variance matters for the scheduler, or when the system is at or above capacity and clients retry. Worked numbers were re-derived with a script (Erlang-B/C recursion).

## 1. G/G/c: Allen-Cunneen, not "one fast server"

**Rule.** For c servers with non-Poisson arrivals or non-exponential service:

```
Wq(G/G/c) ≈ Wq(M/M/c) × (CV²_a + CV²_s) / 2
```

This is the Allen-Cunneen approximation (Allen, *Probability, Statistics, and Queueing Theory with Computer Science Applications*, 2nd ed., Academic Press 1990). Whitt (1993) gives refined GI/G/m approximations when more accuracy is needed. Both are approximations, not bounds.

**Do not** model c servers as one server that is c times faster. That shortcut overstates Wq (about 14× at c = 10, ρ = 0.5; about 2× at c = 10, ρ = 0.8, against exact M/M/c) and understates response time, because each job still takes E[S] on one server.

**Worked example.** Voice-bot pool, λ = 0.5 calls/s, E[S] = 240 s, so offered load a = 120 Erlangs. SLO: mean wait ≤ 3 s.

| Model | Minimum c | ρ | Wq at that c |
|---|---|---|---|
| M/M/c (Erlang-C) | 134 | 0.896 | 2.48 s (c = 133 gives 3.15 s) |
| Allen-Cunneen, CV²_s = 2, CV²_a = 1 | 135 | 0.889 | 2.92 s |
| Fixed ρ ≤ 0.70 rule | 172 | 0.70 | far below SLO; 38 more than Erlang-C needs |

## 2. Square-root staffing and pooling

**Rule.** For a pooled M/M/c-like system, staff c ≈ a + β√a, where a = λE[S] and β sets the service level (Halfin & Whitt, *Operations Research* 29(3):567–588, 1981; Borst, Mandelbaum & Reiman, *Operations Research* 52(1):17–34, 2004). The spare capacity grows with √a, not with a, so the right utilization rises with scale.

Same SLO (Wq ≤ 3 s, E[S] = 240 s) at different scales:

| a (Erlangs) | Minimum c | β | ρ |
|---|---|---|---|
| 10 | 16 | 1.90 | 0.63 |
| 100 | 113 | 1.30 | 0.89 |
| 1000 | 1026 | 0.82 | 0.97 |

Consequences:
- **No fixed ρ target is portable.** ρ ≤ 0.70 over-provisions large pools and can under-provision small pools with tight SLOs. Derive c from the SLO.
- **Pooling beats partitioning.** Two separate pools of a = 60 each need 71 + 71 = 142 servers for the same SLO that one pooled a = 120 meets with 134. Partition only for isolation (noisy neighbours, priority, blast radius), and state that you are paying for it.
- **Uneven routing breaks pooling.** The pooled result assumes any idle server takes the next job. Random or hash routing across replicas behaves closer to separate queues; join-shortest-queue or power-of-d routing recovers much of the pooling gain.

**When not to use it:** heavy-tailed service, strong arrival autocorrelation, or abandonment. Use Allen-Cunneen for variability, an abandonment model (Erlang-A) when callers hang up, and trace simulation when tails are unstable.

## 3. Scheduling discipline changes which formulas apply

| Discipline | Mean response time (M/G/1) | Sensitive to CV²_s? | Typical systems |
|---|---|---|---|
| FCFS | `E[S] + ρ·E[S]·(1+CV²_s)/(2(1−ρ))` (P-K) | Yes | Single-threaded workers, FIFO job queues, connection-pool waits |
| Processor sharing (PS) | E[S]/(1−ρ) | No (mean only) | Time-sliced CPUs, thread-per-request servers, approximately GPU continuous batching |
| Loss (Erlang-B, M/G/c/c) | Blocking depends only on a and c | No (beyond the mean) | Trunks, license pools, drop-on-busy connection limits |

Example at ρ = 0.8, E[S] = 1, CV²_s = 9: FCFS mean response is 21, PS is 5. The "variance matters as much as utilization" advice (VUT) is an FCFS result. Under PS, a heavy tail barely moves the mean but still stretches the response time of the large jobs. Identify the discipline before choosing P-K or Kingman (Harchol-Balter 2013 covers PS and its insensitivity).

## 4. Overload: retries, goodput, and shedding

When ρ ≥ 1 no steady state exists, and the question becomes what happens to *useful* throughput.

**Retry amplification.** If each attempt fails with probability p and clients make up to k attempts, offered load is λ(1 + p + … + p^(k−1)). With k = 3 that is 1.11λ at p = 0.1 and approaches 3λ as p → 1. Retries at several layers multiply: three layers each making 3 attempts can send up to 27 attempts to the bottom layer. The Google SRE book ("Handling Overload") caps retries at three attempts per request, uses a per-client retry budget of about 10% of requests (which it says limits growth to about 1.1× in the general case), and retries at only one layer.

**Goodput collapse under FCFS.** Goodput = completions that finish before the client's deadline. With a backlog Q and service rate μ, a FCFS arrival waits about Q/μ. Once Q/μ exceeds the client timeout, the server spends full capacity on requests whose callers have already given up: CPU reads 100%, goodput reads near zero. Timed-out callers retry, which feeds the backlog. This self-sustaining state is a **metastable failure**: it persists after the trigger is gone (Bronson, Aghayev, Charapko & Zhu, HotOS 2021). The sustaining-loop analysis belongs to `foundations-distributed-systems` and `qa-resilience`; the queueing part is the Q/μ > timeout condition.

**Remedies, in order of leverage:**
1. **Bound the queue by delay, not length.** Drop or reject requests whose queue sojourn exceeds a target (CoDel-style; Nichols & Jacobson 2012). The bound in jobs is roughly μ × (delay budget − E[S]).
2. **Adaptive LIFO under backlog.** Serve FIFO normally and switch to LIFO when a queue forms, so fresh requests, which still have callers, are served first (Maurer, "Fail at Scale", *ACM Queue* 2015, which pairs it with CoDel and concurrency limits).
3. **Propagate deadlines** and discard work whose deadline has passed before starting it.
4. **Retry budgets and single-layer retries** to cap λ_eff.
5. **Admission control / load shedding** by criticality, so the system sheds low-value work first.

Adding capacity alone does not exit a metastable state if the retry loop keeps offered load above the new capacity. Shed or flush first, then scale.

## 5. Fan-out amplifies tails

If each of N parallel sub-requests independently exceeds its p99 with probability 1%, the whole request is slow with probability 1 − 0.99^N: 9.6% at N = 10 and 63% at N = 100. Dean & Barroso ("The Tail at Scale", *CACM* 56(2), 2013) describe hedged requests: send a second copy only after the first has been outstanding longer than a high percentile, which caps the extra load at roughly the tail fraction. Hedging adds load; do not hedge a system that is already overloaded. See primitive 11 for fork-join math.

## 6. Load-test validity (pointer)

Queueing predictions are only as good as the measurements used to fit them. A closed-loop load generator slows its own sending rate as latency rises and hides the knee of the curve; coordinated omission removes the slow samples from the percentiles. Use an open-loop (fixed arrival rate) generator for capacity tests. Tooling and methodology belong to `qa-testing-performance`.
