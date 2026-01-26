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
| [references/operational-playbook.md](references/operational-playbook.md) | Decision frameworks |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/design-brief.md](assets/design-brief.md) | Design brief |
| [assets/ux-review-checklist.md](assets/ux-review-checklist.md) | UX review |
| [assets/ui-generation/full-ui-spec.md](assets/ui-generation/full-ui-spec.md) | UI spec |
| [assets/audits/cro-audit-template.md](assets/audits/cro-audit-template.md) | CRO audit |

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
