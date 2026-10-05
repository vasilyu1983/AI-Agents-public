#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_android_common.sh"

usage() {
  cat <<'EOF'
Capture a screenshot from a connected Android device or emulator via ADB.

Usage:
  ./scripts/capture-screenshot.sh [output-path] [options]

Arguments:
  output-path       Where to save the PNG (default: prints to stdout)

Options:
  --device SERIAL    Target device serial (default: first connected device)
  -h, --help         Show this help

Examples:
  ./scripts/capture-screenshot.sh screenshots/before.png
  ./scripts/capture-screenshot.sh --device emulator-5554 screenshots/current.png
EOF
}

OUTPUT_PATH=""
DEVICE_SERIAL=""

# First positional argument is the output path
if [[ $# -gt 0 && ! "$1" =~ ^- ]]; then
  OUTPUT_PATH="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --device)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      DEVICE_SERIAL="$2"
      shift 2
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

resolve_adb

DEVICE_FLAG=()
if [[ -n "$DEVICE_SERIAL" ]]; then
  DEVICE_FLAG=(-s "$DEVICE_SERIAL")
elif DEVICE_SERIAL="$(discover_running_device)"; then
  DEVICE_FLAG=(-s "$DEVICE_SERIAL")
fi

if [[ -z "$DEVICE_SERIAL" ]]; then
  echo "No connected device found. Pass --device SERIAL or boot an emulator." >&2
  exit 1
fi

if [[ -z "$OUTPUT_PATH" ]]; then
  # Stream PNG to stdout
  $ADB_CMD "${DEVICE_FLAG[@]}" exec-out screencap -p
else
  mkdir -p "$(dirname "$OUTPUT_PATH")"
  $ADB_CMD "${DEVICE_FLAG[@]}" exec-out screencap -p > "$OUTPUT_PATH"
  echo "$OUTPUT_PATH"
fi
