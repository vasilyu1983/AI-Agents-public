# Webhook Reliability Engineering

Patterns for building reliable webhook processing systems. Covers idempotency, retry handling, dead letter queues, monitoring, event ordering, signature verification, queue-based processing, testing, multi-environment routing, and API version migration.

---

## Why Webhook Reliability Matters

Webhooks are the source of truth for payment state. A missed or double-processed webhook means lost revenue, incorrect subscription states, or duplicate charges. Unlike API calls where the client controls retry logic, webhook delivery is controlled by the sender (Stripe, Paddle, etc.). Your handler must be resilient to every delivery scenario.

| Failure Mode | Impact | Mitigation |
|-------------|--------|-----------|
| Handler crashes | Event lost until retry | Return 500, Stripe retries |
| Handler succeeds but DB fails | Inconsistent state | Transactional processing |
| Duplicate delivery | Double-counted revenue | Idempotency |
| Out-of-order events | Wrong final state | Event timestamp comparison |
| Handler too slow | Timeout, retry storm | Queue-based processing |
| Signature not verified | Replay attacks, spoofing | Always verify signature |

---

## Idempotency Key Design

### Strategy 1: Event ID (Recommended)

Use the Stripe event ID as the idempotency key. Each event has a unique ID that is stable across retries.

```typescript
async function processWebhookEvent(event: Stripe.Event): Promise<boolean> {
  // Check if we've already processed this event
  const existing = await db.webhookEvents.findByStripeEventId(event.id);
  if (existing?.status === 'processed') {
    console.log(`[webhook] Skipping duplicate event: ${event.id}`);
    return true; // Already processed — return 200
  }

  // Record that we're processing this event
  await db.webhookEvents.upsert({
    stripe_event_id: event.id,
    event_type: event.type,
    status: 'processing',
    received_at: new Date(),
  });

  try {
    await routeEvent(event);

    await db.webhookEvents.update(event.id, {
      status: 'processed',
      processed_at: new Date(),
    });

    return true;
  } catch (error) {
    await db.webhookEvents.update(event.id, {
      status: 'failed',
      error_message: error instanceof Error ? error.message : 'Unknown error',
      failed_at: new Date(),
    });

    throw error; // Re-throw so webhook returns 500 for retry
  }
}
```

### Strategy 2: Metadata Hash

For events where the same logical change might produce different event IDs (e.g., subscription updates), use a hash of the meaningful data.

```typescript
function computeIdempotencyKey(event: Stripe.Event): string {
  switch (event.type) {
    case 'customer.subscription.updated': {
      const sub = event.data.object as Stripe.Subscription;
      // Same subscription + same status + same price = same logical event
      return createHash('sha256')
        .update(`${sub.id}:${sub.status}:${sub.items.data[0]?.price?.id}`)
        .digest('hex');
    }
    default:
      return event.id; // Use event ID for most events
  }
}
```

### Database Schema for Idempotency

```sql
CREATE TABLE webhook_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  stripe_event_id TEXT UNIQUE NOT NULL,
  event_type TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'received'
    CHECK (status IN ('received', 'processing', 'processed', 'failed', 'dead_letter')),
  idempotency_key TEXT,
  received_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  processed_at TIMESTAMPTZ,
  failed_at TIMESTAMPTZ,
  error_message TEXT,
  retry_count INTEGER DEFAULT 0,
  payload JSONB -- Store full event payload for debugging
);

CREATE INDEX idx_webhook_events_stripe_id ON webhook_events(stripe_event_id);
CREATE INDEX idx_webhook_events_status ON webhook_events(status) WHERE status != 'processed';
CREATE INDEX idx_webhook_events_type ON webhook_events(event_type, received_at DESC);
```

### Deduplication Window

```typescript
// Clean up old processed events to prevent unbounded table growth
// Keep failed and dead_letter events longer for debugging

// Cron job: daily cleanup
async function cleanupProcessedEvents(): Promise<void> {
  const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);
  const ninetyDaysAgo = new Date(Date.now() - 90 * 24 * 60 * 60 * 1000);

  // Remove old successful events
  await db.webhookEvents.deleteWhere({
    status: 'processed',
    processed_at: { lt: thirtyDaysAgo },
  });

  // Remove old failed events (keep longer for forensics)
  await db.webhookEvents.deleteWhere({
    status: 'failed',
    failed_at: { lt: ninetyDaysAgo },
  });
}
```

---

## Retry Handling

### Stripe Retry Schedule

| Attempt | Timing | Total Elapsed |
|---------|--------|---------------|
| 1 | Immediate | 0 |
| 2 | ~1 hour | 1 hour |
| 3 | ~2 hours | 3 hours |
| 4 | ~4 hours | 7 hours |
| 5 | ~8 hours | 15 hours |
| 6 | ~16 hours | 31 hours |
| 7 | ~24 hours | 55 hours |
| 8 | ~24 hours | 79 hours (~3 days) |

After ~3 days of failures, Stripe stops retrying and marks the event as failed.

### Response Codes and Their Meaning

| Code | Stripe Behaviour | When to Return |
|------|-----------------|---------------|
| 2xx | Event processed, no retry | Handler succeeded |
| 4xx | Event failed, no retry | Bad request (invalid signature, malformed) |
| 5xx | Event failed, will retry | Handler error (DB down, timeout) |
| Timeout (>30s) | Treated as failure, will retry | Handler too slow |

### Handler Timeout Strategy

```typescript
// WRONG: Processing everything synchronously in the webhook handler
export async function POST(request: NextRequest) {
  const event = await verifyAndParseEvent(request);

  // This might take 10+ seconds for complex operations
  await processSubscriptionChange(event);      // DB operations
  await sendNotificationEmail(event);          // Email API
  await updateAnalytics(event);               // Analytics API
  await syncToExternalCRM(event);             // CRM API

  return NextResponse.json({ received: true }); // Might timeout
}

// CORRECT: Quick acknowledgment, queue for processing
export async function POST(request: NextRequest) {
  const event = await verifyAndParseEvent(request);

  // Record event for processing (fast — just a DB insert)
  await db.webhookEvents.insert({
    stripe_event_id: event.id,
    event_type: event.type,
    status: 'received',
    payload: event,
  });

  // Return immediately — process asynchronously
  return NextResponse.json({ received: true });
}
```

---

## Dead Letter Queues

### Purpose

A dead letter queue (DLQ) captures events that failed processing after all retries. This prevents data loss and enables manual investigation and replay.

### Implementation

```typescript
// Move permanently failed events to dead letter
async function moveToDeadLetter(eventId: string, reason: string): Promise<void> {
  await db.webhookEvents.update(eventId, {
    status: 'dead_letter',
    error_message: reason,
    failed_at: new Date(),
  });

  // Alert operations team
  await alertSlack({
    channel: '#billing-alerts',
    text: `Dead letter webhook: ${eventId} — ${reason}`,
    severity: 'high',
  });
}

// Manual replay from dead letter queue
async function replayDeadLetterEvent(eventId: string): Promise<void> {
  const event = await db.webhookEvents.findById(eventId);
  if (!event || event.status !== 'dead_letter') {
    throw new Error(`Event ${eventId} not found in dead letter queue`);
  }

  // Reset status and re-process
  await db.webhookEvents.update(eventId, {
    status: 'processing',
    retry_count: event.retry_count + 1,
  });

  try {
    await routeEvent(event.payload as Stripe.Event);
    await db.webhookEvents.update(eventId, {
      status: 'processed',
      processed_at: new Date(),
    });
  } catch (error) {
    await db.webhookEvents.update(eventId, {
      status: 'dead_letter',
      error_message: error instanceof Error ? error.message : 'Unknown',
    });
    throw error;
  }
}

// Admin API: list and replay dead letter events
export async function GET() {
  const deadLetters = await db.webhookEvents.findByStatus('dead_letter', {
    orderBy: 'received_at',
    limit: 100,
  });

  return NextResponse.json({ events: deadLetters });
}

export async function POST(request: NextRequest) {
  const { eventId } = await request.json();
  await replayDeadLetterEvent(eventId);
  return NextResponse.json({ replayed: true });
}
```

---

## Webhook Monitoring

### Key Metrics

| Metric | Target | Alert Threshold | How to Measure |
|--------|--------|----------------|---------------|
| **Delivery success rate** | > 99.5% | < 98% | 2xx responses / total received |
| **Processing time (p95)** | < 5s | > 10s | Time from receipt to processed |
| **Failed events (last 1h)** | 0 | > 5 | Count status=failed |
| **Dead letter queue size** | 0 | > 0 | Count status=dead_letter |
| **Event processing lag** | < 30s | > 5m | Time from Stripe creation to processing |
| **Duplicate rate** | < 5% | > 10% | Duplicates detected / total |

### Monitoring Dashboard Queries

```sql
-- Events processed in last hour by status
SELECT status, COUNT(*), AVG(EXTRACT(EPOCH FROM (processed_at - received_at))) as avg_processing_seconds
FROM webhook_events
WHERE received_at > NOW() - INTERVAL '1 hour'
GROUP BY status;

-- Failed events with error details
SELECT stripe_event_id, event_type, error_message, retry_count, failed_at
FROM webhook_events
WHERE status IN ('failed', 'dead_letter')
  AND failed_at > NOW() - INTERVAL '24 hours'
ORDER BY failed_at DESC;

-- Event volume by type (last 24h)
SELECT event_type, COUNT(*), AVG(retry_count) as avg_retries
FROM webhook_events
WHERE received_at > NOW() - INTERVAL '24 hours'
GROUP BY event_type
ORDER BY COUNT(*) DESC;

-- Processing time percentiles
SELECT
  percentile_cont(0.50) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (processed_at - received_at))) as p50,
  percentile_cont(0.95) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (processed_at - received_at))) as p95,
  percentile_cont(0.99) WITHIN GROUP (ORDER BY EXTRACT(EPOCH FROM (processed_at - received_at))) as p99
FROM webhook_events
WHERE status = 'processed' AND processed_at > NOW() - INTERVAL '1 hour';
```

### Alerting Rules

```yaml
# Example Datadog/Grafana alert rules
alerts:
  - name: webhook_failure_rate
    condition: webhook_success_rate < 0.98
    window: 15m
    severity: critical
    notify: "#billing-alerts"

  - name: dead_letter_queue_growing
    condition: dead_letter_count > 0
    window: 5m
    severity: high
    notify: "#billing-alerts"

  - name: webhook_processing_slow
    condition: webhook_p95_seconds > 10
    window: 15m
    severity: warning
    notify: "#billing-alerts"

  - name: no_webhooks_received
    condition: webhook_received_count == 0
    window: 30m
    severity: critical
    notify: "#billing-alerts, @oncall"
```

---

## Event Ordering

### The Ordering Problem

Stripe does not guarantee event ordering. You may receive `customer.subscription.updated` (status=active) before `customer.subscription.created`, or `invoice.payment_succeeded` after `customer.subscription.deleted`.

### Solution: Use Event Timestamps

```typescript
// Always compare event creation time before applying state changes
async function handleSubscriptionUpdated(
  subscription: Stripe.Subscription,
  eventCreated: number, // Unix timestamp from event.created
): Promise<void> {
  const userId = subscription.metadata.user_id;
  if (!userId || !isValidUUID(userId)) return;

  const existing = await db.subscriptions.findByUserId(userId);

  // Skip if we've already processed a newer event for this subscription
  if (existing?.last_event_at && new Date(existing.last_event_at) >= new Date(eventCreated * 1000)) {
    console.log(`[webhook] Skipping stale event for user ${userId}`);
    return;
  }

  await db.subscriptions.upsert({
    user_id: userId,
    tier: mapPriceToTier(subscription.items.data[0]?.price?.id),
    status: mapStripeStatus(subscription.status),
    current_period_start: new Date(subscription.current_period_start * 1000),
    current_period_end: new Date(subscription.current_period_end * 1000),
    cancel_at_period_end: subscription.cancel_at_period_end,
    last_event_at: new Date(eventCreated * 1000),
    updated_at: new Date(),
  });
}
```

### Add to Schema

```sql
ALTER TABLE subscriptions ADD COLUMN last_event_at TIMESTAMPTZ;
```

---

## Signature Verification

### Timing-Safe Comparison

Stripe's `constructEvent` method internally uses timing-safe comparison. Always use it rather than manual verification.

```typescript
// CORRECT: Use Stripe's built-in verification
const event = stripe.webhooks.constructEvent(
  body,       // Raw request body (string, not parsed JSON)
  signature,  // stripe-signature header
  webhookSecret,
);

// WRONG: Manual verification (timing attack vulnerable)
const expectedSignature = crypto
  .createHmac('sha256', webhookSecret)
  .update(body)
  .digest('hex');
if (signature !== expectedSignature) { /* ... */ } // Timing attack!
```

### Replay Prevention

Stripe signatures include a timestamp. Verify the timestamp is recent to prevent replay attacks.

```typescript
// Stripe's constructEvent has a default tolerance of 300 seconds (5 min)
// You can customise it:
const event = stripe.webhooks.constructEvent(
  body,
  signature,
  webhookSecret,
  300, // tolerance in seconds (default)
);

// For stricter environments:
const event = stripe.webhooks.constructEvent(
  body,
  signature,
  webhookSecret,
  60, // Only accept events from the last 60 seconds
);
```

### Raw Body Requirement

The signature is computed over the raw request body. Parsing and re-serialising the body will break verification.

```typescript
// Next.js App Router: body is already raw
export async function POST(request: NextRequest) {
  const body = await request.text(); // Raw body for signature verification
  const signature = request.headers.get('stripe-signature')!;
  const event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  // ...
}

// Express: must use raw body parser
app.post('/webhook',
  express.raw({ type: 'application/json' }), // NOT express.json()
  (req, res) => {
    const event = stripe.webhooks.constructEvent(
      req.body,
      req.headers['stripe-signature'],
      webhookSecret,
    );
    // ...
  }
);
```

---

## Queue-Based Webhook Processing

### Architecture

```text
┌─────────────┐     ┌──────────────┐     ┌───────────────┐
│  Stripe      │────>│  Webhook     │────>│  Message Queue │
│  Webhook     │     │  Receiver    │     │  (SQS/Redis)   │
└─────────────┘     │  (fast 200)  │     └───────┬───────┘
                    └──────────────┘             │
                                                 ▼
                                      ┌──────────────────┐
                                      │  Queue Consumer   │
                                      │  (process events) │
                                      └──────────────────┘
```

### Implementation with Bull/BullMQ (Redis)

```typescript
import { Queue, Worker } from 'bullmq';

// Webhook receiver: fast acknowledgement
const webhookQueue = new Queue('stripe-webhooks', {
  connection: { host: 'localhost', port: 6379 },
});

export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get('stripe-signature')!;

  // Verify signature (fast)
  const event = stripe.webhooks.constructEvent(body, signature, webhookSecret);

  // Enqueue for processing (fast)
  await webhookQueue.add(event.type, {
    eventId: event.id,
    eventType: event.type,
    payload: event,
  }, {
    jobId: event.id, // Idempotency via job ID
    attempts: 3,
    backoff: { type: 'exponential', delay: 5000 },
  });

  return NextResponse.json({ received: true });
}

// Queue consumer: process at own pace
const worker = new Worker('stripe-webhooks', async (job) => {
  const event = job.data.payload as Stripe.Event;
  await routeEvent(event);
}, {
  connection: { host: 'localhost', port: 6379 },
  concurrency: 5,
});

worker.on('failed', (job, err) => {
  if (job && job.attemptsMade >= job.opts.attempts!) {
    // Move to dead letter
    moveToDeadLetter(job.data.eventId, err.message);
  }
});
```

---

## Testing Webhook Reliability

### Stripe CLI for Local Testing

```bash
# Forward webhooks to local endpoint
stripe listen --forward-to localhost:3000/api/stripe/webhook

# Trigger specific events
stripe trigger checkout.session.completed
stripe trigger invoice.payment_failed
stripe trigger customer.subscription.updated

# Replay a specific event from Stripe Dashboard
stripe events resend evt_1234567890
```

### Chaos Testing

```typescript
// Test webhook handler resilience
describe('Webhook Reliability', () => {
  it('handles duplicate events idempotently', async () => {
    const event = createMockEvent('checkout.session.completed');

    // Process same event twice
    await processWebhookEvent(event);
    await processWebhookEvent(event);

    // Should only create one subscription record
    const subs = await db.subscriptions.findByUserId(event.data.object.metadata.user_id);
    expect(subs).toHaveLength(1);
  });

  it('handles out-of-order events correctly', async () => {
    const userId = 'user_123';

    // Send "updated" before "created"
    await processWebhookEvent(createMockEvent('customer.subscription.updated', {
      status: 'active',
      created: 1000002,
    }));
    await processWebhookEvent(createMockEvent('customer.subscription.created', {
      status: 'trialing',
      created: 1000001,
    }));

    // Final state should be "active" (newer event wins)
    const sub = await db.subscriptions.findByUserId(userId);
    expect(sub.status).toBe('active');
  });

  it('recovers from DB failure', async () => {
    const event = createMockEvent('invoice.payment_succeeded');

    // Simulate DB failure
    jest.spyOn(db.subscriptions, 'update').mockRejectedValueOnce(new Error('DB timeout'));

    // Should throw (return 500 so Stripe retries)
    await expect(processWebhookEvent(event)).rejects.toThrow();

    // Retry should succeed
    jest.spyOn(db.subscriptions, 'update').mockRestore();
    await processWebhookEvent(event);

    const sub = await db.subscriptions.findByUserId(event.data.object.metadata.user_id);
    expect(sub.status).toBe('active');
  });
});
```

---

## Multi-Environment Webhook Routing

### Environment Configuration

| Environment | Webhook Endpoint | Webhook Secret | Stripe Mode |
|-------------|-----------------|----------------|-------------|
| Development | `localhost:3000/api/stripe/webhook` | `whsec_dev_...` | Test mode |
| Staging | `staging.yourdomain.com/api/stripe/webhook` | `whsec_staging_...` | Test mode |
| Production | `yourdomain.com/api/stripe/webhook` | `whsec_prod_...` | Live mode |

### Stripe CLI for Development

```bash
# Use Stripe CLI for local development
stripe listen --forward-to localhost:3000/api/stripe/webhook

# The CLI provides a temporary webhook secret (whsec_...)
# Use this in your .env.local
STRIPE_WEBHOOK_SECRET=whsec_... # From stripe listen output
```

### Webhook Registration

```bash
# Register staging webhook via Stripe CLI
stripe webhook_endpoints create \
  --url "https://staging.yourdomain.com/api/stripe/webhook" \
  --events checkout.session.completed,customer.subscription.created,customer.subscription.updated,customer.subscription.deleted,invoice.payment_succeeded,invoice.payment_failed

# List registered endpoints
stripe webhook_endpoints list
```

---

## Webhook API Version Migration

### Handling Version Changes

When upgrading Stripe API versions, webhook event shapes may change. Handle this gracefully.

```typescript
// Version-aware webhook handler
function getSubscriptionIdFromInvoice(invoice: Stripe.Invoice): string | null {
  // New format (2025-11-17.clover+)
  if (invoice.parent?.subscription_details) {
    const sub = invoice.parent.subscription_details.subscription;
    return typeof sub === 'string' ? sub : sub?.id || null;
  }

  // Legacy format (pre-2025)
  if (typeof (invoice as any).subscription === 'string') {
    return (invoice as any).subscription;
  }

  return null;
}

// Migration checklist for API version upgrade
// 1. Pin new version in Stripe client
// 2. Update type definitions
// 3. Add version-aware field access (like above)
// 4. Test with Stripe CLI using new version
// 5. Deploy webhook handler update BEFORE changing Stripe Dashboard API version
// 6. Update Dashboard API version
// 7. Remove legacy field access after confirming all events use new format
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No idempotency | Double-processing on retry | Track event IDs, skip duplicates |
| Slow webhook handler | Timeouts, retry storms | Queue-based processing, fast 200 response |
| Returning 200 on failure | Event marked as processed, never retried | Return 500 so Stripe retries |
| No dead letter queue | Permanently failed events are lost | Capture failed events for manual replay |
| Manual signature verification | Timing attack vulnerability | Use `stripe.webhooks.constructEvent()` |
| No monitoring | Silent failures go undetected | Dashboard + alerting on failure rate |
| Parsed body for verification | Signature mismatch | Use raw body (`request.text()`) |
| No event ordering protection | Stale events overwrite newer state | Compare event timestamps |
| Same webhook secret across environments | Security risk | Separate secrets per environment |

---

## Cross-References

- [stripe-patterns.md](stripe-patterns.md) — Webhook handler architecture, handler contracts, idempotency patterns
- [subscription-lifecycle.md](subscription-lifecycle.md) — Subscription states, webhook events per transition
- [regional-pricing-guide.md](regional-pricing-guide.md) — Webhook handling for multi-currency events
- [testing-patterns.md](testing-patterns.md) — Stripe CLI testing, event triggering
- [platform-comparison.md](platform-comparison.md) — Webhook behaviour per payment platform
