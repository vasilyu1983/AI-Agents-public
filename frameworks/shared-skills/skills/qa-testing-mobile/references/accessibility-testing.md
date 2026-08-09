# Mobile Accessibility Testing

Accessibility coverage for mobile apps should combine automated checks with targeted manual validation on real devices.

## When To Use

- Release-readiness reviews for iOS and Android apps
- Regression coverage for accessibility-sensitive screens
- Audit planning for dynamic type, screen readers, focus order, and semantics

## iOS

- Use XCTest accessibility audits where the app and Xcode version support them.
- Treat audit output as a release signal, not the only source of truth.
- Pair automated audits with manual VoiceOver and Dynamic Type checks on critical flows.

Example release-gate questions:

- Do auth, checkout, and settings screens pass the accessibility audit without high-severity issues?
- Do important controls expose stable labels, traits, and focus order?
- Does the app remain usable with larger text sizes?

## Android

- Use Compose accessibility testing guidance for semantics, labels, focus behavior, and touch target validation.
- For View-based UIs, keep content descriptions and accessibility traversal explicit and testable.
- Pair automated checks with TalkBack smoke runs on critical flows.

Example release-gate questions:

- Do primary actions expose clear semantics and labels?
- Are error states announced and reachable?
- Do critical flows stay usable at larger font and display sizes?

## Manual Checks That Still Matter

- Screen reader flow for first-run, auth, and revenue-critical journeys
- Dynamic type / font scaling
- Color contrast and non-color-only states
- Focus order after modals, sheets, and navigation changes
- Motion reduction or animation-heavy screens if supported

## axe DevTools Mobile (Deque)

axe DevTools Mobile is Deque's automated accessibility testing solution for native iOS and Android apps. It is the mobile analogue of axe-core for web: it brings the same WCAG-mapped rule engine to native app accessibility trees rather than to DOM elements.

**What it covers (verified against deque.com and docs.deque.com, May 2026):**

- Native iOS apps (SwiftUI, UIKit) and native Android apps (Jetpack Compose, XML layouts)
- Cross-platform frameworks: React Native, Flutter, .NET MAUI (verify current list against Deque's axe DevTools Mobile docs — framework support evolves)
- Checks include color contrast, touch target size, accessible naming, dynamic type support, and screen orientation — mapped to WCAG and platform-specific guidelines
- Two main modes: interactive scanning via a desktop Mobile Analyzer app (no source-code access required), and programmatic integration into XCUITest and Appium suites for CI/CD pipelines

**Automated-vs-manual split — same as web a11y:**

Automated scanning catches structurally detectable issues (missing labels, insufficient touch targets, contrast failures) but does not replace manual assistive-technology verification. The automated-vs-manual split mirrors what web a11y teams already know from axe-core: axe-core finds roughly 30–57% of WCAG issues automatically; the rest require manual review. Apply the same mental model to mobile: axe DevTools Mobile raises the floor, but VoiceOver (iOS) and TalkBack (Android) manual checks on real critical flows remain required gates.

The Deque docs include a "What's Left to Test?" / remaining checklist section, which confirms the tool is explicitly designed to complement — not replace — manual assistive-technology testing.

**Positioning in the mobile test strategy:**

Add axe DevTools Mobile as the automated layer in the accessibility tier alongside the native-framework checks (XCTest accessibility audits on iOS, Compose accessibility testing on Android). Manual VoiceOver and TalkBack runs on the highest-risk flows (auth, checkout, onboarding) remain mandatory and are not superseded by automated scanning.

**Commercial / access model:** axe DevTools Mobile is a paid commercial product (verify current pricing and licensing at deque.com — not independently confirmed here).

**Primary source:** [Axe DevTools for Mobile — deque.com](https://www.deque.com/axe/devtools/mobile-accessibility/) | [docs.deque.com/devtools-mobile](https://docs.deque.com/devtools-mobile/)

---

## Primary Sources

- Apple XCTest accessibility audit docs
- Android Compose accessibility testing docs
- Deque axe DevTools Mobile: https://www.deque.com/axe/devtools/mobile-accessibility/ and https://docs.deque.com/devtools-mobile/
- Verify current API behavior and framework support with official docs before citing exact details
