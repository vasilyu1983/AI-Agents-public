# iOS App Template (Swift + SwiftUI)

Complete production-ready iOS application template using Swift, SwiftUI, MVVM architecture, URLSession for networking, SwiftData/Core Data for persistence, and modern iOS patterns.

---

## Tech Stack

- **Language**: Swift 6.1+
- **UI Framework**: SwiftUI (iOS 19+)
- **Architecture**: MVVM (Model-View-ViewModel)
- **State Management**: @Observable + @Environment (iOS 19+)
- **Concurrency**: Swift Concurrency (async/await, Actors)
- **Networking**: URLSession with async/await
- **Persistence**: SwiftData (primary) / Core Data (legacy)
- **Navigation**: NavigationStack (iOS 17+)
- **Authentication**: Keychain for token storage
- **Dependency Injection**: Protocol-based DI
- **Testing**: Swift Testing (default) + XCTest (UI/legacy)
- **Deployment**: Xcode Cloud / Fastlane

---

## Project Structure

```
YourApp/
├── YourApp/
│   ├── App/
│   │   ├── YourAppApp.swift          # App entry point
│   │   └── ContentView.swift         # Root view
│   ├── Models/
│   │   ├── User.swift                # Domain models
│   │   ├── Post.swift
│   │   └── APIResponse.swift
│   ├── ViewModels/
│   │   ├── AuthViewModel.swift       # Authentication logic
│   │   ├── UsersViewModel.swift
│   │   └── PostsViewModel.swift
│   ├── Views/
│   │   ├── Auth/
│   │   │   ├── LoginView.swift
│   │   │   └── RegisterView.swift
│   │   ├── Users/
│   │   │   ├── UsersListView.swift
│   │   │   └── UserDetailView.swift
│   │   └── Components/
│   │       ├── LoadingView.swift
│   │       └── ErrorView.swift
│   ├── Services/
│   │   ├── APIService.swift          # Network requests
│   │   ├── AuthService.swift         # Authentication
│   │   └── PersistenceController.swift # Core Data
│   ├── Utilities/
│   │   ├── KeychainManager.swift     # Secure storage
│   │   ├── Constants.swift
│   │   └── Extensions.swift
│   └── Resources/
│       ├── Assets.xcassets
│       └── YourApp.xcdatamodeld
└── YourAppTests/
    ├── ViewModelTests/
    ├── ServiceTests/
    └── MockData/
```

---

## 1. App Entry Point

**YourApp/App/YourAppApp.swift**
```swift
import SwiftUI

@main
struct YourAppApp: App {
    @State private var authViewModel = AuthViewModel()
    let persistenceController = PersistenceController.shared

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(authViewModel)
                .environment(\.managedObjectContext, persistenceController.container.viewContext)
        }
    }
}
```

**YourApp/App/ContentView.swift**
```swift
import SwiftUI

struct ContentView: View {
    @Environment(AuthViewModel.self) private var authViewModel

    var body: some View {
        Group {
            if authViewModel.isAuthenticated {
                MainTabView()
            } else {
                LoginView()
            }
        }
        .onAppear {
            authViewModel.checkAuthStatus()
        }
    }
}
```

---

## 2. Models

**YourApp/Models/User.swift**
```swift
import Foundation

struct User: Codable, Identifiable {
    let id: String
    let email: String
    let name: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case email
        case name
        case createdAt = "created_at"
    }
}

struct CreateUserRequest: Codable {
    let email: String
    let password: String
    let name: String
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

struct Post: Codable, Identifiable {
    let id: String
    let title: String
    let content: String
    let authorId: String
    let createdAt: Date

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case content
        case authorId = "author_id"
        case createdAt = "created_at"
    }
}

struct CreatePostRequest: Codable {
    let title: String
    let content: String
}
```

**YourApp/Models/APIResponse.swift**
```swift
import Foundation

struct APIError: Codable, Error {
    let message: String
    let code: String?
}

struct PaginatedResponse<T: Codable>: Codable {
    let data: [T]
    let total: Int
    let page: Int
    let pageSize: Int

    enum CodingKeys: String, CodingKey {
        case data
        case total
        case page
        case pageSize = "page_size"
    }
}
```

---

## 3. Services

**YourApp/Services/APIService.swift**
```swift
import Foundation

enum APIServiceError: Error {
    case invalidURL
    case invalidResponse
    case unauthorized
    case serverError(String)
}

class APIService {
    static let shared = APIService()

    private let baseURL = "https://api.example.com"
    private var authToken: String? {
        KeychainManager.shared.get(key: "auth_token")
    }

    private init() {}

    // MARK: - Generic Request

    private func request<T: Decodable>(
        _ endpoint: String,
        method: String = "GET",
        body: Encodable? = nil
    ) async throws -> T {
        guard let url = URL(string: "\(baseURL)\(endpoint)") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = method
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        if let token = authToken {
            request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
        }

        if let body = body {
            request.httpBody = try JSONEncoder().encode(body)
        }

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse else {
            throw APIServiceError.invalidResponse
        }

        switch httpResponse.statusCode {
        case 200...299:
            let decoder = JSONDecoder()
            decoder.dateDecodingStrategy = .iso8601
            return try decoder.decode(T.self, from: data)

        case 401:
            throw APIServiceError.unauthorized

        default:
            let error = try? JSONDecoder().decode(APIError.self, from: data)
            throw APIServiceError.serverError(error?.message ?? "Unknown error")
        }
    }

    // MARK: - Endpoints

    func getUsers() async throws -> [User] {
        try await request("/users")
    }

    func getUser(id: String) async throws -> User {
        try await request("/users/\(id)")
    }

    func getPosts(page: Int = 1, pageSize: Int = 20) async throws -> PaginatedResponse<Post> {
        try await request("/posts?page=\(page)&page_size=\(pageSize)")
    }

    func createPost(_ post: CreatePostRequest) async throws -> Post {
        try await request("/posts", method: "POST", body: post)
    }
}
```

**YourApp/Services/AuthService.swift**
```swift
import Foundation

class AuthService {
    static let shared = AuthService()

    private let baseURL = "https://api.example.com"

    private init() {}

    func login(email: String, password: String) async throws -> AuthResponse {
        guard let url = URL(string: "\(baseURL)/auth/login") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let loginRequest = LoginRequest(email: email, password: password)
        request.httpBody = try JSONEncoder().encode(loginRequest)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIServiceError.unauthorized
        }

        let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)

        // Save token to Keychain
        KeychainManager.shared.save(token: authResponse.token, key: "auth_token")

        return authResponse
    }

    func register(email: String, password: String, name: String) async throws -> AuthResponse {
        guard let url = URL(string: "\(baseURL)/auth/register") else {
            throw APIServiceError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")

        let registerRequest = CreateUserRequest(email: email, password: password, name: name)
        request.httpBody = try JSONEncoder().encode(registerRequest)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIServiceError.serverError("Registration failed")
        }

        let authResponse = try JSONDecoder().decode(AuthResponse.self, from: data)

        // Save token to Keychain
        KeychainManager.shared.save(token: authResponse.token, key: "auth_token")

        return authResponse
    }

    func logout() {
        KeychainManager.shared.delete(key: "auth_token")
    }
}
```

**YourApp/Services/PersistenceController.swift**
```swift
import CoreData

class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init(inMemory: Bool = false) {
        container = NSPersistentContainer(name: "YourApp")

        if inMemory {
            container.persistentStoreDescriptions.first?.url = URL(fileURLWithPath: "/dev/null")
        }

        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Core Data failed to load: \(error.localizedDescription)")
            }
        }

        container.viewContext.automaticallyMergesChangesFromParent = true
    }

    func save() {
        let context = container.viewContext

        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Failed to save Core Data context: \(error)")
            }
        }
    }
}
```

**SwiftData Variant (optional)**
```swift
import SwiftUI
import SwiftData

@Model
final class UserEntity {
    var id: UUID
    var name: String
    var email: String
    var createdAt: Date

    init(id: UUID = UUID(), name: String, email: String, createdAt: Date = .now) {
        self.id = id
        self.name = name
        self.email = email
        self.createdAt = createdAt
    }
}

@MainActor
struct SwiftDataStack {
    static let shared = SwiftDataStack()
    let container: ModelContainer

    init(inMemory: Bool = false) {
        let config = ModelConfiguration(isStoredInMemoryOnly: inMemory)
        container = try! ModelContainer(for: UserEntity.self, configurations: config)
    }
}
```

---

## 4. ViewModels

**YourApp/ViewModels/AuthViewModel.swift**
```swift
import Foundation
import Observation

@MainActor
@Observable
class AuthViewModel {
    var isAuthenticated = false
    var currentUser: User?
    var isLoading = false
    var errorMessage: String?

    func checkAuthStatus() {
        isAuthenticated = KeychainManager.shared.get(key: "auth_token") != nil
    }

    func login(email: String, password: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let response = try await AuthService.shared.login(email: email, password: password)
            currentUser = response.user
            isAuthenticated = true
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func register(email: String, password: String, name: String) async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            let response = try await AuthService.shared.register(email: email, password: password, name: name)
            currentUser = response.user
            isAuthenticated = true
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    func logout() {
        AuthService.shared.logout()
        currentUser = nil
        isAuthenticated = false
    }
}
```

**YourApp/ViewModels/UsersViewModel.swift**
```swift
import Foundation
import Observation

@MainActor
@Observable
class UsersViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    func fetchUsers() async {
        isLoading = true
        errorMessage = nil
        defer { isLoading = false }

        do {
            users = try await APIService.shared.getUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
```

---

## 5. Views

**YourApp/Views/Auth/LoginView.swift**
```swift
import SwiftUI

struct LoginView: View {
    @Environment(AuthViewModel.self) private var authViewModel

    @State private var email = ""
    @State private var password = ""

    var body: some View {
        NavigationStack {
            VStack(spacing: 20) {
                Text("Welcome Back")
                    .font(.largeTitle)
                    .fontWeight(.bold)

                VStack(spacing: 16) {
                    TextField("Email", text: $email)
                        .textInputAutocapitalization(.never)
                        .keyboardType(.emailAddress)
                        .textContentType(.emailAddress)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)

                    SecureField("Password", text: $password)
                        .textContentType(.password)
                        .padding()
                        .background(Color(.systemGray6))
                        .cornerRadius(10)
                }

                if let error = authViewModel.errorMessage {
                    Text(error)
                        .foregroundColor(.red)
                        .font(.caption)
                }

                Button(action: {
                    Task {
                        await authViewModel.login(email: email, password: password)
                    }
                }) {
                    if authViewModel.isLoading {
                        ProgressView()
                            .progressViewStyle(CircularProgressViewStyle(tint: .white))
                    } else {
                        Text("Sign In")
                            .fontWeight(.semibold)
                    }
                }
                .frame(maxWidth: .infinity)
                .padding()
                .background(Color.blue)
                .foregroundColor(.white)
                .cornerRadius(10)
                .disabled(authViewModel.isLoading || email.isEmpty || password.isEmpty)

                NavigationLink("Create Account") {
                    RegisterView()
                }
                .font(.subheadline)
            }
            .padding()
        }
    }
}
```

**YourApp/Views/Users/UsersListView.swift**
```swift
import SwiftUI

struct UsersListView: View {
    @State private var viewModel = UsersViewModel()

    var body: some View {
        NavigationStack {
            Group {
                if viewModel.isLoading {
                    ProgressView()
                } else if let error = viewModel.errorMessage {
                    ErrorView(message: error) {
                        Task {
                            await viewModel.fetchUsers()
                        }
                    }
                } else {
                    List(viewModel.users) { user in
                        NavigationLink(value: user) {
                            VStack(alignment: .leading) {
                                Text(user.name)
                                    .font(.headline)
                                Text(user.email)
                                    .font(.subheadline)
                                    .foregroundColor(.secondary)
                            }
                        }
                    }
                    .navigationDestination(for: User.self) { user in
                        UserDetailView(user: user)
                    }
                }
            }
            .navigationTitle("Users")
            .task {
                await viewModel.fetchUsers()
            }
            .refreshable {
                await viewModel.fetchUsers()
            }
        }
    }
}
```

**YourApp/Views/Components/ErrorView.swift**
```swift
import SwiftUI

struct ErrorView: View {
    let message: String
    let retry: () -> Void

    var body: some View {
        VStack(spacing: 16) {
            Image(systemName: "exclamationmark.triangle")
                .font(.system(size: 48))
                .foregroundColor(.red)

            Text("Error")
                .font(.title2)
                .fontWeight(.semibold)

            Text(message)
                .font(.body)
                .foregroundColor(.secondary)
                .multilineTextAlignment(.center)
                .padding(.horizontal)

            Button(action: retry) {
                Text("Try Again")
                    .fontWeight(.semibold)
                    .padding(.horizontal, 24)
                    .padding(.vertical, 12)
                    .background(Color.blue)
                    .foregroundColor(.white)
                    .cornerRadius(10)
            }
        }
        .padding()
    }
}
```

---

## 6. Utilities

**YourApp/Utilities/KeychainManager.swift**
```swift
import Security
import Foundation

class KeychainManager {
    static let shared = KeychainManager()

    private init() {}

    func save(token: String, key: String) {
        let data = Data(token.utf8)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]

        SecItemDelete(query as CFDictionary)
        SecItemAdd(query as CFDictionary, nil)
    }

    func get(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true
        ]

        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)

        guard let data = result as? Data else { return nil }
        return String(data: data, encoding: .utf8)
    }

    func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        SecItemDelete(query as CFDictionary)
    }
}
```

---

## 7. Testing

**Swift Testing (Swift 6.1+)**
```swift
import Testing
@testable import YourApp

@Suite struct AuthViewModelSuite {
    @Test @MainActor
    func initialState() {
        let viewModel = AuthViewModel()
        #expect(viewModel.isAuthenticated == false)
        #expect(viewModel.currentUser == nil)
        #expect(viewModel.isLoading == false)
        #expect(viewModel.errorMessage == nil)
    }
}
```

**YourAppTests/ViewModelTests/AuthViewModelTests.swift**
```swift
import XCTest
@testable import YourApp

@MainActor
final class AuthViewModelTests: XCTestCase {
    var viewModel: AuthViewModel!

    override func setUp() {
        super.setUp()
        viewModel = AuthViewModel()
    }

    override func tearDown() {
        viewModel = nil
        super.tearDown()
    }

    func testInitialState() {
        XCTAssertFalse(viewModel.isAuthenticated)
        XCTAssertNil(viewModel.currentUser)
        XCTAssertFalse(viewModel.isLoading)
        XCTAssertNil(viewModel.errorMessage)
    }

    func testLogout() {
        viewModel.logout()
        XCTAssertFalse(viewModel.isAuthenticated)
        XCTAssertNil(viewModel.currentUser)
    }
}
```

---

## 8. Configuration

**Info.plist** additions:
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>api.example.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <false/>
        </dict>
    </dict>
</dict>
```

---

## 9. Deployment

**Using Fastlane:**

```ruby
# fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Run tests"
  lane :test do
    run_tests(scheme: "YourApp")
  end

  desc "Build and upload to TestFlight"
  lane :beta do
    increment_build_number
    build_app(scheme: "YourApp")
    upload_to_testflight
  end

  desc "Release to App Store"
  lane :release do
    increment_version_number
    build_app(scheme: "YourApp")
    upload_to_app_store
  end
end
```

---

## Best Practices

1. **Architecture**
   - Use MVVM for clear separation of concerns
   - ViewModels should be @MainActor for UI updates
   - Use protocols for dependency injection
   - Prefer @Observable + @Environment (iOS 19+) over ObservableObject/@EnvironmentObject

2. **Networking**
   - Always use async/await for network calls
   - Handle errors gracefully with structured error types
   - Implement request timeouts and retry logic
   - Use actors for thread-safe network state

3. **State Management**
   - Use @State for local UI state
   - Use @Observable + @State for view-owned ViewModels (iOS 19+)
   - Use @Environment for dependency injection and shared state
   - Avoid @EnvironmentObject in new code (use @Environment instead)

4. **Concurrency**
   - Mark UI-related code with @MainActor
   - Use actors for shared mutable state
   - Offload heavy computation to background tasks
   - Use TaskGroup for parallel async operations

5. **Security**
   - Store tokens in Keychain, never UserDefaults
   - Use HTTPS for all network requests
   - Validate SSL certificates
   - Implement certificate pinning for sensitive apps

6. **Testing**
   - Use Swift Testing for unit tests; keep XCTest for UI/legacy
   - Write unit tests for ViewModels
   - Mock network calls in tests
   - Test async code with async/await and Observation-aware assertions

7. **Performance**
   - Use lazy loading for images with caching
   - Implement pagination for lists
   - Cache network responses when appropriate
   - Use Instruments for profiling

---

## Next Steps

1. Replace placeholder API URL with your backend
2. Customize models to match your API schema
3. Add more views and features
4. Implement push notifications
5. Add analytics and crash reporting
6. Configure CI/CD pipeline
7. Submit to App Store

---

This template provides a solid foundation for building production-ready iOS applications with modern Swift and SwiftUI patterns.
