---
name: software-payments
description: "Designs production payment and billing systems. Use when implementing Stripe, Paddle, Adyen, subscriptions, tax, marketplaces, or mobile purchase flows."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.3"
last_validated: 2026-07-11
---

# Payments & Billing Engineering

Use this skill to design, implement, and debug production payment integrations: checkout flows, subscription lifecycle handling, billing portals, entitlement gating, webhooks, regional pricing, and payment-testing strategy.

## Quick Reference

| Need | Default | Deviation | Reference |
|------|---------|-----------|-----------|
| Standard SaaS subscription checkout | Stripe Checkout or Payment Links | Use Payment Element plus Express Checkout Element when branded custom UI is a hard requirement | [references/stripe-patterns.md](references/stripe-patterns.md) |
| Merchant of record (managed tax/seller-of-record) | Paddle or LemonSqueezy | Evaluate Stripe Managed Payments after checking seller location, product tax codes, account eligibility and supported surfaces at its eligibility page | [references/platform-comparison.md](references/platform-comparison.md) |
| High-volume or enterprise multi-method processing | Adyen | — | [references/platform-comparison.md](references/platform-comparison.md) |
| UK or EU bank debit and local methods | GoCardless, Mollie, or open-banking providers | Repo-dependent: no bundle source differentiates the three by situation; keep whichever the existing integration already uses | [references/uk-eu-payments-guide.md](references/uk-eu-payments-guide.md) |
| Usage-based metering or token billing | Stripe Billing Meters or Lago | — | [references/subscription-lifecycle.md](references/subscription-lifecycle.md) |
| Complex contract, seat, or revenue-recognition billing | Chargebee or Recurly on top of the processor | — | [references/subscription-lifecycle.md](references/subscription-lifecycle.md) |
| Webhook reliability | verified signatures plus idempotent processing | — | [references/webhook-reliability-patterns.md](references/webhook-reliability-patterns.md) |
| Entitlement and feature gating | registry plus API enforcement plus UI paywall | — | [references/feature-gating-patterns.md](references/feature-gating-patterns.md) |
| Native iOS in-app purchase | StoreKit 2 with backend JWS verification | Add RevenueCat only when multi-platform entitlement sync materially justifies it | [references/storekit2-native-patterns.md](references/storekit2-native-patterns.md) |
| Checkout and webhook testing | Stripe CLI plus E2E automation | — | [references/testing-patterns.md](references/testing-patterns.md) |
| AI agents initiating purchases | Scoped, limited-use payment credential plus seller-side approval | Human confirmation for high-risk actions | [references/agentic-commerce.md](references/agentic-commerce.md) |

## When to Use This Skill

Use this skill when the primary work is:

- choosing a payment processor, merchant-of-record layer, or billing stack
- implementing hosted or custom checkout
- designing subscription lifecycle and webhook handling
- building feature gating and billing-portal flows
- handling regional pricing, tax-sensitive platform choice, or local methods
- testing and operating checkout or billing workflows

Route elsewhere when the main task is:

| Need | Use Instead |
|------|-------------|
| general backend implementation outside payments | [../software-backend/SKILL.md](../software-backend/SKILL.md) |
| API contract design without billing concerns | [../dev-api-design/SKILL.md](../dev-api-design/SKILL.md) |
| pricing strategy and package design | `startup-business-models` |
| checkout conversion optimization | `marketing-cro` |
| application security review | [../software-security-appsec/SKILL.md](../software-security-appsec/SKILL.md) |
| native app implementation around store billing | [../software-mobile/SKILL.md](../software-mobile/SKILL.md) |
| wallets, crypto settlement or on-chain money movement | [../software-crypto-web3/SKILL.md](../software-crypto-web3/SKILL.md) |
| Stripe-specific product/API guidance or account tooling | Available Stripe-maintained skills/plugins; discover them through [Stripe’s agent guidance](https://docs.stripe.com/skills), then follow the runtime’s installation and permission policy |

## Defaults

- Stripe is the default processor for most SaaS and product teams.
- Hosted checkout is the default starting point unless branded custom UI is a hard requirement.
- Verified webhooks trigger state sync; reconcile against the provider’s current objects because delivery can be duplicated or out of order.
- Initialize provider clients lazily; do not fail builds on missing secrets at import time.
- Omit `payment_method_types` unless you intentionally restrict available methods.
- Make every webhook handler signature-verified and idempotent.
- Keep feature gating enforced in three places: registry, API boundary, and UI paywall.
- Treat platform availability, API versions, preview features, and tax behavior as volatile and verify before final advice.

## Workflow

1. Define the money movement, provider, customer and ledger boundary, then classify the business model:
   - one-time purchase
   - subscription
   - usage-based billing
   - marketplace or multi-party flow
   - mobile IAP or hybrid web-plus-app billing
2. Choose the stack:
   - processor
   - merchant-of-record layer if needed
   - billing orchestrator if lifecycle complexity justifies it
3. Choose the checkout surface:
   - Checkout or Payment Links for speed
   - Payment Element for custom UX
4. Implement the operational core:
   - webhook verification
   - idempotent processing
   - billing portal or self-serve management
   - entitlement sync and feature gating
5. Reconcile provider balances or settlement reports, ledger entries and entitlements; assign unmatched records to an owner.
6. Test success, decline, duplicate, timeout, refund and retry paths; add observability and incident handling before calling the integration production-ready.

See the Quick Reference table above for platform defaults by situation, plus [references/platform-comparison.md](references/platform-comparison.md) and [references/uk-eu-payments-guide.md](references/uk-eu-payments-guide.md) for the detailed trade-offs. Mobile subscription default: StoreKit 2 or Play Billing as the store-of-record; add RevenueCat only when cross-platform entitlement sync, experiments, or web-plus-store coordination materially justify it.

## Known Traps

- Hybrid mobile billing without one entitlement registry. If App Store, Play Billing, and web subscriptions can all grant access, define one canonical entitlement state and one conflict-resolution rule before launch.
- Treating checkout success redirects as purchase truth. Redirects are UX only; provisioning must wait for the verified webhook or store-server notification path.
- Mixing mobile digital-goods policy boundaries with web-SaaS billing assumptions. Apple and Google policy treatment for in-app digital goods is volatile and must be re-verified before final implementation advice.
- Showing an iOS link or button to web checkout without branching on the App Store storefront. External-link allowances, entitlements and terms depend on storefront and app category. Branch on `Storefront.current` and re-read the applicable guideline and regional terms before shipping. See [references/storekit2-native-patterns.md](references/storekit2-native-patterns.md#11-external-purchase-links-guideline-311a).
- Assuming RevenueCat is automatically the default for every mobile subscription stack. It is a coordination layer, not a requirement, and adds its own operational surface.
- Reusing one webhook consumer for unrelated billing side effects without idempotent boundaries. Entitlements, invoicing, CRM sync, and analytics fan-out need separate retry and replay behavior.
- Deferring tax, merchant-of-record, and invoice-issuer decisions until after checkout buildout. Those choices affect product catalog, legal entity exposure, refunds, and support flows.

## Common Anti-Patterns

- Using a native digital-goods checkout that violates the applicable storefront’s purchase and external-link policies; verify those policies before choosing the surface.
- Creating separate product or price catalogs in web, mobile, and billing systems with no synchronization contract.
- Using provider object IDs as the only entitlement key instead of a stable internal subscription or account identity.
- Shipping a billing portal without a tested downgrade, cancellation, refund, and grace-period policy.
- Letting the pricing page, checkout copy, entitlement rules, and CRM lifecycle drift independently.
- Treating revenue analytics events as operational truth for access control.

## Stripe Integration Defaults

If Stripe is the chosen processor, apply the general Defaults above plus these Stripe-specific defaults:

- store internal user and tier metadata carefully and validate it before DB use
- use subscription schedules for preplanned billing changes
- keep billing portal enabled for self-serve changes
- use entitlements when packaging changes often, but still enforce authorization in your own API

Use [references/stripe-patterns.md](references/stripe-patterns.md) for API-version notes, webhook mappings, and migration detail.

## Agentic Commerce

When an AI agent buys on a user's behalf, or a seller accepts agent-initiated orders, give the agent only a per-transaction credential bound to a seller, currency, maximum amount, and expiry. Enforce spend limits in code, have the seller approve or decline against the final total, make every step idempotent under agent retries, require human confirmation for high-risk actions such as recurring charges or new merchants, and keep the consent record as dispute evidence. See [references/agentic-commerce.md](references/agentic-commerce.md), which includes Stripe shared-payment-token notes.

## Production Readiness Checklist

**Reconciliation gate.**

Define a provider-independent money record for expected amount, currency, fee, tax, settlement, refund, dispute, and current entitlement. Reconcile webhooks and provider balance or settlement reports against that record on a schedule, with an exception queue and an owner. A successful checkout redirect or webhook is event evidence; neither is proof that cash, accounting state, and access rights agree.

- [ ] Webhook signatures verified on every handler before processing
- [ ] All webhook handlers are idempotent (safe to replay the same event)
- [ ] Checkout creation and webhook failures are explicitly logged
- [ ] Dead-letter or retry strategy defined for out-of-order or failing events
- [ ] Stripe CLI (or equivalent) wired into local and CI test flows
- [ ] Tests cover success, decline, and 3DS / step-up challenge flows
- [ ] Incident playbook written for checkout 500s, auth failures, and policy denials
- [ ] Tax and merchant-of-record decisions finalized before checkout buildout
- [ ] Feature gating enforced in three places: registry, API boundary, UI paywall

Common mistakes:

| Mistake | Consequence |
|---------|-------------|
| Trusting client redirect as proof of purchase | Provisioning before the verified webhook, creating access without payment |
| Hardcoding prices or plan logic in code | Catalog drift and deploy-gated pricing changes |
| Setting `payment_method_types` unnecessarily | Unintentionally restricts available methods |
| Silently failing webhooks instead of retrying | Invisible entitlement loss or dangling subscriptions |
| Treating Apple/Google policy as stable across releases | Store rejection or forced redesign |

See: [references/testing-patterns.md](references/testing-patterns.md), [references/webhook-reliability-patterns.md](references/webhook-reliability-patterns.md), [references/feature-gating-patterns.md](references/feature-gating-patterns.md), [references/ops-runbook-checkout-errors.md](references/ops-runbook-checkout-errors.md)

## Navigation

**Core**

- [references/stripe-patterns.md](references/stripe-patterns.md)
- [references/platform-comparison.md](references/platform-comparison.md)
- [references/subscription-lifecycle.md](references/subscription-lifecycle.md)
- [references/feature-gating-patterns.md](references/feature-gating-patterns.md)

**Regional and operational**

- [references/uk-eu-payments-guide.md](references/uk-eu-payments-guide.md)
- [references/regional-pricing-guide.md](references/regional-pricing-guide.md)
- [references/webhook-reliability-patterns.md](references/webhook-reliability-patterns.md)
- [references/ops-runbook-checkout-errors.md](references/ops-runbook-checkout-errors.md)

**Mobile and in-app purchase**

- [references/storekit2-native-patterns.md](references/storekit2-native-patterns.md)

**Agentic commerce**

- [references/agentic-commerce.md](references/agentic-commerce.md)

**Testing and migrations**

- [references/testing-patterns.md](references/testing-patterns.md)
- [references/in-app-browser-checkout-contract.md](references/in-app-browser-checkout-contract.md)
- [assets/template-checkout-entrypoint-propagation-checklist.md](assets/template-checkout-entrypoint-propagation-checklist.md)
- [data/sources.json](data/sources.json)

## Regulatory and Scheme Traps

Thresholds, dates, and legislative status in this area change often. Look them up at the source each time; this section keeps only the engineering controls.

- **3DS test coverage**: CI should exercise challenge, frictionless, off-session-requires-authentication, decline-after-authentication, and 3DS-not-supported paths. Take the card numbers from Stripe's testing docs (docs.stripe.com/testing) or `stripe:test-cards` at the time you write the test; do not copy them from memory.
- **SCA exemptions for MIT**: merchant-initiated charges (renewals, saved-card charges) need `off_session: true` plus the required consent/mandate captured during on-session setup, with authentication where required. A missing flag can cause unexpected renewal declines. Check [EMVCo](https://www.emvco.com/emv-technologies/3-d-secure/) and provider support for published versus draft specification features before using them.
- **EU PSD3 / PSR**: check publication, effective dates and scope through qualified EU regulatory counsel before treating a provision as binding. Architecture risks to design for now: open-banking API performance standards, revised SCA exemptions, stronger APP-fraud liability, and one-leg-out scope.
- **EU Instant Payments Regulation**: instant SEPA send/receive and Verification of Payee obligations phase in by eurozone and non-euro member state. Take the dates from the regulation text or qualified EU regulatory counsel before committing an implementation date to a customer.
- **Visa VAMP**: the ratio counts fraud reports (TC40) and disputes (TC15) together, so one disputed-and-reported transaction can count twice. The main engineering lever is the exclusion path: disputes resolved pre-dispute (RDR/CDRN-type services) and Compelling Evidence 3.0 wins drop out of the ratio. Take merchant and acquirer thresholds from Visa's current VAMP fact sheet.
- **Mastercard ECP**: tiered by chargeback count and ratio over a trailing window, with escalating fees and possible MATCH listing. Take tiers and fee schedules from the current Mastercard rulebook before quoting numbers to a merchant. Treat a merchant near either scheme's threshold as a specialist-review trigger, not a self-serve calculation.
- **PCI DSS v4.0.1**: the future-dated v4.0 requirements are now baseline, including the payment-page script controls (6.4.3, 11.6.1). This skill covers checkout-surface scope reduction (SAQ A vs SAQ D; see [references/stripe-patterns.md](references/stripe-patterns.md)); route full scoping to a security/compliance specialist.
- **Stripe Managed Payments (merchant of record)**: eligibility-gated by business location, digital products, direct integrations only (no Connect), and Checkout Session or Payment Link surfaces. Check [Stripe’s eligibility page](https://docs.stripe.com/payments/managed-payments/eligibility) for seller locations, account review, product tax codes and supported surfaces before committing to an MoR architecture.
- **UK rules**: UK SCA (PSRs 2017 as amended), mandatory APP-fraud reimbursement, and the FCA deferred-payment-credit (BNPL) regime differ from EU rules. Route status and scope to qualified UK regulatory counsel; do not assume UK and EU consumer-liability rules match.
- **Surcharging**: consumer-card surcharging is prohibited in the EU and UK. Check local rules before any fee pass-through feature that touches card instruments.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
