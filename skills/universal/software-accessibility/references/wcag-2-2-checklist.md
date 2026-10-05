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
| 2.5.7 | AA | Dragging Movements | Drag-only interactions with no single-pointer alternative |
| 2.5.8 | AA | Target Size (Minimum) | Touch targets < 24×24 CSS px |
| 3.2.6 | A | Consistent Help | Help link moves between pages |
| 3.3.7 | A | Redundant Entry | Form re-asks already-provided info |
| 3.3.8 | AA | Accessible Authentication (Minimum) | Cognitive test required to log in |
| 3.3.9 | AAA | Accessible Authentication (Enhanced) | Any object recognition required |

Note: 4.1.1 Parsing was **removed** in WCAG 2.2 — remove from compliance checklists.

---

## High-Failure Criteria (AA)

Check these frequent engineering failure patterns; this is not a ranked prevalence study:

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

# Run the full WCAG 2.2 A/AA rule set. axe tags each rule with exactly one
# version/level tags; include the 2.1-era tags (wcag21a/wcag21aa) too.
axe https://example.com --tags wcag2a,wcag2aa,wcag21a,wcag21aa,wcag22aa --exit
```

Automation coverage depends on the tested rules and rendered states; do not infer conformance from a clean scan.

### Pa11y

```bash
npm install -g pa11y

# Standard run
pa11y https://example.com

# HTML_CodeSniffer WCAG2AA profile; not a complete WCAG 2.2 AA check
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

Whether the EAA (Directive 2019/882) applies to a product or service is a question for qualified counsel; scope, exemptions, transition and enforcement are covered in the [regulatory landscape](../../qa-testing-accessibility/references/regulatory-landscape.md#european-accessibility-act-eaa). Give counsel the entity facts and the product category; do not self-certify.

**Technical mapping (this skill):** Apply Directive 2019/882 Annex I and the relevant national transposition. EN 301 549 v3.2.1 maps web content to WCAG 2.1 AA, but its current OJ citation is for the Web Accessibility Directive, not proof of EAA presumption. Later editions may change both the WCAG mapping and the directive coverage; look up which edition is currently cited in the Official Journal before naming one. Verify the EAA-specific OJ citation or common specification at sign-off; design and test new work to WCAG 2.2 AA.

---

## Production Traps

- **Sticky headers and 2.4.11:** CSS `scroll-margin-top` prevents most failures but is often forgotten for SPAs with client-side routing.
- **Target size 2.5.8:** CSS `padding` counts toward target size; measure the rendered target and check the criterion's spacing, equivalent-control, inline, user-agent and essential exceptions before flagging a failure.
- **Accessible Authentication 3.3.8:** Distorted-text CAPTCHAs fail, because typing transcribed characters is a cognitive function test. Object-recognition CAPTCHAs (e.g. "select all traffic lights") are excepted at AA but fail AAA 3.3.9. An audio CAPTCHA that the user must transcribe does not satisfy the Alternative exception. Prefer allowing paste and password managers, passkeys/WebAuthn, magic links, or a non-interactive bot check.
