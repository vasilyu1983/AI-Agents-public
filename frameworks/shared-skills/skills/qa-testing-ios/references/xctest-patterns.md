# XCTest Patterns and Best Practices

Testing patterns for XCTest and XCUITest in iOS development.

## Contents

- [Unit Testing Patterns](#unit-testing-patterns)
- [Mocking Patterns](#mocking-patterns)
- [UI Testing Patterns](#ui-testing-patterns)
- [Test Data Patterns](#test-data-patterns)
- [Performance Testing](#performance-testing)
- [Test Organization](#test-organization)
- [CI Integration](#ci-integration)
- [Related](#related)

---

## Unit Testing Patterns

### Basic Test Structure

```swift
import XCTest
@testable import MyApp

final class UserServiceTests: XCTestCase {
    // System under test
    var sut: UserService!
    var mockAPI: MockAPIClient!

    override func setUp() {
        super.setUp()
        mockAPI = MockAPIClient()
        sut = UserService(api: mockAPI)
    }

    override func tearDown() {
        sut = nil
        mockAPI = nil
        super.tearDown()
    }

    func testFetchUser_Success() async throws {
        // Given
        mockAPI.mockResponse = User(id: 1, name: "John")

        // When
        let user = try await sut.fetchUser(id: 1)

        // Then
        XCTAssertEqual(user.name, "John")
        XCTAssertEqual(mockAPI.requestCount, 1)
    }
}
```

### Async Testing

```swift
// Async/await (preferred)
func testAsyncOperation() async throws {
    let result = try await sut.performAsync()
    XCTAssertTrue(result.isSuccess)
}

// Expectations (legacy or complex scenarios)
func testCallbackOperation() {
    let expectation = expectation(description: "Callback received")

    sut.performWithCallback { result in
        XCTAssertNotNil(result)
        expectation.fulfill()
    }

    wait(for: [expectation], timeout: 5.0)
}

// Multiple expectations
func testMultipleCallbacks() {
    let first = expectation(description: "First callback")
    let second = expectation(description: "Second callback")

    sut.performSequence(
        onFirst: { first.fulfill() },
        onSecond: { second.fulfill() }
    )

    wait(for: [first, second], timeout: 10.0, enforceOrder: true)
}
```

### Error Testing

```swift
func testInvalidInput_ThrowsError() {
    XCTAssertThrowsError(try sut.validate(input: "")) { error in
        guard let validationError = error as? ValidationError else {
            XCTFail("Wrong error type")
            return
        }
        XCTAssertEqual(validationError, .emptyInput)
    }
}

func testAsyncError() async {
    do {
        _ = try await sut.fetchInvalidResource()
        XCTFail("Expected error to be thrown")
    } catch {
        XCTAssertTrue(error is NetworkError)
    }
}
```

---

## Mocking Patterns

### Protocol-Based Mocks

```swift
// Protocol
protocol APIClientProtocol {
    func fetch<T: Decodable>(endpoint: String) async throws -> T
}

// Mock implementation
class MockAPIClient: APIClientProtocol {
    var mockResponse: Any?
    var mockError: Error?
    var requestCount = 0
    var lastEndpoint: String?

    func fetch<T: Decodable>(endpoint: String) async throws -> T {
        requestCount += 1
        lastEndpoint = endpoint

        if let error = mockError {
            throw error
        }

        guard let response = mockResponse as? T else {
            throw MockError.invalidResponse
        }

        return response
    }
}
```

### Spy Pattern

```swift
class AnalyticsSpy: AnalyticsProtocol {
    var trackedEvents: [(name: String, params: [String: Any])] = []

    func track(event: String, parameters: [String: Any]) {
        trackedEvents.append((event, parameters))
    }

    func verifyTracked(_ event: String) -> Bool {
        trackedEvents.contains { $0.name == event }
    }
}
```

### Stub with Closure

```swift
class StubUserRepository: UserRepositoryProtocol {
    var fetchUserHandler: ((Int) async throws -> User)?

    func fetchUser(id: Int) async throws -> User {
        guard let handler = fetchUserHandler else {
            fatalError("fetchUserHandler not set")
        }
        return try await handler(id)
    }
}

// Usage in test
func testUserFetch() async throws {
    let stub = StubUserRepository()
    stub.fetchUserHandler = { id in
        User(id: id, name: "Test User")
    }

    let user = try await stub.fetchUser(id: 42)
    XCTAssertEqual(user.id, 42)
}
```

---

## UI Testing Patterns

### Basic UI Test

```swift
import XCTest

final class LoginUITests: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting"]
        app.launch()
    }

    func testSuccessfulLogin() {
        // Navigate
        app.buttons["loginButton"].tap()

        // Enter credentials
        let emailField = app.textFields["emailField"]
        emailField.tap()
        emailField.typeText("user@example.com")

        let passwordField = app.secureTextFields["passwordField"]
        passwordField.tap()
        passwordField.typeText("password123")

        // Submit
        app.buttons["submitButton"].tap()

        // Verify
        XCTAssertTrue(app.navigationBars["Dashboard"].waitForExistence(timeout: 5))
    }
}
```

### Page Object Pattern

```swift
// Page object
class LoginPage {
    let app: XCUIApplication

    init(app: XCUIApplication) {
        self.app = app
    }

    var emailField: XCUIElement {
        app.textFields["emailField"]
    }

    var passwordField: XCUIElement {
        app.secureTextFields["passwordField"]
    }

    var submitButton: XCUIElement {
        app.buttons["submitButton"]
    }

    var errorLabel: XCUIElement {
        app.staticTexts["errorLabel"]
    }

    func login(email: String, password: String) {
        emailField.tap()
        emailField.typeText(email)
        passwordField.tap()
        passwordField.typeText(password)
        submitButton.tap()
    }
}

// Usage in test
func testLogin() {
    let loginPage = LoginPage(app: app)
    loginPage.login(email: "user@example.com", password: "password")

    XCTAssertTrue(app.navigationBars["Dashboard"].waitForExistence(timeout: 5))
}
```

### Accessibility Identifiers

```swift
// In production code
emailTextField.accessibilityIdentifier = "emailField"
submitButton.accessibilityIdentifier = "submitButton"

// In SwiftUI
TextField("Email", text: $email)
    .accessibilityIdentifier("emailField")

Button("Submit") { submit() }
    .accessibilityIdentifier("submitButton")
```

### Waiting Patterns

```swift
// Wait for element to exist
func testElementAppears() {
    let element = app.buttons["asyncButton"]
    XCTAssertTrue(element.waitForExistence(timeout: 10))
}

// Wait for element to disappear
func testLoadingDisappears() {
    let spinner = app.activityIndicators["loadingSpinner"]

    // Wait for spinner to appear first
    XCTAssertTrue(spinner.waitForExistence(timeout: 5))

    // Then wait for it to disappear
    let disappeared = NSPredicate(format: "exists == false")
    let expectation = XCTNSPredicateExpectation(predicate: disappeared, object: spinner)
    wait(for: [expectation], timeout: 10)
}

// Custom predicate
func waitForEnabled(_ element: XCUIElement, timeout: TimeInterval = 5) {
    let predicate = NSPredicate(format: "isEnabled == true")
    let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
    wait(for: [expectation], timeout: timeout)
}
```

---

## Test Data Patterns

### Factory Pattern

```swift
enum UserFactory {
    static func make(
        id: Int = 1,
        name: String = "Test User",
        email: String = "test@example.com",
        isVerified: Bool = true
    ) -> User {
        User(id: id, name: name, email: email, isVerified: isVerified)
    }

    static func makeUnverified() -> User {
        make(isVerified: false)
    }

    static func makeList(count: Int) -> [User] {
        (1...count).map { make(id: $0, name: "User \($0)") }
    }
}

// Usage
func testUserDisplay() {
    let user = UserFactory.make(name: "John Doe")
    // test with user...
}
```

### JSON Fixtures

```swift
extension XCTestCase {
    func loadJSON<T: Decodable>(_ filename: String) throws -> T {
        let bundle = Bundle(for: type(of: self))
        guard let url = bundle.url(forResource: filename, withExtension: "json") else {
            throw FixtureError.fileNotFound(filename)
        }
        let data = try Data(contentsOf: url)
        return try JSONDecoder().decode(T.self, from: data)
    }
}

// Usage
func testParseResponse() throws {
    let response: APIResponse = try loadJSON("user_response")
    XCTAssertEqual(response.users.count, 3)
}
```

---

## Performance Testing

### Measure Block

```swift
func testParsingPerformance() {
    let largeJSON = loadLargeTestData()

    measure {
        _ = try? JSONDecoder().decode([User].self, from: largeJSON)
    }
}

// With metrics
func testScrollPerformance() {
    measure(metrics: [XCTCPUMetric(), XCTMemoryMetric()]) {
        // Perform operation
    }
}
```

### Baseline Testing

```swift
func testDatabaseQueryPerformance() {
    let options = XCTMeasureOptions()
    options.iterationCount = 10

    measure(options: options) {
        _ = database.fetchAllUsers()
    }
}
```

---

## Test Organization

### Test Naming Convention

```swift
// Pattern: test_[scenario]_[expectedResult]
func test_login_withValidCredentials_succeeds() { }
func test_login_withInvalidEmail_showsError() { }
func test_fetchUser_whenNetworkFails_throwsError() { }
```

### Test Categories with Tags

```swift
// In scheme settings or xcodebuild:
// -only-testing:MyAppTests/LoginTests
// -skip-testing:MyAppTests/SlowTests

// Or use test plans for different test suites
```

### Shared Setup

```swift
class BaseTestCase: XCTestCase {
    var mockAPI: MockAPIClient!

    override func setUp() {
        super.setUp()
        mockAPI = MockAPIClient()
        // Common setup
    }

    override func tearDown() {
        mockAPI = nil
        super.tearDown()
    }
}

class UserTests: BaseTestCase {
    func testUser() {
        // mockAPI already available
    }
}
```

---

## CI Integration

### xcodebuild Commands

```bash
# Run all tests
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -resultBundlePath TestResults.xcresult

# Run specific tests
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -only-testing:MyAppTests/LoginTests

# Skip slow tests
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -skip-testing:MyAppTests/PerformanceTests

# Parallel testing
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -parallel-testing-enabled YES \
  -parallel-testing-worker-count 4
```

### Test Results

```bash
# Generate JUnit XML (with xcbeautify)
xcodebuild test ... | xcbeautify --report junit

# View results
xcrun xcresulttool get --path TestResults.xcresult --format json
```

---

## Related

- [XCTest Documentation](https://developer.apple.com/documentation/xctest)
- [WWDC Testing Sessions](https://developer.apple.com/videos/testing)
- [Testing Your Apps in Xcode](https://developer.apple.com/documentation/xcode/testing-your-apps-in-xcode)
