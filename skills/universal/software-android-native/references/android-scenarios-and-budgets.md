# Android Scenarios and Performance Budgets

Symptom-keyed recipes and the ANR/frame-budget arithmetic used when diagnosing jank, ANRs, release-only crashes, and platform migrations. Moved from the main SKILL.md; the decision core stays there.

## Contents

- [ANR and Frame Budget Arithmetic](#anr-and-frame-budget-arithmetic)
- [Scenarios](#scenarios)

## ANR and Frame Budget Arithmetic

Classify ANR type before selecting a timeout: use the canonical [runtime-debugging ANR table](../../software-android-runtime-debugging/references/performance-triage.md#anr-thresholds) and its linked Google documentation.

Foreground-service promotion failures are internal `ForegroundServiceDidNotStartInTimeException` crashes, separate from ANRs. Google requires `ServiceCompat.startForeground()` within a few seconds after `startForegroundService()`; a universal five-second threshold is unverified. Promote promptly before lengthy work. Source: [foreground-service troubleshooting](https://developer.android.com/develop/background-work/services/fgs/troubleshooting).

The nominal frame interval is `1000 ms / refresh rate`: approximately 16.67 ms at 60 Hz or 8.33 ms at 120 Hz. This is an arithmetic reference, not the app's entire available CPU budget. Recheck jank at the actual device rate with frame timing and Perfetto traces; emulator performance alone is insufficient.

## Scenarios

Recipes keyed to symptoms or migration moments. Each lists the shortest path to resolution using the patterns in [SKILL.md](../SKILL.md).

### S1 — Compose recomposition perf bug after Strong Skipping upgrade

1. Enable Compose compiler reports using `composeCompiler { reportsDestination = layout.buildDirectory.dir("compose_reports") }`.
2. Identify composables marked `unstable` in the report; focus on those receiving the full UI state object.
3. Split the monolithic state into `@Immutable` slices and hoist derived lists to `StateFlow` in ViewModel.
4. Replace `List<T>` params with `ImmutableList<T>` from `kotlinx-collections-immutable`.
5. Re-run the metrics; verify the hot composables are now marked `skippable`.
6. Compare Perfetto traces before and after on a real device. Baseline Profiles are runtime optimization inputs, not traces; use Macrobenchmark for repeatable timing.

### S2 — R8 stripping kotlinx-serialization classes

1. Reproduce in a release build: run `./gradlew :app:assembleRelease` and trigger the failing serialization path.
2. Check the R8 mapping file and logcat for `SerializationException: Serializer for class 'X' is not found`.
3. Inspect the merged consumer rules. The library bundles serializer rules; named companions require mode-specific additions from the [upstream Android guidance](https://github.com/Kotlin/kotlinx.serialization#android). Add only the rule needed by the reproducer.
4. Add a release-variant smoke test in CI that exercises every serialized entry point.
5. Verify the fixed APK with `adb install -r` and re-run the failing path end-to-end.

### S3 — Foreground service crash on API 35

1. Check the crash log for `ForegroundServiceStartNotAllowedException` or `MissingForegroundServiceTypeException`.
2. Declare `android:foregroundServiceType` in the `<service>` manifest element (e.g. `dataSync`, `mediaPlayback`).
3. Pass the matching `ServiceInfo.FOREGROUND_SERVICE_TYPE_*` flag to `startForeground()`.
4. Check the required type permissions and any permitted background-start exemption; use WorkManager for deferrable work. WorkManager foreground workers also obey foreground-service restrictions.
5. Test the actual background entry/trigger on an API 35 emulator or device; navigate away before triggering. Killing the process alone does not reproduce a background service launch.

### S4 — Predictive back gesture migration

1. On Android 16+ with `targetSdk` 36+, predictive-back system animations are enabled by default; legacy `onBackPressed()` and `KEYCODE_BACK` dispatch no longer occur. Remove a temporary `enableOnBackInvokedCallback="false"` opt-out after migration. See [API 36 behavior changes](https://developer.android.com/about/versions/16/behavior-changes-16#predictive-back).
2. Replace all `onBackPressed()` overrides with `OnBackPressedCallback` registered on `onBackPressedDispatcher`.
3. For Compose Navigation, confirm `NavHost` handles `OnBackPressedCallback` automatically; add explicit callbacks only for custom back logic.
4. Test with gesture navigation enabled on API 33+ device; verify animated back preview renders correctly.
5. Remove any legacy `KeyEvent.KEYCODE_BACK` handlers that now conflict with the new callback.

### S5 — Play Billing entitlement reconciliation

1. Initialize `BillingClient` as a Hilt singleton; connect in `Application.onCreate`.
2. On `BillingClient.BillingResponseCode.OK` after purchase, call the backend to verify the purchase token server-side before granting access.
3. Call `acknowledgePurchase()` within 3 days; unacknowledged purchases auto-refund.
4. Subscribe to `PurchasesUpdatedListener` and `queryPurchasesAsync(QueryPurchasesParams)` on app foreground to catch out-of-band purchases.
5. Handle `ITEM_ALREADY_OWNED` gracefully by querying existing entitlements rather than surfacing an error.
