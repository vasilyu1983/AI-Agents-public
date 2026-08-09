# Primitive 6: CRDTs (Conflict-Free Replicated Data Types)

**Source**: Shapiro, Preguica, Baquero, Zawirski 2011.

---

## Definition

A **CRDT** (Conflict-Free Replicated Data Type) is a data type whose merge function is:
- **Commutative**: `merge(A, B) = merge(B, A)`
- **Associative**: `merge(A, merge(B, C)) = merge(merge(A, B), C)`
- **Idempotent**: `merge(A, A) = A`

These three properties guarantee that any set of replicas that exchange states will **converge to the same value** regardless of the order, timing, or number of times they exchange messages — no coordination protocol required.

**Two families**:

| Family | Mechanism | Example |
|--------|-----------|---------|
| **CvRDT** (Convergent / state-based) | Replicas merge full states; merge must be a join on a semilattice | G-Counter, 2P-Set |
| **CmRDT** (Commutative / op-based) | Replicas broadcast operations; operations must commute | OR-Set, RGA (collaborative text) |

**Common CRDTs**:
| CRDT | Operations | Use Case |
|------|-----------|----------|
| G-Counter | increment | View counts, upvotes |
| PN-Counter | increment, decrement | Inventory (approximate), likes/dislikes |
| G-Set | add | Tag sets (add only) |
| 2P-Set | add, remove (once) | Items that can be removed exactly once |
| OR-Set | add, remove (any time) | Shopping cart, presence set |
| LWW-Register | assign | Last-write-wins key-value store |
| RGA | insert, delete | Collaborative text editing |

---

## When to Use

- Shared mutable state that must converge across replicas without coordination.
- Operations that can be modelled as monotonically increasing (add-only sets, counters).
- Real-time collaboration (text, whiteboards, presence).
- Distributed systems where a strong consistency protocol is too expensive or unavailable.

---

## Inputs

| Input | Description |
|-------|-------------|
| Operation set | What operations must be supported on the replicated state? |
| Conflict semantics | What should happen when two replicas concurrently update the same value? |
| Network model | Is state exchange reliable and ordered, or unreliable and unordered? |

---

## Outputs

| Output | Description |
|--------|-------------|
| Converged state | All replicas eventually hold identical state |
| No coordination required | Replicas merge independently without a consensus round |
| Conflict-free guarantee | By construction — no conflicts possible if the CRDT is chosen correctly |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Non-commutative operation encoded as a CRDT | E.g. subtract-then-add ≠ add-then-subtract for PN-Counter in some implementations | State diverges; replicas never converge |
| Treating a 2P-Set as an OR-Set | 2P-Set allows only one remove per element; re-adding a removed element is silently dropped | Data loss when items are removed and re-added |
| State size explosion in G-Counter or OR-Set | Each replica maintains a per-node counter or tombstone set | Memory and bandwidth grow unbounded without garbage collection |
| Using LWW-Register without a causal clock | Last-write-wins by wall clock; concurrent writes on different replicas silently overwrite each other | Data loss for the "losing" write |
| Applying CRDTs to non-lattice semantics | The domain has a natural total order but the merge is not the join | Convergence property breaks |

---

## Worked Example

**Scenario**: A distributed shopping cart. Users can add and remove items from any replica. The cart must converge to the same contents across replicas regardless of network partitions.

**CRDT choice**: OR-Set (Observed-Remove Set). Each add operation assigns a unique tag. A remove operation removes all observed tags for that item.

**Execution**:
1. Replica A: `add("book", tag=t1)` → cart = `{(book, t1)}`
2. Replica B (concurrent partition): `add("book", tag=t2)` → cart = `{(book, t2)}`
3. Replica A: `remove("book")` removes tag t1 → cart = `{}`
4. Partition heals. Merge: A has `{}`, B has `{(book, t2)}`.
5. Merged state: `{(book, t2)}` — the book added on B is still present.

**Why this is correct**: The OR-Set semantics say "add wins over concurrent remove." The remove on A only removes the tags it observed (t1). B's concurrent add (t2) was not observed by A, so it survives.

---

## Sources

- Shapiro, M., Preguica, N., Baquero, C., & Zawirski, M. (2011). Conflict-Free Replicated Data Types. SSS. [doi.org/10.1007/978-3-642-24550-3_29](https://doi.org/10.1007/978-3-642-24550-3_29)
- Kleppmann, M., & Beresford, A. (2017). A Conflict-Free Replicated JSON Datatype. IEEE TPDS. [arxiv.org/abs/1608.03960](https://arxiv.org/abs/1608.03960)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
