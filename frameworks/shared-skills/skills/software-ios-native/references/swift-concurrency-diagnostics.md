# Swift Concurrency Diagnostics

Maps common Swift concurrency compiler errors and warnings to their fixes. For runtime crash triage, see [`swift-concurrency-crash-triage.md`](../software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md).

Primary docs:

- https://www.swift.org/migration/documentation/swift-6-migration-guide/commonproblems/
- https://developer.apple.com/documentation/swift/sendable

## Table of Contents

- [Diagnostic Fix Order](#diagnostic-fix-order)
- [Sending Risks Data Races](#sending-risks-data-races)
- [Static Property Not Concurrency-Safe](#static-property-not-concurrency-safe)
- [Capture of Non-Sendable Type in Sendable Closure](#capture-of-non-sendable-type-in-sendable-closure)
- [Protocol Conformance Crossing Isolation](#protocol-conformance-crossing-isolation)
- [Missing Await](#missing-await)
- [Isolated Conformance in Nonisolated Context](#isolated-conformance-in-nonisolated-context)
- [Call to MainActor Method in Synchronous Nonisolated Context](#call-to-mainactor-method-in-synchronous-nonisolated-context)
- [Mutable Capture in Sendable Closure](#mutable-capture-in-sendable-closure)

## Diagnostic Fix Order

For any concurrency diagnostic, try fixes in this order (smallest change first):

1. **Value type** — make the type a struct or enum if it has no reference semantics
2. **Sendable conformance** — add `Sendable` if the type is genuinely thread-safe (immutable or internally synchronized)
3. **Actor isolation** — wrap mutable state in an actor
4. **`sending` parameter** — use `sending` keyword (Swift 6.0+) if the value is transferred, not shared
5. **`@unchecked Sendable`** — last resort, only for types with proven internal locking; document the safety invariant and add a removal plan

Do NOT use `@preconcurrency` as a blanket silencer — it hides real issues and re-introduces the crash class.

## Sending Risks Data Races

**Diagnostic:** `Sending 'x' risks causing data races`

The compiler detected that a non-Sendable value crosses an isolation boundary.

**5-step fix:**

1. Can the type be a value type (struct/enum)? → Convert it
2. Is the type immutable after creation? → Add `Sendable` conformance
3. Does the type need mutable state? → Wrap it in an actor
4. Is the value transferred (moved), not shared? → Use `sending` parameter
5. Does the type have internal locking (e.g., `os_unfair_lock`, `Mutex`)? → `@unchecked Sendable` with documented invariant

```swift
// Example: sending a value across isolation
func process(_ item: sending Item) async {
    // 'sending' guarantees the caller gives up access
    await handler.handle(item)
}
```

## Static Property Not Concurrency-Safe

**Diagnostic:** `Static property 'x' is not concurrency-safe because it is nonisolated global shared mutable state`

**Fixes (choose one):**

```swift
// 1. Make it a constant (if truly immutable)
static let shared = MyType()

// 2. Isolate to an actor
@MainActor static var shared = MyType()

// 3. Use nonisolated(unsafe) for known-safe patterns (e.g., logger)
nonisolated(unsafe) static var logger = Logger()

// 4. Wrap in actor
actor Registry {
    static let shared = Registry()
    var items: [String: Item] = [:]
}
```

## Capture of Non-Sendable Type in Sendable Closure

**Diagnostic:** `Capture of 'x' with non-sendable type 'T' in '@Sendable' closure`

A `@Sendable` closure captures a value that isn't safe to share across threads.

**Fixes:**

```swift
// 1. Make the captured type Sendable
struct Config: Sendable { let url: URL }

// 2. Copy the value before capturing
let localCopy = nonSendableValue.copy()
Task { use(localCopy) }

// 3. If it's a class, consider making it an actor
actor DataStore { var items: [Item] = [] }

// 4. Use sending parameter if transferring ownership
func submit(_ work: sending Work) async { }
```

## Protocol Conformance Crossing Isolation

**Diagnostic:** `Main actor-isolated instance method 'x' cannot be used to satisfy nonisolated protocol requirement`

A `@MainActor` type is conforming to a protocol whose methods are not isolated.

**Fixes:**

```swift
// 1. Mark the protocol requirement as @MainActor (if you own the protocol)
@MainActor protocol MyDelegate {
    func didComplete()
}

// 2. Use nonisolated and hop to main actor (if you don't own the protocol)
nonisolated func delegateCallback() {
    Task { @MainActor in
        handleCallback()
    }
}

// 3. Use @preconcurrency on the protocol import (temporary bridge)
@preconcurrency import SomeFramework
// Document a removal plan — this hides real issues
```

## Missing Await

**Diagnostic:** `Expression is 'async' but is not marked with 'await'`

An async function call is missing its `await` keyword.

**Fix:** Add `await`. If the enclosing function is not `async`, either:

1. Make the enclosing function `async`
2. Wrap in `Task { }` (if appropriate for the context)

```swift
// WRONG
let data = fetchData()

// CORRECT
let data = await fetchData()
```

## Isolated Conformance in Nonisolated Context

**Diagnostic:** `Global-actor-isolated conformance of 'X' to 'Y' cannot be used in nonisolated context`

Swift 6.2 with default main-actor isolation can produce this when a globally-isolated conformance is used from a nonisolated generic context.

**Fixes:**

```swift
// 1. Make the consuming function also isolated
@MainActor func process<T: Protocol>(_ value: T) { }

// 2. Make the conformance nonisolated (if the protocol methods are safe)
extension MyType: @preconcurrency Protocol { }

// 3. Use existential instead of generic (eliminates static checking)
func process(_ value: any Protocol) { }
```

## Call to MainActor Method in Synchronous Nonisolated Context

**Diagnostic:** `Call to main actor-isolated method 'x' in a synchronous nonisolated context`

A `nonisolated` synchronous function is trying to call a `@MainActor` method.

**Fixes:**

```swift
// 1. Make the function async and await the call
func doWork() async {
    await mainActorMethod()
}

// 2. If you know you're on main (e.g., UIKit callback), assert
func callback() {
    MainActor.assumeIsolated {
        mainActorMethod()
    }
}

// 3. Make the calling function also @MainActor
@MainActor func doWork() {
    mainActorMethod()
}
```

## Mutable Capture in Sendable Closure

**Diagnostic:** `Mutation of captured var 'x' in concurrently-executing code`

A mutable variable is being mutated inside a concurrent context (task group, `@Sendable` closure).

**Fixes:**

```swift
// WRONG — mutating captured var in task group
var results: [Int] = []
await withTaskGroup(of: Int.self) { group in
    for id in ids { group.addTask { await fetch(id) } }
    for await result in group {
        results.append(result)  // Mutation of captured var
    }
}

// CORRECT — collect inside the group scope
let results = await withTaskGroup(of: Int.self) { group in
    for id in ids { group.addTask { await fetch(id) } }
    var collected: [Int] = []
    for await result in group {
        collected.append(result)  // Local var, not captured
    }
    return collected
}
```

## Common Bug Patterns (Compile-Time)

| Pattern | Problem | Fix |
|---|---|---|
| `@unchecked Sendable` on a class with mutable properties | Hides actual races | Use actor, value types, or `Mutex` |
| `@preconcurrency import` left in production | Silences real diagnostics | Remove after completing migration |
| `nonisolated` on method that accesses `self` state | Compiler may not catch all violations in Swift 5.x | Verify with strict concurrency checking enabled |
| `as! Sendable` cast | Type erasure, no compiler checking | Use proper Sendable conformance |
| Missing `try` on `Task.checkCancellation()` | Cancellation silently ignored | Always use `try Task.checkCancellation()` |
