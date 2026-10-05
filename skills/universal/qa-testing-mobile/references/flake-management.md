# Mobile Test Flake Management

## Table of Contents

- [Flake Detection](#flake-detection)
- [Common Causes and Fixes](#common-causes-and-fixes)
- [Quarantine Strategy](#quarantine-strategy)
- [Rerun Policies](#rerun-policies)
- [Flake Economics: Real Device vs Simulator](#flake-economics-real-device-vs-simulator)
- [Prevention Checklist](#prevention-checklist)
- [Monitoring Dashboard](#monitoring-dashboard)
- [Resources](#resources)

Strategies for identifying, tracking, and eliminating flaky tests in mobile automation.

Treat "flake budget" as a first-class quality SLI; UI suites without active controls commonly show high flake rates (rates vary by suite; measure your own).

## Flake Detection

### Metrics to Track

| Metric | Target | Action if Exceeded |
|--------|--------|-------------------|
| Flake rate per test | <5% | Quarantine and fix |
| Flake rate per device | <10% | Investigate device-specific issues |
| CI rerun rate | <15% | Review infrastructure stability |
| Time lost to flakes | <2 hrs/week | Prioritize top offenders |

### Artifacts and Reproducibility (REQUIRED)

Capture enough context to reproduce on the same device/OS and compare runs:

- iOS: `.xcresult` bundle, screenshots, screen recording (if enabled), device logs, simulator/device model + iOS version, test plan/config, app build SHA.
- Android: instrumentation output, logcat, screenshots/video (device farm), device model + API level + OEM build, test runner args, app build SHA.
- Network state: mocked vs real, throttling profile, backend environment, feature flags/experiments state.

### Identifying Flaky Tests

```bash
# Track test history over time
# Look for tests that pass/fail inconsistently on same code

# Pattern: same test, same code, different results
Test: LoginFlow
Run 1: PASS
Run 2: FAIL (timeout)
Run 3: PASS
Run 4: PASS
Run 5: FAIL (element not found)
```

### Test Analytics (Optional)

Use test analytics to correlate failures with device model/OS, infra, and recent changes.

Examples (non-exhaustive):

- Test analytics/visibility in CI (Datadog, Buildkite/Test Analytics, etc.)
- Device cloud observability (BrowserStack, LambdaTest, etc.)
- Quarantine workflows (Trunk.io, custom tags, etc.)

## Common Causes and Fixes

Generic fixes (explicit waits instead of sleeps, stubbing the network at the test boundary, resetting state per test) apply as on any UI suite. The mobile-specific versions:

| Cause | Symptom | Mobile-specific fix |
|---|---|---|
| Async work the framework cannot see | Element not found, timeouts | iOS: `waitForExistence(timeout:)` / expectations; Android: register an Espresso `IdlingResource` for custom executors and network clients (Compose tests sync with the Compose clock automatically); Detox: keep synchronization on and wait with `waitFor` |
| Animations | Tap lands on the wrong element, scroll fails | Android: set `window_animation_scale`, `transition_animation_scale` and `animator_duration_scale` to 0 via `adb shell settings put global …`, or `testOptions { animationsDisabled = true }` in Gradle; iOS: a launch argument the app reads to disable its own animations (XCUITest has no global switch) |
| Backend or network | Passes locally, fails in CI | iOS: `URLProtocol` stub registered in the app under test; Android: OkHttp `MockWebServer`; for parallel device runs give each shard its own test account or data namespace |
| State leaking between tests | Passes alone, fails in suite | Android: Test Orchestrator with `clearPackageData`; iOS: a reset launch argument or uninstall between suites; never rely on test order |
| Screen size and OEM behaviour | Passes on flagship, fails on small or OEM devices | Scroll to the element with a bounded retry (not an unbounded `while !isHittable` loop); handle OEM permission and battery dialogs with UIAutomator; keep the smallest supported screen in the PR matrix |
| System dialogs and permissions | Random blocking alerts | Pre-grant with `adb shell pm grant` / `xcrun simctl privacy`, or use `addUIInterruptionMonitor` / UIAutomator for the dialogs that remain |

## Quarantine Strategy

### Quarantine Workflow

1. **Detect**: Test fails 3+ times on same code within 24 hours
2. **Quarantine**: Mark as flaky and exclude from blocking CI
3. **Assign**: Assign owner with 1-week SLA
4. **Fix or Delete**: Either stabilize or remove permanently
5. **Reinstate**: Return to main suite after 10 consecutive passes

### Implementation

For iOS UI automation (XCUITest), quarantine by test plan/selection rather than ad-hoc code flags:

- Put unstable tests in a separate class/target (for example `FlakyTests`) or a separate Xcode Test Plan configuration.
- Run stable suites on PR; run flaky suites in a non-blocking job.

For Android instrumentation, quarantine with annotations + runner arguments:

```kotlin
@Retention(AnnotationRetention.RUNTIME)
@Target(AnnotationTarget.FUNCTION)
annotation class Flaky(val bug: String)

@Flaky("JIRA-1234")
@Test
fun unstableTest() { }
```

```bash
# Stable suite (exclude flaky)
./gradlew connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.notAnnotation=com.example.Flaky

# Flaky suite (run separately, non-blocking)
./gradlew connectedDebugAndroidTest -Pandroid.testInstrumentationRunnerArguments.annotation=com.example.Flaky
```

### CI Configuration

```yaml
# GitHub Actions: Separate flaky test job
jobs:
  stable-tests:
    runs-on: macos-latest
    steps:
      - run: xcodebuild test -skip-testing:MyAppTests/FlakyTests

  flaky-tests:
    runs-on: macos-latest
    continue-on-error: true  # Don't block PR
    steps:
      - run: xcodebuild test -only-testing:MyAppTests/FlakyTests
```

## Rerun Policies

### Recommended Limits

| Test Type | Max Retries | Notes |
|-----------|-------------|-------|
| Unit tests | 0 | Must be deterministic |
| Integration | 1 | May have external deps |
| UI tests | 2 | Most prone to flakes |
| E2E tests | 2 | Complex, allow retries |

### Implementation

```yaml
# Fastlane
lane :test do
  scan(
    scheme: "MyApp",
    only_testing: ["MyAppUITests"],
    try_count: 2,  # Retries for failed tests (keep low)
    parallel_testing: true
  )
end
```

```bash
# xcodebuild: emit a result bundle for triage
xcodebuild test ... -resultBundlePath TestResults.xcresult
# Optional: rerun only failing tests via your CI orchestration (keep retries low)
```

**Warning**: High rerun rates mask underlying issues. If rerun rate >20%, stop and fix root causes.

## Flake Economics: Real Device vs Simulator

The same nominal "flake rate" costs very differently depending on where the test ran. Budget and quarantine decisions should weigh cost-per-flake, not just frequency:

| Cost driver | Simulator / Emulator | Real Device (owned or cloud farm) |
|---|---|---|
| Rerun latency | Seconds (already booted, local) | Minutes (queue for a device slot, re-flash, re-provision) |
| Rerun cost | Near-zero marginal compute | Metered minutes or concurrency-slot time; queue contention can block other jobs |
| Root-cause class | Mostly test-code timing/animation bugs — genuinely fixable | Mix of test bugs **and** real hardware variance (thermal throttling, background OS processes, carrier network blips, OEM skin quirks) that no test fix will fully remove |
| Signal value | High — a simulator flake is almost always a test defect | Mixed — some real-device flakes are legitimate defects (worth fixing), others are irreducible hardware noise (worth tolerating, not chasing) |

**Practical implications:**

- Do not apply the same rerun-limit or quarantine SLA uniformly. A simulator flake at >5% justifies an aggressive 1-week fix SLA (cheap to reproduce, high signal). A real-device flake at the same rate may warrant a longer investigation window because reproduction itself costs queue time and money.
- When a real-device-only flake cannot be reproduced after 2-3 real-device reruns plus a review of device/thermal/network logs, it is reasonable to tag it "hardware noise — monitor" rather than burn further device-farm budget chasing it. Re-open if the rate climbs or spreads to other devices.
- Keep the PR-gate layer emulator/simulator-first specifically because a flaky PR gate on real devices creates a double cost: developer time waiting on a slow rerun loop, and device-farm spend on reruns that may not even be diagnosable.
- Track flake rate **and** cost-to-reproduce as two separate columns in the flake dashboard; a low-frequency but expensive-to-reproduce real-device flake can consume more budget than a high-frequency, cheap-to-fix simulator flake.

## Prevention Checklist

Before adding new UI tests:

- [ ] Uses explicit waits, not fixed sleeps
- [ ] Uses accessibilityIdentifier, not text labels
- [ ] Mocks network calls
- [ ] Resets app state in setUp
- [ ] Handles system alerts (permissions, notifications)
- [ ] Verified on smallest and largest device in matrix
- [ ] Runs 10x locally without failure

## Monitoring Dashboard

Track these metrics weekly:

```text
Flake Report - Week of 2026-01-18
---------------------------------
Total UI tests:           245
Flaky tests (>5% rate):   12 (4.9%)
Top offenders:
  1. testPaymentFlow      - 23% flake rate (network timing)
  2. testOnboarding       - 18% flake rate (animation)
  3. testDeepLink         - 15% flake rate (race condition)

Action items:
  - testPaymentFlow: Add network mock by 01/25
  - testOnboarding: Disable animations, verify by 01/22
  - testDeepLink: Review async handling by 01/24
```

## Resources

- [Bitrise: Why Flaky Tests Are Increasing](https://sdtimes.com/bitrise/why-flaky-tests-are-increasing-and-what-you-can-do-about-it/)
- [AccelQ: Flaky Tests 2026](https://www.accelq.com/blog/flaky-tests/)
- [TestDino: Flaky Test Detection Tools](https://testdino.com/blog/flaky-test-detection-tools/)
- [UI-Based Flaky Tests Research (ICSE)](https://weihang-wang.github.io/papers/UIFlaky-icse21.pdf)
