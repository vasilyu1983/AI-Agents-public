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

Without Orchestrator, all tests run in a single instrumentation process. If one test crashes, all subsequent tests fail. With Orchestrator, each test runs in its own instrumentation invocation.

```text
WITHOUT ORCHESTRATOR:
┌─────────────────────────────────────┐
│ Single Instrumentation Process      │
│ Test A → Test B → CRASH → Test C ✗  │
│                          Test D ✗   │
│                          Test E ✗   │
└─────────────────────────────────────┘
All remaining tests lost after crash.

WITH ORCHESTRATOR:
┌──────────────────┐
│ Orchestrator APK │  (controls execution)
└────────┬─────────┘
         ├── Instrumentation 1 → Test A ✓
         ├── Instrumentation 2 → Test B ✓
         ├── Instrumentation 3 → Test C CRASH (isolated)
         ├── Instrumentation 4 → Test D ✓
         └── Instrumentation 5 → Test E ✓
```

### Benefits

| Benefit                   | Description                                          |
|---------------------------|------------------------------------------------------|
| Crash isolation           | One test crash does not affect other tests            |
| Shared state elimination  | Each test starts with a clean process                 |
| Reliable results          | No flakes from leaked state between tests             |
| Per-test data clearing    | Optional `clearPackageData` between tests             |
| Better CI reporting       | Crashed tests reported individually, not as batch     |

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
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test:rules:1.6.1")
    androidTestUtil("androidx.test:orchestrator:1.5.1")
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
                    systemImageSource = "aosp-atd"
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
| Performance-sensitive CI           | No               | Reduces per-test overhead ~2-5s |

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

```bash
# Shard 1 of 3
adb shell am instrument -w \
  -e numShards 3 \
  -e shardIndex 0 \
  -e clearPackageData true \
  androidx.test.orchestrator/androidx.test.orchestrator.AndroidTestOrchestrator

# Shard 2 of 3
adb shell am instrument -w \
  -e numShards 3 \
  -e shardIndex 1 \
  -e clearPackageData true \
  androidx.test.orchestrator/androidx.test.orchestrator.AndroidTestOrchestrator

# Shard 3 of 3
adb shell am instrument -w \
  -e numShards 3 \
  -e shardIndex 2 \
  -e clearPackageData true \
  androidx.test.orchestrator/androidx.test.orchestrator.AndroidTestOrchestrator
```

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
./gradlew pixel6api34GroupDebugAndroidTest \
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
# Run only smoke tests with Orchestrator
adb shell am instrument -w \
  -e annotation com.example.app.SmokeSuite \
  -e clearPackageData true \
  androidx.test.orchestrator/androidx.test.orchestrator.AndroidTestOrchestrator
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
import androidx.compose.ui.test.junit4.createAndroidComposeRule

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

    @get:Rule(order = 1)
    val composeRule = createAndroidComposeRule<MainActivity>()

    @get:Rule(order = 2)
    val dbRule = DatabaseSeedRule(::seed, ::clean)
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

```kotlin
@Before
fun setLocale() {
    val locale = Locale("es", "ES")
    Locale.setDefault(locale)

    val config = InstrumentationRegistry.getInstrumentation()
        .targetContext.resources.configuration
    config.setLocale(locale)

    InstrumentationRegistry.getInstrumentation()
        .targetContext.createConfigurationContext(config)
}
```

### Managing WiFi and Network

```kotlin
// Requires android.permission.CHANGE_WIFI_STATE in androidTest manifest
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

```bash
gcloud firebase test android run \
  --type instrumentation \
  --app app-debug.apk \
  --test app-debug-androidTest.apk \
  --use-orchestrator \
  --environment-variables clearPackageData=true \
  --device model=Pixel6,version=34,locale=en,orientation=portrait \
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
| `--device`         | model=Pixel6,version=34  | Target device profile       |

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
// All AndroidX Test dependencies should use compatible versions
dependencies {
    androidTestImplementation("androidx.test:runner:1.6.2")
    androidTestImplementation("androidx.test:rules:1.6.1")
    androidTestImplementation("androidx.test:core:1.6.1")
    androidTestImplementation("androidx.test.ext:junit:1.2.1")
    androidTestUtil("androidx.test:orchestrator:1.5.1")
}
```

---

## Performance Impact and Mitigation

### Overhead Measurement

| Configuration                      | Overhead per Test | 100-Test Suite |
|------------------------------------|-------------------|----------------|
| No Orchestrator                    | ~0s               | ~5 min         |
| Orchestrator (no clearPackageData) | ~2-3s             | ~9 min         |
| Orchestrator + clearPackageData    | ~4-6s             | ~13 min        |

### Mitigation Strategies

```text
1. SHARD AGGRESSIVELY
   Split tests across 4-8 parallel emulators to offset per-test overhead.

2. USE ATD IMAGES
   Automated Test Devices boot faster and have less overhead.
   systemImageSource = "aosp-atd"

3. SELECTIVE ORCHESTRATOR
   Use Orchestrator only for integration/E2E tests.
   Run unit tests without Orchestrator (they are process-isolated anyway).

4. MINIMIZE clearPackageData
   Only enable for tests that genuinely need clean state.
   Handle cleanup in @Before/@After for lightweight state resets.

5. EMULATOR SNAPSHOTS
   Boot emulator once, snapshot, restore per shard.
   Saves 30-60s per shard start.
```

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
- [ ] Sharding configured for CI (4+ shards for large suites)
- [ ] Crash recovery verified (one crashing test does not block others)

---

## Related Resources

- [espresso-patterns.md](espresso-patterns.md) -- Espresso testing patterns
- [compose-testing.md](compose-testing.md) -- Jetpack Compose test setup
- [gradle-managed-devices.md](gradle-managed-devices.md) -- Managed device configuration
- [android-ci-optimization.md](android-ci-optimization.md) -- CI pipeline optimization
- [uiautomator.md](uiautomator.md) -- System-level UI testing
