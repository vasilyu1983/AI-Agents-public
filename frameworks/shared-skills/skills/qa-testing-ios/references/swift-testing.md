# Swift Testing Framework (Testing module)

Apple's modern testing framework (`import Testing`) available in recent Xcode toolchains. Uses Swift macros for expressive, concise tests.

**Official docs**: [Swift Testing](https://developer.apple.com/documentation/testing) | [Xcode Swift Testing](https://developer.apple.com/xcode/swift-testing)

## Contents

- [When to Use Swift Testing vs XCTest](#when-to-use-swift-testing-vs-xctest)
- [Basic Syntax](#basic-syntax)
- [Parameterized Tests](#parameterized-tests)
- [Test Organization](#test-organization)
- [Setup and Teardown](#setup-and-teardown)
- [Async and Concurrency](#async-and-concurrency)
- [Migration from XCTest](#migration-from-xctest)
- [CI Integration](#ci-integration)
- [Best Practices](#best-practices)
- [Resources](#resources)

---

## When to Use Swift Testing vs XCTest

| Use Case | Framework |
|----------|-----------|
| New unit tests | Swift Testing |
| New integration tests | Swift Testing |
| UI tests (XCUITest) | XCTest (required) |
| Performance tests | XCTest (required) |
| Existing XCTest suites | Keep or migrate gradually |

Swift Testing and XCTest can coexist in the same test target.

---

## Basic Syntax

### Test Functions

```swift
import Testing

// Basic test
@Test func userCanLogin() {
    let auth = AuthService()
    let result = auth.login(email: "user@example.com", password: "pass123")
    #expect(result.isSuccess)
}

// Async test
@Test func fetchUserReturnsData() async throws {
    let service = UserService()
    let user = try await service.fetchUser(id: 1)
    #expect(user.name == "John")
}

// Test with display name
@Test("Login fails with invalid email format")
func loginInvalidEmail() {
    let auth = AuthService()
    let result = auth.login(email: "not-an-email", password: "pass")
    #expect(result.error == .invalidEmail)
}
```

### Assertions with #expect

```swift
// Basic equality
#expect(user.name == "John")
#expect(count > 0)
#expect(items.isEmpty)

// Optional handling
#expect(user != nil)
let unwrapped = try #require(optionalValue)  // Unwrap or fail

// Error expectations
#expect(throws: ValidationError.self) {
    try validator.validate(input: "")
}

// Specific error
#expect(throws: NetworkError.timeout) {
    try await api.fetch(timeout: 0)
}
```

### Comparison: XCTest vs Swift Testing

```swift
// XCTest
XCTAssertEqual(user.name, "John")
XCTAssertTrue(user.isActive)
XCTAssertNotNil(user.email)
XCTAssertThrowsError(try validate("")) { error in
    XCTAssertEqual(error as? ValidationError, .empty)
}

// Swift Testing
#expect(user.name == "John")
#expect(user.isActive)
#expect(user.email != nil)
#expect(throws: ValidationError.empty) {
    try validate("")
}
```

---

## Parameterized Tests

Run the same test logic with multiple inputs.

```swift
// Basic parameterized test
@Test(arguments: ["apple", "banana", "cherry"])
func fruitIsValid(_ fruit: String) {
    #expect(FruitValidator.isValid(fruit))
}

// Multiple parameters
@Test(arguments: [
    (email: "user@example.com", valid: true),
    (email: "invalid", valid: false),
    (email: "", valid: false),
    (email: "user@domain.co.uk", valid: true)
])
func emailValidation(email: String, valid: Bool) {
    #expect(EmailValidator.isValid(email) == valid)
}

// Combining sequences
@Test(arguments: 1...5, ["USD", "EUR", "GBP"])
func currencyConversion(amount: Int, currency: String) async throws {
    let result = try await converter.convert(amount: amount, to: currency)
    #expect(result > 0)
}

// Using zip for paired arguments
@Test(arguments: zip(["admin", "user", "guest"], [true, false, false]))
func adminAccess(role: String, hasAccess: Bool) {
    let user = User(role: role)
    #expect(user.canAccessAdmin == hasAccess)
}
```

---

## Test Organization

### Suites (Grouping Tests)

```swift
import Testing

@Suite("Authentication")
struct AuthTests {
    @Test func loginSucceeds() { }
    @Test func logoutClearsSession() { }
}

@Suite("User Management")
struct UserTests {
    @Suite("Profile")
    struct ProfileTests {
        @Test func updateName() { }
        @Test func updateEmail() { }
    }

    @Suite("Settings")
    struct SettingsTests {
        @Test func changePassword() { }
    }
}
```

### Tags

```swift
extension Tag {
    @Tag static var critical: Self
    @Tag static var slow: Self
    @Tag static var network: Self
}

@Test(.tags(.critical))
func paymentProcessing() { }

@Test(.tags(.slow, .network))
func syncLargeDataset() async { }

// Run only tagged tests via Xcode or xcodebuild
```

### Traits

```swift
// Disabled test
@Test(.disabled("Waiting for API v2"))
func newFeatureTest() { }

// Conditionally enabled
@Test(.enabled(if: ProcessInfo.processInfo.environment["CI"] != nil))
func ciOnlyTest() { }

// Timeout
@Test(.timeLimit(.minutes(2)))
func longRunningOperation() async { }

// Bug reference
@Test(.bug("https://github.com/org/repo/issues/123", "Flaky on iOS 17"))
func flakyTest() { }
```

---

## Setup and Teardown

```swift
@Suite struct DatabaseTests {
    var database: TestDatabase

    // Called before each test
    init() async throws {
        database = try await TestDatabase.create()
    }

    // Called after each test
    deinit {
        database.destroy()
    }

    @Test func insertUser() async throws {
        try await database.insert(User(name: "John"))
        #expect(await database.count() == 1)
    }
}
```

---

## Async and Concurrency

```swift
// Async tests run with full Swift Concurrency support
@Test func fetchMultipleUsers() async throws {
    async let user1 = api.fetchUser(id: 1)
    async let user2 = api.fetchUser(id: 2)

    let users = try await [user1, user2]
    #expect(users.count == 2)
}

// Actor isolation
@Test func actorState() async {
    let counter = Counter()  // actor
    await counter.increment()
    await counter.increment()
    #expect(await counter.value == 2)
}
```

---

## Migration from XCTest

### Gradual Migration Strategy

1. **New tests**: Write in Swift Testing
2. **Existing XCTest**: Keep working, migrate when touched
3. **UI tests**: Keep in XCTest (required)
4. **Performance tests**: Keep in XCTest (required)

### Side-by-Side Example

```swift
// Same test target can have both:

// XCTest (existing)
import XCTest

class LegacyTests: XCTestCase {
    func testOldFeature() {
        XCTAssertTrue(feature.works)
    }
}

// Swift Testing (new)
import Testing

@Test func newFeature() {
    #expect(feature.works)
}
```

### Key Differences

| Aspect | XCTest | Swift Testing |
|--------|--------|---------------|
| Test marker | `func test...()` | `@Test` |
| Assertions | `XCTAssert*` (40+ functions) | `#expect`, `#require` |
| Async | `async` or expectations | Native `async` |
| Grouping | Classes inheriting XCTestCase | `@Suite` structs |
| Parameterized | Manual loops | `@Test(arguments:)` |
| Parallel | Opt-in | Default |

---

## CI Integration

```bash
# Run Swift Testing tests (same as XCTest)
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=latest'

# Filter by tag (Xcode 16+)
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=latest' \
  -testPlan CriticalTests
```

### Test Plans for Tags

Create an `.xctestplan` file to run tests by tag:

```json
{
  "configurations": [{
    "name": "Critical Tests",
    "options": {
      "testExecutionOrdering": "random"
    }
  }],
  "testTargets": [{
    "target": { "name": "MyAppTests" },
    "selectedTests": ["tag:critical"]
  }]
}
```

---

## Best Practices

### Do

- Use `#expect` for all assertions (simpler, better diagnostics)
- Use `#require` to unwrap optionals and fail fast
- Use parameterized tests to reduce duplication
- Use tags to categorize tests (critical, slow, network)
- Use suites to organize related tests
- Set timeouts for async tests that could hang

### Avoid

- Mixing XCTest assertions in Swift Testing tests
- Using Swift Testing for UI tests (not supported)
- Using Swift Testing for performance tests (not supported)
- Overusing parameterized tests (keep readable)

---

## Resources

- [Apple Swift Testing Documentation](https://developer.apple.com/documentation/testing)
- [Swift Testing Overview](https://developer.apple.com/xcode/swift-testing)
- [WWDC24: Meet Swift Testing](https://developer.apple.com/videos/play/wwdc2024/10179/)
- [Migrating from XCTest](https://developer.apple.com/documentation/testing/migratingfromxctest)
