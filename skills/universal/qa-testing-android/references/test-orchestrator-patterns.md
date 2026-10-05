# AndroidX Test Orchestrator Patterns

Test isolation and crash recovery using AndroidX Test Orchestrator.

**Official docs**: [AndroidX Test Orchestrator](https://developer.android.com/training/testing/instrumented-tests/androidx-test-libraries/runner#orchestrator)

## Contents

- [Orchestrator Architecture](#orchestrator-architecture)
- [Gradle Configuration](#gradle-configuration)
- [clearPackageData Flag](#clearpackagedata-flag)
- [Test Sharding](#test-sharding)
- [Custom Test Runners](#custom-test-runners)
- [JUnit 4 Rules for Setup and Teardown](#junit-4-rules-for-setup-and-teardown)
- [Device State Management](#device-state-management)
- [Orchestrator with Firebase Test Lab](#orchestrator-with-firebase-test-lab)
- [Troubleshooting](#troubleshooting)
- [Performance Impact and Mitigation](#performance-impact-and-mitigation)
- [Related Resources](#related-resources)

---

## Orchestrator Architecture

Without Orchestrator, all tests run in a single instrumentation process, so one crash takes out
every subsequent test in that process. With Orchestrator, each test runs in its own instrumentation
invocation: a crash is isolated to that test, each test starts with a clean process, and CI can
report crashed tests individually instead of as a batch. `clearPackageData` (below) adds optional
per-test data clearing on top of that isolation.

---

## Gradle Configuration

### Basic Setup

```kotlin
// app/build.gradle.kts
android {
    defaultConfig {
        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"

        testInstrumentationRunnerArguments["clearPackageData"] = "true"
    }

    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"
    }
}

dependencies {
    androidTestImplementation("androidx.test:runner:<compatible-version>")
    androidTestImplementation("androidx.test:rules:<compatible-version>")
    androidTestUtil("androidx.test:orchestrator:<compatible-version>")
}
```

### Using Gradle Managed Devices with Orchestrator

```kotlin
android {
    testOptions {
        execution = "ANDROIDX_TEST_ORCHESTRATOR"

        managedDevices {
            localDevices {
                create("pixel6api34") {
                    device = "Pixel 6"
                    apiLevel = 34
                    systemImageSource = "aosp"
                }
            }
        }
    }
}
```

```bash
# Run with managed device + orchestrator
./gradlew pixel6api34DebugAndroidTest
```

---

## clearPackageData Flag

When enabled, Orchestrator clears all app data (SharedPreferences, databases, files) between each test.

### When to Use

| Scenario                           | clearPackageData | Reason                          |
|------------------------------------|------------------|---------------------------------|
| Tests modify SharedPreferences     | Yes              | Prevent state leakage           |
| Tests write to local database      | Yes              | Clean database per test         |
| Tests are read-only                | No               | Skip overhead for faster runs   |
| Login state persists between tests | Yes              | Ensure consistent auth state    |
| Performance-sensitive CI           | No               | Avoids data-wipe overhead; measure locally |

### Selective Clearing

You cannot selectively enable `clearPackageData` per test class with the flag alone. Instead, handle cleanup in test code.

```kotlin
@Before
fun clearState() {
    // Clear only specific data
    InstrumentationRegistry.getInstrumentation()
        .targetContext
        .deleteDatabase("app.db")

    InstrumentationRegistry.getInstrumentation()
        .targetContext
        .getSharedPreferences("user_prefs", Context.MODE_PRIVATE)
        .edit()
        .clear()
        .commit()
}
```

---

## Test Sharding

Orchestrator supports sharding tests across multiple devices or emulators for parallel execution.

### Command-Line Sharding

With Orchestrator enabled in Gradle, run one shard per connected runner:

```bash
# Example: first shard of three
./gradlew connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.numShards=3 \
  -Pandroid.testInstrumentationRunnerArguments.shardIndex=0
```

For direct ADB execution, use the [official shell-executor setup](https://developer.android.com/training/testing/instrumented-tests/androidx-test-libraries/runner#enable-command)
with test-services installed and an explicit `targetInstrumentation`; invoking Orchestrator without
that target does not identify the suite.

### CI Sharding with Gradle Managed Devices

```kotlin
android {
    testOptions {
        managedDevices {
            groups {
                create("phoneShards") {
                    targetDevices.addAll(
                        listOf(
                            devices["pixel6api34"],
                        )
                    )
                    // GMD handles sharding automatically with -Pandroid.experimental.androidTest.numManagedDeviceShards
                }
            }
        }
    }
}
```

```bash
# Run with 4 shards across managed devices
./gradlew phoneShardsGroupDebugAndroidTest \
  -Pandroid.experimental.androidTest.numManagedDeviceShards=4
```

---

## Custom Test Runners

### Filtering Tests by Annotation

```kotlin
// Custom annotation
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class SmokeSuite

// Test class
class LoginTests {
    @SmokeSuite
    @Test
    fun login_with_valid_credentials() { /* ... */ }

    @Test
    fun login_with_expired_token() { /* ... */ }
}
```

```bash
# With Orchestrator already enabled in Gradle
./gradlew connectedDebugAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.annotation=com.example.app.SmokeSuite
```

### Custom Runner with Hilt

```kotlin
// HiltTestRunner.kt
class HiltTestRunner : AndroidJUnitRunner() {
    override fun newApplication(
        cl: ClassLoader?,
        className: String?,
        context: Context?
    ): Application {
        return super.newApplication(cl, HiltTestApplication::class.java.name, context)
    }
}
```

```kotlin
// build.gradle.kts
android {
    defaultConfig {
        testInstrumentationRunner = "com.example.app.HiltTestRunner"
    }
}
```

---

## JUnit 4 Rules for Setup and Teardown

### Activity Scenario Rule

```kotlin
import androidx.test.ext.junit.rules.ActivityScenarioRule

class MainActivityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(MainActivity::class.java)

    @Test
    fun activity_launches_successfully() {
        activityRule.scenario.onActivity { activity ->
            assertNotNull(activity.findViewById<View>(R.id.root))
        }
    }
}
```

### Compose Test Rule

```kotlin
import androidx.compose.ui.test.junit4.v2.createAndroidComposeRule

class ComposeActivityTest {
    @get:Rule
    val composeRule = createAndroidComposeRule<MainActivity>()

    @Test
    fun greeting_displays() {
        composeRule.onNodeWithText("Welcome").assertIsDisplayed()
    }
}
```

### Custom Rule: Database Seeding

```kotlin
class DatabaseSeedRule(
    private val seedData: () -> Unit,
    private val cleanUp: () -> Unit
) : TestRule {
    override fun apply(base: Statement, description: Description): Statement {
        return object : Statement() {
            override fun evaluate() {
                seedData()
                try {
                    base.evaluate()
                } finally {
                    cleanUp()
                }
            }
        }
    }
}

// Usage
class OrderHistoryTest {
    @get:Rule
    val dbRule = DatabaseSeedRule(
        seedData = { TestDatabase.insertOrders(sampleOrders) },
        cleanUp = { TestDatabase.clearAll() },
    )

    @Test
    fun displays_order_list() {
        // sampleOrders are in the database
    }
}
```

### Rule Ordering

```kotlin
class ComplexTest {
    // Rules execute outer-to-inner based on order
    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    // Seed before the Activity launches and reads the database.
    @get:Rule(order = 1)
    val dbRule = DatabaseSeedRule(::seed, ::clean)

    @get:Rule(order = 2)
    val composeRule = createAndroidComposeRule<MainActivity>()
}
```

---

## Device State Management

### Disabling Animations

```bash
# Via adb (do this before test suite)
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0
```

```kotlin
// Via Gradle test options
android {
    testOptions {
        animationsDisabled = true
    }
}
```

### Setting Locale

Set the locale through the app's locale API or a test-specific configuration override before
launching the Activity. `createConfigurationContext(config)` returns a new Context; discarding
that Context does not change the displayed Activity. Restore the prior locale after the test.

### Managing WiFi and Network

```kotlin
// Shell identity performs this command; CHANGE_WIFI_STATE does not grant airplane-mode control
@Before
fun enableAirplaneMode() {
    InstrumentationRegistry.getInstrumentation()
        .uiAutomation
        .executeShellCommand("cmd connectivity airplane-mode enable")
}

@After
fun disableAirplaneMode() {
    InstrumentationRegistry.getInstrumentation()
        .uiAutomation
        .executeShellCommand("cmd connectivity airplane-mode disable")
}
```

### Screen State

```kotlin
@Before
fun wakeDevice() {
    val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
    device.wakeUp()
    // Dismiss keyguard
    InstrumentationRegistry.getInstrumentation()
        .uiAutomation
        .executeShellCommand("wm dismiss-keyguard")
}
```

---

## Orchestrator with Firebase Test Lab

### gcloud Command

Resolve model IDs with `gcloud firebase test android models list` before substituting the example.

```bash
gcloud firebase test android run \
  --type instrumentation \
  --app app-debug.apk \
  --test app-debug-androidTest.apk \
  --use-orchestrator \
  --environment-variables clearPackageData=true \
  --device "model=<model-id>,version=34,locale=en,orientation=portrait" \
  --num-uniform-shards=4 \
  --timeout 30m \
  --results-dir="test-results/$(date +%Y%m%d)" \
  --results-bucket=gs://my-test-results
```

### Firebase Test Lab Configuration Matrix

| Parameter          | Value                    | Purpose                     |
|--------------------|--------------------------|-----------------------------|
| `--use-orchestrator` | (flag)                 | Enable test isolation       |
| `--num-uniform-shards` | 4                    | Parallel execution          |
| `--timeout`        | 30m                      | Per-shard timeout           |
| `--environment-variables` | `clearPackageData=true` | Clean state per test   |
| `--device`         | model=<model-id>,version=34 | Target device profile — get valid model codenames from `gcloud firebase test android models list`, not the marketing name (unverified: whether "Pixel6" is a valid FTL model id) |

---

## Troubleshooting

### Common Issues

| Issue                                    | Cause                          | Fix                                      |
|------------------------------------------|--------------------------------|------------------------------------------|
| Tests hang indefinitely                  | Orchestrator APK not installed | Add `androidTestUtil` dependency          |
| "No tests found"                         | Wrong runner class             | Verify `testInstrumentationRunner`        |
| Tests pass locally, fail on CI           | State leaking without Orchestrator | Enable `clearPackageData`           |
| Extremely slow test suite                | Per-test process overhead      | Limit `clearPackageData` to needed tests  |
| `SecurityException` on shell commands    | Missing permissions            | Add to `androidTest/AndroidManifest.xml`  |
| Orchestrator crashes on start            | Version mismatch               | Align runner, rules, and orchestrator versions |

### Debugging

```bash
# Check Orchestrator logs
adb logcat -s "AndroidTestOrchestrator" "TestRunner"

# Verify Orchestrator APK is installed
adb shell pm list packages | grep orchestrator

# Check test APK instrumentation
adb shell pm list instrumentation
```

### Version Alignment

```kotlin
// All AndroidX Test dependencies should use compatible versions.
// Select the runner, rules, core, ext.junit and orchestrator from the compatible release family:
// https://developer.android.com/jetpack/androidx/releases/test. Their version numbers differ.
dependencies {
    androidTestImplementation("androidx.test:runner:<compatible-version>")
    androidTestImplementation("androidx.test:rules:<compatible-version>")
    androidTestImplementation("androidx.test:core:<compatible-version>")
    androidTestImplementation("androidx.test.ext:junit:<compatible-version>")
    androidTestUtil("androidx.test:orchestrator:<compatible-version>")
}
```

---

## Performance Impact and Mitigation

### Overhead Measurement

Orchestrator runs each test in its own instrumentation process, so suite time ≈ baseline suite
time + (number of tests × per-test overhead). `clearPackageData` adds an app-data wipe to each
test's overhead. Measure the per-test overhead on your own suite (run a sample with and without
Orchestrator) before sizing shards; do not budget from a generic figure.

### Mitigation Strategies

- Size shards against measured runner capacity; extra devices can cause provisioning timeouts.
- Use ATD only when the required API and system surface are supported, and hardware rendering is irrelevant.
- Keep JVM tests outside Orchestrator; it isolates instrumented invocations.
- Use `clearPackageData` when process isolation leaves persistent state behind; compare its overhead on the suite.
- Prefer the managed-device snapshot lifecycle over custom restoration scripts.

### Gradle Task Separation

```kotlin
// Separate tasks for unit vs instrumented tests
// Unit tests: no orchestrator overhead
// ./gradlew testDebugUnitTest

// Instrumented tests with orchestrator
// ./gradlew connectedDebugAndroidTest
```

**Checklist -- Orchestrator Setup:**

- [ ] Orchestrator dependency added as `androidTestUtil`
- [ ] `execution = "ANDROIDX_TEST_ORCHESTRATOR"` in `testOptions`
- [ ] `clearPackageData` enabled for tests that modify state
- [ ] Animations disabled in test options or via adb
- [ ] Version alignment across all AndroidX Test dependencies
- [ ] Sharding sized to measured runner capacity
- [ ] Crash recovery verified (one crashing test does not block others)

---

## Related Resources

- [espresso-patterns.md](espresso-patterns.md) -- Espresso testing patterns
- [compose-testing.md](compose-testing.md) -- Jetpack Compose test setup
- [gradle-managed-devices.md](gradle-managed-devices.md) -- Managed device configuration
- [android-ci-optimization.md](android-ci-optimization.md) -- CI pipeline optimization
- [uiautomator.md](uiautomator.md) -- System-level UI testing
