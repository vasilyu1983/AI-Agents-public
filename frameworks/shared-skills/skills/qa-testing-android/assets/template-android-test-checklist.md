# Android UI Test Stability Checklist

Pre-flight checklist for stable, deterministic Android UI tests.

## Environment Setup

- REQUIRED: animations disabled (prefer Gradle `testOptions { animationsDisabled = true }`)
- REQUIRED: Test Orchestrator enabled for isolation (instrumented tests)
- REQUIRED: sufficient emulator resources (RAM, storage)
- REQUIRED: network controlled or mocked for deterministic tests
- CONSIDER: emulator GPU mode `swiftshader_indirect` on CI if rendering issues

## Test Structure

- REQUIRED: each test is independent (no ordering dependencies)
- REQUIRED: app state reset per test (account, storage, flags)
- REQUIRED: test data created fresh per test
- REQUIRED: no shared mutable state between tests
- REQUIRED: teardown/cleanup in `@After`

## Synchronization

- AVOID: `Thread.sleep()`
- REQUIRED: IdlingResources (Espresso) or `waitUntil` (Compose) for async operations
- REQUIRED: network mocked (MockWebServer / DI fake) or synchronized via idling
- REQUIRED: database operations complete before assertions
- REQUIRED: animations disabled or deterministically awaited

## Element Selection

- REQUIRED: Views use resource IDs (`withId()`), not text
- REQUIRED: Compose uses `testTag` for stable selection
- CONSIDER: content descriptions for accessibility and some system UI elements
- AVOID: locale-dependent text matching for primary selectors
- REQUIRED: selectors remain stable across UI refactors

## Assertions

- REQUIRED: wait for element existence before interaction
- REQUIRED: use `waitUntil` for dynamic content
- REQUIRED: check visibility before click actions
- REQUIRED: verify state, not just existence
- REQUIRED: meaningful failure messages

## Device Matrix

- REQUIRED: tested on min supported API level
- REQUIRED: tested on target API level
- CONSIDER: small screen phone + large screen tablet/foldable (if supported)
- CONSIDER: different locales (if localization is user-facing)

## CI Configuration

- REQUIRED: emulator boot completion gate before tests run
- REQUIRED: screenshots captured on failure (where feasible)
- REQUIRED: logcat captured on failure
- CONSIDER: retry policy for known transient failures (max 1-2)

## Flake Prevention

- REQUIRED: test runs 10x locally without failure before merging
- AVOID: time-dependent assertions
- REQUIRED: no live network-dependent data (use mocks)
- REQUIRED: no reliance on device state outside the test
- REQUIRED: scroll to element before interaction

## Quick Commands

```bash
# Clear app data before test
adb shell pm clear com.example.app

# Run with orchestrator
./gradlew connectedAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.clearPackageData=true

# Capture logcat on failure
adb logcat -d > test_failure.log

# Screenshot on failure
adb exec-out screencap -p > failure.png
```

## Common Flake Causes

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Element not found | Animation in progress | Disable animations or use IdlingResource |
| Timeout | Network delay | Mock network with MockWebServer |
| Wrong element clicked | Scroll position | Call `scrollTo()` before click |
| State from previous test | Shared state | Reset app data in @Before |
| Works locally, fails on CI | Animation timing | Add explicit waits |

## Sign-Off

| Check | Owner | Date |
|-------|-------|------|
| 10x local runs pass | | |
| CI pipeline verified | | |
| Device matrix covered | | |
| Flake rate <5% | | |
