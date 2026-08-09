#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_android_common.sh"

usage() {
  cat <<'EOF'
Build the Android app module using Gradle.

Usage:
  ./scripts/build-android.sh [options] [-- extra Gradle args]

Options:
  --module NAME       Gradle module (default: app)
  --variant NAME      Build variant (default: Debug)
  --extra-args ARGS   Additional Gradle arguments
  -h, --help          Show this help
EOF
}

MODULE="app"
VARIANT="Debug"
EXTRA_ARGS=()

while [[ $# -gt 0 ]]; do
  case "$1" in
    --module|--variant)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      case "$1" in
        --module) MODULE="$2" ;;
        --variant) VARIANT="$2" ;;
      esac
      shift 2
      ;;
    --extra-args)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      EXTRA_ARGS+=("$2")
      shift 2
      ;;
    --)
      shift
      EXTRA_ARGS+=("$@")
      break
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

PROJECT_ROOT="$(repo_root)"
GRADLEW="$PROJECT_ROOT/gradlew"

if [[ ! -x "$GRADLEW" ]]; then
  echo "gradlew not found at $GRADLEW" >&2
  echo "Run this script from the project root or ensure gradlew exists." >&2
  exit 1
fi

TASK=":${MODULE}:assemble${VARIANT}"
echo "Building $TASK"
"$GRADLEW" "$TASK" "${EXTRA_ARGS[@]}" --console=plain
echo "Build complete: $TASK"
