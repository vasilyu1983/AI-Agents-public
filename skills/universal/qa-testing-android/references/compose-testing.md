# Jetpack Compose Testing Guide

Non-obvious Compose UI testing content: the v2 migration, the merged-tree trap (corrected),
synchronization, and the API surface worth a reminder. Base-model-obvious finder/action/assertion
syntax has been cut — see the [official API reference](https://developer.android.com/develop/ui/compose/testing/apis)
for the full method list.

**Official docs**: [Compose Testing](https://developer.android.com/develop/ui/compose/testing) | [v1→v2 migration](https://developer.android.com/develop/ui/compose/testing/migrate-v2) | [Testing APIs](https://developer.android.com/develop/ui/compose/testing/apis)

## Table of Contents

- [Setup](#setup)
- [Compose Test v2 Migration](#compose-test-v2-migration)
- [Trap: Compose Semantics Tree Merging](#trap-compose-semantics-tree-merging)
- [Synchronization](#synchronization)
- [Testing Patterns Worth Calling Out](#testing-patterns-worth-calling-out)
- [Screenshot Testing](#screenshot-testing)
- [Debugging](#debugging)
- [Best Practices](#best-practices)

## Setup

### Dependencies

```kotlin
// app/build.gradle.kts
dependencies {
    androidTestImplementation(platform(libs.androidx.compose.bom))
    androidTestImplementation(libs.androidx.compose.ui.test.junit4)
    debugImplementation(libs.androidx.compose.ui.test.manifest)
}
```

Notes:
- `createComposeRule()` still hosts your `@Composable` content inside a `ComponentActivity` under
  the hood — that is why `ui-test-manifest` is a required `debugImplementation`. It avoids *your*
  app's `Activity`, DI graph, and navigation, not a device: unless the module also runs it under
  Robolectric (`test/` + `@RunWith(AndroidJUnit4)` + `isIncludeAndroidResources = true`), it still
  runs instrumented on an emulator or device. Prefer it over `createAndroidComposeRule<Activity>()`
  when the composable does not need real navigation, DI, or activity lifecycle — that is the actual
  unit-vs-instrumented tradeoff, not "no device at all."
- Roborazzi and similar tools exist specifically to run Compose test rules under Robolectric in
  JVM `test/`, closing that gap when you want true JVM speed.
- If you do not use version catalogs, apply the Compose BOM in `androidTestImplementation(...)` and
  keep versions aligned with your app module.

### Test Rules

```kotlin
import androidx.compose.ui.test.junit4.v2.createComposeRule
import androidx.compose.ui.test.junit4.v2.createAndroidComposeRule

// Uses the test ComponentActivity, without your app's Activity/DI/navigation
@get:Rule
val composeTestRule = createComposeRule()

// With Activity (for integration tests)
@get:Rule
val composeTestRule = createAndroidComposeRule<MainActivity>()
```

## Compose Test v2 Migration

The v1 APIs (`androidx.compose.ui.test.junit4.createComposeRule`,
`createAndroidComposeRule`) are deprecated. v2 (`androidx.compose.ui.test.junit4.v2.createComposeRule`,
`androidx.compose.ui.test.v2.runComposeUiTest`) is available from `ui-test`/`ui-test-junit4`
1.11.0-alpha03+. Check the [migration guide](https://developer.android.com/develop/ui/compose/testing/migrate-v2)
and your installed artifacts for API status and configuration overloads before changing imports.

**The breaking change**: v1 ran on `UnconfinedTestDispatcher`; v2 defaults to
`StandardTestDispatcher`. v2 also forces `InputMode.Touch` by default. Both are deliberate — v1's
unconfined dispatcher let coroutine work run eagerly and out of order, hiding real race bugs.

Expect three failure classes when migrating a v1 suite to v2, and classify each one before "fixing" it:

1. **State read immediately after a trigger.** A test asserts on state right after `performClick()`
   without waiting for the triggered coroutine to run. Fix: call `composeTestRule.waitForIdle()` or
   wrap the assertion in `runOnIdle { }`.
2. **`LaunchedEffect`/`delay` timing.** Fix: use `composeTestRule.mainClock.advanceTimeBy(...)` or,
   inside `runComposeUiTest`, `mainClock.scheduler.runCurrent()` for explicit control over queued work.
3. **Input-mode assumptions.** Tests written against v1's default input handling may need an explicit
   `ComposeUiTestConfig(inputMode = ...)` (available from `ui-test` 1.13.0-alpha01+) if they assumed
   non-touch input.

A v2 failure that is none of the above — one that surfaces a missing `withContext` or an off-main
race that v1's eager dispatcher was masking — is a real bug, not a harness artifact. Prefer
`runComposeUiTest` for new tests: it gives you one clock and one dispatcher to reason about, instead
of the rule/activity split.

Standard Compose assertions already synchronize. Add explicit waiting when reading state directly
or manually controlling the clock; unrelated external work still needs an idling resource or condition.

## Trap: Compose Semantics Tree Merging

Compose merges the semantics of child nodes into a single parent node by default. A `Button` that
wraps an `Icon` and a `Text("Save")` presents as one merged node carrying
`Text = ["Save"]` in its semantics — **text finders like `onNodeWithText("Save")` still match that
merged parent by default.** `hasText` matches if any entry in the node's Text list matches, so the
common claim that `onNodeWithText`/`assertExists()` "finds nothing" on a merged component is wrong.

**What actually fails**:

- A `testTag` placed on a *child* inside the merged component is invisible to `onNodeWithTag`
  unless you pass `useUnmergedTree = true` — the child node itself is gone from the default tree,
  only its semantics survive, merged into the parent.
- An assertion that expects exactly one value when the merged list holds several — for example
  `assertTextEquals("Save")` on a Button containing `Text("Save")` and `Text("Draft")` —
  fails because the assertion compares against the whole merged list, not because the finder found
  nothing. An Icon's `contentDescription` belongs to ContentDescription, not the Text list.
- A click on the child's coordinates lands on the parent's click handler, since only the parent
  carries the merged click action.

```kotlin
// Child testTag is invisible in the merged tree by default
composeTestRule.onNodeWithTag("saveIcon").assertExists() // fails: node not in merged tree

// Pass useUnmergedTree = true to reach the child
composeTestRule.onNodeWithTag("saveIcon", useUnmergedTree = true).assertExists()

// This works even without useUnmergedTree — text finders match the merged parent
composeTestRule.onNodeWithText("Save").assertExists()

// This can fail even though the text is present, if the merged list has more than one value
composeTestRule.onNodeWithTag("saveButton").assertTextEquals("Save") // fails if merged list has 2+ entries
```

**Rule of thumb**: use `testTag` on the merged parent and assert on aggregated semantics when
possible. Drop into `useUnmergedTree = true` when you need to target an individual child node the
merge hides. Print both trees to compare during investigation:

```kotlin
composeTestRule.onRoot().printToLog("MERGED")
composeTestRule.onRoot(useUnmergedTree = true).printToLog("UNMERGED")
```

## Synchronization

```kotlin
// Wait for Compose-tracked work; this does not await arbitrary external IO
composeTestRule.waitForIdle()

// v2: run currently-queued clock work without waiting for real time
composeTestRule.mainClock.scheduler.runCurrent() // v2 scheduler

// Advance time explicitly (both v1 and v2)
composeTestRule.mainClock.advanceTimeBy(1000)

// Wait for an arbitrary condition
composeTestRule.waitUntil(timeoutMillis = 5000) {
    composeTestRule.onAllNodesWithTag("item").fetchSemanticsNodes().size >= 10
}
```

`registerIdlingResource`/`unregisterIdlingResource` still exist for Espresso interop when a Compose
screen shares a test with View-based Espresso code.

## Testing Patterns Worth Calling Out

- **`StateRestorationTester`** exercises save/restore without a real process death:
  `StateRestorationTester(composeTestRule)` then `restorationTester.emulateSavedInstanceStateRestore()`
  after `setContent`.
- **ViewModel tests should not go through the UI.** Test `StateFlow` emissions with Turbine/MockK
  against the ViewModel directly; a Compose UI test that only exercises the ViewModel through button
  clicks recreates the old inverted pyramid with new tools.
- **LazyColumn/LazyRow**: `performScrollToIndex(n)` scrolls to an item that may not yet be
  composed; assert visibility after the scroll completes, not before.
- Full finder/action/assertion syntax (by tag, by text, by content description, click/scroll/gesture
  actions, existence/state/content assertions) is standard Compose testing API surface — see the
  [API reference](https://developer.android.com/develop/ui/compose/testing/apis) rather than a
  restated catalogue here.

## Screenshot Testing

```kotlin
@Test
fun loginScreen_matchesSnapshot() {
    composeTestRule.setContent { LoginScreen() }
    val image = composeTestRule.onRoot().captureToImage()
    // Persist/compare `image` with your snapshot tool.
}
```

See `references/screenshot-testing.md` for tool choice (Compose Preview Screenshot Testing,
Paparazzi, Roborazzi) and CI wiring — this file only covers the in-test capture call.

## Debugging

```kotlin
composeTestRule.onRoot().printToLog("MERGED")
composeTestRule.onRoot(useUnmergedTree = true).printToLog("UNMERGED")
```

## Best Practices

### Do

- Use `testTag` for stable element identification.
- Test ViewModels independently of the UI (Turbine/MockK on `StateFlow`).
- Use `waitForIdle`/`runOnIdle`/`waitUntil` for async operations — never `Thread.sleep()`.
- Test state restoration with `StateRestorationTester`.
- Assert on semantic state, not reference equality — Strong Skipping Mode and `data class copy()`
  mean a re-composition may hand you a structurally-equal but non-identical instance.

### Avoid

- Relying on locale-sensitive text as the only selector.
- Treating a v2 migration failure as a harness bug before checking it isn't a real race.
- Over-specifying assertions against a merged node's full Text list when only one value matters —
  use `useUnmergedTree` or a narrower assertion instead.

## Resources

- [Compose Testing Documentation](https://developer.android.com/develop/ui/compose/testing)
- [Migrate to Compose Testing v2](https://developer.android.com/develop/ui/compose/testing/migrate-v2)
- [Compose Testing APIs](https://developer.android.com/develop/ui/compose/testing/apis)
- [Semantics in Compose](https://developer.android.com/develop/ui/compose/accessibility/semantics)
