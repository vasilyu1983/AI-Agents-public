# Push Notification Implementation Guide

Complete guide to push notification implementation across iOS (APNs) and Android (FCM). Covers architecture, permission patterns, notification channels, rich notifications, silent notifications, analytics, troubleshooting, and cross-platform patterns.

---
## Table of Contents

- [Architecture Overview](#architecture-overview)
- [iOS: Apple Push Notification Service (APNs)](#ios-apple-push-notification-service-apns)
- [Android: Firebase Cloud Messaging (FCM)](#android-firebase-cloud-messaging-fcm)
- [iOS: APNs Implementation](#ios-apns-implementation)
- [Authentication: Key-Based (Recommended)](#authentication-key-based-recommended)
- [Device Token Registration](#device-token-registration)
- [APNs Payload Format](#apns-payload-format)
- [Handling Notifications](#handling-notifications)
- [Android: FCM Implementation](#android-fcm-implementation)
- [Message Types](#message-types)
- [FCM Service Implementation](#fcm-service-implementation)
- [Topics and Conditions](#topics-and-conditions)
- [Permission Request Patterns](#permission-request-patterns)
- [Strategy Comparison](#strategy-comparison)
- [Pre-Prompt Pattern (iOS)](#pre-prompt-pattern-ios)
- [Android 13+ Runtime Permission](#android-13-runtime-permission)
- [Notification Channels (Android 8+)](#notification-channels-android-8)
- [Channel Configuration](#channel-configuration)
- [Importance Levels](#importance-levels)
- [Rich Notifications](#rich-notifications)
- [iOS: Notification Content Extension](#ios-notification-content-extension)
- [iOS: Notification Actions](#ios-notification-actions)
- [Android: Rich Notifications](#android-rich-notifications)
- [Silent / Background Notifications](#silent-background-notifications)
- [iOS: Content-Available](#ios-content-available)
- [Android: Data-Only Messages](#android-data-only-messages)
- [Notification Analytics](#notification-analytics)
- [Key Metrics](#key-metrics)
- [Tracking Implementation](#tracking-implementation)
- [Troubleshooting](#troubleshooting)
- [Common Delivery Failures](#common-delivery-failures)
- [Debugging Tools](#debugging-tools)
- [Cross-Platform: React Native](#cross-platform-react-native)
- [Expo Notifications](#expo-notifications)
- [React Native Firebase](#react-native-firebase)
- [Anti-Patterns](#anti-patterns)
- [Cross-References](#cross-references)


## Architecture Overview

### iOS: Apple Push Notification Service (APNs)

```text
┌──────────┐    ┌──────────┐    ┌──────┐    ┌──────────┐
│  Your    │───>│  APNs    │───>│ iOS  │───>│  Your    │
│  Server  │    │  Server  │    │ Device│   │  App     │
└──────────┘    └──────────┘    └──────┘    └──────────┘

Flow:
1. App registers with APNs, receives device token
2. App sends device token to your server
3. Server sends push payload to APNs with device token
4. APNs delivers to device
5. App handles notification (foreground, background, or killed)
```

### Android: Firebase Cloud Messaging (FCM)

```text
┌──────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐
│  Your    │───>│  FCM     │───>│ Android │───>│  Your    │
│  Server  │    │  Server  │    │ Device  │    │  App     │
└──────────┘    └──────────┘    └─────────┘    └──────────┘

Flow:
1. App registers with FCM, receives registration token
2. App sends token to your server
3. Server sends message to FCM with device token (or topic)
4. FCM delivers to device
5. App handles via FirebaseMessagingService
```

---

## iOS: APNs Implementation

### Authentication: Key-Based (Recommended)

```text
Key-based auth (p8):
  - One key works for all your apps
  - Keys do not expire
  - Simpler to manage than certificates

Certificate-based auth (p12):
  - Per-app certificates
  - Expire annually — must rotate
  - Legacy approach, use only if required
```

### Per-device APNs environment routing

Apple runs TWO separate APNs environments with distinct server URLs. A token issued in one is rejected by the other with `BadDeviceToken`. This is the #1 cause of "push works locally but silently fails in TestFlight" and "push worked yesterday but nothing arrives today after a reinstall".

#### The two APNs environments

```text
Sandbox   api.sandbox.push.apple.com   development builds, Xcode-installed
Production api.push.apple.com          App Store builds, distribution-signed TestFlight
```

Same `.p8` auth key works for both — only the host URL differs. The client's build configuration determines which environment Apple issues the token from: a `DEBUG` build with `aps-environment = development` in its entitlements gets a sandbox token; a distribution-signed build with `aps-environment = production` gets a production token.

**A sandbox token sent to production APNs (or vice versa) is rejected with `BadDeviceToken` and the notification silently drops.** There is no user-visible error and the backend's send log shows a successful HTTP 400 response from Apple.

#### Per-device routing column on the device row

The correct architecture is to store the environment on each device row and route per-device, not globally:

```sql
-- Supabase migration example
alter table mobile_push_devices
  add column push_environment text not null default 'production'
  check (push_environment in ('sandbox', 'production'));
```

- iOS client sends the field on register based on its build's `aps-environment` entitlement (see iOS register payload below)
- Backend register endpoint persists the field on upsert
- Backend send code reads `mobile_push_devices.push_environment` for each device row and routes to the matching APNs host (`api.sandbox.push.apple.com` or `api.push.apple.com`)
- Any global `APNS_ENVIRONMENT` env var is a fallback for legacy rows with null `push_environment`, not the primary switch

This makes the dev Xcode build and the production TestFlight build coexist on the same backend without env-var flipping. Test accounts can have mixed sandbox and production rows for different devices, and each send routes correctly.

#### iOS register payload

```swift
// iOS client — CosmicCopilot/Core/Push/PushRegistrationService.swift
private struct PushRegistrationRequest: Encodable {
    let deviceToken: String
    let platform: String
    /// "sandbox" for DEBUG builds, "production" for Release.
    /// Backend routes per-device using this field; the env var is
    /// only a fallback.
    let environment: String
    let authorizationStatus: String
    // ...
}

/// Derived from the build configuration. For stricter detection
/// (e.g. ad-hoc distribution where the scheme is Release but the
/// entitlement is still development), parse the embedded
/// provisioning profile at runtime.
private func currentAPNSEnvironment() -> String {
    #if DEBUG
    return "sandbox"
    #else
    return "production"
    #endif
}
```

```typescript
// Backend (Next.js / Node) — cosmic-copilot/app/src/app/api/v1/mobile/push/register/route.ts
const registerPushDeviceSchema = z.object({
  deviceToken: z.string().min(16).max(512),
  platform: z.literal('ios').default('ios'),
  // Default to 'production' preserves backwards compatibility with
  // older iOS clients that don't yet send the field.
  environment: z.enum(['sandbox', 'production']).default('production'),
  // ...
});
```

Backend send code example:

```typescript
// Backend APNs sender — cosmic-copilot/app/src/lib/push/send.ts
const { data: devices } = await supabase
  .from('mobile_push_devices')
  .select('device_token, push_environment, notification_categories')
  .eq('user_id', userId)
  .eq('is_active', true);

for (const device of devices ?? []) {
  const env = device.push_environment === 'sandbox' ? 'sandbox' : 'production';
  await sendAPNsNotification(device.device_token, payload, env);
}
```

The `sendAPNsNotification` helper maintains two lazy-initialized `ApnsClient` instances (one per environment) and picks the right one based on the argument. Both clients share the same `.p8` key and team ID — only the `host` differs.

#### Device row hygiene during development

Every Xcode reinstall issues a fresh APNs token. The previous token's row stays `is_active=true` in the database until the next push send marks it dead via `BadDeviceToken`. After several debug iterations, a single test user can have 10+ active sandbox rows for the same physical iPhone, and any QA push fans out to all of them — producing one success and N noisy `BadDeviceToken` failures that obscure the verification result.

Pre-test cleanup pattern (run before each push verification cycle):

```sql
-- Keep the freshest active row per (user_id, push_environment) group,
-- deactivate the rest. Idempotent and safe to re-run.
with active_rows as (
  select
    mpd.id              as device_id,
    mpd.user_id,
    mpd.push_environment,
    row_number() over (
      partition by mpd.user_id, mpd.push_environment
      order by mpd.updated_at desc
    ) as freshness_rank
  from auth.users au
  join public.mobile_push_devices mpd on mpd.user_id = au.id
  where lower(au.email) = 'tester@example.com'
    and mpd.is_active = true
),
stale_ids as (
  select device_id from active_rows where freshness_rank > 1
)
update public.mobile_push_devices
set is_active = false, updated_at = now()
where id in (select device_id from stale_ids)
returning id, push_environment;
```

For a test user where the audit trail is not useful, you can also hard-delete stale rows instead of flipping `is_active`:

```sql
-- Hard-delete all inactive rows for the test user (keeps the
-- currently-active row so the iPhone stays registered).
delete from public.mobile_push_devices mpd
using auth.users au
where mpd.user_id = au.id
  and lower(au.email) = 'tester@example.com'
  and mpd.is_active = false;
```

A full worked script with diagnostic queries, preview, cleanup, and verification sections lives at `cosmic-swift/scripts/push-devices-cleanup.sql` in the cosmic project.

#### TestFlight push pre-flight gates

Before uploading an archive to TestFlight, ALL four of these gates must pass. Missing any one means TestFlight will silently fail push delivery for real users.

**G1 — Phase A local Xcode-build push delivers via sandbox**

```bash
curl -sS -X POST https://api.example.com/internal/push/daily-test \
  -H "Authorization: Bearer $CRON_SECRET" \
  -H "Content-Type: application/json" \
  -d "{\"userId\":\"<uuid>\",\"dryRun\":false}"
```

Expected response:

```json
{
  "pushResult": {
    "success": true,
    "deliveries": [
      { "channel": "apns", "success": true, "environment": "sandbox", "topic": "com.example.app" }
    ]
  }
}
```

And the iPhone visibly receives the banner within ~3 seconds.

**G2 — Backend env var is production AND redeploy happened AND QA route still delivers via sandbox**

After flipping `APNS_ENVIRONMENT=production` in the deployment environment (e.g. Vercel Production scope), force a redeploy — env var changes do NOT apply to existing serverless functions until the next deploy. Then re-run the G1 curl against the SAME sandbox device. The response must still show `environment: "sandbox"` and the iPhone must still receive the banner. This proves per-device routing is reading from the database column, not from the env var.

**G3 — Archive entitlement shows `aps-environment = production`**

Create a fresh archive in Xcode (Product → Archive). Before uploading, inspect the signed entitlements:

```bash
codesign -d --entitlements - "/path/to/CosmicCopilot.xcarchive/Products/Applications/CosmicCopilot.app" \
  2>&1 | grep -A1 aps-environment
```

Must print:

```
<key>aps-environment</key>
<string>production</string>
```

If it prints `development`, STOP. The distribution provisioning profile or automatic signing is misconfigured — every TestFlight install will register a sandbox token against the production backend, and every send will fail with `BadDeviceToken`. Fix in Xcode → Signing & Capabilities → regenerate provisioning profile → re-archive.

**G4 — TestFlight install creates a production device row AND the QA route delivers via production**

After TestFlight upload, install the build on the iPhone via TestFlight. The iOS app fires its register payload with `environment: "production"` (because it's now a Release build). Verify the database:

```sql
select push_environment, is_active, updated_at
from mobile_push_devices
where user_id = '<uuid>'
order by updated_at desc
limit 1;
```

Expected: `push_environment = production`, `is_active = true`, `updated_at` within the last few minutes.

Re-run the G1 curl. The response must now show `environment: "production"` and the iPhone must receive the banner.

After all four gates pass, TestFlight is cleared for distribution.

#### Common APNs failure modes

| Error `reason` | Likely cause | Fix |
|----------------|--------------|-----|
| `BadDeviceToken` + `environment: "production"` in response | Device row has `push_environment='production'` but the token is actually a sandbox token (usually from a prior TestFlight install whose row wasn't cleaned up) | Run the cleanup SQL above to deactivate stale production rows, or force re-register by deleting and reinstalling the app |
| `BadDeviceToken` + `environment: "sandbox"` in response | Token is genuinely stale — uninstall, iCloud restore, or sandbox rotation | Delete app from device + reinstall via Xcode to force a fresh token; deactivate the failing row |
| `Unregistered` | Apple invalidated the token (user uninstalled, app bundle ID changed) | Deactivate the row and wait for a fresh register on next install |
| `DeviceTokenNotForTopic` | `APNS_BUNDLE_ID` env var does not match the iOS app's bundle identifier | Fix the env var in the backend deployment; redeploy |
| `ExpiredProviderToken` | The `.p8` key's JWT has expired (rare — the library should regenerate automatically) | Force the backend to rebuild the APNs client so it issues a fresh JWT |
| `apns_not_configured` (custom app error) | One of `APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_KEY_BASE64`, `APNS_BUNDLE_ID` is missing from the deployment env | Fix the env vars; redeploy |

**Reference:** [twocentstudios 2025-08 article — 3 Swift Concurrency Challenges from the Last 2 Weeks](https://twocentstudios.com/2025/08/12/3-swift-concurrency-challenges-from-the-last-2-weeks/) documents the iOS-side `UNUserNotificationCenterDelegate` crash that blocks a working per-device routing pipeline end-to-end. See also the [swift-concurrency-crash-triage.md](../../software-ios-runtime-debugging/references/swift-concurrency-crash-triage.md) runbook in the runtime debugging skill.

### Device Token Registration

```swift
// AppDelegate.swift
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
    ) -> Bool {
        UNUserNotificationCenter.current().delegate = self
        application.registerForRemoteNotifications()
        return true
    }

    func application(
        _ application: UIApplication,
        didRegisterForRemoteNotificationsWithDeviceToken deviceToken: Data
    ) {
        let token = deviceToken.map { String(format: "%02.2hhx", $0) }.joined()
        // Send token to your server
        Task { await APIService.shared.registerPushToken(token) }
    }

    func application(
        _ application: UIApplication,
        didFailToRegisterForRemoteNotificationsWithError error: Error
    ) {
        print("Push registration failed: \(error.localizedDescription)")
    }
}
```

### APNs Payload Format

```json
{
  "aps": {
    "alert": {
      "title": "New Message",
      "subtitle": "From John",
      "body": "Hey, are you free for lunch?",
      "launch-image": "chat-icon"
    },
    "badge": 3,
    "sound": "default",
    "category": "MESSAGE_CATEGORY",
    "thread-id": "chat-123",
    "mutable-content": 1,
    "content-available": 1
  },
  "custom_data": {
    "chat_id": "123",
    "sender_id": "user_456"
  }
}
```

### Handling Notifications

```swift
extension AppDelegate: UNUserNotificationCenterDelegate {
    // Called when notification arrives while app is in foreground
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        willPresent notification: UNNotification,
        withCompletionHandler completionHandler: @escaping (UNNotificationPresentationOptions) -> Void
    ) {
        let userInfo = notification.request.content.userInfo
        // Process notification data
        processNotification(userInfo)

        // Show banner + sound even in foreground
        completionHandler([.banner, .sound, .badge])
    }

    // Called when user taps notification
    func userNotificationCenter(
        _ center: UNUserNotificationCenter,
        didReceive response: UNNotificationResponse,
        withCompletionHandler completionHandler: @escaping () -> Void
    ) {
        let userInfo = response.notification.request.content.userInfo
        let actionIdentifier = response.actionIdentifier

        switch actionIdentifier {
        case UNNotificationDefaultActionIdentifier:
            // User tapped notification body
            navigateToContent(userInfo)
        case "REPLY_ACTION":
            if let textResponse = response as? UNTextInputNotificationResponse {
                handleReply(text: textResponse.userText, context: userInfo)
            }
        default:
            break
        }

        completionHandler()
    }
}
```

---

## Android: FCM Implementation

### Message Types

| Type | Display | Data Access | Background Behaviour |
|------|---------|-------------|---------------------|
| **Notification message** | System tray auto-display | In `onMessageReceived` (foreground only) | System handles display |
| **Data message** | Custom handling required | Always in `onMessageReceived` | App handles everything |
| **Combined** | System tray + data | Data in `onMessageReceived` (foreground) | System displays notification, data in intent extras |

**Recommendation**: Use data messages for full control. Notification messages auto-display in background but limit customisation.

### FCM Service Implementation

```kotlin
class MyFirebaseMessagingService : FirebaseMessagingService() {

    override fun onNewToken(token: String) {
        // Send token to your server
        CoroutineScope(Dispatchers.IO).launch {
            ApiService.registerPushToken(token)
        }
    }

    override fun onMessageReceived(message: RemoteMessage) {
        val data = message.data

        when (data["type"]) {
            "chat_message" -> handleChatMessage(data)
            "order_update" -> handleOrderUpdate(data)
            "promotion" -> handlePromotion(data)
            else -> handleGenericNotification(message)
        }
    }

    private fun handleChatMessage(data: Map<String, String>) {
        val notification = NotificationCompat.Builder(this, CHAT_CHANNEL_ID)
            .setSmallIcon(R.drawable.ic_chat)
            .setContentTitle(data["sender_name"])
            .setContentText(data["message"])
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE)
            .setAutoCancel(true)
            .setContentIntent(createChatPendingIntent(data["chat_id"]!!))
            .addAction(createReplyAction(data["chat_id"]!!))
            .build()

        NotificationManagerCompat.from(this).notify(
            data["chat_id"]!!.hashCode(),
            notification,
        )
    }
}
```

### Topics and Conditions

```kotlin
// Subscribe to topics
Firebase.messaging.subscribeToTopic("news")
Firebase.messaging.subscribeToTopic("deals_us")

// Server-side: send to topic
// POST https://fcm.googleapis.com/v1/projects/{project}/messages:send
{
  "message": {
    "topic": "news",
    "data": { "type": "news", "article_id": "123" }
  }
}

// Conditions: combine topics with boolean logic
{
  "message": {
    "condition": "'news' in topics && 'deals_us' in topics",
    "data": { "type": "targeted_deal" }
  }
}
```

---

## Permission Request Patterns

### Strategy Comparison

| Pattern | Description | Opt-in Rate | Best For |
|---------|-------------|-------------|----------|
| **Cold ask** | Request on first launch | 30-40% | Simple apps |
| **Pre-prompt** | Explain value, then system dialog | 50-70% | Most apps |
| **Progressive** | Request after user demonstrates intent | 60-80% | Feature-rich apps |
| **Contextual** | Request when feature needs it | 70-85% | Best practice |

### Pre-Prompt Pattern (iOS)

```swift
class NotificationPermissionManager {
    func requestPermissionWithPrePrompt() async -> Bool {
        // Step 1: Show custom pre-prompt explaining value
        let userAccepted = await showPrePromptUI()

        guard userAccepted else {
            // User declined pre-prompt — do not show system dialog
            // Try again later with different context
            return false
        }

        // Step 2: Show system permission dialog
        let center = UNUserNotificationCenter.current()
        do {
            let granted = try await center.requestAuthorization(
                options: [.alert, .sound, .badge]
            )
            if granted {
                await MainActor.run {
                    UIApplication.shared.registerForRemoteNotifications()
                }
            }
            return granted
        } catch {
            return false
        }
    }
}
```

### Android 13+ Runtime Permission

```kotlin
// Android 13 (API 33) requires POST_NOTIFICATIONS permission
class NotificationPermissionHandler(private val activity: ComponentActivity) {
    private val requestPermissionLauncher = activity.registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        if (isGranted) {
            // Permission granted, register for FCM
            registerForPush()
        } else {
            // Permission denied, show settings prompt later
        }
    }

    fun requestPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            when {
                ContextCompat.checkSelfPermission(
                    activity, Manifest.permission.POST_NOTIFICATIONS
                ) == PackageManager.PERMISSION_GRANTED -> {
                    registerForPush()
                }
                activity.shouldShowRequestPermissionRationale(
                    Manifest.permission.POST_NOTIFICATIONS
                ) -> {
                    // Show explanation UI, then request
                    showRationaleDialog {
                        requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                    }
                }
                else -> {
                    requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
                }
            }
        } else {
            // Pre-Android 13: permission granted at install
            registerForPush()
        }
    }
}
```

---

## Notification Channels (Android 8+)

### Channel Configuration

```kotlin
object NotificationChannels {
    const val CHAT_CHANNEL_ID = "chat_messages"
    const val ORDER_CHANNEL_ID = "order_updates"
    const val PROMO_CHANNEL_ID = "promotions"

    fun createChannels(context: Context) {
        val manager = context.getSystemService(NotificationManager::class.java)

        val channels = listOf(
            NotificationChannel(
                CHAT_CHANNEL_ID,
                "Chat Messages",
                NotificationManager.IMPORTANCE_HIGH,
            ).apply {
                description = "New messages from your conversations"
                enableLights(true)
                enableVibration(true)
                setShowBadge(true)
            },

            NotificationChannel(
                ORDER_CHANNEL_ID,
                "Order Updates",
                NotificationManager.IMPORTANCE_DEFAULT,
            ).apply {
                description = "Updates about your orders"
                enableVibration(true)
            },

            NotificationChannel(
                PROMO_CHANNEL_ID,
                "Promotions",
                NotificationManager.IMPORTANCE_LOW,
            ).apply {
                description = "Deals and special offers"
                setShowBadge(false)
            },
        )

        channels.forEach { manager.createNotificationChannel(it) }
    }
}
```

### Importance Levels

| Level | Behaviour | Use Case |
|-------|-----------|----------|
| IMPORTANCE_HIGH | Heads-up, sound, vibration | Messages, alerts |
| IMPORTANCE_DEFAULT | Sound, status bar | Order updates, reminders |
| IMPORTANCE_LOW | Status bar only, no sound | Promotions, tips |
| IMPORTANCE_MIN | No sound, no status bar | Background info |

---

## Rich Notifications

### iOS: Notification Content Extension

```swift
// Rich notification with image
func sendRichNotification() {
    let content = UNMutableNotificationContent()
    content.title = "New Photo"
    content.body = "Sarah shared a photo with you"
    content.categoryIdentifier = "PHOTO_CATEGORY"

    // Attach image
    if let imageURL = Bundle.main.url(forResource: "photo", withExtension: "jpg"),
       let attachment = try? UNNotificationAttachment(
           identifier: "photo",
           url: imageURL,
           options: [UNNotificationAttachmentOptionsTypeHintKey: UTType.jpeg.identifier]
       ) {
        content.attachments = [attachment]
    }

    let request = UNNotificationRequest(
        identifier: UUID().uuidString,
        content: content,
        trigger: nil
    )
    UNUserNotificationCenter.current().add(request)
}
```

### iOS: Notification Actions

```swift
// Define action categories
func registerNotificationCategories() {
    let replyAction = UNTextInputNotificationAction(
        identifier: "REPLY_ACTION",
        title: "Reply",
        options: [],
        textInputButtonTitle: "Send",
        textInputPlaceholder: "Type your reply..."
    )

    let likeAction = UNNotificationAction(
        identifier: "LIKE_ACTION",
        title: "Like",
        options: []
    )

    let messageCategory = UNNotificationCategory(
        identifier: "MESSAGE_CATEGORY",
        actions: [replyAction, likeAction],
        intentIdentifiers: [],
        options: [.customDismissAction]
    )

    UNUserNotificationCenter.current().setNotificationCategories([messageCategory])
}
```

### Android: Rich Notifications

```kotlin
// Big picture notification
fun showImageNotification(context: Context, imageUrl: String, title: String) {
    val bitmap = Glide.with(context)
        .asBitmap()
        .load(imageUrl)
        .submit()
        .get()

    val notification = NotificationCompat.Builder(context, CHAT_CHANNEL_ID)
        .setSmallIcon(R.drawable.ic_notification)
        .setContentTitle(title)
        .setLargeIcon(bitmap)
        .setStyle(
            NotificationCompat.BigPictureStyle()
                .bigPicture(bitmap)
                .bigLargeIcon(null as Bitmap?)
        )
        .build()

    NotificationManagerCompat.from(context).notify(generateId(), notification)
}

// Conversation-style notification (Android 11+)
fun showConversationNotification(context: Context, messages: List<ChatMessage>) {
    val person = Person.Builder()
        .setName(messages.first().senderName)
        .setIcon(IconCompat.createWithBitmap(senderAvatar))
        .build()

    val style = NotificationCompat.MessagingStyle(person)
        .setConversationTitle("Team Chat")

    messages.forEach { msg ->
        style.addMessage(msg.text, msg.timestamp, person)
    }

    val notification = NotificationCompat.Builder(context, CHAT_CHANNEL_ID)
        .setSmallIcon(R.drawable.ic_chat)
        .setStyle(style)
        .build()

    NotificationManagerCompat.from(context).notify(CHAT_NOTIFICATION_ID, notification)
}
```

---

## Silent / Background Notifications

### iOS: Content-Available

```json
{
  "aps": {
    "content-available": 1
  },
  "sync_type": "new_data",
  "resource_id": "456"
}
```

```swift
// AppDelegate
func application(
    _ application: UIApplication,
    didReceiveRemoteNotification userInfo: [AnyHashable: Any],
    fetchCompletionHandler completionHandler: @escaping (UIBackgroundFetchResult) -> Void
) {
    guard let syncType = userInfo["sync_type"] as? String else {
        completionHandler(.noData)
        return
    }

    Task {
        do {
            switch syncType {
            case "new_data":
                let hasNewData = try await SyncService.shared.syncResource(
                    id: userInfo["resource_id"] as? String ?? ""
                )
                completionHandler(hasNewData ? .newData : .noData)
            default:
                completionHandler(.noData)
            }
        } catch {
            completionHandler(.failed)
        }
    }
}
```

### Android: Data-Only Messages

```kotlin
// Data-only messages are always handled by onMessageReceived
// even when the app is in the background
override fun onMessageReceived(message: RemoteMessage) {
    if (message.data["type"] == "sync") {
        CoroutineScope(Dispatchers.IO).launch {
            SyncService.getInstance().performSync(
                resourceId = message.data["resource_id"] ?: return@launch
            )
        }
    }
}
```

---

## Notification Analytics

### Key Metrics

| Metric | Formula | Target | How to Track |
|--------|---------|--------|-------------|
| **Delivery rate** | Delivered / Sent | > 95% | Server logs + APNs/FCM feedback |
| **Open rate** | Opened / Delivered | 5-15% | Track tap events |
| **Opt-out rate** | Disabled / Total users | < 5%/month | Check permission status periodically |
| **Conversion rate** | Converted / Opened | Varies | Track post-tap actions |
| **Time to open** | Median open - send time | < 1 hour | Timestamp comparison |

### Tracking Implementation

```typescript
// Server-side: track notification lifecycle
interface NotificationEvent {
  notificationId: string;
  userId: string;
  event: 'sent' | 'delivered' | 'opened' | 'dismissed' | 'action_taken';
  timestamp: string;
  metadata: Record<string, string>;
}

// Client-side: report open event
function onNotificationOpened(notification: PushNotification) {
  analytics.track('notification_opened', {
    notification_id: notification.data.notification_id,
    notification_type: notification.data.type,
    time_to_open: Date.now() - notification.sentAt,
    app_state: notification.appState, // 'foreground' | 'background' | 'killed'
  });
}
```

---

## iOS Environment Validation: Xcode vs TestFlight

For iOS push work, the first question is not whether APNs exists in the architecture, but **which APNs environment the current binary should be using**. Treat local Xcode installs and distributed TestFlight / App Store installs as separate proof paths.

### Expected Environment by Build Origin

| Build Origin | Expected APNs Environment | What To Verify |
|-------------|---------------------------|----------------|
| Xcode build installed on a real device | `sandbox` | Newest backend device row shows `push_environment = sandbox` |
| TestFlight or App Store install | `production` | Newest backend device row shows `push_environment = production` |

### Required Validation Loop

1. Install the Xcode debug build on a physical iPhone and open the app once.
2. Check the newest backend device row for the user. It should be active, authorized, and `push_environment = sandbox`.
3. Use a deterministic server-side send path that builds the same payload shape as production. Prefer this over waiting for a cron window or a campaign schedule.
4. Inspect the send result and the device outcome separately. APNs acceptance proves backend delivery; the visible banner / Notification Center card proves the device UX.
5. Archive the iOS app for distribution. Before upload, inspect the archived `.app` and confirm the signed entitlement contains `aps-environment = production`.
6. Install from TestFlight, open the app once, then confirm the newest backend device row flipped to `push_environment = production`.
7. Run the deterministic send again and confirm the successful APNs delivery reports `environment = production`.

### Archive-Time Entitlement Check

Use the archived `.app`, not the checked-in `.entitlements` file, as the source of truth:

```bash
codesign -d --entitlements - "/path/to/CosmicCopilot.app" | grep -A1 aps-environment
```

Expected output for TestFlight / App Store readiness:

```text
aps-environment
production
```

If the archive still prints `development`, stop. A TestFlight build that signs for the wrong environment will register the wrong token class and produce misleading delivery failures against a production backend.

### Backend Routing Defaults

- The backend should route by the stored device environment, not by a single deployment-wide guess.
- A global environment variable such as `APNS_ENVIRONMENT` should remain a production-safe fallback in production deployments.
- Deterministic QA routes should report the delivery environment (`sandbox` vs `production`) and the APNs status / reason so environment mismatches are visible immediately.

### Interpreting Common Results

| Result | Likely Meaning | Action |
|-------|----------------|--------|
| APNs success with `environment = sandbox` on Xcode build | Local debug path works | Continue to TestFlight proof |
| APNs success with `environment = production` on TestFlight build | Distribution path works | Push pipeline is release-ready |
| `BadDeviceToken` on older production rows while the newest sandbox row succeeds | Stale installs or stale tokens | Clean up stale rows later; do not treat as current-device blocker |
| BadDeviceToken on older production rows after a fresh local send | Usually stale installs rather than a current-device blocker | Verify the newest row first, then clean up old rows after release proof is complete |
| No visible banner but APNs success | Delivery path is healthy; presentation is device/UI state | Check foreground behavior, Focus, notification settings, and Notification Center |

## Troubleshooting

### Common Delivery Failures

| Issue | Platform | Cause | Fix |
|-------|----------|-------|-----|
| Token invalid | Both | App uninstalled, token expired | Handle 410 Gone (APNs) / registration error (FCM) |
| Silent notification throttled | iOS | Too many content-available pushes | Limit to 2-3 per hour |
| Background restriction | Android | Battery saver, manufacturer restrictions | Use high-priority for critical messages |
| Notification not shown | Android | Missing channel (Android 8+) | Create channel before sending |
| Permission denied | Both | User disabled notifications | Check permission status, re-prompt contextually |
| Payload too large | Both | > 4KB (APNs) / > 4KB (FCM) | Trim payload, fetch details from server |

### Debugging Tools

| Tool | Platform | Purpose |
|------|----------|---------|
| `Console.app` | macOS | View APNs delivery logs from connected device |
| `xcrun simctl push` | iOS Simulator | Send test push to simulator |
| FCM Diagnostics | Android | Check message delivery in Firebase Console |
| `adb shell dumpsys notification` | Android | View notification state on device |
| Pusher / NWPusher | iOS | Send test APNs payloads |
| Firebase Console | Android | Send test messages |

---

## Cross-Platform: React Native

### Expo Notifications

```typescript
import * as Notifications from 'expo-notifications';
import * as Device from 'expo-device';

// Configure notification handling
Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
  }),
});

// Register for push
async function registerForPush(): Promise<string | null> {
  if (!Device.isDevice) {
    console.warn('Push notifications require a physical device');
    return null;
  }

  const { status: existingStatus } = await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== 'granted') {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== 'granted') return null;

  const token = await Notifications.getExpoPushTokenAsync({
    projectId: 'your-expo-project-id',
  });

  return token.data;
}

// Listen for notifications
useEffect(() => {
  const foregroundSub = Notifications.addNotificationReceivedListener((notification) => {
    // Handle foreground notification
  });

  const responseSub = Notifications.addNotificationResponseReceivedListener((response) => {
    const data = response.notification.request.content.data;
    // Navigate based on notification data
    navigation.navigate(data.screen, data.params);
  });

  return () => {
    foregroundSub.remove();
    responseSub.remove();
  };
}, []);
```

### React Native Firebase

```typescript
import messaging from '@react-native-firebase/messaging';

// Request permission (iOS)
const authStatus = await messaging().requestPermission();
const enabled =
  authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
  authStatus === messaging.AuthorizationStatus.PROVISIONAL;

// Get FCM token
const token = await messaging().getToken();

// Background message handler (must be registered outside of component)
messaging().setBackgroundMessageHandler(async (remoteMessage) => {
  // Handle background data message
  await syncData(remoteMessage.data);
});

// Foreground message handler
useEffect(() => {
  const unsubscribe = messaging().onMessage(async (remoteMessage) => {
    // Show local notification or in-app banner
  });

  return unsubscribe;
}, []);
```

---

## Unified Backend Sender (Web + APNs)

When a backend serves both a web app (web-push/VAPID) and a native iOS app (APNs), extend the existing `sendPushNotification()` to query both device tables rather than creating separate call paths. All existing callers get iOS delivery for free.

```text
sendPushNotification(userId, payload)
  ├── push_subscriptions (web-push / VAPID) → browser
  └── mobile_push_devices (APNs / HTTP2)   → iOS
      └── checks notification_categories JSONB before sending
```

**Key patterns:**
- Store per-device notification preferences as JSONB on the device registration table — avoids joins in cron queries
- Map the web-push `tag` field to `aps.thread-id` (notification grouping in iOS)
- Use `collapse-id` (APNs header) to replace stale notifications — e.g., `daily-{date}` prevents duplicates if a cron re-fires
- `thread-id` groups notifications in Notification Center; `collapse-id` replaces them — they serve different purposes
- Mark invalid tokens (`BadDeviceToken`, `Unregistered`) as `is_active = false` immediately

**APNs library choice (Node.js):**
- `apns2` — lightweight HTTP/2 client, token-based `.p8` auth, actively maintained
- Firebase Admin SDK — adds massive dependency + requires Firebase project setup; only use if already using Firebase
- `@parse/node-apn` — archived/abandoned, do not use

## iOS Badge Management (iOS 16+)

```swift
// Deprecated — do not use
UIApplication.shared.applicationIconBadgeNumber = 0

// Current (iOS 16+) — async throws
try? await UNUserNotificationCenter.current().setBadgeCount(0)
```

Clear badge in the scene-active handler so it resets when the user opens the app.

## Apple Developer Program Prerequisite

APNs authentication keys (`.p8` files) require active enrollment in the Apple Developer Program ($99/year). Without enrollment, you can build all the push notification code but cannot create the key to actually send notifications. Enrollment is usually approved within 24-48 hours.

---

## Anti-Patterns

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Cold-asking for permission on first launch | Low opt-in rate (30-40%) | Use pre-prompt or contextual permission request |
| Sending notification messages instead of data messages | Cannot customise in background | Use data messages for full control |
| Not handling token refresh | Notifications stop working | Listen for `onNewToken` / `didRegisterForRemoteNotificationsWithDeviceToken` |
| Missing notification channels (Android 8+) | Notifications silently dropped | Create channels at app startup |
| Large payloads | Delivery failure | Keep under 4KB, fetch details from server |
| No analytics on delivery/open | Cannot measure effectiveness | Track full notification lifecycle |
| Same priority for all notifications | Important messages buried | Use channels/categories with appropriate priority |
| Using `applicationIconBadgeNumber` (iOS) | Deprecated since iOS 16 | Use `UNUserNotificationCenter.setBadgeCount()` (async throws) |
| Local-only notification preferences | Backend crons can't respect user toggles | Sync preferences to backend on toggle change |
| Separate APNs sender from web-push sender | Duplicated calling code, inconsistent delivery | Unified sender that queries both device tables |

---

## Cross-References

- [deep-linking-guide.md](deep-linking-guide.md) — Deep link handling from notification taps
- [offline-first-architecture.md](offline-first-architecture.md) — Background sync via silent notifications
- [ios-best-practices.md](ios-best-practices.md) — iOS app lifecycle and background tasks
- [android-best-practices.md](android-best-practices.md) — Android services and WorkManager
- [cross-platform-comparison.md](cross-platform-comparison.md) — Push notification SDK comparison
