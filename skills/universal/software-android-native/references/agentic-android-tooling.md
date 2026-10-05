# Agentic Android Tooling

Choose the narrowest tool surface that can prove the next step.

## Default tool selection

| Situation | Default |
|-----------|---------|
| Working inside Android Studio | Android Studio's built-in Gemini coding assistant |
| Working from Codex CLI or Claude Code outside Android Studio | Gradle CLI + ADB |
| Emulator or device management | `avdmanager` + `emulator` CLI + `adb` |

## Android Studio Gemini

Use Android Studio directly when the developer already lives inside the IDE and wants the shortest edit-build-run loop.

Verified Android Studio Gemini capabilities:

- code generation and completion in Kotlin and Java
- inline code explanation and refactoring suggestions
- build error diagnosis and fix suggestions
- documentation lookup from developer.android.com

Maximum-value use:

- keep Android Studio as the inner loop for edit, build, run, and UI inspection
- keep Codex or Claude Code as the outer loop for scoped implementation, planning, and verification
- do not bounce between multiple tool surfaces for the same small change unless one of them is blocked

## Gradle CLI + ADB

Use Gradle CLI and ADB as the default external agent bridge when you need:

- build, install, and launch loops from terminal
- targeted test execution
- screenshot and UI hierarchy capture
- logcat inspection
- device and emulator management

### Command catalog

| Task | Command |
|------|---------|
| Build debug APK | `./gradlew assembleDebug` |
| Build specific module | `./gradlew :app:assembleDebug` |
| Run unit tests | `./gradlew testDebugUnitTest` |
| Run instrumented tests | `./gradlew connectedDebugAndroidTest` |
| Install APK | `adb install -r app/build/outputs/apk/debug/app-debug.apk` |
| Launch app | `adb shell am start -n com.example.app/.MainActivity` |
| Force stop app | `adb shell am force-stop com.example.app` |
| Uninstall app | `adb uninstall com.example.app` |
| Screenshot | `adb exec-out screencap -p > screenshot.png` |
| UI hierarchy dump | `adb shell uiautomator dump /sdcard/ui.xml && adb pull /sdcard/ui.xml` |
| Logcat (filtered) | `adb logcat -s TAG:V` |
| Logcat (errors only) | `adb logcat *:E` |
| Clear app data | `adb shell pm clear com.example.app` |
| List connected devices | `adb devices` |

Maximum-value use:

- put default module, build variant, package name, and emulator in `AGENTS.md`
- check build success first, then install, then launch
- use screenshot or UI hierarchy before guessing at layout issues
- use logcat before debugger attach
- keep commands version-controlled in `AGENTS.md`

## Emulator management

| Task | Command |
|------|---------|
| List available AVDs | `emulator -list-avds` |
| Create AVD | `avdmanager create avd -n Pixel_8_API_35 -k "system-images;android-35;google_apis;x86_64"` |
| Start emulator | `emulator -avd Pixel_8_API_35` |
| Start headless (CI) | `emulator -avd Pixel_8_API_35 -no-window -no-audio -no-boot-anim` |
| Wait for boot | `adb wait-for-device shell getprop sys.boot_completed` |
| Wipe data | `emulator -avd Pixel_8_API_35 -wipe-data` |

### Optional: scrcpy for screen mirroring

`scrcpy` mirrors a device or emulator screen to the host machine with low latency. Useful for real-time visual inspection when screenshots are not enough. Install via `brew install scrcpy` (macOS) or `apt install scrcpy` (Linux). Not required — use only when live mirroring adds value.

## Avoid

- Using debugger or UI automation before a simpler build, install, or logcat-based proof exists.
- Treating emulator availability as guaranteed without checking `adb devices`.
- Running instrumented tests on emulator before verifying that the emulator is booted and the app installs cleanly.
