# Swift Concurrency Patterns

Constructive patterns for writing correct Swift Concurrency code. Complements the crash triage reference (`swift-concurrency-crash-triage.md`) which covers reactive diagnosis.

Primary docs:

- https://developer.apple.com/documentation/swift/concurrency
- https://docs.swift.org/swift-book/documentation/the-swift-programming-language/concurrency/

## Table of Contents

- [Concurrency Tool Selection](#concurrency-tool-selection)
- [Structured Concurrency](#structured-concurrency)
- [Async Streams](#async-streams)
- [Actor Patterns](#actor-patterns)
- [Bridging Sync and Async](#bridging-sync-and-async)
- [GCD-to-Concurrency Migration](#gcd-to-concurrency-migration)
- [Combine-to-AsyncSequence Migration](#combine-to-asyncsequence-migration)
- [Swift 6.2 Features](#swift-62-features)
- [Review Hotspots](#review-hotspots)

## Hard Rules

- **Never use GCD** (`DispatchQueue`) in new code. Swift Concurrency replaces all GCD patterns. GCD is acceptable only in low-level framework interop or performance-critical synchronous work where an actor hop is measured as too expensive.
- **Never use `Task.sleep(nanoseconds:)`** — use `Task.sleep(for: .seconds(N))` or `Task.sleep(for: .milliseconds(N))`. The `nanoseconds` variant is error-prone and doesn't support `Duration`.
- **Before flagging `MainActor.run {}` as unnecessary**, check whether the project uses default main-actor isolation (`SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor`). With default isolation, many `MainActor.run` calls are genuinely redundant. Without it, they may be necessary.
- **`nonisolated async` functions stay on the caller's actor by default in Swift 6.2** — they no longer hop to the global executor. Use `@concurrent` to explicitly opt into offloading. This is a behavioral change from Swift 6.1.

## Concurrency Tool Selection

| Need | Tool | When to choose |
|---|---|---|
| Await a single async result | `async`/`await` | Default for any async call |
| Run 2-3 independent async operations | `async let` | Known fixed number of tasks at compile time |
| Run N dynamic parallel operations | `withTaskGroup` / `withThrowingTaskGroup` | Unknown or variable number of tasks |
| Fire-and-forget background work | `withDiscardingTaskGroup` | Results not needed; errors logged internally |
| One-off unstructured background work | `Task { }` | Inherits actor context; use sparingly |
| Detached work with no inheritance | `Task.detached { }` | Rarely correct — only when you intentionally need to break priority/actor inheritance |
| Protect mutable shared state | `actor` | Multiple isolation contexts need safe mutation |
| UI-bound state protection | `@MainActor` class | All consumers are main-isolated |
| Synchronous locking | `Mutex` (Swift 6.0+) | Synchronous API that cannot be async; replaces `os_unfair_lock` |

## Structured Concurrency

### async let scoping trap

`async let` variables that are never awaited are **implicitly cancelled and awaited** at scope exit. This can cause unexpected delays or suppress errors:

```swift
func example() async throws {
    async let result = expensiveWork()  // Started
    if condition {
        return  // result is cancelled AND awaited here — blocks until expensiveWork finishes cancellation cleanup
    }
    let value = try await result
}
```

Always `await` your `async let` values explicitly, or be aware that early returns will block until the implicit cancellation completes.

### Task-local values do not propagate to Task.detached

`@TaskLocal` values propagate to structured children (`async let`, task groups) and `Task { }`, but NOT to `Task.detached { }`. Logging correlation IDs, request context, and tracing tokens will be silently lost in detached tasks.

### async let (fixed parallelism)

```swift
async let user = fetchUser(id: userId)
async let posts = fetchPosts(for: userId)
let (fetchedUser, fetchedPosts) = try await (user, posts)
```

### Task groups (dynamic parallelism)

```swift
let results = try await withThrowingTaskGroup(of: (Int, Data).self) { group in
    for id in ids {
        group.addTask { (id, try await fetchData(id: id)) }
    }
    var collected: [Int: Data] = [:]
    for try await (id, data) in group {
        collected[id] = data
    }
    return collected
}
```

### Limiting concurrency

```swift
await withTaskGroup(of: Void.self) { group in
    var iterator = urls.makeIterator()
    // Seed with N concurrent workers
    for _ in 0..<maxConcurrent {
        guard let url = iterator.next() else { break }
        group.addTask { await download(url) }
    }
    // As each finishes, start the next
    for await _ in group {
        guard let url = iterator.next() else { continue }
        group.addTask { await download(url) }
    }
}
```

### Discarding task groups (fire-and-forget)

```swift
try await withDiscardingTaskGroup { group in
    for event in events {
        group.addTask { try await process(event) }
    }
    // No return value collection; errors propagate
}
```

### Error handling with partial results

```swift
await withTaskGroup(of: Result<Item, Error>.self) { group in
    for id in ids {
        group.addTask {
            do { return .success(try await fetch(id)) }
            catch { return .failure(error) }
        }
    }
    var items: [Item] = []
    var errors: [Error] = []
    for await result in group {
        switch result {
        case .success(let item): items.append(item)
        case .failure(let error): errors.append(error)
        }
    }
}
```

## Cancellation

### How Cancellation Works

Cancellation in Swift Concurrency is **cooperative** — setting a task as cancelled does not stop it. The task's code must check for cancellation and exit gracefully.

### Propagation Rules

- Cancelling a parent task cancels all its structured children (async let, task group children)
- Cancelling an unstructured `Task {}` does NOT propagate to its parent
- `Task.detached {}` has no parent — cancellation is fully independent
- Cancelling a task group cancels all tasks in the group

### checkCancellation vs isCancelled

| API | Behavior | Use When |
|---|---|---|
| `try Task.checkCancellation()` | Throws `CancellationError` if cancelled | Default — propagates cancellation up the call chain |
| `Task.isCancelled` | Returns `Bool`, does not throw | When you need to do cleanup before exiting, or return a partial result |

```swift
// Default: throw on cancellation
func processItems(_ items: [Item]) async throws -> [Result] {
    var results: [Result] = []
    for item in items {
        try Task.checkCancellation()  // Exits immediately if cancelled
        results.append(try await process(item))
    }
    return results
}

// When you need cleanup or partial results
func processWithCleanup(_ items: [Item]) async -> [Result] {
    var results: [Result] = []
    for item in items {
        if Task.isCancelled {
            await savePartialResults(results)
            break
        }
        if let result = try? await process(item) {
            results.append(result)
        }
    }
    return results
}
```

### withTaskCancellationHandler

Bridges cancellation into callback-based or delegate-based APIs:

```swift
func downloadFile(url: URL) async throws -> Data {
    let session = URLSession.shared
    let request = URLRequest(url: url)

    return try await withTaskCancellationHandler {
        try await session.data(for: request).0
    } onCancel: {
        // Called immediately when task is cancelled
        // Runs on an arbitrary thread — keep it minimal
        session.invalidateAndCancel()
    }
}
```

The `onCancel` handler runs immediately, even if the main body has not started yet. It runs on an arbitrary thread — do not access actor-isolated state from it.

### Broken Cancellation Patterns

| Pattern | Problem | Fix |
|---|---|---|
| `catch { }` that swallows `CancellationError` | Cancellation is silently ignored; work continues | Re-throw `CancellationError` or check `error is CancellationError` and return |
| Stored `Task` property without cleanup | Task runs forever even after the owning view/object is gone | Cancel stored tasks in `deinit`, `onDisappear`, or `task` modifier |
| CPU-bound loop without cancellation check | Cannot be cancelled; blocks until done | Add `try Task.checkCancellation()` at loop iteration boundaries |
| `task.cancel()` and assuming immediate stop | Cancellation is cooperative; code must check | Verify task body contains checkCancellation or isCancelled checks |

```swift
// WRONG — CancellationError silently caught
do {
    try await longRunningWork()
} catch {
    // Swallows CancellationError along with real errors
    logger.error("Failed: \(error)")
}

// CORRECT — re-throw cancellation
do {
    try await longRunningWork()
} catch is CancellationError {
    throw error  // Let cancellation propagate
} catch {
    logger.error("Failed: \(error)")
}
```

## Async Streams

### Creating streams (prefer makeStream factory)

```swift
// Modern (Swift 5.9+) — prefer this
let (stream, continuation) = AsyncStream.makeStream(of: Event.self)

// Continuation lifecycle: finish exactly once
continuation.yield(event)
continuation.finish()  // Must be called; omitting leaks the consumer
```

### Buffering policies

| Policy | Behavior |
|---|---|
| `.bufferingNewest(n)` | Keeps the newest N elements; drops oldest when full |
| `.bufferingOldest(n)` | Keeps the oldest N elements; drops newest when full |
| `.unbounded` | No limit — memory grows unbounded if consumer is slow |

Default is `.unbounded`. For UI event streams, prefer `.bufferingNewest(1)` to avoid backpressure from slow consumers.

### Consuming streams

```swift
for await event in stream {
    handle(event)
}
// Loop exits when continuation.finish() is called or task is cancelled
```

### Wrapping delegate APIs

```swift
func locationUpdates() -> AsyncStream<CLLocation> {
    let (stream, continuation) = AsyncStream.makeStream(of: CLLocation.self)
    let delegate = LocationDelegate(continuation: continuation)
    continuation.onTermination = { _ in
        delegate.stop()  // Clean up when consumer cancels
    }
    delegate.start()
    return stream
}
```

## Actor Patterns

### Reentrancy (most common LLM concurrency bug)

Never assume state is unchanged after an `await` inside an actor:

```swift
actor Cache {
    var data: [String: Data] = [:]

    // WRONG — state may have changed after await
    func fetchIfNeeded(key: String) async throws -> Data {
        if data[key] == nil {
            data[key] = try await network.fetch(key)  // Another call may have set it
        }
        return data[key]!
    }

    // CORRECT — in-flight task deduplication
    var inFlight: [String: Task<Data, Error>] = [:]

    func fetch(key: String) async throws -> Data {
        if let cached = data[key] { return cached }
        if let existing = inFlight[key] { return try await existing.value }

        let task = Task { try await network.fetch(key) }
        inFlight[key] = task
        defer { inFlight[key] = nil }

        let result = try await task.value
        data[key] = result
        return result
    }
}
```

### Global actor inference rules

Isolation propagates through:
- Subclasses (inherit superclass isolation)
- Property wrappers that are actor-isolated
- Protocol conformance (when the protocol requires isolation)
- Extensions that are explicitly annotated

Isolation does NOT propagate to:
- Closures (must be explicitly annotated or inherit from context)
- Unstructured `Task { }` in Swift 5.x (does NOT inherit class `@MainActor`)

### Isolated parameters

Pass actor isolation explicitly to functions that need to run on a specific actor:

```swift
func updateUI(isolation: isolated any Actor = #isolation) async {
    // Runs on whatever actor the caller is isolated to
}

// Or explicitly require main actor
func refreshView(isolation: isolated MainActor) {
    // Guaranteed to run on main actor
}
```

### Debugging isolation

```swift
MainActor.assertIsolated()  // Crashes if not on main actor
SomeActor.assertIsolated()  // Crashes if not on the actor
```

## Bridging Sync and Async

### Continuations (exactly-once resume)

```swift
func loadData() async throws -> Data {
    try await withCheckedThrowingContinuation { continuation in
        legacyLoader.load { result in
            switch result {
            case .success(let data):
                continuation.resume(returning: data)
            case .failure(let error):
                continuation.resume(throwing: error)
            }
            // Must resume exactly once. Zero resumes = consumer hangs forever.
            // Two resumes = runtime crash.
        }
    }
}
```

### Runtime actor assertions

```swift
// When you know you're on the main actor but the compiler doesn't
MainActor.assumeIsolated {
    updateUI()  // Safe only if truly on main
}
```

## GCD-to-Concurrency Migration

| GCD Pattern | Swift Concurrency Replacement |
|---|---|
| `DispatchQueue.main.async { }` | `@MainActor` isolation or `Task { @MainActor in }` |
| `DispatchQueue.global().async { }` | `@concurrent` function (Swift 6.2+) or `Task.detached` |
| Serial `DispatchQueue` (state protection) | `actor` |
| `DispatchQueue` with `sync` (blocking read) | `Mutex` (Swift 6.0+) for synchronous APIs |
| `DispatchGroup` + `notify` | `async let` or `withTaskGroup` |
| `DispatchSemaphore` | Generally not needed; use structured concurrency |
| Completion handler closures | `async`/`await` functions |
| Delegate callbacks | `AsyncStream` wrapping the delegate |
| `DispatchQueue.concurrentPerform` | `withTaskGroup` with concurrency limiting |

## Combine-to-AsyncSequence Migration

| Combine | AsyncSequence Equivalent |
|---|---|
| `Publisher` | `AsyncSequence` |
| `sink { }` | `for await value in stream { }` |
| `map { }` | `.map { }` on AsyncSequence |
| `filter { }` | `.filter { }` on AsyncSequence |
| `flatMap { }` | Nested `for await` or `TaskGroup` |
| `combineLatest` | `AsyncAlgorithms.combineLatest()` (swift-async-algorithms package) |
| `merge` | `AsyncAlgorithms.merge()` |
| `debounce` | `AsyncAlgorithms.debounce(for:)` |
| `CurrentValueSubject` | `@Observable` property or actor-protected state |
| `PassthroughSubject` | `AsyncStream` with continuation |

## Swift 6.2 Features

### Default Main Actor Isolation

New projects can set `SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor` — all app code is `@MainActor` by default. Mark real non-UI work as `nonisolated` or `@concurrent`.

### @concurrent

Explicitly opt a function into running on the global concurrent executor:

```swift
@concurrent
func processImage(_ data: Data) -> UIImage {
    // Runs off the main actor even in a default-MainActor module
}
```

### Task.immediate

Start a task that runs synchronously up to its first suspension point:

```swift
let task = Task.immediate {
    // Runs synchronously here
    let data = try await fetchData()  // First suspension
    // Continues asynchronously after this
}
```

### isolated deinit

Deinitializers can now be isolated to an actor:

```swift
actor ResourceManager {
    var resource: Resource?

    isolated deinit {
        resource?.cleanup()  // Safe actor-isolated cleanup
    }
}
```

### Task priority escalation

```swift
await withTaskPriorityEscalationHandler {
    try await longRunningWork()
} onPriorityEscalated: { newPriority in
    logger.info("Priority escalated to \(newPriority)")
}
```

### Task naming

```swift
Task(name: "FetchUserProfile") {
    try await fetchProfile()
}
// Visible in Instruments and debugger
```

## Review Hotspots

When reviewing Swift concurrency code, grep for these patterns:

| Pattern | Risk |
|---|---|
| `DispatchQueue` | Legacy GCD — evaluate for migration |
| `Task.detached` | Usually wrong — check if structured alternative exists |
| `Task { }` inside loops | Creates unbounded unstructured tasks — use task group |
| `withCheckedContinuation` / `withCheckedThrowingContinuation` | Verify exactly-once resume on all paths |
| `AsyncStream` closure initializer | Prefer `makeStream(of:)` factory |
| `@unchecked Sendable` | Verify internal locking or value-type safety; document invariant |
| `MainActor.run { }` | Often unnecessary — check if caller is already main-isolated |
| `actor` with `await` inside methods | Check for reentrancy assumptions |
| Force unwraps after `await` inside actors | State may have changed |
| `nonisolated` on class methods | Verify the method truly doesn't touch isolated state |
| `Task { }` inside `.onAppear` | Code smell — use `.task { }` modifier instead (auto-cancels) |
| `Task { }` wrapping code that could be `async` | Code smell — make the calling function async instead of spawning |
| `Task { try await ... }` with no error handling | Swallowed errors — thrown errors are silently discarded |
| `catch { }` blocks | Check if `CancellationError` is being swallowed |
| `Task.sleep(nanoseconds:)` | Use `Task.sleep(for:)` instead |
| `DispatchQueue` | Legacy GCD — migrate to Swift Concurrency |
