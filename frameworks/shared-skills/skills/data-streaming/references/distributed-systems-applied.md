# Distributed Systems Applied to Data Streaming

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Distributed systems theory and streaming platforms share the same underlying failure modes: split-brain leaders corrupt ordered logs, stale replicas serve wrong offsets, duplicate deliveries corrupt sinks, and partition rebalances expose unsafe leader transitions. This reference maps the 11 distributed-systems primitives from `foundations-distributed-systems` to concrete streaming decisions in Kafka, Flink, Debezium, and Pulsar pipelines.

## Table of Contents

- [Why Distributed Systems Theory Matters for Streaming](#why-distributed-systems-theory-matters-for-streaming)
- [Patterns](#patterns)
  - [P1 Kafka ISR vs. Quorum Semantics — Choosing Write Durability](#p1-kafka-isr-vs-quorum-semantics--choosing-write-durability)
  - [P2 Exactly-Once via Idempotent Producer and Transactional Consumer](#p2-exactly-once-via-idempotent-producer-and-transactional-consumer)
  - [P3 Leader-Epoch Fencing During Partition Rebalance](#p3-leader-epoch-fencing-during-partition-rebalance)
  - [P4 CDC Ordering Using Vector Clocks](#p4-cdc-ordering-using-vector-clocks)
  - [P5 Broadcast Semantics in Pub/Sub Fan-Out](#p5-broadcast-semantics-in-pubsub-fan-out)
  - [P6 Consumer-Group Rebalance Correctness via Raft-Modeled State](#p6-consumer-group-rebalance-correctness-via-raft-modeled-state)
- [Anti-Patterns](#anti-patterns)
  - [A1 CAP Misconfiguration — Choosing Availability Over Consistency for Financial Events](#a1-cap-misconfiguration--choosing-availability-over-consistency-for-financial-events)
  - [A2 Idempotency Key Scoped Too Broadly Across Pipeline Stages](#a2-idempotency-key-scoped-too-broadly-across-pipeline-stages)
  - [A3 Fencing Token Not Enforced at the Sink Layer](#a3-fencing-token-not-enforced-at-the-sink-layer)
  - [A4 Assuming Wall-Clock Order for CDC Events Across Shards](#a4-assuming-wall-clock-order-for-cdc-events-across-shards)
  - [A5 Sloppy Quorum Without Hinted Handoff in Leaderless Pub/Sub](#a5-sloppy-quorum-without-hinted-handoff-in-leaderless-pubsub)
- [Recipes](#recipes)
  - [R1 End-to-End Exactly-Once with Downstream Sink](#r1-end-to-end-exactly-once-with-downstream-sink)
  - [R2 Retry Budget Design Tied to Idempotency Keys](#r2-retry-budget-design-tied-to-idempotency-keys)
  - [R3 CDC Pipeline with Vector-Clock Ordering and Causal-Consistent Delivery](#r3-cdc-pipeline-with-vector-clock-ordering-and-causal-consistent-delivery)
- [Cross-References](#cross-references)
- [Sources](#sources)

---

## Why Distributed Systems Theory Matters for Streaming

Streaming platforms are distributed systems. Kafka partitions are replicated logs managed by a Raft-equivalent protocol (KRaft). Exactly-once delivery is an application of idempotency over at-least-once transport. Consumer group rebalance is a leader election problem. CDC ordering across shards is a vector clock problem. Pub/sub fan-out is a broadcast protocol choice.

Treating these as platform-specific configuration knobs — rather than instances of known distributed-systems problems — leads to repeatable failure patterns: silent data loss when quorum is misconfigured, duplicate writes when idempotency keys are reused, split-brain during leader transitions when fencing is absent, and causal anomalies in CDC streams when ordering is not explicitly modeled.

The patterns and recipes below name the underlying primitive, map it to the streaming context, and provide actionable decision rules.

---

## Patterns

### P1 Kafka ISR vs. Quorum Semantics — Choosing Write Durability

**Primitive**: [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md) | [01-cap-pacelc.md](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md)

**What it is.** Kafka's In-Sync Replica (ISR) list is an adaptive quorum. The broker leader tracks which replicas are caught up within `replica.lag.time.max.ms`. A write is acknowledged only when all members of the ISR have persisted the message. The ISR can shrink to 1 (the leader alone) during replica lag, which trades consistency for availability.

This is a PACELC choice: Kafka's default configuration (`acks=all`, `min.insync.replicas=2`) is EC — it adds replication latency under normal operation to preserve consistency. Setting `acks=1` is EL — it returns immediately from the leader, accepting possible data loss if the leader crashes before replication completes.

**Kafka quorum mapping to NWR:**

| Kafka setting | NWR equivalent | Guarantee |
|---|---|---|
| `acks=0` | W=0 | Fire-and-forget; no durability |
| `acks=1` | W=1 | Leader-only write; data loss on leader failure |
| `acks=all` + `min.insync.replicas=2` | W=2, N=3 | Strong durability; ISR must have 2 members |
| `acks=all` + `min.insync.replicas=N` | W=N | Write-to-all; any failure blocks writes |

**Decision rule.** For financial events, audit logs, or CDC source topics: `acks=all`, `min.insync.replicas=2`, replication factor 3. For high-throughput telemetry where occasional loss is acceptable: `acks=1` with `replication.factor=2`.

**KRaft context (Kafka 4.0+).** KRaft uses a Raft quorum of controller nodes to manage broker metadata (topic assignments, ISR changes, partition leadership). Controller quorum size follows odd-N Raft sizing — 3 or 5 controllers. Do not confuse controller quorum size with `replication.factor` for data partitions; they are independent.

```
Example: 3 controllers (Raft quorum), replication.factor=3 per partition.
- Controller quorum: majority = 2 → tolerates 1 controller failure.
- Partition ISR (min.insync.replicas=2): tolerates 1 replica failure.
```

**Tail latency.** Quorum writes wait for the slowest ISR member. Monitor `ReplicaFetcherLagMetrics` per broker. An ISR member falling behind slows every write on that partition until it is removed from ISR or catches up.

---

### P2 Exactly-Once via Idempotent Producer and Transactional Consumer

**Primitive**: [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md) | [02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)

**What it is.** FLP Impossibility establishes that no deterministic protocol can guarantee consensus (and therefore exactly-once delivery) in an asynchronous system with even one faulty process. Kafka's exactly-once semantics (EOS) create the _illusion_ of exactly-once by combining two idempotency layers:

1. **Idempotent producer** (`enable.idempotence=true`): each producer is assigned a Producer ID (PID). Every batch carries a monotonically increasing sequence number per partition. The broker deduplicates retried batches by `(PID, partition, sequence_number)`. Duplicate sequences are silently discarded.

2. **Transactional producer + read_committed consumer**: the producer wraps a batch of writes across multiple partitions and/or topics in a transaction. The broker writes a transaction marker (COMMIT or ABORT) atomically. Consumers with `isolation.level=read_committed` skip messages from aborted transactions and messages without a COMMIT marker.

**The idempotency key in Kafka terms:**

```
idempotency key = (producer_id, partition, sequence_number)
dedupe store    = broker-side sequence tracking per (PID, partition)
atomic execute  = batch write + sequence increment in a single broker append
```

**Scope of the guarantee.** Kafka EOS covers broker-to-broker deduplication and consumer-visible ordering within the transaction. It does **not** cover:

- Duplicate delivery to the consumer application if the consumer crashes between `poll()` and committing the offset.
- Idempotency at the sink (downstream database, API, or object store).
- Side effects outside Kafka (HTTP calls, emails) made inside the consumer processing loop.

**Platform specifics.**

- Flink with Kafka source + Kafka sink: Flink's two-phase commit (TwoPhaseCommitSinkFunction) aligns Flink checkpoints with Kafka transactions. On checkpoint completion, the Kafka transaction is committed; on recovery, uncommitted transactions are aborted. End-to-end exactly-once within the Flink → Kafka boundary.
- Kafka Streams: `processing.guarantee=exactly_once_v2` (EOS-V2) uses one transaction per task rather than one per thread. Fewer transactions = lower overhead. Default since Kafka 3.0.

---

### P3 Leader-Epoch Fencing During Partition Rebalance

**Primitive**: [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md) | [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md)

**What it is.** Kafka assigns each partition a **leader epoch** — a monotonically increasing integer incremented on every leader election. This is functionally equivalent to a Raft term number or a fencing token. The leader epoch is the mechanism by which Kafka prevents a deposed partition leader from writing stale data after a new leader has been elected.

**Fencing flow during a rebalance or broker failure:**

```
Epoch 5: Broker A is partition leader. Produces and replicates normally.

Broker A experiences a GC pause (60 seconds).
Controller detects heartbeat timeout → elects Broker B as leader → epoch = 6.

Broker A resumes from GC pause. Believes it is still leader (epoch 5).
Broker A attempts to write. Followers receive AppendEntries with epoch 5.
Followers reject: epoch 5 < current epoch 6. Broker A learns it is deposed.

Broker B (epoch 6) continues as leader. Broker A becomes follower.
```

**Where fencing matters for streaming pipelines:**

- **Producer with acks=all during failover**: a producer retrying a write after the original leader crashed must use the new leader's epoch. The idempotent producer handles this automatically — the PID + sequence is revalidated against the new leader.
- **Consumer offset commit during rebalance**: a consumer that has processed records but not yet committed offsets during a rebalance may commit to a partition it no longer owns. The group coordinator rejects offset commits with a stale `generation_id`, which is the consumer group's fencing token equivalent.
- **Flink checkpoint alignment**: Flink barriers propagate through the operator graph; a checkpoint that spans a Kafka partition leadership change may contain offsets from both the old and new leader. The Kafka source connector uses the leader epoch in offset metadata to detect and handle this safely.

**Lease-epoch relationship.** Kafka's leader epoch is not a time-bounded lease — it does not expire on a clock. It is a strictly monotonically increasing counter incremented at election time, making it a pure fencing token rather than a combined lease + token. This is safer than lease-based fencing because it does not rely on clock synchronization.

---

### P4 CDC Ordering Using Vector Clocks

**Primitive**: [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md) | [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)

**What it is.** A CDC pipeline captures database write-ahead log (WAL) events from a source database and delivers them to a downstream topic. When the source is sharded (multiple primary nodes) or when a failover occurs mid-stream, events from different shards may arrive at the consumer out of causal order.

Wall-clock timestamps from `updated_at` columns are insufficient for ordering: two concurrent writes on different shards may have timestamps within NTP skew (sub-millisecond), and a clock correction on one node can produce timestamps that go backwards.

**Vector-clock analog in CDC systems:**

Debezium and most log-based CDC tools embed the source's native logical clock into the event envelope. For PostgreSQL, this is the **Log Sequence Number (LSN)**; for MySQL, the **GTID (Global Transaction ID)**; for MongoDB, the **oplog timestamp + operation counter**.

These are monotonically increasing logical clocks on a single primary — Lamport-equivalent for a single-shard source. For multi-primary setups (MySQL Group Replication, Vitess, CockroachDB), the system assigns globally unique transaction IDs that encode causal ordering — vector-clock equivalent.

**Ordering guarantees by source topology:**

| Source topology | Ordering guarantee | CDC clock type |
|---|---|---|
| Single primary | Total order within the shard | LSN / GTID monotonic |
| Multi-primary (same region) | Causal order within a transaction; concurrent across primaries | GTID set / CockroachDB HLC |
| Multi-primary (multi-region) | Eventual; causal order only with explicit coordination | CockroachDB HLC, Spanner TrueTime |
| Post-failover (new primary) | Ordering gap at failover point; requires LSN reconciliation | LSN restarts from new primary |

**Practical rule.** When consuming CDC events from multi-shard sources, do not rely on event arrival time or `updated_at` for ordering. Use the CDC envelope's `source.lsn`, `source.gtid`, or `source.ts_ms` (with the understanding that `ts_ms` is wall-clock and may regress). For foreign-key integrity across tables, buffer events keyed by entity ID and emit only when the causal chain is complete.

---

### P5 Broadcast Semantics in Pub/Sub Fan-Out

**Primitive**: [11-broadcast-protocols.md](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md)

**What it is.** A pub/sub fan-out — one topic, many independent consumer groups — implements a specific broadcast protocol depending on the platform and configuration:

| Streaming platform behavior | Broadcast type | Guarantee |
|---|---|---|
| Kafka topic with N consumer groups | Reliable broadcast per group | Every group gets every message; order preserved per partition |
| Kafka compacted topic | Best-effort broadcast (only latest value per key) | Old values may be overwritten before a slow group reads them |
| Pulsar shared subscription | Best-effort broadcast | Messages distributed across consumers; no ordering guarantee |
| Pulsar exclusive subscription | Reliable broadcast (single consumer) | Single active consumer per subscription; failover on crash |
| Pulsar key-shared subscription | Reliable + ordered per key | Same key always delivered to the same consumer instance |
| Kafka Streams changelog topics | Total-order broadcast | All standby tasks replicate state in the same order |

**Total-order broadcast equivalence.** Kafka's replicated log is a total-order broadcast: all consumers in a group receive the same messages in the same order within a partition. Across partitions, ordering is only guaranteed per key if the producer uses consistent key-based partitioning.

**Gossip for cluster membership.** Kafka (pre-KRaft) and Pulsar use ZooKeeper for cluster membership; KRaft replaces ZooKeeper with an internal Raft-based gossip-free quorum. Redpanda uses Raft natively. Consumer group membership changes (joins, leaves, crashes) are disseminated via the group coordinator, not gossip — convergence is deterministic (O(1) once the coordinator processes the join group request), not probabilistic.

**Fan-out amplification.** Adding consumer groups to a Kafka topic is O(1) in broker cost — the log is written once. Adding Pulsar shared subscribers in a single subscription increases message dispatch overhead because the broker must track per-consumer acknowledgements. Design fan-out topology before adding subscribers: separate subscriptions for independent consumers in Pulsar; separate consumer groups in Kafka.

---

### P6 Consumer-Group Rebalance Correctness via Raft-Modeled State

**Primitive**: [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md) | [03-paxos.md](../../foundations-distributed-systems/assets/templates/distributed-systems/03-paxos.md)

**What it is.** Kafka's consumer group coordinator is a broker that acts as the single leader for group state management — equivalent to the Raft leader role. The group coordinator:

1. Receives `JoinGroup` requests from all group members (election phase).
2. Elects a consumer as group leader (not to be confused with partition leader).
3. The group leader runs the partition assignment algorithm and submits the result via `SyncGroup`.
4. All members receive their assigned partitions and resume consumption.

This is structurally a single-leader protocol. Safety properties:

- **At-most-one assignment at any time**: the coordinator's `generation_id` is the fencing token. A consumer holding a stale `generation_id` (from a previous rebalance) has its offset commits rejected.
- **Log matching equivalent**: all consumers in the group see the same partition assignment after `SyncGroup` completes — equivalent to Raft's log matching property.

**Rebalance protocol versions:**

| Protocol | Behavior | When to use |
|---|---|---|
| Eager (RANGE, ROUNDROBIN) | All consumers stop and rejoin simultaneously | Kafka < 2.4; simple topologies |
| Cooperative Sticky (Kafka 2.4+) | Only revoked partitions change hands; others continue consuming | Production; reduces stop-the-world duration |
| Static membership (`group.instance.id`) | Consumer retains assignment across restarts within `session.timeout.ms` | Stateful consumers (Flink task slots, long-lived workers) |

**Correctness invariant.** A consumer must not commit offsets for partitions it no longer owns. After detecting a rebalance (via `ConsumerRebalanceListener.onPartitionsRevoked`), the consumer must:

1. Flush any in-flight processing for revoked partitions.
2. Commit offsets for revoked partitions before returning from `onPartitionsRevoked`.
3. Discard any buffered records for revoked partitions — do not process after the revocation callback returns.

Failing step 3 is the most common source of duplicate processing during rebalances.

---

## Anti-Patterns

### A1 CAP Misconfiguration — Choosing Availability Over Consistency for Financial Events

**Diagnosis.** A Kafka topic for payment events is configured with `acks=1` and `min.insync.replicas=1` for throughput. The partition leader crashes mid-flight. The new leader does not have the last acknowledged write. The payment event is silently lost. Downstream reconciliation detects the discrepancy hours later.

**CAP framing.** `acks=1` is an AP choice: Kafka acknowledges the write before replication, prioritizing availability (the producer gets a response) over consistency (the write survives leader failure). For financial events, this is wrong — the correct choice is CP: `acks=all` with `min.insync.replicas=2`, accepting the write failure if the ISR shrinks below 2.

**Fix.** Set `acks=all`, `min.insync.replicas=2`, `replication.factor=3` for all topics carrying financial, audit, or CDC events. Alert on `UnderReplicatedPartitions > 0` — a partition with fewer ISR members than `min.insync.replicas` will block writes. Do not treat `UnderReplicatedPartitions` as an informational metric; it signals imminent write failure risk.

---

### A2 Idempotency Key Scoped Too Broadly Across Pipeline Stages

**Diagnosis.** A Flink job uses the input Kafka message's `message_id` as the idempotency key for all downstream writes. The same `message_id` is used for the enriched record written to the output topic, the side-effect call to an external API, and the sink upsert into PostgreSQL. When the Flink job restarts from a checkpoint, it reprocesses records and finds the `message_id` already in the dedupe store — it skips all downstream operations, including the PostgreSQL upsert that may have failed in the previous attempt.

**The scoping error.** One idempotency key covering multiple independent operations makes each operation's deduplication contingent on all others having succeeded. If any operation fails after the key is written but before all operations complete, the key is present in the dedupe store but the downstream state is inconsistent.

**Fix.** Derive stage-scoped idempotency keys from the root key:

```
root_key          = message_id
kafka_write_key   = sha256(root_key + ":kafka:" + output_topic + partition)
api_call_key      = sha256(root_key + ":api:" + endpoint + ":v1")
sink_upsert_key   = sha256(root_key + ":pg:" + table + primary_key_value)
```

Each stage's dedupe store is independent. A failure and retry at the API call stage does not affect the Kafka write deduplication record.

---

### A3 Fencing Token Not Enforced at the Sink Layer

**Diagnosis.** A Flink job writes to a PostgreSQL sink using a JDBC connector. During a leader partition failover, Flink recovers from a checkpoint and reprocesses a batch that was already written by the previous task attempt (before the checkpoint completed). The JDBC sink performs `INSERT ON CONFLICT DO NOTHING` — but the conflict key is on a non-unique column combination, so the deduplication does not fire. Duplicate rows appear in the sink table.

**Root cause.** The fencing guarantee (Flink's two-phase commit) protects the Kafka output topic but does not extend to the JDBC sink. The JDBC sink does not participate in Flink's checkpoint protocol unless it implements `TwoPhaseCommitSinkFunction`. A simple JDBC sink is at-least-once, not exactly-once.

**Fix.**

1. Use a sink-side idempotency key derived from `(checkpoint_id, subtask_index, record_offset)` — a composite that uniquely identifies each record in the processing history.
2. Implement the sink as `INSERT ... ON CONFLICT (idempotency_key) DO UPDATE SET ... WHERE excluded.updated_at > sink.updated_at` — conditional upsert using the idempotency key as the conflict target.
3. Alternatively, use the Flink JDBC connector with `JdbcExecutionOptions.builder().withMaxRetries(0)` and transactional batch mode — write all records in a batch within a single PostgreSQL transaction, using the checkpoint ID as the transaction key.

---

### A4 Assuming Wall-Clock Order for CDC Events Across Shards

**Diagnosis.** A CDC pipeline from a Vitess (sharded MySQL) source captures `updated_at` timestamps from the source rows and uses them to merge concurrent updates in the downstream data warehouse. Two shards process concurrent writes to the same entity with timestamps within 1ms of each other. NTP skew causes the later write (on shard 2) to have a lower `updated_at` than the earlier write (on shard 1). The warehouse retains the older value.

**Root cause.** Wall-clock timestamps are not logical clocks. They do not satisfy the Lamport guarantee (`A → B ⟹ ts(A) < ts(B)`) when events originate from different processes with independent clocks.

**Fix.** Use the CDC envelope's logical clock for ordering:

- For Vitess/MySQL: use `GTID` sets. The Debezium MySQL connector embeds `gtid` in the event envelope. GTIDs are globally unique and monotonically increasing per server, enabling causal ordering across shards.
- For multi-region sources where even GTID ordering is ambiguous across primaries: add an application-level sequence number generated by the service that originates the mutation, propagated through the event and captured by CDC.
- For the warehouse merge logic: replace `last_write_wins on updated_at` with `last_write_wins on (shard_id, gtid)` using a deterministic tie-break rule (higher shard ID wins) for truly concurrent writes.

---

### A5 Sloppy Quorum Without Hinted Handoff in Leaderless Pub/Sub

**Diagnosis.** A Pulsar cluster with 3 bookies (ledger storage nodes) is configured with `EnsembleSize=3, WriteQuorum=2, AckQuorum=2`. During a network partition, one bookie is unreachable. Pulsar falls back to writing to the two available bookies — a sloppy quorum. The partition heals, but the third bookie's hinted handoff is delayed beyond the topic's retention period. A consumer replaying from the beginning of the topic reads an incomplete sequence from the third bookie.

**Root cause.** Sloppy quorums improve write availability during a partition (PACELC: PA choice) but do not guarantee that all quorum members have all data when the partition heals. Hinted handoff is the repair mechanism — without it, or when it is delayed past retention, the gap is permanent.

**Fix.**

- For Pulsar: monitor `ManagedLedgerUnacknowledgedMessages` per bookie. Alerts on missing entries trigger proactive hinted handoff before the retention window expires.
- Set `managedLedgerUnacknowledgedRangesOpenCacheSetEnabled=true` in Pulsar to track unacknowledged ranges explicitly.
- For strict ordering guarantees (CDC, financial events): use `AckQuorum=EnsembleSize` (write to all bookies before acknowledging). This sacrifices the sloppy-quorum availability benefit but eliminates the gap risk.
- For Kafka equivalents: set `min.insync.replicas = replication.factor - 0` — writes block rather than fall back to a sloppy quorum. Alert on `UnderReplicatedPartitions` before this condition is reached.

---

## Recipes

### R1 End-to-End Exactly-Once with Downstream Sink

**Goal.** Guarantee that each source event produces exactly one row in a downstream PostgreSQL or ClickHouse sink, surviving Flink task failures, Kafka leader failovers, and sink connection errors.

**Primitives used.**

- Idempotency → [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)
- Leases and Fencing → [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)
- Raft (leader epoch as fencing token) → [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md)

**Architecture.**

```
Kafka Source (read_committed)
    → Flink Job (checkpointing, EOS-V2)
        → Enrichment / Transform operators
        → Sink operator (TwoPhaseCommitSinkFunction)
            → PostgreSQL (transactional upsert with idempotency key)
```

**Step 1: Configure the Kafka source for exactly-once reads.**

```properties
# Kafka consumer config
isolation.level=read_committed
enable.auto.commit=false
# Flink Kafka connector
scan.bounded.mode=latest_offset   # or unbounded for streaming
```

**Step 2: Configure Flink checkpointing aligned with Kafka EOS.**

```java
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
env.enableCheckpointing(30_000);  // 30-second checkpoint interval
env.getCheckpointConfig().setCheckpointingMode(CheckpointingMode.EXACTLY_ONCE);
env.getCheckpointConfig().setMinPauseBetweenCheckpoints(10_000); // avoid back-to-back checkpoints
env.getCheckpointConfig().setCheckpointTimeout(60_000);          // abort checkpoint if > 60s
```

**Step 3: Derive a sink-side idempotency key.**

For each record flowing through the Flink job, derive a stable idempotency key that survives replay:

```java
// In the sink function's invoke() method
String idempotencyKey = String.format(
    "%s:%d:%d:%d",
    sourceTopicName,        // topic
    sourcePartition,        // partition
    sourceOffset,           // offset (unique per message in Kafka)
    checkpointId            // optional: if the same offset can produce multiple sink rows
);
```

The `(topic, partition, offset)` triple is immutable — the same source message always maps to the same idempotency key. This satisfies the "client-generated, globally unique" requirement from idempotency primitive 07.

**Step 4: Sink upsert with idempotency enforcement.**

```sql
-- PostgreSQL sink DDL
ALTER TABLE processed_events
    ADD COLUMN idempotency_key TEXT NOT NULL,
    ADD CONSTRAINT processed_events_idempotency_key_unique UNIQUE (idempotency_key);

-- Sink write (in Flink TwoPhaseCommitSinkFunction.invoke)
INSERT INTO processed_events (idempotency_key, entity_id, payload, processed_at)
VALUES (:key, :entity_id, :payload, NOW())
ON CONFLICT (idempotency_key) DO NOTHING;
```

`ON CONFLICT DO NOTHING` is the atomic check-and-execute from idempotency primitive 07. The unique constraint is the dedupe store. The sink never needs to read before writing.

**Step 5: Verify end-to-end.**

```
Verification checklist:
- Kill a Flink task manager mid-checkpoint → job recovers → no duplicate rows in PostgreSQL
  (check: SELECT COUNT(*) / COUNT(DISTINCT idempotency_key) = 1)
- Kill the Kafka partition leader → new leader elected → Flink resumes from last checkpoint
  → no gaps or duplicates in sink
- Restart Flink job from savepoint → source replays from saved offset → no duplicates
```

**Scope boundary.** This recipe covers Kafka → Flink → PostgreSQL. If the Flink job also calls an external HTTP API or sends emails, those calls are outside the transactional boundary and require their own idempotency keys (see R2).

---

### R2 Retry Budget Design Tied to Idempotency Keys

**Goal.** Define a retry budget for at-least-once operations (Kafka consumer processing, HTTP calls from stream jobs, CDC sink writes) that is bounded, observable, and safe to exhaust without data loss or duplication.

**Primitives used.**

- Idempotency → [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)
- FLP Impossibility → [02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)

**FLP context.** FLP impossibility means there is no protocol that guarantees termination with exactly-once semantics in an asynchronous system. The practical response is to design for at-least-once delivery and idempotent consumption — accept that retries will happen, bound how many are safe, and ensure each retry is detectable as a duplicate.

**Retry budget structure.**

```python
@dataclass
class RetryBudget:
    max_attempts: int        # hard ceiling on total attempts (including first)
    base_delay_ms: int       # initial backoff delay
    max_delay_ms: int        # ceiling on exponential backoff
    jitter_factor: float     # fraction of delay to randomize (0.0–0.5)
    idempotency_key: str     # MUST be fixed across all retries for the same operation

    def delay_for_attempt(self, attempt: int) -> float:
        """Exponential backoff with bounded jitter."""
        base = self.base_delay_ms * (2 ** attempt)
        capped = min(base, self.max_delay_ms)
        jitter = capped * self.jitter_factor * random.random()
        return (capped + jitter) / 1000.0  # seconds
```

**Key rule: the idempotency key must be generated once, before the first attempt, and reused across all retries.** If the key changes between attempts, each retry is a new operation from the dedupe store's perspective — duplicates bypass deduplication.

**Budget sizing by operation type:**

| Operation | Recommended max_attempts | base_delay_ms | Rationale |
|---|---|---|---|
| Kafka producer send | 3–5 | 100 | Broker restarts are fast; leader election < 30s |
| CDC sink upsert (PostgreSQL) | 5 | 200 | Connection pool exhaustion recovers in seconds |
| External HTTP API call | 3 | 500 | APIs have rate limits; aggressive retry causes throttling |
| Debezium snapshot chunk | 10 | 1000 | Snapshots are long-running; source DB load must be managed |
| Flink async I/O call | 3 | 100 | Async I/O has a fixed capacity; exhausted budget triggers DLQ |

**Dead-letter queue (DLQ) on budget exhaustion.**

```python
def process_with_retry(record, budget: RetryBudget):
    for attempt in range(budget.max_attempts):
        try:
            result = call_with_idempotency_key(record, budget.idempotency_key)
            return result
        except RetryableError as e:
            if attempt == budget.max_attempts - 1:
                send_to_dlq(record, budget.idempotency_key, str(e))
                return  # do not raise; do not block the consumer
            time.sleep(budget.delay_for_attempt(attempt))
        except NonRetryableError as e:
            send_to_dlq(record, budget.idempotency_key, str(e))
            return  # immediate DLQ for non-retriable errors
```

**DLQ design contract.** The DLQ record must include the `idempotency_key` from the failed operation. When the DLQ record is replayed manually, the idempotency key ensures the operation is still deduplicated correctly if the original attempt partially succeeded.

**Observability.**

```
Metrics to emit:
- retry_attempt_count{operation, attempt_number}  — histogram per attempt number
- retry_budget_exhausted_total{operation}         — counter for DLQ routing events
- idempotency_key_collision_total{operation}      — counter when dedupe store finds a match
```

A rising `retry_budget_exhausted_total` without a corresponding `idempotency_key_collision_total` means the operation is genuinely failing (not just duplicated). Investigate the root cause — do not increase `max_attempts` without understanding why the budget is exhausted.

---

### R3 CDC Pipeline with Vector-Clock Ordering and Causal-Consistent Delivery

**Goal.** Deliver CDC events from a multi-primary MySQL (Vitess) source to a downstream Kafka topic, preserving causal order across shards and surviving primary failovers without ordering gaps or regressions.

**Primitives used.**

- Vector Clocks and Lamport Timestamps → [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md)
- Causal Consistency → [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)
- Leases and Fencing → [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)

**Architecture.**

```
Vitess shard 0 (MySQL primary) ──┐
Vitess shard 1 (MySQL primary) ──┤── Debezium connectors ──→ Kafka per-shard topics
Vitess shard 2 (MySQL primary) ──┘         │
                                            ↓
                                   Flink merge job
                                   (causal ordering buffer)
                                            │
                                            ↓
                                   Kafka merged topic
                                   (ordered by GTID causal chain)
                                            │
                                            ↓
                                   Downstream consumers
                                   (data warehouse, search, cache)
```

**Step 1: Embed GTID in the CDC envelope.**

Debezium MySQL connector emits events with `source.gtid` in the event payload. Configure the connector to include GTID sets:

```json
{
  "connector.class": "io.debezium.connector.mysql.MySqlConnector",
  "include.schema.changes": "true",
  "gtid.source.includes": ".*",
  "snapshot.mode": "initial"
}
```

Each event payload includes:

```json
{
  "source": {
    "server_id": 1001,
    "gtid": "3E11FA47-71CA-11E1-9E33-C80AA9429562:1-5",
    "file": "binlog.000003",
    "pos": 154,
    "ts_ms": 1746182400000
  }
}
```

**Step 2: Flink causal ordering buffer.**

The merge job buffers events from all per-shard topics and emits them in GTID causal order:

```java
// Pseudocode: causal ordering buffer keyed by entity_id
// Flink KeyedProcessFunction on entity_id
public class CausalOrderBuffer extends KeyedProcessFunction<String, CdcEvent, CdcEvent> {

    // State: set of received GTIDs for this entity
    private MapState<String, CdcEvent> pendingEvents;

    @Override
    public void processElement(CdcEvent event, Context ctx, Collector<CdcEvent> out) {
        String gtid = event.getSourceGtid();
        String[] dependencies = event.getCausalDependencies(); // preceding GTIDs this event depends on

        if (allDependenciesDelivered(dependencies)) {
            out.collect(event);
            markDelivered(gtid);
            // Attempt to flush any buffered events that depended on this one
            flushReady(out);
        } else {
            // Buffer event until dependencies are delivered
            pendingEvents.put(gtid, event);
            // Set a timer to detect causal dependency gaps (source failover)
            ctx.timerService().registerProcessingTimeTimer(
                ctx.timerService().currentProcessingTime() + 30_000L
            );
        }
    }

    @Override
    public void onTimer(long timestamp, OnTimerContext ctx, Collector<CdcEvent> out) {
        // If events have been buffered longer than 30s without their dependencies arriving,
        // the source shard likely experienced a failover. Emit buffered events in GTID
        // lexicographic order as a best-effort causal approximation.
        emitBufferedInGtidOrder(out);
    }
}
```

**Step 3: Fencing on source failover.**

When a Vitess shard primary fails over, the new primary assigns new GTIDs from a different `server_uuid`. The Debezium connector detects the binlog discontinuity and emits a `HEARTBEAT` or schema change event. The Flink merge job uses this as a fencing signal:

```
On detecting server_uuid change for shard S:
1. Drain all buffered events for shard S (emit in current GTID order).
2. Reset the causal dependency tracking for shard S.
3. Begin accepting events from the new server_uuid as the authoritative source.
4. Emit a sentinel event to downstream consumers: {"type": "FAILOVER", "shard": S, "new_uuid": "..."}
```

Downstream consumers that maintain entity state must handle the FAILOVER sentinel by invalidating any cached state for entities on shard S and re-reading from the Kafka topic from the failover point.

**Step 4: Verify causal consistency.**

```
Verification:
- Generate two causally related writes: write A to entity X, then write B to entity Y
  where B's application logic reads entity X's value.
- Inject 500ms latency to shard 0 (entity X's shard) to simulate skew.
- Verify that consumers never observe B before A for the same entity.
- Simulate a shard failover mid-test: verify no ordering regression after the FAILOVER sentinel.
```

---

## Cross-References

**Primitive definitions** (full definitions in `foundations-distributed-systems`):

- [01-cap-pacelc.md](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md) — CAP theorem and PACELC extension
- [02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md) — FLP impossibility and its practical implications
- [03-paxos.md](../../foundations-distributed-systems/assets/templates/distributed-systems/03-paxos.md) — Paxos consensus algorithm
- [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md) — Raft consensus, leader election, log replication
- [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md) — Vector clocks, Lamport timestamps, causal ordering
- [06-crdts.md](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md) — CRDTs for conflict-free merges in leaderless replication
- [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md) — Idempotency keys, dedupe stores, exactly-once illusion
- [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md) — Leases, fencing tokens, split-brain prevention
- [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md) — NWR quorum model, consistency configurations
- [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md) — Causal consistency model and read-your-writes
- [11-broadcast-protocols.md](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md) — Gossip, reliable broadcast, total-order broadcast

**Related `data-streaming` references:**

- [control-theory-applied.md](control-theory-applied.md) — Backpressure, lag autoscaler, watermark tuning
- [queueing-theory-applied.md](queueing-theory-applied.md) — Partition planning, lag SLO, coordinator scaling
- [operations-and-slos.md](operations-and-slos.md) — Checkpoint policy, lag monitoring, incident drills
- [cdc-and-schema-governance.md](cdc-and-schema-governance.md) — Debezium rollout, tombstones, schema evolution
- [stream-processing-patterns.md](stream-processing-patterns.md) — Stateful joins, windows, aggregations

---

## Sources

- Kleppmann, M. (2017). _Designing Data-Intensive Applications_, Chapters 5, 8, 9, 11. [dataintensive.net](https://dataintensive.net/)
- Ongaro, D., & Ousterhout, J. (2014). In Search of an Understandable Consensus Algorithm. USENIX ATC. [raft.github.io/raft.pdf](https://raft.github.io/raft.pdf)
- DeCandia, G., et al. (2007). Dynamo: Amazon's Highly Available Key-Value Store. SOSP. [doi.org/10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)
- Lamport, L. (1978). Time, Clocks, and the Ordering of Events in a Distributed System. CACM. [lamport.azurewebsites.net/pubs/time-clocks.pdf](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- Gilbert, S., & Lynch, N. (2002). Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services. ACM SIGACT News. [doi.org/10.1145/564585.564601](https://doi.org/10.1145/564585.564601)
- Fischer, M. J., Lynch, N. A., & Paterson, M. S. (1985). Impossibility of Distributed Consensus with One Faulty Process. JACM. [doi.org/10.1145/3149.214121](https://doi.org/10.1145/3149.214121)
- Gray, J., & Cheriton, D. (1989). Leases: An Efficient Fault-Tolerant Mechanism for Distributed File Cache Consistency. SOSP.
- Apache Kafka documentation — producer idempotence, transactions, ISR, KRaft. [kafka.apache.org/documentation](https://kafka.apache.org/documentation/)
- Apache Flink documentation — exactly-once, checkpointing, two-phase commit. [flink.apache.org/docs](https://flink.apache.org/docs/)
- Debezium documentation — MySQL connector, GTID handling, snapshot modes. [debezium.io/documentation](https://debezium.io/documentation/)
- Apache Pulsar documentation — quorum protocols, subscription types, bookie quorum. [pulsar.apache.org/docs](https://pulsar.apache.org/docs/)
