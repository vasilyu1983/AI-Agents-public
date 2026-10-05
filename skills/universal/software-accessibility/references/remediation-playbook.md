# Remediation Playbook

APG-aligned widget patterns and symptom-keyed remediation scenarios. The implementation rules and verification gate stay in [../SKILL.md](../SKILL.md); APG deviations that break assistive technology are listed in [wcag-2.2-and-3.0-watchlist.md](wcag-2.2-and-3.0-watchlist.md#aria-apg-patterns-reference).

## Contents

- [Common Patterns](#common-patterns)
- [Component ARIA Contract Tests](#component-aria-contract-tests)
- [Scenarios](#scenarios)
  - [S1 — Form audit: missing labels, error association, focus order](#s1--form-audit-missing-labels-error-association-focus-order)
  - [S2 — Modal trap: inert/keyboard escape/focus return](#s2--modal-trap-inertkeyboard-escapefocus-return)
  - [S3 — Color contrast remediation in design tokens](#s3--color-contrast-remediation-in-design-tokens)
  - [S4 — RSC navigation focus loss in Next.js App Router](#s4--rsc-navigation-focus-loss-in-nextjs-app-router)
  - [S5 — Reduced-motion fallback for animation library](#s5--reduced-motion-fallback-for-animation-library)

## Common Patterns

Use APG-aligned implementations. Do not invent new interaction models when a known pattern exists.

| Widget | Required keyboard behavior | ARIA pattern |
|--------|---------------------------|--------------|
| Tabs | Arrow keys switch tabs; Tab moves into panel | `role="tablist"`, `role="tab"`, `aria-selected` |
| Dialog | Tab/Shift+Tab cycles inside; Escape closes | `role="dialog"`, `aria-modal="true"`, `aria-labelledby` |
| Combobox | Arrow keys navigate listbox; Enter selects; Escape closes | `role="combobox"`, `aria-expanded`, `aria-controls` |
| Accordion | Enter/Space toggle panels; optional arrow-key navigation | `role="button"`, `aria-expanded`, `aria-controls` |
| Menu | Arrow keys navigate items; Escape closes; Tab exits | `role="menu"`, `role="menuitem"`, `aria-haspopup` |
| Tree view | Arrow keys navigate; Enter activates; Space selects | `role="tree"`, `role="treeitem"`, `aria-expanded` |

### Native surfaces and library boundaries

- [Native dialog](https://html.spec.whatwg.org/multipage/interactive-elements.html#the-dialog-element): supply an accessible name, a close control and suitable initial focus; test Escape, focus containment and return. Close with `close()`/`requestClose()` rather than removing `open` manually.
- [Popover API](https://html.spec.whatwg.org/multipage/popover.html): use `popover`/`popovertarget` for non-modal transient surfaces and light dismissal. It does not supply a menu's arrow-key model or turn generic content into a modal dialog; choose semantics and focus behavior for the actual interaction.
- [Forced colors](https://drafts.csswg.org/css-color-adjust/#forced-colors-properties): test `@media (forced-colors: active)` with the target OS. Box shadows can disappear; retain an outline/border using system colors such as `Highlight`/`CanvasText`. Avoid blanket `forced-color-adjust: none`, which disables the user's palette.
- [Headless primitives](https://www.radix-ui.com/primitives/docs/overview/accessibility): prefer an existing APG-aligned primitive for a custom widget, then verify the composed names, refs, focus return and keyboard behavior. Styling or `asChild` composition can break the contract; the library name is not evidence of conformance.
- [ISO/IEC 40500](https://www.w3.org/WAI/standards-guidelines/wcag/#isoiec-40500-eaa-en-301-549): read the edition named by the contract and its WCAG mapping. W3C identifies ISO/IEC 40500:2025 as the October 2023 WCAG 2.2 text; do not assume every 40500 citation means WCAG 2.0 or that ISO adoption establishes a jurisdiction's legal baseline.

## Component ARIA Contract Tests

axe catches missing or invalid ARIA but not a component that silently drops its accessible name or modal semantics after a refactor. Pin each shared widget's contract in a unit test next to the axe check, querying by role and accessible name the way assistive tech does:

```typescript
import { render, screen } from '@testing-library/react'
import { axe } from 'jest-axe' // or vitest-axe

it('Modal keeps its dialog contract', async () => {
  const { container } = render(
    <Modal isOpen onClose={() => {}} title="Delete file" description="This cannot be undone." />
  )
  const dialog = screen.getByRole('dialog', { name: 'Delete file' }) // aria-labelledby resolves
  expect(dialog).toHaveAttribute('aria-modal', 'true')
  expect(dialog).toHaveAccessibleDescription('This cannot be undone.') // aria-describedby resolves
  expect(await axe(container)).toHaveNoViolations()
})
```

Write one such test per pattern in the table above (tab `aria-selected`, combobox `aria-expanded`/`aria-controls`, accordion `aria-expanded`), and assert keyboard behaviour with `userEvent`, not only attributes.

## Scenarios

Recipes keyed to symptoms or remediation moments. Each lists the shortest path to resolution.

### S1 — Form audit: missing labels, error association, focus order

1. Run axe-core on the form page; collect all label, error, and focus violations.
2. Replace `placeholder`-only fields with visible `<label for="id">` elements.
3. Associate each error message with its input via `aria-describedby`.
4. Verify tab order matches visual reading order; fix DOM order rather than `tabindex`.
5. Re-run axe-core; confirm zero critical/serious label and error violations remain.
6. Do a keyboard walkthrough end-to-end: Tab, Shift+Tab, Enter, and Escape paths.

### S2 — Modal trap: inert/keyboard escape/focus return

1. Prefer native `<dialog>` opened with `showModal()` for modality: it places the dialog in the top layer and makes the rest of its document inert; `show()` or setting `open` alone does not create modality. Choose initial focus to suit the task, which can be a static heading with `tabindex="-1"` inside the dialog.
2. For a custom dialog, implement background inertness and a focus trap; preserve prior `inert` state on cleanup. Never make an ancestor containing the dialog inert.
3. Verify Tab and Shift+Tab cycle only inside the dialog.
4. Verify Escape closes the dialog and returns focus to the triggering control.
5. Test with VoiceOver and NVDA; confirm modal role and accessible name are announced.

### S3 — Color contrast remediation in design tokens

1. Extract all foreground/background token pairs from the design system.
2. Run each pair through a WCAG 2.2 contrast checker; flag pairs below 4.5:1 (3:1 for large text).
3. Propose adjusted token values that pass AA; confirm with the design team.
4. Update the token file and regenerate CSS; run Lighthouse in CI to catch regressions.
5. Verify author-supplied focus indicators meet 3:1 against adjacent colors under [SC 1.4.11, introduced in WCAG 2.1](https://www.w3.org/TR/WCAG21/#non-text-contrast), alongside SC 2.4.7 Focus Visible. Unmodified user-agent indicators have a contrast exception; WCAG 2.2 SC 2.4.13 is a separate AAA requirement.

### S4 — RSC navigation focus loss in Next.js App Router

1. Reproduce the focus defect on the supported browser/reader matrix. Next.js has a [built-in route announcer](https://nextjs.org/docs/architecture/accessibility) using `document.title`, then `<h1>`, then pathname; give each route a descriptive title and heading before adding announcements.
2. Keep a stable skip-link target on the layout-level `<main>`.
3. Add a client-side focus move only where the reproduced navigation needs it; focus the new heading or main landmark with `tabindex="-1"` after its destination content is ready. Do not steal focus on initial hydration, query updates or intentional in-page navigation.
4. Verify the existing route announcer and focus move together on VoiceOver/Safari and NVDA/Chrome; avoid duplicate announcements.
5. Add an E2E assertion on `document.activeElement` after the affected navigation; axe alone does not test where focus lands.

### S5 — Reduced-motion fallback for animation library

1. Audit all animation calls; identify those lacking a `prefers-reduced-motion` branch.
2. Add `@media (prefers-reduced-motion: reduce)` CSS overrides or check the media query in JS.
3. Replace motion-heavy transitions with instant or fade-only alternatives under reduced-motion.
4. Verify with OS reduced-motion enabled on macOS and Windows; confirm no vestibular-triggering motion.
5. Add a CI check (Playwright with `reducedMotion: 'reduce'` context) to prevent regression.
