# Research Frontier (2021–2026 protocols)

Load this only when a design is actually choosing among research protocols: Byzantine settings, WAN consensus latency, cross-cluster replication, ordering fairness, or encrypted CRDTs. For crash-fault systems inside one organisation, the playbooks in [`../assets/templates/distributed-systems/`](../assets/templates/distributed-systems/) are enough.

**Evidence caveat for everything below.** Benchmark numbers are self-reported by the authors against the baselines they chose, and several authors have commercial interest in the protocol. Treat them as directional; test against your own workload and fault model. Citation details are recorded in [`../data/sources.json`](../data/sources.json); the figures were not re-checked in the latest review, so confirm them against the paper before quoting.

## Byzantine consensus: DAG-BFT

DAG-based BFT separates **data dissemination** from **ordering**: every node proposes blocks into a shared DAG, and a separate rule fixes the commit order. This removes the single-leader throughput bottleneck while tolerating Byzantine faults.

- **Use when** validators are mutually untrusted (permissioned ledgers, blockchain infrastructure) and both every-node-proposes throughput and low latency are required.
- **Do not use** for crash-fault-only workloads; Raft is simpler and sufficient.
- **Lineage:** Narwhal/Tusk (EuroSys 2022, arXiv:2105.11827) introduced the DAG mempool; Bullshark (CCS 2022) added zero-overhead ordering; Shoal++ (NSDI 2025) reports average commit latency cut from 10.5 to 4.5 message delays; Mysticeti-C (NDSS 2025, arXiv:2310.14821) reports reaching the 3-message-round lower bound, 0.5 s WAN commit at >200k TPS.
- **Trusted single-datacentre shortcut:** SwitchBFT (NSDI 2026) uses packet source authentication and programmable switches to drop signatures on the fault-free path. The trust assumption is the whole design; it does not transfer to WAN, multi-tenant or public-validator settings.
- **Ordering fairness is a separate property from agreement.** Consensus guarantees replicas agree on an order, not that the order is fair; a leader can front-run without violating safety or liveness. Equal Opportunity (OSDI 2026) formalises this and uses bounded randomness (a secret random oracle on trusted hardware or threshold VRFs) to mitigate ordering attacks.

## WAN consensus latency

- **Leaderless reads/writes:** EPaxos Revisited (NSDI 2021) found EPaxos tail latency more than 4× worse than Multi-Paxos. Pineapple (NSDI 2025) unifies Multi-Paxos with ABD registers so any node serves reads and writes, reporting >50% median latency reduction vs Raft in balanced workloads. It adds a round on writes; skip it for write-dominated workloads. Details: [`03-paxos.md`](../assets/templates/distributed-systems/03-paxos.md).
- **Retrofit a fast path:** Jetpack (OSDI 2026) adds a 1-RTT fast path to an *existing* protocol and reports up to 60% lower average commit latency across six systems. Its stated hazard applies to any home-grown fast path: promises made during stable operation can silently become invalid across a view change.
- **Speculative geo-2PC:** Mako (OSDI 2025) decouples transaction execution from WAN replication to remove WAN RTT from client-visible latency, with bounded aborts. It requires idempotent re-execution on speculative abort. Skip it under high contention.

## Cross-cluster replication

Cross-Cluster Consistent Broadcast (C3B) from Picsou (OSDI 2025, arXiv:2312.11029) gives formal guarantees for RSM-to-RSM message exchange, replacing ad-hoc bridges and dual writes. Details and kill criteria: [`11-broadcast-protocols.md`](../assets/templates/distributed-systems/11-broadcast-protocols.md).

## Encrypted collaboration over CRDTs

End-to-end encryption conflicts with server-side CRDT merging. Acumen (OSDI 2026) provides strong snapshot consistency over encrypted CRDTs using cryptographic accumulators and secure tombstone garbage collection; it was evaluated at 25 concurrent typists.

## Verification research

Basilisk (OSDI 2025), Smart Casual Verification (NSDI 2025) and modular TLA+ conformance testing (VLDB 2025) are summarised in [`formal-theory-map.md`](formal-theory-map.md#verification-reference-implementations). For choosing a verification tool at all, use [`foundations-formal-methods`](../../foundations-formal-methods/SKILL.md), which owns tool selection.
