# Mobile Accessibility Testing

Platform-specific accessibility testing patterns for iOS and Android. Covers automated scanning tools, programmatic checks in test suites, and manual screen reader workflows.

## Table of Contents

- [iOS Accessibility Testing](#ios-accessibility-testing)
- [Accessibility Inspector](#accessibility-inspector)
- [XCUITest Accessibility Assertions](#xcuitest-accessibility-assertions)
- [VoiceOver Testing Protocol (iOS)](#voiceover-testing-protocol-ios)
- [SwiftUI Accessibility Modifiers](#swiftui-accessibility-modifiers)
- [Android Accessibility Testing](#android-accessibility-testing)
- [Accessibility Scanner](#accessibility-scanner)
- [Espresso Accessibility Checks](#espresso-accessibility-checks)
- [Compose Accessibility Testing](#compose-accessibility-testing)
- [TalkBack Testing Protocol (Android)](#talkback-testing-protocol-android)
- [Touch Target Validation](#touch-target-validation)
- [Cross-Platform Considerations](#cross-platform-considerations)
- [CI Integration for Mobile](#ci-integration-for-mobile)
- [iOS (GitHub Actions)](#ios-github-actions)
- [Android (GitHub Actions)](#android-github-actions)

## iOS Accessibility Testing

### Accessibility Inspector

Xcode's built-in tool for auditing accessibility properties.

**Launch**: Xcode → Open Developer Tool → Accessibility Inspector

**Key Features**:
- **Inspection mode**: hover over elements to see accessibility properties (label, value, traits, frame).
- **Audit mode**: run automated checks on the current screen for common issues.
- **Settings**: simulate accessibility features (bold text, reduced motion, increased contrast, etc.).

**Audit Workflow**:
1. Launch app in Simulator.
2. Open Accessibility Inspector and select the Simulator.
3. Click the Audit button (checkmark icon).
4. Run audit on each key screen.
5. Review warnings — each links to the element and suggests a fix.
6. Export audit results for tracking.

### XCUITest Accessibility Assertions

```swift
// Verify element has accessibility label
let submitButton = app.buttons["Submit order"]
XCTAssertTrue(submitButton.exists, "Submit button must have accessible label")

// Verify element is accessible
XCTAssertTrue(submitButton.isAccessibilityElement)

// Verify accessibility traits
XCTAssertTrue(submitButton.accessibilityTraits.contains(.button))

// Verify image has description
let productImage = app.images["Product photo of blue sneakers"]
XCTAssertTrue(productImage.exists, "Product image must have descriptive label")
```

### VoiceOver Testing Protocol (iOS)

1. Enable VoiceOver: `Settings → Accessibility → VoiceOver`.
2. Navigate the critical flow using swipe gestures only.
3. Verify:
   - [ ] All interactive elements are reachable by swiping
   - [ ] Labels are descriptive and concise
   - [ ] Traits announced correctly (button, link, heading, adjustable)
   - [ ] Custom views announce role and state
   - [ ] Grouped elements read as a single unit where appropriate
   - [ ] Dynamic content changes announced via `UIAccessibility.post(notification:)`
   - [ ] Touch targets are at least 44x44 points
   - [ ] Dismiss gestures work (two-finger scrub for back/dismiss)

### SwiftUI Accessibility Modifiers

Verify these are present in reviewed code:

```swift
Image("icon")
    .accessibilityLabel("Shopping cart, 3 items")

Button("Buy") { }
    .accessibilityHint("Double tap to purchase this item")

VStack {
    Text("Price")
    Text("$29.99")
}
.accessibilityElement(children: .combine)
```

## Android Accessibility Testing

### Accessibility Scanner

Google's standalone app for auditing accessibility issues.

**Install**: Google Play Store → "Accessibility Scanner" by Google LLC.

**Workflow**:
1. Open Accessibility Scanner and grant overlay permission.
2. Navigate to each key screen in your app.
3. Tap the Scanner floating action button to capture.
4. Review suggestions: touch target size, contrast, labels, content grouping.
5. Export results for tracking.

**Common Findings**:
- Touch targets smaller than 48x48 dp
- Missing content descriptions on ImageViews and ImageButtons
- Insufficient text contrast ratios
- Items not labeled for screen readers

### Espresso Accessibility Checks

Enable accessibility checks globally for all Espresso tests:

```kotlin
@RunWith(AndroidJUnit4::class)
class AccessibilityTest {

    @Before
    fun enableAccessibilityChecks() {
        AccessibilityChecks.enable()
            .setRunChecksFromRootView(true)
            .setThrowExceptionFor(
                AccessibilityCheckResult.AccessibilityCheckResultType.ERROR
            )
    }

    @Test
    fun loginScreen_passesAccessibilityChecks() {
        // Any Espresso interaction triggers accessibility checks
        onView(withId(R.id.email_input)).perform(typeText("user@example.com"))
        onView(withId(R.id.login_button)).perform(click())
    }
}
```

### Compose Accessibility Testing

```kotlin
@Test
fun productCard_hasAccessibleDescription() {
    composeTestRule.setContent {
        ProductCard(product = testProduct)
    }

    composeTestRule
        .onNodeWithContentDescription("Product: Blue Sneakers, $59.99")
        .assertExists()

    composeTestRule
        .onNodeWithTag("add_to_cart")
        .assertHasClickAction()
        .assertContentDescriptionEquals("Add Blue Sneakers to cart")
}
```

### TalkBack Testing Protocol (Android)

1. Enable TalkBack: `Settings → Accessibility → TalkBack`.
2. Navigate the critical flow using swipe gestures only.
3. Verify:
   - [ ] All interactive elements are reachable by swiping
   - [ ] Content descriptions are meaningful (not "button" or "image")
   - [ ] Custom views announce role and state via `AccessibilityNodeInfo`
   - [ ] RecyclerView items are individually focusable and described
   - [ ] Touch targets are at least 48x48 dp
   - [ ] Dynamic updates announced via `AccessibilityEvent` or `LiveData` observers
   - [ ] Bottom sheets, dialogs, and drawers are focusable and dismissible
   - [ ] Toast and Snackbar messages are announced

### Touch Target Validation

Programmatic check for minimum touch target size:

```kotlin
@Test
fun allButtons_meetMinimumTouchTarget() {
    // Espresso accessibility checks catch this automatically when enabled
    // For explicit checks:
    onView(withId(R.id.small_button))
        .check { view, _ ->
            assertThat(view.width).isAtLeast(48.dp.toPx())
            assertThat(view.height).isAtLeast(48.dp.toPx())
        }
}
```

Compose provides `Modifier.minimumInteractiveComponentSize()` (48dp default).

## Cross-Platform Considerations

| Concern | iOS | Android |
|---------|-----|---------|
| Minimum touch target | 44x44 pt | 48x48 dp |
| Screen reader | VoiceOver | TalkBack |
| Automated scanner | Accessibility Inspector | Accessibility Scanner |
| Programmatic checks | XCUITest assertions | Espresso AccessibilityChecks |
| Content description | `accessibilityLabel` | `contentDescription` |
| Grouping | `accessibilityElement(children:)` | `importantForAccessibility` + grouping |
| Live announcements | `UIAccessibility.post(notification:)` | `AccessibilityEvent.TYPE_ANNOUNCEMENT` |
| Reduced motion | `UIAccessibility.isReduceMotionEnabled` | `Settings.Global.ANIMATOR_DURATION_SCALE` |

## CI Integration for Mobile

### iOS (GitHub Actions)

```yaml
- name: Run accessibility audit
  run: |
    xcodebuild test \
      -scheme MyApp \
      -destination 'platform=iOS Simulator,name=<simulator-name>' \
      -only-testing:MyAppUITests/AccessibilityTests
```

### Android (GitHub Actions)

```yaml
- name: Run accessibility tests
  run: |
    ./gradlew connectedAndroidTest \
      -Pandroid.testInstrumentationRunnerArguments.class=com.example.AccessibilityTest
```
