# Gradle Build Troubleshooting

## Dependency Resolution Failures

When Gradle reports "Could not resolve" or "Could not find":

1. Check the `repositories` block in `settings.gradle.kts` (or root `build.gradle.kts`). Common missing repos: `google()`, `mavenCentral()`, `maven("https://jitpack.io")`.
2. Run `./gradlew dependencies --configuration releaseRuntimeClasspath` to see the resolved tree.
3. Use `./gradlew dependencyInsight --dependency <artifact> --configuration releaseRuntimeClasspath` to trace why a specific version was selected or why resolution failed.
4. If using a BOM (e.g., `platform("androidx.compose:compose-bom:...")`), confirm the BOM version includes the library version you expect.

## Version Catalogs (libs.versions.toml)

The `gradle/libs.versions.toml` file is the canonical source for dependency versions in modern Android projects.

Common issues:

- **Missing alias**: a `build.gradle.kts` references `libs.something` but no matching entry exists in the TOML — Gradle sync fails with an unclear error.
- **Stale version**: the TOML pins an old version while a transitive dependency pulls a newer incompatible one.
- **Typo in group or artifact**: TOML syntax is `module = "group:artifact"` — a wrong group silently resolves to nothing.
- **Bundle vs library**: bundles group multiple libraries under one alias. Adding a library to a bundle without declaring it first causes sync failure.

After editing `libs.versions.toml`, run `./gradlew --refresh-dependencies` to force re-resolution.

## KSP vs KAPT

KSP (Kotlin Symbol Processing) is the preferred annotation processor for Kotlin projects. KAPT (Kotlin Annotation Processing Tool) is the legacy bridge to Java annotation processors.

- **KSP version must match Kotlin version**: KSP releases are tagged as `<kotlin-version>-<ksp-version>` (e.g., `2.0.21-1.0.28`). A Kotlin upgrade without a matching KSP upgrade breaks the build.
- **Migration path**: replace `kapt("...")` with `ksp("...")` in `build.gradle.kts`. Room, Hilt, and Moshi all support KSP. Dagger/Hilt requires `dagger-compiler` for KSP.
- **KAPT stubs**: KAPT generates Java stubs from Kotlin before processing. Stale stubs after renaming cause phantom errors — clean build resolves them.
- **Cannot use both for the same processor**: if a library offers both KAPT and KSP, pick one. Using both causes duplicate processing.

## AGP Compatibility

Android Gradle Plugin (AGP) requires specific Gradle and JDK versions. After any upgrade, verify the compatibility chain:

| AGP | Minimum Gradle | Minimum JDK |
|-----|---------------|-------------|
| 9.0 | 9.1           | 17          |
| 8.7 | 8.9           | 17          |
| 8.5 | 8.7           | 17          |
| 8.3 | 8.4           | 17          |
| 8.1 | 8.0           | 17          |
| 7.4 | 7.5           | 11          |

AGP 9.x (current stable series as of 2026-07-11) also enables built-in Kotlin support by default — remove the explicit `org.jetbrains.kotlin.android` plugin application where AGP 9 already handles it, and expect the "unrelated-looking Gradle task/DSL error after an AGP bump" symptom to often be a Gradle-wrapper-version mismatch, not an app-code regression. Verify current minimums (this table is a snapshot) at [developer.android.com/build/releases/gradle-plugin-roadmap](https://developer.android.com/build/releases/gradle-plugin-roadmap).

After an AGP upgrade:

1. Update `gradle/wrapper/gradle-wrapper.properties` to the required Gradle version.
2. Confirm JDK version: `./gradlew --version` shows the JVM.
3. Run `./gradlew assembleDebug` — watch for deprecated API warnings that become errors in the new version.
4. Check `gradle.properties` for removed or renamed flags.

## Configuration Cache

Gradle's configuration cache serializes the task graph to skip re-configuration on subsequent builds. It breaks when:

- A plugin reads a file at configuration time that has changed.
- A `buildscript` dependency was upgraded but the serialized graph holds the old classpath.
- A `settings.gradle.kts` change is not detected by the cache key.

**Symptom**: build fails with a serialization or "configuration cache state could not be reused" error.

**Fix**: delete `.gradle/configuration-cache/` and rebuild.

## Build Scan Analysis

Gradle build scans provide detailed timing, dependency resolution, and failure diagnostics:

```bash
./gradlew assembleDebug --scan
```

The scan URL shows: task execution timeline, cache hit rates, dependency resolution details, and deprecation warnings. Use this when a build is slow or failing intermittently.

## Multi-Module Build Issues

- **Missing module**: `settings.gradle.kts` must `include(":moduleName")` for every module. A missing include silently ignores the module directory.
- **api vs implementation**: `api` exposes a dependency to consumers of the module; `implementation` keeps it internal. Wrong choice causes `Unresolved reference` in downstream modules.
- **Circular dependencies**: Module A depends on B and B depends on A. Gradle fails at configuration time. Extract shared code to a third module.
- **Build order**: Gradle builds modules in dependency order. A missing dependency declaration may work locally (if the module was built before) but fail on CI.

## Common Gradle Properties

| Property | Purpose |
|----------|---------|
| `android.useAndroidX=true` | Required for AndroidX libraries |
| `kotlin.code.style=official` | Kotlin formatting style |
| `org.gradle.jvmargs=-Xmx4g` | Daemon heap size — increase for large projects |
| `org.gradle.parallel=true` | Parallel module compilation |
| `org.gradle.caching=true` | Enable local build cache |
| `org.gradle.configuration-cache=true` | Enable configuration cache |
| `android.nonTransitiveRClass=true` | Each module gets only its own R class — reduces APK size and avoids resource collisions |
| `android.defaults.buildfeatures.buildconfig=false` | Disable BuildConfig generation unless explicitly enabled per module |
