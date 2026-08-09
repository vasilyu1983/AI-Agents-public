#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_android_common.sh"

usage() {
  cat <<'EOF'
Create and boot an Android Virtual Device for design iteration.

Usage:
  ./scripts/bootstrap-emulator.sh [options]

Options:
  --api LEVEL        API level (default: 35)
  --device ID        Device profile (default: pixel_8)
  --name NAME        AVD name (default: design_avd_api${API})
  --force            Delete existing AVD with the same name first
  -h, --help         Show this help
EOF
}

API="35"
DEVICE="pixel_8"
AVD_NAME=""
FORCE="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --api|--device|--name)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      case "$1" in
        --api) API="$2" ;;
        --device) DEVICE="$2" ;;
        --name) AVD_NAME="$2" ;;
      esac
      shift 2
      ;;
    --force)
      FORCE="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

if [[ -z "$AVD_NAME" ]]; then
  AVD_NAME="design_avd_api${API}"
fi

SYSTEM_IMAGE="system-images;android-${API};google_apis_playstore;x86_64"

resolve_avdmanager
resolve_emulator
resolve_adb

# Install system image if missing
if ! "$AVDMANAGER_CMD" list target 2>/dev/null | grep -q "android-${API}"; then
  echo "Installing system image: $SYSTEM_IMAGE"
  sdkmanager "$SYSTEM_IMAGE" || {
    echo "Could not install system image. Run: sdkmanager \"$SYSTEM_IMAGE\"" >&2
    exit 1
  }
fi

# Delete existing AVD if --force
if [[ "$FORCE" == "true" ]]; then
  "$AVDMANAGER_CMD" delete avd -n "$AVD_NAME" 2>/dev/null || true
fi

# Create AVD if it does not exist
if ! "$AVDMANAGER_CMD" list avd -c 2>/dev/null | grep -qx "$AVD_NAME"; then
  echo "Creating AVD: $AVD_NAME (device=$DEVICE, api=$API)"
  echo "no" | "$AVDMANAGER_CMD" create avd \
    -n "$AVD_NAME" \
    -k "$SYSTEM_IMAGE" \
    -d "$DEVICE" \
    --force
else
  echo "AVD already exists: $AVD_NAME"
fi

# Boot emulator in background
echo "Booting emulator: $AVD_NAME"
"$EMULATOR_CMD" -avd "$AVD_NAME" -no-snapshot-load -gpu auto &
EMULATOR_PID=$!

wait_for_boot

echo ""
echo "Emulator running (PID $EMULATOR_PID)."
echo "Next steps:"
echo "  ./scripts/run-android.sh --uninstall-first"
echo "  ./scripts/capture-screenshot.sh screenshots/current.png"
