# iOS App Template (TDD with XCTest + ViewInspector)

Complete production-ready iOS application template focused on Test-Driven Development (TDD) using XCTest, ViewInspector for SwiftUI testing, and comprehensive test coverage patterns.

---

## Tech Stack

- **Language**: Swift 6.1+
- **UI Framework**: SwiftUI
- **Architecture**: MVVM (Testable)
- **Unit Testing**: Swift Testing (preferred) + XCTest (legacy/UI)
- **UI Testing**: ViewInspector + XCTest UI
- **Mocking**: Protocol-based DI + Mock Services
- **Code Coverage**: Xcode Coverage Tools
- **CI/CD**: GitHub Actions / Xcode Cloud
- **Test Frameworks**: Quick/Nimble (optional)

---

## Project Structure

```
YourApp/
├── YourApp/
│   ├── App/
│   │   ├── YourAppApp.swift
│   │   └── ContentView.swift
│   ├── Models/
│   │   ├── User.swift
│   │   └── Post.swift
│   ├── ViewModels/
│   │   ├── UserViewModel.swift
│   │   └── PostViewModel.swift
│   ├── Views/
│   │   ├── UserListView.swift
│   │   └── PostDetailView.swift
│   ├── Services/
│   │   ├── Protocols/
│   │   │   ├── APIServiceProtocol.swift
│   │   │   ├── AuthServiceProtocol.swift
│   │   │   └── StorageServiceProtocol.swift
│   │   ├── APIService.swift
│   │   ├── AuthService.swift
│   │   └── StorageService.swift
│   └── Utilities/
│       ├── DependencyContainer.swift
│       └── Extensions/
└── YourAppTests/
    ├── ModelTests/
    │   ├── UserTests.swift
    │   └── PostTests.swift
    ├── ViewModelTests/
    │   ├── UserViewModelTests.swift
    │   └── PostViewModelTests.swift
    ├── ViewTests/
    │   ├── UserListViewTests.swift
    │   └── PostDetailViewTests.swift
    ├── ServiceTests/
    │   ├── APIServiceTests.swift
    │   └── AuthServiceTests.swift
    ├── Mocks/
    │   ├── MockAPIService.swift
    │   ├── MockAuthService.swift
    │   └── MockStorageService.swift
    └── Helpers/
        ├── TestHelpers.swift
        └── XCTestCase+Extensions.swift
```

---

## 1. Protocol-Based Dependency Injection

**YourApp/Services/Protocols/APIServiceProtocol.swift**

```swift
import Foundation
import Combine

protocol APIServiceProtocol {
    func getUsers() async throws -> [User]
    func getUser(id: String) async throws -> User
    func createUser(_ user: CreateUserRequest) async throws -> User
    func deleteUser(id: String) async throws
}
```

**YourApp/Services/APIService.swift**

```swift
import Foundation

class APIService: APIServiceProtocol {
    private let baseURL: String
    private let session: URLSession

    init(baseURL: String = "https://api.example.com", session: URLSession = .shared) {
        self.baseURL = baseURL
        self.session = session
    }

    func getUsers() async throws -> [User] {
        guard let url = URL(string: "\(baseURL)/users") else {
            throw APIError.invalidURL
        }

        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode([User].self, from: data)
    }

    func getUser(id: String) async throws -> User {
        guard let url = URL(string: "\(baseURL)/users/\(id)") else {
            throw APIError.invalidURL
        }

        let (data, _) = try await session.data(from: url)
        return try JSONDecoder().decode(User.self, from: data)
    }

    func createUser(_ user: CreateUserRequest) async throws -> User {
        guard let url = URL(string: "\(baseURL)/users") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(user)

        let (data, _) = try await session.data(for: request)
        return try JSONDecoder().decode(User.self, from: data)
    }

    func deleteUser(id: String) async throws {
        guard let url = URL(string: "\(baseURL)/users/\(id)") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "DELETE"

        _ = try await session.data(for: request)
    }
}

enum APIError: Error, Equatable {
    case invalidURL
    case invalidResponse
    case decodingError
}
```

---

## 2. Dependency Container

**YourApp/Utilities/DependencyContainer.swift**

```swift
import Foundation

class DependencyContainer {
    static let shared = DependencyContainer()

    // Services
    lazy var apiService: APIServiceProtocol = APIService()
    lazy var authService: AuthServiceProtocol = AuthService()
    lazy var storageService: StorageServiceProtocol = StorageService()

    private init() {}

    // For testing - allows injecting mocks
    func configure(
        apiService: APIServiceProtocol? = nil,
        authService: AuthServiceProtocol? = nil,
        storageService: StorageServiceProtocol? = nil
    ) {
        if let apiService = apiService {
            self.apiService = apiService
        }
        if let authService = authService {
            self.authService = authService
        }
        if let storageService = storageService {
            self.storageService = storageService
        }
    }
}
```

---

## 3. Testable ViewModel

**YourApp/ViewModels/UserViewModel.swift**

```swift
import Foundation

@MainActor
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let apiService: APIServiceProtocol

    init(apiService: APIServiceProtocol = DependencyContainer.shared.apiService) {
        self.apiService = apiService
    }

    func fetchUsers() async {
        isLoading = true
        errorMessage = nil

        do {
            users = try await apiService.getUsers()
            isLoading = false
        } catch {
            errorMessage = "Failed to load users: \(error.localizedDescription)"
            isLoading = false
        }
    }

    func deleteUser(at offsets: IndexSet) async {
        let usersToDelete = offsets.map { users[$0] }

        for user in usersToDelete {
            do {
                try await apiService.deleteUser(id: user.id)
                users.removeAll { $0.id == user.id }
            } catch {
                errorMessage = "Failed to delete user: \(error.localizedDescription)"
            }
        }
    }
}
```

---

## 4. Mock Services

**YourAppTests/Mocks/MockAPIService.swift**

```swift
import Foundation
@testable import YourApp

class MockAPIService: APIServiceProtocol {
    var getUsersResult: Result<[User], Error> = .success([])
    var getUserResult: Result<User, Error>?
    var createUserResult: Result<User, Error>?
    var deleteUserResult: Result<Void, Error> = .success(())

    var getUsersCalled = false
    var getUserCalled = false
    var createUserCalled = false
    var deleteUserCalled = false

    var getUserIdParameter: String?
    var createUserParameter: CreateUserRequest?
    var deleteUserIdParameter: String?

    func getUsers() async throws -> [User] {
        getUsersCalled = true
        switch getUsersResult {
        case .success(let users):
            return users
        case .failure(let error):
            throw error
        }
    }

    func getUser(id: String) async throws -> User {
        getUserCalled = true
        getUserIdParameter = id

        guard let result = getUserResult else {
            throw APIError.invalidResponse
        }

        switch result {
        case .success(let user):
            return user
        case .failure(let error):
            throw error
        }
    }

    func createUser(_ user: CreateUserRequest) async throws -> User {
        createUserCalled = true
        createUserParameter = user

        guard let result = createUserResult else {
            throw APIError.invalidResponse
        }

        switch result {
        case .success(let user):
            return user
        case .failure(let error):
            throw error
        }
    }

    func deleteUser(id: String) async throws {
        deleteUserCalled = true
        deleteUserIdParameter = id

        switch deleteUserResult {
        case .success:
            return
        case .failure(let error):
            throw error
        }
    }

    // Helper to reset state between tests
    func reset() {
        getUsersCalled = false
        getUserCalled = false
        createUserCalled = false
        deleteUserCalled = false

        getUserIdParameter = nil
        createUserParameter = nil
        deleteUserIdParameter = nil

        getUsersResult = .success([])
        getUserResult = nil
        createUserResult = nil
        deleteUserResult = .success(())
    }
}
```

---

## 5. ViewModel Unit Tests

**Swift Testing (preferred)**
```swift
import Testing
@testable import YourApp

@Suite struct UserViewModelSuite {
    @Test @MainActor
    func initialState() {
        let viewModel = UserViewModel(apiService: MockAPIService())
        #expect(viewModel.users.isEmpty)
        #expect(viewModel.isLoading == false)
        #expect(viewModel.errorMessage == nil)
    }
}
```

**YourAppTests/ViewModelTests/UserViewModelTests.swift**

```swift
import XCTest
@testable import YourApp

@MainActor
final class UserViewModelTests: XCTestCase {
    var viewModel: UserViewModel!
    var mockAPIService: MockAPIService!

    override func setUp() {
        super.setUp()
        mockAPIService = MockAPIService()
        viewModel = UserViewModel(apiService: mockAPIService)
    }

    override func tearDown() {
        viewModel = nil
        mockAPIService = nil
        super.tearDown()
    }

    // MARK: - Initial State Tests

    func testInitialState() {
        XCTAssertTrue(viewModel.users.isEmpty)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }

    // MARK: - Fetch Users Tests

    func testFetchUsersSuccess() async {
        // Given
        let expectedUsers = [
            User(id: "1", email: "user1@test.com", name: "User 1", createdAt: Date()),
            User(id: "2", email: "user2@test.com", name: "User 2", createdAt: Date())
        ]
        mockAPIService.getUsersResult = .success(expectedUsers)

        // When
        await viewModel.fetchUsers()

        // Then
        XCTAssertTrue(mockAPIService.getUsersCalled)
        XCTAssertEqual(viewModel.users.count, 2)
        XCTAssertEqual(viewModel.users, expectedUsers)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }

    func testFetchUsersFailure() async {
        // Given
        mockAPIService.getUsersResult = .failure(APIError.invalidResponse)

        // When
        await viewModel.fetchUsers()

        // Then
        XCTAssertTrue(mockAPIService.getUsersCalled)
        XCTAssertTrue(viewModel.users.isEmpty)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNotNil(viewModel.errorMessage)
        XCTAssertTrue(viewModel.errorMessage!.contains("Failed to load users"))
    }

    func testFetchUsersSetsLoadingState() async {
        // Given
        let expectation = XCTestExpectation(description: "Loading state set")
        mockAPIService.getUsersResult = .success([])

        // When
        Task {
            // Check loading is true during fetch
            XCTAssertTrue(viewModel.isLoading)
            expectation.fulfill()
        }

        await viewModel.fetchUsers()

        // Then
        await fulfillment(of: [expectation], timeout: 1.0)
        XCTAssertFalse(viewModel.isLoading)
    }

    // MARK: - Delete User Tests

    func testDeleteUserSuccess() async {
        // Given
        viewModel.users = [
            User(id: "1", email: "user1@test.com", name: "User 1", createdAt: Date()),
            User(id: "2", email: "user2@test.com", name: "User 2", createdAt: Date())
        ]
        mockAPIService.deleteUserResult = .success(())

        // When
        await viewModel.deleteUser(at: IndexSet(integer: 0))

        // Then
        XCTAssertTrue(mockAPIService.deleteUserCalled)
        XCTAssertEqual(mockAPIService.deleteUserIdParameter, "1")
        XCTAssertEqual(viewModel.users.count, 1)
        XCTAssertEqual(viewModel.users[0].id, "2")
    }

    func testDeleteUserFailure() async {
        // Given
        viewModel.users = [
            User(id: "1", email: "user1@test.com", name: "User 1", createdAt: Date())
        ]
        mockAPIService.deleteUserResult = .failure(APIError.invalidResponse)

        // When
        await viewModel.deleteUser(at: IndexSet(integer: 0))

        // Then
        XCTAssertTrue(mockAPIService.deleteUserCalled)
        XCTAssertEqual(viewModel.users.count, 1) // User not removed
        XCTAssertNotNil(viewModel.errorMessage)
    }

    // MARK: - Error Clearing Tests

    func testFetchUsersClearsErrorMessage() async {
        // Given
        viewModel.errorMessage = "Previous error"
        mockAPIService.getUsersResult = .success([])

        // When
        await viewModel.fetchUsers()

        // Then
        XCTAssertNil(viewModel.errorMessage)
    }
}
```

---

## 6. View Tests with ViewInspector

**Installation (Package.swift)**

```swift
dependencies: [
    .package(url: "https://github.com/nalexn/ViewInspector", from: "0.9.0")
]
```

**YourApp/Views/UserListView.swift**

```swift
import SwiftUI

struct UserListView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView("Loading users...")
                } else if let error = viewModel.errorMessage {
                    VStack {
                        Text(error)
                            .foregroundColor(.red)
                        Button("Retry") {
                            Task {
                                await viewModel.fetchUsers()
                            }
                        }
                    }
                } else {
                    List {
                        ForEach(viewModel.users) { user in
                            UserRow(user: user)
                        }
                        .onDelete { indexSet in
                            Task {
                                await viewModel.deleteUser(at: indexSet)
                            }
                        }
                    }
                }
            }
            .navigationTitle("Users")
            .task {
                await viewModel.fetchUsers()
            }
        }
    }
}

struct UserRow: View {
    let user: User

    var body: some View {
        VStack(alignment: .leading) {
            Text(user.name)
                .font(.headline)
            Text(user.email)
                .font(.subheadline)
                .foregroundColor(.secondary)
        }
    }
}

#if DEBUG
extension UserListView {
    init(viewModel: UserViewModel) {
        _viewModel = StateObject(wrappedValue: viewModel)
    }
}
#endif
```

**YourAppTests/ViewTests/UserListViewTests.swift**

```swift
import XCTest
import SwiftUI
import ViewInspector
@testable import YourApp

@MainActor
final class UserListViewTests: XCTestCase {
    var mockAPIService: MockAPIService!

    override func setUp() {
        super.setUp()
        mockAPIService = MockAPIService()
    }

    override func tearDown() {
        mockAPIService = nil
        super.tearDown()
    }

    func testLoadingStateDisplaysProgressView() throws {
        // Given
        let viewModel = UserViewModel(apiService: mockAPIService)
        viewModel.isLoading = true

        // When
        let view = UserListView(viewModel: viewModel)

        // Then
        let progressView = try view.inspect().find(ViewType.ProgressView.self)
        XCTAssertNotNil(progressView)
    }

    func testErrorStateDisplaysErrorMessage() throws {
        // Given
        let viewModel = UserViewModel(apiService: mockAPIService)
        viewModel.errorMessage = "Test error"

        // When
        let view = UserListView(viewModel: viewModel)

        // Then
        let errorText = try view.inspect().find(text: "Test error")
        XCTAssertNotNil(errorText)

        let retryButton = try view.inspect().find(button: "Retry")
        XCTAssertNotNil(retryButton)
    }

    func testSuccessStateDisplaysList() throws {
        // Given
        let viewModel = UserViewModel(apiService: mockAPIService)
        viewModel.users = [
            User(id: "1", email: "user1@test.com", name: "User 1", createdAt: Date()),
            User(id: "2", email: "user2@test.com", name: "User 2", createdAt: Date())
        ]

        // When
        let view = UserListView(viewModel: viewModel)

        // Then
        let list = try view.inspect().find(ViewType.List.self)
        XCTAssertNotNil(list)

        let rows = try list.findAll(UserRow.self)
        XCTAssertEqual(rows.count, 2)
    }

    func testUserRowDisplaysUserInfo() throws {
        // Given
        let user = User(id: "1", email: "test@example.com", name: "Test User", createdAt: Date())

        // When
        let view = UserRow(user: user)

        // Then
        let nameText = try view.inspect().find(text: "Test User")
        XCTAssertNotNil(nameText)

        let emailText = try view.inspect().find(text: "test@example.com")
        XCTAssertNotNil(emailText)
    }
}
```

---

## 7. Integration Tests

**YourAppTests/IntegrationTests/UserFlowTests.swift**

```swift
import XCTest
@testable import YourApp

@MainActor
final class UserFlowTests: XCTestCase {
    var mockAPIService: MockAPIService!
    var viewModel: UserViewModel!

    override func setUp() {
        super.setUp()
        mockAPIService = MockAPIService()
        viewModel = UserViewModel(apiService: mockAPIService)
    }

    override func tearDown() {
        viewModel = nil
        mockAPIService = nil
        super.tearDown()
    }

    func testCompleteUserFlow() async {
        // 1. Fetch users
        let users = [
            User(id: "1", email: "user1@test.com", name: "User 1", createdAt: Date()),
            User(id: "2", email: "user2@test.com", name: "User 2", createdAt: Date())
        ]
        mockAPIService.getUsersResult = .success(users)

        await viewModel.fetchUsers()

        XCTAssertEqual(viewModel.users.count, 2)
        XCTAssertNil(viewModel.errorMessage)

        // 2. Delete a user
        mockAPIService.deleteUserResult = .success(())

        await viewModel.deleteUser(at: IndexSet(integer: 0))

        XCTAssertEqual(viewModel.users.count, 1)
        XCTAssertEqual(viewModel.users[0].id, "2")

        // 3. Handle error on next fetch
        mockAPIService.getUsersResult = .failure(APIError.invalidResponse)

        await viewModel.fetchUsers()

        XCTAssertNotNil(viewModel.errorMessage)
    }
}
```

---

## 8. Test Helpers

**YourAppTests/Helpers/TestHelpers.swift**

```swift
import Foundation
@testable import YourApp

extension User {
    static func mockUser(
        id: String = "test-id",
        email: String = "test@example.com",
        name: String = "Test User",
        createdAt: Date = Date()
    ) -> User {
        User(id: id, email: email, name: name, createdAt: createdAt)
    }

    static func mockUsers(count: Int) -> [User] {
        (0..<count).map { index in
            mockUser(id: "\(index)", email: "user\(index)@test.com", name: "User \(index)")
        }
    }
}
```

**YourAppTests/Helpers/XCTestCase+Extensions.swift**

```swift
import XCTest

extension XCTestCase {
    func waitForPublisher<T>(
        _ publisher: Published<T>.Publisher,
        timeout: TimeInterval = 1.0,
        file: StaticString = #file,
        line: UInt = #line
    ) async throws -> T {
        var cancellable: AnyCancellable?
        let expectation = XCTestExpectation(description: "Publisher value")

        var result: T?

        cancellable = publisher.sink { value in
            result = value
            expectation.fulfill()
        }

        await fulfillment(of: [expectation], timeout: timeout)
        cancellable?.cancel()

        guard let unwrapped = result else {
            XCTFail("Publisher did not emit a value", file: file, line: line)
            throw PublisherError.noValue
        }

        return unwrapped
    }

    enum PublisherError: Error {
        case noValue
    }
}
```

---

## 9. Code Coverage Configuration

**Enable Code Coverage in Xcode:**

1. Edit Scheme → Test → Options
2. Check "Gather coverage for all targets"
3. Or specify specific targets

**Command Line:**

```bash
# Run tests with coverage
xcodebuild test \
  -scheme YourApp \
  -destination 'platform=iOS Simulator,name=iPhone 16' \
  -enableCodeCoverage YES

# Generate coverage report
xcrun xccov view --report DerivedData/.../Coverage.profdata
```

---

## 10. CI/CD GitHub Actions

**.github/workflows/test.yml**

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v3

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_15.2.app

      - name: Run tests
        run: |
          xcodebuild test \
            -scheme YourApp \
            -destination 'platform=iOS Simulator,name=iPhone 16' \
            -enableCodeCoverage YES \
            -resultBundlePath TestResults

      - name: Check code coverage
        run: |
          xcrun xccov view --report TestResults.xcresult > coverage.txt
          cat coverage.txt

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: coverage.txt
```

---

## 11. TDD Best Practices

1. **Write Tests First**
   - Red: Write failing test
   - Green: Write minimal code to pass
   - Refactor: Improve code quality

2. **Test Structure (AAA Pattern)**
   - Arrange: Set up test data
   - Act: Execute the code
   - Assert: Verify the results

3. **Test Naming**
   - Use descriptive names
   - Format: `test<MethodName><Scenario><ExpectedResult>`
   - Example: `testFetchUsersWithEmptyResponseReturnsEmptyArray`

4. **Mocking**
   - Use protocols for dependencies
   - Create dedicated mock classes
   - Verify interactions (called, parameters)

5. **Code Coverage Goals**
   - Aim for 80%+ coverage
   - Focus on business logic
   - Don't test framework code

6. **Test Independence**
   - Each test should be independent
   - Use setUp/tearDown properly
   - Don't share state between tests

---

This template provides comprehensive testing patterns for building reliable, maintainable iOS applications with high confidence in code quality.
