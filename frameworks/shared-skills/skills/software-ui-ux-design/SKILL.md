---
name: software-ui-ux-design
description: Use when designing UI interfaces, conducting accessibility audits (WCAG 2.2), building design systems, or improving user flows. Covers platform guidelines (iOS/Android/Web/Desktop), state patterns, CRO, demographic-inclusive design, and AI design tools.
---

# Software UI/UX Design Skill — Quick Reference

Use this skill when the primary focus is designing intuitive, accessible, and user-centered interfaces. For research planning/synthesis, use `software-ux-research`.

---

## Jan 2026 Baselines (Core)

- **Accessibility baseline**: WCAG 2.2 Level AA (W3C Recommendation, 12 Dec 2024) https://www.w3.org/TR/WCAG22/
- **US regulatory note**: ADA Title II requires WCAG 2.1 AA for state/local government sites by 24 April 2026 https://www.ada.gov/resources/web-guidance/
- **EU shipping note**: European Accessibility Act applies to covered products/services after 28 Jun 2025 (Directive (EU) 2019/882) https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32019L0882
- **Web performance UX baseline**: Core Web Vitals stable set is `LCP` (≤2.5s), `INP` (≤200ms), `CLS` (≤0.1) https://web.dev/vitals/
- **Sustainable design baseline**: W3C Web Sustainability Guidelines (WSG) 1.0 — 93 guidelines for sustainable digital design (W3C Note, April 2026) https://www.w3.org/TR/web-sustainability-guidelines/
- **Design system interoperability**: Prefer token-first foundations aligned to Design Tokens Community Group Technical Reports 2025.10 https://tr.designtokens.org/
- **Platform constraints**: Use Apple HIG and Material 3 as primary sources: https://developer.apple.com/design/human-interface-guidelines/ and https://m3.material.io/

## When to Use This Skill

Invoke when users ask for:

- UI/UX design patterns and best practices
- Usability evaluation and improvement recommendations
- Accessibility compliance (WCAG, ARIA)
- Design system setup and component patterns
- Information architecture and navigation design
- Mobile-first and responsive design patterns
- Form design and input validation UX
- **Pattern selection based on user pain points** (from `software-ux-research` analysis)
- **UI fixes for feedback-identified issues** (navigation, onboarding, performance, forms)
- **Demographic-specific design** (seniors, children, cultural, neurodiversity)
- **UI generation from scratch** (wireframes to handoff)
- **Conversion rate optimization** (CRO audits, A/B testing)
- **AI-assisted design workflows** (Figma AI, v0, Midjourney)

## When NOT to Use This Skill

- **User research planning/synthesis** → Use [software-ux-research](../software-ux-research/SKILL.md) first
- **Frontend code implementation** → Use [software-frontend](../software-frontend/SKILL.md)
- **Mobile platform-specific development** → Use [software-mobile](../software-mobile/SKILL.md)
- **Product strategy/roadmap decisions** → Use [product-management](../product-management/SKILL.md)
- **Visual/graphic design** → This skill focuses on interaction design, not brand identity

---

## Operating Mode (Core)

If inputs are missing, ask for: users + top tasks, platforms (web/iOS/Android/desktop), IA depth, accessibility target, performance constraints, and any evidence (screenshots, URLs, analytics, tickets, prior research).

Default outputs (pick what the user asked for):
- UX review checklist → prioritized issues → recommendations + acceptance criteria
- Flow + state spec (happy path + edge/error/empty/loading/offline/degraded) with acceptance criteria
- Design system delta spec (tokens + components + states) with governance-ready contribution plan

## UX Impact Metrics

| Activity | Proxy Metric | Value Calculation |
|----------|--------------|-------------------|
| Usability finding | Prevented dev rework | Hours saved × $150/hr |
| Heuristic evaluation | Early defect detection | Defects × Cost-to-fix-later |
| A/B test result | Improved conversion | ΔConversion × Traffic × LTV |
| Accessibility fix | Compliance + reach | Avoided lawsuit + 15% audience |

**Quick ROI benchmarks**:
- 1 usability fix preventing 40hr rework = **$6,000**
- 0.5% conversion lift on 100k visitors × $50 LTV = **$25,000/mo**
- Task success rate = (Completed / Attempted) × 100

## Core Interaction Design

### Interaction Checklist (Do / Avoid / Acceptance Criteria)

| Goal | Do | Avoid | Acceptance Criteria |
|------|----|-------|---------------------|
| Clarity | One primary action per view; front-load labels | Competing CTAs; ambiguous verbs | User can state next step in 5 seconds [Inference] |
| Affordances | Use native controls; strong signifiers | Clickable `<div>`; hover-only cues | All actions are discoverable without hover |
| Feedback | Immediate visual response on input | Silent taps/clicks | Every action has an observable state change |
| Error prevention | Constrain inputs; show examples | “Submit then fail” patterns | Invalid states are hard to create |
| Error recovery | Specific message + next step | “Something went wrong” only | Every error offers retry/undo/support path |
| Safe defaults | Preselect safest option; make destructive explicit | Risky defaults; hidden consequences | Destructive actions are confirmed or reversible |
| Consistency | Reuse patterns and terms | Same term used for different concepts | Pattern library covers common flows |

## Decision Tree: UI/UX Design Approach

```text
Design challenge: [Feature Type]
    ├─ Need to decide what to build? → Use software-ux-research first
    ├─ Improving an existing UI?
    │   ├─ Usability issues? → Heuristic review (references/nielsen-heuristics.md)
    │   ├─ Accessibility gaps? → WCAG 2.2 audit (references/wcag-accessibility.md)
    │   ├─ Inconsistency? → Design system alignment (references/design-systems.md)
    │   └─ Conversion issues? → CRO audit (references/cro-framework.md)
    ├─ Building a new UI from scratch?
    │   ├─ Full workflow → references/ui-generation-workflows.md
    │   ├─ Use AI tools? → references/ai-design-tools-2025.md
    │   └─ Spec template → assets/ui-generation/full-ui-spec.md
    ├─ Building a new flow?
    │   ├─ Define states → loading/empty/error/offline/degraded
    │   ├─ Define recovery → retry/cancel/undo/support
    │   └─ Define telemetry → success, error, time, abandonment
    ├─ Designing for specific demographics?
    │   ├─ Age groups (seniors, children, teens) → references/demographic-inclusive-design.md
    │   ├─ Cultural/regional (RTL, Asia, MENA) → references/cultural-design-patterns.md
    │   └─ Neurodiversity (ADHD, autism, dyslexia) → references/neurodiversity-design.md
    └─ Platform constraints?
        ├─ Web → semantics + focus + reflow
        ├─ iOS → system navigation + Dynamic Type
        ├─ Android → Material patterns + back/edge-to-edge
        └─ Desktop → shortcuts + selection models
```

---

## Information Architecture (Scalable Products)

### IA Checklist

- [ ] Identify primary user roles and their top tasks (by frequency and criticality).
- [ ] Define content types (nouns) and actions (verbs); avoid mixing.
- [ ] Choose navigation model: global (app-level) vs local (within a section).
- [ ] Ensure findability at scale: search, filters, sort, saved views.
- [ ] Label in user language; include short helper text where needed.
- [ ] Plan permissions/visibility states: “no access”, “request access”, “limited view”.

### Common IA Anti-Patterns

| Anti-pattern | Why it fails | Better |
|-------------|--------------|--------|
| Deep nesting (“6 clicks deep”) | Recall burden, lost context | Flatter IA + search + saved views |
| Hamburger-only desktop nav | Hidden affordance for frequent tasks | Visible primary nav + overflow |
| Filters without “clear/reset” | Traps users in empty results | Clear-all + applied-filter chips |

## Platform Constraints & Anti-Patterns

### Web (Browser-Based)

| Do | Avoid | Rationale |
|----|-------|-----------|
| Semantic HTML first | "div soup" | A11y + reliability (WAI-ARIA APG) |
| ARIA only when needed | ARIA on native controls | "No ARIA > bad ARIA" |
| Manage focus on SPA nav | Focus resets to body | WCAG 2.4.3/2.4.7 |
| Visible focus, non-obscured | Focus hidden by sticky UI | WCAG 2.4.7 + 2.4.11 |
| Reflow at 320 CSS px | Fixed-width layouts | WCAG 1.4.10 |
| Non-drag alternatives | Drag-only | WCAG 2.5.7 |
| ≥24px target size | Tiny hit targets | WCAG 2.5.8 |

Browser gotchas: Safari datetime-local limited; Firefox :focus-visible differs; Chrome autocomplete inconsistent.

### iOS / iPadOS (Apple HIG)

| Do | Avoid |
|----|-------|
| System nav (tab bar, nav bar) | Custom nav paradigms |
| Dynamic Type support | Fixed font sizes |
| Pull-to-refresh for lists | Custom refresh gestures |
| SF Symbols for icons | Custom icons for standard actions |
| Dark mode + system materials | Light-only |
| Handle Safe Areas | Assume full-screen |
| System controls for input | Custom re-implementations |

### Android (Material Design 3)

| Do | Avoid |
|----|-------|
| Material 3 components | iOS-style patterns |
| Dynamic Color (Material You) | Hardcoded brand colors |
| Edge-to-edge content | System bar padding hacks |
| Navigation rail on tablets | Phone UI stretched |
| Handle predictive back | Block system back |
| Support split-screen/foldables | Single-window only |

Android notes: Test Samsung One UI, handle mdpi-xxxhdpi, support gesture + 3-button nav.

### Desktop (Windows/macOS/Linux)

| Do | Avoid |
|----|-------|
| Keyboard shortcuts + discoverability | Mouse-only |
| Proper window resize | Fixed-size windows |
| Multi-window/monitor support | Single viewport |
| Hover states for interactives | Touch-first without hover |
| Right-click context menus | Hamburger for all actions |
| High-DPI support (Retina, 4K) | 1x assets only |
| Selection models (click, shift, ctrl) | Single-select only |

---

## State-Heavy UI Patterns

### State Matrix: Required States for All Interactive Views

| State | Visual Treatment | When to Show | Duration |
|-------|------------------|--------------|----------|
| **Loading** | Placeholder matching layout; label if blocking | Data fetching | Until data arrives or times out |
| **Empty** | Message + next step + CTA | Zero items, no data | Until content exists |
| **Partial Data** | Show available content + placeholders | Incremental loads | Until complete |
| **Error** | Alert with specific message + retry action | Request fails, validation fails | Until user dismisses or retries |
| **Success** | Inline confirmation or toast | Action completes | Context-dependent |
| **Offline** | Banner with status + cached data indicator | Network unavailable | Until reconnection |
| **Degraded** | Warning badge + limited functionality notice | Partial system failure | Until service restored |
| **No Access** | Explain + request path | Missing permissions | Until access granted |

### Loading State Decision Tree

```text
Data fetch initiated
    ├─ Fast → pressed/disabled state only
    ├─ Noticeable → inline placeholder
    └─ Long-running → progress + cancel + background option
```

**Empty states**: Context-relevant illustration + headline + next steps + CTA. Never "No data found" without guidance.

### Error State Severity Levels

| Level | Example | Treatment | User Action |
|-------|---------|-----------|-------------|
| **Recoverable** | Network timeout | Inline warning + retry | Retry button |
| **Correctable** | Invalid email format | Field-level error | Fix input |
| **Blocking** | 500 server error | Full-page error | Contact support / retry later |
| **Partial** | Some items failed to load | Inline notice per item | Retry individual items |

---

## Long-Running Operations

### Pattern: Operations >10 Seconds

For uploads, exports, batch processing, and migrations:

| Element | Implementation | Example |
|---------|----------------|---------|
| **Progress** | Determinate if known, indeterminate if unknown | "Uploading 3 of 10 files (30%)" |
| **Cancel** | Always provide cancel option | "Cancel upload" button |
| **Background** | Allow user to navigate away | "Processing in background—we'll notify you" |
| **Resumability** | Support pause/resume for large operations | "Resume upload" after interruption |
| **Notification** | Notify on completion | Toast, badge, or push notification |
| **History** | Show operation history/status | "Recent exports" list |

### Implementation Checklist

- [ ] Show progress percentage or step count if determinable
- [ ] Allow cancel at any point without data loss
- [ ] Support backgrounding (user can navigate away)
- [ ] Provide completion notification (in-app and/or push)
- [ ] Handle interruptions gracefully (network drop, browser close)
- [ ] Show operation history with status and retry option
- [ ] For uploads: show per-file progress, allow skip/retry individual

---

## Performance UX & Latency Budgets

### Perceived Speed Thresholds

Use human response-time thresholds to decide when to show feedback and when to switch to progress indicators (NN/g) https://www.nngroup.com/articles/response-times-3-important-limits/

| Duration | User Perception | UI Response |
|----------|-----------------|-------------|
| ~0.1s | Feels instant | No extra UI beyond direct manipulation feedback |
| ~1s | Flow stays intact | Keep context; show subtle “working” feedback |
| ≥10s | Attention breaks | Show percent-done + cancel + resumability |

### Core Web Vitals (User-Centric Performance)

Core Web Vitals stable set and thresholds (including INP replacing FID as the interaction metric) https://web.dev/vitals/

| Metric | UX Meaning | Design/System Impact |
|--------|------------|----------------------|
| LCP ≤ 2.5s | “Content loads fast” | Reduce hero weight; reserve layout; avoid late-loading fonts |
| INP ≤ 200ms | “UI responds” | Avoid main-thread long tasks; prioritize input responsiveness |
| CLS ≤ 0.1 | “UI doesn’t jump” | Set media dimensions; avoid late injections; stable skeletons |

### Perceived Performance Techniques

| Technique | When to Use | Implementation |
|-----------|-------------|----------------|
| **Optimistic UI** | High-confidence operations | Show success immediately, rollback on failure |
| **Skeleton Screens** | Content loading | Match layout shape of final content |
| **Progressive Loading** | Large datasets | Load critical content first, then enhance |
| **Streaming/Chunked** | Incremental content, long lists | Show content as it arrives |
| **Prefetching** | Predictable navigation | Preload likely next pages on hover/idle |
| **Placeholder Content** | Images, media | Low-res blur-up, dominant color |

### Anti-Patterns

| Pattern | Problem | Alternative |
|---------|---------|-------------|
| Spinner for everything | No layout context, feels slower | Skeleton matching content shape |
| Blocking UI during async | User can't interact | Background processing + toast |
| Full-page reload on action | Loses context, slow | Client-side state update |
| No feedback <3 seconds | User thinks action failed | Immediate button state change |

---

## Accessibility & Motion Safety (WCAG 2.2 AA)

### WCAG 2.2 Changes That Impact Product UI

| Requirement | What to Build | Link |
|-------------|---------------|------|
| Focus not obscured (AA) | Keep focus visible with sticky headers/footers | https://www.w3.org/TR/WCAG22/#focus-not-obscured-minimum |
| Focus appearance (AA) | Provide a clearly visible focus indicator | https://www.w3.org/TR/WCAG22/#focus-appearance |
| Dragging movements | Provide non-drag alternatives | https://www.w3.org/TR/WCAG22/#dragging-movements |
| Target size (minimum) | Make targets at least 24×24 CSS px (exceptions apply) | https://www.w3.org/TR/WCAG22/#target-size-minimum |
| Consistent help | Keep help mechanisms consistent across pages | https://www.w3.org/TR/WCAG22/#consistent-help |
| Redundant entry | Don’t require re-entering known information | https://www.w3.org/TR/WCAG22/#redundant-entry |
| Accessible authentication | Avoid cognitive-function tests without alternatives | https://www.w3.org/TR/WCAG22/#accessible-authentication-minimum |

### Reduced Motion Support

`prefers-reduced-motion` is defined in Media Queries Level 5 https://www.w3.org/TR/mediaqueries-5/#prefers-reduced-motion

```css
/* Always provide reduced motion path */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Motion Safety Checklist

- [ ] All animations respect `prefers-reduced-motion`
- [ ] No content flashes >3 times per second (WCAG 2.3.1)
- [ ] Parallax effects have static alternative
- [ ] Auto-playing carousels can be paused
- [ ] No pure-motion conveyed information (add text labels)
- [ ] Avoid large-area color transitions (can trigger vestibular issues)

### Focus Management Requirements

| Scenario | Focus Behavior | Implementation |
|----------|----------------|----------------|
| Modal opens | Focus moves to modal | `trapFocus()` + `aria-modal="true"` |
| Modal closes | Focus returns to trigger | Store and restore `document.activeElement` |
| Route change (SPA) | Focus to main content | `main.focus()` or skip link |
| Toast appears | Announce, don't steal focus | `aria-live="polite"` |
| Error on submit | Focus to first error field | `firstError.focus()` |
| Dynamic content loads | Announce update | `aria-live` region |

### Keyboard Navigation Patterns

| Pattern | Keys | Implementation |
|---------|------|----------------|
| **Roving tabindex** | Arrow keys within composite | Tab to enter widget, arrows to move, Tab to exit |
| **Focus trap** | Tab cycles within region | Modal, dropdown (until dismissed) |
| **Skip links** | Tab → Enter | "Skip to main content" as first focusable |
| **Escape to close** | Esc | Modals, dropdowns, tooltips |
| **Enter/Space to activate** | Enter or Space | Buttons, links, toggles |

---

## Design Tokens (Dec 2025)

### Design Tokens Community Group Format

Standardized token format for design system interoperability (Design Tokens Technical Reports 2025.10) https://tr.designtokens.org/

```json
{
  "color": {
    "primary": {
      "$value": "#0066cc",
      "$type": "color",
      "$description": "Primary brand color"
    },
    "primary-hover": {
      "$value": "{color.primary}",
      "$type": "color",
      "$extensions": {
        "mode": {
          "dark": "#3399ff"
        }
      }
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

### Token Architecture

| Layer | Examples | Purpose |
|-------|----------|---------|
| Primitive | `blue-500`, `16px` | Raw values |
| Semantic | `color-primary`, `spacing-sm` | Intent-based |
| Component | `button-bg`, `card-padding` | Component-specific |

### Governance & Contribution Model

| Topic | Policy (Default) | Notes |
|------|-------------------|-------|
| Ownership | Design + Eng co-owners | Shared accountability |
| Versioning | SemVer + changelog | Breaking changes require migration notes |
| Deprecation | “Warn → ship both → remove” | Provide codemods where possible [Inference] |
| Contributions | RFC → design review → implementation → release | Include a11y + QA gates |
| Documentation | Token tables, component API, examples, dos/don’ts | “How to use” beats “what it is” |

---

## Hybrid Input Handling

Modern users switch between mouse, touch, keyboard, trackpad, and stylus—often within a single session.

### Input Detection & Adaptation

Pointer and hover capabilities are defined in Media Queries Level 4 https://www.w3.org/TR/mediaqueries-4/#mf-interaction

```typescript
// Detect primary input modality
const supportsHover = window.matchMedia('(hover: hover)').matches;
const supportsTouch = 'ontouchstart' in window;
const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Respond to input changes
window.matchMedia('(pointer: coarse)').addEventListener('change', (e) => {
  // User switched to touch device or changed mode
  updateInteractionStyle(e.matches ? 'touch' : 'pointer');
});
```

### Input-Aware Design Matrix

| Feature | Mouse/Trackpad | Touch | Keyboard | Stylus |
|---------|----------------|-------|----------|--------|
| **Hover states** | Show on hover | N/A (use long-press or tap) | Show on focus | Show on hover |
| **Target size** | ≥24px (WCAG minimum) | ≥44px (recommended) | N/A | ≥44px |
| **Tooltips** | On hover | On long-press or tap icon | On focus | On hover |
| **Context menu** | Right-click | Long-press | Shift+F10 | Right-click equivalent |
| **Drag-and-drop** | Native | Touch-and-hold + drag | Provide keyboard alternative | Native |
| **Selection** | Click + shift/ctrl | Tap + selection mode | Space to select | Tap |

### Hybrid Input Checklist

- [ ] All interactions work with keyboard alone
- [ ] Touch targets meet WCAG 2.5.8 minimum and aim larger where feasible
- [ ] Hover states have touch-accessible alternative
- [ ] Drag-and-drop has non-drag alternative (WCAG 2.5.7) https://www.w3.org/TR/WCAG22/#dragging-movements
- [ ] No hover-only information (provide tap/focus alternative)
- [ ] Stylus/pen input treated as pointer (supports hover)
- [ ] Test with actual touch devices, not just emulation

---

## AI/Automation UX (Optional)

For products with AI/ML features (chatbots, recommendations, generative AI), see [references/ai-automation-ux.md](references/ai-automation-ux.md) — covers transparency, user control patterns, trust calibration, and anti-patterns.

---

## Navigation

### References

| Category | File |
|----------|------|
| Visual design | [frontend-aesthetics-2025.md](references/frontend-aesthetics-2025.md) |
| Design systems | [design-systems.md](references/design-systems.md) |
| Component libraries | [component-library-comparison.md](references/component-library-comparison.md) |
| UX patterns | [modern-ux-patterns-2024.md](references/modern-ux-patterns-2024.md) |
| Heuristics | [nielsen-heuristics.md](references/nielsen-heuristics.md) |
| Accessibility | [wcag-accessibility.md](references/wcag-accessibility.md) |
| Age-specific UX | [demographic-inclusive-design.md](references/demographic-inclusive-design.md) |
| Neurodiversity | [neurodiversity-design.md](references/neurodiversity-design.md) |
| Cultural patterns | [cultural-design-patterns.md](references/cultural-design-patterns.md) |
| UI generation | [ui-generation-workflows.md](references/ui-generation-workflows.md) |
| AI design tools | [ai-design-tools-2025.md](references/ai-design-tools-2025.md) |
| CRO | [cro-framework.md](references/cro-framework.md) |

### Templates

| Template | File |
|----------|------|
| shadcn/ui setup | [template-shadcn-ui.md](assets/component-libraries/template-shadcn-ui.md) |
| MUI setup | [template-mui-material-ui.md](assets/component-libraries/template-mui-material-ui.md) |
| Micro-interactions | [template-micro-interactions.md](assets/interaction-patterns/template-micro-interactions.md) |
| Design brief | [design-brief.md](assets/design-brief.md) |
| UX review | [ux-review-checklist.md](assets/ux-review-checklist.md) |
| UI spec | [full-ui-spec.md](assets/ui-generation/full-ui-spec.md) |
| CRO audit | [cro-audit-template.md](assets/audits/cro-audit-template.md) |

### UI Pattern Inspiration

- [Mobbin](https://mobbin.com/) — 300k+ mobile/web screenshots
- [Page Flows](https://pageflows.com/) — User flow recordings
- [Refero Design](https://refero.design/) — Web design references

### Related Skills

- [software-ux-research](../software-ux-research/SKILL.md) — Research (use FIRST)
- [software-frontend](../software-frontend/SKILL.md) — Implementation
- [software-mobile](../software-mobile/SKILL.md) — Mobile patterns
- [product-management](../product-management/SKILL.md) — Strategy
- [qa-testing-strategy](../qa-testing-strategy/SKILL.md) — Testing

---

## Trend Awareness Protocol

**WebSearch required** for: "best design system for...", "what component library...", "latest UI/UX trends", "current best practices for..."

Search: `"UI UX design trends 2026"`, `"design system best practices 2026"`, `"WCAG updates 2026"`

Report: Current landscape → Emerging trends → Deprecated patterns → Recommendation

---

## Operational Playbooks

- [references/operational-playbook.md](references/operational-playbook.md) — Design themes, accessibility heuristics, mobile-first guidance, decision frameworks
