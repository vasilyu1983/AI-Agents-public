# Accessibility Regulatory Landscape

Which standard applies, by what date, and what evidence a compliance-relevant audit must produce. Dates and legal status move; re-verify against the primary source before putting any of this in a compliance plan. This is testing guidance, not legal advice.

## Table of Contents

- [WCAG Versions](#wcag-versions)
- [ADA Title II and Title III (US)](#ada-title-ii-and-title-iii-us)
- [Section 508 (US Federal)](#section-508-us-federal)
- [EN 301 549 (EU)](#en-301-549-eu)
- [European Accessibility Act (EAA)](#european-accessibility-act-eaa)
- [UK (PSBAR and Equality Act)](#uk-psbar-and-equality-act)
- [Accessibility Overlays and Legal Exposure](#accessibility-overlays-and-legal-exposure)

## WCAG Versions

**WCAG 2.2** has been a W3C Recommendation since 5 October 2023 (updated edition 12 December 2024). It added nine success criteria, six of them at Level A/AA: 2.4.11, 2.5.7, 2.5.8, 3.2.6 (Consistent Help, Level A), 3.3.7 and 3.3.8. 4.1.1 Parsing is obsolete and was removed in the 2023 Recommendation (not in the 2024 edition). Target WCAG 2.2 AA by default: it covers the 2.1 AA that most regulations below cite, except 4.1.1, which is still part of WCAG 2.0/2.1 and so still part of any 2.1-based legal test. Source: [What's New in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/).

**WCAG 3.0** is a W3C Working Draft (the 10 September 2026 draft; check [w3.org/TR/wcag-3.0](https://www.w3.org/TR/wcag-3.0/) for a newer one). Candidate Recommendation and Recommendation dates are not fixed (check the W3C WCAG 3 page for the current timeline). It uses an outcomes-based conformance model rather than 2.2's binary pass/fail, and it will not replace 2.2 in regulation for years. Track it; do not gate against a draft.

## ADA Title II and Title III (US)

Do not cite the original 2024 dates without the 2026 extension:

- The DOJ final rule (24 April 2024) set **WCAG 2.1 Level AA** as the technical standard for state and local government web content and mobile apps.
- The original compliance dates were 24 April 2026 (population 50,000+) and 24 April 2027 (under 50,000, and special district governments).
- A DOJ Interim Final Rule, effective 20 April 2026, **extended both dates by one year**, to 26 April 2027 and 26 April 2028. Comments closed 22 June 2026 ([Federal Register 2026-07663](https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web)); treat the new dates as current but not necessarily final.
- **Title III** (private businesses and public accommodations) has no DOJ rule setting a technical standard or deadline. Courts apply Title III to websites case by case, and WCAG 2.1/2.2 AA is the de facto standard in settlements. Do not tell a private-sector client they have an "ADA deadline" in the Title II sense.

## Section 508 (US Federal)

The binding technical standard is still **WCAG 2.0 Level AA** (2017 refresh); it has not been updated to reference 2.1 or 2.2 ([section508.gov](https://www.section508.gov/)). Target 2.2 AA as forward cover, but do not claim 2.2 is the current legal Section 508 baseline. Many federal agencies target 2.1 or 2.2 AA as policy; read the specific agency's procurement language rather than assuming 2.0 AA is the ceiling.

## EN 301 549 (EU)

| Version | WCAG basis | Status |
|---------|-----------|--------|
| V3.2.1 (March 2021) | WCAG 2.1 AA | OJ-cited under the Web Accessibility Directive (WAD); remains the current reference standard |
| V4.1.1 (September 2026) | WCAG 2.2 AA | Published by ETSI in September 2026; not yet cited in the Official Journal |

AccessibleEU (7 Sept 2026) says V4.1.1 is "not yet the legal reference standard for demonstrating compliance with the EAA or the WAD" and that until the Commission cites it, "the current reference remains EN 301 549 v3.2.1". Whether and how V3.2.1 gives presumption of conformity under the EAA depends on the Commission's citation decisions — verify before asserting either way. A citation that gives presumption under the Web Accessibility Directive (2016/2102) does not by itself cover the EAA: Commission request M/587 asks the standards bodies to revise standards in support of the EAA, so claim EAA presumption only after verifying an EAA-specific Official Journal citation or common specification for the requirement. The technical mapping from EN 301 549 to WCAG lives in [software-accessibility](../../software-accessibility/references/regulatory-traps.md). Audit against WCAG 2.2 AA now so a V4.1.1 citation does not force a re-audit.

Sources: [ETSI EN 301 549 V4.1.1 PDF](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/04.01.01_60/en_301549v040101p.pdf), [AccessibleEU news, 2026-09-07](https://accessible-eu-centre.ec.europa.eu/content-corner/news/european-accessibility-standard-en-301-549-has-been-updated-2026-09-07_en). axe-core tags rules `EN-301-549` (V3.2.1) and `EN-301-549v4` (V4.1.1) if you need a standard-specific rule list.

## European Accessibility Act (EAA)

Directive (EU) 2019/882 ([EUR-Lex](https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019L0882)):

- **Application date:** Member States apply their national measures from **28 June 2025** (Art. 31). Enforcement is active, not theoretical, and varies by national market-surveillance authority.
- **Transition (Art. 32) is narrow, not a blanket grace period for "existing services":**
  - Service providers may continue to provide services *using products they lawfully used before 28 June 2025* until 28 June 2030.
  - Service contracts agreed before 28 June 2025 may continue unaltered until they expire, but no longer than five years from that date.
  - Member States *may* let self-service terminals already in use continue until the end of their economically useful life, up to 20 years.
- **Microenterprise exemption:** microenterprises *providing services* (fewer than 10 persons and turnover or balance sheet ≤ EUR 2 million) are exempt from the accessibility requirements (Art. 4(5)). Microenterprises that make or sell in-scope *products* are not exempt.
- **Scope is a question for qualified counsel.** Whether the EAA applies to a given product or service is a legal determination: identify a covered category under Art. 2 plus the national implementation (e-commerce, consumer banking, electronic communications, transport ticketing, e-books and reader software, audiovisual media player controls, consumer operating systems and hardware). Do not treat every consumer-facing digital product or streaming service as covered, and record the entity facts (size, turnover, provision date) the answer relied on. Engineering teams should not self-certify scope.
- **Microenterprise definition:** read Art. 3(23) for the definition (including the turnover or balance-sheet alternative) and Art. 4(5) for the service exemption; do not apply the service exemption to a product manufacturer because it is small.
- **Separate product and service duties:** manufacturer conformity and technical documentation duties (Art. 7, Annex IV) differ from service-provider information duties (Art. 13, Annex V). Verify each against national implementation; a universal accessibility statement with a remediation timeline is not established here, so do not invent that duty.
- **Enforcement varies by member state:** look up the competent authority, remedies and penalties in the national implementing law; do not quote a fine cap or infer procedure from another country. Disability-rights organisations can also litigate.
- **Evidence duty:** service providers must publish information per Annex V explaining how the service meets the accessibility requirements, in an accessible format, and keep it for as long as the service runs (Art. 13(2)). Treat the accessibility statement as an audit deliverable.
- Native mobile apps for in-scope services (e-commerce, banking, e-books, transport ticketing, and similar) are in scope; EN 301 549 clause 11 applies WCAG to software via [WCAG2ICT](https://www.w3.org/TR/wcag2ict-22/).

## UK (PSBAR and Equality Act)

UK public sector bodies are under the Public Sector Bodies (Websites and Mobile Applications) Accessibility Regulations 2018 (PSBAR), which set the standard by reference; look up the WCAG version the regulation and current GOV.UK guidance name before quoting one. Private-sector digital services fall under Equality Act 2010 reasonable-adjustment duties. The UK did not transpose the EAA, so UK and EU obligations diverge; a product serving both markets needs each answered separately.

## Accessibility Overlays and Legal Exposure

"Overlay" or "widget" products (one injected script that claims to auto-remediate a site) are not a substitute for code-level remediation:

- UsableNet's 2025 mid-year report found 22.6% of H1 2025 US web-accessibility lawsuit filings targeted sites with an overlay installed. That share has no denominator (how many sites run overlays), so it does not show a higher lawsuit rate or causation; quote it as a count, not a risk multiplier.
- The FTC's order against accessiBe ($1,000,000; final order approved April 2025) addressed misleading or unsubstantiated claims that the product made sites WCAG/ADA compliant. The Decision and Order was issued 21 April 2025 and announced 22 April; it is a marketing-claims consent order, not a technical conformance test, and should not be generalised to every overlay ([FTC press release](https://www.ftc.gov/news-events/news/press-releases/2025/04/ftc-approves-final-order-requiring-accessibe-pay-1-million)).
- Overlays can interfere with users' own assistive technology and cannot fix missing semantics, reading order, or incorrect ARIA in the underlying markup.
- Require evidence (code-level checks plus assistive-technology testing) for any claimed compliance result.
- If a product already has an overlay, record it as an open risk item in the audit, not as a control, and plan remediation plus removal or demotion to an optional enhancement (text resize, contrast toggle).
