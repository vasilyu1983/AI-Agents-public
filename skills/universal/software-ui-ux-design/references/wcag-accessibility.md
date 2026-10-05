# WCAG Accessibility for Design

The WCAG success criteria that change design decisions, plus the legal baselines a design spec must name. WCAG 2.2 is a W3C Recommendation (October 2023) and the default design target.

This file stops at design. Route the rest:

- ARIA patterns, component remediation and code fixes: [software-accessibility](../../software-accessibility/SKILL.md) (full AA checklist in [wcag-2-2-checklist.md](../../software-accessibility/references/wcag-2-2-checklist.md), widget patterns and ARIA contract tests in [remediation-playbook.md](../../software-accessibility/references/remediation-playbook.md))
- Automated and manual accessibility testing, CI gates and screen-reader passes: [qa-testing-accessibility](../../qa-testing-accessibility/SKILL.md)
- WCAG 3.0 status and migration risk: [wcag-2.2-and-3.0-watchlist.md](../../software-accessibility/references/wcag-2.2-and-3.0-watchlist.md)
- Contrast numbers in a spec: compute them with `../scripts/contrast_check.py`, never estimate them

## Table of Contents

- [Principles and Levels](#principles-and-levels)
- [Design-Affecting Success Criteria](#design-affecting-success-criteria)
- [WCAG 2.2 Additions in Design Terms](#wcag-22-additions-in-design-terms)
- [Common Design Mistakes](#common-design-mistakes)
- [Jurisdictional Baselines](#jurisdictional-baselines)
- [Regulatory Context](#regulatory-context)
- [Resources](#resources)

---

## Principles and Levels

WCAG is organised around four principles: content must be **Perceivable**, **Operable**, **Understandable** and **Robust** (POUR). Conformance has three levels: A (minimum), AA (the usual legal and contractual baseline) and AAA (not achievable for all content; use selected AAA criteria as quality targets). Conforming to 2.2 AA also conforms to 2.1 AA and 2.0 AA.

## Design-Affecting Success Criteria

Criteria a designer decides, not just an engineer. Level in brackets.

| Criterion | Design requirement |
|-----------|--------------------|
| 1.1.1 Non-text Content (A) | Every meaningful image, icon and chart has a text alternative written into the spec; decorative images are marked decorative |
| 1.2.x Time-based Media (A/AA) | Captions for video with sound; transcripts for audio; audio description where visuals carry meaning |
| 1.3.1 Info and Relationships (A) | Visual structure (headings, lists, tables, groups) maps to real semantics; annotate heading levels and landmarks in the spec |
| 1.3.4 Orientation (AA) | Do not lock to portrait or landscape unless essential |
| 1.3.5 Identify Input Purpose (AA) | Personal-data fields carry the right `autocomplete` purpose |
| 1.4.1 Use of Color (A) | Colour is never the only signal: pair it with text, icon, pattern or position (errors, status, chart series, links in text) |
| 1.4.3 Contrast Minimum (AA) | Text 4.5:1; large text 3:1 (at least 18 pt / 24 CSS px, or 14 pt / about 18.66 CSS px bold) |
| 1.4.4 Resize Text (AA) and 1.4.10 Reflow (AA) | Layouts survive 200% text zoom and reflow at 320 CSS px width without two-dimensional scrolling (data tables and maps excepted) |
| 1.4.11 Non-text Contrast (AA) | 3:1 for component boundaries needed to identify them, states, focus indicators and meaningful graphics |
| 1.4.12 Text Spacing (AA) | Nothing clips or overlaps when users set line height 1.5×, paragraph spacing 2×, letter spacing 0.12× and word spacing 0.16× the font size |
| 1.4.13 Content on Hover or Focus (AA) | Tooltips and popovers are dismissible (Esc), hoverable and persistent |
| 1.4.6 Contrast Enhanced (AAA) | 7:1 text, 4.5:1 large text; use for long-form reading and low-vision audiences |
| 2.1.1 Keyboard (A) and 2.1.2 No Keyboard Trap (A) | Every interaction has a keyboard path; every layer has a keyboard exit |
| 2.2.1 Timing Adjustable (A) and 2.2.2 Pause, Stop, Hide (A) | Time limits can be extended; auto-moving content (carousels, tickers) can be paused |
| 2.3.1 Three Flashes (A) | Nothing flashes more than three times per second |
| 2.4.1 Bypass Blocks (A) | A way past repeated navigation: a skip link, landmarks or headings (a skip link is not strictly required but is the most robust for keyboard-only users) |
| 2.4.2 Page Titled (A) and 2.4.6 Headings and Labels (AA) | Descriptive page titles, headings and labels in the spec |
| 2.4.3 Focus Order (A) | Focus order follows reading order |
| 2.4.4 Link Purpose (A) | Link text says where it goes; no bare "Click here" |
| 2.4.7 Focus Visible (AA) | A visible focus style is designed for every interactive element; never remove the outline without a replacement |
| 2.5.1 Pointer Gestures (A) and 2.5.4 Motion Actuation (A) | Multi-point, path-based and device-motion gestures have single-pointer, on-screen alternatives |
| 2.5.2 Pointer Cancellation (A) | Actions fire on release, so users can slide off to cancel |
| 2.5.3 Label in Name (A) | The accessible name contains the visible label text |
| 3.1.1 Language of Page (A) | Page language, and language changes within content, are declared |
| 3.2.1 On Focus (A) and 3.2.2 On Input (A) | Focusing or changing a control does not change context unexpectedly (no auto-submitting selects) |
| 3.2.3 Consistent Navigation (AA) and 3.2.4 Consistent Identification (AA) | Navigation keeps its place and order; the same function keeps the same label and icon |
| 3.3.1 Error Identification (A) and 3.3.3 Error Suggestion (AA) | Errors are described in text at the field, with how to fix them |
| 3.3.2 Labels or Instructions (A) | Visible labels and format hints; placeholders are not labels |
| 3.3.4 Error Prevention (AA) | Legal, financial and data submissions are reversible, checked or confirmed |
| 4.1.2 Name, Role, Value (A) and 4.1.3 Status Messages (AA) | Custom controls expose name, role and state; status messages are announced without moving focus |

Form-specific patterns are in [form-design-patterns.md](form-design-patterns.md); motion and reduced-motion rules are in [motion-design.md](motion-design.md).

## WCAG 2.2 Additions in Design Terms

| Criterion | Level | What the design must do |
|-----------|-------|-------------------------|
| 2.4.11 Focus Not Obscured (Minimum) | AA | The focused element is never entirely hidden by sticky headers, footers, cookie banners or chat widgets; reserve scroll padding for them |
| 2.4.13 Focus Appearance | AAA | Focus indicator at least as large as a 2 CSS px perimeter of the component, with 3:1 change of contrast; a good quality target even when AAA is not required |
| 2.5.7 Dragging Movements | AA | Every drag (reorder, slider, kanban move, map pan) has a single-pointer alternative such as buttons, menus or tap-to-place |
| 2.5.8 Target Size (Minimum) | AA | Pointer targets at least 24 × 24 CSS px, or spaced so a 24 px circle around each does not overlap another target; exceptions for inline links, equivalent controls, user-agent controls and essential presentation. Platform guidance (44 × 44 pt on iOS, 48 × 48 dp on Android) is a stronger quality target, not the WCAG minimum |
| 3.2.6 Consistent Help | A | Help mechanisms (contact details, chat, help link) appear in the same relative order across pages |
| 3.3.7 Redundant Entry | A | Do not ask for information the user already gave in the same process; pre-fill it or let them select it |
| 3.3.8 Accessible Authentication (Minimum) | AA | No cognitive function test (remembering, transcribing, solving) unless there is an alternative or assistance: allow paste and password managers (`autocomplete="current-password"`), offer passkeys, magic links or OAuth. Distorted-text CAPTCHAs fail; CAPTCHAs that ask users to recognise objects, or to identify non-text content they supplied, are excepted at AA (but not at AAA 3.3.9) |

WCAG 2.2 also removed 4.1.1 Parsing as obsolete.

## Common Design Mistakes

1. Low contrast on secondary text, placeholder text, disabled-looking but active controls, and text over images.
2. Colour-only status (red/green) in forms, charts and tables.
3. Focus styles removed or invisible against the brand colour; focus hidden under sticky UI.
4. Icon-only buttons with no label in the spec.
5. Targets below 24 × 24 CSS px packed together, especially in toolbars and tables.
6. Placeholder-only labels and errors shown only in a banner at the top.
7. Drag-only interactions with no alternative.
8. Carousels and animations with no pause and no reduced-motion variant.
9. Login flows that block paste or require puzzle CAPTCHAs.
10. Layouts that break at 200% zoom or 320 px width.

---

## Jurisdictional Baselines

WCAG 2.2 (W3C Recommendation, October 2023) is the default design target for new work because conformance also covers WCAG 2.1 and 2.0. It is **not** the binding version in every jurisdiction: EN 301 549 v3.2.1 maps web content to WCAG 2.1 AA and is OJ-cited under the Web Accessibility Directive (EN 301 549 v4.1.1 adopts WCAG 2.2; check whether it has been OJ-cited before relying on it), US ADA Title II specifies WCAG 2.1 AA for state/local government web and mobile apps, and Revised Section 508 incorporates WCAG 2.0 AA. For EAA work, apply Directive 2019/882 and national transposition, and verify an EAA-specific OJ citation or common specification before claiming presumption. WCAG 3.0 is not a shipping target while it is a draft; check its status on the W3C TR page before saying otherwise.

| Requirement | Minimum target | Notes |
|-------------|---------------|-------|
| EU public-sector web/mobile | EN 301 549 v3.2.1 / WCAG 2.1 mapping | OJ-cited route under Directive 2016/2102; verify current citation |
| EU B2C covered by EAA | Directive 2019/882 + national transposition; design to WCAG 2.2 AA | Verify an EAA-specific OJ standard/common specification before claiming presumption; EN 301 549 remains useful test coverage |
| US state/local government | WCAG 2.1 AA | ADA Title II technical standard; verify applicable date and exceptions |
| US federal ICT | WCAG 2.0 AA plus Revised Section 508 requirements | Agency procurement may set a newer target |
| iOS / Android | Platform APIs + applicable legal/contract baseline; design to WCAG 2.2 principles where they map | Native conformance includes platform behavior that web success criteria do not fully express |
| Rich media / APNG / video | WCAG 2.2 AA 1.4.2, 1.4.5, 1.2.x | Captions, audio description, no strobing |

---

## Regulatory Context

This is design guidance, not legal advice. Take the statutory basis for any compliance document from qualified counsel, and verify dates and citations against the primary sources below before quoting them.

### European Accessibility Act (EAA)

- **Applies from** 28 June 2025 to in-scope B2C products and services sold into the EU: websites, mobile apps, e-commerce, banking, e-books, ticketing and transport booking, among others. Microenterprises are exempt for *services* only.
- **Standards route**: Directive 2019/882 and each national transposition set the requirements. EN 301 549 v3.2.1 (WCAG 2.1 AA for web) is cited for the Web Accessibility Directive by Implementing Decision (EU) 2021/1339; that citation does not by itself establish EAA presumption. Treat an EN 301 549 mapping as evidence and design to WCAG 2.2 AA as the forward target.
- **Penalties and enforcement** are set by each member state's transposition; check the national law for the markets you ship to.

Sources: [Directive (EU) 2019/882](https://eur-lex.europa.eu/eli/dir/2019/882/oj/eng), [Commission Implementing Decision (EU) 2021/1339](https://eur-lex.europa.eu/eli/dec_impl/2021/1339/oj/eng), [Interoperable Europe M/587 status](https://interoperable-europe.ec.europa.eu/collection/rolling-plan-ict-standardisation/accessibility-ict-products-and-services-rp-2026), [EN 301 549 V3.2.1](https://www.etsi.org/deliver/etsi_en/301500_301599/301549/).

### ADA (US)

The DOJ's April 2024 ADA Title II rule requires state and local government web content and mobile apps to meet **WCAG 2.1 AA**. An Interim Final Rule published 20 April 2026 extended the compliance dates by one year (to 26 April 2027 for entities serving 50,000 or more people, and 26 April 2028 for smaller entities and special districts). The dates have moved once already, so check the Federal Register before advising. Title III (private businesses) has no DOJ technical standard; courts and settlements commonly reference WCAG 2.x AA.

Source: [Federal Register — Extension of Compliance Dates (2026-07663)](https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web).

### Dark Patterns and Consent Design (EU)

Digital Services Act Article 25 prohibits manipulative interface design on online platforms, but Article 25(2) carves out practices already covered by the GDPR or the Unfair Commercial Practices Directive, so cookie-consent design sits mainly under those regimes and national cookie law. In September 2025 the French CNIL fined Google €325M and SHEIN €150M under French cookie and data-protection law (not the DSA) for cookies placed without valid consent, including after "Refuse all". Design consent with equal visual weight for accept and reject, and honour refusal. See [modern-ux-patterns.md](modern-ux-patterns.md) for the design implications.

---

## Resources

- [WCAG 2.2](https://www.w3.org/TR/WCAG22/), [Understanding WCAG 2.2](https://www.w3.org/WAI/WCAG22/Understanding/), [How to Meet WCAG (Quick Reference)](https://www.w3.org/WAI/WCAG22/quickref/)
- [WAI-ARIA Authoring Practices](https://www.w3.org/WAI/ARIA/apg/)
- [WCAG 3.0 Working Draft](https://www.w3.org/TR/wcag-3.0/) — directional only; see the watchlist linked above
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/), [axe DevTools](https://www.deque.com/axe/devtools/), [WAVE](https://wave.webaim.org/extension/)
- [Inclusive Components](https://inclusive-components.design/), [A11y Project](https://www.a11yproject.com/)
