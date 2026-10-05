#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_xcodebuildmcp_common.sh"

usage() {
  cat <<'EOF'
Capture a Simulator screenshot through XcodeBuildMCP.

Usage:
  ./scripts/capture-screenshot.sh [output-path] [options]

Options:
  --simulator-id UUID
  --profile NAME
  -h, --help
EOF
}

OUTPUT_PATH=""
SIMULATOR_ID=""
PROFILE=""

if [[ $# -gt 0 && ! "$1" =~ ^- ]]; then
  OUTPUT_PATH="$1"
  shift
fi

while [[ $# -gt 0 ]]; do
  case "$1" in
    --simulator-id|--profile)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      if [[ "$1" == "--simulator-id" ]]; then
        SIMULATOR_ID="$2"
      else
        PROFILE="$2"
      fi
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

if [[ -z "$SIMULATOR_ID" ]]; then
  SIMULATOR_ID="$(discover_booted_simulator_id)"
fi

if [[ -z "$SIMULATOR_ID" ]]; then
  echo "Could not determine a booted simulator. Pass --simulator-id explicitly." >&2
  exit 1
fi

ARGS=(simulator screenshot --simulator-id "$SIMULATOR_ID" --return-format path --output text)
if [[ -n "$PROFILE" ]]; then
  ARGS+=(--profile "$PROFILE")
fi

RESULT="$(run_xcodebuildmcp "${ARGS[@]}")"
SOURCE_PATH="$(printf '%s\n' "$RESULT" | sed -n 's/^Screenshot captured: \([^ ]*\) .*/\1/p' | head -n 1)"

if [[ -z "$SOURCE_PATH" ]]; then
  echo "$RESULT"
  exit 1
fi

if [[ -z "$OUTPUT_PATH" ]]; then
  printf '%s\n' "$SOURCE_PATH"
  exit 0
fi

mkdir -p "$(dirname "$OUTPUT_PATH")"
cp "$SOURCE_PATH" "$OUTPUT_PATH"
printf '%s\n' "$OUTPUT_PATH"
