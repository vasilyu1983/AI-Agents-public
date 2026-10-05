---
name: software-ios-runtime-debugging
description: "Proves iOS build/install/launch truth and triages hangs, crashes, jank, memory kills, and stale builds. Use when simulator, bundle, or runtime performance state is in doubt."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Native iOS Runtime Debugging

Use this skill when the core problem is not app architecture or visual design, but runtime truth: did the current binary build, install, launch, and render on the intended simulator or device — and once that's proven, is the live complaint a hang, a crash, jank, a memory kill, or a launch-time regression?

This skill owns stale-build suspicion, simulator drift, malformed `.app` bundles, missing executables, XcodeGen resource packaging mistakes, and the proof loop required before trusting screenshots, UI behavior, or downstream API/auth debugging. It also owns classifying and diagnosing live runtime performance and stability complaints once that proof exists: hangs and watchdog kills, crash symbolication, jank against frame budgets, Jetsam/memory pressure, and launch-time measurement traps.

## Quick Reference

| Symptom | First Move | Notes |
|--------|------------|-------|
| Screenshot does not match source | Preserve repro, then replace/install and launch the known artifact | Reset or uninstall only after preserving evidence and isolating the suspected layer |
| Tool cannot read a simulator screenshot temp path | Re-capture from the current simulator | Temp screenshot files expire or move. Do not treat a missing temp path as invalidating the user's visible report |
| Install says app is missing executable | Inspect built `.app` bundle | Verify `Info.plist` and executable path before touching Swift |
| Simulator behaves inconsistently | Prove destination, boot, install, launch state | Do not debate UI until runtime truth exists |
| Auth appears to succeed but next screen is unauthenticated | Inspect token persistence and auth propagation after fresh launch | Do not redesign UI first |
| Push works on Xcode build but fails on TestFlight | Inspect archived entitlements and newest backend device row | Wrong APNs environment is more likely than feature-code regression |
| APNs returns `BadDeviceToken` for older installs | Check device-row environment and staleness first | Often stale tokens or env mismatch, not a current-device blocker |
| Push tap opens to black screen, freeze, or `_performBlockAfterCATransactionCommitSynchronizes` | Start at [`references/swift-concurrency-crash-triage.md`](references/swift-concurrency-crash-triage.md); web-search the exact symbol before any code review | Root-cause candidates include a nonisolated delegate or completion callback mutating main-actor UI state, nested actor hops, or SceneKit updates. `Task { }` inherits the actor context where its closure is formed; inspect that creation context rather than assuming every task is detached. Separate transport proof from push-open proof |
| UITest env var is present but the wrong screen is captured | Verify branch execution and a screen-specific accessibility marker | Process env alone is not runtime proof |
| Route state changes but the destination never appears | Prefer a direct presentation hook for isolated proof | `NavigationStack` state is not the same as a visible screen |
| "cannot find X in scope" after adding new files | XcodeGen project not regenerated | Regenerate: `scripts/generate-xcodeproj.sh` or `xcodegen generate` |
| "cannot find X in scope" in a `.pbxproj` project after adding files | New file not added to target membership | Add the file to the target before touching Swift feature code |
| CoreSimulatorService "Connection refused" | Simulator service crashed | Use `generic/platform=iOS` destination instead of simulator; or restart Simulator.app |
| DerivedData write failure / sandbox error | Check the denied path and active toolchain | Use a writable project-specific DerivedData path; if platform services need wider access, use the runtime's scoped approval mechanism or Xcode.app |
| Swift "failed to produce diagnostic" | Type inference overload in complex ViewBuilder | Simplify: inline optional views, remove `AnyView`, split large computed properties |
| "Copy Bundle Resources contains entitlements" warning | Check whether the entitlements file was added as a bundled resource | Keep entitlements in signing configuration only; exclude them from copied app resources |
| **Background `xcodebuild … \| tail -N` output file stays 0 bytes until exit** | Looks like a stall; not one | `tail` emits only when its input stream closes. In background execution, the output file appears empty for the entire build run, which looks stuck but is actually normal. Alternatives: `2>&1 \| tee output.log` for live progress, or drop `tail` entirely and accept the full output. The `tail -N` recipe trades live visibility for clean final output — pick based on whether you need progress signals during the run |
| `Ld failed` / missing file after project generation | Check generated paths and target membership, then try an isolated clean build | Cache drift is a hypothesis; a missing source or resource remains missing after a cache reset |
| App terminates with `0x8badf00d` / `WATCHDOG` reason | Not a code crash — a callback (scene-create, background task) failed to return in time | Read the reason string for which subsystem timed out; treat as a hang that ran out the clock. See [references/runtime-performance-triage.md](references/runtime-performance-triage.md#hangs-and-watchdog-terminations) |
| Process still alive but input goes unanswered | Hang, not crash — no crash log will exist | Capture a main-thread backtrace via the Hangs instrument or lldb `bt all`; do not search for a nonexistent crash report |
| Scrolling or animation stutters but the app stays responsive | Jank — a missed frame budget, not a hang | Profile with Hitches/SwiftUI instrument, not the Hangs template. 60 Hz = 16.67 ms/frame, ProMotion 120 Hz = 8.33 ms/frame (adaptive; measure the target device's active refresh rate) |
| App disappears with no crash log after memory growth | Suspect a Jetsam kill | Confirm via a jetsam event report or the memory diagnostic available in the target SDK; do not assume a normal crash was swallowed. Apple publishes no official per-device memory-limit table — treat any specific MB figure as empirical |
| "Main thread blocked" in a trace, but the code path looks fine | Possible priority inversion, not main-thread overwork | Check the QoS of every thread in the backtrace before moving work off main; a low-priority thread holding a lock the main thread needs looks identical to a slow main-thread task |
| Launch-time regression only shows up in some samples | Prewarming skew | The OS may prewarm the process before the user taps the icon — loads linked libraries, then suspends before any app code runs. No documented API detects it. Treat a single launch sample as unverified — use MetricKit's launch-type-bucketed metrics or a large field sample |
| MetricKit payload never arrives during local testing | Distinguish field delivery from simulated payloads | On a physical device, Xcode's Debug > Simulate MetricKit Payloads tests report handling with sample data; it does not measure the app's performance |

## When to Use This Skill

Use this skill to:

- Prove the current binary builds, installs, and launches on the intended target
- Diagnose stale installs or stale screenshots in simulator-driven workflows
- Inspect built `.app` bundles when installation fails
- Debug simulator boot, shutdown, destination, and launch-state drift
- Investigate XcodeGen, resource packaging, bundle executable, or `Info.plist` path problems
- Establish runtime truth before routing to feature implementation, design, or test skills
- Classify a live complaint as a hang, a crash, jank, a memory (Jetsam) kill, or a launch-time regression before choosing a fix
- Read Instruments, MetricKit, or crash-symbolication output and judge whether a lab fix will actually move field metrics

## Core Workflow

1. Discover the project entrypoint: workspace or project, scheme, configuration, destination, and bundle ID.
2. Check the callable tool inventory against Agent Tool Selection; record the selected Xcode/toolchain and destination.
3. Build the app with the simplest reproducible command.
4. Inspect the built `.app`:
   verify `Info.plist`, executable name, and expected bundle contents.
5. Preserve the reproduction before resetting anything: record launch arguments, deep link, account, local data dependency, installed bundle version/signature, logs, and the visible state.
6. Install or upgrade the freshly built bundle while preserving its data container where the target supports that path. Uninstall/reset only when replacement fails, signing differs, migration/state corruption is the suspected layer, or the repro evidence has already been captured.
7. Launch the freshly installed app and capture proof:
   screenshot, UI hierarchy, launch logs, and a target-screen-specific marker when isolating a route.
8. Only after the app is freshly running, debug feature behavior, design, auth, or API issues.
   - For push issues, also prove the binary origin (Xcode debug vs TestFlight), the signed APNs entitlement on archive builds, and the newest backend device-row environment before chasing app logic.
- Treat transport proof and push-open proof as separate gates: APNs success and a visible banner do not prove tapping is safe.
9. Route onward:
   - visual hierarchy and HIG review -> [software-ios-design](../software-ios-design/SKILL.md)
   - native feature or architecture work -> [software-ios-native](../software-ios-native/SKILL.md)
   - test execution and `xcresult` triage -> [qa-testing-ios](../qa-testing-ios/SKILL.md)

## Runtime Proof Loop

- Prefer one bounded loop:
  discover -> build -> inspect bundle -> preserve repro -> replace/install -> launch -> capture evidence
- Escalate separately to a clean build, container reset, or uninstall. Record which reset changes the symptom; that difference distinguishes build drift from persisted-state or migration defects.
- If any step fails, stop there and fix that layer before moving deeper.
- Do not trust screenshots from a simulator session that has not been tied to the current build.
- Do not trust “build succeeded” on its own; install and launch proof still matter.
- Do not stop on an unreadable temp screenshot path. Re-capture a screenshot, inspect the UI tree, or use the user's exact visible symptom to drive a focused source-level check.
- Verify isolated launch hooks at three levels: the env reached the process, the intended app branch executed, and the target screen is present through a screen-specific accessibility marker.
- If a screenshot or UI tree contradicts the expected launch hook, inspect only the named non-secret launch-hook flag values through a scoped app diagnostic and then verify the marker before trusting the capture.

## Agent Tool Selection

Choose the smallest callable tool that covers the evidence needed. A documented tool is not proof that this runtime exposes it.

| Need | Default | Capability check / fallback |
|---|---|---|
| Build through an open Xcode project | Apple's Xcode MCP bridge | Check Xcode Intelligence access and the connected tool inventory; Apple documents `xcrun mcpbridge`. Use CLI if the bridge is unavailable. [Apple guide](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode) |
| Simulator build/install/launch/log/UI loop | Existing XcodeBuildMCP or MobileBuildMCP connection | Upstream is [MobileBuildMCP](https://github.com/getsentry/MobileBuildMCP); inspect the installed tool inventory and configuration rather than assume old tool names still work. Fall back to `xcodebuild` + `simctl`. |
| Paused-process stack, variables, stepping | LLDB or its MCP interface | [LLVM's `lldb-mcp`](https://lldb.llvm.org/use/mcp.html) requires a compatible installed debugger; verify availability and a stopped process. MCP debugger output excludes the debuggee's stdout. |
| Physical-device install/launch/control | `xcrun devicectl` | Use `xcrun devicectl help` for the installed command surface and check device/signing state. It does not replace symbolication or Instruments. [Apple CLI reference](https://developer.apple.com/documentation/xcode/xcode-command-line-tool-reference) |
| Result bundle or performance trace | `xcresulttool` or `xctrace` | Read installed help for result/trace schemas; keep raw artifacts alongside filtered output. |

Project scaffolding, buildable folders, warnings policies, and Xcode Cloud setup belong to [software-ios-native](../software-ios-native/SKILL.md). Server auth, writes, and deployment behavior belong to [software-backend](../software-backend/SKILL.md); request/response contracts belong to [dev-api-design](../dev-api-design/SKILL.md).

## Stale-Build Heuristics

| Symptom | Suspect | Action |
|---|---|---|
| UI doesn't match current source | Stale install | Preserve repro; replace/install the verified bundle |
| App shows old screen after rebuild | Cached install | Inspect artifact and install logs; replace before reset |
| Build succeeded but app looks old | Stale DerivedData or incremental build error | Check install logs; do not keep editing feature code |
| Simulator already running, UI state surprising | Previous simulator session | Re-prove install and launch before reasoning about app state |
| Push works on Xcode build, fails on TestFlight | APNs environment mismatch | Local → `sandbox`; TestFlight / App Store → `production`; verify per-device row |
| Transport works, app freezes or crashes on push tap | Notification-open path: delegate isolation, route staging, off-main mutation | Route to [swift-concurrency-crash-triage.md](references/swift-concurrency-crash-triage.md) |
| `dataCorrupted` + `<!DOCTYPE html>` response | API routing / auth bug | Log URL, curl it; do not conflate with push-open crashes |
| Route state updates but destination never appears | Presentation hook not reached | Use a direct presentation hook to prove the screen in isolation |
| Simulator unresponsive (CoreSimulatorService errors) | Simulator service crashed | Switch to `generic/platform=iOS` for compile-only verification |

See [references/stale-build-triage.md](references/stale-build-triage.md).

## Packaging and Bundle Health

- When installation fails, inspect the built `.app` bundle directly.
- Confirm:
  - `Info.plist` has expanded values, not unresolved placeholders
  - the executable exists at the path referenced by the bundle metadata
  - expected resources are copied as resources, not malformed folder references
- If the error mentions missing bundle executable, treat it as a packaging issue first.

See [references/xcodegen-resource-packaging.md](references/xcodegen-resource-packaging.md).

## Swift Concurrency Hop Rule

In a `@MainActor` context, code after an `await` resumes on the MainActor. Swift does not lose isolation across an `await` (SE-0338). Under the default settings, the awaited `nonisolated async` function itself runs off the main actor. If that function reaches main-actor state (possible through `@unchecked Sendable` or minimally checked code), that access is the bug; a missed hop back is not. Swift 6.2's approachable-concurrency setting, or the `NonisolatedNonsendingByDefault` upcoming feature (SE-0461), makes `nonisolated async` functions run on the caller's actor unless marked `@concurrent`. Check the project's build settings before reasoning about where a function runs. Crash patterns and fixes are in [references/swift-concurrency-crash-triage.md](references/swift-concurrency-crash-triage.md).

## Runtime Performance Triage

Once build/install/launch truth is established, a live complaint still needs to be classified before you touch code. Hang, watchdog kill, jank, Jetsam kill, and launch-time regression have different evidence and different fix ladders — do not default to "read the code" until the failure class has a name.

- Walk the triage order: terminated-with-crash-log → terminated-with-`0x8badf00d`/watchdog → alive-but-unresponsive (hang) → alive-and-responsive-but-stuttering (jank) → disappeared-with-no-crash-log (Jetsam) → slow-to-first-frame (launch).
- Watch for the two most common misdiagnoses: blaming "main thread blocked" when it's priority inversion on a lower-QoS thread holding a shared lock, and trusting a single launch-time sample that may have been prewarmed.
- Instruments, MetricKit, hang/watchdog thresholds, Jetsam behavior, frame-budget math, crash symbolication, LLDB workflows, thermal-state handling, and launch-time optimization are covered in depth in [references/runtime-performance-triage.md](references/runtime-performance-triage.md) — including which of these categories the Simulator cannot faithfully reproduce, and why lab evidence alone should never close out a field-facing performance fix.

## Archive And APNs Validation

- Validate the exact `.xcarchive` selected for upload before blaming runtime code. Avoid generic `find ... .app | tail -1` shortcuts when multiple archives or export folders may exist:

```bash
codesign -d --entitlements :- "$APP" 2>/dev/null
security cms -D -i "$APP/embedded.mobileprovision" | plutil -p - | grep -A2 aps-environment
```

- Pass condition for a TestFlight/App Store archive:
  - `aps-environment = production` in the archived app entitlements
  - `get-task-allow = false`
  - `aps-environment = production` in the embedded provisioning profile
- If `aps-environment = development` or `get-task-allow = true`, the archive is still development-signed. If those values are correct but validation fails, inspect generated plist metadata next.
- When push debugging crosses release channels, separate token-registration truth from transport truth. A common iOS/TestFlight failure is: many sandbox deliveries succeed, the only production delivery fails with `BadDeviceToken`, and the phone receives nothing. Treat that as a stale-registration or invalid-production-token problem first, not as proof that APNs transport or signing is generally broken.
- Preserve the device registration and failure response before resetting. Prove the installed build channel, current token registration, APNs environment, successful send, actual receipt, and push-open behavior separately. Route backend device-row lifecycle changes to software-backend; an app uninstall is a later diagnostic reset, not a default transport fix.

## XcodeGen and Project File Discovery

Generator specs and target membership cause install-time failures and "cannot find X in scope" errors that look like Swift bugs. Regenerate XcodeGen projects after adding files (`scripts/generate-xcodeproj.sh` or `xcodegen generate`), and add new files to the target in `.pbxproj`-managed projects. Details in [references/xcodegen-resource-packaging.md](references/xcodegen-resource-packaging.md#project-file-discovery).

## Route Elsewhere

- Use [software-ios-native](../software-ios-native/SKILL.md) once runtime truth is established and the task becomes feature implementation, rewrite planning, or SwiftUI architecture.
- Use [software-ios-design](../software-ios-design/SKILL.md) once the screen is confirmed to come from a fresh build and the task is visual hierarchy, typography, materials, or HIG compliance.
- Use [qa-testing-ios](../qa-testing-ios/SKILL.md) once the app is buildable and installable and the task becomes test execution, `xcresult`, destinations, or flake control.
- Use [software-mobile](../software-mobile/SKILL.md) for platform choice, Android, or cross-platform tradeoffs.

## Navigation

### References

| Resource | Purpose |
|----------|---------|
| [references/runtime-proof-loop.md](references/runtime-proof-loop.md) | Canonical build/install/launch verification loop |
| [references/stale-build-triage.md](references/stale-build-triage.md) | Heuristics for screenshots, stale installs, and simulator drift |
| [references/xcodegen-resource-packaging.md](references/xcodegen-resource-packaging.md) | XcodeGen and bundle-packaging failure patterns |
| [references/swift-concurrency-crash-triage.md](references/swift-concurrency-crash-triage.md) | Symptom-first triage for concurrency-rooted crashes and freezes |
| [references/runtime-performance-triage.md](references/runtime-performance-triage.md) | Hang/crash/jank/memory/launch triage tree, Instruments, MetricKit, Jetsam, frame budgets, thermal state |
| [data/sources.json](data/sources.json) | Primary Apple and XcodeBuildMCP sources |

### Templates

| Template | Purpose |
|----------|---------|
| [assets/template-ios-runtime-debug-request.md](assets/template-ios-runtime-debug-request.md) | Short request format for proof-first runtime debugging |

### Related Skills

| Skill | Purpose |
|-------|---------|
| [software-ios-native](../software-ios-native/SKILL.md) | Native iOS implementation and rewrites after runtime truth exists |
| [software-ios-design](../software-ios-design/SKILL.md) | Visual audits after fresh build/install/launch proof |
| [qa-testing-ios](../qa-testing-ios/SKILL.md) | XCTest, XCUITest, `xcresult`, and flake control after installability is proven |
| [software-mobile](../software-mobile/SKILL.md) | Mobile platform choice and cross-platform tradeoffs |

- Prefer Apple documentation for `xcodebuild`, `simctl`, and bundle structure behavior.
- Prefer upstream XcodeBuildMCP docs for tool names, CLI commands, and config keys.
- Treat repo-specific build, scheme, bundle ID, and generator behavior as local facts that must be discovered, not assumed.
- Instrument names, hardware-gated feature availability (e.g., Processor Trace chip requirements), and exact watchdog timings change across Xcode/iOS releases — re-verify against current Apple release notes rather than trusting a fixed number from this skill. Jetsam memory-limit figures are explicitly empirical, not Apple-published, and should be re-derived from device behavior (`os_proc_available_memory`, jetsam event reports), not hardcoded.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
