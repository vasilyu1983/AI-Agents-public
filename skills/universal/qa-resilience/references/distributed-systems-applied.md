---
description: Distributed-systems primitives applied to QA resilience testing — Jepsen-style invariant checking, consistency test selection, split-brain detection, clock-skew fuzz tests, quorum reconfiguration safety, and idempotency soak tests. Link adapter to foundations-distributed-systems.
status: stable
---

# Distributed Systems Applied to QA Resilience

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

_Link adapter to [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md). The foundation owns the theory (CAP/PACELC, consensus, clocks, CRDTs, quorums, fencing); this file keeps only what is specific to resilience testing: which invariants to check, how to inject the fault, what to assert, and the test pitfalls. Overload, retry storms, and metastable failure are owned by this skill: [cascading-failure-prevention.md](cascading-failure-prevention.md), [load-shedding-backpressure.md](load-shedding-backpressure.md), [retry-patterns.md](retry-patterns.md)._

## Table of Contents

- [Theory Pointers](#theory-pointers)
- [Resilience Test Gaps → Primitive](#resilience-test-gaps--primitive)
- [Patterns](#patterns)
  - [P1 — Jepsen-Style Invariant Checking Under Partition](#p1--jepsen-style-invariant-checking-under-partition)
  - [P2 — Consistency Test Selection](#p2--consistency-test-selection)
  - [P3 — Split-Brain Detection](#p3--split-brain-detection)
  - [P4 — Clock-Skew Fuzz Tests](#p4--clock-skew-fuzz-tests)
  - [P5 — Quorum Reconfiguration Safety Tests](#p5--quorum-reconfiguration-safety-tests)
  - [P6 — Idempotency Validation Under Retries](#p6--idempotency-validation-under-retries)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
  - [R1 — Jepsen-Style Harness for a CRDT Store](#r1--jepsen-style-harness-for-a-crdt-store)
  - [R2 — Asymmetric Partition Test for a Leader-Elected Service](#r2--asymmetric-partition-test-for-a-leader-elected-service)
  - [R3 — Idempotency Soak Test for a Payment Retry Path](#r3--idempotency-soak-test-for-a-payment-retry-path)
- [Cross-References](#cross-references)

---

## Theory Pointers

| Concept | Canonical owner |
|---|---|
| CAP / PACELC | [01-cap-pacelc.md](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md) |
| FLP | [02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md) |
| Raft (elections, joint consensus, PreVote/CheckQuorum, read paths) | [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md) |
| Vector clocks / Lamport | [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md) |
| CRDT merge semantics | [06-crdts.md](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md) |
| Idempotency / receiver contract | [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md), [execution-histories.md](../../foundations-distributed-systems/references/execution-histories.md) |
| Leases and fencing tokens | [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md) |
| Quorum intersection, sloppy quorums, read repair | [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md) |
| Causal consistency | [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md) |
| Linearizability vs serializability; Jepsen/Elle, DST evidence tiers | [formal-theory-map.md](../../foundations-distributed-systems/references/formal-theory-map.md) |
| Split-brain prevention, exactly-once receiver recipe | [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md) |
| Gray failure, hybrid logical clocks, clock uncertainty | [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md) |
| Formal verification tool choice | [foundations-formal-methods](../../foundations-formal-methods/SKILL.md) |

## Resilience Test Gaps → Primitive

| Resilience test gap | Why it hides bugs | Owner |
|---|---|---|
| Replication tested only without partition | The C/A trade-off only exists during a partition | 01-cap-pacelc |
| No consistency checker | `W + R > N` gives quorum intersection, **not** linearizability by itself (needs versioning, read/write repair, fixed membership) | 09-quorums |
| Split-brain found in production | Fencing must be enforced at storage, not in app logic | 08-leases-fencing |
| Timestamp LWW assumed correct | Clock skew reorders writes inside the skew window | 05-vector-clocks-lamport |
| Idempotency tested only for duplicate HTTP calls | Duplicates also come from queue redelivery, consumer crash before commit, leader handover | 07-idempotency |
| Membership change untested | Raft membership changes need joint consensus or one-server-at-a-time changes; either path can be implemented wrongly | 04-raft |

---

## Patterns

### P1 — Jepsen-Style Invariant Checking Under Partition

A Jepsen-style test runs concurrent client operations while a nemesis injects partitions, kills, and clock skew, then a checker analyses the recorded history against the system's **advertised** model. Do not hand-roll a linearizability checker: the check is a search for a valid linearization (NP-complete in general) — use Knossos or Porcupine for registers, Elle for transactional isolation. See [formal-theory-map.md § Empirical Falsification](../../foundations-distributed-systems/references/formal-theory-map.md#empirical-falsification-complement-not-substitute) for what black-box checking can and cannot establish.

**History record per operation** (Jepsen convention): `{type: invoke|ok|fail|info, process, f: read|write|cas, value}`. `info` means indeterminate (timeout) — the checker must treat it as possibly applied; recording timeouts as `fail` produces false passes.

**Partition sequence:**

```
1. Baseline: all nodes healthy; ~10 ops/s for 30 s
2. Partition: isolate the leader (or one replica), e.g. iptables -A INPUT -s <peer_ip> -j DROP
3. During partition: concurrent reads and writes from clients on both sides
4. Heal after 60 s
5. Post-heal: 30 s more operations (observe convergence)
6. Run the checker on the full history
```

**What to assert** (depends on the documented model):
- Claims linearizability (e.g. etcd, CockroachDB): zero linearizability anomalies.
- Claims eventual consistency (e.g. Cassandra at ONE): convergence after heal; stale reads during partition are allowed.
- Claims read-your-writes: no client reads older than its own last acknowledged write.

### P2 — Consistency Test Selection

Test the model the **data path needs**, not the strongest one the store can offer. Too strong → phantom failures; too weak → missed bugs.

| Use case | Required model | Correct test | Common mistake |
|---|---|---|---|
| Payment balance read after write | Linearizable | Checker over concurrent read/write/CAS history (Knossos/Porcupine) | Testing read-your-writes only — misses cross-client stale reads |
| User profile visible to same user | Read-your-writes | Session-sticky soak: write then read on the same session, 1000× | Asserting linearizability — fails on legitimately stale cross-client reads |
| Event feed ordering | Causal | Assert no event is visible before its causal parent | Asserting a global order across unrelated authors |
| Add-only cart | Eventual (G-Set) | Partition + convergence check after heal | Asserting linearizability — fails during partition by design |

**Convergence check (eventual stores):**

```python
def check_eventual_convergence(nodes, timeout_seconds=30):
    """After heal, poll all replicas every 1 s; pass if all agree within the window."""
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        if len({read_from_replica(n) for n in nodes}) == 1:
            return True
        time.sleep(1)
    return False
```

Convergence also requires quiescence: stop writes before polling, or the check flaps.

### P3 — Split-Brain Detection

Split-brain = two nodes act as leader/primary at once, or two partitions accept conflicting writes. The test must show a **paused or slow old leader cannot write after its lease expires** — consensus alone does not stop a resumed stale leader. Theory: [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md); prevention recipe: [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md).

**Stale-leader probe:**

```
Setup: leader L1 + standby L2; lease authority (etcd/ZooKeeper); fencing enforced at storage
1. SIGSTOP L1 (or inject a long GC pause) for longer than lease TTL + election timeout
2. L2 acquires the lease with token T=2 and writes v2
3. SIGCONT L1 (it still believes it holds T=1); L1 writes v1 with T=1
Assert: storage rejects T=1 (< max seen 2); only v2 visible; L1 self-demotes on rejection
Fail signal: both v1 and v2 committed → fencing not enforced
```

**Active-active without fencing (multi-master LWW):** compare per-key write logs across regions; flag conflicting values written by both regions within the clock-skew tolerance window. This is a heuristic — it misses conflicts beyond the tolerance and needs version vectors for a precise answer.

**Fencing checklist:**

```
[ ] Token is monotonic (etcd revision / lease-scoped revision, ZooKeeper zxid)
[ ] Token travels with every downstream write
[ ] Storage accepts a write only if token >= last_seen_token for that resource (conditional write)
[ ] last_seen_token is stored per resource, not per session
[ ] Rejection triggers self-demotion
[ ] Test pause exceeds lease TTL; rejection verified
```

### P4 — Clock-Skew Fuzz Tests

Wall clocks are used for LWW conflict resolution, log ordering, and lease expiry; any of these is wrong when skew exceeds the conflict window. Clock uncertainty bounds and hybrid logical clocks: [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md). Spanner's TrueTime reports its uncertainty ε explicitly (Corbett et al., OSDI 2012: typically 1–7 ms); NTP-synchronised fleets vary widely by environment — measure your own offset distribution rather than assuming one.

| Failure | Skew cause | Test |
|---|---|---|
| LWW discards the causally later write | Earlier write stamped by a fast clock | Write v1 on a fast-clock node; a client that has read v1 writes v2 on a normal node; assert v2 wins |
| Lease held past expiry | Holder's clock runs slow | Slow the holder's clock; assert its writes are fenced after real expiry |
| Log ordering inverted | Causally earlier event has later timestamp | Write A then (after reading A) B; assert A precedes B |
| Node serves reads beyond max clock offset | Offset exceeds the database's configured bound (e.g. CockroachDB max offset) | Skew one node past the bound; assert the node refuses/self-terminates rather than serving inconsistent reads |

**Injection methods** (staging/test only):

```bash
# Per-process: libfaketime (check offset syntax against your libfaketime version)
faketime -f '+2s' python3 write_client.py

# Per-node: disable time sync on a test VM, then step the clock
sudo systemctl stop chronyd && sudo date -s '+2 seconds'

# NOT clock skew: tc netem adds network delay; use it for latency/timeout tests, not skew tests
tc qdisc add dev eth0 root netem delay 100ms 50ms distribution normal
```

**LWW assertion:**

```python
def test_lww_under_clock_skew(store, skew_s=2.0):
    # Node A clock is +skew_s ahead
    store.write_via(node="A", key="balance", value=100)          # stamped T+skew
    assert store.read_via(node="B", key="balance") == 100          # client observes v1 ...
    store.write_via(node="B", key="balance", value=200)          # ... then writes v2 (causally later, lower stamp)
    assert store.read("balance") == 200, "wall-clock LWW discarded the causally later write"
```

If it fails, replace wall-clock LWW with version vectors or HLC; do not "fix" it by shrinking the skew in the test. Choose the skew from your measured worst-case offset plus margin, not from a fixed number.

### P5 — Quorum Reconfiguration Safety Tests

Membership change is where Raft implementations break (joint consensus vs single-server change, learners, removed-node disruption, PreVote/CheckQuorum): theory in [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md). A majority of N tolerates f = ⌊(N−1)/2⌋ failures (N=3→1, 4→1, 5→2).

```
Test 1: Add a member under write load
  3-node cluster (quorum 2) → add node-4 (quorum becomes 3; still tolerates only 1 failure)
  Prefer adding as a learner/non-voter first, promote after catch-up
  Assert: no acknowledged write lost; log consistent; one leader per term;
          throughput back to baseline within 30 s (example target)

Test 2: Remove a non-leader member
  5-node (quorum 3) → remove node-5 → N=4, quorum 3
  Assert: no acknowledged write lost; writes continue; removed node stops
          participating (and cannot disrupt elections) within 10 s (example target)

Test 3: Remove the leader
  3-node cluster; remove current leader
  Assert: new leader within the election-timeout window; no committed write lost;
          no two leaders commit in the same term

Test 4: Partition during joint consensus
  5 → 6 nodes (C_old={1..5}, C_new={1..6}); partition {5,6} from {1..4}
  Assert: minority side cannot commit in either config; majority side progresses;
          partitioned nodes catch up after heal
```

**Replication-factor change (Cassandra):** after `ALTER KEYSPACE … RF 3→5`, reads at QUORUM (now 3 of 5) can miss data until `nodetool repair` completes — assert all known keys are readable at QUORUM **after** repair, and separately record the failure/stale rate **during** the window rather than asserting zero.

### P6 — Idempotency Validation Under Retries

Unit tests miss the failure conditions that create duplicates: dedup store unavailable (restart, failover), non-atomic check-then-execute, key TTL shorter than the retry window, queue visibility-timeout races. Delivery is at-least-once in all of these; the property under test is **one effect per logical operation**. Receiver contract: [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md), [execution-histories.md](../../foundations-distributed-systems/references/execution-histories.md); key design: [idempotency-key-design.md](idempotency-key-design.md).

**Scenario taxonomy:**

```
S1 HTTP retry after lost response: same Idempotency-Key → 1 charge, identical responses
S2 Consumer crash between effect and offset commit → redelivery → 1 effect per message
S3 Dedup store restarted between attempt and retry → 1 effect (test durable and non-durable store configs)
S4 100 concurrent requests, same key → 1 effect, 100 identical responses (or 409 in-progress, per contract)
```

**Concurrent-retry atomicity test:**

```python
import threading, requests

def test_concurrent_idempotency(endpoint, key, n=100):
    results, errors = [], []
    def send():
        try:
            r = requests.post(endpoint, json={"amount": 100, "currency": "GBP"},
                              headers={"Idempotency-Key": key}, timeout=10)
            results.append((r.status_code, r.text))
        except Exception as e:
            errors.append(str(e))
    threads = [threading.Thread(target=send) for _ in range(n)]
    for t in threads: t.start()
    for t in threads: t.join()
    assert not errors, errors
    assert len({body for code, body in results if code < 300}) == 1, "non-identical success responses"
    assert len(query_charges_for_key(key)) == 1, "duplicate side effect"
```

**Queue redelivery soak:** enqueue N logical messages, re-send a random 10% as duplicates, consume all, assert each logical message's **effect** is applied once (`processor.get_effect_count(msg_id) == 1`). Count effects in the sink, not handler invocations — invocations are expected to exceed N.

---

## Anti-Patterns

**A1 — Happy-path replication only.** Write-then-read on a healthy cluster never exercises the partition trade-off. Fix: a partition test (P1) for every data path with a consistency SLO; record whether the system blocks, errors, or serves stale data, and check it matches the SLO.

**A2 — Node kills but no partitions.** A killed node restarts and rejoins through normal recovery; a partitioned node keeps running and can act on stale state. Fix: add leader-isolation, minority-partition, symmetric-split (even N) and asymmetric (one-way) partitions to the chaos matrix ([chaos-tooling-recipes.md](chaos-tooling-recipes.md)). Partial/gray failures (slow, not dead) are covered in [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md).

**A3 — No clock-skew tests.** Wall-clock LWW, `CURRENT_TIMESTAMP` ordering, or wall-clock lease checks go untested until a rare timing coincidence in production. Fix: P4, with skew taken from measured worst-case offset.

**A4 — Asserting strong consistency on an eventual store.** A test that reads any replica immediately after a write on Cassandra at ONE, or a DynamoDB eventually consistent read, flaps by construction. Fix: test read-your-writes via sticky routing, convergence via poll-and-wait (P2), and reserve linearizability assertions for paths that request it (DynamoDB strongly consistent reads; Cassandra QUORUM/QUORUM with read repair and no sloppy quorums — still verify with a checker, see [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md)).

**A5 — Idempotency tested only in-process.** Calling the handler twice in one process cannot reproduce concurrent retries, redelivery after consumer crash, or dedup-store failover. Fix: S1–S4 from P6 as integration/soak tests; gate promotion on them.

**A6 — Claiming "exactly-once" from a durable journal or retries.** Retries and durable workflow journals give at-least-once execution; external side effects are once only if the receiver deduplicates. Test the effect count at the sink.

---

## Recipes

### R1 — Jepsen-Style Harness for a CRDT Store

**Objective:** verify a CRDT-backed store converges under concurrent writes, partitions, and node restart, and that the merge result equals the expected value. CRDT semantics: [06-crdts.md](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md).

**Invariant (PN-Counter):** after quiescence and heal, every replica reads `Σ(acknowledged increments) − Σ(acknowledged decrements)`. Operations that timed out (`info`) are indeterminate — the check must accept any value in `[expected_ok, expected_ok + Σ indeterminate deltas]` per sign, or the test flaps.

**Workload and nemesis:**

```
Clients: 10, 100 ops each over 60 s (70% increment, 30% decrement)
T=10s  partition replica-2 from {1,3}
T=40s  heal
T=50s  kill and restart replica-3
Expect: both sides keep accepting writes; all replicas converge after heal;
        replica-3 catches up via anti-entropy after restart
```

**Checker:**

```python
from dataclasses import dataclass

@dataclass
class Op:
    client: int
    kind: str      # "increment" | "decrement" | "read"
    delta: int
    status: str    # "ok" | "fail" | "info"

def check_crdt_convergence(history, replicas):
    sign = {"increment": 1, "decrement": -1}
    ok = sum(sign[o.kind] * o.delta for o in history if o.status == "ok" and o.kind in sign)
    pos = sum(o.delta for o in history if o.status == "info" and o.kind == "increment")
    neg = sum(o.delta for o in history if o.status == "info" and o.kind == "decrement")
    values = {rid: r.read_counter() for rid, r in replicas.items()}
    assert len(set(values.values())) == 1, f"replicas diverged: {values}"
    v = next(iter(values.values()))
    assert ok - neg <= v <= ok + pos, f"value {v} outside [{ok - neg}, {ok + pos}]"
```

Run: start clients and nemesis, join, stop writes, wait for anti-entropy (poll with P2's convergence check rather than a fixed sleep), then check. If the store exposes version vectors, additionally assert that for every causally ordered pair (B issued after observing A), `VV(B)` dominates `VV(A)` — definitions in [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md).

### R2 — Asymmetric Partition Test for a Leader-Elected Service

**Objective:** a leader-elected service (e.g. a job coordinator on etcd leases) must regain a working leader after a one-way partition, and the old leader must not write after losing quorum. Raft behaviour (CheckQuorum, PreVote): [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md).

**Scenario — leader can send, cannot receive.** L1 (leader), F1, F2. Drop inbound traffic **on L1** from the followers:

```bash
# on L1
iptables -A INPUT -s <F1_IP> -j DROP
iptables -A INPUT -s <F2_IP> -j DROP
```

L1's heartbeats still reach F1/F2, so their election timers keep resetting; L1 never receives acks, so it cannot commit.
- **Without CheckQuorum:** L1 stays leader indefinitely, followers never elect → write unavailability for the whole partition. This is a liveness bug the test must surface.
- **With CheckQuorum** (leader steps down after an election timeout without hearing from a quorum): L1 steps down, heartbeats stop, F1/F2 elect a new leader. etcd's server enables CheckQuorum; verify for your version and for any other Raft library.

Run the mirror case too (drop on F1/F2 inbound from L1): followers stop hearing heartbeats and elect; L1 keeps sending and, without CheckQuorum, still believes it is leader.

**Assertions:**

```
A1 New leader elected within ~2 election timeouts (etcd default election timeout 1000 ms,
   heartbeat 100 ms — check your configured values)
A2 L1 commits nothing after partition start (proposals time out or return "not leader")
A3 Writes to the new leader commit and replicate; no L1 entries after partition in the log
A4 After heal, any stale L1 write to downstream storage is rejected by fencing
   (T_L1 < T_new); L1 self-demotes within 5 s (example target)
```

**Storage fencing check:**

```python
def test_stale_leader_fencing(storage, old_token, new_token):
    storage.write("state", "v_new", fencing_token=new_token)
    result = storage.write("state", "v_old", fencing_token=old_token)
    assert result.rejected
    assert storage.read("state") == "v_new"
```

**Gate metrics:** time to new leader; writes committed by old leader after partition (must be 0); old-leader self-demotion time after heal; acknowledged writes lost (must be 0).

### R3 — Idempotency Soak Test for a Payment Retry Path

**Objective:** no double charges under sustained retries plus dedup-store restart, forced queue redelivery, and a replica partition.

**Retry surfaces to inventory:**

```
1. HTTP client retry      key: Idempotency-Key (client UUID)     store: Redis SET NX + TTL
2. Provider webhook retry key: provider event_id                  store: PostgreSQL unique index
3. Queue redelivery       key: message/business id                store: DynamoDB conditional write
   (SQS FIFO deduplication ID only dedups within a 5-minute interval; standard queues do not dedup)
4. Internal job retry     key: job_id stable across retries       store: job_status + optimistic lock
```

**Soak parameters (example values — size to your traffic):** 30 min at 500 requests/min; 20% of requests retried 1–3× with the same key; Redis restart at T=5 min; SQS visibility timeout forced to 1 s for 2 min at T=15 min; partition payment-service replica-2 at T=22 min for 5 min.

**Runner core:**

```python
def soak(endpoint, duration_s=1800, rpm=500):
    issued = {}
    start = time.time()
    while time.time() - start < duration_s:
        key, amount = str(uuid.uuid4()), random.randint(100, 10000)  # pence
        r = charge(endpoint, key, amount)
        if r.ok:
            issued[key] = r.json()["charge_id"]
        if random.random() < 0.2:
            rr = charge(endpoint, key, amount)
            if rr.ok and key in issued:
                assert rr.json()["charge_id"] == issued[key], "retry produced a new charge"
        time.sleep(60 / rpm)
    return issued

def assert_no_double_charges():
    counts = collections.Counter(c["idempotency_key"] for c in query_all_charges())
    assert not {k: v for k, v in counts.items() if v > 1}
```

Drive the chaos schedule from a separate thread (`docker restart redis-dedup`; `sqs.set_queue_attributes(... VisibilityTimeout="1")` then restore; `inject_partition`/`heal_partition`).

**Gate:**

```
PASS
[ ] Zero duplicate charges per idempotency key in the ledger
[ ] While the dedup store is unavailable, retries fail closed (409 in-progress or 503) —
    never a second charge; outside that window, no 5xx
[ ] Redelivery window: no duplicate effects in the ledger
[ ] Partition window: error rate within the SLO budget; no stale writes
[ ] No key expired before the client retry window ended
FAIL
[ ] Any duplicate charge; any charge_id reused with a different amount; stale dedup state served
```

If retries during the incident overload the service instead of merely duplicating, that is a retry-storm / metastable problem — use [cascading-failure-prevention.md](cascading-failure-prevention.md) and [retry-patterns.md](retry-patterns.md).

---

## Cross-References

### Foundation

- [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) — canonical source for primitives #1–#11
- [patterns-scenarios-traps.md](../../foundations-distributed-systems/references/patterns-scenarios-traps.md) — payment webhook receiver and multi-region write scenarios
- [primitives-overview.md](../../foundations-distributed-systems/references/primitives-overview.md) — primitive index and anti-patterns by domain

### Sibling References in This Skill

- [idempotency-key-design.md](idempotency-key-design.md) — key design for P6 / R3
- [chaos-engineering-guide.md](chaos-engineering-guide.md), [chaos-tooling-recipes.md](chaos-tooling-recipes.md) — partition and kill injection for P1 / R2
- [cascading-failure-prevention.md](cascading-failure-prevention.md) — metastable failure, retry storms (owned here)
- [load-shedding-backpressure.md](load-shedding-backpressure.md), [retry-patterns.md](retry-patterns.md), [deadlines-hedging.md](deadlines-hedging.md) — overload controls
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) — breaker behaviour during R3's partition window
- [resilience-telemetry.md](resilience-telemetry.md) — SLIs for the gate metrics

