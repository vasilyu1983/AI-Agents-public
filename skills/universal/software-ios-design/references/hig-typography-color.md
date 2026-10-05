# HIG Typography, Color, and Materials

Use this reference for text hierarchy, semantic color, contrast, and materials decisions that should feel native on every iOS app.

## Table of Contents

- [San Francisco and Font Roles](#san-francisco-and-font-roles)
- [Dynamic Type Scale](#dynamic-type-scale)
- [Typography Rules](#typography-rules)
- [Color System](#color-system)
- [Contrast Targets](#contrast-targets)
- [Materials and Liquid Glass](#materials-and-liquid-glass)
- [Dark Mode Pitfalls](#dark-mode-pitfalls)
- [Common Smells](#common-smells)

## San Francisco and Font Roles

iOS ships with three San Francisco variants. Pick by intent, not by aesthetics:

| Font | Use for | Notes |
|---|---|---|
| **SF Pro** | Default UI text, body copy, titles | `.font(.body)`, `.font(.headline)` — uses SF Pro by default |
| **SF Pro Rounded** | Friendly/playful surfaces, large display numbers, kids/health/money apps | `.fontDesign(.rounded)` |
| **SF Mono** | Code, tabular numerics that must align column-to-column | `.fontDesign(.monospaced)` or `.monospacedDigit()` |
| **New York** | Editorial long-form reading | `.fontDesign(.serif)` — reserve for prose, not UI chrome |

Use `.monospacedDigit()` (not full SF Mono) when you only need digits to align — clocks, scoreboards, counters. It preserves the rest of the font's proportional rendering.

## Dynamic Type Scale

Standard text styles and their default sizes. Always use the style, not the raw size — the system scales styles correctly through all Dynamic Type levels including accessibility sizes.

| Style | Default (pt) | Accessibility (pt at AX5) | Common use |
|---|---|---|---|
| `.largeTitle` | 34 | 53 | Screen titles at root |
| `.title` | 28 | 40 | Primary section titles |
| `.title2` | 22 | 32 | Secondary titles |
| `.title3` | 20 | 30 | Tertiary titles |
| `.headline` | 17 (semibold) | 23 | Row titles, card titles |
| `.subheadline` | 15 | 21 | Supporting row text |
| `.body` | 17 | 53 | Primary readable copy |
| `.callout` | 16 | 21 | Short supporting text |
| `.footnote` | 13 | 19 | Metadata, timestamps |
| `.caption` | 12 | 18 | Labels, tags |
| `.caption2` | 11 | 17 | Smallest legible label |

Rules:

- `.body` and `.largeTitle` scale *much* larger at AX sizes than the others — design layouts that can absorb ~3× growth on these styles without clipping.
- `.headline` is semibold by default; don't override weight casually.
- Text in UI controls (buttons, tab bar labels) uses `.body`-ish sizing on iOS 26 — custom scale overrides typically break on Larger Text.
- For repeated custom sizes (e.g., a 24pt hero number), extract to a design token and derive it from a relative style: `Font.system(size: 24, weight: .semibold).leading(.tight)` — but prefer scaling via `.dynamicTypeSize(.xSmall ... .accessibility5)` limits only when there is a real reason (e.g., complex custom layouts where AX5 breaks hierarchy).

### Emphasized weight variants

The HIG added an `emphasized` variant for Dynamic Type styles. Use it when you need a heavier weight that still scales correctly with the user's text-size preference, instead of hard-coding `.bold`/`.semibold` on a style:

```swift
Text("Today")
    .font(.title2)
    .fontWeight(.semibold)            // OK
Text("Today")
    .font(.system(.title2, design: .default).weight(.semibold))  // works but verbose
```

Emphasized variants are the canonical 2026 way to express "this title should be heavier" without losing Dynamic Type behaviour. Use them in tokens; do not stack `.fontWeight()` calls on top of styles inside view code.

## Typography Rules

- Express hierarchy through **weight, spacing, and placement** before you reach for a bigger size.
- Keep each card/module to a small set of text roles — usually title + body + metadata.
- Never ship fixed pixel sizes like `.font(.system(size: 14))` for user-facing body text. Use styles.
- Use `.tracking()` and `.textCase(.uppercase)` for eyebrows and labels; do not bake tracking into variable text.
- Use `.foregroundStyle(.primary | .secondary | .tertiary | .quaternary)` for hierarchy, not opacity math.
- For editorial prose, add `.lineSpacing(4...8)` and `.kerning(0.1)` to increase readability.
- Avoid `minimumScaleFactor` as a layout escape hatch — it hides Dynamic Type failures rather than fixing them.

## Color System

Always prefer semantic system colors. Hardcoded RGB produces apps that don't adapt to Dark Mode, Increase Contrast, or tinted iPad Dynamic Desktop.

### Foreground

- `.primary` — main readable text
- `.secondary` — supporting text
- `.tertiary` — disabled/inactive
- `.quaternary` — scaffolding, placeholders

### Background

| Token | Use |
|---|---|
| `Color(.systemBackground)` | Base screen background |
| `Color(.secondarySystemBackground)` | Grouped content background |
| `Color(.tertiarySystemBackground)` | Nested surface |
| `Color(.systemGroupedBackground)` | Grouped list background |
| `Color(.secondarySystemGroupedBackground)` | Row background in grouped lists |

### Fills

`Color(.systemFill)`, `Color(.secondarySystemFill)`, `Color(.tertiarySystemFill)`, `Color(.quaternarySystemFill)` — for UI-element fills (chips, toggles, quick-action squares). These already adapt to Dark Mode and Increase Contrast.

### Tint

`.tint(.accentColor)` for user-facing primary actions and selection state. Don't scatter `.tint()` through a view tree — set it once at the app or navigation level and let children inherit.

### Status Semantics

Reserve semantic colors (`.red`, `.orange`, `.green`, `.blue`) for state meaning, not decoration:

- `.red` — destructive, error
- `.orange` — caution, pending
- `.yellow` — warning (reserve; users confuse yellow and orange at small sizes)
- `.green` — success, positive
- `.blue` — informational, selection

## Contrast Targets

Apple aligns with WCAG 2.1 AA:

| Content | Minimum ratio |
|---|---|
| Body text (<18pt regular, <14pt bold) | 4.5 : 1 |
| Large text (≥18pt regular, ≥14pt bold) | 3.0 : 1 |
| UI components and graphical objects (icons, focus rings) | 3.0 : 1 |

Verify with Apple's Accessibility Inspector (`xcrun simctl ... ` or Xcode > Open Developer Tool > Accessibility Inspector). Do not eyeball contrast — semantic colors pass by default, but custom colors often fail in one appearance and pass in the other.

`.secondary`, `.tertiary`, `.quaternary` text against a plain background already hits AA in both appearances. If you override colors, re-verify.

When Increase Contrast is enabled, the system increases contrast for semantic colors automatically. If you hardcoded colors, you miss this entirely.

## Materials and Liquid Glass

Materials create layering through translucency. They are not a decoration — they exist to show "what's behind" as a spatial cue.

### Standard Materials (all iOS versions)

| Modifier | Use |
|---|---|
| `.ultraThinMaterial` | Lightest — floating overlays over busy content |
| `.thinMaterial` | Hover cards, tooltips |
| `.regularMaterial` | Sheet backgrounds, popovers |
| `.thickMaterial` | Heavy panels, modal scrims |
| `.ultraThickMaterial` | Near-opaque, rarely used |

Apply via `.background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16))` — always pair with a shape so the material clips correctly.

### Liquid Glass (iOS 26+)

Apple's current navigation-layer material. See [ios26-liquid-glass.md](ios26-liquid-glass.md) for the full API and rules. Summary:

- Standard chrome (tab bars, toolbars, nav bars, sheets, sidebars) adopts Liquid Glass automatically on iOS 26.
- Use `.glassEffect(_:in:)` and `GlassEffectContainer` only for chrome you build yourself.
- Glass does not belong on content cards or data surfaces.

### When Opaque Surfaces Beat Materials

- Text-heavy forms and settings
- Dense data tables and lists
- Screens with already-busy imagery behind content
- Any place where materials reduce contrast

## Dark Mode Pitfalls

- **Hardcoded `.white` / `.black`** in Canvas, gradients, or `UIColor` literals — swap to `Color(.label)`, `Color(.systemBackground)`, or pass `@Environment(\.colorScheme)` into Canvas.
- **Pure white text on near-black** — harsh; Apple uses a warm off-white (`Color(.label)`) for primary text. Match it.
- **Transparent overlays on `.black`** — `.black.opacity(0.05)` disappears on dark backgrounds. Use `.primary.opacity(0.05)` so it adapts.
- **Accent colors that invert poorly** — verify your brand accent in both appearances; some blues drown on Dark Mode backgrounds. Define a `Color` asset with separate light/dark values instead of a single `Color(red:green:blue:)`.
- **Shadows on dark** — default `.shadow()` uses `.black` and vanishes on dark backgrounds. Use `.shadow(color: .black.opacity(0.5), ...)` or drop shadows entirely and rely on material/surface layering for depth.
- **Glass over dark-only backgrounds** — if the app is dark-only, document that assumption and test Increase Contrast. Apps sometimes ship "dark only" accidentally because light mode was never verified.

## Common Smells

- Fixed-size typography (`.font(.system(size: 14))` for body text)
- Hardcoded light/dark colors instead of semantic colors
- `minimumScaleFactor` below 0.7 — a sign Dynamic Type wasn't really accommodated
- Material backgrounds under text-heavy forms
- Accent color used as decoration instead of interaction cue
- `foregroundColor` (deprecated spelling) instead of `foregroundStyle`
- Mixing `SF Pro` and a custom font without explaining why
- Pure `.black` shadows on Dark Mode
- Three accent colors on one screen — iOS expects one accent + semantic status colors
