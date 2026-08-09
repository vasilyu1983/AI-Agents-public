# Material Layout and Spacing

## Table of Contents

- [Core Rules](#core-rules)
- [Edge-to-Edge](#edge-to-edge)
- [Spacing Discipline](#spacing-discipline)
- [Column Grid System](#column-grid-system)
- [Canonical Adaptive Layouts](#canonical-adaptive-layouts)
- [Layout Adaptivity](#layout-adaptivity)
- [Lists, Cards, and Dense Screens](#lists-cards-and-dense-screens)
- [Common Smells](#common-smells)

Use this reference for layout decisions that should feel native on Android phones, foldables, and tablets.

## Core Rules

- Use the 8dp grid as the primary spacing unit. Use 4dp for fine adjustments within components.
- Content margins: 16dp on compact screens, 24dp on medium and expanded.
- Respect system bars and display cutouts — go edge-to-edge and consume insets properly.
- Let content size and font scaling drive height whenever possible.
- Adapt structure across compact (phone), medium (foldable inner), and expanded (tablet) WindowSizeClass.

## Edge-to-Edge

Android expects apps to draw behind system bars. Set up edge-to-edge in the Activity:

```kotlin
enableEdgeToEdge()
```

Then consume `WindowInsets` in Compose:

```kotlin
Scaffold(
    modifier = Modifier.fillMaxSize(),
    contentWindowInsets = ScaffoldDefaults.contentWindowInsets
) { innerPadding ->
    Content(modifier = Modifier.padding(innerPadding))
}
```

For custom layouts outside Scaffold, use `Modifier.windowInsetsPadding(WindowInsets.safeDrawing)` or `Modifier.systemBarsPadding()`.

### Common Inset Mistakes

- Applying `systemBarsPadding` on a Scaffold that already handles insets — double padding
- Forgetting `navigationBarsPadding` on ModalBottomSheet content — last row hides behind gesture bar
- Using `Modifier.padding(WindowInsets.statusBars.asPaddingValues())` when `Modifier.statusBarsPadding()` reads better

## Spacing Discipline

- Keep tighter spacing inside a group than between groups — `Arrangement.spacedBy(8.dp)` within a row, 16dp between sections.
- Use section spacing to signal hierarchy rather than adding `HorizontalDivider` everywhere.
- Keep touch targets at or above 48dp (Material minimum). Use `Modifier.sizeIn(minWidth = 48.dp, minHeight = 48.dp)` on custom interactive elements.
- When screens start to feel crowded, remove or merge elements before shrinking hit areas or typography.

## Column Grid System

Material Design uses a responsive column grid:

| WindowSizeClass | Columns | Margins | Gutters |
|-----------------|---------|---------|---------|
| Compact | 4 | 16dp | 8dp |
| Medium | 8 | 24dp | 16dp |
| Expanded | 12 | 24dp | 24dp |

Use `LazyVerticalGrid` with `GridCells.Fixed(N)` or `GridCells.Adaptive(minSize)` to implement column grids. For precise Material column layouts, calculate column span manually based on WindowSizeClass.

## Canonical Adaptive Layouts

Material 3 provides adaptive layout scaffolds for common patterns:

- **ListDetailPaneScaffold** — list on the left, detail on the right (email, settings). Falls back to navigation push on compact.
- **SupportingPaneScaffold** — main content with a supplementary side panel. Detail collapses to sheet on compact.
- **Feed / Grid** — `LazyVerticalGrid` with `GridCells.Adaptive(minSize = 300.dp)` for card feeds that reflow across screen sizes.
- **NavigationSuiteScaffold** — automatically switches between `NavigationBar` (compact), `NavigationRail` (medium), and `PermanentNavigationDrawer` (expanded) based on WindowSizeClass.

Prefer these over building custom adaptive layouts unless the content structure genuinely requires it.

## Layout Adaptivity

WindowSizeClass breakpoints:

| Class | Width | Typical devices |
|-------|-------|-----------------|
| Compact | < 600dp | Most phones |
| Medium | 600-839dp | Foldable inner display, small tablets |
| Expanded | >= 840dp | Tablets, desktop |

Check WindowSizeClass in Compose:

```kotlin
val windowSizeClass = currentWindowAdaptiveInfo().windowSizeClass
when (windowSizeClass.windowWidthSizeClass) {
    WindowWidthSizeClass.COMPACT -> { /* single column */ }
    WindowWidthSizeClass.MEDIUM -> { /* rail + content */ }
    WindowWidthSizeClass.EXPANDED -> { /* drawer + multi-pane */ }
}
```

### Adaptivity Rules

- Prefer single-column layouts on compact-width phones for content-heavy screens.
- Use `NavigationRail` on medium and `PermanentNavigationDrawer` on expanded — never show `NavigationBar` on tablets.
- Re-check long titles, localized strings, and large font scale on the smallest supported phone.
- On expanded width, constrain content to a maximum reading width (600-840dp) rather than stretching edge-to-edge.
- Do not skip testing the medium band (600-839dp) — it is where foldable inner displays and small tablets live, and it is the width where a two-column layout or rail/nav choice most often looks wrong. Compact and expanded alone do not prove medium behaves correctly.

### Foldable Hinge Awareness

On foldable devices, query `FoldingFeature` via `WindowInfoTracker` (androidx.window) rather than treating the device as a plain wide/narrow rectangle:

- Do not place primary controls, text input focus targets, or critical content directly under the hinge in tabletop or book posture — the fold seam occludes or distorts content there.
- In tabletop posture (device folded to ~90°, screen split top/bottom), move controls to the bottom half and content/preview to the top half — this is the standard camera/video-call pattern.
- In book posture (vertical fold, side-by-side halves), a list-detail layout that already adapts at the `medium`/`expanded` breakpoint usually reads well split across the two halves — verify the split lands near the hinge, not mid-content.
- Test with the emulator's foldable device profiles (fold-in and fold-out configurations), not just a resized phone skin — hinge position and posture are not derivable from width alone.

## Lists, Cards, and Dense Screens

- Prefer `LazyColumn` with `ListItem` for homogeneous rows and long collections.
- Prefer Cards for mixed-content summaries, overview surfaces, and visual grouping.
- For overview screens, treat 5-6 visible cards as a heuristic, not a platform rule; if more content competes above the fold, the hierarchy is usually weak.
- When content exceeds the viewport, choose whether it should scroll, paginate, collapse, or move to a secondary destination.

## Common Smells

- Content pressed against screen edges without 16dp margin
- Equal spacing between everything — no hierarchy signal
- Cards used where a `ListItem` list would scan better
- `LazyVerticalGrid` with `Fixed(3)` on compact phones for content that really wants one column
- Fixed heights that break under large font scale
- `fillMaxWidth()` on every surface without max-width constraint on expanded WindowSizeClass
- Nested scrollable containers (`LazyColumn` inside `Column(verticalScroll)`)
