# Material Typography, Color, and Theming

## Table of Contents

- [Material Type Scale](#material-type-scale)
- [Custom Fonts](#custom-fonts)
- [Font Scaling](#font-scaling)
- [Material Color Roles](#material-color-roles)
- [Dynamic Color](#dynamic-color)
- [Tonal Palettes and Surface Elevation](#tonal-palettes-and-surface-elevation)
- [Harmonized Custom Colors](#harmonized-custom-colors)
- [Contrast and Accessibility](#contrast-and-accessibility)
- [Common Smells](#common-smells)

Use this reference for text hierarchy, color roles, dynamic color, contrast, and theming decisions.

## Material Type Scale

Material 3 defines a type scale with five categories, each in three sizes:

| Role | Style | Default | Typical Use |
|------|-------|---------|-------------|
| Display | displayLarge / Medium / Small | Roboto 57/45/36sp | Hero numbers, splash headlines |
| Headline | headlineLarge / Medium / Small | Roboto 32/28/24sp | Screen titles, section headers |
| Title | titleLarge / Medium / Small | Roboto 22/16/14sp | Card titles, dialog titles, TopAppBar |
| Body | bodyLarge / Medium / Small | Roboto 16/14/12sp | Paragraph text, descriptions, list content |
| Label | labelLarge / Medium / Small | Roboto 14/12/11sp | Buttons, chips, tabs, captions, metadata |

Access via `MaterialTheme.typography`:

```kotlin
Text("Score", style = MaterialTheme.typography.displayLarge)
Text("Your reading", style = MaterialTheme.typography.headlineMedium)
Text("Energy level today", style = MaterialTheme.typography.titleSmall)
Text("The stars suggest a period of reflection.", style = MaterialTheme.typography.bodyLarge)
Text("Updated 2h ago", style = MaterialTheme.typography.labelSmall)
```

Use weight, spacing, and placement to express hierarchy before increasing font size. Keep each card or compact module to a small set of text roles — usually title, body, and label.

## Custom Fonts

Override the Material type scale with a custom font family:

```kotlin
val AppFontFamily = FontFamily(
    Font(R.font.inter_regular, FontWeight.Normal),
    Font(R.font.inter_medium, FontWeight.Medium),
    Font(R.font.inter_semibold, FontWeight.SemiBold),
    Font(R.font.inter_bold, FontWeight.Bold)
)

val AppTypography = Typography(
    displayLarge = MaterialTheme.typography.displayLarge.copy(fontFamily = AppFontFamily),
    headlineMedium = MaterialTheme.typography.headlineMedium.copy(fontFamily = AppFontFamily),
    // ... override all 15 styles
)

MaterialTheme(typography = AppTypography) { ... }
```

Keep the Material size and weight defaults unless a specific brand requirement justifies changing them. Partial overrides (only changing font family) preserve the scale's readability tuning.

## Font Scaling

Android scales `sp` units automatically with the system font size setting. This is the equivalent of iOS Dynamic Type.

### Testing Font Scale

Test at three breakpoints:
- **100%** — default rendering
- **130%** — common accessibility setting, catches first overflow issues
- **200%** — maximum scale, catches hard failures (text clipping, overlapping, layout collapse)

Set font scale in emulator via Settings > Display > Font size, or via ADB:

```bash
adb shell settings put system font_scale 2.0
```

### Common Font Scale Issues

- `maxLines = 1` on content that wraps at 200% — use `maxLines` + `TextOverflow.Ellipsis` and verify truncation is acceptable
- Fixed-height containers that clip text at large scale — use `wrapContentHeight()` or `IntrinsicSize`
- Hardcoded `dp` heights on text containers — let the text drive height

## Material Color Roles

Material 3 defines color roles that adapt across light, dark, and dynamic themes:

### Primary Group
- `primary` — key interactive elements, FABs, active states
- `onPrimary` — content on primary color
- `primaryContainer` — softer primary for card fills, selected states
- `onPrimaryContainer` — content on primary containers

### Secondary Group
- `secondary` / `onSecondary` / `secondaryContainer` / `onSecondaryContainer`
- Supporting UI: filters, chips, less prominent actions

### Tertiary Group
- `tertiary` / `onTertiary` / `tertiaryContainer` / `onTertiaryContainer`
- Complementary accent for special features

### Error Group
- `error` / `onError` / `errorContainer` / `onErrorContainer`
- Destructive actions and validation errors only

### Surface Group
- `surface` — base background
- `onSurface` — primary text and icons
- `onSurfaceVariant` — secondary text, icons, outlines
- `surfaceContainerLowest` through `surfaceContainerHighest` — 5 tonal levels for surface hierarchy
- `outline` — borders, dividers
- `outlineVariant` — subtle separators

### Background and Inverse
- `background` / `onBackground` — legacy, prefer `surface`
- `inverseSurface` / `inverseOnSurface` / `inversePrimary` — for snackbars, tooltips

Always access via `MaterialTheme.colorScheme`:

```kotlin
Surface(
    color = MaterialTheme.colorScheme.surfaceContainerLow,
    contentColor = MaterialTheme.colorScheme.onSurface
) { ... }
```

## Dynamic Color

Android 12+ (API 31+) extracts a color palette from the user's wallpaper. Enable it:

```kotlin
val colorScheme = when {
    Build.VERSION.SDK_INT >= Build.VERSION_CODES.S -> {
        if (darkTheme) dynamicDarkColorScheme(context)
        else dynamicLightColorScheme(context)
    }
    else -> {
        if (darkTheme) DarkColorScheme  // static seed palette
        else LightColorScheme
    }
}

MaterialTheme(colorScheme = colorScheme) { ... }
```

### Dynamic Color Rules

- Always provide a static seed palette as fallback for API < 31
- Test with at least 3 different wallpapers — the generated palette varies significantly
- Custom brand colors that must remain fixed should use `harmonize()` to blend with the dynamic palette rather than ignoring it
- Dynamic color does NOT affect `error` roles — error red stays consistent

## Tonal Palettes and Surface Elevation

Material 3 uses tonal color (not opacity overlays) for elevation:

```kotlin
Surface(tonalElevation = 3.dp) { ... }  // subtle tonal shift toward primary
Surface(tonalElevation = 6.dp) { ... }  // more pronounced shift
```

Or use the named surface container roles directly:

```kotlin
Surface(color = MaterialTheme.colorScheme.surfaceContainer) { ... }
```

The tonal system replaces the Material 2 pattern of white overlays on dark surfaces. Never use `Color.White.copy(alpha = 0.08f)` for elevation — use tonal roles instead.

## Harmonized Custom Colors

When an app needs a fixed brand color alongside dynamic color, harmonize it:

```kotlin
val harmonizedGreen = MaterialColors.harmonize(
    colorToHarmonize = Color(0xFF4CAF50).toArgb(),
    colorToHarmonizeWith = MaterialTheme.colorScheme.primary.toArgb()
).let { Color(it) }
```

This shifts the custom color slightly toward the dynamic primary, maintaining visual coherence without losing brand identity.

## Contrast and Accessibility

Material 3 color roles are designed to meet WCAG AA contrast ratios:

| Pair | Minimum ratio |
|------|---------------|
| `onPrimary` on `primary` | 4.5:1 |
| `onSurface` on `surface` | 4.5:1 (large text 3:1) |
| `onSurfaceVariant` on `surface` | 4.5:1 |
| `outline` on `surface` | 3:1 (non-text) |

### When to Verify Manually

- Custom colors not from the Material palette
- Dynamic color on wallpapers with extreme saturation
- Text on images or gradients (Canvas overlays)
- `onSurfaceVariant` text at `labelSmall` size

Use Android Studio's Accessibility Scanner or the Color Contrast Analyzer to verify ratios.

## Common Smells

- Hardcoded `Color(0xFF...)` values instead of `MaterialTheme.colorScheme` roles
- `Color.White` / `Color.Black` for text instead of `onSurface` / `onSurfaceVariant`
- Fixed `sp` sizes outside the type scale without justification
- `shadow()` as the only elevation signal (Material 3 prefers tonal elevation)
- Bright accent colors used as decoration rather than interaction cues
- Custom theme that skips `surfaceContainer*` levels — surfaces look flat
- Dynamic color enabled without testing on multiple wallpapers
