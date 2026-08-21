---
description: Domain-agnostic overview of 11 distributed-systems primitives with anti-patterns and a decision checklist.
last_verified: 2026-08-14
status: stable
---

# Distributed Systems Primitives Overview

## Table of Contents

- [Why These Primitives Matter](#why-these-primitives-matter)
- [Primitive Index](#primitive-index)
- [Anti-Patterns by Domain](#anti-patterns-by-domain)
- [Decision Checklist](#decision-checklist)
- [Sources](#sources)

---

## Why These Primitives Matter

Distributed systems fail in predictable ways. Clocks drift, networks partition, nodes crash and restart. Without explicit models for ordering, agreement, and conflict resolution, these failures produce silent data corruption, split-brain, duplicate processing, or causality violations that are expensive to detect and fix. The 11 primitives below are the formal vocabulary for reasoning about these failure modes before they reach production.

| Failure Mode | Primitive | What Goes Wrong Without It |
|-------------|-----------|---------------------------|
| Network partition forces a consistency/availability choice | CAP / PACELC (#1) | Unexpected data loss or service unavailability, depending on which side of the partition the system chose implicitly |
| Consensus protocol hangs with a crashed node | FLP Impossibility (#2) | Protocol is stuck waiting for a response that will never come |
| Multiple proposers fight for leadership indefinitely | Paxos (#3) | Livelock — no value is ever decided |
| Log divergence across replicas after a partition heals | Raft (#4) | Replicas apply conflicting log entries; state diverges silently |
| Events on different nodes cannot be ordered causally | Vector Clocks (#5) | Wall-clock timestamps produce incorrect causal ordering; conflict resolution is broken |
| Concurrent writes to replicated state produce merge conflicts | CRDTs (#6) | Manual conflict resolution required; human errors introduce inconsistencies |
| At-least-once delivery causes duplicate side effects | Idempotency (#7) | Double charges, double sends, double inserts |
| Deposed leader continues to write after demotion | Leases and Fencing (#8) | Two nodes simultaneously believe they are primary; split-brain corruption |
| Stale reads from replicas not yet up to date | Quorums (#9) | Read returns a value that has already been overwritten |
| Later write visible before causally earlier write | Causal Consistency (#10) | A reply appears before the original message; a deletion appears before the item |
| Replicas apply the same updates in different orders | Broadcast Protocols (#11) | Replicated state machines diverge; total-order invariants violated |

---

## Primitive Index

| # | Primitive | Failure Mode | Primary Domains |
|---|-----------|-------------|-----------------|
| 1 | [CAP / PACELC](../assets/templates/distributed-systems/01-cap-pacelc.md) | Confusion about consistency/availability during a partition; latency vs. consistency under normality | Database replication, multi-region architecture, data stores |
| 2 | [FLP Impossibility](../assets/templates/distributed-systems/02-flp-impossibility.md) | Expecting deterministic consensus to always terminate | Consensus protocol design, distributed lock services |
| 3 | [Paxos](../assets/templates/distributed-systems/03-paxos.md) | Multi-proposer livelock; unclear quorum protocol | Distributed databases, configuration management, lease services |
| 4 | [Raft](../assets/templates/distributed-systems/04-raft.md) | Log divergence, leader ambiguity after partition | Replicated state machines, etcd, CockroachDB, TiKV |
| 5 | [Vector Clocks / Lamport Timestamps](../assets/templates/distributed-systems/05-vector-clocks-lamport.md) | Wall-clock ordering failures; causal anomalies | Event sourcing, multi-master replication, distributed tracing |
| 6 | [CRDTs](../assets/templates/distributed-systems/06-crdts.md) | Merge conflicts in eventually-consistent state | Collaborative editing, shopping carts, presence indicators |
| 7 | [Idempotency](../assets/templates/distributed-systems/07-idempotency.md) | Duplicate processing from at-least-once delivery | Payments, email, webhooks, message queues |
| 8 | [Leases and Fencing](../assets/templates/distributed-systems/08-leases-fencing.md) | Split-brain under GC pauses or slow networks | Distributed locks, primary election, storage coordination |
| 9 | [Quorums (NWR)](../assets/templates/distributed-systems/09-quorums.md) | Stale reads or lost writes | Cassandra, DynamoDB, Riak, custom replication layers |
| 10 | [Causal Consistency](../assets/templates/distributed-systems/10-causal-consistency.md) | Causal anomalies across replicas | Real-time collaboration, social feeds, messaging systems |
| 11 | [Broadcast Protocols](../assets/templates/distributed-systems/11-broadcast-protocols.md) | Unordered or lossy replica updates | Gossip-based membership, replicated state machines, pub-sub |

---

## Anti-Patterns by Domain

### Database Replication

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Claiming a database is "CP" or "AP" without specifying the failure mode | CAP applies only under network partition | State the specific consistency model (linearisability, causal, read-your-writes) and the specific availability guarantee |
| Using wall-clock timestamps for conflict resolution | Clocks drift; later timestamp does not imply later causation | Use vector clocks (#5) or Last-Write-Wins with a monotonic logical clock |
| Setting W = 1 for writes and R = 1 for reads | R + W = 2 ≤ N; stale reads are possible | Set W + R > N (#9) |

### Payments and Messaging

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Processing a payment without an idempotency key | Network retry causes double charge | Add idempotency key at the API boundary; deduplicate in the receiver (#7) |
| At-most-once delivery for critical messages | Dropped messages cause lost events | Use at-least-once delivery with idempotent receivers (#7) |
| Relying on message queue exactly-once semantics | No queue provides true end-to-end exactly-once | Design the consumer as idempotent; treat the queue as at-least-once (#7) |

### Distributed Locking and Leadership

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Holding a distributed lock without a TTL | Lock holder crash leaves lock permanently held | Use a time-bounded lease (#8); require renewal before expiry |
| Trusting the lock holder without a fencing token | GC pause or slow network allows a deposed holder to write | Storage layer enforces monotonic fencing tokens (#8) |
| Leader election without quorum acknowledgement | Two nodes both win an election in a split partition | Require majority quorum to confirm a new leader (#3, #4) |

### Real-Time Collaboration

| Anti-Pattern | Diagnosis | Fix |
|-------------|-----------|-----|
| Last-write-wins without a causal clock | Concurrent edits silently overwrite each other | Use CRDTs (#6) for conflict-free merge or vector clocks (#5) for causal ordering |
| Sticky session without happens-before enforcement | Client switches replica mid-session and reads stale data | Enforce causal consistency with sticky sessions or causal tokens (#10) |

---

## Decision Checklist

- [ ] **Partition behaviour**: What happens to your service when a network partition occurs? Which side is primary? → CAP (#1)
- [ ] **Normal-operation latency**: Under no partition, is extra latency acceptable to achieve stronger consistency? → PACELC (#1)
- [ ] **Consensus termination**: Can your consensus protocol block indefinitely if a node crashes? → FLP (#2) — add partial-synchrony timeouts
- [ ] **Agreement without stable leader**: Multiple nodes proposing values that need a single agreed outcome → Paxos (#3)
- [ ] **Replicated log with strong leader**: Single leader appends to a replicated log → Raft (#4)
- [ ] **Event ordering across nodes**: Determining whether event A caused event B → Vector Clocks (#5)
- [ ] **Conflict-free eventual consistency**: Shared mutable state that must converge without coordination → CRDTs (#6)
- [ ] **At-least-once delivery with side effects**: Message processing that must not be applied twice → Idempotency (#7)
- [ ] **Primary safety under failure**: Preventing two nodes from writing simultaneously → Leases and Fencing (#8)
- [ ] **Read/write consistency tuning**: Choosing R and W for a replica set → Quorums (#9)
- [ ] **Causal ordering guarantees**: Ensuring a read sees all causally prior writes → Causal Consistency (#10)
- [ ] **State dissemination to all nodes**: Propagating cluster membership or soft state → Broadcast Protocols (#11)

---

## Sources

Primary papers are the canonical evidence tier. Secondary sources (blog posts, conference talks) are useful for implementation patterns but not for formal guarantees.

- Lamport 1978 — logical clocks and happens-before. [lamport.azurewebsites.net/pubs/time-clocks.pdf](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- Fischer, Lynch, Paterson 1985 — FLP impossibility. [doi.org/10.1145/3149.214121](https://doi.org/10.1145/3149.214121)
- Lamport 1998 — Paxos. [lamport.azurewebsites.net/pubs/lamport-paxos.pdf](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf)
- Brewer 2000 — CAP conjecture. [people.eecs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf](https://people.eecs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf)
- Gilbert & Lynch 2002 — CAP proof. [doi.org/10.1145/564585.564601](https://doi.org/10.1145/564585.564601)
- Ongaro & Ousterhout 2014 — Raft. [raft.github.io/raft.pdf](https://raft.github.io/raft.pdf)
- Shapiro et al. 2011 — CRDTs. [doi.org/10.1007/978-3-642-24550-3_29](https://doi.org/10.1007/978-3-642-24550-3_29)
- DeCandia et al. 2007 — Dynamo. [doi.org/10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)
- Abadi 2012 — PACELC. [doi.org/10.1109/MC.2012.33](https://doi.org/10.1109/MC.2012.33)
- Corbett et al. 2013 — Spanner. [doi.org/10.1145/2491245](https://doi.org/10.1145/2491245)
- Lakshman & Malik 2010 — Cassandra. [doi.org/10.1145/1773912.1773922](https://doi.org/10.1145/1773912.1773922)
- Kleppmann 2017 — Designing Data-Intensive Applications. [dataintensive.net](https://dataintensive.net/)
- Birman 2007 — Gossip protocols. [doi.org/10.1145/1317379.1317382](https://doi.org/10.1145/1317379.1317382)
- Chandra, Griesemer, Redstone 2007 — Paxos Made Live. [doi.org/10.1145/1281100.1281103](https://doi.org/10.1145/1281100.1281103)
