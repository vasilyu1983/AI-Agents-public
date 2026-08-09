# Compose Debugging

## Table of Contents

- [Recomposition Tracking](#recomposition-tracking)
- [Stability Annotations](#stability-annotations)
- [Layout Inspector (Compose Mode)](#layout-inspector-compose-mode)
- [Compose Compiler Reports](#compose-compiler-reports)
- [Common Compose Runtime Issues](#common-compose-runtime-issues)
- [Compose + Navigation Debugging](#compose--navigation-debugging)
- [Compose 1.10.x Regressions](#compose-110x-regressions)
- [Off-main snapshot mutation (main-thread crash)](#off-main-snapshot-mutation-main-thread-crash)

## Recomposition Tracking

Jetpack Compose recomposes (re-executes composable functions) when state changes. Unnecessary recompositions degrade performance and can cause visible glitches.

**Layout Inspector (Android Studio)**: enable "Show Recomposition Counts" in the Compose tab. Each composable shows a recomposition count and skip count. High recomposition counts on stable-looking composables indicate a stability problem.

**Compose Compiler Metrics**: generate recomposition-relevant reports programmatically:

```kotlin
// In app/build.gradle.kts
composeCompiler {
    metricsDestination = layout.buildDirectory.dir("compose-metrics")
    reportsDestination = layout.buildDirectory.dir("compose-reports")
}
```

Build, then inspect the generated files in `app/build/compose-metrics/` and `app/build/compose-reports/`.

## Stability Annotations

The Compose compiler marks each class as **Stable** or **Unstable**. Unstable parameters force recomposition even when values have not changed.

- **Stable by default**: primitives, `String`, `enum`, `@Immutable` or `@Stable` annotated classes, and function types.
- **Unstable by default**: standard `List`, `Map`, `Set` (use `kotlinx.collections.immutable` for stable variants), classes with `var` properties, classes from external modules without Compose compiler analysis.

To fix unstable parameters:

1. Use `@Immutable` on data classes that are truly immutable.
2. Use `@Stable` on classes where the Compose compiler cannot infer stability.
3. Replace `List<T>` with `ImmutableList<T>` from `kotlinx-collections-immutable`.
4. Enable Compose compiler stability configuration file to mark external classes as stable.

## Layout Inspector (Compose Mode)

Android Studio's Layout Inspector has a Compose-specific mode:

- **Component tree**: shows the composable hierarchy, not the View hierarchy.
- **Parameters**: inspect the current parameter values for each composable at capture time.
- **Modifier chain**: view the full modifier chain applied to a composable in application order.
- **3D view**: rotate the layer view to identify overlapping composables or unexpected z-ordering.
- **Snapshot vs live**: live mode streams the tree; snapshot mode captures a single frame for inspection.

## Compose Compiler Reports

The compiler reports classify every composable and class:

- **restartable**: the function can be re-invoked when state changes (most composables).
- **skippable**: the function can skip recomposition if all parameters are stable and unchanged. Non-skippable functions always recompose.
- **stable / unstable**: parameter and class stability classification.

Look for composables that are **restartable but not skippable** — these recompose on every parent recomposition regardless of parameter changes. Fix by stabilizing their parameters.

## Common Compose Runtime Issues

**Modifier order matters**: `Modifier.clickable().padding()` has a different click target than `Modifier.padding().clickable()`. The clickable area includes the padding in the second form but not the first. When clicks seem to do nothing, check modifier order.

**`remember` vs `rememberSaveable`**: `remember` survives recomposition but not configuration changes (rotation). `rememberSaveable` survives both. Use `rememberSaveable` for user-facing state that should persist across rotation.

**`LaunchedEffect` key instability**: if the key parameter is unstable (e.g., a new list instance on every recomposition), the effect relaunches every recomposition. Use a stable key or `Unit` for one-shot effects.

**`derivedStateOf`**: use when a state value is computed from other state values and only a subset of changes should trigger recomposition. Without it, every upstream change triggers recomposition even when the derived value has not changed.

**Side effects in composition**: composition can run multiple times, in any order, and on any thread. Never perform I/O, network calls, or state mutation directly in a composable body. Use `LaunchedEffect`, `SideEffect`, or `DisposableEffect`.

**Previews do not run side effects**: `@Preview` composables do not execute `LaunchedEffect`, `SideEffect`, or `DisposableEffect`. If a preview looks wrong, confirm whether the composable depends on a side effect for its initial state.

## Compose + Navigation Debugging

**Route matching**: Compose Navigation uses string-based route matching. A typo in a route string causes silent navigation failure — no crash, just no navigation. Log the route at the `navigate()` call site and verify it matches the `composable("route")` declaration.

**NavBackStackEntry lifecycle**: each destination has its own `NavBackStackEntry` with its own `ViewModel` scope. Accessing a ViewModel from the wrong entry returns unexpected state. Use `hiltViewModel()` or `viewModel()` scoped to the correct entry.

**Deep link overlap**: if two destinations declare overlapping deep link patterns, the first match wins. Check `NavGraph` construction order when deep links route to unexpected destinations.

**Destination changed listener**: use `navController.addOnDestinationChangedListener` to log every navigation event during debugging. Remove it before release — it holds a reference to the NavController.

## Compose 1.10.x Regressions

Before treating any of the following as an app-level bug, check the installed Compose UI version. Several runtime races that looked like app-level problems were upstream bugs with version-specific fixes. Source: [Jetpack Compose release notes](https://developer.android.com/jetpack/androidx/releases/compose-ui).

| Symptom | Root cause | Fixed in |
|---------|-----------|----------|
| Crash with pausable composition animated inside `LookaheadScope` | Compose runtime regression in pausable composition interaction with `LookaheadScope` measurement pass | Compose UI 1.10.1 (2026-01-14) |
| Nested `Popup` placed at the screen's top-left instead of anchoring to its parent `Popup` | `PopupPositionProvider` received absolute screen coordinates for the anchor bounds instead of the parent-relative bounds; nested popups lost the anchor entirely | Compose UI 1.10.0 / 1.10.1 |
| `ConcurrentModificationException` inside `SnapshotStateObserver` while recording derived states | Reentrant modification race when derived-state recording triggered another derived-state read on the same observer | Compose UI 1.10.0-rc01 |

Triage order when you hit one of these:

1. Check `app/build.gradle.kts` (or the version catalog) for the Compose UI version actually resolving — `./gradlew :app:dependencies --configuration releaseRuntimeClasspath | rg compose-ui` gives the truth, not the BOM entry you think you wrote.
2. If below 1.10.1, upgrade and re-run the reproducing flow before changing app code.
3. If at or above 1.10.1 and the crash persists, it is not the upstream regression — route to app-level investigation: off-main snapshot mutation (see `software-android-native/references/compose-state-concurrency.md` → "Threading traps"), Strong Skipping instability, or a modifier-chain bug.

## Off-main snapshot mutation (main-thread crash)

`android.view.ViewRootImpl$CalledFromWrongThreadException: Only the original thread that created a view hierarchy can touch its views` in a Compose-only app usually means a `MutableStateFlow` backing UI state was mutated from `Dispatchers.IO` or `Dispatchers.Default` without switching back to the main dispatcher. On Compose surfaces this can also surface as `ConcurrentModificationException` inside `SnapshotStateObserver` (distinct from the 1.10.0-rc01 upstream race above, which is already fixed).

Triage:

1. Find the crashing frame's coroutine. `adb logcat` usually shows the `kotlinx.coroutines` dispatcher name in the stack.
2. Look for an `_uiState.value = ... .copy(...)` or `_state.emit(...)` call inside a `withContext(Dispatchers.IO) { ... }` block.
3. Refactor: keep the IO block pure (return a value), then assign `_uiState.value = copy(...)` on the resumed main context.
4. Verify composables collect via `collectAsStateWithLifecycle()`, not a raw `collect` inside `LaunchedEffect`.

Source: [developer.android.com/develop/ui/compose/state](https://developer.android.com/develop/ui/compose/state). See also [software-android-native/references/compose-state-concurrency.md](../../software-android-native/references/compose-state-concurrency.md) → "Threading traps: off-main snapshot mutation".
