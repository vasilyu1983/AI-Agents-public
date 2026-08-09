# Screenshot Testing for Android

Visual regression testing tools and patterns for Android UI validation.

**Official overview**: [Screenshot testing](https://developer.android.com/training/testing/ui-tests/screenshot)  
**Compose-specific official docs**: [Compose Preview Screenshot Testing](https://developer.android.com/studio/preview/compose-screenshot-testing)

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

## Tool Comparison

| Tool | Runs On | Compose | Views | Device Required | Best Use |
|------|---------|---------|-------|-----------------|----------|
| Compose Preview Screenshot Testing | JVM via Gradle | Yes | No | No | `@Preview` coverage with official tooling |
| Paparazzi | JVM | Yes | Yes | No | Fast reviewable diffs in app modules |
| Roborazzi | JVM via Robolectric | Yes | Yes | No | Activity, Fragment, and integration-style rendering |
| Shot (Karumi) | Device or emulator | Yes | Yes | Yes | Real-renderer fidelity |
| Device screenshots via UI Automator or test rule | Device or emulator | Yes | Yes | Yes | Failure artifacts and targeted smoke assertions |

**Recommendation:** Start with host-side screenshot tests for PR gates. Use device-based snapshots only when the renderer, camera, maps, WebView, or GPU path matters.

## Compose Preview Screenshot Testing

The official Jetpack tool generates screenshots from `@Preview` composables in the `screenshotTest` source set.

### Current requirements

For the Gradle-task workflow, the current Android Developers page requires at least:

- AGP 8.5.0+ (AGP 9.x is the current stable series as of 2026)
- Compose Preview Screenshot Testing plugin `0.0.1-alpha15+` (latest alpha as of July 2026; still in alpha)
- Kotlin 2.2.10+ (raised from the earlier 1.9.20 floor — confirm the current minimum in the official release notes before pinning, since alpha tooling raises this without a major version bump)
- JDK 17+

For the full IDE integration, the page calls out AGP 9.0+, plugin `0.0.1-alpha15+`, and Android Studio Otter 3 Feature Drop support. IDE integration is still in canary as of June 2026 — verify the current studio release before relying on it in CI.

### Setup

```properties
# gradle.properties
android.experimental.enableScreenshotTest=true
```

```kotlin
// libs.versions.toml
[versions]
screenshot = "0.0.1-alpha15"  # latest alpha as of June 2026; check release notes before pinning

[plugins]
screenshot = { id = "com.android.compose.screenshot", version.ref = "screenshot" }

[libraries]
screenshot-validation-api = { group = "com.android.tools.screenshot", name = "screenshot-validation-api", version.ref = "screenshot" }
androidx-ui-tooling = { group = "androidx.compose.ui", name = "ui-tooling" }
```

```kotlin
// module build.gradle.kts
plugins {
    alias(libs.plugins.screenshot)
}

android {
    experimentalProperties["android.experimental.enableScreenshotTest"] = true

    testOptions {
        screenshotTests {
            imageDifferenceThreshold = 0.0001f
        }
    }
}

dependencies {
    screenshotTestImplementation(libs.screenshot.validation.api)
    screenshotTestImplementation(libs.androidx.ui.tooling)
}
```

### Writing preview screenshot tests

```kotlin
// src/screenshotTest/kotlin/com/example/app/LoginPreviewScreenshotTest.kt
package com.example.app

import androidx.compose.runtime.Composable
import androidx.compose.ui.tooling.preview.Preview
import com.android.tools.screenshot.PreviewTest
import com.example.app.ui.theme.AppTheme

@PreviewTest
@Preview(showBackground = true)
@Composable
fun LoginScreenDefaultPreview() {
    AppTheme {
        LoginScreen(
            state = LoginState(email = "", password = "", isLoading = false)
        )
    }
}
```

Keep previews small and purposeful. Use multi-previews, `uiMode`, `fontScale`, and locale variants where they represent product-level layouts you actually support.

### Commands

```bash
# Record or update reference images
./gradlew updateDebugScreenshotTest

# Validate current rendering against references
./gradlew validateDebugScreenshotTest
```

The official workflow produces HTML reports under `build/reports/screenshotTest/preview/...`.

## Paparazzi

Paparazzi is the fastest option for most host-side PR coverage across Compose and legacy View code.

### Setup

```kotlin
plugins {
    id("app.cash.paparazzi") version "<current-version>"
}
```

Use the current project-approved version instead of copying a stale hardcoded version from docs.

### Compose snapshot example

```kotlin
class ProfileScreenTest {
    @get:Rule
    val paparazzi = Paparazzi(
        deviceConfig = DeviceConfig.PIXEL_6,
        theme = "android:Theme.Material3.Light.NoActionBar"
    )

    @Test
    fun defaultState() {
        paparazzi.snapshot {
            AppTheme {
                ProfileScreen(
                    user = User(name = "Jane Doe", email = "jane@example.com"),
                    isEditing = false
                )
            }
        }
    }
}
```

## Roborazzi

Roborazzi is useful when you want screenshot assertions around full Activity or Fragment rendering with Robolectric support.

### Setup

```kotlin
plugins {
    id("io.github.takahirom.roborazzi") version "<current-version>"
}

dependencies {
    testImplementation("io.github.takahirom.roborazzi:roborazzi:<current-version>")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-compose:<current-version>")
    testImplementation("io.github.takahirom.roborazzi:roborazzi-junit-rule:<current-version>")
}
```

## Shot by Karumi

Use device-based screenshot tooling when host-side rendering is not good enough, for example WebView, Maps, platform widgets, or GPU-sensitive rendering.

## Comparison Strategies

- Compare focused components or states rather than whole app flows.
- Store goldens close to the source set and review diffs in pull requests.
- Use thresholds sparingly and document why a non-zero threshold exists.
- Split rendering-sensitive suites from logic-heavy UI flows so teams can reason about failures quickly.

## Recording And Updating Baselines

- Treat baseline updates as code changes that need review.
- Rename screenshot functions carefully: Compose Preview Screenshot Testing keys reference files by function name and preview parameters.
- Freeze clocks, locale, seeded data, font scale, and image inputs before regenerating baselines.

## CI Integration

### Compose Preview Screenshot Testing

```yaml
jobs:
  screenshot-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-java@v5
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: gradle/actions/setup-gradle@v5
      - run: ./gradlew validateDebugScreenshotTest
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: screenshot-report
          path: |
            **/build/reports/screenshotTest/
            **/build/reports/paparazzi/
            **/build/outputs/roborazzi/
```

## Handling Dynamic Content

- Freeze time and timezone.
- Replace remote images with local placeholders or fake loaders.
- Use deterministic fonts and locales.
- Avoid video, ads, network spinners, and other volatile content in baseline images.

## Theme And Display Testing

- Capture light and dark themes only if both are supported.
- Add large font or compact-width variants when they reveal real layout changes.
- Do not use ATD for fidelity-sensitive screenshot assertions because ATD disables hardware rendering.

## Flake Reduction

- Prefer host-side screenshot tooling for PR gates.
- Keep screenshot assertions focused and small.
- Separate visual regression failures from functional UI failures in CI reporting.
- Review HTML reports or diff artifacts, not just raw PNG outputs.

## Related Resources

- [Screenshot testing overview](https://developer.android.com/training/testing/ui-tests/screenshot)
- [Compose Preview Screenshot Testing](https://developer.android.com/studio/preview/compose-screenshot-testing)
- [Gradle Managed Devices](gradle-managed-devices.md)
- [Compose Testing](compose-testing.md)
