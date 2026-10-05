---
name: software-android-runtime-debugging
description: "Build/install/launch proof, ANR/jank/memory triage, and stale-build debugging for native Android apps. Use when runtime truth, performance, or crash root cause is in doubt."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Native Android Runtime Debugging

Use this skill when the core problem is not app architecture or visual design, but runtime truth: did the current APK/AAB build, install, launch, and render on the intended emulator or device — and, once that's proven, why is it slow, freezing, or leaking memory?

This skill owns stale-build suspicion, emulator drift, malformed APKs, ADB failures, Gradle cache corruption, ProGuard/R8 stripping, Compose recomposition issues, ANR/jank/memory/startup performance triage, and the proof loop required before trusting screenshots, UI behavior, or downstream API/auth debugging.

## Platform Currency (look up, do not assume)

Platform facts drift within months. Before citing any of these, check the live source:

- **Current Android release and API level**: [developer.android.com/about/versions](https://developer.android.com/about/versions).
- **Google Play target API requirement and deadlines**: [developer.android.com/google/play/requirements/target-sdk](https://developer.android.com/google/play/requirements/target-sdk). Never hardcode the required level.
- **16 KB page-size support** for apps that ship native (`.so`) libraries: an app whose ELF `LOAD` segments are still 4 KB-aligned runs in a backcompat mode on 16 KB devices, so test on a 16 KB-page-size emulator image, not just the default. Check the current enforcement scope at [developer.android.com/guide/practices/page-sizes](https://developer.android.com/guide/practices/page-sizes).
- **AGP and Gradle minimums**: a new AGP major version can raise the minimum Gradle version and change Kotlin plugin defaults. Check [developer.android.com/build/releases/gradle-plugin-roadmap](https://developer.android.com/build/releases/gradle-plugin-roadmap) before assuming an older Gradle wrapper still works.
- **Android Studio release name and version**: [developer.android.com/studio/releases](https://developer.android.com/studio/releases). Google renames each yearly series.
- **Perfetto**, not Systrace, is the system- and app-tracing stack; Systrace is retired. See [references/performance-triage.md](references/performance-triage.md).

- Prefer developer.android.com for ADB, aapt2, AGP, and build system behavior.
- Prefer upstream Gradle documentation for wrapper, daemon, caching, and dependency resolution.
- Prefer developer.android.com/topic/performance for ANR thresholds, vitals thresholds, tracing (Perfetto), and Macrobenchmark/Baseline Profile guidance — these are Google-controlled policy numbers and tool defaults that move.
- Prefer perfetto.dev and square.github.io/leakcanary for Perfetto and LeakCanary specifics respectively.
- Treat repo-specific build variants, applicationId, module structure, and Gradle properties as local facts that must be discovered, not assumed.

## Quick Reference

| Symptom | First Move | Notes |
|--------|------------|-------|
| Screenshot does not match source | Check artifact/installed identity, then replace-install and launch | Preserve repro; follow the reset ladder below |
| `INSTALL_FAILED_UPDATE_INCOMPATIBLE` | Compare signing identities and preserve local evidence before uninstalling | Signing mismatch can require uninstall; it clears app data |
| App crashes immediately on launch | Check logcat for first `FATAL EXCEPTION` | Missing Activity in manifest or ProGuard stripping |
| `ClassNotFoundException` / `NoSuchMethodError` at runtime | Check ProGuard/R8 keep rules | Minification removed referenced class or method |
| Emulator stuck on boot animation | Cold boot AVD or wipe data | Snapshot corruption is common after SDK updates |
| `BUILD FAILED` with dependency resolution | Check `libs.versions.toml` and repositories block | Version catalog mismatch or missing repo |
| Gradle sync fails in Android Studio | `./gradlew --stop && ./gradlew --refresh-dependencies` | Daemon or cache corruption |
| `adb: device not found` | `adb kill-server && adb start-server && adb devices` | USB debugging off or emulator not connected |
| App shows old layout after Compose changes | Clean build; check recomposition stability | Incremental build may not invalidate Compose output |
| Resources not found at runtime | Inspect APK with `aapt2 dump resources` | Missing from merged manifest or wrong resource qualifier |
| `minSdk` version error on install | Check device API level vs `minSdk` in build.gradle.kts | APK requires higher API than device provides |
| KSP/KAPT annotation processing errors | Check resolved processor, KSP generation and Kotlin/AGP compatibility | Check the resolved KSP generation and its compatibility documentation |
| Logcat shows nothing from the app | Filter by PID: `adb logcat --pid=$(adb shell pidof <pkg>)` | Default logcat is too noisy to be useful |
| App works on emulator but crashes on device | Check for ABI-mismatched native libs (.so) | Emulator ABI depends on host (x86_64 on Intel hosts, arm64 on Apple Silicon); missing `arm64-v8a` or an x86_64-only `.so` is the usual cause, not emulator-vs-device x86-vs-ARM in general |
| Compose UI renders but interactions do nothing | Check clickable modifier order and state hoisting | Modifier order determines hit-testing; state must be hoisted |
| `CalledFromWrongThreadException` | Find the View-system call made off the main thread in the stack trace | Thrown when a View is touched off its owning thread; a `MutableStateFlow.value` write is thread-safe and is not the cause |
| `ConcurrentModificationException` inside `SnapshotStateObserver` | Match the stack to Compose release notes, then inspect snapshot writes | A thread-safe StateFlow write does not establish this cause |
| Nested `Popup` pinned to screen top instead of anchor | Check resolved Compose UI and matching release notes | Reproduce with the smallest popup/anchor hierarchy before changing app coordinates |
| `Argument type mismatch: Function0<Unit> vs @Composable ComposableFunction0<Unit>` | Verify `kotlin("plugin.compose")` is applied and version-locked to the Kotlin compiler | Kotlin 2.x ships the Compose compiler bundled; missing/stale plugin declaration skips the composable transform |
| Release serializer lookup crash | Verify compiler plugin, resolved runtime and merged consumer rules; reproduce in the minified variant | Serialization ships consumer rules; named companions need targeted additional rules |
| `LazyColumn` recomposes on unrelated updates | Inspect state reads and compiler reports; hoist expensive derivation only when measured | Call `remember` in an enclosing composable or item content, never in the non-composable `LazyListScope` DSL; see Compose triage |
| System shows "App isn't responding" or Play Console reports an ANR cluster | Read the ANR trace first, do not open a profiler yet | Blocked-thread stack is already in the trace; classify by which watchdog fired (input/no-focused-window/broadcast/service/provider) |
| Scrolling stutters or animation skips frames, app otherwise responsive | `adb shell dumpsys gfxinfo <pkg> framestats`, then Perfetto if the cause isn't obvious | This is jank, not an ANR — different tool, different budget math (16.67ms @60Hz, 8.33ms @120Hz) |
| App feels slower over a session or gets OOM-killed | `adb shell dumpsys meminfo <pkg>` trend, then LeakCanary or a debuggable heap dump; check supported field-capture APIs for release | Confirm monotonic growth before assuming a leak; one-time cache warm-up is not a leak |
| Cold start feels slow but no measurement exists yet | Macrobenchmark `StartupTimingMetric` with explicit `StartupMode.COLD` | Do not guess a fix before there's a baseline number; warm/hot starts have different budgets than cold |
| Dropped frame blamed on "GC" without checking the trace | Open the Perfetto thread-state track for that frame | Binder/IPC contention produces the same visible symptom as a GC pause and is commonly misdiagnosed as GC |

## When to Use This Skill

Use this skill to:

- Prove a fresh build/replace-install/launch loop for a native Android app
- Diagnose stale installs or stale screenshots in emulator-driven workflows
- Inspect built APK/AAB contents when installation or launch fails
- Debug emulator boot, ADB connectivity, and device state drift
- Investigate Gradle build failures, dependency resolution, and cache corruption
- Triage R8/ProGuard stripping errors that surface only at runtime
- Debug Compose recomposition, stability, and incremental compilation artifacts
- Classify and triage ANRs, jank, memory leaks, and slow startup using Perfetto, Macrobenchmark, LeakCanary, and StrictMode
- Establish runtime truth before routing to feature implementation, design, or test skills

## Core Workflow

1. Discover the project entrypoint: `build.gradle.kts` (root and app module), `applicationId`, build variant (debug/release), target device or emulator.
2. Check environment:
   `ANDROID_HOME` set, JDK version matches AGP requirement, Gradle wrapper present, `adb devices` shows the target, emulator booted or device connected.
3. Build the app: `./gradlew assembleDebug`.
   Confirm output ends with `BUILD SUCCESSFUL`.
4. Inspect the APK: `aapt2 dump badging app/build/outputs/apk/debug/app-debug.apk`.
   Verify `applicationId`, `versionCode`, `minSdk`, declared activities, and expected resources.
5. Preserve reproduction state before any reset: record account, deep link/intent, local data dependency, and the installed package/version/signing identity. Export logs and screenshots first.
6. Replace-install the fresh build without clearing data:
   `adb install -r app/build/outputs/apk/debug/app-debug.apk`.
   Uninstall or clear data only when replace-install fails, signatures differ, state migration is the suspected cause, or the current evidence has already been preserved.
7. Launch and capture proof:
   `adb shell am start -n <applicationId>/<fully.qualified.Activity>`, then capture logcat output and a screenshot (`adb exec-out screencap -p > proof.png`).
8. Only after the app is freshly running, debug feature behavior, design, auth, or API issues.
9. Route onward:
   - native feature or architecture work -> [software-android-native](../software-android-native/SKILL.md)
   - test execution and device matrix -> [qa-testing-android](../qa-testing-android/SKILL.md)
   - general debugging methodology -> [qa-debugging](../qa-debugging/SKILL.md)

## Runtime Proof Loop

- Prefer one bounded loop:
  discover -> check env -> build -> inspect APK -> preserve repro -> replace-install -> launch -> capture evidence -> then debug.
- Escalate to clean build, clear data, or uninstall one step at a time. Record which reset makes the symptom disappear; that difference is diagnostic evidence, not housekeeping.
- If any step fails, stop there and fix that layer before moving deeper.
- Do not trust screenshots from an emulator session that has not been tied to the current build.
- Do not trust "BUILD SUCCESSFUL" on its own; install and launch proof still matter.
- Verify launch at three levels: the process started (`adb shell pidof <pkg>`), the correct Activity is in the foreground (`adb shell dumpsys activity top`), and the expected content rendered (screenshot or UI automator dump).
- If a screenshot contradicts the expected state, check the installed APK's `versionCode` against the build output before trusting the capture.
- For agent-driven device loops, check whether Google's agent tooling (Android CLI, Journeys) is installed — see [developer.android.com/tools/agents](https://developer.android.com/tools/agents) for current commands. Otherwise fall back to adb: `adb shell uiautomator dump` for hierarchy assertions, plus `adb exec-out screencap -p` for visual proof.

See [references/runtime-proof-loop.md](references/runtime-proof-loop.md).

## Stale-Build Heuristics

- If the UI on screen does not match current source, suspect stale APK before any other explanation.
- If an old layout persists, compare the installed artifact and selected variant, replace-install, then clean-build if needed; clear data or uninstall only after preserving repro evidence.
- If Gradle says build succeeded but the app looks old, check the APK timestamp and path — the wrong variant or module may have been built.
- If the emulator was already running and UI state is surprising, re-prove install and launch before reasoning about app state.
- If incremental compilation is suspected, clean-build as the next rung after checking artifact identity and replace-install.
- If the Gradle daemon has been running for hours with changing `jvmargs` or plugin versions, stop it with `./gradlew --stop` and rebuild.

See [references/stale-build-triage.md](references/stale-build-triage.md).

## APK/AAB Health Checklist

When installation or launch fails, inspect the built artifact directly:

- [ ] `aapt2 dump badging <apk>` — verify `applicationId`, `versionCode`, `minSdk`, `targetSdk`, declared activities and permissions
- [ ] Launcher Activity declared with correct intent filter in merged manifest (`app/build/intermediates/merged_manifests/`)
- [ ] Expected resources present: `aapt2 dump resources <apk>`
- [ ] For apps with native code: `.so` files present for correct ABIs (`lib/arm64-v8a/`, `lib/armeabi-v7a/`, `lib/x86_64/`)
- [ ] For release builds: `mapping.txt` exists alongside the APK for crash symbolication

## Gradle Troubleshooting Patterns

Gradle is the most common source of build failures. Common patterns: dependency resolution, version catalog drift, KSP/KAPT version mismatches, AGP compatibility, and configuration cache invalidation.

See [references/gradle-build-troubleshooting.md](references/gradle-build-troubleshooting.md).

## Compose Debugging

Jetpack Compose introduces recomposition, stability, and compiler-level concerns that do not exist in View-based UI. When Compose UI behaves unexpectedly — interactions silently fail, UI does not update, or performance is poor — use Compose-specific debugging before blaming app logic.

See [references/compose-debugging.md](references/compose-debugging.md).

## Performance Triage: ANR, Jank, Memory, Startup

Once build/install/launch is proven, "the app is slow" or "the app freezes" is not one problem — it is an ANR, jank, a memory leak, or a slow start, and each has a different first move. Classify before reaching for a profiler:

1. System ANR dialog or a Play Console ANR cluster exists -> read the ANR trace, find the blocked thread and which watchdog (input/no-focused-window/broadcast/service/provider) fired.
2. Stutter or skipped frames while the app stays responsive -> jank. Start with `framestats`, escalate to Perfetto.
3. The app slows down over a session or gets OOM-killed -> memory. Confirm a growth trend with `dumpsys meminfo` before assuming a leak.
4. The complaint is specifically about time-to-first-frame after tapping the icon -> startup. Measure with Macrobenchmark before changing code.
5. None of the above -> it is a correctness bug, not a performance problem; route to normal crash/log triage.

**When not to microbenchmark**: a microbenchmark measures one function's CPU cost in isolation. It cannot see cold-start AOT/JIT/class-loading cost (use Macrobenchmark instead), cannot see multi-frame jank pipeline stages (use Perfetto/`framestats` first), and should never run before a trace has confirmed the function is actually on the critical path.

**Common misdiagnosis to catch**: a dropped frame during an IPC-heavy screen looks identical to a GC pause from the outside. Check the Perfetto thread-state track — GC pauses show explicit GC markers; binder contention shows the calling thread blocked on a transaction to another process. Do not write "it's GC" into a report without checking the trace.

See [references/performance-triage.md](references/performance-triage.md) for the full decision tree, ANR thresholds, frame budget math, field profiling, native tombstones, Perfetto SQL, Macrobenchmark/StrictMode/LeakCanary usage and Play Console vitals lookup, and more misdiagnosis patterns.

## ProGuard/R8 Triage

R8 (the default code shrinker) can remove classes, methods, and fields that are referenced only via reflection, serialization, or framework conventions. When release builds crash with `ClassNotFoundException`, `NoSuchMethodError`, or silent data corruption, suspect R8 stripping before app logic.

See [references/proguard-r8-triage.md](references/proguard-r8-triage.md).

## Route Elsewhere

- Use [software-android-native](../software-android-native/SKILL.md) once runtime truth is established and the task becomes feature implementation, Kotlin architecture, or Compose layout.
- Use [qa-testing-android](../qa-testing-android/SKILL.md) once the app is buildable and installable and the task becomes test execution, device matrix, or flake control.
- Use [qa-debugging](../qa-debugging/SKILL.md) for general debugging methodology not specific to Android build/install/launch.
- Use [software-mobile](../software-mobile/SKILL.md) for platform choice, iOS, or cross-platform tradeoffs.

## Navigation

### References

| Resource | Purpose |
|----------|---------|
| [references/runtime-proof-loop.md](references/runtime-proof-loop.md) | Canonical build/install/launch verification loop |
| [references/stale-build-triage.md](references/stale-build-triage.md) | Heuristics for stale APKs, Gradle cache, and emulator drift |
| [references/gradle-build-troubleshooting.md](references/gradle-build-troubleshooting.md) | Dependency resolution, version catalogs, AGP, and daemon issues |
| [references/compose-debugging.md](references/compose-debugging.md) | Recomposition tracking, stability, compiler reports, and common pitfalls |
| [references/proguard-r8-triage.md](references/proguard-r8-triage.md) | R8 stripping, keep rules, mapping files, and library-specific rules |
| [references/performance-triage.md](references/performance-triage.md) | ANR/jank/memory/startup decision tree, Perfetto, Macrobenchmark, StrictMode, LeakCanary, ART GC, Play Console vitals, misdiagnoses |
| [data/sources.json](data/sources.json) | Primary Android platform and tooling sources |

### Templates

| Template | Purpose |
|----------|---------|
| [assets/template-android-runtime-debug-request.md](assets/template-android-runtime-debug-request.md) | Short request format for proof-first runtime debugging |

### Related Skills

| Skill | Purpose |
|-------|---------|
| [software-android-native](../software-android-native/SKILL.md) | Native Android implementation and architecture after runtime truth exists |
| [qa-testing-android](../qa-testing-android/SKILL.md) | Espresso, UI Automator, Compose testing, and device matrix after installability is proven |
| [qa-debugging](../qa-debugging/SKILL.md) | General debugging methodology not specific to Android runtime |
| [software-mobile](../software-mobile/SKILL.md) | Mobile platform choice and cross-platform tradeoffs |

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
