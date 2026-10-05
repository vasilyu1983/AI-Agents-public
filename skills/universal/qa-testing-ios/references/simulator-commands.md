# iOS Simulator Commands

Current `simctl` commands worth using in automation. Prefer documented, stable operations over obscure subcommands.

Primary doc:

- https://developer.apple.com/documentation/xcode/simctl

## Discovery

```bash
xcrun simctl list devices available
xcrun simctl list runtimes
xcrun simctl list devicetypes
xcrun simctl list devices --json
```

## Boot And Reset

```bash
xcrun simctl boot "<simulator-name>"
xcrun simctl bootstatus booted -b
xcrun simctl shutdown "<simulator-name>"
xcrun simctl shutdown all
xcrun simctl erase "<simulator-name>"
xcrun simctl erase all
xcrun simctl delete unavailable
```

Use erase sparingly in CI. It improves determinism, but it also costs time.

## Create Or Clone

Verify the runtime identifier before copying a create command.

```bash
# Runtime identifier must exist in this environment
xcrun simctl create "CI-iPhone" "<device-type>" "<runtime-id>"

# Clone only when you have confirmed the base simulator exists
xcrun simctl clone "<existing-simulator>" "CI-iPhone-Worker-1"
```

## App Lifecycle

```bash
xcrun simctl install booted /path/to/MyApp.app
xcrun simctl uninstall booted com.example.myapp
xcrun simctl launch booted com.example.myapp
xcrun simctl launch --console booted com.example.myapp
xcrun simctl terminate booted com.example.myapp
xcrun simctl get_app_container booted com.example.myapp
```

Prefer launching through XCUITest when the goal is test coverage, and use direct `simctl launch` for setup or debugging.

## Media And URLs

```bash
xcrun simctl io booted screenshot screenshot.png
xcrun simctl io booted screenshot --type=jpeg screenshot.jpg
xcrun simctl io booted recordVideo recording.mov
xcrun simctl openurl booted "myapp://debug/reset"
xcrun simctl openurl booted "https://example.com/app-link"
```

This reference intentionally omits undocumented or unverified input-injection examples. Re-check Apple docs before using any `simctl io` action beyond screenshot and video capture.

## Permissions And Device State

```bash
xcrun simctl privacy booted grant photos com.example.myapp
xcrun simctl privacy booted revoke camera com.example.myapp
xcrun simctl privacy booted reset all com.example.myapp

xcrun simctl location booted set 37.7749,-122.4194
xcrun simctl location booted clear

xcrun simctl status_bar booted override \
  --time "9:41" \
  --batteryState charged \
  --batteryLevel 100

xcrun simctl status_bar booted clear
```

Use status-bar overrides for deterministic screenshots, not general UI-test execution.

## Push Notifications

```bash
xcrun simctl push booted com.example.myapp notification.apns
echo '{"aps":{"alert":"Test"}}' | xcrun simctl push booted com.example.myapp -
```

## CI Guardrails

- Never assume a simulator name or runtime exists. Check first.
- Prefer placeholders like `<simulator-name>` and `<runtime-id>` in shared docs.
- If the environment is unstable, capture the output of `simctl list devices available` in logs.
