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
still expects JUnit 4. The `de.mannodermaus.android-junit-framework` Gradle plugin (formerly
`android-junit5`, renamed in 2026 for its tenth anniversary) bridges the gap by wrapping JUnit
5 tests in a JUnit 4-compatible runner so they work on-device and with instrumented test tasks
without any additional runner configuration. Version 2.0+ also adds JUnit 6 compatibility, so
the project is no longer tied to a single JUnit generation.

```kotlin
// build.gradle.kts (module)
plugins {
    // Renamed from de.mannodermaus.android-junit5 in 2026; check the compatibility matrix
    // at https://github.com/mannodermaus/android-junit-framework for the current version.
    id("de.mannodermaus.android-junit5") version "2.0.1"
}

dependencies {
    // Unit tests (JVM) — align jupiter versions with the plugin's compatibility matrix
    testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.4")
    testImplementation("org.junit.jupiter:junit-jupiter-params:5.11.4")
    testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.11.4")

    // Instrumented tests (on-device) — requires the plugin
    androidTestImplementation("de.mannodermaus.junit5:android-test-core:1.6.0")
    androidTestRuntimeOnly("de.mannodermaus.junit5:android-test-runner:1.6.0")
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
`suspend` functions, and `final` classes without extra configuration (unlike Mockito, which
requires the `mockito-kotlin` wrapper and an `open-mocking` agent). Prefer MockK for all new
Kotlin tests; reserve Mockito for pre-existing Java test suites where migration cost is not
justified.

```kotlin
dependencies {
    testImplementation("io.mockk:mockk:1.14.3")
    androidTestImplementation("io.mockk:mockk-android:1.14.3")
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
provides a concise `turbineScope { }` API that drives collection deterministically without
`delay()` or `advanceUntilIdle()` gymnastics. `awaitItem()` suspends until the next emission,
`expectMostRecentItem()` asserts the latest emitted value without consuming the queue, and
`awaitComplete()`/`awaitError()` assert terminal states.

```kotlin
dependencies {
    testImplementation("app.cash.turbine:turbine:1.2.1")
}
```

```kotlin
import app.cash.turbine.turbineScope
import app.cash.turbine.test
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

Run Turbine tests inside `runTest { }` from `kotlinx-coroutines-test` so the test dispatcher
controls time. Avoid `turbineScope` outside `runTest` — coroutine cancellation behaviour
differs in unconfined dispatchers and can produce spurious failures.

---

## Maestro (E2E YAML Flows)

Maestro is a mobile UI testing framework that drives real apps on simulators and devices using
declarative YAML flow files, with no compilation step. It connects to the device over ADB (Android)
or `xcrun simctl` (iOS), inspects the live accessibility tree, and replays flows. The CLI
`maestro test` command runs a single flow; `maestro cloud` runs a flow matrix on Maestro's cloud
device farm. MaestroGPT (`maestro ai`) accepts a natural-language prompt and generates a YAML
flow, which is useful for rapid scaffolding — always review the generated output before committing.
API 35 and 36 support arrived in 2026 (Maestro Cloud lagged local support by roughly a quarter,
per upstream issue tracking); API 37 (Android 17, shipped 2026-06-16) support is **unverified as
of 2026-07-11** — check the current release notes before targeting Android 17 devices, especially
on Maestro Cloud.

```bash
# Install (see https://maestro.dev for the current install command)
brew install maestro  # macOS
# or
curl -Ls "https://get.maestro.mobile.dev" | bash

# Run a flow
maestro test flows/login.yaml

# Generate a flow with MaestroGPT (requires MAESTRO_CLOUD_API_KEY)
maestro ai "Log in with email user@example.com and password test123"
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

Robolectric is the standard JVM test runner for Android-framework-dependent unit tests. Current stable version is 4.16.x.

Key version constraints for 2026:

- Robolectric 4.16 supports Android Baklava (SDK 36, API level 36) and removes support for Android L (SDK 21 and 22).
- SDK 36 targets require JDK 21. Running Robolectric tests targeting SDK 36 under JDK 17 throws: `"Android SDK 36 requires Java 21 (have Java 17)"`. Update your CI java-version to 21 when testing against SDK 36.
- `ResourcesMode.NATIVE` is a new opt-in mode (SDK 36 only) that uses native Android resource loading — prefer it for SDK 36 targets when available.
- Android 17 (API level 37) shipped 2026-06-16. As of 2026-07-11, Robolectric does **not** yet support API 37 — this is tracked in an open upstream issue (robolectric/robolectric#11239, filed 2026-06-14). Do not configure `sdk = [37]` in Robolectric annotations yet; keep JVM unit tests targeting SDK 36 until a Robolectric release adds API 37 support, and re-check the release notes before assuming coverage.

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
    testImplementation("org.robolectric:robolectric:4.16.1")
}
```

When using SDK 36 on CI, set `java-version: '21'` in `actions/setup-java`. Robolectric downloads SDK jars at test time; pre-warm the cache in CI with `./gradlew roborazziTest --dry-run` or a dedicated task.

---

## Quick Reference

| Tool | Dependency group | Primary use case |
|------|-----------------|-----------------|
| `de.mannodermaus.android-junit-framework` (formerly `android-junit5`) | Gradle plugin + `junit-jupiter-*` | JUnit 5 (and 6) syntax on Android (unit + instrumented) |
| MockK | `io.mockk:mockk` | Kotlin-first mocking: objects, suspend fns, finals |
| Turbine | `app.cash.turbine:turbine` | Deterministic `Flow`/`StateFlow` emission assertions |
| Maestro | CLI + YAML | E2E flows on device/simulator, LLM-generated scaffolding |
