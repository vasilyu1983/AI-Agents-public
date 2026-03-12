# Android Testing Patterns Reference (Kotlin + Jetpack Compose)

Comprehensive guide to testing Android applications with JUnit, MockK, Compose UI Testing, and modern testing patterns.

---

## Table of Contents

1. [Unit Testing ViewModels](#unit-testing-viewmodels)
2. [Testing Coroutines & Flow](#testing-coroutines--flow)
3. [Compose UI Testing](#compose-ui-testing)
4. [Testing Repository Layer](#testing-repository-layer)
5. [End-to-End Testing](#end-to-end-testing)

---

## Unit Testing ViewModels

**Use when:** Testing business logic in ViewModels.

### Basic ViewModel Test

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    private val testDispatcher = StandardTestDispatcher()
    private lateinit var repository: UserRepository
    private lateinit var viewModel: UserViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        repository = mockk()
        viewModel = UserViewModel(repository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `loadUser success updates UI state`() = runTest {
        // Given
        val user = User(id = "1", name = "John")
        coEvery { repository.getUser("1") } returns Result.success(user)

        // When
        viewModel.loadUser("1")
        testDispatcher.scheduler.advanceUntilIdle()

        // Then
        assertEquals(user, viewModel.uiState.value.user)
        assertFalse(viewModel.uiState.value.isLoading)
        assertNull(viewModel.uiState.value.error)
    }

    @Test
    fun `loadUser failure shows error`() = runTest {
        // Given
        coEvery { repository.getUser(any()) } returns Result.failure(Exception("Network error"))

        // When
        viewModel.loadUser("1")
        testDispatcher.scheduler.advanceUntilIdle()

        // Then
        assertNull(viewModel.uiState.value.user)
        assertFalse(viewModel.uiState.value.isLoading)
        assertEquals("Network error", viewModel.uiState.value.error)
    }
}
```

### Testing with Turbine (Flow Testing)

```kotlin
@Test
fun `searchQuery emits filtered results`() = runTest {
    // Given
    val allUsers = listOf(User("1", "John"), User("2", "Jane"))
    coEvery { repository.getUsers() } returns allUsers

    // When/Then
    viewModel.searchResults.test {
        viewModel.setSearchQuery("John")
        assertEquals(listOf(User("1", "John")), awaitItem())
    }
}
```

---

## Testing Coroutines & Flow

**Use when:** Testing asynchronous code with coroutines and flows.

### Testing Suspend Functions

```kotlin
@Test
fun `fetchData returns correct data`() = runTest {
    // Given
    val expected = Data("test")
    coEvery { apiService.getData() } returns expected

    // When
    val result = repository.fetchData()

    // Then
    assertEquals(expected, result)
    coVerify { apiService.getData() }
}
```

### Testing Flow with Turbine

```kotlin
@Test
fun `user flow emits all users`() = runTest {
    // Given
    val users = listOf(User("1", "John"), User("2", "Jane"))
    coEvery { dao.getAllUsers() } returns flowOf(users)

    // When/Then
    repository.getUsersFlow().test {
        assertEquals(users, awaitItem())
        awaitComplete()
    }
}

@Test
fun `posts flow handles errors`() = runTest {
    // Given
    coEvery { apiService.getPosts() } throws IOException()

    // When/Then
    repository.getPostsFlow().test {
        assertTrue(awaitItem().isEmpty()) // Error handling returns empty list
        awaitComplete()
    }
}
```

### Testing StateFlow

```kotlin
@Test
fun `uiState updates correctly`() = runTest {
    // Given
    val user = User("1", "John")
    coEvery { repository.getUser(any()) } returns Result.success(user)

    // When
    val states = mutableListOf<UserUiState>()
    val job = launch {
        viewModel.uiState.collect { states.add(it) }
    }

    viewModel.loadUser("1")
    advanceUntilIdle()

    // Then
    assertTrue(states[0].isLoading) // Initial loading state
    assertEquals(user, states[1].user) // Success state
    assertFalse(states[1].isLoading)

    job.cancel()
}
```

---

## Compose UI Testing

**Use when:** Testing Compose UI components.

### Basic Compose Test

```kotlin
class LoginScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun `login button is disabled when fields are empty`() {
        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onLoginSuccess = {}
            )
        }

        composeTestRule
            .onNodeWithText("Sign In")
            .assertIsNotEnabled()
    }

    @Test
    fun `clicking login with valid credentials calls viewModel`() {
        val viewModel = mockk<LoginViewModel>(relaxed = true)

        composeTestRule.setContent {
            LoginScreen(
                onNavigateToRegister = {},
                onLoginSuccess = {},
                viewModel = viewModel
            )
        }

        // Enter credentials
        composeTestRule
            .onNodeWithText("Email")
            .performTextInput("test@example.com")

        composeTestRule
            .onNodeWithText("Password")
            .performTextInput("password123")

        // Click login
        composeTestRule
            .onNodeWithText("Sign In")
            .performClick()

        // Verify
        verify { viewModel.login("test@example.com", "password123") }
    }
}
```

### Testing Lists

```kotlin
@Test
fun `user list displays all users`() {
    val users = listOf(
        User("1", "John"),
        User("2", "Jane"),
        User("3", "Bob")
    )

    composeTestRule.setContent {
        UserList(users = users)
    }

    users.forEach { user ->
        composeTestRule
            .onNodeWithText(user.name)
            .assertIsDisplayed()
    }
}

@Test
fun `clicking user item navigates to detail`() {
    var clickedUserId: String? = null

    composeTestRule.setContent {
        UserList(
            users = listOf(User("1", "John")),
            onUserClick = { clickedUserId = it }
        )
    }

    composeTestRule
        .onNodeWithText("John")
        .performClick()

    assertEquals("1", clickedUserId)
}
```

### Testing with Semantics

```kotlin
@Composable
fun LoadingButton(onClick: () -> Unit, isLoading: Boolean) {
    Button(
        onClick = onClick,
        modifier = Modifier.semantics { testTag = "loading_button" }
    ) {
        if (isLoading) {
            CircularProgressIndicator(
                modifier = Modifier.semantics { testTag = "loading_indicator" }
            )
        } else {
            Text("Submit")
        }
    }
}

@Test
fun `shows loading indicator when loading`() {
    composeTestRule.setContent {
        LoadingButton(onClick = {}, isLoading = true)
    }

    composeTestRule
        .onNodeWithTag("loading_indicator")
        .assertIsDisplayed()
}
```

---

## Testing Repository Layer

**Use when:** Testing data layer with mocked dependencies.

### Repository Test with MockK

```kotlin
class UserRepositoryTest {
    private lateinit var apiService: ApiService
    private lateinit var dao: UserDao
    private lateinit var repository: UserRepository

    @Before
    fun setup() {
        apiService = mockk()
        dao = mockk()
        repository = UserRepository(apiService, dao)
    }

    @Test
    fun `getUser fetches from API when not cached`() = runTest {
        // Given
        val userDto = UserDto("1", "john@example.com", "John")
        coEvery { dao.getUserById("1") } returns null
        coEvery { apiService.getUser("1") } returns userDto
        coEvery { dao.insert(any()) } just Runs

        // When
        val result = repository.getUser("1")

        // Then
        assertTrue(result.isSuccess)
        assertEquals("John", result.getOrNull()?.name)
        coVerify { apiService.getUser("1") }
        coVerify { dao.insert(any()) }
    }

    @Test
    fun `getUser returns cached data when available`() = runTest {
        // Given
        val cachedUser = UserEntity("1", "john@example.com", "John", 123456)
        coEvery { dao.getUserById("1") } returns cachedUser

        // When
        val result = repository.getUser("1")

        // Then
        assertTrue(result.isSuccess)
        assertEquals("John", result.getOrNull()?.name)
        coVerify(exactly = 0) { apiService.getUser(any()) }
    }
}
```

---

## End-to-End Testing

**Use when:** Testing complete user flows.

### Espresso E2E Test

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun `complete login flow`() {
        // Enter email
        onView(withId(R.id.emailField))
            .perform(typeText("test@example.com"), closeSoftKeyboard())

        // Enter password
        onView(withId(R.id.passwordField))
            .perform(typeText("password123"), closeSoftKeyboard())

        // Click login
        onView(withId(R.id.loginButton))
            .perform(click())

        // Verify navigation to home
        onView(withId(R.id.homeScreen))
            .check(matches(isDisplayed()))
    }
}
```

---

## Best Practices

1. **Unit Tests**
   - Test business logic, not implementation details
   - Use MockK for mocking
   - Test edge cases and error handling
   - Aim for 80%+ code coverage

2. **Coroutine Testing**
   - Use `runTest` for coroutine tests
   - Use `StandardTestDispatcher` for controlled execution
   - Test cancellation scenarios
   - Use Turbine for Flow testing

3. **Compose Testing**
   - Use semantic properties for test identifiers
   - Test user interactions, not internal state
   - Use `composeTestRule` for UI tests
   - Test accessibility

4. **Integration Tests**
   - Test repository layer with mocked services
   - Verify caching behavior
   - Test error handling
   - Use in-memory databases for tests

5. **E2E Tests**
   - Test critical user flows
   - Keep tests stable and deterministic
   - Use page objects for maintainability
   - Run on CI pipeline

---

This reference provides comprehensive testing patterns for building reliable, well-tested Android applications.
