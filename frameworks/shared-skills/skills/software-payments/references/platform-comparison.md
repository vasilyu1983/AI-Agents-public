# Payment Platform Comparison (Feb 2026)

Detailed comparison across three platform layers: processors (Stripe, Adyen), merchants of record (Paddle, LemonSqueezy), and billing orchestrators (Chargebee, Recurly, Lago). Plus mobile (RevenueCat) and deprecation warnings (Braintree).

---

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
- Managed Payments (MoR) launching 2025
- Stripe Link for one-click checkout (50M+ stored cards)

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

## LemonSqueezy (Stripe-Powered)

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
- No usage-based billing
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

**Best for:** Mobile apps with in-app subscriptions (iOS + Android).

### Strengths
- Wraps both App Store and Google Play billing
- Unified API for cross-platform subscriptions
- Experiments/A/B testing for pricing
- Detailed subscription analytics (MRR, churn, LTV)
- Handles receipt validation
- Webhook support for server-side logic
- Free tier for small apps

### Weaknesses
- Mobile-only (no web checkout)
- Doesn't replace Stripe for web billing
- Limited to subscription billing models
- Can't handle one-time purchases via web

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

## Braintree (DEPRECATED — Avoid for New Projects)

> **WARNING (Feb 2026):** Braintree Drop-in SDK moves to unsupported status July 14, 2026. PayPal Powered by Braintree processing ends January 2027. SSL certificates for mobile SDKs expire March 30, 2026.

**Migration paths:**
- For PayPal payments → Use Stripe's PayPal payment method or PayPal Commerce Platform directly
- For card processing → Migrate to Stripe or Adyen
- For Venmo → PayPal Commerce Platform

Do NOT start new projects on Braintree.

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
| Already on Stripe, need MoR | Wait for Stripe Managed Payments GA |
| Need it working today with MoR | Paddle |
| Hybrid mobile + web | RevenueCat (mobile) + Stripe (web) |
| Need PayPal button | Stripe PayPal method or PayPal Commerce Platform |
| Currently on Braintree | Migrate to Stripe or Adyen (Braintree EOL Jan 2027) |
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
- Expected to be a configuration change, not a full migration
- Opt-in on existing Stripe account
- Stripe handles tax + fraud + disputes going forward

---

## Stripe Managed Payments (MoR) — 2025+

Stripe announced **Managed Payments** in 2025 as a merchant of record offering, expanding through 2026:

- Stripe handles global tax compliance (VAT in 100+ countries)
- AI-driven fraud prevention with Smart Disputes (+13% chargeback win rate)
- Transaction-level customer support
- Expanding from private preview for subscription SaaS and digital goods (NA + EU)
- Acquired LemonSqueezy in 2024 to build this capability
- Expected to be a configuration toggle on existing Stripe accounts (not a full migration)

**Decision: Stripe MoR vs Paddle vs LemonSqueezy**

| Factor | Stripe Managed Payments | Paddle | LemonSqueezy |
|--------|------------------------|--------|--------------|
| Tax handling | Included | Included | Included |
| Ecosystem | Full Stripe ecosystem | Standalone | Stripe-powered |
| Pricing | TBD (likely % + fee) | 5% + 50c | 5% + 50c |
| API flexibility | Full Stripe API | Paddle API | Simpler API |
| Maturity | Private preview | Production | Production |
| Best for | Already on Stripe | Established SaaS | Indie/small SaaS |

---

## RevenueCat Integration (Mobile)

For mobile apps with in-app subscriptions:

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
