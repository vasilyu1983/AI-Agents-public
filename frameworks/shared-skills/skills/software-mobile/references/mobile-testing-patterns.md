# Mobile Testing Patterns

Comprehensive testing strategies for native and cross-platform mobile apps. Covers the testing pyramid, platform-specific frameworks, snapshot testing, device farms, CI/CD integration, flaky test management, and performance testing.

---

## Mobile Testing Pyramid

```text
                    ┌──────────┐
                    │  Manual  │  ~5%  Exploratory, edge cases
                    │  / E2E   │
                   ┌┴──────────┴┐
                   │  UI Tests   │  ~15%  User flows, navigation
                  ┌┴────────────┴┐
                  │  Integration  │  ~25%  API, DB, services
                 ┌┴──────────────┴┐
                 │   Unit Tests    │  ~55%  ViewModels, logic, utils
                 └────────────────┘
```

| Layer | Speed | Reliability | Cost | What to Test |
|-------|-------|-------------|------|-------------|
| Unit | < 1s per test | Very high | Low | Business logic, ViewModels, utilities, parsing |
| Integration | 1-10s | High | Medium | API client + mock server, DB operations, service composition |
| UI/E2E | 10-120s | Medium | High | Critical user flows, navigation, visual regression |
| Manual | Minutes | Variable | Very high | Exploratory, accessibility, real device edge cases |

---

## iOS Testing

### XCTest (Unit + Integration)

```swift
import XCTest
@testable import MyApp

final class PaymentServiceTests: XCTestCase {
    var sut: PaymentService!
    var mockAPI: MockPaymentAPI!

    override func setUp() {
        mockAPI = MockPaymentAPI()
        sut = PaymentService(api: mockAPI)
    }

    override func tearDown() {
        sut = nil
        mockAPI = nil
    }

    func testProcessPaymentSuccess() async throws {
        mockAPI.stubbedResult = .success(.init(id: "pay_123", status: .completed))

        let result = try await sut.processPayment(amount: 999, currency: "USD")

        XCTAssertEqual(result.status, .completed)
        XCTAssertEqual(mockAPI.processPaymentCallCount, 1)
    }

    func testProcessPaymentInsufficientFunds() async {
        mockAPI.stubbedResult = .failure(.insufficientFunds)

        do {
            _ = try await sut.processPayment(amount: 999, currency: "USD")
            XCTFail("Expected error")
        } catch let error as PaymentError {
            XCTAssertEqual(error, .insufficientFunds)
        }
    }
}
```

### Swift Testing (Swift 6.1+)

```swift
import Testing
@testable import MyApp

@Suite("Payment Service")
struct PaymentServiceTests {
    let mockAPI = MockPaymentAPI()
    let sut: PaymentService

    init() {
        sut = PaymentService(api: mockAPI)
    }

    @Test("Processes payment successfully")
    func processPaymentSuccess() async throws {
        mockAPI.stubbedResult = .success(.init(id: "pay_123", status: .completed))

        let result = try await sut.processPayment(amount: 999, currency: "USD")

        #expect(result.status == .completed)
        #expect(mockAPI.processPaymentCallCount == 1)
    }

    @Test("Handles insufficient funds", arguments: [100, 500, 9999])
    func insufficientFunds(amount: Int) async {
        mockAPI.stubbedResult = .failure(.insufficientFunds)

        await #expect(throws: PaymentError.insufficientFunds) {
            try await sut.processPayment(amount: amount, currency: "USD")
        }
    }
}
```

### XCUITest (UI Testing)

```swift
import XCTest

final class LoginUITests: XCTestCase {
    let app = XCUIApplication()

    override func setUp() {
        continueAfterFailure = false
        app.launchArguments = ["--uitesting", "--reset-state"]
        app.launch()
    }

    func testLoginFlow() {
        let emailField = app.textFields["email-input"]
        emailField.tap()
        emailField.typeText("user@example.com")

        let passwordField = app.secureTextFields["password-input"]
        passwordField.tap()
        passwordField.typeText("password123")

        app.buttons["login-button"].tap()

        // Wait for navigation to dashboard
        let dashboard = app.staticTexts["dashboard-title"]
        XCTAssertTrue(dashboard.waitForExistence(timeout: 10))
    }
}
```

---

## Android Testing

### JUnit + ViewModel Testing

```kotlin
import kotlinx.coroutines.test.runTest
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test

class PaymentViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private lateinit var viewModel: PaymentViewModel
    private lateinit var mockRepo: FakePaymentRepository

    @Before
    fun setup() {
        mockRepo = FakePaymentRepository()
        viewModel = PaymentViewModel(mockRepo)
    }

    @Test
    fun `processPayment updates state to success`() = runTest {
        mockRepo.setResult(PaymentResult.Success("pay_123"))

        viewModel.processPayment(amount = 999, currency = "USD")

        val state = viewModel.uiState.value
        assertTrue(state is PaymentUiState.Success)
        assertEquals("pay_123", (state as PaymentUiState.Success).paymentId)
    }

    @Test
    fun `processPayment handles network error`() = runTest {
        mockRepo.setResult(PaymentResult.Error(PaymentError.NetworkError))

        viewModel.processPayment(amount = 999, currency = "USD")

        val state = viewModel.uiState.value
        assertTrue(state is PaymentUiState.Error)
    }
}
```

### Espresso (UI Testing)

```kotlin
import androidx.test.espresso.Espresso.onView
import androidx.test.espresso.action.ViewActions.*
import androidx.test.espresso.assertion.ViewAssertions.matches
import androidx.test.espresso.matcher.ViewMatchers.*
import androidx.test.ext.junit.runners.AndroidJUnit4
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class LoginActivityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun loginFlow_success() {
        onView(withId(R.id.email_input))
            .perform(typeText("user@example.com"), closeSoftKeyboard())

        onView(withId(R.id.password_input))
            .perform(typeText("password123"), closeSoftKeyboard())

        onView(withId(R.id.login_button))
            .perform(click())

        // Verify navigation to dashboard
        onView(withId(R.id.dashboard_title))
            .check(matches(isDisplayed()))
    }
}
```

### Compose Test

```kotlin
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test

class PaymentScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun paymentForm_displaysCorrectly() {
        composeTestRule.setContent {
            PaymentScreen(viewModel = FakePaymentViewModel())
        }

        composeTestRule
            .onNodeWithTag("amount-input")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("pay-button")
            .assertIsDisplayed()
            .assertIsEnabled()
    }

    @Test
    fun paymentForm_disablesButtonDuringProcessing() {
        val viewModel = FakePaymentViewModel(initialState = PaymentUiState.Processing)

        composeTestRule.setContent {
            PaymentScreen(viewModel = viewModel)
        }

        composeTestRule
            .onNodeWithTag("pay-button")
            .assertIsNotEnabled()
    }
}
```

### UIAutomator (Cross-App Testing)

```kotlin
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.By
import androidx.test.uiautomator.Until

class DeepLinkTest {
    @Test
    fun deepLink_opensCorrectScreen() {
        val device = UiDevice.getInstance(InstrumentationRegistry.getInstrumentation())

        // Open deep link via adb
        device.executeShellCommand("am start -a android.intent.action.VIEW -d 'myapp://payment/123'")

        // Wait for app to handle deep link
        device.wait(Until.hasObject(By.res("payment-detail-screen")), 5000)

        val paymentId = device.findObject(By.res("payment-id-text"))
        assertEquals("123", paymentId.text)
    }
}
```

---

## React Native Testing

### Jest (Unit Testing)

```typescript
// __tests__/PaymentService.test.ts
import { PaymentService } from '../services/PaymentService';

describe('PaymentService', () => {
  let service: PaymentService;
  let mockApi: jest.Mocked<PaymentApi>;

  beforeEach(() => {
    mockApi = {
      processPayment: jest.fn(),
      getPaymentStatus: jest.fn(),
    };
    service = new PaymentService(mockApi);
  });

  it('processes payment successfully', async () => {
    mockApi.processPayment.mockResolvedValue({
      id: 'pay_123',
      status: 'completed',
    });

    const result = await service.processPayment(999, 'USD');

    expect(result.status).toBe('completed');
    expect(mockApi.processPayment).toHaveBeenCalledWith(999, 'USD');
  });

  it('throws on insufficient funds', async () => {
    mockApi.processPayment.mockRejectedValue(new InsufficientFundsError());

    await expect(service.processPayment(999, 'USD'))
      .rejects.toThrow(InsufficientFundsError);
  });
});
```

### Detox (E2E Testing)

```typescript
// e2e/login.test.ts
describe('Login Flow', () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true });
  });

  it('should login successfully', async () => {
    await element(by.id('email-input')).typeText('user@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();

    await waitFor(element(by.id('dashboard-title')))
      .toBeVisible()
      .withTimeout(10000);
  });

  it('should show error for invalid credentials', async () => {
    await element(by.id('email-input')).typeText('wrong@example.com');
    await element(by.id('password-input')).typeText('wrong');
    await element(by.id('login-button')).tap();

    await waitFor(element(by.text('Invalid credentials')))
      .toBeVisible()
      .withTimeout(5000);
  });
});
```

### Maestro (YAML-Based E2E)

```yaml
# flows/login.yaml
appId: com.myapp
---
- launchApp
- tapOn:
    id: "email-input"
- inputText: "user@example.com"
- tapOn:
    id: "password-input"
- inputText: "password123"
- tapOn:
    id: "login-button"
- assertVisible:
    id: "dashboard-title"
    timeout: 10000
```

---

## Snapshot and Screenshot Testing

### iOS Snapshot Testing

```swift
// Using swift-snapshot-testing
import SnapshotTesting
import XCTest

final class PaymentCardSnapshotTests: XCTestCase {
    func testPaymentCardDefault() {
        let view = PaymentCardView(amount: "$9.99", status: .pending)
        assertSnapshot(of: view, as: .image(layout: .fixed(width: 375, height: 120)))
    }

    func testPaymentCardDarkMode() {
        let view = PaymentCardView(amount: "$9.99", status: .completed)
        assertSnapshot(of: view, as: .image(
            layout: .fixed(width: 375, height: 120),
            traits: .init(userInterfaceStyle: .dark)
        ))
    }

    func testPaymentCardAccessibility() {
        let view = PaymentCardView(amount: "$9.99", status: .pending)
        assertSnapshot(of: view, as: .image(
            layout: .fixed(width: 375, height: 200),
            traits: .init(preferredContentSizeCategory: .accessibilityLarge)
        ))
    }
}
```

### Android Compose Screenshot Testing

```kotlin
// Using Paparazzi or Roborazzi
import app.cash.paparazzi.Paparazzi
import org.junit.Rule
import org.junit.Test

class PaymentCardScreenshotTest {
    @get:Rule
    val paparazzi = Paparazzi()

    @Test
    fun paymentCard_default() {
        paparazzi.snapshot {
            PaymentCard(amount = "$9.99", status = PaymentStatus.Pending)
        }
    }

    @Test
    fun paymentCard_darkMode() {
        paparazzi.snapshot(theme = "Theme.MyApp.Dark") {
            PaymentCard(amount = "$9.99", status = PaymentStatus.Completed)
        }
    }
}
```

---

## Device Farm Testing

### Platform Comparison

| Service | Real Devices | Emulators | Parallel | Pricing | Best For |
|---------|-------------|-----------|----------|---------|----------|
| Firebase Test Lab | Yes | Yes (Android) | Yes | Pay per minute | Android-first teams |
| AWS Device Farm | Yes | No | Yes | Pay per minute | Enterprise, custom devices |
| BrowserStack | Yes | No | Yes | Monthly plans | Cross-platform teams |
| Sauce Labs | Yes | Yes | Yes | Monthly plans | Large test suites |
| Bitrise Device Testing | Yes | Yes | Yes | Included in plan | CI/CD-integrated teams |

### Firebase Test Lab Configuration

```yaml
# .github/workflows/android-test.yml
- name: Run tests on Firebase Test Lab
  run: |
    gcloud firebase test android run \
      --type instrumentation \
      --app app/build/outputs/apk/debug/app-debug.apk \
      --test app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk \
      --device model=Pixel7,version=34 \
      --device model=SamsungGalaxyS23,version=33 \
      --timeout 10m \
      --results-dir test-results \
      --results-bucket gs://my-test-bucket
```

### Device Matrix Strategy

| Tier | Devices | OS Versions | Run Frequency |
|------|---------|-------------|---------------|
| **Tier 1** | iPhone 15, Pixel 8 | Latest OS | Every PR |
| **Tier 2** | iPhone 13, Galaxy S22, Pixel 6 | Latest - 1 | Nightly |
| **Tier 3** | iPhone SE, budget Android | Oldest supported | Weekly |

---

## CI/CD Integration

### iOS CI Pipeline

```yaml
# .github/workflows/ios.yml
name: iOS CI
on: [pull_request]

jobs:
  test:
    runs-on: macos-14
    steps:
      - uses: actions/checkout@v4

      - name: Select Xcode
        run: sudo xcode-select -s /Applications/Xcode_16.app

      - name: Unit Tests
        run: |
          xcodebuild test \
            -scheme MyApp \
            -destination 'platform=iOS Simulator,name=iPhone 16' \
            -resultBundlePath TestResults.xcresult

      - name: Upload Results
        uses: actions/upload-artifact@v4
        with:
          name: test-results
          path: TestResults.xcresult
```

### Android CI Pipeline

```yaml
# .github/workflows/android.yml
name: Android CI
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up JDK
        uses: actions/setup-java@v4
        with:
          java-version: '17'
          distribution: 'temurin'

      - name: Unit Tests
        run: ./gradlew testDebugUnitTest

      - name: Android Lint
        run: ./gradlew lintDebug
```

### React Native CI Pipeline

```yaml
# .github/workflows/rn.yml
name: React Native CI
on: [pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - name: Install Dependencies
        run: npm ci

      - name: Type Check
        run: npx tsc --noEmit

      - name: Unit Tests
        run: npx jest --coverage --ci

      - name: Lint
        run: npx eslint .
```

---

## Flaky Test Management

### Common Causes of Flaky Mobile Tests

| Cause | Platform | Fix |
|-------|----------|-----|
| Animation timing | All | Disable animations in test mode |
| Network latency | All | Use mock servers, not real APIs |
| Async state race | All | Use proper wait/expect patterns |
| Simulator/emulator startup | iOS/Android | Warm up in CI setup step |
| Keyboard appearance | All | Use `closeSoftKeyboard()` / dismiss |
| Date/time dependency | All | Mock system clock |
| Device state (low memory, etc.) | Device farms | Reset device state before test |

### Flaky Test Strategy

```text
1. Quarantine: Move flaky test to quarantine suite
2. Track: Log flaky rate per test (aim for < 1% flake rate)
3. Fix: Dedicate time each sprint to fix quarantined tests
4. Gate: Block merge on non-quarantine test failures only
5. Alert: Notify team when quarantine suite grows > 5% of total
```

---

## Performance Testing

### Key Metrics

| Metric | Target | Tool |
|--------|--------|------|
| Cold start time | < 2s | Instruments (iOS), Macrobenchmark (Android) |
| Warm start time | < 500ms | Instruments, Macrobenchmark |
| Frame rate | >= 58 FPS | Instruments, Android Profiler |
| Jank frames | < 1% | Instruments, Android Profiler |
| Memory (steady state) | < 150MB | Instruments, LeakCanary |
| Memory leaks | 0 | LeakCanary, Instruments |
| API response handling | < 100ms to UI | Custom profiling |

### Android Macrobenchmark

```kotlin
@RunWith(AndroidJUnit4::class)
class StartupBenchmark {
    @get:Rule
    val benchmarkRule = MacrobenchmarkRule()

    @Test
    fun coldStartup() {
        benchmarkRule.measureRepeated(
            packageName = "com.myapp",
            metrics = listOf(StartupTimingMetric()),
            iterations = 5,
            startupMode = StartupMode.COLD
        ) {
            pressHome()
            startActivityAndWait()
        }
    }

    @Test
    fun scrollPerformance() {
        benchmarkRule.measureRepeated(
            packageName = "com.myapp",
            metrics = listOf(FrameTimingMetric()),
            iterations = 5
        ) {
            startActivityAndWait()
            device.findObject(By.res("item-list")).apply {
                repeat(5) { fling(Direction.DOWN) }
            }
        }
    }
}
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| No unit tests, only E2E | Slow, flaky, expensive | Follow testing pyramid proportions |
| Testing implementation details | Tests break on refactor | Test behaviour and outputs |
| Hardcoded test data | Brittle, hard to maintain | Use factories and fixtures |
| Skipping device farm testing | Bugs only on specific devices | Run tier 2-3 device tests weekly |
| No performance regression tests | Gradual degradation goes unnoticed | Benchmark critical paths in CI |
| Testing on only one OS version | Version-specific bugs missed | Test on oldest + newest supported |

---

## Cross-References

- [cross-platform-comparison.md](cross-platform-comparison.md) — Framework selection and ecosystem comparison
- [ios-best-practices.md](ios-best-practices.md) — iOS testing with XCTest, Swift Testing, ViewInspector
- [android-best-practices.md](android-best-practices.md) — Android testing with JUnit, Compose Test, Espresso
- [operational-playbook.md](operational-playbook.md) — CI/CD patterns and release workflows
