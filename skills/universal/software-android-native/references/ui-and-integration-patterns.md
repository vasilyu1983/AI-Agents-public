# UI And Integration Patterns

Use this reference for specialized native Android implementation patterns that are too detailed for the main skill entrypoint: Compose patterns, adaptive layouts, backend integration gotchas, and Play Billing rules.

## Table of Contents

- [Quick Picks](#quick-picks)
- [Compose Patterns](#compose-patterns)
- [Adaptive Layout Patterns](#adaptive-layout-patterns)
- [Backend Integration](#backend-integration)
- [Google Play Billing Integration](#google-play-billing-integration)

## Quick Picks

Default API picks for Compose, billing, adaptive layout, and auth/push work (moved from the SKILL.md quick reference).

| Task | Default Picks | Notes |
|------|---------------|-------|
| **Compose patterns** | | |
| LazyColumn / LazyRow | Always provide `key` in `items(key = { it.id })` | Prevents recomposition bugs on list mutation |
| Canvas drawing | `Canvas(modifier) { drawScope -> ... }` with `DrawScope` | Use `drawLine`, `drawCircle`, `drawArc`, `drawPath` |
| Canvas gestures | `Modifier.pointerInput(Unit) { detectTapGestures / detectDragGestures }` | Compute hit targets from coordinates, not invisible tap areas |
| Type-safe navigation | `@Serializable` route classes + `NavHost` (type-safe routes since Navigation 2.8; consider Navigation 3 for scene-based adaptive layouts) | Compile-time route safety; replaces string-based routes |
| Animations | `animateFloatAsState`, `Animatable`, `InfiniteTransition` | Choose based on one-shot vs continuous vs interruptible |
| `derivedStateOf` | `remember { derivedStateOf { ... } }` | For computed state that depends on frequently changing sources |
| Side effects | `LaunchedEffect`, `DisposableEffect`, `SideEffect` | `LaunchedEffect(key)` for coroutine work; `DisposableEffect` for cleanup |
| Modifier order | Padding before background vs after changes result | Modifier chain is sequential; order is layout-significant |
| `Modifier.testTag` | `Modifier.testTag("submit_button")` | Required for Compose test node finders |
| Snackbar | `SnackbarHostState` + `SharedFlow` from ViewModel | Collect events in `LaunchedEffect`; never use `Toast` for important feedback |
| **Billing & payments** | | |
| BillingClient | A Play Billing Library major that Play still accepts (Play sets a minimum PBL version for new apps and updates, with a deadline) | Initialize in `Application.onCreate` or Hilt singleton; verify current minimum at [developer.android.com/google/play/billing/release-notes](https://developer.android.com/google/play/billing/release-notes) |
| Acknowledge purchases | `acknowledgePurchase()` within 3 days | Unacknowledged purchases auto-refund after 3 days |
| Subscription offers | `ProductDetails.subscriptionOfferDetails` | Base plan, offer phases (free trial, introductory price) |
| Promotional offers | Developer-determined offers in Play Console | Configure offer eligibility; apply via `ProductDetailsParams.setOfferToken(offerToken)` from `subscriptionOfferDetails` — `SubscriptionUpdateParams` is for plan changes (upgrade/downgrade) on an existing subscription |
| Consumables | `consumeAsync()` after backend confirms | Prevents re-granting; consume only after server receipt |
| **Adaptive layouts** | | |
| Window size classes | `currentWindowAdaptiveInfo(supportLargeAndXLargeWidth = true).windowSizeClass` from Material3 adaptive | Branch with `isWidthAtLeastBreakpoint(...)`; opt in to large/extra-large widths and test resize transitions |
| List-detail pane | `ListDetailPaneScaffold` (Material3 adaptive) | Canonical two-pane pattern for tablets and foldables |
| Navigation suite | `NavigationSuiteScaffold` | Auto-switches between bottom nav, rail, and drawer by size class |
| Foldable support | `WindowInfoTracker` (Jetpack Window) | Detect fold posture, hinge bounds; adapt layout for table-top mode |
| **Auth & push** | | |
| Credential Manager | `CredentialManager` API (Jetpack) | Unified passkeys, passwords, and federated sign-in |
| Biometric auth | `BiometricPrompt` (AndroidX) | `canAuthenticate()` check first; `BIOMETRIC_STRONG` for crypto |
| Push notifications | FCM (`FirebaseMessaging`) | `onNewToken` for registration; `onMessageReceived` for data messages |
| Notification channels | `NotificationChannel` (API 26+) | Must create before posting; group related channels with `NotificationChannelGroup` |
| Deep links | Compose Navigation deep links | `navDeepLink { uriPattern = "app://..." }` on route; App Links require `assetlinks.json` |

## Compose Patterns

Lessons from production Compose-based apps:

- Always provide stable keys in `LazyColumn` and `LazyRow` item blocks. Mutable lists without stable keys cause broken local state and wrong recomposition.
- Use `rememberSaveable` for user input, dialog state, and scroll position; use `remember` for values that can be recomputed safely.
- Avoid allocating new lambdas, lists, or maps in composable scope when they can be hoisted or remembered.
- Use `Canvas {}` with `DrawScope` for custom drawing and layer calls in a fixed order: background, grid, data, labels, overlays.
- Canvas does not own gestures directly. Use `pointerInput` and compute hit targets from geometry.
- Reach for `Layout` or `SubcomposeLayout` only when standard containers cannot express the arrangement.
- Match animation tool to intent: `animate*AsState` for one-shot values, `Animatable` for interruptible coroutine-driven motion, `InfiniteTransition` for loops.
- Use `derivedStateOf` for computed values that depend on frequently changing state but should not trigger downstream recomposition on every update.
- Use `LaunchedEffect`, `DisposableEffect`, and `SideEffect` correctly instead of launching coroutines directly in composable scope.
- Modifier order is part of layout semantics. Document it when the order is non-obvious.
- Add `Modifier.testTag` where tests need stable selectors.
- Prefer `SnackbarHostState` plus a one-shot event flow over `Toast` for actionable feedback.
- Use `collectAsStateWithLifecycle()` for ViewModel `StateFlow` collection.

## Adaptive Layout Patterns

Use [window size classes](https://developer.android.com/develop/ui/compose/layouts/adaptive/use-window-size-classes) from the current app window, not device-type heuristics.

- Use `WindowSizeClass` as the default breakpoint layer for phone, tablet, and foldable branching.
- `ListDetailPaneScaffold` is the canonical two-pane pattern for list-detail layouts.
- `NavigationSuiteScaffold` is the default adaptive navigation shell because it chooses bottom bar, rail, or drawer automatically.
- Use `WindowInfoTracker` to adapt for fold posture and hinge bounds on foldables.
- Keep tablet and foldable previews next to phone previews so adaptive behavior is visible during development.
- Use `DeviceConfigurationOverride` in Compose tests when you need tablet-like geometry without a physical device.

## Backend Integration

- Firebase Auth plus Supabase is a valid split when Firebase owns identity and Supabase owns data plus RLS.
- Avoid Retrofit `baseUrl` path duplication when the base already includes a version segment.
- Prefer Room `@Upsert` over separate insert/update methods where the entity may or may not exist yet.
- Treat server truth as primary for onboarding or entitlement state. Local cache is only fallback when offline.
- `SharedPreferences` is device-scoped, not user-scoped. Clear auth-coupled flags on sign-out.
- Prefer Credential Manager over legacy sign-in APIs for passkeys, passwords, and federated identity.
- Use `BiometricPrompt` for sensitive confirmation flows and gate it with `canAuthenticate`.
- Use the official `supabase-kt` client when Supabase is part of the stack.
- Handle backend 404 or 401 empty-resource responses as explicit empty state when that is the product contract, not always as user-visible error.

## Google Play Billing Integration

- Initialize `BillingClient` once and own the connection lifecycle deliberately.
- Do not acknowledge purchases before backend receipt verification completes. Unacknowledged purchases auto-refund after three days.
- Consume consumables only after the backend confirms grant success.
- If web billing uses Stripe and Android uses Play Billing, add a `billing_platform` guard to prevent double charging.
- Wire Real-Time Developer Notifications and verify them against the Google Play Developer API.
- Use `ProductDetails.subscriptionOfferDetails` plus `offerToken` to drive base-plan and offer selection.
- Keep the billing library on the current supported major version and re-check migration notes before changing setup code. Google sets a minimum Play Billing Library major version for new apps and updates, with a deadline and sometimes an extension. Read the current minimum and deadline at [developer.android.com/google/play/billing/release-notes](https://developer.android.com/google/play/billing/release-notes) and the deprecation FAQ before assuming an older major is still accepted.
