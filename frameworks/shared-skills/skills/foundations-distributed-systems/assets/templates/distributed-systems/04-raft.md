# Primitive 4: Raft

**Source**: Ongaro & Ousterhout 2014.

---

## Definition

**Raft** is a consensus algorithm designed for understandability. It achieves the same safety guarantees as Multi-Paxos but decomposes the problem into three relatively independent sub-problems:

1. **Leader election**: At most one leader per term. A candidate wins by receiving votes from a majority of servers.
2. **Log replication**: The leader accepts log entries from clients, replicates them to followers, and commits entries once a majority of servers have stored them.
3. **Safety**: The Log Matching Property ensures no two committed entries at the same log index can differ.

**Key properties**:
- **Terms**: Monotonically increasing integers. Each term begins with an election. If a candidate wins, it serves as leader for the rest of the term.
- **Commit rule**: An entry is committed when stored by a majority. A leader only commits entries from the current term (it cannot retroactively commit old-term entries directly).
- **Leader completeness**: A server with incomplete logs cannot win an election — candidates must have a log at least as up-to-date as any committed entry (last log index and last log term check).

---

## When to Use

- Implementing a replicated state machine (etcd, CockroachDB, TiKV, Consul).
- Choosing a consensus protocol for a new distributed system where code clarity and correctness proofs matter.
- Understanding how Kubernetes (via etcd) stores cluster state.
- Diagnosing log divergence or leader-election failures in an etcd or Raft-backed system.

---

## Inputs

| Input | Description |
|-------|-------------|
| Cluster size N | Odd numbers preferred; majority = floor(N/2) + 1 |
| Election timeout | Randomised interval [T, 2T]; must be >> heartbeat interval and >> 99th-pct RTT |
| Heartbeat interval | Frequency at which leader sends AppendEntries RPCs to followers |
| Log entry payload | Commands to replicate across the state machine |

---

## Outputs

| Output | Description |
|--------|-------------|
| Committed log entries | Entries applied to the state machine in the same order on all servers |
| Current leader | At most one per term |
| Term number | Monotonically increasing; used to detect stale messages |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Log divergence after leader crash | New leader has fewer entries than some followers | Raft resolves this by forcing followers to adopt the new leader's log — entries not replicated to a majority are discarded |
| Split vote / no elected leader | Election timeouts are too similar across nodes | Repeated elections with no majority; cluster unavailable for writes |
| Leader stale after partition heals | Old leader re-joins with a lower term number | Any message with a stale term is rejected; the old leader reverts to follower |
| Committing old-term entries without a new-term entry | Leader tries to commit entries from a previous term directly | Safety violation — Raft prohibits direct commitment of old-term entries; must commit a new-term entry first |
| Linearisable reads without a lease check | Follower reads or stale leader reads return old data | Use read-index or leader leases to guarantee linearisable reads |

---

## Worked Example

**Scenario**: A 5-node etcd cluster. The leader (node 1) crashes after replicating an entry to 2 followers (nodes 2 and 3) but before receiving acknowledgements from nodes 4 and 5.

**What Raft does**:
1. Nodes 2, 3, 4, 5 detect the leader heartbeat timeout and start elections.
2. Node 3 has the most up-to-date log (the replicated entry). It wins the election by receiving votes from nodes 2, 4, 5 (majority = 3).
3. Node 3 becomes leader in term T+1. It sends AppendEntries to nodes 4 and 5, which replicate the entry.
4. Once a majority (3 of 5) has the entry, it is committed and applied to the state machine.
5. Node 1 recovers, receives a heartbeat from node 3 with term T+1 > node 1's term T, and reverts to follower. Its uncommitted divergent entries are replaced by node 3's log.

**Election timeout tuning**: If all nodes use the same timeout, they all start elections simultaneously — split vote. Use a randomised range: `election_timeout = random(150ms, 300ms)`.

---

## Sources

- Ongaro, D., & Ousterhout, J. (2014). In Search of an Understandable Consensus Algorithm. USENIX ATC. [raft.github.io/raft.pdf](https://raft.github.io/raft.pdf)
- Raft website and visualisation: [raft.github.io](https://raft.github.io/)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
