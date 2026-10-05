# Runtime Proof Loop

Use this exact order when runtime truth is unclear. This mirrors [SKILL.md](../SKILL.md)'s escalation ladder — preserve state first, replace-install by default, and escalate to clean/clear/uninstall one step at a time rather than jumping straight to a full wipe.

1. Discover the entrypoint:
   `build.gradle.kts` (root and app module), `applicationId`, build variant, target device or emulator.
2. Check environment:
   `ANDROID_HOME`, JDK version, Gradle wrapper, ADB connectivity, emulator booted or device connected.
3. Build:
   `./gradlew assembleDebug`. Confirm `BUILD SUCCESSFUL`.
4. Inspect the built APK:
   `aapt2 dump badging <apk>` — verify applicationId, versionCode, minSdk, activities.
5. Preserve reproduction state before any reset:
   record account, deep link/intent, local data dependency, and the installed package/version/signing identity; export logs and screenshots first.
6. Replace-install the fresh build without clearing data:
   `adb install -r <path-to-apk>`. Escalate to `adb shell pm clear <applicationId>` or `adb uninstall <applicationId>` only when replace-install fails, signatures differ, or state migration is the suspected cause — and only after step 5.
7. Launch the fresh install:
   `adb shell am start -n <applicationId>/<Activity>`.
8. Capture one proof artifact:
   screenshot (`adb exec-out screencap -p > proof.png`), logcat output, or UI hierarchy dump.
9. Only then interpret UI, auth, API, or visual issues.

Escalate to a clean build (`./gradlew clean assembleDebug`) as a separate diagnostic step when incremental compilation is suspected — source moved between modules, annotation processor stale, or Compose compiler version changed — not as a default first move.
