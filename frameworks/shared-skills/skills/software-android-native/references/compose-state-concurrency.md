# Compose, StateFlow, and Kotlin Coroutines

This reference mixes platform-backed defaults with explicit repo defaults chosen to reduce ambiguity for agents.

## Table of Contents

- [Verified platform defaults](#verified-platform-defaults)
- [Repo defaults for new API 28+ work](#repo-defaults-for-new-api-28-work)
- [Safe defaults](#safe-defaults) — state, concurrency, UI boundaries, Canvas/drawing, visualization state ownership, Material Design icons, dual-pane patterns, score/progress patterns
- [Kotlin 2.x / K2 compiler transition](#kotlin-2x--k2-compiler-transition)
- [Testing defaults](#testing-defaults)
- [Avoid](#avoid)
- [Backend Integration: Polymorphic and Tier-Gated DTOs](#backend-integration-polymorphic-and-tier-gated-dtos) — GatedOr, lenient deserialization, response wrappers
- [Compose stability pitfalls](#compose-stability-pitfalls)
- [Type naming conflicts](#type-naming-conflicts)

## Verified platform defaults

- Jetpack Compose is the primary Android declarative UI framework.
- ViewModel + StateFlow is the current recommended state management pattern for Android.
- Kotlin Coroutines with Flow is the current async model for structured async work on Android.
- JUnit 5 with Turbine is the preferred test stack for coroutine and Flow testing.
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

- do not update `MutableStateFlow` from a background thread without proper dispatcher switching
- `StateFlow.value` assignment is thread-safe, but collecting in Compose must happen on the main thread
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

### Score and progress patterns

- APIs may return scores on 0-10 or 0-100 scales; detect automatically: `val max = if (score > 10) 100f else 10f`
- apply consistently across progress indicators, gauge needles, and circular progress
- never hardcode a divisor without checking the actual data range first
- use `CircularProgressIndicator` for indeterminate loading; `Canvas` for custom determinate progress with styled arcs

## Kotlin 2.x / K2 compiler transition

- Prefer Kotlin 2.x with K2 compiler for new Android projects where all dependencies support it.
- K2 brings faster compilation, improved type inference, and better IDE performance.
- Enable K2 in `gradle.properties`: `kotlin.experimental.tryK2=true` (pre-2.0) or use Kotlin 2.0+ where K2 is the default.
- Verify Compose compiler compatibility with K2: Compose Compiler 2.0+ is K2-native (no separate Compose compiler plugin — it ships as part of the Kotlin compiler plugin).
- Re-check dependency readiness before enabling K2 — some annotation processors (especially KAPT-based) may need migration to KSP.

## Testing defaults

- use JUnit 5 for new unit and integration tests
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
- Fix unstable parameters before optimizing anything else.

### Lambda stability

- Lambdas that capture unstable references cause the composable to be non-skippable.
- Hoist lambdas to ViewModel methods or use `remember { { viewModel.doSomething() } }` to stabilize the lambda reference.

### Strong Skipping Mode (Kotlin 2.x)

Strong Skipping Mode is enabled by default in the Compose compiler shipped with Kotlin 2.x. It changes the stability contract in two ways that matter for day-to-day code:

1. **Unstable params are now compared by instance identity.** Under the old rules, any composable with an unstable parameter was forced to recompose every time its parent recomposed. Under Strong Skipping, such a composable is still restartable but can skip if the incoming unstable parameter is the **same reference** as the previous invocation. This means stability still matters, but identity matters too.
2. **Lambdas inside `@Composable` functions are auto-memoized.** The compiler inserts a `remember`-equivalent around lambdas whose captured values are all stable, so most inline lambdas stop forcing recomposition.

The new footguns:

- **New `copy()` per frame defeats skipping.** `_uiState.value = _uiState.value.copy(field = new)` creates a new instance; identity-based skip check fails. Fix by splitting the state:
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
- **`LazyListScope.items { }` is NOT inside an `@Composable` function.** Strong Skipping's lambda memoization does not reach there. Unremembered callbacks captured inside `items { item -> Card(onClick = { vm.onClick(item.id) }) }` produce a fresh lambda per recomposition:
  ```kotlin
  // Wrong — new lambda per recomposition
  LazyColumn {
      items(list, key = { it.id }) { item ->
          ItemRow(item, onClick = { vm.onClick(item.id) })
      }
  }

  // Right — remember the lambda with the id as key
  LazyColumn {
      items(list, key = { it.id }) { item ->
          val onClick = remember(item.id) { { vm.onClick(item.id) } }
          ItemRow(item, onClick = onClick)
      }
  }
  ```
- **Derived list inside the composable body breaks identity.** `items.filter { it.active }` creates a new `List` on every recomposition. Compute it in the ViewModel with `stateIn` or wrap in `remember { derivedStateOf { items.filter { it.active } } }` so the filtered list reference only changes when the source changes.
- **`@Immutable` / `@Stable` still help.** Strong Skipping does not make stability annotations obsolete — it makes them more valuable. Annotate data classes whose stability the compiler cannot prove (e.g., those containing `List<T>`) with `@Immutable` and use `kotlinx.collections.immutable.ImmutableList` to document runtime guarantees.

Diagnostic:

1. Generate Compose compiler metrics (see earlier section in this file) and open `*-composables.txt`.
2. Look for composables marked `restartable` but **not** `skippable`, or `skippable` composables that still show high recomposition counts in Layout Inspector.
3. Use Android Studio's Recomposition Highlighter or the open-source Compose Stability Analyzer plugin to trace a specific composable.

Source: [developer.android.com/develop/ui/compose/performance/stability/strongskipping](https://developer.android.com/develop/ui/compose/performance/stability/strongskipping) and [developer.android.com/develop/ui/compose/performance/stability/diagnose](https://developer.android.com/develop/ui/compose/performance/stability/diagnose).

### Threading traps: off-main snapshot mutation

Compose reads and writes snapshot state on the main thread. Mutating state from a coroutine that has switched to `Dispatchers.IO` or `Dispatchers.Default` without switching back causes either:

- `android.view.ViewRootImpl$CalledFromWrongThreadException: Only the original thread that created a view hierarchy can touch its views` — the classic Android main-thread guard, when the mutation happens to touch a View (e.g., a legacy Views interop surface or a `DialogWindow`).
- `java.util.ConcurrentModificationException` inside `androidx.compose.runtime.snapshots.SnapshotStateObserver` — Compose's internal observer set is not thread-safe against concurrent mutation from multiple coroutines.

Canonical bug shape:

```kotlin
// Wrong — mutation happens on Dispatchers.IO
viewModelScope.launch {
    withContext(Dispatchers.IO) {
        val rows = dao.loadRows()
        _uiState.value = _uiState.value.copy(rows = rows)  // off-main mutation
    }
}

// Right — pure IO block returns a value; mutation happens on the resumed main context
viewModelScope.launch {
    val rows = withContext(Dispatchers.IO) { dao.loadRows() }
    _uiState.value = _uiState.value.copy(rows = rows)  // back on main
}
```

Rules:

- `_uiState.value = ...` assignment is technically thread-safe at the `MutableStateFlow` level, but Compose's collector and downstream snapshot observation are not safe against concurrent mutation from multiple non-main threads.
- Prefer `viewModelScope.launch { val x = withContext(IO) { ... }; _uiState.value = copy(x) }` over `launch(Dispatchers.IO) { _uiState.value = copy(...) }`.
- In composables, always collect via `collectAsStateWithLifecycle()` — a raw `collect` inside `LaunchedEffect` runs on the composition dispatcher and can still observe inconsistent intermediate state during rapid upstream emissions.
- For tests, use `runTest { }` with a `TestDispatcher` and a `MainDispatcherRule`; never `Dispatchers.setMain(Dispatchers.Unconfined)` in isolation — it hides these bugs until production.

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
