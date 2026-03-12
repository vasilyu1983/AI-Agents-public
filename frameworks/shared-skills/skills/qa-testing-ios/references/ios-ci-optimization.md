# iOS CI Optimization

Build and test pipeline optimization for iOS projects in continuous integration.

## Contents

- [Xcode Build Caching](#xcode-build-caching)
- [Test Parallelization](#test-parallelization)
- [Test Sharding Across CI Nodes](#test-sharding-across-ci-nodes)
- [Simulator Management](#simulator-management)
- [CI Provider Comparison](#ci-provider-comparison)
- [xcresult Bundle Processing](#xcresult-bundle-processing)
- [Test Result Merging](#test-result-merging)
- [Fastlane Integration](#fastlane-integration)
- [Code Signing in CI](#code-signing-in-ci)
- [Build Time Optimization](#build-time-optimization)
- [Test Selection](#test-selection)
- [Related Resources](#related-resources)

---

## Xcode Build Caching

### DerivedData Caching

```yaml
# GitHub Actions: cache DerivedData
- name: Cache DerivedData
  uses: actions/cache@v4
  with:
    path: ~/Library/Developer/Xcode/DerivedData
    key: deriveddata-${{ runner.os }}-${{ hashFiles('**/*.xcodeproj/project.pbxproj', '**/Package.resolved') }}
    restore-keys: |
      deriveddata-${{ runner.os }}-
```

### SPM Cache

```yaml
# Cache Swift Package Manager resolved packages
- name: Cache SPM
  uses: actions/cache@v4
  with:
    path: |
      ~/Library/Caches/org.swift.swiftpm
      .build
    key: spm-${{ runner.os }}-${{ hashFiles('**/Package.resolved') }}
    restore-keys: |
      spm-${{ runner.os }}-
```

### CocoaPods Cache

```yaml
- name: Cache CocoaPods
  uses: actions/cache@v4
  with:
    path: Pods
    key: pods-${{ runner.os }}-${{ hashFiles('**/Podfile.lock') }}
    restore-keys: |
      pods-${{ runner.os }}-

- name: Install pods
  run: |
    if [ ! -d "Pods" ]; then
      pod install
    fi
```

### Incremental Builds

```bash
# Build for testing (compiles without running)
xcodebuild build-for-testing \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -derivedDataPath ./DerivedData

# Run tests using pre-built artifacts
xcodebuild test-without-building \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -derivedDataPath ./DerivedData
```

---

## Test Parallelization

### xcodebuild Parallel Testing

```bash
# Enable parallel testing (distributes test classes across simulators)
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -parallel-testing-enabled YES \
  -parallel-testing-worker-count 4 \
  -resultBundlePath TestResults.xcresult
```

### Test Plan Configuration

```json
{
  "configurations": [
    {
      "name": "Default",
      "options": {
        "targetForVariableExpansion": {
          "containerPath": "container:MyApp.xcodeproj",
          "identifier": "MyAppTests",
          "name": "MyAppTests"
        },
        "maximumTestExecutionTimeAllowance": 60,
        "testExecutionOrdering": "random",
        "testTimeoutsEnabled": true
      }
    }
  ],
  "defaultOptions": {
    "isParallelizable": true,
    "maximumParallelTestWorkerCount": 4
  }
}
```

### Parallel Testing Strategies

| Strategy          | How It Works                       | Best For                    |
|-------------------|------------------------------------|-----------------------------|
| Class-level       | Each test class on a different sim | Mixed test durations        |
| Target-level      | Each test target on a different sim| Multi-module projects       |
| Manual sharding   | Split by test plan                 | Fine-grained control        |

---

## Test Sharding Across CI Nodes

### Manual Sharding with Test Plans

```bash
# Shard 1: Unit tests
xcodebuild test \
  -scheme MyApp \
  -testPlan UnitTests \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -resultBundlePath UnitResults.xcresult

# Shard 2: Integration tests
xcodebuild test \
  -scheme MyApp \
  -testPlan IntegrationTests \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -resultBundlePath IntegrationResults.xcresult

# Shard 3: UI tests
xcodebuild test \
  -scheme MyApp \
  -testPlan UITests \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -resultBundlePath UIResults.xcresult
```

### GitHub Actions Matrix Sharding

```yaml
jobs:
  test:
    strategy:
      fail-fast: false
      matrix:
        include:
          - shard: unit
            test-plan: UnitTests
          - shard: integration
            test-plan: IntegrationTests
          - shard: ui-1
            only-testing: MyAppUITests/LoginFlowTests
          - shard: ui-2
            only-testing: MyAppUITests/CheckoutFlowTests
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_16.0.app

      - name: Run tests
        run: |
          ARGS="-scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15'"
          if [ -n "${{ matrix.test-plan }}" ]; then
            ARGS="$ARGS -testPlan ${{ matrix.test-plan }}"
          fi
          if [ -n "${{ matrix.only-testing }}" ]; then
            ARGS="$ARGS -only-testing:${{ matrix.only-testing }}"
          fi
          eval xcodebuild test $ARGS \
            -resultBundlePath "Results-${{ matrix.shard }}.xcresult"

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: results-${{ matrix.shard }}
          path: "Results-${{ matrix.shard }}.xcresult"
```

---

## Simulator Management

### Boot and Clone Simulators

```bash
# List available simulators
xcrun simctl list devices available

# Boot a specific simulator
xcrun simctl boot "iPhone 15"

# Clone a simulator for parallel testing
xcrun simctl clone "iPhone 15" "iPhone 15 - Worker 1"
xcrun simctl clone "iPhone 15" "iPhone 15 - Worker 2"
xcrun simctl clone "iPhone 15" "iPhone 15 - Worker 3"

# Boot clones in parallel
xcrun simctl boot "iPhone 15 - Worker 1" &
xcrun simctl boot "iPhone 15 - Worker 2" &
xcrun simctl boot "iPhone 15 - Worker 3" &
wait
```

### Simulator Lifecycle in CI

```bash
#!/bin/bash
set -euo pipefail

DEVICE_NAME="CI-iPhone15"
RUNTIME="iOS-18-0"
DEVICE_TYPE="iPhone 15"

# Create simulator
UDID=$(xcrun simctl create "$DEVICE_NAME" "$DEVICE_TYPE" "$RUNTIME")

# Boot
xcrun simctl boot "$UDID"

# Wait for boot
xcrun simctl bootstatus "$UDID" -b

# Disable keyboard autocorrect and autocapitalization
xcrun simctl spawn "$UDID" defaults write \
  com.apple.Preferences KeyboardAutocorrection -bool NO
xcrun simctl spawn "$UDID" defaults write \
  com.apple.Preferences KeyboardAutocapitalization -bool NO

# Run tests
xcodebuild test \
  -scheme MyApp \
  -destination "platform=iOS Simulator,id=$UDID" \
  -resultBundlePath TestResults.xcresult

# Cleanup
xcrun simctl shutdown "$UDID"
xcrun simctl delete "$UDID"
```

### Parallel Simulator Strategy

```bash
# Create and boot 4 parallel simulators
WORKERS=4
PIDS=()

for i in $(seq 1 $WORKERS); do
  UDID=$(xcrun simctl create "Worker-$i" "iPhone 15" "iOS-18-0")
  xcrun simctl boot "$UDID" &
  PIDS+=($!)
done

# Wait for all boots
for pid in "${PIDS[@]}"; do wait "$pid"; done

# Run tests distributed across workers
xcodebuild test \
  -scheme MyApp \
  -parallel-testing-enabled YES \
  -parallel-testing-worker-count $WORKERS \
  -destination 'platform=iOS Simulator,name=Worker-1' \
  -destination 'platform=iOS Simulator,name=Worker-2' \
  -destination 'platform=iOS Simulator,name=Worker-3' \
  -destination 'platform=iOS Simulator,name=Worker-4'
```

---

## CI Provider Comparison

| Feature                 | Xcode Cloud      | GitHub Actions    | CircleCI          |
|-------------------------|------------------|-------------------|-------------------|
| **macOS runners**       | Included         | macos-14          | macOS resource class |
| **Xcode pre-installed** | Latest + recent  | Multiple versions | Via orb/image     |
| **Simulator caching**   | Automatic        | Manual            | Manual            |
| **Code signing**        | App Store Connect| Manual/fastlane   | Manual/fastlane   |
| **Build minutes (free)**| 25 hrs/month     | 2000 min/month (10x) | 6000 min/month |
| **Parallelism**         | Limited          | Up to 20 parallel | Depends on plan   |
| **Xcode integration**   | Native           | Via CLI           | Via CLI           |
| **Artifact storage**    | App Store Connect| 500MB-50GB       | 30 days           |

### Xcode Cloud Configuration

```yaml
# ci_scripts/ci_post_clone.sh
#!/bin/bash
set -euo pipefail

# Install dependencies
if [ -f "Podfile.lock" ]; then
  pod install
fi

# ci_scripts/ci_pre_xcodebuild.sh
#!/bin/bash
# Pre-build steps (environment setup)
export API_BASE_URL="https://staging.example.com"
```

### GitHub Actions Recommended Config

```yaml
name: iOS Tests
on:
  pull_request:
    paths:
      - '**/*.swift'
      - '**/*.xib'
      - '**/*.storyboard'
      - '**/project.pbxproj'

jobs:
  test:
    runs-on: macos-14
    timeout-minutes: 30
    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode 16
        run: sudo xcode-select -s /Applications/Xcode_16.0.app

      - uses: actions/cache@v4
        with:
          path: |
            ~/Library/Developer/Xcode/DerivedData
            ~/Library/Caches/org.swift.swiftpm
          key: xcode-${{ runner.os }}-${{ hashFiles('**/Package.resolved', '**/project.pbxproj') }}

      - name: Build and test
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=18.0' \
            -parallel-testing-enabled YES \
            -resultBundlePath TestResults.xcresult \
            | xcbeautify

      - name: Publish test results
        if: always()
        uses: dorny/test-reporter@v1
        with:
          name: iOS Tests
          path: TestResults.xcresult
          reporter: xcode
```

---

## xcresult Bundle Processing

### Extract Test Results

```bash
# Summary
xcrun xcresulttool get --path TestResults.xcresult --format json

# Test failures
xcrun xcresulttool get test-results summary \
  --path TestResults.xcresult \
  --format json

# Export for CI reporting
xcrun xcresulttool export \
  --path TestResults.xcresult \
  --output-path ./exported-results \
  --type file
```

### Convert to JUnit XML

```bash
# Using xcbeautify (recommended)
xcodebuild test ... | xcbeautify --report junit --report-path results.xml

# Using xcresultparser
xcresultparser -o junit TestResults.xcresult > results.xml
```

### Extract Failure Screenshots

```bash
# xcresulttool can export attachments
xcrun xcresulttool export \
  --path TestResults.xcresult \
  --output-path ./test-attachments \
  --type attachments
```

---

## Test Result Merging

### Merging Results from Shards

```bash
# Use xcresulttool merge (Xcode 16+)
xcrun xcresulttool merge \
  Results-unit.xcresult \
  Results-integration.xcresult \
  Results-ui.xcresult \
  --output-path MergedResults.xcresult
```

### Custom Merge Script for JUnit XML

```bash
#!/bin/bash
# Merge JUnit XML files from multiple shards

OUTPUT="merged-results.xml"

echo '<?xml version="1.0" encoding="UTF-8"?>' > "$OUTPUT"
echo '<testsuites>' >> "$OUTPUT"

for file in results-*.xml; do
  # Extract testsuites content (skip xml declaration and root tags)
  sed -n '/<testsuite /,/<\/testsuite>/p' "$file" >> "$OUTPUT"
done

echo '</testsuites>' >> "$OUTPUT"

echo "Merged $(ls results-*.xml | wc -l) result files into $OUTPUT"
```

---

## Fastlane Integration

### Scanfile Configuration

```ruby
# fastlane/Scanfile
scheme("MyApp")
device("iPhone 15")
clean(false)
code_coverage(true)
output_directory("./fastlane/test_output")
result_bundle(true)
parallel_testing(true)
concurrent_workers(4)
```

### Fastlane Scan Action

```ruby
# fastlane/Fastfile
default_platform(:ios)

platform :ios do
  desc "Run all tests"
  lane :test do
    scan(
      scheme: "MyApp",
      device: "iPhone 15 (18.0)",
      result_bundle: true,
      output_types: "junit,html",
      parallel_testing: true,
      concurrent_workers: 4,
      fail_build: true,
    )
  end

  desc "Run unit tests only"
  lane :unit_test do
    scan(
      scheme: "MyApp",
      testplan: "UnitTests",
      device: "iPhone 15 (18.0)",
      result_bundle: true,
    )
  end

  desc "Run UI tests with retry"
  lane :ui_test do
    scan(
      scheme: "MyApp",
      testplan: "UITests",
      device: "iPhone 15 (18.0)",
      result_bundle: true,
      number_of_retries: 2,  # retry flaky tests
    )
  end
end
```

### CI with Fastlane

```yaml
- name: Run tests via fastlane
  run: bundle exec fastlane test
  env:
    FASTLANE_XCODEBUILD_SETTINGS_TIMEOUT: 120
```

---

## Code Signing in CI

### Automatic Signing Disabled for Tests

```bash
# For running tests, code signing is typically not needed
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  CODE_SIGNING_ALLOWED=NO \
  CODE_SIGNING_REQUIRED=NO
```

### Fastlane Match for Distribution Builds

```ruby
# fastlane/Matchfile
type("development")
app_identifier("com.example.myapp")
git_url("https://github.com/org/certificates.git")
storage_mode("git")

# In Fastfile
lane :build_for_testing do
  match(type: "development", readonly: true)
  gym(
    scheme: "MyApp",
    export_method: "development",
    skip_codesigning: false,
  )
end
```

### Keychain Management in CI

```bash
# Create a temporary keychain for CI
KEYCHAIN_NAME="ci-keychain"
KEYCHAIN_PASSWORD="ci-password"

security create-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_NAME"
security default-keychain -s "$KEYCHAIN_NAME"
security unlock-keychain -p "$KEYCHAIN_PASSWORD" "$KEYCHAIN_NAME"
security set-keychain-settings -lut 3600 "$KEYCHAIN_NAME"

# Import certificates
security import cert.p12 \
  -k "$KEYCHAIN_NAME" \
  -P "$CERT_PASSWORD" \
  -A -T /usr/bin/codesign

# Allow codesign access
security set-key-partition-list -S apple-tool:,apple: \
  -s -k "$KEYCHAIN_PASSWORD" "$KEYCHAIN_NAME"
```

---

## Build Time Optimization

### Modular Builds

```text
Monolith (slow):
  MyApp (all source) → 8 min build

Modular (fast):
  Core         → 1 min (cached)
  Networking   → 1 min (cached)
  Feature-Auth → 1 min
  Feature-Home → 1 min
  MyApp (thin) → 30 sec
  Total: ~2 min (with cache hits)
```

### Explicit Modules

```bash
# Enable explicit module builds for faster compilation
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -enableExplicitModules YES
```

### Build Settings for CI

```bash
# Optimize for CI speed
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  COMPILER_INDEX_STORE_ENABLE=NO \
  DEBUG_INFORMATION_FORMAT=dwarf \
  ONLY_ACTIVE_ARCH=YES \
  ENABLE_TESTABILITY=YES
```

### Build Time Budgets

| Phase                  | Target    | Optimization Lever                    |
|------------------------|-----------|---------------------------------------|
| Checkout + cache       | < 1 min   | Shallow clone, cache restore          |
| Dependency resolution  | < 1 min   | Cache SPM/CocoaPods                   |
| Compilation            | < 5 min   | Modular builds, DerivedData cache     |
| Simulator boot         | < 15 sec  | Pre-booted sim, clone strategy        |
| Unit tests             | < 3 min   | Parallel forks                        |
| UI tests               | < 10 min  | Sharding across 4+ simulators         |
| Artifact upload        | < 1 min   | Compress, selective upload            |
| **Total pipeline**     | **< 20 min** | All of the above                  |

---

## Test Selection

### Only Run Changed Targets

```bash
#!/bin/bash
# Detect changed Swift files and run affected test targets

CHANGED_FILES=$(git diff --name-only origin/main...HEAD -- '*.swift')

TARGETS_TO_TEST=()
for file in $CHANGED_FILES; do
  # Map source file to test target
  if [[ "$file" == *"Feature/Auth"* ]]; then
    TARGETS_TO_TEST+=("FeatureAuthTests")
  elif [[ "$file" == *"Feature/Home"* ]]; then
    TARGETS_TO_TEST+=("FeatureHomeTests")
  elif [[ "$file" == *"Core/"* ]]; then
    # Core changes require all tests
    TARGETS_TO_TEST=("ALL")
    break
  fi
done

# Deduplicate
UNIQUE_TARGETS=($(echo "${TARGETS_TO_TEST[@]}" | tr ' ' '\n' | sort -u))

if [[ "${UNIQUE_TARGETS[0]}" == "ALL" ]]; then
  xcodebuild test -scheme MyApp -destination '...'
else
  ONLY_TESTING=""
  for target in "${UNIQUE_TARGETS[@]}"; do
    ONLY_TESTING="$ONLY_TESTING -only-testing:$target"
  done
  eval xcodebuild test -scheme MyApp -destination '...' $ONLY_TESTING
fi
```

### Skip/Only Testing Flags

```bash
# Run only specific test targets
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -only-testing:MyAppTests/AuthTests \
  -only-testing:MyAppTests/PaymentTests

# Skip slow or flaky tests
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=iOS Simulator,name=iPhone 15' \
  -skip-testing:MyAppUITests/PerformanceTests \
  -skip-testing:MyAppUITests/FlakyNetworkTests
```

**Checklist -- iOS CI Optimization:**

- [ ] DerivedData cached between CI runs
- [ ] SPM/CocoaPods dependencies cached
- [ ] Parallel testing enabled with 4+ workers
- [ ] Test sharding across CI matrix for large suites
- [ ] Simulator pre-booted or cloned for parallel execution
- [ ] xcresult bundles uploaded as artifacts
- [ ] JUnit XML generated for CI reporting
- [ ] Code signing disabled for test-only pipelines
- [ ] Build time budget defined and tracked
- [ ] Test selection skips unaffected targets on PRs
- [ ] Flaky tests retried or quarantined separately

---

## Related Resources

- [xctest-patterns.md](xctest-patterns.md) -- XCTest testing patterns
- [xcuitest-patterns.md](xcuitest-patterns.md) -- XCUITest UI testing
- [snapshot-testing-ios.md](snapshot-testing-ios.md) -- Visual snapshot CI integration
- [swift-testing.md](swift-testing.md) -- Modern Swift Testing framework
- [simulator-commands.md](simulator-commands.md) -- Simulator lifecycle management
