# Test Layers and Suite Anti-Patterns

The layer cost profile, entry points for deep-link and offline tests, and the suite-level anti-patterns. These parts of the retired software-mobile testing reference were not already covered here. Framework choice lives in [framework-comparison.md](framework-comparison.md), the cross-platform pyramid in [cross-platform-test-patterns.md](cross-platform-test-patterns.md), flakes in [flake-management.md](flake-management.md), device farms in [device-farm-strategies.md](device-farm-strategies.md), and snapshots in [visual-regression-mobile.md](visual-regression-mobile.md).

## Layer Cost Profile

Put each risk at the cheapest layer that can actually catch it. The profile below is relative. It is not a quota; derive real proportions from the app's risk list, not from a fixed percentage split.

| Layer | Relative speed | Reliability | Maintenance cost | What belongs here |
|---|---|---|---|---|
| Unit | Fastest | Very high | Low | Business logic, view-model state transitions, parsing, formatting, validation |
| Integration | Fast | High | Medium | API client against a mock server, local DB and migrations, cache and sync logic, service composition |
| UI / E2E | Slow | Medium (device and timing noise) | High | Critical flows, navigation, permissions, backgrounding, deep links, visual regression |
| Manual / exploratory | Slowest | Variable | Highest per run | Real-device edge cases, accessibility feel, new-feature exploration |

## Deep-Link and Offline Scenario Entry Points

- **Android deep link, from an instrumented test:** fire the intent with `UiDevice.executeShellCommand("am start -a android.intent.action.VIEW -d '<scheme://path>'")`. Then wait on a resource-id with `device.wait(Until.hasObject(By.res("<screen-id>")), timeoutMs)` and assert on the destination content. UiAutomator is needed because the launch crosses the app boundary.
- **iOS deep link on a simulator:** use `xcrun simctl openurl booted "<url>"`. See [qa-testing-ios simulator-commands.md](../../qa-testing-ios/references/simulator-commands.md). For domain verification of Universal Links and App Links, follow the testing steps in [software-mobile deep-linking-guide.md](../../software-mobile/references/deep-linking-guide.md#deep-link-testing-and-debugging).
- **Offline:** drive the app through a mock server that can return network errors and delays, not through a real API. Assert on the queued-write and retry UI states, then restore the network and assert the sync result.

## Suite Anti-Patterns

| Anti-pattern | Why it hurts | Fix |
|---|---|---|
| Only E2E tests, no unit layer | Slow, flaky, expensive feedback | Push logic down to unit and integration layers; keep E2E for flows that need the device |
| Testing implementation details | Tests break on every refactor | Assert on behavior and outputs, not private calls or view hierarchy internals |
| Hard-coded test data inline | Brittle, hard to update | Use factories and fixtures; seed and reset through an API or launch arguments |
| Real network in UI tests | Latency and backend state become flake sources | Use a mock server or recorded fixtures; keep a small separate contract suite |
| One OS version only | Version-specific regressions escape | Cover the oldest and newest supported OS in the matrix ([device-matrix](../assets/device-matrix.md)) |
| No performance regression checks | Startup and jank degrade unnoticed | Benchmark critical paths in CI ([mobile-performance-testing.md](mobile-performance-testing.md)) |
| Never running on real devices | OEM-, thermal- and hardware-specific bugs escape | Schedule Tier 2 and Tier 3 real-device runs ([device-farm-strategies.md](device-farm-strategies.md)) |
