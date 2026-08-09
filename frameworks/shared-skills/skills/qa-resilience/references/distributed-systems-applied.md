---
description: Distributed-systems primitives applied to QA resilience testing — Jepsen-style invariant checking, consistency test selection, split-brain detection, clock-skew fuzz tests, quorum reconfiguration safety, and idempotency soak tests.
last_verified: 2026-07-11
status: stable
---

# Distributed Systems Applied to QA Resilience

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Companion to [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md). Applies its 11 primitives to the concrete testing and validation work that sits inside qa-resilience: designing Jepsen-style invariant harnesses, selecting consistency tests by model, detecting split-brain in active-active deployments, fuzzing clock skew, validating quorum reconfiguration safety, and soak-testing idempotency under retries._

## Table of Contents

- [Why Distributed-Systems Theory for Resilience Testing](#why-distributed-systems-theory-for-resilience-testing)
- [Patterns](#patterns)
  - [P1 — Jepsen-Style Invariant Checking Under Partition](#p1--jepsen-style-invariant-checking-under-partition)
  - [P2 — Linearisability vs Sequential Consistency Test Selection](#p2--linearisability-vs-sequential-consistency-test-selection)
  - [P3 — Split-Brain Detection in Active-Active Deployments](#p3--split-brain-detection-in-active-active-deployments)
  - [P4 — Cross-Region Clock-Skew Fuzz Tests](#p4--cross-region-clock-skew-fuzz-tests)
  - [P5 — Quorum Reconfiguration Safety Tests](#p5--quorum-reconfiguration-safety-tests)
  - [P6 — Idempotency Validation Under Retries](#p6--idempotency-validation-under-retries)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Testing Only Happy-Path Replication](#a1--testing-only-happy-path-replication)
  - [A2 — No Partition-Mode Testing](#a2--no-partition-mode-testing)
  - [A3 — Skipping Clock-Skew Tests](#a3--skipping-clock-skew-tests)
  - [A4 — Asserting Strong Consistency in Eventually-Consistent Stores](#a4--asserting-strong-consistency-in-eventually-consistent-stores)
  - [A5 — Idempotency Tested Only at the Unit Level](#a5--idempotency-tested-only-at-the-unit-level)
- [Recipes](#recipes)
  - [R1 — Designing a Jepsen-Style Harness for a CRDT Store](#r1--designing-a-jepsen-style-harness-for-a-crdt-store)
  - [R2 — Asymmetric Partition Test Plan for a Leader-Elected Service](#r2--asymmetric-partition-test-plan-for-a-leader-elected-service)
  - [R3 — Idempotency Soak Test for a Payment Retry Path](#r3--idempotency-soak-test-for-a-payment-retry-path)
- [Cross-References](#cross-references)

---

## Why Distributed-Systems Theory for Resilience Testing

Distributed-system correctness failures are not visible on happy-path test suites. The same Cassandra cluster that passes unit tests and integration tests can serve stale reads on a partition — but only if W+R ≤ N, only if sloppy quorums are enabled, and only when two writes happen within the replication lag window. These conditions never appear in a happy-path suite.

The primitives in [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) define the invariants that need testing — and the conditions under which they break:

| Resilience test gap | Distributed-systems diagnosis |
|---|---|
| Replication tested only without partition | CAP (#1): partition is the condition under which C and A trade off; omitting it means the critical failure mode is never exercised |
| No linearisability check | Quorums (#9): W+R>N guarantees linearisability but only if sloppy quorums are disabled and the configuration is verified under load |
| Split-brain discovered in production | Leases and Fencing (#8): fencing tokens must be verified at the storage layer, not just in application logic |
| Timestamp-based conflict resolution assumed correct | Vector Clocks (#5): clock skew of 100–500 ms between nodes routinely produces wrong last-write-wins outcomes |
| Idempotency tested only for duplicate HTTP calls | Idempotency (#7): duplicate side effects arise from queue re-delivery, retry storms, and leader handover — not just HTTP retries |
| Quorum reconfiguration done in production without a safety test | Raft (#4): member changes require a joint consensus period; skipping tests causes split quorums |

Foundation primitives live in `../../foundations-distributed-systems/assets/templates/distributed-systems/`. Refer to them for protocol definitions; this file applies them.

---

## Patterns

### P1 — Jepsen-Style Invariant Checking Under Partition

**Primitive anchors**: [01-cap-pacelc](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md), [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md)

**The Jepsen methodology (Kingsbury, 2013–present).** A Jepsen-style test runs concurrent client operations against a distributed system while a nemesis process injects network partitions, node kills, and clock skews. After the test, a checker analyses the operation history to determine whether the system's advertised consistency model was violated.

**Core invariants to check per consistency model:**

| Model | Invariant to verify | Violation signature |
|---|---|---|
| Linearisability | Every operation appears to take effect atomically at some point between its invocation and completion; no read returns a value older than the latest write in real time | A read returns value v1 after a write of v2 has completed and been acknowledged |
| Sequential consistency | All operations are consistent with a single sequential order; that order respects each client's program order | Client A writes v1 then reads v2 (stale); Client B sees v2 before v1 in causal order |
| Read-your-writes | A client always reads values at least as new as its own writes | Client writes v2, immediately reads v1 (stale) |
| Monotonic reads | Once a client reads v2, it never reads a value older than v2 | Client reads v2, then reads v1 after a replica switch |

**History encoding.** Record each operation as a triple `(invoke, value, complete)`:

```python
# History entry format
{
  "type": "invoke" | "ok" | "fail" | "info",
  "process": <client_id>,
  "f": <operation_type>,   # "write" | "read" | "cas"
  "value": <value_or_None>
}

# Linearisability checker verifies:
# For every read r that returns v, there exists a write w of v such that:
#   w.complete < r.complete  AND  no other write of a different value w'
#   satisfies w.complete < w'.complete < r.complete
```

**Partition injection sequence for CAP validation:**

```
1. Start: all nodes healthy; run 10 operations per second for 30 seconds (baseline)
2. Partition: isolate the leader node (or one replica) using iptables
   iptables -A INPUT -s <node_ip> -j DROP
3. During partition: continue concurrent reads and writes from multiple clients
4. Heal: remove partition rules after 60 seconds
5. Post-heal: continue operations for 30 seconds (observe convergence)
6. Check: run the invariant checker on the full history
```

**What to assert.** The assertion depends on the system's documented consistency model:
- If the system claims linearisability (e.g. etcd, CockroachDB): assert zero linearisability violations.
- If the system claims eventual consistency (e.g. Cassandra default): assert eventual convergence (all replicas agree after partition heals), but permit stale reads during the partition window.
- If the system claims read-your-writes: assert no client reads a value older than its most recent acknowledged write.

---

### P2 — Linearisability vs Sequential Consistency Test Selection

**Primitive anchors**: [01-cap-pacelc](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md), [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md), [10-causal-consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)

**The selection problem.** Teams sometimes test for stronger consistency guarantees than the system provides (and see phantom failures) or weaker guarantees than their use case requires (and miss real bugs). The correct test is derived from the consistency model the data path actually needs, not the model the storage layer is theoretically capable of.

**Consistency model → test selection matrix:**

| Use case | Required model | Correct test | Common mistake |
|---|---|---|---|
| Payment balance read after write | Linearisability | Jepsen linearisability check with concurrent CAS operations | Testing read-your-writes (too weak) — misses cross-client stale reads |
| User profile update visible to same user | Read-your-writes | Session-sticky soak test: write then read on same session 1000× | Testing linearisability (too strong) — asserts cross-client ordering that the system doesn't need to provide |
| Event feed ordering | Causal consistency | Vector-clock ordering check: assert no event appears before its causal parent | Testing sequential consistency (too strong) — concurrent events from unrelated authors don't need a global order |
| Shopping cart (add only) | Eventual consistency (G-Set) | Partition test + convergence check: all replicas agree after heal | Testing linearisability (too strong) — will falsely fail during partition |

**Test selection procedure:**

1. Identify the consistency requirement for the data path (from the CAP/PACELC classification of the service boundary).
2. Select the checker that matches exactly that requirement.
3. Write the partition scenario that exercises the boundary: what happens to in-flight operations when the partition occurs?
4. Assert the correct invariant — not a stronger one.

**Linearisability test signature (register semantics):**

```python
# A register supports read, write, and CAS
# Linearisability: every history of read/write/CAS is consistent with
# some sequential interleaving where each operation is atomic

def check_linearisability(history):
    """
    Use the Wing & Gong algorithm or Knossos checker.
    For each read that returns v:
      - Verify there exists a write of v that completed before the read started
      - Verify no later write of v' ≠ v completed before the read started
    """
    ...
```

**Eventual consistency convergence check (simpler):**

```python
def check_eventual_convergence(node_states, timeout_seconds=30):
    """
    After partition heals, poll all replicas every 1 second for timeout_seconds.
    Assert all replicas return the same value within the window.
    """
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        values = [read_from_replica(node) for node in nodes]
        if len(set(values)) == 1:
            return True  # converged
        time.sleep(1)
    return False  # failed to converge within window
```

---

### P3 — Split-Brain Detection in Active-Active Deployments

**Primitive anchors**: [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md), [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md), [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md)

**Split-brain definition.** A split-brain occurs when two or more nodes simultaneously believe they hold a primary or leader role, or when two network partitions both accept writes that contradict each other. Split-brain is not a transient inconsistency — it is a correctness violation: without fencing tokens enforced at storage, the conflicting writes both persist.

**Detection test design.** A split-brain test must verify that the fencing mechanism actually prevents double writes — not just that two leaders cannot coexist simultaneously (which the consensus protocol prevents), but that a paused or slow leader cannot continue writing after its lease expires.

**Split-brain probe for an active-active write path:**

```
Setup:
  - 2 leader nodes (L1, L2); both active
  - Shared storage (PostgreSQL or etcd); fencing token enforced at storage

Test steps:
  1. Pause L1's GC-equivalent (or sleep the process) for 30 seconds
  2. Wait for lease expiry + election timeout (L2 acquires sole leadership)
  3. L2 writes value v2 with fencing token T=2
  4. Resume L1 (it believes it still holds the lease from T=1)
  5. L1 attempts to write value v1 with fencing token T=1

Assert:
  - Storage rejects L1's write (T=1 < max_seen_token T=2)
  - Only v2 is visible after the test
  - L1 receives a write rejection error and stops writing (self-demotion)

Failure signal: v1 and v2 are both committed → split-brain occurred → fencing not enforced
```

**Active-active detection via write trace analysis:**

For systems without explicit fencing tokens (e.g. multi-master databases using last-write-wins), split-brain detection requires comparing write histories:

```python
def detect_split_brain(write_log_region_a, write_log_region_b, key):
    """
    For a given key, compare the write sequences from two regions.
    Split-brain: both regions accepted a write for the same key in the same
    time window without the writes being causally ordered.
    """
    writes_a = [w for w in write_log_region_a if w["key"] == key]
    writes_b = [w for w in write_log_region_b if w["key"] == key]

    for wa in writes_a:
        for wb in writes_b:
            # Concurrent writes within clock_skew_tolerance of each other
            if abs(wa["timestamp"] - wb["timestamp"]) < clock_skew_tolerance_ms:
                if wa["value"] != wb["value"]:
                    return True, wa, wb  # split-brain detected
    return False, None, None
```

**Fencing token verification checklist:**

```
[ ] Fencing token is a monotonically increasing integer (etcd revision, ZooKeeper zxid)
[ ] Token is included in every write to downstream storage
[ ] Storage layer enforces token via conditional write (WHERE token >= last_seen)
[ ] Storage layer stores last_seen token per key (not per session)
[ ] Application handles write rejection with self-demotion (queries lease authority)
[ ] Test: inject pause long enough to expire lease; verify rejection fires
```

---

### P4 — Cross-Region Clock-Skew Fuzz Tests

**Primitive anchors**: [05-vector-clocks-lamport](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md), [10-causal-consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)

**The clock-skew problem.** Wall-clock timestamps are routinely used as conflict resolvers in multi-region systems (last-write-wins), as ordering signals in event logs, and as lease expiry checks. NTP synchronisation between nodes typically achieves ±100 ms accuracy; GPS-disciplined clocks (Google TrueTime) achieve ±7 ms. Any ordering mechanism that uses wall clocks without accounting for this skew is incorrect in a provable sense.

**Failure modes from clock skew:**

| Failure | Clock-skew cause | Test to catch it |
|---|---|---|
| LWW conflict resolver discards newer write | Two concurrent writes within the skew window; the one with the lower timestamp "wins" even if it was written later in causal order | Inject writes with timestamps 50 ms apart; assert the causally later write wins |
| Lease considered valid after expiry | Node's local clock runs slow; it reads lease expiry as T+5s when wall clock is T+6s | Advance node clock by skew amount; assert lease is rejected |
| Event log ordering wrong | Event A causally precedes event B; but A's timestamp > B's timestamp due to skew | Write A then B causally; read log; assert A appears before B |
| `AS OF SYSTEM TIME` stale read | Clock on read node is ahead; follower read returns data from the future | Use `tc` to skew one node's clock; verify no "future" reads are served |

**Clock-skew fuzz test procedure:**

```bash
# Introduce clock skew on one node using Linux tc + faketime
# Requires root; use in staging/test environments only

# Method 1: faketime (userspace — affects process only)
faketime -f '+0.15' python3 write_client.py  # advance clock by 150 ms

# Method 2: chrony offset injection (system-level — affects all processes on node)
chronyc makestep -100ms  # force clock 100 ms behind

# Method 3: tc netem for network delay that mimics clock skew effects
tc qdisc add dev eth0 root netem delay 100ms 50ms distribution normal
```

**Fuzz test assertions for LWW stores:**

```python
def test_lww_under_clock_skew(store, skew_ms=150):
    """
    Write value v1 from node with clock +skew_ms ahead.
    Write value v2 from node with normal clock 100 ms later (wall time).
    v2 is causally later but its timestamp may be earlier.
    Assert: store returns v2 (the causally later write).
    """
    # Setup: node A is clock-fast by skew_ms
    ts_v1 = time_on_fast_node()         # e.g. 1000150 ms
    store.write(key="balance", value=100, timestamp=ts_v1)

    time.sleep(0.1)  # 100 ms later in wall time

    ts_v2 = time_on_normal_node()       # e.g. 1000100 ms (lower due to skew)
    store.write(key="balance", value=200, timestamp=ts_v2)

    result = store.read("balance")
    # LWW by timestamp: returns v1 (100) — WRONG, causally v2 (200) should win
    # LWW by vector clock: returns v2 (200) — CORRECT
    assert result == 200, f"Clock skew caused stale LWW result: {result}"
```

**Recommendation.** For any conflict resolver that uses wall-clock timestamps, add a clock-skew fuzz test with a skew of at least 500 ms (conservative NTP drift). If the test reveals incorrect ordering, replace wall-clock LWW with vector-clock ordering (primitive #5) or hybrid logical clocks (HLC).

---

### P5 — Quorum Reconfiguration Safety Tests

**Primitive anchors**: [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md), [03-paxos](../../foundations-distributed-systems/assets/templates/distributed-systems/03-paxos.md), [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md)

**The reconfiguration risk.** Adding or removing a node from a Raft-based cluster (etcd, CockroachDB, Kafka with KRaft) requires a joint consensus phase: both the old configuration and the new configuration must each form a quorum for any decision during the transition. If the implementation skips the joint consensus phase (or if an operator performs the change in a way that bypasses it), the cluster can split into two independent quorums that both believe they have majority — a correctness violation.

**Safety tests for quorum reconfiguration:**

```
Test 1: Single-member addition safety
  Setup: 3-node Raft cluster (N=3, quorum=2)
  Action: Add node-4 during active write workload
  Assert:
    - No writes are lost during the reconfiguration
    - The cluster log is fully consistent before and after
    - No two nodes simultaneously believe they are leader
    - Write throughput recovers to baseline within 30 seconds

Test 2: Single-member removal safety (minority)
  Setup: 5-node Raft cluster (N=5, quorum=3)
  Action: Remove node-5 (non-leader) during active write workload
  Assert:
    - No writes are lost
    - Cluster continues to accept writes with N=4, quorum=3
    - Removed node stops accepting writes within 10 seconds

Test 3: Leader removal during reconfiguration
  Setup: 3-node Raft cluster
  Action: Remove the current leader; trigger re-election
  Assert:
    - A new leader is elected within the election timeout window
    - No writes committed by the old leader are lost
    - No writes are committed by two different leaders simultaneously (split-brain)
    - Write latency spike < 5× during leadership transition

Test 4: Minority partition during reconfiguration
  Setup: 5-node cluster in joint-consensus state (adding node-6, old={1,2,3,4,5}, new={1,2,3,4,5,6})
  Action: Partition node-5 and node-6 from the rest during joint consensus
  Assert:
    - Partitioned nodes cannot form a quorum in either old or new config
    - Majority partition continues to make progress
    - After partition heals, partitioned nodes catch up from the leader
```

**NWR configuration test for Cassandra/DynamoDB:**

```python
def test_quorum_reconfiguration_safety(session, replication_factor_old, replication_factor_new):
    """
    Change replication factor from N=3 to N=5 on a live keyspace.
    Assert: reads return consistent results during and after the change.
    """
    # Write 100 known values before reconfiguration
    for i in range(100):
        session.execute("INSERT INTO kv (key, value) VALUES (%s, %s)", (f"key-{i}", i))

    # Trigger reconfiguration
    session.execute(f"ALTER KEYSPACE test WITH REPLICATION = {{'class': 'NetworkTopologyStrategy', 'dc1': {replication_factor_new}}}")

    # Run nodetool repair to propagate to new replicas
    subprocess.run(["nodetool", "repair", "test"])

    # Verify: all 100 values are readable with QUORUM consistency
    for i in range(100):
        row = session.execute("SELECT value FROM kv WHERE key = %s", (f"key-{i}",),
                             execution_profile="quorum").one()
        assert row.value == i, f"key-{i}: expected {i}, got {row.value}"
```

---

### P6 — Idempotency Validation Under Retries

**Primitive anchors**: [07-idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md), [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md)

**Why unit tests are not enough.** An idempotency key implementation that passes unit tests can still fail under realistic retry conditions:
- The deduplication store is unavailable at the moment of the second retry (Redis restart, leader election gap).
- The check-and-execute is not atomic: a concurrent retry arrives between the "check" and the "store."
- The idempotency key TTL expires during the client's retry window.
- A queue consumer processes the same message twice due to a visibility timeout race.

Idempotency validation under retries tests the full stack — transport, deduplication store, and application — under the failure conditions where duplicate delivery actually occurs.

**Retry scenario taxonomy:**

```
Scenario 1: HTTP client retry on timeout
  Client sends POST /payments; server receives and processes the request
  but the response is lost in transit (TCP timeout).
  Client retries with the same Idempotency-Key.
  Assert: exactly 1 charge, 2 identical responses.

Scenario 2: Queue message re-delivery
  SQS/Kafka consumer processes message and commits offset.
  Between processing and offset commit, the consumer crashes.
  On restart, the broker re-delivers the message (visibility timeout expires).
  Assert: exactly 1 side effect per message.

Scenario 3: Deduplicate store unavailable during retry
  First request succeeds; deduplication store is restarted before the retry arrives.
  Retry arrives; deduplication store is back but may have lost recent writes.
  Assert: exactly 1 side effect (depends on store durability — test both durable and non-durable configurations).

Scenario 4: Concurrent retries (retry storm)
  100 concurrent clients all send the same Idempotency-Key simultaneously.
  Assert: exactly 1 side effect, 100 identical responses (not 100 side effects).
```

**Concurrent-retry atomicity test:**

```python
import threading, requests, collections

def test_concurrent_idempotency(endpoint, idempotency_key, n_concurrent=100):
    """
    Send n_concurrent requests with the same key concurrently.
    Assert: exactly 1 side effect (charge, insert, etc.) and n_concurrent identical responses.
    """
    results = []
    errors = []

    def send_request():
        try:
            resp = requests.post(
                endpoint,
                json={"amount": 100, "currency": "GBP"},
                headers={"Idempotency-Key": idempotency_key},
                timeout=10
            )
            results.append(resp.json())
        except Exception as e:
            errors.append(str(e))

    threads = [threading.Thread(target=send_request) for _ in range(n_concurrent)]
    for t in threads: t.start()
    for t in threads: t.join()

    assert len(errors) == 0, f"Errors during concurrent test: {errors}"

    # All responses should be identical
    unique_responses = set(str(r) for r in results)
    assert len(unique_responses) == 1, f"Non-identical responses: {unique_responses}"

    # Exactly 1 charge in the payments ledger
    charges = query_charges_for_key(idempotency_key)
    assert len(charges) == 1, f"Expected 1 charge, found {len(charges)}"
```

**Queue re-delivery soak test:**

```python
def test_queue_redelivery_idempotency(queue_client, processor, n_messages=1000, redelivery_rate=0.1):
    """
    Send n_messages to the queue; randomly re-deliver redelivery_rate fraction.
    Assert: processor executes each logical message exactly once.
    """
    message_ids = [str(uuid.uuid4()) for _ in range(n_messages)]
    sent_counts = collections.Counter()
    processed_counts = collections.Counter()

    # Enqueue with some duplicates
    for msg_id in message_ids:
        queue_client.send({"id": msg_id, "payload": f"data-{msg_id}"})
        sent_counts[msg_id] += 1
        if random.random() < redelivery_rate:
            queue_client.send({"id": msg_id, "payload": f"data-{msg_id}"})  # duplicate
            sent_counts[msg_id] += 1

    # Process all messages
    processor.consume_all(timeout=60)

    # Assert: each message processed exactly once
    for msg_id in message_ids:
        count = processor.get_processed_count(msg_id)
        assert count == 1, f"Message {msg_id} processed {count} times (sent {sent_counts[msg_id]})"
```

---

## Anti-Patterns

### A1 — Testing Only Happy-Path Replication

**Symptom**: The integration test suite writes data to the primary and reads it back. All tests pass. The team considers replication "tested."

**Why it fails**: CAP theorem (primitive #1) states that consistency and availability trade off only during a network partition. A test without a partition never exercises the trade-off. The system's actual behaviour during a partition — whether it blocks writes, serves stale reads, or violates consistency — remains unknown until a real partition occurs in production.

**Fix**: Add a partition test for every data path that has a consistency SLO. Use tc netem or a Chaos Mesh NetworkPolicy to inject a partition; then check the invariant defined by the system's consistency model (P1). At minimum: can the system still serve reads during a partition? Does it serve stale reads or return an error? Is the SLO definition compatible with the observed behaviour?

---

### A2 — No Partition-Mode Testing

**Symptom**: The team runs load tests and chaos experiments that kill nodes (pod deletion, process kill) but never partition the network. Node kill tests exercise restart recovery; they do not exercise split-brain, quorum loss, or consistency violations under network partition.

**Why it fails**: Node kill restarts the process and re-joins the cluster; from the consensus protocol's perspective, it is a normal recovery. Network partition isolates the node while it remains running — the partition is what triggers the CAP trade-off. Without partition tests, the full class of CAP-induced failures is untested.

**Fix**: Add network partition injections (not just node kills) to the chaos test matrix. Test at minimum: leader partition (the leader is isolated), minority partition (less than quorum isolated), and symmetric partition (cluster split into two equal halves). For each, assert the expected quorum behaviour and consistency guarantees.

---

### A3 — Skipping Clock-Skew Tests

**Symptom**: The team uses timestamp-based last-write-wins conflict resolution, relies on `CURRENT_TIMESTAMP` for ordering, or uses wall-clock lease expiry checks. No tests are run with artificially skewed clocks.

**Why it fails**: NTP synchronisation has ±100 ms accuracy under normal conditions and can drift by seconds during network instability. Any system that uses wall-clock timestamps for ordering or conflict resolution will produce incorrect results when the skew exceeds the conflict window. These bugs are among the hardest to reproduce in production because they require specific timing coincidences.

**Fix**: Add clock-skew fuzz tests (P4) with a minimum skew of 500 ms. For LWW conflict resolvers: assert that the causally later write always wins regardless of timestamp. For lease expiry: assert that a process whose clock runs slow does not hold a lease past its actual expiry. If the tests fail, replace wall-clock ordering with vector clocks (primitive #5) or hybrid logical clocks.

---

### A4 — Asserting Strong Consistency in Eventually-Consistent Stores

**Symptom**: The integration test for a Cassandra or DynamoDB table asserts that a write is immediately readable from any node. Tests occasionally flap in CI. The team treats the flaps as infrastructure noise rather than test-design errors.

**Why it fails**: Eventual consistency (primitive #1, CAP AP/EL) explicitly does not guarantee that a write is immediately visible on all replicas. Asserting immediate cross-replica visibility on an eventually-consistent store is testing the wrong invariant — the test is designed to fail intermittently by construction.

**Fix**: Align the test assertion with the system's actual consistency model. For eventually-consistent stores:
- Test read-from-the-same-node-you-wrote-to (read-your-writes via sticky routing).
- Test eventual convergence with a poll-and-wait pattern (check_eventual_convergence from P2).
- Reserve linearisability assertions (no stale reads, ever) for data paths that use strong consistency reads explicitly (DynamoDB consistent reads, Cassandra QUORUM with W+R>N).

---

### A5 — Idempotency Tested Only at the Unit Level

**Symptom**: The idempotency key logic is unit-tested by calling the handler twice with the same key in the same process. The test passes. The production system still occasionally double-charges customers after a network timeout.

**Why it fails**: Unit tests cannot exercise the conditions under which production duplicate delivery occurs: concurrent retries from multiple client instances, message re-delivery after a consumer crash, or a race between the check and the execute when the deduplication store has a brief unavailability. These require integration-level and soak-level tests (P6).

**Fix**: Add at minimum: a concurrent-retry test (100 parallel requests, same key, assert 1 side effect), a queue re-delivery test with a random re-delivery rate, and a chaos test that restarts the deduplication store between the first request and the retry. Gate promotion on all three passing.

---

## Recipes

### R1 — Designing a Jepsen-Style Harness for a CRDT Store

**Objective**: Build a test harness that verifies a CRDT-backed store (e.g. a Redis CRDT module or Riak) preserves its convergence guarantee under concurrent writes and network partitions, and that the merge operation produces the correct result.

**Primitive stack**: CRDTs (#6) + CAP/PACELC (#1) + Vector Clocks (#5) + Quorums (#9)

**Step 1: Choose the CRDT type and define the invariant.**

```
CRDT type: PN-Counter (supports both increment and decrement)
Use case: distributed user session count (concurrent increments across regions)

Invariant:
  After all operations are applied and all partitions are healed:
  final_value = Σ(increments) - Σ(decrements)
  (regardless of the order in which replicas receive the operations)

Pre-conditions:
  - All writes are eventually delivered to all replicas (gossip convergence)
  - Merge operation is commutative and associative (PN-Counter guarantee)
  - No operation is dropped during partition (at-least-once delivery)
```

**Step 2: Design the workload.**

```
Clients: 10 concurrent clients, each performing 100 random operations
  (70% increment, 30% decrement) over 60 seconds

Nemesis: 
  - T=10s: partition replica-2 from replica-1 and replica-3 (minority partition)
  - T=40s: heal the partition
  - T=50s: kill and restart replica-3 (node failure + rejoin)

Expected behaviour:
  - During partition: clients on either side can still write (AP system)
  - After heal: all replicas converge to the same value
  - After replica-3 rejoin: replica-3 catches up via gossip or anti-entropy
```

**Step 3: Implement the history recorder and checker.**

```python
import threading, dataclasses, time

@dataclasses.dataclass
class Operation:
    client_id: int
    op_type: str          # "increment" | "decrement" | "read"
    value: int            # delta for increment/decrement; observed value for read
    timestamp: float
    succeeded: bool

history: list[Operation] = []
history_lock = threading.Lock()

def record_op(client_id, op_type, value, succeeded):
    with history_lock:
        history.append(Operation(client_id, op_type, value, time.time(), succeeded))

def check_crdt_convergence(history, replica_states):
    """
    After all operations: compute expected final value from successful ops.
    Assert all replicas report the same value.
    """
    expected = 0
    for op in history:
        if op.succeeded:
            if op.op_type == "increment":
                expected += op.value
            elif op.op_type == "decrement":
                expected -= op.value

    for replica_id, state in replica_states.items():
        actual = state.read_counter()
        assert actual == expected, \
            f"Replica {replica_id}: expected {expected}, got {actual}"
```

**Step 4: Run the harness and verify.**

```python
def run_crdt_jepsen_test():
    # Start clients
    threads = [threading.Thread(target=client_worker, args=(i,)) for i in range(10)]
    for t in threads: t.start()

    # Start nemesis (partition at T=10, heal at T=40, kill at T=50)
    nemesis = threading.Thread(target=nemesis_worker)
    nemesis.start()

    # Wait for all clients to finish
    for t in threads: t.join()
    nemesis.join()

    # Wait for convergence (gossip propagation)
    time.sleep(30)

    # Check invariant
    replica_states = {i: get_replica_state(i) for i in range(3)}
    check_crdt_convergence(history, replica_states)
    print("CRDT convergence test: PASS")
```

**Step 5: Assert vector-clock ordering where applicable.**

If the store tracks vector clocks on operations:

```python
def check_vector_clock_ordering(history):
    """
    For any two operations A and B where A causally precedes B (B was issued
    after observing A's response), assert VC(A) < VC(B) in the replica logs.
    """
    for op_a, op_b in causal_pairs(history):
        vc_a = get_vector_clock_for_op(op_a)
        vc_b = get_vector_clock_for_op(op_b)
        assert vector_clock_dominates(vc_b, vc_a), \
            f"Causal ordering violated: VC({op_b}) does not dominate VC({op_a})"
```

---

### R2 — Asymmetric Partition Test Plan for a Leader-Elected Service

**Objective**: Design a test plan that verifies a leader-elected service (e.g. a scheduled job coordinator using etcd leases) handles asymmetric network partitions correctly — specifically, that the old leader cannot write after losing quorum even if it believes it still holds the lease.

**Primitive stack**: Leases and Fencing (#8) + Raft (#4) + CAP (#1)

**Step 1: Define the asymmetric partition scenario.**

```
Asymmetric partition: node A can reach node B, but node B cannot reach node A.
(Common in real networks: a firewall rule drops traffic in one direction only.)

Setup:
  Cluster: L1 (leader), F1 (follower), F2 (follower)
  Asymmetric partition: F1 and F2 cannot reach L1; L1 can reach F1 and F2 (one-way)

Effect on Raft:
  L1 can send heartbeats to F1 and F2 (its heartbeats arrive)
  F1 and F2 cannot send responses back to L1 (responses are dropped)
  L1's heartbeats are not acknowledged; it cannot form a quorum for writes
  F1 and F2 elect a new leader (they can reach each other)
  L1 may continue to believe it is leader (it has not heard that a new leader exists)
```

**Step 2: Inject the partition.**

```bash
# On F1 and F2: drop all traffic from L1 (asymmetric)
iptables -A INPUT -s <L1_IP> -j DROP

# L1's heartbeats are dropped by F1 and F2
# F1 and F2 see L1 as unresponsive; trigger election
# L1 does not see the election (it can still reach F1 and F2 in theory, but responses are dropped)
```

**Step 3: Assert the expected Raft behaviour.**

```
Assert 1: F1 and F2 elect a new leader within 2× election timeout
  → Measure: time from partition injection to new leader elected
  → Target: < 10 seconds (etcd default election timeout = 5 s)

Assert 2: L1 cannot commit new writes
  → L1 needs acknowledgement from a majority (F1 or F2) to commit
  → With dropped responses, L1's write proposals time out
  → Assert: all write attempts from L1 return a timeout or "not leader" error

Assert 3: New leader (F1 or F2) commits writes correctly
  → Assert: writes to the new leader succeed and are replicated
  → Assert: no writes from L1 appear in the log after the partition

Assert 4: Fencing token prevents L1 stale writes after partition heals
  → Heal partition; L1 discovers it is no longer leader
  → Any pending writes from L1 are rejected by the storage layer (T_L1 < T_new_leader)
  → Assert: L1 self-demotes and stops writing within 5 seconds of partition heal
```

**Step 4: Test the storage-layer fencing.**

```python
def test_stale_leader_fencing(storage, old_leader_token, new_leader_token):
    """
    Simulate the stale-leader write that should be rejected.
    old_leader_token < new_leader_token (old leader's fencing token is stale).
    """
    # New leader has already written with its token
    storage.write("state", "v_new", fencing_token=new_leader_token)

    # Old leader (partitioned, paused, now resumed) attempts to write
    result = storage.write("state", "v_old", fencing_token=old_leader_token)

    assert result.rejected, f"Expected rejection of stale write; got {result}"
    assert storage.read("state") == "v_new", "Stale write overwrote valid leader write"
```

**Step 5: Measure and gate.**

```
Gate: asymmetric partition test must pass before promoting to production
Metrics to capture:
  - Time to elect new leader after asymmetric partition injection
  - Number of writes committed by old leader after partition (must be 0)
  - Time for old leader to self-demote after partition heal (target: < 5 s)
  - Data loss: any writes committed by new leader must be present after heal
```

---

### R3 — Idempotency Soak Test for a Payment Retry Path

**Objective**: Validate that the payment service's idempotency key mechanism prevents double charges under sustained retry load, including failure modes that only appear at scale: concurrent retries, deduplication store unavailability, and queue re-delivery.

**Primitive stack**: Idempotency (#7) + Quorums (#9) + CAP (#1)

**Step 1: Map the retry surfaces in the payment path.**

```
Retry surface inventory:
  1. HTTP client retry: client retries POST /charges on timeout or 5xx
     Idempotency key: Idempotency-Key header (client-generated UUID)
     Deduplication store: Redis SETNX with 24-hour TTL

  2. Payment webhook retry: payment provider retries webhook delivery
     Idempotency key: webhook event_id (provider-generated, immutable)
     Deduplication store: PostgreSQL unique index on event_id

  3. SQS message re-delivery: visibility timeout expires before consumer commits
     Idempotency key: SQS message deduplication ID (content-based)
     Deduplication store: DynamoDB conditional write on message_id

  4. Internal job queue retry: background processor retries failed tasks
     Idempotency key: job_id (stable across retries)
     Deduplication store: PostgreSQL job_status with optimistic locking
```

**Step 2: Define the soak test parameters.**

```
Duration: 30 minutes
Load: 500 payment requests per minute (baseline)
Retry injection: 20% of all requests are retried 1–3 times with the same Idempotency-Key
Failure injection (chaos):
  - Redis restart at T=5 min (deduplication store unavailability)
  - SQS visibility timeout set to 1 s for 2 minutes at T=15 min (forced re-delivery)
  - Network partition on payment-service replica-2 at T=22 min (partition test)

Expected results:
  - Zero double charges throughout the 30-minute window
  - All idempotent retries return the same response as the original request
  - After Redis restart: retries that arrive before the store recovers return
    an appropriate error (409 or 503) rather than executing a duplicate charge
```

**Step 3: Implement the soak test runner.**

```python
class PaymentSoakTest:
    def __init__(self, endpoint, duration_minutes=30):
        self.endpoint = endpoint
        self.duration = duration_minutes * 60
        self.issued_keys = {}       # idempotency_key → expected_charge_id
        self.charges = []
        self.errors = []

    def run(self):
        start = time.time()
        while time.time() - start < self.duration:
            key = str(uuid.uuid4())
            amount = random.randint(100, 10000)  # pence

            # First attempt
            resp = self._charge(key, amount)
            if resp.ok:
                self.issued_keys[key] = resp.json()["charge_id"]

            # Random retry (20% of requests)
            if random.random() < 0.2:
                retry_resp = self._charge(key, amount)
                if retry_resp.ok:
                    assert retry_resp.json()["charge_id"] == self.issued_keys.get(key), \
                        f"Duplicate charge on retry: {retry_resp.json()}"

            time.sleep(60 / 500)  # 500 rpm

    def _charge(self, key, amount):
        return requests.post(
            f"{self.endpoint}/charges",
            json={"amount": amount, "currency": "GBP"},
            headers={"Idempotency-Key": key},
            timeout=5
        )

    def assert_no_double_charges(self):
        ledger_charges = query_all_charges()
        key_counts = collections.Counter(c["idempotency_key"] for c in ledger_charges)
        double_charged = {k: v for k, v in key_counts.items() if v > 1}
        assert not double_charged, f"Double charges detected: {double_charged}"
```

**Step 4: Run chaos scenarios during the soak.**

```python
def chaos_worker(start_time):
    # T=5 min: restart Redis
    while time.time() - start_time < 300: time.sleep(1)
    subprocess.run(["docker", "restart", "redis-dedup"])

    # T=15 min: force SQS re-delivery by setting visibility timeout to 1s
    while time.time() - start_time < 900: time.sleep(1)
    sqs.set_queue_attributes(QueueUrl=PAYMENT_QUEUE, Attributes={"VisibilityTimeout": "1"})
    time.sleep(120)  # 2 min of forced re-delivery
    sqs.set_queue_attributes(QueueUrl=PAYMENT_QUEUE, Attributes={"VisibilityTimeout": "30"})

    # T=22 min: partition one payment-service replica
    while time.time() - start_time < 1320: time.sleep(1)
    inject_partition("payment-service-2")
    time.sleep(300)  # 5 min partition
    heal_partition("payment-service-2")
```

**Step 5: Gate criteria.**

```
PASS:
  [ ] Zero double charges in the ledger at end of soak
  [ ] Zero 5xx responses during Redis availability window (retries return 409 or 503 only)
  [ ] Queue re-delivery window: no duplicate side effects in ledger
  [ ] Partition window: error rate < 1% (circuit breaker activates; no stale writes)
  [ ] All idempotency key TTLs are intact at end of soak (no premature expiry)

FAIL:
  [ ] Any duplicate charge_id in the ledger
  [ ] Any charge_id that appears with a different amount (key collision)
  [ ] Idempotency key store returns stale or incorrect deduplication state
```

---

## Cross-References

### Foundation

All primitives cited by number in this file are defined with inputs, outputs, failure modes, and worked examples in:

- [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) — canonical source for primitives #1–#11

### Sibling References in This Skill

- [idempotency-key-design.md](idempotency-key-design.md) — implementation patterns for idempotency keys; complements P6 (idempotency validation) and R3 (payment soak test)
- [chaos-engineering-guide.md](chaos-engineering-guide.md) — tooling for partition injection and node kill; complements P1 (Jepsen harness) and R2 (partition test plan)
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) — circuit breaker behaviour under partition; relevant to P2 (consistency test selection) and R2 step 3
- [retry-patterns.md](retry-patterns.md) — retry configuration and storm prevention; complements P6 (idempotency under retries) and R3 (retry surface inventory)
- [resilience-telemetry.md](resilience-telemetry.md) — SLI instrumentation for the metrics referenced in P1 (Jepsen invariant checks) and the soak test gate criteria in R3

_Last verified: 2026-07-11. Re-derived all arithmetic (Jepsen invariants, CRDT convergence math, split-brain fencing-token logic) during the 2026-07-11 audit; no corrections were required._
