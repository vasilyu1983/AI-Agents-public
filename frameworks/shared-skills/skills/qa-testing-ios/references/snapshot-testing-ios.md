# Snapshot Testing For iOS

Visual and structural snapshot testing guidance for iOS projects.

Primary upstream:

- https://github.com/pointfreeco/swift-snapshot-testing
- https://github.com/pointfreeco/swift-snapshot-testing/releases

## Table of Contents

- [Versioning Rule](#versioning-rule)
- [When To Use Snapshot Tests](#when-to-use-snapshot-tests)
- [Baseline Example](#baseline-example)
- [Recording](#recording)
- [Useful Strategies](#useful-strategies)
- [SwiftUI Example](#swiftui-example)
- [Flake Prevention](#flake-prevention)
- [Known Bugs To Check Before Upgrading](#known-bugs-to-check-before-upgrading)
- [CI Guidance](#ci-guidance)
- [Swift Testing](#swift-testing)

## Versioning Rule

Re-check the upstream releases page before copying a version pin. As of July 2026, the latest release is 1.19.3 (1.19.2 shipped shortly before it). Verify at https://github.com/pointfreeco/swift-snapshot-testing/releases before pinning.

```swift
.package(url: "https://github.com/pointfreeco/swift-snapshot-testing", from: "1.19.0")
```

If the repo has already standardized on another tested version, follow the repo, not this example. Recent releases added a `.customDump` strategy (in a separate `SnapshotTestingCustomDump` module) and Android support; `.dump` is now soft-deprecated in favor of `.customDump` — prefer it for new suites.

## When To Use Snapshot Tests

- stable visual rendering for critical screens or components
- structural assertions where screenshots are too brittle
- cross-state verification for SwiftUI or UIKit views

Avoid using snapshot tests as a substitute for:

- logic tests
- accessibility audits
- end-to-end behavior tests

## Baseline Example

```swift
import SnapshotTesting
import XCTest
@testable import MyApp

final class LoginViewSnapshotTests: XCTestCase {
    func testDefaultState() {
        let view = LoginView(
            state: .init(email: "", password: "", isLoading: false)
        )

        assertSnapshot(of: view, as: .image)
    }
}
```

## Recording

Use explicit recording, not accidental baseline churn.

```swift
override func invokeTest() {
    withSnapshotTesting(record: .failed) {
        super.invokeTest()
    }
}

func testLoadingState() {
    let view = LoginView(state: .loading)
    assertSnapshot(of: view, as: .image, named: "loading")
}
```

## Useful Strategies

```swift
assertSnapshot(of: view, as: .image)
assertSnapshot(of: view, as: .recursiveDescription)
assertSnapshot(of: model, as: .dump)
```

Note: upstream now treats `.dump` as older guidance for some cases. Prefer upstream release notes when choosing between `.dump` and newer strategies.

## SwiftUI Example

```swift
import SnapshotTesting
import SwiftUI
import XCTest

final class ProfileViewTests: XCTestCase {
    func testProfileView() {
        let view = ProfileView(user: .preview, isEditing: false)

        assertSnapshot(
            of: view,
            as: .image(layout: .device(config: .iPhone13))
        )
    }
}
```

The exact device preset is less important than consistency. Keep the chosen layout stable across contributors and CI.

## Flake Prevention

- record snapshots on a stable macOS and Xcode baseline
- fix locale, region, dynamic type, appearance, and content state
- use status-bar overrides for screenshot realism only when needed
- avoid live clocks, live networking, and non-deterministic animations
- keep snapshot coverage focused on high-value UI states

### iOS 26 Liquid Glass Baseline Migration

The iOS 26 SDK introduces Liquid Glass as the default rendering layer for native UI components. Existing snapshot baselines recorded on iOS 18 or earlier will fail against the iOS 26 simulator. Plan a one-time baseline regeneration pass after adopting Xcode 26. Treat this as a visual audit opportunity: review each changed snapshot before accepting it rather than bulk-accepting diffs.

## Known Bugs To Check Before Upgrading

Verify these against the upstream issue tracker before pinning a new Xcode/simulator/library combination — do not treat either as fixed without checking current issue status:

- **Xcode 26.2 + iOS 26.2 simulator crash (open as of mid-2026):** swift-snapshot-testing 1.19.2 crashes immediately in `add(traits:viewController:to:)` when asserting any snapshot — even a trivial `Text("hello")` — against an iOS 26.2 simulator, across every snapshot strategy. Tracked at [pointfreeco/swift-snapshot-testing#1089](https://github.com/pointfreeco/swift-snapshot-testing/issues/1089). Before upgrading a project's simulator runtime to iOS 26.2 (or Xcode to 26.2), check this issue's current status; if unresolved, pin the simulator OS one minor version back for the snapshot-test lane rather than blocking the whole suite.
- This is a recurring pattern with this library: a very similar UIHostingController-setup crash occurred on an earlier Xcode 16 / iOS 18 pairing (issue #957). Whenever a new Xcode/iOS simulator pairing ships, budget a quick smoke check of the snapshot-test lane before trusting it in CI, rather than assuming SDK-only changes are always visual-diff-only.

## CI Guidance

- persist failure artifacts
- keep one stable baseline lane before expanding matrix coverage
- do not silently re-record in CI

## Swift Testing

The upstream library supports Swift Testing workflows as well as XCTest. Re-check the upstream README and release notes for the latest traits and repeated-run behavior.
