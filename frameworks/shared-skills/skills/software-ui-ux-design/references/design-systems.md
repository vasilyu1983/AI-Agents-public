# Design Systems — Comprehensive Guide

A design system is a collection of reusable components, guided by clear standards, that can be assembled to build applications. It serves as a single source of truth for design and development teams.

---
## Table of Contents

- [What is a Design System?](#what-is-a-design-system)
- [Design System vs Style Guide vs Component Library](#design-system-vs-style-guide-vs-component-library)
- [Building a Design System](#building-a-design-system)
- [Phase 1: Audit and Inventory](#phase-1-audit-and-inventory)
- [Phase 2: Define Foundations](#phase-2-define-foundations)
- [Phase 3: Design Components](#phase-3-design-components)
- [Phase 4: Document Patterns](#phase-4-document-patterns)
- [Phase 5: Create Documentation](#phase-5-create-documentation)
- [Button](#button)
- [Usage](#usage)
- [Variants](#variants)
- [Code Example](#code-example)
- [Props](#props)
- [Accessibility](#accessibility)
- [Best Practices](#best-practices)
- [Related](#related)
- [Design Tokens (W3C Design Tokens Community Group Format)](#design-tokens-w3c-design-tokens-community-group-format)
- [File Format Reference (2025.10 Reports)](#file-format-reference-202510-reports)
- [Token Types (2025.10 Reports)](#token-types-202510-reports)
- [Semantic vs. Primitive Tokens](#semantic-vs-primitive-tokens)
- [Modes (Light/Dark/High-Contrast)](#modes-lightdarkhigh-contrast)
- [Tooling Ecosystem](#tooling-ecosystem)
- [Multi-Platform Design Systems](#multi-platform-design-systems)
- [Platform-Specific Considerations](#platform-specific-considerations)
- [Theming](#theming)
- [Governance and Maintenance](#governance-and-maintenance)
- [Design System Team](#design-system-team)
- [Contribution Model](#contribution-model)
- [Versioning](#versioning)
- [Changelog](#changelog)
- [[2.0.0] - 2024-03-15](#200-2024-03-15)
- [Breaking Changes](#breaking-changes)
- [Added](#added)
- [Fixed](#fixed)
- [Adoption Metrics](#adoption-metrics)
- [Example Design Systems](#example-design-systems)
- [Material Design (Google)](#material-design-google)
- [Human Interface Guidelines (Apple)](#human-interface-guidelines-apple)
- [Carbon Design System (IBM)](#carbon-design-system-ibm)
- [Polaris (Shopify)](#polaris-shopify)
- [Fluent (Microsoft)](#fluent-microsoft)
- [Building Blocks Checklist](#building-blocks-checklist)
- [Foundations](#foundations)
- [Components](#components)
- [Patterns](#patterns)
- [Documentation](#documentation)
- [Tooling](#tooling)
- [Tools and Resources](#tools-and-resources)
- [Design Tools](#design-tools)
- [Development Tools](#development-tools)
- [Component Libraries](#component-libraries)
- [Inspiration](#inspiration)
- [Figma Operations (Library Hygiene)](#figma-operations-library-hygiene)
- [Common Pitfalls](#common-pitfalls)
- [Success Metrics](#success-metrics)
- [Resources](#resources)


## What is a Design System?

**Definition**: A design system is a collection of reusable components and a set of standards guiding their use, enabling teams to design and develop products faster and more consistently.

**Components**:
1. **Foundations** — Visual styles (color, typography, spacing, etc.)
2. **Components** — Reusable UI elements (buttons, inputs, cards, etc.)
3. **Patterns** — Common solutions to recurring problems
4. **Guidelines** — Rules and best practices
5. **Documentation** — How to use the system

**Benefits**:
- **Consistency** — Unified user experience across products
- **Efficiency** — Figma's internal research measured designers completing a task 34% faster with an up-to-date, task-relevant design system in place; Figma's own writeup flags this as close to a best case, not a guaranteed number — treat as directional, not a universal benchmark ([Figma Blog — Measuring the Value of Design Systems](https://www.figma.com/blog/measuring-the-value-of-design-systems/))
- **Scalability** — Easy to maintain and update at scale
- **Collaboration** — Shared language between design and development
- **Quality** — Built-in accessibility and best practices

---

## Design System vs Style Guide vs Component Library

**Style Guide**
- Visual standards (colors, typography, logo usage)
- Brand guidelines
- Static documentation

**Component Library**
- Collection of reusable UI components
- Code implementation
- Technical resource

**Design System**
- Comprehensive framework including both above
- Living documentation
- Principles, patterns, guidelines
- Tooling and workflows

---

## Building a Design System

### Phase 1: Audit and Inventory

**Visual Audit**
- Collect all existing UI patterns
- Identify inconsistencies
- Document current components
- Analyze usage frequency

**Tools**:
- Screenshots of all major screens
- Component inventory spreadsheet
- Design file audit (Figma, Sketch)

**Questions to Answer**:
- How many button styles exist?
- How many shades of each brand color?
- What spacing values are in use?
- Which patterns are duplicated?

### Phase 2: Define Foundations

Establish the core design language that everything else builds upon.

#### Color System

**Structure**:
- **Primary** — Brand color (main actions, links)
- **Secondary** — Supporting brand color
- **Neutral** — Grays (text, backgrounds, borders)
- **Semantic** — Purpose-based (success, warning, error, info)

**Scale**: Each color needs multiple shades (50-900)

```javascript
const colors = {
  primary: {
    50: '#e3f2fd',
    100: '#bbdefb',
    // ...
    500: '#2196f3', // Base
    // ...
    900: '#0d47a1',
  },
  semantic: {
    success: '#4caf50',
    warning: '#ff9800',
    error: '#f44336',
    info: '#2196f3',
  },
};
```

**Best Practices**:
- 5-10 shades per color family
- Ensure WCAG AA contrast (4.5:1 for text)
- Test in light and dark modes
- Name by function, not appearance

**Distinctive Color Strategies**:
- **Avoid overly generic palettes**: Purple gradients, blue-on-white corporate schemes, evenly-distributed rainbows
- **Commit to a dominant theme**: 60-70% dominant color, 20-30% secondary, 5-10% accent
- **Theme strategies**: Dark-first with neon accents (dev tools), warm earth tones (wellness), bold monochrome (fashion), brutalist (experimental)
- **Draw inspiration from**: IDE themes (Dracula, Nord, Tokyo Night), cultural aesthetics (Japanese, Scandinavian), art movements (Bauhaus, Art Deco)
- **See**: [frontend-aesthetics.md](frontend-aesthetics.md#principle-2-committed-color--themes) for comprehensive color guidance

#### Typography

**Type Scale**
Use a modular scale for consistent sizing.

```css
/* Example: 1.25 ratio (Major Third) */
--font-size-xs: 0.64rem;   /* 10.24px */
--font-size-sm: 0.8rem;    /* 12.8px */
--font-size-base: 1rem;    /* 16px */
--font-size-lg: 1.25rem;   /* 20px */
--font-size-xl: 1.563rem;  /* 25px */
--font-size-2xl: 1.953rem; /* 31.25px */
--font-size-3xl: 2.441rem; /* 39px */
```

**Font Families**:
- **Heading** — Display font (can be decorative)
- **Body** — Highly readable (serif or sans-serif)
- **Monospace** — Code blocks

**Text Styles**:
```css
h1 { font-size: var(--font-size-3xl); font-weight: 700; line-height: 1.2; }
h2 { font-size: var(--font-size-2xl); font-weight: 600; line-height: 1.3; }
h3 { font-size: var(--font-size-xl); font-weight: 600; line-height: 1.4; }
body { font-size: var(--font-size-base); font-weight: 400; line-height: 1.6; }
small { font-size: var(--font-size-sm); line-height: 1.5; }
```

**Best Practices**:
- Maximum 3 font families
- Line height: 1.4-1.6 for body text
- Limit font weights to 3-4 (e.g., 400, 500, 700)
- Ensure readability at all sizes

**Distinctive Typography Choices**:
- **Avoid unintentional defaults**: Make typography a deliberate brand choice [Inference]
- **Choose fonts with character**: Outfit, Syne, Crimson Pro, DM Sans, Cabinet Grotesk
- **Font pairing strategies**: Contrast pairing (geometric + serif), tonal pairing (same style, different weights), unexpected pairing (playful + professional)
- **See**: [frontend-aesthetics.md](frontend-aesthetics.md#principle-1-distinctive-typography) for comprehensive typography guidance

#### Spacing System

**8px Grid** (Most Common)
```css
--spacing-1: 0.5rem;  /* 8px */
--spacing-2: 1rem;    /* 16px */
--spacing-3: 1.5rem;  /* 24px */
--spacing-4: 2rem;    /* 32px */
--spacing-5: 2.5rem;  /* 40px */
--spacing-6: 3rem;    /* 48px */
--spacing-8: 4rem;    /* 64px */
--spacing-10: 5rem;   /* 80px */
```

**4px Grid** (Alternative)
```css
--spacing-1: 0.25rem; /* 4px */
--spacing-2: 0.5rem;  /* 8px */
--spacing-3: 0.75rem; /* 12px */
--spacing-4: 1rem;    /* 16px */
```

**Usage**:
- Padding, margins, gaps
- Consistent whitespace
- Predictable layouts

#### Elevation / Shadows

Define shadow layers for depth perception.

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
--shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
```

**Levels**:
- **0** — Flat (no shadow)
- **1** — Raised (cards, buttons)
- **2** — Floating (dropdowns, tooltips)
- **3** — Modal (dialogs, overlays)

#### Border Radius

```css
--radius-sm: 0.125rem; /* 2px */
--radius-md: 0.25rem;  /* 4px */
--radius-lg: 0.5rem;   /* 8px */
--radius-xl: 1rem;     /* 16px */
--radius-full: 9999px; /* Fully rounded */
```

#### Breakpoints (Responsive)

```css
--breakpoint-sm: 640px;   /* Mobile landscape */
--breakpoint-md: 768px;   /* Tablet */
--breakpoint-lg: 1024px;  /* Desktop */
--breakpoint-xl: 1280px;  /* Large desktop */
--breakpoint-2xl: 1536px; /* Extra large */
```

### Phase 3: Design Components

Create reusable UI components with consistent behavior.

#### Component Anatomy

Every component should define:
1. **Structure** — HTML/JSX markup
2. **Variants** — Different versions (primary, secondary, etc.)
3. **States** — Interaction states (hover, focus, disabled, etc.)
4. **Props/Options** — Configurable parameters
5. **Accessibility** — ARIA labels, keyboard support
6. **Documentation** — Usage guidelines and examples

#### Essential Components

**Buttons**
```jsx
// Variants
<Button variant="primary">Primary Action</Button>
<Button variant="secondary">Secondary Action</Button>
<Button variant="tertiary">Tertiary Action</Button>
<Button variant="danger">Delete</Button>

// Sizes
<Button size="sm">Small</Button>
<Button size="md">Medium</Button>
<Button size="lg">Large</Button>

// States
<Button disabled>Disabled</Button>
<Button loading>Loading...</Button>

// Icons
<Button iconLeft={<Icon name="plus" />}>Add Item</Button>
```

**Component Specifications**:
- Minimum height: 44px (touch target)
- Padding: 12px 24px (horizontal spacing)
- Border radius: 4px (or per design system)
- States: default, hover, active, focus, disabled, loading

**Form Inputs**
```jsx
// Text input
<Input
  label="Email address"
  type="email"
  placeholder="you@example.com"
  error="Please enter a valid email"
  required
/>

// Select
<Select
  label="Country"
  options={countries}
  placeholder="Select a country"
/>

// Checkbox
<Checkbox
  label="I agree to the terms"
  checked={agreed}
  onChange={setAgreed}
/>

// Radio group
<RadioGroup
  label="Shipping method"
  options={shippingMethods}
  value={selected}
  onChange={setSelected}
/>
```

**Cards**
```jsx
<Card>
  <CardHeader>
    <CardTitle>Card Title</CardTitle>
    <CardDescription>Supporting text</CardDescription>
  </CardHeader>
  <CardContent>
    Main content goes here
  </CardContent>
  <CardFooter>
    <Button>Action</Button>
  </CardFooter>
</Card>
```

**Modals/Dialogs**
```jsx
<Modal open={isOpen} onClose={handleClose}>
  <ModalHeader>
    <ModalTitle>Confirm Action</ModalTitle>
  </ModalHeader>
  <ModalBody>
    Are you sure you want to proceed?
  </ModalBody>
  <ModalFooter>
    <Button variant="secondary" onClick={handleClose}>
      Cancel
    </Button>
    <Button variant="primary" onClick={handleConfirm}>
      Confirm
    </Button>
  </ModalFooter>
</Modal>
```

**Navigation**
```jsx
// Top navigation
<Header>
  <Logo />
  <Nav>
    <NavItem href="/">Home</NavItem>
    <NavItem href="/about">About</NavItem>
    <NavItem href="/contact">Contact</NavItem>
  </Nav>
  <UserMenu />
</Header>

// Breadcrumbs
<Breadcrumbs>
  <BreadcrumbItem href="/">Home</BreadcrumbItem>
  <BreadcrumbItem href="/products">Products</BreadcrumbItem>
  <BreadcrumbItem current>Product Name</BreadcrumbItem>
</Breadcrumbs>
```

**Feedback Components**
```jsx
// Alert
<Alert variant="success">
  <AlertIcon />
  <AlertTitle>Success</AlertTitle>
  <AlertDescription>Your changes have been saved.</AlertDescription>
</Alert>

// Toast notification
<Toast variant="info" duration={5000}>
  New message received
</Toast>

// Progress
<ProgressBar value={65} max={100} />

// Spinner
<Spinner size="lg" />
```

### Phase 4: Document Patterns

Document common UI patterns and solutions.

#### Layout Patterns

**Page Layout**
```
┌─────────────────────────────────┐
│         Header / Nav            │
├─────────────────────────────────┤
│  ┌──────────┬───────────────┐   │
│  │          │               │   │
│  │ Sidebar  │  Main Content │   │
│  │          │               │   │
│  └──────────┴───────────────┘   │
├─────────────────────────────────┤
│           Footer                │
└─────────────────────────────────┘
```

**Grid System**
- 12-column grid (most common)
- Responsive breakpoints
- Gutters between columns

```css
.container {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: var(--spacing-4);
}

.col-4 {
  grid-column: span 4;
}

.col-6 {
  grid-column: span 6;
}
```

#### Form Patterns

**Single Column Layout** (Recommended)
- Reduces errors
- Faster completion
- Better mobile experience

**Field Grouping**
```jsx
<FormSection title="Personal Information">
  <Input label="First Name" />
  <Input label="Last Name" />
  <Input label="Email" type="email" />
</FormSection>

<FormSection title="Shipping Address">
  <Input label="Street Address" />
  <Input label="City" />
  <Select label="State" options={states} />
  <Input label="ZIP Code" />
</FormSection>
```

**Validation Pattern**
- Validate on blur (not on every keystroke)
- Show inline errors near field
- Disable submit until valid
- Preserve data on error

#### Empty States

```jsx
<EmptyState
  icon={<EmptyInboxIcon />}
  title="No messages yet"
  description="When someone sends you a message, it will appear here."
  action={<Button>Compose Message</Button>}
/>
```

#### Loading States

**Skeleton Screens** (Preferred over spinners)
```jsx
<SkeletonCard>
  <SkeletonText width="60%" height="24px" />
  <SkeletonText width="100%" height="16px" />
  <SkeletonText width="100%" height="16px" />
  <SkeletonText width="80%" height="16px" />
</SkeletonCard>
```

**Progressive Loading**
- Show critical content first
- Load secondary content asynchronously
- Indicate loading state clearly

### Phase 5: Create Documentation

**Documentation Structure**:
```
Design System Documentation
├── Getting Started
│   ├── Installation
│   ├── Quick Start
│   └── Migration Guide
├── Foundations
│   ├── Colors
│   ├── Typography
│   ├── Spacing
│   ├── Shadows
│   └── Breakpoints
├── Components
│   ├── Button
│   ├── Input
│   ├── Select
│   ├── Card
│   └── [etc.]
├── Patterns
│   ├── Forms
│   ├── Navigation
│   ├── Data Display
│   └── Feedback
├── Guidelines
│   ├── Accessibility
│   ├── Content
│   └── Internationalization
└── Resources
    ├── Figma Library
    ├── Code Repository
    └── Changelog
```

**Component Documentation Template**:

```markdown
# Button

Primary action component for user interactions.

## Usage

Use buttons for actions like submit, save, delete, or navigate.

## Variants

- **Primary** — Main call-to-action
- **Secondary** — Less prominent actions
- **Tertiary** — Subtle actions
- **Danger** — Destructive actions

## Code Example

[Interactive playground]

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | string | 'primary' | Button style variant |
| size | string | 'md' | Button size |
| disabled | boolean | false | Disable interaction |
| loading | boolean | false | Show loading state |

## Accessibility

- Minimum 44x44px touch target
- Focus visible indicator
- Disabled state communicated to screen readers

## Best Practices

DO:
- Use verb labels ("Save", "Delete")
- One primary button per screen
- Disable during async operations

AVOID:
- Use buttons for navigation (use links)
- Use generic labels ("Click here")

## Related

- Link component
- Icon button
```

---

## Design Tokens (Design Tokens Community Group Format)

**Reference**: [Design Tokens Technical Reports 2025.10](https://tr.designtokens.org/)

The Design Tokens Community Group (DTCG) — a W3C Community Group, not a Working Group — announced 2025.10 as the **first stable version** of the Format Module (28 October 2025), after several years of draft-only reports. Stable here means production-ready and safe to build tooling against, not a formal W3C Recommendation; DTCG specs are never W3C Recommendations because Community Group output sits outside the W3C standards track. Figma, Penpot, Sketch, Tokens Studio, and Style Dictionary all support the 2025.10 format as of mid-2026.

**Definition**: Design tokens are named entities that store visual design attributes (colors, spacing, etc.) in a platform-agnostic format.

**Benefits**:

- Single source of truth
- Multi-platform consistency
- Easy theming
- Programmatic updates

### File Format Reference (2025.10 Reports)

Design tokens use `.tokens.json` extension with standardized properties:

```json
{
  "$schema": "https://tr.designtokens.org/format/",
  "color": {
    "primary": {
      "$value": "#2196f3",
      "$type": "color",
      "$description": "Primary brand color for CTAs and links"
    },
    "primary-hover": {
      "$value": "{color.primary}",
      "$type": "color",
      "$description": "References primary color"
    }
  },
  "spacing": {
    "sm": {
      "$value": "8px",
      "$type": "dimension"
    },
    "md": {
      "$value": "16px",
      "$type": "dimension"
    }
  },
  "typography": {
    "heading-1": {
      "$value": {
        "fontFamily": "Inter",
        "fontSize": "32px",
        "fontWeight": 700,
        "lineHeight": 1.2
      },
      "$type": "typography"
    }
  },
  "shadow": {
    "elevation-1": {
      "$value": [
        {
          "color": "#00000026",
          "offsetX": "0px",
          "offsetY": "1px",
          "blur": "2px"
        }
      ],
      "$type": "shadow"
    }
  }
}
```

### Token Types (2025.10 Reports)

| Type | Format | Example |
|------|--------|---------|
| `color` | Hex, RGB, HSL, P3 | `"#2196f3"`, `"rgb(33, 150, 243)"` |
| `dimension` | Number + unit | `"16px"`, `"1rem"`, `"0.5em"` |
| `fontFamily` | String or array | `"Inter"`, `["Inter", "sans-serif"]` |
| `fontWeight` | Number or keyword | `700`, `"bold"` |
| `duration` | Number + time unit | `"200ms"`, `"0.3s"` |
| `cubicBezier` | Array of 4 numbers | `[0.4, 0, 0.2, 1]` |
| `shadow` | Array of shadow objects | See example above |
| `typography` | Composite object | Font family, size, weight, line height |
| `gradient` | Array of color stops | Linear, radial, conic |

### Semantic vs. Primitive Tokens

```json
{
  "primitive": {
    "blue-500": { "$value": "#2196f3", "$type": "color" },
    "blue-600": { "$value": "#1976d2", "$type": "color" }
  },
  "semantic": {
    "color-action-primary": { "$value": "{primitive.blue-500}", "$type": "color" },
    "color-action-primary-hover": { "$value": "{primitive.blue-600}", "$type": "color" }
  }
}
```

### Modes (Light/Dark/High-Contrast)

```json
{
  "color": {
    "background": {
      "$value": "#ffffff",
      "$type": "color",
      "$extensions": {
        "mode": {
          "dark": "#121212",
          "high-contrast": "#000000"
        }
      }
    }
  }
}
```

### Tooling Ecosystem

| Tool | Purpose | Notes |
|------|---------|-------|
| **Style Dictionary** | Transform tokens to CSS/JS/iOS/Android | Amazon, widely adopted |
| **Tokens Studio for Figma** | Figma plugin for token management | Syncs with JSON files |
| **Theo** | Token transformation (Salesforce) | Alternative to Style Dictionary |
| **Design Tokens Validator** | Validate against 2025.10 reports | CLI tool |

**Output Formats**:

- CSS custom properties
- Sass variables
- JavaScript objects
- iOS Swift
- Android XML

---

## Multi-Platform Design Systems

### Platform-Specific Considerations

**Web**
- CSS/Sass implementation
- Responsive breakpoints
- Browser compatibility

**iOS**
- Swift/SwiftUI components
- Human Interface Guidelines
- Native controls and gestures

**Android**
- Kotlin/Jetpack Compose
- Material Design guidelines
- Device fragmentation

**React Native**
- Cross-platform components
- Platform-specific adaptations
- Performance optimization

### Theming

**Light and Dark Modes**

```css
/* CSS Custom Properties approach */
:root {
  --color-background: #ffffff;
  --color-text: #000000;
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-background: #000000;
    --color-text: #ffffff;
  }
}
```

**Component Theming**
```jsx
const theme = {
  light: {
    background: '#ffffff',
    text: '#000000',
  },
  dark: {
    background: '#000000',
    text: '#ffffff',
  },
};

function App() {
  const [mode, setMode] = useState('light');

  return (
    <ThemeProvider theme={theme[mode]}>
      <YourApp />
    </ThemeProvider>
  );
}
```

---

## Governance and Maintenance

### Design System Team

**Roles**:
- **Design Lead** — Visual direction, component design
- **Engineering Lead** — Technical architecture, code quality
- **Product Manager** — Prioritization, roadmap
- **Content Designer** — Voice, tone, content patterns
- **Accessibility Specialist** — Ensure WCAG compliance

### Contribution Model

**Centralized** (Small teams)
- Core team owns all changes
- Faster decision-making
- Consistent quality
- Can become bottleneck

**Federated** (Large organizations)
- Multiple teams contribute
- Faster iteration
- Requires strong governance
- Risk of inconsistency

**Hybrid** (Recommended)
- Core team maintains foundations and critical components
- Other teams can contribute with approval
- Clear contribution guidelines

### Versioning

**Semantic Versioning** (MAJOR.MINOR.PATCH)
- **MAJOR** — Breaking changes (v2.0.0)
- **MINOR** — New features, backward compatible (v1.5.0)
- **PATCH** — Bug fixes (v1.5.1)

**Changelog**:
```markdown
# Changelog

## [2.0.0] - 2024-03-15
### Breaking Changes
- Button component: Removed `type` prop, use `variant` instead

### Added
- Dark mode support for all components
- New DatePicker component

### Fixed
- Input component: Fixed focus state in Safari
```

### Adoption Metrics

**Track**:
- Component usage across products
- Design-dev handoff time
- Consistency score (design audits)
- Time to build new features
- Developer satisfaction

**Tools**:
- Component analytics (track component usage)
- Design system surveys
- Contribution metrics (PRs, issues)

---

## Example Design Systems

> **Choosing between an official system and hand-rolling?** See [Official Design System Required by Brief](component-library-comparison.md#official-design-system-required-by-brief) in `component-library-comparison.md` for the brief-signal → required-package routing table (Fluent, Polaris, GOV.UK, USWDS, Material) and when hand-rolling forfeits compliance guarantees the official package provides. The list below is reference material on each system, not routing logic.
>
> *Cross-reference adapted from the "Brief → Design System Map" (§2) in [Leonxlnx/taste-skill](https://github.com/Leonxlnx/taste-skill), commit `e988add20dab0fa97d7a76781c48961c8184288e` (MIT License). Added 2026-08-09.*

### Material Design (Google)
- **Current version**: Material 3 Expressive (announced Google I/O 2025; the recommended Android/Wear OS design language as of 2026 (verify current at m3.material.io))
- **Platforms**: Web, Android, iOS, Flutter
- **Strengths**: Comprehensive, well-documented, expanded color and shape morphing (35 new shapes), new motion physics; eye-tracking studies showed 4× faster element identification vs Material 3
- **Tools**: Material Theme Builder, Material Icons
- **URL**: https://m3.material.io/

### Human Interface Guidelines (Apple)
- **Platforms**: iOS, macOS, watchOS, tvOS
- **Strengths**: Platform-native feel, detailed guidance
- **Focus**: Clarity, deference, depth
- **URL**: https://developer.apple.com/design/human-interface-guidelines/

### Carbon Design System (IBM)
- **Platforms**: Web (React, Vue, Angular, Vanilla)
- **Strengths**: Enterprise focus, data visualization, accessibility
- **Open Source**: Yes
- **URL**: https://carbondesignsystem.com/

### Polaris (Shopify)
- **Platforms**: Web (React)
- **Strengths**: E-commerce patterns, merchant-focused
- **Open Source**: Yes
- **URL**: https://polaris.shopify.com/

### Fluent (Microsoft)
- **Platforms**: Web, Windows, iOS, Android
- **Strengths**: Cross-platform, modern aesthetic
- **Tools**: Fluent UI React, Fluent UI Web Components
- **URL**: https://www.microsoft.com/design/fluent/

---

## Building Blocks Checklist

### Foundations
- [ ] Color palette (primary, secondary, neutral, semantic)
- [ ] Typography scale and font families
- [ ] Spacing system (4px or 8px grid)
- [ ] Elevation/shadows
- [ ] Border radius values
- [ ] Breakpoints (responsive)
- [ ] Iconography
- [ ] Motion/animation guidelines

### Components
- [ ] Buttons (primary, secondary, tertiary, danger)
- [ ] Form inputs (text, email, password, number, tel)
- [ ] Select/dropdown
- [ ] Checkbox, radio, toggle
- [ ] Textarea
- [ ] Cards
- [ ] Modal/dialog
- [ ] Alert/notification/toast
- [ ] Navigation (header, sidebar, tabs, breadcrumbs)
- [ ] Tables/data grids
- [ ] Pagination
- [ ] Tooltip
- [ ] Progress indicators (spinner, progress bar)
- [ ] Badges/chips/tags
- [ ] Avatar
- [ ] Accordion/collapse
- [ ] Tabs
- [ ] Date picker
- [ ] File upload

### Patterns
- [ ] Form layouts
- [ ] Page layouts
- [ ] Empty states
- [ ] Loading states (skeleton screens)
- [ ] Error states
- [ ] Data visualization
- [ ] Search and filtering
- [ ] Authentication flows

### Documentation
- [ ] Getting started guide
- [ ] Component documentation
- [ ] Pattern library
- [ ] Accessibility guidelines
- [ ] Code examples
- [ ] Design file (Figma/Sketch)
- [ ] Changelog

### Tooling
- [ ] Design tokens
- [ ] Component library (code)
- [ ] Storybook/playground
- [ ] Testing (visual regression, accessibility)
- [ ] CI/CD pipeline
- [ ] NPM package (if applicable)

---

## Tools and Resources

### Design Tools
- **Figma** — Collaborative design, component libraries, variables
- **Sketch** — macOS design tool, symbols, libraries
- **Adobe XD** — Design and prototyping
- **Penpot** — Open-source alternative to Figma

### Development Tools
- **Storybook** — Component development and documentation
- **Style Dictionary** — Design token transformation
- **Chromatic** — Visual regression testing
- **Zeroheight** — Design system documentation platform

### Component Libraries
- **Radix UI** — Unstyled, accessible primitives
- **Headless UI** — Unstyled components (React, Vue)
- **Chakra UI** — Modular, accessible React components
- **shadcn/ui** — Copy-paste components with Tailwind

### Inspiration
- **Design Systems Repo** — Collection of design systems
- **Adele** — Design systems and pattern libraries repository
- **Component Gallery** — Component examples from popular systems

---

## Figma Operations (Library Hygiene)

- Naming: Structured tokens (e.g., `Button/Primary/Default`, `Form/Input/Textfield/Success`); avoid ad-hoc variants.
- Autolayout defaults: Padding/gap tokens, min/max width, responsive resizing set on every component and state.
- Variants: Limit to essential props; keep booleans binary; document interaction states; prevent combinatorial explosion.
- Variables and tokens: Centralize color/spacing/typography/motion tokens; prefer semantic tokens (surface/primary/warning) over raw hex.
- Assets: Use component properties for icons/media swaps; keep icon library consistent in stroke/fill and naming.
- Handoff: Publish release notes, map components to code, include usage/do-not-use notes, attach prototype flows for critical journeys.

---

## Common Pitfalls

1. **Starting too big**
   - Start small (foundations + 5-10 components)
   - Iterate based on actual needs

2. **Building in isolation**
   - Involve product teams early
   - Solve real problems, not hypothetical ones

3. **Perfectionism**
   - Ship and iterate
   - Better to have 80% solution in use than 100% solution never released

4. **Lack of governance**
   - Define contribution process
   - Establish design review

5. **Poor documentation**
   - Components without docs won't get used
   - Include examples and code snippets

6. **Not considering maintenance**
   - Plan for updates and versioning
   - Design systems require ongoing investment

7. **One-size-fits-all approach**
   - Allow for customization
   - Support edge cases

8. **Ignoring accessibility**
   - Build accessibility in from the start
   - Test with real assistive technologies

---

## Success Metrics

**Efficiency**
- Time to design new feature
- Time to develop new feature
- Reuse rate of components

**Consistency**
- Design consistency score (audits)
- Number of unique button styles (should decrease)

**Adoption**
- Percentage of products using design system
- Number of active contributors
- Component usage analytics

**Quality**
- Accessibility audit scores
- User satisfaction (NPS)
- Bug reports related to design system

**Impact**
- Faster time-to-market
- Reduced design debt
- Improved cross-team collaboration

---

## Resources

**Books**
- *Design Systems* by Alla Kholmatova
- *Atomic Design* by Brad Frost
- *Modular Web Design* by Nathan Curtis

**Articles**
- [Design Systems 101](https://www.nngroup.com/articles/design-systems-101/) — Nielsen Norman Group
- [Figma: What is a Design System?](https://www.figma.com/blog/design-systems-101-what-is-a-design-system/)

**Communities**
- Design Systems Slack
- Design Systems Repo
- Figma Community

**Tools**
- [Style Dictionary](https://amzn.github.io/style-dictionary/)
- [Storybook](https://storybook.js.org/)
- [Chromatic](https://www.chromatic.com/)

---

## Scale Craft

Practical patterns for design systems that serve large, diverse user bases. These decisions compound: a wrong call in density or component API at token-rollout time costs weeks to undo.

### Density modes

Three-mode pattern: **comfortable / default / compact**. Pick a per-surface scope — not per-component.

| Mode | Row height | Padding (block) | Icon size | Body font size |
|------|-----------|-----------------|-----------|----------------|
| Comfortable | 52px | 16px | 20px | 14px |
| Default | 40px | 12px | 16px | 13px |
| Compact | 32px | 8px | 14px | 12px |

**Token examples**

```json
{
  "density": {
    "row-height": {
      "$value": "40px",
      "$type": "dimension",
      "$extensions": {
        "mode": {
          "comfortable": "52px",
          "compact": "32px"
        }
      }
    },
    "padding-block": {
      "$value": "12px",
      "$type": "dimension",
      "$extensions": {
        "mode": {
          "comfortable": "16px",
          "compact": "8px"
        }
      }
    }
  }
}
```

**Storage**: user preference → account settings, not `localStorage`. Syncs across devices; survives logout.

**Mixed-density trap**: a compact data table nested inside a comfortable page layout creates a jarring seam. Assign density at surface scope (table = compact, modal = default, reading view = comfortable) and document the mapping explicitly in the handoff. Never mix modes within the same surface.

**Real-world references**:
- Linear: compact default — power users prefer density; comfortable opt-in in settings
- Notion: comfortable default — reading-focused, whitespace is intentional
- Gmail: compact toggle in Display settings — shipped density modes before the term existed

---

### Component API design

**Boolean prop explosion** is the canonical smell. More than three booleans on a single component is a signal to split.

| Anti-pattern | Refactored |
|---|---|
| `<Button isPrimary isLarge isDanger isLoading isDisabled>` | `<Button variant="destructive" size="lg" loading>` |
| `<Input isLarge isReadOnly hasError isRequired>` | `<Input size="lg" readOnly state="error" required>` |

**Composition over props** (Headless UI / Radix pattern): expose a slot hierarchy rather than a monolithic component.

```jsx
// Instead of <Dialog title="..." footer={<>...</>} open={...} onClose={...}>
<Dialog.Root open={isOpen} onOpenChange={setOpen}>
  <Dialog.Trigger asChild>
    <Button>Open</Button>
  </Dialog.Trigger>
  <Dialog.Content>
    <Dialog.Title>Confirm deletion</Dialog.Title>
    <Dialog.Description>This cannot be undone.</Dialog.Description>
    <Dialog.Footer>
      <Dialog.Close asChild><Button variant="secondary">Cancel</Button></Dialog.Close>
      <Button variant="destructive" onClick={handleConfirm}>Delete</Button>
    </Dialog.Footer>
  </Dialog.Content>
</Dialog.Root>
```

**Polymorphic `as` prop** — renders as any element without subclassing:

```jsx
<Button as="a" href="/dashboard">Go to dashboard</Button>
<Button as={Link} to="/settings">Settings</Button>
```

**Slot pattern** — named regions for layout flexibility without prop drilling:

```jsx
<Card>
  <Card.Header>Monthly summary</Card.Header>
  <Card.Content><Chart /></Card.Content>
  <Card.Footer><Button>Export</Button></Card.Footer>
</Card>
```

**Variants by enum, not booleans**: `variant="primary" | "secondary" | "destructive" | "ghost"`. Enum variants are exhaustive, documentable in Storybook, and type-safe — booleans are not.

---

### RTL layout decisions at design time

RTL is a **design decision**, not an implementation step. Decide before token rollout; retrofitting doubles the cost.

**Logical properties** — use these from day one:

```css
/* RTL-safe */
margin-inline-start: var(--spacing-3);
padding-inline: var(--spacing-4);
border-inline-end: 1px solid var(--color-border);

/* Not RTL-safe */
margin-left: var(--spacing-3);
padding-left: var(--spacing-4);
border-right: 1px solid var(--color-border);
```

**Icon flip decision table**:

| Icon | Flip in RTL? | Rationale |
|------|-------------|-----------|
| Chevron right / left | Yes | Indicates direction of reading flow |
| Back arrow | Yes | Back = opposite of reading direction |
| Undo / redo arrows | Yes | Tied to reading direction |
| Sort ascending / descending indicator | Yes | Column order reverses |
| Clock / circular progress | No | Rotation is universal |
| Search magnifier (with handle) | No | Handle position is conventional |
| Media play button | No | Audio/video playback is LTR-universal |
| Warning / info icon | No | Shape carries meaning, not direction |

**Text alignment**: use `text-align: start` / `end`, never `left` / `right` in design tokens.

**Number direction**: numerals always render LTR even in RTL interfaces. `42%`, `$1,200`, `3 items` — leave these alone.

**Bidirectional text mixing**: an English brand name inside Arabic copy needs explicit Unicode bidi marks or a `dir="ltr"` wrapper to prevent mirroring:

```html
<!-- Arabic sentence containing an LTR brand name -->
<p dir="rtl">مرحبًا بك في <span dir="ltr">TaxAdvisor</span></p>
```

---

### i18n text expansion

Design button copy and labels at the **longest expected locale**, not English. English is unusually short.

| Language | Expansion vs. English | Notes |
|----------|-----------------------|-------|
| German | +30–40% | Compound nouns; "Settings" → "Einstellungen" |
| Russian | +30–50% | Full words, minimal abbreviation |
| French | +15–30% | Articles add length; "Sign in" → "Se connecter" |
| Japanese | −10% | Shorter character count but breaks word-wrap assumptions (no spaces) |
| Chinese (Simplified) | −20–30% | Very dense glyphs; no word boundaries |

**Practical rules**:

- Design buttons with the German or Russian string in mind; English will have extra breathing room, which is fine
- Never hardcode button widths — let content drive size within min/max bounds
- `overflow: hidden` + `text-overflow: ellipsis` on button labels is always a bug, not a fix
- Line-height assumptions break in Japanese/Chinese — test CJK strings in every text component

**Pseudolocalization before real strings ship**: use an accent-extension tool (e.g., `[Ȧȧȧ čček ƀůƭƭǿƞ]`) to surface truncation, broken layouts, and hardcoded widths before localized strings arrive. Run it in CI.

```bash
# Example: pseudolocalize a JSON strings file
npx pseudolocale --input src/locales/en.json --output src/locales/ps.json
```

---

### Motion choreography across flows

**One transition per gesture** — a list-tap to detail view is one movement, not three independent fades.

| Principle | Correct | Anti-pattern |
|-----------|---------|--------------|
| Single matched transition | Hero card morphs to detail header | Card fades out + header fades in + content slides up simultaneously |
| Direction consistency | Back navigation reverses forward animation | Back uses the same slide-in-from-right as forward |
| Hierarchy sequencing | Hero element animates first; supporting content follows | All elements animate in parallel, same duration |
| Reduced-motion parity | Every choreography has a `prefers-reduced-motion` equivalent | Reduced-motion just disables animation, removing spatial context entirely |

**Hierarchy sequence pattern**:
```css
/* Hero enters first */
.detail-hero    { animation: slide-up 220ms ease-out; }
/* Supporting content staggers in */
.detail-meta    { animation: fade-in 180ms ease-out 80ms both; }
.detail-body    { animation: fade-in 180ms ease-out 140ms both; }
.detail-actions { animation: fade-in 180ms ease-out 200ms both; }

@media (prefers-reduced-motion: reduce) {
  .detail-hero,
  .detail-meta,
  .detail-body,
  .detail-actions { animation: none; }
}
```

**Real-world references**:
- iOS push/pop: content slides in from right, nav title crossfades, back gesture reverses exactly
- Linear list-to-detail: single shared-element transition on the row, no extra fades
- Things 3 task expansion: task row expands in-place; related tasks compress; single coordinated move

**Anti-pattern**: every state change has its own motion — hover animation, open animation, content-load animation, badge animation — all competing for attention. Motion should orient, not decorate.

---

### Elevation-aware color tokens

Elevation in modern systems is expressed through **color shift**, not just shadow depth.

**Surface token layer model**:

```json
{
  "surface": {
    "1": { "$value": "#ffffff", "$extensions": { "mode": { "dark": "#1a1a1a" } } },
    "2": { "$value": "#f5f5f5", "$extensions": { "mode": { "dark": "#242424" } } },
    "3": { "$value": "#ebebeb", "$extensions": { "mode": { "dark": "#2e2e2e" } } }
  }
}
```

- **Light mode**: surfaces darken as they elevate (cards on background, modals on cards)
- **Dark mode**: surfaces lighten as they elevate — this is the correct dark mode behavior, opposite of light

**Material 3 tonal elevation**: elevation adds a color tint from the primary color on top of the surface color, not a shadow. Higher elevation = more primary color mixed in. This provides depth without requiring heavy shadows.

**Border-as-elevation** (Linear dark mode pattern): on very dark surfaces, a subtle `1px` border (`border: 1px solid rgba(255,255,255,0.08)`) communicates card boundaries more cleanly than a shadow, which loses contrast on dark backgrounds.

**Rules**:
- Never stack opaque shadows on translucent/frosted-glass backgrounds — the shadow renders incorrectly through the blur
- Use `box-shadow` only when the surface is fully opaque
- For translucent surfaces (iOS vibrancy, glassmorphism), use border + backdrop-filter, not shadow

**Real-world references**:
- Material 3: tonal elevation — color shifts replace shadow for most elevation levels
- Apple: `NSVisualEffectView` / `UIVisualEffectView` with vibrancy; backdrop-filter on web
- Linear dark mode: flat cards, `1px` border, no shadow — elevation implied purely by color difference
