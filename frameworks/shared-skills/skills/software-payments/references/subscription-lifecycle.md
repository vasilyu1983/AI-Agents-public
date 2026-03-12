# Subscription Lifecycle Management

Complete guide to managing subscription states, transitions, trials, upgrades/downgrades, cancellation, reactivation, dunning, grace periods, pausing, and database schema design for Stripe-based subscription systems.

---

## Subscription State Machine

### States

| State | Description | Access? | Billing? |
|-------|-------------|---------|----------|
| **trialing** | Free trial period, no charge yet | Full access | No charge until trial ends |
| **active** | Paid and current | Full access | Recurring charges |
| **past_due** | Payment failed, retrying | Configurable (grace) | Retry schedule active |
| **canceled** | Cancellation requested or completed | Until period end (if cancel-at-period-end) | No further charges |
| **incomplete** | Initial payment failed | No access | Awaiting first payment |
| **incomplete_expired** | Initial payment never completed | No access | Dead |
| **unpaid** | All retry attempts exhausted | No access | No further charges |
| **paused** | Subscription paused by customer or system | No access (configurable) | No charges during pause |

### State Transition Diagram

```text
                    ┌─────────────┐
    Checkout ──────>│  incomplete  │──── payment succeeds ────┐
                    └──────┬──────┘                           │
                           │ expires (23h)                    │
                    ┌──────▼──────────┐                       │
                    │incomplete_expired│                       │
                    └─────────────────┘                       │
                                                              │
    Checkout ──────────────────────────>┌──────────┐<─────────┘
    (with trial)──────────────────────>│ trialing  │
                                       └─────┬────┘
                                             │ trial ends + payment succeeds
                                             ▼
                              ┌─────────> active <──────────┐
                              │           │    │             │
                              │   payment │    │ payment     │ payment
                              │   succeeds│    │ fails       │ succeeds
                              │           │    ▼             │
                              │           │  past_due ───────┘
                              │           │    │
                              │           │    │ all retries fail
                              │           │    ▼
                              │           │  unpaid
                              │           │
                              │    cancel │
                              │           ▼
                              │       canceled ───> (reactivate) ──> active
                              │           │
                              │    pause  │
                              │           ▼
                              └────── paused
```

### Webhook Events Per Transition

| Transition | Webhook Event | Key Data |
|-----------|---------------|----------|
| Checkout → trialing | `customer.subscription.created` | status=trialing, trial_end |
| Checkout → active | `customer.subscription.created` | status=active |
| Checkout → incomplete | `customer.subscription.created` | status=incomplete |
| trialing → active | `customer.subscription.updated` | status=active (trial ended) |
| trialing → active | `invoice.payment_succeeded` | billing_reason=subscription_create |
| active → past_due | `invoice.payment_failed` | attempt_count, next_payment_attempt |
| past_due → active | `invoice.payment_succeeded` | Recovery payment |
| past_due → unpaid | `customer.subscription.updated` | status=unpaid |
| active → canceled | `customer.subscription.updated` | cancel_at_period_end=true |
| canceled → ended | `customer.subscription.deleted` | Subscription removed |
| active → paused | `customer.subscription.paused` | pause_collection |
| paused → active | `customer.subscription.resumed` | Active again |

---

## Trial Management

### Trial Configuration

```typescript
// Create subscription with trial
const session = await stripe.checkout.sessions.create({
  mode: 'subscription',
  customer: customerId,
  line_items: [{ price: priceId, quantity: 1 }],
  subscription_data: {
    trial_period_days: 14,
    trial_settings: {
      end_behavior: {
        missing_payment_method: 'cancel', // or 'pause' or 'create_invoice'
      },
    },
    metadata: { user_id: userId },
  },
  // Require payment method during trial signup for better conversion
  payment_method_collection: 'always',
  success_url: `${appUrl}/welcome?trial=true`,
  cancel_url: `${appUrl}/pricing`,
});
```

### trial_will_end Handling

Stripe sends `customer.subscription.trial_will_end` 3 days before trial expires.

```typescript
async function handleTrialWillEnd(subscription: Stripe.Subscription): Promise<void> {
  const userId = subscription.metadata.user_id;
  if (!userId || !isValidUUID(userId)) return;

  const trialEnd = subscription.trial_end
    ? new Date(subscription.trial_end * 1000)
    : null;

  // Send retention email with value highlights
  await sendEmail(userId, 'trial-ending', {
    trialEndDate: trialEnd?.toLocaleDateString(),
    daysRemaining: 3,
    planName: getTierFromPriceId(subscription.items.data[0].price.id),
    billingPortalUrl: await createBillingPortalUrl(subscription.customer as string),
  });

  // Track for analytics
  captureEvent(userId, 'trial_ending_notification_sent', {
    subscription_id: subscription.id,
    trial_end: trialEnd?.toISOString(),
  });
}
```

### Trial Conversion Optimisation

| Strategy | Implementation | Impact |
|----------|---------------|--------|
| Require payment method | `payment_method_collection: 'always'` | 2-3x higher conversion |
| Send value email on day 3 | Highlight features used during trial | +10-20% conversion |
| Send trial-ending email (day 11/14) | Urgency + billing portal link | +5-10% conversion |
| Offer discounted first month | Apply coupon on trial-end | +15-25% conversion (lower ARPU) |
| Show usage stats in-app | "You've used X feature 15 times" | +10-15% conversion |

---

## Upgrade / Downgrade Flows

### Proration Strategies

| Strategy | Stripe Value | Use Case | Customer Experience |
|----------|-------------|----------|---------------------|
| **Create prorations** | `create_prorations` | Upgrades | Charged difference immediately |
| **None** | `none` | Downgrades | Change at next billing cycle |
| **Always invoice** | `always_invoice` | Immediate billing | Instant charge/credit |

### Upgrade Flow

```typescript
async function upgradeSubscription(
  userId: string,
  newTier: PaidTier,
  interval: BillingInterval,
): Promise<{ success: boolean; prorationAmount?: number }> {
  const sub = await db.subscriptions.findByUserId(userId);
  if (!sub?.stripe_subscription_id) throw new Error('No active subscription');

  const stripeSubscription = await stripe.subscriptions.retrieve(
    sub.stripe_subscription_id,
  );

  const newPriceId = getPriceId(newTier, interval, sub.country_code);

  // Preview proration before applying
  const preview = await stripe.invoices.createPreview({
    customer: sub.stripe_customer_id,
    subscription: sub.stripe_subscription_id,
    subscription_items: [{
      id: stripeSubscription.items.data[0].id,
      price: newPriceId,
    }],
    subscription_proration_behavior: 'create_prorations',
  });

  const prorationAmount = preview.total; // Amount in cents

  // Apply upgrade
  await stripe.subscriptions.update(sub.stripe_subscription_id, {
    items: [{
      id: stripeSubscription.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: 'create_prorations',
    metadata: {
      user_id: userId,
      previous_tier: sub.tier,
      new_tier: newTier,
      upgrade_date: new Date().toISOString(),
    },
  });

  // Optimistic local update (webhook will confirm)
  await db.subscriptions.update(userId, { tier: newTier, billing_interval: interval });

  return { success: true, prorationAmount };
}
```

### Downgrade Flow

```typescript
async function downgradeSubscription(
  userId: string,
  newTier: PaidTier,
  interval: BillingInterval,
): Promise<{ success: boolean; effectiveDate: Date }> {
  const sub = await db.subscriptions.findByUserId(userId);
  if (!sub?.stripe_subscription_id) throw new Error('No active subscription');

  const stripeSubscription = await stripe.subscriptions.retrieve(
    sub.stripe_subscription_id,
  );

  const newPriceId = getPriceId(newTier, interval, sub.country_code);

  // Schedule downgrade at end of current period (no proration)
  const updatedSub = await stripe.subscriptions.update(sub.stripe_subscription_id, {
    items: [{
      id: stripeSubscription.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: 'none', // No credit — change at renewal
    metadata: {
      user_id: userId,
      previous_tier: sub.tier,
      new_tier: newTier,
      downgrade_scheduled: new Date().toISOString(),
    },
  });

  const effectiveDate = new Date(updatedSub.current_period_end * 1000);

  return { success: true, effectiveDate };
}
```

---

## Cancellation Patterns

### Cancel-at-Period-End (Recommended Default)

```typescript
async function cancelSubscription(userId: string): Promise<{ endsAt: Date }> {
  const sub = await db.subscriptions.findByUserId(userId);
  if (!sub?.stripe_subscription_id) throw new Error('No active subscription');

  const updatedSub = await stripe.subscriptions.update(
    sub.stripe_subscription_id,
    { cancel_at_period_end: true },
  );

  const endsAt = new Date(updatedSub.current_period_end * 1000);

  // Update local DB
  await db.subscriptions.update(userId, {
    cancel_at_period_end: true,
    canceled_at: new Date(),
  });

  // Send cancellation confirmation + retention offer
  await sendEmail(userId, 'cancellation-confirmation', {
    endsAt: endsAt.toLocaleDateString(),
    reactivateUrl: `${appUrl}/settings/subscription`,
  });

  return { endsAt };
}
```

### Immediate Cancellation

```typescript
// Use only when customer demands immediate cancellation
async function cancelImmediately(userId: string): Promise<void> {
  const sub = await db.subscriptions.findByUserId(userId);
  if (!sub?.stripe_subscription_id) throw new Error('No active subscription');

  // This triggers customer.subscription.deleted webhook
  await stripe.subscriptions.cancel(sub.stripe_subscription_id, {
    prorate: true, // Issue credit for unused time
  });

  // Webhook handler will reset to free tier
}
```

### Cancellation with Survey

```typescript
// Collect cancellation reason before processing
interface CancellationReason {
  reason: 'too_expensive' | 'missing_features' | 'found_alternative' | 'not_using' | 'other';
  feedback?: string;
}

async function cancelWithReason(
  userId: string,
  cancellation: CancellationReason,
): Promise<{ endsAt: Date; offerApplied?: string }> {
  // Store reason for analytics
  await db.cancellationReasons.insert({
    user_id: userId,
    reason: cancellation.reason,
    feedback: cancellation.feedback,
    created_at: new Date(),
  });

  // Offer retention discount for price-sensitive users
  if (cancellation.reason === 'too_expensive') {
    const offer = await applyRetentionOffer(userId, '25_percent_3_months');
    if (offer.accepted) {
      return { endsAt: offer.newPeriodEnd, offerApplied: '25% off for 3 months' };
    }
  }

  return cancelSubscription(userId);
}
```

---

## Reactivation and Win-Back

### Reactivate Before Period End

```typescript
// User changed their mind before subscription ends
async function reactivateSubscription(userId: string): Promise<void> {
  const sub = await db.subscriptions.findByUserId(userId);
  if (!sub?.stripe_subscription_id || !sub.cancel_at_period_end) {
    throw new Error('No cancellation to reverse');
  }

  await stripe.subscriptions.update(sub.stripe_subscription_id, {
    cancel_at_period_end: false,
  });

  await db.subscriptions.update(userId, {
    cancel_at_period_end: false,
    canceled_at: null,
  });
}
```

### Win-Back Expired Subscriptions

```typescript
// Create new subscription for previously-churned user
async function winBackSubscription(
  userId: string,
  tier: PaidTier,
  interval: BillingInterval,
  discountCoupon?: string,
): Promise<{ checkoutUrl: string }> {
  const sub = await db.subscriptions.findByUserId(userId);

  const session = await stripe.checkout.sessions.create({
    customer: sub?.stripe_customer_id || undefined,
    mode: 'subscription',
    line_items: [{ price: getPriceId(tier, interval), quantity: 1 }],
    discounts: discountCoupon ? [{ coupon: discountCoupon }] : undefined,
    metadata: {
      user_id: userId,
      win_back: 'true',
      previous_tier: sub?.tier || 'unknown',
    },
    success_url: `${appUrl}/welcome-back`,
    cancel_url: `${appUrl}/pricing`,
  });

  return { checkoutUrl: session.url! };
}
```

### Win-Back Email Sequence

| Day | Email | Offer |
|-----|-------|-------|
| 7 | "We miss you" | None — highlight new features |
| 14 | "Here's what you're missing" | Show usage stats from when they were active |
| 30 | "Come back with 25% off" | 25% discount for 3 months |
| 60 | "Last chance: 40% off" | 40% discount for 3 months |
| 90 | Final attempt | 50% off first month |

---

## Dunning Management

### Retry Schedule (Stripe Default)

| Attempt | Timing | Webhook |
|---------|--------|---------|
| 1st | Immediately | `invoice.payment_failed` (attempt_count=1) |
| 2nd | 3 days later | `invoice.payment_failed` (attempt_count=2) |
| 3rd | 5 days after 2nd | `invoice.payment_failed` (attempt_count=3) |
| 4th | 7 days after 3rd | `invoice.payment_failed` (attempt_count=4) |
| Final | Configured action | `customer.subscription.deleted` or mark unpaid |

### Smart Retries

Stripe Smart Retries use ML to retry at the optimal time (when the card is most likely to succeed). Enable in Dashboard > Settings > Billing > Subscriptions.

### Grace Period Pattern

```typescript
// During dunning, maintain access to reduce churn
export function hasActiveAccess(
  status: SubscriptionStatus,
  tier: SubscriptionTier,
): boolean {
  if (tier === 'free') return true;

  switch (status) {
    case 'active':
    case 'trialing':
      return true;
    case 'past_due':
      return true; // Grace period — maintain access during retries
    case 'canceled':
    case 'unpaid':
    case 'incomplete':
      return false;
    default:
      return false;
  }
}

// Show non-blocking banner during grace period
export function shouldShowDunningBanner(status: SubscriptionStatus): boolean {
  return status === 'past_due';
}
```

### Customer Notification During Dunning

```typescript
async function handlePaymentFailed(invoice: Stripe.Invoice): Promise<void> {
  const subscriptionId = getSubscriptionIdFromInvoice(invoice);
  if (!subscriptionId) return;

  const subscription = await stripe.subscriptions.retrieve(subscriptionId);
  const userId = subscription.metadata.user_id;
  if (!userId || !isValidUUID(userId)) return;

  await db.subscriptions.update(userId, { status: 'past_due' });

  const attemptCount = invoice.attempt_count || 1;
  const billingPortalUrl = await createBillingPortalUrl(
    subscription.customer as string,
  );

  // Escalating urgency in emails
  const emailTemplates: Record<number, string> = {
    1: 'payment-failed-gentle',      // "Your payment didn't go through"
    2: 'payment-failed-reminder',    // "Action required: update payment"
    3: 'payment-failed-urgent',      // "Last chance to keep your subscription"
    4: 'payment-failed-final',       // "Your subscription will be canceled"
  };

  await sendEmail(userId, emailTemplates[attemptCount] || 'payment-failed-gentle', {
    attemptCount,
    billingPortalUrl,
    nextRetryDate: invoice.next_payment_attempt
      ? new Date(invoice.next_payment_attempt * 1000).toLocaleDateString()
      : null,
  });
}
```

---

## Pause and Resume

### Stripe Subscription Pause (2026+)

```typescript
// Pause subscription (no charges, configurable access)
async function pauseSubscription(
  userId: string,
  resumeDate?: Date,
): Promise<void> {
  const sub = await db.subscriptions.findByUserId(userId);
  if (!sub?.stripe_subscription_id) throw new Error('No active subscription');

  await stripe.subscriptions.update(sub.stripe_subscription_id, {
    pause_collection: {
      behavior: 'void', // or 'keep_as_draft' or 'mark_uncollectible'
      resumes_at: resumeDate ? Math.floor(resumeDate.getTime() / 1000) : undefined,
    },
  });

  await db.subscriptions.update(userId, {
    status: 'paused',
    paused_at: new Date(),
    resume_at: resumeDate || null,
  });
}

// Resume subscription
async function resumeSubscription(userId: string): Promise<void> {
  const sub = await db.subscriptions.findByUserId(userId);
  if (!sub?.stripe_subscription_id) throw new Error('No active subscription');

  await stripe.subscriptions.update(sub.stripe_subscription_id, {
    pause_collection: '', // Clear pause
  });

  await db.subscriptions.update(userId, {
    status: 'active',
    paused_at: null,
    resume_at: null,
  });
}
```

---

## Database Schema

```sql
CREATE TABLE subscriptions (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id),

  -- Stripe identifiers
  stripe_customer_id TEXT UNIQUE,
  stripe_subscription_id TEXT UNIQUE,
  stripe_price_id TEXT,

  -- Subscription state
  tier TEXT NOT NULL DEFAULT 'free'
    CHECK (tier IN ('free', 'starter', 'pro', 'enterprise')),
  status TEXT NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'trialing', 'canceled', 'past_due',
                      'incomplete', 'unpaid', 'paused')),
  billing_interval TEXT DEFAULT 'month'
    CHECK (billing_interval IN ('month', 'year')),

  -- Period tracking
  current_period_start TIMESTAMPTZ,
  current_period_end TIMESTAMPTZ,

  -- Cancellation
  cancel_at_period_end BOOLEAN DEFAULT FALSE,
  canceled_at TIMESTAMPTZ,

  -- Trial
  trial_start TIMESTAMPTZ,
  trial_end TIMESTAMPTZ,

  -- Pause
  paused_at TIMESTAMPTZ,
  resume_at TIMESTAMPTZ,

  -- Regional pricing
  country_code TEXT,

  -- Timestamps
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for webhook lookups
CREATE INDEX idx_sub_stripe_customer ON subscriptions(stripe_customer_id);
CREATE INDEX idx_sub_stripe_subscription ON subscriptions(stripe_subscription_id);
CREATE INDEX idx_sub_status ON subscriptions(status) WHERE status != 'active';

-- Cancellation analytics
CREATE TABLE cancellation_reasons (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  reason TEXT NOT NULL,
  feedback TEXT,
  tier_at_cancel TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Subscription events log (audit trail)
CREATE TABLE subscription_events (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id),
  event_type TEXT NOT NULL,
  stripe_event_id TEXT UNIQUE, -- Idempotency key
  previous_state JSONB,
  new_state JSONB,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_sub_events_user ON subscription_events(user_id, created_at DESC);
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No grace period during dunning | Users lose access immediately on failed payment | Keep access during `past_due` state |
| Immediate cancellation as default | No time for win-back | Use `cancel_at_period_end` |
| No trial qualification check | Users abuse trials on re-signup | Track previous subscriptions |
| Proration on downgrades | Unexpected credits, accounting complexity | Use `proration_behavior: 'none'` for downgrades |
| No cancellation reason collection | Cannot improve retention | Survey before cancellation |
| Trusting client-side status | Stale or manipulated data | Always check server/webhook as source of truth |
| Missing audit trail | Cannot debug subscription issues | Log all state transitions |
| No dunning emails | Users do not know payment failed | Send escalating notifications |

---

## Cross-References

- [stripe-patterns.md](stripe-patterns.md) — Webhook handler architecture, idempotency, status mapping
- [webhook-reliability-patterns.md](webhook-reliability-patterns.md) — Idempotency, retry handling, dead letter queues
- [regional-pricing-guide.md](regional-pricing-guide.md) — Multi-currency pricing for subscription tiers
- [testing-patterns.md](testing-patterns.md) — Testing subscription lifecycle with Stripe CLI
- [platform-comparison.md](platform-comparison.md) — Dunning and subscription features per platform
