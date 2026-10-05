# XCUITest Patterns

Authoring guidance for iOS UI tests that survive CI and platform drift.

Primary docs:

- https://developer.apple.com/documentation/xctest/user_interface_tests
- https://developer.apple.com/documentation/xcode/testing-your-apps-in-xcode

## Table of Contents

- [Defaults](#defaults)
- [Baseline Test](#baseline-test)
- [Page Objects](#page-objects)
- [Selector Strategy](#selector-strategy)
- [Wait Strategy](#wait-strategy)
- [Launch Hooks](#launch-hooks)
- [Permissions](#permissions)
- [Flake Triage](#flake-triage)
- [Review Checklist](#review-checklist)

## Defaults

- use accessibility identifiers first
- keep journeys thin and business-critical
- make app state explicit through launch arguments and launch environment
- prefer state-based waits over timing guesses
- isolate every test so it can run alone or in parallel

## Baseline Test

```swift
import XCTest

final class LoginUITests: XCTestCase {
    private var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false

        app = XCUIApplication()
        app.launchArguments = ["--uitesting", "--reset-state", "--disable-animations"]
        app.launchEnvironment["API_BASE_URL"] = "http://localhost:8080"
        app.launch()
    }

    func testSuccessfulLogin() {
        app.textFields["emailField"].tap()
        app.textFields["emailField"].typeText("user@example.com")

        app.secureTextFields["passwordField"].tap()
        app.secureTextFields["passwordField"].typeText("password123")

        app.buttons["submitButton"].tap()

        XCTAssertTrue(app.navigationBars["Dashboard"].waitForExistence(timeout: 5))
    }
}
```

## Page Objects

Page objects help when:

- a screen is used in many tests
- selectors and waits should be centralized
- the flow is easier to read as intent than as raw element operations

Keep page objects thin. Do not hide assertions, navigation, and setup so deeply that failures become opaque.

## Selector Strategy

Prefer:

1. accessibility identifiers
2. scoped queries inside known containers
3. predicate queries only when identifiers are not available

Avoid:

- index-based selectors
- brittle label-only queries for localized UIs
- selectors copied from recorded scripts without review

## Wait Strategy

Use:

- `waitForExistence`
- expectations for state transitions
- polling on a specific, user-visible state

Avoid:

- `sleep`
- long blanket timeouts used to hide race conditions
- tapping elements before they are hittable or visible

## Launch Hooks

Typical UI-test hooks:

- `--uitesting`
- `--reset-state`
- `--disable-animations`
- stub-server base URL
- signed-in or seed-data shortcuts only for flows that are not explicitly testing auth

The app code should own these hooks explicitly and make them no-ops outside test mode.

## Permissions

Keep permissions deterministic:

- pre-grant or reset simulator permissions when possible
- isolate tests that must interact with real permission prompts
- avoid broad alert-handling code that blindly taps buttons

## Flake Triage

When a UI test fails:

1. inspect `xcresult`
2. rerun one test with `-only-testing`
3. decide whether the failure is selector, wait, state, permission, or environment drift
4. only then consider repetition flags

## UI Automation Recording (Xcode 26)

Xcode 26 ships a completely new code-generation system for **UI automation recording** (WWDC25 session 247; dedicated session: "Record, replay, and review: UI automation with Xcode", WWDC25 session 344). It changes the authoring flow but does not change the flake-control discipline required of every XCUITest.

### What it does

Place the cursor inside a test method body and click **Start Recording** in the editor gutter. Xcode builds and relaunches the app in Simulator. Every interaction you perform is translated in real time into generated Swift XCTest code. Stop recording when done.

Generated code includes multiple identifier options per element, selectable via inline dropdowns.

### What it generates

- Swift XCTest method bodies calling `XCUIApplication` queries and interaction APIs (`tap()`, `typeText()`, etc.)
- Multiple query alternatives per element (accessibility identifier, label, predicate) — you choose the one to keep
- The same `XCUIApplication` / `XCUIElement` types hand-authored tests use; there is no separate generated test format

### Flake discipline still applies — recording is not a flake fix

Recording eliminates manual query typing; it does not produce stable tests on its own. Apply the full selector and wait discipline from this document on top of every recorded test:

- **Review every generated query.** Apple's own guidance: prefer accessibility identifiers; for deeply nested views, choose the shortest possible query; for dynamic content (timestamps, server-driven values), use a generic query. Queries copied from recording without review are a known flake source (see `## Selector Strategy`).
- **Generated tests contain no waits.** Add `waitForExistence` and state-based expectations everywhere the app may be mid-transition at the time an element is tapped.
- **Launch hooks are absent from recorded output.** Recorded tests launch the app with no arguments or environment overrides. Add `--uitesting`, `--reset-state`, `--disable-animations`, and stub-server URLs in `setUp()` (see `## Launch Hooks`).
- **State isolation is not provided.** The recording captures a single live session. Every test still needs `setUp`/`tearDown` reset discipline to run independently.

### Practical workflow

1. Write the `setUp` harness (launch hooks, state reset) before recording.
2. Record the interaction sequence into the test body.
3. Open the inline query dropdowns and select accessibility identifiers where available.
4. Add `waitForExistence` calls before any tap that may race with a transition.
5. Add assertions (`XCTAssertTrue`, `wait(for:toEqual:)`) — recording does not insert them.
6. Run with `-only-testing` and verify the test is deterministic across 3+ runs before merging.

Primary sources: [Recording UI automation for testing](https://developer.apple.com/documentation/XCUIAutomation/recording-ui-automation-for-testing) · [WWDC25 session 344](https://developer.apple.com/videos/play/wwdc2025/344/) · [WWDC25 session 247](https://developer.apple.com/videos/play/wwdc2025/247/)

## Review Checklist

- the test proves a user outcome, not a long incidental journey
- selectors are semantic and stable
- launch arguments and environment remove hidden dependencies
- the test can run with `-only-testing` and reproduce the same behavior
- if the test was started from recording: every generated query reviewed and identifiers preferred; waits added; launch hooks added; assertions added
