# Mobile Platform Traps, Judgment Calls, and Anti-Patterns

Detail moved out of [SKILL.md](../SKILL.md) to keep the skill body under its line budget. Store dates, SDK minimums, and policy wording change; re-check the primary pages named in SKILL.md before quoting anything here as current.

## Contents

- [iOS Release Operations](#ios-release-operations)
- [Known Platform Traps](#known-platform-traps)
- [Expert Judgment Calls](#expert-judgment-calls)
- [Common Anti-Patterns](#common-anti-patterns)

## iOS Release Operations

| Gate | Rule |
|------|------|
| TestFlight channels | internal → external (Beta App Review) → public link |
| Upload path | App Store Connect Organizer → `App Store Connect`. `Release Testing` is not the submission route. |
| Backend/content vs binary | Backend fixes that don't change the binary, native UI, capabilities, or App Review-visible behavior do not require a new iOS release. |
| Smoke proof | Real-iPhone TestFlight smoke: production APNs delivery + product loading + purchase + restore + relaunch. |
| Minimum SDK for upload | Apple periodically raises the minimum Xcode/SDK version accepted at App Store Connect — check [developer.apple.com/news/upcoming-requirements](https://developer.apple.com/news/upcoming-requirements/) before any archive/upload, since a passing local build can still be rejected at ingestion. |

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
- When `adb logcat` shows the crash includes `SnapshotStateObserver`, `MonotonicFrameClock`, or `Recomposer`, route to [software-android-native](../../software-android-native/SKILL.md) and [software-android-runtime-debugging](../../software-android-runtime-debugging/SKILL.md).

## Expert Judgment Calls

Non-experts see a working build and call it done. An expert checks the cases where "it built and ran once" is not the same as "it will pass review, survive an audit, or work for the next user."

- **Cross-platform regret is asymmetric.** Moving from native to shared code is a full rewrite; moving from shared code to native is usually a partial, surgical one (pull out the hot path, keep the rest). When timeline pressure forces a shared-framework choice, explicitly list which native integrations (camera pipelines, ARKit/ARCore, background audio, CarPlay/Android Auto, widgets, App Intents/App Actions) are foreseeable within 12 months — those are the ones that force a native escape hatch later, and the earlier you know, the cheaper the hedge (e.g., isolate the module behind a platform-abstraction boundary from day one).
- **One native escape hatch usually means you need native hiring anyway.** Teams under-price this: a single deep native module (e.g., a custom camera pipeline or a hardware SDK) requires the same iOS/Android specialist skill as a fully native app, just applied to a smaller surface. Budget the hire, not just the sprint.
- **App Review rejection risk hides in account and auth flows, not UI polish.** The most common late-stage iOS rejections a non-expert misses: (1) Guideline 5.1.1(v) — in-app account deletion that actually deletes the record and revokes tokens, not just deactivates; (2) Sign in with Apple parity — if the app offers any third-party or social login, Sign in with Apple must be offered too, at equal prominence; (3) subscription flows that don't expose "Cancel Subscription" reachably inside the app or account settings. Verify all three before submission, every release — Apple periodically increases enforcement on these without a version bump to announce it.
- **Push permission priming is a judgment call, not a technical one.** Requesting notification permission on first launch reliably produces "Don't Allow" from most users, who then never see the system prompt again. An expert defers the OS prompt until the user has taken an action that makes the value of push obvious (e.g., after placing an order), and separately audits whether the soft-ask copy itself needs its own re-prompt path if declined.
- **Offline-first correctness is a conflict-resolution decision, not a caching decision.** Before implementing local-first storage, force an explicit answer to "what happens when two devices edit the same record while offline" — last-write-wins, field-level merge, or user-facing conflict UI. Silence on this question means the team will discover the answer in production, from a support ticket.
- **A shared entitlement registry is cheaper before launch than after.** Apps that sell both in-store (StoreKit/Play Billing) and web/Stripe entitlements without one canonical source of truth accumulate silent state drift (a user paid on web, app still shows locked) that is expensive to retrofit once both paths have real users.
- **Framework benchmark claims decay faster than they're written.** A blog post claiming "Flutter is now as fast as native" or "RN startup time improved 40%" is a snapshot of one app, one release, one device. Treat every unsourced performance claim as a hypothesis to verify with Instruments/Macrobenchmark on the actual product, not a fact to design around.

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
