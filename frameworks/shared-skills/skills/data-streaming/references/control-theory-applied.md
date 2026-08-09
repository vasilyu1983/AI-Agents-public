# Control Theory Applied to Data Streaming

> **Gate before invoking:** Check [`foundations-control-theory` § When to Apply](../../foundations-control-theory/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Feedback control and streaming systems share the same underlying problem: a producer generates work faster than a consumer can absorb it, delays accumulate between action and effect, and state drifts from its target under disturbance. This reference maps the 11 control-theory primitives from `foundations-control-theory` to concrete streaming failure modes in Kafka, Flink, Pulsar, and Kinesis pipelines.

## Table of Contents

- [Patterns](#patterns)
  - [P1 Backpressure as Feedback Control](#p1-backpressure-as-feedback-control)
  - [P2 Watermark Tuning to Compensate for Dead-Time](#p2-watermark-tuning-to-compensate-for-dead-time)
  - [P3 Flow Control via Token Bucket on Producers](#p3-flow-control-via-token-bucket-on-producers)
  - [P4 Adaptive Batch Sizing — MPC-Style Throughput/Latency Tradeoff](#p4-adaptive-batch-sizing--mpc-style-throughputlatency-tradeoff)
  - [P5 Lag-Based Consumer Scaling with PID and Anti-Windup](#p5-lag-based-consumer-scaling-with-pid-and-anti-windup)
- [Anti-Patterns](#anti-patterns)
  - [A1 Producer Rate Fixed Without Backpressure — Pipeline Collapse](#a1-producer-rate-fixed-without-backpressure--pipeline-collapse)
  - [A2 Watermark Too Aggressive — Silent Data Loss](#a2-watermark-too-aggressive--silent-data-loss)
  - [A3 Consumer Auto-Scale on Raw Lag Without Derivative — Overshoot](#a3-consumer-auto-scale-on-raw-lag-without-derivative--overshoot)
  - [A4 Ignoring Kafka Rebalance Dead-Time](#a4-ignoring-kafka-rebalance-dead-time)
  - [A5 Token Bucket Sized Without Measuring Slow-Consumer Recovery Time](#a5-token-bucket-sized-without-measuring-slow-consumer-recovery-time)
- [Recipes](#recipes)
  - [R1 Lag-Aware Consumer Autoscaler](#r1-lag-aware-consumer-autoscaler)
  - [R2 Producer Flow Control with Circuit Breaker](#r2-producer-flow-control-with-circuit-breaker)
  - [R3 Watermark Tuner with Kalman-Filtered Drift Estimator](#r3-watermark-tuner-with-kalman-filtered-drift-estimator)
- [Composition](#composition)
- [Sources](#sources)

---

## Patterns

### P1 Backpressure as Feedback Control

**Primitive**: [Circuit Breaker & Backpressure](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md)

**What it is.** Backpressure is closed-loop flow control: the consumer measures its own saturation and signals the producer to reduce send rate. Queue depth is the observed state. Desired queue depth (or zero growth) is the setpoint. The admission-throttle signal applied to the producer is the control output.

```
Producer → [Kafka / Pulsar / Kinesis] → Consumer
                     ↑                       |
                     └── backpressure signal ─┘
                         (queue depth > threshold)
```

**Streaming implementation.**

- **Flink**: native credit-based backpressure propagates automatically through the task graph. When a sink operator slows, credits stop flowing upstream; source operators pause reading from Kafka partitions. No configuration required — but monitor `backpressure.level` per operator in the Flink Web UI. A value above `HIGH` for more than a few minutes indicates the downstream stage is the bottleneck.
- **Kafka consumers**: pause partitions explicitly (`consumer.pause(partitions)`) when the processing queue exceeds a threshold. Resume when the queue drains below the low-water mark. This is a manual two-level bang-bang controller; for continuous control, use a PID on consumer fetch size instead.
- **Kinesis / Kafka Streams**: use `max.poll.records` and `fetch.max.bytes` as coarse-grained levers. Reducing these slows the effective producer-side ingestion rate from the consumer's perspective.
- **Pulsar**: negative acknowledgements and `receiverQueueSize` act as a combined backpressure and buffer mechanism. Shrinking `receiverQueueSize` slows delivery to the consumer application.

**Key control insight.** Without backpressure, the pipeline is open-loop: the producer runs at its maximum rate regardless of downstream state. Open-loop operation with a bounded buffer terminates in one of two failure modes — buffer overflow (data loss or memory exhaustion) or producer blocking (latency divergence). Backpressure closes the loop and bounds both.

**Tuning.**

| Parameter | Conservative (start here) | Aggressive |
|-----------|--------------------------|------------|
| Queue high-water mark | 70% of max | 90% of max |
| Queue low-water mark (resume) | 40% of max | 60% of max |
| Backpressure signal hysteresis band | 30 pp | 10 pp |

Hysteresis prevents the producer from toggling pause/resume rapidly (chattering), which itself causes overhead.

---

### P2 Watermark Tuning to Compensate for Dead-Time

**Primitive**: [Dead-Time Compensation](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md)

**What it is.** Event-time watermarks set the boundary after which late events are dropped (or routed to a side output). A watermark at `event_time = max_seen − L` means the processor waits `L` time units past the most recent observed event before closing a window. `L` is the dead-time budget: the operator's best estimate of how late events can arrive and still be valid.

Setting `L` too small closes windows before all events arrive — valid late events are silently dropped. Setting `L` too large holds window state open, consuming memory and increasing result latency. This is exactly the dead-time compensation tradeoff: underestimate the delay and the controller (windowed aggregation) reacts to an incomplete state; overestimate and system latency increases unnecessarily.

**Watermark as Smith Predictor analog.**

The Smith Predictor removes transport delay from the feedback path by predicting the delay-free output. A well-calibrated watermark does the same: it predicts "enough time has passed that all in-transit events have arrived" and triggers computation on a delay-free view of the data.

```
Watermark(t) = max_event_time_seen − L
where L = p99(event_arrival_delay) + safety_margin
```

**Measuring `L` in practice.**

1. Sample `processing_time − event_time` for a 24-hour window.
2. Compute the empirical CDF of arrival delay.
3. Set `L = p99 + σ` where `σ` is a safety margin (commonly 20–30% of p99 for normal skew; larger for mobile clients or cross-region pipelines).
4. Re-measure weekly — arrival delay distributions shift with product changes, new SDK versions, and traffic pattern changes.

**Platform specifics.**

- **Flink**: `WatermarkStrategy.forBoundedOutOfOrderness(Duration.ofSeconds(L))`. Use `AssignerWithPeriodicWatermarks` for continuous emission or `AssignerWithPunctuatedWatermarks` for event-driven emission. The periodic emitter fires every `auto.watermark.interval` (default 200ms) — reduce this for low-latency pipelines.
- **Kafka Streams**: `grace` period on windowed operations (`TimeWindows.ofSizeWithNoGrace(size).grace(Duration.ofSeconds(L))`). Events arriving after the grace period are dropped.
- **Spark Structured Streaming**: `withWatermark("event_time", "L seconds")`. Note that Spark's watermark is single-valued across a microbatch — it does not update within a batch.

**Failure signal.** If `late_events_dropped_rate > 0.5%` of total events, `L` is too small. If window state memory grows continuously, `L` may be too large or a source is stalled and emitting no events (which blocks watermark advancement).

---

### P3 Flow Control via Token Bucket on Producers

**Primitive**: [Rate Limiting / Token Bucket](../../foundations-control-theory/assets/templates/control-theory/11-rate-limiting-token-bucket.md)

**What it is.** A token bucket on the producer side enforces a maximum sustained write rate while permitting short bursts. This protects the downstream broker and consumer from overload without forcing the producer to drop events — it queues locally instead of overwhelming shared infrastructure.

**When to apply at the producer.** Backpressure (P1) is reactive — it responds after the queue is already filling. A token bucket is feedforward admission control: the producer never puts more work into the broker than the known downstream capacity. Use the token bucket when:

- The producer is a microservice that writes events synchronously and can tolerate millisecond-scale queuing.
- The consumer has a known steady-state throughput limit that the broker cannot enforce on its own.
- The pipeline has experienced broker-side `RecordTooLargeException` or throttling errors caused by bursty writes.

**Configuration.**

```
fill_rate r  = measured consumer throughput × 0.85  (leave 15% headroom)
burst_cap b  = r × max_burst_seconds               (typical: 5–30 seconds)
request_cost = 1 per event, or bytes / avg_event_bytes for byte-weighted control
```

The 0.85 headroom factor prevents the fill rate from sitting right at the consumer's processing limit, where any variance causes queue growth.

**Platform specifics.**

- **Kafka producer**: `max.block.ms` and `buffer.memory` implement a coarse token bucket — when the internal send buffer fills, `send()` blocks until space is available. For explicit rate control, implement a `RateLimiter` (e.g., Guava) in the producer application ahead of the Kafka client.
- **Kinesis**: `PutRecords` has hard limits (1 MB/s per shard, 1000 records/s per shard). A token bucket at the producer is the standard mechanism to stay under limits without dropping events. Use AWS SDK retry configuration alongside the bucket.
- **Pulsar**: producer `maxPendingMessages` and `blockIfQueueFull=true` act as a token bucket equivalent. For explicit rate control, use the `RateLimiter` in the Pulsar client SDK.

**Leaky bucket vs. token bucket.** If the downstream consumer requires strictly smooth input (e.g., a sink that fails under any burst), use a leaky bucket instead — it enforces constant output rate regardless of arrival pattern. Most Kafka/Flink sinks tolerate moderate bursting; token bucket is sufficient and more efficient.

---

### P4 Adaptive Batch Sizing — MPC-Style Throughput/Latency Tradeoff

**Primitive**: [Model Predictive Control (MPC)](../../foundations-control-theory/assets/templates/control-theory/05-mpc.md)

**What it is.** Batch size in stream processors (Flink checkpoint intervals, Kafka consumer `max.poll.records`, Spark microbatch trigger intervals) governs a throughput/latency tradeoff. Large batches amortize per-batch overhead and increase throughput; small batches reduce end-to-end latency. MPC frames this as: given a model of system behavior, solve for the batch size sequence over a short horizon that minimizes a cost function combining throughput shortfall and latency violation.

**Simplified receding-horizon formulation.**

At each control cycle (e.g., every 60 seconds):

```
State x(k)       = [current_lag, current_throughput, current_p99_latency]
Control u(k)     = batch_size (records per poll / per checkpoint)
Constraints:     u_min ≤ u ≤ u_max
                 p99_latency(u) ≤ SLO_latency
                 lag(k+N) ≤ max_acceptable_lag

Minimize over horizon N=3:
  Σ [ w_lag × lag(k+i)² + w_lat × max(0, latency(k+i) − SLO)² ]

Apply u*(k). Re-measure. Re-solve at k+1.
```

**In practice, MPC for batch sizing simplifies to a lookup with feedback correction.**

Full quadratic MPC solvers are rarely deployed in streaming control loops — the operational overhead is high. The practical version is:

1. Offline: characterize the `(batch_size → throughput, latency)` curve for your workload at 3–5 operating points.
2. Online: measure current lag and latency. Select the batch-size operating point that maximizes throughput while keeping latency within SLO.
3. Feedback correction: if the model prediction is consistently wrong (lag grows despite "optimal" batch size), increase the model's uncertainty parameter and fall back to a smaller batch size until a re-characterization run is scheduled.

**Flink checkpoint interval tuning.** The checkpoint interval is a batch-size analog: shorter intervals reduce state recovery time but increase checkpoint overhead and latency spikes. A starting point: set interval = 5× average checkpoint duration. If lag grows during checkpointing, the interval is too short; if recovery time SLO is violated, it is too long. Adjust using the feedback measurement at each checkpoint.

**Kafka `max.poll.records` adaptive control.**

```python
# Pseudocode: simple proportional controller on poll record count
target_poll_ms = 500  # ms
measured_poll_ms = consumer.metrics()["poll-time-avg"]
error = target_poll_ms - measured_poll_ms
new_max_poll_records = current_max_poll_records + Kp * error
new_max_poll_records = clamp(new_max_poll_records, 50, 5000)
```

This is a P-controller; add derivative to damp oscillation in variable-latency workloads.

---

### P5 Lag-Based Consumer Scaling with PID and Anti-Windup

**Primitive**: [PID Control](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md) + [Anti-Windup](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md)

**What it is.** Consumer group lag (offset distance between producer head and consumer committed offset) is the natural observed state for a consumer autoscaler. Target lag is the setpoint (often 0 or a small steady-state buffer). The number of consumer instances (or Flink task slots) is the actuator.

```
e(k) = target_lag − measured_lag
u(k) = Kp·e(k) + Ki·T·Σe(j) + (Kd/T)·(e(k) − e(k−1))
new_consumer_count = current_count − round(u(k))  // negative e means over-lagged → add consumers
new_consumer_count = clamp(new_consumer_count, min_instances, max_instances)
```

**Anti-windup is required.** Consumer count has hard limits: `min_instances` (usually 1) and `max_instances` (partition count for Kafka; resource budget). When the controller hits the ceiling during a backfill event, the integral term accumulates without bound. When the backfill completes and lag collapses, the wound-up integral causes an over-scale-down that starves the pipeline. Use clamping anti-windup: freeze the integral when the actuator is at its limit.

```python
# Clamping anti-windup
if new_consumer_count == max_instances or new_consumer_count == min_instances:
    # do not update integral this cycle
    pass
else:
    integral += e * T
```

**Derivative term.** The derivative `Kd·(e(k) − e(k−1))/T` measures the rate of lag growth. A rapidly growing lag (derivative large and negative) should trigger faster scale-up than a slowly growing lag of the same magnitude. Without Kd, the scaler reacts only to the lag level — it will be slow to respond to sudden producer spikes. With Kd too large, a noisy lag metric (see A3) causes derivative kick.

**Recommended tuning sequence.**

1. Set `Ki = Kd = 0`. Tune `Kp` until the scaler adds/removes consumers proportionally without oscillation.
2. Add `Ki` to eliminate steady-state lag offset. Start at `Ki = 0.2 × Kp / T_i` where `T_i` is the time for lag to stabilize after a step change.
3. Add `Kd` last. Filter the lag measurement with a 3-period moving average before computing the derivative to suppress noise.

**Gain scheduling across regimes.** Use separate PID gains for steady-state vs. backfill (see Recipe R1). A pipeline catching up from 10-million-record lag requires more aggressive scale-up than one maintaining 5k-record steady-state lag. See [Gain Scheduling](../../foundations-control-theory/assets/templates/control-theory/09-gain-scheduling.md).

---

## Anti-Patterns

### A1 Producer Rate Fixed Without Backpressure — Pipeline Collapse

**Diagnosis.** The producer writes at its maximum rate regardless of downstream consumer throughput. The broker queue grows monotonically. When the queue reaches its retention limit, old messages are dropped (Kafka log compaction / retention eviction) or new writes are rejected. The pipeline experiences either silent data loss or producer blocking cascading into upstream service degradation.

**Control theory framing.** The system is open-loop. No feedback path exists from consumer state to producer rate. Any mismatch between production rate and consumption rate accumulates as unbounded queue growth — equivalent to an integrator with no feedback stabilization.

**Fix.** Implement backpressure (P1) or a producer-side token bucket (P3). At minimum, instrument consumer lag and alert before retention boundaries are reached. See [Circuit Breaker & Backpressure](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md).

---

### A2 Watermark Too Aggressive — Silent Data Loss

**Diagnosis.** The watermark lateness bound `L` is set to a value smaller than the true p99 arrival delay for the event source. Windows close and emit results before all events have arrived. Late events are silently dropped (or accumulate in a side output that nobody monitors).

**Streaming context.** This commonly occurs when `L` is calibrated against a local development environment or a low-traffic period, then deployed against production traffic with mobile clients, cross-region sources, or variable-latency IoT devices. The dead-time `L` is not a fixed property of the system — it is a distribution that shifts with traffic composition.

**Failure signal.** Monitor `numLateRecordsDropped` in Flink metrics or equivalent in Kafka Streams. Any non-zero rate warrants investigation. A rising trend indicates watermark drift relative to actual event delay.

**Fix.** Measure `L` from the empirical arrival delay distribution (see P2). Re-tune weekly. Use Flink's side output for late data rather than silent drop — route to a repair topic and monitor volume. See [Dead-Time Compensation](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md).

---

### A3 Consumer Auto-Scale on Raw Lag Without Derivative — Overshoot

**Diagnosis.** The autoscaler reads consumer lag as a raw metric and scales consumer count proportionally (P-only controller). When a traffic spike arrives, lag grows → scaler adds consumers → consumers process the backlog faster than the model predicted → lag drops to zero → scaler removes consumers → lag grows again. The system oscillates with a period of minutes.

**Control theory framing.** Proportional-only control without derivative damping produces underdamped response. The lag measurement has no rate-of-change signal, so the controller cannot distinguish "lag is 100k and stable" from "lag is 100k and growing at 50k/min." Both receive the same scale-up signal; the growing case should receive a larger response.

**Compounding factor.** Consumer group rebalancing introduces dead-time `L_rebalance` between the scale-up decision and the new consumers actually processing messages. The P-only controller does not account for this delay and over-adds consumers before the effect of the previous scale-up is visible.

**Fix.** Add derivative term (P5). Add dead-time compensation for rebalance latency (A4 and R1). Smooth the lag measurement with a 3-period moving average before differencing to avoid derivative kick from metric noise.

---

### A4 Ignoring Kafka Rebalance Dead-Time

**Diagnosis.** When consumer instances are added or removed, Kafka triggers a consumer group rebalance. During rebalance, all consumers in the group stop processing for the rebalance duration (`max.poll.interval.ms` worst case, typically 5–60 seconds for incremental cooperative rebalancing). An autoscaler that does not account for this dead-time interprets the consumption pause as additional lag growth and scales up further — triggering another rebalance, further pause, and additional spurious scale-up.

**Control theory framing.** Rebalance is transport dead-time `L_rebalance`. A feedback controller that ignores dead-time sees no effect from its control action during `L_rebalance`, accumulates error, applies more control, then experiences the combined effect of all control actions simultaneously when rebalance completes. This is the classic overshoot signature of dead-time-uncompensated control.

**Measured values.** Rebalance duration depends on group size and rebalance protocol:
- **Eager rebalance** (default before Kafka 2.4): full stop-the-world, 10–120 seconds for large groups.
- **Incremental cooperative rebalance** (Kafka 2.4+, `partition.assignment.strategy=CooperativeStickyAssignor`): partial rebalance, typically 5–20 seconds.

**Fix.** Freeze the autoscaler's integral term during detected rebalance events. Detect rebalance via consumer group state API (`kafka-consumer-groups.sh --describe` shows `STATE: PreparingRebalance`). Add a dead-time compensator: suppress scale-up decisions for `L_rebalance` seconds after a previous scale-up action. See [Dead-Time Compensation](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md).

---

### A5 Token Bucket Sized Without Measuring Slow-Consumer Recovery Time

**Diagnosis.** A token bucket is deployed on the producer to prevent downstream overload. The fill rate `r` and burst capacity `b` are set based on steady-state consumer throughput measurements. After a consumer slowdown or restart, the bucket fills to capacity and the producer resumes at full burst rate before the consumer has fully recovered processing capacity. The burst re-saturates the consumer immediately.

**The recovery-time gap.** After a consumer slowdown event (GC pause, checkpoint, rebalance), the consumer requires `T_recovery` to drain its internal buffers and reach steady-state throughput again. If `b / r > T_recovery`, the burst released by the full bucket exceeds what the recovering consumer can absorb.

**Fix.** Measure `T_recovery` empirically under load. Set `b = r × min(T_recovery × 0.5, max_burst_seconds)`. Additionally: pair the token bucket with a circuit breaker (see R2) — when consumer saturation is detected, open the circuit breaker and pause token fill. Resume filling only after the consumer reports healthy processing metrics. See [Rate Limiting / Token Bucket](../../foundations-control-theory/assets/templates/control-theory/11-rate-limiting-token-bucket.md) and [Circuit Breaker & Backpressure](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md).

---

## Recipes

### R1 Lag-Aware Consumer Autoscaler

**Goal.** Scale Kafka consumer instances (or Flink task slots) to maintain a target lag of ≤ `target_lag` records per partition under both steady-state and backfill conditions, without oscillating or collapsing during rebalances.

**Primitives used.**
- PID Control → [01-pid-control.md](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md)
- Anti-Windup → [08-anti-windup.md](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md)
- Dead-Time Compensation → [07-dead-time-compensation.md](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md)
- Gain Scheduling → [09-gain-scheduling.md](../../foundations-control-theory/assets/templates/control-theory/09-gain-scheduling.md)

**Architecture.**

```
1. Observe:  per-partition lag from Kafka AdminClient or MSK metrics
2. Aggregate: sum(lag) across partitions assigned to consumer group
3. Smooth:   3-period moving average (suppresses metric jitter before derivative)
4. Control:  PID with anti-windup (see below)
5. Compensate: dead-time freeze during rebalance window
6. Schedule: switch PID gains between backfill and steady-state regimes
7. Actuate:  update consumer group target instance count or Flink parallelism
```

**PID with anti-windup.**

```python
TARGET_LAG     = 5_000        # records; SLO
T              = 60           # control interval (seconds)
MIN_INSTANCES  = 2
MAX_INSTANCES  = partition_count  # Kafka: consumers > partitions are idle

Kp, Ki, Kd = 0.002, 0.0005, 0.001   # steady-state gains (tune per workload)

integral = 0.0
prev_error = 0.0

def control_step(measured_lag, current_instances, rebalancing: bool):
    global integral, prev_error

    error = TARGET_LAG - measured_lag  # negative = over-lagged, need more consumers
    derivative = (error - prev_error) / T
    prev_error = error

    u = Kp * error + Ki * integral + Kd * derivative
    new_count = clamp(current_instances - round(u), MIN_INSTANCES, MAX_INSTANCES)

    # Anti-windup: freeze integral if actuator is at limit OR rebalance in progress
    at_limit = (new_count == MIN_INSTANCES or new_count == MAX_INSTANCES)
    if not at_limit and not rebalancing:
        integral += error * T

    return new_count
```

**Dead-time compensation for rebalance.**

```python
REBALANCE_DEAD_TIME = 30  # seconds; measure from `CooperativeStickyAssignor` logs
last_scale_action_time = None

def should_suppress_scale(now):
    if last_scale_action_time is None:
        return False
    return (now - last_scale_action_time) < REBALANCE_DEAD_TIME

# Before calling control_step: if rebalance detected OR dead-time window active,
# pass rebalancing=True to freeze integral and hold current count.
```

**Gain scheduling: backfill vs. steady-state.**

| Regime | Condition | Kp | Ki | Kd |
|--------|-----------|----|----|-----|
| Steady-state | lag < 5× target | 0.002 | 0.0005 | 0.001 |
| Backfill | lag ≥ 5× target | 0.005 | 0.0002 | 0.002 |

Backfill regime uses higher Kp (faster scale-up), lower Ki (avoid windup during the long catch-up), and higher Kd (dampen overshoot as lag collapses). Switch gains smoothly at the boundary: interpolate linearly over 2 control cycles to avoid a bump.

**Verification checks.**

- `lag_time_to_target < 10 min` after a 10× traffic spike.
- `consumer_count_oscillation_frequency < 1 change per 5 min` at steady state.
- `rebalance_count per hour` does not exceed baseline + 20% after autoscaler is enabled.

---

### R2 Producer Flow Control with Circuit Breaker

**Goal.** Prevent a Kafka or Kinesis producer from collapsing a downstream pipeline when the consumer saturates or becomes temporarily unavailable, without dropping events.

**Primitives used.**
- Rate Limiting / Token Bucket → [11-rate-limiting-token-bucket.md](../../foundations-control-theory/assets/templates/control-theory/11-rate-limiting-token-bucket.md)
- Circuit Breaker & Backpressure → [10-circuit-breaker-backpressure.md](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md)
- Feedback vs. Feedforward → [02-feedback-vs-feedforward.md](../../foundations-control-theory/assets/templates/control-theory/02-feedback-vs-feedforward.md)

**Architecture.**

```
Application → [Token Bucket] → Kafka Producer → Broker → Consumer
                    ↑
             [Circuit Breaker]
                    ↑
             Saturation signal
             (consumer lag > threshold OR
              producer error rate > threshold)
```

**Token bucket configuration.**

```python
# Measure these from your consumer before setting:
CONSUMER_STEADY_THROUGHPUT = 50_000   # events/sec (p50 measured over 1 hour)
T_RECOVERY_SECONDS         = 45       # measured: time from consumer restart to steady throughput

FILL_RATE     = CONSUMER_STEADY_THROUGHPUT * 0.85   # 15% headroom
BURST_CAP     = FILL_RATE * min(T_RECOVERY_SECONDS * 0.5, 10)  # cap burst at 10 sec

class TokenBucket:
    def __init__(self):
        self.tokens = BURST_CAP  # start full
        self.last_refill = time.monotonic()

    def acquire(self, cost=1) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(BURST_CAP, self.tokens + FILL_RATE * elapsed)
        self.last_refill = now

        if self.tokens >= cost:
            self.tokens -= cost
            return True  # admitted
        return False  # backpressure: caller must queue or wait
```

**Circuit breaker — downstream saturation signal.**

Derive the saturation signal from one of:
- Consumer lag growth rate > 0 for `T_window` seconds (lag is not draining).
- Producer-side write error rate (`RecordTooLargeException`, `TimeoutException`) > 5% in a 30-second window.
- Explicit health endpoint from the consumer service.

```python
CIRCUIT_STATES = ("CLOSED", "OPEN", "HALF_OPEN")
FAILURE_THRESHOLD = 0.05   # 5% producer errors in window
OPEN_TIMEOUT      = 30     # seconds before half-open probe

class CircuitBreaker:
    state = "CLOSED"
    last_open_time = None

    def record_failure(self, rate):
        if self.state == "CLOSED" and rate > FAILURE_THRESHOLD:
            self.state = "OPEN"
            self.last_open_time = time.monotonic()
            token_bucket.pause_fill()   # do not refill during outage

    def allow_request(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if time.monotonic() - self.last_open_time > OPEN_TIMEOUT:
                self.state = "HALF_OPEN"
                return True  # single probe
            return False
        if self.state == "HALF_OPEN":
            return False  # wait for probe result

    def record_success(self):
        if self.state == "HALF_OPEN":
            self.state = "CLOSED"
            token_bucket.resume_fill()
```

**Feedforward element.** If you have a known traffic spike schedule (batch jobs, cron-triggered events, business-hours peaks), pre-reduce the token bucket fill rate 60 seconds before the expected spike — do not wait for the consumer lag signal to arrive. This is feedforward on the known disturbance.

**Failure modes to avoid.**
- Do not pause token fill on every OPEN transition without a minimum healthy period — burst recovery will re-open the circuit immediately (A5).
- Do not set `BURST_CAP` based on broker limits alone; the bottleneck is the consumer, not the broker.

---

### R3 Watermark Tuner with Kalman-Filtered Drift Estimator

**Goal.** Maintain a watermark lateness bound `L` that tracks the true p99 event arrival delay as it drifts over time, using a Kalman filter to produce a stable estimate that drives weekly re-tuning and alarm suppression.

**Primitives used.**
- Kalman Filter → [06-kalman-filter.md](../../foundations-control-theory/assets/templates/control-theory/06-kalman-filter.md)
- Dead-Time Compensation → [07-dead-time-compensation.md](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md)

**Step 1: Measure event arrival delay distribution.**

For each event consumed from Kafka/Pulsar/Kinesis, record:

```
arrival_delay(event) = processing_time − event_time
```

Aggregate into a sliding histogram over a 1-hour window. Extract `p99_delay` and `p999_delay` per source partition. Partition-level granularity matters: a single slow partition from a mobile SDK region can skew the group aggregate significantly.

**Step 2: Kalman filter on p99 drift.**

The true p99 delay is a slowly-drifting hidden state. Each hourly measurement of p99 is a noisy observation of it.

```python
# State: true_p99_delay (seconds)
# Model: random walk (true delay changes slowly)
# Sensor: hourly empirical p99 measurement (noisy)

A = 1.0        # state transition: p99 stays similar hour to hour
Q = 0.25       # process noise: p99 drifts ~0.5 sec/hr 1-sigma
R = 4.0        # measurement noise: empirical p99 has ~2 sec std dev

x_hat = 30.0   # initial estimate (seconds)
P     = 10.0   # initial uncertainty

def kalman_update(y_measured):
    global x_hat, P
    # Predict
    x_prior = A * x_hat
    P_prior = A * P * A + Q
    # Update
    K = P_prior / (P_prior + R)
    x_hat = x_prior + K * (y_measured - x_prior)
    P = (1 - K) * P_prior
    return x_hat
```

**Step 3: Set watermark and re-tune weekly.**

```python
SAFETY_MARGIN = 1.20   # 20% margin above Kalman-estimated p99

def compute_watermark_L(kalman_p99_estimate):
    return kalman_p99_estimate * SAFETY_MARGIN

# Re-tune weekly: run kalman_update() on each hourly measurement.
# If |new_L - current_L| > 5 seconds, trigger a Flink configuration update
# via the Flink REST API (job parameter update or rolling savepoint restart).
```

**Step 4: Alert on accelerating drift.**

Use the Kalman innovation `y_measured − x_prior` as an anomaly signal. A sustained positive innovation (measurements consistently exceeding the model's prediction) means the true delay is rising faster than the random-walk model assumes. Increase `Q` to track faster, and page the on-call engineer:

```python
DRIFT_ALERT_THRESHOLD = 10.0  # seconds; innovation exceeds model by this much

innovation = y_measured - x_prior
if abs(innovation) > DRIFT_ALERT_THRESHOLD:
    alert("Watermark drift anomaly: event delay increasing faster than baseline model")
```

**Platform update path.**

- **Flink**: update `WatermarkStrategy` requires a savepoint and job restart. Automate via Flink REST API. Schedule weekly during a low-traffic window.
- **Kafka Streams**: `grace()` period is set at topology build time; requires application restart. Use a config-driven restart with a feature flag to avoid code deploys.
- **Spark Structured Streaming**: `withWatermark()` is a query parameter; updating it requires a stream restart from a checkpoint. Coordinate with the checkpoint compaction schedule.

---

## Composition

The three recipes compose into a full pipeline control stack. Deploy in this order — each layer depends on the previous being stable:

| Layer | Recipe / Pattern | Stabilizes |
|-------|-----------------|------------|
| 1. Admission | R2 token bucket on producer | Broker and consumer not overloaded |
| 2. Lag control | R1 PID autoscaler | Consumer count tracks throughput |
| 3. Time semantics | R3 watermark tuner | Window results are accurate |

**Interaction to manage.** The lag autoscaler (R1) and the circuit breaker (R2) can conflict: R2 slows the producer (reduces input), which reduces lag (causes R1 to scale down), which reduces consumer capacity just as the circuit re-closes and the producer resumes. Coordinate by: hold R1 in freeze mode for `REBALANCE_DEAD_TIME` after R2 transitions from OPEN to CLOSED.

**Observability minimum.** The control stack is not operable without these metrics:

| Metric | Platform | Used By |
|--------|----------|---------|
| `consumer_lag_sum` per group | Kafka / MSK / Confluent | R1 PID input |
| `late_records_dropped` | Flink metrics | R3 alert |
| `producer_error_rate` | Kafka producer metrics | R2 circuit breaker |
| `rebalance_count` per hour | Kafka consumer group API | R1 dead-time freeze |
| `event_arrival_delay_p99` | Custom instrumentation | R3 Kalman input |

---

## Sources

- Åström & Murray, *Feedback Systems* (2020). [https://fbsbook.org](https://fbsbook.org) — foundational PID, dead-time, gain scheduling.
- Hellerstein et al., *Feedback Control of Computing Systems* (2004), Ch. 2, 7, 8 — computing-domain control applications.
- Nygard, M., *Release It!* 2nd ed. (2018), Ch. 5 — circuit breaker pattern.
- Apache Kafka documentation — consumer group rebalance protocols, producer configuration.
- Apache Flink documentation — watermark strategies, backpressure monitoring, checkpoint tuning.
- Apache Pulsar documentation — flow control, receiver queue, backpressure.
- Kalman, R.E. (1960), "A New Approach to Linear Filtering and Prediction Problems," ASME J. Basic Engineering 82:35-45.
- Turner (1986), "New directions in communications," IEEE Communications Magazine 24(10):2-9 — token bucket algorithm.

**Primitive cross-references** (full definitions):

- [01-pid-control.md](../../foundations-control-theory/assets/templates/control-theory/01-pid-control.md)
- [02-feedback-vs-feedforward.md](../../foundations-control-theory/assets/templates/control-theory/02-feedback-vs-feedforward.md)
- [05-mpc.md](../../foundations-control-theory/assets/templates/control-theory/05-mpc.md)
- [06-kalman-filter.md](../../foundations-control-theory/assets/templates/control-theory/06-kalman-filter.md)
- [07-dead-time-compensation.md](../../foundations-control-theory/assets/templates/control-theory/07-dead-time-compensation.md)
- [08-anti-windup.md](../../foundations-control-theory/assets/templates/control-theory/08-anti-windup.md)
- [09-gain-scheduling.md](../../foundations-control-theory/assets/templates/control-theory/09-gain-scheduling.md)
- [10-circuit-breaker-backpressure.md](../../foundations-control-theory/assets/templates/control-theory/10-circuit-breaker-backpressure.md)
- [11-rate-limiting-token-bucket.md](../../foundations-control-theory/assets/templates/control-theory/11-rate-limiting-token-bucket.md)
