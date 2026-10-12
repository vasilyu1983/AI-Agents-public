# Research Frontier (BFT and WAN consensus)

Load this only when a design is choosing among research protocols: Byzantine settings, WAN consensus latency, cross-cluster replication, ordering fairness, or encrypted CRDTs. For crash-fault systems inside one organisation, the playbooks in [`../assets/templates/distributed-systems/`](../assets/templates/distributed-systems/) are enough.

Author-reported numbers are directional and not carried here. Read the paper, and test against your own workload and fault model, before relying on a claim. Citations are in [`../data/sources.json`](../data/sources.json).

- **DAG-BFT** (validators mutually untrusted): Narwhal/Tusk (EuroSys 2022, arXiv:2105.11827), Bullshark (CCS 2022), Shoal++ (NSDI 2025), Mysticeti (NDSS 2025, arXiv:2310.14821). Do not use for crash-fault-only workloads; Raft is simpler.
- **Trusted single-datacentre BFT shortcut:** SwitchBFT (NSDI 2026). The trust assumption is the whole design; it does not transfer to WAN or multi-tenant settings.
- **Ordering fairness is a separate property from agreement.** Consensus fixes an order, not a fair one; a leader can front-run without violating safety or liveness. Equal Opportunity (OSDI 2026) formalises this.
- **WAN latency:** EPaxos Revisited (NSDI 2021), Pineapple (NSDI 2025, see [`03-paxos.md`](../assets/templates/distributed-systems/03-paxos.md)), Jetpack (OSDI 2026), Mako (OSDI 2025). A home-grown fast path can silently invalidate promises across a view change.
- **Cross-cluster replication:** Picsou / C3B (OSDI 2025, arXiv:2312.11029); see [`11-broadcast-protocols.md`](../assets/templates/distributed-systems/11-broadcast-protocols.md).
- **Encrypted CRDTs:** Acumen (OSDI 2026).
- **Verification research:** see [`formal-theory-map.md`](formal-theory-map.md#verification-reference-implementations); tool choice belongs to [`foundations-formal-methods`](../../foundations-formal-methods/SKILL.md).
