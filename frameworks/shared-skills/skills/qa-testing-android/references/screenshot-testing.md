# Screenshot Testing for Android

Visual regression testing tools and patterns for Android UI validation.

**Official docs**: [Compose Preview Screenshot Testing](https://developer.android.com/studio/preview/compose-screenshot-testing)

## Contents

- [Tool Comparison](#tool-comparison)
- [Compose Preview Screenshot Testing](#compose-preview-screenshot-testing)
- [Paparazzi](#paparazzi)
- [Roborazzi](#roborazzi)
- [Shot by Karumi](#shot-by-karumi)
- [Comparison Strategies](#comparison-strategies)
- [Recording and Updating Baselines](#recording-and-updating-baselines)
- [CI Integration](#ci-integration)
- [Handling Dynamic Content](#handling-dynamic-content)
- [Theme and Display Testing](#theme-and-display-testing)
- [Flake Reduction](#flake-reduction)
- [Related Resources](#related-resources)

---

## Tool Comparison

| Tool                     | Runs On     | Compose | Views | Device Required | Speed       |
|--------------------------|-------------|---------|-------|-----------------|-------------|
| Compose Preview Screenshot | JVM (Gradle)| Yes   | No    | No              | Fast        |
| Paparazzi                | JVM         | Yes     | Yes   | No              | Fast        |
| Roborazzi                | JVM (Robolectric) | Yes | Yes | No             | Fast        |
| Shot (Karumi)            | Device/Emulator | Yes  | Yes   | Yes             | Slow        |
| Dropshots (Dropbox)      | Device/Emulator | Yes  | Yes   | Yes             | Slow        |

**Recommendation:** Start with Paparazzi or Roborazzi for JVM-based speed. Use device-based tools only when you need real rendering fidelity (shadows, hardware-accelerated drawing).

---

## Compose Preview Screenshot Testing

The official Jetpack tool generates screenshots from `@Preview` composables on the JVM.

### Setup

```kotlin
// build.gradle.kts (app module)
plugins {
    id("com.android.compose.screenshot") version "0.0.1-alpha07"
}

android {
    experimentalProperties["android.experimental.enableScreenshotTest"] = true
}

dependencies {
    screenshotTestImplementation(libs.androidx.compose.ui.tooling)
}
```

### Writing Preview Screenshot Tests

```kotlin
// src/screenshotTest/kotlin/LoginScreenshots.kt
package com.example.app

import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import com.example.app.ui.theme.AppTheme

@Preview(showBackground = true)
@Composable
fun LoginScreen_Default() {
    AppTheme {
        LoginScreen(
            state = LoginState(email = "", password = "", isLoading = false)
        )
    }
}

@Preview(showBackground = true)
@Composable
fun LoginScreen_Loading() {
    AppTheme {
        LoginScreen(
            state = LoginState(email = "user@test.com", password = "****", isLoading = true)
        )
    }
}

@Preview(showBackground = true)
@Composable
fun LoginScreen_Error() {
    AppTheme {
        LoginScreen(
            state = LoginState(
                email = "user@test.com",
                password = "",
                error = "Invalid credentials"
            )
        )
    }
}
```

### Commands

```bash
# Record golden images
./gradlew updateDebugScreenshotTest

# Verify against goldens
./gradlew validateDebugScreenshotTest
```

---

## Paparazzi

JVM-based screenshot testing from Cash App. No device or emulator needed.

### Setup

```kotlin
// build.gradle.kts (module)
plugins {
    id("app.cash.paparazzi") version "1.3.4"
}
```

### Compose Screenshot Test

```kotlin
import app.cash.paparazzi.DeviceConfig
import app.cash.paparazzi.Paparazzi
import org.junit.Rule
import org.junit.Test

class ProfileScreenTest {
    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_6,
        theme = "android:Theme.Material3.Light.NoActionBar",
    )

    @Test
    fun default_state() {
        paparazzi.snapshot {
            AppTheme {
                ProfileScreen(
                    user = User(name = "Jane Doe", email = "jane@example.com"),
                    isEditing = false,
                )
            }
        }
    }

    @Test
    fun editing_state() {
        paparazzi.snapshot {
            AppTheme {
                ProfileScreen(
                    user = User(name = "Jane Doe", email = "jane@example.com"),
                    isEditing = true,
                )
            }
        }
    }
}
```

### View-Based Screenshot Test

```kotlin
class LegacyViewTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun custom_card_view() {
        val view = paparazzi.inflate<CustomCardView>(R.layout.card_item)
        view.setTitle("Product Name")
        view.setPrice("$29.99")
        view.setRating(4.5f)
        paparazzi.snapshot(view)
    }
}
```

### Commands

```bash
# Record golden images
./gradlew :app:recordPaparazziDebug

# Verify against goldens
./gradlew :app:verifyPaparazziDebug
```

---

## Roborazzi

Robolectric-based screenshot testing. Captures full Activity/Fragment rendering.

### Setup

```kotlin
// build.gradle.kts
plugins {
    id("io.github.takahirom.roborazzi") version "1.26.0"
}

dependencies {
    testImplementation("io.github.takahirom.roborazzi:roborazzi:1.26.0")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose:1.26.0")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-junit-rule:1.26.0")
}

android {
    testOptions {
        unitTests {
            isIncludeAndroidResources = true
        }
    }
}
```

### Compose Test with Roborazzi

```kotlin
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.compose.ui.test.onRoot
import com.github.takahirom.roborazzi.captureRoboImage
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith
import org.robolectric.RobolectricTestRunner

@RunWith(RobolectricTestRunner::class)
class SettingsScreenTest {
    @get:Rule
    val composeRule = createComposeRule()

    @Test
    fun settings_default() {
        composeRule.setContent {
            AppTheme {
                SettingsScreen(darkMode = false, notifications = true)
            }
        }
        composeRule.onRoot().captureRoboImage()
    }

    @Test
    fun settings_dark_mode() {
        composeRule.setContent {
            AppTheme(darkTheme = true) {
                SettingsScreen(darkMode = true, notifications = true)
            }
        }
        composeRule.onRoot().captureRoboImage()
    }
}
```

### Commands

```bash
# Record
./gradlew recordRoborazziDebug

# Verify
./gradlew verifyRoborazziDebug

# Compare (generates diff images)
./gradlew compareRoborazziDebug
```

---

## Shot by Karumi

Device-based screenshot testing with pixel-perfect accuracy.

### Setup

```kotlin
// build.gradle.kts
plugins {
    id("com.karumi.shot") version "6.1.0"
}

dependencies {
    androidTestImplementation("com.karumi:shot-android:6.1.0")
}
```

### Writing Shot Tests

```kotlin
import com.karumi.shot.ScreenshotTest

class LoginActivityTest : ScreenshotTest {
    @Test
    fun login_screen_default() {
        val activity = launchActivity<LoginActivity>()
        compareScreenshot(activity)
    }

    @Test
    fun login_screen_with_error() {
        val activity = launchActivity<LoginActivity>()
        activity.runOnUiThread {
            activity.showError("Invalid credentials")
        }
        compareScreenshot(activity, name = "login_error")
    }
}
```

### Commands

```bash
# Record on connected device/emulator
./gradlew executeScreenshotTests -Precord

# Verify
./gradlew executeScreenshotTests
```

---

## Comparison Strategies

| Strategy          | Tolerance | Speed  | Use Case                           |
|-------------------|-----------|--------|------------------------------------|
| Exact pixel match | 0%        | Fast   | Deterministic rendering, JVM tools |
| Pixel diff + threshold | 0.1-1% | Fast | Account for anti-aliasing differences |
| Perceptual diff (SSIM) | Configurable | Medium | Human-like similarity detection |
| Region-based      | Per-region | Medium | Ignore dynamic areas               |

### Configuring Tolerance in Paparazzi

```kotlin
@get:Rule
val paparazzi = Paparazzi(
    deviceConfig = DeviceConfig.PIXEL_6,
    renderingMode = SessionParams.RenderingMode.SHRINK,
    // Paparazzi uses exact match by default
    // For tolerance, use a custom image comparator:
)

// Custom comparator example
class ThresholdComparator(private val maxDiffPercent: Double = 0.5) {
    fun compare(golden: BufferedImage, actual: BufferedImage): Boolean {
        val totalPixels = golden.width * golden.height
        var diffPixels = 0

        for (x in 0 until golden.width) {
            for (y in 0 until golden.height) {
                if (golden.getRGB(x, y) != actual.getRGB(x, y)) {
                    diffPixels++
                }
            }
        }

        val diffPercent = (diffPixels.toDouble() / totalPixels) * 100
        return diffPercent <= maxDiffPercent
    }
}
```

---

## Recording and Updating Baselines

### Workflow

```text
1. Developer makes UI change
2. Run verification: ./gradlew verifyPaparazziDebug
3. Test fails with diff images
4. Review diff images manually
5. If intentional: ./gradlew recordPaparazziDebug
6. Commit updated golden images
7. PR review includes visual diff review
```

### Golden Image Storage

| Strategy           | Pros                        | Cons                         |
|--------------------|-----------------------------|------------------------------|
| In-repo (Git)      | Simple, versioned with code | Increases repo size          |
| Git LFS            | Versioned, smaller repo     | Requires LFS setup           |
| Cloud storage (S3) | No repo bloat               | Separate versioning needed   |
| Artifact registry  | Integrates with CI          | More complex setup           |

**Recommendation:** Use Git LFS for teams with many screenshots. Keep in-repo for small projects (< 200 images).

---

## CI Integration

### GitHub Actions with Paparazzi

```yaml
name: Screenshot Tests
on: [pull_request]

jobs:
  screenshot-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true

      - uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - uses: gradle/actions/setup-gradle@v4

      - name: Verify screenshots
        run: ./gradlew verifyPaparazziDebug

      - name: Upload diff images on failure
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: screenshot-diffs
          path: '**/build/paparazzi/failures/'
```

### PR Comment with Diff Images

```yaml
      - name: Comment PR with diffs
        if: failure()
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const glob = require('glob');
            const diffs = glob.sync('**/failures/*.png');
            if (diffs.length > 0) {
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.pull_request.number,
                body: `## Screenshot diffs detected\n${diffs.length} screenshot(s) differ from baselines.\nCheck the uploaded artifacts for diff images.`
              });
            }
```

---

## Handling Dynamic Content

### Freeze Time

```kotlin
@Test
fun order_confirmation_screen() {
    val fixedClock = Clock.fixed(
        Instant.parse("2025-01-15T10:30:00Z"),
        ZoneId.of("UTC")
    )

    paparazzi.snapshot {
        AppTheme {
            OrderConfirmation(
                order = Order(id = "ORD-001", total = 99.99),
                clock = fixedClock,
            )
        }
    }
}
```

### Replace Animations

```kotlin
// Disable animations in composables under test
@Test
fun animated_component() {
    paparazzi.snapshot {
        CompositionLocalProvider(
            LocalInspectionMode provides true  // disables animations
        ) {
            AnimatedStatusBadge(status = Status.SUCCESS)
        }
    }
}
```

### Placeholder for Network Images

```kotlin
// Replace Coil/Glide image loading with static placeholder
@Test
fun user_avatar() {
    val testImageLoader = FakeImageLoader.Builder(paparazzi.context)
        .default(ColorDrawable(Color.GRAY))
        .build()

    paparazzi.snapshot {
        CompositionLocalProvider(
            LocalImageLoader provides testImageLoader
        ) {
            UserAvatar(url = "https://example.com/avatar.jpg")
        }
    }
}
```

---

## Theme and Display Testing

### Dark Mode Testing

```kotlin
class ThemeScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi(deviceConfig = DeviceConfig.PIXEL_6)

    @Test
    fun home_screen_light() {
        paparazzi.snapshot {
            AppTheme(darkTheme = false) {
                HomeScreen(state = HomeState.preview())
            }
        }
    }

    @Test
    fun home_screen_dark() {
        paparazzi.snapshot {
            AppTheme(darkTheme = true) {
                HomeScreen(state = HomeState.preview())
            }
        }
    }
}
```

### Multi-Density Testing

```kotlin
@Test
fun component_mdpi() {
    val paparazzi = Paparazzi(deviceConfig = DeviceConfig.NEXUS_5.copy(density = Density.MEDIUM))
    paparazzi.snapshot { MyComponent() }
}

@Test
fun component_xxhdpi() {
    val paparazzi = Paparazzi(deviceConfig = DeviceConfig.PIXEL_6) // xxhdpi by default
    paparazzi.snapshot { MyComponent() }
}
```

### Multi-Device Parameterized Test

```kotlin
@RunWith(TestParameterInjector::class)
class DeviceScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    enum class Device(val config: DeviceConfig) {
        PHONE(DeviceConfig.PIXEL_6),
        FOLDABLE(DeviceConfig.PIXEL_FOLD),
        TABLET(DeviceConfig.PIXEL_C),
    }

    @TestParameter
    lateinit var device: Device

    @Test
    fun dashboard_screen() {
        paparazzi.unsafeUpdateConfig(device.config)
        paparazzi.snapshot {
            AppTheme {
                DashboardScreen(state = DashboardState.preview())
            }
        }
    }
}
```

---

## Flake Reduction

| Flake Source          | Mitigation                                        |
|-----------------------|---------------------------------------------------|
| Font rendering diffs  | Use JVM tools (Paparazzi/Roborazzi) for consistency |
| Animation frames      | Disable animations or use `LocalInspectionMode`   |
| System UI (status bar)| Exclude system chrome from capture area            |
| Network images        | Use fake image loaders with static placeholders    |
| Date/time display     | Inject fixed clocks                                |
| Random content        | Use seeded random or fixed test data               |
| Floating point rounding | Set pixel diff threshold of 0.1-0.5%            |

**Checklist -- Flake Prevention:**

- [ ] All tests use deterministic data (no random, no real timestamps)
- [ ] Network image loading is stubbed
- [ ] Animations are disabled or frozen at target frame
- [ ] JVM-based tool used where device fidelity is not required
- [ ] Pixel diff threshold is configured for anti-aliasing tolerance
- [ ] CI uses consistent JDK version and OS for rendering

---

## Related Resources

- [compose-testing.md](compose-testing.md) -- Jetpack Compose testing patterns
- [espresso-patterns.md](espresso-patterns.md) -- Espresso UI testing
- [android-ci-optimization.md](android-ci-optimization.md) -- CI pipeline setup for screenshot tests
- [gradle-managed-devices.md](gradle-managed-devices.md) -- Managed device configuration
