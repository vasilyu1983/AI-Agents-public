# UK & EU Payment Platforms Guide

Platforms available to UK/EU-based businesses beyond the core Stripe/Adyen stack. Check account eligibility and onboarding requirements for the chosen seller location.

Pricing, availability, and regulatory timelines move quickly. Use the pricing and policy lookup at the relevant decision before making a recommendation.

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
- [Market and Regulatory Watch](#market-and-regulatory-watch)
- [Decision Matrix: When to Choose Which](#decision-matrix-when-to-choose-which)


## Tier 1: Self-Serve, Full Coverage

### GoCardless

**What:** Direct Debit specialist (UK Bacs, SEPA, ACH, BECS, PAD). Collects recurring payments by pulling directly from bank accounts; compare bank-debit fees and recovery behavior with the card alternative.

**Signup:** Self-serve at gocardless.com. Check entity eligibility and onboarding requirements before promising a launch date.

**Pricing:** Read [GoCardless pricing](https://gocardless.com/pricing/) for the seller country, payment scheme, caps, add-ons and FX fees.

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

**What:** European multi-method payment processor. Supports cards, iDEAL (NL), Bancontact (BE), SEPA DD, Klarna, Apple Pay, PayPal through one integration; confirm enabled methods for the seller and currency.

**Signup:** Self-serve at mollie.com. Check supported seller locations and onboarding requirements.

**Pricing:** Read [Mollie pricing](https://www.mollie.com/pricing) for the seller country and enabled methods, including refund and chargeback fees.

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

**Pricing:** Read [Square UK pricing](https://squareup.com/gb/en/pricing) for online, in-person and invoice surfaces, including card-origin surcharges.

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

**Pricing:** Read [PayPal UK merchant fees](https://www.paypal.com/uk/business/paypal-business-fees) for the product, method, cross-border mix and currency conversion.

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

**Best for:** Offering a wallet customers already use; measure incremental completed orders. Use alongside Stripe (Stripe handles cards, PayPal handles wallet users).

---

## Tier 2: Self-Serve, Sectoral

### Klarna

**What:** Buy Now, Pay Later (BNPL). Customers split payments into 3-4 installments. Merchant receives full amount upfront (minus fee).

**Signup:** Self-serve at klarna.com/business. Check country and category eligibility.

**Pricing:** Read [Klarna’s business site](https://www.klarna.com/business/) and obtain the seller quote for the relevant country, payment product and refund/dispute terms.

**Integration:** Via Klarna Payments API or through Stripe/Mollie/Adyen as a payment method.

**Regulatory note:** the FCA regulates deferred payment credit (BNPL) lending. Take the regime's current status, scope, affordability and disclosure duties, and the lender's authorisation status from qualified UK regulatory counsel before launch; do not treat BNPL as unregulated.

**Best for:** E-commerce where installment terms fit the customer and product. Fashion, electronics, home goods. Not suitable for SaaS subscriptions.

### SumUp

**What:** Mobile POS and card reader specialist. Online payments API expanding.

**Pricing:** Read [SumUp UK pricing](https://www.sumup.com/en-gb/pricing/) for the device, online surface, plan and transaction mix.

**Best for:** Small merchants, market stalls, pop-up shops. Limited API — not for custom SaaS integrations.

---

## Tier 3: Sales-Required (Enterprise)

| Platform | Focus | Onboarding | Notes |
|----------|-------|-----------|-------|
| **Checkout.com** | High-volume online payments | Obtain seller quote | Cards, Apple Pay, Google Pay. Strong in UK/EU. Interchange++ pricing. |
| **TrueLayer** | Open Banking payments (A2A) | Contact sales | UK/EU bank-to-bank via Open Banking APIs. Instant settlement. |
| **Yapily** | Open Banking infrastructure | Contact sales | Check bank and country coverage for the required AIS/PIS flows. |
| **WorldPay** | Legacy enterprise payments | Enterprise only | Check the acquiring entity, integration surface and support window. |

---

## Open Banking (UK/EU)

**What:** Regulated bank-to-bank (A2A) payments via PSD2/Open Banking APIs. Customer authorizes payment directly from their bank app without sharing card details; the payment-initiation provider remains part of the flow.

**UK market:** For market-sizing claims, read [Open Banking Limited’s published updates](https://www.openbanking.org.uk/news/) and distinguish users, connections and payments; do not use a forecast as an observed adoption figure.

**EU market:** Receive, send and Verification of Payee obligations have different deadlines by currency region and institution type. Check the [ECB’s Instant Payments Regulation overview](https://www.ecb.europa.eu/paym/retail/instant_payments/html/instant_payments_regulation.en.html) and the regulation text before assigning a customer deadline.

**Key benefits:**
- No card processing fee, but A2A provider, bank, FX and refund costs can still apply
- Settlement timing depends on the rail and provider; confirm funds availability before fulfillment
- Card-scheme chargebacks do not apply, but fraud reimbursement, mistaken-payment recovery and refunds can still create liability
- Strong authentication built in (bank app approval)

**Integration options:**
- **TrueLayer** (most developer-friendly) — REST API, hosted payment page
- **Yapily** — lower-level integration; check the required banks and payment rails
- **Stripe** — Pay by Bank for one-time checkout in supported markets
- **GoCardless** — Instant Bank Pay (Open Banking-powered DD mandate setup)

**Best for:** High-value one-off payments (property, car, B2B invoices), subscription mandate setup, payroll, treasury operations.

---

## Market and Regulatory Watch

| Event | Impact |
|-------|--------|
| **UK Open Banking adoption** | A2A payments are mainstream enough to evaluate for high-value checkout; take current connection figures from Open Banking Limited's published statistics before quoting one. |
| **EU Instant Payments Regulation** | Receive, send and Verification of Payee obligations phase in separately for eurozone and non-euro member states; take the dates from the regulation text or qualified EU regulatory counsel. |
| **BNPL regulation (UK)** | The FCA deferred payment credit regime changes affordability and disclosure duties; take its current status from qualified UK regulatory counsel. |
| **Stripe Managed Payments** | Merchant-of-record option for eligible digital sellers already on Stripe, gated by business location and integration type; check Stripe's eligibility page before designing around it. |
| **PSD3 / PSR (EU)** | Check publication, effective dates and applicability through qualified EU regulatory counsel. |

---

## Decision Matrix: When to Choose Which

| Scenario | Recommended | Why |
|----------|-------------|-----|
| Default SaaS billing | Stripe | Most flexible API, largest ecosystem |
| EU-focused, need iDEAL/Bancontact | Mollie | Relevant local methods and seller eligibility |
| UK Direct Debit recurring | GoCardless | Specialist DD mandate and collection lifecycle |
| Need PayPal button | Stripe (PayPal method) or PayPal Commerce | Customer wallet demand; measure incremental completed orders |
| Online + in-person POS | Square | Unified commerce platform |
| BNPL for e-commerce | Klarna (via Stripe/Mollie/direct) | Split payments, merchant paid upfront |
| High-value A2A transfers | Open Banking (TrueLayer) | Bank-to-bank rail; verify funds availability and total fees |
| Enterprise high-volume | Checkout.com or Adyen | Interchange++ pricing at scale |
| Multi-method EU checkout | Mollie or Adyen | Check exact method and seller-country support |
| Bank data + payments | Yapily / TrueLayer | PSD2 AIS + PIS combined |
