# Swift Concurrency crash triage

## Table of Contents

- [How to use this reference](#how-to-use-this-reference)
- [Symptom: `_performBlockAfterCATransactionCommitSynchronizes:` "Call must be made on main thread"](#symptom-performblockaftercatransactioncommitsynchronizes-call-must-be-made-on-main-thread)
- [Symptom: `dataCorrupted` JSON decoding error with `<!DOCTYPE html>` raw response](#symptom-datacorrupted-json-decoding-error-with-doctype-html-raw-response)
- [Symptom: app freezes/black-screens on push tap, recovers on next launch](#symptom-app-freezesblack-screens-on-push-tap-recovers-on-next-launch)
- [Symptom: app freezes/black-screens on push tap AND persists across cold relaunches](#symptom-app-freezesblack-screens-on-push-tap-and-persists-across-cold-relaunches)
- [Symptom: iOS app builds fine in terminal but Xcode shows compile errors, or device runs old binary](#symptom-ios-app-builds-fine-in-terminal-but-xcode-shows-compile-errors-or-device-runs-old-binary)
- [Symptom: explosion of isolation violations after enabling Default Main Actor Isolation](#symptom-explosion-of-isolation-violations-after-enabling-default-main-actor-isolation)
- [Symptom: Core Data `main actor-isolated property` error under strict concurrency](#symptom-core-data-main-actor-isolated-property-error-under-strict-concurrency)
- [Diagnostic tool ladder](#diagnostic-tool-ladder)
- [Meta-lesson: when to switch from code review to external research](#meta-lesson-when-to-switch-from-code-review-to-external-research)

Symptom-first triage runbook for iOS runtime crashes that look like threading bugs, SwiftUI off-main publishes, push-open freezes, stale-binary surprises, or opaque CATransaction assertions. Pair with the detailed fix references in [`software-ios-native/references/swiftui-observation-concurrency.md`](../../software-ios-native/references/swiftui-observation-concurrency.md).

## How to use this reference

Walk the ladder from cheapest to most expensive diagnostic tool until the offender has a name and a line number. Do NOT jump straight to code review for these crashes — private SwiftUI symbols like `_performBlockAfterCATransactionCommitSynchronizes:` are not grep-able in your codebase, so reading source will not find the bug. Find the symptom row below that matches, follow the linked root-cause candidates, and apply the documented fix.

If none of the symptom rows match, use the "Diagnostic tool ladder" at the bottom to produce a symbolicated backtrace, then come back to this page with a real function name.

## Symptom: `_performBlockAfterCATransactionCommitSynchronizes:` "Call must be made on main thread"

Crash text (Xcode console):

```
*** Assertion failure in -[_TtC...SwiftUIApplication _performBlockAfterCATransactionCommitSynchronizes:],
    UIApplication.m:3426
*** Terminating app due to uncaught exception 'NSInternalInconsistencyException',
    reason: 'Call must be made on main thread'
```

This is a SwiftUI internal assertion — private symbol, not grep-able in user code. The thread that crashes is typically a Swift Concurrency Task (e.g. `Task 53`) running on `com.apple.root.user-initiated-qos.cooperative`, not the main thread. The fire is in SwiftUI/UIKit machinery, but the OFFENDER is your code mutating an `@Observable` property or calling UIKit from the wrong actor.

**Web-search this symbol BEFORE any code review.** This exact signature is documented at [twocentstudios.com (2025-08-12)](https://twocentstudios.com/2025/08/12/3-swift-concurrency-challenges-from-the-last-2-weeks/) and several Apple Developer Forums threads. A 2-minute web search saves hours of guess-and-check.

Root-cause candidates, ranked by frequency:

1. **`nonisolated async` `UNUserNotificationCenterDelegate` method with a nested `await MainActor.run { ... }`** — the most common cause in recent Swift Concurrency codebases. The async function's auto-generated continuation epilogue must execute on main, but the nested actor hop violates this. Fix: `@unchecked Sendable` on the AppDelegate class + `@MainActor` on the delegate methods directly; delete the nested `MainActor.run` wraps. See [swiftui-observation-concurrency.md → `nonisolated async` delegate methods + nested `MainActor.run`](../../software-ios-native/references/swiftui-observation-concurrency.md#nonisolated-async-delegate-methods--nested-mainactorrun). **Triggering path to reproduce:** send a push notification to a physical device and tap the banner to open the app. The `userNotificationCenter(_:didReceive:)` delegate call on cold-start is the reliable repro — a plain app launch often hides the bug because no delegate method is invoked.

2. **Bare `Task { ... }` from a `@MainActor` class mutating an `@Observable` property** — in Swift 5.7+ with `StrictConcurrency`, bare `Task` runs on the global executor and does NOT inherit `@MainActor`. Fix: `Task { @MainActor [weak self] in ... }`. Common offenders: cooldown timers, StoreKit `Transaction.updates` listeners, debounced flush schedulers, post-`Task.sleep` state resets. See [swiftui-observation-concurrency.md → Bare `Task { }` isolation](../../software-ios-native/references/swiftui-observation-concurrency.md#bare-task---does-not-inherit-mainactor).

3. **`@MainActor` class awaiting a method on a separate `actor` type** — the `@MainActor → actor → @MainActor` round-trip via `await` can leave the post-await tail on the actor's executor instead of `@MainActor`. Fix: promote the inner `actor` to `@MainActor final class` if all its callers are `@MainActor`. Common offenders in a typical iOS app: `APIClient`, `AppCache`, billing helpers. See [swiftui-observation-concurrency.md → `actor` → `@MainActor final class`](../../software-ios-native/references/swiftui-observation-concurrency.md#actor--mainactor-final-class-refactoring-guidance).

4. **`@Sendable async` closure awaited from `@MainActor`** — Swift's continuation scheduler does NOT reliably hop back to `@MainActor` after a `@Sendable async` closure call. Fix: retype the closure as `@MainActor` instead of `@Sendable`. Common offender: analytics/logging SDKs that take a `RequestExecutor`-shaped closure typealias. See [swiftui-observation-concurrency.md → `@Sendable async` closure isolation footgun](../../software-ios-native/references/swiftui-observation-concurrency.md#sendable-async-closure-isolation-footgun).

5. **`SCNView` in a `UIViewRepresentable` reassigning `view.scene = scene` in `updateUIView`** — every parent re-render rebuilds the scene and schedules a CATransaction commit on SceneKit's render server thread, which then calls back into UIKit off-main. Fix: build the scene once in `makeUIView`, leave `updateUIView` as a no-op, disable `allowsCameraControl`. Or use the Coordinator pattern for incremental scene mutation. See [swiftui-observation-concurrency.md → `SCNView` reassignment anti-pattern](../../software-ios-native/references/swiftui-observation-concurrency.md#scnview-reassignment-in-updateuiview-anti-pattern).

Related Apple Developer Forums threads worth reading: [thread 796407 (Crash in Swift 6 when using UNUserNotificationCenter)](https://developer.apple.com/forums/thread/796407), [thread 762217 (Implement UNUserNotificationCenterDelegate)](https://developer.apple.com/forums/thread/762217), [thread 709563 (MainActor and NSInternalInconsistencyException)](https://developer.apple.com/forums/thread/709563), [thread 735651 (Call must be on main thread)](https://developer.apple.com/forums/thread/735651).

## Symptom: `dataCorrupted` JSON decoding error with `<!DOCTYPE html>` raw response

Console text:

```
dataCorrupted at : The given data was not valid JSON.
raw response: <!DOCTYPE html><html data-dpl-id="dpl_..." lang="en" ...
```

The iOS client expected JSON from an API endpoint, but the server returned Vercel's / Next.js' SPA HTML fallback page instead. This is a routing or config bug, not a threading bug — do NOT conflate it with concurrent push-open crashes even if they appear in the same console session.

Root-cause candidates:

1. **Wrong API URL on the client** — `AppConfig.apiBaseURL` resolves to a path that doesn't match the deployed API route. Most common specific case: missing `/api/` prefix or accidentally double `/api/api/` prefix. Fix: log the URL being requested, curl the same URL from terminal, compare against a known-good endpoint in the same deployment.
2. **Missing or expired auth token** — middleware redirects an unauthenticated request to the login HTML page instead of a 401 JSON response. Fix: log the `Authorization` header being sent, confirm the token is non-empty and unexpired, check that the backend's route definition accepts the header.
3. **Endpoint doesn't exist in the deployed build** — the API route was added in a commit not yet deployed to the hosting environment, or was renamed, or the deploy pipeline is stuck. Fix: check the Vercel/Cloud deployments dashboard for the deployment commit SHA; compare against the commit that defines the endpoint.

The `dataCorrupted` error is swallowed by the typical catch block in an iOS store or API client, so the app may appear to function with partially-loaded state. Fix it even if it doesn't directly crash — the downstream data will be wrong or missing.

## Symptom: app freezes/black-screens on push tap, recovers on next launch

The iPhone shows a notification banner. User taps it. The app launches (or returns from background), shows a blank dark screen (no tab bar, no content), and stays frozen. Force-quit and relaunch recovers — next normal launch is fine.

This is a cold-start route consume race. Both the `launchOptions[.remoteNotification]` path (in `AppDelegate.application(_:didFinishLaunchingWithOptions:)`) and the `userNotificationCenter(_:didReceive:)` path fire on cold-start tap, and they race for the same cache. One path can consume the staged route before the other is ready to process it, leaving the app in an undefined-navigation state.

Fix: add a cold-start auth guard in `handleOpenedPush`. If `session.isAuthenticated` is false (bootstrap hasn't completed yet), do NOT consume the pending route — stage it and return. Let `bootstrapIfNeeded` own the route resume via its own `consumePendingRouteIfNeeded(source: "post_auth_resume")` call. Only one path consumes the route per launch.

## Symptom: app freezes/black-screens on push tap AND persists across cold relaunches

Same symptom as above, but deleting the app or restarting the phone does NOT fix it. Every launch re-crashes or freezes.

This is poisoned UserDefaults state from a prior crashed launch. The previous session wrote a `pendingRoutePath` to cache that the next launch tries to consume, which re-triggers the same crash before the app can recover. The cache key survives across launches because `UserDefaults.standard` is backed by a plist file in the app's sandbox.

Fix (in order of safety):

1. **Delete the app from the device and reinstall** — clears the entire `UserDefaults` plist file along with the sandbox. Confirmed working recovery. Requires re-signing in.
2. **Defensive clear at `AppCache.init`** — wipe `pendingRoutePath` on every cold launch before bootstrap reads it. Only do this if you can tolerate losing a legitimately-pending route from a clean shutdown.
3. **Restart the iPhone** — clears some in-memory UIKit state but does NOT clear UserDefaults. Sometimes recovers transient scene issues. Usually does NOT fix this specific symptom.

Prevention: once the underlying crash is fixed, the poisoned-state scenario can't happen. This is a secondary symptom caused by a primary concurrency bug higher up. Find the primary bug in the previous symptom section.

## Symptom: iOS app builds fine in terminal but Xcode shows compile errors, or device runs old binary

You edited Swift files. `./scripts/build-ios.sh` from terminal says `BUILD SUCCEEDED`. Xcode's build log shows errors in files you know are valid, OR the app on the device does not reflect your latest changes even though Xcode says "Build Succeeded".

This is an incremental build cache stuck on stale state. Xcode sometimes fails to detect actor isolation changes, cross-module type changes, or generated-code regeneration and keeps using cached object files. The app that lands on the device is the last-successfully-built binary, not the source you're looking at.

Fix ladder:

1. **Clean build folder**: Xcode → Product → Clean Build Folder (`⇧⌘K`). Cheapest fix, 30 seconds.
2. **Delete DerivedData for this project**: `rm -rf ~/Library/Developer/Xcode/DerivedData/<project>-*`. Takes a longer rebuild but kills deep caches. 1–2 minutes.
3. **Delete the app from the device**: long-press → Remove App → Delete App. Clears the installed `.app` bundle so the next install is guaranteed fresh.
4. **Quit Xcode entirely** (`⌘Q`, not just the project window) — Xcode process holds some indices in memory that survive project close.
5. **Reopen the project, wait for indexing to complete**, then `⌘R`.

Verify the fresh binary is actually on the device with the **DEBUG marker print pattern**: add a temporary `print("[<class>] build marker — fix-revision-<YYYY-MM-DD>")` to a class `init` or `bootstrap` method that runs at launch. If you don't see the marker in the Xcode console on next run, the binary on the device is still stale. Remove the print after confirming.

## Symptom: explosion of isolation violations after enabling Default Main Actor Isolation

You flipped `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` (or opened a new Xcode project that has it on by default) and rebuilt. Every previously-tolerated cross-actor hop now surfaces as a compile error. Builds that passed an hour ago now produce hundreds of diagnostics concentrated in networking, caching, analytics, and background-task layers.

This is a documented Xcode behavior change, not a regression. The flag converts what used to be runtime races into compile errors — exactly what you want, but the shock is real. Reference: [Swift Forums 81696](https://forums.swift.org/t/explosion-of-isolation-violations-in-xcode-26-beta-6/81696).

Fix ladder (in order):

1. **Do not bulk-silence with `@preconcurrency`**. That re-introduces the `_performBlockAfterCATransactionCommitSynchronizes:` crash class — you traded a compile error for a runtime crash.
2. **Triage errors by module, starting with leaf types** (types that call out but are not called into). Fix them first; their fixes often cascade up the stack.
3. **Mark genuine non-UI work `nonisolated` or `@concurrent`**. Image decoding, JSON parsing, file I/O, network transport, cache serialization, and analytics batching all belong off the main actor. Tag them explicitly.
4. **Remove defensive `await MainActor.run { … }` wraps** scattered through the codebase. Under default main-actor isolation they are redundant at best and crash-inducing at worst (they re-introduce the nested-hop footgun).
5. **Promote `actor` types called only from `@MainActor` to `@MainActor final class`**. Common candidates: `APIClient`, auth services, billing helpers, caches, preference stores. If no real cross-actor coordination is happening, the `actor` is pure overhead.
6. **Land the migration in a single PR per module**, not one giant diff. Each module's tests should pass with the flag both on and off during the transition.

## Symptom: Core Data `main actor-isolated property` error under strict concurrency

Swift 6 strict concurrency surfaces `main actor-isolated property '<name>' can not be referenced from a non-isolated context` errors on `NSManagedObject` subclass properties. This is [Apple Developer Forums 803827](https://developer.apple.com/forums/thread/803827).

Root cause: a `NSManagedObject` instance fetched from a `@MainActor`-isolated view context is being passed to a background context, a `nonisolated` function, or a `@concurrent` Task. Core Data managed objects are bound to the thread of their owning `NSManagedObjectContext` — passing them across isolation domains is unsafe, and Swift 6 now enforces it at compile time.

Fix:

- **Pass `NSManagedObjectID`, never the managed object itself**, across isolation boundaries. Re-fetch on the destination actor using `context.existingObject(with: id)` or `context.object(with: id)`.
- **Keep each `NSManagedObjectContext` on one isolation domain**: the view context is `@MainActor`; background contexts should be inside a dedicated `actor` or a `@concurrent` worker type.
- **Do not mark `NSManagedObject` subclasses `@unchecked Sendable`** to paper over the error. That re-introduces the exact race the compiler caught.
- **For batch writes**, use `context.perform { }` / `context.performAndWait { }` on the background context and only pass `NSManagedObjectID`s in and out.

## Diagnostic tool ladder

When the symptom does not match a row above, walk this ladder in order. Each step is cheaper to run than the next; do not skip ahead.

### 1. Console output

Run from Xcode, reproduce the crash, read the entire console buffer from app launch to terminate. Look for:

- `WARNING: ThreadSanitizer: data race` (TSan was already on)
- `Main Thread Checker: UI API called on a background thread:` (MTC was already on)
- `Publishing changes from background threads is not allowed` (Combine's off-main warning, can also fire for `@Observable`)
- Any line with `libc++abi: terminating` — the preceding lines are the uncaught exception's description
- System logs like `Home affordance gate timed out` — signals the main thread was blocked for too long

Cost: free, always on. Information density: high for known error patterns, low for novel ones.

**Allocations instrument note:** the Allocations instrument sometimes fails to report reference counting operations for native Swift types. Prefer Leaks + `vmmap` / `heap` command-line snapshots over Allocations when chasing a retain-cycle suspicion. Treat Allocations charts as directional, not authoritative.

### 2. Main Thread Checker (pause on issue)

Enable in `project.yml` so it's permanent:

```yaml
schemes:
  <SchemeName>:
    run:
      enableMainThreadChecker: true
      stopOnEveryMainThreadCheckerIssue: true
```

Run `./scripts/generate-xcodeproj.sh` to propagate. On the next run, any UIKit/AppKit API called from a non-main thread pauses the debugger at the exact call site, with a symbolicated stack trace in the Debug Navigator.

Catches: UIKit/AppKit method calls from background threads.
Misses: SwiftUI internal commits triggered by off-main `@Observable` mutations (the crash WE debugged). MTC is a UIKit-level tool, not a SwiftUI state-level tool.

Cost: free in Debug builds. No runtime overhead. Leave it on permanently.

### 3. Thread Sanitizer

Enable on-demand in `project.yml`:

```yaml
schemes:
  <SchemeName>:
    run:
      enableThreadSanitizer: true
      stopOnEveryThreadSanitizerIssue: true
```

Run `./scripts/generate-xcodeproj.sh`. Next run catches any data race on shared storage — including `@Observable` property writes from the wrong thread. TSan reports look like:

```
WARNING: ThreadSanitizer: data race (pid=...)
  Write of size 8 at 0x... by thread T2:
    #0 0x... in <function name> <file>:<line>
    #1 ...

  Previous read of size 8 at 0x... by main thread:
    #0 0x... in <function name> <file>:<line>
    #1 ...

  Location is heap block of size ... at ... allocated by main thread:
    ...
```

The "Write by thread T2" stack is the offender. Paste it, grep for the function name, fix.

Cost: 5–15× runtime slowdown, 5–10× memory overhead. Only enable when actively chasing a threading bug. Disable immediately after.

### 4. lldb `bt` and `image lookup`

When the debugger pauses at a crash (either via MTC pause-on-issue, TSan breakpoint, or an uncaught exception breakpoint):

```
(lldb) bt
```

Prints the full symbolicated backtrace for the current thread. The top user-code frame is where the offending work happens. If the title bar of the debug window says `Task 53` or similar, the crash thread is a Swift Concurrency Task running on the global cooperative queue — not main.

For individual addresses from an unsymbolicated crash log:

```
(lldb) image lookup --address 0x1071b5244
```

Returns `Summary: <binary>`<function name>` at <file>:<line>`. Useful for matching up raw backtrace addresses to source lines when you have the paused process.

Set an **Objective-C Exception Breakpoint** in Xcode's Breakpoint Navigator (⌘8 → + → Exception Breakpoint → set Exception to Objective-C) so `NSInternalInconsistencyException` and friends pause at the call site instead of unwinding.

Cost: free. Requires a paused process (the debugger must be attached when the crash happens).

### 5. Web search the exact symbol

Before spending another hour on code review, **search for the exact crash signature including private SwiftUI symbols**. Examples that point at documented articles:

- `_performBlockAfterCATransactionCommitSynchronizes "Call must be made on main thread"`
- `UNUserNotificationCenter nonisolated async crash main thread Swift 6`
- `SwiftUI @Observable background thread data race`

The private SwiftUI symbol makes the query highly specific — there's usually exactly ONE blog post, Apple Forums thread, or GitHub issue that matches. A 2-minute search has closed cases that code review couldn't.

Cost: zero. Often faster than MTC/TSan combined.

### 6. Git bisect (last resort)

If the symptom started after a specific commit and you can't find the offender any other way:

```bash
git bisect start
git bisect bad HEAD
git bisect good <last-known-good-SHA>
# Xcode reinstall + test at each step
git bisect run ./scripts/test-ios.sh smoke
```

Cost: hours of rebuilds and tests, but guaranteed to narrow down to a single commit. Reserve for cases where nothing else is working.

## Meta-lesson: when to switch from code review to external research

If you have fixed 3+ "obviously correct" threading bugs in a row and the crash signature has not changed, **stop code-reviewing and web-search**. Each additional fix is almost certainly a real independent bug that was hiding behind the same symptom class, but it is not THE bug. The actual root cause is in a place that code review is blind to — usually a framework interaction (UNUserNotificationCenter, SceneKit, StoreKit), a private SwiftUI machinery, or a Swift Concurrency edge case that is documented but not obvious.

Symptoms that should trigger the web-search escape valve immediately:

- Crash fires inside a private system symbol (underscore-prefixed Apple frameworks)
- Crash fires on a Swift Concurrency Task on a cooperative queue, not main thread
- Crash reproduces on a single line in a short function that compiles cleanly and looks correct
- The same assertion message recurs across multiple "obviously correct" fixes
- You're adding defensive `await MainActor.run { ... }` wraps because "it can't hurt" — that's the pattern that caused THIS bug. More wraps in the wrong places make it worse.

Search query template: `<private symbol> "<exact assertion message>" <platform>`. Example: `_performBlockAfterCATransactionCommitSynchronizes "Call must be made on main thread" SwiftUI`.
