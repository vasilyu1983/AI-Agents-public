# Coroutine and Compose Recipes

Small, correct recipes for coroutine plumbing, networking hygiene, custom modifiers, and animation choice. Moved from the retired software-mobile Kotlin templates, with their bugs fixed. Defaults for state, stability and scope anti-patterns stay in [compose-state-concurrency.md](compose-state-concurrency.md). Test recipes (Turbine, MockK, Compose UI tests) are owned by [qa-testing-android](../../qa-testing-android/SKILL.md). Secure token storage is owned by [software-security-appsec](../../software-security-appsec/assets/mobile/template-mobile-security.md); do not use the deprecated `security-crypto` APIs.

## Contents

- [Scope Choice](#scope-choice)
- [Search-as-You-Type Pipeline](#search-as-you-type-pipeline)
- [Retry with Backoff](#retry-with-backoff)
- [Bounded Parallelism and Timeouts](#bounded-parallelism-and-timeouts)
- [One-Shot UI Events](#one-shot-ui-events)
- [Cooperative Cancellation and Cleanup](#cooperative-cancellation-and-cleanup)
- [HTTP Client Hygiene](#http-client-hygiene)
- [Custom Modifiers](#custom-modifiers)
- [Animation API Choice](#animation-api-choice)

## Scope Choice

| Work | Scope |
|---|---|
| Screen state loading, repository calls | `viewModelScope` |
| Collecting flows in an Activity or Fragment | `lifecycleScope` + `repeatOnLifecycle(STARTED)` (or `collectAsStateWithLifecycle` in Compose) |
| Suspend calls from a UI event (snackbar, scroll, animate) | `rememberCoroutineScope()` inside the composable |
| Work driven by composition or a key change | `LaunchedEffect(key)` |
| Work that must outlive a screen | An injected application-level `CoroutineScope(SupervisorJob() + dispatcher)`, or WorkManager if it must survive process death |

Never create an ad-hoc `CoroutineScope(...)` inside a class without owning its cancellation. Never use `GlobalScope`.

## Search-as-You-Type Pipeline

```kotlin
private val query = MutableStateFlow("")

val results: StateFlow<List<Item>> = query
    .debounce(300)
    .map { it.trim() }
    .distinctUntilChanged()
    .flatMapLatest { q ->
        if (q.isEmpty()) flowOf(emptyList())
        else flow { emit(repo.search(q)) }.catch { emit(emptyList()) }  // or map to an error UI state
    }
    .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
```

`flatMapLatest` cancels the previous search when a new query arrives. `catch` goes inside the inner flow, so one failure does not end the outer stream.

## Retry with Backoff

```kotlin
suspend fun <T> retryWithBackoff(
    maxAttempts: Int = 3,
    initialDelayMs: Long = 500,
    maxDelayMs: Long = 8_000,
    isTransient: (Throwable) -> Boolean = { it is IOException },
    block: suspend () -> T,
): T {
    var delayMs = initialDelayMs
    repeat(maxAttempts - 1) {
        try { return block() }
        catch (e: CancellationException) { throw e }          // never swallow cancellation
        catch (e: Throwable) { if (!isTransient(e)) throw e }
        delay(delayMs + Random.nextLong(delayMs / 2 + 1))    // jitter avoids synchronized retries
        delayMs = (delayMs * 2).coerceAtMost(maxDelayMs)
    }
    return block()
}
```

Retry only idempotent calls and transient failures, such as I/O errors and 5xx/429 responses. Do not retry 4xx client errors. The retired template caught `Exception`, so it also swallowed `CancellationException` and retried errors that can never succeed.

Rule: `rules/kotlin/coroutines.md` loads this invariant when Claude edits a matching file.

## Bounded Parallelism and Timeouts

- **Fixed fan-out:** use `coroutineScope { listOf(async { a() }, async { b() }).awaitAll() }`. If one call fails, the siblings are cancelled.
- **Cap concurrent work:** use `val permits = Semaphore(n)` with `permits.withPermit { download(url) }`, or give a dispatcher its own lane with `Dispatchers.IO.limitedParallelism(n)`.
- **Timeouts:** `withTimeoutOrNull(ms) { ... }` returns `null` when time runs out. `withTimeout` throws `TimeoutCancellationException`, which is a `CancellationException`. A broad `catch (e: Exception)` placed after it can therefore misclassify a timeout, or swallow a real cancellation. Catch the timeout explicitly, or use the `OrNull` form.

## One-Shot UI Events

| Need | Use | Trade-off |
|---|---|---|
| Deliver each event exactly once to the single screen collector | `Channel<Event>(Channel.BUFFERED)` exposed as `receiveAsFlow()` | Events buffer while the UI is stopped. Only one collector receives each event. |
| Broadcast to many collectors | `MutableSharedFlow<Event>(extraBufferCapacity = 1, onBufferOverflow = DROP_OLDEST)` | With `replay = 0`, events emitted while nobody collects are lost. |
| Last value matters (location, connectivity) | `MutableSharedFlow(replay = 1)` or `StateFlow` | New collectors get the latest value right away. |

Where you can, model the event as state that the UI acknowledges, for example a `userMessage` field that is cleared after it is shown. This avoids lost events entirely.

## Cooperative Cancellation and Cleanup

- In long loops that never suspend, call `ensureActive()` (or `yield()`) so cancellation can take effect.
- Release resources in `finally` or with `use {}`. If the cleanup itself must suspend, wrap it in `withContext(NonCancellable) { ... }`.
- If you catch `CancellationException` to log it, rethrow it.
- Never use `runBlocking` on the main thread. Never start collecting a flow with `.collect` in a ViewModel `init` without launching. Expose the flow through `stateIn` instead.

## HTTP Client Hygiene

- Add the auth header in an OkHttp interceptor that reads the token at request time. Handle token refresh in one place, for example an OkHttp `Authenticator`, so parallel 401s trigger a single refresh.
- Enable `HttpLoggingInterceptor` at `BODY` level only in debug builds. At that level it logs bearer tokens and personal data to logcat.
- Set connect and read timeouts deliberately, per client, and use the same values in tests.

## Custom Modifiers

Android's guidance ([Create custom modifiers](https://developer.android.com/develop/ui/compose/custom-modifiers)) is to try chaining existing modifiers first, and to use `Modifier.Node` for stateful or lower-level behavior. That page says `Modifier.composed {}` "is no longer recommended due to the performance issues it created". The retired template used `composed` for a shimmer effect. Do not copy that pattern.

```kotlin
// Chain first: covers most "custom" styling
fun Modifier.cardStyle(color: Color, shape: Shape = RoundedCornerShape(12.dp)) =
    shadow(4.dp, shape).background(color, shape).padding(16.dp)

// Conditional application without branching the chain
Modifier.then(if (highlighted) Modifier.border(2.dp, highlightColor) else Modifier)
```

Pass theme colors in from the call site (for example, `Modifier.cardStyle(MaterialTheme.colorScheme.surface)`). A plain modifier factory is not a composable, so it cannot read `MaterialTheme` itself.

## Animation API Choice

This table adds to the chooser in [ui-and-integration-patterns.md](ui-and-integration-patterns.md) (`animate*AsState`, `Animatable`, `InfiniteTransition`):

| Intent | API |
|---|---|
| Show or hide content with enter/exit transitions | `AnimatedVisibility` |
| Swap content when a target state changes | `AnimatedContent` |
| Smoothly resize a container when its content changes | `Modifier.animateContentSize()` |
| Several values driven by one state (color, size and elevation together) | `updateTransition(targetState)` with `animate*` children |
| Looping placeholder or shimmer | `rememberInfiniteTransition`. Read the animated value in a draw or `graphicsLayer` lambda so it does not recompose every frame. |

Always pass a `label` to transitions so Android Studio's animation preview can identify them.
