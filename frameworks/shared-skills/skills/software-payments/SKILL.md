---
name: software-payments
description: Production-grade payment integration for Stripe, Paddle, LemonSqueezy, RevenueCat, Adyen, Chargebee, Recurly, and Lago. Covers checkout flows, subscription lifecycle, webhook handling, multi-currency/regional pricing, feature gating, one-time purchases, billing portal, refunds, usage-based billing, and payment testing. Use when implementing or debugging any payment/billing/subscription system.
---

# Payments & Billing Engineering

Use this skill to design, implement, and debug production payment integrations: checkout flows, subscription management, webhook handling, regional pricing, feature gating, one-time purchases, billing portals, and payment testing.

Defaults bias toward: Stripe as primary processor (most common), webhooks as source of truth, idempotent handlers, lazy-initialized clients, dynamic payment methods, Zod validation at boundaries, structured logging, and fire-and-forget for non-critical tracking. For complex billing, consider a billing orchestrator (Chargebee, Recurly, Lago) on top of Stripe/Adyen.

---

## Quick Reference

| Task | Default Picks | Notes |
|------|---------------|-------|
| Subscription billing | Stripe Checkout (hosted) | Omit `payment_method_types` for dynamic methods |
| MoR / tax compliance | Stripe Managed Payments / Paddle / LemonSqueezy | MoR handles VAT/sales tax for you |
| Mobile subscriptions | RevenueCat | Wraps App Store + Google Play |
| Enterprise / high-volume | Adyen | 250+ payment methods, interchange++ pricing |
| Complex billing logic | Chargebee / Recurly on top of Stripe | Per-seat + usage, contract billing, revenue recognition |
| Usage-based billing | Stripe Billing Meters or Lago (open-source) | API calls, AI tokens, compute metering |
| Webhook handling | Verify signature + idempotent handlers | Stripe retries for 3 days |
| Feature gating | Tier hierarchy + feature matrix | Check at API boundary |
| One-time purchases | Stripe Checkout `mode: 'payment'` | Alongside subscriptions |
| Billing portal | Stripe Customer Portal | Self-service management |
| Regional pricing | PPP-adjusted prices per country | Use `x-vercel-ip-country` or GeoIP |
| PayPal button | Stripe PayPal method or PayPal Commerce Platform | Avoid Braintree — deprecated 2026, EOL Jan 2027 |
| Testing | Stripe CLI + test cards | `4242 4242 4242 4242` |

## Scope

Use this skill to:

- Implement checkout flows (hosted, embedded, custom)
- Build subscription lifecycle management (create, upgrade, downgrade, cancel)
- Handle webhooks reliably (signature verification, idempotency, error handling)
- Set up regional/multi-currency pricing (PPP, emerging markets)
- Build feature gating and entitlement systems
- Implement one-time purchases alongside subscriptions
- Create billing portal integrations
- Test payment flows end-to-end
- Debug common payment integration issues

## When NOT to Use This Skill

Use a different skill when:

- **General backend patterns** -> See [software-backend](../software-backend/SKILL.md)
- **API design only (no payments)** -> See [dev-api-design](../dev-api-design/SKILL.md)
- **Conversion optimization** -> See [marketing-cro](../marketing-cro/SKILL.md)
- **Business model / pricing strategy** -> See [startup-business-models](../startup-business-models/SKILL.md)
- **Security audits** -> See [software-security-appsec](../software-security-appsec/SKILL.md)

---

## Decision Tree: Payment Platform Selection

Three platform layers (can be combined):

| Layer | Role | Examples |
|-------|------|----------|
| **Payment Processor** | Moves money, payment methods, fraud | Stripe, Adyen |
| **Merchant of Record (MoR)** | Handles tax, legal, disputes for you | Paddle, LemonSqueezy, Stripe Managed Payments |
| **Billing Orchestrator** | Subscription logic, dunning, revenue recognition | Chargebee, Recurly, Lago (open-source) |

```text
Payment integration needs: [Business Model]

  STEP 1: Choose your processor
    - Default / most common -> Stripe
    - Enterprise, >$1M/yr, 250+ payment methods -> Adyen
    - Need PayPal button -> Stripe (PayPal method) or PayPal Commerce Platform
    - ⚠ Do NOT start new projects on Braintree (deprecated 2026, EOL Jan 2027)

  STEP 2: Do you need a MoR?
    - Handle own tax + compliance -> Skip MoR, use processor directly
    - Want tax/VAT/disputes handled -> Stripe Managed Payments, Paddle, LemonSqueezy
    - Indie / small SaaS -> LemonSqueezy (simplest MoR)
    - EU-heavy customer base -> Paddle (strongest EU VAT handling)

  STEP 3: Is billing logic complex?
    - Simple tiers (free/pro/enterprise) -> Stripe Billing is sufficient
    - Per-seat + usage, contract billing, rev-rec -> Chargebee or Recurly on top of Stripe
    - Usage-based (API calls, AI tokens) -> Stripe Billing Meters or Lago (open-source)
    - B2C subscriptions, churn focus -> Recurly (strong revenue recovery)

  STEP 4: Platform-specific needs
    - Mobile app (iOS/Android) -> RevenueCat (wraps both stores)
    - Hybrid (web + app) -> RevenueCat + Stripe (share customer IDs)
    - Marketplace / multi-party -> Stripe Connect
    - One-time digital goods -> Stripe Checkout (payment mode)
    - Physical goods -> Stripe + shipping integration
    - Emerging markets / PPP -> Multiple Stripe Price objects per region
    - Multi-currency -> Stripe multi-currency or Paddle (auto-converts)
    - B2B invoicing -> Stripe Invoicing
```

---

## Platform Comparison (Feb 2026)

### Payment Processors

| Feature | Stripe | Adyen |
|---------|--------|-------|
| **Model** | Payment processor | Payment processor (enterprise) |
| **Tax handling** | Add-on (Stripe Tax) / MoR (Managed Payments) | Via partners or self-managed |
| **Pricing** | 2.9% + 30c (US) | Interchange++ (volume-dependent) |
| **Subscription mgmt** | Full API (Stripe Billing) | Basic (pair with Chargebee/Recurly) |
| **Payment methods** | 100+ (dynamic selection) | 250+ (strongest local method coverage) |
| **Checkout** | Hosted / Embedded / Custom | Drop-in / API / Hosted |
| **Marketplace** | Stripe Connect | Adyen for Platforms |
| **Best for** | Default choice, startups to enterprise | High-volume (>$1M/yr), global enterprise |

### Merchants of Record (MoR)

| Feature | Paddle | LemonSqueezy | Stripe Managed Payments |
|---------|--------|--------------|------------------------|
| **Tax handling** | Included (200+ countries) | Included | Included |
| **Pricing** | 5% + 50c | 5% + 50c | TBD (expanding from preview) |
| **Subscription mgmt** | Full API | Full API | Full Stripe API |
| **API flexibility** | Paddle API | Simpler API | Full Stripe ecosystem |
| **Best for** | SaaS (EU tax) | Indie SaaS, digital products | Already on Stripe, want MoR |

### Billing Orchestrators (sit on top of processors)

| Feature | Chargebee | Recurly | Lago |
|---------|-----------|---------|------|
| **Model** | Billing layer on Stripe/Adyen/Braintree | Billing layer on processors | Open-source billing engine |
| **Pricing** | From $0 (Startup) to custom | From $0 to custom | Free (self-host) or cloud |
| **Usage-based** | Limited (5K records cap) | Basic support | Full metering (designed for it) |
| **Revenue recognition** | Built-in (RevRec) | Built-in | Via integrations |
| **Dunning** | Advanced automation | Strong (best-in-class B2C) | Basic |
| **Best for** | B2B SaaS, complex billing | B2C subscriptions, churn focus | AI/ML SaaS, usage-based pricing |

### Mobile

| Feature | RevenueCat |
|---------|------------|
| **Model** | Mobile subscription SDK |
| **Pricing** | Free to $499/mo + % |
| **Platforms** | iOS, Android, React Native, Flutter |
| **Best for** | In-app purchases, cross-platform subscriptions |

---

## Stripe Integration Patterns (Feb 2026)

### 1. Client Initialization

**CRITICAL: Lazy-initialize the Stripe client.** Import-time initialization fails during build/SSR when env vars aren't available.

```typescript
// CORRECT: Lazy initialization with proxy for backwards compatibility
import Stripe from 'stripe';

let _stripe: Stripe | null = null;

export function getStripeServer(): Stripe {
  if (!_stripe) {
    const secretKey = process.env.STRIPE_SECRET_KEY;
    if (!secretKey) {
      throw new Error('STRIPE_SECRET_KEY is not configured');
    }
    _stripe = new Stripe(secretKey, {
      apiVersion: '2026-01-28.clover', // Pin to specific version
      typescript: true,
    });
  }
  return _stripe;
}

// Proxy for convenience (backwards-compatible named export)
export const stripe = {
  get customers() { return getStripeServer().customers; },
  get subscriptions() { return getStripeServer().subscriptions; },
  get checkout() { return getStripeServer().checkout; },
  get billingPortal() { return getStripeServer().billingPortal; },
  get webhooks() { return getStripeServer().webhooks; },
};
```

```typescript
// WRONG: Crashes during build when STRIPE_SECRET_KEY is undefined
import Stripe from 'stripe';
export const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!); // Build failure
```

### 2. Checkout Session Creation

**CRITICAL: Do NOT set `payment_method_types`.** Omitting it enables Stripe's dynamic payment method selection (Apple Pay, Google Pay, Link, bank transfers, local methods) based on customer region and device.

```typescript
const session = await stripe.checkout.sessions.create({
  customer: customerId,
  mode: 'subscription',
  // DO NOT set payment_method_types — let Stripe auto-select
  line_items: [{ price: priceId, quantity: 1 }],
  subscription_data: {
    trial_period_days: 7,
    metadata: {
      user_id: userId,
      billing_interval: interval,
    },
  },
  success_url: `${appUrl}/dashboard?checkout=success&tier=${tier}`,
  cancel_url: `${appUrl}/dashboard?checkout=canceled`,
  allow_promotion_codes: true,
  billing_address_collection: 'auto',
  metadata: {
    user_id: userId,
    tier,
    billing_interval: interval,
  },
});
```

```typescript
// WRONG: Limits to cards only, blocks Apple Pay, Google Pay, Link, etc.
const session = await stripe.checkout.sessions.create({
  payment_method_types: ['card'], // REMOVE THIS
  // ...
});
```

### 3. Webhook Handler Architecture

**Webhooks are the source of truth for subscription state.** Never trust client-side callbacks alone.

```typescript
// Webhook route (Next.js App Router)
export async function POST(request: NextRequest) {
  const body = await request.text();
  const signature = request.headers.get('stripe-signature');

  if (!signature) {
    return NextResponse.json({ error: 'Missing signature' }, { status: 400 });
  }

  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;
  if (!webhookSecret) {
    console.error('[webhook] STRIPE_WEBHOOK_SECRET not configured');
    return NextResponse.json({ error: 'Config error' }, { status: 500 });
  }

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(body, signature, webhookSecret);
  } catch (err) {
    console.error('[webhook] Signature verification failed:', err);
    return NextResponse.json({ error: 'Invalid signature' }, { status: 400 });
  }

  try {
    switch (event.type) {
      case 'checkout.session.completed':
        await handleCheckoutCompleted(event.data.object);
        break;
      case 'checkout.session.expired':
        handleCheckoutExpired(event.data.object); // Fire-and-forget
        break;
      case 'customer.subscription.created':
        await handleSubscriptionCreated(event.data.object);
        break;
      case 'customer.subscription.updated':
        await handleSubscriptionUpdated(event.data.object);
        break;
      case 'customer.subscription.deleted':
        await handleSubscriptionDeleted(event.data.object);
        break;
      case 'invoice.payment_succeeded':
        await handlePaymentSucceeded(event.data.object);
        break;
      case 'invoice.payment_failed':
        await handlePaymentFailed(event.data.object);
        break;
      default:
        console.log(`Unhandled event: ${event.type}`);
    }
    return NextResponse.json({ received: true });
  } catch (error) {
    console.error('[webhook] Handler failed', {
      eventId: event.id,
      eventType: event.type,
      error: error instanceof Error ? error.message : 'Unknown',
    });
    return NextResponse.json({ error: 'Handler failed' }, { status: 500 });
  }
}
```

#### Essential Webhook Events

| Event | When | Handler Pattern |
|-------|------|-----------------|
| `checkout.session.completed` | Checkout finishes | Link Stripe customer to user, create subscription record |
| `checkout.session.expired` | Abandoned checkout | Fire-and-forget analytics (never fail the response) |
| `customer.subscription.created` | New subscription | Upsert subscription record with tier, status, period |
| `customer.subscription.updated` | Plan change, renewal, cancel-at-period-end | Update tier, status, cancel flags |
| `customer.subscription.deleted` | Subscription ends | Reset to free tier |
| `invoice.payment_succeeded` | Successful charge | Update period dates, process referral rewards |
| `invoice.payment_failed` | Failed charge | Set status to `past_due` |
| `customer.subscription.trial_will_end` | 3 days before trial ends | Trigger retention email |

#### Fire-and-Forget Pattern for Non-Critical Tracking

```typescript
// Abandonment tracking — MUST NOT fail the webhook response
export function handleCheckoutExpired(session: Stripe.Checkout.Session): void {
  const userId = session.metadata?.user_id;
  if (!userId) return;

  // No await, no throw — pure side effect
  captureServerEvent(userId, 'checkout_abandoned', {
    tier: session.metadata?.tier,
    interval: session.metadata?.billing_interval,
    session_id: session.id,
  });
}
```

### 4. Subscription Tier Model

```typescript
// Type definitions
export type SubscriptionTier = 'free' | 'starter' | 'pro' | 'enterprise';
export type SubscriptionStatus = 'active' | 'trialing' | 'canceled' | 'past_due' | 'incomplete';
export type BillingInterval = 'month' | 'year';

// Tier hierarchy for comparison
export const TIER_HIERARCHY: Record<SubscriptionTier, number> = {
  free: 0,
  starter: 1,
  pro: 2,
  enterprise: 3,
};

// Feature access matrix
export type Feature = 'basic_dashboard' | 'advanced_reports' | 'api_access' | 'priority_support';

const TIER_FEATURES: Record<SubscriptionTier, Feature[]> = {
  free: ['basic_dashboard'],
  starter: ['basic_dashboard', 'advanced_reports'],
  pro: ['basic_dashboard', 'advanced_reports', 'api_access'],
  enterprise: ['basic_dashboard', 'advanced_reports', 'api_access', 'priority_support'],
};

export function hasFeatureAccess(tier: SubscriptionTier, feature: Feature): boolean {
  return TIER_FEATURES[tier].includes(feature);
}

export function isTierUpgrade(current: SubscriptionTier, target: SubscriptionTier): boolean {
  return (TIER_HIERARCHY[target] ?? 0) > (TIER_HIERARCHY[current] ?? 0);
}
```

### 5. Upgrade/Downgrade Flow

```typescript
// In-place upgrade: modify existing subscription with proration
if (hasActivePaidSubscription) {
  const currentSub = await stripe.subscriptions.retrieve(subscriptionId);

  await stripe.subscriptions.update(subscriptionId, {
    items: [{
      id: currentSub.items.data[0].id,
      price: newPriceId,
    }],
    proration_behavior: 'create_prorations', // Charge/credit difference
    metadata: {
      user_id: userId,
      previous_tier: currentTier,
      new_tier: newTier,
    },
  });

  // Update local DB immediately (webhook will confirm)
  await db.subscriptions.update({ tier: newTier }).where({ user_id: userId });

  return { success: true, upgraded: isTierUpgrade(currentTier, newTier) };
}
```

### 6. Regional / PPP Pricing

```typescript
// Define emerging markets for PPP-adjusted pricing
export const EMERGING_MARKETS = [
  'IN', 'BR', 'MX', 'ID', 'PH', 'ZA', 'TR', 'VN',
  'EG', 'MA', 'DZ', 'TN',
] as const;

// Create separate Stripe Price objects for each region
// Standard: $9.99/mo, Emerging: $3.99/mo (~60% discount)

export function getPriceId(
  tier: PaidTier,
  interval: BillingInterval,
  countryCode?: string
): string {
  const isEmerging = countryCode && EMERGING_MARKETS.includes(countryCode);

  if (interval === 'year') {
    return isEmerging
      ? TIER_EMERGING_ANNUAL_PRICE_IDS[tier]
      : TIER_ANNUAL_PRICE_IDS[tier];
  }

  return isEmerging
    ? TIER_EMERGING_PRICE_IDS[tier]
    : TIER_PRICE_IDS[tier];
}

// Get country from Vercel header (or GeoIP service)
const countryCode = request.headers.get('x-vercel-ip-country') || 'US';
const priceId = getPriceId(tier, interval, countryCode);
```

### 7. One-Time Purchases Alongside Subscriptions

```typescript
// Some products are one-time (e.g., PDF reports, credits)
// but subscribers get unlimited access
export function hasUnlimitedProductAccess(
  tier: SubscriptionTier,
  status: SubscriptionStatus,
  product: OneTimeProduct
): boolean {
  const isActive = status === 'active' || status === 'trialing';
  if (!isActive) return false;

  const productConfig = ONE_TIME_PRODUCTS[product];
  if (!productConfig.unlimitedFeature) return false;

  return hasFeatureAccess(tier, productConfig.unlimitedFeature);
}

// Checkout for one-time purchase
const session = await stripe.checkout.sessions.create({
  customer: customerId,
  mode: 'payment', // Not 'subscription'
  line_items: [{ price: productPriceId, quantity: 1 }],
  metadata: {
    user_id: userId,
    product_type: 'crush_compatibility',
    purchase_id: purchaseId, // Track in your DB
  },
  success_url: `${appUrl}/purchase/success?id=${purchaseId}`,
  cancel_url: `${appUrl}/purchase/cancel`,
});
```

### 8. Billing Portal

```typescript
// Minimal billing portal route
export async function POST() {
  const user = await getAuthenticatedUser();
  const subscription = await db.subscriptions
    .select('stripe_customer_id')
    .where({ user_id: user.id })
    .single();

  if (!subscription?.stripe_customer_id) {
    return NextResponse.json({ error: 'No billing account' }, { status: 404 });
  }

  const session = await stripe.billingPortal.sessions.create({
    customer: subscription.stripe_customer_id,
    return_url: `${appUrl}/settings/subscription`,
  });

  return NextResponse.json({ url: session.url });
}
```

### 9. Referral/Coupon Integration

```typescript
// Check for pending referral before creating checkout
const pendingReferral = await getUserPendingReferral(userId);

const session = await stripe.checkout.sessions.create({
  // ...
  discounts: pendingReferral
    ? [{ coupon: REFERRAL_COUPON_ID }]
    : undefined,
  // Only allow promo codes if no referral discount
  allow_promotion_codes: !pendingReferral,
});

// On invoice.payment_succeeded, reward the referrer
if (invoice.billing_reason === 'subscription_create') {
  await stripe.customers.createBalanceTransaction(
    referrerCustomerId,
    {
      amount: -creditAmount, // Negative = credit
      currency: 'gbp',
      description: `Referral reward (${referralCode})`,
    }
  );
}
```

---

## Feature Gating Patterns

### Three-Layer Feature Gating

Every paid feature requires enforcement at exactly 3 layers. Missing any layer creates either a security hole or a broken UX.

| Layer | Role | Example | Failure Mode |
|-------|------|---------|--------------|
| **1. Feature Registry** | Maps features to tiers + defines benefit text | `FEATURES: { house_systems: { tier: 'cosmic' } }` | Wrong tier assignment = gate is a no-op |
| **2. API Enforcement** | Returns 403 or gated response for unauthorized access | `if (!hasAccess(feature)) return Response.json({ error: 'upgrade' }, { status: 403 })` | Data leaks to free users |
| **3. UI Paywall** | Shows upgrade CTA instead of locked content | `<FeatureBannerPreview feature="house_systems" />` | Users see broken/empty UI |

PASS/FAIL:

```
FAIL: canAccess('natal_chart') where natal_chart is in free tier → always true, paywall never shows
PASS: canAccess('house_systems') where house_systems is Cosmic-only → correctly gates advanced sections
FAIL: UI shows paywall but API still returns full data → security hole
PASS: API returns gated response AND UI shows paywall → defense in depth
```

Anti-pattern — "Gate on Wrong Key": The most dangerous gating bug. If the feature key used in `canAccess()` is listed in the free tier, the gate is a permanent no-op. Always verify the gate key maps to the correct tier in the feature registry.

Pattern — Consistent Paywall Components: Use ONE paywall component across all features (e.g., `FeatureBannerPreview`). Don't build one-off locked views per feature.

Pattern — Analytics on Every Gate: Every paywall must fire an analytics event (e.g., `feature_gated`) for conversion funnel measurement.

### Gated API Response Shapes

Anti-pattern — Polymorphic Field Shapes:

```typescript
// FAIL: Same field returns different types depending on tier
type Response = {
  transits: Transit[] | { __gated: true; count: number; topTransit: string };
}
// Client code: (data.transits || []).sort() → CRASH on gated object (truthy non-array)
```

```typescript
// PASS: Consistent shape with explicit gated flag
type Response = {
  transits: Transit[];  // Always an array (empty for free, full for paid)
  transitsGated: boolean;
  transitTeaser?: { count: number; topTransit: string };
}
```

If you must use polymorphic shapes, guard with `Array.isArray()` at the boundary:

```typescript
// Defensive: Array.isArray() guard, NOT || []
const transits = Array.isArray(data.transits) ? data.transits : [];
// WRONG: data.transits || [] — { __gated: true } is truthy, passes through
```

### Stripe Checkout Mutual Exclusivity

```
FAIL: { allow_promotion_codes: true, discounts: [{ coupon: introId }] } → Stripe rejects
PASS: if (hasIntroCoupon) { discounts: [...] } else { allow_promotion_codes: true }
```

Test every billing path: monthly intro, monthly referral, annual no-discount, free trial. They exercise different parameter combinations.

### SDK Types vs. Documentation

```
FAIL: Plan says stripe.customers.list().total_count — doesn't exist in SDK
PASS: stripe.customers.list().data.length — actual SDK ApiList<T> shape
```

**Always verify Stripe SDK TypeScript types** (`node_modules/stripe/types/`), not documentation examples. SDK types diverge from REST API docs.

For detailed gating architecture (consumables, fraud prevention, discriminated unions), see [references/feature-gating-patterns.md](references/feature-gating-patterns.md).

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

---

## Common Mistakes and Anti-Patterns

| FAIL Avoid | PASS Instead | Why |
|------------|--------------|-----|
| `payment_method_types: ['card']` | Omit the field entirely | Blocks Apple Pay, Google Pay, Link, local methods |
| Trusting client-side checkout callback | Use webhooks as source of truth | Client can close browser before callback |
| `new Stripe(key)` at module top level | Lazy-initialize in a function | Build fails when env var is undefined |
| Catching webhook errors silently | Log + return 500 so Stripe retries | Lost events = lost revenue |
| Storing subscription state only client-side | Sync from webhook to DB | Single source of truth |
| Hardcoding prices in code | Use Stripe Price objects via env vars | Prices change, regional variants |
| Skipping webhook signature verification | Always verify with `constructEvent()` | Prevents replay/spoofing attacks |
| Using `invoice.subscription` (2025+) | Use `invoice.parent.subscription_details` | Breaking change since 2025-11-17.clover |
| `await` on fire-and-forget analytics | Don't await, don't throw | Non-critical tracking must not fail webhooks |
| Missing UUID validation on `user_id` from metadata | Validate with regex before DB operations | Prevents injection and corrupt data |
| Creating checkout without checking existing subscription | Check and use upgrade flow if active | Prevents duplicate subscriptions |
| Using `--no-verify` for Stripe webhook testing | Use Stripe CLI: `stripe listen --forward-to` | Real signature verification in dev |

---

## E2E Testing Patterns

Quick reference — full patterns in [references/testing-patterns.md](references/testing-patterns.md).

```bash
# Stripe CLI: forward events to local webhook endpoint
stripe listen --forward-to localhost:3001/api/stripe/webhook

# Trigger specific events
stripe trigger checkout.session.completed
stripe trigger invoice.payment_failed
```

| Card | Scenario |
|------|----------|
| `4242 4242 4242 4242` | Successful payment |
| `4000 0000 0000 0002` | Declined |
| `4000 0000 0000 3220` | 3D Secure required |
| `4000 0000 0000 9995` | Insufficient funds |

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

## Navigation

**References**
- [references/stripe-patterns.md](references/stripe-patterns.md) - Stripe patterns: webhook handlers, idempotency, status mapping, error handling, dunning, usage-based billing
- [references/platform-comparison.md](references/platform-comparison.md) - Platform comparison: Stripe, Adyen, Paddle, LemonSqueezy, Chargebee, Recurly, Lago, Braintree (deprecated)
- [references/testing-patterns.md](references/testing-patterns.md) - E2E testing: Stripe CLI, Playwright checkout, test cards, state sync
- [references/subscription-lifecycle.md](references/subscription-lifecycle.md) - Full subscription state machine, trials, upgrades/downgrades, cancellation, dunning, pause/resume, database schema
- [references/regional-pricing-guide.md](references/regional-pricing-guide.md) - PPP implementation, multi-currency Stripe prices, tax by region, fraud prevention, A/B testing pricing
- [references/webhook-reliability-patterns.md](references/webhook-reliability-patterns.md) - Idempotency, retry handling, dead letter queues, monitoring, event ordering, queue-based processing
- [references/feature-gating-patterns.md](references/feature-gating-patterns.md) - Feature gating: consumable vs binary unlocks, spread-then-override filtering, fraud prevention, discriminated union typed responses
- [data/sources.json](data/sources.json) - External documentation links (59 sources)

**Related Skills**
- [../software-backend/SKILL.md](../software-backend/SKILL.md) - Backend API patterns, database, auth
- [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) - API design patterns
- [../marketing-cro/SKILL.md](../marketing-cro/SKILL.md) - Conversion optimization for checkout
- [../startup-business-models/SKILL.md](../startup-business-models/SKILL.md) - Pricing strategy
- [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) - Payment security
- [../qa-testing-playwright/SKILL.md](../qa-testing-playwright/SKILL.md) - E2E testing patterns

---

## Freshness Protocol

When users ask version-sensitive questions about payment platforms, do a freshness check.

### Trigger Conditions

- "What's the best payment platform for [use case]?"
- "Stripe vs Paddle vs LemonSqueezy?"
- "How do I handle [tax/VAT/sales tax]?"
- "What's new in Stripe [API/Billing/Checkout]?"
- "Is Stripe Managed Payments available?"
- "Best mobile subscription SDK?"

### How to Freshness-Check

1. Start from `data/sources.json` (official docs, changelogs, API versions).
2. Run a targeted web search for the specific platform and feature.
3. Prefer official documentation and changelogs over blog posts.

### What to Report

- **Current landscape**: what is stable and widely used now
- **Emerging trends**: Managed Payments, usage-based billing, entitlements API
- **Deprecated/declining**: hardcoded payment_method_types, top-level invoice.subscription
- **Recommendation**: default choice + alternatives with trade-offs

## Ops Runbook: Checkout 500 + Authorization or RLS Denials

Use this when checkout endpoints return 500 and DB writes fail due to auth policy (for example PostgreSQL RLS, tenant predicates, or missing role grants).

### 5-Step Incident Loop

```bash
# 1) Trace checkout call path fast
rg -n "checkout|purchase|subscription|webhook" src app lib

# 2) Reproduce with minimal request (capture full response)
curl -i -X POST http://localhost:3000/api/purchases/checkout \
  -H 'content-type: application/json' \
  -d '{"productKey":"example"}'

# 3) Inspect auth and policy checks in code
rg -n "auth\.|user_id|tenant_id|policy|row level|RLS|canPurchase" src app lib

# 4) Verify DB policies (PostgreSQL)
psql "$DATABASE_URL" -c "select schemaname, tablename, policyname, permissive, cmd, qual, with_check from pg_policies where tablename in ('purchases','subscriptions','orders') order by tablename, policyname;"

# 5) Verify constrained insert path under app role
psql "$DATABASE_URL" -c "begin; set local role app_user; -- run minimal insert/select test here; rollback;"
```

### Required Logging for Fast Triage

- `request_id`, `user_id`, `tenant_id`, `product_key`, `price_id`, `policy_branch`
- database error code + message + table name
- payment provider request id (`stripe_request_id` or equivalent)

### Guardrails

- Keep checkout create calls idempotent (idempotency key per user + product + window).
- Validate authorization before payment intent/session creation.
- In webhook handlers, never trust client state; reconcile from provider event + DB.
- Fail closed on entitlement write errors; do not grant access on partial checkout success.

