---
name: software-mobile
description: "Guides mobile platform selection and delivery across native and cross-platform stacks. Use when planning auth, push, deep links, releases, or app architecture for iOS/Android."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.2"
last_validated: 2026-07-11
---

# Mobile Development

Use this skill for platform choice, cross-platform tradeoffs, and shared mobile concerns such as authentication, notifications, deep linking, release readiness, and policy checks. For deep native iOS implementation or rewrite work, route to [software-ios-native](../software-ios-native/SKILL.md). For native iOS build, install, packaging, or stale-app debugging, route to [software-ios-runtime-debugging](../software-ios-runtime-debugging/SKILL.md). For native Android implementation, route to [software-android-native](../software-android-native/SKILL.md).

## Quick Reference

| Task | iOS | Android | Cross-Platform | Default |
|------|-----|---------|----------------|---------|
| UI | SwiftUI + UIKit interop | Jetpack Compose + Views interop | React Native, Flutter, KMP + native UI | Native first for platform-heavy work |
| State | `@State`, `@Observable`, `@Environment` | ViewModel + StateFlow | Zustand/RTK, Riverpod, shared domain state | Platform-native state models |
| Navigation | `NavigationStack` | Navigation Compose / Navigation Component | Expo Router or React Navigation | Expo Router for greenfield Expo apps |
| Networking | `URLSession` + async/await | Retrofit/OkHttp/Ktor + coroutines | Fetch/Axios, generated clients | Typed clients over ad hoc fetches |
| Storage | SwiftData/Core Data, Keychain | Room/DataStore, Keystore | MMKV/SQLite/WatermelonDB, secure storage | Keep secrets in platform secure storage |
| Testing | Swift Testing + XCTest UI | JUnit + Compose Test + Macrobenchmark | Detox/Maestro, framework-native tests | Measure performance, do not assume it |
| Release | Privacy manifests, App Review checks | Play target SDK, Data safety, signing | Expo/EAS or native pipelines | Re-check store policy before each cut |
| CI / signing | Xcode Cloud or native CI | Gradle signing / Play App Signing | EAS Build or native pipelines | Prove release signing separately from app attestation |
| Push proof | Xcode real-device → APNs `sandbox` | FCM debug / prod separation by config | Production send path must prove delivery per environment | Never treat local push success as TestFlight proof |

## When to Use This Skill

Use this skill when you need:

- Platform selection between native iOS, native Android, React Native, Flutter, Kotlin Multiplatform, and wrapper shells
- Cross-platform decisions across React Native, Expo, Flutter, Kotlin Multiplatform, and WebView shells
- Mobile auth, passkeys, push notifications, offline-first sync, deep links, and app-store release preparation

## When NOT to Use This Skill

| Need | Use Instead |
|------|-------------|
| Web-only frontend | [software-frontend](../software-frontend/SKILL.md) |
| Strings, plurals, catalogs, translation pipeline, backend-generated localized prose | [software-localisation](../software-localisation/SKILL.md) ([backend prose reference](../software-localisation/references/backend-generated-content-i18n.md)) |
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

### Cross-Platform Defaults

| Framework | Default | Status |
|-----------|---------|--------|
| React Native | New Architecture is mandatory in current RN releases: the Legacy Architecture is removed and `newArchEnabled=false` is ignored. Check the RN release notes for the cutoff version and the Expo SDK changelog for the last Legacy-capable SDK. The decision point is "is every native module/library we depend on migrated or covered by the interop layer" | Mandatory, not opt-in |
| Expo + Expo Router | Team default for a JS/TS greenfield app; use a development build for custom native code and check the installed Router release for embedding support | Active default |
| Flutter | Strong when shared rendering and animation control matter more than native feel | Active |
| Kotlin Multiplatform | Best fit for shared business logic with native UI; Compose Multiplatform for iOS is stable; check its release notes for what the current release adds | Validate library maturity per release, not from a single stability announcement |

## Workflow

1. Confirm product scope, platform targets, native requirements, and release constraints.
2. Route web-only, backend, or iOS-native deep dives to adjacent skills.
3. Choose the stack from the selection guidance above.
4. Apply guidance for auth, push, offline behavior, release gates, and testing.
   - For iOS push: prove the local `sandbox` path and the `production` path separately.
   - Treat push signoff as two gates: transport proof (notification accepted and shown) and open-path proof (tapping from cold start and warm start does not freeze or crash).
5. Re-check current platform-policy and framework facts before final recommendations.

### Platform-Choice Proof Gate

Before committing to native, React Native, Flutter, or KMP, list the product's hardest likely capability: background execution, camera/media pipeline, Bluetooth/hardware SDK, widgets/extensions, deep links, offline conflict resolution, payments, accessibility, or platform-specific UI. Rank each candidate's uncertainty and consequence. Reuse existing evidence when it covers the same framework and version range, native dependency, release configuration, capability, and representative device class; record its date and owner.

Run a time-boxed spike only for serious finalists with a material unresolved native, performance, lifecycle, accessibility, or packaging risk. Define pass/fail before it: build and package, native SDK integration, cold-start and interaction budget, accessibility behavior, offline/recovery behavior, and maintainer skill. Use the real release configuration and the oldest device class relevant to that risk. If the spike consumes paid services, signing capacity, scarce devices, or shared CI quota outside the agreed task budget, obtain authorization for that resource use first. For low-risk products, a documented decision with applicable production evidence and explicit assumptions is sufficient. If the hardest capability fails or requires a permanent bespoke native module, include that module's two-platform ownership cost in the decision; if no hard capability exists, favor the stack that reduces duplicated product work.

### Capability and Native Escape Hatches

Load [cross-platform-comparison.md](references/cross-platform-comparison.md) when weighing shared delivery against native ownership. Use this catalog to identify the native work the chosen stack still needs:

| Stack | Escape hatch | Capability to prove before committing |
|-------|--------------|-------------------------------------|
| Separate native apps | Swift/Objective-C and Kotlin/Java SDKs directly | Two-platform implementation and release ownership |
| React Native / Expo | [Turbo Native Modules](https://reactnative.dev/docs/turbo-native-modules-introduction), or [Expo Modules](https://docs.expo.dev/workflow/customizing/) in a development build | Hardware SDK, background lifecycle, and native dependency compatibility; Expo Go cannot load arbitrary native modules |
| Flutter | [Platform channels / Pigeon](https://docs.flutter.dev/platform-integration/platform-channels), plugins, native views | Camera/media throughput, platform-view composition, and channel threading |
| KMP with native UI | Platform source sets and iOS framework integration | Swift-facing API, Kotlin/Native library support, packaging and symbolication |
| Compose Multiplatform | Platform APIs and native UI interop where shared UI lacks the required surface | Accessibility, input, platform-specific UI, extensions and lifecycle |
| Capacitor / WebView | [Native plugins](https://capacitorjs.com/docs/plugins) and a native host | Background execution, hardware APIs and extension targets; browser APIs alone do not supply these capabilities |

**KMP iOS toolchain gate.** Apple final binaries require a macOS host and Xcode even when business logic is shared. Read the [Kotlin/Gradle/AGP/Xcode compatibility matrix](https://kotlinlang.org/docs/multiplatform/multiplatform-compatibility-guide.html) for the project's Kotlin plugin and [supported targets/hosts](https://kotlinlang.org/docs/native-target-support.html) for device/simulator architectures. Choose [direct Xcode integration or dependency-manager integration](https://kotlinlang.org/docs/multiplatform/multiplatform-ios-integration-overview.html) according to existing CocoaPods dependencies and module distribution needs; prove both a simulator build and a signed device archive.

**Attestation gate.** For sensitive server actions, evaluate [App Attest](https://developer.apple.com/documentation/devicecheck/establishing-your-app-s-integrity) and [Play Integrity](https://developer.android.com/google/play/integrity/overview) through the stack's native module/plugin. Verify results on the server and bind them to a fresh challenge or request content. Check device/API availability and release distribution before enforcing; define behavior for unsupported devices and outages. Attestation is an abuse signal, alongside authentication and authorization, and is not a universal store-submission requirement. Detailed threat modeling and secure storage belong to [software-security-appsec](../software-security-appsec/SKILL.md).

## Platform Delivery Gates

- **iOS:** Route architecture, state, concurrency and performance to [software-ios-native](../software-ios-native/SKILL.md). Check privacy manifests, required-reason APIs and SDK compliance before submission. Validate APNs transport and notification opening for each install environment; inspect the distribution archive's `aps-environment` entitlement and keep its token routing aligned with that environment.
- **Android:** Route Compose, state, background work and performance to [software-android-native](../software-android-native/SKILL.md). Read the current [Play target-API requirements](https://developer.android.com/google/play/requirements/target-sdk) for app type and release track, then verify Data safety, signing and background restrictions. Evaluate Play Integrity when abuse risk warrants it.

### Release Operations, Traps, and Judgment Calls

iOS release-operation gates (TestFlight channels, upload path, backend-only fixes, real-device smoke proof, minimum Xcode/SDK for upload), known iOS and Android runtime traps, expert judgment calls, and the anti-pattern table live in [references/platform-traps-and-judgment.md](references/platform-traps-and-judgment.md). Load it before a release cut, a push/open-path investigation, or a platform-choice recommendation.

- Before any archive/upload, check [developer.apple.com/news/upcoming-requirements](https://developer.apple.com/news/upcoming-requirements/) for the minimum Xcode/SDK; a passing local build can still be rejected at ingestion.
- Review account deletion, login-service requirements and subscription disclosures/cancellation under the applicable App Review clauses; auth alone does not make Sign in with Apple mandatory.

## OTA Updates and External Payments

Both are store-policy decisions that change often. Decision logic, operating rules, and primary-page links are in [references/store-update-and-payment-policy.md](references/store-update-and-payment-policy.md).

- **OTA / code push.** Check Apple Guideline 2.5.2 and its interpreted-code license clause separately from Google Play's interpreter exception. A JS bundle is not blanket permission to change functionality. Default to a store build for native changes or new features; use an OTA only after checking the applicable policy, runtime compatibility, staged rollout and rollback in the reference.
- **External payments / anti-steering.** US-storefront link-outs and regional alternative-billing or external-offer programs exist on both stores. Eligibility, entitlements, disclosure UI, and remaining fees vary by storefront and change after rulings. Decide per storefront from the Apple guidelines/StoreKit External Purchase pages and the Google Play Payments/billing-program pages at decision time. Branch server-side on the store-reported storefront and keep a kill switch back to store billing. Never quote a fee or date from memory.

## Release Readiness Checklist

### iOS App Store

- [ ] Icons, launch assets, and permission copy are complete
- [ ] Privacy manifest and required-reason APIs are correct for app targets and listed SDKs
- [ ] Third-party SDK compliance matches Apple's current requirements
- [ ] Accessibility, deep links, and push flows tested on current devices
- [ ] App Store metadata, privacy policy, and TestFlight coverage ready
- [ ] Full App Store Connect preparation — see [references/app-store-connect-checklist.md](references/app-store-connect-checklist.md)

### Google Play

- [ ] Target SDK meets the current Play target-API requirement (read the level and deadline on the Play target-SDK page; it moves every year)
- [ ] Privacy policy, content rating, and Data safety complete
- [ ] Signing, auth and background behavior tested under modern Android constraints; attestation tested if used
- [ ] Internal/closed/open tracks configured appropriately

## Known Traps

- Assuming one mobile framework decision solves release, entitlement, deep-link, and push behavior without platform-specific proof
- Validating auth, push, or deep links only in local debug builds and treating that as production readiness
- Mixing sandbox, staging, and production mobile backends until install-specific behavior becomes impossible to reproduce
- Using emulator or simulator success as proof for background execution, notification delivery, or device-specific lifecycle
- Choosing a cross-platform stack before listing native integrations, extension points, and store-policy constraints that can force native escape hatches

## Navigation

### References

- [references/ios-best-practices.md](references/ios-best-practices.md) — native iOS owner pointers; load when handing off implementation
- [references/android-best-practices.md](references/android-best-practices.md) — native Android owner pointers; load when handing off implementation
- [references/cross-platform-comparison.md](references/cross-platform-comparison.md) — React Native / Flutter / KMP / native tradeoffs
- [references/deep-linking-guide.md](references/deep-linking-guide.md) — Universal Links, App Links, Expo Router, post-Dynamic-Links
- Mobile testing (layers, device matrix, snapshot/UI/E2E, flakes) is owned by [qa-testing-mobile](../qa-testing-mobile/SKILL.md); start at [test-layers-and-suite-anti-patterns.md](../qa-testing-mobile/references/test-layers-and-suite-anti-patterns.md)
- [references/offline-first-architecture.md](references/offline-first-architecture.md) — local-first storage, sync, conflict resolution
- [references/push-notifications-guide.md](references/push-notifications-guide.md) — APNs, FCM, permissions, channels, analytics
- [references/operational-playbook.md](references/operational-playbook.md) — release operations, decision tables, centralized patterns
- [references/app-store-connect-checklist.md](references/app-store-connect-checklist.md) — App Store Connect field-by-field checklist
- [references/store-update-and-payment-policy.md](references/store-update-and-payment-policy.md) — OTA/code-push policy and external-payment / anti-steering decisions
- [references/platform-traps-and-judgment.md](references/platform-traps-and-judgment.md) — iOS release operations, platform traps, judgment calls, anti-patterns
- [data/sources.json](data/sources.json) — current official and curated external sources

### Shared Checklists And Utilities

- [../software-clean-code-standard/assets/checklists/mobile-release-checklist.md](../software-clean-code-standard/assets/checklists/mobile-release-checklist.md)
- [../software-clean-code-standard/references/auth-utilities.md](../software-clean-code-standard/references/auth-utilities.md)
- [../software-clean-code-standard/references/error-handling.md](../software-clean-code-standard/references/error-handling.md)
- [../software-clean-code-standard/references/resilience-utilities.md](../software-clean-code-standard/references/resilience-utilities.md)
- [../software-clean-code-standard/references/testing-utilities.md](../software-clean-code-standard/references/testing-utilities.md)
- [../software-clean-code-standard/references/clean-code-standard.md](../software-clean-code-standard/references/clean-code-standard.md)

### Templates

- **Cross-platform**: [assets/cross-platform/template-webview.md](assets/cross-platform/template-webview.md) (WebView wrapper, iOS + Android)
- **Native code** lives with the native skills. For iOS, see [networking-and-data-loading.md](../software-ios-native/references/networking-and-data-loading.md) and [swiftui-composition-patterns.md](../software-ios-native/references/swiftui-composition-patterns.md). For Android, see [coroutine-and-compose-recipes.md](../software-android-native/references/coroutine-and-compose-recipes.md). For Keychain and Keystore storage, see [template-mobile-security.md](../software-security-appsec/assets/mobile/template-mobile-security.md).

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

## Release Lookups

Before a release recommendation, read Apple's upload/SDK and third-party SDK requirements, Google's target-API policy, and the installed framework's upgrade notes using [data/sources.json](data/sources.json). An unreachable submission gate is **unverified** and blocks a readiness claim. Source-list edit dates do not establish that every page was checked.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
