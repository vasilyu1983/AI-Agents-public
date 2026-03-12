# Android CI Optimization

Build and test pipeline optimization for Android projects in continuous integration.

## Contents

- [Build Caching Strategies](#build-caching-strategies)
- [Test Sharding Across CI Nodes](#test-sharding-across-ci-nodes)
- [ATD vs Full Emulator Images](#atd-vs-full-emulator-images)
- [Gradle Managed Devices in CI](#gradle-managed-devices-in-ci)
- [Emulator Snapshot Caching](#emulator-snapshot-caching)
- [Parallel Test Execution](#parallel-test-execution)
- [Flaky Test Quarantine](#flaky-test-quarantine)
- [Test Impact Analysis](#test-impact-analysis)
- [CI Provider Comparison](#ci-provider-comparison)
- [Artifact Management](#artifact-management)
- [Build Time Budgets](#build-time-budgets)
- [Related Resources](#related-resources)

---

## Build Caching Strategies

### Gradle Build Cache

```kotlin
// settings.gradle.kts
buildCache {
    local {
        isEnabled = true
        directory = File(rootDir, ".gradle/build-cache")
    }
    remote<HttpBuildCache> {
        url = uri("https://cache.example.com/cache/")
        isPush = System.getenv("CI") != null
        credentials {
            username = System.getenv("CACHE_USER") ?: ""
            password = System.getenv("CACHE_PASS") ?: ""
        }
    }
}
```

### Dependency Caching

```yaml
# GitHub Actions: cache Gradle dependencies
- name: Cache Gradle
  uses: actions/cache@v4
  with:
    path: |
      ~/.gradle/caches
      ~/.gradle/wrapper
      ~/.android/build-cache
    key: gradle-${{ runner.os }}-${{ hashFiles('**/*.gradle*', '**/gradle-wrapper.properties', '**/libs.versions.toml') }}
    restore-keys: |
      gradle-${{ runner.os }}-
```

### Configuration Cache

```properties
# gradle.properties
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn

# Parallel execution
org.gradle.parallel=true
org.gradle.workers.max=4

# Daemon tuning
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError
org.gradle.daemon=true
```

### Cache Hit Rate Monitoring

```bash
# Check cache statistics after build
./gradlew assembleDebug --scan
# Build scan shows cache hit/miss per task

# Quick local check
./gradlew assembleDebug --build-cache --info 2>&1 | grep -c "FROM-CACHE"
```

---

## Test Sharding Across CI Nodes

### Strategy Comparison

| Strategy        | Distribution Method       | Pros                        | Cons                      |
|-----------------|---------------------------|-----------------------------|---------------------------|
| Count-based     | Equal test count per shard| Simple                      | Uneven execution time     |
| Time-based      | Balance by historical time| Optimal parallelism         | Needs timing data         |
| Module-based    | One module per shard      | Natural boundaries          | Uneven if modules differ  |
| Annotation-based| By test category          | Logical grouping            | Manual maintenance        |

### GitHub Actions Matrix Sharding

```yaml
jobs:
  instrumented-tests:
    strategy:
      fail-fast: false
      matrix:
        shard: [0, 1, 2, 3]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run shard ${{ matrix.shard }}
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          target: aosp_atd
          arch: x86_64
          script: |
            adb shell am instrument -w \
              -e numShards 4 \
              -e shardIndex ${{ matrix.shard }} \
              -e clearPackageData true \
              androidx.test.orchestrator/androidx.test.orchestrator.AndroidTestOrchestrator

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results-shard-${{ matrix.shard }}
          path: '**/build/outputs/androidTest-results/'

  merge-results:
    needs: instrumented-tests
    runs-on: ubuntu-latest
    steps:
      - name: Download all shard results
        uses: actions/download-artifact@v4
        with:
          pattern: test-results-shard-*
          merge-multiple: true

      - name: Merge and publish
        run: |
          # Merge JUnit XML files
          npx junit-merge -d ./test-results -o merged-results.xml
```

---

## ATD vs Full Emulator Images

Automated Test Devices (ATD) are stripped-down emulator images optimized for testing.

| Feature               | ATD (`aosp-atd`)         | Full (`google_apis`)       |
|-----------------------|--------------------------|----------------------------|
| Boot time             | ~15 seconds              | ~45-90 seconds             |
| Image size            | ~600 MB                  | ~1.2 GB                    |
| Google Play Services  | No                       | Yes (google_apis_playstore)|
| System apps           | Minimal                  | Full set                   |
| Camera, sensors       | Stubbed                  | Emulated                   |
| Best for              | Unit + integration tests | E2E, Google Sign-In        |

### Selecting ATD in Gradle

```kotlin
android {
    testOptions {
        managedDevices {
            localDevices {
                create("pixel6api34atd") {
                    device = "Pixel 6"
                    apiLevel = 34
                    systemImageSource = "aosp-atd"  // ATD image
                }
                create("pixel6api34full") {
                    device = "Pixel 6"
                    apiLevel = 34
                    systemImageSource = "google_apis"  // Full image
                }
            }
        }
    }
}
```

---

## Gradle Managed Devices in CI

Gradle Managed Devices (GMD) automate emulator lifecycle -- download, create, boot, test, shutdown.

### CI Configuration

```yaml
# GitHub Actions with GMD
jobs:
  android-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-java@v4
        with:
          distribution: 'zulu'
          java-version: '17'

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' \
            | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Cache emulator images
        uses: actions/cache@v4
        with:
          path: ~/.android/avd
          key: avd-${{ hashFiles('**/build.gradle.kts') }}

      - name: Run managed device tests
        run: ./gradlew pixel6api34atdDebugAndroidTest

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: '**/build/outputs/managed_device_android_test_additional_output/'
```

### GMD Groups for Multi-Device Testing

```kotlin
android {
    testOptions {
        managedDevices {
            localDevices {
                create("pixel6api34") {
                    device = "Pixel 6"
                    apiLevel = 34
                    systemImageSource = "aosp-atd"
                }
                create("pixelTabletApi34") {
                    device = "Pixel Tablet"
                    apiLevel = 34
                    systemImageSource = "aosp-atd"
                }
            }
            groups {
                create("allDevices") {
                    targetDevices.addAll(
                        devices["pixel6api34"],
                        devices["pixelTabletApi34"],
                    )
                }
            }
        }
    }
}
```

```bash
# Run on all devices in the group
./gradlew allDevicesGroupDebugAndroidTest
```

---

## Emulator Snapshot Caching

### Snapshot Strategy

```bash
# 1. Boot emulator and wait for ready
emulator -avd Pixel_6_API_34 -no-window -no-audio -gpu swiftshader_indirect &
adb wait-for-device
adb shell getprop sys.boot_completed | grep 1

# 2. Disable animations
adb shell settings put global window_animation_scale 0
adb shell settings put global transition_animation_scale 0
adb shell settings put global animator_duration_scale 0

# 3. Save snapshot
adb emu avd snapshot save ci-ready

# 4. Kill emulator
adb emu kill

# 5. On subsequent CI runs, load snapshot
emulator -avd Pixel_6_API_34 -no-window -no-audio -snapshot ci-ready -no-snapshot-save &
```

### CI Cache for Snapshots

```yaml
- name: Cache AVD snapshot
  uses: actions/cache@v4
  with:
    path: |
      ~/.android/avd/Pixel_6_API_34.avd/snapshots/ci-ready
    key: avd-snapshot-pixel6-api34-${{ hashFiles('scripts/setup-emulator.sh') }}
```

---

## Parallel Test Execution

### Gradle Parallel Testing

```kotlin
android {
    testOptions {
        // Run test classes in parallel within a single device
        execution = "ANDROIDX_TEST_ORCHESTRATOR"

        // For unit tests
        unitTests.all {
            it.maxParallelForks = Runtime.getRuntime().availableProcessors()
        }
    }
}
```

### Multi-Emulator Parallel Execution

```bash
#!/bin/bash
# Launch multiple emulators and run shards in parallel

SHARD_COUNT=4

for i in $(seq 0 $((SHARD_COUNT - 1))); do
  PORT=$((5554 + i * 2))
  emulator -avd Pixel_6_API_34 -port "$PORT" -no-window -no-audio &
done

# Wait for all emulators
for i in $(seq 0 $((SHARD_COUNT - 1))); do
  PORT=$((5554 + i * 2))
  adb -s "emulator-$PORT" wait-for-device
  adb -s "emulator-$PORT" shell 'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 1; done'
done

# Run shards in parallel
for i in $(seq 0 $((SHARD_COUNT - 1))); do
  PORT=$((5554 + i * 2))
  adb -s "emulator-$PORT" shell am instrument -w \
    -e numShards "$SHARD_COUNT" \
    -e shardIndex "$i" \
    com.example.app.test/androidx.test.runner.AndroidJUnitRunner &
done

wait
```

---

## Flaky Test Quarantine

### Detection

```kotlin
// Custom test rule that retries flaky tests
class RetryRule(private val maxRetries: Int = 2) : TestRule {
    override fun apply(base: Statement, description: Description): Statement {
        return object : Statement() {
            override fun evaluate() {
                var lastException: Throwable? = null
                for (attempt in 0..maxRetries) {
                    try {
                        base.evaluate()
                        return // success
                    } catch (e: Throwable) {
                        lastException = e
                        if (attempt < maxRetries) {
                            println("Test ${description.methodName} failed, retrying (${attempt + 1}/$maxRetries)")
                        }
                    }
                }
                throw lastException!!
            }
        }
    }
}
```

### Quarantine Strategy

```kotlin
// Mark flaky tests for quarantine
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class Quarantined(val reason: String, val ticket: String)

// Usage
@Quarantined(reason = "Flaky on API 34", ticket = "JIRA-1234")
@Test
fun intermittent_animation_test() { /* ... */ }
```

```bash
# Run excluding quarantined tests (main CI)
adb shell am instrument -w \
  -e notAnnotation com.example.app.Quarantined \
  com.example.app.test/androidx.test.runner.AndroidJUnitRunner

# Separate job: run only quarantined tests (non-blocking)
adb shell am instrument -w \
  -e annotation com.example.app.Quarantined \
  com.example.app.test/androidx.test.runner.AndroidJUnitRunner
```

---

## Test Impact Analysis

Run only tests affected by code changes to reduce CI time.

### Module-Level Impact

```bash
#!/bin/bash
# Detect changed modules and run only their tests

CHANGED_FILES=$(git diff --name-only origin/main...HEAD)

MODULES_TO_TEST=()
for file in $CHANGED_FILES; do
  module=$(echo "$file" | cut -d'/' -f1-2)
  if [[ -f "$module/build.gradle.kts" ]]; then
    MODULES_TO_TEST+=("$module")
  fi
done

# Deduplicate
UNIQUE_MODULES=($(echo "${MODULES_TO_TEST[@]}" | tr ' ' '\n' | sort -u))

for module in "${UNIQUE_MODULES[@]}"; do
  echo "Running tests for $module"
  ./gradlew ":${module//\//:}:connectedDebugAndroidTest"
done
```

### Class-Level Impact with Affected Module Detection

```yaml
# GitHub Actions: conditional test execution
- name: Detect changes
  id: changes
  uses: dorny/paths-filter@v3
  with:
    filters: |
      feature-auth:
        - 'feature/auth/**'
      feature-payments:
        - 'feature/payments/**'
      core:
        - 'core/**'

- name: Run auth tests
  if: steps.changes.outputs.feature-auth == 'true' || steps.changes.outputs.core == 'true'
  run: ./gradlew :feature:auth:connectedDebugAndroidTest

- name: Run payments tests
  if: steps.changes.outputs.feature-payments == 'true' || steps.changes.outputs.core == 'true'
  run: ./gradlew :feature:payments:connectedDebugAndroidTest
```

---

## CI Provider Comparison

| Feature                   | GitHub Actions | CircleCI       | Bitrise         |
|---------------------------|----------------|----------------|-----------------|
| **KVM support**           | Linux runners  | Machine exec   | Dedicated stacks|
| **Emulator caching**      | actions/cache  | Docker layer   | Built-in cache  |
| **Managed devices**       | Yes (KVM req)  | Yes (KVM req)  | Yes             |
| **Android-specific tools**| Community actions| Android orb   | Native steps    |
| **Max parallel jobs**     | 20 (default)   | Depends on plan| Depends on plan |
| **macOS runners**         | Available       | Available      | Available       |
| **Free tier**             | 2000 min/month | 6000 min/month | 150 builds/month|
| **Setup complexity**      | Low            | Medium         | Low             |

### GitHub Actions Recommended Config

```yaml
jobs:
  unit-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'zulu', java-version: '17' }
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew testDebugUnitTest
      - uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Unit Tests
          path: '**/build/test-results/**/*.xml'
          reporter: java-junit

  instrumented-test:
    runs-on: ubuntu-latest
    needs: unit-test
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-java@v4
        with: { distribution: 'zulu', java-version: '17' }
      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' \
            | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules && sudo udevadm trigger --name-match=kvm
      - uses: gradle/actions/setup-gradle@v4
      - run: ./gradlew pixel6api34atdDebugAndroidTest
```

---

## Artifact Management

### Test Reports

```yaml
# Upload test results and screenshots
- name: Upload test reports
  if: always()
  uses: actions/upload-artifact@v4
  with:
    name: test-reports
    path: |
      **/build/reports/androidTests/
      **/build/outputs/androidTest-results/
      **/build/outputs/managed_device_android_test_additional_output/
    retention-days: 14
```

### Screenshot Artifacts on Failure

```kotlin
// Custom rule to capture screenshots on test failure
class ScreenshotOnFailureRule : TestWatcher() {
    override fun failed(e: Throwable?, description: Description) {
        val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())
        val dir = File(
            InstrumentationRegistry.getInstrumentation().targetContext.filesDir,
            "test-screenshots"
        )
        dir.mkdirs()
        device.takeScreenshot(File(dir, "${description.methodName}.png"))
    }
}
```

---

## Build Time Budgets

| Phase                    | Target    | Optimization Lever              |
|--------------------------|-----------|---------------------------------|
| Checkout + setup         | < 1 min   | Shallow clone, cached deps      |
| Compilation              | < 3 min   | Build cache, incremental builds |
| Unit tests               | < 5 min   | Parallel forks, skip unchanged  |
| Emulator boot            | < 30 sec  | ATD images, snapshot restore    |
| Instrumented tests       | < 10 min  | Sharding (4+ shards)            |
| Artifact upload          | < 1 min   | Compress, selective upload      |
| **Total pipeline**       | **< 20 min** | All of the above             |

**Checklist -- CI Optimization:**

- [ ] Gradle build cache enabled (local + remote)
- [ ] Dependencies cached between CI runs
- [ ] Configuration cache enabled
- [ ] ATD emulator images used for non-Google-API tests
- [ ] Tests sharded across 4+ parallel nodes
- [ ] Emulator snapshots cached
- [ ] Flaky tests quarantined to non-blocking job
- [ ] Test impact analysis skips unaffected modules
- [ ] Build time budget defined and tracked
- [ ] Test reports and failure screenshots uploaded as artifacts

---

## Related Resources

- [test-orchestrator-patterns.md](test-orchestrator-patterns.md) -- Test isolation with Orchestrator
- [gradle-managed-devices.md](gradle-managed-devices.md) -- Managed device configuration
- [screenshot-testing.md](screenshot-testing.md) -- Visual regression in CI
- [espresso-patterns.md](espresso-patterns.md) -- Espresso test patterns
- [compose-testing.md](compose-testing.md) -- Compose testing setup
