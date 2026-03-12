# Core Mobile Patterns

## Pattern: Mobile App Architecture

**Use when:** Designing mobile application structure.

**Common Architectures:**

**MVVM (Model-View-ViewModel):**
```
Model (Data) ↔ ViewModel (Business Logic) ↔ View (UI)
```

**MVI (Model-View-Intent):**
```
User Intent → Model Update → View Re-render
```

**Clean Architecture:**
```
Presentation Layer → Domain Layer → Data Layer
```

**Structure:**
```
app/
├── models/ # Data models
├── viewmodels/ # Business logic
├── views/ # UI components
├── services/ # API, storage, etc.
├── repositories/ # Data access
├── utils/ # Utilities
└── navigation/ # Navigation logic
```

**Checklist:**
- [ ] Separation of concerns (UI, logic, data)
- [ ] Dependency injection
- [ ] Testable architecture
- [ ] Clear data flow
- [ ] Offline-first capability

---

## Pattern: Platform-Specific Patterns

**Use when:** Implementing navigation, state management, networking, storage, authentication, or push notifications.

For comprehensive platform-specific patterns for iOS and Android, see:

**Reference:** `assets/cross-platform/template-platform-patterns.md`

**Key Patterns Covered:**
- **Navigation**: NavigationStack (iOS 17+), TabView, Jetpack Compose Navigation, Bottom Navigation
- **State Management**: @State/@Observable + @Environment (iOS), remember/ViewModel/StateFlow (Android)
- **Network Requests**: URLSession with async/await (iOS), Retrofit with Coroutines (Android)
- **Local Storage**: Core Data (iOS), Room Database (Android)
- **Authentication**: Keychain (iOS), EncryptedSharedPreferences (Android)
- **Push Notifications**: APNs (iOS), FCM (Android)

**Quick Reference - iOS Navigation:**
```swift
NavigationStack(path: $path) {
 List {
 NavigationLink("Users", value: Route.users)
 }
 .navigationDestination(for: Route.self) { route in
 // Route to view
 }
}
```

**Quick Reference - Android Navigation:**
```kotlin
NavHost(navController, startDestination = "home") {
 composable("home") { HomeScreen() }
 composable("detail/{id}") { DetailScreen() }
}
```

**Quick Reference - State Management:**
```swift
// iOS
@State private var count = 0 // Local
@State private var viewModel = ViewModel() // View-owned (@Observable)
@Environment(ViewModel.self) private var auth // Global via environment injection
```

```kotlin
// Android
var count by remember { mutableStateOf(0) } // Local
val users by viewModel.users.collectAsState() // ViewModel
```

---

## Pattern: Swift Concurrency

**Use when:** Building concurrent operations with actors, task groups, and async sequences.

For comprehensive Swift Concurrency patterns including Actors, TaskGroup, AsyncSequence, and advanced async/await techniques, see:

**Reference:** `assets/swift/template-swift-concurrency.md`

**Key Patterns Covered:**
- **Actors**: Thread-safe state management (@MainActor, custom actors)
- **Task Groups**: Parallel operations with error handling and concurrency limits
- **AsyncSequence**: Streaming data with custom iterators and operators
- **Advanced Patterns**: Task cancellation, priority, detached tasks, sendable types

**Quick Example - Actor:**
```swift
actor UserCache {
 private var cache: [String: User] = [:]

 func getUser(id: String) async -> User? {
 cache[id]
 }

 func setUser(_ user: User) async {
 cache[user.id] = user
 }
}
```

**Quick Example - TaskGroup:**
```swift
func fetchMultipleUsers(ids: [String]) async throws -> [User] {
 try await withThrowingTaskGroup(of: User.self) { group in
 for id in ids {
 group.addTask {
 try await APIService.shared.getUser(id: id)
 }
 }

 var users: [User] = []
 for try await user in group {
 users.append(user)
 }
 return users
 }
}
```

---

## Pattern: SwiftUI Advanced Patterns

**Use when:** Building sophisticated UIs with custom modifiers, preference keys, reactive state, and modern Swift features.

For comprehensive SwiftUI advanced patterns including ViewModifiers, PreferenceKey, GeometryReader, Combine integration, and Swift 6.0+ features, see:

**Reference:** `assets/swiftui/template-swiftui-advanced.md`

**Key Patterns Covered:**
- **ViewModifiers**: Reusable styling and conditional modifiers
- **PreferenceKey**: Child-to-parent data flow, scroll offset tracking
- **GeometryReader**: Adaptive layouts and responsive grids
- **Combine Integration**: Reactive state, debouncing, publisher chaining
- **Swift 6.0+**: @Observable macro, result builders, property wrappers

**Quick Example - ViewModifier:**
```swift
struct CardModifier: ViewModifier {
 var backgroundColor: Color = .white
 var cornerRadius: CGFloat = 12

 func body(content: Content) -> some View {
 content
 .padding()
 .background(backgroundColor)
 .cornerRadius(cornerRadius)
 }
}

extension View {
 func cardStyle() -> some View {
 modifier(CardModifier())
 }
}
```

**Quick Example - PreferenceKey:**
```swift
struct SizePreferenceKey: PreferenceKey {
 static var defaultValue: CGSize = .zero
 static func reduce(value: inout CGSize, nextValue: () -> CGSize) {
 value = nextValue()
 }
}
```

---

## Pattern: Mobile Security

**Use when:** Building secure mobile applications.

**IMPORTANT:** For comprehensive security patterns, see the **software-security-appsec** skill which covers:
- OWASP Mobile Top 10 vulnerabilities
- Authentication & Authorization (OAuth, biometrics, secure token storage)
- Data encryption at rest and in transit
- Secure API communication
- Input validation and sanitization
- Cryptography standards for mobile

**Mobile-Specific Security:**
- **Keychain/Keystore**: Use iOS Keychain and Android Keystore for sensitive data
- **Certificate Pinning**: Prevent MITM attacks on API calls
- **Biometric Authentication**: FaceID/TouchID (iOS), BiometricPrompt (Android)
- **App Transport Security**: Enforce HTTPS only (iOS)
- **ProGuard/R8**: Obfuscate code (Android)
- **Jailbreak Detection**: Detect compromised devices
- **Secure Storage**: Never store secrets in UserDefaults/SharedPreferences

**Quick Example - Keychain (iOS):**
```swift
import Security

func saveToKeychain(key: String, data: Data) -> Bool {
    let query: [String: Any] = [
        kSecClass as String: kSecClassGenericPassword,
        kSecAttrAccount as String: key,
        kSecValueData as String: data
    ]

    SecItemDelete(query as CFDictionary)
    return SecItemAdd(query as CFDictionary, nil) == errSecSuccess
}
```

**Quick Example - Keystore (Android):**
```kotlin
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKeys

val masterKeyAlias = MasterKeys.getOrCreate(MasterKeys.AES256_GCM_SPEC)

val sharedPreferences = EncryptedSharedPreferences.create(
    "secure_prefs",
    masterKeyAlias,
    context,
    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
)
```

**Checklist:**
- [ ] Sensitive data in Keychain/Keystore only
- [ ] Certificate pinning for API calls
- [ ] Biometric authentication implemented
- [ ] HTTPS enforced for all network calls
- [ ] Code obfuscation enabled (Android)
- [ ] Jailbreak/root detection implemented
- [ ] No hardcoded secrets in code

---

# Quick Decision Tables

## Platform Selection

| Need | iOS | Android | React Native | WebView |
|------|-----|---------|--------------|---------|
| Native performance | BEST | BEST | CONDITIONAL | OMIT |
| Platform-specific UI | BEST | BEST | CONDITIONAL | OMIT |
| Faster development | OMIT | OMIT | INCLUDE | INCLUDE |
| Code sharing | OMIT | OMIT | INCLUDE | INCLUDE |
| Web content | OMIT | OMIT | CONDITIONAL | BEST |
| Existing web app | OMIT | OMIT | OMIT | BEST |

---

## State Management Selection

| Scope | iOS | Android |
|-------|-----|---------|
| Local UI | @State | remember |
| View-level | @Observable + @State | ViewModel |
| Shared/Global | @Environment | Singleton/DI |
| Persistent | UserDefaults/SwiftData/CoreData | SharedPreferences/Room |

---

# Templates

See `assets/` directory for platform-specific implementations:

**Swift Templates** (`assets/swift/`)
- `template-swift.md` - iOS (Swift 6.1+ + SwiftUI, MVVM, @Observable)
- `template-swift-combine.md` - iOS (SwiftUI + Combine, Reactive state management)
- `template-swift-testing.md` - iOS (TDD with XCTest + ViewInspector, comprehensive testing)
- `template-swift-performance.md` - iOS (Performance-optimized, lazy loading, caching, profiling)
- `template-swift-concurrency.md` - Swift Concurrency (Actors, TaskGroup, AsyncSequence)

**SwiftUI Templates** (`assets/swiftui/`)
- `template-swiftui-advanced.md` - SwiftUI Advanced (ViewModifiers, PreferenceKey, Combine, Swift 6.0+)

**Kotlin Templates** (`assets/kotlin/`)
- `template-kotlin.md` - Android (Kotlin + Jetpack Compose, MVVM, Hilt)
- `template-kotlin-coroutines.md` - Kotlin Coroutines (Flow, StateFlow, Channels, async patterns)
- `template-kotlin-compose-advanced.md` - Jetpack Compose Advanced (Modifiers, Side Effects, Animations)
- `template-kotlin-testing.md` - Android Testing (JUnit, MockK, Compose UI Testing)

**Cross-Platform Templates** (`assets/cross-platform/`)
- `template-platform-patterns.md` - iOS & Android Platform Patterns (Navigation, State, Networking, Storage, Auth, Notifications)
- `template-webview.md` - WebView wrapper (iOS + Android)

---

# Resources

**Best Practices Guides** (`references/`)
- `ios-best-practices.md` - iOS architecture, security, performance, testing, deployment
- `android-best-practices.md` - Android architecture, security, performance, testing, deployment

**External Documentation:**
See [data/sources.json](../data/sources.json) for official documentation links and learning resources.

---

# END
```
