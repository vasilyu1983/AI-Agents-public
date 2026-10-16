# Marketplace and Multi-Party Payouts

Load this when money moves from a buyer to a third party (seller, creator, affiliate, partner) through your platform. For single-merchant checkout use the main skill instead.

## 1. Pick the money-flow model first

The model decides who owes KYC, tax forms and licences. Choose before building the ledger.

Default for a program paying many small partners across countries: let a network or payout platform act as payer of record. It is usually cheaper than building KYC, tax-form collection and multi-country payouts in-house. Pay directly only when you need control the network cannot give, and price the in-house build first.

| Model | Who holds funds | Duties shift to |
|-------|-----------------|-----------------|
| Merchant of record (you sell, then pay suppliers) | You | You are the seller: tax collection, refunds, and your own payout obligations |
| Marketplace with connected accounts (provider holds and splits funds) | Payment provider | Provider carries most KYC and licensing; you carry platform duties and the provider's terms |
| Network or aggregator pays the payee (you only report the commission) | Third party | The payer does KYC and tax forms; you keep attribution and dispute data |

Default: connected accounts at a regulated provider. Deviate to merchant of record only when you need to own pricing, refunds and the customer relationship end to end. Deviate to network-pays when you do not need to touch the money.

Holding funds for others can be a regulated payment service in the UK and EU. If your design holds or pools payee money, stop and route the perimeter question to qualified UK regulatory counsel or qualified EU regulatory counsel and qualified counsel. Do not conclude from this file.

## 2. Commission ledger

Keep one ledger entry per payee earning, with these states:

`accrued` -> `held` -> `payable` -> `paid` -> `clawed back`

- Accrue on the sale event. Move to `held` for the refund and chargeback window. Move to `payable` when the window closes and the payee passes checks.
- A refund or dispute after payout creates a negative balance. Net it against the next payout. Decide up front, in the payee terms, how to recover a balance when no future payout exists.
- Use one idempotency key per payout batch and per payee line, so a retried batch cannot pay twice.
- Reconcile daily: payout file or provider payout report against ledger `paid` entries. Assign every mismatch an owner. See the reconciliation gate in `SKILL.md`.

## 3. Payee controls

- KYC at onboarding and before the first payout. Rescreen on a schedule.
- Sanctions screening against the lists that apply to you (for example OFSI for UK and OFAC for US exposure). Take the list scope from counsel.
- Bank-detail change is the top payout-fraud vector. Verify out of band (a call-back or a confirmation sent to the previously verified channel) and hold the next payout for a review window after any change.
- Hold period at least as long as your refund and chargeback window, not a convenience number. A shorter hold needs a reserve sized to expected clawbacks.
- Set a minimum payout and a rule for dormant balances. Escheat and unclaimed-property rules vary by jurisdiction, so send that rule to counsel.

## 4. Choosing a rail

Compare payout rails on criteria, then look up the numbers in each provider's current docs:

- countries and currencies supported for payees
- who does KYC and who is liable for payee fraud
- tax-form collection and filing support
- payout speed, reversal and clawback mechanics
- fees and who pays them (platform or payee)
- fit with your ledger: webhooks, payout reports, idempotency support

Candidates to check: Stripe Connect, Adyen for Platforms, PayPal Payouts, Wise, and dedicated payout platforms. Read the provider's connected-account or payout documentation for current fees, countries and tax-form support. Do not copy fees into your design doc without a date and source.

## 5. Tax forms and platform reporting

Payee tax forms, platform reporting duties and 1099-style filings are covered in ../../marketing-affiliate-partnerships/references/partner-payout-tax-ops.md. Use it rather than restating tax rules here.
