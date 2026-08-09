# Stale-Build Triage

Treat these as stale-build signals until proven otherwise:

- the emulator shows UI that does not exist in current source
- Gradle says build succeeded but the app still behaves like yesterday's build
- screenshots from repeated runs do not reflect recent code edits
- sign-in appears to work but downstream screens behave like an older runtime
- the APK timestamp in `app/build/outputs/` predates recent source edits

Default response:

1. Stop the Gradle daemon: `./gradlew --stop`
2. Clean: `./gradlew clean`
3. Build: `./gradlew assembleDebug`
4. Confirm APK timestamp matches the current build
5. Uninstall the installed app: `adb uninstall <applicationId>`
6. Install the fresh APK: `adb install -r <path-to-apk>`
7. Launch: `adb shell am start -n <applicationId>/<Activity>`
8. Only then continue with feature debugging

If the fresh install fails, stop there and inspect APK health.

## Gradle Cache Invalidation

Gradle uses multiple layers of caching that can each hold stale artifacts:

- **Build cache** (`~/.gradle/caches/build-cache-1/`): task output cache shared across projects. Force bypass: `--no-build-cache`.
- **Configuration cache** (`.gradle/configuration-cache/`): serialized task graph. Invalidated by plugin upgrades or buildscript changes. Delete when configuration errors appear after plugin updates.
- **Local build output** (`build/`, `app/build/`): module-level compiled output. Cleared by `./gradlew clean`.
- **Daemon memory**: the long-running Gradle daemon holds class loaders and plugin state in memory. Stop it: `./gradlew --stop`.

Nuclear option when nothing else works:

```bash
./gradlew --stop
rm -rf ~/.gradle/caches/build-cache-1/ .gradle/ build/ app/build/
./gradlew assembleDebug
```

## Incremental Compilation Signals

Suspect incremental compilation artifacts when:

- a source file was moved between modules but the old module still has compiled output
- an annotation processor (KAPT/KSP) produces stale generated sources after a model change
- the Compose compiler plugin version does not match the Kotlin version (Compose compiler is now bundled with Kotlin 2.0+, but older setups use a separate version)
- KAPT stubs are stale after renaming or removing annotated classes

In all cases, a full clean build is the safe first move.

## Gradle Daemon Issues

The Gradle daemon runs persistently and can hold stale state:

- Check daemon status: `./gradlew --status`
- Stop all daemons: `./gradlew --stop`
- If `jvmargs` changed in `gradle.properties`, the old daemon ignores the change until restarted
- Memory pressure (`OutOfMemoryError` during compilation): increase `org.gradle.jvmargs` in `gradle.properties`

## Logcat for Runtime Diagnostics

Default logcat output is too noisy. Use filters:

```bash
# Filter by app PID (most precise)
adb logcat --pid=$(adb shell pidof -s <applicationId>)

# Filter by tag and priority
adb logcat -s MyTag:D ActivityManager:I

# Show only warnings and above from all sources
adb logcat *:W

# Clear existing buffer and start fresh
adb logcat -c && adb logcat --pid=$(adb shell pidof -s <applicationId>)
```

For crash investigation, search for `FATAL EXCEPTION` in logcat — the first occurrence contains the root cause stack trace. Subsequent "Caused by" lines may be wrappers.

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
