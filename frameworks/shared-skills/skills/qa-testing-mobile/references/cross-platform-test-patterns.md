# Cross-Platform Mobile Test Patterns

Test patterns and architecture for cross-platform mobile apps: React Native (Detox), Flutter (integration_test), Kotlin Multiplatform, and Appium as a universal layer.

## Contents

- Shared Test Layer Architecture
- Platform-Specific Test Isolation
- Detox for React Native
- Flutter Integration Testing
- Kotlin Multiplatform Test Sharing
- Appium Cross-Platform Patterns
- Test Data Sharing Strategies
- Abstraction Layers for Platform Differences
- CI Matrix Configuration
- When to Write Shared vs Platform-Specific Tests
- Migration Guide
- Related Resources

---

## Shared Test Layer Architecture

### The Cross-Platform Test Pyramid

```text
                    ┌──────────────┐
                    │   E2E/UI     │  Platform-specific (Detox, XCUITest, Espresso)
                    │  (per-plat)  │  or cross-platform (Appium)
                   ─┼──────────────┼─
                  │  Integration   │  Shared logic tests + platform API mocks
                  │   (shared)     │
                ──┼────────────────┼──
              │      Unit Tests      │  Shared business logic (Jest, Dart test, KMP)
              │       (shared)       │
            ──┴──────────────────────┴──
```

### Layer Ownership

| Layer | Shared? | Framework Examples | Run Frequency |
|-------|---------|--------------------|---------------|
| Unit (business logic) | Yes | Jest, Dart test, KMP common test | Every commit |
| Integration (API, state) | Mostly | Supertest, Dio mock, Ktor mock | Every commit |
| UI component | Partial | React Native Testing Library, Flutter Widget test | Every commit |
| E2E (device) | Platform-specific or cross-platform | Detox, integration_test, Appium | PR + nightly |

---

## Platform-Specific Test Isolation

### When Platform Tests Diverge

Not all behavior is identical across iOS and Android. Isolate tests for:

```text
ALWAYS PLATFORM-SPECIFIC:
  ✓ Push notification handling (APNs vs FCM)
  ✓ Deep link / Universal Link / App Link resolution
  ✓ Permissions dialogs (different UI per OS)
  ✓ Background task scheduling (BGTaskScheduler vs WorkManager)
  ✓ Biometric authentication (Face ID vs fingerprint)
  ✓ File system paths and storage APIs
  ✓ Platform-specific UI components (UIKit / Jetpack Compose wrappers)

SAFE TO SHARE:
  ✓ Business logic and validation rules
  ✓ API integration (same endpoints)
  ✓ Navigation flows (screen sequence)
  ✓ Form input and data entry
  ✓ Authentication flows (login, logout, token refresh)
  ✓ Search, filter, sort behavior
```

### Test File Organization

```text
tests/
├── shared/                    # Cross-platform tests
│   ├── auth.test.ts           # Login/logout flows
│   ├── search.test.ts         # Search behavior
│   └── checkout.test.ts       # Purchase flow
├── ios/                       # iOS-only tests
│   ├── push-notifications.test.ts
│   ├── face-id.test.ts
│   └── universal-links.test.ts
├── android/                   # Android-only tests
│   ├── push-notifications.test.ts
│   ├── fingerprint.test.ts
│   └── app-links.test.ts
└── helpers/
    ├── platform.ts            # Platform detection + abstraction
    └── fixtures.ts            # Shared test data
```

---

## Detox for React Native

### Setup

```bash
# Install Detox CLI and dependencies
npm install -D detox @types/detox jest-circus
npx detox init

# Build for testing
npx detox build --configuration ios.sim.debug
npx detox build --configuration android.emu.debug
```

### Configuration

```javascript
// .detoxrc.js
module.exports = {
  testRunner: {
    args: { $0: 'jest', config: 'e2e/jest.config.js' },
    jest: { setupTimeout: 120000 },
  },
  apps: {
    'ios.debug': {
      type: 'ios.app',
      binaryPath: 'ios/build/Build/Products/Debug-iphonesimulator/MyApp.app',
      build: 'xcodebuild -workspace ios/MyApp.xcworkspace -scheme MyApp -configuration Debug -sdk iphonesimulator -derivedDataPath ios/build',
    },
    'android.debug': {
      type: 'android.apk',
      binaryPath: 'android/app/build/outputs/apk/debug/app-debug.apk',
      testBinaryPath: 'android/app/build/outputs/apk/androidTest/debug/app-debug-androidTest.apk',
      build: 'cd android && ./gradlew assembleDebug assembleAndroidTest -DtestBuildType=debug',
    },
  },
  devices: {
    simulator: { type: 'ios.simulator', device: { type: 'iPhone 15' } },
    emulator: { type: 'android.emulator', device: { avdName: 'Pixel_8_API_34' } },
  },
  configurations: {
    'ios.sim.debug': { device: 'simulator', app: 'ios.debug' },
    'android.emu.debug': { device: 'emulator', app: 'android.debug' },
  },
};
```

### Detox Test Patterns

```typescript
// e2e/auth.test.ts - cross-platform Detox test
import { device, element, by, expect } from 'detox';

describe('Authentication', () => {
  beforeAll(async () => {
    await device.launchApp({ newInstance: true });
  });

  beforeEach(async () => {
    await device.reloadReactNative();
  });

  it('should login with valid credentials', async () => {
    await element(by.id('email-input')).typeText('user@example.com');
    await element(by.id('password-input')).typeText('password123');
    await element(by.id('login-button')).tap();

    await waitFor(element(by.id('dashboard-screen')))
      .toBeVisible()
      .withTimeout(5000);
  });

  it('should show error for invalid credentials', async () => {
    await element(by.id('email-input')).typeText('bad@example.com');
    await element(by.id('password-input')).typeText('wrong');
    await element(by.id('login-button')).tap();

    await expect(element(by.text('Invalid credentials'))).toBeVisible();
  });
});
```

### Detox Flake Reduction

| Technique | Implementation |
|-----------|---------------|
| Use `waitFor` instead of `expect` | `waitFor(el).toBeVisible().withTimeout(5000)` |
| Disable animations | `device.disableSynchronization()` for problematic screens |
| Reset state between tests | `device.reloadReactNative()` in `beforeEach` |
| Use testIDs consistently | `<View testID="unique-id">` on every interactable element |
| Avoid index-based selectors | Use `by.id()` over `by.type().atIndex(n)` |
| Synchronization control | `device.enableSynchronization()` / `device.disableSynchronization()` |

---

## Flutter Integration Testing

### Setup

```yaml
# pubspec.yaml
dev_dependencies:
  integration_test:
    sdk: flutter
  flutter_test:
    sdk: flutter
```

### Test Structure

```dart
// integration_test/app_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:my_app/main.dart' as app;

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  group('Authentication', () {
    testWidgets('login with valid credentials', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      // Enter credentials
      await tester.enterText(find.byKey(const Key('email-input')), 'user@example.com');
      await tester.enterText(find.byKey(const Key('password-input')), 'password123');
      await tester.tap(find.byKey(const Key('login-button')));
      await tester.pumpAndSettle(const Duration(seconds: 3));

      // Verify dashboard
      expect(find.byKey(const Key('dashboard-screen')), findsOneWidget);
    });

    testWidgets('show error for invalid credentials', (tester) async {
      app.main();
      await tester.pumpAndSettle();

      await tester.enterText(find.byKey(const Key('email-input')), 'bad@example.com');
      await tester.enterText(find.byKey(const Key('password-input')), 'wrong');
      await tester.tap(find.byKey(const Key('login-button')));
      await tester.pumpAndSettle(const Duration(seconds: 3));

      expect(find.text('Invalid credentials'), findsOneWidget);
    });
  });
}
```

### Running on Both Platforms

```bash
# iOS simulator
flutter test integration_test/app_test.dart -d "iPhone 15"

# Android emulator
flutter test integration_test/app_test.dart -d emulator-5554

# All integration tests on both platforms (CI)
flutter test integration_test/ -d "iPhone 15"
flutter test integration_test/ -d emulator-5554
```

### Flutter-Specific Patterns

```dart
// Custom test utilities for Flutter
extension IntegrationTestHelpers on WidgetTester {
  /// Scroll until widget is visible
  Future<void> scrollUntilVisible(
    Finder finder,
    Finder scrollable, {
    double delta = 300,
    int maxScrolls = 20,
  }) async {
    int scrolls = 0;
    while (finder.evaluate().isEmpty && scrolls < maxScrolls) {
      await drag(scrollable, Offset(0, -delta));
      await pumpAndSettle();
      scrolls++;
    }
  }

  /// Wait for network-dependent widget
  Future<void> waitForWidget(Finder finder, {Duration timeout = const Duration(seconds: 10)}) async {
    final end = DateTime.now().add(timeout);
    while (finder.evaluate().isEmpty && DateTime.now().isBefore(end)) {
      await pump(const Duration(milliseconds: 100));
    }
    expect(finder, findsOneWidget);
  }
}
```

---

## Kotlin Multiplatform Test Sharing

### Shared Test Module

```kotlin
// shared/src/commonTest/kotlin/AuthTests.kt
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class AuthValidationTest {
    private val validator = AuthValidator()

    @Test
    fun validEmailAccepted() {
        assertTrue(validator.isValidEmail("user@example.com"))
    }

    @Test
    fun invalidEmailRejected() {
        assertTrue(!validator.isValidEmail("not-an-email"))
    }

    @Test
    fun passwordStrengthCalculation() {
        assertEquals(PasswordStrength.WEAK, validator.checkStrength("abc"))
        assertEquals(PasswordStrength.STRONG, validator.checkStrength("C0mpl3x!Pass"))
    }
}
```

### Platform-Specific Test Expectations

```kotlin
// shared/src/iosTest/kotlin/PlatformAuthTest.kt
import kotlin.test.Test
import kotlin.test.assertEquals

class PlatformAuthTest {
    @Test
    fun biometricTypeIsCorrect() {
        val biometric = BiometricHelper()
        // iOS returns FaceID or TouchID
        assertTrue(biometric.availableType in listOf(
            BiometricType.FACE_ID, BiometricType.TOUCH_ID, BiometricType.NONE
        ))
    }
}

// shared/src/androidTest/kotlin/PlatformAuthTest.kt
class PlatformAuthTest {
    @Test
    fun biometricTypeIsCorrect() {
        val biometric = BiometricHelper()
        // Android returns FINGERPRINT or FACE
        assertTrue(biometric.availableType in listOf(
            BiometricType.FINGERPRINT, BiometricType.FACE, BiometricType.NONE
        ))
    }
}
```

### KMP Test Structure

```text
shared/
├── src/
│   ├── commonMain/kotlin/        # Shared production code
│   ├── commonTest/kotlin/        # Shared tests (run on ALL platforms)
│   ├── androidMain/kotlin/       # Android-specific code
│   ├── androidUnitTest/kotlin/   # Android-specific tests
│   ├── iosMain/kotlin/           # iOS-specific code
│   └── iosTest/kotlin/           # iOS-specific tests
```

---

## Appium Cross-Platform Patterns

### Page Object Abstraction

```typescript
// pages/LoginPage.ts - shared interface
export interface LoginPage {
  enterEmail(email: string): Promise<void>;
  enterPassword(password: string): Promise<void>;
  tapLogin(): Promise<void>;
  getErrorMessage(): Promise<string>;
}

// pages/LoginPage.ios.ts
export class IOSLoginPage implements LoginPage {
  constructor(private driver: WebdriverIO.Browser) {}

  async enterEmail(email: string) {
    const el = await this.driver.$('~email-input');
    await el.setValue(email);
  }

  async enterPassword(password: string) {
    const el = await this.driver.$('~password-input');
    await el.setValue(password);
  }

  async tapLogin() {
    const el = await this.driver.$('~login-button');
    await el.click();
  }

  async getErrorMessage() {
    const el = await this.driver.$('~error-message');
    return el.getText();
  }
}

// pages/LoginPage.android.ts
export class AndroidLoginPage implements LoginPage {
  constructor(private driver: WebdriverIO.Browser) {}

  async enterEmail(email: string) {
    const el = await this.driver.$('~email-input');
    await el.setValue(email);
  }
  // ... same interface, platform-specific selectors if needed
}
```

### Platform-Aware Test Runner

```typescript
// helpers/platform.ts
import { LoginPage } from '../pages/LoginPage';
import { IOSLoginPage } from '../pages/LoginPage.ios';
import { AndroidLoginPage } from '../pages/LoginPage.android';

export function getLoginPage(driver: WebdriverIO.Browser): LoginPage {
  const platformName = driver.capabilities.platformName;
  if (platformName === 'iOS') return new IOSLoginPage(driver);
  return new AndroidLoginPage(driver);
}

// tests/auth.test.ts - shared test, platform-agnostic
describe('Authentication', () => {
  let loginPage: LoginPage;

  before(async () => {
    loginPage = getLoginPage(driver);
  });

  it('should login successfully', async () => {
    await loginPage.enterEmail('user@example.com');
    await loginPage.enterPassword('password123');
    await loginPage.tapLogin();
    // Assert dashboard visible (cross-platform selector)
    await expect(driver.$('~dashboard-screen')).toBeDisplayed();
  });
});
```

---

## Test Data Sharing Strategies

### Shared Fixtures

```typescript
// fixtures/test-data.ts - shared across platforms
export const TestUsers = {
  valid: { email: 'test-user@example.com', password: 'Test1234!' },
  invalid: { email: 'invalid@example.com', password: 'wrong' },
  admin: { email: 'admin@example.com', password: 'Admin1234!' },
} as const;

export const TestProducts = {
  basic: { id: 'prod-001', name: 'Basic Plan', price: 9.99 },
  premium: { id: 'prod-002', name: 'Premium Plan', price: 29.99 },
} as const;
```

### API-Based Test Data Setup

```typescript
// fixtures/api-setup.ts
export async function seedTestData(baseUrl: string) {
  // Create test user via API (skip UI)
  const response = await fetch(`${baseUrl}/api/test/seed`, {
    method: 'POST',
    headers: { 'X-Test-Key': process.env.TEST_API_KEY! },
    body: JSON.stringify({
      users: [TestUsers.valid, TestUsers.admin],
      products: [TestProducts.basic, TestProducts.premium],
    }),
  });
  return response.json();
}

export async function cleanupTestData(baseUrl: string) {
  await fetch(`${baseUrl}/api/test/cleanup`, {
    method: 'POST',
    headers: { 'X-Test-Key': process.env.TEST_API_KEY! },
  });
}
```

---

## CI Matrix Configuration

### GitHub Actions: Same Tests on Both Platforms

```yaml
# .github/workflows/cross-platform-tests.yml
name: Cross-Platform E2E
on: [push, pull_request]

jobs:
  e2e-tests:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: ios
            os: macos-latest
            device: "iPhone 15"
            command: "npx detox test --configuration ios.sim.debug"
          - platform: android
            os: ubuntu-latest
            device: "Pixel_8_API_34"
            command: "npx detox test --configuration android.emu.debug"
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: 20 }
      - run: npm ci

      - name: Setup Android emulator
        if: matrix.platform == 'android'
        uses: reactivecircus/android-emulator-runner@v2
        with:
          api-level: 34
          target: google_apis
          arch: x86_64
          profile: Pixel 8
          script: ${{ matrix.command }}

      - name: Run iOS tests
        if: matrix.platform == 'ios'
        run: |
          npx detox build --configuration ios.sim.debug
          ${{ matrix.command }}

      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v4
        with:
          name: e2e-artifacts-${{ matrix.platform }}
          path: artifacts/
```

### Flutter CI Matrix

```yaml
jobs:
  integration-tests:
    strategy:
      fail-fast: false
      matrix:
        include:
          - platform: ios
            os: macos-latest
            device: "iPhone 15 Simulator"
          - platform: android
            os: ubuntu-latest
            device: "emulator-5554"
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { flutter-version: '3.x' }
      - run: flutter test integration_test/ -d "${{ matrix.device }}"
```

---

## When to Write Shared vs Platform-Specific Tests

| Signal | Write Shared | Write Platform-Specific |
|--------|-------------|------------------------|
| Same UI on both platforms | Yes | No |
| Same business logic | Yes | No |
| Platform-specific UI widget | No | Yes |
| System dialog (permissions, share sheet) | No | Yes |
| Navigation flow (same screens) | Yes | No |
| Push notifications | No | Yes |
| Deep links / app links | No | Yes |
| Biometric auth | No | Yes |
| File system operations | No | Yes |
| HTTP API calls | Yes | No |
| Form validation | Yes | No |
| Accessibility behavior | Partial | Partial |

### Decision Rule

```text
IF the behavior is:
  - identical on both platforms AND
  - uses the same selectors (testID/key) AND
  - doesn't touch OS-level APIs
THEN write a shared test.

OTHERWISE write platform-specific tests with a shared interface.
```

---

## Migration Guide

### From Platform-Native to Cross-Platform Testing

**Phase 1: Audit existing tests (1 week)**

```text
1. Inventory all native tests (XCUITest, Espresso)
2. Categorize: shared-eligible vs platform-specific
3. Identify testID gaps (add testID/accessibilityIdentifier to shared components)
4. Choose cross-platform framework (Detox for RN, integration_test for Flutter, Appium for native)
```

**Phase 2: Build abstraction layer (1-2 weeks)**

```text
1. Create page objects with platform interface
2. Set up shared test data / fixtures
3. Write first 3-5 cross-platform tests (login, navigation, core flow)
4. Validate on both platforms in CI
```

**Phase 3: Migrate incrementally (ongoing)**

```text
1. New tests: write cross-platform by default
2. Existing tests: migrate during feature work (boy scout rule)
3. Keep platform-specific tests for OS-level behavior
4. Track migration progress: shared_tests / total_tests
```

### Migration Tracking

```text
Cross-Platform Test Migration - Sprint 12
------------------------------------------
Total E2E tests:        84
Shared (cross-plat):    52 (62%)
iOS-only:               16 (19%)
Android-only:           16 (19%)

Target: 75% shared by Q3
```

---

## Related Resources

- [framework-comparison.md](./framework-comparison.md) -- full framework selection guide
- [flake-management.md](./flake-management.md) -- flake patterns specific to cross-platform tests
- [device-farm-strategies.md](./device-farm-strategies.md) -- running cross-platform suites on cloud devices
- [SKILL.md](../SKILL.md) -- parent mobile testing skill
- [Detox Documentation](https://wix.github.io/Detox/)
- [Flutter Integration Testing](https://docs.flutter.dev/testing/integration-tests)
- [Kotlin Multiplatform Testing](https://kotlinlang.org/docs/multiplatform-run-tests.html)
- [Appium Documentation](https://appium.io/docs/en/latest/)
