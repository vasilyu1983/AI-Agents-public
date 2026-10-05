# Runtime Performance Triage: Hangs, Crashes, Jank, Memory, Launch

## Table of Contents

- [Triage Decision Tree](#triage-decision-tree)
- [Common Misdiagnoses](#common-misdiagnoses)
- [Instruments](#instruments)
- [MetricKit](#metrickit)
- [Hangs and Watchdog Terminations](#hangs-and-watchdog-terminations)
- [Jetsam and Memory Limits](#jetsam-and-memory-limits)
- [Frame Budgets](#frame-budgets)
- [Crash Symbolication](#crash-symbolication)
- [LLDB Modern Workflows](#lldb-modern-workflows)
- [Thermal State](#thermal-state)
- [Launch-Time Optimization](#launch-time-optimization)
- [Field vs Lab Discipline](#field-vs-lab-discipline)
- [When Not to Trust the Simulator](#when-not-to-trust-the-simulator)

This reference assumes runtime truth (fresh build, install, launch) is already established via the [Runtime Proof Loop](runtime-proof-loop.md). It covers the next layer: classifying and diagnosing a live performance or stability complaint once you know the binary on screen is the one you think it is.

## Triage Decision Tree

Work through these questions in order. Do not skip to "read the code" before you know which failure class you are looking at — the fix ladder is different for each.

1. **Did the process actually terminate, and is there a crash log?**
   Yes with a real exception (`SIGABRT`, `EXC_BAD_ACCESS`, an uncaught Swift/ObjC exception) → this is a crash. Symbolicate and read the top user-code frame. See [Crash Symbolication](#crash-symbolication).
2. **Did it terminate with `EXC_CRASH` / `0x8badf00d` and a `WATCHDOG` reason?**
   This is not a code crash — it is the OS killing a process that failed to respond to a system callback in time (scene-create, background task expiration, `applicationDidEnterBackground` overrun). Treat it as a hang that ran out the clock, not a logic bug. See [Hangs and Watchdog Terminations](#hangs-and-watchdog-terminations).
3. **Is the process still alive, but input goes unanswered for a noticeable stretch?**
   That's a hang, not a crash — there is no crash log to chase. Capture a main-thread backtrace (Instruments Hangs template, or attach lldb and `bt` while it's stuck). See [Hangs and Watchdog Terminations](#hangs-and-watchdog-terminations).
4. **Is the process alive and responsive, but scrolling/animation stutters?**
   That's jank — a missed [frame budget](#frame-budgets), not a hang. The main thread answered input; it just didn't finish enough work before the next frame deadline. Profile with the Hitches / SwiftUI Profiler template, not the Hangs template.
5. **Did the process disappear with no crash log at all, often after a period of memory growth?**
   Suspect a Jetsam (out-of-memory) kill. There is no stack trace by design — that's what distinguishes it from a crash. Confirm via a jetsam event report or a memory-termination diagnostic available in the target SDK, not by assuming a normal crash was "swallowed." See [Jetsam and Memory Limits](#jetsam-and-memory-limits).
6. **Is the complaint specifically about time-to-first-frame or time-to-interactive?**
   That's a launch-time problem, and it has its own measurement traps (prewarming) before you touch code. See [Launch-Time Optimization](#launch-time-optimization).

## Common Misdiagnoses

- **"Main thread is blocked" when it's actually priority inversion.** A high-priority (main-thread, user-interactive) task is waiting on a lock or resource held by a low-priority background-QoS task, and the low-priority task isn't getting scheduled time. A wall-clock trace shows the main thread "stuck," but the fix is not to move work off main — it's to fix the priority donation (raise the QoS of the blocking work, or avoid taking a lock shared with background QoS code from the main thread). Check the QoS of every thread in the backtrace, not just which thread shows the largest wall-clock gap.
- **Trusting a single cold-launch number when the process was prewarmed.** Since iOS 15, the system can prewarm your process in the background before the user taps the icon. Prewarming loads the libraries your app links against, then suspends the process without letting any of your application code run — no static initializers and no early setup actually execute during prewarm, so it skews *process-start-based* timers rather than pre-main work. It measures much faster than a genuinely cold launch because part of the OS-side setup is already done. There is no documented public API to detect prewarming; Apple DTS has described an `ActivePrewarm` environment variable set on prewarmed launches, but it is undocumented and unsupported — treat any use of it as a stopgap, not a stable contract. Treat any single launch-time sample as unverified until you have enough samples (ideally from MetricKit's launch metrics, which the OS buckets by launch type) to see the distribution, not a point estimate. Measure from `main`/first-frame using Organizer's launch-type buckets rather than trying to infer prewarm state client-side.
- **Reading the Allocations instrument as proof of "no leak."** Allocations has a known gap: it can under-report reference-counting traffic for native Swift types, so a flat Allocations graph does not rule out a retain cycle. Cross-check with Leaks plus a `vmmap`/`heap` snapshot before clearing a memory-growth suspicion. (See also `references/swift-concurrency-crash-triage.md` → Diagnostic tool ladder → Console output, which flags the same Allocations caveat.)
- **Confusing a third-party SDK's "app hang" threshold with Apple's system default.** Apple's own tooling (Instruments Hangs template, MetricKit `MXHangDiagnostic`) reports on main-run-loop unresponsiveness starting around 250 ms by default. Crash-reporting SDKs (e.g., Sentry's Cocoa SDK) define their own separately configurable "app hang" thresholds, commonly defaulting to around 2 seconds, to avoid over-reporting minor stalls. If a hang rate looks inconsistent across two dashboards, confirm both are using the same threshold before concluding one tool is wrong.
- **Debugging a memory, thermal, or precise-timing issue purely in Simulator.** See [When Not to Trust the Simulator](#when-not-to-trust-the-simulator).

## Instruments

Instruments received a significant overhaul around Xcode 26, reorganizing several templates around SwiftUI and CPU-level tracing. Treat instrument names and exact template contents as something to re-verify against the release notes for the Xcode version actually in use — Apple has renamed and regrouped instruments across recent major versions.

- **SwiftUI Profiler template** — bundles Update Groups (when SwiftUI is doing work), View Body / View Properties (what views were created/changed and why), Core Animation Commits, and Time Profiler into one recording, replacing what used to require several separate instruments.
- **Hangs** — reports main-run-loop unresponsiveness; default reporting threshold is ~250 ms, configurable lower for stricter budgets.
- **Hitches / Animation Hitches** — tracks short UI stalls that don't rise to a full hang but still miss a frame deadline; this is the tool for jank, not Hangs.
- **Time Profiler** — general-purpose sampling CPU profiler; still the right first stop when you don't yet know what category of problem you have.
- **Processor Trace** — a hardware-level instruction/branch trace with very low overhead, giving a near-complete execution record rather than statistical samples. **Hardware-gated**: it requires the CPU's trace hardware, available on Apple silicon Macs and iPads with **M4 or later**, and iPhones with **A18-class silicon (iPhone 16 and later)**. It will not run on older Apple silicon or on Intel Macs — verify device/chip generation before planning a Processor Trace session, and re-confirm the exact chip cutoff against current Apple documentation, since Apple has extended hardware-gated Instruments features to new chip generations before without renaming the instrument.
- **Allocations / Leaks / VM Tracker** — memory instruments; see the Allocations under-reporting caveat above.
- **App Launch** — time-to-first-frame breakdown; cross-reference with the prewarming caveat before trusting a single sample.

Primary source: [WWDC26 session 268](https://developer.apple.com/videos/play/wwdc2026/268/) demonstrates the Release-build workflow: high CPU → Time Profiler; actor contention → Swift Concurrency; low CPU while blocked → System Trace. Compare baseline/fix runs over matching signpost intervals. Resolve template availability against the installed Xcode.

## MetricKit

MetricKit is Apple's on-device, privacy-preserving telemetry framework for real installs — it is field data, not lab data.

- **Legacy `MXMetricPayload` API** — aggregated performance metrics (CPU, memory, disk, network, launch time, hang time, animation-hitch rate, battery) delivered roughly once per day at the system's discretion. Treat the delivery cadence as approximate; it is not a guaranteed fixed interval.
- **Legacy `MXDiagnosticPayload` API** — triggered diagnostics for crashes, hangs (`MXHangDiagnostic`), CPU exceptions, and disk-write exceptions, each carrying a symbolicatable call stack tree. Apple documents immediate diagnostic delivery from iOS 15, separate from daily metrics; an app that crashed must be running again to receive its callback.
- **Development exception:** on a physical device, Xcode's Debug > Simulate MetricKit Payloads delivers sample reports to exercise report handling. These are synthetic data, not measurements of the current Debug run. MetricKit does not deliver reports on simulated devices. [Apple monitoring guide](https://developer.apple.com/documentation/metrickit/monitoring-app-performance-with-metrickit).
- For field verification, collect real device reports from the deployed app and distinguish them from synthetic payloads. Do not infer delivery eligibility solely from a Debug/Release label; use the installed SDK's MetricKit guide and record the distribution channel.
- Select the API by deployment target: Apple's [MetricKit overview](https://developer.apple.com/documentation/metrickit) documents the iOS 27 boundary for `MetricManager` asynchronous sequences and state-aware reports; keep the older subscriber API where older OS support requires it. Resolve memory-diagnostic type names and availability against that SDK; do not assume `MXMemoryExceptionDiagnostic` exists.
- Because MetricKit payloads are aggregated and delayed by design, pair it with a real-time crash/hang reporter (Crashlytics, Sentry, or similar) for immediate alerting, and use MetricKit for the trustworthy field-wide baseline those SDKs' self-reported thresholds should be checked against.

## Hangs and Watchdog Terminations

- **Hang vs watchdog kill are different failure classes that share a root cause family.** A hang is a live, unresponsive process; a watchdog termination is the OS killing the process because a specific system callback (launch's scene-create, `applicationDidEnterBackground`, a background task expiration handler) didn't return in time.
- **`0x8BADF00D`** ("ate bad food") is Apple's exception code for watchdog terminations generally — it is not launch-specific. Always read the accompanying reason string (e.g., `WATCHDOG` + a subsystem name) to know which callback timed out.
- **Launch's scene-create watchdog** is commonly cited around ~20 seconds, but Apple does not publish a single fixed guaranteed number — the actual budget can vary with device load and iOS version. Treat any specific second-count for this watchdog as an empirical, not contractual, figure, and design for "as fast as possible" rather than "just under N seconds."
- **Instruments/MetricKit hang-reporting default is ~250 ms** of unresponsive main run loop — this is the number to use when talking about Apple's own hang detection. Do not conflate it with a third-party SDK's own configurable hang threshold (see [Common Misdiagnoses](#common-misdiagnoses)).
- Common root causes for both hangs and scene-create watchdog kills: synchronous network/disk I/O on launch, database migrations run on the main thread, blocking `.wait()`/`.result`-style calls on async work, and heavy JSON/model decoding before the first screen is shown. Defer all of this past first paint.
- Primary source: Apple's "Addressing watchdog terminations" and "Understanding hangs in your app" documentation.

## Jetsam and Memory Limits

- **Apple does not publish an official per-device-class memory limit table.** Any specific megabyte figure you see for a given iPhone model is a community-derived, empirical estimate from jetsam event report reverse-engineering — label it as such, expect it to drift across iOS versions and device generations, and never hardcode a number into product logic.
- The empirical shape holds directionally: limits scale with device RAM (roughly proportional, with older/entry-level devices getting a much smaller allowance than current Pro-tier devices), but exact figures are not something to treat as stable API contract.
- **The signal to build against is behavioral, not tabular**: `os_proc_available_memory()` for headroom, `didReceiveMemoryWarning` for soft pressure, plus jetsam event reports for memory terminations; use SDK-available MetricKit memory diagnostics as additional evidence. React to pressure signals rather than trying to stay under a guessed absolute ceiling.
- Jetsam kills produce **no crash log with a normal stack trace** — that absence, combined with prior memory growth in the same session, is itself the diagnostic signature. Don't spend time looking for a crash report that structurally does not exist for this failure mode.
- Primary source: Apple's "Identifying high-memory use with jetsam event reports" documentation.

## Frame Budgets

Re-derived from the display refresh rate, not looked up as a constant:

- **60 Hz (older/entry-tier iPhones, most iPads):** 1000 ms / 60 = 16.666... ms → **16.67 ms per frame**.
- **120 Hz (ProMotion, LTPO):** 1000 ms / 120 = 8.333... ms → **8.33 ms per frame**.
- **ProMotion is adaptive**, not fixed at 120 Hz — the display can scale down depending on content motion, so a jank complaint on a ProMotion device may actually be occurring at a lower instantaneous refresh rate. Check the actual refresh rate in the Hitches/Core Animation trace rather than assuming 120 Hz math applies to every frame, and do not cite a fixed low-end floor — read the measured rate from the trace.
- Resolve display capabilities for the exact target device and measure the active refresh rate; model names are not a frame-budget contract.

## Crash Symbolication

- Keep the `.xcarchive` and dSYMs from the shipped build. Locate missing symbols using [Apple's guide](https://developer.apple.com/documentation/xcode/locating-a-missing-debug-symbol-file); do not assume another build or a download can supply matching symbols.
- **UUID match is non-negotiable.** Every compiled binary carries a build UUID, and the dSYM must have the exact matching UUID or symbolication silently fails (or worse, produces wrong-looking-but-plausible symbols from a stale dSYM). Verify UUIDs with `dwarfdump --uuid` before trusting a symbolicated report.
- Prefer Xcode for full reports and `atos` for a known address with the correct image load address, architecture, binary, and matching dSYM. Follow [Apple's symbolication guide](https://developer.apple.com/documentation/xcode/adding-identifiable-symbol-names-to-a-crash-report); check the installed toolchain before relying on optional crash-report scripts.
- If you use a third-party crash reporter (Crashlytics, Sentry, etc.), confirm its dSYM upload step actually ran for the exact build that crashed — a missing or mismatched upload produces an unsymbolicated report that looks like a tooling failure rather than a missing-artifact problem.

## LLDB Modern Workflows

- **Core commands**: `bt` (current thread backtrace), `bt all` (every thread — use this first when a hang or crash could be on a background/Task thread rather than main), `image lookup --address <addr>` (resolve a raw crash-log address once attached to the matching binary), `watchpoint set variable <name>` (break on a specific memory write).
- **Swift Concurrency-aware backtraces**: modern lldb can show Task-relative backtraces so you can tell whether a paused thread is really "main thread" or a Task running on the cooperative thread pool — check the debugger's thread/queue label before assuming a crash inside SwiftUI/UIKit machinery means main-thread code is at fault (see `references/swift-concurrency-crash-triage.md` for the exact failure family this catches).
- **Exception breakpoints**: set an Objective-C/Swift error exception breakpoint (Xcode Breakpoint Navigator → + → Exception Breakpoint) so uncaught exceptions pause at the throw site instead of unwinding to an opaque top-level handler.
- **`swift-inspect`** is a separate command-line tool (ships with the Swift toolchain, not lldb itself) for inspecting a *live* Swift process's heap and concurrency state out-of-process — useful for retain-cycle and actor-state inspection without attaching a full debugger session. Its concurrency-inspection support is more mature on Apple platforms than on other supported platforms; verify current capability against the Swift.org toolchain docs for the toolchain version in use, since platform parity has been uneven.

## Thermal State

- `ProcessInfo.thermalState` reports one of four coarse states: `.nominal`, `.fair`, `.serious`, `.critical`. `ProcessInfo.thermalStateDidChangeNotification` fires on transitions.
- This is a long-stable API (available since iOS 11) — the judgment call is behavioral, not API-currency: degrade gracefully (reduce frame rate, pause speculative background work, lower render quality) at `.serious`, and cut non-essential work aggressively at `.critical`. Don't wait for `.critical` to start responding; by then the user has already noticed.
- **The Simulator cannot reproduce real thermal throttling** — it reports the host Mac's thermal state, not a modeled device state, so thermal-adaptive code paths must be validated on a physical device.

## Launch-Time Optimization

- Profile the target OS's actual loader and pre-main work before applying older dyld advice; use the launch trace to decide whether linking or app initialization dominates.
- **Mergeable libraries** (Xcode 15+, `MERGED_BINARY_TYPE` build setting): let a set of dynamic frameworks be statically merged into the app binary for Release builds while keeping normal dynamic linking for Debug builds, aiming for static-linking launch speed without giving up dynamic-framework build times during development. Real-world gains are inconsistent — the benefit is proportional to how many dynamically-linked frameworks the app actually loads at launch, and adoption is still often described as "a reasonable default when you haven't otherwise optimized your dependency graph," not a guaranteed fixed-percentage win. Benchmark before and after on-device, the same way you would for any other build-setting change.
- **Prewarming realities**: since iOS 15, the system may prewarm your process ahead of a user tap — this loads your app's linked libraries and then suspends the process before any of your code runs; no app code executes during prewarm. There is no documented public API to detect prewarming (the undocumented `ActivePrewarm` env var is a stopgap signal, not a stable contract), and this remains an open, acknowledged measurement problem for client-side launch-time instrumentation. Any launch-time regression investigation must first establish whether the compared samples are cold, warm, or prewarmed launches — comparing across launch types will manufacture a "regression" or "fix" out of noise.
- Practical guidance: prefer MetricKit's OS-bucketed launch metrics (which classify launch type) or a large TestFlight/production sample over a handful of Xcode Organizer runs on a tethered dev device, and never treat a Simulator launch-time number as representative of device performance.

## Field vs Lab Discipline

- **Lab measurements** (Instruments/Xcode Organizer on a tethered dev device) run under artificial conditions: often plugged into power (no battery-saving throttling), on a newer/higher-spec device than most of the install base, without real background app contention, and without real-world thermal history.
- **Field measurements** (MetricKit payloads, App Store Connect's aggregated power-and-performance metrics, production crash-reporter dashboards) reflect the actual device mix, real prewarming behavior, real background contention, and real thermal soak.
- **Do not declare a performance fix "done" from lab evidence alone.** A fix that looks clean on a tethered iPhone Pro can fail to move the field hang rate or Jetsam rate at all if the real driver is thermal throttling or memory pressure specific to older/entry-tier devices that never show up in a dev's device drawer. Cross-check the lab fix against field metrics after it ships before closing the investigation.

## When Not to Trust the Simulator

The Simulator shares the host Mac's CPU, memory, and thermal management — it is not a scaled-down device, it is a different machine. Treat these categories as **device-only** verification:

- Thermal state and thermal-throttling behavior (Simulator reports the Mac's thermal state, not a modeled device state).
- Absolute memory ceilings and Jetsam behavior (Simulator memory limits are the host Mac's, not any iOS device's).
- Precise launch-time, frame-budget, or CPU-bound performance numbers (Simulator CPU/GPU characteristics do not match any specific iOS device, and vary with whatever else is running on the host Mac).
- MetricKit payloads entirely (MetricKit does not deliver in Simulator at all — see [MetricKit](#metrickit)).
- APNs push delivery and most background-execution scheduling realism (covered in the existing stale-build/APNs guidance in this skill's `SKILL.md`).

The Simulator remains the right tool for UI logic, layout, and functional reproduction — just not for anything in this file's title.
