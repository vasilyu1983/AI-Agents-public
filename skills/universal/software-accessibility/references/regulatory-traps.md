# Conformance Mapping Traps and Overlay Warning

Technical conformance mapping for accessibility work: which WCAG level and standard edition to build and test against, and what engineering evidence to keep. Legal scope, deadlines, exemptions, enforcement and overlay evidence live in [qa-testing-accessibility regulatory landscape](../../qa-testing-accessibility/references/regulatory-landscape.md); this skill does not restate them. Standard editions and citations change: verify against W3C/WAI, the Official Journal, or ETSI before quoting.

## Contents

- [Technical Mapping](#technical-mapping)
- [Engineering Traps](#engineering-traps)
- [Accessibility Overlay Warning](#accessibility-overlay-warning)

## Technical Mapping

- **Design target:** WCAG 2.2 AA for new builds. Do not describe it as the binding version everywhere; the legal baseline differs by jurisdiction (see the landscape reference for the current per-jurisdiction standard).
- **EU Accessibility Act (Directive 2019/882):** whether it applies to a product or service is a question for qualified counsel, not an engineering call. Once scope is confirmed, start the technical work from the Directive's Annex I requirements and the national transposition. EN 301 549 is useful engineering evidence and maps web content to a specific WCAG version per edition; look up the edition currently cited in the Official Journal, for which directive, and its WCAG mapping before naming one. A citation under the Web Accessibility Directive does not by itself give EAA presumption of conformity.
- **Native mobile apps:** for services confirmed in scope, test the app against the Directive and national requirements. EN 301 549 Chapter 11 gives engineering coverage beyond web WCAG, but do not call it the binding route unless the applicable citation or national rule says so.
- **WCAG 2.2 delta from 2.1:** nine new success criteria (2.4.11, 2.4.12, 2.4.13, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8, 3.3.9) and 4.1.1 Parsing removed. Audit existing products against them before 2.1-only remediation is treated as complete; criteria table in [wcag-2-2-checklist.md](wcag-2-2-checklist.md) and [wcag-2.2-and-3.0-watchlist.md](wcag-2.2-and-3.0-watchlist.md).

## Engineering Traps

- **Third-party components inherit risk:** a UI library or SDK that fails WCAG 2.2 AA makes the product fail; audit vendor components and request accessibility conformance reports (ACRs / VPATs), then verify them.
- **Evidence over claims:** a conformance claim needs automated findings, manual review and assistive-technology testing on the affected journeys; hand the evidence structure to `qa-testing-accessibility`.

## Accessibility Overlay Warning

Do not recommend, and flag if found, third-party "accessibility overlay" or "widget" scripts (injected toolbars that claim to auto-remediate a site) as a compliance solution. An overlay promise does not establish that semantics, labels, keyboard access and focus work; fix and test the underlying implementation. If a client already has one installed, do not build on top of it: fix the markup and remove it or demote it to an optional enhancement (text resize, contrast toggle). Legal exposure, the FTC order and litigation-statistics caveats: [landscape reference](../../qa-testing-accessibility/references/regulatory-landscape.md#accessibility-overlays-and-legal-exposure).
