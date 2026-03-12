# iOS Simulator Commands Reference

Complete `simctl` command reference for iOS simulator automation.

## Contents

- [Device Management](#device-management)
- [App Management](#app-management)
- [I/O Operations](#io-operations)
- [Device State](#device-state)
- [Push Notifications](#push-notifications)
- [Media and Files](#media-and-files)
- [Diagnostics](#diagnostics)
- [Scripting Patterns](#scripting-patterns)
- [Environment Variables](#environment-variables)
- [Related](#related)

---

## Device Management

### List Devices

```bash
# All devices with runtimes
xcrun simctl list devices

# Available runtimes only
xcrun simctl list runtimes

# Booted devices only
xcrun simctl list devices | grep "Booted"

# Device types
xcrun simctl list devicetypes

# JSON output (for scripting)
xcrun simctl list devices --json
```

### Boot and Shutdown

```bash
# Boot by name
xcrun simctl boot "iPhone 15 Pro"

# Boot by UDID
xcrun simctl boot 12345678-ABCD-1234-ABCD-123456789ABC

# Shutdown specific device
xcrun simctl shutdown "iPhone 15 Pro"

# Shutdown all
xcrun simctl shutdown all

# Erase (factory reset)
xcrun simctl erase "iPhone 15 Pro"

# Erase all
xcrun simctl erase all
```

### Create and Delete

```bash
# Create new simulator
xcrun simctl create "My Test iPhone" "iPhone 15" "iOS-17-2"

# Clone existing
xcrun simctl clone "iPhone 15 Pro" "iPhone 15 Pro Clone"

# Delete simulator
xcrun simctl delete "My Test iPhone"

# Delete unavailable (cleanup)
xcrun simctl delete unavailable
```

---

## App Management

### Install and Uninstall

```bash
# Install app bundle
xcrun simctl install booted /path/to/MyApp.app

# Install on specific device
xcrun simctl install "iPhone 15" /path/to/MyApp.app

# Uninstall by bundle ID
xcrun simctl uninstall booted com.example.myapp

# Get app container path
xcrun simctl get_app_container booted com.example.myapp
```

### Launch and Terminate

```bash
# Launch app
xcrun simctl launch booted com.example.myapp

# Launch with arguments
xcrun simctl launch booted com.example.myapp --argument1 --argument2

# Launch and wait for debugger
xcrun simctl launch --wait-for-debugger booted com.example.myapp

# Launch with console output
xcrun simctl launch --console booted com.example.myapp

# Terminate app
xcrun simctl terminate booted com.example.myapp
```

---

## I/O Operations

### Screenshots

```bash
# PNG screenshot
xcrun simctl io booted screenshot screenshot.png

# JPEG screenshot
xcrun simctl io booted screenshot --type=jpeg screenshot.jpg

# Specific device
xcrun simctl io "iPhone 15 Pro" screenshot home.png

# With mask (device frame)
xcrun simctl io booted screenshot --mask=black screenshot.png
```

### Video Recording

```bash
# Start recording (Ctrl+C to stop)
xcrun simctl io booted recordVideo recording.mov

# With codec
xcrun simctl io booted recordVideo --codec=h264 recording.mp4

# Force overwrite
xcrun simctl io booted recordVideo --force recording.mov
```

### Touch Input

```bash
# Tap at coordinates
xcrun simctl io booted tap 200 400

# Swipe (x1 y1 x2 y2)
xcrun simctl io booted swipe 100 500 100 200

# Type text
xcrun simctl io booted type "Hello World"

# Paste from clipboard
xcrun simctl io booted paste

# Press home button
xcrun simctl io booted home
```

---

## Device State

### Location

```bash
# Set GPS coordinates
xcrun simctl location booted set 37.7749,-122.4194

# Set with scenario
xcrun simctl location booted set --scenario=freeway

# Clear location
xcrun simctl location booted clear

# Available scenarios: none, freeway, city, hiking
```

### Privacy Permissions

```bash
# Grant permission
xcrun simctl privacy booted grant photos com.example.myapp

# Revoke permission
xcrun simctl privacy booted revoke camera com.example.myapp

# Reset all permissions
xcrun simctl privacy booted reset all com.example.myapp

# Permission types: all, calendar, contacts, location,
#   location-always, photos, photos-add, media-library,
#   microphone, camera, reminders, siri
```

### Status Bar

```bash
# Override status bar
xcrun simctl status_bar booted override \
  --time "9:41" \
  --batteryState charged \
  --batteryLevel 100 \
  --cellularMode active \
  --cellularBars 4

# Clear overrides
xcrun simctl status_bar booted clear
```

---

## Push Notifications

### Send Push

```bash
# Send from file
xcrun simctl push booted com.example.myapp notification.apns

# Send inline JSON
echo '{"aps":{"alert":"Test"}}' | xcrun simctl push booted com.example.myapp -
```

### APNS Payload Examples

```json
// Basic alert
{
  "aps": {
    "alert": "Hello World"
  }
}

// Rich notification
{
  "aps": {
    "alert": {
      "title": "New Message",
      "subtitle": "From John",
      "body": "Hey, how are you?"
    },
    "badge": 5,
    "sound": "default",
    "category": "MESSAGE"
  },
  "customData": {
    "messageId": "12345"
  }
}

// Silent push
{
  "aps": {
    "content-available": 1
  }
}
```

---

## Media and Files

### Add Media

```bash
# Add photo
xcrun simctl addmedia booted photo.jpg

# Add video
xcrun simctl addmedia booted video.mp4

# Add multiple
xcrun simctl addmedia booted photo1.jpg photo2.jpg video.mp4
```

### Open URL

```bash
# Open URL in Safari
xcrun simctl openurl booted "https://example.com"

# Open deep link
xcrun simctl openurl booted "myapp://path/to/screen"

# Open universal link
xcrun simctl openurl booted "https://example.com/app-link"
```

---

## Diagnostics

### Logs

```bash
# Spawn log stream
xcrun simctl spawn booted log stream --predicate 'subsystem == "com.example.myapp"'

# System log
xcrun simctl spawn booted log show --last 1h

# Collect diagnostics
xcrun simctl diagnose
```

### Device Info

```bash
# Get device UDID
xcrun simctl list devices | grep "iPhone 15"

# Boot status
xcrun simctl bootstatus booted

# Environment info
xcrun simctl getenv booted HOME
```

---

## Scripting Patterns

### Wait for Boot

```bash
#!/bin/bash
DEVICE="iPhone 15 Pro"

xcrun simctl boot "$DEVICE"
xcrun simctl bootstatus "$DEVICE" -b
echo "Simulator ready"
```

### Batch Screenshot

```bash
#!/bin/bash
DEVICES=("iPhone 15" "iPhone 15 Pro" "iPad Pro (12.9-inch)")

for device in "${DEVICES[@]}"; do
  xcrun simctl boot "$device"
  xcrun simctl bootstatus "$device" -b
  xcrun simctl io "$device" screenshot "${device// /-}.png"
  xcrun simctl shutdown "$device"
done
```

### Clean Environment

```bash
#!/bin/bash
# Reset all simulators to clean state
xcrun simctl shutdown all
xcrun simctl erase all
echo "All simulators reset"
```

---

## Environment Variables

| Variable | Purpose |
|----------|---------|
| `SIMCTL_CHILD_*` | Pass env vars to simulator |
| `SIMULATOR_DEVICE_NAME` | Current device name |
| `SIMULATOR_UDID` | Current device UDID |
| `SIMULATOR_RUNTIME_VERSION` | iOS version |

```bash
# Set env var in simulator
export SIMCTL_CHILD_MY_VAR="value"
xcrun simctl boot "iPhone 15"
```

---

## Related

- [Apple simctl Documentation](https://developer.apple.com/documentation/xcode/simctl)
- [Testing Hardware Scenarios](https://developer.apple.com/documentation/xcode/testing-complex-hardware-device-scenarios-in-simulator)
