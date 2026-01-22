---
name: qa-testing-android
description: "Android testing with Espresso, UIAutomator, and Compose Testing: layered strategy, flake control, device matrix, CI integration, and ADB automation."
---

# QA Testing (Android, Jan 2026) — Quick Reference

This skill enables Android testing automation via Espresso, UIAutomator, and Compose Testing, with focus on reliable UI tests and layered coverage.

**Note**: Requires Android SDK with build-tools and emulator installed.

Core references: [Android Testing Docs](https://developer.android.com/training/testing), [Espresso](https://developer.android.com/training/testing/espresso), [UIAutomator](https://developer.android.com/training/testing/other-components/ui-automator), [Compose Testing](https://developer.android.com/develop/ui/compose/testing).

---

## Core QA (Default)

### Testing Layers (Use the Smallest Effective Layer)

- Unit tests: business logic, ViewModels, data transformations (fast, JVM-based).
- Integration tests: Room databases, repositories, networking with MockWebServer.
- UI tests (Espresso/Compose): in-app UI interactions, single activity.
- System tests (UIAutomator): cross-app flows, permissions, notifications.

### Framework Selection

| Framework | Use For | Scope |
|-----------|---------|-------|
| JUnit + Mockito | Unit tests | JVM, no Android |
| Robolectric | Unit tests with Android APIs | JVM, simulated |
| Espresso | UI tests (View-based) | Instrumented |
| Compose Testing | UI tests (Compose) | Instrumented |
| UIAutomator | System/cross-app tests | Instrumented |
| Appium | Cross-platform | External |

### Device Matrix

- Default: emulators for PR gates; real devices for nightly/release.
- Keep matrix small and risk-based:
  - One small phone (API 26-28), one flagship (API 34+), one tablet if supported.
  - Cover min/target SDK versions.

### UI Test Flake Control (Determinism)

- Disable animations via ADB or test rule.
- Use IdlingResources for async operations.
- Mock network with MockWebServer or Hilt test modules.
- Reset app state between tests (clear SharedPreferences, databases).
- Avoid test ordering dependencies.

### CI Economics

- PR gate: unit tests + smoke UI suite; full UI on schedule.
- Collect artifacts on failure: screenshots, logcat, video.
- Use Android Test Orchestrator for isolation.

### Do / Avoid

Do:

- Use IdlingResources for async waits.
- Use Robot Pattern or Page Objects.
- Test on multiple API levels.

Avoid:

- `Thread.sleep()` for synchronization.
- Tests depending on network or specific time.
- Flaky selectors (text that changes with locale).

---

## Quick Reference

| Task | Command | When to Use |
|------|---------|-------------|
| List emulators | `emulator -list-avds` | Check available AVDs |
| Start emulator | `emulator @Pixel_6_API_34` | Launch emulator |
| List devices | `adb devices` | Check connected devices |
| Install APK | `adb install app.apk` | Deploy to device |
| Run tests | `./gradlew connectedAndroidTest` | Execute instrumented tests |
| Run unit tests | `./gradlew test` | Execute JVM tests |
| Take screenshot | `adb exec-out screencap -p > screen.png` | Capture screen |
| Record video | `adb shell screenrecord /sdcard/demo.mp4` | Record session |
| Clear app data | `adb shell pm clear com.example.app` | Reset app state |

---

## When to Use This Skill

Claude should invoke this skill when a user requests:

- Build and run Android app in emulator
- Test Android app functionality
- Write Espresso or UIAutomator tests
- Test Jetpack Compose UI
- Debug Android app behavior
- Set up Android CI/CD pipeline

---

## Espresso Testing

### Basic Espresso Test

```kotlin
// app/src/androidTest/java/com/example/LoginTest.kt
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.rules.ActivityScenarioRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LoginTest {

    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun loginWithValidCredentials_showsDashboard() {
        // Enter email
        onView(withId(R.id.emailField))
            .perform(typeText("user@example.com"), closeSoftKeyboard())

        // Enter password
        onView(withId(R.id.passwordField))
            .perform(typeText("password123"), closeSoftKeyboard())

        // Click login
        onView(withId(R.id.loginButton))
            .perform(click())

        // Verify dashboard is shown
        onView(withId(R.id.dashboardTitle))
            .check(matches(isDisplayed()))
    }

    @Test
    fun loginWithEmptyEmail_showsError() {
        onView(withId(R.id.loginButton))
            .perform(click())

        onView(withId(R.id.emailError))
            .check(matches(withText("Email is required")))
    }
}
```

### IdlingResource for Async Operations

```kotlin
class NetworkIdlingResource : IdlingResource {
    private var callback: IdlingResource.ResourceCallback? = null
    @Volatile private var isIdle = true

    override fun getName() = "NetworkIdlingResource"

    override fun isIdleNow(): Boolean = isIdle

    override fun registerIdleTransitionCallback(callback: ResourceCallback) {
        this.callback = callback
    }

    fun setIdle(idle: Boolean) {
        isIdle = idle
        if (idle) callback?.onTransitionToIdle()
    }
}

// In test setup
@Before
fun setUp() {
    IdlingRegistry.getInstance().register(networkIdlingResource)
}

@After
fun tearDown() {
    IdlingRegistry.getInstance().unregister(networkIdlingResource)
}
```

### Robot Pattern

```kotlin
// LoginRobot.kt
class LoginRobot {
    fun enterEmail(email: String) = apply {
        onView(withId(R.id.emailField))
            .perform(typeText(email), closeSoftKeyboard())
    }

    fun enterPassword(password: String) = apply {
        onView(withId(R.id.passwordField))
            .perform(typeText(password), closeSoftKeyboard())
    }

    fun clickLogin() = apply {
        onView(withId(R.id.loginButton)).perform(click())
    }

    fun verifyDashboardDisplayed() {
        onView(withId(R.id.dashboardTitle))
            .check(matches(isDisplayed()))
    }

    fun verifyError(message: String) {
        onView(withText(message))
            .check(matches(isDisplayed()))
    }
}

// Usage in test
@Test
fun loginFlow() {
    LoginRobot()
        .enterEmail("user@example.com")
        .enterPassword("password123")
        .clickLogin()
        .verifyDashboardDisplayed()
}
```

---

## Compose Testing

### Basic Compose Test

```kotlin
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test

class LoginScreenTest {

    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun loginButton_isDisplayed() {
        composeTestRule.setContent {
            LoginScreen(onLogin = {})
        }

        composeTestRule.onNodeWithText("Login")
            .assertIsDisplayed()
    }

    @Test
    fun enterCredentials_enablesLoginButton() {
        composeTestRule.setContent {
            LoginScreen(onLogin = {})
        }

        // Enter email
        composeTestRule.onNodeWithTag("emailField")
            .performTextInput("user@example.com")

        // Enter password
        composeTestRule.onNodeWithTag("passwordField")
            .performTextInput("password123")

        // Verify login button is enabled
        composeTestRule.onNodeWithTag("loginButton")
            .assertIsEnabled()
    }

    @Test
    fun clickLogin_callsCallback() {
        var loginClicked = false

        composeTestRule.setContent {
            LoginScreen(onLogin = { loginClicked = true })
        }

        composeTestRule.onNodeWithTag("emailField")
            .performTextInput("user@example.com")
        composeTestRule.onNodeWithTag("passwordField")
            .performTextInput("password123")
        composeTestRule.onNodeWithTag("loginButton")
            .performClick()

        assert(loginClicked)
    }
}
```

### Setting TestTags in Composables

```kotlin
@Composable
fun LoginScreen(onLogin: () -> Unit) {
    Column {
        TextField(
            value = email,
            onValueChange = { email = it },
            modifier = Modifier.testTag("emailField")
        )
        TextField(
            value = password,
            onValueChange = { password = it },
            modifier = Modifier.testTag("passwordField")
        )
        Button(
            onClick = onLogin,
            modifier = Modifier.testTag("loginButton")
        ) {
            Text("Login")
        }
    }
}
```

### Waiting for Async Updates

```kotlin
@Test
fun loadData_showsList() {
    composeTestRule.setContent {
        DataListScreen(viewModel = testViewModel)
    }

    // Wait for idle state
    composeTestRule.waitForIdle()

    // Or wait for specific condition
    composeTestRule.waitUntil(timeoutMillis = 5000) {
        composeTestRule.onAllNodesWithTag("listItem")
            .fetchSemanticsNodes().isNotEmpty()
    }

    composeTestRule.onNodeWithTag("listItem")
        .assertIsDisplayed()
}
```

---

## UIAutomator

### Cross-App and System Tests

```kotlin
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.UiSelector
import androidx.test.uiautomator.By
import androidx.test.uiautomator.Until
import androidx.test.platform.app.InstrumentationRegistry
import org.junit.Before
import org.junit.Test

class SystemTest {
    private lateinit var device: UiDevice

    @Before
    fun setUp() {
        device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
    }

    @Test
    fun grantPermission_allowsAccess() {
        // Start app
        device.pressHome()
        val launcher = device.launcherPackageName
        device.wait(Until.hasObject(By.pkg(launcher)), 5000)

        // Launch app
        val context = InstrumentationRegistry.getInstrumentation().context
        val intent = context.packageManager.getLaunchIntentForPackage("com.example.app")
        context.startActivity(intent)
        device.wait(Until.hasObject(By.pkg("com.example.app")), 5000)

        // Handle permission dialog
        val allowButton = device.findObject(
            UiSelector().text("Allow")
        )
        if (allowButton.exists()) {
            allowButton.click()
        }

        // Continue with test
        device.findObject(By.res("com.example.app:id/mainContent"))
            .click()
    }

    @Test
    fun openNotification_navigatesToApp() {
        // Open notification shade
        device.openNotification()
        device.wait(Until.hasObject(By.text("New Message")), 5000)

        // Click notification
        device.findObject(By.text("New Message")).click()

        // Verify app opened to correct screen
        device.wait(Until.hasObject(By.res("com.example.app:id/messageDetail")), 5000)
    }
}
```

---

## ADB Commands

### Emulator Management

```bash
# List available AVDs
emulator -list-avds

# Start emulator (headless for CI)
emulator @Pixel_6_API_34 -no-window -no-audio -no-boot-anim

# Start with specific options
emulator @Pixel_6_API_34 -gpu swiftshader_indirect -no-snapshot

# Wait for device to be ready
adb wait-for-device
adb shell getprop sys.boot_completed | grep -q 1
```

### App Management

```bash
# Install APK
adb install -r app-debug.apk

# Install test APK
adb install -r app-debug-androidTest.apk

# Uninstall
adb uninstall com.example.app

# Clear app data
adb shell pm clear com.example.app

# Force stop
adb shell am force-stop com.example.app

# Launch activity
adb shell am start -n com.example.app/.MainActivity
```

### Disable Animations (Required for UI Tests)

```bash
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
```

### Screenshots and Recording

```bash
# Screenshot
adb exec-out screencap -p > screenshot.png

# Screen recording (max 180 seconds)
adb shell screenrecord /sdcard/demo.mp4
# Ctrl+C to stop, then pull:
adb pull /sdcard/demo.mp4

# Logcat
adb logcat -d > logcat.txt
adb logcat *:E  # Errors only
```

---

## CI/CD Integration

### GitHub Actions

```yaml
# .github/workflows/android.yml
name: Android CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Setup Gradle
        uses: gradle/actions/setup-gradle@v3

      - name: Run unit tests
        run: ./gradlew test

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Run instrumented tests
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          arch: x86_64
          script: ./gradlew connectedAndroidTest

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: |
            **/build/reports/
            **/build/outputs/androidTest-results/
```

### Gradle Test Configuration

```kotlin
// app/build.gradle.kts
android {
    testOptions {
        unitTests {
            isIncludeAndroidResources = true
            isReturnDefaultValues = true
        }
        animationsDisabled = true
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
    }
}

dependencies {
    // Unit testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("org.mockito.kotlin:mockito-kotlin:5.2.1")
    testImplementation("org.robolectric:robolectric:4.11.1")

    // Instrumented testing
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.test.espresso:espresso-intents:3.5.1")
    androidTestImplementation("androidx.test.uiautomator:uiautomator:2.2.0")

    // Compose testing
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.6.0")
    debugImplementation("androidx.compose.ui:ui-test-manifest:1.6.0")

    // Test orchestrator
    androidTestUtil("androidx.test:orchestrator:1.4.2")
}
```

---

## Navigation

**Resources**

- [references/espresso-patterns.md](references/espresso-patterns.md) — Espresso matchers, actions, and advanced patterns
- [references/compose-testing.md](references/compose-testing.md) — Jetpack Compose testing guide
- [references/gradle-managed-devices.md](references/gradle-managed-devices.md) — Gradle Managed Devices for CI/CD
- [data/sources.json](data/sources.json) — Android documentation links

**Templates**

- [assets/template-android-test-checklist.md](assets/template-android-test-checklist.md) — Android UI test stability checklist

**Related Skills**

- [../software-mobile/SKILL.md](../software-mobile/SKILL.md) — Android/Kotlin development
- [../qa-testing-strategy/SKILL.md](../qa-testing-strategy/SKILL.md) — General testing strategies
- [../qa-testing-mobile/SKILL.md](../qa-testing-mobile/SKILL.md) — Cross-platform mobile testing strategy
- [../ops-devops-platform/SKILL.md](../ops-devops-platform/SKILL.md) — CI/CD pipelines
