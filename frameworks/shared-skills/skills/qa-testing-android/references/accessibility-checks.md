# Accessibility Checks

Accessibility coverage patterns for Android UI tests.

**Official Espresso guide**: [Accessibility checking](https://developer.android.com/training/testing/espresso/accessibility-checking)  
**General testing guide**: [Test your app's accessibility](https://developer.android.com/guide/topics/ui/accessibility/testing)

## Why This Belongs In Test Automation

Accessibility regressions are often ordinary UI regressions:

- missing labels
- undersized touch targets
- low contrast
- broken focus order
- content that is present visually but not exposed correctly to assistive tech

Run these checks inside high-value UI journeys instead of leaving them to manual QA only.

## Espresso Checks

Enable accessibility checks in Espresso suites with one setup call:

```kotlin
import androidx.test.espresso.accessibility.AccessibilityChecks

class LoginFlowTest {
    init {
        AccessibilityChecks.enable().setRunChecksFromRootView(true)
    }
}
```

This makes Espresso evaluate more than the interacted view when each action runs.

## Suppressing Known Failures Carefully

If you must suppress a known issue temporarily, suppress the narrowest possible matcher and tie it to a tracked fix. Do not build a large ignore list that hides future regressions.

## Compose Notes

Compose testing now has accessibility-focused APIs in `androidx.compose.ui.test.accessibility`. Use them when your team is already investing heavily in Compose-first test infrastructure.

For most teams, the practical starting point is still:

- run Espresso accessibility checks on end-to-end flows
- add Compose semantics assertions where needed
- back this up with manual TalkBack checks on critical journeys

## What To Cover

- primary onboarding and auth flows
- checkout or purchase flows
- navigation landmarks
- dialogs, sheets, snackbars, and error states
- icon-only buttons and tappable graphics

## Related Resources

- [Compose Testing](compose-testing.md)
- [Espresso Patterns](espresso-patterns.md)
- [Adaptive Screen-Size Testing](adaptive-screen-testing.md)
