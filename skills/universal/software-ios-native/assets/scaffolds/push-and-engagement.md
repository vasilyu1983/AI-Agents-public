# Scaffold: Push + Engagement

Copy-paste push registration with **deferred opt-in** (the single highest-leverage engagement decision) plus a reachability publisher. App-class-agnostic. Fill the `// TODO` markers.

Pairs with [cloudflare-worker-backend.md](cloudflare-worker-backend.md) (the server that stores device tokens and sends push) and [../../references/starter-stacks-and-monetization.md](../../references/starter-stacks-and-monetization.md) (engagement layer).

## When to Use

- Any app where re-engagement matters (most). Push opt-in correlates with large engagement lifts — but only if you ask at the right moment.
- For delivery analytics, segmentation, rich media, or push A/B, graduate to OneSignal/Firebase; this scaffold is the free Tier-1 path (your server → APNs).

## The one rule

**Never call `requestAuthorization` on first launch.** The system dialog fires once; a cold "Deny" is permanent. Gate it behind an action with an obvious notification benefit ("notify me when this is ready"), after a custom pre-prompt that explains the exact notification.

## PushManager.swift

```swift
import SwiftUI
import UserNotifications

/// Owns notification permission + token registration. @MainActor so it can mutate
/// @Observable state safely. The delegate isolation here matters: a `nonisolated
/// async` delegate doing nested `await MainActor.run { }` is a known SwiftUI crash
/// (the _performBlockAfterCATransactionCommitSynchronizes family). Keep it @MainActor.
@Observable
@MainActor
final class PushManager: NSObject {
    enum Status { case unknown, notRequested, authorized, denied }
    private(set) var status: Status = .unknown
    private(set) var deviceToken: String?

    func refreshStatus() async {
        let settings = await UNUserNotificationCenter.current().notificationSettings()
        switch settings.authorizationStatus {
        case .notDetermined: status = .notRequested
        case .denied: status = .denied
        case .authorized, .provisional, .ephemeral: status = .authorized
        @unknown default: status = .unknown
        }
    }

    /// Call ONLY from a contextual moment (after a pre-prompt the user accepted).
    func requestAuthorizationAndRegister() async {
        do {
            let granted = try await UNUserNotificationCenter.current()
                .requestAuthorization(options: [.alert, .badge, .sound])
            status = granted ? .authorized : .denied
            if granted {
                UIApplication.shared.registerForRemoteNotifications()
            }
        } catch {
            status = .denied
        }
    }

    /// Called by the AppDelegate hook below. Send this token to your server.
    func didRegister(tokenData: Data) {
        let token = tokenData.map { String(format: "%02x", $0) }.joined()
        deviceToken = token
        Task { await uploadToken(token) }
    }

    private func uploadToken(_ token: String) async {
        // TODO: POST the token + the current APNs environment (sandbox vs prod)
        // to your Cloudflare Worker. Store the token PER DEVICE on the server and
        // route by the device's environment — a global env var must stay a
        // production-safe fallback only (mismatched env => BadDeviceToken).
        _ = token
    }
}
```

## AppDelegate hook (SwiftUI app)

```swift
import SwiftUI

@main
struct MyApp: App {
    @UIApplicationDelegateAdaptor(AppDelegate.self) private var appDelegate
    @State private var push = PushManager()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environment(push)
                .task { await push.refreshStatus() }
        }
    }
}

final class AppDelegate: NSObject, UIApplicationDelegate {
    // PushManager is resolved from the environment at the call site; for the
    // token callback, post a Notification or hold a reference your app injects.
    func application(_ application: UIApplication,
                     didRegisterForRemoteNotificationsWithDeviceToken data: Data) {
        NotificationCenter.default.post(name: .didRegisterPushToken, object: data)
    }
    func application(_ application: UIApplication,
                     didFailToRegisterForRemoteNotificationsWithError error: Error) {
        // TODO: log; common cause in sim is no push entitlement / no APNs env.
    }
}

extension Notification.Name { static let didRegisterPushToken = Notification.Name("didRegisterPushToken") }
```

## Contextual opt-in (the pattern that converts)

```swift
// At a moment with an obvious notification benefit — NOT first launch:
Button("Notify me when it's ready") {
    showPushPrePrompt = true        // your custom screen explaining the value
}
// In the pre-prompt's "Enable" button:
.task { await push.requestAuthorizationAndRegister() }
```

## Reachability (disable submit when offline)

```swift
import Network

@Observable
@MainActor
final class Reachability {
    private(set) var isConnected = true
    private let monitor = NWPathMonitor()
    func start() {
        monitor.pathUpdateHandler = { [weak self] path in
            Task { @MainActor in self?.isConnected = (path.status == .satisfied) }
        }
        monitor.start(queue: .global(qos: .utility))
    }
}
```

## Fill-in checklist

- [ ] Add the Push Notifications capability + background `remote-notification` mode only if you genuinely use it (background-mode abuse is a rejection cause).
- [ ] Pre-prompt screen written; opt-in deferred behind a real action.
- [ ] Server stores token per device WITH its APNs environment; prod env var is fallback only.
- [ ] Verified on TestFlight (archived entitlements), not just the Xcode build — APNs env mismatch is the usual TestFlight-only push failure.
