# iOS Version and visionOS Testing

Testing changes and visionOS/Apple Vision Pro test targets for iOS 26 / Xcode 26.

Note on versioning: Apple unified all platform version numbers in 2025. iOS 19 became iOS 26, macOS became macOS Tahoe 26, visionOS 3 became visionOS 26. All "26" numbers refer to the same release cycle.

## Contents

- [iOS 26 Testing Changes](#ios-26-testing-changes)
- [iOS 18 Testing Changes](#ios-18-testing-changes)
- [visionOS Simulator Destination](#visionos-simulator-destination)
- [Reality Composer Pro Asset Testing](#reality-composer-pro-asset-testing)
- [Hand-Tracking Simulator Limits](#hand-tracking-simulator-limits)
- [Platform Notes](#platform-notes)

---

## iOS 26 Testing Changes

### Liquid Glass UI and Snapshot Baselines

iOS 26 ships Liquid Glass as the default system visual layer. Apps built with the iOS 26 SDK automatically pick up the new material rendering on all native UI components. Testing impact:

- Snapshot/screenshot baselines recorded on iOS 18 or earlier will fail against the iOS 26 simulator due to visual rendering differences. Regenerate baselines after migrating to Xcode 26.
- Liquid Glass renders differently between the iOS 26 simulator and real hardware in some conditions. Treat simulator snapshot coverage as a regression gate for layout, not pixel-perfect rendering proof.
- If your app opts out of Liquid Glass via `UIApplicationSupportsLiquidGlass = NO` in Info.plist, the visual delta is smaller but still present for some system chrome.

### App Store SDK Deadline

As of April 28, 2026, App Store Connect rejects submissions not built with the iOS 26 SDK. The test gate before submission must run under Xcode 26 with the iOS 26 simulator or device.

### iOS 26 Accessibility Known Issue

On iOS 26.1, a `ToolbarItem` placed in `.keyboard` is no longer exposed to the accessibility hierarchy. VoiceOver cannot focus it and XCUITest cannot discover the element. Workaround: move the action out of `.keyboard` placement or use a floating overlay. Check the Xcode release notes for a fix before relying on keyboard toolbar accessibility in XCUITest.

---

## iOS 18 Testing Changes

### Predictive Back Gesture

iOS 18 introduced predictive back navigation (a swipe-preview of the previous
screen before the gesture completes). XCUITest implications:

- Back-swipe gestures that relied on `swipeRight()` completing immediately may
  observe the preview state rather than the completed pop. Use
  `waitForExistence` or an assertion on the destination view to confirm the
  transition completed.
- If your app uses `NavigationTransition` or custom interactive-pop overrides,
  add a dedicated XCUITest case that exercises the back gesture and asserts the
  destination view identifier is accessible after the swipe.

### Apple Intelligence Test Contexts (iOS 18+)

Apple Intelligence features (Writing Tools, Image Playground, Genmoji,
Priority Notifications) surface inside existing system UI:

- Writing Tools: triggers on text selection in `UITextView` / `WKWebView`;
  test by asserting the text-selection accessory bar exists or does not appear
  in contexts where you suppress it.
- Priority Notifications: affects notification ordering — do not assert a
  specific notification position in UI tests; assert presence only.
- For unit-testable code that calls Apple Intelligence APIs, use protocol
  mocking to avoid live model calls in CI.

### Transit and Wallet Pass APIs

Transit card APIs (added via DriverKit/PassKit extensions) are not testable on
simulator for NFC proximity triggers. Scope UI tests to the UI state that
follows a mock pass-add confirmation rather than the tap itself.

---

---

## visionOS Simulator Destination

Use the following destination string for visionOS simulator runs:

```bash
-destination 'platform=visionOS Simulator,name=Apple Vision Pro'
```

Full example:

```bash
xcodebuild test \
  -scheme MyApp \
  -destination 'platform=visionOS Simulator,name=Apple Vision Pro' \
  -resultBundlePath TestResults.xcresult
```

List available visionOS simulators:

```bash
xcrun simctl list devices available | grep -i vision
```

Create a visionOS simulator if one is not listed. The runtime identifier changes with each major version — verify with `xcrun simctl list runtimes` before copying any hardcoded identifier. Example for visionOS 26:

```bash
# First check what runtimes are available
xcrun simctl list runtimes | grep -i vision

# Then create using the confirmed runtime ID
xcrun simctl create "Apple Vision Pro" \
  "com.apple.CoreSimulator.SimDeviceType.Apple-Vision-Pro" \
  "<runtime-id-from-above>"
```

---

## Reality Composer Pro Asset Testing

Reality Composer Pro bundles `.usda` / `.reality` assets that are loaded at
runtime via `RealityKit`. Testing recommendations:

- Unit-test `RealityKit` scene loading with `Entity.load(named:in:)` in an
  `XCTestCase` — this works on simulator for entity graph assertions.
- For visual fidelity, capture screenshots from the visionOS simulator; treat
  them as smoke, not pixel-perfect regression tests (renderer output varies
  between simulator versions).
- Asset loading tests are slow. Tag them with `@Tag(.assetLoading)` (Swift
  Testing) or a custom test plan to exclude from the fast PR gate.

---

## Hand-Tracking Simulator Limits

Hand tracking via ARKit / RealityKit on the visionOS simulator is
**simulation-only** — it does not reflect real hardware fidelity:

- The simulator provides basic gesture recognition (pinch, direct touch) but
  does not simulate continuous hand-pose streams as a real device would.
- Do not use simulator hand-tracking results as release proof for
  hand-interaction UX. Use a real Apple Vision Pro device pass for that.
- For CI purposes, scope hand-tracking tests to presence/absence of
  `ARHandTrackingProvider.isSupported` and mock the provider in unit tests.
- XCUITest tap gestures work normally on the visionOS simulator; test button
  activation and focus-and-tap flows at that layer.

---

## Platform Notes

| Platform | Simulator support | Real device required |
|----------|-------------------|----------------------|
| iOS 26 Liquid Glass | Yes (layout/structure regression) | For visual rendering fidelity confirmation |
| iOS 18+ predictive back | Yes (test UI transitions) | For touch-fidelity confirmation |
| Apple Intelligence | Limited (mock APIs) | For end-to-end model calls |
| visionOS 26 spatial UI | Yes (basic gestures) | For hand-tracking and eye-tracking fidelity |
| Reality Composer Pro assets | Yes (entity graph) | For visual rendering validation |
