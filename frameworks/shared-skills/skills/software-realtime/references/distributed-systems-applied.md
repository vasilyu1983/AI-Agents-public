# Distributed Systems Applied to Real-Time and Collaborative Apps

> **Gate before invoking:** Check [`foundations-distributed-systems` § When to Apply](../../foundations-distributed-systems/SKILL.md#when-to-apply) first. The recipes below assume the foundation is the right tool for the situation; the foundation's skip-conditions route you to a different foundation if not.


Real-time systems are distributed systems. A collaborative editor is a multi-master replication system. A presence channel is a gossip ring. A chat thread is a causally ordered log. A WebSocket reconnect is a lease renewal. This reference maps the 11 distributed-systems primitives from `foundations-distributed-systems` to concrete design and failure patterns in realtime transports, collaborative state, and multi-node fan-out.

_Last verified: 2026-07-11._

## Table of Contents

- [Why Distributed Systems Theory Matters Here](#why-distributed-systems-theory-matters-here)
- [Patterns](#patterns)
  - [P1 CAP/PACELC Framing for Collaboration vs Chat Consistency](#p1-cappacelc-framing-for-collaboration-vs-chat-consistency)
  - [P2 CRDT Merge for Offline-First Collaborative Editing](#p2-crdt-merge-for-offline-first-collaborative-editing)
  - [P3 Vector-Clock-Based Reaction Ordering](#p3-vector-clock-based-reaction-ordering)
  - [P4 Causal+ Consistency for Chat Thread Ordering](#p4-causal-consistency-for-chat-thread-ordering)
  - [P5 Idempotent Message Delivery with Dedupe Key](#p5-idempotent-message-delivery-with-dedupe-key)
  - [P6 Gossip-Based Presence Channel Broadcast](#p6-gossip-based-presence-channel-broadcast)
  - [P7 Lease-Gated WebSocket Room Authority](#p7-lease-gated-websocket-room-authority)
- [Anti-Patterns](#anti-patterns)
  - [A1 Treating Collaborative State as a Request-Response Mutation](#a1-treating-collaborative-state-as-a-request-response-mutation)
  - [A2 Using Wall-Clock Timestamps for Message Ordering](#a2-using-wall-clock-timestamps-for-message-ordering)
  - [A3 Conflating Presence Data with Durable Document State](#a3-conflating-presence-data-with-durable-document-state)
  - [A4 Skipping Dedupe on WebSocket Reconnect Replay](#a4-skipping-dedupe-on-websocket-reconnect-replay)
- [Recipes](#recipes)
  - [R1 OT vs CRDT Choice for a Collaborative Editor](#r1-ot-vs-crdt-choice-for-a-collaborative-editor)
  - [R2 WebSocket Reconnect and Replay Protocol](#r2-websocket-reconnect-and-replay-protocol)
  - [R3 Causal+ Chat Thread with Vector-Clock Dependency Tracking](#r3-causal-chat-thread-with-vector-clock-dependency-tracking)
- [Cross-References](#cross-references)

---

## Why Distributed Systems Theory Matters Here

Real-time applications routinely hide distributed-systems problems behind product language. "Live collaboration" is multi-master replication. "Offline sync" is eventual consistency with conflict resolution. "Notification delivery" is at-least-once broadcast with deduplication. "Typing indicator" is a lease — it expires unless renewed.

Without a framework for these problems, teams reach for ad-hoc solutions that break in production: last-write-wins by wall clock loses concurrent edits; broadcast-everything presence channels saturate at scale; reconnect-without-dedupe creates phantom messages; strong-consistency-in-chat blocks writes during regional partitions.

The primitives in `foundations-distributed-systems` provide the vocabulary. This reference translates them into decisions you make in a real-time system before touching implementation.

---

## Patterns

### P1 CAP/PACELC Framing for Collaboration vs Chat Consistency

**Primitive**: [01-cap-pacelc](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md)

**What it is.** CAP forces a choice between consistency and availability when a partition occurs. PACELC extends this: even without a partition, there is a latency-vs-consistency trade-off. These are distinct axes and real-time systems need an explicit answer for both.

**Realtime mapping.**

| System | Partition choice | Normal-case choice | Rationale |
| ------ | --------------- | ------------------ | --------- |
| Collaborative document (Yjs/Loro) | A — availability | L — latency | Accept divergence; CRDT merge repairs it after partition heals |
| Chat thread ordering | A — availability | L or C depending on SLO | Most chat apps tolerate slightly stale ordering; reply-before-post is unacceptable (causal+) |
| Financial ledger / audit log | C — consistency | C — consistency | Incorrect ordering has real cost; block writes during partition |
| Presence channel | A — availability | L — latency | Presence is ephemeral; stale data expires via TTL; availability matters more than precision |
| Realtime multiplayer game state | A — availability | L — latency | Divergence repaired by authoritative server tick; player experience degrades with latency more than with brief stale state |

**Realtime implication.** The common mistake is applying strong consistency (C/C on the PACELC grid) to data types that do not require it, then paying latency penalties under load. Document state, presence, and ephemeral awareness data are almost always in the A/L quadrant. Only operations that require total ordering — payment ledgers, ranked leaderboards, monotonically increasing counters used for authorization — belong in the C/C quadrant.

**Decision gate.** Before designing any realtime data flow, answer:

1. What happens if two clients make concurrent writes that are never reconciled? (If the answer is "divergence that must never happen," you need consensus — expensive.)
2. Can a temporary stale read cause harm, or is it merely a UX imperfection? (If the latter, eventual or causal consistency is sufficient.)
3. Does the product need "reply before post" ordering? (If yes, causal+ is the minimum; see P4.)

---

### P2 CRDT Merge for Offline-First Collaborative Editing

**Primitive**: [06-crdts](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md)

**What it is.** CRDTs guarantee that any set of replicas converges to the same state when they exchange operations, without coordination. The merge function is commutative, associative, and idempotent — order of delivery does not matter.

**Offline-first sync pattern.** A user opens a document, loses their network connection, makes edits locally, then reconnects. Without CRDTs, the server needs to merge the offline ops with concurrent server-side ops — a hard problem requiring OT or a custom merge algorithm. With CRDTs:

1. The client accumulates a `Y.Doc` update log locally as a sequence of binary-encoded state diffs (`Y.encodeStateAsUpdate`).
2. On reconnect, the client sends its pending update to the server.
3. The server applies `Y.applyUpdate(doc, pendingUpdate)` — the CRDT merge function handles all concurrent ops from other clients automatically.
4. The server sends back the diff since the client's last known state vector (`Y.encodeStateAsUpdateV2(doc, clientStateVector)`).
5. The client applies the server diff. Both now have identical state.

**CRDT type selection for common realtime objects.**

| Object | CRDT | Why |
| ------ | ---- | --- |
| Collaborative rich text (Yjs, Loro) | RGA or FUGUE | Stable position semantics; concurrent inserts at the same position resolve deterministically |
| Shared whiteboard shapes | OR-Set of shapes with LWW-Register per property | Add/remove shapes conflict-free; concurrent property edits resolve by last-write (causal clock) |
| Presence set (online users) | OR-Set with TTL expiry | Concurrent joins and leaves converge; TTL prevents stale entries |
| Shared counter (reaction counts) | PN-Counter | Increment/decrement commute across replicas |
| Shared cursor position | LWW-Register per `user_id` key | Each user's cursor is their own replica; no conflict possible |

**Storage coupling.** Yjs persists documents as binary update logs, not decoded JSON. Store the raw `Uint8Array` update stream in Postgres (`bytea` column) or an object store. Never store the decoded in-memory structure — the serialized format is the authoritative CRDT state and must be re-applied from scratch on server restart.

---

### P3 Vector-Clock-Based Reaction Ordering

**Primitive**: [05-vector-clocks-lamport](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md)

**What it is.** Vector clocks capture true causal relationships: if event A happened before event B, the vector clock of B dominates A's. If two events are concurrent (neither clock dominates), no causal relationship exists and they can be ordered arbitrarily or by a tie-breaker.

**Reaction ordering problem.** In a messaging or social feed system, a user reacts to a message (e.g., thumbs-up on a post). The reaction is causally downstream of the message: it cannot make sense before the message exists. In a multi-region system, reactions may arrive at a replica before the message they reference.

**Pattern: vector-clock dependency check at deliver time.**

```text
Each event carries:
  { event_id, type, body, causal_deps: [{event_id, version}], vc: VectorClock }

Delivery rule:
  For each event E arriving at replica R:
    for dep in E.causal_deps:
      if dep.event_id not in R.applied_events:
        buffer E; do not expose to subscribers
    if all deps satisfied:
      apply E; emit to subscribers; update R.vector_clock
```

**Concurrency detection for UI.** Two emoji reactions to the same message from different users are concurrent (neither reaction caused the other). Vector clocks detect this: `vc(reaction_A) || vc(reaction_B)` — neither dominates. The UI can display them in any stable order (e.g., arrival order, user ID sort). This is correct under PACELC's L/L trade-off: the ordering is deterministic once both arrive, even if the order differs momentarily across replicas.

**Practical size management.** Vector clocks grow with the number of processes. In a realtime system with transient clients, use **version vectors** keyed by stable server-node ID (not client ID). Clients include only the server's version vector in their events. Client-side causality is expressed by tagging events with the `last_server_event_id` they observed, not a full client vector.

---

### P4 Causal+ Consistency for Chat Thread Ordering

**Primitive**: [10-causal-consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)

**What it is.** Causal+ consistency guarantees that causally related operations are delivered in causal order on all replicas, and that replicas converge to the same state when all operations have been applied. It is weaker than linearisability (no global wall-clock ordering of concurrent events) but stronger than eventual consistency (no "reply before post" anomaly).

**Chat thread model.**

The "reply before post" anomaly is not hypothetical — it appears whenever a chat backend serves reads from a replica that is behind the write-region. A user in Frankfurt posts a message (W1 applied to EU replica). Their colleague in Singapore replies (W2, causally depends on W1). A third user in Tokyo loads the thread from an AP replica that has received W2 but not yet W1. They see the reply without the original post.

**Causal+ delivery design for a multi-region chat system.**

1. Assign each message a `causal_token`: the vector clock at the time the message was created, including all messages the sender has read.
2. When a replica receives a message, check whether all entries in its `causal_token` are already applied.
3. If any causal dependency is unresolved, buffer the message in a per-channel hold queue.
4. Apply messages from the hold queue as soon as their dependencies arrive.
5. Expose only applied messages to subscribers — never expose held messages.

**Strong consistency vs causal+ for chat.**

| Dimension | Strong consistency (linearisable) | Causal+ |
| --------- | --------------------------------- | ------- |
| Ordering guarantee | Total order across all messages globally | Causal order; concurrent messages may differ in order across replicas |
| Cost during partition | Blocks writes until quorum re-established | Accepts writes at available replicas; converges after heal |
| Latency | Adds cross-region round-trip on every write | Write-local latency; causal ordering enforced at read/deliver time |
| Typical choice | Financial ledgers, audit logs | Chat, social feeds, collaborative tools |

For most chat products, causal+ is the correct choice: replies always appear after the message they reference, concurrent messages in the same thread may differ slightly in order across regions (acceptable), and the system remains writable during a regional partition.

---

### P5 Idempotent Message Delivery with Dedupe Key

**Primitive**: [07-idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)

**What it is.** At-least-once delivery is the tractable guarantee for WebSocket transports: on reconnect, a client may replay unacknowledged messages. Idempotent receivers absorb duplicates without side effects by keying on a client-assigned `op_id`.

**WebSocket at-least-once delivery model.**

Every client-originated message carries a `op_id` (UUID or ULID). The server processes messages with an atomic check-and-execute:

```python
async def handle_message(msg: dict, db: Database):
    op_id = msg["op_id"]

    # Atomic check: has this op already been processed?
    result = await db.query(
        "SELECT result FROM processed_ops WHERE op_id = $1", op_id
    )
    if result:
        # Already processed — return stored result without re-executing
        return result["result"]

    # Execute and record atomically
    async with db.transaction():
        output = await apply_operation(msg)
        await db.execute(
            "INSERT INTO processed_ops (op_id, result, created_at) "
            "VALUES ($1, $2, now())",
            op_id, output
        )
    return output
```

**Dedupe store TTL.** The `processed_ops` store does not grow unboundedly. Apply a TTL: any `op_id` older than the maximum client reconnect window (e.g., 7 days for mobile apps) can be expired. After TTL expiry, a replayed op will be processed again — this is acceptable because a client that replays a 7-day-old op has lost its local state anyway.

**Scoping dedupe keys.** Scope `op_id` to `(user_id, op_type)` to prevent cross-user key collision. A user crafting a message with an `op_id` that matches another user's recent op_id should not suppress the second user's operation.

**Presence heartbeat idempotency.** Presence heartbeats are inherently idempotent: publishing `user X is online at timestamp T` is a SET operation — applying it twice produces the same state. No dedupe store is needed for heartbeats; the storage is overwrite-safe by design.

---

### P6 Gossip-Based Presence Channel Broadcast

**Primitive**: [11-broadcast-protocols](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md)

**What it is.** Broadcast protocols differ in their delivery guarantees. Presence updates require neither total-order broadcast (expensive, consensus-equivalent) nor reliable broadcast (every node guaranteed delivery). They require **best-effort causal broadcast**: presence data that propagates quickly to all subscribers, with TTL-based expiry compensating for lost updates.

**Gossip-style presence dissemination across a WebSocket fleet.**

When a WebSocket fleet spans multiple nodes (processes or edge regions), presence data must propagate across nodes so that a user connected to Node A is visible to users connected to Node B.

Design:

1. Each node maintains an in-memory presence map: `{ room_id → { user_id → { last_seen, metadata } } }`.
2. On user heartbeat (every 5 s), the node updates its local map and publishes a diff event to a shared pub/sub channel (Redis Pub/Sub, Ably channel, or internal gossip ring).
3. Remote nodes receive the diff, merge it into their local maps, and broadcast the diff to their connected subscribers.
4. Each node independently expires entries where `last_seen + 2 × heartbeat_interval < now()`. No coordination needed for expiry — TTL is local.

**Why gossip is the right broadcast class.** Total-order broadcast would require consensus for every presence update — prohibitively expensive at 50 ms heartbeat frequency across thousands of users. Best-effort causal broadcast is sufficient: users observe presence joins and leaves in approximately causal order (a user's "leave" is never seen before their "join"), and momentary staleness is tolerable for ephemeral presence data.

**Presence fan-out math (worked from these inputs — re-derive for your own numbers, do not reuse this example).** At 1,000 concurrent users in a room with heartbeats every 5 s:

- Presence events per second: 1,000 users ÷ 5 s/heartbeat = 200 updates/s per room.
- Gossip convergence rounds with fan-out k=3 across N=20 nodes: rounds ≈ log(N) / log(k) = log(20) / log(3) ≈ 2.73, round up → 3 rounds to reach all nodes with high probability.
- Steady-state intra-fleet forwarding cost per round: 200 updates/s × k(3) = 600 messages/s per room — this is the per-hop forwarding rate a single node's gossip fan-out generates, independent of how many rounds convergence takes.

Contrast with full-mesh broadcast (each node sends every update directly to all N-1 = 19 others): 200 × 19 = 3,800 messages/s per room — this is O(N²) in fleet size and quickly saturates as either N (nodes) or room count grows, versus gossip's O(N·k) cost that stays flat as N grows for fixed k.

---

### P7 Lease-Gated WebSocket Room Authority

**Primitive**: [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)

**What it is.** A lease is a time-bounded grant of authority. A fencing token monotonically increases with each new lease grant and rejects stale writes. In WebSocket infrastructure, leases model room ownership, editor locks, and "exclusive write" features.

**Exclusive-edit lock pattern.**

When a document section allows only one editor at a time (e.g., a block in a Notion-style editor), model the edit permission as a lease:

1. When a user begins editing block B, request a lease from the lease authority (the server or a coordination service like etcd).
2. The lease authority issues a lease with `{ holder: user_id, token: N, expires_at: T }`.
3. All writes to block B must include the fencing token `N`. The storage layer rejects writes with `token < max_seen_token`.
4. The user's client renews the lease every `T/2` seconds via a heartbeat. If the client disconnects, the lease expires at `T`.
5. After expiry, a new user can acquire the lease with token `N+1`. The previous holder's stale writes (if they reconnect) are rejected because `N < N+1`.

**Fencing token in WebSocket messages.**

```json
{
  "op": "edit_block",
  "block_id": "b123",
  "content": "...",
  "lease_token": 42
}
```

Server-side validation:

```python
def apply_block_edit(block_id: str, content: str, lease_token: int):
    current_max = db.get("block_max_token", block_id, default=0)
    if lease_token < current_max:
        raise StaleLeaseError(f"Token {lease_token} < max seen {current_max}")
    db.set("block_max_token", block_id, lease_token)
    db.update_block(block_id, content)
```

**Lease duration trade-off.** Short leases (5–10 s) reduce the lock-hold time after a client crash, improving availability. Long leases (30–60 s) reduce renewal overhead but leave blocks locked for longer after disconnection. For collaborative editing, 10 s with 5 s renewal is a reasonable default: a crashed client releases authority within 10 s, and renewal traffic is one heartbeat per 5 s per active lock.

---

## Anti-Patterns

### A1 Treating Collaborative State as a Request-Response Mutation

**Diagnosis.** A collaborative document is implemented as a standard HTTP PATCH or a WebSocket "update" command that overwrites the server's current state with the client's proposed state. Concurrent edits from two clients overwrite each other. The last write wins, determined by server arrival time.

**What goes wrong.** Two users concurrently edit the same paragraph. Client A's PATCH arrives first and is applied. Client B's PATCH arrives 200 ms later with B's version of the paragraph — which does not include A's edit. A's edit is silently erased. Neither client sees an error. The document now contains only B's changes.

**Distributed systems diagnosis.** Request-response mutation is single-master write serialization: it works when only one client writes at a time. For concurrent writes, it is linearisable by arrival order — but arrival order under network jitter is not deterministic or meaningful. This is the wrong consistency model for collaboration.

**Fix.** Replace mutations with operation-based or state-based CRDTs (P2). The client sends an operation delta, not a full state replacement. The server merges the delta into the CRDT state. Concurrent operations from multiple clients converge deterministically regardless of arrival order. See Recipe R1 for the OT vs CRDT decision gate.

---

### A2 Using Wall-Clock Timestamps for Message Ordering

**Diagnosis.** Messages in a chat thread or event stream are ordered by server `created_at` timestamp (a database `TIMESTAMP WITH TIME ZONE` populated at insert time). Clients submit messages from multiple regions or multiple server nodes. The ordering appears correct in testing and breaks in production.

**What goes wrong.** Two messages posted 10 ms apart from servers in different data centers are assigned timestamps from those servers' local clocks. NTP drift between the servers can be 1–50 ms on a LAN and 100+ ms across regions. A reply to a message can receive a timestamp that is earlier than the original message's timestamp if the reply's server clock is behind.

**Distributed systems diagnosis.** Wall-clock ordering violates the happens-before relation (primitive 05). Lamport timestamps guarantee that if A happened before B, `L(A) < L(B)`. Wall-clock timestamps make no such guarantee: two concurrent events on different nodes can have any relative timestamp.

**Fix.** Use Lamport timestamps or vector clocks for event ordering. Each server maintains a Lamport counter. On message receipt, apply `L := max(L, L_received) + 1`. Use `(L, server_id)` as the sort key for deterministic ordering across replicas. For chat threads requiring causal ordering, attach a causal dependency token as in P4. Reserve wall-clock timestamps for display only, never for ordering logic.

---

### A3 Conflating Presence Data with Durable Document State

**Diagnosis.** User presence (online status, cursor position, typing indicator) is stored in the same data structure as the document content — for example, persisted to the same database row or included in the CRDT document update log.

**What goes wrong.** Each cursor movement generates a CRDT update. A 30-minute editing session from 10 users generates tens of thousands of CRDT updates encoding cursor positions. The document update log grows to hundreds of megabytes. On client reconnect, the client downloads and replays the full update log — including all historical cursor positions — which have no meaning after the session ends. Storage grows unboundedly. Load time degrades proportionally.

**Distributed systems diagnosis.** CRDTs (primitive 06) are designed for durable, convergent state. Presence data is ephemeral: a cursor position is only meaningful in the current session. Applying CRDT merge semantics to ephemeral data inherits the storage overhead without the benefit, because the data becomes stale seconds after creation.

**Fix.** Keep awareness data in a separate, non-persistent channel. In Yjs, use `provider.awareness` (a separate protocol from the CRDT document). In custom systems, maintain presence state in an in-memory OR-Set with TTL (P6) published over a separate WebSocket event stream. Never write presence data to the durable document CRDT, and never persist awareness state to the document store.

---

### A4 Skipping Dedupe on WebSocket Reconnect Replay

**Diagnosis.** On WebSocket reconnect, the client replays its pending operation queue (accumulated while disconnected) without attaching idempotency keys. The server applies all replayed operations as new writes.

**What goes wrong.** User sends a message (op M1). The WebSocket drops before the server acknowledges. The client reconnects and replays M1. The server, having no record of M1 from the dropped connection, applies it again. The chat thread now contains two identical messages. For non-idempotent operations (increment a counter, charge a card, send an email notification), the duplicate causes real harm.

**Distributed systems diagnosis.** At-least-once delivery (primitive 07) without idempotent receivers produces exactly this outcome. The transport cannot guarantee exactly-once — only the receiver can create the illusion of exactly-once semantics via a dedupe store keyed on client-generated `op_id`.

**Fix.** Assign a stable `op_id` (UUID) to every operation before adding it to the offline queue. The server uses atomic check-and-execute (P5) to absorb duplicates. The `op_id` persists in the client's local storage until the operation is confirmed by the server. On reconnect, replay the queue with the same `op_id` values. The server returns the stored result for already-processed operations without re-executing them.

---

## Recipes

### R1 OT vs CRDT Choice for a Collaborative Editor

**Goal.** Choose between Operational Transformation (OT) and CRDTs for a collaborative text or structured-document editor, based on the system's consistency, offline, and scaling requirements.

**Primitives used.**

- CRDTs → [06-crdts](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md)
- CAP/PACELC → [01-cap-pacelc](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md)
- FLP Impossibility → [02-flp-impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)

**Step 1: Understand the fundamental distinction.**

| Axis | Operational Transformation (OT) | CRDT |
| ---- | ------------------------------- | ---- |
| Mechanism | Transform ops against concurrent ops at a central server | Merge-by-design; no transformation needed |
| Coordination requirement | Requires a server to serialize and transform all ops | Decentralized; peers merge directly |
| Offline support | Offline edits require server reconciliation on reconnect | Native: merge function handles all concurrent states |
| Scaling | Single-server coordination bottleneck | Can merge on edge, mobile, or peer-to-peer |
| Implementation complexity | Complex transformation functions for each op type | Complex CRDT type selection; merge is mechanical once type is chosen |
| Production libraries | Google Docs (proprietary), ShareDB/json0 (open) | Yjs (MIT), Loro (MIT, Rust-based), Automerge (MIT) |

**Step 2: Decision gate.**

```text
Q1: Is offline editing required (mobile, PWA, or low-connectivity use case)?
    → Yes: CRDT. OT's server-serialization requirement makes offline edits
           hard to reconcile without re-implementing parts of a CRDT.
    → No: proceed to Q2.

Q2: Is a server available as a coordination point during all editing sessions?
    → No (P2P, edge-only, or serverless): CRDT.
    → Yes: proceed to Q3.

Q3: Is the document a plain text or rich text document?
    → Plain/rich text: CRDT (Yjs Y.Text or Loro text) is production-ready and
                       well-supported. OT via ShareDB is also viable for
                       server-coordinated sessions.
    → Structured JSON document (nested objects, arrays, maps):
       → Yjs Y.Map + Y.Array (CRDT) handles concurrent structural mutations.
       → ShareDB/json0 (OT) handles JSON but transformation rules are complex
          for deeply nested concurrent mutations.

Q4: Is document size expected to exceed 10 MB or history retention > 30 days?
    → Yes: evaluate CRDT tombstone GC strategy. Yjs update logs grow with
           delete operations (tombstones); run Y.gc = true and implement
           periodic snapshot compaction to avoid unbounded growth.
    → No: either approach is viable at this scale.
```

**Step 3: Yjs CRDT implementation checklist.**

1. One `Y.Doc` per document. Do not share a `Y.Doc` across unrelated documents.
2. Persist state as binary: `Y.encodeStateAsUpdateV2(doc)` → `Uint8Array` → store in Postgres `bytea`.
3. On reconnect, send state vector: `Y.encodeStateVector(doc)` → server returns diff → `Y.applyUpdateV2(doc, diff)`.
4. Awareness in `provider.awareness` only. Never write cursor or typing state to the `Y.Doc`.
5. Garbage-collect deleted content: `doc.gc = true` (default). Disable GC only if undo history beyond the session is required.
6. Test concurrent edits: open two clients, partition the network, make edits on both, reconnect, verify convergence.

**Step 4: Verification checks.**

- Two clients with simulated 2-second network partition produce identical final doc state after reconnect.
- Document update log size grows at ≤ 1 KB/s per active user (approximate; depends on edit frequency).
- `Y.encodeStateAsUpdateV2` binary diff sent on reconnect is ≤ 1 MB for a typical session's pending changes.
- Awareness events are never present in the persisted `Y.Doc` update log.

---

### R2 WebSocket Reconnect and Replay Protocol

**Goal.** Design a reconnect protocol that replays unacknowledged operations safely across a WebSocket drop without producing duplicate side effects.

**Primitives used.**

- Idempotency → [07-idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md)
- Leases and Fencing → [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md)
- FLP Impossibility → [02-flp-impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md)

**Step 1: Assign stable op_ids at creation.**

```typescript
interface Operation {
  op_id: string;       // UUID generated at creation, stable across retries
  op_type: string;     // "send_message" | "edit_block" | "react" | ...
  payload: unknown;
  created_at: number;  // Client-local timestamp (display only, not ordering)
}

// Client-side queue (persisted to localStorage / IndexedDB)
const pendingQueue: Operation[] = [];

function enqueue(op: Omit<Operation, "op_id" | "created_at">): Operation {
  const operation: Operation = {
    ...op,
    op_id: crypto.randomUUID(),
    created_at: Date.now(),
  };
  pendingQueue.push(operation);
  persistQueue(pendingQueue);  // survives page reload
  return operation;
}
```

**Step 2: Reconnect with exponential backoff.**

```typescript
let reconnectDelay = 1000; // ms

async function reconnect() {
  while (true) {
    try {
      await connect();            // throws on failure
      await authenticate();       // re-authenticate; refresh token if needed
      await replayPendingQueue(); // send all unacknowledged ops
      reconnectDelay = 1000;      // reset on success
      return;
    } catch {
      const jitter = 1 + (Math.random() * 0.4 - 0.2); // ±20%
      reconnectDelay = Math.min(reconnectDelay * 2 * jitter, 30_000);
      await sleep(reconnectDelay);
    }
  }
}
```

**Step 3: Server-side idempotent op handler.**

```python
async def handle_operation(ws_session, msg: dict):
    op_id   = msg["op_id"]
    op_type = msg["op_type"]
    payload = msg["payload"]
    user_id = ws_session.user_id

    # Scoped dedupe key: prevents cross-user collision
    dedupe_key = f"{user_id}:{op_id}"

    result = await redis.get(f"dedupe:{dedupe_key}")
    if result is not None:
        # Already processed — return stored ack without re-executing
        await ws_session.send({"ack": op_id, "result": json.loads(result)})
        return

    # Execute
    output = await dispatch(op_type, payload, user_id)

    # Store with TTL (7 days covers mobile reconnect window)
    await redis.setex(
        f"dedupe:{dedupe_key}",
        7 * 24 * 3600,
        json.dumps(output),
    )

    await ws_session.send({"ack": op_id, "result": output})
```

**Step 4: Client-side ack and queue drain.**

```typescript
ws.on("message", (msg) => {
  const { ack, result } = JSON.parse(msg);
  if (ack) {
    // Remove from pending queue only after server ack
    const idx = pendingQueue.findIndex((op) => op.op_id === ack);
    if (idx !== -1) {
      pendingQueue.splice(idx, 1);
      persistQueue(pendingQueue);
    }
  }
});
```

**Step 5: Queue size guard.**

```typescript
const MAX_QUEUE_SIZE = 200; // tune per app

function enqueue(op) {
  if (pendingQueue.length >= MAX_QUEUE_SIZE) {
    // Surface to user rather than silently dropping
    notifyUser("Too many pending changes. Please reconnect to continue editing.");
    return null;
  }
  // ... normal enqueue
}
```

**Verification checks.**

- Simulate WebSocket drop mid-send; confirm the operation appears exactly once in the server's data store after reconnect.
- Simulate client crash and reload; confirm `localStorage` queue is replayed and deduplicated on reconnect.
- Confirm queue drain order: operations replay in enqueue order (FIFO), not arrival order.
- Confirm expired dedupe keys (> TTL) do not suppress legitimate future operations with reused `op_id` values (UUID v4 collision probability is negligible).

---

### R3 Causal+ Chat Thread with Vector-Clock Dependency Tracking

**Goal.** Design a multi-region chat thread that never shows a reply before its parent message, uses causal+ consistency, and remains writable during a regional partition.

**Primitives used.**

- Causal Consistency → [10-causal-consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md)
- Vector Clocks and Lamport Timestamps → [05-vector-clocks-lamport](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md)
- Quorums → [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md)
- Broadcast Protocols → [11-broadcast-protocols](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md)

**Step 1: Message schema with causal dependencies.**

```typescript
interface ChatMessage {
  id: string;              // ULID (time-sortable for UI display, not for ordering)
  thread_id: string;
  author_id: string;
  body: string;
  // Causal metadata
  lamport_ts: number;      // Lamport timestamp at time of creation
  parent_id?: string;      // For replies: the message_id being replied to
  causal_deps: string[];   // [parent_id] for replies; [] for root messages
  region: string;          // Source region of the write
}
```

**Step 2: Per-replica hold queue for causal gating.**

```python
class CausalDeliveryBuffer:
    """
    Buffers messages whose causal dependencies are not yet applied.
    Applied messages are emitted to subscribers in causal order.
    """

    def __init__(self, db):
        self.db   = db
        self.held = {}  # message_id → ChatMessage

    async def receive(self, msg: dict):
        deps_satisfied = all(
            await self.db.message_exists(dep)
            for dep in msg["causal_deps"]
        )

        if deps_satisfied:
            await self._apply(msg)
            # Check whether held messages are now unblocked
            await self._drain_held()
        else:
            self.held[msg["id"]] = msg

    async def _apply(self, msg: dict):
        await self.db.insert_message(msg)
        await self.broadcast_to_subscribers(msg)

    async def _drain_held(self):
        released = True
        while released:
            released = False
            for msg_id, msg in list(self.held.items()):
                deps_satisfied = all(
                    await self.db.message_exists(dep)
                    for dep in msg["causal_deps"]
                )
                if deps_satisfied:
                    del self.held[msg_id]
                    await self._apply(msg)
                    released = True
```

**Step 3: Lamport timestamp on write.**

```python
async def post_message(thread_id: str, author_id: str, body: str,
                       parent_id: str | None, client_lamport: int) -> dict:
    # Server Lamport update: max(server_L, client_L) + 1
    server_L = await redis.incr(f"lamport:{thread_id}")
    L = max(server_L, client_lamport) + 1
    await redis.set(f"lamport:{thread_id}", L)

    msg = {
        "id":          ulid(),
        "thread_id":   thread_id,
        "author_id":   author_id,
        "body":        body,
        "lamport_ts":  L,
        "parent_id":   parent_id,
        "causal_deps": [parent_id] if parent_id else [],
        "region":      CURRENT_REGION,
    }
    await db.insert_message(msg)
    await pubsub.publish(f"thread:{thread_id}", msg)
    return msg
```

**Step 4: Client subscription and causal ordering on receipt.**

```typescript
const appliedIds = new Set<string>();
const holdQueue  = new Map<string, ChatMessage>();

function onMessageReceived(msg: ChatMessage) {
  const depsReady = msg.causal_deps.every((dep) => appliedIds.has(dep));

  if (depsReady) {
    applyMessage(msg);
  } else {
    holdQueue.set(msg.id, msg);
  }
}

function applyMessage(msg: ChatMessage) {
  appliedIds.add(msg.id);
  renderMessage(msg);

  // Drain hold queue: check if anything unblocked
  for (const [id, held] of holdQueue) {
    const depsReady = held.causal_deps.every((dep) => appliedIds.has(dep));
    if (depsReady) {
      holdQueue.delete(id);
      applyMessage(held);
    }
  }
}
```

**Step 5: Display ordering.**

Use Lamport timestamp for display sort within a thread. For concurrent root messages (no causal relationship), `(lamport_ts, author_id)` provides a stable total order that is consistent across all clients once both messages are applied. For replies, causal ordering guarantees the parent always appears before the reply regardless of Lamport timestamp.

**Verification checks.**

- Send a reply before the parent has arrived at a test replica; confirm the reply is held in the buffer until the parent arrives.
- Partition the EU and AP regions; confirm both accept writes; after partition heals, confirm both replicas converge to the same message order.
- Confirm no message with a non-empty `causal_deps` is ever delivered to subscribers before all its deps are in `applied_ids`.
- Confirm Lamport timestamps are strictly monotonically increasing within a thread across all regions.

---

## Cross-References

**Primitive definitions** (full details in `foundations-distributed-systems`):

- [01-cap-pacelc](../../foundations-distributed-systems/assets/templates/distributed-systems/01-cap-pacelc.md) — CAP theorem and PACELC extension
- [02-flp-impossibility](../../foundations-distributed-systems/assets/templates/distributed-systems/02-flp-impossibility.md) — FLP impossibility result
- [03-paxos](../../foundations-distributed-systems/assets/templates/distributed-systems/03-paxos.md) — Paxos consensus algorithm
- [04-raft](../../foundations-distributed-systems/assets/templates/distributed-systems/04-raft.md) — Raft consensus algorithm
- [05-vector-clocks-lamport](../../foundations-distributed-systems/assets/templates/distributed-systems/05-vector-clocks-lamport.md) — Vector clocks and Lamport timestamps
- [06-crdts](../../foundations-distributed-systems/assets/templates/distributed-systems/06-crdts.md) — Conflict-free replicated data types
- [07-idempotency](../../foundations-distributed-systems/assets/templates/distributed-systems/07-idempotency.md) — Idempotency and at-least-once delivery
- [08-leases-fencing](../../foundations-distributed-systems/assets/templates/distributed-systems/08-leases-fencing.md) — Leases and fencing tokens
- [09-quorums](../../foundations-distributed-systems/assets/templates/distributed-systems/09-quorums.md) — Quorum reads and writes
- [10-causal-consistency](../../foundations-distributed-systems/assets/templates/distributed-systems/10-causal-consistency.md) — Causal and causal+ consistency
- [11-broadcast-protocols](../../foundations-distributed-systems/assets/templates/distributed-systems/11-broadcast-protocols.md) — Gossip, FIFO, causal, and total-order broadcast

**Sibling references in this skill:**

- [collaboration-patterns.md](collaboration-patterns.md) — Document model, awareness separation, sync transport, and recovery patterns for collaborative editing
- [transport-selection.md](transport-selection.md) — SSE vs WebSocket vs managed real-time decision matrix
- [edge-realtime.md](edge-realtime.md) — Edge platforms, CRDT picks, and channel limits: PartyKit, Liveblocks v2, Supabase, Socket.IO v4, Yjs/Loro
- [april-vendor-traps.md](april-vendor-traps.md) — Vendor-specific gotchas and version-pinned regressions

**Related skills:**

- [software-architecture-design](../../software-architecture-design/SKILL.md) — System-level event architecture and consistency model decisions
- [software-backend](../../software-backend/SKILL.md) — Request-response APIs, background jobs, and storage patterns underlying realtime systems
- [qa-resilience](../../qa-resilience/SKILL.md) — Chaos testing for partition recovery, reconnect behavior, and CRDT convergence verification
