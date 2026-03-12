# Espresso Patterns and Best Practices

Advanced patterns for Espresso UI testing on Android.

**Official docs**: [Espresso](https://developer.android.com/training/testing/espresso)

---

## Core Concepts

### ViewMatchers (Find Elements)

```kotlin
// By ID
onView(withId(R.id.emailField))

// By text
onView(withText("Login"))
onView(withText(R.string.login_button))

// By content description (accessibility)
onView(withContentDescription("Submit button"))

// By hint
onView(withHint("Enter email"))

// Combining matchers
onView(allOf(
    withId(R.id.button),
    withText("Submit"),
    isDisplayed()
))

// Negation
onView(allOf(
    withId(R.id.button),
    not(isEnabled())
))

// Parent/child relationships
onView(withParent(withId(R.id.container)))
onView(isDescendantOfA(withId(R.id.form)))
onView(hasSibling(withText("Username")))

// Position in list
onData(anything())
    .inAdapterView(withId(R.id.listView))
    .atPosition(0)
```

### ViewActions (Interact)

```kotlin
// Click actions
onView(withId(R.id.button)).perform(click())
onView(withId(R.id.button)).perform(doubleClick())
onView(withId(R.id.button)).perform(longClick())

// Text input
onView(withId(R.id.field)).perform(typeText("hello"))
onView(withId(R.id.field)).perform(replaceText("new text"))
onView(withId(R.id.field)).perform(clearText())

// Keyboard
onView(withId(R.id.field)).perform(closeSoftKeyboard())
onView(withId(R.id.field)).perform(pressImeActionButton())
onView(withId(R.id.field)).perform(pressKey(KeyEvent.KEYCODE_ENTER))

// Scrolling
onView(withId(R.id.scrollView)).perform(scrollTo())
onView(withId(R.id.recyclerView)).perform(
    RecyclerViewActions.scrollToPosition<androidx.recyclerview.widget.RecyclerView.ViewHolder>(10)
)

// Swiping
onView(withId(R.id.pager)).perform(swipeLeft())
onView(withId(R.id.pager)).perform(swipeRight())
onView(withId(R.id.list)).perform(swipeUp())
```

### ViewAssertions (Verify)

```kotlin
// Visibility
onView(withId(R.id.view)).check(matches(isDisplayed()))
onView(withId(R.id.view)).check(matches(not(isDisplayed())))
onView(withId(R.id.view)).check(doesNotExist())

// State
onView(withId(R.id.button)).check(matches(isEnabled()))
onView(withId(R.id.checkbox)).check(matches(isChecked()))
onView(withId(R.id.field)).check(matches(isFocused()))
onView(withId(R.id.field)).check(matches(hasFocus()))

// Content
onView(withId(R.id.text)).check(matches(withText("Expected")))
onView(withId(R.id.text)).check(matches(withText(containsString("part"))))
onView(withId(R.id.text)).check(matches(withText(startsWith("Hello"))))

// List assertions
onView(withId(R.id.recyclerView))
    .check(matches(hasDescendant(withText("Item 1"))))
```

---

## RecyclerView Testing

### Scroll and Click

```kotlin
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.recyclerview.widget.RecyclerView

// Scroll to position
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.scrollToPosition<RecyclerView.ViewHolder>(5))

// Click item at position
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
        3, click()
    ))

// Scroll to item with text
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.scrollTo<RecyclerView.ViewHolder>(
        hasDescendant(withText("Target Item"))
    ))

// Action on item with matcher
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.actionOnItem<RecyclerView.ViewHolder>(
        hasDescendant(withText("Target Item")),
        click()
    ))
```

### Click Child View in Item

```kotlin
import android.view.View
import androidx.recyclerview.widget.RecyclerView
import androidx.test.espresso.UiController
import androidx.test.espresso.ViewAction
import androidx.test.espresso.contrib.RecyclerViewActions
import androidx.test.espresso.matcher.ViewMatchers.isAssignableFrom
import org.hamcrest.Matcher

fun clickChildViewWithId(id: Int): ViewAction {
    return object : ViewAction {
        override fun getConstraints(): Matcher<View> = isAssignableFrom(View::class.java)

        override fun getDescription() = "Click on child view with id $id"

        override fun perform(uiController: UiController, view: View) {
            val child = view.findViewById<View>(id)
            checkNotNull(child) { "No view with id $id found under ${view.javaClass.simpleName}" }
            child.performClick()
        }
    }
}

// Usage
onView(withId(R.id.recyclerView))
    .perform(RecyclerViewActions.actionOnItemAtPosition<RecyclerView.ViewHolder>(
        0, clickChildViewWithId(R.id.deleteButton)
    ))
```

### Assert Item Count

```kotlin
fun hasItemCount(count: Int): Matcher<View> {
    return object : BoundedMatcher<View, RecyclerView>(RecyclerView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has $count items")
        }

        override fun matchesSafely(view: RecyclerView): Boolean {
            return view.adapter?.itemCount == count
        }
    }
}

// Usage
onView(withId(R.id.recyclerView))
    .check(matches(hasItemCount(10)))
```

---

## Intents Testing

### Stub External Intents

```kotlin
import androidx.test.espresso.intent.Intents
import androidx.test.espresso.intent.matcher.IntentMatchers.*
import androidx.test.espresso.intent.Intents.intending
import android.app.Activity
import android.app.Instrumentation

@Before
fun setUp() {
    Intents.init()
}

@After
fun tearDown() {
    Intents.release()
}

@Test
fun pickImage_returnsSelectedImage() {
    // Stub the camera intent
    val resultData = Intent().apply {
        putExtra("data", testBitmap)
    }
    intending(hasAction(MediaStore.ACTION_IMAGE_CAPTURE))
        .respondWith(Instrumentation.ActivityResult(Activity.RESULT_OK, resultData))

    // Trigger the intent
    onView(withId(R.id.cameraButton)).perform(click())

    // Verify the result is displayed
    onView(withId(R.id.imagePreview))
        .check(matches(isDisplayed()))
}
```

### Verify Intent Was Sent

```kotlin
@Test
fun shareButton_sendsShareIntent() {
    onView(withId(R.id.shareButton)).perform(click())

    Intents.intended(allOf(
        hasAction(Intent.ACTION_SEND),
        hasType("text/plain"),
        hasExtra(Intent.EXTRA_TEXT, "Share content")
    ))
}
```

---

## Custom Matchers

### Text Color Matcher

```kotlin
fun withTextColor(expectedColor: Int): Matcher<View> {
    return object : BoundedMatcher<View, TextView>(TextView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("with text color: $expectedColor")
        }

        override fun matchesSafely(textView: TextView): Boolean {
            return textView.currentTextColor == expectedColor
        }
    }
}

// Usage
onView(withId(R.id.errorText))
    .check(matches(withTextColor(Color.RED)))
```

### Drawable Matcher

```kotlin
fun withDrawable(@DrawableRes id: Int): Matcher<View> {
    return object : BoundedMatcher<View, ImageView>(ImageView::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("with drawable resource: $id")
        }

        override fun matchesSafely(imageView: ImageView): Boolean {
            val expectedDrawable = ContextCompat.getDrawable(
                imageView.context, id
            ) ?: return false
            return imageView.drawable.constantState == expectedDrawable.constantState
        }
    }
}
```

### EditText Error Matcher

```kotlin
fun hasErrorText(expectedError: String): Matcher<View> {
    return object : BoundedMatcher<View, EditText>(EditText::class.java) {
        override fun describeTo(description: Description) {
            description.appendText("has error text: $expectedError")
        }

        override fun matchesSafely(editText: EditText): Boolean {
            return editText.error?.toString() == expectedError
        }
    }
}

// Usage
onView(withId(R.id.emailField))
    .check(matches(hasErrorText("Invalid email")))
```

---

## Handling Async Operations

### IdlingResource Pattern

```kotlin
class OkHttp3IdlingResource private constructor(
    private val name: String,
    private val dispatcher: Dispatcher
) : IdlingResource {

    @Volatile private var callback: IdlingResource.ResourceCallback? = null

    override fun getName() = name

    override fun isIdleNow(): Boolean {
        val idle = dispatcher.runningCallsCount() == 0
        if (idle) callback?.onTransitionToIdle()
        return idle
    }

    override fun registerIdleTransitionCallback(callback: ResourceCallback) {
        this.callback = callback
    }

    companion object {
        fun create(name: String, client: OkHttpClient): OkHttp3IdlingResource {
            return OkHttp3IdlingResource(name, client.dispatcher)
        }
    }
}
```

### CountingIdlingResource

```kotlin
object EspressoIdlingResource {
    private const val RESOURCE = "GLOBAL"

    @JvmField
    val countingIdlingResource = CountingIdlingResource(RESOURCE)

    fun increment() = countingIdlingResource.increment()

    fun decrement() {
        if (!countingIdlingResource.isIdleNow) {
            countingIdlingResource.decrement()
        }
    }
}

// In production code (Repository)
fun fetchData(): Flow<Data> = flow {
    EspressoIdlingResource.increment()
    try {
        val data = api.getData()
        emit(data)
    } finally {
        EspressoIdlingResource.decrement()
    }
}

// In test
@Before
fun registerIdlingResource() {
    IdlingRegistry.getInstance().register(EspressoIdlingResource.countingIdlingResource)
}

@After
fun unregisterIdlingResource() {
    IdlingRegistry.getInstance().unregister(EspressoIdlingResource.countingIdlingResource)
}
```

---

## Robot Pattern (Full Example)

```kotlin
// robots/LoginRobot.kt
class LoginRobot {
    fun enterEmail(email: String) = apply {
        onView(withId(R.id.emailField))
            .perform(replaceText(email), closeSoftKeyboard())
    }

    fun enterPassword(password: String) = apply {
        onView(withId(R.id.passwordField))
            .perform(replaceText(password), closeSoftKeyboard())
    }

    fun clickLogin() = apply {
        onView(withId(R.id.loginButton)).perform(click())
    }

    fun clickForgotPassword() = apply {
        onView(withId(R.id.forgotPasswordLink)).perform(click())
    }

    infix fun verify(func: LoginVerification.() -> Unit): LoginVerification {
        return LoginVerification().apply(func)
    }
}

class LoginVerification {
    fun dashboardIsDisplayed() {
        onView(withId(R.id.dashboardContainer))
            .check(matches(isDisplayed()))
    }

    fun errorIsDisplayed(message: String) {
        onView(withText(message))
            .check(matches(isDisplayed()))
    }

    fun emailErrorIsDisplayed() {
        onView(withId(R.id.emailError))
            .check(matches(isDisplayed()))
    }
}

// Helper function
fun login(func: LoginRobot.() -> Unit) = LoginRobot().apply(func)

// Test usage
@Test
fun successfulLogin() {
    login {
        enterEmail("user@example.com")
        enterPassword("password123")
        clickLogin()
    } verify {
        dashboardIsDisplayed()
    }
}

@Test
fun invalidEmail_showsError() {
    login {
        enterEmail("invalid")
        clickLogin()
    } verify {
        emailErrorIsDisplayed()
    }
}
```

---

## Test Annotations and Rules

### Disable Animations Rule

```kotlin
class DisableAnimationsRule : TestRule {
    override fun apply(base: Statement, description: Description): Statement {
        return object : Statement() {
            override fun evaluate() {
                // Disable animations
                InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand(
                    "settings put global window_animation_scale 0"
                )
                InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand(
                    "settings put global transition_animation_scale 0"
                )
                InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand(
                    "settings put global animator_duration_scale 0"
                )

                try {
                    base.evaluate()
                } finally {
                    // Re-enable animations
                    InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand(
                        "settings put global window_animation_scale 1"
                    )
                    InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand(
                        "settings put global transition_animation_scale 1"
                    )
                    InstrumentationRegistry.getInstrumentation().uiAutomation.executeShellCommand(
                        "settings put global animator_duration_scale 1"
                    )
                }
            }
        }
    }
}

// Usage
@get:Rule
val disableAnimationsRule = DisableAnimationsRule()
```

### Grant Permissions Rule

```kotlin
import androidx.test.rule.GrantPermissionRule

@get:Rule
val permissionRule: GrantPermissionRule = GrantPermissionRule.grant(
    android.Manifest.permission.CAMERA,
    android.Manifest.permission.ACCESS_FINE_LOCATION
)
```

---

## Debugging Tips

### Print View Hierarchy

```kotlin
// In test, when matcher fails
onView(isRoot()).check { view, _ ->
    val hierarchy = TreePrinter(view).print()
    Log.d("ViewHierarchy", hierarchy)
}

// Or use Espresso's built-in
onView(withId(R.id.nonExistent))  // Will print hierarchy on failure
```

### Screenshot on Failure

```kotlin
@get:Rule
val screenshotRule = ScreenshotRule()

class ScreenshotRule : TestWatcher() {
    override fun failed(e: Throwable?, description: Description) {
        val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
        val filename = "${description.methodName}_failure.png"
        device.takeScreenshot(File(
            InstrumentationRegistry.getInstrumentation().targetContext.filesDir,
            filename
        ))
    }
}
```

---

## Resources

- [Espresso Documentation](https://developer.android.com/training/testing/espresso)
- [Espresso Cheat Sheet](https://developer.android.com/training/testing/espresso/cheat-sheet)
- [Test Automation University: Espresso](https://testautomationu.applitools.com/espresso-mobile-testing-tutorial/)
