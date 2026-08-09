# Primitive 11: Broadcast Protocols

**Sources**: Birman 2007 (gossip); Hadzilacos & Toueg 1994 (broadcast taxonomy); Lakshman & Malik 2010 (Cassandra gossip).

---

## Definition

A **broadcast protocol** defines how a message from one node is delivered to all (or a subset of) nodes in a cluster. Broadcast protocols differ in their delivery guarantees:

### Taxonomy

| Protocol | Guarantee | Use Case |
|----------|-----------|---------|
| **Best-effort broadcast** | Delivered if sender does not crash | Metrics, telemetry |
| **Reliable broadcast** | Every correct node delivers it, or no correct node does | Alert distribution |
| **FIFO broadcast** | Messages from the same sender delivered in send order | Log tailing |
| **Causal broadcast** | Causally related messages delivered in causal order | Social feeds (see #10) |
| **Total-order broadcast (TOB)** | All correct nodes deliver the same messages in the same order | Replicated state machines |
| **Atomic broadcast** | TOB + reliable broadcast (identical guarantee) | Equivalent to consensus |

### Gossip / Epidemic Protocols

**Gossip** (anti-entropy) is a probabilistic broadcast protocol:
1. Periodically, each node selects k random peers (fan-out).
2. The node exchanges state digests with those peers.
3. If a peer is missing an update, it is pushed or pulled.

**Convergence**: With fan-out k and N nodes, all nodes receive a message within O(log N / log k) rounds with high probability.

**Properties**:
- Highly available: no single point of failure.
- Scalable: O(N log N) messages per broadcast.
- Eventually consistent: convergence is probabilistic, not guaranteed in finite time.

**Use cases**: Cluster membership (Cassandra, Consul), failure detection, CAS dissemination.

### Total-Order Broadcast

**Total-order broadcast (TOB)** guarantees that all nodes deliver the same set of messages in the same order. This is **equivalent to consensus**: implementing TOB is as hard as consensus, and any consensus algorithm can be used to implement TOB.

**Relation to replicated state machines**: If all replicas start in the same state and apply the same sequence of commands (delivered via TOB), they remain identical. This is the foundation of the **replicated state machine** pattern used by Paxos (#3), Raft (#4), and ZooKeeper.

### DAG-BFT as High-Throughput Ordered Broadcast

In Byzantine-adversarial settings, DAG-based BFT protocols (Shoal++, Mysticeti) implement ordered broadcast where every node proposes — eliminating the single-leader throughput bottleneck while preserving total ordering. This is the broadcast layer of permissioned blockchain and DeFi infrastructure stacks. See primitive #3a (DAG-BFT Consensus) for full details and kill criteria.

### Inter-Cluster Consistent Broadcast (C3B)

When two independent Replicated State Machines (RSMs) must exchange messages across cluster boundaries — a gap the standard TOB taxonomy does not cover — the **Cross-Cluster Consistent Broadcast (C3B)** primitive provides formal correctness guarantees.

**Problem:** Prior practice used ad-hoc workarounds (custom bridges, dual-write patterns) that lacked formal correctness guarantees for RSM-to-RSM communication.

**C3B solution (Picsou, OSDI 2025):**
- Defines C3B as a formal primitive for inter-RSM message exchange.
- Uses **Quorum Acknowledgments (QUACKs)** — nodes determine with precision whether messages were received or lost, avoiding the ambiguity of raw replication bridges.
- Constant metadata overhead; 24x performance improvement over prior ad-hoc solutions.

**When to use:** Two independent RSMs must exchange messages with guaranteed delivery. Multi-region deployments where RSM-to-RSM links cross region boundaries.

**Kill criteria:** C3B is overhead when RSMs share the same cluster or communicate via a shared log (Kafka/Kinesis). Drop if inter-cluster communication is unidirectional and loss-tolerant.

**Reference:** Frank et al. (OSDI 2025). arXiv:2312.11029.

---

## When to Use

- **Gossip**: Cluster membership, failure detection, CRDT state exchange, service discovery.
- **Causal broadcast**: Social feeds, messaging systems where causal ordering matters but total order is not required.
- **Total-order broadcast**: Replicated state machines (etcd, ZooKeeper, database replication).

---

## Inputs

| Input | Description |
|-------|-------------|
| Fan-out k | Number of peers contacted per gossip round (typically 3–5) |
| Gossip interval | Period between gossip rounds (typical: 1 second) |
| Message payload | State digest (gossip) or command (TOB) |
| Cluster size N | Determines convergence time O(log N) |

---

## Outputs

| Output | Description |
|--------|-------------|
| Convergence time | O(log N) rounds for gossip; O(1) decision rounds for TOB (with a stable leader) |
| Delivery guarantee | Probabilistic (gossip) or deterministic (TOB) |
| Bandwidth | O(N log N) messages per broadcast for gossip |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Gossip fan-out too low | k=1 or k=2 in a large cluster | Slow convergence; some nodes may never receive the message |
| Gossip without anti-entropy | Only push-based gossip; receiver never requests missing state | State diverges indefinitely when messages are dropped |
| Total-order broadcast without consensus | Attempting TOB without a consensus protocol | Two nodes may deliver messages in different orders; replicated state machines diverge |
| FIFO broadcast confused with causal broadcast | FIFO orders messages from the same sender; causally related messages from different senders may be reordered | Causal anomalies across senders |
| Gossip message amplification | Each node re-gossips everything it receives without deduplication | Bandwidth O(N^2) instead of O(N log N) |

---

## Worked Example

**Scenario**: A Cassandra cluster needs to propagate node failure detection. A node that detects a peer as unreachable must inform all other nodes.

**Gossip approach (Cassandra phi accrual failure detector)**:
1. Each node maintains a heartbeat counter for all peers.
2. Every gossip interval (1 second), each node selects 3 random peers (fan-out = 3).
3. Nodes exchange `{node_id: heartbeat_count}` digests.
4. A peer is marked suspicious if its heartbeat count has not increased for longer than the failure threshold.
5. After φ rounds with no heartbeat, the peer is marked down and the information propagates via gossip.

**Convergence**: In a 100-node cluster with fan-out 3, failure information reaches all nodes in approximately log₃(100) ≈ 4–5 gossip rounds (4–5 seconds).

**TOB alternative**: For stronger guarantees (all nodes mark the peer as down at the same time), use total-order broadcast via Raft or Paxos to agree on the failure event before applying it. Cost: higher latency, requires a quorum.

---

## Sources

- Birman, K. P. (2007). The Promise, and Limitations, of Gossip Protocols. ACM SIGOPS. [doi.org/10.1145/1317379.1317382](https://doi.org/10.1145/1317379.1317382)
- Hadzilacos, V., & Toueg, S. (1994). A Modular Approach to Fault-Tolerant Broadcasts and Related Problems. Cornell TR.
- Lakshman, A., & Malik, P. (2010). Cassandra: A Decentralized Structured Storage System. SIGOPS. [doi.org/10.1145/1773912.1773922](https://doi.org/10.1145/1773912.1773922)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
