# Mobile Test Plan

## App Overview

- **App Name**:
- **App Type**: Native / Cross-platform (React Native, Flutter) / Hybrid WebView
- **Platforms**: iOS, Android, or both
- **Min OS Policy**: iOS (typically N-2) / Android (typically N-4), or your product policy

## Critical User Flows

Prioritize flows by business impact:

| Flow | Priority | Automation | Notes |
| --- | --- | --- | --- |
| User registration / login | P0 | Yes | Auth is critical path |
| Core feature (e.g., checkout) | P0 | Yes | Revenue-generating |
| Profile management | P1 | Yes | High usage |
| Settings / preferences | P2 | Partial | Lower risk |
| Edge cases (offline, errors) | P1 | Yes | Reliability |

## Test Layers

### Unit Tests

- Business logic, data transformations, utilities.
- Target: stable coverage on critical logic (coverage % is secondary to risk reduction).
- Run on every commit.

### Integration Tests

- API contracts, local database, caching.
- Run on PR merge.

### UI / E2E Tests

- Critical flows on Tier 1 devices.
- Smoke suite: 10-15 tests, < 10 min.
- Full regression: 50-100 tests, < 30 min.

## Mobile-Specific Scenarios

| Scenario | Test Approach | Priority |
| --- | --- | --- |
| Network offline | Mock network, verify graceful degradation | P0 |
| Poor network (3G, high latency) | Throttle network in test | P1 |
| Background / foreground | Test state restoration | P1 |
| Permissions (camera, location) | Test grant/deny flows | P1 |
| Push notifications | Verify delivery and deep links | P2 |
| Deep links / universal links | Verify routing + auth gating | P1 |
| App upgrades | Test upgrade from previous version | P2 |
| Rotation / size classes | Test landscape, split view | P2 |
| Low memory / battery | Monitor for leaks, battery drain | P2 |
| Accessibility | VoiceOver/TalkBack basics; dynamic type; contrast | P1 |
| Locale/timezone | Locale, RTL (if applicable), 12/24h time, calendars | P2 |

## Automation Stack

| Platform | Framework | Language | Notes |
| --- | --- | --- | --- |
| iOS | XCUITest | Swift | Native, fast, Apple-supported |
| Android | Espresso / Compose Testing | Kotlin | Native, fast, Google-supported |
| Cross-platform smoke | Maestro | YAML | Fast authoring, black-box flows |
| Flutter | `integration_test` + Patrol | Dart | Prefer to Appium for Flutter |
| React Native | Detox | JS | Fast, gray-box testing |
| Cross-platform (fallback) | Appium (v2) | JS/Python/etc. | Flexible but higher cost/flake |

## CI Integration

```yaml
# Example: GitHub Actions mobile CI
mobile-tests:
  runs-on: macos-latest
  steps:
    - uses: actions/checkout@v4
    - name: Run iOS tests
      run: xcodebuild test -scheme App -destination 'platform=iOS Simulator,name=iPhone 16' -resultBundlePath TestResults.xcresult
    - name: Upload results
      uses: actions/upload-artifact@v4
      with:
        name: test-results
        path: TestResults.xcresult
```

```yaml
# Example: Android instrumentation on emulator
- name: Run Android tests
  run: ./gradlew connectedDebugAndroidTest
```

Notes:

- Pick a simulator/emulator name that exists in your CI image; treat device names in this template as examples.
- Always upload artifacts needed for triage (iOS `.xcresult`, Android logcat, screenshots/video when available).

## Release Gates

| Gate | Threshold | Action if Failed |
| --- | --- | --- |
| Unit tests | 100% pass | Block merge |
| Smoke suite | 100% pass | Block release |
| Regression suite | 95% pass | Review failures |
| Crash-free rate | > 99.5% | Block release |
| Performance (startup) | < 2s cold start | Review |
| Android ANR rate | Meets SLO | Block release or stage rollout |

## Reporting

- Test results in CI artifacts.
- Crash monitoring: Firebase Crashlytics / Sentry.
- Performance: Firebase Performance, Android Macrobenchmark, iOS XCTest metrics.
- Weekly QA summary with flake rate, runtime, and coverage trends.
