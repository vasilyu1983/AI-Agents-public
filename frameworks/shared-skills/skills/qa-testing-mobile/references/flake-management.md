# Mobile Test Flake Management

Strategies for identifying, tracking, and eliminating flaky tests in mobile automation.

Typical UI-suite flake rates can reach 5-30% without active controls; treat "flake budget" as a first-class quality SLI.

## Contents

- Flake Detection
- Common Causes and Fixes
- Quarantine Strategy
- Rerun Policies
- Prevention Checklist
- Monitoring Dashboard
- Resources

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

### 1. Timing Issues (Most Common)

**Symptom**: Element not found, timeout errors

**Bad**:
```javascript
// Fixed sleep - fragile
await driver.sleep(3000);
await driver.findElement(By.id('submit')).click();
```

**Good**:
```javascript
// Explicit wait for condition
await driver.wait(
  until.elementIsVisible(driver.findElement(By.id('submit'))),
  10000
);
await driver.findElement(By.id('submit')).click();
```

**Platform-specific**:

```swift
// iOS: waitForExistence
let button = app.buttons["submitButton"]
XCTAssertTrue(button.waitForExistence(timeout: 10))
button.tap()
```

```kotlin
// Android Espresso: IdlingResource
IdlingRegistry.getInstance().register(networkIdlingResource)
onView(withId(R.id.submit)).perform(click())
```

### 2. Animation Interference

**Symptom**: Tap registers on wrong element, scroll fails

**Fix**: Disable animations in test builds

```swift
// iOS: In test setUp or launch arguments
app.launchArguments.append("--disable-animations")
```

```kotlin
// Android: Developer options or test rule
@get:Rule
val disableAnimationsRule = DisableAnimationsRule()
```

```bash
# Android: ADB command
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
```

### 3. Network Dependency

**Symptom**: Works locally, fails in CI

**Fix**: Mock network at test boundary

```swift
// iOS: URLProtocol stubbing
class MockURLProtocol: URLProtocol {
    static var mockResponses: [URL: Data] = [:]

    override class func canInit(with request: URLRequest) -> Bool { true }

    override func startLoading() {
        if let data = Self.mockResponses[request.url!] {
            client?.urlProtocol(self, didLoad: data)
        }
        client?.urlProtocolDidFinishLoading(self)
    }
}
```

```kotlin
// Android: OkHttp MockWebServer
@Before
fun setUp() {
    mockWebServer = MockWebServer()
    mockWebServer.start()

    mockWebServer.enqueue(MockResponse()
        .setBody("""{"user": "test"}""")
        .setResponseCode(200))
}
```

### 4. Shared State Between Tests

**Symptom**: Test passes alone, fails in suite

**Fix**: Reset state before each test

```swift
// iOS: Reset app state
override func setUp() {
    app = XCUIApplication()
    app.launchArguments = ["--reset-state", "--uitesting"]
    app.launch()
}
```

```kotlin
// Android: Clear app data
@Before
fun clearData() {
    InstrumentationRegistry.getInstrumentation()
        .targetContext.deleteDatabase("app.db")
    InstrumentationRegistry.getInstrumentation()
        .targetContext.getSharedPreferences("prefs", 0).edit().clear().apply()
}
```

### 5. Device-Specific Issues

**Symptom**: Passes on iPhone 15, fails on iPhone SE

**Fix**:
- Check screen size assumptions
- Verify element visibility before interaction
- Use scroll-to-element patterns

```swift
// Scroll to element before tap
let element = app.buttons["hiddenButton"]
while !element.isHittable {
    app.swipeUp()
}
element.tap()
```

### 6. Race Conditions

**Symptom**: Intermittent failures, non-deterministic order

**Fix**: Use synchronization primitives

```kotlin
// Android: Espresso IdlingResource for async operations
class NetworkIdlingResource : IdlingResource {
    private var callback: IdlingResource.ResourceCallback? = null
    private var isIdle = true

    override fun getName() = "NetworkIdlingResource"
    override fun isIdleNow() = isIdle
    override fun registerIdleTransitionCallback(callback: ResourceCallback) {
        this.callback = callback
    }

    fun setIdle(idle: Boolean) {
        isIdle = idle
        if (idle) callback?.onTransitionToIdle()
    }
}
```

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
