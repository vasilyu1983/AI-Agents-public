# Distributed Systems Formal Theory Map

Use this map when a design claim depends on timing, failure, ordering, or consistency assumptions.

## Theory Spine

| Construct | What It Formalizes | Operational Test |
|-----------|--------------------|------------------|
| Failure model | Crash, omission, Byzantine, partition, pause, or clock fault | Which failures are tolerated, and which are outside the contract? |
| Timing model | Synchronous, asynchronous, or partially synchronous network | What timeout or eventual-timeliness assumption is required for liveness? |
| Happens-before | Causal order created by local order and message send/receive | Can two events be ordered without relying on wall time? |
| Logical clock | Timestamp preserving partial or total order constraints | Does the clock encode causality or only a deterministic ordering? |
| Consensus | Agreement, validity, and termination under a failure model | What is the quorum, log, leader, and durability assumption? |
| Quorum intersection | Any two successful operation sets overlap | Do read/write or election quorums share at least one correct node? |
| Replication consistency | Visibility and ordering rules for reads/writes | Which anomalies are allowed? |
| CRDT semilattice | Merge is associative, commutative, and idempotent | Can replicas converge without coordination? |

## Primitive Dependency Map

| Primitive | Depends On | Boundary |
|-----------|------------|----------|
| CAP/PACELC | Partition model, availability definition, consistency definition | CAP is about partition behavior; PACELC adds normal-case latency tradeoffs |
| FLP | Asynchrony, deterministic consensus, one crash fault | Explains why liveness needs timing/randomization assumptions |
| Paxos/Raft | Quorum intersection, durable log, leader/election rules | Safety can hold during partitions; liveness needs timing assumptions |
| Lamport/vector clocks | Happens-before relation | Lamport clocks do not detect concurrency; vector clocks can |
| CRDTs | Semilattice merge | Not suitable for arbitrary invariants without coordination |
| Idempotency | Stable operation identity and dedupe state | Transport "exactly once" is not an end-to-end guarantee |
| Leases/fencing | Monotonic token authority and storage enforcement | A lease without fencing does not protect against stale leaders |

## Correctness Vocabulary

- Safety: nothing bad happens; for example, no two leaders commit conflicting log entries.
- Liveness: something good eventually happens; for example, a valid proposal eventually commits.
- Linearizability: operations appear to occur atomically in real-time order.
- Serializability: transactions are equivalent to some serial order; real-time order is not necessarily preserved.
- Causal consistency: causally related writes are observed in happens-before order.
- Eventual consistency: replicas converge if writes stop and messages are delivered.

## Evidence Standards

- Consensus claim: name protocol, quorum size, failure model, durable state, leader behavior, and reconfiguration rules.
- Consistency claim: name the exact model and show an allowed/forbidden anomaly.
- Idempotency claim: specify key scope, dedupe retention, operation side effects, and retry behavior.
- CRDT claim: show state representation and merge law.
- Lease claim: show monotonic fencing token enforcement at the resource, not only the lock service.

## Source Anchors

- Lamport: happens-before, logical clocks, Paxos.
- Fischer, Lynch, Paterson: deterministic consensus impossibility in asynchronous systems.
- Gilbert and Lynch: formal CAP proof.
- Abadi: PACELC framing.
- Ongaro and Ousterhout: Raft consensus.
- Shapiro et al.: CRDT formalism.

## Verification Reference Implementations

Three complementary approaches define the current state-of-the-art for verifying distributed protocols:

| Approach | Reference | Scope | Artifact |
|----------|-----------|-------|---------|
| Automated invariant synthesis (fully automated safety proofs) | Zhang et al., Basilisk, OSDI 2025 Best Paper | Safety only; applied to 16 protocols; Provenance Invariants via Atomic Sharding static analysis | github.com/GLaDOS-Michigan/Basilisk |
| CI-integrated TLA+ simulation (probabilistic, no full proof) | Howard et al., Smart Casual Verification, NSDI 2025 | Safety + liveness bugs caught in CI; found 6 bugs in CCF Raft variant; arXiv:2406.17455 | microsoft/CCF |
| Modular TLA+ + conformance testing (spec-to-code gap) | Schultz & Demirbas, PVLDB vol.18 no.12, 2025 | Safety, permissiveness; automated conformance testing of C++ implementation against TLA+ spec | github.com/mongodb-labs/vldb25-dist-txns |

**Choosing between them:** Use Basilisk when exhaustive automated safety proof is required and the protocol admits static analysis. Use SCV when the team has TLA+ expertise and wants continuous verification in CI without full proof overhead. Use MongoDB's modular approach when the system has a stable spec-to-code interface and conformance testing infrastructure can be maintained alongside implementation changes.

## Empirical Falsification (complement, not substitute)

Formal verification establishes properties of a *specification*. The three approaches above differ in how much of the gap to the running binary they close, and none closes it entirely. Two empirical techniques cover the remainder:

| Approach | What it establishes | Blind spot |
|----------|---------------------|------------|
| Deterministic simulation testing (FoundationDB lineage; TigerBeetle, WarpStream, Antithesis) | The real binary survives adversarial schedules, clocks, and injected faults, with every failure replayable from a seed | Only faults the simulator can generate; requires all I/O, time, and concurrency behind injectable interfaces, so it is an architectural commitment made early or not at all |
| Black-box consistency checking (Jepsen + the Elle isolation checker) | An observed history of a *real deployment* under real faults does or does not satisfy a claimed consistency model | Finds violations, never proves their absence; coverage is bounded by the fault schedule and run length |

**Evidence hierarchy for a consistency claim**, strongest first: machine-checked proof of the implementation; conformance-tested spec (MongoDB pattern); DST over the real binary; external black-box report (Jepsen); internal fuzzing; vendor documentation. Documentation alone is the weakest tier and has been repeatedly falsified — see the Galera case in SKILL.md, where the *recommended* configuration did not provide the durability its docs implied.
