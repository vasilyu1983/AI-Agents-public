---
description: Mobile Product — extracted from monolith for progressive disclosure.
last_verified: 2026-09-02
status: stable
---

## Mobile Product

**Typical scenario**

You need a cross-platform mobile read on a feature before implementation or release.

**Claude prompt**

```text
Run the saved `expert-board` workflow with `board: "mobile-product"`.

Scenario: Plan and review a new mobile onboarding flow that spans permissions, account creation, and the first value-delivery moment on both iOS and Android.

Required context:
- target flow and release timeline
- platform targets: iOS and Android
- optional evidence: build notes, screenshots, test evidence

Instructions:
- software-mobile-architect defines the cross-platform delivery and ownership model
- software-ios-specialist reviews the iOS-native implementation and UX implications
- software-android-specialist reviews the Android-native implementation and UX implications
- qa-mobile-release-reviewer reviews test confidence and release risk
- Blind memos first, then one chaired synthesis of the mobile delivery recommendation
- The workflow returns one chaired synthesis with mandatory dissent; nothing to clean up
```

**Codex prompt**

```text
Spawn mobile_architect, ios_specialist, android_specialist, and mobile_release_reviewer.

Task: plan and review a cross-platform mobile onboarding flow for iOS and Android.

Return:
- architecture and sequencing recommendation
- iOS-specific issues
- Android-specific issues
- release confidence and missing test evidence
```
