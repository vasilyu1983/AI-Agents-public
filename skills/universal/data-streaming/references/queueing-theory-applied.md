# Queueing Theory Applied to Data Streaming

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. This file only maps the theory to streaming decisions. Definitions, derivations, and assumptions live in the foundation.

Streaming systems are queueing systems. A keyed Kafka partition is a single-server queue. A Flink operator subtask is a G/G/1 queue. A controller quorum is a coordination-bound system that USL can describe. This file says which model to use for which streaming decision, gives worked examples, and lists the domain pitfalls.

**Theory owners (read these for formulas and assumptions):**

| Topic | Owner |
|-------|-------|
| Little's Law | [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) |
| M/M/1 | [02-mm1.md](../../foundations-queueing-theory/assets/templates/queueing-theory/02-mm1.md) |
| M/M/c (Erlang-C), square-root staffing | [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md) |
| M/G/1 (Pollaczek-Khinchine) | [04-mg1-pollaczek-khinchine.md](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md) |
| Jackson networks | [06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) |
| Kingman G/G/1 | [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) |
| Bufferbloat, queue limits | [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md) |
| USL | [09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md) |
| Fork-join | [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md) |
| G/G/c (Allen-Cunneen), pooling, overload, retries, tail at scale | [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md) |

**No portable utilization target.** Do not size to a fixed ρ such as 0.70 or 0.75. Derive c and ρ from the wait SLO and the measured variability (CV²_a, CV²_s). For pooled consumers use square-root staffing; for keyed partitions use the per-partition model in P1.

## Table of Contents

- [Patterns](#patterns)
  - [P1 Partition Sizing: Per-Partition Queues, Not One Shared Pool](#p1-partition-sizing-per-partition-queues-not-one-shared-pool)
  - [P2 Consumer Parallelism from Little's Law on Lag](#p2-consumer-parallelism-from-littles-law-on-lag)
  - [P3 Producer Flow as Jackson-Network Input Rate](#p3-producer-flow-as-jackson-network-input-rate)
  - [P4 Bufferbloat in Batch Sizes and Commit Intervals](#p4-bufferbloat-in-batch-sizes-and-commit-intervals)
  - [P5 USL Detection in Coordinator-Bound Topologies](#p5-usl-detection-in-coordinator-bound-topologies)
- [Anti-Patterns](#anti-patterns)
  - [A1 Partition Count Set Without Little's Analysis](#a1-partition-count-set-without-littles-analysis)
  - [A2 Buffer Sizes Large "for Resilience" Creating Bufferbloat](#a2-buffer-sizes-large-for-resilience-creating-bufferbloat)
  - [A3 Ignoring Service-Time Variability in Stream Processors](#a3-ignoring-service-time-variability-in-stream-processors)
  - [A4 Fork-Join Sized by Mean Across Operators](#a4-fork-join-sized-by-mean-across-operators)
- [Recipes](#recipes)
  - [R1 Partition Plan: λ → Consumer Service Time → Per-Partition Queue → Safety Factor](#r1-partition-plan-λ--consumer-service-time--per-partition-queue--safety-factor)
  - [R2 Lag SLO: Little's Law on Lq vs Latency Target](#r2-lag-slo-littles-law-on-lq-vs-latency-target)
  - [R3 Coordinator Scaling Check: USL Retrograde Detection](#r3-coordinator-scaling-check-usl-retrograde-detection)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 Partition Sizing: Per-Partition Queues, Not One Shared Pool

**Model.** In a classic consumer group, each partition goes to exactly one consumer, and keyed messages are pinned to their partition. A message waiting on a busy partition cannot move to an idle consumer. So a topic with c partitions is **c independent single-server queues**, each receiving λ/c under uniform keys. It is not one M/M/c pool. Per-partition ρ = (λ/c) × E[S] must be < 1, and per-partition wait follows [M/M/1](../../foundations-queueing-theory/assets/templates/queueing-theory/02-mm1.md), or [Kingman](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) when CV² ≠ 1.

Only a pool where any idle consumer can take any waiting message behaves like M/M/c (Erlang-C): Kafka share groups (KIP-932), Pulsar Shared subscriptions, or a plain work queue. For those, use Erlang-C for Poisson/exponential inputs and Allen-Cunneen for other variability ([multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md)).

**Worked example (uniform keys, M/M/1 per partition).** λ = 50,000 msg/s, E[S] = 2 ms, Wq target = 10 ms. The smallest c that meets the target is **121** (ρ = 0.83, Wq = 9.5 ms). Hot keys make this worse: the hottest partition, not the average, sets the lag SLO.

**Why it matters.** Erlang-C applied to keyed partitions understates wait badly. In the R1 example, Erlang-C says 121 partitions give Wq ≈ 4.7 ms; the per-partition model gives ≈ 630 ms at the same c (both with the same Kingman factor), about 130× more.

**Shared pools only.** At ρ = 0.9, the Erlang-C probability of waiting depends strongly on c: about 0.67 at c = 10, 0.36 at c = 50, 0.22 at c = 100. That is the pooling effect; keyed partitions do not get it.

**Platform specifics.**

- **Kafka / Redpanda**: partition count can grow later, but growing it remaps keys and can break per-key ordering. Plan headroom up front. Share groups (KIP-932; check that your broker and client versions support them) are the one Kafka mode where M/M/c applies.
- **Flink**: keyed operators pin records to a subtask by key group, so each subtask is its own queue. Raising parallelism lowers per-subtask ρ.
- **Pulsar**: Exclusive and Failover subscriptions follow the per-partition model. Shared subscriptions let several consumers drain one partition and approach M/M/c.
- **Kinesis**: shards are the c analog. Look up the current per-shard write and read limits (bytes/s and records/s) in the Kinesis Data Streams quotas page. Model λ and μ in bytes/s against those limits, then apply the per-shard model.

---

### P2 Consumer Parallelism from Little's Law on Lag

**Model.** [Little's Law](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md) links **mean** lag L, produce rate λ, and **mean** time in system W: L = λW. For a latency SLO, L_max = λ × W_target is the mean lag at which the mean wait hits the target.

**Wait vs drain.** Two different numbers come out of a lag reading. Keep them apart:

- **Wait of a new message (FCFS):** a message that arrives behind backlog Q waits about Q / μ_consume, where μ_consume is the group's total consume rate.
- **Drain time:** the backlog clears in Q / (μ_consume − λ). This is how long recovery takes, not the latency any message sees.

**Worked example — Kafka consumer group.**

- λ = 80,000 msg/s, W_target = 5 s, so L_max = 400,000 messages (mean).
- Current lag: 1,200,000 messages. Excess over L_max: 800,000.
- Each consumer can process 10,000 msg/s at full speed.
- Goal: keep up with λ and clear the 800,000 excess in 10 minutes. Extra rate = 800,000 / 600 ≈ 1,333 msg/s. Total = 81,333 msg/s. Consumers = ceil(81,333 / 10,000) = **9** (ρ ≈ 0.89 in steady state).
- With 9 consumers (90,000 msg/s): a new message behind 1.2 M waits about 1,200,000 / 90,000 ≈ **13 s**. The 800,000 excess drains in 800,000 / (90,000 − 80,000) = **80 s**, well inside the 10-minute goal.
- Consumers cannot exceed the partition count in a classic group. If partitions = 8, add partitions first.

**Platform notes.** For Flink, replace "consumer" with "task slot" and watch per-subtask input queue depth. For Kinesis, iterator age (`GetRecords.IteratorAgeMilliseconds`) is already a time: it is the age of the last record read, so compare it to W_target directly; it is not L.

---

### P3 Producer Flow as Jackson-Network Input Rate

**Model.** A pipeline is an open [Jackson network](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md) only under Poisson arrivals, exponential service, probabilistic routing, and stable stations. Streaming pipelines rarely meet all of that. The traffic equations still find each stage's λᵢ and the bottleneck (highest ρᵢ) without product form.

**Worked example — Flink enrichment pipeline.** External rate γ = 100,000 msg/s.

| Stage | μ per slot | Slots | ρ |
|-------|-----------|-------|---|
| Enrichment (all cache hits) | 150,000/s | 4 | 0.167 |
| Aggregation | 80,000/s | 4 | 0.313 |

Now 90% of enrichment lookups miss the cache and take a slow path at 30,000/s:

```
E[S] = 0.10/150,000 + 0.90/30,000 = 30.67 µs  →  μ ≈ 32,609/s per slot
ρ_enrichment = 100,000 / (4 × 32,609) ≈ 0.767   ← bottleneck
```

This assumes one pooled, balanced set of four slots that serially process the mixture. Dedicated fast/slow pools need their own rates; key skew needs per-slot measurements. Scaling partitions or sink parallelism does nothing until enrichment is fixed.

**Pitfalls.**
- If γ exceeds the bottleneck capacity and back-pressure does not reach producers, the bottleneck queue grows without bound while downstream stages sit idle.
- After you scale the bottleneck, re-solve the traffic equations. The bottleneck moves to the next-highest ρ.

---

### P4 Bufferbloat in Batch Sizes and Commit Intervals

**Model.** [Bufferbloat](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md): a buffer larger than the delay budget adds standing delay without adding throughput. In streaming it lives in `max.poll.records`, Pulsar `receiverQueueSize`, producer `linger.ms`/`batch.size`, Flink network buffers, and checkpoint intervals.

**Size a buffer from the delay budget.** A FCFS item behind Q items waits Q / μ, where μ is the rate that drains the buffer. So:

```
buffer_limit ≈ μ × (W_budget − E[S])
```

Do not size from "2–3× the average queue" or from habit.

**Worked examples.**

- **`max.poll.records`.** E[S] = 0.5 ms, so μ = 2,000 records/s per consumer. A poll of 5,000 takes 2.5 s; its last record waits about 2.5 s after fetch. For W_budget = 100 ms: limit ≈ 2,000 × 0.0995 ≈ **200 records**, not 5,000.
- **Pulsar `receiverQueueSize`.** Check the client's default in the Pulsar docs. With a queue of 1,000 and a consumer that drains 10,000 msg/s, a full prefetch queue adds 1,000 / 10,000 = **100 ms** before `receive()`. For latency-sensitive paths set it near μ × (W_budget − E[S]).
- **Flink checkpoints.** A long checkpoint interval lowers overhead but raises the replay window after failure; alignment pauses can build input backlog that later bursts downstream. Choose the interval from recovery-time and latency targets and check p99 during checkpoints.

`max.poll.interval.ms` is not a lag or latency control. It is a liveness timeout: if the gap between `poll()` calls exceeds it, the consumer is removed from the group and a rebalance starts. Raising it hides slow processing; it does not reduce lag. Fix slow batches by lowering `max.poll.records` or speeding up processing.

---

### P5 USL Detection in Coordinator-Bound Topologies

**Model.** [USL](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md): throughput X(N) with contention σ and coherency κ. With κ > 0, throughput peaks at N_max = √((1 − σ)/κ) and then falls. N must be a concurrency or size variable (controllers, brokers, task managers, partitions), not an offered-load rate.

**Where it shows up.**

- **Kafka KRaft controller quorum.** Every metadata change (leader election, ISR change, reassignment) is a Raft write that the quorum must acknowledge. Coordination cost grows with partition count, churn rate, and inter-controller RTT. Symptoms: rising metadata-operation latency, slow leader elections, client timeout spikes.
- **Flink JobManager.** Checkpoint coordination, heartbeats, and failover run through one JobManager. Symptoms near N_max: checkpoint time grows faster than cluster size; heartbeat timeouts rise; recovery time spikes.
- **Kinesis KCL leases.** The DynamoDB lease table coordinates shard ownership. Lease-renewal latency vs shard count is the curve to fit; do not assume a fixed shard threshold.

---

## Anti-Patterns

### A1 Partition Count Set Without Little's Analysis

**Diagnosis.** Partition count comes from habit ("10 last time", "one per broker"), not from λ, E[S], and a per-partition wait SLO.

**Worked example.** λ = 60,000 msg/s, E[S] = 5 ms, offered load a = λ × E[S] = 300.
- 32 partitions: per-partition ρ = 300 / 32 = 9.4. Unstable.
- 512 partitions: ρ = 0.586, per-partition Wq ≈ 7 ms. Stable, but likely over-provisioned unless the SLO is that tight. Extra partitions cost log segments, replication, controller metadata, slower rebalances, and coordinator load (P5).

**Fix.** Run R1 with measured λ, E[S], CV²_a, CV²_s. Use the per-partition model (M/M/c only for share groups). Do not round the result up to a power of 2: Kafka's default partitioner hashes keys modulo the partition count, so a power of 2 buys nothing. Record the derivation in the topic contract so it can be re-run.

---

### A2 Buffer Sizes Large "for Resilience" Creating Bufferbloat

**Diagnosis.** `max.poll.records = 10,000`, `receiverQueueSize = 5,000`, or maximal Flink network buffers, set without computing the delay they add.

**What goes wrong.** With 5,000 records prefetched and E[S] = 1 ms, the last record waits about 5 s after fetch. Throughput looks fine and broker lag looks low, because the records have left the broker. End-to-end latency (event time to processing time) is what breaks, and lag alerts do not see it.

**Fix.** Size each buffer from P4: `limit ≈ μ × (W_budget − E[S])`, with μ the drain rate of that buffer. Bound Flink in-flight data with the network memory settings and confirm back-pressure metrics fire when buffers fill.

---

### A3 Ignoring Service-Time Variability in Stream Processors

**Diagnosis.** Sizing assumes constant service time. Real operators mix cache hits and misses, variable deserialization, external calls, and GC pauses.

**Worked example ([P-K](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md)).** ρ = 0.70, E[S] = 5 ms, CV²_s = 3 (illustrative):

```
Wq = 0.70 × 5 ms × (1 + 3) / (2 × 0.30) = 23.3 ms
M/M/1 (CV² = 1):                          11.7 ms
```

Variability doubles the wait. The ratio (1 + CV²)/2 does not depend on ρ, but the absolute error grows as ρ → 1. With bursty arrivals too, use [Kingman](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md) for one server and Allen-Cunneen for c servers. Do not approximate c servers by a single server with E[S]/c.

**Pitfalls.**
- Do not infer CV² from p99/p50. Tail ratios do not identify the second moment. Compute CV² = Var(S)/E[S]² from the per-record service-time sample.
- A cache hit/miss mix is not automatically CV² ≈ 3. For example, 1 ms hits and 20 ms misses with a 5 ms mean give CV² ≈ 2.4 if each path is constant; measure it.

**Fix.** Record per-operator service-time histograms, compute CV², and feed it into R1. For high-CV² operators, isolate the slow path (separate slot sharing group or separate operator) so fast records do not queue behind slow ones.

---

### A4 Fork-Join Sized by Mean Across Operators

**Diagnosis.** A scatter-gather enrichment (K parallel lookups) or a multi-partition window join is estimated with the mean branch time. Completion waits for the **slowest** branch.

**What the theory supports.** E[max] = E[S] × H_K (H_K = 1 + 1/2 + … + 1/K) is exact only for K iid exponential service times with no queueing. Example under that assumption: K = 5, E[S] = 50 ms gives 114 ms; K = 10 gives 146 ms. With queueing at the branches, correlated branches, or non-exponential service, no fixed correction factor applies. Simulate or model the joint maximum ([11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md)).

**Streaming cases.**
- A window join over K partitions closes when the slowest partition's watermark passes. One slow partition delays every window.
- Tail at scale: if each branch is slow 1% of the time independently, 1 − 0.99^10 = 9.6% of 10-way requests and 1 − 0.99^100 = 63% of 100-way requests hit at least one slow branch.

**Fix.** Hedge requests after a timeout, return partial results when not all K are required, cap slow branches with timeouts and fallbacks, and use Flink watermark idleness for idle partitions. See [multiserver-overload-and-disciplines.md](../../foundations-queueing-theory/references/multiserver-overload-and-disciplines.md) for tail-at-scale fan-out.

---

## Recipes

### R1 Partition Plan: λ → Consumer Service Time → Per-Partition Queue → Safety Factor

**Goal.** Derive a partition count before topic creation. A keyed consumer group is c independent per-partition queues, with a Kingman factor for variability. For share groups or Pulsar Shared subscriptions, swap in a pooled G/G/c model (P1).

**Step 1: Measure inputs.**

| Input | Symbol | How to measure |
|-------|--------|----------------|
| Peak arrival rate | λ | Burst peak from a load test or producer metrics |
| Mean processing time | E[S] | Consumer profiling: record-to-commit histogram |
| Arrival CV² | CV²_a | Inter-arrival variance / mean²; > 1 for batchy producers |
| Service CV² | CV²_s | Service-time variance / mean² from the sample |
| Queue-wait SLO | Wq_SLO | End-to-end target minus the other budget terms (R2 Step 1) |
| Key skew | — | Share of traffic on the hottest partition |

**Step 2: Find the minimum partition count.**

```python
import math

def per_partition_wait(c, lam, E_S, CV2_a=1.0, CV2_s=1.0):
    """Keyed consumer group: c independent queues, each receiving lam/c (uniform keys)."""
    mu = 1.0 / E_S
    lam_p = lam / c
    rho = lam_p / mu
    if rho >= 1.0:
        return rho, float("inf")
    Wq_mm1 = rho / (mu - lam_p)                    # M/M/1 mean queue wait
    return rho, Wq_mm1 * (CV2_a + CV2_s) / 2.0     # Kingman G/G/1 variability factor

def find_min_partitions(lam, E_S, Wq_SLO, CV2_a=1.0, CV2_s=1.0):
    c = math.floor(lam * E_S) + 1                  # smallest c with rho < 1
    for c in range(c, c + 5000):
        rho, Wq = per_partition_wait(c, lam, E_S, CV2_a, CV2_s)
        if Wq <= Wq_SLO:
            return {"min_c": c, "rho": round(rho, 3), "Wq_ms": round(Wq * 1000, 1)}
    return {"error": "no stable c found in search range"}

result = find_min_partitions(lam=40_000, E_S=0.003, Wq_SLO=0.020, CV2_a=1.5, CV2_s=2.0)
# → {'min_c': 152, 'rho': 0.789, 'Wq_ms': 19.7}
```

The binding constraint is per-partition utilization: with a Kingman factor of 1.75 and E[S] = 3 ms, the 20 ms target needs ρ ≤ 0.79, so c ≥ 120 / 0.79 ≈ 152. The ρ comes out of the SLO and CV²; it is not an input. An Erlang-C (shared-pool) version returns 121 partitions at ρ = 0.99. That is valid only for share groups; if the topic is keyed it gives about 630 ms mean wait.

**Step 3: Headroom and skew.**
- Size for the hottest partition when skew is measurable: use λ_hot = (hot share) × λ in place of λ/c.
- Add headroom for forecast growth, because adding partitions later remaps keys. The size of the margin is a planning choice (a 25% margin, giving 190 partitions here, is illustrative, not a sourced rule).
- Record λ, E[S], CV²_a, CV²_s, Wq_SLO, skew, and the chosen c in the [topic contract](../assets/topic-contract-template.md). Re-run when peak λ or E[S] changes materially.

**Step 4: Check with Little's Law.** Mean queue occupancy at the target is λ × Wq_SLO = 40,000 × 0.020 = 800 messages. One lag reading above 800 does not prove a violation; measure queue age and end-to-end quantiles.

**Verification checks.**
- Measured `lag / λ` over a stable window ≤ Wq_SLO at peak.
- Per-partition Wq predicted from measured ρ and CV² is within the SLO, and the hottest partition's queue age stays inside it.

---

### R2 Lag SLO: Little's Law on Lq vs Latency Target

**Goal.** Turn an end-to-end latency SLO into lag alert thresholds that fire before the SLO is breached.

**Step 1: Split the budget.**

```
Wq_budget = W_total_SLO − W_broker − W_processing − W_sink_commit
```

Example (Kafka → Flink → Kafka): 500 ms SLO, 5 ms broker, 100 ms processing (measured), 10 ms sink commit → Wq_budget = **385 ms**.

**Step 2: Convert to lag thresholds.** Use the consume rate for per-message wait (P2) and the produce rate for the Little's Law mean:

```
L_max (mean, Little's Law)   = λ × Wq_budget        = 50,000 × 0.385 = 19,250 messages
L_wait (new message waits Wq_budget at FCFS) = μ_consume × Wq_budget
```

If consumers can run faster than λ, L_wait is the looser bound on an instantaneous reading. An alert at half of L_max (9,625 messages) is an illustrative early-warning choice.

**Step 3: Separate transient from sustained lag.** Little's Law holds for long-run averages. Short bursts spike lag without breaking the long-run SLO.

```
Warn:     rolling_average(lag, 5 min) > L_alert
Critical: lag > L_max AND lag_growth_rate > 0
```

Lag that is high but falling is recovery; report its drain time Q / (μ_consume − λ). Lag that is growing means λ > μ_consume.

**Step 4: Check partition structure.** With keyed partitions, check the hottest partition's queue age, not only total lag. If lag sits near L_max at peak, re-run R1 with fresh λ and E[S].

**Worked example — Kinesis.** 20 shards, 1 MB/s written per shard, iterator-age target 10 s. Mean in-flight data per shard at the target is 1 MB/s × 10 s = 10 MB. Alert on iterator age directly (it is already a time): warn at 5 s, critical at ≥ 10 s and rising. The thresholds are illustrative.

**Verification checks.**
- In steady state, `lag / λ ≤ Wq_budget`.
- Replay a past incident and confirm the warning fires before the SLO breach at the observed lag growth rate.
- Normal spikes do not page (tune the rolling window).

---

### R3 Coordinator Scaling Check: USL Retrograde Detection

**Goal.** Before adding brokers, partitions, replication, or task managers, check whether the coordinator (KRaft quorum or Flink JobManager) is near its USL peak.

**Step 1: Pick N and X.** N is a size or concurrency variable (for example partition count, broker count, or task managers). X is the throughput you care about (for example metadata operations completed per minute). Do not use an offered-load rate as N: a sweep of "requests per minute in vs completions out" measures saturation, not coherency.

**Step 2: Measure X at several N and fit.** Fit σ, κ with nonlinear least squares ([09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md) has the fitting code).

```
N:  100   500   1,000  2,000  5,000  10,000
X:   95   460     840  1,340  2,100   2,800
```

Fitting these illustrative points gives σ ≈ 0.0003 and κ ≈ 0: a contention plateau with no retrograde in range. The curve is flattening, but USL does not predict a peak here. (If N in these points is an offered rate, the flattening is saturation; see Step 1.)

**Step 3: Act on the fit.**

| Fit | Meaning | Action |
|-----|---------|--------|
| κ ≈ 0, σ small | Near-linear scaling | Safe to scale; re-measure after growth |
| κ ≈ 0, σ large | Contention plateau | Find and split the serialized resource |
| κ > 0, N well below N_max | Safe region | Proceed; track N / N_max as a headroom metric |
| κ > 0, N near N_max | Retrograde close | Do not add partitions or task managers; cut coordination load first |
| N past N_max | Retrograde | Reduce coordination load (merge low-traffic topics, split Flink jobs) |

The "well below" and alert levels are judgment calls; set them from how fast N grows and how long remediation takes.

**Remediation.**
- Kafka: merge low-traffic topics, move high-churn topics to a separate cluster, and run dedicated controller nodes so broker traffic does not share the controllers' resources.
- Flink: use incremental checkpoints (RocksDB state backend), split large applications into smaller jobs, and consider reactive mode (`scheduler-mode: reactive`, standalone deployments).

**Verification.** After a change, re-measure and re-fit. Confirm N_max rose (or κ fell) and that lag at the same produce rate went down.

---

## Composition

Apply the recipes in this order:

| Layer | Recipe | Stabilizes | Precondition |
|-------|--------|-----------|--------------|
| 1. Coordinator headroom | R3 USL check | KRaft / JobManager not retrograde | Before large partition or cluster growth |
| 2. Partition plan | R1 per-partition sizing | Consumers not saturated | Coordinator has headroom |
| 3. Lag SLO | R2 thresholds | Latency SLO met | Partitions sized from R1 |

**Interactions.**
- P4 → R2: large prefetch buffers move lag out of the broker's view. Shrink buffers before trusting R2 thresholds.
- P3 → R1: the bottleneck operator's E[S] and CV²_s feed R1. Re-run R1 when the bottleneck moves.
- P5 gates P1: more partitions lower per-partition wait but raise coordinator load. Run R3 before large partition increases.

**Minimum metrics.**

| Metric | Source | Used by |
|--------|--------|---------|
| Consumer lag per partition and group | Kafka AdminClient / MSK / Confluent | R2, hottest-partition check |
| Produce rate per topic | Broker `BytesInPerSec` / `MessagesInPerSec` | R1, R2 |
| Per-record service-time histogram (mean and CV²) | Consumer application | R1, A3 |
| Metadata operation rate and latency | KRaft controller metrics | R3 |
| Checkpoint duration | Flink metrics | R3, P4 |
| Back-pressure per operator | Flink Web UI / REST | P4, A2 |

---

## Sources

- Little, J. D. C. (1961). "A Proof for the Queuing Formula: L = λW." *Operations Research*, 9(3), 383–387.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer.
- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11).
- Apache Kafka documentation — consumer configs (`max.poll.records`, `max.poll.interval.ms`), KRaft, KIP-932 share groups.
- Apache Flink documentation — checkpointing, network buffers, reactive mode.
- Apache Pulsar documentation — subscription types, `receiverQueueSize`.
- Amazon Kinesis Data Streams documentation — shard limits, KCL leases, iterator age.

**Sibling applied reference:** [control-theory-applied.md](control-theory-applied.md) — lag-aware autoscaler, producer circuit breaker, watermark tuning.
