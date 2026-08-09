# Payment Platform Comparison

Detailed comparison across three platform layers: processors (Stripe, Adyen), merchants of record (Paddle, LemonSqueezy), and billing orchestrators (Chargebee, Recurly, Lago). Plus mobile (RevenueCat) and deprecation warnings (Braintree).

Pricing, availability, and preview status change frequently. Verify live pricing pages and official docs before making a final recommendation.

---
## Table of Contents

- [Stripe](#stripe)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [Key Integration Points](#key-integration-points)
- [Paddle](#paddle)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [When to Choose Paddle Over Stripe](#when-to-choose-paddle-over-stripe)
- [LemonSqueezy](#lemonsqueezy)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [When to Choose LemonSqueezy](#when-to-choose-lemonsqueezy)
- [RevenueCat](#revenuecat)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [Hybrid Pattern (RevenueCat + Stripe)](#hybrid-pattern-revenuecat-stripe)
- [Adyen](#adyen)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [When to Choose Adyen Over Stripe](#when-to-choose-adyen-over-stripe)
- [Chargebee (Billing Orchestrator)](#chargebee-billing-orchestrator)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [When to Choose Chargebee](#when-to-choose-chargebee)
- [Recurly (Billing Orchestrator)](#recurly-billing-orchestrator)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [When to Choose Recurly Over Chargebee](#when-to-choose-recurly-over-chargebee)
- [Lago (Open-Source Billing)](#lago-open-source-billing)
- [Strengths](#strengths)
- [Weaknesses](#weaknesses)
- [Pricing](#pricing)
- [When to Choose Lago](#when-to-choose-lago)
- [Braintree (Legacy / Migration-Only)](#braintree-legacy-migration-only)
- [Decision Matrix](#decision-matrix)
- [Migration Paths](#migration-paths)
- [Stripe -> Paddle](#stripe-paddle)
- [LemonSqueezy -> Stripe](#lemonsqueezy-stripe)
- [Stripe -> Stripe Managed Payments](#stripe-stripe-managed-payments)
- [Stripe Managed Payments (MoR) — 2025+](#stripe-managed-payments-mor-—-2025)
- [RevenueCat Integration (Mobile + Web)](#revenuecat-integration-mobile-web)


## Stripe

**Best for:** Maximum control, complex billing, marketplaces, established businesses.

### Strengths
- Most complete API and SDK ecosystem
- Support for 135+ currencies and 100+ payment methods
- Stripe Connect for marketplace/platform payments
- Stripe Tax for automated tax calculation
- Stripe Radar for fraud detection (ML-based)
- Stripe Invoicing for B2B
- Stripe Billing Meters for usage-based pricing
- Managed Payments generally available (2026) for eligible digital-product businesses, rollout still gated by seller eligibility
- Stripe Link for one-click checkout (50M+ stored cards)
- Flexible `billing_mode`, Subscription Schedules, and Entitlements for more complex billing setups

### Weaknesses
- You handle tax compliance by default (unless using Tax or Managed Payments)
- Higher complexity for simple SaaS
- Dispute/chargeback management is your responsibility

### Pricing
- Standard: 2.9% + 30c (US domestic)
- International: +1.5% (cross-border)
- Stripe Tax: 0.5% per transaction
- No monthly fees (pay-per-use)

### Key Integration Points
```
Checkout Session -> Webhook -> DB Sync -> Feature Gating
     |                                        |
     +--> Success URL (client redirect)       |
     +--> Cancel URL (client redirect)        |
                                              v
                                    Subscription Context
                                    (React Context / API middleware)
```

---

## Paddle

**Best for:** SaaS businesses selling globally, especially to EU customers needing VAT compliance.

### Strengths
- Full merchant of record: handles VAT, sales tax, GST in 200+ countries
- Automatic tax calculation and filing
- Handles refunds, chargebacks, and customer invoicing
- Paddle Retain for dunning and churn reduction
- ProfitWell Metrics (acquired) for revenue analytics
- Relatively simple integration for the value provided

### Weaknesses
- Higher fee (5% + 50c) compared to Stripe
- Less flexible API than Stripe
- Limited customization of checkout experience
- No marketplace/Connect equivalent
- Smaller ecosystem of third-party integrations

### Pricing
- 5% + 50c per transaction
- No monthly fees
- Includes all tax compliance, fraud, chargebacks

### When to Choose Paddle Over Stripe
- Selling to EU/UK customers (VAT compliance is complex)
- Small team without tax/legal resources
- B2C SaaS with global customer base
- Want to avoid dealing with payment disputes

---

## LemonSqueezy

**Best for:** Indie developers, small SaaS, digital products, creators.

### Strengths
- MoR: handles tax compliance globally
- Simple integration (embeddable checkout, overlay)
- Built-in affiliate system
- Email marketing tools included
- Nice dashboard for non-technical founders
- Acquired by Stripe in 2024 — long-term backing

### Weaknesses
- 5% + 50c fees (same as Paddle)
- Less mature API compared to Stripe/Paddle
- Limited webhook events compared to Stripe
- Usage-based billing exists, but the broader billing surface is still narrower than Stripe or Chargebee
- Limited marketplace support

### Pricing
- 5% + 50c per transaction
- Free tier available
- Includes all tax compliance

### When to Choose LemonSqueezy
- Solo developer or very small team
- Digital products (ebooks, courses, templates)
- Want simplest possible integration
- Don't need advanced billing features

---

## RevenueCat

**Best for:** Mobile apps that need unified subscriptions across iOS, Android, and optionally web.

### Strengths
- Wraps both App Store and Google Play billing
- Unified API for cross-platform subscriptions
- Web Billing for browser checkout with shared entitlements
- Experiments/A/B testing for pricing
- Detailed subscription analytics (MRR, churn, LTV)
- Handles receipt validation
- Webhook support for server-side logic
- Free tier for small apps
- Syncs with Stripe or Paddle billing engines

### Weaknesses
- Web flows are newer and less universal than the core mobile SDK path
- Doesn't replace Stripe or Paddle if you need deep processor-level control
- Best fit is still subscription-led products, not broad payments orchestration
- Some billing-engine combinations add operational complexity

### Pricing
- Free: up to $2.5K MTR
- Starter: $99/mo (up to $10K MTR)
- Pro: $499/mo (custom MTR limits)
- Enterprise: custom

### Hybrid Pattern (RevenueCat + Stripe)

For apps with both mobile and web users:

```typescript
// Mobile: RevenueCat handles App Store / Google Play
// Web: Stripe handles checkout and billing
// Backend: Unified user subscription state

// When RevenueCat webhook fires:
if (event.type === 'INITIAL_PURCHASE') {
  await db.subscriptions.upsert({
    user_id: event.app_user_id,
    platform: 'mobile',
    tier: mapRevenueCatToPlan(event.product_id),
    status: 'active',
  });
}

// When Stripe webhook fires:
if (event.type === 'customer.subscription.created') {
  await db.subscriptions.upsert({
    user_id: event.data.object.metadata.user_id,
    platform: 'web',
    tier: getTierFromPriceId(event.data.object.items.data[0].price.id),
    status: 'active',
  });
}
```

---

## Adyen

**Best for:** Enterprise businesses, high-volume processors (>$1M/yr), companies needing 250+ local payment methods.

### Strengths
- Largest local payment method coverage (250+ methods globally)
- Interchange++ pricing (transparent, lower at high volume)
- Unified platform: online, in-app, and point-of-sale
- Adyen for Platforms (marketplace/multi-party equivalent to Stripe Connect)
- Strong in APAC, LATAM, and EMEA local methods
- Used by Uber, Spotify, eBay, Microsoft

### Weaknesses
- Complex setup — not suitable for startups or low-volume businesses
- No built-in subscription billing (pair with Chargebee/Recurly)
- Less developer-friendly documentation compared to Stripe
- Interchange++ pricing model can be confusing for small teams
- Limited self-serve — requires sales engagement for onboarding

### Pricing
- Interchange++ (transaction processing fee + scheme fee + Adyen markup)
- No monthly minimums for online payments
- Volume-dependent — gets cheaper at scale
- Typical effective rate: 1.5-2.5% for high-volume EU transactions

### When to Choose Adyen Over Stripe
- Processing >$1M/yr (interchange++ becomes cheaper than Stripe flat rate)
- Need local payment methods in APAC/LATAM that Stripe doesn't support
- Unified online + point-of-sale on one platform
- Enterprise compliance requirements (SOC 2 Type II, PCI Level 1)

---

## Chargebee (Billing Orchestrator)

**Best for:** B2B SaaS with complex billing logic — per-seat, usage-based, contract billing, multi-currency invoicing.

### Strengths
- Sits on top of Stripe/Adyen/Braintree (you keep your processor)
- Advanced subscription management (trials, prorations, contract terms)
- Revenue recognition (ASC 606 / IFRS 15 compliance)
- Quote-to-cash workflow for B2B sales-led deals
- 100+ integrations (Salesforce, HubSpot, Xero, QuickBooks)
- Hosted checkout pages and customer portal included

### Weaknesses
- Usage-based billing limited to 5,000 records per subscription lifetime
- Adds a billing layer = additional vendor and cost
- Can be overkill for simple tier-based SaaS
- Chargebee-managed dunning may conflict with Stripe's built-in dunning

### Pricing
- Startup: Free (up to $250K revenue)
- Performance: 0.75% of revenue
- Enterprise: custom
- Plus processor fees (Stripe/Adyen) on top

### When to Choose Chargebee
- B2B SaaS with per-seat + usage hybrid pricing
- Need revenue recognition / ASC 606 compliance
- Sales-led with custom contracts and quotes
- Outgrowing hand-rolled subscription logic on top of Stripe

---

## Recurly (Billing Orchestrator)

**Best for:** B2C subscription businesses, media/streaming, companies focused on churn reduction and revenue recovery.

### Strengths
- Best-in-class dunning and revenue recovery (claims 8-12% revenue uplift)
- Strong B2C subscription analytics (MRR, churn, LTV, cohort analysis)
- Multi-gateway support (Stripe, Adyen, Braintree, Worldpay)
- Flexible pricing models (flat, tiered, usage, ramp)
- Hosted payment pages with PCI compliance
- US-based support team (never outsourced)

### Weaknesses
- Reporting features often criticized as limited/inaccurate
- Less flexible API compared to Chargebee for custom logic
- Weaker B2B/enterprise billing features
- No built-in revenue recognition (via partner integrations)

### Pricing
- Core: Free (limited features)
- Professional: custom pricing
- Elite: custom pricing
- Plus processor fees on top

### When to Choose Recurly Over Chargebee
- B2C subscriptions (media, streaming, consumer SaaS)
- Churn reduction is your top priority
- Need best-in-class dunning automation
- Prefer US-based support

---

## Lago (Open-Source Billing)

**Best for:** AI/ML SaaS with usage-based pricing, developer-tools companies, teams wanting billing logic in their own infrastructure.

### Strengths
- Open-source (MIT license), self-hostable
- Purpose-built for usage-based billing (API calls, AI tokens, compute, storage)
- Real-time metering with aggregation engine
- Composable pricing: flat + usage + per-seat in one plan
- Event-driven architecture (scales to billions of events)
- Growing fast in AI/developer-tools space

### Weaknesses
- Younger platform (less battle-tested than Chargebee/Recurly)
- Smaller ecosystem of integrations
- Self-hosting requires infrastructure investment
- Cloud version still maturing
- No built-in dunning comparable to Recurly

### Pricing
- Self-hosted: Free (MIT license)
- Cloud: usage-based pricing
- Premium: custom

### When to Choose Lago
- AI/ML product with token-based or compute-based pricing
- Need metering flexibility beyond Stripe Billing Meters
- Want billing logic in your own infrastructure
- Open-source alignment / vendor independence

---

## Braintree (Legacy / Migration-Only)

> **WARNING:** Treat Braintree as legacy for new builds. PayPal has deprecated the Drop-in SDK and the Braintree mobile SDK SSL pinning deadline has passed. Verify current migration paths and support windows in official PayPal deprecation policy docs before extending any existing integration.

**Migration paths:**
- For PayPal payments → Use Stripe's PayPal payment method or PayPal Commerce Platform directly
- For card processing → Migrate to Stripe or Adyen
- For Venmo → PayPal Commerce Platform

Do not start new projects on legacy Braintree surfaces unless you have a specific migration constraint.

---

## Decision Matrix

| Scenario | Recommendation |
|----------|---------------|
| Maximum API flexibility | Stripe |
| Enterprise, high-volume (>$1M/yr) | Adyen |
| SaaS with global tax needs | Paddle or Stripe Managed Payments |
| Indie developer, digital products | LemonSqueezy |
| Mobile app subscriptions | RevenueCat |
| Marketplace / multi-party payments | Stripe Connect or Adyen for Platforms |
| B2B invoicing | Stripe Invoicing |
| Complex subscription logic (per-seat + usage) | Chargebee on top of Stripe |
| B2C subscriptions, churn focus | Recurly on top of Stripe |
| Usage-based pricing (simple) | Stripe Billing Meters |
| Usage-based pricing (complex, AI tokens) | Lago (open-source) or Chargebee |
| Already on Stripe, eligible digital products, need MoR | Evaluate Stripe Managed Payments (GA, eligibility-gated) |
| Need it working today with MoR | Paddle |
| Hybrid mobile + web | RevenueCat (mobile) + Stripe (web) |
| Need PayPal button | Stripe PayPal method or PayPal Commerce Platform |
| Currently on Braintree | Plan a migration to Stripe, Adyen, or PayPal Commerce based on current surface area |
| Revenue recognition / ASC 606 | Chargebee RevRec |
| Desktop software / license keys | FastSpring (MoR) |

---

## Migration Paths

### Stripe -> Paddle
- Export customer data from Stripe
- Create Paddle products/prices to match
- Migrate active subscriptions gradually (honor current billing periods)
- Update webhook endpoints

### LemonSqueezy -> Stripe
- Natural since LemonSqueezy is Stripe-powered
- May get migration tools as Stripe integrates the acquisition

### Stripe -> Stripe Managed Payments
- Evaluate eligibility first: direct seller, digital goods/services, no Connect dependency
- Recheck unsupported surfaces before planning a migration
- Stripe handles tax + fraud + disputes for eligible flows going forward

---

## Stripe Managed Payments (MoR) — 2025→2026

Stripe introduced **Managed Payments** as a merchant of record offering, moving from private beta (2025) to general availability (2026) for eligible digital-product sellers:

- Stripe handles global tax compliance (80+ countries for indirect tax as of the GA announcement)
- AI-driven fraud prevention and dispute handling
- Transaction-level customer support
- GA for subscriptions, one-time purchases, and usage-based billing, but rollout is still gated by seller eligibility (initially concentrated on US-based sellers in good standing) — verify current eligibility before scoping a build
- Supports direct sellers; Connect platforms are not supported
- Checkout-only surface today (hosted or embedded form); verify current unsupported features before recommending it

**Decision: Stripe MoR vs Paddle vs LemonSqueezy**

| Factor | Stripe Managed Payments | Paddle | LemonSqueezy |
|--------|------------------------|--------|--------------|
| Tax handling | Included | Included | Included |
| Ecosystem | Full Stripe ecosystem | Standalone | Stripe-powered |
| Pricing | Verify current GA pricing | 5% + 50c | 5% + 50c |
| API flexibility | Full Stripe API | Paddle API | Simpler API |
| Maturity | GA (2026), eligibility-gated rollout | Production | Production |
| Best for | Already on Stripe, meets eligibility gates | Established SaaS | Indie/small SaaS |

---

## RevenueCat Integration (Mobile + Web)

For mobile apps with in-app subscriptions, optionally unified with web billing:

```typescript
// RevenueCat SDK initialization (React Native)
import Purchases from 'react-native-purchases';

Purchases.configure({
  apiKey: REVENUECAT_API_KEY,
  appUserID: userId, // Match your backend user ID
});

// Check entitlements
const customerInfo = await Purchases.getCustomerInfo();
const isPro = customerInfo.entitlements.active['pro'] !== undefined;

// Purchase
const offerings = await Purchases.getOfferings();
const package = offerings.current?.availablePackages[0];
if (package) {
  const result = await Purchases.purchasePackage(package);
}
```
