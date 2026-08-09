# Performance Triage: ANR, Jank, Memory, Startup

## Table of Contents

- [Triage Decision Tree](#triage-decision-tree)
- [ANR Thresholds](#anr-thresholds)
- [Frame Budget Arithmetic](#frame-budget-arithmetic)
- [Perfetto Is the Tracing Stack](#perfetto-is-the-tracing-stack)
- [Macrobenchmark and Baseline Profiles](#macrobenchmark-and-baseline-profiles)
- [When NOT to Microbenchmark](#when-not-to-microbenchmark)
- [Memory Leak Triage](#memory-leak-triage)
- [StrictMode](#strictmode)
- [ART Runtime Behavior](#art-runtime-behavior)
- [Play Console Vitals Thresholds](#play-console-vitals-thresholds)
- [Common Misdiagnoses](#common-misdiagnoses)

A "runtime failure" report is frequently not one problem — a user says "the app is slow" or "the app freezes" and the actual cause could be an ANR, a jank episode, a slow cold start, or a memory leak that only manifests as jank right before an OOM kill. Classify before instrumenting; the tool you reach for depends entirely on which bucket the symptom falls into.

## Triage Decision Tree

Ask these questions in order — each one either resolves the bucket or rules it out:

1. **Did the system show an "App isn't responding" dialog, or does Play Console / `dumpsys activity` show an ANR trace?**
   Yes -> this is an **ANR**. Go straight to the ANR trace (`/data/anr/traces.txt` on a debug build, or the trace attached to a Play Console ANR cluster) and find which thread was blocked and for how long. Do not start with a profiler; the trace already names the blocked stack.
2. **Is the complaint about stutter, skipped frames, or a laggy scroll while the app is visibly responsive (no system dialog, no watchdog kill)?**
   Yes -> this is **jank**. Use Perfetto (or `adb shell dumpsys gfxinfo <pkg> framestats` for a quick first look) to find which frames missed budget and why (long main-thread work, layout thrashing, GC pause, or an oversized bitmap decode on the UI thread).
3. **Is the complaint about the app getting slower over a session, background-app-restore feeling wrong, or an eventual crash with `OutOfMemoryError`?**
   Yes -> this is a **memory** problem. Confirm with `adb shell dumpsys meminfo <pkg>` trending upward across repeated navigation of the same screen, then use LeakCanary (debug builds) or a heap dump + Android Studio Memory Profiler (any build) to find the retained object graph.
4. **Is the complaint specifically about time-to-first-frame or time-to-interactive after tapping the launcher icon?**
   Yes -> this is a **startup** problem. Measure with Macrobenchmark's `StartupTimingMetric` before touching code — a felt-slow startup and a measured-slow startup are not always the same thing, and guessing at a fix without a baseline number wastes the loop.
5. **None of the above — the app produced wrong output, a stack trace, or crashed outside of memory pressure.**
   This is a correctness bug, not a performance problem. Route to normal crash/log triage (see the runtime proof loop and `qa-debugging`), not this reference.

Do not skip straight to "attach a profiler" for any of these. Each bucket has a first move that is cheaper and more diagnostic than a general-purpose trace: the ANR trace file for ANRs, `framestats` for jank, `meminfo` trend for memory, `StartupTimingMetric` for startup.

## ANR Thresholds

Re-derive these from the trace timestamps rather than assuming a single "5 second" rule applies everywhere — the timeout depends on which watchdog fired:

- **Input dispatch: 5 seconds.** The main thread did not return from a touch/key event within 5s. This is the most common production ANR class and is almost always a synchronous DB/network/disk call on the main thread, not a genuinely 5-second computation.
- **Broadcast receiver: 10s foreground / 60s background.** `onReceive()` ran past the window for the app's current process state.
- **Service execution: 20s foreground / 200s background.** `onCreate()`/`onStartCommand()`/`onBind()` blocked past the window for the service's process state.
- **Foreground service start: 5 seconds.** `startForegroundService()` must reach `startForeground()` within 5s.

These specific numbers move across Android releases; verify the current values at [developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) before treating them as fixed constants in a report. See also [software-android-native/SKILL.md](../../software-android-native/SKILL.md) → "ANR and Frame Budget Arithmetic", which carries the same figures for architecture-level decisions; this file is the diagnostic-triage counterpart.

## Frame Budget Arithmetic

Always re-derive; do not quote a remembered millisecond figure without checking the refresh rate first.

- **60Hz: 1000ms ÷ 60 = 16.666...ms per frame**, commonly rounded to 16.67ms. A composable's measure/layout/draw pass exceeding this drops a frame; two consecutive misses read as visible jank.
- **120Hz: 1000ms ÷ 120 = 8.333...ms per frame**, commonly rounded to 8.33ms. High-refresh-rate hardware halves the available budget. A screen that was smooth at 60Hz on an emulator can visibly jank at 120Hz on a physical device — verify on the actual target refresh rate with `adb shell dumpsys gfxinfo <pkg> framestats` or Android Studio's Frame Profiler, not just on the emulator's default 60Hz.

## Perfetto Is the Tracing Stack

Systrace is retired. **Perfetto** is the current system- and app-tracing stack for Android (introduced with Android 10, and the only tracing surface actively developed since); it replaces Systrace's chromium-based tooling and reads Systrace/Chromium-JSON/ftrace formats for backward compatibility. Do not propose Systrace commands (`systrace.py`, the old `am_systrace` category flags) as a live recommendation — if a repo's docs still reference Systrace, treat that as the stale artifact, not the current tool.

Practical entry points:

- Record from the command line: `adb shell perfetto -o /data/misc/perfetto-traces/trace.pftrace -t 20s sched freq idle am wm gfx view` (adjust categories to the investigation).
- Record from Android Studio's Profiler (System Trace recording uses Perfetto under the hood on supported API levels).
- Analyze at [ui.perfetto.dev](https://ui.perfetto.dev) — it loads `.pftrace` files directly in the browser and gives per-thread, per-frame, and binder-transaction views.

Verify current recording flags and minimum API support at [developer.android.com/topic/performance/tracing](https://developer.android.com/topic/performance/tracing) and [perfetto.dev/docs/getting-started/system-tracing](https://perfetto.dev/docs/getting-started/system-tracing) before pasting an exact command into a report — category names have changed release to release.

## Macrobenchmark and Baseline Profiles

**Baseline Profiles** ship a list of classes/methods for ART to ahead-of-time (AOT) compile on install, instead of interpreting or JIT-compiling them on first run. This mainly helps cold/warm startup and first-interaction jank; it does not fix an algorithmic slowdown deep in a hot loop.

**Macrobenchmark** (`androidx.benchmark:benchmark-macro-junit4`) is the library that both generates Baseline Profiles (`BaselineProfileRule`) and measures the effect (`StartupTimingMetric`, `FrameTimingMetric`). It drives the app as a black box from a separate test process — this is deliberate: it measures what a real user experiences, including process start and AOT/JIT behavior, which an in-process microbenchmark cannot see.

Minimum versions move; verify current requirements (AGP, `benchmark-macro-junit4`, `profileinstaller`) at [developer.android.com/topic/performance/baselineprofiles/overview](https://developer.android.com/topic/performance/baselineprofiles/overview) and [developer.android.com/topic/performance/benchmarking/macrobenchmark-overview](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview) before pinning a version number in a build file.

## When NOT to Microbenchmark

A **microbenchmark** (`androidx.benchmark:benchmark-junit4`, in-process, JIT/AOT state controlled) measures a single function's CPU cost in isolation. It is the wrong tool — and a common expert-level misdiagnosis to reach for it too early — when:

- The complaint is about startup or first-frame time. Macrobenchmark measures the real process-cold-start path; a microbenchmark runs inside an already-warm test process and cannot see AOT/JIT/class-loading cost, which is usually the actual bottleneck.
- The complaint is about jank during a user interaction that spans multiple frames (scrolling, animation). Jank is a property of the frame pipeline (Choreographer, RenderThread, GPU), not a single function's execution time; use Perfetto/`framestats` first to locate which frame and which stage is slow, then microbenchmark only the specific function identified as the culprit.
- There is no reproducible measurement baseline yet. Microbenchmarking a function before confirming it is even on the critical path (via a trace) risks optimizing code that was never the bottleneck — a classic case of "fixing" 2ms out of a 200ms frame.
- The suspected cost involves IPC, disk, or network. Microbenchmarks are designed for pure CPU work with controlled JIT state; I/O-bound and binder-bound costs need Perfetto's system-wide view (to see contention with other processes/threads), not an isolated loop.

Reach for a microbenchmark only after a trace has already identified a specific hot function as the dominant cost on the critical path.

## Memory Leak Triage

1. **Confirm it's a leak, not expected retention.** `adb shell dumpsys meminfo <pkg>` across several minutes of normal navigation (visit-and-return to the same screen repeatedly). A monotonically increasing Java heap that never returns to baseline after `System.gc()` and navigating away is the leak signal; a one-time increase that plateaus is often just cache warm-up.
2. **LeakCanary for debug builds.** LeakCanary automatically detects and dumps retained-object chains for common leak patterns (Activity/Fragment/View outliving its lifecycle owner) with zero manual heap-dump work. As of 2026-07-11 the stable production line is the 2.x series (2.14, released 2024-04-17); a 3.0 alpha line is in active development. Verify the current recommended version at [square.github.io/leakcanary](https://square.github.io/leakcanary/) before pinning a version — do not assume a 3.0 stable release exists without checking.
3. **Manual heap dump for release builds or leaks LeakCanary doesn't catch.** Android Studio Profiler → Memory → "Dump Java heap", then use the Analyzer view to find the shortest path from a GC root. Common root causes: a static field holding a `Context` or `View`, an anonymous inner class (listener, `Runnable`, coroutine) capturing an outer `Activity`/`Fragment` reference across a lifecycle boundary, and a registered listener/callback never unregistered in `onDestroy()`/`onCleared()`.
4. **Coroutine-specific leak pattern.** `GlobalScope.launch { ... }` or a manually-created `CoroutineScope` without a matching cancel survives navigation indefinitely and holds whatever it captured. See [software-android-native/SKILL.md](../../software-android-native/SKILL.md) Kotlin Anti-Patterns table (K1) for the fix.

## StrictMode

`android.os.StrictMode` is a free, in-process detector for accidental disk/network access on the main thread and for object leaks (unclosed `Closeable`, leaked `SQLiteCursor`/`Activity`). It costs nothing beyond enabling it in `Application.onCreate()` and is complementary to, not a replacement for, Perfetto tracing and LeakCanary — StrictMode tells you *that* a violation happened and where, not the full timeline or retained-object graph.

```kotlin
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder().detectAll().penaltyLog().build()
    )
    StrictMode.setVmPolicy(
        StrictMode.VmPolicy.Builder().detectAll().penaltyLog().build()
    )
}
```

Never ship `StrictMode` enabled with `penaltyDeath()` (or any policy at all) in a release build — gate it behind `BuildConfig.DEBUG`. Treat any StrictMode violation log as a lead to investigate, not noise to suppress; disk/network on the main thread is a direct contributor to input-dispatch ANRs. Verify current detector coverage at [developer.android.com/reference/android/os/StrictMode](https://developer.android.com/reference/android/os/StrictMode) since detectable violation types have expanded across releases.

## ART Runtime Behavior

The Android Runtime (ART) is the sole runtime on all currently supported Android versions (Dalvik has been gone since Android 5.0). Two behaviors matter for triage:

- **AOT/JIT hybrid compilation.** A freshly installed app runs interpreted or JIT-compiled until ART's background `dex2oat` compilation (or a shipped Baseline Profile) produces optimized code. This is why the *first* run after install is measurably slower than the *tenth* — a startup regression report should specify which run it was measured on.
- **Generational, concurrent garbage collection.** Modern ART GC runs concurrently with the app on most collections, but a large single allocation, a full GC (triggered by heap pressure or an explicit `System.gc()`), or GC running on the same core as the main thread under load can still produce a visible pause. A GC pause and jank look identical from the outside (a dropped frame) — a Perfetto trace will show the GC event explicitly; do not assume a dropped frame is a GC pause without confirming it in the trace (see "Common Misdiagnoses" below).

## Play Console Vitals Thresholds

Google Play uses **user-perceived** rates (an ANR or crash that happened while the user was actively interacting with the app, not a background occurrence) as the core-vitals discoverability signal:

- **User-perceived ANR rate — bad behavior thresholds:** at least 0.47% of daily active users overall, or at least 8% of daily users on a single device model.
- **User-perceived crash rate — bad behavior thresholds:** at least 1.09% of daily active users overall, or at least 8% of daily users on a single device model.

Exceeding the overall threshold reduces store discoverability across all devices; exceeding the per-device threshold reduces discoverability (and can show a store warning) only on the affected device models. These percentages are Google's current published figures as of 2026-07-11 and have changed before — verify at [developer.android.com/topic/performance/vitals/anr](https://developer.android.com/topic/performance/vitals/anr) and [developer.android.com/topic/performance/vitals/crash](https://developer.android.com/topic/performance/vitals/crash) before citing them in a release-readiness decision.

## Common Misdiagnoses

Patterns an expert catches before writing a root-cause report:

- **"It's GC" when it's actually binder contention.** A dropped frame during a screen that makes an IPC call (ContentProvider query, system service call, cross-process AIDL) is frequently blamed on garbage collection because both produce a generic "main thread was blocked" symptom. Perfetto's thread-state track distinguishes a GC pause (visible GC markers, `Waiting for a blocking GC` states) from a binder call blocked on another process (the calling thread shows in `Blocked`/`Uninterruptible Sleep` waiting on a binder transaction, and the *other* process's thread is doing the work). Check the trace before writing "GC" in a report.
- **"It's the emulator" when the code is genuinely slow.** Emulator CPU/GPU performance does not track physical device performance linearly, but a real O(n²) list operation or main-thread network call is exactly as slow on both — do not dismiss a profiled hotspot as "just emulator overhead" without confirming on a physical device first.
- **"It's cold start" when it's actually a warm/hot start regression.** Users describe all slow launches as "the app is slow to open," but ART/process reuse means a warm or hot start (process already alive, only Activity recreation) has a very different budget and cause than a true cold start (new process, `Application.onCreate()`, full class loading). Use Macrobenchmark's `StartupTimingMetric` with explicit `StartupMode.COLD`/`WARM`/`HOT` to separate these before proposing a fix.
- **Treating one profiler run as ground truth.** A single Perfetto trace or `framestats` sample can be dominated by an unrelated background task (a scheduled sync, another app, a system service). Confirm a jank or ANR pattern across at least two to three reproductions, or check Play Console's aggregated vitals, before committing to a root cause from one trace.
- **Fixing the symptom frame instead of the triggering allocation/call.** The dropped frame in a trace is often the *victim* (e.g., where a GC triggered by an allocation two frames earlier finally causes a pause), not the cause. Walk the trace backward from the janky frame to find what actually triggered the GC or blocking call.
