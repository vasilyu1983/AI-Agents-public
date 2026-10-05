# Execution Histories and Receiver Contract

Use small histories to distinguish the property claimed from the mechanism proposed. `invoke → return` defines operation intervals; successful acknowledgement requires the protocol's durability contract.

| History | Claim and diagnosis | Required evidence |
|---|---|---|
| write(x=1) returns; later read(x) returns0 | Violates linearizability of x; can be allowed under eventual consistency | Ordered invocation/return timestamps, no later overwrite, replica/version provenance |
| Pending write(x=1) reaches A; read1(A,B) returns1; later read2(B,C) returns0 while write remains pending | Fixed N3/R2/W2 intersection alone permits read inversion without a correct atomic read protocol | Read1 completes before read2 invokes; initial B/C=0; no repair or intervening write. A linearizable register must not revert after observing1 |
| write1 and write2 overlap; replicas retain different versions | Overlap does not define the winner; deterministic timestamps can converge while violating a claimed real-time property | State version order, acknowledged sets, conflict/repair protocol and exact guarantee |
| Old configuration {A,B,C} accepts A/B; new {C,D,E} accepts D/E independently | Each majority is local; the successful quorums are disjoint and can commit conflicts | Joint consensus or a protocol-specific safe handoff; membership and durable epoch history |
| charge request times out; retry uses new key; both charge | Timeout is unknown outcome, not definite failure | Stable scoped operation identity, provider lookup/idempotency and durable reconciliation |
| Database mutation+outbox commit; relay publishes; relay crashes before marking sent; publishes again | Allowed at-least-once duplicate; transport does not ensure single business effect | Consumer atomic inbox/effect and independent external-effect idempotency |
| Total-order event e applied at A now and B later, both in same relative order | Allowed; total order does not imply simultaneous delivery | Agreement/order and timing are distinct observations |

## Dedupe / outbox design record

1. Define a stable key from tenant, logical operation and source event identity. Hash the canonical payload; same key/different payload is a conflict, not silent reuse. Define business-semantic dedupe where distinct event ids represent the same operation.
2. Use an atomic unique claim and transactional state transition. Concurrent identical requests return the committed result or explicit in-progress status; never check then execute outside the transaction. Record pending/completed/failed states and response replay policy.
3. Commit the database mutation and outbox row together. Relay delivery is at least once; consumer inbox and local effect share a transaction. Order guarantees require explicit per-entity sequence handling, not only dedupe.
4. An external charge/email cannot generally share the local database transaction. Persist intent, send with the provider's stable idempotency key, then persist receipt. After timeout/crash use provider lookup/reconciliation; do not blindly issue a new operation. If the provider cannot dedupe or resolve status, expose uncertainty and route manual recovery.
5. Set key retention from maximum delivery/retry/reconciliation horizon. After expiry, replay can duplicate effects; choose a business uniqueness constraint, retained tombstone or explicit expiry rejection where required. State what happens if the dedupe store is unavailable.
6. Test concurrent duplicates, payload mismatch, crash before/after commit, publish-before-mark crash, unknown external outcome, expired replay and membership handoff. Record observed histories and the advertised model; passing finite cases is not proof of absence.

Source anchors: [Dynamo](https://www.allthingsdistributed.com/2007/10/amazons_dynamo.html) for quorum-like replication and concurrent versions; [Raft paper](https://raft.github.io/raft.pdf) for configuration transitions. Follow the existing [formal theory map](formal-theory-map.md) for specification versus implementation evidence.
