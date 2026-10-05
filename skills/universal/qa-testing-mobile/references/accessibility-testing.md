# Mobile Accessibility Testing

The API-level detail lives in the owning skills. This file keeps the cross-platform release-gate view.

- iOS and Android APIs, including `performAccessibilityAudit`, Espresso/Compose accessibility checks, VoiceOver and TalkBack protocols, touch targets and CI wiring: [qa-testing-accessibility mobile-accessibility.md](../../qa-testing-accessibility/references/mobile-accessibility.md)
- Android-specific checks: [qa-testing-android accessibility-checks.md](../../qa-testing-android/references/accessibility-checks.md)

## Release-Gate Questions

Ask these of every release candidate, on both platforms:

- Do auth, checkout, onboarding and settings screens pass the platform audit with no high-severity issues?
- Do primary controls expose stable labels, traits/roles and a sensible focus order, including after modals, sheets and navigation changes?
- Are error states announced and reachable by screen reader?
- Do critical flows stay usable at the largest Dynamic Type / font-scale and display-size settings?
- Did someone run a manual VoiceOver and TalkBack pass on the revenue-critical journeys? Automated audits raise the floor but do not replace this.

## axe DevTools Mobile (Deque)

Deque's commercial scanner for native iOS/Android plus React Native, Flutter and .NET MAUI (verify the current framework list in Deque's docs). It runs interactively through a desktop analyzer or programmatically inside XCUITest and Appium suites. Treat it as an extra automated layer next to the native audits, not a substitute for manual assistive-technology checks; Deque's own docs include a "What's Left to Test?" checklist for that reason. Pricing and licensing: verify at deque.com.

Sources: <https://www.deque.com/axe/devtools/mobile-accessibility/>, <https://docs.deque.com/devtools-mobile/>
