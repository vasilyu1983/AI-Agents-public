# Compose, StateFlow, and Kotlin Coroutines

This reference mixes platform-backed defaults with explicit repo defaults chosen to reduce ambiguity for agents.

## Table of Contents

- [Verified platform defaults](#verified-platform-defaults)
- [Repo defaults for new API 28+ work](#repo-defaults-for-new-api-28-work)
- [Safe defaults](#safe-defaults) — state, concurrency, UI boundaries, Canvas/drawing, visualization state ownership, Material Design icons, dual-pane patterns, score/progress patterns
- [Kotlin 2.x / K2 compiler transition](#kotlin-2x--k2-compiler-transition)
- [Testing defaults](#testing-defaults)
- [Avoid](#avoid)
- [Kotlin Anti-Patterns (K1-K8)](#kotlin-anti-patterns-k1-k8)
- [Backend Integration: Polymorphic and Tier-Gated DTOs](#backend-integration-polymorphic-and-tier-gated-dtos) — GatedOr, lenient deserialization, response wrappers
- [Compose stability pitfalls](#compose-stability-pitfalls)
- [Type naming conflicts](#type-naming-conflicts)

## Verified platform defaults

- Jetpack Compose is the primary Android declarative UI framework.
- ViewModel + StateFlow is the current recommended state management pattern for Android.
- Kotlin Coroutines with Flow is the current async model for structured async work on Android.
- Android local-test guidance uses [JUnit 4](https://developer.android.com/training/testing/local-tests); `createComposeRule()` is a JUnit 4 rule. JUnit 5 requires verified community integration. Use Turbine for Flow assertions on either.
- Compose Testing APIs are the preferred UI test framework for Compose screens.

## Repo defaults for new API 28+ work

- Prefer Jetpack Compose for new screens.
- Prefer ViewModel + `StateFlow` for new UI-facing state.
- Keep UI state updates on the main thread via `collectAsStateWithLifecycle`.
- Prefer `@HiltViewModel` for ViewModel creation with constructor injection.
- Prefer explicit dependency flow over hidden global state or service locators.

## Safe defaults

### State

- local transient view state -> `remember { mutableStateOf(...) }`
- survived configuration change state -> `rememberSaveable { mutableStateOf(...) }`
- shared screen state -> `ViewModel` + `StateFlow` exposed via `collectAsStateWithLifecycle`
- shared dependency or scoped state -> Hilt `@Inject` in ViewModel

Avoid introducing `LiveData` in new Compose code unless the app still supports older baselines or already standardizes on it.

### Concurrency

- prefer `viewModelScope.launch { }` for ViewModel-scoped coroutine work
- prefer `lifecycleScope.launch { }` only in Activity/Fragment when ViewModel is not appropriate
- use `withContext(Dispatchers.IO)` for blocking I/O (network, disk, database)
- use `withContext(Dispatchers.Default)` for CPU-bound work (JSON parsing, sorting)
- prefer `Mutex` or `Channel` over `@Synchronized` for coroutine-safe shared mutable state
- check `isActive` or use `ensureActive()` in long-running loops
- prefer structured concurrency: let child coroutines inherit the parent scope

### UI boundaries

- `MutableStateFlow.value` assignment is itself thread-safe from any dispatcher; the hazard is a non-atomic read-modify-write (`value = value.copy()`) racing under concurrent writers — use `update { }` instead. Keep Compose snapshot-state (`mutableStateOf`) writes on the main thread by convention
- collecting a `StateFlow` in Compose must happen on the main thread (`collectAsStateWithLifecycle()`)
- keep networking and storage layers testable and non-UI-aware
- map low-level exceptions into UI-safe sealed class states before emitting to the UI

### Canvas and custom drawing

- use Compose `Canvas` for custom data visualizations that standard composables cannot express (chart wheels, radar charts, geometric overlays)
- Canvas renders all drawing operations through `DrawScope`, which provides `drawLine`, `drawCircle`, `drawArc`, `drawPath`, `drawRect`, `drawOval`, `drawImage`, `drawText`
- structure complex Canvas views as sequential layer functions: each receives `DrawScope` + shared geometry
- Canvas cannot handle gestures directly — attach gesture modifiers to the Canvas composable:
  - `Modifier.pointerInput(Unit) { detectTapGestures { offset -> computeHitTarget(offset) } }`
  - `Modifier.pointerInput(Unit) { detectDragGestures { change, dragAmount -> ... } }`
  - Combine with `HapticFeedback` via `LocalHapticFeedback.current` for boundary-crossing feedback
  - For simple cases, invisible `Box` tap targets work too, but coordinate math scales better for dense layouts (Gantt charts, data grids)
- use `drawContext.canvas.nativeCanvas` with `android.graphics.Paint` only when `DrawScope` lacks a needed feature (e.g., complex text drawing with `StaticLayout`)
- prefer `drawWithCache` for expensive Path calculations that should not recompute on every draw
- animate Canvas content via `Animatable` or `InfiniteTransition` driving state: the Canvas redraws when state changes

### Text in Canvas

- Use `drawText(textMeasurer, text, topLeft)` with a `TextMeasurer` obtained from `rememberTextMeasurer()`
- Measure text size with `textMeasurer.measure(text, style)` before drawing to position accurately
- For numeric labels in Canvas, avoid locale formatting issues by using string conversion explicitly

### Visualization state ownership

Interactive visualization views (Canvas charts, 3D renderers, map views) need a deliberate choice about where zoom, pan, and drag state lives:

| Interaction model | State pattern | Rationale |
|---|---|---|
| **Inspect a diagram** (chart wheel, radar chart) | ViewModel `StateFlow` collected in Composable | Controls strip reads/writes same state via ViewModel actions. No latency concern for subtle zoom/pan. |
| **Custom GL/SurfaceView** (3D scene) | View-internal state + callback to ViewModel | The native view drives rendering directly for smooth 60fps, then reports the final value back via callback. ViewModel can reset or read. |
| **Navigate spatial terrain** (maps, MapView) | View-internal state | Continuous pinch-zoom and pan need zero-latency gesture response. A ViewModel round-trip adds perceptible lag during spatial navigation. |

Decision checklist:
- Does the controls strip need to read or write zoom/pan? -> ViewModel `StateFlow`
- Does the visualization use a custom View with its own gesture handling? -> callback pattern
- Is the interaction continuous spatial navigation (like a map)? -> internal state

### Material Design icons for domain visuals

- prefer Material Icons and Material Symbols over custom Canvas drawing when a symbol exists for the concept
- use `Icons.Filled`, `Icons.Outlined`, `Icons.Rounded` from `androidx.compose.material.icons`
- for extended icon sets, add `material-icons-extended` dependency but be aware of APK size impact — use R8 to tree-shake unused icons
- reserve custom Canvas drawing for visualizations that have no icon equivalent (radar charts, gauge needles, domain-specific diagrams)

### Dual-pane patterns with tabs or chips

- use `@Composable` with `TabRow` or `FilterChip` row to switch between two dashboard views
- both views read from the same data source (no separate API calls)
- shared elements (quick links, summary card) render outside the conditional, after both view blocks
- name modes by function ("Overview" / "Details"), not by implementation ("List" / "Canvas")
- `LazyColumn` for both views — not `RecyclerView` in Compose, which breaks interop patterns

## Kotlin 2.x / K2 compiler transition

- Prefer Kotlin 2.x with K2 compiler for new Android projects where all dependencies support it.
- K2 brings faster compilation, improved type inference, and better IDE performance.
- Verify Compose compiler compatibility with K2: Since Kotlin 2.0, apply `org.jetbrains.kotlin.plugin.compose` at the Kotlin version; the compiler ships with Kotlin but still requires this Gradle plugin. See the [migration guide](https://kotlinlang.org/docs/compose-compiler-migration-guide.html).
- Re-check dependency readiness before enabling K2 — some annotation processors (especially KAPT-based) may need migration to KSP.

## Testing defaults

- use Android-supported JUnit 4; select JUnit 5 only after verifying the community runner/plugin and device-test integration
- use Turbine (`app.cash.turbine`) for `StateFlow` and `Flow` assertion in tests
- use Compose Testing APIs (`createComposeRule()`, `onNodeWithTag`, `onNodeWithText`, `performClick`, `assertIsDisplayed`) for UI tests
- keep Espresso for Views-based screens and legacy test suites
- use Robolectric for tests that need `Context` without an emulator
- use `kotlinx-coroutines-test` (`runTest`, `TestDispatcher`, `advanceUntilIdle`) for coroutine timing control

## Avoid

- mixing multiple state patterns (LiveData + StateFlow + mutableStateOf) in one new feature without a reason
- using `Thread.sleep` or `delay` in production code when a state-based readiness check exists
- hiding coroutine cancellation or exception warnings instead of resolving them
- using `GlobalScope.launch` — prefer `viewModelScope` or a custom `CoroutineScope` with explicit lifecycle management

## Kotlin Anti-Patterns (K1-K8)

Review these lifecycle and state ownership hazards in new code.

| # | Anti-pattern | Why it bites | Better default |
|---|-------------|-------------|----------------|
| K1 | `GlobalScope.launch { ... }` | Marked `@DelicateCoroutinesApi`; It has no owning Job and screen teardown does not cancel its work; cancellation must be explicit. Legitimate app-lifetime use requires deliberate opt-in, not an assumed phase-out. | `viewModelScope`, `lifecycleScope`, or an injected `CoroutineScope` parented to a `SupervisorJob` you own. |
| K2 | Passing an external `Job` into `launch(externalJob)` to "inherit" cancellation | Overrides the scope's job, becomes the parent, and breaks structured concurrency. Cancellation of the scope no longer propagates. Recent IntelliJ releases flag this with a coroutine inspection. | Never pass `Job` as a context argument. Use a child scope or a `SupervisorJob` explicitly scoped to the lifecycle you want. |
| K3 | `LiveData` + `observeAsState` in new Compose code | Adds a second observation model when the feature otherwise uses Flow; this alone does not imply worse recomposition or backpressure. | `StateFlow` + `collectAsStateWithLifecycle()` for new code. Keep LiveData only for legacy Views screens still on it. |
| K4 | Nullability as the primary way to model "loading" / "error" / "success" | Forces every call site to branch on `null` and loses type information about why the value is absent. | Sealed class / sealed interface: `Idle` / `Loading` / `Success(data)` / `Error(message, cause)` with an exhaustive `when`. Kotlin's compiler warns on missing branches when a new state is added. |
| K5 | Keeping `kapt` on Kotlin 2.x annotation processors | Do not assume processor compatibility across Kotlin/AGP upgrades; check the processor and build-plugin migration notes. | Migrate to KSP2 (K2-compatible). Hilt, Room, and Moshi-codegen all support KSP2; verify current support status in each library's release notes. |
| K6 | Treating `StateFlow.value = copy(field = new)` as free | StateFlow conflates equal values; for emitted changes, unstable Compose parameters use identity and stable ones use equality. Inspect consumers before blaming allocation alone. | Split state into logical slices, hoist derived lists, and prefer primitives or `@Immutable` sub-objects as composable parameters. |
| K7 | Filtering or sorting lists inside a composable body | Repeated work can allocate a new list; unstable downstream parameters then use identity. Whether a consumer skips depends on its parameters and stability. | Compute in ViewModel or use `remember(source, filters) { ... }`. Use `derivedStateOf` when inputs change more often than the derived result, not for every transformation. |
| K8 | `runBlocking { ... }` in production code paths (outside `main()` and tests) | Blocks the calling thread; on the main thread it freezes the UI and can ANR; in library code it defeats structured concurrency. | Make the function `suspend` and let the caller pick the scope. |

## Backend Integration: Polymorphic and Tier-Gated DTOs

### The Problem

Backend APIs often return polymorphic responses where a field can be either real data OR a gated placeholder (e.g., `{ "gated": true, "teaser": {...} }` for free-tier users). Strict Kotlin deserialization fails the ENTIRE response when ANY field has a type mismatch — even optional fields inside nested data classes.

### GatedOr<T> Sealed Class

For fields that can be either real data or a gated placeholder:

```kotlin
@Serializable
sealed class GatedOr<out T> {
    @Serializable
    data class Data<T : @Serializable Any>(val value: T) : GatedOr<T>()

    @Serializable
    data object Gated : GatedOr<Nothing>()

    val valueOrNull: T? get() = (this as? Data)?.value
    val isGated: Boolean get() = this is Gated
}
```

Usage with KotlinX Serialization custom serializer or by decoding with `try/catch` per field.

### Lenient Deserialization with KotlinX Serialization

Configure the JSON instance for tolerant decoding:

```kotlin
val json = Json {
    ignoreUnknownKeys = true
    coerceInputValues = true    // null -> default for non-null fields
    isLenient = true
    explicitNulls = false       // missing keys -> null for nullable fields
}
```

### Response Wrapper Pattern

Backend APIs often wrap data in a response object. Do not decode the inner type directly:

```kotlin
// Wrong — assumes flat response
val reading: DailyReading = api.getDailyReading(sign)

// Right — decode the wrapper first
val response: DailyReadingResponse = api.getDailyReading(sign)
val reading = response.data
```

### Common Decode Failures

| Symptom | Cause | Fix |
|---------|-------|-----|
| `JsonDecodingException` on one field kills entire response | One nested field has wrong type | Use `ignoreUnknownKeys` + per-field `try/catch` |
| Nullable field crashes instead of becoming null | Field present but type mismatches | `coerceInputValues = true` + `explicitNulls = false` |
| Gated fields crash free-tier users | Backend sends `{gated: true}` instead of data | Use `GatedOr<T>` |
| Moshi `@Json` name mismatch | JSON key differs from Kotlin property name | Use `@SerialName` with KotlinX or `@Json(name=)` with Moshi |

### API Error Handling for Empty States

Backend may return 404/401 when a resource does not exist. Handle as empty state:

```kotlin
} catch (e: HttpException) {
    if (e.code() == 404) {
        _uiState.value = UiState.Empty
        return
    }
    _uiState.value = UiState.Error(e.message())
}
```

## Compose stability pitfalls

### @Immutable and @Stable annotations

- The Compose compiler treats parameters as stable or unstable to decide whether to skip recomposition.
- Standard Kotlin `data class` with only `val` primitive/String fields is automatically stable.
- Data classes with `List`, `Map`, `Set`, or other collection types are UNSTABLE by default because Kotlin collections are interfaces that could be mutable at runtime.
- Fix: annotate with `@Immutable` for truly immutable classes, or use `kotlinx.collections.immutable` (`ImmutableList`, `PersistentList`).

```kotlin
// Unstable — List is a mutable interface
data class UserProfile(val name: String, val tags: List<String>)

// Stable — ImmutableList is guaranteed immutable
@Immutable
data class UserProfile(val name: String, val tags: ImmutableList<String>)
```

### Compose compiler metrics

- Generate stability reports: add to `build.gradle.kts`:
  ```kotlin
  composeCompiler {
      reportsDestination = layout.buildDirectory.dir("compose_metrics")
      metricsDestination = layout.buildDirectory.dir("compose_metrics")
  }
  ```
- Check `*-composables.txt` for `restartable` vs `restartable skippable` — non-skippable composables recompose on every parent recomposition.
- Match stability findings to measured hot paths before optimizing them.

### Lambda stability

- With Strong Skipping, lambdas in composable functions are remembered even with unstable captures. Outside that boundary, stabilize callback identity only where measurement requires it; include changing captures in manual `remember` keys.

### Strong Skipping Mode (Kotlin 2.x)

Strong Skipping Mode is enabled by default since Kotlin 2.0.20. It changes the stability contract in two ways that matter for day-to-day code:

1. **Unstable params are now compared by instance identity.** Under the old rules, any composable with an unstable parameter was forced to recompose every time its parent recomposed. Under Strong Skipping, such a composable is still restartable but can skip if the incoming unstable parameter is the **same reference** as the previous invocation. This means stability still matters, but identity matters too.
2. **Lambdas inside `@Composable` functions are auto-memoized.** The compiler remembers lambdas keyed by their captures: unstable captures use identity, stable ones use equality.

The new footguns:

- **Fresh instances can defeat skipping for unstable consumers.** Equal StateFlow values are conflated; emitted changes are compared by identity only for unstable Compose parameters. When metrics show unrelated slices recomposing, split the state:
  ```kotlin
  // Before: one big state class
  data class ScreenState(val header: HeaderState, val items: List<Item>, val footer: FooterState)

  // After: hoist slices so consumers take only what they need
  class ScreenVm : ViewModel() {
      val header: StateFlow<HeaderState> = ...
      val items: StateFlow<ImmutableList<Item>> = repo.items.stateIn(
          viewModelScope, SharingStarted.WhileSubscribed(5000), persistentListOf()
      )
      val footer: StateFlow<FooterState> = ...
  }
  ```
  Composables that only depend on `header` now skip when `items` changes.
- **`LazyListScope` DSL versus item content.** The DSL block is non-composable, but `items { item -> ... }` content is composable. Strong Skipping memoizes lambdas allocated in that content, including callbacks capturing unstable values. The [LazyListScope source](https://github.com/androidx/androidx/blob/androidx-main/compose/foundation/foundation/src/commonMain/kotlin/androidx/compose/foundation/lazy/LazyDsl.kt) declares item content `@Composable`. Do not label ordinary item callbacks as a memoization gap. For a callback allocated directly in the non-composable DSL, hoist it into the enclosing composable if stable identity matters; `remember` cannot be called directly in the DSL.
- **Derived lists can cause repeated allocation.** `items.filter { it.active }` inside composition repeats work; unstable downstream parameters compare list identity. Compute in the ViewModel or use `remember(items) { items.filter { it.active } }` with immutable source values. Use `derivedStateOf` only when the derived result changes less often than its inputs.
- **`@Immutable` / `@Stable` still help.** Strong Skipping does not make stability annotations obsolete — it makes them more valuable. Use `@Immutable` only when the complete public state is immutable; prefer `kotlinx.collections.immutable.ImmutableList` rather than using the annotation to hide a mutable collection.

Diagnostic:

1. Generate Compose compiler metrics (see earlier section in this file) and open `*-composables.txt`.
2. Look for composables marked `restartable` but **not** `skippable`, or `skippable` composables that still show high recomposition counts in Layout Inspector.
3. Use Android Studio's Recomposition Highlighter or the open-source Compose Stability Analyzer plugin to trace a specific composable.

Source: [developer.android.com/develop/ui/compose/performance/stability/strongskipping](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) and [developer.android.com/develop/ui/compose/performance/stability/diagnose](https://developer.android.com/develop/ui/compose/performance/stability/diagnose).

### Threading traps: snapshot state versus StateFlow

`MutableStateFlow.value` is thread-safe from any dispatcher; `update { }` makes read-modify-write atomic. Neither statement makes mutable objects held inside the flow safe to change concurrently. Publish immutable values instead of mutating a shared list in place. Source: [StateFlow](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/).

Compose snapshot state (`mutableStateOf`, snapshot lists) has snapshot visibility and conflict rules. Keep UI-owned writes on the main dispatcher as a repo convention; off-main snapshot writes are not inherently illegal. If a design needs background snapshot mutation, use an explicit snapshot transaction and handle conflicts instead of inferring View-thread safety from StateFlow. Direct View calls remain main-thread-only.

```kotlin
// UI-owned snapshot state; IO returns data, UI context commits it.
var rows by mutableStateOf(emptyList<Row>())
    private set

fun loadRows() = viewModelScope.launch {
    val loaded = withContext(Dispatchers.IO) { dao.loadRows() }
    rows = loaded
}

// StateFlow can be updated safely from a background dispatcher.
// update's function may run more than once; keep it free of side effects.
_uiState.update { previous -> previous.copy(rows = loaded) }
```

Use `collectAsStateWithLifecycle()` for screen state and `LaunchedEffect` for effects with explicit collection policy. Raw effect collection does not turn a thread-safe upstream flow into an unsafe emitter. See [Compose state](https://developer.android.com/develop/ui/compose/state) and [snapshot transactions](https://github.com/androidx/androidx/blob/androidx-main/compose/runtime/runtime/src/commonMain/kotlin/androidx/compose/runtime/snapshots/Snapshot.kt).

### Coroutine scope anti-patterns

Beyond the `GlobalScope` item under [Avoid](#avoid), two more anti-patterns are worth naming explicitly. Recent IntelliJ IDEA releases ship inspections that flag both; see the JetBrains blog for current inspection release notes.

- **Passing an external `Job` as a coroutine context argument.** `launch(externalJob) { ... }` replaces the parent job, breaks structured concurrency, and decouples cancellation from the enclosing scope. Never do this. If you need a separate lifecycle, create a child scope explicitly: `val childScope = CoroutineScope(SupervisorJob() + Dispatchers.Main)` and cancel it at a known point.
- **Fire-and-forget via `coroutineScope { launch { ... } }` without awaiting.** Inside a suspend function, `coroutineScope { }` waits for its children, so a child `launch { }` does run and complete before the block returns — but if you `launch` without any `await`-semantics expectation, a thrown exception cancels the whole scope, not just the child, and the caller sees the exception. Be deliberate: use `supervisorScope { }` when you want child failures to stay isolated.

## Type naming conflicts

Compose and Android SDK reserve common names. If you create `data class Text(...)`, it shadows Compose's `Text` composable and causes import conflicts. Prefix with your domain:

- `Text` -> `ChatMessage` or `AppText`
- `Image` -> `AppImage` or `MediaItem`
- `Box` -> avoid as a data model name
- `Column` -> avoid as a data model name
- `Row` -> `DataRow` or `TableRow`
- `Button` -> avoid as a data model name
- `Card` -> `ContentCard` or `InfoCard`
- `Surface` -> avoid as a data model name
