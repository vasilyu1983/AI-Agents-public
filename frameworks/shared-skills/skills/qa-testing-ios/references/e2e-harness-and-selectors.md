# E2E Harness And Selectors

Use this reference when a native iOS suite needs deterministic app-side fixtures, stable XCUITest selectors, or a release-safe landing pattern for a new end-to-end flow.

## Table of Contents

- [Deterministic E2E Fixture Harness](#deterministic-e2e-fixture-harness)
- [Rules For The Harness](#rules-for-the-harness)
- [Accessibility Identifiers vs Labels](#accessibility-identifiers-vs-labels)
- [Atomic Commit Pattern](#atomic-commit-pattern)
- [Multi-Account And Backend Parity Scenarios](#multi-account-and-backend-parity-scenarios)
- [SwiftUI Compiler Diagnostic Failures](#swiftui-compiler-diagnostic-failures)

## Deterministic E2E Fixture Harness

The canonical pattern for native iOS E2E suites that must run without live backend credentials. Use the same approach for auth flows, referral programs, onboarding, billing, and any other feature where hitting a real backend would introduce flake, network dependency, or per-user state leakage.

The pattern uses three launch-environment flags to switch the app into deterministic fixture-backed mode, plus one global reset hook that guarantees per-test idempotency.

```swift
// XCUITest side — launch environment sets the app into fixture mode
final class ReferralProgramE2ETests: XCTestCase {
    private func launchApp(
        userVariant: String,
        resetReferralScenario: Bool = false
    ) -> XCUIApplication {
        let app = XCUIApplication()
        app.launchEnvironment["UITEST_RESET_STATE"] = "1"                   // clear keychain, caches
        app.launchEnvironment["UITEST_AUTH_STATE"] = "signed_in"           // bypass auth screens
        app.launchEnvironment["UITEST_FEATURE_FIXTURES"] = "1"             // app reads fixture data instead of real API
        app.launchEnvironment["UITEST_USER_VARIANT"] = userVariant         // inviter, referred, paid, free, etc.
        app.launchEnvironment["UITEST_INITIAL_PATH"] = "/settings"         // land on target surface directly
        if resetReferralScenario {
            app.launchEnvironment["UITEST_RESET_REFERRAL_FIXTURES"] = "1"  // reset per-feature fixture ledger
        }
        app.launch()
        XCTAssertTrue(app.wait(for: .runningForeground, timeout: 5))
        return app
    }
}
```

```swift
// App side — AuthSession picks the SessionUser from a fixture store by variant
func restoreIfPossible() async {
    if ProcessInfo.processInfo.environment["UITEST_AUTH_STATE"] == "signed_in" {
        currentUser = UITestFixtures.sessionUser(for: UITestHarness.userVariant)
        status = .signedIn
        return
    }
    // real auth path
}

// App side — feature screens branch on the fixture flag
private func loadData() async {
    if UITestHarness.isFeatureFixturesEnabled {
        let sessionUser = model.session.currentUser
        stats = UITestFixtures.referralStatsResponse(for: sessionUser)
        loadState = .loaded
        return
    }
    // real API call path
}

// App side — global reset hook in AppModel (fires when UITEST_RESET_STATE=1)
func resetForUITests() async {
    TokenStore.shared.clear()
    await cache.resetForUITests()
    if UITestHarness.isFeatureFixturesEnabled, UITestHarness.shouldResetReferralFixtures {
        UITestFixtures.resetReferralScenario()
    }
}
```

## Rules For The Harness

1. Never hardcode a single test user in UITest auth paths. Route every `signed_in` state through `UITestFixtures.sessionUser(for: variant)` so each suite can request its own isolated user (`inviter`, `referred`, `paid`, `free`, `web_subscriber`).
2. Fixture data must be `MainActor`-isolated and deterministic. No randomness, no `Date()`-derived timestamps, no ordering dependent on dictionary iteration.
3. Per-feature reset hooks are opt-in via a second flag such as `UITEST_RESET_REFERRAL_FIXTURES=1`, so tests that want a clean slate request it explicitly.
4. Keep the fixture branch in the same function as the real path. `if UITestHarness.isFeatureFixturesEnabled { … return }` at the top of `loadData()` is easier to audit than a protocol-switched data source hidden elsewhere.
5. Every tappable element in the test path needs `.accessibilityIdentifier()`, not just `.accessibilityLabel()`. Identifiers are stable strings for XCUITest; labels are localized strings for VoiceOver.

## Accessibility Identifiers vs Labels

XCUITest needs stable, locale-independent selectors. VoiceOver needs human-readable, localized announcements. These are different properties and a reliable E2E suite treats them separately.

```swift
PrimaryActionButton(
    title: l10n.text("nativeApp.settings.referrals.applyButton", fallback: "Apply"),
    fullWidth: true
) {
    Task { await applyReferralCode() }
}
.accessibilityIdentifier("referrals.applyButton")
.accessibilityLabel(l10n.text("nativeApp.settings.referrals.applyButton", fallback: "Apply"))
.disabled(applyCode.isEmpty || applyState == .applying)
```

Rules:

- `.accessibilityIdentifier()`: dot-namespaced, lowercased, stable across localizations, and matched by XCUITest. Never localize it.
- `.accessibilityLabel()`: localized and user-facing. Used by VoiceOver, not by tests.
- Apply the identifier at the outermost interactive view in the composition, not inside a nested `Label` or `Text`.
- Any identifier used in assertions becomes a stable contract. Renaming it breaks every test that references the old string.
- Before landing a new E2E suite, walk every tappable element in the flow and confirm each has a unique identifier. Missing identifiers force fallback to label-based matching, which breaks under localization.

## Atomic Commit Pattern

When you land a new E2E suite, ship all of these in the same commit:

1. The new test file in the UI-test target directory
2. Every `.accessibilityIdentifier()` call the test depends on
3. The fixture data and reset hook in the app-side fixture store
4. The reset-hook wiring in `AppModel.resetForUITests()` or equivalent
5. The regenerated `project.pbxproj` if the project uses XcodeGen
6. Any runbook updates that list the new suite as a release gate

The reason is coupling: every item on the list is a prerequisite for every other item. Splitting this across multiple commits produces a sequence where at least one intermediate state is broken.

The one exception is when the prerequisite already exists and only needs a trivial scenario entry, such as adding one more fixture variant to an existing deterministic harness.

Verify the full suite with the repo’s canonical iOS test script and require a three-in-a-row pass for any UI test that feels flaky on first run.

## Multi-Account And Backend Parity Scenarios

- Onboarding detection across account lifecycle: delete and recreate an account with the same email, then verify onboarding still triggers. Old `UserDefaults` flags must not suppress onboarding for the new account.
- Stale cache across sign-out/sign-in: sign out, sign in as a different user, and confirm no cached flags leak across sessions.
- Web vs API tier parity: verify the API returns the same access level as the web experience for equivalent users, especially around subscription rows and fallback tiers.
- OTP email verification flow: verify confirmation emails include both the magic link and the 6-digit code, auto-submit works on the sixth digit, resend cooldown works, and `.textContentType(.oneTimeCode)` is set.
- Apple Sign-In requires a physical device: first-sign-in testing must verify the full name is persisted because Apple only sends it once.
- Hybrid email template parity: if both magic link and OTP code exist in the same email, verify web confirmation and iOS OTP entry both work, and using one method does not invalidate the other prematurely.

## SwiftUI Compiler Diagnostic Failures

Swift sometimes crashes during type inference with `failed to produce diagnostic for expression` errors. This is usually a compiler limitation around complex `@ViewBuilder` expressions, not a code logic bug.

Common triggers:

- `.contentTransition(.numericText)` combined with complex optional `Int` expressions
- Large `@ViewBuilder` bodies with many conditional branches and inline `Canvas` views
- `AnyView?` computed properties later unwrapped with `if let`

Fixes in order of preference:

1. Inline the optional view directly with `if let` in the `@ViewBuilder` body instead of extracting it to a computed `AnyView?`
2. Remove `.contentTransition(.numericText)` if the visual gain is minor
3. Split the large `@ViewBuilder` body into smaller extracted views that return concrete types
4. Add explicit type annotations to help the constraint solver

Example before:

```swift
private var moonPhaseBadge: AnyView? {
    guard let moonPhase = day.moonPhase else { return nil }
    return AnyView(HStack { ... })
}
// In body: if let moonPhaseBadge { moonPhaseBadge }
```

Example after:

```swift
if let moonPhase = day.moonPhase, !moonPhase.isEmpty {
    HStack { ... }
}
```
