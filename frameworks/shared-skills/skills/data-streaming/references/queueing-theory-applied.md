# Queueing Theory Applied to Data Streaming

> **Gate before invoking:** Check [`foundations-queueing-theory` § When to Apply](../../foundations-queueing-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Streaming systems are queueing systems in disguise. A Kafka topic partition is a queue with one logical server (the consumer). A Flink operator is an M/G/1 queue whose service-time distribution is the per-record processing duration. A Kafka broker controller quorum is a coherency-bound multi-server system governed by USL. This reference maps the 11 queueing-theory primitives from `foundations-queueing-theory` to concrete streaming failure modes in Kafka, Flink, Pulsar, and Kinesis pipelines.

## Table of Contents

- [Patterns](#patterns)
  - [P1 Partition Sizing via M/M/c Thinking](#p1-partition-sizing-via-mmc-thinking)
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
  - [R1 Partition Plan: λ → Consumer Service Time → M/M/c → Safety Factor](#r1-partition-plan-λ--consumer-service-time--mmc--safety-factor)
  - [R2 Lag SLO: Little's Law on Lq vs Latency Target](#r2-lag-slo-littles-law-on-lq-vs-latency-target)
  - [R3 Coordinator Scaling Check: USL Retrograde Detection](#r3-coordinator-scaling-check-usl-retrograde-detection)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 Partition Sizing via M/M/c Thinking

**Primitive**: [M/M/c (Erlang-C)](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)

**What it is.** A Kafka topic with P partitions and a consumer group with C consumers (one consumer per partition at saturation) is structurally an M/M/c queue: arrivals enter the topic at rate λ msg/s, each consumer serves messages at rate μ (the reciprocal of per-message processing time E[S]), and there are c = P = C servers. The offered load in Erlangs is a = λ/μ. Stability requires ρ = λ/(c × μ) < 1.

The Erlang-C formula gives the probability a message must wait before a consumer picks it up:

```
C(c, a) = [ (a^c / c!) × 1/(1 − ρ) ] /
           [ Σ_{k=0}^{c-1} (a^k / k!) + (a^c / c!) × 1/(1 − ρ) ]
```

Mean wait in queue (lag-to-consumption latency):

```
Wq = C(c, a) / (c × μ − λ)
```

**Streaming application.** Before creating a topic, collect:
- `λ` — peak message arrival rate (msg/s), measured from a representative load test or production sample.
- `E[S]` — mean processing time per message by the consumer application (ms), profiled under realistic message sizes and enrichment calls.
- `μ = 1 / E[S]`.

Then solve for the minimum c that satisfies a target Wq SLO:

```python
# Pseudocode: find minimum partition count c
import math

def erlang_c(c, a):
    rho = a / c
    if rho >= 1:
        return 1.0  # unstable
    erlang_b_inv = sum((a**k) / math.factorial(k) for k in range(c))
    erlang_b_inv += (a**c / math.factorial(c)) * (1 / (1 - rho))
    P_wait = (a**c / math.factorial(c)) * (1 / (1 - rho)) / erlang_b_inv
    return P_wait

lam = 50_000   # msg/s peak
E_S = 0.002    # 2 ms per message
mu  = 1 / E_S  # 500 msg/s per consumer thread
a   = lam / mu # 100 Erlangs offered load
Wq_SLO = 0.010  # 10 ms target queue wait

for c in range(int(a) + 1, int(a) * 3):
    rho = a / c
    Ec  = erlang_c(c, a)
    Wq  = Ec / (c * mu - lam)
    if Wq <= Wq_SLO:
        print(f"Minimum partitions: {c}, ρ = {rho:.2f}, Wq = {Wq*1000:.1f} ms")
        break
```

**Key insight.** At ρ = 0.9 (a common "intuitive" partition count), C(c,a) is typically 0.50–0.80 — meaning 50–80% of messages wait in queue. Sizing to ρ ≤ 0.70 reduces C(c,a) to below 0.15 for most workloads. Add one safety partition beyond the formula result to absorb Kingman variance at bursty arrivals (CV²_a > 1 from irregular producer batching).

**Platform specifics.**

- **Kafka / Redpanda**: partition count is set at topic creation and can be increased later (but increasing splits existing key ranges, potentially breaking ordering for key-based consumers). Plan with a 2× headroom factor over the M/M/c minimum to avoid a costly repartition.
- **Flink**: operator parallelism is the analog of c. Increasing `setParallelism()` adds servers to the M/M/c pool. Ensure upstream network shuffle matches downstream parallelism to avoid re-keying bottlenecks.
- **Pulsar**: partition count maps directly; each partition has one set of consumers per subscription. The same M/M/c analysis applies. Pulsar's subscription modes (exclusive, shared, failover) change whether multiple consumers are active per partition.
- **Kinesis**: shard count is the c analog. Each shard supports 1 MB/s ingest and 2 MB/s read. Model λ in bytes/s and E[S] as bytes processed per second per consumer before applying M/M/c.

---

### P2 Consumer Parallelism from Little's Law on Lag

**Primitive**: [Little's Law](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md)

**What it is.** Consumer lag — the offset distance between the producer's head and the consumer's committed offset — is the queue depth L in Little's Law:

```
L = λ × W
```

Where:
- `L` = lag (messages), measured per consumer group from Kafka AdminClient or Flink consumer group offsets.
- `λ` = message arrival rate (msg/s), the current produce rate.
- `W` = average time a message spends in the queue before being consumed (seconds) — the end-to-end processing latency budget.

Rearranging: given a latency SLO `W_target`, the maximum allowable lag is:

```
L_max = λ × W_target
```

Any lag above `L_max` means the pipeline is violating its latency SLO at the current produce rate.

**Consumer count from lag budget.** If lag is growing at rate `dL/dt = λ_produce − λ_consume`, the number of consumer instances N needed to drain it at rate sufficient to maintain L ≤ L_max is:

```
Required throughput per instance = (λ_produce + dL/dt_target) / N
```

Where `dL/dt_target` is the rate at which you want to drain excess lag (zero for steady-state; positive for backfill recovery).

**Worked example — Kafka consumer group.**

- Produce rate: λ = 80,000 msg/s.
- End-to-end latency SLO: W = 5 s.
- L_max = 80,000 × 5 = 400,000 messages.
- Current lag: L = 1,200,000 messages → SLO violated.
- Each consumer processes 10,000 msg/s at ρ = 0.70.
- To maintain produce rate AND drain 800,000-message backlog in 10 minutes (600 s):
  - Required extra throughput = 800,000 / 600 ≈ 1,333 msg/s extra.
  - Total required = 80,000 + 1,333 = 81,333 msg/s.
  - Consumers needed = ceil(81,333 / 10,000) = 9.
- Note: N ≤ partition count (Kafka); if partitions = 8, add a partition first.

**Flink task slot sizing.** Replace "consumer instance" with "task slot." If one task slot processes 10,000 records/s, Little's Law directly dictates the minimum slot count to hold lag below L_max. Monitor per-subtask input queue depth in the Flink Web UI — a growing backlog at an operator indicates the upstream M/M/c sizing is incorrect.

**Pulsar / Kinesis analogs.** The same L = λW relationship holds. For Kinesis, L is the iterator-age metric (seconds behind head). Set iterator-age alerts at `W_target / 2` to fire before SLO breach.

---

### P3 Producer Flow as Jackson-Network Input Rate

**Primitive**: [Jackson Networks](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md)

**What it is.** A streaming pipeline is an open Jackson network: each operator or service is a station with arrival rate λᵢ, service rate μᵢ, and server count cᵢ. The overall throughput ceiling is the station with the highest utilization ρᵢ = λᵢ/(cᵢ × μᵢ). Because Jackson's product-form theorem holds, each station can be analyzed as an independent M/M/c queue once the traffic equations are solved.

**Traffic equations for a streaming pipeline.**

```
λᵢ = γᵢ + Σⱼ λⱼ × Pⱼᵢ
```

For a linear pipeline (no fan-out): λ passes through each stage unchanged. For pipelines with fan-out (Flink side outputs, topic forks), λᵢ is the product of upstream rate and branching probability.

**Example — Flink enrichment pipeline.**

```
Kafka source → [Deserializer] → [Enrichment join] → [Aggregation] → Kafka sink
     γ = 100k msg/s              μ = 150k/s           μ = 80k/s
     c = 1 (logical)             c = 4 slots           c = 4 slots
     ρ = –                       ρ = 100k/(4×150k)     ρ = 100k/(4×80k)
                                   = 0.167 (fine)        = 0.313 (fine)
```

Now suppose the Enrichment join involves an external lookup with 90% cache miss re-routing to a slower path:

```
Effective μ_enrichment = 0.10 × 150k + 0.90 × 30k = 15k + 27k = 42k/s per slot
ρ_enrichment = 100k / (4 × 42k) = 0.595  ← bottleneck
```

The Jackson analysis reveals the enrichment stage is the bottleneck — not because it is slow on average, but because 90% of messages hit the slow path. Scaling partition count or sink parallelism without addressing this does nothing.

**Producer input rate as system-level λ.** The total produce rate γ (from all upstream producers) is the external arrival rate into the Jackson network. When the bottleneck station saturates (ρ → 1), back-pressure must propagate to producers. Without back-pressure, the network enters instability: queue depths grow unboundedly at the bottleneck station even as downstream stations sit idle. This is the open-loop instability modeled in Jackson networks when γ > min_i(cᵢ × μᵢ).

**After scaling a bottleneck.** Solve the traffic equations again after adding parallelism to a stage. The bottleneck shifts to the next highest-ρ station. Teams that scale one operator and declare the pipeline fixed routinely discover the next bottleneck within days.

---

### P4 Bufferbloat in Batch Sizes and Commit Intervals

**Primitive**: [Bufferbloat](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md)

**What it is.** In streaming, bufferbloat manifests as large in-process buffers that absorb traffic spikes while silently accumulating latency. Unlike network bufferbloat (oversized router queues), streaming bufferbloat lives in:

- `max.poll.records` on Kafka consumers — each poll fetches a large batch, but per-message latency = (batch size / throughput).
- Flink checkpoint intervals — a long interval reduces overhead but delays state recovery and increases reprocessing window.
- Pulsar `receiverQueueSize` — large queue enables throughput but adds queueing delay per message.
- Kafka producer `linger.ms` and `batch.size` — large batches improve throughput but increase producer-side latency.

**The BDP rule for streaming.** In network bufferbloat, the correct buffer size is the Bandwidth-Delay Product:

```
Optimal_buffer = RTprop × bottleneck_rate
```

The streaming analog: the correct in-flight message count at any stage is the product of the stage's processing rate and the maximum acceptable per-message delay at that stage:

```
Optimal_queue_depth = throughput × W_target
```

This is exactly Little's Law in reverse: use L_max = λ × W_target as the buffer ceiling. Buffers larger than L_max create standing queues with no additional throughput benefit.

**Checkpoint interval bufferbloat.** Flink checkpointing introduces a periodic latency spike during which the operator pauses record processing to serialize state. If the checkpoint interval T_ck is large, records accumulate in the input buffer during checkpoint — up to `λ × T_ck` messages. After checkpoint completes, these messages are processed in a burst that temporarily saturates the downstream stage.

A practical starting point: `T_ck = 5 × mean_checkpoint_duration`. Shorten if latency spikes during checkpoints appear in p99 metrics. Do not lengthen purely to reduce overhead — the recovery cost rises proportionally with T_ck.

**Kafka `max.poll.records` bufferbloat.**

A consumer configured with `max.poll.records = 5000` and processing time per record of 0.5 ms processes each poll batch in 2.5 s. The last record in a 5000-record poll waits up to 2.5 s from fetch to process — even though the broker could have served it immediately. Correct sizing:

```
max.poll.records = W_target / E[S]
                 = latency_SLO_seconds / mean_processing_time_per_record_seconds
```

For W_target = 100 ms, E[S] = 0.5 ms: max.poll.records = 200 records, not 5000.

**Pulsar receiverQueueSize.** The consumer prefetch queue (`receiverQueueSize`, default 1000) holds messages before the application calls `receive()`. At 10,000 msg/s, a queue of 1000 adds 100 ms of deterministic queueing latency before the message reaches application code. For latency-sensitive pipelines, reduce `receiverQueueSize` to `W_target × throughput_per_consumer`.

---

### P5 USL Detection in Coordinator-Bound Topologies

**Primitive**: [Universal Scalability Law (USL)](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md)

**What it is.** The USL models throughput X(N) as a function of the number of parallel processors N:

```
X(N) = λ × N / (1 + σ(N − 1) + κN(N − 1))
```

Where σ is the contention coefficient (serialized resource) and κ is the coherency coefficient (cross-node coordination cost). When κ > 0, adding nodes past N_max = sqrt((1−σ)/κ) **reduces** throughput — retrograde scaling.

**Kafka KRaft controller quorum.** Kafka 4.0 is KRaft-only (ZooKeeper removed). The KRaft quorum uses a Raft consensus protocol among controller nodes. Each metadata operation (partition leader election, reassignment, ISR change) requires a quorum write through the controller log. This is a coherency operation: all controller replicas must acknowledge. The coherency coefficient κ for the controller scales with:

- Number of controller nodes (quorum size).
- Frequency of metadata events (partition count × reassignment rate).
- Network round-trip between controller nodes.

At small cluster sizes (3–5 controllers), κ is negligible and throughput scales linearly with added partitions. At large clusters with high partition churn, the controller quorum becomes the bottleneck. Symptoms: metadata operation latency rises, leader election storms lag behind, producer/consumer client timeouts spike.

**Detect retrograde before it occurs.** Run load tests at controller-event throughput N = 100, 200, 500, 1000, 2000 partition reassignments/min. Fit σ and κ:

```python
from scipy.optimize import curve_fit
import numpy as np

def usl(N, lam, sigma, kappa):
    return lam * N / (1 + sigma * (N - 1) + kappa * N * (N - 1))

N_vals = np.array([100, 200, 500, 1000, 2000])
X_vals = np.array([...])  # measured throughput at each N

params, _ = curve_fit(usl, N_vals, X_vals, p0=[10, 0.01, 0.001])
lam, sigma, kappa = params
N_max = np.sqrt((1 - sigma) / kappa) if kappa > 0 else float('inf')
print(f"N_max = {N_max:.0f} partition-events/min before retrograde")
```

**Flink JobManager coherency.** The Flink JobManager (in standalone or session cluster mode) is a coordinator-bound singleton. All task state checkpoints, heartbeats, and failover decisions route through the JobManager. USL applies: adding task managers increases coordination load on the JobManager proportionally. Symptoms of approaching N_max: checkpoint completion time grows super-linearly with cluster size; task heartbeat timeout rate rises; job recovery time after failover spikes.

Fix: shard across multiple Flink clusters (one Flink cluster per logical pipeline group), size JobManager on high-memory nodes, and reduce checkpoint coordination overhead by using incremental checkpoints (`EnableIncrementalCheckpointing`) and tuning `heartbeat.interval` and `heartbeat.timeout`.

**Kinesis shard coordinator.** The Kinesis shard iterator lease management (via KCL or Flink Kinesis connector) has analogous coherency cost: the DynamoDB lease table is the coordinator. At large shard counts (>200 shards), lease renewal becomes a coordination bottleneck. Apply USL analysis to lease renewal latency vs. shard count before scaling beyond 100 shards.

---

## Anti-Patterns

### A1 Partition Count Set Without Little's Analysis

**Diagnosis.** The topic is created with a partition count chosen by heuristic ("we did 10 last time"; "one partition per broker") rather than by deriving the minimum c from the offered load a = λ/μ and the Erlang-C wait-time SLO.

**What goes wrong.** At λ = 60,000 msg/s and E[S] = 5 ms per message (μ = 200 msg/s per consumer):
- Offered load: a = 60,000 / 200 = 300 Erlangs.
- Heuristic: "32 partitions" → ρ = 300 / 32 = 9.4 → ρ >> 1 → unstable.
- Heuristic: "512 partitions" → ρ = 300 / 512 = 0.586 → stable, but C(512, 300) ≈ 0.01 (over-provisioned by 2×).

Both outcomes are wrong for opposite reasons. Under-partitioned topics saturate immediately. Over-partitioned topics waste memory (each partition has its own log segment, replication overhead, and controller metadata), slow rebalances, and inflate coordinator coherency cost (P5).

**Queueing theory diagnosis.** Without Little's Law to bound the required partition count and Erlang-C to find the minimum c satisfying the wait-time SLO, partition count is set by cargo cult. The P-K correction (CV² on arrival burstiness, primitive 04) and Kingman's formula (primitive 07) are never applied — so the designed system systematically underestimates peak latency at high-CV arrival patterns.

**Fix.** Apply Recipe R1. Start from measured or estimated λ and E[S]. Compute the minimum c from M/M/c. Add 20–30% safety margin. Round up to the nearest power of 2 (Kafka key-routing efficiency). Document the derivation in the topic contract so future changes can re-run the calculation.

---

### A2 Buffer Sizes Large "for Resilience" Creating Bufferbloat

**Diagnosis.** A platform engineer sets `max.poll.records = 10,000`, `receiverQueueSize = 5,000`, or Flink network buffer size to the maximum ("more buffers = better throughput, more resilience during spikes") without computing the resulting queueing delay.

**What goes wrong.** At 5,000 records in the consumer prefetch queue and E[S] = 1 ms per record, the last record in the batch waits 5 s before being processed — regardless of how fast the broker can deliver it. The pipeline reports excellent throughput and zero lag from the broker's perspective, while end-to-end latency (event_time to processing_time) is 5× the latency SLO. Monitoring shows "no lag" because the consumer is consuming; the latency problem is invisible to lag-based alerts.

**Bufferbloat framing.** The large prefetch queue is the streaming analog of an oversized router buffer. The queue absorbs all traffic at the cost of deterministic latency inflation equal to `queue_depth / consumer_throughput`. Good throughput coexists with latency violation — the classic bufferbloat signature.

**Kingman amplification.** For a Flink operator with bursty upstream output (CV²_a > 1, which is typical for windowed aggregations that release batches periodically), Kingman's formula predicts:

```
Wq ≈ (ρ / (1 − ρ)) × E[S] × (CV²_a + CV²_s) / 2
```

A large downstream buffer absorbs the Kingman-predicted queue without signaling backpressure — but it does so by adding the exact latency that the formula predicts. The buffer doesn't eliminate the latency; it just hides it from operators.

**Fix.** Derive buffer bounds from Little's Law: `L_max = λ × W_target`. Configure `max.poll.records`, `receiverQueueSize`, and Flink network buffer counts to be no larger than L_max. For Flink, tune `taskmanager.network.memory.fraction` and `taskmanager.network.memory.min` to control the total in-flight buffer pool. Use `backpressure.level` monitoring to confirm backpressure signals are flowing correctly when buffers fill.

---

### A3 Ignoring Service-Time Variability in Stream Processors (CV² on G/G/1)

**Diagnosis.** Capacity planning assumes that all messages take the same time to process (deterministic service time, CV² = 0) or that variability is negligible. In practice, stream processors have high CV²: messages may hit cache or miss, trigger complex deserialization, call external enrichment APIs with variable latency, or trigger GC pauses.

**P-K formula impact.** For an M/G/1 queue (Poisson arrivals, general service), the P-K formula is:

```
Wq = (ρ × E[S] × (1 + CV²)) / (2 × (1 − ρ))
```

At ρ = 0.70, E[S] = 5 ms, CV² = 3 (typical for a Flink enrichment operator mixing cache hits at 1 ms and cache misses at 20 ms):

```
Wq = (0.70 × 0.005 × (1 + 3)) / (2 × 0.30) = 0.014 / 0.60 = 23.3 ms
```

Under the M/M/1 assumption (CV² = 1):

```
Wq_MM1 = (0.70 × 0.005 × 2) / 0.60 = 11.7 ms
```

The real Wq is 2× the M/M/1 estimate because of variability alone. At 90% utilization the error compounds further: (1 + CV²)/2 = 2 at CV² = 3, and the (1−ρ) denominator amplifies any underestimate.

**Kingman generalization.** When arrivals are also bursty (windowed upstream operators releasing batches, periodic Flink checkpoints creating micro-pauses), Kingman's G/G/1 formula applies:

```
Wq ≈ (ρ / (1 − ρ)) × E[S] × (CV²_a + CV²_s) / 2
```

Teams that size Flink parallelism from mean throughput (ignoring both CV²_a and CV²_s) observe p99 latency 3–10× above the mean — not from traffic spikes, but from the structural latency inflation of variability.

**Fix.** Measure service-time distributions per Flink operator using the `numRecordsInPerSecond` and `numBytesInPerSecond` JMX metrics combined with custom latency histograms. Compute CV² from the histogram. Apply P-K or Kingman correction to the parallelism sizing. For operators with high CV², consider priority scheduling (Flink slot groups with dedicated resources) to isolate low-CV fast-path messages from high-CV slow-path messages.

---

### A4 Fork-Join Sized by Mean Across Operators

**Diagnosis.** A Flink pipeline fans out to K parallel enrichment operators (or a Kafka consumer triggers K parallel external lookups) and the response time is estimated as the mean per-worker service time E[S]. The fork-join completion time is actually governed by the **slowest worker**, not the mean.

**Fork-join formula.** For K parallel workers with exponential service time E[S]:

```
E[max(S₁, ..., Sₖ)] = E[S] × H_K
```

where H_K = 1 + 1/2 + 1/3 + ... + 1/K (harmonic number).

For K = 5 enrichment lookups each averaging 50 ms: E[max] = 50 × (1 + 0.5 + 0.333 + 0.25 + 0.2) = 50 × 2.283 = 114 ms — 2.28× the mean. For K = 10: 50 × 2.93 = 146 ms.

**Flink side-output fan-out.** A Flink operator that emits to 5 downstream operators and waits for all 5 to complete (e.g., a scatter-gather enrichment pattern) faces this completion distribution. If any one operator is at ρ = 0.70, its M/M/1 wait time Wq = ρ/(μ(1−ρ)) = 2.33 × E[S] per-operator. The join waits for the maximum — the tail of the maximum distribution is much heavier than the tail of any individual operator.

**Kafka parallel consumer with aggregation.** A join processor consuming from K partitions and waiting for all K partitions to contribute to a window result is a fork-join queue: the window closes when the slowest partition produces its event for the window period. Late-arriving events from a single slow partition delay the entire window result by E[max] rather than E[mean].

**Fix.** Apply the H_K correction before committing to a fan-out design. For K > 5, consider: (1) speculative execution — issue the request to a second worker if the first exceeds a timeout; (2) returning best-effort partial results if not all K workers are required; (3) capping slow workers with timeouts and routing to fallback paths. See [Primitive 11 — Fork-Join](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md).

---

## Recipes

### R1 Partition Plan: λ → Consumer Service Time → M/M/c → Safety Factor

**Goal.** Derive a defensible Kafka (or Pulsar/Kinesis) partition count from first principles before topic creation, using M/M/c Erlang-C analysis, with a Kingman variance adjustment for bursty arrivals.

**Primitives used.**
- M/M/c (Erlang-C) → [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)
- Little's Law → [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md)
- Kingman's Formula → [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md)

**Step 1: Measure or estimate inputs.**

| Input | Symbol | How to measure |
|-------|--------|----------------|
| Peak message arrival rate | λ | Burst p95 from load test or upstream producer metrics |
| Mean processing time per message | E[S] | Consumer profiling: record-to-commit latency histogram |
| Arrival CV² | CV²_a | Measure inter-arrival time variance; >1 for bursty batch producers |
| Service CV² | CV²_s | Measure processing time variance; >1 for enrichment with variable lookup times |
| Latency SLO for queue wait | Wq_SLO | End-to-end target minus broker propagation time |

**Step 2: Compute minimum partition count from Erlang-C.**

```python
import math

def erlang_c(c, a):
    rho = a / c
    if rho >= 1.0:
        return 1.0
    sum_terms = sum((a**k) / math.factorial(k) for k in range(c))
    last_term  = (a**c / math.factorial(c)) * (1.0 / (1.0 - rho))
    return last_term / (sum_terms + last_term)

def find_min_partitions(lam, E_S, Wq_SLO, CV2_a=1.0, CV2_s=1.0):
    mu = 1.0 / E_S
    a  = lam / mu         # offered load in Erlangs
    c_min = math.ceil(a) + 1  # minimum stable c

    for c in range(c_min, c_min + 500):
        rho = a / c
        Ec  = erlang_c(c, a)

        # M/M/c base wait
        Wq_mmc = Ec / (c * mu - lam)

        # Kingman correction for variability (G/G/c approximation)
        Wq_kingman = Wq_mmc * (CV2_a + CV2_s) / 2.0

        if Wq_kingman <= Wq_SLO:
            safety_c = math.ceil(c * 1.25)   # 25% safety margin
            return {
                "min_c":    c,
                "safe_c":   safety_c,
                "rho":      round(rho, 3),
                "Wq_ms":    round(Wq_kingman * 1000, 1),
            }
    return {"error": "no stable c found in search range"}

# Example: high-volume order events
result = find_min_partitions(
    lam      = 40_000,    # 40k msg/s peak
    E_S      = 0.003,     # 3 ms per message
    Wq_SLO   = 0.020,     # 20 ms queue wait SLO
    CV2_a    = 1.5,       # mildly bursty producer batching
    CV2_s    = 2.0,       # enrichment service time has high variance
)
# → {"min_c": 168, "safe_c": 210, "rho": 0.714, "Wq_ms": 19.8}
```

**Step 3: Verify with Little's Law.**

```
L_max = λ × Wq_SLO = 40,000 × 0.020 = 800 messages max allowable queue depth
```

If the Kafka consumer group lag monitor shows L > 800 at peak, the system is violating the latency SLO regardless of what per-message processing metrics show.

**Step 4: Apply safety factor and document.**

- Round `safe_c` up to the next power of 2 (cleaner key distribution for hash-partitioned topics).
- Record `λ`, `E[S]`, `CV²_a`, `CV²_s`, `Wq_SLO`, and `safe_c` in the topic contract (see `assets/topic-contract-template.md`).
- Set a re-run trigger: when peak λ grows by ≥ 20% or E[S] changes by ≥ 30%, recompute.

**Verification checks.**

- `consumer_lag_sum / λ ≤ Wq_SLO` at peak traffic.
- Consumer group ρ_observed ≤ 0.75 sustained (USL headroom).
- Erlang-C C(safe_c, a) < 0.05 (less than 5% of messages wait in queue).

---

### R2 Lag SLO: Little's Law on Lq vs Latency Target

**Goal.** Translate a consumer latency SLO (end-to-end message latency) into a concrete lag threshold for alerting, and show when a lag alert should fire before the latency SLO is breached.

**Primitives used.**
- Little's Law → [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md)
- M/M/c (Erlang-C) → [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)
- Bufferbloat → [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md)

**Step 1: Decompose end-to-end latency budget.**

```
W_total = W_broker_propagation + W_queue_wait + W_processing + W_sink_commit

Wq_budget = W_total_SLO − W_broker_propagation − W_processing − W_sink_commit
```

For a Kafka → Flink → Kafka sink pipeline:
- W_total_SLO = 500 ms.
- W_broker_propagation ≈ 5 ms (local broker, replication to ISR).
- W_processing = E[S] per Flink operator (measure from `numRecordsOutPerSecond` and operator latency histograms).
- W_sink_commit ≈ 10 ms (Kafka producer linger + ack).
- Wq_budget = 500 − 5 − 100 − 10 = 385 ms.

**Step 2: Convert Wq_budget to L_max (the lag alert threshold).**

```
L_max = λ × Wq_budget

Example: λ = 50,000 msg/s, Wq_budget = 0.385 s
L_max = 50,000 × 0.385 = 19,250 messages
```

Set the consumer group lag alert at `L_alert = 0.5 × L_max = 9,625 messages`. This fires before the SLO is breached, giving the on-call team time to act.

**Step 3: Distinguish steady-state lag from transient lag.**

Little's Law requires steady-state. A burst of short-duration will spike lag without violating the long-run SLO. Use a sustained-breach condition:

```
Alert if: rolling_average(lag, window=5min) > L_alert
Critical if: lag > L_max AND lag_growth_rate > 0 (lag not draining)
```

Lag that is high but draining (growth rate < 0) is a recovery event — annoying but not an SLO breach. Lag that is growing (growth rate > 0) means λ_produce > λ_consume and the system is accumulating debt.

**Step 4: Adjust for Erlang-C structure.**

At exactly L_max = λ × Wq_budget, the Erlang-C model says the queue is at capacity for the given partition count. If L routinely approaches L_max at peak, the partition count is too small or the consumer is undersized. Re-run R1 with the updated λ and E[S] measurements.

**Worked example — Kinesis pipeline.**

- Kinesis stream: 20 shards, each reading at up to 2 MB/s.
- Iterator age (Kinesis's lag equivalent): target ≤ 10 s.
- Produce rate: λ = 1 MB/s per shard.
- L_max in bytes = 1,000,000 × 10 = 10 MB per shard in-flight.
- Alert threshold: iterator age ≥ 5 s.
- Critical threshold: iterator age ≥ 10 s AND growing.

**Verification checks.**

- During steady-state: `lag / λ ≤ Wq_budget` (Little's Law holds).
- Alert fires ≥ 2 min before latency SLO breach at observed lag growth rate.
- No false positives during normal load spikes (use the `rolling_average` window to suppress transients).

---

### R3 Coordinator Scaling Check: USL Retrograde Detection

**Goal.** Before scaling a Kafka cluster (adding brokers, increasing partition count, increasing replication factor) or a Flink cluster (adding task managers), detect whether the coordinator (KRaft controller quorum or Flink JobManager) is approaching the USL retrograde region. Prevent the scenario where adding infrastructure reduces observed throughput.

**Primitives used.**
- USL → [09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md)
- M/M/c → [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)
- Little's Law → [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md)

**Step 1: Define the coordination load metric N.**

For Kafka KRaft: N = metadata operations per minute (partition leader elections + ISR changes + reassignments). Measure from the KRaft controller metrics (`kafka.controller:type=KafkaController,name=ActiveControllerCount` and `MetadataChangeRateAndTimeMs`).

For Flink JobManager: N = task heartbeats per second + checkpoint coordination operations per second. Measure from Flink JMX: `numTasksTotal`, `lastCheckpointDuration`, `totalNumberOfCheckpoints`.

**Step 2: Run coordination load tests at increasing N.**

```
Kafka KRaft example:
- N = 100 partition reassignments/min  → X = 95 completions/min
- N = 500                               → X = 460
- N = 1,000                             → X = 840
- N = 2,000                             → X = 1,340
- N = 5,000                             → X = 2,100  ← growth slowing
- N = 10,000                            → X = 2,800  ← near plateau
```

**Step 3: Fit USL parameters.**

```python
import numpy as np
from scipy.optimize import curve_fit

def usl(N, lam, sigma, kappa):
    return lam * N / (1 + sigma * (N - 1) + kappa * N * (N - 1))

N_data = np.array([100, 500, 1000, 2000, 5000, 10000])
X_data = np.array([95, 460, 840, 1340, 2100, 2800])

(lam_fit, sigma_fit, kappa_fit), _ = curve_fit(
    usl, N_data, X_data, p0=[1.0, 0.01, 0.0001],
    bounds=([0, 0, 0], [np.inf, 1, 1])
)

if kappa_fit > 0:
    N_max = np.sqrt((1 - sigma_fit) / kappa_fit)
    print(f"λ={lam_fit:.3f}, σ={sigma_fit:.4f}, κ={kappa_fit:.6f}")
    print(f"N_max = {N_max:.0f} coordination ops/min before retrograde")
    print(f"Current headroom: {N_max - N_data[-1]:.0f} ops/min")
else:
    print("κ ≈ 0: no retrograde detected in this range; Amdahl plateau only")
```

**Step 4: Interpret and act.**

| USL Result | Interpretation | Action |
|------------|---------------|--------|
| κ ≈ 0, σ small | Linear or near-linear scaling | Safe to scale; revisit at 2× current N |
| κ ≈ 0, σ large | Amdahl plateau — contention on serialized resource | Find and shard the serialized resource (e.g., KRaft log segment, JobManager state store) |
| κ > 0, N < N_max × 0.6 | In safe scaling regime | Proceed; monitor headroom metric |
| κ > 0, N approaching N_max | Retrograde imminent | Do not add partitions or task managers; reduce σ and κ first |
| N already past N_max | Retrograde confirmed | Scale down coordination load (reduce partition count, merge topics, split Flink cluster) |

**Step 5: Kafka-specific remediation if retrograde detected.**

- Reduce partition count for low-traffic topics (combine topics with similar retention and consumer SLAs).
- Increase controller leader election timeout to reduce frequency of reassignments (`controller.quorum.election.timeout.ms`).
- Separate high-churn topics (frequently reassigned) from stable topics across different Kafka clusters.
- Move to KRaft mode with dedicated controller nodes (separate from broker roles) to eliminate broker→coordinator cross-traffic.

**Flink-specific remediation.**

- Enable Flink incremental checkpoints (`EnableIncrementalCheckpointing`) to reduce checkpoint state transferred through JobManager.
- Use reactive mode (`scheduler-mode: reactive`) to decouple task slot allocation from JobManager scheduling decisions.
- Split a large Flink application into multiple smaller jobs to distribute coordinator load.

**Verification checks.**

- After intervention: re-run load test series and re-fit USL. Confirm N_max has increased.
- Ongoing: expose `coordination_ops_per_min / N_max_fitted` as a capacity headroom metric in the operational dashboard. Alert at 70% of N_max.
- Confirm with Little's Law: after retrograde remediation, `X(N_new) > X(N_old)` and lag at constant produce rate decreases.

---

## Composition

The three recipes compose into a pipeline capacity stack. Apply in order — each layer sets preconditions for the next:

| Layer | Recipe | Stabilizes | Precondition |
|-------|--------|-----------|--------------|
| 1. Coordinator headroom | R3 USL check | KRaft / JobManager not in retrograde | Run before increasing partition count or cluster size |
| 2. Partition plan | R1 Erlang-C sizing | Consumers not saturated | Coordinator has headroom from R3 |
| 3. Lag SLO enforcement | R2 Little's Law threshold | Latency SLO met continuously | Partitions and consumers sized from R1 |

**Cross-pattern interactions.**

- P4 (Bufferbloat) interacts with R2: a large `max.poll.records` hides lag from the broker's perspective while inflating W. Reduce buffer sizes before relying on R2 lag thresholds.
- P3 (Jackson network) feeds R1: the bottleneck operator's E[S] and CV²_s are inputs to the partition plan. If the bottleneck shifts after scaling (Jackson), re-run R1 with updated numbers.
- P5 (USL) gates P1 (M/M/c partition sizing): adding partitions past the KRaft N_max makes individual partition wait times better while making coordinator metadata latency worse — net outcome negative. Always run R3 before R1 when adding more than 20% to current partition count.

**Observability minimum for this stack.**

| Metric | Source | Used By |
|--------|--------|---------|
| `consumer_lag_sum` per group | Kafka AdminClient / MSK / Confluent | R2 alert threshold |
| `lambda_produce_rate` per topic | Kafka broker `BytesInPerSec` | R1 input, R2 L_max |
| `consumer_process_time_p50` | Consumer application histogram | R1 E[S] input |
| `consumer_process_time_cv2` | Consumer application histogram | R1 Kingman correction |
| `metadata_ops_per_min` | KRaft controller JMX | R3 USL N input |
| `checkpoint_duration_ms` | Flink JMX | R3 coordination load proxy |
| `backpressure_level` per operator | Flink Web UI / REST API | P4 bufferbloat detection |

---

## Sources

- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. — M/M/1, M/M/c, M/G/1, Jackson networks.
- Kleinrock, L. (1976). *Queueing Systems, Vol. 2: Computer Applications*. Wiley-Interscience. — Computer system applications of queueing theory.
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press. — P-K, fork-join, scheduling.
- Gunther, N. J. (2007). *Guerrilla Capacity Planning*. Springer. — USL, retrograde scaling.
- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11). — Bufferbloat definition and BDP rule.
- Little, J. D. C. (1961). "A Proof for the Queuing Formula: L = λW." *Operations Research*, 9(3), 383–387.
- Jackson, J. R. (1957). "Networks of Waiting Lines." *Operations Research*, 5(4), 518–521.
- Apache Kafka documentation — KRaft mode, controller quorum sizing, partition management.
- Apache Flink documentation — checkpoint configuration, JobManager scaling, operator parallelism.
- Apache Pulsar documentation — receiver queue, subscription modes, flow control.
- Amazon Kinesis documentation — shard limits, KCL lease management, iterator age metrics.

**Primitive cross-references** (full definitions in `foundations-queueing-theory`):

- [01-littles-law.md](../../foundations-queueing-theory/assets/templates/queueing-theory/01-littles-law.md)
- [03-mmc.md](../../foundations-queueing-theory/assets/templates/queueing-theory/03-mmc.md)
- [04-mg1-pollaczek-khinchine.md](../../foundations-queueing-theory/assets/templates/queueing-theory/04-mg1-pollaczek-khinchine.md)
- [06-jackson-networks.md](../../foundations-queueing-theory/assets/templates/queueing-theory/06-jackson-networks.md)
- [07-kingman-formula.md](../../foundations-queueing-theory/assets/templates/queueing-theory/07-kingman-formula.md)
- [08-bufferbloat.md](../../foundations-queueing-theory/assets/templates/queueing-theory/08-bufferbloat.md)
- [09-usl-universal-scalability.md](../../foundations-queueing-theory/assets/templates/queueing-theory/09-usl-universal-scalability.md)
- [11-fork-join-parallel.md](../../foundations-queueing-theory/assets/templates/queueing-theory/11-fork-join-parallel.md)

**Sibling applied reference:**
- [control-theory-applied.md](control-theory-applied.md) — Control-theory recipes for streaming: lag-aware PID autoscaler, producer circuit breaker, watermark Kalman tuner.
