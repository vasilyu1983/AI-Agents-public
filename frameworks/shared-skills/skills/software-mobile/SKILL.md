---
name: software-mobile
description: "Guides mobile platform selection and delivery across native and cross-platform stacks. Use when planning auth, push, deep links, releases, or app architecture for iOS/Android."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Mobile Development

Use this skill for platform choice, cross-platform tradeoffs, Android implementation guidance, and shared mobile concerns such as authentication, notifications, deep linking, release readiness, and policy checks. For deep native iOS implementation or rewrite work, route to [software-ios-native](../software-ios-native/SKILL.md). For native iOS build, install, packaging, or stale-app debugging, route to [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md).

## Quick Reference

| Task | iOS | Android | Cross-Platform | Default |
|------|-----|---------|----------------|---------|
| UI | SwiftUI + UIKit interop | Jetpack Compose + Views interop | React Native, Flutter, KMP + native UI | Native first for platform-heavy work |
| State | `@State`, `@Observable`, `@Environment` | ViewModel + StateFlow | Zustand/RTK, Riverpod, shared domain state | Platform-native state models |
| Navigation | `NavigationStack` | Navigation Compose / Navigation Component | Expo Router or React Navigation | Expo Router for greenfield Expo apps |
| Networking | `URLSession` + async/await | Retrofit/OkHttp/Ktor + coroutines | Fetch/Axios, generated clients | Typed clients over ad hoc fetches |
| Storage | SwiftData/Core Data, Keychain | Room/DataStore, Keystore | MMKV/SQLite/WatermelonDB, secure storage | Keep secrets in platform secure storage |
| Testing | Swift Testing + XCTest UI | JUnit + Compose Test + Macrobenchmark | Detox/Maestro, framework-native tests | Measure performance, do not assume it |
| Release | Privacy manifests, App Review checks | Play target SDK, Data safety, Integrity | Expo/EAS or native pipelines | Re-check store policy before each cut |
| iOS CI | Xcode Cloud `ci_scripts/ci_post_clone.sh` for generated files | Gradle Play Publisher or managed pipelines; Play Integrity for signing | EAS Build / Codemagic for RN/Expo | Platform-managed CI for submission |
| Push proof | Xcode real-device → APNs `sandbox` | FCM debug / prod separation by config | Production send path must prove delivery per environment | Never treat local push success as TestFlight proof |

## When to Use This Skill

Use this skill when you need:

- Platform selection between native iOS, native Android, React Native, Flutter, Kotlin Multiplatform, and wrapper shells
- Android app development with Kotlin, Jetpack Compose, ViewModel, StateFlow, and WorkManager
- Cross-platform decisions across React Native, Expo, Flutter, Kotlin Multiplatform, and WebView shells
- Mobile auth, passkeys, push notifications, offline-first sync, deep links, and app-store release preparation
- Backend translation pipeline design for localized prose delivery to mobile clients

## When NOT to Use This Skill

| Need | Use Instead |
|------|-------------|
| Web-only frontend | [software-frontend](../software-frontend/SKILL.md) |
| Backend API implementation | [software-backend](../software-backend/SKILL.md) |
| Managed app-backend (Supabase, Firebase, Appwrite) | [software-baas-platforms](../software-baas-platforms/SKILL.md) |
| Native iOS app skeleton with iCloud/CloudKit/App Intents/Foundation Models | [software-ios-native](../software-ios-native/SKILL.md) + [software-ios-ai-engine](../software-ios-ai-engine/SKILL.md) |
| Native iOS rewrite, SwiftUI, or Xcode workflows | [software-ios-native](../software-ios-native/SKILL.md) |
| Native iOS build/install/launch failures, stale-app, simulator drift | [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md) |
| Native iOS visual audits | [software-ios-design](../software-ios-design/SKILL.md) |
| iOS-specific testing deep dives | [qa-testing-ios](../qa-testing-ios/SKILL.md) |
| Native Android rewrite, Kotlin, Gradle, Android Studio | [software-android-native](../software-android-native/SKILL.md) |
| Native Android build/install/launch failures, emulator drift | [software-android-runtime-debugging](../software-android-runtime-debugging/SKILL.md) |
| Native Android visual audits | [software-android-design](../software-android-design/SKILL.md) |

## Platform Selection

```text
Need to ship mobile product?
    │
    ├─ Single platform only?
    │   ├─ iOS → SwiftUI for new code, UIKit interop where needed
    │   └─ Android → Jetpack Compose for new code, Views interop where needed
    │
    ├─ Both iOS and Android?
    │   ├─ Native integrations / performance / platform fidelity dominate? → Separate native apps
    │   ├─ JS/TS team and fastest shared delivery? → React Native + Expo-managed for greenfield
    │   ├─ Fully shared rendering and custom UI control? → Flutter
    │   └─ Kotlin team, shared logic, native UI? → Kotlin Multiplatform
    │
    └─ Existing web app wrapper?
        ├─ Low-complexity shell → WebView / Capacitor
        └─ Meaningful native features → React Native or native modules
```

### Cross-Platform Defaults (July 2026)

| Framework | Default | Status |
|-----------|---------|--------|
| React Native | New Architecture is now the only architecture — Legacy Architecture has been removed from current RN/Expo releases, not merely opt-out. The decision point has shifted from "should we adopt it" to "is every native module/library we depend on migrated" | Mandatory, not opt-in |
| Expo + Expo Router | Fastest greenfield path unless bare/native-heavy control needed early; current Router major version ships file-based routing plus brownfield-embedding support | Active default |
| Flutter | Strong when shared rendering and animation control matter more than native feel | Active |
| Kotlin Multiplatform | Best fit for shared business logic with native UI; Compose Multiplatform for iOS reached stable in 2025 and has continued shipping performance-focused releases since (concurrent rendering, native text input) | Validate library maturity per release, not from a single stability announcement |

## Workflow

1. Confirm product scope, platform targets, native requirements, and release constraints.
2. Route web-only, backend, or iOS-native deep dives to adjacent skills.
3. Choose the stack from the selection guidance above.
4. Apply guidance for auth, push, offline behavior, release gates, and testing.
   - For iOS push: prove the local `sandbox` path and the `production` path separately.
   - Treat push signoff as two gates: transport proof (notification accepted and shown) and open-path proof (tapping from cold start and warm start does not freeze or crash).
5. Re-check current platform-policy and framework facts before final recommendations.

```text
Mobile task
  -> Identify platform mix, app type, and user-facing surface
  -> Route deep native work to iOS or Android specialist skills
  -> Define architecture, state, navigation, storage, and release gates
  -> Implement bounded slice with accessibility and localization checks
  -> Build, install, launch, test, and capture proof
  -> Report platform-specific blockers and handoffs
```

## Platform Defaults

### iOS

- SwiftUI for new screens; UIKit interop for mature or heavily customized flows.
- `@Observable` on iOS 17+; keep `ObservableObject` only when supporting older baselines.
- Swift Concurrency throughout; keep UI-facing state on `@MainActor`.
- Swift Testing for unit tests; XCTest for UI/legacy coverage.
- Privacy manifests, required-reason APIs, and App Review requirements are hard release gates.
- Backend routing authoritative per device row (`push_environment`); verify the newest row after every install type change.
- iOS push QA: validate the notification-open path explicitly after transport succeeds — tap from cold start, tap from warm resume, force-close and relaunch normally.
- Before TestFlight upload, inspect archived app entitlements: confirm `aps-environment = production`.

### iOS Release Operations

| Gate | Rule |
|------|------|
| TestFlight channels | internal → external (Beta App Review) → public link |
| Upload path | App Store Connect Organizer → `App Store Connect`. `Release Testing` is not the submission route. |
| Backend/content vs binary | Backend fixes that don't change the binary, native UI, capabilities, or App Review-visible behavior do not require a new iOS release. |
| Smoke proof | Real-iPhone TestFlight smoke: production APNs delivery + product loading + purchase + restore + relaunch. |
| Minimum SDK for upload | Apple periodically raises the minimum Xcode/SDK version accepted at App Store Connect (e.g., the iOS/iPadOS 26 SDK plus Xcode 26+ became mandatory for new uploads in April 2026) — check [developer.apple.com/news/upcoming-requirements](https://developer.apple.com/news/upcoming-requirements/) before any archive/upload, since a passing local build can still be rejected at ingestion. |

### Android

- Jetpack Compose for new UI; Views only for interop or legacy.
- ViewModel + StateFlow; LiveData is maintenance-mode for older View-based code only.
- WorkManager for guaranteed background work; Credential Manager for passkeys/password/federated sign-in.
- Baseline Profiles and Macrobenchmark for startup and scroll performance.
- Play target SDK policy, Data safety, and Play Integrity are hard release gates.
- New apps and updates must target API 36 / Android 16 by August 31, 2026 (extension requests can push individual apps to November 1, 2026); existing published apps must target at least API 35 / Android 15 to remain visible on Android 16+/17 devices. This deadline moves every year — re-check [developer.android.com/google/play/requirements/target-sdk](https://developer.android.com/google/play/requirements/target-sdk) before every release, don't reuse a cached deadline.

## Known Platform Traps

### iOS

- `_performBlockAfterCATransactionCommitSynchronizes:` / "Call must be made on main thread" is a **private SwiftUI symbol**, not user-code. Web-search the signature before any code review.
- Once APNs accepts a push payload and the banner appears, any freeze or crash after tapping belongs to the **app-side open path** (delegate isolation, pending-route races, off-main UI mutations) — not to transport.
- `dataCorrupted` + `<!DOCTYPE html>` is an API routing / auth bug, not a concurrency bug.
- Xcode 26 default TLS Client Hello changed: apps talking to servers with strict TLS-fingerprint allowlists may see login or API failures on fresh builds — verify against staging.

### Android / Kotlin

- `android.view.ViewRootImpl$CalledFromWrongThreadException` and `ConcurrentModificationException` inside `SnapshotStateObserver` are the Android parallels to iOS main-thread crashes. They surface when a `MutableStateFlow` backing UI state is mutated from `Dispatchers.IO` while Compose is reading it on the main thread.
- Safe pattern: do blocking work inside `withContext(Dispatchers.IO) { ... }`, return a plain value, then assign to `_uiState.value` on the main thread. Collect in composables via `collectAsStateWithLifecycle()`.
- Kotlin 2.x + Strong Skipping Mode: emitting a fresh `data class` instance per field on every ViewModel event defeats Compose's identity-based skip check. Split UI state into `@Immutable` sub-objects; hoist derived lists with `stateIn`; wrap per-row callbacks in `remember(id) { { ... } }`.
- When `adb logcat` shows the crash includes `SnapshotStateObserver`, `MonotonicFrameClock`, or `Recomposer`, route to [software-android-native](../software-android-native/SKILL.md) and [software-android-runtime-debugging](../software-android-runtime-debugging/SKILL.md).

## Expert Judgment Calls

Non-experts see a working build and call it done. An expert checks the cases where "it built and ran once" is not the same as "it will pass review, survive an audit, or work for the next user."

- **Cross-platform regret is asymmetric.** Moving from native to shared code is a full rewrite; moving from shared code to native is usually a partial, surgical one (pull out the hot path, keep the rest). When timeline pressure forces a shared-framework choice, explicitly list which native integrations (camera pipelines, ARKit/ARCore, background audio, CarPlay/Android Auto, widgets, App Intents/App Actions) are foreseeable within 12 months — those are the ones that force a native escape hatch later, and the earlier you know, the cheaper the hedge (e.g., isolate the module behind a platform-abstraction boundary from day one).
- **One native escape hatch usually means you need native hiring anyway.** Teams under-price this: a single deep native module (e.g., a custom camera pipeline or a hardware SDK) requires the same iOS/Android specialist skill as a fully native app, just applied to a smaller surface. Budget the hire, not just the sprint.
- **App Review rejection risk hides in account and auth flows, not UI polish.** The most common late-stage iOS rejections a non-expert misses: (1) Guideline 5.1.1(v) — in-app account deletion that actually deletes the record and revokes tokens, not just deactivates; (2) Sign in with Apple parity — if the app offers any third-party or social login, Sign in with Apple must be offered too, at equal prominence; (3) subscription flows that don't expose "Cancel Subscription" reachably inside the app or account settings. Verify all three before submission, every release — Apple periodically increases enforcement on these without a version bump to announce it.
- **Push permission priming is a judgment call, not a technical one.** Requesting notification permission on first launch reliably produces "Don't Allow" from most users, who then never see the system prompt again. An expert defers the OS prompt until the user has taken an action that makes the value of push obvious (e.g., after placing an order), and separately audits whether the soft-ask copy itself needs its own re-prompt path if declined.
- **Offline-first correctness is a conflict-resolution decision, not a caching decision.** Before implementing local-first storage, force an explicit answer to "what happens when two devices edit the same record while offline" — last-write-wins, field-level merge, or user-facing conflict UI. Silence on this question means the team will discover the answer in production, from a support ticket.
- **A shared entitlement registry is cheaper before launch than after.** Apps that sell both in-store (StoreKit/Play Billing) and web/Stripe entitlements without one canonical source of truth accumulate silent state drift (a user paid on web, app still shows locked) that is expensive to retrofit once both paths have real users.
- **Framework benchmark claims decay faster than they're written.** A blog post claiming "Flutter is now as fast as native" or "RN startup time improved 40%" is a snapshot of one app, one release, one device. Treat every unsourced performance claim as a hypothesis to verify with Instruments/Macrobenchmark on the actual product, not a fact to design around.

## Release Readiness Checklist

### iOS App Store

- [ ] Icons, launch assets, and permission copy are complete
- [ ] Privacy manifest and required-reason APIs are correct for app targets and listed SDKs
- [ ] Third-party SDK compliance matches Apple's current requirements
- [ ] Accessibility, deep links, and push flows tested on current devices
- [ ] App Store metadata, privacy policy, and TestFlight coverage ready
- [ ] Full App Store Connect preparation — see [references/app-store-connect-checklist.md](references/app-store-connect-checklist.md)

### Google Play

- [ ] Target SDK matches the latest Play policy (API 36 / Android 16 required for new apps and updates by August 31, 2026 — re-verify the current deadline, it moves annually)
- [ ] Privacy policy, content rating, and Data safety complete
- [ ] Integrity, auth, and background behavior tested under modern Android constraints
- [ ] Internal/closed/open tracks configured appropriately

## Common Anti-Patterns

| Anti-Pattern | Problem | Better Default |
|--------------|---------|----------------|
| Unsourced framework benchmarks | Misleads architecture decisions | Measure with Instruments, Macrobenchmark, and real-device runs |
| Treating old policy dates as timeless | Store submission failures | Re-check Apple/Google policy pages before release |
| Defaulting to LiveData in new Android apps | Older reactive model | ViewModel + StateFlow for new work |
| Treating Expo as "just React Native tooling" | Missed routing/OTA ergonomics | Use Expo Router and EAS deliberately |
| Fingerprinting-based deferred deep links | Reliability and privacy issues | Verified Universal/App Links plus approved attribution flows |
| SafetyNet Attestation on Android | Deprecated | Play Integrity API |
| Mixed web + store entitlements without one canonical registry | Conflicting access state | One entitlement registry with documented conflict-resolution rule before launch |
| Treating mobile billing policy as static | Store rejection | Re-verify Apple and Google billing policy before release and major monetization changes |

## Known Traps

- Assuming one mobile framework decision solves release, entitlement, deep-link, and push behavior without platform-specific proof
- Validating auth, push, or deep links only in local debug builds and treating that as production readiness
- Mixing sandbox, staging, and production mobile backends until install-specific behavior becomes impossible to reproduce
- Using emulator or simulator success as proof for background execution, notification delivery, or device-specific lifecycle
- Choosing a cross-platform stack before listing native integrations, extension points, and store-policy constraints that can force native escape hatches

## Navigation

### References

- [references/ios-best-practices.md](references/ios-best-practices.md) — iOS architecture, concurrency, testing, accessibility, release
- [references/android-best-practices.md](references/android-best-practices.md) — Android architecture, Compose, coroutines, testing, performance
- [references/cross-platform-comparison.md](references/cross-platform-comparison.md) — React Native / Flutter / KMP / native tradeoffs
- [references/deep-linking-guide.md](references/deep-linking-guide.md) — Universal Links, App Links, Expo Router, post-Dynamic-Links
- [references/mobile-testing-patterns.md](references/mobile-testing-patterns.md) — test pyramid, device strategy, snapshot/UI/E2E
- [references/offline-first-architecture.md](references/offline-first-architecture.md) — local-first storage, sync, conflict resolution
- [references/push-notifications-guide.md](references/push-notifications-guide.md) — APNs, FCM, permissions, channels, analytics
- [references/operational-playbook.md](references/operational-playbook.md) — release operations, decision tables, centralized patterns
- [references/app-store-connect-checklist.md](references/app-store-connect-checklist.md) — App Store Connect field-by-field checklist
- [references/backend-translation-pipeline.md](references/backend-translation-pipeline.md) — i18n patterns for backend-generated prose delivered to mobile clients
- [data/sources.json](data/sources.json) — current official and curated external sources

### Shared Checklists And Utilities

- [../software-clean-code-standard/assets/checklists/mobile-release-checklist.md](../software-clean-code-standard/assets/checklists/mobile-release-checklist.md)
- [../software-clean-code-standard/references/auth-utilities.md](../software-clean-code-standard/references/auth-utilities.md)
- [../software-clean-code-standard/references/error-handling.md](../software-clean-code-standard/references/error-handling.md)
- [../software-clean-code-standard/references/resilience-utilities.md](../software-clean-code-standard/references/resilience-utilities.md)
- [../software-clean-code-standard/references/testing-utilities.md](../software-clean-code-standard/references/testing-utilities.md)
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md)

### Templates

- **Swift**: [assets/swift/template-swift.md](assets/swift/template-swift.md), [assets/swift/template-swift-concurrency.md](assets/swift/template-swift-concurrency.md), [assets/swift/template-swift-combine.md](assets/swift/template-swift-combine.md), [assets/swift/template-swift-performance.md](assets/swift/template-swift-performance.md), [assets/swift/template-swift-testing.md](assets/swift/template-swift-testing.md)
- **SwiftUI**: [assets/swiftui/template-swiftui-advanced.md](assets/swiftui/template-swiftui-advanced.md)
- **Kotlin / Android**: [assets/kotlin/template-kotlin.md](assets/kotlin/template-kotlin.md), [assets/kotlin/template-kotlin-coroutines.md](assets/kotlin/template-kotlin-coroutines.md), [assets/kotlin/template-kotlin-compose-advanced.md](assets/kotlin/template-kotlin-compose-advanced.md), [assets/kotlin/template-kotlin-testing.md](assets/kotlin/template-kotlin-testing.md)
- **Cross-platform**: [assets/cross-platform/template-platform-patterns.md](assets/cross-platform/template-platform-patterns.md), [assets/cross-platform/template-webview.md](assets/cross-platform/template-webview.md)

### Related Skills

- [software-ios-native](../software-ios-native/SKILL.md) — Native iOS 17+ implementation, rewrites, and agent workflows
- [software-ios-ai-engine](../software-ios-ai-engine/SKILL.md) — Apple Foundation Models, local AI engines, on-device retrieval
- [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md) — Build/install/launch proof, simulator drift, packaging triage
- [software-ios-design](../software-ios-design/SKILL.md) — Native iOS visual hierarchy, HIG, screenshot review
- [software-android-native](../software-android-native/SKILL.md) — Native Android, Kotlin, Jetpack Compose, agent workflows
- [software-android-design](../software-android-design/SKILL.md) — Material Design 3, screenshot review
- [software-android-runtime-debugging](../software-android-runtime-debugging/SKILL.md) — Android build/install/launch proof, emulator drift
- [software-frontend](../software-frontend/SKILL.md) — Web UI and shared product surfaces
- [software-backend](../software-backend/SKILL.md) — API design, auth, backend contracts
- [software-baas-platforms](../software-baas-platforms/SKILL.md) — Supabase, Firebase, Appwrite, PocketBase
- [qa-testing-strategy](../qa-testing-strategy/SKILL.md) — CI gates, reliability, release confidence
- [qa-resilience](../qa-resilience/SKILL.md) — Network resilience and failure-mode design
- [qa-testing-ios](../qa-testing-ios/SKILL.md) — iOS-specific testing
- [software-ui-ux-design](../software-ui-ux-design/SKILL.md) — Mobile UX and accessibility

## Fact-Checking

Store policy deadlines, minimum SDK/Xcode requirements, and framework architecture defaults (React Native, Expo, Kotlin/Compose Multiplatform) change on their own release cadence and are wrong within months if hardcoded. Before quoting any date, version, or percentage in this skill or its references, verify it against a current primary source — Apple Developer News/Release Notes, Google Play Console Help, the framework's official changelog — rather than this file's memory of it. If a source can't be reached and the fact is load-bearing (a submission gate, a deadline, a required minimum version), say so explicitly and flag the guidance as unverified rather than stating it as current fact.

Always re-verify before release or final recommendation:
- Apple release notes, minimum Xcode/SDK version for App Store Connect uploads, third-party SDK requirements, App Review Guidelines
- Google Play target API policy and deadline, Android release behavior, Credential Manager, Play Integrity
- React Native and Expo changelogs (architecture status, routing, OTA)
- Kotlin Multiplatform and Compose Multiplatform release notes

## Freshness Protocol

When users ask recommendation or "what's current" questions, use web search first. If unavailable, answer from `data/sources.json` and mark guidance as potentially stale.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
