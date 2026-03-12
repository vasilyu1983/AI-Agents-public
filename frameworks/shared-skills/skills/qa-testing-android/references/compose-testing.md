# Jetpack Compose Testing Guide

UI testing patterns for Jetpack Compose applications.

**Official docs**: [Compose Testing](https://developer.android.com/develop/ui/compose/testing)

## Setup

### Dependencies

```kotlin
// app/build.gradle.kts
dependencies {
    // Preferred: version catalogs + Compose BOM alignment (names may vary in your project).
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
}
```

Notes:
- Compose UI tests are typically instrumented (`androidTest/`) and run on an emulator/real device.
- If you do not use version catalogs, apply the Compose BOM in `androidTestImplementation(...)` and keep versions aligned with your app module.
- Robolectric is great for JVM unit tests, but Compose UI test support is limited and stack-dependent; validate before adopting for UI.

### Test Rules

```kotlin
// Compose-only test (no Activity)
@get:Rule
val composeTestRule = createComposeRule()

// With Activity (for integration tests)
@get:Rule
val composeTestRule = createAndroidComposeRule<MainActivity>()
```

## Finding Elements

### By TestTag (Recommended)

```kotlin
// In Composable
Button(
    onClick = { },
    modifier = Modifier.testTag("loginButton")
) {
    Text("Login")
}

// In Test
composeTestRule.onNodeWithTag("loginButton")
    .performClick()
```

### By Text

```kotlin
composeTestRule.onNodeWithText("Login")
    .assertIsDisplayed()

// Substring match
composeTestRule.onNodeWithText("Log", substring = true)
    .assertExists()

// Ignore case
composeTestRule.onNodeWithText("login", ignoreCase = true)
    .assertExists()
```

### By Content Description

```kotlin
// In Composable
Icon(
    imageVector = Icons.Default.Search,
    contentDescription = "Search",
    modifier = Modifier.semantics {
        contentDescription = "Search button"
    }
)

// In Test
composeTestRule.onNodeWithContentDescription("Search button")
    .performClick()
```

### Multiple Nodes

```kotlin
// Find all matching nodes
composeTestRule.onAllNodesWithTag("listItem")
    .assertCountEquals(5)

// Get specific node from list
composeTestRule.onAllNodesWithTag("listItem")[0]
    .performClick()

// Filter nodes
composeTestRule.onAllNodesWithTag("listItem")
    .filter(hasText("Important"))
    .assertCountEquals(2)
```

### Hierarchical Finders

```kotlin
// Child of specific node
composeTestRule.onNodeWithTag("card")
    .onChild()
    .assertTextEquals("Title")

// Children
composeTestRule.onNodeWithTag("list")
    .onChildren()
    .assertCountEquals(10)

// Ancestor
composeTestRule.onNodeWithText("Submit")
    .onAncestors()
    .filter(hasTestTag("form"))
    .assertCountEquals(1)

// Sibling
composeTestRule.onNodeWithTag("label")
    .onSibling()
    .assertHasClickAction()
```

---

## Actions

### Click and Touch

```kotlin
// Click
composeTestRule.onNodeWithTag("button")
    .performClick()

// Double click
composeTestRule.onNodeWithTag("item")
    .performTouchInput { doubleClick() }

// Long click
composeTestRule.onNodeWithTag("item")
    .performTouchInput { longClick() }

// Click at specific position
composeTestRule.onNodeWithTag("canvas")
    .performTouchInput { click(center) }
```

### Text Input

```kotlin
// Type text
composeTestRule.onNodeWithTag("emailField")
    .performTextInput("user@example.com")

// Replace text
composeTestRule.onNodeWithTag("emailField")
    .performTextReplacement("new@example.com")

// Clear text
composeTestRule.onNodeWithTag("emailField")
    .performTextClearance()

// IME action
composeTestRule.onNodeWithTag("searchField")
    .performImeAction()
```

### Scrolling

```kotlin
// Scroll to node
composeTestRule.onNodeWithTag("bottomItem")
    .performScrollTo()

// Scroll in LazyColumn
composeTestRule.onNodeWithTag("lazyList")
    .performScrollToIndex(50)

// Scroll to key
composeTestRule.onNodeWithTag("lazyList")
    .performScrollToKey("item_key")

// Swipe gestures
composeTestRule.onNodeWithTag("pager")
    .performTouchInput { swipeLeft() }
```

### Gestures

```kotlin
composeTestRule.onNodeWithTag("slider")
    .performTouchInput {
        swipeRight(
            startX = centerX - 100f,
            endX = centerX + 100f
        )
    }

composeTestRule.onNodeWithTag("zoomable")
    .performTouchInput {
        pinch(
            start0 = center - Offset(100f, 0f),
            end0 = center - Offset(200f, 0f),
            start1 = center + Offset(100f, 0f),
            end1 = center + Offset(200f, 0f)
        )
    }
```

---

## Assertions

### Existence and Visibility

```kotlin
// Exists in tree
composeTestRule.onNodeWithTag("element")
    .assertExists()

// Does not exist
composeTestRule.onNodeWithTag("element")
    .assertDoesNotExist()

// Is displayed (visible on screen)
composeTestRule.onNodeWithTag("element")
    .assertIsDisplayed()

// Is not displayed
composeTestRule.onNodeWithTag("element")
    .assertIsNotDisplayed()
```

### State Assertions

```kotlin
// Enabled/Disabled
composeTestRule.onNodeWithTag("button")
    .assertIsEnabled()
composeTestRule.onNodeWithTag("button")
    .assertIsNotEnabled()

// Selected
composeTestRule.onNodeWithTag("tab")
    .assertIsSelected()

// Focused
composeTestRule.onNodeWithTag("field")
    .assertIsFocused()

// Checked (for toggles)
composeTestRule.onNodeWithTag("checkbox")
    .assertIsOn()
composeTestRule.onNodeWithTag("checkbox")
    .assertIsOff()
```

### Content Assertions

```kotlin
// Text content
composeTestRule.onNodeWithTag("title")
    .assertTextEquals("Welcome")

// Contains text
composeTestRule.onNodeWithTag("paragraph")
    .assertTextContains("important")

// Content description
composeTestRule.onNodeWithTag("image")
    .assertContentDescriptionEquals("Profile photo")
```

### Custom Assertions

```kotlin
composeTestRule.onNodeWithTag("customView")
    .assert(hasText("Expected"))
    .assert(isEnabled())
    .assert(hasClickAction())

// Using SemanticsMatcher
composeTestRule.onNode(
    hasText("Label") and hasClickAction()
).assertExists()
```

---

## Synchronization

### Wait for Idle

```kotlin
// Wait for all pending compositions
composeTestRule.waitForIdle()

// Advance time (for animations)
composeTestRule.mainClock.advanceTimeBy(1000)

// Auto-advance disabled (manual control)
composeTestRule.mainClock.autoAdvance = false
composeTestRule.mainClock.advanceTimeByFrame()
```

### Wait Until

```kotlin
// Wait for condition
composeTestRule.waitUntil(timeoutMillis = 5000) {
    composeTestRule.onAllNodesWithTag("item")
        .fetchSemanticsNodes().size >= 10
}

// Wait for node to exist
composeTestRule.waitUntil {
    composeTestRule.onNodeWithTag("loaded")
        .fetchSemanticsNodes().isNotEmpty()
}
```

### IdlingResource Integration

```kotlin
// Register IdlingResource for Espresso interop
@Before
fun setUp() {
    composeTestRule.registerIdlingResource(networkIdlingResource)
}

@After
fun tearDown() {
    composeTestRule.unregisterIdlingResource(networkIdlingResource)
}
```

---

## Testing Patterns

### Test in Isolation

```kotlin
@Test
fun loginButton_whenCredentialsEntered_isEnabled() {
    var isEnabled = false

    composeTestRule.setContent {
        LoginButton(
            email = "user@example.com",
            password = "password",
            onEnabledChange = { isEnabled = it }
        )
    }

    composeTestRule.onNodeWithTag("loginButton")
        .assertIsEnabled()
}
```

### Test with ViewModel

```kotlin
@Test
fun loginScreen_showsLoadingState() {
    val viewModel = LoginViewModel(FakeAuthRepository())

    composeTestRule.setContent {
        LoginScreen(viewModel = viewModel)
    }

    // Trigger loading
    composeTestRule.onNodeWithTag("loginButton")
        .performClick()

    // Verify loading indicator
    composeTestRule.onNodeWithTag("loadingIndicator")
        .assertIsDisplayed()
}
```

### Test Navigation

```kotlin
@Test
fun loginSuccess_navigatesToHome() {
    val navController = TestNavHostController(
        ApplicationProvider.getApplicationContext()
    )
    navController.setGraph(R.navigation.nav_graph)

    composeTestRule.setContent {
        AppNavigation(navController = navController)
    }

    // Perform login
    composeTestRule.onNodeWithTag("emailField")
        .performTextInput("user@example.com")
    composeTestRule.onNodeWithTag("passwordField")
        .performTextInput("password")
    composeTestRule.onNodeWithTag("loginButton")
        .performClick()

    // Verify navigation
    composeTestRule.waitUntil {
        navController.currentDestination?.route == "home"
    }
}
```

### Test State Restoration

```kotlin
@Test
fun textField_preservesStateOnRecreation() {
    val restorationTester = StateRestorationTester(composeTestRule)

    restorationTester.setContent {
        var text by rememberSaveable { mutableStateOf("") }
        TextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier.testTag("textField")
        )
    }

    // Enter text
    composeTestRule.onNodeWithTag("textField")
        .performTextInput("Hello")

    // Simulate recreation
    restorationTester.emulateSavedInstanceStateRestore()

    // Verify text preserved
    composeTestRule.onNodeWithTag("textField")
        .assertTextEquals("Hello")
}
```

---

## LazyColumn/LazyRow Testing

### Scroll to Item

```kotlin
@Test
fun lazyColumn_scrollsToItem() {
    composeTestRule.setContent {
        LazyColumn(Modifier.testTag("list")) {
            items(100) { index ->
                Text(
                    text = "Item $index",
                    modifier = Modifier.testTag("item_$index")
                )
            }
        }
    }

    // Scroll to item 50
    composeTestRule.onNodeWithTag("list")
        .performScrollToIndex(50)

    // Verify item is visible
    composeTestRule.onNodeWithTag("item_50")
        .assertIsDisplayed()
}
```

### Test Dynamic Content

```kotlin
@Test
fun lazyColumn_displaysAllItems() {
    val items = List(20) { "Item $it" }

    composeTestRule.setContent {
        LazyColumn(Modifier.testTag("list")) {
            items(items) { item ->
                Text(item, Modifier.testTag(item))
            }
        }
    }

    // Check first items visible
    composeTestRule.onNodeWithTag("Item 0")
        .assertIsDisplayed()

    // Scroll and check last item
    composeTestRule.onNodeWithTag("list")
        .performScrollToIndex(19)
    composeTestRule.onNodeWithTag("Item 19")
        .assertIsDisplayed()
}
```

---

## Screenshot Testing

### Basic Screenshot

```kotlin
@Test
fun loginScreen_matchesSnapshot() {
    composeTestRule.setContent {
        LoginScreen()
    }

    val image = composeTestRule.onRoot().captureToImage()
    // Persist/compare `image` using your snapshot tool (Shot/Roborazzi/Paparazzi/etc).
}
```

### With Paparazzi (JVM)

```kotlin
// No device needed
class LoginScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun loginScreen() {
        paparazzi.snapshot {
            LoginScreen()
        }
    }

    @Test
    fun loginScreen_error() {
        paparazzi.snapshot {
            LoginScreen(error = "Invalid credentials")
        }
    }
}
```

---

## Debugging

### Print Semantics Tree

```kotlin
@Test
fun debug_printTree() {
    composeTestRule.setContent {
        LoginScreen()
    }

    // Print full tree
    composeTestRule.onRoot().printToLog("COMPOSE_TREE")

    // Print unmerged tree (more detail)
    composeTestRule.onRoot(useUnmergedTree = true)
        .printToLog("UNMERGED_TREE")
}
```

### Use Unmerged Tree

```kotlin
// When merged semantics hide nodes
composeTestRule.onNodeWithTag("innerElement", useUnmergedTree = true)
    .assertExists()
```

---

## Best Practices

### Do

- Use `testTag` for stable element identification
- Test composables in isolation when possible
- Use `waitUntil` for async operations
- Test state restoration with `StateRestorationTester`
- Keep tests focused on behavior, not implementation

### Avoid

- Relying on text that changes with locale
- Using `Thread.sleep()` for timing
- Testing implementation details
- Over-specifying assertions
- Ignoring flaky test warnings

---

## Resources

- [Compose Testing Documentation](https://developer.android.com/develop/ui/compose/testing)
- [Testing Codelab](https://developer.android.com/codelabs/jetpack-compose-testing)
- [Common Testing Patterns](https://developer.android.com/develop/ui/compose/testing/common-patterns)
- [Semantics in Compose](https://developer.android.com/develop/ui/compose/accessibility/semantics)
