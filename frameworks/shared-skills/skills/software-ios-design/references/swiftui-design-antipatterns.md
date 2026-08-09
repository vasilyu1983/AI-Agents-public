# SwiftUI Design Anti-Patterns

## Table of Contents

- [State and Identity](#state-and-identity)
- [Navigation](#navigation)
- [Layout](#layout)
- [Color and Dark Mode](#color-and-dark-mode)
- [Animations and Transitions](#animations-and-transitions)
- [Controls and Actions](#controls-and-actions)
- [Sheets and Modals](#sheets-and-modals)
- [Data Display](#data-display)
- [Identity, Previews, and Tooling](#identity-previews-and-tooling)
- [Verification](#verification)

Common SwiftUI design and layout anti-patterns that degrade iOS apps. Each entry lists the smell, why it's wrong, and the fix. Focused on design-quality issues, not general SwiftUI correctness.

For runtime/compile crashes and framework footguns specific to Canvas and iOS 26, see the Anti-Patterns section of `SKILL.md`. For accessibility-specific anti-patterns see [ios-accessibility-patterns.md](ios-accessibility-patterns.md).

## State and Identity

### `.id(UUID())` as a "force refresh" trick

```swift
// ANTI
SomeView(data: data).id(UUID())
```

A fresh UUID every render means SwiftUI treats the view as newly created every time — breaks animations, resets scroll position, discards focus, thrashes identity diffing.

**Fix:** Use a stable identifier (the model's ID, a version counter), or trigger re-render via `@State` changes, not identity churn.

### `@State` for shared or model-owned data

```swift
// ANTI — data belongs in a model, not a view
@State private var user: User = User.load()
```

`@State` is view-local. Sharing it through bindings across subtrees produces stale reads and race conditions. On iOS 17+, use `@Observable`.

```swift
// CORRECT
@Observable
final class UserStore {
    var user: User
    init() { self.user = User.load() }
}

// In view
@Environment(UserStore.self) private var userStore
```

Always annotate `@Observable` view models with `@MainActor` to satisfy Swift 6 concurrency.

### `.sheet(isPresented:)` for model-backed data

```swift
// ANTI — stale data if user opens sheet twice
@State var showSheet = false
@State var selected: Item?

Button("Open") { selected = item; showSheet = true }
.sheet(isPresented: $showSheet) {
    DetailView(item: selected!)  // stale if user taps another item
}
```

**Fix:** Use `.sheet(item:)` — the sheet tracks the identity of the item, not a boolean.

```swift
.sheet(item: $selected) { item in
    DetailView(item: item)
}
```

## Navigation

### `NavigationView` (deprecated)

```swift
// ANTI — deprecated since iOS 16
NavigationView { ... }
```

**Fix:** `NavigationStack` for single-column, `NavigationSplitView` for iPad. `NavigationView` has broken back-stack behavior on iOS 16+ and was removed from the sample code in WWDC25.

### `NavigationLink(destination:)` inline destinations

```swift
// ANTI — the destination is instantiated for every row, even offscreen
List(items) { item in
    NavigationLink(destination: DetailView(item: item)) {
        ItemRow(item: item)
    }
}
```

**Fix:** Value-based navigation with `navigationDestination`:

```swift
NavigationStack {
    List(items) { item in
        NavigationLink(value: item) { ItemRow(item: item) }
    }
    .navigationDestination(for: Item.self) { item in
        DetailView(item: item)
    }
}
```

Destinations resolve lazily, enable programmatic navigation via `NavigationPath`, and survive state restoration.

### Custom back buttons that break swipe-to-go-back

```swift
// ANTI — hiding the back button breaks the swipe-from-left-edge gesture
.navigationBarBackButtonHidden(true)
.toolbar { ToolbarItem(placement: .navigationBarLeading) {
    Button("Back") { dismiss() }
}}
```

Hiding the back button removes the swipe gesture with it — users who expect iOS navigation lose a primary gesture.

**Fix:** Keep the system back button. If you need custom text, use `navigationTitle` on the *previous* screen to control what the back button reads. If you genuinely need a custom back handler (confirmation before leaving), intercept via `onDisappear` or `interactiveDismissDisabled` + custom button that explicitly calls `dismiss()`.

### Mixing sheets into `NavigationStack` as if they were destinations

Sheets are not part of the navigation stack. They present on top of the nav stack and don't push history.

**Fix:** Manage sheet state separately from `NavigationPath`. Use `.sheet(item:)` on the root; never try to "navigate to a sheet."

### Navigation collapse: hiding tab bars or back-button labels on context

iOS 26 first-party apps shipped patterns where the tab bar collapses on scroll (Health), or the back-button label disappears entirely. Nielsen Norman Group's iOS 26 usability audit ("Liquid Glass Is Cracked, and Usability Suffers in iOS 26," nngroup.com) rated this as causing "major confusion" because users must rescan to find primary navigation.

**Anti-pattern:**
- conditionally hiding the tab bar based on scroll position or content state, with no clear restore affordance
- removing back-button labels in nav stacks where the previous destination's name is ambiguous ("< " alone)
- collapsing primary chrome to maximise content area in apps where users navigate frequently

**Fix:** Keep navigation chrome stable. If you need more content space, use a sheet or full-screen cover for the immersive view rather than disappearing the tab bar. Always preserve back-button labels when the previous screen's title is non-obvious.

### Motion-for-motion's-sake (iOS 26 Liquid Glass over-animation)

Nielsen Norman Group and developer community feedback flagged a pattern where every interactive element gets bubble/jitter/shimmer animations on iOS 26 — tab items bubbling on tap, song titles shimmering during scroll, buttons jerking on press. Documented as "distraction with a side of nausea."

**Anti-pattern:**
- adding `.glassEffect(.regular.interactive())` to every button on a screen
- `.symbolEffect(.bounce)` on every icon transition
- spring-driven `scaleEffect` press states with overshoot on dense lists

**Fix:** Reserve interactive glass and pronounced motion for *primary* actions. For repeated controls (list rows, tab items), use the system default press feedback. Always honour `accessibilityReduceMotion`; for shimmer or bounce effects, the reduced-motion fallback should be a static state, not a slower animation.

## Layout

### Fixed-height rows that clip at large Dynamic Type

```swift
// ANTI
.frame(height: 44)
```

Clips at AX3+. **Fix:** `.frame(minHeight: 44)` — lets the row grow when content grows.

### Hardcoded screen widths / absolute positions

```swift
// ANTI
.frame(width: 390)         // iPhone 13 only
.offset(x: 200, y: 100)    // breaks on SE
```

**Fix:** Use relative layout (`GeometryReader` when absolutely necessary, `ViewThatFits`, size classes). Prefer constraint-like stacks over absolute positioning.

### `ScrollView` without `LazyVStack` for long content

```swift
// ANTI — eager layout of 500 rows
ScrollView { VStack { ForEach(items) { row } } }
```

All children render on appear. FPS drops, memory spikes.

**Fix:** Use `List` for homogeneous rows (free laziness, swipe actions, edit mode), or `LazyVStack` for custom-visual feeds.

### `GeometryReader` as a first choice

`GeometryReader` fills its parent and flattens stack layouts — it often breaks the layout it's trying to measure.

**Fix:** Try `.frame(maxWidth: .infinity)`, `.containerRelativeFrame`, `@ScaledMetric`, and `ViewThatFits` first. Reach for `GeometryReader` only when none of these work — typically for Canvas sizing or precise overlay positioning.

### `AnyView` for conditional content

```swift
// ANTI — erases identity, triggers full subtree rebuilds
var body: some View {
    isLoggedIn ? AnyView(HomeView()) : AnyView(LoginView())
}
```

Type erasure defeats SwiftUI's view diffing. Re-renders descendants unnecessarily.

**Fix:** `@ViewBuilder` + `if`, or `Group`:

```swift
@ViewBuilder var body: some View {
    if isLoggedIn { HomeView() } else { LoginView() }
}
```

## Color and Dark Mode

### Hardcoded `.white` / `.black` / literal RGB

```swift
// ANTI
.foregroundColor(.white)
.background(Color(red: 0.04, green: 0.05, blue: 0.09))
```

Breaks Dark Mode adaptation, Increase Contrast, and reduces accessibility score.

**Fix:** Semantic colors:

```swift
.foregroundStyle(Color(.label))
.background(Color(.systemBackground))
```

For brand colors that must stay constant, define them as Color Assets with separate light/dark values.

### `.black` shadows on dark backgrounds

```swift
// ANTI — invisible on Dark Mode
.shadow(radius: 4)
```

Default shadow color is `.black`, which vanishes on dark backgrounds.

**Fix:** Explicit shadow color with opacity, or drop shadows in favor of material layering:

```swift
.shadow(color: .black.opacity(0.3), radius: 8, y: 2)
```

### `foregroundColor` (deprecated spelling)

`foregroundColor` is soft-deprecated in favor of `foregroundStyle`, which supports gradients, materials, and shape styles. Migrate to `foregroundStyle` across the codebase.

## Animations and Transitions

### Animating `.frame(height:)` directly

```swift
// ANTI — janky because SwiftUI can't predict intermediate heights
.frame(height: isExpanded ? 200 : 50)
.animation(.spring, value: isExpanded)
```

**Fix:** Prefer `containerRelativeFrame`, explicit `.transition(.move(edge: .top))` on children, or structural changes (`DisclosureGroup`, matchedGeometry) over animating height values.

### Implicit `.animation` modifier (deprecated form)

```swift
// ANTI — animates every state change on this view
.animation(.spring)
```

**Fix:** Scoped form:

```swift
.animation(.spring, value: isExpanded)
```

Or use explicit `withAnimation` in the state-changing block:

```swift
withAnimation(.spring) { isExpanded.toggle() }
```

### Spring-bounce presses on primary CTAs without Reduce Motion handling

Scale-bounce animations on buttons feel premium — but under Reduce Motion they need to be suppressed. See [ios-accessibility-patterns.md](ios-accessibility-patterns.md#reduce-motion) for the pattern.

## Controls and Actions

### Every action rendered as a filled button

A screen with six filled buttons has no primary action. iOS UI typically has **one** prominent CTA; secondary actions are `.bordered` or plain text, tertiary are toolbar/menu items.

**Fix:** One primary per screen. Relegate alternates to a `Menu`, `.toolbar`, or secondary row.

### Custom chrome replacing standard controls

If you built a custom segmented picker, custom sheet, custom tab bar, ask:

- Does it do anything the system control doesn't?
- Can you afford to re-implement accessibility, Dynamic Type, Dark Mode, VoiceOver, Increase Contrast, Reduce Transparency, RTL, keyboard focus, haptics?

Usually not. **Fix:** Use the system control; style through `.tint()`, `.controlSize()`, `.buttonStyle()` rather than reinventing.

### Turning everything into a gesture

Swipe-to-archive, long-press-to-edit, pinch-to-zoom, drag-to-rearrange — all valuable, all need a non-gesture equivalent exposed through `.accessibilityAction` or a visible button. Gesture-only UI fails keyboard users, VoiceOver users, and Voice Control users.

## Sheets and Modals

### `.sheet` with hardcoded heights

```swift
// ANTI — no detents, no drag handle, no accessibility handle
.sheet(isPresented: $show) {
    DetailView().frame(height: 400)
}
```

**Fix:** Use `.presentationDetents([.medium, .large])` and `.presentationDragIndicator(.visible)` — the sheet responds to Dynamic Type, orientation, and system gestures properly.

### `fullScreenCover` for anything not immersive

Full-screen covers remove the user's sense of context and the swipe-to-dismiss gesture. Reserve for truly immersive flows (photo viewer, video player, onboarding) — not forms, detail views, or confirmations.

### Dismissing sheets by tapping the background when there's unsaved work

The default behavior is `.interactiveDismissDisabled(false)` — any tap outside dismisses. On forms with unsaved work, protect with `.interactiveDismissDisabled(hasUnsavedChanges)` and surface the user's options via a confirmation sheet.

## Data Display

### Label-value rows with fixed-width labels

```swift
// ANTI — "Sun" is 3 chars in English, 6 in French, RTL in Arabic
HStack {
    Text("Sun").frame(width: 84)
    Spacer()
    Text(value)
}
```

**Fix:** `LabeledContent` (native, adaptive), vertical stack with label above value, or grid cells with flexible widths.

### `Text("\(intValue)")` for years, IDs, and quantities that shouldn't be locale-formatted

```swift
// ANTI — renders as "2,026" in en_US, "2 026" in fr_FR
Text("\(year)")
```

**Fix:** `Text(verbatim: "\(year)")` or `Text(year.formatted(.number.grouping(.never)))`. For navigation titles and string concatenation (no `verbatim:` overload), use `String(year)`.

### `Text("X/5")` next to a bar as a rating

Looks like a loading bar, not a rating. **Fix:** Use SF Symbols (`star.fill`), energy/score rings, or small filled/outline pips. Reserve `ProgressView` for actual progress.

## Identity, Previews, and Tooling

### Previews that require full dependency injection

Previews that crash because they can't build a model tree are untested. Provide preview mocks for every `@Observable` model:

```swift
#Preview {
    ContentView()
        .environment(UserStore.preview)   // static stub
}
```

### `@Published` on `ObservableObject` when you could use `@Observable`

On iOS 17+, `@Observable` is the canonical pattern. It tracks dependencies per-property (not whole-object), which means fewer re-renders. Migrate unless you have a specific reason to stay on `ObservableObject`.

## Verification

Run this grep before any design handoff to catch the most common smells:

```bash
rg -n '\.frame\(height: [0-9]+\)|NavigationView\s*\{|\.id\(UUID\(\)\)|AnyView\(|foregroundColor\(|\.sheet\(isPresented.*@State' app/
```

None of these are definitive bugs, but every match deserves a second look.

## Canvas, Runtime, and Workflow Anti-Patterns

- Do not audit or redesign from screenshots that have not been tied to a fresh install and launch.
- Do not invent custom chrome before checking whether standard iOS structure already solves the hierarchy problem.
- Do not apply Liquid Glass to content cards — it belongs to the navigation/control layer. See [ios26-liquid-glass.md](ios26-liquid-glass.md).
- Do not treat dashboard heuristics (card count, density) as Apple rules.
- Do not let visual data float unbounded inside cards when a grid, row, divider, or symbol anchor would improve scanability.
- Do not feed raw `xcodebuild` output to agents — pipe through `xcbeautify`.
- Do not use `AnyView` for optional views in `@ViewBuilder` — causes compiler crashes and defeats view diffing. Use inline `if let` or `Group`.
- Do not start Canvas `animatedProgress` at 0 for data-driven views — data may load after `.onAppear`, leaving the Canvas empty. Start at 1 or trigger animation on data change.
- Do not use `Text("\(intValue)")` for years or IDs — SwiftUI applies locale number formatting (2,026 instead of 2026). Use `Text(verbatim: "\(value)")` or `String(year)` for `.navigationTitle` concatenation.
- Do not use `.contentTransition(.numericText)` inside `if let` blocks — causes Swift compiler crashes ("failed to produce diagnostic").
- Do not overlay custom controls on a full-bleed Canvas visualization — markers, labels, and glyphs clip behind the overlay. Place controls in the `VStack` layout below the Canvas, not as `.overlay(alignment: .bottom)` on it.
- Do not use `GeometryReader` for a square Canvas without `.aspectRatio(1, contentMode: .fit)` on the outer view — the Canvas uses `min(width, height)` for sizing but renders centered, leaving dead space.
- Do not build a separate visualization for export — use `ImageRenderer` with a dedicated static export view (no gestures, no parallax, no sheets) that renders the same data.
- Do not use `.buttonStyle(.plain)` on tappable cards, indicators, or interactive elements without visual press feedback. Use a custom `ButtonStyle` with `scaleEffect` on press.
- Do not use `.clipShape(Capsule())` on grid cells or stat pills that stretch to fill column width — capsules pinch at wide aspect ratios. Use `RoundedRectangle(cornerRadius:style:.continuous)`.
- Do not use `.lineLimit(1)` in detail sheets — detail content must wrap fully. Reserve `.lineLimit` for list-level summary rows where truncation signals "tap for more."
- Do not hardcode `.white.opacity()` / `.black.opacity()` in Canvas without considering environment. Pass `@Environment(\.colorScheme)` to Canvas, or use semantic palette tokens.
- Do not skip haptic feedback (`.sensoryFeedback`) on interactive elements — editorial richness without tactile micro-interactions feels dead.
- Do not let one unexpected null from a backend API fail the entire screen decode. Use a custom `init(from decoder:)` that wraps non-critical fields in `try?` with sensible defaults.
- Do not call `withAnimation` directly inside a `@MainActor`-annotated method on iOS 26 / Swift 6.2 without verifying the animation actually plays. Root cause: Swift 6.2's *default actor isolation* feature (which infers `@MainActor` for module code in new Xcode projects) changes `withAnimation` scheduling in deferred execution contexts; calls inside `didSet`/`onAppear` that run before the first layout pass may silently no-op. Workaround: hoist `withAnimation` to a `Task { @MainActor in … }` or move it out of the pre-layout callback. The trap applies only to Swift 6.2 projects with default actor isolation enabled — Swift 5.x projects are unaffected, so don't apply the workaround everywhere.
- Do not reach for `AnyView` to handle conditional content — type erasure defeats SwiftUI's diffing and triggers full subtree rebuilds. Use `@ViewBuilder` or `Group` with `if` / `switch`.
