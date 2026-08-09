# Primitive 5: Vector Clocks and Lamport Timestamps

**Source**: Lamport 1978; Mattern 1989 (vector clocks).

---

## Definition

### Lamport Timestamps

A **Lamport timestamp** is a logical clock that assigns a monotonically increasing integer to every event in a distributed system, preserving the **happens-before** relation.

**Rules**:
1. Each process maintains a counter `L`, initially 0.
2. Before each local event, increment `L := L + 1`.
3. When sending a message, include the current `L` in the message.
4. When receiving a message with timestamp `L_m`, set `L := max(L, L_m) + 1`.

**Property**: If event A happened before event B (A → B), then `L(A) < L(B)`. The converse is not guaranteed — two events may have the same timestamp yet be concurrent.

### Vector Clocks

A **vector clock** is an array of counters, one per process, that captures full causal history.

**Rules** (process `i` out of N processes):
1. Initialise `V[j] = 0` for all `j`.
2. Before each local event, increment `V[i] := V[i] + 1`.
3. When sending a message, include the current vector `V`.
4. When receiving `V_m`, set `V[j] := max(V[j], V_m[j])` for all `j`, then increment `V[i] := V[i] + 1`.

**Comparison**:
- `V_a < V_b` (A happened before B) iff `V_a[j] <= V_b[j]` for all `j` and `V_a != V_b`.
- `V_a || V_b` (concurrent) iff neither `V_a < V_b` nor `V_b < V_a`.

---

## When to Use

- Lamport timestamps: when only causal ordering is needed (logging, event sourcing) and false positives (same timestamp ≠ concurrent) are acceptable.
- Vector clocks: when true concurrency detection is required (conflict resolution in multi-master replication, distributed debugging).
- Both: as the causal ordering substrate for causal consistency (#10) and gossip state (#11).

---

## Inputs

| Input | Description |
|-------|-------------|
| Number of processes N | Size of the vector clock array |
| Event stream | All send, receive, and local events per process |
| Comparison query | Did A happen before B? Are A and B concurrent? |

---

## Outputs

| Output | Description |
|--------|-------------|
| Causal order | Total order consistent with → for Lamport; partial order with true concurrency for vector clocks |
| Concurrent event pairs | Pairs `(A, B)` where `A || B` (vector clocks only) |
| Conflict candidates | Events that need merge / conflict resolution (vector clocks) |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Using wall-clock timestamps instead of logical clocks | Clocks drift; NTP corrections can go backwards | Events appear in wrong causal order; data loss in LWW conflict resolution |
| Using Lamport timestamps to detect concurrency | `L(A) < L(B)` does not imply A → B | False "not concurrent" classifications; incorrect merge decisions |
| Vector clock size explosion in large clusters | One counter per process; dynamically-joining nodes grow the vector | Memory and bandwidth overhead; use version vectors or dotted version vectors as a practical approximation |
| Missing clock update on receive | Process skips `max` merge step | Vector clock loses causal history; concurrency is falsely inferred |

---

## Worked Example

**Scenario**: Two users (Alice on node A, Bob on node B) simultaneously edit a shared document. We need to detect if their edits are concurrent or causally ordered.

**Initial state**: `V_A = [0,0]`, `V_B = [0,0]`.

1. Alice makes edit e1 on node A: `V_A = [1,0]`. Sends the document to Bob with `V = [1,0]`.
2. Bob receives e1: `V_B = max([0,0],[1,0]) + B_increment = [1,1]`. Bob makes edit e2: `V_B = [1,2]`.
3. Meanwhile, Charlie (node C) independently reads the original document and makes edit e3 with `V_C = [0,0,1]`.

**Comparison**:
- `V(e2) = [1,2]` vs. `V(e3) = [0,0,1]`: neither dominates → **concurrent** → conflict resolution needed.
- `V(e1) = [1,0]` vs. `V(e2) = [1,2]`: `V(e1) < V(e2)` → e1 happened before e2 → no conflict.

**Action**: Merge e2 and e3 with application-level conflict resolution (last-write-wins by author priority, or CRDT merge).

---

## Sources

- Lamport, L. (1978). Time, Clocks, and the Ordering of Events in a Distributed System. CACM. [lamport.azurewebsites.net/pubs/time-clocks.pdf](https://lamport.azurewebsites.net/pubs/time-clocks.pdf)
- Mattern, F. (1989). Virtual Time and Global States of Distributed Systems. Workshop on Parallel and Distributed Algorithms.
- DeCandia, G., et al. (2007). Dynamo: Amazon's Highly Available Key-Value Store. SOSP. [doi.org/10.1145/1294261.1294281](https://doi.org/10.1145/1294261.1294281)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
