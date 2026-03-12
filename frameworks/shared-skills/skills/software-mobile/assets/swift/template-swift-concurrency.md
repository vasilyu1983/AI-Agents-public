# Swift Concurrency Patterns Reference

Comprehensive guide to modern Swift Concurrency patterns including Actors, TaskGroup, AsyncSequence, and advanced async/await techniques for iOS development.

---

## Table of Contents

1. [Swift Concurrency (Swift 5.5+)](#swift-concurrency-swift-55)
2. [Actors for Thread-Safe State](#actors-for-thread-safe-state)
3. [Task Groups for Parallel Operations](#task-groups-for-parallel-operations)
4. [AsyncSequence for Streaming Data](#asyncsequence-for-streaming-data)
5. [Advanced Concurrency Patterns](#advanced-concurrency-patterns)

---

## Swift Concurrency (Swift 5.5+)

**Use when:** Writing async code with `async/await`, cancellation, actors, and data-race safety; especially when upgrading toolchains with stricter concurrency checking.

Swift Concurrency is based on structured concurrency: tasks inherit priority and cancellation, and actor isolation protects shared mutable state. For UI apps, the default is to keep UI-facing state on the main actor and move I/O / CPU work off the main thread explicitly.

### Key Benefits

- **Structured cancellation**: Cancellation propagates through child tasks
- **Actor isolation**: Shared mutable state is protected without manual locking
- **Static checking**: Toolchains can enforce `Sendable` and isolation boundaries to prevent data races

### Basic Pattern

```swift
@MainActor
final class UserListViewModel: ObservableObject {
    @Published private(set) var users: [User] = []
    @Published private(set) var isLoading = false

    private let api: APIService

    init(api: APIService) { self.api = api }

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }

        do {
            users = try await api.fetchUsers()
        } catch {
            // Map to UI-safe error and present
        }
    }
}
```

### Running CPU/I/O Work Off the Main Actor

```swift
// Use Task.detached only when you explicitly need to break actor inheritance.
// Captures must be Sendable (prefer value types).
func processData(_ input: Input) async -> Output {
    await Task.detached(priority: .userInitiated) {
        await heavyComputation(input)
    }.value
}
```

### SwiftUI Integration

```swift
struct UserListView: View {
    @StateObject private var viewModel = UserListViewModel(api: APIService())

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task {
            await viewModel.loadUsers()
        }
    }
}
```

**Best Practices:**

- Keep SwiftUI-facing state on `@MainActor`
- Use actors for caches, dedupers, and shared state
- Prefer structured tasks over detached tasks so cancellation and priority propagate
- Treat concurrency warnings as design feedback; fix via isolation (`@MainActor`, actors) and `Sendable` correctness

---

## Actors for Thread-Safe State

**Use when:** Managing shared mutable state safely across concurrent tasks.

### Actor for Thread-Safe State

```swift
actor UserCache {
    private var cache: [String: User] = [:]
    private var lastUpdated: Date?

    func getUser(id: String) async -> User? {
        cache[id]
    }

    func setUser(_ user: User) async {
        cache[user.id] = user
        lastUpdated = Date()
    }

    func clear() async {
        cache.removeAll()
        lastUpdated = nil
    }

    // Non-isolated for read-only access
    nonisolated func cacheSize() -> Int {
        // Compiler error - can't access mutable state
        // Use Task to await if needed
        return 0
    }
}

// Usage
let cache = UserCache()

Task {
    await cache.setUser(user)
    let cached = await cache.getUser(id: "123")
}
```

### Global Actor (@MainActor)

```swift
@MainActor
class UIStateManager: ObservableObject {
    @Published var isLoading = false
    @Published var errorMessage: String?

    func showError(_ message: String) {
        // Always runs on main thread
        errorMessage = message
    }
}

// Usage in ViewModel
@MainActor
class ProfileViewModel: ObservableObject {
    @Published var user: User?

    func loadUser() async {
        // Already on MainActor, safe to update @Published
        user = try? await APIService.shared.getUser()
    }
}
```

### Custom Global Actor

```swift
@globalActor
actor DatabaseActor {
    static let shared = DatabaseActor()
}

@DatabaseActor
class DatabaseManager {
    private var connection: DatabaseConnection?

    func query(_ sql: String) async throws -> [Row] {
        // All calls serialized through DatabaseActor
        try await connection?.execute(sql)
    }
}
```

**Checklist:**
- [ ] Use actors for shared mutable state
- [ ] @MainActor for UI-related code
- [ ] Avoid blocking actor's executor
- [ ] Use nonisolated for pure functions
- [ ] Custom actors for domain-specific isolation

---

## Task Groups for Parallel Operations

**Use when:** Running multiple async operations concurrently and collecting results.

### TaskGroup for Parallel Fetching

```swift
func fetchMultipleUsers(ids: [String]) async throws -> [User] {
    try await withThrowingTaskGroup(of: User.self) { group in
        // Add tasks to group
        for id in ids {
            group.addTask {
                try await APIService.shared.getUser(id: id)
            }
        }

        // Collect results as they complete
        var users: [User] = []
        for try await user in group {
            users.append(user)
        }
        return users
    }
}
```

### TaskGroup with Error Handling

```swift
func fetchUsersWithFallback(ids: [String]) async -> [Result<User, Error>] {
    await withTaskGroup(of: Result<User, Error>.self) { group in
        for id in ids {
            group.addTask {
                do {
                    let user = try await APIService.shared.getUser(id: id)
                    return .success(user)
                } catch {
                    return .failure(error)
                }
            }
        }

        var results: [Result<User, Error>] = []
        for await result in group {
            results.append(result)
        }
        return results
    }
}
```

### Limiting Concurrency

```swift
func batchFetchUsers(ids: [String], maxConcurrent: Int = 5) async throws -> [User] {
    var users: [User] = []

    for batch in ids.chunked(into: maxConcurrent) {
        let batchUsers = try await withThrowingTaskGroup(of: User.self) { group in
            for id in batch {
                group.addTask {
                    try await APIService.shared.getUser(id: id)
                }
            }

            var results: [User] = []
            for try await user in group {
                results.append(user)
            }
            return results
        }
        users.append(contentsOf: batchUsers)
    }

    return users
}

extension Array {
    func chunked(into size: Int) -> [[Element]] {
        stride(from: 0, to: count, by: size).map {
            Array(self[$0..<Swift.min($0 + size, count)])
        }
    }
}
```

**Checklist:**
- [ ] Use TaskGroup for parallel async operations
- [ ] Handle errors per task or globally
- [ ] Limit concurrency for resource control
- [ ] Cancel group when needed
- [ ] Collect results efficiently

---

## AsyncSequence for Streaming Data

**Use when:** Processing streams of asynchronous data.

### Custom AsyncSequence

```swift
struct NotificationStream: AsyncSequence {
    typealias Element = Notification

    let notificationName: Notification.Name

    func makeAsyncIterator() -> AsyncIterator {
        AsyncIterator(notificationName: notificationName)
    }

    struct AsyncIterator: AsyncIteratorProtocol {
        let notificationName: Notification.Name
        private var continuation: AsyncStream<Notification>.Continuation?
        private let stream: AsyncStream<Notification>
        private var iterator: AsyncStream<Notification>.Iterator

        init(notificationName: Notification.Name) {
            self.notificationName = notificationName
            self.stream = AsyncStream { continuation in
                self.continuation = continuation

                let observer = NotificationCenter.default.addObserver(
                    forName: notificationName,
                    object: nil,
                    queue: nil
                ) { notification in
                    continuation.yield(notification)
                }

                continuation.onTermination = { _ in
                    NotificationCenter.default.removeObserver(observer)
                }
            }
            self.iterator = stream.makeAsyncIterator()
        }

        mutating func next() async -> Notification? {
            await iterator.next()
        }
    }
}

// Usage
for await notification in NotificationStream(notificationName: .userDidLogin) {
    print("User logged in: \(notification)")
}
```

### AsyncSequence Operators

```swift
extension AsyncSequence {
    func compactMap<T>(_ transform: @escaping (Element) async throws -> T?) rethrows -> AsyncCompactMapSequence<Self, T> {
        AsyncCompactMapSequence(self, transform: transform)
    }

    func filter(_ predicate: @escaping (Element) async throws -> Bool) rethrows -> AsyncFilterSequence<Self> {
        AsyncFilterSequence(self, predicate: predicate)
    }
}

// Usage
let eventStream = NotificationStream(notificationName: .dataUpdated)
    .compactMap { notification -> User? in
        notification.userInfo?["user"] as? User
    }
    .filter { user in
        user.isActive
    }

for await user in eventStream {
    print("Active user updated: \(user.name)")
}
```

### URL Session AsyncBytes

```swift
func downloadLargeFile(url: URL) async throws {
    let (asyncBytes, response) = try await URLSession.shared.bytes(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw URLError(.badServerResponse)
    }

    var data = Data()
    for try await byte in asyncBytes {
        data.append(byte)

        // Progress tracking
        let progress = Double(data.count) / Double(httpResponse.expectedContentLength)
        print("Download progress: \(progress * 100)%")
    }
}
```

**Checklist:**
- [ ] Use AsyncSequence for streaming data
- [ ] Implement custom iterators when needed
- [ ] Use operators for transformation
- [ ] Handle cancellation properly
- [ ] Monitor memory for long-running streams

---

## Advanced Concurrency Patterns

### Task Cancellation

```swift
class DownloadManager {
    private var downloadTask: Task<Data, Error>?

    func startDownload(from url: URL) {
        downloadTask = Task {
            let (data, _) = try await URLSession.shared.data(from: url)
            return data
        }
    }

    func cancelDownload() {
        downloadTask?.cancel()
        downloadTask = nil
    }

    func checkCancellation() async throws -> Data {
        try Task.checkCancellation()

        // Or use:
        if Task.isCancelled {
            throw CancellationError()
        }

        let data = try await heavyOperation()
        return data
    }
}
```

### Task Priority

```swift
func processWithPriority() {
    // High priority task
    Task(priority: .high) {
        await criticalOperation()
    }

    // Background task
    Task(priority: .background) {
        await cleanupOperation()
    }

    // User-initiated task (default)
    Task(priority: .userInitiated) {
        await fetchData()
    }
}
```

### Detached Tasks

```swift
func performHeavyComputation() {
    // Detached task - doesn't inherit context
    Task.detached(priority: .background) {
        let result = await expensiveCalculation()
        print(result)
    }
}
```

### AsyncStream

```swift
func makeLocationStream() -> AsyncStream<CLLocation> {
    AsyncStream { continuation in
        let manager = CLLocationManager()
        let delegate = LocationDelegate(continuation: continuation)

        manager.delegate = delegate
        manager.startUpdatingLocation()

        continuation.onTermination = { _ in
            manager.stopUpdatingLocation()
        }
    }
}

// Usage
for await location in makeLocationStream() {
    print("New location: \(location.coordinate)")
}
```

### Actor Reentrancy

```swift
actor Counter {
    private var value = 0

    func increment() async {
        // Suspension point - actor can be re-entered
        await Task.yield()

        // Value might have changed!
        value += 1
    }

    func safeIncrement() {
        // No suspension - atomic
        value += 1
    }
}
```

### Sendable Types

```swift
// Value types are implicitly Sendable
struct User: Sendable {
    let id: String
    let name: String
}

// Classes must explicitly conform
final class UserCache: Sendable {
    let cache: [String: User] // Must be immutable
}

// Mark closure as Sendable
func performAsync(_ operation: @Sendable () async -> Void) async {
    await operation()
}
```

---

## Best Practices

1. **Use @MainActor for UI Code**
   - Mark ViewModels and UI-related classes
   - Ensures all UI updates happen on main thread
   - Prevents threading issues

2. **Prefer Actors Over Locks**
   - Actors provide compile-time safety
   - No deadlocks or race conditions
   - Better performance in most cases

3. **Handle Cancellation**
   - Check `Task.isCancelled` in long operations
   - Use `Task.checkCancellation()`
   - Clean up resources on cancellation

4. **Limit Concurrency**
   - Don't create unlimited concurrent tasks
   - Use TaskGroup with batching
   - Consider system resources

5. **Avoid Blocking Operations**
   - Never block an actor's executor
   - Use `Task.detached` for CPU-intensive work
   - Keep actor methods fast

6. **Test Concurrent Code**
   - Test cancellation paths
   - Test race conditions
   - Use async test helpers

---

## Common Pitfalls

### AVOID: Capturing Self Strongly in Tasks

```swift
// Bad
class ViewModel {
    func loadData() {
        Task {
            self.data = await fetchData() // Retains self
        }
    }
}

// Good
class ViewModel {
    func loadData() {
        Task { [weak self] in
            guard let self = self else { return }
            self.data = await fetchData()
        }
    }
}
```

### AVOID: Ignoring Cancellation

```swift
// Bad
func processItems(_ items: [Item]) async {
    for item in items {
        await process(item) // Continues even if cancelled
    }
}

// Good
func processItems(_ items: [Item]) async throws {
    for item in items {
        try Task.checkCancellation()
        await process(item)
    }
}
```

### AVOID: Mixing Actors with Locks

```swift
// Bad
actor Cache {
    private let lock = NSLock()
    private var data: [String: Data] = [:]

    func get(_ key: String) -> Data? {
        lock.lock()
        defer { lock.unlock() }
        return data[key]
    }
}

// Good - actors don't need locks
actor Cache {
    private var data: [String: Data] = [:]

    func get(_ key: String) -> Data? {
        data[key]
    }
}
```

---

This reference provides comprehensive Swift Concurrency patterns for building safe, performant concurrent iOS applications.
