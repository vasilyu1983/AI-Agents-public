# WCAG 2.2 AA and 3.0 Watchlist

## Table of Contents

- [WCAG 2.2 AA — Current Baseline](#wcag-22-aa--current-baseline)
- [WCAG 3.0 Draft Watchlist](#wcag-30-draft-watchlist)
- [EU Accessibility Act — Technical Mapping](#eu-accessibility-act--technical-mapping)
- [ARIA APG Patterns Reference](#aria-apg-patterns-reference)
- [React 19 RSC Focus-Management Gaps](#react-19-rsc-focus-management-gaps)
- [CI and Automation Coverage Map](#ci-and-automation-coverage-map)

---

## WCAG 2.2 AA — Current Baseline

Use WCAG 2.2 AA as this skill's design/test target; look up the W3C status page before claiming a latest standard. Do not call it the legal baseline without mapping the jurisdiction: EN 301 549 v3.2.1 maps web content to WCAG 2.1 AA and is OJ-cited under the Web Accessibility Directive, Revised Section 508 incorporates WCAG 2.0 AA, and US ADA Title II specifies WCAG 2.1 AA for state/local government web and mobile apps. Verify the legislation-specific citation at sign-off.

### New Success Criteria in 2.2 (relative to 2.1)

| SC | Level | Name | What changed |
|----|-------|------|--------------|
| 2.4.11 | AA | Focus Not Obscured (Minimum) | Focused component must not be entirely hidden by sticky headers, overlays, or cookie banners |
| 2.4.12 | AAA | Focus Not Obscured (Enhanced) | No part of the focused component may be hidden |
| 2.4.13 | AAA | Focus Appearance | Focus indicator must meet minimum size and contrast: 2px perimeter of the focused UI component, 3:1 contrast ratio against unfocused state (this is an AAA-only criterion — AA conformance only requires the weaker 2.4.7 Focus Visible plus 1.4.11 Non-text Contrast for the focus indicator; do not tell a client 2.4.13 is required for AA) |
| 2.5.3 | A (retained) | Label in Name | Accessible name must contain the visible label text |
| 2.5.7 | AA | Dragging Movements | Any pointer-drag operation must have a single-pointer alternative |
| 2.5.8 | AA | Target Size (Minimum) | Touch targets must be at least 24x24 CSS pixels (or have adequate spacing) |
| 3.2.6 | A | Consistent Help | Help mechanisms appearing on multiple pages must appear in the same relative order |
| 3.3.7 | A | Redundant Entry | Users are not asked to re-enter information already provided in the same session |
| 3.3.8 | AA | Accessible Authentication (Minimum) | Cognitive function tests (typing transcribed text, puzzles) must not be required unless an alternative is provided |
| 3.3.9 | AAA | Accessible Authentication (Enhanced) | Cognitive test requires a non-cognitive alternative or assistance mechanism; object/personal-content recognition exceptions from AA do not apply |

### Removed in WCAG 2.2

- **4.1.1 Parsing** was removed. Browsers now handle malformed HTML consistently. Do not cite it in new audits.

### Full AA Criteria Most Commonly Missed in Practice

| Criterion | Common failure mode |
|-----------|---------------------|
| 1.1.1 Non-text Content | Decorative images missing `alt=""`, icon buttons missing label |
| 1.3.1 Info and Relationships | Table data in `div` grid without ARIA roles |
| 1.4.3 Contrast (Minimum) | Placeholder text, disabled state text, secondary labels |
| 1.4.4 Resize Text | Content breaks or overlaps at 200% zoom |
| 1.4.10 Reflow | Horizontal scroll introduced at 320px viewport |
| 1.4.11 Non-text Contrast | Form border, icon, focus ring fail 3:1 against background |
| 2.1.1 Keyboard | Drag-and-drop, date pickers, custom select without keyboard alternative |
| 2.4.3 Focus Order | Logical DOM order broken by `tabindex` manipulation or CSS `order` |
| 2.4.6 Headings and Labels | No heading structure, or generic "Click here" link text |
| 2.5.8 Target Size | Mobile tap targets under 24x24 px |
| 4.1.2 Name, Role, Value | Custom widgets missing `role`, `aria-label`, or state attributes |
| 4.1.3 Status Messages | Toast and error messages shown visually but not in a live region |

---

## WCAG 3.0 Draft Watchlist

WCAG 3.0 is an AGWG Working Draft, not a Recommendation, and W3C does not expect it to become a completed standard for several years; WCAG 2.x will not be deprecated when 3.0 ships. **Do not cite 3.0 as a compliance target for any current engagement.** The draft has been reorganized more than once, so before quoting any 3.0 structure, requirement name, count, or date, read the current draft at w3.org/TR/wcag-3.0/ and the status page at w3.org/WAI/standards-guidelines/wcag/wcag3-intro/.

### Key Structural Differences from 2.x

| Area | WCAG 2.x approach | WCAG 3.0 direction |
|------|-------------------|-------------------|
| Conformance model | Binary pass/fail per page | Tiered reporting model; check the current draft for which tier means conformance and do not equate a named tier such as Bronze with conformance |
| Success criteria | Testable yes/no criteria | "Guidelines" with associated tests and scoring rubrics |
| User needs scope | Covers disability categories broadly | Explicitly organized by user needs and functional categories |
| Cognitive accessibility | Limited; COGA task force separate | Integrated more deeply into core guidelines |
| Adaptive components | Not addressed directly | Includes guidelines for personalization and adaptable content |

### Areas to Watch

Track these areas in the current draft rather than relying on any summary here: clear language (no readability-formula target should be assumed), image alternatives beyond `alt`, and how focus appearance is specified for keyboard and pointer users.

### Migration Risk

Teams building to 2.2 AA now should expect 3.0 conformance to require:

1. Additional cognitive-load review (plain language, error prevention, instructions).
2. Outcome-based re-testing against user need scenarios, not just page-by-page SC checks.
3. Tooling updates — current automated tools (axe, Lighthouse) have limited 3.0 coverage.

---

## EU Accessibility Act — Technical Mapping

Whether the European Accessibility Act (EAA, Directive 2019/882) applies to a product or service is a question for qualified counsel. Scope (covered sectors), dates, transition, exemptions and enforcement are owned by the [regulatory landscape](../../qa-testing-accessibility/references/regulatory-landscape.md#european-accessibility-act-eaa). This section keeps only the technical conformance mapping.

### Technical Standard: EN 301 549

- EN 301 549 v3.2.1 maps web content to **WCAG 2.1 AA** and its OJ citation supports the Web Accessibility Directive (Directive 2016/2102). Later editions may change the WCAG mapping and add EAA coverage; check which edition is currently cited in the Official Journal, and for which directive, before naming a version in a compliance document.
- For EAA work, start from Directive 2019/882 and national transposition. M/587 requests standards supporting the EAA; verify an EAA-specific OJ citation or common specification before claiming presumption of conformity. Use WCAG 2.2 AA as a forward design target, not as proof of the EAA legal route.

### Practical Implications for Engineering Teams

- EN 301 549/WCAG mappings are engineering evidence unless the verified EAA conformity route gives them legal effect.
- Testing with AT (screen readers, switch access) must be evidenced, not just automated reports.
- Checkout and banking flows are highest-risk areas; mobile apps serving those flows need the same test coverage.

---

## ARIA APG Patterns Reference

The WAI ARIA Authoring Practices Guide (APG) at `www.w3.org/WAI/ARIA/apg/patterns/` is the canonical source for keyboard interaction and ARIA role assignments for composite widgets.

### Patterns Engineers Must Follow Exactly

| Pattern | Key behaviors | Common deviation that breaks AT |
|---------|--------------|----------------------------------|
| Dialog (Modal) | Focus traps inside dialog; Escape closes; focus returns to trigger on close | Missing focus trap; focus returns to body instead of trigger |
| Combobox | `aria-expanded`, `aria-controls`, `aria-activedescendant`; ArrowDown opens list | Role set on wrapper div not on input; `aria-activedescendant` points to wrong element |
| Tabs | `role="tablist"`, `role="tab"`, `role="tabpanel"`; arrow keys move between tabs | Tab key used to move between tabs (should be arrows); `aria-selected` missing |
| Accordion | `aria-expanded` on button; button controls `id`-linked panel | `aria-expanded` on div, not button; heading wraps entire panel |
| Menu / Menu Button | `role="menu"`, `role="menuitem"`; arrow keys navigate; Escape closes and returns focus | Arrow keys missing; space/enter behavior incorrect for `menuitemcheckbox` |
| Listbox | `role="listbox"`, `role="option"`; `aria-selected` per option; `aria-activedescendant` | Single vs multi-select `aria-multiselectable` missing; keyboard selection not announced |
| Tree View | `role="tree"`, `role="treeitem"`; ArrowRight expands; ArrowLeft collapses | ArrowLeft does not collapse or move to parent node |
| Breadcrumb | `<nav aria-label="Breadcrumb">`; `aria-current="page"` on last item | `aria-current` missing; nav landmark missing |

### Anti-Pattern: Inventing Keyboard Behaviors

Do not invent keyboard interactions that deviate from APG unless there is a documented, tested reason. Users of AT rely on consistent patterns. Deviations create relearning costs and often break announcements.

---

## React 19 RSC Focus-Management Gaps

React Server Components (RSC) introduce patterns that break focus management and dynamic announcements in ways not present in client-only React.

### Gap 1 — Server-Rendered Route Transitions

In RSC-based routing (Next.js App Router and similar), a navigation event triggers a server fetch and partial hydration. The browser does not perform a full page load, so the default browser behavior of moving focus to the top of the document does not occur.

**Failure mode:** focus stays on the navigation element (or is lost) after route change; screen-reader users do not hear the new page's heading or title.

**Fix:** check Next.js's built-in route announcer and route title/heading first; add a focus move only for a reproduced navigation defect after the destination is ready. See [S4](remediation-playbook.md#s4--rsc-navigation-focus-loss-in-nextjs-app-router) for the verification conditions.

### Gap 2 — Streaming Suspense Boundaries

When a `<Suspense>` boundary streams in content, the DOM is updated without a user gesture or announced live region.

**Failure mode:** content appears visually but AT users do not hear an announcement.

**Fix:** keep streamed content in its normal semantic structure. If completion changes a task status, update a separate, already-mounted `role="status"` region with a short message such as "Results loaded"; do not make the whole streamed section live. Reserve alerts for urgent messages and test that feedback is not repetitive. [W3C status-message guidance](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html) warns against overly chatty feedback.

### Gap 3 — Client Component Islands and Focus Traps

In RSC architecture, interactive components are `"use client"` islands. A dialog or combobox rendered as a client island may not have access to the full focus trap context if it is nested inside a server-rendered shell.

**Failure mode:** focus escapes the dialog island into server-rendered content that has no interactive elements, leaving the user stranded.

**Fix:** focus traps must be implemented inside the client component boundary. Use a library such as `focus-trap-react` or a custom hook scoped to the island's root ref.

### Gap 4 — Missing Skip-Links in App Router Layouts

In traditional SPA routing, skip-link targets are stable DOM nodes. In RSC layouts, the `<main>` element may be re-rendered or its `id` reset on route transitions.

**Failure mode:** skip link navigates to a stale target or an element that has been replaced.

**Fix:** use a stable `id` on the layout-level `<main>` element; avoid dynamically generated `id` values on skip-link targets.

### Gap 5 — Server Actions and Form Error Announcement

React 19 introduces Server Actions for form submission. Validation errors returned from Server Actions update the UI without triggering a focus change.

**Failure mode:** form error messages are rendered but not announced; keyboard users are not moved to the error summary.

**Fix:** on Server Action completion with errors, move focus to an error summary or the first invalid field after submission, and associate each error with its field. Avoid simultaneously focusing and assertively announcing the same text, which can duplicate speech; use a short live status when focus stays in place. Do not rely on visual scroll alone.

---

## CI and Automation Coverage Map

| Tool | What it catches | What it misses |
|------|----------------|----------------|
| `eslint-plugin-jsx-a11y` | Missing `alt`, role misuse, label associations, interactive handler without keyboard | Runtime state, dynamic ARIA, focus behavior |
| axe-core (component or E2E) | Rule-detectable roles, labels, landmarks and supported contrast cases; coverage depends on rules and rendered states | Announcement quality, focus order logic, AT interaction fidelity |
| Lighthouse accessibility | Subset of axe rules; CI-friendly score | Same limits as axe; score can be high with real failures |
| Pa11y | HTML_CodeSniffer by default; axe is an optional runner, or explicitly run both | Same runtime gaps as axe |
| Manual keyboard walkthrough | Tab order, visible focus, escape/arrow handling | Cannot be automated |
| Screen-reader test (VO + NVDA) | Announcement quality, reading order, live regions, AT-specific bugs | Time-intensive; not automatable |

**Rule:** automation gates are necessary but not sufficient. A CI axe pass does not satisfy WCAG 2.2 AA conformance. Keyboard and AT tests must be scheduled as part of every release cycle for any flow in scope.
