---
name: software-accessibility
description: "Implements accessibility fixes in code. Use when remediating semantic HTML, ARIA, focus, keyboard support, or screen-reader behavior."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Accessibility Engineering

This skill owns engineering implementation. It does not own design-side WCAG interpretation or formal accessibility-test programs.

## Quick Reference

| Need | Default | Notes |
|------|---------|-------|
| fix component semantics | semantic HTML first | add ARIA only when HTML is insufficient |
| keyboard support | tab order, visible focus, correct key handling | test manually every time |
| screen reader verification | Primary browser/reader pair for the affected users | add a second platform for shared primitives or cross-platform claims |
| automated coverage | axe-core plus Lighthouse or Pa11y | automation catches markup-level issues, not the full experience |
| modal or composite widget | APG-aligned pattern | do not invent custom keyboard behavior |
| compliance prep | Design/test to WCAG 2.2 AA, then map the applicable legal or procurement baseline | do not describe the design target as the binding version everywhere |
| WCAG 2.2 checklist, axe-core/Pa11y snippets, EU Accessibility Act | [references/wcag-2-2-checklist.md](references/wcag-2-2-checklist.md) | technical mapping only; EAA applicability goes to qualified counsel |
| run axe-core in CI | [scripts/run_axe.sh](scripts/run_axe.sh) | exits non-zero on violations |

## When to Use This Skill

Use this skill when the main work is:

- remediating semantic HTML, labels, roles, and landmarks
- fixing keyboard access, focus management, or SPA route focus behavior
- implementing APG-style component patterns
- improving screen-reader announcements and dynamic content handling
- adding accessibility engineering checks to CI

Route elsewhere when the main work is:

| Need | Use Instead |
|------|-------------|
| design-side accessibility and interaction design | [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md) |
| accessibility test automation program or formal audit flow | [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md) |
| usability research with disabled users | [../software-ux-research/SKILL.md](../software-ux-research/SKILL.md) |
| frontend stack setup and general UI build work | [../software-frontend/SKILL.md](../software-frontend/SKILL.md) |
| platform-specific mobile accessibility behavior | [../software-mobile/SKILL.md](../software-mobile/SKILL.md) |

## Defaults

- semantic HTML before ARIA
- visible focus always on
- keyboard support for every interactive element
- screen-reader checks before calling the fix complete
- automation as baseline, not proof of full accessibility
- current standards and regulatory deadlines are volatile and must be verified before final compliance advice

## Workflow

1. Identify the affected flow, component, and assistive-technology risk.
2. Replace incorrect custom markup with semantic HTML where possible.
3. Add the minimum ARIA state and relationship attributes required for the pattern.
4. Verify keyboard interaction and focus behavior.
5. Verify screen-reader announcements and dynamic updates.
6. Add or update automated checks to prevent regression. For recorded criterion claims, [check_a11y_baseline.py](scripts/check_a11y_baseline.py) rejects unassessed criteria and missing evidence; its template starts unassessed and it checks claim completeness, not conformance.

## Implementation Rules

### Semantic HTML First

Default order:

1. native element
2. minimal ARIA enhancement
3. fully custom widget only when no native pattern exists

Common mistakes to avoid:

- `div` or `span` used as buttons
- focusable elements hidden from assistive tech
- redundant or conflicting `aria-label`
- missing state attributes such as `aria-expanded`
- stripping semantics from interactive elements

### Keyboard and Focus

Every interactive surface must support:

- logical tab order
- visible focus indicator
- escape and arrow-key behavior where the pattern requires it
- focus trap and focus restoration for dialogs
- route-change focus management in SPAs

### Screen Reader Verification

Minimum verification set:

- landmarks and heading structure
- form labels and error association
- role and state announcement for controls
- live-region behavior for dynamic feedback
- meaningful alt text and decorative-image hiding

Choose the assistive-technology matrix from the claim and blast radius:

| Change | Minimum manual evidence |
|---|---|
| Page-specific copy, label, or state fix | One supported browser/reader pair used by the affected audience |
| Shared widget or design-system primitive | One Apple and one Windows/browser pair where the product supports both |
| Mobile-native behavior | The platform reader on a physical target device (VoiceOver or TalkBack) |
| Broad “accessible” or conformance claim | Product support matrix plus disabled-user testing or a qualified audit; automation alone is insufficient |

If a required platform is unavailable, report that cell as unverified. Do not block a narrow source fix merely because an unrelated platform cannot be exercised, and do not generalize the evidence beyond the tested pair.

### Automation and CI

| Layer | Tool | Catches |
|-------|------|---------|
| Authoring | `eslint-plugin-jsx-a11y` (React) or `axe-linter` | Missing labels, wrong roles, bad ARIA usage |
| Development diagnostics | `@axe-core/react` | Logs runtime findings in the development console |
| Component tests | `jest-axe` | Rule checks on the rendered test state |
| E2E / integration | axe-core via Playwright or Cypress | Page-level violations in rendered state |
| CI gate | Lighthouse or Pa11y | Score regression and critical issues |

Automation does not replace keyboard walkthroughs, screen-reader validation, or judgment on content order, announcement quality, and alt-text quality.

A clean scan covers only the rules and rendered states exercised. Report the tool, route/state, violations and manual evidence; it does not establish WCAG conformance.

### When Automation Is Enough vs When a Human Must Check

| Signal type | Automatable | Requires a human pass |
|---|---|---|
| Missing `alt`, label, or landmark | Yes — rule-detectable | — |
| Contrast ratio below threshold | Partial — supported rendered cases | Yes when gradients, images, transparency or incomplete results prevent a reliable computed check |
| `role`/state attribute present but semantically wrong for context | Partial — flags presence, not correctness | Yes — judgment on whether the role fits the interaction |
| Reading order matches visual order | No | Yes — screen-reader walkthrough |
| Live-region announcement is timely and not noisy | No | Yes — screen-reader walkthrough |
| Focus lands somewhere sensible after a route change or async update | No | Yes — keyboard + screen-reader walkthrough |
| Alt text is accurate and non-redundant (not just present) | No | Yes — content review |
| Keyboard operability of a composite widget (arrow keys, Home/End, typeahead) | No | Yes — manual keyboard pass |

Never report an automated scan result (axe-core, Lighthouse, WAVE, Pa11y) as "accessible" or "WCAG conformant" on its own — report it as "N automated violations resolved; manual keyboard and screen-reader verification pending/complete."

## Remediation Prioritization

When a scan or audit returns more issues than can be fixed at once, rank by user impact, not by rule-engine severity label alone:

1. **Blocks a core task entirely** (cannot submit a form, cannot open a required dialog, cannot complete checkout) — fix first regardless of how many instances exist.
2. **Affects a high-traffic or legally sensitive flow** (auth, checkout, account settings, any flow named in a demand letter or audit finding) — fix next.
3. **Widespread pattern-level defect** (e.g., every icon button sitewide is unlabeled) — fix once at the component/design-system level; this clears more violations per hour of engineering time than any single-page fix.
4. **Isolated, low-traffic instances** — batch these; do not let them block a release on their own merits.

Effort-vs-impact check before committing to a large remediation plan: a single shared-component fix (e.g., the button, input, or modal primitive) frequently resolves dozens of scattered violations at once — audit the design system before auditing every page.

## Accessibility Overlay Warning

Do not recommend, and flag if found, third-party "accessibility overlay" scripts as a compliance solution: their marketing promise does not establish that semantics, labeling, keyboard and focus work; require implementation and assistive-technology evidence. If one is installed, fix the underlying markup and demote the overlay to an optional enhancement. Legal evidence and enforcement precedent are owned by [qa-testing-accessibility](../qa-testing-accessibility/references/regulatory-landscape.md#accessibility-overlays-and-legal-exposure).

## Common Patterns

Prefer native `<dialog>.showModal()` for modal surfaces; use Popover API for suitable non-modal surfaces. Test forced colors and composed headless-library contracts; map ISO/IEC 40500 by its cited edition. Implementation conditions, keyboard and ARIA requirements for tabs, dialog, combobox, accordion, menu, and tree view: [references/remediation-playbook.md](references/remediation-playbook.md#common-patterns).

## Known Traps

- Route transitions in SPAs that never move focus to the new page heading or landmark.
- Dialogs that trap focus while open but fail to restore focus to the triggering control on close.
- Toasts and validation messages that update visually but never announce through a correctly scoped live region.
- Screen-reader-hidden containers that still contain focusable descendants.
- Composite widgets that handle arrow keys but forget Home/End, Escape, typeahead, or disabled-item semantics required by the pattern.
- Mobile-only testing that misses desktop screen-reader and keyboard failures.

## Common Anti-Patterns

- Placeholder text used as the only label.
- Click handlers on non-interactive elements without full keyboard and semantic remediation.
- Positive `tabindex` used to force order instead of fixing DOM order.
- `aria-label` added on top of already-correct visible labels, creating redundant or conflicting names.
- `aria-hidden="true"` applied to visible interactive content.
- Custom selects, comboboxes, or menus built from scratch when a native control or established APG pattern would work.

## AI-Generated Accessibility Risks

Pay extra attention to AI-produced code that shows div soup, broken or invented ARIA, missing form labels, skipped heading hierarchy, low-contrast styling, missing or broken focus states, or incomplete keyboard handlers.

## Verification Gate

Do not call the work complete until all of these are checked:

- [ ] Keyboard walkthrough passes for the affected flow (Tab, Shift+Tab, Enter, Escape, arrow keys as required)
- [ ] Visible focus indicator present in all interactive states (never removed with `outline: none` alone)
- [ ] Screen-reader output checked on the risk-based matrix above; tested browser/reader/device pairs and unverified pairs are named
- [ ] Zero critical or serious axe-core violations remain; any suppressed violation has an explicit justification comment
- [ ] Heading levels express the content hierarchy and labels describe purpose; inspect skipped levels in context rather than treating every skip as an automatic WCAG failure; landmarks match intended page regions
- [ ] All form inputs have visible labels bound via `for`/`id` or `aria-labelledby`; errors use `aria-describedby`
- [ ] Task status updates announced briefly where needed; streamed content retains normal semantics and is not wrapped wholesale in a live region
- [ ] Any WCAG or legal-compliance claim is verified against W3C/WAI or official regulatory sources, not memory

- Verify current WCAG, EN 301 549, EAA, browser-support, and tool-maintenance claims before final advice.
- Prefer W3C, WAI, official tool docs, and government or regulator sources.

## Scenarios

Symptom-keyed recipes S1-S5 (form label/error/focus audit, modal focus trap with `inert` and focus return, contrast remediation in design tokens, RSC route-change focus loss, reduced-motion fallback): [references/remediation-playbook.md](references/remediation-playbook.md#scenarios).

## Navigation

**Adjacent skills**

- [../software-ui-ux-design/SKILL.md](../software-ui-ux-design/SKILL.md)
- [../qa-testing-accessibility/SKILL.md](../qa-testing-accessibility/SKILL.md)
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md)
- [../software-mobile/SKILL.md](../software-mobile/SKILL.md)
- [../software-localisation/SKILL.md](../software-localisation/SKILL.md)
- [../qa-testing-playwright/SKILL.md](../qa-testing-playwright/SKILL.md)

**Sources**

- [data/sources.json](data/sources.json)
- [references/remediation-playbook.md](references/remediation-playbook.md) — APG widget patterns and remediation scenarios
- [references/regulatory-traps.md](references/regulatory-traps.md) — conformance mapping traps (EN 301 549, native apps, third-party components, WCAG 2.2 delta) and the overlay warning
- [references/wcag-2.2-and-3.0-watchlist.md](references/wcag-2.2-and-3.0-watchlist.md) — WCAG 2.2 AA baseline, 3.0 draft watchlist, RSC focus gaps, CI coverage map

## Conformance Mapping

- **EU Accessibility Act**: whether it applies to a product is a question for qualified counsel; law, deadlines, exemptions and enforcement live in [qa-testing-accessibility](../qa-testing-accessibility/references/regulatory-landscape.md#european-accessibility-act-eaa). Technical mapping stays here: start from Directive 2019/882 Annex I and the national transposition; EN 301 549 is engineering evidence whose edition, cited directive and WCAG mapping must be looked up (ETSI, Official Journal) rather than named from memory. Target WCAG 2.2 AA for new builds.
- **Native apps, third-party components, WCAG 2.2 delta**: [references/regulatory-traps.md](references/regulatory-traps.md).

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
