---
name: software-android-native
description: "Guides native Android development with Kotlin, Jetpack Compose, and Views interop. Use when building, rewriting, or reviewing modern Android apps after establishing runtime truth."
compatibility: Portable core. Works on Claude Code and Codex.
version: "1.1"
last_validated: 2026-07-11
---

# Native Android Development

Use this skill for native Android work only. It is the default shared-skill entrypoint for Compose-first Android apps targeting API 28+, bounded rewrites from older codebases, and agent-assisted workflows in Android Studio, Codex, and Claude Code.

## Quick Reference

| Task | Default Picks | Notes |
|------|---------------|-------|
| **State & UI** | | |
| New UI screens | Jetpack Compose | Views interop only where existing mature flows or third-party SDKs require it |
| Observable state | ViewModel + `StateFlow` (Kotlin 2.x) | Replaces LiveData for new code |
| Async work | Kotlin Coroutines + Flow | `Dispatchers.IO` for blocking, `Dispatchers.Default` for CPU; structured concurrency preferred |
| Unit/integration tests | JUnit 4 + Turbine | Android-supported default; JUnit 5 requires verified community integration |
| UI tests | Compose Testing APIs (`ComposeTestRule`) | Espresso only for Views interop or legacy screens |
| **State machine discipline** | | |
| Submit guard | `if (_uiState.value is Loading) return` | Prevents double-tap duplicate submissions in ViewModel |
| Transient completion | One-shot UI effect or explicit acknowledgement | Do not reset durable state on an arbitrary timer; cancel or supersede stale work |
| Minimal sealed classes | Remove states that can't happen anymore | Dead sealed subclasses produce dead `when` branches and mislead future readers |
| **Networking & resilience** | | |
| Network reachability | `ConnectivityManager` + `NetworkCallback` wrapped in `StateFlow` | Publish `isConnected`; disable submit buttons when offline; observe in `collectAsStateWithLifecycle` |
| **DI & architecture** | | |
| Dependency injection | Hilt | `@HiltViewModel`, `@Inject constructor`, `@Module` + `@InstallIn` |
| Local persistence | Room + KSP | Prefer `@Upsert` over separate insert/update; KSP replaces KAPT |
| Background work | WorkManager + `CoroutineWorker` | Deferrable, constraint-aware background processing |
| Runtime tool selection and device proof | [software-android-runtime-debugging](../software-android-runtime-debugging/SKILL.md) | Use its tool checks before implementation; build-loop details are in [Android Studio workflows](references/android-studio-workflows.md) |
| **Compose, billing, adaptive, auth & push** | See [Quick Picks](references/ui-and-integration-patterns.md#quick-picks) | `LazyColumn` keys, side effects, Play Billing acknowledgement, `WindowSizeClass`, Credential Manager, FCM, deep links |
| `collectAsStateWithLifecycle` | `stateFlow.collectAsStateWithLifecycle()` | Lifecycle-aware collection; prevents updates when app is backgrounded |
| **Strong Skipping (Kotlin 2.x)** | | |
| UI state instance identity | Inspect stability/recompositions before splitting state | Unstable parameters use identity, stable ones equality; StateFlow conflates equal values |
| `LazyListScope` lambdas | Distinguish the non-composable DSL from composable item content | Strong Skipping memoizes lambdas in composable item content; hoist callbacks into the enclosing composable only when a non-composable DSL allocation matters |
| Concurrent state updates | Use `MutableStateFlow.update { }` for read-modify-write; keep Compose snapshot-state (`mutableStateOf`) writes on the main thread by convention | `MutableStateFlow.value` assignment is itself thread-safe — the real hazard is a non-atomic `value = value.copy()` race under concurrent writers |

## When to Use This Skill

Use this skill to:

- Build new Compose-first screens and features for Android apps targeting API 28+
- Plan and execute bounded rewrites from Views or older Kotlin/Java codebases
- Set up agent-assisted Android workflows in Android Studio, Codex, or Claude Code
- Implement Kotlin Coroutines, Flow, and ViewModel state patterns
- Prepare data safety declarations, target SDK compliance, and release gates
- Review native Android code for architecture, performance, and compliance

## Defaults

- New native Android work: prefer Jetpack Compose for new screens and Views interop only where existing mature flows or third-party SDKs require it.
- New observable UI state: prefer ViewModel + `StateFlow` and keep UI-facing state collected on the main thread with `collectAsStateWithLifecycle`.
- Async work: prefer Kotlin Coroutines with structured concurrency; use `Dispatchers.IO` for blocking I/O and `Dispatchers.Default` for CPU-bound work.
- Dependency injection: prefer Hilt for new projects.
- Local persistence: prefer Room with KSP annotation processing.
- Build system: prefer Gradle KTS (`build.gradle.kts`) with version catalogs (`libs.versions.toml`).
- Navigation: prefer type-safe Compose Navigation (type-safe routes since 2.8) with `@Serializable` route classes; evaluate Navigation 3 (stable) for scene-based adaptive layouts.
- New unit and integration tests: prefer JUnit 5 with Turbine for Flow assertions.
- UI tests: prefer Compose Testing APIs; keep Espresso for legacy Views screens.
- Release gates: treat target SDK compliance, data safety declarations, ProGuard/R8 rules, Play Integrity, accessibility, and real-device verification as non-optional.

## ASCII Flow

```text
Android native task
  -> Confirm app shape: Compose, Views interop, service, or release gate
  -> Prove Gradle, emulator/device, install, and launch reality
  -> Choose architecture: ViewModel, StateFlow, Hilt, Room, Navigation
  -> Implement bounded slice with lifecycle-aware state and tests
  -> Check Kotlin, Compose, R8, billing, and Play-policy traps
  -> Build, install, launch, inspect logs, and report proof
```

## Known Kotlin Traps

These are headline footguns for Compose-first native Android on Kotlin 2.x. Each is source-backed; re-verify versions against the linked release notes before quoting a fix window.

- **Lost updates from non-atomic state writes.** `MutableStateFlow.value` assignment is itself thread-safe from any dispatcher ("All methods of state flow are thread-safe" — [kotlinx.coroutines StateFlow docs](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-state-flow/)), so assigning it from `Dispatchers.IO` is not a crash cause. The real hazard is a non-atomic read-modify-write (`value = value.copy()`) racing under concurrent writers and silently dropping an update. Fix: keep `withContext(Dispatchers.IO) { ... }` blocks pure (return a value, do not mutate state inside), use `MutableStateFlow.update { }` for concurrent updates, keep Compose snapshot-state (`mutableStateOf`) writes on the main thread by convention, and collect UI state via `collectAsStateWithLifecycle()`. Use `LaunchedEffect` for effects with an explicit lifecycle/delivery policy. See [references/compose-state-concurrency.md](references/compose-state-concurrency.md).
- **Strong Skipping Mode identity checks.** Enabled by default since 2.0.20 (Kotlin compiler boundary), it compares unstable parameters by identity and stable parameters by equality. A new instance matters for unstable consumers; an equal `data class` value is also suppressed by StateFlow's equality conflation. Inspect compiler stability and actual recompositions before splitting state or adopting immutable collections. See [Compose stability pitfalls](references/compose-state-concurrency.md#compose-stability-pitfalls).
- **`LazyListScope` lambda boundaries.** Item content is composable and receives Strong Skipping memoization. A lambda allocated in the non-composable DSL block is a different case; create any needed remembered callback in the enclosing composable, where `remember` is valid. See [Strong Skipping](references/compose-state-concurrency.md#strong-skipping-mode-kotlin-2x).
- **Compose plugin version skew on Kotlin 2.x.** Since Kotlin 2.0 the Compose compiler ships with the Kotlin compiler and is applied via the Gradle plugin `kotlin("plugin.compose")`. A stale or missing plugin declaration surfaces as `Argument type mismatch: actual type 'Function0<Unit>', but '@Composable ComposableFunction0<Unit>' was expected` — the transform did not run. Fix: lock `plugin.compose` to the exact Kotlin version in `libs.versions.toml`. Source: [developer.android.com/jetpack/androidx/releases/compose-kotlin](https://developer.android.com/jetpack/androidx/releases/compose-kotlin).
- **Compose runtime regressions fixed upstream.** If you see a crash in pausable composition under `LookaheadScope`, nested `Popup` positioning against the screen instead of the parent, or a reentrant-modification crash in `SnapshotStateObserver`, upgrade to the latest Compose UI patch release before treating the problem as app-level — check the compose-ui release notes for a fix matching the stack trace; a project pinned below the release that carries the fix should treat the crash as a known-fixed upgrade target, not a fresh bug. Newer Compose releases can raise the required `compileSdk` and AGP, so check those before bumping. Verify current at [developer.android.com/jetpack/androidx/releases/compose-ui](https://developer.android.com/jetpack/androidx/releases/compose-ui). Route to [../software-android-runtime-debugging/references/compose-debugging.md](../software-android-runtime-debugging/references/compose-debugging.md).
- **`kotlinx-serialization` + R8.** The library bundles keep rules for retained serializable classes. Named companion objects need additional mode-specific rules; use the [upstream Android guidance](https://github.com/Kotlin/kotlinx.serialization#android), inspect merged rules, and smoke-test the minified release path. Do not blanket-keep every serializer or assume a library-version regression without a reproducer. Runtime triage: [proguard-r8-triage.md](../software-android-runtime-debugging/references/proguard-r8-triage.md).

## Kotlin Anti-Patterns

Refuse these in new code: K1 `GlobalScope.launch`; K2 passing an external `Job` to `launch`; K3 `LiveData` + `observeAsState` in new Compose code; K4 nullability as the loading/error/success model; K5 keeping `kapt` on Kotlin 2.x (migrate to KSP2); K6 treating `StateFlow.value = copy(...)` as free; K7 filtering or sorting lists inside a composable body; K8 `runBlocking` in production paths. Why each bites and the better default: [references/compose-state-concurrency.md](references/compose-state-concurrency.md#kotlin-anti-patterns-k1-k8).

## Architecture Judgment Calls

### State Versus Effect Ownership

Keep durable screen facts in `StateFlow`: input, loading, result, recoverable error, and data needed after recreation. Model one-time navigation, snackbar, focus, and haptic work as effects with a named delivery policy. A delayed `Idle` reset is correct only when the product contract explicitly says the result expires; otherwise it races a retry, process recreation, or a newer request.

For each async intent, assign a request identity or cancel the prior job, ignore results from superseded requests, and make the backend operation idempotent when duplicate delivery is possible. Verify rapid double-tap, navigate-away, retry-before-completion, and process recreation instead of relying on a fixed debounce or `delay()`.

Decisions that need a rationale, not just a default pick. Verify each version-specific claim at the linked source before quoting it.

- **Compose vs Views.** Compose is the repo default for new screens. Choose Views or interop when integration constraints justify it. Keep Views only for: (1) a third-party SDK that ships a `View`-based render surface with no Compose wrapper (some map, ad, or video SDKs), (2) a legacy screen mid-migration where the cost of a full rewrite outweighs the interop tax, or (3) `SurfaceView`/`TextureView`-backed continuous rendering (camera preview, custom video) where Compose's `AndroidView` bridge is the right embedding, not a reason to avoid Compose for the rest of the screen. Compare measured performance on the target workload before selecting either toolkit for speed.
- **Hilt vs Koin.** Hilt (compile-time, annotation-processor-based, built on Dagger) remains the repo default for new API 28+ apps: it fails at compile time on a broken graph, has first-class `@HiltViewModel` / `WorkManager` / `Compose Navigation` integration, and is what most enterprise Android codebases already standardize on. Prefer Koin instead only when: the team explicitly wants to avoid annotation processing and Gradle plugin overhead (KSP-free build), the project is small enough that compile-time graph validation matters less than iteration speed, or the codebase is a Kotlin Multiplatform module where Hilt cannot run (Hilt is Android/JVM-only; Koin runs on all KMP targets). Do not switch an existing Hilt codebase to Koin mid-project without a concrete, named pain point — DI framework churn has a high cost for a marginal ergonomics gain.
- **Kotlin Multiplatform (KMP).** KMP is a real option for sharing business logic (networking, persistence, ViewModel state) across Android and iOS — but it is a **product/architecture decision**, not a default for this skill. If the task is "should we share code with iOS," route to [software-mobile](../software-mobile/SKILL.md) (or the `software-mobile-architect` advisor, where available) for the cross-platform tradeoff call before writing shared-module code; this skill assumes the Android-native side once that call is made. Verify current KMP/Compose Multiplatform stability status at [kotlinlang.org/docs/multiplatform/supported-platforms.html](https://kotlinlang.org/docs/multiplatform/supported-platforms.html).
- **When NOT to go native.** If the actual question is "should this feature be a native Android screen at all" (vs. a cross-platform framework, a web view, or a KMP-shared module), that decision belongs to [software-mobile](../software-mobile/SKILL.md) (or the `software-mobile-architect` advisor) — do not let this skill's Compose-first defaults silently answer a platform-choice question it was not asked.
- **Coroutines vs Flow failure modes.** A `suspend fun` returns one value and is the wrong tool for anything that emits more than once (search-as-you-type, connectivity state, DB observation) — using a polling `suspend` loop instead of `Flow` produces stale reads and duplicate work. Conversely, wrapping a one-shot operation (a single network POST) in a `Flow` that a caller collects once adds `Flow`'s cancellation/backpressure machinery for no benefit — a plain `suspend fun` is simpler and equally cancellable via structured concurrency. Rule of thumb: one value now -> `suspend fun`; zero-to-many values over time -> `Flow`; a single ViewModel-to-UI event stream that should not replay -> `SharedFlow` with `replay = 0`, not `StateFlow`.
- **Process death and `SavedStateHandle`.** `ViewModel` survives configuration change but not process death under memory pressure. Anything the user would be upset to lose on a background-kill-and-restore (form input mid-fill, scroll position, in-progress multi-step flow state) must go through `SavedStateHandle` (`@HiltViewModel` constructor-injects it automatically), not just `ViewModel` field state. Test this with `adb shell am kill <package>` while backgrounded, not just rotation — rotation alone never exercises the process-death path and gives false confidence.

## ANR and Frame Budget Arithmetic

Classify ANRs with the canonical [runtime-debugging thresholds](../software-android-runtime-debugging/references/performance-triage.md#anr-thresholds), and distinguish foreground-service promotion exceptions from ANRs. Re-derive frame budget as 1000 ms / measured refresh rate; verify on the affected device. Recipes: [references/android-scenarios-and-budgets.md](references/android-scenarios-and-budgets.md#anr-and-frame-budget-arithmetic).

## Runtime Truth And Prompting

Use a proof-first execution loop for native Android work:

- verify tool reality first: Android Studio Gemini, Gradle CLI, ADB, and emulator or device availability
- prove build, install, and launch before UI diagnosis
- keep repo memory lean and fact-only
- require bounded slices with explicit proof artifacts

Load [references/runtime-proof-and-prompts.md](references/runtime-proof-and-prompts.md) for AI-agent defaults, proof-first and token-discipline rules, the execution loop, and high-value prompt shape.

## Rewrite Workflow

1. Lock the baseline:
   existing app behavior, minimum API level, device classes, external integrations, and non-goals.
2. Choose the target defaults:
   Compose-first, API 28+, ViewModel + StateFlow, Hilt, Room + KSP, Kotlin Coroutines, JUnit 4 (or verified JUnit 5 integration), Compose Testing.
3. Slice the rewrite into bounded vertical features:
   app shell (Application class, Hilt setup, navigation graph), auth/session, core navigation, feature flows, integrations, release surfaces.
   - If the project uses multi-module Gradle, verify module dependencies and build order before adding new modules.
   - If migrating from Java to Kotlin, convert one file at a time using Android Studio's converter, then review and fix idiom issues. Do not bulk-convert entire packages without validation.
   - If migrating from Views to Compose, use `ComposeView` in existing XML layouts as a bridge. Do not rewrite an entire Activity/Fragment hierarchy in one pass.
4. For each slice, require evidence:
   build success, install and launch success, targeted tests, parity notes, and known gaps.
5. Keep release-only concerns visible throughout:
   data safety declarations, target SDK compliance, ProGuard/R8 rules, Play Integrity, push/deep-link behavior, store metadata.
6. End every batch with a handoff:
   changed behavior, validation performed, residual risk, next slice.
7. When a backend change eliminates an error class (e.g., unifying two API paths into one), immediately remove the now-impossible error types, decoders, and UI states from the Android client. Dead error handling misleads future developers about what can actually happen and inflates the codebase.

## Specialized Patterns

Load [references/ui-and-integration-patterns.md](references/ui-and-integration-patterns.md) for Compose, adaptive-layout, and foldable patterns; the quick picks for billing, adaptive layout, auth, and push; native/backend integration gotchas (auth, onboarding, Supabase or Firebase); and Google Play Billing rules and RTDN constraints.

## When NOT to Use This Skill

Use a different skill when:

- **Cross-platform or platform-choice decisions** -> [software-mobile](../software-mobile/SKILL.md)
- **Android test execution, device matrix, Espresso deep dives** -> [qa-testing-android](../qa-testing-android/SKILL.md)
- **Web UI or browser app implementation** -> [software-frontend](../software-frontend/SKILL.md)
- **General architecture without Android-specific constraints** -> [software-architecture-design](../software-architecture-design/SKILL.md)
- **Backend platform selection (Supabase, Firebase, Convex)** -> [software-baas-platforms](../software-baas-platforms/SKILL.md)

## Scenarios

Symptom-keyed recipes (S1 Strong Skipping recomposition perf, S2 R8 stripping kotlinx-serialization, S3 foreground-service crash on API 35, S4 predictive back migration, S5 Play Billing entitlement reconciliation) live in [references/android-scenarios-and-budgets.md](references/android-scenarios-and-budgets.md#scenarios).

## Navigation

### References

| Resource | Purpose |
|----------|---------|
| [references/android-rewrite-playbook.md](references/android-rewrite-playbook.md) | Rewrite slicing, acceptance criteria, and evidence rules |
| [references/agentic-android-tooling.md](references/agentic-android-tooling.md) | Android Studio Gemini, Gradle CLI + ADB, and emulator selection rules |
| [references/android-studio-workflows.md](references/android-studio-workflows.md) | Gradle wrapper, build variants, canonical build/test/install loops |
| [references/codex-claude-android-workflows.md](references/codex-claude-android-workflows.md) | Repo memory, approval boundaries, and prompt patterns |
| [references/runtime-proof-and-prompts.md](references/runtime-proof-and-prompts.md) | Proof-first runtime execution, token discipline, and prompt shape |
| [references/ui-and-integration-patterns.md](references/ui-and-integration-patterns.md) | Compose, adaptive-layout, backend integration, and billing patterns |
| [references/compose-state-concurrency.md](references/compose-state-concurrency.md) | Verified app-layer defaults for Compose, StateFlow, and coroutines |
| [references/android-release-and-compliance.md](references/android-release-and-compliance.md) | Target SDK, data safety, ProGuard/R8, and release-gate checks |
| [references/android-scenarios-and-budgets.md](references/android-scenarios-and-budgets.md) | ANR/frame-budget arithmetic and symptom-keyed scenarios S1-S5 |
| [references/coroutine-and-compose-recipes.md](references/coroutine-and-compose-recipes.md) | Coroutine scope choice, retry/backoff, bounded parallelism, one-shot events, OkHttp hygiene, custom modifiers, animation API choice |
| [data/sources.json](data/sources.json) | Primary sources and current external references |

### Templates

Use the rewrite brief at project start, the feature request per slice, the proof checklist at each verification gate, and the agent handoff at batch boundaries.

| Template | Purpose |
|----------|---------|
| [assets/template-android-rewrite-brief.md](assets/template-android-rewrite-brief.md) | Rewrite scope and constraint brief |
| [assets/template-android-feature-request.md](assets/template-android-feature-request.md) | Feature-level Codex / Claude Code request format |
| [assets/template-android-proof-checklist.md](assets/template-android-proof-checklist.md) | Source-backed proof and validation checklist |
| [assets/template-android-agent-handoff.md](assets/template-android-agent-handoff.md) | Post-change handoff with evidence and residual risk |

### Related Skills

| Skill | Purpose |
|-------|---------|
| [software-mobile](../software-mobile/SKILL.md) | Platform choice and cross-platform tradeoffs |
| [qa-testing-android](../qa-testing-android/SKILL.md) | Android test execution, device matrix, and Espresso/UI Automator |
| [qa-testing-mobile](../qa-testing-mobile/SKILL.md) | Cross-platform mobile QA strategy |
| [agents-memory](../agents-memory/SKILL.md) | Shared `AGENTS.md` / `CLAUDE.md` memory strategy |
| [dev-context-engineering](../dev-context-engineering/SKILL.md) | Cross-tool context design for Codex and Claude Code |
| [software-performance](../software-performance/SKILL.md) | Performance measurement and regression gates |
| [software-baas-platforms](../software-baas-platforms/SKILL.md) | Backend platform selection and comparison |
| [ai-context-layer/references/conversational-surfaces-cross-platform.md](../ai-context-layer/references/conversational-surfaces-cross-platform.md) | Natural-conversation composition for Android (Gemini Nano via AICore / ML Kit GenAI, ObjectBox on-device vector index, deterministic Composer B for non-AICore devices) inside the cross-platform recipe |

---

## Freshness Protocol

For dependency/tool upgrades, resolve the installed Gradle/AGP/Kotlin/Compose matrix from the release notes linked in [Android Studio workflows](references/android-studio-workflows.md). For submission, read the live target-SDK, page-size and Billing requirements in [release checks](references/android-release-and-compliance.md); for API 37 migration, load its [behavior checklist](references/android-release-and-compliance.md#target-api-37-migration-checklist). Record the checked URL and date; do not reuse historical learnings as current release requirements.

## Learnings Loop

When prior decisions or pitfalls are relevant, consult `learnings.consolidated.md` if present; use `learnings.md` only for needed history or as the available fallback. Otherwise skip both.

After applying it, if you encountered a pattern worth remembering, a mistake worth preventing, or a domain fact that surprised you, append one dated bullet to `learnings.md` via `agents-skills-feedback-loop/scripts/append_learning.py`. Do not modify `SKILL.md` itself.
