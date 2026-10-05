---
description: Distributed-systems primitives applied to software architecture decisions — CAP-conscious service boundaries, consensus service selection, idempotency at API surfaces, leases-with-fencing for leader-elected jobs, quorum sizing for multi-region storage, ADR template for consistency vs. latency, and eventual-consistency UX design. Link adapter to foundations-distributed-systems.
last_verified: 2026-09-23
status: stable
---

# Distributed Systems Applied to Architecture Decisions

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.

_Link adapter to [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md). The foundation owns the theory; this file keeps only the architecture decisions the primitives drive — service boundary placement, consensus-service choice, API idempotency contracts, leader-elected jobs, quorum configuration, and eventual-consistency UX — plus the ADR and worksheet templates._

## Table of Contents

- [Theory Pointers](#theory-pointers)
- [Architecture Failures → Primitive](#architecture-failures--primitive)
- [Patterns](#patterns)
  - [P1 — CAP-Conscious Service Boundary Design](#p1--cap-conscious-service-boundary-design)
  - [P3/P4 — Choosing a Consensus Service for Control Planes](#p3p4--choosing-a-consensus-service-for-control-planes)
  - [P7 — Idempotency Keys at API Boundaries](#p7--idempotency-keys-at-api-boundaries)
  - [P8 — Leases with Fencing for Leader-Elected Jobs](#p8--leases-with-fencing-for-leader-elected-jobs)
  - [P9 — Quorum Sizing in Multi-Region Storage](#p9--quorum-sizing-in-multi-region-storage)
  - [P10 — Causal Consistency for Collaborative and Social Features](#p10--causal-consistency-for-collaborative-and-social-features)
  - [P6/P5 — CRDTs and Vector Clocks for Offline-First Sync](#p6p5--crdts-and-vector-clocks-for-offline-first-sync)
- [Anti-Patterns](#anti-patterns)
- [Recipes](#recipes)
  - [R1 — ADR Template: Consistency vs. Latency Tradeoff](#r1--adr-template-consistency-vs-latency-tradeoff)
  - [R2 — Idempotency Key Design Checklist for APIs](#r2--idempotency-key-design-checklist-for-apis)
  - [R3 — Quorum Configuration Worksheet for Multi-Region Storage](#r3--quorum-configuration-worksheet-for-multi-region-storage)
- [Cross-References](#cross-references)

---

## Theory Pointers

| Concept | Canonical owner |
|---|---|
| CAP / PACELC | [01-cap-pacelc.md](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md) |
| FLP | [02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md) |
| Paxos / Raft (incl. production pitfalls: PreVote, CheckQuorum, ReadIndex vs lease reads) | [03-paxos.md](../../foundations-distributed-systems/assets/templates/distributed-systems/03-paxos.md), [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md) |
| Vector clocks / Lamport | [05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md) |
| CRDTs | [06-crdts.md](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md) |
| Idempotency, dedupe/outbox | [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md), [execution-histories.md](../../foundations-distributed-systems/references/execution-histories.md) |
| Leases and fencing | [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md) |
| Quorums (NWR, sloppy quorums, read repair) | [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md) |
| Causal consistency | [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md) |
| Gossip / broadcast | [11-broadcast-protocols.md](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md) |
| Multi-region writes, exactly-once receiver, split-brain prevention | [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md) |
| Gray failure, deadlines, hedging, HLC/clock uncertainty | [production-failure-modes.md](../../foundations-distributed-systems/references/production-failure-modes.md) |
| Linearizability vs serializability | [formal-theory-map.md](../../foundations-distributed-systems/references/formal-theory-map.md) |
| Formal verification tool choice | [foundations-formal-methods](../../foundations-formal-methods/SKILL.md) |

## Architecture Failures → Primitive

| Architecture failure | Diagnosis | Owner |
|---|---|---|
| Two services share a DB and see phantom inconsistency under load | Both claim the same consistency boundary; the implicit CP assumption breaks under partition | 01-cap-pacelc |
| etcd used as a job queue; throughput collapses | Every enqueue is a consensus commit (quorum round trip + fsync) | 04-raft |
| Payment API charges twice after client timeout | No idempotency key; at-least-once retries duplicate the effect | 07-idempotency |
| Scheduled job runs on two hosts after a pause | Lease without storage-enforced fencing token | 08-leases-fencing |
| Cassandra QUORUM reads return stale balances | W=1 was set for write latency, so W + R ≤ N and quorums no longer intersect | 09-quorums |
| Reply shown before the original post in some regions | Multi-region async replication without causal tracking | 10-causal-consistency |
| Offline edit silently overwrote server state | Wall-clock LWW merge discarded concurrent intent | 06-crdts, 05-vector-clocks-lamport |

---

## Patterns

### P1 — CAP-Conscious Service Boundary Design

A service boundary is a consistency domain: inside it you can coordinate atomically; across it you must tolerate divergence. **Draw boundaries to enclose strong-consistency requirements; split wherever staleness is acceptable.** Choose the storage tier to match the boundary's requirement, not the reverse.

- **PC/EC paths** (linearizable reads needed): payment ledger, inventory reservation, seat allocation — single-owner write path, synchronous replication to standby.
- **PA/EL paths** (staleness tolerable): catalogue, profile snapshots, analytics aggregates — serve from nearby replicas without coordination.

**Example — order vs inventory extraction.** Ask: does `PlaceOrder` need a linearizable read of `inventory.reserved_quantity`?
- Yes → keep `PlaceOrder` and `ReserveInventory` in one consistency boundary until a reservation-plus-confirm saga exists.
- No (bounded over-sell is acceptable) → split, and handle over-sell as a business exception.

**Failure mode avoided:** splitting first and retrofitting 2PC or saga compensation later, which is far costlier than placing the boundary correctly up front.

### P3/P4 — Choosing a Consensus Service for Control Planes

The decision is never "implement Paxos vs Raft" — it is which managed consensus service to use and which workloads may go on it.

| Workload | Recommended approach |
|---|---|
| Leader election for scheduled jobs | etcd leases (e.g. Go `concurrency.NewSession` + election) or ZooKeeper; plus fencing (P8) |
| Distributed lock for a critical section | etcd/ZooKeeper lock + fencing token enforced at storage (P8) |
| Control-plane configuration | etcd or ZooKeeper; keep values small (etcd rejects requests above its configured max request size; check `--max-request-bytes` for your deployment) |
| High-throughput ordered event stream | Kafka — partition replication uses the ISR protocol, not Raft; KRaft (KIP-500/KIP-595) is Raft for the **metadata** quorum only |
| Multi-region strongly consistent database | CockroachDB (Raft per range) or Spanner (Paxos per split); cross-region commit latency is real |
| Workflow step coordination | A durable-execution engine (e.g. Temporal) on its own persistence store; do not re-implement consensus |

**Sizing constraint.** Each consensus write costs a quorum round trip plus an fsync. A client that issues writes serially at 10 ms RTT gets at most 1/0.010 s = 100 writes/s; batching and pipelining raise cluster throughput well above that, but the per-write latency floor remains and throughput is bounded by disk fsync latency (etcd is very sensitive to it). Route only low-rate, high-importance coordination (leader grants, config, locks) through consensus; never job queues, event streams, or cache invalidations.

**Availability implication.** Consensus preserves safety by refusing progress without a quorum; FLP ([02-flp-impossibility.md](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)) is why liveness relies on timeouts and partial synchrony. Design control-plane consumers to tolerate the consensus service being briefly unavailable (cached config, bounded retry, fail-safe defaults). Production Raft pitfalls that affect availability (disruptive rejoining nodes, fsync-induced leader flapping, lease vs ReadIndex reads) are in [04-raft.md](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md).

### P7 — Idempotency Keys at API Boundaries

Applies to every retryable mutating endpoint, queue consumer, and webhook receiver. Receiver theory and the exactly-once-receiver recipe: [07-idempotency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md), [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md).

**Architectural contract:**

1. **Client generates the key before the first attempt** (UUID/ULID), scoped `{operation_type}/{actor_id}/{nonce}`. A server-generated key is lost if the server fails before responding, so the retry arrives unmatched (A3).
2. **Persistent dedup store** `(key → request fingerprint, result)` with TTL: Redis `SET NX` + expiry, PostgreSQL unique index with `INSERT … ON CONFLICT DO NOTHING`, DynamoDB `attribute_not_exists` condition.
3. **Atomic claim-then-execute** — the claim and the side effect's commit must share a transaction (or use an in-progress state + completion record); otherwise a concurrent retry slips through.
4. **Return the stored result on duplicate**; return `409` if the same key arrives with a different body.

```
POST /payments
Idempotency-Key: <client-generated UUID>
first request   → execute, store key → response
same key retry  → return stored response, no new charge
different key   → new operation
```

**Delivery semantics.** Transport retries (HTTP with `Retry-After`, SQS visibility timeout, Kafka producer retries) give at-least-once delivery; idempotent effects at the receiver make the **outcome** once-only. Nothing here makes delivery exactly-once, and durable workflow journals do not make external side effects exactly-once either — the external system must deduplicate.

### P8 — Leases with Fencing for Leader-Elected Jobs

Any single-runner job (data pipeline, renewal processor, cache warmer) needs leader election **with** fencing: a paused process does not know its lease expired. Theory: [08-leases-fencing.md](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md).

```
1. Acquire lease → fencing token T=42
2. Include T=42 in every downstream write
3. Storage rejects writes with token < last_seen_token
4. Pause → lease expires → standby gets T=43 → old job resumes with 42 → rejected → it re-checks and stops
```

**Lease sizing.** The lease must outlast the longest expected pause (stop-the-world GC, VM stall, network hiccup) plus clock-rate uncertainty; too short causes needless failovers, too long delays failover. Check your etcd client's default session TTL and measure your p99.9 pause before shortening it.

**Enforce the fence at storage** (application-level checks are racy):

- **PostgreSQL:** `UPDATE t SET …, last_token = $tok WHERE id = $id AND last_token <= $tok` — 0 rows updated means fenced.
- **Object storage:** conditional writes (`If-Match` on ETag) give compare-and-swap, not a monotonic fence — combine with a token stored in the object or its metadata.
- **Redis:** Lua script that compares and writes atomically.

**Common mistake:** using the etcd/ZooKeeper lock without wiring the token into the write path (A4).

### P9 — Quorum Sizing in Multi-Region Storage

Managed defaults do not automatically meet your consistency SLO; choose N/W/R deliberately. A majority quorum is ⌊N/2⌋+1 and tolerates f = ⌊(N−1)/2⌋ failures (N=3→1, 4→1, 5→2, 6→2, 7→3). Quorum intersection vs linearizability: [09-quorums.md](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md).

```
Requirement
├─ Strong reads (balances, reservations, lock state)
│    W + R > N (e.g. N=3, W=2, R=2), no sloppy quorums, versioned values + read repair;
│    intersection alone is not linearizability — verify with a checker
├─ Read-your-writes (own profile edits)
│    sticky routing or a causal/session token (P10), or W + R > N
├─ Monotonic reads (feeds, logs)
│    per-session sticky replica, or a session token carrying the max version seen
└─ Eventual (catalogue, analytics)
     W=1, R=1; accept stale reads
```

**Multi-region latency.** With replicas in three regions and W=2, each write waits for the coordinator's nearest remote replica — one inter-region round trip (tens to low hundreds of ms depending on the region pair; measure, don't assume). For tight write budgets use regional leaders with async replication and explicit conflict handling (CRDTs or version vectors); see the multi-region write recipe in [composition-recipes.md](../../foundations-distributed-systems/references/composition-recipes.md).

**Platform specifics:**
- **Cassandra:** consistency level per request (`LOCAL_QUORUM`, `QUORUM`, `EACH_QUORUM`); hinted handoff stores missed writes for down replicas — hints do not count toward the consistency level (except `ANY`), so a QUORUM write still fails if it cannot reach a real quorum.
- **DynamoDB:** within a region, choose eventually vs strongly consistent reads per request. Global tables replicate asynchronously across regions with last-writer-wins conflict resolution by default; there is no N/W/R knob. Check whether the multi-Region strong consistency mode fits and what it costs in latency and region constraints (verify current availability).
- **CockroachDB/Spanner:** consensus-replicated; the knobs are replica placement, survival goal, and follower/stale reads, not W/R.

### P10 — Causal Consistency for Collaborative and Social Features

Causal anomalies (reply before post, deleted item reappearing, own write not visible) erode trust in collaborative tools and feeds. Theory: [10-causal-consistency.md](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md).

| Anomaly | Root cause | Fix |
|---|---|---|
| Reply before post | Async multi-region replication without dependency tracking | Causal+ (COPS-style dependency metadata on writes) |
| Own write not visible on re-read | Replica switch between write and read | Sticky sessions or causal-token routing |
| Notification about a deleted item | Notification path replicated independently of the object | Put notifications behind the same consistency boundary / dependency check |
| Counter disagrees with list | Denormalised counter on a separate async path | CRDT counter, or derive the count at read time |

**Causal-token routing:** the write response carries a version token (e.g. `{replica: r1, seq: 42}`); the client sends it on later reads; the router serves from a replica that has applied ≥ that version, or waits. MongoDB's causally consistent sessions (operationTime/clusterTime with majority read/write concern) implement this pattern. Alternatives that give read-your-writes without tokens: DynamoDB strongly consistent reads (single region), reading from the leader.

### P6/P5 — CRDTs and Vector Clocks for Offline-First Sync

Offline-first clients must merge divergent state on reconnect; wall-clock LWW silently discards intent for counters, list appends, and toggles. Merge semantics: [06-crdts.md](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md).

| Data | CRDT | Architecture note |
|---|---|---|
| Add-only set (e.g. cart adds) | G-Set | Use OR-Set if removes are needed (2P-Set forbids re-adding) |
| Counts | PN-Counter | Cannot enforce a floor — stock that must not go negative needs a reservation/escrow or bounded counter, not a plain PN-Counter |
| Collaborative text | Sequence CRDT (e.g. Yjs, Automerge) | Use a library; do not hand-roll |
| Presence / cursors | LWW-Register per user | Single writer per register, so no real conflicts |
| Per-user settings | LWW-Register or OR-Map | LWW acceptable when last intent should win |

**Structured records with business invariants:** don't auto-merge. Carry a version vector with each write; if one dominates, apply it; if concurrent, surface a conflict or apply a documented deterministic policy ([05-vector-clocks-lamport.md](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md)). Never rely on device wall clocks alone to order writes.

---

## Anti-Patterns

**A1 — "We are CP" / "we are AP" as a global label.** CAP applies only during partitions; normal operation is the PACELC latency-vs-consistency choice, and it differs per path. Fix: classify per boundary and per operation (catalogue PA/EL, ledger PC/EC) and record it in the ADR (R1).

**A2 — Consensus for every coordination problem.** Job scheduling, cache invalidation, rate-limit counters, and event routing through etcd/ZooKeeper saturate the quorum (P3/P4 sizing) and inherit its unavailability during quorum loss. Fix: consensus only for leader identity, mutual exclusion, and config; Kafka for streams, a queue for jobs, Redis or local token buckets for rate limits; gossip for membership/dissemination ([11-broadcast-protocols.md](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md)).

**A3 — Server-generated idempotency keys.** A key minted per receipt differs on every retry, so dedup never matches. Fix: client-generated key before the first attempt; document format and TTL; `409` on same key + different body.

**A4 — Lease without storage-enforced fencing.** Check-lease-then-write is not atomic relative to expiry; a process can pause between the two and write after a new leader started. Fix: pass the token (etcd revision, ZooKeeper zxid) into every write and enforce `last_token <= $tok` at storage (P8).

**A5 — Majority quorum on even N.** N=4 needs a quorum of 3 and tolerates f = ⌊(4−1)/2⌋ = 1 failure — the same as N=3 with W=R=2, for one more node — and a 2+2 split blocks all majority operations. Fix: odd N (3 tolerates 1; 5 tolerates 2). Use even N only with a tiebreaker/witness that makes the voting set odd.

**A6 — Eventual consistency with no UX accommodation.** Storage-level eventual consistency does not excuse users seeing their own edits revert. Fix: optimistic UI with revert on error; causal-token routing (P10); sticky write-read sessions; explicit "saving…/pending" states until read-your-writes holds.

---

## Recipes

### R1 — ADR Template: Consistency vs. Latency Tradeoff

**Use when** a data-path decision affects stale reads, write rejection during partition, or cross-service transactions. Extends [adr-template.md](../assets/planning/adr-template.md).

```markdown
## ADR-NNN: Consistency Model for [Service / Data Domain]

### Status
Proposed | Accepted | Superseded

### Context
[Data involved, mutating and reading operations, current failure mode or constraint.]

### CAP/PACELC Classification
| Dimension         | Choice | Rationale |
|-------------------|--------|-----------|
| Partition: C or A | C / A  | [Behaviour during a partition] |
| Else: L or C      | L / C  | [Stale reads accepted for latency?] |
| PACELC label      | PC/EC, PA/EL, PA/EC, PC/EL | [Composite] |

### Options Considered
**Option A: [Name]** — storage; partition behaviour; normal-operation write latency (measured); stale-read window
**Option B: [Name]** — same fields

### Decision
[Chosen option, the guarantee it provides, and why the business needs (or doesn't need) it.]

### Consistency SLO
| Operation | Guarantee | Acceptable stale window |
|-----------|-----------|-------------------------|
| [write]   | [durability: replicas/regions acked] | N/A |
| [read]    | [linearizable / session / eventual] | [0 ms / N s / session] |

### Conditions for Reopening
- Write volume exceeds [X]/s and synchronous replication latency becomes unacceptable
- A regulatory requirement mandates linearizable audit reads
- The acceptable stale window falls below [Y] ms

### Cross-References
- Idempotency key policy: [link]
- Quorum configuration (R3): [link]
```

### R2 — Idempotency Key Design Checklist for APIs

**Use before shipping** any `POST`/`PATCH`/`PUT` that triggers a payment, reservation, notification, or other non-idempotent effect.

```
[ ] Key is CLIENT-generated (UUIDv4/ULID), scoped {operation_type}/{actor_id}/{nonce}
[ ] Key is required (400 if absent) — header Idempotency-Key or body field
[ ] Dedup store is persistent (not process memory)
[ ] Claim and side effect commit atomically (same transaction, or in-progress + completion states)
[ ] Duplicate → stored response (same status/body); no re-execution
[ ] Same key + different body → 409
[ ] TTL ≥ the longest client/provider retry window (24 h is a common floor; e.g. set per contract)
[ ] Key scope documented in the API contract
[ ] Load test: 100 parallel requests, same key → 1 side effect, identical responses
```

**PostgreSQL — claim and effect in one transaction:**

```sql
BEGIN;
INSERT INTO idempotency_keys (key, request_hash, status, created_at)
VALUES ($key, $hash, 'in_progress', NOW())
ON CONFLICT (key) DO NOTHING;
-- 0 rows inserted: key exists → ROLLBACK; SELECT stored result (409 if request_hash differs,
--                  or 409/retry-later if status is still 'in_progress')
-- 1 row inserted:  perform the side effect's DB writes here, then:
UPDATE idempotency_keys SET status = 'done', result = $result WHERE key = $key;
COMMIT;
```

If the side effect is an external call (payment provider), the transaction cannot cover it: persist `in_progress`, call the provider **with the same idempotency key**, then record the result — the provider's dedup is what prevents a second charge.

**Redis — atomic claim:**

```lua
-- KEYS[1]=key, ARGV[1]=placeholder, ARGV[2]=ttl seconds
local existing = redis.call('GET', KEYS[1])
if existing then return existing end
redis.call('SET', KEYS[1], ARGV[1], 'EX', ARGV[2])
return nil
```

(Equivalent to a single `SET key val NX EX ttl` followed by `GET` on failure.)

### R3 — Quorum Configuration Worksheet for Multi-Region Storage

**Use before** configuring a Cassandra keyspace or another NWR-configurable store, or when auditing one. For DynamoDB global tables and CockroachDB/Spanner, the equivalents are read-consistency mode and replica placement/survival goals (P9 platform notes).

**Step 1 — Requirements**

```
Consistency:     [ ] linearizable  [ ] read-your-writes  [ ] monotonic reads  [ ] eventual
Tolerate:        f = ___ simultaneous replica/region failures
Write budget:    ___ ms p99      Read budget: ___ ms p99
Inter-region RTT between each region pair: ___ ms (measure)
```

**Step 2 — Derive N, W, R**

```
N = 2f + 1                         (odd; majority ⌊N/2⌋+1 tolerates ⌊(N−1)/2⌋ = f failures)
Strong:            W = R = ⌊N/2⌋ + 1  → W + R = N + 1 > N   (N=3: W=R=2; N=5: W=R=3)
Read-your-writes:  W = majority + sticky/session-token reads, or W = R = majority
Eventual:          W = R = 1          → W + R = 2 ≤ N (no overlap guaranteed)
```

**Step 3 — Latency feasibility**

```
Strong write latency ≈ RTT from coordinator to the (W−1)-th nearest remote replica + local write/fsync
N=3 across 3 regions, W=2 → one RTT to the nearest other region
If write budget < that RTT → regional leader + async replication (PA/EL) + explicit conflict handling
Else                       → synchronous majority is feasible; record the measured p99 in the ADR
```

Adding replicas changes the tail: with W−1 remote acks needed from a larger pool, the wait is an order statistic of more samples, so the tail can shrink even as cost grows. Decide N by failures tolerated vs replica cost; measure latency rather than assuming "fewer replicas = faster".

**Step 4 — Record the decision**

```markdown
| Parameter | Value | Rationale |
|-----------|-------|-----------|
| N | 3 | Tolerate 1 region failure (⌊(3−1)/2⌋ = 1) |
| W | 2 | Majority; durable on 2 of 3 regions |
| R | 2 | W + R = 4 > 3 (intersection) |
| Consistency level | QUORUM (Cassandra) | |
| Sloppy quorum / ANY writes | Disabled | Breaks intersection guarantee |
| Stale-read window | 0 (verified with a consistency checker) | Financial balance reads |
| Write p99 | [measured] ms | [flow it must fit] |
| Re-evaluate if | Write budget drops below measured RTT | Switch to regional leader + async |
```

**Step 5 — Verify with a chaos test** (harness: [qa-resilience distributed-systems-applied.md](../../qa-resilience/references/distributed-systems-applied.md))

```
1. Take one region down
2. Assert: W=2 writes still succeed on the remaining 2 regions
3. Assert: R=2 reads return the latest acknowledged write; checker finds no stale reads
4. Restore; assert missed writes are delivered (hinted handoff/repair in Cassandra)
```

---

## Cross-References

### Foundation

- [foundations-distributed-systems](../../foundations-distributed-systems/SKILL.md) — canonical source for primitives #1–#11
- [patterns-scenarios-traps.md](../../foundations-distributed-systems/references/patterns-scenarios-traps.md) — multi-region write path, payment webhook receiver, collaborative state scenarios
- [primitives-overview.md](../../foundations-distributed-systems/references/primitives-overview.md) — primitive index and decision checklist

### Sibling References in This Skill

- [decision-theory-applied.md](decision-theory-applied.md) — expected-value and real-options framing for irreversible consistency commits; pairs with R1
- [queueing-theory-applied.md](queueing-theory-applied.md) — sizing when quorum write latency (P9) becomes the bottleneck
- [theory-of-constraints-applied.md](theory-of-constraints-applied.md) — when the consensus layer or dedup store is the constraint
- [reliability-theory-applied.md](reliability-theory-applied.md) — availability math for replica counts
- [data-architecture-patterns.md](data-architecture-patterns.md) — CQRS, event sourcing, sagas
- [scalability-reliability-guide.md](scalability-reliability-guide.md) — database scaling and read-replica topology; complements P1
- [api-gateway-service-mesh.md](api-gateway-service-mesh.md) — idempotency key propagation across a mesh; complements P7/R2
- [adr-template.md](../assets/planning/adr-template.md) — base ADR template extended by R1

### Other Skills

- [qa-resilience cascading-failure-prevention.md](../../qa-resilience/references/cascading-failure-prevention.md) — overload, retry storms, metastable failure (owned there)
