# Design Systems

A design system is a set of reusable components, tokens and usage rules that teams assemble into products; it is the single source of truth for design and engineering. This file covers how to build one, token format, multi-platform theming, governance and scale decisions. Choosing a component base is in [component-library-comparison.md](component-library-comparison.md); token change control is in [design-token-governance.md](design-token-governance.md); code-level component implementation is in [software-frontend](../../software-frontend/SKILL.md).

## Table of Contents

- [Building a Design System](#building-a-design-system)
- [Design Tokens (Design Tokens Community Group Format)](#design-tokens-design-tokens-community-group-format)
- [Multi-Platform Design Systems](#multi-platform-design-systems)
- [Governance and Maintenance](#governance-and-maintenance)
- [Official Design Systems](#official-design-systems)
- [Figma Operations (Library Hygiene)](#figma-operations-library-hygiene)
- [Common Pitfalls](#common-pitfalls)
- [Success Metrics](#success-metrics)
- [Resources](#resources)
- [Scale Craft](#scale-craft)

---

## Building a Design System

A style guide documents visual rules; a component library is coded UI; a design system is both plus the tokens, patterns, documentation and governance that keep them in sync. Build in this order.

### 1. Audit and inventory

Screenshot every major screen and list what exists: how many button styles, how many shades of each brand colour, which spacing values, which patterns are duplicated. The count of near-duplicates is the baseline the system should shrink.

### 2. Define foundations as tokens

| Foundation | Decide | Rule |
|------------|--------|------|
| Colour | Primary, secondary, neutral and semantic (success, warning, error, info) families, each a shade scale | Name by function, not appearance; check text pairs with `../scripts/contrast_check.py`; define light and dark values together ([dark-mode-theming.md](dark-mode-theming.md)). Commit to a dominant colour instead of an even spread; see [frontend-aesthetics.md](frontend-aesthetics.md#principle-2-committed-color--themes) |
| Typography | A modular type scale (for example a 1.2 or 1.25 ratio), at most three families, three or four weights | Body line height about 1.4-1.6; make the typeface a deliberate brand choice, not a default ([frontend-aesthetics.md](frontend-aesthetics.md#principle-1-distinctive-typography), [typography-systems.md](typography-systems.md)) |
| Spacing | A 4 px or 8 px base grid | Every padding, margin and gap comes from the scale |
| Elevation | Three or four levels: flat, raised (cards), floating (menus, tooltips), modal | Tie shadows to levels, not to components; see [Elevation-aware color tokens](#elevation-aware-color-tokens) for dark mode |
| Radius | A small scale plus "full" | One radius family per product |
| Breakpoints | Named widths for the layouts you actually design | Design content-first; add a breakpoint where the layout breaks, not per device |
| Motion | Durations and easings as tokens | See [motion-design.md](motion-design.md) |

### 3. Design components

Every component defines: structure (markup), variants, states (default, hover, focus-visible, active, disabled, loading, error), props, accessibility (role, name, keyboard, focus) and usage guidance. Start with the components the audit shows are used most (typically button, input, select, checkbox and radio, card, modal, toast, tabs, table) rather than a complete catalogue.

### 4. Document patterns

Patterns combine components into answers for recurring jobs: layouts, forms ([form-design-patterns.md](form-design-patterns.md)), empty, loading and error states, and surface recipes ([surface-type-recipes.md](surface-type-recipes.md)).

### 5. Write the documentation page

One page per component, in this order: what it is and when to use it (and when not), variants with live examples, a code example using the real package, props, accessibility notes (keyboard, screen-reader name, contrast), do and don't examples, and related components. A component with no page will not be adopted.

---

## Design Tokens (Design Tokens Community Group Format)

**Reference**: [Design Tokens Technical Reports 2025.10](https://tr.designtokens.org/)

The Design Tokens Community Group (DTCG) — a W3C Community Group, not a Working Group — announced 2025.10 as the **first stable version** of the Format Module, after several years of draft-only reports. Stable here means production-ready and safe to build tooling against, not a formal W3C Recommendation; DTCG specs are never W3C Recommendations because Community Group output sits outside the W3C standards track. Tool support for 2025.10 varies (Style Dictionary's own DTCG page describes 2025.10 support as incomplete and in progress); check each tool's DTCG support notes before promising a lossless round trip.

**Definition**: Design tokens are named entities that store visual design attributes (colors, spacing, etc.) in a platform-agnostic format.

**Benefits**:

- Single source of truth
- Multi-platform consistency
- Easy theming
- Programmatic updates

### File Format Reference (2025.10 Reports)

Design tokens use `.tokens.json` extension with standardized properties. The stable 2025.10 format requires `color` as an object (`colorSpace` + `components`, not a hex string) and `dimension` as an object (`value` + `unit`, not a combined string like `"8px"`) — the older hex-string and `"8px"`-string shorthand from pre-stable drafts is not valid against this spec, even though some tooling still accepts it for convenience:

```json
{
  "color": {
    "primary": {
      "$value": { "colorSpace": "srgb", "components": [0.129, 0.588, 0.953] },
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
      "$value": { "value": 8, "unit": "px" },
      "$type": "dimension"
    },
    "md": {
      "$value": { "value": 16, "unit": "px" },
      "$type": "dimension"
    }
  },
  "typography": {
    "heading-1": {
      "$value": {
        "fontFamily": "Inter",
        "fontSize": { "value": 32, "unit": "px" },
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
          "color": { "colorSpace": "srgb", "components": [0, 0, 0], "alpha": 0.15 },
          "offsetX": { "value": 0, "unit": "px" },
          "offsetY": { "value": 1, "unit": "px" },
          "blur": { "value": 2, "unit": "px" }
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
| `color` | Object: `colorSpace` + `components` (+ optional `alpha`, `hex`) | `{ "colorSpace": "srgb", "components": [1, 0, 0] }` |
| `dimension` | Object: `value` (number) + `unit` (`"px"` or `"rem"`) | `{ "value": 16, "unit": "px" }` |
| `fontFamily` | String or array | `"Inter"`, `["Inter", "sans-serif"]` |
| `fontWeight` | Number or keyword | `700`, `"bold"` |
| `duration` | Object: `value` (number) + `unit` (`"ms"` or `"s"`) | `{ "value": 200, "unit": "ms" }` |
| `cubicBezier` | Array of 4 numbers | `[0.4, 0, 0.2, 1]` |
| `shadow` | Array of shadow objects | See example above |
| `typography` | Composite object | Font family, size, weight, line height |
| `gradient` | Array of color stops | Linear, radial, conic |

The 2025.10 Format Module does not publish a JSON Schema yet (the group is still exploring one), so do not add an invented `$schema` URL to token files.

### Semantic vs. Primitive Tokens

```json
{
  "primitive": {
    "blue-500": { "$value": { "colorSpace": "srgb", "components": [0.129, 0.588, 0.953] }, "$type": "color" },
    "blue-600": { "$value": { "colorSpace": "srgb", "components": [0.098, 0.463, 0.824] }, "$type": "color" }
  },
  "semantic": {
    "color-action-primary": { "$value": "{primitive.blue-500}", "$type": "color" },
    "color-action-primary-hover": { "$value": "{primitive.blue-600}", "$type": "color" }
  }
}
```

### Modes (Light/Dark/High-Contrast)

Do not encode modes as per-token `$extensions` maps. The 2025.10 reports include a separate, stable **Resolver Module**: a resolver document lists token *sets* (files) and *modifiers* with named contexts (for example `light`, `lightHighContrast`, `dark`, `darkHighContrast`), and a tool resolves one concrete token set per chosen context. Keep one file per context-specific override (for example `dark.tokens.json` redefining `color.background` as `{ "colorSpace": "srgb", "components": [0.071, 0.071, 0.071] }`), and add brand themes as a second modifier instead of multiplying files by hand. Check the [Resolver Module](https://www.designtokens.org/tr/2025.10/resolver/) for the exact document syntax.

### Tooling Ecosystem

| Tool | Purpose | Notes |
|------|---------|-------|
| **Style Dictionary** | Transform tokens to CSS/JS/iOS/Android | Widely adopted; check its DTCG page for 2025.10 support status |
| **Tokens Studio for Figma** | Figma plugin for token management | Syncs with JSON files |
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

- **Team**: name owners for visual design, engineering, product prioritisation, content and accessibility; a system with no named owner decays.
- **Contribution model**: centralised (core team owns everything; consistent but a bottleneck), federated (product teams contribute; faster but drifts) or hybrid (core team owns foundations and critical components, others contribute through a documented review). Most organisations beyond one team end up hybrid.
- **Versioning**: semantic versioning, where MAJOR means a breaking API or visual change, MINOR a backward-compatible addition, PATCH a fix. Every release gets a changelog entry listing breaking changes with the migration step, and deprecations get a removal version.
- **Adoption signals**: component usage across products (from code search or analytics), design-to-dev handoff time, audit consistency, contribution activity and consumer satisfaction surveys.

---

## Official Design Systems

When the brief names a platform or public-sector context, the official system usually wins over hand-rolling; the routing table is [Official Design System Required by Brief](component-library-comparison.md#official-design-system-required-by-brief). Check each system's site for its current version and packages before you commit.

| System | Owner | Platforms | Reach for it when |
|--------|-------|-----------|-------------------|
| [Material Design 3](https://m3.material.io/) | Google | Android, Web, Flutter | Android-first products; the Expressive update adds shape and motion range (Google reports users found key elements up to 4x faster in its own studies) |
| [Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/) | Apple | iOS, iPadOS, macOS, watchOS, tvOS, visionOS | Native Apple apps; platform conventions matter more than brand |
| [Carbon](https://carbondesignsystem.com/) | IBM | Web (React and others) | Dense enterprise and data-heavy tools |
| [Polaris](https://polaris.shopify.com/) | Shopify | Web | Apps embedded in the Shopify admin |
| [Fluent 2](https://fluent2.microsoft.design/) | Microsoft | Web, Windows, iOS, Android | Microsoft 365 and Teams extensions, Windows apps |
| [GOV.UK Design System](https://design-system.service.gov.uk/) | UK Government Digital Service | Web | UK public services |
| [USWDS](https://designsystem.digital.gov/) | US General Services Administration | Web | US federal services |

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

- **Starting too big**: ship foundations plus the handful of most-used components, then grow from real demand.
- **Building in isolation**: involve product teams early and solve problems they have, not hypothetical ones.
- **No governance**: without a contribution and review process the system forks inside a year.
- **Undocumented components**: they will not be used; see step 5 above.
- **No maintenance budget**: a design system is a product with ongoing cost, not a project.
- **Rigid one-size-fits-all**: allow documented extension points so teams do not detach and fork.
- **Accessibility as a later pass**: build it into every component's definition and test with assistive technology.

---

## Success Metrics

| Goal | Signal |
|------|--------|
| Efficiency | Time to design and build a new feature; component reuse rate |
| Consistency | Unique variants of the same control found in audits (should fall) |
| Adoption | Share of products on the system; active contributors; component usage |
| Quality | Accessibility audit results; defects attributed to system components |

---

## Resources

- Books: *Design Systems* (Alla Kholmatova), *Atomic Design* (Brad Frost)
- [Design Systems 101](https://www.nngroup.com/articles/design-systems-101/) (NN/g)
- [Design Tokens Community Group reports](https://tr.designtokens.org/)
- Tooling: [Style Dictionary](https://styledictionary.com/) for token transforms, [Storybook](https://storybook.js.org/) for component documentation, and visual-regression tooling for release checks

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

This snippet is conceptual shorthand. In a DTCG 2025.10 file, write each color as a `colorSpace`/`components` object and put the dark values in a dark-context set selected by the Resolver Module (see [Modes](#modes-lightdarkhigh-contrast)), not in `$extensions.mode`.

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
