# WCAG 2.2 Level AA Automation Matrix

Maps each WCAG 2.2 Level A and AA success criterion to its automation coverage. Use this to plan the split between automated CI gates and manual audit effort, not to claim a fixed automation percentage for conformance.

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
- [Regulatory Reference: EN 301 549](#regulatory-reference-en-301-549)
- [Contrast Ratio: Worked Example](#contrast-ratio-worked-example)

## Principle 1: Perceivable

| Criterion | ID | Automation | Tool | Notes |
|-----------|-----|-----------|------|-------|
| Non-text Content | 1.1.1 | Partial | axe-core | Detects missing alt; human verifies alt quality |
| Audio-only and Video-only (Prerecorded) | 1.2.1 | None | Manual | Verify transcript or audio track equivalent |
| Captions (Prerecorded) | 1.2.2 | Partial | axe-core + manual | axe `video-caption` checks a captions track exists (needs review); accuracy and sync are manual |
| Audio Description or Media Alternative (Prerecorded) | 1.2.3 | None | Manual | Verify audio description or full text alternative |
| Captions (Live) | 1.2.4 | None | Manual | Verify live captions on live streams |
| Audio Description (Prerecorded) | 1.2.5 | None | Manual | Must verify description completeness |
| Info and Relationships | 1.3.1 | Partial | axe-core | Detects missing labels, broken structure; human verifies semantics |
| Meaningful Sequence | 1.3.2 | Partial | axe-core | DOM order checks; human verifies visual-logical match |
| Sensory Characteristics | 1.3.3 | None | Manual | "Click the red button" — context-dependent |
| Orientation | 1.3.4 | Partial | axe-core (experimental) + manual | `css-orientation-lock` is experimental (off by default); test both orientations on mobile |
| Identify Input Purpose | 1.3.5 | Partial | axe-core | Detects missing autocomplete; human verifies correctness |
| Use of Color | 1.4.1 | None | Manual | Must verify color is not sole indicator |
| Audio Control | 1.4.2 | None | Manual | Verify auto-playing audio has pause/stop |
| Contrast (Minimum) | 1.4.3 | Full | axe-core | Automated ratio calculation |
| Resize Text | 1.4.4 | Partial | Manual + browser | Zoom to 200%, verify no loss of content |
| Images of Text | 1.4.5 | None | Manual | No axe rule; review images that contain text |
| Reflow | 1.4.10 | Partial | Manual + browser | Set viewport to 320px width, verify no horizontal scroll |
| Non-text Contrast | 1.4.11 | Partial | axe-core | Some UI component contrast checks; incomplete |
| Text Spacing | 1.4.12 | Partial | axe-core + manual | `avoid-inline-spacing` (tag `wcag21aa`) catches `!important` inline spacing only; apply a text-spacing bookmarklet and check for clipping |
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
| Bypass Blocks | 2.4.1 | Partial | axe-core | axe `bypass` is a needs-review rule (landmark/heading/skip-link heuristic); verify the mechanism works |
| Page Titled | 2.4.2 | Full | axe-core | Detects missing/empty titles |
| Focus Order | 2.4.3 | Partial | axe-core + manual | Tabindex checks automated; logical order is manual |
| Link Purpose (In Context) | 2.4.4 | Partial | axe-core | `link-name` detects links with no accessible name; it does not judge link text such as "click here" |
| Multiple Ways | 2.4.5 | None | Manual | Verify site map, search, or nav alternatives |
| Headings and Labels | 2.4.6 | Partial | axe-core | Detects empty headings; descriptive quality is manual |
| Focus Visible | 2.4.7 | Partial | axe-core | Detects removed outlines; custom styling is manual |
| Focus Not Obscured (Minimum) | 2.4.11 | None | Manual | WCAG 2.2 — verify focused element is not behind sticky headers |
| Pointer Gestures | 2.5.1 | None | Manual | Multipoint/path gestures need a single-pointer alternative |
| Pointer Cancellation | 2.5.2 | None | Manual | Actions fire on up-event or can be aborted/undone |
| Label in Name | 2.5.3 | Partial | axe-core (experimental) + manual | `label-content-name-mismatch` is experimental; voice-control check is manual |
| Motion Actuation | 2.5.4 | None | Manual | Shake/tilt actions need a UI alternative and can be disabled |
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
| Consistent Help | 3.2.6 | None | Manual | WCAG 2.2 (A) — help mechanisms appear in the same relative order across pages |
| Redundant Entry | 3.3.7 | None | Manual | WCAG 2.2 — verify no re-entry of previously provided info |
| Error Identification | 3.3.1 | Partial | axe-core | Detects missing error roles; message quality is manual |
| Labels or Instructions | 3.3.2 | Partial | axe-core | Detects missing labels; instruction quality is manual |
| Error Suggestion | 3.3.3 | None | Manual | Verify helpful error suggestions |
| Error Prevention (Legal, Financial) | 3.3.4 | None | Manual | Verify review/confirm/undo for sensitive actions |
| Accessible Authentication (Minimum) | 3.3.8 | None | Manual | WCAG 2.2 — verify no cognitive function test for auth |

## Principle 4: Robust

| Criterion | ID | Automation | Tool | Notes |
|-----------|-----|-----------|------|-------|
| Parsing | 4.1.1 | n/a | HTML validator | Obsolete and removed in WCAG 2.2 (5 Oct 2023 Recommendation). Still present in WCAG 2.1-based standards (EN 301 549 V3.2.1, Section 508 via WCAG 2.0); valid markup remains a best practice. |
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
| axe-core + IBM Equal Access | A second rule engine; which extra rules it adds varies by release (check IBM's rule list) |
| axe-core + HTML validator | Catches parsing issues (4.1.1) and malformed markup that affects AT |
| axe-core + color contrast analyzer | Specialized tools check gradient backgrounds, text over images, and SVG contrast |

## Planning Manual Audit Effort

Use this table to estimate manual testing time per flow (heuristics):

| Activity | Time per Flow | Frequency |
|----------|---------------|-----------|
| Keyboard navigation walkthrough | 15-30 min | Every release |
| Screen reader flow verification | 30-60 min | Every release (critical flows) |
| Zoom/reflow testing (200% + 400%) | 10-20 min | Every release |
| Color-only information check | 10-15 min | When visual design changes |
| Timing and motion review | 10-15 min | When interactions change |
| Cognitive/reading level review | 15-30 min | When content changes significantly |

**Total estimated manual effort** for a typical 5-flow application: 4-8 hours per release cycle. These times are planning heuristics, not sourced benchmarks; calibrate them against your own audit logs.

## WCAG 2.2 New Criteria (Delta from 2.1)

WCAG 2.2 added nine criteria; these six are Level A/AA (the other three, 2.4.12, 2.4.13 and 3.3.9, are AAA). Source: [What's New in WCAG 2.2](https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/).

| Criterion | ID | Level | Automation | Key Point |
|-----------|-----|-------|-----------|-----------|
| Focus Not Obscured (Minimum) | 2.4.11 | AA | None | Author content must not entirely hide a focused component; check the criterion exceptions |
| Dragging Movements | 2.5.7 | AA | None | Every drag must have a single-pointer alternative |
| Target Size (Minimum) | 2.5.8 | AA | Partial | 24x24 CSS pixels minimum, with exceptions |
| Consistent Help | 3.2.6 | A | None | Help (contact, chat, FAQ link) stays in the same relative order across pages |
| Redundant Entry | 3.3.7 | A | None | Do not ask users to re-enter info already provided |
| Accessible Authentication (Minimum) | 3.3.8 | AA | None | No cognitive function tests (CAPTCHAs that require memory/transcription) |

These are especially important for compliance projects because many existing audit checklists only cover WCAG 2.1.

## Regulatory Reference: EN 301 549

| Version | WCAG Basis | Status |
|---------|-----------|--------|
| V3.2.1 (March 2021) | WCAG 2.1 AA | OJ-cited under the Web Accessibility Directive; remains the reference until the Commission cites a newer version |
| V4.1.1 (September 2026) | WCAG 2.2 AA | Published by ETSI September 2026; Official Journal citation pending (check the Official Journal before relying on it) |

Target WCAG 2.2 AA now: the six A/AA criteria added in 2.2 (2.4.11, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8) are in V4.1.1, so auditing against 2.2 today avoids a re-audit once it is cited. See [regulatory-landscape.md](regulatory-landscape.md) for the EAA/WAD detail.

## Contrast Ratio: Worked Example

1.4.3 (Contrast Minimum) requires **4.5:1** for normal text and **3:1** for large text (≥18pt,
or ≥14pt bold) and for UI component/graphical-object boundaries (1.4.11). The formula, per the
WCAG 2.2 relative luminance definition (WCAG 2.0 printed the threshold as 0.03928; W3C notes the
change to 0.04045 has "no practical effect"):

For each sRGB channel `C` (0-255), normalize `c = C/255`, then:

```
C_lin = c / 12.92                          if c <= 0.04045
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

`#767676` on white is **4.54:1** — passes the 4.5:1 AA threshold for normal text, but only just.
One shade *lighter*, `#777777`, gives **4.48:1** and fails; one shade darker, `#757575`, gives
**4.61:1** and passes. This is why axe-core/Lighthouse flag colors near this boundary for
manual re-verification rather than trusting anti-aliasing or sub-pixel rendering assumptions.

Same method for `#949494` on white gives **3.03:1** — passes the 3:1 large-text/UI-component
threshold but fails 4.5:1, so this gray is only acceptable for large text, bold large text, or
UI component boundaries, never for normal body text.

Do not hand-wave contrast math in an audit report — cite the actual computed ratio (tools report
it directly, e.g. axe-core's `failureSummary`), not just pass/fail, so remediation can target
the smallest color change that clears the threshold.
