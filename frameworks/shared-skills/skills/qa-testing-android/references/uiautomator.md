# UIAutomator Guide

System UI and cross-app testing patterns using UIAutomator.

Official docs: https://developer.android.com/training/testing/other-components/ui-automator

## When to Use UIAutomator

- System dialogs (permissions, settings, biometric prompts) that Espresso/Compose cannot reach
- Cross-app flows (browser, camera picker, share sheet)
- Notifications and Quick Settings

Prefer Espresso/Compose for in-app UI; use UIAutomator only for the system boundary.

## Setup

Add UIAutomator as an instrumented-test dependency (align versions with your AndroidX Test stack):

```kotlin
dependencies {
    // Preferred: version catalogs (names may vary in your project).
    androidTestImplementation(libs.androidx.test.uiautomator)
}
```

## Core Pattern

```kotlin
import androidx.test.platform.app.InstrumentationRegistry
import androidx.test.uiautomator.By
import androidx.test.uiautomator.UiDevice
import androidx.test.uiautomator.Until

val instrumentation = InstrumentationRegistry.getInstrumentation()
val device = UiDevice.getInstance(instrumentation)

device.waitForIdle()
```

### Waits (Avoid Sleeps)

```kotlin
val timeoutMs = 5_000L
device.wait(Until.hasObject(By.textContains("Allow")), timeoutMs)
device.findObject(By.textContains("Allow"))?.click()
```

Notes:
- Text-based selectors are locale-sensitive. Prefer resource-id/content-desc when stable in your device image.
- For runtime permissions, prefer `GrantPermissionRule` (Espresso) instead of clicking dialogs.

## Common Tasks

### Open Notifications / Quick Settings

```kotlin
device.openNotification()
device.waitForIdle()
```

### Dismiss a System Dialog (Best-Effort)

```kotlin
device.pressBack()
device.waitForIdle()
```

### Cross-App Launch (Example: Browser)

```kotlin
val intent = instrumentation.context.packageManager.getLaunchIntentForPackage("com.android.chrome")
requireNotNull(intent).addFlags(android.content.Intent.FLAG_ACTIVITY_CLEAR_TASK)
instrumentation.context.startActivity(intent)
device.wait(Until.hasObject(By.pkg("com.android.chrome").depth(0)), 10_000)
```

## Flake Control

- Prefer ATD/managed devices in CI for consistency.
- Keep waits explicit (`Until.*`) and timeouts reasonable; fail fast with diagnostics (screenshot/logcat).
- Avoid depending on OEM-specific UI; validate selectors on the device images in your matrix.

