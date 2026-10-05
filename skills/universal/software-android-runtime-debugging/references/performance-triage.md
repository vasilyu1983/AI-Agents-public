# Performance Triage: ANR, Jank, Memory, Startup

## Table of Contents

- [Triage Decision Tree](#triage-decision-tree)
- [ANR Classification and Timeout Lookup](#anr-classification-and-timeout-lookup)
- [Frame Budget Arithmetic](#frame-budget-arithmetic)
- [Perfetto Is the Tracing Stack](#perfetto-is-the-tracing-stack)
- [Field Profiling and App Quality Insights](#field-profiling-and-app-quality-insights)
- [Native Crash Triage](#native-crash-triage)
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
   Yes -> this is an **ANR**. Go straight to the ANR trace — newer releases write `/data/anr/anr_*` files (needs root or `adb bugreport`; `/data/anr/traces.txt` only exists on older releases), or pull it in-app via `ApplicationExitInfo.getTraceInputStream()` (API 30+), or use the trace attached to a Play Console ANR cluster — and find which thread was blocked and for how long. Do not start with a profiler; the trace already names the blocked stack.
2. **Is the complaint about stutter, skipped frames, or a laggy scroll while the app is visibly responsive (no system dialog, no watchdog kill)?**
   Yes -> this is **jank**. Use Perfetto (or `adb shell dumpsys gfxinfo <pkg> framestats` for a quick first look) to find which frames missed budget and why (long main-thread work, layout thrashing, GC pause, or an oversized bitmap decode on the UI thread).
3. **Is the complaint about the app getting slower over a session, background-app-restore feeling wrong, or an eventual crash with `OutOfMemoryError`?**
   Yes -> this is a **memory** problem. Confirm with `adb shell dumpsys meminfo <pkg>` trending upward across repeated navigation of the same screen, then use LeakCanary (debug builds) or a heap dump + Android Studio heap analysis (capture requires a supported debuggable configuration) to find the retained object graph.
4. **Is the complaint specifically about time-to-first-frame or time-to-interactive after tapping the launcher icon?**
   Yes -> this is a **startup** problem. Measure with Macrobenchmark's `StartupTimingMetric` before touching code — a felt-slow startup and a measured-slow startup are not always the same thing, and guessing at a fix without a baseline number wastes the loop.
5. **None of the above — the app produced wrong output, a stack trace, or crashed outside of memory pressure.**
   This is a correctness bug, not a performance problem. Route to normal crash/log triage (see the runtime proof loop and `qa-debugging`), not this reference.

Do not skip straight to "attach a profiler" for any of these. Each bucket has a first move that is cheaper and more diagnostic than a general-purpose trace: the ANR trace file for ANRs, `framestats` for jank, `meminfo` trend for memory, `StartupTimingMetric` for startup.

<a id="anr-thresholds"></a>

## ANR Classification and Timeout Lookup

Read the subject and full thread dump before choosing a fix. [Android's diagnosis guide](https://developer.android.com/topic/performance/anrs/diagnose-and-fix-anrs) distinguishes these watchdogs; look up the timeout for the device's OS and OEM before quoting it. Broadcast timeouts depend on `FLAG_RECEIVER_FOREGROUND` and CPU starvation, not simply whether the app is visible.

| ANR class | Evidence to inspect |
|---|---|
| Input dispatch | Main-thread blocking call, lock holder, GPU or scheduling delay |
| No focused window (input dispatch subtype) | Time to first frame and window focusability, including `FLAG_NOT_FOCUSABLE` |
| Broadcast receiver | Receiver thread; with `goAsync()`, worker scheduling and every path to `PendingResult.finish()`; cold start counts |
| Execute service | Main-thread `onCreate` / `onStartCommand` / `onBind`, plus cold start |
| Content provider not responding | Remote provider cold start, slow query and binder-pool exhaustion; timeout comes from `ContentProviderClient.setDetectNotResponding()` |
| Slow job response | `JobService.onStartJob` / `onStopJob` and notification delivery |

A foreground-service promotion failure is a separate failure path: inspect the exception and [service troubleshooting guide](https://developer.android.com/develop/background-work/services/fgs/troubleshooting), rather than calling it a universal ANR timeout.

## Frame Budget Arithmetic

Always re-derive; do not quote a remembered millisecond figure without checking the refresh rate first.

- **60Hz: 1000ms ÷ 60 = 16.666...ms per frame**, commonly rounded to 16.67ms. This is the nominal display interval; app CPU work shares the frame pipeline with rendering and GPU work. Use FrameTimeline deadlines to classify actual misses.
- **120Hz: 1000ms ÷ 120 = 8.333...ms per frame**, commonly rounded to 8.33ms. Doubling refresh rate halves the nominal interval. A screen that was smooth at 60Hz on an emulator can visibly jank at 120Hz on a physical device — verify on the actual target refresh rate with `adb shell dumpsys gfxinfo <pkg> framestats` or Android Studio's Frame Profiler, not just on the emulator's default 60Hz.

## Perfetto Is the Tracing Stack

Use Perfetto for new system-tracing investigations. [Android system tracing](https://developer.android.com/topic/performance/tracing) explains which capture formats are available on the target OS; keep old Systrace captures as historical evidence rather than assuming they use today's recording commands.

Practical entry points:

- Record from the command line: `adb shell perfetto -o /data/misc/perfetto-traces/trace.pftrace -t 20s sched freq idle am wm gfx view` (adjust categories to the investigation).
- Record from Android Studio's Profiler (System Trace recording uses Perfetto under the hood on supported API levels).
- Analyze at [ui.perfetto.dev](https://ui.perfetto.dev) — it loads `.pftrace` files directly in the browser and gives per-thread, per-frame, and binder-transaction views.

Verify current recording flags and minimum API support at [developer.android.com/topic/performance/tracing](https://developer.android.com/topic/performance/tracing) and [perfetto.dev/docs/getting-started/system-tracing](https://perfetto.dev/docs/getting-started/system-tracing) before pasting an exact command into a report — category names have changed release to release.

For repeatable analysis, use [Trace Processor SQL](https://perfetto.dev/docs/analysis/trace-processor) over the same capture and time window. In Perfetto UI's SQL query pane, this example ranks completed slices by duration; durations are nanoseconds and this is a candidate list, not proof of the critical path:

```sql
SELECT name, dur / 1e6 AS duration_ms
FROM slice
WHERE dur > 0
ORDER BY dur DESC
LIMIT 20;
```

Use `trace_processor` (or the installed package's `trace_processor_shell`) for batch queries; check its `--help` for that build's file/query flags. Restrict results to the app's process/thread and reproduction interval, then correlate `thread_state`, scheduler and binder tracks before assigning causality.

## Field Profiling and App Quality Insights

- [ProfilingManager](https://developer.android.com/reference/android/os/ProfilingManager) begins at API 35; API 36 adds event-trigger registration. For field-only issues, use the [capture guide](https://developer.android.com/topic/performance/tracing/profiling-manager/overview) and its recommended AndroidX wrappers. Register an executor/listener, handle failure and rate limiting, and treat a missing capture as unavailable evidence. Look up supported types and trigger availability on the actual OS; captures can contain sensitive runtime data.
- [App Quality Insights](https://developer.android.com/studio/debug/app-quality-insights) brings Crashlytics and Android vitals stacks into Android Studio. Select the production application ID, affected version and device/OS cohort, then compare the stack with the source revision that shipped. Check IDE/cloud compatibility before promising integration; cached offline reports are historical. Play and Crashlytics counts can differ because their collection populations differ.

## Native Crash Triage

For `SIGSEGV` / `SIGABRT`, capture the native crash log or tombstone rather than searching only for Java `FATAL EXCEPTION`. `/data/tombstones/` normally needs privileged access; use an available bugreport or production crash report when direct access is denied. Preserve the signal, abort message, crashing thread and library build IDs.

Use matching **unstripped** libraries for the shipped build and ABI:

```bash
"$ANDROID_NDK_HOME/ndk-stack" -sym <matching-unstripped-abi-directory> -dump <native-crash.txt>
```

Keep the initial asterisk crash-header line or `ndk-stack` may not parse the report. [The NDK guide](https://developer.android.com/ndk/guides/ndk-stack) gives AGP's symbol-output paths and usage. Archive native debug symbols with each artifact; Java `mapping.txt` cannot symbolize C/C++ addresses. A symbolization failure or mismatched build ID leaves the frame unverified.

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

1. **Confirm it's a leak, not expected retention.** `adb shell dumpsys meminfo <pkg>` across several minutes of normal navigation (visit-and-return to the same screen repeatedly). Persistent retained objects after navigation and collection are a leak lead; `System.gc()` is only a request, so a heap trend alone does not prove a leak; a one-time increase that plateaus is often just cache warm-up.
2. **LeakCanary for debug builds.** Use its retained-object chains to find lifecycle owners held after navigation. Look up installation and version compatibility at [LeakCanary](https://square.github.io/leakcanary/).
3. **Manual heap dump.** [Android Studio heap capture](https://developer.android.com/studio/profile/capture-heap-dump) uses a debuggable profiling configuration. For a field release, check supported ProfilingManager capture types rather than promising that Studio can dump any release process. Inspect paths to GC roots: static Context/View references, captured lifecycle owners and callbacks that were never unregistered.
4. **Coroutine-specific leak pattern.** `GlobalScope.launch { ... }` or a manually-created `CoroutineScope` without a matching cancel survives navigation indefinitely and holds whatever it captured. See [software-android-native/SKILL.md](../../software-android-native/SKILL.md) Kotlin Anti-Patterns table (K1) for the fix.

## StrictMode

`android.os.StrictMode` is a free, in-process detector for accidental disk/network access on the main thread and for object leaks (unclosed `Closeable`, leaked `SQLiteCursor`/`Activity`). It adds diagnostic work and complements Perfetto tracing and LeakCanary — StrictMode tells you *that* a violation happened and where, not the full timeline or retained-object graph.

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

Gate this diagnostic sample behind `BuildConfig.DEBUG`; do not ship `penaltyDeath()` unintentionally. A production logging policy needs a measured overhead and reporting decision. Treat any StrictMode violation log as a lead to investigate, not noise to suppress; disk/network on the main thread is a direct contributor to input-dispatch ANRs. Verify current detector coverage at [developer.android.com/reference/android/os/StrictMode](https://developer.android.com/reference/android/os/StrictMode) since detectable violation types have expanded across releases.

## ART Runtime Behavior

The Android Runtime (ART) is the sole runtime on all currently supported Android versions (Dalvik has been gone since Android 5.0). Two behaviors matter for triage:

- **AOT/JIT hybrid compilation.** A freshly installed app runs interpreted or JIT-compiled until ART's background `dex2oat` compilation (or a shipped Baseline Profile) produces optimized code. This can change startup cost across runs — a startup regression report should specify which run it was measured on.
- **Generational, concurrent garbage collection.** Modern ART GC runs concurrently with the app on most collections, but a large single allocation, a full GC (triggered by heap pressure or an explicit `System.gc()`), or GC running on the same core as the main thread under load can still produce a visible pause. A GC pause and jank look identical from the outside (a dropped frame) — a Perfetto trace will show the GC event explicitly; do not assume a dropped frame is a GC pause without confirming it in the trace (see "Common Misdiagnoses" below).

## Play Console Vitals Thresholds

Google Play uses **user-perceived** rates (an ANR or crash that happened while the user was actively interacting with the app, not a background occurrence) as the core-vitals discoverability signal. Only ANRs of type `Input dispatching timed out` count toward the user-perceived ANR rate — broadcast/service/content-provider ANR clusters do not move this core vital, which changes triage priority.

Look up the current overall/per-device bad-behavior thresholds and metric eligibility in [ANR vitals](https://developer.android.com/google/play/vitals/anr), [crash vitals](https://developer.android.com/google/play/vitals/crash), and the [vitals overview](https://developer.android.com/google/play/vitals). Record the metric, denominator, cohort and time window used in the decision; do not store a second threshold table here. Overall and device-specific discoverability effects differ.

## Common Misdiagnoses

Patterns an expert catches before writing a root-cause report:

- **"It's GC" when it's actually binder contention.** A dropped frame during a screen that makes an IPC call (ContentProvider query, system service call, cross-process AIDL) is frequently blamed on garbage collection because both produce a generic "main thread was blocked" symptom. Perfetto's thread-state track distinguishes a GC pause (visible GC markers, `Waiting for a blocking GC` states) from a binder call blocked on another process (the calling thread shows in `Blocked`/`Uninterruptible Sleep` waiting on a binder transaction, and the *other* process's thread is doing the work). Check the trace before writing "GC" in a report.
- **"It's the emulator" when the code is genuinely slow.** Emulator CPU/GPU performance does not track physical device performance linearly, but an O(n²) list operation or main-thread network call remains a code problem on either — do not dismiss a profiled hotspot as "just emulator overhead" without confirming on a physical device first.
- **"It's cold start" when it's actually a warm/hot start regression.** Users describe all slow launches as "the app is slow to open," but ART/process reuse means a warm or hot start (process already alive, only Activity recreation) has a very different budget and cause than a true cold start (new process, `Application.onCreate()`, full class loading). Use Macrobenchmark's `StartupTimingMetric` with explicit `StartupMode.COLD`/`WARM`/`HOT` to separate these before proposing a fix.
- **Treating one profiler run as ground truth.** A single Perfetto trace or `framestats` sample can be dominated by an unrelated background task (a scheduled sync, another app, a system service). Confirm a jank or ANR pattern across at least two to three reproductions, or check Play Console's aggregated vitals, before committing to a root cause from one trace.
- **Fixing the symptom frame instead of the triggering allocation/call.** The dropped frame in a trace is often the *victim* (e.g., where a GC triggered by an allocation two frames earlier finally causes a pause), not the cause. Walk the trace backward from the janky frame to find what actually triggered the GC or blocking call.
