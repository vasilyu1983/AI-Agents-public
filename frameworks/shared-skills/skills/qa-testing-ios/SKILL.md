---
name: qa-testing-ios
description: "Run and stabilize iOS tests (XCTest, XCUITest, Swift Testing) on simulators and devices with xcodebuild/simctl: choose destinations, manage simulator state, control flakes (locale/time/network/animations), configure CI, and collect/parse xcresult artifacts."
---

# QA Testing (iOS)

Use `xcodebuild` + Xcode Simulator (`simctl`) to build, run, and stabilize iOS tests.

**Primary docs**: [XCTest](https://developer.apple.com/documentation/xctest), [Swift Testing](https://developer.apple.com/documentation/testing), [simctl](https://developer.apple.com/documentation/xcode/simctl), [Xcode testing](https://developer.apple.com/documentation/xcode/testing-your-apps-in-xcode)

## Inputs to Confirm

- Xcode entrypoint: `-workspace` or `-project`
- `-scheme` (and optional `-testPlan`)
- Destination(s): simulator name + iOS runtime (or `OS=latest`), and whether real devices are required
- UI-test hooks: launch arguments/env toggles (stubs, demo data, auth bypass, disable animations)
- Artifact needs: `xcresult`, coverage, screenshots/video, logs

## Quick Commands

| Task | Command |
|------|---------|
| List schemes | `xcodebuild -list -workspace MyApp.xcworkspace` |
| List simulators | `xcrun simctl list devices` |
| List devices (USB) | `xcrun xctrace list devices` |
| Boot simulator | `xcrun simctl boot "iPhone 15 Pro"` |
| Wait for boot | `xcrun simctl bootstatus booted -b` |
| Build app | `xcodebuild build -scheme MyApp -sdk iphonesimulator` |
| Install app | `xcrun simctl install booted app.app` |
| Run tests | `xcodebuild test -scheme MyApp -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=latest' -resultBundlePath TestResults.xcresult` |
| Run tests (device) | `xcodebuild test -scheme MyApp -destination 'platform=iOS,id=<UDID>' -resultBundlePath TestResults.xcresult` |
| Reset simulators | `xcrun simctl shutdown all && xcrun simctl erase all` |
| Take screenshot | `xcrun simctl io booted screenshot screenshot.png` |
| Record video | `xcrun simctl io booted recordVideo recording.mov` |

## Workflow

1. Resolve build inputs (`workspace/project`, `scheme`, `testPlan`, destinations).
2. Make simulator state repeatable: shutdown/erase as needed, boot, and wait for boot.
3. Run tests with artifacts enabled (`-resultBundlePath`); parallelize and retry only when appropriate.
4. Triage failures from the `xcresult` bundle; confirm flakes with repetition; quarantine with an owner and reproduction steps.

## xcodebuild Patterns

- Select tests to reproduce: `-only-testing:TargetTests/ClassName/testMethod` and `-skip-testing:TargetTests/FlakyClass`.
- Prefer test plans for large suites: `-testPlan <plan>` (keeps device/config/runs consistent).
- Enable parallel testing when suites are isolation-safe: `-parallel-testing-enabled YES` (+ `-maximum-parallel-testing-workers N`).
- Always write a result bundle in automation: `-resultBundlePath TestResults.xcresult`.
- For reruns, split build and test: `xcodebuild build-for-testing ...` then `xcodebuild test-without-building ...`.
- Inspect results locally: `open TestResults.xcresult` or `xcrun xcresulttool get --path TestResults.xcresult --format json`.

### Flake Triage (Repetition and Retry)

- Prefer repetition to prove flake rate before adding retries.
- Use targeted reruns before suite-wide retries.

Common patterns (flags vary by Xcode version):

- Retry failing tests once in CI: `-retry-tests-on-failure -test-iterations 2`
- Measure flakiness until first failure: `-test-iterations 50 -test-repetition-mode until-failure`
- Run a single test repeatedly: `-only-testing:TargetTests/ClassName/testMethod -test-iterations 20`

## Testing Layers

| Layer | Framework | Scope |
|-------|-----------|-------|
| Unit | XCTest / Swift Testing | Business logic (fast) |
| Snapshot | XCTest + snapshot libs | View rendering |
| Integration | XCTest | Persistence, networking |
| UI | XCUITest | Critical user journeys |

### Device Matrix

- Default: simulators for PR gates; real devices for release
- Cover: one small phone, one large phone, iPad if supported
- Add OS versions only for multiple major release support

### Flake Control

Use these defaults unless the project requires otherwise:

- Disable or reduce animations in UI-test builds.
- Fix locale/timezone (via launch arguments or app-level configuration).
- Stub network at the boundary (avoid real third-party calls in UI tests).
- Reset app state between tests (fresh install, deep-link reset, or explicit teardown).
- Prefer state-based waits (`waitForExistence`, expectations) over sleeps.
- Pre-grant/reset permissions where possible (simulators): `xcrun simctl privacy booted grant ...`.

## CI Integration (GitHub Actions)

```yaml
name: iOS CI
on: [push, pull_request]
jobs:
  test:
    runs-on: macos-15
    steps:
      - uses: actions/checkout@v4
      - uses: maxim-lobanov/setup-xcode@v1
        with:
          xcode-version: "16.0"
      - run: |
          set -euo pipefail
          xcodebuild test \
            -scheme MyApp \
            -sdk iphonesimulator \
            -destination 'platform=iOS Simulator,name=iPhone 15 Pro,OS=latest' \
            -resultBundlePath TestResults.xcresult
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results
          path: TestResults.xcresult
```

## Do / Avoid

### Do

- Make UI tests independent and idempotent
- Use test data builders and dedicated test accounts
- Collect `xcresult` bundles on failure
- Use accessibilityIdentifier, not labels

### Avoid

- Relying on test ordering or global state
- UI tests requiring real network
- Thread.sleep() for synchronization
- Accepting AI-proposed selectors without validation

## Resources

| Resource | Purpose |
|----------|---------|
| [references/swift-testing.md](references/swift-testing.md) | Swift Testing framework |
| [references/simulator-commands.md](references/simulator-commands.md) | Complete simctl reference |
| [references/xctest-patterns.md](references/xctest-patterns.md) | XCTest/XCUITest patterns |

## Templates

| Template | Purpose |
|----------|---------|
| [assets/template-ios-ui-test-stability-checklist.md](assets/template-ios-ui-test-stability-checklist.md) | Stability checklist |

## Related Skills

| Skill | Purpose |
|-------|---------|
| [software-mobile](../software-mobile/SKILL.md) | iOS development |
| [qa-testing-strategy](../qa-testing-strategy/SKILL.md) | Test strategy |
| [qa-testing-mobile](../qa-testing-mobile/SKILL.md) | Cross-platform mobile |
