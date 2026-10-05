# iOS Version and visionOS Testing

SDK-dependent testing changes and visionOS/Apple Vision Pro destinations. Read the release notes for the selected Xcode and destination OS before using these patterns.

Apple adopted year-based platform numbering in 2025; the iOS, macOS and visionOS 26 releases share a release cycle. Select the actual installed runtime rather than extrapolating identifiers from older platform numbers.

## Contents

- [iOS 26 Testing Changes](#ios-26-testing-changes)
- [visionOS Simulator Destination](#visionos-simulator-destination)
- [Reality Composer Pro Asset Testing](#reality-composer-pro-asset-testing)
- [Hand-Tracking Simulator Limits](#hand-tracking-simulator-limits)
- [Platform Notes](#platform-notes)

---

## iOS 26 Testing Changes

### Liquid Glass UI and Snapshot Baselines

iOS 26 ships Liquid Glass as the default system visual layer. Apps linked against the iOS 26 SDK adopt the new system UI appearance unless compatibility mode applies. Testing impact:

- Existing snapshot baselines can change after adopting the iOS 26 SDK/runtime. Compare the actual diffs and regenerate affected baselines; an SDK upgrade does not justify bulk acceptance.
- Check whether Liquid Glass rendering differs between simulator and real hardware in your app before treating simulator snapshot coverage as anything more than a layout/structure regression gate.
- For an SDK that supports it, `UIDesignRequiresCompatibility = YES` requests the previous UI appearance. Read the [key documentation](https://developer.apple.com/documentation/bundleresources/information-property-list/uidesignrequirescompatibility) and selected SDK release notes before using compatibility mode; test the final appearance rather than relying on this as a long-term opt-out. There is no documented `UIApplicationSupportsLiquidGlass` key.

### App Store SDK Deadline

The April 28, 2026 requirement sets an iOS 26 SDK floor for uploads. Check [Apple’s upcoming requirements](https://developer.apple.com/news/upcoming-requirements/) before submission, and run the release gate with the selected supported Xcode and destination OS; the floor does not require pinning tests to Xcode 26.

### iOS 26 Accessibility Known Issue

Toolbar items placed in `.keyboard` have been reported missing from the accessibility hierarchy (VoiceOver cannot focus them, XCUITest cannot find them); check the current Xcode/iOS release notes. If you reproduce it, treat any `.keyboard`-placed toolbar action as needing an XCUITest accessibility check before shipping.

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
- Asset loading tests are slow. Declare a tag (`extension Tag { @Tag static var assetLoading: Self }`), apply it with `@Test(.tags(.assetLoading))`, and either filter it out of the fast PR gate via a test plan configuration or run it in a separate Full/nightly plan.

---

## Hand-Tracking Simulator Limits

Hand tracking via ARKit / RealityKit on the visionOS simulator is
**simulation-only** — it does not reflect real hardware fidelity:

- The simulator provides basic gesture recognition (pinch, direct touch) but
  does not simulate continuous hand-pose streams as a real device would.
- Do not use simulator hand-tracking results as release proof for
  hand-interaction UX. Use a real Apple Vision Pro device pass for that.
- For CI purposes, scope hand-tracking tests to presence/absence of
  `HandTrackingProvider.isSupported` (not `ARHandTrackingProvider`, which does not exist) and mock the provider in unit tests.
- XCUITest tap gestures work normally on the visionOS simulator; test button
  activation and focus-and-tap flows at that layer.

---

## Platform Notes

| Platform | Simulator support | Real device required |
|----------|-------------------|----------------------|
| iOS 26 Liquid Glass | Yes (layout/structure regression) | For visual rendering fidelity confirmation |
| visionOS 26 spatial UI | Yes (basic gestures) | For hand-tracking and eye-tracking fidelity |
| Reality Composer Pro assets | Yes (entity graph) | For visual rendering validation |
