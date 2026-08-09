#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_xcodebuildmcp_common.sh"

usage() {
  cat <<'EOF'
Run simulator tests through XcodeBuildMCP.

Usage:
  ./scripts/test-ios.sh [unit|ui|all] [options] [-- extra xcodebuild args]

Modes:
  unit  Alias for compile/test flow without additional filtering.
  ui    Alias for compile/test flow without additional filtering.
  all   Default mode.

Notes:
  XcodeBuildMCP exposes suite filtering through --json testRunnerEnv or extra args.
  For repo-specific target filtering, pass extra xcodebuild arguments after --.

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

MODE="all"
if [[ $# -gt 0 && ! "$1" =~ ^- ]]; then
  MODE="$1"
  shift
fi

case "$MODE" in
  unit|ui|all)
    ;;
  *)
    echo "Unknown mode: $MODE" >&2
    usage >&2
    exit 1
    ;;
esac

ARGS=(simulator test)

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

if [[ "$MODE" != "all" ]]; then
  echo "Note: mode '$MODE' is a naming convenience only. Pass repo-specific target filters after -- if needed." >&2
fi

run_xcodebuildmcp "${ARGS[@]}"
