# Stripe Implementation Patterns

Detailed patterns, error handling, and lessons learned from production Stripe integrations.

---

## Webhook Handler Architecture

### Handler Module Organization

Organize webhook handlers by domain in separate files:

```
lib/stripe/
  index.ts              # Client init, types, tier model, feature matrix
  client.ts             # Browser-side Stripe.js loader
  handlers/
    index.ts            # Re-export all handlers
    types.ts            # Shared types (WebhookContext, status mapping, UUID validation)
    checkout.ts          # checkout.session.completed, checkout.session.expired
    subscription.ts      # subscription.created, subscription.updated, subscription.deleted
    invoice.ts           # invoice.payment_succeeded, invoice.payment_failed
    referral.ts          # Referral reward processing
```

### Handler Contract

Each handler:
1. Receives the Stripe event object + a DB client
2. Extracts relevant data (customer ID, user ID from metadata)
3. Validates user_id format (UUID regex)
4. Upserts data to the database (idempotent)
5. Tracks analytics events
6. Throws on DB errors (so webhook returns 500 and Stripe retries)

### UUID Validation

Always validate `metadata.user_id` before using it in DB queries:

```typescript
const UUID_REGEX = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;

export function isValidUUID(userId: string): boolean {
  return UUID_REGEX.test(userId);
}

// In handler:
if (!userId || !isValidUUID(userId)) {
  log.error('Invalid user_id in metadata', { sessionId, userId });
  throw new Error('Invalid user_id format');
}
```

---

## Error Handling Patterns

### Structured Logging for Webhooks

```typescript
const log = stripeLogger.child({ handler: 'checkout' });

// Always include event context in logs
log.error('DB upsert failed', {
  event: 'checkout.session.completed',
  sessionId: session.id,
  userId,
  customerId,
}, error);
```

### Error Categories

| Error Type | Action | Retry? |
|-----------|--------|--------|
| Signature verification failed | Return 400 | No (client error) |
| Missing metadata (user_id) | Log + throw | Yes (Stripe retries) |
| DB upsert failed | Log + throw | Yes |
| Analytics capture failed | Log + continue | No (non-critical) |
| Stripe API rate limit | Exponential backoff | Yes |
| Card declined | Return error to user | No |

### Webhook Response Strategy

```
200: Event processed successfully
400: Bad request (missing signature, malformed payload)
500: Handler failed (Stripe will retry for 3 days)
```

Never return 200 for an event you failed to process — Stripe needs to know to retry.

---

## Trial Management

### Trial Qualification Logic

```typescript
// Only first-time subscribers get a trial
const hasHadPaidSubscription = subscription?.tier && subscription.tier !== 'free';
const trialDays = hasHadPaidSubscription ? undefined : 7;
```

### Trial Events Timeline

```
Day 0: trial_started (subscription.created with status='trialing')
Day 4: trial_will_end (3 days before expiry — send retention email)
Day 7: subscription becomes 'active' (first charge) or 'canceled' (no card)
```

---

## Proration Strategies

| Strategy | Use When | Stripe Setting |
|----------|----------|----------------|
| `create_prorations` | Upgrades (charge difference) | Default, fairest |
| `none` | Downgrades (wait until next period) | Prevents credits |
| `always_invoice` | Immediate billing change | Instant charge |

---

## Subscription Database Schema

```sql
CREATE TABLE subscriptions (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id),
  stripe_customer_id TEXT,
  stripe_subscription_id TEXT,
  stripe_price_id TEXT,
  tier TEXT NOT NULL DEFAULT 'free',
  status TEXT NOT NULL DEFAULT 'active',
  billing_interval TEXT DEFAULT 'month',
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  canceled_at TIMESTAMPTZ,
  trial_start TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for webhook lookups (customer ID -> user)
CREATE INDEX idx_subscriptions_stripe_customer
  ON subscriptions(stripe_customer_id);
```

---

## Handling Duplicate Subscriptions

Prevent users from having multiple active subscriptions:

```typescript
// Before creating checkout, check for existing active subscription
if (hasActivePaidSubscription && existingSubscriptionId) {
  // Use upgrade flow instead of new checkout
  await stripe.subscriptions.update(existingSubscriptionId, {
    items: [{ id: existingItemId, price: newPriceId }],
    proration_behavior: 'create_prorations',
  });
  return; // Skip checkout creation
}
```

---

## HTTPS Enforcement

```typescript
let appUrl = process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000';
if (process.env.NODE_ENV === 'production' && appUrl.startsWith('http://')) {
  console.warn('[checkout] NEXT_PUBLIC_APP_URL should use HTTPS in production');
  appUrl = appUrl.replace('http://', 'https://');
}
```

---

## Stripe API Version Migration Checklist

When upgrading Stripe API version:

1. [ ] Read the changelog for breaking changes
2. [ ] Check `invoice.subscription` -> `invoice.parent.subscription_details` migration
3. [ ] Check `subscription.current_period_start/end` -> `subscription.items.data[0].current_period_start/end`
4. [ ] Update all type casts in webhook handlers
5. [ ] Test with Stripe CLI using the new version
6. [ ] Pin the version in `new Stripe(key, { apiVersion: 'YYYY-MM-DD.codename' })`
7. [ ] Verify webhook event shapes match your handlers

---

## Customer Portal Configuration

Configure the Stripe Customer Portal in Dashboard > Settings > Customer Portal:

- [ ] Enable subscription cancellation
- [ ] Enable plan switching (if multiple tiers)
- [ ] Enable payment method updates
- [ ] Set cancellation proration to "None" (prevents credits)
- [ ] Configure custom return URL
- [ ] Disable invoice history if not needed
- [ ] Configure cancellation survey questions

---

## Retention Workflows Triggered by Payment Events

| Event | Retention Action |
|-------|-----------------|
| `checkout.session.expired` | 24h nudge email ("You left something behind") |
| `customer.subscription.trial_will_end` | 3-day trial ending email with value highlights |
| `invoice.payment_failed` | Dunning email sequence (day 0, 3, 7) |
| `customer.subscription.deleted` | Win-back email at 7 and 30 days |
| Checkout started but no completion (24h) | Post-onboarding checkout nudge |

---

## Stripe Billing Meters (Usage-Based Billing)

For usage-based pricing (API calls, AI tokens, storage):

```typescript
// Report usage to Stripe Meter
await stripe.billing.meterEvents.create({
  event_name: 'api_calls',
  payload: {
    stripe_customer_id: customerId,
    value: '150', // Number of API calls
  },
});
```

This is an emerging pattern (2025+) for hybrid subscription + usage billing.

---

## Webhook Idempotency

Stripe retries webhooks for up to 3 days. Your handlers **must** be idempotent.

```typescript
// Pattern: Upsert instead of insert
await supabase
  .from('subscriptions')
  .upsert(
    {
      user_id: userId,
      stripe_customer_id: customerId,
      tier,
      status,
    },
    { onConflict: 'user_id' } // Idempotent — same user_id = update
  );
```

```typescript
// Pattern: Check-before-act for one-time operations
if (invoice.billing_reason !== 'subscription_create') {
  return; // Only process first payment, not renewals
}
```

---

## Status Mapping

```typescript
// Map Stripe statuses to your internal statuses
export function mapStripeStatus(status: Stripe.Subscription.Status): SubscriptionStatus {
  const map: Record<Stripe.Subscription.Status, SubscriptionStatus> = {
    active: 'active',
    trialing: 'trialing',
    canceled: 'canceled',
    past_due: 'past_due',
    incomplete: 'incomplete',
    incomplete_expired: 'canceled',
    unpaid: 'past_due',
    paused: 'canceled',
  };
  return map[status] || 'incomplete';
}
```

---

## Dunning / Failed Payment Recovery

### Smart Retry Configuration (Stripe Dashboard)

Configure in Dashboard > Settings > Billing > Subscriptions > Manage failed payments:

| Retry | Timing | Notes |
|-------|--------|-------|
| 1st attempt | 1 day after failure | Stripe sends `invoice.payment_failed` |
| 2nd attempt | 3 days after first retry | Customer notified automatically |
| 3rd attempt | 5 days after second retry | Final automated attempt |
| After final | Cancel or mark unpaid | Configure in dashboard |

### Dunning Email Sequence

| Day | Event | Email | CTA |
|-----|-------|-------|-----|
| 0 | `invoice.payment_failed` | "Your payment failed" | Update payment method (billing portal link) |
| 3 | 2nd retry fails | "Action required: subscription at risk" | Update payment method |
| 7 | 3rd retry fails | "Last chance to keep your subscription" | Update payment method |
| 8 | `customer.subscription.deleted` | "We're sorry to see you go" | Reactivation link |
| 30 | (scheduled) | "We'd love to have you back" | Win-back offer with discount |

### Webhook Handler for Failed Payments

```typescript
async function handlePaymentFailed(invoice: Stripe.Invoice) {
  const subscriptionDetails = invoice.parent?.subscription_details;
  const subscriptionId =
    typeof subscriptionDetails?.subscription === 'string'
      ? subscriptionDetails.subscription
      : subscriptionDetails?.subscription?.id;

  if (!subscriptionId) return;

  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const userId = subscription.metadata?.user_id;
  if (!userId || !isValidUUID(userId)) return;

  // Update local status to past_due
  await db.subscriptions.update({
    status: 'past_due',
    updated_at: new Date(),
  }).where({ user_id: userId });

  // Determine retry count from invoice attempt_count
  const attemptCount = invoice.attempt_count || 1;

  // Send appropriate dunning email
  await sendDunningEmail(userId, {
    attempt: attemptCount,
    nextRetry: invoice.next_payment_attempt
      ? new Date(invoice.next_payment_attempt * 1000)
      : null,
    billingPortalUrl: await createBillingPortalUrl(subscription.customer as string),
  });
}
```

### Billing Portal Link for Self-Service Recovery

```typescript
async function createBillingPortalUrl(customerId: string): Promise<string> {
  const session = await stripe.billingPortal.sessions.create({
    customer: customerId,
    return_url: `${process.env.NEXT_PUBLIC_APP_URL}/settings/subscription`,
  });
  return session.url;
}
```

### Grace Period Pattern

```typescript
// Allow access during grace period (past_due but not yet canceled)
export function hasActiveAccess(
  status: SubscriptionStatus,
  tier: SubscriptionTier
): boolean {
  if (tier === 'free') return true;
  // Active, trialing, or within dunning grace period
  return status === 'active' || status === 'trialing' || status === 'past_due';
}
```

---

## Security Checklist

- [ ] Webhook signature verified with `constructEvent()` on every request
- [ ] `STRIPE_WEBHOOK_SECRET` stored in environment, never in code
- [ ] Webhook endpoint returns 200 quickly (offload heavy work)
- [ ] UUID validation on all `metadata.user_id` values before DB operations
- [ ] HTTPS enforced in production for checkout URLs
- [ ] Service role client used for webhook DB operations (bypasses RLS)
- [ ] No PII logged (mask customer IDs in non-error logs)
- [ ] Idempotency keys used for critical mutations
- [ ] Rate limiting on checkout endpoint
- [ ] Existing subscription check before creating new checkout

---

## Stripe API Version Notes (2025-2026)

| Version | Key Changes |
|---------|-------------|
| `2026-01-28.clover` | Subscription pause support, Reserve resources, per-payment-method capture config |
| `2025-11-17.clover` | Invoice `parent.subscription_details` replaces top-level `subscription` field |
| `2025+` | Managed Payments (MoR) — expanding from private preview |
| `2024+` | Dynamic payment methods by default when `payment_method_types` omitted |
| API v2 (`/v2`) | Improved idempotency — re-executes failed requests instead of returning cached error |

### Invoice API Breaking Change

```typescript
// OLD (pre-2025): invoice.subscription was a string
const subscriptionId = invoice.subscription;

// NEW (2025+): access via parent.subscription_details
const subscriptionDetails = invoice.parent?.subscription_details;
const subscriptionId =
  typeof subscriptionDetails?.subscription === 'string'
    ? subscriptionDetails.subscription
    : subscriptionDetails?.subscription?.id;
```
