#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_android_common.sh"

usage() {
  cat <<'EOF'
Dump the UI hierarchy of the current screen via uiautomator for structure review.

Usage:
  ./scripts/layout-inspector.sh [output-path] [options]

Arguments:
  output-path       Where to save the XML dump (default: prints to stdout)

Options:
  --device SERIAL    Target device serial (default: first connected device)
  -h, --help         Show this help

Examples:
  ./scripts/layout-inspector.sh hierarchy/current.xml
  ./scripts/layout-inspector.sh --device emulator-5554
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

# Dump UI hierarchy on device
DEVICE_DUMP_PATH="/sdcard/window_dump.xml"
$ADB_CMD "${DEVICE_FLAG[@]}" shell uiautomator dump "$DEVICE_DUMP_PATH" >/dev/null 2>&1

if [[ -z "$OUTPUT_PATH" ]]; then
  # Print to stdout
  $ADB_CMD "${DEVICE_FLAG[@]}" shell cat "$DEVICE_DUMP_PATH"
else
  mkdir -p "$(dirname "$OUTPUT_PATH")"
  $ADB_CMD "${DEVICE_FLAG[@]}" pull "$DEVICE_DUMP_PATH" "$OUTPUT_PATH" >/dev/null 2>&1
  echo "$OUTPUT_PATH"
fi

# Clean up device file
$ADB_CMD "${DEVICE_FLAG[@]}" shell rm -f "$DEVICE_DUMP_PATH" 2>/dev/null || true
