# Webhook Design and Implementation Patterns

> Operational reference for designing, delivering, and consuming webhooks reliably. Covers event schemas, delivery guarantees, retry logic, security, and testing.

**Freshness anchor:** January 2026 — aligned with Stripe API v2025-12, GitHub Webhooks v3, and current HMAC-SHA256 best practices.

---

## Quick Decision: Webhook vs Polling vs Streaming

| Factor | Webhooks | Polling | SSE / Streaming |
|---|---|---|---|
| Latency | Near real-time (seconds) | Interval-dependent (minutes) | True real-time (ms) |
| Consumer complexity | Medium — must host endpoint | Low — simple GET requests | High — persistent connection |
| Provider complexity | High — delivery, retry, DLQ | Low — stateless | High — connection management |
| Firewall friendliness | Requires inbound port | Fully outbound | Fully outbound |
| Use when | Event-driven integrations, third-party notifications | Simple status checks, low-frequency updates | Dashboards, live feeds, chat |

---

## Event Schema Design

### Schema Structure Checklist

- [ ] Top-level envelope wraps every event type
- [ ] `id` field is globally unique (UUIDv7 preferred for sortability)
- [ ] `type` field uses dot-notation hierarchy (`order.created`, `order.updated`)
- [ ] `created_at` is ISO 8601 with timezone (`2026-01-15T10:30:00Z`)
- [ ] `data` object contains the resource payload
- [ ] `api_version` field pins the schema version used to generate the event
- [ ] No sensitive data in payload unless consumer explicitly opts in

### Envelope Template

```json
{
  "id": "evt_01JKXYZ123456789",
  "type": "invoice.payment_succeeded",
  "api_version": "2026-01",
  "created_at": "2026-01-15T10:30:00Z",
  "data": {
    "object": {
      "id": "inv_abc123",
      "amount": 5000,
      "currency": "usd",
      "status": "paid"
    }
  },
  "livemode": true
}
```

### Versioning Strategy Decision Tree

```
Is this a breaking change to event payload?
├── YES → Bump api_version (e.g., 2026-01 → 2026-02)
│   ├── Support previous version for minimum 12 months
│   ├── Send events using the version each consumer registered with
│   └── Document migration path in changelog
└── NO (additive field, new event type)
    └── Ship without version bump
        └── Consumers MUST ignore unknown fields
```

### Event Type Naming Convention

| Pattern | Example | Use when |
|---|---|---|
| `resource.action` | `customer.created` | Standard CRUD events |
| `resource.sub.action` | `invoice.payment.failed` | Nested resource events |
| `resource.action.qualifier` | `subscription.updated.plan_change` | Distinguishing sub-types |

---

## Delivery Guarantees

### At-Least-Once Delivery (Standard)

- Provider retries until consumer returns 2xx or retries are exhausted
- Consumer MUST be idempotent — duplicate events will arrive
- Provider SHOULD include `delivery_attempt` header for observability
- Provider MUST NOT guarantee ordering across event types

### Retry Strategy: Exponential Backoff

```
Attempt 1: immediate
Attempt 2: 30 seconds
Attempt 3: 2 minutes
Attempt 4: 10 minutes
Attempt 5: 1 hour
Attempt 6: 4 hours
Attempt 7: 24 hours (final)
```

**Implementation checklist:**

- [ ] Jitter added to prevent thundering herd (random 0-25% of delay)
- [ ] Max retry count configurable (default: 7)
- [ ] Total retry window documented for consumers (typically 72 hours)
- [ ] Failed deliveries after exhaustion go to Dead Letter Queue (DLQ)
- [ ] DLQ events retrievable via API for manual replay

### Dead Letter Queue (DLQ) Setup

| Component | Requirement |
|---|---|
| Storage | Durable message store (SQS, Redis Streams, Postgres) |
| Retention | Minimum 30 days |
| Replay | API endpoint to retry individual or batch events |
| Alerting | Notify provider ops when DLQ depth exceeds threshold |
| Consumer visibility | Dashboard or API showing failed deliveries |

---

## Signature Verification (HMAC)

### Provider-Side Signing

```python
import hmac
import hashlib
import time

def sign_webhook(payload_bytes: bytes, secret: str) -> dict:
    timestamp = str(int(time.time()))
    signed_content = f"{timestamp}.{payload_bytes.decode('utf-8')}"
    signature = hmac.new(
        secret.encode("utf-8"),
        signed_content.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    return {
        "X-Webhook-Timestamp": timestamp,
        "X-Webhook-Signature": f"sha256={signature}"
    }
```

### Consumer-Side Verification

```python
import hmac
import hashlib
import time

TOLERANCE_SECONDS = 300  # 5-minute replay window

def verify_webhook(payload: bytes, timestamp: str, signature: str, secret: str) -> bool:
    # 1. Check timestamp freshness (replay attack prevention)
    if abs(time.time() - int(timestamp)) > TOLERANCE_SECONDS:
        return False

    # 2. Recompute signature
    signed_content = f"{timestamp}.{payload.decode('utf-8')}"
    expected = hmac.new(
        secret.encode("utf-8"),
        signed_content.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()

    # 3. Constant-time comparison
    return hmac.compare_digest(f"sha256={expected}", signature)
```

### Signature Verification Checklist

- [ ] Use HMAC-SHA256 (not MD5, not SHA1)
- [ ] Constant-time comparison to prevent timing attacks
- [ ] Timestamp tolerance window (300s recommended)
- [ ] Raw request body used for verification (not parsed/re-serialized JSON)
- [ ] Secret rotation supported (verify against current AND previous secret during rotation window)
- [ ] Return 401 on signature failure (not 400)

---

## Idempotency

### Consumer Idempotency Implementation

```
Receive webhook event
├── Extract event ID from payload
├── Check idempotency store (Redis/DB) for event ID
│   ├── FOUND → Return 200 immediately (already processed)
│   └── NOT FOUND → Process event
│       ├── Execute business logic
│       ├── Store event ID with TTL (minimum 72 hours)
│       └── Return 200
```

### Idempotency Store Options

| Store | TTL support | Performance | Use when |
|---|---|---|---|
| Redis SET with EX | Native | Fast | High-volume, ephemeral ok |
| Postgres unique constraint | Manual cleanup | Medium | Need audit trail |
| DynamoDB with TTL | Native | Fast | AWS-native, serverless |

### Idempotency Key Rules

- Use the provider's `event.id`, not a hash of the payload
- Store the processing result alongside the key for debugging
- TTL must exceed the provider's total retry window
- Log duplicate detections at INFO level (expected behavior, not errors)

---

## Webhook Testing Patterns

### Local Development Testing

| Tool | Purpose | Command |
|---|---|---|
| ngrok | Tunnel to localhost | `ngrok http 3000` |
| Stripe CLI | Forward Stripe events | `stripe listen --forward-to localhost:3000/webhooks` |
| GitHub CLI | Redeliver events | `gh api /repos/{owner}/{repo}/hooks/{id}/deliveries` |
| smee.io | Proxy for GitHub webhooks | `smee -u https://smee.io/xyz --target http://localhost:3000` |

### Automated Testing Checklist

- [ ] Unit test: signature verification with known good/bad signatures
- [ ] Unit test: idempotency (send same event twice, verify single processing)
- [ ] Unit test: each event type handler with fixture payloads
- [ ] Integration test: full delivery flow (send → receive → process → respond)
- [ ] Failure test: handler throws error → returns 500 → provider retries
- [ ] Timeout test: handler exceeds timeout → appropriate error response
- [ ] Security test: invalid signature → 401 response
- [ ] Security test: expired timestamp → 401 response

### Payload Fixture Management

```
tests/
  fixtures/
    webhooks/
      invoice.payment_succeeded.v2026-01.json
      invoice.payment_failed.v2026-01.json
      customer.created.v2026-01.json
```

- Pin fixtures to API versions
- Update fixtures when subscribing to new API version
- Store both happy-path and edge-case payloads

---

## Consumer Best Practices

### Response Time Requirements

| Provider | Timeout | Recommendation |
|---|---|---|
| Stripe | 20 seconds | Respond in <5s, process async |
| GitHub | 10 seconds | Respond in <3s, process async |
| Shopify | 5 seconds | Respond immediately, queue processing |
| General | Varies | Always return 200 before heavy processing |

### Async Processing Pattern

```
1. Receive webhook HTTP request
2. Verify signature
3. Validate event envelope structure
4. Enqueue event to internal queue (SQS, Redis, RabbitMQ)
5. Return 200 OK immediately
6. Worker picks up event from queue
7. Process business logic
8. Handle failures with internal retry
```

### Consumer Endpoint Checklist

- [ ] HTTPS only (no HTTP endpoints)
- [ ] Returns 200/201/204 on success (anything in 2xx)
- [ ] Returns 401 on signature failure
- [ ] Returns 500 on processing error (triggers provider retry)
- [ ] Does NOT return 301/302 redirects (most providers won't follow)
- [ ] Handles unknown event types gracefully (return 200, log, skip)
- [ ] Processes events asynchronously when handler logic exceeds 3 seconds
- [ ] Monitors endpoint uptime and response latency

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|---|---|---|
| Synchronous heavy processing | Timeouts, lost events | Enqueue and process async |
| Relying on event ordering | Events arrive out of order | Use timestamps and state checks |
| No idempotency handling | Duplicate processing on retries | Implement idempotency store |
| Parsing body before signature check | Security vulnerability | Verify signature against raw body first |
| Hardcoded webhook secret | Cannot rotate without downtime | Support multiple active secrets |
| Returning 200 on processing failure | Provider thinks delivery succeeded | Return 500 to trigger retry |
| No DLQ or failure visibility | Silent data loss | Implement DLQ with alerting |
| Webhook secret in query params | Leaks in logs and referrer headers | Use header-based HMAC signatures |
| Not validating timestamp | Replay attack vulnerability | Check timestamp within tolerance window |
| Filtering events client-side only | Unnecessary traffic and processing | Configure event types at subscription level |

---

## Cross-References

- `dev-api-design/references/api-testing-patterns.md` — contract testing for webhook payloads
- `dev-api-design/references/real-time-api-patterns.md` — when to use WebSocket/SSE instead of webhooks
- `software-backend/references/message-queues-background-jobs.md` — async processing infrastructure
- `software-security-appsec/references/api-security-patterns.md` — endpoint security patterns
- `qa-resilience/references/cascading-failure-prevention.md` — failure isolation for webhook consumers
