---
name: foundations-distributed-systems
description: Distributed-systems primitives for CAP/PACELC, FLP, Paxos, Raft, clocks, CRDTs, leases, quorums, and broadcast protocols. Use when designing coordination.
compatibility: Portable core only.
version: "1.1"
last_validated: 2026-07-11
---

# Distributed Systems Foundations

11 canonical primitives for distributed systems theory. Each primitive resolves a specific correctness or availability failure. Primitives are domain-agnostic: the same quorum math that governs database replication governs agent-state synchronisation; the same fencing tokens that prevent split-brain in a storage cluster prevent double-writes in a payment processor.

## When to Apply

**Apply distributed-systems primitives when:**
- 2+ nodes participate in a write or shared state (replication, consensus)
- Network partitions are possible and must be tolerated (CAP/PACELC tradeoff)
- Idempotency, exactly-once, or fencing tokens are needed for safety
- Consistency level is being chosen (linearizable / sequential / causal / eventual)
- Multi-region or multi-AZ deployment with failover/quorum requirements

**Skip and use simpler alternatives when:**
- Single-node system, single writer — none of these primitives apply
- Question is about throughput/latency under load — use foundations-queueing-theory
- Question is about availability/SLO budget — use foundations-reliability-theory
- "We don't have a partition problem" — verify by looking at past incidents; if true, simpler replication patterns suffice
- Eventual-consistency is acceptable AND ordering doesn't matter — use last-writer-wins or CRDTs without consensus
- Strong-consistency demand is a vague preference, not a stated business invariant — challenge it; the cost is high

## Contents

- [Quick Reference](#quick-reference)
- [Primitive Index](#primitive-index)
- [Formal Supporting Theory](#formal-supporting-theory)
- [Misuse Boundaries](#misuse-boundaries)
- [Decision Checklist](#decision-checklist)
- [Anti-Patterns](#anti-patterns)
- [Expert Diagnosis: Reading Symptoms](#expert-diagnosis-reading-symptoms)
- [Consistency Level by Product Feature](#consistency-level-by-product-feature)
- [The Retry/Timeout/Idempotency Triad](#the-retrytimeoutidempotency-triad)
- [Most Outages Are Operational, Not Algorithmic](#most-outages-are-operational-not-algorithmic)
- [Composition Recipes](#composition-recipes)
- [Workflow](#workflow)
- [ASCII Flow](#ascii-flow)
- [Related Skills](#related-skills)
- [Fact-Checking](#fact-checking)

---

## Quick Reference

| # | Primitive | When to Reach For It |
|---|-----------|----------------------|
| 1 | [CAP / PACELC](#1-cappacelc) | Choosing a replication topology or data store trade-off |
| 2 | [FLP Impossibility](#2-flp-impossibility) | Reasoning about whether a consensus protocol can terminate |
| 3 | [Paxos](#3-paxos) | Implementing or auditing a quorum-based agreement protocol |
| 3a | [DAG-BFT Consensus (Shoal++/Mysticeti family)](#3a-dag-bft-consensus) | BFT domains where every-node-proposes throughput and low latency are both required |
| 4 | [Raft](#4-raft) | Leader-based consensus; easier to implement than Paxos |
| 5 | [Vector Clocks / Lamport Timestamps](#5-vector-clocks--lamport-timestamps) | Causal ordering of events across nodes |
| 6 | [CRDTs](#6-crdts) | Conflict-free eventually-consistent data structures |
| 7 | [Idempotency](#7-idempotency) | Exactly-once semantics over at-least-once delivery |
| 8 | [Leases and Fencing](#8-leases-and-fencing) | Split-brain prevention; safe leader handover |
| 9 | [Quorums (NWR)](#9-quorums-nwr) | Tuning read/write consistency vs. availability |
| 10 | [Causal Consistency](#10-causal-consistency) | Preserving happens-before across replicas without serialisability |
| 11 | [Broadcast Protocols](#11-broadcast-protocols) | Gossip, total-order broadcast, atomic broadcast, and inter-cluster consistent broadcast |

---

## Primitive Index

Each primitive has a full playbook in [`assets/templates/distributed-systems/`](assets/templates/distributed-systems/).

| # | Primitive | Failure Mode It Addresses |
|---|-----------|--------------------------|
| 1 | [CAP / PACELC](assets/templates/distributed-systems/01-cap-pacelc.md) | Confusion between consistency, availability, and partition tolerance; latency vs. consistency under normality |
| 2 | [FLP Impossibility](assets/templates/distributed-systems/02-flp-impossibility.md) | Expecting a deterministic consensus protocol to always terminate with one crash faulty node |
| 3 | [Paxos](assets/templates/distributed-systems/03-paxos.md) | Leaderless agreement fragility; unbounded dueling proposers |
| 3a | DAG-BFT Consensus | Throughput/latency tradeoff in Byzantine-adversarial, every-node-proposes settings |
| 4 | [Raft](assets/templates/distributed-systems/04-raft.md) | Unclear log divergence; leader ambiguity during network partition |
| 5 | [Vector Clocks / Lamport Timestamps](assets/templates/distributed-systems/05-vector-clocks-lamport.md) | Wall-clock ordering of events that may be concurrent |
| 6 | [CRDTs](assets/templates/distributed-systems/06-crdts.md) | Merge conflicts in eventually-consistent replicated state |
| 7 | [Idempotency](assets/templates/distributed-systems/07-idempotency.md) | Duplicate delivery of at-least-once messages causing double processing |
| 8 | [Leases and Fencing](assets/templates/distributed-systems/08-leases-fencing.md) | Multiple nodes simultaneously believing they hold a lock (split-brain) |
| 9 | [Quorums (NWR)](assets/templates/distributed-systems/09-quorums.md) | Stale reads or lost writes from uncoordinated replication |
| 10 | [Causal Consistency](assets/templates/distributed-systems/10-causal-consistency.md) | Reads seeing later writes before earlier causally-linked writes |
| 11 | [Broadcast Protocols](assets/templates/distributed-systems/11-broadcast-protocols.md) | Inconsistent replica state from unordered or lossy message delivery; see also DAG-BFT (#3a) for high-throughput ordered broadcast and C3B/Picsou for inter-cluster broadcast |

### 3a. DAG-BFT Consensus

DAG-based Byzantine Fault Tolerant (BFT) consensus separates **data dissemination** from **ordering**: every node proposes blocks into a shared DAG structure, and a separate ordering rule determines the commit sequence. This eliminates the single-leader throughput bottleneck while tolerating Byzantine (arbitrary) faults.

**When to reach for it:** Byzantine-adversarial settings (blockchain/DeFi infrastructure, permissioned ledgers with untrusted validators) where every-node-proposer throughput is required AND low latency must be preserved.

**Kill criteria:** Drop if the workload is crash-fault-only — Raft (#4) is simpler and sufficient. DAG-BFT complexity is justified only when both high throughput and Byzantine fault tolerance are required.

**DAG-BFT lineage:** Narwhal/Tusk (EuroSys 2022, arXiv:2105.11827) introduced the DAG-mempool architecture separating dissemination from ordering; Bullshark (CCS 2022) added zero-overhead ordering on the DAG; Shoal++ (NSDI 2025) redesigned the commit rule for lower latency; Mysticeti (NDSS 2025) reached the 3-message-round lower bound.

**Current state-of-the-art:**
- **Shoal++ (NSDI 2025)**: Redesigned commit rule reduces average commit latency from 10.5 to 4.5 message delays (60% reduction) while matching state-of-the-art DAG throughput. Successor to Bullshark/Shoal. Reference: Arun et al. 2025.
- **Mysticeti-C (NDSS 2025, arXiv:2310.14821)**: First uncertified DAG BFT protocol to achieve the 3-message-round latency lower bound. WAN commit latency 0.5 s at >200 k TPS; 4× latency reduction on Sui production deployment. Fast path variant Mysticeti-FPC weaves certificates into the DAG without additional round trips. Reference: Babel, Chursin, Danezis, Kokoris-Kogias, Sonnino et al. 2025.

**Trap:** DAG-BFT benchmarks compare against prior DAG protocols (Bullshark, Shoal) with industry interest from protocol authors (Aptos Labs, MystenLabs). Claims about throughput/latency are self-reported; verify against your own workload and fault assumptions.

**Cross-reference:** DAG-BFT also functions as a high-throughput ordered broadcast variant — see primitive #11 (Broadcast Protocols).

---

## Formal Supporting Theory

Load [`references/formal-theory-map.md`](references/formal-theory-map.md) when the design depends on model assumptions: asynchronous vs. partially synchronous networks, happens-before and logical clocks, consensus safety/liveness, quorum intersection, broadcast ordering, CRDT semilattices, causal consistency, leases, fencing, or CAP/PACELC trade-off boundaries.

## Misuse Boundaries

Load [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md) before asserting a system is "exactly once", "available and consistent", "leader safe", "eventually consistent", or "CRDT-friendly". It contains production scenarios, anti-patterns, and the checks that prevent common distributed-systems folklore from becoming a false guarantee.

---

## Decision Checklist

- [ ] **Replication topology**: Need to choose between availability and consistency during a partition? → CAP (#1)
- [ ] **Latency vs. consistency under normal conditions**: No partition, but need to understand the latency trade-off? → PACELC (#1)
- [ ] **Consensus termination**: Wondering whether your consensus protocol is guaranteed to terminate with a faulty node? → FLP (#2)
- [ ] **Multi-node agreement without a stable leader**: Need quorum-based agreement tolerant of proposer failures? → Paxos (#3)
- [ ] **Leader-based replicated log**: Need a simpler consensus protocol with strong leader semantics? → Raft (#4)
- [ ] **Causal ordering of events**: Need to determine if event A happened before event B across nodes? → Vector Clocks (#5)
- [ ] **Conflict-free replication**: Need replicas to converge without coordination? → CRDTs (#6)
- [ ] **Exactly-once semantics**: Using at-least-once delivery and need to prevent double processing? → Idempotency (#7)
- [ ] **Lock / primary ownership safety**: Need to prevent split-brain under GC pauses or network partitions? → Leases and Fencing (#8)
- [ ] **Read/write consistency tuning**: Need to choose R + W > N trade-offs for your replica set? → Quorums (#9)
- [ ] **Causal visibility guarantees**: Need to ensure writes are visible in causal order across replicas? → Causal Consistency (#10)
- [ ] **Message dissemination**: Need eventual or total-order delivery to all replicas? → Broadcast Protocols (#11)

---

## Anti-Patterns

| Anti-Pattern | Why It Is Wrong | Fix |
|-------------|-----------------|-----|
| Framing CAP as "pick 2 of 3" | CAP applies only during a network partition; C and A are not binary dials — they are contingent on partition occurrence. Under normal operation all three hold. | State the actual trade-off: during a partition you must choose consistency or availability. Use PACELC to reason about latency trade-offs when there is no partition. |
| Claiming "exactly once" delivery without idempotency | No transport layer provides exactly-once semantics end-to-end. At-least-once with deduplication is the only tractable pattern. Declaring exactly-once in the protocol interface creates a false contract. | Design receivers as idempotent. Use an idempotency key and a deduplicated state store (#7). Combine with at-least-once delivery. |
| Leader-only writes without fencing tokens | A deposed leader that has not yet learned about its demotion (e.g. due to a GC pause or a slow network) can continue to accept writes, causing split-brain corruption. | Issue a monotonically increasing fencing token with each lease (#8). Storage must reject writes with a stale token regardless of what the writer believes. |
| CRDTs with non-commutative operations | CRDTs guarantee convergence only when merge is commutative, associative, and idempotent. Encoding an operation that does not commute (e.g. subtract-then-add vs. add-then-subtract) breaks the convergence guarantee. | Model the state as a semilattice where merge is the join. Use G-Counter, PN-Counter, OR-Set, or LWW-Register depending on the operation set (#6). |
| Quorum reads without quorum write coordination | Reading from R replicas guarantees seeing the latest write only when R + W > N. Relaxing writes to W = 1 while reading from R = 1 means the latest value may never be in the intersection. | Set W and R such that W + R > N (#9). For strong consistency, use W = majority and R = majority. |
| Causal consistency without happens-before tracking | Relying on wall-clock timestamps to enforce causal order causes reads to see writes out of causal sequence when clocks drift. | Attach a vector clock or logical timestamp to every write (#5, #10). Readers use the vector clock to enforce causal order before exposing data. |
| Assuming Paxos/Raft guarantees liveness unconditionally | FLP proves that no deterministic consensus protocol can guarantee both safety and termination in an asynchronous network with even one crash fault. Liveness requires a partial-synchrony assumption. | Acknowledge the partial-synchrony assumption explicitly (#2, #3, #4). Add heartbeat and leader-election timeouts calibrated to the actual network model. |
| Single-leader bottleneck in read-heavy WAN workloads | Multi-Paxos and Raft route all reads through the leader, creating a bottleneck in read-heavy or geographically distributed workloads. | For balanced or read-heavy WAN workloads, consider Pineapple-style any-node serving (NSDI 2025): unifies Multi-Paxos with ABD atomic registers via logical timestamps, allowing any node to serve reads and writes with >50% median latency reduction vs. Raft. Preferred over EPaxos when tail latency matters (EPaxos Revisited, NSDI 2021, showed EPaxos tail latency is 4x worse than Multi-Paxos). Reference: Bantikyan et al. 2025. Kill criteria: drop in write-dominated workloads (extra round on write path) or if leader instability is not the bottleneck. |

---

## Expert Diagnosis: Reading Symptoms

A non-expert asks "which primitive applies?" An expert reads a symptom report and already suspects a short list of mechanisms before opening any code — because most distributed-systems failures announce themselves through a small number of recognizable smells. Use this table to go from a bug report to a hypothesis before instrumenting anything.

| Symptom | What It Smells Like | First Things to Check | Primitive |
|---------|---------------------|------------------------|-----------|
| "We read the old value right after the write succeeded" | Read hit a replica that had not applied the write yet | Is W + R > N? Is the read sticky to the writer's replica or read-your-writes enforced? Did a load balancer route the retry to a different node than the original write? | Quorums (#9), Causal Consistency (#10) |
| "Two nodes both think they're primary" (split-brain) | A lease expired without the storage layer enforcing a fencing token, or a GC/scheduler pause exceeded the lease TTL without the holder noticing | Is the fencing token checked at the resource boundary (storage), not just in application logic? Was there a GC pause, VM stop-the-world, or container CPU throttle around the incident window that exceeds lease duration? | Leases and Fencing (#8) |
| "A write vanished after failover" (phantom write) | The client got an ack before a durable majority had the entry, or the failover promoted a replica that was not guaranteed to hold every committed entry | Does write-ack require majority acknowledgement before returning success? Does leader election enforce the up-to-date-log check (Raft's leader completeness) before granting votes? Or did the client treat a timeout as a definite failure and silently drop a write that actually committed? | Raft/Paxos (#3/#4), Idempotency (#7) |
| "Duplicate charge/email/row after a retry" | At-least-once retry without a stable idempotency key, or the key was regenerated by the server on each attempt instead of supplied by the client | Is the idempotency key client-generated and identical across retries of the same logical operation? Is the check-and-execute atomic (same transaction), not check-then-execute? | Idempotency (#7) |
| "Replicas never converge; state keeps drifting" | A non-commutative operation was modeled as a CRDT, or tombstones/version vectors are growing without garbage collection, or a receive path skipped the `max` merge step | Does every operation in the type's operation set actually commute? Is there a compaction/GC policy for tombstones? Is the vector clock merged (not overwritten) on every receive? | CRDTs (#6), Vector Clocks (#5) |
| "Retries made the outage worse, not better" | Retry storm / thundering herd: no backoff, no jitter, no circuit breaker, and the retries are hitting an already-degraded downstream | See [The Retry/Timeout/Idempotency Triad](#the-retrytimeoutidempotency-triad) below | Idempotency (#7) |
| "It worked in staging, fell over in prod under load" | Usually not a protocol bug — connection-pool exhaustion, a timeout set below real p99 latency, clock skew larger than the lease-safety margin assumed, or a config value (quorum size, TTL) changed without a capacity review | See [Most Outages Are Operational, Not Algorithmic](#most-outages-are-operational-not-algorithmic) below | n/a — operational triage first |
| "Consensus looks stuck / no leader elected" | Could be a genuine network partition with no majority component, or could be a resource-exhaustion symptom (thread pool, disk fsync latency, connection limits) masquerading as a partition to the protocol's heartbeat mechanism | Check host-level resource saturation before assuming a network partition; a node that cannot fsync in time looks identical to a network-partitioned node from the protocol's point of view | FLP (#2), Raft/Paxos (#3/#4) |

**How an expert uses this table**: match the symptom, form one falsifiable hypothesis, check the specific mechanism (not the whole subsystem), and only reach for the primitive's full playbook once the mechanism is confirmed. Treat this as triage, not diagnosis — confirm with logs/traces before changing production behavior.

---

## Consistency Level by Product Feature

Non-experts default to "strong consistency, to be safe" or "eventual consistency, for speed," as if it were one global dial. An expert asks which consistency level the *specific feature* actually needs, because over-provisioning consistency costs latency and availability for no user-visible benefit, and under-provisioning it creates a business-visible defect.

| Product Feature | Consistency Actually Needed | Why | Common Over/Under-Engineering Mistake |
|-----------------|------------------------------|-----|----------------------------------------|
| Bank balance / ledger entry | Linearizable or serializable on the write path | Double-spend or lost debit/credit is a direct financial and compliance failure | Using CRDTs or LWW on a balance field — merge semantics do not express "never go negative" or "never double-apply" |
| Inventory decrement (prevent oversell) | Strong consistency on the decrement (majority-quorum write or single-writer with fencing) | Overselling is visible to the customer and costly to unwind | Eventual consistency without a compensating reconciliation/refund path |
| Shopping cart contents | Causal or eventual (CRDT OR-Set) | Availability matters more than perfect ordering; "union of adds, tag-based remove" is the natural merge | Routing cart writes through a consensus protocol — unnecessary coordination cost |
| Like / view / upvote counters | Eventual (CRDT G-Counter/PN-Counter) | An approximate, eventually-accurate count is acceptable; users do not notice a few seconds of undercount | Coordinating counter increments through a leader — throughput bottleneck for no correctness gain |
| Social feed post + reply ordering | Causal consistency | "Reply before post" is a confusing, user-visible anomaly; global linearizability is not required, only happens-before | Wall-clock timestamp ordering — clock skew silently reorders causally related posts |
| Session / auth token validity check | Read-your-writes on the session, ideally linearizable on the revocation path | A stale "still valid" read on a just-revoked token is a security defect, not a UX nuisance | Caching token validity with a TTL longer than the incident-response requirement for revocation |
| Leaderboard / ranking display | Eventual consistency with periodic reconciliation | Real-time exact ranking is rarely a stated business requirement; coordination cost is high relative to user benefit | Recomputing rank transactionally on every score update |
| Distributed lock / leader election | Linearizable, consensus-backed (Raft/Paxos + fencing) | Lock safety is a correctness invariant (split-brain prevention), not a latency knob | Implementing a "good enough" lock with a TTL and no fencing token |
| Collaborative document editing | CRDT (RGA) or causal broadcast | Low-latency convergence under concurrent edits matters more than a single global order | Serializing all edits through one node — kills the "everyone can type at once" experience |
| Feature flags / config propagation | Eventual, bounded-staleness for normal flags; near-linearizable for a security kill-switch | Most flags tolerate seconds of propagation lag; an incident kill-switch does not | Treating all flags as needing the same propagation SLA — over-engineering routine flags, under-engineering the kill-switch |

**Judgment call**: when a stakeholder states "we need strong consistency" as a preference rather than tracing it to one of the rows above (a stated business invariant — money, inventory, security), challenge it. The cost (latency, availability, engineering complexity) is real; the benefit for most product features is not.

---

## The Retry/Timeout/Idempotency Triad

These three mechanisms must be designed as one decision, not three independent ones — changing any one changes the safety requirement of the other two.

- **Timeout too short relative to real tail latency** → the caller retries a request that was actually still in flight and would have succeeded. This is safe *only if* the receiver is idempotent (#7). Without idempotency, an aggressive timeout is a duplicate-processing generator.
- **Retry without backoff and jitter** → synchronized retries from many callers hit the downstream at the same moment it is already degraded, extending the outage (retry storm / thundering herd). This is the single most common way "adding retries for resilience" makes an incident worse instead of better.
- **Idempotency without a retry policy** → dead weight; nothing is retried, so the dedupe store protects against nothing. Idempotency is a precondition for safe retries, not a substitute for having a retry policy.
- **Rule of thumb**: set timeouts above the observed p99.9 of the operation under normal load (not the p50 or even p99 — tail latency during partial degradation is what triggers spurious timeouts), use exponential backoff with full jitter and a bounded max-attempts, and add a circuit breaker that fails fast once the downstream's error rate crosses a threshold — a fast, clear failure is better than a retry storm that prevents recovery.
- **Cross-check**: the idempotency key's dedupe-store TTL must exceed the maximum possible retry window (last retry attempt + its own timeout), or a very late retry will be treated as a new operation. See primitive #7 for the dedupe-store schema.
- **Expert smell**: "we added retries and things got worse" is almost always missing backoff+jitter+circuit-breaker, not a case for removing retries — the fix is usually to make the retry policy safer, not to remove the safety net.

---

## Most Outages Are Operational, Not Algorithmic

Distributed-systems theory (CAP, FLP, consensus safety proofs) answers what is *possible* — it explains why certain guarantees cannot be had for free. It does not predict where the next incident comes from. Field experience and public postmortems (major cloud providers and infrastructure vendors routinely publish these) repeatedly show that the proximate cause of an outage is configuration drift, capacity exhaustion, a deployment or migration mistake, or human error during an operational change — not a violated algorithmic invariant in Paxos, Raft, or the CAP trade-off itself. The theory is what you use to *diagnose* the incident correctly; it is rarely the site of the actual bug.

Before reaching for a primitive to "fix" an incident, ask:
- Was a config value (quorum size, election/lease timeout, TTL, connection-pool limit) changed recently without a corresponding capacity or timing review?
- Was the failover path (leader election, promotion, DNS/service-discovery cutover) tested under the same load and network conditions as the actual incident, or only tested in isolation at low load?
- Is "consensus looks stuck" actually a network partition, or is it resource exhaustion (disk fsync latency, thread pool saturation, CPU throttling) that looks identical to a partition from the protocol's point of view (see the last row of the [symptom table](#expert-diagnosis-reading-symptoms))?
- Did a routine dependency upgrade (client library, driver, OS, kernel network stack) silently change a timeout default, retry default, or connection-pooling behavior?

This does not mean the primitives in this skill are unnecessary — they are exactly what lets you tell the difference between "our fencing token enforcement has a real gap" (an algorithmic/design bug worth a primitive-level fix) and "the lease TTL was fine but a bad deploy exhausted the connection pool and everything downstream started timing out" (an operational bug that no amount of consensus theory would have prevented). Do the operational triage first; escalate to a primitive-level design change only when the operational explanation is ruled out.

---

## Composition Recipes

### Multi-region writes

**Goal**: Accept writes in multiple regions with bounded staleness and no lost updates.

**Stack**:
1. Quorums (#9) — set W = majority across region replicas; read repair on stale reads.
2. Leases and Fencing (#8) — each region's write coordinator holds a time-bounded lease; fencing token prevents deposed coordinators from writing.
3. Idempotency (#7) — idempotent receivers with per-operation idempotency keys tolerate retries across region failover.
4. Causal Consistency (#10) — vector clocks track happens-before across regions; clients use sticky-session routing to avoid causal anomalies.

**WAN replication latency on the critical path (2025):** For workloads where standard geo-replicated 2PC blocks at the WAN replication boundary (latency dominated by WAN RTT), see Mako (OSDI 2025): speculative 2PC decouples transaction execution from replication, eliminating WAN RTT from client-visible latency while preserving strong consistency with bounded-abort guarantees. Requires idempotent re-execution on speculative abort (#7). Artifact: github.com/makodb/mako. Kill criteria: drop if workload tolerates eventual consistency (use CRDTs instead) or if speculative aborts are frequent (high-contention workloads make speculation expensive).

**RSM-to-RSM links across regions:** Use Cross-Cluster Consistent Broadcast (C3B) from Picsou (OSDI 2025) rather than raw replication bridges or ad-hoc dual-write patterns. C3B provides formal correctness guarantees; see primitive #11 for details.

**When to add CRDTs (#6)**: If the shared state supports a commutative merge (e.g. counters, sets, last-write-wins register), replace quorum coordination with CRDT replication to eliminate coordination overhead entirely.

**Inputs:** N (total replica count across regions), W (write quorum size), R (read quorum size), lease duration (ms), latency SLO for writes (p99 ms), partition tolerance requirement (AZ-failure count), idempotency key schema.
**Rules:** Strong consistency requires W + R > N; set W = ⌊N/2⌋+1 (majority) for write durability; set R = 1 for read-heavy paths if W = N; lease duration must be shorter than the SLO for detecting a deposed coordinator; use CRDT replication when state supports commutative merge and coordination overhead exceeds the latency SLO.
**Outputs:** Recommended (N, W, R) tuple, lease duration, expected write p99 latency per region, maximum AZ-failure tolerance, flag indicating whether CRDT replacement is viable.

---

### Exactly-once receiver

**Goal**: Deliver a message exactly once to application logic despite at-least-once transport semantics.

**Stack**:
1. Idempotent receiver (#7) — application operation is idempotent by design (pure function of inputs, no hidden state mutation).
2. Idempotency key + dedupe store — persistent log of processed keys; reject duplicates before executing.
3. At-least-once delivery — transport retries until acknowledged; the receiver's idempotency makes retries safe.

**When to add Raft (#4)**: If the dedupe store itself must be replicated, use a Raft-backed key-value store so the dedupe log survives node failures without split-brain.

**Inputs:** Idempotency key schema (operation type + client ID + sequence number), dedupe store type (in-memory / persistent / replicated), at-least-once transport (retry count, backoff policy), expected duplicate rate (%), required exactly-once guarantee scope (single node vs. cluster).
**Rules:** Receiver must be a pure function of its inputs with no hidden state mutations; every operation must be looked up in the dedupe store before execution; duplicate = same key → return cached result, do not re-execute; dedupe store must outlive the longest possible retry window; if the dedupe store is replicated, use Raft-backed KV so the log is durable across node failures.
**Outputs:** Idempotency key format specification, dedupe store schema (key → result + TTL), confirmation that the receiver is side-effect-free, recommended dedupe TTL relative to retry window, decision on whether Raft-backed replication is required.

---

### Split-brain prevention

**Goal**: Prevent two nodes from simultaneously believing they are the primary/leader.

**Stack**:
1. Lease tokens (#8) — primary holds a time-bounded lease; all writes require a valid lease.
2. Fencing tokens (#8) — monotonically increasing integer issued at each lease grant; storage layer rejects writes with a token lower than the maximum seen.
3. Paxos (#3) or Raft (#4) termination — after a partition heals, run a full election round before granting a new lease; never grant a new lease without quorum acknowledgement.

**When to add Quorums (#9)**: For storage nodes that cannot run Paxos/Raft, enforce W > N/2 so no two disjoint quorums can each accept a write.

**Inputs:** N (cluster node count), AZ layout (nodes per AZ), lease duration (ms), fencing token current value, election timeout range (ms), network round-trip time estimate (ms), write latency SLO (p99 ms).
**Rules:** Quorum = ⌊N/2⌋+1; a new lease may only be granted after a full election round with quorum acknowledgement; fencing token must be monotonically increasing and stored durably; storage must reject any write carrying a token ≤ max_seen_token; lose any AZ → remaining nodes must still meet quorum for the cluster to accept writes; for non-Raft storage enforce W > N/2.
**Outputs:** Quorum size, recommended AZ node distribution, fencing token increment policy, write p99 latency estimate (network RTT + leader processing), maximum single-AZ failure tolerance, flag indicating whether quorum enforcement alone is sufficient or Paxos/Raft is required.

**Worked example:** 5-node Raft cluster, single-AZ failure tolerance. Quorum = ⌊5/2⌋+1 = 3. Deploy: AZ-A holds 2 nodes, AZ-B holds 2, AZ-C holds 1. Lose AZ-A → 3 nodes alive → quorum holds, cluster available. Lose AZ-B + AZ-C → 2 nodes alive → below quorum, cluster unavailable (correct: safety preserved). Fencing token increments on each new lease grant; a deposed AZ-A leader resuming after a GC pause sends token=4, storage has seen token=5, write rejected. Write latency budget: 1 RTT leader→client ack waits for fastest 2 followers: p50 = 8 ms, p99 = 25 ms, plus 5 ms leader processing → write p99 ≈ 30 ms. Shrinking to a 3-node cluster (quorum = 2) drops write p99 to ~13 ms but loses tolerance for any two-node AZ failure — exactly the availability/latency trade-off PACELC quantifies.

---

### Gossip-based state dissemination

**Goal**: Propagate cluster membership or soft state to all nodes with eventual convergence and no single point of failure.

**Stack**:
1. Gossip / epidemic broadcast (#11) — each node periodically selects k random peers and exchanges state digests; convergence is O(log N) rounds.
2. CRDTs (#6) — model disseminated state as a CRDT (e.g. OR-Set for membership) so merge at any node is safe and idempotent regardless of message order.
3. Vector Clocks (#5) — attach a vector clock to gossip payloads to detect and discard stale updates.

**Inputs:** N (cluster node count), gossip fan-out k (peers per round), state model (membership list, soft metric, counter, set), update frequency (updates/s), acceptable convergence time (ms or rounds), network partition tolerance requirement.
**Rules:** Convergence time ≈ O(log N) gossip rounds; each round selects k peers uniformly at random; state must be modelled as a CRDT (G-Counter, OR-Set, LWW-Register, or PN-Counter) so any merge order is safe; attach a vector clock to each payload; discard a payload if its vector clock is dominated by the node's current clock.
**Outputs:** Recommended gossip fan-out k for target convergence time, CRDT type for the disseminated state, vector clock schema (node ID → logical timestamp), expected convergence rounds and wall-clock time at given N.

---

### AI-agent pipeline: idempotent tool calls and shared CRDT state

**Goal**: Build a multi-agent pipeline where tool calls are safe to retry (exactly-once side effects) and shared document/workspace state converges without coordination locks.

**Stack**:
1. **Idempotency (#7)** — assign a deterministic idempotency key to every agent tool call (derived from `agent_id + step_id + input_hash`). A durable-execution runtime (Temporal, Restate) journals the key before execution and replays the journal on crash, making retries safe without application-level dedupe code.
2. **Leases and Fencing (#8)** — when an agent must hold exclusive control over a resource (e.g. a file section or an external API quota slot), issue a time-bounded lease with a fencing token. The resource layer rejects tool calls carrying a stale token, preventing a crashed-and-recovered agent from double-applying writes.
3. **CRDTs (#6)** — model the shared workspace (document, task list, code buffer) as a CRDT (RGA for rich text, OR-Set for task sets, LWW-Register for key-value slots). Agents write as CRDT peers; strong eventual consistency guarantees convergence across concurrent edits without a consensus round. Production implementations (2026): Yjs (RGA) remains the ecosystem-dominant default; Automerge (now on its 3.x line, with the Peritext rich-text algorithm and a built-in version-history model) trades some performance for document branching/merge/attribution as a product feature; Loro (Rust-based) is a newer entrant — verify production maturity before committing to it over Yjs/Automerge.

**Kill criteria for CRDTs:** if the shared state has non-commutative invariants (e.g. a unique-name constraint, a capacity limit, a transaction balance), replace CRDTs with consensus-backed coordination (#3/#4) for those invariants. CRDTs are correct only when merge semantics match intended semantics.

**Kill criteria for durable execution:** if tool calls are pure reads with no side effects, no idempotency infrastructure is needed — the retry is naturally safe.

**Inputs:** Agent count, tool call rate (calls/s), durable-execution backend (Temporal/Restate/custom), shared state type (text, task list, KV), CRDT type, lease duration (ms), expected retry rate (%).
**Rules:** Idempotency key must be derived deterministically from inputs, not from server-side randomness; journal the key before execution, not after; dedupe TTL ≥ max retry window; CRDT merge must be commutative for all operations in the operation set; fencing token must be stored durably and enforced at the resource boundary.
**Outputs:** Idempotency key schema, journal/dedupe backend choice, CRDT type for each shared state segment, lease duration recommendation, flag indicating which invariants (if any) require consensus instead of CRDT.

---

### Disaggregated LLM inference

**Goal**: Serve LLM inference requests meeting both Time-To-First-Token (TTFT) and Inter-Token Latency (ITL) SLOs simultaneously — which co-located deployments cannot independently optimise.

**Background**: Prefill (prompt processing) is compute-intensive and batching-unfriendly; decode (token generation) is memory-bandwidth-bound. Co-location forces a trade-off between TTFT and ITL that cannot be resolved without disaggregation. DistServe (OSDI 2024, arXiv:2401.09670) demonstrated 7.4× goodput improvement and 12.6× tighter SLO vs. co-located state-of-the-art. Production adoption: Meta, LinkedIn, Mistral, Hugging Face via vLLM.

**Stack**:
1. **Idempotency (#7)** — KV-cache transfer between prefill and decode pools may be retried; receiving decode workers must handle duplicate cache chunks without re-processing.
2. **Quorums (#9)** — route inference requests across prefill/decode pools using replica-aware scheduling; quorum math governs minimum prefill pool availability for write-ahead KV-cache commits.
3. **Broadcast Protocols (#11)** — gossip KV-cache state and load metrics across decode replicas; enables any decode worker to serve continuation tokens without a single scheduler bottleneck.

**Kill criteria:** Drop disaggregation if workload is small-batch, latency-insensitive, or GPU pool is too small to split (co-location wins below ~4 GPUs per pool). Include whenever TTFT and ITL are independently SLO-constrained.

**Inputs:** Prefill pool size (GPU count), decode pool size (GPU count), TTFT SLO (ms p99), ITL SLO (ms p99), KV-cache chunk size (MB), network bandwidth between pools (Gbps), expected duplicate prefill rate (%).
**Rules:** Prefill and decode pools must be independently scalable; KV-cache transfer is the latency-critical path — optimise network bandwidth before adding more GPUs; dedupe store TTL must exceed maximum prefill retry window; gossip fan-out for decode replicas ≥ 2 (O(log N) convergence).
**Outputs:** Recommended prefill/decode pool split ratio, KV-cache transfer protocol (chunk size, retry policy, idempotency key schema), decode replica gossip fan-out, expected TTFT and ITL p99 at given pool sizes.

---

## Workflow

1. Identify the system failure mode (split-brain, stale reads, duplicate processing, causal anomaly, consensus termination).
2. Use the [Decision Checklist](#decision-checklist) to map failure mode → primitive.
3. Open the per-primitive playbook in [`assets/templates/distributed-systems/`](assets/templates/distributed-systems/) for the definition, inputs, outputs, failure modes, and worked example.
4. For multi-failure scenarios, use the [Composition Recipes](#composition-recipes) to stack primitives.
5. Check the [Anti-Patterns](#anti-patterns) table before shipping the design.

---

## ASCII Flow

```text
Distributed-system correctness problem
  -> Name failure mode: partition, stale read, duplicate work, causal anomaly, consensus risk
  -> Identify topology, fault model, and consistency requirement
  -> Select primitive: consensus, replication, CRDT, clock, lease, idempotency, or gossip
  -> Check assumptions against latency, partition, and failure behavior
     +-- assumptions break -> weaken guarantee or change architecture
     +-- assumptions hold -> define protocol and invariants
  -> Test with fault injection and anti-pattern review
```

---

## Navigation

- Per-primitive playbooks: [`assets/templates/distributed-systems/`](assets/templates/distributed-systems/) (one file per primitive)
- Composition guide: [`assets/templates/distributed-systems/README.md`](assets/templates/distributed-systems/README.md)
- Domain-agnostic primitives overview: [`references/primitives-overview.md`](references/primitives-overview.md)
- Formal theory map: [`references/formal-theory-map.md`](references/formal-theory-map.md)
- Patterns, scenarios, and traps: [`references/patterns-scenarios-traps.md`](references/patterns-scenarios-traps.md)
- Sources: [`data/sources.json`](data/sources.json)

---

## Related Skills

_Consumer skills that apply these primitives in domain-specific recipes will link here when ready._

- [`software-architecture-design`](../software-architecture-design/SKILL.md) — system design patterns; applies replication and consensus primitives
- [`data-streaming`](../data-streaming/SKILL.md) — exactly-once delivery, log compaction, partition assignment
- [`ops-devops-platform`](../ops-devops-platform/SKILL.md) — cluster coordination, leader election, health checks
- `agents-subagents` — multi-agent state synchronisation, task deduplication
- [`software-realtime`](../software-realtime/SKILL.md) — low-latency replication, causal ordering for real-time collaboration

---

## Fact-Checking

- Verify protocol correctness claims against primary papers (Lamport 1978/1998, FLP 1985, Raft 2014) before treating them as design guarantees.
- CAP and PACELC quantify trade-offs; they do not specify protocols. Always verify the specific system's consistency model against its documentation.
- Source links and verified dates are in [`data/sources.json`](data/sources.json).
- If web access is unavailable, mark runtime-specific benchmark claims as unverified.
- Never synthesise a protocol's formal safety or liveness properties from memory: name the primary paper, the failure and timing model assumed, and explicitly state whether safety or liveness is the claimed property.
- Primary sources: Lamport (1978 logical clocks, 1998 Paxos), Fischer-Lynch-Paterson (1985 FLP), Brewer (2000 CAP conjecture), Gilbert & Lynch (2002 CAP proof), Ongaro & Ousterhout (2014 Raft), Shapiro et al. (2011 CRDTs), DeCandia et al. (2007 Dynamo), Corbett et al. (2013 Spanner), Kleppmann (Designing Data-Intensive Applications).
- **Automated safety proofs (2025):** For formal verification of consensus protocols, Basilisk (OSDI 2025 Best Paper, Jay Lepreau Award) automates inductive invariant synthesis via Provenance Invariants derived by Atomic Sharding static analysis — applicable when verifying custom Paxos/Raft variants (#3, #4). Proves safety only, not liveness. Artifact available at github.com/GLaDOS-Michigan/Basilisk. Reference: Zhang et al. 2025.
- **CI-integrated TLA+ simulation (2025):** For production consensus systems, Smart Casual Verification (NSDI 2025) provides a CI-integrated TLA+ simulation methodology that found 6 bugs (5 safety, 1 liveness) in CCF's Raft variant without full formal proof. Applicable to any system using Raft (#4) or Paxos (#3) variants. Finds violations probabilistically, not exhaustively — escalate to Basilisk for exhaustive proof. Reference: Howard et al. 2025 (arXiv:2406.17455).
- **Modular TLA+ conformance testing (2025):** For production distributed transaction protocols, Schultz & Demirbas (VLDB 2025) demonstrate a pattern of modular TLA+ specification + automated conformance testing of the production implementation that closes the spec-to-code gap (#3, #7, #10). Novel permissiveness analysis verifies a protocol is not overly conservative in granting concurrency. Artifact at github.com/mongodb-labs/vldb25-dist-txns.
- **2026-07-11 verification pass:** All 2024–2025 paper citations in this skill (Shoal++, Mysticeti, Narwhal/Tusk, Basilisk, Picsou, Mako, Pineapple, Smart Casual Verification, Schultz & Demirbas/MongoDB, DistServe, Eiger-PORT+) were checked against publisher (USENIX/NDSS/VLDB) and arXiv records for author list, venue, and headline claims — no fabrications found. Kleppmann chapter references were checked against the actual DDIA table of contents (ch.5 Replication, ch.8 The Trouble with Distributed Systems, ch.9 Consistency and Consensus, ch.11 Stream Processing) and are correctly mapped. CRDT library reference updated: Automerge has moved to its 3.x line (Peritext rich-text, columnar storage) since the 2.0 reference; Yjs remains the ecosystem-dominant default; Loro is a newer Rust-based entrant whose production maturity should be independently verified before adoption. Benchmark numbers (e.g. Shoal++ 10.5→4.5 message delays, Mysticeti 0.5s WAN commit at >200k TPS, Picsou 24x, Mako's TPC-C throughput) remain self-reported by the paper authors — treat as directional, verify against your own workload before using as a capacity-planning input.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
