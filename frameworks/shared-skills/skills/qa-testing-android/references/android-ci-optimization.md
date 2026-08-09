# Android CI Optimization

Build and test pipeline optimization for Android projects in continuous integration.

## Contents

- [Build Caching Strategies](#build-caching-strategies)
- [Test Sharding Across CI Nodes](#test-sharding-across-ci-nodes)
- [ATD vs Standard Images](#atd-vs-standard-images)
- [Build-Managed Devices In CI](#build-managed-devices-in-ci)
- [Failure Snapshots And Artifacts](#failure-snapshots-and-artifacts)
- [Parallel Test Execution](#parallel-test-execution)
- [Flaky Test Quarantine](#flaky-test-quarantine)
- [Test Impact Analysis](#test-impact-analysis)
- [CI Provider Comparison](#ci-provider-comparison)
- [Build Time Budgets](#build-time-budgets)
- [Related Resources](#related-resources)

## Build Caching Strategies

### Gradle setup on GitHub Actions

Prefer the official Gradle action over hand-rolled `actions/cache` snippets:

```yaml
- uses: gradle/actions/setup-gradle@v5
```

This action is the current Gradle-recommended setup path and handles wrapper validation, dependency caching, and Gradle-user-home optimization more safely than copy-pasted cache paths.

### Configuration cache

```properties
# gradle.properties
org.gradle.configuration-cache=true
org.gradle.configuration-cache.problems=warn
org.gradle.parallel=true
org.gradle.workers.max=4
org.gradle.jvmargs=-Xmx4g -XX:+HeapDumpOnOutOfMemoryError
```

Measure configuration-cache compatibility before turning it on globally in a multi-module Android repo.

### Cache observability

```bash
./gradlew assembleDebug --scan
./gradlew assembleDebug --build-cache --info 2>&1 | grep -c "FROM-CACHE"
```

## AGP 9.x Migration Notes

AGP 9.0 (January 2026, current stable series 9.2.x) introduced breaking changes that affect CI setups:

- Built-in Kotlin support is enabled by default — remove explicit `org.jetbrains.kotlin.android` plugin application where AGP 9 already handles it.
- `CommonExtension` parameterization removed — DSL access moves to `ApplicationExtension`, `LibraryExtension`, etc. Update any shared Gradle convention plugins that use `CommonExtension` directly.
- `applicationVariants` and similar APIs are deprecated in favor of `androidComponents`. Migrate before AGP 10.0 (mid-2026) when opt-out is removed.
- AGP 9.2 requires Gradle 8.11+. Verify your wrapper version before upgrading.
- Roborazzi 1.55+ and AGP 9.0 compatibility: Roborazzi updated its Gradle plugin for AGP 9.0/9.1 in late 2025; pin to 1.55+ when using AGP 9.x.

## Test Sharding Across CI Nodes

### Build-managed device sharding

Prefer official build-managed-device sharding for homogeneous emulator parallelism:

```properties
# gradle.properties
android.experimental.androidTest.numManagedDeviceShards=2
```

### Manual matrix sharding

Use manual shard matrices only when you need strict CI fan-out control or non-GMD infrastructure:

```yaml
jobs:
  instrumented-tests:
    strategy:
      fail-fast: false
      matrix:
        shard: [0, 1, 2, 3]
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-java@v5
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: gradle/actions/setup-gradle@v5
      - name: Run shard ${{ matrix.shard }}
        run: |
          ./gradlew connectedDebugAndroidTest \
            -Pandroid.testInstrumentationRunnerArguments.numShards=4 \
            -Pandroid.testInstrumentationRunnerArguments.shardIndex=${{ matrix.shard }}
```

## ATD vs Standard Images

Use ATD when:

- you care about speed and determinism
- you do not need hardware-rendered screenshots
- you do not need the full Google-services stack
- API level 30 is sufficient (ATD images are only available at API 30; for API 35/36 suites use standard `google` or `aosp` images)

Use standard `google` or `aosp` images when:

- your tests depend on Google APIs
- hardware-rendered visuals matter
- ATD image constraints block realistic behavior

The current Android Developers guide also notes that ATD disables hardware rendering, so fidelity-sensitive screenshot tests should not run there.

## Build-Managed Devices In CI

```yaml
jobs:
  android-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-java@v5
        with:
          distribution: 'temurin'
          java-version: '17'
      - uses: gradle/actions/setup-gradle@v5
      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm
      - name: Run managed device tests
        run: ./gradlew pixel6api35DebugAndroidTest -Pandroid.testoptions.manageddevices.emulator.gpu=swiftshader_indirect
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: android-test-artifacts
          path: |
            **/build/reports/androidTests/
            **/build/outputs/androidTest-results/
            **/build/outputs/managed_device_android_test_additional_output/
```

Notes:

- `actions/checkout@v6`, `actions/setup-java@v5`, and `gradle/actions/setup-gradle@v5` are current majors.
- `swiftshader_indirect` is still what the current build-managed-devices guide tells you to pass on GitHub Actions and other servers without hardware rendering support.

## Failure Snapshots And Artifacts

Prefer Android Test Retention over custom emulator snapshot shell scripts:

```kotlin
android {
    testOptions {
        emulatorSnapshots {
            enableForTestFailures = true
            maxSnapshotsForTestFailures = 2
            compressSnapshots = false
        }
    }
}
```

This integrates with UTP and gives you emulator-state snapshots on test failure.

Upload at least:

- Android test HTML reports
- managed-device additional output
- screenshot or diff reports
- logcat or failure screenshots if your framework captures them

## Parallel Test Execution

### Unit tests

```kotlin
android {
    testOptions {
        unitTests.all {
            it.maxParallelForks = Runtime.getRuntime().availableProcessors()
        }
    }
}
```

### Instrumented tests

Prefer:

- more managed-device shards for homogeneous suites
- more device profiles for compatibility coverage

Avoid mixing both aggressively unless you have measured the runner capacity.

## Flaky Test Quarantine

Use quarantine as a reporting and ownership mechanism, not as a permanent hiding place.

```kotlin
@Target(AnnotationTarget.CLASS, AnnotationTarget.FUNCTION)
@Retention(AnnotationRetention.RUNTIME)
annotation class Quarantined(val reason: String, val ticket: String)
```

```bash
# Main CI: exclude quarantined tests
adb shell am instrument -w \
  -e notAnnotation com.example.app.Quarantined \
  com.example.app.test/androidx.test.runner.AndroidJUnitRunner
```

Pair quarantine with a non-blocking job plus ticket ownership.

## Test Impact Analysis

Use test impact analysis only after the baseline suite is already deterministic. Impact-based skipping on top of flaky tests creates false confidence.

At minimum:

- map changed modules to their local unit and UI tests
- rerun core smoke suites regardless of impact
- keep screenshot and device-compatibility suites separate from fast smoke suites

## CI Provider Comparison

| Feature | GitHub Actions | CircleCI | Bitrise |
|---------|----------------|----------|---------|
| KVM support | Linux runners | Machine executors | Android-focused stacks |
| Managed-device support | Yes | Yes | Yes |
| Best default docs for Android examples | Strong | Medium | Medium |
| Setup complexity | Low | Medium | Low |

Prefer GitHub Actions examples in shared skill docs unless a project has standardized elsewhere.

## Build Time Budgets

| Phase | Target | Optimization Lever |
|-------|--------|--------------------|
| Checkout and setup | < 2 min | current actions, shallow fetch where safe |
| Compilation | < 4 min | build cache, incremental builds |
| Unit tests | < 5 min | parallel forks, impact analysis |
| Managed-device startup | < 1 min | ATD, built-in snapshots |
| Instrumented tests | < 10 min | shards, focused matrix |
| Total PR pipeline | < 20 min | all of the above |

## Related Resources

- [Build-Managed Devices](gradle-managed-devices.md)
- [AndroidX Test Orchestrator](test-orchestrator-patterns.md)
- [Screenshot Testing](screenshot-testing.md)
- [Compose Testing](compose-testing.md)
