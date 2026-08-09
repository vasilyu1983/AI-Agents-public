# Kotlin Coroutines Patterns Reference

Comprehensive guide to Kotlin Coroutines patterns including Flow, StateFlow, Channels, and advanced async techniques for Android development.

---

## Table of Contents

1. [Coroutine Scope Management](#coroutine-scope-management)
2. [Flow for Streaming Data](#flow-for-streaming-data)
3. [StateFlow & SharedFlow](#stateflow--sharedflow)
4. [Channels for Communication](#channels-for-communication)
5. [Advanced Patterns](#advanced-patterns)

---

## Coroutine Scope Management

**Use when:** Managing lifecycle-aware coroutines in Android components.

### ViewModel Scope

```kotlin
class UserViewModel : ViewModel() {
    private val _users = MutableStateFlow<List<User>>(emptyList())
    val users: StateFlow<List<User>> = _users.asStateFlow()

    fun fetchUsers() {
        viewModelScope.launch {
            try {
                val result = apiService.getUsers()
                _users.value = result
            } catch (e: Exception) {
                // Handle error
            }
        }
    }

    // Coroutine is automatically cancelled when ViewModel is cleared
}
```

### Lifecycle Scope

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        lifecycleScope.launch {
            // Cancelled when lifecycle is destroyed
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { state ->
                    updateUI(state)
                }
            }
        }
    }
}
```

### Custom Scope with SupervisorJob

```kotlin
class DataRepository {
    private val scope = CoroutineScope(
        SupervisorJob() + Dispatchers.IO
    )

    fun fetchData() {
        scope.launch {
            // Job failure doesn't cancel sibling jobs
            try {
                val data = apiService.getData()
                processData(data)
            } catch (e: Exception) {
                handleError(e)
            }
        }
    }

    fun cleanup() {
        scope.cancel()
    }
}
```

**Checklist:**
- [ ] Use viewModelScope for ViewModel coroutines
- [ ] Use lifecycleScope for Activity/Fragment
- [ ] Use SupervisorJob for independent child jobs
- [ ] Cancel scopes in cleanup methods
- [ ] Use appropriate dispatchers (IO, Main, Default)

---

## Flow for Streaming Data

**Use when:** Processing streams of asynchronous data with backpressure.

### Flow Builders

```kotlin
// Cold flow - starts emitting when collected
fun getUsers(): Flow<List<User>> = flow {
    val users = apiService.getUsers()
    emit(users)
}

// Flow from callback
fun locationUpdates(): Flow<Location> = callbackFlow {
    val callback = object : LocationCallback() {
        override fun onLocationResult(result: LocationResult) {
            trySend(result.lastLocation)
        }
    }

    locationManager.requestLocationUpdates(callback)

    awaitClose {
        locationManager.removeUpdates(callback)
    }
}

// Flow from LiveData
val userFlow: Flow<User> = userLiveData.asFlow()
```

### Flow Operators

```kotlin
class PostRepository {
    fun getPostsStream(): Flow<List<Post>> = flow {
        while (true) {
            val posts = apiService.getPosts()
            emit(posts)
            delay(30_000) // Refresh every 30 seconds
        }
    }
        .map { posts -> posts.filter { it.isPublished } }
        .distinctUntilChanged()
        .catch { e -> emit(emptyList()) }
        .flowOn(Dispatchers.IO)
}

// Usage in ViewModel
class PostViewModel : ViewModel() {
    val posts: StateFlow<List<Post>> = repository.getPostsStream()
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

### Combining Flows

```kotlin
class FeedViewModel : ViewModel() {
    private val posts = repository.getPostsFlow()
    private val filter = MutableStateFlow(PostFilter.ALL)

    val filteredPosts: StateFlow<List<Post>> = combine(
        posts,
        filter
    ) { posts, filter ->
        when (filter) {
            PostFilter.ALL -> posts
            PostFilter.STARRED -> posts.filter { it.isStarred }
            PostFilter.RECENT -> posts.filter {
                it.createdAt > System.currentTimeMillis() - 86400_000
            }
        }
    }.stateIn(
        scope = viewModelScope,
        started = SharingStarted.WhileSubscribed(5000),
        initialValue = emptyList()
    )

    fun setFilter(newFilter: PostFilter) {
        filter.value = newFilter
    }
}
```

**Checklist:**
- [ ] Use `flow { }` for cold flows
- [ ] Use `callbackFlow` for callback-based APIs
- [ ] Apply operators (map, filter, catch, etc.)
- [ ] Use `flowOn()` to specify dispatcher
- [ ] Convert to StateFlow with `stateIn()`

---

## StateFlow & SharedFlow

**Use when:** Sharing state or events between components.

### StateFlow for State

```kotlin
class UserViewModel : ViewModel() {
    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    fun loadUser(id: String) {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }

            try {
                val user = repository.getUser(id)
                _uiState.update {
                    it.copy(
                        user = user,
                        isLoading = false
                    )
                }
            } catch (e: Exception) {
                _uiState.update {
                    it.copy(
                        error = e.message,
                        isLoading = false
                    )
                }
            }
        }
    }
}

data class UserUiState(
    val user: User? = null,
    val isLoading: Boolean = false,
    val error: String? = null
)
```

### SharedFlow for Events

```kotlin
class EventBus {
    private val _events = MutableSharedFlow<Event>(
        replay = 0,
        extraBufferCapacity = 1,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val events: SharedFlow<Event> = _events.asSharedFlow()

    suspend fun emit(event: Event) {
        _events.emit(event)
    }
}

// Usage in ViewModel
class MainViewModel(private val eventBus: EventBus) : ViewModel() {
    init {
        viewModelScope.launch {
            eventBus.events.collect { event ->
                when (event) {
                    is Event.UserLoggedIn -> handleLogin(event.user)
                    is Event.UserLoggedOut -> handleLogout()
                }
            }
        }
    }
}
```

### SharedFlow with Replay

```kotlin
class LocationRepository {
    private val _locations = MutableSharedFlow<Location>(
        replay = 1, // Cache last location for new collectors
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val locations: SharedFlow<Location> = _locations.asSharedFlow()

    suspend fun updateLocation(location: Location) {
        _locations.emit(location)
    }
}
```

**Checklist:**
- [ ] Use StateFlow for UI state (always has value)
- [ ] Use SharedFlow for one-time events
- [ ] Use `update { }` for atomic state updates
- [ ] Set appropriate replay/buffer settings
- [ ] Expose read-only flows with `asStateFlow()`/`asSharedFlow()`

---

## Channels for Communication

**Use when:** Sending values between coroutines with buffering.

### Channel Basics

```kotlin
class DownloadManager {
    private val downloadChannel = Channel<Download>(Channel.BUFFERED)

    fun enqueueDownload(url: String) {
        scope.launch {
            downloadChannel.send(Download(url))
        }
    }

    init {
        scope.launch {
            for (download in downloadChannel) {
                processDownload(download)
            }
        }
    }

    private suspend fun processDownload(download: Download) {
        // Download file
    }
}
```

### Channel with Select

```kotlin
suspend fun selectFromMultipleSources(
    channel1: ReceiveChannel<Data>,
    channel2: ReceiveChannel<Data>
) {
    select<Unit> {
        channel1.onReceive { data ->
            println("Received from channel1: $data")
        }
        channel2.onReceive { data ->
            println("Received from channel2: $data")
        }
    }
}
```

### Producer-Consumer Pattern

```kotlin
fun CoroutineScope.produceNumbers() = produce<Int> {
    var x = 1
    while (true) {
        send(x++)
        delay(100)
    }
}

fun CoroutineScope.square(numbers: ReceiveChannel<Int>) = produce<Int> {
    for (x in numbers) {
        send(x * x)
    }
}

// Usage
val numbers = produceNumbers()
val squares = square(numbers)

for (i in 1..5) {
    println(squares.receive())
}
```

**Checklist:**
- [ ] Use Channel for buffered communication
- [ ] Choose appropriate channel capacity
- [ ] Close channels when done
- [ ] Use `produce` for channel builders
- [ ] Handle channel cancellation

---

## Advanced Patterns

### Debouncing User Input

```kotlin
class SearchViewModel : ViewModel() {
    private val searchQuery = MutableStateFlow("")

    val searchResults: StateFlow<List<Result>> = searchQuery
        .debounce(300)
        .filter { it.isNotBlank() }
        .distinctUntilChanged()
        .flatMapLatest { query ->
            flow {
                emit(apiService.search(query))
            }.catch { e ->
                emit(emptyList())
            }
        }
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )

    fun onSearchQueryChanged(query: String) {
        searchQuery.value = query
    }
}
```

### Retry with Exponential Backoff

```kotlin
suspend fun <T> retryWithBackoff(
    maxRetries: Int = 3,
    initialDelay: Long = 1000,
    factor: Double = 2.0,
    block: suspend () -> T
): T {
    var currentDelay = initialDelay
    repeat(maxRetries) { attempt ->
        try {
            return block()
        } catch (e: Exception) {
            if (attempt == maxRetries - 1) throw e
            delay(currentDelay)
            currentDelay = (currentDelay * factor).toLong()
        }
    }
    throw IllegalStateException("Unreachable")
}

// Usage
val users = retryWithBackoff {
    apiService.getUsers()
}
```

### Parallel Async with async/await

```kotlin
class UserRepository {
    suspend fun fetchUserWithDetails(userId: String): UserDetails {
        return coroutineScope {
            val userDeferred = async { apiService.getUser(userId) }
            val postsDeferred = async { apiService.getUserPosts(userId) }
            val friendsDeferred = async { apiService.getUserFriends(userId) }

            UserDetails(
                user = userDeferred.await(),
                posts = postsDeferred.await(),
                friends = friendsDeferred.await()
            )
        }
    }
}
```

### Limiting Concurrency

```kotlin
class ImageDownloader {
    private val semaphore = Semaphore(5) // Max 5 concurrent downloads

    suspend fun downloadImages(urls: List<String>): List<Image> {
        return coroutineScope {
            urls.map { url ->
                async {
                    semaphore.withPermit {
                        downloadImage(url)
                    }
                }
            }.awaitAll()
        }
    }

    private suspend fun downloadImage(url: String): Image {
        // Download image
        delay(1000)
        return Image(url)
    }
}
```

### Timeout and withContext

```kotlin
class ApiRepository {
    suspend fun fetchDataWithTimeout(): Result<Data> {
        return try {
            withTimeout(5000) { // 5 second timeout
                withContext(Dispatchers.IO) {
                    val data = apiService.getData()
                    Result.success(data)
                }
            }
        } catch (e: TimeoutCancellationException) {
            Result.failure(Exception("Request timed out"))
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
}
```

### Cancellation and Cleanup

```kotlin
class FileProcessor {
    suspend fun processFile(file: File) {
        try {
            val stream = file.inputStream()
            try {
                processStream(stream)
            } finally {
                stream.close() // Cleanup even if cancelled
            }
        } catch (e: CancellationException) {
            println("Processing cancelled")
            throw e // Re-throw to propagate cancellation
        }
    }

    private suspend fun processStream(stream: InputStream) {
        // Check for cancellation periodically
        ensureActive()

        // Or use yield()
        yield()

        // Process data
    }
}
```

---

## Best Practices

1. **Scope Management**
   - Use viewModelScope/lifecycleScope for lifecycle-aware coroutines
   - Create custom scopes with SupervisorJob for independent tasks
   - Cancel scopes in cleanup methods
   - Use appropriate dispatchers (IO for I/O, Default for CPU-intensive)

2. **Flow Usage**
   - Prefer Flow over LiveData for reactive streams
   - Use StateFlow for state that always has a value
   - Use SharedFlow for one-time events
   - Apply operators in the right order
   - Use `stateIn()` to convert cold flows to hot

3. **Error Handling**
   - Use try-catch in coroutines
   - Use `catch` operator in flows
   - Handle CancellationException separately
   - Implement retry logic for transient failures

4. **Performance**
   - Use `flowOn()` to specify dispatcher
   - Use `conflate()` for dropping intermediate values
   - Use `debounce()` for user input
   - Limit concurrency with Semaphore
   - Use `distinctUntilChanged()` to avoid redundant work

5. **Testing**
   - Use `StandardTestDispatcher` for tests
   - Use `runTest` for testing coroutines
   - Use `turbine` library for testing flows
   - Mock suspend functions with MockK

---

## Common Pitfalls

### AVOID: Blocking Main Thread

```kotlin
// Bad
fun loadData() {
    runBlocking { // Blocks UI thread!
        val data = apiService.getData()
    }
}

// Good
fun loadData() {
    viewModelScope.launch {
        val data = apiService.getData()
        updateUI(data)
    }
}
```

### AVOID: Ignoring Cancellation

```kotlin
// Bad
suspend fun processItems(items: List<Item>) {
    for (item in items) {
        process(item) // Continues even if cancelled
    }
}

// Good
suspend fun processItems(items: List<Item>) {
    for (item in items) {
        ensureActive() // Check for cancellation
        process(item)
    }
}
```

### AVOID: Flow Collection in ViewModel init

```kotlin
// Bad
class ViewModel : ViewModel() {
    init {
        repository.dataFlow.collect { // Blocks initialization!
            // Process data
        }
    }
}

// Good
class ViewModel : ViewModel() {
    val data = repository.dataFlow
        .stateIn(
            scope = viewModelScope,
            started = SharingStarted.WhileSubscribed(5000),
            initialValue = emptyList()
        )
}
```

---

This reference provides comprehensive Kotlin Coroutines patterns for building safe, performant concurrent Android applications.
