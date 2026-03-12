# XCUITest Patterns and Best Practices

Advanced UI testing patterns for iOS using XCUITest.

**Official docs**: [XCUITest](https://developer.apple.com/documentation/xctest/user_interface_tests)

## Contents

- [Element Query Patterns](#element-query-patterns)
- [Page Object Pattern for iOS](#page-object-pattern-for-ios)
- [System Alerts and Permissions](#system-alerts-and-permissions)
- [Wait Strategies](#wait-strategies)
- [Keyboard Interaction](#keyboard-interaction)
- [Scroll and Swipe Gestures](#scroll-and-swipe-gestures)
- [Picker Wheel Interaction](#picker-wheel-interaction)
- [Launch Arguments and Environment Variables](#launch-arguments-and-environment-variables)
- [Test Data Injection](#test-data-injection)
- [Accessibility Identifier Best Practices](#accessibility-identifier-best-practices)
- [Recording and Debugging](#recording-and-debugging)
- [Related Resources](#related-resources)

---

## Element Query Patterns

### XCUIElementQuery Basics

```swift
import XCTest

class ElementQueryExamples: XCTestCase {
    let app = XCUIApplication()

    func testElementQueries() {
        // By accessibility identifier (preferred)
        let loginButton = app.buttons["loginButton"]

        // By label text
        let submitButton = app.buttons["Submit"]

        // By element type
        let allButtons = app.buttons
        let firstTextField = app.textFields.firstMatch

        // By index (fragile -- avoid in production tests)
        let secondCell = app.cells.element(boundBy: 1)
    }
}
```

### Predicate-Based Queries

```swift
// NSPredicate matching
let containsEmail = NSPredicate(format: "label CONTAINS[c] 'email'")
let emailField = app.textFields.matching(containsEmail).firstMatch

// Begins with
let startsWithUser = NSPredicate(format: "label BEGINSWITH 'User'")
let userLabel = app.staticTexts.matching(startsWithUser).firstMatch

// Multiple conditions
let enabledSubmit = NSPredicate(
    format: "label == 'Submit' AND isEnabled == true"
)
let readyButton = app.buttons.matching(enabledSubmit).firstMatch

// Regular expression
let datePattern = NSPredicate(
    format: "label MATCHES '\\\\d{2}/\\\\d{2}/\\\\d{4}'"
)
let dateLabel = app.staticTexts.matching(datePattern).firstMatch
```

### Descendant Queries

```swift
// Find elements within a container
let formContainer = app.otherElements["loginForm"]
let emailField = formContainer.textFields["emailField"]
let passwordField = formContainer.secureTextFields["passwordField"]

// Navigate table cells
let orderCell = app.tables.cells.containing(
    NSPredicate(format: "label CONTAINS 'Order #1234'")
).firstMatch

// Find button within a specific cell
let deleteButton = orderCell.buttons["deleteButton"]

// Children vs descendants
let directChildren = app.otherElements["container"].children(matching: .button)
let allDescendants = app.otherElements["container"].descendants(matching: .button)
```

### Element Type Reference

| XCUIElement Type         | UIKit Equivalent       | SwiftUI Equivalent     |
|--------------------------|------------------------|------------------------|
| `buttons`                | UIButton               | Button                 |
| `textFields`             | UITextField            | TextField              |
| `secureTextFields`       | UITextField (secure)   | SecureField            |
| `staticTexts`            | UILabel                | Text                   |
| `images`                 | UIImageView            | Image                  |
| `switches`               | UISwitch               | Toggle                 |
| `sliders`                | UISlider               | Slider                 |
| `tables`                 | UITableView            | List                   |
| `collectionViews`        | UICollectionView       | LazyVGrid/LazyHGrid   |
| `navigationBars`         | UINavigationBar        | NavigationStack        |
| `tabBars`                | UITabBar               | TabView                |
| `alerts`                 | UIAlertController      | .alert modifier        |
| `sheets`                 | UIViewController (sheet)| .sheet modifier       |

---

## Page Object Pattern for iOS

### Base Page

```swift
protocol Page {
    var app: XCUIApplication { get }
    func verify() -> Self
}

extension Page {
    @discardableResult
    func verify() -> Self {
        return self
    }
}
```

### Page Implementation

```swift
class LoginPage: Page {
    let app: XCUIApplication

    init(app: XCUIApplication) {
        self.app = app
    }

    // MARK: - Elements
    private var emailField: XCUIElement {
        app.textFields["emailField"]
    }

    private var passwordField: XCUIElement {
        app.secureTextFields["passwordField"]
    }

    private var loginButton: XCUIElement {
        app.buttons["loginButton"]
    }

    private var errorBanner: XCUIElement {
        app.staticTexts["errorBanner"]
    }

    private var forgotPasswordLink: XCUIElement {
        app.buttons["forgotPasswordLink"]
    }

    // MARK: - Actions
    @discardableResult
    func typeEmail(_ email: String) -> Self {
        emailField.tap()
        emailField.clearAndType(email)
        return self
    }

    @discardableResult
    func typePassword(_ password: String) -> Self {
        passwordField.tap()
        passwordField.clearAndType(password)
        return self
    }

    @discardableResult
    func tapLogin() -> DashboardPage {
        loginButton.tap()
        return DashboardPage(app: app).verify()
    }

    @discardableResult
    func tapLoginExpectingError() -> Self {
        loginButton.tap()
        XCTAssertTrue(errorBanner.waitForExistence(timeout: 5))
        return self
    }

    func tapForgotPassword() -> ForgotPasswordPage {
        forgotPasswordLink.tap()
        return ForgotPasswordPage(app: app).verify()
    }

    // MARK: - Assertions
    @discardableResult
    func assertErrorMessage(_ message: String) -> Self {
        XCTAssertEqual(errorBanner.label, message)
        return self
    }

    @discardableResult
    func assertLoginButtonEnabled(_ enabled: Bool = true) -> Self {
        XCTAssertEqual(loginButton.isEnabled, enabled)
        return self
    }

    // MARK: - Verify
    @discardableResult
    func verify() -> Self {
        XCTAssertTrue(emailField.waitForExistence(timeout: 5),
                       "Login page did not appear")
        return self
    }
}
```

### Using Pages in Tests

```swift
final class LoginFlowTests: XCTestCase {
    var app: XCUIApplication!

    override func setUp() {
        super.setUp()
        continueAfterFailure = false
        app = XCUIApplication()
        app.launchArguments = ["--uitesting", "--reset-state"]
        app.launch()
    }

    func testSuccessfulLogin() {
        LoginPage(app: app)
            .verify()
            .typeEmail("user@example.com")
            .typePassword("password123")
            .tapLogin()
            .assertWelcomeMessage("Welcome, user@example.com")
    }

    func testInvalidCredentials() {
        LoginPage(app: app)
            .verify()
            .typeEmail("wrong@example.com")
            .typePassword("wrongpass")
            .tapLoginExpectingError()
            .assertErrorMessage("Invalid email or password")
    }
}
```

---

## System Alerts and Permissions

### Handling Permission Dialogs

```swift
// Method 1: addUIInterruptionMonitor (handles alerts globally)
override func setUp() {
    super.setUp()
    app = XCUIApplication()

    addUIInterruptionMonitor(withDescription: "Permission Alert") { alert in
        let allowButton = alert.buttons["Allow"]
        let allowWhileUsing = alert.buttons["Allow While Using App"]

        if allowWhileUsing.exists {
            allowWhileUsing.tap()
            return true
        } else if allowButton.exists {
            allowButton.tap()
            return true
        }
        return false
    }

    app.launch()
}

// After triggering a permission, interact with app to fire the monitor
func testCameraPermission() {
    app.buttons["takePhotoButton"].tap()
    app.tap() // tap the app to trigger the interruption monitor
    // Continue test after permission is granted
}
```

### Handling Specific System Alerts

```swift
// Method 2: Direct springboard interaction
func testNotificationPermission() {
    app.buttons["enableNotifications"].tap()

    let springboard = XCUIApplication(bundleIdentifier: "com.apple.springboard")
    let allowButton = springboard.buttons["Allow"]

    if allowButton.waitForExistence(timeout: 5) {
        allowButton.tap()
    }
}

// Method 3: Reset permissions via launch arguments (iOS 15+)
func testLocationPermission() {
    app.resetAuthorizationStatus(for: .location)
    app.launch()

    app.buttons["shareLocation"].tap()

    let springboard = XCUIApplication(bundleIdentifier: "com.apple.springboard")
    let allowOnce = springboard.buttons["Allow Once"]
    if allowOnce.waitForExistence(timeout: 5) {
        allowOnce.tap()
    }
}
```

### Common Alert Button Labels

| Permission      | Allow Button Text               | Deny Button Text       |
|-----------------|----------------------------------|------------------------|
| Location        | "Allow While Using App" / "Allow Once" | "Don't Allow"   |
| Camera          | "OK"                             | "Don't Allow"          |
| Photos          | "Allow Full Access" / "Select Photos" | "Don't Allow"   |
| Notifications   | "Allow"                          | "Don't Allow"          |
| Contacts        | "OK"                             | "Don't Allow"          |
| Tracking (ATT)  | "Allow"                          | "Ask App Not to Track" |

---

## Wait Strategies

### waitForExistence (Built-in)

```swift
// Simple existence wait
let element = app.buttons["asyncButton"]
XCTAssertTrue(element.waitForExistence(timeout: 10))
```

### XCTNSPredicateExpectation (Advanced)

```swift
// Wait for element to become enabled
func waitForEnabled(_ element: XCUIElement, timeout: TimeInterval = 10) {
    let predicate = NSPredicate(format: "isEnabled == true")
    let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
    let result = XCTWaiter().wait(for: [expectation], timeout: timeout)
    XCTAssertEqual(result, .completed, "Element did not become enabled")
}

// Wait for element to disappear
func waitForDisappearance(_ element: XCUIElement, timeout: TimeInterval = 10) {
    let predicate = NSPredicate(format: "exists == false")
    let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
    let result = XCTWaiter().wait(for: [expectation], timeout: timeout)
    XCTAssertEqual(result, .completed, "Element did not disappear")
}

// Wait for label to change
func waitForLabel(_ element: XCUIElement, toBe text: String, timeout: TimeInterval = 10) {
    let predicate = NSPredicate(format: "label == %@", text)
    let expectation = XCTNSPredicateExpectation(predicate: predicate, object: element)
    let result = XCTWaiter().wait(for: [expectation], timeout: timeout)
    XCTAssertEqual(result, .completed, "Label did not become '\(text)'")
}
```

### Polling Wait (Custom)

```swift
extension XCTestCase {
    func waitUntil(
        timeout: TimeInterval = 10,
        interval: TimeInterval = 0.5,
        condition: () -> Bool
    ) {
        let deadline = Date().addingTimeInterval(timeout)
        while Date() < deadline {
            if condition() { return }
            Thread.sleep(forTimeInterval: interval)
        }
        XCTFail("Condition not met within \(timeout) seconds")
    }
}

// Usage
func testDataLoads() {
    app.buttons["refreshButton"].tap()
    waitUntil {
        app.cells.count > 0
    }
    XCTAssertGreaterThan(app.cells.count, 0)
}
```

---

## Keyboard Interaction

```swift
// Type text
let field = app.textFields["searchField"]
field.tap()
field.typeText("search query")

// Clear and type (helper extension)
extension XCUIElement {
    func clearAndType(_ text: String) {
        guard let currentValue = self.value as? String, !currentValue.isEmpty else {
            self.typeText(text)
            return
        }

        // Select all and delete
        self.tap()
        self.press(forDuration: 1.0) // long press to show menu
        if XCUIApplication().menuItems["Select All"].waitForExistence(timeout: 2) {
            XCUIApplication().menuItems["Select All"].tap()
            self.typeText(XCUIKeyboardKey.delete.rawValue)
        }
        self.typeText(text)
    }
}

// Dismiss keyboard
app.keyboards.buttons["Return"].tap()
// Or tap outside
app.otherElements["mainView"].tap()
// Or swipe down (common pattern)
app.swipeDown()

// Check keyboard visibility
func isKeyboardVisible() -> Bool {
    return app.keyboards.count > 0
}
```

---

## Scroll and Swipe Gestures

```swift
// Swipe in a direction
app.swipeUp()
app.swipeDown()
app.swipeLeft()
app.swipeRight()

// Scroll to find an element in a table/list
func scrollToElement(_ element: XCUIElement, in scrollView: XCUIElement,
                     maxSwipes: Int = 10) {
    var swipeCount = 0
    while !element.isHittable && swipeCount < maxSwipes {
        scrollView.swipeUp()
        swipeCount += 1
    }
    XCTAssertTrue(element.isHittable,
                   "Element not found after \(maxSwipes) swipes")
}

// Usage
let cell = app.cells["item-42"]
scrollToElement(cell, in: app.tables.firstMatch)
cell.tap()

// Scroll to exact position using coordinate-based swipe
func scrollSlowly(in element: XCUIElement) {
    let start = element.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.8))
    let end = element.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.2))
    start.press(forDuration: 0.1, thenDragTo: end)
}

// Pull to refresh
func pullToRefresh(in table: XCUIElement) {
    let start = table.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.1))
    let end = table.coordinate(withNormalizedOffset: CGVector(dx: 0.5, dy: 0.9))
    start.press(forDuration: 0.1, thenDragTo: end)
}
```

---

## Picker Wheel Interaction

```swift
// Date picker
func selectDate(month: String, day: String, year: String) {
    let datePicker = app.datePickers.firstMatch
    datePicker.pickerWheels.element(boundBy: 0).adjust(toPickerWheelValue: month)
    datePicker.pickerWheels.element(boundBy: 1).adjust(toPickerWheelValue: day)
    datePicker.pickerWheels.element(boundBy: 2).adjust(toPickerWheelValue: year)
}

// Standard picker
func selectPickerValue(_ value: String) {
    let picker = app.pickers.firstMatch
    picker.pickerWheels.firstMatch.adjust(toPickerWheelValue: value)
}

// Segmented control
func selectSegment(_ title: String) {
    app.segmentedControls.buttons[title].tap()
}
```

---

## Launch Arguments and Environment Variables

### Setting Launch Arguments

```swift
override func setUp() {
    super.setUp()
    app = XCUIApplication()

    // Feature flags
    app.launchArguments.append("--uitesting")
    app.launchArguments.append("--skip-onboarding")
    app.launchArguments.append("--disable-animations")

    // Environment variables (key-value pairs)
    app.launchEnvironment["API_BASE_URL"] = "http://localhost:8080"
    app.launchEnvironment["MOCK_AUTH_TOKEN"] = "test-token-123"
    app.launchEnvironment["LOCALE"] = "en_US"

    app.launch()
}
```

### Reading in App Code

```swift
// In your app's AppDelegate or entry point
struct AppConfig {
    static var isUITesting: Bool {
        ProcessInfo.processInfo.arguments.contains("--uitesting")
    }

    static var shouldSkipOnboarding: Bool {
        ProcessInfo.processInfo.arguments.contains("--skip-onboarding")
    }

    static var apiBaseURL: String {
        ProcessInfo.processInfo.environment["API_BASE_URL"]
            ?? "https://api.production.com"
    }
}

// Usage in app
if AppConfig.isUITesting {
    // Use mock network layer
    NetworkService.shared = MockNetworkService()
}
```

---

## Test Data Injection

### Local Mock Server

```swift
// Launch a local server before tests
override func setUp() {
    super.setUp()

    app = XCUIApplication()
    app.launchEnvironment["API_BASE_URL"] = "http://localhost:8080"
    app.launch()
}

// Combine with a test fixture server (e.g., using Embassy or Swifter)
```

### Pre-Seeded Database

```swift
// Copy a pre-built SQLite database before launch
override func setUp() {
    super.setUp()

    // Use launch argument to trigger data seeding
    app = XCUIApplication()
    app.launchArguments.append("--seed-test-data")
    app.launchArguments.append("--seed-file=test_orders.json")
    app.launch()
}
```

### UserDefaults Injection

```swift
app.launchArguments += ["-user_has_completed_onboarding", "YES"]
app.launchArguments += ["-preferred_currency", "EUR"]
// The - prefix sets UserDefaults keys directly
```

---

## Accessibility Identifier Best Practices

### Naming Convention

```swift
// Pattern: [screen]_[element]_[type] or camelCase with context
// Consistent naming makes test maintenance easier

// UIKit
emailTextField.accessibilityIdentifier = "login_email_textField"
passwordTextField.accessibilityIdentifier = "login_password_secureField"
submitButton.accessibilityIdentifier = "login_submit_button"

// SwiftUI
TextField("Email", text: $email)
    .accessibilityIdentifier("login_email_textField")

SecureField("Password", text: $password)
    .accessibilityIdentifier("login_password_secureField")

Button("Log In") { login() }
    .accessibilityIdentifier("login_submit_button")
```

### Centralized Identifier Registry

```swift
// AccessibilityIdentifiers.swift (shared between app and test targets)
enum AccessibilityID {
    enum Login {
        static let emailField = "login_email_textField"
        static let passwordField = "login_password_secureField"
        static let submitButton = "login_submit_button"
        static let errorBanner = "login_error_banner"
    }

    enum Dashboard {
        static let welcomeLabel = "dashboard_welcome_label"
        static let settingsButton = "dashboard_settings_button"
    }

    enum OrderList {
        static func orderCell(id: String) -> String {
            "orderList_cell_\(id)"
        }
        static let refreshControl = "orderList_refresh"
    }
}

// In production code
submitButton.accessibilityIdentifier = AccessibilityID.Login.submitButton

// In test code
let button = app.buttons[AccessibilityID.Login.submitButton]
```

**Checklist -- Accessibility Identifiers:**

- [ ] Every interactive element has an accessibility identifier
- [ ] Identifiers use a consistent naming convention
- [ ] Identifiers are defined in a shared file between app and test targets
- [ ] Dynamic list items use parameterized identifiers (e.g., `cell_\(id)`)
- [ ] Identifiers do not duplicate accessibility labels (they serve different purposes)

---

## Recording and Debugging

### Xcode Test Recording

```text
1. Open UI test file in Xcode
2. Place cursor inside a test method
3. Click the red Record button at bottom of editor
4. Interact with the app -- Xcode generates XCUITest code
5. Stop recording and clean up generated code

Note: Recorded code is verbose. Always refactor into page objects.
```

### Debugging Techniques

```swift
// Print element tree
func testDebugElementTree() {
    // Print full accessibility hierarchy
    print(app.debugDescription)

    // Print specific container
    print(app.tables.firstMatch.debugDescription)
}

// Screenshot during test
func testWithScreenshot() {
    let screenshot = app.screenshot()
    let attachment = XCTAttachment(screenshot: screenshot)
    attachment.name = "debug-screenshot"
    attachment.lifetime = .keepAlways
    add(attachment)
}

// Conditional breakpoint in test
func testWithDebugging() {
    let button = app.buttons["submitButton"]
    // Set breakpoint here and use `po app.debugDescription` in lldb
    if !button.exists {
        let screenshot = app.screenshot()
        add(XCTAttachment(screenshot: screenshot))
        XCTFail("Submit button not found. See screenshot attachment.")
    }
}
```

### Common Debugging Commands (LLDB)

```text
(lldb) po app.debugDescription           # Full element tree
(lldb) po app.buttons.debugDescription    # All buttons
(lldb) po app.buttons["login"].exists     # Check specific element
(lldb) expr app.screenshot()              # Capture screenshot
```

---

## Related Resources

- [xctest-patterns.md](xctest-patterns.md) -- XCTest unit testing patterns
- [swift-testing.md](swift-testing.md) -- Modern Swift Testing framework
- [snapshot-testing-ios.md](snapshot-testing-ios.md) -- Visual snapshot testing
- [simulator-commands.md](simulator-commands.md) -- Simulator management
- [ios-ci-optimization.md](ios-ci-optimization.md) -- CI pipeline optimization
