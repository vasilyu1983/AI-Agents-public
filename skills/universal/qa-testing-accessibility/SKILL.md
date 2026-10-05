---
name: qa-testing-accessibility
description: "Builds accessibility testing for WCAG 2.2 audits, CI gates, mobile audits, and EAA/ADA/VPAT evidence. Use when adding axe-core, Lighthouse, or screen-reader tests; not fixes."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# QA Testing (Accessibility)

Accessibility testing automation, CI gating, and audit methodology for web and mobile: what to automate, what needs manual testing, and how to keep a sustainable gate. This skill covers *testing* and conformance evidence; `software-ui-ux-design` covers accessible design and `software-accessibility` covers implementing fixes.

## Workflow

1. Gather the target surfaces, WCAG scope, and platform constraints.
2. Cover what automation can reliably detect first.
3. Add manual keyboard and screen-reader checks for critical journeys.
4. Turn findings into CI gates, remediation work, and verification evidence.

## Inputs to Gather

- Target WCAG level: AA (default) or AAA (specific requirements)
- Platforms: web, iOS, Android, or combination
- Assistive technology requirements: screen readers, switch access, voice control
- Existing accessibility tooling and baseline violation count
- Regulatory requirements: ADA Title II, Section 508, EN 301 549, EAA — see `## Regulatory Landscape`; do not assume any single deadline applies to a private US business
- Critical user flows that must be accessible
- Design system or component library status (tested vs untested)

## WCAG 2.2 Automation Boundary

Automation covers only a subset of WCAG 2.2. The exact share varies by product, framework, and tool rule set, so do not treat any percentage as a conformance rule.

| Coverage Type | Examples |
|---------------|----------|
| Reliably automatable | Missing alt attributes, missing form labels, many ARIA validity checks; candidate contrast, heading and landmark findings still need scope review |
| Candidate detection + human verification | Alt-text quality, keyboard usability, touch target adequacy, focus order, live-region behavior |
| Manual only | Cognitive load, reading level, error-prevention UX, consistent navigation, timing adjustments, motion preferences, full screen-reader usability, reflow at high zoom |

Read [references/wcag-automation-matrix.md](references/wcag-automation-matrix.md) when you need criterion-level automation planning beyond the table above.

## Canonical axe tag set

Use this array everywhere axe-core runs (Playwright, Cypress, jest-axe, Storybook, the baseline script):

```ts
['wcag2a', 'wcag2aa', 'wcag21a', 'wcag21aa', 'wcag22aa']   // WCAG 2.2 Level A + AA
// optional: add 'best-practice', and report those results as non-WCAG
```

Why all five: axe gives each rule exactly one version/level tag, the WCAG version that *introduced* its criterion ([axe-core API: tags](https://github.com/dequelabs/axe-core/blob/develop/doc/API.md#axe-core-tags)). `wcag2aa` means "WCAG 2.0 AA rules", not "all AA rules". `['wcag2a','wcag2aa','wcag22aa']` silently skips the 2.1 rules — for example `autocomplete-valid` (1.3.5) and `avoid-inline-spacing` (1.4.12) — so a gate stays green against a WCAG 2.1 AA legal standard it never tested. Check the installed axe rule metadata for default-enabled and experimental rules; `runOnly` tag selection changes which rules run. No tag set equals conformance.

Tools for a second rule engine: Lighthouse (axe-based, weighted score), Pa11y (`runners: ["axe","htmlcs"]`), IBM Equal Access; WAVE for manual review. See [references/automated-auditing.md](references/automated-auditing.md).

## Conformance Boundary

Automated scans and tool severity labels do not establish WCAG conformance; they are implementation guidance. A conformance claim needs combined evidence: automated findings, manual review, and assistive-technology testing on the relevant journeys.

## Accessibility Overlays: Do Not Recommend

Overlay/widget products (one injected script that claims to auto-remediate) do not confer conformance and add legal exposure: the FTC ordered accessiBe to pay for unsubstantiated compliance claims. Read the cited report before quoting litigation figures; a share of filings does not establish a higher lawsuit rate among overlay users. Record an installed overlay as an open risk, not a control, and plan remediation plus removal. Evidence: [references/regulatory-landscape.md](references/regulatory-landscape.md#accessibility-overlays-and-legal-exposure).

## Prioritizing Fixes: User Impact, Not Violation Count

Violation *count* is a weak signal for triage. Rank by: (1) **absolute barrier vs. workaround** — a missing label on the only checkout submit button outranks fifty redundant footer roles; (2) **flow centrality** — sign-in, checkout, account recovery, and anything users cannot route around; (3) **breadth** — a shared component or layout template defect hits every consuming page. Two critical violations on a conversion path outrank 200 minor ones; do not let count-sorted dashboards drive the backlog.

## Design-System Leverage

Fix shared components (Button, Modal, Form Field, Tabs, Combobox) first: one fix remediates every consuming page. Audit core interactive components against their ARIA APG pattern, fix, then re-scan pages — many page-level findings collapse. Component-level tests (Storybook a11y with `parameters.a11y.test = 'error'`, `jest-axe`) stop regressions in these primitives.

## Web Testing Patterns

- **Component tests**: axe-core via `@axe-core/playwright`, `cypress-axe`, or Storybook `a11y` addon.
- **E2E tests**: inject `@axe-core/playwright` into page-level assertions after navigation.
- **Lighthouse CI**: the category score is weighted and can pass a serious failure; block on named audits, track the score as a trend.
- **States**: axe skips hidden regions. Open menus, dialogs, error states, and themes, then re-scan; re-scan after SPA route changes.
- **`incomplete` results** are needs-review items: route to manual review, never block on them or count them as passes.

Read [references/automated-auditing.md](references/automated-auditing.md) when wiring axe-core, Lighthouse, or Pa11y into component or CI tests.

## Mobile Testing Patterns

- **iOS**: `XCUIApplication.performAccessibilityAudit(for:_:)` in UI tests (Xcode 15+, iOS 17+), Accessibility Inspector for exploratory audits, VoiceOver manual protocol. `accessibilityIdentifier` is a test hook VoiceOver never reads, so identifier lookups are not accessibility checks.
- **Android**: Compose `composeTestRule.enableAccessibilityChecks()` (Compose 1.8.0+, `ui-test-junit4-accessibility`), Espresso `AccessibilityChecks.enable()`, Accessibility Scanner, TalkBack manual protocol.
- Map WCAG to native apps with W3C WCAG2ICT.

Read [references/mobile-accessibility.md](references/mobile-accessibility.md) when scoping iOS or Android accessibility test workflows.

## CI Integration

| Stage | What to Run | Gate |
|-------|-------------|------|
| PR (component) | axe-core on changed components | Use team policy; common starter is block critical/serious |
| PR (E2E) | axe-core on smoke flows | Use team policy; common starter is block critical/serious |
| Staging deploy | Full-page Lighthouse + axe scan | Common starter: block critical, warn serious/moderate |
| Release | Manual audit of critical flows + screen reader verification | Sign-off required |

Baseline management: for existing codebases, snapshot current violations and gate only on *new* ones. Compare per-node fingerprints (rule + page + target), not per-rule node counts: with a count diff, one fixed node hides one new node of the same rule. See [references/ci-accessibility-gates.md](references/ci-accessibility-gates.md).

Close a finding against the criterion, assistive-technology/browser setup, viewport/device, and user task that exposed it. Preserve the failing evidence, retest the repaired component or flow, then check adjacent focus, announcements, keyboard order, zoom/reflow, and error recovery as applicable. A clean automated rerun proves only the rules executed on the scanned state; record which manual, expert, or real-user tier remains untested.

## Three Tiers of Testing: Automated, Manual Expert, Real AT Users

Each tier catches defects the others miss — none is a substitute for the others on a
compliance-relevant or high-traffic critical flow:

| Tier | Who | Catches | Misses |
|------|-----|---------|--------|
| Automated | CI (axe-core, Lighthouse, jsx-a11y) | Structural/programmatic defects reliably, with repeatable coverage of the scanned states | Anything requiring judgment about meaning, sufficiency, or usability |
| Manual expert | Sighted engineer/QA running keyboard + screen-reader protocol | Flow-level defects, focus management, ARIA correctness in context | Real-world friction — expert testers know the workarounds a first-time AT user does not |
| Real AT users | Actual disabled users, their own devices/AT/versions/speed | Highest-fidelity signal — muscle-memory shortcuts, unfamiliar error recovery, device-specific quirks | Coverage depends on recruited users and tested tasks; combine with structural checks |

Automated plus in-house expert is necessary but not sufficient for a critical or regulated flow. Before a compliance-relevant release (EAA, ADA Title II, VPAT/ACR sign-off) or a core-flow redesign, run at least one round with actual AT users (research panels, disability ERGs, screen-reader-using customers), paid as research participants. Vendor names and panel pricing change — verify before budgeting.

## Screen Reader Testing Protocol

Test critical flows with at least one screen reader per target platform:

| Platform | Screen Reader | When |
|----------|---------------|------|
| macOS/iOS | VoiceOver | Default for Apple targets |
| Windows | NVDA (free); add JAWS for enterprise/US-heavy audiences | Default for Windows web |
| Android | TalkBack | Default for Android targets |

What to verify: landmark announcements, heading navigation, form label association, error announcements, dynamic content updates (live regions), modal/dialog focus management, custom widget interaction.

Test NVDA and JAWS both for enterprise or US-heavy audiences: JAWS still leads primary desktop use in North America (WebAIM Screen Reader Survey #10; check webaim.org for a newer survey before quoting shares).

Read [references/screen-reader-testing.md](references/screen-reader-testing.md) when running VoiceOver, NVDA, JAWS, or TalkBack verification.

## Keyboard Navigation Testing

Tab order, visible focus, skip link, modal focus trap and return, and APG keyboard patterns for custom widgets. See [references/keyboard-navigation.md](references/keyboard-navigation.md).

## Quick Reference

| What to Test | Tool / Method | CI Stage | Automation |
|--------------|---------------|----------|------------|
| Color contrast | axe-core + manual for unsupported states/backgrounds | PR + release | Partial |
| Missing alt text | axe-core | PR gate | Full |
| Form labels | axe-core | PR gate | Full |
| Heading hierarchy | axe-core + manual structure review | PR + release | Partial |
| ARIA validity | axe-core | PR gate | Full |
| Keyboard navigation | axe-core + manual | PR + release | Partial |
| Touch target size | axe-core + manual | PR + release | Partial |
| Screen reader flow | Manual (VoiceOver/NVDA/TalkBack) | Release | Manual |
| Cognitive load | Manual review | Release | Manual |
| Reflow at 400% zoom | Manual browser test | Release | Manual |

## Regulatory Landscape

Summary; details, sources and caveats in [references/regulatory-landscape.md](references/regulatory-landscape.md):

- **WCAG 2.2 AA** is the default target. It added six A/AA criteria over 2.1 (2.4.11, 2.5.7, 2.5.8, 3.2.6, 3.3.7, 3.3.8); 4.1.1 was removed in the 5 Oct 2023 Recommendation. Check the W3C publication status before discussing WCAG 3.0; use a published Recommendation for conformance gates.
- **ADA Title II**: WCAG 2.1 AA; the 2026 Interim Final Rule moved the dates to 26 Apr 2027 (50k+) and 26 Apr 2028. **Title III** has no DOJ technical standard or deadline.
- **Section 508**: still WCAG 2.0 AA.
- **EN 301 549**: read the applicable Official Journal citation and its directive scope before asserting presumption of conformity; publication alone does not make a newer edition the harmonised reference.
- **EAA**: applies from 28 Jun 2025; whether it covers a given product is a question for qualified counsel. The Art. 32 transition covers products already in use and pre-existing contracts, not "existing services" in general; microenterprises providing services are exempt; an Annex V accessibility statement is required.

## Do / Avoid

### Do

- Start with axe-core as the default cross-framework scanner
- Treat CI severity thresholds as team policy, not as a WCAG verdict
- Test with real assistive technology for critical flows, including sessions with actual
  disabled AT users before a compliance-relevant or core-flow release
- Fix shared design-system components first — highest leverage per hour spent
- Include accessibility in definition of done
- Use ARIA Authoring Practices Guide (APG) for custom component keyboard patterns
- Combine multiple automated tools for broader rule coverage
- Prioritize by user impact (blocker vs. workaround, flow centrality) over raw violation count

### Avoid

- Treating automated scanning as complete coverage or as proof of WCAG conformance
- Recommending or shipping an accessibility overlay/widget as a substitute for code-level
  remediation — it does not confer conformance
- Blocking all PRs on all existing violations (use baselines)
- Using only one automated tool without manual testing
- Testing accessibility only before release (shift left)
- Sorting remediation backlogs by violation count alone instead of user impact
- Blocking CI on axe `incomplete` results, or disabling `color-contrast` globally to silence noise
- Gating on the Lighthouse accessibility score alone
- Writing VPAT/ACR "Supports" from automated results without manual and AT evidence

## Navigation

- `## Workflow` and `## WCAG 2.2 Automation Boundary` for the baseline sequence
- `## Resources` and `## Templates` for deeper materials
- `## Related Skills` for cross-platform handoffs

## Resources

| Resource | Purpose |
|----------|---------|
| [references/automated-auditing.md](references/automated-auditing.md) | axe-core, Lighthouse, Pa11y integration and configuration |
| [references/screen-reader-testing.md](references/screen-reader-testing.md) | VoiceOver, NVDA, TalkBack testing protocols |
| [references/wcag-automation-matrix.md](references/wcag-automation-matrix.md) | WCAG 2.2 AA criteria mapped to automation coverage |
| [references/ci-accessibility-gates.md](references/ci-accessibility-gates.md) | CI gate design, baselines, and severity mapping |
| [references/cognitive-accessibility.md](references/cognitive-accessibility.md) | WCAG 2.2 cognitive criteria (3.2.6, 3.3.7, 3.3.8), reading-level checks, COGA guidance |
| [references/eslint-jsx-a11y-integration.md](references/eslint-jsx-a11y-integration.md) | eslint-plugin-jsx-a11y wiring, custom rule set, CI gate with --max-warnings=0 |
| [references/mobile-accessibility.md](references/mobile-accessibility.md) | iOS `performAccessibilityAudit`, Compose/Espresso checks, VoiceOver/TalkBack protocols |
| [references/regulatory-landscape.md](references/regulatory-landscape.md) | WCAG versions, ADA, Section 508, EN 301 549, EAA, overlay evidence |
| [references/keyboard-navigation.md](references/keyboard-navigation.md) | Keyboard testing and ARIA APG patterns |
| [data/sources.json](data/sources.json) | Curated external sources |

## Scripts

| Script | Purpose |
|--------|---------|
| [scripts/generate-a11y-baseline.ts](scripts/generate-a11y-baseline.ts) | Playwright + axe-core baseline generator; rejects malformed configuration and unsuccessful navigation before replacing the baseline — run with `npx tsx scripts/generate-a11y-baseline.ts` |
| [scripts/test_baseline_regressions.py](scripts/test_baseline_regressions.py) | Offline mocked regressions; run with Node 24+ available: `python3 scripts/test_baseline_regressions.py` |
| [scripts/README.md](scripts/README.md) | Setup and usage guide for all scripts |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-accessibility-audit.md](assets/template-accessibility-audit.md) | Accessibility audit scope, findings, and remediation plan |
| [assets/template-accessibility-ci-config.md](assets/template-accessibility-ci-config.md) | Example CI configurations for axe-core and Lighthouse gates |
| [assets/template-screen-reader-checklist.md](assets/template-screen-reader-checklist.md) | Per-flow screen reader testing checklist |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-accessibility](../software-accessibility/SKILL.md) | Implementing accessibility fixes in code |
| [software-ui-ux-design](../software-ui-ux-design/SKILL.md) | Accessible design and WCAG 2.2 design patterns |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Risk-based test strategy and coverage planning |
| [qa-testing-playwright](../qa-testing-playwright/SKILL.md) | E2E web testing with accessibility assertions |
| [qa-testing-android](../qa-testing-android/SKILL.md) | Android accessibility checks with Espresso |
| [qa-testing-ios](../qa-testing-ios/SKILL.md) | iOS accessibility testing with XCTest |
| [qa-testing-mobile](../qa-testing-mobile/SKILL.md) | Cross-platform mobile accessibility |
| [software-frontend](../software-frontend/SKILL.md) | Frontend development and semantic HTML |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
