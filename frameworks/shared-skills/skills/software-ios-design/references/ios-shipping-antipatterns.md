# iOS Shipping Anti-Patterns

Hard-edged review notes for senior iOS engineers about to hit Submit. These mistakes cost rejections, churn, and 1-star reviews. Fix them before you ship.

---

## Table of Contents

- [1. ATT Prompt at First Launch](#1-att-prompt-at-first-launch)
- [2. Push Permission at First Launch](#2-push-permission-at-first-launch)
- [3. Permissions Requested Too Early or With Generic Descriptions](#3-permissions-requested-too-early-or-with-generic-descriptions)
- [4. Paywall on First Launch Before Value Preview](#4-paywall-on-first-launch-before-value-preview)
- [5. Toolbar Overcrowding](#5-toolbar-overcrowding)
- [6. `.alert` Where `.confirmationDialog` Belongs](#6-alert-where-confirmationdialog-belongs)
- [7. Custom Nav Bars That Break Edge-Swipe-Back](#7-custom-nav-bars-that-break-edge-swipe-back)
- [8. `.interactiveDismissDisabled` on Every Sheet](#8-interactivedismissdisabled-on-every-sheet)
- [9. `.navigationDestination` Outside `NavigationStack`](#9-navigationdestination-outside-navigationstack)
- [10. `NavigationLink(isActive:)` Deprecated API](#10-navigationlinkisactive-deprecated-api)
- [11. Drag-Dismissal Resistance Feel](#11-drag-dismissal-resistance-feel)
- [12. Large Title Scroll-Collapse Choreography Broken](#12-large-title-scroll-collapse-choreography-broken)
- [13. Full-Swipe Destructive Without Confirmation](#13-full-swipe-destructive-without-confirmation)
- [14. Picker Wheel Physics Override](#14-picker-wheel-physics-override)
- [15. Edge-Swipe Back Gesture Conflicts With Horizontal Pager](#15-edge-swipe-back-gesture-conflicts-with-horizontal-pager)
- [16. App Store Screenshots Without Craft](#16-app-store-screenshots-without-craft)
- [17. App Store Preview Video That Fails Within 3 Seconds](#17-app-store-preview-video-that-fails-within-3-seconds)
- [18. App Store Metadata Craft Failures](#18-app-store-metadata-craft-failures)
- [19. App Review Process Traps](#19-app-review-process-traps)
- [20. Monetization on Lock Screen Widgets or Live Activities](#20-monetization-on-lock-screen-widgets-or-live-activities)
- [21. Background Mode Abuse](#21-background-mode-abuse)
- [22. Privacy Nutrition Label Drift](#22-privacy-nutrition-label-drift)
- [23. No Crash-on-Launch Test in Reviewer's Region](#23-no-crash-on-launch-test-in-reviewers-region)
- [24. Memory Pressure on Older Devices](#24-memory-pressure-on-older-devices)
- [25. Sign in with Apple Omission](#25-sign-in-with-apple-omission)
- [26. English-Only App Store Metadata for a Localized App](#26-english-only-app-store-metadata-for-a-localized-app)
- [27. Rating Prompt at the Wrong Moment](#27-rating-prompt-at-the-wrong-moment)
- [28. Third-Party AI Data Sharing Without Consent (2026)](#28-third-party-ai-data-sharing-without-consent-2026)
- [29. AI Features Ignored in the Age Rating (2026)](#29-ai-features-ignored-in-the-age-rating-2026)
- [30. Shipping Without the iOS 26 SDK (in effect since April 28, 2026)](#30-shipping-without-the-ios-26-sdk-in-effect-since-april-28-2026)
- [Pre-Submit Checklist](#pre-submit-checklist)

---

## 1. ATT Prompt at First Launch

**Asking for tracking permission before the user has experienced any value.**

**Why it fails:** Apple's ATT guidelines require that the purpose of tracking be clear to the user. Presenting `ATT.requestTrackingAuthorization()` on the first screen they ever see means they have no context for why you need it, no trust in your product, and every incentive to tap "Ask App Not to Track." Industry data consistently shows opt-in rates of 20–30% when prompted cold on launch versus 50–65% after a meaningful session.

**Fix:** Gate the prompt behind a real user action — first completed workout, first content save, first session completion. Immediately before the system dialog, show a custom pre-prompt screen that explains in plain language what you track and what the user gets in return ("We use this to show you relevant content and keep the app free"). This pre-prompt is your only chance to shift the framing; the system dialog gives you nothing.

**Real-world consequence:** ATT decline rates above 70% for apps that prompt cold. At that rate attribution breaks, paid UA becomes guesswork, and LTV modelling collapses. Not a rejection risk — a revenue risk.

---

## 2. Push Permission at First Launch

**Asking for notification permission on the splash or onboarding screen.**

**Why it fails:** The user has no idea yet whether your notifications are worth anything. iOS shows the system permission dialog once; deny means permanently off until the user manually re-enables in Settings. Burning that dialog cold is irreversible.

**Fix:** Defer until the user takes an action that has an obvious notification benefit: saves an item ("notify me when price drops"), submits a reply ("notify me when someone responds"), sets an alarm, or completes a meaningful session. At that moment show a pre-prompt explaining the exact notification they'll receive, then fire `UNUserNotificationCenter.requestAuthorization`.

**Real-world consequence:** Cold-prompt opt-in rates run 40–50% lower than contextual-prompt rates. Low opt-in means poor re-engagement, higher churn, and degraded push campaign ROI — all of which App Review does not care about, but your retention metrics will.

---

## 3. Permissions Requested Too Early or With Generic Descriptions

**Photos, camera, location, microphone, and contacts permissions presented before the user has a reason to grant them, with boilerplate `NSPrivacy*UsageDescription` strings.**

**Why it fails:** Apple rejects apps where usage descriptions are vague ("This app uses your camera") or where permissions are requested speculatively. Reviewers read the usage description strings in `Info.plist` and cross-check them against the actual prompt context. "We use location to serve you better" gets rejected. Permissions presented before the relevant feature is accessed get rejected under Guideline 5.1.1.

**Fix:** Request permissions inline at the point of need — camera when the user taps "Take Photo," location when they tap "Find Nearby." Write usage descriptions that name the specific feature: "Used to scan receipts in the Expense Capture screen." For location, use `.whenInUse` unless you have a documented continuous-use case; `.always` requires a second, more invasive prompt and draws App Review scrutiny.

**Real-world consequence:** Rejection under Guideline 5.1.1. Even if it ships, premature permission dialogs increase deny rates, which breaks the feature and generates 1-star reviews from users who don't know they denied it.

---

## 4. Paywall on First Launch Before Value Preview

**Full paywall or subscription prompt before the user has seen what they're buying.**

**Why it fails:** App Review Guideline 3.1.1 is explicit: apps must not present paywalls that prevent users from seeing what the app does before asking for payment. Reviewers will reject an app that opens directly into a purchase screen. Beyond rejection, cold paywalls produce conversion rates near zero and churn after any free trial that was only accessed to skip the gate.

**Fix:** Build a value-preview path. Show the core feature in read-only or limited mode. Let the user feel the product. Gate advanced features or unlimited use behind the subscription, not the first tap. If you must gate hard, show at least 2–3 populated screens of the real UI before the paywall appears.

**Real-world consequence:** Rejection under Guideline 3.1.1. Even when it slips through review, cold paywalls are a primary driver of "this app does nothing, just asks for money" 1-star reviews.

---

## 5. Toolbar Overcrowding

**More than 3–4 `ToolbarItem` entries without overflow handling.**

**Why it fails:** On the smallest currently-sold iPhone (6.1", e.g. iPhone 16e — Apple discontinued the sub-6.1"/4.7" iPhone SE in February 2025) or any compact-width device, SwiftUI's toolbar collapses items unpredictably when they don't fit. The collapse order is not guaranteed and varies by OS version. Users end up with truncated labels, invisible buttons, or layout breakage — and a large installed base still runs older 4.7"/5.4" hardware, so don't assume 6.1" is a floor for real users even though it is for new-device testing.

**Fix:** Apply the 3-item rule: primary action, secondary action, optional overflow. Wrap everything else in a `Menu`:

```swift
ToolbarItem(placement: .topBarTrailing) {
    Menu {
        Button("Archive", action: archive)
        Button("Share", action: share)
        Button("Duplicate", action: duplicate)
    } label: {
        Image(systemName: "ellipsis.circle")
    }
}
```

Test on the smallest currently-sold iPhone (6.1") and, if you support older OS versions, an iPhone SE/mini-class device from the installed base, at every toolbar change.

**Real-world consequence:** Visual regression on small devices. App Review tests on real hardware, including older iPhones still in the field. Layout breakage triggers rejection or post-ship 1-star reviews from compact-device users.

---

## 6. `.alert` Where `.confirmationDialog` Belongs

**Using `Alert` for destructive multi-choice actions.**

**Why it fails:** Apple HIG is unambiguous: alerts are for system-state information and single-action acknowledgements. Destructive choices — delete, discard, remove — belong in action sheets (`confirmationDialog`). Alerts with more than two buttons, or alerts used for irreversible actions, deviate from the platform pattern users have internalized since iOS 7.

**Fix:**
```swift
// Wrong — alert for destructive choice
.alert("Delete item?", isPresented: $showDelete) {
    Button("Delete", role: .destructive) { delete() }
    Button("Cancel", role: .cancel) {}
}

// Correct — confirmationDialog for destructive choice
.confirmationDialog("Delete item?", isPresented: $showDelete, titleVisibility: .visible) {
    Button("Delete", role: .destructive) { delete() }
    Button("Cancel", role: .cancel) {}
}
```

**Real-world consequence:** Not a rejection trigger, but a UX signal. Users feel it as "this app feels wrong." Combined with other platform deviations, it contributes to churn and negative reviews.

---

## 7. Custom Nav Bars That Break Edge-Swipe-Back

**Replacing the navigation back button or overriding the navigation bar appearance in ways that disable the interactivePopGestureRecognizer.**

**Why it fails:** The edge-swipe-back gesture (`UINavigationController.interactivePopGestureRecognizer`) is a deeply learned iOS navigation primitive. Custom back button implementations that hide or replace the system chevron typically disable it silently. Users swipe from the left edge, nothing happens, and they feel trapped.

**Fix:** Use `.toolbarBackground` and `.toolbarColorScheme` for visual customization instead of replacing the bar. If you must change the back button label, use `.navigationBackButtonHidden(false)` only when truly hiding, and wire your replacement button to `dismiss` or `popViewController`. Never set `interactivePopGestureRecognizer.isEnabled = false` unless the current screen has an explicit swipe interaction that conflicts.

**Real-world consequence:** "Back button doesn't work" is a 1-star review generator. Users do not understand the technical cause; they just know the app feels broken.

---

## 8. `.interactiveDismissDisabled` on Every Sheet

**Disabling swipe-down dismissal globally on presented sheets.**

**Why it fails:** `.interactiveDismissDisabled(true)` was designed for one scenario: the user has unsaved data that would be lost if they dismiss. Using it everywhere because it feels "safer" breaks the modal-dismissal contract users expect on iOS. Every sheet that refuses to swipe down generates a moment of confusion.

**Fix:** Enable it only when there is genuinely unsaved state:

```swift
.interactiveDismissDisabled(hasUnsavedChanges)
```

When enabled, always provide a visible "Cancel" or "Discard" button so the user can exit intentionally. For sheets with no destructive state, leave swipe-dismiss active.

**Real-world consequence:** Not a rejection cause. A persistent "feels broken" signal that accumulates into negative reviews, especially from power users who live in swipe-dismiss muscle memory.

---

## 9. `.navigationDestination` Outside `NavigationStack`

**Placing `.navigationDestination(for:destination:)` on a view that is not inside a `NavigationStack`.**

**Why it fails:** `.navigationDestination` is silently ignored when there is no `NavigationStack` ancestor. No error, no warning, no crash — just navigation that never happens. This is one of the most common SwiftUI navigation bugs because the failure is invisible at compile time.

**Fix:** Always verify the containment chain. The `NavigationStack` must be the direct or indirect ancestor:

```swift
NavigationStack(path: $path) {
    ContentView()
        .navigationDestination(for: Item.self) { item in
            ItemDetailView(item: item)
        }
}
```

Do not add `.navigationDestination` in a subview hoping it propagates up — it must sit inside the stack's content closure.

**Real-world consequence:** Dead navigation paths. In App Review, any tappable element that does nothing is a rejection risk under the "functional app" requirement. Post-ship, users report "tapping X does nothing."

---

## 10. `NavigationLink(isActive:)` Deprecated API

**Using the `isActive`-binding form of `NavigationLink` in new code.**

**Why it fails:** `NavigationLink(isActive:destination:label:)` was deprecated in iOS 16. It works against the `NavigationStack` path model and does not compose with programmatic navigation. Mixing deprecated link syntax with `NavigationStack` path-based routing produces unpredictable behavior — multiple destinations activating simultaneously, back-stack inconsistencies, and state desync.

**Fix:** Migrate to path-based routing:

```swift
@State private var path = NavigationPath()

NavigationStack(path: $path) {
    List(items) { item in
        NavigationLink(value: item) {
            ItemRow(item: item)
        }
    }
    .navigationDestination(for: Item.self) { item in
        ItemDetailView(item: item)
    }
}
```

For programmatic push: `path.append(item)`. For pop: `path.removeLast()`.

**Real-world consequence:** Not a rejection trigger. A technical debt bomb — the deprecated API will be removed in a future SDK, and the migration cost grows with every screen added on top of it.

---

## 11. Drag-Dismissal Resistance Feel

**Sheets that snap closed too aggressively, refuse intermediate detents, or fight the user's drag.**

**Why it fails:** When a sheet has no `presentationDetents` modifier, it presents at full height and either dismisses or doesn't — no intermediate resting point. Users who drag a sheet down expecting it to settle at half-height get a hard snap to closed, which feels unresponsive and wastes their context.

**Fix:** Define explicit detents and show the drag indicator:

```swift
.sheet(isPresented: $showSheet) {
    SheetContent()
        .presentationDetents([.medium, .large])
        .presentationDragIndicator(.visible)
}
```

Use `.medium` as the default for utility sheets. Use `.large` for content-rich sheets. Do not define a single `.large` detent and hide the drag indicator — it signals the sheet is dismissible but provides no grip affordance.

**Real-world consequence:** Low-grade UX friction. Users who don't find the drag indicator assume the sheet is modal and hunt for a close button. If there isn't one, they force-close the app.

---

## 12. Large Title Scroll-Collapse Choreography Broken

**Overriding the navigation bar background in ways that break the large-title-to-inline-title collapse animation.**

**Why it fails:** The large title collapse on scroll is choreographed with the navigation bar's glass/blur material. When you replace the bar background with a solid `UIColor` via `UINavigationBarAppearance` or use `.toolbarBackground(.hidden)` globally, the collapse animation either freezes, flickers, or exposes the underlying content bleeding through the bar.

**Fix:** Use SwiftUI's `.toolbarBackground` modifier with a `ShapeStyle` rather than overriding `UINavigationBarAppearance` directly:

```swift
.toolbarBackground(.ultraThinMaterial, for: .navigationBar)
.toolbarBackground(.visible, for: .navigationBar)
```

If you need a solid color, apply it through `Color` as a `ShapeStyle`, not through UIKit appearance overrides. Test the scroll-collapse at every navigation level with `displayMode: .large`.

**Real-world consequence:** Visible animation glitch on scroll in the primary navigation view. Prominent enough to trigger "looks unfinished" App Review feedback and 1-star "bad UI" reviews.

---

## 13. Full-Swipe Destructive Without Confirmation

**List rows with `allowsFullSwipe: true` on a destructive action, with no undo path.**

**Why it fails:** The default `swipeActions` behavior allows a full swipe to immediately commit the leading or trailing action. For a destructive action (delete, archive permanently), this means one fast swipe destroys data with no confirmation and no recovery. Users who swipe accidentally have no recourse.

**Fix:** Either disable full-swipe for destructive actions:

```swift
.swipeActions(edge: .trailing, allowsFullSwipe: false) {
    Button(role: .destructive) { delete(item) } label: {
        Label("Delete", systemImage: "trash")
    }
}
```

Or keep full-swipe and show an undo toast immediately after commit:

```swift
// After deletion
withAnimation { items.remove(at: index) }
showUndoToast(for: deletedItem, timeout: 4)
```

**Real-world consequence:** "Accidentally deleted everything" is a category of 1-star reviews. No rejection risk, but the review bomb is worse for long-term ranking than a single rejection.

---

## 14. Picker Wheel Physics Override

**Replacing a `Picker` with `.pickerStyle(.wheel)` with a custom segmented button strip or horizontal scroll view.**

**Why it fails:** The wheel Picker delivers haptic feedback at each detent via `UISelectionFeedbackGenerator`, simulating physical scroll momentum. Custom button strips have no momentum, no haptics, and no accessibility support for VoiceOver scroll-to-select. Users on older muscle memory expect the wheel's physics for date, time, and other enumerated values.

**Fix:** Keep `.pickerStyle(.wheel)` for enumerated value selection where order and proximity matter. Use `.pickerStyle(.segmented)` only for 2–4 options where all values are simultaneously visible. Build custom UI only when the picker genuinely cannot express the interaction — and wire `UISelectionFeedbackGenerator` manually.

**Real-world consequence:** Accessibility failures (VoiceOver cannot interact with custom button strips built without `accessibilityAdjustableAction`). App Review flags accessibility regressions on explicitly tested pickers.

---

## 15. Edge-Swipe Back Gesture Conflicts With Horizontal Pager

**A `TabView` with `.tabViewStyle(.page)` or a custom horizontal carousel placed at the root of a navigation stack, consuming the left-edge swipe.**

**Why it fails:** `UIScrollView`-backed horizontal pagers intercept the `UIScreenEdgePanGestureRecognizer` used by `interactivePopGestureRecognizer`. The back gesture fires into the pager instead of the navigation stack. Users cannot swipe back from a screen that hosts a full-width horizontal scroll view.

**Fix:** Scope the horizontal gesture to an area that does not reach the screen edge. Add leading padding to the pager's hit area, or use `UIGestureRecognizerDelegate.gestureRecognizerShouldBegin` to fail the pager's recognizer when the touch originates within 20pt of the left edge. Alternatively, move the pager to a sub-area of the screen rather than full-bleed.

**Real-world consequence:** "Can't go back" is reported as a crash by many users who don't know swipe-back exists. 1-star reviews and churn.

---

## 16. App Store Screenshots Without Craft

**Submitting raw simulator screenshots with no device frames, no captions, no populated state.**

**Why it fails:** Screenshots are the primary conversion driver on the App Store product page. Apple's own data shows screenshots are the first thing users examine before tapping "Get." A blank or lightly populated UI with no explanatory text tells the user nothing about the value. Top-grossing apps in every category use bold caption overlays naming the feature, show the app in its most compelling populated state, and use device frames or lifestyle context to establish trust.

**Fix:** For each screenshot: pick the single most compelling feature state, populate it with realistic data, add a 2–6 word caption in large bold type that names the feature's benefit ("Track spending in seconds"), and use consistent branding across all 6–10 screenshots. Use Sketch, Figma, or AppStore Screenshot Generator to composite frames and captions.

**Real-world consequence:** Not a rejection risk. A direct conversion loss. Low-quality screenshots reduce tap-through from search results, increasing effective CPI by 20–40% on paid campaigns and suppressing organic conversion.

---

## 17. App Store Preview Video That Fails Within 3 Seconds

**Preview videos that open on a loading screen, an empty state, or a logo, with no subtitles and reliance on audio.**

**Why it fails:** App Store preview videos autoplay silently in search results. If the first 3 seconds show a splash screen or loading spinner, the user sees nothing useful and scrolls past. Apple requires videos to be 15–30 seconds, but the decision to stop or tap is made in the first 3.

**Fix:** Open the video on the most visually compelling UI state — a populated dashboard, a satisfying interaction, a before/after. Use captions or on-screen text for every key point because autoplay is silent. Show the core value proposition by second 3. Film on a real device or use a simulator recording cleaned up in Final Cut or ScreenFlow. Never use a marketing-style montage that doesn't show the actual app UI.

**Real-world consequence:** App Review rejects preview videos that show placeholder content, competitor UI, pricing claims that contradict the current subscription terms, or content that violates App Store guidelines. A video rejection holds the entire submission.

---

## 18. App Store Metadata Craft Failures

**Title overflow, keyword field waste, and Promotional Text neglected.**

**Why it fails:**
- Title: 30-character hard cap. Characters beyond 30 are truncated in search results. Keywords in the title field boost ASO but must not duplicate the keyword field.
- Subtitle: 30-character hard cap. Second most visible text in search results. Used by the App Store algorithm for indexing. Wasting it on taglines instead of descriptive keywords is a ranking loss.
- Keywords: 100-character field, comma-separated, **no spaces after commas** (spaces consume characters), no words that duplicate the title or subtitle (Apple ignores duplicates), no competitor names (guidelines violation and grounds for rejection), no App Store category names (already indexed).
- Promotional Text: 170 characters, not indexed, updateable without a new app submission. Use it for what's-new teasers and time-limited offers.

**Fix:** Treat the keyword field as 100 characters of pure ASO real estate. Every character counts. Run keyword research, eliminate low-volume terms, cut spaces, deduplicate against title and subtitle. Update Promotional Text with every meaningful release.

**Real-world consequence:** Keyword field violations (competitor names) trigger rejection. Subtitle overflow and wasted keywords are silent ranking losses that compound over the app's lifetime.

---

## 19. App Review Process Traps

**Common submission mistakes that trigger rejection or prolonged review.**

**Why it fails — specific traps:**
- **Placeholder or lorem ipsum content** anywhere in the binary. Reviewers open the app and read.
- **Broken demo login credentials** in the review notes. If the reviewer cannot sign in, the app is rejected immediately.
- **Beta/test language** in the UI ("coming soon," "placeholder," "debug mode"). Signals the app is not ready.
- **Apple trademark misuse** — do not use "iPhone," "iPad," "Apple," or "iOS" in your app name or screenshots in ways that imply Apple endorsement.
- **Subscription terms inconsistency** — the in-app purchase product description, the paywall copy, and the App Store subscription description must all agree on price, duration, and what's included.
- **Sign in with Apple omission (Guideline 4.8)** — if the app offers any third-party or email-based login (Google, Facebook, email+password), it must also offer Sign in with Apple. This is one of the most common rejection causes for apps with social login.

**Fix:** Before every submission: clear all demo credentials from keychain, verify demo account works in the reviewer's region, grep the binary for "placeholder"/"TODO"/"test"/"beta," audit all subscription copy for consistency, and confirm Sign in with Apple is implemented if any other login method exists.

**Real-world consequence:** Rejection. Guideline 4.8 rejections are immediate and require a resubmission cycle. Each cycle is 24–48 hours of delay at minimum.

---

## 20. Monetization on Lock Screen Widgets or Live Activities

**Attempting to show IAP prompts, subscription upsells, or paid content gates inside WidgetKit extensions or Live Activities.**

**Why it fails:** Widgets and Live Activities run in a sandboxed extension process with no access to `StoreKit` and no ability to present UI overlays. Any attempt to gate widget content behind a paywall or trigger a purchase flow from a widget tap is disallowed. Apple's guidelines explicitly prohibit widgets from being the primary surface for monetization.

**Fix:** Widgets and Live Activities are awareness and re-engagement surfaces, not conversion surfaces. Tapping a widget can deep-link into the app where the paywall or IAP flow lives. Design widget content to be useful without a gate — if a user cannot get value from the widget without paying, they will remove it.

**Real-world consequence:** Rejection if the implementation attempts to present StoreKit UI from a widget extension. Even if it compiles, the StoreKit calls will silently fail, and the widget will appear broken.

---

## 21. Background Mode Abuse

**Declaring `background-fetch`, `location`, `audio`, or `processing` in `UIBackgroundModes` without a continuous, demonstrable use case.**

**Why it fails:** App Review audits background mode declarations during review. An app that claims `location` background mode but only shows a one-time "Find Nearby" feature will be rejected under Guideline 2.5.4. Reviewers look for correlation between the declared mode and the app's actual functionality. Using background fetch to keep data fresh for a weather app is legitimate; using it to ping an analytics endpoint is not.

**Fix:** Declare only the modes you actively use. For location, use `.whenInUse` wherever possible and document the always-on use case explicitly in review notes if you genuinely need it. For background processing, use `BGTaskScheduler` correctly with explicit task identifiers registered in `Info.plist`.

**Real-world consequence:** Rejection under Guideline 2.5.4. Post-ship, undeclared background activity is caught by App Store privacy nutrition label audits and can trigger removal.

---

## 22. Privacy Nutrition Label Drift

**Declared data collection in the App Store privacy label diverging from actual SDK behavior after a dependency update.**

**Why it fails:** The privacy nutrition label is a legal attestation. When an SDK update introduces new data collection — an ad network SDK adding device fingerprinting, an analytics SDK adding new identifiers — your declared label is now wrong. Apple cross-checks labels against known SDK behaviors and flags discrepancies. More importantly, privacy regulators treat the label as a binding disclosure.

**Fix:** Before every release that bumps a third-party dependency, audit what data that SDK collects. Most SDK vendors publish data collection disclosures in their privacy policies. Check: analytics SDKs, ad networks, crash reporters, attribution platforms, and any SDK with a network layer. Run a proxy (Charles, Proxyman) against a fresh install to verify actual network calls match declarations. Update the privacy nutrition label before submission.

**Real-world consequence:** App removal post-submission if Apple audits and finds the label misleading. In the EU under GDPR, an incorrect label is a regulatory exposure for apps with European users.

---

## 23. No Crash-on-Launch Test in Reviewer's Region

**Shipping without a fresh install test on the lowest supported device in a non-default locale.**

**Why it fails:** App Review uses fresh installs on real devices, often in the US or EU, with system language set to their region's default. The three most common reviewer-locale bugs: (1) a `dateFormatter.date(from:)` returning `nil` for a locale-specific format string, (2) Dynamic Type set to Accessibility XL breaking a fixed-height layout, (3) a runtime crash on lower-RAM devices caused by a force-unwrap that only triggers when memory is constrained.

**Fix:** Before every submission, run a fresh install (delete app, reinstall from archive) on the lowest device your deployment target actually supports — check your minimum-RAM device against the current Apple lineup each session; Apple discontinued the iPhone SE (and sub-6.1" displays generally) in February 2025, so "lowest supported device" now means either the smallest current model (6.1", e.g. iPhone 16e) or the oldest OS-eligible device still in your deployment target, whichever is more constrained — with system language set to a non-English locale (French or German reveal date/number formatting bugs fastest). Enable Dynamic Type Accessibility XL in Settings and scroll every primary screen.

**Real-world consequence:** Crash on launch in App Review = immediate rejection with binary quarantine. The reviewer's device becomes the evidence. Reproduce it yourself before they do.

---

## 24. Memory Pressure on Older Devices

**Loading full-resolution images synchronously on the main thread without size constraints.**

**Why it fails:** Older and lower-RAM devices still in the installed base (4GB-class hardware such as iPhone SE 3rd gen or iPhone 12) share that RAM with a full iOS stack. An app that loads 10 × 4MB images into a `UICollectionView` without downsampling will receive memory warnings within seconds and be terminated by the OS on that hardware. App Review tests on real devices, and a jetsam termination mid-review is indistinguishable from a crash.

**Fix:** Downsample images to display size using `ImageIO` or `vImage` before rendering. Use `UIImage(data:scale:)` with explicit scale, not `UIImage(named:)` for downloaded content. In SwiftUI, use `AsyncImage` with a `.resizable()` + `.scaledToFill()` combo and explicit `.frame` to ensure the image decoder knows the target size. Never load `Data` of unknown size synchronously on the main thread.

**Real-world consequence:** OS termination during App Review = rejection. Post-ship, jetsam logs in Xcode Organizer confirm the pattern; it generates 1-star "app keeps crashing" reviews specifically from lower-RAM device users (SE-class, iPhone 12).

---

## 25. Sign in with Apple Omission

**Offering Google Sign-In, Facebook Login, or email/password login without including Sign in with Apple.**

**Why it fails:** App Review Guideline 4.8 is explicit and mechanically enforced: any app that offers a third-party login mechanism must also offer Sign in with Apple as an equivalent option. The reviewer will tap "Continue with Google," see no Sign in with Apple button, and reject the submission. No exceptions for "we'll add it later."

**Fix:** Implement `AuthenticationServices` Sign in with Apple before adding any other third-party login. It takes less time to implement than Google Sign-In. Place the Sign in with Apple button at the top of the login stack (Apple's guidelines require it be at least as prominent as other options). Handle the credential revocation notification (`ASAuthorizationAppleIDProvider.credentialRevokedNotification`) to sign users out gracefully.

**Real-world consequence:** Immediate rejection on first submission. If it somehow shipped without it, a future review cycle (update, new feature) triggers the same rejection retroactively.

---

## 26. English-Only App Store Metadata for a Localized App

**Shipping only the default English `en-US` App Store listing when the app itself supports multiple languages.**

**Why it fails:** The App Store serves localized product pages to users based on their device language and store region. An app with full German, French, and Japanese localization that has only English App Store metadata shows English screenshots, English descriptions, and English titles to German, French, and Japanese users. Conversion rates in non-English stores drop sharply when the listing is not localized — users interpret an English listing as a product that doesn't support their language, even when it does.

**Fix:** For every locale the app supports, create a matching App Store Connect localization: translated title, subtitle, description, keywords (translated and region-relevant, not just translated), and localized screenshots with region-appropriate content and captions. Use `fastlane deliver` or App Store Connect's localization export to manage this at scale.

**Real-world consequence:** Not a rejection risk. A direct and measurable conversion loss in non-English stores. For apps with significant non-English user bases, this is a sustained revenue underperformance.

---

## 27. Rating Prompt at the Wrong Moment

**Calling `SKStoreReviewController.requestReview()` after an error, on first launch, or on a timer.**

**Why it fails:** Apple throttles `requestReview()` to a maximum of 3 displays per 365-day period per user. Once the quota is spent, the call is silently ignored until the next year. Wasting a prompt on a user who just encountered an error or who has used the app for 30 seconds produces a 1-star review from the small percentage who respond and silence from everyone else. The 3/year limit also means poorly timed prompts may fire at wrong moments long after the initial trigger.

**Fix:** Fire `requestReview()` only after a genuine success moment: task completed, level passed, report generated, trip logged, item saved. Gate it behind a minimum usage threshold (at least 3 sessions, at least 5 days since install). Track internally whether you've prompted in the last 60 days and skip if so, as a conservative inner guard. Never prompt after an error, a failed network call, or a permission denial.

**Real-world consequence:** Wasted quota (3 prompts per year) means you lose the ability to reach willing reviewers at the right moment. Low-quality prompt timing correlates with lower average ratings because the only users who rate are the ones just annoyed enough to tap 1 star.

---

## 28. Third-Party AI Data Sharing Without Consent (2026)

**Sending user content to a third-party AI provider (OpenAI, Anthropic, Google, any cloud LLM SDK) without disclosing it and getting explicit permission first.**

**Why it fails:** Apple's 2026 App Review Guidelines require that you clearly disclose where personal data will be shared with third parties — explicitly including third-party AI — and obtain the user's explicit permission before doing so. An app that silently pipes user text, photos, or documents to a cloud model is now a rejection cause, not just a privacy-policy footnote. This is distinct from the privacy nutrition label (item 22): the label is a static disclosure; this is a runtime consent requirement.

**Fix:** Before the first call that leaves the device for a third-party model, present a plain-language consent screen naming the provider and what is sent ("Your question is sent to OpenAI to generate a response"). Gate the cloud path behind that grant. This pairs naturally with an on-device-first architecture — run Apple Foundation Models or local logic by default, and treat the cloud as an explicit, consented upgrade (see `software-ios-ai-engine`). Keep the privacy nutrition label consistent with the disclosure.

**Real-world consequence:** Rejection under the AI-disclosure provisions. In the EU, undisclosed third-party AI processing is also a GDPR exposure.

---

## 29. AI Features Ignored in the Age Rating (2026)

**Setting the age rating from the app's static content while an AI assistant or chatbot can surface anything.**

**Why it fails:** Apple's 2026 age-rating system replaced 4+/9+/12+/17+ with **4+, 9+, 13+, 16+, 18+**, and now requires that AI/chatbot functionality be factored into the rating: a free-text AI surface can produce sensitive content the rest of the app never would. The updated age-rating questionnaire has been mandatory for every app since January 31, 2026 (developers who missed that date already had update submissions blocked) — this is now steady-state enforcement, not an upcoming deadline. An app that rates itself 4+ but ships an open chatbot is mis-rated.

**Fix:** When the app contains any generative or chatbot surface, answer the age-rating questionnaire for the *worst plausible* AI output, not the curated UI. Constrain the model (guided generation, safety prompts, refusal paths) if you need a lower rating, and re-answer the questionnaire after adding any AI feature. Treat the rating as a function of capability, not of the happy path.

**Real-world consequence:** A mis-rated AI app is a removal/recategorization risk and, in some regions, a regulatory one. Update submissions are blocked until the questionnaire is answered.

---

## 30. Shipping Without the iOS 26 SDK (in effect since April 28, 2026)

**Submitting a build compiled against an older SDK.**

**Why it fails:** Since **April 28, 2026**, iOS and iPadOS apps uploaded to App Store Connect must be built with the **iOS 26 SDK (Xcode 26 or later)** — this gate is now live, not upcoming; uploads built against older SDKs are rejected at upload, before review even begins. Current stable tooling has moved past this baseline (Xcode 26.6 as of mid-2026); WWDC26 (June 2026) previewed Xcode 27 / the iOS 27 SDK as a beta, so expect this cutover to repeat annually with each new SDK generation.

**Fix:** Keep CI and local builds on Xcode 26.x or later (verify the current stable point release each session) and re-verify before every submission — do not assume a build that passed six months ago still uses a qualifying SDK if the toolchain wasn't pinned. Building against the iOS 26 SDK also opts the app into Liquid Glass on stock chrome (see [ios26-liquid-glass.md](ios26-liquid-glass.md)) — verify the UI under the new material as part of any SDK bump, since chrome adopts glass automatically once you link the new SDK. Raising the *build* SDK does not force raising the *minimum deployment target*; keep supporting older OS versions if your user base needs it.

**Real-world consequence:** Upload rejection for any build compiled with a pre-iOS-26 SDK — the binary never reaches review. A surprise SDK bump also surfaces Liquid Glass regressions late if not verified deliberately.

---

## Pre-Submit Checklist

Run this before every App Store submission.

- [ ] ATT prompt is deferred behind at least one meaningful user action; custom pre-prompt screen explains value exchange
- [ ] Push notification permission is gated on a user action that has an obvious notification benefit
- [ ] All `NSPrivacy*UsageDescription` strings name the specific feature, not a generic purpose
- [ ] No paywall on first launch; value preview exists before any subscription gate
- [ ] Sign in with Apple implemented and at least as prominent as all other login options (Guideline 4.8)
- [ ] Demo account credentials in App Review notes are valid, region-independent, and tested on a fresh install
- [ ] No "placeholder," "TODO," "beta," or "test" strings visible anywhere in the app UI
- [ ] Privacy nutrition label audited against current SDK versions; proxy-verified network calls match declarations
- [ ] Fresh install tested on the smallest/lowest-RAM device your deployment target actually supports (verify against the current Apple lineup — iPhone SE was discontinued in Feb 2025) in a non-English locale with Dynamic Type Accessibility XL enabled
- [ ] All subscription copy (paywall screen, IAP product description, App Store listing) is consistent in price, duration, and entitlements
- [ ] App Store screenshots have populated UI state, device frames or context, and bold feature captions
- [ ] App Store preview video demonstrates core value within first 3 seconds with on-screen captions (no audio reliance)
- [ ] Keyword field: 100 chars, no spaces after commas, no duplicates with title/subtitle, no competitor names
- [ ] Background mode declarations in `UIBackgroundModes` audited — remove any mode not actively used
- [ ] `SKStoreReviewController.requestReview()` gated behind minimum session count, minimum days-since-install, and a genuine success moment
- [ ] Any third-party AI / cloud-LLM call is gated behind an explicit, named consent screen, and the privacy label matches (2026 AI-disclosure requirement)
- [ ] Age rating answered for the worst plausible AI/chatbot output, not the curated UI; questionnaire re-answered after adding any AI feature (4+/9+/13+/16+/18+ system)
- [ ] Build compiled with the iOS 26 SDK / Xcode 26 or later (mandatory for all uploads since April 28, 2026 — re-verify current CI toolchain, do not assume a stale pin still qualifies); Liquid Glass chrome re-verified after the SDK bump
