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
**Goal**: Accept writes in multiple regions under explicit read/write guarantees and a stated fault model. Quorum intersection, leases and causal order alone do not establish bounded staleness or prevent lost updates.
**Stack**: Quorums (#9) + Leases/Fencing (#8) + Idempotency (#7) + Causal Consistency (#10).
**Add CRDTs (#6)** if state supports a commutative merge.

### Exactly-once receiver
**Goal**: One committed business effect per operation over at-least-once transport (idempotent receiver + dedupe).
**Stack**: Idempotent receiver (#7) + dedupe store. Atomically commit the operation key, payload binding, business mutation and result in one receiver transaction; acknowledge after commit. External effects require destination-enforced idempotency or a named atomic coordination boundary. Replicating the dedupe store alone does not make it atomic with the business effect.

### Split-brain prevention
**Goal**: Prevent stale owners from committing effects at the protected resource, even if they still believe they are primary.
**Stack**: Consensus-backed ownership (#3/#4) + lease expiry + resource-enforced fencing (#8). Liveness requires the protocol's timing and quorum assumptions.

### Gossip-based state dissemination
**Goal**: Propagate membership or soft state to all nodes eventually.
**Stack**: Gossip broadcast (#11) + CRDTs (#6) + Vector Clocks (#5).

---

## Related

- Full composition recipes: [`../../../references/composition-recipes.md`](../../../references/composition-recipes.md)
- Primitives overview: [`../../../references/primitives-overview.md`](../../../references/primitives-overview.md)
- Sources: [`../../../data/sources.json`](../../../data/sources.json)
