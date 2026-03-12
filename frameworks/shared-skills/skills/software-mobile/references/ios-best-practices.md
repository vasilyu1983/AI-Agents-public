# iOS Best Practices

Comprehensive guide to iOS development best practices for production applications.

---

## Architecture

**MVVM Pattern:**
- ViewModels should be `@MainActor` for UI updates
- Prefer `@Observable` (Swift 5.9+ / iOS 17+) for new SwiftUI code; use `ObservableObject` when supporting older baselines
- Prefer `@Environment` over `@EnvironmentObject`
- Use protocol-based dependency injection

**Clean Architecture:**

- Presentation Layer: Views + ViewModels
- Domain Layer: Use Cases + Business Logic
- Data Layer: Repositories + Network/Storage

**TCA (Composable Architecture):**

For complex SwiftUI apps requiring predictable state management and high testability:

- **State**: Single source of truth, immutable value type
- **Action**: Enum describing all possible events
- **Reducer**: Pure function `(State, Action) -> Effect<Action>`
- **Store**: Runtime that connects views to reducers

```swift
@Reducer
struct CounterFeature {
    @ObservableState
    struct State: Equatable {
        var count = 0
    }

    enum Action {
        case incrementTapped
        case decrementTapped
    }

    var body: some ReducerOf<Self> {
        Reduce { state, action in
            switch action {
            case .incrementTapped:
                state.count += 1
                return .none
            case .decrementTapped:
                state.count -= 1
                return .none
            }
        }
    }
}
```

When to use TCA:

- Complex state with many features/screens
- Need deterministic, time-travel debugging
- High test coverage requirements
- Team familiar with Redux/Elm patterns

---

## State Management

**Best Practices:**
- `@State` for local UI state (counter, toggle, text field)
- `@Observable + @State` for view-owned ViewModels (iOS 18+)
- `@Environment` for dependency injection and shared state
- Avoid `@EnvironmentObject` in new code

**State Scope:**
- Local: `@State`
- View-level: `@Observable` ViewModel
- Shared/Global: `@Environment`
- Persistent: UserDefaults, Keychain, Core Data

### @Bindable for NavigationStack

When using `@Observable` ViewModels with `NavigationStack`, you need `@Bindable` to create bindings:

```swift
struct DashboardView: View {
    @State private var viewModel = DashboardViewModel()

    var body: some View {
        // Create bindable reference inside body
        @Bindable var viewModel = viewModel

        NavigationStack(path: $viewModel.navigationPath) {
            // Content using $viewModel bindings
            List(viewModel.items) { item in
                NavigationLink(value: item) {
                    Text(item.title)
                }
            }
            .navigationDestination(for: Item.self) { item in
                DetailView(item: item)
            }
        }
    }
}

@MainActor @Observable
final class DashboardViewModel {
    var navigationPath = NavigationPath()
    var items: [Item] = []
}
```

Key points:

- `@Bindable var viewModel = viewModel` must be inside `body`
- This enables `$viewModel.property` bindings for `@Observable` classes
- Required for `NavigationStack(path:)`, `TextField`, `Toggle`, etc.

---

## Concurrency

### Swift Concurrency (Swift 5.5+)

**Swift Concurrency:**
- Always use `async/await` for asynchronous operations
- Keep UI state and SwiftUI-facing ViewModels on `@MainActor`
- Use actors for shared mutable state
- Use `defer` for guaranteed cleanup
- Check `Task.isCancelled` in long-running operations

**TaskGroup for Parallel Operations:**
- Use `withThrowingTaskGroup` for parallel async operations
- Limit concurrency with batching
- Handle errors per task or globally

```swift
@MainActor
final class DashboardViewModel {
    private let api: APIService
    private(set) var items: [Item] = []
    private(set) var isLoading = false

    init(api: APIService) { self.api = api }

    func load() async {
        isLoading = true
        defer { isLoading = false }
        do {
            items = try await api.fetchItems()
        } catch {
            // Map to UI-safe error and present
        }
    }
}

func processImages(_ images: [UIImage]) async -> [ProcessedImage] {
    await withTaskGroup(of: ProcessedImage?.self) { group in
        for image in images {
            group.addTask { await process(image) }
        }

        var processed: [ProcessedImage] = []
        for await result in group {
            if let result { processed.append(result) }
        }
        return processed
    }
}
```

### Swift 6 Migration / Strict Concurrency Checks

- When upgrading toolchains, follow Apple’s migration guidance and address strict concurrency warnings intentionally (do not silence blindly): prefer actor isolation, `Sendable` correctness, and explicit `@MainActor` boundaries for UI types.
- Avoid `Task.detached` unless you truly need to break actor inheritance; prefer structured tasks so cancellation and priority propagate.

---

## Networking

**URLSession:**
- Always use `async/await` with URLSession
- Validate HTTP status codes (200-299)
- Handle network errors gracefully
- Implement request timeouts (30-60 seconds)
- Use structured error types

**API Service Pattern:**
- Centralize API calls in a service layer
- Use protocols for testability
- Implement retry logic for transient failures
- Cache responses when appropriate

---

## Defensive API Decoding

Real-world APIs often return inconsistent data. Use defensive decoding to handle edge cases.

### Missing Required Fields

Backend APIs sometimes omit fields that should be required (e.g., `id`).

```swift
// BAD: Crashes if field is missing
let id = try container.decode(String.self, forKey: .id)

// GOOD: Handle missing fields gracefully
if let idValue = try container.decodeIfPresent(String.self, forKey: .id) {
    id = idValue
} else {
    id = UUID().uuidString  // Generate fallback
}
```

### Array vs Dictionary Format

APIs may return data in different formats depending on context:

```swift
// API might return either:
// Dictionary: {"employer_name": "ACME", "gross_pay": 50000}
// Array: [{"name": "employer_name", "value": "ACME"}, ...]

struct FieldArrayItem: Decodable {
    let name: String
    let value: FieldValueType?
}

// In custom decoder:
if let dictFields = try? container.decodeIfPresent([String: FieldValueType].self, forKey: .fields) {
    fields = dictFields ?? [:]
} else if let arrayFields = try? container.decodeIfPresent([FieldArrayItem].self, forKey: .fields) {
    // Convert array to dictionary
    fields = Dictionary(uniqueKeysWithValues: arrayFields.compactMap {
        guard let value = $0.value else { return nil }
        return ($0.name, value)
    })
} else {
    fields = [:]
}
```

### Multiple Key Formats (snake_case vs camelCase)

```swift
enum CodingKeys: String, CodingKey {
    case declarationId = "declaration_id"
    case declarationIdCamel = "declarationId"  // Fallback
}

init(from decoder: Decoder) throws {
    let container = try decoder.container(keyedBy: CodingKeys.self)
    declarationId = try container.decodeIfPresent(String.self, forKey: .declarationId)
        ?? container.decodeIfPresent(String.self, forKey: .declarationIdCamel)
        ?? ""
}
```

**Key Principle:** Always use `decodeIfPresent` and provide sensible defaults

---

## Security

**Token Storage:**
- ALWAYS use Keychain for tokens/credentials
- NEVER store sensitive data in UserDefaults
- Use `kSecAttrAccessible` for access control

**Network Security:**
- Use HTTPS for all network requests
- Implement certificate pinning for sensitive apps
- Validate SSL certificates

**Data Protection:**
- Enable Data Protection for sensitive files
- Use Face ID/Touch ID for authentication
- Implement app lock after inactivity

---

## Performance

**View Optimization:**
- Use `LazyVStack`/`LazyHStack` for large lists
- Implement pagination (20-50 items per page)
- Avoid expensive computations in `body`
- Use `equatable` to prevent unnecessary re-renders

**Image Loading:**
- Implement two-tier caching (memory + disk)
- Use `AsyncImage` with placeholders
- Resize images before caching
- Limit cache size (100-200 MB)

**Memory Management:**

- Use `[weak self]` in closures to prevent retain cycles
- Monitor memory with Instruments
- Implement proper cleanup in `deinit`

---

## Translucency and Material Effects (SwiftUI)

Prefer platform-provided materials for translucency/blur. Avoid custom rendering-heavy effects unless you have a clear, measured UX need.

### Material Card with Solid Fallback

```swift
struct MaterialCard<Content: View>: View {
    let content: Content

    init(@ViewBuilder content: () -> Content) {
        self.content = content()
    }

    var body: some View {
        if #available(iOS 15.0, *) {
            content
                .padding()
                .background(.ultraThinMaterial, in: RoundedRectangle(cornerRadius: 16, style: .continuous))
        } else {
            content
                .padding()
                .background(
                    RoundedRectangle(cornerRadius: 16, style: .continuous)
                        .fill(Color(.systemBackground))
                )
        }
    }
}
```

Key points:

- Prefer system materials (`.thinMaterial`/`.ultraThinMaterial`) over custom blur views
- Verify contrast and readability with Reduce Transparency enabled [Inference]
- Avoid large, full-screen blur surfaces on older devices (GPU cost) [Inference]

---

## Testing

**Unit Tests:**
- Prefer Swift Testing (Swift 6.1+) for unit tests
- Test ViewModels with structured fixtures and Observation-aware assertions
- Mock network calls with protocols
- Test async code with `async/await`
- Aim for 80%+ code coverage

**UI Tests:**
- Keep XCTest UI for critical user flows
- Test accessibility identifiers
- Implement Page Object pattern

**ViewInspector:**
- Test SwiftUI views directly
- Verify state changes
- Test user interactions

---

## Accessibility

**VoiceOver:**
- Add accessibility labels to all interactive elements
- Use semantic labels (`Button`, `Label`, not just `Text`)
- Test with VoiceOver enabled

**Dynamic Type:**
- Support Dynamic Type for all text
- Test at different text sizes
- Use `.font(.body)` instead of fixed sizes

**Color Contrast:**
- Ensure WCAG AA compliance (4.5:1 for text)
- Support Dark Mode
- Test with color blindness simulators

---

## App Store Guidelines

**Submission Checklist:**
- [ ] App Privacy details filled out
- [ ] Privacy manifest per target/framework; required-reason APIs declared
- [ ] Third-party SDK privacy manifests reviewed; follow current Apple requirements for embedded SDK compliance
- [ ] Sign in with Apple implemented (if using auth)
- [ ] App Store screenshots (all device sizes)
- [ ] Privacy policy URL
- [ ] Age rating correctly set
- [ ] No placeholder content
- [ ] No crashes or bugs
- [ ] Proper error handling

**Review Process:**
- Expect 24-48 hour review time
- Respond to App Review feedback promptly
- Test on physical devices before submission

---

## Deployment

### Version Support (Guidance)

- Choose minimum iOS support based on product analytics + device demographics; a common default is “current major minus ~2”, but confirm with your users and business requirements.
- Verify current App Store submission requirements (minimum SDK/toolchain) in App Store Connect / Apple developer news before release cutoffs.

**Versioning:**
- Use semantic versioning (MAJOR.MINOR.PATCH)
- Increment build number for each submission
- Tag releases in Git

**CI/CD:**
- Use Xcode Cloud or Fastlane
- Automate screenshots with Fastlane Snapshot
- Run tests in CI pipeline
- Automatic TestFlight uploads

---

## References

For implementation details, see:

- [template-swift.md](../assets/swift/template-swift.md) - Full iOS app template
- [template-swift-concurrency.md](../assets/swift/template-swift-concurrency.md) - Swift Concurrency patterns
- [template-swiftui-advanced.md](../assets/swiftui/template-swiftui-advanced.md) - Advanced SwiftUI patterns
- [template-swift-testing.md](../assets/swift/template-swift-testing.md) - Testing patterns
- [template-swift-performance.md](../assets/swift/template-swift-performance.md) - Performance optimization

---

## Shared Utilities (Backend Integration Patterns)

When building mobile apps that connect to backend services, reference these centralized utilities for consistent implementation:

- [auth-utilities.md](../../software-clean-code-standard/utilities/auth-utilities.md) — OAuth 2.1/PKCE patterns for mobile clients, JWT handling
- [error-handling.md](../../software-clean-code-standard/utilities/error-handling.md) — Result types, error patterns (Swift has native Result, but align with backend)
- [resilience-utilities.md](../../software-clean-code-standard/utilities/resilience-utilities.md) — Retry patterns, circuit breaker concepts for network calls
- [testing-utilities.md](../../software-clean-code-standard/utilities/testing-utilities.md) — Test factories, fixtures, mock patterns

---

This guide provides production-ready best practices for building secure, performant, and accessible iOS applications.
