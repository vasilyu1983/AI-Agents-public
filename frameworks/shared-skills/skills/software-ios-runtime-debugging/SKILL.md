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
| Screenshot does not match source | Uninstall -> install -> launch | Assume stale app first |
| Tool cannot read a simulator screenshot temp path | Re-capture from the current simulator | Temp screenshot files expire or move. Do not treat a missing temp path as invalidating the user's visible report |
| Install says app is missing executable | Inspect built `.app` bundle | Verify `Info.plist` and executable path before touching Swift |
| Simulator behaves inconsistently | Prove destination, boot, install, launch state | Do not debate UI until runtime truth exists |
| XcodeBuildMCP is unavailable | Fall back to `xcodebuild`, `simctl`, `xcresulttool` | Switch immediately |
| Auth appears to succeed but next screen is unauthenticated | Inspect token persistence and auth propagation after fresh launch | Do not redesign UI first |
| Push works on Xcode build but fails on TestFlight | Inspect archived entitlements and newest backend device row | Wrong APNs environment is more likely than feature-code regression |
| APNs returns `BadDeviceToken` for older installs | Check device-row environment and staleness first | Often stale tokens or env mismatch, not a current-device blocker |
| Push tap opens to black screen, freeze, or `_performBlockAfterCATransactionCommitSynchronizes` | Start at [`references/swift-concurrency-crash-triage.md`](references/swift-concurrency-crash-triage.md); web-search the exact symbol before any code review | Known root cause family: `nonisolated async` UN delegate + nested `MainActor.run`, bare `Task { }` in `@MainActor` class, `actor → @MainActor` round-trip, `@Sendable async` closure, or SCNView `updateUIView` scene reassign. Separate transport proof from push-open proof: if APNs accepted delivery and the banner appeared, the bug is app-side |
| App stuck on a stale binary after `⌘R` | Delete DerivedData + delete app from device + reopen Xcode + reinstall | Xcode incremental build sometimes fails to detect actor isolation changes and reuses cached object files. Verify the fresh binary is on the device with the DEBUG marker print pattern (temporary `print("[<class>] build marker — <date>")` in a class `init`). See [`references/swift-concurrency-crash-triage.md` → "iOS app builds fine in terminal but Xcode shows compile errors, or device runs old binary"](references/swift-concurrency-crash-triage.md#symptom-ios-app-builds-fine-in-terminal-but-xcode-shows-compile-errors-or-device-runs-old-binary) |
| Cold-start push tap re-crashes on every relaunch | Delete + reinstall to clear `pendingRoutePath` in UserDefaults | A prior crashed launch staged a route in UserDefaults that the next cold launch tries to consume and re-crashes on before recovery. Primary bug is higher up (one of the Swift Concurrency patterns); this is the persistent secondary symptom. See [`references/swift-concurrency-crash-triage.md` → "app freezes/black-screens on push tap AND persists across cold relaunches"](references/swift-concurrency-crash-triage.md#symptom-app-freezesblack-screens-on-push-tap-and-persists-across-cold-relaunches) |
| UITest env var is present but the wrong screen is captured | Verify branch execution and a screen-specific accessibility marker | Process env alone is not runtime proof |
| Route state changes but the destination never appears | Prefer a direct presentation hook for isolated proof | `NavigationStack` state is not the same as a visible screen |
| "cannot find X in scope" after adding new files | XcodeGen project not regenerated | Regenerate: `scripts/generate-xcodeproj.sh` or `xcodegen generate` |
| "cannot find X in scope" in a `.pbxproj` project after adding files | New file not added to target membership | Add the file to the target before touching Swift feature code |
| CoreSimulatorService "Connection refused" | Simulator service crashed | Use `generic/platform=iOS` destination instead of simulator; or restart Simulator.app |
| DerivedData write failure / sandbox error | Build sandbox restrictions | Use `dangerouslyDisableSandbox: true` for xcodebuild, or build from Xcode.app |
| Canvas view renders empty on cold start | `animatedProgress` starts at 0, `.onAppear` fires before data loads | Start progress at 1 or trigger animation on data arrival |
| Swift "failed to produce diagnostic" | Type inference overload in complex ViewBuilder | Simplify: inline optional views, remove `AnyView`, split large computed properties |
| 401 from a backend route with a valid JWT | Check whether the route or middleware defaults to cookie or session auth | Explicitly enable bearer or JWT auth for that route, and keep privileged server clients behind the server boundary |
| 404 with the correct endpoint name | Inspect base URL and route-prefix composition before changing client code | Double-prefixed path segments such as `/api/api/...` and environment-specific base URLs are common culprits |
| PATCH or UPDATE returns 200 but no data changes for a first-time record | Check whether the write path assumes the row already exists | Use explicit insert-or-update (`upsert`) or create-on-miss behavior when the domain allows it |
| "Copy Bundle Resources contains entitlements" warning | Check whether the entitlements file was added as a bundled resource | Keep entitlements in signing configuration only; exclude them from copied app resources |
| **Background `xcodebuild … \| tail -N` output file stays 0 bytes until exit** | Looks like a stall; not one | `tail` emits only when its input stream closes. Combined with `run_in_background`, the output file appears empty for the entire 3–8 minute xcodebuild run, which looks stuck but is actually normal. Alternatives: `2>&1 \| tee output.log` for live progress, or drop `tail` entirely and accept the full output. The `tail -N` recipe trades live visibility for clean final output — pick based on whether you need progress signals during the run |
| **Simulator boot + install takes 2–5 min before first test output** | First xcodebuild output appears ~90–120s after start | Not a stall. The sequence is: compile → `xcodebuild` starts → simulator boot → install `.app` → TEST HOST launch → first `Test Case '…'` line. During this window the output file may be 0 bytes or contain only build headers. Wait for the background Bash task completion notification rather than polling |
| **API returns English on a localized screen even after locale-picker change** | Stored profile locale wins over explicit request locale | Request-locale priority should be explicit override (`?locale=` or equivalent) > `Accept-Language` header > stored profile. If the priority is inverted, localized clients can get cached content under the wrong locale contract |
| `EXC_BREAKPOINT` in `LocalizationStore.resolvedTemplate` / `LocalizationStore.text` | Inspect generated locale catalogs and their source generator | This is usually a missing-key assertion in the app bundle, not a SwiftUI layout or simulator problem. Patch the durable locale source, regenerate, and run key coverage before continuing UI work |
| **Raw test output too long to skim** | `xcodebuild test` emits ~10k-50k lines for a full run | Pipe through `xcbeautify` for design-review loops, or use `-quiet` + trailing `\| tail -200` for the final summary. For background runs where you want the pass/fail gate only, `grep -E "(TEST SUCCEEDED\|TEST FAILED\|Executed.*tests)"` gives a one-line outcome |
| **Xcode Cloud build fails with "The file X couldn't be opened" for a committed-looking file** | Check `git ls-files` for the path, not just `ls` | Classic "works on my machine" failure mode: a gitignored folder contains *some* tracked files (added pre-gitignore) and *some* untracked generated files. Local builds regenerate the missing file; Xcode Cloud clones only what is actually committed. Fix with `git add -f <path>`; verify no new file added to the folder is ever untracked |
| **Local `Ld failed` + "file couldn't be opened" immediately after `xcodegen`** | Delete `~/Library/Developer/Xcode/DerivedData/<project>-*`, not just `xcodebuild clean` | XcodeGen reshuffles file-reference UUIDs in `project.pbxproj`. DerivedData's build manifest is keyed by those UUIDs, so the cached build plan dangles. `xcodebuild clean` does not purge DerivedData; a project's repo-level `scripts/clean-ios.sh` typically does both |
| **Xcode Cloud `xcodebuild` exits with 65, no clear error in the summary view** | Expand the "Building project …" row; exit 65 is Apple's generic compile/link failure code | Usual culprits (in order of frequency on Xcode Cloud): missing generated file that the pbxproj references (Info.plist, manifest.json, locale JSON), App ID capability missing for an entitlement declared in `.entitlements` (Push, Sign in with Apple, Associated Domains), no team selected in the Xcode Cloud workflow, provisioning profile lookup failed. The one-line summary is always "non-zero exit code 65" — root cause only appears in the nested log |
| **Xcode Cloud ci_post_clone.sh not taking effect** | Verify path, permissions, and that the step ran | Must be at `ci_scripts/ci_post_clone.sh` (exactly — convention-based, no configuration). Must be `chmod +x`. Must exit 0. Its log appears under the **Post-Clone** step in the Xcode Cloud build log; if you see "Post-Clone script not found at ci_scripts/ci_post_clone.sh" the hook is not recognised. Same convention for `ci_pre_xcodebuild.sh` and `ci_post_xcodebuild.sh` |
| **Xcode Cloud build needs a sibling repo that doesn't exist on CI** | Don't try to clone it inside ci_post_clone; commit the generated output instead | Xcode Cloud clones only one repo into `/Volumes/workspace/repository`. Scripts that `cd ../<sibling>/<path>` will fail because the sibling is absent. Commit the exported artefacts (locale JSONs, manifests, generated bundles) into the building repo, even if the build step is gitignored locally. Prefer `git add -f` over relaxing the ignore rule so new untracked files don't silently regress |
| App terminates with `0x8badf00d` / `WATCHDOG` reason | Not a code crash — a callback (scene-create, background task) failed to return in time | Read the reason string for which subsystem timed out; treat as a hang that ran out the clock. See [references/runtime-performance-triage.md](references/runtime-performance-triage.md#hangs-and-watchdog-terminations) |
| Process still alive but input goes unanswered | Hang, not crash — no crash log will exist | Capture a main-thread backtrace via the Hangs instrument or lldb `bt all`; do not search for a nonexistent crash report |
| Scrolling or animation stutters but the app stays responsive | Jank — a missed frame budget, not a hang | Profile with Hitches/SwiftUI Profiler, not the Hangs template. 60 Hz = 16.67 ms/frame, ProMotion 120 Hz = 8.33 ms/frame (adaptive, not fixed) |
| App disappears with no crash log after memory growth | Suspect a Jetsam kill | Confirm via `MXMemoryExceptionDiagnostic` or a jetsam event report; do not assume a normal crash was swallowed. Apple publishes no official per-device memory-limit table — treat any specific MB figure as empirical |
| "Main thread blocked" in a trace, but the code path looks fine | Possible priority inversion, not main-thread overwork | Check the QoS of every thread in the backtrace before moving work off main; a low-priority thread holding a lock the main thread needs looks identical to a slow main-thread task |
| Launch-time regression only shows up in some samples | Prewarming skew | The OS may prewarm the process before the user taps the icon; there is still no supported API to detect or opt out of it. Treat a single launch sample as unverified — use MetricKit's launch-type-bucketed metrics or a large field sample |
| MetricKit payload never arrives during local testing | Expected — MetricKit only reports from App Store/TestFlight builds | It does not fire in Simulator or local Debug builds; ship to TestFlight before relying on it for verification |

## When to Use This Skill

Use this skill to:

- Prove a fresh uninstall/install/launch loop for a native iOS app
- Diagnose stale installs or stale screenshots in simulator-driven workflows
- Inspect built `.app` bundles when installation fails
- Debug simulator boot, shutdown, destination, and launch-state drift
- Investigate XcodeGen, resource packaging, bundle executable, or `Info.plist` path problems
- Establish runtime truth before routing to feature implementation, design, or test skills
- Classify a live complaint as a hang, a crash, jank, a memory (Jetsam) kill, or a launch-time regression before choosing a fix
- Read Instruments, MetricKit, or crash-symbolication output and judge whether a lab fix will actually move field metrics

## Core Workflow

1. Discover the project entrypoint: workspace or project, scheme, configuration, destination, and bundle ID.
2. Check tool reality:
   use XcodeBuildMCP only if it is actually callable in the current runtime.
3. Build the app with the simplest reproducible command.
4. Inspect the built `.app`:
   verify `Info.plist`, executable name, and expected bundle contents.
5. Remove stale installs:
   uninstall the app from the target simulator or device.
6. Install the freshly built bundle.
7. Launch the freshly installed app and capture proof:
   screenshot, UI hierarchy, launch logs, and a target-screen-specific marker when isolating a route.
8. Only after the app is freshly running, debug feature behavior, design, auth, or API issues.
   - For push issues, also prove the binary origin (Xcode debug vs TestFlight), the signed APNs entitlement on archive builds, and the newest backend device-row environment before chasing app logic.
- Treat transport proof and push-open proof as separate gates: APNs success and a visible banner do not prove tapping is safe.
9. Route onward:
   - visual hierarchy and HIG review -> [software-ios-design](../software-ios-design/SKILL.md)
   - native feature or architecture work -> [software-ios-native](../software-ios-native/SKILL.md)
   - test execution and `xcresult` triage -> [qa-testing-ios](../qa-testing-ios/SKILL.md)

## ASCII Flow

```text
iOS runtime failure
  -> Capture exact Xcode, iOS, device, build, repro, and logs
  -> Prove clean build, install, launch, and current binary
  -> Classify: crash, hang, UI, concurrency, persistence, network, or release
  -> Inspect debugger, logs, Instruments, and screenshot evidence
  -> Patch the smallest failing path
  -> Rerun same repro and preserve before/after proof
```

## Runtime Proof Loop

- Prefer one bounded loop:
  discover -> build -> inspect bundle -> uninstall -> install -> launch -> capture evidence
- If any step fails, stop there and fix that layer before moving deeper.
- Do not trust screenshots from a simulator session that has not been tied to the current build.
- Do not trust “build succeeded” on its own; install and launch proof still matter.
- Do not stop on an unreadable temp screenshot path. Re-capture a screenshot, inspect the UI tree, or use the user's exact visible symptom to drive a focused source-level check.
- Verify isolated launch hooks at three levels: the env reached the process, the intended app branch executed, and the target screen is present through a screen-specific accessibility marker.
- If a screenshot or UI tree contradicts the expected launch hook, inspect the process env (`ps eww`) and then verify the marker before trusting the capture.

## Agent-Friendly Scaffold (Preventative)

Most stale-build, "cannot find X in scope", and unparseable-test-output symptoms in this skill are downstream of an Xcode project that was never set up for agents. The AppCreator pattern (Paul Solt, @PaulSolt) is the canonical recipe for scaffolding new iOS projects so agents stop generating those symptoms in the first place.

- **Pattern:** ship four properties together; each one breaks if removed.
  1. **Buildable folders** — agents add `.swift` files by writing to disk; the project picks them up without `pbxproj` regeneration.
  2. **Warnings-as-errors** — surfaces deprecated APIs during the agent's own build/fix loop instead of at code review.
  3. **`Makefile` as the single entrypoint** — `make build`, `make run`, `make test`. Agents do not need to learn `xcodebuild` flag combinations per project.
  4. **`xcbeautify`** wrapping every `xcodebuild` invocation — output stays parseable; agent does not choke on the 10–50k line wall.
- **Anti-pattern:** any one of these alone. Buildable folders without warnings-as-errors lets the agent ship deprecated code. `xcbeautify` without a `Makefile` keeps the flag-juggling problem. A `Makefile` over a non-buildable-folder project means every new file still needs `xcodegen` or `pbxproj` surgery.
- **Recipe (existing repo):** add `Makefile` first (wrap whatever build command already works) → wire `xcbeautify` into that target → switch project to buildable folders → flip warnings-as-errors last (it will fail until earlier deprecations are cleaned up). Source: https://super-easy-apps.kit.com/app-creator

For diagnostic patterns when the project is already mis-scaffolded, see the Quick Reference rows on `xcodegen` regeneration, target membership, and `xcbeautify`/`-quiet` output filtering.

## Stale-Build Heuristics

| Symptom | Suspect | Action |
|---|---|---|
| UI doesn't match current source | Stale install | Remove installed app; reinstall fresh build |
| App shows old screen after rebuild | Cached install | Remove + reinstall; inspect install logs |
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

## Runtime Performance Triage

Once build/install/launch truth is established, a live complaint still needs to be classified before you touch code. Hang, watchdog kill, jank, Jetsam kill, and launch-time regression have different evidence and different fix ladders — do not default to "read the code" until the failure class has a name.

- Walk the triage order: terminated-with-crash-log → terminated-with-`0x8badf00d`/watchdog → alive-but-unresponsive (hang) → alive-and-responsive-but-stuttering (jank) → disappeared-with-no-crash-log (Jetsam) → slow-to-first-frame (launch).
- Watch for the two most common misdiagnoses: blaming "main thread blocked" when it's priority inversion on a lower-QoS thread holding a shared lock, and trusting a single launch-time sample that may have been prewarmed.
- Instruments (Xcode 26-era), MetricKit, hang/watchdog thresholds, Jetsam behavior, frame-budget math, crash symbolication, LLDB workflows, thermal-state handling, and launch-time optimization are covered in depth in [references/runtime-performance-triage.md](references/runtime-performance-triage.md) — including which of these categories the Simulator cannot faithfully reproduce, and why lab evidence alone should never close out a field-facing performance fix.

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
- Recovery sequence for mixed sandbox/production device state:
  1. Deactivate stale iOS device rows for the affected user.
  2. Uninstall local/debug builds and the TestFlight build.
  3. Reboot the physical iPhone.
  4. Reinstall from TestFlight.
  5. Open the app, sign in, allow notifications, then cold-reopen once.
  6. Confirm the newest active backend device row is `push_environment = production` before re-sending.
- When validating backend send results, require both a successful APNs delivery with `environment = production` and actual receipt on the TestFlight-installed phone. Transport success alone is not the end of the investigation.
## XcodeGen and Resource Packaging

- If the repo generates Xcode projects, inspect the generator spec before blaming Swift code.
- Wrong resource declarations can create bundles that build but do not install correctly.
- Resource-folder copies, malformed folder references, or unresolved build settings often surface as install-time failures, not compile-time failures.

## Project File Discovery

When a project uses XcodeGen with `sources: [path: AppName]`, all `.swift` files in that directory tree are auto-discovered — but only when the project is regenerated.

**Symptom:** `cannot find 'MyNewView' in scope` after creating a new Swift file, even though the file exists on disk.

**Fix:** Run the project's generation script (typically `scripts/generate-xcodeproj.sh`) or `xcodegen generate` directly. The `.xcodeproj/project.pbxproj` will be updated with the new file references.

**Common pattern:** After creating multiple new files in a feature directory, regenerate once, then build.

For repos managed directly through `.xcodeproj/project.pbxproj`, new Swift files may exist on disk but still be invisible to the build until they are added to the correct target membership. In that case, edit the project file or use Xcode to register the file before investigating feature code.

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

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Prefer Apple documentation for `xcodebuild`, `simctl`, and bundle structure behavior.
- Prefer upstream XcodeBuildMCP docs for tool names, CLI commands, and config keys.
- Treat repo-specific build, scheme, bundle ID, and generator behavior as local facts that must be discovered, not assumed.
- Instrument names, hardware-gated feature availability (e.g., Processor Trace chip requirements), and exact watchdog timings change across Xcode/iOS releases — re-verify against current Apple release notes rather than trusting a fixed number from this skill. Jetsam memory-limit figures are explicitly empirical, not Apple-published, and should be re-derived from device behavior (`os_proc_available_memory`, jetsam event reports), not hardcoded.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

