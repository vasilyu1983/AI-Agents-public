# Distributed Systems Patterns, Scenarios, and Traps

Use this reference before making production claims about replication, ordering, availability, exactly-once behavior, or leader safety.

## Core Patterns

| Pattern | Use When | Watch For |
|---------|----------|-----------|
| State the model first | Any design mentions consensus, timeout, or consistency | Hidden asynchrony and failure assumptions |
| Quorum intersection | Reads, writes, elections, or commits span replicas | Reconfiguration and failure-domain overlap |
| Idempotent receiver | Messages can be retried or duplicated | Key scope too narrow or dedupe window too short |
| Fenced lease | A primary/leader controls a shared resource | Resource must reject stale tokens |
| Causal metadata | Users must read their own writes or preserve dependencies | Wall-clock timestamps do not prove causality |
| CRDT merge | Availability matters more than invariant coordination | Non-commutative operations or global constraints |

## Scenarios

### Multi-Region Write Path

1. Define the consistency contract: linearizable, causal, read-your-writes, or eventual.
2. Pick quorum or CRDT based on whether invariants require coordination.
3. If using a leader, use leases with fencing tokens at the storage boundary.
4. Add idempotency keys to all cross-region retries.
5. Test partition behavior explicitly; state whether the system rejects or accepts writes.

### Payment Webhook Receiver

1. Treat provider delivery as at-least-once.
2. Key dedupe by provider event id plus operation type.
3. Persist the dedupe record transactionally with the side effect.
4. Make the business operation idempotent independently of transport.
5. Alert on dedupe-store unavailability; it is part of correctness.

### Collaborative Editing or Agent Shared State

1. Determine whether operations commute.
2. Use a CRDT only when merge laws preserve intended semantics.
3. Use vector clocks or causal metadata for conflict visibility.
4. Use consensus for non-commutative invariants such as balances, unique names, or capacity limits.

## Anti-Patterns

| Anti-Pattern | Why It Fails | Corrective Move |
|--------------|--------------|-----------------|
| CAP as "pick two" | Partition tolerance is not optional in a real distributed system | State behavior during partition and use PACELC for normal-case latency |
| Timeout proves failure | Slow node and failed node are indistinguishable in async networks | Treat timeout as suspicion, not proof |
| Exactly-once transport | End-to-end side effects can be retried after partial success | Use idempotent receivers and transactional dedupe |
| Lease without fencing | Paused old leader can write after losing the lease | Enforce monotonic token at the resource |
| CRDT for money balance | Invariants do not commute under arbitrary merge | Coordinate the invariant with consensus/transaction |
| Wall clock for causality | Clock skew and concurrency break event ordering | Use logical/vector clocks or session guarantees |
| Majority quorum by count only | Zones, racks, or regions may fail together | Model failure domains and reconfiguration |
| Trusting the vendor's recommended configuration for durability | Recommended defaults are tuned for benchmark performance, not for surviving correlated crashes. Jepsen's MariaDB Galera Cluster 12.1.2 report (2026-03) found the documented recommended setting acknowledged commits before flushing, silently losing committed transactions on coordinated node crashes | Read what each durability flag actually does at the storage layer; test the configuration you will actually deploy, under correlated (not just single-node) crashes |
| Verified spec, unverified binary | A TLA+ model or safety proof constrains the specification; production runs the implementation. The spec-to-code gap is where most real consensus bugs live | Close the gap explicitly: conformance testing against the spec, deterministic simulation over the real binary, or an external black-box consistency report — see the evidence hierarchy in `formal-theory-map.md` |
| Recovery load planned as steady-state load | Reconnect, lease-renewal, and cache-refill storms after an outage can exceed normal peak by an order of magnitude and cause a second, longer outage — the AWS us-east-1 October 2025 cascade is the reference case | Capacity-plan and load-test the *recovery* path separately; add backoff, jitter, and admission control to reconnection and lease-renewal paths, not just to request paths |
| Dual-write without outbox | Writing to the database and publishing to the broker in two separate operations creates a split-brain window: a crash between the two writes leaves one durable and the other lost — breaking at-least-once delivery | Use the transactional outbox pattern: write the mutation and the outbox row in the same DB transaction; relay publishes from the outbox via CDC or polling; consumers still implement idempotent receivers (#7) |

## Known Traps

- Reconfiguration trap: old and new quorums must overlap safely.
- Snapshot trap: compacting logs must preserve membership and term metadata.
- Read trap: reading from a follower can violate a stronger advertised model.
- Retry trap: retries after timeout may duplicate writes even when the first write succeeded.
- Clock trap: synchronized clocks can bound uncertainty but do not remove causality requirements.
- CRDT tombstone trap: set CRDTs may grow metadata unless compaction is designed. Harder still under end-to-end encryption, where the server cannot inspect what it is collecting.
- Control-plane trap: the automation that manages replicas, DNS, leases, and membership is itself a distributed system, and is usually less tested than the data plane it manages. Most recent large-scale outages originate there.
- Ordering-fairness trap: consensus fixes *an* order, not a fair one. Where order position carries value, agreement and liveness can both hold while the ordering is systematically biased.

## Compact Review Sequence

1. Name the failure model.
2. Name the timing model.
3. Name the consistency model.
4. Identify the operation that must be safe under retry.
5. Identify the quorum or merge rule.
6. Check leader handoff and fencing.
7. Check partition behavior.
8. Check reconfiguration behavior.
9. List allowed anomalies.
10. Add tests that reproduce duplicates, partitions, pauses, and stale reads.
