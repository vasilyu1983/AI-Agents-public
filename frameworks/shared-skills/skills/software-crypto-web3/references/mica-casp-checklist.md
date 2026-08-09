# MiCA CASP Readiness Checklist

Structured checklist for assessing compliance with Regulation (EU) 2023/1114 (MiCA — Markets in Crypto-Assets).
Applicable from 30 December 2024. The Article 143 national grandfathering period for pre-existing nationally-licensed operators ends **1 July 2026 at the latest EU-wide**; several member states set shorter national windows that closed earlier (e.g., the Netherlands, Finland, Latvia, Hungary, and Slovenia closed by mid-2025; Sweden by September 2025), while others used the full 18 months with their own filing-date conditions (e.g., Czech Republic required an application filed by 31 July 2025; Italy required AML-register entities to have filed by 30 December 2025). Verify the specific member state's deadline — do not assume either "already closed" or "safe until July 2026" without checking.

**Last Updated:** 2026-07-11

Primary legal source: EUR-Lex 2023/1114 (MiCA).

---

## Table of Contents

1. [Authorisation (CASP Licence)](#1-authorisation-casp-licence)
2. [Whitepaper Requirements](#2-whitepaper-requirements)
3. [Marketing Communication Rules](#3-marketing-communication-rules)
4. [Travel Rule (TFR)](#4-travel-rule-tfr)
5. [Stablecoin Issuance — ART and EMT](#5-stablecoin-issuance--art-and-emt)
6. [Organisational and Governance Requirements](#6-organisational-and-governance-requirements)
7. [Custody and Safeguarding](#7-custody-and-safeguarding)
8. [AML / KYC Integration](#8-aml--kyc-integration)
9. [Ongoing Supervisory Obligations](#9-ongoing-supervisory-obligations)
10. [UK and Third-Country Considerations](#10-uk-and-third-country-considerations)

---

## 1. Authorisation (CASP Licence)

**MiCA Title V — Articles 59–76**

- [ ] Identify the EU member state of primary establishment; submit CASP authorisation application to the relevant national competent authority (NCA).
- [ ] Confirm the entity meets minimum capital requirements (varying by service category; Arts. 67–68).
- [ ] Verify all intended crypto-asset services are listed in the authorisation application; services not listed cannot be offered post-authorisation.
- [ ] Confirm senior management fitness-and-propriety assessment is complete.
- [ ] Confirm the entity has a registered office in the EU and adequate substance (staff, systems, governance present in the jurisdiction).
- [ ] Identify qualifying shareholders (>10% ownership) and submit required background assessments.
- [ ] Entities operating under transitional national licensing must confirm their specific member state's grandfathering deadline and filing conditions (see header above) — deadlines and conditions vary by state and are not uniformly "December 2025."

---

## 2. Whitepaper Requirements

**MiCA Title II (ART), Title III (EMT), Title IV (other crypto-assets)**

- [ ] Determine whether tokens offered fall under ART, EMT, or "other crypto-asset" classification.
- [ ] Draft whitepaper complying with Annex I (other crypto-assets), Annex II (ART), or Annex III (EMT) templates.
- [ ] Whitepaper must include: issuer identity, token description, rights and obligations, underlying technology description, risk factors, and fee schedule.
- [ ] Notify the relevant NCA at least 20 working days before publication (certain categories may require approval rather than notification — verify by asset type).
- [ ] Publish whitepaper on issuer's public website; keep it current and update for material changes.
- [ ] Confirm whitepaper is available in official EU language(s) of the jurisdiction of offer; English is acceptable for cross-border offers if home-state language is also provided.
- [ ] Liability statement required: officers sign off on whitepaper accuracy.

---

## 3. Marketing Communication Rules

**MiCA Article 7 (other CA), Article 29 (ART), Article 46 (EMT), Article 77 (CASPs)**

- [ ] All marketing materials must be clearly identifiable as such and consistent with the whitepaper.
- [ ] Risk warnings must appear prominently and use prescribed language (EBA/ESMA RTS pending finalisation; check current NCA guidance for interim standards).
- [ ] Marketing materials must link to or reference the whitepaper.
- [ ] Social media posts, influencer content, and email campaigns are in scope — do not treat paid promotions as outside MiCA's marketing rules.
- [ ] Confirm geo-targeting excludes jurisdictions where the offering is not authorised.
- [ ] Retain copies of all marketing materials and distribution records for supervisory review.

---

## 4. Travel Rule (TFR)

**Transfer of Funds Regulation recast — Regulation (EU) 2023/1113, applicable 30 December 2024**

- [ ] Implement originator and beneficiary information collection for all crypto-asset transfers, regardless of amount (no EUR 1,000 de minimis threshold).
- [ ] Required originator fields: name, account identifier (wallet address), geographic address or national identity number or date/place of birth.
- [ ] Required beneficiary fields: name, account identifier.
- [ ] Transmit TFR data to the beneficiary CASP (or receiving VASP) along with the transfer.
- [ ] Implement a Travel Rule compliance solution (e.g., Notabene, Sygna Bridge, TRISA, or equivalent) that covers both sunrise and post-compliance periods.
- [ ] For transfers to/from unhosted wallets: apply enhanced due diligence for transactions above EUR 1,000; apply FATF Recommendation 16 principles.
- [ ] Retain TFR data for 5 years minimum.
- [ ] Define a policy for transfers where the counterparty CASP/VASP does not support TFR (sunrise problem): block, delay, or accept with enhanced monitoring based on risk appetite and NCA guidance.

---

## 5. Stablecoin Issuance — ART and EMT

**MiCA Title II (ART — Arts. 16–47), Title III (EMT — Arts. 48–58)**

- [ ] Classify the token: Asset-Referenced Token (backed by basket of assets) or E-Money Token (backed by single fiat currency).
- [ ] EMT issuers must hold an e-money institution (EMI) or credit institution licence, or obtain specific MiCA authorisation.
- [ ] Reserves must be held 1:1, in segregated custody with an authorised credit institution or investment firm; no commingling with issuer assets.
- [ ] Reserve composition, redemption procedures, and audit cadence must comply with EBA regulatory technical standards (RTS) published under MiCA.
- [ ] Token holders have a statutory right of redemption at par at any time — ensure redemption flow is implemented and tested.
- [ ] "Significant" ART/EMT designation by EBA triggers additional requirements: interoperability obligations, daily transaction volume caps, mandatory liquidity buffers, and EBA direct supervisory involvement.
- [ ] Check EBA's latest significance lists (published from 2025) to determine if your token is or is likely to become significant.
- [ ] Publish quarterly reserve reports and annual audited financial statements.

---

## 6. Organisational and Governance Requirements

**MiCA Arts. 66–76 (CASPs)**

- [ ] Establish a management body with fit-and-proper members; minimum two independent directors for significant CASPs.
- [ ] Implement written policies for: conflicts of interest, complaints handling, outsourcing, business continuity, and incident reporting.
- [ ] Outsourcing of critical functions requires: written agreement, NCA notification, continued supervisory access, and no degradation of oversight.
- [ ] Maintain a register of all crypto-asset services provided, with client records retained for 5 years post-relationship.
- [ ] Business continuity and disaster recovery plan must be tested annually.
- [ ] Incident reporting: material operational or security incidents must be reported to the NCA within prescribed timeframes (EBA RTS on incident classification applicable).

---

## 7. Custody and Safeguarding

**MiCA Art. 70 (CASPs providing custody)**

- [ ] Client crypto-assets must be held segregated from CASP's own assets; segregation must be enforceable in insolvency.
- [ ] Maintain a register of positions per client, reconciled daily.
- [ ] Liability for loss due to malfunction or hack: CASP bears liability up to market value of the lost asset at the time of loss unless it can demonstrate the loss was caused by an external event beyond its reasonable control.
- [ ] Implement cold/warm/hot wallet tiering appropriate to product risk profile; document security architecture.
- [ ] Conduct an annual penetration test and key management review; retain results for supervisory access.

---

## 8. AML / KYC Integration

**MiCA does not replace AMLD6/AMLD5 obligations; they run in parallel**

- [ ] Confirm existing AML/KYC programme covers CASP customer onboarding under applicable AMLD6 national transposition.
- [ ] KYC must be completed before crypto-asset services are rendered; no grace period for onboarding-in-progress clients.
- [ ] Politically exposed persons (PEPs) and high-risk jurisdictions require enhanced due diligence.
- [ ] Suspicious transaction reporting (STR) obligations apply to all transactions — integrate CASP transaction monitoring with existing AML systems.
- [ ] Travel Rule data feeds must be integrated with the AML screening workflow; TFR data is also AML evidence.

---

## 9. Ongoing Supervisory Obligations

- [ ] Annual report to NCA on: volumes, clients, incidents, and material changes.
- [ ] Notify NCA before any material change to authorised services, senior management, or qualifying shareholders.
- [ ] Maintain a publicly accessible complaints procedure and respond to complaints within prescribed timeframes.
- [ ] Cooperate with NCA inspection requests; retain all required books and records for minimum 5 years.
- [ ] Monitor ESMA and EBA Q&A updates and RTS/ITS publications — MiCA full-application phase since 30 December 2024; verify current secondary legislation status as RTS/ITS packages continue to be adopted.

---

## 10. UK and Third-Country Considerations

- [ ] **UK**: MiCA does not apply in the UK. UK crypto-asset regulation falls under FSMA 2023; the FCA finalized its core cryptoasset regime via a package of policy statements published 30 June 2026 (stablecoin issuance, custody/safeguarding, trading/intermediation, and prudential requirements), with the authorisation gateway opening 30 September 2026 and the regime expected to take effect around 25 October 2027. Cite the current policy statement number for the specific rule area rather than an older consultation/discussion paper, and re-verify the gateway/effective dates as they can move; maintain a separate UK compliance track if serving UK customers.
- [ ] **US (for CASPs/issuers also serving US clients)**: the US GENIUS Act (signed 18 July 2025) creates a separate federal payment-stablecoin framework with a rulemaking deadline of 18 July 2026 — do not assume MiCA compliance satisfies US obligations. The broader US market-structure bill (CLARITY Act) had not been enacted as of mid-2026; verify its current status before relying on it.
- [ ] **Third countries**: passporting under MiCA is limited; serving clients in additional EU member states after initial authorisation may require notification rather than separate authorisation — verify reverse solicitation rules carefully (MiCA Art. 61).
- [ ] **NFTs**: unique non-fungible tokens are provisionally outside MiCA scope (recital 6c); tokens issued in large series that resemble fungible instruments may fall within scope — obtain legal opinion before asserting NFT exemption.
- [ ] **DeFi**: fully decentralised protocols without an identifiable issuer or service provider may be outside CASP scope (recital 22); ESMA guidance on the "sufficiently decentralised" test is expected — do not rely on this exemption without current legal analysis.
