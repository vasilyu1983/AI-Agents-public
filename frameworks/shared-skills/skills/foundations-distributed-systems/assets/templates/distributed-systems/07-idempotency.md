# Primitive 7: Idempotency

**Sources**: Kleppmann 2017; industry practice (Stripe, AWS, Twilio).

---

## Definition

An operation is **idempotent** if applying it multiple times produces the same result as applying it once: `f(f(x)) = f(x)`.

In distributed systems, **at-least-once delivery** is the tractable delivery guarantee — messages may be delivered more than once due to retries, network timeouts, or producer restarts. Transport delivery alone does not establish exactly-once business effects; FLP is a consensus-termination result, not a universal exactly-once impossibility theorem. The idempotency pattern creates the **illusion of exactly-once** semantics by designing receivers to be safe against duplicate processing.

**Pattern**:
1. **Idempotency key**: A client-generated, globally unique identifier attached to every write request (UUID, ULID, or hash of content + nonce).
2. **Deduplicate store**: A persistent record of all processed idempotency keys (key → result).
3. **Atomic check-and-execute**: Before processing, check whether the key is already in the dedupe store. If yes, return the stored result. If no, execute the operation and store the key + result atomically.
4. **At-least-once delivery**: The transport retries until acknowledged. The receiver's dedupe store absorbs duplicates.

**Idempotent by design** (no dedupe store required):
- Pure functions (same inputs → same outputs, no side effects).
- SET operations (setting a field to a specific value is idempotent; incrementing is not).
- DELETE operations (deleting an already-deleted record is a no-op).

---

## When to Use

- Payment APIs, webhook receivers, email sends, SMS — anywhere a duplicate causes harm.
- Message queue consumers (Kafka, SQS, Pub/Sub) with at-least-once delivery.
- Distributed saga steps that may be retried after a partial failure.
- Any HTTP POST/PATCH that mutates state and may be retried by the client or an intermediary proxy.

---

## Inputs

| Input | Description |
|-------|-------------|
| Idempotency key | Client-provided UUID; scoped to the operation type and user/account |
| Dedupe store | Persistent key-value store (Redis, DynamoDB, PostgreSQL) with TTL |
| At-least-once transport | The delivery mechanism that may deliver the same message multiple times |
| Operation result | Cached completed response; explicit in-progress reconciliation behavior, never blind side-effect re-execution |

---

## Outputs

| Output | Description |
|--------|-------------|
| At-most-once execution | At most one committed effect within the stated atomicity boundary; at-most-once does not imply eventual completion |
| Stable response | Duplicate requests return the same response as the first successful request |
| Audit trail | The dedupe store provides a record of all processed operations |

---

## Failure Modes

| Failure | Cause | Consequence |
|---------|-------|-------------|
| Non-atomic check-and-execute | Gap between "check if key exists" and "store key" allows a concurrent duplicate to slip through | Double processing under concurrent retries |
| Idempotency key scoped too broadly | One key covers multiple operations; a duplicate key hits the dedupe store but the operations are different | Wrong cached result returned |
| Unspecified retention | Indefinite keys may exhaust capacity; premature expiry permits replay | Choose retention/archival from replay horizon and obligations |
| Unpersisted/new retry key | A retry receives a fresh operation ID after ambiguous completion | Duplicate processing; generated IDs are safe if persisted and reused before dispatch |
| Assuming PUT is idempotent in all contexts | PUT is idempotent for full-object replacement but not for conditional updates | Conditional updates (if-match ETags) require additional concurrency control |

---

## Worked Example

**Scenario**: A payment API. The client sends `POST /payments` with `{"amount": 100, "idempotency_key": "order-42-pay-1"}`. The network drops the response. The client retries.

**Without idempotency**: Two payments of £100 are charged.

**With idempotency**:
1. First request atomically reserves key `"order-42-pay-1"` bound to account/amount. For an external provider, dispatch using the same provider idempotency key; persist its result or reconcile status after ambiguous completion.
2. Response is dropped. Client retries with the same key.
3. Second request arrives. Server checks: key `"order-42-pay-1"` is in dedupe store. Returns the cached result `{payment_id: "pmt_7x9", status: "succeeded"}` without re-executing the charge.
4. Client receives a success response. Single charge occurred.

**Atomicity**: A database transaction can atomically commit a local ledger mutation and dedupe record only when both live in that transaction. It cannot roll back an unrelated provider charge. Crash after provider acceptance but before result persistence requires same-key provider retry/status reconciliation; absent that support, report unknown outcome and avoid a fresh-key blind retry.

---

## Production Pattern: Transactional Outbox

The atomic local-effect/dedupe transaction protects its stated commit boundary, including concurrent requests when correctly serialized. The **transactional outbox** is the production implementation that extends this guarantee across a database boundary to a message broker.

**Problem**: A naive "dual-write" — write to the database AND publish to the broker in two separate operations — creates a split-brain window: if the process crashes between the two writes, the database is updated but the event is never published (or vice versa). This breaks at-least-once delivery.

**Pattern**:
1. Write the business mutation AND an `outbox` record to the same database transaction. The outbox row contains: `{id, operation_type, payload, created_at, published_at: null}`.
2. On transaction commit, both the mutation and the outbox row are durable atomically.
3. A separate relay process reads unpublished outbox rows (via CDC — Change Data Capture, e.g. Debezium — or polling) and publishes them to the broker.
4. On successful broker acknowledgement, the relay marks the outbox row `published_at = now()`.

**Key properties**:
- Outbox guarantees **at-least-once delivery to the broker** — the relay may publish the same row more than once on retry, so consumers must still implement idempotent receivers.
- CDC-based relay (Debezium, AWS EventBridge Pipes) reads the database WAL directly, avoiding polling overhead and achieving near-real-time propagation.
- Polling-based relay is simpler to implement but adds latency proportional to the poll interval.

**Trade-offs**:
| Approach | Latency | Throughput | Operational complexity |
|----------|---------|------------|------------------------|
| CDC relay (Debezium) | Near-real-time | High | Requires WAL access, connector infra |
| Polling relay | Poll interval | Medium | Simple — single query loop |
| Dual-write (no outbox) | Lowest | Highest | Fragile — split-brain window on crash |

**Anti-pattern**: Do not write to the database and publish to the broker in two separate operations (dual-write without outbox). One will succeed and the other may not; there is no atomic rollback across them.

**Sources**: microservices.io/patterns/data/transactional-outbox.html; AWS Prescriptive Guidance (docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/transactional-outbox.html); Debezium open source (debezium.io).

---

## Sources

- Kleppmann, M. (2017). Designing Data-Intensive Applications, Chapter 11 (stream processing and exactly-once). [dataintensive.net](https://dataintensive.net/)
- Stripe Engineering. Idempotent Requests. [stripe.com/docs/api/idempotent_requests](https://stripe.com/docs/api/idempotent_requests)
- AWS. Idempotency for API Gateway and Lambda. [docs.aws.amazon.com/lambda/latest/dg/invocation-idempotency.html](https://docs.aws.amazon.com/lambda/latest/dg/invocation-idempotency.html)
