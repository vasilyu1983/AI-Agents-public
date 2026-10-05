# Regulatory Context: UK, EU & US Dark-Pattern and Nudge Law

Read before shipping a pattern that touches pricing disclosure, defaults, cancellation flow, or AI-agent choice architecture in a regulated market. Not legal advice — qualified counsel determines the governing instrument for a specific practice.

## UK

Dark patterns may violate:
- **ASA CAP Code** (misleading advertising, false urgency)
- **CMA Consumer Markets Investigation** (subscription traps, fake reviews)
- **DMCC Act 2024, ss. 226–228** — misleading actions (s.226), misleading omissions (s.227), aggressive practices (s.228), plus the Sch. 20 list of practices banned outright. In force **6 April 2025**. These *replaced* the Consumer Protection from Unfair Trading Regulations 2008, revoked on that date by DMCC s.251(1) (commenced by SI 2025/272) — cite the DMCC, not the CPRs. The CMA can impose fines of up to **10% of global annual turnover** by direct civil enforcement, without a court order.
  - **Enforcement history**: on **18 November 2025** the CMA opened investigations into **8 businesses** it suspected of infringing (StubHub, viagogo, AA Driving School, BSM, Gold's Gym, Wayfair, Appliances Direct, Marks Electrical) — these were investigations *opened*, not infringement decisions.
  - The **first DMCC civil penalty** was **AA/BSM driving schools, 15 April 2026**: £4.2m (reduced from £7m for a 40% early-settlement discount), plus more than £760k in refunds to more than 80,000 customers, for drip pricing of a mandatory booking fee (GOV.UK press release). Do not cite a specific fee amount — none is named in the primary source.
  - **Marks Electrical** was the second penalty, **18 June 2026**: £720,000 (after a 40% reduction from £1.2m), plus about £600,000 in refunds to nearly 40,000 customers, for automatic opt-ins to paid add-on services.
  - Verification trap: legislation.gov.uk's page for SI 2008/1277 may still show no revocation banner because the revised-text pipeline lags commencement — check the *revoking* instrument, not the revoked one.
- **ICO GDPR guidance** (deceptive consent patterns count as invalid consent)

## EU

**DSA Article 25**: assess applicable online-platform scope, including the micro/small-enterprise exemption and the Article 25(2) carve-out for practices covered by UCPD or GDPR. It does not extend to every EU-facing product, and is not confined to Very Large Online Platforms. See the [Commission DSA Q&A](https://digital-strategy.ec.europa.eu/en/faqs/digital-services-act-questions-and-answers) and [Regulation (EU) 2022/2065](https://eur-lex.europa.eu/eli/reg/2022/2065/oj/eng/pdf).

**EU AI Act manipulation review (Article 5(1)(a))**: requires the relevant technique, impaired informed decision-making, material behavioural distortion, and actual or reasonably likely significant harm — not every nudge or dark pattern meets those conditions. Assess territorial scope and current text with qualified counsel; prohibitions apply separately from the high-risk schedules. Check the [official timeline](https://ai-act-service-desk.ec.europa.eu/en/ai-act/timeline/timeline-implementation-eu-ai-act) for current application dates: GPAI rules applied from 2 August 2025, and the Omnibus moved the Annex III high-risk dates, so read the timeline rather than a cached date. The [official Article 5 explorer](https://ai-act-service-desk.ec.europa.eu/en/ai-act/article-5) warns its displayed text is not yet updated — retrieve current amended law before a legal conclusion.

**EU digital fairness policy**: do not treat future initiatives as adopted law or forecast enactment dates. Check the [Commission consumer-law review](https://commission.europa.eu/law/law-topic/consumer-protection-law/review-eu-consumer-law_en) for the Digital Fairness Act's current status; treat it as a proposal until it is published in the Official Journal. Being outside one provision does not establish that a practice is lawful elsewhere.

**EDPB Guidelines 03/2022** on deceptive design patterns (v2.0, adopted 14 Feb 2023) is the most usable EU taxonomy for a dark-pattern or sludge audit: six categories — Overloading, Skipping, Stirring, Obstructing, Fickle, Left in the Dark. (https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en)

**DMA Art. 13(4) and 13(6)** ban circumvention "by behavioural techniques or interface design" and non-neutral choice presentation — relevant only to gatekeepers or products that depend on a gatekeeper's choice screen.

## US

Dark patterns are actionable under **FTC Act §5** (unfair or deceptive acts) and **ROSCA**. Landmark enforcement: **FTC v. Amazon**, settled 25 September 2025 — $2.5B total ($1.0B civil penalty + $1.5B in consumer refunds to ~35M Prime subscribers) over deceptive Prime enrollment and cancellation flows.

**Click-to-cancel status**: the rule (cancellation as easy as sign-up) was vacated by the Eighth Circuit in July 2025 on procedural (notice-and-comment) grounds, not on the merits. The FTC sent a reviving ANPRM to OIRA on 30 January 2026, and it was published for comment on **13 March 2026** with a 30-day comment window (closed 13 April 2026). Check the FTC rule page for any later NPRM or final rule. **Treat click-to-cancel as a live enforcement expectation regardless of the rule's procedural status** — the FTC continues to charge the same conduct under §5/ROSCA. Live example: **FTC v. Uber** (amended complaint 15 December 2025, joined by 21 states plus DC) alleges UberOne enrollment without consent and a cancellation path requiring up to 32 actions across 23 screens.

Roughly 30 US states also maintain their own automatic-renewal statutes, so a compliant federal posture alone is not sufficient.

## Sources

CMA 18 Nov 2025 investigations — https://www.gov.uk/government/news/cma-launches-major-consumer-protection-drive-focused-on-online-pricing-practices · AA/BSM penalty — https://www.gov.uk/government/news/cma-orders-the-aa-and-bsm-driving-schools-to-refund-learner-drivers-over-drip-pricing · Marks Electrical penalty — https://www.gov.uk/government/news/cma-orders-marks-electrical-to-refund-customers-over-pre-selected-extra-charges · FTC v. Amazon — https://www.ftc.gov/news-events/news/press-releases/2025/09/ftc-secures-historic-25-billion-settlement-against-amazon · EDPB 03/2022 — https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032022-deceptive-design-patterns-social-media_en.
