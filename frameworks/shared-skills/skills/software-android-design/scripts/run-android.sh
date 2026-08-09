#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_android_common.sh"

usage() {
  cat <<'EOF'
Build, optionally uninstall, install, and launch the Android app on a connected device or emulator.

Usage:
  ./scripts/run-android.sh [options]

Options:
  --module NAME        Gradle module (default: app)
  --variant NAME       Build variant (default: Debug)
  --package ID         Application package ID (auto-detected from merged manifest if omitted)
  --activity NAME      Launch activity (default: auto-detected main launcher)
  --uninstall-first    Uninstall existing app before installing (recommended for design loops)
  -h, --help           Show this help
EOF
}

MODULE="app"
VARIANT="Debug"
PACKAGE=""
ACTIVITY=""
UNINSTALL_FIRST="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --module|--variant|--package|--activity)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      case "$1" in
        --module) MODULE="$2" ;;
        --variant) VARIANT="$2" ;;
        --package) PACKAGE="$2" ;;
        --activity) ACTIVITY="$2" ;;
      esac
      shift 2
      ;;
    --uninstall-first)
      UNINSTALL_FIRST="true"
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

resolve_adb

PROJECT_ROOT="$(repo_root)"
GRADLEW="$PROJECT_ROOT/gradlew"

if [[ ! -x "$GRADLEW" ]]; then
  echo "gradlew not found at $GRADLEW" >&2
  exit 1
fi

VARIANT_LOWER="$(echo "$VARIANT" | tr '[:upper:]' '[:lower:]')"
TASK=":${MODULE}:assemble${VARIANT}"

echo "==> Building $TASK"
"$GRADLEW" "$TASK" --console=plain

# Locate the APK
APK_DIR="$PROJECT_ROOT/$MODULE/build/outputs/apk/$VARIANT_LOWER"
APK="$(find "$APK_DIR" -name '*.apk' -type f | head -n 1 2>/dev/null)" || true

if [[ -z "$APK" ]]; then
  echo "APK not found in $APK_DIR" >&2
  exit 1
fi
echo "==> APK: $APK"

# Auto-detect package from APK if not specified
if [[ -z "$PACKAGE" ]]; then
  PACKAGE="$($ADB_CMD shell pm dump 2>/dev/null | head -1 || true)"
  # Fallback: parse from aapt
  if command -v aapt2 >/dev/null 2>&1; then
    PACKAGE="$(aapt2 dump badging "$APK" 2>/dev/null | grep 'package: name=' | sed "s/.*name='\\([^']*\\)'.*/\\1/" || true)"
  elif command -v aapt >/dev/null 2>&1; then
    PACKAGE="$(aapt dump badging "$APK" 2>/dev/null | grep 'package: name=' | sed "s/.*name='\\([^']*\\)'.*/\\1/" || true)"
  fi

  if [[ -z "$PACKAGE" ]]; then
    echo "Could not auto-detect package. Pass --package explicitly." >&2
    exit 1
  fi
fi
echo "==> Package: $PACKAGE"

# Uninstall if requested
if [[ "$UNINSTALL_FIRST" == "true" ]]; then
  echo "==> Uninstalling $PACKAGE"
  $ADB_CMD uninstall "$PACKAGE" 2>/dev/null || echo "    (not installed)"
fi

# Install
echo "==> Installing $APK"
$ADB_CMD install -r "$APK"

# Launch
if [[ -n "$ACTIVITY" ]]; then
  COMPONENT="$PACKAGE/$ACTIVITY"
else
  COMPONENT="$($ADB_CMD shell cmd package resolve-activity --brief -a android.intent.action.MAIN -c android.intent.category.LAUNCHER "$PACKAGE" 2>/dev/null | tail -n 1 | tr -d '\r')" || true
fi

if [[ -n "$COMPONENT" ]]; then
  echo "==> Launching $COMPONENT"
  $ADB_CMD shell am start -n "$COMPONENT"
else
  echo "==> Could not determine launch activity. Start the app manually." >&2
fi

echo "==> Done."
