# Swift Concurrency crash triage

## Table of Contents

- [How to use this reference](#how-to-use-this-reference)
- [Symptom: `_performBlockAfterCATransactionCommitSynchronizes:` "Call must be made on main thread"](#symptom-_performblockaftercatransactioncommitsynchronizes-call-must-be-made-on-main-thread)
- [Symptom: `dataCorrupted` JSON decoding error with `<!DOCTYPE html>` raw response](#symptom-datacorrupted-json-decoding-error-with--raw-response)
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

Treat the assertion as evidence of a thread requirement violation, not a unique root cause. Pause at the exception and inspect the first app/SDK frame and the actor isolation of the callback or closure that reaches UI state.

- A `Task { ... }` inherits its creation context; a nonisolated callback does not automatically make its task main-actor-isolated. For UI work, explicitly isolate the boundary to `@MainActor` and verify the protocol requirements against the installed SDK.
- A main-actor caller resumes on that actor after `await`. Inspect the isolation of the awaited function or closure itself; do not assume it remains on a different executor afterward.
- Notification delegate isolation can interact with imported protocol requirements. [Apple Forums thread 796407](https://developer.apple.com/forums/thread/796407) is a reported reproduction, not proof that every nested `MainActor.run` causes this assertion. Match the SDK, signature, and stopped stack before applying an isolated conformance or completion-handler variant.
- If the top app frame reaches SceneKit/UIKit through a representable, inspect scene lifetime and callback thread requirements before changing `updateUIView`.

Implementation patterns belong to [software-ios-native's concurrency reference](../../software-ios-native/references/swiftui-observation-concurrency.md).

Related Apple Developer Forums threads worth reading: [thread 796407 (Crash in Swift 6 when using UNUserNotificationCenter)](https://developer.apple.com/forums/thread/796407), [thread 762217 (Implement UNUserNotificationCenterDelegate)](https://developer.apple.com/forums/thread/762217), [thread 709563 (MainActor and NSInternalInconsistencyException)](https://developer.apple.com/forums/thread/709563), [thread 735651 (Call must be on main thread)](https://developer.apple.com/forums/thread/735651).

## Symptom: `dataCorrupted` JSON decoding error with `<!DOCTYPE html>` raw response

Record the requested URL, status, content type, redirect chain, and a redacted response prefix: HTML where JSON is expected suggests a route, auth, or deployment mismatch.
Route server-side diagnosis to [software-backend](../../software-backend/SKILL.md) and response contracts to [dev-api-design](../../dev-api-design/SKILL.md); decoding failure does not establish a concurrency bug.

## Symptom: app freezes/black-screens on push tap, recovers on next launch

The iPhone shows a notification banner. User taps it. The app launches (or returns from background), shows a blank dark screen (no tab bar, no content), and stays frozen. Force-quit and relaunch recovers — next normal launch is fine.

A possible cause is a race between notification delivery, auth bootstrap, and route presentation. Trace each callback and route-consumption attempt; compare a cold push tap with a normal launch. Stage the route until the required auth/navigation state is ready, and give one component ownership of consuming it. App-specific cache keys and function names are not a platform contract.

## Symptom: app freezes/black-screens on push tap AND persists across cold relaunches

Repeated launches may replay persisted route state from a prior failed launch. Rebooting does not normally clear `UserDefaults`; deleting and reinstalling the app removes its local data container and may change the reproduction. Neither outcome proves the underlying concurrency cause.

1. Capture logs and the redacted pending-route state before any reset.
2. Use a scoped diagnostic launch option to bypass or clear only the suspect route, then compare behavior with the original state.
3. If replacement and scoped reset fail, preserve needed local data before uninstall/reinstall. Record whether that reset changes the symptom; do not describe it as a code fix.
4. Fix route validation/consumption in software-ios-native and repeat the original push-open path. Clearing every pending route on launch can lose legitimate navigation and conceal the defect.

## Symptom: iOS app builds fine in terminal but Xcode shows compile errors, or device runs old binary

You edited Swift files. `./scripts/build-ios.sh` from terminal says `BUILD SUCCEEDED`. Xcode's build log shows errors in files you know are valid, OR the app on the device does not reflect your latest changes even though Xcode says "Build Succeeded".

Treat build-cache drift as a hypothesis. Compare the Xcode and terminal project, scheme, configuration, developer directory, build settings, destination, and build exit status first. A failed build may leave an older `.app` behind.

1. Preserve launch/state evidence and inspect the artifact path and executable UUID.
2. Try a fresh build in an isolated project-specific DerivedData directory, then replace/install that exact artifact while retaining its data container.
3. Escalate to Xcode Clean Build Folder or a verified project-only cache reset if the comparison implicates incremental state.
4. Uninstall only if artifact replacement fails or persisted state is itself under investigation.

Use a temporary debug log with a unique build marker in a known launch path. An absent marker is meaningful only if that path executed and its output was captured. Remove it after verifying the installed binary.

## Symptom: explosion of isolation violations after enabling Default Main Actor Isolation

You flipped `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` (or opened a new Xcode project that has it on by default) and rebuilt. Every previously-tolerated cross-actor hop now surfaces as a compile error. Builds that passed an hour ago now produce hundreds of diagnostics concentrated in networking, caching, analytics, and background-task layers.

This is a documented Xcode behavior change, not a regression. The flag converts what used to be runtime races into compile errors — exactly what you want, but the shock is real. Reference: [Swift Forums 81696](https://forums.swift.org/t/explosion-of-isolation-violations-in-xcode-26-beta-6/81696).

Fix ladder (in order):

1. **Do not bulk-silence with `@preconcurrency`**. It suppresses checking without establishing a safe isolation boundary.
2. **Triage errors by module, starting with leaf types** (types that call out but are not called into). Fix them first; their fixes often cascade up the stack.
3. **Mark genuine non-UI work `nonisolated` or `@concurrent`**. Image decoding, JSON parsing, file I/O, network transport, cache serialization, and analytics batching all belong off the main actor. Tag them explicitly.
4. **Remove defensive `await MainActor.run { … }` wraps** scattered through the codebase. Remove one only when the surrounding code is already main-actor-isolated; an explicit hop from a nonisolated callback may be necessary.
5. **Promote `actor` types called only from `@MainActor` to `@MainActor final class`**. Common candidates: `APIClient`, auth services, billing helpers, caches, preference stores. This is an architecture choice, not a substitute for locating the failing access.
6. **Land the migration in a single PR per module**, not one giant diff. Each module's tests should pass with the flag both on and off during the transition.

## Symptom: Core Data `main actor-isolated property` error under strict concurrency

Swift 6 strict concurrency surfaces `main actor-isolated property '<name>' can not be referenced from a non-isolated context` errors on `NSManagedObject` subclass properties. This is [Apple Developer Forums 803827](https://developer.apple.com/forums/thread/803827).

Root cause: a `NSManagedObject` instance fetched from a `@MainActor`-isolated view context is being passed to a background context, a `nonisolated` function, or a `@concurrent` Task. Core Data managed objects are confined to their owning context's queue — passing them across isolation domains is unsafe, and Swift 6 now enforces it at compile time.

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
      # disableMainThreadChecker defaults to false, i.e. MTC is on by default; leave it unset or explicit false
      disableMainThreadChecker: false
      stopOnEveryMainThreadCheckerIssue: true
```

Regenerate the project using its documented command. XcodeGen's reviewed [ProjectSpec](https://github.com/yonaskolb/XcodeGen/blob/master/Docs/ProjectSpec.md) documents `disableMainThreadChecker` and `stopOnEveryMainThreadCheckerIssue`; use supported keys and inspect the generated scheme rather than assume an arbitrary `enableMainThreadChecker` key took effect. When a monitored system API is called off-main, pause on the reported issue and inspect the app frame.


Catches: UIKit/AppKit method calls from background threads.
Coverage limit: MTC checks selected system APIs with known thread requirements; a clean run does not establish that SwiftUI state mutations are race-free.

Apple describes the overhead as minimal, not zero. Keep it enabled for correctness diagnosis; compare performance with an uninstrumented Profile build. [Apple sanitizer guide](https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early).

### 3. Thread Sanitizer

Enable on demand and verify the effective scheme:

Use only keys supported by the installed XcodeGen version's [ProjectSpec](https://github.com/yonaskolb/XcodeGen/blob/master/Docs/ProjectSpec.md), and inspect the generated scheme to confirm the setting took effect. The reviewed ProjectSpec does not document a TSan key; avoid assuming an unrecognized key enables instrumentation. For a direct invocation:

```sh
xcodebuild test -scheme <SchemeName> -enableThreadSanitizer YES
```

or toggle it in the scheme's Run/Test action > Diagnostics tab in Xcode. TSan can find exercised data races on shared storage; a clean run does not rule out an unexercised race or a UI thread-requirement violation. TSan reports look like:

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

Use TSan on a supported Simulator destination for iOS; Apple does not support it on physical iOS devices. Its instrumentation changes timing and memory use, so disable it for performance measurement. See the Apple sanitizer guide above.

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

Run bisect only in an isolated checkout with a reproducible pass/fail probe; it mutates Git state and belongs outside a shared working tree. An intermittent or environment-dependent probe can misidentify the commit.

## Meta-lesson: when to switch from code review to external research

If you have fixed 3+ "obviously correct" threading bugs in a row and the crash signature has not changed, **stop code-reviewing and web-search**. An unchanged signature means the current hypothesis remains unproven. The actual root cause is in a place that code review is blind to — usually a framework interaction (UNUserNotificationCenter, SceneKit, StoreKit), a private SwiftUI machinery, or a Swift Concurrency edge case that is documented but not obvious.

Symptoms that should trigger the web-search escape valve immediately:

- Crash fires inside a private system symbol (underscore-prefixed Apple frameworks)
- Crash fires on a Swift Concurrency Task on a cooperative queue, not main thread
- Crash reproduces on a single line in a short function that compiles cleanly and looks correct
- The same assertion message recurs across multiple "obviously correct" fixes
- You're adding defensive `await MainActor.run { ... }` wraps because "it can't hurt" — inspect the required actor boundary before adding or removing a hop.

Search query template: `<private symbol> "<exact assertion message>" <platform>`. Example: `_performBlockAfterCATransactionCommitSynchronizes "Call must be made on main thread" SwiftUI`.
