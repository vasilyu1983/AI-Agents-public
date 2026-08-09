# Primitive 10: Causal Consistency

**Sources**: Ahamad et al. 1995; Lloyd et al. 2011 (COPS); Lamport 1978.

---

## Definition

**Causal consistency** guarantees that operations that are causally related are seen by all processes in the same causal order. Concurrent (causally unrelated) operations may be seen in any order.

Formally: If operation A **causally precedes** operation B (A → B), then every process that observes B must first have observed A.

**Causal ordering sources**:
1. **Program order**: If process P executes A then B, then A → B.
2. **Message passing**: If P sends message m (event A) and Q receives m (event B), then A → B.
3. **Transitivity**: If A → B and B → C, then A → C.

**Causal consistency is weaker than linearisability** (the strongest consistency model) and **stronger than eventual consistency**.

**Causal+ consistency**: Causal consistency plus convergence — when two replicas have seen the same set of causally related operations, they must be in the same state. COPS (Clusters of Order-Preserving Servers) implements causal+.

**Mechanisms**:
- **Dependency tracking**: Each write carries a vector clock (or set of version dependencies). A replica delays exposing a write until all its causal dependencies have been applied.
- **Sticky sessions**: A client always reads from the same replica (or a replica that has seen all the client's prior writes), ensuring read-your-writes.
- **Causal tokens**: A client carries a token representing the maximum vector clock it has seen. The replica checks the token before serving the read.

---

## When to Use

- Social networks, messaging systems, and collaborative tools where the "reply before the post" anomaly is unacceptable.
- Geographically distributed systems that cannot afford the coordination cost of linearisability.
- Systems where eventual consistency is too weak but serializability is too expensive.
- Any system where the happens-before relation between user actions must be preserved.

---

## Inputs

| Input | Description |
|-------|-------------|
| Vector clock or dependency set | Attached to every write; propagated with the data |
| Client session token | Maximum version vector seen by the client; used for sticky routing |
| Replica dependency store | Tracks which versions each replica has applied |

---

## Outputs

| Output | Description |
|--------|-------------|
| Causal ordering guarantee | A read never returns a write unless all of its causal predecessors have been applied on the reading replica |
| No "reply before post" anomaly | A response to a message is never visible before the original message |
| Eventual convergence | All replicas converge to the same state after all writes are propagated |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Reading from a different replica mid-session | Client switches replicas; the new replica has not yet applied the client's prior writes | Reads return stale data — the client's own writes are invisible |
| Dependency tracking dropped in caches | An intermediate cache strips the vector clock from the response | Cache serves causally stale data; downstream clients see anomalies |
| Causal consistency confused with linearisability | Causal consistency does not prevent concurrent writes from appearing in different orders on different replicas | Two replicas may converge to a different ordering of concurrent events (correct under causal+, unexpected under linearisability) |
| Large dependency sets | Every write carries the full set of its causal predecessors | Memory and bandwidth overhead; use garbage collection or compressed version vectors |

---

## Worked Example

**Scenario**: A social feed. Alice posts "Going to the concert tonight!" (write W1). Bob, who sees W1, replies "See you there!" (write W2, causally depends on W1). Charlie visits the feed.

**Without causal consistency**: Charlie's replica has applied W2 (the reply) but not yet W1 (the original post). Charlie sees "See you there!" without context — a causal anomaly.

**With causal consistency**:
1. W2 carries a dependency: `{W1: version 1}`.
2. Charlie's replica checks: "Has W1 been applied?" No → delays exposing W2.
3. W1 arrives and is applied. Charlie's replica now exposes both W1 and W2 in causal order.
4. Charlie sees the original post, then the reply — correct causal ordering.

**Sticky session**: If Charlie is always routed to the same replica, the replica only needs to track Charlie's own causal tokens (not all cluster versions). This is simpler but breaks if the replica fails.

---

## Sources

- Ahamad, M., et al. (1995). Causal Memory: Definitions, Implementation, and Programming. Distributed Computing. [doi.org/10.1007/BF01784241](https://doi.org/10.1007/BF01784241)
- Lloyd, W., et al. (2011). Don't Settle for Eventual: Scalable Causal Consistency for Wide-Area Storage with COPS. SOSP. [doi.org/10.1145/2043556.2043593](https://doi.org/10.1145/2043556.2043593)
- Lamport, L. (1978). Time, Clocks, and the Ordering of Events in a Distributed System. CACM. [lamport.azurewebsites.net/pubs/time-clocks.pdf](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
