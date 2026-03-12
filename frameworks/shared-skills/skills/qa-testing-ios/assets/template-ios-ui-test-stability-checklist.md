# iOS UI Test Stability Checklist (Isolation, Determinism, Device Matrix)

Use this checklist when adding or reviewing XCUITest suites.

## Core

### Scope and Layering

- [ ] UI test protects a critical user journey (thin E2E); lower-layer tests cover most logic.
- [ ] Test name states user intent and expected outcome.

### Device Matrix

- [ ] Simulator matrix is risk-based and small (1-2 iPhones + iPad if needed).
- [ ] Real-device runs exist for nightly/release confidence.

### Determinism (Flake Control)

- [ ] Animations reduced/disabled in test configuration where possible.
- [ ] Locale/timezone fixed (no “works on my locale”).
- [ ] Time control: avoid wall-clock dependencies; use injectable clocks where possible.
- [ ] Network: avoid real third-party calls in UI tests; stub boundaries.
- [ ] Permissions: predictable permission state (camera/photos/notifications/location).

### Isolation

- [ ] Tests are order-independent and parallel-safe where applicable.
- [ ] App state reset between tests (fresh install or explicit reset flow).
- [ ] No shared accounts/tenants unless isolated by test-run namespace.

### Test Data

- [ ] Data builders/factories exist for required accounts and content.
- [ ] Cleanup is deterministic (no leaking records into the next test run).

### CI Ergonomics

- [ ] `xcodebuild test` writes an `xcresult` bundle (`-resultBundlePath TestResults.xcresult`) for artifacts.
- [ ] Failing tests capture screenshots/logs and attach to the `xcresult` bundle.
- [ ] Simulator setup is automated (boot/erase as needed via `simctl`: https://developer.apple.com/documentation/xcode/simctl).

### Debugging Ergonomics

- [ ] Failure output includes: scheme, destination, device, OS, and `xcresult` location.
- [ ] Rerun policy is explicit: rerun-pass tests are treated as flakes with a ticket and owner.

## Optional: AI / Automation

Do:
- Use AI to expand test ideas from user journeys and failure modes; automate only deterministic cases.
- Use AI to summarize `xcresult` output and cluster failures; verify by reproducing with controlled conditions.

Avoid:
- Generating UI tests that rely on sleeps/timing rather than state-based assertions.
