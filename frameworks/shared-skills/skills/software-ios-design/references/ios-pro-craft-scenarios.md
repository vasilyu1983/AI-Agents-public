# iOS Pro-Craft Scenarios

Audience: senior iOS engineer/designer shipping an Apple Design Award-class consumer app. Each scenario gives the concrete details — APIs, states, choreography — needed to ship at the level of Things, Halide, Apollo, Overcast, and Mela.

---

## Table of Contents

- [1. Onboarding](#1-onboarding)
- [2. IAP / Subscription Paywall](#2-iap--subscription-paywall)
- [3. Settings Hierarchy](#3-settings-hierarchy)
- [4. Search](#4-search)
- [5. Photo Viewer](#5-photo-viewer)
- [6. Media Player](#6-media-player)
- [7. Focused-Input App](#7-focused-input-app)
- [8. Daily-Habit App](#8-daily-habit-app)
- [9. Camera UI](#9-camera-ui)
- [10. Chart-Heavy Surface](#10-chart-heavy-surface)
- [11. Inbox / List-Based Reader](#11-inbox--list-based-reader)
- [12. App Intents / Shortcuts Donation](#12-app-intents--shortcuts-donation)

---

## 1. Onboarding

**Goal:** Move the user from cold launch to first meaningful success in under 90 seconds.

**Critical first impression:** The first screen must show the app's value, not a login wall. Open with a full-bleed sample-data state — real-looking content, not lorem ipsum. The CTA is "Get Started", not "Sign Up".

**Required states + flow:**
1. Splash → sample-populated home (skip auth entirely on first render)
2. "Continue with Apple" primary CTA, "Continue with Email" secondary text button, "Explore first" ghost button
3. Permission requests deferred: location only when a location-dependent feature is first tapped; push only after the user completes one success action; photo library only when upload is triggered
4. First-success celebration (confetti, scale pulse, haptic chord) before any paywall
5. "Skip" always visible — never hide it; track skip→conversion rate

**APIs:**
- `ASAuthorizationAppleIDProvider` + `ASAuthorizationController` for Sign in with Apple
- Store credential state in `ASAuthorizationAppleIDProvider.getCredentialState(forUserID:)` on every cold launch
- `UNUserNotificationCenter.requestAuthorization(options:)` deferred to post-success moment
- `CLLocationManager.requestWhenInUseAuthorization()` gated behind feature touch
- `PHPhotoLibrary.requestAuthorization(for:)` gated behind upload action
- `UIViewPropertyAnimator` with `.spring(duration:bounce:)` for celebration; `UIImpactFeedbackGenerator(style: .medium)` + `UINotificationFeedbackGenerator` combo for haptic chord

**Haptic + motion choreography:**
- Apple button tap: `.selection` feedback
- Account created / first success: `.notificationOccurred(.success)` at 0 ms, scale 1.0→1.12→1.0 over 0.4 s spring, confetti emitter at 100 ms
- Skip: no haptic — treat it as a ghost action

**Accessibility:**
- All onboarding screens must have `accessibilityViewIsModal = true` on the presented sheet
- "Continue with Apple" button: `accessibilityLabel = "Sign in with Apple"`
- Celebration animation: wrap in `withAnimation(.none)` when `UIAccessibility.isReduceMotionEnabled`; still deliver haptic

**Anti-patterns:**
- Showing a paywall before the user has experienced any value
- Requesting all permissions upfront in a permission parade
- Making "Skip" tiny or grey to discourage tapping
- Storing the Apple user identifier only in UserDefaults (use Keychain)

**Elite reference:** Things 3 (deferred push, immediate sample data); Mela (zero-friction first recipe add)

---

## 2. IAP / Subscription Paywall

**Goal:** Convert with transparency — no dark patterns, no App Store rejection.

**Critical first impression:** Show a value-loaded preview of what the user is about to unlock before showing a price. Paywalls that open cold on price (no feature preview, no value framing) measurably underperform value-first paywalls in industry conversion benchmarks — treat "cold-price loses meaningfully more subscribers" as the durable direction, not a specific percentage; the exact lift varies by category, price point, and audience, so validate with your own A/B data rather than citing a fixed figure.

**Required states + flow:**
1. Feature preview state (blur overlay on locked content, or a "try it" demo path)
2. Product loading state — spinner replaced with skeleton, never an empty price button
3. Loaded: show plan options (annual highlighted, monthly secondary), free-trial pill, price/period
4. "Restore Purchases" always tappable and clearly visible (App Store rules require this)
5. Family Sharing badge when `product.isFamilyShareable`
6. Purchase in-flight: button shows `ProgressView`, disabled; background dim
7. Purchase success: dismiss + trigger same first-success celebration as onboarding
8. Error: inline error message, retry CTA — never silent failure
9. Downgrade/cancel surface: deep-link to `UIApplication.shared.open(URL(string: "https://apps.apple.com/account/subscriptions")!)`

**APIs:**
- `StoreKit.Product.products(for:)` async — always await before showing price; never hard-code prices
- `StoreKit.Transaction.currentEntitlements` for entitlement check on every app foreground
- `Product.SubscriptionInfo.renewalInfo` for expiry and cancellation state
- `Product.SubscriptionOffer` for introductory / promotional offer display
- `AppStore.sync()` for restore — wrap in `do/catch`, surface error if `StoreKitError.userCancelled`
- `SKAdNetwork` / `AdAttributionKit` if running paid UA (register conversions at purchase)

**Haptic + motion choreography:**
- Plan selection: `.selection` feedback
- Successful purchase: `.notificationOccurred(.success)` + scale animation on checkmark
- Failed purchase: `.notificationOccurred(.error)` + shake on price button (CGAffineTransform x-translation)

**Accessibility:**
- `accessibilityLabel` on price buttons: "Annual plan, $29.99 per year, three-day free trial"
- Don't rely on colour alone to differentiate recommended plan — add a "Best Value" text badge
- Restore button: minimum 44 pt touch target

**Anti-patterns:**
- Hard-coding price strings (App Store rejection risk when prices change)
- "X" close button smaller than 44 pt or absent
- Free trial language that hides when billing starts — must state "then $X/year"
- Requesting a review immediately after a successful purchase (against guidelines)
- Showing the paywall on every cold launch after a user has already dismissed it

**Elite reference:** Cardpointers (clear plan differentiation, family sharing badge); Sofa (value-first preview)

---

## 3. Settings Hierarchy

**Goal:** Users find what they need in under three taps; power settings never clutter the primary flow.

**Critical first impression:** Settings should feel like a first-party Apple app. InsetGrouped list, system font, system colors, no custom chrome.

**Required states + flow:**
1. Top-level: Account, Appearance, Notifications, Data & Privacy, then app-specific sections
2. Destructive zone (Delete Account, Clear Cache, Sign Out) at the very bottom, red tint
3. Search bar at top with `.searchable(text:placement:.navigationBarDrawer)` — searches setting labels + descriptions
4. "About" at bottom: version, build, acknowledgements (open source licenses via Settings.bundle or custom view)
5. Inline toggles save immediately — no "Save" button; form-style inputs (name, email) use "Done" on the keyboard toolbar

**APIs:**
- `List { } .listStyle(.insetGrouped)` — default for Settings
- `.searchable(text: $query, placement: .navigationBarDrawer(displayMode: .always))`
- `NavigationStack(path: $path)` with typed `NavigationPath` for deep-link into a specific setting (e.g. from an onboarding prompt)
- `@AppStorage` for simple toggles; `@EnvironmentObject` or `@Observable` model for complex state
- `Label("Delete Account", systemImage: "trash").foregroundStyle(.red)` for destructive row
- `confirmationDialog` before any irreversible destructive action
- `Link` + `UIApplication.shared.open` for external URLs (privacy policy, terms)

**Haptic + motion choreography:**
- Toggle change: `.selection` feedback (UIKit: `UISelectionFeedbackGenerator`)
- Destructive confirmation: `.warning` medium impact before presenting dialog

**Accessibility:**
- Every section has a `Section { } header: { Text("Section Title") }` — VoiceOver announces section boundaries
- Destructive rows: `accessibilityHint = "Double-tap to begin account deletion"`
- Dynamic Type: all labels scale; test at Accessibility XL

**Anti-patterns:**
- "Save" button for toggles — instant persistence is the system convention
- Putting destructive actions in the middle of the list
- Custom table view cells that break system tint and Dynamic Type
- Deeply nested settings (more than 3 levels)

**Elite reference:** Overcast (flat, discoverable settings); Things 3 (sectioned by frequency, clean destructive zone)

---

## 4. Search

**Goal:** Results appear before the user finishes typing; empty states are never dead ends.

**Critical first impression:** The search field must be reachable within one tap from any primary screen. Keyboard appears immediately on focus.

**Required states + flow:**
1. Inactive: search bar in navigation bar (collapsed or visible)
2. Active / empty query: recent searches list + suggested searches
3. Active / typing: debounced results (150 ms), skeleton rows while loading
4. Active / results: highlighted matches in titles/subtitles
5. Active / no results: illustration + copy + actionable suggestion ("Try 'pasta'" or "Add a new item")
6. Scopes: segmented control for entity type (e.g. Recipes / Ingredients / Tags)

**APIs:**
- `.searchable(text: $query, tokens: $tokens, placement: .navigationBarDrawer, prompt: "Search recipes")` (iOS 16+)
- `.searchScopes($scope) { ForEach(Scope.allCases) { Text($0.label) } }`
- `.onSubmit(of: .search) { commitSearch() }`
- Debounce: `$query.debounce(for: .milliseconds(150), scheduler: RunLoop.main)` via Combine, or `Task { try await Task.sleep(for: .milliseconds(150)) }` with cancellation in `.task(id: query)`
- Recent searches: `UserDefaults` array, capped at 8, displayed with `Label` + clock symbol
- Result highlighting: `AttributedString` with `AttributeContainer` setting `.foregroundColor` and `.font` on matched ranges; use `Range` search on `query.localizedLowercase`
- No-results illustration: SF Symbol `magnifyingglass` with `imageScale(.large)` + secondary text

**Haptic + motion choreography:**
- Scope switch: `.selection` feedback
- Result tap: standard list selection (no extra haptic needed)
- Clearing search: `.selection` feedback on the × button

**Accessibility:**
- `accessibilityLabel` on highlighted text: include full string, not fragmented pieces
- VoiceOver announcement on result count change: `UIAccessibility.post(notification: .announcement, argument: "\(results.count) results")`
- Minimum row height 44 pt even for dense lists

**Anti-patterns:**
- Searching only on exact match — always use `localizedCaseInsensitiveContains` or `NaturalLanguage` tokenization
- Clearing recents automatically on every app launch
- A no-results state with only "No results" and nothing actionable
- Search that fires on every keystroke without debounce (burns battery, hammers API)

**Elite reference:** Apollo (instant results, scope tabs); Anybox (recent + suggested searches, rich highlighting)

---

## 5. Photo Viewer

**Goal:** Fluid, gallery-class browsing with delightful detail reveals.

**Critical first impression:** The hero transition from grid to full-screen must be seamless — matchedGeometryEffect or a custom UIKit hero. No flash, no jump.

**Required states + flow:**
1. Grid → detail via `matchedGeometryEffect(id: photo.id, in: namespace)` + `.navigationTransition(.zoom(sourceID: photo.id, in: namespace))` (iOS 18+)
2. Full-screen: pinch-to-zoom, double-tap to toggle fit/fill, swipe horizontally to navigate
3. Info overlay (caption, metadata, location) shown initially, hidden on single tap, toggle on tap
4. Share sheet: `ShareLink(item: image, preview: SharePreview(photo.title, image: image))`
5. Delete: `confirmationDialog` with `.destructive` button; animate removal from grid
6. Live Photo: `PHLivePhotoView` or `LivePhotoView` (PhotosUI), long-press to play

**APIs:**
- `NavigationTransition.zoom` (iOS 18) or `matchedGeometryEffect` fallback for iOS 17
- `MagnificationGesture` + `DragGesture` composed with `.simultaneously` for pinch+pan
- Double-tap reset: `TapGesture(count: 2).onEnded { withAnimation(.spring) { scale = 1; offset = .zero } }`
- `TabView(selection:) { }.tabViewStyle(.page(indexDisplayMode: .never))` for horizontal swipe between photos
- `PhotosPickerItem` / `PHImageManager` for loading full-resolution async
- `confirmationDialog(isPresented:) { Button("Delete Photo", role: .destructive) { } }`
- Live Photo: `PhotosUI.LivePhotoView` (SwiftUI, iOS 18) or `PHLivePhotoView` wrapped in `UIViewRepresentable`

**Haptic + motion choreography:**
- Reach zoom limits (min/max): `.impactOccurred(intensity: 0.4)` rubber-band bounce
- Delete confirm: `.notificationOccurred(.warning)`
- Swipe page turn: no haptic (matches Photos.app)

**Accessibility:**
- `accessibilityLabel` on each photo: alt-text or "Photo taken [date]"
- Pinch gestures: provide "Zoom In" / "Zoom Out" `accessibilityAction` alternatives
- Info overlay: ensure it's a separate `accessibilityElement` with correct label

**Anti-patterns:**
- Loading full-resolution on grid (always use thumbnails in grid, full-res on demand)
- No confirmation before delete
- Blocking the main thread during image decode — use `UIImage(data:)` in a `Task` on a background actor
- Hero transition that cross-fades instead of zooming (breaks spatial model)

**Elite reference:** Halide (buttery zoom, info overlay); native Photos.app hero transition

---

## 6. Media Player

**Goal:** Now-playing experience that rivals Overcast and Apple Music — lock screen, Dynamic Island, widget, queue.

**Critical first impression:** The player must respond to scrub within one frame. Latency on the scrub bar is the most common craft failure in media apps.

**Required states + flow:**
1. Mini-player bar → expanded player sheet (interactive dismiss, not modal)
2. Scrub bar with live position update, long-press for fine-scrub mode
3. AirPlay / Bluetooth route picker
4. Lock screen Now Playing (auto via AVAudioSession + MPNowPlayingInfoCenter)
5. Now Playing widget: `ActivityKit` + `WidgetKit` complication
6. Dynamic Island: compact (playing indicator), expanded (artwork + progress bar)
7. Sleep timer: `.timer` countdown in Dynamic Island expanded view
8. Queue: reorderable `List` with `.onMove`

**APIs:**
- `AVAudioSession.sharedInstance().setCategory(.playback, mode: .default)` — call before first play
- `MPNowPlayingInfoCenter.default().nowPlayingInfo` — update on every position change and track change
- `MPRemoteCommandCenter` for lock-screen controls (play, pause, skip, seek)
- `AVRoutePickerView` wrapped in `UIViewRepresentable` for AirPlay button
- `ActivityKit.Activity<PlayerAttributes>.request` for Live Activity; update via `Activity.update`
- Dynamic Island: `DynamicIsland { DynamicIslandExpandedRegion(.leading) { } } compactLeading: { } compactTrailing: { } minimal: { }`
- Scrub bar: `Slider(value: $position, in: 0...duration, onEditingChanged: { scrubbing = $0 })` with `let generator = UISelectionFeedbackGenerator()` — call `prepare()` on touch down, `selectionChanged()` at detent intervals

**Haptic + motion choreography:**
- Scrub detents (every 15 s): `.selectionChanged()` on `UISelectionFeedbackGenerator`
- Play/pause toggle: `.impactOccurred(style: .light)`
- Track skip: `.impactOccurred(style: .medium)` + artwork slide animation
- Sleep timer end: `.notificationOccurred(.success)`

**Accessibility:**
- Scrub slider: `accessibilityLabel = "Playback position"`, `accessibilityValue = "\(formattedPosition) of \(formattedDuration)"`
- Route picker: `accessibilityLabel = "Audio output"`
- Queue reorder: `accessibilityAction(named: "Move up") { }` / `"Move down"`

**Anti-patterns:**
- Not calling `MPNowPlayingInfoCenter` update on every seek — lock screen position drifts
- Blocking audio with `AVAudioSession` not active before `AVPlayer.play()`
- Custom scrub implementation that ignores `UIAccessibility.isReduceMotionEnabled`
- Updating Dynamic Island on every position tick — batch updates to every 1 s

**Elite reference:** Overcast (scrub haptics, chapter markers); Castro (Dynamic Island Live Activity)

---

## 7. Focused-Input App

**Goal:** Things-level composer — keyboard-first, inline pickers, zero friction to add a task.

**Critical first impression:** The keyboard must appear within one frame of tapping the compose button. Any delay breaks the "quick capture" promise.

**Required states + flow:**
1. Quick-entry bar always visible at bottom (floating above keyboard)
2. Tap to compose: `@FocusState` immediately sets focus to text field
3. Inline pickers: due date (calendar popover via `.popover`), tags (Menu), priority (segmented)
4. Return adds and resets — "Return to add" mode toggled in settings
5. Swipe-to-complete on list row: custom `swipeActions` with checkmark, `.full` threshold
6. Drag-to-reorder: `.onMove(perform:)` in `List { } .editMode(.active)`
7. Empty state: aspirational copy ("What needs doing today?"), not a blank canvas

**APIs:**
- `@FocusState var composerFocused: Bool` — set to `true` in `.onAppear` and on compose button tap
- `TextField("Add task…", text: $title, axis: .vertical)` for multiline with dynamic height
- `.onSubmit { addTask(); title = "" }` for return-to-add
- `.swipeActions(edge: .leading) { Button { complete(task) } label: { Label("Done", systemImage: "checkmark") }.tint(.green) }`
- `List($tasks, editActions: .move) { $task in … }` for reorder
- `Menu { DatePicker(…) } label: { Label("Due Date", systemImage: "calendar") }` for inline date picker
- `UIImpactFeedbackGenerator(style: .rigid)` for swipe-complete threshold cross

**Haptic + motion choreography:**
- Swipe threshold reached: `.impactOccurred(style: .rigid)` — confirms the action will fire
- Task completed: `.notificationOccurred(.success)` + checkmark scale 0.5→1.2→1.0
- Drag reorder pick-up: `.impactOccurred(style: .light)`; drop: `.impactOccurred(style: .medium)`

**Accessibility:**
- Swipe-to-complete gesture: mirror as `accessibilityAction(named: "Mark Complete") { complete(task) }`
- Reorder: `accessibilityAction(named: "Move up")` / `"Move down"` on each row
- Composer `@FocusState` change: `UIAccessibility.post(notification: .screenChanged, argument: composerField)` so VoiceOver lands on the field

**Anti-patterns:**
- Showing a date picker modal that covers the task being edited
- Return key submitting without re-focusing for next task in return-to-add mode
- `.editMode` toggle visible in primary UI — hide reorder behind long-press or edit button
- Blocking the list update on the main thread when sorting

**Elite reference:** Things 3 (keyboard-first composer, inline quick-entry); OmniFocus (natural language date parsing)

---

## 8. Daily-Habit App

**Goal:** Make streaks feel earned and recoverable — not punishing.

**Critical first impression:** The streak count must be the most prominent element. Users open habit apps to feel progress, not manage data.

**Required states + flow:**
1. Today view: habit ring/checkmark grid, streak counter, completion percentage
2. Calendar grid: `LazyVGrid` with colour intensity encoding completion (GitHub-style)
3. One-missed-day grace: streak visually "freezes" for 24 h before breaking; freeze/insurance day mechanic
4. Goal setting: wheel `Picker` for target count, `Stepper` for target days/week
5. Gentle re-engagement: local notification at user-set time with copy that doesn't guilt ("Your streak is waiting")
6. Streak celebration: milestone (7, 30, 100 days) triggers full-screen confetti + haptic chord

**APIs:**
- `LazyVGrid(columns: Array(repeating: .init(.fixed(32)), count: 7))` for calendar
- `Color.interpolate(from: .systemGray5, to: .systemGreen, fraction: completionRatio)` — custom extension on `Color` using `UIColor` mixing
- `UNUserNotificationCenter` with `UNCalendarNotificationTrigger` for daily nudge
- `Picker("Daily goal", selection: $goal) { ForEach(1...10, id: \.self) { Text("\($0)") } }.pickerStyle(.wheel)` for goal
- Streak freeze: store `lastCompletedDate` + `freezesRemaining` in `@AppStorage` or SwiftData `@Model`
- Celebration: `CAEmitterLayer` for confetti or `package: confetti-swift-ui`; `UINotificationFeedbackGenerator().notificationOccurred(.success)` + 80 ms delay + `UIImpactFeedbackGenerator(style: .heavy).impactOccurred()`

**Haptic + motion choreography:**
- Habit check-off: `.impactOccurred(style: .medium)` + ring fill animation (trim from 0 to completion fraction over 0.5 s)
- Streak milestone: 3-beat haptic chord (success → 80 ms → medium impact → 80 ms → medium impact)
- Freeze used: `.notificationOccurred(.warning)` + shield symbol bounce

**Accessibility:**
- Calendar cells: `accessibilityLabel = "Monday June 2nd, completed"` / `"not completed"`
- Ring animation: pause or replace with instant fill when `isReduceMotionEnabled`
- Streak counter: `accessibilityLabel = "Current streak: \(streak) days"`

**Anti-patterns:**
- Streak breaks silently at midnight with no recovery path
- Guilt-driven notification copy ("You broke your streak!")
- Calendar that shows only the current month — users want to see historical data
- Hiding the freeze mechanic — surface it prominently before the streak breaks

**Elite reference:** Streaks (ring UI, grace period); Habitify (calendar density)

---

## 9. Camera UI

**Goal:** Halide-class: professional controls, instant capture, zero shutter lag.

**Critical first impression:** The viewfinder must be live within 200 ms of the camera screen appearing. Pre-warm the session.

**Required states + flow:**
1. `viewDidLoad` / `.onAppear`: pre-warm `AVCaptureSession` on a background `DispatchQueue` or Swift actor
2. Focus ring animates to tap point, exposure slider appears alongside
3. Manual controls in trailing toolbar: ISO, shutter speed, WB — each a vertical `Slider`
4. Capture: shutter button scales 1.0→0.85→1.0 over 0.15 s, haptic fires at peak compression
5. RAW/HEIF toggle: `AVCapturePhotoSettings(rawPixelFormatType:)` vs standard
6. After capture: thumbnail animates to corner; tap to enter photo picker / viewer handoff via `PHPickerViewController`
7. Permission denied state: full-screen instructional UI with deep-link to Settings

**APIs:**
- `AVCaptureSession`, `AVCaptureDeviceInput`, `AVCapturePhotoOutput` — configure on `sessionQueue`
- `AVCaptureDevice.Focus`: `device.lockForConfiguration(); device.focusPointOfInterest = point; device.focusMode = .autoFocus`
- `AVCapturePhotoSettings(rawPixelFormatType: photoOutput.availableRawPhotoPixelFormatTypes.first!)` for RAW
- `AVCaptureDevice.ExposureMode.custom` + `setExposureModeCustom(duration:iso:completionHandler:)` for manual
- `UIImpactFeedbackGenerator(style: .heavy)` pre-`prepare()`d during viewfinder display; fire on `capturePhoto`
- `PHPickerConfiguration` + `PHPickerViewController` for handoff to library
- `AVCaptureVideoPreviewLayer` in a `UIViewRepresentable` with `videoGravity = .resizeAspectFill`

**Haptic + motion choreography:**
- Focus lock: `.impactOccurred(style: .light)` + focus ring shrink + colour change to yellow
- Shutter press: `.impactOccurred(style: .heavy)` at button scale minimum
- RAW/HEIF toggle: `.selectionChanged()` on `UISelectionFeedbackGenerator`

**Accessibility:**
- Shutter button: `accessibilityLabel = "Take photo"`, `accessibilityTraits = .button`
- Manual controls: `accessibilityLabel = "ISO \(Int(isoValue))"`, `accessibilityHint = "Swipe up or down to adjust"`
- Camera unavailable: `UIAccessibility.post(notification: .announcement, argument: "Camera access required")`

**Anti-patterns:**
- Creating `AVCaptureSession` on the main thread — causes UI freeze
- Not calling `prepare()` on `UIImpactFeedbackGenerator` — adds latency to shutter haptic
- Showing a permissions prompt without explaining why camera access is needed
- Using `captureStillImageAsynchronously` (deprecated) — use `AVCapturePhotoOutput`

**Elite reference:** Halide (manual controls, session pre-warm, focus ring UX); ProCamera

---

## 10. Chart-Heavy Surface

**Goal:** Data is instantly readable at a glance; complex datasets remain accessible to VoiceOver.

**Critical first impression:** Charts must render on first frame, not after a loading delay. Pre-compute data on a background actor.

**Required states + flow:**
1. Summary KPI row at top (large number + trend arrow)
2. Primary chart with interactive selection (tap or drag to inspect a data point)
3. Detail callout: animated popover or overlay showing exact value + date
4. Axis labels adapt to Dynamic Type and locale
5. Legend for multi-series; colour + shape differentiation (never colour alone)
6. Empty state with skeleton chart (dashed axes, placeholder bars)

**APIs:**
- `Chart(data) { BarMark(x: .value("Date", $0.date), y: .value("Count", $0.count)) }` — Swift Charts default
- `chartOverlay { proxy in DragGesture().onChanged { value in selectedX = proxy.value(atX: value.location.x, as: Date.self) } }` for selection via `ChartProxy`
- `.chartXAxis { AxisMarks(values: .stride(by: .day)) { AxisValueLabel(format: .dateTime.weekday()) } }` for axis formatting
- `.accessibilityRepresentation { List(data) { Text("\($0.date.formatted()): \($0.count)") } }` — critical for VoiceOver
- `Text(value, format: .number.locale(Locale.current))` for locale-aware number formatting
- `Canvas` only when Swift Charts cannot meet frame-rate requirements (e.g. 10k+ data points animating continuously) — measure first with Instruments

**Haptic + motion choreography:**
- Selection drag crossing a data point: `.selectionChanged()` on `UISelectionFeedbackGenerator`
- KPI trend direction change (on data refresh): `.notificationOccurred(.success)` for improvement, `.notificationOccurred(.warning)` for regression

**Accessibility:**
- Always provide `.accessibilityRepresentation` — Swift Charts' default VoiceOver is poor without it
- Colour differentiation: pair with distinct `symbol` shapes (`PointMark` with `.square`, `.circle`, `.triangle`)
- Trend arrows: `accessibilityLabel = "Up 12 percent from last week"`, not just "↑12%"

**Anti-patterns:**
- Using `Canvas` before proving Swift Charts can't handle the load
- Axis labels that truncate at default Dynamic Type sizes — test at Accessibility XL
- Interactive charts with only colour distinguishing states (fails colour-blind users)
- Omitting `.accessibilityRepresentation` (leaves VoiceOver users with nothing)

**Elite reference:** Strava (segment charts, KPI surface); Health.app (Swift Charts with full VoiceOver representation)

---

## 11. Inbox / List-Based Reader

**Goal:** Apollo-class triage: fast, swipeable, never loses unread state.

**Critical first impression:** Content must be visible before the first scroll — no full-screen loading spinner. Load optimistically from cache, then refresh in background.

**Required states + flow:**
1. Unread badge on tab bar item (`UITabBarItem.badgeValue`)
2. Pull-to-refresh: `refreshable { await viewModel.refresh() }`
3. Swipe-to-archive (leading): green, checkmark; swipe-to-snooze (trailing): purple, clock
4. Mark-all-read: toolbar button with `confirmationDialog` if count > 10
5. `.listRowSeparator(.hidden)` for editorial card layout; `.listRowSeparator(.visible)` for dense list
6. Unread dot: filled circle in leading margin, fades on read with `.animation(.easeOut(duration: 0.3))`
7. Empty inbox: celebratory illustration + "You're all caught up" copy

**APIs:**
- `List(items) { item in … }.refreshable { await refresh() }` — pulls iOS system refresh control
- `.swipeActions(edge: .leading, allowsFullSwipe: true) { Button { archive(item) } label: { Label("Archive", systemImage: "archivebox") }.tint(.green) }`
- `.swipeActions(edge: .trailing) { Button { snooze(item) } label: { Label("Snooze", systemImage: "clock") }.tint(.purple) }`
- `.listRowSeparator(.hidden)` for card-style rows; surround cards in `.listRowInsets(.init(top: 4, leading: 16, bottom: 4, trailing: 16))`
- `UIApplication.shared.applicationIconBadgeNumber` or `UNUserNotificationCenter` for badge
- Unread persistence: SwiftData `@Model` with `isRead: Bool`; `NSPredicate` fetch for unread count
- `UIImpactFeedbackGenerator(style: .soft)` on full-swipe threshold

**Haptic + motion choreography:**
- Full-swipe threshold cross: `.impactOccurred(style: .soft)` confirming the action
- Archive completes: `.notificationOccurred(.success)` + row slides out with `.transition(.move(edge: .leading))`
- Mark-all-read: `.impactOccurred(style: .medium)` + badge number animates to 0

**Accessibility:**
- Swipe actions mirrored as `accessibilityAction`: `accessibilityAction(named: "Archive") { archive(item) }`
- Unread indicator: `accessibilityLabel` includes "unread," e.g. "Article title, unread"
- Badge: handled automatically by system when `badgeValue` is set

**Anti-patterns:**
- Full-screen spinner on every app launch — always show stale cache first
- Swipe actions that require pixel-perfect drag angle — use generous gesture recognizer tolerance
- Resetting scroll position on background refresh — preserve offset, insert new items at top
- Showing badge for in-app notifications the user can't dismiss

**Elite reference:** Apollo (swipe choreography, unread persistence); Reeder (editorial card layout, snooze)

---

## 12. App Intents / Shortcuts Donation

**Goal:** The app's core actions appear in Spotlight, Siri suggestions, and the Shortcuts app without the user doing anything.

**Critical first impression:** Siri suggestions appear in Spotlight within 24 h of a user completing an action twice at roughly the same time or context — donate immediately after the meaningful action.

**Required states + flow:**
1. Define `AppIntent` conformances for top 5–8 user actions
2. Donate `INInteraction` (legacy) or `AppShortcutsProvider` (current) after each meaningful action
3. Shortcuts app: `AppShortcutsProvider` with `AppShortcut(intent:phrases:shortTitle:systemImageName:)` — these appear automatically without user setup
4. Siri suggestion surface: `INVoiceShortcutCenter` registration + widget suggestion
5. Widget / Spotlight: `CSSearchableItem` for content deep-links
6. Parameter summarization: `ParameterSummary` for rich Shortcuts editor display

**APIs:**
- `struct AddTaskIntent: AppIntent { static let title = LocalizedStringResource("Add Task"); @Parameter(title: "Title") var title: String; func perform() async throws -> some IntentResult }` (Swift 5.9+, iOS 17+)
- `AppShortcutsProvider`: `static var appShortcuts: [AppShortcut] { AppShortcut(intent: AddTaskIntent(), phrases: ["Add a task in \(.applicationName)", "Remind me in \(.applicationName)"], shortTitle: "Add Task", systemImageName: "plus.circle") }`
- `AppShortcutsProvider.updateAppShortcutParameters()` — call when dynamic parameter values change (e.g. project list changes)
- `INInteraction(intent:response:).donate(completion:)` for legacy Siri donation (iOS 12+ fallback)
- `CSSearchableItem(uniqueIdentifier:domainIdentifier:attributeSet:)` + `CSSearchableIndex.default().indexSearchableItems` for Spotlight
- `RelevantContext` / `RelevantIntentManager` (iOS 16+) for proactive Siri suggestions at contextually relevant times

**Haptic + motion choreography:**
- No haptic needed for silent donations — they happen in the background
- Siri shortcut added confirmation (if surfacing an "Add to Siri" button): `.notificationOccurred(.success)`

**Accessibility:**
- `AppIntent` phrases must cover natural language variants — include both "Add a task" and "Create a task"
- `ParameterSummary` ensures VoiceOver in Shortcuts editor reads the intent configuration correctly
- All `@Parameter` titles are `LocalizedStringResource` — never raw `String`

**Anti-patterns:**
- Donating intents before the user completes an action (premature donations confuse Siri's ML)
- Registering only one phrase per shortcut — Siri matching improves with diversity
- Using deprecated `INSiriAuthorizationStatus` APIs instead of `AppIntents` framework
- Forgetting `AppShortcutsProvider.updateAppShortcutParameters()` when dynamic options change — stale parameters break the Shortcuts editor

**Elite reference:** Things 3 (deep Shortcuts integration, parameterised task creation); Mela (recipe intent, Spotlight indexing)
