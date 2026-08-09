# iOS App Template (SwiftUI + Combine)

Complete production-ready iOS application template using Swift, SwiftUI, Combine framework for reactive state management, MVVM architecture, and modern iOS patterns.

---

## Tech Stack

- **Language**: Swift 6.1+
- **UI Framework**: SwiftUI
- **Reactive Framework**: Combine
- **Architecture**: MVVM with Reactive Bindings
- **State Management**: Combine + ObservableObject (Observation for new screens)
- **Networking**: URLSession + Combine Publishers
- **Persistence**: Core Data + Combine
- **Navigation**: NavigationStack (iOS 17+)
- **Authentication**: Keychain + Reactive Auth State
- **Testing**: Swift Testing (preferred) + XCTest + Combine Testing
- **Deployment**: Xcode Cloud / Fastlane

---

## Project Structure

```
YourApp/
├── YourApp/
│   ├── App/
│   │   ├── YourAppApp.swift          # App entry point
│   │   └── AppCoordinator.swift      # Navigation coordinator
│   ├── Models/
│   │   ├── User.swift                # Domain models
│   │   ├── Post.swift
│   │   └── APIResponse.swift
│   ├── ViewModels/
│   │   ├── AuthViewModel.swift       # Reactive auth logic
│   │   ├── FeedViewModel.swift       # Feed with Combine
│   │   └── SearchViewModel.swift     # Search with debouncing
│   ├── Views/
│   │   ├── Auth/
│   │   │   ├── LoginView.swift
│   │   │   └── RegisterView.swift
│   │   ├── Feed/
│   │   │   ├── FeedView.swift
│   │   │   └── PostRowView.swift
│   │   └── Search/
│   │       └── SearchView.swift
│   ├── Services/
│   │   ├── APIService.swift          # Combine publishers
│   │   ├── AuthService.swift         # Reactive auth
│   │   └── PersistenceService.swift  # Core Data + Combine
│   ├── Repositories/
│   │   ├── UserRepository.swift      # Data layer
│   │   └── PostRepository.swift
│   ├── Utilities/
│   │   ├── Publishers/               # Custom publishers
│   │   ├── Operators/                # Custom operators
│   │   └── Extensions/
│   └── Resources/
│       ├── Assets.xcassets
│       └── YourApp.xcdatamodeld
└── YourAppTests/
    ├── ViewModelTests/
    ├── PublisherTests/
    └── MockServices/
```

---

## 1. App Entry Point

**YourApp/App/YourAppApp.swift**

```swift
import SwiftUI
import Combine

@main
struct YourAppApp: App {
    @StateObject private var coordinator = AppCoordinator()

    var body: some Scene {
        WindowGroup {
            coordinator.rootView
                .environmentObject(coordinator.authViewModel)
                .environmentObject(coordinator)
        }
    }
}
```

**YourApp/App/AppCoordinator.swift**

```swift
import SwiftUI
import Combine

class AppCoordinator: ObservableObject {
    @Published var authViewModel: AuthViewModel
    @Published var isAuthenticated = false

    private var cancellables = Set<AnyCancellable>()

    init() {
        self.authViewModel = AuthViewModel()

        // React to auth state changes
        authViewModel.$isAuthenticated
            .assign(to: \.isAuthenticated, on: self)
            .store(in: &cancellables)
    }

    @ViewBuilder
    var rootView: some View {
        if isAuthenticated {
            MainTabView()
        } else {
            LoginView()
        }
    }
}
```

---

## 2. Models

**YourApp/Models/User.swift**

```swift
import Foundation

struct User: Codable, Identifiable, Equatable {
    let id: String
    let email: String
    let name: String
    let avatarURL: URL?
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case email
        case name
        case avatarURL = "avatar_url"
        case createdAt = "created_at"
    }
}

struct LoginRequest: Codable {
    let email: String
    let password: String
}

struct AuthResponse: Codable {
    let token: String
    let user: User
}
```

**YourApp/Models/Post.swift**

```swift
import Foundation

struct Post: Codable, Identifiable, Equatable {
    let id: String
    let title: String
    let content: String
    let author: User
    let isStarred: Bool
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id, title, content, author
        case isStarred = "is_starred"
        case createdAt = "created_at"
    }
}

enum PostFilter {
    case all
    case starred
    case recent
}
```

---

## 3. Services with Combine Publishers

**YourApp/Services/APIService.swift**

```swift
import Foundation
import Combine

enum APIError: Error {
    case invalidURL
    case invalidResponse
    case unauthorized
    case serverError(String)
}

class APIService {
    static let shared = APIService()

    private let baseURL = "https://api.example.com"
    private let decoder: JSONDecoder = {
        let decoder = JSONDecoder()
        decoder.dateDecodingStrategy = .iso8601
        return decoder
    }()

    private init() {}

    // MARK: - Generic Request

    private func request<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        body: Encodable? = nil,
        headers: [String: String] = [:]
    ) -> AnyPublisher<T, APIError> {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            return Fail(error: APIError.invalidURL)
                .eraseToAnyPublisher()
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        // Add auth token if available
        if let token = KeychainManager.shared.get(key: "auth_token") {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        // Add custom headers
        headers.forEach { request.setValue($1, forHTTPHeaderField: $0) }

        // Encode body if provided
        if let body = body {
            request.httpBody = try? JSONEncoder().encode(body)
        }

        return URLSession.shared.dataTaskPublisher(for: request)
            .tryMap { data, response -> Data in
                guard let httpResponse = response as? HTTPURLResponse else {
                    throw APIError.invalidResponse
                }

                switch httpResponse.statusCode {
                case 200...299:
                    return data
                case 401:
                    throw APIError.unauthorized
                default:
                    let error = try? self.decoder.decode(APIErrorResponse.self, from: data)
                    throw APIError.serverError(error?.message ?? "Unknown error")
                }
            }
            .decode(type: T.self, decoder: decoder)
            .mapError { error in
                if let apiError = error as? APIError {
                    return apiError
                } else {
                    return APIError.serverError(error.localizedDescription)
                }
            }
            .eraseToAnyPublisher()
    }

    // MARK: - Endpoints

    func login(email: String, password: String) -> AnyPublisher<AuthResponse, APIError> {
        request("/auth/login", method: "POST", body: LoginRequest(email: email, password: password))
    }

    func getUsers() -> AnyPublisher<[User], APIError> {
        request("/users")
    }

    func getUser(id: String) -> AnyPublisher<User, APIError> {
        request("/users/\(id)")
    }

    func getPosts() -> AnyPublisher<[Post], APIError> {
        request("/posts")
    }

    func searchUsers(query: String) -> AnyPublisher<[User], APIError> {
        request("/users/search?q=\(query)")
    }
}

struct APIErrorResponse: Decodable {
    let message: String
}
```

**YourApp/Services/AuthService.swift**

```swift
import Foundation
import Combine

class AuthService {
    static let shared = AuthService()

    @Published private(set) var currentUser: User?
    @Published private(set) var isAuthenticated = false

    private init() {
        checkAuthStatus()
    }

    func login(email: String, password: String) -> AnyPublisher<User, APIError> {
        APIService.shared.login(email: email, password: password)
            .handleEvents(
                receiveOutput: { [weak self] response in
                    KeychainManager.shared.save(token: response.token, key: "auth_token")
                    self?.currentUser = response.user
                    self?.isAuthenticated = true
                }
            )
            .map(\.user)
            .eraseToAnyPublisher()
    }

    func logout() -> AnyPublisher<Void, Never> {
        Future { promise in
            KeychainManager.shared.delete(key: "auth_token")
            self.currentUser = nil
            self.isAuthenticated = false
            promise(.success(()))
        }
        .eraseToAnyPublisher()
    }

    private func checkAuthStatus() {
        isAuthenticated = KeychainManager.shared.get(key: "auth_token") != nil
    }
}
```

---

## 4. ViewModels with Combine

**YourApp/ViewModels/AuthViewModel.swift**

```swift
import Foundation
import Combine

@MainActor
class AuthViewModel: ObservableObject {
    @Published var email = ""
    @Published var password = ""
    @Published var isLoading = false
    @Published var errorMessage: String?
    @Published var isAuthenticated = false

    private let authService = AuthService.shared
    private var cancellables = Set<AnyCancellable>()

    init() {
        // Sync with auth service
        authService.$isAuthenticated
            .assign(to: \.isAuthenticated, on: self)
            .store(in: &cancellables)

        // Validate email format
        $email
            .debounce(for: .milliseconds(500), scheduler: DispatchQueue.main)
            .sink { [weak self] email in
                if !email.isEmpty && !email.contains("@") {
                    self?.errorMessage = "Invalid email format"
                } else {
                    self?.errorMessage = nil
                }
            }
            .store(in: &cancellables)
    }

    func login() {
        isLoading = true
        errorMessage = nil

        authService.login(email: email, password: password)
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        switch error {
                        case .unauthorized:
                            self?.errorMessage = "Invalid credentials"
                        case .serverError(let message):
                            self?.errorMessage = message
                        default:
                            self?.errorMessage = "Login failed. Please try again."
                        }
                    }
                },
                receiveValue: { _ in
                    // Success handled by auth service
                }
            )
            .store(in: &cancellables)
    }

    func logout() {
        authService.logout()
            .receive(on: DispatchQueue.main)
            .sink { _ in
                // Logout completed
            }
            .store(in: &cancellables)
    }
}
```

**YourApp/ViewModels/FeedViewModel.swift**

```swift
import Foundation
import Combine

@MainActor
class FeedViewModel: ObservableObject {
    @Published var posts: [Post] = []
    @Published var filteredPosts: [Post] = []
    @Published var filter: PostFilter = .all
    @Published var isLoading = false
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()

    init() {
        setupFilterBinding()
        setupAutoRefresh()
    }

    private func setupFilterBinding() {
        // Automatically filter posts when filter changes
        Publishers.CombineLatest($posts, $filter)
            .map { posts, filter in
                switch filter {
                case .all:
                    return posts
                case .starred:
                    return posts.filter { $0.isStarred }
                case .recent:
                    let yesterday = Date().addingTimeInterval(-86400)
                    return posts.filter { $0.createdAt > yesterday }
                }
            }
            .assign(to: \.filteredPosts, on: self)
            .store(in: &cancellables)
    }

    private func setupAutoRefresh() {
        // Auto-refresh every 30 seconds
        Timer.publish(every: 30, on: .main, in: .common)
            .autoconnect()
            .sink { [weak self] _ in
                self?.refreshPosts()
            }
            .store(in: &cancellables)
    }

    func loadPosts() {
        isLoading = true
        errorMessage = nil

        APIService.shared.getPosts()
            .receive(on: DispatchQueue.main)
            .sink(
                receiveCompletion: { [weak self] completion in
                    self?.isLoading = false
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { [weak self] posts in
                    self?.posts = posts
                }
            )
            .store(in: &cancellables)
    }

    func refreshPosts() {
        APIService.shared.getPosts()
            .receive(on: DispatchQueue.main)
            .replaceError(with: posts) // Keep existing posts on error
            .assign(to: \.posts, on: self)
            .store(in: &cancellables)
    }
}
```

**YourApp/ViewModels/SearchViewModel.swift**

```swift
import Foundation
import Combine

@MainActor
class SearchViewModel: ObservableObject {
    @Published var searchQuery = ""
    @Published var results: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()

    init() {
        setupSearchPipeline()
    }

    private func setupSearchPipeline() {
        $searchQuery
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .removeDuplicates()
            .handleEvents(receiveOutput: { [weak self] query in
                if query.isEmpty {
                    self?.results = []
                    self?.isLoading = false
                }
            })
            .filter { !$0.isEmpty }
            .flatMap { [weak self] query -> AnyPublisher<[User], Never> in
                guard let self = self else {
                    return Just([]).eraseToAnyPublisher()
                }

                self.isLoading = true

                return APIService.shared.searchUsers(query: query)
                    .catch { error -> AnyPublisher<[User], Never> in
                        self.errorMessage = error.localizedDescription
                        return Just([]).eraseToAnyPublisher()
                    }
                    .eraseToAnyPublisher()
            }
            .receive(on: DispatchQueue.main)
            .sink { [weak self] users in
                self?.results = users
                self?.isLoading = false
            }
            .store(in: &cancellables)
    }
}
```

---

## 5. Views

**YourApp/Views/Auth/LoginView.swift**

```swift
import SwiftUI

struct LoginView: View {
    @EnvironmentObject var viewModel: AuthViewModel

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("Welcome Back")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                VStack(spacing: 16) {
                    TextField("Email", text: $viewModel.email)
                        .textInputAutocapitalization(.never)
                        .keyboardType(.emailAddress)
                        .textContentType(.emailAddress)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)

                    SecureField("Password", text: $viewModel.password)
                        .textContentType(.password)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                }

                if let error = viewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                Button(action: viewModel.login) {
                    if viewModel.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text("Sign In")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(
                    viewModel.email.isEmpty || viewModel.password.isEmpty
                        ? Color.gray
                        : Color.blue
                )
                .foregroundColor(.white)
                .cornerRadius(10)
                .disabled(viewModel.isLoading || viewModel.email.isEmpty || viewModel.password.isEmpty)
            }
            .padding()
        }
    }
}
```

**YourApp/Views/Feed/FeedView.swift**

```swift
import SwiftUI

struct FeedView: View {
    @StateObject private var viewModel = FeedViewModel()

    var body: some View {
        NavigationStack {
            VStack {
                // Filter Picker
                Picker("Filter", selection: $viewModel.filter) {
                    Text("All").tag(PostFilter.all)
                    Text("Starred").tag(PostFilter.starred)
                    Text("Recent").tag(PostFilter.recent)
                }
                .pickerStyle(.segmented)
                .padding()

                // Posts List
                Group {
                    if viewModel.isLoading {
                        ProgressView()
                    } else if let error = viewModel.errorMessage {
                        ErrorView(message: error) {
                            viewModel.loadPosts()
                        }
                    } else {
                        List(viewModel.filteredPosts) { post in
                            PostRowView(post: post)
                        }
                    }
                }
            }
            .navigationTitle("Feed")
            .task {
                viewModel.loadPosts()
            }
            .refreshable {
                viewModel.refreshPosts()
            }
        }
    }
}

struct PostRowView: View {
    let post: Post

    var body: some View {
        VStack(alignment: .leading, spacing: 8) {
            HStack {
                Text(post.author.name)
                    .font(.headline)
                Spacer()
                if post.isStarred {
                    Image(systemName: "star.fill")
                        .foregroundColor(.yellow)
                }
            }

            Text(post.title)
                .font(.subheadline)
                .fontWeight(.semibold)

            Text(post.content)
                .font(.body)
                .foregroundColor(.secondary)
                .lineLimit(3)

            Text(post.createdAt, style: .relative)
                .font(.caption)
                .foregroundColor(.gray)
        }
        .padding(.vertical, 4)
    }
}
```

**YourApp/Views/Search/SearchView.swift**

```swift
import SwiftUI

struct SearchView: View {
    @StateObject private var viewModel = SearchViewModel()

    var body: some View {
        NavigationStack {
            VStack {
                // Search Field
                TextField("Search users...", text: $viewModel.searchQuery)
                    .textFieldStyle(.roundedBorder)
                    .padding()

                // Results
                if viewModel.isLoading {
                    ProgressView()
                        .padding()
                } else if !viewModel.results.isEmpty {
                    List(viewModel.results) { user in
                        UserRowView(user: user)
                    }
                } else if !viewModel.searchQuery.isEmpty {
                    ContentUnavailableView(
                        "No Results",
                        systemImage: "magnifyingglass",
                        description: Text("No users found for '\(viewModel.searchQuery)'")
                    )
                }

                Spacer()
            }
            .navigationTitle("Search")
        }
    }
}

struct UserRowView: View {
    let user: User

    var body: some View {
        HStack(spacing: 12) {
            AsyncImage(url: user.avatarURL) { image in
                image
                    .resizable()
                    .aspectRatio(contentMode: .fill)
            } placeholder: {
                Circle()
                    .fill(Color.gray.opacity(0.3))
            }
            .frame(width: 50, height: 50)
            .clipShape(Circle())

            VStack(alignment: .leading) {
                Text(user.name)
                    .font(.headline)
                Text(user.email)
                    .font(.subheadline)
                    .foregroundColor(.secondary)
            }
        }
    }
}
```

---

## 6. Custom Combine Publishers

**YourApp/Utilities/Publishers/ValidationPublisher.swift**

```swift
import Combine

extension Publishers {
    struct ValidateEmail: Publisher {
        typealias Output = Bool
        typealias Failure = Never

        let upstream: AnyPublisher<String, Never>

        func receive<S>(subscriber: S) where S : Subscriber, Failure == S.Failure, Output == S.Input {
            let subscription = ValidateEmailSubscription(subscriber: subscriber, upstream: upstream)
            subscriber.receive(subscription: subscription)
        }
    }

    private class ValidateEmailSubscription<S: Subscriber>: Subscription where S.Input == Bool, S.Failure == Never {
        private var subscriber: S?
        private var cancellable: AnyCancellable?

        init(subscriber: S, upstream: AnyPublisher<String, Never>) {
            self.subscriber = subscriber

            cancellable = upstream
                .map { email in
                    let emailRegex = "[A-Z0-9a-z._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,64}"
                    let predicate = NSPredicate(format: "SELF MATCHES %@", emailRegex)
                    return predicate.evaluate(with: email)
                }
                .sink { isValid in
                    _ = subscriber.receive(isValid)
                }
        }

        func request(_ demand: Subscribers.Demand) {}

        func cancel() {
            cancellable?.cancel()
            subscriber = nil
        }
    }
}

extension Publisher where Output == String, Failure == Never {
    func validateEmail() -> Publishers.ValidateEmail {
        Publishers.ValidateEmail(upstream: self.eraseToAnyPublisher())
    }
}
```

---

## 7. Testing with Combine

**Swift Testing (preferred)**
```swift
import Testing
@testable import YourApp

@Suite struct SearchViewModelSuite {
    @Test @MainActor
    func emptyQueryClearsResults() {
        let viewModel = SearchViewModel()
        viewModel.results = [
            User(id: "1", email: "test@test.com", name: "Test", avatarURL: nil, createdAt: .now)
        ]
        viewModel.searchQuery = ""
        #expect(viewModel.results.isEmpty)
    }
}
```

**YourAppTests/ViewModelTests/SearchViewModelTests.swift**

```swift
import XCTest
import Combine
@testable import YourApp

@MainActor
final class SearchViewModelTests: XCTestCase {
    var viewModel: SearchViewModel!
    var cancellables: Set<AnyCancellable>!

    override func setUp() {
        super.setUp()
        viewModel = SearchViewModel()
        cancellables = []
    }

    override func tearDown() {
        viewModel = nil
        cancellables = nil
        super.tearDown()
    }

    func testSearchDebouncing() throws {
        let expectation = XCTestExpectation(description: "Search debounced")

        var emissionCount = 0

        viewModel.$searchQuery
            .debounce(for: .milliseconds(300), scheduler: DispatchQueue.main)
            .sink { _ in
                emissionCount += 1
                if emissionCount == 1 {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        // Rapidly type - should only emit once after debounce
        viewModel.searchQuery = "a"
        viewModel.searchQuery = "ab"
        viewModel.searchQuery = "abc"

        wait(for: [expectation], timeout: 1.0)
        XCTAssertEqual(emissionCount, 1)
    }

    func testEmptyQueryClearsResults() {
        viewModel.results = [User(id: "1", email: "test@test.com", name: "Test", avatarURL: nil, createdAt: Date())]
        viewModel.searchQuery = ""

        let expectation = XCTestExpectation(description: "Results cleared")

        viewModel.$results
            .dropFirst()
            .sink { results in
                if results.isEmpty {
                    expectation.fulfill()
                }
            }
            .store(in: &cancellables)

        wait(for: [expectation], timeout: 1.0)
    }
}
```

---

## 8. Best Practices

1. **Combine Pipelines**
   - Use operators for data transformation
   - Debounce user input (300-500ms)
   - Use `receive(on:)` for thread safety
   - Store cancellables properly

2. **Memory Management**
   - Use `[weak self]` in closures
   - Cancel subscriptions on deinit
   - Use `Set<AnyCancellable>` for storage
   - Avoid retain cycles

3. **Error Handling**
   - Use `catch` for graceful degradation
   - Provide user-friendly error messages
   - Use `replaceError(with:)` for fallbacks
   - Log errors for debugging

4. **Performance**
   - Use `removeDuplicates()` to reduce emissions
   - Debounce expensive operations
   - Use `share()` for multiple subscribers
   - Cancel when not needed

5. **Testing**
   - Test publisher chains
   - Use expectations for async
   - Mock API responses
   - Test debouncing/throttling

---

## 9. Common Combine Patterns

**Auto-Save with Debouncing:**

```swift
$formData
    .debounce(for: .seconds(2), scheduler: DispatchQueue.main)
    .removeDuplicates()
    .sink { [weak self] data in
        self?.saveToLocalStorage(data)
    }
    .store(in: &cancellables)
```

**Combine Multiple Publishers:**

```swift
Publishers.CombineLatest3($email, $password, $agreedToTerms)
    .map { email, password, agreed in
        !email.isEmpty && !password.isEmpty && agreed
    }
    .assign(to: \.isFormValid, on: self)
    .store(in: &cancellables)
```

**Retry with Delay:**

```swift
APIService.shared.getPosts()
    .retry(3)
    .delay(for: .seconds(1), scheduler: DispatchQueue.main)
    .sink(receiveCompletion: { _ in }, receiveValue: { posts in })
    .store(in: &cancellables)
```

---

This template provides a solid foundation for building reactive iOS applications with SwiftUI and Combine, enabling declarative data flows and responsive UIs.
