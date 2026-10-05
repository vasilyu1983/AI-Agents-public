# SwiftUI Performance Patterns

Actionable patterns for keeping SwiftUI views fast. Focus on avoiding unnecessary re-evaluations, reducing diff complexity, and keeping the render pipeline lean.

Primary docs:

- https://developer.apple.com/documentation/swiftui/performance
- https://developer.apple.com/videos/play/wwdc2023/10160/

## Table of Contents

- [View Splitting](#view-splitting)
- [Modifier Efficiency](#modifier-efficiency)
- [List and Scroll Performance](#list-and-scroll-performance)
- [Initializer Discipline](#initializer-discipline)
- [Async Work](#async-work)
- [Formatting](#formatting)
- [ViewBuilder Closures](#viewbuilder-closures)
- [Type Erasure](#type-erasure)
- [Identity and Diffing](#identity-and-diffing)
- [Quick Checklist](#quick-checklist)

## View Splitting

The single most impactful SwiftUI performance pattern: **break large views into separate View structs**.

- Extract subviews into their own `struct: View` types — not computed properties, not methods
- Each extracted view gets its own identity in the SwiftUI diff, so changes to one subview don't re-evaluate siblings
- Computed properties and methods returning `some View` are inlined into the parent body — they do not create separate diff nodes

```swift
// WRONG — everything re-evaluates together
struct ProfileView: View {
    @State var user: User
    @State var posts: [Post]

    var body: some View {
        VStack {
            // Header and posts re-evaluate together
            Text(user.name).font(.title)
            Image(user.avatar)
            ForEach(posts) { post in
                PostRow(post: post)
            }
        }
    }
}

// BETTER — separate diff nodes
struct ProfileView: View {
    @State var user: User
    @State var posts: [Post]

    var body: some View {
        VStack {
            ProfileHeader(user: user)
            PostList(posts: posts)
        }
    }
}
```

Flag any `body` property longer than ~30 lines as a candidate for extraction.

### One Type Per File

Keep each struct, class, or enum in its own Swift file. Multiple types in one file make navigation harder and defeat incremental compilation benefits.

### File Ordering Convention

Within a SwiftUI View struct, maintain a predictable property ordering:

```swift
struct ProfileView: View {
    // 1. Environment values
    @Environment(\.dismiss) private var dismiss

    // 2. Let constants (injected dependencies)
    let user: User

    // 3. @State properties
    @State private var isEditing = false
    @State private var editedName = ""

    // 4. Computed properties
    var displayName: String { isEditing ? editedName : user.name }

    // 5. Initializer (if custom)
    init(user: User) { self.user = user }

    // 6. body
    var body: some View { ... }

    // 7. @ViewBuilder helper methods
    @ViewBuilder
    private func headerSection() -> some View { ... }

    // 8. Non-view helper methods
    private func save() { ... }
}
```

### Common Smells

- View `body` exceeding 30 lines without extracted subviews
- Computed properties returning `some View` instead of separate View structs
- Business logic mixed into `body` or action closures
- Multiple types defined in a single file
- Button actions containing more than 2-3 lines of logic (extract to methods)
- Toolbar or command group content inlined in `body` instead of extracted

## Modifier Efficiency

### Ternary over if/else for modifier toggling

Using `if/else` in a `@ViewBuilder` creates `_ConditionalContent` — two separate view trees. SwiftUI must tear down one and create the other, losing animations and state.

```swift
// WRONG — creates _ConditionalContent, breaks animation
if isHighlighted {
    Text(label).foregroundStyle(.red)
} else {
    Text(label).foregroundStyle(.primary)
}

// CORRECT — same view identity, modifier changes smoothly
Text(label)
    .foregroundStyle(isHighlighted ? .red : .primary)
```

### Opaque scroll backgrounds

When a scrollable view sits on a custom background, the system draws its own translucent background on top:

```swift
List { ... }
    .scrollContentBackground(.visible)  // Keeps the system background visible
    // or
    .scrollContentBackground(.hidden)   // Hides it for full custom control
```

## List and Scroll Performance

- Use `LazyVStack` and `LazyHStack` for large or dynamic data — they only instantiate visible rows
- Avoid `VStack` and `HStack` inside `ScrollView` for more than ~20-30 items
- Avoid expensive inline transforms (sorting, filtering, mapping) inside `ForEach` — compute them before the view body
- Prefer `ForEach(items)` with `Identifiable` conformance over `ForEach(items, id: \.someProperty)`

```swift
// WRONG — sorts on every evaluation
ForEach(items.sorted(by: { $0.date > $1.date })) { item in
    ItemRow(item: item)
}

// CORRECT — sort once
let sortedItems = items.sorted(by: { $0.date > $1.date })
// in body:
ForEach(sortedItems) { item in
    ItemRow(item: item)
}
```

## Initializer Discipline

Keep view initializers trivial. Move any real work to `task()`:

```swift
// WRONG — work in init runs on every state change
struct DataView: View {
    let processedData: [Item]

    init(rawData: [RawItem]) {
        processedData = rawData.map { Item(from: $0) }  // Runs every re-init
    }
}

// CORRECT — defer work to task
struct DataView: View {
    let rawData: [RawItem]
    @State private var processedData: [Item] = []

    var body: some View {
        List(processedData) { ItemRow(item: $0) }
            .task { processedData = rawData.map { Item(from: $0) } }
    }
}
```

## Async Work

- Prefer `.task { }` over `.onAppear { }` for async work — `task` provides automatic cancellation when the view disappears
- `.task(id:)` re-runs when the id changes, replacing the previous task

```swift
// WRONG — no automatic cancellation
.onAppear {
    Task { data = try await fetch() }
}

// CORRECT — cancelled automatically on disappear
.task {
    data = try await fetch()
}

// CORRECT — re-fetches when userId changes
.task(id: userId) {
    data = try await fetchUser(userId)
}
```

## Formatting

Avoid creating formatters as stored properties — they're expensive to initialize and don't benefit from SwiftUI's text optimizations:

```swift
// WRONG — formatter created per view instance
struct PriceView: View {
    let price: Double
    let formatter: NumberFormatter = {
        let f = NumberFormatter()
        f.numberStyle = .currency
        return f
    }()

    var body: some View {
        Text(formatter.string(from: NSNumber(value: price)) ?? "")
    }
}

// CORRECT — use Text's built-in format
struct PriceView: View {
    let price: Double

    var body: some View {
        Text(price, format: .currency(code: "USD"))
    }
}
```

`Text` with format styles uses SwiftUI's internal caching and localization infrastructure.

## ViewBuilder Closures

Avoid storing escaping `@ViewBuilder` closures as properties — store the built view value instead:

```swift
// PROBLEMATIC — retains the closure and its captures
struct Card<Content: View>: View {
    let content: () -> Content
    init(@ViewBuilder content: @escaping () -> Content) {
        self.content = content
    }
}

// BETTER — store the built view
struct Card<Content: View>: View {
    let content: Content
    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }
}
```

## Type Erasure

Avoid `AnyView` — it defeats SwiftUI's structural diffing and forces full subtree rebuilds:

```swift
// WRONG — AnyView breaks identity
func makeView() -> AnyView {
    if condition {
        AnyView(ViewA())
    } else {
        AnyView(ViewB())
    }
}

// CORRECT — @ViewBuilder preserves identity
@ViewBuilder
func makeView() -> some View {
    if condition {
        ViewA()
    } else {
        ViewB()
    }
}
```

`AnyView` also accumulates orphaned subscriptions and degrades type-based view identity.

## Identity and Diffing

- `.id(UUID())` as a force-refresh mechanism is an anti-pattern — it forces complete view re-initialization and keeps old view instances alive through retained subscriptions
- Drive refreshes from state changes, not identity changes
- Use stable identifiers for `ForEach` items — changing identifiers causes teardown/rebuild

```swift
// WRONG — new identity every render
Text("Hello").id(UUID())

// CORRECT — identity tied to meaningful state
Text("Hello").id(refreshToken)
```

## SwiftUI Traps and Edge Cases

### @State initialization from parent is ignored on re-render

`@State` initializes once per view lifetime. If a parent passes a new value and the child uses it in `@State` init, the state retains the original value:

```swift
// TRAP — @State keeps the first value forever
struct ChildView: View {
    @State private var text: String

    init(initialText: String) {
        _text = State(initialValue: initialText)  // Only runs on first init
    }
}

// FIX — use onChange to sync, or use @Binding / plain let
struct ChildView: View {
    let externalText: String
    @State private var editedText: String = ""

    var body: some View {
        TextField("Edit", text: $editedText)
            .onChange(of: externalText) { _, new in editedText = new }
    }
}
```

### sheet(item:) captures stale state

The sheet closure captures `item` at presentation time. If the underlying model changes while the sheet is open, the sheet sees stale data. Pass a `Binding` or use `@Environment` for live data inside sheets.

### @Environment(\.dismiss) behavior depends on context

- Inside a `NavigationStack` pushed view: `dismiss()` pops the view
- Inside a `.sheet`: `dismiss()` dismisses the sheet
- Inside a deeply nested child with multiple containers: behavior is ambiguous

Always verify dismiss behavior in the specific navigation/presentation context.

### GeometryReader is greedy

`GeometryReader` expands to fill all available space and pushes siblings out of layout. Always prefer `containerRelativeFrame()`, `visualEffect`, or `Layout` protocol before reaching for `GeometryReader`.

### Only one alert or confirmationDialog active per view

Multiple `.alert()` modifiers on the same view — only the first to activate shows; the second is silently dropped. Attach alerts to different child views or use a single `.alert` with switching logic.

### @FocusState can reset on view re-evaluation

`@FocusState` may lose keyboard focus when the view body re-evaluates (e.g., an error message appears, changing the view structure). Keep the view structure stable around focused fields.

### onChange(of:) initial parameter

The two-parameter `onChange(of:) { old, new in }` has an `initial:` parameter (default `false`). Set `initial: true` if you need the handler to fire immediately with the current value.

## Quick Checklist

Before shipping a SwiftUI screen:

- [ ] No `body` longer than ~30 lines without extracted subviews
- [ ] No `if/else` toggling modifiers that could be a ternary
- [ ] No expensive computation inside `ForEach` or `List` closures
- [ ] No formatter properties — using `Text` format styles instead
- [ ] No `AnyView` — using `@ViewBuilder` or `Group`
- [ ] No `.id(UUID())` for refresh — using state-driven updates
- [ ] Using `LazyVStack`/`LazyHStack` for lists > 20 items
- [ ] Using `.task { }` instead of `.onAppear { Task { } }`
- [ ] View initializers are trivial — work deferred to `.task`
