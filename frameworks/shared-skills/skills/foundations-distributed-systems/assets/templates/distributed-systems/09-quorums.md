# Primitive 9: Quorums (NWR)

**Sources**: DeCandia et al. 2007 (Dynamo); Gifford 1979 (quorum systems).

---

## Definition

A **quorum** is the minimum number of nodes that must participate in a read or write operation to guarantee consistency. The **NWR model** (from Dynamo) parameterises this with three values:

| Symbol | Meaning |
|--------|---------|
| **N** | Total number of replicas for a key |
| **W** | Number of replicas that must acknowledge a write before it is considered successful |
| **R** | Number of replicas that must respond to a read before the result is returned |

**Core property**: If `W + R > N`, at least one replica in every read quorum must have the latest write. This guarantees that reads always include the most recently written value.

**Common configurations**:

| W | R | N | Property |
|---|---|---|---------|
| N | 1 | N | Write to all; fast reads; any single failure blocks writes |
| 1 | N | N | Fast writes; read from all; any single failure blocks reads |
| majority | majority | N | Strong consistency; tolerates floor(N/2) failures |
| 1 | 1 | N | Fast writes and reads; eventual consistency only (W+R ≤ N) |
| 2 | 2 | 3 | Common Cassandra strong-consistency config; tolerates 1 failure |

**Sloppy quorums** (Dynamo): When the full quorum is unavailable, accept writes to any available nodes (possibly outside the "preference list"). The "hinted handoff" mechanism delivers these writes to the correct nodes when they recover. Sloppy quorums improve availability but do not guarantee strong consistency.

**Read repair**: When a read fetches responses from R replicas and some are stale, the coordinator sends the latest value to the stale replicas to bring them up to date.

---

## When to Use

- Configuring a leaderless replication system (Cassandra, DynamoDB, Riak, Voldemort).
- Designing a custom replication layer with tunable consistency.
- Reasoning about the consistency level required for a given workload.
- Auditing why a Cassandra or DynamoDB read returned stale data.

---

## Inputs

| Input | Description |
|-------|-------------|
| N | Replication factor (typically 3 or 5) |
| W | Write quorum size |
| R | Read quorum size |
| Fault tolerance requirement | Number of node failures the system must survive |

---

## Outputs

| Output | Description |
|--------|-------------|
| Consistency guarantee | W + R > N → strong consistency; W + R ≤ N → eventual consistency |
| Fault tolerance | Can tolerate min(N - W, N - R) failures while maintaining quorum |
| Latency profile | Dominated by the slowest node in the quorum (tail latency) |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| W + R ≤ N | Relaxed quorums for performance; reads and writes can miss each other | Stale reads — read returns a value that has been overwritten |
| Tail latency from slow replicas | The operation waits for the slowest node in the quorum | High 99th-percentile latency for reads and writes |
| Sloppy quorum without hinted handoff | Writes accepted on non-authoritative nodes during a partition; never delivered | Data loss when the temporary replica is replaced or crashes |
| Quorum without vector clocks or version timestamps | Cannot determine which replica has the latest value among R responses | Incorrect value returned (read repair cannot choose correctly) |
| N not odd with majority quorums | Even N with majority quorum (N/2 + 1) is less efficient than odd N | Asymmetric failure tolerance; no improvement in fault tolerance vs. N-1 |

---

## Worked Example

**Scenario**: Cassandra cluster with N=3, W=2, R=2 (QUORUM consistency level). A write updates key `"user:42:balance"` to `$150`.

**Write path**:
1. Coordinator sends write to all 3 replicas.
2. Two replicas (R1, R2) acknowledge → W=2 satisfied → write considered successful.
3. R3 is slow; receives the write asynchronously.

**Read path** (before R3 updates):
1. Coordinator sends read to all 3 replicas.
2. R1 returns `$150` (version 2). R2 returns `$150` (version 2). R3 returns `$100` (version 1). R=2 satisfied on R1, R2.
3. Coordinator returns `$150` (latest version from quorum). Sends read repair to R3.
4. R3 is updated to `$150`.

**Why W=1, R=1 is dangerous here**: A write to R1 only, followed by a read from R3 only → stale `$100` returned. `W + R = 2 ≤ N = 3` → no guarantee of intersection.

---

## Sources

- Gifford, D. K. (1979). Weighted Voting for Replicated Data. SOSP. [doi.org/10.1145/800215.806583](https://doi.org/10.1145/800215.806583)
- DeCandia, G., et al. (2007). Dynamo: Amazon's Highly Available Key-Value Store. SOSP. [doi.org/10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)
- Lakshman, A., & Malik, P. (2010). Cassandra: A Decentralized Structured Storage System. SIGOPS. [doi.org/10.1145/1773912.1773922](https://doi.org/10.1145/1773912.1773922)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 5. [dataintensive.net](https://dataintensive.net/)
