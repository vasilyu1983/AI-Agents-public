# Swift Testing

Apple's `import Testing` framework for modern unit and integration tests.

Primary docs:

- https://developer.apple.com/documentation/testing
- https://developer.apple.com/documentation/testing/migratingfromxctest
- https://developer.apple.com/videos/play/wwdc2024/10179/
- https://developer.apple.com/videos/play/wwdc2024/10195/
- https://developer.apple.com/documentation/xcode-release-notes/xcode-26-release-notes

## Table of Contents

- [Positioning](#positioning)
- [Basic Syntax](#basic-syntax)
- [Suite Structure](#suite-structure)
- [Assertions: #expect vs #require](#assertions-expect-vs-require)
- [Error Testing](#error-testing)
- [Parameterized Tests](#parameterized-tests)
- [Tags and Traits](#tags-and-traits)
- [Async Test Patterns](#async-test-patterns)
- [Confirmations](#confirmations)
- [Swift 6.2 Features](#swift-62-features)
- [Xcode 26 Additions](#xcode-26-additions)
- [XCTest Migration](#xctest-migration)
- [Custom Assertion Helpers](#custom-assertion-helpers)
- [CLI Notes](#cli-notes)
- [Review Checklist](#review-checklist)

## Positioning

Prefer Swift Testing for:

- new unit tests
- new integration tests
- parameterized tests
- trait-based organization such as tags, time limits, and conditional enablement

Keep using XCTest for:

- UI tests (Swift Testing does NOT support UI tests)
- performance tests
- mature suites where a migration would not pay for itself yet

Swift Testing and XCTest can coexist in the same project. Only `import Testing` in test targets — never in production code.

## Basic Syntax

```swift
import Testing

@Test func userCanLogin() {
    let auth = AuthService()
    let result = auth.login(email: "user@example.com", password: "pass123")
    #expect(result.isSuccess)
}

@Test("Login fails with invalid email")
func invalidEmail() {
    let auth = AuthService()
    let result = auth.login(email: "bad", password: "pass123")
    #expect(result.error == .invalidEmail)
}
```

No `test` prefix needed — `@Test` marks the function. Display names are optional.

## Suite Structure

- Prefer structs over classes for test suites (value semantics, fresh state per test)
- `@Suite` is unnecessary unless you need a display name or traits on the suite
- Use `init()` and `deinit` instead of `setUp()`/`tearDown()`
- All suite initializers must be parameterless
- `async` and `throws` are allowed on `init` and test functions
- Each type in its own file, matching production code structure
- Parallel execution is the default — write tests that don't share mutable state

```swift
struct AuthTests {
    let service: AuthService

    init() async throws {
        service = try await AuthService.configured()
    }

    @Test func loginSucceeds() async throws {
        let result = try await service.login(email: "user@test.com", password: "pass")
        #expect(result.isSuccess)
    }
}
```

## Assertions: #expect vs #require

| Macro | Use When | Behavior on Failure |
|---|---|---|
| `#expect(condition)` | Validating outcomes | Records failure, test continues |
| `try #require(condition)` | Preconditions that must hold for the test to be meaningful | Throws, test stops immediately |
| `try #require(optionalValue)` | Unwrapping optionals | Returns unwrapped value or throws |

```swift
@Test func userProfile() throws {
    let user = try #require(fetchUser(id: 1))  // Unwraps or stops
    #expect(user.name == "John")               // Continues on failure
    #expect(user.isActive)                     // Still runs even if name check failed
}
```

**Never use `!` to negate inside `#expect` or `#require`** — it defeats the macro's ability to expand and display the actual vs expected values:

```swift
// WRONG — macro can't show what went wrong
#expect(!result.isEmpty)

// CORRECT — macro shows the actual value
#expect(result.isEmpty == false)
// Or better, test what you actually want
#expect(result.count > 0)
```

## Error Testing

```swift
// Expect a specific error
@Test func invalidInputThrows() {
    #expect(throws: ValidationError.invalidEmail) {
        try validate(email: "bad")
    }
}

// Expect a specific error type (less precise — prefer specific error)
@Test func networkErrorType() {
    #expect(throws: NetworkError.self) {
        try fetch(url: badURL)
    }
}

// Never use broad Error.self — it passes on ANY error
// #expect(throws: Error.self) { ... }  // TOO BROAD — avoid

// Expect NO error is thrown
@Test func validInputDoesNotThrow() {
    #expect(throws: Never.self) {
        try validate(email: "user@test.com")
    }
}

// Capture thrown error for detailed validation (Swift 6.2+)
@Test func captureError() throws {
    let error = try #require(throws: ValidationError.self) {
        try validate(email: "bad")
    }
    #expect(error.field == "email")
    #expect(error.message.contains("invalid"))
}

// For do/catch patterns, use Issue.record()
@Test func manualErrorCheck() {
    do {
        try riskyOperation()
        Issue.record("Expected an error but none was thrown")
    } catch let error as SpecificError {
        #expect(error.code == 42)
    } catch {
        Issue.record("Unexpected error type: \(error)")
    }
}
```

## Parameterized Tests

Parameterized tests run the same test body with different inputs. Max 2 collections form a **Cartesian product**:

```swift
@Test(arguments: ["user@example.com", "admin@test.com"], [true, false])
func emailWithFlag(email: String, active: Bool) {
    // Runs 4 times: every combination
}
```

For **pairwise** (not Cartesian), use `zip()`:

```swift
@Test(arguments: zip(
    ["user@example.com", "bad", ""],
    [true, false, false]
))
func emailValidation(email: String, expectedValid: Bool) {
    // Runs 3 times: paired inputs
    #expect(EmailValidator.isValid(email) == expectedValid)
}
```

Rules:

- `@available` goes on individual test functions, not on the suite type
- If a test has no `#expect` or `#require`, it is assumed to pass (useful for "does not crash" tests)
- `withKnownIssue { }` marks a test as expected to fail — use `isIntermittent: true` for flaky tests

```swift
@Test func knownBug() {
    withKnownIssue {
        #expect(brokenFunction() == expected)
    }
}

@Test func flakyNetworkTest() {
    withKnownIssue(isIntermittent: true) {
        #expect(try await fetchWithRetry() != nil)
    }
}
```

## Tags and Traits

Define tags for test categorization:

```swift
extension Tag {
    @Tag static var networking: Self
    @Tag static var slow: Self
    @Tag static var edgeCase: Self
    @Tag static var smoke: Self
}
```

Apply tags and traits:

```swift
@Suite("Authentication")
struct AuthTests {
    @Test(.tags(.networking, .smoke))
    func loginSucceeds() async { }

    @Test(.tags(.slow), .timeLimit(.minutes(2)))
    func refreshAllTokens() async { }

    @Test(.bug("https://github.com/org/repo/issues/123", "Flaky on CI"))
    func intermittentFailure() { }
}
```

### Trait Reference

| Trait | Purpose |
|---|---|
| `.tags(...)` | Categorization for filtering |
| `.timeLimit(.minutes(N))` | Maximum execution time (**only `.minutes()`, no `.seconds()`**) |
| `.bug(url, title)` | Link to tracked issue |
| `.disabled(comment)` | Skip with explanation |
| `.enabled(if: condition)` | Conditional execution |
| `.serialized` | **Only works on parameterized tests** — forces sequential execution of parameter iterations within one test |

**`.serialized` does NOT serialize an entire suite.** It only applies to parameterized tests to run their iterations sequentially instead of in parallel.

## Async Test Patterns

Just make the test function `async`:

```swift
@Test func fetchUser() async throws {
    let user = try await api.fetchUser(id: 1)
    #expect(user.name == "John")
}
```

### Actor isolation in tests

```swift
// Test that needs main actor
@Test @MainActor func uiUpdate() {
    let vm = ViewModel()
    vm.refresh()
    #expect(vm.isLoading)
}

// Whole suite on main actor
@Suite @MainActor struct ViewModelTests { }

// Testing actor state
@Test func actorState() async {
    let cache = await DataCache()
    await cache.store("key", value: data)
    let result = await cache.fetch("key")
    #expect(result == data)
}
```

### Testing pre-concurrency code

```swift
@Test func legacyCallback() async {
    let result = await withCheckedContinuation { continuation in
        legacyService.fetch { data in
            continuation.resume(returning: data)
        }
    }
    #expect(result != nil)
}
```

### Mocking networking

```swift
protocol URLSessionProtocol {
    func data(for request: URLRequest) async throws -> (Data, URLResponse)
}

extension URLSession: URLSessionProtocol { }

struct MockSession: URLSessionProtocol {
    var responseData: Data
    var statusCode: Int = 200

    func data(for request: URLRequest) async throws -> (Data, URLResponse) {
        let response = HTTPURLResponse(url: request.url!, statusCode: statusCode, httpVersion: nil, headerFields: nil)!
        return (responseData, response)
    }
}
```

## Confirmations

`confirmation()` is Swift Testing's way to verify that something happens asynchronously:

```swift
// Verify a callback fires exactly once
@Test func notificationFired() async {
    await confirmation { confirmed in
        NotificationCenter.default.addObserver(
            forName: .didUpdate, object: nil, queue: nil
        ) { _ in
            confirmed()
        }
        await triggerUpdate()
        await Task.yield()  // Give notification time to fire
    }
}

// Verify something happens exactly N times
@Test func batchProcessing() async {
    await confirmation(expectedCount: 3) { confirmed in
        processor.onItemProcessed = { confirmed() }
        await processor.process(items: threeItems)
    }
}

// Verify something NEVER happens
@Test func noUnexpectedCalls() async {
    await confirmation(expectedCount: 0) { confirmed in
        service.onError = { _ in confirmed() }  // Should not fire
        await service.performSafeOperation()
    }
}
```

**All async work must complete before the closure returns.** If the closure returns before the expected count is reached, the test fails.

Range-based confirmations (Swift 6.2+):

```swift
await confirmation(expectedCount: 5...10) { confirmed in
    // Must fire between 5 and 10 times
}

await confirmation(expectedCount: ...3) { confirmed in
    // Must fire at most 3 times
}
```

### Confirmation with actor isolation

Both `confirmation` and `withKnownIssue` accept an `isolation:` parameter for actor-isolated contexts.

## Swift 6.2 Features

### Raw identifiers for natural test names

```swift
@Test func `user can log in with valid credentials`() { }
@Test func `empty cart shows zero total`() { }
```

### Test scoping traits

Custom traits that set up and tear down shared state:

```swift
struct DatabaseTrait: TestTrait, TestScoping {
    func provideScope(for test: Test, testCase: Test.Case?, performing body: @Sendable () async throws -> Void) async throws {
        try await Database.withTestDatabase { db in
            DatabaseContext.$current.withValue(db) {
                try await body()
            }
        }
    }
}

extension TestTrait where Self == DatabaseTrait {
    static var database: Self { .init() }
}

@Test(.database) func fetchUsers() async {
    // DatabaseContext.$current is set
}
```

### Exit tests

Test that code calls `precondition`, `fatalError`, or `exit`:

```swift
@Test func preconditionFires() async {
    await #expect(processExitsWith: .failure) {
        preconditionFailure("Expected failure")
    }
}
```

### Attachments

Record diagnostic data on test failure:

```swift
@Test func dataIntegrity() throws {
    let data = try loadTestData()
    Attachment.record(data, named: "test-input.json")
    #expect(validate(data))
}
```

Supports `String`, `Data`, and any `Encodable` type. Image type support (`UIImage`, `CGImage`, etc.) was added in Xcode 26 — see `## Xcode 26 Additions` below.

### Error capture from throws assertions

```swift
// New: #expect(throws:) and #require(throws:) return the error
let error = try #require(throws: APIError.self) {
    try callAPI()
}
#expect(error.statusCode == 404)
```

## Xcode 26 Additions

### Image Attachments

Swift Testing in Xcode 26 supports attaching image types directly to test reports. Use this for snapshot diffs, rendering assertions, and Vision framework outputs:

```swift
import UIKit

@Test func renderOutput() throws {
    let image: UIImage = try renderChart()
    Attachment.record(image, named: "chart-output.png")
    #expect(image.size.width > 0)
}
```

Supported types: `CGImage`, `NSImage`, `UIImage`, `CIImage`. Limitation: `UIImage` attachments do not work in Mac Catalyst test targets — use `UIImage.cgImage` as a workaround in those targets.

### Issue Severity Levels

Record issues with a severity to distinguish between critical and informational failures:

```swift
Issue.record("Unexpected response format", severity: .warning)
Issue.record("Missing required field", severity: .error)
```

Useful for large suites where not every deviation warrants a hard failure.

### XCTest Interop Now Opt-In (Breaking for CI)

XCTest interoperability with Swift Testing is off by default in Xcode 26. Projects that ran XCTest-based tests through the Swift Testing runner in previous versions must now explicitly opt in.

To preserve the old behavior, set this in your test plan or environment:

```
SWIFT_TESTING_XCTEST_INTEROP_MODE=limited
```

Without this, XCTest test cases that were implicitly discovered by the Swift Testing runner will no longer run. Check your CI xcresult output for unexpected test-count drops when upgrading to Xcode 26.

### Mixing Assertion Frameworks Now Warns at Runtime (Xcode 26.4+)

In Xcode 26.4, calling an `XCTAssert*` function inside a `@Test` function now emits a runtime warning instead of silently passing. This makes the previously invisible failure mode (see `## Testing Traps`) visible. The behavior was always wrong; now it is loud.

---

## XCTest Migration

### Assertion Mapping

| XCTest | Swift Testing |
|---|---|
| `XCTAssertTrue(x)` | `#expect(x)` |
| `XCTAssertFalse(x)` | `#expect(!x)` |
| `XCTAssertEqual(a, b)` | `#expect(a == b)` |
| `XCTAssertNotEqual(a, b)` | `#expect(a != b)` |
| `XCTAssertNil(x)` | `#expect(x == nil)` |
| `XCTAssertNotNil(x)` | `#expect(x != nil)` or `try #require(x)` |
| `XCTUnwrap(x)` | `try #require(x)` |
| `XCTAssertThrowsError(expr)` | `#expect(throws: ErrorType.self) { expr }` |
| `XCTAssertNoThrow(expr)` | `#expect(throws: Never.self) { expr }` |
| `XCTFail("msg")` | `Issue.record("msg")` |
| `XCTAssertIdentical(a, b)` | `#expect(a === b)` |
| `XCTAssertGreaterThan(a, b)` | `#expect(a > b)` |
| `XCTAssertLessThan(a, b)` | `#expect(a < b)` |

### Float Tolerance

No built-in float tolerance in Swift Testing. Use Swift Numerics:

```swift
import Numerics

#expect(result.isApproximatelyEqual(to: expected, absoluteTolerance: 0.001))
```

Do not add the `swift-numerics` library without asking permission first.

### 4-Step Conversion Process

1. **Structure**: Replace `XCTestCase` class with struct, `@Test` on methods, `init` replaces `setUp`
2. **Parameterize**: Find repeated test bodies with different inputs → `@Test(arguments:)`
3. **Preconditions**: Replace early `XCTAssertNotNil` + force unwrap chains with `try #require`
4. **Traits**: Add `.tags`, `.bug`, `.timeLimit`, `.disabled` where they add selection value

### What NOT to Migrate

- UI tests (XCUITest) — Swift Testing has no UI test support
- Performance tests (`measure { }`) — keep in XCTest
- Tests using `XCTestExpectation` for complex async — migrate only if `confirmation()` covers the pattern
- Stable suites with no active development — migration cost > benefit

## Custom Assertion Helpers

When building reusable assertion helpers, propagate source location so failures point to the call site:

```swift
func expectValid(_ user: User, sourceLocation: SourceLocation = #_sourceLocation) {
    #expect(user.name.isEmpty == false, sourceLocation: sourceLocation)
    #expect(user.email.contains("@"), sourceLocation: sourceLocation)
}
```

For readable parameterized test output, conform to `CustomTestStringConvertible` (only in test targets):

```swift
extension User: CustomTestStringConvertible {
    var testDescription: String { "\(name) (\(email))" }
}
```

## Testing Traps and Edge Cases

### Parallel execution breaks shared state

Swift Testing runs tests in parallel by default. These shared resources will cause flaky or crashing tests:

- **Shared UserDefaults suite** — tests writing/reading the same keys interfere. Use a unique suite name per test via `init()`.
- **Keychain items** — persist across runs. Clean up in `deinit` or use test-specific keys.
- **File system** — tests writing to the same path race. Use unique temp directories per test.
- **Singletons / static state** — any `static var` shared across tests is a race. Use dependency injection instead.
- **Database / SwiftData ModelContext** — tests sharing a context corrupt each other. Create a fresh in-memory container per test.

`.serialized` only works on parameterized tests — it does NOT serialize a whole suite.

### confirmation() has no built-in timeout

If the confirmed event never fires, `confirmation()` hangs until the suite-level `.timeLimit` kicks in (which may be very long). Always pair with `.timeLimit(.minutes(1))`:

```swift
@Test(.timeLimit(.minutes(1)))
func eventFires() async {
    await confirmation { confirmed in
        service.onComplete = { confirmed() }
        await service.start()
    }
}
```

### Mixing XCTest and Swift Testing assertions silently fails (loudly fails in Xcode 26.4+)

If a file imports both `XCTest` and `Testing`, `XCTAssert*` calls inside a `@Test` function do not record failures in the Swift Testing runner — they silently pass. In Xcode 26.4+, this now emits a runtime warning instead of silently passing, making the problem visible. Never mix assertion frameworks in the same function regardless of Xcode version.

### @Test must be top-level or type-level

`@Test` functions nested inside other functions or closures are silently ignored by the test runner. Always declare test functions at the struct/class level.

## Test Design Principles

### FIRST

Good tests follow the FIRST principles:

- **Fast** — tests should run in milliseconds, not seconds. Move I/O behind protocol boundaries.
- **Isolated** — no shared mutable state between tests. Each test gets fresh state via `init()`.
- **Repeatable** — same result every run, regardless of order, time of day, or network state.
- **Self-validating** — pass/fail is determined by `#expect` / `#require`, not manual inspection.
- **Timely** — written alongside (or before) the production code, not as an afterthought.

### Test Generation Heuristics

When writing tests for a new function, cover these categories:

1. **Happy path** — the intended use case with valid input
2. **Boundary values** — empty collections, zero, max, nil, first/last
3. **Invalid input** — malformed data, out-of-range values, wrong types
4. **Concurrency** — async behavior, cancellation, actor isolation

### What Not to Test Directly

- **Never test SwiftUI views directly** — test the view model or model layer instead. Views are rendering infrastructure.
- **Avoid timing-based tests** — tests that depend on `Task.sleep`, wall-clock time, or animation duration are flaky by nature. Use `confirmation()` for async events.

### Testing Cancellation

Verify that production code properly checks for cancellation:

```swift
@Test func cancellationStopsProcessing() async {
    let task = Task {
        try await processor.processLargeDataset(items)
    }
    // Give the task time to start
    await Task.yield()
    task.cancel()

    do {
        _ = try await task.value
        Issue.record("Expected CancellationError")
    } catch is CancellationError {
        // Expected
    } catch {
        Issue.record("Unexpected error: \(error)")
    }
}
```

## CLI Notes

Swift Testing runs through the same `xcodebuild test` flow as XCTest. The useful CLI controls stay the same:

- `-testPlan`
- `-only-testing`
- `-retry-tests-on-failure`
- `-run-tests-until-failure`
- `-resultBundlePath`

## Review Checklist

- `#require` is used for preconditions that must hold; `#expect` for all other assertions
- Parameterized tests are used where the same logic is tested with different inputs
- Tags add real selection value for CI filtering, not just decoration
- `.serialized` is only applied to parameterized tests, never suites
- Async tests do not hide timeouts or hangs
- Error assertions use specific error values/types, not broad `Error.self`
- The suite still has a clear path for CLI execution and CI filtering
- No `XCTAssert*` calls are mixed into Swift Testing tests
- `CustomTestStringConvertible` is only in test targets, never production
