# Distributed Systems Primitives — Playbook Guide

11 domain-agnostic distributed systems primitives. Each file is a standalone playbook (definition, when to use, inputs, outputs, failure modes, worked example, sources). Cross-cutting guidance — primitives overview, anti-patterns, decision checklist — lives in [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md).

---

## Primitives

| # | File | Failure Mode It Addresses |
|---|------|--------------------------|
| 1 | [01-cap-pacelc.md](01-cap-pacelc.md) | Confusion about consistency/availability during a partition; latency vs. consistency under normality |
| 2 | [02-flp-impossibility.md](02-flp-impossibility.md) | Expecting deterministic consensus to always terminate with a crash-faulty node |
| 3 | [03-paxos.md](03-paxos.md) | Multi-proposer livelock; unclear quorum-based agreement |
| 4 | [04-raft.md](04-raft.md) | Log divergence; leader ambiguity after partition |
| 5 | [05-vector-clocks-lamport.md](05-vector-clocks-lamport.md) | Wall-clock ordering failures; causal anomalies |
| 6 | [06-crdts.md](06-crdts.md) | Merge conflicts in eventually-consistent replicated state |
| 7 | [07-idempotency.md](07-idempotency.md) | Duplicate processing from at-least-once delivery |
| 8 | [08-leases-fencing.md](08-leases-fencing.md) | Split-brain under GC pauses or slow networks |
| 9 | [09-quorums.md](09-quorums.md) | Stale reads or lost writes from uncoordinated replication |
| 10 | [10-causal-consistency.md](10-causal-consistency.md) | Reads seeing later writes before causally prior writes |
| 11 | [11-broadcast-protocols.md](11-broadcast-protocols.md) | Inconsistent replica state from unordered or lossy message delivery |

---

## Composition Stacks

### Multi-region writes
**Goal**: Accept writes in multiple regions with bounded staleness and no lost updates.
**Stack**: Quorums (#9) + Leases/Fencing (#8) + Idempotency (#7) + Causal Consistency (#10).
**Add CRDTs (#6)** if state supports a commutative merge.

### Exactly-once receiver
**Goal**: At-most-once application logic over at-least-once transport.
**Stack**: Idempotent receiver (#7) + dedupe store. **Add Raft (#4)** if the dedupe store must be replicated.

### Split-brain prevention
**Goal**: Prevent two nodes simultaneously believing they are primary.
**Stack**: Lease tokens (#8) + Fencing tokens (#8) + Paxos (#3) or Raft (#4) termination.

### Gossip-based state dissemination
**Goal**: Propagate membership or soft state to all nodes eventually.
**Stack**: Gossip broadcast (#11) + CRDTs (#6) + Vector Clocks (#5).

---

## Related

- Full composition recipes: [`../../../../SKILL.md#composition-recipes`](../../../../SKILL.md)
- Primitives overview: [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md)
- Sources: [`../../../data/sources.json`](../../../data/sources.json)
