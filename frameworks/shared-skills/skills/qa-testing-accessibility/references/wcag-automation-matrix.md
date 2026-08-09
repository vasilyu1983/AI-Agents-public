# WCAG 2.2 Level AA Automation Matrix

Maps each WCAG 2.2 Level AA success criterion to its automation coverage. Use this to plan the split between automated CI gates and manual audit effort, not to claim a fixed automation percentage for conformance.

Legend:
- **Full**: Automation reliably detects all violations.
- **Partial**: Automation flags candidates but human must verify intent or context.
- **None**: Requires manual testing only.

## Table of Contents

- [Principle 1: Perceivable](#principle-1-perceivable)
- [Principle 2: Operable](#principle-2-operable)
- [Principle 3: Understandable](#principle-3-understandable)
- [Principle 4: Robust](#principle-4-robust)
- [Summary](#summary)
- [Recommended Strategy](#recommended-strategy)
- [axe-core Rule Coverage by Principle](#axe-core-rule-coverage-by-principle)
- [Combining Tools for Better Coverage](#combining-tools-for-better-coverage)
- [Planning Manual Audit Effort](#planning-manual-audit-effort)
- [WCAG 2.2 New Criteria (Delta from 2.1)](#wcag-22-new-criteria-delta-from-21)
- [Contrast Ratio: Worked Example](#contrast-ratio-worked-example)

## Principle 1: Perceivable

| Criterion | ID | Automation | Tool | Notes |
|-----------|-----|-----------|------|-------|
| Non-text Content | 1.1.1 | Partial | axe-core | Detects missing alt; human verifies alt quality |
| Captions (Prerecorded) | 1.2.2 | None | Manual | Must verify caption accuracy and sync |
| Audio Description (Prerecorded) | 1.2.5 | None | Manual | Must verify description completeness |
| Info and Relationships | 1.3.1 | Partial | axe-core | Detects missing labels, broken structure; human verifies semantics |
| Meaningful Sequence | 1.3.2 | Partial | axe-core | DOM order checks; human verifies visual-logical match |
| Sensory Characteristics | 1.3.3 | None | Manual | "Click the red button" — context-dependent |
| Orientation | 1.3.4 | None | Manual | Test both orientations on mobile |
| Identify Input Purpose | 1.3.5 | Partial | axe-core | Detects missing autocomplete; human verifies correctness |
| Use of Color | 1.4.1 | None | Manual | Must verify color is not sole indicator |
| Audio Control | 1.4.2 | None | Manual | Verify auto-playing audio has pause/stop |
| Contrast (Minimum) | 1.4.3 | Full | axe-core | Automated ratio calculation |
| Resize Text | 1.4.4 | Partial | Manual + browser | Zoom to 200%, verify no loss of content |
| Images of Text | 1.4.5 | Partial | axe-core | Flags `<img>` with text-like patterns; human verifies |
| Reflow | 1.4.10 | Partial | Manual + browser | Set viewport to 320px width, verify no horizontal scroll |
| Non-text Contrast | 1.4.11 | Partial | axe-core | Some UI component contrast checks; incomplete |
| Text Spacing | 1.4.12 | None | Manual | Apply custom spacing, verify no clipping |
| Content on Hover or Focus | 1.4.13 | None | Manual | Verify tooltips/popovers are dismissible and persistent |

## Principle 2: Operable

| Criterion | ID | Automation | Tool | Notes |
|-----------|-----|-----------|------|-------|
| Keyboard | 2.1.1 | Partial | axe-core + manual | Detects tabindex issues and focus traps; human verifies full operability |
| No Keyboard Trap | 2.1.2 | Partial | axe-core | Detects some traps; manual verification needed |
| Character Key Shortcuts | 2.1.4 | None | Manual | Verify shortcut remapping/disabling |
| Timing Adjustable | 2.2.1 | None | Manual | Verify timeout warnings and extensions |
| Pause, Stop, Hide | 2.2.2 | Partial | axe-core | Detects auto-updating; human verifies controls |
| Three Flashes | 2.3.1 | None | Manual/PEAT | Photosensitive Epilepsy Analysis Tool |
| Bypass Blocks | 2.4.1 | Full | axe-core | Skip navigation link detection |
| Page Titled | 2.4.2 | Full | axe-core | Detects missing/empty titles |
| Focus Order | 2.4.3 | Partial | axe-core + manual | Tabindex checks automated; logical order is manual |
| Link Purpose (In Context) | 2.4.4 | Partial | axe-core | Detects "click here" and empty links; context is manual |
| Multiple Ways | 2.4.5 | None | Manual | Verify site map, search, or nav alternatives |
| Headings and Labels | 2.4.6 | Partial | axe-core | Detects empty headings; descriptive quality is manual |
| Focus Visible | 2.4.7 | Partial | axe-core | Detects removed outlines; custom styling is manual |
| Focus Not Obscured (Minimum) | 2.4.11 | None | Manual | WCAG 2.2 — verify focused element is not behind sticky headers |
| Focus Appearance | 2.4.13 | None | Manual | WCAG 2.2 AAA (included for teams targeting it) |
| Dragging Movements | 2.5.7 | None | Manual | WCAG 2.2 — verify single-pointer alternative |
| Target Size (Minimum) | 2.5.8 | Partial | axe-core | Measures CSS size; spacing context is manual |

## Principle 3: Understandable

| Criterion | ID | Automation | Tool | Notes |
|-----------|-----|-----------|------|-------|
| Language of Page | 3.1.1 | Full | axe-core | Detects missing `lang` attribute |
| Language of Parts | 3.1.2 | Partial | axe-core | Detects missing `lang` on sections; correctness is manual |
| On Focus | 3.2.1 | None | Manual | Verify no unexpected context changes |
| On Input | 3.2.2 | None | Manual | Verify no unexpected context changes on form input |
| Consistent Navigation | 3.2.3 | None | Manual | Compare nav across pages |
| Consistent Identification | 3.2.4 | None | Manual | Verify same function = same label |
| Redundant Entry | 3.3.7 | None | Manual | WCAG 2.2 — verify no re-entry of previously provided info |
| Error Identification | 3.3.1 | Partial | axe-core | Detects missing error roles; message quality is manual |
| Labels or Instructions | 3.3.2 | Partial | axe-core | Detects missing labels; instruction quality is manual |
| Error Suggestion | 3.3.3 | None | Manual | Verify helpful error suggestions |
| Error Prevention (Legal, Financial) | 3.3.4 | None | Manual | Verify review/confirm/undo for sensitive actions |
| Accessible Authentication (Minimum) | 3.3.8 | None | Manual | WCAG 2.2 — verify no cognitive function test for auth |

## Principle 4: Robust

| Criterion | ID | Automation | Tool | Notes |
|-----------|-----|-----------|------|-------|
| Parsing | 4.1.1 | Full | HTML validator | Removed in WCAG 2.2 (December 2024 update). Valid HTML markup remains a best practice for AT compatibility, but 4.1.1 is no longer a normative WCAG 2.2 requirement. |
| Name, Role, Value | 4.1.2 | Partial | axe-core | Detects missing ARIA; custom widget correctness is manual |
| Status Messages | 4.1.3 | Partial | axe-core | Detects missing live regions; announcement quality is manual |

## Summary

This matrix shows a stable pattern rather than a standards-grade percentage:

- a minority of criteria are reliably machine-detectable end to end
- many criteria support candidate detection but still require human verification
- a large set remains manual because usability, context, and assistive-technology behavior cannot be inferred from static rules alone

Use the matrix to decide where automation helps most and where manual review must stay in the release process.

## Recommended Strategy

1. **Automate everything in the "Full" column** — these are cheap, reliable CI gates.
2. **Use automation to triage "Partial" criteria** — flag candidates, then human-verify in manual audit.
3. **Plan dedicated manual audit time for "None" criteria** — these cannot be shortcut.
4. **Prioritize manual effort** on criteria that impact your specific user flows and content types.

## axe-core Rule Coverage by Principle

axe-core exposes broad rule coverage, but exact rule counts change across releases. Use current tool docs for version-specific counts.

| Principle | axe Rules | Coverage Notes |
|-----------|-----------|----------------|
| 1 — Perceivable | ~35 rules | Strong on contrast (1.4.3), alt text detection (1.1.1), form labels (1.3.1). Weaker on resize/reflow and text spacing. |
| 2 — Operable | ~20 rules | Good on bypass blocks (2.4.1), page titles (2.4.2), and tabindex issues. Cannot verify logical focus order or timing. |
| 3 — Understandable | ~15 rules | Good on language attributes (3.1.1) and label presence (3.3.2). Cannot verify content quality or consistency across pages. |
| 4 — Robust | ~10 rules | Good on ARIA validity and name/role/value (4.1.2). Cannot verify custom widget announcement quality. |

## Combining Tools for Better Coverage

No single tool covers all automatable rules. Combine tools strategically:

| Tool Combination | Additional Coverage |
|------------------|---------------------|
| axe-core + Lighthouse | Lighthouse adds tap target checks, crawlable links, and broader performance/SEO context |
| axe-core + IBM Equal Access | IBM adds rules for cognitive accessibility and some ARIA patterns axe misses |
| axe-core + HTML validator | Catches parsing issues (4.1.1) and malformed markup that affects AT |
| axe-core + color contrast analyzer | Specialized tools check gradient backgrounds, text over images, and SVG contrast |

## Planning Manual Audit Effort

Use this table to estimate manual testing time per flow:

| Activity | Time per Flow | Frequency |
|----------|---------------|-----------|
| Keyboard navigation walkthrough | 15-30 min | Every release |
| Screen reader flow verification | 30-60 min | Every release (critical flows) |
| Zoom/reflow testing (200% + 400%) | 10-20 min | Every release |
| Color-only information check | 10-15 min | When visual design changes |
| Timing and motion review | 10-15 min | When interactions change |
| Cognitive/reading level review | 15-30 min | When content changes significantly |

**Total estimated manual effort** for a typical 5-flow application: 4-8 hours per release cycle.

## WCAG 2.2 New Criteria (Delta from 2.1)

These criteria were added in WCAG 2.2 and are often missed in audits:

| Criterion | ID | Level | Automation | Key Point |
|-----------|-----|-------|-----------|-----------|
| Focus Not Obscured (Minimum) | 2.4.11 | AA | None | Sticky headers/footers must not hide focused elements |
| Dragging Movements | 2.5.7 | AA | None | Every drag must have a single-pointer alternative |
| Target Size (Minimum) | 2.5.8 | AA | Partial | 24x24 CSS pixels minimum, with exceptions |
| Redundant Entry | 3.3.7 | A | None | Do not ask users to re-enter info already provided |
| Accessible Authentication (Minimum) | 3.3.8 | AA | None | No cognitive function tests (CAPTCHAs that require memory/transcription) |

These are especially important for compliance projects because many existing audit checklists only cover WCAG 2.1.

## Regulatory Reference: EN 301 549

| Version | WCAG Basis | Status |
|---------|-----------|--------|
| V3.2.1 (March 2021) | WCAG 2.1 AA | Current harmonized standard for EAA and WAD |
| V4.1.1 (expected 2026) | WCAG 2.2 AA | Draft in progress at ETSI; not yet published as of June 2026 |

Until V4.1.1 is published, EN 301 549 V3.2.1 (WCAG 2.1 basis) is the normative harmonized standard for the European Accessibility Act. In practice, target WCAG 2.2 AA now — the five criteria added in 2.2 that are not in 2.1 (2.4.11, 2.5.7, 2.5.8, 3.3.7, 3.3.8) are required by EAA once V4.1.1 is adopted. Auditing against 2.2 today avoids a re-audit gap when V4.1.1 publishes. A public-review draft (v4.1.0) was released November 2025; V4.1.1 publication in the Official Journal of the EU is expected around October 2026 (unverified as of 2026-07-11 — treat as a forecast, EU/ETSI publication timelines have slipped before).

## Contrast Ratio: Worked Example

1.4.3 (Contrast Minimum) requires **4.5:1** for normal text and **3:1** for large text (≥18pt,
or ≥14pt bold) and for UI component/graphical-object boundaries (1.4.11). The formula, per the
WCAG relative luminance definition:

For each sRGB channel `C` (0-255), normalize `c = C/255`, then:

```
C_lin = c / 12.92                          if c <= 0.03928
C_lin = ((c + 0.055) / 1.055) ^ 2.4         otherwise

L = 0.2126*R_lin + 0.7152*G_lin + 0.0722*B_lin

Contrast ratio = (L_lighter + 0.05) / (L_darker + 0.05)
```

Worked digit-by-digit for `#767676` (a commonly-cited "just passes AA" gray) on white:

- `c = 118/255 = 0.462745`
- `(0.462745 + 0.055) / 1.055 = 0.490762`
- `0.490762 ^ 2.4 = 0.181164` → this is `R_lin = G_lin = B_lin` (gray, so all channels equal)
- `L = 0.181164` (since the three luminance weights sum to 1.0 and all channels are equal)
- White `L = 1.0`
- Ratio = `(1.0 + 0.05) / (0.181164 + 0.05) = 1.05 / 0.231164 = 4.542`

`#767676` on white is **4.54:1** — passes the 4.5:1 AA threshold for normal text, but only just;
one shade darker fails. This is why axe-core/Lighthouse flag colors near this boundary for
manual re-verification rather than trusting anti-aliasing or sub-pixel rendering assumptions.

Same method for `#949494` on white gives **3.03:1** — passes the 3:1 large-text/UI-component
threshold but fails 4.5:1, so this gray is only acceptable for large text, bold large text, or
UI component boundaries, never for normal body text.

Do not hand-wave contrast math in an audit report — cite the actual computed ratio (tools report
it directly, e.g. axe-core's `failureSummary`), not just pass/fail, so remediation can target
the smallest color change that clears the threshold.
