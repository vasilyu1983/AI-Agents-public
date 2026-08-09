# UI And Integration Patterns

Use this reference for specialized native Android implementation patterns that are too detailed for the main skill entrypoint: Compose patterns, adaptive layouts, backend integration gotchas, and Play Billing rules.

## Table of Contents

- [Compose Patterns](#compose-patterns)
- [Adaptive Layout Patterns](#adaptive-layout-patterns)
- [Backend Integration](#backend-integration)
- [Google Play Billing Integration](#google-play-billing-integration)

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
- Keep the billing library on the current supported major version and re-check migration notes before changing setup code. As of 2026-07-11, Play Billing Library v9.x is current (v9.0.0 shipped 2026-05-19) and Google requires all new apps/updates to be on v8+ by 2026-08-31 (extension to 2026-11-01); verify the live minimum at [developer.android.com/google/play/billing/release-notes](https://developer.android.com/google/play/billing/release-notes) before assuming v7 or earlier is still acceptable.
