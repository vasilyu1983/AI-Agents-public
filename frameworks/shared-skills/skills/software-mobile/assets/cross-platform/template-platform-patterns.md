# Mobile Platform Patterns Reference

Comprehensive reference for iOS (SwiftUI, UIKit), Android (Jetpack Compose, Views), and cross-platform mobile development patterns including navigation, state management, networking, storage, and platform-specific features.

---

## Table of Contents

**iOS Patterns:**
- [Navigation (SwiftUI)](#navigation-ios-swiftui)
- [Navigation (UIKit)](#navigation-ios-uikit)
- [State Management (SwiftUI)](#state-management-ios-swiftui)
- [Network Requests (iOS)](#network-requests-ios)
- [Local Storage (Core Data)](#local-storage-ios-core-data)
- [Authentication (iOS)](#authentication-ios)
- [Push Notifications (iOS)](#push-notifications-ios)

**Android Patterns:**
- [Navigation (Jetpack Compose)](#navigation-android-jetpack-compose)
- [State Management (Jetpack Compose)](#state-management-android-jetpack-compose)
- [Network Requests (Android)](#network-requests-android)
- [Local Storage (Room)](#local-storage-android-room)
- [Authentication (Android)](#authentication-android)
- [Push Notifications (Android)](#push-notifications-android)

---

## Navigation (iOS - SwiftUI)

**Use when:** Implementing navigation in iOS apps.

### NavigationStack (iOS 17+)

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List {
                NavigationLink("Users", value: Route.users)
                NavigationLink("Settings", value: Route.settings)
            }
            .navigationDestination(for: Route.self) { route in
                switch route {
                case .users:
                    UsersView()
                case .settings:
                    SettingsView()
                case .userDetail(let id):
                    UserDetailView(userId: id)
                }
            }
        }
    }
}

enum Route: Hashable {
    case users
    case settings
    case userDetail(String)
}
```

### TabView

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem {
                    Label("Home", systemImage: "house")
                }
                .tag(0)

            ProfileView()
                .tabItem {
                    Label("Profile", systemImage: "person")
                }
                .tag(1)
        }
    }
}
```

**Checklist:**
- [ ] Type-safe navigation
- [ ] Deep linking support
- [ ] Back navigation handling
- [ ] State preservation
- [ ] Tab bar for primary navigation

---

## Navigation (Android - Jetpack Compose)

**Use when:** Implementing navigation in Android apps.

### Navigation Component

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(
        navController = navController,
        startDestination = "home"
    ) {
        composable("home") {
            HomeScreen(
                onNavigateToDetail = { id ->
                    navController.navigate("detail/$id")
                }
            )
        }

        composable(
            route = "detail/{userId}",
            arguments = listOf(
                navArgument("userId") { type = NavType.StringType }
            )
        ) { backStackEntry ->
            val userId = backStackEntry.arguments?.getString("userId")
            DetailScreen(userId = userId)
        }
    }
}
```

### Bottom Navigation

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()
    val items = listOf(
        Screen.Home,
        Screen.Search,
        Screen.Profile
    )

    Scaffold(
        bottomBar = {
            NavigationBar {
                items.forEach { screen ->
                    NavigationBarItem(
                        icon = { Icon(screen.icon, contentDescription = null) },
                        label = { Text(screen.title) },
                        selected = currentRoute == screen.route,
                        onClick = { navController.navigate(screen.route) }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            // Navigation graph
        }
    }
}
```

**Checklist:**
- [ ] Safe Args for type safety
- [ ] Deep linking configured
- [ ] Back stack management
- [ ] Navigation animations
- [ ] Bottom navigation for primary sections

---

## State Management (iOS - SwiftUI)

**Use when:** Managing app state in iOS.

### @State (Local State)

```swift
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("Increment") {
                count += 1
            }
        }
    }
}
```

### @Observable (iOS 18+)

```swift
import Observation

@Observable
class UserViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    func fetchUsers() async {
        isLoading = true
        defer { isLoading = false }

        do {
            users = try await APIService.shared.getUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

struct UsersView: View {
    @State private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task {
            await viewModel.fetchUsers()
        }
    }
}
```

### @Environment (Global State)

```swift
@Observable
class AuthManager {
    var isAuthenticated = false
    var user: User?

    func login(email: String, password: String) async throws {
        // Login logic
        isAuthenticated = true
    }

    func logout() {
        isAuthenticated = false
        user = nil
    }
}

@main
struct MyApp: App {
    @State private var authManager = AuthManager()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environment(authManager)
        }
    }
}

struct ProfileView: View {
    @Environment(AuthManager.self) private var authManager

    var body: some View {
        if authManager.isAuthenticated {
            Text("Welcome, \(authManager.user?.name ?? "")")
        }
    }
}
```

**Checklist:**
- [ ] @State for local UI state
- [ ] @Observable for view models (iOS 18+)
- [ ] @Environment for global state
- [ ] Async/await for async operations

---

## State Management (Android - Jetpack Compose)

**Use when:** Managing app state in Android.

### remember (Local State)

```kotlin
@Composable
fun CounterScreen() {
    var count by remember { mutableStateOf(0) }

    Column {
        Text("Count: $count")
        Button(onClick = { count++ }) {
            Text("Increment")
        }
    }
}
```

### ViewModel (Screen-Level)

```kotlin
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    private val _isLoading = MutableStateFlow(false)
    val isLoading: StateFlow<Boolean> = _isLoading.asStateFlow()

    fun fetchUsers() {
        viewModelScope.launch {
            _isLoading.value = true
            try {
                _users.value = apiService.getUsers()
            } catch (e: Exception) {
                // Handle error
            } finally {
                _isLoading.value = false
            }
        }
    }
}

@Composable
fun UsersScreen(viewModel: UserViewModel = viewModel()) {
    val users by viewModel.users.collectAsState()
    val isLoading by viewModel.isLoading.collectAsState()

    LaunchedEffect(Unit) {
        viewModel.fetchUsers()
    }

    if (isLoading) {
        CircularProgressIndicator()
    } else {
        LazyColumn {
            items(users) { user ->
                Text(user.name)
            }
        }
    }
}
```

**Checklist:**
- [ ] remember for local state
- [ ] ViewModel for business logic
- [ ] StateFlow for observable state
- [ ] collectAsState for UI updates
- [ ] viewModelScope for coroutines

---

## Network Requests (iOS)

**Use when:** Making API calls in iOS apps.

### URLSession with async/await

```swift
struct APIService {
    static let shared = APIService()
    private let baseURL = "https://api.example.com"

    func getUsers() async throws -> [User] {
        guard let url = URL(string: "\(baseURL)/users") else {
            throw APIError.invalidURL
        }

        let (data, response) = try await URLSession.shared.data(from: url)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError
        }

        let users = try JSONDecoder().decode([User].self, from: data)
        return users
    }

    func createUser(_ user: CreateUserRequest) async throws -> User {
        guard let url = URL(string: "\(baseURL)/users") else {
            throw APIError.invalidURL
        }

        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(user)

        let (data, response) = try await URLSession.shared.data(for: request)

        guard let httpResponse = response as? HTTPURLResponse,
              (200...299).contains(httpResponse.statusCode) else {
            throw APIError.serverError
        }

        return try JSONDecoder().decode(User.self, from: data)
    }
}

enum APIError: Error {
    case invalidURL
    case serverError
    case decodingError
}
```

**Checklist:**
- [ ] Error handling
- [ ] Response validation
- [ ] JSON encoding/decoding
- [ ] Authentication headers
- [ ] Request timeout configuration
- [ ] Network reachability check

---

## Network Requests (Android)

**Use when:** Making API calls in Android apps.

### Retrofit with Coroutines

```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(): List<User>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): User

    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(
        @Path("id") id: String,
        @Body user: UpdateUserRequest
    ): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String)
}

object RetrofitClient {
    private const val BASE_URL = "https://api.example.com/"

    val apiService: ApiService by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(ApiService::class.java)
    }
}

// Usage in ViewModel
class UserViewModel : ViewModel() {
    fun fetchUsers() {
        viewModelScope.launch {
            try {
                val users = RetrofitClient.apiService.getUsers()
                _users.value = users
            } catch (e: Exception) {
                _error.value = e.message
            }
        }
    }
}
```

**Checklist:**
- [ ] Retrofit interface defined
- [ ] Coroutines for async calls
- [ ] Error handling
- [ ] Authentication interceptor
- [ ] Logging interceptor (debug)
- [ ] Network timeout configuration

---

## Local Storage (iOS - Core Data)

**Use when:** Persisting data locally in iOS.

### Core Data Setup

```swift
class PersistenceController {
    static let shared = PersistenceController()

    let container: NSPersistentContainer

    init() {
        container = NSPersistentContainer(name: "Model")
        container.loadPersistentStores { description, error in
            if let error = error {
                fatalError("Core Data failed to load: \(error)")
            }
        }
    }

    func save() {
        let context = container.viewContext
        if context.hasChanges {
            do {
                try context.save()
            } catch {
                print("Failed to save: \(error)")
            }
        }
    }
}

// CRUD Operations
class UserRepository {
    private let context = PersistenceController.shared.container.viewContext

    func fetchUsers() -> [UserEntity] {
        let request = UserEntity.fetchRequest()
        do {
            return try context.fetch(request)
        } catch {
            print("Failed to fetch users: \(error)")
            return []
        }
    }

    func createUser(name: String, email: String) {
        let user = UserEntity(context: context)
        user.id = UUID()
        user.name = name
        user.email = email
        PersistenceController.shared.save()
    }

    func deleteUser(_ user: UserEntity) {
        context.delete(user)
        PersistenceController.shared.save()
    }
}
```

**Checklist:**
- [ ] Data model defined
- [ ] Persistent container initialized
- [ ] Context management
- [ ] Error handling
- [ ] Background context for heavy operations

---

## Local Storage (Android - Room)

**Use when:** Persisting data locally in Android.

### Room Setup

```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val name: String,
    val email: String,
    val createdAt: Long
)

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: String): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Update
    suspend fun update(user: UserEntity)

    @Delete
    suspend fun delete(user: UserEntity)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}

@Database(entities = [UserEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "app_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}

// Repository
class UserRepository(private val userDao: UserDao) {
    val allUsers: Flow<List<UserEntity>> = userDao.getAll()

    suspend fun insert(user: UserEntity) {
        userDao.insert(user)
    }

    suspend fun delete(user: UserEntity) {
        userDao.delete(user)
    }
}
```

**Checklist:**
- [ ] Entity classes defined
- [ ] DAO interfaces created
- [ ] Database class configured
- [ ] Migration strategy
- [ ] Type converters for complex types
- [ ] Flow for reactive queries

---

## Authentication (iOS)

**Use when:** Implementing user authentication.

### Token Storage (Keychain)

```swift
import Security

class KeychainManager {
    static let shared = KeychainManager()

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

**Checklist:**
- [ ] Secure token storage (Keychain)
- [ ] Token refresh logic
- [ ] Biometric authentication
- [ ] Session management
- [ ] Logout functionality

---

## Authentication (Android)

**Use when:** Implementing user authentication.

### Token Storage (EncryptedSharedPreferences)

```kotlin
class SecureStorage(context: Context) {
    private val sharedPreferences = EncryptedSharedPreferences.create(
        "secure_prefs",
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        context,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveToken(token: String) {
        sharedPreferences.edit()
            .putString("auth_token", token)
            .apply()
    }

    fun getToken(): String? {
        return sharedPreferences.getString("auth_token", null)
    }

    fun clearToken() {
        sharedPreferences.edit()
            .remove("auth_token")
            .apply()
    }
}
```

---

## Push Notifications (iOS)

**Use when:** Implementing push notifications.

### APNs Setup

```swift
import UserNotifications

class NotificationManager: NSObject, UNUserNotificationCenterDelegate {
    static let shared = NotificationManager()

    func requestAuthorization() {
        UNUserNotificationCenter.current().requestAuthorization(
            options: [.alert, .sound, .badge]
        ) { granted, error in
            if granted {
                DispatchQueue.main.async {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
        }
    }

    // In AppDelegate
    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        print("Device Token: \(token)")
        // Send token to your server
    }

    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        completionHandler([.banner, .sound])
    }
}
```

**Checklist:**
- [ ] Permission requested
- [ ] Device token obtained
- [ ] Token sent to server
- [ ] Notification handling (foreground/background)
- [ ] Deep linking from notifications

---

## Push Notifications (Android)

**Use when:** Implementing push notifications.

### FCM Setup

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)
        Log.d("FCM", "Token: $token")
        // Send token to your server
    }

    override fun onMessageReceived(remoteMessage: RemoteMessage) {
        super.onMessageReceived(remoteMessage)

        remoteMessage.notification?.let {
            showNotification(it.title, it.body)
        }
    }

    private fun showNotification(title: String?, body: String?) {
        val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(title)
            .setContentText(body)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .build()

        notificationManager.notify(0, notification)
    }
}
```

---

This reference provides comprehensive platform-specific patterns for building production-ready mobile applications on iOS and Android.
