---
name: software-payments
description: "Designs production payment and billing systems. Use when implementing Stripe, Paddle, Adyen, subscriptions, tax, marketplaces, or mobile purchase flows."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Payments & Billing Engineering

Use this skill to design, implement, and debug production payment integrations: checkout flows, subscription lifecycle handling, billing portals, entitlement gating, webhooks, regional pricing, and payment-testing strategy.

Keep the skill focused on system choice and durable integration defaults. Push provider-specific code detail, migration edge cases, and deep implementation examples into the references.

## Quick Reference

| Need | Default | Reference |
|------|---------|-----------|
| SaaS subscriptions | Stripe Checkout or Payment Links | [references/stripe-patterns.md](references/stripe-patterns.md) |
| Custom branded checkout | Stripe Payment Element plus Express Checkout Element | [references/stripe-patterns.md](references/stripe-patterns.md) |
| Merchant of record | Paddle, LemonSqueezy, or Stripe Managed Payments when eligible | [references/platform-comparison.md](references/platform-comparison.md) |
| Enterprise multi-method processing | Adyen | [references/platform-comparison.md](references/platform-comparison.md) |
| UK or EU bank debit and local methods | GoCardless, Mollie, or open-banking providers | [references/uk-eu-payments-guide.md](references/uk-eu-payments-guide.md) |
| Usage or complex billing | Stripe Billing Meters, Chargebee, Recurly, or Lago | [references/platform-comparison.md](references/platform-comparison.md), [references/subscription-lifecycle.md](references/subscription-lifecycle.md) |
| Webhook reliability | verified signatures plus idempotent processing | [references/webhook-reliability-patterns.md](references/webhook-reliability-patterns.md) |
| Entitlement and feature gating | registry plus API enforcement plus UI paywall | [references/feature-gating-patterns.md](references/feature-gating-patterns.md) |
| Native iOS in-app purchase | StoreKit 2 with backend JWS verification; add RevenueCat only when multi-platform entitlement sync materially justifies it | [references/storekit2-native-patterns.md](references/storekit2-native-patterns.md) |
| Checkout and webhook testing | Stripe CLI plus E2E automation | [references/testing-patterns.md](references/testing-patterns.md) |

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

## Defaults

- Stripe is the default processor for most SaaS and product teams.
- Hosted checkout is the default starting point unless branded custom UI is a hard requirement.
- Webhooks are the source of truth for subscription and entitlement state.
- Initialize provider clients lazily; do not fail builds on missing secrets at import time.
- Omit `payment_method_types` unless you intentionally restrict available methods.
- Make every webhook handler signature-verified and idempotent.
- Keep feature gating enforced in three places: registry, API boundary, and UI paywall.
- Treat platform availability, API versions, preview features, and tax behavior as volatile and verify before final advice.

## Workflow

1. Classify the business model:
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
5. Add testing, observability, and incident handling before calling the integration production-ready.

## ASCII Flow

```text
Payments task
  -> Define money movement, provider, customer, and ledger boundary
  -> Classify charge, subscription, payout, refund, dispute, or wallet flow
  -> Design idempotency, webhooks, reconciliation, and audit trail
  -> Implement failure handling, retries, and customer-safe messaging
  -> Verify provider rules, network behavior, and compliance constraints
  -> Test success, decline, duplicate, timeout, refund, and retry paths
```

## Platform Selection Defaults

| Situation | Default |
|-----------|---------|
| standard SaaS subscription | Stripe |
| managed tax and seller-of-record model | Paddle or LemonSqueezy; Stripe Managed Payments only where eligible |
| high-volume or enterprise payment ops | Adyen |
| mobile subscription-heavy product | StoreKit 2 or Play Billing as the store-of-record; add RevenueCat only when cross-platform entitlement sync, experiments, or web-plus-store coordination materially justify it |
| UK or EU local rails and direct debit | GoCardless, Mollie, or open-banking providers |
| complex contract, seat, or revenue-recognition logic | Chargebee or Recurly on top of the processor |
| usage-based metering or token billing | Stripe Billing Meters or Lago |

Use [references/platform-comparison.md](references/platform-comparison.md) and [references/uk-eu-payments-guide.md](references/uk-eu-payments-guide.md) for the detailed trade-offs.

## Known Traps

- Hybrid mobile billing without one entitlement registry. If App Store, Play Billing, and web subscriptions can all grant access, define one canonical entitlement state and one conflict-resolution rule before launch.
- Treating checkout success redirects as purchase truth. Redirects are UX only; provisioning must wait for the verified webhook or store-server notification path.
- Mixing mobile digital-goods policy boundaries with web-SaaS billing assumptions. Apple and Google policy treatment for in-app digital goods is volatile and must be re-verified before final implementation advice.
- Assuming RevenueCat is automatically the default for every mobile subscription stack. It is a coordination layer, not a requirement, and adds its own operational surface.
- Reusing one webhook consumer for unrelated billing side effects without idempotent boundaries. Entitlements, invoicing, CRM sync, and analytics fan-out need separate retry and replay behavior.
- Deferring tax, merchant-of-record, and invoice-issuer decisions until after checkout buildout. Those choices affect product catalog, legal entity exposure, refunds, and support flows.

## Common Anti-Patterns

- Selling iOS in-app digital goods through Stripe inside the native app flow.
- Creating separate product or price catalogs in web, mobile, and billing systems with no synchronization contract.
- Using provider object IDs as the only entitlement key instead of a stable internal subscription or account identity.
- Shipping a billing portal without a tested downgrade, cancellation, refund, and grace-period policy.
- Letting the pricing page, checkout copy, entitlement rules, and CRM lifecycle drift independently.
- Treating revenue analytics events as operational truth for access control.

## Stripe Integration Defaults

If Stripe is the chosen processor, keep these defaults:

- initialize the server client lazily
- prefer Checkout or Payment Links first
- let Stripe choose dynamic payment methods unless business rules require restriction
- use webhooks, not the client redirect, as the source of truth
- store internal user and tier metadata carefully and validate it before DB use
- use subscription schedules for preplanned billing changes
- keep billing portal enabled for self-serve changes
- use entitlements when packaging changes often, but still enforce authorization in your own API

Use [references/stripe-patterns.md](references/stripe-patterns.md) for API-version notes, webhook mappings, and migration detail.

## Production Readiness Checklist

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

**Testing and migrations**

- [references/testing-patterns.md](references/testing-patterns.md)
- [references/in-app-browser-checkout-contract.md](references/in-app-browser-checkout-contract.md)
- [assets/template-checkout-entrypoint-propagation-checklist.md](assets/template-checkout-entrypoint-propagation-checklist.md)
- [data/sources.json](data/sources.json)

## July 2026 Regulatory and Scheme Traps

- **SCA 3DS2 test card matrix (Stripe)**: use `4000000000003220` to force a 3DS2 challenge flow; use `4000000000003063` for a frictionless 3DS2 authentication; use `4000002500003155` for a card requiring authentication; use `4000008400001629` for a card where 3DS2 is not supported (fallback to 3DS1 or no-auth). Verify current test card list in Stripe docs before CI test runs — card numbers and behaviour occasionally change between API versions.
- **SCA exemptions apply to low-value and MIT transactions**: merchant-initiated transactions (subscriptions, saved-payment charges) are exempt from SCA when correctly flagged with `off_session: true` and a valid mandate; failing to set this flag causes unexpected declines on renewal charges. EMV 3DS 2.3.1 (August 2022) remains the deployed spec; 2.3.1 is not a hard requirement for exemption handling, but issuer/network support for it varies — a v2.4 pilot with AI-based risk scoring and EU Digital Identity Wallet support is in early 2026 rollout and is not yet something to build against.
- **PSD3 / PSR — agreed, not yet in force**: the European Parliament and Council reached political agreement on PSD3 and the Payment Services Regulation (PSR) in November 2025; final texts were published in April 2026 and cleared committee/plenary votes in the following weeks. Official Journal publication was expected around mid-2026 but may slip later in the year — verify current status before citing an in-force date. The PSR is a Regulation (direct effect, no national transposition); PSD3 is a Directive requiring member-state transposition, typically 18–24 months after entry into force. Do not build to final PSD3/PSR requirements yet, but flag the expected changes below as architecture risks now.
- **PSD3 / PSR changes to design around**: mandatory open banking performance/API standards, revised SCA exemption thresholds, stronger consumer liability protections for APP fraud (aligning with the direction already set by UK PSR 2024 mandatory reimbursement), and expanded scope to one-leg-out (one side of the transaction outside the EEA) transactions.
- **EU Instant Payments Regulation (IPR) milestones**: eurozone PSPs have had to receive instant SEPA credit transfers since 9 January 2025 and send them since 9 October 2025, with Verification of Payee (VOP) required in the eurozone since October 2025. Non-euro EU member states have longer runways: VOP is not required until 9 July 2027, and the obligation to send instant credit transfers in euro from local-currency accounts can extend to 9 June 2028 under specified conditions. Re-verify exact dates against the regulation text before committing an implementation date to a customer.
- **Visa Acquirer Monitoring Program (VAMP)**: Visa lowered the merchant "excessive" fraud-plus-dispute ratio threshold from 2.20% to 1.50% effective 1 April 2026 for the US, Canada, EU, and APAC (CEMEA remains at 2.20% as of this writing). The ratio merges fraud reports (TC40) and disputes (TC15) — a single disputed-and-flagged transaction can count twice. Acquirer-level thresholds (0.5% "above standard", 0.7% "excessive") also apply. Treat these exact percentages as volatile and verify against current Visa program documentation before advising a merchant near the line.
- **Mastercard Excessive Chargeback Program (ECP)**: two tiers apply over a trailing two-month window — Excessive Chargeback Merchant (ECM) at roughly 100–299 chargebacks and a 1.5%–2.99% ratio, and High Excessive Chargeback Merchant (HECM) at 300+ chargebacks and a 3%+ ratio. Fines escalate from roughly $1,000 to $200,000+ at HECM, with possible MATCH listing. Verify current thresholds and fee schedules in the Mastercard rulebook before quoting numbers to a merchant.
- **PCI DSS v4.0.1**: this is the sole active version of the standard (v4.0 was retired; v4.0.1 is a clarification-only release, no new requirements). All 51 future-dated requirements from v4.0 became mandatory on 31 March 2025 and are now baseline, not aspirational — assessors expect them in scope (e.g., authenticated internal vulnerability scans, phishing-resistant MFA for CDE access, targeted risk analyses). Route full compliance scoping to a security/compliance specialist; this skill covers scope-reduction choices (SAQ A vs A-EP vs D) at the checkout-surface level.
- **Stripe Managed Payments (merchant of record)**: Stripe announced general availability of Managed Payments in 2026 after a 2025 private beta, but rollout remains gradual and is gated by seller eligibility (initially concentrated on US-based sellers in good standing, digital-goods sellers, no Connect dependency). Verify current eligibility and supported surfaces directly with Stripe before committing to an MoR architecture built on it.
- **UK BNPL regulation**: the FCA's new regime for deferred payment credit (BNPL) enters into force 15 July 2026, requiring creditworthiness assessments before every agreement (including sub-£50 agreements, subject to a proportionate/outcomes-based approach), upfront disclosure, financial-difficulty support pathways, and FOS access. Firms could register for temporary permission from 15 May 2026 through 1 July 2026. This date is imminent relative to last-validated — re-verify it has actually taken effect before advising a BNPL integration as unregulated.
- **UK PSD2 / FCA rules post-Brexit**: UK SCA rules under FCA PSRs 2017 (as amended) remain in force and broadly mirror EU SCA with some divergences; the UK's mandatory APP-fraud reimbursement regime under PSR 2024 is already live and distinct from the EU's PSD3/PSR APP-fraud provisions still working through the legislative process — do not assume UK and EU consumer-liability rules are identical.
- **Surcharging rules**: surcharging on card payments remains prohibited for consumer cards in the EU and UK; verify local rules before any dynamic pricing or fee pass-through feature that touches card instruments.

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Verify provider availability, preview status, API-version behavior, and tax or compliance claims before final advice.
- Prefer official processor, merchant-of-record, and platform docs over secondary summaries.
- If live verification is unavailable, mark provider-specific claims as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

