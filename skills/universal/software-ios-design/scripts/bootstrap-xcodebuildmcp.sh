#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
source "$SCRIPT_DIR/_xcodebuildmcp_common.sh"

usage() {
  cat <<'EOF'
Verify XcodeBuildMCP availability and scaffold a repo-local .xcodebuildmcp/config.yaml.

Usage:
  ./scripts/bootstrap-xcodebuildmcp.sh [options]

Options:
  --project-path PATH
  --workspace-path PATH
  --scheme NAME
  --configuration NAME
  --simulator-name NAME
  --platform NAME
  --bundle-id ID
  --force
  -h, --help
EOF
}

PROJECT_PATH=""
WORKSPACE_PATH=""
SCHEME=""
CONFIGURATION="Debug"
SIMULATOR_NAME="iPhone 17 Pro"
PLATFORM="iOS"
BUNDLE_ID=""
FORCE="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project-path|--workspace-path|--scheme|--configuration|--simulator-name|--platform|--bundle-id)
      [[ $# -ge 2 ]] || { echo "Missing value for $1" >&2; exit 1; }
      case "$1" in
        --project-path) PROJECT_PATH="$2" ;;
        --workspace-path) WORKSPACE_PATH="$2" ;;
        --scheme) SCHEME="$2" ;;
        --configuration) CONFIGURATION="$2" ;;
        --simulator-name) SIMULATOR_NAME="$2" ;;
        --platform) PLATFORM="$2" ;;
        --bundle-id) BUNDLE_ID="$2" ;;
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

resolve_xcodebuildmcp
echo "Using XcodeBuildMCP via: ${XCODEBUILDMCP_CMD[*]}"

CONFIG_PATH="$(default_config_path)"
CONFIG_DIR="$(dirname "$CONFIG_PATH")"

if [[ -f "$CONFIG_PATH" && "$FORCE" != "true" ]]; then
  echo "Config already exists at $CONFIG_PATH"
  echo "Pass --force to overwrite it."
  exit 0
fi

mkdir -p "$CONFIG_DIR"

PATH_KEY=""
PATH_VALUE=""
if [[ -n "$WORKSPACE_PATH" ]]; then
  PATH_KEY="workspacePath"
  PATH_VALUE="$WORKSPACE_PATH"
elif [[ -n "$PROJECT_PATH" ]]; then
  PATH_KEY="projectPath"
  PATH_VALUE="$PROJECT_PATH"
fi

cat > "$CONFIG_PATH" <<EOF
schemaVersion: 1
enabledWorkflows:
  - simulator
  - ui-automation
  - debugging
sessionDefaults:
EOF

if [[ -n "$PATH_KEY" ]]; then
  cat >> "$CONFIG_PATH" <<EOF
  $PATH_KEY: "$PATH_VALUE"
EOF
fi

if [[ -n "$SCHEME" ]]; then
  cat >> "$CONFIG_PATH" <<EOF
  scheme: "$SCHEME"
EOF
fi

cat >> "$CONFIG_PATH" <<EOF
  configuration: "$CONFIGURATION"
  simulatorName: "$SIMULATOR_NAME"
  platform: "$PLATFORM"
  useLatestOS: true
EOF

if [[ -n "$BUNDLE_ID" ]]; then
  cat >> "$CONFIG_PATH" <<EOF
  bundleId: "$BUNDLE_ID"
EOF
fi

echo "Wrote $CONFIG_PATH"
echo "Next steps:"
echo "  1. Fill in missing projectPath/workspacePath or scheme if needed."
echo "  2. Run ./scripts/run-ios.sh --scheme YOUR_SCHEME"
echo "  3. Run ./scripts/capture-screenshot.sh screenshots/current.png"
