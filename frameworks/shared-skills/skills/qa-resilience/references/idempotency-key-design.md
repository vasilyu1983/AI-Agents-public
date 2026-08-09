# Idempotency Key Design

Practical guidance for making distributed operations safe to retry without producing duplicate side effects.

---

## Table of Contents

- [Why Idempotency Keys](#why-idempotency-keys)
- [Exactly-Once Myth](#exactly-once-myth)
- [Key Derivation Strategies](#key-derivation-strategies)
- [Storage and Deduplication](#storage-and-deduplication)
- [At-Least-Once Handling](#at-least-once-handling)
- [Idempotency Window Selection](#idempotency-window-selection)
- [Stripe-Style Header Pattern](#stripe-style-header-pattern)
- [Schema Example](#schema-example)
- [Pseudocode: Server-Side Dedupe Handler](#pseudocode-server-side-dedupe-handler)
- [Checklist](#checklist)
- [Related Resources](#related-resources)

---

## Why Idempotency Keys

Retries are mandatory in distributed systems. Networks drop packets, processes restart, load balancers time out mid-flight. Without a dedupe mechanism, every retry risks a duplicate side effect: double charge, double email, double ledger entry.

An idempotency key allows a client to safely replay any request. The server records the result of the first successful execution and returns the same result for any subsequent request carrying the same key — without re-executing the operation.

---

## Exactly-Once Myth

> **Callout: exactly-once delivery does not exist at the network layer.**
>
> No transport protocol guarantees that a message is delivered and processed exactly once. TCP gives at-most-once delivery when segments are lost; application-level retries yield at-least-once. "Exactly-once" is an application-level illusion achieved by combining at-least-once delivery with idempotent processing and server-side deduplication. Design for at-least-once, dedupe at the receiver.

---

## Key Derivation Strategies

### Option A: Client-supplied key (preferred for HTTP APIs)

The client generates a unique token — a UUID v4 or a ULID — and passes it in a header or request body field. The server treats it as an opaque string.

Advantages:
- Client controls retry safety without coordination with the server.
- Consistent with how Stripe, Adyen, and PayPal model idempotency.
- Works across client restarts (client persists the key until the operation confirms).

Risks:
- Clients must not reuse keys across semantically different requests. A key tied to a UI action (button click UUID) is safer than a key derived from request content alone.

### Option B: Request-derived hash (useful for message queues and async workers)

When the client is a background worker or event consumer that cannot persist state, derive the key from the content of the request using a deterministic hash.

```text
key = sha256(operation_name + "|" + canonical_sort(payload_fields))
```

Advantages:
- Stateless: the worker can recompute the key after a crash.
- Naturally deduplicates identical retransmitted messages.

Risks:
- Two semantically different requests with identical payload fields produce the same key. Add a domain discriminator (operation name, tenant ID, event timestamp) to the hash input.
- Do not hash mutable fields (timestamps, counters) that differ between retries of the same logical operation.

### Choosing Between Them

| Signal | Use client-supplied | Use request-derived hash |
|--------|--------------------|-----------------------|
| HTTP API with interactive client | Yes | No |
| Async worker consuming a queue | No | Yes |
| Message broker with dedup support (SQS FIFO, Kafka) | No | Use broker's built-in dedup ID |
| Idempotency across restarts without client state | No | Yes |

---

## Storage and Deduplication

### Request-ID table with TTL

The most portable approach is a dedicated table (SQL or key-value) that records each key and its result for the duration of the idempotency window.

Minimum schema: see [Schema Example](#schema-example).

### Redis SET NX

For low-latency deduplication, Redis is a common choice. Use `SET NX PX` to atomically claim a key only if it does not exist, with a millisecond TTL equal to the idempotency window.

```text
# Pseudo-command
SET idempotency:{key} {serialized_result} NX PX {window_ms}
```

- `NX` — only set if not exists (atomic claim).
- `PX` — TTL in milliseconds (auto-expire).
- Read back the stored value to return the original response for duplicate requests.

Important: store the serialized response alongside the key, not just a boolean. Returning `200 OK` without the original response body breaks client retries that need the resource ID.

### At-Rest Persistence Requirement

If the idempotency window spans days (see [Idempotency Window Selection](#idempotency-window-selection)), Redis alone is insufficient unless you use persistence (`AOF` or `RDB` with appropriate fsync). A durable SQL table with a TTL-based background cleanup job is more reliable for long windows.

---

## At-Least-Once Handling

The server MUST handle the following lifecycle correctly:

1. **First request arrives** — key not found. Begin execution. Write key to store with status `in_progress` before executing the side effect (not after).
2. **Execution succeeds** — update key record to `completed`, store serialized response.
3. **Duplicate request arrives while in progress** — return `202 Accepted` or `409 Conflict` depending on your API contract. Do not execute again.
4. **Duplicate request arrives after completion** — return the stored response with the original status code. Do not execute again.
5. **Execution fails** — delete the key record or mark it `failed` so the client can retry with the same key. Do not lock the key on failure.

**Key rule:** write the key record before the side effect, not after. Writing after introduces a race where the operation succeeded but the key was not stored — the server will re-execute on the next retry.

---

## Idempotency Window Selection

The idempotency window is the duration for which the server stores a key and guarantees deduplication.

| Use Case | Typical Window | Rationale |
|----------|---------------|-----------|
| Synchronous HTTP payment | 24 hours | Client may retry for minutes; 24h covers overnight batch reconciliation |
| Async event / queue message | 7 days | Message brokers can redeliver for days after an outage |
| Webhook delivery | 24–72 hours | Webhook consumers retry with exponential backoff over hours |
| Idempotent job / worker task | TTL of the job queue + buffer | Match the queue's own visibility timeout + retry window |

**24 hours is the most common default** for synchronous HTTP APIs. It is long enough to cover all practical retry scenarios while keeping storage requirements modest. Use a longer window only when the upstream delivery guarantee exceeds 24 hours.

---

## Stripe-Style Header Pattern

Stripe popularized the `Idempotency-Key` request header as the industry standard for HTTP APIs. This pattern is widely understood by API consumers and client libraries.

**Request (client → server):**

```http
POST /v1/charges HTTP/1.1
Host: api.example.com
Authorization: Bearer sk_live_...
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "amount": 2000,
  "currency": "usd",
  "source": "tok_visa"
}
```

**Response on first execution:**

```http
HTTP/1.1 200 OK
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
X-Idempotency-Replayed: false
Content-Type: application/json

{ "id": "ch_abc123", "status": "succeeded" }
```

**Response on duplicate request (same key):**

```http
HTTP/1.1 200 OK
Idempotency-Key: 550e8400-e29b-41d4-a716-446655440000
X-Idempotency-Replayed: true
Content-Type: application/json

{ "id": "ch_abc123", "status": "succeeded" }
```

Header conventions:
- `Idempotency-Key` — client-supplied opaque string (UUID or ULID recommended, max 255 chars).
- `X-Idempotency-Replayed: true` — signals to the client that this response came from cache, not a new execution.
- Return the original HTTP status code and response body unchanged on replay.

---

## Schema Example

Minimal SQL table for a durable idempotency store:

```sql
CREATE TABLE idempotency_keys (
  key            VARCHAR(255)  PRIMARY KEY,
  tenant_id      VARCHAR(64)   NOT NULL,
  operation      VARCHAR(128)  NOT NULL,
  status         VARCHAR(16)   NOT NULL DEFAULT 'in_progress',
  -- 'in_progress' | 'completed' | 'failed'
  request_hash   CHAR(64),
  -- SHA-256 of the canonical request body; detect key reuse with different payload
  response_code  SMALLINT,
  response_body  TEXT,
  created_at     TIMESTAMPTZ   NOT NULL DEFAULT now(),
  expires_at     TIMESTAMPTZ   NOT NULL,
  -- set to created_at + idempotency_window at insert time
  CONSTRAINT valid_status CHECK (status IN ('in_progress','completed','failed'))
);

CREATE INDEX ON idempotency_keys (expires_at);
-- Used by the background cleanup job: DELETE WHERE expires_at < now()
```

---

## Pseudocode: Server-Side Dedupe Handler

Language-agnostic. Adapt to any HTTP framework.

```text
function handle_request(request):
  key = request.header("Idempotency-Key")

  if key is absent:
    if operation_is_non_idempotent(request):
      return 400 Bad Request, "Idempotency-Key header required"
    else:
      # Idempotency-Key optional for safe methods (GET, HEAD)
      return execute_and_respond(request)

  # Normalize key: trim whitespace, enforce max length
  key = normalize(key)

  existing = store.get(key)

  if existing is not null:
    if existing.status == "in_progress":
      return 409 Conflict, "Request in progress"
    if existing.status == "completed":
      return existing.response_code, existing.response_body,
             header("X-Idempotency-Replayed", "true")
    # status == "failed": fall through and allow retry

  # Payload conflict detection (optional but recommended)
  incoming_hash = sha256(canonical_serialize(request.body))
  if existing is not null and existing.request_hash != incoming_hash:
    return 422 Unprocessable Entity, "Idempotency-Key reused with different payload"

  # Write key BEFORE executing side effect
  store.put(key, {
    tenant_id:    current_tenant(),
    operation:    request.route,
    status:       "in_progress",
    request_hash: incoming_hash,
    expires_at:   now() + IDEMPOTENCY_WINDOW,
  })

  try:
    result = execute_operation(request)
    store.update(key, {
      status:        "completed",
      response_code: result.code,
      response_body: serialize(result.body),
    })
    return result.code, result.body

  catch error:
    store.update(key, { status: "failed" })
    raise error
```

---

## Checklist

- [ ] Client-facing HTTP endpoints that mutate state require `Idempotency-Key`.
- [ ] Key is written to the store before the side effect executes.
- [ ] `in_progress` status blocks concurrent duplicate requests.
- [ ] Failure clears or marks the key `failed` so the client can retry.
- [ ] Replay returns the original status code and response body unchanged.
- [ ] `X-Idempotency-Replayed: true` header is set on replay responses.
- [ ] Payload hash is compared on replay to detect key reuse with different content.
- [ ] Idempotency window is set to at least 24 hours for synchronous HTTP APIs.
- [ ] Background job purges expired keys to prevent unbounded store growth.
- [ ] Redis-backed stores use `SET NX PX` atomically and persist to disk if the window exceeds hours.

---

## Related Resources

- [retry-patterns.md](retry-patterns.md) — Retry semantics and backoff strategies
- [circuit-breaker-patterns.md](circuit-breaker-patterns.md) — Preventing retry storms into broken dependencies
- [resilience-checklists.md](resilience-checklists.md) — Release and production hardening checks
