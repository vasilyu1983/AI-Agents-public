# Android Studio Workflows

Use this reference when the user wants canonical build, test, install, and debugging workflows for Android projects.

## Table of Contents

- [What to verify first](#what-to-verify-first)
- [Gradle wrapper setup](#gradle-wrapper-setup)
- [Version catalogs](#version-catalogs)
- [Build variants and flavors](#build-variants-and-flavors)
- [Canonical loops](#canonical-loops)
- [CI mode](#ci-mode)
- [Signing config](#signing-config)

## What to verify first

- Gradle wrapper exists and is executable (`./gradlew --version`)
- Project syncs successfully in Android Studio (`File > Sync Project with Gradle Files`)
- Target device or emulator is available (`adb devices`)
- Correct build variant is selected (debug vs release, flavor)
- `local.properties` has valid `sdk.dir` pointing to Android SDK

## Gradle wrapper setup

Every Android project should use the Gradle wrapper:

```text
project-root/
  gradlew
  gradlew.bat
  gradle/
    wrapper/
      gradle-wrapper.jar
      gradle-wrapper.properties
```

- `gradle-wrapper.properties` pins the Gradle version. Update with `./gradlew wrapper --gradle-version=X.Y`.
- Always use `./gradlew` (not a globally installed `gradle`) so all developers and CI use the same version.
- If `gradlew` is not executable: `chmod +x gradlew`.

## Version catalogs

Prefer `gradle/libs.versions.toml` for dependency management. Illustrative snapshot as of 2026-07-11 — re-verify every version against its release notes before pinning, these move on independent cadences:

```toml
[versions]
kotlin = "2.4.0"           # verify: kotlinlang.org/docs/releases.html
agp = "9.2.0"               # verify: developer.android.com/build/releases/agp-9-2-0-release-notes
compose-bom = "2026.06.01"  # verify: developer.android.com/jetpack/androidx/releases/compose
hilt = "2.57.1"              # verify: developer.android.com/jetpack/androidx/releases/hilt

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
kotlin-android = { id = "org.jetbrains.kotlin.android", version.ref = "kotlin" }
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

### AGP 8.x -> 9.x migration trap

AGP crossed a major version boundary to 9.x in early 2026. AGP 9.x has a higher minimum/default Gradle requirement (9.x-series Gradle, not the 8.x-series most AGP-8 projects still pin) and Compose 1.12 requires `compileSdk 37` + AGP 9. If a project's build fails after bumping AGP with unrelated-looking Gradle task or DSL errors, check the Gradle wrapper version and the AGP release notes' DSL migration section before assuming the app code is at fault — this is a build-tooling version-skew problem, not a Kotlin or Compose regression. Verify current minimums at [developer.android.com/build/releases/gradle-plugin-roadmap](https://developer.android.com/build/releases/gradle-plugin-roadmap).

Reference in `build.gradle.kts`:

```kotlin
dependencies {
    implementation(platform(libs.compose.bom))
    implementation(libs.compose.ui)
    implementation(libs.hilt.android)
}
```

Benefits: single source of truth for versions, IDE auto-complete, centralized updates.

## Build variants and flavors

- **Build types**: `debug` (debuggable, no minification) and `release` (minified, signed).
- **Product flavors**: use for environment switching (`dev`, `staging`, `prod`) or feature gating (`free`, `pro`).
- **Build variant** = flavor + build type (e.g., `devDebug`, `prodRelease`).
- Verify active variant before building: `./gradlew tasks --group=build` lists available assemble tasks.

```kotlin
// build.gradle.kts
android {
    flavorDimensions += "environment"
    productFlavors {
        create("dev") { dimension = "environment"; applicationIdSuffix = ".dev" }
        create("prod") { dimension = "environment" }
    }
}
```

## Canonical loops

### Build + run on emulator

```bash
./gradlew :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
adb shell am start -n com.example.app/.MainActivity
```

### Build + run on device

Same commands — ADB targets the connected device. If multiple devices:

```bash
adb -s DEVICE_SERIAL install -r app/build/outputs/apk/debug/app-debug.apk
```

### Targeted tests

```bash
# All unit tests
./gradlew testDebugUnitTest

# Single test class
./gradlew testDebugUnitTest --tests "com.example.app.MyViewModelTest"

# Instrumented tests on connected device/emulator
./gradlew connectedDebugAndroidTest
```

### UI verification

```bash
# Screenshot
adb exec-out screencap -p > screenshot.png

# UI hierarchy (for layout inspection)
adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml

# Layout Inspector: use Android Studio's built-in Layout Inspector for Compose hierarchy
```

### Log-first debugging

```bash
# Stream logcat filtered by tag
adb logcat -s MyApp:V

# Dump recent errors
adb logcat -d *:E > errors.txt

# Clear logcat buffer before reproduction
adb logcat -c
```

### Debugger attach

Use Android Studio's debugger for breakpoint-driven inspection. From CLI, the app must be `debuggable` (debug build variant). Attach via `Run > Attach Debugger to Android Process` in the IDE.

## CI mode

```bash
# Headless emulator
emulator -avd CI_Emulator -no-window -no-audio -no-boot-anim &
adb wait-for-device shell getprop sys.boot_completed | grep -q 1

# Build + test
./gradlew assembleDebug testDebugUnitTest connectedDebugAndroidTest

# Collect test results
# Unit: app/build/reports/tests/testDebugUnitTest/
# Instrumented: app/build/reports/androidTests/connected/
```

## Signing config

- **Debug**: uses auto-generated `debug.keystore` at `~/.android/debug.keystore`. No configuration needed.
- **Release**: requires a keystore file. Store signing config in `build.gradle.kts` with environment variables or `local.properties` (never commit keystore passwords):

```kotlin
android {
    signingConfigs {
        create("release") {
            storeFile = file(System.getenv("KEYSTORE_PATH") ?: "release.keystore")
            storePassword = System.getenv("KEYSTORE_PASSWORD") ?: ""
            keyAlias = System.getenv("KEY_ALIAS") ?: ""
            keyPassword = System.getenv("KEY_PASSWORD") ?: ""
        }
    }
}
```

- **Play App Signing**: Prefer enrollment in Play App Signing. Google manages the app signing key; you upload with an upload key. Reduces key loss risk.
