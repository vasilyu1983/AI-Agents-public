# iOS Surfaces Reference

Baseline: iOS 26 / SwiftUI 6 / Swift 6.2. Senior-engineer decision reference — pick the right API for each surface. Verify availability flags at use-time.

---

## Table of Contents

- [Charts](#charts)
- [Dynamic Island](#dynamic-island)
- [Widgets](#widgets)
- [App Clips](#app-clips)
- [App Intents and Shortcuts](#app-intents-and-shortcuts)
- [Drag and Drop with Transferable](#drag-and-drop-with-transferable)
- [ShareLink vs UIActivityViewController](#sharelink-vs-uiactivityviewcontroller)
- [NavigationSplitView for iPad](#navigationsplitview-for-ipad)
- [Swipe Actions](#swipe-actions)
- [Photo / Document Picker](#photo--document-picker)
- [Camera Surface](#camera-surface)
- [Live Activities](#live-activities)
- [Universal Links + Handoff](#universal-links--handoff)
- [Multitasking Awareness](#multitasking-awareness)

---

## Charts

**Default to Swift Charts (iOS 16+).** It handles bar, line, area, scatter, sector, and rule marks natively with accessibility built in.

| Need | API |
|---|---|
| Bar, line, area, scatter, sector, rule | `Chart { ... }` with typed marks |
| Hit-testing / selection | `ChartProxy` via `.chartOverlay` |
| Accessibility fallback | `.accessibilityRepresentation { }` |
| Radar / custom physics / particle | `Canvas` |
| Pixel-level control in UIKit hierarchy | `UIView` + `CALayer` |

```swift
Chart(data) { item in
    BarMark(x: .value("Day", item.day), y: .value("Count", item.count))
}
.chartOverlay { proxy in
    GeometryReader { geo in
        Rectangle().fill(.clear).contentShape(Rectangle())
            .onTapGesture { location in
                let x: String? = proxy.value(atX: location.x - geo[proxy.plotAreaFrame].origin.x)
                // handle selection
            }
    }
}
```

```swift
// Accessibility for custom chart
Chart { ... }
    .accessibilityRepresentation {
        // Provide a table or list that VoiceOver can read
        List(data) { Text("\($0.day): \($0.count)") }
    }
```

**Canvas** — use only when Swift Charts cannot model the geometry (free-form radar, graph layouts with physics, custom shaders). Canvas has no built-in accessibility; add `.accessibilityElement` siblings manually.

**Custom UIView** — last resort. Justify explicitly. Drawbacks: no SwiftUI layout integration, manual dark mode, no Charts animations.

---

## Dynamic Island

Three display states. Get the stage wrong and the system crops or ignores your content.

### Compact

Two independent slots rendered on either side of the TrueDepth camera.

| Constraint | Value |
|---|---|
| Content padding | 8 pt each side |
| Height | ~36 pt (system-managed) |
| Guiding principle | Single glanceable datum per slot |

```swift
.compactLeading {
    Image(systemName: "heart.fill").foregroundStyle(.red)
}
.compactTrailing {
    Text(state.bpm.formatted()).monospacedDigit()
}
```

**Anti-pattern:** multi-word text in compact. Truncation is silent; the user sees garbage.

### Minimal

Single circular slot. Shown when two Live Activities compete.

- ~28 pt diameter
- One icon or very short number only
- No text labels

### Expanded

Full-width rich layout. Regions: `leading`, `trailing`, `center`, `bottom`.

```swift
.expanded {
    HStack {
        VStack(alignment: .leading) { /* leading */ }
        Spacer()
        VStack(alignment: .trailing) { /* trailing */ }
    }
    VStack { /* bottom */ }
}
```

**State transitions** — the system drives expansion on long-press. Never trigger programmatic expansion. Use `ActivityKit` push updates to change content state; transitions animate automatically.

**ActivityKit lifecycle:** `Activity.request(attributes:contentState:)` → update via `activity.update(using:)` → end with `activity.end(using:dismissalPolicy:)`. Always call `.end()` or the Island persists for up to 8 hours.

**Anti-patterns:**
- Animating expansion on every content update (system rate-limits; excess calls are dropped)
- Putting navigation controls in expanded (users cannot tap into your app from the Island directly — long-press only opens your app)

---

## Widgets

### Size Families

| Family | Platforms |
|---|---|
| `.systemSmall` | iPhone, iPad |
| `.systemMedium` | iPhone, iPad |
| `.systemLarge` | iPhone, iPad |
| `.systemExtraLarge` | iPad only |
| `.accessoryCircular` | Lock Screen, Watch |
| `.accessoryRectangular` | Lock Screen, Watch |
| `.accessoryInline` | Lock Screen (single line) |

Declare supported families in `Widget.body` via `.supportedFamilies([...])`. Omit unsupported families — don't render and return `.redacted`.

### Timeline Lifecycle

```
placeholder() → snapshot() → getTimeline(entries:)
```

- `placeholder`: static, no network. Shown while widget loads. Use `.redacted(reason: .placeholder)`.
- `snapshot`: single-entry fast render for widget gallery.
- `getTimeline`: return `Timeline(entries:policy:)`. Policy: `.atEnd`, `.after(date)`, or `.never`.

### Interactive Widgets (iOS 17+)

Use `AppIntent` conformance on `Button` and `Toggle`. The intent runs in the widget extension process — no app launch.

```swift
struct ToggleFavoriteIntent: AppIntent {
    static var title: LocalizedStringResource = "Toggle Favorite"
    @Parameter(title: "Item ID") var itemID: String
    func perform() async throws -> some IntentResult { ... }
}

// In widget view:
Button(intent: ToggleFavoriteIntent(itemID: item.id)) {
    Label("Favorite", systemImage: "star")
}
```

**`.containerBackground` is required** (iOS 17+). Wrap widget content:

```swift
.containerBackground(for: .widget) { Color.blue }
```

Omitting it causes a build warning and incorrect rendering in Smart Stacks.

### Smart Stack / Glancability

- Add `.widgetRelevances` returning `WidgetRelevance` entries to surface in Smart Stack at the right time.
- Every widget must be readable in ~1 second. If the user needs to "read" it, it's too dense.
- Avoid custom fonts below 13 pt in widgets — Dynamic Type does not apply.

---

## App Clips

**Hard ceiling: 8 MB** compressed binary. Validate with `du -sh *.app` in the archive. Exceeding 8 MB rejects at submission.

### Entry Points

| Invocation | Required setup |
|---|---|
| URL (Safari banner, Messages) | Associated domain `appclips:` in entitlement |
| NFC tag | App Clip Code or standard NFC tag with URL |
| App Clip Code (QR hybrid) | Physical or digital; registered in App Store Connect |
| Location-based (Maps, Siri) | `NSAppClip` `NSAppClipRequestEphemeralUserNotification` key |

### App Clip Card

Configured in App Store Connect per invocation URL prefix. Title, subtitle, image, and action verb are mandatory. Card loads before the clip; a poor card kills conversion before code runs.

### Upgrade Prompt

Present `SKOverlay(configuration: .appClip(position: .bottom))` after the user completes the core action. Prompting before the action is gating — App Review will reject.

### Anti-patterns

- Sign-up / log-in wall on first launch (violates HIG and App Review guideline 2.5.10)
- Using App Clip as a standalone app without a full-app counterpart in the App Store
- Importing large frameworks (SwiftUI renders fast; avoid Alamofire, Firebase, etc.)

---

## App Intents and Shortcuts

### Hierarchy

```
AppShortcut → AppIntent → performs action → returns IntentResult
```

### AppShortcut Phrases

```swift
struct MyShortcuts: AppShortcutsProvider {
    static var appShortcuts: [AppShortcut] {
        AppShortcut(
            intent: LogWorkoutIntent(),
            phrases: ["Log a workout in \(.applicationName)", "Start workout with \(.applicationName)"],
            shortTitle: "Log Workout",
            systemImageName: "figure.run"
        )
    }
}
```

Phrases must include `\(.applicationName)`. No more than 10 shortcuts per app.

### Intent Donation

Donate after the user completes a meaningful action, not on app launch.

```swift
let intent = ViewRecipeIntent()
intent.recipe = recipe
try await IntentDonationManager.shared.donate(intent: intent)
```

Donations feed Siri suggestions and Spotlight. Over-donating (e.g., every background refresh) pollutes suggestions.

### Parameter Prompts

Declare `@Parameter` with `requestValueDialog` for Siri voice prompting. For complex disambiguation, implement `DynamicOptionsProvider`.

### Spotlight Semantic Search

Implement `IndexedEntity` on your model type + `CSSearchableItem` attribution. Intents with matching entity parameters surface in Spotlight natively from iOS 16+.

### AppIntent vs Custom URL Scheme

| Criterion | AppIntent | URL Scheme |
|---|---|---|
| Siri / Shortcuts integration | Yes | No |
| Spotlight suggestion | Yes | No |
| Widget interactivity | Yes | No |
| Third-party app linking | Limited | Yes |
| No Shortcuts app required | Yes | Yes |

Default to `AppIntent`. Use URL schemes only for cross-app deep linking where you do not control the calling app.

---

## Drag and Drop with Transferable

### SwiftUI-native (iOS 16+)

```swift
// Draggable
Text(item.title)
    .draggable(item) {
        // Optional custom drag preview
        RoundedRectangle(cornerRadius: 8).fill(.blue)
            .frame(width: 100, height: 44)
            .overlay(Text(item.title).foregroundStyle(.white))
    }

// Drop destination
List { ... }
    .dropDestination(for: MyItem.self) { items, location in
        handle(items)
        return true
    }
```

`MyItem` must conform to `Transferable`. Simplest path: `Codable` bridge via `CodableRepresentation`.

```swift
struct MyItem: Transferable {
    static var transferRepresentation: some TransferRepresentation {
        CodableRepresentation(contentType: .myItem)
    }
}
```

### Multi-Item

`dropDestination(for:)` receives `[T]` — handle the array. For heterogeneous types use `ItemProvider` directly.

### UIKit Interop

For `UICollectionView`/`UITableView` drag: implement `UICollectionViewDragDelegate` + `UICollectionViewDropDelegate`. Bridge to Transferable via `NSItemProvider(object:)` where the object conforms to `NSItemProviderWriting`. Direct bridge: `NSItemProvider.loadTransferable(type:completionHandler:)`.

### Drag Preview Customization

The trailing closure in `.draggable(_:preview:)` accepts any `View`. Keep preview ≤ the dragged item's visual size; oversized previews feel broken.

---

## ShareLink vs UIActivityViewController

**Default: `ShareLink`.** Handles Quick Look preview, AirDrop, Messages, Mail, Copy, Save to Files — all system standard.

```swift
ShareLink(item: url, subject: Text("Check this out"), message: Text("Shared via MyApp"))

ShareLink(item: photo, preview: SharePreview("Sunset", image: photo))
```

**Use `UIActivityViewController` only when:**
- You need `excludedActivityTypes` to suppress specific share targets
- You need custom `UIActivity` subclasses
- You need to set `subject` on email in a way ShareLink's `subject:` doesn't expose
- You need `completionWithItemsHandler` for post-share analytics

```swift
// UIKit bridge when needed
let vc = UIActivityViewController(activityItems: [url], applicationActivities: nil)
vc.excludedActivityTypes = [.postToFacebook]
present(vc, animated: true)
```

`ShareLink` cannot set `excludedActivityTypes`. If suppressing targets matters, use `UIActivityViewController`.

---

## NavigationSplitView for iPad

### Column Configurations

```swift
// Two-column
NavigationSplitView {
    SidebarView()
} detail: {
    DetailView()
}

// Three-column
NavigationSplitView {
    SidebarView()
} content: {
    ContentListView()
} detail: {
    DetailView()
}
```

### Display Style

| Style | Behavior |
|---|---|
| `.automatic` | System decides per device / size class |
| `.balanced` | Sidebar and detail split evenly |
| `.prominentDetail` | Detail fills width; sidebar overlays |

```swift
NavigationSplitView(columnVisibility: $columnVisibility) { ... }
    .navigationSplitViewStyle(.balanced)
```

### Compact Adaptation

`NavigationSplitView` automatically collapses to `NavigationStack` in compact width. You do not need a separate iPhone code path. **Test this.** The collapse is structural — `@State` in the split view is reset.

### `columnVisibility` Binding

```swift
@State private var columnVisibility = NavigationSplitViewVisibility.automatic

Button("Toggle Sidebar") {
    columnVisibility = columnVisibility == .detailOnly ? .all : .detailOnly
}
```

### Anti-patterns

- Using `NavigationSplitView` on iPhone intentionally (it collapses anyway; design for compact first)
- Not binding `columnVisibility` (sidebar toggle in Stage Manager becomes uncontrollable)
- Putting modal flows inside the detail column (use `.sheet` from the root scene instead)

---

## Swipe Actions

```swift
List(items) { item in
    ItemRow(item: item)
        .swipeActions(edge: .trailing, allowsFullSwipe: true) {
            Button(role: .destructive) { delete(item) } label: {
                Label("Delete", systemImage: "trash")
            }
        }
        .swipeActions(edge: .leading) {
            Button { archive(item) } label: {
                Label("Archive", systemImage: "archivebox")
            }
            .tint(.orange)
        }
}
```

### Rules

- `role: .destructive` auto-applies red background — do not override `.tint` on destructive actions
- Destructive actions belong on the **trailing** edge (standard iOS convention; breaking it confuses users)
- Non-destructive actions (archive, flag, pin) belong on **leading**
- `allowsFullSwipe: true` only on single-action trailing with destructive role — full-swipe on non-destructive surprises users
- Label text: ≤ 8 characters or icon-only. The system truncates silently at small widths.
- Maximum practical actions per edge: 3. Beyond that the system clips them.

---

## Photo / Document Picker

### PhotosPicker (iOS 16+)

```swift
@State private var selectedItems: [PhotosPickerItem] = []

PhotosPicker(
    selection: $selectedItems,
    maxSelectionCount: 10,
    matching: .images
) {
    Label("Select Photos", systemImage: "photo.on.rectangle")
}
.onChange(of: selectedItems) { _, items in
    Task {
        for item in items {
            if let data = try? await item.loadTransferable(type: Data.self) {
                // handle data
            }
        }
    }
}
```

**Inline picker** — embed `PhotosPicker` in a form cell. For a full-screen sheet, present normally. Both use the same API.

Filter options: `.images`, `.videos`, `.livePhotos`, `.screenshots`, `.depthEffectPhotos`, `.any(of: [...])`.

### `.fileImporter` for Documents

```swift
.fileImporter(
    isPresented: $showingImporter,
    allowedContentTypes: [.pdf, .plainText],
    allowsMultipleSelection: false
) { result in
    if case .success(let urls) = result {
        let url = urls[0]
        guard url.startAccessingSecurityScopedResource() else { return }
        defer { url.stopAccessingSecurityScopedResource() }
        // read file
    }
}
```

Always call `startAccessingSecurityScopedResource()` / `stopAccessingSecurityScopedResource()` for `.fileImporter` results. Omitting it causes silent permission failures.

---

## Camera Surface

### AVCaptureSession Lifecycle

```swift
// Pre-warm on app open, not on camera button tap
Task.detached(priority: .userInitiated) {
    session.startRunning() // blocks; run off main thread
}

// Background transition
NotificationCenter.default.addObserver(
    forName: UIApplication.didEnterBackgroundNotification
) { _ in session.stopRunning() }
```

Pre-warming eliminates the 300–800 ms shutter lag users notice.

### Focus / Exposure POI

```swift
try device.lockForConfiguration()
if device.isFocusPointOfInterestSupported {
    device.focusPointOfInterest = pointInCaptureDeviceCoordinates
    device.focusMode = .autoFocus
}
device.unlockForConfiguration()
```

Convert tap point: `AVCaptureVideoPreviewLayer.captureDevicePointConverted(fromLayerPoint:)`.

### Format Selection

| Format | When |
|---|---|
| HEIF (`.heic`) | Default for still photos; smallest file, HDR |
| RAW (`AVCapturePhotoOutput.isRAWCaptureSupported`) | Pro editing apps only; large files |
| Slow-motion | `AVCaptureDevice.Format` with high frame rate (120/240 fps) |
| Multi-cam | `AVCaptureMultiCamSession` (A13+); check `isMultiCamSupported` first |

### SwiftUI Bridge

```swift
struct CameraPreview: UIViewRepresentable {
    let session: AVCaptureSession
    func makeUIView(context: Context) -> PreviewView { PreviewView(session: session) }
    func updateUIView(_ uiView: PreviewView, context: Context) { }
}

final class PreviewView: UIView {
    override class var layerClass: AnyClass { AVCaptureVideoPreviewLayer.self }
    var previewLayer: AVCaptureVideoPreviewLayer { layer as! AVCaptureVideoPreviewLayer }
    init(session: AVCaptureSession) {
        super.init(frame: .zero)
        previewLayer.session = session
        previewLayer.videoGravity = .resizeAspectFill
    }
    required init?(coder: NSCoder) { fatalError() }
}
```

---

## Live Activities

### ActivityAttributes

```swift
struct DeliveryAttributes: ActivityAttributes {
    struct ContentState: Codable, Hashable {
        var status: String
        var eta: Date
    }
    var orderID: String // static, set once at start
}
```

`ActivityAttributes` properties = static (set at start, never change). `ContentState` = dynamic (updated frequently).

### Starting and Updating

```swift
let activity = try Activity.request(
    attributes: DeliveryAttributes(orderID: "123"),
    contentState: DeliveryAttributes.ContentState(status: "Preparing", eta: .now.addingTimeInterval(1800)),
    pushType: .token // or nil for local-only
)

// Local update
await activity.update(using: newContentState)

// End
await activity.end(using: finalState, dismissalPolicy: .after(.now.addingTimeInterval(60)))
```

### ActivityKit Budget

The system rate-limits updates. As of iOS 16.2+, budget is ~15 updates / hour for local pushes. Push token updates bypass this but cost APNs bandwidth. Use push tokens for real-time (delivery, live scores); use local updates for low-frequency (step count, timer).

### Anti-patterns

- Using Live Activities for static notifications (use `UNUserNotificationCenter` instead)
- Forgetting `.end()` — activity persists 4–8 hours, shown to the user as stale data
- Updating `ActivityAttributes` static properties — impossible after start; redesign your model
- Not handling `Activity.activities` on app launch to reconnect to ongoing activities

---

## Universal Links + Handoff

### Universal Links

**`apple-app-site-association`** must be served at `https://yourdomain.com/.well-known/apple-app-site-association` with `Content-Type: application/json`, no redirect.

```json
{
  "applinks": {
    "details": [{
      "appIDs": ["TEAMID.com.example.app"],
      "components": [{ "/": "/order/*", "comment": "Order deep links" }]
    }]
  }
}
```

App-side:

```swift
.onOpenURL { url in
    router.handle(url)
}
```

**Deep link routing pattern:** define a `Router` that parses `URL` → `Destination` enum, then drive navigation state. Never call `NavigationPath.append` from `SceneDelegate` directly — route through a single coordinator.

### Handoff

```swift
// Advertising activity
let activity = NSUserActivity(activityType: "com.example.viewRecipe")
activity.title = recipe.title
activity.userInfo = ["recipeID": recipe.id]
activity.isEligibleForHandoff = true
activity.becomeCurrent()

// Continuing on another device
func application(_ application: UIApplication,
                 continue userActivity: NSUserActivity,
                 restorationHandler: @escaping ([UIUserActivityRestoring]?) -> Void) -> Bool {
    guard let id = userActivity.userInfo?["recipeID"] as? String else { return false }
    router.navigateTo(recipeID: id)
    return true
}
```

Call `activity.invalidate()` when the view disappears. Multiple simultaneous `becomeCurrent()` calls replace each other — only one activity is active per app.

---

## Multitasking Awareness

### Contexts

| Mode | Width class | Notes |
|---|---|---|
| Full screen | Regular | Standard |
| Slide Over | Compact | Floating panel; your app is in background briefly before Slide Over |
| Split View | Regular (shrunk) or Compact | Two apps side by side |
| Stage Manager | Regular (any size) | Free-form window; can be very narrow |

**Never assume full-screen.** Test at every Split View ratio (25/75, 50/50, 75/25).

### `.scenePhase`

```swift
@Environment(\.scenePhase) private var scenePhase

.onChange(of: scenePhase) { _, phase in
    switch phase {
    case .active: resumeWork()
    case .background: persistState()
    case .inactive: pauseAnimations()
    @unknown default: break
    }
}
```

### Multiple Windows

Declare additional scene types in `Info.plist` → `UIApplicationSceneManifest` → `UISceneConfigurations`. Use `@SceneStorage` for per-window state (not `@AppStorage`).

```swift
@SceneStorage("selectedTabIndex") private var selectedTab = 0
```

`@AppStorage` is global; `@SceneStorage` is per-window — always use `@SceneStorage` for navigation state in multi-window apps.

### Stage Manager

- On iPadOS 16+, windows can be any size. Layouts that only work at iPad full-screen will break.
- Use adaptive layout: `HorizontalSizeClass` + `GeometryReader` fallbacks, not hardcoded widths.
- `UIWindowScene.activationConditions` lets you specify preferred window size on open.

### Anti-patterns

- Hardcoding `UIScreen.main.bounds` (deprecated in iOS 16; use `GeometryReader` or `UIWindowScene.coordinateSpace`)
- Not implementing `UISceneConfiguration` for multi-window (Document-based apps must support this)
- Using `UIApplication.shared.windows` (deprecated; use `UIApplication.shared.connectedScenes`)
