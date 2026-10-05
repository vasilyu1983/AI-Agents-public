# Modern Android Test Tooling

Fills gaps not covered by the core Espresso/Compose/UI Automator guides: JUnit 5 on Android,
MockK, Turbine for coroutine flows, and Maestro for E2E scripting.

---

## Table of Contents

- [JUnit 5 on Android](#junit-5-on-android)
- [MockK](#mockk)
- [Turbine (Flow and StateFlow Testing)](#turbine-flow-and-stateflow-testing)
- [Maestro (E2E YAML Flows)](#maestro-e2e-yaml-flows)
- [Quick Reference](#quick-reference)

---

## JUnit 5 on Android

JUnit 5 (Jupiter) is not natively supported by the Android Gradle Plugin test runner, which
still expects JUnit 4. The `android-junit-framework` project (plugin ID `de.mannodermaus.android-junit`,
formerly `android-junit5`) bridges the gap by wrapping JUnit
5 tests in a JUnit 4-compatible runner so they work on-device and with instrumented test tasks
with `AndroidJUnitRunner` (or a subclass) configured as `testInstrumentationRunner` and
Jupiter API/BOM dependencies added to `androidTestImplementation`. Version 2.0+ also adds JUnit 6 compatibility — JUnit
6 itself requires Java 17 and a device/emulator at API 35+ (verified against the plugin README,
2026-09-23).

```kotlin
// build.gradle.kts (module)
plugins {
    // Plugin id is de.mannodermaus.android-junit (verified against the upstream README,
    // 2026-09-23) — not de.mannodermaus.android-junit5. Check the compatibility matrix at
    // https://github.com/mannodermaus/android-junit-framework for the current version.
    id("de.mannodermaus.android-junit") version "<project-approved-version>"
}

dependencies {
    // Unit tests (JVM) — align jupiter versions with the plugin's compatibility matrix
    testImplementation(platform("org.junit:junit-bom:<compatible-version>"))
    testImplementation("org.junit.jupiter:junit-jupiter-api")
    testImplementation("org.junit.jupiter:junit-jupiter-params")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine")

    // Instrumented tests: configure AndroidJUnitRunner in defaultConfig, then add:
    androidTestImplementation(platform("org.junit:junit-bom:<compatible-version>"))
    androidTestImplementation("org.junit.jupiter:junit-jupiter-api")
    // The plugin supplies its compatible instrumentation runtime.
}
```

```kotlin
// Example: parameterized unit test with Jupiter
import org.junit.jupiter.params.ParameterizedTest
import org.junit.jupiter.params.provider.ValueSource

class EmailValidatorTest {

    @ParameterizedTest
    @ValueSource(strings = ["user@example.com", "a@b.co"])
    fun `valid emails pass validation`(email: String) {
        assert(EmailValidator.isValid(email))
    }
}
```

Key differences from JUnit 4: use `@Test` from `org.junit.jupiter.api`, lifecycle callbacks
become `@BeforeEach`/`@AfterEach`/`@BeforeAll`/`@AfterAll`, and test classes and methods can
be package-private. Check the plugin's compatibility matrix before upgrading the engine version
independently of the plugin version — they must stay in sync.

---

## MockK

MockK is the idiomatic Kotlin mocking library. It understands Kotlin's object model: it can
mock `object` singletons, `companion object` members, extension functions, coroutine-aware
`suspend` functions, and Kotlin's top-level/extension-function style directly. Mockito 5 made the
inline mock maker the JVM default, so final-class support alone does not distinguish it from MockK.
This does not mean agent-free execution: on Java 21+, follow Mockito's
[explicit instrumentation setup](https://raw.githubusercontent.com/mockito/mockito/main/mockito-core/src/main/java/org/mockito/Mockito.java).
The [Mockito 5 migration](https://github.com/mockito/mockito/releases/tag/v5.0.0) did not change
Android mocking; for instrumented tests, check the installed `mockito-android` release's final-class,
API-level and manifest requirements separately. Prefer MockK for Kotlin object/extension/suspend
DSLs, and Mockito for existing Java suites.

```kotlin
dependencies {
    testImplementation("io.mockk:mockk:<project-approved-version>")
    androidTestImplementation("io.mockk:mockk-android:<project-approved-version>")
    // Select matching MockK artifacts from https://github.com/mockk/mockk/releases.
}
```

```kotlin
import io.mockk.*

class OrderServiceTest {

    private val repository = mockk<OrderRepository>()
    private val service = OrderService(repository)

    @Test
    fun `fetchOrder returns mapped domain model`() = runTest {
        val dto = OrderDto(id = "42", total = 9.99)
        coEvery { repository.fetchOrder("42") } returns dto

        val result = service.getOrder("42")

        assertThat(result.id).isEqualTo("42")
        coVerify(exactly = 1) { repository.fetchOrder("42") }
    }

    @Test
    fun `object singleton can be mocked`() {
        mockkObject(Analytics)
        every { Analytics.track(any()) } just Runs

        service.placeOrder(fakeOrder())

        verify { Analytics.track("order_placed") }
        unmockkObject(Analytics)
    }
}
```

Use `coEvery`/`coVerify` for `suspend` functions. Call `unmockkAll()` in `@AfterEach` (or use
`MockKExtension` with JUnit 5) to prevent mock leakage across tests.

---

## Turbine (Flow and StateFlow Testing)

Testing `Flow` and `StateFlow` emissions with `collect {}` in tests is fragile: you must manage
coroutine scopes manually, handle timing, and cancel collection yourself. Turbine, from Cash App,
provides a concise `turbineScope { }` API that drives collection without
`delay()` or `advanceUntilIdle()` gymnastics. `awaitItem()` suspends until the next emission,
`expectMostRecentItem()` receives the most recently emitted item and **consumes and discards**
every earlier item still queued (verified against the Turbine README, 2026-09-23 — it does not
leave the queue untouched), and `awaitComplete()`/`awaitError()` assert terminal states.

```kotlin
dependencies {
    testImplementation("app.cash.turbine:turbine:<project-approved-version>") // https://github.com/cashapp/turbine/releases
}
```

```kotlin
import app.cash.turbine.turbineScope
import app.cash.turbine.test
import app.cash.turbine.testIn
import kotlinx.coroutines.test.runTest

class CartViewModelTest {

    private val viewModel = CartViewModel(FakeCartRepository())

    // Simple single-flow assertion
    @Test
    fun `adding item emits updated cart state`() = runTest {
        viewModel.cartState.test {
            // Consume the initial emission
            val initial = awaitItem()
            assertThat(initial.items).isEmpty()

            viewModel.addItem(sampleItem())

            val updated = awaitItem()
            assertThat(updated.items).hasSize(1)
            cancelAndIgnoreRemainingEvents()
        }
    }

    // Turbine scope for multiple flows in one test
    @Test
    fun `checkout clears cart and emits loading then success`() = runTest {
        turbineScope {
            val cartTurbine = viewModel.cartState.testIn(backgroundScope)
            val uiTurbine = viewModel.uiEvents.testIn(backgroundScope)

            cartTurbine.awaitItem() // initial

            viewModel.checkout()

            assertThat(uiTurbine.awaitItem()).isInstanceOf(UiEvent.Loading::class.java)
            assertThat(uiTurbine.awaitItem()).isInstanceOf(UiEvent.Success::class.java)
            assertThat(cartTurbine.expectMostRecentItem().items).isEmpty()
        }
    }
}
```

Use `runTest { }` when controlling virtual time, and `backgroundScope` for long-lived
`testIn` collectors so they are cancelled at test completion. `turbineScope` itself does not
require `runTest`; consume terminal events for finite flows or cancel collection explicitly.

---

## Maestro (E2E YAML Flows)

Maestro is a mobile UI testing framework that drives real apps on simulators and devices using
declarative YAML flow files, with no compilation step. It connects to the device over ADB (Android)
or `xcrun simctl` (iOS), inspects the live accessibility tree, and replays flows. The CLI
`maestro test` command runs a flow. Before installation or cloud/AI integration, check the
[official CLI docs](https://docs.maestro.dev/maestro-cli/) and installed `maestro --help`; do not
assume a flow-generation command or cloud device matrix from older examples. Review generated
YAML before running it against the intended target.

```bash
# Inspect the installed command surface
maestro --help

# Run a reviewed local flow
maestro test flows/login.yaml
```

```yaml
# flows/login.yaml
appId: com.example.myapp
---
- launchApp
- tapOn:
    text: "Email"
- inputText: "user@example.com"
- tapOn:
    text: "Password"
- inputText: "test123"
- tapOn:
    text: "Log In"
- assertVisible:
    text: "Welcome"
- takeScreenshot: login_success
```

Maestro flows are well-suited for smoke tests, release-gate checks, and cross-platform flows
(the same YAML runs on Android and iOS with the same semantics). They are not a substitute for
Espresso or Compose tests for unit-level UI logic — reserve Maestro for high-level happy-path
and regression flows that must survive across builds without code changes.

---

## Robolectric

Robolectric is the standard JVM test runner for Android-framework-dependent unit tests. Current stable version — verify against the Robolectric release notes before pinning.

Key version constraints to re-check before pinning:

- Robolectric 4.17 added SDK 37 (Android 17) support; 4.16 added SDK 36 (Baklava) and removed
  SDK 21 and 22. Before setting `sdk = [...]`, check the release notes for the SDK range your
  installed release supports, and do not configure a level it does not list.
- SDK 36+ targets require JDK 21. Running Robolectric tests targeting SDK 36+ under JDK 17 throws:
  `"Android SDK 36 requires Java 21 (have Java 17)"`. Update your CI java-version to 21.
- `ResourcesMode.NATIVE` is an opt-in mode (SDK 36+) that uses native Android resource loading —
  prefer it for SDK 36+ targets when available.

```kotlin
// build.gradle.kts
android {
    testOptions {
        unitTests {
            isIncludeAndroidResources = true
        }
    }
}

dependencies {
    testImplementation("org.robolectric:robolectric:<project-approved-version>") // https://github.com/robolectric/robolectric/releases
}
```

When using SDK 36+ on CI, set `java-version: '21'` in `actions/setup-java`. Robolectric downloads
SDK jars at test time. `--dry-run` does **not** pre-warm that cache — Gradle's `--dry-run` prints
the task plan without executing any task action, so it does not run Robolectric or fetch its runtime SDK jar (Gradle may still resolve build-configuration dependencies). To pre-warm, either run one
real test task that exercises the target SDK, or configure Robolectric's offline-SDK jar
mechanism (`robolectric.offline` plus a dependency-jar setup) ahead of the CI run.

---

## Quick Reference

| Tool | Dependency group | Primary use case |
|------|-----------------|-----------------|
| `de.mannodermaus.android-junit` (android-junit-framework project) | Gradle plugin + `junit-jupiter-*` | JUnit 5 (and 6) syntax on Android (unit + instrumented) |
| MockK | `io.mockk:mockk` | Kotlin-first mocking: objects, suspend fns, finals |
| Turbine | `app.cash.turbine:turbine` | Deterministic `Flow`/`StateFlow` emission assertions |
| Maestro | CLI + YAML | E2E flows on device/simulator, LLM-generated scaffolding |
