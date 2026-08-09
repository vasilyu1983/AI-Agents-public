# UI Automator Guide

System UI, cross-app, and benchmarking patterns using UI Automator.

**Official docs**: [Write automated tests with UI Automator](https://developer.android.com/training/testing/other-components/ui-automator)  
**Release notes**: [AndroidX Test UI Automator](https://developer.android.com/jetpack/androidx/releases/test-uiautomator)

## Table of Contents

- [When to Use UI Automator](#when-to-use-ui-automator)
- [2026 Default](#2026-default)
- [Setup](#setup)
- [Core Pattern (Modern DSL)](#core-pattern-modern-dsl)
- [Legacy Interop Pattern](#legacy-interop-pattern)
- [Common Tasks](#common-tasks)
- [Handle permission dialogs](#handle-permission-dialogs)
- [Start or reset the target app](#start-or-reset-the-target-app)
- [Work with multiple windows](#work-with-multiple-windows)
- [Capture screenshots and report artifacts](#capture-screenshots-and-report-artifacts)
- [Flake Control](#flake-control)
- [Benchmark And Baseline Profile Notes](#benchmark-and-baseline-profile-notes)
- [Resources](#resources)

## When to Use UI Automator

- System dialogs that Espresso or Compose cannot reach
- Cross-app flows such as browser, camera, account pickers, or share sheets
- Notifications, quick settings, and other system surfaces
- Macrobenchmark and baseline-profile drivers
- Multi-window or picture-in-picture interactions

Prefer Espresso or Compose Testing for in-app UI. Use UI Automator at the system boundary or when performance tooling needs app-driving APIs.

## 2026 Default

For new work, prefer the modern UI Automator 2.4 APIs and the `uiAutomator {}` scope. Keep `UiDevice` plus `By` or `Until` patterns only for legacy suites or when migrating incrementally.

As of 2026-07-11, UI Automator 2.4.0 is at release-candidate (`2.4.0-rc01`), not a final stable release — check the AndroidX release notes before pinning a specific patch in a shared template, since the RC-to-stable jump can still change API surface.

## Setup

Add UI Automator as an instrumented-test dependency and align versions with your AndroidX Test stack:

```kotlin
dependencies {
    androidTestImplementation("androidx.test.uiautomator:uiautomator:<latest-stable-or-beta>")
}
```

Check the AndroidX release notes before pinning a version in documentation or templates.

## Core Pattern (Modern DSL)

```kotlin
import androidx.test.ext.junit.runners.AndroidJUnit4
import androidx.test.uiautomator.PermissionDialog
import androidx.test.uiautomator.uiAutomator
import org.junit.Test
import org.junit.runner.RunWith

@RunWith(AndroidJUnit4::class)
class PermissionsTest {
    @Test
    fun grantsPermission() = uiAutomator {
        watchFor(PermissionDialog) { clickAllow() }

        startApp("com.example.targetapp")
        onElement { textAsString() == "Continue" }.click()
        onElement { viewIdResourceName == "com.example.targetapp:id/status" }
    }
}
```

What the 2.4-style APIs improve:

- `uiAutomator {}` gives a focused automation scope instead of scattered `UiDevice` calls.
- `onElement`, `onElements`, and `onElementOrNull` make selectors easier to read and reason about.
- `watchFor(...)` handles unexpected dialogs such as permissions more cleanly than ad-hoc polling.
- `waitForAppToBeVisible`, `waitForStable`, and related helpers reduce flaky timing assumptions.
- Screenshots and `ResultsReporter` help collect richer debugging artifacts.

## Legacy Interop Pattern

If your suite still uses the classic API, this remains valid while you migrate:

```kotlin
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.Until

val instrumentation = InstrumentationRegistry.getInstrumentation()
val device = UiDevice.getInstance(instrumentation)

device.wait(Until.hasObject(By.textContains("Allow")), 5_000)
device.findObject(By.textContains("Allow"))?.click()
```

Prefer resource-id or content-description over localized text whenever the system image exposes stable identifiers.

## Common Tasks

### Handle permission dialogs

```kotlin
import androidx.test.uiautomator.PermissionDialog

uiAutomator {
    watchFor(PermissionDialog) { clickAllow() }
    startApp("com.example.targetapp")
}
```

If you fully control the permission state, `GrantPermissionRule` is simpler than interacting with dialogs.

### Start or reset the target app

```kotlin
uiAutomator {
    clearAppData("com.example.targetapp")
    startApp("com.example.targetapp")
    waitForAppToBeVisible("com.example.targetapp")
}
```

This is especially useful for self-instrumenting benchmark or baseline-profile tests.

### Work with multiple windows

```kotlin
uiAutomator {
    val pipWindow = windows().first { it.isInPictureInPictureMode == true }
    pipWindow.onElement { textAsString() == "Play" }.click()
}
```

### Capture screenshots and report artifacts

Use UI Automator screenshots for debugging, failure triage, or visual checkpoints around cross-app flows. Prefer saving these as artifacts rather than comparing whole-device screenshots in a flaky way.

## Flake Control

- Prefer explicit conditions over sleeps.
- Register watchers only for truly unexpected UI.
- Validate selectors on the same device images you run in CI.
- Keep OEM-specific assumptions out of portable tests.
- For visual fidelity, remember that ATD disables hardware rendering.

## Benchmark And Baseline Profile Notes

UI Automator is not only for functional tests. It is also the standard driver for many macrobenchmark and baseline-profile scenarios because it can start activities, wait for app visibility, and interact with release builds from outside the app process.

## Resources

- [UI Automator setup guide](https://developer.android.com/training/testing/other-components/ui-automator)
- [UI Automator release notes](https://developer.android.com/jetpack/androidx/releases/test-uiautomator)
- [Macrobenchmark](https://developer.android.com/studio/profile/macrobenchmark)
- [Baseline Profiles](https://developer.android.com/topic/performance/baselineprofiles)
