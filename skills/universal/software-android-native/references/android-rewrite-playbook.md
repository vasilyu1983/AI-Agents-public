# Android Rewrite Playbook

Use this reference when the user is rewriting an existing app to modern native Android. Treat this as the repo default migration shape, not as a Google-mandated architecture.

## Rewrite stance

- Prefer an incremental rewrite over a big-bang replacement.
- Keep one active migration brief with:
  - target minimum API level
  - Kotlin / Android Studio / AGP baseline
  - scope in and scope out
  - release blockers
  - parity exceptions accepted by the user
- Rewrite vertical slices, not disconnected utility layers.

## Safe slice order

1. App shell
   Application class, Hilt setup, navigation graph, Gradle configuration, signing, launch path
2. Session and app state
   auth, onboarding gating, permissions, shared app state (DataStore or SharedPreferences migration)
3. Core feature slices
   one user-visible flow at a time
4. Integration surfaces
   FCM, deep links, WorkManager, analytics, Play Billing, support SDKs
5. Release-only surfaces
   data safety declarations, target SDK compliance, ProGuard/R8, Play Integrity, accessibility, store metadata

## Acceptance criteria per slice

- Builds in the intended configuration (`assembleDebug` or `assembleRelease`).
- Installs and launches on the chosen emulator or device.
- The rewritten user flow works end-to-end for the slice.
- Targeted automated tests exist or were intentionally deferred with a reason.
- New data safety / target SDK / permissions implications are recorded.
- Known parity gaps are explicit.

## Evidence bundle

Require a compact evidence bundle after each slice:

- build result
- install and launch result
- screenshot or UI proof for user-facing changes
- targeted test result
- changed behavior summary
- residual risk and next slice

## Architectural defaults

Use these as repo defaults for low-ambiguity rewrites:

- Compose-first UI
- Views interop only where needed
- ViewModel + StateFlow for UI-facing state
- Hilt for dependency injection
- Room + KSP for local persistence
- Kotlin Coroutines for async work
- feature-oriented module boundaries only when they reduce coupling; do not create module sprawl without a concrete need

## Java-to-Kotlin migration notes

- Convert one file at a time using Android Studio's built-in Java-to-Kotlin converter (`Code > Convert Java File to Kotlin File`).
- Review converter output: it often produces non-idiomatic Kotlin (unnecessary `!!`, `var` where `val` works, missing data classes).
- Do not bulk-convert entire packages without building and testing after each file.
- Interop: Kotlin files can call Java and vice versa. Keep both languages working during migration — do not block features on full conversion.

## Views-to-Compose migration notes

- Use `ComposeView` in existing XML layouts to embed Compose in Views-based screens.
- Use `AndroidView` in Compose to embed existing custom Views (MapView, AdView, legacy widgets).
- Migrate one screen at a time: replace the Activity/Fragment content with a Compose `setContent` block or embed `ComposeView` in the existing layout.
- Navigation: bridge Compose Navigation and Fragment-based navigation using `NavHostFragment` alongside Compose `NavHost` during transition. Do not maintain two parallel navigation graphs long-term.

## Avoid

- Rewriting multiple feature slices before one slice is fully validated.
- Migrating state model, navigation, persistence, and networking all at once without a feature boundary.
- Treating emulator-only proof as complete release proof.
- Hiding compatibility gaps behind "later cleanup" with no owner or end condition.
- Bulk Java-to-Kotlin conversion without per-file validation.
