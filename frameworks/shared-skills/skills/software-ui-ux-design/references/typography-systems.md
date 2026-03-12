# Typography Systems

Comprehensive guide to building systematic, accessible, and responsive typography for digital products. Covers type scales, font pairing, variable fonts, spacing rules, vertical rhythm, web font loading, platform-specific conventions, accessibility requirements, and design token integration. Typography is the primary interface layer -- it carries 90%+ of content in most applications.

**Last Updated**: March 2026

---

## Type Scale Systems

A type scale is a set of predefined font sizes that maintain visual harmony through consistent proportional relationships.

### Scale Types

| Scale Type | Ratio | Sizes (base 16px) | Best For |
|-----------|-------|-------------------|----------|
| **Minor Second** | 1.067 | 14, 15, 16, 17, 18 | Dense UI, data-heavy apps |
| **Major Second** | 1.125 | 13, 14, 16, 18, 20, 23 | Body-heavy content, documentation |
| **Minor Third** | 1.200 | 11, 13, 16, 19, 23, 28 | General purpose, balanced hierarchy |
| **Major Third** | 1.250 | 10, 13, 16, 20, 25, 31 | Marketing sites, clear hierarchy |
| **Perfect Fourth** | 1.333 | 9, 12, 16, 21, 28, 38 | Editorial, strong headlines |
| **Golden Ratio** | 1.618 | 8, 10, 16, 26, 42, 68 | Very dramatic hierarchy (use sparingly) |

### Modular Scale Implementation

```css
:root {
  --type-ratio: 1.25;  /* Major Third */
  --type-base: 1rem;   /* 16px */

  --type-xs:   calc(var(--type-base) / var(--type-ratio));        /* 12.8px */
  --type-sm:   calc(var(--type-base) / 1.125);                    /* 14.2px */
  --type-md:   var(--type-base);                                  /* 16px   */
  --type-lg:   calc(var(--type-base) * var(--type-ratio));        /* 20px   */
  --type-xl:   calc(var(--type-base) * var(--type-ratio) * var(--type-ratio));  /* 25px */
  --type-2xl:  calc(var(--type-base) * var(--type-ratio) * var(--type-ratio) * var(--type-ratio)); /* 31.25px */
  --type-3xl:  calc(var(--type-base) * var(--type-ratio) * var(--type-ratio) * var(--type-ratio) * var(--type-ratio)); /* 39px */
}
```

### Fluid Typography

Fluid type scales smoothly between a minimum and maximum size based on viewport width, eliminating breakpoint jumps.

```css
/* Fluid type with clamp() */
:root {
  /* clamp(minimum, preferred, maximum) */
  --type-body:    clamp(1rem,    0.95rem + 0.25vw,  1.125rem);   /* 16-18px */
  --type-h3:      clamp(1.25rem, 1.1rem + 0.75vw,   1.5rem);    /* 20-24px */
  --type-h2:      clamp(1.5rem,  1.2rem + 1.5vw,    2.25rem);   /* 24-36px */
  --type-h1:      clamp(2rem,    1.5rem + 2.5vw,    3.5rem);    /* 32-56px */
  --type-display: clamp(2.5rem,  1.75rem + 3.75vw,  5rem);      /* 40-80px */
}

h1 { font-size: var(--type-h1); }
h2 { font-size: var(--type-h2); }
h3 { font-size: var(--type-h3); }
body { font-size: var(--type-body); }
```

### Custom Scale (Non-Ratio)

Some design systems define arbitrary sizes that do not follow a mathematical ratio. This is acceptable when the sizes are tested across real content.

```json
{
  "fontSize": {
    "xs":      "0.75rem",
    "sm":      "0.875rem",
    "base":    "1rem",
    "lg":      "1.125rem",
    "xl":      "1.25rem",
    "2xl":     "1.5rem",
    "3xl":     "1.875rem",
    "4xl":     "2.25rem",
    "5xl":     "3rem",
    "display": "3.75rem"
  }
}
```

---

## Font Pairing Strategies

### Pairing Principles

| Strategy | How It Works | Example |
|----------|-------------|---------|
| **Complementary** | Same designer or foundry, designed to work together | Inter (body) + Inter Display (headings) |
| **Contrasting structure** | Serif headings + sans-serif body (or reverse) | Playfair Display (headings) + Source Sans 3 (body) |
| **Shared skeleton** | Different families with similar x-height and proportions | Lora (serif) + Merriweather Sans |
| **Superfamily** | One family covering multiple classifications | Roboto + Roboto Slab + Roboto Mono |
| **Monospace accent** | Monospace for code/data, proportional for body | JetBrains Mono (code) + system sans-serif (body) |

### Tested Pairings

| Heading Font | Body Font | Style | Use Case |
|-------------|-----------|-------|----------|
| Fraunces | Inter | Classic + modern | Marketing, editorial |
| Space Grotesk | Outfit | Geometric consistency | SaaS dashboards |
| DM Serif Display | DM Sans | High contrast | Landing pages |
| Source Serif 4 | Source Sans 3 | Adobe superfamily | Documentation, long-form |
| Sora | Noto Sans | Clean, wide support | International products |

### Anti-Patterns in Font Pairing

| Mistake | Problem | Fix |
|---------|---------|-----|
| More than 2-3 font families | Visual chaos, slow loading | Limit to 2 families (heading + body) + 1 mono |
| Two similar sans-serifs | Looks like a mistake, not a choice | Use contrasting categories (serif vs sans) |
| Decorative font for body text | Poor readability at small sizes | Reserve decorative fonts for display use only |
| Mismatched x-heights | Feels unbalanced side by side | Choose fonts with similar x-height proportions |

---

## Variable Fonts and Responsive Typography

### Variable Font Axes

| Axis | Tag | Description | Example Range |
|------|-----|-------------|---------------|
| Weight | `wght` | Thin to Black | 100-900 |
| Width | `wdth` | Condensed to Expanded | 75-125 |
| Slant | `slnt` | Upright to oblique | -12 to 0 |
| Italic | `ital` | Roman to italic | 0 or 1 |
| Optical size | `opsz` | Text to display optimization | 8-144 |
| Grade | `GRAD` | Weight without layout shift | -200 to 150 |

### Variable Font Implementation

```css
/* Loading a variable font */
@font-face {
  font-family: 'Inter Variable';
  src: url('/fonts/InterVariable.woff2') format('woff2-variations');
  font-weight: 100 900;
  font-display: swap;
  font-style: normal;
}

/* Using weight axis */
body { font-variation-settings: 'wght' 400; }
strong { font-variation-settings: 'wght' 700; }

/* Or use standard font-weight (preferred) */
body { font-weight: 400; }
h1 { font-weight: 750; }  /* Non-standard weight, only possible with variable fonts */

/* Responsive weight: slightly heavier on small screens for readability */
@media (max-width: 640px) {
  body { font-weight: 420; }
}

/* Dark mode: slightly lighter weight to compensate for halation */
@media (prefers-color-scheme: dark) {
  body { font-weight: 380; }
}
```

### Performance Benefit

| Approach | Requests | Total Size (typical) |
|----------|----------|---------------------|
| Static: Regular + Bold + Italic + Bold Italic | 4 files | 240-400 KB |
| Variable: single file covering all axes | 1 file | 150-250 KB |

---

## Line Height, Letter Spacing, and Measure

### Line Height (Leading)

| Content Type | Line Height | Rationale |
|-------------|-------------|-----------|
| Body text (14-18px) | 1.5-1.6 | WCAG SC 1.4.12 requires support for 1.5x |
| Headings (24px+) | 1.1-1.3 | Large text needs less leading; tight leading signals hierarchy |
| Captions / small text (12px) | 1.4-1.5 | Small text needs more relative space |
| UI labels (14px) | 1.25-1.4 | Compact but readable |
| Code blocks | 1.5-1.7 | Generous spacing aids scanning |

### Letter Spacing (Tracking)

| Context | Letter Spacing | Notes |
|---------|---------------|-------|
| Body text | 0 (default) | Most well-designed fonts have correct spacing at body sizes |
| All-caps text | +0.05em to +0.1em | Uppercase needs more tracking for readability |
| Large headings (48px+) | -0.01em to -0.03em | Tight tracking at display sizes is conventional |
| Small text (< 12px) | +0.02em to +0.04em | Slight loosening improves legibility |

### Measure (Line Length)

| Measure | Characters | Best For |
|---------|------------|----------|
| Narrow | 45-55 ch | Narrow columns, sidebars, mobile |
| Optimal | 55-75 ch | Body text, articles, documentation |
| Wide | 75-90 ch | Code blocks, data tables |
| Too wide | > 90 ch | Avoid -- eye loses track returning to next line |

```css
/* Optimal measure */
.prose {
  max-width: 65ch;
  margin-inline: auto;
}

/* Code blocks can be wider */
.prose pre {
  max-width: 85ch;
}
```

---

## Vertical Rhythm and Baseline Grids

### Vertical Rhythm

Vertical rhythm means all spacing values derive from a common base unit, so text and whitespace align to a predictable grid.

```css
:root {
  --baseline: 0.5rem;  /* 8px base unit */
}

body {
  font-size: 1rem;
  line-height: calc(var(--baseline) * 3); /* 24px */
}

h1 {
  font-size: 2.25rem;
  line-height: calc(var(--baseline) * 5); /* 40px */
  margin-top: calc(var(--baseline) * 6);  /* 48px */
  margin-bottom: calc(var(--baseline) * 3); /* 24px */
}

h2 {
  font-size: 1.5rem;
  line-height: calc(var(--baseline) * 4); /* 32px */
  margin-top: calc(var(--baseline) * 5);  /* 40px */
  margin-bottom: calc(var(--baseline) * 2); /* 16px */
}

p {
  margin-bottom: calc(var(--baseline) * 3); /* 24px = one line of body text */
}

/* Spacing scale built on baseline */
.space-1 { margin: calc(var(--baseline) * 1); }  /*  8px */
.space-2 { margin: calc(var(--baseline) * 2); }  /* 16px */
.space-3 { margin: calc(var(--baseline) * 3); }  /* 24px */
.space-4 { margin: calc(var(--baseline) * 4); }  /* 32px */
.space-6 { margin: calc(var(--baseline) * 6); }  /* 48px */
```

### When Strict Baseline Grids Break Down

| Situation | Problem | Pragmatic Fix |
|-----------|---------|---------------|
| Images and media | Arbitrary heights break the grid | Allow media to break rhythm; re-establish after |
| Component spacing | Padding inside cards does not align to grid | Use baseline multiples for outer margins, relax inner spacing |
| Different line heights per element | Headings at 1.2 vs body at 1.5 | Match heading `margin-bottom` to restore rhythm |

---

## Web Font Loading Strategies

### Loading Behaviors

| Strategy | Abbreviation | Behavior | User Experience |
|----------|-------------|----------|-----------------|
| Flash of Invisible Text | FOIT | Browser hides text until font loads | Blank text for up to 3 seconds (bad) |
| Flash of Unstyled Text | FOUT | Browser shows fallback font, swaps when ready | Text always visible, brief visual shift |
| Flash of Faux Text | FOFT | Load regular weight first, faux-bold until bold loads | Reduces total swap count |

### `font-display` Values

| Value | Behavior | Best For |
|-------|----------|----------|
| `swap` | Immediate fallback, swap when loaded | Body text -- content must be readable immediately |
| `optional` | Brief block, use font only if cached | Decorative or non-essential fonts |
| `fallback` | Short block (~100ms), short swap (~3s) | Balance between swap and optional |
| `block` | Long invisible block (up to 3s) | Icon fonts (but prefer SVG icons) |
| `auto` | Browser default (usually `block`) | Avoid using explicitly |

### Optimal Loading Pattern

```html
<!-- 1. Preload critical fonts -->
<link
  rel="preload"
  href="/fonts/InterVariable.woff2"
  as="font"
  type="font/woff2"
  crossorigin
/>

<!-- 2. Font-face with swap -->
<style>
  @font-face {
    font-family: 'Inter Variable';
    src: url('/fonts/InterVariable.woff2') format('woff2-variations');
    font-weight: 100 900;
    font-display: swap;
  }
</style>

<!-- 3. Size-adjusted fallback to minimize layout shift -->
<style>
  @font-face {
    font-family: 'Inter Fallback';
    src: local('Arial');
    ascent-override: 90%;
    descent-override: 22%;
    line-gap-override: 0%;
    size-adjust: 107%;
  }

  body {
    font-family: 'Inter Variable', 'Inter Fallback', system-ui, sans-serif;
  }
</style>
```

### Font Subsetting

| Subset | Characters | Size Reduction |
|--------|-----------|---------------|
| Latin only | ~230 glyphs | 60-80% smaller than full |
| Latin + Latin Extended | ~600 glyphs | 40-60% smaller |
| Full Unicode | 2000+ glyphs | Full size |

```bash
# Subset with pyftsubset (fonttools)
pyftsubset Inter.woff2 \
  --output-file=Inter-subset.woff2 \
  --flavor=woff2 \
  --unicodes="U+0000-007F,U+00A0-00FF,U+2000-206F"
```

---

## Platform-Specific Typography

### iOS Dynamic Type

```swift
// SwiftUI: use built-in text styles for Dynamic Type
Text("Headline")
    .font(.headline)         // Scales with user settings

Text("Body text")
    .font(.body)             // Scales with user settings

// Custom font with Dynamic Type scaling
Text("Custom")
    .font(.custom("Inter", size: 16, relativeTo: .body))
```

| iOS Text Style | Default Size | Scales With |
|---------------|-------------|-------------|
| `.largeTitle` | 34pt | Accessibility sizes |
| `.title` | 28pt | Accessibility sizes |
| `.headline` | 17pt semi-bold | Accessibility sizes |
| `.body` | 17pt | Accessibility sizes |
| `.callout` | 16pt | Accessibility sizes |
| `.footnote` | 13pt | Accessibility sizes |
| `.caption` | 12pt | Accessibility sizes |

### Android sp Units

```kotlin
// Compose: sp scales with user font size preference
Text(
    text = "Headline",
    style = MaterialTheme.typography.headlineMedium  // Uses sp internally
)

// Custom sp values
Text(
    text = "Custom",
    fontSize = 16.sp  // Scales with system font size
)
```

| Unit | Scales With User Setting | Use For |
|------|-------------------------|---------|
| `sp` | Yes | All text |
| `dp` | No | Non-text elements only |

### Web rem/em

| Unit | Relative To | Best For |
|------|-------------|----------|
| `rem` | Root `<html>` font-size | Global sizing, spacing, type scale |
| `em` | Parent element font-size | Component-scoped sizing (padding relative to text) |
| `px` | Absolute | Borders, shadows (should not scale) |
| `ch` | Width of "0" character | Line length (measure) |
| `lh` | Line height of element | Vertical spacing relative to text rhythm |

```css
/* rem for type scale, em for component-relative spacing */
h2 {
  font-size: 1.5rem;       /* Relative to root */
  margin-bottom: 0.5em;    /* Relative to this heading's size */
  padding: 0.75em 1em;     /* Scales with heading size */
}

/* Never set root font-size in px -- breaks user preferences */
html {
  font-size: 100%; /* = user's preferred size, usually 16px */
}
```

---

## Typography Accessibility

### Minimum Sizes

| Context | Minimum Size | Recommended |
|---------|-------------|-------------|
| Body text (web) | 16px (1rem) | 16-18px |
| Body text (mobile) | 16px | 16-17px (prevents iOS zoom on focus) |
| Secondary text / captions | 12px | 13-14px |
| Button labels | 14px | 16px |
| Form input text | 16px | 16px (prevents mobile zoom) |
| Navigation labels | 14px | 14-16px |

### WCAG Text Spacing Requirements (SC 1.4.12)

Content must remain readable and functional when users override text spacing to at least these values:

| Property | Minimum Override |
|----------|-----------------|
| Line height | 1.5x the font size |
| Paragraph spacing | 2x the font size |
| Letter spacing | 0.12em |
| Word spacing | 0.16em |

```css
/* Test your layout with WCAG text spacing overrides */
.wcag-text-spacing-test * {
  line-height: 1.5 !important;
  letter-spacing: 0.12em !important;
  word-spacing: 0.16em !important;
}
.wcag-text-spacing-test p {
  margin-bottom: 2em !important;
}
```

### Dyslexia-Friendly Typography

| Guideline | Implementation |
|-----------|---------------|
| Use sans-serif fonts with distinct letterforms | Inter, Atkinson Hyperlegible, Lexie Readable |
| Avoid fonts where b/d, p/q, I/l/1 are mirrors | Test with "Illicit bdpq 1Il" string |
| Generous line height (1.5+) | `line-height: 1.5` minimum |
| Generous letter spacing | `letter-spacing: 0.05em` for improved readability |
| Left-align text (do not justify) | `text-align: left` -- justified text creates rivers |
| Limit line length | `max-width: 65ch` |
| Adequate paragraph spacing | `margin-bottom: 1.5em` between paragraphs |
| Avoid all-caps for body text | Reserve for short labels or acronyms |

### Atkinson Hyperlegible Example

```css
@font-face {
  font-family: 'Atkinson Hyperlegible';
  src: url('/fonts/AtkinsonHyperlegible-Regular.woff2') format('woff2');
  font-weight: 400;
  font-display: swap;
}

/* Offer as an accessibility preference toggle */
[data-font="accessible"] body {
  font-family: 'Atkinson Hyperlegible', sans-serif;
  letter-spacing: 0.03em;
  word-spacing: 0.05em;
}
```

---

## Design Token Integration

### Typography Token Structure

```json
{
  "typography": {
    "fontFamily": {
      "heading": { "value": "'Space Grotesk', sans-serif" },
      "body":    { "value": "'Outfit', sans-serif" },
      "mono":    { "value": "'JetBrains Mono', monospace" }
    },
    "fontSize": {
      "xs":      { "value": "0.75rem" },
      "sm":      { "value": "0.875rem" },
      "base":    { "value": "1rem" },
      "lg":      { "value": "1.125rem" },
      "xl":      { "value": "1.25rem" },
      "2xl":     { "value": "1.5rem" },
      "3xl":     { "value": "1.875rem" },
      "4xl":     { "value": "2.25rem" }
    },
    "fontWeight": {
      "regular":  { "value": 400 },
      "medium":   { "value": 500 },
      "semibold": { "value": 600 },
      "bold":     { "value": 700 }
    },
    "lineHeight": {
      "tight":    { "value": 1.25 },
      "normal":   { "value": 1.5 },
      "relaxed":  { "value": 1.625 }
    },
    "letterSpacing": {
      "tight":    { "value": "-0.02em" },
      "normal":   { "value": "0" },
      "wide":     { "value": "0.05em" },
      "caps":     { "value": "0.08em" }
    }
  }
}
```

### Composite Typography Tokens

```json
{
  "textStyle": {
    "display": {
      "value": {
        "fontFamily": "{typography.fontFamily.heading}",
        "fontSize": "{typography.fontSize.4xl}",
        "fontWeight": "{typography.fontWeight.bold}",
        "lineHeight": "{typography.lineHeight.tight}",
        "letterSpacing": "{typography.letterSpacing.tight}"
      }
    },
    "heading": {
      "value": {
        "fontFamily": "{typography.fontFamily.heading}",
        "fontSize": "{typography.fontSize.2xl}",
        "fontWeight": "{typography.fontWeight.semibold}",
        "lineHeight": "{typography.lineHeight.tight}",
        "letterSpacing": "{typography.letterSpacing.normal}"
      }
    },
    "body": {
      "value": {
        "fontFamily": "{typography.fontFamily.body}",
        "fontSize": "{typography.fontSize.base}",
        "fontWeight": "{typography.fontWeight.regular}",
        "lineHeight": "{typography.lineHeight.normal}",
        "letterSpacing": "{typography.letterSpacing.normal}"
      }
    },
    "caption": {
      "value": {
        "fontFamily": "{typography.fontFamily.body}",
        "fontSize": "{typography.fontSize.sm}",
        "fontWeight": "{typography.fontWeight.regular}",
        "lineHeight": "{typography.lineHeight.normal}",
        "letterSpacing": "{typography.letterSpacing.wide}"
      }
    }
  }
}
```

### Generating CSS from Tokens

```javascript
// Style Dictionary config for typography tokens
module.exports = {
  source: ['tokens/**/*.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'build/css/',
      files: [{
        destination: 'typography.css',
        format: 'css/variables',
        filter: (token) => token.attributes.category === 'typography',
      }],
    },
  },
};
```

---

## Typography Checklist

- [ ] Type scale defined with consistent ratios or intentional custom sizes
- [ ] No more than 2-3 font families loaded
- [ ] Body text is 16px minimum
- [ ] Line height is 1.5 or greater for body text
- [ ] Line length (measure) is 55-75 characters for prose
- [ ] `font-display: swap` set on all `@font-face` declarations
- [ ] Critical fonts preloaded with `<link rel="preload">`
- [ ] Fallback font size-adjusted to minimize CLS
- [ ] Layout survives WCAG text spacing overrides (SC 1.4.12)
- [ ] Distinct letterforms for I, l, 1, 0, O (test with "Illicit 1Il0O")
- [ ] No justified text in body content
- [ ] All-caps text has increased letter spacing
- [ ] Variable font used where possible (single file, multiple weights)
- [ ] Typography tokens defined and consumed by components
- [ ] iOS Dynamic Type / Android sp units used in native apps

---

## References

- [Butterick, Matthew. Practical Typography.](https://practicaltypography.com/)
- [Spencer, Herbert. The Visible Word. 1969.](https://en.wikipedia.org/wiki/The_Visible_Word)
- [Google Fonts — Variable Fonts Guide](https://fonts.google.com/knowledge/using_variable_fonts_on_the_web)
- [MDN — Variable Fonts Guide](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_fonts/Variable_fonts_guide)
- [Web.dev — Best Practices for Fonts](https://web.dev/articles/font-best-practices)
- [WCAG 2.2 SC 1.4.12 — Text Spacing](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing.html)
- [Apple HIG — Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
- [Material Design 3 — Typography](https://m3.material.io/styles/typography/overview)
- [Style Dictionary Documentation](https://amzn.github.io/style-dictionary/)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview and interaction checklist
- [design-systems.md](design-systems.md) — Token architecture and design system structure
- [wcag-accessibility.md](wcag-accessibility.md) — WCAG 2.2 text and contrast requirements
- [dark-mode-theming.md](dark-mode-theming.md) — Font weight adjustment in dark mode
- [performance-ux-vitals.md](performance-ux-vitals.md) — Font loading impact on CLS and LCP
