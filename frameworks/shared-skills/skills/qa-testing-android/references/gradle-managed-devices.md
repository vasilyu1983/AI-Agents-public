# Build-Managed Devices (GMD)

Build-managed devices automate emulator provisioning for CI and repeatable Android test runs.

**Official documentation**: [Scale your tests with build-managed devices](https://developer.android.com/studio/test/managed-devices)

## Table of Contents

- [Quick Start](#quick-start)
- [Define devices in `build.gradle.kts`](#define-devices-in-buildgradlekts)
- [Run tests](#run-tests)
- [Discover generated tasks (names vary by AGP + variants)](#discover-generated-tasks-names-vary-by-agp-variants)
- [Typical per-device and group runs](#typical-per-device-and-group-runs)
- [Device Groups](#device-groups)
- [System Image Sources](#system-image-sources)
- [Sharding](#sharding)
- [gradle.properties](#gradleproperties)
- [CI Integration](#ci-integration)
- [GitHub Actions](#github-actions)
- [Key CI Requirements](#key-ci-requirements)
- [Emulator Snapshots And Result Caching](#emulator-snapshots-and-result-caching)
- [Device Matrix Strategy](#device-matrix-strategy)
- [Troubleshooting](#troubleshooting)
- [Related](#related)

## Quick Start

### Define devices in `build.gradle.kts`

```kotlin
android {
    testOptions {
        managedDevices {
            localDevices {
                create("pixel2api30Atd") {
                    device = "Pixel 2"
                    apiLevel = 30
                    systemImageSource = "aosp-atd"
                }
                create("pixelTabletApi35") {
                    device = "Pixel Tablet"
                    apiLevel = 35
                    systemImageSource = "google"
                }
            }
        }
    }
}
```

Use ATD where hardware rendering is not required. Use standard `google` or `aosp` images when the test depends on Google services or hardware-rendered fidelity.

### Run tests

```bash
# Discover generated tasks (names vary by AGP + variants)
./gradlew tasks --all | rg "AndroidTest|Group|ManagedDevices"

# Typical per-device and group runs
./gradlew pixel2api30AtdDebugAndroidTest
./gradlew phoneMatrixGroupDebugAndroidTest
```

If your CI runner does not support hardware rendering, pass:

```bash
-Pandroid.testoptions.manageddevices.emulator.gpu=swiftshader_indirect
```

That flag is explicitly called out by the current Android Developers guide for environments such as GitHub Actions.

## Device Groups

```kotlin
android {
    testOptions {
        managedDevices {
            localDevices {
                create("pixel6api35") {
                    device = "Pixel 2"
                    apiLevel = 30
                    systemImageSource = "aosp-atd"
                }
                create("pixelTabletApi35") {
                    device = "Pixel Tablet"
                    apiLevel = 35
                    systemImageSource = "google"
                }
            }

            groups {
                create("phoneMatrix") {
                    targetDevices.addAll(
                        devices["pixel6api35"],
                        devices["pixelTabletApi35"]
                    )
                }
            }
        }
    }
}
```

```bash
./gradlew phoneMatrixGroupDebugAndroidTest
```

## System Image Sources

| Source | Description | Use Case |
|--------|-------------|----------|
| `aosp-atd` | Android Test Device image | Fast CI for non-rendering-sensitive tests |
| `google-atd` | Google APIs ATD image | Fast CI with Google APIs where supported |
| `aosp` | Standard AOSP image | General emulator coverage |
| `google` | Standard Google APIs image | Google services or rendering-sensitive flows |

What ATD changes:

- Reduces CPU and memory usage
- Removes preinstalled apps that are not useful for testing
- Disables some background services
- Disables hardware rendering

ATD images are currently only available for API level 30 (`aosp-atd`, `google-atd`). For suites that need to run on API 35 or 36, use standard `google` or `aosp` images. Do not use ATD for screenshot assertions that depend on hardware-rendered output.

## Sharding

Build-managed devices support sharding through Gradle properties:

```properties
# gradle.properties
android.experimental.androidTest.numManagedDeviceShards=2
```

Each shard provisions another virtual device instance per managed device in the run, so shard counts multiply infrastructure cost quickly.

## CI Integration

### GitHub Actions

```yaml
name: Android Tests

on: [push, pull_request]

jobs:
  instrumented-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6

      - uses: actions/setup-java@v5
        with:
          java-version: '17'
          distribution: 'temurin'

      - uses: gradle/actions/setup-gradle@v5

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Run managed device tests
        run: ./gradlew pixel2api30AtdDebugAndroidTest -Pandroid.testoptions.manageddevices.emulator.gpu=swiftshader_indirect

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: android-test-results
          path: |
            **/build/reports/androidTests/
            **/build/outputs/managed_device_android_test_additional_output/
```

### Key CI Requirements

1. KVM acceleration on Linux runners.
2. Enough RAM for the number of devices and shards you provision.
3. Current Android Emulator and system images.

## Emulator Snapshots And Result Caching

The current build-managed devices guide calls out three platform-level benefits:

- Emulator snapshots improve startup time and restore devices to a clean state between tests.
- Device lifecycle is controlled by the Android Gradle Plugin.
- Gradle caches test results and reruns only tests likely to produce different results.

Do not rebuild your own snapshot cache strategy unless you have measured a clear gap in the built-in behavior.

For failure artifacts, prefer Android Test Retention:

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

This works with UTP and gives you failure-state snapshots instead of only logs.

## Device Matrix Strategy

- PRs: one fast phone ATD plus one rendering-sensitive or Google-services path only if needed.
- Nightly: min API, target API, tablet, and foldable or expanded-layout coverage where relevant.
- Release: real-device or device-farm validation for checkout, login, camera, or OEM-sensitive journeys.

## Troubleshooting

| Issue | Preferred fix |
|-------|---------------|
| Emulator fails on GitHub Actions | Add the `swiftshader_indirect` property and verify KVM is enabled |
| Slow CI boot | Use ATD for non-rendering-sensitive suites |
| Too many timeout errors | Reduce shard count, device count, or both |
| Missing Google APIs behavior | Switch that suite from `aosp-atd` to `google` or `google-atd` |
| Screenshot diffs look wrong on ATD | Use a non-ATD image or JVM screenshot tooling |

## Related

- [Android CI Optimization](android-ci-optimization.md)
- [AndroidX Test Orchestrator](test-orchestrator-patterns.md)
- [Screenshot Testing](screenshot-testing.md)
