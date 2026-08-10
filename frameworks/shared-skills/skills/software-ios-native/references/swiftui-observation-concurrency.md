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
| **Inspect a diagram** (natal chart wheel, radar chart) | Parent owns state via `@Binding` | Controls strip needs to read/write the same zoom and drag values. Gestures write through bindings. No latency concern because tilt/zoom is subtle (±7.5°). |
| **Orbit a 3D scene** (Solar 3D, SceneKit) | Parent `@State` + callback (`onZoomChange:`) | SceneKit's Coordinator drives the camera directly for smooth 60fps, then reports the final value back to the parent via callback. Parent can reset or read the value. |
| **Navigate spatial terrain** (maps, astrocartography) | View-internal `@State` | Continuous pinch-zoom and pan need zero-latency gesture response. A `@Binding` round-trip adds perceptible lag during spatial navigation. Built-in zoom buttons overlay the map (standard MapKit pattern). |

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
- reserve custom Canvas drawing for visualizations that have no SF Symbol equivalent (radar charts, gauge needles, natal chart wheels)

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
- wrapping post-await code in `await MainActor.run { ... }` from inside a `nonisolated async` function — it looks defensive but causes the continuation epilogue to crash on main-thread assertion (see "Swift Concurrency crash patterns and fixes" below)
- reaching for bare `Task { ... }` from a `@MainActor` class without explicit `Task { @MainActor in ... }` annotation — with `StrictConcurrency` the body runs on the global executor and crashes on any `@Observable` mutation

## Swift Concurrency crash patterns and fixes

This section documents the specific Swift Concurrency anti-patterns that have caused real crashes in this codebase and in the broader iOS community in 2025–2026. For a symptom-first triage runbook (start here when you have a crash log and no hypothesis), see [`software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md`](../../software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md).

Read this whole section before adding any `MainActor.run`, `Task { }`, `actor`, or `@Sendable async` pattern to new code — every one of these patterns has a documented footgun.

### `nonisolated async` delegate methods + nested `MainActor.run`

**Crash signature:**

```
*** Assertion failure in -[_TtC...SwiftUIApplication _performBlockAfterCATransactionCommitSynchronizes:],
    UIApplication.m:3426
*** Terminating app due to uncaught exception 'NSInternalInconsistencyException',
    reason: 'Call must be made on main thread'
```

The thread that crashes is a Swift Concurrency Task on `com.apple.root.user-initiated-qos.cooperative`, not main.

**Mechanism:** when an `async` function returns, Swift generates a continuation epilogue that runs cleanup code at the end of the call. For UN delegate methods (and other Apple async delegate protocols), that epilogue must execute on the main thread. Wrapping the body in a nested `await MainActor.run { ... }` from inside an `nonisolated async` function violates the contract — the epilogue tries to run on main but is forced through an actor hop and hits an isolation mismatch. UIKit asserts and the app terminates.

**The bug pattern (do NOT do this):**

```swift
final class AppDelegate: NSObject,
    UIApplicationDelegate,
    UNUserNotificationCenterDelegate {

    nonisolated func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        let userInfo = response.notification.request.content.userInfo
        await MainActor.run {                    // ← THE TRAP
            NotificationCenter.default.post(
                name: .didOpenPushNotification,
                object: nil,
                userInfo: ["userInfo": userInfo]
            )
        }
    }
}
```

**The fix** — annotate the class `@unchecked Sendable` and the delegate methods `@MainActor` directly. Remove the nested `MainActor.run` wraps. The entire delegate body, including the auto-generated continuation epilogue, then runs on `@MainActor` from start to finish:

```swift
final class AppDelegate: NSObject,
    UIApplicationDelegate,
    UNUserNotificationCenterDelegate,
    @unchecked Sendable {                        // ← required because UN protocol is non-Sendable

    @MainActor                                    // ← directly on the method, not via MainActor.run
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse
    ) async {
        let userInfo = response.notification.request.content.userInfo
        NotificationCenter.default.post(
            name: .didOpenPushNotification,
            object: nil,
            userInfo: ["userInfo": userInfo]
        )
    }
}
```

**Why `@unchecked Sendable`:** `UNUserNotificationCenterDelegate` is a non-Sendable Apple protocol. The Swift compiler refuses to conform a pure `@MainActor` class to a non-Sendable protocol without the `@unchecked` escape. Apple has acknowledged in [Apple Developer Forums thread 762217](https://developer.apple.com/forums/thread/762217) that the UN framework has not yet been audited for Swift 6 / strict concurrency, so this workaround is the community-standard fix.

**Alternative workarounds (both valid, pick one):**

- `@preconcurrency` on the protocol conformance: `final class AppDelegate: NSObject, @preconcurrency UNUserNotificationCenterDelegate` — silences the Sendable errors without `@unchecked`. Pick this if you want compiler-tracked migration rather than a blanket escape.
- Mark the class itself `@MainActor`: conflicts with `UIApplicationDelegate` non-isolated requirements in some Xcode versions. Only works if you can also add `@preconcurrency` on `UIApplicationDelegate` or avoid methods that the compiler treats as non-isolated.

**References:**

- [3 Swift Concurrency Challenges from the Last 2 Weeks (twocentstudios, 2025-08-12)](https://twocentstudios.com/2025/08/12/3-swift-concurrency-challenges-from-the-last-2-weeks/) — the blog post that documented this exact crash with the exact same symbol name and explained the continuation-epilogue mechanism
- [Apple Developer Forums thread 796407 — Crash in Swift 6 when using UNUserNotificationCenter](https://developer.apple.com/forums/thread/796407)
- [Apple Developer Forums thread 762217 — Implement UNUserNotificationCenterDelegate](https://developer.apple.com/forums/thread/762217)
- [Apple Developer Forums thread 709563 — MainActor and NSInternalInconsistencyException](https://developer.apple.com/forums/thread/709563)

The same rule applies to `ASAuthorizationControllerDelegate`, `MKLocalSearchCompleterDelegate`, and other async Apple delegate protocols. If the method is async and wants to touch `@MainActor` state, annotate the method `@MainActor` directly — do NOT use nested `MainActor.run`.

### Bare `Task { }` does not inherit `@MainActor`

In Swift 5.7+ with the `StrictConcurrency` upcoming-feature enabled, a bare `Task { ... }` spawned from inside a `@MainActor` class runs on the global executor, NOT on the main actor. The body has no isolation. Any `@Observable` mutation inside the body is an off-main publish and crashes with the same `_performBlockAfterCATransactionCommitSynchronizes:` assertion documented above.

**The bug pattern:**

```swift
@MainActor
@Observable
final class AuthSession {
    var otpResendCooldown: Int = 0                        // ← tracked @Observable

    private func startResendCooldownTimer() {
        otpResendCooldown = 60
        Task { [weak self] in                              // ← BARE Task, runs on global executor
            while let self, self.otpResendCooldown > 0 {
                try? await Task.sleep(for: .seconds(1))
                self.otpResendCooldown -= 1                // ← off-main @Observable mutation
            }
        }
    }
}
```

**The fix** — explicit `@MainActor` isolation on the Task:

```swift
private func startResendCooldownTimer() {
    otpResendCooldown = 60
    Task { @MainActor [weak self] in                       // ← explicit @MainActor
        while let self, self.otpResendCooldown > 0 {
            try? await Task.sleep(for: .seconds(1))
            self.otpResendCooldown -= 1                    // ← now on main, safe
        }
    }
}
```

**Real instances found in cosmic-swift** (worked examples of the same anti-pattern):

- `Core/Auth/AuthSession.swift` — `startResendCooldownTimer` per-second mutation of `otpResendCooldown`
- `Core/Billing/StoreKitManager.swift` — `startTransactionListener` `for await Transaction.updates` loop mutating `activeSubscriptionProductID`
- `Core/Analytics/AnalyticsClient.swift` — `scheduleFlush` debounce timer mutating `lastFlushAt` / `pendingEventCount`
- `Features/Ask/AskStore.swift` — two `submitState` cleanup tasks that sleep then reset state

Before `StrictConcurrency` was enabled, these would have been runtime warnings. With strict mode, they're hard crashes the first time the loop body ran.

**Decision rule:**

| Context | Use |
|---------|-----|
| Task body needs to mutate `@MainActor` state | `Task { @MainActor [weak self] in ... }` |
| Task body calls an `async` method and then doesn't mutate anything | `Task { await model.foo() }` — await hops to main, post-return tail is bare but doesn't touch anything |
| Task body does non-UI background work only | `Task.detached { ... }` — deliberately non-isolated |
| SwiftUI `.task` modifier or `.onReceive` closure inside a `View` | Already `@MainActor` — bare `Task { await model.foo() }` is fine because the closure inherits |

**Rule of thumb:** if you're adding a `Task` inside a `@MainActor` class AND the body touches any stored property (mutating or reading), write `Task { @MainActor [weak self] in ... }` explicitly. It never hurts and often prevents the bug. Every bare `Task { ... }` in a `@MainActor` class is a latent crash waiting for the right timing.

### `actor` → `@MainActor final class` refactoring guidance

If all consumers of an `actor` type are `@MainActor` types, the `@MainActor → actor → @MainActor` round-trip via `await` introduces resumption ambiguity where the post-await tail can land on the inner actor's executor instead of `@MainActor`. This is a subtle form of the continuation-epilogue bug — the Swift compiler doesn't statically forbid the pattern, but the runtime resumption scheduling can place the continuation on the wrong actor.

**Rule of thumb:** promote the type to `@MainActor final class` unless it genuinely needs to coordinate concurrent access from multiple non-`@MainActor` contexts.

**Worked examples from cosmic-swift:**

```swift
// BEFORE — separate actor, subtle resumption bugs
actor APIClient {
    static let shared = APIClient(...)
    private let session: URLSession

    func get<T: Decodable>(_ endpoint: Endpoint) async throws -> T { ... }
}

@MainActor @Observable final class DashboardStore {
    @ObservationIgnored let apiClient = APIClient.shared

    func load() async {
        do {
            let response: Snapshot = try await apiClient.get(.dashboard)
            snapshot = response              // ← can land off-main after actor-bridge hop
        } catch {
            lastError = error.localizedDescription   // ← same
        }
    }
}
```

```swift
// AFTER — @MainActor final class, post-await tail guaranteed on main
@MainActor
final class APIClient {
    static let shared = APIClient(...)
    private let session: URLSession

    func get<T: Decodable>(_ endpoint: Endpoint) async throws -> T { ... }
}

@MainActor @Observable final class DashboardStore {
    @ObservationIgnored let apiClient = APIClient.shared

    func load() async {
        do {
            let response: Snapshot = try await apiClient.get(.dashboard)
            snapshot = response              // ← now reliably on main
        } catch {
            lastError = error.localizedDescription
        }
    }
}
```

**Cascading rule:** promoting an `actor` to `@MainActor` often requires cascading `@MainActor` annotations on any `struct` that takes a default parameter of `.shared`:

```swift
// BEFORE
struct PushRegistrationService {
    private let apiClient: APIClient
    init(apiClient: APIClient = .shared) { self.apiClient = apiClient }  // ← error: main-actor default value in nonisolated init
}

// AFTER
@MainActor
struct PushRegistrationService {
    private let apiClient: APIClient
    init(apiClient: APIClient = .shared) { self.apiClient = apiClient }  // ← ok, struct is @MainActor
}
```

The cascade is mechanical: the compiler tells you every default-parameter site that needs `@MainActor`. Walk the list, annotate each struct/class, re-compile, repeat.

**When to keep `actor` instead:** if the type is genuinely consumed from multiple actor contexts (background download manager, watch app extension, share extension), keep it as `actor`. The round-trip bug only applies when all consumers are `@MainActor` and the wrap is pure overhead.

### `@Sendable async` closure isolation footgun

When a `@MainActor` function awaits a closure typed as `@Sendable async`, Swift's continuation scheduler does not reliably hop back to `@MainActor` after the await. The `@Sendable` annotation tells the compiler "this closure can be passed across actor boundaries" — which includes leaving the continuation on the wrong side.

**Symptoms:** same `_performBlockAfterCATransactionCommitSynchronizes:` crash, usually fires inside a retry/debounce loop that awaits a network-executor closure.

**The bug pattern:**

```swift
@MainActor @Observable final class AnalyticsClient {
    typealias RequestExecutor = @Sendable (URLRequest) async throws -> (Data, URLResponse)
    //                          ^^^^^^^^^ — @Sendable, escapes actor isolation

    private(set) var lastFlushAt: Date?         // ← tracked @Observable

    func flush() async {
        let request = buildRequest()
        let (_, response) = try await requestExecutor(request)   // ← the await
        lastFlushAt = Date()                    // ← can land off-main
    }
}
```

**The fix** — retype the closure as `@MainActor` instead of `@Sendable`:

```swift
typealias RequestExecutor = @MainActor (URLRequest) async throws -> (Data, URLResponse)
```

Now the closure inherits `@MainActor` isolation, the await hops cleanly, and the post-await tail is guaranteed on main.

**When to keep `@Sendable`:** if the closure genuinely runs on a non-main executor (e.g. a background image decoder or download task), keep it `@Sendable` but wrap the post-await mutations in explicit `await MainActor.run { ... }` blocks. The footgun is specifically `@Sendable async` awaited from `@MainActor` WITHOUT an explicit hop afterward.

### `SCNView` reassignment in `updateUIView` anti-pattern

`UIViewRepresentable.updateUIView(_:context:)` is called on every SwiftUI body re-render. If you rebuild an entire `SCNScene` and reassign `view.scene = scene` inside it, each reassignment schedules a CATransaction commit on SceneKit's render server thread, which then calls back into UIKit off-main and crashes with the same `_performBlockAfterCATransactionCommitSynchronizes:` assertion.

**The bug pattern (do NOT do this):**

```swift
// AT CALL SITE — body rebuilds scene on every render
var body: some View {
    MoonSceneView(scene: buildMoonScene(phase: currentPhase))  // ← new scene every render
}

// UIViewRepresentable wrapper
private struct MoonSceneView: UIViewRepresentable {
    let scene: SCNScene

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView()
        view.scene = scene
        view.allowsCameraControl = true                         // ← also a trap
        return view
    }

    func updateUIView(_ view: SCNView, context: Context) {
        view.scene = scene                                      // ← THE BUG — reassigns on every body re-render
    }
}
```

Every parent re-render rebuilds `buildMoonScene(...)`, SwiftUI calls `updateUIView`, SceneKit tears down the old scene graph and sets up the new one, schedules a render server commit, calls back into UIKit off-main → crash.

**The minimum fix** — make `updateUIView` a no-op, remove camera control, build the scene once in `makeUIView`:

```swift
private struct MoonSceneView: UIViewRepresentable {
    let scene: SCNScene

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView()
        view.scene = scene                                      // ← set once
        view.allowsCameraControl = false                        // ← dashboard widget shouldn't be a draggable 3D toy
        view.backgroundColor = .clear
        view.isOpaque = false
        return view
    }

    func updateUIView(_ view: SCNView, context: Context) {
        // Intentionally a no-op. Reassigning view.scene here triggers a
        // SceneKit render-thread CATransaction commit that crashes via
        // _performBlockAfterCATransactionCommitSynchronizes: "Call must
        // be made on main thread" the next time the parent re-renders.
    }
}
```

SwiftUI's structural identity guarantees the same `SCNView` instance persists across body re-renders, so the scene set in `makeUIView` survives. For a daily moon widget whose phase changes once per day, this is enough — the dashboard reloads on app launch.

**The better fix — Coordinator pattern for incremental updates:**

When the scene DOES need to update in response to prop changes (e.g. a continuously-spinning 3D solar system that responds to user drag), use a `@MainActor` Coordinator class to own the scene and mutate it incrementally:

```swift
private struct Solar3DSceneViewport: UIViewRepresentable {
    let planets: [Solar3DScenePlanet]
    let cameraPreset: Solar3DCameraPreset

    func makeCoordinator() -> Coordinator { Coordinator() }

    func makeUIView(context: Context) -> SCNView {
        let view = SCNView(frame: .zero)
        view.backgroundColor = .clear
        view.autoenablesDefaultLighting = false
        view.allowsCameraControl = false
        context.coordinator.configure(view: view)              // ← coordinator owns scene
        return view
    }

    func updateUIView(_ uiView: SCNView, context: Context) {
        context.coordinator.update(                             // ← incremental mutation only
            planets: planets,
            cameraPreset: cameraPreset
        )
    }

    @MainActor
    final class Coordinator: NSObject {
        private let scene = SCNScene()                          // ← built once, mutated forever
        private let contentNode = SCNNode()
        private let cameraNode = SCNNode()
        private weak var view: SCNView?

        func configure(view: SCNView) {
            view.scene = scene
            self.view = view
            // initial scene setup
        }

        func update(planets: [Solar3DScenePlanet], cameraPreset: Solar3DCameraPreset) {
            // incremental mutations on contentNode children, cameraNode transform, etc.
            // NEVER reassign view.scene
        }
    }
}
```

Key rules:

- Build `SCNScene`, `SCNNode`s, lights, camera once in `makeUIView` or the Coordinator init
- `updateUIView` MUST NOT reassign `view.scene`
- Mutate the existing scene graph (add/remove child nodes, update transforms, change materials) instead of rebuilding
- Keep the Coordinator `@MainActor` so its methods are main-isolated
- Don't use `allowsCameraControl = true` on widgets — it adds gesture recognizers and CADisplayLink callbacks on render threads that make the crash more likely

**References:** [Apple Developer Forums thread 124671 (UIViewRepresentable update loop warnings)](https://developer.apple.com/forums/thread/124671), [Apple Developer Forums thread 659873 (SceneView in SwiftUI)](https://developer.apple.com/forums/thread/659873).

### Diagnostic tools and when to use each

When a crash looks like a Swift Concurrency bug, walk this ladder from cheapest to most expensive:

| Tool | Catches | Cost | How to enable |
|------|---------|------|---------------|
| **Console output** | Known error patterns, assertions, warnings | free | Always on |
| **Main Thread Checker** (pause on issue) | UIKit/AppKit APIs called from background threads | free in Debug, zero runtime overhead | `project.yml` → `schemes.<name>.run: enableMainThreadChecker: true; stopOnEveryMainThreadCheckerIssue: true` — leave on permanently |
| **Thread Sanitizer** | Data races on any shared storage including `@Observable` | 5–15× slowdown, 5–10× memory | `project.yml` → `schemes.<name>.run: enableThreadSanitizer: true; stopOnEveryThreadSanitizerIssue: true` — on demand only |
| **lldb `bt`** | Full symbolicated backtrace of the paused thread | free, requires paused process | Type `bt` in LLDB prompt when debugger pauses; set Objective-C Exception Breakpoint in Xcode Breakpoint Navigator to force a pause on `NSInternalInconsistencyException` |
| **lldb `image lookup --address <hex>`** | Function name + source line for a raw crash backtrace address | free | `image lookup --address 0x1071b5244` |
| **Web search the exact symbol** | Documented known bugs matching the exact crash signature | free, often fastest | Search for the private symbol (e.g. `_performBlockAfterCATransactionCommitSynchronizes`) + platform + year |
| **`git bisect`** | Regression introduced by a specific commit | hours of rebuilds | `git bisect start`, last resort |

**Important:** Main Thread Checker does NOT catch the `_performBlockAfterCATransactionCommitSynchronizes:` crash class. MTC is a UIKit-level tool that only catches `user code → UIKit API call from background thread`. The crash pattern documented in this section is a SwiftUI internal mechanism triggered by off-main `@Observable` mutations — a DIFFERENT machinery. **Use Thread Sanitizer for that bug class.**

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

**Meta-lesson from a real 17-iteration cosmic-swift debugging session:** when a bug persists across 3+ "obviously correct" fixes targeting the same symptom class, **stop code-reviewing and web-search**. Each additional fix is almost certainly a real independent bug that was hiding behind the same symptom class, but it is not THE bug. The actual root cause is usually in a place that code review is blind to — a framework interaction (UNUserNotificationCenter, SceneKit, StoreKit), a private SwiftUI machinery, or a Swift Concurrency edge case that's documented but not obvious from the API surface.

Symptoms that should trigger the web-search escape valve immediately:

- Crash fires inside a private system symbol (underscore-prefixed Apple frameworks like `_performBlockAfterCATransactionCommitSynchronizes:`)
- Crash fires on a Swift Concurrency Task on a cooperative queue, not main thread
- Crash reproduces on a single line in a short function that compiles cleanly and looks correct
- The same assertion message recurs across multiple "obviously correct" fixes
- You're adding defensive `await MainActor.run { ... }` wraps because "it can't hurt" — that's the pattern that caused the cosmic-swift bug. More wraps in the wrong places make it worse.

Search query template: `<private symbol> "<exact assertion message>" <platform> <year>`. Examples that would have closed the cosmic-swift bug at iteration 1 instead of iteration 17:

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
struct NumerologyResponse: Decodable, Equatable {
    let profile: NumerologyProfile?          // always present
    let angelNumbers: GatedOr<AngelData>?    // data for cosmic, gated for free
    let advanced: GatedOr<AdvancedData>?     // data for cosmic, gated for free
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

Use for fields like `birthday.meaning` that might be a string OR an object depending on the backend version.

### Lenient Custom Decoders

When a DTO has fields that might have unexpected types, use `try?` per field:

```swift
extension DreamEntry: Decodable {
    private enum CodingKeys: String, CodingKey {
        case id, dreamDate, description, emotions, interpretation
    }

    init(from decoder: Decoder) throws {
        let c = try decoder.container(keyedBy: CodingKeys.self)
        id = try? c.decodeIfPresent(String.self, forKey: .id)
        dreamDate = try? c.decodeIfPresent(String.self, forKey: .dreamDate)
        interpretation = try? c.decodeIfPresent(DreamInterpretation.self, forKey: .interpretation)
        // Each field that fails becomes nil instead of crashing the entire response
    }
}
```

### Response Wrapper Pattern

Backend APIs often wrap data in a response object. Don't decode the inner type directly:

```swift
// BAD: Wrong — assumes flat response
dailyReading = try await apiClient.get(.horoscopeDaily(sign: "cancer"))

// GOOD: Right — decode the wrapper first
let response: DailyHoroscopeResponse = try await apiClient.get(.horoscopeDaily(sign: "cancer"))
dailyReading = response.horoscope
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
.background { if showPanel { CosmicPanel { Color.clear } } }

// GOOD: Use parenthesized form with ternary — no branching for the type checker
.overlay(RoundedRectangle().stroke(isActive ? color : .clear))
.background(CosmicPanel { Color.clear })
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
1. Break the complex view function into 2-3 smaller named helper functions (`eclipseCard` → `eclipseInfo` + `eclipseCountdown`). Each function boundary resets type inference.
2. Add explicit type annotations to `let` bindings (`let tint: Color = ...` instead of `let tint = ...`).
3. Replace trailing closure `.background { }` with parenthesized `.background()`.
4. Extract inline conditionals into separate `@ViewBuilder` functions.

## Type Naming Conflicts

SwiftUI reserves common names. If you create `struct Group`, it shadows SwiftUI's `Group` view and causes compile errors across the entire project. Prefix with your app name:

- `Group` → `CosmicGroup` or `ChartGroup`
- `Section` → avoid as a model name
- `Label` → avoid as a model name
- `Image` → avoid as a model name
