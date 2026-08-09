# Runtime Proof Loop

Use this exact order when runtime truth is unclear:

1. Discover the entrypoint:
   `build.gradle.kts` (root and app module), `applicationId`, build variant, target device or emulator.
2. Check environment:
   `ANDROID_HOME`, JDK version, Gradle wrapper, ADB connectivity, emulator booted or device connected.
3. Clean and build:
   `./gradlew clean assembleDebug`. Confirm `BUILD SUCCESSFUL`.
4. Inspect the built APK:
   `aapt2 dump badging <apk>` — verify applicationId, versionCode, minSdk, activities.
5. Uninstall any stale installed copy:
   `adb uninstall <applicationId>`.
6. Install the fresh build:
   `adb install -r <path-to-apk>`.
7. Launch the fresh install:
   `adb shell am start -n <applicationId>/<Activity>`.
8. Capture one proof artifact:
   screenshot (`adb exec-out screencap -p > proof.png`), logcat output, or UI hierarchy dump.
9. Only then interpret UI, auth, API, or visual issues.

Do not skip the uninstall step when the symptom is "the app still shows the old screen."

Do not skip the clean step when incremental compilation is suspected — source moved between modules, annotation processor stale, or Compose compiler version changed.
