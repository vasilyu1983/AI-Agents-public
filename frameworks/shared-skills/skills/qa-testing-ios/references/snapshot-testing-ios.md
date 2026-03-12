# Snapshot Testing for iOS

Visual snapshot testing patterns for iOS applications using swift-snapshot-testing.

**Library**: [swift-snapshot-testing](https://github.com/pointfreeco/swift-snapshot-testing) (Point-Free)

## Contents

- [Setup and Configuration](#setup-and-configuration)
- [Recording vs Verifying](#recording-vs-verifying)
- [Snapshot Strategies](#snapshot-strategies)
- [SwiftUI Snapshot Testing](#swiftui-snapshot-testing)
- [UIKit Snapshot Testing](#uikit-snapshot-testing)
- [Device Sizes and Orientations](#device-sizes-and-orientations)
- [Dark Mode Testing](#dark-mode-testing)
- [Dynamic Type Testing](#dynamic-type-testing)
- [CI Integration](#ci-integration)
- [Handling Diffs and Updating Baselines](#handling-diffs-and-updating-baselines)
- [Perceptual Diff Tools](#perceptual-diff-tools)
- [Flake Prevention](#flake-prevention)
- [Related Resources](#related-resources)

---

## Setup and Configuration

### Swift Package Manager

```swift
// Package.swift dependency
.package(url: "https://github.com/pointfreeco/swift-snapshot-testing", from: "1.17.0"),

// Target dependency
.testTarget(
    name: "MyAppTests",
    dependencies: [
        .product(name: "SnapshotTesting", package: "swift-snapshot-testing"),
    ]
)
```

### Xcode Project (SPM)

```text
1. File > Add Package Dependencies
2. URL: https://github.com/pointfreeco/swift-snapshot-testing
3. Add "SnapshotTesting" to your test target
```

### Basic Test Structure

```swift
import XCTest
import SnapshotTesting
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

---

## Recording vs Verifying

### Recording Mode

When a reference image does not exist, the test fails and records a new baseline. You can also force recording.

```swift
// Method 1: Set globally (record all snapshots in this test run)
// Useful when first creating tests or after major UI changes
override func invokeTest() {
    withSnapshotTesting(record: .all) {
        super.invokeTest()
    }
}

// Method 2: Per-assertion recording
func testNewComponent() {
    let view = NewFeatureView()
    assertSnapshot(of: view, as: .image, record: .all)
}

// Method 3: Environment variable
// Set SNAPSHOT_TESTING_RECORD=all in scheme environment variables
```

### Verify Mode (Default)

```swift
func testLoginView() {
    let view = LoginView(state: .default)

    // Compares against existing reference image
    // Fails if reference does not exist (records and fails)
    // Fails if pixel differences detected
    assertSnapshot(of: view, as: .image)
}
```

### Named Snapshots

```swift
func testLoginStates() {
    let defaultView = LoginView(state: .default)
    assertSnapshot(of: defaultView, as: .image, named: "default")

    let loadingView = LoginView(state: .loading)
    assertSnapshot(of: loadingView, as: .image, named: "loading")

    let errorView = LoginView(state: .error("Invalid credentials"))
    assertSnapshot(of: errorView, as: .image, named: "error")
}
```

Reference images are stored at:
```text
__Snapshots__/
  LoginViewSnapshotTests/
    testLoginStates.default.png
    testLoginStates.loading.png
    testLoginStates.error.png
```

---

## Snapshot Strategies

### Image Strategy (Most Common)

```swift
// Default image snapshot
assertSnapshot(of: view, as: .image)

// With specific size
assertSnapshot(of: view, as: .image(size: CGSize(width: 375, height: 667)))

// With traits (device traits)
assertSnapshot(of: view, as: .image(
    traits: UITraitCollection(userInterfaceStyle: .dark)
))
```

### Recursive Description Strategy

Captures the view hierarchy as text. Useful for structural testing without pixel sensitivity.

```swift
func testViewHierarchy() {
    let vc = LoginViewController()
    vc.loadViewIfNeeded()

    assertSnapshot(of: vc, as: .recursiveDescription)
}

// Output looks like:
// <UIView; frame = (0 0; 375 667)>
//   <UITextField; frame = (20 100; 335 44); text = ''>
//   <UITextField; frame = (20 160; 335 44); text = ''>
//   <UIButton; frame = (20 220; 335 50); title = 'Log In'>
```

### Dump Strategy

Captures the full Swift Mirror dump of an object. Useful for testing non-visual models.

```swift
func testUserModel() {
    let user = User(
        id: "123",
        name: "Jane Doe",
        email: "jane@example.com",
        role: .admin
    )
    assertSnapshot(of: user, as: .dump)
}
```

### Custom Strategy Composition

```swift
// Combine multiple strategies in one test
func testLoginViewAllStrategies() {
    let vc = LoginViewController()
    vc.loadViewIfNeeded()

    // Visual appearance
    assertSnapshot(of: vc, as: .image, named: "visual")

    // View hierarchy structure
    assertSnapshot(of: vc, as: .recursiveDescription, named: "hierarchy")

    // Accessibility audit
    assertSnapshot(of: vc, as: .recursiveDescription(on: .init(
        preferredContentSizeCategory: .accessibilityExtraLarge
    )), named: "accessibility")
}
```

---

## SwiftUI Snapshot Testing

### Basic SwiftUI Snapshots

```swift
import SwiftUI
import SnapshotTesting
import XCTest

final class ProfileViewTests: XCTestCase {
    func testProfileView() {
        let view = ProfileView(
            user: .preview,
            isEditing: false
        )

        assertSnapshot(
            of: view,
            as: .image(layout: .device(config: .iPhone13))
        )
    }

    func testProfileEditMode() {
        let view = ProfileView(
            user: .preview,
            isEditing: true
        )

        assertSnapshot(
            of: view,
            as: .image(layout: .device(config: .iPhone13)),
            named: "editing"
        )
    }
}
```

### Layout Options

```swift
// Fixed size
assertSnapshot(of: view, as: .image(layout: .fixed(width: 375, height: 200)))

// Size that fits content
assertSnapshot(of: view, as: .image(layout: .sizeThatFits))

// Device configuration
assertSnapshot(of: view, as: .image(layout: .device(config: .iPhone13)))
assertSnapshot(of: view, as: .image(layout: .device(config: .iPadPro11)))
```

### Testing SwiftUI Previews

```swift
// In your app: define Preview providers
struct ProfileView_Previews: PreviewProvider {
    static var previews: some View {
        Group {
            ProfileView(user: .preview, isEditing: false)
                .previewDisplayName("Default")

            ProfileView(user: .preview, isEditing: true)
                .previewDisplayName("Editing")
        }
    }
}

// In test target: snapshot each preview state
final class ProfileViewPreviewTests: XCTestCase {
    func testDefault() {
        assertSnapshot(
            of: ProfileView(user: .preview, isEditing: false),
            as: .image(layout: .device(config: .iPhone13)),
            named: "default"
        )
    }

    func testEditing() {
        assertSnapshot(
            of: ProfileView(user: .preview, isEditing: true),
            as: .image(layout: .device(config: .iPhone13)),
            named: "editing"
        )
    }
}
```

---

## UIKit Snapshot Testing

### View Controller Snapshots

```swift
func testSettingsViewController() {
    let vc = SettingsViewController()
    vc.viewModel = SettingsViewModel(
        user: .preview,
        preferences: .defaultPreferences
    )

    // Load view hierarchy
    vc.loadViewIfNeeded()

    assertSnapshot(of: vc, as: .image(on: .iPhone13))
}
```

### Individual View Snapshots

```swift
func testCustomCard() {
    let card = ProductCardView()
    card.configure(with: ProductCardViewModel(
        title: "Premium Widget",
        price: "$29.99",
        rating: 4.5,
        imageURL: nil  // use placeholder
    ))

    // Set intrinsic size
    card.frame = CGRect(x: 0, y: 0, width: 343, height: 200)
    card.layoutIfNeeded()

    assertSnapshot(of: card, as: .image)
}
```

### Navigation Controller Snapshots

```swift
func testNavigationFlow() {
    let vc = OrderDetailViewController()
    vc.order = Order.preview
    let nav = UINavigationController(rootViewController: vc)

    assertSnapshot(of: nav, as: .image(on: .iPhone13))
}
```

---

## Device Sizes and Orientations

### Multiple Device Sizes

```swift
final class ResponsiveLayoutTests: XCTestCase {
    let view = DashboardView(state: .preview)

    func testIPhoneSE() {
        assertSnapshot(of: view,
                       as: .image(layout: .device(config: .iPhoneSe)),
                       named: "iPhone-SE")
    }

    func testIPhone13() {
        assertSnapshot(of: view,
                       as: .image(layout: .device(config: .iPhone13)),
                       named: "iPhone-13")
    }

    func testIPhone15ProMax() {
        assertSnapshot(of: view,
                       as: .image(layout: .device(config: .iPhone13ProMax)),
                       named: "iPhone-15-Pro-Max")
    }

    func testIPadPro11() {
        assertSnapshot(of: view,
                       as: .image(layout: .device(config: .iPadPro11)),
                       named: "iPad-Pro-11")
    }
}
```

### Landscape Orientation

```swift
func testLandscape() {
    let vc = VideoPlayerViewController()
    vc.loadViewIfNeeded()

    assertSnapshot(
        of: vc,
        as: .image(on: .iPhone13(.landscape))
    )
}
```

### Parameterized Device Testing

```swift
final class MultiDeviceTests: XCTestCase {
    struct DeviceConfig {
        let name: String
        let config: ViewImageConfig
    }

    let devices: [DeviceConfig] = [
        .init(name: "iPhone-SE", config: .iPhoneSe),
        .init(name: "iPhone-13", config: .iPhone13),
        .init(name: "iPhone-13-Pro-Max", config: .iPhone13ProMax),
        .init(name: "iPad-Pro-11", config: .iPadPro11),
    ]

    func testOnboardingAcrossDevices() {
        let view = OnboardingView(step: .welcome)

        for device in devices {
            assertSnapshot(
                of: view,
                as: .image(layout: .device(config: device.config)),
                named: device.name
            )
        }
    }
}
```

---

## Dark Mode Testing

```swift
final class ThemeSnapshotTests: XCTestCase {
    func testSettingsLight() {
        let view = SettingsView(preferences: .default)
        assertSnapshot(
            of: view,
            as: .image(
                layout: .device(config: .iPhone13),
                traits: UITraitCollection(userInterfaceStyle: .light)
            ),
            named: "light"
        )
    }

    func testSettingsDark() {
        let view = SettingsView(preferences: .default)
        assertSnapshot(
            of: view,
            as: .image(
                layout: .device(config: .iPhone13),
                traits: UITraitCollection(userInterfaceStyle: .dark)
            ),
            named: "dark"
        )
    }
}

// Helper for both modes
extension XCTestCase {
    func assertSnapshotInBothModes<V: View>(
        _ view: V,
        config: ViewImageConfig = .iPhone13,
        file: StaticString = #file,
        testName: String = #function,
        line: UInt = #line
    ) {
        assertSnapshot(
            of: view,
            as: .image(
                layout: .device(config: config),
                traits: .init(userInterfaceStyle: .light)
            ),
            named: "light",
            file: file, testName: testName, line: line
        )
        assertSnapshot(
            of: view,
            as: .image(
                layout: .device(config: config),
                traits: .init(userInterfaceStyle: .dark)
            ),
            named: "dark",
            file: file, testName: testName, line: line
        )
    }
}

// Usage
func testProfileCard() {
    assertSnapshotInBothModes(ProfileCardView(user: .preview))
}
```

---

## Dynamic Type Testing

```swift
final class AccessibilitySnapshotTests: XCTestCase {
    let contentSizes: [(String, UIContentSizeCategory)] = [
        ("xs", .extraSmall),
        ("default", .large),
        ("xl", .extraLarge),
        ("xxxl", .accessibilityExtraExtraExtraLarge),
    ]

    func testOrderSummaryDynamicType() {
        let view = OrderSummaryView(order: .preview)

        for (name, size) in contentSizes {
            assertSnapshot(
                of: view,
                as: .image(
                    layout: .device(config: .iPhone13),
                    traits: UITraitCollection(preferredContentSizeCategory: size)
                ),
                named: name
            )
        }
    }
}
```

---

## CI Integration

### GitHub Actions

```yaml
name: Snapshot Tests
on: [pull_request]

jobs:
  snapshot-tests:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4
        with:
          lfs: true  # if snapshots stored in LFS

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_16.0.app

      - name: Run snapshot tests
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 15,OS=18.0' \
            -only-testing:MyAppTests/SnapshotTests \
            -resultBundlePath SnapshotResults.xcresult

      - name: Upload failure diffs
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: snapshot-failures
          path: |
            **/Failures/*.png
          retention-days: 7
```

### Snapshot Storage Strategy

| Strategy        | Pros                          | Cons                        |
|-----------------|-------------------------------|-----------------------------|
| In-repo         | Simple, versioned with code   | Repo size grows             |
| Git LFS         | Efficient storage, versioned  | Requires LFS setup          |
| Separate branch | Keeps main branch small       | Harder to review            |

**Recommendation:** Store snapshots in the repo for small-medium projects. Use Git LFS when snapshot count exceeds 500 images.

### CI Consistency

```swift
// Always specify exact simulator for consistent rendering
// In CI, pin to a specific Xcode and simulator version

// Snapshots recorded on macOS 14 + Xcode 16 + iPhone 15 simulator
// Will differ on macOS 13 + Xcode 15 due to rendering differences
```

---

## Handling Diffs and Updating Baselines

### Reviewing Diffs

When a snapshot test fails, swift-snapshot-testing saves three files:

```text
__Snapshots__/
  Failures/
    testLoginView.reference.png    # Original baseline
    testLoginView.failure.png      # Current render
    testLoginView.diff.png         # Pixel difference overlay
```

### Updating Baselines After Intentional Changes

```bash
# Method 1: Delete old snapshots, re-run tests
rm -rf Tests/__Snapshots__/LoginViewTests/
xcodebuild test -scheme MyApp -only-testing:MyAppTests/LoginViewTests

# Method 2: Set record mode in code
# withSnapshotTesting(record: .all) { ... }
# Run tests, then revert the record mode change

# Method 3: Environment variable
# SNAPSHOT_TESTING_RECORD=all xcodebuild test ...
```

### PR Workflow

```text
1. Make UI changes
2. Run snapshot tests locally -- see failures
3. Review diff images to verify changes are intentional
4. Update baselines: delete old snapshots, re-record
5. Commit updated snapshots alongside code changes
6. PR reviewer checks snapshot diffs in the file changes
```

---

## Perceptual Diff Tools

For cases where exact pixel matching is too strict.

### Custom Precision

```swift
// Allow small pixel differences (anti-aliasing, font rendering)
assertSnapshot(
    of: view,
    as: .image(precision: 0.98)  // 98% pixel match required
)

// Looser tolerance for complex views
assertSnapshot(
    of: view,
    as: .image(precision: 0.95, perceptualPrecision: 0.98)
)
```

### Precision Parameters

| Parameter             | Range | Description                                |
|-----------------------|-------|--------------------------------------------|
| `precision`           | 0-1   | Fraction of pixels that must match exactly |
| `perceptualPrecision` | 0-1   | Per-pixel color similarity threshold       |

```swift
// Strict: every pixel must match (default)
assertSnapshot(of: view, as: .image(precision: 1.0, perceptualPrecision: 1.0))

// Moderate: allow 2% pixel difference, 98% color similarity
assertSnapshot(of: view, as: .image(precision: 0.98, perceptualPrecision: 0.98))

// Loose: for dynamic content areas
assertSnapshot(of: view, as: .image(precision: 0.90, perceptualPrecision: 0.95))
```

---

## Flake Prevention

| Flake Source          | Mitigation                                          |
|-----------------------|-----------------------------------------------------|
| Date/time in UI       | Inject fixed dates in view models                   |
| Animated content      | Disable animations or capture at known state        |
| Network images        | Use placeholder images in test data                 |
| Cursor blinking       | Resign first responder before snapshot               |
| Simulator differences | Pin Xcode + simulator version in CI                 |
| Font rendering        | Same OS version across all environments             |
| Random content        | Use seeded random or static test data               |

### Deterministic Test Data

```swift
extension User {
    static var preview: User {
        User(
            id: "test-123",
            name: "Jane Doe",
            email: "jane@example.com",
            avatarURL: nil,  // no network image
            joinDate: Date(timeIntervalSince1970: 1700000000) // fixed date
        )
    }
}
```

### Disable Animations

```swift
override func setUp() {
    super.setUp()
    UIView.setAnimationsEnabled(false)
}

override func tearDown() {
    UIView.setAnimationsEnabled(true)
    super.tearDown()
}
```

**Checklist -- Snapshot Test Reliability:**

- [ ] All test data uses fixed values (no random, no current date)
- [ ] Network images replaced with local placeholders
- [ ] Animations disabled during snapshot capture
- [ ] Xcode and simulator versions pinned in CI
- [ ] Precision threshold set appropriately (0.98 for most views)
- [ ] Snapshots committed with code changes in same PR
- [ ] CI uses same macOS and Xcode version as developers
- [ ] Failure artifacts uploaded for review on CI failure

---

## Related Resources

- [xctest-patterns.md](xctest-patterns.md) -- XCTest unit testing patterns
- [xcuitest-patterns.md](xcuitest-patterns.md) -- XCUITest UI testing
- [swift-testing.md](swift-testing.md) -- Modern Swift Testing framework
- [ios-ci-optimization.md](ios-ci-optimization.md) -- CI pipeline optimization
- [simulator-commands.md](simulator-commands.md) -- Simulator management commands
