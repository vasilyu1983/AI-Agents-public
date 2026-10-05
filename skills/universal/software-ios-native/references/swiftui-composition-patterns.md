# SwiftUI Composition Patterns

Reusable view styling, child-to-parent data flow, and small DSL tools. Moved from the retired software-mobile SwiftUI template. Its Combine sections were dropped: `@Observable` is the default, and migration is covered in [swift-concurrency-patterns.md](swift-concurrency-patterns.md#combine-to-asyncsequence-migration). Its conditional-modifier helper was dropped too, for the reason given below.

## Contents

- [Custom ViewModifiers](#custom-viewmodifiers)
- [PreferenceKey for Child-to-Parent Data](#preferencekey-for-child-to-parent-data)
- [Custom Property Wrappers](#custom-property-wrappers)
- [Result Builders](#result-builders)

## Custom ViewModifiers

Extract a `ViewModifier` when the same styling or behavior repeats across screens. Expose it through a `View` extension so call sites read like built-in modifiers.

```swift
struct CardStyle: ViewModifier {
    var cornerRadius: CGFloat = 12
    func body(content: Content) -> some View {
        content
            .padding()
            .background(.background, in: .rect(cornerRadius: cornerRadius))
            .shadow(color: .black.opacity(0.1), radius: 4, y: 2)
    }
}

extension View {
    func cardStyle(cornerRadius: CGFloat = 12) -> some View {
        modifier(CardStyle(cornerRadius: cornerRadius))
    }
}
```

- Use semantic colors and design tokens, not literals such as `.white`. Literals break dark mode. Design-token choice is owned by [software-ios-design](../../software-ios-design/SKILL.md).
- A modifier that needs state or the environment can declare `@State` or `@Environment` inside the `ViewModifier` struct.
- **Do not add a generic `.if(condition) { $0.modifier() }` helper.** It branches the view tree, so toggling the condition changes view identity. That resets `@State`, breaks animations and forces a rebuild. Toggle the modifier's argument instead (ternary, opacity, `nil` value). See [swiftui-performance.md](swiftui-performance.md#ternary-over-ifelse-for-modifier-toggling).

## PreferenceKey for Child-to-Parent Data

Use a `PreferenceKey` when a parent needs a value that its children produce, such as measured sizes, anchor bounds, or a selected item's frame.

```swift
struct MaxWidthKey: PreferenceKey {
    static let defaultValue: CGFloat = 0
    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = max(value, nextValue())   // combine siblings; do not just keep the last one
    }
}

// Children report their width; the parent aligns every label to the widest one.
Text(label)
    .background(GeometryReader { Color.clear.preference(key: MaxWidthKey.self, value: $0.size.width) })
// Parent:
.onPreferenceChange(MaxWidthKey.self) { labelWidth = $0 }
```

- Write `reduce` for many children. A last-writer-wins `reduce` silently drops sibling values.
- Guard against layout feedback loops. If the parent's reaction changes the child's measured size, the preference changes again and the view re-renders forever. Round the values, or compare before you assign.
- Measurement through `GeometryReader` is greedy and expensive. Before you reach for it, check `containerRelativeFrame`, `ViewThatFits`, the `Layout` protocol, and the geometry- and scroll-change callbacks available at your deployment target (check the SwiftUI documentation for their availability). See [swiftui-performance.md](swiftui-performance.md#geometryreader-is-greedy) and [swiftui-deprecated-api.md](swiftui-deprecated-api.md).
- Scroll-offset tracking through a PreferenceKey fires on every frame. Throttle what the handler does, or use the scroll-geometry APIs where your target allows them.

## Custom Property Wrappers

Property wrappers suit value policies on plain model types:

```swift
@propertyWrapper
struct Clamped<Value: Comparable> {
    private var value: Value
    private let range: ClosedRange<Value>
    var wrappedValue: Value {
        get { value }
        set { value = min(max(range.lowerBound, newValue), range.upperBound) }
    }
    init(wrappedValue: Value, _ range: ClosedRange<Value>) {
        self.range = range
        self.value = min(max(range.lowerBound, wrappedValue), range.upperBound)
    }
}

struct Volume { @Clamped(0...100) var level = 50 }
```

- A plain property wrapper on a `View` struct does not trigger updates, cannot be mutated from `body`, and has no `$binding`. For view state, use `@State`, `@Binding`, `@Environment` or `@AppStorage`. To build your own view-aware wrapper, conform it to `DynamicProperty` and back it with `@State`.
- Prefer `@AppStorage` over a hand-rolled `@UserDefault` wrapper inside views. Keep secrets out of both; they belong in the Keychain.

## Result Builders

Use `@resultBuilder` for a small internal DSL, such as request builders, attributed-text assembly, or validation rule lists, when call sites would otherwise build arrays with `if` branches. Implement `buildBlock`, plus `buildOptional` / `buildEither` for `if` / `else` and `buildArray` for `for` loops. Keep builders narrow; a builder nobody else on the team can read costs more than the arrays it replaced. For views, `@ViewBuilder` already covers this; see [swiftui-performance.md](swiftui-performance.md#viewbuilder-closures).
