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

Take the current version from https://github.com/pointfreeco/swift-snapshot-testing/releases before pinning, and read the notes for fixes that affect your macOS/Xcode host (for example, perceptual-image-comparison crashes).

Use the project's `Package.resolved` and a release selected from that page; do not copy a portable version pin. Check which snapshot strategies are public in that release before changing `.dump` to the separate `SnapshotTestingCustomDump` module.

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

Use explicit recording, not accidental baseline churn — `record: .failed` rewrites the baseline whenever a comparison fails, so leaving it enabled in a shared `invokeTest()` silently absorbs real regressions into the baseline. Scope it to a deliberate re-recording pass (a local flag, an env var, or a temporary override in the one test being re-baselined), not a permanent override:

```swift
// Only when re-recording on purpose — never leave this in place for CI runs.
override func invokeTest() {
    withSnapshotTesting(record: ProcessInfo.processInfo.environment["SNAPSHOT_RECORD"] != nil ? .all : .missing) {
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

The iOS 26 SDK introduces Liquid Glass as the default rendering layer for native UI components. Existing snapshot baselines can change with the new SDK/runtime. Compare actual diffs and regenerate affected baselines after adoption. Treat this as a visual audit opportunity: review each changed snapshot before accepting it rather than bulk-accepting diffs.

## Known Bugs To Check Before Upgrading

Verify these against the upstream issue tracker before pinning a new Xcode/simulator/library combination — do not treat either as fixed without checking current issue status:

- [Issue #1089](https://github.com/pointfreeco/swift-snapshot-testing/issues/1089) reports a UIHostingController setup crash with the Xcode 26.2 / iOS 26.2 simulator pairing and package 1.19.2. Treat this as a reporter's reproduction, not proof that every project or later package release is affected. Re-check issue status and maintainer comments, then run the trivial image-snapshot probe on the exact package/SDK/runtime combination before adopting it. Select a tested runtime if it reproduces; do not claim a fixed package floor without release evidence.
- A similar report exists for Xcode 16 / iOS 18 in [issue #957](https://github.com/pointfreeco/swift-snapshot-testing/issues/957). Run the focused snapshot lane after SDK/runtime changes before accepting baseline churn.

## CI Guidance

- persist failure artifacts
- keep one stable baseline lane before expanding matrix coverage
- do not silently re-record in CI

## Swift Testing

The upstream library supports Swift Testing workflows as well as XCTest. Re-check the upstream README and release notes for the latest traits and repeated-run behavior.
