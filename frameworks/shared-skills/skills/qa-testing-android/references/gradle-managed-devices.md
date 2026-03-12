# Gradle Managed Devices (GMD)

Gradle Managed Devices automate emulator provisioning for CI/CD Android testing. No pre-configured emulator images required.

**Official Documentation**: [developer.android.com/studio/test/gradle-managed-devices](https://developer.android.com/studio/test/gradle-managed-devices)

## Quick Start

### Define Devices in build.gradle.kts

```kotlin
android {
    testOptions {
        managedDevices {
            localDevices {
                create("pixel6api34") {
                    device = "Pixel 6"
                    apiLevel = 34
                    systemImageSource = "aosp-atd"  // Android Test Device image
                }
                create("pixel4api30") {
                    device = "Pixel 4"
                    apiLevel = 30
                    systemImageSource = "aosp"
                }
            }
        }
    }
}
```

### Run Tests

```bash
# Discover generated tasks (names vary by AGP + variants)
./gradlew tasks --all | rg "AndroidTest|managedDevice|Group"

# Typical patterns (Debug variant)
./gradlew pixel6api34DebugAndroidTest
./gradlew phoneMatrixGroupDebugAndroidTest
./gradlew allDevicesDebugAndroidTest
```

## Device Groups

Test across multiple configurations simultaneously:

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
                create("pixel4api30") {
                    device = "Pixel 4"
                    apiLevel = 30
                    systemImageSource = "aosp-atd"
                }
                create("smallPhone") {
                    device = "Nexus 5"
                    apiLevel = 30
                    systemImageSource = "aosp-atd"
                }
            }

            groups {
                create("phoneMatrix") {
                    targetDevices.addAll(
                        devices["pixel6api34"],
                        devices["pixel4api30"],
                        devices["smallPhone"]
                    )
                }
            }
        }
    }
}
```

```bash
# Run on all devices in group
./gradlew phoneMatrixGroupDebugAndroidTest
```

## System Image Sources

| Source | Description | Use Case |
|--------|-------------|----------|
| `aosp-atd` | Android Test Device (headless, fast) | CI/CD, instrumentation tests |
| `aosp` | Standard AOSP image | General testing |
| `google` | Google APIs included | Tests requiring Google services |
| `google-atd` | Google ATD image | CI/CD with Google APIs |

**ATD images** are optimized for testing:
- Faster boot times
- Lower resource usage
- No UI rendering overhead

## CI/CD Integration

### GitHub Actions

```yaml
name: Android Tests

on: [push, pull_request]

jobs:
  instrumented-tests:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Enable KVM
        run: |
          echo 'KERNEL=="kvm", GROUP="kvm", MODE="0666", OPTIONS+="static_node=kvm"' | sudo tee /etc/udev/rules.d/99-kvm4all.rules
          sudo udevadm control --reload-rules
          sudo udevadm trigger --name-match=kvm

      - name: Gradle cache
        uses: gradle/actions/setup-gradle@v3

      - name: Run instrumented tests
        run: ./gradlew pixel6api34DebugAndroidTest

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: '**/build/reports/androidTests/'
```

### Key CI Requirements

1. **KVM acceleration** - Required for acceptable performance on Linux runners
2. **Sufficient RAM** - 8GB+ recommended for emulator
3. **Disk space** - System images cached between runs

## Advanced Configuration

### Hardware Profiles

```kotlin
create("tabletApi34") {
    device = "Pixel Tablet"
    apiLevel = 34
    systemImageSource = "google-atd"
}

create("foldableApi34") {
    device = "7.6in Foldable"
    apiLevel = 34
    systemImageSource = "google-atd"
}
```

### Test Sharding

Prefer device groups for parallel coverage; keep per-device runs small and deterministic.

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
# Run with Gradle parallelism (device tasks may still serialize depending on AGP setup)
./gradlew pixel6api34DebugAndroidTest --parallel -Dorg.gradle.workers.max=4
```

### Emulator Settings

```kotlin
create("pixel6api34") {
    device = "Pixel 6"
    apiLevel = 34
    systemImageSource = "aosp-atd"
    require64Bit = true
}
```

---

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| Emulator won't start | Enable KVM: `sudo usermod -aG kvm $USER` |
| Slow boot on CI | Use ATD images (`aosp-atd` or `google-atd`) |
| Out of disk space | Clean managed devices cache (search tasks: `./gradlew tasks --all | rg cleanManagedDevices`) |
| Tests timeout | Increase timeout in test runner config |
| API level not available | Check available images: `sdkmanager --list` |

### Cache Management

```bash
# Search available cache/cleanup tasks (names vary by AGP)
./gradlew tasks --all | rg -n "ManagedDevices|cleanManagedDevices"

# Location of cached images
# ~/.android/avd/gradle-managed/
```

---

## Device Matrix Strategy

### Recommended Matrix for Production Apps

```kotlin
managedDevices {
    localDevices {
        // Latest API
        create("pixel8api35") {
            device = "Pixel 8"
            apiLevel = 35
            systemImageSource = "google-atd"
        }

        // Popular mid-range API
        create("pixel6api33") {
            device = "Pixel 6"
            apiLevel = 33
            systemImageSource = "google-atd"
        }

        // Min supported API
        create("nexus5api24") {
            device = "Nexus 5"
            apiLevel = 24
            systemImageSource = "aosp-atd"
        }

        // Tablet
        create("tabletApi34") {
            device = "Pixel Tablet"
            apiLevel = 34
            systemImageSource = "google-atd"
        }
    }

    groups {
        create("ciMatrix") {
            targetDevices.addAll(
                devices["pixel8api35"],
                devices["pixel6api33"],
                devices["nexus5api24"]
            )
        }

        create("fullMatrix") {
            targetDevices.addAll(
                devices["pixel8api35"],
                devices["pixel6api33"],
                devices["nexus5api24"],
                devices["tabletApi34"]
            )
        }
    }
}
```

### Usage

```bash
# Quick CI check (3 devices)
./gradlew ciMatrixGroupDebugAndroidTest

# Full release validation (4 devices)
./gradlew fullMatrixGroupDebugAndroidTest
```

## Firebase Test Lab (Optional)

For cloud-based testing with real devices, use the Firebase Test Lab CLI:

```bash
gcloud firebase test android run --type instrumentation \
  --app app/build/outputs/apk/debug/app-debug.apk \
  --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
  --device model=Pixel6,version=34,locale=en,orientation=portrait
```

## Related

- [espresso-patterns.md](espresso-patterns.md) - Espresso test patterns
- [compose-testing.md](compose-testing.md) - Compose UI testing
- [SKILL.md](../SKILL.md) - Main Android testing skill
