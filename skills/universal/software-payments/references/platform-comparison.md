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
- [Hybrid Pattern (RevenueCat + Stripe)](#hybrid-pattern-revenuecat--stripe)
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
- [Braintree (Legacy / Migration-Only)](#braintree-legacy--migration-only)
- [Decision Matrix](#decision-matrix)
- [Migration Paths](#migration-paths)
- [Stripe -> Paddle](#stripe---paddle)
- [LemonSqueezy -> Stripe](#lemonsqueezy---stripe)
- [Stripe -> Stripe Managed Payments](#stripe---stripe-managed-payments)
- [Stripe Managed Payments (MoR)](#stripe-managed-payments-mor)
- [RevenueCat Integration (Mobile + Web)](#revenuecat-integration-mobile--web)


## Stripe

**Best for:** Maximum control, complex billing, marketplaces, established businesses.

### Strengths
- Most complete API and SDK ecosystem
- Currency and payment-method coverage varies by seller location and checkout surface; check the required markets in Stripe’s docs
- Stripe Connect for marketplace/platform payments
- Stripe Tax for automated tax calculation
- Stripe Radar for fraud detection (ML-based)
- Stripe Invoicing for B2B
- Stripe Billing Meters for usage-based pricing
- Managed Payments offers merchant-of-record processing for eligible digital products; confirm account access and integration eligibility
- Stripe Link for accelerated checkout
- Flexible `billing_mode`, Subscription Schedules, and Entitlements for more complex billing setups

### Weaknesses
- You retain merchant tax responsibility with a processor; calculation tooling and a merchant-of-record contract address different responsibilities
- Higher complexity for simple SaaS
- Dispute/chargeback management is your responsibility

### Pricing
Read [Stripe pricing](https://stripe.com/pricing) for the seller country, payment-method and cross-border mix. Include Billing, Tax, FX, dispute and payout charges in the comparison.

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
- Merchant of record for supported products and markets, including indirect-tax handling
- Automatic tax calculation and filing
- Handles refunds, chargebacks, and customer invoicing
- Paddle Retain for dunning and churn reduction
- ProfitWell Metrics (acquired) for revenue analytics
- Relatively simple integration for the value provided

### Weaknesses
- Compare the full MoR quote with processor, tax, support and dispute costs
- Less flexible API than Stripe
- Limited customization of checkout experience
- No marketplace/Connect equivalent
- Smaller ecosystem of third-party integrations

### Pricing
Read [Paddle pricing](https://www.paddle.com/pricing) and the seller quote for transaction charges, add-ons and the scope of MoR services.

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
- Compare total fees and add-ons with the alternative MoR quote
- Less mature API compared to Stripe/Paddle
- Limited webhook events compared to Stripe
- Usage-based billing exists, but the broader billing surface is still narrower than Stripe or Chargebee
- Limited marketplace support

### Pricing
Read [Lemon Squeezy pricing](https://www.lemonsqueezy.com/pricing) for the base fee, international/subscription add-ons and payout costs.

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
Read [RevenueCat pricing](https://www.revenuecat.com/pricing) for the definition of billable tracked revenue, included features and overage treatment.

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

**Best for:** Enterprise businesses needing negotiated acquiring, local payment methods or unified online and point-of-sale processing.

### Strengths
- Local payment methods across supported markets; check the specific method and seller-country combination
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
Read [Adyen pricing](https://www.adyen.com/pricing) and the negotiated quote. Compare processing, scheme, interchange, minimum-invoice and ancillary fees for your actual transaction mix.

### When to Choose Adyen Over Stripe
- A negotiated interchange++ quote beats the alternative for your observed country, card and channel mix
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
- Integrations with CRM and accounting systems; verify the required connector and plan
- Hosted checkout pages and customer portal included

### Weaknesses
- Check metering ingestion, aggregation and retention limits against the intended workload
- Adds a billing layer = additional vendor and cost
- Can be overkill for simple tier-based SaaS
- Chargebee-managed dunning may conflict with Stripe's built-in dunning

### Pricing
Read [Chargebee pricing](https://www.chargebee.com/pricing/) and the quote for revenue-based fees, feature tiers and minimum commitments; add the underlying processor fees.

### When to Choose Chargebee
- B2B SaaS with per-seat + usage hybrid pricing
- Need revenue recognition / ASC 606 compliance
- Sales-led with custom contracts and quotes
- Outgrowing hand-rolled subscription logic on top of Stripe

---

## Recurly (Billing Orchestrator)

**Best for:** B2C subscription businesses, media/streaming, companies focused on churn reduction and revenue recovery.

### Strengths
- Dunning and revenue recovery; measure recovered revenue against a control before claiming uplift
- Strong B2C subscription analytics (MRR, churn, LTV, cohort analysis)
- Multi-gateway support (Stripe, Adyen, Braintree, Worldpay)
- Flexible pricing models (flat, tiered, usage, ramp)
- Hosted payment pages with PCI compliance
- Confirm support coverage, escalation paths and service levels in the contract

### Weaknesses
- Reporting features often criticized as limited/inaccurate
- Less flexible API compared to Chargebee for custom logic
- Weaker B2B/enterprise billing features
- No built-in revenue recognition (via partner integrations)

### Pricing
Read [Recurly pricing](https://recurly.com/plans/) and the quote for platform, transaction and add-on fees; include the processor’s separate charges.

### When to Choose Recurly Over Chargebee
- B2C subscriptions (media, streaming, consumer SaaS)
- Churn reduction is your top priority
- Need best-in-class dunning automation
- Need the contracted support coverage and escalation model

---

## Lago (Open-Source Billing)

**Best for:** AI/ML SaaS with usage-based pricing, developer-tools companies, teams wanting billing logic in their own infrastructure.

### Strengths
- Self-hostable; review the [Lago platform’s AGPLv3 license](https://github.com/getlago/lago/blob/main/LICENSE) and the chosen component’s license
- Purpose-built for usage-based billing (API calls, AI tokens, compute, storage)
- Real-time metering with aggregation engine
- Composable pricing: flat + usage + per-seat in one plan
- Event-driven metering; benchmark ingestion and aggregation against your workload
- Growing fast in AI/developer-tools space

### Weaknesses
- Younger platform (less battle-tested than Chargebee/Recurly)
- Smaller ecosystem of integrations
- Self-hosting requires infrastructure investment
- Cloud version still maturing
- No built-in dunning comparable to Recurly

### Pricing
Read [Lago pricing](https://www.getlago.com/pricing) for managed deployment and premium features. For self-hosting, budget infrastructure and operations and review the component licenses.

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
| Enterprise, negotiated acquiring | Adyen |
| SaaS with global tax needs | Paddle or Stripe Managed Payments |
| Indie developer, digital products | LemonSqueezy |
| Mobile app subscriptions | RevenueCat |
| Marketplace / multi-party payments | Stripe Connect or Adyen for Platforms |
| B2B invoicing | Stripe Invoicing |
| Complex subscription logic (per-seat + usage) | Chargebee on top of Stripe |
| B2C subscriptions, churn focus | Recurly on top of Stripe |
| Usage-based pricing (simple) | Stripe Billing Meters |
| Usage-based pricing (complex, AI tokens) | Lago (open-source) or Chargebee |
| Already on Stripe, eligible digital products, need MoR | Evaluate Stripe Managed Payments after checking account and product eligibility |
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

## Stripe Managed Payments (MoR)

For a digital-product seller seeking a merchant of record, check [Managed Payments eligibility](https://docs.stripe.com/payments/managed-payments/eligibility) before designing the migration:

1. Confirm the legal entity’s seller location is supported and Stripe has approved account access. Do not infer eligibility from a US-only rollout assumption.
2. Check the product category, distribution rights, automation requirements and eligible product tax codes.
3. Check the [overview’s integration restrictions](https://docs.stripe.com/payments/managed-payments) against the intended surface. It documents Checkout and Payment Links; do not assume every Stripe API or Connect flow is available.
4. Read the applicable commercial terms and pricing. Compare tax responsibility, support, refunds and disputes with Paddle or Lemon Squeezy for the actual sales regions.

Release labels, supported locations and feature coverage are lookup inputs. An eligibility review is required even when the integration surface is documented.

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
