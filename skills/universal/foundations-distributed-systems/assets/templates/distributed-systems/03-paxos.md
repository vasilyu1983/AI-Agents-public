# Primitive 3: Paxos

**Source**: Lamport 1998; Chandra, Griesemer, Redstone 2007 (Paxos Made Live).

---

## Definition

**Paxos** is a family of consensus protocols that allow a set of processes to agree on a single value despite message loss and process crashes, as long as a majority of processes remain reachable.

**Classic Paxos** (single-decree) proceeds in two phases:

**Phase 1 — Prepare**:
1. A proposer chooses a proposal number `n` (monotonically increasing, globally unique).
2. The proposer sends `Prepare(n)` to all acceptors.
3. Each acceptor responds with `Promise(n, v_a, n_a)` — promising to reject any proposal with number < n — and returning the highest-accepted value `v_a` with its proposal number `n_a`.

**Phase 2 — Accept**:
1. If the proposer receives promises from a majority of acceptors, it selects the value: the `v_a` from the highest `n_a` among the promises (or a new value if no acceptor has accepted anything).
2. The proposer sends `Accept(n, v)` to all acceptors.
3. Each acceptor accepts the proposal unless it has already promised a higher `n`.
4. When a majority of acceptors accept `(n, v)`, the value `v` is **decided**.

**Multi-Paxos** extends single-decree Paxos to a replicated log by electing a stable leader for multiple rounds, reducing Phase 1 to a one-time setup per leader epoch.

### Hybrid Leaderless Variants

**EPaxos Revisited (NSDI 2021)** showed that EPaxos's leaderless approach, while eliminating the leader bottleneck, produces tail latency 4x worse than Multi-Paxos due to dependency graph resolution.

**Pineapple (NSDI 2025)** solves this by unifying Multi-Paxos with ABD atomic shared registers via logical timestamps:
- Any node can serve reads and writes — the single-leader bottleneck is eliminated.
- Median latency reduced by >50% vs. optimized Raft in balanced workloads.
- Beats EPaxos, Multi-Paxos, and Gryff on both WAN and LAN.
- Preferred over EPaxos when tail latency matters.

**Kill criteria:** Pineapple adds one extra communication round vs. Multi-Paxos in the write path. Drop in write-dominated workloads where this extra round exceeds the latency budget. Drop if leader election instability is not the bottleneck.

**Reference:** Bantikyan, Zarnstorff, Chou, Tseng, Palmieri. NSDI 2025.

---

## When to Use

- Implementing a quorum-based agreement service from scratch.
- Auditing a distributed coordination system for safety properties.
- Understanding the theoretical foundation of Raft, Zab (ZooKeeper), and Viewstamped Replication.
- Designing a distributed lock or configuration service.

---

## Inputs

| Input | Description |
|-------|-------------|
| Number of nodes N | Total acceptors; majority quorum = floor(N/2) + 1 |
| Number of tolerated failures f | Must have N ≥ 2f + 1 |
| Proposal number source | Globally unique, monotonically increasing (often epoch + node-id) |
| Network model | Partial synchrony assumed for liveness |

---

## Outputs

| Output | Description |
|--------|-------------|
| Decided value | The single value agreed upon by a majority |
| Safety guarantee | No two correct processes decide different values |
| Liveness note | Progress requires a stable leader under partial synchrony |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Dueling proposers (livelock) | Two proposers repeatedly interrupt each other's Phase 2 by starting a new Phase 1 with a higher number | No value is ever decided — Paxos loops indefinitely |
| Incorrect proposal number generation | Proposal numbers are not globally unique or not monotonically increasing | Safety violated — two proposals with the same number accepted by disjoint quorums |
| Skipping Phase 1 after leader crash | A new leader assumes it can reuse the old leader's log without running Phase 1 | Uncommitted entries from the old leader may be incorrectly committed |
| Using Paxos without a stable leader | Classic Paxos without Multi-Paxos requires Phase 1 for every value | High latency; expensive in practice |

---

## Worked Example

**Scenario**: A distributed configuration service must ensure that all nodes agree on the current cluster leader name, even if one node crashes during the update.

**Setup**: 3 acceptors (A1, A2, A3). Quorum = 2. Proposer P1 wants to propose value "node-7".

**Phase 1**:
- P1 sends `Prepare(n=5)` to A1, A2, A3.
- A1, A2 respond `Promise(5, null, 0)` — no previously accepted value.
- A3 is slow (crashed). P1 has a majority (A1, A2).

**Phase 2**:
- Since no acceptor reported a previously accepted value, P1 proposes its own value: `Accept(5, "node-7")`.
- A1, A2 accept. Value "node-7" is decided.
- A3 recovers later, runs Phase 1 with a higher number, learns "node-7" was already accepted, and adopts it.

**Livelock prevention**: Use a randomised back-off before re-proposing, or designate a single distinguished proposer (Multi-Paxos leader election).

---

## Sources

- Lamport, L. (1998). The Part-Time Parliament. ACM TOCS. [lamport.azurewebsites.net/pubs/lamport-paxos.pdf](https://lamport.azurewebsites.net/pubs/lamport-paxos.pdf)
- Lamport, L. (2001). Paxos Made Simple. ACM SIGACT News. [lamport.azurewebsites.net/pubs/paxos-simple.pdf](https://lamport.azurewebsites.net/pubs/paxos-simple.pdf)
- Chandra, T., Griesemer, R., & Redstone, J. (2007). Paxos Made Live — An Engineering Perspective. PODC. [doi.org/10.1145/1281100.1281103](https://doi.org/10.1145/1281100.1281103)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
