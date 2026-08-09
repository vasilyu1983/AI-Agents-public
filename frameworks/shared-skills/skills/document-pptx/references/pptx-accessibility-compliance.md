# PPTX Accessibility & Compliance - Authoring and Review Workflow

Use this reference when the user mentions accessibility, procurement, regulated distribution, government/enterprise delivery, or exported handouts.

---
## Table of Contents

- [March 2026 Baseline](#march-2026-baseline)
- [What "Accessible Deck" Means in Practice](#what-accessible-deck-means-in-practice)
- [Manual Review Workflow](#manual-review-workflow)
- [1. Run PowerPoint's Accessibility Checker](#1-run-powerpoints-accessibility-checker)
- [2. Check Reading Order](#2-check-reading-order)
- [3. Review Alt Text](#3-review-alt-text)
- [4. Review Delivery Context](#4-review-delivery-context)
- [Library-Specific Guidance](#library-specific-guidance)
- [`PptxGenJS`](#pptxgenjs)
- [`python-pptx`](#python-pptx)
- [`PPTX-Automizer`](#pptx-automizer)
- [Suggested Accessibility QA Checklist](#suggested-accessibility-qa-checklist)
- [Do / Avoid](#do-avoid)
- [Do](#do)
- [Avoid](#avoid)
- [Related Resources](#related-resources)


## July 2026 Baseline

- Microsoft's PowerPoint accessibility guidance is the practical operational baseline for authoring: titles, reading order, contrast, alt text, and built-in checks.
- WCAG 2.2 is a strong best-practice target for decks that will be exported to PDF, published on the web, or reviewed under modern accessibility programs.
- Do **not** treat WCAG 2.2 and EN 301 549 as interchangeable today. The in-force EN 301 549 (v3.2.1, 2021) still cites WCAG 2.1 AA. A revision incorporating WCAG 2.2 AA (provisionally V4.0.0) is in late-stage ETSI/CEN/CENELEC drafting and expected to publish sometime in 2026, followed by Official Journal citation — treat it as pending, not yet the compliance baseline, and re-check before citing a firm date to a client.
- For procurement or regulated-audience decks, confirm which specific standard (and version) the requester actually needs — "accessible" without a named standard usually means the Microsoft baseline plus WCAG 2.2 as best practice, not a formal conformance claim.
- For live delivery, PowerPoint Live / Teams captions can help attendees, but they do not replace accessible slide content.

---

## What "Accessible Deck" Means in Practice

Every deck should have:

- A unique, meaningful title on every slide
- Logical reading order for all visible content
- Meaningful alt text for non-decorative images and charts
- Sufficient contrast and font sizes that hold up on projected screens
- Links with descriptive text instead of raw URLs
- No meaning conveyed by color alone
- A static alternative when motion is important to comprehension

If the deck is exported to PDF, verify the PDF workflow separately with the `document-pdf` skill.

---

## Manual Review Workflow

### 1. Run PowerPoint's Accessibility Checker

- Run the built-in Accessibility Checker before final delivery.
- Fix missing slide titles, missing alt text, and obvious contrast issues first.
- Re-run after final edits, not only after the first draft.

### 2. Check Reading Order

- Use the Selection Pane / reading-order tooling in PowerPoint to verify the screen-reader sequence.
- Charts, icons, captions, and footnotes should follow the same logical order as the spoken presentation.
- Decorative elements should not clutter the reading order.

### 3. Review Alt Text

- Add alt text to images, screenshots, diagrams, and charts that carry meaning.
- Keep it functional: explain why the visual exists, not every pixel.
- Mark purely decorative visuals as decorative where the PowerPoint version supports it.

### 4. Review Delivery Context

- Projected slides need larger text and stronger contrast than laptop-only decks.
- If motion is used, ship a static handout or PDF version as well.
- If the session is live in Teams/PowerPoint Live, enable captions where appropriate.

---

## Library-Specific Guidance

### `PptxGenJS`

- Prefer this when generated shapes need alt text set in code.
- Good fit for browser and Node.js workflows where slides come from structured UI or report data.
- Still run a manual PowerPoint review: code can generate metadata, but only PowerPoint shows the final accessibility result in context.

### `python-pptx`

- Strong for notes, charts, tables, and structural editing.
- Use it for data-heavy pipelines and inspection scripts.
- Plan on a manual PowerPoint pass for accessibility metadata and reading-order verification.

### `PPTX-Automizer`

- Good for designer-owned templates and named-element replacement.
- Accessibility quality depends heavily on the original template and on how invasive the replacements are.
- Re-run accessibility checks after content replacement, especially for charts, screenshots, and reordered slides.

---

## Suggested Accessibility QA Checklist

- [ ] Every slide has a title
- [ ] Reading order is logical on each non-trivial slide
- [ ] Non-decorative images and charts have meaningful alt text
- [ ] Tables are readable and not presented as screenshots when live text is possible
- [ ] Contrast works on projector and laptop displays
- [ ] Hyperlinks use descriptive text
- [ ] Motion-heavy slides have a static fallback
- [ ] Accessibility Checker run completed in the final deck
- [ ] If exporting to PDF, the PDF output is reviewed separately

---

## Do / Avoid

### Do

- Treat accessibility as a release gate, not a cleanup step
- Keep chart labels, axes, units, and timeframe explicit
- Prefer live text over screenshots for key numbers
- Document whether the target is best-practice WCAG 2.2 or an EN 301 549 compliance baseline

### Avoid

- Saying "WCAG 2.2 / EN 301 549" as if they are the same requirement
- Assuming generated slides inherit good reading order automatically
- Using color alone to show status, risk, or trend direction
- Shipping a final deck without running the checker in PowerPoint

---

## Related Resources

- [pptx-speaker-notes-delivery.md](pptx-speaker-notes-delivery.md) - Presenter workflow and notes hygiene
- [pptx-animations-transitions.md](pptx-animations-transitions.md) - Motion, reduced-motion concerns, and static fallback guidance
- [../data/sources.json](../data/sources.json) - Verified links for Microsoft, WCAG, and EU standards context
