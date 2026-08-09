# UI And Integration Patterns

Use this reference for specialized native iOS implementation patterns that are too detailed for the main skill entrypoint: Canvas and gesture lessons, immersive visualization screens, backend integration gotchas, and StoreKit 2 billing rules.

## Table of Contents

- [Canvas And Gesture Patterns](#canvas-and-gesture-patterns)
- [Immersive Visualization Screens](#immersive-visualization-screens)
- [Backend Integration](#backend-integration)
- [StoreKit 2 Billing Integration](#storekit-2-billing-integration)

## Canvas And Gesture Patterns

Lessons from production Canvas-based data visualizations:

- Catmull-Rom spline for smooth curves through data points. Use alpha `0.5` to prevent cusps and duplicate first and last points for boundary interpolation.
- `DragGesture(minimumDistance: 0)` is the tap-or-drag default for Canvas. Inside a `ScrollView`, use `.simultaneousGesture` plus axis locking so vertical scroll still passes through.
- Map gesture location to data index with the same coordinate math used for drawing. Canvas size is not available in gesture handlers, so use the known frame height or wrap in `GeometryReader`.
- Keep geometry constants in the visualization domain. Do not move them into the app design system.

## Immersive Visualization Screens

Use these rules for full-screen data or spatial surfaces:

- Use `ZStack { background; scene; controls; persistentSheet }` instead of wrapping the whole screen in cards or scroll containers.
- Drive persistent sheet detents explicitly and enable `.presentationBackgroundInteraction(.enabled(upThrough: .medium))` so the visualization stays interactive while the sheet is visible.
- Put controls in the layout, not as overlays on top of the Canvas. Overlay controls clip behind glyphs and labels.
- Use native controls such as segmented `Picker` and `Menu` for mode switches and overflow actions rather than custom material-backed button strips.
- Selection changes should update both the selected entity and the panel detent in the same animated transaction.
- When visualization, control strip, and detail panel share state, extract that state into an `@MainActor @Observable` class owned by the screen.

## Backend Integration

- JWT auth on Next.js API routes often defaults to cookie-backed session auth. Native iOS Bearer-token clients need explicit JWT support and usually an admin-scoped Supabase client on the backend path.
- Shared backend helper functions that create their own session-scoped client break JWT-native flows. Let those helpers accept an injected client.
- Avoid API base URL duplication when the base path already includes `/api`.
- Use upsert semantics for rows that may not exist yet.
- Treat server truth as primary for onboarding or entitlement state; local cache is only fallback when offline.
- `UserDefaults` is device-scoped, not user-scoped. Clear auth-coupled cache values on sign-out.
- For native-owned onboarding, keep OAuth redirect paths on the backend aligned with native navigation so a web onboarding route does not flash in `ASWebAuthenticationSession`.
- If the app offers any third-party social login, Sign in with Apple is required for App Store approval.
- Apple only sends the user’s full name on the first authorization; persist it immediately.
- Use `nonisolated` delegate methods plus `MainActor.assumeIsolated` for delegate protocols that are called on the main thread but not annotated `@MainActor`.
- Prefer OTP codes over magic links for native flows where notification auto-fill is more reliable than browser deep-link routing.
- Supabase email templates can carry both magic-link and OTP content in the same message.

## StoreKit 2 Billing Integration

- The signed JWS lives on `VerificationResult<Transaction>`, not on `Transaction`. Capture it before unwrapping.
- Do not call `transaction.finish()` before the backend confirms sync. Unfinished transactions are the retry mechanism after crashes.
- If web billing uses Stripe and native billing uses StoreKit, add a `billing_platform` guard to prevent double-charging and return that platform state to the app.
- App Store Server Notifications v2 should be wired and verified server-side; always return HTTP 200 after processing or durable enqueue.
- Use `product.displayPrice` for native price rendering instead of hardcoded strings.
- Referral or reward credits that exist in Stripe but not in Apple billing require a native redemption flow, typically via StoreKit promotional offers.
- Promotional offer signing is server-side only. The iOS app should fetch a signed payload from the backend and never hold the `.p8` signing key.
