#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_xcodebuildmcp_common.sh"

usage() {
  cat <<'EOF'
Build the current iOS app for Simulator using XcodeBuildMCP.

Usage:
  ./scripts/build-ios.sh [options] [-- extra xcodebuild args]

Options:
  --project-path PATH
  --workspace-path PATH
  --scheme NAME
  --configuration NAME
  --derived-data-path PATH
  --simulator-id UUID
  --simulator-name NAME
  --profile NAME
  --output text|json
  --json JSON
  --use-latest-os
  --prefer-xcodebuild
  -h, --help
EOF
}

ARGS=(simulator build)

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-path|--workspace-path|--scheme|--configuration|--derived-data-path|--simulator-id|--simulator-name|--profile|--output|--json)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      ARGS+=("$1" "$2")
      shift 2
      ;;
    --use-latest-os|--prefer-xcodebuild)
      ARGS+=("$1")
      shift
      ;;
    --)
      shift
      while [[ $# -gt 0 ]]; do
        ARGS+=(--extra-args "$1")
        shift
      done
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

run_xcodebuildmcp "${ARGS[@]}"
