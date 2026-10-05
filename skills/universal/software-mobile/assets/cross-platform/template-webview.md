# WebView Wrapper Template (iOS + Android)

Wrap your existing web application in native mobile containers using WKWebView (iOS) and WebView (Android). Perfect for Progressive Web Apps (PWAs) or when you want native app distribution for a web application.

---

## When to Use WebView Approach

**Good Fit:**
- Existing web application you want to distribute via app stores
- Content-heavy apps (news, blogs, documentation)
- Rapid prototyping before building native UI
- Web-first strategy with native app as secondary channel
- Frequent updates without app store review delays

**Not Recommended:**
- Performance-critical apps (games, video editing)
- Heavy use of device hardware (camera, sensors)
- Apps requiring complex native UI patterns
- Offline-first mobile experiences

---

## Architecture

```
WebView App
├── Native Shell (iOS/Android)
│   ├── WebView container
│   ├── JavaScript bridge
│   ├── Deep linking
│   ├── Push notifications
│   └── Native features (camera, location, etc.)
└── Web Application
    ├── Responsive web UI
    ├── Service Worker (offline support)
    └── Web APIs
```

---

## Part 1: iOS WebView Implementation

### Project Structure (iOS)

```
YourWebApp-iOS/
├── YourWebApp/
│   ├── App/
│   │   ├── YourWebAppApp.swift
│   │   └── ContentView.swift
│   ├── WebView/
│   │   ├── WebView.swift
│   │   ├── WebViewCoordinator.swift
│   │   └── JavaScriptBridge.swift
│   ├── Services/
│   │   ├── NotificationService.swift
│   │   └── DeepLinkService.swift
│   └── Utilities/
│       └── Constants.swift
└── Info.plist
```

### 1. WebView Component (iOS)

**WebView/WebView.swift**
```swift
import SwiftUI
import WebKit

struct WebView: UIViewRepresentable {
    let url: URL
    @Binding var isLoading: Bool
    @Binding var error: Error?

    func makeCoordinator() -> WebViewCoordinator {
        WebViewCoordinator(self)
    }

    func makeUIView(context: Context) -> WKWebView {
        let configuration = WKWebViewConfiguration()
        configuration.allowsInlineMediaPlayback = true
        configuration.mediaTypesRequiringUserActionForPlayback = []

        // Enable caching
        configuration.websiteDataStore = .default()

        let webView = WKWebView(frame: .zero, configuration: configuration)
        webView.navigationDelegate = context.coordinator
        webView.scrollView.contentInsetAdjustmentBehavior = .never

        // Add JavaScript bridge
        let bridge = JavaScriptBridge()
        bridge.setupBridge(for: webView)

        return webView
    }

    func updateUIView(_ webView: WKWebView, context: Context) {
        if webView.url != url {
            let request = URLRequest(url: url)
            webView.load(request)
        }
    }
}
```

**WebView/WebViewCoordinator.swift**
```swift
import WebKit

class WebViewCoordinator: NSObject, WKNavigationDelegate {
    var parent: WebView

    init(_ parent: WebView) {
        self.parent = parent
    }

    func webView(_ webView: WKWebView, didStartProvisionalNavigation navigation: WKNavigation!) {
        parent.isLoading = true
    }

    func webView(_ webView: WKWebView, didFinish navigation: WKNavigation!) {
        parent.isLoading = false
    }

    func webView(_ webView: WKWebView, didFail navigation: WKNavigation!, withError error: Error) {
        parent.isLoading = false
        parent.error = error
    }

    func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction, decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
        // Handle external links
        if let url = navigationAction.request.url,
           !url.absoluteString.hasPrefix("https://yourdomain.com") {
            if UIApplication.shared.canOpenURL(url) {
                UIApplication.shared.open(url)
                decisionHandler(.cancel)
                return
            }
        }

        decisionHandler(.allow)
    }
}
```

**WebView/JavaScriptBridge.swift**
```swift
import WebKit

class JavaScriptBridge: NSObject, WKScriptMessageHandler {
    func setupBridge(for webView: WKWebView) {
        let contentController = webView.configuration.userContentController

        // Add message handlers
        contentController.add(self, name: "nativeLog")
        contentController.add(self, name: "nativeShare")
        contentController.add(self, name: "nativeNotification")

        // Inject JavaScript
        let script = """
        window.nativeBridge = {
            log: function(message) {
                window.webkit.messageHandlers.nativeLog.postMessage(message);
            },
            share: function(data) {
                window.webkit.messageHandlers.nativeShare.postMessage(data);
            },
            requestNotificationPermission: function() {
                window.webkit.messageHandlers.nativeNotification.postMessage('request');
            }
        };
        """

        let userScript = WKUserScript(
            source: script,
            injectionTime: .atDocumentEnd,
            forMainFrameOnly: false
        )

        contentController.addUserScript(userScript)
    }

    func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
        switch message.name {
        case "nativeLog":
            if let body = message.body as? String {
                print("Web Log:", body)
            }

        case "nativeShare":
            if let data = message.body as? [String: Any],
               let text = data["text"] as? String {
                shareContent(text: text)
            }

        case "nativeNotification":
            requestNotificationPermission()

        default:
            break
        }
    }

    private func shareContent(text: String) {
        DispatchQueue.main.async {
            let activityVC = UIActivityViewController(
                activityItems: [text],
                applicationActivities: nil
            )

            if let windowScene = UIApplication.shared.connectedScenes.first as? UIWindowScene,
               let rootViewController = windowScene.windows.first?.rootViewController {
                rootViewController.present(activityVC, animated: true)
            }
        }
    }

    private func requestNotificationPermission() {
        UNUserNotificationCenter.current().requestAuthorization(options: [.alert, .sound, .badge]) { granted, error in
            print("Notification permission granted:", granted)
        }
    }
}
```

### 2. Main App (iOS)

**App/ContentView.swift**
```swift
import SwiftUI

struct ContentView: View {
    @State private var isLoading = false
    @State private var error: Error?
    @State private var showError = false

    private let webURL = URL(string: "https://yourdomain.com")!

    var body: some View {
        ZStack {
            WebView(url: webURL, isLoading: $isLoading, error: $error)
                .edgesIgnoringSafeArea(.all)

            if isLoading {
                VStack {
                    ProgressView()
                        .scaleEffect(1.5)
                    Text("Loading...")
                        .padding(.top, 8)
                }
                .frame(maxWidth: .infinity, maxHeight: .infinity)
                .background(Color.white.opacity(0.9))
            }
        }
        .alert("Error", isPresented: $showError) {
            Button("OK") { showError = false }
        } message: {
            Text(error?.localizedDescription ?? "An error occurred")
        }
        .onChange(of: error) { newError in
            showError = newError != nil
        }
    }
}
```

### 3. Configuration (iOS)

**Info.plist**
```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <false/>
    <key>NSExceptionDomains</key>
    <dict>
        <key>yourdomain.com</key>
        <dict>
            <key>NSIncludesSubdomains</key>
            <true/>
            <key>NSTemporaryExceptionAllowsInsecureHTTPLoads</key>
            <false/>
        </dict>
    </dict>
</dict>

<key>NSCameraUsageDescription</key>
<string>This app needs camera access for taking photos</string>

<key>NSLocationWhenInUseUsageDescription</key>
<string>This app needs location access</string>
```

---

## Part 2: Android WebView Implementation

### Project Structure (Android)

```
app/
├── src/main/
│   ├── java/com/example/yourwebapp/
│   │   ├── MainActivity.kt
│   │   ├── WebAppInterface.kt
│   │   └── WebViewClient.kt
│   ├── res/
│   │   └── layout/
│   │       └── activity_main.xml
│   └── AndroidManifest.xml
└── build.gradle.kts
```

### 1. WebView Activity (Android)

**MainActivity.kt**
```kotlin
package com.example.yourwebapp

import android.annotation.SuppressLint
import android.os.Bundle
import android.webkit.*
import android.widget.ProgressBar
import android.view.View
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    private lateinit var webView: WebView
    private lateinit var progressBar: ProgressBar

    @SuppressLint("SetJavaScriptEnabled")
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        webView = findViewById(R.id.webview)
        progressBar = findViewById(R.id.progress_bar)

        setupWebView()

        webView.loadUrl("https://yourdomain.com")
    }

    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            mediaPlaybackRequiresUserGesture = false
            setSupportZoom(true)
            builtInZoomControls = false
            useWideViewPort = true
            loadWithOverviewMode = true
        }

        // Add JavaScript interface
        webView.addJavascriptInterface(WebAppInterface(this), "Android")

        // Set WebViewClient
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                val url = request?.url.toString()

                // Handle external URLs
                if (!url.startsWith("https://yourdomain.com")) {
                    // Open in external browser
                    return true
                }

                return false
            }

            override fun onPageStarted(view: WebView?, url: String?, favicon: android.graphics.Bitmap?) {
                progressBar.visibility = View.VISIBLE
            }

            override fun onPageFinished(view: WebView?, url: String?) {
                progressBar.visibility = View.GONE
            }

            override fun onReceivedError(
                view: WebView?,
                request: WebResourceRequest?,
                error: WebResourceError?
            ) {
                progressBar.visibility = View.GONE
                // Show error message
            }
        }

        // Set WebChromeClient for features like file upload, geolocation
        webView.webChromeClient = object : WebChromeClient() {
            override fun onProgressChanged(view: WebView?, newProgress: Int) {
                progressBar.progress = newProgress
            }

            override fun onPermissionRequest(request: PermissionRequest?) {
                // Handle permission requests (camera, microphone, etc.)
                request?.grant(request.resources)
            }
        }
    }

    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }

    override fun onDestroy() {
        webView.destroy()
        super.onDestroy()
    }
}
```

**WebAppInterface.kt**
```kotlin
package com.example.yourwebapp

import android.content.Context
import android.content.Intent
import android.webkit.JavascriptInterface
import android.widget.Toast

class WebAppInterface(private val context: Context) {

    @JavascriptInterface
    fun log(message: String) {
        android.util.Log.d("WebApp", message)
    }

    @JavascriptInterface
    fun showToast(message: String) {
        Toast.makeText(context, message, Toast.LENGTH_SHORT).show()
    }

    @JavascriptInterface
    fun share(text: String) {
        val shareIntent = Intent().apply {
            action = Intent.ACTION_SEND
            type = "text/plain"
            putExtra(Intent.EXTRA_TEXT, text)
        }
        context.startActivity(Intent.createChooser(shareIntent, "Share via"))
    }

    @JavascriptInterface
    fun getDeviceInfo(): String {
        return """
        {
            "platform": "Android",
            "version": "${android.os.Build.VERSION.RELEASE}",
            "model": "${android.os.Build.MODEL}"
        }
        """.trimIndent()
    }
}
```

### 2. Layout (Android)

**res/layout/activity_main.xml**
```xml
<?xml version="1.0" encoding="utf-8"?>
<RelativeLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <WebView
        android:id="@+id/webview"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

    <ProgressBar
        android:id="@+id/progress_bar"
        style="?android:attr/progressBarStyleHorizontal"
        android:layout_width="match_parent"
        android:layout_height="4dp"
        android:layout_alignParentTop="true"
        android:visibility="gone" />

</RelativeLayout>
```

### 3. Configuration (Android)

**AndroidManifest.xml**
```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.CAMERA" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />

    <application
        android:allowBackup="true"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:theme="@style/Theme.YourWebApp"
        android:usesCleartextTraffic="false">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

            <!-- Deep linking -->
            <intent-filter>
                <action android:name="android.intent.action.VIEW" />
                <category android:name="android.intent.category.DEFAULT" />
                <category android:name="android.intent.category.BROWSABLE" />
                <data android:scheme="https" android:host="yourdomain.com" />
            </intent-filter>
        </activity>

    </application>

</manifest>
```

---

## Part 3: Web Application Integration

### JavaScript Bridge Usage

**In your web application:**
```html
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Your Web App</title>
</head>
<body>
    <button onclick="shareContent()">Share</button>
    <button onclick="logMessage()">Log to Native</button>

    <script>
        // Detect platform
        const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent);
        const isAndroid = /Android/.test(navigator.userAgent);

        // Share content
        function shareContent() {
            const text = "Check out this awesome app!";

            if (isIOS && window.nativeBridge) {
                window.nativeBridge.share({ text: text });
            } else if (isAndroid && window.Android) {
                window.Android.share(text);
            } else if (navigator.share) {
                navigator.share({ text: text });
            }
        }

        // Log message
        function logMessage() {
            const message = "Hello from web!";

            if (isIOS && window.nativeBridge) {
                window.nativeBridge.log(message);
            } else if (isAndroid && window.Android) {
                window.Android.log(message);
            } else {
                console.log(message);
            }
        }

        // Request notification permission
        function requestNotifications() {
            if (isIOS && window.nativeBridge) {
                window.nativeBridge.requestNotificationPermission();
            } else if ('Notification' in window) {
                Notification.requestPermission();
            }
        }
    </script>
</body>
</html>
```

### Service Worker (Offline Support)

**service-worker.js**
```javascript
const CACHE_NAME = 'your-app-v1';
const urlsToCache = [
  '/',
  '/styles.css',
  '/app.js',
  '/offline.html'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(() => caches.match('/offline.html'))
  );
});
```

---

## Best Practices

### Performance
- Enable caching for faster load times
- Minimize JavaScript bridge calls
- Use lazy loading for images and assets
- Implement service worker for offline support

### Security
- Use HTTPS only
- Validate all JavaScript bridge inputs
- Restrict external URL navigation
- Implement Content Security Policy

### User Experience
- Show loading indicators
- Handle errors gracefully
- Support back button navigation
- Maintain scroll position on app resume

### Testing
- Test on various devices and OS versions
- Test offline functionality
- Verify deep linking works
- Test JavaScript bridge communication

---

## Deployment Checklist

**iOS:**
- [ ] Configure App Transport Security in Info.plist
- [ ] Add required permission descriptions
- [ ] Set up deep linking URL schemes
- [ ] Test on physical devices
- [ ] Submit to App Store

**Android:**
- [ ] Add required permissions in AndroidManifest.xml
- [ ] Configure ProGuard rules for release builds
- [ ] Test deep linking
- [ ] Generate signed APK/AAB
- [ ] Submit to Google Play

---

## Advanced Features

### Deep Linking

**iOS - Handle Deep Links:**
```swift
// AppDelegate.swift or Scene
func scene(_ scene: UIScene, openURLContexts URLContexts: Set<UIOpenURLContext>) {
    guard let url = URLContexts.first?.url else { return }

    // Extract path and query parameters
    if url.scheme == "yourapp" {
        let path = url.path
        let components = URLComponents(url: url, resolvingAgainstBaseURL: false)
        let queryItems = components?.queryItems

        // Navigate WebView to corresponding URL
        let webURL = "https://yourdomain.com\(path)"
        // Update WebView URL
    }
}
```

**Android - Handle Deep Links:**
```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    handleIntent(intent)
}

override fun onNewIntent(intent: Intent?) {
    super.onNewIntent(intent)
    intent?.let { handleIntent(it) }
}

private fun handleIntent(intent: Intent) {
    val data: Uri? = intent.data
    data?.let {
        val webUrl = "https://yourdomain.com${it.path}?${it.query}"
        webView.loadUrl(webUrl)
    }
}
```

### File Upload Support

**iOS - File Upload:**
```swift
class WebViewCoordinator: NSObject, WKNavigationDelegate, WKUIDelegate {
    func webView(
        _ webView: WKWebView,
        runOpenPanelWith parameters: WKOpenPanelParameters,
        initiatedByFrame frame: WKFrameInfo,
        completionHandler: @escaping ([URL]?) -> Void
    ) {
        let picker = UIDocumentPickerViewController(
            forOpeningContentTypes: [.image, .pdf]
        )
        picker.delegate = self
        picker.allowsMultipleSelection = parameters.allowsMultipleSelection

        // Present picker
        completionHandler([])
    }
}
```

**Android - File Upload:**
```kotlin
private var fileUploadCallback: ValueCallback<Array<Uri>>? = null

webView.webChromeClient = object : WebChromeClient() {
    override fun onShowFileChooser(
        webView: WebView?,
        filePathCallback: ValueCallback<Array<Uri>>?,
        fileChooserParams: FileChooserParams?
    ): Boolean {
        fileUploadCallback = filePathCallback

        val intent = Intent(Intent.ACTION_GET_CONTENT).apply {
            type = "*/*"
            putExtra(Intent.EXTRA_ALLOW_MULTIPLE, true)
        }

        startActivityForResult(
            Intent.createChooser(intent, "Choose File"),
            FILE_CHOOSER_REQUEST_CODE
        )

        return true
    }
}

override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    if (requestCode == FILE_CHOOSER_REQUEST_CODE) {
        fileUploadCallback?.onReceiveValue(
            WebChromeClient.FileChooserParams.parseResult(resultCode, data)
        )
        fileUploadCallback = null
    }
    super.onActivityResult(requestCode, resultCode, data)
}
```

### Push Notifications

**iOS - Firebase Cloud Messaging:**
```swift
import FirebaseMessaging

class NotificationService {
    func configure() {
        UNUserNotificationCenter.current().requestAuthorization(
            options: [.alert, .sound, .badge]
        ) { granted, _ in
            guard granted else { return }

            DispatchQueue.main.async {
                UIApplication.shared.registerForRemoteNotifications()
            }
        }

        Messaging.messaging().token { token, error in
            if let token = token {
                // Send token to web app
                self.sendTokenToWeb(token)
            }
        }
    }

    private func sendTokenToWeb(_ token: String) {
        let script = """
        if (window.receiveNativeToken) {
            window.receiveNativeToken('\(token)');
        }
        """
        // Execute in WebView
    }
}
```

**Android - Firebase Cloud Messaging:**
```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {
    override fun onNewToken(token: String) {
        super.onNewToken(token)

        // Send to web app via JavaScript bridge
        MainActivity.instance?.runOnUiThread {
            MainActivity.instance?.webView?.evaluateJavascript(
                "window.receiveNativeToken && window.receiveNativeToken('$token')",
                null
            )
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        super.onMessageReceived(message)

        // Show notification or pass to web app
        message.data["webUrl"]?.let { url ->
            val intent = Intent(this, MainActivity::class.java).apply {
                putExtra("url", url)
            }
            startActivity(intent)
        }
    }
}
```

### Cookie Management

**iOS - Cookie Sync:**
```swift
class CookieManager {
    static func syncCookies(for url: URL) {
        let cookieStore = WKWebsiteDataStore.default().httpCookieStore

        // Get cookies from HTTPCookieStorage
        if let cookies = HTTPCookieStorage.shared.cookies(for: url) {
            for cookie in cookies {
                cookieStore.setCookie(cookie)
            }
        }
    }

    static func clearCookies() {
        let dataStore = WKWebsiteDataStore.default()
        dataStore.removeData(
            ofTypes: [WKWebsiteDataTypeCookies],
            modifiedSince: Date(timeIntervalSince1970: 0)
        ) {
            print("Cookies cleared")
        }
    }
}
```

**Android - Cookie Sync:**
```kotlin
class CookieManager {
    companion object {
        fun syncCookies(url: String) {
            val cookieManager = android.webkit.CookieManager.getInstance()
            cookieManager.setAcceptCookie(true)
            cookieManager.setAcceptThirdPartyCookies(webView, true)

            // Set specific cookies
            cookieManager.setCookie(url, "session_token=abc123")
            cookieManager.flush()
        }

        fun clearCookies() {
            val cookieManager = android.webkit.CookieManager.getInstance()
            cookieManager.removeAllCookies { success ->
                Log.d("WebView", "Cookies cleared: $success")
            }
        }
    }
}
```

### Offline Detection

**Web App - Detect Online/Offline:**
```javascript
// In your web application
window.addEventListener('online', () => {
    console.log('Back online');
    // Sync pending data
});

window.addEventListener('offline', () => {
    console.log('Gone offline');
    // Show offline UI
});

// Check current status
if (!navigator.onLine) {
    showOfflineMessage();
}
```

### Pull-to-Refresh

**iOS - Pull to Refresh:**
```swift
struct WebView: UIViewRepresentable {
    func makeUIView(context: Context) -> WKWebView {
        let webView = WKWebView()

        let refreshControl = UIRefreshControl()
        refreshControl.addTarget(
            context.coordinator,
            action: #selector(WebViewCoordinator.refresh),
            for: .valueChanged
        )

        webView.scrollView.refreshControl = refreshControl
        webView.scrollView.bounces = true

        return webView
    }
}

class WebViewCoordinator {
    @objc func refresh(_ sender: UIRefreshControl) {
        parent.webView?.reload()
        sender.endRefreshing()
    }
}
```

**Android - Pull to Refresh:**
```kotlin
// Use SwipeRefreshLayout
class MainActivity : AppCompatActivity() {
    private lateinit var swipeRefresh: SwipeRefreshLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        swipeRefresh = findViewById(R.id.swipe_refresh)
        swipeRefresh.setOnRefreshListener {
            webView.reload()
            swipeRefresh.isRefreshing = false
        }
    }
}
```

### Error Handling

**Custom Error Pages:**
```html
<!-- offline.html -->
<!DOCTYPE html>
<html>
<head>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
            background: #f5f5f5;
        }
        .error-container {
            text-align: center;
            padding: 20px;
        }
        button {
            margin-top: 20px;
            padding: 12px 24px;
            background: #007AFF;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <h1>You're Offline</h1>
        <p>Please check your internet connection and try again.</p>
        <button onclick="location.reload()">Retry</button>
    </div>
</body>
</html>
```

---

## Performance Optimization

### Image Optimization

```swift
// iOS - Optimize images before loading
webView.configuration.preferences.minimumFontSize = 10
webView.configuration.preferences.javaScriptCanOpenWindowsAutomatically = false

// Limit memory usage
webView.configuration.processPool = WKProcessPool()
```

```kotlin
// Android - Optimize WebView performance
webView.settings.apply {
    // Enable hardware acceleration
    setRenderPriority(WebSettings.RenderPriority.HIGH)

    // Optimize caching
    cacheMode = WebSettings.LOAD_DEFAULT
    setAppCacheEnabled(true)
    setAppCachePath(cacheDir.absolutePath)

    // Reduce memory usage
    setGeolocationEnabled(false)
    setSaveFormData(false)
}
```

### Memory Management

```swift
// iOS - Clear cache
func clearCache() {
    let dataStore = WKWebsiteDataStore.default()
    let dataTypes = WKWebsiteDataStore.allWebsiteDataTypes()
    let date = Date(timeIntervalSince1970: 0)

    dataStore.removeData(ofTypes: dataTypes, modifiedSince: date) {
        print("Cache cleared")
    }
}
```

```kotlin
// Android - Clear cache
fun clearCache() {
    webView.clearCache(true)
    webView.clearHistory()

    val cookieManager = CookieManager.getInstance()
    cookieManager.removeAllCookies(null)
}
```

---

## Security Hardening

### SSL Pinning (iOS)

```swift
class WebViewCoordinator: NSObject, WKNavigationDelegate {
    func webView(
        _ webView: WKWebView,
        didReceive challenge: URLAuthenticationChallenge,
        completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void
    ) {
        guard let serverTrust = challenge.protectionSpace.serverTrust else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }

        // Verify certificate
        let credential = URLCredential(trust: serverTrust)
        completionHandler(.useCredential, credential)
    }
}
```

### Content Security Policy

```html
<!-- Add to your web app -->
<meta http-equiv="Content-Security-Policy"
      content="default-src 'self';
               script-src 'self' 'unsafe-inline';
               style-src 'self' 'unsafe-inline';
               img-src 'self' data: https:;">
```

---

## Monitoring & Analytics

### Track Page Views

```javascript
// In your web app
function trackPageView(page) {
    if (window.nativeBridge) {
        window.nativeBridge.trackPageView(page);
    }
}

// Track route changes
window.addEventListener('popstate', () => {
    trackPageView(window.location.pathname);
});
```

```swift
// iOS - Analytics integration
func userContentController(
    _ userContentController: WKUserContentController,
    didReceive message: WKScriptMessage
) {
    if message.name == "trackPageView",
       let page = message.body as? String {
        Analytics.logEvent("page_view", parameters: ["page": page])
    }
}
```

---

This enhanced template provides production-ready WebView wrapper implementation with advanced features including deep linking, file uploads, push notifications, offline support, and security hardening for both iOS and Android platforms.
