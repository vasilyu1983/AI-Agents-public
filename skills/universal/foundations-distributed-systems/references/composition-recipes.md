# Composition Recipes

Load this when one failure needs several primitives stacked: multi-region writes, an exactly-once receiver, split-brain prevention, gossip dissemination, or an AI-agent pipeline with retried tool calls and shared state. Each recipe lists the stack, then the inputs, rules and outputs a design review should produce.

Primitive numbers refer to the playbooks in [`../assets/templates/distributed-systems/`](../assets/templates/distributed-systems/).

## Contents

- [Multi-region writes](#multi-region-writes)
- [Exactly-once receiver](#exactly-once-receiver)
- [Split-brain prevention](#split-brain-prevention)
- [Gossip-based state dissemination](#gossip-based-state-dissemination)
- [AI-agent pipeline: idempotent tool calls and shared CRDT state](#ai-agent-pipeline-idempotent-tool-calls-and-shared-crdt-state)
- [Not here: disaggregated LLM serving](#not-here-disaggregated-llm-serving)

---

## Multi-region writes

**Goal**: Accept writes in multiple regions with bounded staleness and no lost updates.

**Stack**:
1. Quorums (#9): set W = majority across region replicas; read repair on stale reads.
2. Leases and Fencing (#8): each region's write coordinator holds a time-bounded lease; a fencing token stops deposed coordinators from writing.
3. Idempotency (#7): idempotent receivers with per-operation idempotency keys tolerate retries across region failover.
4. Causal Consistency (#10): vector clocks or hybrid logical clocks track happens-before across regions; clients use sticky routing to avoid causal anomalies.

**When to add CRDTs (#6)**: if the shared state supports a commutative merge (counters, sets, last-write-wins registers), replace quorum coordination with CRDT replication.

WAN-latency research options (speculative 2PC, cross-cluster consistent broadcast) are in [`research-frontier.md`](research-frontier.md).

**Inputs:** N (replicas across regions), W, R, lease duration (ms), write latency SLO (p99 ms), AZ/region-failure tolerance, idempotency key schema.
**Rules:** For a fixed-set quorum design, W + R > N provides intersection, not a complete strong-consistency guarantee; choose durable acknowledgement and read/write ordering from the protocol. W = majority addresses replica-count failures only with durability and safe elections. R = 1 with W = N still needs version/concurrency handling. Lease duration must be shorter than the SLO for detecting a deposed coordinator, and the lease is only safe under a stated clock-drift bound. Use CRDT replication when state supports commutative merge and coordination overhead exceeds the latency SLO.
**Outputs:** (N, W, R), lease duration and drift bound, expected write p99 per region, maximum AZ/region-failure tolerance, whether CRDT replacement is viable.

---

## Exactly-once receiver

**Goal**: Commit one business effect within a stated atomicity boundary despite at-least-once delivery; reconcile external effects when that boundary cannot include the provider.

**Stack**:
1. Idempotent receiver (#7): the operation is idempotent, or it commits its state mutation and dedupe result atomically.
2. Idempotency key + dedupe store: atomically reserve/commit the business operation and cached result; a lookup alone is not atomic with execution.
3. At-least-once delivery: the transport retries until acknowledged; the receiver's idempotency makes retries safe.

**When to add Raft (#4)**: if the dedupe store must be replicated, use a consensus-backed store so the dedupe log survives node failures without split-brain.

**Inputs:** idempotency key schema (operation type + client ID + sequence number), dedupe store type (in-memory / persistent / replicated), transport retry count and backoff, expected duplicate rate, guarantee scope (single node vs cluster).
**Rules:** Define the commit boundary and concurrent-duplicate behavior. Commit local effect plus dedupe result in one transaction, or use stable provider idempotency and status reconciliation for external effects. Same key plus different payload must fail; a duplicate of a completed operation returns its cached result. Retention must cover replay; dedupe TTL ≥ last retry attempt + its timeout. Replicated durability does not make an external call atomic. Follow [`execution-histories.md`](execution-histories.md).
**Outputs:** key format, dedupe schema (key → result + TTL), atomicity scope and crash-window reconciliation evidence, dedupe TTL vs retry window, whether consensus-backed replication is required.

---

## Split-brain prevention

**Goal**: Prevent two nodes from simultaneously acting as primary/leader.

**Stack**:
1. Lease (#8): the primary holds a time-bounded lease; all writes require a valid lease.
2. Fencing token (#8): a monotonically increasing integer issued at each lease grant; the storage layer rejects writes whose token is below the maximum seen.
3. Consensus (#3/#4): after a partition heals, run a full election round before granting a new lease; never grant a lease without quorum acknowledgement.

**When to add Quorums (#9)**: W > N/2 gives intersecting write quorums under fixed membership, but needs protocol-specific ordering/version validation for single-winner safety; it is not a substitute for consensus.

**Inputs:** N, AZ layout (nodes per AZ), lease duration (ms), current fencing token, election timeout range (ms), network RTT (ms), write latency SLO (p99 ms).
**Rules:** Quorum = ⌊N/2⌋+1, which tolerates ⌊(N−1)/2⌋ node failures (N=4 tolerates 1, not 2). A new lease may be granted only after an election round with quorum acknowledgement. The fencing token is monotonic and stored durably; storage atomically rejects a token strictly below max_seen_token and persists the new maximum with the write; repeated valid writes at the same epoch remain allowed, with operation dedupe checked separately. Losing any one AZ must leave a quorum. For non-Raft storage, document the protocol that establishes ordering and the invariant; quorum intersection alone is insufficient.
**Outputs:** quorum size, AZ node distribution, fencing-token increment policy, write p99 estimate, single-AZ failure tolerance, whether quorum enforcement alone suffices or consensus is required.

**Worked example (5 nodes vs 3 nodes).** 5-node Raft cluster across three AZs as 2/2/1. Quorum = ⌊5/2⌋+1 = 3. Lose AZ-A (2 nodes) → 3 alive → quorum holds. Lose AZ-B and AZ-C → 2 alive → below quorum, writes stop (safety preserved). A deposed AZ-A leader resuming after a GC pause sends token 4; storage has seen token 5; the write is rejected.

Write latency is set by how long the leader waits for acks. A 5-node leader waits for the 2nd-fastest of 4 followers; a 3-node leader waits for the faster of 2. With iid follower latency survival S(t), P(ack wait > t) is 4S³−3S⁴ for 5 nodes and S² for 3 nodes; S² is larger whenever S < 1/3, which covers the whole tail. Illustration (exponential follower latency, per-follower p99 = 25 ms, 5 ms leader processing): ack-wait p99 is 10.6 ms for 5 nodes vs 12.5 ms for 3 nodes, so write p99 ≈ 15.6 ms vs ≈ 17.5 ms. Shrinking to 3 nodes does **not** buy tail latency under these assumptions. Its trade is fewer replicas (less fsync, bandwidth and cost) against tolerating 1 node failure instead of 2; both layouts survive one AZ loss. This is quorum sizing, not PACELC (PACELC's else-branch is latency vs consistency in normal operation). Real placements break the iid assumption (a same-AZ follower answers faster), so measure per-follower latency before sizing.

---

## Gossip-based state dissemination

**Goal**: Propagate membership or soft state to all nodes with eventual convergence and no single point of failure.

**Stack**:
1. Gossip / epidemic broadcast (#11): each node periodically exchanges digests with k random peers; convergence takes O(log N) rounds.
2. CRDTs (#6): model the state as a CRDT (e.g. OR-Set for membership) so merge order does not matter.
3. Vector clocks (#5): attach a clock to payloads to discard stale updates.

**Inputs:** N, fan-out k, state model, update rate, acceptable convergence time, partition tolerance requirement.
**Rules:** Convergence ≈ O(log N) rounds with k peers chosen uniformly at random; state must be a CRDT so any merge order is safe; discard a payload whose clock is dominated by the node's current clock. Gossip-based failure detection is a suspicion signal, not a fact; see gray failure in [`production-failure-modes.md`](production-failure-modes.md).
**Outputs:** fan-out k, CRDT type, clock schema, expected rounds and wall-clock convergence at the given N.

---

## AI-agent pipeline: idempotent tool calls and shared CRDT state

**Goal**: Tool calls with business effects survive retries, recovery and agent reassignment without duplication; shared workspace state converges without locks.

**Stack**:
1. **Idempotency (#7)**: persist one stable business-operation ID before dispatch and reuse it across transport retries, recovery and reassignment. Distinct authorized operations need distinct IDs even with identical arguments; a hash of inputs or agent/step identity alone is insufficient. A durable workflow journal preserves execution history but cannot atomically commit an unrelated provider's side effect: an activity may run again after the provider accepted it and before local completion was persisted. Require provider idempotency/status reconciliation, or one database transaction containing both the local effect and the dedupe result. Choose a runtime by its verified transaction boundary, not a blanket exactly-once claim. [Temporal's Activity documentation](https://docs.temporal.io/activities) recommends idempotent activities. Runtime selection itself belongs to [`ai-coding-agents-state`](../../ai-coding-agents-state/references/durable-trigger-integration.md).
2. **Leases and Fencing (#8)**: when an agent needs exclusive control of a resource (a file section, an API quota slot), issue a lease with a fencing token; the resource rejects stale tokens, so a crashed-and-recovered agent cannot double-apply writes.
3. **CRDTs (#6)**: model the shared workspace as a CRDT (RGA for text, OR-Set for task sets, LWW-Register for key-value slots). Yjs, Automerge 3 and Loro are the usual libraries; treat their version and performance claims as volatile and check release notes. Read the migration notes before a major upgrade: Automerge 3 removed the `Text` class.

**Durable-execution correctness contract** (runtime-neutral; the runtimes themselves are out of scope here):
- Workflow code must be deterministic on replay; side effects live in activities.
- Activities are at-least-once. Every effectful activity needs the operation ID above.
- Changing the code of in-flight workflows needs explicit versioning, or replay diverges.
- Compensations must themselves be idempotent and must tolerate racing a late forward effect; name the point of no return after which the saga can only go forward.

**Classical concurrency control transfers badly to agents.** An agent "transaction" spans a long inference, its read set is broad and opaque, and its writes take effect immediately through tools, so 2PL/OCC have no clean validate-or-rollback point. CoAgent (arXiv:2606.15376, June 2026, preprint) fixes a serialization order at launch, filters reads to that order, and applies writes speculatively over undoable tools; the paper reports in its abstract correctness within 5% of serial execution at 1.4× speedup on ten contended workloads. Unreplicated; the transferable point is the diagnosis: **before reaching for locks across agents, check whether the tools are undoable and whether a pre-agreed order removes the conflict.**

**Kill criteria:** replace CRDTs with consensus-backed coordination for non-commutative invariants (unique names, capacity limits, balances). Pure-read tool calls need no idempotency infrastructure.

**Inputs:** agent count, tool call rate, durable-execution backend, shared state type, CRDT type, lease duration, expected retry rate.
**Rules:** persist a stable business-operation key before dispatch; record payload binding and in-progress/completed states; journal-before-execution alone is insufficient for external effects; retain dedupe records across the admitted duplicate horizon; apply the chosen CRDT's state-merge or operation-delivery contract; the fencing token is durable and enforced at the resource.
**Outputs:** key schema, journal/dedupe backend, CRDT type per state segment, lease duration, which invariants need consensus instead of CRDTs.

---

## Not here: disaggregated LLM serving

Prefill/decode disaggregation is a queueing and interference decision, not a consensus or quorum problem. Use [`ai-llm-inference`](../../ai-llm-inference/SKILL.md) and [`foundations-queueing-theory`](../../foundations-queueing-theory/SKILL.md). The only primitive that carries over is idempotency (#7) for retried KV-cache transfers.
