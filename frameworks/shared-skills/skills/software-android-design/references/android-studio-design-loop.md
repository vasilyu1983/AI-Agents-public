# Android Studio Design Loop

## Table of Contents

- [What to Prefer](#what-to-prefer)
- [@Preview Loop](#preview-loop)
- [Recommended Emulator Loop](#recommended-emulator-loop)
- [CLI Flow](#cli-flow)
- [Layout Inspector](#layout-inspector)
- [What to Inspect](#what-to-inspect)
- [Common Fix Patterns](#common-fix-patterns)
- [Proof Expectations](#proof-expectations)

Use this reference when the user wants design fixes proved on an emulator instead of explained abstractly.

## What to Prefer

- Prefer `@Preview` composables for rapid visual iteration during development — test layout, theme, and font scale without booting an emulator.
- Prefer a running emulator for runtime truth — dynamic color, real insets, system font scale, and interaction behavior.
- Prefer Layout Inspector for hierarchy, bounds, and recomposition inspection on a running app.
- Prefer standard Material 3 controls and current navigation patterns before custom surfaces or animations.

## @Preview Loop

Use `@Preview` annotations for fast design iteration without launching an emulator:

```kotlin
@Preview(showBackground = true, widthDp = 360)
@Preview(showBackground = true, widthDp = 360, uiMode = Configuration.UI_MODE_NIGHT_YES)
@Preview(showBackground = true, widthDp = 600, name = "Medium")
@Preview(showBackground = true, widthDp = 360, fontScale = 2.0f, name = "Large Font")
@Composable
fun DashboardPreview() {
    AppTheme {
        DashboardScreen(sampleState)
    }
}
```

### Preview Variants to Always Include

| Variant | Why |
|---------|-----|
| Default (360dp) | Baseline compact phone |
| Dark mode (`uiMode = UI_MODE_NIGHT_YES`) | Verify contrast and surface hierarchy |
| Medium width (600dp) | Foldable/tablet layout switching |
| Large font (fontScale 2.0f) | Accessibility overflow testing |

### Limitations

Previews do not show:
- Dynamic color (requires runtime wallpaper extraction)
- Real WindowInsets (status bar, navigation bar)
- Gesture behavior and animation timing
- Actual network-loaded content

Always verify final design on a running emulator.

## Recommended Emulator Loop

1. Boot the target AVD (or use `bootstrap-emulator.sh` to create one).
2. Build and install with `./scripts/run-android.sh --uninstall-first`.
3. Navigate to the target screen.
4. Capture a screenshot with `./scripts/capture-screenshot.sh screenshots/before.png`.
5. Review spacing, typography, contrast, hierarchy, and navigation against Material 3 guidance.
6. Apply the smallest Compose fix that addresses the issue.
7. Rebuild, reinstall, and compare screenshots with `./scripts/capture-screenshot.sh screenshots/after.png`.

## CLI Flow

```bash
# One-time: create and boot an emulator
./scripts/bootstrap-emulator.sh --api 35 --device pixel_8

# Build, uninstall, install, and launch
./scripts/run-android.sh --uninstall-first

# Capture screenshot for review
./scripts/capture-screenshot.sh screenshots/before.png

# After code changes — rebuild and compare
./scripts/run-android.sh --uninstall-first
./scripts/capture-screenshot.sh screenshots/after.png

# Inspect UI hierarchy
./scripts/layout-inspector.sh hierarchy/current.xml
```

## Layout Inspector

Android Studio's Layout Inspector shows:
- Composable hierarchy and bounds
- Recomposition counts
- Modifier chains
- Semantic properties

### When to Use Layout Inspector vs ADB Dump

| Need | Tool |
|------|------|
| Live hierarchy exploration | Layout Inspector |
| Quick XML dump for AI review | `adb shell uiautomator dump` via `layout-inspector.sh` |
| Screenshot for visual review | `adb exec-out screencap -p` via `capture-screenshot.sh` |
| Bounds and padding verification | Layout Inspector (preferred) or uiautomator XML |

## What to Inspect

- Is the screen using Material structure for the task?
- Does the most important content win first attention?
- Are title, body, and metadata clearly separated by type scale and spacing?
- Does tonal elevation improve hierarchy without creating visual noise?
- Does light and dark theme preserve contrast?
- Are `TopAppBar`, `NavigationBar`, `ModalBottomSheet` behaving like standard Material chrome?
- Do touch targets meet the 48dp minimum?
- Does font scaling at 200% cause overflow or clipping?

## Common Fix Patterns

- Replace fixed `TextStyle(fontSize = N.sp)` with `MaterialTheme.typography` roles.
- Replace hardcoded `Color(0xFF...)` with `MaterialTheme.colorScheme` roles.
- Reduce dashboard clutter by promoting one hero card and demoting secondary content to `OutlinedCard` or `ListItem`.
- Move actions into `TopAppBar` actions, `DropdownMenu`, or FAB when the screen feels crowded.
- Convert custom navigation to `NavigationSuiteScaffold` when the structure is really app-level.
- Add `windowInsetsPadding` when content renders behind system bars.
- Replace `Box(Modifier.clickable { })` with proper ripple `Indication` for tactile feedback.
- Add `contentDescription` to all meaningful icons and images.

## Proof Expectations

Prefer artifacts over summary:

- build/install output
- screenshot before
- screenshot after
- relevant logcat lines if layout or composition warnings appear
- short explanation of what changed and why it is more Material-native
