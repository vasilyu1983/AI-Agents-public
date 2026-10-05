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

Prefer `gradle/libs.versions.toml` for dependency management. Illustrative shape only — look up each current version in its release notes before pinning; they move on independent cadences:

```toml
[versions]
kotlin = "<current>"        # look up: kotlinlang.org/docs/releases.html
agp = "<current 9.x>"       # look up: developer.android.com/build/releases/gradle-plugin (check its minimum Gradle)
compose-bom = "<current>"   # look up: developer.android.com/develop/ui/compose/bom/bom-mapping
hilt = "<current>"          # look up: developer.android.com/jetpack/androidx/releases/hilt

[libraries]
compose-bom = { group = "androidx.compose", name = "compose-bom", version.ref = "compose-bom" }
compose-ui = { group = "androidx.compose.ui", name = "ui" }
hilt-android = { group = "com.google.dagger", name = "hilt-android", version.ref = "hilt" }

[plugins]
android-application = { id = "com.android.application", version.ref = "agp" }
# AGP 9+ turns on built-in Kotlin support by default — do NOT also apply org.jetbrains.kotlin.android;
# doing so fails with "plugin is no longer required for Kotlin support since AGP 9.0". Move kapt users to KSP
# or the com.android.legacy-kapt plugin instead. See the AGP 8.x -> 9.x migration trap below.
hilt = { id = "com.google.dagger.hilt.android", version.ref = "hilt" }
compose-compiler = { id = "org.jetbrains.kotlin.plugin.compose", version.ref = "kotlin" }
```

### AGP 8.x -> 9.x migration trap

AGP 9 turned on **built-in Kotlin support by default**. Applying `org.jetbrains.kotlin.android` alongside AGP 9 now fails with "plugin is no longer required for Kotlin support since AGP 9.0" — drop that catalog entry, and move `kapt` users to KSP or the `com.android.legacy-kapt` plugin. A temporary `android.builtInKotlin=false` opt-out exists; plan to remove it before the next AGP major. AGP 9.x also needs a 9.x-series Gradle, not the 8.x-series most AGP-8 projects still pin (look up the exact minimum in the AGP release notes), and newer Compose releases can raise the required `compileSdk`/AGP — check the Compose release notes before bumping the BOM. If a project's build fails after bumping AGP with unrelated-looking Gradle task or DSL errors, check the Gradle wrapper version and the AGP release notes' DSL migration section before assuming the app code is at fault — this is a build-tooling version-skew problem, not a Kotlin or Compose regression. Verify current minimums at [developer.android.com/build/releases/gradle-plugin-roadmap](https://developer.android.com/build/releases/gradle-plugin-roadmap).

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
