# Compose Runtime Debugging

## Recomposition or Missed Updates

Use Layout Inspector's recomposition/skip counts while reproducing the exact interaction, then inspect the compiler reports from the resolved build:

```kotlin
composeCompiler {
    metricsDestination = layout.buildDirectory.dir("compose-metrics")
    reportsDestination = layout.buildDirectory.dir("compose-reports")
}
```

A count alone does not prove a performance problem: correlate the costly work with a frame trace. With [Strong Skipping](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping), restartable functions can skip even with unstable parameters. Unstable inputs use identity comparison; stable ones use `equals`. Mutable collections changed in place can hide updates; new unstable instances can prevent skipping. Check the resolved compiler mode and actual state reads before adding `@Stable` or `@Immutable`, which promise a contract rather than repairing mutation. Implementation patterns belong in [software-android-native](../../software-android-native/SKILL.md).

## Interactions and Effect Lifetime

| Runtime symptom | Check |
|---|---|
| Tap area differs from visible padding | `clickable().padding()` includes padding in the tap area; `padding().clickable()` leaves it outside. Inspect the full chain and overlapping nodes. [Modifier order](https://developer.android.com/develop/ui/compose/modifiers) |
| Effect repeats after an update | Compare the effect key values: keys use equality, so a new equal list does not automatically restart the effect. `Unit` runs once per entry into composition, not once per app lifetime. [Effects](https://developer.android.com/develop/ui/compose/side-effects) |
| State disappears on rotation or process recreation | Inspect its owner and saved-state support; an in-memory `remember` value survives recomposition only. Route implementation to android-native. |
| Preview differs from the device | Previews lack normal app wiring and may restrict network/file access; inject sample state and prove behavior on the device. Do not assume all effect APIs are disabled. |

## Navigation Runtime Proof

Discover whether the app uses string routes, Navigation's typed routes, or Navigation 3 before choosing instrumentation. Log the requested destination, arguments and observed back stack; a bad route can throw instead of silently doing nothing. Check the lifecycle/ViewModel owner for the actual entry. For unexpected deep links, inspect the matched URI pattern and destination rather than assuming declaration order decides every match.

## Upstream Regressions

Match the exact resolved `compose-ui`/runtime/compiler versions and crashing frames to [Compose UI release notes](https://developer.android.com/jetpack/androidx/releases/compose-ui). Use a minimal reproducer for nested `Popup`, pausable composition/`LookaheadScope`, or `SnapshotStateObserver` failures; a symptom match alone does not prove the same upstream defect. Test the documented fix version before changing app coordinates or state ownership. Keep any fix boundary in the incident evidence, rather than calling a historical version current.

## View Threading and Snapshot Races

`ViewRootImpl$CalledFromWrongThreadException` identifies a View operation performed off its owning thread. Find that call in the stack, including `AndroidView`, listeners and platform APIs. [StateFlow operations are thread-safe](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/); writing a `MutableStateFlow` on `Dispatchers.IO` is not sufficient evidence for this exception.

For `SnapshotStateObserver` concurrent-modification failures, distinguish an upstream race from writes to Compose snapshot state and mutable objects shared across threads. Reduce the state-write path and ownership boundary; if a View mutation is involved, dispatch that operation to the main thread. Lifecycle-aware collection does not make the producer's View operations thread-safe. See [android-native's threading guidance](../../software-android-native/references/compose-state-concurrency.md).
