# Stale-Build Triage

Treat these as stale-build signals until proven otherwise:

- the emulator shows UI that does not exist in current source
- Gradle says build succeeded but the app still behaves like yesterday's build
- screenshots from repeated runs do not reflect recent code edits
- sign-in appears to work but downstream screens behave like an older runtime
- the APK timestamp in `app/build/outputs/` predates recent source edits

Escalation ladder — try the cheapest step first, and preserve repro state (account, deep link, local data, installed version/signing identity) before any step that clears data:

1. Build: `./gradlew assembleDebug`. Confirm `BUILD SUCCESSFUL` and that the APK timestamp matches the current build.
2. Replace-install without clearing data: `adb install -r <path-to-apk>`, then launch (`adb shell am start -n <applicationId>/<Activity>`) and verify.
3. If still stale, stop the Gradle daemon and clean-build: `./gradlew --stop && ./gradlew clean assembleDebug`, then replace-install again.
4. Only if the symptom persists after a clean build — uninstall the installed app (`adb uninstall <applicationId>`) as the last rung, then install the fresh APK and launch.
5. Only then continue with feature debugging.

Record which rung made the symptom disappear — that is diagnostic evidence for the root cause, not just housekeeping. If the fresh install fails, stop there and inspect APK health.

## Gradle Cache Invalidation

Gradle uses multiple layers of caching that can each hold stale artifacts:

- **Build cache** (`~/.gradle/caches/build-cache-1/`): task output cache shared across projects. Force bypass: `--no-build-cache`.
- **Configuration cache** (`.gradle/configuration-cache/`): serialized task graph. Invalidated by plugin upgrades or buildscript changes. Delete when configuration errors appear after plugin updates.
- **Local build output** (`build/`, `app/build/`): module-level compiled output. Cleared by `./gradlew clean`.
- **Daemon memory**: the long-running Gradle daemon holds class loaders and plugin state in memory. Stop it: `./gradlew --stop`.

Bypass the relevant cache first (`--no-build-cache` or `--no-configuration-cache`) and retain the failing logs. If a cache must be removed, identify only the affected project's/generated entry; a global cache wipe destroys useful comparisons and forces unrelated projects to rebuild.

## Incremental Compilation Signals

Suspect incremental compilation artifacts when:

- a source file was moved between modules but the old module still has compiled output
- an annotation processor (KAPT/KSP) produces stale generated sources after a model change
- the Compose compiler plugin version does not match the Kotlin version (Compose compiler is now bundled with Kotlin 2.0+, but older setups use a separate version)
- KAPT stubs are stale after renaming or removing annotated classes

After checking artifact identity and attempting replace-install, use a clean build as the next diagnostic rung.

## Gradle Daemon Issues

The Gradle daemon runs persistently and can hold stale state:

- Check daemon status: `./gradlew --status`
- Stop all daemons: `./gradlew --stop`
- Different JVM arguments normally select a compatible daemon or start a new one; inspect `./gradlew --status` and the actual JVM before attributing stale behavior to daemon reuse. [Gradle daemon compatibility](https://docs.gradle.org/current/userguide/gradle_daemon.html)
- Memory pressure (`OutOfMemoryError` during compilation): increase `org.gradle.jvmargs` in `gradle.properties`

## Logcat for Runtime Diagnostics

Default logcat output is too noisy. Use filters:

```bash
# Filter by app PID (most precise)
adb logcat --pid=$(adb shell pidof -s <applicationId>)

# Filter by tag and priority
adb logcat -s MyTag:D ActivityManager:I

# Show only warnings and above from all sources
adb logcat '*:W'

# Preserve existing logs before clearing the buffer; start a new capture after export
```

For Java crashes, capture the whole `FATAL EXCEPTION` chain including every `Caused by`; the deepest cause can identify the failure. Native signals require tombstone triage in [performance-triage.md](performance-triage.md#native-crash-triage).

## Partial Build Failure + Stale APK Trap

When a build has errors, `./gradlew assembleDebug` fails but leaves a valid APK from a previous successful build in `app/build/outputs/`. Running `adb install` after a failed build silently installs this stale artifact.

**Detection heuristic:** If behavior does not match latest code, check whether the build actually succeeded:

```bash
# Check the exit code — do not just look for your errors
./gradlew assembleDebug; echo "EXIT: $?"
```

**Prevention:** Only install after confirming build success:

```bash
./gradlew assembleDebug && adb install -r app/build/outputs/apk/debug/app-debug.apk
# The && ensures install only runs on success
```

**Common scenario:** Pre-existing errors in files from concurrent work cause build failure, but the APK from the last successful session sits in the output directory. `adb install` picks it up silently.
