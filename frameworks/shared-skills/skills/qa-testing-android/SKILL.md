---
name: qa-testing-android
description: "Designs Android testing with Espresso, UI Automator, and Compose. Use when planning device matrices, screenshot tests, CI flows, or flake-control workflows."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# QA Testing (Android)

Android testing automation with Espresso, UI Automator, Compose Testing, screenshot tests, and adaptive UI validation.

**Core References**: [Android Testing Docs](https://developer.android.com/training/testing), [Build-Managed Devices](https://developer.android.com/studio/test/managed-devices), [Compose Testing](https://developer.android.com/develop/ui/compose/testing), [UI Automator](https://developer.android.com/training/testing/other-components/ui-automator), [Screenshot Testing](https://developer.android.com/training/testing/ui-tests/screenshot), [Accessibility Checking](https://developer.android.com/training/testing/espresso/accessibility-checking)

## Quick Reference

| Task | Command |
|------|---------|
| List emulators | `emulator -list-avds` |
| Start emulator | `emulator @<avd_name>` |
| List devices | `adb devices` |
| Install APK | `adb install -r <path-to-apk>` |
| Run unit tests | `./gradlew test` |
| Run instrumented tests (connected) | `./gradlew connectedAndroidTest` |
| Run instrumented tests (GMD) | `./gradlew <device><variant>AndroidTest` |
| Run screenshot tests | `./gradlew validateDebugScreenshotTest` |
| List GMD tasks | `./gradlew tasks --all | rg -n "AndroidTest|Group|ManagedDevices"` |
| Clear app data | `adb shell pm clear <applicationId>` |

## Platform Versions (July 2026)

| Component | Current stable | Notes |
|-----------|---------------|-------|
| Android | 17 (API 37), shipped 2026-06-16; Android 16 (API 36) is the prior release | See "Google Play Target API Policy" below for what to actually target — the newest OS version is not automatically the target-API requirement |
| AGP | 9.2.x | Requires Gradle 8.11+; breaking DSL changes from 8.x |
| Robolectric | 4.16.x | Supports up to SDK 36 (Baklava); SDK 36 requires JDK 21. API 37 support is **not yet released** as of 2026-07-11 — an open upstream issue (robolectric/robolectric#11239, filed 2026-06-14) tracks it. Do not assume Robolectric can simulate Android 17 behavior yet; verify before relying on it for API-37-specific logic |
| UI Automator | 2.4.0-rc01 | Modern `uiAutomator {}` DSL; release-candidate, not yet fully stable — verify current status before pinning in a template |
| Compose Preview Screenshot Testing | 0.0.1-alpha15 | Still alpha; requires AGP 8.5+, Kotlin 2.2.10+ (raised from 1.9.20 — verify against the current release notes before relying on an older Kotlin floor), JDK 17+ |
| ATD images | API 30 only | Use standard `google`/`aosp` images for API 35/36/37 |
| Maestro | API 35/36 added 2026 Q2 | API 37 support **unverified as of 2026-07-11** — check release notes before targeting Android 17 devices in Maestro Cloud |

### Google Play Target API Policy (verify before every release cutover)

As of the 2026-08-31 deadline: new apps and app updates submitted to Google Play must target API level 36 (Android 16) or higher — submissions targeting lower are rejected in Play Console. Apps not updated at all must still target at least API level 35 (Android 15) or they become invisible/uninstallable for new users on newer OS versions. A one-time extension to 2026-11-01 is available by request. This is a moving deadline — re-check `https://developer.android.com/google/play/requirements/target-sdk` before treating any specific API number as "the" requirement, since Google raises it roughly once a year.

## Quick Start

- Prefer build-managed devices (GMD) for CI, using ATD images where the suite and supported API levels allow it; use `connectedAndroidTest` for local ad-hoc runs.
- ATD images only exist for API 30. For API 35/36 suites, use `google` or `aosp` images.
- Enable Android Test Orchestrator and `clearPackageData` for instrumented suites that need strong isolation.
- Disable animations in Gradle, not with ad-hoc ADB steps inside the test flow.
- Treat screenshot tests as a separate fast regression layer: Compose Preview Screenshot Testing for `@Preview` coverage, Paparazzi or Roborazzi for JVM rendering, device-based snapshots only when hardware fidelity matters.
- Cover adaptive layouts explicitly: compact and expanded layouts, tablet or foldable paths when supported, and orientation changes where the product depends on them.
- Add accessibility checks to existing UI tests early instead of treating accessibility as a manual-only phase.

Recommended Gradle defaults for stable instrumented tests:

```kotlin
android {
    testOptions {
        animationsDisabled = true
        execution = "ANDROIDX_TEST_ORCHESTRATOR"

        emulatorSnapshots {
            enableForTestFailures = true
            maxSnapshotsForTestFailures = 2
        }
    }
}

dependencies {
    androidTestUtil(libs.androidx.test.orchestrator)
}

```

If you rely on test isolation between instrumented tests, also set runner args such as `clearPackageData=true` in your Gradle or CI wiring.

## When to Use

- Debug or stabilize flaky Android UI tests
- Add Espresso tests for View-based UIs
- Add Compose UI tests for composables
- Add UI Automator tests for system UI, cross-app flows, or macrobenchmark drivers
- Add screenshot tests for visual regression
- Validate adaptive layouts across screen sizes, window states, or foldable postures
- Add an Android test gate in CI

## Inputs to Gather

- UI stack: Views, Compose, or mixed
- Test layer: unit, Robolectric, instrumented UI, screenshot, UI Automator, macrobenchmark
- CI target: PR gate vs nightly vs release; managed emulator vs device farm
- Device matrix: min supported API, target API, screen classes, locales, dark mode, form factors
- Flake symptoms: timeouts, missing nodes, idling or sync issues, renderer-only diffs, device-only failures
- Accessibility requirements: touch targets, labels, contrast, TalkBack-critical flows
- App seams: DI hooks for fakes, feature flags, test accounts, deterministic clocks, image loaders

## Testing Layers

| Layer | Framework | Scope |
|-------|-----------|-------|
| Unit | JUnit + Mockito | JVM, no Android |
| Unit (Android) | Robolectric | JVM, simulated framework |
| UI (Views) | Espresso | Instrumented |
| UI (Compose) | Compose Testing | Instrumented |
| Adaptive UI | Espresso Device API + `DeviceConfigurationOverride` | Instrumented or host-assisted |
| Screenshot | Compose Preview Screenshot Testing, Paparazzi, Roborazzi | JVM or instrumented |
| System | UI Automator | Cross-app, system UI, benchmarking drivers |

## Core Principles (Stability)

### Device Matrix

- Default: emulators for PR gates; real devices or device farms for release-critical journeys.
- Cover at least min supported API and target API, then add tablet or foldable coverage if the product exposes expanded layouts.
- Model adaptive coverage by layout behavior, not by device marketing names alone.

### Flake Control

- Prefer `testOptions { animationsDisabled = true }` for instrumented tests.
- Use Android Test Orchestrator when shared app state or process crashes cause cross-test leakage.
- Use IdlingResources, Compose synchronization, `waitUntil`, or UI Automator conditions instead of sleeps.
- Mock network with `MockWebServer` or DI fakes; avoid live backends in CI.
- Keep screenshot tests deterministic: fixed fonts, locale, clocks, network images, and seeded data.
- Use test-failure snapshots or screenshots in CI so failures have artifacts, not just stack traces.

### Accessibility And Adaptive Coverage

- Run accessibility checks in the same suite as high-value Espresso or Compose journeys.
- Validate compact and expanded layout states intentionally; do not assume a phone-only test matrix covers responsive layouts.
- Prefer stable selectors: `withId()` for Views, `testTag` for Compose, and resource-id or content descriptions for UI Automator.

## Expert Judgment (What A Checklist Misses)

### Emulator vs. Physical Device — the actual decision

A checklist says "use emulators for CI, real devices for release." The judgment call is *which* real-device signals are worth paying for:

- Emulators (ideally build-managed, ATD where hardware fidelity is not required) are correct for PR gates because they are deterministic, disposable, and free of thermal/battery/OEM noise that would otherwise get misattributed to app bugs.
- Physical devices or a device farm earn their cost only for journeys where OEM or hardware behavior is the actual risk: camera capture, biometric auth, NFC/BLE, background-work reliability under real Doze/App Standby, foldable hinge/posture transitions, and payment SDKs that behave differently under real Play Integrity checks. If none of those are in the flow, a device farm run is theater, not signal.
- A common anti-pattern is running the *entire* regression suite nightly on a device farm "for confidence." This burns budget without changing the failure mode you'd actually catch — most of what fails there also fails, faster and cheaper, on a managed emulator. Reserve device-farm minutes for the handful of hardware-coupled journeys above and gate them separately from the general regression suite.
- Emulator system-image choice is itself a judgment call, not just "google vs aosp": Google Play Services-dependent flows (Play Billing, FCM, Play Integrity, Maps) need `google` images; anything asserting on hardware-rendered pixels needs a non-ATD image; everything else should default to ATD for speed.

### Android Flake Taxonomy (diagnose by category, not by symptom)

Generic "flaky test" triage wastes time re-running instead of classifying. Android UI-test flakiness clusters into a small number of root-cause families — identify which one you're looking at before reaching for retries:

1. **Synchronization gaps** — an async operation Espresso/Compose does not know how to wait for. Signature: passes on a fast local machine, fails under CI load; `NoMatchingViewException` or an assertion firing against a stale loading state. Root cause is almost always an unregistered `IdlingResource` (Espresso) or a missing `waitUntil`/synchronized `TestDispatcher` (Compose/coroutines) — see `references/espresso-patterns.md` for the registration trap.
2. **Animation/transition timing** — window or property animations still running when Espresso samples the view tree. Fix at the Gradle level (`animationsDisabled = true`), never per-test with sleeps; ad-hoc `adb shell settings put global *_scale 0` inside a test body is a workaround that silently stops working if the runner changes.
3. **Semantics-tree merging (Compose-specific)** — `assertExists()`/`onNodeWithText()` finds nothing because Material components merge child semantics into the parent node by default. Not a timing issue at all; do not "fix" it with a wait loop. See the merged-tree trap in `references/compose-testing.md`.
4. **State leakage across tests** — a prior test left SharedPreferences, a DB row, or a singleton in a state the next test doesn't expect. Symptom is order-dependent failures that disappear when the failing test is run alone. Fix with Test Orchestrator + `clearPackageData`, not by reordering tests.
5. **Doze / App Standby / background restrictions** — tests that rely on background work (WorkManager, FCM, foreground services) can behave differently under device power-management states than in a freshly booted emulator. This shows up almost exclusively on physical devices or long-running CI machines, rarely on ephemeral managed devices — if a background-work test is flaky only in one environment, suspect power-management state before suspecting the test.
6. **Renderer/fidelity mismatches** — screenshot diffs that are real but meaningless: ATD disabling hardware rendering, GPU driver differences between CI and local, or font substitution differences across OS images. Distinguish this from an actual visual regression by re-running the same golden generation pipeline on the same image type used to record it.
7. **Non-deterministic test data or clocks** — live network calls, real `System.currentTimeMillis()`, or unseeded random data leaking into assertions or screenshot goldens. Always mockable; the fact that it's still happening usually means a fake wasn't reused when a new screen was added.

When a test is flaky, name which of the seven it is before touching the test — the fix for #1 (register/await) will not touch #4 (isolate/clear state), and applying #2's fix (disable animations) to a #5 issue (Doze) does nothing.

### Test Pyramid Reality For Compose Apps

The classic pyramid (many unit tests, some integration, few E2E) still holds, but Compose changes where the *middle* layer sits:

- Compose lets you unit-test a composable's rendered semantics tree via `createComposeRule()` without an `Activity` or device at all — this is functionally a unit test even though it "looks like" a UI test. Prefer it over `createAndroidComposeRule<Activity>()` whenever the composable doesn't need real navigation, DI graph, or activity lifecycle.
- This shifts a large share of what used to be slow instrumented Espresso coverage down into fast, parallelizable JVM-adjacent tests — but only if ViewModels are tested independently (Turbine/MockK against `StateFlow`, not through the UI). A Compose app that only has "instrumented Compose tests that also exercise the ViewModel" has recreated the old inverted pyramid with new tools.
- Screenshot tests (Compose Preview Screenshot Testing / Paparazzi / Roborazzi) form a *separate, parallel* layer, not a replacement for either unit or instrumented behavioral tests — they catch visual regressions that behavioral assertions cannot see (spacing, overlap, dark-mode contrast) but say nothing about correctness of state transitions.
- Reserve UI Automator and Maestro-style E2E flows for the top of the pyramid: a handful of true cross-app or full-stack smoke journeys (onboarding, checkout, deep-link entry), run on nightly/release pipelines, not PR gates.

### Device / API Fragmentation Strategy

- Always cover the app's actual min supported API and its current target API — these two are non-negotiable regardless of market share.
- Beyond that pair, prioritize by *behavioral risk*, not by device popularity: API levels that changed permission models, background-execution limits, or storage scoping (e.g., scoped storage, notification runtime permission, foreground-service type declarations) deserve dedicated coverage on the OS version that introduced the change, even if that OS version is not the most common one in your install base.
- Treat any specific device/API market-share number as **unverified unless sourced from your own analytics** (Play Console's own device catalog and Android Vitals for your app) — public aggregate stats go stale within months and vary enormously by app category and geography. Do not hardcode "X% of users are on API N" into test-planning docs; pull it fresh from the app's own Play Console dashboard each planning cycle.
- Foldable/tablet/expanded-layout coverage is now a fragmentation axis in its own right, independent of API level — a phone-only test matrix increasingly under-covers real usage on large-screen and foldable devices even when API coverage looks complete.

### When To Invest In Screenshot Testing

Screenshot testing has real setup and maintenance cost (goldens go stale, false positives from font/renderer drift, review burden on every intentional UI change). It is worth that cost when:

- The team ships UI changes frequently enough that manual visual review does not scale (multiple PRs/day touching shared components).
- The app has a design system or component library where a single regression fans out across many screens — screenshot tests catch that fan-out cheaply; behavioral tests do not.
- Dark mode, large font scale, or RTL layouts are supported and have historically regressed silently.

It is a poor early investment for a small team still iterating rapidly on visual design — churn in intentional goldens will dominate signal from real regressions. Start with host-side tools (Compose Preview Screenshot Testing, Paparazzi, Roborazzi) for cheap iteration; only add device-based snapshot testing (Shot, or ATD-excluded device runs) once a specific rendering-sensitive surface (WebView, Maps, camera preview, custom `Canvas`/GPU work) has already caused a shipped visual bug that host-side rendering could not have caught.

## Writing Tests

- Espresso (Views): open `references/espresso-patterns.md`
- Compose: open `references/compose-testing.md`
- UI Automator (system or cross-app): open `references/uiautomator.md`
- Screenshot tests: open `references/screenshot-testing.md`
- Adaptive screen-size testing: open `references/adaptive-screen-testing.md`
- Accessibility checks: open `references/accessibility-checks.md`

## Workflow

### Add a New UI Test (Instrumented)

- Pick the narrowest framework that can observe the behavior: Espresso or Compose first, UI Automator at the system boundary.
- Add stable selectors: View `id`, Compose `Modifier.testTag`, system `resource-id` or content description.
- Control externals: fake network, deterministic data, fixed time and locale, and stable image sources.
- Add waits through framework synchronization or explicit conditions; avoid `Thread.sleep()`.
- Run locally with `connectedAndroidTest` or a single managed-device task before widening the matrix.

### Add Screenshot Coverage

- Use Compose Preview Screenshot Testing for `@Preview`-driven Compose UI states.
- Use Paparazzi or Roborazzi when you need JVM-fast coverage across Compose and legacy Views.
- Keep goldens small, reviewable, and tied to stable UI states instead of whole-screen snapshots of volatile content.
- Capture HTML or diff artifacts in CI on every failure.

### Diagnose a Flaky Instrumented Test

- Reproduce locally or on one managed device before widening the matrix.
- Remove nondeterminism: network, locale, clock, feature flags, image loading, renderer differences.
- Replace sleeps with idling, `waitUntil`, `onElement`, or watcher-based synchronization.
- Capture logcat, screenshot, screen recording, and any managed-device failure snapshot.
- If still flaky, isolate app state further with Orchestrator or runner args and bisect the interaction steps.

### Add A CI Gate (Preferred: Build-Managed Devices)

- Configure build-managed devices plus ATD images when hardware rendering is not required and the API level is supported by the image.
- Add the GitHub Actions GPU flag when your runner lacks hardware rendering support.
- Keep PR gates small and deterministic; expand device groups or sharding on nightly and release pipelines.
- Upload reports from `build/reports/androidTests/`, screenshot reports, diff images, logcat, and managed-device outputs.

## ADB Commands (Triage)

```bash
# Screenshot
adb exec-out screencap -p > screenshot.png

# Screen recording
adb shell screenrecord /sdcard/demo.mp4

# Pull managed-device test artifacts after a local failure
adb pull /sdcard/Android/media ./device-artifacts
```

## CI Integration

Preferred: build-managed devices. See `references/gradle-managed-devices.md` and `references/android-ci-optimization.md`.

```yaml
# .github/workflows/android.yml
name: Android CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6  # or later — verify at actions/checkout releases
      - uses: actions/setup-java@v5  # or later
        with:
          java-version: '17'  # or later
          distribution: 'temurin'
      - uses: gradle/actions/setup-gradle@v5  # or later
      - run: ./gradlew testDebugUnitTest <device><api>DebugAndroidTest -Pandroid.testoptions.manageddevices.emulator.gpu=swiftshader_indirect
```

## ASCII Flow

```text
Android testing request
  -> Classify layer: unit, Robolectric, Compose, Espresso, UI Automator, screenshot
  -> Choose device/API matrix from risk, analytics, and adaptive UI needs
  -> Stabilize state, idling, selectors, permissions, and test data
  -> Run local targeted tests before managed-device or connected-device gates
  -> Capture artifacts: logs, screenshots, videos, and test reports
  -> Deflake root cause before expanding CI matrix or retries
```

## Navigation

The reference guides are intentionally large; search within them instead of loading everything:

- `rg -n "^## " frameworks/shared-skills/skills/qa-testing-android/references/compose-testing.md`
- `rg -n "Idling|waitUntil|Synchronization" frameworks/shared-skills/skills/qa-testing-android/references/compose-testing.md`
- `rg -n "DisplaySizeRule|DeviceConfigurationOverride|fold" frameworks/shared-skills/skills/qa-testing-android/references/adaptive-screen-testing.md`
- `rg -n "PreviewTest|Paparazzi|Roborazzi|Shot" frameworks/shared-skills/skills/qa-testing-android/references/screenshot-testing.md`

## Do / Avoid

### Do

- Prefer build-managed devices plus ATD images for stable CI
- Use Android Test Orchestrator only where isolation solves a real state-leak or crash problem
- Add screenshot and accessibility checks to high-value UI flows
- Run a small matrix on PRs and widen via groups or shards on nightly or release pipelines
- Use a `MainDispatcherRule` + `TestDispatcher` (`runTest { }`, `advanceUntilIdle()`, `kotlinx-coroutines-test`) for every ViewModel and `StateFlow` test — `Dispatchers.setMain(UnconfinedTestDispatcher())` hides off-main crashes that only surface in production
- Run a release-variant smoke test in CI that exercises at least one `@Serializable` endpoint per data class, so R8 full-mode stripping of kotlinx-serialization `$serializer` classes is caught before release (see `software-android-runtime-debugging/references/proguard-r8-triage.md`)
- For Compose tests, assert on semantic state — `onNodeWithTag(...).assertTextEquals(...)` — not on reference equality of UI state objects, because Strong Skipping Mode means the UI may or may not receive the same instance across emissions

### Avoid

- `Thread.sleep()` for synchronization
- Tests that depend on live backends or time-sensitive external content
- Flaky selectors such as localized text or positional-only nodes
- Device-wide screenshot assertions on ATD when hardware-rendered fidelity is required
- Asserting `StateFlow<UiState>` reference equality across emissions (`assertThat(state).isSameInstanceAs(previous)`) — new `data class` instances from `copy()` have different references but structurally equal content; test semantic equality, not identity
- Running serialization-dependent tests only on debug builds — R8 is off in debug, so debug-only suites cannot catch serialization keep-rule failures

## Resources

| Resource | Purpose |
|----------|---------|
| [references/espresso-patterns.md](references/espresso-patterns.md) | Espresso matchers and actions |
| [references/compose-testing.md](references/compose-testing.md) | Compose testing guide |
| [references/uiautomator.md](references/uiautomator.md) | UI Automator patterns for system UI and benchmarking |
| [references/gradle-managed-devices.md](references/gradle-managed-devices.md) | Managed device setup and CI |
| [references/screenshot-testing.md](references/screenshot-testing.md) | Visual regression testing |
| [references/adaptive-screen-testing.md](references/adaptive-screen-testing.md) | Screen-size and foldable coverage |
| [references/accessibility-checks.md](references/accessibility-checks.md) | Accessibility checks for Espresso and Compose |
| [references/test-orchestrator-patterns.md](references/test-orchestrator-patterns.md) | AndroidX Test Orchestrator patterns |
| [references/android-ci-optimization.md](references/android-ci-optimization.md) | CI pipeline optimization |
| [references/modern-test-tooling.md](references/modern-test-tooling.md) | JUnit 5, MockK, Turbine, Robolectric, Maestro |
| [data/sources.json](data/sources.json) | Curated external sources |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-android-test-checklist.md](assets/template-android-test-checklist.md) | Stability checklist |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-mobile](../software-mobile/SKILL.md) | Android development |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Test strategy |
| [qa-testing-mobile](../qa-testing-mobile/SKILL.md) | Cross-platform mobile |
| [software-android-native](../software-android-native/SKILL.md) | Native Android implementation and agent workflows |
| [software-android-runtime-debugging](../software-android-runtime-debugging/SKILL.md) | Build/install/launch proof and stale-build triage |
| [software-android-design](../software-android-design/SKILL.md) | Native Android visual design and Material 3 review |

## Fact-Checking

- Known bugs, regressions, framework/compiler/runtime footguns, and version-specific crash or workaround guidance must be verified against current primary web sources before being treated as current fact.
- Use web search or web fetch to verify current external facts, versions, pricing, deadlines, regulations, or platform behavior before final answers.
- Prefer primary sources; report source links and dates for volatile information.
- If web access is unavailable, state the limitation and mark guidance as unverified.

## Learnings Loop

Before applying this skill on a non-trivial task, read `learnings.consolidated.md` in this directory (and `learnings.md` if present).

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.

