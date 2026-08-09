---
description: Distributed-systems primitives applied to software architecture decisions — CAP-conscious service boundaries, consensus algorithm selection, idempotency at API surfaces, leases-with-fencing for leader-elected jobs, quorum sizing for multi-region storage, ADR template for consistency vs. latency, and eventual-consistency UX design.
last_verified: 2026-05-02
status: stable
---

# Distributed Systems Applied to Architecture Decisions

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


_Companion to [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md). Applies its 11 primitives to the concrete decisions that arise in software architecture work: service boundary placement, storage tier selection, consensus algorithm choice, API idempotency design, leader-election infrastructure, quorum configuration, and eventual-consistency UX._

## Table of Contents

- [Why Distributed-Systems Theory in Architecture](#why-distributed-systems-theory-in-architecture)
- [Patterns](#patterns)
  - [P1 — CAP-Conscious Service Boundary Design](#p1--cap-conscious-service-boundary-design)
  - [P3/P4 — Choosing a Consensus Algorithm for Control Planes](#p3p4--choosing-a-consensus-algorithm-for-control-planes)
  - [P7 — Idempotency Keys at API Boundaries](#p7--idempotency-keys-at-api-boundaries)
  - [P8 — Leases with Fencing for Leader-Elected Jobs](#p8--leases-with-fencing-for-leader-elected-jobs)
  - [P9 — Quorum Sizing in Multi-Region Storage](#p9--quorum-sizing-in-multi-region-storage)
  - [P10 — Causal Consistency for Collaborative and Social Features](#p10--causal-consistency-for-collaborative-and-social-features)
  - [P6/P5 — CRDTs and Vector Clocks for Offline-First and Sync Architectures](#p6p5--crdts-and-vector-clocks-for-offline-first-and-sync-architectures)
- [Anti-Patterns](#anti-patterns)
  - [A1 — Using "CAP" as a Static Design-Time Pick](#a1--using-cap-as-a-static-design-time-pick)
  - [A2 — Applying Paxos/Raft to Every Coordination Problem](#a2--applying-paxosraft-to-every-coordination-problem)
  - [A3 — Idempotency Keys Generated Server-Side](#a3--idempotency-keys-generated-server-side)
  - [A4 — Lease Without Fencing Token Enforcement at Storage](#a4--lease-without-fencing-token-enforcement-at-storage)
  - [A5 — Majority Quorum in an Even-N Cluster](#a5--majority-quorum-in-an-even-n-cluster)
  - [A6 — Eventual Consistency Without UX Accommodation](#a6--eventual-consistency-without-ux-accommodation)
- [Recipes](#recipes)
  - [R1 — ADR Template: Consistency vs. Latency Tradeoff](#r1--adr-template-consistency-vs-latency-tradeoff)
  - [R2 — Idempotency Key Design Checklist for APIs](#r2--idempotency-key-design-checklist-for-apis)
  - [R3 — Quorum Configuration Worksheet for Multi-Region Storage](#r3--quorum-configuration-worksheet-for-multi-region-storage)
- [Cross-References](#cross-references)

---

## Why Distributed-Systems Theory in Architecture

Distributed system failures follow repeatable patterns. The same theoretical structures that underpin CAP, Raft, and quorum design appear again and again in everyday architecture decisions — and the mistakes recur for the same reasons:

| Architecture failure | Distributed-systems diagnosis |
|---|---|
| Two services share a database and experience phantom inconsistency under load | CAP (#1) — both services claim ownership of the same consistency boundary; partition exposes the implicit CP assumption |
| etcd used as a job queue; throughput collapses | Raft (#4) — every enqueue triggers a consensus round; Raft latency × queue depth exceeds worker capacity |
| Payment API charges twice after client timeout | Idempotency (#7) — no idempotency key; at-least-once delivery creates duplicate charges |
| Scheduled job runs on two hosts simultaneously after restart | Leases and fencing (#8) — leader election uses a lease but the storage layer does not enforce fencing tokens |
| Cassandra QUORUM reads return stale balances | Quorums (#9) — W + R ≤ N because W=1 was set for write latency; the read quorum and write quorum no longer overlap |
| Social feed shows a reply before the original post in some regions | Causal consistency (#10) — multi-region replication is eventually consistent without causal tracking; the dependency is not enforced |
| Offline mobile edit conflicts silently overwrote server state on sync | CRDTs / vector clocks (#6, #5) — last-write-wins timestamp merge discarded the client's intent |

The primitives in [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) are the formal vocabulary for diagnosing and fixing these failures. The patterns below show how to apply them at the architecture level.

---

## Patterns

### P1 — CAP-Conscious Service Boundary Design

**Primitives**: CAP/PACELC (#1)

The most consequential place to apply CAP is at service boundary design, not just storage selection. A service boundary defines a consistency domain: everything inside the boundary can be coordinated atomically; everything outside must tolerate partition-time divergence.

**Design rule**: Draw service boundaries to enclose strong-consistency requirements. Separate boundaries wherever eventual consistency is acceptable.

**PACELC framing for boundary placement**:

- **EC (consistent under partition, higher latency without partition)**: Enclose related entities that require linearisable reads — e.g., payment ledger, inventory reservation, seat allocation. Use a single-owner write path (single-region primary, synchronous replication to standby).
- **EL (available under partition, lower latency without partition)**: Separate read-heavy views where staleness is tolerable — e.g., product catalogue, user profile snapshot, analytics aggregates. Serve from a nearby replica without coordination.

**Domain example — e-commerce service decomposition**:

An order service and an inventory service are candidates for extraction from a monolith. The critical question is: "Does `PlaceOrder` need a linearisable read of `inventory.reserved_quantity`?"

- If yes: keep `PlaceOrder` and `ReserveInventory` inside the same consistency boundary, either as a single service or as a synchronous call within a transaction boundary. Do not split until a distributed saga or reservation-plus-confirm flow is implemented.
- If no (optimistic over-sell is acceptable): separate the services. Accept that `inventory.reserved_quantity` may be stale at the moment of order placement; handle over-sell as a business exception.

The CAP classification of the storage tier should match the consistency requirement of the service boundary, not the other way around.

**Failure mode avoided**: Splitting services first and adding consistency mechanisms later. The cost of retrofitting two-phase commit or saga compensation into an already-decomposed system is an order of magnitude higher than designing the boundary correctly upfront.

---

### P3/P4 — Choosing a Consensus Algorithm for Control Planes

**Primitives**: Paxos (#3), Raft (#4)

Consensus algorithms — Paxos, Raft, and their variants — guarantee that a cluster agrees on a single value (or a sequence of values) even when a minority of nodes fail. The architecture decision is not "implement Paxos vs. Raft" but "which managed consensus service is appropriate, and what workload can safely be placed on it?"

**Decision matrix**:

| Workload | Consensus requirement | Recommended approach |
|---|---|---|
| Leader election for scheduled jobs | Single agreed leader at any time | etcd leases (Raft-based) via `clientv3.NewSession` |
| Distributed lock for critical section | Mutual exclusion with liveness | etcd + fencing token (see P8) |
| Configuration store for control plane | Consistent reads of small key-value pairs | etcd or ZooKeeper; avoid large values (>1 MB) |
| High-throughput event stream ordering | Total order of events across producers | Kafka partition leader (Raft since KIP-595); not general Paxos |
| Multi-region primary election | Consensus across geographically distributed nodes | CockroachDB or Spanner (Paxos with multi-Paxos leader); latency cost is real |
| Application-level coordinator state | Workflow step coordination | Temporal.io (uses Raft internally); do not re-implement consensus |

**Key sizing constraint**: Raft-based systems (etcd, CockroachDB) write every state change to a consensus log before responding. At 10 ms round-trip latency, a single Raft group can commit roughly 80–100 operations per second. **Never route high-throughput workloads (job queues, event streams, cache invalidations) through a Raft-based system.** Route only low-rate, high-importance coordination operations (leader grants, config updates, lock acquisitions).

**FLP impossibility** (#2) implication: No consensus algorithm can guarantee both safety and liveness in an asynchronous network with even one faulty process. In practice, etcd and Raft achieve liveness by assuming eventually synchronous networks (bounded message delay in the common case). When network partitions exceed the election timeout, the cluster sacrifices availability to preserve safety. Design control-plane consumers to tolerate brief unavailability of the consensus service during network events.

---

### P7 — Idempotency Keys at API Boundaries

**Primitive**: Idempotency (#7)

Every API endpoint that mutates state and may be retried by a client or proxy is a candidate for idempotency key enforcement. This applies to synchronous HTTP calls, message queue consumers, and webhook receivers.

**Architectural contract**:

1. **Client generates the key before the first attempt** — a UUID or ULID scoped to the operation type and the initiating actor (e.g., `order-42-pay-attempt-1`). Never let the server generate the key: if the server crashes after generating but before responding, the client retries with a new server-generated key and the deduplication misses.

2. **Server maintains a deduplicate store** — a persistent record of `(idempotency_key → result)` with a TTL. Suitable stores: Redis (`SET NX` + `EXPIRE`), PostgreSQL (`INSERT … ON CONFLICT DO NOTHING`), DynamoDB (conditional expression `attribute_not_exists`).

3. **Check-and-execute must be atomic** — a non-atomic check allows a concurrent retry to slip through between the "check" and the "store." Use a database transaction or a Lua script in Redis.

4. **Return the stored result on duplicate** — do not re-execute; return the original response including the original idempotency-key header in the response.

**API surface design**:

```
POST /payments
Idempotency-Key: <client-generated UUID>

# On first request: execute charge, store key → response
# On retry with same key: return stored response, no new charge
# On retry with different key: execute charge (new operation)
```

**Idempotency key scope**: Scope keys per operation type and per account to prevent cross-user collisions. A key space of `{resource_type}/{actor_id}/{client_nonce}` provides sufficient isolation without requiring a global key registry.

**At-least-once → exactly-once illusion**: Pair idempotency keys with at-least-once delivery guarantees at the transport layer (HTTP retries with `Retry-After`, SQS with visibility timeout, Kafka with `acks=all`). The combination produces the illusion of exactly-once semantics without requiring distributed transactions.

---

### P8 — Leases with Fencing for Leader-Elected Jobs

**Primitive**: Leases and Fencing Tokens (#8)

Any job that runs on exactly one host at a time — a scheduled data pipeline, a subscription renewal processor, a cache warmer — requires leader election with fencing. A lease alone is not sufficient: a paused or slow process may not know its lease has expired.

**Correct architecture**:

```
1. Job acquires lease from etcd/ZooKeeper (gets fencing token T=42).
2. Job performs work; includes T=42 in every write to downstream storage.
3. Downstream storage rejects writes where token < max_seen_token.
4. If job pauses (GC, slow network) and lease expires:
   a. Lease authority grants new lease + token T=43 to standby.
   b. Original job resumes with T=42.
   c. Storage rejects writes (42 < 43).
   d. Job sees rejection, queries lease authority, recognises demotion, stops.
```

**Lease duration sizing**:

- Minimum lease duration: `2 × max_clock_skew + 1 × max_GC_pause`. For a JVM workload with stop-the-world GC, allow at least 20–30 seconds. etcd default session TTL is 60 seconds — reasonable for most jobs.
- Do not set lease duration shorter than the maximum expected pause. A JVM GC pause of 10 seconds on a 5-second lease triggers unnecessary failovers.

**Storage fencing implementation**:

The fencing token must be enforced at the storage layer, not just checked in application code. Application-level checks are bypassed by crashes between the check and the write. Enforce at:

- **PostgreSQL**: include `WHERE fencing_token = $current AND $current >= last_seen_token` in the `UPDATE`; store `last_seen_token` in the target row.
- **S3 / object storage**: use `If-Match: <etag>` for conditional writes; the ETag serves as a version fence.
- **Redis**: use Lua scripting to check and write atomically in a single round-trip.

**Common mistake**: Using ZooKeeper/etcd's distributed lock without wiring the fencing token into the write path. The lock prevents two nodes from believing they hold the lease simultaneously — but not from having a paused node resume and write after its lease expires if storage does not enforce the token.

---

### P9 — Quorum Sizing in Multi-Region Storage

**Primitive**: Quorums / NWR (#9)

Multi-region storage clusters require explicit quorum sizing decisions. The default configuration of most managed databases (Cassandra, DynamoDB global tables, CockroachDB multi-region) does not automatically satisfy a given consistency SLO; quorum parameters must be chosen deliberately.

**NWR sizing decision tree**:

```
What is the consistency requirement?
  ├─ Linearisable reads (financial balances, seat reservations, lock state)
  │   → W + R > N. Example: N=3, W=2, R=2. Tolerates 1 region failure.
  │
  ├─ Read-your-writes (user profile updates visible to own session)
  │   → Sticky routing to one replica, OR W + R > N on that replica's group.
  │
  ├─ Monotonic reads (event feed, time-ordered log)
  │   → Route to the same replica per session (sticky), OR W=majority, R=1 (can tolerate stale)
  │
  └─ Eventually consistent (product catalogue, analytics snapshot)
      → W=1, R=1. Fast writes and reads; accept stale data.
```

**Multi-region tail latency tradeoff**: With N=3 spread across three AWS regions (us-east-1, eu-west-1, ap-southeast-1), W=2 means a write must cross at least one inter-region hop (50–150 ms). For write-latency-sensitive workloads, consider regional leaders with async replication (`W=1` in the local region for EC, with a background sync to the other regions). Pair with conflict resolution (CRDT or last-write-wins with vector clocks) if concurrent cross-region writes are possible.

**Sloppy quorums in managed databases**: DynamoDB global tables and Cassandra with sloppy quorums enabled will accept writes to any available node during a partition, then propagate via "hinted handoff." This improves availability but breaks the `W + R > N` consistency guarantee. Disable sloppy quorums (or use strongly consistent reads in DynamoDB) when the data is financially sensitive or drives downstream reservations.

---

### P10 — Causal Consistency for Collaborative and Social Features

**Primitive**: Causal Consistency (#10)

Eventual consistency produces causal anomalies — a reply visible before its parent post, a deleted comment re-appearing after an undo, a read returning a stale state after the client just wrote. These anomalies are not just cosmetic; in collaborative tools and social feeds they erode user trust and drive re-loads and confusion.

**Architecture choices by anomaly class**:

| Anomaly | Root cause | Fix |
|---|---|---|
| Reply before post | Multi-region replication without causal ordering | COPS / causal+ consistency; carry dependency vectors on writes |
| Client write not visible on re-read | Replica switch between write and read | Sticky sessions OR causal token routing: client carries max-seen version vector |
| Notification about deleted item | Notification service replicated async without dependency tracking | Route notifications through the same consistency boundary as the object store |
| Comment counter inconsistent with comment list | Denormalised counter updated via separate async path | CRDT counter (#6) OR read the count from the canonical list at read time |

**Causal token pattern for read-your-writes**:

1. Write response includes a version token `{replica_id: "r1", seq: 42}`.
2. Client attaches the token to subsequent reads: `X-Causal-Token: r1:42`.
3. Routing layer directs the read to a replica that has applied at least sequence 42 on r1, or holds the request until the target replica catches up.
4. Client sees its own write on the next read, regardless of which replica serves it.

This pattern is implemented in MongoDB (read-concern `"majority"` + session tokens), DynamoDB (strongly consistent reads), and CockroachDB (follower reads with `AS OF SYSTEM TIME`).

---

### P6/P5 — CRDTs and Vector Clocks for Offline-First and Sync Architectures

**Primitives**: CRDTs (#6), Vector Clocks / Lamport Timestamps (#5)

Offline-first applications (mobile, desktop, field-ops tools) must merge divergent local state with the server when reconnecting. Last-write-wins timestamp merge silently discards intent and produces incorrect results for non-idempotent operations (counter increments, list appends, presence toggles).

**CRDT selection by data type**:

| Data | CRDT | Notes |
|---|---|---|
| Shopping cart (add only) | G-Set | Cannot remove; use 2P-Set if removal needed |
| Inventory count | PN-Counter | Per-replica increment + decrement; merge by summing per-replica max |
| Collaborative text | RGA or YATA | Used by Yjs and Automerge; preserves user intent on concurrent edits |
| Presence / live cursors | LWW-Register per user | Each user owns their register; no conflicts |
| Feature-flag override per user | LWW-Register | Monotone timestamp; last-writer rule is correct for flag state |
| Settings / config | OR-Set (observed-remove) | Handles add-remove-add correctly; avoids zombie elements |

**Vector clock use in sync protocols**: When CRDTs are not applicable (structured records with business invariants), use vector clocks to detect divergence and surface explicit conflicts rather than silently merging:

1. Each write includes the vector clock of the state it was based on.
2. On merge: if vector clocks are comparable (one dominates), apply the later version. If concurrent (neither dominates), surface as a conflict for user resolution or apply a deterministic merge policy.
3. Never use wall-clock timestamps as the sole conflict resolver for non-financial data: clock skew of 100–500 ms is common between mobile devices and servers.

---

## Anti-Patterns

### A1 — Using "CAP" as a Static Design-Time Pick

**Symptom**: The architecture document states "we are a CP system" or "we are AP" as a global property, applied uniformly to all data and all operations.

**Why it fails**: CAP is conditional on a partition occurring. Under normal operation, PACELC governs: the choice is between latency (serve from a nearby replica) and consistency (wait for coordination). Treating CAP as a static property causes teams to over-provision coordination mechanisms on paths that could be EL without consequence, and to under-protect paths that genuinely need EC guarantees.

**Fix**: Apply CAP/PACELC per service boundary and per operation type. Map each high-value write path to a CAP classification. Accept that different parts of the system have different classifications — the product catalogue is PA/EL; the payment ledger is PC/EC.

---

### A2 — Applying Paxos/Raft to Every Coordination Problem

**Symptom**: The team routes job scheduling, cache invalidation, rate-limit counters, and event routing through etcd or ZooKeeper because those systems are "strongly consistent."

**Why it fails**: Raft-based systems linearise every operation through a quorum write. At 10 ms inter-replica latency, a three-node etcd cluster handles roughly 100 writes/second per key. Routing a 50,000 events/minute job queue through etcd saturates the cluster within minutes. FLP impossibility (#2) means the cluster must also sacrifice availability during network instability to preserve safety.

**Fix**: Reserve consensus systems for low-rate, high-importance coordination: leader election, lock acquisition, distributed configuration. Route high-throughput workloads through systems designed for throughput (Kafka for event streams, Redis for rate-limit counters, SQS for job queues). Use consensus only at the boundaries where leader identity or mutual exclusion is genuinely required. For cluster-wide notifications and membership updates, use epidemic (gossip) broadcast protocols (#11) — they scale sub-linearly in message cost and tolerate node churn without a consensus round.

---

### A3 — Idempotency Keys Generated Server-Side

**Symptom**: On a `POST /charges` endpoint, the server generates a UUID at request receipt and uses it as the idempotency key. On client retry (network timeout), the server generates a new UUID — the deduplicate store never matches.

**Why it fails**: If the server generates the key after receiving the request but before responding, and then crashes, the client retries with no key. The server generates a new key. The duplicate is not detected. Double processing occurs.

**Fix**: Require the client to generate and supply the idempotency key before the first request. Document the key format and TTL in the API contract. Return a `409 Conflict` for attempts to use the same key with a different request body. Treat the idempotency key as part of the API contract, not an implementation detail.

---

### A4 — Lease Without Fencing Token Enforcement at Storage

**Symptom**: The team implements distributed leader election with an etcd lease. The elected leader writes to PostgreSQL. There is no fencing token — the application checks the lease before writing, but the check and the write are not atomic relative to lease expiry.

**Why it fails**: The gap between the lease check and the write is a split-brain window. A paused or slow process can check the lease, see it as valid, pause for 20 seconds (GC, network hiccup), then write — after its lease has expired and a new leader has already started writing. Without the storage layer rejecting the stale write, both writes succeed; the database now contains interleaved writes from two leaders.

**Fix**: Pass the fencing token (etcd revision number, ZooKeeper zxid) into every downstream write. Enforce the token at the storage layer with a conditional write (`WHERE fencing_token >= $current`). Do not rely on application-level lease checks alone.

---

### A5 — Majority Quorum in an Even-N Cluster

**Symptom**: A Cassandra cluster is deployed with N=4 per datacenter, W=3 (majority), R=3. The team expects to tolerate one node failure.

**Why it fails**: With N=4, a majority quorum is `floor(4/2) + 1 = 3`. The cluster can tolerate `N − W = 1` write failure and `N − R = 1` read failure. That is no better than N=3 with W=2, R=2 — and it costs an extra node. Worse, a two-node failure (network partition splitting N=4 into 2+2) blocks all majority-quorum operations. An odd-N cluster (N=3) has a clear majority partition (2 nodes) that can continue operating; an even-N cluster risks a symmetric split.

**Fix**: Use odd replication factors (N=3, N=5) for quorum-based replication. For N=3: tolerate one failure with W=2, R=2. For N=5: tolerate two failures with W=3, R=3. Reserve even N only for specific topologies (two active datacenters plus a tiebreaker, where the tiebreaker makes the effective quorum odd).

---

### A6 — Eventual Consistency Without UX Accommodation

**Symptom**: The frontend displays stale data after a user action. The team considers this "correct" because the storage is "eventually consistent." Users see their submitted form reverting to old values, or see a deleted item reappear for a few seconds.

**Why it fails**: Eventual consistency (#10) is a storage-level contract, not a UX contract. Users have a causal expectation: actions they take should be visible to them immediately. Violating read-your-writes is a UX regression regardless of theoretical correctness.

**Fix**: Apply one or more of the following patterns:

- **Optimistic UI update**: Apply the change immediately in the client's local state before the server confirms. Revert on error.
- **Causal token routing**: Pass the write's version token back in the response; subsequent reads route only to replicas that have applied that version (see Pattern P10).
- **Write-read sticky session**: Route the user's reads to the same replica that received their writes for the duration of the session.
- **Hide the stale state**: Show a "saving…" or "pending" indicator rather than the old value until the read-your-writes guarantee is satisfied.

---

## Recipes

### R1 — ADR Template: Consistency vs. Latency Tradeoff

**Goal**: Produce an ADR whose consistency/latency tradeoff is explicit, testable, and re-evaluable when requirements change.

**When to use**: Any data-path decision that affects whether reads may return stale values, whether writes may be rejected during a partition, or whether cross-service transactions are needed.

**Template**:

```markdown
## ADR-NNN: Consistency Model for [Service / Data Domain]

### Status
Proposed | Accepted | Superseded

### Context
[Describe the data involved, the operations that mutate it, and the
operations that read it. State the current failure mode or the
constraint that makes a consistency decision necessary.]

### CAP/PACELC Classification

| Dimension        | Choice       | Rationale                          |
|------------------|--------------|------------------------------------|
| Partition: C or A | C / A       | [What happens during a partition?] |
| Normal: L or C   | L / C        | [Accept stale reads for lower latency?] |
| PACELC label     | PC/EC or PA/EL or PA/EC | [Composite classification] |

### Options Considered

**Option A: [Name]**
- Storage: [e.g., PostgreSQL synchronous replica]
- Partition behaviour: [e.g., writes block if replica unreachable]
- Normal-operation latency: [e.g., +8 ms per write for sync ack]
- Stale-read window: [e.g., 0 ms — always consistent]

**Option B: [Name]**
- Storage: [e.g., Cassandra W=1, R=1]
- Partition behaviour: [e.g., writes accepted, may diverge]
- Normal-operation latency: [e.g., 2 ms per write]
- Stale-read window: [e.g., up to 30 seconds during normal operation]

### Decision

[State the chosen option, the consistency guarantee it provides, and
the business reason the guarantee is or is not required.]

### Consistency SLO

| Operation       | Guarantee            | Acceptable Stale Window |
|-----------------|----------------------|-------------------------|
| [Write operation] | [Durability level] | N/A                     |
| [Read operation]  | [Consistency level] | [e.g., 0 ms / 5 s / session-consistent] |

### Conditions for Reopening

This decision should be revisited if:
- Write volume exceeds [X] writes/second and synchronous replication
  adds unacceptable latency.
- A regulatory requirement mandates linearisable audit reads.
- The acceptable stale-read window changes below [Y] ms.

### Cross-References
- Relevant idempotency key policy: [link to API spec or ADR]
- Quorum configuration for the storage tier: [link to runbook or ADR]
```

---

### R2 — Idempotency Key Design Checklist for APIs

**Goal**: Ensure every state-mutating API endpoint that may be retried provides safe duplicate suppression.

**When to use**: Before shipping any `POST`, `PATCH`, or `PUT` endpoint that triggers a payment, reservation, notification, or other non-idempotent side effect.

**Checklist**:

```
[ ] Key generation is CLIENT-SIDE (not server-side).
    Format: UUID v4 or ULID, scoped to {operation_type}/{actor_id}/{nonce}.

[ ] Key is required in the request (reject 400 Bad Request if absent).
    Header: Idempotency-Key: <value>  OR  body field: idempotency_key.

[ ] Deduplicate store is persistent (not in-process memory).
    Recommended: Redis SETNX + EXPIRE, or PostgreSQL with a unique index.

[ ] Check-and-execute is ATOMIC.
    Redis: Lua script. PostgreSQL: INSERT … ON CONFLICT DO NOTHING
    in the same transaction as the side effect.

[ ] On duplicate: return the STORED response (same status code,
    same body, same Idempotency-Key header in response).
    Do NOT re-execute the side effect.

[ ] TTL is set on the deduplicate store.
    Minimum: 24 hours (covers client retry windows).
    Maximum: 7 days (balances storage cost vs. safety window).

[ ] 409 Conflict returned if the same key is used with a DIFFERENT
    request body (key collision, not duplicate retry).

[ ] Key scope is documented in the API contract.
    Example: "Keys are unique per user account; reusing a key across
    accounts is undefined behaviour."

[ ] Load test: send 100 parallel requests with the same key.
    Assert: exactly 1 side effect, 100 identical responses.
```

**Storage atomicity patterns**:

```sql
-- PostgreSQL: atomic check-and-execute in one transaction
BEGIN;
INSERT INTO idempotency_keys (key, result, created_at)
VALUES ($key, NULL, NOW())
ON CONFLICT (key) DO NOTHING;

-- If 0 rows inserted, key already existed: return stored result
-- If 1 row inserted, key is new: execute side effect, then UPDATE result
UPDATE idempotency_keys SET result = $result WHERE key = $key;
COMMIT;
```

```lua
-- Redis Lua: atomic SETNX + EXPIRE
local existing = redis.call('GET', KEYS[1])
if existing then
  return existing
end
redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2])
return nil
```

---

### R3 — Quorum Configuration Worksheet for Multi-Region Storage

**Goal**: Choose N, W, R for a given multi-region storage cluster to satisfy a stated consistency SLO and fault-tolerance requirement.

**When to use**: Before configuring a new Cassandra keyspace, DynamoDB global table, or CockroachDB multi-region database, or when auditing an existing configuration for consistency gaps.

**Step 1 — State the requirements**:

```
Consistency requirement:  [ ] Linearisable  [ ] Read-your-writes
                          [ ] Monotonic reads  [ ] Eventual
Fault-tolerance target:   tolerate ___ simultaneous region/node failures
Write latency budget:     ___ ms p99
Read latency budget:      ___ ms p99
Inter-region latency:     ___ ms (measure with ping; typical 50–150 ms)
```

**Step 2 — Derive N, W, R**:

```
N = (2 × fault_tolerance_target) + 1     [odd N for clean majority]

Strong consistency (linearisable):
  W = floor(N/2) + 1  (majority)
  R = floor(N/2) + 1  (majority)
  Check: W + R = N + 1 > N  [holds]

Read-your-writes (session consistency):
  Option A: W = majority, R = 1 + sticky routing to replica that saw write
  Option B: W = majority, R = majority (full strong consistency)

Eventual consistency:
  W = 1, R = 1
  Check: W + R = 2 <= N  [holds] (no overlap guaranteed)
```

**Step 3 — Check latency feasibility**:

```
Write latency (strong consistency) ≈ inter_region_latency × 1 round-trip
                                    + local_write_latency

For N=3, one write quorum (W=2) requires one inter-region hop.
Example: eu-west-1 → us-east-1 ≈ 85 ms → write p99 ≈ 90–100 ms.

If write latency budget < 20 ms:
  → Use regional leader + async replication (PA/EL).
  → Accept eventual consistency on cross-region reads.
  → Add CRDT or vector-clock conflict resolution for concurrent writes.

If write latency budget = 50–150 ms:
  → Synchronous majority quorum (W=majority) is feasible.
  → Accept ~80–120 ms write latency for strong consistency.
```

**Step 4 — Document the configuration decision**:

```markdown
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| N | 3 | Tolerate 1 region failure; odd N for clean majority |
| W | 2 | Majority quorum; ensures durability on 2 of 3 regions |
| R | 2 | Majority quorum; guarantees W + R > N (2+2=4>3) |
| Consistency level | QUORUM (Cassandra) / Majority (DynamoDB) | |
| Sloppy quorums | DISABLED | Enabled sloppy quorums break W+R>N guarantee |
| Stale-read window | 0 ms (linearisable) | Financial balance reads |
| Write latency p99 | ~100 ms | Acceptable for payment confirmation flow |
| Re-evaluate if | Write latency budget drops below 30 ms | Switch to regional-leader + async replication |
```

**Step 5 — Verify with a chaos test**:

```
1. Kill one region (simulate AZ/region failure).
2. Assert: writes succeed with W=2 (quorum still available on 2 regions).
3. Assert: reads return the latest write (R=2 overlaps with W=2).
4. Assert: no stale reads returned during the failure window.
5. Restore the region; assert: hinted handoff delivers any missed writes.
```

---

## Cross-References

### Foundation

All primitives cited by number in this file are defined with inputs, outputs, failure modes, and worked examples in:

- [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) — canonical source for primitives #1–#11

### Sibling Applied-Recipe References

The following sibling references in this skill complement distributed-systems decisions:

- [decision-theory-applied.md](decision-theory-applied.md) — ADR EU + sensitivity framing for storage selection, real options for irreversible consistency model commits; combine with R1 above for complete ADR methodology
- [queueing-theory-applied.md](queueing-theory-applied.md) — Service sizing and backpressure design; relevant when quorum write latency (P9) becomes the bottleneck in a queueing chain
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md) — Identifying the system-wide bottleneck; use when the consensus layer (P3/P4) or the deduplication store (P7) is suspected as a constraint

### Core Skill References

- [data-architecture-patterns.md](data-architecture-patterns.md) — CQRS, event sourcing, saga coordination; distributed-systems consistency decisions feed directly into saga design
- [scalability-reliability-guide.md](scalability-reliability-guide.md) — CAP theorem in the context of database scaling and read-replica topology; complements Pattern P1
- [api-gateway-service-mesh.md](api-gateway-service-mesh.md) — Idempotency key propagation across a service mesh; complements Pattern P7 and Recipe R2
- [assets/planning/adr-template.md](../assets/planning/adr-template.md) — Base ADR template that Recipe R1 extends with consistency-vs-latency framing
