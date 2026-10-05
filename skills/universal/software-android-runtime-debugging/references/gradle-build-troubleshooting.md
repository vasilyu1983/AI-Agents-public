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
- **Typo in group or artifact**: TOML syntax is `module = "group:artifact"` — a wrong group/artifact normally produces an unresolved-dependency failure.
- **Bundle vs library**: bundles group multiple libraries under one alias. Adding a library to a bundle without declaring it first causes sync failure.

After editing the catalog, run the affected task and inspect its resolved dependency graph. Use `--refresh-dependencies` only when repository metadata/cache behavior is the suspected cause.

## KSP vs KAPT

KSP (Kotlin Symbol Processing) is the preferred annotation processor for Kotlin projects. KAPT (Kotlin Annotation Processing Tool) is the legacy bridge to Java annotation processors.

- **Check the resolved KSP generation**: older KSP1 releases were compiler-coupled; KSP2 compatibility must be checked in [the upstream KSP documentation](https://github.com/google/ksp) and processor release notes. Do not infer compatibility from a version-string prefix.
- **Migration path**: replace `kapt("...")` with `ksp("...")` in `build.gradle.kts`. Room, Hilt, and Moshi all support KSP. Dagger/Hilt requires `dagger-compiler` for KSP.
- **KAPT stubs**: KAPT generates Java stubs from Kotlin before processing. Stale stubs after renaming cause phantom errors — clean build resolves them.
- **Cannot use both for the same processor**: if a library offers both KAPT and KSP, pick one. Using both causes duplicate processing.

## AGP Compatibility

Each AGP release pins a **minimum Gradle version** and a **minimum JDK to run Gradle**, and an AGP major can also raise the minimum Kotlin Gradle Plugin (KGP) version. Treat the chain AGP -> Gradle wrapper -> Gradle JDK -> KGP as one unit: never bump AGP without re-checking the other three. Do not copy a compatibility table into docs or build comments; the minimums move with every release.

**Lookup step:** open the release notes for the exact AGP version you are moving to at [developer.android.com/build/releases/gradle-plugin](https://developer.android.com/build/releases/gradle-plugin) and read its **Compatibility** table (minimum and default Gradle, SDK Build Tools, NDK, JDK). For older AGP lines, use the per-version release-notes page linked from there. For planned removals of legacy Variant/DSL APIs, check [developer.android.com/build/releases/gradle-plugin-roadmap](https://developer.android.com/build/releases/gradle-plugin-roadmap).

How mismatches present, and the fix:

| Symptom | Cause | Fix |
|---------|-------|-----|
| Plugin apply fails with `Android Gradle plugin requires Java <N> to run. You are currently using Java <M>.` (wrapped in `Failed to apply plugin 'com.android.internal.application'`) | The JDK **running Gradle** is below the AGP minimum. This is the Gradle JDK, not the project's Java toolchain. | Point Gradle at a compliant JDK: the Gradle JDK setting in Android Studio, `JAVA_HOME` for terminal builds, or `org.gradle.java.home` in `gradle.properties`. See [developer.android.com/build/jdks](https://developer.android.com/build/jdks). |
| Plugin apply fails with a message naming the minimum supported Gradle version and the current version | The Gradle wrapper is older than the AGP minimum. | Update `distributionUrl` in `gradle/wrapper/gradle-wrapper.properties` (or run `./gradlew wrapper --gradle-version <version>`) to at least the minimum in the AGP Compatibility table. |
| Unrelated-looking Gradle task or DSL error right after an AGP bump | Often a Gradle-wrapper mismatch or a removed/renamed DSL API, not an app-code regression. | Check wrapper version first, then the AGP release notes for removed APIs and flags. |
| "Built-in Kotlin" or Kotlin plugin errors after moving to AGP 9 | AGP 9 enables built-in Kotlin support by default and requires a minimum KGP version. | Remove the explicit `org.jetbrains.kotlin.android` plugin application where AGP already handles it, and raise KGP to the minimum named in the AGP release notes. |

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

**Isolation**: rerun the failing task with `--no-configuration-cache`. If that resolves it, inspect the reported incompatible plugin/input and the [Gradle configuration-cache guide](https://docs.gradle.org/current/userguide/configuration_cache.html) before clearing a scoped cache.

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

## Runtime-Linked Build Symptoms

| Symptom | Diagnostic check |
|---|---|
| Gradle daemon OOM | Read the daemon error and available memory; tune `org.gradle.jvmargs` for that build rather than copying a universal heap size |
| Missing generated `BuildConfig` | Inspect module `buildFeatures` and AGP migration notes; do not apply an obsolete global flag |
| Stale task outputs suspected | Compare `--no-build-cache` with the same task and inputs before clearing caches |

Formatting and generic optimization flags belong in [software-android-native](../../software-android-native/SKILL.md); they are not runtime fixes.
