# Agentic Commerce

How to let AI agents start purchases without handing them open-ended spending power. Covers both sides: the **agent or platform** that buys on a user's behalf, and the **seller** that accepts agent-initiated orders.

## Contents

- [Threat Model](#threat-model)
- [Controls](#controls)
- [Human Confirmation Gates](#human-confirmation-gates)
- [Disputes, Fraud, and Evidence](#disputes-fraud-and-evidence)
- [Stripe Implementation Notes](#stripe-implementation-notes)
- [Checklist](#checklist)

## Threat Model

An agent is software that acts on untrusted input, such as product pages, reviews, or tool output, and can loop or retry. Design so that no prompt, injected instruction, or model error can:

- spend more than the user approved, or with a merchant the user did not choose
- reuse a payment credential after the purchase it was issued for
- place the same order twice because a request was retried
- bind the user to a subscription or other recurring charge without their knowledge

Spending policy is deterministic code. The model can propose a purchase; it must not decide whether a limit applies.

## Controls

| Control | Rule | Why |
|---------|------|-----|
| Scoped, limited-use credential | Give the agent a per-transaction token bound to one seller, one currency, a maximum amount (set to the cart total), and an expiry. Never put a PAN, a reusable saved payment method, or an unrestricted API key in the agent's context. | A leaked or misused token can only complete the one purchase it was issued for. |
| Revocation | Make credentials revocable until they are used, and treat the used, expired, or revoked state as terminal. | Lets the user or the platform cancel mid-flow. |
| Agent-side spend policy | Enforce per-transaction caps, per-period budgets, merchant allowlists, and category blocks in code before issuing a credential. | Limits are enforced outside the model. |
| Seller-side authorization | The seller rechecks price, stock, tax, and the final total against what the credential allows, then approves or declines. If the approval step times out or fails, decline. | Stops price drift and stale-catalog orders from settling. |
| Idempotency | Key every checkout intent (for example, user + cart hash + session) and dedupe on it. Make the seller's approval and callback endpoints idempotent, because agents retry. | Retries must not produce duplicate orders or charges. |
| Strong customer authentication | Send any 3DS or redirect step to the human in a UI the agent cannot operate. | Authentication proves the customer, not the agent. |
| Provenance tagging | Record the originating agent on each order and payment, and monitor refund, dispute, and decline rates per agent. | A misbehaving agent shows up as a cluster. |

## Human Confirmation Gates

Require explicit human confirmation in a UI the model cannot operate, showing merchant, line items, final total, and recurrence, before any of these:

- amount above the user's auto-approve threshold, or the first purchase from a new merchant
- creating a subscription, installment plan, or any recurring or deferred charge
- changing the shipping address, payment method, or account-level settings
- non-refundable, age-restricted, or regulated goods
- anything the agent's policy check flagged as unusual, such as a price well above the catalog quote or a quantity outlier

Record the confirmation (who, what total, when, and the credential limits issued). You will need it as dispute evidence.

## Disputes, Fraud, and Evidence

- An agent-initiated card payment is still a card payment. Standard chargeback rights, dispute reason codes, and scheme monitoring programs apply to the seller. Check with your processor and the card-scheme rules for any agent-specific liability treatment before assuming a shift.
- Expect "I did not authorize this" disputes where the user approved an agent in general but not this order. The consent record, the issued credential's limits, and the agent identity are your evidence, so keep them with the order.
- Keep fraud screening on for agentic orders, and do not allowlist a traffic source only because it arrives through an agent platform.
- Run refunds and cancellations through the same flows as other orders so reconciliation and entitlement revocation stay unified.

## Stripe Implementation Notes

The notes below come from Stripe's agentic commerce docs. Several of these APIs are in preview and need a preview API version header, and availability is limited by country. Before building, read the live pages: [Agentic commerce](https://docs.stripe.com/agentic-commerce), [Shared payment tokens](https://docs.stripe.com/agentic-commerce/concepts/shared-payment-tokens), [Sell through agents](https://docs.stripe.com/agentic-commerce/for-sellers), [Manage your integration](https://docs.stripe.com/agentic-commerce/for-sellers/manage).

- **Protocols.** Stripe lists the Agentic Commerce Protocol ([ACP](https://www.agenticcommerce.dev/)) and UCP for selling through agents, and MPP or x402 for machine payments.
- **Shared payment tokens (SPTs).** The agent issues an SPT for the customer's payment method to the seller's Stripe profile (`seller_details.network_business_profile`), with `usage_limits` for `currency`, `max_amount`, and `expires_at`. Stripe's docs say the agent sets the maximum amount to match the transaction total. The seller receives a granted token and confirms a `PaymentIntent` with `payment_method_data[shared_payment_granted_token]`. The seller sees only limited payment-method details, such as brand and last four digits.
- **SPT lifecycle.** The agent can revoke an SPT before use. The statuses are `active`, `requires_action` (for example, 3DS for the customer), and the terminal `deactivated` (consumed, expired, or revoked). Listen for `shared_payment.issued_token.*` (agent) and `shared_payment.granted_token.deactivated` (seller) events.
- **Order approval hook.** Sellers can have Stripe call their endpoint to approve or decline each agentic checkout before it completes. Stripe declines the payment if the hook does not answer within its timeout, and returns an error to agents on a non-2xx response. Because some agents retry, the endpoint must be idempotent.
- **After checkout.** Orders arrive as `checkout.session.completed` and are tagged with the originating agent. Manual capture is available, and refunds and disputes use the existing Stripe flows. Fraud checks run according to the seller's Radar setup.

If you are not on Stripe, apply the same controls using your processor's equivalent of scoped or network tokens, and look up its agentic-payments docs before you design around a specific API.

## Checklist

- [ ] No raw card data, reusable payment method, or unrestricted key is ever in agent context or logs
- [ ] Each credential is bound to a seller, currency, maximum amount, and expiry, and is revocable
- [ ] Spend policy (caps, budgets, allowlists) is enforced in code before a credential is issued
- [ ] The seller revalidates totals and approves or declines, and a timeout declines
- [ ] Checkout, approval, and webhook handlers are idempotent under agent retries
- [ ] A human confirms high-risk actions in a UI the agent cannot drive, and the confirmation is stored
- [ ] Orders carry agent provenance, and dispute evidence includes the consent record
- [ ] Refund and cancellation paths are shared with non-agent orders
