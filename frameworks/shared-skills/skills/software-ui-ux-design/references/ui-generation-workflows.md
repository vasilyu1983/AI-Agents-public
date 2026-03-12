# UI Generation Workflows

End-to-end workflow for creating UI from scratch: discovery to handoff.

**Last Updated**: January 2026
**References**: [Google Design Sprint](https://designsprintkit.withgoogle.com/), [Figma - Design Process](https://www.figma.com/best-practices/), [Nielsen Norman - UX Process](https://www.nngroup.com/articles/ux-research-cheat-sheet/)

---

## Workflow Overview

```
Discovery → Information Architecture → Wireframes → Visual Design → Prototyping → Handoff
    ↓              ↓                      ↓             ↓              ↓          ↓
 Research      Sitemap             Low-fidelity    High-fidelity  Interactive  Dev specs
 Personas      User flows          Layouts         Components      Testing      Tokens
 Competitor    Content             Annotations     Motion          Validation   Assets
 audit         hierarchy           Feedback        Typography                   Code
```

---

## Phase 1: Discovery

### Inputs Required

| Input | Source | Purpose |
|-------|--------|---------|
| Business goals | Stakeholders | Define success metrics |
| User research | Interviews, surveys | Understand user needs |
| Technical constraints | Engineering | Know platform limits |
| Brand guidelines | Marketing | Visual language foundation |
| Competitor analysis | Market research | Identify opportunities |

### Discovery Checklist

```
BUSINESS:
- [ ] Primary business objective defined
- [ ] Success metrics identified (KPIs)
- [ ] Budget and timeline constraints
- [ ] Stakeholder alignment documented

USER:
- [ ] Target user segments defined
- [ ] User needs/jobs documented
- [ ] Pain points identified
- [ ] Current journey mapped (if existing product)

TECHNICAL:
- [ ] Platform(s) confirmed (web, iOS, Android)
- [ ] Technology stack known
- [ ] Performance requirements
- [ ] Accessibility requirements (WCAG level)
- [ ] Browser/device support matrix

COMPETITIVE:
- [ ] 3-5 competitors analyzed
- [ ] Strengths/weaknesses documented
- [ ] Differentiation opportunities identified
```

### Persona Template

```markdown
## [Persona Name]

**Demographics**
- Age: [range]
- Role: [job/life stage]
- Tech comfort: [low/medium/high]
- Devices: [primary, secondary]

**Goals**
1. [Primary goal]
2. [Secondary goal]

**Frustrations**
1. [Pain point 1]
2. [Pain point 2]

**Quote**
"[Representative quote capturing their perspective]"

**Scenario**
[1-2 sentence usage scenario]
```

---

## Phase 2: Information Architecture

### Sitemap Creation

```
1. List all required pages/screens
2. Group by category/function
3. Define hierarchy (max 3 levels deep)
4. Identify shared components
5. Map navigation paths
```

**Sitemap Template**
```
Home
├── Products
│   ├── Category A
│   │   ├── Product List
│   │   └── Product Detail
│   └── Category B
├── Account
│   ├── Profile
│   ├── Orders
│   └── Settings
├── Cart
│   ├── Cart View
│   └── Checkout
└── Support
    ├── FAQ
    └── Contact
```

### User Flow Mapping

**Flow Notation**
```
[ ] = Screen/Page
<> = Decision point
() = Entry/Exit point
→ = Navigation
```

**Example: Checkout Flow**
```
(Cart) → [Cart View] → [Shipping] → <Guest/Login?>
                                        ↓ Guest
                                    [Guest Checkout]
                                        ↓ Login
                                    [Login] → [Account] → [Shipping]
[Shipping] → [Payment] → [Review] → <Payment Success?>
                                        ↓ Yes
                                    [Confirmation] → (Exit)
                                        ↓ No
                                    [Error] → [Payment]
```

### Content Inventory

| Page | Content Blocks | Priority | Status |
|------|----------------|----------|--------|
| Home | Hero, Features, CTA, Testimonials | High | Draft |
| Product List | Filters, Grid, Pagination | High | Planned |
| Product Detail | Gallery, Info, Reviews, Related | High | Planned |

---

## Phase 3: Wireframes

### Wireframe Levels

| Level | Fidelity | Purpose | Time |
|-------|----------|---------|------|
| Sketch | Very low | Rapid ideation | 5 min/screen |
| Lo-fi | Low | Structure validation | 15 min/screen |
| Mid-fi | Medium | Interaction design | 30 min/screen |

### Wireframe Checklist

```
LAYOUT:
- [ ] Content hierarchy clear
- [ ] Primary action prominent
- [ ] Navigation consistent
- [ ] Responsive breakpoints considered

INTERACTION:
- [ ] All interactive elements marked
- [ ] States defined (default, hover, active, disabled)
- [ ] Error states planned
- [ ] Empty states planned
- [ ] Loading states planned

ANNOTATIONS:
- [ ] Element behavior described
- [ ] Content requirements noted
- [ ] Constraints documented
- [ ] Questions/assumptions flagged
```

### Component Inventory

```markdown
## Core Components Needed

### Navigation
- [ ] Header (logo, nav, search, account, cart)
- [ ] Footer (links, legal, social)
- [ ] Mobile nav (hamburger, bottom bar)
- [ ] Breadcrumbs

### Content
- [ ] Card (product, feature, testimonial)
- [ ] List (horizontal, vertical, grid)
- [ ] Image (single, gallery, carousel)
- [ ] Video player
- [ ] Table

### Forms
- [ ] Input (text, email, password, phone)
- [ ] Textarea
- [ ] Select/Dropdown
- [ ] Checkbox, Radio
- [ ] Date picker
- [ ] File upload

### Feedback
- [ ] Button (primary, secondary, tertiary)
- [ ] Modal/Dialog
- [ ] Toast/Snackbar
- [ ] Alert/Banner
- [ ] Progress (bar, spinner, skeleton)

### Utility
- [ ] Badge/Tag
- [ ] Avatar
- [ ] Icon set
- [ ] Tooltip
- [ ] Divider
```

---

## Phase 4: Visual Design

### Design Token Definition

```json
{
  "color": {
    "primary": {
      "50": "#E3F2FD",
      "500": "#2196F3",
      "900": "#0D47A1"
    },
    "semantic": {
      "success": "#4CAF50",
      "warning": "#FF9800",
      "error": "#F44336",
      "info": "#2196F3"
    }
  },
  "typography": {
    "fontFamily": {
      "sans": "Inter, system-ui, sans-serif",
      "mono": "JetBrains Mono, monospace"
    },
    "fontSize": {
      "xs": "0.75rem",
      "sm": "0.875rem",
      "base": "1rem",
      "lg": "1.125rem",
      "xl": "1.25rem",
      "2xl": "1.5rem",
      "3xl": "1.875rem"
    }
  },
  "spacing": {
    "0": "0",
    "1": "0.25rem",
    "2": "0.5rem",
    "4": "1rem",
    "8": "2rem",
    "16": "4rem"
  },
  "radius": {
    "none": "0",
    "sm": "0.25rem",
    "md": "0.5rem",
    "lg": "1rem",
    "full": "9999px"
  }
}
```

### Typography Scale

| Level | Size | Weight | Line Height | Use |
|-------|------|--------|-------------|-----|
| Display | 3rem | 700 | 1.1 | Hero headings |
| H1 | 2.25rem | 700 | 1.2 | Page titles |
| H2 | 1.875rem | 600 | 1.25 | Section headings |
| H3 | 1.5rem | 600 | 1.3 | Subsections |
| H4 | 1.25rem | 600 | 1.35 | Card titles |
| Body | 1rem | 400 | 1.5 | Paragraphs |
| Small | 0.875rem | 400 | 1.5 | Captions |
| Tiny | 0.75rem | 400 | 1.4 | Labels |

### Component States

```
EVERY interactive component needs:

┌─────────────────────────────────────────────┐
│ STATE          │ VISUAL CHANGE             │
├─────────────────────────────────────────────┤
│ Default        │ Base appearance           │
│ Hover          │ Subtle highlight          │
│ Focus          │ Visible ring/outline      │
│ Active/Pressed │ Darker/inset              │
│ Disabled       │ Reduced opacity (0.5)     │
│ Loading        │ Spinner, disabled         │
│ Error          │ Red border, error text    │
│ Success        │ Green indicator           │
└─────────────────────────────────────────────┘
```

### Responsive Breakpoints

| Name | Min Width | Columns | Gutter | Margin |
|------|-----------|---------|--------|--------|
| Mobile | 0 | 4 | 16px | 16px |
| Tablet | 768px | 8 | 24px | 32px |
| Desktop | 1024px | 12 | 24px | auto |
| Wide | 1440px | 12 | 32px | auto |

---

## Phase 5: Prototyping

### Prototype Levels

| Level | Tool | Interactions | Purpose |
|-------|------|--------------|---------|
| Clickable | Figma | Page links | Flow validation |
| Interactive | Figma/Framer | Animations, states | UX testing |
| Coded | React/Vue | Real data | Dev preview |

### Interaction Specification

```markdown
## Component: Add to Cart Button

**Default State**
- Background: primary-500
- Text: white
- Shadow: sm

**Hover**
- Background: primary-600
- Transition: 150ms ease

**Active**
- Background: primary-700
- Transform: scale(0.98)

**Loading**
- Show spinner (white, 16px)
- Text: "Adding..."
- Disabled: true

**Success**
- Background: success-500
- Icon: checkmark
- Text: "Added!"
- Duration: 2000ms
- Then: return to default

**Error**
- Shake animation (2 cycles)
- Show toast with error message
- Return to default
```

### Prototype Testing Checklist

```
BEFORE USER TESTING:
- [ ] All critical flows complete
- [ ] No dead ends
- [ ] Error states included
- [ ] Loading states included
- [ ] Mobile version ready (if applicable)
- [ ] Realistic content (not lorem ipsum)

TEST SCENARIOS:
1. [ ] Happy path completion
2. [ ] Error recovery
3. [ ] Edge cases (empty cart, no results)
4. [ ] Accessibility (keyboard navigation)
```

---

## Phase 6: Developer Handoff

### Handoff Package Contents

```
/handoff
├── /design-tokens
│   ├── tokens.json
│   ├── colors.css
│   └── typography.css
├── /components
│   ├── button.spec.md
│   ├── input.spec.md
│   └── [component].spec.md
├── /pages
│   ├── home.spec.md
│   └── [page].spec.md
├── /assets
│   ├── /icons (SVG)
│   ├── /images (optimized)
│   └── /fonts
└── README.md
```

### Component Specification Template

```markdown
# Button Component

## Variants
- Primary: Main CTA actions
- Secondary: Secondary actions
- Tertiary: Low-emphasis actions
- Destructive: Delete/cancel actions

## Sizes
| Size | Height | Padding | Font Size |
|------|--------|---------|-----------|
| sm | 32px | 12px 16px | 14px |
| md | 40px | 16px 24px | 16px |
| lg | 48px | 20px 32px | 18px |

## States
- Default, Hover, Focus, Active, Disabled, Loading

## Props
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | string | 'primary' | Visual variant |
| size | string | 'md' | Button size |
| disabled | boolean | false | Disable interaction |
| loading | boolean | false | Show loading state |
| icon | ReactNode | null | Leading icon |
| iconRight | ReactNode | null | Trailing icon |

## Accessibility
- role="button"
- Focusable when not disabled
- aria-disabled when disabled
- aria-busy when loading

## Code Example
```jsx
<Button variant="primary" size="md">
  Add to Cart
</Button>
```
```

### Asset Export Guidelines

| Asset Type | Format | Sizes | Naming |
|------------|--------|-------|--------|
| Icons | SVG | 16, 20, 24px | icon-[name].svg |
| Logos | SVG + PNG | @1x, @2x, @3x | logo-[variant].svg |
| Images | WebP + fallback | responsive | [context]-[desc].webp |
| Favicons | ICO + PNG | 16, 32, 180 | favicon-[size].png |

---

## Quick Start Templates

### New Project Kickoff

```markdown
## Project: [Name]

### Overview
[1-2 sentence description]

### Goals
1. [Primary goal]
2. [Secondary goal]

### Users
- Primary: [segment]
- Secondary: [segment]

### Platforms
- [ ] Web (desktop)
- [ ] Web (mobile)
- [ ] iOS app
- [ ] Android app

### Timeline
- Discovery: [dates]
- Design: [dates]
- Development: [dates]
- Launch: [date]

### Success Metrics
- [Metric 1]: [target]
- [Metric 2]: [target]
```

### Design Review Checklist

```
VISUAL:
- [ ] Consistent with design system
- [ ] Color contrast passes WCAG AA
- [ ] Typography hierarchy clear
- [ ] Spacing consistent
- [ ] Responsive at all breakpoints

INTERACTION:
- [ ] All states designed
- [ ] Feedback for user actions
- [ ] Error handling clear
- [ ] Loading states present

CONTENT:
- [ ] Real content (not placeholder)
- [ ] Copy reviewed
- [ ] Localization considered

ACCESSIBILITY:
- [ ] Focus states visible
- [ ] Keyboard navigation works
- [ ] Screen reader compatible
- [ ] Motion respects preferences
```

---

## Related Resources

- [Design Systems](design-systems.md) - Token and component architecture
- [Modern UX Patterns](modern-ux-patterns-2025.md) - Skeleton screens, optimistic UI
- [WCAG Accessibility](wcag-accessibility.md) - Accessibility requirements
- [AI Design Tools](ai-design-tools-2025.md) - AI-assisted workflows
