# Push Notification Implementation Guide

Complete guide to push notification implementation across iOS (APNs) and Android (FCM). Covers architecture, permission patterns, notification channels, rich notifications, silent notifications, analytics, troubleshooting, and cross-platform patterns.

---

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

---

## Cross-References

- [deep-linking-guide.md](deep-linking-guide.md) — Deep link handling from notification taps
- [offline-first-architecture.md](offline-first-architecture.md) — Background sync via silent notifications
- [ios-best-practices.md](ios-best-practices.md) — iOS app lifecycle and background tasks
- [android-best-practices.md](android-best-practices.md) — Android services and WorkManager
- [cross-platform-comparison.md](cross-platform-comparison.md) — Push notification SDK comparison
