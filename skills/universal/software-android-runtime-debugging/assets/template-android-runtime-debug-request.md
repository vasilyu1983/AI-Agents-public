# Android Runtime Debug Request

- Goal:
  prove whether the current Android build really installs and launches on the intended emulator or device
- Project facts:
  build.gradle.kts path (root and app module), applicationId, build variant (debug/release), target device or emulator, Gradle version, AGP version
- Current symptom:
  stale UI, install failure, ADB error, crash on launch, Gradle build failure, R8 stripping, Compose recomposition issue
- Proof required:
  build success, APK path and timestamp, fresh uninstall/install/launch result, screenshot or logcat output
- Constraints:
  emulator or physical device, ProGuard/R8 enabled or disabled, multi-module project, specific Gradle/AGP version
