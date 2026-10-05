# Adaptive Screen-Size Testing

Patterns for validating Android UIs across compact, medium, expanded, tablet, and foldable states.

**Official docs**: [Test different screen sizes](https://developer.android.com/training/testing/different-screens)  
**Tools guide**: [Libraries and tools to test different screen sizes](https://developer.android.com/training/testing/different-screens/tools)  
**Setup guide**: [Espresso Device API](https://developer.android.com/studio/test/espresso-api)

## When to Add Adaptive Coverage

- Your app has tablet, foldable, desktop, or expanded-width layouts.
- Navigation, pane layouts, or list-detail patterns change with window size.
- Orientation or posture changes can hide, overlap, or reset state.
- You support resizable windows or ChromeOS-style multi-window behavior.

## 2026 Default

Do not treat adaptive coverage as "run the same phone tests on a tablet." Model the behaviors that change with size classes or folding state.

## Main Tools

### Espresso Device API

Use it when you need to change or simulate device conditions from tests, especially screen size and posture-related coverage.

### `DisplaySizeRule`

Use this rule to restore the original display size after each test.

```kotlin
@get:Rule(order = 2)
val displaySizeRule = DisplaySizeRule()
```

### `DeviceConfigurationOverride`

Use it to fit tablet or larger-layout coverage inside a smaller physical device or emulator when the test only needs layout behavior rather than hardware realism.

## Coverage Strategy

- Compact-width phone layout
- Expanded or tablet layout
- Foldable-specific state if the app exposes different panes or navigation
- Orientation changes only where they change behavior or state retention
- Font-scale and dark-mode variants where they expose real layout risk

## Patterns

### Validate layout switching, not just rendering

Assert the behavior that changes:

- one-pane vs two-pane content
- bottom nav vs rail
- list-detail persistence
- dialog vs side sheet behavior

### Keep adaptive assertions focused

Avoid full-screen snapshot comparisons for every size. Prefer:

- structural assertions
- visible controls
- pane presence or absence
- state retention after size change

### Combine with screenshot tests selectively

Use screenshots for a few high-risk adaptive states, not every possible permutation.

## Example Use Cases

- Verify that a list-detail screen keeps selection visible in expanded layouts.
- Verify that a fold or posture change does not reset unsaved state.
- Verify that the rail replaces bottom navigation in expanded width.
- Verify that a dialog becomes an inline pane at larger sizes.

## Related Resources

- [Compose Testing](compose-testing.md)
- [Screenshot Testing](screenshot-testing.md)
- [Build-Managed Devices](gradle-managed-devices.md)
