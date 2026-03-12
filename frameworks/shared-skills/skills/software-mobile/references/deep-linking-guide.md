# Deep Linking and Universal Links Guide

Complete guide to deep linking across iOS and Android. Covers Universal Links, App Links, deferred deep linking, React Native integration, dynamic links, testing, routing architecture, and edge cases.

---

## Deep Link Types

| Type | Description | Requires Install | Fallback |
|------|-------------|-----------------|----------|
| **URI Scheme** | `myapp://path` | Yes | None (error) |
| **Universal Links** (iOS) | `https://example.com/path` | No | Opens in Safari |
| **App Links** (Android) | `https://example.com/path` | No | Opens in browser |
| **Deferred Deep Links** | Routes through install to content | No | Store → app → content |

### When to Use Each

```text
URI Schemes (myapp://):
  ✓ App-to-app communication
  ✓ Internal navigation (React Navigation)
  ✗ Not for web-to-app (no fallback, can be hijacked)

Universal Links / App Links (https://):
  ✓ Web-to-app links (emails, social, web)
  ✓ SEO-friendly (same URL works in browser)
  ✓ Secure (verified domain ownership)
  ✗ Setup is more complex

Deferred Deep Links:
  ✓ Marketing campaigns (user may not have app installed)
  ✓ Referral programs
  ✓ Re-engagement campaigns
  ✗ Requires attribution service (Branch, AppsFlyer, Adjust)
```

---

## iOS Universal Links

### Apple App Site Association (AASA)

The AASA file tells iOS which URLs your app handles. It must be hosted at `https://yourdomain.com/.well-known/apple-app-site-association`.

```json
{
  "applinks": {
    "details": [
      {
        "appIDs": ["TEAMID.com.yourcompany.yourapp"],
        "components": [
          {
            "/": "/product/*",
            "comment": "Product detail pages"
          },
          {
            "/": "/user/*",
            "comment": "User profile pages"
          },
          {
            "/": "/invite/*",
            "comment": "Invitation links"
          },
          {
            "/": "/reset-password",
            "?": { "token": "?*" },
            "comment": "Password reset with token"
          },
          {
            "/": "/admin/*",
            "exclude": true,
            "comment": "Exclude admin paths"
          }
        ]
      }
    ]
  }
}
```

### AASA Requirements

| Requirement | Detail |
|-------------|--------|
| Content-Type | `application/json` (no `.json` extension in URL) |
| HTTPS | Must be served over HTTPS with valid certificate |
| No redirects | Apple's CDN fetches directly — redirects cause failure |
| File size | < 128 KB |
| CDN caching | Apple caches via its own CDN; updates may take 24-48 hours |
| Signing | Not required for `applinks` (required for `webcredentials`) |

### Entitlements Configuration

```xml
<!-- YourApp.entitlements -->
<dict>
    <key>com.apple.developer.associated-domains</key>
    <array>
        <string>applinks:yourdomain.com</string>
        <string>applinks:www.yourdomain.com</string>
    </array>
</dict>
```

### Handling Universal Links

```swift
// SceneDelegate (UIKit) or App (SwiftUI)
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    func scene(
        _ scene: UIScene,
        continue userActivity: NSUserActivity
    ) {
        guard userActivity.activityType == NSUserActivityTypeBrowsingWeb,
              let url = userActivity.webpageURL else { return }

        handleDeepLink(url)
    }
}

// SwiftUI App
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .onOpenURL { url in
                    handleDeepLink(url)
                }
        }
    }
}

// Deep link handler
func handleDeepLink(_ url: URL) {
    guard let components = URLComponents(url: url, resolvingAgainstBaseURL: true) else { return }

    let pathComponents = components.path.split(separator: "/").map(String.init)

    switch pathComponents.first {
    case "product":
        if let productId = pathComponents.dropFirst().first {
            router.navigate(to: .productDetail(id: productId))
        }
    case "user":
        if let userId = pathComponents.dropFirst().first {
            router.navigate(to: .userProfile(id: userId))
        }
    case "invite":
        if let code = pathComponents.dropFirst().first {
            router.navigate(to: .acceptInvitation(code: code))
        }
    case "reset-password":
        let token = components.queryItems?.first(where: { $0.name == "token" })?.value
        if let token {
            router.navigate(to: .resetPassword(token: token))
        }
    default:
        // Unhandled deep link — open home
        router.navigate(to: .home)
    }
}
```

---

## Android App Links

### Digital Asset Links

Host at `https://yourdomain.com/.well-known/assetlinks.json`:

```json
[
  {
    "relation": ["delegate_permission/common.handle_all_urls"],
    "target": {
      "namespace": "android_app",
      "package_name": "com.yourcompany.yourapp",
      "sha256_cert_fingerprints": [
        "AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90:AB:CD:EF:12:34:56:78:90"
      ]
    }
  }
]
```

### Getting SHA-256 Fingerprint

```bash
# Debug keystore
keytool -list -v -keystore ~/.android/debug.keystore -alias androiddebugkey -storepass android

# Release keystore
keytool -list -v -keystore your-release-key.keystore -alias your-alias

# Google Play App Signing (from Play Console)
# Setup > App signing > SHA-256 certificate fingerprint
```

### AndroidManifest Intent Filters

```xml
<activity android:name=".MainActivity">
    <!-- App Links (verified, HTTPS) -->
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />

        <data
            android:scheme="https"
            android:host="yourdomain.com"
            android:pathPrefix="/product" />
        <data
            android:scheme="https"
            android:host="yourdomain.com"
            android:pathPrefix="/user" />
        <data
            android:scheme="https"
            android:host="yourdomain.com"
            android:pathPrefix="/invite" />
    </intent-filter>

    <!-- URI Scheme (unverified, for app-to-app) -->
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />

        <data android:scheme="myapp" android:host="open" />
    </intent-filter>
</activity>
```

### Handling App Links

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent) {
        val uri = intent.data ?: return

        when {
            uri.pathSegments.firstOrNull() == "product" -> {
                val productId = uri.pathSegments.getOrNull(1) ?: return
                navController.navigate("product/$productId")
            }
            uri.pathSegments.firstOrNull() == "user" -> {
                val userId = uri.pathSegments.getOrNull(1) ?: return
                navController.navigate("user/$userId")
            }
            uri.pathSegments.firstOrNull() == "invite" -> {
                val code = uri.pathSegments.getOrNull(1) ?: return
                navController.navigate("invite/$code")
            }
        }
    }
}
```

---

## Deferred Deep Linking

Deferred deep linking routes a user through the app store install process and then into specific content on first launch.

### Flow

```text
1. User clicks link: https://yourdomain.com/invite/ABC123
2. App not installed → redirect to App Store / Play Store
3. User installs app
4. First launch: attribution service provides original link data
5. App navigates to /invite/ABC123 content
```

### Branch.io Integration

```typescript
// React Native with Branch
import branch from 'react-native-branch';

// Subscribe to deep link events
branch.subscribe({
  onOpenStart: ({ uri, cachedInitialEvent }) => {
    console.log('Deep link opening:', uri);
  },
  onOpenComplete: ({ error, params, uri }) => {
    if (error) {
      console.error('Deep link error:', error);
      return;
    }

    if (params['+clicked_branch_link']) {
      // This is a Branch link — handle routing
      const screen = params.screen;
      const id = params.id;

      switch (screen) {
        case 'product':
          navigation.navigate('ProductDetail', { id });
          break;
        case 'invite':
          navigation.navigate('AcceptInvite', { code: params.invite_code });
          break;
      }
    }
  },
});
```

### Attribution Without Third-Party SDK

```text
Lightweight deferred deep link (without Branch/AppsFlyer):

1. User clicks https://yourdomain.com/invite/ABC123
2. Server sets cookie with deep link data
3. Redirect to App Store / Play Store
4. On first launch, app calls server: GET /api/deferred-deeplink
   - Server matches by: device fingerprint, IP + user-agent, or stored cookie
   - Returns original deep link path
5. App navigates to content

Limitations:
  - Less reliable than SDK-based solutions
  - iOS App Tracking Transparency limits fingerprinting
  - Cookie matching requires Safari → App handoff
```

---

## React Native Deep Linking

### React Navigation Linking Configuration

```typescript
// navigation/linking.ts
import { LinkingOptions } from '@react-navigation/native';

export const linking: LinkingOptions<RootParamList> = {
  prefixes: [
    'https://yourdomain.com',
    'myapp://',
  ],
  config: {
    screens: {
      Home: '',
      ProductDetail: 'product/:id',
      UserProfile: 'user/:id',
      AcceptInvite: 'invite/:code',
      ResetPassword: {
        path: 'reset-password',
        parse: {
          token: (token: string) => token,
        },
      },
      Settings: 'settings',
      NotFound: '*',
    },
  },
  // Custom URL resolution
  getStateFromPath: (path, options) => {
    // Custom path parsing if needed
    return getStateFromPath(path, options);
  },
};

// App.tsx
function App() {
  return (
    <NavigationContainer linking={linking} fallback={<LoadingScreen />}>
      <RootNavigator />
    </NavigationContainer>
  );
}
```

### Expo Linking

```typescript
import * as Linking from 'expo-linking';
import { useURL } from 'expo-linking';

// Get initial URL (cold start)
const initialUrl = await Linking.getInitialURL();

// Listen for URLs while app is running
const subscription = Linking.addEventListener('url', ({ url }) => {
  handleDeepLink(url);
});

// Create deep link URL for sharing
const shareUrl = Linking.createURL('product/123', {
  queryParams: { ref: 'share' },
});
// Development: exp://192.168.1.1:8081/--/product/123?ref=share
// Production: myapp://product/123?ref=share
```

---

## Dynamic Links and QR Code Integration

### Generating Dynamic Links

```typescript
// Server-side: generate short deep link
async function createDynamicLink(params: {
  path: string;
  title: string;
  description: string;
  imageUrl?: string;
}): Promise<string> {
  // Option 1: Branch
  const branchLink = await branch.link({
    channel: 'app',
    feature: 'share',
    data: {
      $desktop_url: `https://yourdomain.com${params.path}`,
      $ios_url: `https://yourdomain.com${params.path}`,
      $android_url: `https://yourdomain.com${params.path}`,
      $og_title: params.title,
      $og_description: params.description,
      $og_image_url: params.imageUrl,
      screen: params.path.split('/')[1],
      id: params.path.split('/')[2],
    },
  });

  return branchLink;
}

// Option 2: Self-hosted with QR code
function generateQRDeepLink(path: string): { url: string; qrCodeUrl: string } {
  const deepLinkUrl = `https://yourdomain.com${path}`;
  const qrCodeUrl = `https://api.qrserver.com/v1/create-qr-code/?size=300x300&data=${encodeURIComponent(deepLinkUrl)}`;

  return { url: deepLinkUrl, qrCodeUrl };
}
```

---

## Deep Link Testing and Debugging

### iOS Testing

```bash
# Test Universal Link on simulator
xcrun simctl openurl booted "https://yourdomain.com/product/123"

# Test URI scheme on simulator
xcrun simctl openurl booted "myapp://product/123"

# Validate AASA file
curl -v "https://yourdomain.com/.well-known/apple-app-site-association"

# Check Apple CDN cache of your AASA
curl -v "https://app-site-association.cdn-apple.com/a/v1/yourdomain.com"
```

### Android Testing

```bash
# Test App Link via adb
adb shell am start -a android.intent.action.VIEW \
  -d "https://yourdomain.com/product/123" \
  com.yourcompany.yourapp

# Test URI scheme via adb
adb shell am start -a android.intent.action.VIEW \
  -d "myapp://product/123"

# Verify App Links registration
adb shell pm get-app-links com.yourcompany.yourapp

# Force re-verification
adb shell pm verify-app-links --re-verify com.yourcompany.yourapp
```

### Automated Deep Link Tests

```typescript
// tests/deep-links.spec.ts (Detox)
describe('Deep Links', () => {
  it('opens product detail from universal link', async () => {
    await device.launchApp({
      newInstance: true,
      url: 'https://yourdomain.com/product/123',
    });

    await waitFor(element(by.id('product-detail-screen')))
      .toBeVisible()
      .withTimeout(5000);

    await expect(element(by.id('product-id'))).toHaveText('123');
  });

  it('handles deep link while app is running', async () => {
    await device.launchApp();

    // Simulate deep link while app is in foreground
    await device.openURL({
      url: 'https://yourdomain.com/user/456',
    });

    await waitFor(element(by.id('user-profile-screen')))
      .toBeVisible()
      .withTimeout(5000);
  });

  it('handles invalid deep link gracefully', async () => {
    await device.launchApp({
      newInstance: true,
      url: 'https://yourdomain.com/nonexistent/path',
    });

    // Should show home screen, not crash
    await waitFor(element(by.id('home-screen')))
      .toBeVisible()
      .withTimeout(5000);
  });
});
```

---

## Routing Architecture for Deep Links

### Centralised Deep Link Router

```typescript
// navigation/DeepLinkRouter.ts
type DeepLinkRoute =
  | { screen: 'ProductDetail'; params: { id: string } }
  | { screen: 'UserProfile'; params: { id: string } }
  | { screen: 'AcceptInvite'; params: { code: string } }
  | { screen: 'ResetPassword'; params: { token: string } }
  | { screen: 'Home'; params: undefined }
  | null;

function parseDeepLink(url: string): DeepLinkRoute {
  const parsed = new URL(url);
  const pathParts = parsed.pathname.split('/').filter(Boolean);

  switch (pathParts[0]) {
    case 'product':
      return pathParts[1]
        ? { screen: 'ProductDetail', params: { id: pathParts[1] } }
        : null;
    case 'user':
      return pathParts[1]
        ? { screen: 'UserProfile', params: { id: pathParts[1] } }
        : null;
    case 'invite':
      return pathParts[1]
        ? { screen: 'AcceptInvite', params: { code: pathParts[1] } }
        : null;
    case 'reset-password':
      const token = parsed.searchParams.get('token');
      return token
        ? { screen: 'ResetPassword', params: { token } }
        : null;
    default:
      return { screen: 'Home', params: undefined };
  }
}

// Handle routing with auth state
async function handleDeepLink(url: string, navigation: NavigationRef) {
  const route = parseDeepLink(url);
  if (!route) return;

  const isAuthenticated = await checkAuthState();

  if (route.screen === 'AcceptInvite' && !isAuthenticated) {
    // Store pending deep link, redirect to login
    await storePendingDeepLink(url);
    navigation.navigate('Login');
    return;
  }

  navigation.navigate(route.screen, route.params);
}
```

---

## Edge Cases

### Cold Start vs Background vs Killed State

| State | iOS Handling | Android Handling |
|-------|-------------|-----------------|
| **Cold start** | `onOpenURL` / `scene(_:continue:)` | `onCreate` → `intent.data` |
| **Background** | `onOpenURL` fires | `onNewIntent` fires |
| **Killed** | App launches with URL in `userActivity` | App launches with URL in `intent` |
| **Locked screen** | Deferred until unlock | Deferred until unlock |

### Common Universal Link Failures

| Issue | Cause | Fix |
|-------|-------|-----|
| Link opens in Safari | AASA not found or invalid | Validate AASA at `/.well-known/apple-app-site-association` |
| Works in some browsers, not others | In-app browsers bypass Universal Links | Long-press opens link sheet; use Smart App Banner |
| AASA updates not taking effect | Apple CDN caches AASA | Wait 24-48h; test with `swcutil` on device |
| Link opens wrong app | Multiple apps claim same domain | Check `appIDs` array in AASA |
| Redirect chain breaks link | Universal Links fail if server redirects to different domain | Serve AASA from the same domain as the link |

### Redirect Chain Problem

```text
PROBLEM:
  User clicks: https://link.yourdomain.com/product/123
  Server redirects to: https://yourdomain.com/product/123
  iOS does NOT open app (redirect breaks Universal Link)

SOLUTION 1: Serve AASA from both domains
SOLUTION 2: Use the final domain directly in links
SOLUTION 3: Use Smart App Banner as fallback on web page
```

### Smart App Banner (iOS Safari Fallback)

```html
<!-- Add to web pages as Universal Link fallback -->
<meta
  name="apple-itunes-app"
  content="app-id=123456789, app-argument=https://yourdomain.com/product/123"
/>
```

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Using URI schemes for web-to-app | No fallback if app not installed, security risk | Use Universal Links / App Links |
| Not handling cold-start deep links | User lands on home instead of content | Check for initial URL on app launch |
| Not validating AASA/assetlinks in CI | Broken deep links ship to production | Automated validation in CI |
| Redirect chains in Universal Links | iOS silently falls back to Safari | Direct links, no intermediate redirects |
| Missing auth check before navigation | Unauthenticated user sees protected content | Check auth state, store pending deep link |
| Not testing killed-state deep links | Different code path from background | Test all three app states |
| Hardcoded paths without versioning | Cannot change deep link structure | Use a URL router with pattern matching |

---

## Cross-References

- [push-notifications-guide.md](push-notifications-guide.md) — Deep links from notification taps
- [cross-platform-comparison.md](cross-platform-comparison.md) — Deep linking SDK support per framework
- [ios-best-practices.md](ios-best-practices.md) — iOS app lifecycle and scene delegate
- [android-best-practices.md](android-best-practices.md) — Android intent handling and navigation
- [mobile-testing-patterns.md](mobile-testing-patterns.md) — Automated deep link testing
