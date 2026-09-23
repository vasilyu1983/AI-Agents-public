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

### Failure Detection (what the broadcast layer disseminates)

Gossip's dominant production payload is failure-detector state, so the detector taxonomy belongs here. Petrov frames the whole problem as one tradeoff: "there's always a trade-off between wrongly suspecting alive processes as dead (producing false-positives), and delaying marking an unresponsive process as dead" — and, citing Chandra & Toueg 1996, "It is provably impossible to build a failure detector that is both accurate and efficient."

Two quality axes: **completeness** ("every nonfaulty member should eventually notice the process failure") and **accuracy** (whether the failure "was precisely detected" — an algorithm "is not accurate if it falsely accuses a live process of being failed"). Efficiency (how fast) trades against accuracy.

| Detector | Mechanism | Buys you | Costs you |
|----------|-----------|----------|-----------|
| **Ping / heartbeat + timeout** (e.g. Akka deadline failure detector) | Ping expects a reply in a fixed window; heartbeat has the process announce itself. Miss the deadline → suspected | Simplicity, strong completeness | "its precision relies on the careful selection of ping frequency and timeout, and it does not capture process visibility from the perspective of other processes" |
| **Timeout-free heartbeat counters** (Aguilera et al. 1997) | Heartbeats carry the path travelled; each receiver increments counters for every process on the path. No timeouts → holds under asynchronous assumptions | Can "(correctly) mark an unreachable process as alive even when the direct link between the two processes is faulty" | Requires fair links and full membership knowledge; "interpreting heartbeat counters may be quite tricky: we need to pick a threshold" |
| **SWIM / outsourced heartbeats** (Gupta et al. 2001) | P1 pings P2; on no reply, P1 asks *random* members P3, P4 to probe P2 and relay the ack | Direct *and* indirect reachability; only needs a subset of peers, not full membership; parallel probes give "more information about suspected processes quickly" | Extra round-trip on the suspicion path; decision now depends on the helpers' own health |
| **Phi-accrual** (Hayashibara et al. 2004) | Sliding window of recent heartbeat arrival times (assumed normally distributed); estimates the next arrival and emits a continuous suspicion level φ instead of up/down | "dynamically adapts to changing network conditions by adjusting the scale on which the node can be marked as a suspect"; the threshold becomes an application knob, not a hardcoded timeout | Needs a warm sample window; a normality assumption that bimodal/GC-pause latency violates |
| **Gossip-style detection** (van Renesse et al. 1998) | Members gossip a table of `{member: heartbeat_counter, last_updated}`; a counter that stops advancing marks the member failed | Cluster view is "an aggregate from multiple nodes"; heartbeats route around a broken link; worst-case bandwidth "can grow at most linearly with a number of processes" | More messages overall; still needs a carefully chosen timeout "to minimize the probability of false-positives" |
| **FUSE** (Dunagan et al. 2004) | Inverts the problem: processes are arranged in groups, and a member that detects a failure *stops answering pings itself*, converting a single failure into a group failure that propagates via absence of communication | "every member is guaranteed to learn about group failure"; works "even in cases of network partitions" | "a link failure separating a single process from other ones can be converted to the group failure as well" — deliberate, but must match the application's failure semantics |

**Architecture split (phi-accrual, generalizable):** *monitoring* (collect liveness via pings/heartbeats/request sampling) → *interpretation* (decide whether to suspect) → *action* (callback on suspicion). Keeping these three separable is what lets you swap a deadline detector for phi-accrual without touching membership logic.

**Selection rule.** Fixed timeout when the network is predictable and the cost of a false positive is low. SWIM when you cannot afford full-membership knowledge or single-observer verdicts. Phi-accrual when latency varies enough that any one timeout is either too twitchy or too slow (Cassandra, Akka). Gossip-style when link failures must not be mistaken for node failures. FUSE when the application's real unit of failure is the group, not the node.

**Tie to consensus:** FLP (#2) says no protocol guarantees consensus in an asynchronous system; failure detectors augment the model. Chandra & Toueg 1996 "shows that solving consensus is possible even with a failure detector that makes an infinite number of mistakes" — which is why detector *accuracy* is a tuning parameter, not a correctness prerequisite.

*Source: Petrov, Database Internals (2019), Ch.9 "Failure Detection" — §Heartbeats and Pings through §Summary, PDF pp.246–254.*

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

**TOB alternative**: For a common agreed event order (delivery/application can occur at different wall-clock times), use total-order broadcast via Raft or Paxos to agree on the failure event before applying it. Cost: higher latency, requires a quorum.

---

## Sources

- Birman, K. P. (2007). The Promise, and Limitations, of Gossip Protocols. ACM SIGOPS. [doi.org/10.1145/1317379.1317382](https://doi.org/10.1145/1317379.1317382)
- Hadzilacos, V., & Toueg, S. (1994). A Modular Approach to Fault-Tolerant Broadcasts and Related Problems. Cornell TR.
- Lakshman, A., & Malik, P. (2010). Cassandra: A Decentralized Structured Storage System. SIGOPS. [doi.org/10.1145/1773912.1773922](https://doi.org/10.1145/1773912.1773922)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
