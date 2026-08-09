# Visual Regression Testing (Mobile)

Screenshot-based regression testing for iOS and Android: golden image strategy, tooling, diff algorithms, and CI integration.

## Table of Contents

- [Golden Image Strategy](#golden-image-strategy)
- [Visual-Diff Tools](#visual-diff-tools)
- [iOS/Android Native Snapshot Tooling](#iosandroid-native-snapshot-tooling)
- [Pixel-Tolerance vs Perceptual Diff](#pixel-tolerance-vs-perceptual-diff)
- [Baseline Rotation Cadence](#baseline-rotation-cadence)
- [CI Artifact Upload Pattern](#ci-artifact-upload-pattern)
- [Related Resources](#related-resources)

---

## Golden Image Strategy

A golden image is a pre-approved screenshot captured at a known-good state. Future runs diff against it; deviations require either approval (intended change) or a fix (regression).

### Per-Device Baselines

Screenshots vary by screen resolution, pixel density, and OS rendering. Store baselines scoped to at least:

- **Device model** — e.g. `iPhone_16_Pro`, `Pixel_9`
- **OS version** — e.g. `iOS_18`, `Android_14`
- **Locale** — e.g. `en_US`, `ar_SA` (RTL layout differs)
- **Color scheme** — light / dark mode (separate golden sets)
- **Font scale** — default / large (accessibility text size affects layout)

```
baselines/
  ios/
    iPhone_16_Pro/
      iOS_18/
        en_US/
          light/
            home_screen.png
          dark/
            home_screen.png
  android/
    pixel_9/
      android_14/
        en_US/
          ...
```

Restrict PR-gate baselines to a small canonical set (e.g. one iPhone size class, one Android reference device) to keep CI fast. Run the full per-device matrix in nightly or pre-release jobs.

### Locale-Specific Baselines

For apps with localized UI, maintain separate golden images per locale. RTL languages (Arabic, Hebrew) mirror layouts and require distinct baselines. Even LTR locales differ: German and Finnish strings are 20–40% longer than English and can wrap or truncate differently.

### OS-Version Sensitivity

Font rendering, corner radius, system sheet styles, and status bar height change across OS releases. When a major OS version ships, plan a scheduled baseline update before the new OS reaches user adoption (typically 4–8 weeks post-release).

---

## Visual-Diff Tools

### Percy / App Percy (BrowserStack)

- BrowserStack offers two visual testing products for mobile: **Percy** (web and hybrid/Appium flows) and **App Percy** (native iOS and Android apps).
- App Percy is purpose-built for native app visual testing with access to 30,000+ real devices. It includes the **Visual Review Agent** (AI-powered): replaces pixel-level red highlights with smart bounding boxes and natural-language summaries of changes, cutting review time up to 3x.
- Percy integrates with Appium, XCUITest, Espresso, and Maestro via Percy SDK.
- Both support branch-aware baseline management and approval workflows.
- Primary docs: Percy — <https://www.browserstack.com/docs/percy>; App Percy — <https://www.browserstack.com/app-percy>

### Applitools Eyes

- AI-powered visual diff engine ("Visual AI") that ignores irrelevant rendering differences (font hinting, sub-pixel shifts) while catching meaningful layout changes.
- Native SDKs for XCUITest, Espresso, Appium, and React Native.
- Supports Ultrafast Test Cloud for cross-device visual runs from a single snapshot upload.
- Checkpoints can be grouped into test suites with per-region ignore masks.
- Primary docs: <https://applitools.com/docs>

### Chromatic (for React Native Web / Storybook)

- Purpose-built for Storybook component libraries.
- For React Native teams using React Native Web to share components, Chromatic runs visual regression at the component level from Storybook stories.
- Not a device-level tool; complements (does not replace) Detox or Maestro device tests.
- Primary docs: <https://www.chromatic.com/docs>

### Sauce Visual

- Cloud visual diff layer within Sauce Labs.
- Captures screenshots via the Sauce Labs device cloud during existing Appium or XCUI/Espresso runs; no separate upload step.
- Diff baseline management in the Sauce Labs dashboard.
- Primary docs: <https://docs.saucelabs.com/visual-testing>

### Screener (deprecated / merged into Sauce Visual)

- Screener was acquired by Sauce Labs and merged into Sauce Visual. New integrations should use Sauce Visual directly.

---

## iOS/Android Native Snapshot Tooling

Native snapshot libraries generate golden images as part of the unit/UI test run without a cloud service. Baselines are committed to the repo and diffs fail the test run locally and in CI.

### Paparazzi (Android)

- Gradle plugin by Cash App for Android composable and View screenshot tests without a device or emulator.
- Renders views on the JVM using the Android framework's layout engine; no Robolectric dependency.
- Baselines stored in `src/test/snapshots/images/`.
- Update baselines: `./gradlew recordPaparazziDebug`
- Verify: `./gradlew verifyPaparazziDebug`
- Supports multi-resolution, dark mode, and font-scale variants via `DeviceConfig`.
- GitHub: <https://github.com/cashapp/paparazzi>

```kotlin
@get:Rule val paparazzi = Paparazzi(
    deviceConfig = DeviceConfig.PIXEL_6,
    theme = "android:Theme.Material3.Light"
)

@Test fun homeScreen() {
    paparazzi.snapshot { HomeScreen(state = HomeState.loaded()) }
}
```

### Roborazzi (Android)

- Robolectric-based screenshot testing for Compose and View.
- Runs on the JVM; faster than device-based screenshot tests.
- Integrates with Compose UI testing semantics.
- Supports diff images on failure and configurable comparison thresholds.
- GitHub: <https://github.com/takahirom/roborazzi>

```kotlin
@Test fun feedItem() {
    composeTestRule.setContent { FeedItem(item = sampleItem) }
    composeTestRule.onRoot().captureRoboImage("feed_item.png")
}
```

### swift-snapshot-testing (iOS)

- Point-Free library for snapshot testing in Swift.
- Supports `UIViewController`, `UIView`, `SwiftUI.View`, and arbitrary `Encodable` values.
- Baselines stored in `__Snapshots__/` next to the test file.
- Record mode: set `record: true` on first run to write baselines.
- Ships with multiple strategies: `.image`, `.recursiveDescription`, `.dump` (for non-visual regression).
- GitHub: <https://github.com/pointfreeco/swift-snapshot-testing>

```swift
import SnapshotTesting

final class HomeViewTests: XCTestCase {
    func testHomeView() {
        let vc = HomeViewController()
        assertSnapshot(of: vc, as: .image(on: .iPhoneXsMax))
    }
}
```

---

## Pixel-Tolerance vs Perceptual Diff

### Pixel-Tolerance (Exact)

Compares images pixel-by-pixel with an optional tolerance threshold (e.g. allow up to 0.1% of pixels to differ by up to 10 color units).

**Pros**: deterministic, no inference cost, catches subtle color regressions.

**Cons**: sensitive to anti-aliasing, font hinting, and sub-pixel rendering differences across OS versions and GPU drivers — produces false positives that erode trust.

**When to use**: design-system component libraries where pixel-perfect consistency is enforced; emulator-only runs where rendering is deterministic.

### Perceptual Diff (AI / Structural)

Compares images using perceptual hashing or neural networks that model human visual attention. Ignores sub-pixel noise; flags layout shifts, missing elements, and color-range changes.

**Pros**: low false positive rate on cross-device runs; resilient to minor rendering differences.

**Cons**: may miss very small intentional changes (e.g. a 1 px border tweak); higher tooling complexity and latency.

**When to use**: device-cloud runs on real hardware (rendering varies per device); cross-OS regression sweeps; release-candidate full-suite runs.

### Recommended Pairing

| Environment | Strategy |
|---|---|
| Unit/JVM snapshot (Paparazzi, Roborazzi, swift-snapshot-testing) | Pixel-tolerance (low threshold) — deterministic renderer |
| Device-cloud full regression (Percy, Applitools) | Perceptual diff — real hardware noise |
| Component Storybook (Chromatic) | Perceptual diff — visual AI baselines |

---

## Baseline Rotation Cadence

Baselines must be updated proactively; stale baselines cause cascading false-positive diffs that teams start ignoring.

### Planned Rotation Triggers

| Trigger | Action |
|---|---|
| Major OS release (iOS/Android) | Schedule baseline refresh 2–4 weeks before expected user adoption peak |
| Design system token update (colors, typography, spacing) | Refresh all affected component baselines in the same PR as the token change |
| Planned layout change (feature flag on → stable) | Update baselines when the flag reaches 100% |
| New device tier added to CI matrix | Capture baselines for the new device before enabling diff checks |

### Baseline Hygiene Rules

- Never approve diffs in bulk without visual inspection. One-click "approve all" defeats the purpose.
- Store baselines in version control (native tools) or in the cloud service's branch-aware baseline management (Percy, Applitools).
- Tag baselines with the OS version and device model in the filename or metadata so stale images are identifiable.
- Keep a rotation log (a simple `BASELINES.md` or commit history) noting when and why baselines were updated.

---

## CI Artifact Upload Pattern

Screenshots and diff images are ephemeral. Upload them as CI artifacts on every run so failures are debuggable without re-running.

### GitHub Actions Pattern

```yaml
- name: Run visual regression tests
  id: visual_tests
  run: ./gradlew verifyPaparazziDebug  # or xctest, or percy CLI

- name: Upload snapshot diffs on failure
  if: failure()
  uses: actions/upload-artifact@v4
  with:
    name: snapshot-diffs-${{ github.run_id }}
    path: |
      **/build/outputs/paparazzi/failures/
      **/src/test/snapshots/images/
    retention-days: 14

- name: Upload Percy screenshots (always)
  if: always()
  run: |
    npx percy upload screenshots/ \
      --commit "${{ github.sha }}" \
      --branch "${{ github.head_ref }}"
```

### Artifact Naming Convention

Include enough context in artifact names to trace back to the failure:

```
snapshot-diffs-<run_id>/
  <device>/<os>/<locale>/<test_name>_expected.png
  <device>/<os>/<locale>/<test_name>_actual.png
  <device>/<os>/<locale>/<test_name>_diff.png
```

### Retention Policy

- Keep diff artifacts for 14–30 days (enough to cover the release cycle).
- Keep approved baselines indefinitely in version control or the cloud service.
- Do not upload full golden sets to CI artifacts on every run — this inflates artifact storage; upload only diffs and failures.

---

## Related Resources

- [framework-comparison.md](./framework-comparison.md) — automation framework selection
- [device-farm-strategies.md](./device-farm-strategies.md) — cloud device farm for screenshot runs at scale
- [mobile-performance-testing.md](./mobile-performance-testing.md) — performance testing reference
- [SKILL.md](../SKILL.md) — parent mobile testing skill
- [Percy Mobile docs](https://www.browserstack.com/docs/percy)
- [Applitools Eyes docs](https://applitools.com/docs)
- [Paparazzi (GitHub)](https://github.com/cashapp/paparazzi)
- [Roborazzi (GitHub)](https://github.com/takahirom/roborazzi)
- [swift-snapshot-testing (GitHub)](https://github.com/pointfreeco/swift-snapshot-testing)
