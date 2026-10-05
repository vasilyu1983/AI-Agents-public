# Primitive 2: FLP Impossibility

**Source**: Fischer, Lynch, Paterson 1985.

---

## Definition

**FLP Impossibility** states that in a fully asynchronous message-passing system with no bound on message delay, it is impossible for any deterministic consensus protocol to simultaneously guarantee:

1. **Safety**: All non-faulty processes agree on the same value.
2. **Liveness (termination)**: Every execution eventually reaches a decision.

...even if only **one** process may crash (fail-stop).

The proof shows that for any protocol in this model, there always exists a run where the protocol is in a "bivalent" configuration — a state from which both 0 and 1 could still be decided — that can be extended indefinitely without reaching agreement.

**Implication for practice**: Real consensus systems (Paxos, Raft, ZooKeeper) escape FLP by relaxing the asynchrony assumption. They operate under **partial synchrony**: message delays are bounded eventually (not always). They use timeouts and leader election to guarantee liveness in practice, accepting that under adversarial scheduling liveness is not guaranteed.

---

## When to Use

- Evaluating whether a consensus protocol can "hang" under fault conditions.
- Explaining why Paxos and Raft need timeout-based leader election.
- Auditing a distributed lock or coordination service for liveness guarantees.
- Justifying why "guaranteed exactly-once" termination is not achievable in a fully async network.

---

## Inputs

| Input | Description |
|-------|-------------|
| Network model | Fully asynchronous vs. partially synchronous vs. synchronous |
| Fault model | Crash-stop vs. Byzantine vs. crash-recovery |
| Number of tolerated failures | f out of N processes |

---

## Outputs

| Output | Description |
|--------|-------------|
| Liveness classification | Does the protocol guarantee termination in the given model? |
| Required synchrony assumption | What timeout or partial-synchrony assumption enables liveness? |
| Failure scenario | Describe the specific scheduling attack that prevents termination |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Assuming Paxos/Raft always terminates | Both protocols require partial synchrony for liveness | In adversarial scheduling or severe network delays, the protocol can block indefinitely |
| Ignoring FLP when adding a "fast path" to consensus | Fast paths can introduce bivalent states | The fast path may silently fall back to slow path or block |
| Treating a 2-phase commit as a consensus protocol | 2PC blocks if the coordinator crashes before phase 2 | Participants are stuck in the "prepared" state — classic FLP violation |
| Claiming "consensus without coordination" | Coordination is necessary for agreement under asynchrony | Any such claim implies either a relaxed consistency model or a synchrony assumption |

---

## Worked Example

**Scenario**: A team asks "Why does etcd's leader election sometimes seem to hang during network problems?"

**FLP explanation**:
etcd uses the Raft protocol, which requires a majority quorum to elect a leader. When the network is partitioned and no partition contains a majority of nodes, no leader can be elected. The protocol blocks waiting for a quorum that cannot form.

This is not a bug — it is the safety guarantee in action. Raft prefers consistency (no split-brain) over availability (making progress without a quorum). FLP explains why Raft cannot guarantee that an election will always terminate: in a fully async network with f crash faults, liveness is not provable. Raft's heartbeat timeout is the partial-synchrony assumption that makes liveness practical.

**Fix**: Calibrate the election timeout to be significantly larger than the 99th-percentile round-trip time in the expected network. This does not eliminate the FLP result — it narrows the window in which adversarial scheduling can prevent liveness.

---

## Sources

- Fischer, M. J., Lynch, N. A., & Paterson, M. S. (1985). Impossibility of Distributed Consensus with One Faulty Process. Journal of the ACM. [doi.org/10.1145/3149.214121](https://doi.org/10.1145/3149.214121)
- Lamport, L., Shostak, R., & Pease, M. (1982). The Byzantine Generals Problem. ACM TOPLAS. [doi.org/10.1145/357172.357176](https://doi.org/10.1145/357172.357176)
- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 9. [dataintensive.net](https://dataintensive.net/)
