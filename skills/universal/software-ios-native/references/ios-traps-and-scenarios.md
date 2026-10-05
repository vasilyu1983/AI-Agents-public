# iOS Native: Known Traps and Scenarios

Full trap table and scenario recipes. Reference from SKILL.md.

---

## Table of Contents

- [Known iOS Traps](#known-ios-traps)
- [Scenarios](#scenarios)

## Known iOS Traps

Use these diagnostic leads when inheriting an iOS codebase or migrating concurrency settings. Confirm the affected toolchain and reproduction before applying a workaround.

| Trap | Symptom | Fix |
|---|---|---|
| `_performBlockAfterCATransactionCommitSynchronizes:` "Call must be made on main thread" | UIKit main-thread assertion | Capture the backtrace; the symbol alone does not identify the offending call or concurrency pattern. |
| UN delegate accessing UI-owned state | Isolation diagnostic or notification-tap failure | Match the imported SDK requirement, transfer Sendable routing values, and hop UI updates to `@MainActor`. |
| `Task { }` formed in a nonisolated callback mutating `@Observable` | Same crash class; creation context has no main-actor isolation | `Task { @MainActor [weak self] in … }`; do not misdiagnose tasks formed inside main-actor-isolated methods, which inherit that actor |
| `@MainActor → actor → @MainActor` round-trip via `await` | Caller resumes on its actor; state can change during suspension | Re-check request identity/state after `await`; choose isolation by state ownership and work. |
| `@Sendable async` closure touching UI state | Sendability alone does not provide main-actor isolation | Isolate its body when required; the awaiting caller retains its own isolation. |
| `SCNView` updates | Rebuilding scenes can reset interaction state or perform unnecessary work | Create initial objects once; apply changed inputs incrementally in `updateUIView`. |
| Notification callback hits an isolation assertion | Callback executor disagrees with assumed isolation | Inspect SDK signatures and backtrace; a targeted `@preconcurrency` annotation does not change the callback executor. |
| iOS 26 `withAnimation` regression inside `@MainActor` methods | Animations fail to start or skip starting state | Hoist `withAnimation` out of the `@MainActor` body, or wrap in inner `Task { @MainActor in … }` |
| Xcode 26 `SubscriptionStatus.all` stale after subscription change | StoreKit 2 paywall shows wrong tier post-upgrade | Query `Product.SubscriptionInfo.Status` directly or read `currentEntitlements` after a `Transaction.updates` tick |
| Xcode 26 Allocations instrument misreports Swift ref counting | Retain-cycle hunts produce misleading charts | Use Leaks + `vmmap` / `heap` command-line snapshots; treat Allocations as directional |
| Xcode 26 default TLS Client Hello changed | Login / API regressions on strict-fingerprint backends | Verify against a staging tier that mirrors prod edge config |
| Default Main Actor Isolation migration (Xcode 26 Beta 6+) | Explosion of compile-time isolation violations on flag flip | Migrate in layered passes; do NOT bulk-silence with `@preconcurrency` |
| Core Data `main actor-isolated property` error under strict concurrency | Fetched objects cross isolation domains | Pass `NSManagedObjectID`, re-fetch on destination actor |
| Cold-start push-tap black screen / freeze | `launchOptions[.remoteNotification]` races `didReceive` for route cache | Cold-start auth guard in `handleOpenedPush`; let `bootstrapIfNeeded` own the resume |
| Poisoned UserDefaults from prior crashed launch | Crash persists across relaunches | Delete + reinstall; or defensive `pendingRoutePath` wipe in `AppCache.init` |
| `dataCorrupted` + `<!DOCTYPE html>` raw response | Client expected JSON, got web shell | API routing / auth bug — log URL, curl it, compare to known-good |
| Xcode incremental build reuses stale object files on actor isolation changes | Device runs old binary after edit; "Build Succeeded" lies | Clean Build Folder → delete DerivedData → delete app from device → DEBUG build marker print |
| `@State` initialized from parent parameter keeps original value forever | Child ignores parent's new value on re-render | Use `.onChange(of:)` to sync, or use `@Binding` / plain `let` instead of `@State` init |
| `async let` never awaited blocks at scope exit | Early return silently waits for implicit cancellation | Always `await` explicitly; be aware early returns block until cancellation cleanup |
| `sheet(item:)` closure captures stale state | Sheet sees original item, not updated model | Pass `Binding` or use `@Environment` for live data inside sheets |
| `beginBackgroundTask` has ~30-second hard limit | Background work killed without warning on modern iOS | Use `BGProcessingTask` for long work; design for interruption; save progress incrementally |
| Universal Link arrival races scene setup on cold start | Deep link lost or crashes if scene not ready | Same pattern as push cold-start: stage route, let bootstrap own the resume |
| `didReceiveMemoryWarning` is last chance before jetsam kill | App killed without warning if memory not released | Purge image caches, web view caches, and large data structures in the handler |
| APNs payload size limit is 4 KB | Notifications with large `userInfo` silently dropped by APNs | Keep payloads minimal; fetch large data on open, not in the notification |
| Keychain items persist across app reinstall | Stale auth tokens from prior install cause login confusion | Check and clear on fresh install (detect via `UserDefaults` flag that resets on reinstall) |
| God objects (500+ line ViewModels) | Untestable, hard to reason about, single point of failure | Split by responsibility; compose smaller `@Observable` types; inject dependencies |
| Hardcoded `DateFormatter` with fixed `en_US_POSIX` locale on user-visible surfaces | Non-English users see English time formats regardless of locale picker | Use `DateFormatter.dateFormat(fromTemplate: "jm", locale: l10n.currentLocale)`. Reserve `en_US_POSIX` for parsing API strings only |
| Backend returns raw English prose on a localized screen | First user of a locale gets English; cache fills English; others see it too | Inspect the backend contract: generated prose needs a translation layer; structured data localizes on iOS via enum helpers |
| l10n cache drift after locale switch mid-session | User changes locale picker, next API call still uses old locale | `LocalizationStore.propagateLocaleToAPIClient()` on every `currentLocaleIdentifier` change; `APIClient.currentLocale` read at request-build time |
| In-memory store snapshots survive locale change | Language change has no visible effect until pull-to-refresh | Reset every backend-prose-caching store + `URLCache.shared.removeAllCachedResponses()` on locale change; do NOT rely on fire-and-forget `Task { await store.refresh() }` without first resetting the snapshot |
| Stored profile locale wins over explicit `?locale=` query param | iOS user with `profile.locale = "en"` but active picker `"ru"` still sees English | Server priority must be `?locale=` > `Accept-Language` > stored profile |

**Operating rules:**
- After APNs accepts the payload and the banner appears, any post-tap crash belongs to the app-side open path, not transport.
- `_performBlockAfterCATransactionCommitSynchronizes:` is a private SwiftUI symbol — web-search the exact signature before any code review.
- `dataCorrupted` + `<!DOCTYPE html>` is an API routing / auth bug — do not conflate with push-open crashes.
- Never bulk-silence Swift 6 isolation errors with `@preconcurrency` — it re-introduces the crash class.

Route detailed diagnosis and fix recipes to [`software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md`](../../software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md).

---

## Scenarios

Recipes keyed to common iOS implementation moments.

### S1 — StoreKit 2 entitlement reconciliation with SubscriptionStatus.all

1. Open an async `Transaction.updates` listener on app launch; do not rely on a one-shot product fetch.
2. Call `Product.SubscriptionInfo.Status.statuses(for: groupID)` directly after any transaction event.
3. Do not trust `SubscriptionStatus.all` as a live signal; it caches and goes stale after upgrade/downgrade (Xcode 26 trap).
4. For each status, call `transaction.finish()` only after your backend has confirmed entitlement sync.
5. Update your `@Observable` entitlement store on the main actor; gate all paywall UI from the store.
6. Test upgrade, downgrade, restore, and cancellation paths in StoreKit sandbox before TestFlight.

### S2 — APNs sandbox vs production proof

1. Confirm `aps-environment` in the final exported `.app` and its selected provisioning profile: `codesign -d --entitlements - App.app | grep aps-environment`.
2. Development builds signed by Xcode on-device use `sandbox`; TestFlight and App Store require `production`.
3. Store per-device `push_environment` in your backend device table; never rely on a global env var.
4. After installing a TestFlight build, verify the newest backend device row shows `push_environment = production`.
5. Send a deterministic server-side push to that device row and confirm receipt before debugging cron or polling paths.
6. Do not treat local sandbox success as proof the production path works; verify both paths explicitly.

### S3 — Swift 6.2 concurrency migration of a legacy actor

1. Inspect `SWIFT_VERSION`, default actor isolation, and `NonisolatedNonsendingByDefault` separately before changing the app target.
2. Triage leaf types first. Keep UI-owned state on `@MainActor`; retain separate actors where shared state or non-UI work needs them.
3. A main-actor caller resumes on that actor after `await`; re-check state after suspension rather than replacing actors to repair an imagined executor loss.
4. For CPU work that must leave the actor, use `@concurrent` on supported toolchains; `nonisolated async` can inherit caller isolation under SE-0461.
5. Scope compatibility annotations to a proven SDK boundary; they do not change runtime callback execution.
6. Run Thread Sanitizer in a supported Simulator configuration, then verify affected device flows separately. Apple does not support Thread Sanitizer on physical iOS devices. A clean run covers exercised paths only. See [Apple sanitizer guidance](https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early).

### S4 — withAnimation Xcode 26 regression workaround

1. Identify animations that fail to start or skip starting state inside `@MainActor` methods on iOS 26.
2. Hoist the `withAnimation` call outside the `@MainActor` body, or wrap in `Task { @MainActor in withAnimation(…) { … } }`.
3. Verify on iOS 26.0, 26.2, and 26.4 separately; behavior differs across point releases.
4. Add a UI snapshot test for the affected transition to catch regression on future OS updates.
5. File a Feedback Assistant report with a minimal reproducer; track the open radar in your release notes.

### S5 — Privacy manifest required-reasons audit pre-submission

1. Get the current required-reason API category list and symbol names from https://developer.apple.com/documentation/bundleresources/describing-use-of-required-reason-api (the five categories cover file timestamps, disk space, system boot time, active keyboards, and user defaults) — do not rely on a hardcoded symbol list without checking it against that page first.
2. Run `rg 'UserDefaults|NSFileManager|systemUptime|volumeAvailableCapacity|activeInputModes|creationDate|modificationDate|mach_absolute_time' --type swift` across the codebase. Note the unescaped `|` inside single quotes: an escaped `\|` inside a ripgrep regex is a literal pipe character and will silently match nothing — verify the command actually flags a known-positive file before trusting a clean run.
3. For each required-reason API usage, add the corresponding `NSPrivacyAccessedAPITypes` entry to `PrivacyInfo.xcprivacy`.
4. Audit third-party SDKs; each must ship its own privacy manifest or you must declare their reasons.
5. Build an `.xcarchive` and validate with Xcode Organizer; it lists missing privacy declarations before upload.
6. Treat this as a release gate, not a last-minute check; missing declarations cause App Review rejection.
