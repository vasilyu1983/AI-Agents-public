# XCTest Patterns

XCTest remains the baseline for UI tests, performance tests, and many existing iOS suites.

Primary docs:

- https://developer.apple.com/documentation/xctest
- https://developer.apple.com/documentation/xcode/testing-your-apps-in-xcode

## Table of Contents

- [Where XCTest Still Fits Best](#where-xctest-still-fits-best)
- [Unit Test Structure](#unit-test-structure)
- [Async And Errors](#async-and-errors)
- [Mocking Guidance](#mocking-guidance)
- [Performance Tests](#performance-tests)
- [CLI Patterns](#cli-patterns)
- [Review Checklist](#review-checklist)

## Where XCTest Still Fits Best

- XCUITest UI automation
- performance measurements
- legacy or mature test targets where migration is unnecessary
- mixed Swift and Objective-C test suites

## Unit Test Structure

```swift
import XCTest
@testable import MyApp

final class UserServiceTests: XCTestCase {
    private var sut: UserService!
    private var api: MockAPIClient!

    override func setUp() {
        super.setUp()
        api = MockAPIClient()
        sut = UserService(api: api)
    }

    override func tearDown() {
        sut = nil
        api = nil
        super.tearDown()
    }

    func testFetchUser_success() async throws {
        api.mockResponse = User(id: 1, name: "John")

        let user = try await sut.fetchUser(id: 1)

        XCTAssertEqual(user.name, "John")
        XCTAssertEqual(api.requestCount, 1)
    }
}
```

## Async And Errors

```swift
func testCallbackOperation() {
    let exp = expectation(description: "callback")

    sut.performWithCallback { result in
        XCTAssertNotNil(result)
        exp.fulfill()
    }

    wait(for: [exp], timeout: 5)
}

func testInvalidInput_throws() {
    XCTAssertThrowsError(try sut.validate(input: "")) { error in
        XCTAssertEqual(error as? ValidationError, .emptyInput)
    }
}
```

Prefer native `async` tests where the code under test already exposes async APIs.

## Mocking Guidance

- prefer protocol seams over subclass hacks
- use spies for side-effect verification
- use lightweight stubs for deterministic inputs
- avoid sharing mutable mocks across tests

## Performance Tests

```swift
func testSearchPerformance() {
    measure {
        _ = sut.search(query: "coffee")
    }
}
```

Use XCTest for performance testing until Apple documents an equivalent in Swift Testing for your use case.

## CLI Patterns

```bash
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=<simulator-name>,OS=latest' \
  -only-testing:MyAppTests/UserServiceTests/testFetchUser_success \
  -resultBundlePath TestResults.xcresult
```

## Review Checklist

- tests are deterministic and isolated
- setup and teardown own all mutable state
- assertions match the real contract, not implementation trivia
- async tests fail quickly when callbacks or tasks never complete
