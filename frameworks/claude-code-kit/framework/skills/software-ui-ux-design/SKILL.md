---
name: software-ui-ux-design
description: UI/UX design principles, usability heuristics, accessibility standards, and design system patterns for creating user-centered interfaces.
---

# Software UI/UX Principles Skill — Quick Reference

Use this skill when the primary focus is designing intuitive, accessible, and user-centered interfaces rather than implementing technical features.

---

## When to Use This Skill

Invoke when users ask for:

- UI/UX design patterns and best practices
- Usability evaluation and improvement recommendations
- Accessibility compliance (WCAG, ARIA)
- Design system setup and component libraries
- User-centered design methodologies
- Information architecture and navigation design
- Mobile-first and responsive design patterns
- Form design and input validation UX
- **Pattern selection based on user pain points** (from `software-ux-research` analysis)
- **UI fixes for feedback-identified issues** (navigation, onboarding, performance, forms)

---

## Quick Reference Table

| UX Task | Pattern/Tool | Implementation | When to Use |
|---------|--------------|----------------|-------------|
| **Distinctive Aesthetics** | **Creative typography, bold color** | **Avoid Inter/Roboto, commit to theme** | **Prevent generic AI aesthetics** |
| **Pain Point → Pattern** | **Feedback-driven design** | **Use `software-ux-research` first** | **When you have user feedback to act on** |
| Cognitive Load & Cues | Gestalt grouping, preattentive cues | Chunk info, align, use contrast/weight/icons | Dense data, complex flows; reduce working-memory load |
| Signifiers & Mappings | Visible affordances, natural layouts | Show clickable states, map controls to outputs | Any interactive element; prevent slips/mistakes |
| Loading States | Skeleton screens | Shimmer placeholders | All async data (preferred over spinners) |
| User Feedback | Toast notifications | 3-5 sec auto-dismiss | Non-blocking confirmations |
| Form Validation | Inline validation | Validate on blur | Real-time feedback without annoyance |
| Navigation | Breadcrumbs + tabs | Hierarchical + contextual | Multi-level content (max 3 clicks) |
| Empty States | Action-oriented prompts | "Create your first..." | Never show blank pages |
| Accessibility | WCAG 2.2 AA | 4.5:1 contrast, keyboard nav | All production apps (legal requirement) |
| Component Library | shadcn/ui or MUI | Copy-paste or npm install | Design system foundation |
| Micro-interactions | 200-400ms animations | CSS transitions/Framer Motion | Button states, hover, loading |

## Decision Tree: UI/UX Design Approach

```text
Design challenge: [Feature Type]
    ├─ Building from scratch?
    │   ├─ Need full control? → shadcn/ui (copy-paste, Tailwind)
    │   ├─ Need speed? → MUI (comprehensive, out-of-the-box)
    │   └─ Accessibility priority? → Chakra UI (best-in-class a11y)
    │
    ├─ Improving existing UI?
    │   ├─ Usability issues? → Nielsen heuristics evaluation (resources/nielsen-heuristics.md)
    │   ├─ Accessibility gaps? → WCAG 2.2 audit (resources/wcag-accessibility.md)
    │   └─ Visual inconsistency? → Design system setup (resources/design-systems.md)
    │
    ├─ Loading/feedback states?
    │   ├─ Data loading? → Skeleton screens (not spinners)
    │   ├─ User action? → Optimistic UI + toast notifications
    │   └─ Form submission? → Inline validation + progress indicators
    │
    ├─ Complex form?
    │   ├─ Multi-step? → Progress bar + save drafts
    │   ├─ Many fields? → Group related fields + progressive disclosure
    │   └─ Validation? → Inline on blur (not on every keystroke)
    │
    ├─ First 5 seconds clear?
    │   ├─ First-click test? → Primary action obvious, trunk nav clear
    │   └─ Scannable copy? → Plain-language labels, front-loaded headings
    │
    ├─ Mobile vs Desktop?
    │   ├─ Mobile-first design → Start 320px, scale up
    │   └─ Touch targets 44x44px minimum
    │
    └─ Have user pain points from feedback?
        ├─ Navigation issues? → Breadcrumbs, tabs, simplified IA
        ├─ Onboarding confusion? → Progressive disclosure, guided tours
        ├─ Performance complaints? → Skeleton screens, optimistic UI
        ├─ Form frustration? → Inline validation, autosave, chunking
        └─ Need pain points first? → Use software-ux-research skill
```

---

## Navigation

### Resources (Best Practices & Guides)

- [resources/frontend-aesthetics-2025.md](resources/frontend-aesthetics-2025.md) — Distinctive design principles to avoid generic AI aesthetics (typography, color, motion, backgrounds, AI design tools)
- [resources/design-systems.md](resources/design-systems.md) — Comprehensive design system implementation guide (foundations, components, patterns)
- [resources/component-library-comparison.md](resources/component-library-comparison.md) — 2025 UI library comparison (MUI, shadcn/ui, Ant Design, Chakra UI, Radix UI, React Aria, Mantine, Headless UI)
- [resources/modern-ux-patterns-2024.md](resources/modern-ux-patterns-2024.md) — Modern UX patterns (skeleton screens, optimistic UI, progressive disclosure, micro-interactions)
- [resources/nielsen-heuristics.md](resources/nielsen-heuristics.md) — Heuristic evaluation guide with practical examples
- [resources/wcag-accessibility.md](resources/wcag-accessibility.md) — WCAG 2.2 success criteria and implementation guide
- [data/sources.json](data/sources.json) — 85+ curated external references (usability research, design systems, component libraries, animation libraries, 2024 patterns)

### Templates by Category

**Component Libraries (Implementation Guides):**

- [templates/component-libraries/template-shadcn-ui.md](templates/component-libraries/template-shadcn-ui.md) — shadcn/ui with Radix UI + Tailwind CSS (copy-paste components, full ownership)
- [templates/component-libraries/template-mui-material-ui.md](templates/component-libraries/template-mui-material-ui.md) — Material-UI (Google Material Design, enterprise-grade, 95k+ stars)

**Interaction Patterns (Micro-interactions & Animations):**

- [templates/interaction-patterns/template-micro-interactions.md](templates/interaction-patterns/template-micro-interactions.md) — 2024 micro-interaction patterns (buttons, forms, loading states, toasts, drag-and-drop)

**Design & Planning:**

- [templates/design-brief.md](templates/design-brief.md) — Single-source design brief (goals, IA, accessibility, experimentation)
- [templates/ux-review-checklist.md](templates/ux-review-checklist.md) — Heuristic + accessibility review checklist

### Related Skills (Cross-Functional)

- [../software-ux-research/SKILL.md](../software-ux-research/SKILL.md) — **Research sibling**: Use FIRST for feedback analysis, pain point extraction, competitive analysis → feeds pattern selection here
- [../software-frontend/SKILL.md](../software-frontend/SKILL.md) — Frontend implementation (Next.js 16, React, TypeScript, Tailwind CSS, shadcn/ui)
- [../software-mobile/SKILL.md](../software-mobile/SKILL.md) — Mobile UX patterns (iOS Swift, Android Kotlin, platform conventions)
- [../product-management/SKILL.md](../product-management/SKILL.md) — Product strategy, user research, positioning
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) — UI/E2E testing, visual regression, accessibility automation
- [../software-architecture-design/SKILL.md](../software-architecture-design/SKILL.md) — System design patterns and architecture principles
- [../software-backend/SKILL.md](../software-backend/SKILL.md) — API design for optimal UX (REST, GraphQL, real-time)

---

## Operational Playbooks
- [resources/operational-playbook.md](resources/operational-playbook.md) — Design themes, accessibility heuristics, mobile-first guidance, and decision frameworks
