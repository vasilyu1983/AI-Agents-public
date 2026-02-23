---
name: software-ui-ux-design
description: Use when designing or auditing UI/UX (wireframes to UI specs), running heuristic and accessibility reviews (WCAG 2.2 AA, ARIA), defining design systems and tokens, improving flows/forms/states and conversion (CRO), or tailoring inclusive experiences (age, neurodiversity) across web/iOS/Android/desktop, including AI/automation UX patterns.
---

# Software UI/UX Design

Design intuitive, accessible, user-centered interfaces.

**Baselines (Jan 2026)**:
- **Accessibility**: WCAG 2.2 Level AA — [W3C](https://www.w3.org/TR/WCAG22/)
- **Performance**: Core Web Vitals (LCP ≤2.5s, INP ≤200ms, CLS ≤0.1) — [web.dev](https://web.dev/vitals/)
- **Platforms**: [Apple HIG](https://developer.apple.com/design/human-interface-guidelines/), [Material 3](https://m3.material.io/)

---

## Quick Start

- Clarify platform(s), primary user journey, and constraints (accessibility level, performance, localization, auth).
- Choose track: audit an existing UI (heuristics + state matrix + WCAG) or design a new UI (IA + flows + UI spec).
- Produce artifacts: recommendations, acceptance criteria, and a handoff spec (components, states, copy, tokens).

---

## Decision Tree

```text
Design challenge:
    ├─ What to build? → Use software-ux-research first
    ├─ Improving existing UI?
    │   ├─ Usability issues → Heuristic review
    │   ├─ Accessibility gaps → WCAG 2.2 audit
    │   ├─ Inconsistency → Design system alignment
    │   └─ Conversion issues → CRO audit
    ├─ Building new UI?
    │   └─ references/ui-generation-workflows.md
    ├─ Specific demographics?
    │   └─ references/demographic-inclusive-design.md
    └─ Platform constraints?
        ├─ Web → semantics + focus + reflow
        ├─ iOS → system nav + Dynamic Type
        └─ Android → Material + edge-to-edge
```

---

## Interaction Checklist

| Goal | Do | Avoid |
|------|----|-------|
| Clarity | One primary action per view | Competing CTAs |
| Affordances | Native controls, strong signifiers | Clickable divs, hover-only |
| Feedback | Immediate visual response | Silent taps |
| Error prevention | Constrain inputs, show examples | Submit-then-fail |
| Error recovery | Specific message + next step | "Something went wrong" |
| Consistency | Reuse patterns and terms | Same term, different meanings |

---

## State Matrix

| State | Treatment | When |
|-------|-----------|------|
| **Loading** | Placeholder matching layout | Data fetching |
| **Empty** | Message + CTA | Zero items |
| **Error** | Alert + retry action | Request fails |
| **Offline** | Banner + cached indicator | No network |
| **Degraded** | Warning + limited functionality | Partial failure |

---

## Platform Constraints

### Web

- Semantic HTML first (no "div soup")
- ARIA only when needed
- Manage focus on SPA navigation
- Reflow at 320 CSS px (WCAG 1.4.10)
- Target size ≥24px (WCAG 2.5.8)

### iOS

- System navigation (tab bar, nav bar)
- Dynamic Type support
- Dark mode + system materials
- Handle Safe Areas

### Android

- Material 3 components
- Dynamic Color (Material You)
- Edge-to-edge content
- Handle predictive back

---

## WCAG 2.2 Key Changes

| Requirement | Implementation |
|-------------|----------------|
| Focus not obscured | Keep focus visible with sticky UI |
| Focus appearance | Clear visible indicator |
| Dragging movements | Non-drag alternatives |
| Target size | ≥24×24 CSS px |
| Redundant entry | Don't re-request known info |
| Accessible auth | Avoid cognitive tests |

### Reduced Motion

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Design Tokens

```json
{
  "color": {
    "primary": {
      "$value": "#0066cc",
      "$type": "color"
    }
  },
  "spacing": {
    "sm": {
      "$value": "8px",
      "$type": "dimension"
    }
  }
}
```

| Layer | Examples | Purpose |
|-------|----------|---------|
| Primitive | `blue-500`, `16px` | Raw values |
| Semantic | `color-primary` | Intent-based |
| Component | `button-bg` | Component-specific |

---

## Resources

| Resource | Purpose |
|----------|---------|
| [references/implementation-research-workflow.md](references/implementation-research-workflow.md) | Research before building |
| [references/design-systems.md](references/design-systems.md) | Design system patterns |
| [references/component-library-comparison.md](references/component-library-comparison.md) | shadcn, MUI, Radix |
| [references/nielsen-heuristics.md](references/nielsen-heuristics.md) | Heuristic evaluation |
| [references/wcag-accessibility.md](references/wcag-accessibility.md) | WCAG compliance |
| [references/demographic-inclusive-design.md](references/demographic-inclusive-design.md) | Age-specific UX |
| [references/neurodiversity-design.md](references/neurodiversity-design.md) | ADHD, autism, dyslexia |
| [references/ui-generation-workflows.md](references/ui-generation-workflows.md) | UI from scratch |
| [references/ai-design-tools-2025.md](references/ai-design-tools-2025.md) | Figma AI, v0 |
| [references/cro-framework.md](references/cro-framework.md) | Conversion optimization |
| [references/mobile-ux-patterns.md](references/mobile-ux-patterns.md) | Mobile UX: thumb zone, navigation, gestures, platform patterns |
| [references/form-design-patterns.md](references/form-design-patterns.md) | Form UX: layout, validation, multi-step, accessibility |
| [references/dark-mode-theming.md](references/dark-mode-theming.md) | Dark mode & multi-theme: tokens, CSS, platform implementation |
| [references/ai-automation-ux.md](references/ai-automation-ux.md) | AI/automation UX: chatbots, agents, progressive disclosure |
| [references/cultural-design-patterns.md](references/cultural-design-patterns.md) | Cross-cultural design: RTL, CJK, color semiotics, locale UX |
| [references/frontend-aesthetics-2025.md](references/frontend-aesthetics-2025.md) | Visual design trends 2025: glassmorphism, variable fonts, 3D |
| [references/modern-ux-patterns-2025.md](references/modern-ux-patterns-2025.md) | Modern UX patterns: command palettes, skeleton states, dark mode |
| [references/operational-playbook.md](references/operational-playbook.md) | Decision frameworks |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/design-brief.md](assets/design-brief.md) | Design brief |
| [assets/ux-review-checklist.md](assets/ux-review-checklist.md) | UX review |
| [assets/ui-generation/full-ui-spec.md](assets/ui-generation/full-ui-spec.md) | UI spec |
| [assets/audits/cro-audit-template.md](assets/audits/cro-audit-template.md) | CRO audit |
| [assets/accessibility/template-wcag-testing.md](assets/accessibility/template-wcag-testing.md) | WCAG testing |
| [assets/design-systems/template-design-system.md](assets/design-systems/template-design-system.md) | Design system setup |
| [assets/component-libraries/template-shadcn-ui.md](assets/component-libraries/template-shadcn-ui.md) | shadcn/ui integration |
| [assets/component-libraries/template-mui-material-ui.md](assets/component-libraries/template-mui-material-ui.md) | MUI / Material UI |
| [assets/interaction-patterns/template-micro-interactions.md](assets/interaction-patterns/template-micro-interactions.md) | Micro-interactions |

## Pattern Inspiration

- [Mobbin](https://mobbin.com/) — 300k+ screenshots
- [Page Flows](https://pageflows.com/) — User flow recordings
- [Refero Design](https://refero.design/) — Web design references

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-ux-research](../software-ux-research/SKILL.md) | Research (use first) |
| [software-frontend](../software-frontend/SKILL.md) | Implementation |
| [software-mobile](../software-mobile/SKILL.md) | Mobile patterns |
| [product-management](../product-management/SKILL.md) | Product strategy |

---

## Prototype-to-Production Alignment (Dashboard Lesson Pack)

Use this when a team says "prototype is close, but real page feels off".

### 1) Desktop choreography before pixel tweaks

- Start with asymmetric columns (about 60/40), not strict mirrored rows.
- Keep independent vertical rhythm per column; align only intentional pairs.
- Prevent dead-right canvas by moving right-column cards up when left grows.

### 2) Compactness heuristics (web)

- Tighten module spacing to ~10-14px in related zones.
- Remove decorative section labels unless they add navigation value.
- Merge adjacent related blocks into one container if this reduces visual fragmentation.
- **Default to flat/compact, not expandable/accordion**: Use static inline content unless the user explicitly needs progressive disclosure. Expanding panels add interaction cost, layout shift, and complexity. Only use accordions/drawers when content volume genuinely exceeds viewport tolerance.

### 3) Control standardization

- One primary action per card context.
- One share style across dashboard; avoid duplicate share controls in one context.
- Replace oversized full-width disclosure controls with compact secondary pills/links.
- Keep day chips + "This Week" as one visual family with stable alignment.

### 4) De-duplication rules

- Do not repeat the same meaning in metadata, chips, and body hints.
- If context is shown under the hero title (date/moon/phase), remove duplicate decorative restatements.
- Remove duplicate guidance fragments across Signal/Tension and Do/Do not.

### 5) Banner governance

- Promotional/validation banners are contextual, not always-on.
- Dismissal must persist; route-level suppression is required for noisy cards.
- Passive banners should not look selected (no heavy "active" border unless stateful).

### 6) Loading-state quality bar

- Skeletons must map to final IA (shape/count/relative sizing).
- Keep header context visible while loading.
- Avoid disconnected full-page placeholder compositions that create "messy" perception.

### 7) i18n requirement in design handoff

- Every user-visible string (including aria labels/tooltips) must be key-based.
- Define EN keys as baseline in spec before implementation.
- Reject hardcoded strings in final QA.

### 8) Final QA pass sequence

1. Desktop rhythm and right-side void check (1440+).
2. Mobile chip size/contrast/alignment check.
3. Control consistency sweep (buttons, links, share, chips).
4. Expansion behavior check (no whitespace blowouts).
5. Loading state and feature-surfacing sanity check.

## Ops UI QA: Design-to-Ship Checks

Use this after implementing visual changes to prevent "looks good in Figma, broken in prod" outcomes.

### Fast QA Commands

```bash
# 1) Run build first (layout and import safety)
npm run build

# 2) Run accessibility smoke if available
npm run test:e2e -- --grep "@a11y"

# 3) Capture route screenshots for review set
# (replace with your project screenshot task)
npm run test:e2e -- --grep "@visual"
```

### Required Review Grid

Validate each critical screen for:
- desktop rhythm (1366+, 1440+, 1920),
- mobile spacing and tap targets (360-430 width),
- loading/empty/error state consistency,
- contrast and focus visibility,
- localization expansion (long strings, RTL if supported).

### Operational Rule

Do not sign off on visual changes without state coverage (loading, empty, error, success). Most production regressions hide outside the default happy state.

