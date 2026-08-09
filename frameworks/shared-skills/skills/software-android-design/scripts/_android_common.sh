#!/usr/bin/env bash
set -euo pipefail

# Shared helpers for Android design scripts.
# Source this file from sibling scripts:
#   SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
#   source "$SCRIPT_DIR/_android_common.sh"

ADB_CMD=""
EMULATOR_CMD=""
AVDMANAGER_CMD=""

resolve_adb() {
  if [[ -n "$ADB_CMD" ]]; then return 0; fi

  if command -v adb >/dev/null 2>&1; then
    ADB_CMD="adb"
    return 0
  fi

  if [[ -n "${ANDROID_HOME:-}" && -x "$ANDROID_HOME/platform-tools/adb" ]]; then
    ADB_CMD="$ANDROID_HOME/platform-tools/adb"
    return 0
  fi

  if [[ -n "${ANDROID_SDK_ROOT:-}" && -x "$ANDROID_SDK_ROOT/platform-tools/adb" ]]; then
    ADB_CMD="$ANDROID_SDK_ROOT/platform-tools/adb"
    return 0
  fi

  echo "adb not found. Set ANDROID_HOME or add platform-tools to PATH." >&2
  return 1
}

resolve_emulator() {
  if [[ -n "$EMULATOR_CMD" ]]; then return 0; fi

  if command -v emulator >/dev/null 2>&1; then
    EMULATOR_CMD="emulator"
    return 0
  fi

  if [[ -n "${ANDROID_HOME:-}" && -x "$ANDROID_HOME/emulator/emulator" ]]; then
    EMULATOR_CMD="$ANDROID_HOME/emulator/emulator"
    return 0
  fi

  if [[ -n "${ANDROID_SDK_ROOT:-}" && -x "$ANDROID_SDK_ROOT/emulator/emulator" ]]; then
    EMULATOR_CMD="$ANDROID_SDK_ROOT/emulator/emulator"
    return 0
  fi

  echo "emulator not found. Set ANDROID_HOME or add emulator/ to PATH." >&2
  return 1
}

resolve_avdmanager() {
  if [[ -n "$AVDMANAGER_CMD" ]]; then return 0; fi

  if command -v avdmanager >/dev/null 2>&1; then
    AVDMANAGER_CMD="avdmanager"
    return 0
  fi

  # Try cmdline-tools latest
  local candidates=(
    "${ANDROID_HOME:-}/cmdline-tools/latest/bin/avdmanager"
    "${ANDROID_SDK_ROOT:-}/cmdline-tools/latest/bin/avdmanager"
    "${ANDROID_HOME:-}/tools/bin/avdmanager"
    "${ANDROID_SDK_ROOT:-}/tools/bin/avdmanager"
  )

  for candidate in "${candidates[@]}"; do
    if [[ -x "$candidate" ]]; then
      AVDMANAGER_CMD="$candidate"
      return 0
    fi
  done

  echo "avdmanager not found. Install Android SDK Command-line Tools." >&2
  return 1
}

repo_root() {
  local git_root
  if git_root="$(git rev-parse --show-toplevel 2>/dev/null)"; then
    printf '%s\n' "$git_root"
    return 0
  fi
  pwd
}

discover_running_device() {
  resolve_adb
  local serial
  serial="$($ADB_CMD devices | grep -E 'device$' | head -n 1 | awk '{print $1}')" || true
  if [[ -n "$serial" ]]; then
    printf '%s\n' "$serial"
    return 0
  fi
  return 1
}

wait_for_boot() {
  resolve_adb
  local device="${1:-}"
  local device_flag=()
  if [[ -n "$device" ]]; then
    device_flag=(-s "$device")
  fi

  echo "Waiting for device to boot..." >&2
  $ADB_CMD "${device_flag[@]}" wait-for-device

  local attempts=0
  while [[ "$($ADB_CMD "${device_flag[@]}" shell getprop sys.boot_completed 2>/dev/null | tr -d '\r')" != "1" ]]; do
    if (( attempts++ > 60 )); then
      echo "Device did not finish booting after 60 seconds." >&2
      return 1
    fi
    sleep 1
  done
  echo "Device booted." >&2
}
