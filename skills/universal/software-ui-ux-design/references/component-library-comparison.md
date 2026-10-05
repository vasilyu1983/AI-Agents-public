# UI Component Library Comparison Guide

How to choose a React component library or primitive layer for a product surface. This file holds the selection judgment; installation, theming code and framework integration live in [software-frontend](../../software-frontend/SKILL.md) (shadcn/ui setup in its Next.js and operational-playbook references; MUI in [mui-integration-notes.md](../../software-frontend/references/mui-integration-notes.md)).

## Table of Contents

- [Quick Comparison Table](#quick-comparison-table)
- [Decision Rules](#decision-rules)
- [Official Design System Required by Brief](#official-design-system-required-by-brief)
- [Accessibility](#accessibility)
- [Vetting Before You Commit](#vetting-before-you-commit)
- [Resources](#resources)

---

## Quick Comparison Table

Do not hardcode popularity metrics (stars, downloads) or version numbers in specs; check them on demand (see [Vetting Before You Commit](#vetting-before-you-commit)).

| Library | Approach | Styling | Accessibility posture | Best For | Tradeoffs |
|---------|----------|---------|------------------------|----------|-----------|
| **MUI** | Full component system | CSS-in-JS (`sx`/theme) | Strong primitives + patterns | Enterprise apps, dashboards | Material look, heavier baseline; advanced grid and pickers are separately licensed tiers |
| **shadcn/ui** | Copy-paste components | Tailwind CSS | Strong (via accessible primitives) | Custom design systems | Manual updates (you own the code) |
| **Base UI** | Primitives | Unstyled | Strong | Custom design systems | Newer ecosystem; verify component coverage before standardizing |
| **Ant Design** | Full component system | CSS-in-JS with design tokens | Good | Admin/back-office UIs | Opinionated visual language |
| **Chakra UI** | Full component system | CSS-in-JS (style props) | Strong | Accessibility-forward apps | Fewer "enterprise data" widgets |
| **React Aria** | Primitives/components | Unstyled | Strong | Building custom accessible components | More engineering time |
| **Radix UI** | Primitives | Unstyled | Strong | Custom design systems | Mature primitives; you own styling and composition |
| **Headless UI** | Primitives | Unstyled | Good | Tailwind teams | Smaller component surface area |
| **Mantine** | Full component system | Built-in theming | Good | Rapid development | Less standardized across orgs |
| **21st.dev** | Community registry on shadcn conventions, with an MCP for search and generation | Tailwind CSS | Varies per contributor — audit each pull | Fast prototyping, AI-assisted component sourcing | Uneven quality, per-component licensing, copy-in means no upstream patches |

## Decision Rules

- **Many prebuilt widgets and fast delivery, brand can be themed** → MUI or Ant Design (Ant for dense admin UIs).
- **Custom visual identity on Tailwind** → shadcn/ui (on Radix or Base UI primitives) or Headless UI.
- **Primitives-first custom design system** → React Aria, Radix UI or Base UI; budget for styling and composition work.
- **Simple component system, fast iteration** → Chakra UI or Mantine.
- **Data-heavy screens** → pick the grid, chart and date-picker story first; it usually decides the library. Measure those widgets' payload separately.
- **Performance** → measure route payloads with your own build; zero-runtime styling (Tailwind, static CSS) avoids CSS-in-JS runtime cost, but tree-shaking and code-splitting usually matter more than the library choice.
- **Migrating between majors or libraries** → read the vendor's migration guide and codemods for the installed version; never plan from memory.
- **Community registries** → treat each pulled component as third-party code: check its licence, run the accessibility checks below, and record where it came from.

## Official Design System Required by Brief

The rules above route among **generic React libraries** — the right default whenever the brief does not name a platform. This subsection is **additive**: it covers the narrower case where the brief names, or clearly implies, a specific platform or official design system. Then the choice is a compliance or platform-integration requirement, and hand-rolling a visual clone forfeits guarantees a generic library was never built to provide.

**"Required" applies only when a specific official system is named or clearly implied by the brief.** Otherwise use the table and rules above — do not default to an official system "just in case."

| Brief signal | Required package | Why hand-rolling is wrong |
|--------------|------------------|---------------------------|
| Microsoft / enterprise SaaS on Windows or M365 surfaces | `@fluentui/react-components` | Cloning Fluent visually still misses accessibility and Windows-integration guarantees |
| Shopify app surfaces (embedded admin, checkout extensions) | Shopify Polaris | Polaris compliance is an App Store review criterion, not just a look |
| UK public-sector service | `govuk-frontend` | GOV.UK Design System accessibility conformance is a Service Standard requirement, not a preference |
| US federal/public-sector service | `uswds` | Section 508 conformance is built into USWDS components; a hand-rolled clone forfeits it |
| Google/Android-native surfaces | Material Design 3 (see [design-systems.md](design-systems.md#official-design-systems)) | Platform conventions and accessibility services expect Material semantics |
| Enterprise data-heavy admin/back-office | Carbon / Ant Design / MUI X — cross-reference the [Decision Rules](#decision-rules) | Generic libraries are the right default when no official system is named |

When **no official package exists** for the requested look — glassmorphism, bento grids, brutalism, and other aesthetic movements have no owning platform or vendor — build with native CSS or Tailwind, and note in code comments that the treatment is inspired by a genre rather than implementing a named system.

> Adapted from the "Brief → Design System Map" (§2) in [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), commit `e988add20dab0fa97d7a76781c48961c8184288e` (MIT License). Added 2026-08-09.

## Accessibility

No UI library guarantees WCAG conformance; you still need automated checks plus manual keyboard and screen-reader passes. When accessibility is a hard requirement, prefer libraries with explicit focus, keyboard and ARIA guarantees and strong docs (React Aria, Radix, Headless UI) or systems with well-documented patterns (MUI, Chakra). Design-level criteria are in [wcag-accessibility.md](wcag-accessibility.md); component remediation and testing are in [software-accessibility](../../software-accessibility/SKILL.md).

## Vetting Before You Commit

Check maintenance and fit on the day you decide, not from a static list:

1. `npm view <package> version time repository.url` — publish cadence and latest major.
2. The repository's recent commits, open-issue response time and release notes.
3. The licence of the core package and of any paid tier (grids, pickers, charts, templates).
4. Coverage for the components your surface needs (menus, dialogs, combobox, date picker, data grid) in the version you would install.
5. A keyboard and screen-reader smoke test of the three most complex components you need.

## Resources

- **Base UI**: https://base-ui.com/
- **MUI**: https://mui.com/
- **shadcn/ui**: https://ui.shadcn.com/
- **Ant Design**: https://ant.design/
- **Chakra UI**: https://chakra-ui.com/
- **Radix UI**: https://www.radix-ui.com/
- **Mantine**: https://mantine.dev/
- **Headless UI**: https://headlessui.com/
- **React Aria**: https://react-spectrum.adobe.com/react-aria/
- [design-systems.md](design-systems.md) — building a custom design system on top of a library
