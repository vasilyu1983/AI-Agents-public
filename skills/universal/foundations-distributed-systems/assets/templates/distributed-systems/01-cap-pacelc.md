# Primitive 1: CAP Theorem and PACELC Extension

**Sources**: Brewer 2000 (CAP conjecture), Gilbert & Lynch 2002 (CAP proof), Abadi 2012 (PACELC).

---

## Definition

**CAP Theorem**: In a distributed system, during a network partition, it is impossible to simultaneously guarantee both **Consistency** (every read sees the most recent write or returns an error) and **Availability** (every request receives a non-error response). Partition Tolerance is not optional in a real network — it must be assumed.

> Correct framing: "During a partition, choose C or A." Incorrect framing: "Pick 2 of 3 at design time."

**PACELC Extension**: When there is **no** partition (the normal case), a system faces a trade-off between **Latency** (lower latency by serving from a nearby replica) and **Consistency** (stronger consistency requires coordination across replicas, which adds latency).

The full trade-off is:
- **Under Partition (P)**: choose **A**vailability or **C**onsistency.
- **Else (no partition)**: choose **L**atency or **C**onsistency.

---

## When to Use

- Choosing a database or storage system for a given workload.
- Designing a replication topology (single-leader, multi-leader, leaderless).
- Communicating trade-offs to stakeholders when selecting a consistency model.
- Auditing whether a system's documented behaviour matches its actual guarantees.

---

## Inputs

| Input | Description |
|-------|-------------|
| Workload consistency requirement | Linearisability, causal, read-your-writes, eventual |
| Availability requirement | Is it acceptable to reject requests during a partition? |
| Network topology | Single-region, multi-region, WAN latency |
| Partition frequency | Rare (same datacenter) vs. frequent (multi-continent) |

---

## Outputs

| Output | Description |
|--------|-------------|
| CAP classification | CP (prefer consistency under partition) or AP (prefer availability under partition) |
| PACELC classification | EL (lower latency, weaker consistency) or EC (higher latency, stronger consistency) |
| System selection recommendation | Database or storage system matching the trade-off |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Treating CAP as a static design-time dial | CAP is contingent on a partition occurring | Design may choose a "CP" system but still return stale data during normal operation (PACELC EL) |
| Claiming a system is both CA | All real networks can partition; CA is not a valid distributed-system classification | Silent data loss or unavailability during a real partition |
| Confusing consistency with durability | A linearisable read may still return lost data if the write was not durable | Separate the consistency model from the durability/fsync guarantee |
| Ignoring PACELC for latency-sensitive workloads | Under normal operation, extra coordination round-trips add latency even without a partition | Choose an EL system (e.g. Dynamo, Cassandra) for latency-sensitive, eventually-consistent workloads |

---

## Worked Example

**Scenario**: An e-commerce platform must choose a database for product inventory counts. The team asks: "Should we use Cassandra or PostgreSQL (with a synchronous replica)?"

**CAP analysis**:
- Cassandra is AP: during a partition, it continues to accept writes and reads, but replicas may diverge.
- PostgreSQL with synchronous replication is CP: during a partition where the synchronous replica is unreachable, writes block (or fail) to preserve consistency.

**PACELC analysis**:
- Cassandra is PA/EL: no partition → serve from nearest replica (low latency, possibly stale).
- PostgreSQL sync replica is PC/EC: no partition → wait for replica acknowledgement (higher latency, consistent).

**Decision**: For inventory counts where overselling must be prevented, the team chooses PC/EC (PostgreSQL). For product view counts (approximate), the team chooses PA/EL (Cassandra).

---

## Sources

- Brewer, E. (2000). Towards Robust Distributed Systems. PODC keynote. [people.eecs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf](https://people.eecs.berkeley.edu/~brewer/cs262b-2004/PODC-keynote.pdf)
- Gilbert, S., & Lynch, N. (2002). Brewer's Conjecture and the Feasibility of Consistent, Available, Partition-Tolerant Web Services. ACM SIGACT News. [doi.org/10.1145/564585.564601](https://doi.org/10.1145/564585.564601)
- Abadi, D. (2012). Consistency Tradeoffs in Modern Distributed Database System Design. IEEE Computer. [doi.org/10.1109/MC.2012.33](https://doi.org/10.1109/MC.2012.33)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
