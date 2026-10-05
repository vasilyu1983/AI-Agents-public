# SwiftUI, Observation, and Concurrency

This reference mixes platform-backed defaults with explicit repo defaults chosen to reduce ambiguity for agents.

## Table of Contents

- [Verified platform defaults](#verified-platform-defaults)
- [Repo defaults for new iOS 17+ work](#repo-defaults-for-new-ios-17-work)
- [Safe defaults](#safe-defaults) — state, concurrency, UI boundaries, Canvas/GPU, visualization state ownership, SF Symbols, dual-view patterns, score scale, iOS 17+ features
- [Testing defaults](#testing-defaults)
- [Avoid](#avoid)
- [Backend Integration: Polymorphic and Tier-Gated DTOs](#backend-integration-polymorphic-and-tier-gated-dtos) — GatedOr, AnyCodableValue, lenient decoders, response wrappers
- [@ViewBuilder Pitfall: guard/return](#viewbuilder-pitfall-guardreturn)
- [@ViewBuilder Pitfall: Type Checker Crashes](#viewbuilder-pitfall-type-checker-crashes)
- [Type Naming Conflicts](#type-naming-conflicts)

## Verified platform defaults

- SwiftUI is the primary Apple declarative UI framework for iOS.
- Observation is the current modern observation model for Apple-platform state tracking.
- Swift Concurrency is the current async model for structured async work.
- Swift Testing is the modern Apple test framework for unit and integration tests.

## Repo defaults for new iOS 17+ work

- Prefer SwiftUI for new screens.
- Prefer `@Observable` for new UI-facing state.
- Keep UI-facing models on `@MainActor`.
- Prefer `@State` for local view state and view-owned models.
- Prefer explicit dependency flow over hidden global state.

## Safe defaults

### State

- local transient view state -> `@State`
- view-owned model -> `@State` with an `@Observable` type
- shared dependency or environment value -> `@Environment`

Avoid introducing `ObservableObject` or `@EnvironmentObject` in new iOS 17+ code unless the app still supports older baselines or already standardizes on them.

### Data Flow Anti-Patterns

- Never use `@AppStorage` inside an `@Observable` class — `AppStorage` does not trigger Observable updates and produces stale reads. Use `@AppStorage` in views or pass the value into the Observable class.
- Avoid `Binding(get:set:)` in `body` — it creates a new binding on every evaluation. Use `onChange(of:)` or restructure state ownership.
- Prefer `Identifiable` conformance on model types over `id: \.someProperty` in `ForEach` — provides stable identity across evaluations.
- `@State` should always be `private` — non-private `@State` is almost always a state-ownership mistake.
- Complete avoid-list for new iOS 17+ code: `ObservableObject`, `@Published`, `@StateObject`, `@ObservedObject`, `@EnvironmentObject`. Replace with: `@Observable`, direct properties, `@State`, `@Bindable`, `@Environment` with `@Entry`.

### Swift 6.2 Concurrency Additions

- `@concurrent` — explicitly opt a function into the global concurrent executor. Use for CPU-bound work in default-MainActor modules.
- `Task.immediate` — starts a task that runs synchronously up to its first suspension point. Useful when you need synchronous setup before async work.
- `isolated deinit` — deinitializers can be isolated to an actor for safe cleanup of actor-owned resources.
- Task priority escalation — `withTaskPriorityEscalationHandler` lets you observe and react to priority boosts.
- Task naming — `Task(name: "FetchProfile") { }` makes tasks visible in Instruments and the debugger.

For constructive concurrency patterns (structured concurrency, async streams, bridging, migration tables), see [`swift-concurrency-patterns.md`](swift-concurrency-patterns.md). For compiler diagnostics, see [`swift-concurrency-diagnostics.md`](swift-concurrency-diagnostics.md).

### Concurrency

- prefer `async` / `await`
- prefer structured tasks
- check cancellation in long-running work
- use actors or explicit isolation for shared mutable state
- prefer `Task {}` over `Task.detached` unless you explicitly need detached behavior

### UI boundaries

- do not update UI-facing state from a background-isolated context
- keep networking and storage layers testable and non-UI-aware
- map low-level errors into UI-safe state before presenting them

### Canvas and GPU-accelerated drawing

- use SwiftUI `Canvas` for custom data visualizations that standard controls cannot express (chart wheels, radar charts, geometric overlays)
- Canvas renders all drawing operations in a single GPU pass — suitable for 500+ operations (degree ticks, grid lines, data points)
- structure complex Canvas views as sequential layer functions: each receives `GraphicsContext` + shared geometry
- Canvas cannot handle gestures directly — overlay gestures on the Canvas view itself and compute hit targets from coordinates:
  - `SpatialTapGesture`: compute row/column from `value.location` against known geometry (e.g., `let rowIndex = Int((y - headerHeight) / rowHeight)`)
  - `DragGesture`: compute position along an axis for scrubbing (e.g., `let month = Int(relX / monthWidth)`)
  - Combine with `.sensoryFeedback(.selection, trigger: computedIndex)` for boundary-crossing haptics
  - For simple cases, invisible `Circle().fill(.clear)` tap targets work too, but coordinate math scales better for dense layouts (Gantt charts, data grids)
- use `ctx.resolve(Text(...))` to draw text in Canvas; avoid multiline `Text` (use separate resolved calls per line)
- prefer `ctx.stroke(path, with:, style: StrokeStyle(lineWidth:, dash:))` for varied line styles (dotted, dashed, solid)
- animate Canvas content via `@State` driving the data: the Canvas redraws when state changes

### Visualization state ownership

Interactive visualization views (Canvas charts, SceneKit scenes, map canvases) need a deliberate choice about where zoom, pan, and drag state lives. The right pattern depends on the interaction model:

| Interaction model | State pattern | Rationale |
|---|---|---|
| **Inspect a diagram** (chart wheel, radar chart) | Parent owns state via `@Binding` | Controls strip needs to read/write the same zoom and drag values. Gestures write through bindings. No latency concern because tilt/zoom is subtle (±7.5°). |
| **Orbit a 3D scene** (3D model viewer, SceneKit) | Parent `@State` + callback (`onZoomChange:`) | SceneKit's Coordinator drives the camera directly for smooth 60fps, then reports the final value back to the parent via callback. Parent can reset or read the value. |
| **Navigate spatial terrain** (maps, route overlays) | View-internal `@State` | Continuous pinch-zoom and pan need zero-latency gesture response. A `@Binding` round-trip adds perceptible lag during spatial navigation. Built-in zoom buttons overlay the map (standard MapKit pattern). |

Decision checklist:
- Does the controls strip need to read or write zoom/pan? → `@Binding`
- Does the visualization use UIKit/SceneKit with its own gesture handling? → callback pattern
- Is the interaction continuous spatial navigation (like a map)? → internal `@State`

#### Reset token pattern

When a visualization owns its state internally but the parent needs to trigger a reset (e.g., toolbar reset button), use an integer token:

```swift
// Parent state
var mapResetToken = 0
func reset() { mapResetToken += 1 }

// Visualization view
var resetToken: Int = 0  // default so existing callers aren't broken
@State private var zoom: CGFloat = 1
@State private var pan: CGSize = .zero

var body: some View {
    content
        .onChange(of: resetToken) {
            withAnimation(.spring(response: 0.28, dampingFraction: 0.82)) {
                zoom = 1; pan = .zero
            }
        }
}
```

The token avoids lifting all state while giving the parent a one-way "reset" signal. The view stays responsive because zoom/pan remain internal `@State` for gesture handling.

### SF Symbols for domain-specific visuals

- prefer Apple's built-in SF Symbols over custom Canvas drawing when a symbol exists for the concept
- moon phases: `moonphase.new.moon`, `moonphase.waxing.crescent`, `moonphase.first.quarter`, `moonphase.waxing.gibbous`, `moonphase.full.moon`, `moonphase.waning.gibbous`, `moonphase.last.quarter`, `moonphase.waning.crescent`
- map API string identifiers to symbol names with a switch (e.g., `"waxing_gibbous"` → `"moonphase.waxing.gibbous"`)
- use `.font(.system(size: 56))` for hero-sized symbols with `.shadow()` for glow effects
- reserve custom Canvas drawing for visualizations that have no SF Symbol equivalent (radar charts, gauge needles, circular chart wheels)

### Dual-view patterns with segmented picker

- use `@State private var viewMode` with a segmented `Picker` to switch between two dashboard views
- both views read from the same data source (no separate API calls)
- shared elements (quick links, social card) render outside the if/else, after both view blocks
- name modes by function ("Guide" / "Compass"), not by implementation ("List" / "Canvas")
- `ScrollView` + `LazyVStack` for both views — not `List`, which constrains layout too much for visual dashboards

### Score scale auto-detection

- APIs may return scores on 0-10 or 0-100 scales; detect automatically: `let max = score > 10 ? 100.0 : 10.0`
- apply consistently across score rings, progress bars, and gauge needles
- never hardcode a divisor without checking the actual data range first

### iOS 17+ interactive features

- `.scrollTransition { content, phase in }` — fade, scale, or offset sections as they enter the viewport
- `.contentTransition(.numericText(value:))` — smoothly morph digits in counters (score rings, progress displays)
- `.symbolEffect(.bounce, value:)` — animate SF Symbols on state changes
- `.sensoryFeedback(.impact(flexibility:, intensity:), trigger:)` — haptic confirmation for meaningful interactions (score animations, section toggles)
- `ShareLink(item:, subject:, message:)` — native share sheet for report sharing
- `.contextMenu { }` — long-press for secondary actions on data rows
- `.ultraThinMaterial` — glassmorphism for comparison cards and overlays

## Swift 6 Transition

- Prefer Swift 6 language mode for new iOS projects where all dependencies support it.
- Enable strict concurrency checking incrementally in existing projects (`-strict-concurrency=targeted` → `complete`).
- Resolve sendability warnings on shared state; actor isolation rules from Swift Concurrency still apply and become enforced rather than warned.
- `@Observable` types on `@MainActor` already satisfy most sendability requirements.
- Re-check dependency readiness before enabling Swift 6 mode — some libraries still emit warnings.

## Testing defaults

- use Swift Testing for new unit and integration coverage
- keep XCTest and XCUITest for UI automation and mature suites

## Avoid

- mixing multiple state models in one new feature without a reason
- using sleeps when a state-based readiness check exists
- hiding actor or sendability warnings instead of resolving them
- using `MainActor.assumeIsolated` without a documented executor guarantee; it checks isolation rather than hopping to it
- assuming the containing type determines task isolation without checking the enclosing function — `Task { ... }` inherits the closure-formation context, which may be actor-isolated or nonisolated

## Swift Concurrency crash patterns and fixes

Use the crash backtrace and imported SDK declarations to locate the actual isolation boundary. A private UIKit assertion alone does not establish which concurrency pattern caused it. For symptom-first diagnosis, load [`software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md`](../../software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md).

### `nonisolated async` delegate methods + nested `MainActor.run`

Do not assume an Apple delegate requirement is main-actor isolated. Inspect its declaration in the installed SDK, including the async and completion-handler variants. [`UNUserNotificationCenterDelegate`](https://developer.apple.com/documentation/usernotifications/unusernotificationcenterdelegate) requires assigning the delegate before launch finishes; its protocol documentation does not establish a universal main-actor execution guarantee.

For a nonisolated requirement, extract the minimal Sendable routing values before transferring work to the main actor. Avoid transferring the notification response object or an arbitrary `[AnyHashable: Any]` across isolation domains. Use `await MainActor.run` for synchronous UI-state updates from an async context, or an explicitly main-actor task from a synchronous callback; retain/cancel tasks if the operation outlives the callback. Complete a completion-handler requirement exactly once after the required work.

Annotate a requirement or conformance `@MainActor` only if the SDK and runtime callback contract allow it. An isolated conformance or targeted `@preconcurrency` annotation is not proof that an Objective-C callback arrives on that actor. Do not silence a delegate's unsynchronized mutable state with `@unchecked Sendable`.

There is no general Swift rule that `MainActor.run` makes a nonisolated function's return epilogue invalid. A reproduced compiler or SDK defect needs its own affected toolchain, stack trace, and regression test before applying a workaround globally.

### `Task { }` inherits its actor context

Swift Evolution SE-0304 specifies that an unstructured task created with `Task { ... }` inherits actor isolation from the context in which its closure is formed. Inside a main-actor-isolated method, the task body remains main-actor isolated across suspension. `Task.detached` is the API that deliberately drops actor, priority, and task-local inheritance.

The type's annotation alone is not enough to reason about a call site. A protocol requirement, delegate method, completion handler, or explicitly `nonisolated` method may form the task outside the main actor even when the containing type is `@MainActor`. Inspect the enclosing function's isolation.

```swift
@MainActor
@Observable
final class AuthSession {
    var cooldown = 0

    func startCooldown() {
        Task { [weak self] in
            // Inherits MainActor because this closure is formed in a
            // main-actor-isolated method.
            try? await Task.sleep(for: .seconds(1))
            self?.cooldown -= 1
        }
    }

    nonisolated func callbackFromSDK() {
        Task { @MainActor [weak self] in
            // Explicit hop is required because the callback is nonisolated.
            self?.cooldown = 0
        }
    }
}
```

**Decision rule:**

| Closure formation context | Use |
|---|---|
| Actor-isolated method and work belongs to that actor | `Task { ... }`; actor isolation is inherited |
| Nonisolated delegate/callback needs UI state | `Task { @MainActor [weak self] in ... }` |
| CPU work must deliberately leave the actor | With Swift 6.2+, use `@concurrent`; inspect `NonisolatedNonsendingByDefault` before relying on `nonisolated async`. Use `Task.detached` only when lost inheritance and unstructured lifetime are intentional. |
| View lifecycle work | SwiftUI `.task` so cancellation follows the view |

Actor correctness does not make an unstructured task lifecycle-safe. Store and cancel long-lived task handles, check cancellation after sleeps, and guard delayed state changes with request identity so an older task cannot erase newer state.

### `actor` → `@MainActor final class` refactoring guidance

A main-actor caller resumes on the main actor after awaiting another actor. Actor reentrancy can change state during suspension, so re-check assumptions after `await`. Choose `@MainActor final class` for UI-owned state, and a separate actor for shared mutable state or work that should not occupy the UI executor. Caller count alone does not justify moving networking, decoding, or storage work onto the main actor.

[SE-0338](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0338-clarify-execution-non-actor-async.md) defines resumption on an isolated function's executor. [SE-0461](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0461-async-function-isolation.md) changes nonisolated async execution with `NonisolatedNonsendingByDefault`: it can inherit caller isolation; `@concurrent` explicitly selects concurrent execution. Inspect language mode and feature flags before diagnosing an executor hop.

### `@Sendable async` closure isolation footgun

`@Sendable` constrains capture/transfer safety; it does not select an executor. A main-actor caller remains isolated after awaiting the closure, while the closure body's isolation depends on its type, formation context, and language settings.

If the body needs UI-owned state, express that contract explicitly:

```swift
typealias UIExecutor = @MainActor @Sendable (URLRequest) async throws -> (Data, URLResponse)
```

For networking or decoding without UI state, preserve the appropriate non-UI isolation and return Sendable results to the main-actor caller. Do not change every request executor to `@MainActor` to fix a supposed loss of caller isolation.

### `SCNView` reassignment in `updateUIView` anti-pattern

Create the view and initial scene in `makeUIView`; apply changed inputs in `updateUIView`. Prefer incremental node/material/camera updates when a rebuild would reset interaction state or perform expensive work. A no-op update method is correct only for immutable inputs; otherwise it leaves the UIKit view stale.

A coordinator can own scene objects and forward delegate/gesture changes to SwiftUI. Keep UIKit mutations on the main actor, and inspect SceneKit callbacks separately before touching UI from them. Scene replacement in `updateUIView` is not inherently proof of an off-main crash; establish the failing call with a backtrace before imposing a workaround.

[Apple's UIViewRepresentable contract](https://developer.apple.com/documentation/swiftui/uiviewrepresentable) defines creation, state updates, coordinator communication, and teardown. Clean up retained callbacks/tasks in `dismantleUIView` when their lifetime belongs to the represented view.

### Diagnostic tools and when to use each

When a crash looks like a Swift Concurrency bug, walk this ladder from cheapest to most expensive:

| Tool | Catches | Cost | How to enable |
|------|---------|------|---------------|
| **Console output** | Known error patterns, assertions, warnings | free | Always on |
| **Main Thread Checker** (pause on issue) | UIKit/AppKit APIs called from background threads | low diagnostic overhead | On by default in Debug schemes; with XcodeGen, `project.yml` → `schemes.<name>.run: stopOnEveryMainThreadCheckerIssue: true` (the only related ProjectSpec keys are that and `disableMainThreadChecker`) — leave on permanently |
| **Thread Sanitizer** | Data races on any shared storage including `@Observable` | instrumentation overhead; measure on the workload | `xcodebuild test -scheme <name> -enableThreadSanitizer YES`, or the scheme's Diagnostics tab — XcodeGen's ProjectSpec has no TSan key and silently ignores unknown keys — on demand only |
| **lldb `bt`** | Full symbolicated backtrace of the paused thread | free, requires paused process | Type `bt` in LLDB prompt when debugger pauses; set Objective-C Exception Breakpoint in Xcode Breakpoint Navigator to force a pause on `NSInternalInconsistencyException` |
| **lldb `image lookup --address <hex>`** | Function name + source line for a raw crash backtrace address | free | `image lookup --address 0x1071b5244` |
| **Web search the exact symbol** | Documented known bugs matching the exact crash signature | free, often fastest | Search for the private symbol (e.g. `_performBlockAfterCATransactionCommitSynchronizes`) + platform + year |
| **`git bisect`** | Regression introduced by a specific commit | hours of rebuilds | `git bisect start`, last resort |

Main Thread Checker covers known system APIs with thread requirements; Thread Sanitizer detects exercised memory races. Neither proves that every UI access is correct, and a private crash symbol does not determine which tool will expose its cause. For iOS Thread Sanitizer runs, use Simulator rather than a physical device; see [Apple diagnostic guidance](https://developer.apple.com/documentation/xcode/diagnosing-memory-thread-and-crash-issues-early).

### DEBUG marker pattern for binary identity verification

When you're making architectural changes (actor → @MainActor conversions, etc.) and need to verify that the fresh binary is actually running on the device (Xcode's incremental build can reuse stale object files), add a temporary marker print to a class `init` that runs at launch:

```swift
@MainActor
final class APIClient {
    static let shared = APIClient(...)

    init(...) {
        // ... existing init body ...

        #if DEBUG
        print("[APIClient] @MainActor build marker — fix-revision-2026-04-11")
        #endif
    }
}
```

Run the app, watch the Xcode console at launch. If you see the marker line, your latest code is on the device. If you don't, you're running a stale binary — clean build folder, delete the app from the device, reinstall.

Remove the print after the debugging session — it's not meant to live in the committed codebase long-term.

### The web-search escape valve

**Meta-lesson from a real 17-iteration debugging session in a reference app:** when a bug persists across 3+ "obviously correct" fixes targeting the same symptom class, **stop code-reviewing and web-search**. Each additional fix is almost certainly a real independent bug that was hiding behind the same symptom class, but it is not THE bug. The actual root cause is usually in a place that code review is blind to — a framework interaction (UNUserNotificationCenter, SceneKit, StoreKit), a private SwiftUI machinery, or a Swift Concurrency edge case that's documented but not obvious from the API surface.

Symptoms that should trigger the web-search escape valve immediately:

- Crash fires inside a private system symbol (underscore-prefixed Apple frameworks like `_performBlockAfterCATransactionCommitSynchronizes:`)
- Crash fires on a Swift Concurrency Task on a cooperative queue, not main thread
- Crash reproduces on a single line in a short function that compiles cleanly and looks correct
- The same assertion message recurs across multiple "obviously correct" fixes
- You're adding defensive `await MainActor.run { ... }` wraps because "it can't hurt" — that's the pattern that caused the reference app's bug. More wraps in the wrong places make it worse.

Search query template: `<private symbol> "<exact assertion message>" <platform> <year>`. Examples that would have closed that bug at iteration 1 instead of iteration 17:

- `_performBlockAfterCATransactionCommitSynchronizes "Call must be made on main thread" SwiftUI 2025`
- `UNUserNotificationCenter nonisolated async crash main thread Swift 6`
- `nonisolated async delegate MainActor.run crash Swift Concurrency`

The private SwiftUI symbol makes the query highly specific — there's usually exactly ONE blog post, Apple Forums thread, or GitHub issue that matches. A 2-minute search has closed cases that code review couldn't.

## Backend Integration: Polymorphic and Tier-Gated DTOs

### The Problem

Backend APIs often return polymorphic responses where a field can be either real data OR a gated placeholder (e.g., `{ gated: true, teaser: {...} }` for free-tier users). Swift's `Decodable` fails the ENTIRE response when ANY field has a type mismatch — even optional fields inside nested structs.

### GatedOr<T> Union Type

For fields that can be either real data or a gated placeholder:

```swift
enum GatedOr<T: Decodable & Equatable>: Decodable, Equatable {
    case data(T)
    case gated

    init(from decoder: Decoder) throws {
        if let value = try? T(from: decoder) {
            self = .data(value)
            return
        }
        self = .gated
    }

    var value: T? {
        if case .data(let v) = self { return v }
        return nil
    }

    var isGated: Bool {
        if case .gated = self { return true }
        return false
    }
}
```

Usage:
```swift
struct ProfileResponse: Decodable, Equatable {
    let profile: UserProfile?          // always present
    let derivedNumbers: GatedOr<DerivedNumberData>?    // data for paid tier, gated for free
    let advanced: GatedOr<AdvancedData>?     // data for paid tier, gated for free
}
```

### AnyCodableValue for Opaque JSON

When a field can be any JSON type (string, number, object, array) and you don't control the shape:

```swift
enum AnyCodableValue: Decodable, Equatable {
    case string(String)
    case int(Int)
    case double(Double)
    case bool(Bool)
    case object([String: AnyCodableValue])
    case array([AnyCodableValue])
    case null

    init(from decoder: Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() { self = .null }
        else if let v = try? container.decode(Bool.self) { self = .bool(v) }
        else if let v = try? container.decode(Int.self) { self = .int(v) }
        else if let v = try? container.decode(Double.self) { self = .double(v) }
        else if let v = try? container.decode(String.self) { self = .string(v) }
        else if let v = try? container.decode([String: AnyCodableValue].self) { self = .object(v) }
        else if let v = try? container.decode([AnyCodableValue].self) { self = .array(v) }
        else { self = .null }
    }
}
```

Use for fields like `profile.summary` that might be a string OR an object depending on the backend version.

### Lenient Custom Decoders

When a DTO has fields that might have unexpected types, use `try?` per field:

```swift
extension JournalEntry: Decodable {
    private enum CodingKeys: String, CodingKey {
        case id, entryDate, description, emotions, analysis
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try? c.decodeIfPresent(String.self, forKey: .id)
        entryDate = try? c.decodeIfPresent(String.self, forKey: .entryDate)
        analysis = try? c.decodeIfPresent(EntryAnalysis.self, forKey: .analysis)
        // Each field that fails becomes nil instead of crashing the entire response
    }
}
```

### Response Wrapper Pattern

Backend APIs often wrap data in a response object. Don't decode the inner type directly:

```swift
// BAD: Wrong — assumes flat response
dailyDigest = try await apiClient.get(.dailyDigest(profileId: "user123"))

// GOOD: Right — decode the wrapper first
let response: DailyDigestResponse = try await apiClient.get(.dailyDigest(profileId: "user123"))
dailyDigest = response.digest
```

### Common Decode Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| "data couldn't be read" on ALL fields | One nested field has wrong type | Add `os.Logger` diagnostic, fix the specific field |
| Optional field fails instead of becoming nil | Field present but type mismatches | Custom `init(from:)` with `try?` |
| Gated fields crash free-tier users | Backend sends `{gated: true}` instead of data | Use `GatedOr<T>` |
| `.convertFromSnakeCase` not matching | JSON is already camelCase | Works fine — no conversion needed for camelCase keys |

### API Error Handling for Empty States

Backend may return 404/401 when a resource doesn't exist (e.g., no partner, no groups). Handle these as empty state, not errors:

```swift
} catch {
    if case APIError.notFound = error {
        loadState = .loaded  // empty state, not error
        return
    }
    loadState = .failed(error.localizedDescription)
}
```

## @ViewBuilder Pitfall: guard/return

Swift result builders do NOT support `guard ... else { return }`. The compiler gives unhelpful errors like "non-void function should return a value" or "failed to produce diagnostic."

```swift
// BAD: Crashes the compiler
@ViewBuilder
var body: some View {
    guard let data = response else { return }  // FAILS
    Text(data.title)
}

// GOOD: Use if-let instead
@ViewBuilder
var body: some View {
    if let data = response {
        Text(data.title)
    } else {
        EmptyView()
    }
}
```

## @ViewBuilder Pitfall: Type Checker Crashes

Complex view bodies cause "failed to produce diagnostic for expression" — the Swift type checker gives up. Common triggers:

```swift
// BAD: Conditional inside trailing closure ViewBuilder
.overlay { if isActive { RoundedRectangle().stroke(color) } }
.background { if showPanel { OverlayPanel { Color.clear } } }

// GOOD: Use parenthesized form with ternary — no branching for the type checker
.overlay(RoundedRectangle().stroke(isActive ? color : .clear))
.background(OverlayPanel { Color.clear })
```

```swift
// BAD: Tuple array with ForEach(enumerated()) — crashes in complex bodies
let phases: [(String, Color, Bool)] = [...]
ForEach(Array(phases.enumerated()), id: \.offset) { index, phase in ... }

// GOOD: Use Identifiable structs — gives ForEach a clean type boundary
struct PhaseStep: Identifiable { let id: Int; let label: String; let color: Color }
ForEach(steps) { step in ... }
```

**General fixes when the type checker crashes:**
1. Break the complex view function into 2-3 smaller named helper functions (`eventCard` → `eventInfo` + `eventCountdown`). Each function boundary resets type inference.
2. Add explicit type annotations to `let` bindings (`let tint: Color = ...` instead of `let tint = ...`).
3. Replace trailing closure `.background { }` with parenthesized `.background()`.
4. Extract inline conditionals into separate `@ViewBuilder` functions.

## Type Naming Conflicts

SwiftUI reserves common names. If you create `struct Group`, it shadows SwiftUI's `Group` view and causes compile errors across the entire project. Prefix with your app name:

- `Group` → `AppGroup` or `ChartGroup`
- `Section` → avoid as a model name
- `Label` → avoid as a model name
- `Image` → avoid as a model name
