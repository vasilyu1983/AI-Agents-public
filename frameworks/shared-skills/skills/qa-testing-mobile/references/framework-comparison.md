# Mobile Test Framework Comparison

## Contents

- Defaults (2026)
- Decision Matrix
- When to Use Each
- Recommendation by App Type
- Hybrid Strategy
- CI Integration Patterns
- Cost Considerations

## Defaults (2026)

- Prefer first-party frameworks (XCUITest + Espresso/Compose) for PR gates and smoke coverage.
- Add app-specific cross-platform frameworks (Detox for React Native; Flutter `integration_test`/Patrol for Flutter) when they reduce total maintenance.
- Use Appium when you truly need one codebase across iOS + Android (accept higher cost/flake).
- Use Maestro for fast-to-author, black-box smoke flows (treat as complementary, not a full replacement).
- Keep unit tests in native stacks (Swift Testing/XCTest; JUnit) and treat UI automation as a smaller, higher-cost layer.

## Decision Matrix

| Framework | Best for | Platform | Speed | Reliability | Setup | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| XCUITest (XCTest UI) | iOS native UI tests | iOS | Fast | High | Low | Deep OS integration; best simulator ergonomics |
| Espresso / Compose UI Testing | Android native UI tests | Android | Fast | High | Low | Best sync with UI thread; Compose tests are first-class |
| UIAutomator | System-level Android flows | Android | Medium | Medium | Medium | Cross-app/system dialogs, notifications, Settings |
| Detox | React Native E2E | iOS + Android | Fast | High | Medium | Gray-box sync with RN bridge; requires app wiring |
| Flutter `integration_test` + Patrol | Flutter E2E | iOS + Android | Fast | High | Medium | Prefer to Appium for Flutter; app wiring required |
| Maestro | Cross-platform smoke flows | iOS + Android | Fast | Medium | Low | YAML-driven; black-box; great for breadth, not deep assertions |
| Appium (v2) | One test codebase for many apps | iOS + Android | Slow | Medium | High | Most flexible, most overhead; higher flake risk |

## When to Use Each

### XCUITest (iOS Native UI)

**Best for**: iOS-only apps, teams with Swift expertise.

**Pros**:

- First-party Apple support, always up-to-date.
- Fast execution, runs in-process.
- Deep OS integration (accessibility, permissions).
- No external dependencies.

**Cons**:

- iOS only, no cross-platform.
- Parallelization is possible, but requires careful test isolation and infrastructure.

### Espresso / Compose (Android Native UI)

**Best for**: Android-only apps, teams with Kotlin expertise.

**Pros**:

- First-party Google support.
- Synchronization with UI thread (fewer flakes).
- Fast execution.
- Excellent Android Studio integration.

**Cons**:

- Android only.
- Complex gestures and cross-app flows may need UIAutomator.

### Maestro (Cross-Platform Smoke)

**Best for**: Fast-to-author smoke tests across iOS + Android, onboarding, and regression breadth.

**Pros**:

- Very fast authoring; readable YAML scenarios.
- Works well for "happy path" coverage and broad device/language coverage.

**Cons**:

- Limited for deep assertions and complex app-internal state.
- Still needs the same flake disciplines (stable selectors, determinism, controlled state).

### Appium (Cross-Platform, Black-Box)

**Best for**: Cross-platform apps needing single test codebase, teams with existing Selenium expertise.

**Pros**:

- Write once, run on iOS and Android.
- Language-agnostic (Python, JS, Java, Ruby).
- Large community and ecosystem.
- Works with native, hybrid, and web apps.

**Cons**:

- Slower than native frameworks (uses WebDriver protocol).
- Higher flake rate due to indirection.
- Complex setup with multiple dependencies.
- Maintenance overhead keeping drivers in sync.

### Detox (React Native Gray-Box)

**Best for**: React Native apps.

**Pros**:

- Gray-box testing with JS bridge access.
- Automatic synchronization with React Native.
- Fast execution.
- Good flake resistance.

**Cons**:

- React Native only.
- Requires Detox-specific app configuration.
- Smaller community than Appium.

## Recommendation by App Type

| App Type | Primary Framework | Secondary |
| --- | --- | --- |
| iOS native | XCUITest | - |
| Android native | Espresso / Compose | UIAutomator for system dialogs |
| React Native | Detox | Appium for edge cases |
| Flutter | Flutter `integration_test` + Patrol | Appium for edge cases |
| Cross-platform (other) | Maestro (smoke) | Appium for deep automation |
| Hybrid WebView | Playwright (web layer) | Appium for native shell |

## Hybrid Strategy

Many teams use multiple frameworks:

1. **Native frameworks for speed**: XCUITest/Espresso for smoke tests in CI.
2. **App-specific cross-platform**: Detox (RN) or Patrol (Flutter) for shared coverage.
3. **Black-box smoke**: Maestro to expand breadth across devices/regions.
4. **Cross-platform fallback**: Appium for hard-to-reach areas and legacy coverage.
5. **Manual for exploratory**: Real devices for UX, edge cases, and "unknown unknowns".

## CI Integration Patterns

### Native (Fast Feedback)

```yaml
# Run on every PR
- XCUITest smoke suite (5 min)
- Espresso smoke suite (5 min)
```

### Cross-Platform (Nightly)

```yaml
# Run nightly on device farm
- Appium full regression (30 min)
- Multiple device configurations
```

## Cost Considerations

| Framework | Device Farm Cost | Maintenance Cost |
| --- | --- | --- |
| XCUITest | Low (simulators) | Low |
| Espresso | Low (emulators) | Low |
| Detox | Medium | Medium |
| Maestro | Medium | Medium |
| Appium | High (real devices) | High |
