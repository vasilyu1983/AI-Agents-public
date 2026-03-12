# Mobile Performance Testing

Mobile app performance testing and benchmarking -- measuring startup time, frame rate, memory, battery, network, and app size with automated regression detection.

## Contents

- Startup Time Measurement
- Frame Rate and Jank Detection
- Memory Profiling
- Battery Drain Testing
- Network Performance
- App Size Optimization
- Performance Budgets and CI Gates
- Automated Regression Detection
- Tools Comparison
- Performance Testing Checklist
- Related Resources

---

## Startup Time Measurement

### Startup Types

| Type | Definition | Target | Measurement |
|------|-----------|--------|-------------|
| **Cold start** | App process not running; full initialization | <1.5s (Android), <2s (iOS) | From process fork to first frame |
| **Warm start** | Process alive but activity recreated | <1.0s | From activity create to first frame |
| **Hot start** | Activity in background, brought to foreground | <0.5s | From resume to first frame |

### Android: Measuring Startup

```bash
# Displayed time (cold start) - simplest measurement
adb shell am start-activity -W -n com.example.app/.MainActivity
# Output: TotalTime: 1234  (milliseconds)

# Fully drawn time (report when app considers itself ready)
adb shell am start-activity -W -n com.example.app/.MainActivity
# Requires calling Activity.reportFullyDrawn() in app code
```

```kotlin
// Report fully drawn after data loads
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        viewModel.data.observe(this) { data ->
            renderData(data)
            // Signal that the app is fully usable
            reportFullyDrawn()
        }
    }
}
```

### Android: Macrobenchmark (Automated)

```kotlin
// benchmark/src/androidTest/java/StartupBenchmark.kt
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun startupCold() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 10,
        startupMode = StartupMode.COLD
    ) {
        pressHome()
        startActivityAndWait()
    }

    @Test
    fun startupWarm() = benchmarkRule.measureRepeated(
        packageName = "com.example.app",
        metrics = listOf(StartupTimingMetric()),
        iterations = 10,
        startupMode = StartupMode.WARM
    ) {
        pressHome()
        startActivityAndWait()
    }
}
```

### iOS: Measuring Startup

```swift
// XCTest performance measurement
func testColdStartupTime() throws {
    let app = XCUIApplication()
    measure(metrics: [XCTApplicationLaunchMetric()]) {
        app.launch()
    }
}

// Custom metric: time to interactive
func testTimeToInteractive() throws {
    let app = XCUIApplication()
    let start = CFAbsoluteTimeGetCurrent()
    app.launch()

    // Wait for key element indicating app is usable
    let feed = app.collectionViews["mainFeed"]
    XCTAssertTrue(feed.waitForExistence(timeout: 5))

    let elapsed = CFAbsoluteTimeGetCurrent() - start
    XCTAssertLessThan(elapsed, 2.0, "Time to interactive exceeded 2s budget")
}
```

```bash
# Xcode Instruments: App Launch template
xcrun xctrace record --template "App Launch" \
  --device "iPhone 15" \
  --launch com.example.app \
  --output startup-trace.trace
```

---

## Frame Rate and Jank Detection

### Jank Thresholds

| Metric | Good | Needs Work | Poor |
|--------|------|------------|------|
| Average FPS | >=58 | 50-57 | <50 |
| Janky frames (>16ms) | <5% | 5-15% | >15% |
| Frozen frames (>700ms) | 0% | <1% | >=1% |
| 99th percentile frame time | <32ms | 32-50ms | >50ms |

### Android: Jank Detection

```bash
# systrace / Perfetto capture
adb shell perfetto --txt -c - --out /data/misc/perfetto-traces/trace.pb <<EOF
buffers: { size_kb: 63488 }
data_sources: { config { name: "linux.ftrace" ftrace_config {
  ftrace_events: "sched/sched_switch"
  ftrace_events: "power/suspend_resume"
  ftrace_events: "android_os/android_os_wait_for_vsync"
  atrace_categories: "gfx" atrace_categories: "view"
  atrace_categories: "wm" atrace_categories: "am"
} } }
duration_ms: 10000
EOF

adb pull /data/misc/perfetto-traces/trace.pb .
# Open at https://ui.perfetto.dev
```

```bash
# Quick jank stats via dumpsys
adb shell dumpsys gfxinfo com.example.app framestats

# Output includes:
# Total frames rendered: 1234
# Janky frames: 56 (4.54%)
# 50th percentile: 8ms
# 90th percentile: 14ms
# 95th percentile: 18ms
# 99th percentile: 28ms
```

### iOS: Frame Rate Monitoring

```swift
// Instruments: Core Animation FPS
// Use Animation Hitches template in Instruments

// Programmatic monitoring (debug builds)
import QuartzCore

class FrameRateMonitor {
    private var displayLink: CADisplayLink?
    private var lastTimestamp: CFTimeInterval = 0
    private var frameCount = 0
    private var jankCount = 0

    func start() {
        displayLink = CADisplayLink(target: self, selector: #selector(tick))
        displayLink?.add(to: .main, forMode: .common)
    }

    @objc private func tick(link: CADisplayLink) {
        let frameDuration = link.timestamp - lastTimestamp
        frameCount += 1

        // Jank = frame took longer than 2x target (33ms for 60fps)
        if frameDuration > 0.033 && lastTimestamp > 0 {
            jankCount += 1
        }
        lastTimestamp = link.timestamp
    }

    var jankRate: Double {
        guard frameCount > 0 else { return 0 }
        return Double(jankCount) / Double(frameCount) * 100
    }
}
```

---

## Memory Profiling

### Key Metrics

| Metric | Description | Android Tool | iOS Tool |
|--------|-------------|-------------|----------|
| RSS | Resident Set Size (total physical memory) | `dumpsys meminfo` | Instruments Allocations |
| Heap | Java/Kotlin heap (Android) or Swift heap | Android Studio Profiler | Xcode Memory Graph |
| Native | C/C++ allocations | `dumpsys meminfo` | Instruments Leaks |
| Graphics | GPU textures, buffers | `dumpsys meminfo` | Metal System Trace |

### Android Memory Profiling

```bash
# Quick memory snapshot
adb shell dumpsys meminfo com.example.app

# Key values to track:
#   TOTAL PSS (Proportional Set Size) - your app's real memory footprint
#   Java Heap
#   Native Heap
#   Graphics

# Detect leaks with LeakCanary (debug builds)
# build.gradle.kts
# debugImplementation("com.squareup.leakcanary:leakcanary-android:2.14")
```

```kotlin
// Automated memory test with Macrobenchmark
@Test
fun scrollMemoryUsage() = benchmarkRule.measureRepeated(
    packageName = "com.example.app",
    metrics = listOf(MemoryUsageMetric(MemoryUsageMetric.Mode.Max)),
    iterations = 5,
    startupMode = StartupMode.COLD
) {
    startActivityAndWait()
    // Scroll through content
    val list = device.findObject(By.res("com.example.app:id/recyclerView"))
    repeat(10) {
        list.fling(Direction.DOWN)
        device.waitForIdle()
    }
}
```

### iOS Memory Profiling

```bash
# Xcode Instruments: Leaks template
xcrun xctrace record --template "Leaks" \
  --device "iPhone 15" \
  --attach com.example.app \
  --output leaks-trace.trace \
  --time-limit 60s
```

```swift
// Memory assertion in XCTest
func testMemoryAfterNavigation() throws {
    let app = XCUIApplication()
    app.launch()

    // Navigate through screens
    for _ in 0..<10 {
        app.buttons["detailButton"].tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
    }

    // Check memory via MetricKit or os_signpost
    let metrics = XCTMemoryMetric(application: app)
    measure(metrics: [metrics]) {
        app.buttons["detailButton"].tap()
        app.navigationBars.buttons.element(boundBy: 0).tap()
    }
}
```

---

## Battery Drain Testing

### Android: Battery Historian

```bash
# Reset battery stats
adb shell dumpsys batterystats --reset

# Run your test scenario (e.g., 30 min usage simulation)
# ...

# Capture bug report
adb bugreport bugreport.zip

# Analyze with Battery Historian
# Upload bugreport.zip to https://bathist.ef.lc/ or run locally:
docker run -p 9999:9999 gcr.io/android-battery-historian/stable:latest
```

### iOS: Xcode Energy Diagnostics

```bash
# Xcode Instruments: Energy Log template
xcrun xctrace record --template "Energy Log" \
  --device "iPhone 15" \
  --attach com.example.app \
  --output energy-trace.trace \
  --time-limit 300s
```

### Battery Budget Thresholds

| Scenario | Budget | Measurement |
|----------|--------|-------------|
| Idle (background, 1 hour) | <2% drain | Battery Historian / Energy Log |
| Active use (10 min session) | <3% drain | Battery Historian / Energy Log |
| Location tracking (1 hour) | <8% drain | Real device, GPS enabled |
| Push notification idle (8 hours) | <5% drain | Overnight real device test |

---

## Network Performance

### Latency and Bandwidth Simulation

```bash
# Android: emulator network throttling
emulator -avd Pixel_8_API_34 -netdelay 3g -netspeed 3g

# Network condition presets:
#   none    : no delay
#   gprs    : 150-550ms delay, 20-40 kbps
#   edge    : 80-400ms delay, 120-240 kbps
#   umts    : 35-200ms delay, 384 kbps-2Mbps
#   hsdpa   : 0-100ms delay, 14.4 Mbps
#   lte     : 0-50ms delay, 100 Mbps
```

```swift
// iOS: Network Link Conditioner (Xcode)
// Settings > Developer > Network Link Conditioner

// Programmatic with URLSession configuration
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 10
config.waitsForConnectivity = true

// Test offline behavior
config.requestCachePolicy = .reloadIgnoringLocalCacheData

let session = URLSession(configuration: config)
```

### API Response Time Validation

```kotlin
// Android: automated API performance test
@Test
fun apiResponseTimeBudget() = runBlocking {
    val client = OkHttpClient()
    val endpoints = listOf("/api/feed", "/api/profile", "/api/search")

    for (endpoint in endpoints) {
        val start = System.nanoTime()
        val response = client.newCall(
            Request.Builder().url("$BASE_URL$endpoint").build()
        ).execute()
        val elapsed = (System.nanoTime() - start) / 1_000_000 // ms

        assertTrue(
            "API $endpoint took ${elapsed}ms (budget: 500ms)",
            elapsed < 500
        )
        assertTrue("API $endpoint failed: ${response.code}", response.isSuccessful)
    }
}
```

---

## App Size Optimization

### Android: APK Analyzer

```bash
# Command-line APK analysis
$ANDROID_HOME/cmdline-tools/latest/bin/apkanalyzer apk summary app-release.apk
$ANDROID_HOME/cmdline-tools/latest/bin/apkanalyzer apk file-size app-release.apk
$ANDROID_HOME/cmdline-tools/latest/bin/apkanalyzer dex packages app-release.apk | head -20

# Size budget CI check
MAX_SIZE_MB=25
ACTUAL_SIZE=$(stat -f%z app-release.apk)
ACTUAL_MB=$((ACTUAL_SIZE / 1048576))
if [ "$ACTUAL_MB" -gt "$MAX_SIZE_MB" ]; then
  echo "FAIL: APK size ${ACTUAL_MB}MB exceeds budget ${MAX_SIZE_MB}MB"
  exit 1
fi
```

### iOS: App Thinning Report

```bash
# Generate app thinning size report
xcodebuild -exportArchive \
  -archivePath MyApp.xcarchive \
  -exportOptionsPlist ExportOptions.plist \
  -exportPath output/ \
  -exportThinning '<thin-for-all-variants>'

# Parse App Thinning Size Report.txt for per-device sizes
```

### Size Budgets

| Platform | Category | Budget |
|----------|----------|--------|
| Android | APK (universal) | <30 MB |
| Android | AAB download size | <15 MB (per device) |
| iOS | IPA (thinned) | <30 MB |
| iOS | App Store download | <200 MB (cellular limit) |

---

## Performance Budgets and CI Gates

### Budget Configuration

```json
{
  "performance_budgets": {
    "startup_cold_ms": 1500,
    "startup_warm_ms": 1000,
    "jank_rate_pct": 5,
    "memory_peak_mb": 256,
    "apk_size_mb": 25,
    "ipa_size_mb": 30,
    "api_p95_ms": 500,
    "frozen_frames_pct": 0
  }
}
```

### CI Gate Script

```python
#!/usr/bin/env python3
"""Performance budget gate for CI pipelines."""
import json
import sys

def check_budgets(results_file: str, budgets_file: str) -> bool:
    with open(results_file) as f:
        results = json.load(f)
    with open(budgets_file) as f:
        budgets = json.load(f)["performance_budgets"]

    passed = True
    for metric, budget in budgets.items():
        actual = results.get(metric)
        if actual is None:
            print(f"  WARN: {metric} not measured")
            continue
        if actual > budget:
            print(f"  FAIL: {metric} = {actual} (budget: {budget})")
            passed = False
        else:
            print(f"  PASS: {metric} = {actual} (budget: {budget})")

    return passed

if __name__ == "__main__":
    ok = check_budgets(sys.argv[1], sys.argv[2])
    sys.exit(0 if ok else 1)
```

```yaml
# GitHub Actions: performance gate
- name: Check performance budgets
  run: python scripts/check_perf_budgets.py results.json budgets.json
```

---

## Automated Regression Detection

### Statistical Comparison

```python
def detect_regression(
    baseline: list[float],
    current: list[float],
    threshold_pct: float = 10.0
) -> dict:
    """Compare current metrics against baseline with statistical significance."""
    import statistics

    baseline_median = statistics.median(baseline)
    current_median = statistics.median(current)
    change_pct = ((current_median - baseline_median) / baseline_median) * 100

    # Mann-Whitney U test for significance (non-parametric)
    from scipy.stats import mannwhitneyu
    stat, p_value = mannwhitneyu(baseline, current, alternative='greater')

    regression = change_pct > threshold_pct and p_value < 0.05
    return {
        "baseline_median": f"{baseline_median:.1f}",
        "current_median": f"{current_median:.1f}",
        "change_pct": f"{change_pct:+.1f}%",
        "p_value": f"{p_value:.4f}",
        "regression_detected": regression,
    }
```

### Trend Tracking

| Approach | Pros | Cons |
|----------|------|------|
| Compare to last N runs | Simple, catches recent regressions | Noisy with small N |
| Compare to release baseline | Stable reference point | Must update baselines |
| Rolling percentile | Smooth trend detection | Slow to detect sudden changes |
| Statistical test (Mann-Whitney) | Confidence interval | Requires 10+ data points |

---

## Tools Comparison

| Tool | Platform | Metrics | Automation | CI Ready |
|------|----------|---------|------------|----------|
| Android Macrobenchmark | Android | Startup, frames, memory | Gradle test | Yes |
| Perfetto / systrace | Android | Frames, CPU, I/O | CLI | Yes |
| Battery Historian | Android | Battery, wakelocks | CLI + web | Partial |
| Xcode Instruments | iOS | All performance metrics | xctrace CLI | Yes |
| XCTest metrics | iOS | Startup, memory, CPU | XCTest | Yes |
| Firebase Performance | Both | Startup, network, traces | SDK | Yes |
| Emerge Tools | Both | App size analysis | CLI + web | Yes |

---

## Performance Testing Checklist

Before release:

- [ ] Cold start measured on minimum-spec device (Tier 1)
- [ ] Frame rate profiled during key user journeys (scroll, transition)
- [ ] Memory profiled: no leaks after 10 navigation cycles
- [ ] Battery measured for 30-min active session
- [ ] App size within budget; delta from last release documented
- [ ] Network performance tested under 3G simulation
- [ ] Performance budgets gate passing in CI
- [ ] Regression comparison against last release baseline
- [ ] Results documented in release notes

---

## Related Resources

- [device-farm-strategies.md](./device-farm-strategies.md) -- cloud device farm selection for perf testing at scale
- [flake-management.md](./flake-management.md) -- stability for performance test suites
- [framework-comparison.md](./framework-comparison.md) -- automation frameworks with performance support
- [SKILL.md](../SKILL.md) -- parent mobile testing skill
- [Android Macrobenchmark](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)
- [Xcode Instruments](https://developer.apple.com/tutorials/instruments)
- [Perfetto Trace Viewer](https://ui.perfetto.dev)
- [Firebase Performance Monitoring](https://firebase.google.com/docs/perf-mon)
