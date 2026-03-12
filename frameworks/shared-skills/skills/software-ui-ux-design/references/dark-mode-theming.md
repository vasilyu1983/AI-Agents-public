# Dark Mode & Multi-Theme Implementation Guide (Jan 2026)

Practical guide to designing and implementing dark mode and multi-theme systems. Covers color system architecture, platform-specific patterns for iOS, Android, and web, CSS implementation, testing, and common mistakes. Dark mode is no longer optional — users expect it.

---

## Color System Design for Multi-Theme

The foundation of robust theming is a semantic token system. Hard-coded hex values break when themes change; semantic tokens adapt.

### Token Architecture

```text
LAYER 1: Primitive Tokens (raw values)
  blue-50: #eff6ff
  blue-500: #3b82f6
  blue-900: #1e3a5c
  gray-50: #f9fafb
  gray-900: #111827

LAYER 2: Semantic Tokens (intent-based, theme-aware)
  color-surface-primary:     light → gray-50     | dark → gray-900
  color-surface-secondary:   light → white       | dark → #1a1a2e
  color-text-primary:        light → gray-900    | dark → gray-50
  color-text-secondary:      light → gray-600    | dark → gray-400
  color-border-default:      light → gray-200    | dark → gray-700
  color-interactive-primary: light → blue-600    | dark → blue-400
  color-error:               light → red-600     | dark → red-400
  color-success:             light → green-600   | dark → green-400

LAYER 3: Component Tokens (component-specific)
  button-bg-primary:        → color-interactive-primary
  card-bg:                  → color-surface-secondary
  input-border:             → color-border-default
  nav-bg:                   → color-surface-primary
```

### Why Semantic Tokens Matter

| Approach | Light Mode | Dark Mode | Maintenance |
|----------|-----------|-----------|-------------|
| Hard-coded: `color: #111827` | Works | Invisible on dark bg | Must find and change every instance |
| Semantic: `color: var(--text-primary)` | Resolves to dark text | Resolves to light text | Change token mapping once |

### Token Naming Conventions

| Convention | Example | Benefit |
|-----------|---------|---------|
| `{category}-{property}-{variant}` | `color-text-primary` | Clear purpose |
| `{component}-{property}-{state}` | `button-bg-hover` | Component-specific |
| Avoid color names in semantic tokens | `color-danger` not `color-red` | Theme-independent |
| Use consistent suffixes | `-primary`, `-secondary`, `-tertiary` | Predictable scale |

---

## Dark Mode Color Principles

Dark mode is not simply inverting light mode. The correct approach uses elevated surfaces, reduced vibrancy, and careful contrast management.

### Core Principles

| Principle | Light Mode | Dark Mode | Why |
|-----------|-----------|-----------|-----|
| **Background** | White or near-white (#FFFFFF) | Dark gray (#121212 or #1a1a2e) | Pure black (#000000) causes eye strain on OLED |
| **Surface elevation** | Shadows indicate elevation | Lighter surfaces indicate elevation | Shadows are invisible on dark backgrounds |
| **Text** | Dark on light (high contrast) | Light on dark (slightly reduced) | Full white (#FFFFFF) on dark is too harsh; use #E0E0E0 |
| **Primary colors** | Full saturation | Reduced saturation, increased lightness | Saturated colors vibrate on dark backgrounds |
| **Accent colors** | Standard brand colors | Lighter tints of brand colors | Ensure 4.5:1 contrast on dark surfaces |

### Elevation System for Dark Mode

```text
DARK MODE SURFACE ELEVATION:
┌────────────────────────────────────────┐
│ Layer 0 (Background):    #121212       │
│                                        │
│ ┌──────────────────────────────────┐   │
│ │ Layer 1 (Card):       #1E1E1E   │   │  +3% white overlay
│ │                                  │   │
│ │ ┌──────────────────────────┐     │   │
│ │ │ Layer 2 (Dialog):  #232323│    │   │  +5% white overlay
│ │ │                          │    │   │
│ │ │ ┌──────────────────┐     │    │   │
│ │ │ │ Layer 3: #282828 │     │    │   │  +8% white overlay
│ │ │ └──────────────────┘     │    │   │
│ │ └──────────────────────────┘     │   │
│ └──────────────────────────────────┘   │
└────────────────────────────────────────┘

Each elevation level adds a white overlay percentage:
  dp0:  0% overlay   → #121212
  dp1:  5% overlay   → #1E1E1E
  dp2:  7% overlay   → #222222
  dp3:  8% overlay   → #242424
  dp4:  9% overlay   → #262626
  dp6:  11% overlay  → #2C2C2C
  dp8:  12% overlay  → #2E2E2E
  dp12: 14% overlay  → #333333
  dp16: 15% overlay  → #353535
  dp24: 16% overlay  → #383838
```

---

## Material Design 3 Dark Scheme

Material Design 3 (Material You) provides a systematic approach to dark mode with dynamic color.

### M3 Color Roles in Dark Mode

| Role | Light Value | Dark Value | Usage |
|------|-----------|-----------|-------|
| `primary` | Primary-40 | Primary-80 | Primary interactive elements |
| `onPrimary` | White | Primary-20 | Text/icons on primary |
| `primaryContainer` | Primary-90 | Primary-30 | Filled containers |
| `surface` | Neutral-99 | Neutral-6 | Page/card backgrounds |
| `surfaceContainer` | Neutral-94 | Neutral-12 | Elevated containers |
| `onSurface` | Neutral-10 | Neutral-90 | Body text |
| `onSurfaceVariant` | NeutralVariant-30 | NeutralVariant-80 | Secondary text |
| `outline` | NeutralVariant-50 | NeutralVariant-60 | Borders and dividers |
| `error` | Error-40 | Error-80 | Error states |

### Dynamic Color Generation

```kotlin
// Android: Dynamic color from wallpaper (Material You)
val dynamicColorScheme = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
    if (darkTheme) dynamicDarkColorScheme(context)
    else dynamicLightColorScheme(context)
} else {
    if (darkTheme) darkColorScheme() else lightColorScheme()
}

MaterialTheme(
    colorScheme = dynamicColorScheme,
    content = content
)
```

### M3 Dark Theme Generator

Use the Material Theme Builder to generate light and dark palettes from a source color: https://www.figma.com/community/plugin/1034969338659738588/material-theme-builder

---

## iOS Dark Mode

### System Materials and Vibrancy

iOS does not use flat dark colors. It uses system materials that provide blur, vibrancy, and adaptivity.

| Material | Light Appearance | Dark Appearance | Usage |
|----------|-----------------|-----------------|-------|
| `systemBackground` | White | Black (true) | Root background |
| `secondarySystemBackground` | #F2F2F7 | #1C1C1E | Grouped content |
| `tertiarySystemBackground` | White | #2C2C2E | Inner grouped content |
| `systemGroupedBackground` | #F2F2F7 | Black | Table view background |

### Semantic Colors (UIKit / SwiftUI)

```swift
// Always use semantic colors, never hard-coded
label.textColor = .label              // Adapts: black ↔ white
label.textColor = .secondaryLabel     // Adapts: gray values
view.backgroundColor = .systemBackground
view.backgroundColor = .secondarySystemGroupedBackground

// SwiftUI
Text("Hello")
    .foregroundStyle(.primary)        // Adapts automatically
    .background(.background)          // System background
```

### Elevated Surfaces on iOS

```swift
// iOS uses trait collections for elevation
override func traitCollectionDidChange(_ previousTraitCollection: UITraitCollection?) {
    super.traitCollectionDidChange(previousTraitCollection)
    if traitCollection.userInterfaceLevel == .elevated {
        // Elevated appearance (sheets, modals)
        // System colors automatically adjust
    }
}
```

---

## CSS Implementation

### `prefers-color-scheme` Media Query

```css
/* Base styles (light theme) */
:root {
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f9fafb;
  --color-text-primary: #111827;
  --color-text-secondary: #6b7280;
  --color-border: #e5e7eb;
  --color-interactive: #2563eb;
  --color-interactive-hover: #1d4ed8;
  --color-surface-elevated: #ffffff;
  --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
}

/* Dark theme */
@media (prefers-color-scheme: dark) {
  :root {
    --color-bg-primary: #0f172a;
    --color-bg-secondary: #1e293b;
    --color-text-primary: #f1f5f9;
    --color-text-secondary: #94a3b8;
    --color-border: #334155;
    --color-interactive: #60a5fa;
    --color-interactive-hover: #93bbfd;
    --color-surface-elevated: #1e293b;
    --shadow-sm: 0 1px 2px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.4);
  }
}

/* Usage */
body {
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}
.card {
  background-color: var(--color-surface-elevated);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-sm);
}
a {
  color: var(--color-interactive);
}
a:hover {
  color: var(--color-interactive-hover);
}
```

### Tailwind CSS Dark Mode

```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media' for system preference only
  theme: {
    extend: {
      colors: {
        surface: {
          primary: 'var(--color-bg-primary)',
          secondary: 'var(--color-bg-secondary)',
        }
      }
    }
  }
}
```

```html
<!-- Tailwind dark mode classes -->
<div class="bg-white dark:bg-gray-900">
  <h1 class="text-gray-900 dark:text-gray-100">Title</h1>
  <p class="text-gray-600 dark:text-gray-400">Description</p>
  <button class="bg-blue-600 dark:bg-blue-500 text-white">Action</button>
</div>
```

### CSS Custom Properties with Class Toggle

```css
/* Support both system preference AND user toggle */
:root {
  /* Light theme defaults */
  --bg: #ffffff;
  --text: #111827;
}

/* System dark preference */
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #0f172a;
    --text: #f1f5f9;
  }
}

/* Explicit dark theme override */
[data-theme="dark"] {
  --bg: #0f172a;
  --text: #f1f5f9;
}

/* Explicit light theme override */
[data-theme="light"] {
  --bg: #ffffff;
  --text: #111827;
}
```

---

## Theme Switching

### System Preference Detection

```javascript
// Detect system theme preference
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

// Listen for changes
prefersDark.addEventListener('change', (e) => {
  if (!getUserThemePreference()) {
    // Only auto-switch if user hasn't set a manual preference
    applyTheme(e.matches ? 'dark' : 'light');
  }
});
```

### User Toggle with Persistence

```javascript
const THEME_KEY = 'theme-preference';

function getTheme() {
  // Priority: user preference > system preference
  const stored = localStorage.getItem(THEME_KEY);
  if (stored) return stored;

  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? 'dark'
    : 'light';
}

function setTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  localStorage.setItem(THEME_KEY, theme);

  // Update meta theme-color for browser chrome
  document.querySelector('meta[name="theme-color"]')
    ?.setAttribute('content', theme === 'dark' ? '#0f172a' : '#ffffff');
}

// Three-state toggle: light → dark → system
function cycleTheme() {
  const current = localStorage.getItem(THEME_KEY);
  if (current === 'light') {
    setTheme('dark');
  } else if (current === 'dark') {
    localStorage.removeItem(THEME_KEY);  // Return to system
    applySystemTheme();
  } else {
    setTheme('light');
  }
}

// Apply on page load (before paint to prevent flash)
setTheme(getTheme());
```

### Preventing Flash of Wrong Theme (FOWT)

```html
<!-- Add this script in <head> before any CSS to prevent flash -->
<script>
  (function() {
    var theme = localStorage.getItem('theme-preference');
    if (!theme) {
      theme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark' : 'light';
    }
    document.documentElement.setAttribute('data-theme', theme);
  })();
</script>
```

---

## Image and Media Adaptation

### Logo Adaptation

| Approach | Implementation | Best For |
|----------|---------------|----------|
| Separate assets | `logo-light.svg` / `logo-dark.svg` | Logos with colored backgrounds |
| CSS filter | `filter: invert(1)` on dark theme | Simple black logos |
| SVG `currentColor` | `fill="currentColor"` in SVG paths | Monochrome logos |
| `<picture>` + media query | `<source media="(prefers-color-scheme: dark)">` | Any image format |

### Image Adaptation

```html
<!-- Responsive image for dark mode -->
<picture>
  <source
    media="(prefers-color-scheme: dark)"
    srcset="hero-dark.webp"
  />
  <img src="hero-light.webp" alt="Hero illustration" />
</picture>
```

```css
/* Reduce image brightness in dark mode to avoid glare */
@media (prefers-color-scheme: dark) {
  img:not([data-no-dim]) {
    filter: brightness(0.85);
  }

  /* Illustrations may need inversion or specific treatment */
  .illustration-adaptable {
    filter: invert(1) hue-rotate(180deg);
  }
}
```

### Content That Needs Adaptation

| Content | Light → Dark Treatment |
|---------|----------------------|
| Photography | Slight brightness reduction (85-90%) |
| Illustrations (flat) | Provide dark variant or use `currentColor` SVGs |
| Charts and graphs | Swap axis/label colors via theme tokens |
| Code blocks | Use dark syntax theme (already standard) |
| Maps | Use dark map style (Mapbox/Google Maps dark mode) |
| Embedded videos | No change needed (thumbnails may need border) |
| User-uploaded content | Do not modify; add subtle dark border for separation |

---

## Contrast Requirements

### WCAG Contrast in Both Themes

**Both light and dark themes must independently meet WCAG contrast requirements.**

| Content Type | Minimum Ratio (AA) | Enhanced Ratio (AAA) |
|-------------|--------------------|--------------------|
| Normal text (< 18pt) | 4.5:1 | 7:1 |
| Large text (≥ 18pt or 14pt bold) | 3:1 | 4.5:1 |
| UI components (borders, icons) | 3:1 | — |
| Focus indicators | 3:1 against adjacent | — |

### Common Contrast Failures in Dark Mode

| Element | Failure | Fix |
|---------|---------|-----|
| Secondary text on dark bg | Gray (#808080) on dark gray (#1a1a1a) = 3.5:1 | Lighten to #a0a0a0 or lighter |
| Disabled buttons | Too similar to background | Use opacity + strikethrough or clear visual distinction |
| Placeholder text | Insufficient contrast | Minimum 4.5:1; better yet, use labels |
| Link color | Blue (#0000FF) on dark bg | Use lighter blue (#60a5fa) |
| Red error text | Dark red on dark bg | Use lighter red (#f87171) |

### Testing Contrast

| Tool | Platform | Notes |
|------|----------|-------|
| **WebAIM Contrast Checker** | Web | Quick manual check |
| **Stark** | Figma plugin | Design-time checking |
| **axe DevTools** | Browser extension | Automated scanning |
| **Colour Contrast Analyser** | Desktop app | Eyedropper for any screen element |

---

## Testing Dark Mode

### Visual Regression Testing

```javascript
// Playwright: screenshot testing both themes
import { test, expect } from '@playwright/test';

const themes = ['light', 'dark'];

for (const theme of themes) {
  test(`homepage renders correctly in ${theme} mode`, async ({ page }) => {
    // Set color scheme preference
    await page.emulateMedia({ colorScheme: theme });
    await page.goto('/');

    // Screenshot comparison
    await expect(page).toHaveScreenshot(`homepage-${theme}.png`, {
      fullPage: true,
      maxDiffPixelRatio: 0.01
    });
  });
}

// Test theme switching
test('theme toggle switches correctly', async ({ page }) => {
  await page.goto('/');
  await page.click('[data-testid="theme-toggle"]');
  await expect(page.locator('html')).toHaveAttribute('data-theme', 'dark');

  await expect(page).toHaveScreenshot('after-toggle-dark.png');
});
```

### Accessibility Audit per Theme

Run full accessibility audit in both themes:

```javascript
// axe-core audit for each theme
import { AxeBuilder } from '@axe-core/playwright';

for (const theme of ['light', 'dark']) {
  test(`accessibility audit in ${theme} mode`, async ({ page }) => {
    await page.emulateMedia({ colorScheme: theme });
    await page.goto('/');

    const results = await new AxeBuilder({ page })
      .withTags(['wcag2a', 'wcag2aa'])
      .analyze();

    expect(results.violations).toEqual([]);
  });
}
```

### Manual Testing Checklist

- [ ] All text meets 4.5:1 contrast in dark mode
- [ ] All UI components meet 3:1 contrast in dark mode
- [ ] Logos and brand elements are visible in dark mode
- [ ] Images do not glare on dark backgrounds
- [ ] Focus indicators are visible in dark mode
- [ ] Form fields have visible borders in dark mode
- [ ] Error, warning, and success states are distinguishable
- [ ] Charts and data visualizations are readable
- [ ] Third-party embeds (maps, videos, widgets) are not broken
- [ ] Theme toggle works correctly (light → dark → system)
- [ ] Theme preference persists across page loads
- [ ] No flash of wrong theme on initial load
- [ ] Scrollbar styling adapts to theme
- [ ] Print stylesheet is not affected by dark mode

---

## Common Dark Mode Mistakes

| Mistake | Problem | Correct Approach |
|---------|---------|-----------------|
| **Pure black background (#000000)** | Eye strain, especially on OLED with white text | Use very dark gray (#121212, #0f172a) |
| **Full white text (#FFFFFF)** | Too much contrast, halation effect | Use off-white (#E0E0E0, #f1f5f9) |
| **Just inverting colors** | Saturated colors vibrate, images look wrong | Design dark palette separately with desaturated accents |
| **Same shadows as light mode** | Shadows invisible on dark backgrounds | Use surface elevation (lighter bg) instead of/in addition to shadows |
| **Forgetting third-party components** | Date pickers, modals, tooltips stay light | Theme all components, including third-party |
| **No system preference respect** | Users must manually toggle every site | Default to system preference, allow override |
| **Forgetting meta theme-color** | Browser chrome stays light | Update `<meta name="theme-color">` per theme |
| **Hard-coded colors in inline styles** | Override CSS custom properties | Audit for inline styles, use tokens everywhere |
| **Ignoring `color-scheme` CSS** | Browser UI elements (scrollbars, form controls) don't adapt | Add `color-scheme: light dark` to `:root` |
| **Testing only one theme** | Accessibility violations in untested theme | Automated testing for both themes |

### The `color-scheme` Property

```css
/* Tell the browser both color schemes are supported */
:root {
  color-scheme: light dark;
}

/* This makes native form controls, scrollbars, and other
   browser-rendered UI adapt to the current theme */
```

---

## Anti-Patterns

| Anti-Pattern | Why It Fails | Correct Approach |
|-------------|-------------|------------------|
| Building dark mode as an afterthought | Requires touching every component | Design token system from day one |
| Using `filter: invert(1)` on entire page | Images, videos, brand colors all break | Proper token-based theming |
| Different information hierarchy per theme | Users learn one layout, breaks in other | Same layout and hierarchy, different colors only |
| Dark mode only (no light option) | Some users need light mode (readability, outdoor use) | Always support both themes |
| Separate CSS files per theme | Code duplication, sync issues | CSS custom properties with theme class |
| Ignoring reduced transparency preference | Glass/blur effects cause readability issues | Respect `prefers-reduced-transparency` |

---

## References

- [Material Design 3 — Dark Theme](https://m3.material.io/styles/color/dynamic/choosing-a-scheme#0a78b608-3519-4834-8d31-0cdec3e0da57)
- [Apple HIG — Dark Mode](https://developer.apple.com/design/human-interface-guidelines/dark-mode)
- [MDN — prefers-color-scheme](https://developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme)
- [web.dev — Building a Dark Mode](https://web.dev/articles/prefers-color-scheme)
- [WCAG 2.2 — Contrast (Minimum) 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html)
- [Tailwind CSS — Dark Mode](https://tailwindcss.com/docs/dark-mode)

---

## Cross-References

- [SKILL.md](../SKILL.md) — Parent skill overview, platform constraints section
- [design-systems.md](design-systems.md) — Token architecture and design system structure
- [wcag-accessibility.md](wcag-accessibility.md) — Contrast requirements and accessibility auditing
- [component-library-comparison.md](component-library-comparison.md) — Theme support across component libraries
- [mobile-ux-patterns.md](mobile-ux-patterns.md) — Platform-specific iOS/Android dark mode patterns
