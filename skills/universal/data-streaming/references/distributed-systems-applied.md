# Distributed Systems Applied to Data Streaming

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. This file is a link adapter: theory lives in the foundation; this file keeps only the streaming-specific decisions, platform settings, and failure scenarios.

Kafka, Flink, Debezium, and Pulsar failures are distributed-systems failures with platform names: split-brain leaders, stale offsets, duplicate sink writes, unsafe rebalances. Each section below names the primitive, links the foundation file that owns the theory, and keeps only what is specific to streaming.

## Table of Contents

- [Primitive Map](#primitive-map)
- [Patterns](#patterns)
  - [P1 Kafka ISR vs. Quorum Semantics — Choosing Write Durability](#p1-kafka-isr-vs-quorum-semantics--choosing-write-durability)
  - [P2 Exactly-Once via Idempotent Producer and Transactional Consumer](#p2-exactly-once-via-idempotent-producer-and-transactional-consumer)
  - [P3 Leader-Epoch Fencing During Partition Rebalance](#p3-leader-epoch-fencing-during-partition-rebalance)
  - [P4 CDC Ordering Using Vector Clocks](#p4-cdc-ordering-using-vector-clocks)
  - [P5 Broadcast Semantics in Pub/Sub Fan-Out](#p5-broadcast-semantics-in-pubsub-fan-out)
  - [P6 Consumer-Group Rebalance Correctness](#p6-consumer-group-rebalance-correctness)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
  - [R1 End-to-End Exactly-Once Effects with a Downstream Sink](#r1-end-to-end-exactly-once-effects-with-a-downstream-sink)
  - [R2 Retry Budget Design Tied to Idempotency Keys](#r2-retry-budget-design-tied-to-idempotency-keys)
  - [R3 CDC Pipeline with Causal Ordering Across Shards](#r3-cdc-pipeline-with-causal-ordering-across-shards)
- [Cross-References](#cross-references)
- [Sources](#sources)

---

## Primitive Map

Foundation root: `../../foundations-distributed-systems/`. Theory is not restated here.

| Streaming decision | Primitive | Owning file |
|---|---|---|
| `acks`, `min.insync.replicas`, BookKeeper quorums | Quorums, PACELC | [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [01-cap-pacelc.md](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md) |
| Idempotent producer, EOS, sink dedupe | Idempotency | [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md) |
| Leader epoch, `generation_id`, zombie producers | Leases and fencing | [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md) |
| KRaft controller quorum | Raft | [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md) |
| LSN / GTID / HLC ordering in CDC | Logical clocks, causal consistency | [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md), [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md) |
| Consumer groups, subscriptions, changelogs | Broadcast | [11-broadcast-protocols.md](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md) |
| Why consensus needs timeouts (FLP) | FLP | [02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md) |
| Exactly-once receiver, split-brain prevention | Composition | [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md) |
| Gray failure, deadlines, hybrid logical clocks | Production failures | [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md) |
| Retry storms, consumer-lag overload, load shedding | Overload (owned by qa-resilience) | [cascading-failure-prevention.md](../../qa-resilience/references/cascading-failure-prevention.md) |

---

## Patterns

### P1 Kafka ISR vs. Quorum Semantics — Choosing Write Durability

**Primitive**: quorums and PACELC → [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [01-cap-pacelc.md](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md)

Kafka's In-Sync Replica (ISR) set is an adaptive quorum. The leader tracks which replicas are caught up within `replica.lag.time.max.ms`. With `acks=all`, a write is acknowledged once every current ISR member has replicated it. Replicas acknowledge from the page cache, so durability comes from replication, not fsync. The ISR can shrink to the leader alone; `min.insync.replicas` sets the floor below which `acks=all` writes are rejected.

This is a PACELC choice. The recommended durable setting (`acks=all`, which is the producer default since Kafka 3.0, plus `min.insync.replicas=2`, which you must set because the broker default is 1) is EC — it adds replication latency under normal operation to preserve consistency. Setting `acks=1` is EL — it returns immediately from the leader, accepting possible data loss if the leader crashes before replication completes.

| Kafka setting | NWR analogue | Guarantee |
|---|---|---|
| `acks=0` | W=0 | Fire-and-forget; no durability |
| `acks=1` | W=1 | Leader-only; loss on leader failure before replication |
| `acks=all` + `min.insync.replicas=2`, RF=3 | W = current ISR size, never below 2 | Survives 1 replica loss without losing acknowledged writes |
| `acks=all` + `min.insync.replicas=RF` | W=N | Any replica failure blocks writes |

**Decision rule.** Financial, audit, and CDC source topics: `acks=all`, `min.insync.replicas=2`, `replication.factor=3`, `unclean.leader.election.enable=false` (the default). High-throughput telemetry that tolerates loss: `acks=1`, `replication.factor=2`.

**KRaft (Kafka 4.0+ is KRaft-only).** Controllers form a Raft quorum for metadata. It is sized separately from `replication.factor`. A majority quorum of N tolerates ⌊(N−1)/2⌋ failures: 3 controllers tolerate 1, 5 tolerate 2. With 3 controllers and RF=3 / `min.insync.replicas=2`, the controllers tolerate 1 failure and each partition tolerates 1 replica loss while it stays writable.

**Tail latency.** An `acks=all` write waits for the slowest ISR member. Watch replica fetcher lag per broker: a lagging follower slows every write on its partitions until it catches up or leaves the ISR. For slow-but-alive brokers, see gray failure in [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md).

---

### P2 Exactly-Once via Idempotent Producer and Transactional Consumer

**Primitive**: idempotency → [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md); receiver composition → [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md)

**Framing.** The network gives you at-least-once delivery. Kafka EOS builds exactly-once *effects* inside a transactional boundary by combining idempotence with atomic commit. FLP concerns deterministic consensus termination; it does not by itself rule out exactly-once effects. Two layers:

1. **Idempotent producer** (`enable.idempotence=true`; the Java client default since 3.0, while librdkafka-based clients default to `false`): the broker dedupes the producer's *internal* retries by `(producer_id, partition, sequence_number)`. If the application calls `send()` again after a failure, the record gets a new sequence number and is written twice. Let the producer retry within `delivery.timeout.ms` instead of re-sending in application code.
2. **Transactions + `isolation.level=read_committed`**: writes to several partitions and topics, plus the consumer offset commit (`sendOffsetsToTransaction`), commit or abort atomically. Read-committed consumers skip aborted and still-open transactional records.

**Scope of the guarantee.** Exactly-once holds only for Kafka→Kafka read-process-write, or for a Flink job whose checkpoint is aligned with a two-phase-commit sink. It does **not** cover:

- Downstream databases, APIs, or object stores that sit outside the transaction. Use an idempotent sink key (R1).
- Side effects inside the processing loop, such as HTTP calls or emails. Each needs its own idempotency key (R2).
- Non-transactional consumers that crash between processing and committing their offsets. They reprocess.

**Platform specifics.**

- Flink with Kafka source + Kafka sink: Flink's two-phase commit (`KafkaSink` on the Sink V2 API with `DeliveryGuarantee.EXACTLY_ONCE` and a `transactionalIdPrefix`) aligns Flink checkpoints with Kafka transactions. The legacy `SinkFunction`/`TwoPhaseCommitSinkFunction` API was removed in Flink 2.0; use Sink V2 (`Sink` + `SupportsCommitter`). On checkpoint completion, the Kafka transaction is committed; on recovery, uncommitted transactions are aborted. End-to-end exactly-once within the Flink → Kafka boundary. Downstream consumers see output only at checkpoint cadence, so `transaction.timeout.ms` must exceed the maximum checkpoint duration plus the restart time.
- Kafka Streams: `processing.guarantee=exactly_once_v2` (EOS-V2, available since Kafka 3.0) uses one transaction per thread rather than one per task. Fewer transactions = lower overhead. It is opt-in: the default `processing.guarantee` is `at_least_once`.

---

### P3 Leader-Epoch Fencing During Partition Rebalance

**Primitive**: fencing tokens → [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md); split-brain prevention → [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md)

The **leader epoch** is a counter that increases at every partition leader election, so it works like a Raft term or a fencing token. Kafka's streaming-specific fencing tokens:

| Token | Fences | Where a stale holder is rejected |
|---|---|---|
| Partition leader epoch | Deposed partition leader | Follower fetches and the controller metadata update |
| Producer epoch (per `transactional.id`) | Zombie transactional producer after restart | Broker rejects the old epoch (`ProducerFencedException`) |
| Consumer group `generation_id` / member epoch | Consumer that lost its partitions in a rebalance | Group coordinator rejects offset commits |

**Failover flow.**

```
Epoch 5: Broker A is partition leader. Produces and replicates normally.

Broker A experiences a GC pause (60 seconds).
Controller detects heartbeat timeout → elects Broker B as leader → epoch = 6.

Broker A resumes from GC pause. Believes it is still leader (epoch 5).
Followers now fetch from Broker B (Kafka followers pull; leaders do not push).
Broker A cannot grow its ISR; its stale-epoch requests are rejected, and the
metadata update from the controller tells it that it is deposed.

Broker B (epoch 6) continues as leader. Broker A becomes follower.
```

The epoch never expires on a clock; it only increases at election. Detection still depends on timeouts. An `acks=all` write sent to A during its pause cannot complete, because the followers no longer replicate from A.

**Flink.** The Kafka source stores the offset and leader epoch in checkpoint state. On restore after a leadership change, the client uses the epoch to detect log truncation and does not resume from a divergent offset.

---

### P4 CDC Ordering Using Vector Clocks

**Primitive**: logical clocks → [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md); causal consistency → [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md); HLC and clock uncertainty → [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md)

CDC envelopes carry the source's native logical position. PostgreSQL uses the **LSN**, MySQL the **GTID** (`server_uuid:txn_no`), and MongoDB the oplog timestamp plus counter. On a single primary, each is a total order. A MySQL **GTID set** holds per-`server_uuid` transaction ranges, which is structurally a version vector. GTIDs from different servers are not comparable.

| Source topology | Ordering you actually get | Clock to use |
|---|---|---|
| Single primary | Total order for the whole source | LSN / GTID |
| Sharded (Vitess, Citus); each key on one shard | Per-key total order (the key's shard); no order across shards | Per-shard GTID/LSN; app-level sequence for cross-shard causality |
| Multi-region SQL (CockroachDB, Spanner) | Commit timestamps from HLC / TrueTime | Source commit timestamp in the changefeed |
| Primary failover | New GTID `server_uuid` or LSN timeline; possible gap or rewind at the switch | Reconcile at the failover point (R3 step 3) |

**Practical rule.** Never order CDC events by arrival time or `updated_at`. Order per key by the envelope position (`source.lsn`, `source.gtid`). Debezium's `source.ts_ms` is wall-clock and can regress. For foreign-key integrity across tables or shards, buffer by entity and emit once the dependency is present.

---

### P5 Broadcast Semantics in Pub/Sub Fan-Out

**Primitive**: broadcast → [11-broadcast-protocols.md](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md)

Broadcast happens *across* consumer groups (Kafka) or subscriptions (Pulsar). *Within* one group or subscription, the dispatch mode decides who gets each message.

| Platform behavior | Delivery semantics |
|---|---|
| Kafka topic, N consumer groups | Each group receives every retained record; order is per partition only (a total order per partition) |
| Kafka compacted topic | Only the last written value per key is guaranteed to survive. A slow group can miss intermediate values, so it is not a full-history broadcast |
| Pulsar exclusive / failover subscription | One active consumer; ordered; failover on crash |
| Pulsar shared subscription | Competing consumers (load balancing, not broadcast); no ordering |
| Pulsar key_shared subscription | Per-key ordering, keys spread across consumers |
| Kafka Streams changelog topic | Per-partition total order replayed to standby tasks |

**Cross-partition order** exists only per key, and only while the key→partition mapping is stable. Adding partitions remaps keys.

**Membership.** KRaft replaced ZooKeeper for Kafka metadata. Pulsar's metadata store is pluggable, ZooKeeper historically (other backends: verify for your version). Consumer-group membership goes through the group coordinator, not gossip.

**Fan-out cost.** A Kafka log is written once, and each extra consumer group adds read load only. In Pulsar, give independent consumers their own subscriptions rather than one shared subscription.

---

### P6 Consumer-Group Rebalance Correctness

**Primitive**: fencing → [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)

The group coordinator is a single-leader authority for group state. It is not Raft; its safety comes from the generation or epoch fencing in P3.

| Protocol | Behavior | When to use |
|---|---|---|
| Classic eager (range, round-robin) | All members revoke everything and rejoin | Legacy; simple topologies |
| Classic cooperative-sticky (Kafka 2.4+) | Only moved partitions are revoked | Default choice on the classic protocol |
| Static membership (`group.instance.id`) | Keeps its assignment across restarts within `session.timeout.ms` | Stateful consumers, rolling restarts |
| Consumer protocol (KIP-848, `group.protocol=consumer`) | Broker-side incremental assignment, member epochs | Newer clusters (GA version: verify against Kafka release notes) |

**Correctness invariant.** Never commit or process for partitions you no longer own. In `onPartitionsRevoked`, do three things. First, flush in-flight work for the revoked partitions. Second, commit their offsets. Third, drop buffered records for them. Skipping the third step is the most common source of duplicates during a rebalance.

---

## Anti-Patterns

### A1 Choosing Availability Over Consistency for Financial Events

A payment topic runs `acks=1`, `min.insync.replicas=1`. The leader crashes before replication, the new leader lacks the acknowledged write, and the event is lost silently. Reconciliation finds it hours later. `acks=1` is the EL/AP choice.

**Fix.** Apply the P1 decision rule. Alert when a partition is under its minimum ISR, not only on `UnderReplicatedPartitions`. Below `min.insync.replicas`, `acks=all` producers get `NotEnoughReplicas` errors, so treat under-replication as a write-outage precursor. Keep `unclean.leader.election.enable=false` so an out-of-sync replica never becomes leader.

### A2 Idempotency Key Scoped Too Broadly Across Pipeline Stages

A Flink job uses the input `message_id` as the single dedupe key for the Kafka write, an external API call, and a PostgreSQL upsert. After a partial failure and restore, the key is already present, so every stage is skipped, including the upsert that failed.

**Fix.** Derive stage-scoped keys from the root key so that each stage dedupes on its own:

```
root_key          = message_id
kafka_write_key   = sha256(root_key + ":kafka:" + output_topic + partition)
api_call_key      = sha256(root_key + ":api:" + endpoint + ":v1")
sink_upsert_key   = sha256(root_key + ":pg:" + table + primary_key_value)
```

### A3 Fencing Token Not Enforced at the Sink Layer

A Flink job writes to PostgreSQL through a plain JDBC sink. After a failover, Flink restores from a checkpoint and replays records that the previous attempt had already written. The `ON CONFLICT` target is not unique per record, so duplicates land.

**Root cause.** The fencing guarantee (Flink's two-phase commit) protects the Kafka output topic but does not extend to the JDBC sink. The JDBC sink does not participate in Flink's checkpoint protocol unless it implements two-phase commit on the Sink V2 API (`SupportsCommitter` with a committing writer); the legacy `TwoPhaseCommitSinkFunction` was removed in Flink 2.0. A simple JDBC sink is at-least-once, not exactly-once.

**Fix.**

1. Use a sink-side idempotency key derived from `(source_topic, source_partition, source_offset)`, plus a deterministic output ordinal if one source record fans out to several rows. Do not include `checkpoint_id` or `subtask_index`: a restore replays the same offsets under new checkpoint IDs (and possibly other subtasks), so the key would change and dedup would not fire.
2. Upsert on that key: `INSERT ... ON CONFLICT (idempotency_key) DO NOTHING`, or `DO UPDATE ... WHERE excluded.updated_at > sink.updated_at` for mutable rows.
3. Alternative: the JDBC connector's exactly-once sink uses XA transactions committed on checkpoint. It needs an XA-capable database; PostgreSQL requires `max_prepared_transactions > 0`. Check the current connector docs for the API. Prefer option 1 unless you need atomic multi-row visibility.

### A4 Assuming Wall-Clock Order for CDC Events

A warehouse merges CDC events from a sharded source with last-write-wins on `updated_at`. Clock skew between hosts, or an NTP step correction, makes a later write carry an earlier timestamp, and the warehouse keeps the stale value. Wall-clock time is not a logical clock ([05](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md)).

**Fix.**

- Same key: in a sharded source, each key lives on one shard. Order by that shard's log position: GTID transaction number within the current `server_uuid`, or LSN. Handle the failover boundary (R3 step 3).
- Cross-shard or cross-entity causality: the log cannot supply it. Have the originating service stamp an application sequence or version (for example, a per-aggregate version column or an outbox sequence) and merge on that.
- During resharding, the same key moves between shards. Use the resharding tool's cut-over marker, or the application version, to decide which copy wins.

### A5 Under-Replicated Ledgers in Pulsar/BookKeeper

A Pulsar namespace uses ensemble size E, write quorum Qw, and ack quorum Qa, with Qa < Qw. When a bookie fails, BookKeeper replaces it in the ensemble for new entries. Entries already written stay under-replicated until **autorecovery** re-replicates them. If autorecovery is disabled or backlogged and a second bookie fails, entries whose remaining copies sat on those bookies can be lost.

**Fix.** Run autorecovery, and alert on under-replicated ledgers. Set Qa = Qw for CDC and financial topics, so an entry is acknowledged only once it is fully written. Size E ≥ Qw with enough spare bookies for ensemble changes. Kafka has no sloppy quorum; its equivalent risk is unclean leader election (keep it disabled).

---

## Recipes

### R1 End-to-End Exactly-Once Effects with a Downstream Sink

**Goal.** Each source record has exactly one effect in PostgreSQL or ClickHouse across Flink task failures, Kafka leader failovers, and sink errors. The mechanism is at-least-once replay plus an idempotent sink, per the exactly-once receiver recipe in [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md).

```
Kafka Source (read_committed)
    → Flink Job (checkpointing, CheckpointingMode.EXACTLY_ONCE)
        → Enrichment / Transform operators
        → Sink operator: at-least-once writer + idempotent upsert
          (or Sink V2 two-phase commit: Sink + SupportsCommitter, when atomic visibility is required)
            → PostgreSQL (upsert keyed on idempotency_key)
```

**Step 1: Source.** Set `isolation.level=read_committed`. Flink tracks source offsets in checkpoints, so Kafka auto-commit is irrelevant to correctness.

**Step 2: Checkpointing.**

```java
env.enableCheckpointing(30_000, CheckpointingMode.EXACTLY_ONCE); // interval is illustrative
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(10_000);
env.getCheckpointConfig().setCheckpointTimeout(60_000);
```

**Step 3: Stable key from source coordinates.**

```java
// In the Sink V2 writer
String idempotencyKey = String.format(
    "%s:%d:%d:%d",
    sourceTopicName,        // topic
    sourcePartition,        // partition
    sourceOffset,           // offset (unique per message in Kafka)
    outputOrdinal           // deterministic index if one source record yields several sink rows;
                            // never checkpointId: restores replay offsets under new checkpoint IDs
);
```

**Step 4: Upsert.**

```sql
ALTER TABLE processed_events
    ADD COLUMN idempotency_key TEXT NOT NULL,
    ADD CONSTRAINT processed_events_idempotency_key_unique UNIQUE (idempotency_key);

-- Sink write (in the Flink Sink V2 writer/committer)
INSERT INTO processed_events (idempotency_key, entity_id, payload, processed_at)
VALUES (:key, :entity_id, :payload, NOW())
ON CONFLICT (idempotency_key) DO NOTHING;
```

**Step 5: Verify.**

- Kill a TaskManager mid-checkpoint, let the job recover, and confirm `COUNT(*) = COUNT(DISTINCT idempotency_key)`.
- Kill the partition leader. Flink should resume from the last checkpoint with no gaps or duplicates.
- Restart from a savepoint. The replay should produce no duplicates.

**Scope boundary.** HTTP calls or emails made inside the job are outside this boundary and need their own keys (R2).

### R2 Retry Budget Design Tied to Idempotency Keys

**Primitive**: idempotency → [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md); deadline propagation → [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md). Fleet-level retry budgets, retry storms, and load shedding belong to [qa-resilience](../../qa-resilience/references/cascading-failure-prevention.md). This recipe covers only per-operation attempts inside a stream job.

**Rules.**

- Generate the idempotency key **once, before the first attempt**, and reuse it on every retry and on DLQ replay. A new key per attempt defeats dedupe.
- Kafka producer: do not wrap `send()` in application retries. Use the client's retries bounded by `delivery.timeout.ms` (see P2).
- Use capped exponential backoff with jitter, and a hard attempt cap. Send non-retryable errors to the DLQ immediately.
- Never block the partition forever. On budget exhaustion, send the record with its idempotency key to a DLQ and continue.

```python
def process_with_retry(record, key, max_attempts, base_ms, cap_ms):
    for attempt in range(max_attempts):
        try:
            return call_with_idempotency_key(record, key)
        except NonRetryableError as e:
            return send_to_dlq(record, key, str(e))
        except RetryableError as e:
            if attempt == max_attempts - 1:
                return send_to_dlq(record, key, str(e))
            time.sleep(random.uniform(0, min(cap_ms, base_ms * 2 ** attempt)) / 1000)  # full jitter
```

**Starting budgets (unsourced heuristics — tune against your own failover times):** sink upsert, about 5 attempts from 200 ms. External HTTP API, about 3 from 500 ms, honoring `Retry-After`. Debezium snapshot chunk: more attempts and longer backoff to protect the source database. Flink async I/O: few attempts, because async capacity is fixed.

**Metrics.** Track `retry_attempt_count{operation}`, `retry_budget_exhausted_total{operation}`, and `idempotency_key_collision_total{operation}`. If exhaustions rise without collisions, the dependency is failing rather than you seeing duplicates. Find the cause before raising `max_attempts`.

### R3 CDC Pipeline with Causal Ordering Across Shards

**Goal.** Merge CDC from a sharded MySQL source (for example, Vitess) into one topic. Preserve per-key order, respect cross-shard dependencies that the application declares, and survive primary failovers.

**Primitives**: [05](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md), [10](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md), [08](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)

```
Shard 0/1/2 primaries ── Debezium (Vitess connector via VStream, or MySQL connector per shard)
      → per-shard (or per-table) Kafka topics
      → Flink merge job keyed by entity_id (causal buffer)
      → merged topic → warehouse / search / cache
```

**Step 1: Positions.** Keep `source.gtid` (MySQL connector) or the VStream position (Vitess connector) in every event, and key topics by entity ID so that per-key order holds.

**Step 2: Causal buffer (Flink `KeyedProcessFunction` on `entity_id`).** Emit an event when its declared dependencies have been emitted; otherwise buffer it and register a timer. Dependencies must come from the application, such as an outbox row carrying `depends_on` versions. CDC positions cannot express cross-shard causality.

```java
public void processElement(CdcEvent e, Context ctx, Collector<CdcEvent> out) throws Exception {
    if (allDependenciesDelivered(e.getDependsOn())) {
        out.collect(e); markDelivered(e.getVersion()); flushReady(out);
    } else {
        pending.put(e.getVersion(), e);
        ctx.timerService().registerProcessingTimeTimer(
            ctx.timerService().currentProcessingTime() + DEP_TIMEOUT_MS); // tune; illustrative
    }
}
// onTimer: a dependency is missing past the timeout. Emit a GAP marker and alert.
// Do not guess an order: GTIDs from different server_uuids are not comparable.
```

**Step 3: Failover fencing.** A new primary writes GTIDs under a new `server_uuid`. When the merge job sees a `server_uuid` change for shard S:

1. Drain the buffered events for S in their current per-key order.
2. Reset dependency tracking for S.
3. Treat the new `server_uuid` as authoritative.
4. Emit a `{"type": "FAILOVER", "shard": S, "new_uuid": "..."}` sentinel. Consumers invalidate cached state for S's entities and re-read from that point.

**Step 4: Verify.**

- Write A to X, then B to Y where B depends on A, with X and Y on different shards. Inject 500 ms of delay on X's shard. B must never be emitted before A.
- Fail over a shard mid-test. There should be no per-key regression after the sentinel.
- Remove a dependency so that it never arrives. The GAP marker and the alert should both fire.

---

## Cross-References

**Foundation** (`foundations-distributed-systems`): [SKILL.md](../../foundations-distributed-systems/SKILL.md) · [primitives-overview.md](../../foundations-distributed-systems/references/primitives-overview.md) · [patterns-scenarios-traps.md](../../foundations-distributed-systems/references/patterns-scenarios-traps.md) · [execution-histories.md](../../foundations-distributed-systems/references/execution-histories.md) · [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md) · [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md) · [formal-theory-map.md](../../foundations-distributed-systems/references/formal-theory-map.md). Primitive templates are linked in the [Primitive Map](#primitive-map). To model-check a protocol, choose the tool through [foundations-formal-methods](../../foundations-formal-methods/SKILL.md).

**Related `data-streaming` references:**

- [control-theory-applied.md](control-theory-applied.md) — Backpressure, lag autoscaler, watermark tuning
- [queueing-theory-applied.md](queueing-theory-applied.md) — Partition planning, lag SLO, coordinator scaling
- [operations-and-slos.md](operations-and-slos.md) — Checkpoint policy, lag monitoring, incident drills
- [cdc-and-schema-governance.md](cdc-and-schema-governance.md) — Debezium rollout, tombstones, schema evolution
- [stream-processing-patterns.md](stream-processing-patterns.md) — Stateful joins, windows, aggregations

---

## Sources

- Kleppmann, M. (2017). _Designing Data-Intensive Applications_, Chapters 5, 8, 9, 11. [dataintensive.net](https://dataintensive.net/)
- Apache Kafka documentation — producer idempotence, transactions, ISR, KRaft, consumer rebalance protocols. [kafka.apache.org/documentation](https://kafka.apache.org/documentation/)
- Apache Flink documentation — checkpointing, Sink V2, Kafka and JDBC connectors. [flink.apache.org/docs](https://flink.apache.org/docs/)
- Debezium documentation — MySQL and Vitess connectors, GTID handling, snapshot modes. [debezium.io/documentation](https://debezium.io/documentation/)
- Apache Pulsar / BookKeeper documentation — ensemble, write and ack quorums, autorecovery, subscription types. [pulsar.apache.org/docs](https://pulsar.apache.org/docs/)
- Primary papers (Raft, Lamport clocks, FLP, CAP, leases, Dynamo) are cited in the foundation templates linked above.
