# MiCA / Travel Rule Engineering Controls

Engineering-side checklist for systems operated by crypto-asset service providers (CASPs) and token issuers under Regulation (EU) 2023/1114 (MiCA) and the Transfer of Funds Regulation recast (Regulation (EU) 2023/1113).

**Scope boundary:** this file lists the systems, data, and controls engineering must build. Licensing, transitional-regime dates, member-state windows, capital, governance, whitepaper approval, and any "does MiCA apply to us" question belong to the legal skills:

- EU (MiCA, TFR, DORA, GDPR, NCA mapping): qualified EU regulatory counsel
- US (GENIUS Act, state MTLs, CLARITY Act status): qualified US regulatory counsel
- UK (FCA cryptoasset regime): qualified UK regulatory counsel

Do not restate statute status or deadlines here; they drift. Article numbers below are anchors for the conversation with legal; confirm the operative text and thresholds with qualified EU regulatory counsel before building to them.

---

## 1. Travel Rule (TFR) Data Plumbing

- [ ] Collect and transmit originator and beneficiary information with every crypto-asset transfer; there is no de minimis threshold for CASP-to-CASP transfers.
- [ ] Model the data explicitly: originator name, account identifier (address or account), and the address / ID / date-and-place-of-birth fields the counterparty needs; beneficiary name and account identifier.
- [ ] Integrate a Travel Rule messaging network or protocol (e.g. TRISA, or a commercial provider) behind an adapter so the provider can be swapped.
- [ ] Handle the "counterparty CASP does not support Travel Rule" path as an explicit state (block, hold, or accept-with-monitoring per compliance policy), not an exception.
- [ ] Self-hosted wallet transfers: extra ownership-verification duties apply above a TFR value threshold — build the ownership-evidence capture flow and take the exact threshold and duty from qualified EU regulatory counsel.
- [ ] Feed Travel Rule payloads into AML screening and transaction monitoring; retain them for the retention period compliance sets.

## 2. Custody and Segregation

- [ ] Client assets on addresses/accounts segregated from the CASP's own assets; the ledger can prove per-client positions at any time.
- [ ] Reconcile on-chain balances to the internal ledger at least daily; alert on any unexplained difference.
- [ ] Hot/warm/cold tiering with withdrawal velocity limits tied to reconciliation state (see SKILL.md custody gates).
- [ ] Key-management review and penetration testing on a fixed cadence, with evidence retained for supervisors.

## 3. Token Issuance Systems (ART / EMT)

- [ ] **Issuer eligibility is a hard gate.** Art. 48(1): only an issuer authorised as a credit institution or electronic money institution may offer an EMT to the public or seek its admission to trading (others only with the issuer's written consent). Do not build an EMT launch for an entity without that status.
- [ ] **Redemption at par.** Holders of EMTs can redeem at par; build, test, and monitor the redemption flow (queueing, cut-offs, reconciliation to reserve movements).
- [ ] **Means-of-exchange telemetry.** Art. 23 requires an ART issuer to stop issuing, and submit a reduction plan, when the estimated quarterly average of daily means-of-exchange transactions within a single currency area exceeds the article's transaction-count and value thresholds; Art. 58(3) extends this to EMTs denominated in a non-EU currency. Take the exact thresholds, deadline, and any significance scope from qualified EU regulatory counsel. Instrument per-currency-area transaction counts and values and alert well before the threshold; make "pause issuance" an operational switch.
- [ ] Reserve-of-assets reporting pipelines (Arts. 36–38 for ARTs; applied to significant EMTs by Art. 58(1)): data feeds for reserve composition, valuation, and independent audit. Confirm reporting cadence with legal before building schedules.
- [ ] Freeze/blacklist and upgrade authorities inventoried under the privileged-control gate in SKILL.md.

## 4. Product and Marketing Controls

- [ ] Gate public offer pages and marketing templates on a published, current white paper version; link the white paper from every marketing surface.
- [ ] Geo-gating: block offers in jurisdictions where the product is not authorised; log the decision inputs.
- [ ] Archive every marketing asset and its distribution record.

## 5. Operational Resilience Hooks

- [ ] Incident classification and reporting hooks (DORA applies to CASPs): severity taxonomy, timestamps, and evidence capture wired into incident tooling; the reporting obligations themselves are owned by legal.
- [ ] Outsourcing register for critical providers (custody tech, Travel Rule vendor, KYC, cloud).
- [ ] Business continuity and disaster recovery tested on a schedule, with results retained.

## 6. Scope Notes (Engineering-Relevant Only)

- **NFTs:** MiCA recital 10 excludes crypto-assets that are unique and not fungible with other crypto-assets. Large series or fractionalised items may not qualify; treat classification as a legal decision and keep metadata that supports it.
- **DeFi:** whether a protocol is "fully decentralised" is a legal analysis. Engineering should document admin keys, upgrade paths, and fee switches, since those facts drive the analysis.
