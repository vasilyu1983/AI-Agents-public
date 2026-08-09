# Primitive 08 — Bufferbloat (Excessive Buffers, Latency Under Load)

**Source**: Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11). Nichols, K. & Jacobson, V. (2012). CoDel algorithm.

## Definition

**Bufferbloat** is the phenomenon where oversized buffers at network devices, queues, or application layers cause excessive latency under load without triggering the congestion signals that would reduce sending rates. Buffers were designed to prevent packet loss; when they are too large, they fill during congestion, adding seconds of latency while concealing the congestion from upstream senders.

### The Core Mechanism

```
Queue depth D (in time) = Buffer_size / Link_rate

If D >> RTT: congestion is absorbed silently.
TCP's congestion control triggers on loss or ECN.
With no loss (buffer not yet full), TCP keeps increasing rate.
Result: buffer stays perpetually full → latency ≈ D >> RTprop.
```

In application systems: if a thread pool queue, a Kafka consumer lag, or an HTTP server backlog is unbounded, the system absorbs spikes at the cost of latency — and the caller sees no 503 signal to back off.

### Latency Decomposition (Bufferbloat framing)

```
Total_latency = RTprop + Queueing_delay
             = min_path_latency + (buffer_occupancy / bottleneck_rate)
```

When buffer_occupancy is large (bufferbloat):
- Throughput stays near-maximal (buffer prevents loss).
- Latency soars.
- This is the opposite of acceptable: latency spikes, SLOs break, but the system appears "working."

## When to Use

- **Diagnosing high-latency-despite-good-throughput**: if p99 latency is 10–100× p50 under load, bufferbloat is a prime suspect.
- **Sizing application-level queues**: choose finite queue depths with backpressure signals rather than unbounded queues.
- **Evaluating AQM (Active Queue Management)**: CoDel, FQ-CoDel, PIE — apply to software queues in addition to network routers.
- **Kafka consumer lag analysis**: a growing consumer lag is application-layer bufferbloat.
- **HTTP/2 head-of-line blocking**: streams share one connection; a large slow stream blocks fast ones.

## Inputs

| Input | Description |
|-------|-------------|
| Buffer size | In packets, bytes, or requests |
| Link/service rate | Throughput at bottleneck |
| RTprop (minimum RTT) | Propagation delay without any queue |
| Observed p50 vs. p99 latency | Spread indicates bufferbloat |

## Outputs

- **Standing queue depth**: buffer_occupancy at steady state.
- **Latency penalty**: additional latency due to bufferbloat = standing_queue / rate.
- **Recommended buffer size**: BDP (Bandwidth-Delay Product) = RTprop × rate — the correct buffer for full utilization without standing queues.

## BDP Rule

```
Optimal_buffer ≈ RTprop × bottleneck_rate
```

Any buffer significantly larger than BDP creates standing queues and bufferbloat.

## Failure Modes

| Failure | Cause | Fix |
|---------|-------|-----|
| Unbounded application queues | Default: "never drop a request" | Set queue depth = BDP estimate or apply backpressure |
| Interpreting zero loss as "healthy" | Full buffer = no loss, but huge latency | Monitor latency percentiles; use AQM (CoDel) |
| Large Kafka consumer lag tolerated | Each message stays in lag buffer for minutes | Set max.poll.interval.ms and consumer concurrency; alert on lag growth rate, not just absolute lag |
| Default TCP buffers on high-BDP paths | 64KB buffer on 10 Gbps × 50ms path → BDP = 62 MB; buffer too small and TCP never fills pipe | Tune net.core.rmem_max / wmem_max to match BDP |
| Growing async job queue masked | "Jobs are being processed" — but latency is 10 minutes | Bound queue depth; add separate worker pools or backpressure |

## Worked Example

A batch processing pipeline:
- Job arrival rate: 500 jobs/s
- Processing rate: 600 jobs/s (ρ = 0.83)
- Queue depth limit: **unbounded** (default asyncio queue)

Kingman (primitive 07) predicts Wq = (0.83/0.17) × 1.0 × (1/600) = ~8 ms mean queue wait. Acceptable.

But the queue is unbounded. During a 10-second traffic spike at 700 jobs/s (ρ > 1), 700 jobs/s - 600 jobs/s = 100 extra jobs/s accumulate. After 10 seconds: **1000 jobs in queue**. When spike ends, the backlog takes **1000/100 excess capacity = 10 seconds** to drain. During drain, latency = 1000/(600−500) = 10 extra seconds per job.

**Fix**: bound the queue at BDP equivalent — for this system, a few hundred jobs. Reject or backpressure when full. Callers see 503/429 and back off, preventing unbounded accumulation.

## Composition

- **Little's Law** (primitive 01): L = λ × W; bufferbloat is diagnosed when L >> expected (signal: high W).
- **Kingman** (primitive 07): Kingman Wq reveals expected queue accumulation at high ρ; bufferbloat amplifies this when buffers are large.
- **M/M/1** (primitive 02): M/M/1 Lq = ρ²/(1−ρ); this is the correct queue depth at steady state — size buffers no larger than 2–3× this value.
- **USL** (primitive 09): scaling out without fixing bufferbloat can shift the standing queue to the new bottleneck.

## Sources

- Gettys, J. & Nichols, K. (2012). "Bufferbloat: Dark Buffers in the Internet." *ACM Queue*, 9(11).
- Nichols, K. & Jacobson, V. (2012). "Controlling Queue Delay." *ACM Queue*, 10(5). (CoDel algorithm.)
- Kleinrock, L. (1975). *Queueing Systems, Vol. 1: Theory*. Wiley-Interscience. (Queueing delay foundations.)
- Harchol-Balter, M. (2013). *Performance Modeling and Design of Computer Systems*. Cambridge University Press.
