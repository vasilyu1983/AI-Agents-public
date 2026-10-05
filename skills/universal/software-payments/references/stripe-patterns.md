# Stripe Implementation Patterns

Detailed patterns, error handling, and lessons learned from production Stripe integrations.

---
## Table of Contents

- [Webhook Handler Architecture](#webhook-handler-architecture)
- [Handler Module Organization](#handler-module-organization)
- [Handler Contract](#handler-contract)
- [UUID Validation](#uuid-validation)
- [Error Handling Patterns](#error-handling-patterns)
- [Structured Logging for Webhooks](#structured-logging-for-webhooks)
- [Error Categories](#error-categories)
- [Webhook Response Strategy](#webhook-response-strategy)
- [Trial Management](#trial-management)
- [Trial Qualification Logic](#trial-qualification-logic)
- [Trial Events Timeline](#trial-events-timeline)
- [Proration Strategies](#proration-strategies)
- [Subscription Database Schema](#subscription-database-schema)
- [Handling Duplicate Subscriptions](#handling-duplicate-subscriptions)
- [HTTPS Enforcement](#https-enforcement)
- [Stripe API Version Migration Checklist](#stripe-api-version-migration-checklist)
- [Customer Portal Configuration](#customer-portal-configuration)
- [Retention Workflows Triggered by Payment Events](#retention-workflows-triggered-by-payment-events)
- [Stripe Billing Meters (Usage-Based Billing)](#stripe-billing-meters-usage-based-billing)
- [Webhook Idempotency](#webhook-idempotency)
- [Network Tokens](#network-tokens)
- [Status Mapping](#status-mapping)
- [Dunning / Failed Payment Recovery](#dunning--failed-payment-recovery)
- [Smart Retry Configuration](#smart-retry-configuration)
- [Dunning Email Sequence](#dunning-email-sequence)
- [Webhook Handler for Failed Payments](#webhook-handler-for-failed-payments)
- [Billing Portal Link for Self-Service Recovery](#billing-portal-link-for-self-service-recovery)
- [Grace Period Pattern](#grace-period-pattern)
- [Security Checklist](#security-checklist)
- [Stripe API Version Notes](#stripe-api-version-notes)
- [Invoice API Breaking Change](#invoice-api-breaking-change)


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
500: Handler failed (provider retry policy applies)
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

Example seven-day trial; the no-payment-method end behavior is configurable, including cancellation or pause. Read the subscription’s trial settings rather than assuming cancellation.

```
Day 0: trial_started (subscription.created with status='trialing')
Day 4: trial_will_end (3 days before expiry — send retention email)
Day 7: subscription becomes 'active' (first charge) or 'canceled' (no card)
```

---

## Proration Strategies

Check [Stripe’s proration behavior](https://docs.stripe.com/billing/subscriptions/prorations) before promising an immediate charge or end-of-period plan change.

| Strategy | Use When | Stripe Setting |
|----------|----------|----------------|
| `create_prorations` | Create adjustment lines for an upgrade/downgrade | Does not itself guarantee immediate collection |
| `none` | Deliberately omit proration adjustments | Does not delay the subscription change; schedule an end-of-period downgrade separately |
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
6. [ ] Pin the version in `new Stripe(key, { apiVersion: '<your-pinned-version>' })` — pin the version your account uses, not a value copied from docs or examples; see Stripe's [API upgrades page](https://docs.stripe.com/upgrades)
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

Use a stable event identifier and reconcile your usage ledger with accepted meter events before invoicing.

---

## Network Tokens

A network token replaces a card PAN with a credential managed by a card network. It differs from a provider’s vault token or `PaymentMethod` ID. Network lifecycle updates can keep saved-card payments working after reissue; they do not replace customer consent, SCA handling or entitlement checks.

For Stripe, leave provisioning and credential selection to its managed integration. Read [Stripe’s network-token guide](https://stripe.com/guides/understanding-benefits-of-network-tokens) for issuer/region coverage, PAN fallback and credential lifecycle. For multi-processor routing, verify token-requestor ownership and portability with both processors; do not assume a saved provider ID or network token transfers. Measure authorization outcomes on comparable traffic before claiming uplift.

## Webhook Idempotency

An upsert prevents duplicate rows; it does not deduplicate side effects or protect against stale events. Atomically record the provider event ID with the state mutation, and reconcile current provider state before applying an out-of-order update. Use an outbox for independently retried side effects.

Stripe can redeliver events. Read the [webhook delivery policy](https://docs.stripe.com/webhooks) for the environment’s retry window; make handlers idempotent.

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
    incomplete_expired: 'incomplete_expired',
    unpaid: 'unpaid',
    paused: 'paused',
  };
  if (!Object.hasOwn(map, status)) {
    throw new Error(`Unsupported subscription status: ${status}`);
  }
  return map[status];
}
```

---

Keep these states in the internal `SubscriptionStatus` union and database constraint. `paused` is resumable; `canceled` is terminal. Distinguish `unpaid` from `past_due` so a dunning grace policy does not grant indefinite access after retries end. Read the [subscription lifecycle](https://docs.stripe.com/billing/subscriptions/overview) for the pinned API’s state transitions.

`pause_collection` changes collection behavior without setting the subscription’s status to `paused`; track collection settings separately. An actual subscription pause can follow trial end or use the dedicated pause API where supported. Check [pause subscriptions](https://docs.stripe.com/billing/subscriptions/pause) and [pause collection](https://docs.stripe.com/billing/subscriptions/pause-payment) before choosing a retention flow.

## Dunning / Failed Payment Recovery

### Smart Retry Configuration

Read the account’s Billing recovery settings and [Smart Retries documentation](https://docs.stripe.com/billing/revenue-recovery/smart-retries). Retry timing depends on the configured policy and payment method; derive customer notices from actual attempts and the scheduled retry rather than a copied timetable.

### Dunning Email Sequence

Example communication cadence; align it with actual retry outcomes and consent requirements.

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
  tier: SubscriptionTier,
  graceEndsAt: Date | null,
  now: Date = new Date(),
): boolean {
  if (tier === 'free') return true;
  if (status === 'active' || status === 'trialing') return true;
  return status === 'past_due' && graceEndsAt !== null && now < graceEndsAt;
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
- [ ] PCI scope confirmed: hosted Checkout/Payment Links → SAQ A; Payment Element or embedded Checkout (Stripe iframe) → SAQ A, provided the page meets the PCI SSC FAQ 1588 "not susceptible to script attacks" criterion or runs the 6.4.3/11.6.1 script controls; raw card data through your server or the API → SAQ D. Choose the lowest-scope surface your UX requirements allow.
- [ ] No raw card data (number, CVV, expiry) logged, stored, or passed through your servers at any point.
- [ ] Read the current PCI SSC standard and assessment forms before choosing scope; do not assume an older checklist covers later effective requirements. Route full-standard compliance work to a dedicated security/compliance review; this checklist covers the checkout-surface scope-reduction choice, not the full assessment.

---

## Stripe API Version Notes

Rows name the API version where a behaviour changed, so you can tell which shape your pinned version returns. They are not a statement of which version is current: check your pinned version in Workbench and the [Stripe changelog](https://docs.stripe.com/changelog) / [API upgrades page](https://docs.stripe.com/upgrades) before pinning or upgrading.

| Version | Key Changes |
|---------|-------------|
| `2025-03-31.basil` and later | Invoice `parent.subscription_details.subscription` replaces the removed top-level `invoice.subscription` field; `current_period_*` moved from the subscription to subscription items |
| `2025-06-30.basil` and later | Flexible `billing_mode` available (opt-in); required for mixed-interval subscriptions and other flexible-only capabilities |
| `2025-09-30.clover` and later | Flexible `billing_mode` becomes the API default for new subscriptions (breaking: set `billing_mode` to `classic` explicitly to keep old behaviour) |
| `2025+` | `entitlements.active_entitlement_summary.updated` becomes the provisioning signal for Stripe Entitlements |
| Managed Payments | Merchant-of-record offering, eligibility-gated (business location, digital products, direct integrations only, no Connect, Checkout Session or Payment Link); check Stripe's eligibility page before committing |
| `2024+` | Dynamic payment methods by default when `payment_method_types` omitted |
| API v2 (`/v2`) | Improved idempotency — re-executes failed requests instead of returning cached error |

### Invoice API Breaking Change

```typescript
// OLD (pinned API versions before the invoice `parent` change above): invoice.subscription was a string
const subscriptionId = invoice.subscription;

// NEW (versions with invoice `parent`): access via parent.subscription_details
const subscriptionDetails = invoice.parent?.subscription_details;
const subscriptionId =
  typeof subscriptionDetails?.subscription === 'string'
    ? subscriptionDetails.subscription
    : subscriptionDetails?.subscription?.id;
```
