# SwiftUI Advanced Patterns Reference

Comprehensive guide to advanced SwiftUI patterns including custom ViewModifiers, PreferenceKey, GeometryReader, and Combine integration for building sophisticated iOS user interfaces.

---

## Table of Contents

1. [Custom ViewModifiers](#custom-viewmodifiers)
2. [PreferenceKey for Data Flow](#preferencekey-for-data-flow)
3. [GeometryReader for Adaptive Layouts](#geometryreader-for-adaptive-layouts)
4. [Combine Integration](#combine-integration)
5. [Swift 6.0+ Features](#swift-60-features)

---

## Custom ViewModifiers

**Use when:** Creating reusable view styling and behavior.

### Custom ViewModifier

```swift
struct CardModifier: ViewModifier {
    var backgroundColor: Color = .white
    var cornerRadius: CGFloat = 12
    var shadowRadius: CGFloat = 4

    func body(content: Content) -> some View {
        content
            .padding()
            .background(backgroundColor)
            .cornerRadius(cornerRadius)
            .shadow(color: .black.opacity(0.1), radius: shadowRadius, x: 0, y: 2)
    }
}

extension View {
    func cardStyle(
        backgroundColor: Color = .white,
        cornerRadius: CGFloat = 12,
        shadowRadius: CGFloat = 4
    ) -> some View {
        modifier(CardModifier(
            backgroundColor: backgroundColor,
            cornerRadius: cornerRadius,
            shadowRadius: shadowRadius
        ))
    }
}

// Usage
Text("Hello, World!")
    .cardStyle()

VStack {
    Text("Custom Card")
}
.cardStyle(backgroundColor: .blue.opacity(0.1), cornerRadius: 16)
```

### Conditional Modifier

```swift
extension View {
    @ViewBuilder
    func `if`<Transform: View>(
        _ condition: Bool,
        transform: (Self) -> Transform
    ) -> some View {
        if condition {
            transform(self)
        } else {
            self
        }
    }
}

// Usage
Text("Conditional Styling")
    .if(isHighlighted) { view in
        view
            .foregroundColor(.red)
            .bold()
    }
```

**Checklist:**
- [ ] Extract repeated styling into ViewModifiers
- [ ] Use extensions for convenience
- [ ] Keep modifiers composable
- [ ] Use @ViewBuilder for conditional logic
- [ ] Document modifier parameters

---

## PreferenceKey for Data Flow

**Use when:** Passing data from child views up to parent views.

### PreferenceKey for View Sizes

```swift
struct SizePreferenceKey: PreferenceKey {
    static var defaultValue: CGSize = .zero

    static func reduce(value: inout CGSize, nextValue: () -> CGSize) {
        value = nextValue()
    }
}

extension View {
    func readSize(onChange: @escaping (CGSize) -> Void) -> some View {
        background(
            GeometryReader { geometry in
                Color.clear
                    .preference(key: SizePreferenceKey.self, value: geometry.size)
            }
        )
        .onPreferenceChange(SizePreferenceKey.self, perform: onChange)
    }
}

// Usage
struct AdaptiveView: View {
    @State private var contentSize: CGSize = .zero

    var body: some View {
        VStack {
            Text("Dynamic Content")
                .readSize { size in
                    contentSize = size
                }

            Text("Size: \(contentSize.width) x \(contentSize.height)")
        }
    }
}
```

### PreferenceKey for Scroll Offset

```swift
struct ScrollOffsetPreferenceKey: PreferenceKey {
    static var defaultValue: CGFloat = 0

    static func reduce(value: inout CGFloat, nextValue: () -> CGFloat) {
        value = nextValue()
    }
}

struct ScrollOffsetModifier: ViewModifier {
    let coordinateSpace: String
    let onChange: (CGFloat) -> Void

    func body(content: Content) -> some View {
        content
            .background(
                GeometryReader { geometry in
                    Color.clear
                        .preference(
                            key: ScrollOffsetPreferenceKey.self,
                            value: geometry.frame(in: .named(coordinateSpace)).minY
                        )
                }
            )
            .onPreferenceChange(ScrollOffsetPreferenceKey.self, perform: onChange)
    }
}

// Usage
struct ScrollableContentView: View {
    @State private var scrollOffset: CGFloat = 0

    var body: some View {
        ScrollView {
            VStack {
                ForEach(0..<50) { index in
                    Text("Item \(index)")
                        .frame(height: 50)
                }
            }
            .modifier(ScrollOffsetModifier(coordinateSpace: "scroll") { offset in
                scrollOffset = offset
            })
        }
        .coordinateSpace(name: "scroll")
        .overlay(
            Text("Offset: \(scrollOffset)")
                .padding(),
            alignment: .top
        )
    }
}
```

**Checklist:**
- [ ] Use PreferenceKey for upward data flow
- [ ] Implement reduce for multiple values
- [ ] Combine with GeometryReader for measurements
- [ ] Use named coordinate spaces
- [ ] Handle performance for frequent updates

---

## GeometryReader for Adaptive Layouts

**Use when:** Creating adaptive layouts based on available space.

### Responsive Grid

```swift
struct AdaptiveGrid<Content: View>: View {
    let items: [String]
    let minItemWidth: CGFloat
    let spacing: CGFloat
    let content: (String) -> Content

    init(
        items: [String],
        minItemWidth: CGFloat = 150,
        spacing: CGFloat = 16,
        @ViewBuilder content: @escaping (String) -> Content
    ) {
        self.items = items
        self.minItemWidth = minItemWidth
        self.spacing = spacing
        self.content = content
    }

    var body: some View {
        GeometryReader { geometry in
            let columns = max(1, Int(geometry.size.width / (minItemWidth + spacing)))
            let itemWidth = (geometry.size.width - spacing * CGFloat(columns - 1)) / CGFloat(columns)

            ScrollView {
                LazyVGrid(
                    columns: Array(repeating: GridItem(.fixed(itemWidth), spacing: spacing), count: columns),
                    spacing: spacing
                ) {
                    ForEach(items, id: \.self) { item in
                        content(item)
                            .frame(width: itemWidth)
                    }
                }
                .padding(spacing)
            }
        }
    }
}

// Usage
AdaptiveGrid(items: photos, minItemWidth: 150) { photo in
    AsyncImage(url: photo.url) { image in
        image
            .resizable()
            .aspectRatio(contentMode: .fill)
    } placeholder: {
        ProgressView()
    }
    .frame(height: 150)
    .clipped()
    .cornerRadius(8)
}
```

### Aspect Ratio Container

```swift
struct AspectRatioContainer<Content: View>: View {
    let aspectRatio: CGFloat
    let content: Content

    init(aspectRatio: CGFloat, @ViewBuilder content: () -> Content) {
        self.aspectRatio = aspectRatio
        self.content = content()
    }

    var body: some View {
        GeometryReader { geometry in
            content
                .frame(
                    width: geometry.size.width,
                    height: geometry.size.width / aspectRatio
                )
                .clipped()
        }
        .aspectRatio(aspectRatio, contentMode: .fit)
    }
}

// Usage
AspectRatioContainer(aspectRatio: 16/9) {
    VideoPlayerView(url: videoURL)
}
```

**Checklist:**
- [ ] Use GeometryReader for adaptive layouts
- [ ] Avoid overusing (performance cost)
- [ ] Combine with ScrollView for large content
- [ ] Handle orientation changes
- [ ] Test on different screen sizes

---

## Combine Integration

**Use when:** Building reactive data flows and complex state management.

### Combine Publisher in ViewModel

```swift
import Combine

class SearchViewModel: ObservableObject {
    @Published var searchQuery = ""
    @Published var results: [SearchResult] = []
    @Published var isLoading = false

    private var cancellables = Set<AnyCancellable>()

    init() {
        $searchQuery
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .filter { !$0.isEmpty }
            .sink { [weak self] query in
                self?.performSearch(query)
            }
            .store(in: &cancellables)
    }

    private func performSearch(_ query: String) {
        isLoading = true

        APIService.shared.search(query: query)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        print("Search error: \(error)")
                    }
                },
                receiveValue: { [weak self] results in
                    self?.results = results
                }
            )
            .store(in: &cancellables)
    }
}
```

### Custom Publishers

```swift
extension URLSession {
    func dataTaskPublisher(for request: URLRequest) -> AnyPublisher<Data, Error> {
        dataTaskPublisher(for: request)
            .tryMap { data, response in
                guard let httpResponse = response as? HTTPURLResponse,
                      (200...299).contains(httpResponse.statusCode) else {
                    throw URLError(.badServerResponse)
                }
                return data
            }
            .eraseToAnyPublisher()
    }
}

class APIService {
    func getUsers() -> AnyPublisher<[User], Error> {
        let url = URL(string: "https://api.example.com/users")!

        return URLSession.shared.dataTaskPublisher(for: URLRequest(url: url))
            .decode(type: [User].self, decoder: JSONDecoder())
            .eraseToAnyPublisher()
    }
}
```

### Operators Chaining

```swift
class FeedViewModel: ObservableObject {
    @Published var posts: [Post] = []
    @Published var filter: PostFilter = .all

    private var cancellables = Set<AnyCancellable>()

    init() {
        Publishers.CombineLatest(
            postsPublisher,
            $filter
        )
        .map { posts, filter in
            switch filter {
            case .all:
                return posts
            case .starred:
                return posts.filter { $0.isStarred }
            case .recent:
                return posts.filter { $0.createdAt > Date().addingTimeInterval(-86400) }
            }
        }
        .receive(on: DispatchQueue.main)
        .assign(to: \.posts, on: self)
        .store(in: &cancellables)
    }

    private var postsPublisher: AnyPublisher<[Post], Never> {
        Timer.publish(every: 30, on: .main, in: .common)
            .autoconnect()
            .flatMap { _ in
                APIService.shared.getPosts()
                    .catch { _ in Just([]) }
            }
            .eraseToAnyPublisher()
    }
}
```

**Checklist:**
- [ ] Use Combine for reactive data flows
- [ ] Debounce user input
- [ ] Combine multiple publishers
- [ ] Handle cancellables properly
- [ ] Use async/await for new code

---

## Swift 6.0+ Features

### Macros

**@Observable Macro (iOS 18+):**

```swift
import Observation

@Observable
class UserViewModel {
    var user: User?
    var isLoading = false
    var errorMessage: String?

    func loadUser() async {
        isLoading = true
        defer { isLoading = false }

        do {
            user = try await APIService.shared.getCurrentUser()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// Usage in SwiftUI (no @ObservedObject needed!)
struct ProfileView: View {
    let viewModel = UserViewModel()

    var body: some View {
        VStack {
            if viewModel.isLoading {
                ProgressView()
            } else if let user = viewModel.user {
                Text(user.name)
            }
        }
        .task {
            await viewModel.loadUser()
        }
    }
}
```

### Result Builders

```swift
@resultBuilder
struct ArrayBuilder<Element> {
    static func buildBlock(_ components: [Element]...) -> [Element] {
        components.flatMap { $0 }
    }

    static func buildExpression(_ expression: Element) -> [Element] {
        [expression]
    }

    static func buildOptional(_ component: [Element]?) -> [Element] {
        component ?? []
    }

    static func buildEither(first component: [Element]) -> [Element] {
        component
    }

    static func buildEither(second component: [Element]) -> [Element] {
        component
    }

    static func buildArray(_ components: [[Element]]) -> [Element] {
        components.flatMap { $0 }
    }
}

// Usage
struct MenuItem {
    let title: String
    let action: () -> Void
}

func buildMenu(@ArrayBuilder<MenuItem> _ builder: () -> [MenuItem]) -> [MenuItem] {
    builder()
}

let menu = buildMenu {
    MenuItem(title: "Home", action: { })
    MenuItem(title: "Profile", action: { })

    if isAdmin {
        MenuItem(title: "Admin Panel", action: { })
    }

    for category in categories {
        MenuItem(title: category.name, action: { })
    }
}
```

### Property Wrappers

**@UserDefault Property Wrapper:**

```swift
@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T

    var wrappedValue: T {
        get {
            UserDefaults.standard.object(forKey: key) as? T ?? defaultValue
        }
        set {
            UserDefaults.standard.set(newValue, forKey: key)
        }
    }
}

// Usage
struct AppSettings {
    @UserDefault(key: "theme", defaultValue: "light")
    static var theme: String

    @UserDefault(key: "notifications_enabled", defaultValue: true)
    static var notificationsEnabled: Bool
}

// Access
print(AppSettings.theme)
AppSettings.theme = "dark"
```

**@Clamped Property Wrapper:**

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

// Usage
struct VolumeControl {
    @Clamped(0...100)
    var volume: Int = 50
}

var control = VolumeControl()
control.volume = 150  // Clamped to 100
control.volume = -10  // Clamped to 0
```

**@Trimmed Property Wrapper:**

```swift
@propertyWrapper
struct Trimmed {
    private var value: String = ""

    var wrappedValue: String {
        get { value }
        set { value = newValue.trimmingCharacters(in: .whitespacesAndNewlines) }
    }

    init(wrappedValue: String) {
        self.value = wrappedValue.trimmingCharacters(in: .whitespacesAndNewlines)
    }
}

// Usage in SwiftUI
struct RegistrationForm: View {
    @Trimmed var email = ""
    @Trimmed var name = ""

    var body: some View {
        Form {
            TextField("Email", text: $email)
            TextField("Name", text: $name)
        }
    }
}
```

---

## Best Practices

1. **ViewModifiers**
   - Keep modifiers focused and composable
   - Provide sensible defaults
   - Use extensions for convenience APIs
   - Document modifier behavior

2. **PreferenceKey**
   - Use for child-to-parent communication
   - Implement efficient reduce methods
   - Consider performance for frequent updates
   - Name coordinate spaces clearly

3. **GeometryReader**
   - Avoid overuse (performance impact)
   - Cache calculations when possible
   - Test across device sizes
   - Handle orientation changes

4. **Combine**
   - Debounce user input appropriately
   - Store cancellables in Set
   - Use [weak self] in closures
   - Consider async/await for new code

5. **Modern Features**
   - Prefer @Observable (iOS 18+) over ObservableObject
   - Use result builders for DSLs
   - Create reusable property wrappers
   - Leverage Swift macros for boilerplate

---

This reference provides advanced SwiftUI patterns for building sophisticated, production-ready iOS user interfaces.
