# Cloud Device Farm Strategies

## Table of Contents

- [Provider Comparison](#provider-comparison)
- [Procurement Questions](#procurement-questions)
- [Pricing Models](#pricing-models)
- [Device Selection Strategy](#device-selection-strategy)
- [Real Device vs Emulator Trade-Offs](#real-device-vs-emulator-trade-offs)
- [Test Sharding Across Devices](#test-sharding-across-devices)
- [Parallel Execution Optimization](#parallel-execution-optimization)
- [On-Premise Device Lab](#on-premise-device-lab)
- [CI/CD Integration Patterns](#cicd-integration-patterns)
- [Cost Tracking and Budgeting](#cost-tracking-and-budgeting)
- [Free Tier Optimization](#free-tier-optimization)
- [Device Availability and Queue Management](#device-availability-and-queue-management)
- [Decision Checklist](#decision-checklist)
- [Related Resources](#related-resources)

Cloud device farm selection, cost optimization, and CI/CD integration for mobile testing at scale.

Treat provider capabilities, device inventories, and pricing as live facts. Verify them in official docs before making a recommendation or quoting a number.

## Provider Comparison

Use provider classes rather than memorizing vendor counts:

| Provider Type | Best Fit | Watch-Out |
|----------|-------------|-----------|
| Dedicated device cloud | Broad real-device coverage, manual + automated testing | Queueing, data residency, contract lock-in |
| Platform-native lab | Android-first automation and store-adjacent workflows | Narrower framework support, platform bias |
| CI vendor with device/virtual-device integrations | Teams already standardized on that CI stack | May not replace a full real-device cloud |
| On-prem device lab | Regulated or hardware-specific needs | Hardware ops, maintenance, lower elasticity |

### Framework Support Matrix

Verify support directly in vendor docs before locking a plan. Support details worth checking explicitly include:

- Appium 3 compatibility and client/runtime expectations
- Native framework support for Espresso/XCUITest
- Maestro support on the target provider
- API surface for uploads, reruns, artifacts, and parallel runs
- Data residency, SSO, and compliance controls for enterprise buyers

---

## Procurement Questions

Before recommending a provider, answer these questions with official docs or a trial account:

- Which frameworks must run there: Appium, Espresso, XCUITest, Detox, Maestro, Flutter?
- Which devices or OEM variants are mandatory from product analytics?
- Do you need manual debugging as well as automation?
- Are queue-time guarantees, private devices, or regional data residency required?
- Is procurement buying per-minute, per-concurrency, or enterprise capacity?
- Does the provider expose the artifacts and APIs your CI and triage flow need?

## Pricing Models

### Per-Minute Pricing

Pay only for active test time. Best for variable workloads.

```text
Monthly estimate formula:
  Cost = (avg_test_minutes_per_run) × (runs_per_day) × (working_days) × (provider_rate_per_minute)
```

### Concurrent Device Plans

Fixed number of parallel devices; unlimited minutes. Best for high-volume CI.

```text
Example (AWS Device Farm - Unmetered):
  device_slots × quoted_monthly_slot_price

Break-even vs per-minute:
  If projected minutes exceed the quoted break-even point, concurrency plans usually win
```

### Flat-Rate / Enterprise

Annual contracts with volume discounts. Negotiate when spending above $2,000/month.

| Model | Best For | Watch Out For |
|-------|----------|---------------|
| Per-minute | <500 test-min/month, early teams | Costs spike on flaky reruns |
| Concurrent | Predictable daily CI, 500-5000 min/month | Idle slots waste money |
| Enterprise | >5000 min/month, multi-team | Lock-in, use-it-or-lose-it clauses |

---

## Device Selection Strategy

### Coverage vs Cost Matrix

Build device tiers from analytics data:

```text
Tier 1 (Must-test, ~70% users):
  - Top 3-5 devices by active installs
  - Latest + previous OS version
  - Run on every PR

Tier 2 (Should-test, ~20% users):
  - Next 5-8 devices
  - Specific OEM variants (Samsung, Xiaomi, Pixel)
  - Run on merge to main / nightly

Tier 3 (Spot-check, ~10% users):
  - Older devices, budget phones
  - Edge OS versions (oldest supported)
  - Run weekly or pre-release
```

Compute the cumulative-share cutoffs (70% / 90%) from the same analytics window you use for crash-rate triage, keyed by `device_model|os_version`, and refresh the tiers each release train.

### Minimum Viable Matrix

For teams with limited budget, start here:

| Platform | Device | Rationale |
|----------|--------|-----------|
| iOS | Current flagship iPhone | Current flagship coverage |
| iOS | iPhone SE 3rd gen | Smallest screen, lowest specs |
| iOS | Current iPad | Tablet layout |
| Android | Current Pixel | Reference device |
| Android | Current Samsung S-series | Popular OEM flagship |
| Android | Current Samsung A-series | Budget and mid-range coverage |

---

## Real Device vs Emulator Trade-Offs

| Dimension | Real Device | Emulator/Simulator |
|-----------|-------------|-------------------|
| **Accuracy** | Production-identical hardware | Close for app logic; gaps in GPU, sensors, OEM behaviour |
| **Speed** | Slower provisioning and queue-dependent | Faster startup and lower provisioning friction |
| **Cost** | Paid capacity or contract-bound | Usually lower marginal cost |
| **Sensors** | Camera, GPS, biometrics, NFC | Simulated (limited fidelity) |
| **Performance testing** | Reliable benchmarks | Not representative |
| **Flakiness** | Adds hardware noise (thermal, OEM dialogs, battery, network); see [flake-management.md](flake-management.md) | More deterministic, but animation timing differs from hardware |
| **Availability** | Queue contention possible | Always available |
| **Network** | Real conditions testable | Simulated throttling |

### When to Use Each

```text
USE EMULATORS/SIMULATORS FOR:
  - Unit test execution
  - Integration tests
  - Rapid iteration during development
  - PR-level smoke checks
  - Screenshot generation for docs

USE REAL DEVICES FOR:
  - E2E / UI acceptance tests
  - Performance benchmarking
  - Camera / biometric / NFC flows
  - Pre-release validation
  - Network condition testing
  - OEM-specific behavior verification
```

---

## Test Sharding Across Devices

### Sharding Strategies

**By test suite** (recommended for device farms):

```yaml
# GitHub Actions: matrix strategy for device sharding
jobs:
  mobile-tests:
    strategy:
      fail-fast: false
      matrix:
        include:
          - device: "Current Pixel"
            os_version: "14.0"
            shard: 0   # AndroidJUnitRunner shardIndex is 0-based
          - device: "Current Samsung flagship"
            os_version: "14.0"
            shard: 1
          - device: "Previous Android reference device"
            os_version: "13.0"
            shard: 2
    steps:
      - name: Run sharded tests
        run: |
          ./gradlew connectedAndroidTest \
            -Pandroid.testInstrumentationRunnerArguments.numShards=3 \
            -Pandroid.testInstrumentationRunnerArguments.shardIndex=${{ matrix.shard }}
```

**By test tag** (functional grouping):

```bash
# Run smoke tests on all devices, regression on Tier 1 only
# Smoke (all devices)
./gradlew connectedAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.annotation=com.example.Smoke

# Regression (Tier 1 only)
./gradlew connectedAndroidTest \
  -Pandroid.testInstrumentationRunnerArguments.annotation=com.example.Regression
```

---

## Parallel Execution Optimization

### Optimal Parallelism Formula

```text
Optimal parallel devices = ceil(total_test_minutes / target_wall_clock_minutes)

Example:
  Total suite: 120 test-minutes
  Target wall clock: 15 minutes
  Optimal devices: ceil(120 / 15) = 8 parallel devices
```

### Parallelism Gotchas

| Issue | Symptom | Fix |
|-------|---------|-----|
| Shared backend state | Tests pass alone, fail in parallel | Isolate test accounts / data per device |
| Rate limiting | API 429 errors under parallel load | Mock APIs or raise limits for test env |
| Device warm-up time | First test slower on cold device | Include warm-up step in CI |
| Uneven shard sizes | One shard finishes late | Use historical timing data to balance |

---

## On-Premise Device Lab

### When It Makes Sense

- Testing >4 hours/day of real-device time
- Regulatory requirement for on-prem data processing
- Need devices not available in cloud (specialized hardware, carrier-specific)
- Break-even point depends on device count, utilisation and staff time (work it out with your own cost model rather than a rule-of-thumb device count)

### Setup Checklist

- [ ] USB hubs with independent power per port
- [ ] Dedicated Mac Mini / Linux host per 5-8 devices
- [ ] STF (DeviceFarmer) or similar orchestration
- [ ] Temperature-controlled environment
- [ ] Automated device health checks (battery, connectivity)
- [ ] Remote access for debugging (scrcpy for Android, Xcode wireless for iOS)
- [ ] Automatic device reboot schedule (daily)

STF is maintained as [DeviceFarmer/stf](https://github.com/DeviceFarmer/stf); the original `openstf/stf` image is unmaintained. STF needs RethinkDB plus ADB access; use the project's `docker-compose.yaml` and [Compose setup guide](https://github.com/DeviceFarmer/stf/blob/master/docker/compose/README.md) (image `devicefarmer/stf`) rather than a single `docker run`.

---

## CI/CD Integration Patterns

### BrowserStack + GitHub Actions

```yaml
# .github/workflows/mobile-tests.yml
name: Mobile Tests
on: [push, pull_request]

jobs:
  android-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build APK
        run: ./gradlew assembleDebug assembleDebugAndroidTest

      - name: Upload and run on BrowserStack
        env:
          BROWSERSTACK_USERNAME: ${{ secrets.BROWSERSTACK_USERNAME }}
          BROWSERSTACK_ACCESS_KEY: ${{ secrets.BROWSERSTACK_ACCESS_KEY }}
        run: |
          # Upload app
          APP_URL=$(curl -u "$BROWSERSTACK_USERNAME:$BROWSERSTACK_ACCESS_KEY" \
            -X POST "https://api-cloud.browserstack.com/app-automate/upload" \
            -F "file=@app/build/outputs/apk/debug/app-debug.apk" \
            | jq -r '.app_url')

          # Upload test suite
          TEST_URL=$(curl -u "$BROWSERSTACK_USERNAME:$BROWSERSTACK_ACCESS_KEY" \
            -X POST "https://api-cloud.browserstack.com/app-automate/espresso/v2/test-suite" \
            -F "file=@app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk" \
            | jq -r '.test_suite_url')

          # Execute tests
          curl -u "$BROWSERSTACK_USERNAME:$BROWSERSTACK_ACCESS_KEY" \
            -X POST "https://api-cloud.browserstack.com/app-automate/espresso/v2/build" \
            -d "{\"app\": \"$APP_URL\", \"testSuite\": \"$TEST_URL\", \
                 \"devices\": [\"<tier-1-device-a>\", \"<tier-1-device-b>\"]}"
```

### Firebase Test Lab + Cloud Build

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/gradle'
    args: ['assembleDebug', 'assembleDebugAndroidTest']

  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'firebase'
      - 'test'
      - 'android'
      - 'run'
      - '--type=instrumentation'
      - '--app=app/build/outputs/apk/debug/app-debug.apk'
      - '--test=app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk'
      - '--device=model=oriole,version=33'
      - '--device=model=redfin,version=31'
      - '--timeout=15m'
      - '--results-dir=test-results'
```

---

## Cost Tracking and Budgeting

### Monthly Cost Dashboard

```python
def calculate_monthly_cost(
    pricing_model: str,
    daily_runs: int,
    avg_minutes_per_run: float,
    parallel_devices: int,
    per_minute_rate: float | None = None,
    concurrent_monthly_cost: float | None = None,
    working_days: int = 22
) -> dict:
    """Estimate monthly device farm costs."""
    total_minutes = daily_runs * avg_minutes_per_run * working_days

    if pricing_model == "per_minute":
        if per_minute_rate is None:
            raise ValueError("per_minute_rate is required for per-minute pricing")
        cost = total_minutes * parallel_devices * per_minute_rate
    else:
        if concurrent_monthly_cost is None:
            raise ValueError("concurrent_monthly_cost is required for concurrency pricing")
        cost = parallel_devices * concurrent_monthly_cost

    return {
        "model": pricing_model,
        "total_minutes": total_minutes * parallel_devices,
        "monthly_cost": f"${cost:,.0f}",
        "cost_per_test_minute": f"${cost / (total_minutes * parallel_devices):.3f}",
    }
```

### Cost Reduction Checklist

- [ ] Run Tier 2/3 devices only on nightly, not every PR
- [ ] Use emulators for unit/integration tests in CI
- [ ] Implement test sharding to reduce wall-clock (but not total minutes)
- [ ] Remove or quarantine flaky tests that waste rerun minutes
- [ ] Use trial or low-cost quotas only for smoke coverage and procurement validation
- [ ] Cache device provisioning where providers support it
- [ ] Right-size parallel device count using timing data

---

## Free Tier Optimization

Do not hard-code free-tier numbers in planning documents. Check the current pricing/quota pages on the day you decide:

- Firebase pricing and quotas
- AWS Device Farm pricing
- Device-cloud trial terms and enterprise quotes

Good uses for limited free or trial capacity:

- Smoke suites on one or two representative devices
- API and artifact-flow validation
- Procurement bake-offs between two providers

---

## Device Availability and Queue Management

### Handling Queue Contention

```text
Problem: Real devices may be in use by other customers.
  - Popular current flagship devices usually have the longest queues
  - Queue behavior varies by region, account tier, and time of day

Mitigation:
  1. Schedule heavy runs off-peak for your provider and region
  2. Use an equivalent device alternative from the same tier when queues are high
  3. Set queue timeout + fallback to emulator
  4. Pre-reserve devices for release testing
```

### Timeout and Fallback Pattern

```yaml
# CI config with device fallback
env:
  DEVICE_TIMEOUT: 120  # seconds to wait for device

steps:
  - name: Run on real device
    id: real_device
    continue-on-error: true
    run: |
      timeout $DEVICE_TIMEOUT run-tests --device="current-tier-1-device" --real

  - name: Fallback to emulator
    if: steps.real_device.outcome == 'failure'
    run: |
      echo "Real device unavailable, falling back to emulator"
      run-tests --device="current-tier-1-device" --emulator
```

---

## Decision Checklist

Before selecting a device farm provider:

- [ ] Identified top 10 devices from analytics
- [ ] Calculated monthly test minutes and rerun waste (current and projected)
- [ ] Compared quoted per-minute vs concurrent pricing for your volume
- [ ] Verified framework support (Espresso, XCUITest, Appium, etc.)
- [ ] Tested API and CI integration with a trial run
- [ ] Confirmed data residency and compliance requirements
- [ ] Evaluated queue wait times for target devices
- [ ] Assessed on-prem vs cloud break-even for your scale

---

## Related Resources

- [framework-comparison.md](framework-comparison.md) -- automation framework selection guide
- [flake-management.md](flake-management.md) -- managing flaky tests on device farms
- [SKILL.md](../SKILL.md) -- parent mobile testing skill
- [BrowserStack App Automate](https://www.browserstack.com/app-automate)
- [BrowserStack Maestro docs](https://www.browserstack.com/docs/app-automate/maestro)
- [Firebase Test Lab](https://firebase.google.com/docs/test-lab)
- [Firebase Pricing](https://firebase.google.com/pricing)
- [AWS Device Farm](https://docs.aws.amazon.com/devicefarm/)
- [AWS Device Farm Pricing](https://aws.amazon.com/device-farm/pricing/)
- [Bitrise iOS simulator testing](https://docs.bitrise.io/en/bitrise-ci/testing/testing-ios-apps/building-an-ios-app-for-a-simulator)
- [DeviceFarmer STF (successor to OpenSTF)](https://github.com/DeviceFarmer/stf)
