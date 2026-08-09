# UK & EU Payment Platforms Guide

Platforms available to UK/EU-based businesses beyond the core Stripe/Adyen stack. All Tier 1 and Tier 2 platforms offer self-serve signup.

Pricing, availability, and regulatory timelines move quickly. Treat specific fees and regulation dates here as a snapshot and re-check official sources before final recommendations.

---
## Table of Contents

- [Tier 1: Self-Serve, Full Coverage](#tier-1-self-serve-full-coverage)
- [GoCardless](#gocardless)
- [Mollie](#mollie)
- [Square](#square)
- [PayPal Commerce Platform](#paypal-commerce-platform)
- [Tier 2: Self-Serve, Sectoral](#tier-2-self-serve-sectoral)
- [Klarna](#klarna)
- [SumUp](#sumup)
- [Tier 3: Sales-Required (Enterprise)](#tier-3-sales-required-enterprise)
- [Open Banking (UK/EU)](#open-banking-ukeu)
- [Market Events 2025-26](#market-events-2025-26)
- [Decision Matrix: When to Choose Which](#decision-matrix-when-to-choose-which)


## Tier 1: Self-Serve, Full Coverage

### GoCardless

**What:** Direct Debit specialist (UK Bacs, SEPA, ACH, BECS, PAD). Collects recurring payments by pulling directly from bank accounts — lower fees than card payments, near-zero involuntary churn.

**Signup:** Self-serve at gocardless.com. UK company or sole trader. KYC typically < 24h.

**Pricing (verify current rates):**
- UK Bacs: 1% + 20p (capped at GBP 4)
- SEPA: 1% + 20c (capped at EUR 4)
- ACH: 1% + 30c (capped at USD 5)
- No monthly fee on Standard plan

**API pattern:**

```typescript
// GoCardless payment flow (server-side)
import gocardless from 'gocardless-nodejs';

const client = gocardless(process.env.GOCARDLESS_ACCESS_TOKEN!, {
  environment: gocardless.Environments.Live,
});

// 1. Create a Billing Request Flow (hosted mandate setup)
const billingRequestFlow = await client.billingRequestFlows.create({
  redirect_uri: `${appUrl}/mandate/complete`,
  exit_uri: `${appUrl}/mandate/cancel`,
  links: {
    billing_request: billingRequest.id,
  },
});

// 2. After mandate setup, create recurring payment
const payment = await client.payments.create({
  amount: 999,         // in pence
  currency: 'GBP',
  links: { mandate: mandateId },
  metadata: { user_id: userId, invoice_id: invoiceId },
});
```

**Webhooks:** Signed with `Webhook-Signature` header. Key events: `payments.confirmed`, `payments.failed`, `mandates.cancelled`.

**Best for:** Recurring B2B/B2C with predictable amounts. Gym memberships, SaaS with annual DD, utility-style billing. Pairs well with Stripe for card fallback.

---

### Mollie

**What:** European multi-method payment processor. Supports cards, iDEAL (NL), Bancontact (BE), SEPA DD, Klarna, Apple Pay, PayPal — 25+ methods via one integration.

**Signup:** Self-serve at mollie.com. EU/UK/CH companies. Typically approved in 1-2 business days.

**Pricing (verify current rates):**
- Cards: 1.8% + 25c (EU) / 2.8% + 25c (non-EU)
- iDEAL: 29c flat
- SEPA DD: 35c flat
- Klarna: 2.99% + 0c
- No monthly fee, no setup cost

**API pattern:**

```typescript
// Mollie payment creation (server-side)
import createMollieClient from '@mollie/api-client';

const mollie = createMollieClient({
  apiKey: process.env.MOLLIE_API_KEY!,
});

const payment = await mollie.payments.create({
  amount: { currency: 'EUR', value: '9.99' },
  description: 'Pro plan — monthly',
  redirectUrl: `${appUrl}/checkout/complete`,
  webhookUrl: `${appUrl}/api/mollie/webhook`,
  method: undefined, // Let customer choose (shows all enabled methods)
  metadata: { user_id: userId, tier: 'pro' },
});

// Redirect customer to payment.getCheckoutUrl()
```

**Webhooks:** POST to your `webhookUrl` with payment ID in body. Fetch full payment details via API to verify status.

**Best for:** EU-focused SaaS needing iDEAL/Bancontact/SEPA. Simpler API than Adyen, more EU methods than Stripe.

---

### Square

**What:** Full commerce platform — online payments, POS hardware, invoicing, banking. Strong UK presence since 2017.

**Signup:** Self-serve at squareup.com/gb. UK sole traders and companies.

**Pricing (verify current rates):**
- Online: 1.4% + 25p (EU cards) / 2.5% + 25p (non-EU)
- In-person (POS): 1.75% flat (UK)
- Invoices: 2.5%
- No monthly fee for payments

**API pattern:**

```typescript
// Square online checkout (server-side)
import { Client, Environment } from 'square';

const square = new Client({
  accessToken: process.env.SQUARE_ACCESS_TOKEN!,
  environment: Environment.Production,
});

const { result } = await square.checkout.createPaymentLink({
  idempotencyKey: crypto.randomUUID(),
  quickPay: {
    name: 'Pro Plan Monthly',
    priceMoney: { amount: BigInt(999), currency: 'GBP' },
    locationId: process.env.SQUARE_LOCATION_ID!,
  },
});
// Redirect to result.paymentLink.url
```

**Best for:** Businesses needing both online + in-person POS under one platform. Restaurants, retail with online ordering. Not ideal for pure SaaS.

---

### PayPal Commerce Platform

**What:** PayPal's modern API stack and a common migration target from older Braintree setups. Supports PayPal wallet, Venmo (US), cards, Pay Later, and local methods.

**Signup:** Self-serve at developer.paypal.com. Business account required.

**Pricing (verify current rates):**
- Standard: 2.9% + 30p (UK) — varies by method
- PayPal Checkout: includes buyer protection
- No monthly fee

**API pattern:**

```typescript
// PayPal Commerce Platform order creation (server-side)
const response = await fetch('https://api-m.paypal.com/v2/checkout/orders', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
    'PayPal-Request-Id': idempotencyKey,
  },
  body: JSON.stringify({
    intent: 'CAPTURE',
    purchase_units: [{
      amount: { currency_code: 'GBP', value: '9.99' },
      custom_id: userId,
    }],
    application_context: {
      return_url: `${appUrl}/paypal/complete`,
      cancel_url: `${appUrl}/paypal/cancel`,
    },
  }),
});
```

**Best for:** Maximizing checkout conversion — PayPal wallet is trusted by 400M+ users. Use alongside Stripe (Stripe handles cards, PayPal handles wallet users).

---

## Tier 2: Self-Serve, Sectoral

### Klarna

**What:** Buy Now, Pay Later (BNPL). Customers split payments into 3-4 installments. Merchant receives full amount upfront (minus fee).

**Signup:** Self-serve at klarna.com/business. UK and 45+ countries.

**Pricing:** Varies by merchant category — typically 3-6% per transaction. No setup fee.

**Integration:** Via Klarna Payments API or through Stripe/Mollie/Adyen as a payment method.

**Regulatory note:** the FCA's deferred payment credit (BNPL) regime enters into force 15 July 2026, requiring creditworthiness/affordability assessments for agreements (including sub-£50 agreements, under a proportionate outcomes-based test), upfront disclosure, and FOS access. This date is imminent relative to last-validated — re-verify it is actually in force, and check whether temporary-permission or full-authorisation status applies to the specific lender before launch.

**Best for:** E-commerce with AOV GBP 50-500. Fashion, electronics, home goods. Not suitable for SaaS subscriptions.

### SumUp

**What:** Mobile POS and card reader specialist. Online payments API expanding.

**Pricing:** 1.69% flat (in-person UK). Online: 2.5%.

**Best for:** Small merchants, market stalls, pop-up shops. Limited API — not for custom SaaS integrations.

---

## Tier 3: Sales-Required (Enterprise)

| Platform | Focus | Min Volume | Notes |
|----------|-------|-----------|-------|
| **Checkout.com** | High-volume online payments | ~$500K/yr | Cards, Apple Pay, Google Pay. Strong in UK/EU. Interchange++ pricing. |
| **TrueLayer** | Open Banking payments (A2A) | Contact sales | UK/EU bank-to-bank via Open Banking APIs. Instant settlement. |
| **Yapily** | Open Banking infrastructure | Contact sales | Connect to 2000+ banks across EU/UK for AIS and PIS. |
| **WorldPay (FIS)** | Legacy enterprise payments | Enterprise only | Largest acquirer globally. Complex integration. Legacy but ubiquitous. |

---

## Open Banking (UK/EU)

**What:** Regulated bank-to-bank (A2A) payments via PSD2/Open Banking APIs. Customer authorizes payment directly from their bank app — no card details, no intermediary.

**UK market:** UK open banking connections passed 16.5 million by December 2025 (up from 12.1 million a year earlier) and industry projections put usage above 30 million connections by end of 2026. Adoption is mainstream enough to consider for high-value checkout and account-to-account payment flows — treat the exact figure as volatile and verify current numbers from Open Banking Limited or the FCA before citing them externally.

**EU market:** the Instant Payments Regulation is driving a separate but related shift toward account-to-account rails. Eurozone PSPs must receive instant SEPA credit transfers (since 9 January 2025), send them (since 9 October 2025), and support Verification of Payee (since October 2025). Non-euro EU states have longer runways — VOP by 9 July 2027, sending obligations that can extend to 9 June 2028 under specified conditions. Re-verify exact dates before committing to a customer-facing timeline.

**Key benefits:**
- Zero card fees (flat per-transaction or percentage, typically 0.1-0.5%)
- Instant settlement (Faster Payments in UK)
- No chargebacks (irrevocable bank transfer)
- Strong authentication built in (bank app approval)

**Integration options:**
- **TrueLayer** (most developer-friendly) — REST API, hosted payment page
- **Yapily** — lower-level, connect to 2000+ banks
- **Stripe** — Pay by Bank for one-time checkout in supported markets
- **GoCardless** — Instant Bank Pay (Open Banking-powered DD mandate setup)

**Best for:** High-value one-off payments (property, car, B2B invoices), subscription mandate setup, payroll, treasury operations.

---

## Market Events 2025-26

| Event | Impact |
|-------|--------|
| **UK Open Banking 16.5M+ connections (Dec 2025)** | A2A payments are mainstream enough to evaluate for high-value checkout; verify the current figure before quoting it externally. |
| **EU Instant Payments Regulation** | Eurozone receive/send/VOP obligations are live (Jan 2025 / Oct 2025 / Oct 2025); non-euro states have until 2027-2028 — verify exact dates per member state. |
| **BNPL regulation (UK)** | FCA deferred payment credit regime enters into force 15 July 2026 — verify it has actually taken effect before treating BNPL as unregulated. |
| **Stripe Managed Payments** | Reached general availability in 2026, but eligibility-gated rollout (initially US-focused sellers); useful for eligible digital sellers already on Stripe, not yet a universal MoR replacement. |
| **PSD3 / PSR (EU)** | Political agreement reached Nov 2025; final texts agreed and moving through Parliament/Council approval in 2026; Official Journal publication expected but not confirmed as of last-validated date. Do not build to it as law yet. |

---

## Decision Matrix: When to Choose Which

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Default SaaS billing | Stripe | Most flexible API, largest ecosystem |
| EU-focused, need iDEAL/Bancontact | Mollie | Best EU local method coverage |
| UK Direct Debit recurring | GoCardless | Specialist DD, lowest involuntary churn |
| Need PayPal button | Stripe (PayPal method) or PayPal Commerce | 400M+ PayPal wallets |
| Online + in-person POS | Square | Unified commerce platform |
| BNPL for e-commerce | Klarna (via Stripe/Mollie/direct) | Split payments, merchant paid upfront |
| High-value A2A transfers | Open Banking (TrueLayer) | Zero card fees, instant settlement |
| Enterprise high-volume | Checkout.com or Adyen | Interchange++ pricing at scale |
| Multi-method EU checkout | Mollie or Adyen | 25-250+ local methods |
| Bank data + payments | Yapily / TrueLayer | PSD2 AIS + PIS combined |
