# Stripe Cost Guide

Operational reference for understanding and reducing Stripe payment processing spend. Covers pricing structure, cost drivers ranked by typical impact, volume negotiation, and a repeatable optimization checklist.

## Table of Contents

- [Pricing Structure](#pricing-structure)
- [Cost Drivers](#cost-drivers)
  - [Transaction Processing Fees](#transaction-processing-fees)
  - [Dispute and Chargeback Fees](#dispute-and-chargeback-fees)
  - [Stripe Billing](#stripe-billing)
  - [Stripe Tax](#stripe-tax)
  - [Radar Fraud Prevention](#radar-fraud-prevention)
  - [Connect Platform Fees](#connect-platform-fees)
- [Volume Negotiation](#volume-negotiation)
- [Common Optimization Checklist](#common-optimization-checklist)
- [Monitoring](#monitoring)
- [When to Consider Alternatives](#when-to-consider-alternatives)

---

## Pricing Structure

Standard US rates. All percentages apply on top of each other where multiple features are used.

| Fee Type | Rate | Notes |
|---|---|---|
| Domestic card (US) | 2.9% + $0.30 | Per successful charge |
| International card | +1.5% | Added to base rate (total 4.4% + $0.30) |
| Currency conversion | +1% | On top of international surcharge if converting |
| ACH Direct Debit | 0.8%, capped at $5 | Per transaction |
| ACH Credit | $1.00 | Per payout |
| Wire transfers | $8.00 | Domestic wire |
| Instant payouts | 1%, min $0.50 | To debit card or bank |
| Stripe Billing | +0.5% | On recurring revenue, added to processing fees |
| Stripe Tax | +0.5% | Per transaction with tax calculation |
| Radar | $0.05/txn | $0.07/txn for Radar for Fraud Teams |
| Disputes | $15 | Per dispute, win or lose |

Key takeaway: a US SaaS company using Billing, Tax, and Radar on a domestic card pays roughly 3.95% + $0.30 + $0.05 per transaction before any disputes. International cards push that past 5.4%.

---

## Cost Drivers

Ranked by typical impact on total Stripe spend.

### Transaction Processing Fees

The base cost. Unavoidable, but the largest single line item and the most negotiable at volume.

- Standard pricing is blended: Stripe absorbs interchange variance and charges a flat 2.9% + $0.30.
- Interchange-plus pricing is available at roughly $80K+/month volume. You pay actual interchange (varies by card type, typically 1.5–2.2%) plus a fixed Stripe markup. This is almost always cheaper for businesses with a predictable card mix.
- International cards add 1.5% automatically. Currency conversion adds another 1%.

Optimization levers:

- Use ACH Direct Debit for large B2B invoices. On a $10K invoice, ACH costs $5 vs. $290.30 on card.
- Minimize international transactions where possible — localize billing entities or encourage domestic payment methods.
- Negotiate interchange-plus pricing once volume justifies it.

### Dispute and Chargeback Fees

$15 per dispute regardless of outcome. The direct fee is bad; the indirect cost is worse — high dispute rates (above 0.75%) trigger card network monitoring programs that carry fines and potential account termination.

Common waste:

- Not using Radar for fraud prevention on transactions that later result in disputes.
- Missing 3D Secure on high-risk transactions (eliminates liability shift).
- Unclear billing descriptors that cause "I don't recognize this charge" disputes.

Optimization levers:

- Enable Radar ($0.05–$0.07/txn). If your dispute rate exceeds 0.1%, Radar pays for itself.
- Implement 3D Secure for high-risk transactions (large amounts, new customers, international).
- Set clear billing descriptors that match your brand name and product.
- Respond to disputes promptly with evidence — winning reverses the charge but not the $15 fee.

### Stripe Billing

0.5% on recurring revenue, applied on top of processing fees. On $100K MRR, that is $500/month ($6K/year) for subscription management.

When Billing is worth it:

- You need dunning (failed payment retries with customizable schedules).
- You need proration for mid-cycle plan changes.
- You need metered or usage-based billing with automatic invoice generation.
- You need hosted customer portal for self-service subscription management.

When to skip it:

- Simple monthly charge with no plan changes — use the Charges or PaymentIntents API directly.
- Annual billing with manual invoicing — use Stripe Invoicing without Billing.
- You already have subscription logic in your application and only need Stripe for payment processing.

Optimization: audit whether you actually use Billing features. Many teams enable it during setup and never use dunning or proration.

### Stripe Tax

0.5% per transaction for automatic tax calculation and collection. On $200K/month revenue, that is $1K/month ($12K/year).

When Tax is worth it:

- Selling to multiple US states and need sales tax compliance.
- Selling to EU customers and need VAT calculation.
- No in-house tax expertise and need audit-ready reporting.

When a third-party tool may be better:

- TaxJar: cheaper at volume, strong US nexus tracking, starts at $99/month flat.
- Avalara: better for complex tax scenarios (physical goods, mixed taxability), enterprise pricing.
- Paddle or Lemon Squeezy: handle tax as part of merchant-of-record model, eliminating the problem entirely.

Optimization: compare 0.5% of revenue against flat-rate third-party costs. At high revenue, flat-rate tools are significantly cheaper.

### Radar Fraud Prevention

$0.05 per screened transaction for Radar; $0.07 per transaction for Radar for Fraud Teams (adds manual review queues, custom lists, and advanced rules).

When Radar is worth it:

- Dispute rate exceeds 0.1%.
- Selling digital goods or services with high fraud exposure.
- Processing international transactions.

Optimization levers:

- Use Radar rules to skip screening on low-risk transactions: returning customers with successful payment history, small amounts below your fraud threshold, corporate cards from known accounts.
- Start with base Radar ($0.05). Upgrade to Fraud Teams ($0.07) only if you need manual review queues or custom block/allow lists.
- Monitor Radar's false positive rate — blocking legitimate customers is a hidden cost.

### Connect Platform Fees

Relevant if you operate a marketplace or platform with Stripe Connect.

Fee structures by charge type:

- **Direct charges**: the connected account pays Stripe fees. You collect a platform fee via `application_fee_amount`.
- **Destination charges**: you pay Stripe fees on the full amount, then transfer to connected account.
- **Separate charges and transfers**: you control the full flow but manage fee allocation manually.

Optimization levers:

- Choose the charge type that matches your business model. Direct charges are cheapest if connected accounts have their own Stripe relationship.
- Audit connected accounts — remove unused, test, or abandoned accounts.
- Use `application_fee_amount` rather than taking a percentage at the transfer level to keep fee reporting clean.

---

## Volume Negotiation

### When to Negotiate

- Processing $80K+/month consistently (some sources cite $50K as the floor, but $80K gets more attention from Stripe sales).
- Predictable volume with low dispute rates strengthens your position.

### What Is Negotiable

- **Interchange-plus pricing**: replaces the blended 2.9% with actual interchange + a fixed Stripe markup (typically 0.2–0.5%).
- **Reduced per-transaction fee**: the $0.30 fixed fee can be reduced for high-volume, low-average-ticket businesses.
- **Dispute fee waivers or reductions**: possible at very high volume with demonstrated low dispute rates.
- **Volume discounts on Radar, Billing, or Tax**: bundled pricing at scale.

### How to Approach

1. Gather 3–6 months of processing data: volume, average ticket, dispute rate, refund rate.
2. Get competing quotes from Adyen, Square, or a direct processor relationship.
3. Contact Stripe sales (not support) and request a custom pricing review.
4. Lead with your total volume and growth trajectory — Stripe prices on expected lifetime value.

### Typical Savings

- 0.2–0.5% reduction on processing rate at $80K–$500K/month.
- Larger reductions possible above $1M/month.
- On $200K/month processing, a 0.3% reduction saves $7.2K/year.

---

## Common Optimization Checklist

1. **Review dispute rate.** If above 0.1%, enable Radar. If above 0.5%, treat as urgent — card network monitoring programs start at 0.75%.
2. **Use ACH for large B2B payments.** Any invoice over $500 is cheaper via ACH ($5 cap) than card (2.9% + $0.30).
3. **Set clear billing descriptors.** Match your trading name and product. Reduces "unrecognized charge" disputes by 20–40%.
4. **Audit Billing and Tax usage.** Only pay for features you actively use. Disable Billing if you manage subscriptions in your own code. Disable Tax if you use a third-party tax tool.
5. **Negotiate rates at $80K+/month.** Request interchange-plus pricing and reduced per-transaction fees.
6. **Audit connected accounts.** Remove unused, test, or abandoned Connect accounts.
7. **Review webhook retry settings.** Failed webhooks can trigger retried charges that still incur processing fees. Ensure idempotency keys are set and retry logic is sound.
8. **Minimize international card surcharges.** Localize billing entities in key markets or offer local payment methods.

---

## Monitoring

### Stripe Dashboard

- **Payments > Overview**: total volume, successful charges, refunds.
- **Payments > Disputes**: dispute count, rate, and outcomes.
- **Billing > Overview**: MRR, churn, failed payments (if using Billing).
- **Reports > Financial reports**: fee breakdown by type.

### Key Metrics to Track

| Metric | Target | Red Flag |
|---|---|---|
| Effective fee rate | < 3.5% domestic | > 4% without international volume |
| Dispute rate | < 0.1% | > 0.5% (network monitoring at 0.75%) |
| Refund rate | < 2% | > 5% signals product/expectation issues |
| Failed payment rate | < 5% of attempts | > 10% signals card update or retry issues |

### Alerting

- Set up alerts for dispute rate spikes (Stripe Dashboard > Radar > Rules or via webhook events).
- Monitor `charge.dispute.created` webhook events and route to an ops channel.
- Track monthly fee totals against budget — unexpected increases often indicate a new Stripe product was enabled or international volume shifted.

---

## When to Consider Alternatives

| Scenario | Alternative | Why |
|---|---|---|
| High volume (>$1M/month) | Adyen, direct processor | Lower interchange-plus rates, more control over payment routing |
| B2B SaaS needing tax + billing | Paddle, Lemon Squeezy | Merchant of record handles tax, billing, and payments — one fee, no tax compliance burden |
| Marketplaces | Adyen for Platforms, PayPal Commerce | Compare Connect fees and payout flexibility |
| Subscription-heavy with low AOV | Evaluate per-transaction fee impact | The $0.30 fixed fee hurts on small charges (e.g., $5 subscription = 8.9% effective rate) |
| Crypto or alternative payments | Direct integrations | Stripe supports limited crypto; specialized processors may be cheaper |

Stripe's strength is developer experience and speed of integration. Switching costs are real — factor in engineering time, not just fee savings. A 0.2% fee reduction that takes 3 months of engineering to implement may not be worth it below $500K/month volume.
