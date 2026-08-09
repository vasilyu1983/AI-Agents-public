# SwiftUI Deprecated API Reference

Systematic mapping of deprecated or outdated SwiftUI and Swift patterns to their modern replacements. Target: iOS 17+ with Swift 6.2.

Primary docs:

- https://developer.apple.com/documentation/swiftui
- https://developer.apple.com/xcode/swiftui/

## Table of Contents

- [View Modifiers](#view-modifiers)
- [Navigation](#navigation)
- [State and Data Flow](#state-and-data-flow)
- [Controls and Input](#controls-and-input)
- [Layout and Geometry](#layout-and-geometry)
- [Animation](#animation)
- [Accessibility](#accessibility)
- [Images and Resources](#images-and-resources)
- [Haptics and Feedback](#haptics-and-feedback)
- [Text and Localization](#text-and-localization)
- [Preview and Development](#preview-and-development)
- [Environment and Keys](#environment-and-keys)
- [Combine and Observation](#combine-and-observation)

## View Modifiers

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `.foregroundColor(_:)` | `.foregroundStyle(_:)` | Accepts `ShapeStyle`, not just `Color` |
| `.cornerRadius(_:)` | `.clipShape(.rect(cornerRadius:))` | Explicit clip shape is composable |
| `overlay(_:alignment:)` (deprecated overload) | `overlay(alignment:content:)` | ViewBuilder trailing closure |
| `.background(_:alignment:)` (deprecated overload) | `.background(alignment:content:)` | ViewBuilder trailing closure |
| `.navigationBarLeading` | `.topBarLeading` | Consistent with `ToolbarItemPlacement` naming |
| `.navigationBarTrailing` | `.topBarTrailing` | Same |
| `.accentColor(_:)` | `.tint(_:)` | Tint applies to more control types |
| `fontWeight(.bold)` | `.bold()` | Dedicated modifier, clearer intent |

## Navigation

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `NavigationView` | `NavigationStack` / `NavigationSplitView` | Stack for push/pop, SplitView for multi-column |
| `NavigationLink(destination:)` | `NavigationLink(value:)` + `navigationDestination(for:)` | Type-safe, data-driven |
| `.tabItem()` modifier | `Tab` API (iOS 18+) | Enum-based `TabView(selection:)` with `Tab` |
| `sheet(isPresented:)` for optionals | `sheet(item:)` | Clearer ownership when presenting from optional state |

Rules:

- Never mix `NavigationLink(destination:)` with `navigationDestination(for:)` in the same navigation stack — they use different resolution paths and produce undefined behavior.
- Register `navigationDestination(for:)` once per data type, not per view.
- Attach `confirmationDialog()` to the triggering UI element for correct Liquid Glass animations.
- Single-OK alerts can omit the button — the system provides a default dismiss.
- Prefer `sheet(item: $someItem, content: SomeView.init)` for concise sheet wiring.

## State and Data Flow

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `ObservableObject` + `@Published` | `@Observable` class | iOS 17+; no publisher overhead |
| `@StateObject` | `@State` (with `@Observable` type) | Lifecycle ownership is the same |
| `@ObservedObject` | Direct reference or `@Bindable` | Bindable for two-way binding |
| `@EnvironmentObject` | `@Environment` with custom `@Entry` | Type-safe environment injection |
| `onChange(of:perform:)` (1-param) | `onChange(of:) { oldValue, newValue in }` | Two-parameter closure variant |

Rules:

- `@State` should be `private` — non-private `@State` is almost always a design mistake.
- Never use `@AppStorage` inside an `@Observable` class — AppStorage does not trigger Observable updates and produces stale reads.
- Avoid `Binding(get:set:)` in `body` — use `onChange(of:)` instead to avoid re-evaluation on every render.
- Prefer `Identifiable` conformance on model types over `id: \.someProperty` in `ForEach`.

## Controls and Input

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `TextEditor` | `TextField(axis: .vertical)` | Native multiline text with built-in behavior |
| `UIKit haptics` (`UIImpactFeedbackGenerator`) | `.sensoryFeedback(_:trigger:)` | SwiftUI-native, declarative |
| Manual text button actions | `Button("Label", systemImage: "plus", action: myAction)` | Direct action parameter |
| `onTapGesture { action() }` | `Button` | Buttons provide built-in accessibility; only use `onTapGesture` when you need tap count or location, and add `.accessibilityAddTraits(.isButton)` |

## Layout and Geometry

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `GeometryReader` for simple relative sizing | `containerRelativeFrame()` | Cleaner, no GeometryReader noise |
| `GeometryReader` for scroll effects | `.visualEffect { content, proxy in }` | Direct access to geometry proxy |
| `GeometryReader` for complex layout | `Layout` protocol | Custom layout without GeometryReader overhead |
| `UIScreen.main.bounds` | `GeometryReader` or `containerRelativeFrame()` | Screen bounds is fragile (split view, Slide Over) |
| Fixed `.frame(width:height:)` | Intrinsic sizing + `.frame(minWidth:maxWidth:)` | Adapts to Dynamic Type and device classes |

## Animation

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `animation(_ animation: Animation?)` (no value) | `.animation(_:value:)` | Must bind to a state value to avoid implicit animation issues |
| Manual `animatableData` | `@Animatable` macro | Reduces boilerplate (Swift 6.2+) |
| `PreviewProvider` | `#Preview` macro | Lighter syntax, faster iteration |
| `UIGraphicsImageRenderer` | `ImageRenderer` | SwiftUI-native rendering |
| `withAnimation` completion (pre-iOS 17) | `withAnimation(.spring) { … } completion: { … }` | Chained completion closures |

## Accessibility

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| Hard-coded font sizes | `.font(.body)`, `.font(.headline)`, etc. | Respects Dynamic Type |
| Custom sizing for Dynamic Type | `@ScaledMetric` or `.font(.body.scaled(by:))` (iOS 26+) | Auto-scales with text size preference |
| Unclear VoiceOver on images | `Image(decorative:)` or `.accessibilityHidden(true)` | Decorative images should not announce |
| `Image(systemName:)` as button label | `Button("Label", systemImage: "plus", action: act)` | Always include text for VoiceOver |
| Ignoring Reduce Motion | Respect `.accessibilityReduceMotion` | Suppress animations when enabled |
| Ignoring differentiate without color | Respect `.accessibilityDifferentiateWithoutColor` | Add icons or shapes alongside color-only indicators |

## HIG-Aligned SwiftUI Alternatives

Prefer these Apple-native SwiftUI components over building custom equivalents:

| Custom Pattern | Native Alternative | Notes |
|---|---|---|
| Custom empty-state view | `ContentUnavailableView` | System-styled empty states with icon, title, description |
| Custom search-empty view | `ContentUnavailableView.search` | Auto-includes the current search term |
| `HStack { Image(); Text() }` for icon+text | `Label("Title", systemImage: "star")` | Correct semantics, adaptive layout, accessibility |
| Manual opacity for secondary text | System hierarchical styles (`.secondary`, `.tertiary`, `.quaternary`) | Automatic dark/light adaptation |
| `HStack { Text("Label"); Spacer(); Text("Value") }` in Form | `LabeledContent("Label", value: "Value")` | Correct Form alignment and semantics |
| Hard-coded corner radius | `RoundedRectangle(cornerRadius:)` | Defaults to `.continuous` style (matches Apple controls) |
| `.fontWeight(.bold)` | `.bold()` | Dedicated modifier, clearer intent |
| `UIColor.systemBlue` etc. | SwiftUI `Color` semantic colors | `UIColor` is UIKit; use `Color.accentColor`, `Color.primary`, etc. |
| `.font(.system(size: 9))` | Avoid `.caption2` or smaller | Too small for readability; minimum `.caption` for secondary text |
| Fixed `.padding(16)` | System-adaptive `.padding()` or named tokens | Avoid hard-coded spacing values |
| `UIScreen.main.bounds` | `GeometryReader` or `containerRelativeFrame()` | Screen bounds is fragile under Slide Over, Split View, Stage Manager |
| Fixed `.frame(width:height:)` | Intrinsic sizing + min/max constraints | Adapt to Dynamic Type and varying device widths |
| Custom touch target sizing | Minimum 44x44pt on all interactive elements | Apple accessibility requirement; check with `.frame(minHeight: 44)` |

## Images and Resources

| Deprecated | Modern Replacement | Notes |
|---|---|---|
| `Image("name")` for asset catalog | `Image(.name)` | Generated symbol asset (type-safe) |
| Manual fill+stroke overlays | Shape chaining: `.fill(.red).stroke(.blue, lineWidth: 2)` | No overlay needed |

## Haptics and Feedback

Use `.sensoryFeedback(_:trigger:)` for all haptic feedback in SwiftUI. The canonical pattern for tappable containers:

```swift
@State private var tapCount: Int = 0

Button {
    tapCount &+= 1  // overflow-safe wrap-around
    action()
} label: {
    // ...
}
.sensoryFeedback(.selection, trigger: tapCount)
```

## Text and Localization

| Pattern to Avoid | Modern Alternative | Notes |
|---|---|---|
| `Text(number) + Text(string)` concatenation | `Text("\(number) \(string)")` interpolation | `+` concatenation is fragile and defeats localization |
| Missing `import Combine` with `ObservableObject` | Add `import Combine` | Required if you still use `ObservableObject` |
| `scrollIndicators()` missing | `.scrollIndicators(.hidden)` | Explicit control over scroll indicator visibility |
| `Text(verbatim:)` missing for IDs/years | `Text(verbatim: "\(year)")` | Suppress locale number formatting (2026 not 2,026) |
| Automatic grammar disagreement | Use automatic grammar agreement API | Localizable strings adapt to count/gender |

## Preview and Development

| Deprecated | Modern | Notes |
|---|---|---|
| `PreviewProvider` struct | `#Preview { }` macro | Less boilerplate |
| Manual preview data | `#Preview` with inline state | Direct `@Previewable @State` |

## Environment and Keys

| Old Pattern | Modern | Notes |
|---|---|---|
| `EnvironmentKey` protocol conformance | `@Entry` macro | Reduces boilerplate for custom environment keys |
| `EnvironmentValues` extension | `@Entry` declaration | One-line environment value definition |

## Combine and Observation

| Old | Modern | Notes |
|---|---|---|
| `ObservableObject` | `@Observable` | iOS 17+; no `objectWillChange` publisher |
| `@Published` | Direct property on `@Observable` class | Mutation tracking is automatic |
| `sink` / `assign` subscriptions | Direct property access in views | No Combine subscription lifecycle to manage |
| `.onReceive(publisher)` for Combine | `onChange(of:)` for Observable state | Only use Combine when working with actual Combine publishers |

### iOS 26+ Only

- `WebView` — native SwiftUI web view, replaces `WKWebView` via `UIViewRepresentable`
- `ForEach` with `enumerated()` directly — no wrapper needed
- `.font(.body.scaled(by:))` — replaces `@ScaledMetric` for proportional scaling
