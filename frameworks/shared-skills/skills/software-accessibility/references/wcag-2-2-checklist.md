# WCAG 2.2 Production Checklist

## Table of Contents

- [New in WCAG 2.2](#new-in-wcag-22)
- [High-Failure Criteria (AA)](#high-failure-criteria-aa)
- [Automation Runners](#automation-runners)
- [EU Accessibility Act Applicability](#eu-accessibility-act-applicability)
- [Production Traps](#production-traps)

---

## New in WCAG 2.2

Nine new success criteria added over WCAG 2.1 (W3C Recommendation October 2023):

| SC | Level | Name | Common Failure |
|----|-------|------|----------------|
| 2.4.11 | AA | Focus Not Obscured (Minimum) | Sticky header/footer covers focused element |
| 2.4.12 | AAA | Focus Not Obscured (Enhanced) | Fully hidden by persistent overlay |
| 2.4.13 | AAA | Focus Appearance | Focus ring too thin or low-contrast |
| 2.5.3 | A | Label in Name | Button label ≠ accessible name |
| 2.5.7 | AA | Dragging Movements | Drag-only interactions with no single-pointer alternative |
| 2.5.8 | AA | Target Size (Minimum) | Touch targets < 24×24 CSS px |
| 3.2.6 | A | Consistent Help | Help link moves between pages |
| 3.3.7 | A | Redundant Entry | Form re-asks already-provided info |
| 3.3.8 | AA | Accessible Authentication (Minimum) | Cognitive test required to log in |
| 3.3.9 | AAA | Accessible Authentication (Enhanced) | Any object recognition required |

Note: 4.1.1 Parsing was **removed** in WCAG 2.2 — remove from compliance checklists.

---

## High-Failure Criteria (AA)

Highest automated or manual failure rates in current audits:

- **1.1.1** Missing or empty `alt` on informative images
- **1.3.1** Form inputs lack programmatic labels (`<label>`, `aria-label`, `aria-labelledby`)
- **1.4.3** Text contrast < 4.5:1 (normal), < 3:1 (large)
- **1.4.11** Non-text contrast — icon/input borders < 3:1 against background
- **2.4.7** Focus visible — invisible outline on links/buttons
- **4.1.3** Status messages not exposed via `role="status"` or `aria-live`

---

## Automation Runners

### axe-core/cli

```bash
# Install once
npm install -g @axe-core/cli

# Run against a live URL
axe https://example.com --exit

# Save report
axe https://example.com --save report.json

# Run only WCAG 2.2 AA rules
axe https://example.com --tags wcag2a,wcag2aa,wcag22aa --exit
```

axe-core detects ~57% of WCAG issues automatically (Deque research; verify current figure).

### Pa11y

```bash
npm install -g pa11y

# Standard run
pa11y https://example.com

# WCAG 2.2 AA standard
pa11y --standard WCAG2AA https://example.com

# CI threshold: fail on any error
pa11y --threshold 0 https://example.com
```

### Lighthouse CLI

```bash
npm install -g lighthouse

# Accessibility audit only
lighthouse https://example.com \
  --only-categories=accessibility \
  --output=json \
  --output-path=./lh-report.json \
  --chrome-flags="--headless"

# Assert score threshold (jq)
score=$(jq '.categories.accessibility.score' lh-report.json)
python3 -c "exit(0 if $score >= 0.90 else 1)"
```

Lighthouse scores are 0–1 (multiply by 100 for percentage).

---

## EU Accessibility Act Applicability

The European Accessibility Act (EAA) Directive 2019/882 entered force **28 June 2025** for new products and services.

**Applies if:**
- You sell or provide digital products/services (e-commerce, banking, transport ticketing, e-books, e-readers, telephony) **within the EU**
- Your company has ≥ 10 employees **or** > €2 M annual turnover
- Service is offered to consumers (B2B-only is partially exempt)

**Microenterprise exemption:** < 10 employees AND ≤ €2 M turnover — exempt from EAA service obligations but check national transposition.

**Technical standard:** EN 301 549 v3.2.1, which maps to WCAG 2.1 AA as the web baseline. WCAG 2.2 AA is strongly recommended as it supersedes 2.1 for new builds.

**Enforcement:** National market-surveillance authorities in each EU member state. UK has its own PSBAR (Public Sector Bodies Accessibility Regulations) and follows WCAG 2.1 AA for public-sector sites.

**Decision checklist:**
1. Is the product/service a covered category under Annex I of Directive 2019/882? → Yes: EAA applies.
2. Is the entity a microenterprise? → If yes: EAA service obligations waived; products still covered.
3. Is the product placed on the EU market after 28 June 2025? → Yes: must comply at launch.
4. Existing services have until **28 June 2030** to achieve conformance.

---

## Production Traps

- **Sticky headers and 2.4.11:** CSS `scroll-margin-top` prevents most failures but is often forgotten for SPAs with client-side routing.
- **axe-core rule changes (verify current version):** `aria-allowed-role` ruleset tightened — `<div role="button">` without `tabindex` now errors.
- **Target size 2.5.8:** CSS `padding` counts toward target size; rendered size in DevTools must be ≥ 24×24. Check with `getComputedStyle`.
- **Accessible Authentication 3.3.8:** Image-based CAPTCHAs are a direct failure; use hCaptcha's audio alternative or Cloudflare Turnstile (no-challenge mode).
- **Lighthouse CI (verify current version):** recent releases deprecated the `--quiet` flag; update CI scripts.
